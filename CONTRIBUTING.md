# Contributing to TeapotLang

Thank you for your interest in contributing to **TeapotLang**.

TeapotLang is an experimental programming language focused on exploring language design, parsing, semantics, memory management, and compiler implementation.

Contributions of all sizes are welcome, including bug fixes, documentation, tests, compiler improvements, language design, and tooling.

## Before Contributing

Please familiarise yourself with the existing codebase before making changes.

For substantial changes, open an issue or discussion before implementing the feature. This helps avoid spending significant time on a change that conflicts with the direction of the language.

Small bug fixes, documentation improvements, tests, and other focused changes can generally be submitted directly as pull requests.

## Development Principles

Contributions should aim to make TeapotLang:

* Correct
* Predictable
* Maintainable
* Consistent
* Well documented
* Easy to understand

Prefer simple implementations over unnecessarily clever ones.

Avoid introducing abstractions solely for the sake of abstraction.

Keep changes focused. A pull request fixing one parser bug should not also restructure unrelated parts of the compiler.

---

# Coding Standards

## Python Version

TeapotLang is written in Python.

Code should be compatible with the Python version currently supported by the project.

Do not use newer language features without confirming that the project's supported Python version allows them.

## British English

TeapotLang uses **British English** in documentation, comments, error messages, identifiers where appropriate, and other user-facing text.

Prefer:

```text
analyse
analysed
analyser
behaviour
colour
initialise
organisation
optimise
serialise
```

over:

```text
analyze
analyzed
analyzer
behavior
color
initialize
organization
optimize
serialize
```

For example:

```python
class SemanticAnalyser:
    ...
```

and:

```python
def analyse(self, ast_tree):
    ...
```

### Exceptions

Do not unnecessarily rename technical terms, third-party APIs, Python APIs, library names, or external terminology simply to make them British English.

For example, Python's:

```python
isinstance()
```

should obviously remain `isinstance()`.

Likewise, if an external API uses American English, use the API's actual name.

## Naming

Use descriptive names.

### Classes

Classes should use `PascalCase`:

```python
class Parser:
    ...

class ParserError(Exception):
    ...

class SemanticAnalyser:
    ...
```

### Functions and Methods

Functions and methods should use `snake_case`:

```python
def handle_expression():
    ...

def handle_function_argument():
    ...

def current_token():
    ...
```

Use names that describe what the function actually does.

Prefer:

```python
handle_array_literal()
```

over:

```python
handle_thing()
```

### Variables

Variables should use `snake_case`:

```python
current_token
ast_tree
memory_mode
return_type
member_name
```

Avoid unnecessary abbreviations.

Prefer:

```python
identifier
```

over:

```python
ident
```

unless the shorter form has an established meaning in the surrounding code.

### Constants

Constants should use `UPPER_SNAKE_CASE`:

```python
DATATYPES_MUTABILITY = {...}
STMT_HANDLERS = {...}
```

Constants should only be written this way when they represent values intended to remain constant.

Do not use uppercase names merely because a variable is important.

## Compiler Terminology

Use consistent terminology throughout the compiler.

Prefer the following terms:

| Term              | Meaning                                 |
| ----------------- | --------------------------------------- |
| Lexer             | Converts source text into tokens        |
| Token             | A lexical unit produced by the lexer    |
| Parser            | Converts tokens into an AST             |
| AST               | Abstract Syntax Tree                    |
| Semantic analyser | Checks semantic correctness             |
| Symbol table      | Stores information about identifiers    |
| Type              | Represents a TeapotLang type            |
| Expression        | Produces a value                        |
| Statement         | Performs an action                      |
| Operator          | Performs an operation                   |
| Identifier        | Name referring to a declaration         |
| Literal           | A value written directly in source code |

Do not use multiple names for the same compiler concept without a good reason.

## Imports

Keep imports organised and explicit.

Prefer:

```python
from dataclasses import is_dataclass
from sys import exit as leave

import src.teapot_ast as ast
from src import tokens
from src.debug import print
```

Avoid wildcard imports:

```python
from src.tokens import *
```

Imports should be placed at the top of the file unless there is a specific reason for a local import.

## Aliases

Aliases should be used when they improve clarity.

For example:

```python
import src.teapot_ast as ast
```

is appropriate because AST classes are frequently accessed throughout the parser.

Avoid aliases that make code harder to understand.

## Error Messages

Errors are part of TeapotLang's user experience.

Errors should be:

* Specific
* Consistent
* Understandable
* Useful to the programmer

Prefer:

```text
Parser error at token IDENTIFIER at position 12: Expected assignment operator
```

over:

```text
Something went wrong.
```

Use **British English** in user-facing error messages.

Compiler errors should identify the relevant location whenever that information is available.

## Exceptions

Use specific exception classes for compiler errors.

For example:

```python
class ParserError(Exception):
    ...
```

Semantic analysis should have its own error type rather than reusing `ParserError`.

For example:

```python
class SemanticError(Exception):
    ...
```

Do not silently catch compiler errors unless there is a meaningful reason to do so.

## AST Code

