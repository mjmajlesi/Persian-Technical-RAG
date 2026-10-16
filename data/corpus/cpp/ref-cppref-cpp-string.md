Source: https://en.cppreference.com/w/cpp/string/basic_string
Retrieved: 2026-10-16
License: CC-BY-SA (cppreference.com)

# std::basic_string - cppreference.com

# std::basic_string

Defined in header <string>

```
template<
    class CharT,
    class Traits = std::char_traits<CharT>,
    class Allocator = std::allocator<CharT>
> class basic_string;
```

(1)

```
namespace pmr {
template<
    class CharT,
    class Traits = std::char_traits<CharT>
> using basic_string =
    std::basic_string<CharT, Traits, std::pmr::polymorphic_allocator<CharT>>;
}
```

(2) | (since C++17)

The class template basic_string stores and manipulates sequences of character-like objects, which are non-array objects of TrivialType and StandardLayoutType. The class is dependent neither on the character type nor on the nature of operations on that type. The definitions of the operations are supplied via the Traits template parameter - a specialization of std::char_traits or a compatible traits class.

The elements of a basic_string are stored contiguously, that is, for a basic_string s, &*(s.begin() + n) == &*s.begin() + n for any n in [0, s.size()), and *(s.begin() + s.size()) has value CharT() (a null terminator)(since C++11); or, equivalently, a pointer to s[0] can be passed to functions that expect a pointer to the first element of an array(until C++11)a null-terminated array(since C++11) of CharT.

std::basic_string satisfies the requirements of AllocatorAwareContainer (except that customized construct/destroy are not used for construction/destruction of elements), SequenceContainer and ContiguousContainer(since C++17).

The program is ill-formed if Traits::char_type is not CharT or Allocator::value_type is not CharT.

However, defining a constexpr std::basic_string variable is generally an error, because constant evaluation requires any dynamically allocated storage to be released in the same evaluation, which is usually not the case with std::basic_string's initializer.

All member functions of std::basic_string are constexpr: it is possible to create and use std::basic_string objects in the evaluation of a constant expression. | (since C++20)

Several typedefs for common character types are provided:

Defined in header <string>

Type | Definition

std::string | std::basic_string<char>

std::wstring | std::basic_string<wchar_t>

std::u8string (C++20) | std::basic_string<char8_t>

std::u16string (C++11) | std::basic_string<char16_t>

std::u32string (C++11) | std::basic_string<char32_t>

std::pmr::string (C++17) | std::pmr::basic_string<char>

std::pmr::wstring (C++17) | std::pmr::basic_string<wchar_t>

std::pmr::u8string (C++20) | std::pmr::basic_string<char8_t>

std::pmr::u16string (C++17) | std::pmr::basic_string<char16_t>

std::pmr::u32string (C++17) | std::pmr::basic_string<char32_t>

### Template parameters

CharT | - | character type

Traits | - | traits class specifying the operations on the character type

Allocator | - | Allocator type used to allocate internal storage

### Iterator invalidation

References, pointers, and iterators referring to the elements of a basic_string may be invalidated by any standard library function taking a reference to non-const basic_string as an argument, such as std::getline, std::swap, or operator>>, and by calling non-const member functions, except operator[], at, data, front, back, begin, rbegin, end, and rend.

### Nested types

Type | Definition

traits_type | Traits

value_type | CharT

allocator_type | Allocator[edit]

Allocator::size_type | (until C++11)

std::allocator_traits<Allocator>::size_type | (since C++11)

Allocator::difference_type | (until C++11)

std::allocator_traits<Allocator>::difference_type | (since C++11)

reference | value_type&[edit]

const_reference | const value_type&[edit]

Allocator::pointer

(until C++11)

std::allocator_traits<Allocator>::pointer

(since C++11)

Allocator::const_pointer

(until C++11)

std::allocator_traits<Allocator>::const_pointer

(since C++11)

LegacyRandomAccessIterator and LegacyContiguousIterator to value_type

(until C++20)

LegacyRandomAccessIterator, contiguous_iterator, and ConstexprIterator to value_type

