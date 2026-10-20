"""Contract test (002-US2, T016): zero cross-language contamination.

NOTE on FAIL-first: written AFTER the threshold-gated abstention path
(002-T023 wired the score gate BEFORE any LLM call, and T009/T014 per-pack
registry), so each probe is EXPECTED to pass immediately — the same post-hoc
status already documented for T011–T015 tests. The FAIL-first gate belonged
to T017 (pack-scoped citation validation in the ANSWER branch, not yet
implemented); this test locks the contamination contract now. Run:
pytest tests/contract/test_no_cross_language_citations.py

Contract (002 spec.md US2 independent test + constitution Principle VIII):
for EACH ready pack A, a question answerable ONLY in another pack B's
corpus (A has no such concept) must yield
  - type == "abstain" (no fabricated answer);
  - citations == [] — zero citations, hence zero foreign chunk_ids;
  - language_id == A (the abstention came from the selected pack).
Probes are deliberately single-domain (range = Python, malloc = C,
interface = Java, template = C++) so semantic adjacency cannot lift them
over the pack's gate. The gate abstains pre-LLM, so these calls cost zero
model credit.
"""

import json
import re
import subprocess
import time
import urllib.error
import urllib.request

from src.web.packs import load_packs

PORT = 8137
# B-only question asked under pack A (key = pack that must ABSTAIN).
FOREIGN_QUESTIONS = {
    "c": "تابع range در پایتون چگونه کار می‌کند؟",          # python-only
    "cpp": "تعریف interface در جاوا چگونه است؟",            # java-only
    "python": "تفاوت malloc و calloc چیست؟",               # c-only
    "java": "الگوی template در ++C چگونه کار می‌کند؟",       # cpp-only
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


def test_cross_pack_questions_abstain_with_zero_citations():
    ready = {p.language_id: p for p in load_packs() if p.status == "ready"}
    assert ready, "no ready packs - run the ingest CLIs first"
    assert set(ready) >= set(FOREIGN_QUESTIONS), \
        "missing ready packs for the cross-language probes"
    proc = _serve()
    try:
        for lang, question in FOREIGN_QUESTIONS.items():
            status, body = _post({"question": question, "language": lang})
            assert status == 200, \
                f"[{lang}] expected 200, got {status}: {body}"
            assert body["type"] == "abstain", \
                f"[{lang}] B-only question answered under pack A: {body}"
            assert body.get("citations") == [], \
                f"[{lang}] abstain response must carry zero citations, " \
                f"got {body.get('citations')}"
            assert body.get("language_id") == lang, \
                f"[{lang}] abstention attributed to the wrong pack: {body}"
            # No bare chunk id from another pack anywhere in the payload.
            ids = _dump_ids(body)
            assert not ids, f"[{lang}] chunk ids leaked into abstain: {ids}"
    finally:
        proc.terminate()


import re  # noqa: E402 - single helper below

CHUNK_ID_RE = re.compile(r"[\w\-]+#s\d+-c\d+")


def _dump_ids(payload):
    """Any 001-style chunk id ("<corpus>#s<b>-c<d>") inside the payload."""
    return CHUNK_ID_RE.findall(json.dumps(payload, ensure_ascii=False))
