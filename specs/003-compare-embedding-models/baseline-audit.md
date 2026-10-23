# Baseline Audit: Feature 003 (T001)

**Date**: 2026-10-23 | **Branch**: `003-compare-embedding-models` (created from `main` at commit `c714a34`; no work discarded)

## Purpose

Freeze and record the byte-level baseline of the four frozen v1 evaluation sets, canonical chunk inventories and manifests **before** any feature 003 implementation. These hashes must remain unchanged through T053 (recorded again in the final validation of T053).

## 1. Prerequisite verification

| Check | Result |
|---|---|
| Branch `003-compare-embedding-models` created from `main` | OK (`git switch -c`; working tree clean, commit `c714a34`) |
| Four `data/index/<lang>/` indices present (`faiss.index`, `chunks.jsonl`, `ids.json`) | OK for c/cpp/python/java; 1030 chunks total (503/201/253/73) |
| Four `data/corpus/manifest.<lang>.json` manifests present | OK; snapshots c=2026-09-23, cpp/python/java=2026-10-16 |
| T027 marked `[X]` in `specs/002-multi-language-dashboard/tasks.md` | OK (32 passed, 1 FAISS deprecation warning, recorded 2026-10-22) |
| `pytest tests/ -q` on the 003 branch | PASSED: **32 passed, 1 warning** in 0:09:11 (per-pack FAISS/Numpy deprecation warning only) |

## 2. Frozen v1 evaluation sets (inventory verification)

All four sets verified: **30 items each**, exactly **20 in-corpus / 5 mixed / 5 out-of-corpus**, every out-of-corpus item has empty `expected_source_ids`, and item IDs are sequential with the expected prefixes (`C-`, `CPP-`, `PY-`, `JV-`).

| Pack | File | SHA-256 | Version | Items (in/mixed/OOC) |
|---|---|---|---|---|
| c | `data/eval/c/eval-set.c.v1.json` | `55a69ac80a2e7bc1db11aae2ded7c346b5372ebeba9619f7e9cfd181b3083e88` | c-v1 | 30 (20/5/5) |
| cpp | `data/eval/cpp/eval-set.cpp.v1.json` | `087cf8a163563bfa9765b769e939b08622d10efed43f825646ba67291a01f533` | cpp-v1 | 30 (20/5/5) |
| python | `data/eval/python/eval-set.python.v1.json` | `a4b364891578dd9023a70994d2e351fce5c83b0eb5fe7f2b7ef7a388b2b3f22a` | python-v1 | 30 (20/5/5) |
| java | `data/eval/java/eval-set.java.v1.json` | `60d015014299f3d29d8e42cda61d78b5aa3a560a1881799aff7dafbd3ded3725` | java-v1 | 30 (20/5/5) |

## 3. Canonical chunk inventories and manifests (baseline hashes)

These are the frozen in-project files every research index must read via a validated hash. `ids.json` order equals `chunks.jsonl` order for every pack.

| Pack | chunks.jsonl SHA-256 | Chunk count | manifest.<lang>.json SHA-256 | Snapshot |
|---|---|---:|---|---|
| c | `8b2bb61d8a853280bc400d2ea1e4b8bd6bfb76c5a1106bbc99ab2a08ddcfad74` | 503 | `1dbe049e86faf9bb74cdccf6f33a7cba8eac19895af161ea5d7efcd2e6dc00c6` | 2026-09-23 |
| cpp | `c22bd9fb1e37a9f3e8cf1d2b747c8d9a9e6b050d7798817feb35f20fa0444366` | 201 | `24c1d9962909633fd9e5b66b64582377e71356750ec6923a659762761c1c9908` | 2026-10-16 |
| python | `0b7afc4c24a6c34e10d797b9c2bab6ebd68f7c32636442c17eba280226d07649` | 253 | `a601c0628d112fd40a7ba9405faf6189e74575f7fd810960ef138d18ec8a3650` | 2026-10-16 |
| java | `dd119c50203b76016275ae95513f145fac6005a95a4752a69f4dd0c35b63c9a8` | 73 | `32167e0df69405a2ad31776429613cf7fce9042c4f32be0b507b8bc31ba1258f` | 2026-10-16 |

## 4. Ordered `chunk_id` lists (index order; `data/index/<lang>/ids.json` matches `chunks.jsonl` order)

Correctness check: `ids.json` matched chunk order for all four packs (`ids_json_matches_chunks_order = true`).
The lists below are the **complete ordered inventories** used for index-isolation checks in T009/T031-T033 and for the T053 final unchanged-hash comparison.

### Pack `c` — 503 chunk_ids

