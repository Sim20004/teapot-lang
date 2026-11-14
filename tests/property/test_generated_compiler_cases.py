import itertools

import pytest

import teapot.teapot_ast as ast
from teapot import tokens
from teapot.lexer import Lexer
from teapot.parser import Parser

WHITESPACE = ("", " ", "\t", "\n", " \t", "\n\n", " \n", "\t\n", "\r\n")
LEXICAL_ATOMS = tuple(
    (value, token_type)
    for value, token_type in itertools.chain(
        tokens.KEYWORDS.items(),
        ((value, tokens.TokenType.TYPE) for value in sorted(tokens.TYPE_KEYWORDS)),
        tokens.SYMBOLS.items(),
        (("true", tokens.TokenType.BOOLEAN), ("false", tokens.TokenType.BOOLEAN)),
    )
)
LEXICAL_CASES = tuple(
    (value, token_type, prefix, suffix)
    for value, token_type in LEXICAL_ATOMS
    for prefix, suffix in itertools.product(WHITESPACE, repeat=2)
)


@pytest.mark.parametrize("value, expected_type, prefix, suffix", LEXICAL_CASES)
def test_lexer_classifies_every_atom_across_whitespace_boundaries(
    value, expected_type, prefix, suffix
):
    tokenised = Lexer(prefix + value + suffix).tokenise()

    assert tokenised[0].type == expected_type
    assert tokenised[0].value == (
        True
        if expected_type == tokens.TokenType.BOOLEAN and value == "true"
        else False
        if expected_type == tokens.TokenType.BOOLEAN and value == "false"
        else value
    )
    assert tokenised[-1].type == tokens.TokenType.EOF


PRIMITIVE_DECLARATION_CASES = tuple(
    (datatype, literal, name)
    for datatype in sorted(tokens.TYPE_KEYWORDS)
    for literal in ("1", "-1", "1.5", '"value"')
    for name in ("value", "value_1", "_value", "value2")
)


@pytest.mark.parametrize("datatype, literal, name", PRIMITIVE_DECLARATION_CASES)
def test_parser_builds_variable_ast_for_type_literal_and_identifier_matrix(
    datatype, literal, name
):
    program = Parser(
        Lexer(f"$MEM-GC\nval {datatype} {name} = {literal}.").tokenise()
    ).parse()

    declaration = program.statements[0]
    assert isinstance(declaration, ast.DeclareVariable)
    assert declaration.identifier == name
    assert declaration.datatype.name == datatype
    assert declaration.value is not None


BALANCED_ATOM_CASES = tuple(
    (atom_text, atom_node, depth)
    for atom_text, atom_node in (
        ("1", ast.Literal(1)),
        ("x", ast.Identifier("x")),
        ("true", ast.Literal(True)),
    )
    for depth in range(5)
)


@pytest.mark.parametrize("atom_text, atom_node, depth", BALANCED_ATOM_CASES)
def test_parser_parses_balanced_parenthesised_atoms(atom_text, atom_node, depth):
    wrapped = "(" * depth + atom_text + ")" * depth
    program = Parser(Lexer(f"$MEM-GC\nval si64 value = {wrapped}.").tokenise()).parse()

    declaration = program.statements[0]
    assert isinstance(declaration, ast.DeclareVariable)
    assert declaration.value == atom_node


BALANCED_BINARY_CASES = tuple(
    (
        left_text,
        left_node,
        operator,
        right_text,
        right_node,
        left_wrap,
        right_wrap,
        whole_wrap,
    )
    for (left_text, left_node, operator, right_text, right_node) in (
        ("1", ast.Literal(1), "+", "x", ast.Identifier("x")),
        ("x", ast.Identifier("x"), "*", "2", ast.Literal(2)),
    )
    for left_wrap, right_wrap, whole_wrap in itertools.product(range(3), repeat=3)
)


@pytest.mark.parametrize(
    (
        "left_text",
        "left_node",
        "operator",
        "right_text",
        "right_node",
        "left_wrap",
        "right_wrap",
        "whole_wrap",
    ),
    BALANCED_BINARY_CASES,
)
def test_parser_parses_balanced_parenthesised_binary_expressions(
    left_text,
    left_node,
    operator,
    right_text,
    right_node,
    left_wrap,
    right_wrap,
    whole_wrap,
):
    left_expression = "(" * left_wrap + left_text + ")" * left_wrap
    right_expression = "(" * right_wrap + right_text + ")" * right_wrap
    inner = f"{left_expression} {operator} {right_expression}"
    wrapped = "(" * whole_wrap + inner + ")" * whole_wrap
    program = Parser(Lexer(f"$MEM-GC\nval si64 value = {wrapped}.").tokenise()).parse()

    declaration = program.statements[0]
    assert isinstance(declaration, ast.DeclareVariable)
    assert declaration.value == ast.BinaryExpression(left_node, operator, right_node)
