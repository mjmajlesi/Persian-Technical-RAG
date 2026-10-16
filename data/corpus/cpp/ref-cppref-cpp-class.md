Source: https://en.cppreference.com/w/cpp/language/class
Retrieved: 2026-10-16
License: CC-BY-SA (cppreference.com)

# Class declaration - cppreference.com

# Class declaration

Classes are user-defined types, defined by class-specifier, which appears in decl-specifier-seq of the declaration syntax.

### Syntax

The class specifier has the following syntax:

class-key attr ﻿(optional) class-head-name final(optional) base-clause ﻿(optional) { member-specification } | (1)

class-key attr ﻿(optional) base-clause ﻿(optional) { member-specification } | (2)

class-key | - | one of class, struct and union. The keywords class and struct are identical except for the default member access and the default base class access. If it is union, the declaration introduces a union type.

attr | - | (since C++11) any number of attributes, may include alignas specifier

class-head-name | - | the name of the class that's being defined, optionally qualified

final | - | (since C++11) if present, the class cannot be derived

base-clause | - | list of one or more base classes and the model of inheritance used for each (see derived class)

member-specification | - | list of access specifiers, member object and member function declarations and definitions (see below)

### Forward declaration

A declaration of the following form

class-key attr identifier ;

Declares a class type which will be defined later in this scope. Until the definition appears, this class name has incomplete type. This allows classes that refer to each other:

```
class Vector; // forward declaration

class Matrix
{
    // ...
    friend Vector operator*(const Matrix&, const Vector&);
};

class Vector
{
    // ...
    friend Vector operator*(const Matrix&, const Vector&);
};
```

and if a particular source file only uses pointers and references to the class, this makes it possible to reduce #include dependencies:

```
// In MyStruct.h
#include <iosfwd> // contains forward declaration of std::ostream

struct MyStruct
{
    int value;
    friend std::ostream& operator<<(std::ostream& os, const S& s);
    // definition provided in MyStruct.cpp file which uses #include <ostream>
};
```

If forward declaration appears in local scope, it hides previously declared class, variable, function, and all other declarations of the same name that may appear in enclosing scopes:

```
struct s { int a; };
struct s; // does nothing (s already defined in this scope)

void g()
{
    struct s; // forward declaration of a new, local struct "s"
              // this hides global struct s until the end of this block
    
    s* p; // pointer to local struct s
    
    struct s { char* p; }; // definitions of the local struct s
}
```

Note that a new class name may also be introduced by an elaborated type specifier which appears as part of another declaration, but only if name lookup can't find a previously declared class with the same name.

```
class U;

namespace ns
{
    class Y f(class T p); // declares function ns::f and declares ns::T and ns::Y
    
    class U f(); // U refers to ::U
    
    // can use pointers and references to T and Y
    Y* p;
    T* q;
}
```

### Member specification

The member specification, or the body of a class definition, is a brace-enclosed sequence of any number of the following:

attr ﻿(optional) decl-specifier-seq ﻿(optional) member-declarator-list ﻿(optional) ;

attr | - | (since C++11) any number of attributes

decl-specifier-seq | - | sequence of specifiers. It is only optional in the declarations of constructors, destructors, and user-defined type conversion functions

member-declarator-list | - | similar to an init-declarator-list, but additionally allows bit-field declaration, pure-specifier, and virt-specifier (override or final)(since C++11), and does not allow direct-non-list-initialization syntax.

This declaration may declare static and non-static data members and member functions, member typedefs, member enumerations, and nested classes. It may also be a friend declaration.

```
class S
{
    int d1;             // non-static data member
    int a[10] = {1, 2}; // non-static data member with initializer (C++11)
    
    static const int d2 = 1; // static data member with initializer
    
    virtual void f1(int) = 0; // pure virtual member function
    
    std::string d3, *d4, f2(int); // two data members and a member function
    
    enum { NORTH, SOUTH, EAST, WEST };
    
    struct NestedS
    {
        std::string s;
    } d5, *d6;
    
    typedef NestedS value_type, *pointer_type;
};
```

```
class M
{
    std::size_t C;
    std::vector<int> data;
public:
    M(std::size_t R, std::size_t C) : C(C), data(R*C) {} // constructor definition
    
    int operator()(std::size_t r, std::size_t c) const // member function definition
    {
        return data[r * C + c];
    }
    
    int& operator()(std::size_t r, std::size_t c) // another member function definition
    {
        return data[r * C + c];
    }
};
```

```
class S
{
public:
    S();          // public constructor
    S(const S&);  // public copy constructor
    virtual ~S(); // public virtual destructor
private:
    int* ptr; // private data member
};
```

```
class Base
{
protected:
    int d;
};

class Derived : public Base
{
public:
    using Base::d;    // make Base's protected member d a public member of Derived
    using Base::Base; // inherit all bases' constructors (C++11)
};
```

```
template<typename T>
struct Foo
{
    static_assert(std::is_floating_point<T>::value, "Foo<T>: T must be floating point");
};
```

```
struct S
{
    template<typename T>
    void f(T&& n);
    
    template<class CharT>
    struct NestedS
    {
        std::basic_string<CharT> s;
    };
};
```

```
template<typename T>
struct identity
{
    using type = T;
};
```

7) alias declarations: | (since C++11)

```
struct S
{
    template<class CharT>
    struct NestedS
    {
        std::basic_string<CharT> s;
    };
    
    template<class CharT>
    NestedS(std::basic_string<CharT>) -> NestedS<CharT>;
};
```

8) deduction guides of member class templates: | (since C++17)

```
enum class color { red, orange, yellow };

struct highlight
{
    using enum color;
};
```

9) Using-enum-declarations: | (since C++20)

### Local classes

A class declaration can appear inside the body of a function, in which case it defines a local class. The name of such a class only exists within the function scope, and is not accessible outside.

- Members of a local class can only be declared in the definition of that class, except that members that are nested classes can also be declared in the nearest enclosing block scope of that class.

- A class nested within a local class is also a local class.

- A local class cannot have static data members.

- Member functions of a local class have no linkage.

- Member functions of a local class have to be defined entirely inside the class body.

- Local classes other than closure types(since C++14) cannot have member templates.

- Local classes cannot have friend templates.

- Local classes cannot define friend functions inside the class definition.

- A local class inside a function (including member function) can access the same names that the enclosing function can access.

- Local classes could not be used as template arguments.

(until C++11)

```
#include <algorithm>
#include <iostream>
#include <vector>

int main()
{
    std::vector<int> v{1, 2, 3};
    
    struct Local
    {
        bool operator()(int n, int m)
        {
            return n > m;
        }
    };
    
    std::sort(v.begin(), v.end(), Local()); // since C++11
    
    for (int n : v)
        std::cout << n << ' ';
    std::cout << '\n';
}
```

Output:

```
3 2 1
```

### Keywords

class, struct, union

### Defect reports

The following behavior-changing defect reports were applied retroactively to previously published C++ standards.

DR | Applied to | Behavior as published | Correct behavior

CWG 1693 | C++98 | member declarations could not be empty | empty declaration allowed

CWG 1930 | C++98 | member-declarator-list could be empty when decl-specifier-seqcontains a storage class specifier or cv qualifier | the list must not be empty

CWG 2890 | C++98 | it was unclear where the members of nested classes can be declared | made clear

### See also

C documentation for Struct declaration
