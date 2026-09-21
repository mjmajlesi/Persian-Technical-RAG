"""Section-aware Markdown chunker (T006).

Splits documents on Markdown headings, never cutting inside fenced code
blocks. Chunks target ~TARGET_WORDS words with ~OVERLAP_WORDS words of
overlap. Word counts are an approximation of tokens (documented in
research.md chunking decision); the limit keeps chunks well inside the
~512-token budget for mixed Persian/English text.

Emits Chunk objects matching the CorpusChunk entity in data-model.md.
Standard library only.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass

TARGET_WORDS = 512
OVERLAP_WORDS = 64

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
_FENCE_RE = re.compile(r"^\s*```")


def detect_lang(text: str) -> str:
    """fa | en | mixed based on script presence (data-model.md lang enum)."""
    has_fa = any("؀" <= ch <= "ۿ" for ch in text)
    has_latin = any("A" <= ch <= "Z" or "a" <= ch <= "z" for ch in text)
    if has_fa and has_latin:
        return "mixed"
    if has_fa:
        return "fa"
    return "en"


@dataclass
class Chunk:
    chunk_id: str  # {source_id}#s{section:02d}-c{ordinal:02d}, deterministic
    source_id: str
    doc_title: str
    section_heading: str  # non-empty
    text: str  # non-empty
    lang: str  # fa | en | mixed

    def to_dict(self) -> dict:
        return asdict(self)


def _split_words(text: str) -> list[str]:
    return text.split()


def _window_split(words: list[str], prefix: str) -> list[str]:
    """Greedy windows of TARGET_WORDS with OVERLAP_WORDS overlap."""
    if len(words) <= TARGET_WORDS:
        return [" ".join(words)]
    out: list[str] = []
    start = 0
    step = TARGET_WORDS - OVERLAP_WORDS
    while start < len(words):
        out.append(" ".join(words[start : start + TARGET_WORDS]))
        if start + TARGET_WORDS >= len(words):
            break
        start += step
    return out


def chunk_markdown(text: str, source_id: str, doc_title: str) -> list[Chunk]:
    """Split a Markdown document into section-grounded chunks."""
    # Pass 1: group lines into (heading, lines), tracking fenced code blocks
    # so headings inside code fences are ignored and fences stay intact.
    sections: list[tuple[str, list[str]]] = []
    cur_heading = ""
    cur_lines: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            cur_lines.append(line)
            continue
        m = _HEADING_RE.match(line) if not in_fence else None
        if m:
            if cur_lines and any(l.strip() for l in cur_lines):
                sections.append((cur_heading, cur_lines))
            cur_heading = m.group(2).strip()
            cur_lines = []
        else:
            cur_lines.append(line)
    if cur_lines and any(l.strip() for l in cur_lines):
        sections.append((cur_heading, cur_lines))

    # Pass 2: window long sections; keep each code fence inside one window by
    # first splitting the section body on blank lines outside fences, then
    # greedily packing blocks (a fence block is atomic).
    chunks: list[Chunk] = []
    for s_idx, (heading, lines) in enumerate(sections, start=1):
        section_heading = heading or doc_title
        blocks: list[str] = []
        buf: list[str] = []
        in_fence = False
        for line in lines:
            if _FENCE_RE.match(line):
                in_fence = not in_fence
                buf.append(line)
                if not in_fence:
                    blocks.append("\n".join(buf).strip())
                    buf = []
                continue
            if in_fence:
                buf.append(line)
                continue
            if not line.strip():
                if buf:
                    blocks.append("\n".join(buf).strip())
                    buf = []
            else:
                buf.append(line)
        if buf:
            blocks.append("\n".join(buf).strip())
        blocks = [b for b in blocks if b]

        windows: list[str] = []
        current: list[str] = []
        current_words = 0
        for block in blocks:
            n = len(_split_words(block))
            if n > TARGET_WORDS:
                # Oversized single block (e.g. giant code sample): fall back
                # to word windows; code may split here only as last resort.
                if current:
                    windows.append("\n\n".join(current))
                    current, current_words = [], 0
                windows.extend(_window_split(_split_words(block), ""))
            elif current_words + n > TARGET_WORDS and current:
                windows.append("\n\n".join(current))
                # overlap: carry the tail of the previous window
                tail = _split_words(windows[-1])[-OVERLAP_WORDS:]
                current, current_words = [" ".join(tail)], len(tail)
                current.append(block)
                current_words += n
            else:
                current.append(block)
                current_words += n
        if current:
            windows.append("\n\n".join(current))

        for c_idx, body in enumerate(windows, start=1):
            body = body.strip()
            if not body:
                continue
            chunks.append(
                Chunk(
                    chunk_id=f"{source_id}#s{s_idx:02d}-c{c_idx:02d}",
                    source_id=source_id,
                    doc_title=doc_title,
                    section_heading=section_heading,
                    text=body,
                    lang=detect_lang(body),
                )
            )
    return chunks
