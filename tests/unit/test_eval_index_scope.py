"""F14: v1 retrieval and web answers must use the same operational index."""

import json
from pathlib import Path

import pytest

from src.eval import run


@pytest.fixture
def eval_fixture(tmp_path, monkeypatch):
    path = tmp_path / "fixture.json"
    contents = json.dumps({"version": "synthetic", "items": [{
        "item_id": "fixture", "qtype": "in-corpus", "question": "پرسش ساختگی درباره سی چیست؟",
        "expected_source_ids": ["c#1"]}]}, ensure_ascii=False) + "\n"
    path.write_text(contents, encoding="utf-8", newline="\n")
    assert path.read_text(encoding="utf-8") == contents
    calls = []

    class FakeRetriever:
        def __init__(self, directory):
            calls.append(("index", str(directory)))
            self._by_id = {"c#1": {}}

        def retrieve(self, question, k=5):
            calls.append(("retrieve", question))
            return [{"chunk_id": "c#1", "score": 1.0}]

    def fake_ask(request):
        calls.append(("ask", request.language))
        return {"type": "answer", "citations": [{"chunk_id": "c#1"}]}

    monkeypatch.setattr(run, "Retriever", FakeRetriever)
    monkeypatch.setattr(run, "ask", fake_ask)
    return path, calls


@pytest.mark.parametrize("language", ["c", "cpp", "python", "java"])
def test_v1_rejects_mismatched_index_before_read_or_retrieval(tmp_path, monkeypatch, language, eval_fixture):
    path, _ = eval_fixture
    def forbidden(*args, **kwargs):
        pytest.fail("invalid override must be rejected before retrieval or web ask")
    monkeypatch.setattr(run, "Retriever", forbidden)
    monkeypatch.setattr(run, "ask", forbidden)
    with pytest.raises(ValueError, match="(?i)index.dir.*(?:selected|operational|language)"):
        run.run_eval(str(path), str(tmp_path / "wrong-index"),
                     str(tmp_path), language=language)


@pytest.mark.parametrize("spelling", ["relative", "absolute", "dot-segments"])
def test_equivalent_default_index_runs_v1(eval_fixture, tmp_path, spelling):
    path, calls = eval_fixture
    default = Path("data/index/c")
    index = {"relative": str(default), "absolute": str(default.resolve()),
             "dot-segments": str(default / ".." / "c")}[spelling]
    report = run.run_eval(str(path), index, str(tmp_path), language="c")
    assert [call[0] for call in calls] == ["index", "retrieve", "ask"]
    assert report["language_id"] == "c" and report["error_count"] == 0
    assert report["per_item_rows"][0]["response_type"] == "answer"


def test_v1_cli_default_still_uses_canonical_index(eval_fixture, tmp_path, monkeypatch):
    path, calls = eval_fixture
    monkeypatch.setattr(run, "write_reports", lambda report, directory: ("fake.json", "fake.md"))
    assert run.main(["run", "--lang", "c", "--set", str(path),
                     "--report-dir", str(tmp_path), "--contamination-set", ""]) == 0
    assert calls[0] == ("index", "data/index/c")
    assert calls[-1] == ("ask", "c")


def test_research_003_keeps_its_index_dispatch(tmp_path, monkeypatch):
    calls = []
    sentinel = {"research": "ok"}
    monkeypatch.setattr(run, "_run_research_eval", lambda *args: calls.append(args) or sentinel)
    directory = "data/research/embedding-compare/e5-base/c"
    assert run.run_eval("synthetic-set", directory, str(tmp_path), language="c",
                        model_key="e5-base", mode="retrieval-only") is sentinel
    assert calls == [("synthetic-set", directory, 5, "c", "e5-base", "retrieval-only")]
