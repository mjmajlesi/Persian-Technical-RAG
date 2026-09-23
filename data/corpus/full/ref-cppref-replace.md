Source: https://en.cppreference.com/w/c/preprocessor/replace
Retrieved: 2026-09-23
License: CC-BY-SA (cppreference.com)

# Replacing text macros - cppreference.com

# Replacing text macros

The preprocessor supports text macro replacement and function-like text macro replacement.

### Syntax

#define identifier replacement-list ﻿(optional) | (1)

#define identifier ﻿( parameters ) replacement-list | (2)

#define identifier ﻿( parameters, ... ) replacement-list | (3) | (since C99)

#define identifier ﻿( ... ) replacement-list | (4) | (since C99)

#undef identifier | (5)

### Explanation

#### #define directives

The #define directives define the identifier as a macro, that is they instruct the compiler to replace all successive occurrences of identifier with replacement-list, which can be optionally additionally processed. If the identifier is already defined as any type of macro, the program is ill-formed unless the definitions are identical.

Object-like macros replace every occurrence of a defined identifier with replacement-list. Version (1) of the #define directive behaves exactly like that.

Function-like macros replace each occurrence of a defined identifier with replacement-list, additionally taking a number of arguments, which then replace corresponding occurrences of any of the parameters in the replacement-list.

The syntax of a function-like macro invocation is similar to the syntax of a function call: each instance of the macro name followed by a ( as the next preprocessing token introduces the sequence of tokens that is replaced by the replacement-list. The sequence is terminated by the matching ) token, skipping intervening matched pairs of left and right parentheses.

The number of arguments must be the same as the number of arguments in the macro definition (parameters) or the program is ill-formed. If the identifier is not in functional-notation, i.e. does not have parentheses after itself, it is not replaced at all.

Version (2) of the #define directive defines a simple function-like macro.

Version (3) of the #define directive defines a function-like macro with variable number of arguments. The additional arguments can be accessed using __VA_ARGS__ identifier, which is then replaced with arguments, supplied with the identifier to be replaced.

Version (4) of the #define directive defines a function-like macro with variable number of arguments, but no regular arguments. The arguments can be accessed only with __VA_ARGS__ identifier, which is then replaced with arguments, supplied with identifier to be replaced.

For versions (3,4), replacement-list may contain the token sequence __VA_OPT__ ( content ), which is replaced by content if __VA_ARGS__ is non-empty, and expands to nothing otherwise.

```
#define F(...) f(0 __VA_OPT__(,) __VA_ARGS__)
F(a, b, c) // replaced by f(0, a, b, c)
F()        // replaced by f(0)

#define G(X, ...) f(0, X __VA_OPT__(,) __VA_ARGS__)
G(a, b, c) // replaced by f(0, a, b, c)
G(a, )     // replaced by f(0, a)
G(a)       // replaced by f(0, a)

#define SDEF(sname, ...) S sname __VA_OPT__(= { __VA_ARGS__ })
SDEF(foo);       // replaced by S foo;
SDEF(bar, 1, 2); // replaced by S bar = { 1, 2 };
```

(since C23)

Note: if an argument of a function-like macro includes commas that are not protected by matched pairs of left and right parentheses (such as macro(array[x = y, x + 1]) or atomic_store (p, (struct S){ a, b });), the comma is interpreted as macro argument separator, causing a compilation failure due to argument count mismatch.

#### # and ## operators

In function-like macros, a # operator before an identifier in the replacement-list runs the identifier through parameter replacement and encloses the result in quotes, effectively creating a string literal. In addition, the preprocessor adds backslashes to escape the quotes surrounding embedded string literals, if any, and doubles the backslashes within the string as necessary. All leading and trailing whitespace is removed, and any sequence of whitespace in the middle of the text (but not inside embedded string literals) is collapsed to a single space. This operation is called "stringification". If the result of stringification is not a valid string literal, the behavior is undefined.

When # appears before __VA_ARGS__, the entire expanded __VA_ARGS__ is enclosed in quotes:

```
#define showlist(...) puts(#__VA_ARGS__)
showlist();            // expands to puts("")
showlist(1, "x", int); // expands to puts("1, \"x\", int")
```

(since C99)

A ## operator between any two successive identifiers in the replacement-list runs parameter replacement on the two identifiers and then concatenates the result. This operation is called "concatenation" or "token pasting". Only tokens that form a valid token together may be pasted: identifiers that form a longer identifier, digits that form a number, or operators + and = that form a +=. A comment cannot be created by pasting / and * because comments are removed from text before macro substitution is considered. If the result of concatenation is not a valid token, the behavior is undefined.

Note: Some compilers offer an extension that allows ## to appear after a comma and before __VA_ARGS__, in which case the ## does nothing when __VA_ARGS__ is non-empty, but removes the comma when __VA_ARGS__ is empty: this makes it possible to define macros such as fprintf (stderr, format, ##__VA_ARGS__).

The order of evaluation of # and ## operators is unspecified.

#### #undef directive

The #undef directive undefines the identifier, that is it cancels the previous definition of the identifier by #define directive. If the identifier does not have an associated macro, the directive is ignored.

### Predefined macros

The following macro names are predefined in any translation unit:

__STDC__ | expands to the integer constant 1. This macro is intended to indicate a conforming implementation  (macro constant)

- 199409L (C95)

- 199901L (C99)

- 201112L (C11)

- 201710L (C17)

- 202311L (C23)  (macro constant)

__STDC_VERSION__(C95) | expands to an integer constant of type long whose value increases with each version of the C standard:

