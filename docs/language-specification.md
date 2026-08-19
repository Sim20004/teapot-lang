# TeapotLang language specification

This document is the authoritative statement of the language design recorded by the repository. It describes intended meaning separately from current compiler support. The [language reference](language-reference.md) is the practical guide to syntax that the current lexer and parser recognise.

A feature marked **design** is part of the intended language model but is not established by the current compiler. A feature marked **parser** is constructed into the current AST. A feature marked **lexer** is tokenised but may be rejected by the parser. No feature is executable: the repository has no code-generation or runtime stage.

## 1. Overview and design goals

TeapotLang is intended to be a statically typed, compiled, general-purpose language with explicit type names, mutable and constant type forms, user-defined data structures, multiple memory-management modes, and structured control flow. The repository explores language design and compiler construction in Python.

The current implementation provides a lexer, a partial parser, AST dataclasses, and a shallow semantic-analysis traversal. Static typing, symbol resolution, runtime memory management, and executable compilation remain design requirements rather than implemented guarantees.

## 2. Source files and program structure

A Teapot source file has the `.tp` extension. The intended program entry point is:

```teapot
fc main()!void {
}
```

**Design:** a program starts at `main`. The current parser does not require, find, or execute an entry point.

A memory directive is required before parsing:

```teapot
$MEM-GC
```

or:

```teapot
$MEM-MANUAL
```

The current lexer allows a directive to be encountered after other tokens, but the parser requires the first token to be a valid directive. The lexer rejects unknown and duplicate directives.

The parser represents the complete file as a `Program` containing statements and the selected `memory_mode`.

## 3. Lexical structure

### 3.1 Encoding and line endings

The lexer accepts Python strings as source input and normalises CRLF (`\r\n`) to LF (`\n`). The existing documentation calls the source encoding UTF-8, but the repository does not perform an encoding declaration or byte-to-text decoding; callers provide text to `Lexer`.

### 3.2 Whitespace

Whitespace is skipped. Line and column tracking starts at line 1, column 1. Newlines increment the line and reset the column to 1.

### 3.3 Comments

The implemented comment form is a single-line comment beginning with `//`. It continues until newline or end of input. Comment markers inside a string are string contents.

**Design:** the previous specification mentioned block comments, but the current lexer has no block-comment implementation. Block comments are therefore unresolved design material, not current syntax.

### 3.4 Identifiers

The implemented identifier rule is:

```text
identifier ::= (letter | "_") (letter | digit | "_")*
```

Identifiers are case-sensitive. Keywords, type names, and Boolean literals are classified before ordinary identifiers. The lexer tests establish that leading underscores and digits after the first character are accepted.

### 3.5 Keywords

The lexer classifies these words as keywords:

| Area | Keywords |
| --- | --- |
| Modules and visibility | `attach`, `as`, `pub` |
| Functions | `fc`, `exit`, `operator` |
| Variables and memory | `val`, `ref`, `free`, `null` |
| Control flow | `if`, `elif`, `else`, `while`, `for`, `break`, `continue` |
| Errors | `do`, `fail`, `err` |
| Data structures | `sct`, `enm`, `list`, `map` |

Being in this table means a word receives a keyword token. It does not mean that a later parser or semantic stage supports the feature.

### 3.6 Types and literals

The lexer classifies the following as `TYPE` tokens:

```text
void str char bln aint dml f32 f64
si8 si16 si32 si64 ui8 ui16 ui32 ui64
mstr mchar mbln msi8 msi16 msi32 msi64
mui8 mui16 mui32 mui64 maint mf32 mf64 mdml
cstr cchar cbln csi8 csi16 csi32 csi64
cui8 cui16 cui32 cui64 caint cf32 cf64 cdml
```

The lexer produces these literal tokens:

| Source | Token value |
| --- | --- |
| decimal digits, such as `42` | Python `int` |
| decimal number, such as `3.14` | Python `float` |
| double-quoted text | Python `str` |
| `true` | Python `True` |
| `false` | Python `False` |

