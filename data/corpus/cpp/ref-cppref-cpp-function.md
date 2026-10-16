Source: https://en.cppreference.com/w/cpp/language/function
Retrieved: 2026-10-16
License: CC-BY-SA (cppreference.com)

# Function declaration - cppreference.com

# Function declaration

A function declaration introduces the function name and its type. A function definition associates the function name/type with the function body.

### Function declaration

Function declarations may appear in any scope. A function declaration at class scope introduces a class member function (unless the friend specifier is used), see member functions and friend functions for details.

noptr-declarator ( parameter-list ) cv ﻿(optional) ref ﻿ ﻿(optional) except ﻿(optional) attr ﻿(optional) | (1)

noptr-declarator ( parameter-list ) cv ﻿(optional) ref ﻿ ﻿(optional) except ﻿(optional) attr ﻿(optional)-> trailing | (2) | (since C++11)

(see Declarations for the other forms of the declarator syntax)

noptr-declarator | - | any valid declarator, but if it begins with *, &, or &&, it has to be surrounded by parentheses.

parameter-list | - | possibly empty, comma-separated list of the function parameters (see below for details)

attr | - | (since C++11) a list of attributes. These attributes are applied to the type of the function, not the function itself. The attributes for the function appear after the identifier within the declarator and are combined with the attributes that appear in the beginning of the declaration, if any.

cv | - | const/volatile qualification, only allowed in non-static member function declarations

ref | - | (since C++11) ref-qualification, only allowed in non-static member function declarations

dynamic exception specification

(until C++11)

either dynamic exception specificationor noexcept specification

(since C++11)(until C++17)

noexcept specification

(since C++17)

trailing | - | Trailing return type, useful if the return type depends on argument names, such as template<class T, class U> auto add(T t, U u) -> decltype(t + u); or is complicated, such as in auto fpif(int)->int(*)(int)

As mentioned in Declarations, the declarator can be followed by a requires clause, which declares the associated constraints for the function, which must be satisfied in order for the function to be selected by overload resolution. (example: void f1(int a) requires true;) Note that the associated constraint is part of function signature, but not part of function type.

(since C++20)

Function declarators can be mixed with other declarators, where the declaration specifier sequence allows:

```
// declares an int, an int*, a function, and a pointer to a function
int a = 1, *p = NULL, f(), (*pf)(double);
// decl-specifier-seq is int
// declarator f() declares (but doesn't define)
//                a function taking no arguments and returning int

struct S
{
    virtual int f(char) const, g(int) &&; // declares two non-static member functions
    virtual int f(char), x; // compile-time error: virtual (in decl-specifier-seq)
                            // is only allowed in declarations of non-static
                            // member functions
};
```

Using a volatile-qualified object type as parameter type or return type is deprecated.

(since C++20)

The return type of a function cannot be a function type or an array type (but can be a pointer or reference to those).

As with any declaration, attributes that appear before the declaration and the attributes that appear immediately after the identifier within the declarator both apply to the entity being declared or defined (in this case, to the function):

```
[[noreturn]] void f [[noreturn]] (); // OK: both attributes apply to the function f
```

However, the attributes that appear after the declarator (in the syntax above), apply to the type of the function, not to the function itself:

```
void f() [[noreturn]]; // Error: this attribute has no effect on the function itself
```

(since C++11)

### Return type deduction

If the decl-specifier-seq of the function declaration contains the keyword auto, trailing return type may be omitted, and will be deduced by the compiler from the type of the operand used in the return statement. If the return type does not use decltype(auto), the deduction follows the rules of template argument deduction:

```
int x = 1;
auto f() { return x; }        // return type is int
const auto& f() { return x; } // return type is const int&
```

If the return type is decltype(auto), the return type is as what would be obtained if the operand used in the return statement were wrapped in decltype:

```
int x = 1;
decltype(auto) f() { return x; }  // return type is int, same as decltype(x)
decltype(auto) f() { return(x); } // return type is int&, same as decltype((x))
```

(note: “const decltype(auto)&” is an error, decltype(auto) must be used on its own)

If there are multiple return statements, they must all deduce to the same type:

```
auto f(bool val)
{
    if (val) return 123; // deduces return type int
    else return 3.14f;   // Error: deduces return type float
}
```

If there is no return statement or if the operand of the return statement is a void expression, the declared return type must be either decltype(auto), in which case the deduced return type is void, or (possibly cv-qualified) auto, in which case the deduced return type is then (identically cv-qualified) void:

```
auto f() {}              // returns void
auto g() { return f(); } // returns void
auto* x() {}             // Error: cannot deduce auto* from void
```

Once a return statement has been seen in a function, the return type deduced from that statement can be used in the rest of the function, including in other return statements:

```
auto sum(int i)
{
    if (i == 1)
        return i;              // sum’s return type is int
    else
        return sum(i - 1) + i; // OK: sum’s return type is already known
}
```

If the return statement uses a brace-enclosed initializer list, deduction is not allowed:

```
auto func() { return {1, 2, 3}; } // Error
```

Virtual functions and coroutines(since C++20) cannot use return type deduction:

```
struct F
{
    virtual auto f() { return 2; } // Error
};
```

Function templates other than user-defined conversion functions can use return type deduction. The deduction takes place at instantiation even if the expression in the return statement is not dependent. This instantiation is not in an immediate context for the purposes of SFINAE.

```
template<class T>
auto f(T t) { return t; }
typedef decltype(f(1)) fint_t;    // instantiates f<int> to deduce return type

template<class T>
auto f(T* t) { return *t; }
void g() { int (*p)(int*) = &f; } // instantiates both fs to determine return types,
                                  // chooses second template overload
```

Redeclarations or specializations of functions or function templates that use return type deduction must use the same return type placeholders:

```
auto f(int num) { return num; }
// int f(int num);            // Error: no placeholder return type
// decltype(auto) f(int num); // Error: different placeholder

template<typename T>
auto g(T t) { return t; }
template auto g(int);     // OK: return type is int
// template char g(char); // Error: not a specialization of the primary template g
```

Similarly, redeclarations or specializations of functions or function templates that do not use return type deduction must not use a placeholder:

```
int f(int num);
// auto f(int num) { return num; } // Error: not a redeclaration of f

template<typename T>
T g(T t) { return t; }
template int g(int);      // OK: specialize T as int
// template auto g(char); // Error: not a specialization of the primary template g
```

Explicit instantiation declarations do not themselves instantiate function templates that use return type deduction:

```
template<typename T>
auto f(T t) { return t; }
extern template auto f(int); // does not instantiate f<int>

int (*p)(int) = f; // instantiates f<int> to determine its return type,
                   // but an explicit instantiation definition 
                   // is still required somewhere in the program
```

(since C++14)

### Parameter list

The parameter list determines the arguments that can be specified when the function is called. It is a comma-separated list of parameter declarations, each of which has the following syntax:

attr ﻿(optional) decl-specifier-seq declarator | (1)

attr ﻿(optional) this decl-specifier-seq declarator

(2) | (since C++23)

attr ﻿(optional) decl-specifier-seq declarator = initializer | (3)

attr ﻿(optional) decl-specifier-seq abstract-declarator ﻿(optional) | (4)

attr ﻿(optional) this decl-specifier-seq abstract-declarator ﻿(optional)

(5) | (since C++23)

attr ﻿(optional) decl-specifier-seq abstract-declarator ﻿(optional) = initializer | (6)

void | (7)

Incorrect usage | Example

multiple parameters are present | int f1(void, int);

the void parameter is named | inf f2(void param);

void is cv-qualified | int f3(const void);

void is dependent | int f4(T); (where T is void)

the void parameter is an explicit object parameter (since C++23) | int f5(this void);

Although decl-specifier-seq implies there can exist specifiers other than type specifiers, the only other specifier allowed is register as well as auto(until C++11), and it has no effect.

(until C++17)

If any of the function parameters uses a placeholder (either auto or a concept type), the function declaration is instead an abbreviated function template declaration:

```
void f1(auto);    // same as template<class T> void f1(T)
void f2(C1 auto); // same as template<C1 T> void f2(T), if C1 is a concept
```

(since C++20)

A parameter declaration with the specifier this (syntax (2)/(5)) declares an explicit object parameter.

An explicit object parameter cannot be a function parameter pack, and it can only appear as the first parameter of the parameter list in the following declarations:

- a declaration of a member function or member function template

- an explicit instantiation or explicit specialization of a templated member function

- a lambda declaration

A member function with an explicit object parameter has the following restrictions:

- The function is not static.

- The function is not virtual.

- The declarator of the function does not contain cv and ref.

