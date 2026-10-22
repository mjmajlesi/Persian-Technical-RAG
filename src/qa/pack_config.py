"""Per-pack abstention threshold config (002-T009 -> replaced by 002-T024).

Stores the abstention similarity threshold per LanguagePack so each language
applies its own gate. Values measured by src/eval/calibrate.py (T024,
2026-10-22) on each pack's own 30-item eval set: threshold = maximally
balanced gap midpoint = (max(out-of-corpus top-1) + min(answerable top-1))
over the 25 answerable / 5 out-of-corpus items. Packs where the two classes
overlap keep the same rule; the residual overlap is listed here because
those outliers are covered by the LLM-insufficient backstop (gate-passing
OOC question -> CANNOT_ANSWER -> abstain), never silently answered.
"""

from __future__ import annotations

from src.qa.abstain import DEFAULT_THRESHOLD

PACK_THRESHOLD_DEFAULT = DEFAULT_THRESHOLD  # hermetic fallback for unknown ids

# 002-T024 measured values (see calibrate.py header for the full tables).
# Stored at 2-3 decimals because FAISS top-1 scores jitter ~3e-4 across
# runs; thresholds sit inside the measured gap with documented residuals:
#   c      0.803  (0.793 C-O05 / 0.814 C-009)               separable
#   cpp    0.82   (0.822 CPP-O01 / 0.821 CPP-019)           overlap 0.001
#          -> CPP-O01 gate-passes; the backstop abstains it.
#   python 0.79   (0.797 PY-O01 / 0.786 PY-006)             overlap 0.011
#          -> PY-O01/PY-O02 gate-pass; the backstop abstains them.
#   java   0.791  (0.790 JV-O01 / 0.792 JV-013-JV-003)      separable
PACK_THRESHOLDS: dict[str, float] = {
    "c": 0.803,
    "cpp": 0.82,
    "python": 0.79,
    "java": 0.791,
}


def threshold_for(language_id: str) -> float:
    """Return the pack's abstention threshold (provisional default if unknown)."""
    return PACK_THRESHOLDS.get(language_id, PACK_THRESHOLD_DEFAULT)
