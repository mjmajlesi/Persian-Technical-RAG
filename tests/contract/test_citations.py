"""Contract test (US1, T016): citation traceability of POST /api/ask.

TDD: written BEFORE the answer path (T018) exists, so it FAILS until T018
wires the endpoint. Run: pytest tests/contract/test_citations.py

Contract (contracts/ask-api.md, type=answer):
  - >= 1 citation; every chunk_id exists in data/index/chunks.jsonl;
  - every cited id is in retrieved_chunk_ids;
  - every excerpt equals the stored chunk text.
"""

import json
import subprocess
import time
import urllib.request

from src.web.packs import get_pack

PORT = 8124
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


def test_answer_citations_are_traceable():
    proc = _serve()
    try:
        status, body = _post({"question": "تفاوت malloc و calloc چیست؟"})
        assert status == 200, f"expected 200, got {status}: {body}"
        assert body["type"] == "answer"
        assert len(body["citations"]) >= 1, "answer has no citations"

        stored = {}
        with open(f"{INDEX_DIR}/chunks.jsonl", encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    record = json.loads(line)
                    stored[record["chunk_id"]] = record["text"]

        for citation in body["citations"]:
            cid = citation["chunk_id"]
            assert cid in stored, f"phantom citation: {cid}"
            assert cid in body["retrieved_chunk_ids"], f"uncited retrieval: {cid}"
            assert citation["excerpt"] == stored[cid], f"excerpt drift: {cid}"
    finally:
        proc.terminate()
