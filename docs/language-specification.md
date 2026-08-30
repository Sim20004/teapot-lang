# TeapotLang language specification

This document describes the intended design of TeapotLang.

It is separate from the [language reference](language-reference.md), which documents syntax currently supported by the compiler.

The implementation is evolving. A feature described here is not necessarily available in the current compiler.

## 1. Language overview

TeapotLang is intended to be a statically typed, compiled, general-purpose programming language.

The language is designed around:

* explicit type names;
* mutable and constant types;
* user-defined data structures;
* functions;
* structured control flow;
* references;
* arrays and collections;
* configurable memory-management modes;
* user-defined operators;
* visibility;
* error handling; and
* eventual compilation to executable code.

The current compiler is written in Python and is being developed incrementally.

## 2. Compiler model

The intended compiler architecture is:

```text
Source
  |
  v
Lexical analysis
  |
  v
Tokens
  |
  v
Parsing
  |
  v
AST
  |
  v
Semantic analysis
  |
  v
Intermediate representation / lowering
  |
  v
Code generation
  |
  v
Executable
```

The current repository implements the lexer, parser, AST, and an initial semantic-analysis phase.

Code generation, runtime execution, and a standard library are not yet implemented.

## 3. Source files

TeapotLang source files use the `.tp` extension.

A program is intended to have a `main` entry point:

```teapot
fc main()!void {
}
```

### Entry point

**Design:** compilation of a complete executable program should identify `main` as the program entry point.

The current compiler does not require or execute `main`.

Entry-point validation remains a semantic-analysis task.

## 4. Memory-management modes

A source file selects its intended memory-management mode with one directive:

```teapot
$MEM-GC
```

or:

```teapot
$MEM-MANUAL
```

The directive applies to the program.

### Garbage collection

`$MEM-GC` is intended to select automatic memory management.

### Manual memory management

`$MEM-MANUAL` is intended to select explicit memory management.

The current compiler records the selected mode but does not implement either runtime memory-management model.

## 5. Types

TeapotLang uses explicit type names.

The language contains primitive types, mutable forms, constant forms, references, arrays, and user-defined types.

### Primitive types

The current built-in type vocabulary includes:

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

Types prefixed with `m` represent mutable values:

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

Types prefixed with `c` represent constant values:

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

The exact rules governing conversions between mutable, constant, and base types are still being established.

## 6. Mutability

The language distinguishes mutable and constant type forms.

Conceptually:

```text
mT
```

represents a mutable value of type `T`, while:

```text
cT
```

represents a constant value of type `T`.

The intended semantics are that constant values cannot be modified after their valid initialisation.

The current semantic analyser records type information but does not yet enforce the complete mutability model.

## 7. Variables

Variables use `val`:

```teapot
val mui8 count = 10.
```

An initialiser may be omitted:

```teapot
val cstr message.
```

The intended semantic rules include:

* the declared type must be valid;
* the variable name must be valid in its scope;
* an initialiser must be compatible with the declared type;
* constant values must obey their immutability rules; and
* references must satisfy reference rules.

Only declaration registration and duplicate-name detection are currently implemented.

## 8. References

The `ref` modifier introduces reference types:

```teapot
val ref csi32 value = other.
```

The intended language model includes references to existing values rather than independent copies.

The following areas remain to be formally specified and implemented:

* aliasing;
* lifetime;
* nullability;
* reference assignment;
* ownership;
* invalid references;
* interaction with garbage collection; and
* interaction with manual memory management.

## 9. Arrays

Arrays are parameterised by an element type:

```text
T[]
```

Example:

```teapot
val csi32[] values = [1, 2, 3].
```

The intended language should provide a coherent model for:

* array creation;
* element access;
* element assignment;
* array length;
* iteration;
* element type checking; and
* memory management.

The current parser supports array types and array literals but not array indexing.

## 10. User-defined types

TeapotLang supports user-defined type declarations.

### Structs

Structs contain named fields:

```teapot
sct Person {
    cstr name.
    csi32 age.
}
```

The intended semantics include:

* named field access;
* construction;
* field type checking;
* field visibility;
* storage;
* and interaction with references and memory management.

The current compiler parses and registers struct declarations but does not implement the complete semantic model.

