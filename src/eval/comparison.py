"""Per-language, question-paired bootstrap; never tune v2 gates or pool packs."""

from __future__ import annotations

import math
import random
from collections import Counter
from itertools import combinations


METRICS = ("hit_at_5", "citation_precision", "fixed_gate_abstention",
           "e2e_abstention")


def _interval(values: list[float], confidence: float) -> list[float] | None:
    if not values:
        return None
    ordered = sorted(values)

    def percentile(q: float) -> float:
        position = (len(ordered) - 1) * q
        lower = math.floor(position)
        fraction = position - lower
        return ordered[lower] * (1 - fraction) + ordered[math.ceil(position)] * fraction

    tail = (1 - confidence) / 2
    return [percentile(tail), percentile(1 - tail)]


def _by_id(rows: list[dict], ids: set[str], label: str) -> dict[str, dict]:
    keyed = {row["item_id"]: row for row in rows}
    if len(rows) != len(ids) or set(keyed) != ids:
        raise ValueError(f"{label} item IDs do not match the benchmark")
    return keyed


def compare_language(runs: dict[str, dict], items: list[dict], *,
                     seed: int = 20261022, replications: int = 10_000) -> dict:
    """Compare three complete retrieval runs; missing E2E remains N/A."""
    if len(runs) != 3 or replications <= 0:
        raise ValueError("comparison requires three models and positive replications")
    ids = [item["item_id"] for item in items]
    qtypes = Counter(item["qtype"] for item in items)
    if len(ids) != len(set(ids)) or qtypes != {
        "in-corpus": 28, "mixed": 10, "out-of-corpus": 7,
    }:
        raise ValueError("comparison requires 45 distinct 28/10/7 benchmark items")
    item_ids = set(ids)
    language = next(iter(runs.values()))["language_id"]
    rows_by_model = {}
    fingerprints = []
    chunk_hashes = []
    for model, run in runs.items():
        if run["model_key"] != model or run["language_id"] != language:
            raise ValueError("comparison model/language mismatch")
        retrieval = run["retrieval"]
        if retrieval["status"] != "complete" or retrieval["error_count"]:
            raise ValueError("comparison requires complete retrieval")
        retrieved = _by_id(retrieval["rows"], item_ids, "retrieval")
        for item in items:
            if retrieved[item["item_id"]]["qtype"] != item["qtype"]:
                raise ValueError("retrieval item type mismatch")
        fingerprints.append(run.get("v2_sha256"))
        chunk_hashes.append(run.get("index", {}).get("chunk_sha256"))
        e2e = run["end_to_end"]
        complete_e2e = (run["status"] == "complete" and
                        e2e["status"] == "complete" and not e2e["error_count"])
        answers = _by_id(e2e["rows"], item_ids, "end-to-end") if complete_e2e else {}
        if run.get("n_items") is not None and run["n_items"] != len(ids):
            raise ValueError("reported item denominator mismatch")
        if complete_e2e and e2e.get("answer_count") is not None and e2e["answer_count"] != sum(
                row["response_type"] == "answer" for row in answers.values()):
            raise ValueError("reported answer count mismatch")
        rows_by_model[model] = (retrieved, answers)
    for hashes in (fingerprints, chunk_hashes):
        if any(hashes) and (not all(hashes) or len(set(hashes)) != 1):
            raise ValueError("v2 item set or canonical chunk hash mismatch")

    values = {}
    counts = {}
    for model, (retrieved, answers) in rows_by_model.items():
        columns = {name: [] for name in METRICS}
        answered = cited = correct = 0
        for item in items:
            item_id = item["item_id"]
            out = item["qtype"] == "out-of-corpus"
            row = retrieved[item_id]
            response = answers.get(item_id)
            columns["hit_at_5"].append(None if out else int(row["hit"]))
            columns["fixed_gate_abstention"].append(int(row["fixed_gate_abstain"]) if out else None)
            columns["e2e_abstention"].append(
                int(response["response_type"] == "abstain" and not response["cited_ids"])
                if out and response else None)
            precision = None
            if response:
                if response["response_type"] not in ("answer", "abstain"):
                    raise ValueError("end-to-end response is not complete")
                if response["response_type"] == "answer":
                    citations = response["cited_ids"]
                    if not citations:
                        raise ValueError("answer has no citation denominator")
                    good = sum(cid in item["expected_source_ids"] for cid in citations)
                    precision = good / len(citations)
                    answered += 1
                    cited += len(citations)
                    correct += good
            columns["citation_precision"].append(precision)
        values[model] = columns
        counts[model] = (answered, cited, correct)

    def mean(column: list[float | None], sample: list[int] | range) -> float | None:
        selected = [column[i] for i in sample if column[i] is not None]
        return sum(selected) / len(selected) if selected else None

    pairs = list(combinations(runs, 2))
    pair_confidence = 1 - 0.05 / len(pairs)
    boot = {model: {metric: [] for metric in METRICS} for model in runs}
    differences = {f"{a}|{b}": {metric: [] for metric in METRICS} for a, b in pairs}
    rng = random.Random(seed)
    for _ in range(replications):
        sample = rng.choices(range(len(ids)), k=len(ids))
        estimates = {model: {metric: mean(values[model][metric], sample) for metric in METRICS}
                     for model in runs}
        for model in runs:
            for metric, value in estimates[model].items():
                if value is not None:
                    boot[model][metric].append(value)
        for a, b in pairs:
            for metric in METRICS:
                left, right = estimates[a][metric], estimates[b][metric]
                if left is not None and right is not None:
                    differences[f"{a}|{b}"][metric].append(left - right)

    metrics = {}
    for model in runs:
        summary = {}
        for metric in METRICS:
            column = values[model][metric]
            present = [v for v in column if v is not None]
            summary[metric] = {"value": mean(column, range(len(ids))),
                               "ci": _interval(boot[model][metric], 0.95)}
            if metric == "citation_precision":
                answer_count, citation_count, correct_count = counts[model]
                summary[metric].update(answer_count=answer_count, citation_count=citation_count,
                                       correct_citations=correct_count)
            else:
                summary[metric].update(numerator=sum(present) if present else None,
                                       denominator=len(present))
        metrics[model] = summary
        threshold = runs[model].get("calibration", {}).get("threshold")
        if threshold is not None:
            metrics[model]["sweep"] = threshold_sweep(
                [rows_by_model[model][0][item_id] for item_id in ids],
                locked_threshold=threshold, seed=seed, replications=replications)
    paired = {}
    for a, b in pairs:
        paired[f"{a}|{b}"] = {}
        for metric in METRICS:
            left, right = metrics[a][metric]["value"], metrics[b][metric]["value"]
            paired[f"{a}|{b}"][metric] = {
                "value": left - right if left is not None and right is not None else None,
                "ci": _interval(differences[f"{a}|{b}"][metric], pair_confidence)
                if left is not None and right is not None else None,
            }

    winner = "inconclusive"
    for candidate in runs:
        valid = True
        for alternative in runs:
            if candidate == alternative:
                continue
            a, b = ((candidate, alternative) if (candidate, alternative) in pairs
                    else (alternative, candidate))
            direction = 1 if a == candidate else -1
            pair = paired[f"{a}|{b}"]
            hit = pair["hit_at_5"]["ci"]
            if hit is None or (hit[0] if direction == 1 else -hit[1]) <= 0:
                valid = False
                break
            for metric in METRICS[1:]:
                ci = pair[metric]["ci"]
                if ci is None or (ci[1] if direction == 1 else -ci[0]) < 0:
                    valid = False
                    break
            if not valid:
                break
        if valid:
            winner = candidate
            break
    return {"language_id": language, "bootstrap_seed": seed, "replications": replications,
            "confidence": 0.95, "pair_confidence": pair_confidence,
            "models": metrics, "paired_differences": paired, "winner_status": winner}


