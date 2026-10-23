# TeapotLang

<p align="center">
  <a href="https://github.com/Sim20004/teapot-lang/actions/workflows/tests.yml"><img src="https://img.shields.io/github/actions/workflow/status/Sim20004/teapot-lang/tests.yml?style=flat&label=tests" alt="Tests"></a>&nbsp;&nbsp;
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white" alt="Python 3.10+"></a>&nbsp;&nbsp;
  <a href="LICENSE"><img src="https://img.shields.io/badge/licence-GPL--3.0--or--later-blue?style=flat" alt="Licence"></a>&nbsp;&nbsp;
  <a href="https://github.com/Sim20004/teapot-lang/issues"><img src="https://img.shields.io/github/issues/Sim20004/teapot-lang?style=flat" alt="Issues"></a>&nbsp;&nbsp;
  <a href="https://github.com/Sim20004/teapot-lang/stargazers"><img src="https://img.shields.io/github/stars/Sim20004/teapot-lang?style=flat" alt="Stars"></a>&nbsp;&nbsp;
  <a href="https://github.com/Sim20004/teapot-lang/forks"><img src="https://img.shields.io/github/forks/Sim20004/teapot-lang?style=flat" alt="Forks"></a>
</p>

**An experimental, statically typed programming language built around explicitness, structure, and a clearly defined specification.**

TeapotLang is an open-source programming language and compiler project written in Python. It explores how a language moves from source code through lexical analysis, parsing, abstract syntax trees, and semantic analysis, with the long-term goal of becoming a compiled, general-purpose language.

