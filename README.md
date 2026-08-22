[![Discord](https://img.shields.io/discord/1540780981634728098?label=Discord&logo=discord&color=5865F2)](https://discord.gg/3G5A9UA8W)

# TeapotLang

TeapotLang is an experimental statically typed programming language and compiler written in Python. It is a learning project for exploring language design, lexing, parsing, abstract syntax trees, semantic analysis, and memory management.

The project is in alpha. The lexer, parser, and AST pipeline are implemented; semantic analysis currently walks the AST, while code generation, an executable runtime, and a standard library are still planned.

## Quick start

TeapotLang requires Python 3.10 or newer.

```bash
git clone https://github.com/Sim20004/teapot-lang.git
cd teapot-lang
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -e .
```

## CLI usage

The compiler requires a `.tp` source file passed with `--input` (or `-i`):

```bash
python main.py --input examples/parser_curr_test.tp
```

Use `--trace` (or `-t`) to print tokens, the AST, and semantic-analysis output while the source is processed:

```bash
python main.py -i examples/parser_curr_test.tp -t
```

The current compiler lexes and parses the source, then performs a shallow semantic traversal. It recreates the `build/` directory on each run, but it does not produce an executable yet. See [Development](docs/development.md) for tests and project structure.

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

Every source file currently begins with either `$MEM-GC` or `$MEM-MANUAL`. Statements are terminated with a period. The complete syntax overview is in [Language reference](docs/language-reference.md).

## Compilation pipeline

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
```

The semantic-analysis stage currently visits top-level AST nodes only. The [language reference](docs/language-reference.md) documents the syntax available at the lexer/parser boundary; the [language specification](docs/language-specification.md) records the broader intended design.

## Contributing

Issues, pull requests, and discussions are welcome. Read [Contributing](CONTRIBUTING.md) before making changes.

## License

Teapot is licensed under the GNU General Public License v3.0-or-later.
