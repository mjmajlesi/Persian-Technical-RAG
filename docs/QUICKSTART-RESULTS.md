# QUICKSTART Results — full end-to-end validation (T033)

**Date**: 2026-10-12 | **Feature**: 001-persian-c-qa (CLOSED after this task)
**Corpus snapshot**: 2026-09-23 manifest, 52 sources | **Eval set**: v1, 30 items (20/5/5)

## 1. Fresh rebuild from scratch

Deleted `data/index/{faiss.index,ids.json,chunks.jsonl}`, re-ran both CLIs:

- Ingest: per-source counts identical to T010b (e.g. fa-pointers 19, cppref-printf 12)
- `total: 503 chunks -> data/index/chunks.jsonl`, `indexed: 503 chunks (dim 1024)`
- Result: **byte-identical chunk inventory** — chunking/ingest fully deterministic ✅

## 2. Demo probes (real server, real LLM)

| Probe | Result |
|---|---|
| In-corpus answer («تفاوت malloc و calloc؟») | `answer`, 3 citations ✅ |
| Out-of-corpus («پایتخت فرانسه؟») | `abstain`, 0 citations ✅ |
| Ambiguous («اشاره‌گر؟») | `clarify` ✅ |
| Mixed («تابع malloc چگونه…؟») | `answer`, `malloc` verbatim ✅ |

## 3. Full test suite

`pytest tests/` → **16 passed** (5 contract/integration server tests + 11 unit) ✅

## 4. Full eval — two runs compared (reproducibility evidence)

| Metric | Run 1 (T031) | Run 2 (T033, fresh index) |
|---|---|---|
| Hit-rate@5 | 1.000 (25/25) | 1.000 (25/25) |
| Citation coverage | 1.000 | 0.958 (23/24) |
| Citation precision (strict) | 0.690 | 0.642 |
| Abstention | 5/5 | 5/5 |
| Mixed slice | hit 1.0 / prec 0.607 | hit 1.0 / prec 0.667 |
| Answers / abstains | 23 / 7 | 24 / 6 |

**Stable across runs**: retrieval (1.000), abstention (5/5), zero phantoms.
**LLM variance** (expected, documented for the thesis): C-011 abstained in run 1
but answered in run 2 (citing 5 sibling chunks, missing the expected one);
C-013 abstained in both runs despite top-1 score 0.83 (over-conservative
generation — first documented prompt-tuning candidate).

## 5. Defects found and fixed in this task

1. **Report clobbering (fixed)**: same-day re-runs overwrote
   `data/eval/reports/<date>-v1.*`, destroying run 1's evidence. Fix in
   `src/eval/run.py`: report stamp now includes HHMM
   (`2026-10-12-1609-v1.*`), verified with a filename assertion. No other
   defects found; nothing else changed beyond this fix.