### Enums

Enums define a finite set of named variants:

```teapot
enm Result {
    Pass.
    Fail.
}
```

The intended semantic model for enum values, matching, conversion, and storage remains under development.

### Errors

Error declarations define structured error types:

```teapot
err ValidationError {
    cstr message.
}
```

The intended runtime error model is not yet implemented.

## 11. Functions

Functions use `fc`:

```teapot
fc add(csi32 left, csi32 right)!csi32 {
    exit left + right.
}
```

A function consists of:

* a name;
* zero or more parameters;
* a return type;
* and a body.

Parameters have a declared type and name.

Default arguments may be specified:

```teapot
fc add(csi32 left, csi32 right = 1)!csi32 {
}
```

The intended semantic rules include:

* parameter name uniqueness;
* parameter type validity;
* default-argument validity;
* return-type correctness;
* call-argument compatibility;
* call arity;
* scope;
* and return-path analysis.

The current compiler registers function declarations and creates function scopes.

## 12. Function scope

Each function has a local scope.

Function parameters are intended to exist within the function's scope.

Nested blocks may eventually introduce additional scopes depending on the final language rules.

The current symbol-table implementation supports parent/child lookup and local shadowing.

The precise shadowing rules are still a language-design decision.

## 13. Return statements

Functions return values using `exit`:

```teapot
exit value.
```

The intended language should verify that the returned expression is compatible with the function's declared return type.

The current parser constructs return AST nodes, but complete return checking is not implemented.

## 14. Visibility

Declarations may be marked `pub`:

```teapot
pub fc public_function()!void {
}
```

The intended purpose is to expose declarations outside their defining module.

The module system and access-control rules are not yet implemented.

## 15. Modules

The language design includes module-related keywords such as:

```text
attach
as
```

The intended module system should eventually define:

* how modules are located;
* how files are imported;
* aliases;
* exported declarations;
* visibility;
* cyclic dependencies;
* and module initialisation.

The current compiler does not implement module resolution.

## 16. Operators

TeapotLang supports user-defined operator declarations in its syntax:

```teapot
operator +(csi32 left, csi32 right)!csi32 {
    exit left + right.
}
```

The intended language should define:

* which operators can be overloaded;
* operator precedence;
* associativity;
* valid parameter counts;
* overload resolution;
* ambiguity handling;
* and interaction with built-in operators.

The parser currently recognises operator declarations, but semantic overload resolution is not implemented.

## 17. Expressions

Expressions are intended to include:

* literals;
* identifiers;
* function calls;
* member access;
* casts;
* unary operators;
* binary operators;
* arrays;
* and eventually additional collection and reference operations.

The current parser supports a subset of these forms.

Semantic analysis is responsible for determining whether an expression is valid and what type it produces.

## 18. Operators and precedence

The current parser uses the following precedence levels:

| Level | Operators            |   |   |
| ----: | -------------------- | - | - |
|     6 | `**`                 |   |   |
|     5 | `%`, `/`, `*`        |   |   |
|     4 | `+`, `-`             |   |   |
|     3 | `<`, `<=`, `>`, `>=` |   |   |
|     2 | `==`, `~=`           |   |   |
|     1 | `&&`                 |   |   |
|     0 | `                    |   | ` |

The final language specification must establish associativity and evaluation semantics for every operator.

The parser currently constructs the corresponding expression tree but does not evaluate it.

## 19. Assignment

The language supports assignment operators:

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

The intended semantic rules should determine:

* whether the target exists;
* whether it is assignable;
* whether it is mutable;
* whether the value has a compatible type;
* and what compound-assignment operations mean for each type.

These checks are not fully implemented.

## 20. Conditional control flow

The language supports:

```teapot
if (condition) {
}
elif (other_condition) {
}
else {
}
```

Conditions are intended to evaluate to a Boolean-compatible value.

The exact condition typing rules remain to be implemented.

## 21. Loops

The language supports:

```teapot
while (condition) {
}
```

and:

```teapot
for (item : values) {
}
```

The final language design must define:

* iteration semantics;
* iterator behaviour;
* loop-variable scope;
* mutation during iteration;
* and the behaviour of `break` and `continue`.

