"""FAISS index build/query module (T009).

IndexFlatIP over L2-normalized e5 embeddings (see embed.py), so scores are
cosine similarities. The ordered chunk_id list is persisted alongside the
index so search results map back to CorpusChunk records in chunks.jsonl.
"""

from __future__ import annotations
import json
from pathlib import Path
import faiss
import numpy as np

INDEX_FILENAME = "faiss.index"
IDS_FILENAME = "ids.json"


def build(embeddings: np.ndarray) -> faiss.Index:
    """Build an inner-product index from (N, dim) normalized embeddings."""
    vectors = np.ascontiguousarray(embeddings, dtype=np.float32)
    if vectors.ndim != 2 or vectors.shape[0] == 0:
        raise ValueError("embeddings must be a non-empty (N, dim) array")
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    return index


def save(index: faiss.Index, chunk_ids: list[str], directory: str | Path) -> None:
    """Persist the index and its ordered chunk_id list to directory."""
    if index.ntotal != len(chunk_ids):
        raise ValueError("chunk_ids length must match index.ntotal")
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(directory / INDEX_FILENAME))
    (directory / IDS_FILENAME).write_text(
        json.dumps(chunk_ids, ensure_ascii=False), encoding="utf-8"
    )


def load(directory: str | Path) -> tuple[faiss.Index, list[str]]:
    """Load a persisted index and its ordered chunk_id list."""
    directory = Path(directory)
    index = faiss.read_index(str(directory / INDEX_FILENAME))
    chunk_ids = json.loads((directory / IDS_FILENAME).read_text(encoding="utf-8"))
    if index.ntotal != len(chunk_ids):
        raise ValueError("persisted ids do not match index size")
    return index, chunk_ids


def search(
    index: faiss.Index, chunk_ids: list[str], query_vec: np.ndarray, k: int
) -> list[tuple[str, float]]:
    """Return top-k (chunk_id, score) pairs, highest score first."""
    if k < 1:
        raise ValueError("k must be >= 1")
    q = np.ascontiguousarray(query_vec, dtype=np.float32).reshape(1, -1)
    k = min(k, index.ntotal)
    scores, idxs = index.search(q, k)
    return [(chunk_ids[i], float(s)) for i, s in zip(idxs[0], scores[0])]
