Source: https://en.cppreference.com/w/cpp/language/overload_resolution
Retrieved: 2026-10-16
License: CC-BY-SA (cppreference.com)

# Overload resolution - cppreference.com

# Overload resolution

In order to compile a function call, the compiler must first perform name lookup, which, for functions, may involve argument-dependent lookup, and for function templates may be followed by template argument deduction.

If the name refers to more than one entity, it is said to be overloaded, and the compiler must determine which overload to call. In simple terms, the overload whose parameters match the arguments most closely is the one that is called.

In detail, overload resolution proceeds through the following steps:

- Building the set of candidate functions.

- Trimming the set to only viable functions.

- Analyzing the set to determine the single best viable function (this may involve ranking of implicit conversion sequences).

```
void f(long);
void f(float);

f(0L); // calls f(long)
f(0);  // error: ambiguous overload
```

Besides function calls, overloaded function names may appear in several additional contexts, where different rules apply: see Address of an overloaded function.

If a function cannot be selected by overload resolution, it cannot be used (e.g. it is a templated entity with a failed constraint).

### Candidate functions

Before overload resolution begins, the functions selected by name lookup and template argument deduction are combined to form the set of candidate functions. The exact details depend on the context in which overload resolution will take place.

#### Call to a named function

If E in a function call expression E(args) designates a set of overloaded functions and/or function templates (but not callable objects), the following rules are followed:

- If the expression E has the form PA->B or A.B (where A has class type cv T), then

- if B is a splice expression, the function declarations designated by B are the candidate functions; otherwise,

(since C++26)

- B is looked up as a member function of T. The function declarations found by that lookup are the candidate functions.

The argument list for the purpose of overload resolution has the implied object argument of type cv T.

- If the expression E is a primary expression, then

- if E is a splice expression, the function declarations designated by E are the candidate functions; otherwise

(since C++26)

- the name is looked up following normal rules for function calls (which may involve ADL). The function declarations found by this lookup are (due to the way lookup works) either:

- all non-member functions (in which case the argument list for the purpose of overload resolution is exactly the argument list used in the function call expression)

- all member functions of some class T, in which case, if this is in scope and is a pointer to T or to a derived class of T, *this is used as the implied object argument. Otherwise (if this is not in scope or does not point to T), a fake object of type T is used as the implied object argument, and if overload resolution subsequently selects a non-static member function, the program is ill-formed.

#### Call to a class object

If E in a function call expression E(args) has class type cv T, then

- The function-call operators of T are obtained by ordinary lookup of the name operator() in the context of the expression (E).operator(), and every declaration found is added to the set of candidate functions.

- For each non-explicit user-defined conversion function in T or in a base of T (unless hidden), whose cv-qualifiers are the same or greater than T's cv-qualifiers, and where the conversion function converts to:

- pointer-to-function

- reference-to-pointer-to-function

- reference-to-function

then a surrogate call function with a unique name whose first parameter is the result of the conversion, the remaining parameters are the parameter list accepted by the result of the conversion, and the return type is the return type of the result of the conversion, is added to the set of candidate functions. If this surrogate function is selected by the subsequent overload resolution, then the user-defined conversion function will be called and then the result of the conversion will be called.

In any case, the argument list for the purpose of overload resolution is the argument list of the function call expression preceded by the implied object argument E (when matching against the surrogate function, the user-defined conversion will automatically convert the implied object argument to the first argument of the surrogate function).

```
int f1(int);
int f2(float);

struct A
{
    using fp1 = int(*)(int);
    operator fp1() { return f1; } // conversion function to pointer to function
    using fp2 = int(*)(float);
    operator fp2() { return f2; } // conversion function to pointer to function
} a;

int i = a(1); // calls f1 via pointer returned from conversion function
```

#### Call to an overloaded operator

If at least one of the arguments to an operator in an expression has a class type or an enumeration type, both builtin operators and user-defined operator overloads participate in overload resolution, with the set of candidate functions selected as follows:

For a unary operator @ whose argument has type T1 (after removing cv-qualifications), or binary operator @ whose left operand has type T1 and right operand of type T2 (after removing cv-qualifications), the following sets of candidate functions are prepared:

