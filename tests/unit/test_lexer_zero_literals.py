import pytest

from teapot import tokens
from teapot.lexer import Lexer


def test_zero_integer_literal():
    lexer = Lexer("0")
    tokens_list = lexer.tokenise()

    assert len(tokens_list) == 2
    assert tokens_list[0].type == tokens.TokenType.INTEGER
    assert tokens_list[0].value == 0
    assert tokens_list[1].type == tokens.TokenType.EOF


def test_zero_float_literal():
    lexer = Lexer("0.0")
    tokens_list = lexer.tokenise()

    assert len(tokens_list) == 2
    assert tokens_list[0].type == tokens.TokenType.FLOAT
    assert tokens_list[0].value == 0.0
    assert tokens_list[1].type == tokens.TokenType.EOF


def test_zero_float_with_trailing_zeros():
    lexer = Lexer("0.00")
    tokens_list = lexer.tokenise()

    assert len(tokens_list) == 2
    assert tokens_list[0].type == tokens.TokenType.FLOAT
    assert tokens_list[0].value == 0.0
    assert tokens_list[1].type == tokens.TokenType.EOF


def test_leading_zeros_integer():
    lexer = Lexer("00")
    tokens_list = lexer.tokenise()

    assert len(tokens_list) == 2
    assert tokens_list[0].type == tokens.TokenType.INTEGER
    assert tokens_list[0].value == 0
    assert tokens_list[1].type == tokens.TokenType.EOF


def test_leading_zeros_float():
    lexer = Lexer("00.0")
    tokens_list = lexer.tokenise()

    assert len(tokens_list) == 2
    assert tokens_list[0].type == tokens.TokenType.FLOAT
    assert tokens_list[0].value == 0.0
    assert tokens_list[1].type == tokens.TokenType.EOF
