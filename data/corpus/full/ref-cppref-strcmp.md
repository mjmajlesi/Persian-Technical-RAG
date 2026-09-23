Source: https://en.cppreference.com/w/c/string/byte/strcmp
Retrieved: 2026-09-23
License: CC-BY-SA (cppreference.com)

# strcmp - cppreference.com

# strcmp

Defined in header <string.h>

```
int strcmp( const char* lhs, const char* rhs );
```

Compares two null-terminated byte strings lexicographically.

The sign of the result is the sign of the difference between the values of the first pair of characters (both interpreted as unsigned char) that differ in the strings being compared.

The behavior is undefined if lhs or rhs are not pointers to null-terminated byte strings.

### Parameters

lhs, rhs | - | pointers to the null-terminated byte strings to compare

### Return value

Negative value if lhs appears before rhs in lexicographical order.

Zero if lhs and rhs compare equal.

Positive value if lhs appears after rhs in lexicographical order.

### Notes

This function is not locale-sensitive, unlike strcoll and strxfrm.

### Example

```
#include <stdio.h>
#include <string.h>

void demo(const char* lhs, const char* rhs)
{
    const int rc = strcmp(lhs, rhs);
    const char* rel = rc < 0 ? "precedes" : rc > 0 ? "follows" : "equals";
    printf("[%s] %s [%s]\n", lhs, rel, rhs);
}

int main(void)
{
    const char* string = "Hello World!";
    demo(string, "Hello!");
    demo(string, "Hello");
    demo(string, "Hello there");
    demo("Hello, everybody!" + 12, "Hello, somebody!" + 11);
}
```

Output:

```
[Hello World!] precedes [Hello!]
[Hello World!] follows [Hello]
[Hello World!] precedes [Hello there]
[body!] equals [body!]
```

### References

- C23 standard (ISO/IEC 9899:2024):

- 7.24.4.2 The strcmp function (p: TBD)

- C17 standard (ISO/IEC 9899:2018):

- 7.24.4.2 The strcmp function (p: TBD)

- C11 standard (ISO/IEC 9899:2011):

- 7.24.4.2 The strcmp function (p: 365-366)

- C99 standard (ISO/IEC 9899:1999):

- 7.21.4.2 The strcmp function (p: 328-329)

- C89/C90 standard (ISO/IEC 9899:1990):

- 4.11.4.2 The strcmp function

### See also

strncmp | compares a certain amount of characters of two strings  (function) [edit]

wcscmp(C95) | compares two wide strings  (function) [edit]

memcmp | compares two buffers  (function) [edit]

strcoll | compares two strings in accordance to the current locale  (function) [edit]

C++ documentation for strcmp
