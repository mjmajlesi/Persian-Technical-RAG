# بازتولید دستی، گام‌به‌گام

The following English and Persian quickstarts are preserved verbatim as historical manual instructions. Run commands from the repository root; the current pinned dependencies are in `requirements-lock.txt`.

## English original

<a id="quickstart"></a>
## Quick start: run the C pack first

This is the shortest setup path to a dashboard with **one prepared pack**, not a
guarantee of short download or processing times. Commands target **Windows,
PowerShell, and Python 3.11** and run from the repository root. Virtual-environment
activation is unnecessary: commands invoke its Python directly.

### Prerequisites

- Git, Python **3.11**, and a browser.
- Internet access for packages and initial embedding-model downloads, plus several GB of free disk space for weights and caches.
- An API key and model name for an OpenAI-compatible Chat service to **generate answers**.
- A GPU was not required for the recorded workflow. Research builds used a CPU-only laptop with about 15.6 GiB RAM; this is not a guaranteed minimum-memory specification.

> [!WARNING]
> Ingest and build commands **write files**. Ingest fails on a missing or empty
> source and atomically publishes its completed output, but rebuilding an index
> can still replace artifacts. Check sources and dataset versions first.

### 1. Clone and install

Skip the clone step if you already have the repository:

```powershell
git clone https://github.com/mjmajlesi/Persian-Technical-RAG.git
cd Persian-Technical-RAG

python --version
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed' }
```

Direct dependencies are pinned; transitive dependencies such as Torch and NumPy
are not fully locked. Check an existing installation with:

```powershell
.\.venv\Scripts\python -m pip check
```

### 2. Configure the answer-generating LLM

Create a local `.env` file at the repository root using an editor. If it already
exists, preserve your settings and update only what is needed. The values below
are **placeholders, not working credentials**:

```dotenv
LLM_API_KEY=<YOUR_API_KEY>
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=<YOUR_CHAT_MODEL>
```

| Variable | Purpose |
|---|---|
| `LLM_API_KEY` | Service API key; never commit it |
| `LLM_BASE_URL` | Service base URL; the provider appends `/chat/completions` |
| `LLM_MODEL` | Answer model name accepted by that service, not the embedding model |
| `LLM_EXPECTED_RESPONSE_MODEL` | Research E2E only: independently verified model ID returned by the API |

For another service, use its valid base URL and model name. Existing process
environment variables take precedence over `.env`. Restart the server after
changing answer-provider settings. The versioned `.env.example` contains only
placeholders; copy it to a local `.env`, supply your own settings, and never
commit `.env`.

Without an LLM, you can still prepare sources, build indices, and run
retrieval-only evaluation. Generating answers requires an active service;
requests reaching the LLM may incur charges.

### 3. Check source files before building

This read-only check inspects sources referenced by all four manifests; it does
not load a model or access the network:

```powershell
@'
import json
from pathlib import Path

for lang in ("c", "cpp", "python", "java"):
    path = Path(f"data/corpus/manifest.{lang}.json")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    missing = []
    for source in manifest["sources"]:
        origin = Path(source["origin"])
        if not origin.is_file() or not origin.read_text(encoding="utf-8").strip():
            missing.append(source["source_id"])
    if missing:
        raise SystemExit(f"Missing or empty sources for {lang}: {missing}")
    print(lang, "sources:", len(manifest["sources"]), "OK")
'@ | .\.venv\Scripts\python -B -
if ($LASTEXITCODE -ne 0) { throw 'Source preflight failed; do not ingest' }
```

Expected source counts: C **52**, C++ **13**, Python **9**, and Java **16**, each
marked `OK`. This check does not establish scientific correctness or redistribution rights.

### 4. Build C and start the web app

```powershell
.\.venv\Scripts\python -m src.ingest --lang c
if ($LASTEXITCODE -ne 0) { throw 'C ingest failed' }
if (@(Get-Content -Encoding UTF8 'data/index/c/chunks.jsonl').Count -ne 503) {
    throw 'Unexpected C chunk count; stop before building the index'
}

.\.venv\Scripts\python -m src.index build --lang c
if ($LASTEXITCODE -ne 0) { throw 'C index build failed' }

.\.venv\Scripts\python -m uvicorn src.web.app:app --host 127.0.0.1 --port 8000
```

The first build downloads the embedding model if needed. C should have **503
chunks with 1,024-dimensional embeddings**. A matching count alone does not prove
content or index integrity; research reproduction also requires matching baseline hashes.

Dashboard: **http://127.0.0.1:8000** · API docs: **http://127.0.0.1:8000/docs**

