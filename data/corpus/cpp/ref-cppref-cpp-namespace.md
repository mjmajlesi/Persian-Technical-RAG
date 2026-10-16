Source: https://en.cppreference.com/w/cpp/language/namespace
Retrieved: 2026-10-16
License: CC-BY-SA (cppreference.com)

# Namespaces - cppreference.com

# Namespaces

Namespaces provide a method for preventing name conflicts in large projects.

Entities declared inside a namespace block are placed in a namespace scope, which prevents them from being mistaken for identically-named entities in other scopes.

Entities declared outside all namespace blocks belong to the global namespace. The global namespace belongs to the global scope, and can be referred to explicitly with a leading ::. While it has no declaration, the global namespace is not an unnamed namespace.

Multiple namespace blocks with the same name are allowed. All declarations within these blocks are declared in the same namespace scope.

### Syntax

namespace ns-name { declarations } | (1)

inline namespace ns-name { declarations } | (2) | (since C++11)

namespace { declarations } | (3)

ns-name :: member-name | (4)

using namespace ns-name ; | (5)

using ns-name :: member-name ; | (6)

namespace name = qualified-namespace ; | (7)

namespace ns-name :: member-name { declarations } | (8) | (since C++17)

namespace ns-name :: inline member-name { declarations } | (9) | (since C++20)

### Explanation

#### Namespaces

inline(optional) namespace attr ﻿(optional) identifier {  namespace-body }

inline | - | (since C++11) if present, makes this an inline namespace (see below). Cannot appear on the extension-namespace-definition if the original-namespace-definition did not use inline

attr | - | (since C++17) optional sequence of any number of attributes

- a previously unused identifier, in which case this is original-namespace-definition;

- the name of a namespace, in which case this is extension-namespace-definition;

- a sequence of enclosing namespace specifiers separated by ::, ending with identifier, in which case this is a nested-namespace-definition

(since C++17)

namespace-body | - | possibly empty sequence of declarations of any kind (including class and function definitions as well as nested namespaces)

Namespace definitions are only allowed at namespace scope, including the global scope.

To reopen an existing namespace (formally, to be an extension-namespace-definition), the lookup for the identifier used in the namespace definition must resolve to a namespace name (not a namespace alias), that was declared as a member of the enclosing namespace or of an inline namespace within an enclosing namespace.

The namespace-body defines a namespace scope, which affects name lookup.

All names introduced by the declarations that appear within namespace-body (including nested namespace definitions) become members of the namespace identifier, whether this namespace definition is the original namespace definition (which introduced identifier), or an extension namespace definition (which "reopened" the already defined namespace)

A namespace member that was declared within a namespace body may be defined or redeclared outside of it using explicit qualification

```
namespace Q
{
    namespace V   // V is a member of Q, and is fully defined within Q
    { // namespace Q::V { // C++17 alternative to the lines above
        class C { void m(); }; // C is a member of V and is fully defined within V
                               // C::m is only declared
        void f(); // f is a member of V, but is only declared here
    }
    
    void V::f() // definition of V's member f outside of V
                // f's enclosing namespaces are still the global namespace, Q, and Q::V
    {
        extern void h(); // This declares ::Q::V::h
    }
    
    void V::C::m() // definition of V::C::m outside of the namespace (and the class body)
                   // enclosing namespaces are the global namespace, Q, and Q::V
    {}
}
```

Out-of-namespace definitions and redeclarations are only allowed

- after the point of declaration,

- at namespace scope, and

- in namespaces that enclose the original namespace (including the global namespace).

Also, they must use qualified-id syntax.

```
namespace Q
{
    namespace V    // original-namespace-definition for V
    {
        void f();  // declaration of Q::V::f
    }
    
    void V::f() {} // OK
    void V::g() {} // Error: g() is not yet a member of V
    
    namespace V    // extension-namespace-definition for V
    {
        void g();  // declaration of Q::V::g
    }
}

namespace R           // not an enclosing namespace for Q
{
    void Q::V::g() {} // Error: cannot define Q::V::g inside R
}

void Q::V::g() {}     // OK: global namespace encloses Q
```

