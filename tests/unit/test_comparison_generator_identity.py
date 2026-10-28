"""F09: complete E2E runs must share a response model and provider."""

import copy
from pathlib import Path

import pytest

from src.eval import comparison


@pytest.mark.parametrize("change", ["model", "provider", "one-row-provider"])
def test_official_comparison_rejects_inconsistent_generator(monkeypatch, change):
    original = comparison._read_report

    def altered(root, language, model, mode):
        report, source = original(root, language, model, mode)
        report = copy.deepcopy(report)
        if model == "e5-base" and mode == "end-to-end":
            rows = [row for row in report["end_to_end"]["rows"] if row.get("llm_metadata")]
            assert len(rows) > 1
            if change == "model":
                report["end_to_end"]["expected_response_model"] = "other-verified-model"
                for row in rows:
                    row["llm_metadata"]["model"] = "other-verified-model"
            elif change == "provider":
                for row in rows:
                    row["llm_metadata"]["provider"] = "other-provider"
            else:
                rows[0]["llm_metadata"]["provider"] = "other-provider"
        return report, source

    monkeypatch.setattr(comparison, "_read_report", altered)
    with pytest.raises(ValueError, match="(?i)(generator|provider|response.model|identity)"):
        comparison.build_official_comparison(Path("data/eval"), "c", replications=10)
