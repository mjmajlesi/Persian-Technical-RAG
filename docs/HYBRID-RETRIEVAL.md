# Hybrid retrieval research results

Pre-registration: [specs/004-hybrid-retrieval/spec.md](../specs/004-hybrid-retrieval/spec.md), committed before all runs. These are retrieval-only research results; no LLM calls or operational adoption decision.

## Hit@5

First five values are the 38 answerable items; the last five are the 10 mixed items. Each hybrid is compared to its corresponding official dense baseline. BM25 uses the E5-large dense gate.

| Pack | Dense E5 | Dense BGE | BM25 E5 gate | Hybrid E5 | Hybrid BGE | Mixed dense E5 | Mixed dense BGE | Mixed BM25 | Mixed hybrid E5 | Mixed hybrid BGE |
|---|---|---|---|---|---|---|---|---|---|---|
| c | 0.6842 | 0.7105 | 0.3158 | 0.4474 | 0.6316 | 0.2000 | 0.7000 | 0.0000 | 0.0000 | 0.6000 |
| cpp | 0.3421 | 0.7632 | 0.0789 | 0.1316 | 0.5526 | 0.5000 | 0.9000 | 0.1000 | 0.3000 | 0.6000 |
| python | 0.6316 | 0.6842 | 0.2895 | 0.6579 | 0.5789 | 0.7000 | 0.9000 | 1.0000 | 0.9000 | 0.9000 |
| java | 0.8684 | 1.0000 | 0.3421 | 0.6053 | 0.8158 | 0.9000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

## Dense-gate verification

Each cell compares all 45 rows with the corresponding official dense baseline. The maximum absolute top-1 score difference is shown separately; gates use the unchanged locked calibration threshold.

| Pack | Arm | Gate equal | Max absolute top-1 difference |
|---|---|---:|---:|
| c | bm25 | 45/45 | 0 |
| c | hybrid-e5-large | 45/45 | 0 |
| c | hybrid-bge-m3 | 45/45 | 0 |
| cpp | bm25 | 45/45 | 0 |
| cpp | hybrid-e5-large | 45/45 | 0 |
| cpp | hybrid-bge-m3 | 45/45 | 0 |
| python | bm25 | 45/45 | 0 |
| python | hybrid-e5-large | 45/45 | 0 |
| python | hybrid-bge-m3 | 45/45 | 0 |
| java | bm25 | 45/45 | 0 |
| java | hybrid-e5-large | 45/45 | 0 |
| java | hybrid-bge-m3 | 45/45 | 0 |

## Paired differences, hybrid minus dense

We use the equivalent of `src/eval/comparison.py`: seeded Python `random.Random(20261022)`, 10,000 samples of all 45 paired question rows with replacement, excluding out-of-corpus rows from each Hit@5 estimate, and its linearly interpolated two-sided 95% percentile interval (`_interval`). Each pack/model comparison resets the seed. Intervals are individual, not multiplicity-adjusted. Improvement requires the full interval above zero; significant regression requires it below zero; otherwise the result is inconclusive.

| Pack | Model | Difference | 95% CI | Conclusion |
|---|---|---:|---|---|
| c | e5-large | -0.2368 | [-0.3947, -0.0833] | significant regression |
| c | bge-m3 | -0.0789 | [-0.2195, +0.0541] | inconclusive |
| cpp | e5-large | -0.2105 | [-0.3429, -0.0833] | significant regression |
| cpp | bge-m3 | -0.2105 | [-0.3590, -0.0588] | significant regression |
| python | e5-large | +0.0263 | [-0.0833, +0.1429] | inconclusive |
| python | bge-m3 | -0.1053 | [-0.2162, -0.0250] | significant regression |
| java | e5-large | -0.2632 | [-0.4211, -0.1081] | significant regression |
| java | bge-m3 | -0.1842 | [-0.3125, -0.0732] | significant regression |

Each report was checked against its matching baseline for question IDs, model revision, set hash, index metadata, and locked calibration. Official dense retrieval-only reports were read without rerunning them. Run reports and baseline paths with SHA-256 are recorded below for provenance.

## Report provenance