Names introduced by friend declarations within a non-local class X become members of the innermost enclosing namespace of X, but they do not become visible to ordinary name lookup (neither unqualified nor qualified) unless a matching declaration is provided at namespace scope, either before or after the class definition. Such name may be found through ADL which considers both namespaces and classes.

Only the innermost enclosing namespace is considered by such friend declaration when deciding whether the name would conflict with a previously declared name.

```
void h(int);
namespace A
{
    class X
    {
        friend void f(X);       // A::f is a friend
        
        class Y
        {
            friend void g();    // A::g is a friend
            friend void h(int); // A::h is a friend, no conflict with ::h
        };
    };
    // A::f, A::g and A::h are not visible at namespace scope
    // even though they are members of the namespace A
    
    X x;
    void g()  // definition of A::g
    {
        f(x); // A::X::f is found through ADL
    }
    
    void f(X) {}   // definition of A::f
    void h(int) {} // definition of A::h
    // A::f, A::g and A::h are now visible at namespace scope
    // and they are also friends of A::X and A::X::Y
}
```

#### Inline namespaces

An inline namespace is a namespace that uses the optional keyword inline in its original-namespace-definition.

Members of an inline namespace are treated as if they are members of the enclosing namespace in many situations (listed below). This property is transitive: if a namespace N contains an inline namespace M, which in turn contains an inline namespace O, then the members of O can be used as though they were members of M or N.

- A using-directive that names the inline namespace is implicitly inserted in the enclosing namespace (similar to the implicit using-directive for the unnamed namespace)

- In argument-dependent lookup, when a namespace is added to the set of associated namespaces, its inline namespaces are added as well, and if an inline namespace is added to the list of associated namespaces, its enclosing namespace is added as well.

- Each member of an inline namespace can be partially specialized, explicitly instantiated, or explicitly specialized as if it were a member of the enclosing namespace.

- Qualified name lookup that examines the enclosing namespace will include the names from the inline namespaces even if the same name is present in the enclosing namespace.

```
// in C++14, std::literals and its member namespaces are inline
{
    using namespace std::string_literals; // makes visible operator""s 
                                          // from std::literals::string_literals
    auto str = "abc"s;
}

{
    using namespace std::literals; // makes visible both
                                   // std::literals::string_literals::operator""s
                                   // and std::literals::chrono_literals::operator""s
    auto str = "abc"s;
    auto min = 60s;
}

{
    using std::operator""s; // makes both std::literals::string_literals::operator""s
                            // and std::literals::chrono_literals::operator""s visible
    auto str = "abc"s;
    auto min = 60s;
}
```

Note: the rule about specializations allows library versioning: different implementations of a library template may be defined in different inline namespaces, while still allowing the user to extend the parent namespace with an explicit specialization of the primary template:

```
namespace Lib
{
    inline namespace Lib_1
    {
        template<typename T> class A; 
    }

    template<typename T> void g(T) { /* ... */ }
}
/* ... */
struct MyClass { /* ... */ };
namespace Lib
{
    template<> class A<MyClass> { /* ... */ };
}

int main()
{
    Lib::A<MyClass> a;
    g(a);  // ok, Lib is an associated namespace of A
}
```

(since C++11)

#### Unnamed namespaces

The unnamed-namespace-definition is a namespace definition of the form

inline(optional) namespace attr ﻿(optional) {  namespace-body }

inline | - | (since C++11) if present, makes this an inline namespace

attr | - | (since C++17) optional sequence of any number of attributes

This definition is treated as a definition of a namespace with unique name and a using-directive in the current scope that nominates this unnamed namespace (Note: implicitly added using directive makes namespace available for the qualified name lookup and unqualified name lookup, but not for the argument-dependent lookup). The unique name is unique over the entire program, but within a translation unit each unnamed namespace definition maps to the same unique name: multiple unnamed namespace definitions in the same scope denote the same unnamed namespace.