Select C and ask **«تفاوت malloc و calloc چیست؟»** (“What is the difference between
malloc and calloc?”). Click a citation to inspect its evidence. Clicking a
**sample question** submits it automatically and may trigger a paid request;
clicking a **suggested topic after abstention** only fills the question field.
Stop the server with `Ctrl+C`. If you built only C, the other packs being
unavailable is expected.

### 5. Prepare the remaining packs

After the source check succeeds, use another PowerShell window or stop the server:

```powershell
$expectedCounts = @{ cpp = 201; python = 253; java = 73 }
foreach ($lang in 'cpp', 'python', 'java') {
    .\.venv\Scripts\python -m src.ingest --lang $lang
    if ($LASTEXITCODE -ne 0) { throw "Ingest failed: $lang" }
    $count = @(Get-Content -Encoding UTF8 "data/index/$lang/chunks.jsonl").Count
    if ($count -ne $expectedCounts[$lang]) { throw "Unexpected chunk count: $lang" }

    .\.venv\Scripts\python -m src.index build --lang $lang
    if ($LASTEXITCODE -ne 0) { throw "Index build failed: $lang" }
}
```

Restart the server afterward. Pack IDs are `c`, `cpp`, `python`, and `java`;
use `cpp`, not `c++`, on the command line.


## متن فارسی اصلی

<a id="quickstart"></a>
## راه‌اندازی سریع؛ اول پک C را اجرا کنید

این مسیر کمترین مراحل برای دیدن داشبورد با **یک پک آماده** است؛ «سریع» به
معنی تضمین زمانِ دانلود یا پردازش نیست. همهٔ دستورها برای **Windows + PowerShell**
و از ریشهٔ مخزن نوشته شده‌اند. فعال‌کردن `.venv` ضروری نیست؛ Python آن را مستقیم اجرا می‌کنیم.

### پیش‌نیازها

- Git، Python **3.11** و مرورگر.
- اینترنت برای نصب بسته‌ها و دریافت اولیهٔ وزن Embedding؛ چند گیگابایت فضای آزاد برای مدل‌ها و Cache.
- برای **پاسخ‌سازی**، کلید و نام مدلِ یک سرویس Chat سازگار با OpenAI.
- GPU برای مسیر ثبت‌شده لازم نبوده است؛ ساخت‌های پژوهشی روی لپ‌تاپ CPU-only با حدود ۱۵٫۶ GiB RAM انجام شده‌اند. این عدد حداقل حافظهٔ تضمین‌شده نیست.

> [!WARNING]
> Ingest و Build **فایل می‌نویسند**. Ingest روی منبع مفقود یا خالی شکست می‌دهد و
> خروجی کاملِ خود را به‌صورت اتمیک منتشر می‌کند، اما بازسازی Index همچنان می‌تواند
> فایل‌ها را جایگزین کند؛ ابتدا منابع و نسخهٔ داده را بررسی کنید.

### ۱. دریافت و نصب

اگر مخزن را از قبل دارید، مرحلهٔ Clone را رد کنید:

```powershell
git clone https://github.com/mjmajlesi/Persian-Technical-RAG.git
cd Persian-Technical-RAG

python --version
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed' }
```

وابستگی‌های مستقیم نسخهٔ ثابت دارند؛ وابستگی‌های غیرمستقیم مثل Torch/NumPy
به‌طور کامل قفل نشده‌اند. برای بررسی سازگاریِ نصب موجود می‌توانید اجرا کنید:

```powershell
.\.venv\Scripts\python -m pip check
```

### ۲. تنظیم پاسخ‌ساز

در ریشه، فایل محلی `.env` را با ویرایشگر بسازید. اگر موجود است، مقادیر خودتان
را حفظ و فقط موارد لازم را تنظیم کنید؛ مثال زیر **مقدار قابل‌استفادهٔ واقعی نیست**:

```dotenv
LLM_API_KEY=<YOUR_API_KEY>
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=<YOUR_CHAT_MODEL>
```

| متغیر | کاربرد |
|---|---|
| `LLM_API_KEY` | کلید سرویس؛ هرگز در Git ثبت نکنید |
| `LLM_BASE_URL` | نشانی پایهٔ سرویس؛ رابط مسیر `/chat/completions` را به آن اضافه می‌کند |
| `LLM_MODEL` | نام مدل پاسخ‌ساز نزد همان سرویس؛ نام مدل Embedding نیست |
| `LLM_EXPECTED_RESPONSE_MODEL` | فقط برای E2E پژوهشی؛ شناسهٔ برگشتیِ مستقل و ازپیش‌بررسی‌شده |

