Source: https://en.cppreference.com/w/cpp/io/cout
Retrieved: 2026-10-16
License: CC-BY-SA (cppreference.com)

# std::cout, std::wcout - cppreference.com

# std::cout, std::wcout

Defined in header <iostream>

```
extern std::ostream cout;
```

(1)

```
extern std::wostream wcout;
```

(2)

The global objects std::cout and std::wcout control output to a stream buffer of implementation-defined type (derived from std::streambuf), associated with the standard C output stream stdout.

These objects are guaranteed to be initialized during or before the first time an object of type std::ios_base::Init is constructed and are available for use in the constructors and destructors of static objects with ordered initialization (as long as <iostream> is included before the object is defined).

Unless std::ios_base::sync_with_stdio(false) has been issued, it is safe to concurrently access these objects from multiple threads for both formatted and unformatted output.

By specification of std::cin, std::cin.tie() returns &std::cout. This means that any input operation on std::cin executes std::cout.flush() (via std::basic_istream::sentry's constructor). Similarly, std::wcin.tie() returns &std::wcout.

By specification of std::cerr, std::cerr.tie() returns &std::cout. This means that any output operation on std::cerr executes std::cout.flush() (via std::basic_ostream::sentry's constructor). Similarly, std::wcerr.tie() returns &std::wcout. (since C++11)

### Notes

The 'c' in the name refers to "character" (stroustrup.com FAQ); cout means "character output" and wcout means "wide character output".

Because dynamic initialization of templated variables are unordered, it is not guaranteed that std::cout has been initialized to a usable state before the initialization of such variables begins, unless an object of type std::ios_base::Init has been constructed.

### Example

```
#include <iostream>

struct Foo
{
    int n;
    Foo()
    {
        std::cout << "static constructor\n";
    }
    ~Foo()
    {
        std::cout << "static destructor\n";
    }
};

Foo f; // static object

int main()
{
    std::cout << "main function\n";
}
```

Output:

```
static constructor
main function
static destructor
```

### See also

Init | initializes standard stream objects  (public member class of std::ios_base) [edit]

cerrwcerr | writes to the standard C error stream stderr, unbuffered(global object)[edit]

clogwclog | writes to the standard C error stream stderr(global object)[edit]

stdinstdoutstderr | expression of type FILE* associated with the input streamexpression of type FILE* associated with the output streamexpression of type FILE* associated with the error output stream  (macro constant) [edit]
