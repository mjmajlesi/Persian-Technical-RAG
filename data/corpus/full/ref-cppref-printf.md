Source: https://en.cppreference.com/w/c/io/printf
Retrieved: 2026-09-23
License: CC-BY-SA (cppreference.com)

# printf, fprintf, sprintf, snprintf, printf_s, fprintf_s, sprintf_s, snprintf_s - cppreference.com

# printf, fprintf, sprintf, snprintf, printf_s, fprintf_s, sprintf_s, snprintf_s

Defined in header <stdio.h>

```
int printf( const char* format, ... );
```

(1) | (until C99)

```
int printf( const char* restrict format, ... );
```

(since C99)

```
int fprintf( FILE* stream, const char* format, ... );
```

(2) | (until C99)

```
int fprintf( FILE* restrict stream, const char* restrict format, ... );
```

(since C99)

```
int sprintf( char* buffer, const char* format, ... );
```

(3) | (until C99)

```
int sprintf( char* restrict buffer, const char* restrict format, ... );
```

(since C99)

```
int snprintf( char* restrict buffer, size_t bufsz,
              const char* restrict format, ... );
```

(4) | (since C99)

```
int printf_s( const char* restrict format, ... );
```

(5) | (since C11)

```
int fprintf_s( FILE* restrict stream, const char* restrict format, ... );
```

(6) | (since C11)

```
int sprintf_s( char* restrict buffer, rsize_t bufsz,
               const char* restrict format, ... );
```

(7) | (since C11)

```
int snprintf_s( char* restrict buffer, rsize_t bufsz,
                const char* restrict format, ... );
```

(8) | (since C11)

Loads the data from the given locations, converts them to character string equivalents and writes the results to a variety of sinks/streams:

- the conversion specifier %n is present in format

- any of the arguments corresponding to %s is a null pointer

- stream or format or buffer is a null pointer

- bufsz is zero or greater than RSIZE_MAX

- encoding errors occur in any of string and character conversion specifiers

- (for sprintf_s only), the string to be stored in buffer (including the trailing null) would exceed bufsz.

### Parameters

stream | - | output file stream to write to

buffer | - | pointer to a character string to write to

bufsz | - | up to bufsz - 1 characters may be written, plus the null terminator

format | - | pointer to a null-terminated byte string specifying how to interpret the data

... | - | arguments specifying data to print. If any argument after default argument promotions is not the type expected by the corresponding conversion specification (the expected type is the promoted type or a compatible type of the promoted type), or if there are fewer arguments than required by format, the behavior is undefined. If there are more arguments than required by format, the extraneous arguments are evaluated and ignored.

The format string consists of ordinary byte characters (except %), which are copied unchanged into the output stream, and conversion specifications. Each conversion specification has the following format:

- introductory % character.

- (optional) flags that modify the behavior of the conversion:

- -: the result of the conversion is left-justified within the field (by default it is right-justified).

- 0: applicable to floating-point and integer conversions only. Leading zeros are used to pad the field instead of space characters. This flag is ignored if - flag is present. For integer conversions, this flag is ignored if the precision is explicitly specified. For floating-point conversions, this flag is ignored if the value is NaN or infinity. Other conversions using this flag have undefined behavior.

- +: applicable to floating-point and signed integer conversions only. Non-negative numbers are prefixed with a plus character. This flag is ignored by other conversions.

- space: applicable to floating-point and signed integer conversions only. Non-negative numbers are prefixed with a space character. This flag is ignored if + flag is present. This flag is ignored by other conversions.

- #: applicable to floating-point and non-decimal integer conversions only. The alternative form of the conversion is performed. See below for the exact semantics. Other conversions using this flag have undefined behavior.

- (optional) integer value or *: specifies minimum field width. The result is padded with space characters (by default), if required, on the left when right-justified, or on the right if left-justified. In the case when * is used, the width is specified by an additional argument of type int, which appears before the argument to be converted and the argument supplying precision if one is supplied. If the value of the argument is negative, then the - flag is implied and the absolute value used for minimum field width.

- (optional) . followed by non-negative integer number or *: specifies the precision of the conversion. In the case when * is used, the precision is specified by an additional argument of type int, which appears before the argument to be converted, but after the argument supplying minimum field width if one is supplied. If the value of this argument is negative, it is ignored. If neither a number nor * is used, the precision is taken as zero. See below for the exact semantics.

