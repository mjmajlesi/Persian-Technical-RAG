Source: https://en.cppreference.com/w/c/io/fscanf
Retrieved: 2026-09-23
License: CC-BY-SA (cppreference.com)

# scanf, fscanf, sscanf, scanf_s, fscanf_s, sscanf_s - cppreference.com

# scanf, fscanf, sscanf, scanf_s, fscanf_s, sscanf_s

Defined in header <stdio.h>

```
int scanf( const char* format, ... );
```

(1) | (until C99)

```
int scanf( const char* restrict format, ... );
```

(since C99)

```
int fscanf( FILE* stream, const char* format, ... );
```

(2) | (until C99)

```
int fscanf( FILE* restrict stream, const char* restrict format, ... );
```

(since C99)

```
int sscanf( const char* buffer, const char* format, ... );
```

(3) | (until C99)

```
int sscanf( const char* restrict buffer, const char* restrict format, ... );
```

(since C99)

```
int scanf_s(const char* restrict format, ...);
```

(4) | (since C11)

```
int fscanf_s(FILE* restrict stream, const char* restrict format, ...);
```

(5) | (since C11)

```
int sscanf_s(const char* restrict buffer, const char* restrict format, ...);
```

(6) | (since C11)

Reads data from a variety of sources, interprets it according to format and stores the results into given locations.

- any of the arguments of pointer type is a null pointer

- format, stream, or buffer is a null pointer

- the number of characters that would be written by %c, %s, or %[, plus the terminating null character, would exceed the second (rsize_t) argument provided for each of those conversion specifiers

- optionally, any other detectable error, such as unknown conversion specifier

### Parameters

stream | - | input file stream to read from

buffer | - | pointer to a null-terminated character string to read from

format | - | pointer to a null-terminated character string specifying how to read the input

... | - | receiving arguments.

The format string consists of

- non-whitespace multibyte characters except %: each such character in the format string consumes exactly one identical character from the input stream, or causes the function to fail if the next character on the stream does not compare equal.

- whitespace characters: any single whitespace character in the format string consumes all available consecutive whitespace characters from the input (determined as if by calling isspace in a loop). Note that there is no difference between "\n", " ", "\t\t", or other whitespace in the format string.

- conversion specifications. Each conversion specification has the following format:

- introductory % character.

- (optional) assignment-suppressing character *. If this option is present, the function does not assign the result of the conversion to any receiving argument.

- (optional) integer number (greater than zero) that specifies maximum field width, that is, the maximum number of characters that the function is allowed to consume when doing the conversion specified by the current conversion specification. Note that %s and %[ may lead to buffer overflow if the width is not provided.

- (optional) length modifier that specifies the size of the receiving argument, that is, the actual destination type. This affects the conversion accuracy and overflow rules. The default destination type is different for each conversion type (see table below).

- conversion format specifier.

The following format specifiers are available:

Conversionspecifier | Explanation | ExpectedArgument type

Length Modifier→ | hh | h | none | l | ll | j | z | t | L

Only available since C99→ | Yes | Yes | Yes | Yes | Yes

% | Matches literal %. | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A

Matches a character or a sequence of characters.

- If a width specifier is used, matches exactly width characters (the argument must be a pointer to an array with sufficient room).

- Unlike %s and %[, does not append the null character to the array.

c | N/A | N/A | char* | wchar_t* | N/A | N/A | N/A | N/A | N/A

Matches a sequence of non-whitespace characters (a string).

- If width specifier is used, matches up to width or until the first whitespace character, whichever appears first.

- Always stores a null character in addition to the characters matched (so the argument array must have room for at least width+1 characters).

s

Matches a non-empty sequence of character from set of characters.

- If the first character of the set is ^, then all characters not in the set are matched.

- If the set begins with ] or ^] then the ] character is also included into the set.

- It is implementation-defined whether the character - in the non-initial position in the scanset may be indicating a range, as in [0-9].

- If width specifier is used, matches only up to width.

- Always stores a null character in addition to the characters matched (so the argument array must have room for at least width+1 characters).

[set ﻿]

Matches a decimal integer.

- The format of the number is the same as expected by strtol with the value 10 for the base argument.

