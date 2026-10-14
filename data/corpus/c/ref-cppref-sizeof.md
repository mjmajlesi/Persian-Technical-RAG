Source: https://en.cppreference.com/w/c/language/sizeof
Retrieved: 2026-09-23
License: CC-BY-SA (cppreference.com)

# sizeof operator - cppreference.com

# sizeof operator

Queries size of the object or type.

Used when actual size of the object must be known.

### Syntax

sizeof( type ) | (1)

sizeof expression | (2)

Both versions return a value of type size_t.

### Explanation

### Notes

Depending on the computer architecture, a byte may consist of 8 or more bits, the exact number provided as CHAR_BIT.

sizeof(char), sizeof(signed char), and sizeof(unsigned char) always return 1.

sizeof cannot be used with function types, incomplete types (including void), or bit-field lvalues.

When applied to an operand that has structure or union type, the result is the total number of bytes in such an object, including internal and trailing padding. The trailing padding is such that if the object were an element of an array, the alignment requirement of the next element of this array would be satisfied, in other words, sizeof(T) returns the size of an element of a T[] array.

If type is a VLA type and changing the value of its size expression would not affect the result of sizeof, it is unspecified whether or not the size expression is evaluated.

(since C99)

Except if the type of expression is a VLA,(since C99)expression is not evaluated and the sizeof operator may be used in an integer constant expression.

If the type of expression is a variable-length array type, expression is evaluated and the size of the array it evaluates to is calculated at run time.

(since C99)

Number of elements in any array a including VLA(since C99) may be determined with the expression sizeof a / sizeof a[0]. Note that if a has pointer type (such as after array-to-pointer conversion of function parameter type adjustment), this expression would simply divide the number of bytes in a pointer type by the number of bytes in the pointed type.

### Keywords

sizeof

### Example

Sample output corresponds to a platform with 64-bit pointers and 32-bit int

```
#include <stdio.h>

int main(void)
{
    short x;
    // type argument:
    printf("sizeof(float)          = %zu\n", sizeof(float));
    printf("sizeof(void(*)(void))  = %zu\n", sizeof(void(*)(void)));
    printf("sizeof(char[10])       = %zu\n", sizeof(char[10]));
//  printf("sizeof(void(void))     = %zu\n", sizeof(void(void))); // Error: function type
//  printf("sizeof(char[])         = %zu\n", sizeof(char[])); // Error: incomplete type

    // expression argument:
    printf("sizeof 'a'             = %zu\n", sizeof 'a'); // type of 'a' is int
//  printf("sizeof main            = %zu\n", sizeof main); // Error: Function type
    printf("sizeof &main           = %zu\n", sizeof &main);
    printf("sizeof \"hello\"         = %zu\n", sizeof "hello"); // type is char[6]
    printf("sizeof x               = %zu\n", sizeof x); // type of x is short
    printf("sizeof (x+1)           = %zu\n", sizeof(x + 1)); // type of x+1 is int
}
```

Possible output:

```
sizeof(float)          = 4
sizeof(void(*)(void))  = 8
sizeof(char[10])       = 10
sizeof 'a'             = 4
sizeof &main           = 8
sizeof "hello"         = 6
sizeof x               = 2
sizeof (x+1)           = 4
```

### References

- C23 standard (ISO/IEC 9899:2024):

- 6.5.3.4 The sizeof and alignof operators (p: TBD)

- C17 standard (ISO/IEC 9899:2018):

- 6.5.3.4 The sizeof and _Alignof operators (p: TBD)

- C11 standard (ISO/IEC 9899:2011):

- 6.5.3.4 The sizeof and _Alignof operators (p: 90-91)

- C99 standard (ISO/IEC 9899:1999):

- 6.5.3.4 The sizeof operator (p: 80-81)

- C89/C90 standard (ISO/IEC 9899:1990):

- 3.3.3.4 The sizeof operator

### See also

C++ documentation for sizeof operator
