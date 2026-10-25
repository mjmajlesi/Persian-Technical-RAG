# cpp v2 embedding comparison

Set: `data/eval/cpp/eval-set.cpp.v2.json` (SHA-256 `1fab399cf00bb133d510e21e9d6c2eb1bf0975ce7d645454d5b3b3fc6bc1c878`; n=45). Seed 20261022, 10000 paired resamples; 95% metric CIs, 98.33% Bonferroni pair CIs.

| Model | Hit@5 /38 (95% CI) | Citation precision (answered; citations) | Fixed OOC /7 | E2E OOC /7 | Errors retrieval/E2E |
|---|---|---|---|---|---|
| e5-large | 13/38 0.342 [0.194, 0.500] | 11/15 (14 answers) 0.750 [0.500, 0.958] | 0/7 0.000 [0.000, 0.000] | 7/7 1.000 [1.000, 1.000] | 0/0 |
| e5-base | 17/38 0.447 [0.289, 0.605] | 16/18 (17 answers) 0.912 [0.767, 1.000] | 0/7 0.000 [0.000, 0.000] | 7/7 1.000 [1.000, 1.000] | 0/0 |
| bge-m3 | 29/38 0.763 [0.622, 0.895] | 24/29 (25 answers) 0.880 [0.769, 0.975] | 3/7 0.429 [0.000, 0.833] | 7/7 1.000 [1.000, 1.000] | 0/0 |

**Decision (this language only): bge-m3**

Citation precision is a question-level mean over answered rows; citation counts are audit denominators, not the mean's denominator.

## Paired model differences (98.33% CIs)

| Pair (first minus second) | Hit@5 | Citation precision | Fixed OOC | E2E OOC |
|---|---|---|---|---|
| e5-large − e5-base | -0.105 [-0.316, 0.105] | -0.162 [-0.500, 0.150] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| e5-large − bge-m3 | -0.421 [-0.625, -0.211] | -0.130 [-0.429, 0.124] | -0.429 [-1.000, 0.000] | 0.000 [0.000, 0.000] |
| e5-base − bge-m3 | -0.316 [-0.538, -0.098] | 0.032 [-0.177, 0.214] | -0.429 [-1.000, 0.000] | 0.000 [0.000, 0.000] |

## Mixed and evidence-language slices (95% CIs)

| Model / slice (n) | Hit@5 | Citation precision | Fixed OOC | E2E OOC |
|---|---|---|---|---|
| e5-large / mixed_qtype | 0.500 [0.167, 0.818] (n=10) | 0.750 [0.361, 1.000] (n=6) | N/A (n=0) | N/A (n=0) |
| e5-large / evidence_language:en | 0.306 [0.162, 0.459] (n=36) | 0.708 [0.438, 0.950] (n=12) | N/A (n=0) | N/A (n=0) |
| e5-large / evidence_language:mixed | 1.000 [1.000, 1.000] (n=2) | 1.000 [1.000, 1.000] (n=2) | N/A (n=0) | N/A (n=0) |
| e5-large / evidence_language:none | N/A (n=0) | N/A (n=0) | 0.000 [0.000, 0.000] (n=7) | 1.000 [1.000, 1.000] (n=7) |
| e5-base / mixed_qtype | 0.800 [0.500, 1.000] (n=10) | 0.833 [0.571, 1.000] (n=9) | N/A (n=0) | N/A (n=0) |
| e5-base / evidence_language:en | 0.417 [0.257, 0.579] (n=36) | 0.900 [0.733, 1.000] (n=15) | N/A (n=0) | N/A (n=0) |
| e5-base / evidence_language:mixed | 1.000 [1.000, 1.000] (n=2) | 1.000 [1.000, 1.000] (n=2) | N/A (n=0) | N/A (n=0) |
| e5-base / evidence_language:none | N/A (n=0) | N/A (n=0) | 0.000 [0.000, 0.000] (n=7) | 1.000 [1.000, 1.000] (n=7) |
| bge-m3 / mixed_qtype | 0.900 [0.667, 1.000] (n=10) | 0.889 [0.750, 1.000] (n=9) | N/A (n=0) | N/A (n=0) |
| bge-m3 / evidence_language:en | 0.778 [0.632, 0.909] (n=36) | 0.875 [0.761, 0.974] (n=24) | N/A (n=0) | N/A (n=0) |
| bge-m3 / evidence_language:mixed | 0.500 [0.000, 1.000] (n=2) | 1.000 [1.000, 1.000] (n=1) | N/A (n=0) | N/A (n=0) |
| bge-m3 / evidence_language:none | N/A (n=0) | N/A (n=0) | 0.429 [0.000, 0.833] (n=7) | 1.000 [1.000, 1.000] (n=7) |

