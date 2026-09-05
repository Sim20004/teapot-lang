Contributing to TeapotLang

Thank you for your interest in contributing to TeapotLang.

TeapotLang is an experimental programming language and compiler project focused on language design, parsing, semantic analysis, type checking, memory management, and compiler implementation.

Contributions of all sizes are welcome, including:

* Bug fixes
* Documentation improvements
* Tests
* Compiler improvements
* New language features
* Language design
* Tooling
* Developer experience improvements

Before Contributing

Please familiarise yourself with the existing codebase and documentation before making changes.

For substantial changes, especially new language features or changes to existing language behaviour, open an issue or discussion before implementing the feature. This helps ensure that the proposed change fits the direction of the language and avoids unnecessary implementation work.

Small bug fixes, documentation improvements, tests, and other focused changes can generally be submitted directly as pull requests.

Before starting work on an existing issue, check whether someone else is already working on it. If an issue is unassigned, consider commenting that you intend to work on it.

⸻

Development Principles

Contributions should aim to make TeapotLang:

* Correct
* Predictable
* Maintainable
* Consistent
* Well documented
* Easy to understand

Prefer simple implementations over unnecessarily clever ones.

Avoid introducing abstractions solely for the sake of abstraction.

A small amount of repetition can be preferable to an abstraction that makes the compiler harder to understand.

Keep changes focused. A pull request fixing one parser bug should not also restructure unrelated parts of the compiler.

Do not make unrelated changes simply because you happen to notice them while working on another feature. Open a separate issue or pull request when appropriate.

⸻

Development Setup

TeapotLang is written in Python.

The repository uses a src layout:

teapot-lang/
├── src/
│   └── teapot/
│       ├── __init__.py
│       ├── lexer.py
│       ├── parser.py
│       ├── semantic.py
│       ├── teapot_ast.py
│       ├── tokens.py
│       └── ...
├── tests/
│   └── unit/
├── examples/
├── requirements.txt
├── pyproject.toml
└── ...

Install the project’s dependencies with:

python -m pip install -r requirements.txt

Run the test suite with:

python -m pytest

Run Ruff’s checks with:

ruff check .
ruff format --check .

To automatically format the project:

ruff format .

CI runs the project’s configured checks automatically on pushes to main and pull requests targeting main.

Python Version

Use a Python version supported by the project’s CI configuration and package metadata.

Do not use language features that are unavailable in the supported Python versions without first discussing the change.

When adding a dependency, ensure that it supports all Python versions currently supported by TeapotLang.

The supported Python version should be determined from the repository’s CI configuration and pyproject.toml, rather than assumed from this document.

⸻

Changelog Requirements

Every commit must include an appropriate entry in CHANGELOG.md.

Each commit must add a concise, informative entry using the following format:

* <Date>: informative description

For example:

* 2026-09-05: Added semantic support for enum declarations.

The description should explain what the commit actually changes.

Avoid vague entries such as:

* 2026-09-05: Changes
* 2026-09-05: Fixed stuff

The changelog should remain useful to someone reviewing the project’s history without having to inspect the commit itself.

If a commit makes multiple closely related changes, describe the overall change clearly rather than listing every individual line changed.

Do not add changelog entries for changes that were not actually made.

⸻

Coding Standards

British English

TeapotLang uses British English in documentation, comments, error messages, identifiers where appropriate, and other user-facing text.

Prefer:

* analyse
* analysed
* analyser
* behaviour
* colour
* initialise
* organisation
* optimise
* serialise

over:

* analyze
* analyzed
* analyzer
* behavior
* color
* initialize
* organization
* optimize
* serialize

For example:

class SemanticAnalyser: ...

and:

def analyse(self, ast_tree): ...

Exceptions

Do not unnecessarily rename technical terms, third-party APIs, Python APIs, library names, or external terminology simply to make them British English.

For example, Python’s isinstance() should remain isinstance().

