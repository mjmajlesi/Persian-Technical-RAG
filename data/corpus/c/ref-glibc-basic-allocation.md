Source: https://sourceware.org/glibc/manual/latest/html_node/Basic-Allocation.html
Retrieved: 2026-09-23
License: GFDL (GNU C Library manual)

# Basic Allocation (The GNU C Library)

#### 3.2.3.1 Basic Memory Allocation ¶

To allocate a block of memory, call malloc. The prototype for this function is in stdlib.h.

**Function: void * malloc (size_t size) ¶**

Preliminary: | MT-Safe | AS-Unsafe lock | AC-Unsafe lock fd mem | See POSIX Safety Concepts.

This function returns a pointer to a newly allocated block size bytes long, or a null pointer (setting errno) if the block could not be allocated.

The contents of the block are undefined; you must initialize it yourself (or use calloc instead; see Allocating Cleared Space). Normally you would convert the value to a pointer to the kind of object that you want to store in the block. Here we show an example of doing so, and of initializing the space with zeros using the library function memset (see Copying Strings and Arrays):

```
struct foo *ptr = malloc (sizeof *ptr);
if (ptr == 0) abort ();
memset (ptr, 0, sizeof (struct foo));
```

You can store the result of malloc into any pointer variable without a cast, because ISO C automatically converts the type void * to another type of pointer when necessary. However, a cast is necessary if the type is needed but not specified by context.

Remember that when allocating space for a string, the argument to malloc must be one plus the length of the string. This is because a string is terminated with a null character that doesn’t count in the “length” of the string but does need space. For example:

```
char *ptr = malloc (length + 1);
```

See Representation of Strings, for more information about this.
