"""FAIL-first v2 set/provenance contract (003-T019); synthetic, never published."""

import json
from collections import Counter
from pathlib import Path

import pytest


def _fixture():
    chunks = [json.loads(line) for line in
              Path("data/index/c/chunks.jsonl").read_text(encoding="utf-8").splitlines()]
    sources = {source["source_id"]: source for source in
               json.loads(Path("data/corpus/manifest.c.json").read_text(encoding="utf-8"))["sources"]}
    items = []
    for i in range(45):
        qtype = "in-corpus" if i < 28 else "mixed" if i < 38 else "out-of-corpus"
        item = {
            "item_id": f"C2-{i + 1:03d}", "pack_id": "c", "version": "c-v2",
            "qtype": qtype,
            "question": (f"در آزمون ساختاری شمارهٔ {i + 1}، موضوع این بخش از زبان سی چیست؟"
                         + (f" `C_probe_{i}`" if qtype == "mixed" else "")),
            "authorship": {"author": "test-fixture", "authored_at": "2026-10-23",
                           "review_status": "reviewed", "reviewer": "test-reviewer",
                           "reviewed_at": "2026-10-23"},
        }
        if qtype == "out-of-corpus":
            item.update(expected_source_ids=[], evidence_language="none", provenance=[],
                        abstain_reason="پیکرهٔ فریز برای این پرسش آزمایشی شاهدی ندارد.")
        else:
            chunk = (next(c for c in chunks if c["chunk_id"] == "cppref-fread#s04-c01")
                     if i == 37 else chunks[i + 2])
            source = sources[chunk["source_id"]]
            item.update(
                expected_source_ids=[chunk["chunk_id"]],
                expected_answer_summary=f"این بخش دربارهٔ {chunk['section_heading']} است.",
                evidence_language=chunk["lang"],
                provenance=[{
                    "chunk_id": chunk["chunk_id"], "source_id": chunk["source_id"],
                    "section_heading": chunk["section_heading"],
                    **{key: source[key] for key in ("title", "origin", "snapshot", "license")},
                }],
            )
        items.append(item)
    assert Counter(x["qtype"] for x in items) == {
        "in-corpus": 28, "mixed": 10, "out-of-corpus": 7,
    }
    assert items[37]["evidence_language"] == "en"  # real English C-pack evidence
    return {"version": "c-v2", "pack_id": "c", "items": items}


def _validate(tmp_path, data, *, complete=True):
    from src.eval.validate_set import validate_set  # absent until T020

    path = tmp_path / "eval-set.c.v2.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    assert json.loads(path.read_text(encoding="utf-8")) == data
    return validate_set(path, pack_id="c", complete=complete)


def test_frozen_c_fixture_sources_and_old_question_are_real():
    data = _fixture()
    assert all(x["item_id"] not in {v["item_id"] for v in json.loads(
        Path("data/eval/c/eval-set.c.v1.json").read_text(encoding="utf-8"))["items"]}
               for x in data["items"])
    assert data["items"][0]["provenance"][0]["chunk_id"] == data["items"][0]["expected_source_ids"][0]


def test_complete_45_item_set_has_exact_split_and_reviewed_provenance(tmp_path):
    result = _validate(tmp_path, _fixture())
    assert result["status"] == "complete"
    assert result["counts"] == {"in-corpus": 28, "mixed": 10, "out-of-corpus": 7}
    assert not result["review_flags"]


def test_28_item_draft_is_incomplete_not_published(tmp_path):
    data = _fixture()
    data["items"] = data["items"][:28]
    for item in data["items"]:
        item["authorship"].update(review_status="pending-user-review", reviewer=None,
                                  reviewed_at=None)
    result = _validate(tmp_path, data, complete=False)
    assert result["status"] == "incomplete"
    with pytest.raises(ValueError, match="45|28|complete|unreviewed"):
        _validate(tmp_path, data)


def test_27_item_draft_is_not_mistaken_for_a_publishable_set(tmp_path):
    data = _fixture()
    data["items"] = data["items"][:27]
    with pytest.raises(ValueError, match="28|draft"):
        _validate(tmp_path, data, complete=False)


