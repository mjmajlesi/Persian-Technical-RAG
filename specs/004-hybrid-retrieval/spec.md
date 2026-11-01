# Pre-registration: hybrid retrieval experiment

## Hypothesis

Combining lexical BM25 and dense retrieval with reciprocal rank fusion (RRF)
may improve Hit@5 on the frozen technical-question sets. The experiment does
not change the operational dashboard, its default retriever, or its gate.

## Three-arm protocol

1. **Dense:** read the existing official v2 retrieval-only reports; do not rerun
   the baseline.
2. **BM25:** rank the canonical chunks of each pack by Okapi BM25, using the
   E5-large research index and its fixed dense top-1 score for the gate.
3. **Hybrid:** fuse each model's dense top 20 and BM25 top 20 with RRF
   (`k=60`). BM25 returns up to 20 ranked documents, including zero-score ties
   in canonical chunk order; fusion ties are deterministic. The gate and its
   top-1 score always come from that arm's dense retriever and locked threshold,
   not from BM25 or RRF scores.

All experimental runs are retrieval-only, use no LLM, preserve official data
and reports, and publish their reports under `data/research/hybrid-retrieval/`.

## Models and datasets

Use the existing E5-large and BGE-M3 research indexes and the official v2 sets
for C, C++, Python and Java. Run BM25 once per pack with E5-large gate context;
run hybrid once per pack for each dense model. Compare each hybrid model against
its own official dense baseline on the same question IDs and frozen pack.

## Metrics, statistics and decision

Report Hit@5 on the 38 answerable questions per pack and the mixed-question
slice, plus row-by-row equality of the fixed dense gate against the matching
official baseline. For each pack and model, compute the paired difference
`hybrid - dense` using the existing comparison method: resample the 45 question
rows together with replacement, exclude out-of-corpus rows from Hit@5 in each
sample, use seed `20261022` and 10,000 replicates, and report a two-sided 95%
percentile interval. These are separate per-comparison intervals, not a
simultaneous correction across all packs and models.

Per pack and dense model, call an effect **improvement** only if the interval is
entirely above zero; call it **significant regression** if entirely below zero.
Otherwise it is **inconclusive**. No operational adoption decision follows from
this experiment.
