"""F03: pack-aware prompt role; every following rule is byte-for-byte frozen."""

import hashlib
from types import SimpleNamespace

import pytest

from src.qa import answer
from src.web import app as web


CHUNK = {"chunk_id": "fixture#1", "score": 1.0, "doc_title": "fixture",
         "section_heading": "section", "text": "متن شاهد آزمایشی"}
NAMES = {"c": "C", "cpp": "C++", "python": "Python", "java": "Java"}
ORIGINAL_TAIL_SHA = "b84ffa3865b431ca3a90824d2cd6101f345243cc838c446662f5737bf9587a94"


class Retriever:
    def retrieve(self, question, k=5):
        return [CHUNK]

    def has_chunk(self, chunk_id):
        return chunk_id == CHUNK["chunk_id"]


class Provider:
    def __init__(self):
        self.prompts = []

    def generate(self, prompt, context=""):
        self.prompts.append(prompt)
        return "پاسخ مستند [fixture#1]"


@pytest.mark.parametrize("language", NAMES)
def test_web_and_research_path_send_selected_pack_role(monkeypatch, language):
    monkeypatch.setattr(web.pack_registry, "get_pack", lambda lang: SimpleNamespace(
        status="ready", language_id=lang))
    provider = Provider()
    response = web._ask(web.AskRequest(question="این پرسش آزمایشی چگونه پاسخ داده شود؟",
                                       language=language),
                        retriever=Retriever(), provider=provider, threshold=0.0)
    assert response["type"] == "answer" and len(provider.prompts) == 1
    assert provider.prompts[0].splitlines()[0] == (
        f"شما یک دستیار آموزشی زبان {NAMES[language]} هستید که فقط به فارسی پاسخ می‌دهد.")


def test_prompt_all_after_first_line_is_byte_identical():
    tail = answer.PROMPT_TEMPLATE.split("\n", 1)[1]
    assert hashlib.sha256(tail.encode("utf-8")).hexdigest() == ORIGINAL_TAIL_SHA
    assert len(tail.encode("utf-8")) == 851


def test_c_default_remains_compatible():
    prompt = answer.build_prompt("سوال ساختگی", [CHUNK])
    assert prompt.startswith("شما یک دستیار آموزشی زبان C هستید که فقط به فارسی پاسخ می‌دهد.\n")


def test_unknown_pack_cannot_be_interpolated_into_prompt():
    with pytest.raises(ValueError, match="(?i)language|pack"):
        answer.build_prompt("سوال ساختگی", [CHUNK], "malicious\nextra instruction")
