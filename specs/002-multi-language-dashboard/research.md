# Research: Multi-Language Dashboard

**Date**: 2026-10-07 | **Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

No NEEDS CLARIFICATION remained (all resolved during specify + constitution
amendment). Decisions below reuse everything proven in feature 001 (T001–T016).

## 1. Pack layout (per-language isolation)

- **Decision**: `data/corpus/<lang>/` sources + `data/corpus/manifest.<lang>.json`
  + `data/index/<lang>/` (`faiss.index`, `ids.json`, `chunks.jsonl`) +
  `data/eval/<lang>/` (set + reports). Language ids: `c`, `cpp`, `python`,
  `java`. Ingest/index/eval CLIs gain a required `--lang` flag selecting the
  pack; `Retriever` is instantiated per selected language (one instance per
  pack, held in a registry keyed by language id).
- **Rationale**: Principle VIII mandates isolation by construction; separate
  directories make SC-004 (add a language without touching others) trivially
  true and keep every 001 module untouched.
- **Alternatives considered**: shared index + language-tag filter (rejected:
  prohibited by Principle VIII; a forgotten filter is a silent fabrication
  risk); per-language git branches (rejected: versioning is data, not code).

## 2. C-pack migration (001 → 002)

- **Decision**: Move the current `data/corpus/manifest.json` →
  `data/corpus/manifest.c.json` (origins rewritten to `data/corpus/c/`),
  move `data/corpus/full/*` → `data/corpus/c/`, move `data/index/*` →
  `data/index/c/`. 001's dev fixtures under `data/corpus/samples/` stay
  shared. 001 docs keep working with `--lang c` defaults.
- **Rationale**: Zero re-ingest cost; the validated 503-chunk C snapshot
  becomes pack v1 verbatim.
- **Alternatives considered**: re-ingesting C from scratch (rejected: wasteful,
  risks snapshot drift vs the validated index).

## 3. New corpora (cpp / python / java)

- **Decision**: Same bounded T010b method — named page subsets, stdlib-only
  HTML→text fetch, local freeze with URL/date/license headers:
  - `cpp`: the on-disk `c-notes-ch09-cpp-intro.md` (moved to `data/corpus/cpp/`)
    + ~10–15 cppreference **C++** pages (e.g. vector, string, iostream, class —
    exact list chosen at task time, same cleaning rules as T010b).
  - `python`: English-reference-only — named subset of docs.python.org
    (tutorial + library sections matching student-level questions).
  - `java`: English-reference-only — named subset of the official Java docs
    (language basics + core library). Exact page lists are fixed at task time
    and frozen in each pack manifest with provenance + license notes.
- **Rationale**: Reuses the proven fetch/clean/freeze pipeline; keeps each
  pack in the hundreds-of-chunks band; FR-007 tradeoff documented per pack.
- **Alternatives considered**: Persian notes for Python/Java (rejected by
  owner: not needed, docs are strong); unbounded crawling (rejected:
  Principle VII).

## 4. API routing

- **Decision**: `POST /api/ask` gains a `language` field (default `"c"`,
  preserving all 001 behavior); unknown language → 422 with a Persian error;
  listed-but-empty pack (no index) → explicit `"corpus not available"` state,
  never silent failure. New `GET /api/languages` returns pack descriptors
  (id, display name, status ready/empty, corpus snapshot date, eval version)
  read live from the manifests.
- **Rationale**: Default keeps 001 contract tests green; registry-from-manifest
  means adding a language is data-only (SC-004).
- **Alternatives considered**: separate endpoint per language (rejected:
  endpoint sprawl, same handler anyway).

## 5. Dashboard UI

- **Decision**: Persistent RTL sidebar listing the four packs (C preselected,
  FR-001); selecting a pack opens/scopes the existing Q&A view to it and
  clears cross-language view state (no mixed history); citation click-reveal
  and abstention rendering reused unchanged from 001.
- **Rationale**: Minimal addition honoring honest scope; sidebar persistence
  satisfies the "always visible selection" edge case.
- **Alternatives considered**: separate page per language (rejected: duplicated
  UI, same view logic).

## 6. Evaluation per language

- **Decision**: `src/eval/run.py` gains `--lang`; each pack gets its own
  ~30-item set in the 20/5/5 shape (in-corpus / mixed / out-of-corpus) with
  expected source ids from its own index; reports land in
  `data/eval/<lang>/reports/`. US2 gets a dedicated contamination probe set:
  questions answerable only in pack B asked under pack A must abstain with
  zero foreign citations.
- **Rationale**: Direct implementation of SC-002/SC-003 and Principle V's
  per-language reporting rule.
- **Alternatives considered**: one blended multilingual set (rejected: hides
  weak languages, prohibited by Principle V).

## 7. Abstention thresholds per pack

- **Decision**: The similarity threshold (T014/T024 mechanism) is calibrated
  **per pack** on its own eval set and stored in pack config, since score
  distributions differ across corpora (proven by the T014 0.737/0.866 finding).
- **Rationale**: A single global threshold would over/under-abstain per
  language; per-pack calibration is the same method, run four times.
