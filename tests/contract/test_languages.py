"""Contract test (002-US1, T011): GET /api/languages.

Written AFTER the endpoint (002-T007) existed, so it may pass immediately —
the FAIL-first gate applied when T007 was implemented; this test locks the
contract so regressions fail here from now on. Run:
pytest tests/contract/test_languages.py

Contract (contracts/languages-api.md):
  - default == "c" (preselected);
  - one entry per pack manifest: c, cpp, python, java (no duplicates);
  - display_name/snapshot/eval_set_version non-empty per pack;
  - status is a valid "ready"|"empty" value (all four are ready in-tree).
"""

import json
import subprocess
import time
import urllib.request
from pathlib import Path

PORT = 8134
SUPPORTED = {"c", "cpp", "python", "java"}  # exact members, order-free



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


def _get(path):
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{PORT}{path}",
                                    timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:  # noqa: B904
        return exc.code, {"detail": exc.read().decode("utf-8")}


def test_languages_matches_pack_contract():
    proc = _serve()
    try:
        status, body = _get("/api/languages")
        assert status == 200, f"expected 200, got {status}: {body}"
        assert body["default"] == "c", f"default must be 'c': {body['default']}"

        packs = body["languages"]
        ids = [p["language_id"] for p in packs]
        assert set(ids) == SUPPORTED, f"pack ids mismatch: {ids}"
        assert len(set(ids)) == len(ids), "duplicate language_id entries"

        for pack in packs:
            lid = pack["language_id"]
            assert pack["status"] in ("ready", "empty"), \
                f"{lid}: invalid status {pack['status']}"
            assert pack["status"] == "ready", \
                f"{lid}: pack not ingested (status={pack['status']})"
            for field in ("display_name", "snapshot", "eval_set_version"):
                assert isinstance(pack[field], str) and pack[field].strip(), \
                    f"{lid}: {field} must be a non-empty string"
            eval_set = json.loads(
                Path(f"data/eval/{lid}/eval-set.{lid}.v1.json").read_text(
                    encoding="utf-8"))
            assert pack["eval_set_version"] == eval_set["version"], \
                f"{lid}: manifest points to a different eval-set version"
    finally:
        proc.terminate()