def test_duplicate_item_id_is_rejected_not_silently_deduplicated(tmp_path):
    data = _fixture()
    data["items"][1]["item_id"] = data["items"][0]["item_id"]  # C2-001 twice
    with pytest.raises(ValueError, match="duplicate|item_id"):
        _validate(tmp_path, data)


def test_review_date_must_be_valid(tmp_path):
    data = _fixture()
    data["items"][0]["authorship"]["reviewed_at"] = "yesterday"
    with pytest.raises(ValueError, match="reviewed_at"):
        _validate(tmp_path, data)


def test_mixed_question_has_a_latin_technical_term(tmp_path):
    data = _fixture()
    data["items"][28]["question"] = "در این پرسش فارسی، مفهوم مربوط به بخش چیست؟"
    with pytest.raises(ValueError, match="mixed|English"):
        _validate(tmp_path, data)


def test_pilot_cannot_be_published_as_v2():
    from src.eval.validate_set import validate_set

    with pytest.raises(ValueError, match="version"):
        validate_set("data/eval/pilot/eval-set.c.pilot.json", pack_id="c")


@pytest.mark.parametrize("field,value", [
    ("pack_id", "python"), ("version", "c-v1"), ("qtype", "unrecognized"),
    ("question", "ASCII only"), ("evidence_language", "none"),
])
def test_invalid_identity_question_type_or_evidence_language(tmp_path, field, value):
    data = _fixture()
    data["items"][0][field] = value
    with pytest.raises(ValueError, match="pack|version|qtype|Persian|evidence|question"):
        _validate(tmp_path, data)


@pytest.mark.parametrize("change", [
    lambda item: item["authorship"].update(reviewer=None),
    lambda item: item.update(expected_answer_summary=""),
    lambda item: item["provenance"][0].update(license=""),
    lambda item: item["provenance"][0].update(origin="not-the-frozen-origin"),
    lambda item: item.update(expected_source_ids=["pyref-tutorial-introduction#s02-c01"]),
])
def test_unreviewed_ungrounded_or_foreign_provenance_is_rejected(tmp_path, change):
    data = _fixture()
    change(data["items"][0])
    with pytest.raises(ValueError, match="review|summary|license|origin|source|chunk|pack"):
        _validate(tmp_path, data)


@pytest.mark.parametrize("change", [
    lambda item: item.update(expected_source_ids=["fa-functions#s18-c01"]),
    lambda item: item.update(abstain_reason=""),
    lambda item: item.update(evidence_language="fa"),
])
def test_ooc_requires_empty_sources_reason_and_none_evidence(tmp_path, change):
    data = _fixture()
    change(data["items"][-1])
    with pytest.raises(ValueError, match="out|source|abstain|reason|evidence"):
        _validate(tmp_path, data)


@pytest.mark.parametrize("copied_question", [
    lambda: json.loads(Path("data/eval/c/eval-set.c.v1.json").read_text(encoding="utf-8"))["items"][0]["question"],
    lambda: next(json.loads(line)["text"] for line in
                 Path("data/index/c/chunks.jsonl").read_text(encoding="utf-8").splitlines()
                 if json.loads(line)["chunk_id"] == "fa-functions#s05-c01"),
])
def test_literal_v1_or_chunk_question_copy_is_rejected(tmp_path, copied_question):
    data = _fixture()
    data["items"][0]["question"] = copied_question()
    with pytest.raises(ValueError, match="copy|copied|v1|chunk|duplicate"):
        _validate(tmp_path, data)


def test_near_v1_paraphrase_is_flagged_for_human_review_not_published(tmp_path):
    data = _fixture()
    data["items"][0]["question"] = "تفاوت calloc با malloc چیست؟"  # C-001, same answer
    result = _validate(tmp_path, data)
    assert result["status"] != "complete"
    assert any(flag["item_id"] == "C2-001" and "v1" in flag["reason"].lower()
               for flag in result["review_flags"])
