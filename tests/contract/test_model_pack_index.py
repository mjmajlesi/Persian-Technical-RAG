"""FAIL-first research retriever isolation contract (003-T009, no LLM/model download)."""

import json
import shutil
from pathlib import Path

import numpy as np
import pytest

from src.index import __main__ as index_cli
from src.index import faiss_store
from src.qa import retriever as retrieval


class _Index:
    def __init__(self, dimension, count):
        self.d = dimension
        self.ntotal = count


def _build(vectors):
    return _Index(vectors.shape[1], vectors.shape[0])


def _write(index, path):
    Path(path).write_text(json.dumps({"dimension": index.d, "count": index.ntotal}),
                          encoding="utf-8")


def _load(directory):
    directory = Path(directory)
    data = json.loads((directory / "faiss.index").read_text(encoding="utf-8"))
    ids = json.loads((directory / "ids.json").read_text(encoding="utf-8"))
    if data["count"] != len(ids):
        raise ValueError("index count does not match ids")
    return _Index(data["dimension"], data["count"]), ids


@pytest.fixture(scope="module")
def pack_template(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("model-pack-index")
    for pack in ("c", "cpp"):
        canonical = tmp_path / "data/index" / pack
        canonical.mkdir(parents=True)
        records = [
            {"chunk_id": f"{pack}-1", "source_id": f"{pack}-source",
             "text": f"{pack} متن اول", "lang": "fa"},
            {"chunk_id": f"{pack}-2", "source_id": f"{pack}-source",
             "text": f"{pack} متن دوم", "lang": "fa"},
        ]
        (canonical / "chunks.jsonl").write_text(
            "\n".join(json.dumps(row, ensure_ascii=False) for row in records) + "\n",
            encoding="utf-8",
        )
        assert "متن اول" in (canonical / "chunks.jsonl").read_text(encoding="utf-8")
        ids = [row["chunk_id"] for row in records]
        (canonical / "ids.json").write_text(json.dumps(ids), encoding="utf-8")
        manifest = tmp_path / "data/corpus" / f"manifest.{pack}.json"
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(json.dumps({"sources": [{"source_id": f"{pack}-source"}]}),
                            encoding="utf-8")
        _write(_Index(1024, 2), canonical / "faiss.index")

    def encode(texts, *, model_key, truncation_stats):
        assert model_key == "e5-base"
        truncation_stats["truncation_count"] = 0
        return np.eye(len(texts), 768, dtype=np.float32)

    with pytest.MonkeyPatch.context() as patch:
        patch.chdir(tmp_path)
        patch.setattr(index_cli, "embed_passages", encode)
        patch.setattr(faiss_store, "build", _build)
        patch.setattr(faiss_store.faiss, "write_index", _write)
        for pack in ("c", "cpp"):
            assert index_cli.main(["build", "--lang", pack, "--model", "e5-base"]) == 0
    return tmp_path


@pytest.fixture
def two_packs(tmp_path, monkeypatch, pack_template):
    shutil.copytree(pack_template / "data", tmp_path / "data")
    monkeypatch.chdir(tmp_path)
    # Keep native FAISS operations out of pre-integration contract tests on
    # Windows: torch import aborts if this fixture runs FAISS first. T008's
    # build tests separately exercise the real FAISS adapter.
    monkeypatch.setattr(faiss_store, "load", _load)
    monkeypatch.setattr(faiss_store, "search",
                        lambda index, ids, vec, k: [(cid, 1.0) for cid in ids[:k]])
    return {pack: tmp_path / "data/research/embedding-compare/e5-base" / pack
            for pack in ("c", "cpp")}


def test_operational_retriever_still_loads_its_own_index(two_packs, tmp_path, monkeypatch):
    default = retrieval.Retriever(tmp_path / "data/index/c")
    assert default.has_chunk("c-1") and not default.has_chunk("cpp-1")
    monkeypatch.setattr(retrieval, "embed_queries",
                        lambda texts: np.eye(1, 1024, dtype=np.float32))
    assert default.retrieve("سؤال فارسی", k=1)[0]["chunk_id"] == "c-1"


def test_research_retrieval_reads_canonical_selected_pack_only(two_packs, monkeypatch):
    calls = []

    def encode(texts, *, model_key):
        calls.append((texts, model_key))
        return np.eye(1, 768, dtype=np.float32)

    monkeypatch.setattr(retrieval, "embed_queries", encode)
    retriever = retrieval.Retriever(two_packs["c"], model_key="e5-base", pack_id="c")
    assert retriever.has_chunk("c-1")
    assert not retriever.has_chunk("cpp-1")  # foreign citation must never validate
    result = retriever.retrieve("حافظه چیست؟", k=2)
    assert calls == [(["حافظه چیست؟"], "e5-base")]
    assert {row["chunk_id"] for row in result} == {"c-1", "c-2"}
    assert all(row["source_id"] == "c-source" for row in result)


def test_wrong_model_for_index_fails(two_packs):
    with pytest.raises(ValueError, match="model|revision|dimension"):
        retrieval.Retriever(two_packs["c"], model_key="bge-m3", pack_id="c")


def test_wrong_pack_for_index_fails(two_packs):
    with pytest.raises(ValueError, match="pack|language|hash"):
        retrieval.Retriever(two_packs["c"], model_key="e5-base", pack_id="cpp")


@pytest.mark.parametrize("field", ["revision_sha", "settings_sha256"])
def test_changed_model_revision_or_settings_fails(two_packs, field):
    path = two_packs["c"] / "index-meta.json"
    metadata = json.loads(path.read_text(encoding="utf-8"))
    metadata[field] = "0" * len(metadata[field])
    path.write_text(json.dumps(metadata, ensure_ascii=False), encoding="utf-8")
    assert json.loads(path.read_text(encoding="utf-8"))[field] == metadata[field]
    with pytest.raises(ValueError, match="model|revision|settings|hash"):
        retrieval.Retriever(two_packs["c"], model_key="e5-base", pack_id="c")


def test_changed_canonical_chunk_text_fails_on_hash(two_packs, tmp_path):
    chunks = tmp_path / "data/index/c/chunks.jsonl"
    chunks.write_text(chunks.read_text(encoding="utf-8").replace("متن اول", "متن جدید"),
                      encoding="utf-8")
    with pytest.raises(ValueError, match="hash|chunk"):
        retrieval.Retriever(two_packs["c"], model_key="e5-base", pack_id="c")


def test_index_dimension_mismatch_fails(two_packs):
    _write(_Index(1024, 2), two_packs["c"] / "faiss.index")
    with pytest.raises(ValueError, match="index|dimension|hash"):
        retrieval.Retriever(two_packs["c"], model_key="e5-base", pack_id="c")


def test_index_ids_out_of_canonical_order_fail(two_packs):
    ids_path = two_packs["c"] / "ids.json"
    ids_path.write_text(json.dumps(["c-2", "c-1"]), encoding="utf-8")
    with pytest.raises(ValueError, match="id|order|chunk"):
        retrieval.Retriever(two_packs["c"], model_key="e5-base", pack_id="c")