Likewise, if an external API uses American English, use the API’s actual name.

Do not modify names from third-party libraries simply to follow TeapotLang’s spelling conventions.

Naming

Use descriptive names throughout the compiler.

Names should describe what a value, function, class, or module actually represents or does.

Avoid unnecessary abbreviations.

Classes

Classes should use PascalCase:

class Parser: ...
class ParserError(Exception): ...
class SemanticAnalyser: ...

Class names should describe the concept represented by the class.

Functions and Methods

Functions and methods should use snake_case:

def handle_expression(): ...
def handle_function_argument(): ...
def current_token(): ...

Use names that describe what the function actually does.

Prefer:

handle_array_literal()

over:

handle_thing()

Avoid overly generic names when a more descriptive name is reasonably short.

Variables

Variables should use snake_case:

current_token
ast_tree
memory_mode
return_type
member_name

Avoid unnecessary abbreviations.

Prefer identifier over ident unless the shorter form has an established meaning in the surrounding code.

Constants

Constants should use UPPER_SNAKE_CASE:

DATATYPES_MUTABILITY = {...}
STMT_HANDLERS = {...}

Use this convention when a value is intended to remain constant.

Do not use uppercase names merely because a variable is important or widely used.

⸻

Compiler Terminology

Use consistent terminology throughout the compiler.

Term	Meaning
Lexer	Converts source text into tokens
Token	A lexical unit produced by the lexer
Parser	Converts tokens into an AST
AST	Abstract Syntax Tree
Semantic analyser	Checks semantic correctness
Symbol table	Stores information about declarations and identifiers
Symbol	Represents information about a declaration within the symbol table
Type	Represents a TeapotLang type
Expression	Produces a value
Statement	Performs an action
Operator	Performs an operation
Identifier	Name referring to a declaration
Literal	A value written directly in source code
Scope	The declaration context in which symbols are visible

Do not use multiple names for the same compiler concept without a good reason.

For example, if the project refers to the component as the semantic analyser, do not introduce another name such as “semantic checker” in a new module without a reason.

Consistency is especially important in compiler development because the same concepts appear in source code, tests, documentation, error messages, and language specifications.

⸻

Imports

Keep imports organised and explicit.

With the project’s src layout, imports should normally refer to the teapot package:

from dataclasses import is_dataclass
from sys import exit as leave
import teapot.teapot_ast as ast
from teapot import tokens
from teapot.debug import print

Avoid wildcard imports:

from teapot.tokens import *

Wildcard imports make it harder to determine where names originate and can make compiler code more difficult to understand.

Imports should normally be placed at the top of the file unless there is a specific reason for a local import.

Aliases

Aliases should be used when they improve clarity.

For example:

import teapot.teapot_ast as ast

is appropriate when AST classes are accessed frequently throughout a module.

Avoid aliases that make code harder to understand.

Do not use meaningless aliases simply to shorten names.

⸻

Formatting

TeapotLang uses Ruff for linting and formatting.

Run:

ruff check .

to check for lint errors.

Run:

ruff format --check .

to check whether files are correctly formatted.

Run:

ruff format .

to automatically apply formatting.

Do not manually reformat unrelated files as part of a feature or bug-fix pull request unless the formatting change is required.

Formatting changes can create large diffs and make code review harder.

⸻

Comments

Comments should explain why, not simply repeat what the code does.

Avoid comments that merely describe an obvious operation:

# Increment position by one
self.position += 1

Prefer comments that explain non-obvious reasoning:

# Keep EOF virtual so the parser can safely inspect it
# without indexing beyond the token list.

Comments are particularly useful when explaining:

* Parser design decisions
* AST invariants
* Workarounds
* Compatibility requirements
* Non-obvious algorithms
* Why apparently unusual behaviour is necessary

Do not add comments to every line.

Well-written code should explain itself where possible.

⸻

Data Structures

