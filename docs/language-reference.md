# TeapotLang language reference

This is the practical reference for the syntax currently recognised by the lexer and parser. It is not a description of a runnable language: semantic analysis is only a shallow AST traversal and the repository has no code generator. For intended rules and design-level features, see the [language specification](language-specification.md).

## Minimal source file

A source file must contain one of the recognised memory directives before parsing can begin:

```teapot
$MEM-GC

fc main()!void {
}
```

The parser consumes the directive as the first token. The lexer itself permits a directive after other tokens, but parsing then fails. Only one directive is allowed, and the lexer rejects unknown or duplicate directives.

Statements that are parsed as statements end with a period (`.`). Braces delimit blocks and do not require a period after the closing brace.

## Lexical syntax

### Whitespace and comments

Whitespace is ignored. CRLF line endings are normalised to LF. Single-line comments start with `//` and continue to the end of the line; a comment may also end the file.

Strings are enclosed in double quotes. They have no escape processing, and the lexer permits newlines inside a string. A string that reaches end of file without a closing quote raises `LexerError`.

### Identifiers

An identifier starts with an alphabetic character or `_`, then contains alphabetic characters, digits, or `_`:

```teapot
val csi32 item_2 = 10.
```

Words in the keyword or type tables are tokenised as those keywords or types rather than as identifiers. User-defined names are otherwise tokenised as identifiers.

### Literals

The lexer produces these literal token kinds:

| Source form | Result |
| --- | --- |
| `42` | Integer value |
| `3.14` | Floating-point value |
| `"tea"` | String value |
| `true`, `false` | Boolean value (`True` or `False`) |

Numbers are decimal integers or decimal floating-point values. Exponent notation is not recognised. A second decimal point in one number raises `LexerError`. There is no separate character-literal form; `char`, `mchar`, and `cchar` are type names only.

### Directives

The lexer recognises exactly:

```text
$MEM-GC
$MEM-MANUAL
```

The selected directive is stored on the parsed `Program` as `memory_mode`. The repository does not implement garbage collection or manual freeing beyond recording this value.

## Types

The lexer recognises these type names:

| Family | Names |
| --- | --- |
| Base types | `void`, `str`, `char`, `bln`, `aint`, `dml`, `f32`, `f64`, `si8`, `si16`, `si32`, `si64`, `ui8`, `ui16`, `ui32`, `ui64` |
| Mutable forms | `mstr`, `mchar`, `mbln`, `maint`, `mdml`, `mf32`, `mf64`, `msi8`, `msi16`, `msi32`, `msi64`, `mui8`, `mui16`, `mui32`, `mui64` |
| Constant forms | `cstr`, `cchar`, `cbln`, `caint`, `cdml`, `cf32`, `cf64`, `csi8`, `csi16`, `csi32`, `csi64`, `cui8`, `cui16`, `cui32`, `cui64` |

The parser records mutability for the prefixed forms and for `void`. It does not perform type checking or enforce mutability. A user-defined type name is tokenised as an identifier and is accepted in some declaration positions.

An array type is written with `[]` after a recognised element type in variable and function-parameter declarations:

```teapot
val csi32[] values = [1, 2, 3].
fc total(csi32[] values)!csi32 {
    exit 0.
}
```

`ref` can precede a variable type and is recorded on the AST type node:

```teapot
val ref csi32 value = other.
```

This is representation only; no reference semantics are implemented.

## Declarations

### Variables

Use `val`, followed by a built-in type or an identifier naming a user-defined type, then a variable name. The initialiser is optional; an omitted value is represented in the AST as a `null` Python value.

```teapot
val csi32 count = 0.
val cstr message.
val ref csi32 alias = count.
```

The parser recognises assignment operators `=`, `+=`, `-=`, `*=`, and `/=` on identifier-led assignment statements:

```teapot
count += 1.
```

The parser does not validate that a target exists, is mutable, or has a compatible type.

### Functions

Function declarations use `fc`, a name, parentheses, `!`, a return type, and a block. Parameters require lexer-recognised type tokens and an identifier. Default arguments are expressions after `=`.