- (optional) length modifier that specifies the size of the argument (in combination with the conversion format specifier, it specifies the type of the corresponding argument).

- conversion format specifier.

If a conversion specification is invalid, the behavior is undefined.

#### Non-numeric

- %: Writes % character. Has no argument. No modifiers supported, full conversion specification must be %%.

- p: Writes a pointer. Argument is a void*, char*, signed char*, or unsigned char*(since C23). Output format is implementation defined.

- c: Writes a character. Argument type depends on the length modifier:

- (none): Argument is an int, which is converted to unsigned char and copied to the output stream.

- l: Argument is a wint_t, which is converted to a wchar_t, put into a null terminated array, and printed with the semantics of %ls.

- s: Write a string. Argument is a pointer to the initial element of an array of characters. Argument type depends on the length modifier:

- (none): Argument is a char*, signed char*, unsigned char*. Characters are copied to the output stream.

- l: Argument is a wchar_t*. String is converted to a narrow string via wcrtomb (with zero-initialized conversion state), and resulting characters copied to the output stream. For the precision modifier and %n specifier, the number of characters refers to the narrow string, not the converted-from wide string.

The precision specifies the maximum number of characters to write. Characters are copied until the maximum is reached or a null terminator is found. The null terminator does not contribute to the number of characters reported by %n.

Even though %c expects int argument, it is safe to pass a char because of the integer promotion that takes place when a variadic function is called.

#### Integer

Let SInt and UInt be respective types determined by the length specifier:

- hh: signed char and unsigned char

(since C99)

- h: short and unsigned short

- (none): int and unsigned

- l: long and unsigned long

- ll: long long and unsigned long long

- j: intmax_t and uintmax_t

- z: signed version of size_t and size_t

- t: ptrdiff_t and unsigned version of ptrdiff_t

(since C99)

- wN: Any signed integer type with bit-width N and any unsigned integer type with bit-width N

- wfN: int_fastN_t and uint_fastN_t

(since C23)

Then:

- d/i: Writes a signed integer in decimal representation. Argument is an SInt.

- u: Writes an unsigned integer in decimal representation. Argument is an UInt.

- x/X: Writes an unsigned integer in hexadecimal representation. Argument is an UInt. The alternative form prefixes 0x if the argument is non-zero. If the format specifier is uppercase, the corresponding output will also be uppercase.

- b: Writes an unsigned integer in binary representation. Argument is an UInt. The alternative form prefixes 0b if the argument is non-zero.

(since C23)

- o: Writes an unsigned integer in octal representation. Argument is an UInt. The alternative form increases the precision as much as is needed for the first digit written to be zero.

- n: Returns the number of characters written so far by this call to the function, including minimum field width padding. Argument is an SInt* to write the result to. Only supported modifier is length modifier.

The precision specifies the minimum number of digits to write, leading zeros will be written if necessary. If unspecified, a precision of 1 is used. If precision is 0 and the argument is 0, no digits will be written (the plus or space character is still written if the + or space flag is specified).

The correct conversion specifications for the fixed-width character types (int8_t, etc) are defined in the header <inttypes.h> (although PRIdMAX, PRIuMAX, etc is synonymous with %jd, %ju, etc).

The memory-writing conversion specifier %n is a common target of security exploits where format strings depend on user input and is not supported by the bounds-checked printf_s family of functions.

There is a sequence point after the action of each conversion specifier; this permits storing multiple %n results in the same variable or, as an edge case, printing a string modified by an earlier %n within the same call.

#### Floating-point

The argument type is determined by the length specifier:

- (none): double

- l: double

(since C99)

- L: long double

- H: _Decimal32

- D: _Decimal64

- DD: _Decimal128

(since C23)

Then:

- If the argument is infinity, then inf or infinity is written. Which one is used is implementation defined.

- If the argument is not-a-number, then nan or nan(char_sequence) is written. Which one is used is implementation defined.

Otherwise:

- f/F: Writes a floating-point in decimal notation [-]ddd.ddd. The precision specifies the number of decimal places, trailing zeros will be written if necessary. If unspecified, a precision of 6 is used.