Choose data structures based on their purpose.

For example:

self.ast_tree = []

is appropriate for an ordered collection of AST nodes.

A dictionary is appropriate when values need to be looked up by a key:

DATATYPES_MUTABILITY = {...}

A set is appropriate when membership checking or uniqueness is important.

Do not introduce complicated data structures when a simple one is sufficient.

Prefer code that clearly expresses the intended operation over code that is unnecessarily optimised or abstract.

⸻

Error Messages

Errors are part of TeapotLang’s user experience.

Compiler errors should be:

* Specific
* Consistent
* Understandable
* Useful to the programmer

Prefer:

Parser error at token IDENTIFIER at position 12: Expected assignment operator

over:

Something went wrong.

Compiler errors should identify the relevant location whenever that information is available.

Use British English in user-facing error messages.

Error messages should explain what the compiler expected and, where practical, what it actually found.

Avoid vague messages such as:

Invalid syntax.

when more useful information is available.

⸻

Exceptions

Use specific exception classes for different compiler stages.

For example:

class ParserError(Exception): ...

Semantic analysis should have its own error type:

class SemanticError(Exception): ...

Different compiler stages should not raise unrelated exception types simply because they already exist.

Do not silently catch compiler errors unless there is a meaningful reason to do so.

Avoid:

try:
    ...
except Exception:
    pass

unless there is a very specific and documented reason.

Compiler errors should generally propagate to the appropriate error-reporting layer.

⸻

Compiler Architecture

TeapotLang is divided into several conceptual stages.

The current general flow is:

TeapotLang source code
        ↓
      Lexer
        ↓
      Tokens
        ↓
      Parser
        ↓
       AST
        ↓
Semantic analysis
        ↓
 Future compiler stages

Each stage should have a clear responsibility.

Avoid moving functionality between stages simply because doing so makes one particular implementation easier.

Lexer

The lexer converts source text into tokens.

The lexer should be responsible for recognising lexical structures such as:

* Keywords
* Identifiers
* Literals
* Operators
* Punctuation
* Directives
* Other lexical constructs

The lexer should not determine whether a syntactically valid program makes semantic sense.

For example, whether a variable has been declared is not a lexer concern.

Parser

The parser converts tokens into the Abstract Syntax Tree.

The parser should primarily be concerned with syntax.

It should answer questions such as:

“Does this sequence of tokens form a valid expression?”

It should not answer questions such as:

“Was this variable already declared?”

Those questions belong to semantic analysis.

Parser methods should have clear responsibilities.

Prefer several focused parsing methods:

handle_expression()
handle_primary()
handle_array_literal()
handle_function()
handle_struct()

over one enormous method responsible for parsing every construct in the language.

AST

The AST is a central part of the compiler and acts as an interface between compiler stages.

Changes to AST nodes should therefore be made carefully.

When adding or changing an AST node:

1. Update the AST definition.
2. Update the parser.
3. Update semantic analysis where necessary.
4. Update later compiler stages where necessary.
5. Add or update tests.
6. Update documentation where the language behaviour changes.
7. Update CHANGELOG.md.

Avoid putting semantic validation into the parser unless the validation is fundamentally syntactic.

A useful distinction is:

Parser:
    "Does this have valid syntax?"
Semantic analyser:
    "Does this syntactically valid program make sense?"

Semantic Analysis

Semantic analysis operates on the AST produced by the parser.

The current semantic-analysis architecture includes symbol-table construction and scoped declarations. It includes support for declarations such as:

* Variables
* Functions
* Function arguments
* Structs
* Struct fields
* Enums
* Enum members
* Errors
* Error members

Symbols have a declaration scope and may own a child scope where appropriate. For example, functions can own a scope for their body and aggregate types can own scopes for their members.

Semantic analysis should be responsible for rules such as:

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

A syntactically valid program is not necessarily a semantically valid program.

⸻

Parser Code

