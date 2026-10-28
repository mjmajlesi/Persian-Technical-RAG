"""F06: operational integrity without loading embedding models or writing data/."""
import json
import logging
from pathlib import Path
from types import SimpleNamespace

import fastapi.routing
import pytest

from src.index.embed import MODEL_ID
from src.qa import retriever as retrieval
from src.web import app as web
from src.web import packs


def write(path, text):
    path.write_text(text, encoding="utf-8", newline="\n")
    assert path.read_text(encoding="utf-8") == text


@pytest.fixture
def index(tmp_path, monkeypatch):
    records = [{"chunk_id": "a#1"}, {"chunk_id": "b#1"}]
    write(tmp_path / "chunks.jsonl", "".join(json.dumps(r) + "\n" for r in records))
    ids = [r["chunk_id"] for r in records]
    fake = SimpleNamespace(d=1024, ntotal=2)
    monkeypatch.setattr(retrieval.faiss_store, "load", lambda directory: (fake, ids))
    return tmp_path, fake, ids


@pytest.mark.parametrize("fault", ["reversed", "duplicate-ids", "duplicate-chunks", "extra-chunk", "dimension", "count"])
def test_corrupt_operational_indexes_fail(index, fault):
    path, fake, ids = index
    if fault == "reversed":
        ids.reverse()
    elif fault == "duplicate-ids":
        ids[1] = ids[0]
    elif fault == "duplicate-chunks":
        write(path / "chunks.jsonl", '{"chunk_id":"a#1"}\n{"chunk_id":"a#1"}\n')
    elif fault == "extra-chunk":
        write(path / "chunks.jsonl", '{"chunk_id":"a#1"}\n{"chunk_id":"b#1"}\n{"chunk_id":"c#1"}\n')
    elif fault == "dimension":
        fake.d = 768
    else:
        fake.ntotal = 1
    with pytest.raises(ValueError, match="(?i)index|ids|dimension|count"):
        retrieval.Retriever(path)


@pytest.mark.parametrize("metadata", [
    {"model_key": "bge-m3"}, {"model_key": "e5-large", "repository": "wrong/model"},
    {"model_key": "e5-large", "revision_sha": "0" * 40}, {}, None, [],
])
def test_incompatible_or_malformed_model_metadata_fails(index, metadata):
    path, _, _ = index
    write(path / "index-meta.json", json.dumps(metadata))
    with pytest.raises(ValueError, match="(?i)model|identity|metadata|revision"):
        retrieval.Retriever(path)


def test_matching_metadata_loads_without_legacy_warning(index, caplog):
    path, _, _ = index
    candidate = retrieval.get_model_candidate("e5-large")
    write(path / "index-meta.json", json.dumps({"model_key": "e5-large", "repository": MODEL_ID,
                                                 "revision_sha": candidate.revision_sha}))
    with caplog.at_level(logging.WARNING, logger=retrieval.__name__):
        retrieval.Retriever(path)
    assert not caplog.records


def test_legacy_warning_once_per_process(index, caplog, monkeypatch):
    path, _, _ = index
    monkeypatch.setattr(retrieval, "_legacy_identity_warned", False, raising=False)
    with caplog.at_level(logging.WARNING, logger=retrieval.__name__):
        retrieval.Retriever(path)
        retrieval.Retriever(path)
    records = [r for r in caplog.records if "هویت مدل تأییدنشده" in r.getMessage()]
    assert len(records) == 1


def test_registry_requires_ids(tmp_path):
    corpus, indexes = tmp_path / "corpus", tmp_path / "index"
    corpus.mkdir()
    directory = indexes / "c"
    directory.mkdir(parents=True)
    write(corpus / "manifest.c.json", json.dumps({"display_name": "C"}))
    write(directory / "faiss.index", "synthetic")
    write(directory / "chunks.jsonl", "synthetic")
    assert packs.load_packs(corpus, indexes)[0].status == "empty"
    write(directory / "ids.json", "[]")
    assert packs.load_packs(corpus, indexes)[0].status == "ready"


def test_corrupt_index_has_clear_status_error(monkeypatch):
    monkeypatch.setattr(web.pack_registry, "get_pack", lambda language: SimpleNamespace(status="ready", language_id=language))
    def bad(language):
        raise ValueError("synthetic corrupt index")
    monkeypatch.setattr(web, "get_retriever", bad)
    with pytest.raises(web.HTTPException) as caught:
        web.ask(web.AskRequest(question="پرسش آزمایشی درباره این موضوع چیست", language="c"))
    assert caught.value.status_code == 503
    assert "ایندکس" in caught.value.detail


@pytest.mark.parametrize("language", ["c", "cpp", "python", "java"])
def test_real_index_loads_without_model_or_rebuild(language, monkeypatch):
    monkeypatch.setattr(retrieval, "embed_queries", lambda *args, **kwargs: pytest.fail("model invoked"))
    instance = retrieval.Retriever(Path("data/index") / language)
    assert instance._index.d == 1024 and instance._index.ntotal == len(instance._ids)


def test_real_languages_api_remains_ready(monkeypatch):
    async def inline(function, *args, **kwargs):
        return function(*args, **kwargs)
    monkeypatch.setattr(fastapi.routing, "run_in_threadpool", inline)
    messages = []
    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}
    async def send(message):
        messages.append(message)
    scope = {"type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1",
             "method": "GET", "scheme": "http", "path": "/api/languages",
             "raw_path": b"/api/languages", "query_string": b"", "root_path": "",
             "headers": [], "client": ("memory", 1), "server": ("memory", 80)}
    request = web.app(scope, receive, send)
    try:
        with pytest.raises(StopIteration):
            request.send(None)
    finally:
        request.close()
    assert next(m["status"] for m in messages if m["type"] == "http.response.start") == 200
    result = json.loads(b"".join(m.get("body", b"") for m in messages
                                  if m["type"] == "http.response.body").decode("utf-8"))
    assert {p["language_id"]: p["status"] for p in result["languages"]} == {
        "c": "ready", "cpp": "ready", "python": "ready", "java": "ready"}