- e/E: Writes a floating-point in decimal exponent notation [-]d.ddde±dd. If the exponent is less than 10, it is written with a leading zero. The precision specifies the number of decimal places, trailing zeros will be written if necessary. If unspecified, a precision of 6 is used.

- g/G: Writes a floating-point in decimal or decimal exponent notation, depending on the argument and precision.

Let P = max(0, precision - 1), or 5 if precision is unspecified.

Let EXP be the exponent written if %e were the specification.

- If -4 ≤ EXP ≤ P, then the argument is written as if the f/F format specifier was used with precision P - EXP.

- Otherwise, the argument is written as if the e/E format specifier was used with precision P.

- a/A: Writes a floating-point in hexadecimal exponent notation [-]0xh.hhhp±d. The precision specifies the number of digits following the decimal point, trailing zeros will be written if necessary.

- If the argument type is double or long double:

- If the precision is unspecified:

- If FLT_RADIX is a power of 2, the exact value is printed.

- Otherwise, enough digits are printed to distinguish the number from any other value of the argument type, except that trailing zeros may be omitted.

- Otherwise, for decimal type arguments:

Let qmin,qmax be:

- -101, 90 if argument type is _Decimal32

- -398, 369 if argument type is _Decimal64

- -6176, 6111 if argument type is _Decimal128

Let the argument be expressed with integers s,c,q as s × c × 10q where:

- c ≥ 0,

- s is -1 or 1,

- qmin ≤ q ≤ qmax.

Let n be the number of significant digits in c.

Let P be the precision.

- If P is specified and 0 < P < n, then the argument is rounded to P decimal digits, with unbounded exponent range, such that c is a P-digit integer

- If 0 ≤ -q ≤ n + 5, then the argument is written with the style of the f/F format specifier used with precision -q.

- Otherwise, the argument is written with the style of the e/E format specifier used with precision n - 1, except that:

- If c = 0, then q is written for the exponent.

- No leading zero is written for the exponent.

(since C23)

There is exactly one digit before the decimal place, but it is unspecified how this digit is chosen. For example, 0x1.fp+6 and 0xf.6p+3 are both valid outputs for an argument of 123.0 with precision 1.

(since C99)

The alternative form writes a decimal point even if precision is 0. If the format specifier is uppercase, the corresponding output will also be uppercase.

### Return value

### Notes

The C standard and POSIX specify that the behavior of sprintf and its variants is undefined when an argument overlaps with the destination buffer. Example:

```
sprintf(dst, "%s and %s", dst, t); // <- broken: undefined behavior
```

POSIX specifies that errno is set on error. It also specifies additional conversion specifications, most notably support for argument reordering (n$ immediately after % indicates nth argument).

Calling snprintf with zero bufsz and null pointer for buffer is useful to determine the necessary buffer size to contain the output:

```
const char fmt[] = "sqrt(2) = %f";
int sz = snprintf(NULL, 0, fmt, sqrt(2));
char buf[sz + 1]; // note +1 for terminating null byte
snprintf(buf, sizeof buf, fmt, sqrt(2));
```

snprintf_s, just like snprintf, but unlike sprintf_s, will truncate the output to fit in bufsz - 1.

### Example

```
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>

int main(void)
{
    const char* s = "Hello";
    printf("Strings:\n"); // same as puts("Strings");
    printf(" padding:\n");
    printf("\t[%10s]\n", s);
    printf("\t[%-10s]\n", s);
    printf("\t[%*s]\n", 10, s);
    printf(" truncating:\n");
    printf("\t%.4s\n", s);
    printf("\t%.*s\n", 3, s);

    printf("Characters:\t%c %%\n", 'A');

    printf("Integers:\n");
    printf("\tDecimal:\t%i %d %.6i %i %.0i %+i %i\n",
                         1, 2,   3, 0,   0,  4,-4);
    printf("\tHexadecimal:\t%x %x %X %#x\n", 5, 10, 10, 6);
    printf("\tOctal:\t\t%o %#o %#o\n", 10, 10, 4);

    printf("Floating-point:\n");
    printf("\tRounding:\t%f %.0f %.32f\n", 1.5, 1.5, 1.3);
    printf("\tPadding:\t%05.2f %.2f %5.2f\n", 1.5, 1.5, 1.5);
    printf("\tScientific:\t%E %e\n", 1.5, 1.5);
    printf("\tHexadecimal:\t%a %A\n", 1.5, 1.5);
    printf("\tSpecial values:\t0/0=%g 1/0=%g\n", 0.0 / 0.0, 1.0 / 0.0);

    printf("Fixed-width types:\n");
    printf("\tLargest 32-bit value is %" PRIu32 " or %#" PRIx32 "\n",
                                     UINT32_MAX,     UINT32_MAX );
}
```

