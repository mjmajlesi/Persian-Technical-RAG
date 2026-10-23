"""Research index build stays scoped to the canonical pack (003-T008)."""

import hashlib
import json

import numpy as np
import pytest

from src.index import __main__ as index_cli


def _pack(tmp_path):
    chunks_dir = tmp_path / "data/index/c"
    chunks_dir.mkdir(parents=True)
    records = [
        {"chunk_id": "c-1", "source_id": "sample", "text": "حافظهٔ پویا"},
        {"chunk_id": "c-2", "source_id": "sample", "text": "آرایه"},
    ]
    chunks = chunks_dir / "chunks.jsonl"
    chunks.write_text("\n".join(json.dumps(record, ensure_ascii=False)
                                for record in records) + "\n", encoding="utf-8")
    (chunks_dir / "ids.json").write_text(json.dumps(["c-1", "c-2"]), encoding="utf-8")
    corpus = tmp_path / "data/corpus"
    corpus.mkdir(parents=True)
    (corpus / "manifest.c.json").write_text(
        json.dumps({"sources": [{"source_id": "sample"}]}), encoding="utf-8"
    )
    assert "حافظهٔ پویا" in chunks.read_text(encoding="utf-8")
    return chunks_dir


def test_research_build_uses_canonical_chunks_and_hits_cache(tmp_path, monkeypatch):
    chunks_dir = _pack(tmp_path)
    chunks = chunks_dir / "chunks.jsonl"
    before = hashlib.sha256(chunks.read_bytes()).hexdigest()
    calls = []

    def encode(texts, *, model_key, truncation_stats):
        assert model_key == "e5-base"
        calls.append(texts)
        truncation_stats["truncation_count"] = 1
        return np.ones((len(texts), 768), dtype=np.float32) / np.sqrt(768)

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(index_cli, "embed_passages", encode)
    assert index_cli.main(["build", "--lang", "c", "--model", "e5-base"]) == 0
    out = tmp_path / "data/research/embedding-compare/e5-base/c"
    manifest = json.loads((out / "index-meta.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "ready" and manifest["cache_hit"] is False
    assert manifest["chunk_sha256"] == before and manifest["dimension"] == 768
    assert manifest["truncation_count"] == 1
    assert json.loads((out / "ids.json").read_text(encoding="utf-8")) == ["c-1", "c-2"]
    assert (out / "faiss.index").exists()
    assert not (out / "chunks.jsonl").exists()
    assert not (chunks_dir / "faiss.index").exists()

    assert index_cli.main(["build", "--lang", "c", "--model", "e5-base"]) == 0
    manifest = json.loads((out / "index-meta.json").read_text(encoding="utf-8"))
    assert manifest["cache_hit"] is True and manifest["truncation_count"] == 1
    assert len(calls) == 1 and hashlib.sha256(chunks.read_bytes()).hexdigest() == before

    chunks.write_text(chunks.read_text(encoding="utf-8").replace("آرایه", "ساختار"),
                      encoding="utf-8")
    old_index = (out / "faiss.index").read_bytes()
    old_manifest = (out / "index-meta.json").read_bytes()
    def fail(*args, **kwargs):
        raise RuntimeError("encoding interrupted")
    monkeypatch.setattr(index_cli, "embed_passages", fail)
    with pytest.raises(RuntimeError, match="interrupted"):
        index_cli.main(["build", "--lang", "c", "--model", "e5-base"])
    assert (out / "faiss.index").read_bytes() == old_index
    assert (out / "index-meta.json").read_bytes() == old_manifest


def test_research_build_rejects_mismatched_canonical_ids(tmp_path, monkeypatch):
    chunks_dir = _pack(tmp_path)
    (chunks_dir / "ids.json").write_text('["foreign", "c-2"]', encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError, match="canonical chunk IDs"):
        index_cli.main(["build", "--lang", "c", "--model", "e5-base"])
    assert not (tmp_path / "data/research").exists()


def test_no_model_flag_keeps_operational_build_path(tmp_path, monkeypatch):
    chunks_dir = _pack(tmp_path)
    original = (chunks_dir / "chunks.jsonl").read_bytes()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(index_cli, "embed_passages",
                        lambda texts: np.ones((len(texts), 1024), dtype=np.float32))
    assert index_cli.main(["build", "--lang", "c"]) == 0
    assert (chunks_dir / "faiss.index").exists()
    assert (chunks_dir / "chunks.jsonl").read_bytes() == original
    assert not (tmp_path / "data/research").exists()


def test_failed_index_write_keeps_previous_ready_index(tmp_path, monkeypatch):
    chunks_dir = _pack(tmp_path)
    monkeypatch.chdir(tmp_path)

    def encode(texts, *, model_key, truncation_stats):
        truncation_stats["truncation_count"] = 0
        return np.ones((len(texts), 768), dtype=np.float32)

    monkeypatch.setattr(index_cli, "embed_passages", encode)
    index_cli.main(["build", "--lang", "c", "--model", "e5-base"])
    out = tmp_path / "data/research/embedding-compare/e5-base/c"
    before_index = (out / "faiss.index").read_bytes()
    before_meta = (out / "index-meta.json").read_bytes()

    def interrupt(index, filename):
        raise RuntimeError("index write interrupted")

    monkeypatch.setattr(index_cli.faiss_store.faiss, "write_index", interrupt)
    with pytest.raises(RuntimeError, match="interrupted"):
        index_cli.main(["build", "--lang", "c", "--model", "e5-base"])
    assert (out / "faiss.index").read_bytes() == before_index
    assert (out / "index-meta.json").read_bytes() == before_meta
    assert not list(out.glob("*.tmp"))
