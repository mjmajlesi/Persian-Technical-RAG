"""F01 FAIL-first: real composer/_ask, in-memory ASGI, no model or HTTP client."""

import json
from types import SimpleNamespace

import fastapi.routing
import pytest

from src.eval import run
from src.qa import abstain, answer
from src.web import app as web


QUESTION = "در زبان سی اشاره‌گر چه کاربردی دارد؟"
INVALID = ["", " \t\n ", "پاسخ بدون ارجاع", "پاسخ [c#1"]
INVALID_IDS = ["empty", "whitespace", "uncited", "incomplete-marker"]
RETRY_MESSAGE = "پاسخ معتبر تولید نشد. لطفاً دوباره تلاش کنید."
CHUNK = {"chunk_id": "c#1", "score": 1.0, "doc_title": "C",
         "section_heading": "اشاره‌گر", "text": "متن شاهد آزمایشی"}


class FakeRetriever:
    def __init__(self, *args, **kwargs):
        self.calls = []

    def retrieve(self, question, k=5):
        self.calls.append((question, k))
        return [dict(CHUNK)]

    def has_chunk(self, chunk_id):
        return chunk_id == CHUNK["chunk_id"]


class FakeProvider:
    def __init__(self, text):
        self.text = text
        self.prompts = []

    def generate(self, prompt, context=""):
        self.prompts.append(prompt)
        return self.text

    def generate_with_metadata(self, prompt, context="", *, expected_model_id):
        return {"text": self.generate(prompt, context), "provider": "fake",
                "request_timestamp": "2026-10-28T00:00:00+00:00",
                "model": expected_model_id, "temperature": 0}


@pytest.fixture
def engine(monkeypatch):
    async def inline_threadpool(function, *args, **kwargs):
        return function(*args, **kwargs)

    # Only scheduling is replaced; ASGI routing, _ask and composer stay real.
    # No event loop/self-pipe sockets are needed for this synchronous endpoint.
    monkeypatch.setattr(fastapi.routing, "run_in_threadpool", inline_threadpool)
    retriever = FakeRetriever()
    provider = FakeProvider("")
    monkeypatch.setattr(web.pack_registry, "get_pack", lambda language: SimpleNamespace(
        status="ready", language_id=language))
    monkeypatch.setattr(web, "get_retriever", lambda language: retriever)
    monkeypatch.setattr(web, "get_provider", lambda: provider)
    return retriever, provider


def _post_ask():
    async def request():
        body = json.dumps({"question": QUESTION, "language": "c"}).encode("utf-8")
        messages = []

        async def receive():
            return {"type": "http.request", "body": body, "more_body": False}

        async def send(message):
            messages.append(message)

        await web.app({"type": "http", "asgi": {"version": "3.0"},
                       "http_version": "1.1", "method": "POST", "scheme": "http",
                       "path": "/api/ask", "raw_path": b"/api/ask", "query_string": b"",
                       "root_path": "", "headers": [(b"content-type", b"application/json")],
                       "client": ("in-memory", 1), "server": ("in-memory", 80)}, receive, send)
        status = next(m["status"] for m in messages if m["type"] == "http.response.start")
        payload = b"".join(m.get("body", b"") for m in messages
                           if m["type"] == "http.response.body")
        return status, json.loads(payload.decode("utf-8"))

    coroutine = request()
    try:
        coroutine.send(None)
    except StopIteration as completed:
        return completed.value
    finally:
        coroutine.close()
    raise AssertionError("in-memory request unexpectedly required asynchronous I/O")


@pytest.mark.parametrize("text", INVALID, ids=INVALID_IDS)
def test_composer_rejects_uncited_output_with_specific_answer_error(text):
    with pytest.raises(answer.AnswerError) as caught:
        answer.compose_answer(QUESTION, [CHUNK], FakeProvider(text))
    subtype = getattr(answer, "UncitedAnswerError", None)
    assert subtype is not None and issubclass(subtype, answer.AnswerError)
    assert type(caught.value) is subtype


@pytest.mark.parametrize("text", INVALID, ids=INVALID_IDS)
def test_asgi_uncited_output_is_http_error_not_abstention(engine, text):
    retriever, provider = engine
    provider.text = text
    status, payload = _post_ask()
    assert retriever.calls == [(QUESTION, 5)]
    assert len(provider.prompts) == 1
    assert status == 500
    assert payload == {"detail": RETRY_MESSAGE}


@pytest.mark.parametrize("text", [answer.INSUFFICIENT, "پاسخ [foreign#1]"],
                         ids=["valid-sentinel", "foreign-citation"])
def test_asgi_existing_abstentions_are_preserved(engine, text):
    retriever, provider = engine
    provider.text = text
    status, payload = _post_ask()
    expected = abstain.decide([CHUNK], 1.0, llm_insufficient=True,
                              threshold=web.pack_config.threshold_for("c"))
    assert status == 200
    assert payload == {"type": "abstain", "language_id": "c", **expected}
    assert payload["citations"] == []
    assert retriever.calls == [(QUESTION, 5)] and len(provider.prompts) == 1


def test_asgi_valid_cited_answer_is_preserved(engine):
    _, provider = engine
    provider.text = "پاسخ مستند [c#1]"
    status, payload = _post_ask()
    assert status == 200 and payload["type"] == "answer"
    assert payload["language_id"] == "c"
    assert payload["answer_text"] == provider.text
    assert payload["retrieved_chunk_ids"] == ["c#1"]
    assert [c["chunk_id"] for c in payload["citations"]] == ["c#1"]


@pytest.mark.parametrize("text", INVALID, ids=INVALID_IDS)
def test_research_uncited_output_records_error_and_incomplete(engine, tmp_path, monkeypatch, text):
    _, provider = engine
    provider.text = text
    monkeypatch.setattr(run, "Retriever", FakeRetriever)
    monkeypatch.setattr(run, "load_dotenv", lambda: None)
    monkeypatch.setenv("LLM_EXPECTED_RESPONSE_MODEL", "fake-response-model")
    path = tmp_path / "synthetic-set.json"
    fixture = json.dumps({"version": "f01-fixture", "items": [
        {"item_id": "f01-ooc", "qtype": "out-of-corpus", "question": QUESTION,
         "expected_source_ids": []}]}, ensure_ascii=False) + "\n"
    path.write_text(fixture, encoding="utf-8", newline="\n")
    assert path.read_text(encoding="utf-8") == fixture
    report = run.run_eval(str(path), "data/research/embedding-compare/e5-large/c",
                          str(tmp_path / "unused"), language="c", model_key="e5-large",
                          mode="end-to-end")
    assert len(provider.prompts) == 1  # real _ask reached the real composer
    assert report["retrieval"]["status"] == "complete"
    assert report["retrieval"]["error_count"] == 0
    assert report["retrieval"]["rows"][0]["fixed_gate_abstain"] is False
    assert report["end_to_end"]["rows"][0]["response_type"] == "error"
    assert report["end_to_end"]["status"] == "incomplete"
    assert report["end_to_end"]["error_count"] == 1
    assert report["status"] == "incomplete" and report["error_count"] == 1
    assert not report["end_to_end"].get("final_metrics")
