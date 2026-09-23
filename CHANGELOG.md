# TeapotLang Changelog

Every commit in the `Sim20004/teapot-lang` repository is represented below, from the initial repository creation through the latest commit. Descriptions have been rewritten to summarise the actual change made by each commit.

# TeapotLang 0.6.2-alpha

* 2026-09-23: Added integration and unit tests covering binary-expression type inference and invalid type combinations, restoring the project to 100% test coverage
* 2026-09-23: Added return-type checking for functions and operators, including validation of returned values against their declared types
* 2026-09-14: Extended semantic analysis to validate function return types and unified function and operator checking
* 2026-09-14: Added operator type checking and introduced a dedicated semantic error for invalid return types
* 2026-09-13: Fixed tests and adjusted semantic-analysis dispatch to accommodate the new type-checking behaviour
* 2026-09-13: Added datatype validation, type-bound checking, and errors for invalid and void datatypes
* 2026-09-12: Changed semantic analysis to ignore AST node types that are intentionally handled by later compiler phases
* 2026-09-12: Fixed `break` and `continue` handling inside nested loop scopes
* 2026-09-12: Corrected the error hierarchy so mypy accepts the semantic error definitions
* 2026-09-12: Reformatted the project with Ruff
* 2026-09-12: Added variable declaration type checking to the second semantic-analysis pass and reorganised the associated semantic errors and tests
* 2026-09-11: Introduced the first implementation of semantic type checking
* 2026-09-09: Reformatted tests covering semantic-analysis coverage gaps
* 2026-09-09: Completed the first semantic-analysis pass for symbol registration
* 2026-09-08: Added parser coverage for the stress-test program and completed its parsing support
* 2026-09-08: Updated documentation that no longer matched the implemented language
* 2026-09-08: Changed CI so builds fail when reported test coverage falls below 100%
* 2026-09-08: Switched Codecov authentication to use a repository secret
* 2026-09-08: Added Codecov coverage reporting to CI
* 2026-09-07: Assigned an otherwise-unused expression to `_` so it complies with TeapotLang's expression rules
* 2026-09-07: Applied the remaining coverage changes needed to restore complete test coverage
* 2026-09-07: Added a large contributor test suite containing roughly 9,000 additional tests
* 2026-09-07: Split semantic analysis into multiple modules to make the implementation easier to maintain
* 2026-09-07: Added support for redefining variables that have already been initialised
* 2026-09-06: Updated the changelog for the v0.6.1-alpha release

# Version 0.6.1-alpha

* 2026-09-06: Added operator support to semantic analysis and repaired the affected tests
* 2026-09-05: Expanded contributor guidance with maintainer contact details
* 2026-09-05: Refined the instructions for reporting security vulnerabilities
* 2026-09-05: Updated the changelog
* 2026-09-05: Added a project roadmap
* 2026-09-05: Added an email contact address for the maintainer
* 2026-09-05: Expanded the instructions for reporting security vulnerabilities
* 2026-09-05: Reworked the symbol table so declaration scope is separated from child scopes and added support for error types
* 2026-09-05: Added symbol construction for struct fields
* 2026-09-05: Added enum support to semantic analysis
* 2026-09-04: Refactored the first semantic-analysis pass so symbol definition is performed by a dedicated helper
* 2026-09-01: Added the TeapotLang trademark policy
* 2026-09-01: Updated tests after removing parameter storage from `Symbol.__init__()`
* 2026-09-01: Changed function parameters to be defined directly in the function scope rather than stored on `Symbol`
* 2026-08-31: Clarified a comment in semantic analysis
* 2026-08-31: Reformatted the website using Prettier
* 2026-08-31: Added release downloads to the website by linking the first release asset
* 2026-08-31: Added cache-busting to website assets
* 2026-08-31: Updated the website index page
* 2026-08-31: Added pagination to the releases page
* 2026-08-31: Fixed a JavaScript bug on the website
* 2026-08-31: Added the releases page to the website

# Version 0.5.5-alpha

