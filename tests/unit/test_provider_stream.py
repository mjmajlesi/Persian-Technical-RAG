"""The local OpenAI-compatible proxy may stream even with stream=False."""

import json

from src.qa.provider import LLMProvider, ProviderConfig


def test_provider_accepts_proxy_sse_response(monkeypatch):
    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def read(self):
            events = [
                {"choices": [{"delta": {"role": "assistant"}}]},
                {"choices": [{"delta": {"content": "سلام"}}]},
                {"choices": [{"delta": {"content": " دنیا"}}]},
            ]
            return ("\n".join("data: " + json.dumps(e, ensure_ascii=False)
                              for e in events) + "\ndata: [DONE]\n").encode()

    def fake_urlopen(request, timeout):
        assert json.loads(request.data)["stream"] is False
        return Response()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    assert LLMProvider(ProviderConfig("key", model="test")).generate("hi") == "سلام دنیا"


def test_provider_still_accepts_json_response(monkeypatch):
    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def read(self):
            return b'{"choices":[{"message":{"content":"hello"}}]}'

    monkeypatch.setattr("urllib.request.urlopen", lambda request, timeout: Response())
    assert LLMProvider(ProviderConfig("key", model="test")).generate("hi") == "hello"
