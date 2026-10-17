"""Contract test (US2, T021): abstention purity of POST /api/ask.

TDD: written BEFORE the threshold-gated abstention path (T023) exists.
Run: pytest tests/contract/test_abstention.py

Contract (contracts/ask-api.md, type=abstain + clarification Q5 decision):
  - out-of-corpus question -> abstain with a Persian redirect message;
  - citations == [] (zero fabricated citations);
  - every suggested_topic exists in the corpus (manifest titles/sections).
"""

import json
import subprocess
import time
import urllib.request

from src.web.packs import get_pack

PORT = 8129
_DEFAULT_PACK = get_pack("c")
INDEX_DIR = _DEFAULT_PACK.index_dir
MANIFEST = _DEFAULT_PACK.manifest_path


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


def _corpus_topics():
    manifest = json.loads(open(MANIFEST, encoding="utf-8").read())
    titles = {s["title"] for s in manifest["sources"]}
    sections = set()
    with open(f"{INDEX_DIR}/chunks.jsonl", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                record = json.loads(line)
                sections.add(record["section_heading"])
                sections.add(record["doc_title"])
    return titles | sections


def test_abstention_has_zero_citations():
    known = _corpus_topics()
    proc = _serve()
    try:
        status, body = _post({"question": "پایتخت فرانسه کجاست و جمعیت آن چقدر است؟"})
        assert status == 200, f"expected 200, got {status}: {body}"
        assert body["type"] == "abstain", f"expected abstain, got: {body}"
        assert body["citations"] == [], "abstention carries citations!"
        assert len(body.get("suggested_topics", [])) >= 1
        for topic in body["suggested_topics"]:
            assert topic in known, f"suggested topic not in corpus: {topic}"
    finally:
        proc.terminate()
