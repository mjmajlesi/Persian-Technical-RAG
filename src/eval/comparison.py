"""Per-language, question-paired bootstrap; never tune v2 gates or pool packs."""

from __future__ import annotations

import math
import random
import hashlib
import json
from collections import Counter
from itertools import combinations
from pathlib import Path

from src.eval.validate_set import ensure_unique_questions


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
    slices = {"mixed_qtype": [i for i, item in enumerate(items) if item["qtype"] == "mixed"]}
    slices.update({f"evidence_language:{lang}": [i for i, item in enumerate(items)
                                                if item.get("evidence_language") == lang]
                   for lang in sorted({item.get("evidence_language") for item in items
                                       if item.get("evidence_language")})})
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
    slice_boot = {model: {name: {metric: [] for metric in METRICS} for name in slices}
                  for model in runs}
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
            for name, positions in slices.items():
                selected = [i for i in sample if i in positions]
                for metric in METRICS:
                    value = mean(values[model][metric], selected)
                    if value is not None:
                        slice_boot[model][name][metric].append(value)
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
        summary["slices"] = {}
        for name, positions in slices.items():
            summary["slices"][name] = {}
            for metric in METRICS:
                column = values[model][metric]
                present = [column[i] for i in positions if column[i] is not None]
                entry = {"value": mean(column, positions),
                         "ci": _interval(slice_boot[model][name][metric], 0.95),
                         "denominator": len(present)}
                if metric == "citation_precision":
                    entry["answer_count"] = len(present)
                    entry["citation_count"] = sum(
                        len(rows_by_model[model][1][ids[i]]["cited_ids"])
                        for i in positions if column[i] is not None)
                    entry["correct_citations"] = sum(
                        cid in items[i]["expected_source_ids"]
                        for i in positions if column[i] is not None
                        for cid in rows_by_model[model][1][ids[i]]["cited_ids"])
                else:
                    entry["numerator"] = sum(present) if present else None
                summary["slices"][name][metric] = entry
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


LANGUAGES = ("c", "cpp", "python", "java")
MODELS = ("e5-large", "e5-base", "bge-m3")


def _read_report(root: Path, language: str, model: str, mode: str) -> tuple[dict, dict]:
    folder = root / language / "reports" / "v2" / model
    paths = list(folder.glob(f"*-{language}-v2-{mode}.json"))
    if len(paths) != 1:
        raise ValueError(f"expected one official {mode} report for {language}/{model}")
    path = paths[0]
    raw = path.read_bytes()
    report = json.loads(raw.decode("utf-8"))
    return report, {"path": path.as_posix(), "sha256": hashlib.sha256(raw).hexdigest(),
                    "status": report["status"], "error_count": report["error_count"]}


