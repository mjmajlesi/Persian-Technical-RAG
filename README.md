# Persian Technical RAG — پرسش‌وپاسخ مستند فارسی برای C، C++، Python و Java

نمونهٔ پایان‌نامهٔ کارشناسی: یک RAG با چهار **LanguagePack مستقل**، داشبورد راست‌به‌چپ، پاسخ فارسی همراه با ارجاع به چانک واقعیِ زبان انتخاب‌شده، و انصراف هنگام ناکافی‌بودن منابع. هر پک کورپوس فریز، ایندکس FAISS و مجموعهٔ ارزیابی خودش را دارد؛ خروجی‌ها بین زبان‌ها ادغام نمی‌شوند.

| پک | ترکیب منابع فریز | چانک | Hit@5 | دقت ارجاع | انصراف خارج‌پیکره | آلودگی بین‌زبان‌ها |
|---|---|---:|---:|---:|---:|---:|
| C | جزوهٔ فارسی + منابع انگلیسی C | 503 | 1.000 | 0.657 | 5/5 | 3/3 |
| C++ | جزوهٔ فارسی + cppreference | 201 | 0.600 | 0.812 | 5/5 | 3/3 |
| Python | مستندات انگلیسی رسمی | 253 | 0.760 | 0.602 | 5/5 | 3/3 |
| Java | مستندات انگلیسی رسمی | 73 | 0.920 | 0.706 | 5/5 | 3/3 |

مقادیر از چهار اجرای کامل پس از بازسازی ایندکس‌ها در T027 (۲۰۲۶-۱۰-۲۲) هستند؛ گزارش‌های Markdown در `data/eval/<lang>/reports/` ثبت شده‌اند. هر اجرا ۳۰ سؤال اصلی (۲۰ درون‌پیکره، ۵ mixed، ۵ خارج‌پیکره) و ۳ probe مستقلِ آلودگی دارد. **دقت ارجاع بین اجرای دوبارهٔ مدل ممکن است تغییر کند**؛ گزارش تازه باید `error_count=0` داشته باشد تا قابل استناد باشد. توضیح مهاجرت C: [`docs/MIGRATION-RESULTS.md`](docs/MIGRATION-RESULTS.md).

## نصب و پیکربندی

Python 3.11 روی Windows/PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

در `.env`، مقادیر `LLM_API_KEY`، `LLM_BASE_URL` و `LLM_MODEL` را برای یک سرویس OpenAI-compatible فعال تنظیم کنید. `.env` را commit نکنید. ingest، ایندکس و retrieval محلی‌اند؛ **پاسخ‌سازی و ارزیابی انتهابه‌انتها به LLM نیاز دارند**. provider پاسخ JSON عادی یا SSE را می‌پذیرد. خطاهای مدل در گزارش ارزیابی ثبت می‌شوند و اجرای ناقص با کد ناموفق پایان می‌یابد.

## بازسازی چهار پک از منابع فریز

از ریشهٔ پروژه، برای هر `lang` یکی از `c`، `cpp`، `python`، `java`:

```powershell
.\.venv\Scripts\python -m src.ingest --lang c
.\.venv\Scripts\python -m src.index build --lang c
```

دستورها را با `--lang cpp`، `--lang python` و `--lang java` نیز اجرا کنید؛ هر بار فقط `data/index/<lang>/` بازنویسی می‌شود. مانیفست‌ها و منشأ/مجوز منابع در `data/corpus/manifest.<lang>.json` هستند. C و C++ جزوهٔ فارسی دارند؛ Python و Java عمداً فقط منابع انگلیسی دارند. برای حالت فعلیِ مهاجرت‌یافته **اسکریپت مهاجرت را دوباره اجرا نکنید**؛ مسیرهای قدیمی دیگر وجود ندارند.

## داشبورد و بررسی

```powershell
.\.venv\Scripts\python -m uvicorn src.web.app:app --port 8000
```

`http://localhost:8000` را باز کنید: C پیش‌فرض است؛ از نوار کناری پک را عوض کنید. سؤال درون‌پیکره باید با ارجاع‌های همان پک جواب بگیرد، سؤال خارج‌پیکره انصراف می‌دهد، و سؤال خیلی کوتاه درخواست توضیح می‌کند. `GET /api/languages` وضعیت پک‌ها را برمی‌گرداند. پکِ بدون ایندکس `unavailable` است و شناسهٔ ناشناخته در `POST /api/ask` خطای 422 می‌گیرد.

## آزمون و ارزیابی مستقل هر زبان

```powershell
.\.venv\Scripts\python -m pytest tests/ -q
.\.venv\Scripts\python -m src.eval run --lang c
.\.venv\Scripts\python -m src.eval run --lang cpp
.\.venv\Scripts\python -m src.eval run --lang python
.\.venv\Scripts\python -m src.eval run --lang java
```

هر اجرا گزارش JSON محلی (نادیده‌گرفته‌شده در git) و Markdown را در `data/eval/<lang>/reports/` می‌نویسد؛ hit-rate@5، دقت و پوشش ارجاع، انصراف، mixed و contamination را **برای همان زبان** بخوانید. مجموعهٔ probeهای بین‌زبانی در `data/eval/contamination.v1.json` نسخه‌بندی شده است. راهنمای مرحله‌به‌مرحلهٔ ممتحن: [`specs/002-multi-language-dashboard/quickstart.md`](specs/002-multi-language-dashboard/quickstart.md).

**دامنه:** نمونهٔ محلی تک‌کاربره، نه سامانهٔ تولیدی؛ افزودن زبان خارج از چهار پک یا بازیابی از ایندکس مشترک در این نسخه پشتیبانی نمی‌شود. اصول پروژه: [constitution.md](.specify/memory/constitution.md).
