# Contract: Languages API

**Feature**: [spec.md](../spec.md) | **Entities**: [data-model.md](../data-model.md)

## GET /api/languages (`200`)

Pack descriptors read live from `data/corpus/manifest.<lang>.json`:

```json
{
  "default": "c",
  "languages": [
    {
      "language_id": "c",
      "display_name": "C / سی",
      "status": "ready",
      "snapshot": "2026-09-23",
      "eval_set_version": "v1"
    },
    {
      "language_id": "java",
      "display_name": "Java / جاوا",
      "status": "empty",
      "snapshot": null,
      "eval_set_version": null
    }
  ]
}
```

Rules: one entry per manifest file; `status` is `empty` when the pack has no
index directory; `default` is always `"c"`.

## POST /api/ask — language field (extends 001's ask-api)

```json
{ "question": "...", "top_k": 5, "language": "cpp" }
```

| Field | Required | Rules |
|-------|----------|-------|
| `language` | No | Language id, default `"c"` (001 behavior preserved) |

Responses: identical `answer` / `abstain` / `clarify` shapes as 001, plus a
`language_id` echo field. Errors:

- Unknown `language` → `422` with a Persian error message.
- `language` whose pack is `empty` → `200` with
  `{"type": "unavailable", "message": "<Persian 'corpus not available'>",
  "language_id": "<id>", "citations": []}` — never an answer attempt.