```
namespace
{
    int i; // defines ::(unique)::i
}

void f()
{
    i++;   // increments ::(unique)::i
}

namespace A
{
    namespace
    {
        int i;        // A::(unique)::i
        int j;        // A::(unique)::j
    }
    
    void g() { i++; } // A::(unique)::i++
}

using namespace A; // introduces all names from A into global namespace

void h()
{
    i++;    // error: ::(unique)::i and ::A::(unique)::i are both in scope
    A::i++; // ok, increments ::A::(unique)::i
    j++;    // ok, increments ::A::(unique)::j
}
```

Even though names in an unnamed namespace may be declared with external linkage, they are never accessible from other translation units because their namespace name is unique.

(until C++11)

Unnamed namespaces as well as all namespaces declared directly or indirectly within an unnamed namespace have internal linkage, which means that any name that is declared within an unnamed namespace has internal linkage.

(since C++11)

#### Using-declarations

Introduces a name that is defined elsewhere into the declarative region where this using-declaration appears.

using typename(optional) nested-name-specifier unqualified-id ; | (until C++17)

using declarator-list ; | (since C++17)

typename | - | the keyword typename may be used as necessary to resolve dependent names, when the using-declaration introduces a member type from a base class into a class template

nested-name-specifier | - | a sequence of names and scope resolution operators ::, ending with a scope resolution operator. A single :: refers to the global namespace.

unqualified-id | - | an id-expression

declarator-list | - | comma-separated list of one or more declarators of the form typename(optional) nested-name-specifier unqualified-id. A declarator may be followed by an ellipsis to indicate pack expansion, although that form is only meaningful in derived class definitions

Using-declarations can be used to introduce namespace members into other namespaces and block scopes, or to introduce base class members into derived class definitions, or to introduce enumerators into namespaces, block, and class scopes(since C++20).

A using-declaration with more than one using-declarator is equivalent to a corresponding sequence of using-declarations with one using-declarator.

(since C++17)

For the use in derived class definitions, see using declaration.

Names introduced into a namespace scope by a using-declaration can be used just like any other names, including qualified lookup from other scopes:

```
void f();
namespace A
{
    void g();
}

namespace X
{
    using ::f;        // global f is now visible as ::X::f
    using A::g;       // A::g is now visible as ::X::g
    using A::g, A::g; // (C++17) OK: double declaration allowed at namespace scope
}

void h()
{
    X::f(); // calls ::f
    X::g(); // calls A::g
}
```

If, after the using-declaration was used to take a member from a namespace, the namespace is extended and additional declarations for the same name are introduced, those additional declarations do not become visible through the using-declaration (in contrast with using-directive). One exception is when a using-declaration names a class template: partial specializations introduced later are effectively visible, because their lookup proceeds through the primary template.

```
namespace A
{
    void f(int);
}
using A::f; // ::f is now a synonym for A::f(int)

namespace A       // namespace extension
{
    void f(char); // does not change what ::f means
}

void foo()
{
    f('a'); // calls f(int), even though f(char) exists.
}

void bar()
{
    using A::f; // this f is a synonym for both A::f(int) and A::f(char)
    f('a');     // calls f(char)
}
```

Using-declarations cannot name template-id, or namespace, or a scoped enumerator(until C++20). Each declarator in a using-declaration introduces one and only one name, for example using-declaration for an enumeration does not introduce any of its enumerators.

All restrictions on regular declarations of the same names, hiding, and overloading rules apply to using-declarations:

