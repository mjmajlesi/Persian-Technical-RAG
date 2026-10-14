---
tags: [C, کنکور-ارشد, فصل-13]
---

# فصل ۱۳: پرونده‌ها (فایل)

## ۱۳.۱ — جویبارها (Streams) و FILE

در C همه ورودی/خروجی از طریق **جویبار (stream)** انجام می‌شود: جریان انتزاعی داده. سه استریم استاندارد که خودکار باز می‌شوند:

| جویبار   | اتصال           | کاربرد          |
| -------- | --------------- | --------------- |
| `stdin`  | ورودی استاندارد | scanf، getchar  |
| `stdout` | خروجی استاندارد | printf، putchar |
| `stderr` | خطای استاندارد  | پیام‌های خطا    |

برای کار با فایل، اشاره‌گر از نوع `FILE*` (تعریف‌شده در `<stdio.h>`) به‌عنوان «دستگیره» (handle) فایل استفاده می‌شود:

```c
FILE *fp;        // دستگیره فایل — همه توابع فایل با همین کار می‌کنند
```

FILE شامل بافر، موقعیت فعلی، وضعیت خطا/پایان و... است — شما فقط اشاره‌گر را بین توابع جابه‌جا می‌کنید.

---

## ۱۳.۲ — باز و بستن فایل

```c
#include <stdio.h>

int main(void)
{
    FILE *fp = fopen("data.txt", "r");   // (نام فایل، حالت)

    if (fp == NULL) {                    // همیشه چک کنید!
        fprintf(stderr, "Cannot open file!\n");
        return 1;
    }

    /* ... کار با فایل ... */

    fclose(fp);                          // آزادسازی + flush بافر
    return 0;
}
```

**NULL یعنی شکست**

fopen در صورت موفقیت اشاره‌گر معتبر و در **شکست NULL** برمی‌گرداند (فایل وجود ندارد، دسترسی ندارید، مسیر غلط...). استفاده از fp بدون چک = کرش تضمینی.


### جدول حالت‌های بازکردن ⭐ (حفظ اجباری)

| حالت | معنا | اگر فایل موجود؟ | اگر نبود؟ | موقعیت اولیه |
|-------|------|------------------|-----------|---------------|
| `"r"` | خواندن | باز می‌شود | **NULL** | ابتدای فایل |
| `"w"` | نوشتن | **محتوا پاک می‌شود!** | ساخته می‌شود | ابتدا |
| `"a"` | الحاق (append) | حفظ می‌شود | ساخته می‌شود | انتهای فایل |
| `"r+"` | خواندن+نوشتن | باز | NULL | ابتدا |
| `"w+"` | خواندن+نوشتن | پاک می‌شود | ساخته | ابتدا |
| `"a+"` | خواندن+الحاق | حفظ | ساخته | نوشتن همیشه انتها |
| `"rb"`, `"wb"`, ... | حالت **باینری** | — | — | — |

**تله‌های کلاسیک**

- `"w"` روی فایل موجود = **پاک شدن کامل محتوا** — باز همیشه خطرناک است!
- `"a"` نوشتن را همیشه به انتها می‌فرستد (حتی بعد از fseek)
- `r+` نوشتن را از هر جایی می‌گذارد ولی فایل را نمی‌سازد
- پسوند b برای فایل باینری است (در لینوکس بی‌اثر ولی استاندارد است)


---

## ۱۳.۳ — نوشتن و خواندن ترتیبی

### نسخه‌های فایلیِ توابع آشنا

| تابع | کار | معادل |
|-------|-----|--------|
| `fprintf(fp, "fmt", ...)` | چاپ قالب‌بندی‌شده در فایل | printf |
| `fscanf(fp, "fmt", ...)` | خواندن قالب‌بندی‌شده از فایل | scanf |
| `fputc(ch, fp)` / `putc` | نوشتن یک کاراکتر | putchar |
| `fgetc(fp)` / `getc` | خواندن یک کاراکتر (int! برای EOF) | getchar |
| `fputs(str, fp)` | نوشتن رشته (بدون \n خودکار) | puts |
| `fgets(buf, n, fp)` | خواندن یک خط (حداکثر n−1) | gets (امن!) |
| `fwrite(buf, size, n, fp)` | نوشتن باینری | — |
| `fread(buf, size, n, fp)` | خواندن باینری | — |