When modifying the parser, consider how the change interacts with existing expression precedence, statements, declarations, and blocks.

Parser changes should preserve the existing grammar unless the change intentionally modifies the language.

When adding a new construct:

1. Determine how the lexer represents it.
2. Determine where it fits into the grammar.
3. Add or modify the relevant parser method.
4. Construct the appropriate AST node.
5. Add valid and invalid tests.
6. Update semantic analysis if necessary.
7. Update the language documentation if user-visible behaviour changes.
8. Update CHANGELOG.md.

Avoid duplicating parsing logic when an existing parser method already handles the required construct.

For example, if a construct contains an expression, use the existing expression parser rather than implementing a second expression parser inside that construct.

⸻

Semantic Analysis

Semantic analysis should enforce language rules that cannot be determined from syntax alone.

Examples include:

* Whether an identifier exists
* Whether a variable can be reassigned
* Whether two types are compatible
* Whether a function call has valid arguments
* Whether a member exists on a type
* Whether a reference is valid
* Whether a declaration conflicts with another declaration
* Whether a construct is valid within its current scope

Do not move these checks into the parser merely because doing so appears convenient.

Keeping these responsibilities separate makes the compiler easier to maintain and makes error handling more predictable.

⸻

Tests

New behaviour should have tests where practical.

When fixing a bug, preferably add a regression test that would have failed before the fix.

A compiler should test both programs that should succeed and programs that should fail.

What to Test

Language features should test:

* Valid programs
* Invalid programs
* Edge cases
* Error handling
* Interaction with existing features
* Operator precedence where applicable
* Boundary conditions

For example, a new control-flow feature should not only test the simplest valid example. It should also consider:

* Nested usage
* Empty blocks where applicable
* Invalid syntax
* Interaction with other control-flow constructs
* Complex expressions
* Incorrect types where semantic analysis is involved

Running Tests

Run the complete test suite with:

python -m pytest

Before submitting a pull request, ensure that the tests pass locally.

If a test cannot be run locally for a documented reason, mention this in the pull request.

⸻

Git

Keep commits focused and descriptive.

Good commit messages include:

parser: support enum declarations
semantic: reject undefined identifiers
lexer: recognise hexadecimal literals

Avoid vague commit messages such as:

fix
stuff
changes

Commit messages should describe what the commit actually changes.

Do not combine unrelated changes into one commit simply because they were made at the same time.

Every commit must also include its corresponding CHANGELOG.md entry.

⸻

Pull Requests

Pull requests should:

* Have a clear title.
* Explain what changed.
* Explain why it changed.
* Include relevant tests.
* Avoid unrelated changes.
* Be reasonably focused.
* Follow the project’s coding standards.
* Pass CI.
* Include the required changelog entry.

A good pull request should be understandable to someone who did not write the implementation.

Before submitting a pull request, check:

ruff check .
ruff format --check .
python -m pytest

Also verify that:

* CHANGELOG.md contains an entry for every commit in the pull request.
* Documentation is updated when necessary.
* Language behaviour is documented when changed.

⸻

Language Design

TeapotLang is an evolving language.

Language design decisions should prioritise consistency and clarity rather than simply adding as many features as possible.

When proposing a language feature, consider:

1. Is the feature actually useful?
2. Does it fit TeapotLang’s existing design?
3. Is the syntax clear?
4. Is the behaviour predictable?
5. How does it interact with existing features?
6. How should invalid programs behave?
7. How does it interact with the type system?
8. How does it interact with mutability?
9. How does it interact with memory management?
10. Does the feature introduce unnecessary complexity?

Do not add a feature solely because another language has it.

TeapotLang should have a coherent identity rather than becoming a collection of features copied from other languages.

For substantial language changes, open an issue or discussion before implementing the feature.

A useful language proposal should explain:

Problem
    ↓
Proposed syntax
    ↓
Proposed semantics
    ↓
Examples
    ↓
