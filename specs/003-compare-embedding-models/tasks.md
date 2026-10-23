# Tasks: Embedding Model Comparison

**Input**: [spec.md](./spec.md), [plan.md](./plan.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/](./contracts/), and [quickstart.md](./quickstart.md).

**Scope**: Three pinned models (`e5-large`, `e5-base`, `bge-m3`) × four packs (C, C++, Python, Java). Each v2 set contains 45 **new** questions: 28 in-corpus, 10 mixed, 7 out-of-corpus. Frozen v1 sets and corpus snapshots must not change. Without `--model`, the feature 002 dashboard and CLI must retain their existing behavior.

## Mandatory execution protocol: checkpoint after EVERY task

> After completing one `Txxx`: **STOP**. **REPORT IN PERSIAN** the files created/changed, verification command and result, errors/deviations, and constitutional impact. Then **WAIT** for the user's explicit «تایید» before starting the next task—even one marked `[P]`. If the pilot or E2E run is incomplete because of LLM identity, temperature, rate limiting, or another error, do not claim success; stop and ask the user how to proceed. Commit each task after its approval; push only on explicit request. Before a commit, inspect staged files and scan for `.env`, credentials, embedding caches, and FAISS binaries. **Every file—especially Persian JSON—must be written with `encoding="utf-8"` and then read back and verified before the task is reported complete.**

**Format**: `- [ ] Txxx [P?] [US?] Action with exact file path`. `[P]` denotes technical independence, **not** permission to bypass the checkpoint. Complete and verify one task per turn; split a task further only with user approval.

---

## Phase 1: Setup and baseline audit

**Goal**: Create an independent branch, verify feature 002 prerequisites, and align design contracts. Do not author any v2 questions yet.

- [X] T001 From `main`, create branch `003-compare-embedding-models` without resetting or discarding existing work. Verify all four `data/eval/{c,cpp,python,java}/eval-set.<lang>.v1.json` files have 30 items in the 20/5/5 split, all four manifests/indices are ready, T027 is `[X]` in `specs/002-multi-language-dashboard/tasks.md`, and `pytest tests/ -q` passes. Record v1 file hashes and `chunk_id` lists **in index order** in `specs/003-compare-embedding-models/baseline-audit.md`. Principles V/VI/VIII: frozen, isolated baseline.
  - CHECKPOINT: STOP → report branch, four hashes/counts, prerequisite and test results → wait for explicit «تایید» before T002.
- [X] T002 Align `specs/003-compare-embedding-models/contracts/model-config.md`, `specs/003-compare-embedding-models/contracts/evaluation-cli-and-report.md`, and `specs/003-compare-embedding-models/quickstart.md` with the revised plan: read canonical pack chunks rather than copying them; commit official JSON and Markdown, not cache/FAISS; distinguish API-returned LLM identity and exploratory pooled analysis. Verify links and spec consistency. Principle VI: documentation agrees with intended behavior.
  - CHECKPOINT: STOP → report contract/quickstart changes and link/consistency checks → wait for explicit «تایید» before T003.
- [X] T003 Write FAIL-first `ModelCandidate` contract tests in `tests/unit/test_model_config.py`: three pinned SHA/license/model-card entries; dimensions 1024/768/1024; E5 prefixes vs instruction-free BGE-M3; normalization and max_tokens 512/512/8192. Reject unknown models and floating revisions. Run only these tests and record failures caused by missing implementation.
  - CHECKPOINT: STOP → report test cases and expected failures → wait for explicit «تایید» before T004.
- [X] T004 Add the pinned registry in `data/eval/model-comparison/models.json` and minimal loading/validation in `src/index/model_config.py`. Keep `e5-large` as the default; verify the SHAs, MIT licenses, prefixes, normalization, dimensions, and max_tokens against [the contract](./contracts/model-config.md). Never load a floating `main` revision. Make T003 pass. Principles III/VI.
  - CHECKPOINT: STOP → report registry contents and passing T003 tests → wait for explicit «تایید» before T005.

---

## Phase 2: Shared foundation and mandatory pilot (BEFORE 180 questions)

**Goal**: Prove the smallest real model → index → calibration → retrieval-only → E2E flow. The pilot uses only C and `e5-large`; its questions belong to neither v1 nor v2.