برای سرویس دیگری، آدرس و نام مدلِ معتبر همان سرویس را بگذارید. متغیرهای ازقبل
موجودِ فرایند بر `.env` اولویت دارند؛ پس از تغییر تنظیم پاسخ‌ساز، سرور را دوباره راه بیندازید.
به وجود `.env.example` در دریافت تازه تکیه نکنید؛ این فایل نسخه‌بندی نشده است.

بدون LLM هم می‌توانید منابع را آماده کنید، Index بسازید و Retrieval-only را
اجرا کنید؛ تولید Answer به سرویس فعال نیاز دارد. درخواست‌هایی که به LLM برسند ممکن است هزینه داشته باشند.

### ۳. پیش از ساخت، وجود منابع را بررسی کنید

این بررسی فقط فایل‌های منبعِ چهار Manifest را می‌خواند؛ مدل یا شبکه‌ای اجرا نمی‌کند:

```powershell
@'
import json
from pathlib import Path

for lang in ("c", "cpp", "python", "java"):
    path = Path(f"data/corpus/manifest.{lang}.json")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    missing = []
    for source in manifest["sources"]:
        origin = Path(source["origin"])
        if not origin.is_file() or not origin.read_text(encoding="utf-8").strip():
            missing.append(source["source_id"])
    if missing:
        raise SystemExit(f"Missing or empty sources for {lang}: {missing}")
    print(lang, "sources:", len(manifest["sources"]), "OK")
'@ | .\.venv\Scripts\python -B -
if ($LASTEXITCODE -ne 0) { throw 'Source preflight failed; do not ingest' }
```

خروجی موردانتظار: C برابر ۵۲، C++ برابر ۱۳، Python برابر ۹ و Java برابر ۱۶
منبع با برچسب `OK`. این کنترل جای بررسی علمیِ متن یا مجوز بازنشر را نمی‌گیرد.

### ۴. ساخت پک C و اجرای وب

```powershell
.\.venv\Scripts\python -m src.ingest --lang c
if ($LASTEXITCODE -ne 0) { throw 'C ingest failed' }
if (@(Get-Content -Encoding UTF8 'data/index/c/chunks.jsonl').Count -ne 503) {
    throw 'Unexpected C chunk count; stop before building the index'
}

.\.venv\Scripts\python -m src.index build --lang c
if ($LASTEXITCODE -ne 0) { throw 'C index build failed' }

.\.venv\Scripts\python -m uvicorn src.web.app:app --host 127.0.0.1 --port 8000
```

ساخت نخست مدل Embedding را در صورت نیاز دانلود می‌کند. شمار موردانتظار C،
**۵۰۳ چانک با بُعد ۱۰۲۴** است. شمار درست به‌تنهایی سلامت کاملِ محتوا/Index را ثابت نمی‌کند؛
برای بازتولید پژوهشی، Hashها هم باید با مبنا برابر باشند.

داشبورد: **http://127.0.0.1:8000** · مستندات API: **http://127.0.0.1:8000/docs**

برای C بپرسید: «تفاوت malloc و calloc چیست؟» سپس روی ارجاع کلیک کنید تا شاهد
را ببینید. کلیک **سؤال نمونه** خودکار ارسال می‌کند و می‌تواند تماس پولی ایجاد
کند؛ کلیک **موضوع پیشنهادی پس از انصراف** فقط کادر سؤال را پر می‌کند.
برای توقف سرور `Ctrl+C` بزنید. اگر فقط C را ساخته‌اید، آماده‌نبودن سه پک دیگر طبیعی است.

### ۵. آماده‌کردن سه پک دیگر

پس از موفقیت بررسی منابع، در PowerShell جدا یا بعد از توقف سرور:

```powershell
$expectedCounts = @{ cpp = 201; python = 253; java = 73 }
foreach ($lang in 'cpp', 'python', 'java') {
    .\.venv\Scripts\python -m src.ingest --lang $lang
    if ($LASTEXITCODE -ne 0) { throw "Ingest failed: $lang" }
    $count = @(Get-Content -Encoding UTF8 "data/index/$lang/chunks.jsonl").Count
    if ($count -ne $expectedCounts[$lang]) { throw "Unexpected chunk count: $lang" }

    .\.venv\Scripts\python -m src.index build --lang $lang
    if ($LASTEXITCODE -ne 0) { throw "Index build failed: $lang" }
}
```

بعد سرور را دوباره اجرا کنید. کلیدها `c`، `cpp`، `python` و `java` هستند؛
برای C++ در خط فرمان `cpp` بنویسید، نه `c++`.

<!-- End of preserved original quickstarts. -->
