Source: https://en.cppreference.com/w/cpp/language/operators
Retrieved: 2026-10-16
License: CC-BY-SA (cppreference.com)

# operator overloading - cppreference.com

# operator overloading

Customizes the C++ operators for operands of user-defined types.

### Syntax

Operator functions are functions with special function names:

operator op | (1)

operator newoperator new [] | (2)

operator deleteoperator delete [] | (3)

operator co_await | (4) | (since C++20)

op | - | any of the following operators:+ - * / % ^ & | ~ ! = < > += -= *= /= %= ^= &= |= << >> >>= <<= == != <= >= <=>(since C++20) && || ++ -- , ->* -> () []

The behaviors of non-punctuation operators are described in their own respective pages. Unless otherwise specified, the remaining description in this page does not apply to these functions.

### Explanation

When an operator appears in an expression, and at least one of its operands has a class type or an enumeration type, then overload resolution is used to determine the user-defined function to be called among all the functions whose signatures match the following:

Expression | As member function | As non-member function | Example

@a | (a).operator@ ( ) | operator@ (a) | !std::cin calls std::cin.operator!()

a@b | (a).operator@ (b) | operator@ (a, b) | std::cout << 42 calls std::cout.operator<<(42)

a=b | (a).operator= (b) | cannot be non-member | Given std::string s;, s = "abc"; calls s.operator=("abc")

a(b...) | (a).operator()(b...) | cannot be non-member | Given std::random_device r;, auto n = r(); calls r.operator()()

a[b...] | (a).operator[](b...) | cannot be non-member | Given std::map<int, int> m;, m[1] = 2; calls m.operator[](1)

a-> | (a).operator->( ) | cannot be non-member | Given std::unique_ptr<S> p;, p->bar() calls p.operator->()

a@ | (a).operator@ (0) | operator@ (a, 0) | Given std::vector<int>::iterator i;, i++ calls i.operator++(0)

In this table, @ is a placeholder representing all matching operators: all prefix operators in @a, all postfix operators other than -> in a@, all infix operators other than = in a@b.

In addition, for comparison operators ==, !=, <, >, <=, >=, <=>, overload resolution also considers the rewritten candidates operator== or operator<=>.

(since C++20)

Overloaded operators (but not the built-in operators) can be called using function notation:

```
std::string str = "Hello, ";
str.operator+=("world");                      // same as str += "world";
operator<<(operator<<(std::cout, str), '\n'); // same as std::cout << str << '\n';
                                              // (since C++17) except for sequencing
```

#### Static overloaded operators

Overloaded operators that are member functions can be declared static. However, this is only allowed for operator() and operator[].

Such operators can be called using function notation. However, when these operators appear in expressions, they still require an object of class type.

```
struct SwapThem
{
    template<typename T>
    static void operator()(T& lhs, T& rhs) 
    {
        std::ranges::swap(lhs, rhs);
    }
    
    template<typename T>
    static void operator[](T& lhs, T& rhs)
    {
        std::ranges::swap(lhs, rhs);
    } 
};
inline constexpr SwapThem swap_them{};

void foo()
{
    int a = 1, b = 2;
    
    swap_them(a, b); // OK
    swap_them[a, b]; // OK
    
    SwapThem{}(a, b); // OK
    SwapThem{}[a, b]; // OK
    
    SwapThem::operator()(a, b); // OK
    SwapThem::operator[](a, b); // OK
    
    SwapThem(a, b); // error, invalid construction
    SwapThem[a, b]; // error
}
```

(since C++23)

### Restrictions

- An operator function must have at least one function parameter or implicit object parameter whose type is a class, a reference to a class, an enumeration, or a reference to an enumeration.

- The operators :: (scope resolution), . (member access), .* (member access through pointer to member), and ?: (ternary conditional) cannot be overloaded.

- New operators such as **, <>, or &| cannot be created.

- It is not possible to change the precedence, grouping, or number of operands of operators.

- The overload of operator -> must either return a raw pointer, or return an object (by reference or by value) for which operator -> is in turn overloaded.

- The overloads of operators && and || lose short-circuit evaluation.

- &&, ||, and , lose their special sequencing properties when overloaded and behave like regular function calls even when they are used without function-call notation.