- [X] T005 Write FAIL-first tests in `tests/unit/test_model_embeddings.py` for query/passage prefixes, normalization, dimension, model-card length limits, truncation counts, and unchanged raw chunk text. Compare an E5 baseline example with current output. Principles III/IV/VI.
  - CHECKPOINT: STOP → report expected failures and tested model-card rules → wait for explicit «تایید» before T006.
- [X] T006 Extend the embedding boundary in `src/index/embed.py` using T004 config: model-specific query/passage preparation, normalized dense vectors, and lazy model loading. Preserve the current E5 behavior without `--model`; never rewrite `chunks.jsonl`. Pass T005 and existing regression tests.
  - CHECKPOINT: STOP → report candidate settings and unchanged default behavior → wait for explicit «تایید» before T007.
- [X] T007 Write FAIL-first cache tests in `tests/unit/test_embedding_cache.py`: keys include revision, prefix/normalization/max_tokens, ordered `(chunk_id, text)` pairs, and vector type. Each change must miss; an exact hit avoids re-encoding; partial output cannot be ready; incompatible IDs/dimensions fail.
  - CHECKPOINT: STOP → report the hit/miss matrix and expected failures → wait for explicit «تایید» before T008.
- [X] T008 Implement model×pack caching/building in `src/index/research_cache.py` and `src/index/__main__.py`: explicit `--model` writes FAISS plus tracked `ids.json`/metadata under `data/research/embedding-compare/<model>/<lang>/`; read and hash canonical `data/index/<lang>/chunks.jsonl`; write cache/index atomically. Update `.gitignore` so only new embedding caches and FAISS binaries are ignored. Keep operational `python -m src.index build --lang c` unchanged; pass T007.
  - CHECKPOINT: STOP → report paths, hashes, cache hits/misses, and unchanged operational index → wait for explicit «تایید» before T009.
- [X] T009 Write FAIL-first index contract tests in `tests/contract/test_model_pack_index.py`: `Retriever` requires matching model_key/pack/hash/dimension, reads chunks only from the selected pack, rejects mismatches explicitly, and never validates a foreign-pack citation.
  - CHECKPOINT: STOP → report contract failures and positive default-path control → wait for explicit «تایید» before T010.
- [X] T010 Extend `src/qa/retriever.py` with a model-specific index path and canonical chunk path, validating hashes/IDs/dimensions. Reuse existing `faiss_store` and `has_chunk`; preserve the no-model path. Pass T009 and current scoped-citation tests. Principles II/VIII.
  - CHECKPOINT: STOP → report mismatch rejection, isolation, and regressions → wait for explicit «تایید» before T011.
- [X] T011 Write FAIL-first pooled-calibration tests in `tests/unit/test_pooled_calibration.py`: one threshold per model from **all four combined v1 sets** (100 answerable/20 OOC), maximum balanced accuracy, higher-threshold tie break, counts, and confusion separately for each pack. Prove that v2 is never read.
  - CHECKPOINT: STOP → report expected failures and tie-case result → wait for explicit «تایید» before T012.
- [X] T012 Extend `src/eval/calibrate.py` with `--model` and `--pooled-v1`; save locked `CalibrationRecord` under `data/eval/model-comparison/calibration/<model>.json`. Do not alter operational gates in `src/qa/pack_config.py`. Pass T011 and run E5-large over the four v1 sets, reporting the pooled threshold and any score overlap.
  - CHECKPOINT: STOP → report 120 scores, locked E5 gate, and four confusion tables → wait for explicit «تایید» before T013.
- [X] T013 Write FAIL-first tests in `tests/unit/test_provider_metadata.py` for sent `temperature=0`, provider/timestamp/API-returned `model` on JSON and SSE responses, missing/changing/unexpected model IDs, and rejected temperature. Ensure credentials never enter outputs; retrieval-only must not depend on the provider.
  - CHECKPOINT: STOP → report metadata/temperature failures and secret-leak checks → wait for explicit «تایید» before T014.
- [X] T014 Extend `src/qa/provider.py` only to send temperature and return provider, timestamp, and response model ID for JSON/SSE. Pre-register and compare the expected response ID for research runs; explicitly state that a stable alias does not prove an unchanged backend. Pass T013 and existing provider tests; unknown identity makes only E2E incomplete.
  - CHECKPOINT: STOP → report JSON/SSE behavior, ID checks, and alias limitation → wait for explicit «تایید» before T015.
