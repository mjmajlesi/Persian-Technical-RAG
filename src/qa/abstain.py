"""Abstention module (T014).

Two abstention triggers (either suffices):
  1. the top retrieval cosine score is below SIMILARITY_THRESHOLD, or
  2. the answer composer reports the LLM insufficiency signal
     (INSUFFICIENT sentinel from src/qa/answer.py).

The response is a fixed-form Persian message naming the closest available
topics (taken from the top retrieved chunks' sections, so they always exist
in the corpus) and carries zero citations. Without topic evidence it uses
a neutral message and suggests no topics.

DEFAULT_THRESHOLD is provisional; T024 (src/eval/calibrate.py) calibrates it
formally on the versioned evaluation set.
"""

from __future__ import annotations

DEFAULT_THRESHOLD = 0.81
# Calibrated in T024 (src/eval/calibrate.py) on 12 probes against the frozen
# 503-chunk v1 index: max(out-of-domain top-1) = 0.775, min(in-domain top-1)
# = 0.849; threshold = gap midpoint, maximizing the margin on both sides.
# Re-validate on the versioned 30-question eval set (T030+): if
# abstention_correct < 5/5 or in-domain answers start gating, re-calibrate.

MESSAGE_TEMPLATE = (
    "در منابع موجود پاسخی برای این سوال پیدا نکردم. "
    "نزدیک‌ترین مباحث موجود: {topics}."
)
NO_TOPICS_MESSAGE = "در منابع موجود پاسخی برای این سوال پیدا نکردم."


def closest_topics(chunks: list[dict], limit: int = 3) -> list[str]:
    """Derive 1–3 topic names from top retrieved chunks (highest score first).

    Uses section headings (falling back to document titles), deduplicated,
    so every suggested topic exists in the corpus by construction.
    """
    topics: list[str] = []
    for chunk in chunks[:limit]:
        name = (chunk.get("section_heading") or chunk.get("doc_title") or "").strip()
        if name and name not in topics:
            topics.append(name)
    return topics[:limit]


def should_abstain(top_score: float, threshold: float = DEFAULT_THRESHOLD) -> bool:
    """True when the best retrieval score is below the confidence threshold."""
    return top_score < threshold


def decide(
    chunks: list[dict],
    top_score: float,
    llm_insufficient: bool,
    threshold: float = DEFAULT_THRESHOLD,
) -> dict | None:
    """Return an abstention payload, or None when answering may proceed.

    Payload shape matches contracts/ask-api.md (minus the "type" envelope,
    which the web layer adds): {message, suggested_topics, citations: []}.
    """
    if not llm_insufficient and not should_abstain(top_score, threshold):
        return None
    topics = closest_topics(chunks)
    return {
        "message": MESSAGE_TEMPLATE.format(topics="، ".join(topics)) if topics else NO_TOPICS_MESSAGE,
        "suggested_topics": topics,
        "citations": [],
    }