* 2026-08-31: Bumped the package version in `__init__.py`
* 2026-08-31: Reformatted the project with Ruff
* 2026-08-31: Expanded integration-test coverage
* 2026-08-31: Updated the website homepage
* 2026-08-30: Merged the fix for CLI tests running from a source checkout
* 2026-08-30: Changed CLI tests to invoke TeapotLang through its module entry point
* 2026-08-30: Refactored the CLI so the module entry point is its sole launcher
* 2026-08-30: Organised Python imports
* 2026-08-30: Triggered CI
* 2026-08-30: Completed the changelog through v0.5.4-alpha
* 2026-08-30: Polished the README and documented repository conventions
* 2026-08-30: Added the changelog
* 2026-08-30: Added the security policy
* 2026-08-30: Added the code of conduct
* 2026-08-30: Added a pull-request template
* 2026-08-30: Added a feature-request issue template
* 2026-08-30: Added a bug-report issue template
* 2026-08-30: Added the conventional package entry point

# Version 0.5.4-alpha

* 2026-08-30: Updated the website homepage
* 2026-08-30: Updated website styling
* 2026-08-30: Updated documentation to use the new positional CLI input argument
* 2026-08-30: Added an interactive TeapotLang demo to the website
* 2026-08-30: Reformatted `web.py` with Ruff
* 2026-08-30: Added `web.py` to expose TeapotLang as a live browser demo
* 2026-08-30: Improved responsive scaling of the website pipeline section
* 2026-08-30: Adjusted mobile scaling of the website pipeline section
* 2026-08-30: Updated stale website content
* 2026-08-30: Updated stale documentation
* 2026-08-30: Changed the CLI file input from an option to a positional argument
* 2026-08-30: Improved website SEO
* 2026-08-30: Added `robots.txt`
* 2026-08-30: Added `sitemap.xml`
* 2026-08-30: Updated homepage metadata for improved SEO
* 2026-08-30: Updated Dependabot configuration
* 2026-08-30: Added Dependabot configuration
* 2026-08-30: Triggered CI
* 2026-08-30: Added a GitHub Pages deployment workflow

# Version 0.5.3-alpha

* 2026-08-30: Added the TeapotLang project website

# Version 0.5.2-alpha

* 2026-08-30: Updated stale documentation

# Version 0.5.1-alpha

* 2026-08-30: Added semantic-analysis tests and expanded integration-test coverage
* 2026-08-29: Removed obsolete tests
* 2026-08-29: Changed function-definition handling to use `Symbol` parameter information instead of creating duplicate local-scope symbols
* 2026-08-29: Connected function-scope statement processing to semantic analysis
* 2026-08-28: Updated the README
* 2026-08-28: Fixed tests after an API change
* 2026-08-27: Began implementing support for statements inside function scopes

# Version 0.5.0-alpha

