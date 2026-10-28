"""F10: frozen-run comparison rejects citations outside row Top-5 or pack."""

import copy
import json
from pathlib import Path

import pytest

from src.eval import comparison


ROOT = Path("data/eval")


@pytest.mark.parametrize("fault", ["same-pack-other-row", "foreign-inside-top5", "sixth-id"])
def test_official_report_rejects_citations_outside_row_or_pack(monkeypatch, fault):
    original = comparison._read_report
    pack_ids = json.loads(Path("data/index/c/ids.json").read_text(encoding="utf-8"))
    foreign_ids = json.loads(Path("data/index/python/ids.json").read_text(encoding="utf-8"))
    items = {item["item_id"]: item for item in json.loads(
        (ROOT / "c/eval-set.c.v2.json").read_text(encoding="utf-8"))["items"]}
    source, _ = original(ROOT, "c", "e5-large", "end-to-end")
    retrieval = {r["item_id"]: r for r in source["retrieval"]["rows"]}
    answers = [a for a in source["end_to_end"]["rows"] if a["response_type"] == "answer"]
    answer = next(a for a in answers if any(
        cid not in items[a["item_id"]]["expected_source_ids"]
        for cid in retrieval[a["item_id"]]["top5_ids"][:5]))
    item_id = answer["item_id"]
    top5 = retrieval[item_id]["top5_ids"][:5]
    outside = next(cid for cid in pack_ids if cid not in top5)
    foreign = next(cid for cid in foreign_ids if cid not in set(pack_ids))
    expected = set(items[item_id]["expected_source_ids"])
    replace_at = next(i for i, cid in enumerate(top5) if cid not in expected)

    def altered(root, language, model, mode):
        report, source_info = original(root, language, model, mode)
        report = copy.deepcopy(report)
        if model == "e5-large":
            row = next(r for r in report["retrieval"]["rows"] if r["item_id"] == item_id)
            if fault == "foreign-inside-top5":
                row["top5_ids"][replace_at] = foreign
            elif fault == "sixth-id":
                row["top5_ids"].append(outside)
            if mode == "end-to-end":
                target = next(a for a in report["end_to_end"]["rows"] if a["item_id"] == item_id)
                target["cited_ids"] = [foreign if fault == "foreign-inside-top5" else outside]
        return report, source_info

    monkeypatch.setattr(comparison, "_read_report", altered)
    with pytest.raises(ValueError, match="(?i)(citation|cited).*(top.5|pack|scope)"):
        comparison.build_official_comparison(ROOT, "c", replications=10)


@pytest.mark.parametrize("language", comparison.LANGUAGES)
def test_existing_complete_official_reports_remain_valid(language):
    report = comparison.build_official_comparison(ROOT, language, replications=10)
    assert report["language_id"] == language
