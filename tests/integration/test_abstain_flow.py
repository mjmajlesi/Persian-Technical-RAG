"""Integration test (US2, T022): out-of-corpus -> abstain journey.

TDD: written BEFORE the threshold-gated abstention path (T023) exists.
Run: pytest tests/integration/test_abstain_flow.py

Journey: ask an irrelevant (out-of-corpus) question -> explicit abstention
with a Persian redirect message and no factual claims (zero citations).
"""

import json
import subprocess
import time
import urllib.request

PORT = 8130


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


def test_out_of_corpus_abstains():
    proc = _serve()
    try:
        status, body = _post(
            {"question": "بهترین دستور پخت قرمه‌سبزی چیست و چقدر طول می‌کشد؟"}
        )
        assert status == 200, f"expected 200, got {status}: {body}"
        assert body["type"] == "abstain", f"expected abstain, got: {body}"
        assert body["citations"] == [], "unsupported claims leaked!"
        assert any("؀" <= ch <= "ۿ" for ch in body["message"]), \
            "abstention message is not Persian"
        assert len(body.get("suggested_topics", [])) >= 1
    finally:
        proc.terminate()
