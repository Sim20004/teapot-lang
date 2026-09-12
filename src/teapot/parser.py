"""Compatibility facade for the parser phase."""

from sys import exit as leave

from teapot.parsing.core import Parser, ParserError, print_ast, run

if __name__ == "__main__":
    leave(
        "Cannot run this file directly! Run `teapot -h` for info on how to start the compiler"
    )

__all__ = ["Parser", "ParserError", "print_ast", "run"]
