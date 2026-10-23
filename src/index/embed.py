"""Model-card-aware dense embeddings; the default remains E5-large."""

from __future__ import annotations

import numpy as np

from .model_config import get_model_candidate

MODEL_ID = "intfloat/multilingual-e5-large"  # unchanged operational default
_model = None
_model_key = None


def get_model(model_key: str | None = None):
    """Retain one model: legacy default or explicitly pinned research model."""
    global _model, _model_key
    if _model is None or _model_key != model_key:
        from sentence_transformers import SentenceTransformer

        if model_key is None:
            _model = SentenceTransformer(MODEL_ID)
        else:
            candidate = get_model_candidate(model_key)
            _model = SentenceTransformer(candidate.repository, revision=candidate.revision_sha)
        _model_key = model_key
    return _model


def _encode(texts: list[str], model_key: str | None, prefix: str,
            truncation_stats: dict | None = None) -> np.ndarray:
    candidate = get_model_candidate(model_key or "e5-large")
    model = get_model() if model_key is None else get_model(model_key)
    model.max_seq_length = candidate.max_tokens
    prepared = [prefix + text for text in texts]
    if truncation_stats is not None:
        # Count tokens without truncation; SentenceTransformer.tokenize may
        # already apply max_seq_length, hiding the very truncation we report.
        tokenizer = getattr(model, "tokenizer", None)
        ids = (tokenizer(prepared, add_special_tokens=True, truncation=False)["input_ids"]
               if tokenizer is not None else model.tokenize(prepared)["input_ids"])
        truncation_stats["truncation_count"] = sum(
            len(tokens) > candidate.max_tokens for tokens in ids
        )
    vectors = np.asarray(model.encode(prepared, normalize_embeddings=True), dtype=np.float32)
    if vectors.ndim != 2 or vectors.shape != (len(texts), candidate.dimension):
        raise ValueError(f"{model_key} returned incompatible embedding dimensions")
    return vectors


def embed_queries(texts: list[str], model_key: str | None = None,
                  truncation_stats: dict | None = None) -> np.ndarray:
    """Embed queries with the selected model's prefix and length limit."""
    candidate = get_model_candidate(model_key or "e5-large")
    return _encode(texts, model_key, candidate.query_prefix, truncation_stats)


def embed_passages(texts: list[str], model_key: str | None = None,
                   truncation_stats: dict | None = None) -> np.ndarray:
    """Embed passages without changing their canonical raw text."""
    candidate = get_model_candidate(model_key or "e5-large")
    return _encode(texts, model_key, candidate.passage_prefix, truncation_stats)