- For the four relational operator expressions x < y, x <= y, x > y, and x >= y, all member, non-member, and built-in operator<=>s found are added to the set.

- For the four relational operator expressions x < y, x <= y, x > y, and x >= y as well as the three-way comparison expression x <=> y, a synthesized candidate with the order of the two parameters reversed is added for each member, non-member, and built-in operator<=>s found.

- For x != y, all member, non-member, and built-in operator==s found are added to the set, unless there is a matching operator!=.

- For equality operator expressions x == y and x != y, a synthesized candidate with the order of the two parameters reversed is added for each member, non-member, and built-in operator==s found, unless there is a matching operator!=.

@4@ rewritten candidates: | (since C++20)

The set of candidate functions to be submitted for overload resolution is a union of the sets above. The argument list for the purpose of overload resolution consists of the operands of the operator except for operator->, where the second operand is not an argument for the function call (see member access operator).

```
struct A
{
    operator int();              // user-defined conversion
};
A operator+(const A&, const A&); // non-member user-defined operator

void m()
{
    A a, b;
    a + b; // member-candidates: none
           // non-member candidates: operator+(a, b)
           // built-in candidates: int(a) + int(b)
           // overload resolution chooses operator+(a, b)
}
```

If the overload resolution selects a built-in candidate, the user-defined conversion sequence from an operand of class type is not allowed to have a second standard conversion sequence: the user-defined conversion function must give the expected operand type directly:

```
struct Y { operator int*(); }; // Y is convertible to int*
int *a = Y() + 100.0;          // error: no operator+ between pointer and double
```

For operator,, the unary operator&, and operator->, if there are no viable functions (see below) in the set of candidate functions, then the operator is reinterpreted as a built-in.

If a rewritten operator<=> candidate is selected by overload resolution for an operator @, x @ y is interpreted as the rewritten expression: 0 @ (y <=> x) if the selected candidate is a synthesized candidate with reversed order of parameters, or (x <=> y) @ 0 otherwise, using the selected rewritten operator<=> candidate.

If a rewritten operator== candidate is selected by overload resolution for an operator @ (which is either == or !=), its return type must be (possibly cv-qualified) bool, and x @ y is interpreted as the rewritten expression: y == x or !(y == x) if the selected candidate is a synthesized candidate with reversed order of parameters, or !(x == y) otherwise, using the selected rewritten operator== candidate.

Overload resolution in this case has a final tiebreaker preferring non-rewritten candidates to rewritten candidates, and preferring non-synthesized rewritten candidates to synthesized rewritten candidates.

This lookup with the reversed arguments order makes it possible to write just operator<=>(std::string, const char*) and operator==(std::string, const char*) to generate all comparisons between std::string and const char*, both ways. See default comparisons for more detail.

(since C++20)

#### Initialization by constructor

When an object of class type is direct-initialized or default-initialized (including default-initialization in the context of copy-list-initialization)(since C++11), the candidate functions are all constructors of the class being initialized. The argument list is the expression list of the initializer.

Otherwise, the candidate functions are all converting constructors of the class being initialized. The argument list is the expression of the initializer.

For default-initialization in the context of copy-list-initialization, if an explicit constructor is chosen, the initialization is ill-formed.

(since C++11)

#### Copy-initialization by conversion

If copy-initialization of an object of class type requires that a user-defined conversion is called to convert the initializer expression of type cv S to the type cv T of the object being initialized, the following functions are candidate functions:

- all converting constructors of T

- the non-explicit conversion functions from S and its base classes (unless hidden) to T or class derived from T or a reference to such. If this copy-initialization is part of the direct-initialization sequence of cv T (initializing a reference to be bound to the first parameter of a constructor that takes a reference to cv T), then explicit conversion functions are also considered.

Either way, the argument list for the purpose of overload resolution consists of a single argument which is the initializer expression, which will be compared against the first argument of the constructor or against the implicit object argument of the conversion function.

#### Non-class initialization by conversion

When initialization of an object of non-class type cv1 T requires a user-defined conversion function to convert from an initializer expression of class type cv S, the following functions are candidates:

- the non-explicit user-defined conversion functions of S and its base classes (unless hidden) that produce type T or a type convertible to T by a standard conversion sequence, or a reference to such type. cv-qualifiers on the returned type are ignored for the purpose of selecting candidate functions.

