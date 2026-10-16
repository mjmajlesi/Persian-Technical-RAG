Source: https://en.cppreference.com/w/cpp/container/vector
Retrieved: 2026-10-16
License: CC-BY-SA (cppreference.com)

# std::vector - cppreference.com

# std::vector

Defined in header <vector>

```
template<
    class T,
    class Allocator = std::allocator<T>
> class vector;
```

(1)

```
namespace pmr {
    template< class T >
    using vector = std::vector<T, std::pmr::polymorphic_allocator<T>>;
}
```

(2) | (since C++17)

The elements are stored contiguously, which means that elements can be accessed not only through iterators, but also using offsets to regular pointers to elements. This means that a pointer to an element of a vector may be passed to any function that expects a pointer to an element of an array.

The storage of the vector is handled automatically, being expanded as needed. Vectors usually occupy more space than static arrays, because more memory is allocated to handle future growth. This way a vector does not need to reallocate each time an element is inserted, but only when the additional memory is exhausted. The total amount of allocated memory can be queried using capacity() function. Extra memory can be returned to the system via a call to shrink_to_fit()[1].

Reallocations are usually costly operations in terms of performance. The reserve() function can be used to eliminate reallocations if the number of elements is known beforehand.

The complexity (efficiency) of common operations on vectors is as follows:

- Random access - constant 𝓞(1).

- Insertion or removal of elements at the end - amortized constant 𝓞(1).

- Insertion or removal of elements - linear in the distance to the end of the vector 𝓞(n).

std::vector (for T other than bool) meets the requirements of Container, AllocatorAwareContainer(since C++11), SequenceContainer, ContiguousContainer(since C++17) and ReversibleContainer.

However, defining a constexpr std::vector variable is generally an error, because constant evaluation requires any dynamically allocated storage to be released in the same evaluation, which is usually not the case with std::vector's initializer.

All member functions of std::vector are constexpr: it is possible to create and use std::vector objects in the evaluation of a constant expression. | (since C++20)

- ↑ In libstdc++, shrink_to_fit() is not available in C++98 mode.

This section is incompleteReason: Add bits from P2846 [vector.cons]

### Template parameters

The type of the elements. | T must meet the requirements of CopyAssignable and CopyConstructible. | (until C++11)

The requirements that are imposed on the elements depend on the actual operations performed on the container. Generally, it is required that element type is a complete type and meets the requirements of Erasable, but many member functions impose stricter requirements. | (since C++11)(until C++17)

The requirements that are imposed on the elements depend on the actual operations performed on the container. Generally, it is required that element type meets the requirements of Erasable, but many member functions impose stricter requirements. This container (but not its members) can be instantiated with an incomplete element type if the allocator satisfies the allocator completeness requirements.

(since C++17)

Allocator | - | An allocator that is used to acquire/release memory and to construct/destroy the elements in that memory. The type must meet the requirements of Allocator. The behavior is undefined(until C++20)The program is ill-formed(since C++20) if Allocator::value_type is not the same as T.[edit]

### Specializations

The standard library provides a specialization of std::vector for the type bool, which may be optimized for space efficiency.

vector<bool> | space-efficient dynamic bitset  (class template specialization) [edit]

### Iterator invalidation

Operations | Invalidated

All read only operations | Never.

swap, std::swap | end()

clear, operator=, assign | Always.

reserve, shrink_to_fit | If the vector changed capacity, all of them. If not, none.

erase | Erased elements and all elements after them (including end()).

push_back, emplace_back | If the vector changed capacity, all of them. If not, only end().

insert, emplace | If the vector changed capacity, all of them.If not, only those at or after the insertion point (including end()).

resize | If the vector changed capacity, all of them. If not, only end() and any elements erased.

pop_back | The element erased and end().

### Member types

Member type | Definition

value_type | T[edit]

allocator_type | Allocator[edit]

size_type | unsigned integer type (usually std::size_t)[edit]

difference_type | signed integer type (usually std::ptrdiff_t)[edit]

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

### Member functions

(constructor) | constructs the vector  (public member function) [edit]

