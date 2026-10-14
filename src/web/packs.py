"""Language-pack registry (002-T003).

Reads data/corpus/manifest.<lang>.json files into LanguagePack descriptors.
A pack is `ready` when its index exists, otherwise `empty` (listed but not
yet ingested). Default language is always "c".
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

DEFAULT_LANGUAGE = "c"
SUPPORTED_LANGUAGES = ("c", "cpp", "python", "java")


class PackError(ValueError):
    """Raised for unknown languages or invalid pack manifests."""


@dataclass
class LanguagePack:
    language_id: str
    display_name: str
    status: str  # ready | empty
    snapshot: str | None
    eval_set_version: str | None
    manifest_path: str
    index_dir: str


def load_packs(corpus_dir: str | Path = "data/corpus",
               index_root: str | Path = "data/index") -> list[LanguagePack]:
    """Load every manifest.<lang>.json into validated descriptors."""
    corpus_dir, index_root = Path(corpus_dir), Path(index_root)
    packs: list[LanguagePack] = []
    seen: set[str] = set()
    for manifest_path in sorted(corpus_dir.glob("manifest.*.json")):
        lang = manifest_path.stem.split(".", 1)[1]
        if lang not in SUPPORTED_LANGUAGES:
            raise PackError(f"unsupported language_id in {manifest_path}: {lang}")
        if lang in seen:
            raise PackError(f"duplicate pack manifest for language: {lang}")
        seen.add(lang)
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
        display_name = (raw.get("display_name") or "").strip()
        if not display_name:
            raise PackError(f"{manifest_path} has empty display_name")
        index_dir = index_root / lang
        ready = (index_dir / "faiss.index").is_file() \
            and (index_dir / "chunks.jsonl").is_file()
        packs.append(LanguagePack(
            language_id=lang,
            display_name=display_name,
            status="ready" if ready else "empty",
            snapshot=raw.get("snapshot"),
            eval_set_version=raw.get("eval_set_version"),
            manifest_path=str(manifest_path),
            index_dir=str(index_dir),
        ))
    return packs


def get_pack(language_id: str, packs: list[LanguagePack] | None = None) -> LanguagePack:
    """Return the pack for a language id, or raise PackError if unknown."""
    packs = packs if packs is not None else load_packs()
    for pack in packs:
        if pack.language_id == language_id:
            return pack
    raise PackError(f"unknown language: {language_id}")
