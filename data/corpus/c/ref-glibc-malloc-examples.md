Source: https://sourceware.org/glibc/manual/latest/html_node/Malloc-Examples.html
Retrieved: 2026-09-23
License: GFDL (GNU C Library manual)

# Malloc Examples (The GNU C Library)

#### 3.2.3.2 Examples of malloc ¶

If no more space is available, malloc returns a null pointer. You should check the value of every call to malloc. It is useful to write a subroutine that calls malloc and reports an error if the value is a null pointer, returning only if the value is non-null. This function is conventionally called xmalloc. Here it is:

```
void *
xmalloc (size_t size)
{
  void *p = malloc (size);
  if (p == NULL)
    fatal ("virtual memory exhausted");
  return p;
}
```

Here is a real example of using malloc (by way of xmalloc). The function savestring will copy a sequence of characters into a newly allocated null-terminated string:

```
char *
savestring (const char *ptr, size_t len)
{
  char *p = xmalloc (len + 1);
  p[len] = '\0';
  return memcpy (p, ptr, len);
}
```

In the current release of the GNU C Library, the block that malloc gives you is aligned so that its address is a multiple of alignof (max_align_t), so that it can hold object types with any fundamental alignment and without stricter alignment specifiers. Only rarely is any higher boundary (such as a page boundary) necessary; for those cases, use aligned_alloc or posix_memalign (see Allocating Aligned Memory Blocks). Future releases of the GNU C Library may relax alignment for small allocations, so long as any object with fundamental alignment that fits in the small allocation will be properly aligned. For example, a future malloc (1) might return a pointer with odd alignment.

Note that the memory located after the end of the block is likely to be in use for something else; perhaps a block already allocated by another call to malloc. If you attempt to treat the block as longer than you asked for it to be, you are liable to destroy the data that malloc uses to keep track of its blocks, or you may destroy the contents of another block. If you have already allocated a block and discover you want it to be bigger, use realloc (see Changing the Size of a Block).
