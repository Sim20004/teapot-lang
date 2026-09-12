"""Errors raised while converting source text into tokens."""

from teapot.errors import (
    DuplicateDirectiveError,
    InvalidDirectiveError,
    InvalidNumberError,
    InvalidSymbolError,
    LexerError,
    LexicalError,
    UnterminatedStringError,
)

__all__ = [
    "DuplicateDirectiveError",
    "InvalidDirectiveError",
    "InvalidNumberError",
    "InvalidSymbolError",
    "LexerError",
    "LexicalError",
    "UnterminatedStringError",
]
