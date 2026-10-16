Source: https://en.cppreference.com/w/cpp/language/constructor
Retrieved: 2026-10-16
License: CC-BY-SA (cppreference.com)

# Constructors and member initializer lists - cppreference.com

# Constructors and member initializer lists

Constructors are non-static member functions declared with a special declarator syntax, they are used to initialize objects of their class types.

A constructor cannot be a coroutine.

(since C++20)

A constructor cannot have an explicit object parameter.

(since C++23)

### Syntax

Constructors are declared using member function declarators of the following form:

class-name ( parameter-list ﻿(optional) ) except ﻿(optional) attr ﻿(optional)

class-name | - | an identifier expression, possibly followed by a list of attributes, and(since C++11) possibly enclosed by a pair parentheses

parameter-list | - | parameter list

dynamic exception specification

(until C++11)

either dynamic exception specificationor noexcept specification

(since C++11)(until C++17)

noexcept specification

(since C++17)

attr | - | (since C++11) a list of attributes

The only specifiers allowed in the declaration specifiers of a constructor declaration are friend, inline, constexpr(since C++11), consteval(since C++20), and explicit (in particular, no return type is allowed). Note that cv- and ref-qualifiers are not allowed either: const and volatile semantics of an object under construction only kick in after the most-derived constructor completes.

The identifier expression of class-name must have one of the following forms:

- In a friend declaration, the identifier expression is a qualified identifier that names a constructor.

- Otherwise, in a member declaration that belongs to the member specification of a class or class template:

- For classes, the identifier expression is the injected-class-name of the immediately-enclosing class.

- For class templates, the identifier expression is a class name that names the current instantiation(until C++20)the injected-class-name(since C++20) of the immediately-enclosing class template.

- Otherwise, the identifier expression is a qualified identifier whose terminal unqualified identifier is the injected-class-name of its lookup context.

### Member initializer list

The body of a function definition of any constructor, before the opening brace of the compound statement, may include the member initializer list, whose syntax is the colon character :, followed by the comma-separated list of one or more member-initializer ﻿s, each of which has the following syntax:

class-or-identifier ( expression-list ﻿(optional) ) | (1)

class-or-identifier braced-init-list | (2) | (since C++11)

parameter-pack ... | (3) | (since C++11)

class-or-identifier | - | any identifier that names a non-static data member or any type name which names either the class itself (for delegating constructors) or a direct or virtual base.

expression-list | - | possibly empty, comma-separated list of the arguments to pass to the constructor of the base or member

braced-init-list | - | brace-enclosed initializer list

parameter-pack | - | name of a variadic template parameter pack

```
struct S
{
    int n;
    
    S(int);       // constructor declaration
    
    S() : n(7) {} // constructor definition:
                  // ": n(7)" is the initializer list
                  // ": n(7) {}" is the function body
};

S::S(int x) : n{x} {} // constructor definition: ": n{x}" is the initializer list

int main()
{
    S s;      // calls S::S()
    S s2(10); // calls S::S(int)
}
```

### Explanation

Constructors have no names and cannot be called directly. They are invoked when initialization takes place, and they are selected according to the rules of initialization. The constructors without explicit specifier are converting constructors. The constructors with a constexpr specifier make their type a literal type. Constructors that may be called without any argument are default constructors. Constructors that take another object of the same type as the argument are copy constructors and move constructors.

Before the compound statement that forms the function body of the constructor begins executing, initialization of all direct bases, virtual bases, and non-static data members is finished. The member initializer list is the place where non-default initialization of these subobjects can be specified. For bases that cannot be default-initialized and for non-static data members that cannot be initialized by default-initialization or by their default member initializer, if any(since C++11), such as members of reference and const-qualified types, member initializers must be specified. (Note that default member initializers for non-static data members of class template instantiations may be invalid if the member type or initializer is dependent.)(since C++11) No initialization is performed for anonymous unions or variant members that do not have a member initializer or default member initializer(since C++11).

The initializers where class-or-identifier names a virtual base class are ignored during construction of any class that is not the most derived class of the object that's being constructed.

Names that appear in expression-list or braced-init-list are evaluated in scope of the constructor:

```
class X
{
    int a, b, i, j;
public:
    const int& r;
    X(int i)
      : r(a) // initializes X::r to refer to X::a
      , b{i} // initializes X::b to the value of the parameter i
      , i(i) // initializes X::i to the value of the parameter i
      , j(this->i) // initializes X::j to the value of X::i
    {}
};
```

Exceptions that are thrown from member initializers may be handled by a function try block.

If a non-static data member has a default member initializer and also appears in a member initializer list, then the member initializer is used and the default member initializer is ignored:

```
struct S
{
    int n = 42;   // default member initializer
    S() : n(7) {} // will set n to 7, not 42
};
```

(since C++11)

Reference members cannot be bound to temporaries in a member initializer list:

```
struct A
{
    A() : v(42) {} // Error
    const int& v;
};
```

Note: same applies to default member initializer.

#### Operations during construction and destruction