- if this is direct-initialization, the explicit user-defined conversion functions of S and its base classes (unless hidden) that produce type T or a type convertible to T by a qualification conversion, or a reference to such type, are also considered.

Either way, the argument list for the purpose of overload resolution consists of a single argument which is the initializer expression, which will be compared against the implicit object argument of the conversion function.

#### Reference initialization by conversion

During reference initialization, where the reference to cv1 T is bound to the lvalue or rvalue result of a conversion from the initializer expression from the class type cv2 S, the following functions are selected for the candidate set:

- The non-explicit user-defined conversion functions of S and its base classes (unless hidden) to the type

- (when converting to an lvalue) lvalue reference to cv2 T2

- (when converting to an rvalue or an lvalue of function type) cv2 T2 or rvalue reference to cv2 T2

where cv2 T2 is reference-compatible with cv1 T.

- For direct initialization, the explicit user-defined conversion functions are also considered if T2 is the same type as T or can be converted to type T with a qualification conversion.

Either way, the argument list for the purpose of overload resolution consists of a single argument which is the initializer expression, which will be compared against the implicit object argument of the conversion function.

#### List-initialization

When an object of non-aggregate class type T is list-initialized, two-phase overload resolution takes place.

- at phase 1, the candidate functions are all initializer-list constructors of T and the argument list for the purpose of overload resolution consists of a single initializer list argument

- if overload resolution fails at phase 1, phase 2 is entered, where the candidate functions are all constructors of T and the argument list for the purpose of overload resolution consists of the individual elements of the initializer list.

If the initializer list is empty and T has a default constructor, phase 1 is skipped.

In copy-list-initialization, if phase 2 selects an explicit constructor, the initialization is ill-formed (as opposed to all over copy-initializations where explicit constructors are not even considered).

#### Additional rules for function template candidates

If name lookup found a function template, template argument deduction and checking of any explicit template arguments are performed to find the template argument values (if any) that can be used in this case:

- If both succeeds, the template arguments are used to synthesize declarations of the corresponding function template specializations, which are added to the candidate set, and such specializations are treated just like non-template functions except where specified otherwise in the tie-breaker rules below.

- If argument deduction fails or the synthesized function template specialization would be ill-formed, no such function is added to the candidate set (see SFINAE).

If a name refers to one or more function templates and also to a set of overloaded non-template functions, those functions and the specializations generated from the templates are all candidates.

See function template overloading for further detail.

If a constructor template or conversion function template has a conditional explicit specifier which happens to be value-dependent, after deduction, if the context requires a candidate that is not explicit and the generated specialization is explicit, it is removed from the candidate set.

(since C++20)

#### Additional rules for constructor candidates

Defaulted move constructors and move assignment operators that are defined as deleted are excluded in the set of candidate functions.

A constructor inherited from class type C that has a first parameter of type “reference to P” (including such a constructor instantiated from a template) is excluded from the set of candidate functions when constructing an object of type D if all following conditions are satisfied:

- The argument list has exactly one argument.

- C is reference-related to P.

- P is reference-related to D.

(since C++11)

#### Additional rules for member function candidates

If any candidate function is a member function (static or non-static) that does not have an explicit object parameter(since C++23), but not a constructor, it is treated as if it has an extra parameter (implicit object parameter) which represents the object for which they are called and appears before the first of the actual parameters.

Similarly, the object on which a member function is being called is prepended to the argument list as the implied object argument.

For member functions of class X, the type of the implicit object parameter is affected by cv-qualifications and ref-qualifications of the member function as described in member functions.

The user-defined conversion functions are considered to be members of the implied object argument for the purpose of determining the type of the implicit object parameter.

The member functions introduced by a using-declaration into a derived class are considered to be members of the derived class for the purpose of defining the type of the implicit object parameter.

For the static member functions, the implicit object parameter is considered to match any object: its type is not examined and no conversion sequence is attempted for it. | (until C++23)

For the rest of overload resolution, the implied object argument is indistinguishable from other arguments, but the following special rules apply to the implicit object parameter:

