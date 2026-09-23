Source: https://en.cppreference.com/w/c/language/switch
Retrieved: 2026-09-23
License: CC-BY-SA (cppreference.com)

# switch statement - cppreference.com

# switch statement

Executes code according to the value of an integral argument.

Used where one or several out of many branches of code need to be executed according to an integral value.

### Syntax

attr-spec-seq(optional) switch ( expression ) statement

attr-spec-seq | - | (C23)optional list of attributes, applied to the switch statement

expression | - | any expression of integer type (char, signed or unsigned integer, or enumeration)

statement | - | any statement (typically a compound statement). case: and default: labels are permitted in statement, and break; statement has special meaning.

case constant-expression : statement | (1) | (until C23)

attr-spec-seq(optional) case constant-expression : statement(optional) | (1) | (since C23)

default : statement | (2) | (until C23)

attr-spec-seq(optional) default : statement(optional) | (2) | (since C23)

constant-expression | - | any integer constant expression

attr-spec-seq | - | (C23)optional list of attributes, applied to the label

### Explanation

The body of a switch statement may have an arbitrary number of case: labels, as long as the values of all constant-expressions are unique (after conversion to the promoted type of expression). At most one default: label may be present (although nested switch statements may use their own default: labels or have case: labels whose constants are identical to the ones used in the enclosing switch).

If expression evaluates to the value that is equal to the value of one of constant-expressions after conversion to the promoted type of expression, then control is transferred to the statement that is labeled with that constant-expression.

If expression evaluates to a value that doesn't match any of the case: labels, and the default: label is present, control is transferred to the statement labeled with the default: label.

If expression evaluates to a value that doesn't match any of the case: labels, and the default: label is not present, none of the switch body is executed.

The break statement, when encountered anywhere in statement, exits the switch statement:

```
switch(1) {
    case 1 : puts("1"); // prints "1",
    case 2 : puts("2"); // then prints "2" ("fall-through")
}
```

```
switch(1) {
    case 1 : puts("1"); // prints "1"
             break;     // and exits the switch
    case 2 : puts("2");
             break;
}
```

As with all other selection and iteration statements, the switch statement establishes block scope: any identifier introduced in the expression goes out of scope after the statement.

If a VLA or another identifier with variably-modified type has a case: or a default: label within its scope, the entire switch statement must be in its scope (in other words, a VLA must be declared either before the entire switch or after the last label):

```
switch (expr)
{
        int i = 4; // not a VLA; OK to declare here
        f(i); // never called
//      int a[i]; // error: VLA cannot be declared here
    case 0:
        i = 17;
    default:
        int a[i]; // OK to declare VLA here
        printf("%d\n", i); // prints 17 if expr == 0, prints indeterminate value otherwise
}
```

(since C99)

### Keywords

switch, case, default

### Example

```
#include <stdio.h>

void func(int x)
{
   printf("func(%d): ", x);
   switch(x)
   {
      case 1: printf("case 1, ");
      case 2: printf("case 2, ");
      case 3: printf("case 3.\n"); break;
      case 4: printf("case 4, ");
      case 5:
      case 6: printf("case 5 or case 6, ");
      default: printf("default.\n");
   }
}

int main(void)
{
   for(int i = 1; i < 9; ++i) func(i);
}
```

Output:

```
func(1): case 1, case 2, case 3.
func(2): case 2, case 3.
func(3): case 3.
func(4): case 4, case 5 or case 6, default.
func(5): case 5 or case 6, default.
func(6): case 5 or case 6, default.
func(7): default.
func(8): default.
```

### References

- C17 standard (ISO/IEC 9899:2018):

- 6.8.4.2 The switch statement (p: 108-109)

- C11 standard (ISO/IEC 9899:2011):

- 6.8.4.2 The switch statement (p: 149-150)

- C99 standard (ISO/IEC 9899:1999):

- 6.8.4.2 The switch statement (p: 134-135)

- C89/C90 standard (ISO/IEC 9899:1990):

- 3.6.4.2 The switch statement

### See also

C++ documentation for switch statement
