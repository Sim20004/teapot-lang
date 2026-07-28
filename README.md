# Teapot Programming Language

Teapot is a statically typed programming language and compiler project written in Python.

The goal of Teapot is to create a simple, readable language while exploring how programming languages work internally, including lexing, parsing, abstract syntax trees, type systems, and compilation.

## Features

Currently implemented:

* Lexer

  * Tokenisation of source code
  * Keywords, operators, literals, and identifiers
  * Error reporting with line and column information

* Parser

  * AST generation
  * Variable declarations
  * Literal expressions
  * Binary expressions
  * Unary expressions

* AST system

  * Structured representation of Teapot programs
  * Support for future language features such as functions, structs, control flow, and memory management

## Example

Teapot source code:

```teapot
val ui8 a = 5 + 3.

val ui8 b = a + 10.

val str greeting = "Hello " + "World".

val bool enabled = ~True.
```

The compiler transforms this source code through multiple stages:

```
Source Code
     |
     v
Lexer
     |
     v
Tokens
     |
     v
Parser
     |
     v
Abstract Syntax Tree
     |
     v
Compiler
```

## Language Design

Teapot is designed around:

* Explicit syntax
* Static typing
* Readable code
* Compiler transparency
* Learning and experimenting with language design

The language includes concepts such as:

* Strongly typed variables
* Signed and unsigned integer types
* References
* Structures
* Functions
* Manual memory management concepts

## Project Status

Teapot is currently in active development.

Current focus:

* Completing the parser
* Expanding expression support
* Adding type checking
* Building the compiler backend
* Developing the standard library

The language is not yet production-ready.

## Building and Running

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/teapot-lang.git
cd teapot-lang
```

Run the compiler:

```bash
python main.py
```

## File Extension

Teapot source files use:

```
.tp
```

Example:

```
hello.tp
```

## Contributing

Contributions, suggestions, and discussions are welcome.

If you are interested in language design, compiler development, or experimenting with programming languages, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License.
