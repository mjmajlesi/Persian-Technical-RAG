# Data Model: Grounded Persian C Q&A

**Feature**: [spec.md](./spec.md) | **Contracts**: [contracts/](./contracts/)

## Entities

### 1. CorpusSource

A frozen input document recorded in `data/corpus/manifest.json`.

| Field | Description | Validation |
|-------|-------------|------------|
| `source_id` | Stable slug, e.g. `fa-notes-pointers`, `cppref-malloc`, `glibc-io` | Unique, lowercase-hyphenated |
| `title` | Human-readable title shown in citations | Non-empty |
| `kind` | `persian-notes` \| `cppreference` \| `glibc` | Enum |
| `origin` | File path (notes) or URL (reference pages) | Non-empty |
| `snapshot` | Retrieval/freezing date (YYYY-MM-DD) + version where applicable | Valid date |
| `license` | License note (e.g. `CC-BY-SA-3.0` for cppreference) | Non-empty |

### 2. CorpusChunk

The unit of retrieval and citation, stored in `data/index/chunks.jsonl`.

| Field | Description | Validation |
|-------|-------------|------------|
| `chunk_id` | Stable ID, e.g. `fa-notes-pointers#s03-c02` | Unique; deterministic from source + section + ordinal |
| `source_id` | FK → CorpusSource | Must exist in manifest |
| `doc_title` | Denormalized title for citation display | Matches source title |
| `section_heading` | Section name for citation display + abstention topic hints | Non-empty |
| `text` | Chunk body (Markdown preserved, code blocks intact) | Non-empty; ≤ ~512 tokens |
| `lang` | `fa` \| `en` \| `mixed` | Enum |

Relationships: CorpusSource 1→N CorpusChunk. Chunks are immutable once the
snapshot is frozen; any corpus change creates a new snapshot version.

### 3. Question

| Field | Description | Validation |
|-------|-------------|------------|
| `text` | Raw user input (Persian, optionally code-mixed) | Non-empty after trim |
| `lang_hint` | `fa` \| `mixed` (detected: presence of Latin identifiers) | Enum |

State: `received` → `clarified?` (if ambiguous, one follow-up asked, no answer
attempted) → `answered` | `abstained`.

### 4. GroundedAnswer

| Field | Description | Validation |
|-------|-------------|------------|
| `answer_text` | Persian response | Non-empty; Persian-dominant |
| `citations` | 1..N Citation objects | ≥1; every `chunk_id` must exist in the index |
| `retrieved_chunk_ids` | Top-k chunk IDs consulted | Superset of cited IDs |

Rule: every factual claim in `answer_text` maps to ≥1 citation; cited IDs must
be a subset of retrieved IDs (no citing what was not retrieved).

### 5. Citation

| Field | Description | Validation |
|-------|-------------|------------|
| `chunk_id` | FK → CorpusChunk | Must resolve in current index |
| `doc_title` | Display title | Matches chunk |
| `section_heading` | Display section | Matches chunk |
| `excerpt` | Full chunk text shown on click | Equals stored chunk text |

### 6. AbstentionResponse

| Field | Description | Validation |
|-------|-------------|------------|
| `message` | Fixed-form Persian sentence | Names closest available topics |
| `suggested_topics` | 1..3 section/source names | Each must exist in corpus |
| `citations` | Always empty | Zero fabricated citations (contract-tested) |

### 7. EvalItem / EvalReport

EvalItem: `{item_id, question, qtype: in-corpus|mixed|out-of-corpus,
expected_source_ids, expected_answer_summary}`. The set version (e.g. `v1`,
30 items in 20/5/5 split) is stored with the items under `data/eval/`.

EvalReport: `{eval_set_version, index_snapshot, llm_id, hit_rate_at_5,
citation_precision, abstention_correct, mixed_slice_scores, per_item_rows}` —
written as JSON + Markdown summary under `data/eval/reports/`.

## Validation rules (cross-entity)

- No Citation may reference a `chunk_id` absent from the active index
  (enforced by contract test on every answer).
- AbstentionResponse must carry zero citations (enforced by test).
- EvalReport is reproducible: same corpus snapshot + same set version ⇒ same
  retrieval rows; LLM text may vary but citation [/abstention](/abstention)
  verdicts must hold.
