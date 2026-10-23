"""FAIL-first cache integrity contract for 003-T007; T008 supplies the code."""

import json
from dataclasses import replace

import numpy as np
import pytest

from src.index.model_config import get_model_candidate
from src.index.research_cache import cached_embeddings


CHUNKS = [
    {"chunk_id": "c-a", "text": "حافظهٔ پویا"},
    {"chunk_id": "c-b", "text": "آرایه و اشاره‌گر"},
]


def _encode(dimension, calls):
    def encode(texts):
        calls.append(list(texts))
        return np.ones((len(texts), dimension), dtype=np.float32)
    return encode


def test_exact_cache_hit_skips_encoding(tmp_path):
    model = get_model_candidate("e5-large")
    calls = []
    encode = _encode(model.dimension, calls)
    first, hit = cached_embeddings(model, "c", CHUNKS, tmp_path, encode)
    assert hit is False
    second, hit = cached_embeddings(
        model, "c", CHUNKS, tmp_path,
        lambda texts: pytest.fail("exact cache hit must not re-encode"),
    )
    assert hit is True
    np.testing.assert_array_equal(first, second)
    assert calls == [[record["text"] for record in CHUNKS]]


@pytest.mark.parametrize("change", [
    "revision_sha", "repository", "query_prefix", "passage_prefix",
    "normalize", "max_tokens", "dimension", "pack_id", "chunk_id",
    "text", "order", "vector_dtype",
])
def test_each_fingerprint_input_change_misses_from_same_baseline(tmp_path, change):
    model = get_model_candidate("e5-large")
    chunks = [record.copy() for record in CHUNKS]
    pack_id = "c"
    vector_dtype = "float32"
    calls = []
    cached_embeddings(model, pack_id, chunks, tmp_path, _encode(model.dimension, calls))
    if change == "revision_sha":
        model = replace(model, revision_sha="a" * 40)
    elif change == "repository":
        model = replace(model, repository="other/repository")
    elif change in ("query_prefix", "passage_prefix"):
        model = replace(model, **{change: "changed: "})
    elif change == "normalize":
        model = replace(model, normalize=False)
    elif change == "max_tokens":
        model = replace(model, max_tokens=256)
    elif change == "dimension":
        model = replace(model, dimension=768)
    elif change == "pack_id":
        pack_id = "cpp"
    elif change == "chunk_id":
        chunks[0]["chunk_id"] = "different"
    elif change == "text":
        chunks[0]["text"] += " جدید"
    elif change == "order":
        chunks.reverse()
    elif change == "vector_dtype":
        vector_dtype = "float64"
    vectors, hit = cached_embeddings(
        model, pack_id, chunks, tmp_path, _encode(model.dimension, calls),
        vector_dtype=vector_dtype,
    )
    assert hit is False, change
    assert len(calls) == 2, change
    assert vectors.shape == (2, model.dimension)


@pytest.mark.parametrize("missing", ["vectors", "metadata"])
def test_partial_cache_is_not_ready(tmp_path, missing):
    model = get_model_candidate("e5-large")
    calls = []
    cached_embeddings(model, "c", CHUNKS, tmp_path, _encode(model.dimension, calls))
    if missing == "vectors":
        next(tmp_path.glob("*.npy")).unlink()
    else:
        (tmp_path / "cache.json").unlink()
    _, hit = cached_embeddings(model, "c", CHUNKS, tmp_path,
                               _encode(model.dimension, calls))
    assert hit is False
    assert len(calls) == 2


def test_cached_id_mismatch_fails_explicitly(tmp_path):
    model = get_model_candidate("e5-large")
    cached_embeddings(model, "c", CHUNKS, tmp_path, _encode(model.dimension, []))
    path = tmp_path / "cache.json"
    metadata = json.loads(path.read_text(encoding="utf-8"))
    metadata["chunk_ids"] = ["foreign-c", "c-b"]
    path.write_text(json.dumps(metadata, ensure_ascii=False), encoding="utf-8")
    assert json.loads(path.read_text(encoding="utf-8"))["chunk_ids"][0] == "foreign-c"
    with pytest.raises(ValueError, match="id|ID"):
        cached_embeddings(model, "c", CHUNKS, tmp_path,
                          lambda texts: pytest.fail("corruption must not re-encode silently"))


@pytest.mark.parametrize("shape", [(1, 1024), (2, 768)])
def test_cached_count_or_dimension_mismatch_fails(tmp_path, shape):
    model = get_model_candidate("e5-large")
    cached_embeddings(model, "c", CHUNKS, tmp_path, _encode(model.dimension, []))
    np.save(next(tmp_path.glob("*.npy")), np.zeros(shape, dtype=np.float32))
    with pytest.raises(ValueError, match="shape|dimension|count"):
        cached_embeddings(model, "c", CHUNKS, tmp_path,
                          lambda texts: pytest.fail("corrupt vectors must not be reused"))
