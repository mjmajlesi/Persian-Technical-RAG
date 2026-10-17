# Tasks: Multi-Language Dashboard

**Input**: Design documents from `/specs/002-multi-language-dashboard/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Cross-feature prerequisite**: Feature 001's answer path (T018+) MUST be complete before Phase 3 of this feature begins, since 002 routes through the same composer/endpoint. Foundational pack work (Phases 1–2) can proceed in parallel with finishing 001.

**Tests**: Included — contract tests (FAIL-first per story) + contamination/integration tests per the 001 TDD pattern.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Execution Protocol — MANDATORY per-task checkpoints (پروتکل اجرای اجباری)

> The user reviews and approves **every single task** before work continues.
> After finishing each task `Txxx`, the implementer MUST:
>
> 1. **STOP** — do not start `Tyyy` (the next task).
> 2. **REPORT** — write a short report: what was created/changed (files), how it was verified (command + result), and any deviations from the task text.
> 3. **WAIT** — for the user's explicit approval message (e.g. «تایید» / "approved Txxx") before proceeding.
>
> Each task below therefore ends with a `CHECKPOINT: STOP → report → wait for explicit approval` line naming the exact next task that is blocked. Skipping a checkpoint is a protocol violation, even if the code works.

## Path Conventions

- **Single project**: `src/`, `tests/`, `data/` at repository root (per plan.md — 002 extends the 001 project in place)

---

## Phase 1: Setup (Pack Migration + Routing Flags)

**Purpose**: Move the validated C snapshot into the pack layout and thread language selection through existing CLIs

- [X] T001 Migrate the C pack to per-language layout: move `data/corpus/full/*` to `data/corpus/c/`, rewrite `data/corpus/manifest.json` as `data/corpus/manifest.c.json` (add `language_id: "c"`, `display_name`, `eval_set_version: "v1"` header fields; origins rewritten to `data/corpus/c/`), move `data/index/*` to `data/index/c/`, and delete the old flat paths
  - CHECKPOINT: STOP → report moved paths + manifest diff → wait for explicit approval before T002.
- [X] T002 Thread a `--lang` flag (default `"c"`) through `src/ingest/__main__.py` and `src/index/__main__.py` so manifest/index paths resolve to `data/corpus/manifest.<lang>.json` and `data/index/<lang>/`; re-run both CLIs with `--lang c` and confirm byte-identical outputs to the migrated C index
  - CHECKPOINT: STOP → report CLI runs + byte comparison → wait for explicit approval before T003.
- [X] T003 Implement the pack registry in `src/web/packs.py` reading all `data/corpus/manifest.<lang>.json` files into LanguagePack descriptors (`language_id` enum c|cpp|python|java unique, `display_name` non-empty, `status` ready|empty enum with `empty` when the index dir is absent) with `default = "c"`
  - CHECKPOINT: STOP → report registry output on the C-only state → wait for explicit approval before T004.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: New language corpora, language-aware API, per-pack eval — MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Build the C++ corpus in `data/corpus/cpp/`: move the on-disk `c-notes-ch09-cpp-intro.md` there, fetch ~10–15 cppreference C++ pages with the T010b stdlib method and cleaning rules (URL/date/CC-BY-SA headers), write `data/corpus/manifest.cpp.json` (pack header fields + unique source_ids + licenses), and run ingest + index build with `--lang cpp`
  - CHECKPOINT: STOP → report source list + per-source chunk counts → wait for explicit approval before T005.
- [X] T005 Build the Python corpus in `data/corpus/python/`: fetch a named docs.python.org subset (tutorial + library sections for student-level questions) with the T010b method, write `data/corpus/manifest.python.json` (English-reference-only composition noted), and run ingest + index build with `--lang python`
  - CHECKPOINT: STOP → report source list + per-source chunk counts → wait for explicit approval before T006.
- [X] T006 Build the Java corpus in `data/corpus/java/`: fetch a named official-Java-docs subset (language basics + core library) with the T010b method, write `data/corpus/manifest.java.json` (English-reference-only composition noted), and run ingest + index build with `--lang java`
  - CHECKPOINT: STOP → report source list + per-source chunk counts → wait for explicit approval before T007.
- [X] T007 Implement `GET /api/languages` in `src/web/app.py` serving pack descriptors from the registry per `contracts/languages-api.md` (one entry per manifest file, `empty` status without index dir, `default: "c"`)
  - CHECKPOINT: STOP → report endpoint JSON on 4-pack state → wait for explicit approval before T008.
- [X] T008 Add the `language` field (default `"c"`) to `POST /api/ask` in `src/web/app.py` per `contracts/languages-api.md`: unknown language → `422` Persian error; `empty`-pack language → `200` `type: unavailable` with Persian message and zero citations, never an answer attempt
  - CHECKPOINT: STOP → report 422/unavailable probing → wait for explicit approval before T009.
- [X] T009 Store a per-pack abstention similarity threshold in each pack's config (`src/qa/pack_config.py`, default from T014's provisional value until calibrated) and thread it through `src/qa/abstain.py` `decide()` so each language applies its own threshold
  - CHECKPOINT: STOP → report config + threaded behavior → wait for explicit approval before T010.
- [X] T010 Add `--lang` to the eval runner in `src/eval/run.py` so scoring runs against one pack's set and writes JSON + Markdown reports to `data/eval/<lang>/reports/` per pack (no blended headline figure)
  - CHECKPOINT: STOP → report `--lang c` run reproducing 001 figures → wait for explicit approval before T011. **Foundation ready — user story implementation can now begin (after 001 T018+ is complete).**

---

## Phase 3: User Story 1 - Select language, ask in its corpus (Priority: P1) ✅ MVP

**Goal**: Sidebar language selection (C default) scopes the Q&A view to that pack; answers cite only that pack's sources.

**Independent Test**: Select each ready language, ask an in-corpus question, confirm the Persian answer's citations all resolve inside that pack's `chunks.jsonl`.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T011 [P] [US1] Contract test for `GET /api/languages` in `tests/contract/test_languages.py` (4 packs, correct statuses, `default == "c"`)
  - CHECKPOINT: STOP → report test run showing FAIL → wait for explicit approval before T012.
- [ ] T012 [P] [US1] Contract test for scoped-answer citations in `tests/contract/test_scoped_citations.py` (per ready language: answer citations all resolve inside that pack's index, cited ⊆ retrieved)
  - CHECKPOINT: STOP → report test run showing FAIL → wait for explicit approval before T013.

### Implementation for User Story 1

- [ ] T013 [US1] Build the dashboard sidebar in `src/web/templates/index.html` (persistent RTL language list from `GET /api/languages`, C preselected, ready/empty states shown) with view-state reset on switch (depends on T011, T012 passing after implementation)
  - CHECKPOINT: STOP → report rendered sidebar → wait for explicit approval before T014.
- [ ] T014 [US1] Wire language-scoped retrieval in `src/web/app.py` (per-pack `Retriever` instances from the registry keyed by `language_id`, selected pack opened only) reusing the 001 composer/answer path
  - CHECKPOINT: STOP → report scoped answers per language → wait for explicit approval before T015.
- [ ] T015 [US1] Integration test for select-and-ask per language in `tests/integration/test_scoped_ask_flow.py` (each ready pack: select → in-corpus question → pack-internal citations)
  - CHECKPOINT: STOP → report test run passing → wait for explicit approval before T015b.
- [ ] T015b [US1] Presentation-grade dashboard styling: new `src/web/static/dashboard.css` (RTL polish, project header, styled language sidebar with active-pack state and ready/empty badges, responsive single column, footer with per-pack corpus snapshot info) linked from `src/web/templates/index.html`; no backend changes, no new dependencies
  - CHECKPOINT: STOP → report styled dashboard (screenshot or HTML dump) → wait for explicit approval before T015c.
- [ ] T015c [US1] Welcome pane + demo sample questions in `src/web/templates/index.html` and `src/web/static/app.js` (Persian welcome text explaining grounded answers/citations, 3 curated sample questions per ready language as clickable chips that fill AND submit the question for one-click live-demo flow — intentional, documented exception to the no-auto-submit rule, which applies to abstention topics only)
  - CHECKPOINT: STOP → report welcome/demo flow (sample click → full answer) → wait for explicit approval before T015d.
- [ ] T015d [US1] Dashboard states polish in `src/web/templates/index.html` and `src/web/static/app.js` (loading indicator during ask, explicit "corpus not available" empty-pack state per contracts/languages-api.md, friendly Persian error display for 422/500 — all RTL-consistent)
  - CHECKPOINT: STOP → report each state rendering → wait for explicit approval before T016. **Checkpoint: User Story 1 fully functional and testable independently.**

---

## Phase 4: User Story 2 - Groundedness guarantees hold per language (Priority: P1)

**Goal**: Cross-language contamination is impossible by construction and proven by tests: B-only questions under A abstain with zero foreign citations.

**Independent Test**: Ask questions answerable only in another pack's corpus under each pack and confirm abstention with zero foreign citations.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T016 [P] [US2] Contamination contract test in `tests/contract/test_no_cross_language_citations.py` (B-only questions under pack A → `type: abstain`, citations == [], no chunk_id from any other pack)
  - CHECKPOINT: STOP → report test run showing FAIL → wait for explicit approval before T017.

### Implementation for User Story 2

- [ ] T017 [US2] Enforce pack-scoped citation validation in the answer path in `src/web/app.py` (every cited chunk_id MUST exist in the selected pack's index; any foreign id → abstain instead of answering, treated as fabrication)
  - CHECKPOINT: STOP → report enforcement probing (foreign-id injection → abstain) → wait for explicit approval before T018.
- [ ] T018 [US2] Integration test for wrong-language questions in `tests/integration/test_contamination_flow.py` (each pack asked another pack's questions → abstain, Persian redirect, zero citations)
  - CHECKPOINT: STOP → report test run passing → wait for explicit approval before T019. **Checkpoint: User Stories 1 AND 2 both work independently.**

---

## Phase 5: User Story 3 - Evaluator verifies each language separately (Priority: P2)

**Goal**: Per-language ~30-item eval sets (20/5/5) with per-language hit-rate/precision/abstention reports; contamination slice included.

**Independent Test**: Run the scorer per language and confirm per-language JSON + Markdown reports with all four metric groups.

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T019 [P] [US3] Unit tests for per-language scoring in `tests/unit/test_lang_scoring.py` (per-pack metrics, contamination slice, empty-pack handling)
  - CHECKPOINT: STOP → report test run showing FAIL → wait for explicit approval before T020.

### Implementation for User Story 3

- [ ] T020 [US3] Author the C eval set in `data/eval/c/eval-set.c.v1.json` (migrate the 001 v1 set: 30 items 20/5/5, `expected_source_ids` resolving to the migrated C index chunk_ids, empty for out-of-corpus)
  - CHECKPOINT: STOP → report item counts per qtype + source-ID validity → wait for explicit approval before T021.
- [ ] T021 [US3] Author the C++ eval set in `data/eval/cpp/eval-set.cpp.v1.json` (30 items 20/5/5 against the cpp pack index)
  - CHECKPOINT: STOP → report item counts per qtype + source-ID validity → wait for explicit approval before T022.
- [ ] T022 [US3] Author the Python eval set in `data/eval/python/eval-set.python.v1.json` (30 items 20/5/5 against the python pack index; reference-only corpus noted)
  - CHECKPOINT: STOP → report item counts per qtype + source-ID validity → wait for explicit approval before T023.
- [ ] T023 [US3] Author the Java eval set in `data/eval/java/eval-set.java.v1.json` (30 items 20/5/5 against the java pack index; reference-only corpus noted)
  - CHECKPOINT: STOP → report item counts per qtype + source-ID validity → wait for explicit approval before T024.
- [ ] T024 [US3] Calibrate the abstention threshold per pack in `src/eval/calibrate.py` (run per-pack analysis on its eval set, record each pack's threshold value + rationale in pack config, replacing T009 provisional values)
  - CHECKPOINT: STOP → report four threshold values + evidence → wait for explicit approval before T025.
- [ ] T025 [US3] Run all four per-language evals and file reports in `data/eval/<lang>/reports/` (hit-rate@5, citation precision, abstention correctness, mixed slice, contamination slice — no blended headline)
  - CHECKPOINT: STOP → report four metric summaries → wait for explicit approval before T026. **Checkpoint: full per-language evaluation loop independently runnable.**

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Prove migration safety and examiner-ready reproduction

- [ ] T026 Re-run the C-pack eval and diff against pre-migration 001 figures in `docs/MIGRATION-RESULTS.md` (SC-004: migration changed nothing; any delta investigated and explained)
  - CHECKPOINT: STOP → report diff result → wait for explicit approval before T027.
- [ ] T027 Run full `quickstart.md` validation end-to-end for all four packs (fresh per-pack index rebuilds, dashboard probes for answer/abstain/clarify/unavailable per language, `pytest tests/`, per-language eval runs) and document examiner reproduction in `README.md`
  - CHECKPOINT: STOP → report full validation log → wait for explicit approval. **All work complete.**

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Pack migration + `--lang` flags — can start immediately, independent of finishing 001.
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories. Corpora tasks T004/T005/T006 touch different `data/corpus/<lang>/` trees and may run in any order once T001–T003 are done.
- **User Stories (Phases 3–5)**: All depend on Foundational completion **AND** on 001's answer path (T018+) being complete, since 002 routes through the same composer/endpoint.
  - Recommended order: US1 → US2 → US3 (priority order), strictly sequential with per-task approvals.
- **Polish (Phase 6)**: Depends on all user stories complete.

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational + 001 T018+ — no dependencies on other 002 stories.
- **User Story 2 (P1)**: Starts after Foundational + 001 T018+ — reuses US1 routing, independently testable via contamination contract.
- **User Story 3 (P2)**: Starts after Foundational — consumes the full pipeline per pack.

### Within Each User Story

- Tests MUST be written and FAIL before implementation (T011/T012, T016, T019).
- Story checkpoint validates independence before the next story begins.

### Parallel Opportunities

- [P] tasks touching different files with no mutual dependency: T011+T012, T016, T019 (test tasks); corpora builds T004/T005/T006 (different pack directories, any order after T001–T003).
- Recommended execution is strictly sequential task-by-task with approvals; [P] markers indicate what *could* be batched only if the user explicitly waives per-task checkpoints for that pair.

---

## Parallel Example: User Story 1

```bash
# Tests for User Story 1 (both [P], different files — write together, confirm both FAIL):
Task: "Contract test for GET /api/languages in tests/contract/test_languages.py"
Task: "Contract test for scoped-answer citations in tests/contract/test_scoped_citations.py"
```

## Parallel Example: Foundational corpora

```bash
# After T001–T003, these touch different pack directories (any order):
Task: "Build the C++ corpus in data/corpus/cpp/"
Task: "Build the Python corpus in data/corpus/python/"
Task: "Build the Java corpus in data/corpus/java/"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T003, approving each)
2. Complete Phase 2: Foundational (T004–T010, approving each — CRITICAL, blocks all stories)
3. Confirm 001's answer path (T018+) is complete
4. Complete Phase 3: User Story 1 (T011–T015d)
5. **STOP and VALIDATE**: independently test US1 per its Independent Test
6. Demo if ready (sidebar + scoped cited answers per language)

### Incremental Delivery

1. Setup + Foundational → four packs ingested, API language-aware
2. + US1 → scoped Persian answers per language (MVP)
3. + US2 → proven isolation (thesis-critical)
4. + US3 → per-language evidence
5. + Polish → migration safety + examiner-ready reproduction

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Per-task CHECKPOINT lines implement the user's mandatory STOP → report → wait-for-approval protocol; the next task is blocked until approval
- Approval keyword: «تایید» or "approved Txxx"
- Commit after each approved task
- Task IDs restart per feature file (001 has its own T001–T033; these T001–T027 belong to 002)
- Avoid: vague tasks, same-file conflicts, cross-story dependencies that break independence
