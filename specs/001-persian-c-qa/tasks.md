# Tasks: Grounded Persian C Q&A

**Input**: Design documents from `/specs/001-persian-c-qa/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Included — plan.md/quickstart.md define pytest contract + integration tests and a scripted eval runner; each test task states the required FAIL-first behavior.

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

- **Single project**: `src/`, `tests/` at repository root (per plan.md — one FastAPI app serves API + demo page)
- Corpus/index/eval artifacts: `data/corpus/`, `data/index/`, `data/eval/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project directory skeleton per plan.md (src/ingest, src/index, src/qa, src/eval, src/web, data/corpus, data/index, data/eval, data/eval/reports, tests/contract, tests/integration, tests/unit) with empty `__init__.py` files
  - CHECKPOINT: STOP → report created tree → wait for explicit approval before T002.
- [X] T002 Create pinned Python dependencies in requirements.txt (python 3.11 target: sentence-transformers, faiss-cpu, fastapi, uvicorn, pydantic, pytest) with exact pinned versions that install cleanly
  - CHECKPOINT: STOP → report `pip install -r requirements.txt` result → wait for explicit approval before T003.
- [X] T003 [P] Write corpus manifest skeleton in data/corpus/manifest.json with one sample entry per kind (persian-notes, cppreference, glibc) carrying all CorpusSource fields from data-model.md (source_id unique lowercase-hyphenated, title non-empty, kind enum, origin non-empty, snapshot date YYYY-MM-DD, license non-empty, CC-BY-SA-3.0 on the cppreference entry)
  - CHECKPOINT: STOP → report manifest content → wait for explicit approval before T004.
- [X] T004 [P] Add three dev fixture sources in data/corpus/samples/ (one small Persian Markdown note with headings + code block, one cppreference C excerpt with section heading, one glibc excerpt with section heading) referenced only for development, not the frozen snapshot
  - CHECKPOINT: STOP → report fixture files → wait for explicit approval before T005.
- [X] T005 [P] Configure pytest in pytest.ini (or pyproject) with testpaths tests/ and add passing smoke test in tests/unit/test_smoke.py asserting the src/ package imports
  - CHECKPOINT: STOP → report `pytest tests/unit/test_smoke.py` result → wait for explicit approval before T006.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core pipeline that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Implement section-aware chunker in src/ingest/chunker.py splitting on Markdown headings/reference sections, target ~512 tokens with ~64-token overlap, never splitting mid-code-block, emitting fields (chunk_id deterministic source+section+ordinal, source_id, doc_title, section_heading non-empty, text non-empty, lang enum fa|en|mixed)
  - CHECKPOINT: STOP → report chunker behavior on fixtures + unit run → wait for explicit approval before T007.
- [X] T007 [P] Implement chunk writer + JSONL schema validation in src/ingest/writer.py writing data/index/chunks.jsonl with chunk_id uniqueness enforced and every source_id existing in data/corpus/manifest.json
  - CHECKPOINT: STOP → report writer validation behavior → wait for explicit approval before T008.
- [X] T008 Implement embedding module in src/index/embed.py using intfloat/multilingual-e5-large via sentence-transformers with query/passage prefixes per model card
  - CHECKPOINT: STOP → report embed smoke output dims on a Persian + an English sample → wait for explicit approval before T009.
- [X] T009 Implement FAISS index build/query module in src/index/faiss_store.py (build from chunk embeddings, persist to data/index/faiss.index, query returning top-k chunk_ids with scores)
  - CHECKPOINT: STOP → report build+query round-trip on fixtures → wait for explicit approval before T010.
- [X] T010 Wire ingest CLI in src/ingest/__main__.py and index build in src/index/__main__.py so `python -m src.ingest --manifest data/corpus/manifest.json` then `python -m src.index build --manifest data/corpus/manifest.json` produce data/index/faiss.index + data/index/chunks.jsonl and print chunk count and per-source counts
  - CHECKPOINT: STOP → report CLI run output on fixtures → wait for explicit approval before T010b.
