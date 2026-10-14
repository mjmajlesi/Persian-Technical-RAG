Source: https://en.cppreference.com/w/c/string/byte/memcpy
Retrieved: 2026-09-23
License: CC-BY-SA (cppreference.com)

# memcpy, memcpy_s - cppreference.com

# memcpy, memcpy_s

Defined in header <string.h>

```
void* memcpy( void* dest, const void* src, size_t count );
```

(1) | (until C99)

```
void* memcpy( void* restrict dest, const void* restrict src, size_t count );
```

(since C99)

```
errno_t memcpy_s( void* restrict dest, rsize_t destsz,
                  const void* restrict src, rsize_t count );
```

(2) | (since C11)

- dest or src is a null pointer

- destsz or count is greater than RSIZE_MAX

- count is greater than destsz (buffer overflow would occur)

- the source and the destination objects overlap

### Parameters

dest | - | pointer to the object to copy to

destsz | - | max number of bytes to modify in the destination (typically the size of the destination object)

src | - | pointer to the object to copy from

count | - | number of bytes to copy

### Return value

### Notes

memcpy may be used to set the effective type of an object obtained by an allocation function.

memcpy is the fastest library routine for memory-to-memory copy. It is usually more efficient than strcpy, which must scan the data it copies or memmove, which must take precautions to handle overlapping inputs.

Several C compilers transform suitable memory-copying loops to memcpy calls.

Where strict aliasing prohibits examining the same memory as values of two different types, memcpy may be used to convert the values.

### Example

```
#define __STDC_WANT_LIB_EXT1__ 1
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void)
{
    // simple usage
    char source[] = "once upon a midnight dreary...", dest[4];
    memcpy(dest, source, sizeof dest);
    for (size_t n = 0; n < sizeof dest; ++n)
        putchar(dest[n]);

    // setting effective type of allocated memory to be int
    int* p = malloc(3 * sizeof(int)); // allocated memory has no effective type
    int arr[3] = {1, 2, 3};
    memcpy(p, arr, 3 * sizeof(int));  // allocated memory now has an effective type

    // reinterpreting data
    double d = 0.1;
//    int64_t n = *(int64_t*)(&d); // strict aliasing violation
    int64_t n;
    memcpy(&n, &d, sizeof d); // OK
    printf("\n%a is %" PRIx64 " as an int64_t\n", d, n);

#ifdef __STDC_LIB_EXT1__
    set_constraint_handler_s(ignore_handler_s);
    char src[] = "aaaaaaaaaa";
    char dst[] = "xyxyxyxyxy";
    int r = memcpy_s(dst,sizeof dst,src,5);
    printf("dst = \"%s\", r = %d\n", dst,r);
    r = memcpy_s(dst,5,src,10);            //  count is greater than destsz
    printf("dst = \"");
    for (size_t ndx = 0; ndx < sizeof dst; ++ndx)
    {
        char c = dst[ndx];
        c ? printf("%c", c) : printf("\\0");
    }
    printf("\", r = %d\n", r);
#endif
}
```

Possible output:

```
once
0x1.999999999999ap-4 is 3fb999999999999a as an int64_t
dst = "aaaaayxyxy", r = 0
dst = "\0\0\0\0\0yxyxy", r = 22
```

### References

- C23 standard (ISO/IEC 9899:2024):

- 7.24.2.1 The memcpy function (p: TBD)

- K.3.7.1.1 The memcpy_s function (p: TBD)

- C17 standard (ISO/IEC 9899:2018):

- 7.24.2.1 The memcpy function (p: TBD)

- K.3.7.1.1 The memcpy_s function (p: TBD)

- C11 standard (ISO/IEC 9899:2011):

- 7.24.2.1 The memcpy function (p: 362)

- K.3.7.1.1 The memcpy_s function (p: 614)

- C99 standard (ISO/IEC 9899:1999):

- 7.21.2.1 The memcpy function (p: 325)

- C89/C90 standard (ISO/IEC 9899:1990):

- 4.11.2.1 The memcpy function

### See also

memccpy(C23) | copies one buffer to another, stopping after the specified delimiter  (function) [edit]

memmovememmove_s(C11) | moves one buffer to another  (function) [edit]

wmemcpywmemcpy_s(C95)(C11) | copies a certain amount of wide characters between two non-overlapping arrays  (function) [edit]

C++ documentation for memcpy