(destructor) | destructs the vector  (public member function) [edit]

operator= | assigns values to the container  (public member function) [edit]

assign | assigns values to the container  (public member function) [edit]

assign_range(C++23) | assigns a range of values to the container  (public member function) [edit]

get_allocator | returns the associated allocator  (public member function) [edit]

Element access

at | access specified element with bounds checking  (public member function) [edit]

operator[] | access specified element  (public member function) [edit]

front | access the first element  (public member function) [edit]

back | access the last element  (public member function) [edit]

data | direct access to the underlying contiguous storage  (public member function) [edit]

Iterators

begincbegin(C++11) | returns an iterator to the beginning  (public member function) [edit]

endcend(C++11) | returns an iterator to the end  (public member function) [edit]

rbegincrbegin(C++11) | returns a reverse iterator to the beginning  (public member function) [edit]

rendcrend(C++11) | returns a reverse iterator to the end  (public member function) [edit]

Capacity

empty | checks whether the container is empty  (public member function) [edit]

size | returns the number of elements  (public member function) [edit]

max_size | returns the maximum possible number of elements  (public member function) [edit]

reserve | reserves storage  (public member function) [edit]

capacity | returns the number of elements that can be held in currently allocated storage  (public member function) [edit]

shrink_to_fit(DR*) | reduces memory usage by freeing unused memory  (public member function) [edit]

Modifiers

clear | clears the contents  (public member function) [edit]

insert | inserts elements  (public member function) [edit]

insert_range(C++23) | inserts a range of elements  (public member function) [edit]

emplace(C++11) | constructs element in-place  (public member function) [edit]

erase | erases elements  (public member function) [edit]

push_back | adds an element to the end  (public member function) [edit]

emplace_back(C++11) | constructs an element in-place at the end  (public member function) [edit]

append_range(C++23) | adds a range of elements to the end  (public member function) [edit]

pop_back | removes the last element  (public member function) [edit]

resize | changes the number of elements stored  (public member function) [edit]

swap | swaps the contents  (public member function) [edit]

### Non-member functions

operator==operator!=operator<operator<=operator>operator>=operator<=>(removed in C++20)(removed in C++20)(removed in C++20)(removed in C++20)(removed in C++20)(C++20) | lexicographically compares the values of two vectors  (function template) [edit]

std::swap(std::vector) | overloads the std::swap algorithm  (function template) [edit]

erase(std::vector)erase_if(std::vector)(C++20)(C++20) | erases all elements satisfying specific criteria  (function template) [edit]

### Deduction guides

(since C++17)

### Notes

Feature-test macro | Value | Std | Feature

__cpp_lib_containers_ranges | 202202L | (C++23) | Ranges construction and insertion for containers

__cpp_lib_erase_if | 202002L | (C++20) | Consistent container erasure

__cpp_lib_incomplete_container_elements | 201505L | (C++17) | Minimal incomplete type support

### Example

```
#include <iostream>
#include <vector>

int main()
{
    // Create a vector containing integers
    std::vector<int> v = {8, 4, 5, 9};
 
    // Add two more integers to vector
    v.push_back(6);
    v.push_back(9);
    
    // Overwrite element at position 2
    v[2] = -1;
 
    // Print out the vector
    for (int n : v)
        std::cout << n << ' ';
    std::cout << '\n';
}
```

Output:

```
8 4 -1 9 6 9
```

### Defect reports

The following behavior-changing defect reports were applied retroactively to previously published C++ standards.

DR | Applied to | Behavior as published | Correct behavior

LWG 69 | C++98 | contiguity of the storage for elements of vector was not required | required

LWG 230 | C++98 | T was not required to be CopyConstructible(an element of type T might not be able to be constructed) | T is also required tobe CopyConstructible

LWG 464 | C++98 | access to the underlying storage of an empty vector resulted in UB | data function provided

### See also

inplace_vector(C++26) | resizable, fixed capacity, inplace contiguous array  (class template) [edit]

array(C++11) | fixed-sized inplace contiguous array  (class template) [edit]

deque | double-ended queue  (class template) [edit]
