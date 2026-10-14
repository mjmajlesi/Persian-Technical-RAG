Source: https://en.cppreference.com/w/c/string/byte/strcat
Retrieved: 2026-09-23
License: CC-BY-SA (cppreference.com)

# strcat, strcat_s - cppreference.com

# strcat, strcat_s

Defined in header <string.h>

```
char* strcat( char* dest, const char* src );
```

(1) | (until C99)

```
char* strcat( char* restrict dest, const char* restrict src );
```

(since C99)

```
errno_t strcat_s(char* restrict dest, rsize_t destsz, const char* restrict src);
```

(2) | (since C11)

- src or dest is a null pointer

- destsz is zero or greater than RSIZE_MAX

- there is no null terminator in the first destsz bytes of dest

- truncation would occur (the available space at the end of dest would not fit every character, including the null terminator, of src)

- overlap would occur between the source and the destination strings

### Parameters

dest | - | pointer to the null-terminated byte string to append to

src | - | pointer to the null-terminated byte string to copy from

destsz | - | maximum number of characters to write, typically the size of the destination buffer

### Return value

### Notes

Because strcat needs to seek to the end of dest on each call, it is inefficient to concatenate many strings into one using strcat.

strcat_s is allowed to clobber the destination array from the last character written up to destsz in order to improve efficiency: it may copy in multibyte blocks and then check for null bytes.

The function strcat_s is similar to the BSD function strlcat, except that

- strlcat truncates the source string to fit in the destination

- strlcat does not perform all the runtime checks that strcat_s does

- strlcat does not make failures obvious by setting the destination to a null string or calling a handler if the call fails.

Although strcat_s prohibits truncation due to potential security risks, it's possible to truncate a string using bounds-checked strncat_s instead.

### Example

```
#define __STDC_WANT_LIB_EXT1__ 1
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void)
{
    char str[50] = "Hello ";
    char str2[50] = "World!";
    strcat(str, str2);
    strcat(str, " ...");
    strcat(str, " Goodbye World!");
    puts(str);

#ifdef __STDC_LIB_EXT1__
    set_constraint_handler_s(ignore_handler_s);
    int r = strcat_s(str, sizeof str, " ... ");
    printf("str = \"%s\", r = %d\n", str, r);
    r = strcat_s(str, sizeof str, " and this is too much");
    printf("str = \"%s\", r = %d\n", str, r);
#endif
}
```

Possible output:

```
Hello World! ... Goodbye World!
str = "Hello World! ... Goodbye World! ... ", r = 0
str = "", r = 22
```

### References

- C23 standard (ISO/IEC 9899:2024):

- 7.24.3.1 The strcat function (p: TBD)

- K.3.7.2.1 The strcat_s function (p: TBD)

- C17 standard (ISO/IEC 9899:2018):

- 7.24.3.1 The strcat function (p: TBD)

- K.3.7.2.1 The strcat_s function (p: TBD)

- C11 standard (ISO/IEC 9899:2011):

- 7.24.3.1 The strcat function (p: 364)

- K.3.7.2.1 The strcat_s function (p: 617-618)

- C99 standard (ISO/IEC 9899:1999):

- 7.21.3.1 The strcat function (p: 327)

- C89/C90 standard (ISO/IEC 9899:1990):

- 4.11.3.1 The strcat function

### See also

strncatstrncat_s(C11) | concatenates a certain amount of characters of two strings  (function) [edit]

strcpystrcpy_s(C11) | copies one string to another  (function) [edit]

memccpy(C23) | copies one buffer to another, stopping after the specified delimiter  (function) [edit]

C++ documentation for strcat
