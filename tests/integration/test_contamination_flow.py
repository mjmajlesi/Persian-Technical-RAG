# -*- coding: utf-8 -*-
"""Integration test (002-US2, T018): wrong-language question flow.

Phase-2 counterpart of the T016 contract probe: through the REAL HTTP flow
(spawned uvicorn + /api/ask), EVERY ready pack is asked a question from
each of the other ready packs' domains. The score gate (T023, before any
LLM call) must redirect in Persian with

  - type == "abstain";
  - a non-empty Persian message (the redirect);
  - citations == [] — zero citations, zero foreign chunk_ids;
  - language_id == the pack that abstained (not the question's domain).

Failures here mean contamination slipped past the contract layer (T016)
into the user-visible flow. Zero LLM credit is spent by construction.
Run: pytest tests/integration/test_contamination_flow.py
"""

import json
import subprocess
import time
import urllib.error
import urllib.request

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
    ready = [p.language_id for p in load_packs() if p.status == "ready"]
    assert len(ready) >= 2, "need at least two ready packs to cross-check"
    proc = _serve()
    try:
        for asked_under in ready:
            for src_lang in ready:
                if src_lang == asked_under:
                    continue
                question = DOMAIN_QUESTIONS[src_lang]
                status, body = _post(
                    {"question": question, "language": asked_under})
                label = f"[{src_lang}-question under {asked_under}]"
                assert status == 200, f"{label} got {status}: {body}"
                assert body["type"] == "abstain", \
                    f"{label} answered instead of abstaining: {body}"
                message = body.get("message", "")
                assert message and _is_persian(message), \
                    f"{label} redirect is not a Persian message: {message!r}"
                assert body.get("citations") == [], \
                    f"{label} carries citations: {body.get('citations')}"
                assert body.get("language_id") == asked_under, \
                    f"{label} abstention attributed to wrong pack: {body}"
    finally:
        proc.terminate()
