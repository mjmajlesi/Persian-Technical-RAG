# v2 Evaluation-Set Audit (T029)

**Date:** 2026-10-24 | **Baseline:** `baseline-audit.md` (T001) | **Status:** awaiting T029 user checkpoint; no v2 benchmark run/publication claimed.

## Full-set findings

- `validate_set(path, pack_id=..., complete=True)` returned `complete` and zero review flags for all four sets. All **180/180** items have reviewed authorship metadata, distinct global item IDs, distinct Persian question text, and no literal v1/chunk question copying or near-v1 wording flagged by T020.
- All **152/152 answerable** items have a grounded summary, same-pack chunk ID(s), chunk-derived evidence language and provenance entries matching the manifest (`chunk_id`, `source_id`, section, title, origin, snapshot, license). All **28/28 OOC** items have empty source/provenance lists, `none` evidence language, a reason for abstention and review metadata. Thus 180/180 items have an audited provenance *status*: 152 positive records plus 28 explicit evidence-absence records, not fabricated OOC citations.
- All 180 IDs and normalized question strings are unique across packs. SHA-256 of every v1 file, canonical chunks file and manifest matches its exact pack row in the T001 baseline byte-for-byte. None of these frozen inputs or the operational path was edited.
- Content spot checks compared answer scenarios to cited chunks and verified distinctive OOC API terms against frozen pack text. In Python, incidental `depends` and `session` occurrences refer to ordinary prose/interpreter sessions, not FastAPI `Depends` or SQLAlchemy `Session`; an incidental `import` in C++ does not document `export module`. Keyword search alone cannot prove semantic absence: the accepted pack-specific user reviews remain the manual grounding control.

## By-pack summary

Evidence counts are `fa/en/mixed/none`; hashes are for the corresponding v1 file and equal the T001 record. Full questions, answer summaries, source metadata and licenses remain in `data/eval/<pack>/eval-set.<pack>.v2.json`.

| Pack | Items (in/mixed/OOC) | Positive provenance + abstentions | Evidence fa/en/mixed/none | Distinct sources | v1 SHA-256 = T001 |
|---|---|---|---|---:|---|
| c | 45 (28/10/7) | 38 + 7 abstentions | 0/12/26/7 | 22 | `55a69ac80a2e7bc1db11aae2ded7c346b5372ebeba9619f7e9cfd181b3083e88` |
| cpp | 45 (28/10/7) | 38 + 7 abstentions | 0/36/2/7 | 13 | `087cf8a163563bfa9765b769e939b08622d10efed43f825646ba67291a01f533` |
| python | 45 (28/10/7) | 38 + 7 abstentions | 0/38/0/7 | 9 | `a4b364891578dd9023a70994d2e351fce5c83b0eb5fe7f2b7ef7a388b2b3f22a` |
| java | 45 (28/10/7) | 38 + 7 abstentions | 0/38/0/7 | 13 | `60d015014299f3d29d8e42cda61d78b5aa3a560a1881799aff7dafbd3ded3725` |

## Issues and disposition

| Issue | Status | Disposition |
|---|---|---|
| Invalid counts, IDs, evidence labels or provenance/license | Cleared | Four complete validations; 152 positive citation records and 28 absent-evidence records checked. |
| Literal or near-v1 question copying | Cleared | T020 flags none; 180 distinct IDs/questions and no literal chunk-question copies. Summary similarity was also spot-checked against v1. |
| OOC keyword collisions with unrelated prose | Cleared | `Depends`/`Session` in Python and `import` in C++ do not supply the requested framework/module API contracts. |
| Open issues | **None identified** | Any newly identified semantic doubt must return the affected item to user review before publication. |

## Per-item ledger

Each row references the full question and summary/abstain reason in its pack JSON. For positive items the chunk ID resolves to that JSON item's title, origin, section, snapshot and license. `Reviewed` means `review_status=reviewed` with reviewer and date.

### `c` - 45 items

