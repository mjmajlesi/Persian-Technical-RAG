Source: https://en.cppreference.com/w/c/string/byte/strcpy
Retrieved: 2026-09-23
License: CC-BY-SA (cppreference.com)

# strcpy, strcpy_s - cppreference.com

# strcpy, strcpy_s

Defined in header <string.h>

```
char* strcpy( char* dest, const char* src );
```

(1) | (until C99)

```
char* strcpy( char* restrict dest, const char* restrict src );
```

(since C99)

```
errno_t strcpy_s( char* restrict dest, rsize_t destsz, const char* restrict src );
```

(2) | (since C11)

- src or dest is a null pointer

- destsz is zero or greater than RSIZE_MAX

- destsz is less or equal strnlen_s(src, destsz); in other words, truncation would occur

- overlap would occur between the source and the destination strings

### Parameters

dest | - | pointer to the character array to write to

src | - | pointer to the null-terminated byte string to copy from

destsz | - | maximum number of characters to write, typically the size of the destination buffer

### Return value

### Notes

strcpy_s is allowed to clobber the destination array from the last character written up to destsz in order to improve efficiency: it may copy in multibyte blocks and then check for null bytes.

The function strcpy_s is similar to the BSD function strlcpy, except that

- strlcpy truncates the source string to fit in the destination (which is a security risk)

- strlcpy does not perform all the runtime checks that strcpy_s does

- strlcpy does not make failures obvious by setting the destination to a null string or calling a handler if the call fails.

Although strcpy_s prohibits truncation due to potential security risks, it's possible to truncate a string using bounds-checked strncpy_s instead.

### Example

```
#define __STDC_WANT_LIB_EXT1__ 1
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void)
{
    const char* src = "Take the test.";
//  src[0] = 'M' ; // this would be undefined behavior
    char dst[strlen(src) + 1]; // +1 to accommodate for the null terminator
    strcpy(dst, src);
    dst[0] = 'M'; // OK
    printf("src = %s\ndst = %s\n", src, dst);

#ifdef __STDC_LIB_EXT1__
    set_constraint_handler_s(ignore_handler_s);
    int r = strcpy_s(dst, sizeof dst, src);
    printf("dst = \"%s\", r = %d\n", dst, r);
    r = strcpy_s(dst, sizeof dst, "Take even more tests.");
    printf("dst = \"%s\", r = %d\n", dst, r);
#endif
}
```

Possible output:

```
src = Take the test.
dst = Make the test.
dst = "Take the test.", r = 0
dst = "", r = 22
```

### References

- C23 standard (ISO/IEC 9899:2024):

- 7.24.2.3 The strcpy function (p: TBD)

- K.3.7.1.3 The strcpy_s function (p: TBD)

- C17 standard (ISO/IEC 9899:2018):

- 7.24.2.3 The strcpy function (p: 264-265)

- K.3.7.1.3 The strcpy_s function (p: 447)

- C11 standard (ISO/IEC 9899:2011):

- 7.24.2.3 The strcpy function (p: 363)

- K.3.7.1.3 The strcpy_s function (p: 615-616)

- C99 standard (ISO/IEC 9899:1999):

- 7.21.2.3 The strcpy function (p: 326)

- C89/C90 standard (ISO/IEC 9899:1990):

- 4.11.2.3 The strcpy function

### See also

strncpystrncpy_s(C11) | copies a certain amount of characters from one string to another  (function) [edit]

memcpymemcpy_s(C11) | copies one buffer to another  (function) [edit]

wcscpywcscpy_s(C95)(C11) | copies one wide string to another  (function) [edit]

strdup(dynamic memory TR) | allocate a copy of a string  (function) [edit]

C++ documentation for strcpy
