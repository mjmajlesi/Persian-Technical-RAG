"""F02: synthetic ingest inputs only; preserve the previous published output."""

import json
import os

import pytest

from src.ingest import __main__ as ingest
from src.ingest import writer
from src.ingest.chunker import chunk_markdown


OLD = "خروجی سالم قبلی\n"


def _text(path, text):
    path.write_text(text, encoding="utf-8", newline="\n")
    assert path.read_text(encoding="utf-8") == text
    return path


def _manifest(tmp_path, sources):
    return _text(tmp_path / "manifest.json",
                 json.dumps({"sources": sources}, ensure_ascii=False) + "\n")


def _chunks():
    return chunk_markdown("# بخش\nمتن آزمایشی اول\n\n# دوم\nمتن آزمایشی دوم\n",
                          "fixture", "منبع آزمایشی")


@pytest.mark.parametrize("has_valid_source", [False, True], ids=["all-missing", "partly-missing"])
@pytest.mark.parametrize("previous", [False, True], ids=["new-output", "existing-output"])
def test_missing_source_fails_before_chunking_or_publishing(tmp_path, monkeypatch,
                                                         has_valid_source, previous):
    sources = []
    if has_valid_source:
        origin = _text(tmp_path / "valid.md", "# بخش\nمتن ساختگی\n")
        sources.append({"source_id": "valid", "origin": str(origin)})
    sources.append({"source_id": "missing", "origin": str(tmp_path / "absent.md")})
    manifest = _manifest(tmp_path, sources)
    out = tmp_path / "chunks.jsonl"
    if previous:
        _text(out, OLD)
    calls = []
    real_chunker = ingest.chunk_markdown

    def tracked(*args):
        calls.append(args)
        return real_chunker(*args)

    monkeypatch.setattr(ingest, "chunk_markdown", tracked)
    code = ingest.main(["--manifest", str(manifest), "--out", str(out),
                        "--samples-dir", str(tmp_path / "no-mirrors")])
    assert code != 0
    assert calls == []  # all paths must resolve before doing any chunking
    assert out.read_text(encoding="utf-8") == OLD if previous else not out.exists()


def test_empty_source_does_not_publish_empty_output(tmp_path):
    origin = _text(tmp_path / "empty.md", " \n\t\n")
    manifest = _manifest(tmp_path, [{"source_id": "empty", "origin": str(origin)}])
    out = _text(tmp_path / "chunks.jsonl", OLD)
    assert ingest.main(["--manifest", str(manifest), "--out", str(out),
                        "--samples-dir", str(tmp_path / "no-mirrors")]) != 0
    assert out.read_text(encoding="utf-8") == OLD


def test_writer_rejects_empty_output_before_touching_destination(tmp_path):
    manifest = _manifest(tmp_path, [{"source_id": "fixture"}])
    out = _text(tmp_path / "chunks.jsonl", OLD)
    with pytest.raises(writer.ChunkValidationError):
        writer.write_chunks_jsonl([], manifest, out)
    assert out.read_text(encoding="utf-8") == OLD


@pytest.mark.parametrize("failure", ["serialization", "replace"])
@pytest.mark.parametrize("previous", [False, True], ids=["new-output", "existing-output"])
def test_writer_failure_preserves_destination_and_cleans_temporary_file(
        tmp_path, monkeypatch, failure, previous):
    manifest = _manifest(tmp_path, [{"source_id": "fixture"}])
    out = tmp_path / "chunks.jsonl"
    if previous:
        _text(out, OLD)
    before = set(tmp_path.iterdir())
    if failure == "serialization":
        real_dumps = json.dumps
        calls = []

        def broken_dumps(*args, **kwargs):
            calls.append(1)
            if len(calls) == 2:
                raise OSError("synthetic serialization failure")
            return real_dumps(*args, **kwargs)

        monkeypatch.setattr(json, "dumps", broken_dumps)
    else:
        def broken_replace(source, destination):
            assert out.read_text(encoding="utf-8") == OLD if previous else not out.exists()
            raise OSError("synthetic replace failure")

        monkeypatch.setattr(os, "replace", broken_replace)
    with pytest.raises(OSError, match="synthetic"):
        writer.write_chunks_jsonl(_chunks(), manifest, out)
    assert out.read_text(encoding="utf-8") == OLD if previous else not out.exists()
    assert set(tmp_path.iterdir()) == before


def test_writer_publishes_complete_utf8_jsonl_with_one_atomic_replace(tmp_path, monkeypatch):
    manifest = _manifest(tmp_path, [{"source_id": "fixture"}])
    out = _text(tmp_path / "chunks.jsonl", OLD)
    chunks = _chunks()
    calls = []
    real_replace = os.replace

    def observed_replace(source, destination):
        from pathlib import Path
        source = Path(source)
        assert source.parent == out.parent and source != out
        assert out.read_text(encoding="utf-8") == OLD
        assert [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines()] == [
            chunk.to_dict() for chunk in chunks]
        calls.append((source, destination))
        return real_replace(source, destination)

    monkeypatch.setattr(os, "replace", observed_replace)
    assert writer.write_chunks_jsonl(chunks, manifest, out) == len(chunks)
    assert len(calls) == 1
    assert b"\r" not in out.read_bytes()
    assert [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()] == [
        chunk.to_dict() for chunk in chunks]
    assert set(tmp_path.iterdir()) == {manifest, out}


def test_cli_existing_mirror_fallback_still_succeeds(tmp_path):
    mirror = _text(tmp_path / "fixture.md", "# بخش\nمتن آفلاین ساختگی\n")
    manifest = _manifest(tmp_path, [{"source_id": "fixture", "origin": "https://invalid.example/source"}])
    out = tmp_path / "chunks.jsonl"
    assert ingest.main(["--manifest", str(manifest), "--out", str(out),
                        "--samples-dir", str(tmp_path)]) == 0
    assert [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()] == [
        c.to_dict() for c in chunk_markdown(mirror.read_text(encoding="utf-8"), "fixture", "fixture")]