| Item ID | Type | Evidence language | Chunk(s) or abstention evidence | Review |
|---|---|---|---|---|
| C2-001 | in-corpus | mixed | `fa-vars-types-operators#s02-c01` | Reviewed |
| C2-002 | in-corpus | mixed | `fa-vars-types-operators#s14-c01` | Reviewed |
| C2-003 | in-corpus | mixed | `fa-vars-types-operators#s17-c01` | Reviewed |
| C2-004 | in-corpus | mixed | `fa-vars-types-operators#s19-c01` | Reviewed |
| C2-005 | in-corpus | mixed | `fa-io-formatting#s05-c01` | Reviewed |
| C2-006 | in-corpus | mixed | `fa-io-formatting#s06-c01` | Reviewed |
| C2-007 | in-corpus | mixed | `fa-io-formatting#s09-c01` | Reviewed |
| C2-008 | in-corpus | mixed | `fa-io-formatting#s12-c01` | Reviewed |
| C2-009 | in-corpus | mixed | `fa-io-formatting#s14-c01` | Reviewed |
| C2-010 | in-corpus | mixed | `fa-selection-iteration#s14-c01` | Reviewed |
| C2-011 | in-corpus | mixed | `fa-selection-iteration#s17-c01` | Reviewed |
| C2-012 | in-corpus | mixed | `fa-selection-iteration#s13-c01` | Reviewed |
| C2-013 | in-corpus | mixed | `fa-arrays#s04-c01` | Reviewed |
| C2-014 | in-corpus | mixed | `fa-arrays#s11-c01` | Reviewed |
| C2-015 | in-corpus | mixed | `fa-arrays#s17-c01` | Reviewed |
| C2-016 | in-corpus | mixed | `fa-pointers#s05-c01` | Reviewed |
| C2-017 | in-corpus | mixed | `fa-pointers#s10-c01` | Reviewed |
| C2-018 | in-corpus | mixed | `fa-pointers#s16-c01` | Reviewed |
| C2-019 | in-corpus | mixed | `fa-pointers#s18-c01` | Reviewed |
| C2-020 | in-corpus | mixed | `fa-structs-unions-enums#s03-c01` | Reviewed |
| C2-021 | in-corpus | mixed | `fa-structs-unions-enums#s09-c01` | Reviewed |
| C2-022 | in-corpus | mixed | `fa-strings#s04-c01` | Reviewed |
| C2-023 | in-corpus | mixed | `fa-files#s07-c01` | Reviewed |
| C2-024 | in-corpus | mixed | `fa-dynamic-memory#s07-c01` | Reviewed |
| C2-025 | in-corpus | mixed | `fa-dynamic-memory#s11-c01` | Reviewed |
| C2-026 | in-corpus | mixed | `fa-preprocessor#s10-c01` | Reviewed |
| C2-027 | in-corpus | en | `cppref-memcpy#s04-c01` | Reviewed |
| C2-028 | in-corpus | en | `cppref-fclose#s02-c01` | Reviewed |
| C2-029 | mixed | en | `cppref-printf#s03-c01` | Reviewed |
| C2-030 | mixed | en | `cppref-fgets#s02-c01` | Reviewed |
| C2-031 | mixed | en | `cppref-strstr#s04-c01` | Reviewed |
| C2-032 | mixed | en | `cppref-qsort#s04-c01` | Reviewed |
| C2-033 | mixed | en | `cppref-bsearch#s02-c01` | Reviewed |
| C2-034 | mixed | en | `cppref-isalpha#s02-c01` | Reviewed |
| C2-035 | mixed | en | `cppref-fwrite#s04-c01` | Reviewed |
| C2-036 | mixed | en | `cppref-realloc#s02-c01` | Reviewed |
| C2-037 | mixed | en | `cppref-strcmp#s04-c01` | Reviewed |
| C2-038 | mixed | en | `cppref-memset#s04-c01` | Reviewed |
| C2-039 | out-of-corpus | none | No source; explicit abstain_reason | Reviewed |
| C2-040 | out-of-corpus | none | No source; explicit abstain_reason | Reviewed |
| C2-041 | out-of-corpus | none | No source; explicit abstain_reason | Reviewed |
| C2-042 | out-of-corpus | none | No source; explicit abstain_reason | Reviewed |
| C2-043 | out-of-corpus | none | No source; explicit abstain_reason | Reviewed |
| C2-044 | out-of-corpus | none | No source; explicit abstain_reason | Reviewed |
| C2-045 | out-of-corpus | none | No source; explicit abstain_reason | Reviewed |

### `cpp` - 45 items

