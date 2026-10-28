# -*- coding: utf-8 -*-
"""Unit tests (002-US3, T019): per-language scoring pieces.

FAIL-first on purpose: the contamination slice (a scoring function and a
report key) and the empty-item-set guard in run_eval DO NOT EXIST yet —
these tests are authored before that implementation lands (same gate the
001 test tasks used). The per-pack metric plumbing that already works
(language_id in the report) is locked here as regression insurance.
Run: pytest tests/unit/test_lang_scoring.py

Contract (002 spec.md US3):
  - contamination slice: contamination-qtype rows (foreign-domain question
    under this pack) aggregate abstain-with-zero-citations correctness;
  - every per-language report carries per-pack metrics + its language_id;
  - an empty item set scores as an explicit zeroed report, never a crash.
"""

import json

import pytest

from src.eval.run import default_set_path, run_eval
from src.eval.scoring import mixed_slice_scores

# ---------------------------------------------------------------------------
# Pure slice aggregation (new in the US3 implementation)
# ---------------------------------------------------------------------------


def test_contamination_slice_scores_abstain_rows_only():
    from src.eval.scoring import contamination_slice_scores  # FAILS: missing

    rows = [
        {"qtype": "contamination", "response_type": "abstain",
         "abstention_ok": True},
        {"qtype": "contamination", "response_type": "answer",
         "abstention_ok": False},
    ]
    scores = contamination_slice_scores(rows)
    assert scores == {"correct": 1, "n": 2}


def test_contamination_slice_empty_rows_zeroed():
    from src.eval.scoring import contamination_slice_scores  # FAILS: missing

    assert contamination_slice_scores([]) == {"correct": 0, "n": 0}
    non_items = [{"qtype": "in-corpus", "response_type": "answer",
                  "abstention_ok": None}]
    assert contamination_slice_scores(non_items) == {"correct": 0, "n": 0}


# ---------------------------------------------------------------------------
# run_eval report aggregation (contamination slice + empty-set handling)
# ---------------------------------------------------------------------------


def _write_set(tmp_path, items):
    spec = {"version": "eval-set.v1", "items": items}
    path = tmp_path / "set.json"
    path.write_text(json.dumps(spec, ensure_ascii=False), "utf-8")
    return str(path)


def test_empty_item_set_scores_as_zeroed_report(tmp_path):
    """0 items must give an explicit zeroed report, not ZeroDivisionError."""
    set_path = _write_set(tmp_path, [])
    report = run_eval(set_path, "data/index/c", str(tmp_path / "reports"))
    assert report["n_items"] == 0
    assert report["language_id"] == "c"
    assert report["hit_rate_at_5"] == 0.0
    assert report["citation_precision"] == 0.0
    assert report["abstention_correct"] == "0/0"
    assert report["mixed_slice"] == mixed_slice_scores([])
    assert report["contamination_slice"] == {"correct": 0, "n": 0}


def test_contamination_item_scored_in_report(tmp_path):
    """An out-of-domain contamination item must gate-abstain and be counted.

    T024 note: the probe is a known-below-gate out-of-domain question
    (C-O02, measured top-1 0.774 < c gate 0.803) so the gate abstains
    deterministically with zero LLM credit. Cross-language questions can
    score above the gate (python-range under c = 0.832) and fall to the
    LLM backstop - that behavior belongs to the T018 integration test and
    the T025 contamination slice, not to this unit test.
    """
    set_path = _write_set(tmp_path, [
        {"item_id": "CON-01", "qtype": "contamination",
         "question": "طرز تهیه قرمه‌سبزی چیست؟",
         "expected_source_ids": []},
    ])
    report = run_eval(set_path, "data/index/c", str(tmp_path / "reports"))
    row = report["per_item_rows"][0]
    assert report["language_id"] == "c"
    assert row["response_type"] == "abstain"      # zero LLM credit
    assert row["abstention_ok"] is True
    assert report["contamination_slice"] == {"correct": 1, "n": 1}


def test_dedicated_contamination_set_keeps_main_metrics_separate(tmp_path, monkeypatch):
    """The 20/5/5 pack set stays intact; cross-pack probes get their own slice."""
    import src.eval.run as runner

    monkeypatch.setattr(runner, "ask", lambda request: {
        "type": "abstain", "citations": [],
    })
    set_path = _write_set(tmp_path, [])
    report = run_eval(set_path, "data/index/c", str(tmp_path / "reports"),
                      contamination_set_path="data/eval/contamination.v1.json")
    assert report["n_items"] == 3
    assert report["contamination_set_version"] == "contamination-v1"
    assert report["error_count"] == 0
    assert report["contamination_slice"] == {"correct": 3, "n": 3}
    assert report["hit_rate_at_5"] == 0.0
    assert report["citation_precision"] == 0.0
    assert {r["item_id"] for r in report["per_item_rows"]} == {
        "C-X-CPP", "C-X-PY", "C-X-JV",
    }


def test_model_errors_mark_report_incomplete(tmp_path, monkeypatch):
    import src.eval.run as runner

    def broken_ask(request):
        raise RuntimeError("model unavailable")

    monkeypatch.setattr(runner, "ask", broken_ask)
    set_path = _write_set(tmp_path, [
        {"item_id": "C-ERR", "qtype": "in-corpus",
         "question": "تفاوت malloc و calloc چیست؟", "expected_source_ids": []},
    ])
    report = run_eval(set_path, "data/index/c", str(tmp_path / "reports"))
    assert report["error_count"] == 1
    _, md_path = runner.write_reports(report, str(tmp_path / "reports"))
    assert "Status: INCOMPLETE (1 model errors)" in open(
        md_path, encoding="utf-8"
    ).read()


# ---------------------------------------------------------------------------
# Regression insurance: existing per-pack plumbing keeps its shape
# ---------------------------------------------------------------------------


def test_per_pack_report_reports_language_id(tmp_path):
    set_path = _write_set(tmp_path, [])
    report = run_eval(set_path, "data/index/python", str(tmp_path / "reports"),
                      language="python")
    assert report["language_id"] == "python"


def test_default_set_path_prefers_per_pack_c_set():
    """002-T020 onward: the per-pack C set exists and takes precedence —
    the flat-set fallback only mattered pre-T020 (kept in default_set_path
    for history)."""
    assert default_set_path("c") == "data/eval/c/eval-set.c.v1.json"


def test_default_set_path_rejects_pack_without_set():
    """A language id without an authored eval set must refuse loudly."""
    with pytest.raises(SystemExit):
        default_set_path("rust")