(until C++17)

### Canonical implementations

Besides the restrictions above, the language puts no other constraints on what the overloaded operators do, or on the return type (it does not participate in overload resolution), but in general, overloaded operators are expected to behave as similar as possible to the built-in operators: operator+ is expected to add, rather than multiply its arguments, operator= is expected to assign, etc. The related operators are expected to behave similarly (operator+ and operator+= do the same addition-like operation). The return types are limited by the expressions in which the operator is expected to be used: for example, assignment operators return by reference to make it possible to write a = b = c = d, because the built-in operators allow that.

Commonly overloaded operators have the following typical, canonical forms:[1]

#### Assignment operator

The assignment operator operator= has special properties: see copy assignment and move assignment for details.

The canonical copy-assignment operator is expected to be safe on self-assignment, and to return the lhs by reference:

```
// copy assignment
T& operator=(const T& other)
{
    // Guard self assignment
    if (this == &other)
        return *this;
    
    // assume *this manages a reusable resource, such as a heap-allocated buffer mArray
    if (size != other.size)           // resource in *this cannot be reused
    {
        temp = new int[other.size];   // allocate resource, if throws, do nothing
        delete[] mArray;              // release resource in *this
        mArray = temp;
        size = other.size;
    }
    
    std::copy(other.mArray, other.mArray + other.size, mArray);
    return *this;
}
```

The canonical move assignment is expected to leave the moved-from object in valid state (that is, a state with class invariants intact), and either do nothing or at least leave the object in a valid state on self-assignment, and return the lhs by reference to non-const, and be noexcept:

```
// move assignment
T& operator=(T&& other) noexcept
{
    // Guard self assignment
    if (this == &other)
        return *this; // delete[]/size=0 would also be ok
    
    delete[] mArray;                               // release resource in *this
    mArray = std::exchange(other.mArray, nullptr); // leave other in valid state
    size = std::exchange(other.size, 0);
    return *this;
}
```

(since C++11)

In those situations where copy assignment cannot benefit from resource reuse (it does not manage a heap-allocated array and does not have a (possibly transitive) member that does, such as a member std::vector or std::string), there is a popular convenient shorthand: the copy-and-swap assignment operator, which takes its parameter by value (thus working as both copy- and move-assignment depending on the value category of the argument), swaps with the parameter, and lets the destructor clean it up.

```
// copy assignment (copy-and-swap idiom)
T& T::operator=(T other) noexcept // call copy or move constructor to construct other
{
    std::swap(size, other.size); // exchange resources between *this and other
    std::swap(mArray, other.mArray);
    return *this;
} // destructor of other is called to release the resources formerly managed by *this
```

This form automatically provides strong exception guarantee, but prohibits resource reuse.

#### Stream extraction and insertion

The overloads of operator>> and operator<< that take a std::istream& or std::ostream& as the left hand argument are known as insertion and extraction operators. Since they take the user-defined type as the right argument (b in a @ b), they must be implemented as non-members.

```
std::ostream& operator<<(std::ostream& os, const T& obj)
{
    // write obj to stream
    return os;
}

std::istream& operator>>(std::istream& is, T& obj)
{
    // read obj from stream
    if (/* T could not be constructed */)
        is.setstate(std::ios::failbit);
    return is;
}
```

These operators are sometimes implemented as friend functions.

#### Function call operator

When a user-defined class overloads the function call operator operator(), it becomes a FunctionObject type.

An object of such a type can be used in a function call expression:

```
// An object of this type represents a linear function of one variable a * x + b.
struct Linear
{
    double a, b;
    
    double operator()(double x) const
    {
        return a * x + b;
    }
};

int main()
{
    Linear f{2, 1};  // Represents function 2x + 1.
    Linear g{-1, 0}; // Represents function -x.
    // f and g are objects that can be used like a function.
    
    double f_0 = f(0);
    double f_1 = f(1);
    
    double g_0 = g(0);
}
```

Many standard library algorithms accept FunctionObjects to customize behavior. There are no particularly notable canonical forms of operator(), but to illustrate the usage:

