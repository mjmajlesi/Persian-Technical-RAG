"""FastAPI demo application skeleton (T015).

POST /api/ask validates requests per contracts/ask-api.md. The
answer/abstain/clarify dispatch is wired in T018/T023/T025; until then valid
requests receive an explicit 501 (Persian) instead of a fabricated answer.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.qa.provider import LLMProvider, ProviderConfig
from src.qa.retriever import Retriever

EMPTY_QUESTION_MESSAGE = "سوال نمی‌تواند خالی باشد."
NOT_WIRED_MESSAGE = "مسیر پاسخ هنوز وصل نشده است."


class AskRequest(BaseModel):
    question: str
    top_k: int = Field(default=5, ge=1, le=10)


app = FastAPI(title="Persian Technical RAG (demo)")

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
    # Dispatch (answer / abstain / clarify) lands in T018/T023/T025.
    raise HTTPException(status_code=501, detail=NOT_WIRED_MESSAGE)
