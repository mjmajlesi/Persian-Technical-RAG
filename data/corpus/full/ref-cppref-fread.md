Source: https://en.cppreference.com/w/c/io/fread
Retrieved: 2026-09-23
License: CC-BY-SA (cppreference.com)

# fread - cppreference.com

# fread

Defined in header <stdio.h>

```
size_t fread( void* buffer, size_t size, size_t count,
              FILE* stream );
```

(until C99)

```
size_t fread( void* restrict buffer, size_t size, size_t count,
              FILE* restrict stream );
```

(since C99)

Reads up to count objects into the array buffer from the given input stream stream as if by calling fgetc size times for each object, and storing the results, in the order obtained, into the successive positions of buffer, which is reinterpreted as an array of unsigned char. The file position indicator for the stream is advanced by the number of characters read.

If an error occurs, the resulting value of the file position indicator for the stream is indeterminate. If a partial element is read, its value is indeterminate.

### Parameters

buffer | - | pointer to the array where the read objects are stored

size | - | size of each object in bytes

count | - | the number of the objects to be read

stream | - | the stream to read

### Return value

Number of objects read successfully, which may be less than count if an error or end-of-file condition occurs.

If size or count is zero, fread returns zero and performs no other action.

fread does not distinguish between end-of-file and error, and callers must use feof and ferror to determine which occurred.

### Example

```
#include <stdio.h>

enum { SIZE = 5 };

int main(void)
{
    const double a[SIZE] = {1.0, 2.0, 3.0, 4.0, 5.0};
    printf("Array has size %ld bytes, element size: %ld\n", sizeof a, sizeof* a);
    FILE* fp = fopen("test.bin", "wb"); // must use binary mode
    fwrite(a, sizeof* a, SIZE, fp); // writes an array of doubles
    fclose(fp);

    double b[SIZE];
    fp = fopen("test.bin","rb");
    const size_t ret_code = fread(b, sizeof b[0], SIZE, fp); // reads an array of doubles
    if (ret_code == SIZE)
    {
        printf("Array at %p read successfully, contents:\n", (void*)&a);
        for (int n = 0; n != SIZE; ++n)
            printf("%f ", b[n]);
        putchar('\n');
    }
    else // error handling
    {
        if (feof(fp))
            printf("Error reading test.bin: unexpected end of file\n");
        else if (ferror(fp))
            perror("Error reading test.bin");
    }

    fclose(fp);
}
```

Possible output:

```
Array has size 40 bytes, element size: 8
Array at 0x1337f00d6960 read successfully, contents:
1.000000 2.000000 3.000000 4.000000 5.000000
```

### References

- C23 standard (ISO/IEC 9899:2024):

- 7.21.8.1 The fread function (p: TBD)

- C17 standard (ISO/IEC 9899:2018):

- 7.21.8.1 The fread function (p: 243-244)

- C11 standard (ISO/IEC 9899:2011):

- 7.21.8.1 The fread function (p: 335)

- C99 standard (ISO/IEC 9899:1999):

- 7.19.8.1 The fread function (p: 301)

- C89/C90 standard (ISO/IEC 9899:1990):

- 4.9.8.1 The fread function

### See also

scanffscanfsscanfscanf_sfscanf_ssscanf_s(C11)(C11)(C11) | reads formatted input from stdin, a file stream or a buffer  (function) [edit]

fgets | gets a character string from a file stream  (function) [edit]

fwrite | writes to a file  (function) [edit]

C++ documentation for fread
