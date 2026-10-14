Source: https://en.cppreference.com/w/c/io/fclose
Retrieved: 2026-09-23
License: CC-BY-SA (cppreference.com)

# fclose - cppreference.com

# fclose

Defined in header <stdio.h>

```
int fclose( FILE* stream );
```

Closes the given file stream. Any unwritten buffered data are flushed to the OS. Any unread buffered data are discarded.

Whether or not the operation succeeds, the stream is no longer associated with a file, and the buffer allocated by setbuf or setvbuf, if any, is also disassociated and deallocated if automatic allocation was used.

The behavior is undefined if the value of the pointer stream is used after fclose returns.

### Parameters

stream | - | the file stream to close

### Return value

0 on success, EOF otherwise

### Example

```
#include <stdio.h>
#include <stdlib.h>

int main(void)
{
    const char* fname = "/tmp/unique_name.txt"; // or tmpnam(NULL);
    int is_ok = EXIT_FAILURE;

    FILE* fp = fopen(fname, "w+");
    if (!fp)
    {
        perror("File opening failed");
        return is_ok;
    }
    fputs("Hello, world!\n", fp);
    rewind(fp);

    int c; // note: int, not char, required to handle EOF
    while ((c = fgetc(fp)) != EOF) // standard C I/O file reading loop
        putchar(c);

    if (ferror(fp))
        puts("I/O error when reading");
    else if (feof(fp))
    {
        puts("End of file is reached successfully");
        is_ok = EXIT_SUCCESS;
    }

    fclose(fp);
    remove(fname);
    return is_ok;
}
```

Possible output:

```
Hello, world!
End of file is reached successfully
```

### References

- C23 standard (ISO/IEC 9899:2024):

- 7.21.5.1 The fclose function (p: TBD)

- C17 standard (ISO/IEC 9899:2018):

- 7.21.5.1 The fclose function (p: TBD)

- C11 standard (ISO/IEC 9899:2011):

- 7.21.5.1 The fclose function (p: 304)

- C99 standard (ISO/IEC 9899:1999):

- 7.19.5.1 The fclose function (p: 270)

- C89/C90 standard (ISO/IEC 9899:1990):

- 4.9.5.1 The fclose function

### See also

fopenfopen_s(C11) | opens a file  (function) [edit]

freopenfreopen_s(C11) | open an existing stream with a different name  (function) [edit]

C++ documentation for fclose
