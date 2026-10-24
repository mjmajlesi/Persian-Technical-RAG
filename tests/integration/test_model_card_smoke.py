"""Opt-in, pinned model-card and real CPU embedding smoke checks.

Run: $env:RUN_MODEL_CARD_SMOKE='1'; python -m pytest tests/integration/test_model_card_smoke.py -q -s
Weights download into the Hugging Face cache, never the repository.
"""

import gc
import os
import time

import numpy as np
import pytest
from huggingface_hub import HfApi, hf_hub_download

from src.index import embed
from src.index.model_config import load_model_registry


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_MODEL_CARD_SMOKE") != "1", reason="opt in to multi-GB pinned CPU model downloads"
)


def test_pinned_cards_agree_with_registry():
    registry = load_model_registry()
    assert set(registry) == {"e5-large", "e5-base", "bge-m3"}
    api = HfApi()
    for key, expected_dim, expected_limit in (
        ("e5-large", 1024, 512), ("e5-base", 768, 512), ("bge-m3", 1024, 8192)
    ):
        candidate = registry[key]
        card = api.model_info(candidate.repository, revision=candidate.revision_sha)
        assert card.sha == candidate.revision_sha
        assert card.cardData["license"].lower() == candidate.license.lower() == "mit"
        from json import load

        with open(hf_hub_download(candidate.repository, "config.json", revision=card.sha), encoding="utf-8") as f:
            config = load(f)
        with open(hf_hub_download(candidate.repository, "sentence_bert_config.json", revision=card.sha), encoding="utf-8") as f:
            sentence_config = load(f)
        assert config["hidden_size"] == candidate.dimension == expected_dim
        assert sentence_config["max_seq_length"] == candidate.max_tokens == expected_limit
        assert config["max_position_embeddings"] >= candidate.max_tokens
        if key.startswith("e5-"):
            assert (candidate.query_prefix, candidate.passage_prefix) == ("query: ", "passage: ")
        else:
            assert candidate.query_prefix == candidate.passage_prefix == ""
        assert candidate.normalize is True


@pytest.mark.parametrize("key,dimension", [("e5-base", 768), ("bge-m3", 1024)])
def test_real_cpu_dense_query_and_passage(monkeypatch, key, dimension):
    import torch

    torch.set_num_threads(4)
    candidate = load_model_registry()[key]
    started = time.perf_counter()
    model = embed.get_model(key)
    try:
        model.cpu()
        assert model.device.type == "cpu"
        seen = []
        original = model.encode

        def encode(texts, **kwargs):
            seen.extend(texts)
            assert kwargs["normalize_embeddings"] is True
            return original(texts, **kwargs)

        monkeypatch.setattr(model, "encode", encode)
        query = "What is an array?"
        passage = "An array holds elements."
        query_stats, passage_stats = {}, {}
        q = embed.embed_queries([query], model_key=key, truncation_stats=query_stats)
        p = embed.embed_passages([passage], model_key=key, truncation_stats=passage_stats)
        assert seen == [candidate.query_prefix + query, candidate.passage_prefix + passage]
        assert model.max_seq_length == candidate.max_tokens
        assert q.shape == p.shape == (1, dimension)
        assert np.isfinite(q).all() and np.isfinite(p).all()
        np.testing.assert_allclose(np.linalg.norm(q, axis=1), 1, atol=1e-5)
        np.testing.assert_allclose(np.linalg.norm(p, axis=1), 1, atol=1e-5)
        assert query_stats == passage_stats == {"truncation_count": 0}
        print(f"{key}: CPU load+2 encodes {time.perf_counter() - started:.1f}s, dimension {dimension}, truncation 0")
    finally:
        embed._model = None
        embed._model_key = None
        del model
        gc.collect()