- [X] T015 Write FAIL-first tests in `tests/integration/test_research_eval_modes.py`: `--model`/retrieval-only makes zero LLM calls and has the same model's top-5 as E2E; E2E uses the research gate and selected pack's citation validation; default `python -m src.eval run --lang c` remains the operational v1 run.
  - CHECKPOINT: STOP → report expected failures and default-path control → wait for explicit «تایید» before T016.
- [X] T016 Extend `src/eval/run.py` and the dependency-injection boundary in `src/web/app.py` for model/mode selection while reusing **the same answer/abstain logic**. Retrieval-only performs retrieval only; E2E receives the same model×pack `Retriever`, pooled gate, and `has_chunk` guard. Pass T015 and v1 regression tests; do not copy the pipeline.
  - CHECKPOINT: STOP → report both modes and unchanged student-facing flow → wait for explicit «تایید» before T017.
- [X] T017 Author exactly **9 new C pilot questions** for `e5-large` in `data/eval/pilot/eval-set.c.pilot.json` (5 in-corpus, 2 mixed, 2 out-of-corpus). Do not copy chunk/v1 wording. Give every answerable item real `expected_source_ids`, a grounded answer summary, source/license provenance; OOC items need empty IDs and an abstention reason. Exclude pilot items from both v2 and calibration.
  - CHECKPOINT: STOP → report 9 IDs, 5/2/2 counts, source validity, and non-copied examples for user review → wait for explicit «تایید» before T018.
- [X] T018 Run the full `e5-large × c` pilot in retrieval-only and E2E modes on `data/eval/pilot/eval-set.c.pilot.json`. Record index/cache, pooled-v1 gate, hit@5, gate decision, pack-internal citations, LLM metadata, time/cost, and errors in `specs/003-compare-embedding-models/pilot-results.md`. If E2E is incomplete due to identity/temperature/rate limit, **STOP before authoring 180 questions** and request user direction; never use pilot for v2/calibration.
  - CHECKPOINT: STOP → report all 9 rows and an explicit healthy/blocked pilot verdict → wait for explicit «تایید» before T019. **No v2 questions before this approval.**

---

## Phase 3: US1 — Auditable v2 research set (P1)

**Goal**: Four independent, source-grounded 45-question sets. **Independent test**: each set has 28/10/7 items, answerable references resolve within its own pack, OOC items have empty IDs/reasons, questions do not copy or paraphrase v1/chunk text, and all v1 hashes remain unchanged. Principles I/II/IV/V/VI.

### Tests and validation

- [X] T019 [US1] Write FAIL-first schema/provenance tests in `tests/unit/test_v2_provenance.py`: `BenchmarkItem` needs unique item_id, pack_id, version, Persian question, valid qtype, evidence_language `fa|en|mixed` (`none` for OOC), authorship/review metadata; answerable items need real sources and grounded summaries, OOC items need `expected_source_ids=[]` and `abstain_reason`. Test rejection of v1/chunk copies.
  - CHECKPOINT: STOP → report expected failures and a rejected duplicate example → wait for explicit «تایید» before T020.
- [X] T020 [US1] Implement `src/eval/validate_set.py`: unique IDs, sources only from the selected pack, provenance/license/evidence language, literal chunk copying and near-v1 paraphrases flagged for human review, and **exactly 45 items in 28/10/7 for a complete set**. Permit 28-item drafts only as incomplete, never published. Pass T019.
  - CHECKPOINT: STOP → report automated rules and human-review limits → wait for explicit «تایید» before T021.

### Author language by language; each completed language has its own review checkpoint

- [X] T021 [P] [US1] Draft 28 **new C in-corpus** questions in `data/eval/c/eval-set.c.v2.json`: non-copied Persian wording, same-pack expected_source_ids, grounded answer summaries, source/license provenance, and evidence language derived from each actual Persian/English source.
  - CHECKPOINT: STOP → report 28 valid references, auditable examples, and draft status → wait for explicit «تایید» before T022.
- [X] T022 [US1] Add 10 new mixed and 7 new OOC questions to `data/eval/c/eval-set.c.v2.json`. Validate the complete 45-item 28/10/7 set with T020, compare with v1, manually check against chunk wording, and require empty IDs/abstention reasons for OOC. **Present the completed C set for its own user review.**
  - CHECKPOINT: STOP → report C counts, sources, and question quality → wait for explicit «تایید» before T023.