__STDC_HOSTED__(C99) | expands to the integer constant 1 if the implementation is hosted (runs under an OS), 0 if freestanding (runs without an OS)  (macro constant)

__FILE__ | expands to the name of the current file, as a character string literal, can be changed by the #line directive  (macro constant)

__LINE__ | expands to the source file line number, an integer constant, can be changed by the #line directive  (macro constant)

__DATE__ | expands to the date of translation, a character string literal of the form "Mmm dd yyyy". The name of the month is as if generated by asctime and the first character of "dd" is a space if the day of the month is less than 10  (macro constant)

__TIME__ | expands to the time of translation, a character string literal of the form "hh:mm:ss", as in the time generated by asctime()  (macro constant)

__STDC_UTF_16__(C23) | expands to 1 to indicate that char16_t use UTF-16 encoding  (macro constant)

__STDC_UTF_32__(C23) | expands to 1 to indicate that char32_t use UTF-32 encoding  (macro constant)

__STDC_EMBED_NOT_FOUND____STDC_EMBED_FOUND____STDC_EMBED_EMPTY__(C23) | expand to 0, 1, and 2, respectively  (macro constant)

The following additional macro names may be predefined by an implementation:

__STDC_ISO_10646__(C99) | expands to an integer constant of the form yyyymmL, if wchar_t uses Unicode; the date indicates the latest revision of Unicode supported  (macro constant)

__STDC_IEC_559__(C99) | expands to 1 if IEC 60559 is supported (deprecated)(since C23)  (macro constant)

__STDC_IEC_559_COMPLEX__(C99) | expands to 1 if IEC 60559 complex arithmetic is supported (deprecated)(since C23)  (macro constant)

__STDC_UTF_16__(C11) | expands to 1 if char16_t use UTF-16 encoding  (macro constant)

__STDC_UTF_32__(C11) | expands to 1 if char32_t use UTF-32 encoding  (macro constant)

__STDC_MB_MIGHT_NEQ_WC__(C99) | expands to 1 if 'x' == L'x' might be false for a member of the basic character set, such as on EBCDIC-based systems that use Unicode for wchar_t  (macro constant)

__STDC_ANALYZABLE__(C11) | expands to 1 if analyzability is supported  (macro constant)

__STDC_LIB_EXT1__(C11) | expands to an integer constant 201112L if bounds-checking interfaces are supported  (macro constant)

__STDC_NO_ATOMICS__(C11) | expands to 1 if atomic types and atomic operations library are not supported  (macro constant)

__STDC_NO_COMPLEX__(C11) | expands to 1 if complex types and complex math library are not supported  (macro constant)

__STDC_NO_THREADS__(C11) | expands to 1 if multithreading is not supported  (macro constant)

__STDC_NO_VLA__(C11) | expands to 1 if variable-length arrays and variably-modified types(until C23)of automatic storage duration(since C23) are not supported  (macro constant)

__STDC_IEC_60559_BFP__(C23) | expands to 202311L if IEC 60559 binary floating-point arithmetic is supported  (macro constant)

__STDC_IEC_60559_DFP__(C23) | expands to 202311L if IEC 60559 decimal floating-point arithmetic is supported  (macro constant)

__STDC_IEC_60559_COMPLEX__(C23) | expands to 202311L if IEC 60559 complex arithmetic is supported  (macro constant)

__STDC_IEC_60559_TYPES__(C23) | expands to 202311L if IEC 60559 interchange and extended types are supported  (macro constant)

The values of these macros (except for __FILE__ and __LINE__) remain constant throughout the translation unit. Attempts to redefine or undefine these macros result in undefined behavior.

The predefined variable __func__ (see function definition for details) is not a preprocessor macro, even though it is sometimes used together with __FILE__ and __LINE__, e.g. by assert.

(since C99)

### Example

```
#include <stdio.h>

// make function factory and use it
#define FUNCTION(name, a) int fun_##name(int x) { return (a) * x; }

FUNCTION(quadruple, 4)
FUNCTION(double, 2)

#undef FUNCTION
#define FUNCTION 34
#define OUTPUT(a) puts( #a )

int main(void)
{
    printf("quadruple(13): %d\n", fun_quadruple(13) );
    printf("double(21): %d\n", fun_double(21) );
    printf("%d\n", FUNCTION);
    OUTPUT(billion);               // note the lack of quotes
}
```

Output:

```
quadruple(13): 52
double(21): 42
34
billion
```

### Defect reports

The following behavior-changing defect reports were applied retroactively to previously published C standards.

DR | Applied to | Behavior as published | Correct behavior

DR 321 | C99 | it was unclear if L'x' == 'x' always holdsamong the basic character set | __STDC_MB_MIGHT_NEQ_WC__ added for the purpose

### References

- C23 standard (ISO/IEC 9899:2024):

- 6.10.4 Macro replacement (p: 187-184)

- 6.10.9 Predefined macro names (p: 186-188)

- C17 standard (ISO/IEC 9899:2018):

- 6.10.3 Macro replacement (p: 121-126)

- 6.10.8 Predefined macro names (p: 127-129)

- C11 standard (ISO/IEC 9899:2011):

- 6.10.3 Macro replacement (p: 166-173)

- 6.10.8 Predefined macro names (p: 175-176)

- C99 standard (ISO/IEC 9899:1999):

- 6.10.3 Macro replacement (p: 151-158)

- 6.10.8 Predefined macro names (p: 160-161)

- C89/C90 standard (ISO/IEC 9899:1990):

- 3.8.3 Macro replacement

- 3.8.8 Predefined macro names

### See also

C++ documentation for Replacing text macros
