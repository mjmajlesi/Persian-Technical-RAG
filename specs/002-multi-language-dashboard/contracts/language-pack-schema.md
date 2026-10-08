# Contract: Language Pack Schema

**Feature**: [spec.md](../spec.md) | **Entities**: [data-model.md](../data-model.md)

## Manifest file (`data/corpus/manifest.<lang>.json`)

Same CorpusSource entry schema as 001, plus pack-level header fields:

```json
{
  "language_id": "cpp",
  "display_name": "C++ / سی‌پلاس‌پلاس",
  "snapshot": "2026-10-07",
  "eval_set_version": "v1",
  "notes": "Frozen snapshot notes (composition + tradeoff where applicable)",
  "sources": [
    {
      "source_id": "cpp-notes-intro",
      "title": "...",
      "kind": "persian-notes",
      "origin": "data/corpus/cpp/<file>.md",
      "snapshot": "2026-10-07",
      "license": "owner-authored study notes (project owner)"
    }
  ]
}
```

Rules: `language_id` matches the filename; every `source_id` unique within
the pack; `origin` is a frozen local file under `data/corpus/<lang>/`;
licenses recorded per source (CC-BY-SA for cppreference-derived files).

## Per-pack directory layout

```text
data/corpus/<lang>/        # frozen sources (*.md with URL/date/license headers)
data/corpus/manifest.<lang>.json
data/index/<lang>/         # faiss.index + ids.json + chunks.jsonl
data/eval/<lang>/          # eval-set.<lang>.v1.json + reports/
```

Rules: chunk_ids need only be unique **within** a pack (same chunker scheme);
retrieval never crosses pack directories (Principle VIII); adding a pack
adds directories only — existing packs byte-identical (SC-004).