Possible output:

```
Strings:
 padding:
        [     Hello]
        [Hello     ]
        [     Hello]
 truncating:
        Hell
        Hel
Characters:     A %
Integers:
        Decimal:        1 2 000003 0  +4 -4
        Hexadecimal:    5 a A 0x6
        Octal:          12 012 04
Floating-point:
        Rounding:       1.500000 2 1.30000000000000004440892098500626
        Padding:        01.50 1.50  1.50
        Scientific:     1.500000E+00 1.500000e+00
        Hexadecimal:    0x1.8p+0 0X1.8P+0
        Special values: 0/0=-nan 1/0=inf
Fixed-width types:
        Largest 32-bit value is 4294967295 or 0xffffffff
```

### References

- C23 standard (ISO/IEC 9899:2024):

- 7.21.6.1 The fprintf function (p: TBD)

- 7.21.6.3 The printf function (p: TBD)

- 7.21.6.5 The snprintf function (p: TBD)

- 7.21.6.6 The sprintf function (p: TBD)

- K.3.5.3.1 The fprintf_s function (p: TBD)

- K.3.5.3.3 The printf_s function (p: TBD)

- K.3.5.3.5 The snprintf_s function (p: TBD)

- K.3.5.3.6 The sprintf_s function (p: TBD)

- C17 standard (ISO/IEC 9899:2018):

- 7.21.6.1 The fprintf function (p: 225-230)

- 7.21.6.3 The printf function (p: 236)

- 7.21.6.5 The snprintf function (p: 237)

- 7.21.6.6 The sprintf function (p: 237)

- K.3.5.3.1 The fprintf_s function (p: 430)

- K.3.5.3.3 The printf_s function (p: 432)

- K.3.5.3.5 The snprintf_s function (p: 432-433)

- K.3.5.3.6 The sprintf_s function (p: 433)

- C11 standard (ISO/IEC 9899:2011):

- 7.21.6.1 The fprintf function (p: 309-316)

- 7.21.6.3 The printf function (p: 324)

- 7.21.6.5 The snprintf function (p: 325)

- 7.21.6.6 The sprintf function (p: 325-326)

- K.3.5.3.1 The fprintf_s function (p: 591)

- K.3.5.3.3 The printf_s function (p: 593-594)

- K.3.5.3.5 The snprintf_s function (p: 594-595)

- K.3.5.3.6 The sprintf_s function (p: 595-596)

- C99 standard (ISO/IEC 9899:1999):

- 7.19.6.1 The fprintf function (p: 274-282)

- 7.19.6.3 The printf function (p: 290)

- 7.19.6.5 The snprintf function (p: 290-291)

- 7.19.6.6 The sprintf function (p: 291)

- C89/C90 standard (ISO/IEC 9899:1990):

- 4.9.6.1 The fprintf function

- 4.9.6.3 The printf function

- 4.9.6.5 The sprintf function

### See also

wprintffwprintfswprintfwprintf_sfwprintf_sswprintf_ssnwprintf_s(C95)(C95)(C95)(C11)(C11)(C11)(C11) | prints formatted wide character output to stdout, a file stream or a buffer  (function) [edit]

vprintfvfprintfvsprintfvsnprintfvprintf_svfprintf_svsprintf_svsnprintf_s(C99)(C11)(C11)(C11)(C11) | prints formatted output to stdout, a file stream or a buffer using variable argument list  (function) [edit]

fputs | writes a character string to a file stream  (function) [edit]

scanffscanfsscanfscanf_sfscanf_ssscanf_s(C11)(C11)(C11) | reads formatted input from stdin, a file stream or a buffer  (function) [edit]

C++ documentation for printf, fprintf, sprintf, snprintf
