<!--
Sync Impact Report
- Version change: 1.0.0 -> 1.1.0 (MINOR: new principle + materially expanded scope guidance; no removals or redefinitions)
- Modified principles: VII. Honest Scope (C-only corpus -> per-language LanguagePacks for C/C++/Python/Java; prototype constraint retained)
- Added principles: VIII. Per-Language Isolation (separate index per language; cross-language citations prohibited; per-language evaluation)
- Modified sections: Technology Preferences & Constraints (corpus bullet -> per-language packs with stated composition rule)
- Removed sections: none
- Follow-up TODOs: none; feature 002 spec (specs/002-multi-language-dashboard/spec.md) is the normative detail source
-->

# Persian Technical RAG Constitution

## Core Principles

### I. Groundedness over Fluency (NON-NEGOTIABLE)

Every answer MUST be traceable to retrieved source chunks. The system MUST NOT
answer from the model's parametric knowledge alone. When retrieved context is
insufficient to answer confidently, the system MUST explicitly state the gap
rather than fabricate an answer.

Rationale: for a graduation thesis claiming retrieval-augmented generation,
ungrounded fluency invalidates the core contribution and risks examiner failure.

### II. Citation Accuracy (NON-NEGOTIABLE)

Every factual claim in a generated answer MUST be attributable to a specific
retrieved source/chunk. Citations MUST reference real, verifiable source
locations (document ID, chunk ID, or page/section) that exist in the ingested
corpus. Fabricated orapproximate citations are prohibited.

Rationale: citations are the only verifiable evidence of groundedness; inaccurate
citations are equivalent to hallucination.

### III. Bounded Complexity

The system MUST use a simple, well-understood RAG architecture: standard
chunking + embedding + vector retrieval + LLM generation. Exotic or highly
experimental pipelines (e.g. custom agents, complex multi-hop orchestration,
learned re-rankers trained from scratch) MUST NOT be introduced without a
written justification and an evaluability plan. Proven, mainstream libraries
and patterns take precedence over custom low-level implementations.

Rationale: the project MUST stay completable within a ~3-month graduation
timeline while remaining demonstrable end-to-end.

### IV. Persian-First Quality

Retrieval and generation quality for Persian-language queries and answers is a
first-class requirement, not an afterthought. The system MUST handle mixed
Persian/English technical terminology (code identifiers, framework names,
error strings) commonly appearing in Persian technical text. Tokenization,
chunking, embedding selection, prompting, and evaluation MUST all be validated
against Persian content.

Rationale: generic English-tuned RAG defaults degrade on Persian morphology
and code-mixed text; without explicit attention the project fails its stated purpose.

### V. Evaluability

The system MUST include a way to measure retrieval quality and answer quality:
a small, versioned evaluation question set with expected sources/answers, plus
scriptable scoring (e.g. retrieval hit-rate/recall, citation precision, groundedness
checks). Design decisions and improvements MUST be justified with evaluation
evidence rather than intuition. Where multiple languages are supported, quality
MUST be measured and reported per language, never only as a blended score.

Rationale: without measurement, iteration is anecdote; a thesis requires evidence.

### VI. Reproducibility and Clarity

Setup, data ingestion, and evaluation MUST be scriptable and documented well
enough that another developer or examiner can reproduce results without
undocumented manual steps. This includes pinned dependencies, documented corpus
provenance, one-command ingest/eval scripts, and README instructions.

Rationale: a graduation project is examined by reproduction; portfolio value
depends on another engineer being able to run it.

### VII. Honest Scope

The system is a focused prototype/demo, NOT a production-scale product. Each
supported programming language is a bounded LanguagePack: launch set is C,
C++, Python, and Java, each with an explicitly stated, frozen corpus snapshot
(C/C++ reuse the owner-authored Persian notes plus English references;
Python/Java use English reference corpora only, per the accepted and
documented tradeoff that they need no exam-style Persian terminology).
Adding a language means adding its pack (corpus + eval set) without changing
existing packs. Scope creep into multi-tenant deployment, authentication,
horizontal scaling, or unbounded/arbitrary corpora is prohibited unless this
constitution is amended.

Rationale: honest, bounded scope is what makes the project defensible and
completable as a bachelor's thesis and portfolio piece.

### VIII. Per-Language Isolation (NON-NEGOTIABLE)

Retrieval and generation for a selected language MUST use only that
language's index and corpus. Cross-language retrieval or citation (answering
from another language's sources) is prohibited and treated as fabrication
under Principles I and II. The default implementation is a separate index per
language, so isolation holds by construction rather than by filter discipline.

Rationale: a shared-index leak would silently violate groundedness while
looking correct; physical isolation makes the guarantee reviewable by an
examiner.

## Technology Preferences & Constraints

Technology choices MUST favor widely-used, well-documented, industry-relevant
tools over obscure or purely academic ones, so the project stands as a portfolio
piece demonstrating current AI engineering practice.

- Standard RAG stack (mainstream vector store, mainstream embedding provider or
  open model, mainstream LLM API or local LLM) is REQUIRED; custom embedding
  models or LLMs built from scratch are explicitly out of scope.
- All dependencies MUST be pinned and installable via script.
- Corpus MUST be organized as per-language packs (LanguagePack per supported
  programming language), each curated, bounded, frozen, and with recorded
  provenance and licensing notes.

## Non-Goals and Scope Boundaries

The following are explicitly out of scope and MUST NOT be pursued under this
constitution:

- Real-time/streaming ingestion of new sources.
- Multi-user or production deployment concerns (auth, multi-tenancy, scaling).
- Support for languages other than Persian (English terms embedded in Persian
  text excepted). Note: this concerns the query/answer/UI language, not the
  programming languages covered — those are governed by Principle VII.
- Building a custom embedding model or LLM from scratch.

Any proposal touching these items MUST be rejected or require a constitution
amendment with explicit scope renegotiation.

## Development Workflow and Quality Gates

- Every spec and implementation MUST state which principle(s) it serves and how
  compliance will be checked.
- Changes that weaken groundedness, citation accuracy, Persian quality, or
  reproducibility MUST be rejected in review.
- Evaluation MUST be re-run before claiming any retrieval/generation improvement.
- Documentation (setup, ingest, eval) MUST be updated in the same change that
  alters the corresponding behavior; undocumented manual steps are defects.

## Governance

This constitution supersedes all other practices, templates, and implementation
preferences for Persian Technical RAG.

- Amendments REQUIRE: a written proposal, bumped version per policy below, and
  a migration/impact note for in-flight specs.
- Versioning policy (semantic): MAJOR for backward-incompatible removals or
  redefinitions of principles; MINOR for new principles or materially expanded
  guidance; PATCH for clarifications, wording, or typo fixes.
- Compliance review: all specs, plans, and reviews MUST verify constitution
  compliance; complexity beyond the bounded RAG pipeline MUST be explicitly
  justified against Principles III and VII.
- Runtime guidance: dependent templates and commands read this file at runtime;
  this document itself is the sole governance source — templates are not edited here.

**Version**: 1.1.0 | **Ratified**: 2026-09-19 | **Last Amended**: 2026-10-07