```
#include <algorithm>
#include <iostream>
#include <vector>

struct Sum
{
    int sum = 0;
    void operator()(int n) { sum += n; }
};

int main()
{
    std::vector<int> v = {1, 2, 3, 4, 5};
    Sum s = std::for_each(v.begin(), v.end(), Sum());
    std::cout << "The sum is " << s.sum << '\n';
}
```

Output:

```
The sum is 15
```

#### Increment and decrement

When the postfix increment or decrement operator appears in an expression, the corresponding user-defined function (operator++ or operator--) is called with an integer argument 0. Typically, it is declared as T operator++(int) or T operator--(int), where the argument is ignored. The postfix increment and decrement operators are usually implemented in terms of the prefix versions:

```
struct X
{
    // prefix increment
    X& operator++()
    {
        // actual increment takes place here
        return *this; // return new value by reference
    }
    
    // postfix increment
    X operator++(int)
    {
        X old = *this; // copy old value
        operator++();  // prefix increment
        return old;    // return old value
    }
    
    // prefix decrement
    X& operator--()
    {
        // actual decrement takes place here
        return *this; // return new value by reference
    }
    
    // postfix decrement
    X operator--(int)
    {
        X old = *this; // copy old value
        operator--();  // prefix decrement
        return old;    // return old value
    }
};
```

Although the canonical implementations of the prefix increment and decrement operators return by reference, as with any operator overload, the return type is user-defined; for example the overloads of these operators for std::atomic return by value.

#### Binary arithmetic operators

Binary operators are typically implemented as non-members to maintain symmetry (for example, when adding a complex number and an integer, if operator+ is a member function of the complex type, then only complex + integer would compile, and not integer + complex). Since for every binary arithmetic operator there exists a corresponding compound assignment operator, canonical forms of binary operators are implemented in terms of their compound assignments:

```
class X
{
public:
    X& operator+=(const X& rhs) // compound assignment (does not need to be a member,
    {                           // but often is, to modify the private members)
        /* addition of rhs to *this takes place here */
        return *this; // return the result by reference
    }
    
    // friends defined inside class body are inline and are hidden from non-ADL lookup
    friend X operator+(X lhs,        // passing lhs by value helps optimize chained a+b+c
                       const X& rhs) // otherwise, both parameters may be const references
    {
        lhs += rhs; // reuse compound assignment
        return lhs; // return the result by value (uses move constructor)
    }
};
```

#### Comparison operators

Standard library algorithms such as std::sort and containers such as std::set expect operator< to be defined, by default, for the user-provided types, and expect it to implement strict weak ordering (thus satisfying the Compare requirements). An idiomatic way to implement strict weak ordering for a structure is to use lexicographical comparison provided by std::tie:

```
struct Record
{
    std::string name;
    unsigned int floor;
    double weight;
    
    friend bool operator<(const Record& l, const Record& r)
    {
        return std::tie(l.name, l.floor, l.weight)
             < std::tie(r.name, r.floor, r.weight); // keep the same order
    }
};
```

Typically, once operator< is provided, the other relational operators are implemented in terms of operator<.

```
inline bool operator< (const X& lhs, const X& rhs) { /* do actual comparison */ }
inline bool operator> (const X& lhs, const X& rhs) { return rhs < lhs; }
inline bool operator<=(const X& lhs, const X& rhs) { return !(lhs > rhs); }
inline bool operator>=(const X& lhs, const X& rhs) { return !(lhs < rhs); }
```

Likewise, the inequality operator is typically implemented in terms of operator==:

```
inline bool operator==(const X& lhs, const X& rhs) { /* do actual comparison */ }
inline bool operator!=(const X& lhs, const X& rhs) { return !(lhs == rhs); }
```

When three-way comparison (such as std::memcmp or std::string::compare) is provided, all six two-way comparison operators may be expressed through that:

```
inline bool operator==(const X& lhs, const X& rhs) { return cmp(lhs,rhs) == 0; }
inline bool operator!=(const X& lhs, const X& rhs) { return cmp(lhs,rhs) != 0; }
inline bool operator< (const X& lhs, const X& rhs) { return cmp(lhs,rhs) <  0; }
inline bool operator> (const X& lhs, const X& rhs) { return cmp(lhs,rhs) >  0; }
inline bool operator<=(const X& lhs, const X& rhs) { return cmp(lhs,rhs) <= 0; }
inline bool operator>=(const X& lhs, const X& rhs) { return cmp(lhs,rhs) >= 0; }
```