| Item ID | Type | Evidence language | Chunk(s) or abstention evidence | Review |
|---|---|---|---|---|
| CPP2-001 | in-corpus | mixed | `cpp-notes-intro#s02-c01` | Reviewed |
| CPP2-002 | in-corpus | mixed | `cpp-notes-intro#s03-c01` | Reviewed |
| CPP2-003 | in-corpus | en | `cppref-cpp-vector#s02-c01` | Reviewed |
| CPP2-004 | in-corpus | en | `cppref-cpp-vector#s04-c01` | Reviewed |
| CPP2-005 | in-corpus | en | `cppref-cpp-vector#s02-c01` | Reviewed |
| CPP2-006 | in-corpus | en | `cppref-cpp-string#s04-c01` | Reviewed |
| CPP2-007 | in-corpus | en | `cppref-cpp-string#s07-c02` | Reviewed |
| CPP2-008 | in-corpus | en | `cppref-cpp-string#s09-c01` | Reviewed |
| CPP2-009 | in-corpus | en | `cppref-cpp-cout#s02-c01` | Reviewed |
| CPP2-010 | in-corpus | en | `cppref-cpp-class#s05-c01` | Reviewed |
| CPP2-011 | in-corpus | en | `cppref-cpp-class#s06-c01` | Reviewed |
| CPP2-012 | in-corpus | en | `cppref-cpp-constructor#s05-c01` | Reviewed |
| CPP2-013 | in-corpus | en | `cppref-cpp-constructor#s09-c01` | Reviewed |
| CPP2-014 | in-corpus | en | `cppref-cpp-namespace#s05-c01` | Reviewed |
| CPP2-015 | in-corpus | en | `cppref-cpp-namespace#s06-c01` | Reviewed |
| CPP2-016 | in-corpus | en | `cppref-cpp-namespace#s07-c01` | Reviewed |
| CPP2-017 | in-corpus | en | `cppref-cpp-reference#s04-c01` | Reviewed |
| CPP2-018 | in-corpus | en | `cppref-cpp-reference#s06-c01` | Reviewed |
| CPP2-019 | in-corpus | en | `cppref-cpp-reference#s08-c01` | Reviewed |
| CPP2-020 | in-corpus | en | `cppref-cpp-function#s12-c01` | Reviewed |
| CPP2-021 | in-corpus | en | `cppref-cpp-function#s13-c01` | Reviewed |
| CPP2-022 | in-corpus | en | `cppref-cpp-function#s16-c01` | Reviewed |
| CPP2-023 | in-corpus | en | `cppref-cpp-operators#s06-c01` | Reviewed |
| CPP2-024 | in-corpus | en | `cppref-cpp-operators#s11-c01` | Reviewed |
| CPP2-025 | in-corpus | en | `cppref-cpp-auto#s03-c01` | Reviewed |
| CPP2-026 | in-corpus | en | `cppref-cpp-auto#s08-c01` | Reviewed |
| CPP2-027 | in-corpus | en | `cppref-cpp-range-for#s05-c01` | Reviewed |
| CPP2-028 | in-corpus | en | `cppref-cpp-overload#s17-c01` | Reviewed |
| CPP2-029 | mixed | en | `cppref-cpp-vector#s05-c01` | Reviewed |
| CPP2-030 | mixed | en | `cppref-cpp-string#s07-c02` | Reviewed |
| CPP2-031 | mixed | en | `cppref-cpp-cout#s02-c01` | Reviewed |
| CPP2-032 | mixed | en | `cppref-cpp-namespace#s08-c01` | Reviewed |
| CPP2-033 | mixed | en | `cppref-cpp-reference#s07-c01` | Reviewed |
| CPP2-034 | mixed | en | `cppref-cpp-function#s04-c01` | Reviewed |
| CPP2-035 | mixed | en | `cppref-cpp-operators#s06-c01` | Reviewed |
| CPP2-036 | mixed | en | `cppref-cpp-range-for#s06-c01` | Reviewed |
| CPP2-037 | mixed | en | `cppref-cpp-overload#s11-c01` | Reviewed |
| CPP2-038 | mixed | en | `cppref-cpp-constructor#s05-c01` | Reviewed |
| CPP2-039 | out-of-corpus | none | No source; explicit abstain_reason | Reviewed |
| CPP2-040 | out-of-corpus | none | No source; explicit abstain_reason | Reviewed |
| CPP2-041 | out-of-corpus | none | No source; explicit abstain_reason | Reviewed |
| CPP2-042 | out-of-corpus | none | No source; explicit abstain_reason | Reviewed |
| CPP2-043 | out-of-corpus | none | No source; explicit abstain_reason | Reviewed |
| CPP2-044 | out-of-corpus | none | No source; explicit abstain_reason | Reviewed |
| CPP2-045 | out-of-corpus | none | No source; explicit abstain_reason | Reviewed |

### `python` - 45 items