```teapot
fc add(csi32 left, csi32 right = 1)!csi32 {
    exit left + right.
}
```

A return type may be a recognised type or an identifier. The parser does not require a `main` function and does not execute one.

`exit` parses one expression followed by a period:

```teapot
exit left + right.
```

### Visibility

`pub` may precede a function, struct, enum, error, or operator declaration. The parser rejects `pub` on other parsed statement kinds. No module boundary or access checking is implemented.

### Structs

Struct declarations contain recognised mutable or constant type names, field names, and periods:

```teapot
sct Person {
    cstr name.
    csi32 age.
}
```

The parser also recognises the following narrow instantiation form:

```teapot
val Person person = Person("Alex", 15).
```

Instantiation arguments are limited to integer, float, Boolean, string, or identifier tokens. The parser does not check field counts or types.

### Enums and errors

Enum members are identifiers followed by periods:

```teapot
enm Result {
    Pass.
    Fail.
}
```

Error declarations contain typed fields in the same shape as struct fields:

```teapot
err ValidationError {
    cstr message.
}
```

### Operators

The parser recognises operator declarations with an operator symbol or identifier, at least one argument, `!`, a return type, and a block:

```teapot
operator +(csi32 left, csi32 right)!csi32 {
    exit left + right.
}
```

The AST records these as `Operator` nodes. No overload resolution or operator type checking is implemented.

## Statements and control flow

The parser dispatch table currently constructs these statement nodes:

| Syntax | AST node |
| --- | --- |
| `val ...` | `DeclareVariable` |
| `fc ...` | `Function` |
| `sct ...` | `Struct` |
| `enm ...` | `Enum` |
| `err ...` | `Error` |
| `operator ...` | `Operator` |
| `exit ...` | `Return` |
| `if (...) { ... }` | `If` |
| `while (...) { ... }` | `While` |
| `for (name : expression) { ... }` | `For` |
| identifier assignment | `Assignment` |

Conditions require parentheses. `if` supports zero or more `elif` branches and an optional `else` block:

```teapot
if (value > 0) {
    exit true.
}
elif (value == 0) {
    exit false.
}
else {
    exit false.
}
```

Loops use these forms:

```teapot
while (condition) {
}

for (item : values) {
}
```

Although `break`, `continue`, `do`, and `fail` are tokenised and have AST dataclasses, they are not in the parser statement dispatch table and are rejected as statements.

## Expressions

Expressions may contain:

- integer, float, string, and Boolean literals;
- identifiers;
- parenthesised expressions;
- array literals such as `[1, 2, 3]`;
- function-call postfixes such as `add(1, 2)`;
- member access using `::`, such as `object::field`;
- casts using `>>`, such as `value >> csi32`;
- unary `~` and unary negation of numeric literals; and
- binary operators listed below.

```teapot
val csi32 result = (left + 2) * 3.
val csi32 converted = result >> csi32.
val csi32 field = object::value.
```

Array indexing is not handled by the parser, so an expression such as `values[0]` is not currently valid.

### Operators and precedence

The parser assigns the following precedence values. Higher values bind more tightly:

| Precedence | Operators |
| ---: | --- |
| 6 | `**` |
| 5 | `%`, `/`, `*` |
| 4 | `+`, `-` |
| 3 | `<`, `<=`, `>`, `>=` |
| 2 | `==`, `~=` |
| 1 | `&&` |
| 0 | `||` |

Assignment operators, `::`, `>>`, and function calls are handled by dedicated parser paths rather than this binary precedence table. The parser builds a left-associated binary expression for operators at the same precedence. It does not evaluate expressions.

## Errors and current boundaries

`LexerError` includes a line and column. `ParserError` includes the current token and parser position. Both error classes also print a diagnostic through the project debug helper.

The current semantic analyser only iterates over top-level `Program.statements`; it does not resolve names, check types, enforce scope or mutability, validate control flow, or produce semantic errors. There is no runtime or code-generation stage. Features present in token tables or AST dataclasses but absent from parser dispatch should be treated as design or implementation scaffolding, not as usable language features.
