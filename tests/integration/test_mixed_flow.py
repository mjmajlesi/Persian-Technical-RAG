"""Integration test (US3, T026): mixed Persian/English queries.

TDD: written BEFORE mixed-query handling (T027) exists.
Run: pytest tests/integration/test_mixed_flow.py

Probes: Persian questions embedding English identifiers (malloc, printf)
-> grounded cited answers meeting the same bar as pure-Persian queries,
with Latin identifiers preserved verbatim (not translated/transliterated).
"""

import json
import subprocess
import time
import urllib.request

from src.web.packs import get_pack

PORT = 8132
_DEFAULT_PACK = get_pack("c")
INDEX_DIR = _DEFAULT_PACK.index_dir


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
    except urllib.error.HTTPError as exc:
        return exc.code, {"detail": exc.read().decode("utf-8")}


def test_mixed_persian_english_queries():
    stored = set()
    with open(f"{INDEX_DIR}/chunks.jsonl", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                stored.add(json.loads(line)["chunk_id"])

    proc = _serve()
    try:
        for question, identifier in [
            ("تابع malloc در C چه کاری انجام می‌دهد؟", "malloc"),
            ("تفاوت printf و scanf در خواندن ورودی چیست؟", "scanf"),
        ]:
            status, body = _post({"question": question})
            assert status == 200, f"expected 200, got {status}: {body}"
            assert body["type"] == "answer", f"expected answer, got: {body}"
            assert len(body["citations"]) >= 1
            for citation in body["citations"]:
                assert citation["chunk_id"] in stored, \
                    f"phantom citation: {citation['chunk_id']}"
            assert identifier in body["answer_text"], \
                f"identifier {identifier!r} not preserved verbatim in answer"
    finally:
        proc.terminate()
