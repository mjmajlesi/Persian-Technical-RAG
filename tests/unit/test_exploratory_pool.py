"""Pooled v2 evidence is secondary; it cannot retune gates or name a winner."""

import copy
import hashlib
import json
from pathlib import Path

import pytest

from src.eval.comparison import LANGUAGES, MODELS, exploratory_pool
from src.qa.pack_config import PACK_THRESHOLDS


ROOT = Path("data/eval")


def _primary():
    return {lang: json.loads((ROOT / lang / "reports/v2/comparison.v2.json")
                             .read_text(encoding="utf-8")) for lang in LANGUAGES}


def test_pool_counts_ci_and_four_primary_decisions_are_unchanged(monkeypatch):
    import src.eval.calibrate as calibration

    monkeypatch.setattr(calibration, "calibrate_pooled_v1", lambda *a, **kw:
                        pytest.fail("v2 must never enter pooled-v1 calibration"))
    hashes = {model: hashlib.sha256((ROOT / "model-comparison/calibration" /
                                      f"{model}.json").read_bytes()).hexdigest()
              for model in MODELS}
    operational = copy.deepcopy(PACK_THRESHOLDS)
    reports = _primary()
    original = copy.deepcopy(reports)
    result = exploratory_pool(reports, replications=100)
    assert result == exploratory_pool(reports, replications=100)
    assert result["status"] == "exploratory-secondary"
    assert (result["n_items"], result["n_answerable"], result["n_out"]) == (180, 152, 28)
    assert result["resampling"] == "within-language paired questions"
    assert not any("winner" in key or "gate" in key or "threshold" in key for key in result)
    assert {lang: reports[lang]["winner_status"] for lang in LANGUAGES} == {
        "c": "inconclusive", "cpp": "bge-m3", "python": "inconclusive", "java": "bge-m3"}
    for model in MODELS:
        for metric, n in (("hit_at_5", 152), ("fixed_gate_abstention", 28),
                          ("e2e_abstention", 28)):
            entry = result["models"][model][metric]
            assert entry["denominator"] == n
            assert entry["numerator"] == sum(reports[lang]["models"][model][metric]["numerator"]
                                             for lang in LANGUAGES)
            assert entry["ci"][0] <= entry["value"] <= entry["ci"][1]
        precision = result["models"][model]["citation_precision"]
        assert precision["answer_count"] == precision["denominator"]
        assert precision["citation_count"] == sum(
            reports[lang]["models"][model]["citation_precision"]["citation_count"]
            for lang in LANGUAGES)
        assert precision["ci"][0] <= precision["value"] <= precision["ci"][1]
    assert reports == original
    assert PACK_THRESHOLDS == operational
    assert hashes == {model: hashlib.sha256((ROOT / "model-comparison/calibration" /
                                             f"{model}.json").read_bytes()).hexdigest()
                      for model in MODELS}


def test_incomplete_e2e_is_na_for_whole_pool_but_retrieval_survives():
    reports = _primary()
    report = reports["java"]
    report["source_reports"]["bge-m3"]["end_to_end"]["status"] = "incomplete"
    report["source_reports"]["bge-m3"]["end_to_end"]["error_count"] = 1
    report["models"]["bge-m3"]["e2e_abstention"]["value"] = None
    for row in report["per_item"]["bge-m3"]:
        row.update(response_type=None, cited_ids=None, correct_citations=None)
    result = exploratory_pool(reports, replications=100)["models"]["bge-m3"]
    assert result["hit_at_5"]["denominator"] == 152
    assert result["fixed_gate_abstention"]["denominator"] == 28
    assert result["e2e_abstention"]["value"] is None
    assert result["e2e_abstention"]["ci"] is None
    assert result["citation_precision"]["value"] is None
    assert result["citation_precision"]["answer_count"] == 0
    assert result["errors"]["e2e_errors"] == 1


def test_document_keeps_four_primary_links_before_exploratory_table():
    document = Path("docs/EMBEDDING-COMPARISON.md")
    text = document.read_text(encoding="utf-8")
    assert text.index("## Primary analysis") < text.index("## Secondary pooled analysis")
    for lang in LANGUAGES:
        for extension in ("json", "md"):
            target = Path(f"../data/eval/{lang}/reports/v2/comparison.v2.{extension}")
            assert target.as_posix() in text
            assert (document.parent / target).is_file()
    for heading in ("### C — inconclusive", "### C++ — bge-m3",
                    "### Python — inconclusive", "### Java — bge-m3"):
        assert heading in text
    assert text.count("| Model | Hit@5 /38 |") == 4
    assert "No global winner is inferred" in text


@pytest.mark.parametrize("change", ("missing_pack", "duplicate_item", "changed_gate", "wrong_hit"))
def test_invalid_pool_inputs_cannot_relabel_primary_evidence(change):
    reports = _primary()
    if change == "missing_pack":
        reports.pop("cpp")
    elif change == "duplicate_item":
        reports["c"]["per_item"]["e5-base"][0]["item_id"] = "C2-002"
    elif change == "changed_gate":
        reports["c"]["source_reports"]["e5-large"]["locked_threshold"] = 0
    else:
        reports["c"]["per_item"]["e5-large"][0]["hit"] = False
    with pytest.raises(ValueError, match="pool|mismatch|pairing|fixed-gate|hit"):
        exploratory_pool(reports, replications=10)