- [X] T023 [P] [US1] Draft 28 **new C++ in-corpus** questions in `data/eval/cpp/eval-set.cpp.v2.json` with same-pack sources, grounded summaries, and actual Persian/English evidence labels; do not copy v1 or chunk wording.
  - CHECKPOINT: STOP → report 28 C++ sources/evidence labels and draft status → wait for explicit «تایید» before T024.
- [X] T024 [US1] Add 10 new mixed and 7 new OOC questions to `data/eval/cpp/eval-set.cpp.v2.json`. Validate all 45 items in 28/10/7, sources, licenses, and non-duplication against v1/chunks. **Present the completed C++ set for its own user review.**
  - CHECKPOINT: STOP → report 45 items and representative C++ evidence → wait for explicit «تایید» before T025.
- [ ] T025 [P] [US1] Draft 28 **new Python in-corpus** questions in `data/eval/python/eval-set.python.v2.json`: Persian question → frozen official English source, valid expected_source_ids, grounded summary, provenance/license, and no v1/chunk copying.
  - CHECKPOINT: STOP → report 28 sources and Python cross-lingual quality → wait for explicit «تایید» before T026.
- [ ] T026 [US1] Add 10 new mixed and 7 new OOC questions to `data/eval/python/eval-set.python.v2.json`. Validate 45 items in 28/10/7, English evidence, summaries, and non-duplication against v1/chunks. **Present the completed Python set for its own user review.**
  - CHECKPOINT: STOP → report 45 items and difficult Python cases → wait for explicit «تایید» before T027.
- [ ] T027 [P] [US1] Draft 28 **new Java in-corpus** questions in `data/eval/java/eval-set.java.v2.json` from frozen official English documentation: valid same-pack IDs, grounded summaries, provenance/license, and no literal chunk/v1 copying.
  - CHECKPOINT: STOP → report 28 sources and Java cross-lingual quality → wait for explicit «تایید» before T028.
- [ ] T028 [US1] Add 10 new mixed and 7 new OOC questions to `data/eval/java/eval-set.java.v2.json`. Validate the full 45-item 28/10/7 set with T020 and **present the completed Java set for its own user review**.
  - CHECKPOINT: STOP → report 45 Java items, provenance, and non-copied wording → wait for explicit «تایید» before T029.
- [ ] T029 [US1] Audit **all 180 items** in `specs/003-compare-embedding-models/v2-audit.md`: four 45-item 28/10/7 sets, 180/180 provenance records, unique IDs, Persian non-copied wording, valid chunks/evidence language, and unchanged SHA-256 of every v1 file since T001. Return any questionable item to user review before publication.
  - CHECKPOINT: STOP → report four summaries and all open/cleared audit issues → wait for explicit «تایید» before T030. **US1 is independently testable.**

---

## Phase 4: US2 — Compare models using the existing pipeline (P1)

**Goal**: 12 model×pack configurations from identical chunks, pooled-v1 gates, retrieval-only without LLM, and E2E with the same citation guard. **Independent test**: model selection, isolation, and unchanged default behavior can be proven on pilot/v1 alone; full v2 comparison depends on US1. Principles I/II/III/V/VI/VIII.

- [ ] T030 [US2] Implement/run real model-card smoke tests for `e5-base` and `bge-m3` in `tests/integration/test_model_card_smoke.py`: verify all three model SHAs/MIT licenses, E5 prefixes vs instruction-free BGE, normalization, max_tokens, 768/1024 dense dimensions, and short-input truncation reporting. Load one model at a time on CPU. If a card contradicts T004 config, STOP and obtain approval before indexing.
  - CHECKPOINT: STOP → report model revisions/licenses/dimensions and CPU cost → wait for explicit «تایید» before T031.
- [ ] T031 [US2] Build all four research `e5-large` indices from `data/index/<lang>/chunks.jsonl` under `data/research/embedding-compare/e5-large/<lang>/`. Check second-run cache hits, canonical hashes/IDs, dimension 1024, and unchanged operational no-`--model` behavior. Record results in `specs/003-compare-embedding-models/index-build-log.md`.
  - CHECKPOINT: STOP → report four chunk counts/hashes and cache hits → wait for explicit «تایید» before T032.
