"""Eval runner (T031): score the versioned set end-to-end.

For each item it measures retrieval (hit@5 vs expected ids) and, through the
REAL endpoint logic (src.web.app.ask: retrieve -> gate -> compose), the
response (answer citations / abstention purity). Writes a JSON report plus a
Markdown summary under data/eval/reports/.

002-T010: `--lang <pack>` scores ONE pack against its own set and writes
both reports under data/eval/<lang>/reports/ (no blended headline figure);
the report carries language_id. Default set/index/report paths resolve
per pack. Until T020 authors data/eval/c/eval-set.c.v1.json, a `--lang c`
run falls back to the 001 flat set data/eval/eval-set.v1.json (same items),
so the figures remain directly comparable.

Cost note: answerable items each spend one LLM call; gated out-of-corpus
items spend none.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import date, datetime
from pathlib import Path

from src.eval.scoring import (
    abstention_correct,
    citation_precision,
    contamination_slice_scores,
    hit_rate_at_5,
    mixed_slice_scores,
)
from src.index.model_config import get_model_candidate
from src.qa.abstain import should_abstain
from src.qa.provider import ProviderError, load_dotenv
from src.qa.retriever import Retriever
from src.web import app as web
from src.web.app import AskRequest, ask
from src.web.packs import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES


def default_set_path(lang: str) -> str:
    """Resolve the pack's eval-set path (001 flat fallback for C pre-T020)."""
    per_pack = f"data/eval/{lang}/eval-set.{lang}.v1.json"
    if Path(per_pack).is_file():
        return per_pack
    if lang == DEFAULT_LANGUAGE:
        return "data/eval/eval-set.v1.json"
    raise SystemExit(f"eval set not found for language: {lang}")


def run_eval(set_path: str, index_dir: str, report_dir: str, top_k: int = 5,
             language: str = DEFAULT_LANGUAGE,
             contamination_set_path: str | None = None, *,
             model_key: str | None = None, mode: str = "end-to-end") -> dict:
    if model_key is not None:
        return _run_research_eval(set_path, index_dir, top_k, language, model_key, mode)
    if mode != "end-to-end":
        raise ValueError("retrieval-only requires --model")
    spec = json.loads(Path(set_path).read_text(encoding="utf-8"))
    items = list(spec["items"])
    contamination_version = None
    if contamination_set_path:
        contamination = json.loads(
            Path(contamination_set_path).read_text(encoding="utf-8")
        )
        contamination_version = contamination["version"]
        items.extend(item for item in contamination["items"]
                     if item["language_id"] == language)
    retriever = Retriever(index_dir)
    index_ids = set(retriever._by_id)

    rows = []
    for item in items:
        question = item["question"]
        expected = item.get("expected_source_ids", [])
        hits = retriever.retrieve(question, k=top_k)
        retrieved = [h["chunk_id"] for h in hits]
        hit = hit_rate_at_5(expected, retrieved)
        try:
            response = ask(AskRequest(question=question, top_k=top_k,
                                      language=language))
        except Exception as exc:  # noqa: BLE001 - recorded, not fatal
            response = {"type": "error", "citations": [], "error": str(exc)[:200]}
        cited = [c["chunk_id"] for c in response.get("citations", [])]
        precision = (
            citation_precision(cited, index_ids, expected)
            if response.get("type") == "answer"
            else None
        )
        rows.append({
            "item_id": item["item_id"],
            "qtype": item["qtype"],
            "top1_score": round(hits[0]["score"], 3),
            "hit": hit,
            "response_type": response.get("type"),
            "error": response.get("error"),
            "precision": precision,
            "coverage": bool(set(cited) & set(expected)) if cited else False,
            "abstention_ok": abstention_correct(item["qtype"], response)
            if item["qtype"] in ("out-of-corpus", "contamination")
            else None,
        })

    answerable = [r for r in rows if r["qtype"] in ("in-corpus", "mixed")]
    answered = [r for r in answerable if r["response_type"] == "answer"]
    out_items = [r for r in rows if r["qtype"] == "out-of-corpus"]
    mixed_rows = [
        {"qtype": "mixed", "hit": r["hit"], "precision": r["precision"] or 0.0}
        for r in rows if r["qtype"] == "mixed"
    ]
    report = {
        "language_id": language,
        "eval_set_version": spec["version"],
        "contamination_set_version": contamination_version,
        "index_snapshot": date.today().isoformat(),
        "n_items": len(rows),
        "error_count": sum(r["response_type"] == "error" for r in rows),
        "hit_rate_at_5": (
            sum(1 for r in answerable if r["hit"]) / len(answerable)
            if answerable else 0.0
        ),
        "citation_precision": (
            sum(r["precision"] for r in answered) / len(answered)
            if answered else 0.0
        ),
        "citation_coverage": (
            sum(1 for r in answered if r["coverage"]) / len(answered)
            if answered else 0.0
        ),
        "abstention_correct": (
            f"{sum(1 for r in out_items if r['abstention_ok'])}/{len(out_items)}"
        ),
        "mixed_slice": mixed_slice_scores(mixed_rows),
        "contamination_slice": contamination_slice_scores(rows),
        "per_item_rows": rows,
    }
    return report