#### Array subscript operator

User-defined classes that provide array-like access that allows both reading and writing typically define two overloads for operator[]: const and non-const variants:

```
struct T
{
          value_t& operator[](std::size_t idx)       { return mVector[idx]; }
    const value_t& operator[](std::size_t idx) const { return mVector[idx]; }
};
```

Alternatively, they can be expressed as a single member function template using an explicit object member functions:

```
struct T
{
    decltype(auto) operator[](this auto& self, std::size_t idx) 
    { 
        return self.mVector[idx]; 
    }
};
```

(since C++23)

If the value type is known to be a scalar type, the const variant should return by value.

Where direct access to the elements of the container is not wanted or not possible or distinguishing between lvalue c[i] = v; and rvalue v = c[i]; usage, operator[] may return a proxy. See for example std::bitset::operator[].

operator[] can only take one subscript. In order to provide multidimensional array access semantics, e.g. to implement a 3D array access a[i][j][k] = x;, operator[] has to return a reference to a 2D plane, which has to have its own operator[] which returns a reference to a 1D row, which has to have operator[] which returns a reference to the element. To avoid this complexity, some libraries opt for overloading operator() instead, so that 3D access expressions have the Fortran-like syntax a(i, j, k) = x;.

(until C++23)

operator[] can take any number of subscripts. For example, an operator[] of a 3D array class declared as T& operator[](std::size_t x, std::size_t y, std::size_t z); can directly access the elements.

```
#include <array>
#include <cassert>
#include <iostream>

template<typename T, std::size_t Z, std::size_t Y, std::size_t X>
struct Array3d
{
    std::array<T, X * Y * Z> m{};

    constexpr T& operator[](std::size_t z, std::size_t y, std::size_t x) // C++23
    {
        assert(x < X and y < Y and z < Z);
        return m[z * Y * X + y * X + x];
    }
};

int main()
{
    Array3d<int, 4, 3, 2> v;
    v[3, 2, 1] = 42;
    std::cout << "v[3, 2, 1] = " << v[3, 2, 1] << '\n';
}
```

Output:

```
v[3, 2, 1] = 42
```

(since C++23)

#### Bitwise arithmetic operators

User-defined classes and enumerations that implement the requirements of BitmaskType are required to overload the bitwise arithmetic operators operator&, operator|, operator^, operator~, operator&=, operator|=, and operator^=, and may optionally overload the shift operators operator<< operator>>, operator>>=, and operator<<=. The canonical implementations usually follow the pattern for binary arithmetic operators described above.

#### Boolean negation operator

The operator operator! is commonly overloaded by the user-defined classes that are intended to be used in boolean contexts. Such classes also provide a user-defined conversion function to boolean type (see std::basic_ios for the standard library example), and the expected behavior of operator! is to return the value opposite of operator bool.

(until C++11)

Since the built-in operator ! performs contextual conversion to bool, user-defined classes that are intended to be used in boolean contexts could provide only operator bool and need not overload operator!.

(since C++11)

#### Rarely overloaded operators

The following operators are rarely overloaded:

- The address-of operator, operator&. If the unary & is applied to an lvalue of incomplete type and the complete type declares an overloaded operator&, it is unspecified whether the operator has the built-in meaning or the operator function is called. Because this operator may be overloaded, generic libraries use std::addressof to obtain addresses of objects of user-defined types. The best known example of a canonical overloaded operator& is the Microsoft class CComPtrBase. An example of this operator's use in EDSL can be found in boost.spirit.

- The boolean logic operators, operator&& and operator||. Unlike the built-in versions, the overloads cannot implement short-circuit evaluation. Also unlike the built-in versions, they do not sequence their left operand before the right one.(until C++17) In the standard library, these operators are only overloaded for std::valarray.

- The comma operator, operator,. Unlike the built-in version, the overloads do not sequence their left operand before the right one.(until C++17) Because this operator may be overloaded, generic libraries use expressions such as a, void(), b instead of a, b to sequence execution of expressions of user-defined types. The boost library uses operator, in boost.assign, boost.spirit, and other libraries. The database access library SOCI also overloads operator,.