d | signed char* or unsigned char* | signed short* or unsigned short* | signed int* or unsigned int* | signed long* or unsigned long* | signed long long* or unsigned long long* | intmax_t* or uintmax_t* | size_t* | ptrdiff_t* | N/A

Matches an unsigned binary integer.

- The format of the number is the same as expected by strtoul with the value 2 for the base argument.

b (C23)

Matches an integer.

- The format of the number is the same as expected by strtol with the value 0 for the base argument (base is determined by the first characters parsed).

i

Matches an unsigned decimal integer.

- The format of the number is the same as expected by strtoul with the value 10 for the base argument.

u

Matches an unsigned octal integer.

- The format of the number is the same as expected by strtoul with the value 8 for the base argument.

o

Matches an unsigned hexadecimal integer.

- The format of the number is the same as expected by strtoul with the value 16 for the base argument.

xX

Returns the number of characters read so far.

- No input is consumed. Does not increment the assignment count.

- If the specifier has assignment-suppressing operator defined, the behavior is undefined.

n

Matches a floating-point number.

- The format of the number is the same as expected by strtof.

a (C99)A (C99)eEfF (C99)gG | N/A | N/A | float* | double* | N/A | N/A | N/A | N/A | long double*

Matches implementation defined character sequence defining a pointer.

- printf family of functions should produce the same sequence using %p format specifier.

p | N/A | N/A | void** | N/A | N/A | N/A | N/A | N/A | N/A

Notes

For every conversion specifier other than n, the longest sequence of input characters which does not exceed any specified ﬁeld width and which either is exactly what the conversion specifier expects or is a prefix of a sequence it would expect, is what's consumed from the stream. The ﬁrst character, if any, after this consumed sequence remains unread. If the consumed sequence has length zero or if the consumed sequence cannot be converted as specified above, the matching failure occurs unless end-of-ﬁle, an encoding error, or a read error prevented input from the stream, in which case it is an input failure.

Except for the % specifier, the input item (or, for %n, the count of input characters) is first converted to a type appropriate to the conversion specifier. Unless assignment was suppressed with *, the result of the conversion is written into the object pointed to by the next argument that wasn't yet written to. If this object does not have an appropriate type, or if the result of the conversion cannot be represented in the object, the behavior is undefined.

