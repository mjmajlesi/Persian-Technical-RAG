Source: https://en.cppreference.com/w/c/string/byte/strlen
Retrieved: 2026-09-23
License: CC-BY-SA (cppreference.com)

# strlen, strnlen_s - cppreference.com

# strlen, strnlen_s

Defined in header <string.h>

```
size_t strlen( const char* str );
```

(1)

```
size_t strnlen_s( const char* str, size_t strsz );
```

(2) | (since C11)

As with all bounds-checked functions, strnlen_s is only guaranteed to be available if __STDC_LIB_EXT1__ is defined by the implementation and if the user defines __STDC_WANT_LIB_EXT1__ to the integer constant 1 before including <string.h>.

### Parameters

str | - | pointer to the null-terminated byte string to be examined

strsz | - | maximum number of characters to examine

### Return value

### Notes

strnlen_s and wcsnlen_s are the only bounds-checked functions that do not invoke the runtime constraints handler. They are pure utility functions used to provide limited support for non-null terminated strings.

### Example

```
#define __STDC_WANT_LIB_EXT1__ 1
#include <stdio.h>
#include <string.h>

int main(void)
{
    const char str[] = "How many characters does this string contain?";

    printf("without null character: %zu\n", strlen(str));
    printf("with null character:    %zu\n", sizeof str);

#ifdef __STDC_LIB_EXT1__
    printf("without null character: %zu\n", strnlen_s(str, sizeof str));
#endif
}
```

Possible output:

```
without null character: 45
with null character:    46
without null character: 45
```

### References

- C23 standard (ISO/IEC 9899:2024):

- 7.24.6.3 The strlen function (p: TBD)

- K.3.7.4.4 The strnlen_s function (p: TBD)

- C17 standard (ISO/IEC 9899:2018):

- 7.24.6.3 The strlen function (p: TBD)

- K.3.7.4.4 The strnlen_s function (p: TBD)

- C11 standard (ISO/IEC 9899:2011):

- 7.24.6.3 The strlen function (p: 372)

- K.3.7.4.4 The strnlen_s function (p: 623)

- C99 standard (ISO/IEC 9899:1999):

- 7.21.6.3 The strlen function (p: 334)

- C89/C90 standard (ISO/IEC 9899:1990):

- 4.11.6.3 The strlen function

### See also

wcslenwcsnlen_s(C95)(C11) | returns the length of a wide string  (function) [edit]

mblen | returns the number of bytes in the next multibyte character  (function) [edit]

C++ documentation for strlen
