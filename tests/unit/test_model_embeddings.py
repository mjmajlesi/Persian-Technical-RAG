"""FAIL-first embedding-boundary contract for 003-T005 (no model downloads)."""

import numpy as np
import pytest

from src.index import embed


class FakeModel:
    def __init__(self, dimension):
        self.dimension = dimension
        self.max_seq_length = None
        self.inputs = []
        self.normalize = None

    def encode(self, texts, normalize_embeddings=False):
        self.inputs.extend(texts)
        self.normalize = normalize_embeddings
        return np.full((len(texts), self.dimension),
                       1 / np.sqrt(self.dimension), dtype=np.float32)

    def tokenize(self, texts):
        # Include two special tokens, as the model tokenizer does.
        return {"input_ids": [[0] + [1] * len(text.split()) + [2] for text in texts]}


@pytest.fixture
def models(monkeypatch):
    fake = {"e5-large": FakeModel(1024), "e5-base": FakeModel(768),
            "bge-m3": FakeModel(1024)}
    monkeypatch.setattr(embed, "get_model", lambda model_key="e5-large": fake[model_key])
    return fake


def test_default_e5_baseline_keeps_existing_query_and_passage_prefixes(models):
    query = embed.embed_queries(["چگونه malloc کار می‌کند؟"])
    passage = embed.embed_passages(["حافظه را آزاد کنید."])
    assert models["e5-large"].inputs == [
        "query: چگونه malloc کار می‌کند؟", "passage: حافظه را آزاد کنید.",
    ]
    assert query.shape == passage.shape == (1, 1024)
    assert models["e5-large"].normalize is True


@pytest.mark.parametrize("model_key,dimension,query_prefix,passage_prefix", [
    ("e5-large", 1024, "query: ", "passage: "),
    ("e5-base", 768, "query: ", "passage: "),
    ("bge-m3", 1024, "", ""),
])
def test_card_prefixes_normalized_dense_dimensions_and_raw_text(
    models, model_key, dimension, query_prefix, passage_prefix,
):
    question = "فرق pointer و reference چیست؟"
    passages = ["یک متن فارسی با Python", "مدرک انگلیسی"]
    original_passages = passages.copy()
    q = embed.embed_queries([question], model_key=model_key)
    p = embed.embed_passages(passages, model_key=model_key)
    assert models[model_key].inputs == [
        query_prefix + question, *(passage_prefix + text for text in passages),
    ]
    assert question == "فرق pointer و reference چیست؟"
    assert passages == original_passages  # never mutate canonical chunk text
    assert q.shape == (1, dimension)
    assert p.shape == (2, dimension)
    assert models[model_key].normalize is True
    np.testing.assert_allclose(np.linalg.norm(q, axis=1), 1, atol=1e-6)
    np.testing.assert_allclose(np.linalg.norm(p, axis=1), 1, atol=1e-6)


@pytest.mark.parametrize("model_key,max_tokens", [
    ("e5-large", 512), ("e5-base", 512), ("bge-m3", 8192),
])
def test_model_card_limit_and_truncation_count(models, model_key, max_tokens):
    stats = {}
    # 600 words + two special tokens exceed 512 but not 8192.
    passages = ["short", "word " * 600]
    embed.embed_passages(passages, model_key=model_key, truncation_stats=stats)
    assert models[model_key].max_seq_length == max_tokens
    assert stats["truncation_count"] == (1 if max_tokens == 512 else 0)
    assert passages[1] == "word " * 600


def test_explicit_e5_large_matches_default_baseline(models):
    text = "چرا strlen پایان رشته را حساب نمی‌کند؟"
    baseline = embed.embed_queries([text])
    explicit = embed.embed_queries([text], model_key="e5-large")
    np.testing.assert_array_equal(explicit, baseline)
    assert models["e5-large"].inputs == ["query: " + text] * 2
