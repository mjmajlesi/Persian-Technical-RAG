"""FAIL-first contract for the three pinned research embedding candidates (003-T003).

T004 provides the registry and src.index.model_config; no model downloads or
LLM calls are needed for these tests.
"""

import re

import pytest

from src.index.model_config import ModelCandidate, get_model_candidate, load_model_registry


@pytest.mark.parametrize(
    ("key", "repository", "sha", "dimension", "query", "passage", "max_tokens"),
    [
        ("e5-large", "intfloat/multilingual-e5-large",
         "3d7cfbdacd47fdda877c5cd8a79fbcc4f2a574f3", 1024,
         "query: ", "passage: ", 512),
        ("e5-base", "intfloat/multilingual-e5-base",
         "d128750597153bb5987e10b1c3493a34e5a4502a", 768,
         "query: ", "passage: ", 512),
        ("bge-m3", "BAAI/bge-m3",
         "5617a9f61b028005a4858fdac845db406aefb181", 1024,
         "", "", 8192),
    ],
)
def test_pinned_model_card(key, repository, sha, dimension, query, passage, max_tokens):
    candidate = get_model_candidate(key)
    assert isinstance(candidate, ModelCandidate)
    assert candidate.model_key == key
    assert candidate.repository == repository
    assert candidate.revision_sha == sha
    assert re.fullmatch(r"[0-9a-f]{40}", candidate.revision_sha)
    assert candidate.license == "MIT"
    assert candidate.model_card_url == f"https://huggingface.co/{repository}"
    assert candidate.dimension == dimension
    assert candidate.query_prefix == query
    assert candidate.passage_prefix == passage
    assert candidate.normalize is True
    assert candidate.max_tokens == max_tokens


def test_registry_is_exactly_the_three_frozen_candidates():
    registry = load_model_registry()
    assert set(registry) == {"e5-large", "e5-base", "bge-m3"}
    assert get_model_candidate().model_key == "e5-large"


def test_unknown_candidate_is_rejected():
    with pytest.raises(ValueError, match="unknown|Unknown"):
        get_model_candidate("unregistered-model")


@pytest.mark.parametrize("revision", ["main", "latest", "v1.0", "3d7cfbd"])
def test_floating_or_short_revision_is_rejected(revision):
    valid = get_model_candidate("e5-large")
    data = {name: getattr(valid, name) for name in (
        "model_key", "repository", "revision_sha", "license", "model_card_url",
        "dimension", "query_prefix", "passage_prefix", "normalize", "max_tokens",
    )}
    data["revision_sha"] = revision
    with pytest.raises(ValueError, match="revision|SHA"):
        ModelCandidate.from_dict(data)