**Explore the project:** [Official website](https://teapotlang.simarpreetsingh.org/) · [Source code](https://github.com/Sim20004/teapot-lang) 

The project is being developed incrementally, with an emphasis on keeping the intended language design distinct from what the compiler can actually support today.

> [!WARNING]
> **TeapotLang is experimental and under active development.** The compiler is not yet a complete implementation of the language specification. Code generation and a complete executable runtime are not implemented, so TeapotLang is not currently suitable for production software.

## Explore TeapotLang

- **[Official website](https://teapotlang.simarpreetsingh.org/)** — the project's web presence and entry point.
- **[Language reference](docs/language-reference.md)** — syntax recognised by the compiler and the implementation's current limitations.
- **[Language specification](docs/language-specification.md)** — the intended language design, including features that have not yet been implemented.
- **[Examples](examples/)** — explore example TeapotLang source files.
- **[Development guide](docs/development.md)** — learn about the compiler architecture and contributing workflow.
- **[Issues](https://github.com/Sim20004/teapot-lang/issues)** — report problems, suggest features, or follow development.
- **[Changelog](CHANGELOG.md)** — follow changes to the project.

## What does TeapotLang look like?

TeapotLang uses explicit type names, structured declarations, and familiar control-flow constructs. Its syntax is designed to make the structure of a program visible rather than relying on extensive implicit behaviour.

For example, the following illustrates the language's declaration and function syntax:

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

This example illustrates several elements of the language's design:

- **Memory-management directives** — source files begin with a directive such as `$MEM-GC` or `$MEM-MANUAL`.
- **Structures** — `sct` introduces a user-defined data structure.
- **Functions** — `fc` declares a function, while `!` introduces its return type.
- **Explicit types** — declarations use type names rather than relying entirely on type inference.
- **Visibility** — `pub` marks declarations as public.
- **Control flow** — constructs such as `if` and compound-assignment operators form part of the language design.
- **Statement terminators** — statements generally end with a period (`.`), while blocks use braces.

This is an illustration of the language's syntax, not a claim that every construct shown is fully implemented or executable. Consult the [language reference](docs/language-reference.md) for the current implementation status of individual features.

## Design goals

TeapotLang aims to provide a structured foundation for writing programs while keeping its rules explicit and its implementation understandable.

| Goal | What it means |
| --- | --- |
| **Static typing** | Make types an explicit part of the language and enable semantic checks before execution. |
| **Readable structure** | Use clear declarations, delimited blocks, and consistent statement syntax. |
| **User-defined types** | Support structures and other abstractions as the language develops. |
| **Predictable semantics** | Define language behaviour in a specification rather than leaving it entirely to implementation choices. |
| **Memory-management choices** | Explore configurable memory-management models through source-level directives. |
| **A staged compiler** | Develop the compiler in distinct phases, making each stage easier to understand and test. |

These are design goals, not a guarantee that every feature is available in the current compiler.

## Compiler status

The compiler is written in Python and is being developed as a sequence of increasingly capable stages.

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
      AST
       |
       v
Semantic analysis
       |
       v
  Future stages
```

The current implementation includes the lexer, parser, abstract syntax tree (AST), and semantic-analysis infrastructure. The pipeline is being extended towards the language specification.

The following distinctions matter:

- **Recognised syntax** means the lexer can identify the relevant tokens.
- **Parsed syntax** means the parser can construct the corresponding AST.
- **Implemented behaviour** means the relevant compiler functionality actually exists.
- **Specified behaviour** describes the intended design, which may still be awaiting implementation.

A keyword being recognised, or an AST node existing, does not necessarily mean the associated language feature is usable.

### What is not implemented yet?

Code generation and a complete executable runtime remain future work. TeapotLang therefore cannot yet compile a program into a finished executable through a complete end-to-end pipeline.

The language specification may describe capabilities beyond those currently supported. Check the [language reference](docs/language-reference.md) before relying on a particular feature.

## Getting started

TeapotLang requires **Python 3.10 or newer**.

Clone the repository and install the project in a virtual environment:

```bash
git clone https://github.com/Sim20004/teapot-lang.git
cd teapot-lang

python -m venv .venv
source .venv/bin/activate

python -m pip install -e .
```

The project provides a `teapot` command-line entry point. You can inspect an example source file using trace mode:

```bash
teapot examples/hello.tp --trace
```

Alternatively, invoke the compiler as a Python module:

```bash
python -m teapot examples/hello.tp --trace
```

TeapotLang source files use the `.tp` extension. Trace output helps inspect the compiler's intermediate stages and diagnostics; it does not mean the source file will be turned into an executable.

For command-line details and supported syntax, see the [language reference](docs/language-reference.md).

## Documentation

The project separates the intended language design from the compiler's current capabilities so that users can tell what is available now and what remains planned.

| Document | Purpose |
| --- | --- |
| [Language reference](docs/language-reference.md) | Documents syntax currently supported or recognised by the implementation. |
| [Language specification](docs/language-specification.md) | Describes the intended language model and future behaviour. |
| [Development guide](docs/development.md) | Explains compiler architecture, the development environment, testing, and contribution workflow. |
| [Documentation index](docs/README.md) | Provides an overview of the project's documentation. |
| [Changelog](CHANGELOG.md) | Records project changes. |

If you are learning the language, start with the language reference. If you want to understand where the language is heading, read the specification as well. The [official website](https://teapotlang.simarpreetsingh.org/) provides a convenient entry point to the project.

## Contributing

TeapotLang is an evolving project, and contributions are welcome. Bug reports, improvements to existing compiler stages, tests, examples, and work towards implementing the language specification can all help move the project forward.

If you are considering contributing:

1. Browse the [open issues](https://github.com/Sim20004/teapot-lang/issues) to find existing work or report a problem.
2. Read [CONTRIBUTING.md](CONTRIBUTING.md) before making a change.
3. When changing compiler behaviour, include relevant tests and keep the documentation consistent with the implementation.
4. For proposed language features, refer to the specification so that implementation work follows the intended design.

You can also review the project's [Code of Conduct](CODE_OF_CONDUCT.md) and [Security Policy](SECURITY.md).

> [!IMPORTANT]
> Contributions to compiler development are especially welcome, as this is currently the project's highest priority. Please see the pinned issue for details.

## Project status

TeapotLang is an active experiment in programming-language and compiler development. Its specification and implementation will evolve as new language features are designed, implemented, and tested.

The project aims to build towards a coherent language implementation rather than treating every proposed feature as already available. The README gives an overview; the [language reference](docs/language-reference.md), [specification](docs/language-specification.md), and source code provide the more detailed picture.

For website updates and release information, visit the [official website](https://teapotlang.simarpreetsingh.org/) or its [release notes](https://teapotlang.simarpreetsingh.org/release.html).

## Licence

TeapotLang is licensed under the **GNU General Public License v3.0 or later (GPL-3.0-or-later)**. See [`LICENSE`](LICENSE) for the full licence text.