```
struct B { void f(int); };
struct A { operator B&(); };

A a;
a.B::f(1); // Error: user-defined conversions cannot be applied
           // to the implicit object parameter
static_cast<B&>(a).f(1); // OK
```

### Viable functions

Given the set of candidate functions, constructed as described above, the next step of overload resolution is examining arguments and parameters to reduce the set to the set of viable functions

To be included in the set of viable functions, the candidate function must satisfy the following:

4) If the function has an associated constraint, it must be satisfied | (since C++20)

User-defined conversions (both converting constructors and user-defined conversion functions) are prohibited from taking part in implicit conversion sequence where it would make it possible to apply more than one user-defined conversion. Specifically, they are not considered if the target of the conversion is the first parameter of a constructor or the implicit object parameter of a user-defined conversion function, and that constructor/user-defined conversion is a candidate for

- copy-initialization of a class by user-defined conversion,

- initialization of a non-class type by a conversion function,

- initialization by conversion function for direct reference binding,

- initialization by constructor during the second (direct-initialization) step of class copy-initialization,

- initialization by list-initialization where the initializer list has exactly one element that is itself an initializer list, and the target is the first parameter of a constructor of class X, and the conversion is to X or reference to (possibly cv-qualified) X:

```
struct A { A(int); };
struct B { B(A); };

B b{{0}}; // list-initialization of B

// candidates: B(const B&), B(B&&), B(A)
// {0} -> B&& not viable: would have to call B(A)
// {0} -> const B&: not viable: would have to bind to rvalue, would have to call B(A)
// {0} -> A viable. Calls A(int): user-defined conversion to A is not banned
```

(since C++11)

### Best viable function

For each pair of viable function F1 and F2, the implicit conversion sequences from the i-th argument to i-th parameter are ranked to determine which one is better (except the first argument, the implicit object argument for static member functions has no effect on the ranking)

F1 is determined to be a better function than F2 if implicit conversions for all arguments of F1 are not worse than the implicit conversions for all arguments of F2, and

3) (only in context of initialization by conversion function for direct reference binding of a reference to function type), the result of F1 is the same kind of reference (lvalue or rvalue) as the reference being initialized, and the result of F2 is not, or, if not that, | (since C++11)

```
template<typename T = int>
struct S
{
    constexpr void f(); // #1
    constexpr void f(this S&) requires true; // #2
};

void test()
{
    S<> s;
    s.f(); // calls #2
}
```

6) F1 and F2 are non-template functions and F1 is more partial-ordering-constrained than F2: | (since C++20)

```
struct A
{
    A(int = 0);
};

struct B: A
{
    using A::A;
    
    B();
};

B b; // OK, B::B()
```

7) F1 is a constructor for a class D, F2 is a constructor for a base class B of D, and for all arguments the corresponding parameters of F1 and F2 have the same type: | (since C++11)

8) F2 is a rewritten candidate and F1 is not, or, if not that, 9) F1 and F2 are both rewritten candidates, and F2 is a synthesized rewritten candidate with reversed order of parameters and F1 is not, or, if not that, | (since C++20)

```
template<class T>
struct A
{
    using value_type = T;
    A(value_type);  // #1
    A(const A&);    // #2
    A(T, T, int);   // #3
    
    template<class U>
    A(int, T, U);   // #4
};                  // #5 is A(A), the copy deduction candidate

A x(1, 2, 3); // uses #3, generated from a non-template constructor

template<class T>
A(T) -> A<T>;       // #6, less specialized than #5

A a (42); // uses #6 to deduce A<int> and #1 to initialize
A b = a;  // uses #5 to deduce A<int> and #2 to initialize

template<class T>
A(A<T>) -> A<A<T>>; // #7, as specialized as #5
A b2 = a; // uses #7 to deduce A<A<int>> and #1 to initialize
```

10) F1 is generated from a user-defined deduction guide and F2 is not, or, if not that, 11) F1 is the copy deduction candidate and F2 is not, or, if not that, 12) F1 is generated from a non-template constructor and F2 is generated from a constructor template: | (since C++17)

These pair-wise comparisons are applied to all viable functions. If exactly one viable function is better than all others, overload resolution succeeds and this function is called. Otherwise, compilation fails.