def _run_research_eval(set_path: str, index_dir: str, top_k: int,
                       language: str, model_key: str, mode: str) -> dict:
    if mode not in ("retrieval-only", "end-to-end"):
        raise ValueError("unknown research evaluation mode")
    if top_k != 5:
        raise ValueError("research hit@5 requires top_k=5")
    candidate = get_model_candidate(model_key)
    calibration = json.loads((Path("data/eval/model-comparison/calibration") /
                              f"{model_key}.json").read_text(encoding="utf-8"))
    if calibration["model_key"] != model_key or calibration["revision_sha"] != candidate.revision_sha:
        raise ValueError("research calibration model/revision mismatch")
    for pack in SUPPORTED_LANGUAGES:
        v1 = Path(f"data/eval/{pack}/eval-set.{pack}.v1.json")
        if hashlib.sha256(v1.read_bytes()).hexdigest() != calibration["v1_hashes"][pack]:
            raise ValueError(f"locked v1 calibration input changed: {pack}")
    spec = json.loads(Path(set_path).read_text(encoding="utf-8"))
    retriever = Retriever(index_dir, model_key=model_key, pack_id=language)
    threshold = calibration["threshold"]
    if mode == "end-to-end":
        load_dotenv()  # same environment source as ProviderConfig.from_env()
    expected_model = (os.environ.get("LLM_EXPECTED_RESPONSE_MODEL", "").strip()
                      if mode == "end-to-end" else "")
    metadata = []

    class AuditedProvider:
        def generate(self, prompt, context=""):
            result = web.get_provider().generate_with_metadata(
                prompt, context, expected_model_id=expected_model)
            metadata.append({key: result[key] for key in
                             ("provider", "request_timestamp", "model", "temperature")}
                            | {"prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest()})
            return result["text"]

    retrieval_rows, answer_rows = [], []
    retrieval_errors = 0
    e2e_errors = 0
    for item in spec["items"]:
        try:
            hits = retriever.retrieve(item["question"], k=top_k)
            if not hits:
                raise ValueError("empty retrieval")
            ids = [hit["chunk_id"] for hit in hits]
            fixed_abstain = should_abstain(hits[0]["score"], threshold)
            retrieval_rows.append({
                "item_id": item["item_id"], "qtype": item["qtype"],
                "top1_score": hits[0]["score"], "top5_ids": ids,
                "hit": bool(set(ids) & set(item.get("expected_source_ids", []))),
                "fixed_gate_abstain": fixed_abstain,
            })
        except Exception:  # noqa: BLE001 - incomplete retrieval is not a zero score
            retrieval_errors += 1
            continue
        if mode == "retrieval-only":
            continue
        if not expected_model:
            e2e_errors += 1
            answer_rows.append({"item_id": item["item_id"], "response_type": "error",
                                "reason": "expected response model ID not pre-registered"})
            continue
        try:
            previous = len(metadata)
            response = web._ask(AskRequest(question=item["question"], top_k=top_k,
                                           language=language),
                                retriever=retriever, threshold=threshold,
                                provider=AuditedProvider(), retrieved_chunks=hits)
            if response["type"] not in ("answer", "abstain"):
                raise ValueError("unexpected research response type")
            answer_rows.append({"item_id": item["item_id"],
                                "response_type": response["type"],
                                "cited_ids": [c["chunk_id"] for c in
                                              response.get("citations", [])],
                                "llm_metadata": metadata[-1] if len(metadata) > previous else None})
        except Exception as exc:  # noqa: BLE001 - only E2E becomes incomplete
            e2e_errors += 1
            answer_rows.append({"item_id": item["item_id"], "response_type": "error",
                                "reason": ("provider identity/temperature/configuration failure"
                                           if isinstance(exc, ProviderError) else
                                           "end-to-end response failed")})

    retrieval_status = ("complete" if spec["items"] and not retrieval_errors
                        and len(retrieval_rows) == len(spec["items"]) else "incomplete")
    e2e_status = ("not_run" if mode == "retrieval-only" else
                  "complete" if not e2e_errors and retrieval_status == "complete"
                  and metadata else "incomplete")
    reasons = sorted({row["reason"] for row in answer_rows if "reason" in row})
    if mode == "end-to-end" and retrieval_errors:
        reasons.append("retrieval errors prevented complete end-to-end evaluation")
    if mode == "end-to-end" and not metadata:
        reasons.append("no API response model ID verified")
    return {
        "model_key": model_key, "language_id": language, "eval_set_version": spec["version"],
        "mode": mode, "calibration": {"threshold": threshold,
                                      "v1_hashes": calibration["v1_hashes"]},
        "retrieval": {"status": retrieval_status, "error_count": retrieval_errors,
                      "rows": retrieval_rows},
        "end_to_end": {"status": e2e_status, "error_count": e2e_errors,
                       "rows": answer_rows, "reasons": reasons,
                       "expected_response_model": expected_model or None},
        "error_count": retrieval_errors + e2e_errors,
    }


def write_reports(report: dict, report_dir: str) -> tuple[str, str]:
    out_dir = Path(report_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    # Timestamped to the minute so same-day re-runs never clobber evidence.
    stamp = (datetime.now().strftime("%Y-%m-%d-%H%M")
             + f"-{report['eval_set_version']}")
    json_path = out_dir / f"{stamp}.json"
    md_path = out_dir / f"{stamp}.md"
    if "model_key" in report:
        # Partial E2E rows are diagnostics, not official complete-run evidence.
        official = dict(report)
        if report["end_to_end"]["status"] == "incomplete":
            official["end_to_end"] = {key: value for key, value in
                                       report["end_to_end"].items() if key != "rows"}
            (out_dir / f"{stamp}.diagnostics.json").write_text(json.dumps({
                "status": "diagnostics-only", "model_key": report["model_key"],
                "language_id": report["language_id"],
                "end_to_end_rows": report["end_to_end"]["rows"],
            }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        json_path.write_text(json.dumps(official, ensure_ascii=False, indent=2) + "\n",
                             encoding="utf-8")
        md_path.write_text(
            f"# Research eval {stamp}\n\n"
            f"- Model / pack: {report['model_key']} / {report['language_id']}\n"
            f"- Retrieval: {report['retrieval']['status']} "
            f"({len(report['retrieval']['rows'])} rows, "
            f"{report['retrieval']['error_count']} errors)\n"
            f"- End-to-end: {report['end_to_end']['status']} "
            f"({report['end_to_end']['error_count']} errors)\n"
            f"- Reasons: {', '.join(report['end_to_end']['reasons']) or 'none'}\n",
            encoding="utf-8",
        )
        return str(json_path), str(md_path)
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2),
                         encoding="utf-8")
    lines = [
        f"# Eval Report {stamp}",
        "",
        f"- Status: {'INCOMPLETE' if report['error_count'] else 'complete'} "
        f"({report['error_count']} model errors)",
        f"- Items: {report['n_items']}",
        f"- Contamination set: {report['contamination_set_version'] or 'none'}",
        f"- Hit-rate@5 (answerable): {report['hit_rate_at_5']:.3f}",
        f"- Citation precision (answered): {report['citation_precision']:.3f}",
        f"- Citation coverage (answered): {report['citation_coverage']:.3f}",
        f"- Abstention correct: {report['abstention_correct']}",
        f"- Contamination slice: {report['contamination_slice']['correct']}/"
        f"{report['contamination_slice']['n']}",
        f"- Mixed slice: hit {report['mixed_slice']['hit_rate_at_5']:.3f}, "
        f"precision {report['mixed_slice']['citation_precision']:.3f} "
        f"(n={report['mixed_slice']['n']})",
        "",
        "## Per-item rows",
        "",
        "| item | qtype | hit | response | precision | abstention_ok |",
        "|------|-------|-----|----------|-----------|---------------|",
    ]
    for r in report["per_item_rows"]:
        lines.append(
            f"| {r['item_id']} | {r['qtype']} | {r['hit']} | "
            f"{r['response_type']} | {r['precision']} | {r['abstention_ok']} |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(json_path), str(md_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the versioned eval set.")
    parser.add_argument("command", choices=["run"])
    parser.add_argument("--lang", default=DEFAULT_LANGUAGE,
                        choices=SUPPORTED_LANGUAGES,
                        help="pack to score (per-pack set, index, reports)")
    parser.add_argument("--set", default=None,
                        help="defaults to data/eval/<lang>/eval-set.<lang>.v1.json")
    parser.add_argument("--index-dir", default=None,
                        help="defaults to the selected operational/research index")
    parser.add_argument("--report-dir", default=None,
                        help="defaults to the selected operational/research reports")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--model", default=None, help="research embedding model key")
    parser.add_argument("--mode", choices=("retrieval-only", "end-to-end"),
                        default="end-to-end")
    parser.add_argument("--contamination-set",
                        default="data/eval/contamination.v1.json",
                        help="dedicated cross-pack probes, scored separately")
    args = parser.parse_args(argv)
    if args.mode == "retrieval-only" and not args.model:
        parser.error("--mode retrieval-only requires --model")
    if args.model and not args.set:
        parser.error("research runs require --set (pilot or approved v2)")
    set_path = args.set or default_set_path(args.lang)
    index_dir = args.index_dir or (f"data/research/embedding-compare/{args.model}/{args.lang}"
                                   if args.model else f"data/index/{args.lang}")
    report_dir = args.report_dir or (f"data/eval/{args.lang}/reports/v2/{args.model}"
                                     if args.model else f"data/eval/{args.lang}/reports")
    if args.model:
        report = run_eval(set_path, index_dir, report_dir, args.top_k, args.lang,
                          None, model_key=args.model, mode=args.mode)
    else:
        report = run_eval(set_path, index_dir, report_dir, args.top_k, args.lang,
                          args.contamination_set)
    json_path, md_path = write_reports(report, report_dir)
    if args.model:
        print(f"retrieval={report['retrieval']['status']} "
              f"end-to-end={report['end_to_end']['status']}")
        print(f"reports: {json_path} {md_path}")
        return 0 if (report["retrieval"]["status"] == "complete" and
                     report["end_to_end"]["status"] in ("complete", "not_run")) else 1
    print(f"hit_rate_at_5={report['hit_rate_at_5']:.3f} "
          f"precision={report['citation_precision']:.3f} "
          f"coverage={report['citation_coverage']:.3f} "
          f"abstention={report['abstention_correct']}")
    print(f"reports: {json_path} {md_path}")
    return 1 if report["error_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