(since C++20)

LegacyRandomAccessIterator and LegacyContiguousIterator to const value_type

(until C++20)

LegacyRandomAccessIterator, contiguous_iterator, and ConstexprIterator to const value_type

(since C++20)

reverse_iterator | std::reverse_iterator<iterator>[edit]

const_reverse_iterator | std::reverse_iterator<const_iterator>[edit]

### Data members

constexpr size_type npos [static] | the special value size_type(-1), its exact meaning depends on the context

### Member functions

(constructor) | constructs a basic_string  (public member function) [edit]

(destructor) | destroys the string, deallocating internal storage if used  (public member function) [edit]

operator= | assigns values to the string  (public member function) [edit]

assign | assign characters to a string  (public member function) [edit]

assign_range(C++23) | assign a range of characters to a string  (public member function) [edit]

get_allocator | returns the associated allocator  (public member function) [edit]

Element access

at | accesses the specified character with bounds checking  (public member function) [edit]

operator[] | accesses the specified character  (public member function) [edit]

front(DR*) | accesses the first character  (public member function) [edit]

back(DR*) | accesses the last character  (public member function) [edit]

data | returns a pointer to the first character of a string  (public member function) [edit]

c_str | returns a non-modifiable standard C character array version of the string  (public member function) [edit]

operator basic_string_view(C++17) | returns a non-modifiable basic_string_view into the entire string  (public member function) [edit]

Iterators

begincbegin(C++11) | returns an iterator to the beginning  (public member function) [edit]

endcend(C++11) | returns an iterator to the end  (public member function) [edit]

rbegincrbegin(C++11) | returns a reverse iterator to the beginning  (public member function) [edit]

rendcrend(C++11) | returns a reverse iterator to the end  (public member function) [edit]

Capacity

empty | checks whether the string is empty  (public member function) [edit]

sizelength | returns the number of characters  (public member function) [edit]

max_size | returns the maximum number of characters  (public member function) [edit]

reserve | reserves storage  (public member function) [edit]

capacity | returns the number of characters that can be held in currently allocated storage  (public member function) [edit]

shrink_to_fit(DR*) | reduces memory usage by freeing unused memory  (public member function) [edit]

Modifiers

clear | clears the contents  (public member function) [edit]

insert | inserts characters  (public member function) [edit]

insert_range(C++23) | inserts a range of characters  (public member function) [edit]

erase | removes characters  (public member function) [edit]

push_back | appends a character to the end  (public member function) [edit]

pop_back(DR*) | removes the last character  (public member function) [edit]

append | appends characters to the end  (public member function) [edit]

append_range(C++23) | appends a range of characters to the end  (public member function) [edit]

operator+= | appends characters to the end  (public member function) [edit]

replace | replaces specified portion of a string  (public member function) [edit]

replace_with_range(C++23) | replaces specified portion of a string with a range of characters  (public member function) [edit]

copy | copies characters  (public member function) [edit]

resize | changes the number of characters stored  (public member function) [edit]

resize_and_overwrite(C++23) | changes the number of characters stored and possibly overwrites indeterminate contents via user-provided operation  (public member function) [edit]

swap | swaps the contents  (public member function) [edit]

Search

find | finds the first occurrence of the given substring  (public member function) [edit]

rfind | find the last occurrence of a substring  (public member function) [edit]

find_first_of | find first occurrence of characters  (public member function) [edit]

find_first_not_of | find first absence of characters  (public member function) [edit]

find_last_of | find last occurrence of characters  (public member function) [edit]

find_last_not_of | find last absence of characters  (public member function) [edit]

Operations

compare | compares two strings  (public member function) [edit]

starts_with(C++20) | checks if the string starts with the given prefix  (public member function) [edit]

ends_with(C++20) | checks if the string ends with the given suffix  (public member function) [edit]

contains(C++23) | checks if the string contains the given substring or character  (public member function) [edit]

substr | returns a substring  (public member function) [edit]

subview(C++26) | returns a sub-view  (public member function) [edit]

