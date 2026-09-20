# malloc — cppreference C excerpt (development fixture only, not part of the frozen snapshot)

Source: https://en.cppreference.com/w/c/memory/malloc (excerpt for local development)

## Description

Allocates `size` bytes of uninitialized storage.

## Parameters

- `size` — number of bytes to allocate.

## Return value

On success, returns a pointer to the beginning of newly allocated memory.
On failure, returns a null pointer.

```c
int *p = (int*)malloc(10 * sizeof(int));
```
