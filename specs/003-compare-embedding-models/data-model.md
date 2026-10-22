# Data Model: Embedding Model Comparison

**Spec**: [spec.md](./spec.md) | **Decisions**: [research.md](./research.md)

## Existing immutable inputs

| Entity | Fields used | Invariant |
|---|---|---|
| LanguagePack snapshot | `language_id`, `snapshot`, source IDs, origin/license | Four existing manifests are read, not refetched or reauthored. |
| CorpusChunk | `chunk_id`, `source_id`, heading, `text`, `lang` | Ordered `(chunk_id, text)` pairs are identical across all candidates; model-specific tokenization is **not** written back to chunks. |
| Eval set v1 | 30 items × four packs, question/type/expected IDs | Read-only calibration source; unchanged file hashes recorded before/after experiment. |

## New entities

### BenchmarkItem (v2)

| Field | Meaning / validation |
|---|---|
| `item_id`, `pack_id`, `version` | Unique within version and pack; exactly 45 per pack, disjoint from v1 IDs and paraphrase duplicates. |
| `question`, `qtype` | Nonempty Persian question; `in-corpus` (28), `mixed` (10; Persian with English technical terms), `out-of-corpus` (7). |
| `expected_source_ids` | Nonempty for answerable questions and resolvable **only** in this pack's frozen chunks; empty for out-of-corpus. |
| `expected_answer_summary` / `abstain_reason` | Answerable: concise source-grounded answer; OOC: documented reason sources do not support an answer. Exactly one applicable. |
| `evidence_language` | `fa`, `en` or `mixed`, derived from supporting source chunks; OOC uses `none`, not a guessed language. |
| `provenance` | Source ID, URL/origin, title, exact chunk/section, snapshot/license, authoring and review evidence; OOC keeps absence/review evidence without fabricated source IDs. |

**Validation**: 180/180 items have review metadata; source IDs exist in the selected pack; no cloned v1 wording/answer; IDs stable across revisions. Published summaries cite origin/licensing, not full third-party source text indiscriminately.

### ModelCandidate

| Field | Meaning / validation |
|---|---|
| `model_key`, `repository`, `revision_sha` | Unique short name; immutable model + tokenizer revision (three fixed candidates). |
| `license`, `model_card_url`, `inference_library_version` | Evidence for legal/reproducible use; no unrecorded `main` revision. |
| `dimension`, `query_prefix`, `passage_prefix`, `normalization`, `max_tokens` | Card-conformant dense encoding settings; type/shape checked before indexing and query. |

### EmbeddingArtifact / IndexArtifact

| Field | Meaning / validation |
|---|---|
| `model_key`, `pack_id`, `chunk_hash`, `settings_hash` | Model+pack identity; hash covers ordered raw `(chunk_id, text)` and all card-relevant settings. |
| `vectors_path`, `index_path`, `ids_path`, `dimension`, `count` | Ignored regenerable files, checked for shape/count, matching IDs, normalization and index metadata. |
| `device`, `batch_size`, `truncation_count`, `elapsed_seconds`, `status` | CPU/GPU context, observed resource/performance evidence; states `building`, `ready`, `failed`. |

Cache reuse only on exact fingerprint match. Model×pack index loader refuses mismatched hash/dimension; a failed/partial build never masquerades as ready. Retain prior valid artifact until a replacement is complete.

### CalibrationRecord

| Field | Meaning / validation |
|---|---|
| `model_key`, `v1_hashes`, `score_direction` | Four v1 set hashes; positive class is OOC (`top1` below gate). |
| `n_answerable`, `n_out`, `method`, `threshold` | 100/20 pooled items; maximal balanced accuracy; higher threshold on ties. |
| `pooled_confusion`, `per_language_confusion`, `locked_at` | Audit pooled optimization and four separate post-selection confusion tables. |

Exactly **one** locked research threshold per candidate, shared across packs. Operational pack thresholds are separate and unchanged. No v2 item participates in calibration.

### EvaluationRun / QuestionResult

| Field | Meaning / validation |
|---|---|
| `run_id`, `model_key`, `pack_id`, `set_version`, `snapshot_hash`, `calibration_id` | Identify one of 12 comparisons unambiguously. |
| `mode`, `top_k`, `llm_revision`, `temperature`, `prompt_hash` | `retrieval-only` has no LLM call; E2E must have verifiably fixed LLM settings and prompt. Never persist API keys. |
| `status`, `error_count`, `started_at`, `duration`, `device` | `running` → `complete` iff 45 expected rows and zero errors; else `incomplete`. |
| `QuestionResult` | Stable item ID; top-5 IDs, top-1 score, hit flag; fixed-gate abstention decision; E2E answer/abstain/error, cited IDs and strict precision/coverage when applicable. |
| `metrics` | Hit@5 on 38 answerable questions (retrieval only), fixed-gate and E2E abstention on 7 OOC, citation precision on answered questions with answer/citation denominators, source-language and mixed slices; estimate + 95% CI or N/A. |

An E2E failure never silently becomes an abstention. If none answered, precision is N/A with denominator 0. Citation IDs must belong to the selected pack; model/pack mismatches are errors, not zero scores.

### ComparisonReport

| Field | Meaning / validation |
|---|---|
| `candidate_runs`, `per_language_metrics` | Only complete, comparable runs; never one blended four-language headline. |
| `paired_differences`, `bootstrap_seed`, `replications` | Same question IDs resampled jointly, seed `20261022`, 10,000 draws, 95% metric CIs and Bonferroni-adjusted pair CIs for winner decision. |
| `threshold_sweep` | OOC-positive AUROC and PR curve from v2 top-1 scores **for analysis only**; any undefined slice reports N/A and counts. |
| `winner_status`, `limitations` | Per-language winner or `inconclusive`, with reasons including non-significant paired difference, meaningful secondary harm, missing metrics, E5's prior v1 exposure and pooled-gate risk. |

## Relationships and lifecycle

`LanguagePack` owns `CorpusChunk` and `BenchmarkItem`. Each `ModelCandidate` × `LanguagePack` produces one scoped `EmbeddingArtifact`/`IndexArtifact`; each model has one `CalibrationRecord` from **all four** v1 sets. `EvaluationRun` binds that index, gate and exactly one pack's v2 items. `ComparisonReport` joins matched QuestionResults by stable item ID **within a language**; it never joins samples from different packs into a single winner calculation.

`registered model + audited sources` → `building vectors` → `ready index` → `locked pooled calibration` → `retrieval-only run` → `optional pinned-LLM E2E run` → `complete comparison`. Errors produce `failed`/`incomplete` artifacts or runs with diagnostics and no winner claim.
