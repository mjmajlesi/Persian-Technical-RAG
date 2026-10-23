# Contract: model selection, indexing and cache integrity

**Status**: planned interface; not yet implemented. This contract extends the existing CLIs without changing their no-flag defaults.

## Registered candidates

Tracked registry: `data/eval/model-comparison/models.json` (planned). Required keys per entry: `model_key`, `repository`, `revision_sha`, `license`, `model_card_url`, `dimension`, `query_prefix`, `passage_prefix`, `normalize`, `max_tokens`. Fixed initial values:

| Key | Repository and revision | License | Dimension | Query / passage prefixes | Normalize | Max tokens |
|---|---|---|---:|---|---|---:|
| `e5-large` | `intfloat/multilingual-e5-large@3d7cfbdacd47fdda877c5cd8a79fbcc4f2a574f3` | MIT | 1024 | `query: ` / `passage: ` | yes | 512 |
| `e5-base` | `intfloat/multilingual-e5-base@d128750597153bb5987e10b1c3493a34e5a4502a` | MIT | 768 | `query: ` / `passage: ` | yes | 512 |
| `bge-m3` | `BAAI/bge-m3@5617a9f61b028005a4858fdac845db406aefb181` | MIT | 1024 dense | none / none | yes | 8192 |

Never substitute a floating revision, change prefix policy across runs, or mix vector dimensions. Cache-key input is the full pinned model/settings record plus SHA-256 of ordered `(chunk_id, text)` pairs, not merely the manifest date. Record observed token truncation count per pack. If a model-card smoke test contradicts the settings above, correct the registry **before** running the benchmark and record the rationale; do not retrofit settings after v2 results are seen.

## CLI surface (to implement)

```powershell
# Existing behavior unchanged: builds the operational e5-large index.
.\.venv\Scripts\python -m src.index build --lang c

# Research build, same frozen chunks, only model and index destination change.
.\.venv\Scripts\python -m src.index build --lang c --model bge-m3
```

`--lang` accepts exactly `c|cpp|python|java`; `--model` accepts registered keys and defaults to the operational E5-large setting. With an explicit research model, write to gitignored `data/research/embedding-compare/<model>/<lang>/` (only regenerable FAISS binaries and embedding caches are ignored there) and leave `data/index/<lang>/` untouched. The research index **reads the canonical pack's frozen `chunks.jsonl` in place** from `data/index/<lang>/` and validates its SHA-256 plus ordered `chunk_id` list against the recorded baseline before serving; it never copies or re-chunks chunk text. The research index manifest carries model/card settings hash, canonical chunk-source hash, ordered IDs and vector dimension; load must fail on any mismatch, unknown revision or wrong dimension. Cache reuse requires an exact key match; a failed build must not overwrite a valid previous index. Config files, small metadata, calibration records and **official final JSON/Markdown reports are versioned and committed**; weights, array caches, FAISS binaries and credentials are not.

**Examiner check**: for a given pack, hash `chunks.jsonl` and its ordered IDs before/after all three model builds; the hash must stay unchanged and the research manifest must reference the same canonical hash. Build twice; the second run reports a cache hit and the same ordered IDs/top-5 on stable hardware. On Kaggle the identical registry/input hashes and CLI are required; note device and floating-point differences rather than assuming byte-equal indices.