* 2026-08-26: Corrected the package version to `v0.5.0a0`
* 2026-08-26: Removed an unnecessary build-directory deletion from the build script
* 2026-08-26: Fixed a build-script status message so it matches the command being executed
* 2026-08-26: Corrected a comment that no longer matched the implementation
* 2026-08-26: Started integration tests
* 2026-08-26: Removed obsolete and broken example programs
* 2026-08-26: Removed the obsolete `requirements.txt` installation step again
* 2026-08-26: Removed `requirements.txt` installation from CI
* 2026-08-26: Removed the unnecessary `requirements.txt` file and standardised the `pip-audit` command in CI
* 2026-08-26: Fixed the commit/build script so its CI test no longer fails unconditionally
* 2026-08-26: Fixed a `TypeError` in semantic analysis
* 2026-08-25: Added semantic-analysis tests
* 2026-08-24: Added semantic-analysis support for function arguments
* 2026-08-24: Fixed the build script
* 2026-08-24: Repaired CI after test changes and removed the obsolete `tests.yml.old`
* 2026-08-24: Moved `main.py` into the package, added the `teapot` command, and updated imports, tests, and documentation
* 2026-08-24: Fixed formatting introduced by the preceding changes
* 2026-08-24: Added parser tests for empty `while` and `if` blocks
* 2026-08-24: Merged parser tests covering empty function, `while`, and `if` blocks
* 2026-08-24: Added function support to semantic-analysis pass 1
* 2026-08-24: Added parser tests for empty function, `while`, and `if` blocks
* 2026-08-23: Added initial struct support
* 2026-08-23: Removed type checking from the parser so it can be handled by semantic analysis
* 2026-08-22: Started semantic analysis
* 2026-08-22: Updated the README
* 2026-08-22: Merged CLI usage documentation
* 2026-08-22: Added CLI usage examples to the documentation
* 2026-08-22: Merged the operator-declaration example
* 2026-08-22: Added an example demonstrating operator declaration syntax
* 2026-08-21: Removed an obsolete comment
* 2026-08-21: Completed lexer and parser test coverage
* 2026-08-21: Fixed failing tests
* 2026-08-21: Reformatted `CONTRIBUTING.md`
* 2026-08-21: Updated `CONTRIBUTING.md`
* 2026-08-21: Added `MAINTAINERS.md`
* 2026-08-21: Updated the package version
* 2026-08-21: Updated the test workflow
* 2026-08-21: Merged the CLI version-option feature
* 2026-08-21: Formatted the project with Ruff
* 2026-08-21: Added a `--version` CLI option and centralised the package version
* 2026-08-21: Added build, mypy, and Ruff checks to CI
* 2026-08-21: Fixed failing tests
* 2026-08-21: Fixed Ruff issues in preparation for CI linting
* 2026-08-21: Updated contributor documentation
* 2026-08-21: Expanded parser unit-test coverage
* 2026-08-21: Expanded parser unit-test coverage
* 2026-08-21: Merged the revert of the parser-performance and CI experiment
* 2026-08-21: Reverted the parser-performance and CI-check changes
* 2026-08-21: Merged the parser-performance and CI pull request
* 2026-08-21: Reused the operator-precedence table to improve parser performance
* 2026-08-21: Made debug-log encoding explicit
* 2026-08-21: Added linting to CI and tightened the test command
* 2026-08-20: Added additional parser unit tests
* 2026-08-20: Expanded parser tests and removed obsolete struct-instantiation handling
* 2026-08-20: Added explanatory comments to the parser
* 2026-08-20: Added parser tests
* 2026-08-20: Updated `debug.py`
* 2026-08-19: Expanded CI to test Python 3.10 through 3.14
* 2026-08-19: Implemented the first six planned parser unit tests
* 2026-08-19: Added the TeapotLang language documentation
* 2026-08-19: Completed the planned lexer unit-test suite
* 2026-08-19: Fixed build handling so the build directory is available when required
* 2026-08-19: Added ten lexer tests, bringing the implemented total to 27 of the planned 38
* 2026-08-19: Added the initial GitHub Actions test workflow
* 2026-08-19: Created the lexer test plan and implemented its first 17 tests
* 2026-08-19: Fixed the first lexer test
* 2026-08-19: Reorganised the project files
* 2026-08-18: Started the semantic analyser and corrected the project directory structure
* 2026-08-16: Removed an obsolete TODO
* 2026-08-13: Updated the README
* 2026-08-13: Completed the v0.3.0 parser work
* 2026-08-10: Removed the MIT licence
* 2026-08-10: Added the project licence
* 2026-08-10: Updated the parser
* 2026-08-02: Added reference support
* 2026-08-02: Reformatted the project
* 2026-08-02: Added stacked member access, character literals, struct instantiation, and `for` loops
* 2026-07-30: Updated the parser
* 2026-07-30: Updated the licence documentation
* 2026-07-30: Updated the licence documentation
* 2026-07-30: Updated the licence documentation
* 2026-07-30: Made major additions to the parser
* 2026-07-30: Added struct parsing support
* 2026-07-29: Updated the TODO list
* 2026-07-29: Added a parser/build example showing tokenisation output and the build directory
* 2026-07-29: Removed an obsolete TODO
* 2026-07-29: Added function parsing support
* 2026-07-29: Added parenthesis support to expressions
* 2026-07-28: Fixed AST printing
* 2026-07-28: Fixed minor parser and AST issues
* 2026-07-28: Resolved merge conflicts
* 2026-07-28: Expanded and clarified the language specification
* 2026-07-28: Updated the README
* 2026-07-28: Added the initial README
* 2026-07-28: Renamed the licence file to `LICENSE.md`
* 2026-07-28: Added the initial licence file
* 2026-07-28: Removed obsolete files from the initial project structure
* 2026-07-28: Completed the first expression and variable handlers and formatted the code with Black
* 2026-07-28: Updated the parser
* 2026-07-26: Made major additions to the language and parser
* 2026-07-26: Completed the AST implementation
* 2026-07-26: Completed the lexer prototype and moved on to tests
* 2026-07-26: Continued lexer development
* 2026-07-25: Updated the lexer implementation
* 2026-07-25: Updated the example Teapot program
* 2026-07-25: Added single-line comment tokenisation support
* 2026-07-25: Expanded tokeniser support
* 2026-07-25: Completed the initial tokeniser
* 2026-07-25: Created the initial repository and project structure
