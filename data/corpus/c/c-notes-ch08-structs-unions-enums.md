---
tags: [C, کنکور-ارشد, فصل-11]
---

# فصل ۱۱: ساختارها، union و enum

## ۱۱.۱ — تعریف ساختار (struct)

**ساختار:** نوع داده‌ای که چند عضو **متفاوت‌نوع** را زیر یک نام جمع می‌کند:

```c
struct Student {
    char  name[30];      // عضو
    int   age;
    float gpa;
};                        // ← سمی‌کولن فراموش نشود!

struct Student s1;                       // تعریف متغیر
struct Student s2 = {"Ali", 20, 18.5};   // initializer مثل آرایه
```

**تعریف نوع ≠ تعریف متغیر**

 `struct Student {...};` فقط **نوع جدید** معرفی می‌کند؛ هنوز هیچ متغیری ساخته نشده.
  کلمه `struct` در C اجباری است (برخلاف ++) مگر با typedef.


### دسترسی به اعضا

```c
printf("%s", s1.name);      // عملگر نقطه .
s1.age = 21;
s1.gpa = 19.25f;

struct Student s3 = s1;     // ✓ کپی کامل ساختار مجاز است!
// اما s3 == s1 یا s1.name == "..." ممنوع (مقایسه/انتساب رشته)
```

ساختارهای تودرتو:

```c
struct Date { int day, month, year; };

struct Employee {
    char name[20];
    struct Date hireDate;    // ساختار داخل ساختار
};

struct Employee e;
e.hireDate.year = 1400;      // زنجیره دسترسی
```

---

## ۱۱.۲ — ارسال ساختار به تابع ⭐⭐

سه روش:

```c
void printByValue(struct Student s);       // کپی کامل! (گران برای ساختار بزرگ)
void printByPointer(const struct Student *s);   // آدرس — روش استاندارد
struct Student makeStudent(void);          // برگرداندن ساختار (کپی برگشت)
```

```c
#include <stdio.h>

struct Point { int x, y; };

void move(struct Point *p, int dx, int dy)   // تغییر اصلی ← اشاره‌گر
{
    p->x += dx;        // (*p).x معادل p->x
    p->y += dy;
}

int main(void)
{
    struct Point pt = {2, 3};
    move(&pt, 10, -5);
    printf("%d %d\n", pt.x, pt.y);   // 12 -2
    return 0;
}
```

### دو عملگر دسترسی — حفظ کنید!

| حالت               | عملگر | مثال   |
| ------------------ | ----- | ------ |
| متغیر ساختار       | نقطه  | `pt.x` |
| اشاره‌گر به ساختار | فلش   | `p->x` |

**رابطه دو عملگر**

$$p\text{->}x \;\equiv\; (*p).x$$
پرانتز ضروری است چون `.` اولویت بالاتر از `*` دارد: `*p.x` یعنی `*(p.x)` ← خطا!

تست کلاسیک: `p->x++` یعنی `(*p).x++` (افزایش عضو x)؛ و `(p++)->x` یعنی عضو x شیء فعلی + حرکت p به بعد از استفاده.


---

## ۱۱.۳ — typedef: نام مستعار

```c
typedef unsigned long ulong;      // ulong = نام مستعار

typedef struct {
    int x, y;
} Point;                          // حالا بدون کلمه struct!

Point a = {1, 2};
Point *p = &a;
p->y;                             // 2
```

قالب: `typedef تعریف_موجود نام_جدید;`
کاربردهای رایج: `typedef struct Node NodePtr;` در لیست پیوندی، انواع سایز (`typedef int Score;`).

**typedef vs #define**

```c
typedef char *String;    // String a, b; → هر دو اشاره‌گر ✓
#define String char*     // String a, b; → فقط a اشاره‌گر! b از type char!
```
typedef توسط کامپایلر (معنادار)، define توسط پیش‌پردازنده (متنی) — تله کنکوری مشهور.


---

## ۱۱.۴ — اندازه ساختار و Padding ⭐⭐

کامپایلر بین اعضا **فضای خالی (padding)** می‌گذارد تا هر عضو روی مرز مضرب اندازه‌اش قرار گیرد (سرعت دسترسی CPU):

```c
struct A {
    char c;      // 1 بایت + 3 padding
    int i;       // 4 بایت
};
sizeof(struct A);   // 8 (نه ۵!)

struct B {
    char c;      // 1 + 7 padding
    double d;    // 8
};
sizeof(struct B);   // 16

struct C {           // ترتیب بهینه!
    double d;    // 8
    int i;       // 4
    char c;      // 1 + 3 padding انتهایی برای align کل به ۸
};
sizeof(struct C);   // 16 — همان B ولی با ترتیب منطقی‌تر
// اما:
struct D {
    char a, b;   // 2
    int i;       // 4 (فقط 2 padding)
    double d;    // 8
};                   // 16 — با یک char کمتر از B!
```

