"""F11: normalized duplicate questions cannot enter a v2 set or comparison."""

import json
from pathlib import Path

import pytest

from src.eval import comparison
from src.eval.validate_set import validate_set
from tests.unit.test_v2_provenance import _fixture


@pytest.mark.parametrize("variant", ["exact", "whitespace", "arabic-letters", "casefold"])
def test_v2_validator_rejects_normalized_duplicates(tmp_path, variant):
    data = _fixture()
    first = "پرسش كد و يک نمونه Test درباره چیست؟"
    variants = {"exact": first,
                "whitespace": "  پرسش   كد و يک نمونه Test  درباره چیست؟ \n",
                "arabic-letters": "پرسش کد و یک نمونه Test درباره چیست؟",
                "casefold": "پرسش كد و يک نمونه tEST درباره چیست؟"}
    data["items"][0]["question"] = first
    data["items"][1]["question"] = variants[variant]
    path = tmp_path / "synthetic.json"
    content = json.dumps(data, ensure_ascii=False) + "\n"
    path.write_text(content, encoding="utf-8", newline="\n")
    assert path.read_text(encoding="utf-8") == content
    with pytest.raises(ValueError, match="(?i)duplicate.*question"):
        validate_set(path, pack_id="c")


def test_official_comparison_rejects_duplicates_before_reading_reports(monkeypatch):
    target = Path("data/eval/c/eval-set.c.v2.json")
    original = Path.read_bytes
    data = json.loads(target.read_text(encoding="utf-8"))
    data["items"][1]["question"] = "  " + data["items"][0]["question"] + "  "
    synthetic = json.dumps(data, ensure_ascii=False).encode("utf-8")

    def read_bytes(path):
        return synthetic if path == target else original(path)

    monkeypatch.setattr(Path, "read_bytes", read_bytes)
    with pytest.raises(ValueError, match="(?i)duplicate.*question"):
        comparison.build_official_comparison(Path("data/eval"), "c", replications=10)


@pytest.mark.parametrize("language", comparison.LANGUAGES)
def test_real_v2_sets_have_unique_normalized_questions(language):
    from src.eval.validate_set import _plain
    path = Path(f"data/eval/{language}/eval-set.{language}.v2.json")
    items = json.loads(path.read_text(encoding="utf-8"))["items"]
    assert len(items) == len({_plain(item["question"]) for item in items}) == 45