- `c dense-e5-large: data/eval/c/reports/v2/e5-large/2026-10-25-003405-458814-c-v2-retrieval-only.json sha256=044291a879e30d84c89bcd376057f99489ba6e112743954e1cd4b14215b31aef`
- `c hybrid-e5-large: data/research/hybrid-retrieval/c/hybrid/e5-large/2026-11-01-231309-792927-c-v2-retrieval-only.json sha256=2de8fc16aefd002df912af5dd1382e033462bab03abaecefbeac857c178f1dcc`
- `c dense-bge-m3: data/eval/c/reports/v2/bge-m3/2026-10-25-003519-848745-c-v2-retrieval-only.json sha256=9bad67a2309a41dbc975da13a9ae52f1d4796510979f5bff37c235bf56e49605`
- `c hybrid-bge-m3: data/research/hybrid-retrieval/c/hybrid/bge-m3/2026-11-01-231724-358575-c-v2-retrieval-only.json sha256=3dc52391ee7e3c9ddc6da50558d0d6e36626822dc0815b9b7fe418ddd4c09022`
- `c bm25: data/research/hybrid-retrieval/c/bm25/e5-large/2026-11-01-231228-093136-c-v2-retrieval-only.json sha256=5d0425a0e0ef0dfd147e751f44b04b23a0e237c2a2725b39d223ca63adf9380e`
- `cpp dense-e5-large: data/eval/cpp/reports/v2/e5-large/2026-10-25-010053-231441-cpp-v2-retrieval-only.json sha256=68cf5d882b23b3161cdd162ea8d8d74f46ded6d44192d6e221455358d2ef3173`
- `cpp hybrid-e5-large: data/research/hybrid-retrieval/cpp/hybrid/e5-large/2026-11-01-231422-525677-cpp-v2-retrieval-only.json sha256=e0c90cc164a303e5d771a5a454a24c3d5ac7072321d0a6c9cd98887aebfb3b78`
- `cpp dense-bge-m3: data/eval/cpp/reports/v2/bge-m3/2026-10-25-010207-328273-cpp-v2-retrieval-only.json sha256=1b964f2d221bb98619edce3e70143411e9ef98e0482cba1caa4605ccbc2c6e28`
- `cpp hybrid-bge-m3: data/research/hybrid-retrieval/cpp/hybrid/bge-m3/2026-11-01-231755-348500-cpp-v2-retrieval-only.json sha256=db2b9f21508fe4a81df4b1f3cb6252216c9be6c1888bc28242a1c6a2aa36f3de`
- `cpp bm25: data/research/hybrid-retrieval/cpp/bm25/e5-large/2026-11-01-231346-897784-cpp-v2-retrieval-only.json sha256=a14ec03070ad7f2110093bf584b4c2546eee37cbaabd457eff5afa5175ab5eac`
- `python dense-e5-large: data/eval/python/reports/v2/e5-large/2026-10-25-011006-858513-python-v2-retrieval-only.json sha256=b1703c5547e876095e4e1f7ef50eeede5a1e9d4d50241161054ccb341324669b`
- `python hybrid-e5-large: data/research/hybrid-retrieval/python/hybrid/e5-large/2026-11-01-231539-083661-python-v2-retrieval-only.json sha256=072298c2fc37298fe13c8c05d6624bb89d355df3f56286ae9912b964cff921ba`
- `python dense-bge-m3: data/eval/python/reports/v2/bge-m3/2026-10-25-011114-840748-python-v2-retrieval-only.json sha256=6abf252036c726b49a915eda2e5016e0a3dbaa279791958771415d31654cad69`
- `python hybrid-bge-m3: data/research/hybrid-retrieval/python/hybrid/bge-m3/2026-11-01-231836-158029-python-v2-retrieval-only.json sha256=104028bb12c1ee812d3f083fe80bc481e549117d6823e53f7e2a42f1782c9211`
- `python bm25: data/research/hybrid-retrieval/python/bm25/e5-large/2026-11-01-231501-131161-python-v2-retrieval-only.json sha256=0eca533abbc5e6efa2587137a7249a755de73dd5ed7c9eff58e1bba00fa75a3f`
- `java dense-e5-large: data/eval/java/reports/v2/e5-large/2026-10-25-011642-343421-java-v2-retrieval-only.json sha256=4cc2ab92531d0b4f540dac2e1766c79e498f12a140bff380b0f3f00ddea6dc5a`
- `java hybrid-e5-large: data/research/hybrid-retrieval/java/hybrid/e5-large/2026-11-01-231650-975393-java-v2-retrieval-only.json sha256=c95a830b71b3a102c0ab07226fb9f47fa8ce7698a523f7f4976a73061ae2ee2a`
- `java dense-bge-m3: data/eval/java/reports/v2/bge-m3/2026-10-25-011757-879447-java-v2-retrieval-only.json sha256=15ee673e75822587b9876b3c3d690a64599b4b1cb09dbab97af6bc6b5b2a08fe`
- `java hybrid-bge-m3: data/research/hybrid-retrieval/java/hybrid/bge-m3/2026-11-01-231913-663601-java-v2-retrieval-only.json sha256=6e3a9621d9c2724cda59b7ccbe92afc37cb68db362d31c1eb0b19e357a2727eb`
- `java bm25: data/research/hybrid-retrieval/java/bm25/e5-large/2026-11-01-231615-183935-java-v2-retrieval-only.json sha256=0eb587bfeb6fa788baab0706a4c05d07731c0b8d1d5ec2e3186f8a8147f3af3e`
