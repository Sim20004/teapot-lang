# TeapotLang

TeapotLang is an experimental statically typed programming language and compiler written in Python.

The project is focused on exploring the stages of compiler development, including lexing, parsing, abstract syntax trees, and semantic analysis.

> **Status: Alpha**
>
> TeapotLang is under active development. The lexer, parser, AST, and early semantic-analysis infrastructure are available, but the language and compiler are not yet complete.

## Quick start

TeapotLang requires **Python 3.10 or newer**.

Clone the repository and install it in a virtual environment:

```bash
git clone https://github.com/Sim20004/teapot-lang.git
cd teapot-lang

python -m venv .venv
source .venv/bin/activate

python -m pip install -r requirements.txt
python -m pip install -e .
```

## Using the compiler

TeapotLang source files use the `.tp` extension.

Compile a source file with:

```bash
teapot examples/hello.tp
```

For diagnostic output, use `--trace`:

```bash
teapot examples/hello.tp --trace
```

The compiler can also be invoked as a Python module:

```bash
python -m teapot examples/hello.tp
```

Trace mode can show the tokens produced by the lexer, the parsed AST, and semantic-analysis diagnostics.

The current pipeline is:

```text
Source
  │
  ▼
Lexer
  │
  ▼
Tokens
  │
  ▼
Parser
  │
  ▼
AST
  │
  ▼
Semantic analysis
```

The compiler currently stops at the semantic-analysis stage. **Code generation and an executable runtime are not implemented yet.**

## Example

```teapot
$MEM-GC

pub sct Person {
    cstr name.
    csi32 age.
}

pub fc add(csi32 a, csi32 b = 5)!csi32 {
    exit a + b.
}

fc main()!void {
    val msi32 x = 10.
    val msi32 y = 20.

    if (x < y) {
        x += 5.
    }
}
```

TeapotLang currently requires a memory-management directive at the beginning of a source file:

```teapot
$MEM-GC
```

or:

```teapot
$MEM-MANUAL
```

Statements generally end with a period (`.`), while blocks are delimited by `{` and `}`.

See the [language reference](docs/language-reference.md) for the syntax currently recognised by the compiler.

## Project structure

```text
teapot-lang/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   ├── workflows/
│   │   ├── pages.yml
│   │   └── tests.yml
│   └── pull_request_template.md
│
├── docs/
│   ├── development.md
│   ├── language-reference.md
│   ├── language-specification.md
│   └── README.md
│
├── examples/
├── src/
│   └── teapot/
│       ├── __init__.py
│       ├── __main__.py
│       ├── debug.py
│       ├── lexer.py
│       ├── main.py
│       ├── parser.py
│       ├── semantic.py
│       ├── teapot_ast.py
│       ├── tokens.py
│       └── web.py
│
├── tests/
│   ├── unit/
│   └── integration/
│
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE
├── MAINTAINERS.md
├── README.md
├── SECURITY.md
└── pyproject.toml
```

## Testing

Run the test suite from the repository root:

```bash
python -m pytest
```

The CI workflow also checks formatting and linting with Ruff, type-checks with mypy, builds the package, audits dependencies, and runs the test suite against supported Python versions.

Tests are organised by compiler stage. As the parser and semantic analyser continue to develop, their test coverage is being expanded alongside the implementation.

## Documentation

The `docs/` directory contains documentation for both users and contributors.

* **[Language reference](docs/language-reference.md)**
  Syntax and behaviour currently supported by the lexer and parser.

* **[Language specification](docs/language-specification.md)**
  The broader language design, including features that are not implemented yet.

* **[Development guide](docs/development.md)**
  Repository structure, development workflow, testing, and compiler architecture.

* **[Documentation index](docs/README.md)**
  Overview of the project's documentation.

## Contributing

Contributions, bug reports, and ideas are welcome.

Before contributing, read [CONTRIBUTING.md](CONTRIBUTING.md) for the project's contribution guidelines.

When adding or changing language behaviour, please include tests where appropriate and keep the documentation consistent with the implementation.

Please also review the [Code of Conduct](CODE_OF_CONDUCT.md) and [Security Policy](SECURITY.md).

## Project policies

* [Code of Conduct](CODE_OF_CONDUCT.md)
* [Contributing guide](CONTRIBUTING.md)
* [Security Policy](SECURITY.md)
* [Maintainers](MAINTAINERS.md)
* [Changelog](CHANGELOG.md)

## License

TeapotLang is licensed under the **GNU General Public License v3.0 or later**.