| Item ID | Type | Evidence language | Chunk(s) or abstention evidence | Review |
|---|---|---|---|---|
| PY2-001 | in-corpus | en | `pyref-tutorial-introduction#s04-c01` | Reviewed |
| PY2-002 | in-corpus | en | `pyref-tutorial-introduction#s05-c02` | Reviewed |
| PY2-003 | in-corpus | en | `pyref-tutorial-controlflow#s12-c01` | Reviewed |
| PY2-004 | in-corpus | en | `pyref-tutorial-controlflow#s16-c01` | Reviewed |
| PY2-005 | in-corpus | en | `pyref-tutorial-controlflow#s17-c01` | Reviewed |
| PY2-006 | in-corpus | en | `pyref-tutorial-controlflow#s21-c01` | Reviewed |
| PY2-007 | in-corpus | en | `pyref-tutorial-datastructures#s05-c01` | Reviewed |
| PY2-008 | in-corpus | en | `pyref-tutorial-datastructures#s10-c01` | Reviewed |
| PY2-009 | in-corpus | en | `pyref-tutorial-datastructures#s11-c01` | Reviewed |
| PY2-010 | in-corpus | en | `pyref-tutorial-datastructures#s15-c01` | Reviewed |
| PY2-011 | in-corpus | en | `pyref-tutorial-classes#s05-c01` | Reviewed |
| PY2-012 | in-corpus | en | `pyref-tutorial-classes#s12-c01` | Reviewed |
| PY2-013 | in-corpus | en | `pyref-tutorial-classes#s15-c01` | Reviewed |
| PY2-014 | in-corpus | en | `pyref-tutorial-classes#s18-c01` | Reviewed |
| PY2-015 | in-corpus | en | `pyref-tutorial-errors#s07-c01` | Reviewed |
| PY2-016 | in-corpus | en | `pyref-tutorial-errors#s09-c01` | Reviewed |
| PY2-017 | in-corpus | en | `pyref-tutorial-errors#s11-c01` | Reviewed |
| PY2-018 | in-corpus | en | `pyref-tutorial-inputoutput#s08-c01` | Reviewed |
| PY2-019 | in-corpus | en | `pyref-tutorial-inputoutput#s09-c02` | Reviewed |
| PY2-020 | in-corpus | en | `pyref-tutorial-inputoutput#s10-c01` | Reviewed |
| PY2-021 | in-corpus | en | `pyref-library-functions#s02-c14` | Reviewed |
| PY2-022 | in-corpus | en | `pyref-library-functions#s02-c22` | Reviewed |
| PY2-023 | in-corpus | en | `pyref-library-functions#s02-c28` | Reviewed |
| PY2-024 | in-corpus | en | `pyref-library-stdtypes#s04-c01` | Reviewed |
| PY2-025 | in-corpus | en | `pyref-library-stdtypes#s20-c02` | Reviewed |
| PY2-026 | in-corpus | en | `pyref-library-stdtypes#s43-c01` | Reviewed |
| PY2-027 | in-corpus | en | `pyref-library-exceptions#s04-c01` | Reviewed |
| PY2-028 | in-corpus | en | `pyref-library-exceptions#s07-c01` | Reviewed |
| PY2-029 | mixed | en | `pyref-library-functions#s02-c01` | Reviewed |
| PY2-030 | mixed | en | `pyref-library-functions#s02-c07` | Reviewed |
| PY2-031 | mixed | en | `pyref-library-stdtypes#s42-c03` | Reviewed |
| PY2-032 | mixed | en | `pyref-library-stdtypes#s28-c06` | Reviewed |
| PY2-033 | mixed | en | `pyref-library-stdtypes#s36-c01` | Reviewed |
| PY2-034 | mixed | en | `pyref-library-stdtypes#s40-c01` | Reviewed |
| PY2-035 | mixed | en | `pyref-library-stdtypes#s25-c01` | Reviewed |
| PY2-036 | mixed | en | `pyref-library-exceptions#s09-c01` | Reviewed |
| PY2-037 | mixed | en | `pyref-library-stdtypes#s12-c01` | Reviewed |
| PY2-038 | mixed | en | `pyref-library-stdtypes#s28-c09` | Reviewed |
| PY2-039 | out-of-corpus | none | No source; explicit abstain_reason | Reviewed |
| PY2-040 | out-of-corpus | none | No source; explicit abstain_reason | Reviewed |
| PY2-041 | out-of-corpus | none | No source; explicit abstain_reason | Reviewed |
| PY2-042 | out-of-corpus | none | No source; explicit abstain_reason | Reviewed |
| PY2-043 | out-of-corpus | none | No source; explicit abstain_reason | Reviewed |
| PY2-044 | out-of-corpus | none | No source; explicit abstain_reason | Reviewed |
| PY2-045 | out-of-corpus | none | No source; explicit abstain_reason | Reviewed |

