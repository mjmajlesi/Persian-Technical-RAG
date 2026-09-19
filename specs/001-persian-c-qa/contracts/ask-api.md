# Contract: Ask API (`POST /api/ask`)

**Feature**: [spec.md](../spec.md) | **Entities**: [data-model.md](../data-model.md)

## Request

```json
{
  "question": "تابع malloc در C چه کاری انجام می‌دهد؟",
  "top_k": 5
}
```

| Field | Required | Rules |
|-------|----------|-------|
| `question` | Yes | Non-empty Persian string after trim |
| `top_k` | No | Integer 1–10, default 5 |

Error: empty/missing question → `422` with Persian error message.

## Success response — grounded answer (`200`)

```json
{
  "type": "answer",
  "answer_text": "…پاسخ فارسی…",
  "citations": [
    {
      "chunk_id": "cppref-malloc#s01-c01",
      "doc_title": "cppreference — malloc",
      "section_heading": "Description",
      "excerpt": "…full chunk text…"
    }
  ],
  "retrieved_chunk_ids": ["cppref-malloc#s01-c01", "fa-notes-memory#s02-c01"]
}
```

Rules: `citations.length >= 1`; every `chunk_id` exists in the active index;
every cited ID ∈ `retrieved_chunk_ids`.

## Success response — abstention (`200`)

```json
{
  "type": "abstain",
  "message": "…جمله فارسی + نزدیک‌ترین مباحث موجود…",
  "suggested_topics": ["مدیریت حافظه (malloc)", "اشاره‌گرها"],
  "citations": []
}
```

Rules: `citations` is always empty; each suggested topic exists in the corpus.

## Clarification response (`200`)

```json
{
  "type": "clarify",
  "message": "…one targeted Persian follow-up question…",
  "citations": []
}
```

Returned instead of an answer when the question is too short/ambiguous; no
answer is attempted on the same turn.
