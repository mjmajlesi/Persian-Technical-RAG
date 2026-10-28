"""Grounded prompt builder + answer composer (T013).

The prompt instructs the model (in Persian) to answer ONLY from the numbered
context chunks, in Persian, citing every factual claim with its chunk ID in
brackets, e.g. [fa-pointers#s02-c01]. When the context is insufficient the
model must reply with exactly the INSUFFICIENT sentinel (no explanation);
the abstention module (T014, src/qa/abstain.py) turns that into the Persian
redirect response. Cited IDs are validated to be a subset of the retrieved
IDs — anything else raises AnswerError instead of silently fabricating.
"""

from __future__ import annotations

import logging
import re

from src.qa.retriever import detect_query_lang

logger = logging.getLogger(__name__)

INSUFFICIENT = "CANNOT_ANSWER"

_CITE_RE = re.compile(r"\[([^\[\]\s]+#[^\[\]\s]+)\]")

PROMPT_TEMPLATE = """شما یک دستیار آموزشی زبان C هستید که فقط به فارسی پاسخ می‌دهد.

قواعد الزامی:
۱. فقط بر اساس «متن‌های زمینه» زیر پاسخ بده؛ از دانش خودت چیزی اضافه نکن.
۲. هر ادعای واقعی (factual claim) را بلافاصله با شناسه همان چانک داخل کروشه استناد بده، مثلاً [fa-pointers#s02-c01].
۳. شناسه‌ای که در فهرست زمینه نیست هرگز ننویس.
۴. اگر متن‌های زمینه برای پاسخ کافی نیستند، بدون هیچ توضیح اضافه دقیقاً بنویس: CANNOT_ANSWER
۵. شناسه‌ها و نام‌های انگلیسی (تابع‌ها، کتابخانه‌ها، پیام‌های خطا) را عیناً و بدون ترجمه یا نویسه‌گردانی نگه دار.

سوال:
{question}

متن‌های زمینه:
{context}
"""


class AnswerError(RuntimeError):
    """Raised when the model output violates the groundedness contract."""


class UncitedAnswerError(AnswerError):
    """Raised when a non-abstention output contains no complete citation."""


def build_prompt(question: str, chunks: list[dict]) -> str:
    """Render the grounded Persian prompt for the given question + chunks."""
    numbered = "\n\n".join(
        f"[{c['chunk_id']}] ({c['doc_title']} — {c['section_heading']})\n{c['text']}"
        for c in chunks
    )
    return PROMPT_TEMPLATE.format(question=question.strip(), context=numbered)


def extract_cited_ids(answer_text: str) -> list[str]:
    """Return chunk IDs cited as [id] markers, in order of appearance."""
    return _CITE_RE.findall(answer_text)


def compose_answer(question: str, chunks: list[dict], provider) -> dict:
    """Generate a grounded answer via the provider and validate citations.

    Returns {"answer_text", "citations", "retrieved_chunk_ids",
    "insufficient"}. Raises UncitedAnswerError without citations, or
    AnswerError on phantom citations.
    """
    retrieved_ids = [c["chunk_id"] for c in chunks]
    logger.info("compose lang_hint=%s", detect_query_lang(question))
    answer_text = provider.generate(
        build_prompt(question, chunks),
        "",  # context is already embedded in the prompt
    ).strip()
    if answer_text == INSUFFICIENT:
        return {
            "answer_text": answer_text,
            "citations": [],
            "retrieved_chunk_ids": retrieved_ids,
            "insufficient": True,
        }
    cited = extract_cited_ids(answer_text)
    if not cited:
        raise UncitedAnswerError("model output contains no complete citation")
    phantom = [cid for cid in cited if cid not in retrieved_ids]
    if phantom:
        raise AnswerError(f"cited unknown chunk ids: {phantom}")
    by_id = {c["chunk_id"]: c for c in chunks}
    citations = [
        {
            "chunk_id": cid,
            "doc_title": by_id[cid]["doc_title"],
            "section_heading": by_id[cid]["section_heading"],
            "excerpt": by_id[cid]["text"],
        }
        for cid in dict.fromkeys(cited)  # dedupe, keep order
    ]
    return {
        "answer_text": answer_text,
        "citations": citations,
        "retrieved_chunk_ids": retrieved_ids,
        "insufficient": False,
    }