Member functions (including virtual member functions) can be called for an object under construction or destruction. Similarly, an object under construction or destruction can be the operand of typeid or dynamic_cast.

However, if these operations are performed during any of the following evaluations, the behavior is undefined:

- an evaluation of a precondition assertion of a constructor

- an evaluation of a postcondition assertion of a destructor

(since C++26)

- an evaluation of a member initializer list before all the member-initializer ﻿s for base classes have completed

#### Delegating constructor

If the name of the class itself appears as class-or-identifier in the member initializer list, then the list must consist of that one member initializer only; such a constructor is known as the delegating constructor, and the constructor selected by the only member of the initializer list is the target constructor.

In this case, the target constructor is selected by overload resolution and executed first, then the control returns to the delegating constructor and its body is executed.

Delegating constructors cannot be recursive.

```
class Foo
{
public: 
    Foo(char x, int y) {}
    Foo(int y) : Foo('a', y) {} // Foo(int) delegates to Foo(char, int)
};
```

#### Inheriting constructors

See using declaration.

(since C++11)

#### Initialization order

The order of member initializers in the list is irrelevant, the actual order of initialization is as follows:

(Note: if initialization order was controlled by the appearance in the member initializer lists of different constructors, then the destructor wouldn't be able to ensure that the order of destruction is the reverse of the order of construction.)

### Notes

Feature-test macro | Value | Std | Feature

__cpp_delegating_constructors | 200604L | (C++11) | Delegating constructors

### Example

```
#include <fstream>
#include <string>
#include <mutex>

struct Base
{
    int n;
};   

struct Class : public Base
{
    unsigned char x;
    unsigned char y;
    std::mutex m;
    std::lock_guard<std::mutex> lg;
    std::fstream f;
    std::string s;
    
    Class(int x) : Base{123}, // initialize base class
        x(x),     // x (member) is initialized with x (parameter)
        y{0},     // y initialized to 0
        f{"test.cc", std::ios::app}, // this takes place after m and lg are initialized
        s(__func__), // __func__ is available because init-list is a part of constructor
        lg(m),    // lg uses m, which is already initialized
        m{}       // m is initialized before lg even though it appears last here
    {}            // empty compound statement
    
    Class(double a) : y(a + 1),
        x(y), // x will be initialized before y, its value here is indeterminate
        lg(m)
    {} // base class initializer does not appear in the list, it is
       // default-initialized (not the same as if Base() were used, which is value-init)
    
    Class()
    try // function try block begins before the function body, which includes init list
      : Class(0.0) // delegate constructor
    {
        // ...
    }
    catch (...)
    {
        // exception occurred on initialization
    }
};

int main()
{
    Class c;
    Class c1(1);
    Class c2(0.1);
}
```

### Defect reports

The following behavior-changing defect reports were applied retroactively to previously published C++ standards.

DR | Applied to | Behavior as published | Correct behavior

CWG 194 | C++98 | the declarator syntax of constructor only allowedat most one function specifier (e.g. a constructorcannot be declared inline explicit) | multiple functionspecifiers allowed

CWG 257 | C++98 | it was unspecified whether an abstract class shouldprovide member initializers for its virtual base classes | specified as not requiredand such member initializersare ignored during execution

CWG 263 | C++98 | the declarator syntax of constructorprohibited constructors from being friends | allowed constructorsto be friends

CWG 1345 | C++98 | anonymous union members without defaultmember initializers were default-initialized | they are not initialized

CWG 1435 | C++98 | the meaning of “class name” in thedeclarator syntax of constructor was unclear | changed the syntax to a specializedfunction declarator syntax

CWG 1696 | C++98 | reference members could be initialized to temporaries(whose lifetime would end at the end of constructor) | such initializationis ill-formed

### References

- C++23 standard (ISO/IEC 14882:2024):

- 11.4.5 Constructors [class.ctor]

- 11.9.3 Initializing bases and members [class.base.init]

- C++20 standard (ISO/IEC 14882:2020):

- 11.4.4 Constructors [class.ctor]

- 11.10.2 Initializing bases and members [class.base.init]

- C++17 standard (ISO/IEC 14882:2017):

- 15.1 Constructors [class.ctor]

- 15.6.2 Initializing bases and members [class.base.init]

- C++14 standard (ISO/IEC 14882:2014):

- 12.1 Constructors [class.ctor]

- 12.6.2 Initializing bases and members [class.base.init]

- C++11 standard (ISO/IEC 14882:2011):

- 12.1 Constructors [class.ctor]

- 12.6.2 Initializing bases and members [class.base.init]

- C++98 standard (ISO/IEC 14882:1998):

- 12.1 Constructors [class.ctor]

- 12.6.2 Initializing bases and members [class.base.init]

### See also

- copy elision

- converting constructor

- copy assignment

- copy constructor

- default constructor

- destructor

- explicit

- initialization

- aggregate initialization

- constant initialization

- copy initialization

- default initialization

- direct initialization

- list initialization

- reference initialization

- value initialization

- zero initialization

- move assignment

- move constructor

- new
