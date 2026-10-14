Source: https://en.cppreference.com/w/c/string/byte/strstr
Retrieved: 2026-09-23
License: CC-BY-SA (cppreference.com)

# strstr - cppreference.com

# strstr

Defined in header <string.h>

```
char* strstr( const char* str, const char* substr );
```

(1)

```
/*QChar*/* strstr( /*QChar*/* str, const char* substr );
```

(2) | (since C23)

- If str is of type const T*, the return type is const char*.

- Otherwise, if str is of type T*, the return type is char*.

- Otherwise, the behavior is undefined.

The behavior is undefined if either str or substr is not a pointer to a null-terminated byte string.

### Parameters

str | - | pointer to the null-terminated byte string to examine

substr | - | pointer to the null-terminated byte string to search for

### Return value

Pointer to the first character of the found substring in str, or a null pointer if such substring is not found. If substr points to an empty string, str is returned.

### Example

```
#include <stdio.h>
#include <string.h>

void find_str(char const* str, char const* substr)
{
    char const* pos = strstr(str, substr);
    if (pos)
        printf(
            "Found the string [%s] in [%s] at position %td\n",
            substr, str, pos - str
        );
    else
        printf(
            "The string [%s] was not found in [%s]\n",
            substr, str
        );
}

int main(void)
{
    char const* str = "one two three";
    find_str(str, "two");
    find_str(str, "");
    find_str(str, "nine");
    find_str(str, "n");
 
    return 0;
}
```

Output:

```
Found the string [two] in [one two three] at position 4
Found the string [] in [one two three] at position 0
The string [nine] was not found in [one two three]
Found the string [n] in [one two three] at position 1
```

### References

- C23 standard (ISO/IEC 9899:2024):

- 7.24.5.7 The strstr function (p: TBD)

- C17 standard (ISO/IEC 9899:2018):

- 7.24.5.7 The strstr function (p: 269)

- C11 standard (ISO/IEC 9899:2011):

- 7.24.5.7 The strstr function (p: 369)

- C99 standard (ISO/IEC 9899:1999):

- 7.21.5.7 The strstr function (p: 332)

- C89/C90 standard (ISO/IEC 9899:1990):

- 4.11.5.7 The strstr function

### See also

strchr | finds the first occurrence of a character  (function) [edit]

strrchr | finds the last occurrence of a character  (function) [edit]

C++ documentation for strstr
