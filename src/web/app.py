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
from src.qa import pack_config
from src.qa.answer import AnswerError, UncitedAnswerError, compose_answer
from src.qa.provider import LLMProvider, ProviderConfig, ProviderError
from src.qa.retriever import Retriever
from src.web import packs as pack_registry

EMPTY_QUESTION_MESSAGE = "سوال نمی‌تواند خالی باشد."
UNKNOWN_LANGUAGE_MESSAGE = "زبان نامشخص است."
CORPUS_UNAVAILABLE_MESSAGE = "کورپوس این زبان هنوز آماده نیست."
LLM_NOT_CONFIGURED_MESSAGE = (
    "سرویس مدل زبانی پیکربندی نشده است (LLM_API_KEY/LLM_MODEL)."
)
INVALID_ANSWER_MESSAGE = "پاسخ معتبر تولید نشد. لطفاً دوباره تلاش کنید."
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
    language: str = Field(default="c")


app = FastAPI(title="Persian Technical RAG (demo)")
app.mount("/static", StaticFiles(directory="src/web/static"), name="static")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse("src/web/templates/index.html", media_type="text/html")


@app.get("/api/languages")
def list_languages() -> dict:
    """Pack descriptors read live from the manifests (002-T007)."""
    return {
        "default": pack_registry.DEFAULT_LANGUAGE,
        "languages": [
            {
                "language_id": p.language_id,
                "display_name": p.display_name,
                "status": p.status,
                "snapshot": p.snapshot,
                "eval_set_version": p.eval_set_version,
            }
            for p in pack_registry.load_packs()
        ],
    }

_retrievers: dict[str, Retriever] = {}
_provider: LLMProvider | None = None


def get_retriever(language: str = "c") -> Retriever:
    """Lazily build (once per language) the Retriever for a pack's index.

    002-T014: pack descriptors come from the registry (single source of
    truth for index locations), and only the SELECTED pack's index is ever
    opened — isolation by construction (constitution Principle VIII). The
    001 composer/answer path is reused unchanged on top.
    """
    if language not in _retrievers:
        _retrievers[language] = Retriever(
            pack_registry.get_pack(language).index_dir
        )
    return _retrievers[language]


def get_provider() -> LLMProvider:
    """Lazily build (once) the shared LLM provider from the environment."""
    global _provider
    if _provider is None:
        _provider = LLMProvider(ProviderConfig.from_env())
    return _provider


def _fabrication_abstain(pack, chunks, threshold: float) -> dict:
    """002-T017: treating fabrication as insufficiency — the Persian
    abstain/redirect response instead of an answer or an HTTP 500."""
    payload = abstain.decide(
        chunks, top_score=chunks[0]["score"], llm_insufficient=True,
        threshold=threshold,
    )
    return {"type": "abstain", "language_id": pack.language_id, **payload}


@app.post("/api/ask")
def ask(request: AskRequest) -> dict:
    return _ask(request)


def _ask(request: AskRequest, *, retriever: Retriever | None = None,
         threshold: float | None = None, provider: LLMProvider | None = None,
         retrieved_chunks: list[dict] | None = None) -> dict:
    """Shared student/research answer path; defaults preserve the web behavior."""
    if not request.question.strip():
        raise HTTPException(status_code=422, detail=EMPTY_QUESTION_MESSAGE)
    question = request.question.strip()
    try:
        pack = pack_registry.get_pack(request.language)
    except pack_registry.PackError:
        raise HTTPException(status_code=422, detail=UNKNOWN_LANGUAGE_MESSAGE)
    if pack.status == "empty":
        # T008: listed but not ingested — explicit state, never an attempt.
        return {
            "type": "unavailable",
            "message": CORPUS_UNAVAILABLE_MESSAGE,
            "language_id": pack.language_id,
            "citations": [],
        }
    if len(question.split()) < AMBIGUOUS_MIN_WORDS:
        # T020b: no retrieval, no LLM call, no answer attempt.
        return {
            "type": "clarify",
            "message": CLARIFY_MESSAGE_TEMPLATE.format(question=question),
            "language_id": pack.language_id,
            "citations": [],
        }
    # T023: retrieve FIRST (local, free), then gate on the similarity
    # threshold BEFORE touching the LLM: low scores abstain immediately,
    # so out-of-domain questions cost zero LLM calls/credit. 002-T009: the
    # gate value is per-pack (pack_config) after the language resolves.
    if threshold is None:
        threshold = pack_config.threshold_for(pack.language_id)
    if retriever is None:
        retriever = get_retriever(pack.language_id)
    chunks = (retrieved_chunks if retrieved_chunks is not None else
              retriever.retrieve(question, k=request.top_k))
    if not chunks:
        payload = abstain.decide([], 0.0, llm_insufficient=True, threshold=threshold)
        return {"type": "abstain", "language_id": pack.language_id, **payload}
    gated = abstain.decide(
        chunks, top_score=chunks[0]["score"], llm_insufficient=False,
        threshold=threshold,
    )
    if gated is not None:
        return {"type": "abstain", "language_id": pack.language_id, **gated}
    if provider is None:
        try:
            provider = get_provider()
        except ProviderError:
            raise HTTPException(status_code=500, detail=LLM_NOT_CONFIGURED_MESSAGE)
    try:
        # 002-T017: pack-scoped citation validation wraps the whole answer
        # path. compose_answer already rejects ids absent from the RECEIVED
        # chunks (AnswerError = fabrication); here a fabricator that slips
        # past that layer still cannot cite anything outside the SELECTED
        # pack's index — foreign ids abstain instead of answering.
        result = compose_answer(question, chunks, provider)
        cited = [c["chunk_id"] for c in result.get("citations", [])]
        if cited and not all(retriever.has_chunk(cid) for cid in cited):
            return _fabrication_abstain(pack, chunks, threshold)
    except UncitedAnswerError:
        raise HTTPException(status_code=500, detail=INVALID_ANSWER_MESSAGE)
    except AnswerError:
        # Fabrication (model cited an unknown chunk id) → abstain, never
        # a fabricated answer and never a 500.
        return _fabrication_abstain(pack, chunks, threshold)
    if result["insufficient"]:
        # Insufficiency fallback only; the threshold-gated abstention path
        # (skipping the LLM call) is wired in T023.
        payload = abstain.decide(
            chunks, top_score=chunks[0]["score"], llm_insufficient=True,
            threshold=threshold,
        )
        return {"type": "abstain", "language_id": pack.language_id, **payload}
    return {
        "type": "answer",
        "language_id": pack.language_id,
        "answer_text": result["answer_text"],
        "citations": result["citations"],
        "retrieved_chunk_ids": result["retrieved_chunk_ids"],
    }
