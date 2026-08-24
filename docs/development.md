# Development

This document is for contributors working on the Python compiler project. It describes the repository as it exists today; the [language specification](language-specification.md) contains design-level rules and proposals.

## Requirements and setup

The project declares Python `>=3.10` in `pyproject.toml`. `requirements.txt` contains `pytest`. From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -e .
```

The editable install makes the `src`-layout `teapot` package importable when running `main.py`. Pytest also adds `src` to its import path through `pyproject.toml`.

## Running the current pipeline

```bash
teapot --input examples/example.tp
```

The command-line entry point is `main.py`:

- `-i`/`--input` is required.
- `-t`/`--trace` enables diagnostic output.
- The input suffix must be exactly `.tp`.
- The command reads the source, removes and recreates `build/`, and starts the compiler pipeline.

The current pipeline is:

```text
source text -> Lexer -> tokens -> Parser -> Program AST -> semantic traversal
```

The lexer prints tokens in trace mode. The parser prints the AST in trace mode. The semantic analyser currently visits top-level AST nodes and prints their class names in trace mode. There is no code-generation module or executable output in the repository.

## Repository structure

```text
main.py                  CLI entry point
pyproject.toml           Packaging, Python version, pytest configuration
requirements.txt         Test dependency declaration
src/teapot/tokens.py     Token types and lexical tables
src/teapot/lexer.py      Source text to tokens
src/teapot/parser.py     Tokens to AST nodes
src/teapot/teapot_ast.py AST dataclass definitions
src/teapot/semantic.py   Current semantic-analysis entry point
src/teapot/debug.py      Diagnostic output helper
examples/                Teapot source examples and parser experiments
tests/unit/              Unit tests, currently lexer-focused
tests/integration/       Integration-test location, currently empty
docs/                    Project documentation
```

`build/` is generated or recreated by the CLI and is ignored by Git. `src/teapot.egg-info/` contains generated packaging metadata and should not be used as the source of language behaviour.

## Testing

Run the available suite with:

```bash
pytest
```

The current tests are in `tests/unit/test_lexer.py`. They cover tokenisation, directives, comments, literals, symbols, source positions, CRLF normalisation, and lexer errors. `tests/integration/` contains no tests at present. There are no parser or semantic tests, so changes to those stages should add focused coverage before relying on them.

## Development workflow

1. Read the relevant lexer, parser, AST, or semantic code before changing documentation or behaviour.
2. Add or update a focused test for the affected stage.
3. Run `pytest` from the repository root.
4. Run the CLI with a small `.tp` input and `--trace` when inspecting token or AST changes.
5. Keep documentation claims aligned with the implementation level: tokenised, parsed, represented in the AST, semantically checked, or executed.

Follow the naming, terminology, British English, and contribution guidance in [CONTRIBUTING.md](../CONTRIBUTING.md).