## Descriptive v2 threshold sensitivity (not calibration)

| Model | Locked pooled-v1 gate | OOC-positive AUROC (95% CI) | Observed v2 best gate (descriptive only) |
|---|---|---|---|
| e5-large | 0.808959 | 0.579 [0.406, 0.750] (7 OOC / 38 answerable) | 0.837727 |
| e5-base | 0.802649 | 0.677 [0.520, 0.824] (7 OOC / 38 answerable) | 0.827413 |
| bge-m3 | 0.550487 | 0.741 [0.568, 0.897] (7 OOC / 38 answerable) | 0.584926 |

## Sources and reproducibility

- e5-large: retrieval `data/eval/cpp/reports/v2/e5-large/2026-10-25-010053-231441-cpp-v2-retrieval-only.json` (SHA-256 `68cf5d882b23b3161cdd162ea8d8d74f46ded6d44192d6e221455358d2ef3173`); E2E `data/eval/cpp/reports/v2/e5-large/2026-10-25-014537-817989-cpp-v2-end-to-end.json` (SHA-256 `26f3d17aca8dbfafd0e282bd43470dc3f127efb64d87f86435f01627457537ac`); revision `3d7cfbdacd47fdda877c5cd8a79fbcc4f2a574f3`; calibration SHA-256 `01eac2939b10b1a97e26f9c10309289df621176d2f4159f275d48f661b51a62c`. E2E status complete; reasons: none.
- e5-base: retrieval `data/eval/cpp/reports/v2/e5-base/2026-10-25-010125-608408-cpp-v2-retrieval-only.json` (SHA-256 `8d36c687860b4035f6d25af3cf3db393ef98f10284e7e110e03b5aac911d1c7e`); E2E `data/eval/cpp/reports/v2/e5-base/2026-10-25-014920-616053-cpp-v2-end-to-end.json` (SHA-256 `cd8b24622b07c36152134185237d489e1dbd81d8de021dc66c866e30269b7fd4`); revision `d128750597153bb5987e10b1c3493a34e5a4502a`; calibration SHA-256 `defbe4d1aeadf87b43000985bb84389f9dcc067d50276d4c6902206bff08e555`. E2E status complete; reasons: none.
- bge-m3: retrieval `data/eval/cpp/reports/v2/bge-m3/2026-10-25-010207-328273-cpp-v2-retrieval-only.json` (SHA-256 `1b964f2d221bb98619edce3e70143411e9ef98e0482cba1caa4605ccbc2c6e28`); E2E `data/eval/cpp/reports/v2/bge-m3/2026-10-25-015232-193295-cpp-v2-end-to-end.json` (SHA-256 `f61ad24a4778228ea1fe1026afa344b9dd6be2ddcc255f92ccbd9b127715f278`); revision `5617a9f61b028005a4858fdac845db406aefb181`; calibration SHA-256 `965f1c07ea0a9bb2a7396ca1dd542c990b6dc62f2369db74a89a9e3320d6b26a`. E2E status complete; reasons: none.

Per-item scores, retrieval IDs, cited IDs, reference IDs and PR points are in the companion JSON; no global winner is inferred.

## Limitations

- Seven out-of-corpus questions per language limit abstention inference.
- The pooled-v1 gates are frozen; v2 sweep optima are descriptive only.
- The E5 baseline saw v1; a stable API model ID cannot prove immutable weights.
