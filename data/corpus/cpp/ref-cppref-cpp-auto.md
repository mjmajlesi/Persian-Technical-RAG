Source: https://en.cppreference.com/w/cpp/language/auto
Retrieved: 2026-10-16
License: CC-BY-SA (cppreference.com)

# Placeholder type specifiers (since C++11) - cppreference.com

# Placeholder type specifiers (since C++11)

A placeholder type specifier designates a placeholder type that will be replaced later, typically by deduction from an initializer.

### Syntax

type-constraint ﻿(optional) auto | (1)

type-constraint ﻿(optional) decltype(auto) | (2) | (since C++14)

type-constraint | - | (since C++20) a concept name, optionally qualified, optionally followed by a template argument list enclosed in <>

The placeholder auto may be accompanied by modifiers, such as const or &, which will participate in the type deduction. The placeholder decltype(auto) must be the sole constituent of the declared type.(since C++14)

If type-constraint is present, let T be the type deduced for the placeholder, the type-constraint introduces a constraint expression as follows:

- If type-constraint is Concept<A1, ..., An>, then the constraint expression is Concept<T, A1, ..., An>;

- otherwise (type-constraint is Concept without an argument list), the constraint expression is Concept<T>.

Deduction fails if the constraint expression is invalid or returns false.

(since C++20)

### Explanation

A placeholder type specifier may appear in the following contexts:

#### Parameter declarations

In the following parameter declarations, the type of the parameter declared can be of syntax (1):

- If a parameter of a lambda expression has a placeholder type, the lambda expression is a generic lambda.

(since C++14)

- If a non-type template parameter has a placeholder type, its type is deduced from the corresponding template argument.

(since C++17)

- If a parameter of a function declaration has a placeholder type, an abbreviated function template is declared.

(since C++20)

#### Function declarations

A placeholder type can appear in the declaration specifiers for a function declarator that includes a trailing return type.

A placeholder type can appear in the declaration specifiers or type specifiers in the declared return type of a function declarator. Return type deduction will be applied in this case.

(since C++14)

```
auto f() -> int; // OK: f returns int
auto g() { return 0.0; } // OK since C++14: g returns double
auto h(); // OK since C++14: h’s return type will be deduced when it is defined
```

#### Variable declarations

The type of a variable declared using a placeholder type is deduced from its initializer. This use is allowed in an initializing declaration of a variable.

The placeholder type can only appear as one of the declaration specifiers in the declaration specifier sequence or as one of the type specifiers in a trailing return type that specifies the type that replaces such a declaration specifier. In this case, the declaration must declare at least one variable, and each variable must have a non-empty initializer.

```
// “auto”s in declaration specifiers
auto x = 5; // OK: x has type int
const auto *v = &x, u = 6; // OK: v has type const int*, u has type const int
static auto y = 0.0; // OK: y has type double

auto f() -> int;
auto (*fp)() -> auto = f; // OK: the “auto” in the trailing return type
                          // can be deduced from f
```

#### Structured binding declarations

The auto specifier can be used in a structured binding declaration.

(since C++17)

#### new expressions

A placeholder type can be used in the type specifier sequence of the type-id of a new expression. In such a type-id, the placeholder type must appear as one of the type specifiers in the type specifier sequence or a trailing return type that specifies the type that replaces such a type specifier.

#### Function-style cast

The auto type specifier can be used as the type specifier of a function-style cast.

(since C++23)

### Notes

Until C++11, auto had the semantic of a storage duration specifier.

A program that uses a placeholder type in a context not explicitly stated above is ill-formed.

If a declaration declares multiple entities, and the declaration specifier sequence uses a placeholder type, the program is ill-formed if any of the following conditions is satisfied:

- Some of the entities declared are not variables.

- The type that replaces the placeholder type is not the same in each deduction.

```
auto f() -> int, i = 0; // Error: declares a function and a variable with “auto”
auto a = 5, b = {1, 2}; // Error: different types for “auto”
```

