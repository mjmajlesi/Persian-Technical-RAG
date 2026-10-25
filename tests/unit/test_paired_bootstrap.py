"""FAIL-first, question-paired uncertainty and winner contract (003-T045)."""

import copy

import pytest


MODELS = ("e5-large", "e5-base", "bge-m3")
SEED = 20261022
REPLICATIONS = 10_000


def _fixture():
    items = [
        {"item_id": f"C2-{i:03}",
         "qtype": "in-corpus" if i < 28 else "mixed" if i < 38 else "out-of-corpus",
         "expected_source_ids": [] if i >= 38 else [f"c-source-{i}"]}
        for i in range(45)
    ]
    runs = {}
    for model in MODELS:
        retrieval = [{"item_id": item["item_id"], "qtype": item["qtype"],
                      "hit": i % 2 == 0 if i < 38 else False,
                      "top1_score": 0.9, "top5_ids": [f"c-source-{i}"],
                      "fixed_gate_abstain": i >= 38}
                     for i, item in enumerate(items)]
        answers = [{"item_id": item["item_id"],
                    "response_type": "answer" if i < 38 else "abstain",
                    "cited_ids": [f"c-source-{i}"] if i < 38 else []}
                   for i, item in enumerate(items)]
        runs[model] = {"model_key": model, "language_id": "c", "status": "complete",
                       "retrieval": {"status": "complete", "error_count": 0,
                                     "rows": retrieval},
                       "end_to_end": {"status": "complete", "error_count": 0,
                                      "rows": answers}}
    return items, runs


def _compare(items, runs):
    from src.eval.comparison import compare_language

    return compare_language(runs, items, seed=SEED, replications=REPLICATIONS)


def test_seeded_bootstrap_uses_identical_question_ids_and_bonferroni_pairs():
    items, runs = _fixture()
    result = _compare(items, runs)
    assert result == _compare(items, runs)  # deterministic 10,000 draws
    assert result["bootstrap_seed"] == SEED and result["replications"] == REPLICATIONS
    assert result["confidence"] == 0.95
    assert result["pair_confidence"] == pytest.approx(1 - 0.05 / 3)
    assert len(result["paired_differences"]) == 3
    for model in MODELS:
        metric = result["models"][model]["hit_at_5"]
        assert metric["numerator"] == 19 and metric["denominator"] == 38
        assert metric["value"] == 0.5
        assert metric["ci"][0] < 0.5 < metric["ci"][1]
        for name in ("fixed_gate_abstention", "e2e_abstention"):
            abstention = result["models"][model][name]
            assert abstention["numerator"] == abstention["denominator"] == 7
            assert abstention["value"] == 1 and abstention["ci"] == [1, 1]
    for difference in result["paired_differences"].values():
        for name in ("hit_at_5", "citation_precision",
                     "fixed_gate_abstention", "e2e_abstention"):
            assert difference[name]["value"] == 0
            assert difference[name]["ci"] == [0, 0]
    assert result["winner_status"] == "inconclusive"

    # Row position cannot replace the common item ID as the pairing key.
    reordered = copy.deepcopy(runs)
    reordered["e5-base"]["retrieval"]["rows"].reverse()
    reordered["e5-base"]["end_to_end"]["rows"].reverse()
    assert _compare(items, reordered) == result