- [ ] T032 [US2] Build four `e5-base` indices under `data/research/embedding-compare/e5-base/<lang>/` at dimension 768 with identical canonical chunk hashes/IDs. Record cache and truncation in `specs/003-compare-embedding-models/index-build-log.md`; do not touch other indices.
  - CHECKPOINT: STOP → report four builds, time/memory, and unchanged corpus → wait for explicit «تایید» before T033.
- [ ] T033 [US2] Build four dense `bge-m3` indices under `data/research/embedding-compare/bge-m3/<lang>/` at dimension 1024. Record model-card behavior, cache, truncation, and CPU timings in `specs/003-compare-embedding-models/index-build-log.md`. If local resources fail, use optional Kaggle only with identical settings/hashes and report CPU/GPU differences.
  - CHECKPOINT: STOP → report four builds or a genuine blocker and reproduction path → wait for explicit «تایید» before T034.
- [ ] T034 [US2] Lock the official report contract in `tests/contract/test_research_reports.py` and finish v2 JSON/Markdown output in `src/eval/run.py`: 45 rows per official run; model revision, chunk/v2 hashes, provider/ID/temperature/time for E2E, complete/incomplete status and errors. Official final JSON **must be stageable/committable**. Change `.gitignore` so only new embedding caches and FAISS binaries are ignored and the old JSON-report rule does not cover official v2 JSON. Check `git check-ignore` on an official JSON and a cache; do not promote incomplete JSON to official evidence.
  - CHECKPOINT: STOP → report schema, tests, ignore checks, and sample staged-file scan → wait for explicit «تایید» before T035.
- [ ] T035 [US2] Lock pooled-v1 gates for the remaining candidates with `src/eval/calibrate.py --model e5-base|bge-m3 --pooled-v1` and review all three records in `data/eval/model-comparison/calibration/`: each has 100/20 samples, balanced accuracy/tie rule, four pack confusion tables, and no v2 data. Do not change operational gates.
  - CHECKPOINT: STOP → report three gates and per-pack pooling effects → wait for explicit «تایید» before T036.
- [ ] T036 [US2] Run three retrieval-only models on the 45 **C v2** questions using `src/eval/run.py --lang c --model ... --mode retrieval-only`. Save top-5/score rows, hit@5 on 38 answerable questions, and fixed-gate abstention on 7 OOC in `data/eval/c/reports/v2/`; assert zero LLM calls and zero errors.
  - CHECKPOINT: STOP → report three C results with numerators/denominators → wait for explicit «تایید» before T037.
- [ ] T037 [US2] Run the same three retrieval-only models on **C++ v2** in `data/eval/cpp/reports/v2/`. Check 45 rows per model, 38-item hit@5, 7-item gate results, zero LLM calls, and matching corpus hashes.
  - CHECKPOINT: STOP → report three C++ results and errors/absence of errors → wait for explicit «تایید» before T038.
- [ ] T038 [US2] Run three retrieval-only models on **Python v2** in `data/eval/python/reports/v2/`. Verify English-source evidence labels, 45 rows, separate hit@5/gate metrics, and zero LLM calls.
  - CHECKPOINT: STOP → report three Python results with numerators/denominators → wait for explicit «تایید» before T039.
- [ ] T039 [US2] Run three retrieval-only models on **Java v2** in `data/eval/java/reports/v2/`. Verify 45 rows, English evidence, hit@5/gate metrics, zero LLM calls, and no threshold tuning on v2.
  - CHECKPOINT: STOP → report three Java results and locked-gate check → wait for explicit «تایید» before T040.
- [ ] T040 [US2] Run E2E for three models on **C v2** with identical LLM version/`temperature=0`/prompt in `data/eval/c/reports/v2/`. Record every API-returned model ID, timestamp, and provider; check C-only citations and precision/E2E abstention separately from the fixed gate. Unknown/changing ID or rejected temperature makes E2E incomplete, not retrieval-only.
  - CHECKPOINT: STOP → report three C E2E statuses and identity/citation evidence → wait for explicit «تایید» before T041.
- [ ] T041 [US2] Run E2E for three models on **C++ v2** under `data/eval/cpp/reports/v2/` using the same locked LLM/version/temperature/prompt and pack guard. Report 45 rows per model and errors, precision, and abstention separately.
  - CHECKPOINT: STOP → report three C++ E2E statuses and citations → wait for explicit «تایید» before T042.
