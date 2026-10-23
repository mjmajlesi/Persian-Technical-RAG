"""FAIL-first contract for auditable research LLM calls (003-T013)."""

import json
from datetime import datetime

import pytest

from src.qa.provider import LLMProvider, ProviderConfig, ProviderError


SECRET = "test-secret-please-never-publish"
EXPECTED = "response-model-2026"


def _mock_api(monkeypatch, bodies, *, reject_temperature=False):
    requests = []
    responses = iter(bodies)

    class Response:
        def __init__(self, body):
            self.body = body

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def read(self):
            return self.body.encode("utf-8")

    def urlopen(request, timeout):
        requests.append(request)
        if reject_temperature:
            raise ValueError("temperature parameter rejected: " + SECRET)
        return Response(next(responses))

    monkeypatch.setattr("urllib.request.urlopen", urlopen)
    return requests


def _provider():
    # Requested alias deliberately differs from the API-returned model ID.
    return LLMProvider(ProviderConfig(SECRET, base_url="https://private.invalid/v1",
                                      model="request-alias"))


def _json(model=EXPECTED):
    return json.dumps({"model": model, "choices": [{"message": {"content": "پاسخ"}}]},
                      ensure_ascii=False)


def _sse(*models):
    return "\n".join("data: " + json.dumps({
        "model": model, "choices": [{"delta": {"content": "پاسخ" if i == 0 else " دوم"}}],
    }, ensure_ascii=False) for i, model in enumerate(models)) + "\ndata: [DONE]\n"


@pytest.mark.parametrize("body", [_json(), _sse(EXPECTED, EXPECTED)], ids=["json", "sse"])
def test_research_call_sends_zero_and_records_api_identity(monkeypatch, body):
    requests = _mock_api(monkeypatch, [body])
    result = _provider().generate_with_metadata("سؤال", expected_model_id=EXPECTED)
    payload = json.loads(requests[0].data)
    assert payload["temperature"] == 0
    assert payload["model"] == "request-alias"
    assert result["text"].startswith("پاسخ")
    assert result["provider"] == "openai-compatible"
    assert result["model"] == EXPECTED  # API return, never the request alias
    assert result["temperature"] == 0
    assert datetime.fromisoformat(result["request_timestamp"]).tzinfo is not None
    assert SECRET not in str(result)
    assert "private.invalid" not in str(result)


@pytest.mark.parametrize("body", [
    _json(None), _json(""), _json("other-model"),
    _sse(EXPECTED, "other-model"), _sse(EXPECTED, None),
], ids=["json-null", "json-empty", "json-unexpected", "sse-changing", "sse-missing"])
def test_missing_changing_or_unexpected_response_model_is_incomplete(monkeypatch, body):
    _mock_api(monkeypatch, [body])
    with pytest.raises(ProviderError, match="model|identit") as error:
        _provider().generate_with_metadata("سؤال", expected_model_id=EXPECTED)
    assert SECRET not in str(error.value)
    assert "private.invalid" not in str(error.value)


def test_id_is_checked_on_every_response_not_only_first(monkeypatch):
    _mock_api(monkeypatch, [_json(), _json("other-model")])
    provider = _provider()
    assert provider.generate_with_metadata("اول", expected_model_id=EXPECTED)["model"] == EXPECTED
    with pytest.raises(ProviderError, match="model|identit"):
        provider.generate_with_metadata("دوم", expected_model_id=EXPECTED)


def test_rejected_temperature_is_not_a_success_or_a_secret_leak(monkeypatch):
    requests = _mock_api(monkeypatch, [], reject_temperature=True)
    with pytest.raises(ProviderError, match="temperature") as error:
        _provider().generate_with_metadata("سؤال", expected_model_id=EXPECTED)
    assert json.loads(requests[0].data)["temperature"] == 0
    assert SECRET not in str(error.value)
    assert "private.invalid" not in str(error.value)


def test_retrieval_only_does_not_construct_or_call_provider(monkeypatch):
    from src.qa import retriever as retrieval

    def forbidden(*args, **kwargs):
        pytest.fail("retrieval-only must not touch LLM provider")

    monkeypatch.setattr(LLMProvider, "__init__", forbidden)
    monkeypatch.setattr(retrieval, "embed_queries", lambda questions: [[1.0]])
    monkeypatch.setattr(retrieval.faiss_store, "search",
                        lambda index, ids, query, k: [("c#1", 0.9)])
    instance = object.__new__(retrieval.Retriever)
    instance._model_key = None
    instance._index = object()
    instance._ids = ["c#1"]
    instance._by_id = {"c#1": {"chunk_id": "c#1"}}
    assert instance.retrieve("سؤال", k=1) == [{"chunk_id": "c#1", "score": 0.9}]
