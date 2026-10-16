Source: https://en.cppreference.com/w/cpp/language/range-for
Retrieved: 2026-10-16
License: CC-BY-SA (cppreference.com)

# Range-based for loop (since C++11) - cppreference.com

# Range-based for loop (since C++11)

Executes a for loop over a range.

Used as a more readable equivalent to the traditional for loop operating over a range of values, such as all elements in a container.

### Syntax

attr ﻿(optional) for ( init-statement ﻿(optional) item-declaration : range-initializer ) statement

attr | - | any number of attributes

- an expression statement (which may be a null statement ;)

- a simple declaration (typically a declaration of a variable with initializer), it may declare arbitrarily many variables or be a structured binding declaration

- an alias declaration

(since C++23)

Note that any init-statement must end with a semicolon. This is why it is often described informally as an expression or a declaration followed by a semicolon.

- a simple declaration where the init-declarator-list has only one init-declarator and no initializer

- a structured binding declaration without an initializer

(since C++17)

The declaration specifier sequence can only contain type specifiers and constexpr, and it cannot define a class or enumeration.

range-initializer | - | an expression or brace-enclosed initializer list

statement | - | any statement (typically a compound statement)

### Explanation

The above syntax produces code equivalent to the following  except for the lifetime expansion of temporaries of range-initializer (see below)(since C++23) (the variables and expressions wrapped in /* */ are for exposition only):

