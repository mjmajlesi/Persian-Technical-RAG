# Quickstart: Multi-Language Dashboard

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Prerequisites

- Feature 001's answer path complete (T018+); Python 3.11 `.venv` from 001.
- New corpora frozen per pack (cpp notes + English refs for cpp/python/java).

## 1. Migrate the C pack (one time)

```powershell
# manifest.json -> manifest.c.json, full/* -> c/, index/* -> index/c/
python scripts/migrate_c_pack.py
.\.venv\Scripts\python -m src.eval run --lang c --set data/eval/c/eval-set.c.v1.json
```

Expected: C eval figures identical to pre-migration (SC-004 for the first pack).

## 2. Ingest a new pack (example: cpp)

```powershell
.\.venv\Scripts\python -m src.ingest --lang cpp --manifest data/corpus/manifest.cpp.json
.\.venv\Scripts\python -m src.index build --lang cpp --manifest data/corpus/manifest.cpp.json
```

Expected: `data/index/cpp/` holds `faiss.index` + `ids.json` + `chunks.jsonl`;
per-pack counts print to console; other packs untouched.

## 3. Dashboard check

```powershell
uvicorn src.web.app:app --port 8000
```

Open `http://localhost:8000`: sidebar lists C (preselected), C++, Python,
Java with ready/empty states. Select C++, ask an in-corpus question, and
confirm: Persian answer, citations resolving inside the cpp pack only,
click-reveal unchanged. Select a pack whose question belongs to another
pack and confirm abstention with zero foreign citations.

Validation probes (contract: [languages-api.md](./contracts/languages-api.md)):

- `GET /api/languages` → 4 packs with correct statuses.
- `POST /api/ask` without `language` → behaves as 001 (C).
- `POST /api/ask` with unknown language → `422` Persian error.
- `POST /api/ask` for an `empty` pack → `type: unavailable`, zero citations.

## 4. Per-language evaluation

```powershell
pytest tests/ -k "cpp or contamination"
.\.venv\Scripts\python -m src.eval run --lang cpp --set data/eval/cpp/eval-set.cpp.v1.json
.\.venv\Scripts\python -m src.eval run --lang python --set data/eval/python/eval-set.python.v1.json
.\.venv\Scripts\python -m src.eval run --lang java --set data/eval/java/eval-set.java.v1.json
```

Expected: per-language JSON + Markdown reports under `data/eval/<lang>/reports/`
(hit-rate@5, citation precision, abstention correctness, contamination slice);
no blended score is the headline figure.

## 5. Examiner reproduction

Delete `data/index/<lang>/` for any language and re-run steps 2–4 for that
language only. Same snapshot + same set version must yield the same retrieval
rows and abstention verdicts, with other packs untouched.