```
struct C
{
    void f(this C& self);     // OK
    
    template<typename Self>
    void g(this Self&& self); // also OK for templates
    
    void p(this C) const;     // Error: “const” not allowed here
    static void q(this C);    // Error: “static” not allowed here
    void r(int, this C);      // Error: an explicit object parameter
                              //        can only be the first parameter
};

// void func(this C& self);   // Error: non-member functions cannot have
                              //        an explicit object parameter
```

(since C++23)

Parameter names declared in function declarations are usually for only self-documenting purposes. They are used (but remain optional) in function definitions.

An ambiguity arises in a parameter list when a type name is nested in parentheses (including lambda expressions)(since C++11). In this case, the choice is between the declaration of a parameter of type pointer to function and the declaration of a parameter with redundant parentheses around the identifier of the declarator. The resolution is to consider the type name as a simple type specifier (which is the pointer to function type):

```
class C {};

void f(int(C)) {} // void f(int(*fp)(C param)) {}
                  // NOT void f(int C) {}

void g(int *(C[10])); // void g(int *(*fp)(C param[10]));
                      // NOT void g(int *C[10]);
```

A type cannot be defined in the declaration of a function's parameter or in return type:

```
void f(struct S1 {} s); // Error
struct S2 {} g();       // Error
```

Parameter type cannot be a type that includes a reference or a pointer to array of unknown bound, including a multi-level pointers/arrays of such types, or a pointer to functions whose parameters are such types.

#### Using an ellipsis

The last parameter in the parameter list can be an ellipsis (...); this declares a variadic function. The comma preceding the ellipsis can be omitted(deprecated in C++26):

```
int printf(const char* fmt, ...); // a variadic function
int printf(const char* fmt...);   // same as above, but deprecated since C++26

template<typename... Args>
void f(Args..., ...); // a variadic function template with a parameter pack

template<typename... Args>
void f(Args... ...);  // same as above, but deprecated since C++26

template<typename... Args>
void f(Args......);   // same as above, but deprecated since C++26
```

### Function type

A function's type is formed from the presence or absence of noexcept (present iff except is non-throwing), (since C++17)ref, (since C++11)cv, its parameter-type-list (see below), and its return type.

#### Parameter-type-list

A function’s parameter-type-list is determined as follows:

- The type of each parameter (including function parameter packs)(since C++11) is determined from its own parameter declaration.

- After determining the type of each parameter, any parameter of type “array of T” or of function type T is adjusted to be “pointer to T”.

- After producing the list of parameter types, any top-level cv-qualifiers modifying a parameter type are deleted when forming the function type.

- The resulting list of transformed parameter types and the presence or absence of the ellipsis or a function parameter pack(since C++11) is the function’s parameter-type-list.

```
void f(char*);         // #1
void f(char[]) {}      // defines #1
void f(const char*) {} // OK, another overload
void f(char* const) {} // Error: redefines #1

void g(char(*)[2]);   // #2
void g(char[3][2]) {} // defines #2
void g(char[3][3]) {} // OK, another overload

void h(int x(const int)); // #3
void h(int (*)(int)) {}   // defines #3
```

#### Trailing qualifiers

A function type with cv ﻿ or ref ﻿ ﻿(since C++11) (including a type named by typedef name) can appear only as:

- the function type for a non-static member function,

- the function type to which a pointer to member refers,

- the top-level function type of a function typedef declaration or alias declaration(since C++11),

- the type-id in the default argument of a template type parameter,

- the type-id of a template argument for a template type parameter,

- the operand of a reflection operator.

(since C++26)

```
typedef int FIC(int) const;
FIC f;     // Error: does not declare a member function

struct S
{
    FIC f; // OK
};

FIC S::*pm = &S::f; // OK

constexpr auto yeti = ^^void(int) const&; // OK (since C++26)
```

### Function signature

Every function has a signature.

The signature of a function consists of its name and parameter-type-list. Its signature also contains the enclosing namespace, with the following exceptions:

- If the function is a member function, its signature contains the class of which the function is a member instead of the enclosing namespace. Its signature also contains the following components, if exists:

- cv

- ref

(since C++11)

- trailing requires clause

- If the function is a non-template friend function with a trailing requires clause, its signature contains the enclosing class instead of the enclosing namespace. The signature also contains the trailing requires clause.

(since C++20)

except and attr(since C++11) doesn't involve function signature, although noexcept specification affects the function type(since C++17).