All conversion specifiers other than [, c, and n consume and discard all leading whitespace characters (determined as if by calling isspace) before attempting to parse the input. These consumed characters do not count towards the specified maximum field width.

The conversion specifiers lc, ls, and l[ perform multibyte-to-wide character conversion as if by calling mbrtowc with an mbstate_t object initialized to zero before the first character is converted.

The conversion specifiers s and [ always store the null terminator in addition to the matched characters. The size of the destination array must be at least one greater than the specified field width. The use of %s or %[, without specifying the destination array size, is as unsafe as gets.

The correct conversion specifications for the fixed-width integer types (int8_t, etc) are defined in the header <inttypes.h> (although SCNdMAX, SCNuMAX, etc is synonymous with %jd, %ju, etc).

There is a sequence point after the action of each conversion specifier; this permits storing multiple fields in the same “sink” variable.

When parsing an incomplete floating-point value that ends in the exponent with no digits, such as parsing "100er" with the conversion specifier %f, the sequence "100e" (the longest prefix of a possibly valid floating-point number) is consumed, resulting in a matching error (the consumed sequence cannot be converted to a floating-point number), with "r" remaining. Some existing implementations do not follow this rule and roll back to consume only "100", leaving "er", e.g., glibc bug 1765.

If a conversion specification is invalid, the behavior is undefined.

### Return value

### Complexity

Not guaranteed. Notably, some implementations of sscanf are O(N), where N = strlen(buffer) [1].

### Notes

Because most conversion specifiers first consume all consecutive whitespace, code such as

```
scanf("%d", &a);
scanf("%d", &b);
```

will read two integers that are entered on different lines (second %d will consume the newline left over by the first) or on the same line, separated by spaces or tabs (second %d will consume the spaces or tabs).

The conversion specifiers that do not consume leading whitespace, such as %c, can be made to do so by using a whitespace character in the format string:

```
scanf("%d", &a);
scanf(" %c", &c); // consume all consecutive whitespace after %d, then read a char
```

### Example

```
#define __STDC_WANT_LIB_EXT1__ 1
#include <locale.h>
#include <stddef.h>
#include <stdio.h>

int main(void)
{
    int i, j;
    float x, y;
    char str1[10], str2[4];
    wchar_t warr[2];
    setlocale(LC_ALL, "en_US.utf8");

    char input[] = "25 54.32E-1 Thompson 56789 0123 56ß水";
    /* parse as follows:
       %d: an integer
       %f: a floating-point value
       %9s: a string of at most 9 non-whitespace characters
       %2d: two-digit integer (digits 5 and 6)
       %f:  a floating-point value (digits 7, 8, 9)
       %*d: an integer which isn't stored anywhere
       ' ': all consecutive whitespace
       %3[0-9]: a string of at most 3 decimal digits (digits 5 and 6)
       %2lc: two wide characters, using multibyte to wide conversion  */
    int ret = sscanf(input, "%d%f%9s%2d%f%*d %3[0-9]%2lc",
                     &i, &x, str1, &j, &y, str2, warr);

    printf("Converted %d fields:\n"
           "i = %d\n"
           "x = %f\n"
           "str1 = %s\n"
           "j = %d\n"
           "y = %f\n"
           "str2 = %s\n"
           "warr[0] = U+%x\n"
           "warr[1] = U+%x\n",
           ret, i, x, str1, j, y, str2, warr[0], warr[1]);

#ifdef __STDC_LIB_EXT1__
    int n = sscanf_s(input, "%d%f%s", &i, &x, str1, (rsize_t)sizeof str1);
    // writes 25 to i, 5.432 to x, the 9 bytes "Thompson\0" to str1, and 3 to n.
#endif
}
```

Possible output:

```
Converted 7 fields:
i = 25
x = 5.432000
str1 = Thompson
j = 56
y = 789.000000
str2 = 56
warr[0] = U+df
warr[1] = U+6c34
```

### References

- C23 standard (ISO/IEC 9899:2024):

- 7.21.6.2 The fscanf function (p: TBD)

- 7.21.6.4 The scanf function (p: TBD)

- 7.21.6.7 The sscanf function (p: TBD)

- K.3.5.3.2 The fscanf_s function (p: TBD)

- K.3.5.3.4 The scanf_s function (p: TBD)

- K.3.5.3.7 The sscanf_s function (p: TBD)

- C17 standard (ISO/IEC 9899:2018):

- 7.21.6.2 The fscanf function (p: 231-236)

- 7.21.6.4 The scanf function (p: 236-237)

- 7.21.6.7 The sscanf function (p: 238-239)

- K.3.5.3.2 The fscanf_s function (p: 430-431)

- K.3.5.3.4 The scanf_s function (p: 432)

- K.3.5.3.7 The sscanf_s function (p: 433)

- C11 standard (ISO/IEC 9899:2011):

- 7.21.6.2 The fscanf function (p: 317-324)

- 7.21.6.4 The scanf function (p: 325)

- 7.21.6.7 The sscanf function (p: 326)

- K.3.5.3.2 The fscanf_s function (p: 592-593)

- K.3.5.3.4 The scanf_s function (p: 594)

- K.3.5.3.7 The sscanf_s function (p: 596)

- C99 standard (ISO/IEC 9899:1999):

- 7.19.6.2 The fscanf function (p: 282-289)

- 7.19.6.4 The scanf function (p: 290)

- 7.19.6.7 The sscanf function (p: 291)

- C89/C90 standard (ISO/IEC 9899:1990):

- 4.9.6.2 The fscanf function

- 4.9.6.4 The scanf function

- 4.9.6.6 The sscanf function

### See also

vscanfvfscanfvsscanfvscanf_svfscanf_svsscanf_s(C99)(C99)(C99)(C11)(C11)(C11) | reads formatted input from stdin, a file stream or a buffer using variable argument list  (function) [edit]

fgets | gets a character string from a file stream  (function) [edit]

printffprintfsprintfsnprintfprintf_sfprintf_ssprintf_ssnprintf_s(C99)(C11)(C11)(C11)(C11) | prints formatted output to stdout, a file stream or a buffer  (function) [edit]

C++ documentation for scanf, fscanf, sscanf
