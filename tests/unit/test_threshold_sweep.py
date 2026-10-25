"""FAIL-first descriptive v2 threshold sweep; v1 gates are never refitted."""

import copy
import hashlib
import math
from pathlib import Path

import pytest

from src.qa.pack_config import PACK_THRESHOLDS


SEED = 20261022
REPLICATIONS = 10_000
CALIBRATIONS = tuple(Path("data/eval/model-comparison/calibration") / f"{model}.json"
                     for model in ("e5-large", "e5-base", "bge-m3"))


def _rows(*scores):
    return [{"item_id": f"fixture-{i}", "qtype": "out-of-corpus" if out else
             "mixed" if i % 2 else "in-corpus", "top1_score": score}
            for i, (out, score) in enumerate(scores)]


def _sweep(rows, threshold=0.85):
    from src.eval.comparison import threshold_sweep

    return threshold_sweep(rows, locked_threshold=threshold,
                           seed=SEED, replications=REPLICATIONS)


def test_ooc_positive_perfect_separation_and_pr_denominators():
    rows = _rows((True, 0.1), (True, 0.2), (False, 0.8), (False, 0.9))
    result = _sweep(rows)
    assert result == _sweep(rows)
    assert result["status"] == "descriptive-only"
    assert result["positive_class"] == "out-of-corpus"
    assert result["seed"] == SEED and result["replications"] == REPLICATIONS
    assert (result["n_out"], result["n_answerable"]) == (2, 2)
    assert result["auroc"] == {"value": 1.0, "ci": [1.0, 1.0]}
    assert result["pr_curve"]
    assert any(point["tp"] == 1 and point["fp"] == 0 and
               point["precision"] == 1 and point["recall"] == 0.5
               for point in result["pr_curve"])
    assert any(point["tp"] == 2 and point["fp"] == 0 and
               point["precision"] == point["recall"] == 1
               for point in result["pr_curve"])
    assert result["pr_curve"][-1]["tp"] == 2
    assert result["pr_curve"][-1]["fp"] == 2
    assert result["pr_curve"][-1]["precision"] == 0.5
    assert result["pr_curve"][-1]["recall"] == 1.0


def test_auroc_direction_ties_and_grouped_pr_points():
    reversed_scores = _sweep(_rows((True, 0.9), (False, 0.1)))
    assert reversed_scores["auroc"] == {"value": 0.0, "ci": [0.0, 0.0]}

    tied = _sweep(_rows((True, 0.2), (False, 0.2)))
    assert tied["auroc"] == {"value": 0.5, "ci": [0.5, 0.5]}
    assert not any(p["tp"] == 1 and p["fp"] == 0 for p in tied["pr_curve"])
    assert tied["pr_curve"][-1]["tp"] == tied["pr_curve"][-1]["fp"] == 1
    assert tied["pr_curve"][-1]["precision"] == 0.5

    overlapped = _sweep(_rows((True, 0.1), (True, 0.6),
                              (False, 0.3), (False, 0.8)))
    assert overlapped["auroc"]["value"] == 0.75
    lower, upper = overlapped["auroc"]["ci"]
    assert 0 <= lower <= 0.75 <= upper <= 1


@pytest.mark.parametrize("scores,counts", [
    (((False, 0.2), (False, 0.8)), (0, 2)),
    (((True, 0.1), (True, 0.7)), (2, 0)),
])
def test_class_absent_is_na_with_counts_not_a_zero_score(scores, counts):
    result = _sweep(_rows(*scores))
    assert (result["n_out"], result["n_answerable"]) == counts
    assert result["auroc"] == {"value": None, "ci": None}
    assert result["pr_curve"] is None


def test_sweep_cannot_retune_pooled_v1_or_operational_gates(monkeypatch):
    import src.eval.calibrate as calibration

    locked_hashes = {str(path): hashlib.sha256(path.read_bytes()).hexdigest()
                     for path in CALIBRATIONS}
    operational = copy.deepcopy(PACK_THRESHOLDS)

    def no_calibration(*args, **kwargs):
        pytest.fail("v2 may not enter pooled-v1 calibration")

    monkeypatch.setattr(calibration, "calibrate_pooled_v1", no_calibration)
    rows = _rows((True, 0.1), (True, 0.2), (False, 0.3), (False, 0.9))
    result = _sweep(rows, threshold=0.85)
    assert result["locked_threshold"] == 0.85
    optimum = result["observed_best_threshold"]
    assert optimum["status"] == "descriptive-only"
    assert 0.2 < optimum["value"] <= 0.3  # better on v2; not deployed
    assert optimum["value"] != result["locked_threshold"]
    assert {str(path): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in CALIBRATIONS} == locked_hashes
    assert PACK_THRESHOLDS == operational


@pytest.mark.parametrize("change", ("duplicate_id", "non_finite", "unknown_qtype"))
def test_malformed_scores_never_become_a_descriptive_sweep(change):
    rows = _rows((True, 0.1), (False, 0.8))
    if change == "duplicate_id":
        rows[1]["item_id"] = rows[0]["item_id"]
    elif change == "non_finite":
        rows[0]["top1_score"] = math.nan
    else:
        rows[0]["qtype"] = "pilot"
    with pytest.raises(ValueError, match="score|item|qtype|finite"):
        _sweep(rows)
