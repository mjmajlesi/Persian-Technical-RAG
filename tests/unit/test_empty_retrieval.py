"""F13: empty retrieval retains pack identity without inventing C topics."""

from types import SimpleNamespace

import pytest

from src.qa import abstain
from src.web import app as web


LANGUAGES = ("c", "cpp", "python", "java")
QUESTION = "پرسش آزمایشی درباره موضوع انتخاب‌شده چیست؟"
NEUTRAL_MESSAGE = "در منابع موجود پاسخی برای این سوال پیدا نکردم."


@pytest.fixture
def engine(monkeypatch):
    calls = []
    hits = []

    class FakeRetriever:
        def retrieve(self, question, k=5):
            calls.append((question, k))
            return hits

    def forbidden_provider():
        pytest.fail("abstention before answering must not construct or call the provider")

    retriever = FakeRetriever()
    monkeypatch.setattr(web.pack_registry, "get_pack", lambda language: SimpleNamespace(
        language_id=language, status="ready"))
    monkeypatch.setattr(web, "get_retriever", lambda language: retriever)
    monkeypatch.setattr(web, "get_provider", forbidden_provider)
    return retriever, hits, calls


@pytest.mark.parametrize("language", LANGUAGES)
@pytest.mark.parametrize("injected", [False, True], ids=["student-route", "injected-hits"])
def test_empty_retrieval_echoes_language_and_uses_neutral_fallback(engine, language, injected):
    retriever, _, calls = engine
    request = web.AskRequest(question=QUESTION, language=language)
    if injected:
        response = web._ask(request, retriever=retriever, retrieved_chunks=[])
        assert calls == []
    else:
        response = web.ask(request)  # real endpoint function -> real _ask
        assert calls == [(QUESTION, 5)]
    assert response == {"type": "abstain", "language_id": language,
                        "message": NEUTRAL_MESSAGE, "suggested_topics": [], "citations": []}


@pytest.mark.parametrize("chunks", [[], [{"score": 0.0}]], ids=["empty", "no-topic-metadata"])
def test_shared_abstention_does_not_invent_topics_without_evidence(chunks):
    assert abstain.decide(chunks, 0.0, llm_insufficient=True) == {
        "message": NEUTRAL_MESSAGE, "suggested_topics": [], "citations": []}


@pytest.mark.parametrize("language", LANGUAGES)
def test_retrieved_topics_and_language_are_preserved_for_low_scores(engine, language):
    _, hits, calls = engine
    topic = f"موضوع ساختگی پک {language}"
    hits.extend([{"score": 0.0, "section_heading": topic},
                 {"score": 0.0, "section_heading": topic}])
    response = web.ask(web.AskRequest(question=QUESTION, language=language))
    assert response == {"type": "abstain", "language_id": language,
                        "message": abstain.MESSAGE_TEMPLATE.format(topics=topic),
                        "suggested_topics": [topic], "citations": []}
    assert calls == [(QUESTION, 5)]


def test_shared_abstention_still_allows_answer_above_gate():
    assert abstain.decide([], 1.0, llm_insufficient=False) is None
