Source: https://en.cppreference.com/w/c/language/if
Retrieved: 2026-09-23
License: CC-BY-SA (cppreference.com)

# if statement - cppreference.com

# if statement

Conditionally executes code.

Used where code needs to be executed only if some condition is true.

### Syntax

attr-spec-seq(optional) if ( expression ) statement-true | (1)

attr-spec-seq(optional) if ( expression ) statement-true else statement-false | (2)

attr-spec-seq | - | (C23)optional list of attributes, applied to the if statement

expression | - | an expression of any scalar type

statement-true | - | any statement (often a compound statement), which is executed if expression compares not equal to 0

statement-false | - | any statement (often a compound statement), which is executed if expression compares equal to 0

### Explanation

expression must be an expression of any scalar type.

If expression compares not equal to the integer zero, statement-true is executed.

In the form (2), if expression compares equal to the integer zero, statement_false is executed.

As with all other selection and iteration statements, the entire if-statement has its own block scope:

```
enum {a, b};
int different(void)
{
    if (sizeof(enum {b, a}) != sizeof(int))
        return a; // a == 1
    return b; // b == 0 in C89, b == 1 in C99
}
```

(since C99)

### Notes

The else is always associated with the closest preceding if (in other words, if statement-true is also an if statement, then that inner if statement must contain an else part as well):

```
int j = 1;
if (i > 1)
   if(j > 2)
       printf("%d > 1 and %d > 2\n", i, j);
    else // this else is part of if(j>2), not part of if(i>1) 
       printf("%d > 1 and %d <= 2\n", i, j);
```

If statement-true is entered through a goto, statement-false is not executed.

### Keywords

if, else

### Example

```
#include <stdio.h>
 
int main(void)
{
    int i = 2;
    if (i > 2) {
        printf("first is true\n");
    } else {
        printf("first is false\n");
    }
 
    i = 3;
    if (i == 3) printf("i == 3\n");
 
    if (i != 3) printf("i != 3 is true\n");
    else        printf("i != 3 is false\n");
}
```

Output:

```
first is false
i == 3
i != 3 is false
```

### References

- C17 standard (ISO/IEC 9899:2018):

- 6.8.4.1 The if statement (p: 108-109)

- C11 standard (ISO/IEC 9899:2011):

- 6.8.4.1 The if statement (p: 148-149)

- C99 standard (ISO/IEC 9899:1999):

- 6.8.4.1 The if statement (p: 133-134)

- C89/C90 standard (ISO/IEC 9899:1990):

- 3.6.4.1 The if statement

### See also

C++ documentation for if statement
