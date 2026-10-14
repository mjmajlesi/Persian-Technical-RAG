Source: https://en.cppreference.com/w/c/language/struct
Retrieved: 2026-09-23
License: CC-BY-SA (cppreference.com)

# Struct declaration - cppreference.com

# Struct declaration

A struct is a type consisting of a sequence of members whose storage is allocated in an ordered sequence (as opposed to union, which is a type consisting of a sequence of members whose storage overlaps).

The type specifier for a struct is identical to the union type specifier except for the keyword used:

### Syntax

struct attr-spec-seq ﻿(optional) name ﻿(optional) { struct-declaration-list } | (1)

struct attr-spec-seq ﻿(optional) name | (2)

name | - | the name of the struct that's being defined

struct-declaration-list | - | any number of variable declarations, bit-field declarations, and static assert declarations. Members of incomplete type and members of function type are not allowed (except for the flexible array member described below)

attr-spec-seq | - | (C23)optional list of attributes, applied to the struct type

### Explanation

Within a struct object, addresses of its elements (and the addresses of the bit-field allocation units) increase in order in which the members were defined. A pointer to a struct can be cast to a pointer to its first member (or, if the member is a bit-field, to its allocation unit). Likewise, a pointer to the first member of a struct can be cast to a pointer to the enclosing struct. There may be unnamed padding between any two members of a struct or after the last member, but not before the first member. The size of a struct is at least as large as the sum of the sizes of its members.

