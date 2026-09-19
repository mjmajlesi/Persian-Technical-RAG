# Quickstart: Grounded Persian C Q&A

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Prerequisites

- Python 3.11, `pip`, and (for the default LLM path) a provider API key in
  `LLM_API_KEY`. No database server needed (FAISS index lives in `data/`).

## 1. Install

```powershell
pip install -r requirements.txt
```

Expected: pinned install completes with no errors.

## 2. Freeze + ingest the corpus

```powershell
python -m src.ingest --manifest data/corpus/manifest.json
python -m src.index build --manifest data/corpus/manifest.json
```

Expected: `data/index/faiss.index` + `data/index/chunks.jsonl` are created;
chunk count and per-source counts print to console.

## 3. Ask a question (demo UI)

```powershell
uvicorn src.web:app --port 8000
```

Open `http://localhost:8000`, submit a Persian C question, and confirm: the
answer is in Persian, each claim carries a citation, and clicking a citation
reveals the source title + section heading + full chunk text (contract:
[ask-api.md](./contracts/ask-api.md)).

Validation probes:

- In-corpus question → `type: answer` with ≥1 traceable citation.
- Out-of-corpus question → `type: abstain`, Persian redirect, zero citations.
- Ambiguous one-word question → `type: clarify` follow-up, no answer attempted.
- Mixed Persian/English question (e.g. containing `malloc`) → same citation bar.

## 4. Run the evaluation

```powershell
pytest tests/
python -m src.eval run --set data/eval/eval-set.v1.json
```

Expected: all tests pass; a JSON + Markdown report lands in
`data/eval/reports/` with hit-rate@5, citation precision, abstention
correctness, and the mixed-language slice (schema:
[eval-set-schema.md](./contracts/eval-set-schema.md)).

## 5. Reproduce from scratch (examiner path)

Delete `data/index/` and re-run steps 2–4 using only this file. Same corpus
snapshot + same eval-set version must yield the same retrieval rows and
abstention verdicts (SC-005).