### Non-member functions

operator+ | concatenates two strings, a string and a char, or a string and string_view  (function template) [edit]

operator==operator!=operator<operator>operator<=operator>=operator<=>(removed in C++20)(removed in C++20)(removed in C++20)(removed in C++20)(removed in C++20)(C++20) | lexicographically compares two strings  (function template) [edit]

std::swap(std::basic_string) | overloads the std::swap algorithm  (function template) [edit]

erase(std::basic_string)erase_if(std::basic_string)(C++20)(C++20) | erases all elements satisfying specific criteria  (function template) [edit]

Input/output

operator<<operator>> | performs stream input and output on strings  (function template) [edit]

getline | read data from an I/O stream into a string  (function template) [edit]

Numeric conversions

stoistolstoll(C++11)(C++11)(C++11) | converts a string to a signed integer  (function) [edit]

stoulstoull(C++11)(C++11) | converts a string to an unsigned integer  (function) [edit]

stofstodstold(C++11)(C++11)(C++11) | converts a string to a floating point value  (function) [edit]

to_string(C++11) | converts an integral or floating-point value to string  (function) [edit]

to_wstring(C++11) | converts an integral or floating-point value to wstring  (function) [edit]

### Literals

Defined in inline namespace std::literals::string_literals

operator""s(C++14) | converts a character array literal to basic_string  (function) [edit]

### Helper classes

std::hash<std::basic_string>(C++11) | hash support for strings  (class template specialization) [edit]

### Deduction guides (since C++17)

### Notes

Although it is required that customized construct or destroy is used when constructing or destroying elements of std::basic_string until C++23, all implementations only used the default mechanism. The requirement is corrected by P1072R10 to match existing practice.

Feature-test macro | Value | Std | Feature

__cpp_lib_string_udls | 201304L | (C++14) | User-defined literals for string types

__cpp_lib_starts_ends_with | 201711L | (C++20) | starts_with, ends_with

__cpp_lib_constexpr_string | 201907L | (C++20) | Constexpr for std::basic_string

__cpp_lib_char8_t | 201907L | (C++20) | std::u8string

__cpp_lib_erase_if | 202002L | (C++20) | erase, erase_if

__cpp_lib_string_contains | 202011L | (C++23) | contains

__cpp_lib_string_resize_and_overwrite | 202110L | (C++23) | resize_and_overwrite

__cpp_lib_containers_ranges | 202202L | (C++23) | Member functions for construction, insertion, and replacement that accept container compatible range

### Example

```
#include <iostream>
#include <string>

int main()
{
    using namespace std::literals;
    
    // Creating a string from const char*
    std::string str1 = "hello";
    
    // Creating a string using string literal
    auto str2 = "world"s;
    
    // Concatenating strings
    std::string str3 = str1 + " " + str2;
    
    // Print out the result
    std::cout << str3 << '\n';
    
    std::string::size_type pos = str3.find(" ");
    str1 = str3.substr(pos + 1); // the part after the space
    str2 = str3.substr(0, pos);  // the part till the space
    
    std::cout << str1 << ' ' << str2 << '\n';
    
    // Accessing an element using subscript operator[]
    std::cout << str1[0] << '\n';
    str1[0] = 'W';
    std::cout << str1 << '\n';
}
```

Output:

```
hello world
world hello
w
World
```

### Defect reports

The following behavior-changing defect reports were applied retroactively to previously published C++ standards.

DR | Applied to | Behavior as published | Correct behavior

LWG 530 | C++98 | contiguity of the storage for elements of basic_stringwas accidently made not required by LWG259 | required again

LWG 2861 | C++98 | value_type was Traits::char_type | changed to CharT

LWG 2994(P1148R0) | C++98 | the behavior is undefined if any of Traits::char_type[1]and Allocator::char_type is different from CharT | the program isill-formed in this case

- ↑ The Traits::char_type case is fixed in P1148R0.

### See also

basic_string_view(C++17) | read-only string view  (class template) [edit]

### External links

C++ string handling