- fa-vars-types-operators#s01-c01 fa-vars-types-operators#s02-c01 fa-vars-types-operators#s03-c01 fa-vars-types-operators#s04-c01 fa-vars-types-operators#s05-c01 fa-vars-types-operators#s06-c01 fa-vars-types-operators#s07-c01 fa-vars-types-operators#s08-c01 fa-vars-types-operators#s09-c01 fa-vars-types-operators#s10-c01
- fa-vars-types-operators#s11-c01 fa-vars-types-operators#s12-c01 fa-vars-types-operators#s13-c01 fa-vars-types-operators#s14-c01 fa-vars-types-operators#s15-c01 fa-vars-types-operators#s16-c01 fa-vars-types-operators#s17-c01 fa-vars-types-operators#s18-c01 fa-vars-types-operators#s19-c01 fa-vars-types-operators#s20-c01
- fa-vars-types-operators#s21-c01 fa-vars-types-operators#s22-c01 fa-vars-types-operators#s23-c01 fa-io-formatting#s01-c01 fa-io-formatting#s02-c01 fa-io-formatting#s03-c01 fa-io-formatting#s04-c01 fa-io-formatting#s05-c01 fa-io-formatting#s06-c01 fa-io-formatting#s07-c01
- fa-io-formatting#s08-c01 fa-io-formatting#s09-c01 fa-io-formatting#s10-c01 fa-io-formatting#s11-c01 fa-io-formatting#s12-c01 fa-io-formatting#s13-c01 fa-io-formatting#s14-c01 fa-io-formatting#s15-c01 fa-selection-iteration#s01-c01 fa-selection-iteration#s02-c01
- fa-selection-iteration#s03-c01 fa-selection-iteration#s04-c01 fa-selection-iteration#s05-c01 fa-selection-iteration#s06-c01 fa-selection-iteration#s07-c01 fa-selection-iteration#s08-c01 fa-selection-iteration#s09-c01 fa-selection-iteration#s10-c01 fa-selection-iteration#s11-c01 fa-selection-iteration#s12-c01
- fa-selection-iteration#s13-c01 fa-selection-iteration#s14-c01 fa-selection-iteration#s15-c01 fa-selection-iteration#s16-c01 fa-selection-iteration#s17-c01 fa-selection-iteration#s18-c01 fa-selection-iteration#s19-c01 fa-selection-iteration#s20-c01 fa-selection-iteration#s21-c01 fa-selection-iteration#s22-c01
- fa-functions#s01-c01 fa-functions#s02-c01 fa-functions#s03-c01 fa-functions#s04-c01 fa-functions#s05-c01 fa-functions#s06-c01 fa-functions#s07-c01 fa-functions#s08-c01 fa-functions#s09-c01 fa-functions#s10-c01
- fa-functions#s11-c01 fa-functions#s12-c01 fa-functions#s13-c01 fa-functions#s14-c01 fa-functions#s15-c01 fa-functions#s16-c01 fa-functions#s17-c01 fa-functions#s18-c01 fa-functions#s19-c01 fa-functions#s20-c01
- fa-functions#s21-c01 fa-functions#s22-c01 fa-arrays#s01-c01 fa-arrays#s02-c01 fa-arrays#s03-c01 fa-arrays#s04-c01 fa-arrays#s05-c01 fa-arrays#s06-c01 fa-arrays#s07-c01 fa-arrays#s08-c01
- fa-arrays#s09-c01 fa-arrays#s10-c01 fa-arrays#s11-c01 fa-arrays#s12-c01 fa-arrays#s13-c01 fa-arrays#s14-c01 fa-arrays#s15-c01 fa-arrays#s16-c01 fa-arrays#s17-c01 fa-arrays#s18-c01
- fa-arrays#s19-c01 fa-arrays#s20-c01 fa-arrays#s21-c01 fa-arrays#s22-c01 fa-pointers#s01-c01 fa-pointers#s02-c01 fa-pointers#s03-c01 fa-pointers#s04-c01 fa-pointers#s05-c01 fa-pointers#s06-c01
- fa-pointers#s07-c01 fa-pointers#s08-c01 fa-pointers#s09-c01 fa-pointers#s10-c01 fa-pointers#s11-c01 fa-pointers#s12-c01 fa-pointers#s13-c01 fa-pointers#s14-c01 fa-pointers#s15-c01 fa-pointers#s16-c01
- fa-pointers#s17-c01 fa-pointers#s18-c01 fa-pointers#s19-c01 fa-strings#s01-c01 fa-strings#s02-c01 fa-strings#s03-c01 fa-strings#s04-c01 fa-strings#s05-c01 fa-strings#s06-c01 fa-strings#s07-c01
- fa-strings#s08-c01 fa-strings#s09-c01 fa-strings#s10-c01 fa-strings#s11-c01 fa-strings#s12-c01 fa-strings#s13-c01 fa-strings#s14-c01 fa-strings#s15-c01 fa-strings#s16-c01 fa-strings#s17-c01
- fa-strings#s18-c01 fa-structs-unions-enums#s01-c01 fa-structs-unions-enums#s02-c01 fa-structs-unions-enums#s03-c01 fa-structs-unions-enums#s04-c01 fa-structs-unions-enums#s05-c01 fa-structs-unions-enums#s06-c01 fa-structs-unions-enums#s07-c01 fa-structs-unions-enums#s08-c01 fa-structs-unions-enums#s09-c01
- fa-structs-unions-enums#s10-c01 fa-structs-unions-enums#s11-c01 fa-structs-unions-enums#s12-c01 fa-structs-unions-enums#s13-c01 fa-structs-unions-enums#s14-c01 fa-files#s01-c01 fa-files#s02-c01 fa-files#s03-c01 fa-files#s04-c01 fa-files#s05-c01
- fa-files#s06-c01 fa-files#s07-c01 fa-files#s08-c01 fa-files#s09-c01 fa-files#s10-c01 fa-files#s11-c01 fa-files#s12-c01 fa-dynamic-memory#s01-c01 fa-dynamic-memory#s02-c01 fa-dynamic-memory#s03-c01
- fa-dynamic-memory#s04-c01 fa-dynamic-memory#s05-c01 fa-dynamic-memory#s06-c01 fa-dynamic-memory#s07-c01 fa-dynamic-memory#s08-c01 fa-dynamic-memory#s09-c01 fa-dynamic-memory#s10-c01 fa-dynamic-memory#s11-c01 fa-dynamic-memory#s12-c01 fa-dynamic-memory#s13-c01
- fa-dynamic-memory#s14-c01 fa-dynamic-memory#s15-c01 fa-preprocessor#s01-c01 fa-preprocessor#s02-c01 fa-preprocessor#s03-c01 fa-preprocessor#s04-c01 fa-preprocessor#s05-c01 fa-preprocessor#s06-c01 fa-preprocessor#s07-c01 fa-preprocessor#s08-c01
- fa-preprocessor#s09-c01 fa-preprocessor#s10-c01 fa-preprocessor#s11-c01 fa-preprocessor#s12-c01 fa-appendix-numbers#s01-c01 fa-appendix-numbers#s02-c01 fa-appendix-numbers#s03-c01 fa-appendix-numbers#s04-c01 fa-appendix-numbers#s05-c01 fa-appendix-numbers#s06-c01
- fa-appendix-numbers#s07-c01 cppref-malloc#s01-c01 cppref-malloc#s02-c01 cppref-malloc#s03-c01 cppref-malloc#s04-c01 cppref-malloc#s05-c01 cppref-malloc#s06-c01 cppref-malloc#s07-c01 cppref-free#s01-c01 cppref-free#s02-c01
- cppref-free#s03-c01 cppref-free#s04-c01 cppref-free#s05-c01 cppref-free#s06-c01 cppref-free#s07-c01 cppref-free#s08-c01 cppref-calloc#s01-c01 cppref-calloc#s02-c01 cppref-calloc#s03-c01 cppref-calloc#s04-c01
- cppref-calloc#s05-c01 cppref-calloc#s06-c01 cppref-calloc#s07-c01 cppref-calloc#s08-c01 cppref-realloc#s01-c01 cppref-realloc#s02-c01 cppref-realloc#s03-c01 cppref-realloc#s04-c01 cppref-realloc#s05-c01 cppref-realloc#s06-c01
- cppref-realloc#s07-c01 cppref-realloc#s08-c01 cppref-strlen#s01-c01 cppref-strlen#s02-c01 cppref-strlen#s03-c01 cppref-strlen#s04-c01 cppref-strlen#s05-c01 cppref-strlen#s06-c01 cppref-strlen#s07-c01 cppref-strcpy#s01-c01
- cppref-strcpy#s02-c01 cppref-strcpy#s03-c01 cppref-strcpy#s04-c01 cppref-strcpy#s05-c01 cppref-strcpy#s06-c01 cppref-strcpy#s07-c01 cppref-strcat#s01-c01 cppref-strcat#s02-c01 cppref-strcat#s03-c01 cppref-strcat#s04-c01
- cppref-strcat#s05-c01 cppref-strcat#s06-c01 cppref-strcat#s07-c01 cppref-strcmp#s01-c01 cppref-strcmp#s02-c01 cppref-strcmp#s03-c01 cppref-strcmp#s04-c01 cppref-strcmp#s05-c01 cppref-strcmp#s06-c01 cppref-strcmp#s07-c01
- cppref-strcmp#s08-c01 cppref-strstr#s01-c01 cppref-strstr#s02-c01 cppref-strstr#s03-c01 cppref-strstr#s04-c01 cppref-strstr#s05-c01 cppref-strstr#s06-c01 cppref-strstr#s07-c01 cppref-memcpy#s01-c01 cppref-memcpy#s02-c01
- cppref-memcpy#s03-c01 cppref-memcpy#s04-c01 cppref-memcpy#s05-c01 cppref-memcpy#s06-c01 cppref-memcpy#s07-c01 cppref-memset#s01-c01 cppref-memset#s02-c01 cppref-memset#s03-c01 cppref-memset#s04-c01 cppref-memset#s05-c01
- cppref-memset#s06-c01 cppref-memset#s07-c01 cppref-printf#s01-c01 cppref-printf#s02-c01 cppref-printf#s03-c01 cppref-printf#s03-c02 cppref-printf#s04-c01 cppref-printf#s05-c01 cppref-printf#s06-c01 cppref-printf#s06-c02
- cppref-printf#s07-c01 cppref-printf#s08-c01 cppref-printf#s09-c01 cppref-printf#s10-c01 cppref-scanf#s01-c01 cppref-scanf#s02-c01 cppref-scanf#s03-c01 cppref-scanf#s03-c02 cppref-scanf#s03-c03 cppref-scanf#s04-c01
- cppref-scanf#s05-c01 cppref-scanf#s06-c01 cppref-scanf#s07-c01 cppref-scanf#s08-c01 cppref-fopen#s01-c01 cppref-fopen#s02-c01 cppref-fopen#s03-c01 cppref-fopen#s04-c01 cppref-fopen#s05-c01 cppref-fopen#s06-c01
- cppref-fopen#s07-c01 cppref-fopen#s08-c01 cppref-fclose#s01-c01 cppref-fclose#s02-c01 cppref-fclose#s03-c01 cppref-fclose#s04-c01 cppref-fclose#s05-c01 cppref-fclose#s06-c01 cppref-fclose#s07-c01 cppref-fread#s01-c01
- cppref-fread#s02-c01 cppref-fread#s03-c01 cppref-fread#s04-c01 cppref-fread#s05-c01 cppref-fread#s06-c01 cppref-fread#s07-c01 cppref-fwrite#s01-c01 cppref-fwrite#s02-c01 cppref-fwrite#s03-c01 cppref-fwrite#s04-c01
- cppref-fwrite#s05-c01 cppref-fwrite#s06-c01 cppref-fwrite#s07-c01 cppref-fgets#s01-c01 cppref-fgets#s02-c01 cppref-fgets#s03-c01 cppref-fgets#s04-c01 cppref-fgets#s05-c01 cppref-fgets#s06-c01 cppref-fgets#s07-c01
- cppref-fgets#s08-c01 cppref-qsort#s01-c01 cppref-qsort#s02-c01 cppref-qsort#s03-c01 cppref-qsort#s04-c01 cppref-qsort#s05-c01 cppref-qsort#s06-c01 cppref-qsort#s07-c01 cppref-rand#s01-c01 cppref-rand#s02-c01
- cppref-rand#s03-c01 cppref-rand#s04-c01 cppref-rand#s05-c01 cppref-rand#s06-c01 cppref-rand#s07-c01 cppref-rand#s08-c01 cppref-pointer#s01-c01 cppref-pointer#s02-c01 cppref-pointer#s03-c01 cppref-pointer#s04-c01
- cppref-pointer#s05-c01 cppref-pointer#s06-c01 cppref-pointer#s07-c01 cppref-pointer#s08-c01 cppref-pointer#s09-c01 cppref-pointer#s10-c01 cppref-pointer#s11-c01 glibc-unconstrained-allocation#s01-c01 glibc-unconstrained-allocation#s02-c01 glibc-basic-allocation#s01-c01
- glibc-basic-allocation#s02-c01 glibc-malloc-examples#s01-c01 glibc-malloc-examples#s02-c01 glibc-standard-streams#s01-c01 glibc-standard-streams#s02-c01 glibc-formatted-output#s01-c01 glibc-formatted-output#s02-c01 cppref-arithmetic-types#s01-c01 cppref-arithmetic-types#s02-c01 cppref-arithmetic-types#s03-c01
- cppref-arithmetic-types#s04-c01 cppref-arithmetic-types#s05-c01 cppref-arithmetic-types#s06-c01 cppref-arithmetic-types#s07-c01 cppref-arithmetic-types#s08-c01 cppref-arithmetic-types#s08-c02 cppref-arithmetic-types#s09-c01 cppref-arithmetic-types#s10-c01 cppref-arithmetic-types#s11-c01 cppref-arithmetic-types#s12-c01
- cppref-sizeof#s01-c01 cppref-sizeof#s02-c01 cppref-sizeof#s03-c01 cppref-sizeof#s04-c01 cppref-sizeof#s05-c01 cppref-sizeof#s06-c01 cppref-sizeof#s07-c01 cppref-sizeof#s08-c01 cppref-if#s01-c01 cppref-if#s02-c01
- cppref-if#s03-c01 cppref-if#s04-c01 cppref-if#s05-c01 cppref-if#s06-c01 cppref-if#s07-c01 cppref-if#s08-c01 cppref-if#s09-c01 cppref-switch#s01-c01 cppref-switch#s02-c01 cppref-switch#s03-c01
- cppref-switch#s04-c01 cppref-switch#s05-c01 cppref-switch#s06-c01 cppref-switch#s07-c01 cppref-switch#s08-c01 cppref-for#s01-c01 cppref-for#s02-c01 cppref-for#s03-c01 cppref-for#s04-c01 cppref-for#s05-c01
- cppref-for#s06-c01 cppref-for#s07-c01 cppref-for#s08-c01 cppref-for#s09-c01 cppref-struct#s01-c01 cppref-struct#s02-c01 cppref-struct#s03-c01 cppref-struct#s04-c01 cppref-struct#s04-c02 cppref-struct#s05-c01
- cppref-struct#s06-c01 cppref-struct#s07-c01 cppref-struct#s08-c01 cppref-struct#s09-c01 cppref-struct#s10-c01 cppref-struct#s11-c01 cppref-byte-strings#s01-c01 cppref-byte-strings#s02-c01 cppref-byte-strings#s03-c01 cppref-byte-strings#s03-c02
- cppref-byte-strings#s03-c03 cppref-byte-strings#s04-c01 cppref-byte-strings#s05-c01 cppref-conditional#s01-c01 cppref-conditional#s02-c01 cppref-conditional#s03-c01 cppref-conditional#s04-c01 cppref-conditional#s05-c01 cppref-conditional#s06-c01 cppref-conditional#s07-c01
- cppref-conditional#s08-c01 cppref-conditional#s09-c01 cppref-conditional#s10-c01 cppref-conditional#s11-c01 cppref-isalpha#s01-c01 cppref-isalpha#s02-c01 cppref-isalpha#s03-c01 cppref-isalpha#s04-c01 cppref-isalpha#s05-c01 cppref-isalpha#s06-c01
- cppref-isalpha#s07-c01 cppref-isalpha#s07-c02 cppref-fseek#s01-c01 cppref-fseek#s02-c01 cppref-fseek#s03-c01 cppref-fseek#s04-c01 cppref-fseek#s05-c01 cppref-fseek#s06-c01 cppref-fseek#s07-c01 cppref-fseek#s08-c01
- cppref-bsearch#s01-c01 cppref-bsearch#s02-c01 cppref-bsearch#s03-c01 cppref-bsearch#s04-c01 cppref-bsearch#s05-c01 cppref-bsearch#s06-c01 cppref-bsearch#s07-c01 cppref-atoi#s01-c01 cppref-atoi#s02-c01 cppref-atoi#s03-c01
- cppref-atoi#s04-c01 cppref-atoi#s05-c01 cppref-atoi#s06-c01 cppref-atoi#s07-c01 cppref-atoi#s08-c01 cppref-replace#s01-c01 cppref-replace#s02-c01 cppref-replace#s03-c01 cppref-replace#s04-c01 cppref-replace#s05-c01
- cppref-replace#s06-c01 cppref-replace#s07-c01 cppref-replace#s07-c02 cppref-replace#s08-c01 cppref-replace#s09-c01 cppref-replace#s10-c01 cppref-replace#s11-c01 cppref-operator-precedence#s01-c01 cppref-operator-precedence#s02-c01 cppref-operator-precedence#s02-c02
- cppref-operator-precedence#s03-c01 cppref-operator-precedence#s04-c01 cppref-operator-precedence#s05-c01