### Function definition

A non-member function definition may appear at namespace scope only (there are no nested functions). A member function definition may also appear in the body of a class definition. They have the following syntax:

attr ﻿(optional) decl-specifier-seq ﻿(optional) declaratorvirt-specs ﻿(optional) contract-specs ﻿(optional) function-body | (1)

attr ﻿(optional) decl-specifier-seq ﻿(optional) declaratorrequires-clause contract-specs ﻿(optional) function-body | (2) | (since C++20)

attr | - | (since C++11) a list of attributes. These attributes are combined with the attributes after the identifier in the declarator (see top of this page), if any.

decl-specifier-seq | - | the return type with specifiers, as in the declaration grammar

declarator | - | function declarator, same as in the function declaration grammar above (can be parenthesized)

virt-specs | - | (since C++11) override, final, or their combination in any order

requires-clause | - | a requires clause

contract-specs | - | (since C++26) a list of function contract specifiers

function-body | - | the function body (see below)

function-body is one of the following:

ctor-initializer ﻿(optional) compound-statement | (1)

function-try-block | (2)

= default ; | (3) | (since C++11)

= delete ; | (4) | (since C++11)

= delete ( string-literal ); | (5) | (since C++26)

ctor-initializer | - | member initializer list, only allowed in constructors

compound-statement | - | the brace-enclosed sequence of statements that constitutes the body of a function

function-try-block | - | a function try block

string-literal | - | an unevaluated string literal that could be used to explain the rationale for why the function is deleted

```
int max(int a, int b, int c)
{
    int m = (a > b) ? a : b;
    return (m > c) ? m : c;
}

// decl-specifier-seq is “int”
// declarator is “max(int a, int b, int c)”
// body is { ... }
```

The function body is a compound statement (sequence of zero or more statements surrounded by a pair of curly braces), which is executed when the function call is made. Moreover, the function body of a constructor also includes the following:

- For all non-static data members whose identifiers are absent in the constructor's member initializer list, the default member initializers or(since C++11) default-initializations used to initialize the corresponding member subobjects.

- For all base classes whose type names are absent in the constructor's member initializer list, the default-initializations used to initialize the corresponding base class subobjects.

If a function definition contains a virt-specs, it must define a member function.

(since C++11)

If a function definition contains a requires-clause, it must define a templated function.

(since C++20)

```
void f() override {} // Error: not a member function

void g() requires (sizeof(int) == 4) {} // Error: not a templated function
```

The parameter types, as well as the return type of a function definition cannot be (possibly cv-qualified) incomplete class types unless the function is defined as deleted(since C++11). The completeness check is only made in the function body, which allows member functions to return the class in which they are defined (or its enclosing class), even if it is incomplete at the point of definition (it is complete in the function body).

