"""Per-pack abstention threshold config (002-T009).

Stores the abstention similarity threshold per LanguagePack so each language
applies its own gate. Every pack currently starts from the provisional 0.81
calibrated on the C index (feature 001 T024 calibration: gap midpoint of
max(out-of-domain) 0.775 / min(in-domain) 0.849 — see src/eval/calibrate.py
header). 002-T024 run of src/eval/calibrate.py calibrates each pack on its
own eval set and replaces these provisional values, recording each value's
rationale here.
"""

from __future__ import annotations

from src.qa.abstain import DEFAULT_THRESHOLD

PACK_THRESHOLD_DEFAULT = DEFAULT_THRESHOLD

# Provisional per-pack values — identical until 002-T024 per-pack calibration.
PACK_THRESHOLDS: dict[str, float] = {
    "c": PACK_THRESHOLD_DEFAULT,
    "cpp": PACK_THRESHOLD_DEFAULT,
    "python": PACK_THRESHOLD_DEFAULT,
    "java": PACK_THRESHOLD_DEFAULT,
}


def threshold_for(language_id: str) -> float:
    """Return the pack's abstention threshold (provisional default if unknown)."""
    return PACK_THRESHOLDS.get(language_id, PACK_THRESHOLD_DEFAULT)