- [ ] T042 [US2] Run E2E for three models on **Python v2** under `data/eval/python/reports/v2/` with the same fixed settings. Check 45 rows per model, returned model IDs, citation precision, abstention, and zero foreign-pack citations.
  - CHECKPOINT: STOP → report three Python E2E statuses and cross-lingual limits → wait for explicit «تایید» before T043.
- [ ] T043 [US2] Run E2E for three models on **Java v2** under `data/eval/java/reports/v2/` with the same settings. Check 45 rows per model, model ID/errors, precision/abstention, and valid Java-pack citations.
  - CHECKPOINT: STOP → report three Java E2E statuses and retrieval-only comparison → wait for explicit «تایید» before T044.
- [ ] T044 [US2] Run model/pack isolation integration tests in `tests/integration/test_research_isolation.py`: a wrong model or pack index fails explicitly, foreign citations abstain/are rejected, retrieval-only uses no LLM, and feature 002's operational path remains green under `pytest tests/ -q`.
  - CHECKPOINT: STOP → report isolation matrix and regressions → wait for explicit «تایید» before T045. **US2 is independently testable using pilot/v1; its full v2 data is now collected.**

---

## Phase 5: US3 — Paper-ready evidence (P2)

**Goal**: Quantify uncertainty, describe threshold sensitivity, and decide winner/inconclusive using paired questions. **Independent test**: fixed synthetic rows can produce four per-language tables, CIs, and reproducible decisions without the student UI; missing valid E2E must not invalidate retrieval-only. Principles V/VI.

- [ ] T045 [P] [US3] Write FAIL-first paired-bootstrap tests in `tests/unit/test_paired_bootstrap.py`: 10,000 resamples with seed `20261022` over identical item IDs, 95% percentile CI per metric, Bonferroni-adjusted 98.33% difference CI for three model pairs, precision conditional on answered rows in each resample, and N/A at denominator zero.
  - CHECKPOINT: STOP → report winner/inconclusive fixtures and expected failures → wait for explicit «تایید» before T046.
- [ ] T046 [US3] Implement CI and paired differences in `src/eval/comparison.py`; accept only complete same-language rows with matching item IDs, numerators/denominators, and answer counts. Declare a winner only when its hit@5 difference CI exceeds zero against **every** alternative and precision/both abstention measures show no significant harm; otherwise `inconclusive`. Pass T045.
  - CHECKPOINT: STOP → report seeded reproducibility and inconclusive cases → wait for explicit «تایید» before T047.
- [ ] T047 [P] [US3] Write FAIL-first threshold-sweep tests in `tests/unit/test_threshold_sweep.py`: OOC is the positive class; calculate AUROC and PR curve from v2 scores, CI for summary measures, N/A for class-absent slices, and unchanged locked pooled-v1 threshold.
  - CHECKPOINT: STOP → report expected failures and no-v2-leakage control → wait for explicit «تایید» before T048.
- [ ] T048 [US3] Complete descriptive sweep and separate fixed-gate/E2E abstention in `src/eval/comparison.py`. Show the observed v2 optimum **only** as sensitivity analysis; never change calibration code or the locked threshold. Pass T047.
  - CHECKPOINT: STOP → report fixture AUROC/PR and unchanged gate → wait for explicit «تایید» before T049.
- [ ] T049 [US3] Produce official per-language reports with `src/eval/__main__.py`/`src/eval/comparison.py`: for each language, three model rows for retrieval-only hit@5, answered-only citation precision, both abstention measures, mixed/evidence-language slices, CI/denominators, and `winner|inconclusive`. Make official machine-readable JSON and Markdown under `data/eval/<lang>/reports/v2/` committable. Run T034 schema checks and per-item reproduction; never mix incomplete and complete runs.
  - CHECKPOINT: STOP → report four tables, CIs, and official file IDs → wait for explicit «تایید» before T050.
- [ ] T050 [US3] Add an **explicitly exploratory secondary pooled analysis** in `src/eval/comparison.py` and a labeled section of `docs/EMBEDDING-COMPARISON.md`. Show four-language counts/CIs alongside—not instead of—the four primary tables. Add `tests/unit/test_exploratory_pool.py` proving pooled results neither tune gates nor produce a global winner.
  - CHECKPOINT: STOP → report pooled evidence and per-language precedence → wait for explicit «تایید» before T051.
