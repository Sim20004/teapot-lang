# TeapotLang documentation

This directory contains documentation for both the current TeapotLang compiler and the language design.

## Where to start

### New to TeapotLang?

Start with the [language reference](language-reference.md).

It documents the syntax currently recognised by the lexer and parser and clearly identifies features that are still incomplete.

### Interested in the language design?

Read the [language specification](language-specification.md).

It describes the intended language model, including features that are still being designed or implemented.

### Contributing to the compiler?

Read the [development guide](development.md) and then [CONTRIBUTING.md](../CONTRIBUTING.md).

The development guide covers:

* repository structure;
* compiler architecture;
* local setup;
* testing;
* semantic-analysis development;
* adding language features; and
* documentation workflow.

### Looking for the project overview?

See the [root README](../README.md).

## Documents

### Language reference

[language-reference.md](language-reference.md)

Practical documentation for syntax currently supported by the compiler.

This document is intentionally implementation-focused. It distinguishes between syntax that is implemented, parsed, lexer-recognised, represented only in the AST, and not yet supported.

### Language specification

[language-specification.md](language-specification.md)

The design document for TeapotLang.

It describes intended language semantics and future compiler/runtime behaviour separately from the current implementation.

### Development

[development.md](development.md)

The contributor guide for working on the compiler and its tests.

It describes the current compiler pipeline, repository structure, development environment, tests, and workflow.

## Documentation status model

The documentation uses several terms to avoid confusing language design with compiler support.

| Term            | Meaning                                                                                               |
| --------------- | ----------------------------------------------------------------------------------------------------- |
| **Implemented** | The relevant compiler behaviour exists                                                                |
| **Parsed**      | The parser constructs an AST representation                                                           |
| **Recognised**  | The lexer recognises the syntax                                                                       |
| **Represented** | A compiler data structure exists, but the feature may not be parser-supported                         |
| **Design**      | The feature belongs to the intended language model but is not currently established by implementation |

A keyword, token, or AST dataclass does **not** by itself mean that a feature is usable.

## Keeping documentation current

When compiler behaviour changes:

1. Update the language reference if the supported syntax changes.
2. Update the language specification if the intended language semantics change.
3. Update the development guide if the compiler architecture, workflow, tests, or repository structure changes.
4. Update the root README if the project overview or quick-start instructions change.

The source code and tests establish current compiler behaviour.

The language specification establishes intended design.

The language reference explains the boundary between the two.
