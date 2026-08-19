# TeapotLang documentation

This directory documents the language design and the compiler that currently exists in this repository.

## Where to start

- New Teapot programmers should start with the [language reference](language-reference.md).
- Readers looking for the intended language rules should use the [language specification](language-specification.md).
- Compiler contributors should read [development](development.md), then [CONTRIBUTING.md](../CONTRIBUTING.md).
- The project overview and installation quick start are in [README.md](../README.md).

## Documents

### Language reference

[language-reference.md](language-reference.md) is a practical, scan-friendly guide to syntax that the current lexer and parser recognise. It does not promise type checking, runtime behaviour, or executable output.

### Language specification

[language-specification.md](language-specification.md) records the intended language model represented by the existing specification document. It is the authoritative design document, but it marks rules that are not established by the current implementation.

### Development

[development.md](development.md) describes the repository layout, compiler pipeline, local commands, test coverage, and the boundaries of the current implementation.

## Evidence and status

The source code and tests are the authority for current behaviour. In these documents:

- **Implemented** means the relevant code path exists and is exercised or directly established by the repository.
- **Recognised** means the lexer can produce a token, but later compiler stages may reject it.
- **Represented** means an AST node or table exists, without implying parser or semantic support.
- **Design** means the existing specification describes the intended feature, but current support is incomplete or absent.

The repository currently has lexer tests but no parser or semantic test suite. Treat untested parser behaviour as implementation behaviour, not as a complete language guarantee.