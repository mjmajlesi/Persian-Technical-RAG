"""FAIL-first research modes contract (003-T015); synthetic items, no API/model calls."""

import json
from pathlib import Path
from types import SimpleNamespace

from src.eval import run
from src.web import app as web


QUESTIONS = ("پرسش آزمایشی درباره اشاره‌گر در سی چیست؟",
             "پرسش آزمایشی مرزی درباره اشاره‌گر چیست؟",
             "پرسش آزمایشی با ارجاع نامعتبر چیست؟")
GATE = 0.808958888053894  # locked E5-large pooled-v1, not the operational C gate


def _fixture(tmp_path, monkeypatch, *, identity_ok=True):
    path = tmp_path / "eval-set.c.fixture.json"
    path.write_text(json.dumps({"version": "c-fixture", "items": [
        {"item_id": f"fixture-{i}", "qtype": "out-of-corpus" if i == 1 else "in-corpus",
         "question": question, "expected_source_ids": [] if i == 1 else ["c#1"]}
        for i, question in enumerate(QUESTIONS)
    ]}, ensure_ascii=False), encoding="utf-8")
    assert "آزمایشی" in path.read_text(encoding="utf-8")

    calls = {"retrievers": [], "retrievals": [], "llm": []}

    class FakeRetriever:
        def __init__(self, directory, *, model_key=None, pack_id=None):
            calls["retrievers"].append((str(directory).replace("\\", "/"),
                                        model_key, pack_id))
            self._by_id = {cid: {"chunk_id": cid} for cid in ("c#1", "c#2")}

        def retrieve(self, question, k=5):
            calls["retrievals"].append((question, k))
            score = 0.805 if question == QUESTIONS[1] else 0.85
            return [{"chunk_id": cid, "score": score, "doc_title": "C",
                     "section_heading": "اشاره‌گر", "text": "متن شاهد"}
                    for cid in ("c#1", "c#2")][:k]

        def has_chunk(self, chunk_id):
            # The retrieved second ID is NOT a member of the selected pack.
            return chunk_id == "c#1"

    class FakeProvider:
        def generate(self, prompt, context=""):
            calls["llm"].append(prompt)
            return "پاسخ مستند [c#2]" if QUESTIONS[2] in prompt else "پاسخ مستند [c#1]"

        def generate_with_metadata(self, prompt, context="", *, expected_model_id):
            if not identity_ok:
                from src.qa.provider import ProviderError
                raise ProviderError("unexpected API response model ID")
            return {"text": self.generate(prompt, context), "provider": "openai-compatible",
                    "request_timestamp": "2026-10-23T00:00:00+00:00",
                    "model": expected_model_id, "temperature": 0}

    monkeypatch.setattr(run, "Retriever", FakeRetriever)
    monkeypatch.setattr(web.pack_registry, "get_pack", lambda lang: SimpleNamespace(
        status="ready", language_id=lang))
    monkeypatch.setattr(web, "get_provider", lambda: FakeProvider())
    monkeypatch.setattr(web, "get_retriever", lambda *args: (_ for _ in ()).throw(
        AssertionError("research must inject its own scoped retriever")))
    monkeypatch.setenv("LLM_EXPECTED_RESPONSE_MODEL", "response-model-2026")
    return path, calls


def _research(path, mode):
    return run.run_eval(str(path), "data/research/embedding-compare/e5-large/c",
                        "unused-report-dir", language="c", model_key="e5-large",
                        mode=mode, contamination_set_path=None)


def test_retrieval_only_zero_llm_and_same_research_top5_as_e2e(tmp_path, monkeypatch):
    path, calls = _fixture(tmp_path, monkeypatch)
    retrieval = _research(path, "retrieval-only")
    assert calls["llm"] == []
    assert retrieval["retrieval"]["status"] == "complete"
    assert len(retrieval["retrieval"]["rows"]) == 3
    assert all(row["top5_ids"] == ["c#1", "c#2"]
               for row in retrieval["retrieval"]["rows"])
    assert retrieval["retrieval"]["rows"][1]["fixed_gate_abstain"] is True
    assert retrieval["end_to_end"]["status"] == "not_run"
    assert all(model == "e5-large" and pack == "c" and
               directory.endswith("e5-large/c")
               for directory, model, pack in calls["retrievers"])

    e2e = _research(path, "end-to-end")
    assert [r["top5_ids"] for r in retrieval["retrieval"]["rows"]] == [
        r["top5_ids"] for r in e2e["retrieval"]["rows"]]
    assert e2e["retrieval"]["status"] == "complete"
    assert e2e["end_to_end"]["rows"][1]["response_type"] == "abstain"
    assert e2e["end_to_end"]["rows"][2]["response_type"] == "abstain"
    assert e2e["end_to_end"]["rows"][0]["response_type"] == "answer"
    assert len(calls["llm"]) == 2  # gate stops the marginal item before provider
    assert e2e["calibration"]["threshold"] == GATE


def test_provider_identity_failure_keeps_retrieval_but_not_e2e(tmp_path, monkeypatch):
    path, _ = _fixture(tmp_path, monkeypatch, identity_ok=False)
    result = _research(path, "end-to-end")
    assert result["retrieval"]["status"] == "complete"
    assert len(result["retrieval"]["rows"]) == 3
    assert result["end_to_end"]["status"] == "incomplete"
    assert result["end_to_end"]["error_count"] > 0
    assert not result["end_to_end"].get("final_metrics")


def test_research_cli_selects_model_pack_and_retrieval_mode(tmp_path, monkeypatch):
    path, _ = _fixture(tmp_path, monkeypatch)
    observed = {}

    def fake_run_eval(*args, **kwargs):
        observed["args"], observed["kwargs"] = args, kwargs
        return {"retrieval": {"status": "complete", "rows": []},
                "end_to_end": {"status": "not_run"}, "error_count": 0,
                "hit_rate_at_5": 1.0, "citation_precision": 0.0,
                "citation_coverage": 0.0, "abstention_correct": "0/0"}

    monkeypatch.setattr(run, "run_eval", fake_run_eval)
    monkeypatch.setattr(run, "write_reports", lambda report, directory: ("a.json", "a.md"))
    assert run.main(["run", "--lang", "c", "--set", str(path), "--model", "e5-large",
                     "--mode", "retrieval-only", "--contamination-set", ""]) == 0
    args = observed["args"]
    assert args[0] == str(path)
    assert args[1].replace("\\", "/").endswith("embedding-compare/e5-large/c")
    assert observed["kwargs"]["model_key"] == "e5-large"
    assert observed["kwargs"]["mode"] == "retrieval-only"


def test_default_cli_still_uses_operational_v1(monkeypatch):
    observed = {}

    def fake_run_eval(*args):
        observed["args"] = args
        return {"hit_rate_at_5": 1.0, "citation_precision": 1.0,
                "citation_coverage": 1.0, "abstention_correct": "5/5",
                "error_count": 0}

    monkeypatch.setattr(run, "run_eval", fake_run_eval)
    monkeypatch.setattr(run, "write_reports", lambda report, directory: ("a.json", "a.md"))
    assert run.main(["run", "--lang", "c", "--contamination-set", ""]) == 0
    args = observed["args"]
    assert args[0] == run.default_set_path("c")
    assert Path(args[0]).name == "eval-set.c.v1.json"
    assert args[1:4] == ("data/index/c", "data/eval/c/reports", 5)
    assert args[4:] == ("c", "")
