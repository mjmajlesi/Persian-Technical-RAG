"""Integration test (US1, T017): ingest -> ask -> cite journey.

TDD: written BEFORE the answer path (T018) exists, so it FAILS until T018
wires the endpoint. Run: pytest tests/integration/test_answer_flow.py

Journey: corpus already ingested (data/index, 503 chunks) -> ask an
in-corpus Persian question -> Persian answer whose every citation traces to
a real ingested chunk.
"""

import json
import subprocess
import time
import urllib.request

from src.web.packs import get_pack

PORT = 8125
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


def test_ingest_ask_cite_journey():
    # ingest artifact present (frozen 503-chunk snapshot)
    stored = {}
    with open(f"{INDEX_DIR}/chunks.jsonl", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                record = json.loads(line)
                stored[record["chunk_id"]] = record
    assert len(stored) > 0, "index is empty - run the ingest CLI first"

    proc = _serve()
    try:
        status, body = _post({"question": "حلقه for در C چگونه کار می‌کند؟"})
        assert status == 200, f"expected 200, got {status}: {body}"
        assert body["type"] == "answer"
        assert len(body["citations"]) >= 1

        # answer is Persian-dominant (Arabic-script chars present)
        assert any("؀" <= ch <= "ۿ" for ch in body["answer_text"]), \
            "answer is not Persian"

        for citation in body["citations"]:
            assert citation["chunk_id"] in stored, \
                f"citation not in ingested corpus: {citation['chunk_id']}"
    finally:
        proc.terminate()