### مثال کامل: نوشتن و خواندن

```c
#include <stdio.h>

int main(void)
{
    /* --- نوشتن --- */
    FILE *fp = fopen("students.txt", "w");
    if (!fp) { perror("open"); return 1; }

    fprintf(fp, "Ali 18.25\n");
    fprintf(fp, "Sara 19.50\n");
    fclose(fp);

    /* --- خواندن --- */
    fp = fopen("students.txt", "r");
    if (!fp) { perror("open"); return 1; }

    char name[30];
    double gpa;
    while (fscanf(fp, "%29s %lf", name, &gpa) == 2) {   // الگوی استاندارد!
        printf("%-10s %.2f\n", name, gpa);
    }
    fclose(fp);
    return 0;
}
```

**خروجی:**
```text
Ali        18.25
Sara       19.50
```

**الگوی طلایی حلقه خواندن**

```c
while (fscanf(fp, "%d", &x) == 1) { ... }
// یا:
while (fscanf(fp, "%d", &x) != EOF) { ... }
```
مقدار برگشتی را **همیشه** چک کنید — وقتی فایل تمام شود fscanf برمی‌گرداند EOF (یا کمتر از تعداد مورد انتظار).
الگوی غلط رایج: `while (!feof(fp)) { fscanf(...); }` ← آخرین داده **دوبار** پردازش می‌شود! (چون feof فقط «بعد از» تلاش ناموفق خواندن true می‌شود.)


### خواندن کاراکتربه‌کاراکتر

```c
int ch;                              // int نه char — برای EOF!
while ((ch = fgetc(fp)) != EOF)      // الگوی کلاسیک C
    putchar(ch);
```

**چرا int؟**

EOF ثابتی برابر **−۱** است. اگر متغیر char باشد (unsigned در بعضی سیستم‌ها)، EOF هرگز تشخیص داده نمی‌شود یا کاراکتر معتبر 0xFF با EOF اشتباه می‌شود. به همین دلیل fgetc نوع int برمی‌گرداند.


### fgets — خواندن امن خط‌به‌خط

```c
char line[100];
while (fgets(line, sizeof line, fp) != NULL) {
    printf("%s", line);          // newline داخل line هست!
}
```

- حداکثر n−۱ کاراکتر می‌خواند (بقیه برای تکرار بعدی می‌ماند) — **سرریز ندارد**
- اگر خط کوتاه باشد، `\n` هم داخل رشته می‌آید (گاهی باید حذفش کنید)
- در پایان فایل NULL برمی‌گرداند

---

## ۱۳.۴ — تشخیص پایان و خطا

| تابع | کار |
|-------|-----|
| `feof(fp)` | غیرصفر اگر **قبلاً** به انتهای فایل خورده باشد |
| `ferror(fp)` | غیرصفر اگر خطای خواندن/نوشتن رخ داده |
| `clearerr(fp)` | پاک کردن پرچم‌های خطا/EOF |
| `perror("msg")` | چاپ پیام خطای سیستم آخر |

**feof درست چطور استفاده می‌شود؟**

feof «آینده» را نمی‌گوید؛ فقط می‌گوید «تلاش قبلی به EOF خورده». پس:
- ✓ درست: `while ((ch = fgetc(fp)) != EOF)` یا `while (fgets(...))`
- ✗ غلط: `while (!feof(fp)) { fscanf(...); }` ← تکرار اضافی روی آخرین داده


---

## ۱۳.۵ — دسترسی تصادفی (اختیاری سرفصل ولی کنکوری!)

هر فایل باز یک «مکان‌نما» دارد. توابع جابه‌جایی:

```c
long pos = ftell(fp);          // موقعیت فعلی (بایت از ابتدا)
rewind(fp);                    // برگشت به ابتدا
fseek(fp, offset, origin);     // پرش
```