```
namespace A
{
    int x;
}

namespace B
{
    int i;
    struct g {};
    struct x {};
    
    void f(int);
    void f(double);
    void g(char); // OK: function name g hides struct g
}

void func()
{
    int i;
    using B::i;   // error: i declared twice

    void f(char);
    using B::f;   // OK: f(char), f(int), f(double) are overloads
    f(3.5);       // calls B::f(double)

    using B::g;
    g('a');       // calls B::g(char)
    struct g g1;  // declares g1 to have type struct B::g

    using B::x;
    using A::x;   // OK: hides struct B::x
    x = 99;       // assigns to A::x
    struct x x1;  // declares x1 to have type struct B::x
}
```

If a function was introduced by a using-declaration, declaring a function with the same name and parameter list is ill-formed (unless the declaration is for the same function). If a function template was introduced by a using-declaration, declaring a function template with the same name, parameter type list, return type, and template parameter list is ill-formed. Two using-declarations can introduce functions with the same name and parameter list, but if a call to that function is attempted, the program is ill-formed.

```
namespace B
{
    void f(int);
    void f(double);
}

namespace C
{
    void f(int);
    void f(double);
    void f(char);
}

void h()
{
    using B::f;  // introduces B::f(int), B::f(double)
    using C::f;  // introduces C::f(int), C::f(double), and C::f(char)
    f('h');      // calls C::f(char)
    f(1);        // error: B::f(int) or C::f(int)?
    void f(int); // error: f(int) conflicts with C::f(int) and B::f(int)
}
```

If an entity is declared, but not defined in some inner namespace, and then declared through using-declaration in the outer namespace, and then a definition appears in the outer namespace with the same unqualified name, that definition is a member of the outer namespace and conflicts with the using-declaration:

```
namespace X
{
    namespace M
    {
        void g(); // declares, but doesn't define X::M::g()
    }
    using M::g;
    
    void g();     // Error: attempt to declare X::g which conflicts with X::M::g()
}
```

More generally, a declaration that appears in any namespace scope and introduces a name using an unqualified identifier always introduces a member into the namespace it's in and not to any other namespace. The exceptions are explicit instantiations and explicit specializations of a primary template that is defined in an inline namespace: because they do not introduce a new name, they may use unqualified-id in an enclosing namespace.

#### Using-directives

A using-directive is a block-declaration with the following syntax:

attr ﻿(optional) using namespace namespace-name ; | (1)

attr ﻿(optional) using namespace splice-specifier ; | (2) | (since C++26)

attr | - | (since C++11) any number of attributes that apply to this using-directive

namespace-name | - | a (possibly qualified) name of a namespace. When looking up this name, lookup considers namespace declarations only. It must not contain a dependent splice specifier(since C++26)

splice-specifier | - | a splice specifier which must not be dependent

Using-directives are allowed only in namespace scope and in block scope. From the point of view of unqualified name lookup of any name after a using-directive and until the end of the scope in which it appears, every name from namespace-name or splice-specifier(since C++26) is visible as if it were declared in the nearest enclosing namespace which contains both the using-directive and namespace-name or splice-specifier(since C++26).

Using-directive does not add any names to the declarative region in which it appears (unlike the using-declaration), and thus does not prevent identical names from being declared.

Using-directives are transitive for the purposes of unqualified lookup: if a scope contains a using-directive that nominates a namespace-name, which itself contains using-directive for some namespace-name-2, the effect is as if the using directives from the second namespace appear within the first. The order in which these transitive namespaces occur does not influence name lookup.

```
namespace A
{
    int i;
}

namespace B
{
    int i;
    int j;
    
    namespace C
    {
        namespace D
        {
            using namespace A;
            // Names from A are "injected" into D.
            // Unqualified lookup within D considers these names to have the same
            // scope as the global scope (e.g. for the purposes of name hiding).
            // Qualified lookup referring to D (D::name for some name)
            // will find the same name as unqualified lookup within D.
            
            int j;
            int k;
            int a = i;   // i is B::i, because A::i is hidden by B::i
            int b = ::i; // error: there is still no i in the global namespace
        }
        
        using namespace D; // names from D and A are injected into C
        
        int k = 89; // OK to declare name identical to one introduced by a using
        int l = k;  // ambiguous: C::k or D::k
        int m = i;  // ok: B::i hides A::i
        int n = j;  // ok: D::j hides B::j
    }
}

// These are all equivalent definitions:
int t0 = B::i;
int t1 = B::C::a;
int t2 = B::C::D::a;
```

