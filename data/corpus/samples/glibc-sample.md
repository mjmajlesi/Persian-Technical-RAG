# Input/Output on Streams — GNU C Library manual excerpt (development fixture only, not part of the frozen snapshot)

Source: https://www.gnu.org/software/libc/manual/ (excerpt for local development)

## Standard Streams

Every program inherits three open streams: standard input (`stdin`),
standard output (`stdout`), and standard error (`stderr`).

## Reading a Character

The function `getchar` reads the next character from standard input
and returns it as an `int`.

```c
int c = getchar();
```