قاعده کلی: sizeof(ساختار) ≥ مجموع اعضا؛ ضریبی از align بزرگ‌ترین عضو.

**نکته تست**

«اندازه ساختار = جمع اعضا» **غلط** است. اگر گزینه‌ای گفت همیشه برابر است → غلط. اگر ترتیب اعضا عوض شود اندازه ممکن است تغییر کند!


---

## ۱۱.۵ — عملگرهای بیتی ⭐⭐⭐

روی نمایش دودویی (بیت‌به‌بیت) کار می‌کنند — مستقیماً از سرفصل کنکور:

| عملگر | نام | قواعد | مثال (a=12=`1100`, b=10=`1010`) |
|--------|-----|--------|----------------------------------|
| `&` | AND | هر دو ۱ ← ۱ | `1100 & 1010` = `1000` (۸) |
| `\|` | OR | یکی ۱ ← ۱ | `1100 \| 1010` = `1110` (۱۴) |
| `^` | XOR | **متفاوت** ← ۱ | `1100 ^ 1010` = `0110` (۶) |
| `~` | NOT (یک‌تایی) | وارونه همه بیت‌ها | `~12` = `...0011` = −۱۳ |
| `<<` | شیفت چپ | بیت‌ها به چپ؛ راست صفر | `12 << 1` = `11000` (۲۴) |
| `>>` | شیفت راست | بیت‌ها به راست | `12 >> 2` = `11` (۳) |

### فرمول‌های طلایی

$$x << n = x \times 2^n \qquad x >> n = \lfloor x / 2^n \rfloor \text{ (برای غیرمنفی‌ها)}$$

```c
x & 1            // آخرین بیت: زوج/فرد (۱← فرد)
x & (x - 1)      // پاک کردن کم‌ارزش‌ترین بیتِ ۱
x & ~(1 << k)    // خاموش کردن بیت k
x | (1 << k)     // روشن کردن بیت k
(x >> k) & 1     // خواندن بیت k
x ^ x = 0 ;  x ^ 0 = x ;  x ^ x ^ y = y    // جفت‌زوجی XOR
```

```c
#include <stdio.h>

int main(void)
{
    unsigned char a = 0b1100, b = 0b1010;
    printf("AND=%d OR=%d XOR=%d\n", a & b, a | b, a ^ b);
    printf("shift=%d %d\n", a << 2, a >> 1);
    printf("not=%d\n", ~a);
    return 0;
}
```
**خروجی:** `AND=8 OR=14 XOR=6` / `shift=48 6` / `not=-13`

**یادداشت:** لیترال دودویی مثل `0b1100` در استاندارد C23 پذیرفته شد؛ کامپایلرهای GCC و Clang سال‌هاست آن را به‌عنوان افزونه پشتیبانی می‌کنند.

**تله‌های بیتی**

- اولویت: `==` بالاتر از `&` است! `if (x & 1 == 0)` یعنی `x & (1==0)` یعنی `x & 0` = ۰ — همیشه غلط! بنویسید `(x & 1) == 0`.
- `>>` روی منفی: پیاده‌سازی‌محور (عملاً arithmetic shift).
- شیفت به اندازه ≥ عرض نوع = UB.
- `~` روی unsigned: `~0u` = بزرگ‌ترین عدد؛ روی signed: −۱.


### کاربرد کلاسیک: نمایش باینری عدد

```c
void printBits(unsigned n)
{
    for (int bit = 31; bit >= 0; bit--)
        putchar((n >> bit & 1) ? '1' : '0');
}
```

---

## ۱۱.۶ — union: اشتراک حافظه ⭐⭐

**اتحاد:** همه اعضا در **یک فضای حافظه مشترک** — فقط یکی از اعضا در لحظه معتبر است:

```c
union Data {
    int    i;      // 4 بایت
    float  f;      // 4 بایت
    char   c;      // 1 بایت
};

union Data d;
d.i = 65;              // حالا معتبر
printf("%c", d.c);     // 'A' — همان ۴ بایت از دید char!
d.f = 3.14f;           // حالا i دیگر معتبر نیست!
```

| ویژگی      | struct         | union                     |
| ---------- | -------------- | ------------------------- |
| حافظه      | جمع (+padding) | **بزرگ‌ترین عضو**         |
| اعضای فعال | همه همزمان     | یکی در لحظه               |
| کاربرد     | رکورد داده     | صرفه‌جویی/بازتفسیر بیت‌ها |

```c
union Data u;
sizeof(u);   // 4 (نه 9!)

union Mixed { char c[10]; double d; };
// sizeof = 16: بزرگ‌تر از هر دو عضو (c=10, d=8) ولی مضرب align دابل (۸)
```