def build_official_comparison(root: Path, language: str, *,
                              seed: int = 20261022, replications: int = 10_000) -> dict:
    """Reproduce one pack's official evidence from the frozen v2 runs only."""
    if language not in LANGUAGES:
        raise ValueError("unknown comparison language")
    set_path = root / language / f"eval-set.{language}.v2.json"
    raw = set_path.read_bytes()
    spec = json.loads(raw.decode("utf-8"))
    if spec["version"] != f"{language}-v2" or spec["pack_id"] != language:
        raise ValueError("v2 set identity mismatch")
    set_hash = hashlib.sha256(raw).hexdigest()
    chunks_path = root.parent / "index" / language / "chunks.jsonl"
    chunks_bytes = chunks_path.read_bytes()
    pack_ids = {json.loads(line)["chunk_id"] for line in chunks_bytes.decode("utf-8").splitlines()
                if line.strip()}
    chunk_hash = hashlib.sha256(chunks_bytes).hexdigest()
    items = spec["items"]
    ensure_unique_questions(items)
    by_id = {item["item_id"]: item for item in items}
    if len(by_id) != len(items):
        raise ValueError("duplicate v2 item ID")
    runs, sources, per_item = {}, {}, {}
    generators = set()
    for model in MODELS:
        retrieval, retrieval_source = _read_report(root, language, model, "retrieval-only")
        e2e, e2e_source = _read_report(root, language, model, "end-to-end")
        for mode, report in (("retrieval-only", retrieval), ("end-to-end", e2e)):
            if (report["mode"] != mode or report["model_key"] != model or
                    report["language_id"] != language or
                    report["eval_set_version"] != spec["version"] or
                    report["v2_sha256"] != set_hash or
                    report["snapshot"] != spec["snapshot"] or
                    report["calibration"]["model_key"] != model or
                    report["calibration"]["revision_sha"] != report["model"]["revision_sha"]):
                raise ValueError(f"report provenance mismatch: {language}/{model}/{mode}")
        calibration_path = root / "model-comparison" / "calibration" / f"{model}.json"
        frozen = json.loads(calibration_path.read_text(encoding="utf-8"))
        if retrieval["calibration"] != frozen or e2e["calibration"] != frozen:
            raise ValueError(f"pooled-v1 calibration mismatch: {language}/{model}")
        if (retrieval["status"] != "complete" or retrieval["error_count"] or
                retrieval["retrieval"]["status"] != "complete" or
                retrieval["retrieval"]["error_count"] or
                e2e["retrieval"]["status"] != "complete" or
                e2e["retrieval"]["error_count"] or
                retrieval["retrieval"]["rows"] != e2e["retrieval"]["rows"] or
                retrieval["index"] != e2e["index"] or
                retrieval["model"] != e2e["model"] or
                retrieval["end_to_end"]["status"] != "not_run"):
            raise ValueError(f"retrieval-only/E2E replay mismatch: {language}/{model}")
        if retrieval["index"]["chunk_sha256"] != chunk_hash:
            raise ValueError(f"canonical pack chunk hash mismatch: {language}/{model}")
        rows = _by_id(retrieval["retrieval"]["rows"], set(by_id), "retrieval")
        for item_id, row in rows.items():
            item = by_id[item_id]
            if (row["qtype"] != item["qtype"] or
                    row["hit"] != bool(set(row["top5_ids"][:5]) &
                                       set(item["expected_source_ids"])) or
                    row["fixed_gate_abstain"] !=
                    (row["top1_score"] < frozen["threshold"])):
                raise ValueError(f"per-item retrieval score mismatch: {item_id}/{model}")
        complete = (e2e["status"] == e2e["end_to_end"]["status"] == "complete" and
                    e2e["error_count"] == e2e["end_to_end"]["error_count"] == 0)
        answers = _by_id(e2e["end_to_end"]["rows"], set(by_id), "end-to-end") if complete else {}
        if complete:
            if (not e2e["end_to_end"].get("expected_response_model") or
                    not any(row.get("llm_metadata") for row in answers.values())):
                raise ValueError(f"unverified E2E model identity: {language}/{model}")
            for item_id, answer in answers.items():
                meta = answer.get("llm_metadata")
                if (answer["response_type"] not in ("answer", "abstain") or
                        (answer["response_type"] == "abstain" and answer["cited_ids"]) or
                        (answer["response_type"] == "answer" and not answer["cited_ids"]) or
                        (meta is None and not (rows[item_id]["fixed_gate_abstain"] and
                                               answer["response_type"] == "abstain")) or
                        (meta is not None and (not meta.get("request_timestamp") or
                                               not meta.get("prompt_sha256") or
                                               not meta.get("provider") or
                                               meta.get("temperature") != 0 or
                                               meta.get("model") != e2e["end_to_end"]["expected_response_model"]))):
                    raise ValueError(f"unverified E2E row: {item_id}/{model}")
                if any(cid not in pack_ids or cid not in rows[item_id]["top5_ids"][:5]
                       for cid in answer["cited_ids"]):
                    raise ValueError(f"citation outside selected pack or row Top-5: {item_id}/{model}")
                if meta is not None:
                    generators.add((meta["provider"], meta["model"]))
        elif e2e["end_to_end"]["status"] != "incomplete" or "rows" in e2e["end_to_end"]:
            raise ValueError(f"partial E2E rows cannot enter official evidence: {language}/{model}")
        runs[model] = {**retrieval, "status": e2e["status"],
                       "end_to_end": e2e["end_to_end"]}
        sources[model] = {"retrieval_only": retrieval_source, "end_to_end": e2e_source,
                          "model": retrieval["model"], "index": retrieval["index"],
                          "locked_threshold": frozen["threshold"],
                          "calibration_sha256": hashlib.sha256(calibration_path.read_bytes()).hexdigest(),
                          "e2e_reasons": e2e["end_to_end"].get("reasons", [])}
        per_item[model] = [{"item_id": item["item_id"], "qtype": item["qtype"],
                            "evidence_language": item["evidence_language"],
                            "expected_source_ids": item["expected_source_ids"],
                            "top5_ids": rows[item["item_id"]]["top5_ids"],
                            "top1_score": rows[item["item_id"]]["top1_score"],
                            "hit": rows[item["item_id"]]["hit"],
                            "fixed_gate_abstain": rows[item["item_id"]]["fixed_gate_abstain"],
                            "response_type": answers[item["item_id"]]["response_type"] if complete else None,
                            "cited_ids": answers[item["item_id"]]["cited_ids"] if complete else None,
                            "correct_citations": sum(cid in item["expected_source_ids"]
                                                     for cid in answers[item["item_id"]]["cited_ids"])
                            if complete else None} for item in items]
    if len(generators) > 1:
        raise ValueError(f"E2E generator identity mismatch in comparison: {language}")
    result = compare_language(runs, items, seed=seed, replications=replications)
    return {**result, "set_version": spec["version"],
            "set": {"path": set_path.as_posix(), "sha256": set_hash,
                    "n_items": len(items)}, "source_reports": sources,
            "per_item": per_item,
            "limitations": ["Seven out-of-corpus questions per language limit abstention inference.",
                            "The pooled-v1 gates are frozen; v2 sweep optima are descriptive only.",
                            "The E5 baseline saw v1; a stable API model ID cannot prove immutable weights."]}