### Pack `cpp` — 201 chunk_ids

- cpp-notes-intro#s01-c01 cpp-notes-intro#s02-c01 cpp-notes-intro#s03-c01 cpp-notes-intro#s04-c01 cpp-notes-intro#s05-c01 cpp-notes-intro#s06-c01 cpp-notes-intro#s07-c01 cpp-notes-intro#s08-c01 cpp-notes-intro#s09-c01 cpp-notes-intro#s10-c01
- cpp-notes-intro#s11-c01 cppref-cpp-vector#s01-c01 cppref-cpp-vector#s02-c01 cppref-cpp-vector#s03-c01 cppref-cpp-vector#s04-c01 cppref-cpp-vector#s05-c01 cppref-cpp-vector#s06-c01 cppref-cpp-vector#s07-c01 cppref-cpp-vector#s08-c01 cppref-cpp-vector#s09-c01
- cppref-cpp-vector#s10-c01 cppref-cpp-vector#s11-c01 cppref-cpp-vector#s12-c01 cppref-cpp-vector#s13-c01 cppref-cpp-string#s01-c01 cppref-cpp-string#s02-c01 cppref-cpp-string#s03-c01 cppref-cpp-string#s04-c01 cppref-cpp-string#s05-c01 cppref-cpp-string#s06-c01
- cppref-cpp-string#s07-c01 cppref-cpp-string#s07-c02 cppref-cpp-string#s08-c01 cppref-cpp-string#s09-c01 cppref-cpp-string#s10-c01 cppref-cpp-string#s11-c01 cppref-cpp-string#s12-c01 cppref-cpp-string#s13-c01 cppref-cpp-string#s14-c01 cppref-cpp-string#s15-c01
- cppref-cpp-cout#s01-c01 cppref-cpp-cout#s02-c01 cppref-cpp-cout#s03-c01 cppref-cpp-cout#s04-c01 cppref-cpp-cout#s05-c01 cppref-cpp-class#s01-c01 cppref-cpp-class#s02-c01 cppref-cpp-class#s03-c01 cppref-cpp-class#s04-c01 cppref-cpp-class#s05-c01
- cppref-cpp-class#s06-c01 cppref-cpp-class#s07-c01 cppref-cpp-class#s08-c01 cppref-cpp-class#s09-c01 cppref-cpp-constructor#s01-c01 cppref-cpp-constructor#s02-c01 cppref-cpp-constructor#s03-c01 cppref-cpp-constructor#s04-c01 cppref-cpp-constructor#s05-c01 cppref-cpp-constructor#s06-c01
- cppref-cpp-constructor#s07-c01 cppref-cpp-constructor#s08-c01 cppref-cpp-constructor#s09-c01 cppref-cpp-constructor#s10-c01 cppref-cpp-constructor#s11-c01 cppref-cpp-constructor#s12-c01 cppref-cpp-constructor#s13-c01 cppref-cpp-constructor#s14-c01 cppref-cpp-namespace#s01-c01 cppref-cpp-namespace#s02-c01
- cppref-cpp-namespace#s03-c01 cppref-cpp-namespace#s04-c01 cppref-cpp-namespace#s04-c02 cppref-cpp-namespace#s05-c01 cppref-cpp-namespace#s06-c01 cppref-cpp-namespace#s07-c01 cppref-cpp-namespace#s07-c02 cppref-cpp-namespace#s08-c01 cppref-cpp-namespace#s08-c02 cppref-cpp-namespace#s09-c01
- cppref-cpp-namespace#s10-c01 cppref-cpp-namespace#s11-c01 cppref-cpp-namespace#s12-c01 cppref-cpp-namespace#s13-c01 cppref-cpp-reference#s01-c01 cppref-cpp-reference#s02-c01 cppref-cpp-reference#s03-c01 cppref-cpp-reference#s04-c01 cppref-cpp-reference#s05-c01 cppref-cpp-reference#s06-c01
- cppref-cpp-reference#s07-c01 cppref-cpp-reference#s08-c01 cppref-cpp-reference#s09-c01 cppref-cpp-reference#s10-c01 cppref-cpp-reference#s11-c01 cppref-cpp-reference#s12-c01 cppref-cpp-reference#s13-c01 cppref-cpp-function#s01-c01 cppref-cpp-function#s02-c01 cppref-cpp-function#s03-c01
- cppref-cpp-function#s03-c02 cppref-cpp-function#s04-c01 cppref-cpp-function#s04-c02 cppref-cpp-function#s05-c01 cppref-cpp-function#s05-c02 cppref-cpp-function#s06-c01 cppref-cpp-function#s07-c01 cppref-cpp-function#s08-c01 cppref-cpp-function#s09-c01 cppref-cpp-function#s10-c01
- cppref-cpp-function#s11-c01 cppref-cpp-function#s11-c02 cppref-cpp-function#s12-c01 cppref-cpp-function#s13-c01 cppref-cpp-function#s14-c01 cppref-cpp-function#s15-c01 cppref-cpp-function#s16-c01 cppref-cpp-function#s17-c01 cppref-cpp-function#s18-c01 cppref-cpp-function#s19-c01
- cppref-cpp-function#s20-c01 cppref-cpp-function#s21-c01 cppref-cpp-function#s22-c01 cppref-cpp-function#s23-c01 cppref-cpp-function#s24-c01 cppref-cpp-function#s25-c01 cppref-cpp-operators#s01-c01 cppref-cpp-operators#s02-c01 cppref-cpp-operators#s03-c01 cppref-cpp-operators#s04-c01
- cppref-cpp-operators#s05-c01 cppref-cpp-operators#s06-c01 cppref-cpp-operators#s07-c01 cppref-cpp-operators#s08-c01 cppref-cpp-operators#s09-c01 cppref-cpp-operators#s10-c01 cppref-cpp-operators#s11-c01 cppref-cpp-operators#s12-c01 cppref-cpp-operators#s13-c01 cppref-cpp-operators#s14-c01
- cppref-cpp-operators#s15-c01 cppref-cpp-operators#s16-c01 cppref-cpp-operators#s17-c01 cppref-cpp-operators#s18-c01 cppref-cpp-operators#s19-c01 cppref-cpp-operators#s20-c01 cppref-cpp-operators#s21-c01 cppref-cpp-operators#s22-c01 cppref-cpp-operators#s23-c01 cppref-cpp-auto#s01-c01
- cppref-cpp-auto#s02-c01 cppref-cpp-auto#s03-c01 cppref-cpp-auto#s04-c01 cppref-cpp-auto#s05-c01 cppref-cpp-auto#s06-c01 cppref-cpp-auto#s07-c01 cppref-cpp-auto#s08-c01 cppref-cpp-auto#s09-c01 cppref-cpp-auto#s10-c01 cppref-cpp-auto#s11-c01
- cppref-cpp-auto#s12-c01 cppref-cpp-auto#s13-c01 cppref-cpp-auto#s14-c01 cppref-cpp-auto#s15-c01 cppref-cpp-range-for#s01-c01 cppref-cpp-range-for#s02-c01 cppref-cpp-range-for#s03-c01 cppref-cpp-range-for#s04-c01 cppref-cpp-range-for#s05-c01 cppref-cpp-range-for#s06-c01
- cppref-cpp-range-for#s07-c01 cppref-cpp-range-for#s08-c01 cppref-cpp-range-for#s09-c01 cppref-cpp-range-for#s10-c01 cppref-cpp-overload#s01-c01 cppref-cpp-overload#s02-c01 cppref-cpp-overload#s03-c01 cppref-cpp-overload#s04-c01 cppref-cpp-overload#s05-c01 cppref-cpp-overload#s06-c01
- cppref-cpp-overload#s06-c02 cppref-cpp-overload#s07-c01 cppref-cpp-overload#s08-c01 cppref-cpp-overload#s09-c01 cppref-cpp-overload#s10-c01 cppref-cpp-overload#s11-c01 cppref-cpp-overload#s12-c01 cppref-cpp-overload#s13-c01 cppref-cpp-overload#s14-c01 cppref-cpp-overload#s15-c01
- cppref-cpp-overload#s16-c01 cppref-cpp-overload#s16-c02 cppref-cpp-overload#s17-c01 cppref-cpp-overload#s17-c02 cppref-cpp-overload#s17-c03 cppref-cpp-overload#s18-c01 cppref-cpp-overload#s18-c02 cppref-cpp-overload#s19-c01 cppref-cpp-overload#s19-c02 cppref-cpp-overload#s20-c01
- cppref-cpp-overload#s21-c01

