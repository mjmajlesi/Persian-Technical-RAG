# Prompt sensitivity: limited follow-up

This follow-up supplements the historical v2.0 results; it does not replace or
recompute them. It examines Python/e5-large twice and C++/e5-large once, with a
C/e5-large control. The old shared answer template described the assistant as a
C assistant for every pack; the revised template names the selected language.
The rendered C prompt is unchanged.

## Runs and comparisons

All runs used the revised template and requested temperature 0. A model ID was
verified for each provider call; gate abstentions do not invoke the provider.
Matches compare the three response categories in the rule below, not citations.

| Run | Provider calls | Response model ID | Historical comparison: response-type matches | d_C / d_T | Extract |
|---|---:|---|---:|---:|---|
| Python pilot 1 | 20 | `gpt-5.6-sol` | R07: 45/45 | — | [JSON](prompt-sensitivity/raw/python-pilot-1.json) |
| Python pilot 2 | 20 | `gpt-5.6-sol` | R07: 45/45 | — | [JSON](prompt-sensitivity/raw/python-pilot-2.json) |
| C control | 43 | `gpt-5.6-sol` | R01: 44/45 | d_C = 1 | [JSON](prompt-sensitivity/raw/c-control.json) |
| C++ treatment | 42 | `gpt-5.6-sol` | R04: 45/45 | d_T = 0 | [JSON](prompt-sensitivity/raw/cpp-treatment.json) |

The Python pilots matched one another on response type for 45/45 questions,
but their citation sets differed on 2/20 provider-called rows. Against R07,
pilot 1 citation sets matched on 19/20 provider-called rows (17/18 answers),
and pilot 2 on 18/20 (16/18 answers). In the C control, `C2-030` changed from
answer to LLM abstention; no C++ treatment row changed response type.

The extracts contain only question IDs, response categories, cited chunk IDs,
and provider/model/requested-temperature metadata. Full source reports are not
published here: retrieval scores and IDs, index and calibration metadata,
timestamps, prompt hashes, status diagnostics and other report fields were
omitted; no response text is needed for this analysis.

## Decision rule

Registered on **2026-11-01**, before these final control and treatment runs:
**از پیش ثبت‌شده، قبل از اجرای کنترل و تیمار؛ بعد از مشاهده‌ی نتیجه قابل تغییر نیست**

قاعده‌ی تفسیر:
- معیار: فقط نوع پاسخ هر ردیف، با سه مقدار answer، انصراف Gate و انصراف LLM. تغییر مجموعه‌ی citation شمرده نمی‌شود (نوسان citation در pilot حدود ۱۰٪ بود).
- d_C: تعداد ردیف‌های C/e5-large که نوع پاسخشان با گزارش تاریخی R01 فرق کرد. d_T: همین شمارش برای C++/e5-large در برابر R04.
- اگر d_C ≥ 5: provider نسبت به گزارش قدیمی drift دارد؛ فوراً STOP و هیچ مقایسه‌ی تاریخی دیگری معتبر نیست.
- اثر prompt «قابل‌تشخیص» است اگر d_T − d_C ≥ 4 و حداقل ۷۵٪ ردیف‌های تغییرکرده‌ی C++ هم‌جهت باشند (مثلاً انصراف LLM به answer).
- «قابل‌تشخیص نیست» اگر d_T − d_C ≤ 1.
- اگر d_T − d_C برابر ۲ یا ۳ باشد: «نامشخص»؛ فقط گزارش و محدودیت، بدون بازاجرای کامل.

**Decision:** d_C = 1, d_T = 0, so d_T − d_C = −1. Under the rule the prompt
effect is **not detectable** in this comparison. No C++ rows changed, so there
is no direction or proportion of same-direction changes to calculate.

## Provenance and limits

- Prompt change commit: `03dde64b8a82dafb7375a15436ff436fcbfa7671`;
  evaluated code HEAD: `de385be2736e20c5802abdfa89f87c46449f1d56`.
- SHA-256 of the UTF-8 `PROMPT_TEMPLATE` literal, before the change:
  `860cc4804bc2bf4874f3d04c6cf6d63a35749d10ef64879f34720c57601dad70`;
  after: `167fc17f67994569df711936edea76d23bb5f7cbe9e4a8779cfedf1509569f18`.
- The rule was registered before the final C and C++ runs, but was **not blind**:
  historical results, the Python pilots, and an earlier run of those same C and
  C++ comparisons had already been observed.
- These are two treatment slices, not the complete 12-combination matrix.
  Failure to detect an effect does not establish that the prompt has no effect
  elsewhere. The 45 questions are a fixed, non-random set; interpreting a
  binomial confidence bound as a population rate requires additional assumptions.
- Temperature 0 is what the client requested and recorded, not an independently
  verified backend setting. A returned model ID does not prove immutable weights.