def comparison_markdown(report: dict) -> str:
    """Human-readable mirror of one language's versioned comparison JSON."""
    def fmt(metric: dict) -> str:
        if metric["value"] is None:
            return "N/A"
        ci = metric["ci"]
        return f"{metric['value']:.3f} [{ci[0]:.3f}, {ci[1]:.3f}]"

    lines = [f"# {report['language_id']} v2 embedding comparison", "",
             f"Set: `{report['set']['path']}` (SHA-256 `{report['set']['sha256']}`; "
             f"n={report['set']['n_items']}). Seed {report['bootstrap_seed']}, "
             f"{report['replications']} paired resamples; 95% metric CIs, "
             f"{report['pair_confidence']:.2%} Bonferroni pair CIs.", "",
             "| Model | Hit@5 /38 (95% CI) | Citation precision (answered; citations) | "
             "Fixed OOC /7 | E2E OOC /7 | Errors retrieval/E2E |",
             "|---|---|---|---|---|---|"]
    for model in MODELS:
        summary = report["models"][model]
        source = report["source_reports"][model]
        hit = summary["hit_at_5"]
        precision = summary["citation_precision"]
        gate = summary["fixed_gate_abstention"]
        e2e = summary["e2e_abstention"]
        lines.append(f"| {model} | {hit['numerator']}/{hit['denominator']} {fmt(hit)} | "
                     f"{precision['correct_citations']}/{precision['citation_count']} "
                     f"({precision['answer_count']} answers) {fmt(precision)} | "
                     f"{gate['numerator']}/{gate['denominator']} {fmt(gate)} | "
                     f"{e2e['numerator']}/{e2e['denominator']} {fmt(e2e)} | "
                     f"{source['retrieval_only']['error_count']}/"
                     f"{source['end_to_end']['error_count']} |")
    lines.extend(["", f"**Decision (this language only): {report['winner_status']}**", "",
                  "Citation precision is a question-level mean over answered rows; "
                  "citation counts are audit denominators, not the mean's denominator.", "",
                  "## Paired model differences (98.33% CIs)", "",
                  "| Pair (first minus second) | Hit@5 | Citation precision | Fixed OOC | E2E OOC |",
                  "|---|---|---|---|---|"])
    for pair, differences in report["paired_differences"].items():
        lines.append("| " + pair.replace("|", " − ") + " | " +
                     " | ".join(fmt(differences[key]) for key in METRICS) + " |")
    lines.extend(["", "## Mixed and evidence-language slices (95% CIs)", "",
                  "| Model / slice (n) | Hit@5 | Citation precision | Fixed OOC | E2E OOC |",
                  "|---|---|---|---|---|"])
    for model in MODELS:
        for name, slice_metrics in report["models"][model]["slices"].items():
            cells = [f"{fmt(slice_metrics[key])} (n={slice_metrics[key]['denominator']})"
                     for key in METRICS]
            lines.append(f"| {model} / {name} | " + " | ".join(cells) + " |")
    lines.extend(["", "## Descriptive v2 threshold sensitivity (not calibration)", "",
                  "| Model | Locked pooled-v1 gate | OOC-positive AUROC (95% CI) | "
                  "Observed v2 best gate (descriptive only) |",
                  "|---|---|---|---|"])
    for model in MODELS:
        sweep = report["models"][model]["sweep"]
        lines.append(f"| {model} | {sweep['locked_threshold']:.6f} | "
                     f"{fmt(sweep['auroc'])} (7 OOC / 38 answerable) | "
                     f"{sweep['observed_best_threshold']['value']:.6f} |")
    lines.extend(["", "## Sources and reproducibility", ""])
    for model in MODELS:
        source = report["source_reports"][model]
        lines.append(f"- {model}: retrieval `{source['retrieval_only']['path']}` "
                     f"(SHA-256 `{source['retrieval_only']['sha256']}`); E2E "
                     f"`{source['end_to_end']['path']}` (SHA-256 "
                     f"`{source['end_to_end']['sha256']}`); revision "
                     f"`{source['model']['revision_sha']}`; "
                     f"calibration SHA-256 `{source['calibration_sha256']}`. "
                     f"E2E status {source['end_to_end']['status']}; "
                     f"reasons: {', '.join(source['e2e_reasons']) or 'none'}.")
    lines.extend(["", "Per-item scores, retrieval IDs, cited IDs, reference IDs and PR points "
                  "are in the companion JSON; no global winner is inferred.", "",
                  "## Limitations", ""])
    lines.extend(f"- {limitation}" for limitation in report["limitations"])
    return "\n".join(lines) + "\n"