Invalid examples
    ↓
Interaction with existing features
    ↓
Implementation considerations

⸻

Documentation

Documentation is part of the language.

If a contribution changes user-visible language behaviour, update the relevant documentation.

Documentation should use examples wherever they make the behaviour clearer.

Examples should be:

* Correct
* Consistent with the current language
* Small enough to understand
* Representative of real usage

Do not document planned behaviour as if it were already implemented.

If a feature is experimental or incomplete, make that clear.

Documentation changes should also receive an appropriate CHANGELOG.md entry.

⸻

AI-Assisted Contributions

TeapotLang does not encourage the use of AI to write code.

The project is intended to remain understandable to its contributors, and contributors should be able to explain the code they submit.

If AI tools are used during development, contributors remain fully responsible for everything they submit.

Contributors must:

* Understand the code they submit.
* Verify any generated code.
* Review all generated output.
* Run relevant tests.
* Ensure the contribution follows project conventions.
* Review generated documentation for correctness.
* Ensure they have permission to submit incorporated material.

Contributors should not submit code they do not understand simply because an AI tool generated it.

Large amounts of unreviewed or AI-generated code may be rejected, particularly where the contributor cannot explain the implementation or its design.

The maintainers may request changes or reject contributions where AI-assisted code introduces:

* Incorrect behaviour
* Unnecessary complexity
* Security issues
* Licensing concerns
* Poor maintainability
* Inconsistent design
* Unverified claims
* Inappropriate generated content

Using AI assistance does not remove responsibility from the contributor.

The quality, understandability, and maintainability of the contribution matter more than how the code was produced.

⸻

Scope of Contributions

Not every proposed contribution will necessarily be accepted.

A contribution may be declined if it:

* Conflicts with the language’s design.
* Adds unnecessary complexity.
* Introduces significant maintenance costs.
* Duplicates existing functionality.
* Makes the language less consistent.
* Has insufficient justification.
* Does not pass the test suite.
* Does not pass CI.
* Does not include appropriate tests for new behaviour.
* Introduces undocumented language behaviour.
* Cannot be reasonably maintained.

A contribution may also be declined if the maintainers believe that the proposed feature does not fit the long-term direction of TeapotLang.

A rejected contribution is not a rejection of the contributor.

Technical disagreement is a normal part of open-source development.

⸻

Good First Issues

TeapotLang maintains issues labelled good first issue for contributors who are new to the project.

These issues are intended to be relatively self-contained and approachable without requiring complete knowledge of the compiler.

Before starting a good first issue:

1. Read the relevant documentation.
2. Inspect the existing implementation.
3. Check related tests.
4. Check whether someone is already working on the issue.
5. Ask questions if the requirements are unclear.

Do not assume that a good first issue requires no understanding of the compiler.

Some issues may still require familiarity with the lexer, parser, AST, or semantic analyser.

⸻

Communication

Be respectful and constructive.

Technical criticism is welcome. Personal attacks are not.

When disagreeing with a design decision, explain the technical reasoning behind your position and, where possible, propose an alternative.

Avoid dismissing ideas without explaining why they are problematic.

Questions are welcome. Contributors should not be expected to understand the entire compiler before making their first contribution.

⸻

Licence

By contributing to TeapotLang, you agree that your contribution may be distributed under the project’s existing licence.

Do not submit code, documentation, or other material that you do not have permission to contribute.

Do not knowingly include copyrighted material that you are not permitted to redistribute.

⸻

Final Principle

Keep TeapotLang understandable.

The compiler, language, and codebase should remain approachable to people learning how programming languages and compilers work.

When choosing between two implementations, prefer the one that is easier to:

* Understand
* Maintain
* Test
* Reason about
* Extend

unless there is a compelling reason not to.

TeapotLang is a learning project as well as a compiler project. Good contributions should improve the language without making the underlying implementation unnecessarily difficult to understand.