```
void Fcn(const int*, short); // overload #1
void Fcn(int*, int);         // overload #2

int i;
short s = 0;

void f() 
{
    Fcn(&i, 1L);  // 1st argument: &i -> int* is better than &i -> const int*
                  // 2nd argument: 1L -> short and 1L -> int are equivalent
                  // calls Fcn(int*, int)
    
    Fcn(&i, 'c'); // 1st argument: &i -> int* is better than &i -> const int*
                  // 2nd argument: 'c' -> int is better than 'c' -> short
                  // calls Fcn(int*, int)
    
    Fcn(&i, s);   // 1st argument: &i -> int* is better than &i -> const int*
                  // 2nd argument: s -> short is better than s -> int
                  // no winner, compilation error
}
```

If the best viable function resolves to a function for which multiple declarations were found, and if any two of these declarations inhabit different scopes and specify a default argument that made the function viable, the program is ill-formed.

```
namespace A
{
    extern "C" void f(int = 5);
}

namespace B
{
    extern "C" void f(int = 5);
}

using A::f;
using B::f;

void use()
{
    f(3); // OK, default argument was not used for viability
    f();  // error: found default argument twice
}
```

### Ranking of implicit conversion sequences

The argument-parameter implicit conversion sequences considered by overload resolution correspond to implicit conversions used in copy initialization (for non-reference parameters), except that when considering conversion to the implicit object parameter or to the left-hand side of assignment operator, conversions that create temporary objects are not considered. When the parameter is the implicit object parameter of a static member function, the implicit conversion sequence is a standard conversion sequence that is neither better nor worse than any other standard conversion sequence.(since C++23)

Each type of standard conversion sequence is assigned one of three ranks:

The rank of the standard conversion sequence is the worst of the ranks of the standard conversions it holds (there may be up to three conversions)

Binding of a reference parameter directly to the argument expression is either identity or a derived-to-base conversion:

```
struct Base {};
struct Derived : Base {} d;

int f(Base&);    // overload #1
int f(Derived&); // overload #2

int i = f(d); // d -> Derived& has rank Exact Match
              // d -> Base& has rank Conversion
              // calls f(Derived&)
```

Since ranking of conversion sequences operates with types and value categories only, a bit field can bind to a reference argument for the purpose of ranking, but if that function gets selected, it will be ill-formed.

```
int i;
int f1();

int g(const int&);  // overload #1
int g(const int&&); // overload #2

int j = g(i);    // lvalue int -> const int& is the only valid conversion
int k = g(f1()); // rvalue int -> const int&& better than rvalue int -> const int&
```

```
int f(void(&)());  // overload #1
int f(void(&&)()); // overload #2

void g();
int i1 = f(g); // calls #1
```

the cv-qualification of the result of S1 is a proper subset of the cv-qualification of the result of S2, and S1 is not the deprecated string literal array-to-pointer conversion(until C++11).

(until C++20)

the result of S1 can be converted to the result of S2 by a qualification conversion.

(since C++20)

```
int f(const int*);
int f(int*);

int i;
int j = f(&i); // &i -> int* is better than &i -> const int*, calls f(int*)
```

```
int f(const int &); // overload #1
int f(int &);       // overload #2 (both references)

int g(const int &); // overload #1
int g(int);         // overload #2

int i;
int j = f(i); // lvalue i -> int& is better than lvalue int -> const int&
              // calls f(int&)
int k = g(i); // lvalue i -> const int& ranks Exact Match
              // lvalue i -> rvalue int ranks Exact Match
              // ambiguous overload: compilation error
```

```
struct Z {};

struct A
{
    operator Z&();
    operator const Z&();  // overload #1
};

struct B
{
    operator Z();
    operator const Z&&(); // overload #2
};

const Z& r1 = A();        // OK, uses #1
const Z&& r2 = B();       // OK, uses #2
```

```
struct A
{
    operator short(); // user-defined conversion function
} a;

int f(int);   // overload #1
int f(float); // overload #2

int i = f(a); // A -> short, followed by short -> int (rank Promotion)
              // A -> short, followed by short -> float (rank Conversion)
              // calls f(int)
```

