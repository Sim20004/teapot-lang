# TeapotLang

TeapotLang is a statically typed programming language and compiler project written in Python.

The project exists both as a learning exercise in compiler development and as an experiment in language design. The compiler is being built from the ground up, including lexing, parsing, abstract syntax trees, semantic analysis, and code generation.

## Features

### Lexer

- Tokenisation
- Keywords
- Operators
- Literals
- Identifiers
- Source location tracking
- Error reporting

### Parser

- Abstract Syntax Tree generation
- Variable declarations
- Assignments
- Binary expressions
- Unary expressions
- Function declarations
- Function calls
- Default arguments
- Return statements
- Struct declarations
- Struct instantiation
- Enum declarations
- Custom error declarations
- If / Elif / Else
- While loops
- For loops
- Type casting
- References
- Array types
- Array literals

### Type System

Current support includes:

- Signed integers
- Unsigned integers
- Booleans
- Strings
- References
- Arrays
- User-defined structures
- Enumerations

### Memory Modes

Teapot is being designed with multiple memory management strategies in mind.

Current parser support includes memory mode directives such as:

```teapot
$MEM-GC
```

## Example

```teapot
pub struct Person {
    cstr name.
    csi32 age.
}

pub fn add(csi32 a, csi32 b = 5) -> csi32 {
    return a + b.
}

fn main() -> void {
    csi32 x = 10.
    csi32 y = 20.

    if x < y {
        x += 5.
    }

    return.
}
```

## Compilation Pipeline

```text
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
Semantic Analysis
     |
     v
Code Generation
```

## Goals

Teapot aims to explore:

- Programming language design
- Compiler implementation
- Static type systems
- Memory management
- Language tooling
- Runtime design

## Current Status

Teapot is currently in alpha development.

Implemented:

- Lexer
- Parser
- AST system

In Progress:

- Semantic analysis
- Type checking
- Symbol resolution

Planned:

- Compiler backend
- Standard library
- Executable generation
- Package manager
- Tooling ecosystem

## Building

Clone the repository:

```bash
git clone https://github.com/Sim20004/teapot-lang.git
cd teapot-lang
```

Run the compiler:

```bash
python main.py
```

## File Extension

```text
.tp
```

Example:

```text
hello.tp
```

## Contributing

Issues, pull requests, and discussions are welcome.

Whether you're interested in compilers, language design, or systems programming, contributions are appreciated.

## License

Teapot is licensed under the GNU General Public License v3.0-or-later.