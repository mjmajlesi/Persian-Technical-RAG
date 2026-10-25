# java v2 embedding comparison

Set: `data/eval/java/eval-set.java.v2.json` (SHA-256 `bd8a0ee4fcfaeb259959a26db55f889f06e4252e45627e5d7fa3378c10144fa6`; n=45). Seed 20261022, 10000 paired resamples; 95% metric CIs, 98.33% Bonferroni pair CIs.

| Model | Hit@5 /38 (95% CI) | Citation precision (answered; citations) | Fixed OOC /7 | E2E OOC /7 | Errors retrieval/E2E |
|---|---|---|---|---|---|
| e5-large | 33/38 0.868 [0.750, 0.972] | 17/21 (18 answers) 0.889 [0.750, 1.000] | 6/7 0.857 [0.500, 1.000] | 7/7 1.000 [1.000, 1.000] | 0/0 |
| e5-base | 32/38 0.842 [0.718, 0.949] | 14/19 (14 answers) 0.845 [0.704, 0.964] | 7/7 1.000 [1.000, 1.000] | 7/7 1.000 [1.000, 1.000] | 0/0 |
| bge-m3 | 38/38 1.000 [1.000, 1.000] | 27/32 (27 answers) 0.920 [0.839, 0.982] | 7/7 1.000 [1.000, 1.000] | 7/7 1.000 [1.000, 1.000] | 0/0 |

**Decision (this language only): bge-m3**

Citation precision is a question-level mean over answered rows; citation counts are audit denominators, not the mean's denominator.

## Paired model differences (98.33% CIs)

| Pair (first minus second) | Hit@5 | Citation precision | Fixed OOC | E2E OOC |
|---|---|---|---|---|
| e5-large − e5-base | 0.026 [-0.114, 0.167] | 0.044 [-0.167, 0.237] | -0.143 [-0.600, 0.000] | 0.000 [0.000, 0.000] |
| e5-large − bge-m3 | -0.132 [-0.278, -0.025] | -0.031 [-0.207, 0.094] | -0.143 [-0.600, 0.000] | 0.000 [0.000, 0.000] |
| e5-base − bge-m3 | -0.158 [-0.308, -0.027] | -0.075 [-0.209, 0.028] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

## Mixed and evidence-language slices (95% CIs)

| Model / slice (n) | Hit@5 | Citation precision | Fixed OOC | E2E OOC |
|---|---|---|---|---|
| e5-large / mixed_qtype | 0.900 [0.667, 1.000] (n=10) | 0.929 [0.750, 1.000] (n=7) | N/A (n=0) | N/A (n=0) |
| e5-large / evidence_language:en | 0.868 [0.750, 0.972] (n=38) | 0.889 [0.750, 1.000] (n=18) | N/A (n=0) | N/A (n=0) |
| e5-large / evidence_language:none | N/A (n=0) | N/A (n=0) | 0.857 [0.500, 1.000] (n=7) | 1.000 [1.000, 1.000] (n=7) |
| e5-base / mixed_qtype | 1.000 [1.000, 1.000] (n=10) | 0.917 [0.750, 1.000] (n=6) | N/A (n=0) | N/A (n=0) |
| e5-base / evidence_language:en | 0.842 [0.718, 0.949] (n=38) | 0.845 [0.704, 0.964] (n=14) | N/A (n=0) | N/A (n=0) |
| e5-base / evidence_language:none | N/A (n=0) | N/A (n=0) | 1.000 [1.000, 1.000] (n=7) | 1.000 [1.000, 1.000] (n=7) |
| bge-m3 / mixed_qtype | 1.000 [1.000, 1.000] (n=10) | 0.875 [0.700, 1.000] (n=8) | N/A (n=0) | N/A (n=0) |
| bge-m3 / evidence_language:en | 1.000 [1.000, 1.000] (n=38) | 0.920 [0.839, 0.982] (n=27) | N/A (n=0) | N/A (n=0) |
| bge-m3 / evidence_language:none | N/A (n=0) | N/A (n=0) | 1.000 [1.000, 1.000] (n=7) | 1.000 [1.000, 1.000] (n=7) |

## Descriptive v2 threshold sensitivity (not calibration)

| Model | Locked pooled-v1 gate | OOC-positive AUROC (95% CI) | Observed v2 best gate (descriptive only) |
|---|---|---|---|
| e5-large | 0.808959 | 0.673 [0.509, 0.825] (7 OOC / 38 answerable) | 0.810418 |
| e5-base | 0.802649 | 0.564 [0.402, 0.725] (7 OOC / 38 answerable) | 0.802216 |
| bge-m3 | 0.550487 | 0.936 [0.845, 1.000] (7 OOC / 38 answerable) | 0.548568 |

## Sources and reproducibility

- e5-large: retrieval `data/eval/java/reports/v2/e5-large/2026-10-25-011642-343421-java-v2-retrieval-only.json` (SHA-256 `4cc2ab92531d0b4f540dac2e1766c79e498f12a140bff380b0f3f00ddea6dc5a`); E2E `data/eval/java/reports/v2/e5-large/2026-10-25-052101-990661-java-v2-end-to-end.json` (SHA-256 `3903e1daf409a6fbe8b086b47155b3f642d4af7d25b2a3f7451767a7d070011f`); revision `3d7cfbdacd47fdda877c5cd8a79fbcc4f2a574f3`; calibration SHA-256 `01eac2939b10b1a97e26f9c10309289df621176d2f4159f275d48f661b51a62c`. E2E status complete; reasons: none.
- e5-base: retrieval `data/eval/java/reports/v2/e5-base/2026-10-25-011712-695645-java-v2-retrieval-only.json` (SHA-256 `f725c78558f658c5a36a41db06a4ec544a2b7f1c260b5f492e9d677934ace09c`); E2E `data/eval/java/reports/v2/e5-base/2026-10-25-052255-457042-java-v2-end-to-end.json` (SHA-256 `74b8dd31b2aaef2a959a2bdbf03de9949fe1ec64a69f082a4454d8a0b28c74be`); revision `d128750597153bb5987e10b1c3493a34e5a4502a`; calibration SHA-256 `defbe4d1aeadf87b43000985bb84389f9dcc067d50276d4c6902206bff08e555`. E2E status complete; reasons: none.
- bge-m3: retrieval `data/eval/java/reports/v2/bge-m3/2026-10-25-011757-879447-java-v2-retrieval-only.json` (SHA-256 `15ee673e75822587b9876b3c3d690a64599b4b1cb09dbab97af6bc6b5b2a08fe`); E2E `data/eval/java/reports/v2/bge-m3/2026-10-25-052559-408017-java-v2-end-to-end.json` (SHA-256 `43151e26da50e3c5f0b05a2126f717953c9ce672283529c047d5bef784b48a50`); revision `5617a9f61b028005a4858fdac845db406aefb181`; calibration SHA-256 `965f1c07ea0a9bb2a7396ca1dd542c990b6dc62f2369db74a89a9e3320d6b26a`. E2E status complete; reasons: none.

Per-item scores, retrieval IDs, cited IDs, reference IDs and PR points are in the companion JSON; no global winner is inferred.

## Limitations

- Seven out-of-corpus questions per language limit abstention inference.
- The pooled-v1 gates are frozen; v2 sweep optima are descriptive only.
- The E5 baseline saw v1; a stable API model ID cannot prove immutable weights.
