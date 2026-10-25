# python v2 embedding comparison

Set: `data/eval/python/eval-set.python.v2.json` (SHA-256 `94a4ec6e4f5c9ecfbf64681e05a314e1c35f47869247671543e1b5bedfc7604a`; n=45). Seed 20261022, 10000 paired resamples; 95% metric CIs, 98.33% Bonferroni pair CIs.

| Model | Hit@5 /38 (95% CI) | Citation precision (answered; citations) | Fixed OOC /7 | E2E OOC /7 | Errors retrieval/E2E |
|---|---|---|---|---|---|
| e5-large | 24/38 0.632 [0.474, 0.784] | 16/20 (18 answers) 0.833 [0.658, 0.972] | 6/7 0.857 [0.500, 1.000] | 7/7 1.000 [1.000, 1.000] | 0/0 |
| e5-base | 19/38 0.500 [0.341, 0.658] | 10/14 (12 answers) 0.792 [0.542, 1.000] | 4/7 0.571 [0.167, 1.000] | 7/7 1.000 [1.000, 1.000] | 0/0 |
| bge-m3 | 26/38 0.684 [0.526, 0.825] | 17/21 (18 answers) 0.861 [0.714, 0.974] | 7/7 1.000 [1.000, 1.000] | 7/7 1.000 [1.000, 1.000] | 0/0 |

**Decision (this language only): inconclusive**

Citation precision is a question-level mean over answered rows; citation counts are audit denominators, not the mean's denominator.

## Paired model differences (98.33% CIs)

| Pair (first minus second) | Hit@5 | Citation precision | Fixed OOC | E2E OOC |
|---|---|---|---|---|
| e5-large − e5-base | 0.132 [-0.051, 0.316] | 0.042 [-0.256, 0.350] | 0.286 [0.000, 0.800] | 0.000 [0.000, 0.000] |
| e5-large − bge-m3 | -0.053 [-0.270, 0.171] | -0.028 [-0.284, 0.225] | -0.143 [-0.571, 0.000] | 0.000 [0.000, 0.000] |
| e5-base − bge-m3 | -0.184 [-0.432, 0.079] | -0.069 [-0.397, 0.167] | -0.429 [-1.000, 0.000] | 0.000 [0.000, 0.000] |

## Mixed and evidence-language slices (95% CIs)

| Model / slice (n) | Hit@5 | Citation precision | Fixed OOC | E2E OOC |
|---|---|---|---|---|
| e5-large / mixed_qtype | 0.700 [0.375, 1.000] (n=10) | 0.929 [0.750, 1.000] (n=7) | N/A (n=0) | N/A (n=0) |
| e5-large / evidence_language:en | 0.632 [0.474, 0.784] (n=38) | 0.833 [0.658, 0.972] (n=18) | N/A (n=0) | N/A (n=0) |
| e5-large / evidence_language:none | N/A (n=0) | N/A (n=0) | 0.857 [0.500, 1.000] (n=7) | 1.000 [1.000, 1.000] (n=7) |
| e5-base / mixed_qtype | 0.700 [0.385, 1.000] (n=10) | 0.786 [0.500, 1.000] (n=7) | N/A (n=0) | N/A (n=0) |
| e5-base / evidence_language:en | 0.500 [0.341, 0.658] (n=38) | 0.792 [0.542, 1.000] (n=12) | N/A (n=0) | N/A (n=0) |
| e5-base / evidence_language:none | N/A (n=0) | N/A (n=0) | 0.571 [0.167, 1.000] (n=7) | 1.000 [1.000, 1.000] (n=7) |
| bge-m3 / mixed_qtype | 0.900 [0.667, 1.000] (n=10) | 0.833 [0.571, 1.000] (n=9) | N/A (n=0) | N/A (n=0) |
| bge-m3 / evidence_language:en | 0.684 [0.526, 0.825] (n=38) | 0.861 [0.714, 0.974] (n=18) | N/A (n=0) | N/A (n=0) |
| bge-m3 / evidence_language:none | N/A (n=0) | N/A (n=0) | 1.000 [1.000, 1.000] (n=7) | 1.000 [1.000, 1.000] (n=7) |

## Descriptive v2 threshold sensitivity (not calibration)

| Model | Locked pooled-v1 gate | OOC-positive AUROC (95% CI) | Observed v2 best gate (descriptive only) |
|---|---|---|---|
| e5-large | 0.808959 | 0.620 [0.445, 0.784] (7 OOC / 38 answerable) | 0.812462 |
| e5-base | 0.802649 | 0.519 [0.341, 0.703] (7 OOC / 38 answerable) | 0.809796 |
| bge-m3 | 0.550487 | 0.895 [0.787, 0.976] (7 OOC / 38 answerable) | 0.524844 |

## Sources and reproducibility

- e5-large: retrieval `data/eval/python/reports/v2/e5-large/2026-10-25-011006-858513-python-v2-retrieval-only.json` (SHA-256 `b1703c5547e876095e4e1f7ef50eeede5a1e9d4d50241161054ccb341324669b`); E2E `data/eval/python/reports/v2/e5-large/2026-10-25-024223-113813-python-v2-end-to-end.json` (SHA-256 `230d28d3fd4b1cdcefb52a3b50c56ddd13074338a1caec786d268fcb60f448b3`); revision `3d7cfbdacd47fdda877c5cd8a79fbcc4f2a574f3`; calibration SHA-256 `01eac2939b10b1a97e26f9c10309289df621176d2f4159f275d48f661b51a62c`. E2E status complete; reasons: none.
- e5-base: retrieval `data/eval/python/reports/v2/e5-base/2026-10-25-011037-537084-python-v2-retrieval-only.json` (SHA-256 `79bf7a1e5fdec7560a2565c351667dfa872b88f333750afa264fe7805e34954d`); E2E `data/eval/python/reports/v2/e5-base/2026-10-25-024441-877000-python-v2-end-to-end.json` (SHA-256 `7d97a83c5cb9cd6d60013e8c03a1fca4b35c0a3d7101262a23c90f78f466b16d`); revision `d128750597153bb5987e10b1c3493a34e5a4502a`; calibration SHA-256 `defbe4d1aeadf87b43000985bb84389f9dcc067d50276d4c6902206bff08e555`. E2E status complete; reasons: none.
- bge-m3: retrieval `data/eval/python/reports/v2/bge-m3/2026-10-25-011114-840748-python-v2-retrieval-only.json` (SHA-256 `6abf252036c726b49a915eda2e5016e0a3dbaa279791958771415d31654cad69`); E2E `data/eval/python/reports/v2/bge-m3/2026-10-25-024723-172063-python-v2-end-to-end.json` (SHA-256 `e65ff43fa477362ffe8dc7ff3393bbfe2d17a8a527cbd24d494787ddd6d84d5c`); revision `5617a9f61b028005a4858fdac845db406aefb181`; calibration SHA-256 `965f1c07ea0a9bb2a7396ca1dd542c990b6dc62f2369db74a89a9e3320d6b26a`. E2E status complete; reasons: none.

Per-item scores, retrieval IDs, cited IDs, reference IDs and PR points are in the companion JSON; no global winner is inferred.

## Limitations

- Seven out-of-corpus questions per language limit abstention inference.
- The pooled-v1 gates are frozen; v2 sweep optima are descriptive only.
- The E5 baseline saw v1; a stable API model ID cannot prove immutable weights.