- [X] T010b Populate data/corpus/full/ with the real, complete corpus — all finished chapters of the owner's Persian C study notes plus the real selected cppreference and glibc pages per the spec's corpus scope — replace the skeleton data/corpus/manifest.json with the frozen snapshot entries (real origins, snapshot dates, licenses), and run the real ingest + index build (`python -m src.ingest` then `python -m src.index build`) replacing the dev-fixture-only index (depends on T010; blocks T011 and T030). Do NOT invent corpus content: request any missing note files or page selections from the user before starting.
  - CHECKPOINT: STOP → report corpus inventory (source list + chunk counts per source) → wait for explicit approval before T011.
- [ ] T011 Implement LLM provider interface in src/qa/provider.py (`generate(prompt, context) -> text`, provider key read from LLM_API_KEY env, model id from config) with one concrete API-backed provider
  - CHECKPOINT: STOP → report interface + provider wiring (no real call needed) → wait for explicit approval before T012.
- [ ] T012 Implement top-k retrieval orchestration in src/qa/retriever.py (embed question, FAISS top-k default 5, return chunk_ids with scores)
  - CHECKPOINT: STOP → report retrieval on a sample Persian question → wait for explicit approval before T013.
- [ ] T013 Implement grounded prompt builder + answer composer in src/qa/answer.py (Persian-only instruction, per-claim chunk-ID citations, cited IDs must be a subset of retrieved IDs)
  - CHECKPOINT: STOP → report prompt template + subset rule enforcement → wait for explicit approval before T014.
- [ ] T014 Implement abstention module in src/qa/abstain.py (similarity-threshold check + LLM-insufficiency signal → AbstentionResponse with fixed-form Persian message, 1–3 suggested_topics each existing in the corpus, citations always empty)
  - CHECKPOINT: STOP → report abstention trigger logic → wait for explicit approval before T015.
- [ ] T015 Create FastAPI app skeleton in src/web/app.py with POST /api/ask request validation per contracts/ask-api.md (question required non-empty after trim, top_k optional integer 1–10 default 5, empty question → 422 with Persian error message)
  - CHECKPOINT: STOP → report skeleton + validation behavior → wait for explicit approval before T016. **Foundation ready — user story implementation can now begin.**

---

## Phase 3: User Story 1 - Ask in Persian, get cited answer (Priority: P1) ✅ MVP

**Goal**: Student submits a Persian C question and receives a Persian answer with verifiable per-claim citations; clicking a citation reveals source title + section heading + full chunk text.

**Independent Test**: Submit an in-corpus Persian question; answer is Persian, has ≥1 citation, every chunk_id resolves in the active index and was among retrieved IDs.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T016 [P] [US1] Contract test for citation traceability in tests/contract/test_citations.py (answer type has ≥1 citation; every chunk_id exists in data/index/chunks.jsonl; cited IDs ⊆ retrieved_chunk_ids; excerpt equals stored chunk text)
  - CHECKPOINT: STOP → report test run showing FAIL (no implementation yet) → wait for explicit approval before T017.
- [ ] T017 [P] [US1] Integration test for ingest→ask→cite journey in tests/integration/test_answer_flow.py (ingest fixtures, ask an in-corpus question, assert Persian answer with traceable citation)
  - CHECKPOINT: STOP → report test run showing FAIL → wait for explicit approval before T018.

### Implementation for User Story 1

- [ ] T018 [US1] Wire answer path into POST /api/ask in src/web/app.py (retriever → answer composer → response shape `type: answer` per contracts/ask-api.md) (depends on T016, T017 passing after implementation)
  - CHECKPOINT: STOP → report endpoint response on a fixture question → wait for explicit approval before T019.
- [ ] T019 [US1] Build demo answer pane in src/web/templates/index.html (or inline page) showing Persian answer with citation chips carrying doc_title + section_heading
  - CHECKPOINT: STOP → report rendered pane (screenshot or HTML dump) → wait for explicit approval before T020.
- [ ] T020 [US1] Implement citation click-reveal in src/web/static/app.js (click shows source title + section heading + full chunk excerpt in place, per clarification decision)
  - CHECKPOINT: STOP → report click behavior → wait for explicit approval before T021. **Checkpoint: User Story 1 fully functional and testable independently.**

---

## Phase 4: User Story 2 - Clear abstention when context is insufficient (Priority: P1)

**Goal**: Out-of-corpus or unsupported questions return a Persian abstention naming the closest available topics, with zero citations and zero fabricated claims.

