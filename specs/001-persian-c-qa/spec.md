# Feature Specification: Grounded Persian C Q&A

**Feature Branch**: `001-persian-c-qa`

**Created**: 2026-09-19

**Status**: Draft

**Input**: User description: "The system answers Persian-language technical questions about C Programming by retrieving from a curated, fixed-snapshot corpus (owner-authored Persian C study notes in Markdown + cppreference.com C pages + GNU C Library manual), via a simple web interface that returns Persian answers with verifiable citations and explicit abstention when context is insufficient."

## Clarifications

### Session 2026-09-19

- Q: How large should the versioned evaluation question set be, and how should it be split across question types? → A: Balanced set (~30 total: 20 in-corpus, 5 mixed, 5 out-of-corpus).
- Q: When a student clicks a citation, what should the interface reveal? → A: Source title + section heading + full cited chunk text.
- Q: How should the system respond to a very short or ambiguous Persian question? → A: Ask one targeted follow-up question and wait; no answer attempted until clarified.
- Q: What bound defines the fixed corpus snapshot for this release? → A: Full owner Persian notes + named subset of cppreference C sections + named glibc chapters, frozen with version/date.
- Q: In what language and form should the "cannot answer" response appear? → A: Persian sentence naming the closest available topics as a helpful redirect.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ask in Persian, get cited answer (Priority: P1)

A student types a technical C question in Persian into a simple web interface
and receives a Persian answer accompanied by verifiable citations (source
document name/title plus specific section or chunk referenced) that can be
clicked through or otherwise verified.

**Why this priority**: This is the core value proposition and the thesis claim;
without it nothing else matters.

**Independent Test**: Can be fully tested by submitting a Persian question whose
answer exists in the corpus and confirming the returned answer is in Persian and
each factual claim traces to a real ingested chunk.

**Acceptance Scenarios**:

1. **Given** the corpus is ingested and the interface is open, **When** the
   student submits a Persian C question covered by the corpus, **Then** the
   system returns a Persian answer with at least one citation traceable to a
   real chunk in the corpus.
2. **Given** an answer combining information from multiple non-adjacent chunks,
   **When** the answer is displayed, **Then** every source chunk used is cited.

---

### User Story 2 - Clear abstention when context is insufficient (Priority: P1)

A student asks a question outside the corpus domain (or otherwise unanswerable
from retrieved context) and receives an explicit statement that the system
cannot answer from the available sources, with no fabricated citations.

**Why this priority**: Honest abstention is a non-negotiable constitutional
requirement (groundedness over fluency); a fabricated answer is a thesis-level
failure.

**Independent Test**: Can be fully tested by submitting an out-of-corpus question
and confirming the abstention response contains zero citations to non-existent
sources.

**Acceptance Scenarios**:

1. **Given** a question entirely outside the corpus domain, **When** submitted,
   **Then** the system responds with an explicit "cannot answer from available
   sources" message and produces no unsupported factual claims.
2. **Given** retrieved chunks are irrelevant or contradictory to the question,
   **When** no confident grounded answer is possible, **Then** the system
   abstains rather than guessing.

---

### User Story 3 - Mixed Persian/English technical queries (Priority: P2)

A student asks a question mixing Persian prose with English technical terms
(function names, library names, error messages, identifiers) and receives a
correctly understood, grounded, cited Persian response.

**Why this priority**: Code-mixed queries are the norm in Persian technical
discourse; the constitution makes Persian-first quality including mixed terms
first-class.

**Independent Test**: Can be fully tested by submitting Persian questions
containing English identifiers and confirming answers meet the same citation and
groundedness standards as pure-Persian queries.

**Acceptance Scenarios**:

1. **Given** a Persian question containing an English function or library name,
   **When** submitted, **Then** the system interprets the term correctly and
   returns a grounded, cited Persian answer.
2. **Given** a mixed-language query in the evaluation set, **When** scored,
   **Then** it meets the same citation and groundedness standards as
   pure-Persian queries.

---

### User Story 4 - Evaluator verifies quality objectively (Priority: P2)

An evaluator/examiner inspects a fixed, versioned evaluation question set with
expected sources/answers and obtains measured retrieval and citation quality
(retrieval hit-rate, citation precision reported).

**Why this priority**: Evaluability is constitutionally required; the thesis
must justify decisions with evidence.

**Independent Test**: Can be fully tested by running the evaluation procedure on
the fixed question set and confirming a report of retrieval hit-rate and
citation precision is produced.

**Acceptance Scenarios**:

