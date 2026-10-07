# Feature Specification: Multi-Language Dashboard

**Feature Branch**: `002-multi-language-dashboard`

**Created**: 2026-10-07

**Status**: Draft

**Input**: User description: "استاد پروژه گفته که دیتابیس نباید محدود به زبان C باشه. ایده من اینه که برای بخش UI یه حالت داشبورد بالا بیاد که کاربر بتونه زبان برنامه نویسی که میخواد را انتخاب بکنه و بعد که زبان را انتخاب کرد سوال یا کوئری مربوط به اون زبان را بپرسه."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Select language, ask in its corpus (Priority: P1)

A student opens the dashboard, sees the list of available programming
languages, selects one language, and then asks a Persian technical question
about that language. The system answers from that language's corpus only,
with verifiable citations to that language's sources.

**Why this priority**: This is the supervisor's explicit requirement and the
core of the feature; without language selection nothing else works.

**Independent Test**: Can be fully tested by selecting a language, asking an
in-corpus question for it, and confirming the answer cites only sources from
that language's corpus.

**Acceptance Scenarios**:

1. **Given** the dashboard shows available languages, **When** the student
   selects a language, **Then** the question interface becomes scoped to that
   language's corpus.
2. **Given** a language is selected, **When** the student asks an in-corpus
   question for it, **Then** the system returns a Persian grounded answer
   citing only that language's sources.

---

### User Story 2 - Groundedness guarantees hold per language (Priority: P1)

A student asking about a selected language receives the same guarantees as
the single-language system: every claim cited to a real chunk of that
language's corpus, and explicit abstention when context is insufficient —
never an answer built from another language's sources.

**Why this priority**: Cross-language contamination (e.g. answering a Python
question with C sources) would be a groundedness failure and invalidate the
thesis claim.

**Independent Test**: Can be fully tested by asking a question whose answer
exists only in another language's corpus and confirming the system abstains
rather than citing foreign-language sources.

**Acceptance Scenarios**:

1. **Given** language A is selected, **When** the student asks something
   answerable only from language B's corpus, **Then** the system abstains
   with zero citations to language B sources.
2. **Given** any selected language, **When** an answer is produced, **Then**
   every citation resolves to a chunk in that language's corpus snapshot.

---

### User Story 3 - Evaluator verifies each language separately (Priority: P2)

An evaluator inspects a per-language evaluation question set and obtains
retrieval/citation quality figures for each supported language.

**Why this priority**: The thesis must justify quality with evidence; a
single blended score would hide a weak language.

**Independent Test**: Can be fully tested by running the scoring procedure
for one language and confirming a per-language report is produced.

**Acceptance Scenarios**:

1. **Given** the versioned per-language evaluation sets, **When** the
   evaluator runs scoring for a language, **Then** hit-rate and citation
   precision for that language are reported.

### Edge Cases

- Student tries to ask without selecting a language → not possible: C is
  preselected by default and the sidebar always shows the current selection.
- A language has no ingested corpus yet (listed but empty) → selection shows
  an explicit "corpus not available" state instead of failing silently.
- Question is about language A but language B is selected → abstention path
  (US2), optionally suggesting the correct language.
- New language added later → appears on the dashboard only with its own
  corpus snapshot + eval set version recorded.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST present a dashboard with a persistent sidebar
  listing available programming languages, letting the student switch
  language at any time; C is preselected by default.
- **FR-002**: System MUST scope retrieval and generation to the selected
  language's corpus only (no cross-language chunk retrieval or citation).
- **FR-003**: System MUST generate the Persian grounded answer with the same
  citation and abstention guarantees as the single-language system, applied
  to the selected language's corpus.
- **FR-004**: System MUST provide a versioned evaluation question set per
  supported language, usable to score that language independently.
- **FR-005**: The launch language set is C, C++, Python, and Java, switched
  via the sidebar; C is preselected by default.
- **FR-006**: Each language's corpus is stored and retrieved from a separate
  per-language index (e.g. one index directory per language); selecting a
  language opens only its index, making cross-language leakage impossible
  by construction.
- **FR-007**: Corpus composition per language: C and C++ reuse the
  owner-authored Persian notes plus English references; Python and Java use
  English reference corpora only (no Persian notes). Accepted tradeoff
  (owner-confirmed): Python/Java need no exam-style Persian terminology and
  their documentation is strong, so reference-only corpora suffice; any
  quality gap vs C/C++ is reported transparently via per-language eval
  (SC-003) rather than claimed away.

### Key Entities *(include if feature involves data)*

- **LanguagePack**: One supported programming language with its display name,
  corpus snapshot (sources + version/date), and eval set version.
- **SelectedLanguage**: The student's current dashboard choice; scopes all
  retrieval, generation, and citation to its LanguagePack.
- **Scoped Answer**: A grounded Persian answer whose citations all resolve
  inside the SelectedLanguage's corpus (plus the per-language abstention
  response when context is insufficient).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Students can select any listed language and receive a Persian
  answer whose citations all resolve to that language's corpus.
- **SC-002**: For a question answerable only in another language's corpus,
  the system abstains in 100% of tested cases with zero foreign citations.
- **SC-003**: Evaluators obtain per-language hit-rate and citation precision
  figures for every supported language.
- **SC-004**: Adding a new language (corpus + eval set) is possible without
  changing existing languages' snapshots or scores.

## Assumptions

- The existing C corpus, pipeline, and guarantees (feature 001) are reused,
  not rebuilt; C becomes the first LanguagePack.
- The supervisor's requirement is multi-language *retrieval scope*, not
  multi-lingual UI: questions and answers stay Persian (per constitution
  non-goals on other languages).
- Expanding beyond the C-only corpus changes the project's stated scope, so
  a constitution amendment (minor version bump, revised Principle VII and
  scope notes) is required before planning this feature.
- Dashboard is a minimal single-user demo addition (language list +
  scoped Q&A view), consistent with the honest-scope prototype constraint.
