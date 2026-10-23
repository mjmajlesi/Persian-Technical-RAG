"""Pack-scoped question retrieval from the operational or research index."""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import asdict
from pathlib import Path

from src.index import faiss_store
from src.index.embed import embed_queries
from src.index.model_config import get_model_candidate

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

    def __init__(self, index_dir: str | Path = "data/index", *,
                 model_key: str | None = None, pack_id: str | None = None):
        self._model_key = model_key
        directory = Path(index_dir)
        chunks_path = directory / "chunks.jsonl"
        if model_key is not None:
            if not pack_id:
                raise ValueError("research index requires a pack_id")
            candidate = get_model_candidate(model_key)
            metadata = json.loads((directory / "index-meta.json").read_text(encoding="utf-8"))
            chunks_path = Path("data/index") / pack_id / "chunks.jsonl"
            settings_hash = hashlib.sha256(json.dumps(
                asdict(candidate), sort_keys=True, ensure_ascii=False
            ).encode("utf-8")).hexdigest()
            expected = {
                "status": "ready", "model_key": model_key, "pack_id": pack_id,
                "revision_sha": candidate.revision_sha,
                "settings_sha256": settings_hash,
                "canonical_chunks_path": chunks_path.as_posix(),
                "dimension": candidate.dimension,
            }
            for field, value in expected.items():
                if metadata.get(field) != value:
                    raise ValueError(f"research index {field} mismatch")
            if hashlib.sha256(chunks_path.read_bytes()).hexdigest() != metadata.get("chunk_sha256"):
                raise ValueError("canonical chunk hash mismatch")
            if hashlib.sha256((directory / "faiss.index").read_bytes()).hexdigest() != metadata.get("index_sha256"):
                raise ValueError("research index hash mismatch")
        elif pack_id is not None:
            raise ValueError("pack_id requires a research model_key")

        self._index, self._ids = faiss_store.load(directory)
        records = [
            json.loads(line)
            for line in chunks_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        if model_key is not None:
            canonical_ids = [record["chunk_id"] for record in records]
            if self._ids != canonical_ids or len(set(canonical_ids)) != len(canonical_ids):
                raise ValueError("research index IDs differ from canonical chunk order")
            if self._index.d != candidate.dimension or self._index.ntotal != metadata.get("count"):
                raise ValueError("research index dimension/count mismatch")
        self._by_id = {record["chunk_id"]: record for record in records}
        missing = [cid for cid in self._ids if cid not in self._by_id]
        if missing:
            raise ValueError(f"index ids missing from chunks.jsonl: {missing[:3]}")

    def has_chunk(self, chunk_id: str) -> bool:
        """Pack membership check (002-T017): is this id in THIS index?"""
        return chunk_id in self._by_id

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
        query_vec = (embed_queries([question])[0] if self._model_key is None else
                     embed_queries([question], model_key=self._model_key)[0])
        hits = faiss_store.search(self._index, self._ids, query_vec, k)
        results = []
        for chunk_id, score in hits:
            record = dict(self._by_id[chunk_id])
            record["score"] = score
            results.append(record)
        return results
