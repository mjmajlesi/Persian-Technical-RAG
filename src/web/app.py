"""FastAPI demo application skeleton (T015).

POST /api/ask validates requests per contracts/ask-api.md. The
answer/abstain/clarify dispatch is wired in T018/T023/T025; until then valid
requests receive an explicit 501 (Persian) instead of a fabricated answer.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from src.qa import abstain
from src.qa.answer import AnswerError, compose_answer
from src.qa.provider import LLMProvider, ProviderConfig, ProviderError
from src.qa.retriever import Retriever

EMPTY_QUESTION_MESSAGE = "سوال نمی‌تواند خالی باشد."
ANSWER_FAILED_MESSAGE = "خطای داخلی در تولید پاسخ grounded."
LLM_NOT_CONFIGURED_MESSAGE = (
    "سرویس مدل زبانی پیکربندی نشده است (LLM_API_KEY/LLM_MODEL)."
)
# T020b: questions shorter than this (words, after trim) get a single
# targeted follow-up instead of an answer attempt (clarify decision Q3).
AMBIGUOUS_MIN_WORDS = 3
CLARIFY_MESSAGE_TEMPLATE = (
    "سوال شما («{question}») خیلی کوتاه است. لطفاً دقیق‌تر بگویید "
    "منظورتان چیست — تعریف، مثال، یا تفاوت با مفهوم دیگر؟"
)


class AskRequest(BaseModel):
    question: str
    top_k: int = Field(default=5, ge=1, le=10)


app = FastAPI(title="Persian Technical RAG (demo)")
app.mount("/static", StaticFiles(directory="src/web/static"), name="static")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse("src/web/templates/index.html", media_type="text/html")

_retriever: Retriever | None = None
_provider: LLMProvider | None = None


def get_retriever() -> Retriever:
    """Lazily build (once) the shared Retriever over the frozen index."""
    global _retriever
    if _retriever is None:
        _retriever = Retriever("data/index")
    return _retriever


def get_provider() -> LLMProvider:
    """Lazily build (once) the shared LLM provider from the environment."""
    global _provider
    if _provider is None:
        _provider = LLMProvider(ProviderConfig.from_env())
    return _provider


@app.post("/api/ask")
def ask(request: AskRequest) -> dict:
    if not request.question.strip():
        raise HTTPException(status_code=422, detail=EMPTY_QUESTION_MESSAGE)
    question = request.question.strip()
    if len(question.split()) < AMBIGUOUS_MIN_WORDS:
        # T020b: no retrieval, no LLM call, no answer attempt.
        return {
            "type": "clarify",
            "message": CLARIFY_MESSAGE_TEMPLATE.format(question=question),
            "citations": [],
        }
    try:
        provider = get_provider()
    except ProviderError:
        raise HTTPException(status_code=500, detail=LLM_NOT_CONFIGURED_MESSAGE)
    chunks = get_retriever().retrieve(question, k=request.top_k)
    try:
        result = compose_answer(question, chunks, provider)
    except AnswerError:
        raise HTTPException(status_code=500, detail=ANSWER_FAILED_MESSAGE)
    if result["insufficient"]:
        # Insufficiency fallback only; the threshold-gated abstention path
        # (skipping the LLM call) is wired in T023.
        payload = abstain.decide(
            chunks, top_score=chunks[0]["score"], llm_insufficient=True
        )
        return {"type": "abstain", **payload}
    return {
        "type": "answer",
        "answer_text": result["answer_text"],
        "citations": result["citations"],
        "retrieved_chunk_ids": result["retrieved_chunk_ids"],
    }
