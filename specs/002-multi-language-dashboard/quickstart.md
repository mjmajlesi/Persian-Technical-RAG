# Quickstart: Multi-Language Dashboard

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Run from the repository root with Python 3.11 and the pinned `.venv` (`pip install -r requirements.txt`). Copy `.env.example` to `.env` and supply `LLM_API_KEY`, `LLM_BASE_URL` and `LLM_MODEL` for end-to-end answers/evaluation; no credentials belong in git. Frozen source manifests are in `data/corpus/manifest.<lang>.json`.

## 1. Rebuild each ready pack

The one-time C migration is already complete. **Do not rerun a migration script:** the old flat corpus/index paths do not exist. See [migration results](../../docs/MIGRATION-RESULTS.md) for the 001 vs 002 comparison.

```powershell
foreach ($lang in 'c', 'cpp', 'python', 'java') {
    .\.venv\Scripts\python -m src.ingest --lang $lang
    .\.venv\Scripts\python -m src.index build --lang $lang
}
```

Expected chunk counts: C **503**, C++ **201**, Python **253**, Java **73** (embedding dimension 1024). Each `data/index/<lang>/` holds `chunks.jsonl`, `ids.json` and `faiss.index`. Repeat the commands without deleting files; on the frozen snapshot, these three files are byte-identical to the previous build for every pack (T027 validation, 2026-10-22). Pack sources and license notes stay in their manifests.

## 2. Dashboard and API probes

```powershell
.\.venv\Scripts\python -m uvicorn src.web.app:app --port 8000
```

Open `http://localhost:8000`: four-pack RTL sidebar, C preselected, answer with pack-internal clickable citations. `GET /api/languages` returns four ready packs; an unknown language on `POST /api/ask` returns 422. For **each** pack, ask one in-corpus question (Persian answer + pack-internal citations), one out-of-corpus question (abstain, zero citations), and a short ambiguous question such as «اشاره‌گر؟» (clarify). An unindexed listed pack responds `unavailable` with zero citations; all four shipped packs are currently ready, so validating this branch requires a controlled mocked empty-pack status, **not moving or deleting an existing index**. Switching languages clears the Q&A view state.

## 3. Tests and per-language evaluation

```powershell
.\.venv\Scripts\python -m pytest tests/ -q
foreach ($lang in 'c', 'cpp', 'python', 'java') {
    .\.venv\Scripts\python -m src.eval run --lang $lang
}
```

Each run writes JSON (gitignored) and Markdown under `data/eval/<lang>/reports/`. Read **four independent reports**, never a blended score: 20 in-corpus + 5 mixed + 5 out-of-corpus questions per pack, plus 3 separate cross-language contamination probes (`data/eval/contamination.v1.json`). Check `error_count=0` / Markdown `Status: complete` before quoting figures; a rate-limited/unavailable model can otherwise produce incomplete reports. Retrieval and frozen index bytes are deterministic; LLM answer/citation selection can vary between runs, so an exact citation-precision match is **not** a reproducibility requirement. The C migration comparison and its limits are in `docs/MIGRATION-RESULTS.md`.

Dashboard state regression check: type a question in one pack and switch packs; the input must clear. Submit a question and switch before the response arrives; the previous pack's delayed answer must not appear under the newly selected pack.
