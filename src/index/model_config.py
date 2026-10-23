"""Pinned research embedding settings; operational embedding remains unchanged."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


REGISTRY_PATH = Path(__file__).resolve().parents[2] / "data/eval/model-comparison/models.json"


@dataclass(frozen=True)
class ModelCandidate:
    model_key: str
    repository: str
    revision_sha: str
    license: str
    model_card_url: str
    dimension: int
    query_prefix: str
    passage_prefix: str
    normalize: bool
    max_tokens: int

    @classmethod
    def from_dict(cls, data: dict) -> ModelCandidate:
        candidate = cls(**data)
        if not re.fullmatch(r"[0-9a-f]{40}", candidate.revision_sha):
            raise ValueError("revision_sha must be a pinned 40-character SHA")
        if not candidate.model_key or not candidate.repository or not candidate.model_card_url:
            raise ValueError("model identity and model card URL are required")
        if candidate.license != "MIT" or candidate.normalize is not True:
            raise ValueError("research candidates require MIT license and normalized vectors")
        if not isinstance(candidate.dimension, int) or candidate.dimension <= 0:
            raise ValueError("dimension must be a positive integer")
        if not isinstance(candidate.max_tokens, int) or candidate.max_tokens <= 0:
            raise ValueError("max_tokens must be a positive integer")
        if not isinstance(candidate.query_prefix, str) or not isinstance(candidate.passage_prefix, str):
            raise ValueError("prefixes must be text")
        return candidate


def load_model_registry(path: Path = REGISTRY_PATH) -> dict[str, ModelCandidate]:
    entries = json.loads(Path(path).read_text(encoding="utf-8"))["models"]
    candidates = [ModelCandidate.from_dict(entry) for entry in entries]
    registry = {candidate.model_key: candidate for candidate in candidates}
    if len(registry) != len(candidates):
        raise ValueError("duplicate model_key in registry")
    return registry


def get_model_candidate(model_key: str = "e5-large") -> ModelCandidate:
    registry = load_model_registry()
    try:
        return registry[model_key]
    except KeyError as exc:
        raise ValueError(f"unknown model: {model_key}") from exc
