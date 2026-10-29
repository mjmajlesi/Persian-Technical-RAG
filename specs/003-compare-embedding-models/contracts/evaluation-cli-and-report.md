# Contract: research evaluation and comparison

**Status**: implemented research CLI and report comparison. Default `python -m src.eval run --lang c` remains the v1 operational run. Historical reports are frozen evidence, not automatically rerun by this contract.

## Commands

```powershell
# Calibrate one research gate per model from all four frozen v1 sets (120 items).
.\.venv\Scripts\python -m src.eval.calibrate --model bge-m3 --pooled-v1

# Select model + one language, same 45 new v2 items for every candidate.
.\.venv\Scripts\python -m src.eval run --lang python --model bge-m3 --set data/eval/python/eval-set.python.v2.json --mode retrieval-only
.\.venv\Scripts\python -m src.eval run --lang python --model bge-m3 --set data/eval/python/eval-set.python.v2.json --mode end-to-end

# Compare complete model runs for each language, without a blended rank.
.\.venv\Scripts\python -m src.eval compare --set-version v2
```

`--model` must not change corpus, chunk order, reference answers, LLM prompt or scoring. `retrieval-only` computes top-5 and top-1 on all 45 items and makes **zero LLM calls**. Fixed-gate abstention is determined from top-1 against the model's locked pooled-v1 gate. `end-to-end` reuses the same selected model-pack retriever, gate, composer and pack-scoped citation check; record the **fixed LLM identity** per response: provider name, request timestamp and the `model` identifier **returned by the API**, plus `temperature=0` actually sent, prompt hash and errors. Pre-register the expected response model ID for the provider and compare it across every response in the run; a missing, changing or unexpected ID, or a rejected temperature parameter, makes **only E2E incomplete**. A returned stable ID or an accepted `temperature` parameter does not prove the backend is unchanged (a provider may silently serve different weights behind one alias): disclose this residual risk; never claim the returned ID proves immutable weights.

The official comparison builder also rejects inconsistent recorded provider/model identities across complete E2E runs and citations outside the same row's first five retrieval IDs or the selected canonical pack. It rejects duplicate normalized question text within a v2 set. Incomplete E2E remains N/A rather than a successful abstention. For v1, `--index-dir` must resolve to the selected language's operational index; incompatible overrides fail rather than mixing retrieval and answer indices.

## Report structure

Each complete `(model, language, v2)` report includes:

- `model_key`, repository/revision/license, pack/snapshot and v2 hashes, ordered chunk ID hash, index/cache settings hash, device, timings, truncation count; for E2E also provider name, request timestamp, API-returned `model` ID, sent `temperature=0` and prompt hash. Committed report metadata records **only the provider name**, never a provider base URL, access token, API key or other credential.
- `calibration`: pooled-v1 source hashes, fixed threshold, pooled and per-pack confusion counts (100 answerable, 20 OOC total); never refit on v2.
- `retrieval`: hit@5 `hits/38`, 95% CI and 45 per-item top-1 scores/top-5 IDs; this section does not depend on LLM availability.
- `abstention`: **fixed gate** correct OOC `n/7` and **E2E** correct OOC `n/7` separately, each with CI; E2E absent/N/A when not run.
- `generation`: answer count, citation count, strict citation precision over answered items (N/A if zero), CI and per-item citation references; mixed and evidence-language slices with counts.
- `sweep`: OOC-positive AUROC (+ CI) and PR points from v2 scores, labeled *descriptive, not used to select threshold*; N/A for a class-absent slice.
- `status`: retrieval-only is `complete` with 45 valid rows and zero retrieval errors; E2E is `complete` only with 45 valid rows, zero E2E errors and verified fixed LLM settings. Otherwise label E2E `incomplete`, retain its error count and reasons, and do not report final E2E metrics.

When E2E is incomplete, the official report contains valid retrieval-only results and an E2E section labeled `incomplete` with no final E2E metrics; partial E2E rows are kept only in diagnostics.

Comparison output contains a **separate table per language**, 95% percentile CIs (10,000 question resamples, seed `20261022`) for each metric, paired question-ID model-difference intervals, Bonferroni-adjusted intervals for the 3 candidate pairs within a language (98.33% each), and a winner/`inconclusive` decision following FR-014. Pairing/resampling is within each language only. A **secondary pooled (four-language) analysis, when included, is explicitly exploratory**: it is labeled as such, shown *alongside—not instead of*—the per-language tables with its own sample counts and uncertainty, and it must never tune gates nor produce a global winner. Disclose the E5 baseline's earlier v1 calibration exposure, pooled-gate distribution differences and the small OOC denominator. Do not collapse four languages into one winner or treat descriptive v2 sweep optima as deployable gates.

## Committed evidence and ignore policy

Official reports are ordinary versioned files: for each `(model, language)` run, write machine-readable JSON (with complete retrieval-only rows, run metadata and E2E status) and readable Markdown under `data/eval/<lang>/reports/v2/<model>/`, then stage and commit them with the code/config changes. Any broad historical ignore rule that would cover these official v2 JSON files must be explicitly overridden so they can be staged. Regenerable artifacts under `data/research/embedding-compare/<model>/<lang>/` (embedding caches, FAISS binaries) stay ignored. Before every commit of this feature: run `git check-ignore` on one sample official JSON (must be **not** ignored) and one cache/FAISS file (must be ignored), and scan staged paths and content for `.env`, credentials and binaries. The official report retains an incomplete E2E error count and reasons; partial E2E rows and detailed errors belong only in separately labeled diagnostics, never in complete-run comparisons.

**Validation examples**: same query/model evaluated in both modes has the same retrieval top-5; an unreachable LLM leaves retrieval-only complete but E2E incomplete; requesting a model index whose embedded revision/dimension does not match the registry fails explicitly; citation IDs from another pack never score as correct.