- [ ] T051 [US3] Finish the paper narrative and publication provenance in `docs/EMBEDDING-COMPARISON.md`: link 180 questions/reference answers/sources and 12 official reports; document licenses, models/SHAs, uncertainty, seven OOC items per language, E5's earlier v1 exposure, pooled-gate risk, silent provider changes, and CPU/Kaggle differences. Do not quote unlicensed text or assert a winner without CI support.
  - CHECKPOINT: STOP → report citation/license audit and explicit paper limitations → wait for explicit «تایید» before T052. **US3 is presentable independently of the student UI.**

---

## Final phase: Reproduction and closeout

- [ ] T052 Finalize the implemented reproduction guide in `specs/003-compare-embedding-models/quickstart.md` and `README.md`: CPU build/cache (Kaggle fallback only), pooled-v1 calibration, 12 retrieval-only/E2E combinations, committed official JSON+Markdown, bootstrap/sweep, and incomplete E2E behavior. Smoke-check guide commands and links to official reports.
  - CHECKPOINT: STOP → report both documents, commands tried, and valid links → wait for explicit «تایید» before T053.
- [ ] T053 Run final validation from `specs/003-compare-embedding-models/quickstart.md`: `pytest tests/ -q`, feature 002 default-path smoke test, unchanged v1/chunk SHAs, retrieval-only reproduction, and inspection of 12 official JSON/Markdown report pairs. Count E2E as complete only with valid provider identity. Record a staged scan for `.env`/keys/cache/FAISS and official JSON status in `specs/003-compare-embedding-models/VALIDATION.md`; do not close the feature if a prerequisite/run is incomplete.
  - CHECKPOINT: STOP → report full log, deviations, and 12-combination status → wait for explicit «تایید»; **only then is the feature complete.**

---

## Dependencies and execution order

- **Setup T001–T004** → **foundation/pilot T005–T018**. T018 is a hard gate: no v2 authorship before an approved pilot; unverified E2E requires a stop and user decision, not automatic continuation.
- **US1 T019–T029** follows the pilot: validator first; each language progresses from draft to a separately reviewed complete set; then audit all 180 items and unchanged v1 hashes.
- **US2 T030–T044**: model-card smoke → four indices per model → official JSON contract → three pooled-v1 calibrations → four retrieval-only languages → four E2E languages → isolation tests. Model selection is independently testable with pilot/v1, but 12 full v2 runs depend on US1.
- **US3 T045–T051**: statistical helpers can be tested on fixtures independently, but paper evidence requires valid US2 rows. Pooled analysis is exploratory and follows per-language tables. **T052–T053** depend on all stories.
- FAIL-first applies only where implementation is absent; an LLM outage or failed model download is **not** an acceptable contract-test failure. Each task has its own approval gate; `[P]` never bypasses it.

### Parallel opportunities (ONLY if the user explicitly waives checkpoints)

- After T020, independent drafts in `data/eval/c/eval-set.c.v2.json` (T021), `data/eval/cpp/eval-set.cpp.v2.json` (T023), `data/eval/python/eval-set.python.v2.json` (T025), and `data/eval/java/eval-set.java.v2.json` (T027) touch different files. Each completed language still requires its own review checkpoint.
- Once inputs are fixed, fixture tests in `tests/unit/test_paired_bootstrap.py` (T045) and `tests/unit/test_threshold_sweep.py` (T047) are independent. Normal execution remains sequential and approval-gated.
- **Never parallelize**: heavy model loads on ~15.6 GiB RAM, E2E calls against a rate-limited provider, or index builds while canonical chunks are changing.

## Delivery strategy

1. **Pilot MVP**: T001–T018, one pack × one model × nine new questions through the real path, with approval before investing in 180 questions.
2. **Independent US1**: T019–T029, four auditable v2 sets; do not claim a model result yet.
3. **US2**: T030–T044, 12 model-pack comparisons with retrieval-only evidence independent of LLM and E2E only when identity/settings are recorded.
4. **US3 + closeout**: T045–T053, CIs, sweep, official reports, and paper reproduction; no global winner from pooled analysis.

**Constitution trace**: I/II grounded reference answers and verifiable citations; III existing pipeline and only three candidates; IV Persian/code-mixed questions; V per-language results first; VI revisions/hashes/official JSON/reproduction; VII only four bounded packs; VIII isolated model×pack indices and citations.
