Source: https://docs.oracle.com/javase/tutorial/java/nutsandbolts/operators.html
Retrieved: 2026-10-16
License: Oracle tutorial (redistribution: see docs.oracle.com terms)

# Operators (The Java™ Tutorials > Learning the Java Language > Language Basics)

Now that you've learned how to declare and initialize variables, you probably want to know how to do something with them. Learning the operators of the Java programming language is a good place to start. Operators are special symbols that perform specific operations on one, two, or three operands, and then return a result.

As we explore the operators of the Java programming language, it may be helpful for you to know ahead of time which operators have the highest precedence. The operators in the following table are listed according to precedence order. The closer to the top of the table an operator appears, the higher its precedence. Operators with higher precedence are evaluated before operators with relatively lower precedence. Operators on the same line have equal precedence. When operators of equal precedence appear in the same expression, a rule must govern which is evaluated first. All binary operators except for the assignment operators are evaluated from left to right; assignment operators are evaluated right to left.

Operators | Precedence

postfix | expr++ expr--

unary | ++expr --expr +expr -expr ~ !

multiplicative | * / %

additive | + -

shift | << >> >>>

relational | < > <= >= instanceof

equality | == !=

bitwise AND | &

bitwise exclusive OR | ^

bitwise inclusive OR | |

logical AND | &&

logical OR | ||

ternary | ? :

assignment | = += -= *= /= %= &= ^= |= <<= >>= >>>=

In general-purpose programming, certain operators tend to appear more frequently than others; for example, the assignment operator "=" is far more common than the unsigned right shift operator ">>>". With that in mind, the following discussion focuses first on the operators that you're most likely to use on a regular basis, and ends focusing on those that are less common. Each discussion is accompanied by sample code that you can compile and run. Studying its output will help reinforce what you've just learned.
