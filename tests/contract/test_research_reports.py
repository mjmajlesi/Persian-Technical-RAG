"""Official v2 report contract, without model downloads or LLM calls."""

import hashlib
import json
import subprocess
from pathlib import Path

from src.eval import run


SET = Path("data/eval/c/eval-set.c.v2.json")
INDEX = Path("data/research/embedding-compare/e5-large/c")


class FakeRetriever:
    def __init__(self, directory, *, model_key, pack_id):
        assert model_key == "e5-large" and pack_id == "c" and Path(directory) == INDEX

    def retrieve(self, question, k=5):
        return [{"chunk_id": "fa-vars-types-operators#s02-c01", "score": 0.9}]


def test_complete_retrieval_report_is_stageable_and_identifies_frozen_inputs(tmp_path, monkeypatch):
    monkeypatch.setattr(run, "Retriever", FakeRetriever)
    monkeypatch.setattr(run.web, "get_provider", lambda: (_ for _ in ()).throw(
        AssertionError("retrieval-only must make zero LLM calls")))
    report = run.run_eval(str(SET), str(INDEX), str(tmp_path), language="c",
                          model_key="e5-large", mode="retrieval-only")
    assert report["status"] == "complete"
    assert report["retrieval"]["status"] == "complete"
    assert len(report["retrieval"]["rows"]) == 45
    assert report["end_to_end"]["status"] == "not_run"
    assert report["model"]["revision_sha"] == run.get_model_candidate("e5-large").revision_sha
    assert report["v2_sha256"] == hashlib.sha256(SET.read_bytes()).hexdigest()
    assert report["index"]["chunk_sha256"] == hashlib.sha256(
        Path("data/index/c/chunks.jsonl").read_bytes()).hexdigest()
    assert len(report["index"]["ordered_ids_sha256"]) == 64
    assert report["index"]["dimension"] == 1024
    assert report["snapshot"] == "2026-09-23"
    assert report["calibration"]["n_answerable"] == 100
    assert report["calibration"]["n_out"] == 20
    assert len(report["calibration"]["per_language_confusion"]) == 4
    assert report["started_at"] and report["elapsed_seconds"] >= 0
    path, markdown = run.write_reports(report, str(tmp_path / "reports"))
    saved = json.loads(Path(path).read_text(encoding="utf-8"))
    assert saved["retrieval"]["rows"] == report["retrieval"]["rows"]
    assert "45 rows" in Path(markdown).read_text(encoding="utf-8")
    assert Path(path).read_bytes() == Path(path).read_text(encoding="utf-8").encode("utf-8")
    assert Path(markdown).read_bytes() == Path(markdown).read_text(encoding="utf-8").encode("utf-8")
    second, _ = run.write_reports(report, str(tmp_path / "reports"))
    assert second != path and Path(path).exists() and Path(second).exists()
    assert subprocess.run(["git", "check-ignore", "-q", "--", "data/eval/c/reports/v2/e5-large/official.json"]).returncode == 1
    for artifact in ("data/research/embedding-compare/e5-large/c/faiss.index",
                     "data/research/embedding-compare/e5-large/c/embeddings-example.npy",
                     "data/eval/c/reports/v2/e5-large/official.diagnostics.json"):
        assert subprocess.run(["git", "check-ignore", "-q", "--", artifact]).returncode == 0


def test_incomplete_e2e_retains_complete_retrieval_but_not_partial_official_rows(tmp_path, monkeypatch):
    monkeypatch.setattr(run, "Retriever", FakeRetriever)
    monkeypatch.setattr(run, "load_dotenv", lambda: None)
    monkeypatch.delenv("LLM_EXPECTED_RESPONSE_MODEL", raising=False)
    report = run.run_eval(str(SET), str(INDEX), str(tmp_path), language="c",
                          model_key="e5-large", mode="end-to-end")
    assert report["status"] == "incomplete" and report["retrieval"]["status"] == "complete"
    assert len(report["retrieval"]["rows"]) == 45
    assert report["end_to_end"]["status"] == "incomplete"
    assert report["end_to_end"]["error_count"] == 45
    path, _ = run.write_reports(report, str(tmp_path / "reports"))
    official = json.loads(Path(path).read_text(encoding="utf-8"))
    assert len(official["retrieval"]["rows"]) == 45
    assert official["end_to_end"]["status"] == "incomplete"
    assert "rows" not in official["end_to_end"] and "final_metrics" not in official["end_to_end"]
    diagnostics = json.loads(next((tmp_path / "reports").glob("*.diagnostics.json"))
                             .read_text(encoding="utf-8"))
    assert len(diagnostics["end_to_end_rows"]) == 45