The parameters declared in the declarator of a function definition are in scope within the body. If a parameter is not used in the function body, it does not need to be named (it's sufficient to use an abstract declarator):

```
void print(int a, int) // second parameter is not used
{
    std::printf("a = %d\n", a);
}
```

Even though top-level cv-qualifiers on the parameters are discarded in function declarations, they modify the type of the parameter as visible in the body of a function:

```
void f(const int n) // declares function of type void(int)
{
    // but in the body, the type of “n” is const int
}
```

#### Defaulted functions

If the function definition is of syntax (3), the function is defined as explicitly defaulted.

A function that is explicitly defaulted must be a special member function or comparison operator function(since C++20), and it must have no default argument.

An explicitly defaulted special member function F1 is allowed to differ from the corresponding special member function F2 that would have been implicitly declared, as follows:

- F1 and F2 may have different ref and/or except.

- If F2 has a non-object parameter of type const C&, the corresponding non-object parameter of F1 maybe of type C&.

- If F2 has an implicit object parameter of type “reference to C”, F1 may be an explicit object member function whose explicit object parameter is of (possibly different) type “reference to C”, in which case the type of F1 would differ from the type of F2 in that the type of F1 has an additional parameter.

(since C++23)

If the type of F1 differs from the type of F2 in a way other than as allowed by the preceding rules, then:

- If F1 is an assignment operator, and the return type of F1 differs from the return type of F2 or F1’s non-object parameter type is not a reference, the program is ill-formed.

- Otherwise, if F1 is explicitly defaulted on its first declaration, it is defined as deleted.

- Otherwise, the program is ill-formed.

A function explicitly defaulted on its first declaration is implicitly inline, and is implicitly constexpr if it can be a constexpr function.

```
struct S
{
    S(int a = 0) = default;             // error: default argument
    void operator=(const S&) = default; // error: non-matching return type
    ~S() noexcept(false) = default;     // OK, different exception specification
private:
    int i;
    S(S&);          // OK, private copy constructor
};

S::S(S&) = default; // OK, defines copy constructor
```

Explicitly-defaulted functions and implicitly-declared functions are collectively called defaulted functions. Their actual definitions will be implicitly provided, see their corresponding pages for details.

#### Deleted functions

If the function definition is of syntax (4) or (5)(since C++26), the function is defined as explicitly deleted.

Any use of a deleted function other than as the operand of reflection operator(since C++26) is ill-formed (the program will not compile). This includes calls, both explicit (with a function call operator) and implicit (a call to deleted overloaded operator, special member function, allocation function, etc), constructing a pointer or pointer-to-member to a deleted function, and even the use of a deleted function in an expression that is not potentially-evaluated.

A non-pure virtual member function can be defined as deleted, even though it is implicitly odr-used. A deleted function can only be overridden by deleted functions, and a non-deleted function can only be overridden by non-deleted functions.

If string-literal is present, the implementation is encouraged to include the text of it as part of the resulting diagnostic message which shows the rationale for deletion or to suggest an alternative.

(since C++26)

If the function is overloaded, overload resolution takes place first, and the program is only ill-formed if the deleted function was selected:

```
struct T
{
    void* operator new(std::size_t) = delete;
    void* operator new[](std::size_t) = delete("new[] is deleted"); // since C++26
};

T* p = new T;    // Error: attempts to call deleted T::operator new
T* p = new T[5]; // Error: attempts to call deleted T::operator new[],
                 //        emits a diagnostic message “new[] is deleted”
```

The deleted definition of a function must be the first declaration in a translation unit: a previously-declared function cannot be redeclared as deleted:

```
struct T { T(); };
T::T() = delete; // Error: must be deleted on the first declaration
```

#### User-provided functions

A function is user-provided if it is user-declared and not explicitly defaulted or deleted on its first declaration. A user-provided explicitly-defaulted function (i.e., explicitly defaulted after its first declaration) is defined at the point where it is explicitly defaulted; if such a function is implicitly defined as deleted, the program is ill-formed. Declaring a function as defaulted after its first declaration can provide efficient execution and concise definition while enabling a stable binary interface to an evolving code base.

```
// All special member functions of “trivial” are
// defaulted on their first declarations respectively,
// they are not user-provided
struct trivial
{
    trivial() = default;
    trivial(const trivial&) = default;
    trivial(trivial&&) = default;
    trivial& operator=(const trivial&) = default;
    trivial& operator=(trivial&&) = default;
    ~trivial() = default;
};

struct nontrivial
{
    nontrivial(); // first declaration
};

// not defaulted on the first declaration,
// it is user-provided and is defined here
nontrivial::nontrivial() = default;
```

#### Ambiguity Resolution

In the case of an ambiguity between a function body and an initializer beginning with { or =(since C++26), the ambiguity is resolved by checking the type of the declarator identifier of noptr-declarator ﻿:

- If the type is a function type, the ambiguous token sequence is treated as a function body.

- Otherwise, the ambiguous token sequence is treated as an initializer.

```
using T = void(); // function type
using U = int;    // non-function type

T a{}; // defines a function doing nothing
U b{}; // value-initializes an int object

T c = delete("hello"); // defines a function as deleted
U d = delete("hello"); // copy-initializes an int object with
                       // the result of a delete expression (ill-formed)
```

#### __func__

Within the function body, the function-local predefined variable __func__ is defined as if by

```
static const char __func__[] = "function-name";
```

This variable has block scope and static storage duration:

```
struct S
{
    S(): s(__func__) {} // OK: initializer-list is part of function body
    const char* s;
};
void f(const char* s = __func__); // Error: parameter-list is part of declarator
```

```
#include <iostream>

void Foo() { std::cout << __func__ << ' '; }

struct Bar
{
    Bar() { std::cout << __func__ << ' '; }
    ~Bar() { std::cout << __func__ << ' '; }
    struct Pub { Pub() { std::cout << __func__ << ' '; } };
};

int main()
{
    Foo();
    Bar bar;
    Bar::Pub pub;
}
```

Possible output:

```
Foo Bar Pub ~Bar
```

(since C++11)

### Function contract specifiers

Function declarations and lambda expressions can contain a sequence of function contract specifiers ﻿, each specifier has the following syntax:

pre attr ﻿(optional) ( predicate ) | (1)

post attr ﻿(optional) ( predicate ) | (2)

post attr ﻿(optional) ( identifier result-attr ﻿(optional) : predicate ) | (3)

attr | - | a list of attributes appertaining to the introduced contract assertion

predicate | - | any expression (except unparenthesized comma expressions)

identifier | - | the identifier that refers to the result

result-attr | - | a list of attributes appertaining to the result binding

Precondition assertion and postcondition assertion are collectively called function contract assertion ﻿.

A function contract assertion is a contract assertion associated with a function. The predicate of a function contract assertion is its predicate contextually converted to bool.

The following functions cannot be declared with function contract specifiers:

- virtual functions

- deleted functions

- function defaulted on their first declarations

#### Precondition assertions

A precondition assertion is associated with entering a function:

```
int divide(int dividend, int divisor) pre(divisor != 0)
{
    return dividend / divisor;
}

double square_root(double num) pre(num >= 0)
{
    return std::sqrt(num);
}
```

#### Postcondition assertions

A postcondition assertion is associated with exiting a function normally.

If a postcondition assertion has an identifier ﻿, the function contract specifier introduces identifier as the name of a result binding of the associated function. A result binding denotes the object or reference returned by invocation of that function. The type of a result binding is the return type of its associated function.

```
int absolute_value(int num) post(r : r >= 0)
{
    return std::abs(num);
}

double sine(double num) post(r : r >= -1.0 && r <= 1.0)
{
    if (std::isnan(num) || std::isinf(num))
        // exiting via an exception never causes contract violation
        throw std::invalid_argument("Invalid argument");
    return std::sin(num);
}
```

If a postcondition assertion has an identifier ﻿, and the return type of the associated function is (possibly cv-qualified) void, the program is ill-formed:

```
void f() post(r : r > 0); // Error: no value can be bound to “r”
```

When the declared return type of a non-templated function contains a placeholder type, a postcondition assertion with an identifier ﻿ can only appear in a function definition:

```
auto g(auto&) post(r : r >= 0); // OK, “g” is a template

auto h() post(r : r >= 0);      // Error: cannot name the return value

auto k() post(r : r >= 0)       // OK, “k” is a definition
{
    return 0;
}
```

#### Contract consistency

A redeclaration D of a function or function template func must have either no contract-specs or the same contract-specs as any first declaration F reachable from D. If D and F are in different translation units, a diagnostic is required only if D is attached to a named module.

If a declaration F1 is a first declaration of func in one translation unit and a declaration F2 is a first declaration of func in another translation unit, F1 and F2 must specify the same contract-specs ﻿, no diagnostic required.

Two contract-specs ﻿s are the same if they consist of the same function contract specifiers in the same order.

A function contract specifier C1 on a function declaration D1 is the same as a function contract specifier C2 on a function declaration D2 if all following conditions are satisfied:

- The predicate ﻿s of C1 and C2 would satisfy the one-definition rule if placed in function definitions on the declarations D1 and D2 (if D1 and D2 are in different translation units, corresponding entities defined within each predicate behave as if there is a single entity with a single definition), respectively, except for the following renamings:

- The renaming of the parameters of the declared function.

- The renaming of template parameters of a template enclosing the declared function.

- The renaming of the result binding (if any).

- Both C1 and C2 have an identifier or neither have.

If this condition is not met solely due to the comparison of two lambda expressions that are contained within the predicate ﻿s, no diagnostic is required.

```
bool b1, b2;

void f() pre (b1) pre([]{ return b2; }());
void f(); // OK, function contract specifiers omitted
void f() pre (b1) pre([]{ return b2; }()); // Error: closures have different types
void f() pre (b1); // Error: function contract specifiers are different

int g() post(r : b1);
int g() post(b1); // Error: no result binding

namespace N
{
    void h() pre (b1);
    bool b1;
    void h() pre (b1); // Error: function contract specifiers differ
                       //        according to the one−definition rule
}
```

(since C++26)

### Notes

In case of ambiguity between a variable declaration using the direct-initialization syntax and a function declaration, the compiler always chooses function declaration; see direct-initialization.

Feature-test macro | Value | Std | Feature

__cpp_decltype_auto | 201304L | (C++14) | decltype(auto)

__cpp_return_type_deduction | 201304L | (C++14) | return type deduction for normal functions

__cpp_explicit_this_parameter | 202110L | (C++23) | explicit object parameters (deducing this)

__cpp_deleted_function | 202403L | (C++26) | deleted function with a reason

### Keywords

default, delete, pre, post

### Example

```
#include <iostream>
#include <string>

// simple function with a default argument, returning nothing
void f0(const std::string& arg = "world!")
{
    std::cout << "Hello, " << arg << '\n';
}

// the declaration is in namespace (file) scope
// (the definition is provided later)
int f1();

// function returning a pointer to f0, pre-C++11 style
void (*fp03())(const std::string&)
{
    return f0;
}

// function returning a pointer to f0, with C++11 trailing return type
auto fp11() -> void(*)(const std::string&)
{
    return f0;
}

int main()
{
    f0();
    fp03()("test!");
    fp11()("again!");
    int f2(std::string) noexcept; // declaration in function scope
    std::cout << "f2(\"bad\"): " << f2("bad") << '\n';
    std::cout << "f2(\"42\"): " << f2("42") << '\n';
}

// simple non-member function returning int
int f1()
{
    return 007;
}

// function with an exception specification and a function try block
int f2(std::string str) noexcept
try
{
    return std::stoi(str);
}
catch (const std::exception& e)
{
    std::cerr << "stoi() failed!\n";
    return 0;
}

// deleted function, an attempt to call it results in a compilation error
void bar() = delete
#   if __cpp_deleted_function
    ("reason")
#   endif
;
```

Possible output:

```
stoi() failed!
Hello, world!
Hello, test!
Hello, again!
f2("bad"): 0
f2("42"): 42
```

### Defect reports

The following behavior-changing defect reports were applied retroactively to previously published C++ standards.

DR | Applied to | Behavior as published | Correct behavior

CWG 135 | C++98 | member functions defined in classcould not have a parameter of or returnits own class because it is incomplete | allowed

CWG 332 | C++98 | a parameter could have cv-qualified void type | prohibited

CWG 393 | C++98 | types that include pointers/references toarray of unknown bound could not be parameters | such types are allowed

CWG 452 | C++98 | member initializer list was not a part of function body | it is

CWG 577 | C++98 | dependent type void could be used todeclare a function taking no parameters | only non-dependentvoid is allowed

CWG 1327 | C++11 | defaulted or deleted functions could notbe specified with override or final | allowed

CWG 1355 | C++11 | only special member functions could be user-provided | extended to all functions

CWG 1394 | C++11 | deleted functions could not have any parameter ofan incomplete type or return an incomplete type | incomplete type allowed

CWG 1824 | C++98 | the completeness check on parameter type andreturn type of a function definition could be madeoutside the context of the function definition | only check in thecontext of thefunction definition

CWG 1877 | C++14 | return type deduction treated return; as return void(); | simply deduce the returntype as void in this case

CWG 2015 | C++11 | the implicit odr-use of a deletedvirtual function was ill-formed | such odr-uses are exemptfrom the use prohibition

CWG 2044 | C++14 | return type deduction on functions returning voidwould fail if the declared return type is decltype(auto) | updated the deductionrule to handle this case

CWG 2081 | C++14 | function redeclarations could use return typededuction even if the initial declaration does not | not allowed

CWG 2144 | C++11 | {} could be a function body or an initializer at the same place | differentiated by the typeof the declarator identifier

CWG 2145 | C++98 | the declarator in function definition could not be parenthesized | allowed

CWG 2259 | C++11 | the ambiguity resolution rule regarding parenthesizedtype names did not cover lambda expressions | covered

CWG 2430 | C++98 | in the definition of a member function in a class definition,the type of that class could not be the return type orparameter type due to the resolution of CWG issue 1824 | only check in thefunction body

CWG 2760 | C++98 | the function body of a constructor did not include the initializationsnot specified in the constructor's regular function body | also includes theseinitializations

CWG 2831 | C++20 | a function definition with a requires-clausecould define a non-templated function | prohibited

CWG 2846 | C++23 | explicit object member functions could not have out-of-class definitions | allowed

CWG 2915 | C++23 | unnamed explicit object parameters could have type void | prohibited

### See also

C documentation for Declaring functions