```
void f1(int);                                 // #1
void f1(std::initializer_list<long>);         // #2
void g1() { f1({42}); }                       // chooses #2

void f2(std::pair<const char*, const char*>); // #3
void f2(std::initializer_list<std::string>);  // #4
void g2() { f2({"foo", "bar"}); }             // chooses #4
```

6) A list-initialization sequence L1 is better than list-initialization sequence L2 if the corresponding parameters are references to arrays, and L1 converts to type "array of N1 T," L2 converts to type "array of N2 T", and N1 is smaller than N2. | (since C++11)(until C++20)

- the number of elements N1 initialized by L1 is less than the number of elements N2 initialized by L2, or

- N1 is equal to N2 and L2 converts to an array of unknown bound and L1 does not.

```
void f(int    (&&)[] ); // overload #1
void f(double (&&)[] ); // overload #2
void f(int    (&&)[2]); // overload #3

f({1});        // #1: Better than #2 due to conversion, better than #3 due to bounds
f({1.0});      // #2: double -> double is better than double -> int
f({1.0, 2.0}); // #2: double -> double is better than double -> int
f({1, 2});     // #3: -> int[2] is better than -> int[], 
               //     and int -> int is better than int -> double
```

6) A list-initialization sequence L1 is better than list-initialization sequence L2 if the corresponding parameters are references to arrays, and L1 and L2 convert to arrays of same element type, and either | (since C++20)

If two conversion sequences are indistinguishable because they have the same rank, the following additional rules apply:

```
enum num : char { one = '0' };
std::cout << num::one; // '0', not 48
```

2) Conversion that promotes an enumeration whose underlying type is fixed to its underlying type is better than one that promotes to the promoted underlying type, if the two types are different. | (since C++11)

- the floating-point conversion rank of FP1 is equal to the rank of FP2, and

- T3 is not a floating-point type, or

- T3 is a floating-point type whose rank is not equal to the rank of FP1, or

- the floating-point conversion subrank of FP2 is greater than the subrank of T3.

```
int f(std::float32_t);
int f(std::float64_t);
int f(long long);

float x;
std::float16_t y;

int i = f(x); // calls f(std::float32_t) on implementations where
              // float and std::float32_t have equal conversion ranks
int j = f(y); // error: ambiguous, no equal conversion rank
```

3) A conversion in either direction between floating-point type FP1 and floating-point type FP2 is better than a conversion in the same direction between FP1 and arithmetic type T3 if | (since C++23)

Ambiguous conversion sequences are ranked as user-defined conversion sequences because multiple conversion sequences for an argument can exist only if they involve different user-defined conversions:

```
class B;

class A { A (B&);};         // converting constructor
class B { operator A (); }; // user-defined conversion function
class C { C (B&); };        // converting constructor

void f(A) {} // overload #1
void f(C) {} // overload #2

B b;
f(b); // B -> A via ctor or B -> A via function (ambiguous conversion)
      // b -> C via ctor (user-defined conversion)
      // the conversions for overload #1 and for overload #2
      // are indistinguishable; compilation fails
```

### Implicit conversion sequence in list-initialization

In list initialization, the argument is a braced-init-list, which isn't an expression, so the implicit conversion sequence into the parameter type for the purpose of overload resolution is decided by the following special rules:

- If the parameter type is some aggregate X and the initializer list consists of exactly one element of same or derived class (possibly cv-qualified), the implicit conversion sequence is the one required to convert the element to the parameter type.

- Otherwise, if the parameter type is a reference to character array and the initializer list has a single element that is an appropriately-typed string literal, the implicit conversion sequence is the identity conversion.

- Otherwise, if the parameter type is std::initializer_list<X>, and there is a non-narrowing implicit conversion from every element of the initializer list to X, the implicit conversion sequence for the purpose of overload resolution is the worst conversion necessary. If the braced-init-list is empty, the conversion sequence is the identity conversion.

```
struct A
{
    A(std::initializer_list<double>);          // #1
    A(std::initializer_list<complex<double>>); // #2
    A(std::initializer_list<std::string>);     // #3
};
A a{1.0, 2.0};     // selects #1 (rvalue double -> double: identity conv)

void g(A);
g({"foo", "bar"}); // selects #3 (lvalue const char[4] -> std::string: user-def conv)
```

