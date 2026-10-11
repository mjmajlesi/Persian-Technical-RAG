"""Threshold calibration (T024).

Calibrated 2026-10-07 on the frozen 503-chunk v1 index with 12 probes
(6 in-domain/C questions that MUST be answered, 6 out-of-domain questions
that MUST abstain). Method: top-1 cosine per probe; threshold = midpoint of
the separation gap between max(out) and min(in) when separable.

RESULT: max(out) = 0.775, min(in) = 0.849 -> gap [0.775, 0.849],
threshold = 0.81. Applied as abstain.DEFAULT_THRESHOLD.

Rationale: the midpoint maximizes the margin on both sides, so small
embedding noise is least likely to flip a verdict. The value is provisional
until the versioned 30-question eval set (T030) re-validates it: if
abstention_correct < 5/5 or in-domain hit-rate drops, re-run this script
with the eval questions and move the threshold.

NOTE: task text says "on fixtures" — outdated; fixtures were replaced by
the real frozen corpus in T010b, so calibration runs on the real index.
"""

CALIBRATION_PROBES: list[tuple[str, bool]] = [
    # (question, should_answer)
    ("تفاوت malloc و calloc چیست؟", True),
    ("حلقه for در C چگونه کار می‌کند؟", True),
    ("اشاره‌گر در C چیست و چه کاربردی دارد؟", True),
    ("پرچم صفر در printf چه اثری دارد؟", True),
    ("اندازه struct در حافظه چگونه محاسبه می‌شود؟", True),
    ("ماکروهای تابع‌وار در پیش‌پردازنده چه خطری دارند؟", True),
    ("پایتخت فرانسه کجاست و جمعیت آن چقدر است؟", False),
    ("بهترین دستور پخت قرمه‌سبزی چیست؟", False),
    ("قهرمان جام جهانی فوتبال چه تیمی شد؟", False),
    ("علائم سرماخوردگی و درمان آن چیست؟", False),
    ("جنگ جهانی دوم در چه سالی تمام شد؟", False),
    ("بهترین آلبوم موسیقی سنتی ایرانی کدام است؟", False),
]


def calibrate(retriever, probes=CALIBRATION_PROBES) -> dict:
    """Score probes and return {in_scores, out_scores, threshold}."""
    in_scores, out_scores = [], []
    for question, should_answer in probes:
        top = retriever.retrieve(question, k=1)[0]["score"]
        (in_scores if should_answer else out_scores).append((question, top))
    lo = max(s for _, s in out_scores)
    hi = min(s for _, s in in_scores)
    if lo >= hi:
        raise ValueError(f"classes not separable: max(out)={lo:.3f} >= min(in)={hi:.3f}")
    return {"in_scores": in_scores, "out_scores": out_scores,
            "threshold": (lo + hi) / 2}


def main() -> None:
    from src.qa.retriever import Retriever

    result = calibrate(Retriever("data/index"))
    print("IN-DOMAIN (must answer):")
    for question, score in result["in_scores"]:
        print(f"  {score:.3f}  {question[:45]}")
    print("OUT-OF-DOMAIN (must abstain):")
    for question, score in result["out_scores"]:
        print(f"  {score:.3f}  {question[:45]}")
    print(f"CALIBRATED THRESHOLD: {result['threshold']:.2f}")


if __name__ == "__main__":
    main()
