"""Hermetic lexical, fusion and research-boundary checks."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.index.bm25 import BM25Index, tokenize
from src.qa.hybrid import HybridRetriever, rrf_fuse
from src.eval import run


@pytest.mark.parametrize(("text", "expected"), [
    ("می\u200cشود", ["می", "شود"]),
    ("ي ك", ["ی", "ک"]),
    ("MY_FUNCTION_42", ["my_function_42"]),
    ("std::vector", ["std", "vector"]),
    ("۱۲۳ 42", ["۱۲۳", "42"]),
    ("ＦＯＯ", ["foo"]),
])
def test_tokenize_normalization(text, expected):
    assert tokenize(text) == expected


def test_bm25_exact_match_and_canonical_ties():
    index = BM25Index([
        {"chunk_id": "a", "text": "allocate array"},
        {"chunk_id": "b", "text": "malloc allocate"},
        {"chunk_id": "c", "text": "malloc allocate"},
    ])
    assert [cid for cid, _ in index.search("malloc", 3)] == ["b", "c", "a"]
    assert [cid for cid, _ in index.search("unknown", 3)] == ["a", "b", "c"]


def test_rrf_hand_computed_and_stable_ties():
    scores = rrf_fuse([["a", "b"], ["b", "c"]], k=60)
    assert [cid for cid, _ in scores] == ["b", "a", "c"]
    assert scores[0][1] == pytest.approx(1 / 62 + 1 / 61)
    assert scores[1][1] == pytest.approx(1 / 61)
    assert scores[2][1] == pytest.approx(1 / 62)
    assert [cid for cid, _ in rrf_fuse([["b"], ["a"]])] == ["b", "a"]


def test_hybrid_uses_fake_dense_and_preserves_dense_scores():
    chunks = [{"chunk_id": "a", "text": "red"},
              {"chunk_id": "b", "text": "blue blue"},
              {"chunk_id": "c", "text": "green"}]

    class Dense:
        def retrieve(self, question, k):
            return [{"chunk_id": "c", "score": 0.8}, {"chunk_id": "a", "score": 0.7}][:k]

    retriever = HybridRetriever(Dense(), chunks)
    rows = retriever.retrieve("blue", k=3)
    assert {row["chunk_id"] for row in rows} == {"a", "b", "c"}
    assert next(row for row in rows if row["chunk_id"] == "b")["dense_score"] is None
    assert next(row for row in rows if row["chunk_id"] == "c")["dense_score"] == 0.8
    assert retriever.dense_top1_score("blue") == 0.8


@pytest.mark.parametrize("strategy", ["bm25", "hybrid"])
def test_alternative_reports_reject_official_and_outside_paths(tmp_path, monkeypatch, strategy):
    monkeypatch.chdir(tmp_path)
    for path in ("data/eval/c/reports/v2/e5-large", "elsewhere"):
        with pytest.raises(ValueError, match="hybrid-retrieval"):
            run.run_eval("unused", "unused", path, model_key="e5-large",
                         mode="retrieval-only", retrieval_strategy=strategy)
        with pytest.raises(ValueError, match="hybrid-retrieval"):
            run.write_reports({"retrieval_strategy": strategy}, path)


def test_alternative_requires_retrieval_only(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError, match="retrieval-only"):
        run.run_eval("unused", "unused", "data/research/hybrid-retrieval/x",
                     model_key="e5-large", mode="end-to-end", retrieval_strategy="hybrid")


@pytest.mark.parametrize("strategy", ["bm25", "hybrid"])
def test_research_arm_uses_dense_gate_with_fake_retriever(tmp_path, monkeypatch, strategy):
    monkeypatch.chdir(tmp_path)
    candidate = SimpleNamespace(revision_sha="revision", repository="model", license="test")
    monkeypatch.setattr(run, "get_model_candidate", lambda _: candidate)
    chunks = [{"chunk_id": "a", "text": "irrelevant"},
              {"chunk_id": "b", "text": "exactmatch"}]
    chunk_dir = Path("data/index/c")
    chunk_dir.mkdir(parents=True)
    (chunk_dir / "chunks.jsonl").write_text(''.join(json.dumps(c) + '\n' for c in chunks))
    for pack in run.SUPPORTED_LANGUAGES:
        p = Path(f"data/eval/{pack}/eval-set.{pack}.v1.json")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"fixture")
    import hashlib
    v1_hash = hashlib.sha256(b"fixture").hexdigest()
    calibration = {"model_key": "e5-large", "revision_sha": "revision", "threshold": 0.5,
                   "v1_hashes": {pack: v1_hash for pack in run.SUPPORTED_LANGUAGES}}
    cpath = Path("data/eval/model-comparison/calibration/e5-large.json")
    cpath.parent.mkdir(parents=True)
    cpath.write_text(json.dumps(calibration))
    index = Path("research-index")
    index.mkdir()
    (index / "ids.json").write_text('["a", "b"]')
    (index / "index-meta.json").write_text(json.dumps({
        "model_key": "e5-large", "pack_id": "c", "revision_sha": "revision",
        "chunk_sha256": "hash", "settings_sha256": "settings", "index_sha256": "index",
        "dimension": 2, "count": 2, "truncation_count": 0,
    }))
    benchmark = Path("set.json")
    benchmark.write_text(json.dumps({"version": "fixture", "items": [{
        "item_id": "q1", "qtype": "mixed", "question": "exactmatch",
        "expected_source_ids": ["b"],
    }]}))

    class FakeRetriever:
        def __init__(self, *args, **kwargs):
            pass
        def retrieve(self, question, k):
            return [dict(chunks[0], score=0.4), dict(chunks[1], score=0.3)]

    monkeypatch.setattr(run, "Retriever", FakeRetriever)
    report = run.run_eval(str(benchmark), str(index), "data/research/hybrid-retrieval/test",
                          language="c", model_key="e5-large", mode="retrieval-only",
                          retrieval_strategy=strategy)
    row = report["retrieval"]["rows"][0]
    assert report["retrieval_strategy"] == row["retrieval_strategy"] == strategy
    assert row["top1_score"] == 0.4 and row["fixed_gate_abstain"] is True
    assert row["hit"] is True