### کاربرد معروف: تشخیص Endianness

```c
union Check {
    int i;
    char c;
} ch;

ch.i = 1;
if (ch.c == 1)   // بایت کم‌ارزش در آدرس پایین؟
    printf("Little-endian");   // x86 همین است
else
    printf("Big-endian");
```

---

## ۱۱.۷ — ثابت‌های شمارشی (enum)

نوعی که مقادیرش **ثابت‌های صحیح نام‌دار** هستند:

```c
enum Color { RED, GREEN, BLUE };         // RED=0, GREEN=1, BLUE=2
enum Week { SAT = 1, SUN, MON, TUE };    // ادامه خودکار: SUN=2 ... TUE=4
enum Flags { ON = 4, OFF = 8, AUTO = 16 };// مقداردهی صریح

enum Color c = GREEN;
printf("%d", c);          // 1
printf("%d", BLUE);       // 2
int x = RED + 5;          // 5 — enum واقعاً int است!
```

قواعد:
- شمارش از **۰** شروع می‌شود (مگر صریحاً مقدار بدهید)
- هر عضو = مقدار قبلی + ۱
- مقادیر می‌توانند تکراری باشند (ولی اسم‌ها نه)

کاربرد واقعی — حالت‌های ماشین وضعیت:

```c
typedef enum { IDLE, RUNNING, PAUSED, STOPPED } State;

State s = RUNNING;
switch (s) {
    case IDLE:    printf("Idle"); break;
    case RUNNING: printf("Run");  break;
    ...
}
```

---

## 💻 تمرین‌های کدنویسی فصل ۱۱

**تمرین ۱:** ساختار Rectangle با طول و عرض بسازید. توابع: ورود داده، محاسبه مساحت، محاسبه محیط، و مقایسه دو مستطیل (بزرگ‌تر را برگرداند).

**پاسخ تمرین ۱**

```c
#include <stdio.h>

typedef struct {
    double width, height;
} Rect;

double area(Rect r)
{
    return r.width * r.height;
}

double perimeter(Rect r)
{
    return 2 * (r.width + r.height);
}

const Rect *bigger(const Rect *a, const Rect *b)   // برگرداندن اشاره‌گر
{
    return area(*a) >= area(*b) ? a : b;
}

int main(void)
{
    Rect r1 = {3.0, 4.0}, r2 = {2.5, 6.0};
    const Rect *win = bigger(&r1, &r2);
    printf("%.1f x %.1f wins (area %.2f)\n",
           win->width, win->height, area(*win));
    return 0;
}
```
ترکیب آموزشی: typedef + توابع کوچک + اشاره‌گر const برای ورودی‌های فقط‌خواندنی + ternary.


**تمرین ۲:** تابعی بنویسید `unsigned flipBits(unsigned n, unsigned mask)` که بیت‌هایی از n را که در mask یک هستند، معکوس کند (XOR!) و با مثال n=170 (`10101010`)، mask=240 (`11110000`) تست کنید.

**پاسخ تمرین ۲**

```c
unsigned flipBits(unsigned n, unsigned mask)
{
    return n ^ mask;      // XOR: بیت‌های mask=1 معکوس، بقیه ثابت
}
// تست: 170 ^ 240 = 10101010 ^ 11110000 = 01011010 = 90
```
یک خط! XOR تنها عملگری است که «معکوس‌سازی هدفمند» انجام می‌دهد: 1^1=0 و 0^1=1.


**تمرین ۳:** خروجی برنامه زیر را پیش‌بینی کنید:
```c
#include <stdio.h>

typedef struct {
    short s;
    char tag;
    int v;
} T;

union V {
    T t;
    unsigned bytes[sizeof(T)];
};

int main(void)
{
    printf("%zu\n", sizeof(T));
    printf("%zu\n", sizeof(union V));
    return 0;
}
```

**پاسخ تمرین ۳**

خروجی (سیستم ۶۴بیتی معمول):
```text
12
48
```

تحلیل:
- sizeof(T): short(2)+2pad+char(1)+3pad+int(4) = **۱۲** (align کل = ۴ به‌خاطر int)
- دام تمرین در سطر دوم است! `bytes[sizeof(T)]` یعنی آرایه‌ای با **۱۲ عضو** از نوع unsigned — و هر unsigned چهار بایت است: ۱۲×۴ = ۴۸ بایت!
- union = max(۱۲، ۴۸) = **۴۸**

درس این تمرین: الگوی رایج بازتفسیر بیت‌ها با آرایه بایت باید `unsigned char raw[...]` باشد (هر عنصر ۱ بایت)؛ با unsigned چهاربایتی اندازه منفجر می‌شود. این دقیقاً نوع دامی است که طراح کنکور دوست دارد.
