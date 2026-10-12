# Persian Technical RAG — پاسخ‌گویی grounded فارسی به سوالات فنی C

پروژه کارشناسی: سیستم بازیابی-افزوده (RAG) که به سوالات فنی فارسی درباره زبان C
از روی کورپوس فریز و محدود، **جواب فارسی مستند** می‌دهد — هر ادعا با استناد قابل
کلیک به چانک واقعی، و در صورت ناکافی‌بودن زمینه، امتناع صریح به‌جای جعل جواب.

## وضعیت بازتولیدشده (Examiner target)

آخرین اجرای ثبت‌شده روی ست v1 (۳۰ سوال، ایندکس ۵۰۳ چانکی) — گزارش کامل:
`data/eval/reports/2026-10-12-v1.{json,md}`

| متریک | مقدار |
|---|---|
| Hit-rate@5 (پاسخ‌دادنی‌ها) | ۱٫۰۰۰ (۲۵/۲۵) |
| Citation coverage (جواب‌ها) | ۱٫۰۰۰ (همه منبع کلیدی را آوردند؛ صفر فانتوم) |
| Citation precision سخت‌گیرانه | ۰٫۶۹۰ (مدل چانک‌های خواهر مرتبط را هم استناد می‌کند) |
| Abstention بیرون‌دامنه | ۵/۵ با صفر استناد |
| Mixed slice | hit ۱٫۰ / precision ۰٫۶۰۷ |

## کورپوس فریز v1 (۵۲ منبع، ۵۰۳ چانک)

- ۱۲ فایل جزوه فارسی (۱۱ فصل C + پیوست مکمل دو) — `data/corpus/full/c-notes-*.md`
- ۳۵ صفحه cppreference.com بخش C (CC-BY-SA) و ۵ گره راهنمای glibc (GFDL) — `data/corpus/full/ref-*.md`
- فصل C++ جزوه عمداً ingest نشده (اسکوپ: فقط C)؛ مانیفست: `data/corpus/manifest.json`

## ۱. نصب

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

Python هدف: 3.11 (تست‌شده با 3.11.15). سپس فایل `.env` را از روی `.env.example`
بسازید و هر سه مقدار را بگذارید (`LLM_API_KEY`، `LLM_BASE_URL`، `LLM_MODEL`).

## ۲. Ingest و ایندکس (یک‌دستوری، قطعی)

```powershell
.\.venv\Scripts\python -m src.ingest --manifest data/corpus/manifest.json
.\.venv\Scripts\python -m src.index build --manifest data/corpus/manifest.json
```

خروجی موردانتظار: `total: 503 chunks` و `indexed: 503 chunks (dim 1024)` در
`data/index/` (چانک‌ها، ایندکس FAISS، فهرست شناسه‌ها).

## ۳. پرسش (دمو وب)

```powershell
.\.venv\Scripts\python -m uvicorn src.web.app:app --port 8000
```

مرورگر: `http://localhost:8000` — سوال فارسی → جواب فارسی با چیپ‌های استناد
(کلیک = عنوان منبع + سرفصل + متن کامل چانک). API مستقیم:

```powershell
curl -X POST http://localhost:8000/api/ask `
  -H "Content-Type: application/json" `
  -d '{"question": "تفاوت malloc و calloc چیست؟"}'
```

## ۴. ارزیابی (یک‌دستوری)

```powershell
.\.venv\Scripts\python -m pytest tests/ -x -q
.\.venv\Scripts\python -m src.eval run --set data/eval/eval-set.v1.json
```

انتظار: همه تست‌ها سبز؛ گزارش JSON + Markdown در `data/eval/reports/` با همان
عددهای جدول بالا (کالیبراسیون آستانه: `python -m src.eval.calibrate`).

## ساختار

```text
src/ingest  chunker + writer + CLI ingest      src/index  embed + FAISS + CLI build
src/qa      retriever + answer + abstain + LLM provider
src/eval    calibrate + scoring + run          src/web    FastAPI + صفحه دمو
data/       corpus/ (فریز) index/ (ساخته‌شده) eval/ (ست v1 + گزارش‌ها)
specs/      001-persian-c-qa (اسپک/plan/تسک‌ها) 002-multi-language-dashboard (فاز بعد)
```

## اسناد حکمرانی

- قانون اساسی: `.specify/memory/constitution.md` (نسخه ۱٫۱٫۰ — groundedness، دقت
  استناد، اسکوپ صادقانه، ایزولاسیون هر زبان)
- توجه لایسنسی: محتوای cppreference با ذکر CC-BY-SA و راهنمای glibc با GFDL
  در هدر هر فایل مرجع و مانیفست ثبت شده است.
