Source: https://sourceware.org/glibc/manual/latest/html_node/Standard-Streams.html
Retrieved: 2026-09-23
License: GFDL (GNU C Library manual)

# Standard Streams (The GNU C Library)

### 12.2 Standard Streams ¶

When the main function of your program is invoked, it already has three predefined streams open and available for use. These represent the “standard” input and output channels that have been established for the process.

These streams are declared in the header file stdio.h.

**Variable: FILE * stdin ¶**

The standard input stream, which is the normal source of input for the program.

**Variable: FILE * stdout ¶**

The standard output stream, which is used for normal output from the program.

**Variable: FILE * stderr ¶**

The standard error stream, which is used for error messages and diagnostics issued by the program.

On GNU systems, you can specify what files or processes correspond to these streams using the pipe and redirection facilities provided by the shell. (The primitives shells use to implement these facilities are described in File System Interface.) Most other operating systems provide similar mechanisms, but the details of how to use them can vary.

In the GNU C Library, stdin, stdout, and stderr are normal variables which you can set just like any others. For example, to redirect the standard output to a file, you could do:

```
fclose (stdout);
stdout = fopen ("standard-output-file", "w");
```

Note however, that in other systems stdin, stdout, and stderr are macros that you cannot assign to in the normal way. But you can use freopen to get the effect of closing one and reopening it. See Opening Streams.

The three streams stdin, stdout, and stderr are not unoriented at program start (see Streams in Internationalized Applications).