- Otherwise, if the parameter type is "array of N T" (this only happens for references to arrays), the initializer list must have N or less elements, and the worst implicit conversion necessary to convert every element of the list (or the empty pair of braces {} if the list is shorter than N) to T is the one used.

- Otherwise, if the parameter type is "array of unknown bound of T" (this only happens for references to arrays), the worst implicit conversion necessary to convert every element of the list to T is the one used.

(since C++20)

```
typedef int IA[3];

void h(const IA&);
void g(int (&&)[]);

h({1, 2, 3}); // int->int identity conversion
g({1, 2, 3}); // same as above since C++20
```

- Otherwise, if the parameter type is a non-aggregate class type X, overload resolution picks the constructor C of X to initialize from the argument initializer list

- If C is not an initializer-list constructor and the initializer list has a single element of possibly cv-qualified X, the implicit conversion sequence has Exact Match rank. If the initializer list has a single element of possibly cv-qualified type derived from X, the implicit conversion sequence has Conversion rank. (note the difference from aggregates: aggregates initialize directly from single-element init lists before considering aggregate initialization, non-aggregates consider initializer_list constructors before any other constructors)

- otherwise, the implicit conversion sequence is a user-defined conversion sequence with the second standard conversion sequence an identity conversion.

If multiple constructors are viable but none is better than the others, the implicit conversion sequence is the ambiguous conversion sequence.

```
struct A { A(std::initializer_list<int>); };
void f(A);

struct B { B(int, double); };
void g(B);

g({'a', 'b'});    // calls g(B(int, double)), user-defined conversion
// g({1.0, 1,0}); // error: double->int is narrowing, not allowed in list-init

void f(B);
// f({'a', 'b'}); // f(A) and f(B) both user-defined conversions
```

- Otherwise, if the parameter type is an aggregate which can be initialized from the initializer list according by aggregate initialization, the implicit conversion sequence is a user-defined conversion sequence with the second standard conversion sequence an identity conversion.

```
struct A { int m1; double m2; };

void f(A);
f({'a', 'b'}); // calls f(A(int, double)), user-defined conversion
```

- Otherwise, if the parameter is a reference, reference initialization rules apply

```
struct A { int m1; double m2; };

void f(const A&);
f({'a', 'b'}); // temporary created, f(A(int, double)) called. User-defined conversion
```

- Otherwise, if the parameter type is not a class and the initializer list has one element, the implicit conversion sequence is the one required to convert the element to the parameter type

- Otherwise, if the parameter type is not a class type and if the initializer list has no elements, the implicit conversion sequence is the identity conversion.

If the argument is a designated initializer list and the parameter is not a reference, a conversion is only possible if the parameter has an aggregate type that can be initialized from that initializer list according to the rules for aggregate initialization, in which case the implicit conversion sequence is a user-defined conversion sequence whose second standard conversion sequence is an identity conversion.

If, after overload resolution, the order of declaration of the aggregate's members does not match for the selected overload, the initialization of the parameter will be ill-formed.

```
struct A { int x, y; };
struct B { int y, x; };

void f(A a, int); // #1
void f(B b, ...); // #2
void g(A a);      // #3
void g(B b);      // #4

void h() 
{
    f({.x = 1, .y = 2}, 0); // OK; calls #1
    f({.y = 2, .x = 1}, 0); // error: selects #1, initialization of a fails
                            // due to non-matching member order
    g({.x = 1, .y = 2});    // error: ambiguous between #3 and #4
}
```

(since C++20)

### Defect reports

The following behavior-changing defect reports were applied retroactively to previously published C++ standards.

DR | Applied to | Behavior as published | Correct behavior

CWG 1 | C++98 | the behavior was unspecified when the samefunction with possibly different defaultarguments (from different scopes) is selected | the program is ill-formed in this case

CWG 83 | C++98 | the conversion sequence from a string literalto char* was better than that to const char*even though the former is deprecated | the rank of the deprecatedconversion is lowered (itwas removed in C++11)

CWG 162 | C++98 | it was invalid if the overload set named by F containsa non-static member function in the case of &F(args) | only invalid if overloadresolution selects a non-staticmember function in this case

CWG 233 | C++98 | references and pointers were handled insonsistently inoverloading resolution with user defined conversions | they are handledconsistently

