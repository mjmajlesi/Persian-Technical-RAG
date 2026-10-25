# Embedding comparison: v2 evidence

## Primary analysis — one decision per language

Each table is a separate 45-question, three-model comparison with paired
question-level intervals. The linked JSON includes source-report hashes,
per-item audit rows, denominators, mixed/evidence-language slices, and
descriptive (non-calibrating) threshold sweeps.

| Language | Official table | Machine-readable evidence | Language-only decision |
|---|---|---|---|
| C | [Markdown](../data/eval/c/reports/v2/comparison.v2.md) | [JSON](../data/eval/c/reports/v2/comparison.v2.json) | inconclusive |
| C++ | [Markdown](../data/eval/cpp/reports/v2/comparison.v2.md) | [JSON](../data/eval/cpp/reports/v2/comparison.v2.json) | bge-m3 |
| Python | [Markdown](../data/eval/python/reports/v2/comparison.v2.md) | [JSON](../data/eval/python/reports/v2/comparison.v2.json) | inconclusive |
| Java | [Markdown](../data/eval/java/reports/v2/comparison.v2.md) | [JSON](../data/eval/java/reports/v2/comparison.v2.json) | bge-m3 |

The primary 95% intervals and counts, reproduced from those four official
tables (precision is the mean over answered questions):

### C — inconclusive

| Model | Hit@5 /38 | Citation precision (answers; correct/cited) | Fixed OOC /7 | E2E OOC /7 |
|---|---|---|---|---|
| e5-large | 26/38 0.684 [0.529, 0.833] | 29; 25/32 0.810 [0.672, 0.931] | 1/7 0.143 [0.000, 0.500] | 7/7 1.000 [1.000, 1.000] |
| e5-base | 21/38 0.553 [0.395, 0.703] | 24; 21/27 0.833 [0.684, 0.958] | 1/7 0.143 [0.000, 0.500] | 7/7 1.000 [1.000, 1.000] |
| bge-m3 | 27/38 0.711 [0.564, 0.848] | 27; 24/37 0.772 [0.638, 0.897] | 6/7 0.857 [0.500, 1.000] | 7/7 1.000 [1.000, 1.000] |

### C++ — bge-m3

| Model | Hit@5 /38 | Citation precision (answers; correct/cited) | Fixed OOC /7 | E2E OOC /7 |
|---|---|---|---|---|
| e5-large | 13/38 0.342 [0.194, 0.500] | 14; 11/15 0.750 [0.500, 0.958] | 0/7 0.000 [0.000, 0.000] | 7/7 1.000 [1.000, 1.000] |
| e5-base | 17/38 0.447 [0.289, 0.605] | 17; 16/18 0.912 [0.767, 1.000] | 0/7 0.000 [0.000, 0.000] | 7/7 1.000 [1.000, 1.000] |
| bge-m3 | 29/38 0.763 [0.622, 0.895] | 25; 24/29 0.880 [0.769, 0.975] | 3/7 0.429 [0.000, 0.833] | 7/7 1.000 [1.000, 1.000] |

### Python — inconclusive

| Model | Hit@5 /38 | Citation precision (answers; correct/cited) | Fixed OOC /7 | E2E OOC /7 |
|---|---|---|---|---|
| e5-large | 24/38 0.632 [0.474, 0.784] | 18; 16/20 0.833 [0.658, 0.972] | 6/7 0.857 [0.500, 1.000] | 7/7 1.000 [1.000, 1.000] |
| e5-base | 19/38 0.500 [0.341, 0.658] | 12; 10/14 0.792 [0.542, 1.000] | 4/7 0.571 [0.167, 1.000] | 7/7 1.000 [1.000, 1.000] |
| bge-m3 | 26/38 0.684 [0.526, 0.825] | 18; 17/21 0.861 [0.714, 0.974] | 7/7 1.000 [1.000, 1.000] | 7/7 1.000 [1.000, 1.000] |

### Java — bge-m3

| Model | Hit@5 /38 | Citation precision (answers; correct/cited) | Fixed OOC /7 | E2E OOC /7 |
|---|---|---|---|---|
| e5-large | 33/38 0.868 [0.750, 0.972] | 18; 17/21 0.889 [0.750, 1.000] | 6/7 0.857 [0.500, 1.000] | 7/7 1.000 [1.000, 1.000] |
| e5-base | 32/38 0.842 [0.718, 0.949] | 14; 14/19 0.845 [0.704, 0.964] | 7/7 1.000 [1.000, 1.000] | 7/7 1.000 [1.000, 1.000] |
| bge-m3 | 38/38 1.000 [1.000, 1.000] | 27; 27/32 0.920 [0.839, 0.982] | 7/7 1.000 [1.000, 1.000] | 7/7 1.000 [1.000, 1.000] |

