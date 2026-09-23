Source: https://en.cppreference.com/w/c/language/for
Retrieved: 2026-09-23
License: CC-BY-SA (cppreference.com)

# for loop - cppreference.com

# for loop

Executes a loop.

Used as a shorter equivalent of while loop.

### Syntax

attr-spec-seq(since C23)(optional) for ( init-clause ; cond-expression ; iteration-expression ) loop-statement

### Explanation

Behaves as follows:

- init-clause may be an expression or a declaration(since C99).

- An init-clause, which is an expression, is evaluated once, before the first evaluation of cond-expression and its result is discarded.

- An init-clause, which is a declaration, is in scope in the entire loop body, including the remainder of init-clause, the entire cond-expression, the entire iteration-expression and the entire loop-statement. Only auto and register storage class specifiers are allowed for the variables declared in this declaration.

(since C99)

- cond-expression is evaluated before the loop body. If the result of the expression is zero, the loop statement is exited immediately.

- iteration-expression is evaluated after the loop body and its result is discarded. After evaluating iteration-expression, control is transferred to cond-expression.

init-clause, cond-expression, and iteration-expression are all optional. If cond-expression is omitted, it is replaced with a non-zero integer constant, which makes the loop endless:

```
for(;;) {
   printf("endless loop!");
}
```

loop-statement is not optional, but it may be a null statement:

```
for(int n = 0; n < 10; ++n, printf("%d\n", n))
    ; // null statement
```

If the execution of the loop needs to be terminated at some point, a  break statement can be used anywhere within the loop-statement.

The  continue statement used anywhere within the loop-statement transfers control to iteration-expression.

A program with an endless loop has undefined behavior if the loop has no observable behavior (I/O, volatile accesses, atomic or synchronization operation) in any part of its cond-expression, iteration-expression or loop-statement. This allows the compilers to optimize out all unobservable loops without proving that they terminate. The only exceptions are the loops where cond-expression is omitted or is a constant expression; for(;;) is always an endless loop.

As with all other selection and iteration statements, the for statement establishes block scope: any identifier introduced in the init-clause, cond-expression, or iteration-expression goes out of scope after the loop-statement.

(since C99)

attr-spec-seq is an optional list of attributes, applied to the for statement.

(since C23)

### Keywords

for

### Notes

The expression statement used as loop-statement establishes its own block scope, distinct from the scope of init-clause, unlike in C++:

```
for (int i = 0; ; ) {
    long i = 1;   // valid C, invalid C++
    // ...
}
```

It is possible to enter the body of a loop using goto. When entering a loop in this manner, init-clause and cond-expression are not executed. (If control then reaches the end of the loop body, repetition may occur including execution of cond-expression.)

### Example

```
#include <stdio.h>
#include <stdlib.h>
enum { SIZE = 8 };
int main(void)
{
    int array[SIZE];
    for(size_t i = 0 ; i < SIZE; ++i)
        array [i] = rand() % 2;
    printf("Array filled!\n");
    for (size_t i = 0; i < SIZE; ++i)
        printf("%d ", array[i]);
    putchar('\n');
}
```

Possible output:

```
Array filled!
1 0 1 1 1 1 0 0
```

### References

- C17 standard (ISO/IEC 9899:2018):

- 6.8.5.3 The for statement (p: 110)

- C11 standard (ISO/IEC 9899:2011):

- 6.8.5.3 The for statement (p: 151)

- C99 standard (ISO/IEC 9899:1999):

- 6.8.5.3 The for statement (p: 136)

- C89/C90 standard (ISO/IEC 9899:1990):

- 3.6.5.3 The for statement

### See also

C++ documentation for for loop
