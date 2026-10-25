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

The provenance, licenses, reproduction narrative and publication caveats
are completed separately in T051.
