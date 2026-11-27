# TeapotLang roadmap

TeapotLang is in alpha. This roadmap describes the intended direction of the project, not a promise of release dates. Items marked complete refer only to the scope stated in that item; they do not imply that the whole language feature is finished.

## Current status

The lexer, parser, AST, CLI, and initial semantic-analysis infrastructure are implemented. Semantic analysis currently has a declaration-and-scope pass followed by a partial type-checking pass. The compiler does not yet generate executable code or provide a language runtime.

### Alpha foundations

- [x] Lexer and token definitions
- [x] Parser and AST infrastructure
- [x] Core declaration syntax for variables, functions, structs, enums, errors, and operators
- [x] Initial symbol table and parent/child scope lookup
- [x] Declaration registration and duplicate-name detection
- [x] Initial semantic type checks for supported declarations, literals, expressions, and callable returns
- [ ] Complete semantic analysis and type checking
- [ ] Assignment value and mutability validation
- [ ] Function-call argument validation
- [ ] Condition and control-flow validation
- [ ] Complete member, cast, and operator-overload resolution
- [ ] Finalise core language semantics and specification

## Phase 1: Language foundations

Make the core language rules reliable and unambiguous.

- [ ] Define and implement assignment compatibility and mutability rules
- [ ] Validate function-call argument counts and types
- [ ] Validate conditions and control-flow requirements
- [ ] Complete type conversions and cast validation
- [ ] Resolve struct fields and enum members
- [ ] Define and implement operator-overload resolution
- [ ] Complete return-path and callable validation
- [ ] Finalise variable, function, struct, enum, and error semantics
- [ ] Improve semantic diagnostics and source locations
- [ ] Keep the language reference aligned with implemented behaviour

## Phase 2: Compiler infrastructure

Build the stages needed to produce executable programs.

- [ ] Design an intermediate representation
- [ ] Implement IR generation and lowering
- [ ] Design a backend interface
- [ ] Select and support an initial target architecture
- [ ] Implement code generation
- [ ] Integrate linking and runtime support
- [ ] Add compiler optimisation infrastructure

## Phase 3: Memory management

The source directives currently record a selected mode; they do not implement memory management.

- [ ] Finalise memory-management semantics
- [ ] Define ownership, aliasing, and lifetime rules
- [ ] Implement automatic memory management
- [ ] Implement manual memory management
- [ ] Add memory-related diagnostics and tests

## Phase 4: Runtime and standard library

- [ ] Design and implement the runtime
- [ ] Add core utilities and input/output
- [ ] Add strings and collections
- [ ] Add filesystem and process APIs
- [ ] Add runtime error-handling facilities
- [ ] Document and stabilise standard-library APIs

## Phase 5: Developer experience

- [ ] Improve CLI diagnostics and tooling
- [ ] Add a formatter
- [ ] Add language-server support
- [ ] Add editor integrations
- [ ] Add project and package management
- [ ] Add tutorials and practical examples

## Phase 6: Ecosystem

- [ ] Design package publishing and dependency management
- [ ] Establish a package registry
- [ ] Encourage third-party libraries and community examples
- [ ] Consider a plugin or extension system where it is useful

## Before a stable 1.0 release

- [ ] Stable language specification and compiler behaviour
- [ ] Usable runtime and standard library
- [ ] Predictable diagnostics
- [ ] Cross-platform support
- [ ] Reproducible builds and release process
- [ ] Migration guidance and compatibility policy
- [ ] Complete user and developer documentation

Breaking language and compiler changes are expected during alpha. Priorities may change as implementation and language design develop.
