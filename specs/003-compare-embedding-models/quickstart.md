# Reproduce the embedding-model comparison (v2)

Run these PowerShell commands from the repository root with Python 3.11.
The research path is separate from the student dashboard's existing v1
operational index and gates. The [paper](../../docs/EMBEDDING-COMPARISON.md)
links the four primary comparison tables and all 12 model-language run pairs.
First model downloads require network access and several GB of disk. The
canonical runs used a CPU-only 15.6 GiB Windows laptop, **one model/process
at a time**. Kaggle/GPU is an optional fallback, not a dependency; use the
same pinned model revisions/settings and source/ID hashes, disclose device
and possible floating-point/top-k differences, and never transfer `.env`.

## 1. Install and regenerate canonical chunks

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt

$expected = @{
    c      = '8b2bb61d8a853280bc400d2ea1e4b8bd6bfb76c5a1106bbc99ab2a08ddcfad74'
    cpp    = 'c22bd9fb1e37a9f3e8cf1d2b747c8d9a9e6b050d7798817feb35f20fa0444366'
    python = '0b7afc4c24a6c34e10d797b9c2bab6ebd68f7c32636442c17eba280226d07649'
    java   = 'dd119c50203b76016275ae95513f145fac6005a95a4752a69f4dd0c35b63c9a8'
}
foreach ($lang in 'c', 'cpp', 'python', 'java') {
    .\.venv\Scripts\python -m src.ingest --lang $lang
    if ($LASTEXITCODE -ne 0) { throw "ingest failed: $lang" }
    $actual = (Get-FileHash "data/index/$lang/chunks.jsonl" -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $expected[$lang]) { throw "frozen chunks changed: $lang" }
}
```

Expected chunk counts are 503/201/253/73 (C/C++/Python/Java). The versioned
`data/index/<lang>/ids.json` must agree with the regenerated chunk order;
the build command checks it. Compare frozen v1 sets, manifests, and chunk
hashes with the [baseline audit](baseline-audit.md) before publication.
`chunks.jsonl` and FAISS binaries are regenerated/ignored, **not** copied
from another machine or staged in Git. Do not ingest the pilot as v2.

## 2. Build the 12 model-scoped dense indices, then verify cache reuse

```powershell
foreach ($model in 'e5-large', 'e5-base', 'bge-m3') {
    foreach ($lang in 'c', 'cpp', 'python', 'java') {
        .\.venv\Scripts\python -m src.index build --lang $lang --model $model
        if ($LASTEXITCODE -ne 0) { throw "index build failed: $model/$lang" }
    }
}
.\.venv\Scripts\python -m src.index build --lang c --model e5-large
```

The last command should print `cache hit`. Pinned revisions, MIT model
licenses, E5 `query:`/`passage:` prefixes and 512-token limit, BGE-M3's
instruction-free normalized dense vectors and 8192-token limit are in the
[registry](../../data/eval/model-comparison/models.json). Expected dimensions
are 1024/768/1024; the [CPU build log](index-build-log.md) records observed
timings, cache behavior, truncation counts, and frozen chunk hashes. The
operational no-`--model` path is not modified by research builds.

## 3. Verify the locked pooled-v1 gate — never fit on v2

```powershell
foreach ($model in 'e5-large', 'e5-base', 'bge-m3') {
    .\.venv\Scripts\python -m src.eval.calibrate --model $model --pooled-v1
    if ($LASTEXITCODE -ne 0) { throw "locked calibration mismatch: $model" }
}
```

One threshold per model was selected before v2 on the four frozen v1 packs
(100 answerable/20 OOC) by maximal balanced accuracy with conservative
tie-breaking. Existing [calibration records](../../data/eval/model-comparison/calibration/)
must say `unchanged locked research gate`; a changed revision, v1 set, or
gate is an error, not a reason to overwrite the record. These research
thresholds do not replace the four operational dashboard gates. Neither
the v2 sets nor pilot questions enter calibration.

## 4. Replay retrieval-only without altering official evidence

The committed report directory contains **exactly one** official
retrieval-only/E2E JSON pair per `(model, language)`. A fresh `run` writes a
new timestamped report; putting it there would make `compare` reject
ambiguous duplicates. Put all replays in a temporary directory instead:

```powershell
$replay = Join-Path $env:TEMP 'persian-rag-v2-replay'
foreach ($model in 'e5-large', 'e5-base', 'bge-m3') {
    foreach ($lang in 'c', 'cpp', 'python', 'java') {
        .\.venv\Scripts\python -m src.eval run --lang $lang --model $model `
            --set "data/eval/$lang/eval-set.$lang.v2.json" `
            --mode retrieval-only --report-dir "$replay/$model/$lang"
        if ($LASTEXITCODE -ne 0) { throw "retrieval failed: $model/$lang" }
    }
}
```

Each of the 12 replays should be `retrieval=complete`, `end-to-end=not_run`,
with 45 item rows, zero retrieval errors and **zero LLM calls**. Compare
top-5 IDs, hit flags, set/chunk SHA-256, model revision, gate and index
metadata with the linked [official reports](../../docs/EMBEDDING-COMPARISON.md#the-12-model-language-run-pairs-official-json).
Scores/top-k may differ across CPU/GPU devices; investigate differences
instead of silently replacing published evidence.

## 5. Optional audited E2E replays (12 runs; many provider calls)

E2E requires a live, authorized provider and incurs cost. In a **local,
gitignored** `.env` supply `LLM_API_KEY`, `LLM_BASE_URL` and requested
`LLM_MODEL`. There is no versioned `.env.example` in this repository;
create `.env` locally and never commit it. Before
the run, independently pre-register the *API-returned* model identifier in
the process environment (the historical reports used `gpt-5.6-sol`):

```powershell
$env:LLM_EXPECTED_RESPONSE_MODEL = '<verified API response model ID>'
foreach ($model in 'e5-large', 'e5-base', 'bge-m3') {
    foreach ($lang in 'c', 'cpp', 'python', 'java') {
        .\.venv\Scripts\python -m src.eval run --lang $lang --model $model `
            --set "data/eval/$lang/eval-set.$lang.v2.json" `
            --mode end-to-end --report-dir "$replay/$model/$lang"
        if ($LASTEXITCODE -ne 0) { throw "E2E incomplete: $model/$lang" }
    }
}
```

Do not run this block with the literal placeholder. The runner sends
`temperature=0` and checks the API-returned model ID on every LLM call;
gate-based abstentions have no LLM call. An absent/changed/unexpected ID,
rejected temperature, or failed request makes **only E2E incomplete**. The
official report preserves valid retrieval and error counts/reasons; partial
E2E rows belong in ignored diagnostics, not comparative metrics. A stable
returned ID (especially a proxy alias) cannot establish immutable backend
weights; `temperature=0` is not a determinism guarantee. Never commit keys,
base URLs, diagnostics, caches or FAISS binaries.

## 6. Reproduce and inspect the four *official* comparison tables

Run this only with the one-per-mode official pairs, not a directory of
multiple timestamped replays. It validates set/calibration provenance,
row-by-row retrieval agreement between modes, LLM response IDs, and
per-item hits/gate decisions before writing the four official files:

```powershell
.\.venv\Scripts\python -m pytest tests/ -q
.\.venv\Scripts\python -m src.eval compare --set-version v2
git diff --check
git status --short
```

The four committed primary tables and companion JSONs are:

| Language | Markdown | JSON | Decision for this language only |
|---|---|---|---|
| C | [C table](../../data/eval/c/reports/v2/comparison.v2.md) | [C data](../../data/eval/c/reports/v2/comparison.v2.json) | inconclusive |
| C++ | [C++ table](../../data/eval/cpp/reports/v2/comparison.v2.md) | [C++ data](../../data/eval/cpp/reports/v2/comparison.v2.json) | bge-m3 |
| Python | [Python table](../../data/eval/python/reports/v2/comparison.v2.md) | [Python data](../../data/eval/python/reports/v2/comparison.v2.json) | inconclusive |
| Java | [Java table](../../data/eval/java/reports/v2/comparison.v2.md) | [Java data](../../data/eval/java/reports/v2/comparison.v2.json) | bge-m3 |

Each language's three-model table has hit@5 on 38 answerable questions,
answered-only macro citation precision with answer/citation denominators,
fixed-gate and E2E abstention on seven OOC questions separately, mixed and
evidence-language slices, 95% percentile intervals (10,000 question draws;
seed `20261022`), and 98.33% Bonferroni-adjusted paired differences for
three model pairs. The OOC-positive AUROC/PR sweep is **descriptive only**;
its observed v2 optimum does not retune the v1 gate. The paper's 180-item
pooled table is explicitly secondary/exploratory and cannot elect a global
winner. If E2E is incomplete, retrieval metrics remain valid, but E2E
precision/abstention are N/A and no complete-run winner may be asserted.

Before any commit, confirm official JSON is stageable while research
`faiss.index` and `embeddings-*.npy` are ignored:

```powershell
git check-ignore -q --no-index -- data/eval/c/reports/v2/comparison.v2.json
if ($LASTEXITCODE -eq 0) { throw 'official JSON is unexpectedly ignored' }
git check-ignore -q --no-index -- data/research/embedding-compare/e5-large/c/faiss.index
if ($LASTEXITCODE -ne 0) { throw 'FAISS cache is unexpectedly stageable' }
git diff --cached --name-only
git diff --cached --check
```

Review staged paths **and content** for `.env`, credentials and binary
caches. This guide does not authorize committing regenerated replays or
changing existing official reports without a new reviewed evidence run.
T052 smoke-checked C ingest/hash, cached C index build, locked e5-large
calibration, one zero-LLM C replay in a temp folder, all four existing
comparisons and focused report tests; a fresh 12×E2E provider run was not
performed. Full closeout validation is a separate T053 gate.
