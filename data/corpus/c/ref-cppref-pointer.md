Source: https://en.cppreference.com/w/c/language/pointer
Retrieved: 2026-09-23
License: CC-BY-SA (cppreference.com)

# Pointer declaration - cppreference.com

# Pointer declaration

Pointer is a type of an object that refers to a function or an object of another type, possibly adding qualifiers. Pointer may also refer to nothing, which is indicated by the special null pointer value.

### Syntax

In the declaration grammar of a pointer declaration, the type-specifier sequence designates the pointed-to type (which may be function or object type and may be incomplete), and the declarator has the form:

* attr-spec-seq ﻿(optional) qualifiers ﻿(optional) declarator

where declarator may be the identifier that names the pointer being declared, including another pointer declarator (which would indicate a pointer to a pointer):

```
float *p, **pp; // p is a pointer to float
                // pp is a pointer to a pointer to float
int (*fp)(int); // fp is a pointer to function with type int(int)
```

The qualifiers that appear between * and the identifier (or other nested declarator) qualify the type of the pointer that is being declared:

```
int n;
const int * pc = &n; // pc is a non-const pointer to a const int
// *pc = 2; // Error: n cannot be changed through pc without a cast
pc = NULL; // OK: pc itself can be changed

int * const cp = &n; // cp is a const pointer to a non-const int
*cp = 2; // OK to change n through cp
// cp = NULL; // Error: cp itself cannot be changed

int * const * pcp = &cp; // non-const pointer to const pointer to non-const int
```

The attr-spec-seq(C23) is an optional list of attributes, applied to the declared pointer.

### Explanation

Pointers are used for indirection, which is a ubiquitous programming technique; they can be used to implement pass-by-reference semantics, to access objects with dynamic storage duration, to implement "optional" types (using the null pointer value), aggregation relationship between structs, callbacks (using pointers to functions), generic interfaces (using pointers to void), and much more.

#### Pointers to objects

A pointer to object can be initialized with the result of the address-of operator applied to an expression of object type (which may be incomplete):

```
int n;
int *np = &n; // pointer to int
int *const *npp = &np; // non-const pointer to const pointer to non-const int

int a[2];
int (*ap)[2] = &a; // pointer to array of int

struct S { int n; } s = {1}
int* sp = &s.n; // pointer to the int that is a member of s
```

Pointers may appear as operands to the indirection operator (unary *), which returns the lvalue identifying the pointed-to object:

```
int n;
int* p = &n; // pointer p is pointing to n
*p = 7; // stores 7 in n
printf("%d\n", *p); // lvalue-to-rvalue conversion reads the value from n
```

Pointers to objects of struct and union type may also appear as the left-hand operands of the member access through pointer operator ->.

Because of the array-to-pointer implicit conversion, pointer to the first element of an array can be initialized with an expression of array type:

```
int a[2];
int *p = a; // pointer to a[0]

int b[3][3];
int (*row)[3] = b; // pointer to b[0]
```

Certain addition, subtraction, compound assignment, increment, and decrement operators are defined for pointers to elements of arrays.

Comparison operators are defined for pointers to objects in some situations: two pointers that represent the same address compare equal, two null pointer values compare equal, pointers to elements of the same array compare the same as the array indices of those elements, and pointers to struct members compare in order of declaration of those members.

Many implementations also provide strict total ordering of pointers of random origin, e.g. if they are implemented as addresses within continuous ("flat") virtual address space.

#### Pointers to functions

A pointer to function can be initialized with an address of a function. Because of the function-to-pointer conversion, the address-of operator is optional:

```
void f(int);
void (*pf1)(int) = &f;
void (*pf2)(int) = f; // same as &f
```

Unlike functions, pointers to functions are objects and thus can be stored in arrays, copied, assigned, passed to other functions as arguments, etc.

A pointer to function can be used on the left-hand side of the function call operator; this invokes the pointed-to function:

```
#include <stdio.h>

int f(int n)
{
    printf("%d\n", n);
    return n * n;
}

int main(void)
{
    int (*p)(int) = f;
    int x = p(7);
}
```

Dereferencing a function pointer yields the function designator for the pointed-to function:

```
int f();
int (*p)() = f;    // pointer p is pointing to f
(*p)(); // function f invoked through the function designator
p();    // function f invoked directly through the pointer
```

Equality comparison operators are defined for pointers to functions (they compare equal if pointing to the same function).

Because compatibility of function types ignores top-level qualifiers of the function parameters, pointers to functions whose parameters only differ in their top-level qualifiers are interchangeable:

```
int f(int), fc(const int);
int (*pc)(const int) = f; // OK
int (*p)(int) = fc;       // OK
pc = p;                   // OK
```

#### Pointers to void

Pointer to object of any type can be implicitly converted to pointer to void (optionally const or volatile-qualified), and vice versa:

```
int n=1, *p=&n;
void* pv = p; // int* to void*
int* p2 = pv; // void* to int*
printf("%d\n", *p2); // prints 1
```

Pointers to void are used to pass objects of unknown type, which is common in generic interfaces: malloc returns void*, qsort expects a user-provided callback that accepts two const void* arguments. pthread_create expects a user-provided callback that accepts and returns void*. In all cases, it is the caller's responsibility to convert the pointer to the correct type before use.

### Null pointers

Pointers of every type have a special value known as null pointer value of that type. A pointer whose value is null does not point to an object or a function (dereferencing a null pointer is undefined behavior), and compares equal to all pointers of the same type whose value is also null.

To initialize a pointer to null or to assign the null value to an existing pointer, a null pointer constant (NULL, or any other integer constant with the value zero) may be used. static initialization also initializes pointers to their null values.

Null pointers can indicate the absence of an object or can be used to indicate other types of error conditions. In general, a function that receives a pointer argument almost always needs to check if the value is null and handle that case differently (for example, free does nothing when a null pointer is passed).

### Notes

Although any pointer to object can be cast to pointer to object of a different type, dereferencing a pointer to the type different from the declared type of the object is almost always undefined behavior. See strict aliasing for details.

It is possible to indicate to a function that accesses objects through pointers that those pointers do not alias. See restrict for details.

(since C99)

lvalue expressions of array type, when used in most contexts, undergo an implicit conversion to the pointer to the first element of the array. See array for details.

```
char *str = "abc"; // "abc" is a char[4] array, str is a pointer to 'a'
```

Pointers to char are often used to represent strings. To represent a valid byte string, a pointer must be pointing at a char that is an element of an array of char, and there must be a char with the value zero at some index greater or equal to the index of the element referenced by the pointer.

### References

- C23 standard (ISO/IEC 9899:2024):

- 6.7.6.1 Pointer declarators (p: TBD)

- C17 standard (ISO/IEC 9899:2018):

- 6.7.6.1 Pointer declarators (p: 93-94)

- C11 standard (ISO/IEC 9899:2011):

- 6.7.6.1 Pointer declarators (p: 130)

- C99 standard (ISO/IEC 9899:1999):

- 6.7.5.1 Pointer declarators (p: 115-116)

- C89/C90 standard (ISO/IEC 9899:1990):

- 3.5.4.1 Pointer declarators

### See also

C++ documentation for Pointer declaration