1. **Given** the versioned evaluation question set, **When** the evaluator runs
   the scoring procedure, **Then** retrieval hit-rate and citation precision
   are measured and reported.
2. **Given** the evaluation set contains out-of-corpus questions, **When**
   scored, **Then** the system is credited only for explicit abstention with
   zero fabricated citations.

### Edge Cases

- Question entirely outside the corpus domain → explicit abstention, zero
  fabricated citations.
- Question mixing Persian and English technical terms/identifiers → understood
  correctly, same groundedness/citation bar.
- Retrieval returns multiple partially conflicting or irrelevant chunks →
  answer uses only supporting chunks or abstains; conflicting sources are not
  silently merged into a false claim.
- Very short or ambiguous Persian questions → system asks one targeted
  follow-up question and waits; no answer is attempted until clarified.
- Answer requires combining multiple non-adjacent chunks → all contributing
  chunks are cited.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept a Persian-language question as input.
- **FR-002**: System MUST retrieve relevant chunks from the defined corpus
  before generating an answer. The corpus snapshot for this release is the full
  owner-authored Persian notes plus a named subset of cppreference.com C
  sections and named GNU C Library chapters, frozen with recorded version/date
  and provenance.
- **FR-003**: System MUST generate a Persian-language answer grounded only in
  retrieved chunks.
- **FR-004**: System MUST attach verifiable citations (source document
  name/title plus specific section or chunk referenced) to every factual claim
  in the answer. Clicking a citation MUST reveal the source title, section
  heading, and full cited chunk text so the user can verify grounding in place.
- **FR-005**: System MUST detect insufficient retrieved context and explicitly
  communicate inability to answer from available sources rather than guessing.
  The abstention response MUST be a Persian sentence naming the closest
  available topics as a helpful redirect.
- **FR-006**: System MUST correctly handle questions containing mixed Persian
  and English technical terms (identifiers, framework/library names, error text).
- **FR-007**: System MUST provide a versioned evaluation question set of ~30
  questions (20 in-corpus, 5 mixed Persian/English, 5 out-of-corpus) with
  expected sources/answers, usable to score retrieval and citation quality.

### Key Entities *(include if feature involves data)*

- **Question**: Persian-language input from the student; may embed English
  technical terms; the unit of retrieval and answering.
- **Corpus Chunk**: A retrievable unit of the fixed-snapshot corpus (Persian
  study notes in Markdown; cppreference.com C pages; GNU C Library manual),
  carrying source identity (document title/name) and location (section/chunk).
- **Grounded Answer**: Persian-language response whose factual claims each map
  to one or more Corpus Chunks; displayed together with its citations.
- **Citation**: Link between a claim in the answer and a real Corpus Chunk
  (source + location); must be verifiable by the user.
- **Abstention Response**: Persian-language message stating the system cannot
  answer from available sources and naming the closest available topics;
  carries no fabricated citations.
- **Evaluation Set**: Versioned collection of ~30 test questions (20 in-corpus,
  5 mixed-language, 5 out-of-corpus) with expected sources/answers; used to
  measure retrieval hit-rate and citation precision.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Students asking in-corpus Persian C questions receive a Persian
  answer with at least one verifiable citation in every response.
- **SC-002**: Evaluators can run the versioned evaluation set and obtain a
  reported retrieval hit-rate and citation precision for the system snapshot.
- **SC-003**: For out-of-corpus questions in the evaluation set, the system
  abstains explicitly in 100% of cases with zero fabricated citations.
- **SC-004**: Mixed Persian/English questions in the evaluation set meet the
  same citation and groundedness standards as pure-Persian questions (no
  degradation class for code-mixed queries).
- **SC-005**: A new evaluator following only the written setup, ingest, and
  evaluation instructions can reproduce the reported evaluation figures.

## Assumptions

- Scope is the C programming language (not C++): the described corpus (Persian
  C notes, cppreference C pages, glibc manual) is C-specific, so the opening
  "C and C++" phrase is treated as C only; C++ support would require a
  constitution amendment and corpus expansion.
- Corpus is a curated, fixed snapshot with recorded provenance and licensing
  notes (cppreference CC-BY-SA attribution preserved); real-time ingestion of
  new sources is out of scope per constitution.
- Interface is a minimal single-user demo web page (question box, answer pane,
  clickable citations, correct Persian/English bidirectional text rendering);
  multi-user, auth, and scaling concerns are out of scope.
- Specific numeric targets for retrieval hit-rate/citation precision thresholds
  are set during planning/evaluation design, not fixed in this spec.
- Clarification flow for very short/ambiguous questions is a simple text
  follow-up, not a multi-turn dialogue manager.