CWG 280 | C++98 | surrogate call functions were not added tothe set of candidate functions for conversionfunctions declared in inaccessible base classes | removed the accessibilityconstraint, the program isill-formed if a surrogate callfunction is selected and thecorresponding conversionfunction cannot be called

CWG 415 | C++98 | when a function template is selected as acandidate, its specializations were instantiatedusing template argument deduction | no instantiation will occurin this case, their declarationswill be synthesized

CWG 495 | C++98 | when the implicit conversions for arguments are equallygood, a non-template conversion function was alwaysbetter than a conversion function template, even if thelatter may have a better standard conversion sequence | standard conversionsequences are comparedbefore specialization levels

CWG 1307 | C++11 | overload resolution based on size of arrays was not specified | a shorter array isbetter when possible

CWG 1328 | C++11 | the determination of the candidate functions whenbinding a reference to a conversion result was not clear | made clear

CWG 1374 | C++98 | qualification conversion was checked before referencebinding when comparing standard conversion sequences | reversed

CWG 1385 | C++11 | a non-explicit user-defined conversion function declared witha ref-qualifier did not have a corresponding surrogate function | it has a correspondingsurrogate function

CWG 1467 | C++11 | same-type list-initialization ofaggregates and arrays was omitted | initialization defined

CWG 1601 | C++11 | conversion from enum to its underlying typedid not prefer the fixed underlying type | fixed type is preferredto what it promotes to

CWG 1608 | C++98 | the set of member candidates of a unary operator @whose argument has type T1 was empty ifT1 is a class currently being defined | the set is the result ofqualified name lookup ofT1::operator@ in this case

CWG 1687 | C++98 | when a built-in candidate is selected by overload resolution,the operands would undergo conversion without restriction | only convert class type operands,and disabled the secondstandard conversion sequence

CWG 2052 | C++98 | ill-formed synthesized function template specializations couldbe added to the candidate set, making the program ill-formed | they are not addedto the candidate set

CWG 2076 | C++11 | user-defined conversion is applied to the single initializerin a nested initializer list during list-initializationdue to the resolution of CWG issue 1467 | not applied

CWG 2137 | C++11 | initializer list constructors lost to copyconstructors when list-initializing X from {X} | non-aggregates considerinitializer lists first

CWG 2273 | C++11 | there was no tiebreaker betweeninherited and non-inherited constructors | non-inherited constructor wins

CWG 2673 | C++20 | built-in candidates with the same parameterlist as a rewritten non-member candidatewere added to the list of built-in candidates | not added

CWG 2712 | C++98 | when a built-in assignment operator is considered,the first parameter could not bound to atemporary, which is already impossible[1] | removed theredundant requirement

CWG 2713 | C++20 | the conversion restriction regarding designated initializerlists was applied even if the parameter is a reference | not restricted in this case

CWG 2789 | C++23 | the explicit object paramaeter was includedwhen comparing parameter-type-lists | excluded

CWG 2856 | C++11 | the overload resolution for default-initialization in the contextof copy-list-initialization only considered converting constructor | considers all constructors

CWG 2919 | C++98 | the candidate set of reference initialization by conversiondepended on the target type of the initialization | depends on the targettype of the conversion

P2468R2 | C++20 | rewritten candidates based on operator== are addedfor a != b even if a matching operator!= exists | not added

- ↑ The type of the of the first parameter of a built-in assignment operator is “lvalue reference to possibly volatile-qualified T”. References of this type cannot bould to a temporary.

### References

- C++23 standard (ISO/IEC 14882:2024):

- 12.2 Overload resolution [over.match]

- C++20 standard (ISO/IEC 14882:2020):

- 12.4 Overload resolution [over.match]

- C++17 standard (ISO/IEC 14882:2017):

- 16.3 Overload resolution [over.match]

- C++14 standard (ISO/IEC 14882:2014):

- 13.3 Overload resolution [over.match]

- C++11 standard (ISO/IEC 14882:2011):

- 13.3 Overload resolution [over.match]

- C++03 standard (ISO/IEC 14882:2003):

- 13.3 Overload resolution [over.match]

### See also

- Name lookup

- Argument-dependent lookup

- Template argument deduction

- SFINAE
