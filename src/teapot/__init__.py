# Teapot package marker; compiler components live in the sibling modules.

# Single source of truth for the project version: pyproject.toml reads it from
# here, and the CLI's --version reports it, so the two cannot drift.
__version__ = "0.5.5a0"
