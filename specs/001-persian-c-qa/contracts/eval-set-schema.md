# Contract: Evaluation Set & Report Schema

**Feature**: [spec.md](../spec.md) | **Entities**: [data-model.md](../data-model.md)

## Eval set file (`data/eval/eval-set.v1.json`)

```json
{
  "version": "v1",
  "items": [
    {
      "item_id": "C-001",
      "question": "…Persian question…",
      "qtype": "in-corpus",
      "expected_source_ids": ["fa-notes-pointers#s03-c02"],
      "expected_answer_summary": "…one-line Persian gist for the scorer…"
    }
  ]
}
```

Rules: `qtype ∈ {in-corpus, mixed, out-of-corpus}`; the set holds ~30 items in
a 20/5/5 split; `expected_source_ids` is empty for `out-of-corpus` items;
`expected_source_ids` reference chunks in the frozen index snapshot.

## Eval report (`data/eval/reports/<date>-v1.json` + `.md` summary)

```json
{
  "eval_set_version": "v1",
  "index_snapshot": "2026-09-19",
  "llm_id": "provider:model-name",
  "hit_rate_at_5": 0.0,
  "citation_precision": 0.0,
  "abstention_correct": "5/5",
  "mixed_slice": { "hit_rate_at_5": 0.0, "citation_precision": 0.0 },
  "per_item_rows": []
}
```

Metric definitions:

- `hit_rate_at_5`: fraction of in-corpus + mixed items whose
  `expected_source_ids ∩ top-5 retrieved ≠ ∅`.
- `citation_precision`: fraction of answers whose every cited `chunk_id`
  exists in the index and supports the claim (unsupported or phantom citations
  score 0 for that item).
- `abstention_correct`: fraction of out-of-corpus items returning
  `type: abstain` with zero citations (target 5/5).
- `mixed_slice`: hit-rate and precision computed over the 5 mixed items only
  (must meet the same bar as the full set per SC-004).
