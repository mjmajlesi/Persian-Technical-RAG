---
tags: [C, کنکور-ارشد, فصل-12]
---

# فصل ۱۲: آشنایی با ++C

## ۱۲.۱ — ورودی/خروجی با جویبارها (Streams)

در ++C به‌جای printf/scanf از **cin** و **cout** استفاده می‌شود (سرآیند `<iostream>`):

```cpp
#include <iostream>
using namespace std;

int main()
{
    int age;
    double gpa;
    cout << "Enter age and gpa: ";   // چاپ با <<
    cin >> age >> gpa;               // خواندن با >> (بدون &!)
    cout << "Age: " << age << " GPA: " << gpa << endl;
    return 0;
}
```

| مفهوم C               | معادل ++C                                 |
| --------------------- | ----------------------------------------- |
| `printf("%d", x)`     | `cout << x`                               |
| `scanf("%d", &x)`     | `cin >> x` (بدون & !)                     |
| `"\n"`                | `endl` (خط جدید + flush)                  |
| `%f %.2f`             | `fixed << setprecision(2)` با `<iomanip>` |
| `stdin/stdout/stderr` | `cin/cout/cerr`                           |

**چرا >> و << ؟**

این‌ها همان عملگرهای شیفت‌اند که **سربارگذاری** شده‌اند تا با داده‌ها کار کنند — خودِ نمونه‌ای از قدرت operator overloading در ++C. جهت فلش جهت جریان داده را نشان می‌دهد: `cout << x` یعنی x به سمت خروجی.


قالب‌بندی:

```cpp
#include <iomanip>
cout << fixed << setprecision(2) << 3.14159;   // 3.14
cout << setw(8) << 42;                          // "      42" (عرض میدان مثل %8d)
```

---

## ۱۲.۲ — فضای نام (namespace) و ::

**فضای نام:** ظرفی برای گروه‌بندی شناسه‌ها و جلوگیری از تداخل نام‌ها:

```cpp
namespace Math {
    const double PI = 3.14159;
    double square(double x) { return x * x; }
}

namespace Physics {
    const double G = 9.8;
}

int main()
{
    cout << Math::PI;              // :: = عملگر تغییر حوزه (scope resolution)
    cout << Physics::G;
    return 0;
}
```

سه راه استفاده:

```cpp
using namespace std;        // ۱) همه چیز از std — راحت ولی آلوده‌کننده
using std::cout;            // ۲) فقط cout
std::cout << "x";           // ۳) نام کامل هر بار
```

**نکته :: بدون namespace**

`::x` (خالی از چپ) یعنی متغیر **سراسری** — وقتی متغیر محلی همنام سایه انداخته:
```cpp
int x = 10;                 // سراسری
int main() {
    int x = 5;              // محلی
    cout << x;              // 5
    cout << ::x;            // 10 — سراسری!
}
```


---

## ۱۲.۳ — فراخوانی با ارجاع (Reference) ⭐⭐⭐

**ارجاع (reference):** نام مستعار برای متغیر موجود — با `&` در تعریف:

```cpp
void swap(int &a, int &b)     // ارجاع! بدون * و بدون & در فراخوانی
{
    int t = a;
    a = b;
    b = t;
}

int main()
{
    int x = 1, y = 9;
    swap(x, y);               // ساده مثل C — ولی اثر واقعی!
    cout << x << y;           // 91
}
```

| روش | امضا C | امضا ++C | فراخوانی | تغییر اصلی؟ |
|------|---------|-----------|-----------|--------------|
| با مقدار | `f(int a)` | همان | `f(x)` | خیر |
| با اشاره‌گر | `f(int *a)` | همان | `f(&x)` | بله |
| با ارجاع | — | `f(int &a)` | `f(x)` | **بله** |

قواعد ارجاع:
- ارجاع باید **هنگام تعریف** مقداردهی شود و هرگز مقصدش عوض نمی‌شود
- ارجاع «اشاره‌گر ثابتِ خودکار dereference» است
- `const int &r` = ارجاع فقط‌خواندنی (برای پارامترهای بزرگ: `const string &s`)

```cpp
int x = 5;
int &r = x;      // r نام مستعار x
r = 100;         // x = 100!
int *p = &r;     // &r همان &x است!
```

**تله & در C در مقابل ++C**