There is no escape processing and no separate character-literal syntax. Exponent notation is not handled. A second decimal point in one numeric token and an unterminated string produce `LexerError`.

### 3.7 Operators and punctuation

The lexer recognises these symbols:

| Category | Symbols |
| --- | --- |
| Arithmetic | `+`, `-`, `*`, `/`, `%`, `**` |
| Comparison | `==`, `~=`, `>`, `<`, `>=`, `<=` |
| Logical | `&&`, `||`, `~` |
| Assignment | `=`, `+=`, `-=`, `*=`, `/=` |
| Delimiters | `(`, `)`, `{`, `}`, `[`, `]`, `,`, `.` |
| Other punctuation | `|`, `:`, `::`, `!`, `>>` |

Two-character symbols are matched before their single-character prefixes. Invalid symbols produce a line-and-column lexer error.

## 4. Types

The intended type families are primitive numeric, Boolean, string, character, references, arrays, and user-defined structures and enumerations. The built-in names and mutable/constant prefixes are listed in the lexical section.

The parser stores a mutability flag for the `m...` and `c...` forms. It also stores whether a variable declaration was prefixed with `ref`. These fields are AST information only. The semantic analyser does not enforce type compatibility, constant assignment rules, scope, or reference validity.

**Design:** the specification describes `m` as mutable and `c` as constant, with `void` having no mutable or constant form. Runtime representation and conversion rules are not implemented.

Arrays use an element type followed by `[]` in parser-supported variable and parameter declarations:

```teapot
val csi32[] values = [1, 2, 3].
```

**Design:** lists, maps, and tuples are described by the existing specification, but they are not parser-supported constructs today.

## 5. Variables and declarations

The parser supports variable declarations beginning with `val`:

```text
variable-declaration ::= "val" ["ref"] type variable-name ["=" expression] "."
type                 ::= TYPE | identifier ["[" "]"]
```

Examples:

```teapot
val csi32 count = 0.
val cstr message.
val ref csi32 alias = count.
```

An omitted initialiser is represented as `Literal(None)` in the AST. The parser does not establish what value a runtime variable receives.

Assignments are identifier-led expressions followed by one of `=`, `+=`, `-=`, `*=`, or `/=`, a value expression, and a period. The parser does not check that the target exists, is mutable, or has a compatible type.

## 6. Expressions

The parser constructs expressions from:

- integer, float, string, and Boolean literals;
- identifiers;
- parenthesised expressions;
- array literals;
- function-call postfixes;
- `::` member access;
- `>>` casts;
- unary `~` and numeric negation of literals; and
- binary operators.

An informal grammar for the parser-supported primary and postfix forms is:

```text
primary       ::= literal | identifier | "(" expression ")" | array-literal
postfix       ::= primary { "(" [expression { "," expression }] ")"
                         | "::" identifier
                         | ">>" TYPE }
array-literal ::= "[" [expression { "," expression }] "]"
```

Array indexing is not included in the parser’s postfix handling. The AST contains `FunctionCall`, `Reference`, `ListLiteral`, and `MapLiteral` dataclasses, but the parser constructs `CallExpression`, not those placeholder nodes, and does not construct the other listed nodes.

## 7. Operators and precedence

The parser uses these precedence values, with larger values binding more tightly:

| Level | Operators |
| ---: | --- |
| 6 | `**` |
| 5 | `%`, `/`, `*` |
| 4 | `+`, `-` |
| 3 | `<`, `<=`, `>`, `>=` |
| 2 | `==`, `~=` |
| 1 | `&&` |
| 0 | `||` |

Parentheses explicitly group an expression. The parser’s precedence-climbing implementation creates binary AST nodes; no evaluation occurs. The specification’s intended associativity and runtime arithmetic behaviour cannot be verified from the repository.

`::` is parsed as repeated member access. `>>` is parsed as a cast to a lexer-recognised type. No type conversion rules are enforced.

## 8. Statements and control flow

The current parser statement dispatch table supports:

