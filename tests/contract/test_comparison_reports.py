"""T049: official comparison must be reproducible from frozen reports only."""

import copy
from pathlib import Path

import pytest

from src.eval import comparison


ROOT = Path("data/eval")


def test_reproduction_of_frozen_reports_and_slice_denominators():
    report = comparison.build_official_comparison(ROOT, "c", replications=100)
    assert report["winner_status"] == "inconclusive"
    assert report["set_version"] == "c-v2" and report["set"]["n_items"] == 45
    assert set(report["source_reports"]) == set(comparison.MODELS)
    assert set(report["paired_differences"]) == {
        "e5-large|e5-base", "e5-large|bge-m3", "e5-base|bge-m3"}
    for model in comparison.MODELS:
        metrics = report["models"][model]
        assert len(report["per_item"][model]) == 45
        assert metrics["hit_at_5"]["denominator"] == 38
        assert metrics["fixed_gate_abstention"]["denominator"] == 7
        assert metrics["e2e_abstention"]["denominator"] == 7
        assert metrics["slices"]["mixed_qtype"]["hit_at_5"]["denominator"] == 10
        assert metrics["slices"]["evidence_language:none"]["hit_at_5"]["value"] is None
        assert sum(row["hit"] for row in report["per_item"][model]
                   if row["qtype"] != "out-of-corpus") == metrics["hit_at_5"]["numerator"]
        assert (sum(row["correct_citations"] for row in report["per_item"][model]) ==
                metrics["citation_precision"]["correct_citations"])
        assert metrics["sweep"]["status"] == "descriptive-only"
    text = comparison.comparison_markdown(report)
    assert "C2-" not in text and "no global winner" in text
    assert "e5-large − e5-base" in text
    assert "e5-large|e5-base" not in text  # unescaped | breaks Markdown tables
    assert "Mixed and evidence-language slices" in text
    assert "N/A" in text


@pytest.mark.parametrize("tamper", ("retrieval", "hit", "model_id", "set_hash", "calibration"))
def test_mismatched_or_unverified_source_cannot_be_published(monkeypatch, tamper):
    original = comparison._read_report

    def altered(root, language, model, mode):
        report, source = original(root, language, model, mode)
        report = copy.deepcopy(report)
        if language == "c" and model == "e5-large":
            if tamper == "retrieval" and mode == "end-to-end":
                report["retrieval"]["rows"][0]["top1_score"] = 0
            elif tamper == "hit" and mode == "retrieval-only":
                report["retrieval"]["rows"][0]["hit"] = False
                # Keep replay equal: invalid per-item hit is still rejected.
            elif tamper == "model_id" and mode == "end-to-end":
                row = next(r for r in report["end_to_end"]["rows"] if r["llm_metadata"])
                row["llm_metadata"]["model"] = "unexpected"
            elif tamper == "set_hash" and mode == "retrieval-only":
                report["v2_sha256"] = "0" * 64
            elif tamper == "calibration" and mode == "retrieval-only":
                report["calibration"]["threshold"] = 0
        return report, source

    monkeypatch.setattr(comparison, "_read_report", altered)
    with pytest.raises(ValueError, match="mismatch|unverified"):
        comparison.build_official_comparison(ROOT, "c", replications=10)


def test_incomplete_e2e_preserves_retrieval_and_cannot_win(monkeypatch):
    original = comparison._read_report

    def incomplete(root, language, model, mode):
        report, source = original(root, language, model, mode)
        report = copy.deepcopy(report)
        if language == "c" and model == "bge-m3" and mode == "end-to-end":
            report["status"] = report["end_to_end"]["status"] = "incomplete"
            report["error_count"] = report["end_to_end"]["error_count"] = 1
            report["end_to_end"].pop("rows")
            report["end_to_end"]["reasons"] = ["provider unavailable"]
        return report, source

    monkeypatch.setattr(comparison, "_read_report", incomplete)
    report = comparison.build_official_comparison(ROOT, "c", replications=100)
    assert report["models"]["bge-m3"]["hit_at_5"]["denominator"] == 38
    assert report["models"]["bge-m3"]["citation_precision"]["value"] is None
    assert report["models"]["bge-m3"]["e2e_abstention"]["value"] is None
    assert report["winner_status"] == "inconclusive"
    assert all(row["cited_ids"] is None for row in report["per_item"]["bge-m3"])
    assert "N/A" in comparison.comparison_markdown(report)
