# Feature 003 final validation — T053

**Date:** 2026-10-25. **Branch/base:** `main` at `fc17efa` (T052 pushed).
**Scope:** validate the committed v2 evidence and local CPU reproduction;
no live E2E provider calls were made during T053. Approval of this checkpoint
is still required before declaring the feature closed.

## Executed checks

| Check | Result |
|---|---|
| `.\.venv\Scripts\python -m pytest tests/ -q --tb=short` | **182 passed, 3 skipped**, 1 existing FAISS/NumPy deprecation warning (425.20s). The skips are opt-in integration tests requiring pinned multi-GB CPU model downloads; real model-card/index smoke runs are recorded in [index-build-log.md](index-build-log.md). |
| Frozen v1 sets, canonical chunks, corpus manifests | SHA-256 of all 12 files matches the [T001 baseline audit](baseline-audit.md); ordered IDs equal each pack's regenerated chunk records (C 503, C++ 201, Python 253, Java 73). First manual C++ manifest hash entry in a scratch check contained a transcription typo; rechecking by parsing the baseline document itself passed for **all four packs**. No baseline file changed. |
| Feature 002 no-model path | All four packs `ready`; `Retriever(pack.index_dir)` **without** `model_key` returned five pack-scoped hits from one frozen v1 question per language, with no LLM call or index write. Default language remains C. |
| v2 retrieval-only reproduction | All **12** model-language runs repeated from the [quickstart](quickstart.md) into a unique temporary folder under `%LOCALAPPDATA%\Temp\opencode`. Each completed with 45 rows, zero retrieval errors and `end_to_end=not_run`; item IDs, top-5 IDs, hits, fixed-gate decisions and top-1 scores (absolute tolerance `1e-6`) matched the committed retrieval-only report. No official run was replaced. |
| 12 model-language official report pairs | Each pair has **one retrieval-only and one E2E JSON and Markdown** under `data/eval/<lang>/reports/v2/<model>/`. Both retrievals have identical 45 rows; E2E has 45 final responses, zero errors and registered returned ID `gpt-5.6-sol`. Model revisions/licenses, v2 and canonical chunk hashes, source-report SHA-256s, pack-scoped citations, timestamps, `temperature=0` and prompt hashes checked. |
| Four primary comparisons | `build_official_comparison` reproduced each committed JSON exactly; `comparison_markdown` reproduced each Markdown byte-for-byte. Decisions: C `inconclusive`, C++ `bge-m3`, Python `inconclusive`, Java `bge-m3`. No global winner, v2 gate change or replacement of valid retrieval metrics by incomplete E2E. |

Of the 540 official E2E item rows, **368** reached the provider and have
verified API-returned `model=gpt-5.6-sol`, provider name, timestamp, prompt
hash and sent temperature; **172** abstained at the fixed gate and therefore
made no LLM call. A pre-registered, stable returned ID verifies the recorded
API response identity, **not** immutable backend weights behind a proxy
alias. The live provider was not recontacted in T053; `temperature=0` does
not guarantee identical generated text in future runs. If a future E2E run
is incomplete or has a mismatched/missing ID, its E2E metrics are N/A and
cannot support a complete-run winner; valid retrieval remains separately
usable.

## Evidence and publication boundaries

- All 12 `(model, language)` official retrieval-only/E2E pairs are **complete**;
  none was inferred from partial diagnostics. The four primary JSON/Markdown
  files live under `data/eval/<lang>/reports/v2/comparison.v2.*`, linked in
  [the paper](../../docs/EMBEDDING-COMPARISON.md) with the v2 questions,
  reference summaries, origins, licenses and source-report hashes.
- CI/winner inference is within language only (10,000 paired question draws,
  seed `20261022`; 98.33% Bonferroni difference CI for the three model pairs).
  The four-language pooled analysis is explicitly secondary/exploratory;
  seven OOC examples per pack, E5's prior v1 exposure, English-only evidence
  in Python/Java, model length/truncation differences and provider alias
  drift limit broader claims.
- T053 did **not** regenerate a live 12×E2E batch or download the opt-in
  multi-GB smoke-test weights. CPU indices/caches already present on this
  machine were verified by retrieval-only replay; Kaggle was not used.

## Stage/ignore safety gate

Before any T053 commit: `git diff --cached --name-only` must contain only
`specs/003-compare-embedding-models/VALIDATION.md` and the T053 marker in
`specs/003-compare-embedding-models/tasks.md`. Read all staged files back as
UTF-8, scan staged paths and text for `.env`, tokens/keys, provider URLs,
embedding arrays (`.npy`/`.npz`), FAISS binaries and diagnostics, then run
`git diff --cached --check`. `git check-ignore -q --no-index` must return
**not ignored** for an official `comparison.v2.json` and **ignored** for a
research `faiss.index` (and `embeddings-*.npy`). T053 staged scan: **PASS**;
only the two UTF-8 documentation/task files above, no sensitive or binary
artifacts. Do not stage temporary replays.
