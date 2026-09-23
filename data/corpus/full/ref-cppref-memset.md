Source: https://en.cppreference.com/w/c/string/byte/memset
Retrieved: 2026-09-23
License: CC-BY-SA (cppreference.com)

# memset, memset_explicit, memset_s - cppreference.com

# memset, memset_explicit, memset_s

Defined in header <string.h>

```
void* memset( void* dest, int ch, size_t count );
```

(1)

```
void* memset_explicit( void* dest, int ch, size_t count );
```

(2) | (since C23)

```
errno_t memset_s( void* dest, rsize_t destsz, int ch, rsize_t count );
```

(3) | (since C11)

- dest is a null pointer

- destsz or count is greater than RSIZE_MAX

- count is greater than destsz (buffer overflow would occur)

As with all bounds-checked functions, memset_s is only guaranteed to be available if __STDC_LIB_EXT1__ is defined by the implementation and if the user defines __STDC_WANT_LIB_EXT1__ to the integer constant 1 before including <string.h>.

### Parameters

dest | - | pointer to the object to fill

ch | - | fill byte

count | - | number of bytes to fill

destsz | - | size of the destination array

### Return value

### Notes

memset may be optimized away (under the as-if rules) if the object modified by this function is not accessed again for the rest of its lifetime (e.g., gcc bug 8537). For that reason, this function cannot be used to scrub memory (e.g., to fill an array that stored a password with zeroes).

This optimization is prohibited for memset_explicit and memset_s: they are guaranteed to perform the memory write.

Third-party solutions for that include FreeBSD explicit_bzero or Microsoft SecureZeroMemory.

### Example

```
#define __STDC_WANT_LIB_EXT1__ 1
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void)
{
    char str[] = "ghghghghghghghghghghgh";
    puts(str);
    memset(str,'a',5);
    puts(str);

#ifdef __STDC_LIB_EXT1__
    set_constraint_handler_s(ignore_handler_s);
    int r = memset_s(str, sizeof str, 'b', 5);
    printf("str = \"%s\", r = %d\n", str, r);
    r = memset_s(str, 5, 'c', 10);   // count is greater than destsz
    printf("str = \"%s\", r = %d\n", str, r);
#endif
}
```

Possible output:

```
ghghghghghghghghghghgh
aaaaahghghghghghghghgh
str = "bbbbbhghghghghghghghgh", r = 0
str = "ccccchghghghghghghghgh", r = 22
```

### References

- C23 standard (ISO/IEC 9899:2024):

- 7.26.6.1 The memset function (p: 383)

- 7.26.6.2 The memset_explicit function (p: 383)

- K.3.7.5.1 The memset_s function (p: 651)

- C17 standard (ISO/IEC 9899:2018):

- 7.24.6.1 The memset function (p: 270)

- K.3.7.4.1 The memset_s function (p: 451)

- C11 standard (ISO/IEC 9899:2011):

- 7.24.6.1 The memset function (p: 371)

- K.3.7.4.1 The memset_s function (p: 621-622)

- C99 standard (ISO/IEC 9899:1999):

- 7.21.6.1 The memset function (p: 333)

- C89/C90 standard (ISO/IEC 9899:1990):

- 4.11.6.1 The memset function

### See also

memcpymemcpy_s(C11) | copies one buffer to another  (function) [edit]

wmemset(C95) | copies the given wide character to every position in a wide character array  (function) [edit]

C++ documentation for memset
