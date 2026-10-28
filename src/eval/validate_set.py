"""Validate source-grounded v2 sets against frozen pack chunks and v1 questions."""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path

from src.web.packs import SUPPORTED_LANGUAGES


def _plain(text: str) -> str:
    return " ".join(text.casefold().replace("ي", "ی").replace("ك", "ک").split())


def _nonempty(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def ensure_unique_questions(items: list[dict]) -> None:
    """Reject duplicate normalized question texts within one set."""
    seen = set()
    for item in items:
        if not isinstance(item, dict) or not _nonempty(item.get("question")):
            raise ValueError("each item requires a non-empty question")
        question = _plain(item["question"])
        if question in seen:
            raise ValueError(f"duplicate normalized question: {item.get('item_id')}")
        seen.add(question)


def validate_set(path: str | Path, *, pack_id: str, complete: bool = True) -> dict:
    """Return counts/review flags, or reject invalid/copy-pasted evidence.

    `complete=False` accepts only an in-corpus 28-item draft and labels it
    incomplete. Near-v1 wording requires human review, never auto-publication.
    """
    if pack_id not in SUPPORTED_LANGUAGES:
        raise ValueError("unsupported pack_id")
    spec = json.loads(Path(path).read_text(encoding="utf-8"))
    version = f"{pack_id}-v2"
    if spec.get("pack_id") != pack_id or spec.get("version") != version:
        raise ValueError("set pack_id/version mismatch")
    items = spec.get("items")
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    ensure_unique_questions(items)

    chunks = {chunk["chunk_id"]: chunk for line in
              Path(f"data/index/{pack_id}/chunks.jsonl").read_text(encoding="utf-8").splitlines()
              if (chunk := json.loads(line))}
    sources = {source["source_id"]: source for source in
               json.loads(Path(f"data/corpus/manifest.{pack_id}.json").read_text(
                   encoding="utf-8"))["sources"]}
    v1 = json.loads(Path(f"data/eval/{pack_id}/eval-set.{pack_id}.v1.json").read_text(
        encoding="utf-8"))["items"]
    old_questions = [_plain(item["question"]) for item in v1]
    old_ids = {item["item_id"] for item in v1}
    old_words = [set(re.findall(r"\w+", question)) for question in old_questions]
    chunk_texts = [_plain(chunk["text"]) for chunk in chunks.values()]
    seen = set()
    review_flags = []
    counts = Counter()

    for item in items:
        if not isinstance(item, dict):
            raise ValueError("each item must be an object")
        item_id = item.get("item_id")
        if not _nonempty(item_id) or item_id in seen or item_id in old_ids:
            raise ValueError(f"duplicate or v1 item_id: {item_id}")
        seen.add(item_id)
        if item.get("pack_id") != pack_id or item.get("version") != version:
            raise ValueError(f"item pack_id/version mismatch: {item_id}")
        qtype = item.get("qtype")
        if qtype not in ("in-corpus", "mixed", "out-of-corpus"):
            raise ValueError(f"invalid qtype: {item_id}")
        counts[qtype] += 1
        question = item.get("question")
        if not _nonempty(question) or len(re.findall(r"[\u0621-\u064a\u067e\u0686\u0698\u06af\u06a9\u06cc]", question)) < 3:
            raise ValueError(f"question must be Persian: {item_id}")
        if qtype == "mixed" and not re.search(r"[A-Za-z]", question):
            raise ValueError(f"mixed question needs an English technical term: {item_id}")
        normalized = _plain(question)
        if normalized in old_questions or any(normalized in text for text in chunk_texts):
            raise ValueError(f"copied v1/chunk question: {item_id}")

        author = item.get("authorship")
        if not isinstance(author, dict) or not all(_nonempty(author.get(key)) for key in
                                                   ("author", "authored_at", "review_status")):
            raise ValueError(f"missing authorship/review metadata: {item_id}")
        if author["review_status"] not in ("draft", "pending-user-review", "reviewed"):
            raise ValueError(f"invalid review status: {item_id}")
        try:
            date.fromisoformat(author["authored_at"])
        except ValueError:
            raise ValueError(f"invalid authored_at: {item_id}") from None
        if author["review_status"] == "reviewed":
            if not _nonempty(author.get("reviewer")) or not _nonempty(author.get("reviewed_at")):
                raise ValueError(f"missing reviewer/date: {item_id}")
            try:
                date.fromisoformat(author["reviewed_at"])
            except ValueError:
                raise ValueError(f"invalid reviewed_at: {item_id}") from None
        if complete and author["review_status"] != "reviewed":
            raise ValueError(f"unreviewed item: {item_id}")

        evidence = item.get("evidence_language")
        ids = item.get("expected_source_ids")
        provenance = item.get("provenance")
        if qtype == "out-of-corpus":
            if ids != [] or provenance != [] or evidence != "none" or not _nonempty(item.get("abstain_reason")):
                raise ValueError(f"out-of-corpus requires empty sources and abstain reason: {item_id}")
            if _nonempty(item.get("expected_answer_summary")):
                raise ValueError(f"out-of-corpus must not have an answer summary: {item_id}")
        else:
            if evidence not in ("fa", "en", "mixed"):
                raise ValueError(f"invalid evidence_language: {item_id}")
            if not _nonempty(item.get("expected_answer_summary")) or _nonempty(item.get("abstain_reason")):
                raise ValueError(f"missing/ambiguous grounded summary: {item_id}")
            if (not isinstance(ids, list) or not ids or
                    any(not _nonempty(cid) for cid in ids) or
                    len(set(ids)) != len(ids) or
                    any(cid not in chunks for cid in ids)):
                raise ValueError(f"source chunk outside selected pack or missing: {item_id}")
            if not isinstance(provenance, list) or len(provenance) != len(ids) or any(
                not isinstance(entry, dict) for entry in provenance
            ):
                raise ValueError(f"missing source provenance: {item_id}")
            if (any(not _nonempty(entry.get("chunk_id")) for entry in provenance) or
                    {entry["chunk_id"] for entry in provenance} != set(ids)):
                raise ValueError(f"source provenance/chunk IDs mismatch: {item_id}")
            languages = {chunks[cid]["lang"] for cid in ids}
            if evidence != (next(iter(languages)) if len(languages) == 1 else "mixed"):
                raise ValueError(f"evidence_language does not match chunks: {item_id}")
            for entry in provenance:
                chunk = chunks[entry["chunk_id"]]
                source = sources.get(chunk["source_id"])
                if (source is None or entry.get("source_id") != chunk["source_id"] or
                    entry.get("section_heading") != chunk["section_heading"] or
                    any(not _nonempty(entry.get(key)) or entry[key] != source[key]
                        for key in ("title", "origin", "snapshot", "license"))):
                    raise ValueError(f"source origin/license/provenance mismatch: {item_id}")

        words = set(re.findall(r"\w+", normalized))
        if any((len(words & prior) / len(words | prior) >= 0.65 if words | prior else False)
               or SequenceMatcher(None, normalized, old).ratio() >= 0.8
               for old, prior in zip(old_questions, old_words)):
            review_flags.append({"item_id": item_id, "reason": "near-v1 paraphrase; human review required"})

    required = {"in-corpus": 28, "mixed": 10, "out-of-corpus": 7} if complete else {
        "in-corpus": 28, "mixed": 0, "out-of-corpus": 0,
    }
    if {key: counts[key] for key in required} != required or len(items) != sum(required.values()):
        raise ValueError("complete set requires 45 (28/10/7); draft requires 28 in-corpus")
    # ponytail: 45 × 1k literal/near-copy checks are cheap; index only if the corpus grows.
    return {"status": "incomplete" if not complete else
            "needs_review" if review_flags else "complete",
            "counts": {key: counts[key] for key in required}, "review_flags": review_flags}