The AST is a central part of the compiler and should be treated as a stable interface between compiler stages.

Changes to AST nodes should be made carefully.

When adding or changing an AST node:

1. Update the AST definition.
2. Update the parser.
3. Update semantic analysis where necessary.
4. Update later compiler stages where necessary.
5. Add or update tests.

Avoid placing semantic validation inside the parser unless the validation is fundamentally syntactic.

For example:

```text
Parser:
    "Does this have valid syntax?"

Semantic analyser:
    "Does this syntactically valid program make sense?"
```

## Parser Code

The parser should primarily be concerned with syntax.

Do not add semantic rules to the parser simply because doing so appears convenient.

For example, checking whether a variable has already been declared belongs in semantic analysis, not parsing.

Parser methods should have clear responsibilities.

Prefer several small parsing methods:

```python
handle_expression()
handle_primary()
handle_array_literal()
handle_function()
handle_struct()
```

over one enormous method responsible for parsing everything.

## Semantic Analysis

Semantic analysis should operate on the AST produced by the parser.

It should be responsible for rules such as:

* Undefined identifiers
* Duplicate declarations
* Type compatibility
* Invalid assignments
* Invalid function calls
* Invalid member access
* Scope rules
* Mutability rules
* Other language-level semantic constraints

Keep semantic analysis separate from parsing wherever practical.

## Comments

Comments should explain **why**, not simply repeat **what** the code does.

Avoid:

```python
# Increment position by one
self.position += 1
```

Prefer comments that explain non-obvious reasoning:

```python
# Keep the EOF token virtual so the parser can safely inspect it
# without indexing beyond the token list.
```

Do not add comments to every line.

Well-written code should explain itself where possible.

## Formatting

Keep formatting consistent with the existing project.

Use readable indentation and spacing.

Avoid extremely long lines where breaking them improves readability.

For example:

```python
if (
    not self.at_end()
    and self.current_token().type != tokens.TokenType.CLOSE_BRACE
):
    ...
```

is preferable to an unnecessarily long single line.

Do not make unrelated formatting changes in a feature or bug-fix pull request.

## Data Structures

Choose data structures based on their purpose.

For example:

```python
self.ast_tree = []
```

is appropriate for an ordered collection of AST nodes.

A dictionary is appropriate when values need to be looked up by a key:

```python
DATATYPES_MUTABILITY = {...}
```

Do not introduce complicated data structures when a simple one is sufficient.

## Tests

New behaviour should have tests where practical.

When fixing a bug, preferably add a test that would have failed before the fix.

Language features should test:

* Valid programs
* Invalid programs
* Edge cases
* Interaction with existing features

A compiler must correctly handle both programs that should succeed and programs that should fail.

## Git

Keep commits focused.

Good commit:

```text
parser: support enum declarations
```

Good:

```text
semantic: reject undefined identifiers
```

Avoid:

```text
fix
```

```text
stuff
```

```text
changes
```

Commit messages should describe what the commit actually changes.

## Pull Requests

Pull requests should:

* Have a clear title.
* Explain what changed.
* Explain why it changed.
* Include relevant tests.
* Avoid unrelated changes.
* Be reasonably focused.
* Follow the project's coding standards.

A good pull request should be understandable to someone who did not write the implementation.

### Suggested Pull Request Structure

```markdown
## Summary

Briefly describe the change.

## Motivation

Explain why the change is needed.

## Changes

- Change one
- Change two
- Change three

## Testing

Explain how the change was tested.

## Notes

Include anything reviewers should be aware of.
```

## Language Design

TeapotLang is an evolving language.

When proposing a language feature, consider:

1. Is the feature actually useful?
2. Does it fit TeapotLang's existing design?
3. Is the syntax clear?
4. Is the behaviour predictable?
5. How does it interact with existing features?
6. How should invalid programs behave?
7. Does the feature introduce unnecessary complexity?

Do not add a feature solely because another language has it.

TeapotLang should have a coherent identity rather than becoming a collection of features copied from other languages.

## Scope of Contributions

Not every proposed contribution will necessarily be accepted.

A contribution may be declined if it:

* Conflicts with the language's design.
* Adds unnecessary complexity.
* Introduces significant maintenance costs.
* Duplicates existing functionality.
* Makes the language less consistent.
* Has insufficient justification.
* Does not pass all tests
* Has not added appropriate tests for the added features
* Is written using AI (Maintainer's discretion)

A rejected contribution is not a rejection of the contributor.

Technical disagreement is normal in open-source development.

## Communication

Be respectful and constructive.

Technical criticism is welcome. Personal attacks are not.

When disagreeing with a design decision, explain the technical reasoning behind your position and, where possible, propose an alternative.

## Licence

By contributing to TeapotLang, you agree that your contribution may be distributed under the project's existing licence.

Do not submit code or other material that you do not have permission to contribute.

## Final Principle

**Keep TeapotLang understandable.**

The compiler, language, and codebase should be approachable to someone learning how a programming language works.

When choosing between two implementations, prefer the one that is easier to understand, maintain, and reason about unless there is a compelling reason not to.
