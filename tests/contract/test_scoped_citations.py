"""Contract test (002-US1, T012): language-scoped answer citations.

Written AFTER the routing existed (002-T008 wired the per-language retriever
registry), so it may pass immediately — the FAIL-first gate belonged to the
implementation task; this test locks cross-pack citation isolation from now
on. Run: pytest tests/contract/test_scoped_citations.py

Contract (002 spec.md US1 independent test + contracts/languages-api.md):
for EACH ready language, an in-corpus question yields type=answer whose
  - citations are >= 1;
  - every chunk_id resolves INSIDE that pack's own index (isolation by
    construction per constitution Principle VIII);
  - every cited id is in retrieved_chunk_ids of the same response.
"""

import json
import subprocess
import time
import urllib.request

from src.web.packs import load_packs

PORT = 8135
# In-corpus Persian probes (T004–T006 verified pack-internal retrieval).
QUESTIONS = {
    "c": "تفاوت malloc و calloc چیست؟",
    "cpp": "کلاس در ++C چیست و چگونه تعریف می‌شود؟",
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


def _pack_chunk_ids(pack):
    """Real chunk ids of one pack's index (only ready packs are probed)."""
    with open(f"{pack.index_dir}/chunks.jsonl", encoding="utf-8") as fh:
        return {json.loads(line)["chunk_id"]
                for line in fh if line.strip()}


def test_scoped_citations_answer_only_from_selected_pack():
    ready = {p.language_id: p for p in load_packs() if p.status == "ready"}
    assert ready, "no ready packs - run the ingest CLIs first"
    proc = _serve()
    try:
        for lang, pack in ready.items():
            status, body = _post({"question": QUESTIONS[lang], "language": lang})
            assert status == 200, f"[{lang}] expected 200, got {status}: {body}"
            assert body["type"] == "answer", \
                f"[{lang}] in-corpus probe did not answer: {body}"
            assert len(body["citations"]) >= 1, f"[{lang}] answer has no citations"

            stored = _pack_chunk_ids(pack)
            retrieved = set(body["retrieved_chunk_ids"])
            for citation in body["citations"]:
                cid = citation["chunk_id"]
                assert cid in stored, \
                    f"[{lang}] foreign/phantom citation: {cid}"
                assert cid in retrieved, f"[{lang}] uncited retrieval: {cid}"
    finally:
        proc.terminate()
