# Implementation Plan: Embedding Model Comparison

**Branch**: `main` (no branch hook configured; feature directory `003-compare-embedding-models`) | **Date**: 2026-10-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/003-compare-embedding-models/spec.md`. Planning/design only; no implementation or task breakdown in this phase.

## Summary

Compare pinned `multilingual-e5-large`, `multilingual-e5-base`, and `bge-m3` across the existing C/C++/Python/Java packs using 45 **new** source-audited questions per pack. Reuse the frozen chunk inventory and current FAISS/answer path; inject a model-specific embedding adapter, index path and pooled-v1 calibration threshold at the existing dependency boundary. Produce retrieval-only and fixed-LLM end-to-end evidence **per model and language** with committed machine-readable final reports, plus pre-registered paired uncertainty and a descriptive v2 threshold sweep. An additional pooled analysis is explicitly exploratory, not a substitute for language-level results or a global winner. Keep the operational E5 index, v1 sets and dashboard defaults intact.

## Technical Context

**Language/Version**: Python 3.11; existing PowerShell/Windows CLI. Local `torch.cuda.is_available()` is false.

**Primary Dependencies**: Existing `sentence-transformers==3.3.1`, `faiss-cpu==1.10.0`, NumPy (transitive), FastAPI, pytest and the existing OpenAI-compatible LLM provider. Use the installed embedding library's dense paths for all three candidates where model-card smoke tests confirm correctness; do not add a second inference framework unless BGE-M3 cannot be represented faithfully, in which case justify and pin it before building indices. Model **weight/tokenizer SHAs** pinned separately in research/config (dependency package pins alone are insufficient).

**Storage**: Existing `data/corpus/<lang>/`, `data/index/<lang>/` and v1 sets stay frozen. New versioned `data/eval/<lang>/eval-set.<lang>.v2.json`; tracked model registry + calibration/run manifests under `data/eval/model-comparison/`; per-model/per-language **official final** JSON reports (including per-question rows and run metadata) and readable Markdown summaries under `data/eval/<lang>/reports/v2/<model>/`, both committed for the paper. Experimental model×pack indices keep tracked IDs/metadata and read the **canonical pack's** frozen `chunks.jsonl` by a validated path/hash (no duplicate chunk copies). For **new experimental outputs**, ignore only regenerable embedding caches and FAISS index binaries under `data/research/embedding-compare/<model>/<lang>/`; retain the repository's existing policy for historical v1 reports and chunk files. Replace or explicitly override any broad JSON-report ignore rule so official v2 JSON can be staged; verify with `git check-ignore` and a staged-file/secret scan before commit. Incomplete attempts are labeled diagnostics, never silently promoted to official reports.

**Testing**: pytest unit tests for model-card formatting/cache keys/calibration/bootstrap; contract tests for unchanged chunk IDs, index/pack/model isolation, committed official JSON schema and v1 CLI behavior; integration tests for retrieval-only (zero LLM calls) and end-to-end citation validation. Audit all 180 authored references and source-language labels against frozen records; full existing test suite must remain green.

**Target Platform**: Canonical: existing 15.6 GiB RAM CPU-only Windows laptop, sequential **one model at a time**. Kaggle is an optional accelerator if measured BGE-M3 throughput or memory blocks local indexing; the same pinned commands, input hashes and settings must work there without hard-coded notebook paths or committed credentials. Record device and floating-point/top-k differences rather than promising CPU/GPU byte-identical indices.

**Project Type**: Existing single FastAPI + CLI Python project, extended with research-only evaluation/configuration. No student-facing model selector or new service.

**Performance Goals**: Once model files and indices are cached, a healthy-provider model×language evaluation completes within the spec's 30-minute target; log actual elapsed time and batches. Cache reuse should avoid re-embedding the 1030 frozen passages on reruns. Initial CPU download/index time is measured separately (not misreported as evaluation latency).

**Constraints**: Identical raw chunk text/order/IDs and frozen corpus for all candidates; model-specific query/passage prefixes, normalization and max lengths follow each pinned model card; dense vector dimension differs (E5-base 768; others 1024). One pooled v1 gate per model (100 answerable/20 OOC), no v2 tuning; **primary paper comparisons remain per-language**. For E2E, send and log `temperature=0`; log provider, request timestamp and the `model` identifier returned by the API for every response (plus the distinct IDs/timestamps in the run manifest). Pre-register the expected response model ID for that provider; missing, changing or unexpected IDs, or rejection of the temperature parameter, make **E2E incomplete only**; retrieval-only evidence remains valid. An accepted parameter does not prove the provider honored its value, and a provider may silently change weights behind a stable model ID: both limitations must be disclosed. Preserve the current per-pack operational gates outside research mode. Record exact runtime package versions/environment per run (not just direct dependency pins).

**Scale/Scope**: Three pinned candidates × four packs = 12 model-pack indices/runs; four new 45-item v2 sets (180 items); no training, new corpus, alternate retrieval algorithm, production deployment or architecture change.

## Constitution Check

*Gate before Phase 0 and rechecked after Phase 1 design: PASS; no justified exceptions required.*

| Principle | Status | Evidence / validation |
|---|---|---|
| I. Groundedness | PASS | Same composer and insufficiency policy; no answer without selected pack's retrieved context; E2E error/abstention recorded. |
| II. Citation Accuracy | PASS | Retain pack-scoped cited-ID checks; every v2 reference answer has audited source evidence. |
| III. Bounded Complexity | PASS | Same chunk → dense embed → existing FAISS search → composer; three mainstream models configured at the embedding boundary, no reranker/agent/new vector store. |
| IV. Persian-First | PASS | New questions in Persian, code-mixed slice and fa→fa/fa→en evidence labels; model-card query formatting smoke-tested. |
| V. Evaluability | PASS | Versioned v2 holdout, pooled v1 calibration, retrieval-only vs E2E split, per-language **primary** metrics/CIs; pooled analysis explicitly exploratory, never a blended winner. |
| VI. Reproducibility | PASS | Exact embedding revisions, licenses, hashes, cache invalidation, calibration seed/method, provider/response-model/request-temperature/time metadata, committed official JSON and CLI quickstart; silent provider switching disclosed. |
| VII. Honest Scope | PASS | Only four frozen packs and three registered models, CPU-first; benchmark claims limited to observed questions/corpora. |
| VIII. Per-Language Isolation | PASS | Distinct model×pack research indices plus current operational indices; no shared language index, membership asserted before citation. |

**Post-design re-check**: the model-card-specific text preparation modifies only embedding inputs (never raw chunks), and per-model cache/index layouts add reproducible artifacts, not a new retrieval pipeline. No constitution amendment or complexity exception needed.

## Implementation Outline (for subsequent tasks)

1. **Freeze experiment inputs**: register candidate IDs, immutable revisions and model-card settings; validate original v1/chunk hashes and author 180 new v2 items with traceable references. Preserve v1 files byte-for-byte.
2. **One configurable embedding boundary**: default `e5-large` remains compatible with all current callers; experimental model selection supplies the right query/passages preparation, normalized dense vectors and vector dimension to the same existing index/retriever. Reuse `faiss_store`, don't duplicate answer/gate rules. Give the existing retriever a model-aware index path and the canonical pack chunk path; validate their shared ID/content hash before serving. Isolate experimental indexes by both model and pack and reject mismatched metadata on load.
3. **Cache and build**: sequential CPU model loads, per-pack passage cache keyed by revision/settings/ordered chunk-text hash, optional query cache keyed by exact question + model settings; write cache/index atomically. Expose model selection to index-build and eval CLIs by config/flag, without exposing model selection on the student dashboard. Validate default operational output unchanged.
4. **Research eval**: extend `src/eval/run.py` with model and mode selection. A retrieval-only pass never requests LLM; for E2E use the **same** answer path with an injected model-pack retriever and pooled gate, preserving its citation guard. Do not let the existing globally cached default retriever silently answer with E5 during an experimental run. Extend the provider boundary to send temperature and capture the API-returned model ID, provider and timestamp per response; validate the returned ID against the pre-registered expected value and across the run. If the response ID cannot be checked or the provider rejects the temperature parameter, mark **only E2E incomplete**, retain its diagnostics, and keep the retrieval-only run complete. Document the residual risk of silent changes behind an unchanged model ID or ignored temperature; do not claim the returned ID proves immutable weights.
5. **Inference and reporting**: calibrate on pooled v1, lock each gate; on v2 collect fixed-gate and E2E abstention separately, AUROC/PR descriptive sweep, 10k seeded question-level bootstrap with paired differences and Bonferroni adjustment for the **per-language** winner rule. Include sample/answer counts, confidence intervals, source-locale/truncation slices, error counts and disclosures of earlier E5-v1 exposure and provider drift. Commit official final JSON with the Markdown summaries. Optionally show a **secondary pooled exploratory analysis**, clearly labeled with its own sample counts/uncertainty, alongside—not in place of—the four language tables; never use it to tune gates or assert a global winner.

## Project Structure

### Documentation (this feature)

```text
specs/003-compare-embedding-models/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── contracts/
│   ├── model-config.md
│   └── evaluation-cli-and-report.md
├── quickstart.md
└── tasks.md              # Future /speckit.tasks output, NOT generated now
```

### Existing project, minimal touch points

```text
src/index/embed.py, __main__.py        # Selected model's card rules + existing build
src/index/faiss_store.py              # Keep the same normalized dense search
src/qa/retriever.py, pack_config.py   # Inject model-aware embedding/index and research gate
src/web/app.py                        # Reuse same answer orchestration with injectable dependencies
src/eval/run.py, calibrate.py         # Extend CLIs; add small comparison/scoring helpers only as needed
data/eval/<lang>/                     # Frozen v1, new v2; official JSON + Markdown reports tracked
data/eval/model-comparison/           # Tracked fixed model and run configurations
data/research/embedding-compare/      # Regenerable caches/FAISS binaries ignored, not final reports
tests/unit, tests/contract, tests/integration/
```

**Structure Decision**: Extend the existing project in place; cache and experimental indices are data layouts, not new services or a second RAG stack. If a model-card requirement needs an extra installed library, pin and document it in the same change rather than introducing a generic adapter framework in advance.

**Documentation alignment before implementation**: the current research contracts still describe final JSON as local/ignored and copying chunks into each experimental index. When decomposing tasks, align them and the research quickstart with this revised plan's **committed official JSON** and **canonical chunk path** policies; this request changes only `plan.md`, so those files are intentionally not edited here.

## Complexity Tracking

No constitutional violations. Keep the adapter/config surface small; optional Kaggle execution uses the same CLI rather than a duplicate notebook implementation.
