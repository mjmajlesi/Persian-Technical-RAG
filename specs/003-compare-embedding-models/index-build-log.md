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
