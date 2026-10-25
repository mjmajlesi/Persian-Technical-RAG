# c v2 embedding comparison

Set: `data/eval/c/eval-set.c.v2.json` (SHA-256 `9f5d929ea4b54f2268a2fcdad2d353ec62cccc2838462928eded9e1f29d37cf3`; n=45). Seed 20261022, 10000 paired resamples; 95% metric CIs, 98.33% Bonferroni pair CIs.

| Model | Hit@5 /38 (95% CI) | Citation precision (answered; citations) | Fixed OOC /7 | E2E OOC /7 | Errors retrieval/E2E |
|---|---|---|---|---|---|
| e5-large | 26/38 0.684 [0.529, 0.833] | 25/32 (29 answers) 0.810 [0.672, 0.931] | 1/7 0.143 [0.000, 0.500] | 7/7 1.000 [1.000, 1.000] | 0/0 |
| e5-base | 21/38 0.553 [0.395, 0.703] | 21/27 (24 answers) 0.833 [0.684, 0.958] | 1/7 0.143 [0.000, 0.500] | 7/7 1.000 [1.000, 1.000] | 0/0 |
| bge-m3 | 27/38 0.711 [0.564, 0.848] | 24/37 (27 answers) 0.772 [0.638, 0.897] | 6/7 0.857 [0.500, 1.000] | 7/7 1.000 [1.000, 1.000] | 0/0 |

**Decision (this language only): inconclusive**

Citation precision is a question-level mean over answered rows; citation counts are audit denominators, not the mean's denominator.

## Paired model differences (98.33% CIs)

| Pair (first minus second) | Hit@5 | Citation precision | Fixed OOC | E2E OOC |
|---|---|---|---|---|
| e5-large − e5-base | 0.132 [-0.024, 0.300] | -0.023 [-0.145, 0.090] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| e5-large − bge-m3 | -0.026 [-0.264, 0.216] | 0.039 [-0.135, 0.205] | -0.714 [-1.000, -0.200] | 0.000 [0.000, 0.000] |
| e5-base − bge-m3 | -0.158 [-0.361, 0.051] | 0.062 [-0.104, 0.215] | -0.714 [-1.000, -0.200] | 0.000 [0.000, 0.000] |

## Mixed and evidence-language slices (95% CIs)

| Model / slice (n) | Hit@5 | Citation precision | Fixed OOC | E2E OOC |
|---|---|---|---|---|
| e5-large / mixed_qtype | 0.200 [0.000, 0.500] (n=10) | 0.400 [0.000, 1.000] (n=5) | N/A (n=0) | N/A (n=0) |
| e5-large / evidence_language:en | 0.167 [0.000, 0.429] (n=12) | 0.400 [0.000, 1.000] (n=5) | N/A (n=0) | N/A (n=0) |
| e5-large / evidence_language:mixed | 0.923 [0.808, 1.000] (n=26) | 0.896 [0.786, 0.980] (n=24) | N/A (n=0) | N/A (n=0) |
| e5-large / evidence_language:none | N/A (n=0) | N/A (n=0) | 0.143 [0.000, 0.500] (n=7) | 1.000 [1.000, 1.000] (n=7) |
| e5-base / mixed_qtype | 0.100 [0.000, 0.333] (n=10) | 0.333 [0.000, 1.000] (n=3) | N/A (n=0) | N/A (n=0) |
| e5-base / evidence_language:en | 0.083 [0.000, 0.286] (n=12) | 0.333 [0.000, 1.000] (n=3) | N/A (n=0) | N/A (n=0) |
| e5-base / evidence_language:mixed | 0.769 [0.600, 0.920] (n=26) | 0.905 [0.781, 1.000] (n=21) | N/A (n=0) | N/A (n=0) |
| e5-base / evidence_language:none | N/A (n=0) | N/A (n=0) | 0.143 [0.000, 0.500] (n=7) | 1.000 [1.000, 1.000] (n=7) |
| bge-m3 / mixed_qtype | 0.700 [0.400, 1.000] (n=10) | 0.593 [0.312, 0.870] (n=9) | N/A (n=0) | N/A (n=0) |
| bge-m3 / evidence_language:en | 0.667 [0.375, 0.917] (n=12) | 0.633 [0.367, 0.889] (n=10) | N/A (n=0) | N/A (n=0) |
| bge-m3 / evidence_language:mixed | 0.731 [0.552, 0.889] (n=26) | 0.853 [0.700, 0.972] (n=17) | N/A (n=0) | N/A (n=0) |
| bge-m3 / evidence_language:none | N/A (n=0) | N/A (n=0) | 0.857 [0.500, 1.000] (n=7) | 1.000 [1.000, 1.000] (n=7) |