def write_comparisons(root: Path = Path("data/eval")) -> list[tuple[Path, Path]]:
    """Validate all four packs before writing any comparison artifacts."""
    reports = {lang: build_official_comparison(root, lang) for lang in LANGUAGES}
    written = []
    for lang, report in reports.items():
        folder = root / lang / "reports" / "v2"
        folder.mkdir(parents=True, exist_ok=True)
        json_path, md_path = folder / "comparison.v2.json", folder / "comparison.v2.md"
        json_path.write_bytes((json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
        md_path.write_bytes(comparison_markdown(report).encode("utf-8"))
        assert json.loads(json_path.read_text(encoding="utf-8")) == report
        assert md_path.read_bytes() == comparison_markdown(report).encode("utf-8")
        written.append((json_path, md_path))
    return written


def exploratory_pool(reports: dict[str, dict], *, seed: int = 20261022,
                     replications: int = 10_000) -> dict:
    """Secondary stratified summary; no cross-pack gate or winner decision."""
    if set(reports) != set(LANGUAGES) or replications <= 0:
        raise ValueError("exploratory pool needs four complete language comparisons")
    columns = {model: {metric: [] for metric in METRICS} for model in MODELS}
    counts = {model: {"answers": 0, "citations": 0, "correct_citations": 0,
                      "retrieval_errors": 0, "e2e_errors": 0} for model in MODELS}
    source_hashes = {}
    incomplete = set()
    for lang in LANGUAGES:
        report = reports[lang]
        if report["language_id"] != lang or report["set_version"] != f"{lang}-v2" or set(
                report["models"]) != set(MODELS) or set(report["per_item"]) != set(MODELS):
            raise ValueError("primary language identity/model mismatch")
        ids = [row["item_id"] for row in report["per_item"][MODELS[0]]]
        if len(ids) != 45 or len(set(ids)) != 45 or Counter(
                row["qtype"] for row in report["per_item"][MODELS[0]]) != {
                "in-corpus": 28, "mixed": 10, "out-of-corpus": 7}:
            raise ValueError("primary language item set mismatch")
        source_hashes[lang] = report["set"]["sha256"]
        for model in MODELS:
            rows = report["per_item"][model]
            if [row["item_id"] for row in rows] != ids:
                raise ValueError("primary question pairing mismatch")
            source = report["source_reports"][model]
            counts[model]["retrieval_errors"] += source["retrieval_only"]["error_count"]
            counts[model]["e2e_errors"] += source["end_to_end"]["error_count"]
            if source["end_to_end"]["status"] != "complete":
                incomplete.add(model)
            if (source["locked_threshold"] != report["models"][model]["sweep"]["locked_threshold"] or
                    (source["end_to_end"]["status"] == "complete") !=
                    (report["models"][model]["e2e_abstention"]["value"] is not None)):
                raise ValueError("locked gate or E2E status mismatch")
            for row in rows:
                out = row["qtype"] == "out-of-corpus"
                cited = row["cited_ids"]
                if (row["hit"] != bool(set(row["top5_ids"][:5]) &
                                        set(row["expected_source_ids"])) or
                        row["fixed_gate_abstain"] !=
                        (row["top1_score"] < source["locked_threshold"])):
                    raise ValueError("pooled input would change a fixed-gate or hit result")
                if cited is not None and row["correct_citations"] != sum(
                        cid in row["expected_source_ids"] for cid in cited):
                    raise ValueError("pooled citation input mismatch")
                columns[model]["hit_at_5"].append(None if out else int(row["hit"]))
                columns[model]["fixed_gate_abstention"].append(
                    int(row["fixed_gate_abstain"]) if out else None)
                columns[model]["e2e_abstention"].append(
                    int(row["response_type"] == "abstain" and cited == [])
                    if out and cited is not None else None)
                precision = None
                if row["response_type"] == "answer":
                    if not cited:
                        raise ValueError("answer without citation denominator")
                    counts[model]["answers"] += 1
                    counts[model]["citations"] += len(cited)
                    counts[model]["correct_citations"] += row["correct_citations"]
                    precision = row["correct_citations"] / len(cited)
                columns[model]["citation_precision"].append(precision)

    # Never form a four-language E2E estimate from fewer than four complete runs.
    for model in incomplete:
        for metric in ("citation_precision", "e2e_abstention"):
            columns[model][metric] = [None] * 180
        for key in ("answers", "citations", "correct_citations"):
            counts[model][key] = 0

    def estimate(column: list[float | None], indices: list[int] | range) -> float | None:
        values = [column[i] for i in indices if column[i] is not None]
        return sum(values) / len(values) if values else None

    boot = {model: {metric: [] for metric in METRICS} for model in MODELS}
    rng = random.Random(seed)
    for _ in range(replications):
        # Resample questions separately per pack, keeping 45 observations per pack.
        sample = [lang_index * 45 + i for lang_index in range(4)
                  for i in rng.choices(range(45), k=45)]
        for model in MODELS:
            for metric in METRICS:
                value = estimate(columns[model][metric], sample)
                if value is not None:
                    boot[model][metric].append(value)
    pooled = {}
    for model in MODELS:
        pooled[model] = {}
        for metric in METRICS:
            column = columns[model][metric]
            present = [value for value in column if value is not None]
            entry = {"value": estimate(column, range(180)),
                     "ci": _interval(boot[model][metric], 0.95),
                     "denominator": len(present)}
            if metric == "citation_precision":
                entry.update(answer_count=counts[model]["answers"],
                             citation_count=counts[model]["citations"],
                             correct_citations=counts[model]["correct_citations"])
            else:
                entry["numerator"] = sum(present) if present else None
            pooled[model][metric] = entry
        pooled[model]["errors"] = {key: counts[model][key]
                                    for key in ("retrieval_errors", "e2e_errors")}
    return {"status": "exploratory-secondary", "languages": list(LANGUAGES),
            "set_sha256": source_hashes, "n_items": 180, "n_answerable": 152,
            "n_out": 28, "seed": seed, "replications": replications,
            "confidence": 0.95, "resampling": "within-language paired questions",
            "models": pooled}
