"""Embedding module (T008).

Wraps intfloat/multilingual-e5-large via sentence-transformers, applying the
query/passage prefixes from the model card (research.md §1). Embeddings are
L2-normalized by default so FAISS inner-product search equals cosine
similarity. The model loads lazily (heavy download/load) — never at import.
"""

from __future__ import annotations

import numpy as np

MODEL_ID = "intfloat/multilingual-e5-large"
QUERY_PREFIX = "query: "
PASSAGE_PREFIX = "passage: "

_model = None


def get_model():
    """Load (once) and return the shared SentenceTransformer instance."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(MODEL_ID)
    return _model


def _encode(prefixed: list[str]) -> np.ndarray:
    model = get_model()
    vectors = model.encode(prefixed, normalize_embeddings=True)
    return np.asarray(vectors, dtype=np.float32)


def embed_queries(texts: list[str]) -> np.ndarray:
    """Embed user/retrieval queries with the e5 query prefix."""
    return _encode([QUERY_PREFIX + t for t in texts])


def embed_passages(texts: list[str]) -> np.ndarray:
    """Embed corpus chunks with the e5 passage prefix."""
    return _encode([PASSAGE_PREFIX + t for t in texts])