## Descriptive v2 threshold sensitivity (not calibration)

| Model | Locked pooled-v1 gate | OOC-positive AUROC (95% CI) | Observed v2 best gate (descriptive only) |
|---|---|---|---|
| e5-large | 0.808959 | 0.838 [0.707, 0.945] (7 OOC / 38 answerable) | 0.834249 |
| e5-base | 0.802649 | 0.767 [0.553, 0.945] (7 OOC / 38 answerable) | 0.831352 |
| bge-m3 | 0.550487 | 0.944 [0.853, 1.000] (7 OOC / 38 answerable) | 0.552714 |

## Sources and reproducibility

- e5-large: retrieval `data/eval/c/reports/v2/e5-large/2026-10-25-003405-458814-c-v2-retrieval-only.json` (SHA-256 `044291a879e30d84c89bcd376057f99489ba6e112743954e1cd4b14215b31aef`); E2E `data/eval/c/reports/v2/e5-large/2026-10-25-012628-154313-c-v2-end-to-end.json` (SHA-256 `cbdf7a96c91f235f32711de7d7f40de1538c50ac24d66982406953b466be3f54`); revision `3d7cfbdacd47fdda877c5cd8a79fbcc4f2a574f3`; calibration SHA-256 `01eac2939b10b1a97e26f9c10309289df621176d2f4159f275d48f661b51a62c`. E2E status complete; reasons: none.
- e5-base: retrieval `data/eval/c/reports/v2/e5-base/2026-10-25-003439-986133-c-v2-retrieval-only.json` (SHA-256 `adb3c5a492da19e18be1eecc95a3298d4c277e60b31b3a69eb044ced8b1d23fb`); E2E `data/eval/c/reports/v2/e5-base/2026-10-25-013116-001298-c-v2-end-to-end.json` (SHA-256 `1278ba61b4a66112afe9b3e64524a7ea92e68e60b604cd6f5f0eb7561b04f546`); revision `d128750597153bb5987e10b1c3493a34e5a4502a`; calibration SHA-256 `defbe4d1aeadf87b43000985bb84389f9dcc067d50276d4c6902206bff08e555`. E2E status complete; reasons: none.
- bge-m3: retrieval `data/eval/c/reports/v2/bge-m3/2026-10-25-003519-848745-c-v2-retrieval-only.json` (SHA-256 `9bad67a2309a41dbc975da13a9ae52f1d4796510979f5bff37c235bf56e49605`); E2E `data/eval/c/reports/v2/bge-m3/2026-10-25-013440-179357-c-v2-end-to-end.json` (SHA-256 `0d9cdf53e1583c4fe5984f3f330c1d4e964dcc44554f903379f8a7b76a4c58b1`); revision `5617a9f61b028005a4858fdac845db406aefb181`; calibration SHA-256 `965f1c07ea0a9bb2a7396ca1dd542c990b6dc62f2369db74a89a9e3320d6b26a`. E2E status complete; reasons: none.

Per-item scores, retrieval IDs, cited IDs, reference IDs and PR points are in the companion JSON; no global winner is inferred.

## Limitations

- Seven out-of-corpus questions per language limit abstention inference.
- The pooled-v1 gates are frozen; v2 sweep optima are descriptive only.
- The E5 baseline saw v1; a stable API model ID cannot prove immutable weights.
