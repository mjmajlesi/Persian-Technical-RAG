# Implementation Plan: Grounded Persian C Q&A

**Branch**: `001-persian-c-qa` | **Date**: 2026-09-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-persian-c-qa/spec.md`

## Summary

Build a bounded, single-user Persian RAG demo: a fixed-snapshot C corpus
(owner Persian Markdown notes + named cppreference C sections + named glibc
chapters) is ingested into chunks with source/section metadata; a Persian
question is embedded and matched against the chunk index; a Persian answer is
generated strictly from retrieved chunks with per-claim citations (click reveals
source title + section + chunk text); insufficient context yields a Persian
abstention naming the closest available topics. A versioned 30-question
evaluation set (20/5/5) measures retrieval hit-rate, citation precision, and
abstention correctness. Approach: plain-Python RAG pipeline (no agent
framework), mainstream embedding + local vector index + pluggable LLM, minimal
web UI — see research.md for decisions.

## Technical Context

**Language/Version**: Python 3.11 (pinned via `requirements.txt`; reproducible,
mainstream for RAG work).

**Primary Dependencies**: `sentence-transformers` (multilingual-e5-large
embeddings), `faiss-cpu` (local vector index), `fastapi` + `uvicorn` (demo web
API/UI host), `pydantic` (schema validation). LLM access via a thin provider
interface with one concrete API-backed implementation (provider key via env)
and documented local-model alternative. No agent/RAG framework (plain pipeline
per bounded-complexity principle).

**Storage**: Files on disk — `data/corpus/` (frozen sources + manifest),
`data/index/` (FAISS index + chunk metadata JSONL), `data/eval/` (versioned
question set + run reports). No database server (single-user demo). The
`data/corpus/` snapshot is populated in two stages: an initial dev-fixture
subset (small samples, used to validate the pipeline during Setup/Foundational
phases) is later replaced by the full frozen snapshot — all completed chapters
of the owner's Persian C notes plus the named cppreference/glibc sections per
spec.md's corpus scope — before the evaluation set (FR-007) is authored, since
eval items require real, resolvable chunk IDs.

**Testing**: `pytest` — contract tests (citation traceability), integration
tests (ingest → ask → eval), eval-set scoring script with JSON report.

**Target Platform**: Local machine / laptop demo (Windows/Linux); browser UI
with correct RTL + mixed Persian/English bidirectional rendering.

**Project Type**: Web application, minimal: Python backend + single-page demo UI.

**Performance Goals**: Interactive demo latency — p95 ask-to-answer under 30 s
on a laptop (local embedding + index lookup + one LLM call); ingest of the
bounded corpus completes in minutes.

**Constraints**: Offline-capable except for the LLM call (if API provider
chosen); all dependencies pinned; one-command ingest and one-command eval;
cppreference CC-BY-SA attribution preserved in manifest and UI.

**Scale/Scope**: Bounded prototype — one frozen corpus snapshot (full owner
notes + named reference subsets), ~30-question eval set, single concurrent
user. No auth, no multi-tenancy, no scaling work.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Groundedness over Fluency | PASS | FR-003/FR-005: generation constrained to retrieved chunks; abstention path is a first-class flow with eval coverage (SC-003). |
| II. Citation Accuracy | PASS | FR-004: per-claim citations to real chunk IDs; click reveals title + section + chunk text; contract tests enforce traceability. |
| III. Bounded Complexity | PASS | Plain chunk → embed → FAISS → LLM pipeline; no agents, no custom-trained rankers; mainstream pinned libs only. |
| IV. Persian-First Quality | PASS | Multilingual embedding validated on Persian; mixed-language eval subset (5 Qs); RTL/bidi UI requirement; Persian-only generation + abstention. |
| V. Evaluability | PASS | Versioned 30-Q set (20/5/5) + scripted hit-rate / citation-precision / abstention report (FR-007, SC-002). |
| VI. Reproducibility | PASS | One-command ingest/eval, pinned deps, frozen corpus manifest, quickstart.md reproduction path (SC-005). |
| VII. Honest Scope | PASS | Single-user demo, frozen subset corpus, explicit non-goals honored; no auth/scaling/streaming work planned. |

Post-design re-check: no new components introduced beyond the pipeline above;
no violations. Complexity Tracking: none required.

## Project Structure

### Documentation (this feature)

```text
specs/001-persian-c-qa/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── ask-api.md       # POST /api/ask + citation payload contract
│   └── eval-set-schema.md  # Versioned evaluation set + report schema
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── ingest/          # corpus loading, chunking, manifest writing
├── index/           # embedding + FAISS build/query
├── qa/              # retrieval orchestration, prompting, abstention logic
├── eval/            # eval-set runner + scoring/report
└── web/             # FastAPI app + single-page demo UI (RTL/bidi)

data/
├── corpus/          # frozen snapshot + manifest.json (provenance, licenses)
├── index/           # faiss.index + chunks.jsonl (chunk_id, source, section, text)
└── eval/            # eval-set v1 (questions, expected sources/answers) + reports/

tests/
├── contract/        # citation traceability, API schema conformance
├── integration/     # ingest → ask → cite; out-of-corpus → abstain
└── unit/            # chunking, scoring helpers
```

**Structure Decision**: Single Python project with a minimal web front (no
frontend/backend split — one FastAPI app serves API + demo page). `data/`
holds only frozen, versioned artifacts so an examiner can reproduce ingest and
eval from scratch.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations — table intentionally empty.