The current parser does not yet accept `break` or `continue` as statements.

## 22. Error handling

The language design includes `do` and `fail`.

These keywords are currently recognised by the lexer and corresponding AST dataclasses exist, but the parser does not currently accept the constructs as normal statements.

The final error-handling model should define:

* how errors are created;
* how errors propagate;
* how they are caught;
* whether functions can declare errors;
* how errors interact with return values;
* and how errors interact with resource management.

## 23. Memory and resource management

The memory-management directives are intended to control how values are managed at runtime.

The final specification should define:

### GC mode

* allocation;
* reachability;
* collection;
* finalisation;
* references;
* and lifetime.

### Manual mode

* allocation;
* explicit release;
* invalid-use behaviour;
* ownership;
* and lifetime.

The `free` keyword exists in the lexical vocabulary, but the current parser does not implement manual freeing.

## 24. Semantic analysis

Semantic analysis is the stage responsible for determining whether a syntactically valid program is meaningful.

The intended responsibilities include:

* declaration checking;
* name resolution;
* scope construction;
* type resolution;
* type checking;
* mutability checking;
* function-call validation;
* return checking;
* operator resolution;
* member resolution;
* control-flow validation;
* entry-point validation;
* and other language invariants.

The current implementation has begun this process with symbol-table construction.

The current first pass:

```text
Program
  |
  +-- variable declarations -> variable symbols
  |
  +-- function declarations -> function symbols + function scopes
  |
  +-- struct declarations -> struct symbols
```

Duplicate declarations in the same scope currently produce `SemanticError`.

Full name resolution and type checking remain future work.

## 25. Diagnostics

Compiler errors should eventually provide enough source information for a programmer to locate and understand the problem.

The current lexer reports line and column information.

Parser errors retain token/parser context.

Semantic errors retain the relevant semantic node.

A future diagnostic system should standardise formatting across all compiler stages.

## 26. Code generation

The compiler is intended to eventually transform semantically valid TeapotLang programs into executable output.

The repository currently contains no code-generation backend.

The target architecture and output format have not yet been finalised.

## 27. Runtime

The intended runtime will eventually provide whatever functionality is required by generated programs, including memory management and standard-library facilities.

There is currently no TeapotLang runtime.

## 28. Standard library

A standard library is planned but not currently implemented.

The eventual standard library may provide facilities such as:

* input/output;
* strings;
* collections;
* filesystem access;
* error handling;
* and other common functionality.

Its API is intentionally not considered stable at this stage.

## 29. Current implementation status

The current repository can be summarised as follows:

| Component                       | Current state                                   |
| ------------------------------- | ----------------------------------------------- |
| Lexer                           | Implemented                                     |
| Token tables                    | Implemented                                     |
| Parser                          | Substantial partial implementation              |
| AST                             | Implemented, with some future/scaffolding nodes |
| Symbol tables                   | Implemented                                     |
| Declaration collection          | Implemented for current supported declarations  |
| Nested symbol lookup            | Implemented                                     |
| Duplicate declaration detection | Implemented                                     |
| Function scopes                 | Implemented                                     |
| Name resolution                 | In progress                                     |
| Type checking                   | Not yet implemented                             |
| Mutability checking             | Not yet implemented                             |
| Complete semantic validation    | Not yet implemented                             |
| Code generation                 | Not implemented                                 |
| Runtime                         | Not implemented                                 |
| Standard library                | Not implemented                                 |
| Module system                   | Not implemented                                 |
| Complete error handling         | Not implemented                                 |

## 30. Design status

This specification deliberately contains areas that are not yet final.

When implementation exposes an ambiguity, the language design should be updated before treating the behaviour as a permanent language rule.

In particular, the following still require explicit design decisions:

* exact type-conversion rules;
* complete mutability semantics;
* shadowing rules;
* function default-argument semantics;
* function return-path requirements;
* array indexing and bounds behaviour;
* reference ownership and lifetime;
* error propagation;
* module resolution;
* operator overload rules;
* loop iteration semantics;
* memory-management semantics;
* executable target;
* runtime architecture;
* and standard-library API.

Until these are defined and implemented, they should be treated as evolving language design rather than stable guarantees.
