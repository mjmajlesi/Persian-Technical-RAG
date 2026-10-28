"""Ingest CLI (T010): manifest -> chunks.jsonl.

Usage:
    python -m src.ingest --manifest data/corpus/manifest.json [--out ...]

For each manifest source the origin is resolved as follows:
  1. an existing local file -> chunked directly;
  2. otherwise (e.g. a reference URL) a dev mirror at
     <samples-dir>/<source_id>.md is used when present;
  3. otherwise ingest fails before chunking or publishing any output.

Rule 2 is a development-only convenience so the skeleton manifest resolves
to the T004 fixtures; the real frozen corpus (T010b) uses real origins.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .chunker import chunk_markdown
from .writer import write_chunks_jsonl


def resolve_origin(source: dict, samples_dir: Path) -> Path | None:
    origin = source.get("origin", "")
    local = Path(origin)
    if local.is_file():
        return local
    mirror = samples_dir / f"{source.get('source_id', '')}.md"
    if mirror.is_file():
        return mirror
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingest corpus manifest to chunks.")
    parser.add_argument("--lang", default="c",
                        help="language pack id (paths derive from it unless overridden)")
    parser.add_argument("--manifest", default=None)
    parser.add_argument("--out", default=None)
    parser.add_argument("--samples-dir", default="data/corpus/samples")
    args = parser.parse_args(argv)
    if args.manifest is None:
        args.manifest = f"data/corpus/manifest.{args.lang}.json"
    if args.out is None:
        args.out = f"data/index/{args.lang}/chunks.jsonl"

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    samples_dir = Path(args.samples_dir)
    resolved = []
    for source in manifest.get("sources", []):
        path = resolve_origin(source, samples_dir)
        if path is None:
            print(f"ERROR {source.get('source_id')}: no local origin or mirror", file=sys.stderr)
            return 1
        resolved.append((source, path))
    chunks = []
    per_source: dict[str, int] = {}
    for source, path in resolved:
        made = chunk_markdown(
            path.read_text(encoding="utf-8"),
            source["source_id"],
            source.get("title", source["source_id"]),
        )
        if not made:
            print(f"ERROR {source['source_id']}: source produced no chunks", file=sys.stderr)
            return 1
        chunks.extend(made)
        per_source[source["source_id"]] = len(made)

    total = write_chunks_jsonl(chunks, args.manifest, args.out)
    for source_id, count in per_source.items():
        print(f"{source_id}: {count} chunks")
    print(f"total: {total} chunks -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