If, after a using-directive was used to nominate some namespace, the namespace is extended and additional members and/or using-directives are added to it, those additional members and the additional namespaces are visible through the using-directive (in contrast with using-declaration)

```
namespace D
{
    int d1;
    void f(char);
}
using namespace D; // introduces D::d1, D::f, D::d2, D::f,
                   // E::e, and E::f into global namespace!

int d1;            // OK: no conflict with D::d1 when declaring

namespace E
{
    int e;
    void f(int);
}

namespace D            // namespace extension
{
    int d2;
    using namespace E; // transitive using-directive
    void f(int);
}

void f()
{
    d1++;    // error: ambiguous ::d1 or D::d1?
    ::d1++;  // OK
    D::d1++; // OK
    d2++;    // OK, d2 is D::d2
    
    e++;     // OK: e is E::e due to transitive using
    
    f(1);    // error: ambiguous: D::f(int) or E::f(int)?
    f('a');  // OK: the only f(char) is D::f(char)
}
```

### Notes

The using-directive using namespace std; at any namespace scope introduces every name from the namespace std into the global namespace (since the global namespace is the nearest namespace that contains both std and any user-declared namespace), which may lead to undesirable name collisions. This, and other using directives are generally considered bad practice at file scope of a header file (SF.7: Don’t write using namespace at global scope in a header file).

Feature-test macro | Value | Std | Feature

__cpp_namespace_attributes | 201411L | (C++17) | Attributes for namespaces

### Keywords

namespace, using, inline

### Example

This example shows how to use a namespace to create a class that already has been named in the std namespace.

```
#include <vector>

namespace vec
{
    template<typename T>
    class vector
    {
        // ...
    };
} // of vec

int main()
{
    std::vector<int> v1; // Standard vector.
    vec::vector<int> v2; // User defined vector.

    // v1 = v2;          // Error: v1 and v2 are different object's type.

    {
        using namespace std;
        vector<int> v3;  // Same as std::vector
        v1 = v3; // OK
    }

    {
        using vec::vector;
        vector<int> v4;  // Same as vec::vector
        v2 = v4; // OK
    }
}
```

### Defect reports

The following behavior-changing defect reports were applied retroactively to previously published C++ standards.

DR | Applied to | Behavior as published | Correct behavior

CWG 101 | C++98 | the program is ill-formed if a function declaration in namespacescope or block scope and a function introduced by ausing-declaration declare the same function (no ambiguity) | allowed

CWG 373 | C++98 | lookup only considered namespace declarations only forthe last name in the operand of a using-directive (which issub-optimal, because classes cannot contain namespaces) | the lookup restrictionapplies to all names in theoperands of using-directives

CWG 460 | C++98 | a using-declaration could name a namespace | prohibited

CWG 565 | C++98 | a using-declaration cannot introduce a functionidentical to another function in the same scope, butthe restriction was not applied to function templates | apply the same restrictionto function templates as well

CWG 986 | C++98 | using-directive was transitive for qualified lookup | only transitive for unqualified lookup

CWG 987 | C++98 | entities declared in a nested namespace wasalso members of the enclosing namespace | nested scopes excluded

CWG 1021 | C++98 | it was unclear whether an entity whose definitionis introduced to a namespace via using-declarationis considered to be defined in that namespace | not defined in that namespace

CWG 1838 | C++98 | unqualified definition in an outer namespacecould define an entity declared, but not defined inanother namespace and pulled in by a using | unqualified definitionalways refers toits namespace

CWG 2155 | C++98 | the resolution of CWG issue 1838 was notapplied to class and enumeration declarations | applied

### See also

namespace alias | creates an alias of an existing namespace[edit]