### `java` - 45 items

| Item ID | Type | Evidence language | Chunk(s) or abstention evidence | Review |
|---|---|---|---|---|
| JV2-001 | in-corpus | en | `javaref-variables#s02-c01` | Reviewed |
| JV2-002 | in-corpus | en | `javaref-variables#s02-c02` | Reviewed |
| JV2-003 | in-corpus | en | `javaref-operators#s02-c01` | Reviewed |
| JV2-004 | in-corpus | en | `javaref-arrays#s03-c01` | Reviewed |
| JV2-005 | in-corpus | en | `javaref-arrays#s06-c01` | Reviewed |
| JV2-006 | in-corpus | en | `javaref-if#s02-c01` | Reviewed |
| JV2-007 | in-corpus | en | `javaref-for#s02-c01` | Reviewed |
| JV2-008 | in-corpus | en | `javaref-classes#s02-c01` | Reviewed |
| JV2-009 | in-corpus | en | `javaref-subclasses#s03-c01` | Reviewed |
| JV2-010 | in-corpus | en | `javaref-subclasses#s05-c01` | Reviewed |
| JV2-011 | in-corpus | en | `javaref-subclasses#s07-c01` | Reviewed |
| JV2-012 | in-corpus | en | `javaref-override#s03-c01` | Reviewed |
| JV2-013 | in-corpus | en | `javaref-override#s05-c01` | Reviewed |
| JV2-014 | in-corpus | en | `javaref-override#s04-c01` | Reviewed |
| JV2-015 | in-corpus | en | `javaref-interface-def#s03-c01` | Reviewed |
| JV2-016 | in-corpus | en | `javaref-strings#s03-c01` | Reviewed |
| JV2-017 | in-corpus | en | `javaref-strings#s05-c01` | Reviewed |
| JV2-018 | in-corpus | en | `javaref-exceptions#s02-c01` | Reviewed |
| JV2-019 | in-corpus | en | `javaref-fileio#s03-c01` | Reviewed |
| JV2-020 | in-corpus | en | `javaref-fileio#s05-c01` | Reviewed |
| JV2-021 | in-corpus | en | `javaref-fileio#s06-c01` | Reviewed |
| JV2-022 | in-corpus | en | `javaref-fileio#s08-c01` | Reviewed |
| JV2-023 | in-corpus | en | `javaref-fileio#s09-c01` | Reviewed |
| JV2-024 | in-corpus | en | `javaref-fileio#s10-c01` | Reviewed |
| JV2-025 | in-corpus | en | `javaref-fileio#s11-c01` | Reviewed |
| JV2-026 | in-corpus | en | `javaref-fileio#s12-c01` | Reviewed |
| JV2-027 | in-corpus | en | `javaref-fileio#s13-c01` | Reviewed |
| JV2-028 | in-corpus | en | `javaref-collections-intro#s04-c01` | Reviewed |
| JV2-029 | mixed | en | `javaref-arrays#s05-c01` | Reviewed |
| JV2-030 | mixed | en | `javaref-if#s03-c01` | Reviewed |
| JV2-031 | mixed | en | `javaref-for#s02-c01` | Reviewed |
| JV2-032 | mixed | en | `javaref-subclasses#s06-c01` | Reviewed |
| JV2-033 | mixed | en | `javaref-override#s02-c01` | Reviewed |
| JV2-034 | mixed | en | `javaref-override#s04-c02` | Reviewed |
| JV2-035 | mixed | en | `javaref-interface-def#s02-c01` | Reviewed |
| JV2-036 | mixed | en | `javaref-strings#s06-c01` | Reviewed |
| JV2-037 | mixed | en | `javaref-fileio#s04-c01` | Reviewed |
| JV2-038 | mixed | en | `javaref-collections-intro#s03-c01` | Reviewed |
| JV2-039 | out-of-corpus | none | No source; explicit abstain_reason | Reviewed |
| JV2-040 | out-of-corpus | none | No source; explicit abstain_reason | Reviewed |
| JV2-041 | out-of-corpus | none | No source; explicit abstain_reason | Reviewed |
| JV2-042 | out-of-corpus | none | No source; explicit abstain_reason | Reviewed |
| JV2-043 | out-of-corpus | none | No source; explicit abstain_reason | Reviewed |
| JV2-044 | out-of-corpus | none | No source; explicit abstain_reason | Reviewed |
| JV2-045 | out-of-corpus | none | No source; explicit abstain_reason | Reviewed |