If a struct defines at least one named member, it is allowed to additionally declare its last member with incomplete array type. When an element of the flexible array member is accessed (in an expression that uses operator . or -> with the flexible array member's name as the right-hand-side operand), then the struct behaves as if the array member had the longest size fitting in the memory allocated for this object. If no additional storage was allocated, it behaves as if an array with 1 element, except that the behavior is undefined if that element is accessed or a pointer one past that element is produced. Initialization and the assignment operator ignore the flexible array member. sizeof omits it, but may have more trailing padding than the omission would imply. Structures with flexible array members (or unions who have a recursive-possibly structure member with flexible array member) cannot appear as array elements or as members of other structures.

```
struct s { int n; double d[]; }; // s.d is a flexible array member

struct s t1 = { 0 };          // OK, d is as if double d[1], but UB to access
struct s t2 = { 1, { 4.2 } }; // error: initialization ignores flexible array

// if sizeof (double) == 8
struct s *s1 = malloc(sizeof (struct s) + 64); // as if d was double d[8]
struct s *s2 = malloc(sizeof (struct s) + 40); // as if d was double d[5]

s1 = malloc(sizeof (struct s) + 10); // now as if d was double d[1]. Two bytes excess.
double *dp = &(s1->d[0]);    // OK
*dp = 42;                    // OK
s1->d[1]++;                  // Undefined behavior. 2 excess bytes can't be accessed
                             // as double.

s2 = malloc(sizeof (struct s) + 6);  // same, but UB to access because 2 bytes are
                                     // missing to complete 1 double
dp = &(s2->d[0]);            // OK, can take address just fine
*dp = 42;                    // undefined behavior

*s1 = *s2; // only copies s.n, not any element of s.d
           // except those caught in sizeof (struct s)
```

(since C99)

Similar to union, an unnamed member of a struct whose type is a struct without name is known as anonymous struct. Every member of an anonymous struct is considered to be a member of the enclosing struct or union, keeping their structure layout. This applies recursively if the enclosing struct or union is also anonymous.

```
struct v
{
   union // anonymous union
   {
      struct { int i, j; }; // anonymous structure
      struct { long k, l; } w;
   };
   int m;
} v1;

v1.i = 2;   // valid
v1.k = 3;   // invalid: inner structure is not anonymous
v1.w.k = 5; // valid
```

Similar to union, the behavior of the program is undefined if struct is defined without any named members (including those obtained via anonymous nested structs or unions).

(since C11)

### Forward declaration

A declaration of the following form

struct attr-spec-seq ﻿(optional) name ;

hides any previously declared meaning for the name name in the tag name space and declares name as a new struct name in current scope, which will be defined later. Until the definition appears, this struct name has incomplete type.

This allows structs that refer to each other:

```
struct y;
struct x { struct y *p; /* ... */ };
struct y { struct x *q; /* ... */ };
```

Note that a new struct name may also be introduced just by using a struct tag within another declaration, but if a previously declared struct with the same name exists in the tag name space, the tag would refer to that name

```
struct s* p = NULL; // tag naming an unknown struct declares it
struct s { int a; }; // definition for the struct pointed to by p
void g(void)
{
    struct s; // forward declaration of a new, local struct s
              // this hides global struct s until the end of this block
    struct s *p;  // pointer to local struct s
                  // without the forward declaration above,
                  // this would point at the file-scope s
    struct s { char* p; }; // definitions of the local struct s
}
```

### Keywords

struct

### Notes

See struct initialization for the rules regarding the initializers for structs.

Because members of incomplete type are not allowed, and a struct type is not complete until the end of the definition, a struct cannot have a member of its own type. A pointer to its own type is allowed, and is commonly used to implement nodes in linked lists or trees.

Because a struct declaration does not establish scope, nested types, enumerations and enumerators introduced by declarations within struct-declaration-list are visible in the surrounding scope where the struct is defined.

### Example

```
#include <stddef.h>
#include <stdio.h>

int main(void)
{
    // Declare the struct type.
    struct car
    {
        char* make;
        int year;
    };
    // Declare and initialize an object of a previously-declared struct type.
    struct car c = {.year = 1923, .make = "Nash"};
    printf("1) Car: %d %s\n", c.year, c.make);

    // Declare a struct type, an object of that type, and a pointer to it.
    struct spaceship
    {
        char* model;
        int max_speed;
    } ship = {"T-65 X-wing starfighter", 1050},
    *pship = &ship;
    printf("2) Spaceship: %s. Max speed: %d km/h\n\n", ship.model, ship.max_speed);

    // Address increase in order of definition. Padding may be inserted.
    struct A { char a; double b; char c; };
    printf(
        "3) Offset of char a = %zu\n"
        "4) Offset of double b = %zu\n"
        "5) Offset of char c = %zu\n"
        "6) Size of struct A = %zu\n\n",
        offsetof(struct A, a),
        offsetof(struct A, b),
        offsetof(struct A, c),
        sizeof(struct A)
    );
    struct B { char a; char b; double c; };
    printf(
        "7) Offset of char a = %zu\n"
        "8) Offset of char b = %zu\n"
        "9) Offset of double c = %zu\n"
        "A) Size of struct B = %zu\n\n",
        offsetof(struct B, a),
        offsetof(struct B, b),
        offsetof(struct B, c),
        sizeof(struct B)
    );

    // A pointer to a struct can be cast to a pointer
    // to its first member and vice versa.
    char** pmodel = (char **)pship;
    printf("B) %s\n", *pmodel);
    pship = (struct spaceship *)pmodel;
}
```

Possible output:

```
1) Car: 1923 Nash
2) Spaceship: T-65 X-wing starfighter. Max speed: 1050 km/h

3) Offset of char a = 0
4) Offset of double b = 8
5) Offset of char c = 16
6) Size of struct A = 24

7) Offset of char a = 0
8) Offset of char b = 1
9) Offset of double c = 8
A) Size of struct B = 16

B) T-65 X-wing starfighter
```

### Defect reports

The following behavior-changing defect reports were applied retroactively to previously published C standards.

DR | Applied to | Behavior as published | Correct behavior

DR 499 | C11 | members of anonymous structs/unions were considered members of the enclosing struct/union | they retain their memory layout

### References

- C23 standard (ISO/IEC 9899:2024):

- 6.7.2.1 Structure and union specifiers (p: TBD)

- C17 standard (ISO/IEC 9899:2018):

- 6.7.2.1 Structure and union specifiers (p: 81-84)

- C11 standard (ISO/IEC 9899:2011):

- 6.7.2.1 Structure and union specifiers (p: 112-117)

- C99 standard (ISO/IEC 9899:1999):

- 6.7.2.1 Structure and union specifiers (p: 101-104)

- C89/C90 standard (ISO/IEC 9899:1990):

- 3.5.2.1 Structure and union specifiers

### See also

- struct and union member access

- bit-field

- struct initialization

C++ documentation for Class declaration
