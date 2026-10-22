# Research: Embedding Model Comparison

**Date**: 2026-10-22 | **Spec**: [spec.md](./spec.md)

## 1. Fixed candidate roster and model-card rules

- **Decision**: compare exactly three dense retrievers for the first paper run. Pin the following repository revisions; record the full SHA and license with each run rather than relying on a moving `main` tag:

  | Candidate ID | Repository @ immutable revision | License | Dense size | Query / passage treatment | Length & normalization |
  |---|---|---|---:|---|---|
  | `e5-large` | `intfloat/multilingual-e5-large@3d7cfbdacd47fdda877c5cd8a79fbcc4f2a574f3` | MIT | 1024 | `query: ` / `passage: ` for retrieval, including Persian | max 512 tokens; L2-normalized |
  | `e5-base` | `intfloat/multilingual-e5-base@d128750597153bb5987e10b1c3493a34e5a4502a` | MIT | 768 | same E5 prefixes | max 512 tokens; L2-normalized |
  | `bge-m3` | `BAAI/bge-m3@5617a9f61b028005a4858fdac845db406aefb181` | MIT | 1024 dense | no query instruction required; use dense output only | max 8192 tokens; normalized dense vectors |

- **Evidence**: official [E5-large card](https://huggingface.co/intfloat/multilingual-e5-large) / [repository API](https://huggingface.co/api/models/intfloat/multilingual-e5-large); [E5-base card](https://huggingface.co/intfloat/multilingual-e5-base) / [API](https://huggingface.co/api/models/intfloat/multilingual-e5-base); [BGE-M3 card](https://huggingface.co/BAAI/bge-m3) / [API](https://huggingface.co/api/models/BAAI/bge-m3), [model pipeline](https://huggingface.co/BAAI/bge-m3/blob/main/modules.json), [tokenizer settings](https://huggingface.co/BAAI/bge-m3/blob/main/tokenizer_config.json). These are the reported revision SHAs at the time of research; download/checksum and tokenizer behavior must be smoke-tested before freezing run records.
- **Rationale**: E5-large is the operational baseline, E5-base isolates a within-family size effect, and BGE-M3 is a different multilingual family. Keep the user-selected three rather than adding a speculative fourth. Compare normalized dense similarity only; sparse/multi-vector modes of BGE-M3 would change retrieval architecture.
- **Alternatives considered**: an extra fourth model (more run cost, no first-run need); forcing E5 prefixes or 512-token limits on BGE-M3 (violates model card); comparing different index types (confounds the model comparison).

## 2. Where to run and how to reproduce

- **Decision**: canonical build and evaluation happen **sequentially on the existing Windows laptop without a GPU** (measured 15.6 GiB RAM, `torch.cuda.is_available() == False`). Load one model at a time; record device, batch size, truncation count, model revision and wall-clock timings. This corpus has 1030 chunks total (C 503, C++ 201, Python 253, Java 73), and each raw chunk is at most ~4k characters. First model download requires network access; CPU runtime for BGE-M3 must be measured, not assumed from weight size (~2.27 GB before runtime overhead).
- **Fallback**: if CPU inference cannot finish within available time/memory, Kaggle may run **the exact same CLI and pinned config** on the same hashed frozen chunks. Export only regenerated embedding/index artifacts and metadata (model revision, source hash, device, tokenizer settings); do not move `.env` or API keys. CPU/GPU floating-point scores may differ slightly: compare ID inventory/top-k and report observed deviations, not claim cross-hardware byte equality. An examiner can always recreate from sources/config; a Kaggle notebook or machine-specific path must not be a hidden requirement.
- **Alternatives considered**: Kaggle-only plan (fragile availability and extra deployment steps); loading all three models at once (unnecessary memory cost).

## 3. Shared chunks, model-scoped vectors and cache

- **Decision**: ingest each pack once. Its `chunks.jsonl`, chunk order, raw text and `chunk_id` inventory remain identical across models. Build a separate dense index for each `(pack, model revision)` from those same records, using the existing normalized-inner-product search. Preserve existing `data/index/<lang>/` as the operational E5-large default; place experimental cache/index files under an explicitly gitignored research path. Store a small tracked run manifest containing hashes of the source chunk inventory and of the model configuration. On every load, reject a mismatched revision, vector dimension, chunk order or source hash rather than silently mixing models.
- **Cache key**: hash the model repository **and revision**, model-card prefix/normalization/max-length settings, pack chunk IDs **and text in order**, and output type. Reuse a cached passage-embedding array only on an exact key match; otherwise recompute and atomically replace the cache. Cache query embeddings by model revision/settings + exact question text + query mode where it reduces repeated evaluation work. Keep caches/FAISS files regenerable and ignored; track IDs, configs and paper summaries.
- **Rationale**: requires only configuration at the embedding/retriever boundary; no new retriever algorithm, chunker or store. Hashes make resume after interrupted CPU runs reproducible.
- **Alternatives considered**: shared FAISS index with model tags (invalid across vector dimensions and dangerous for isolation); re-embedding unchanged passages for every rerun; arbitrary caching that ignores model revisions or tokenizer settings.

## 4. Calibration, measurements and inference rules

- **Decision**: use each model's scores on the **pooled four frozen v1 sets** (100 answerable / 20 out-of-corpus) to select one threshold per model by maximal balanced accuracy; ties choose the higher/conservative gate. Lock it before the fresh v2 sets are scored. The existing per-pack operational gates remain unchanged for the dashboard; research runs use their model-specific pooled gate. Log per-language v1 gate confusion counts to expose pooling artifacts. The operational E5 baseline has previously seen v1; explicitly disclose this advantage.
- **Retrieval-only pass**: compute top-5 hits and top-1 score for every question without a single LLM request. An optional end-to-end pass reuses the same selected retriever and pack-scoped citation guard with a pinned/identifiable LLM revision, unchanged prompt, `temperature=0` and top-k. If the current proxy cannot identify or honor these settings, mark end-to-end comparisons incomplete; still publish retrieval-only evidence. Temperature 0 does **not** guarantee identical generated text. Store both fixed-gate and end-to-end abstention outcomes separately.
- **Statistics**: 10,000 question-resamples with seed `20261022`, paired by question ID across models; 95% percentile intervals next to metrics, model-difference intervals adjusted across all pairs within each language as specified in FR-014. Retain the existing **macro mean of per-answer strict citation precision**, recomputing it from answered rows within every resample; report answer-count and cited-ID denominators so extra abstention cannot masquerade as precision improvement. Sweep all score cutoffs on v2 to plot OOC-positive AUROC and precision/recall **descriptively**; never choose a new gate from v2. Undefined/empty-class estimates show N/A with counts. Disclose the seven OOC questions per language and wide uncertainty; no universal winner from small slices.
- **Alternatives considered**: calibrating each language on its five v1 OOC questions (high variance); retuning v2 gates (leakage); unpaired tests despite identical questions; mixing four languages into one headline rank (violates Principle V).

## 5. Question and answer provenance

- **Decision**: author 45 new v2 questions per pack (28 in-corpus, 10 code-mixed, 7 out-of-corpus), independent of v1. Keep expected chunk IDs, reference-answer summaries and provenance (source URL/title/section/license or explicit OOC absence reason) with every item. Record evidence language from the supporting source, not from the pack name. Audit duplicates/paraphrases against v1 and validate every positive expected ID against the frozen chunk inventory before publication.
- **Alternatives considered**: copying 30 v1 items into v2 (calibration leakage); relying on general model knowledge to write reference answers (not verifiable).