The four primary tables take precedence over the secondary summary below.
No global winner is inferred.

## Secondary pooled analysis — exploratory only

The four frozen language reports contribute 180 questions: 152 answerable
(38 per language) and 28 out-of-corpus (7 per language). `exploratory_pool`
in `src/eval/comparison.py` resamples 45 question IDs *within each language*
per replicate and applies the same indices to all three models. The following
95% percentile intervals use 10,000 replicates and seed `20261022`.
Citation precision is the mean of *answered-question* precision values;
its `correct/cited` counts are audit totals, not its estimator denominator.

| Model | Retrieval hit@5 | Answered-only citation precision | Fixed-gate OOC abstention | E2E OOC abstention | Retrieval/E2E errors |
|---|---|---|---|---|---|
| e5-large | 96/152 = 0.632 [0.559, 0.704] | 0.823 [0.743, 0.897]; 79 answers, 69/88 cited | 13/28 = 0.464 [0.286, 0.643] | 28/28 = 1.000 [1.000, 1.000] | 0/0 |
| e5-base | 89/152 = 0.586 [0.510, 0.660] | 0.848 [0.769, 0.918]; 67 answers, 61/78 cited | 12/28 = 0.429 [0.250, 0.607] | 28/28 = 1.000 [1.000, 1.000] | 0/0 |
| bge-m3 | 120/152 = 0.789 [0.724, 0.850] | 0.857 [0.798, 0.910]; 97 answers, 92/119 cited | 23/28 = 0.821 [0.667, 0.957] | 28/28 = 1.000 [1.000, 1.000] | 0/0 |

**Interpretation boundary:** This table is descriptive, not a fourth
winner test. Pooling can hide pack-specific differences and the OOC sample
remains small within each language. The pooled-v1 thresholds are locked;
neither these v2 scores nor any v2 sweep optimum changes them. If any
model's E2E run is incomplete in one language, that model's pooled E2E
metrics are N/A while its valid retrieval metrics remain available.

## Questions, reference answers, and traceable evidence

The approved v2 benchmark has **45 new Persian questions per pack**: 28
in-corpus, 10 code-mixed, and 7 out-of-corpus; 180 questions in total. The
versioned JSON files contain every question, the author's *reference-answer
summary* (for each of 152 answerable questions), expected chunk IDs, a
section/title/origin/license provenance record, evidence language, and the
authorship/review record. Each of the 28 OOC items instead carries an
`abstain_reason` and has no expected source IDs or provenance. These are
question/reference records, **not** full verbatim extracts from sources.

| Pack | Questions and reference summaries | Frozen source inventory | Ordered chunk-ID audit | Supporting evidence in answerable items |
|---|---|---|---|---|
| C | [C v2](../data/eval/c/eval-set.c.v2.json) | [C manifest](../data/corpus/manifest.c.json) | [C IDs/hash](../specs/003-compare-embedding-models/baseline-audit.md) | 26 owner notes, 12 cppreference |
| C++ | [C++ v2](../data/eval/cpp/eval-set.cpp.v2.json) | [C++ manifest](../data/corpus/manifest.cpp.json) | [C++ IDs/hash](../specs/003-compare-embedding-models/baseline-audit.md) | 2 owner notes, 36 cppreference |
| Python | [Python v2](../data/eval/python/eval-set.python.v2.json) | [Python manifest](../data/corpus/manifest.python.json) | [Python IDs/hash](../specs/003-compare-embedding-models/baseline-audit.md) | 38 Python documentation |
| Java | [Java v2](../data/eval/java/eval-set.java.v2.json) | [Java manifest](../data/corpus/manifest.java.json) | [Java IDs/hash](../specs/003-compare-embedding-models/baseline-audit.md) | 38 Oracle tutorials |

An item links `expected_source_ids` to `provenance[].chunk_id`; each
provenance entry repeats the frozen manifest's title, origin, snapshot, and
license. The original source files record a URL and retrieval date when
applicable. The [baseline audit](../specs/003-compare-embedding-models/baseline-audit.md)
records the immutable v1 and canonical-chunk hashes. Generated
`data/index/<pack>/chunks.jsonl` text is gitignored, so it is **not** a
publishable link; reproduce it from the versioned corpus files and check
its hash and ordered IDs against the audit before evaluating. Validation checked all
152 positive items against their pack's chunk inventory and manifest and
all 28 OOC items for empty evidence and an explicit reason. `evidence_language`
comes from the source, not the language of the question: C has 26 mixed
Persian/English and 12 English answerable sources; C++ has 2 mixed and 36
English; Python and Java each have 38 English-only sources. The evaluation
does not generalize to other domains or to Persian-only reference corpora.