**Independent Test**: Submit an out-of-corpus question; response is `type: abstain` with Persian message, 1–3 real suggested topics, and empty citations.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T021 [P] [US2] Contract test for abstention purity in tests/contract/test_abstention.py (abstain type, citations == [], every suggested_topic exists in corpus manifest/sections)
  - CHECKPOINT: STOP → report test run showing FAIL → wait for explicit approval before T022.
- [ ] T022 [P] [US2] Integration test for out-of-corpus→abstain journey in tests/integration/test_abstain_flow.py (irrelevant-question input yields abstain, no factual claims)
  - CHECKPOINT: STOP → report test run showing FAIL → wait for explicit approval before T023.

### Implementation for User Story 2

- [ ] T023 [US2] Wire abstention path into POST /api/ask in src/web/app.py using src/qa/abstain.py (threshold + insufficiency signal → `type: abstain` shape per contracts/ask-api.md)
  - CHECKPOINT: STOP → report abstain response on an out-of-domain probe → wait for explicit approval before T024.
- [ ] T024 [US2] Calibrate similarity threshold on fixtures in src/eval/calibrate.py (or documented script) recording the chosen threshold value and its rationale in the file header
  - CHECKPOINT: STOP → report threshold value + calibration evidence → wait for explicit approval before T025.
- [ ] T025 [US2] Render abstention state in the demo UI in src/web/templates/index.html (Persian redirect message + clickable suggested topics, no citation chips)
  - CHECKPOINT: STOP → report rendered abstain state → wait for explicit approval before T026. **Checkpoint: User Stories 1 AND 2 both work independently.**

---

## Phase 5: User Story 3 - Mixed Persian/English technical queries (Priority: P2)

**Goal**: Persian questions embedding English identifiers (function/library names, error text) are understood correctly and answered to the same citation/groundedness bar.

**Independent Test**: Submit Persian questions containing English identifiers (e.g. `malloc`); answers meet the same citation standards as pure-Persian queries and Latin terms render correctly (bidi).

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T026 [P] [US3] Integration test for mixed-language queries in tests/integration/test_mixed_flow.py (Persian+`malloc`-style probes → grounded cited answers; identifiers preserved verbatim, not translated)
  - CHECKPOINT: STOP → report test run showing FAIL → wait for explicit approval before T027.

### Implementation for User Story 3

- [ ] T027 [US3] Add mixed-query handling in src/qa/retriever.py + src/qa/answer.py (Latin identifiers preserved verbatim into retrieval and prompt; lang_hint fa|mixed detected and logged)
  - CHECKPOINT: STOP → report mixed-query answer vs pure-Persian parity → wait for explicit approval before T028.
- [ ] T028 [US3] Apply bidi-safe rendering in src/web/templates/index.html (RTL layout with `dir="auto"` on mixed-language spans so English identifiers display correctly inside Persian text)
  - CHECKPOINT: STOP → report rendering check → wait for explicit approval before T029. **Checkpoint: all question-answering stories independently functional.**

---

## Phase 6: User Story 4 - Evaluator verifies quality objectively (Priority: P2)

**Goal**: A versioned 30-question eval set (20 in-corpus / 5 mixed / 5 out-of-corpus) with a one-command scorer reporting hit-rate@5, citation precision, abstention correctness, and the mixed slice.

**Independent Test**: Run the scorer on the frozen set; JSON + Markdown report with all four metrics is produced under data/eval/reports/.

### Tests for User Story 4

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T029 [P] [US4] Unit tests for scoring helpers in tests/unit/test_scoring.py (hit_rate_at_5, citation_precision, abstention_correct, mixed slice — including empty-expected-sources and phantom-citation edge cases)
  - CHECKPOINT: STOP → report test run showing FAIL → wait for explicit approval before T030.

### Implementation for User Story 4

- [ ] T030 [US4] Author versioned eval set in data/eval/eval-set.v1.json (30 items in 20/5/5 split per contracts/eval-set-schema.md: item_id, Persian question, qtype enum, expected_source_ids resolving to real chunk_ids — empty for out-of-corpus, expected_answer_summary one-line Persian gist) (depends on T010b — expected_source_ids must resolve to chunk_ids from the real T010b index, not fixtures)
  - CHECKPOINT: STOP → report item counts per qtype + source-ID validity → wait for explicit approval before T031.