- C: `int &r = x;` **خطای کامپایل** (در فراخوانی/تعریف متغیر)
- ++C: معتبر — ارجاع!
- اما در **هر دو** زبان، `&x` در عبارت یعنی «آدرس x»
تست‌ها معمولاً می‌پرسند «این کد در C اجرا می‌شود یا فقط ++C؟»


---

## ۱۲.۴ — توابع درون‌خطی (inline)

پیشنهاد به کامپایلر: **بدنه تابع را در محل فراخوانی کپی کن** (حذف overhead فراخوانی):

```cpp
inline int cube(int s)
{
    return s * s * s;
}

int main()
{
    cout << cube(3);    // ممکن است به 27 جایگزینی شود!
}
```

- مثل macro است ولی **توسط کامپایلر و با چک نوع** — امن‌تر از `#define`
- کامپایلر می‌تواند پیشنهاد را رد کند (inline فقط درخواست است)
- مناسب توابع کوچک پرتکرار

```cpp
#define SQ(x) ((x)*(x))    // خطرناک: SQ(a+1) با side-effect خراب می‌شود
inline int sq(int x) { return x * x; }   // امن
```

---

## ۱۲.۵ — آرگومان‌های پیش‌فرض

پارامتر می‌تواند مقدار پیش‌فرض داشته باشد؛ اگر فراخواننده نفرستد، پیش‌فرض استفاده می‌شود:

```cpp
double power(double base, int exp = 2)   // پیش‌فرض: مربع
{
    double r = 1;
    for (int i = 0; i < exp; i++)
        r *= base;
    return r;
}

power(3);        // 9   (exp=2)
power(3, 3);     // 27  (exp=3)
```

قواعد:
- پیش‌فرض‌ها باید از **راست** شروع شوند: `f(int a, int b=2, int c=5)` ✓ ولی `f(int a=1, int b)` ✗
- دلیل: فراخوانی `f(7)` مبهم می‌شد
- پیش‌فرض در **اعلان (prototype)** نوشته می‌شود، نه تعریف (یا فقط یکی از آن‌ها)

---

## ۱۲.۶ — سربارگذاری توابع (Function Overloading) ⭐⭐⭐

چند تابع **همنام** با **پارامترهای متفاوت** — کامپایلر از روی آرگومان‌ها تشخیص می‌دهد:

```cpp
#include <iostream>
using namespace std;

int    add(int a, int b)        { return a + b; }
double add(double a, double b)  { return a + b; }
int    add(int a, int b, int c) { return a + b + c; }

int main()
{
    cout << add(2, 3);        // int,int → نسخه اول: 5
    cout << add(2.5, 3.5);    // double,double → نسخه دوم: 6
    cout << add(1, 2, 3);     // سه آرگومان → نسخه سوم: 6
}
```

**تشخیص امضا (signature) = نام + تعداد + ترتیب + نوع پارامترها**
نوع برگشتی در سربارگذاری **نقشی ندارد**!

```cpp
int    f(int x);
double f(int x);     // ❌ خطا! فقط نوع برگشتی فرق دارد

int    g(int x);
int    g(double x);  // ✓ معتبر
```

**ابهام (Ambiguity)**

```cpp
void h(int x);
void h(double x);
h(5L);          // long به هر دو قابل تبدیل → ابهام → خطای کامپایل!
```
تبدیل‌های استاندارد چندگانه هم‌ارز ← کامپایلر نمی‌تواند تصمیم بگیرد.


سربارگذاری در C **وجود ندارد** — این **یکی از تفاوت‌های اصلی C/++C است**
(در C باید نام‌های جدا می‌دادید: `addInts`, `addDoubles`).

---

## ۱۲.۷ — مقدمه کلاس‌ها (Classes)

**کلاس:** ساختار + **توابع عضو** + کنترل دسترسی — پایه شیءگرایی:

```cpp
#include <iostream>
#include <string>
using namespace std;

class Student {
private:                        // خارج از کلاس دسترسی ندارد!
    string name;
    double gpa;

public:                         // همه‌جا قابل دسترسی
    void setData(string n, double g) {
        name = n;               // توابع عضو به private دسترسی دارند
        gpa = g;
    }
    void print() {
        cout << name << ": " << gpa << endl;
    }
};

int main()
{
    Student s;                  // شیء (object) = نمونه کلاس
    s.setData("Ali", 19.5);
    s.print();                  // Ali: 19.5
    // s.name = "X";            // ❌ خطا! name خصوصی است
}
```

