# Research: Grounded Persian C Q&A

**Date**: 2026-09-19 | **Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

All Technical Context unknowns are resolved below. (Live web search was
unavailable at plan time due to provider rate limits; decisions rest on
established, widely-documented mainstream practice consistent with the
constitution's technology-preference rule, and each notes a fallback so the
builder can re-validate during implementation.)

## 1. Persian-capable embeddings

- **Decision**: `intfloat/multilingual-e5-large` via `sentence-transformers`
  (query/passage prefixes per model card), evaluated on the 30-Q set before
  any alternative is considered.
- **Rationale**: Multilingual contrastive model with documented strength on
  non-English retrieval including Persian; runs locally (reproducible, no API
  cost); mainstream and well-documented — fits portfolio + thesis needs.
- **Alternatives considered**: `paraphrase-multilingual-mpnet-base-v2`
  (lighter, weaker on low-resource retrieval — fallback if laptop memory is a
  constraint); API embeddings (OpenAI/Cohere multilingual — rejected as
  default: external dependency hurts examiner reproducibility, kept as an
  opt-in alternative).

## 2. Vector index

- **Decision**: `faiss-cpu` flat/IP index persisted under `data/index/`
  alongside `chunks.jsonl` metadata.
- **Rationale**: Local file, no server process, deterministic rebuild from the
  frozen corpus — ideal for one-command reproduction; the bounded corpus
  (hundreds to low-thousands of chunks) needs no distributed store.
- **Alternatives considered**: Chroma/Qdrant (server or embedded modes add
  operational surface for zero retrieval benefit at this scale — rejected);
  SQLite-vec (less documented for this stack — noted fallback only).

## 3. LLM for Persian grounded generation

- **Decision**: Thin provider interface (`generate(prompt, context) -> text`);
  default concrete implementation calls a mainstream chat API (key via
  environment variable, model name pinned in config); prompt enforces
  Persian-only output, chunk-ID citations per claim, and the fixed abstention
  behavior when context is insufficient.
- **Rationale**: Persian generation quality of frontier APIs far exceeds what
  is trainable in a 3-month thesis; the interface keeps the system honest
  (swap to a local model e.g. via Ollama without touching pipeline code) and
  keeps eval comparable across providers.
- **Alternatives considered**: Local-only LLM default (rejected as default:
  VRAM/latency variance across examiner machines breaks SC-005
  reproducibility; supported as opt-in).

## 4. Chunking for mixed Persian Markdown + English reference HTML

- **Decision**: Section-aware chunking — split on Markdown headings / reference
  page sections, target ~512 tokens with ~64-token overlap; every chunk stores
  `{chunk_id, doc_title, section_heading, source_path_or_url, license}`.
  Code blocks are never split mid-block. Persian notes and English reference
  pages share the same schema so citations render uniformly.
- **Rationale**: Preserves the section granularity the citation UX promises
  (title + section + chunk text); heading metadata doubles as the "closest
  topics" signal for abstention redirects.
- **Alternatives considered**: Fixed-size token windows without structure
  (rejected: severs section context, weakens citation precision); semantic
  chunking (rejected: experimental, violates bounded complexity).

## 5. Retrieval strategy

- **Decision**: Single-stage dense retrieval, top-k=5 chunks into the prompt;
  abstention rule: if the best similarity score is below a calibrated
  threshold (calibrated on the eval set) OR the LLM reports insufficiency, the
  system abstains with the Persian redirect response. No re-ranker in v1.
- **Rationale**: Simplest architecture that satisfies groundedness +
  abstention; threshold is set from eval evidence, not intuition (constitution
  principle V).
- **Alternatives considered**: Hybrid BM25+dense / cross-encoder re-ranking
  (deferred: may be added only with before/after eval evidence per principle V).

## 6. Evaluation scoring

- **Decision**: Scripted scorer over the 30-Q set reporting retrieval
  hit-rate@5 (expected source among top-5), citation precision (cited chunks
  ⊇ supporting chunks, zero cited-but-nonexistent), abstention correctness
  (5/5 out-of-corpus abstain, 0 fabricated citations), plus a mixed-language
  slice reported separately to prove SC-004 parity. Report written as JSON +
  short Markdown summary under `data/eval/reports/`.
- **Rationale**: Directly implements SC-002/SC-003/SC-004 with metrics an
  examiner can re-run in one command.
- **Alternatives considered**: LLM-as-judge scoring (rejected for v1:
  non-deterministic, undermines reproducibility; may supplement later).

## 7. Web stack and RTL/bidi

- **Decision**: FastAPI serves `POST /api/ask` and a single server-rendered
  demo page (RTL layout, `dir="auto"` on mixed-language spans so English
  identifiers render correctly inside Persian text).
- **Rationale**: Minimal moving parts, mainstream, portfolio-standard;
  `dir="auto"` is the documented HTML mechanism for code-mixed bidi text.
- **Alternatives considered**: Streamlit/Gradio (rejected: weaker control over
  citation click-through UX); separate JS framework frontend (rejected: scope
  creep against honest-scope principle).

## 8. Corpus freezing and licensing

- **Decision**: `data/corpus/manifest.json` records every source (owner notes
  path + version/date; cppreference page URLs + retrieval date + CC-BY-SA
  attribution; glibc chapters + version) so the snapshot is auditable and the
  eval set pins to it.
- **Rationale**: Required by reproducibility (principle VI) and the CC-BY-SA
  license of cppreference content.