def test_clear_paired_hit_advantage_wins_but_tie_or_secondary_harm_does_not():
    items, runs = _fixture()
    for i in range(38):
        for model in MODELS:
            runs[model]["retrieval"]["rows"][i]["hit"] = model == "e5-large"
    winning = _compare(items, runs)
    assert winning["winner_status"] == "e5-large"
    for other in ("e5-base", "bge-m3"):
        diff = winning["paired_differences"][f"e5-large|{other}"]["hit_at_5"]
        assert diff["value"] == 1 and diff["ci"] == [1, 1]

    tied = copy.deepcopy(runs)
    for row in tied["e5-base"]["retrieval"]["rows"][:38]:
        row["hit"] = True
    assert _compare(items, tied)["winner_status"] == "inconclusive"

    harmed = copy.deepcopy(runs)
    for row in harmed["e5-large"]["end_to_end"]["rows"][:38]:
        row["cited_ids"] = ["c-other"]  # answered, but no correct citation
    harmed_result = _compare(items, harmed)
    assert harmed_result["winner_status"] == "inconclusive"
    assert harmed_result["paired_differences"]["e5-large|e5-base"]["citation_precision"]["ci"][1] < 0

    harmed_gate = copy.deepcopy(runs)
    for row in harmed_gate["e5-large"]["retrieval"]["rows"][38:]:
        row["fixed_gate_abstain"] = False
    assert _compare(items, harmed_gate)["winner_status"] == "inconclusive"

    harmed_e2e = copy.deepcopy(runs)
    for row in harmed_e2e["e5-large"]["end_to_end"]["rows"][38:]:
        row.update(response_type="answer", cited_ids=["c-other"])
    e2e_result = _compare(items, harmed_e2e)
    assert e2e_result["winner_status"] == "inconclusive"
    assert e2e_result["paired_differences"]["e5-large|e5-base"]["e2e_abstention"]["ci"][1] < 0


def test_precision_is_macro_over_answered_rows_in_each_resample_not_all_items():
    items, runs = _fixture()
    for model in MODELS:
        for row in runs[model]["end_to_end"]["rows"][:38]:
            row.update(response_type="abstain", cited_ids=[])
        runs[model]["end_to_end"]["rows"][0].update(
            response_type="answer", cited_ids=["c-source-0"])
        runs[model]["end_to_end"]["rows"][1].update(
            response_type="answer", cited_ids=["c-source-1", "c-other"])
    result = _compare(items, runs)
    for model in MODELS:
        precision = result["models"][model]["citation_precision"]
        assert precision["answer_count"] == 2 and precision["citation_count"] == 3
        assert precision["value"] == 0.75  # mean(1, 0.5), not micro 2/3
        assert precision["ci"][0] <= 0.5 and precision["ci"][1] >= 1.0


def test_zero_answer_denominator_and_incomplete_e2e_are_na_not_zero():
    items, runs = _fixture()
    for row in runs["e5-large"]["end_to_end"]["rows"][:38]:
        row.update(response_type="abstain", cited_ids=[])
    runs["e5-base"]["status"] = "incomplete"
    runs["e5-base"]["end_to_end"] = {"status": "incomplete", "error_count": 1}
    result = _compare(items, runs)
    assert result["models"]["e5-large"]["citation_precision"] == {
        "value": None, "ci": None, "answer_count": 0,
        "citation_count": 0, "correct_citations": 0}
    assert result["models"]["e5-base"]["hit_at_5"]["denominator"] == 38
    assert result["models"]["e5-base"]["citation_precision"]["value"] is None
    assert result["models"]["e5-base"]["e2e_abstention"]["value"] is None
    assert result["winner_status"] == "inconclusive"


@pytest.mark.parametrize("change", ("language", "missing_id", "duplicate_id",
                                    "incomplete_retrieval", "item_count", "answer_count",
                                    "different_set_hash"))
def test_unpaired_or_incomplete_retrieval_cannot_be_compared(change):
    items, runs = _fixture()
    candidate = runs["e5-base"]
    if change == "language":
        candidate["language_id"] = "cpp"
    elif change == "missing_id":
        candidate["retrieval"]["rows"].pop()
    elif change == "duplicate_id":
        candidate["retrieval"]["rows"][0]["item_id"] = candidate["retrieval"]["rows"][1]["item_id"]
    else:
        if change == "incomplete_retrieval":
            candidate["retrieval"]["status"] = "incomplete"
            candidate["retrieval"]["error_count"] = 1
        elif change == "item_count":
            candidate["n_items"] = 44
        elif change == "answer_count":
            candidate["end_to_end"]["answer_count"] = 37
        else:
            for report in runs.values():
                report["v2_sha256"] = "a" * 64
            candidate["v2_sha256"] = "b" * 64
    with pytest.raises(ValueError, match="language|item|retrieval|complete|answer|hash"):
        _compare(items, runs)
