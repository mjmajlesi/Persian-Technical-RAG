"""Ingest CLI (T010): manifest -> chunks.jsonl.

Usage:
    python -m src.ingest --manifest data/corpus/manifest.json [--out ...]

For each manifest source the origin is resolved as follows:
  1. an existing local file -> chunked directly;
  2. otherwise (e.g. a reference URL) a dev mirror at
     <samples-dir>/<source_id>.md is used when present;
  3. otherwise the source is skipped with a warning.

Rule 2 is a development-only convenience so the skeleton manifest resolves
to the T004 fixtures; the real frozen corpus (T010b) uses real origins.
"""

from __future__ import annotations

import argparse
import json
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
    parser.add_argument("--manifest", default="data/corpus/manifest.json")
    parser.add_argument("--out", default="data/index/chunks.jsonl")
    parser.add_argument("--samples-dir", default="data/corpus/samples")
    args = parser.parse_args(argv)

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    samples_dir = Path(args.samples_dir)
    chunks = []
    per_source: dict[str, int] = {}
    for source in manifest.get("sources", []):
        path = resolve_origin(source, samples_dir)
        if path is None:
            print(f"SKIP {source.get('source_id')}: no local origin or mirror")
            continue
        made = chunk_markdown(
            path.read_text(encoding="utf-8"),
            source["source_id"],
            source.get("title", source["source_id"]),
        )
        chunks.extend(made)
        per_source[source["source_id"]] = len(made)

    total = write_chunks_jsonl(chunks, args.manifest, args.out)
    for source_id, count in per_source.items():
        print(f"{source_id}: {count} chunks")
    print(f"total: {total} chunks -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
