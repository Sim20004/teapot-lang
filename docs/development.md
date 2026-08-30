# Development

This document describes the current TeapotLang repository and development workflow. It is intended for contributors working on the compiler, tests, documentation, and language implementation.

For the practical syntax supported by the current compiler, see the [language reference](language-reference.md). For the intended language design and features that are not necessarily implemented yet, see the [language specification](language-specification.md).

## Requirements

TeapotLang requires Python `3.10` or newer.

The project uses a `src` layout and is packaged through `pyproject.toml`. The `teapot` command is provided by the package's console-script entry point.

Create a virtual environment and install the project in editable mode:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

The repository's test suite uses pytest. If pytest is not already available in the development environment, install it separately:

```bash
python -m pip install pytest
```

The repository does not use `requirements.txt` as its primary dependency or installation mechanism.

## Running TeapotLang

After installing the package:

```bash
teapot --input examples/hello.tp
```

The CLI accepts:

```text
-i, --input PATH    Input TeapotLang source file. Required.
-t, --trace         Enable compiler diagnostic output.
    --version       Display the compiler version.
```

For example:

```bash
teapot examples/hello.tp -t
```

Input files must use the `.tp` extension.

The CLI currently recreates the `build/` directory when it runs. The compiler does not currently generate an executable.

## Compiler pipeline

The current pipeline is:

```text
TeapotLang source
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
   Program AST
       |
       v
Semantic analysis
       |
       v
 Symbol tables
```

The main stages are:

### Lexer

`src/teapot/lexer.py` converts source text into tokens.

The lexer handles:

* identifiers;
* keywords;
* built-in type names;
* integer, floating-point, string, and Boolean literals;
* operators and punctuation;
* `$MEM-GC` and `$MEM-MANUAL`;
* `//` comments;
* line and column tracking; and
* CRLF-to-LF normalisation.

The lexer raises `LexerError` for invalid lexical input.

### Parser

`src/teapot/parser.py` converts tokens into the AST defined in `src/teapot/teapot_ast.py`.

The parser currently supports a substantial subset of the language, including:

* variable declarations;
* functions;
* structs;
* enums;
* error declarations;
* operator declarations;
* assignments;
* `if`/`elif`/`else`;
* `while`;
* `for`;
* `exit`;
* expressions;
* function calls;
* arrays;
* member access; and
* casts.

Not every token or AST dataclass represents a parser-supported feature. Consult the [language reference](language-reference.md) when determining whether a feature is actually parseable.

Parser failures raise `ParserError`.

### AST

`src/teapot/teapot_ast.py` contains the dataclasses used to represent parsed programs.

The AST is the interface between parsing and later compiler stages. When adding syntax, update the AST only when the new syntax needs a new representation.

### Semantic analysis

`src/teapot/semantic.py` currently performs the first stage of semantic analysis.

The current implementation includes:

* `Symbol`;
* `SymbolTable`;
* parent/child scope lookup;
* global scope construction;
* variable declaration registration;
* function declaration registration;
* function scopes;
* struct declaration registration;
* duplicate declaration detection; and
* function parameter metadata.

The analyser currently has a first-pass symbol-table phase and a placeholder second-pass type-checking phase.

The second pass does not yet implement full type checking.

Semantic failures raise `SemanticError`.

## Repository structure

```text
.github/
    workflows/                 GitHub Actions configuration

docs/
    development.md             Contributor/development guide
    language-reference.md      Current lexer/parser syntax
    language-specification.md  Intended language design

examples/
    hello.tp                   Basic language example
    operators.tp               Operator example
    fixtures/                  Compiler test fixtures

scripts/
    Repository/development scripts

src/
    teapot/
        __init__.py             Package metadata/version
        main.py                 CLI entry point
        tokens.py               Token definitions and language tables
        lexer.py                Lexer
        parser.py               Parser
        teapot_ast.py           AST dataclasses
        semantic.py             Semantic analysis
        debug.py                Diagnostic output

tests/
    unit/
        test_lexer.py
        test_parser.py
        test_semantic.py
        test_semantic_advanced.py
        test_semantic_errors.py
        test_semantic_scoping.py

    integration/
        test_pipeline.py

pyproject.toml                  Packaging and pytest configuration
CONTRIBUTING.md                 Contribution guidelines
README.md                       Project overview
```

Generated files and directories such as `build/` and package metadata generated during installation should not be treated as source files.

## Testing

Run the complete test suite with:

```bash
pytest
```

You can also run individual areas:

```bash
pytest tests/unit/test_lexer.py
pytest tests/unit/test_parser.py
pytest tests/unit/test_semantic.py
pytest tests/unit/test_semantic_advanced.py
pytest tests/unit/test_semantic_errors.py
pytest tests/unit/test_semantic_scoping.py
pytest tests/integration/test_pipeline.py
```

Use verbose output when investigating a failure:

```bash
pytest -v
```

### Test organisation

The test suite is divided into two main levels.

**Unit tests** test individual compiler components and semantic-analysis behaviour.

**Integration tests** exercise multiple compiler stages together.

When changing compiler behaviour, add the smallest focused test that demonstrates the new behaviour or regression.

## Adding a language feature

When implementing new syntax, normally work through the compiler in this order:

1. Define or update the relevant token.
2. Update lexical recognition if necessary.
3. Update the AST if a new representation is required.
4. Update the parser.
5. Add parser tests.
6. Add semantic handling if the feature requires it.
7. Add semantic tests.
8. Add or update an integration test when multiple stages interact.
9. Update the language reference.
10. Update the language specification if the intended language design has changed.

Do not add a feature to the language reference merely because a token or AST dataclass exists. A feature should be documented as usable only when the relevant compiler stage actually supports it.

## Semantic-analysis development

Semantic analysis is being developed incrementally.

The intended progression is:

```text
Pass 1
  |
  +-- collect declarations
  +-- create scopes
  +-- register symbols
  |
  v
Pass 2
  |
  +-- resolve names
  +-- validate types
  +-- validate expressions
  +-- validate assignments
  +-- validate function calls
  +-- validate returns
  +-- validate control flow
```

The exact division between passes may evolve as implementation continues.

Current symbol-table behaviour should be tested independently from future type-checking behaviour.

## Trace output

Use `--trace` when investigating compiler behaviour:

```bash
teapot examples/hello.tp --trace
```

Trace output can expose:

* lexer activity;
* generated tokens;
* parser output; and
* semantic-analysis and symbol-table information.

Trace output is diagnostic output and should not be treated as a stable machine-readable interface.

## Documentation rules

Keep the three main documentation layers separate:

* `README.md` explains what the project is and how to get started.
* `docs/language-reference.md` documents syntax currently supported by the lexer and parser.
* `docs/language-specification.md` documents the intended language design, including features that are not yet implemented.

When implementation changes, update the appropriate documentation in the same change where practical.

## Development workflow

A typical change should follow this workflow:

```text
Understand existing implementation
            |
            v
       Make change
            |
            v
       Add tests
            |
            v
     Run pytest
            |
            v
   Test CLI if relevant
            |
            v
    Update documentation
```

Before submitting a change:

```bash
pytest
```

and, for compiler changes:

```bash
teapot examples/hello.tp -t
```

Follow the naming, terminology, British English, and contribution guidance in [CONTRIBUTING.md](../CONTRIBUTING.md).