### سازنده (Constructor)

تابع ویژه با **نام کلاس** که هنگام ساخته شدن شیء **خودکار** اجرا می‌شود؛ **بدون نوع برگشتی**:

```cpp
class Point {
    int x, y;
public:
    Point(int px = 0, int py = 0) {   // سازنده (با پیش‌فرض)
        x = px;
        y = py;
    }
    void print() { cout << "(" << x << "," << y << ")"; }
};

Point a;         // سازنده پیش‌فرض: (0,0)
Point b(3, 7);   // (3,7)
```

| ویژگی         | struct در C    | class در ++C                                       |
| ------------- | -------------- | -------------------------------------------------- |
| داده          | فقط داده       | داده + توابع عضو                                   |
| دسترسی        | همه public     | پیش‌فرض **private** (در struct ++C پیش‌فرض public) |
| سازنده        | ندارد          | دارد                                               |
| ارسال به تابع | مقدار/اشاره‌گر | + ارجاع                                            |

**نکات کنکوری کلاس**

- اعضای کلاس به‌طور پیش‌فرض **private** هستند (در struct پیش‌فرض public!)
- سازنده هم‌نام کلاس است و نوع برگشتی ندارد (حتی void هم نه!)
- سازنده هنگام تعریف شیء خودکار فراخوانی می‌شود
- ارسال/دریافت اشیاء به توابع مثل ساختارها: با مقدار (کپی)، اشاره‌گر یا ارجاع


---

## ۱۲.۸ — خلاصه تفاوت‌های کلیدی C و ++C

| ویژگی | C | ++C |
|--------|---|------|
| ورودی/خروجی | printf/scanf | cin/cout (+ printf هم دارد) |
| فراخوانی با ارجاع | ندارد (فقط اشاره‌گر) | `int &r` |
| سربارگذاری توابع | ندارد | دارد |
| آرگومان پیش‌فرض | ندارد | دارد |
| inline | C99 macro-like | کلمه inline |
| namespace | ندارد | دارد |
| کلاس/OOP | ندارد | دارد |
| کامنت // | C99+ | از ابتدا |

---

## 💻 تمرین‌های کدنویسی فصل ۱۲

**تمرین ۱:** با ++C برنامه‌ای بنویسید که دو مختصات نقطه را بگیرد و فاصله تا مبدأ را با سه نسخه سربارگذاری‌شده `dist` محاسبه کند: (x,y)، (x,y,z) و (نقطه، نقطه).

**پاسخ تمرین ۱**

```cpp
#include <iostream>
#include <cmath>
using namespace std;

double dist(double x, double y)
{
    return sqrt(x*x + y*y);
}

double dist(double x, double y, double z)
{
    return sqrt(x*x + y*y + z*z);
}

double dist(double x1, double y1, double x2, double y2)
{
    return dist(x2 - x1, y2 - y1);   // استفاده مجدد!
}

int main()
{
    cout << dist(3, 4) << endl;          // 5
    cout << dist(1, 2, 2) << endl;       // 3
    cout << dist(1, 1, 4, 5) << endl;    // 5
    return 0;
}
```


**تمرین ۲:** کلاس Counter با سازنده، شمارنده اشیاء زنده (static member) و مخرب بنویسید که در هر ساخت/نابودی گزارش دهد.

**پاسخ تمرین ۲**

```cpp
#include <iostream>
using namespace std;

class Counter {
    static int alive;              // مشترک بین همه اشیاء
public:
    Counter()  { alive++; cout << "born, alive=" << alive << endl; }
    ~Counter() { alive--; cout << "died, alive=" << alive << endl; }
};

int Counter::alive = 0;            // تعریف عضو استاتیک

int main()
{
    Counter a, b;
    {
        Counter c;
    }                               // c اینجا نابود می‌شود
    return 0;                       // سپس b و a (به ترتیب معکوس ساخت)
}
```
خروجی:
```text
born, alive=1
born, alive=2
born, alive=3
died, alive=2      ← c پایان بلوک
died, alive=1      ← b
died, alive=0      ← a
```
دو قاعده مهم: مخرب هر شیء دقیقاً **یک بار** اجرا می‌شود، و ترتیب مخربی **معکوس ترتیب ساخت** است (پشته‌ای).
