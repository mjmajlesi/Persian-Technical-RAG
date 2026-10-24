# Research Index Build Log (Feature 003)

## T031: e5-large across four frozen packs (2026-10-24)

Model: `intfloat/multilingual-e5-large@3d7cfbdacd47fdda877c5cd8a79fbcc4f2a574f3`, dense normalized dimension 1024. Command for each row, **run twice**: `.\.venv\Scripts\python -m src.index build --lang <pack> --model e5-large`. Output is scoped to `data/research/embedding-compare/e5-large/<pack>/`; the canonical `data/index/<pack>/chunks.jsonl` is read in place.

These four research directories **already contained valid caches and indices before T031** (from earlier feature work). Both T031 CLI invocations for every pack were verified cache hits, not fresh model encodes. The old `index-meta.json` values for C/C++/Python had `cache_hit=false` from their original builds; the new metadata truthfully records the current hits. No cache or FAISS binary is staged. A verified hit still rebuilds the FAISS file from the cached vectors; its SHA-256 was unchanged across both runs.

| Pack | Canonical chunks / ordered IDs | Canonical chunks SHA-256 = T001 | Dimension | Truncated passages (cached) | CLI run 1 / run 2 | Research FAISS SHA-256 |
|---|---:|---|---:|---:|---|---|
| c | 503 | `8b2bb61d8a853280bc400d2ea1e4b8bd6bfb76c5a1106bbc99ab2a08ddcfad74` | 1024 | 44 | hit / hit (0.46s / 0.36s) | `11a871d5ad8949f52ef90ce0478683020751939381cf35b14a33b40f0c3fe2a8` |
| cpp | 201 | `c22bd9fb1e37a9f3e8cf1d2b747c8d9a9e6b050d7798817feb35f20fa0444366` | 1024 | 37 | hit / hit (0.34s / 0.34s) | `de80d13a085258ee9c1215351f21f52ae9dc42b4bcd18d1edb270e807f35e9e7` |
| python | 253 | `0b7afc4c24a6c34e10d797b9c2bab6ebd68f7c32636442c17eba280226d07649` | 1024 | 134 | hit / hit (0.38s / 0.34s) | `c199bbea962f4e6da47330b72b6f2df6bc4b3699cafbec751bc7cb0b6fde8077` |
| java | 73 | `dd119c50203b76016275ae95513f145fac6005a95a4752a69f4dd0c35b63c9a8` | 1024 | 10 | hit / hit (0.40s / 0.34s) | `b92f058b5ec8fa724bd3f9b955faa8df528df8c4b2b7f0a9c9c28613db35aa94` |

Verification: every metadata record has `status=ready`, pinned revision, correct pack, count, dimension, canonical and index hashes, `cache_hit=true`, and cached truncation count. Both `ids.json` and loaded `Retriever` index agree exactly with the canonical chunk order/count, with no foreign IDs. Before/after SHA-256 of every file in all four operational `data/index/<pack>/` directories, all four v1 sets and all four manifests matched; the canonical chunk hashes also match T001. The no-`--model` `Retriever` loaded all four operational indices and a real C question returned five scoped hits without changing its index hash (31.74s including model load). No LLM calls, gate changes, corpus rewrite or v2 scoring.

## T032: e5-base across four frozen packs (2026-10-24)

Model: `intfloat/multilingual-e5-base@d128750597153bb5987e10b1c3493a34e5a4502a`, dense normalized dimension 768. Command: `.\.venv\Scripts\python -m src.index build --lang <pack> --model e5-base`, separately per pack on CPU. These four directories did **not** exist before T032: the first run encoded fresh passages (`cache_hit=false`); the second run per pack reused the exact fingerprint (`cache_hit=true`) without encoding. Only the small `cache.json`, `ids.json` and `index-meta.json` are versionable; FAISS binaries and `.npy` vectors remain ignored.

| Pack | Chunks / ordered IDs | Canonical chunks SHA-256 = T001 | Dimension | Truncated / total | First build CPU wall time | Second run | Research FAISS SHA-256 |
|---|---:|---|---:|---:|---|---|---|
| c | 503 | `8b2bb61d8a853280bc400d2ea1e4b8bd6bfb76c5a1106bbc99ab2a08ddcfad74` | 768 | 44/503 | not captured by timer (successful fresh build) | hit | `06760dda3b8e22b3ad77f0891555c3e395eccfb72b921d4189343246cb0e7cb4` |
| cpp | 201 | `c22bd9fb1e37a9f3e8cf1d2b747c8d9a9e6b050d7798817feb35f20fa0444366` | 768 | 37/201 | 126.43s | hit (0.51s) | `e463ad18b4759d845fbe736b038b597d7402bf712265b65945cb2f529a2e76bd` |
| python | 253 | `0b7afc4c24a6c34e10d797b9c2bab6ebd68f7c32636442c17eba280226d07649` | 768 | 134/253 | 214.29s | hit (0.47s) | `a3240f6704816bd7ed61164a7d7933f3348badf93285ec8c7d74acc17dad5fc4` |
| java | 73 | `dd119c50203b76016275ae95513f145fac6005a95a4752a69f4dd0c35b63c9a8` | 768 | 10/73 | 67.35s | hit | `0aff9a42a405a0cbf408c3d572ed3c0feea99f4b7570fda5d350ebb1620f828f` |