### Pack `python` — 253 chunk_ids

- pyref-tutorial-introduction#s01-c01 pyref-tutorial-introduction#s02-c01 pyref-tutorial-introduction#s03-c01 pyref-tutorial-introduction#s04-c01 pyref-tutorial-introduction#s05-c01 pyref-tutorial-introduction#s05-c02 pyref-tutorial-introduction#s05-c03 pyref-tutorial-introduction#s06-c01 pyref-tutorial-introduction#s06-c02 pyref-tutorial-introduction#s07-c01
- pyref-tutorial-introduction#s07-c02 pyref-tutorial-controlflow#s01-c01 pyref-tutorial-controlflow#s02-c01 pyref-tutorial-controlflow#s03-c01 pyref-tutorial-controlflow#s04-c01 pyref-tutorial-controlflow#s05-c01 pyref-tutorial-controlflow#s06-c01 pyref-tutorial-controlflow#s07-c01 pyref-tutorial-controlflow#s08-c01 pyref-tutorial-controlflow#s09-c01
- pyref-tutorial-controlflow#s09-c02 pyref-tutorial-controlflow#s10-c01 pyref-tutorial-controlflow#s10-c02 pyref-tutorial-controlflow#s11-c01 pyref-tutorial-controlflow#s12-c01 pyref-tutorial-controlflow#s13-c01 pyref-tutorial-controlflow#s14-c01 pyref-tutorial-controlflow#s15-c01 pyref-tutorial-controlflow#s16-c01 pyref-tutorial-controlflow#s17-c01
- pyref-tutorial-controlflow#s18-c01 pyref-tutorial-controlflow#s19-c01 pyref-tutorial-controlflow#s20-c01 pyref-tutorial-controlflow#s21-c01 pyref-tutorial-controlflow#s22-c01 pyref-tutorial-controlflow#s23-c01 pyref-tutorial-controlflow#s24-c01 pyref-tutorial-controlflow#s25-c01 pyref-tutorial-datastructures#s01-c01 pyref-tutorial-datastructures#s02-c01
- pyref-tutorial-datastructures#s03-c01 pyref-tutorial-datastructures#s04-c01 pyref-tutorial-datastructures#s05-c01 pyref-tutorial-datastructures#s06-c01 pyref-tutorial-datastructures#s06-c02 pyref-tutorial-datastructures#s07-c01 pyref-tutorial-datastructures#s08-c01 pyref-tutorial-datastructures#s09-c01 pyref-tutorial-datastructures#s10-c01 pyref-tutorial-datastructures#s11-c01
- pyref-tutorial-datastructures#s12-c01 pyref-tutorial-datastructures#s12-c02 pyref-tutorial-datastructures#s13-c01 pyref-tutorial-datastructures#s14-c01 pyref-tutorial-datastructures#s15-c01 pyref-tutorial-classes#s01-c01 pyref-tutorial-classes#s02-c01 pyref-tutorial-classes#s03-c01 pyref-tutorial-classes#s04-c01 pyref-tutorial-classes#s04-c02
- pyref-tutorial-classes#s05-c01 pyref-tutorial-classes#s06-c01 pyref-tutorial-classes#s07-c01 pyref-tutorial-classes#s08-c01 pyref-tutorial-classes#s09-c01 pyref-tutorial-classes#s10-c01 pyref-tutorial-classes#s11-c01 pyref-tutorial-classes#s12-c01 pyref-tutorial-classes#s12-c02 pyref-tutorial-classes#s13-c01
- pyref-tutorial-classes#s14-c01 pyref-tutorial-classes#s15-c01 pyref-tutorial-classes#s16-c01 pyref-tutorial-classes#s17-c01 pyref-tutorial-classes#s18-c01 pyref-tutorial-classes#s19-c01 pyref-tutorial-errors#s01-c01 pyref-tutorial-errors#s02-c01 pyref-tutorial-errors#s03-c01 pyref-tutorial-errors#s04-c01
- pyref-tutorial-errors#s05-c01 pyref-tutorial-errors#s05-c02 pyref-tutorial-errors#s06-c01 pyref-tutorial-errors#s07-c01 pyref-tutorial-errors#s08-c01 pyref-tutorial-errors#s09-c01 pyref-tutorial-errors#s10-c01 pyref-tutorial-errors#s11-c01 pyref-tutorial-errors#s12-c01 pyref-tutorial-inputoutput#s01-c01
- pyref-tutorial-inputoutput#s02-c01 pyref-tutorial-inputoutput#s03-c01 pyref-tutorial-inputoutput#s03-c02 pyref-tutorial-inputoutput#s04-c01 pyref-tutorial-inputoutput#s05-c01 pyref-tutorial-inputoutput#s06-c01 pyref-tutorial-inputoutput#s07-c01 pyref-tutorial-inputoutput#s08-c01 pyref-tutorial-inputoutput#s09-c01 pyref-tutorial-inputoutput#s09-c02
- pyref-tutorial-inputoutput#s10-c01 pyref-library-functions#s01-c01 pyref-library-functions#s02-c01 pyref-library-functions#s02-c02 pyref-library-functions#s02-c03 pyref-library-functions#s02-c04 pyref-library-functions#s02-c05 pyref-library-functions#s02-c06 pyref-library-functions#s02-c07 pyref-library-functions#s02-c08
- pyref-library-functions#s02-c09 pyref-library-functions#s02-c10 pyref-library-functions#s02-c11 pyref-library-functions#s02-c12 pyref-library-functions#s02-c13 pyref-library-functions#s02-c14 pyref-library-functions#s02-c15 pyref-library-functions#s02-c16 pyref-library-functions#s02-c17 pyref-library-functions#s02-c18
- pyref-library-functions#s02-c19 pyref-library-functions#s02-c20 pyref-library-functions#s02-c21 pyref-library-functions#s02-c22 pyref-library-functions#s02-c23 pyref-library-functions#s02-c24 pyref-library-functions#s02-c25 pyref-library-functions#s02-c26 pyref-library-functions#s02-c27 pyref-library-functions#s02-c28
- pyref-library-functions#s02-c29 pyref-library-functions#s02-c30 pyref-library-stdtypes#s01-c01 pyref-library-stdtypes#s02-c01 pyref-library-stdtypes#s03-c01 pyref-library-stdtypes#s04-c01 pyref-library-stdtypes#s05-c01 pyref-library-stdtypes#s06-c01 pyref-library-stdtypes#s06-c02 pyref-library-stdtypes#s07-c01
- pyref-library-stdtypes#s08-c01 pyref-library-stdtypes#s08-c02 pyref-library-stdtypes#s09-c01 pyref-library-stdtypes#s10-c01 pyref-library-stdtypes#s11-c01 pyref-library-stdtypes#s11-c02 pyref-library-stdtypes#s12-c01 pyref-library-stdtypes#s13-c01 pyref-library-stdtypes#s14-c01 pyref-library-stdtypes#s15-c01
- pyref-library-stdtypes#s16-c01 pyref-library-stdtypes#s17-c01 pyref-library-stdtypes#s17-c02 pyref-library-stdtypes#s18-c01 pyref-library-stdtypes#s18-c02 pyref-library-stdtypes#s19-c01 pyref-library-stdtypes#s20-c01 pyref-library-stdtypes#s20-c02 pyref-library-stdtypes#s20-c03 pyref-library-stdtypes#s21-c01
- pyref-library-stdtypes#s22-c01 pyref-library-stdtypes#s23-c01 pyref-library-stdtypes#s24-c01 pyref-library-stdtypes#s25-c01 pyref-library-stdtypes#s25-c02 pyref-library-stdtypes#s26-c01 pyref-library-stdtypes#s27-c01 pyref-library-stdtypes#s28-c01 pyref-library-stdtypes#s28-c02 pyref-library-stdtypes#s28-c03
- pyref-library-stdtypes#s28-c04 pyref-library-stdtypes#s28-c05 pyref-library-stdtypes#s28-c06 pyref-library-stdtypes#s28-c07 pyref-library-stdtypes#s28-c08 pyref-library-stdtypes#s28-c09 pyref-library-stdtypes#s28-c10 pyref-library-stdtypes#s29-c01 pyref-library-stdtypes#s30-c01 pyref-library-stdtypes#s31-c01
- pyref-library-stdtypes#s32-c01 pyref-library-stdtypes#s33-c01 pyref-library-stdtypes#s34-c01 pyref-library-stdtypes#s34-c02 pyref-library-stdtypes#s35-c01 pyref-library-stdtypes#s36-c01 pyref-library-stdtypes#s36-c02 pyref-library-stdtypes#s37-c01 pyref-library-stdtypes#s37-c02 pyref-library-stdtypes#s38-c01
- pyref-library-stdtypes#s38-c02 pyref-library-stdtypes#s38-c03 pyref-library-stdtypes#s38-c04 pyref-library-stdtypes#s38-c05 pyref-library-stdtypes#s38-c06 pyref-library-stdtypes#s38-c07 pyref-library-stdtypes#s38-c08 pyref-library-stdtypes#s38-c09 pyref-library-stdtypes#s39-c01 pyref-library-stdtypes#s39-c02
- pyref-library-stdtypes#s40-c01 pyref-library-stdtypes#s40-c02 pyref-library-stdtypes#s40-c03 pyref-library-stdtypes#s40-c04 pyref-library-stdtypes#s40-c05 pyref-library-stdtypes#s41-c01 pyref-library-stdtypes#s41-c02 pyref-library-stdtypes#s41-c03 pyref-library-stdtypes#s42-c01 pyref-library-stdtypes#s42-c02
- pyref-library-stdtypes#s42-c03 pyref-library-stdtypes#s42-c04 pyref-library-stdtypes#s43-c01 pyref-library-stdtypes#s44-c01 pyref-library-stdtypes#s45-c01 pyref-library-stdtypes#s46-c01 pyref-library-stdtypes#s47-c01 pyref-library-stdtypes#s47-c02 pyref-library-stdtypes#s48-c01 pyref-library-stdtypes#s49-c01
- pyref-library-stdtypes#s50-c01 pyref-library-stdtypes#s51-c01 pyref-library-stdtypes#s52-c01 pyref-library-stdtypes#s53-c01 pyref-library-stdtypes#s54-c01 pyref-library-stdtypes#s55-c01 pyref-library-stdtypes#s56-c01 pyref-library-stdtypes#s57-c01 pyref-library-stdtypes#s58-c01 pyref-library-stdtypes#s59-c01
- pyref-library-stdtypes#s60-c01 pyref-library-stdtypes#s61-c01 pyref-library-stdtypes#s62-c01 pyref-library-stdtypes#s63-c01 pyref-library-stdtypes#s64-c01 pyref-library-stdtypes#s65-c01 pyref-library-stdtypes#s66-c01 pyref-library-exceptions#s01-c01 pyref-library-exceptions#s02-c01 pyref-library-exceptions#s03-c01
- pyref-library-exceptions#s04-c01 pyref-library-exceptions#s05-c01 pyref-library-exceptions#s06-c01 pyref-library-exceptions#s06-c02 pyref-library-exceptions#s06-c03 pyref-library-exceptions#s06-c04 pyref-library-exceptions#s06-c05 pyref-library-exceptions#s06-c06 pyref-library-exceptions#s07-c01 pyref-library-exceptions#s08-c01
- pyref-library-exceptions#s09-c01 pyref-library-exceptions#s09-c02 pyref-library-exceptions#s10-c01

