# TeapotLang Changelog
Below is every change made to the TeapotLang repo with a date and short description.

# Unreleased

- 2026-09-05: Updated maintainer contact information with email addresses
- 2026-09-05: Updated instructions for reporting vulnerabilities

# Version 0.6.0-alpha

- 2026-09-05: Reworked the symbol table to separate declaration scope from child scope and added error type support
- 2026-09-05: Added symbol construction for struct fields
- 2026-09-05: Added enum support
- 2026-09-04: Refactored the bloated semantic analysis first-pass function into a helper method for symbol definition, removing confusing two-way guard logic
- 2026-09-01: Added a trademark policy for TeapotLang
- 2026-09-01: Fixed tests broken by removing params from `Symbol.__init__()`
- 2026-09-01: Reworked function parameter definition in semantic analysis to define parameters in the function scope instead of storing them on `Symbol`
- 2026-08-31: Reworded a comment in `semantic.py`
- 2026-08-31: Formatted website code with Prettier
- 2026-08-31: Made a minor website change
- 2026-08-31: Added cache-busting to website assets
- 2026-08-31: Updated `index.html`
- 2026-08-31: Added pagination to the releases page
- 2026-08-31: Fixed a JavaScript bug on the website
- 2026-08-31: Added a releases page to the website

# Version 0.5.5-alpha

- 2026-08-31: Bumped the version in `__init__.py`
- 2026-08-31: Reformatted code with Ruff
- 2026-08-31: Expanded integration test coverage
- 2026-08-31: Updated the website homepage
- 2026-08-30: Merged a fix for CLI tests running from a source checkout
- 2026-08-30: Updated tests to run the CLI through the module entry point
- 2026-08-30: Refactored the CLI to use the module entry point as its sole launcher
- 2026-08-30: Organized imports
- 2026-08-30: Triggered CI
- 2026-08-30: Completed the changelog through v0.5.4-alpha
- 2026-08-30: Polished the README and documented repository conventions
- 2026-08-30: Added a changelog
- 2026-08-30: Added a security policy
- 2026-08-30: Added a code of conduct
- 2026-08-30: Added a pull request template
- 2026-08-30: Added a feature request issue template
- 2026-08-30: Added a bug report issue template
- 2026-08-30: Added a conventional package entry point

# Version 0.5.4-alpha

- 2026-08-30: Updated the website homepage (multiple passes)
- 2026-08-30: Updated website styles
- 2026-08-30: Fixed stale docs still referencing the old `-i`/`--input` flag
- 2026-08-30: Added an interactive demo to the TeapotLang website
- 2026-08-30: Reformatted `web.py` with Ruff
- 2026-08-30: Added `web.py` to enable a live in-browser demo of TeapotLang
- 2026-08-30: Fixed pipeline section scaling on mobile
- 2026-08-30: Updated stale website content
- 2026-08-30: Updated stale documentation
- 2026-08-30: Changed the file input to a positional CLI argument
- 2026-08-30: Improved website SEO
- 2026-08-30: Added `robots.txt`
- 2026-08-30: Added `sitemap.xml`
- 2026-08-30: Improved homepage SEO
- 2026-08-30: Updated Dependabot configuration
- 2026-08-30: Added Dependabot configuration
- 2026-08-30: Triggered CI
- 2026-08-30: Added a GitHub Pages deploy workflow

# Version 0.5.3-alpha

- 2026-08-30: Added the TeapotLang project website

# Version 0.5.2-alpha

- 2026-08-30: Updated stale documentation

# Version 0.5.1-alpha

- 2026-08-30: Added more semantic analysis tests and expanded integration test coverage
- 2026-08-29: Removed old tests
- 2026-08-29: Reworked function definition in semantic analysis to use `Symbol`'s parameter list instead of constructing a new local-scope symbol
- 2026-08-29: Wired up the call to `define_function_scope_statements()`
- 2026-08-28: Updated the README
- 2026-08-28: Fixed tests failing due to a mismatch with the new API
- 2026-08-27: Began adding support for function-scope statements (partial, still buggy)

# Version 0.5.0-alpha

- 2026-08-26: Fixed the version string to read `v0.5.0a0`
- 2026-08-26: Removed a redundant `rm build/` from the build script
- 2026-08-26: Fixed a mismatch between an echo statement and the script
- 2026-08-26: Fixed a mismatch between a comment and the code
- 2026-08-26: Started integration tests
- 2026-08-26: Removed unnecessar