- The member access through pointer to member operator->*. There are no specific downsides to overloading this operator, but it is rarely used in practice. It was suggested that it could be part of a smart pointer interface, and in fact is used in that capacity by actors in boost.phoenix. It is more common in EDSLs such as cpp.react.

### Notes

Feature-test macro | Value | Std | Feature

__cpp_static_call_operator | 202207L | (C++23) | static operator()

__cpp_multidimensional_subscript | 202211L | (C++23) | static operator[]

### Keywords

operator

### Example

```
#include <iostream>

class Fraction
{
    // or C++17's std::gcd
    constexpr int gcd(int a, int b) { return b == 0 ? a : gcd(b, a % b); }
    
    int n, d;
public:
    constexpr Fraction(int n, int d = 1) : n(n / gcd(n, d)), d(d / gcd(n, d)) {}
    
    constexpr int num() const { return n; }
    constexpr int den() const { return d; }
    
    constexpr Fraction& operator*=(const Fraction& rhs)
    {
        int new_n = n * rhs.n / gcd(n * rhs.n, d * rhs.d);
        d = d * rhs.d / gcd(n * rhs.n, d * rhs.d);
        n = new_n;
        return *this;
    }
};

std::ostream& operator<<(std::ostream& out, const Fraction& f)
{
   return out << f.num() << '/' << f.den();
}

constexpr bool operator==(const Fraction& lhs, const Fraction& rhs)
{
    return lhs.num() == rhs.num() && lhs.den() == rhs.den();
}

constexpr bool operator!=(const Fraction& lhs, const Fraction& rhs)
{
    return !(lhs == rhs);
}

constexpr Fraction operator*(Fraction lhs, const Fraction& rhs)
{
    return lhs *= rhs;
}

int main()
{
    constexpr Fraction f1{3, 8}, f2{1, 2}, f3{10, 2};
    std::cout << f1 << " * " << f2 << " = " << f1 * f2 << '\n'
              << f2 << " * " << f3 << " = " << f2 * f3 << '\n'
              <<  2 << " * " << f1 << " = " <<  2 * f1 << '\n';
    static_assert(f3 == f2 * 10);
}
```

Output:

```
3/8 * 1/2 = 3/16
1/2 * 5/1 = 5/2
2 * 3/8 = 3/4
```

### Defect reports

The following behavior-changing defect reports were applied retroactively to previously published C++ standards.

DR | Applied to | Behavior as published | Correct behavior

CWG 1481 | C++98 | the non-member prefix increment operator could only have a parameterof class type, enumeration type, or a reference type to such types | no type requirement

CWG 2931 | C++23 | explicit object member operator functions could only have no parameterof class type, enumeration type, or a reference type to such types | prohibited

### See also

- Operator precedence

- Alternative operator syntax

- Argument-dependent lookup

Common operators

Assignment | Increment,decrement | Arithmetic | Logical | Comparison | Memberaccess | Other

```
a = b
a += b
a -= b
a *= b
a /= b
a %= b
a &= b
a |= b
a ^= b
a <<= b
a >>= b
```

```
++a
--a
a++
a--
```

```
+a
-a
a + b
a - b
a * b
a / b
a % b
~a
a & b
a | b
a ^ b
a << b
a >> b
```

```
!a
a && b
a || b
```

```
a == b
a != b
a < b
a > b
a <= b
a >= b
a <=> b
```

```
a[...]
*a
&a
a->b
a.b
a->*b
a.*b
```

function calla(...)

commaa, b

conditionala ? b : c

Special operators

static_cast converts one type to another related type dynamic_cast converts within inheritance hierarchies const_cast adds or removes cv-qualifiers reinterpret_cast converts type to unrelated type C-style cast converts one type to another by a mix of static_cast, const_cast, and reinterpret_cast new creates objects with dynamic storage duration delete destructs objects previously created by the new expression and releases obtained memory area sizeof queries the size of a type sizeof... queries the size of a pack (since C++11) typeid queries the type information of a type noexcept checks if an expression can throw an exception (since C++11) alignof queries alignment requirements of a type (since C++11) ^^ produces a reflection value from a grammatical construct (since C++26)

### External links

- ↑ Operator Overloading on StackOverflow C++ FAQ
