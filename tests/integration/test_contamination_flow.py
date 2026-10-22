# -*- coding: utf-8 -*-
"""Integration test (002-US2, T018): wrong-language question flow.

Phase-2 counterpart of the T016 contract probe: through the REAL HTTP flow
(spawned uvicorn + /api/ask), EVERY ready pack is asked a question from
each of the other ready packs' domains.

T024 recalibrated the per-pack gates (c 0.803 / cpp 0.82 / python 0.79 /
java 0.791), and cross-language questions can score ABOVE the gate - even
above the weakest in-domain items - so the gate alone cannot separate
wrong-language questions. The defense-in-depth chain therefore is:

  - question BELOW the gate -> must abstain: Persian redirect, citations
    == [], zero LLM credit. Deterministic.
  - question ABOVE the gate (LLM backstop territory, nondeterministic by
    model behavior) -> the inviolable contract is that citations (if any)
    are strictly pack-internal, guaranteed by the T017 citation validation;
    an in-pack answer to a foreign question is a quality issue measured by
    the T025 contamination slice, never a contamination leak.

Failures here mean foreign citations slipped into the user-visible flow.
Run: pytest tests/integration/test_contamination_flow.py
"""

import json
import subprocess
import time
import urllib.error
import urllib.request

from src.qa.pack_config import threshold_for
from src.qa.retriever import Retriever
from src.web.packs import load_packs

PORT = 8139
# One canonical single-domain question per pack (question authored for
# the keyed pack; asked under every OTHER pack's pack id).
DOMAIN_QUESTIONS = {
    "c": "تفاوت malloc و calloc چیست؟",
    "cpp": "چگونه در ++C متد تعریف کنیم؟",
    "python": "تابع range در پایتون چگونه کار می‌کند؟",
    "java": "وراثت (inheritance) در جاوا چگونه کار می‌کند؟",
}


def _serve():
    proc = subprocess.Popen(
        [".venv/Scripts/python", "-m", "uvicorn", "src.web.app:app",
         "--port", str(PORT)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(60):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{PORT}/docs", timeout=2)
            return proc
        except Exception:  # noqa: BLE001 - server not up yet
            time.sleep(1)
    proc.terminate()
    raise AssertionError("server did not start")


def _post(payload):
    req = urllib.request.Request(
        f"http://127.0.0.1:{PORT}/api/ask",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:  # noqa: B904
        return exc.code, {"detail": exc.read().decode("utf-8")}


def _is_persian(text):
    return any("؀" <= ch <= "ۿ" for ch in text)


def test_wrong_language_questions_abstain_with_persian_redirect():
    ready = [p for p in load_packs() if p.status == "ready"]
    assert len(ready) >= 2, "need at least two ready packs to cross-check"
    retrievers = {p.language_id: Retriever(p.index_dir) for p in ready}
    proc = _serve()
    try:
        for pack in ready:
            asked_under = pack.language_id
            gate = threshold_for(asked_under)
            for src_lang in (p.language_id for p in ready):
                if src_lang == asked_under:
                    continue
                question = DOMAIN_QUESTIONS[src_lang]
                status, body = _post(
                    {"question": question, "language": asked_under})
                label = f"[{src_lang}-question under {asked_under}]"
                assert status == 200, f"{label} got {status}: {body}"
                top1 = retrievers[asked_under].retrieve(
                    question, k=1)[0]["score"]
                message = body.get("message", "")
                if top1 < gate:
                    # Below the calibrated gate: deterministic abstention.
                    assert body["type"] == "abstain", \
                        f"{label} (top-1 {top1:.3f} < gate {gate}) " \
                        f"answered instead of abstaining: {body}"
                    assert message and _is_persian(message), \
                        f"{label} redirect is not a Persian message: {message!r}"
                    assert body.get("citations") == [], \
                        f"{label} carries citations: {body.get('citations')}"
                    assert body.get("language_id") == asked_under, \
                        f"{label} abstention attributed to wrong pack: {body}"
                else:
                    # Above the gate: LLM backstop territory. If the
                    # backstop abstains, require the plain abstain shape;
                    # if it answers, every citation must be pack-internal.
                    assert body["type"] in ("abstain", "answer"), \
                        f"{label} unexpected type {body['type']}: {body}"
                    if body["type"] == "abstain":
                        assert body.get("citations") == [], \
                            f"{label} abstention carries citations: {body}"
                        assert message and _is_persian(message), \
                            f"{label} redirect is not Persian: {message!r}"
                    else:
                        cited = [c["chunk_id"] for c in body.get("citations", [])]
                        assert all(
                            retrievers[asked_under].has_chunk(cid)
                            for cid in cited), \
                            f"{label} cites foreign/fabricated chunks: {cited}"
    finally:
        proc.terminate()
