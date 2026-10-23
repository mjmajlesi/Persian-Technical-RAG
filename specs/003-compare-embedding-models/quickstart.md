# Quickstart: embedding-model comparison validation

**Status:** planned commands to run **after implementation and v2 authoring**. They are not runnable on the current 002-only codebase yet. See [CLI/report contract](./contracts/evaluation-cli-and-report.md), [model registry contract](./contracts/model-config.md) and [data model](./data-model.md).

## Prerequisites

- Python 3.11 and project `.venv` from the root README; network access for first downloads, enough disk for three pinned weight revisions, and the existing frozen four-pack corpora.
- Canonical execution: the CPU-only 15.6 GiB laptop, **one model at a time**. `e5-large`, `e5-base`, `bge-m3` and their exact revisions/licensing are registered before any v2 run. Kaggle is optional only with identical hashes/settings/commands, never required by the examiner.
- Four independently audited 45-question v2 sets (28/10/7), separate from the unmodified v1 sets. Check provenance and frozen chunk IDs before publication.
- Retrieval-only runs require **no LLM key**. For end-to-end runs supply `.env` locally with a verifiably pinned LLM identity, unchanged prompt and `temperature=0`; a dynamic proxy alias without verifiable revision is not acceptable evidence for E2E comparisons.

## 1. Build model×pack indices from the same frozen chunks

```powershell
foreach ($model in 'e5-large', 'e5-base', 'bge-m3') {
    foreach ($lang in 'c', 'cpp', 'python', 'java') {
        .\.venv\Scripts\python -m src.index build --lang $lang --model $model
    }
}
```

Expected: 12 **separate** research indices. The canonical chunk counts are C=503, C++=201, Python=253 and Java=73 (**1,030 total**); vector dimensions are `e5-large`=1024, `e5-base`=768 and `bge-m3`=1024. Each research manifest references the SHA-256 hash of its pack's **canonical** `data/index/<lang>/chunks.jsonl`; read and validate that file in place, never copy or re-chunk it. The hashes and ordered IDs must match `specs/003-compare-embedding-models/baseline-audit.md` before and after building; no operational `data/index/<lang>/` files change. Only embedding caches and FAISS binaries in research directories are ignored; `ids.json` and manifests remain tracked. Re-run one build to confirm an exact-settings cache hit. A changed revision or chunk text invalidates the cache; a mismatched model index fails to load.

## 2. Lock one gate per model on pooled v1

```powershell
foreach ($model in 'e5-large', 'e5-base', 'bge-m3') {
    .\.venv\Scripts\python -m src.eval.calibrate --model $model --pooled-v1
}
```

Expected: one recorded threshold **per model**, selected from 100 answerable + 20 OOC v1 questions across all four packs using maximal balanced accuracy, with per-pack confusion counts. Freeze the values and data hashes before running v2; no v2-derived gate adjustments.

## 3. Run retrieval-only first, E2E second

```powershell
foreach ($model in 'e5-large', 'e5-base', 'bge-m3') {
    foreach ($lang in 'c', 'cpp', 'python', 'java') {
        .\.venv\Scripts\python -m src.eval run --lang $lang --model $model `
            --set "data/eval/$lang/eval-set.$lang.v2.json" --mode retrieval-only
    }
}
```

Expected: each of 12 retrieval-only reports has exactly 45 item rows, retrieval hit@5 on 38 answerable questions **without LLM calls**, fixed-gate OOC abstention on 7 questions and a descriptive v2 AUROC/PR sweep. Write the official machine-readable JSON (per-question retrieval rows and run metadata) and the Markdown summary under `data/eval/<lang>/reports/v2/<model>/`; these official reports are **versioned and committed**. Before each commit, `git check-ignore` must show one official JSON as *not* ignored and one cache/`faiss.index` as ignored, and the staged scan must be free of `.env`/keys/binaries. Only when the LLM identity/temperature can be checked, repeat with `--mode end-to-end`; the API-returned `model` ID, provider name and request timestamp are recorded per response and compared with a pre-registered expected ID. A complete E2E run adds answer/citation precision and **separate** E2E abstention. A 410/rate limit, missing/changing/unexpected ID or rejected `temperature=0` makes E2E incomplete without invalidating retrieval-only evidence.

When E2E is incomplete, the official report contains valid retrieval-only results and an E2E section labeled `incomplete` with no final E2E metrics; partial E2E rows are kept only in diagnostics.

## 4. Produce and inspect the comparison

```powershell
.\.venv\Scripts\python -m pytest tests/ -q
.\.venv\Scripts\python -m src.eval compare --set-version v2
```

Expected: four independent language tables × three candidates, estimates with 95% CIs and denominators, paired question-level bootstrap differences (10,000 resamples, seed `20261022`), Bonferroni-adjusted pairwise winner test and `inconclusive` where appropriate. If a pooled four-language analysis is shown, it is a labeled **exploratory secondary** section with its own counts and uncertainty; it never replaces the per-language tables, tunes gates or asserts a global winner. C/C++ source-language subsets are named from **evidence**, not assumed from pack name; Python/Java highlight fa→en. Inspect per-item provenance, model truncation counts, cache/index hashes, gate calibration record, and the explicit limitation that E5 had previously seen v1. Do not present one combined ranking or select a v2 threshold from the sweep.
