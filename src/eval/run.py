"""Eval runner (T031): score the versioned set end-to-end.

For each item it measures retrieval (hit@5 vs expected ids) and, through the
REAL endpoint logic (src.web.app.ask: retrieve -> gate -> compose), the
response (answer citations / abstention purity). Writes a JSON report plus a
Markdown summary under data/eval/reports/.

Cost note: answerable items each spend one LLM call; gated out-of-corpus
items spend none.
"""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime
from pathlib import Path

from src.eval.scoring import (
    abstention_correct,
    citation_precision,
    hit_rate_at_5,
    mixed_slice_scores,
)
from src.qa.retriever import Retriever
from src.web.app import AskRequest, ask


def run_eval(set_path: str, index_dir: str, report_dir: str, top_k: int = 5) -> dict:
    spec = json.loads(Path(set_path).read_text(encoding="utf-8"))
    items = spec["items"]
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
            response = ask(AskRequest(question=question, top_k=top_k))
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
            "precision": precision,
            "coverage": bool(set(cited) & set(expected)) if cited else False,
            "abstention_ok": abstention_correct(item["qtype"], response)
            if item["qtype"] == "out-of-corpus" else None,
        })

    answerable = [r for r in rows if r["qtype"] in ("in-corpus", "mixed")]
    answered = [r for r in rows if r["response_type"] == "answer"]
    out_items = [r for r in rows if r["qtype"] == "out-of-corpus"]
    mixed_rows = [
        {"qtype": "mixed", "hit": r["hit"], "precision": r["precision"] or 0.0}
        for r in rows if r["qtype"] == "mixed"
    ]
    report = {
        "eval_set_version": spec["version"],
        "index_snapshot": date.today().isoformat(),
        "n_items": len(rows),
        "hit_rate_at_5": sum(1 for r in answerable if r["hit"]) / len(answerable),
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
        "per_item_rows": rows,
    }
    return report


def write_reports(report: dict, report_dir: str) -> tuple[str, str]:
    out_dir = Path(report_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    # Timestamped to the minute so same-day re-runs never clobber evidence.
    stamp = (datetime.now().strftime("%Y-%m-%d-%H%M")
             + f"-{report['eval_set_version']}")
    json_path = out_dir / f"{stamp}.json"
    md_path = out_dir / f"{stamp}.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2),
                         encoding="utf-8")
    lines = [
        f"# Eval Report {stamp}",
        "",
        f"- Items: {report['n_items']}",
        f"- Hit-rate@5 (answerable): {report['hit_rate_at_5']:.3f}",
        f"- Citation precision (answered): {report['citation_precision']:.3f}",
        f"- Citation coverage (answered): {report['citation_coverage']:.3f}",
        f"- Abstention correct: {report['abstention_correct']}",
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
    parser.add_argument("--set", default="data/eval/eval-set.v1.json")
    parser.add_argument("--index-dir", default="data/index")
    parser.add_argument("--report-dir", default="data/eval/reports")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args(argv)
    report = run_eval(args.set, args.index_dir, args.report_dir, args.top_k)
    json_path, md_path = write_reports(report, args.report_dir)
    print(f"hit_rate_at_5={report['hit_rate_at_5']:.3f} "
          f"precision={report['citation_precision']:.3f} "
          f"coverage={report['citation_coverage']:.3f} "
          f"abstention={report['abstention_correct']}")
    print(f"reports: {json_path} {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
