Source: https://sourceware.org/glibc/manual/latest/html_node/Formatted-Output.html
Retrieved: 2026-09-23
License: GFDL (GNU C Library manual)

# Formatted Output (The GNU C Library)

### 12.12 Formatted Output ¶

The functions described in this section (printf and related functions) provide a convenient way to perform formatted output. You call printf with a format string or template string that specifies how to format the values of the remaining arguments.

Unless your program is a filter that specifically performs line- or character-oriented processing, using printf or one of the other related functions described in this section is usually the easiest and most concise way to perform output. These functions are especially useful for printing error messages, tables of data, and the like.

- Formatted Output Basics

- Output Conversion Syntax

- Table of Output Conversions

- Integer Conversions

- Floating-Point Conversions

- Other Output Conversions

- Formatted Output Functions

- Dynamically Allocating Formatted Output

- Variable Arguments Output Functions

- Parsing a Template String

- Example of Parsing a Template String
