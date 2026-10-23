"""Verified, model-and-pack-scoped passage embedding cache."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import asdict
from pathlib import Path
from typing import Callable

import numpy as np

from .model_config import ModelCandidate


def _json_bytes(data: object) -> bytes:
    return json.dumps(data, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def atomic_bytes(path: Path, content: bytes) -> None:
    """Publish a complete file in the destination directory, or leave the old one."""
    path.parent.mkdir(parents=True, exist_ok=True)
    name = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, suffix=".tmp",
                                         delete=False) as handle:
            name = handle.name
            handle.write(content)
        os.replace(name, path)
    finally:
        if name is not None and os.path.exists(name):
            os.unlink(name)


def cached_embeddings(
    candidate: ModelCandidate, pack_id: str, chunks: list[dict],
    cache_dir: str | Path, encode: Callable[[list[str]], np.ndarray],
    *, vector_dtype: str = "float32", stats: dict | None = None,
) -> tuple[np.ndarray, bool]:
    """Return (vectors, cache_hit), rejecting a matching but corrupt cache."""
    if not chunks or not pack_id:
        raise ValueError("pack_id and non-empty chunks are required")
    ids = [record["chunk_id"] for record in chunks]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate chunk IDs")
    dtype = np.dtype(vector_dtype)
    if dtype.kind != "f":
        raise ValueError("vector dtype must be floating-point")
    settings = asdict(candidate)
    fingerprint = hashlib.sha256(_json_bytes({
        "model": settings, "pack_id": pack_id, "vector_dtype": dtype.name,
        "chunks": [(record["chunk_id"], record["text"]) for record in chunks],
    })).hexdigest()
    directory = Path(cache_dir)
    metadata_path = directory / "cache.json"
    metadata = (json.loads(metadata_path.read_text(encoding="utf-8"))
                if metadata_path.exists() else None)
    if metadata and metadata.get("fingerprint") == fingerprint:
        if metadata.get("chunk_ids") != ids:
            raise ValueError("cached chunk IDs do not match canonical order")
        vectors_path = directory / f"embeddings-{fingerprint}.npy"
        if vectors_path.exists():
            vectors = np.load(vectors_path, allow_pickle=False)
            if vectors.shape != (len(ids), candidate.dimension):
                raise ValueError("cached vector shape/dimension/count mismatch")
            if vectors.dtype != dtype:
                raise ValueError("cached vector dtype mismatch")
            if hashlib.sha256(vectors_path.read_bytes()).hexdigest() != metadata.get("vectors_sha256"):
                raise ValueError("cached vector checksum mismatch")
            if stats is not None:
                stats["truncation_count"] = metadata.get("truncation_count", 0)
            return vectors, True

    vectors = np.asarray(encode([record["text"] for record in chunks]), dtype=dtype)
    if vectors.shape != (len(ids), candidate.dimension):
        raise ValueError("encoded vector shape/dimension/count mismatch")
    directory.mkdir(parents=True, exist_ok=True)
    vectors_path = directory / f"embeddings-{fingerprint}.npy"
    temp = None
    try:
        with tempfile.NamedTemporaryFile(dir=directory, suffix=".tmp", delete=False) as handle:
            temp = handle.name
            np.save(handle, vectors, allow_pickle=False)
        digest = hashlib.sha256(Path(temp).read_bytes()).hexdigest()
        os.replace(temp, vectors_path)
    finally:
        if temp is not None and os.path.exists(temp):
            os.unlink(temp)
    atomic_bytes(metadata_path, _json_bytes({
        "fingerprint": fingerprint, "chunk_ids": ids,
        "dimension": candidate.dimension, "vector_dtype": dtype.name,
        "vectors_sha256": digest,
        "truncation_count": stats.get("truncation_count", 0) if stats is not None else 0,
    }))
    return vectors, False
