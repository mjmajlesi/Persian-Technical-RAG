#!/usr/bin/env bash
set -Eeuo pipefail
stage='setup'
trap 'printf "[%s] خطا در خط %s / Failed at line %s\n" "$stage" "$LINENO" "$LINENO" >&2' ERR

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
packs='c,cpp,python,java'
force=false
run=false
while (($#)); do
    case "$1" in
        --packs) (($# >= 2)) || { echo '[Packs] مقدار لازم است / Value required' >&2; exit 1; }; packs="$2"; shift 2 ;;
        --force) force=true; shift ;;
        --run) run=true; shift ;;
        *) echo "[Options] گزینه نامعتبر / Invalid option: $1" >&2; exit 1 ;;
    esac
done
IFS=',' read -r -a selected <<< "$packs"
((${#selected[@]})) || { echo '[Packs] پک لازم است / A pack is required' >&2; exit 1; }
for lang in "${selected[@]}"; do
    case "$lang" in c|cpp|python|java) ;; *) echo "[Packs] پک نامعتبر / Invalid pack: $lang" >&2; exit 1 ;; esac
done
echo '[Python] بررسی Python 3.11 / Checking Python 3.11'
python="$(command -v python3.11 || true)"
if [[ -z "$python" ]] || ! "$python" -c 'import sys; sys.exit(sys.version_info[:2] != (3, 11))'; then
    echo '[Python] Python 3.11 لازم است؛ آن را از python.org نصب کنید / Python 3.11 required; install it from python.org' >&2
    exit 1
fi
venv_python="$root/.venv/bin/python"
if [[ -e .venv ]]; then
    if [[ ! -x "$venv_python" ]] || ! "$venv_python" -c 'import os,sys; sys.exit(not (sys.version_info[:2] == (3,11) and os.path.samefile(sys._base_executable, sys.argv[1])))' "$python"; then
        echo '[venv] محیط موجود نامعتبر یا با مفسر دیگری است؛ آن را دستی جابه‌جا یا حذف کنید و دوباره اجرا کنید / Existing .venv is invalid or uses another interpreter; move or remove it manually, then rerun' >&2
        exit 1
    fi
    echo '[venv] محیط موجود سازگار است / Existing environment is compatible'
else
    stage='venv'
    echo '[venv] ساخت محیط / Creating environment'
    "$python" -m venv .venv
fi
echo '[pip] نصب وابستگی‌ها / Installing dependencies'
stage='pip'
"$venv_python" -m pip install --index-url https://pypi.org/simple -r requirements-lock.txt
echo '[pip check] بررسی وابستگی‌ها / Checking dependencies'
stage='pip check'
"$venv_python" -m pip check
if [[ ! -e .env ]]; then
    stage='env'
    cp -n .env.example .env
    echo '[env] ساخته شد؛ فقط LLM_API_KEY، LLM_BASE_URL و LLM_MODEL را تنظیم کنید؛ تا آن زمان فقط مسیر بدون تولید پاسخ کار می‌کند / Created; set only LLM_API_KEY, LLM_BASE_URL and LLM_MODEL; until then only paths without answer generation work'
else
    echo '[env] فایل موجود حفظ شد / Existing file preserved'
fi
warned=false
for lang in "${selected[@]}"; do
    case "$lang" in c) expected=503 ;; cpp) expected=201 ;; python) expected=253 ;; java) expected=73 ;; esac
    dir="data/index/$lang"
    ready=false
    if [[ -f "$dir/faiss.index" && -f "$dir/chunks.jsonl" && -f "$dir/ids.json" ]]; then
        count="$("$venv_python" -c 'import sys; print(sum(1 for _ in open(sys.argv[1], encoding="utf-8")))' "$dir/chunks.jsonl")"
        [[ "$count" == "$expected" ]] && ready=true
    fi
    if "$ready" && ! "$force"; then
        echo "[$lang] ایندکس آماده است؛ ساخت رد شد / Index ready; build skipped ($count chunks)"
        continue
    fi
    stage="ingest $lang"
    echo "[ingest $lang] ساخت Chunk / Ingesting"
    "$venv_python" -m src.ingest --lang "$lang"
    count="$("$venv_python" -c 'import sys; print(sum(1 for _ in open(sys.argv[1], encoding="utf-8")))' "$dir/chunks.jsonl")"
    if [[ "$count" != "$expected" ]]; then
        echo "[$lang] تعداد Chunk نادرست است / Unexpected chunk count: $count" >&2
        exit 1
    fi
    if ! "$warned"; then
        echo '[Index] دانلود اولیه مدل embedding ممکن است طول بکشد / First embedding-model download may take a while'
        warned=true
    fi
    stage="index $lang"
    echo "[index $lang] ساخت ایندکس / Building index"
    "$venv_python" -m src.index build --lang "$lang"
    for file in faiss.index chunks.jsonl ids.json; do
        if [[ ! -f "$dir/$file" ]]; then
            echo "[$lang] فایل ایندکس وجود ندارد / Index file missing: $file" >&2
            exit 1
        fi
    done
done
for lang in "${selected[@]}"; do
    case "$lang" in c) count=503 ;; cpp) count=201 ;; python) count=253 ;; java) count=73 ;; esac
    echo "[$lang] آماده / Ready: $count chunks"
done
echo '[Server] اجرا / Run: ./.venv/bin/python -m uvicorn src.web.app:app --host 127.0.0.1 --port 8000'
echo '[Server] نشانی / URL: http://127.0.0.1:8000'
if "$run"; then
    stage='server'
    echo '[Server] شروع / Starting'
    "$venv_python" -m uvicorn src.web.app:app --host 127.0.0.1 --port 8000
fi
