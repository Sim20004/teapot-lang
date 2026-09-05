TeapotLang Roadmap

TeapotLang is currently in Alpha.

This roadmap describes the planned direction of the language and may change as development progresses.

Current Status

TeapotLang is currently focused on building the core language infrastructure and compiler pipeline.

Alpha

* [x]	Lexer
* [x]	Parser
* [x]	AST infrastructure
* [x]	Struct declarations
* [x]	Enum declarations
* [x]	Function declarations
* [x]	Operator overloading infrastructure
* [x]	Symbol table
* [x]	First-pass semantic analysis
* [ ]	Complete semantic analysis
* [ ]	Complete type checking
* [ ]	Improve compiler diagnostics
* [ ]	Stabilise the language specification

⸻

Phase 1: Language Foundations

The first priority is making the core language well-defined and reliable.

* [ ]	Complete semantic analysis
* [ ]	Complete type checking
* [ ]	Finalise variable and declaration rules
* [ ]	Finalise function and parameter rules
* [ ]	Finalise struct semantics
* [ ]	Finalise enum semantics
* [ ]	Finalise operator overloading rules
* [ ]	Improve scope and symbol resolution
* [ ]	Define compile-time error behaviour
* [ ]	Expand the language specification
* [ ]	Document all core language features

⸻

Phase 2: Compiler Infrastructure

Build the infrastructure required to turn valid TeapotLang programs into executable code.

* [ ]	Design intermediate representation
* [ ]	Implement IR generation
* [ ]	Implement backend architecture
* [ ]	Add target architecture support
* [ ]	Implement code generation
* [ ]	Implement linking/runtime integration
* [ ]	Add compiler optimisation infrastructure
* [ ]	Improve compiler error messages
* [ ]	Add source-location tracking throughout compilation

⸻

Phase 3: Memory Management

TeapotLang supports different memory-management models through compiler directives.

* [ ]	Finalise memory-management semantics
* [ ]	Implement automatic memory management
* [ ]	Implement manual memory management
* [ ]	Define ownership/lifetime behaviour where applicable
* [ ]	Improve memory-related diagnostics
* [ ]	Document memory-management behaviour

⸻

Phase 4: Standard Library

Build a useful standard library around the language.

* [ ]	Core utilities
* [ ]	Strings
* [ ]	Collections
* [ ]	File I/O
* [ ]	Environment/process APIs
* [ ]	Error handling utilities
* [ ]	Standard library documentation
* [ ]	Stable standard-library API

⸻

Phase 5: Developer Experience

Make TeapotLang pleasant to use outside the compiler itself.

* [ ]	Improve compiler diagnostics
* [ ]	Add a formatter
* [ ]	Add language-server support
* [ ]	Add editor integrations
* [ ]	Improve CLI tooling
* [ ]	Add project/package management
* [ ]	Improve documentation
* [ ]	Add tutorials and examples
* [ ]	Create a comprehensive language reference

⸻

Phase 6: Ecosystem

Move from a language implementation to an ecosystem.

* [ ]	Package registry
* [ ]	Package publishing tooling
* [ ]	Dependency management
* [ ]	Third-party libraries
* [ ]	Community examples
* [ ]	Community tooling
* [ ]	Plugin/extension system where appropriate

⸻

Stability

Before reaching a stable release, TeapotLang should have:

* [ ]	A stable language specification
* [ ]	Stable compiler behaviour
* [ ]	Stable standard library APIs
* [ ]	Predictable error reporting
* [ ]	Cross-platform support
* [ ]	Reproducible builds
* [ ]	Comprehensive documentation
* [ ]	Migration guidance between releases
* [ ]	Versioning policy
* [ ]	Backwards-compatibility policy

⸻

Release Targets

Alpha

Goal: Rapid language and compiler development.

Focus:

* Core language features
* Parser and AST
* Semantic analysis
* Type checking
* Compiler architecture

Breaking changes are expected.

Beta

Goal: Feature-complete language suitable for wider testing.

Focus:

* Stable language semantics
* Compiler reliability
* Standard library
* Developer tooling
* Documentation
* Cross-platform support

Breaking changes should become increasingly rare.

1.0

Goal: A stable TeapotLang release suitable for production use.

Requirements:

* Stable specification
* Stable compiler
* Stable standard library
* Documented compatibil
