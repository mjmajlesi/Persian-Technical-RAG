# Contract: research evaluation and comparison

**Status**: planned interface; not yet implemented. Default `python -m src.eval run --lang c` stays the current v1 operational run.

## Commands (planned)

```powershell
# Calibrate one research gate per model from all four frozen v1 sets (120 items).
.\.venv\Scripts\python -m src.eval.calibrate --model bge-m3 --pooled-v1

# Select model + one language, same 45 new v2 items for every candidate.
.\.venv\Scripts\python -m src.eval run --lang python --model bge-m3 --set data/eval/python/eval-set.python.v2.json --mode retrieval-only
.\.venv\Scripts\python -m src.eval run --lang python --model bge-m3 --set data/eval/python/eval-set.python.v2.json --mode end-to-end

# Compare complete model runs for each language, without a blended rank.
.\.venv\Scripts\python -m src.eval compare --set-version v2
```

`--model` must not change corpus, chunk order, reference answers, LLM prompt or scoring. `retrieval-only` computes top-5 and top-1 on all 45 items and makes **zero LLM calls**. Fixed-gate abstention is determined from top-1 against the model's locked pooled-v1 gate. `end-to-end` reuses the same selected model-pack retriever, gate, composer and pack-scoped citation check; request and record an immutable LLM identity, `temperature=0`, prompt hash and errors. If the proxy cannot guarantee requested LLM identity/temperature, retrieval-only may complete, but the E2E comparison is `incomplete` and excluded from winner claims.

## Report structure

Each complete `(model, language, v2)` report includes:

- `model_key`, repository/revision/license, pack/snapshot and v2 hashes, ordered chunk ID hash, index/cache settings hash, device, timings, truncation count.
- `calibration`: pooled-v1 source hashes, fixed threshold, pooled and per-pack confusion counts (100 answerable, 20 OOC total); never refit on v2.
- `retrieval`: hit@5 `hits/38`, 95% CI and 45 per-item top-1 scores/top-5 IDs; this section does not depend on LLM availability.
- `abstention`: **fixed gate** correct OOC `n/7` and **E2E** correct OOC `n/7` separately, each with CI; E2E absent/N/A when not run.
- `generation`: answer count, citation count, strict citation precision over answered items (N/A if zero), CI and per-item citation references; mixed and evidence-language slices with counts.
- `sweep`: OOC-positive AUROC (+ CI) and PR points from v2 scores, labeled *descriptive, not used to select threshold*; N/A for a class-absent slice.
- `status`: `complete` only with 45 rows and zero errors and, for an E2E report, verified fixed LLM settings. Else `incomplete` with error count, reasons and unaffected retrieval rows retained.

Comparison output contains a **separate table per language**, 95% percentile CIs (10,000 question resamples, seed `20261022`) for each metric, paired question-ID model-difference intervals, Bonferroni-adjusted intervals for the 3 candidate pairs within a language (98.33% each), and a winner/`inconclusive` decision following FR-014. Pairing/resampling is within each language only. Disclose the E5 baseline's earlier v1 calibration exposure, pooled-gate distribution differences and the small OOC denominator. Do not collapse four languages into one winner or treat descriptive v2 sweep optima as deployable gates.

**Validation examples**: same query/model evaluated in both modes has the same retrieval top-5; an unreachable LLM leaves retrieval-only complete but E2E incomplete; requesting a model index whose embedded revision/dimension does not match the registry fails explicitly; citation IDs from another pack never score as correct.