- [ ] T031 [US4] Implement eval runner + scorer in src/eval/run.py writing JSON + Markdown summary to data/eval/reports/ per contracts/eval-set-schema.md (hit_rate_at_5, citation_precision, abstention_correct target 5/5, mixed_slice parity)
  - CHECKPOINT: STOP → report scorer output on the v1 set → wait for explicit approval before T032.
- [ ] T032 [US4] Document examiner reproduction path in README.md (install → ingest → ask → eval commands from quickstart.md; corpus snapshot + set version recorded)
  - CHECKPOINT: STOP → report README section → wait for explicit approval before T033. **Checkpoint: full evaluation loop independently runnable.**

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final verification that the whole thesis demo holds together

- [ ] T033 Run full quickstart.md validation end-to-end (fresh data/index rebuild, demo probes for answer/abstain/clarify/mixed, pytest tests/, eval run) and fix only defects found, in docs/QUICKSTART-RESULTS.md
  - CHECKPOINT: STOP → report full validation log → wait for explicit approval. **All work complete.**

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — starts immediately. Tasks T001→T002→T003/T004/T005 (T003, T004, T005 parallel after T002).
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories. Order: T006 → T007 → T008 → T009 → T010 → T010b (real corpus + real index) → T011 → T012 → T013 → T014 → T015.
- **User Stories (Phases 3–6)**: All depend on Foundational completion; run sequentially US1 → US2 → US3 → US4 in priority order (Recommended: strictly sequential with per-task approvals, no parallel story work).
- **Polish (Phase 7)**: Depends on all user stories complete.

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational — no dependencies on other stories.
- **User Story 2 (P2)**: Starts after Foundational — reuses retriever/endpoint from US1 but independently testable via abstain contract.
- **User Story 3 (P2)**: Starts after Foundational — extends US1 components, independently testable via mixed-flow test.
- **User Story 4 (P2)**: Starts after Foundational — consumes the full pipeline; needs US1–US3 behaviors to score them.

### Within Each User Story

- Tests MUST be written and FAIL before implementation (T016/T017, T021/T022, T026, T029).
- Implementation only after its story's tests show FAIL.
- Story checkpoint validates independence before the next story begins.

### Parallel Opportunities

- [P] tasks touching different files with no mutual dependency: T003/T004/T005 (manifest, fixtures, pytest config); T016+T017, T021+T022 (contract + integration tests per story).
- Foundational chain T006→T015 is sequential (each builds on the previous module); [P] is marked only on T007 which validates schema against fixtures independently.
- Recommended execution is strictly sequential task-by-task with approvals; [P] markers indicate what *could* be batched only if the user explicitly waives per-task checkpoints for that pair.

---

## Parallel Example: User Story 1

```bash
# Tests for User Story 1 (both [P], different files — write together, confirm both FAIL):
Task: "Contract test for citation traceability in tests/contract/test_citations.py"
Task: "Integration test for ingest→ask→cite journey in tests/integration/test_answer_flow.py"
```

## Parallel Example: Setup

```bash
# After T002, these three [P] tasks touch different files:
Task: "Write corpus manifest skeleton in data/corpus/manifest.json"
Task: "Add three dev fixture sources in data/corpus/samples/"
Task: "Configure pytest with smoke test in tests/unit/test_smoke.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T005, approving each)
2. Complete Phase 2: Foundational (T006–T015, approving each — CRITICAL, blocks all stories)
3. Complete Phase 3: User Story 1 (T016–T020)
4. **STOP and VALIDATE**: independently test US1 per its Independent Test
5. Demo if ready (in-corpus Persian Q&A with click-through citations)

### Incremental Delivery

1. Setup + Foundational → pipeline ready
2. + US1 → cited Persian answers (MVP)
3. + US2 → honest abstention (thesis-critical)
4. + US3 → mixed-language parity
5. + US4 → objective evaluation evidence
6. + Polish → examiner-ready reproduction

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Per-task CHECKPOINT lines implement the user's mandatory STOP → report → wait-for-approval protocol; the next task is blocked until approval
- Approval keyword: «تایید» or "approved Txxx"
- Commit after each approved task
- Avoid: vague tasks, same-file conflicts, cross-story dependencies that break independence
