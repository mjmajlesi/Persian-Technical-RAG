# Data Model: Multi-Language Dashboard

**Feature**: [spec.md](./spec.md) | **Contracts**: [contracts/](./contracts/)

001 entities (CorpusSource, CorpusChunk, Question, GroundedAnswer, Citation,
AbstentionResponse, EvalItem/EvalReport) are reused unchanged; what follows
is the per-language scoping layer 002 adds.

## Entities

### 1. LanguagePack

One supported programming language, described live from its manifest.

| Field | Description | Validation |
|-------|-------------|------------|
| `language_id` | Stable id: `c` \| `cpp` \| `python` \| `java` | Enum, unique |
| `display_name` | Sidebar label (Persian + English, e.g. "C++ / سی‌پلاس‌پلاس") | Non-empty |
| `manifest_path` | `data/corpus/manifest.<lang>.json` | File exists |
| `index_dir` | `data/index/<lang>/` | Exists when status is `ready` |
| `snapshot` | Corpus freeze date (YYYY-MM-DD) | Valid date |
| `eval_set_version` | e.g. `v1` | Non-empty when status is `ready` |
| `status` | `ready` \| `empty` (listed, no ingested index yet) | Enum |

### 2. SelectedLanguage

The student's current sidebar choice; default `c`. Scopes every retrieval,
generation, and citation check to its LanguagePack. Switching packs clears
the Q&A view state (no cross-language answer history is shown together).

### 3. Scoped Retrieval / Scoped Answer

Identical shapes to 001's retrieval results and `type: answer` payloads, plus
a `language_id` field echoing the SelectedLanguage. Cross-entity rules:

- Every `chunk_id` in a scoped answer MUST exist in the **selected pack's**
  `chunks.jsonl` (not merely in some pack).
- `citations` MUST be a subset of that pack's `retrieved_chunk_ids`.
- Any citation resolving to another pack's chunk is a **contamination
  failure** (contract-tested, scored 0 for that item).

### 4. PerLanguageEvalReport

001's EvalReport shape run with `--lang`, stored under
`data/eval/<lang>/reports/`, plus a `language_id` field and the
contamination slice: B-only questions asked under this pack must abstain
with zero foreign citations (target: all such probes abstain).

## Validation rules (cross-entity)

- `GET /api/languages` MUST list exactly the packs with manifest files;
  a pack without an index directory MUST report `empty` and its selection
  MUST render the "corpus not available" state, never an answer attempt.
- Adding a pack (new manifest + corpus + index + eval set) MUST NOT alter
  any existing pack's snapshot, index bytes, or recorded scores (SC-004;
  verified by re-running existing packs' evals unchanged).