**Rights and attribution.** Owner-authored study notes are attributed to the
project owner; cppreference material is marked CC-BY-SA, Python documentation
PSF License, and Oracle tutorial material "see docs.oracle.com terms" in the
frozen manifests. GNU C Library material elsewhere in the C corpus is
marked GFDL but is **not** a supporting source for these 152 answers. These
labels identify origins; they are not a legal determination that every
third-party full-text extract may be republished under this project's terms.
In particular, Oracle's redistribution terms require separate review before
reusing substantial text. This paper quotes no third-party source passages;
follow item-level provenance and source URLs for attribution and rights checks.

## Models and evaluation method

The pinned [model registry](../data/eval/model-comparison/models.json) records
the repository, immutable revision, card, MIT model license, vector dimension,
prefixes, normalization, and length limit. The roster is:

| Candidate / model card | Pinned repository revision | Dense dimension | Query/passage preparation and limit |
|---|---|---:|---|
| [e5-large](https://huggingface.co/intfloat/multilingual-e5-large) | `intfloat/multilingual-e5-large@3d7cfbdacd47fdda877c5cd8a79fbcc4f2a574f3` | 1024 | `query: ` / `passage: `, L2 normalized, 512 tokens |
| [e5-base](https://huggingface.co/intfloat/multilingual-e5-base) | `intfloat/multilingual-e5-base@d128750597153bb5987e10b1c3493a34e5a4502a` | 768 | E5 prefixes, L2 normalized, 512 tokens |
| [bge-m3](https://huggingface.co/BAAI/bge-m3) | `BAAI/bge-m3@5617a9f61b028005a4858fdac845db406aefb181` | 1024 | no added instruction, normalized dense-only, 8192 tokens |

All three registered model revisions are marked MIT; this is separate from
the corpus licenses above. The three models embed the same ordered canonical
chunks into **separate** pack/model indices. The research gate is one fixed
threshold per model, selected *before v2* on the four frozen v1 packs pooled
(100 answerable / 20 OOC), by maximal balanced accuracy with a conservative
tie break. [Calibration records](../data/eval/model-comparison/calibration/)
include pooled and pack-level confusion counts. These are **not** the existing
student-facing operational gates; no v2 question or pilot question is used
to select them. E5-large is also the operational baseline and has had earlier
v1 exposure, which limits a naive interpretation of head-to-head differences.

Retrieval hit@5 uses all 38 answerable items per language and makes **zero
LLM calls**. Fixed-gate abstention uses the 7 OOC questions per pack; the
separately measured E2E abstention can additionally benefit from the
response model. Citation precision is the macro mean over *answered* items,
with answer and citation counts shown so excess abstention is visible. AUROC
and OOC-positive PR points sweep v2 scores only for sensitivity analysis;
the observed v2 optimum is not deployed. CI calculations use 10,000 seeded
question resamples (`20261022`), paired on item ID within each language;
the three pairwise model-difference CIs are Bonferroni-adjusted to 98.33%.
A model wins in one language only if its hit@5 difference CI is above zero
against **both** alternatives and precision/fixed-gate/E2E abstention show
no statistically significant harm. Otherwise that language is inconclusive.
The Bonferroni adjustment covers three model pairs **within one language**;
it is not a familywise correction over all four languages or all outcome
metrics. These bootstrap intervals are conditional on these frozen questions.
The actual evidence supports bge-m3 for C++ and Java, not C or Python; the
pooled descriptive figures do not establish a universal winner.

## The 12 model-language run pairs (official JSON)

Every row links **both** the zero-LLM retrieval-only report and the audited
E2E report. Each has 45 retrieval rows and zero errors; E2E has 45 final
responses and a verified, pre-registered API-returned model ID. The linked
per-language comparison JSON/Markdown above supplies the derived CI tables,
per-item reproduction rows, and hashes of both inputs. Incomplete E2E rows
must remain diagnostics rather than be mixed into these complete results.

| Pack / model | Retrieval-only evidence | E2E evidence |
|---|---|---|
| C / e5-large | [JSON](../data/eval/c/reports/v2/e5-large/2026-10-25-003405-458814-c-v2-retrieval-only.json) | [JSON](../data/eval/c/reports/v2/e5-large/2026-10-25-012628-154313-c-v2-end-to-end.json) |
| C / e5-base | [JSON](../data/eval/c/reports/v2/e5-base/2026-10-25-003439-986133-c-v2-retrieval-only.json) | [JSON](../data/eval/c/reports/v2/e5-base/2026-10-25-013116-001298-c-v2-end-to-end.json) |
| C / bge-m3 | [JSON](../data/eval/c/reports/v2/bge-m3/2026-10-25-003519-848745-c-v2-retrieval-only.json) | [JSON](../data/eval/c/reports/v2/bge-m3/2026-10-25-013440-179357-c-v2-end-to-end.json) |
| C++ / e5-large | [JSON](../data/eval/cpp/reports/v2/e5-large/2026-10-25-010053-231441-cpp-v2-retrieval-only.json) | [JSON](../data/eval/cpp/reports/v2/e5-large/2026-10-25-014537-817989-cpp-v2-end-to-end.json) |
| C++ / e5-base | [JSON](../data/eval/cpp/reports/v2/e5-base/2026-10-25-010125-608408-cpp-v2-retrieval-only.json) | [JSON](../data/eval/cpp/reports/v2/e5-base/2026-10-25-014920-616053-cpp-v2-end-to-end.json) |
| C++ / bge-m3 | [JSON](../data/eval/cpp/reports/v2/bge-m3/2026-10-25-010207-328273-cpp-v2-retrieval-only.json) | [JSON](../data/eval/cpp/reports/v2/bge-m3/2026-10-25-015232-193295-cpp-v2-end-to-end.json) |
| Python / e5-large | [JSON](../data/eval/python/reports/v2/e5-large/2026-10-25-011006-858513-python-v2-retrieval-only.json) | [JSON](../data/eval/python/reports/v2/e5-large/2026-10-25-024223-113813-python-v2-end-to-end.json) |
| Python / e5-base | [JSON](../data/eval/python/reports/v2/e5-base/2026-10-25-011037-537084-python-v2-retrieval-only.json) | [JSON](../data/eval/python/reports/v2/e5-base/2026-10-25-024441-877000-python-v2-end-to-end.json) |
| Python / bge-m3 | [JSON](../data/eval/python/reports/v2/bge-m3/2026-10-25-011114-840748-python-v2-retrieval-only.json) | [JSON](../data/eval/python/reports/v2/bge-m3/2026-10-25-024723-172063-python-v2-end-to-end.json) |
| Java / e5-large | [JSON](../data/eval/java/reports/v2/e5-large/2026-10-25-011642-343421-java-v2-retrieval-only.json) | [JSON](../data/eval/java/reports/v2/e5-large/2026-10-25-052101-990661-java-v2-end-to-end.json) |
| Java / e5-base | [JSON](../data/eval/java/reports/v2/e5-base/2026-10-25-011712-695645-java-v2-retrieval-only.json) | [JSON](../data/eval/java/reports/v2/e5-base/2026-10-25-052255-457042-java-v2-end-to-end.json) |
| Java / bge-m3 | [JSON](../data/eval/java/reports/v2/bge-m3/2026-10-25-011757-879447-java-v2-retrieval-only.json) | [JSON](../data/eval/java/reports/v2/bge-m3/2026-10-25-052559-408017-java-v2-end-to-end.json) |

## Reproduction and limitations

The [research build log](../specs/003-compare-embedding-models/index-build-log.md)
records canonical chunk hashes, CPU timings, cache hits, vector dimensions,
and truncated passages. E5-large/E5-base each truncate 44/503 C, 37/201
C++, 134/253 Python, and 10/73 Java passages at 512 tokens; BGE-M3 recorded
zero at 8192 tokens. Different input lengths are a **model configuration
confound**, not proof of an intrinsic quality difference. All 12 indices
were validated locally on the CPU-only Windows laptop, one model/process at a
time; the BGE-M3 fresh-build times ranged from 395s (Java) to 1816s
(Python). Kaggle/GPU was **not used**. An optional Kaggle rerun must pin the
same SHA, settings, chunks and ID order, and disclose CPU/GPU floating-point
and top-k differences; byte-identical scores or indices across hardware
are not guaranteed. No peak-RAM number is claimed.

All completed E2E runs preregistered the expected API response ID
`gpt-5.6-sol`, sent `temperature=0`, and recorded provider, timestamp,
returned model ID and prompt hash for calls that reached the provider.
Fixed-gate abstentions intentionally have **no** LLM call or response ID.
The requested provider model can be an alias: a stable returned ID does
**not** prove immutable backend weights, and temperature zero does not
guarantee identical text on rerun. If an ID is absent/unexpected, the
temperature setting is rejected, or the service fails, E2E is incomplete;
valid retrieval-only evidence remains usable. The stored reports do not
contain API keys or provider URLs.

Finally, seven OOC examples per pack yield wide uncertainty about
abstention; perfect E2E OOC counts here do not establish universal safety.
Pooled-v1 gate performance differs across packs (see calibration records),
and the four corpora differ in size, provenance and language of evidence.
The sample does not isolate model architecture from tokenizer limits,
reference composition, earlier E5 exposure, or provider drift. A
cross-language rank would hide these differences; only the four primary
language-level CI decisions above are used for comparison claims.
