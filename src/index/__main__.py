"""Index-build CLI (T010): chunks.jsonl -> faiss.index + ids.json.

Usage:
    python -m src.index build [--chunks ...] [--index-dir ...]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import faiss_store
from .embed import embed_passages
from src.ingest.writer import load_manifest_ids


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build FAISS index from chunks.")
    parser.add_argument("command", choices=["build"])
    parser.add_argument("--manifest", default="data/corpus/manifest.json")
    parser.add_argument("--chunks", default="data/index/chunks.jsonl")
    parser.add_argument("--index-dir", default="data/index")
    args = parser.parse_args(argv)

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
