"""Retrieval orchestration (T012): question -> top-k grounded chunks.

Loads the persisted FAISS index + chunk records once, embeds the question
with the e5 query prefix, and returns the top-k chunk records (highest
cosine score first), each carrying its citation metadata.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from src.index import faiss_store
from src.index.embed import embed_queries

DEFAULT_TOP_K = 5

logger = logging.getLogger(__name__)


def detect_query_lang(text: str) -> str:
    """Return 'mixed' when Persian text embeds Latin identifiers, else 'fa'.

    Detection only — the question text is NEVER modified before embedding,
    so Latin identifiers reach retrieval verbatim.
    """
    has_fa = any("؀" <= ch <= "ۿ" for ch in text)
    has_latin = any("A" <= ch <= "Z" or "a" <= ch <= "z" for ch in text)
    return "mixed" if (has_fa and has_latin) else "fa"


class Retriever:
    """Question-to-chunks retrieval over the frozen index snapshot."""

    def __init__(self, index_dir: str | Path = "data/index"):
        self._index, self._ids = faiss_store.load(index_dir)
        chunks_path = Path(index_dir) / "chunks.jsonl"
        records = [
            json.loads(line)
            for line in chunks_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self._by_id = {record["chunk_id"]: record for record in records}
        missing = [cid for cid in self._ids if cid not in self._by_id]
        if missing:
            raise ValueError(f"index ids missing from chunks.jsonl: {missing[:3]}")

    def retrieve(self, question: str, k: int = DEFAULT_TOP_K) -> list[dict]:
        """Return top-k chunk records for a Persian question.

        Each record is the stored chunk dict plus a ``score`` field
        (cosine similarity, higher is better).
        """
        if not question or not question.strip():
            raise ValueError("question must be non-empty")
        question = question.strip()
        lang_hint = detect_query_lang(question)
        logger.info("retrieve lang_hint=%s question=%s", lang_hint, question[:60])
        query_vec = embed_queries([question])[0]
        hits = faiss_store.search(self._index, self._ids, query_vec, k)
        results = []
        for chunk_id, score in hits:
            record = dict(self._by_id[chunk_id])
            record["score"] = score
            results.append(record)
        return results