The auto keyword may also be used in a nested name specifier. A nested name specifier of the form auto:: is a placeholder that is replaced by a class or enumeration type following the rules for constrained type placeholder deduction.

(concepts TS)

Feature-test macro | Value | Std | Feature

__cpp_decltype_auto | 201304L | (C++14) | decltype(auto)

### Keywords

auto, decltype

### Example

```
#include <iostream>
#include <utility>

template<class T, class U>
auto add(T t, U u) { return t + u; } // the return type is the type of operator+(T, U)

// perfect forwarding of a function call must use decltype(auto)
// in case the function it calls returns by reference
template<class F, class... Args>
decltype(auto) PerfectForward(F fun, Args&&... args) 
{ 
    return fun(std::forward<Args>(args)...); 
}

template<auto n> // C++17 auto parameter declaration
auto f() -> std::pair<decltype(n), decltype(n)> // auto can't deduce from brace-init-list
{
    return {n, n};
}

int main()
{
    auto a = 1 + 2;          // type of a is int
    auto b = add(1, 1.2);    // type of b is double
    static_assert(std::is_same_v<decltype(a), int>);
    static_assert(std::is_same_v<decltype(b), double>);
    
    auto c0 = a;             // type of c0 is int, holding a copy of a
    decltype(auto) c1 = a;   // type of c1 is int, holding a copy of a
    decltype(auto) c2 = (a); // type of c2 is int&, an alias of a
    std::cout << "before modification through c2, a = " << a << '\n';
    ++c2;
    std::cout << " after modification through c2, a = " << a << '\n';
    
    auto [v, w] = f<0>(); //structured binding declaration
    
    auto d = {1, 2}; // OK: type of d is std::initializer_list<int>
    auto n = {5};    // OK: type of n is std::initializer_list<int>
//  auto e{1, 2};    // Error as of DR n3922, std::initializer_list<int> before
    auto m{5};       // OK: type of m is int as of DR n3922, initializer_list<int> before
//  decltype(auto) z = { 1, 2 } // Error: {1, 2} is not an expression
    
    // auto is commonly used for unnamed types such as the types of lambda expressions
    auto lambda = [](int x) { return x + 3; };
    
//  auto int x; // valid C++98, error as of C++11
//  auto x;     // valid C, error in C++
    
    [](...){}(c0, c1, v, w, d, n, m, lambda); // suppresses "unused variable" warnings
}
```

Possible output:

```
before modification through c2, a = 3
 after modification through c2, a = 4
```

### Defect reports

The following behavior-changing defect reports were applied retroactively to previously published C++ standards.

DR | Applied to | Behavior as published | Correct behavior

CWG 1265 | C++11 | the auto specifier could be used to declare a function with a trailingreturn type and define a variable in one declaration statement | prohibited

CWG 1346 | C++11 | a parenthesized expression list could not be assigned to an auto variable | allowed

CWG 1347 | C++11 | a declaration with the auto specifier could define two variableswith types T and std::initializer_list<T> respectively | prohibited

CWG 1852 | C++14 | the auto specifier in decltype(auto) was also a placeholder | not a placeholderin this case

CWG 1892 | C++11 | the return type of a function pointer type-id could be auto | prohibited

CWG 2476 | C++11 | the resolution of CWG issue 1892 prohibited the deductionof the return type of function pointer variables from initializers | allowed

### References

- C++23 standard (ISO/IEC 14882:2024):

- 9.2.9.6 Placeholder type specifiers [dcl.spec.auto]

- C++20 standard (ISO/IEC 14882:2020):

- 9.2.8.5 Placeholder type specifiers [dcl.spec.auto]

- C++17 standard (ISO/IEC 14882:2017):

- 10.1.7.4 The auto specifier [dcl.spec.auto]

- C++14 standard (ISO/IEC 14882:2014):

- 7.1.6.4 auto specifier [dcl.spec.auto]

- C++11 standard (ISO/IEC 14882:2011):

- 7.1.6.4 auto specifier [dcl.spec.auto]
