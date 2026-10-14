Source: https://en.cppreference.com/w/c/io/fwrite
Retrieved: 2026-09-23
License: CC-BY-SA (cppreference.com)

# fwrite - cppreference.com

# fwrite

Defined in header <stdio.h>

```
size_t fwrite( const void* buffer, size_t size, size_t count,
               FILE* stream );
```

(until C99)

```
size_t fwrite( const void* restrict buffer, size_t size, size_t count,
               FILE* restrict stream );
```

(since C99)

Writes count of objects from the given array buffer to the output stream stream. The objects are written as if by reinterpreting each object as an array of unsigned char and calling fputc size times for each object to write those unsigned chars into stream, in order. The file position indicator for the stream is advanced by the number of characters written.

If an error occurs, the resulting value of the file position indicator for the stream is indeterminate.

### Parameters

buffer | - | pointer to the first object in the array to be written

size | - | size of each object

count | - | the number of the objects to be written

stream | - | pointer to the output stream

### Return value

The number of objects written successfully, which will be less than count only if an error occurs.

If size or count is zero, fwrite returns zero and performs no other action.

### Example

```
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>

enum { SIZE = 5 };

int main(void)
{
    double a[SIZE] = {1, 2, 3, 4, 5};
    FILE* f1 = fopen("file.bin", "wb");
    assert(f1);
    size_t r1 = fwrite(a, sizeof a[0], SIZE, f1);
    printf("wrote %zu elements out of %d requested\n", r1, SIZE);
    fclose(f1);

    double b[SIZE];
    FILE* f2 = fopen("file.bin", "rb");
    size_t r2 = fread(b, sizeof b[0], SIZE, f2);
    fclose(f2);
    printf("read back: ");
    for (size_t i = 0; i < r2; ++i)
        printf("%0.2f ", b[i]);
}
```

Output:

```
wrote 5 elements out of 5 requested
read back: 1.00 2.00 3.00 4.00 5.00
```

### References

- C23 standard (ISO/IEC 9899:2024):

- 7.21.8.2 The fwrite function (p: TBD)

- C17 standard (ISO/IEC 9899:2018):

- 7.21.8.2 The fwrite function (p: TBD)

- C11 standard (ISO/IEC 9899:2011):

- 7.21.8.2 The fwrite function (p: 335-336)

- C99 standard (ISO/IEC 9899:1999):

- 7.19.8.2 The fwrite function (p: 301-302)

- C89/C90 standard (ISO/IEC 9899:1990):

- 4.9.8.2 The fwrite function

### See also

printffprintfsprintfsnprintfprintf_sfprintf_ssprintf_ssnprintf_s(C99)(C11)(C11)(C11)(C11) | prints formatted output to stdout, a file stream or a buffer  (function) [edit]

fputs | writes a character string to a file stream  (function) [edit]

fread | reads from a file  (function) [edit]

C++ documentation for fwrite
