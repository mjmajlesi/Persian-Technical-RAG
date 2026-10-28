"""F12: malformed provider responses fail at the shared provider boundary."""

import json

import pytest

from src.qa.provider import LLMProvider, ProviderConfig, ProviderError


MODEL = "synthetic-response-model"
SECRET = "synthetic-private-response-marker"


def _json(choices):
    return json.dumps({"model": MODEL, "choices": choices})


def _sse(event):
    return "data: " + json.dumps(event) + "\ndata: [DONE]\n"


BAD_RESPONSES = [
    pytest.param('{"broken": ' + SECRET, id="invalid-json"),
    pytest.param("null", id="null-root"),
    pytest.param("[]", id="array-root"),
    pytest.param(json.dumps({"model": MODEL, "private": SECRET}), id="missing-choices"),
    pytest.param(_json(None), id="null-choices"),
    pytest.param(_json([]), id="empty-choices"),
    pytest.param(_json([None]), id="null-choice"),
    pytest.param(_json([{}]), id="missing-message"),
    pytest.param(_json([{"message": None}]), id="null-message"),
    pytest.param(_json([{"message": {}}]), id="missing-content"),
    *[pytest.param(_json([{"message": {"content": content}}]), id=name)
      for name, content in [("null-content", None), ("numeric-content", 7),
                            ("array-content", [SECRET]), ("object-content", {"private": SECRET})]],
    pytest.param("data: {" + SECRET, id="sse-invalid-json"),
    pytest.param(_sse(None), id="sse-null-event"),
    pytest.param(_sse([]), id="sse-array-event"),
    pytest.param(_sse({"model": MODEL, "choices": [{"delta": None}]}), id="sse-null-delta"),
    pytest.param(_sse({"model": MODEL, "choices": [{"delta": []}]}), id="sse-array-delta"),
    pytest.param(_sse({"model": MODEL, "choices": [{"delta": {"content": 7}}]}),
                 id="sse-numeric-content"),
    pytest.param(_sse({"model": MODEL, "choices": [{"delta": {"content": None}}]}),
                 id="sse-only-null-content"),
    *[pytest.param("\n".join("data: " + json.dumps({"model": MODEL, "choices": [
        {"delta": {"content": part}}]}) for part in (content, "پاسخ")) + "\ndata: [DONE]\n",
                   id=name)
      for name, content in [("sse-zero-before-text", 0), ("sse-false-before-text", False),
                            ("sse-empty-array-before-text", []), ("sse-empty-object-before-text", {})]],
]


@pytest.fixture
def call_provider(monkeypatch):
    def call(body, research):
        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

            def read(self):
                return body.encode("utf-8")

        monkeypatch.setattr("urllib.request.urlopen", lambda request, timeout: Response())
        provider = LLMProvider(ProviderConfig(SECRET, base_url="https://private.invalid/v1",
                                              model="synthetic-request-alias"))
        if research:
            return provider.generate_with_metadata("پرسش ساختگی", expected_model_id=MODEL)["text"]
        return provider.generate("پرسش ساختگی")

    return call


@pytest.mark.parametrize("research", [False, True], ids=["ordinary", "research"])
@pytest.mark.parametrize("body", BAD_RESPONSES)
def test_malformed_response_is_standard_sanitized_provider_error(call_provider, research, body):
    with pytest.raises(ProviderError, match="unexpected LLM response shape") as caught:
        call_provider(body, research)
    assert type(caught.value) is ProviderError
    assert SECRET not in str(caught.value) and "private.invalid" not in str(caught.value)
    assert caught.value.__suppress_context__ is True


@pytest.mark.parametrize("research", [False, True], ids=["ordinary", "research"])
@pytest.mark.parametrize("text", ["پاسخ معتبر", "", " \t\n ", "CANNOT_ANSWER"],
                         ids=["text", "empty-for-composer", "whitespace-for-composer", "sentinel"])
def test_json_text_remains_a_string_for_the_composer(call_provider, research, text):
    assert call_provider(_json([{"message": {"content": text}}]), research) == text


@pytest.mark.parametrize("research", [False, True], ids=["ordinary", "research"])
def test_sse_role_and_null_deltas_before_valid_text_remain_supported(call_provider, research):
    body = "\n".join("data: " + json.dumps({"model": MODEL, "choices": [{"delta": delta}]})
                     for delta in ({"role": "assistant"}, {"content": None}, {"content": "پاسخ"}))
    assert call_provider(body + "\ndata: [DONE]\n", research) == "پاسخ"
