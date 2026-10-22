# C-pack migration results (002-T026)

**Re-run:** 2026-10-22, `python -m src.eval run --lang c`  
**001 baseline:** `data/eval/reports/2026-10-12-v1.md` (tracked); its local JSON report supplied the row-level comparison.  
**002 re-run:** `data/eval/c/reports/2026-10-22-0656-c-v1.md` (JSON is ignored by git). Both runs completed without model errors in the recorded report.

## Input equivalence

- The 30 questions, qtypes and expected source IDs in `data/eval/eval-set.v1.json` and `data/eval/c/eval-set.c.v1.json` are identical; only the set version changed (`v1` → `c-v1`). The new run adds three **separately scored** cross-pack probes, excluded from the 30-item comparison and the primary metrics.
- `data/index/c/ids.json` is byte-for-byte equal to pre-migration `data/index/ids.json` at commit `2485a30` (503 entries; SHA-256 `b2f884d7502302c1776bef9cd7347e3df867847f012afaec90493222958e62dc`). The FAISS binary and chunk text are not tracked in git; byte equality of the entire historical index cannot be independently established from the repository alone.
- In the two local JSON reports, every one of the 30 matched rows has the same rounded top-1 score and hit@5 verdict (30/30). Historical JSON reports are gitignored; the tracked baseline Markdown supplies the headline figures and per-item answer/precision verdicts, not top-1 scores.
- The similarity gate changed from 0.81 to 0.803 in T024. On these 30 items max(out)=0.793 and min(answerable)=0.814, so **neither threshold changes a gate decision** for this set.

## Figures (30 matched items; no blended scores)

| Metric | 001 baseline | 002 C re-run | Difference |
|---|---:|---:|---:|
| Retrieval hit@5 (25 answerable) | 1.000 (25/25) | 1.000 (25/25) | 0 |
| Citation precision (answered) | 0.64236 | 0.65278 | +0.01042 |
| Citation coverage (answered) | 0.95833 (23/24) | 0.95833 (23/24) | 0 |
| Out-of-corpus abstention | 5/5 | 5/5 | 0 |
| Mixed hit@5 | 1.000 (5/5) | 1.000 (5/5) | 0 |
| Mixed citation precision | 0.66667 | 0.60000 | -0.06667 |
| Answer / abstain counts (30 items) | 24 / 6 | 24 / 6 | 0 |

The 002 run also scored a separate contamination slice: **3/3 abstained**. The 001 set had no such slice.

## Investigation of nonzero deltas

Eight of the 30 matched rows changed citation precision despite unchanged item IDs, retrieval hit and response type: C-002 (0.5→1), C-003 (1→0.5), C-005 (0.5→1), C-010 (1→0.5), C-011 (0→0.5), C-014 (0.25→0.5), C-018 (0.5→0.33333), and C-M04 (0.33333→0). Citation coverage flipped in C-011 (miss→hit) and C-M04 (hit→miss); the total remains 23/24. This is consistent with generation/citation-selection variance, **not evidence of retrieval drift**: all 30 retrieval verdicts and rounded top-1 scores match. The 002-T025 C run on the same date and same index had precision 0.68939, further showing that generation figures vary without a corpus migration. The provider/model also changed between historical and current runs, so a causal attribution of the exact precision delta to any single factor is not possible.

**Conclusion:** migration preserved the evaluated C questions, index ID inventory, and observed retrieval/abstention results. It did **not** reproduce the exact LLM citation precision or mixed-slice precision; these differences are recorded rather than described as "unchanged." Re-run from the project root with the command above; compare to the tracked baseline and this document.