def threshold_sweep(rows: list[dict], *, locked_threshold: float,
                    seed: int = 20261022, replications: int = 10_000) -> dict:
    """Describe v2 scores; never select or persist a replacement for the v1 gate."""
    if not math.isfinite(locked_threshold) or replications <= 0:
        raise ValueError("finite locked threshold and positive replications required")
    ids = [row["item_id"] for row in rows]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate sweep item ID")
    scores = []
    for row in rows:
        if row["qtype"] not in ("in-corpus", "mixed", "out-of-corpus"):
            raise ValueError("invalid sweep qtype")
        score = row["top1_score"]
        if not math.isfinite(score):
            raise ValueError("non-finite sweep score")
        scores.append((row["qtype"] == "out-of-corpus", score))
    positives = [score for out, score in scores if out]
    negatives = [score for out, score in scores if not out]
    n_out, n_answerable = len(positives), len(negatives)

    def auroc(pos: list[float], neg: list[float]) -> float:
        # Low similarity means OOC; identical scores count as half a win.
        return sum(1 if out < answer else 0.5 if out == answer else 0
                   for out in pos for answer in neg) / (len(pos) * len(neg))

    auc = {"value": None, "ci": None}
    pr = None
    best = {"status": "descriptive-only", "value": None, "balanced_accuracy": None}
    if n_out and n_answerable:
        auc["value"] = auroc(positives, negatives)
        rng = random.Random(seed)
        samples = []
        for _ in range(replications):
            draw = rng.choices(scores, k=len(scores))
            pos = [score for out, score in draw if out]
            neg = [score for out, score in draw if not out]
            if pos and neg:  # class-absent resamples cannot define AUROC
                samples.append(auroc(pos, neg))
        auc["ci"] = _interval(samples, 0.95)

        ordered = sorted(scores, key=lambda pair: pair[1])
        pr = [{"threshold": ordered[0][1], "tp": 0, "fp": 0,
               "precision": 1.0, "recall": 0.0}]
        best_accuracy, best_threshold = (0.5, ordered[0][1])
        tp = fp = 0
        for score in sorted(set(value for _, value in scores)):
            group = [out for out, value in ordered if value == score]
            tp += sum(group)
            fp += len(group) - sum(group)
            threshold = math.nextafter(score, math.inf)  # strict score < threshold
            pr.append({"threshold": threshold, "tp": tp, "fp": fp,
                       "precision": tp / (tp + fp), "recall": tp / n_out})
            balanced = (tp / n_out + (n_answerable - fp) / n_answerable) / 2
            if (balanced, threshold) > (best_accuracy, best_threshold):
                best_accuracy, best_threshold = balanced, threshold
        best.update(value=best_threshold, balanced_accuracy=best_accuracy)

    locked_tp = sum(out and score < locked_threshold for out, score in scores)
    locked_fp = sum(not out and score < locked_threshold for out, score in scores)
    return {"status": "descriptive-only", "positive_class": "out-of-corpus",
            "seed": seed, "replications": replications, "n_out": n_out,
            "n_answerable": n_answerable, "locked_threshold": locked_threshold,
            "locked_gate": {"tp": locked_tp, "fn": n_out - locked_tp,
                            "tn": n_answerable - locked_fp, "fp": locked_fp},
            "auroc": auc, "pr_curve": pr, "observed_best_threshold": best}