### Pack `java` — 73 chunk_ids

- javaref-variables#s01-c01 javaref-variables#s02-c01 javaref-variables#s02-c02 javaref-variables#s03-c01 javaref-operators#s01-c01 javaref-operators#s02-c01 javaref-arrays#s01-c01 javaref-arrays#s02-c01 javaref-arrays#s03-c01 javaref-arrays#s04-c01
- javaref-arrays#s05-c01 javaref-arrays#s06-c01 javaref-if#s01-c01 javaref-if#s02-c01 javaref-if#s03-c01 javaref-for#s01-c01 javaref-for#s02-c01 javaref-oop-concepts#s01-c01 javaref-oop-concepts#s02-c01 javaref-oop-concepts#s03-c01
- javaref-oop-concepts#s04-c01 javaref-oop-concepts#s05-c01 javaref-oop-concepts#s06-c01 javaref-oop-concepts#s07-c01 javaref-oop-concepts#s08-c01 javaref-classes#s01-c01 javaref-classes#s02-c01 javaref-objects#s01-c01 javaref-objects#s02-c01 javaref-subclasses#s01-c01
- javaref-subclasses#s02-c01 javaref-subclasses#s03-c01 javaref-subclasses#s04-c01 javaref-subclasses#s05-c01 javaref-subclasses#s06-c01 javaref-subclasses#s07-c01 javaref-override#s01-c01 javaref-override#s02-c01 javaref-override#s03-c01 javaref-override#s04-c01
- javaref-override#s04-c02 javaref-override#s05-c01 javaref-override#s06-c01 javaref-interface-def#s01-c01 javaref-interface-def#s02-c01 javaref-interface-def#s03-c01 javaref-strings#s01-c01 javaref-strings#s02-c01 javaref-strings#s03-c01 javaref-strings#s04-c01
- javaref-strings#s05-c01 javaref-strings#s06-c01 javaref-exceptions#s01-c01 javaref-exceptions#s02-c01 javaref-exceptions-handling#s01-c01 javaref-exceptions-handling#s02-c01 javaref-fileio#s01-c01 javaref-fileio#s02-c01 javaref-fileio#s03-c01 javaref-fileio#s04-c01
- javaref-fileio#s05-c01 javaref-fileio#s06-c01 javaref-fileio#s07-c01 javaref-fileio#s08-c01 javaref-fileio#s09-c01 javaref-fileio#s10-c01 javaref-fileio#s11-c01 javaref-fileio#s12-c01 javaref-fileio#s13-c01 javaref-collections-intro#s01-c01
- javaref-collections-intro#s02-c01 javaref-collections-intro#s03-c01 javaref-collections-intro#s04-c01
