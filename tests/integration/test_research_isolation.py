"""Research model/pack guards and no-LLM evaluation on frozen local indices."""

import json
from pathlib import Path

import pytest

from src.eval import run
from src.qa.retriever import Retriever
from src.web import app as web


PACKS = ("c", "cpp", "python", "java")
MODELS = ("e5-large", "e5-base", "bge-m3")


@pytest.mark.parametrize("pack", PACKS)
def test_wrong_model_and_pack_index_fail_before_retrieval(pack):
    directory = Path(f"data/research/embedding-compare/e5-base/{pack}")
    if not (directory / "faiss.index").is_file():
        pytest.skip("local research FAISS index required")
    with pytest.raises(ValueError, match="model_key|revision_sha|dimension"):
        Retriever(directory, model_key="bge-m3", pack_id=pack)
    other = next(language for language in PACKS if language != pack)
    with pytest.raises(ValueError, match="pack_id|canonical_chunks_path"):
        Retriever(directory, model_key="e5-base", pack_id=other)


@pytest.mark.parametrize("pack", PACKS)
@pytest.mark.parametrize("model", MODELS)
def test_retrieval_only_uses_selected_model_pack_and_never_calls_llm(pack, model, monkeypatch):
    directory = Path(f"data/research/embedding-compare/{model}/{pack}")
    if not (directory / "index-meta.json").is_file():
        pytest.skip("local research index metadata required")
    chunk_id = json.loads((directory / "ids.json").read_text(encoding="utf-8"))[0]
    calls = []

    class ScopedRetriever:
        def __init__(self, index_dir, *, model_key, pack_id):
            calls.append((Path(index_dir), model_key, pack_id))

        def retrieve(self, question, k=5):
            return [{"chunk_id": chunk_id, "score": 0.9}]

    def no_llm(*args, **kwargs):
        pytest.fail("retrieval-only must not touch the LLM or answer path")

    monkeypatch.setattr(run, "Retriever", ScopedRetriever)
    monkeypatch.setattr(run.web, "get_provider", no_llm)
    monkeypatch.setattr(run.web, "_ask", no_llm)
    monkeypatch.setattr(run, "load_dotenv", no_llm)
    report = run.run_eval(f"data/eval/{pack}/eval-set.{pack}.v2.json", str(directory),
                          "unused", language=pack, model_key=model, mode="retrieval-only")
    assert calls == [(directory, model, pack)]
    assert report["status"] == report["retrieval"]["status"] == "complete"
    assert len(report["retrieval"]["rows"]) == 45
    assert report["end_to_end"]["status"] == "not_run" and report["error_count"] == 0


@pytest.mark.parametrize("bypass_composer", (False, True))
def test_foreign_citation_abstains_even_when_composer_guard_is_bypassed(bypass_composer, monkeypatch):
    directory = Path("data/research/embedding-compare/e5-base/c")
    if not (directory / "faiss.index").is_file():
        pytest.skip("local research FAISS index required")
    retriever = Retriever(directory, model_key="e5-base", pack_id="c")
    chunk = dict(next(iter(retriever._by_id.values())), score=0.99)
    foreign = json.loads(Path("data/index/cpp/ids.json").read_text(encoding="utf-8"))[0]
    assert retriever.has_chunk(chunk["chunk_id"]) and not retriever.has_chunk(foreign)

    class Provider:
        def generate(self, prompt, context=""):
            return f"پاسخ نادرست [{foreign}]"

    if bypass_composer:
        monkeypatch.setattr(web, "compose_answer", lambda *args: {
            "insufficient": False, "answer_text": "forged",
            "citations": [{"chunk_id": foreign}],
            "retrieved_chunk_ids": [chunk["chunk_id"]],
        })
    response = web._ask(web.AskRequest(question="اشاره‌گر در سی چگونه کار می‌کند؟",
                                       language="c"), retriever=retriever,
                        threshold=0.0, provider=Provider(), retrieved_chunks=[chunk])
    assert response["type"] == "abstain" and response["citations"] == []
