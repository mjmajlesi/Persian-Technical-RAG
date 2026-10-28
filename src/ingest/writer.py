"""Chunk writer + JSONL schema validation (T007).

Validates Chunk objects (from chunker.py) against the corpus manifest, then
writes data/index/chunks.jsonl (one JSON object per line). Standard library
only.
"""

from __future__ import annotations
import json
import os
import tempfile
from pathlib import Path
from .chunker import Chunk

REQUIRED_FIELDS = ("chunk_id", "source_id", "doc_title", "section_heading", "text", "lang")
LANGS = ("fa", "en", "mixed")


class ChunkValidationError(ValueError):
    """Raised when a chunk or the manifest violates the CorpusChunk contract."""


def load_manifest_ids(manifest_path: str | Path) -> set[str]:
    """Return the set of source_id values declared in the manifest."""
    raw = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    sources = raw.get("sources", [])
    if not sources:
        raise ChunkValidationError(f"manifest has no sources: {manifest_path}")
    ids = [s.get("source_id", "") for s in sources]
    if any(not i for i in ids):
        raise ChunkValidationError("manifest entry with empty source_id")
    if len(ids) != len(set(ids)):
        raise ChunkValidationError("manifest has duplicate source_id values")
    return set(ids)


def validate_chunks(chunks: list[Chunk], manifest_ids: set[str]) -> None:
    """Enforce the CorpusChunk contract; raise ChunkValidationError on breach."""
    if not chunks:
        raise ChunkValidationError("cannot publish empty chunks")
    seen: set[str] = set()
    for chunk in chunks:
        record = chunk.to_dict()
        for field in REQUIRED_FIELDS:
            value = record.get(field, "")
            if not isinstance(value, str) or not value.strip():
                raise ChunkValidationError(
                    f"chunk {record.get('chunk_id', '?')!r}: empty {field}"
                )
        if record["chunk_id"] in seen:
            raise ChunkValidationError(f"duplicate chunk_id: {record['chunk_id']}")
        seen.add(record["chunk_id"])
        if record["source_id"] not in manifest_ids:
            raise ChunkValidationError(
                f"chunk {record['chunk_id']}: unknown source_id {record['source_id']!r}"
            )
        if record["lang"] not in LANGS:
            raise ChunkValidationError(
                f"chunk {record['chunk_id']}: invalid lang {record['lang']!r}"
            )


def write_chunks_jsonl(
    chunks: list[Chunk], manifest_path: str | Path, out_path: str | Path
) -> int:
    """Validate chunks and atomically replace the destination with complete JSONL.

    Returns the number of chunks written.
    """
    manifest_ids = load_manifest_ids(manifest_path)
    validate_chunks(chunks, manifest_ids)
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                         dir=out.parent, suffix=".tmp", delete=False) as fh:
            temporary = Path(fh.name)
            for chunk in chunks:
                fh.write(json.dumps(chunk.to_dict(), ensure_ascii=False) + "\n")
        os.replace(temporary, out)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return len(chunks)