{

auto&& /* range */ = range-initializer ﻿;

for (auto /* begin */ = /* begin-expr */, /* end */ = /* end-expr */;

/* begin */ != /* end */; ++/* begin */)

{

item-declaration = */* begin */;

statement

}

(until C++17)

{

auto&& /* range */ = range-initializer ﻿;

auto /* begin */ = /* begin-expr */;

auto /* end */ = /* end-expr */;

for ( ; /* begin */ != /* end */; ++/* begin */)

{

item-declaration = */* begin */;

statement

}

(since C++17)(until C++20)

{

init-statement

auto&& /* range */ = range-initializer ﻿;

auto /* begin */ = /* begin-expr */;

auto /* end */ = /* end-expr */;

for ( ; /* begin */ != /* end */; ++/* begin */)

{

item-declaration = */* begin */;

statement

}

(since C++20)

range-initializer is evaluated to initialize the sequence or range to iterate. Each element of the sequence, in turn, is dereferenced and is used to initialize the variable with the type and name given in item-declaration.

Exposition-only expressions /* begin-expr */ and /* end-expr */ are defined as follows:

- If the type of /* range */ is a reference to an array type R:

- If R is of bound N, /* begin-expr */ is /* range */ and /* end-expr */ is /* range */ + N.

- If R is an array of unknown bound or an array of incomplete type, the program is ill-formed.

- If the type of /* range */ is a reference to a class type C, and searches in the scope of C for the names “begin” and “end” each find at least one declaration, then /* begin-expr */ is /* range */.begin() and /* end-expr */ is /* range */.end().

- Otherwise, /* begin-expr */ is begin(/* range */) and /* end-expr */ is end(/* range */), where “begin” and “end” are found via argument-dependent lookup (non-ADL lookup is not performed).

As a loop, a range-based for loop can contain break statements to exit the loop early and continue statements to end the current iteration and continue with the next element.

If a name introduced in init-statement is redeclared in the outermost block of statement, the program is ill-formed:

```
for (int i : {1, 2, 3})
    int i = 1; // error: redeclaration
```

### Temporary range initializer

If range-initializer returns a temporary, its lifetime is extended until the end of the loop, as indicated by binding to the forwarding reference /* range */.

Lifetimes of all temporaries within range-initializer are not extended unless they would otherwise be destroyed at the end of range-initializer(since C++23).

```
// if foo() returns by value
for (auto& x : foo().items()) { /* ... */ } // until C++23 undefined behavior
```

```
for (T thing = foo(); auto& x : thing.items()) { /* ... */ } // OK
```

This problem may be worked around by binding the temporary to a variable in the init-statement: | (since C++20)

Note that even in C++23 non-reference parameters of intermediate function calls do not get a lifetime extension (because in some ABIs they are destroyed in the callee, not in the caller), but that is only a problem for functions that are buggy anyway:

```
using T = std::list<int>;
const T& f1(const T& t) { return t; }
const T& f2(T t)        { return t; } // always returns a dangling reference
T g();

void foo()
{
    for (auto e : f1(g())) {} // OK: lifetime of return value of g() extended
    for (auto e : f2(g())) {} // UB: lifetime of f2's value parameter ends early
}
```

(since C++23)

### Notes

If the range-initializer is a braced-enclosed initializer list, /* range */ is deduced to be a reference to a std::initializer_list.

It is safe, and in fact, preferable in generic code, to use deduction to forwarding reference, for (auto&& var : sequence).

The member interpretation is used if the range type has a member named “begin” and a member named “end”. This is done regardless of whether the member is a type, data member, function, or enumerator, and regardless of its accessibility. Thus a class like class meow { enum { begin = 1, end = 2 }; /* rest of class */ }; cannot be used with the range-based for loop even if the namespace-scope “begin”/“end” functions are present.

While the variable declared in the item-declaration is usually used in the statement, doing so is not required.

As of C++17, the types of the /* begin-expr */ and the /* end-expr */ do not have to be the same, and in fact the type of the /* end-expr */ does not have to be an iterator: it just needs to be able to be compared for inequality with one. This makes it possible to delimit a range by a predicate (e.g. "the iterator points at a null character"). | (since C++17)

When used with a (non-const) object that has copy-on-write semantics, the range-based for loop may trigger a deep copy by (implicitly) calling the non-const begin() member function.

If that is undesirable (for instance because the loop is not actually modifying the object), it can be avoided by using std::as_const:

```
struct cow_string { /* ... */ }; // a copy-on-write string
cow_string str = /* ... */;

// for (auto x : str) { /* ... */ } // may cause deep copy

for (auto x : std::as_const(str)) { /* ... */ }
```

(since C++17)

Feature-test macro | Value | Std | Feature

__cpp_range_based_for | 200907L | (C++11) | Range-based for loop

201603L | (C++17) | Range-based for loop with different begin/end types

202211L | (C++23) | Lifetime extension for all temporary objects in range-initializer

### Keywords

for

### Example

```
#include <iostream>
#include <vector>

int main()
{
    std::vector<int> v = {0, 1, 2, 3, 4, 5};
    
    for (const int& i : v) // access by const reference
        std::cout << i << ' ';
    std::cout << '\n';
    
    for (auto i : v) // access by value, the type of i is int
        std::cout << i << ' ';
    std::cout << '\n';
    
    for (auto&& i : v) // access by forwarding reference, the type of i is int&
        std::cout << i << ' ';
    std::cout << '\n';
    
    const auto& cv = v;
    
    for (auto&& i : cv) // access by f-d reference, the type of i is const int&
        std::cout << i << ' ';
    std::cout << '\n';
    
    for (int n : {0, 1, 2, 3, 4, 5}) // the initializer may be a
                                     // braced-enclosed initializer list
        std::cout << n << ' ';
    std::cout << '\n';
    
    int a[] = {0, 1, 2, 3, 4, 5};
    for (int n : a) // the initializer may be an array
        std::cout << n << ' ';
    std::cout << '\n';
    
    for ([[maybe_unused]] int n : a)  
        std::cout << 1 << ' '; // the loop variable need not be used
    std::cout << '\n';
    
    for (auto n = v.size(); auto i : v) // the init-statement (C++20)
        std::cout << --n + i << ' ';
    std::cout << '\n';
    
    for (typedef decltype(v)::value_type elem_t; elem_t i : v)
    // typedef declaration as init-statement (C++20)
        std::cout << i << ' ';
    std::cout << '\n';
    
    for (using elem_t = decltype(v)::value_type; elem_t i : v)
    // alias declaration as init-statement (C++23)
        std::cout << i << ' ';
    std::cout << '\n';
}
```

Output:

```
0 1 2 3 4 5 
0 1 2 3 4 5 
0 1 2 3 4 5 
0 1 2 3 4 5 
0 1 2 3 4 5 
0 1 2 3 4 5 
1 1 1 1 1 1 
5 5 5 5 5 5 
0 1 2 3 4 5 
0 1 2 3 4 5
```

### Defect reports

The following behavior-changing defect reports were applied retroactively to previously published C++ standards.

DR | Applied to | Behavior as published | Correct behavior

CWG 1442 | C++11 | it was unspecified whether the lookup of non-member“begin” and “end” includes usual unqualified lookup | no usual unqualified lookup

CWG 2220 | C++11 | the names introduced in init-statement could be redeclared | the program is ill-formed in this case

CWG 2825 | C++11 | if range-initializer is a brace-enclosed initializer list,the non-member “begin” and “end” will be looked up | will lookup member “begin”and “end” in this case

P0962R1 | C++11 | member interpretation was used if eithermember “begin” and “end” is present | only used if both are present

### See also

for_each | applies a unary function object to elements from a range(function template & algorithm function object)[edit]

ranges::for_each(C++20)