| origin | معنا |
|--------|------|
| `SEEK_SET` | از ابتدای فایل |
| `SEEK_CUR` | از موقعیت فعلی |
| `SEEK_END` | از انتهای فایل |

```c
fseek(fp, 0, SEEK_SET);        // = rewind(fp)
fseek(fp, 0, SEEK_END);
long size = ftell(fp);         // ← ترفند استاندارد اندازه فایل!
fseek(fp, -10L, SEEK_END);     // ده بایت مانده به انتها
fseek(fp, 5L, SEEK_CUR);       // پنج بایت جلوتر
```

### فایل باینری و رکورد

```c
struct Rec { int id; double score; };

struct Rec r = {7, 18.5};
FILE *fp = fopen("data.bin", "wb");
fwrite(&r, sizeof(struct Rec), 1, fp);      // کل ساختار یکجا!
fclose(fp);

/* خواندن رکورد n-ام مستقیم — قدرت دسترسی تصادفی */
fp = fopen("data.bin", "rb");
fseek(fp, (long)(n - 1) * sizeof(struct Rec), SEEK_SET);
fread(&r, sizeof(struct Rec), 1, fp);
```

fwrite/fread داده را **همان‌طور که در حافظه است** (باینری) می‌نویسند — فشرده و سریع ولی غیرقابل خواندن با ادیتور.

---

## 💻 تمرین‌های کدنویسی فصل ۱۳

**تمرین ۱:** برنامه‌ای بنویسید که یک فایل متنی را بخواند و تعداد خطوط، کلمات و کاراکترهای آن را گزارش دهد (شبیه wc لینوکس).

**پاسخ تمرین ۱**

```c
#include <stdio.h>
#include <ctype.h>

int main(void)
{
    FILE *fp = fopen("input.txt", "r");
    if (!fp) { perror("input.txt"); return 1; }

    int lines = 0, words = 0, chars = 0, inWord = 0;
    int ch;

    while ((ch = fgetc(fp)) != EOF) {
        chars++;
        if (ch == '\n')
            lines++;
        if (isspace(ch)) {
            inWord = 0;
        } else if (!inWord) {
            inWord = 1;
            words++;
        }
    }
    fclose(fp);

    printf("%d lines %d words %d chars\n", lines, words, chars);
    return 0;
}
```
یک گذر، سه شمارنده. الگوی inWord از فصل رشته‌ها — این بار روی جویبار.


**تمرین ۲:** ساختار Student را در فایل باینری ذخیره کنید؛ سپس برنامه‌ای بنویسید رکورد n-ام را با دسترسی تصادفی بخواند و ویرایش کند.

**پاسخ تمرین ۲**

```c
#include <stdio.h>

typedef struct {
    int id;
    char name[30];
    double gpa;
} Student;

void updateRecord(const char *fname, int n, const Student *newData)
{
    FILE *fp = fopen(fname, "r+b");          // خواندن+نوشتن باینری
    if (!fp) { perror(fname); return; }

    fseek(fp, (long)(n - 1) * sizeof(Student), SEEK_SET);
    fwrite(newData, sizeof(Student), 1, fp);  // overwrite همان رکورد
    fclose(fp);
}

int main(void)
{
    Student s1 = {1, "Ali", 18.25}, s2 = {2, "Sara", 19.5};
    FILE *fp = fopen("students.bin", "wb");
    fwrite(&s1, sizeof(Student), 1, fp);
    fwrite(&s2, sizeof(Student), 1, fp);
    fclose(fp);

    Student fixed = {2, "Sara", 20.0};
    updateRecord("students.bin", 2, &fixed);

    /* اثبات: خواندن رکورد دوم */
    fp = fopen("students.bin", "rb");
    Student r;
    fseek(fp, sizeof(Student), SEEK_SET);
    fread(&r, sizeof(Student), 1, fp);
    printf("%s: %.1f\n", r.name, r.gpa);      // Sara: 20.0
    fclose(fp);
    return 0;
}
```
فرمول کلیدی: آدرس رکورد n-ام = `(n-1) * sizeof(Rec)` از SEEK_SET. حالت "r+b" اجازه خواندن و بازنویسی درجا می‌دهد.
