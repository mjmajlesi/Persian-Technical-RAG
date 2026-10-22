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
import json
from datetime import date, datetime
from pathlib import Path

from src.eval.scoring import (
    abstention_correct,
    citation_precision,
    contamination_slice_scores,
    hit_rate_at_5,
    mixed_slice_scores,
)
from src.qa.retriever import Retriever
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
             language: str = DEFAULT_LANGUAGE) -> dict:
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
            "precision": precision,
            "coverage": bool(set(cited) & set(expected)) if cited else False,
            "abstention_ok": abstention_correct(item["qtype"], response)
            if item["qtype"] in ("out-of-corpus", "contamination")
            else None,
        })

    answerable = [r for r in rows if r["qtype"] in ("in-corpus", "mixed")]
    answered = [r for r in rows if r["response_type"] == "answer"]
    out_items = [r for r in rows if r["qtype"] == "out-of-corpus"]
    mixed_rows = [
        {"qtype": "mixed", "hit": r["hit"], "precision": r["precision"] or 0.0}
        for r in rows if r["qtype"] == "mixed"
    ]
    report = {
        "language_id": language,
        "eval_set_version": spec["version"],
        "index_snapshot": date.today().isoformat(),
        "n_items": len(rows),
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
    parser.add_argument("--lang", default=DEFAULT_LANGUAGE,
                        choices=SUPPORTED_LANGUAGES,
                        help="pack to score (per-pack set, index, reports)")
    parser.add_argument("--set", default=None,
                        help="defaults to data/eval/<lang>/eval-set.<lang>.v1.json")
    parser.add_argument("--index-dir", default=None,
                        help="defaults to data/index/<lang>")
    parser.add_argument("--report-dir", default=None,
                        help="defaults to data/eval/<lang>/reports")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args(argv)
    set_path = args.set or default_set_path(args.lang)
    index_dir = args.index_dir or f"data/index/{args.lang}"
    report_dir = args.report_dir or f"data/eval/{args.lang}/reports"
    report = run_eval(set_path, index_dir, report_dir, args.top_k, args.lang)
    json_path, md_path = write_reports(report, report_dir)
    print(f"hit_rate_at_5={report['hit_rate_at_5']:.3f} "
          f"precision={report['citation_precision']:.3f} "
          f"coverage={report['citation_coverage']:.3f} "
          f"abstention={report['abstention_correct']}")
    print(f"reports: {json_path} {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