```text
statement ::= variable-declaration
            | function-declaration
            | struct-declaration
            | enum-declaration
            | error-declaration
            | operator-declaration
            | return-statement
            | if-statement
            | while-statement
            | for-statement
            | assignment
```

### 8.1 Functions and return

```text
function-declaration ::= ["pub"] "fc" identifier "("
                         [parameter { "," parameter }] ")"
                         "!" (TYPE | identifier) block
parameter            ::= TYPE ["[" "]"] identifier ["=" expression]
return-statement     ::= "exit" expression "."
block                ::= "{" { statement } "}"
```

Function parameters currently require `TYPE` tokens, although a return type may be a type token or an identifier. The parser does not check return paths, overload validity, call arity, or default-argument rules.

### 8.2 Conditional statements

`if` requires a parenthesised condition and a block. It may be followed by zero or more `elif` branches and one `else` branch:

```teapot
if (condition) {
}
elif (other_condition) {
}
else {
}
```

### 8.3 Loops

The parser supports:

```text
while-statement ::= "while" "(" expression ")" block
for-statement   ::= "for" "(" identifier ":" expression ")" block
```

`break` and `continue` are lexer keywords and AST dataclasses, but are not parser statements. They are therefore design or unfinished implementation, not usable control-flow syntax.

### 8.4 Error-handling blocks

`do` and `fail` are lexer keywords, and `Do` and `Fail` AST dataclasses exist. They are absent from the parser dispatch table. The error-handling syntax in the existing design specification is not currently parseable.

## 9. Visibility and data structures

`pub` is accepted before functions, structs, enums, errors, and operators. Other parsed statements reject it. The repository has no module resolver or access checker.

Structs, enums, errors, and operator declarations are parsed into corresponding AST dataclasses. Struct fields and error fields require recognised type tokens; enum members are identifiers followed by periods. Struct instantiation has a narrow parser path for literal or identifier arguments.

The lexer recognises `attach`, `as`, `list`, and `map`, and AST dataclasses exist for imports and collection literals. No parser dispatch handles those constructs. Their syntax and semantics remain design-level.

## 10. Memory and references

`$MEM-GC` and `$MEM-MANUAL` are recorded as the program memory mode. The repository contains no collector, allocator, manual-free operation, or runtime. `free` is tokenised but not parsed.

`ref` is accepted in variable declarations and stored on the AST type. The `Reference` AST dataclass is not constructed by the parser. Nullability, aliasing, pointer arithmetic, and lifetime rules are not established by the implementation.

## 11. Errors, diagnostics, and semantic rules

`LexerError` reports a message, line, and column. `ParserError` reports a message, token, and parser position. Both use the project debug print helper as well as raising an exception.

The semantic analyser currently iterates through `Program.statements` and, in trace mode, prints each top-level node class. It does not implement:

- name or symbol resolution;
- type checking or conversion;
- scope or shadowing rules;
- mutability checking;
- overload resolution;
- entry-point validation;
- control-flow validation; or
- runtime or compile-time execution.

The existing design text proposes static typing, scope rules, constant behaviour, automatic conversion, error handling, and memory-management semantics. Those proposals remain unverified until implementation and tests establish them.

## 12. Implementation status and unresolved decisions

The following distinctions are intentional:

| Area | Repository evidence | Status |
| --- | --- | --- |
| Lexing | `Lexer`, token tables, and 32 lexer tests | Implemented and tested |
| Parsing | `Parser` and statement handlers | Partially implemented; no parser tests |
| AST | Dataclasses in `teapot_ast.py` | Mixed: some nodes are constructed, others are placeholders |
| Semantic analysis | `semantic.py` top-level traversal | Minimal traversal only |
| Code generation | No module or runtime present | Not implemented |
| Entry point | Mentioned by design documents only | Not enforced or executed |
| Modules, lists, maps, errors at runtime | Tokens/AST/design text only | Not implemented |

The repository does not resolve whether the design examples are intended as parser fixtures, future syntax, or normative examples. It also does not resolve character-literal syntax, exact runtime values for omitted initialisers, conversion semantics, associativity requirements, or the intended packaging/CLI installation workflow.
