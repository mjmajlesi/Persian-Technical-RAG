"""LLM provider interface (T011).

Thin, OpenAI-compatible chat provider: reads credentials from the environment
(LLM_API_KEY, LLM_BASE_URL, LLM_MODEL), so proxies like the user's 9router
setup work by setting LLM_BASE_URL/LLM_MODEL — nothing is hardcoded.
Standard library only (urllib); a minimal .env loader is included so no new
dependency is needed. The key is never logged or written anywhere.
"""

from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass

DEFAULT_BASE_URL = "https://api.openai.com/v1"
REQUEST_TIMEOUT = 120  # seconds


class ProviderError(RuntimeError):
    """Raised for configuration problems or failed LLM calls."""


def load_dotenv(path: str = ".env") -> None:
    """Minimal .env loader (KEY=value lines, # comments, quotes stripped).

    Existing process environment variables take precedence and are kept.
    """
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError:
        return
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip("\"'")
        if key and key not in os.environ:
            os.environ[key] = value


@dataclass
class ProviderConfig:
    api_key: str
    base_url: str = DEFAULT_BASE_URL
    model: str = ""

    @classmethod
    def from_env(cls) -> "ProviderConfig":
        load_dotenv()
        api_key = os.environ.get("LLM_API_KEY", "").strip()
        if not api_key:
            raise ProviderError(
                "LLM_API_KEY is not set. Copy .env.example to .env and fill it in."
            )
        return cls(
            api_key=api_key,
            base_url=os.environ.get("LLM_BASE_URL", DEFAULT_BASE_URL).strip().rstrip("/"),
            model=os.environ.get("LLM_MODEL", "").strip(),
        )


class LLMProvider:
    """Concrete OpenAI-compatible chat provider (POST {base}/chat/completions)."""

    def __init__(self, config: ProviderConfig):
        if not config.model:
            raise ProviderError(
                "LLM_MODEL is not set. Copy .env.example to .env and fill it in."
            )
        self._config = config

    def generate(self, prompt: str, context: str = "") -> str:
        """Send prompt (+ optional retrieved context) and return answer text."""
        user_content = prompt if not context else f"{prompt}\n\n{context}"
        payload = {
            "model": self._config.model,
            "stream": False,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant that answers "
                        "ONLY from the provided context."
                    ),
                },
                {"role": "user", "content": user_content},
            ],
        }
        request = urllib.request.Request(
            f"{self._config.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._config.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as resp:
                raw = resp.read().decode("utf-8")
        except Exception as exc:  # noqa: BLE001 - mapped to ProviderError
            raise ProviderError(f"LLM request failed: {exc}") from exc
        try:
            if raw.lstrip().startswith("data:"):
                parts = []
                for line in raw.splitlines():
                    if not line.startswith("data:") or line.strip() == "data: [DONE]":
                        continue
                    choice = json.loads(line[5:].strip())["choices"][0]
                    parts.append(choice.get("delta", {}).get("content") or "")
                if not "".join(parts).strip():
                    raise ValueError("no streamed content")
                return "".join(parts)
            return json.loads(raw)["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise ProviderError("unexpected LLM response shape") from exc
