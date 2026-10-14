Source: https://en.cppreference.com/w/c/preprocessor/conditional
Retrieved: 2026-09-23
License: CC-BY-SA (cppreference.com)

# Conditional inclusion - cppreference.com

# Conditional inclusion

The preprocessor supports conditional compilation of parts of source file. This behavior is controlled by #if, #else, #elif, #ifdef, #ifndef, #elifdef, #elifndef(since C23), and #endif directives.

### Syntax

#if expression

#ifdef identifier

#ifndef identifier

#elif expression

#elifdef identifier | (since C23)

#elifndef identifier | (since C23)

#else

#endif

### Explanation

The conditional preprocessing block starts with #if, #ifdef or #ifndef directive, then optionally includes any number of #elif, #elifdef, or #elifndef(since C23) directives, then optionally includes at most one #else directive and is terminated with #endif directive. Any inner conditional preprocessing blocks are processed separately.

Each of #if, #ifdef, #ifndef, #elif, #elifdef, #elifndef(since C23), and #else directives control code block until first #elif, #elifdef, #elifndef(since C23), #else, #endif directive not belonging to any inner conditional preprocessing blocks.

#if, #ifdef and #ifndef directives test the specified condition (see below) and if it evaluates to true, compiles the controlled code block. In that case subsequent #else, #elifdef, #elifndef,(since C23) and #elif directives are ignored. Otherwise, if the specified condition evaluates false, the controlled code block is skipped and the subsequent #else, #elifdef, #elifndef,(since C23) or #elif directive (if any) is processed. If the subsequent directive is #else, the code block controlled by the #else directive is unconditionally compiled. Otherwise, the #elif, #elifdef, or #elifndef(since C23) directive acts as if it was #if directive: checks for condition, compiles or skips the controlled code block based on the result, and in the latter case processes subsequent #elif, #elifdef, #elifndef,(since C23) and #else directives. The conditional preprocessing block is terminated by #endif directive.

### Conditional evaluation

#### #if, #elif

The expression is a constant expression, using only constants and identifiers, defined using  #define directive. Any identifier, which is not literal, non defined using  #define directive, evaluates to 0 except true which evaluates to 1(since C23).

The expression may contain unary operators in form defined identifier or defined (identifier) which return 1 if the identifier was defined using  #define directive and 0 otherwise. In this context, __has_include, __has_embed and __has_c_attribute are treated as if they were the name of defined macros.(since C23) If the expression evaluates to nonzero value, the controlled code block is included and skipped otherwise. If any used identifier is not a constant, it is replaced with 0.

In context of a preprocessor directive, a __has_c_attribute expression detects whether a given attribute token is supported and its supported version. See Attribute testing.

(since C23)

Note: Until DR 412, #if cond1 ... #elif cond2 is different from #if cond1 ... #else followed by #if cond3 because if cond1 is true, the second #if is skipped and cond3 does not need to be well-formed, while #elif's cond2 must be a valid expression. As of DR 412, #elif that leads the skipped code block is also skipped.

#### Combined directives

Checks if the identifier was defined as a macro name.

#ifdef identifier is essentially equivalent to #if defined identifier.

#ifndef identifier is essentially equivalent to #if !defined identifier.

#elifdef identifier is essentially equivalent to #elif defined identifier.

#elifndef identifier is essentially equivalent to #elif !defined identifier.

(since C23)

### Notes

While #elifdef and #elifndef directives target C23, implementations may backport them to the older language modes as conforming extensions.

### Example

```
#define ABCD 2
#include <stdio.h>

int main(void)
{

#ifdef ABCD
    printf("1: yes\n");
#else
    printf("1: no\n");
#endif

#ifndef ABCD
    printf("2: no1\n");
#elif ABCD == 2
    printf("2: yes\n");
#else
    printf("2: no2\n");
#endif

#if !defined(DCBA) && (ABCD < 2 * 4 - 3)
    printf("3: yes\n");
#endif

// C23 directives #elifdef/#elifndef
#ifdef CPU
    printf("4: no1\n");
#elifdef GPU
    printf("4: no2\n");
#elifndef RAM
    printf("4: yes\n"); // selected in C23 mode, may be selected in pre-C23 mode
#else
    printf("4: no3\n"); // may be selected in pre-C23 mode
#endif
}
```

Possible output:

```
1: yes
2: yes
3: yes
4: yes
```

### Defect reports

The following behavior-changing defect reports were applied retroactively to previously published C standards.

DR | Applied to | Behavior as published | Correct behavior

DR 412 | C89 | failed #elif's expression was required to be valid | failed #elif is skipped

### References

- C23 standard (ISO/IEC 9899:2024):

- 6.10.1 Conditional inclusion (p: TBD)

- C17 standard (ISO/IEC 9899:2018):

- 6.10.1 Conditional inclusion (p: 118-119)

- C11 standard (ISO/IEC 9899:2011):

- 6.10.1 Conditional inclusion (p: 162-164)

- C99 standard (ISO/IEC 9899:1999):

- 6.10.1 Conditional inclusion (p: 147-149)

- C89/C90 standard (ISO/IEC 9899:1990):

- 3.8.1 Conditional inclusion

### See also

C++ documentation for Conditional inclusion
