"""Index-build CLI (T010): chunks.jsonl -> faiss.index + ids.json.

Usage:
    python -m src.index build [--chunks ...] [--index-dir ...]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from dataclasses import asdict
from pathlib import Path

from . import faiss_store
from .embed import embed_passages
from .model_config import get_model_candidate
from .research_cache import atomic_bytes, cached_embeddings
from src.ingest.writer import load_manifest_ids


def _build_research(lang: str, model_key: str) -> int:
    if lang not in {"c", "cpp", "python", "java"}:
        raise SystemExit(f"unknown language pack: {lang}")
    candidate = get_model_candidate(model_key)
    chunks_path = Path("data/index") / lang / "chunks.jsonl"
    chunk_bytes = chunks_path.read_bytes()
    chunk_hash = hashlib.sha256(chunk_bytes).hexdigest()
    records = [json.loads(line) for line in chunk_bytes.decode("utf-8").splitlines()
               if line.strip()]
    if not records:
        raise SystemExit("no canonical chunks to index")
    ids = [record["chunk_id"] for record in records]
    canonical_ids = json.loads((chunks_path.parent / "ids.json").read_text(encoding="utf-8"))
    if ids != canonical_ids:
        raise ValueError("canonical chunk IDs do not match index order")
    unknown = {record["source_id"] for record in records} - load_manifest_ids(
        f"data/corpus/manifest.{lang}.json"
    )
    if unknown:
        raise ValueError(f"chunks reference unknown sources: {sorted(unknown)}")

    directory = Path("data/research/embedding-compare") / model_key / lang
    stats = {}
    vectors, hit = cached_embeddings(
        candidate, lang, records, directory,
        lambda texts: embed_passages(texts, model_key=model_key, truncation_stats=stats),
        stats=stats,
    )
    index = faiss_store.build(vectors)
    directory.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        with tempfile.NamedTemporaryFile(dir=directory, suffix=".tmp", delete=False) as handle:
            temp = handle.name
        faiss_store.faiss.write_index(index, temp)
        index_hash = hashlib.sha256(Path(temp).read_bytes()).hexdigest()
        os.replace(temp, directory / "faiss.index")
    finally:
        if temp is not None and os.path.exists(temp):
            os.unlink(temp)

    atomic_bytes(directory / "ids.json", json.dumps(ids, ensure_ascii=False).encode("utf-8"))
    settings_hash = hashlib.sha256(json.dumps(asdict(candidate), sort_keys=True,
                                           ensure_ascii=False).encode("utf-8")).hexdigest()
    atomic_bytes(directory / "index-meta.json", json.dumps({
        "status": "ready", "model_key": model_key, "pack_id": lang,
        "revision_sha": candidate.revision_sha, "dimension": candidate.dimension,
        "count": len(ids), "canonical_chunks_path": chunks_path.as_posix(),
        "chunk_sha256": chunk_hash, "settings_sha256": settings_hash,
        "index_sha256": index_hash, "cache_hit": hit,
        "truncation_count": stats["truncation_count"],
    }, ensure_ascii=False, indent=2).encode("utf-8"))
    print(f"research index: {model_key}/{lang} {len(ids)} chunks "
          f"(dim {candidate.dimension}, cache {'hit' if hit else 'miss'}) -> {directory}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build FAISS index from chunks.")
    parser.add_argument("command", choices=["build"])
    parser.add_argument("--lang", default="c",
                        help="language pack id (paths derive from it unless overridden)")
    parser.add_argument("--manifest", default=None)
    parser.add_argument("--chunks", default=None)
    parser.add_argument("--index-dir", default=None)
    parser.add_argument("--model", default=None,
                        help="registered research model (omit for the operational index)")
    args = parser.parse_args(argv)
    if args.model is not None:
        if any((args.manifest, args.chunks, args.index_dir)):
            parser.error("research builds always use canonical pack paths")
        return _build_research(args.lang, args.model)
    if args.manifest is None:
        args.manifest = f"data/corpus/manifest.{args.lang}.json"
    if args.chunks is None:
        args.chunks = f"data/index/{args.lang}/chunks.jsonl"
    if args.index_dir is None:
        args.index_dir = f"data/index/{args.lang}"

    manifest_ids = load_manifest_ids(args.manifest)
    records = [
        json.loads(line)
        for line in Path(args.chunks).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not records:
        raise SystemExit("no chunks to index")
    unknown = {r["source_id"] for r in records} - manifest_ids
    if unknown:
        raise SystemExit(f"chunks reference unknown sources: {sorted(unknown)}")
    ids = [r["chunk_id"] for r in records]
    vectors = embed_passages([r["text"] for r in records])
    index = faiss_store.build(vectors)
    faiss_store.save(index, ids, args.index_dir)
    print(f"indexed: {index.ntotal} chunks (dim {vectors.shape[1]}) -> {args.index_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
