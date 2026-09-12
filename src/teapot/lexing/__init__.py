"""Lexical analysis public API.

The compatibility module :mod:`teapot.lexer` remains available for existing
programs; new code can import the lexer from this phase-oriented namespace.
"""

from teapot.errors import (
    DuplicateDirectiveError,
    InvalidDirectiveError,
    InvalidNumberError,
    InvalidSymbolError,
    UnterminatedStringError,
)
from teapot.lexer import Lexer, LexerError, run

__all__ = [
    "DuplicateDirectiveError",
    "InvalidDirectiveError",
    "InvalidNumberError",
    "InvalidSymbolError",
    "Lexer",
    "LexerError",
    "UnterminatedStringError",
    "run",
]
