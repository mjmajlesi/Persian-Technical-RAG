"""Unit tests (US4, T029): scoring helpers in src/eval/scoring.py.

TDD: written BEFORE the scorer (T031) exists, so collection FAILS (import
error) until T031 implements the helpers below. The signatures here are the
contract T031 must satisfy (metric definitions: contracts/eval-set-schema.md).
Run: pytest tests/unit/test_scoring.py
"""

import pytest

from src.eval.scoring import (
    abstention_correct,
    citation_precision,
    hit_rate_at_5,
    mixed_slice_scores,
)


def test_hit_rate_at_5_hit():
    assert hit_rate_at_5(["a#s01-c01"], ["x", "a#s01-c01", "y"]) is True


def test_hit_rate_at_5_miss():
    assert hit_rate_at_5(["a#s01-c01"], ["x", "y", "z"]) is False


def test_hit_rate_at_5_empty_expected():
    # out-of-corpus items carry no expected sources: never a "hit".
    assert hit_rate_at_5([], ["x", "y"]) is False


def test_citation_precision_perfect():
    cited = ["a#s01-c01", "a#s02-c01"]
    assert citation_precision(cited, {"a#s01-c01", "a#s02-c01", "b"},
                              ["a#s01-c01", "a#s02-c01"]) == 1.0


def test_citation_precision_phantom():
    # one cited id exists nowhere: precision drops, never crashes.
    assert citation_precision(["a#s01-c01", "ghost#s99-c99"],
                              {"a#s01-c01"}, ["a#s01-c01"]) == pytest.approx(0.5)


def test_citation_precision_empty_cited():
    # abstention-style: nothing cited, nothing wrong.
    assert citation_precision([], {"a#s01-c01"}, []) == 1.0


def test_abstention_correct_out_of_corpus():
    assert abstention_correct("out-of-corpus", {"type": "abstain",
                                                "citations": []}) is True


def test_abstention_correct_fabricated():
    assert abstention_correct("out-of-corpus", {"type": "answer",
                                                "citations": ["a"]}) is False


def test_abstention_correct_in_corpus_answered():
    assert abstention_correct("in-corpus", {"type": "answer",
                                            "citations": ["a"]}) is True


def test_mixed_slice_scores():
    rows = [
        {"qtype": "mixed", "hit": True, "precision": 1.0},
        {"qtype": "mixed", "hit": False, "precision": 0.5},
        {"qtype": "in-corpus", "hit": True, "precision": 1.0},
    ]
    out = mixed_slice_scores(rows)
    assert out["hit_rate_at_5"] == pytest.approx(0.5)
    assert out["citation_precision"] == pytest.approx(0.75)
    assert out["n"] == 2  # only mixed rows counted
