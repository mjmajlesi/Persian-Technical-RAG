"""Per-pack threshold calibration (002-T024).

Method (per task): fetch each ready pack's 30-item eval set, embed every
question through that pack's own index, and record top-1 cosine of

  - answerable items (qtype in-corpus / mixed) — must ANSWER → score high;
  - out-of-corpus items — must ABSTAIN → score lower.

Threshold rule: midpoint of the separation gap — (max(out) + min(in)) / 2 —
the same gap-midpoint rule feature 001 used. When the two classes overlap
(x.eval outliers), the same formula still yields the recorded value and the
residual overlap is documented in pack_config rationales: out-of-corpus
items that gate-pass fall through to the LLM-insufficient backstop
(CANNOT_ANSWER → abstain).

Measured 2026-10-22 (full tables printed by running this script);
stored thresholds sit inside the gap / at documented overlap points:

  c      max(out)=0.793 (C-O05)   min(in)=0.814 (C-009)   -> 0.803   separable
  cpp    max(out)=0.822 (CPP-O01)  min(in)=0.821 (CPP-019) -> 0.82    overlap 0.001
  java   max(out)=0.790 (JV-O01)   min(in)=0.792 (JV-013)  -> 0.791   separable
  python max(out)=0.797 (PY-O01)   min(in)=0.786 (PY-006)  -> 0.79    overlap 0.011

History (feature 001, 2026-10-07): 12 C probes on the frozen 503-chunk
index -> single provisional 0.81; invalid hereafter (this file no longer
calibrates a single value — pack_config.py holds the per-pack results).
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from src.eval.run import default_set_path
from src.qa.retriever import Retriever

ANSWERABLE_TYPES = ("in-corpus", "mixed")


def probe_pack(pack) -> dict:
    """Top-1 separation analysis for one ready pack on its eval set."""
    spec = json.loads(
        Path(default_set_path(pack.language_id)).read_text(encoding="utf-8")
    )
    retriever = Retriever(pack.index_dir)
    in_rows, out_rows = [], []
    for item in spec["items"]:
        top1 = retriever.retrieve(item["question"], k=1)[0]["score"]
        rows = in_rows if item["qtype"] in ANSWERABLE_TYPES else out_rows
        rows.append((item["item_id"], item["question"], top1))
    max_out = max(s for _, _, s in out_rows)
    min_in = min(s for _, _, s in in_rows)
    threshold = (max_out + min_in) / 2
    return {
        "in_rows": in_rows,
        "out_rows": out_rows,
        "max_out": max_out,
        "min_in": min_in,
        "separable": max_out < min_in,
        "threshold": threshold,
        # items that would flip at the recorded threshold (overlap residue)
        "out_passing": [i for i, _, s in out_rows if s >= threshold],
        "in_abstaining": [i for i, _, s in in_rows if s < threshold],
    }


def main() -> None:
    from src.web.packs import load_packs

    print(f"calibration run {date.today().isoformat()}\n")
    for pack in load_packs():
        if pack.status != "ready":
            continue
        result = probe_pack(pack)
        label = f"{pack.language_id} ({pack.index_dir})"
        print(f"=== {label} ===")
        print(f"  IN (must answer):")
        for item_id, _q, score in sorted(result["in_rows"], key=lambda x: x[2]):
            print(f"    {score:.3f}  {item_id}")
        print(f"  OUT (must abstain):")
        for item_id, _q, score in sorted(result["out_rows"], key=lambda x: -x[2]):
            print(f"    {score:.3f}  {item_id}")
        print(f"  max(out)={result['max_out']:.3f}  min(in)={result['min_in']:.3f}  "
              f"{'separable' if result['separable'] else 'OVERLAPPED'}")
        print(f"  THRESHOLD: {result['threshold']:.4f}")
        if result["out_passing"]:
            print(f"  OOC items above gate (LLM backstop): {result['out_passing']}")
        if result["in_abstaining"]:
            print(f"  answerable items below gate: {result['in_abstaining']}")
        print()


if __name__ == "__main__":
    main()
