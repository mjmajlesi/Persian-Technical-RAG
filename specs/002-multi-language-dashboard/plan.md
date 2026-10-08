# Implementation Plan: Multi-Language Dashboard

**Branch**: `002-multi-language-dashboard` | **Date**: 2026-10-07 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-multi-language-dashboard/spec.md`

## Summary

Extend the single-language (C) RAG demo into a language-scoped multi-pack
system: each programming language (C, C++, Python, Java at launch) becomes a
LanguagePack with its own frozen corpus snapshot, separate FAISS index, and
versioned eval set. The dashboard gains a persistent sidebar (C preselected);
every question is answered strictly from the selected pack's index with the
same per-claim citation and abstention guarantees, and quality is measured
per language. All 001 pipeline modules (chunk → embed → index → retrieve →
answer → abstain) are reused unchanged; 002 adds pack layout, language
routing, dashboard UI, new corpora (C++ notes already on disk + English refs
for C++/Python/Java), and per-language eval.

## Technical Context

**Language/Version**: Python 3.11, same `.venv` and pinned `requirements.txt`
as feature 001 (no new dependencies; HTML fetching for new corpora reuses
the stdlib-only approach proven in T010b).

**Primary Dependencies**: Unchanged from 001 (`sentence-transformers`
multilingual-e5-large, `faiss-cpu`, `fastapi`/`uvicorn`, `pydantic`,
`pytest`) + the existing `LLMProvider` (9router/OpenAI-compatible).

**Storage**: Per-language directories (see research.md §1):
`data/corpus/<lang>/` (frozen sources), `data/corpus/manifest.<lang>.json`,
`data/index/<lang>/` (`faiss.index` + `ids.json` + `chunks.jsonl`),
`data/eval/<lang>/` (versioned set + reports). No database server.

**Testing**: `pytest` — per-pack contract tests (citation isolation),
cross-language contamination tests (B-only question under A → abstain),
per-language eval runs.

**Target Platform**: Same local laptop demo; browser UI with RTL sidebar +
correct Persian/English bidirectional rendering.

**Project Type**: Web application (single FastAPI app serves API + dashboard).

**Performance Goals**: Same interactive bar as 001 per language (p95
ask-to-answer under 30 s); four small indices instead of one changes nothing
materially (each pack is hundreds of chunks).

**Constraints**: Offline-capable except the LLM call; one-command ingest and
eval **per language**; CC-BY-SA/GFDL attributions preserved per pack;
Python/Java packs are English-reference-only (accepted, documented tradeoff).

**Scale/Scope**: Bounded prototype — 4 launch packs (C, C++, Python, Java),
one frozen snapshot + one eval set version per pack, single concurrent user.
No auth, no multi-tenancy, no scaling work.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Groundedness | PASS | Same composer/abstention path per pack; US2 contamination tests enforce it. |
| II. Citation Accuracy | PASS | Citations validated against the selected pack's index only (contract-tested). |
| III. Bounded Complexity | PASS | Zero new pipeline components: same 6 modules × 4 packs; no agents/frameworks. |
| IV. Persian-First | PASS | Persian Q&A + mixed terms unchanged; Python/Java ref-only tradeoff documented in spec FR-007 with transparent per-language eval. |
| V. Evaluability | PASS | Per-language versioned sets + per-language reports (now constitutional); no blended scores. |
| VI. Reproducibility | PASS | Per-language one-command ingest/eval; provenance manifests per pack. |
| VII. Honest Scope | PASS | Launch set fixed (4 languages); each pack bounded + frozen; still a demo. |
| VIII. Per-Language Isolation | PASS | Separate index per language (FR-006); isolation by construction, verified by contamination tests. |

Post-design re-check: no new components beyond pack layout + routing + dashboard; no violations. Complexity Tracking: none required.

**Prerequisite note**: 002 implementation requires feature 001's answer path
(T018+) complete, since 002 routes through the same composer/endpoint. 001's
C index migrates unchanged into the `c` pack (research.md §2).

## Project Structure

### Documentation (this feature)

```text
specs/002-multi-language-dashboard/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── languages-api.md    # GET /api/languages + language field on POST /api/ask
│   └── language-pack-schema.md  # per-pack manifest + directory layout
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── ingest/          # UNCHANGED (001) + --lang flag threading manifest.<lang>.json
├── index/           # UNCHANGED (001) + --lang flag threading data/index/<lang>/
├── qa/              # UNCHANGED modules + language-scoped retriever instances
├── eval/            # scorer gains --lang (per-pack sets + reports)
└── web/             # dashboard sidebar + scoped Q&A view; pack registry from manifests

data/
├── corpus/
│   ├── manifest.<lang>.json   # one frozen manifest per language
│   ├── c/ cpp/ python/ java/  # frozen sources per language
│   └── samples/               # dev fixtures (unchanged)
├── index/
│   └── <lang>/                # faiss.index + ids.json + chunks.jsonl per language
└── eval/
    └── <lang>/                # eval-set.<lang>.v1.json + reports/ per language

tests/
├── contract/        # per-pack citation isolation tests
├── integration/     # cross-language contamination tests, sidebar flows
└── unit/            # pack registry, scorer --lang helpers
```

**Structure Decision**: Extend the single Python project in place; per-language
directories (not new services) deliver Principle VIII isolation with zero
architectural novelty.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations — table intentionally empty.
