"""Integration test (002-US1, T015): select-and-ask journey per language.

TDD note: the language-scoped path (retriever registry + routing) already
existed when this test was authored — the FAIL-first checkpoint belonged to
implementation tasks T008/T014; this test audits the END-TO-END journey.
Run: pytest tests/integration/test_scoped_ask_flow.py

Journey (002 spec.md US1 Independent Test): for each ready pack, select the
language (the sidebar equivalent = the `language` field) -> ask an in-corpus
Persian question -> the Persian answer cites only pack-internal chunks.
Uses different in-corpus questions than the T012 contract test for wider
corpus coverage.
"""

import json
import subprocess
import time
import urllib.request

from src.web.packs import load_packs

PORT = 8136
# In-corpus Persian probes (scored 0.813–0.879 against the provisional 0.81
# gate; see the T012 calibration note — T024 will set per-pack values).
QUESTIONS = {
    "c": "حلقه for در C چگونه کار می‌کند؟",
    "cpp": "تفاوت کلاس و شیء در ++C چیست؟",
    "python": "چگونه در پایتون استثنا بگیریم؟",
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


def _pack_chunk_ids(pack):
    with open(f"{pack.index_dir}/chunks.jsonl", encoding="utf-8") as fh:
        return {json.loads(line)["chunk_id"] for line in fh if line.strip()}


def test_select_and_ask_each_ready_pack():
    ready = {p.language_id: p for p in load_packs() if p.status == "ready"}
    assert ready, "no ready packs - run the ingest CLIs first"
    proc = _serve()
    try:
        for lang, pack in ready.items():
            status, body = _post({"question": QUESTIONS[lang],
                                  "language": lang})
            assert status == 200, f"[{lang}] expected 200, got {status}: {body}"
            assert body["type"] == "answer", \
                f"[{lang}] in-corpus probe did not answer: {body}"
            assert body["language_id"] == lang, \
                f"[{lang}] scoped echo mismatch: {body['language_id']}"
            # answer is Persian-dominant (Arabic-script chars present)
            assert any("؀" <= ch <= "ۿ" for ch in body["answer_text"]), \
                f"[{lang}] answer is not Persian"

            stored = _pack_chunk_ids(pack)
            retrieved = set(body["retrieved_chunk_ids"])
            assert len(body["citations"]) >= 1, f"[{lang}] answer has no citations"
            for citation in body["citations"]:
                cid = citation["chunk_id"]
                assert cid in stored, \
                    f"[{lang}] pack-internal citation violated: {cid}"
                assert cid in retrieved, f"[{lang}] uncited retrieval: {cid}"
    finally:
        proc.terminate()
