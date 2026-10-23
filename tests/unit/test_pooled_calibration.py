"""FAIL-first pooled-v1 research gate contract (003-T011; no model/LLM calls)."""

import hashlib
import json
from pathlib import Path

import pytest

from src.eval.calibrate import calibrate_pooled_v1
from src.qa.pack_config import PACK_THRESHOLDS


PACKS = ("c", "cpp", "python", "java")


def _sets(tmp_path, *, tie=False):
    paths, scores = {}, {}
    for pack in PACKS:
        items = []
        for i in range(30):
            qtype = "in-corpus" if i < 20 else "mixed" if i < 25 else "out-of-corpus"
            item_id = f"{pack}-{i:02d}"
            question = f"سؤال {item_id} چیست؟"
            items.append({"item_id": item_id, "question": question, "qtype": qtype})
            if tie:
                score = (0.2 if i < 15 else 0.8) if i < 25 else (0.1 if i < 27 else 0.7)
            elif qtype == "out-of-corpus":
                score = 0.65 if pack == "cpp" else 0.35
            elif pack == "python" and i == 0:
                score = 0.6
            else:
                score = 0.8 if qtype == "mixed" else 0.9
            scores[pack, question] = score
        path = tmp_path / pack / f"eval-set.{pack}.v1.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({"version": f"{pack}-v1", "items": items},
                                   ensure_ascii=False), encoding="utf-8")
        assert "سؤال" in path.read_text(encoding="utf-8")
        paths[pack] = path
    return paths, scores


def test_four_v1_sets_produce_one_gate_and_per_pack_confusion(tmp_path):
    paths, scores = _sets(tmp_path)
    calls = []
    original_gates = PACK_THRESHOLDS.copy()

    def score_question(pack, question):
        calls.append((pack, question))
        return scores[pack, question]

    result = calibrate_pooled_v1("e5-large", paths, score_question)
    assert result["model_key"] == "e5-large"
    assert result["n_answerable"] == 100 and result["n_out"] == 20
    assert len(calls) == len(set(calls)) == 120
    assert result["threshold"] == pytest.approx(0.8)
    assert result["balanced_accuracy"] == pytest.approx(0.995)
    # OOC is positive; score < threshold means predicted OOC.
    assert result["pooled_confusion"] == {"tp": 20, "fn": 0, "tn": 99, "fp": 1}
    assert set(result["per_language_confusion"]) == set(PACKS)
    for pack in PACKS:
        expected = {"tp": 5, "fn": 0, "tn": 24 if pack == "python" else 25,
                    "fp": 1 if pack == "python" else 0}
        assert result["per_language_confusion"][pack] == expected
        assert result["v1_hashes"][pack] == hashlib.sha256(paths[pack].read_bytes()).hexdigest()
    assert PACK_THRESHOLDS == original_gates  # operational gates stay untouched


def test_balanced_accuracy_tie_chooses_higher_conservative_gate(tmp_path):
    paths, scores = _sets(tmp_path, tie=True)
    result = calibrate_pooled_v1("e5-base", paths,
                                 lambda pack, question: scores[pack, question])
    # Both 0.2 and 0.8 score 0.7 on 100/20; 0.8 abstains more readily.
    assert result["threshold"] == pytest.approx(0.8)
    assert result["balanced_accuracy"] == pytest.approx(0.7)
    assert result["pooled_confusion"] == {"tp": 20, "fn": 0, "tn": 40, "fp": 60}


def test_v2_file_is_never_read_for_calibration(tmp_path, monkeypatch):
    paths, scores = _sets(tmp_path)
    v2 = tmp_path / "c" / "eval-set.c.v2.json"
    v2.write_text('{"should_not_be_read": true}', encoding="utf-8")
    read_text = Path.read_text

    def guard(self, *args, **kwargs):
        if ".v2." in self.name:
            pytest.fail("v2 must not enter calibration")
        return read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", guard)
    result = calibrate_pooled_v1("bge-m3", paths,
                                 lambda pack, question: scores[pack, question])
    assert result["n_answerable"] == 100 and result["n_out"] == 20
    with pytest.raises(ValueError, match="v1|version"):
        calibrate_pooled_v1("bge-m3", {**paths, "c": v2},
                            lambda pack, question: pytest.fail("no v2 scoring"))


def test_incomplete_v1_pool_is_rejected(tmp_path):
    paths, scores = _sets(tmp_path)
    with pytest.raises(ValueError, match="four|pack|120"):
        calibrate_pooled_v1("e5-large", {key: path for key, path in paths.items()
                                           if key != "java"},
                            lambda pack, question: scores[pack, question])
    data = json.loads(paths["java"].read_text(encoding="utf-8"))
    data["items"].pop()
    paths["java"].write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    assert len(json.loads(paths["java"].read_text(encoding="utf-8"))["items"]) == 29
    with pytest.raises(ValueError, match="30|120|incomplete"):
        calibrate_pooled_v1("e5-large", paths,
                            lambda pack, question: scores[pack, question])