Memory context: Windows reported 15.64 GiB physical RAM, 3.37 GiB free before builds and 2.94 GiB free afterwards. This is **not** a peak-RSS measurement; no peak or model-specific RAM usage is claimed. Every pack ran in a separate process so model weights were not resident simultaneously. Disk free after builds was 86.81 GiB. Tokenizer warnings for untruncated 618/526/690/712-token passages arose during the deliberate pre-truncation count; real encoding was limited to 512 tokens and the recorded per-pack truncation counts are shown above.

Verification: fresh first-run misses were observed for all four packs, then second-run hits; `status=ready`, pinned revision, 768-dimensional FAISS index, checksum of both `.npy` vectors and FAISS, normalized reconstructed vectors, exact ordered canonical IDs and successful scoped `Retriever` load were checked. Canonical chunks, v1 and manifests still match their pack-specific T001 SHA-256. `git status` showed no changes outside new `e5-base` metadata (until this log/task update); the operational `data/index/` and existing `e5-large` research indices were not edited. No LLM calls or gate changes.

## T033: bge-m3 dense across four frozen packs (2026-10-24)

Model: `BAAI/bge-m3@5617a9f61b028005a4858fdac845db406aefb181` (MIT), dense normalized dimension 1024, 8192-token limit and **no query/passage instructions** per its pinned card and T030 real CPU smoke test. Command: `.\.venv\Scripts\python -m src.index build --lang <pack> --model bge-m3`, one pack/process at a time on CPU with `OMP_NUM_THREADS=4`, `MKL_NUM_THREADS=4`, and `CUDA_VISIBLE_DEVICES` empty. All four directories were absent before T033; first runs freshly encoded passages (cache miss), and second runs used the cached vectors (cache hit). No Kaggle/GPU fallback was needed.

| Pack | Chunks / ordered IDs | Canonical chunks SHA-256 = T001 | Dimension | Truncated / total | First build wall time | Second run | Research FAISS SHA-256 |
|---|---:|---|---:|---:|---|---|---|
| c | 503 | `8b2bb61d8a853280bc400d2ea1e4b8bd6bfb76c5a1106bbc99ab2a08ddcfad74` | 1024 | 0/503 | 1586.09s | hit | `974d536dcecb56023658238f29dd42e56f89dee1575b2291d9c75ab206d91f78` |
| cpp | 201 | `c22bd9fb1e37a9f3e8cf1d2b747c8d9a9e6b050d7798817feb35f20fa0444366` | 1024 | 0/201 | 756.28s | hit | `da08b046d7948a6f68aab4034031d096867f42609095bfe14cff4783fbbb3d9c` |
| python | 253 | `0b7afc4c24a6c34e10d797b9c2bab6ebd68f7c32636442c17eba280226d07649` | 1024 | 0/253 | 1816.17s | hit | `a16373bf201fc063d5f7fe148efaac37b8021950953e98bd433dabe8e62ee0e6` |
| java | 73 | `dd119c50203b76016275ae95513f145fac6005a95a4752a69f4dd0c35b63c9a8` | 1024 | 0/73 | 395.35s | hit | `3f75233e8794b27ba1d0c6cf9b24d8eb51366680bc372fc2c3dcee3fff97ec33` |

Card/tokenizer preflight measured longest passages at C=1207, C++=960, Python=1329, Java=962 tokens, all below 8192. Windows reported 15.64 GiB physical RAM and 3.05 GiB free before the first build; that is a snapshot, **not a peak-RSS measurement**. Per-process execution avoided keeping two model instances in RAM. All four completed locally without resource errors.

Verification: each metadata record has `status=ready`, pinned revision, correct pack/count, 1024 dimensions, zero truncations and `cache_hit=true` after its second run. Research FAISS hashes, ignored `.npy` cache checksums, normalized reconstructed vectors, exact ordered IDs and scoped `Retriever` loads passed. Canonical chunk hashes, frozen v1 files and manifests still match their pack-specific T001 rows. Existing `e5-large` and `e5-base` indices remained valid with the same canonical hashes and their FAISS checksums. Only new `bge-m3` metadata (plus this log/task marker) is versionable; FAISS binaries and embedding caches remain ignored. No LLM calls, operational gate changes, or v2 scoring occurred.
