"""Pure scoring helpers (T031). Signatures are the T029 contract.

- hit_rate_at_5: True when any expected id is in the top-5 retrieved.
- citation_precision: share of cited ids that are real (in the index) AND
  expected supporters of the answer; empty citation lists score 1.0
  (nothing cited, nothing wrong — abstention-style).
- abstention_correct: out-of-corpus items must abstain with zero citations;
  answerable items must answer with >= 1 citation.
- mixed_slice_scores: aggregates over mixed-qtype rows only.
"""

from __future__ import annotations


def hit_rate_at_5(expected: list[str], retrieved: list[str]) -> bool:
    """True when any expected chunk id appears in the top-5 retrieved."""
    if not expected:
        return False
    top5 = set(retrieved[:5])
    return any(e in top5 for e in expected)


def citation_precision(
    cited: list[str], index_ids: set[str], expected: list[str]
) -> float:
    """Share of cited ids that are real index entries and expected supporters."""
    cited = list(cited)
    if not cited:
        return 1.0
    index_ids = set(index_ids)
    expected = set(expected)
    good = sum(1 for c in cited if c in index_ids and c in expected)
    return good / len(cited)


def abstention_correct(qtype: str, response: dict) -> bool:
    """Check the response fits the item type (abstain iff out-of-corpus)."""
    citations = response.get("citations", None)
    if qtype == "out-of-corpus":
        return response.get("type") == "abstain" and citations == []
    return response.get("type") == "answer" and isinstance(citations, list) \
        and len(citations) >= 1


def mixed_slice_scores(rows: list[dict]) -> dict:
    """Aggregate hit-rate and precision over mixed-qtype rows only."""
    mixed = [r for r in rows if r.get("qtype") == "mixed"]
    if not mixed:
        return {"hit_rate_at_5": 0.0, "citation_precision": 0.0, "n": 0}
    return {
        "hit_rate_at_5": sum(1 for r in mixed if r.get("hit")) / len(mixed),
        "citation_precision": sum(float(r.get("precision", 0.0)) for r in mixed)
        / len(mixed),
        "n": len(mixed),
    }
