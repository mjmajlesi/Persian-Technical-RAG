"""Per-pack threshold calibration (002-T024); pooled-v1 research gate (003-T012).

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

import argparse
import hashlib
import json
import math
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Callable

from src.eval.run import default_set_path
from src.index.model_config import get_model_candidate
from src.qa.retriever import Retriever

ANSWERABLE_TYPES = ("in-corpus", "mixed")
RESEARCH_PACKS = ("c", "cpp", "python", "java")


def _confusion(rows: list[dict], threshold: float) -> dict[str, int]:
    """OOC is positive; scores strictly below the gate predict OOC."""
    counts = {"tp": 0, "fn": 0, "tn": 0, "fp": 0}
    for row in rows:
        predicted_out = row["score"] < threshold
        actual_out = row["qtype"] == "out-of-corpus"
        key = ("tp" if predicted_out else "fn") if actual_out else (
            "fp" if predicted_out else "tn"
        )
        counts[key] += 1
    return counts


def calibrate_pooled_v1(
    model_key: str, set_paths: dict[str, str | Path],
    score_question: Callable[[str, str], float],
) -> dict:
    """Select one gate from exactly four frozen v1 packs, never from v2."""
    candidate = get_model_candidate(model_key)
    if set(set_paths) != set(RESEARCH_PACKS):
        raise ValueError("pooled v1 calibration requires all four packs")

    sources, hashes = {}, {}
    for pack in RESEARCH_PACKS:
        path = Path(set_paths[pack])
        if path.name != f"eval-set.{pack}.v1.json":
            raise ValueError(f"only a versioned v1 set is accepted for {pack}")
        raw = path.read_bytes()
        spec = json.loads(raw.decode("utf-8"))
        items = spec["items"]
        counts = {qtype: sum(item["qtype"] == qtype for item in items)
                  for qtype in (*ANSWERABLE_TYPES, "out-of-corpus")}
        if spec.get("version") != f"{pack}-v1" or len(items) != 30 or counts != {
            "in-corpus": 20, "mixed": 5, "out-of-corpus": 5,
        } or len({item["item_id"] for item in items}) != 30:
            raise ValueError(f"incomplete or invalid 30-item v1 set: {pack}")
        hashes[pack] = hashlib.sha256(raw).hexdigest()
        sources[pack] = items

    rows = []
    for pack in RESEARCH_PACKS:
        for item in sources[pack]:
            score = float(score_question(pack, item["question"]))
            if not math.isfinite(score):
                raise ValueError(f"non-finite retrieval score: {pack}/{item['item_id']}")
            rows.append({"pack_id": pack, "item_id": item["item_id"],
                         "qtype": item["qtype"], "score": score})

    candidates = sorted({row["score"] for row in rows})
    candidates.append(math.nextafter(candidates[-1], math.inf))
    best = None
    for threshold in candidates:
        counts = _confusion(rows, threshold)
        accuracy = (counts["tp"] / 20 + counts["tn"] / 100) / 2
        if best is None or (accuracy, threshold) > (best[0], best[1]):
            best = (accuracy, threshold)
    balanced_accuracy, threshold = best
    return {
        "model_key": model_key, "revision_sha": candidate.revision_sha,
        "method": "pooled-v1-max-balanced-accuracy; tie=higher; ooc=score<threshold",
        "n_answerable": 100, "n_out": 20, "v1_hashes": hashes,
        "threshold": threshold, "balanced_accuracy": balanced_accuracy,
        "pooled_confusion": _confusion(rows, threshold),
        "per_language_confusion": {
            pack: _confusion([row for row in rows if row["pack_id"] == pack], threshold)
            for pack in RESEARCH_PACKS
        },
        "score_rows": rows,
    }


def _run_pooled(model_key: str) -> None:
    retrievers = {
        pack: Retriever(f"data/research/embedding-compare/{model_key}/{pack}",
                        model_key=model_key, pack_id=pack)
        for pack in RESEARCH_PACKS
    }
    paths = {pack: Path(default_set_path(pack)) for pack in RESEARCH_PACKS}
    record = calibrate_pooled_v1(
        model_key, paths,
        lambda pack, question: retrievers[pack].retrieve(question, k=1)[0]["score"],
    )
    target = Path("data/eval/model-comparison/calibration") / f"{model_key}.json"
    if target.exists():
        saved = json.loads(target.read_text(encoding="utf-8"))
        for field in ("revision_sha", "v1_hashes", "threshold", "method"):
            if record[field] != saved.get(field):
                raise ValueError(f"locked calibration {field} changed: {target}")
        print(f"unchanged locked research gate: {target}")
    else:
        record["locked_at"] = datetime.now(timezone.utc).isoformat()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8")
        assert json.loads(target.read_text(encoding="utf-8")) == record
    print(f"model={model_key} pooled-v1 threshold={record['threshold']:.6f} "
          f"balanced_accuracy={record['balanced_accuracy']:.4f} "
          f"n={record['n_answerable']}+{record['n_out']}")
    for pack, confusion in record["per_language_confusion"].items():
        print(f"  {pack}: {confusion}")


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


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Calibrate operational or research gates")
    parser.add_argument("--model", default=None)
    parser.add_argument("--pooled-v1", action="store_true")
    args = parser.parse_args(argv)
    if args.pooled_v1:
        if args.model is None:
            parser.error("--pooled-v1 requires --model")
        _run_pooled(args.model)
        return
    if args.model is not None:
        parser.error("--model requires --pooled-v1")
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
