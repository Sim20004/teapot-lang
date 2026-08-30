# TeapotLang language reference

This document describes the syntax currently recognised by the TeapotLang lexer and parser.

It is a **practical language reference**, not a description of a fully executable language. The compiler currently performs lexical analysis, parsing, and initial semantic analysis, but it does not generate executable code or provide a runtime.

For intended language features and design decisions that are not yet fully implemented, see the [language specification](language-specification.md).

## Implementation status

The following terms are used throughout this document:

| Status          | Meaning                                                                                                   |
| --------------- | --------------------------------------------------------------------------------------------------------- |
| **Implemented** | Supported by the relevant compiler stage and covered by the current implementation/tests where applicable |
| **Parsed**      | The parser constructs an AST representation                                                               |
| **Recognised**  | The lexer recognises the syntax, but a later stage may reject it                                          |
| **Represented** | An AST or compiler structure exists, but the syntax is not necessarily parseable                          |
| **Design**      | Part of the intended language model but not currently implemented                                         |

The current compiler does not produce executable output.

## Source files

TeapotLang source files use the `.tp` extension.

A source file must begin with one of the recognised memory directives:

```teapot
$MEM-GC

fc main()!void {
}
```

or:

```teapot
$MEM-MANUAL

fc main()!void {
}
```

The parser expects the memory directive before the rest of the program.

Only one memory directive is allowed. The lexer rejects unknown or duplicate directives.

The directive is stored on the resulting `Program` as `memory_mode`.

## Statements

Statements that are terminated by the parser use a period:

```teapot
val mui8 count = 10.
```

Block constructs use braces and do not require a period after the closing brace:

```teapot
if (count > 0) {
    count -= 1.
}
```

## Lexical syntax

### Whitespace

Whitespace is ignored.

CRLF line endings are normalised to LF before tokenisation.

### Comments

Single-line comments begin with `//`:

```teapot
// This is a comment
val mui8 value = 10.
```

A comment may end at the end of the file.

There is currently no block-comment syntax.

### Identifiers

Identifiers begin with an alphabetic character or `_` and may then contain alphabetic characters, digits, and `_`:

```teapot
val mui8 item_2 = 10.
```

Identifiers are case-sensitive.

Words recognised as keywords, type names, or Boolean literals are not tokenised as ordinary identifiers.

### Literals

The lexer recognises:

| Source  | Value           |
| ------- | --------------- |
| `42`    | Integer         |
| `3.14`  | Float           |
| `"tea"` | String          |
| `true`  | Boolean `True`  |
| `false` | Boolean `False` |

Numeric literals are decimal.

Exponent notation is not currently recognised.

Strings use double quotes and currently have no escape processing. Newlines may occur inside a string. An unterminated string produces `LexerError`.

There is no separate character-literal syntax.

## Memory directives

The lexer recognises exactly:

```text
$MEM-GC
$MEM-MANUAL
```

The selected directive is stored on the AST.

The compiler does not currently implement a garbage collector, manual memory allocator, or executable runtime. These directives currently represent the selected language mode only.

## Types

The lexer recognises the following built-in types.

### Base types

```text
void
str
char
bln
aint
dml
f32
f64
si8
si16
si32
si64
ui8
ui16
ui32
ui64
```

### Mutable types

```text
mstr
mchar
mbln
maint
mdml
mf32
mf64
msi8
msi16
msi32
msi64
mui8
mui16
mui32
mui64
```

### Constant types

```text
cstr
cchar
cbln
caint
cdml
cf32
cf64
csi8
csi16
csi32
csi64
cui8
cui16
cui32
cui64
```

The parser records mutability information for the mutable and constant forms.

Semantic enforcement of mutability and complete type checking are still under development.

## Arrays

Array types use `[]` after the element type:

```teapot
val csi32[] values = [1, 2, 3].

fc total(csi32[] values)!csi32 {
    exit 0.
}
```

Array literals are supported:

```teapot
val csi32[] values = [1, 2, 3].
```

Array indexing is not currently supported:

```teapot
values[0]
```

is not a valid parser-supported expression.

## References

`ref` may precede a variable type:

```teapot
val ref csi32 value = other.
```

The parser records reference information on the type representation.

Reference semantics, aliasing, lifetime rules, and pointer behaviour are not currently implemented.

## Variables

Variables are declared using `val`:

```teapot
val csi32 count = 0.
val cstr message.
val ref csi32 alias = count.
```

The initialiser is optional.

Assignments use an identifier followed by one of:

```text
=
+=
-=
*=
/=
```

For example:

```teapot
count += 1.
```

The semantic analyser does not yet perform complete type or mutability validation for assignments.

## Functions

Functions use the `fc` keyword:

```teapot
fc add(csi32 left, csi32 right)!csi32 {
    exit left + right.
}
```

The general form is:

```text
fc name(parameters)!return_type {
    statements
}
```

Parameters have a type and identifier:

```teapot
fc add(csi32 left, csi32 right)!csi32 {
}
```