def test_complete_e2e_publishes_verified_provider_metadata_without_credentials(tmp_path, monkeypatch):
    monkeypatch.setattr(run, "Retriever", FakeRetriever)
    monkeypatch.setattr(run, "load_dotenv", lambda: None)
    monkeypatch.setenv("LLM_EXPECTED_RESPONSE_MODEL", "fixed-api-model")
    monkeypatch.setenv("LLM_API_KEY", "private-test-token")
    monkeypatch.setenv("LLM_BASE_URL", "https://private.example")

    class Provider:
        def generate_with_metadata(self, prompt, context="", *, expected_model_id):
            assert expected_model_id == "fixed-api-model"
            return {"text": "answer", "provider": "openai-compatible",
                    "request_timestamp": "2026-10-25T00:00:00+00:00",
                    "model": expected_model_id, "temperature": 0}

    monkeypatch.setattr(run.web, "get_provider", lambda: Provider())

    def fake_ask(request, *, retriever, threshold, provider, retrieved_chunks):
        provider.generate("prompt-for-" + request.question)
        return {"type": "answer", "citations": [{"chunk_id": retrieved_chunks[0]["chunk_id"]}]}

    monkeypatch.setattr(run.web, "_ask", fake_ask)
    report = run.run_eval(str(SET), str(INDEX), str(tmp_path), language="c",
                          model_key="e5-large", mode="end-to-end")
    assert report["status"] == report["end_to_end"]["status"] == "complete"
    assert len(report["retrieval"]["rows"]) == len(report["end_to_end"]["rows"]) == 45
    path, _ = run.write_reports(report, str(tmp_path / "reports"))
    text = Path(path).read_text(encoding="utf-8")
    metadata = json.loads(text)["end_to_end"]["rows"][0]["llm_metadata"]
    assert metadata["model"] == "fixed-api-model"
    assert metadata["provider"] == "openai-compatible"
    assert metadata["request_timestamp"] == "2026-10-25T00:00:00+00:00"
    assert metadata["temperature"] == 0 and len(metadata["prompt_sha256"]) == 64
    assert "private-test-token" not in text and "private.example" not in text


def test_incomplete_retrieval_only_writes_diagnostics_not_official_json(tmp_path, monkeypatch):
    class BrokenRetriever(FakeRetriever):
        def retrieve(self, question, k=5):
            raise RuntimeError("offline")

    monkeypatch.setattr(run, "Retriever", BrokenRetriever)
    report = run.run_eval(str(SET), str(INDEX), str(tmp_path), language="c",
                          model_key="e5-large", mode="retrieval-only")
    assert report["status"] == "incomplete" and report["retrieval"]["error_count"] == 45
    path, markdown = run.write_reports(report, str(tmp_path / "reports"))
    assert Path(path).name.endswith(".diagnostics.json")
    assert json.loads(Path(path).read_text(encoding="utf-8"))["status"] == "diagnostics-only"
    assert list((tmp_path / "reports").glob("*.json")) == [Path(path)]
    assert "incomplete" in Path(markdown).read_text(encoding="utf-8")


def test_v2_missing_item_cannot_become_complete_official_report(tmp_path, monkeypatch):
    data = json.loads(SET.read_text(encoding="utf-8"))
    data["items"].pop()
    reduced = tmp_path / "incomplete-v2.json"
    reduced.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(run, "Retriever", FakeRetriever)
    report = run.run_eval(str(reduced), str(INDEX), str(tmp_path), language="c",
                          model_key="e5-large", mode="retrieval-only")
    assert len(report["retrieval"]["rows"]) == 44
    assert report["status"] == report["retrieval"]["status"] == "incomplete"
    path, _ = run.write_reports(report, str(tmp_path / "reports"))
    assert path.endswith(".diagnostics.json")