Default parameter expressions are supported by the parser:

```teapot
fc add(csi32 left, csi32 right = 1)!csi32 {
}
```

The parser does not currently enforce all semantic rules for parameters, calls, defaults, or return paths.

A `main` function is not currently required by the parser and is not executed because there is no runtime.

## Return statements

`exit` returns an expression:

```teapot
exit value.
```

The expression must be followed by a period.

Complete return-type checking is not currently implemented.

## Visibility

`pub` may precede declarations supported by the parser, including:

* functions;
* structs;
* enums;
* errors; and
* operators.

There is currently no module system or access-control semantic pass.

## Structs

Structs use `sct`:

```teapot
sct Person {
    cstr name.
    csi32 age.
}
```

Struct fields are declared with a type, identifier, and period.

The parser also supports a limited struct-instantiation form:

```teapot
val Person person = Person("Alex", 15).
```

The compiler does not currently perform complete field-count or field-type validation.

## Enums

Enums use `enm`:

```teapot
enm Result {
    Pass.
    Fail.
}
```

Enum members are identifiers followed by periods.

Semantic handling of enums is still under development.

## Error declarations

Error declarations use `err`:

```teapot
err ValidationError {
    cstr message.
}
```

They are represented in the AST and parsed by the current parser.

Runtime error handling is not implemented.

## Operator declarations

Operator declarations use `operator`:

```teapot
operator +(csi32 left, csi32 right)!csi32 {
    exit left + right.
}
```

Operator declarations are parsed into `Operator` AST nodes.

Operator overload resolution and semantic validation are not currently implemented.

## Control flow

### `if`

Conditions use parentheses:

```teapot
if (value > 0) {
    exit true.
}
```

`elif` and `else` are supported:

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

### `while`

```teapot
while (condition) {
    // body
}
```

### `for`

The current parser supports:

```teapot
for (item : values) {
    // body
}
```

The exact semantic meaning of iteration is not yet implemented.

### `break` and `continue`

The lexer recognises `break` and `continue`, and corresponding AST dataclasses exist.

They are not currently accepted by the parser as statements.

They should therefore be considered unfinished language features rather than usable control-flow syntax.

## Expressions

The parser currently supports:

* integer literals;
* floating-point literals;
* string literals;
* Boolean literals;
* identifiers;
* parenthesised expressions;
* array literals;
* function calls;
* member access;
* casts;
* unary operators; and
* binary operators.

Examples:

```teapot
val csi32 result = (left + 2) * 3.
val csi32 converted = result >> csi32.
val csi32 field = object::value.
```

### Function calls

Function-call expressions use parentheses:

```teapot
add(1, 2)
```

Calls are represented by the parser as call-expression AST nodes.

Name resolution and call validation are part of ongoing semantic-analysis work.

### Member access

Member access uses `::`:

```teapot
object::field
```

The parser supports the syntax, but semantic member resolution is not currently implemented.

### Casts

Casts use `>>`:

```teapot
value >> csi32
```

The parser records the target type.

The semantic analyser does not yet enforce conversion rules.

## Operators and precedence

The parser uses the following precedence levels. Higher numbers bind more tightly:

| Level | Operators            |   |   |
| ----: | -------------------- | - | - |
|     6 | `**`                 |   |   |
|     5 | `%`, `/`, `*`        |   |   |
|     4 | `+`, `-`             |   |   |
|     3 | `<`, `<=`, `>`, `>=` |   |   |
|     2 | `==`, `~=`           |   |   |
|     1 | `&&`                 |   |   |
|     0 | `                    |   | ` |

Parentheses explicitly group expressions.

Assignment operators, function calls, `::`, and `>>` are handled by dedicated parser paths.

The parser constructs an AST and does not evaluate expressions.

## Semantic analysis

Semantic analysis currently builds symbol tables.

The first pass registers declarations including:

* variables;
* functions;
* structs.

Function declarations receive their own child scope.

The symbol table supports lookup through parent scopes, allowing nested scopes to resolve symbols declared in enclosing scopes.

Duplicate declarations in the same scope raise `SemanticError`.

For example, declaring the same name twice in one scope is rejected.

Shadowing in a child scope is supported by the current symbol-table implementation.

Full name resolution and type checking are not yet implemented.

## Diagnostics

Lexical errors use `LexerError` and include source position information.

Parser errors use `ParserError` and include the current parser/token context.

Semantic errors use `SemanticError`.

Compiler tracing can be enabled with:

```bash
teapot examples/hello.tp --trace
```

## Current boundaries

The following features are not currently complete:

* full type checking;
* identifier resolution;
* function-call validation;
* mutability enforcement;
* complete reference semantics;
* overload resolution;
* entry-point execution;
* runtime memory management;
* executable code generation;
* standard library;
* module/import handling;
* runtime error handling;
* `break` and `continue`;
* array indexing;
* several collection constructs.

Tokens and AST classes may exist for features that are not yet parser-supported. Their existence should not be interpreted as complete language support.
