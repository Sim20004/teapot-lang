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

SIMPLE_INTEGER_LITERALS = ("0", "1", "7", "9", "10", "42", "99", "00", "007", "123")
SIMPLE_FLOAT_LITERALS = ("0.0", "0.5", "1.0", "2.75", "10.01", "00.0", "01.50")
NUMERIC_LITERAL_CASES = tuple(
    (literal, tokens.TokenType.INTEGER, prefix, suffix)
    for literal in SIMPLE_INTEGER_LITERALS
    for prefix, suffix in itertools.product(WHITESPACE, repeat=2)
) + tuple(
    (literal, tokens.TokenType.FLOAT, prefix, suffix)
    for literal in SIMPLE_FLOAT_LITERALS
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


@pytest.mark.parametrize(
    "literal, expected_type, prefix, suffix", NUMERIC_LITERAL_CASES
)
def test_lexer_classifies_simple_numeric_literals_across_whitespace_boundaries(
    literal, expected_type, prefix, suffix
):
    tokenised = Lexer(prefix + literal + suffix).tokenise()

    assert tokenised[0].type == expected_type
    if expected_type == tokens.TokenType.INTEGER:
        assert tokenised[0].value == int(literal)
    else:
        assert tokenised[0].value == pytest.approx(float(literal))
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


NUMERIC_DECLARATION_CASES = tuple(
    ("caint", literal, "value") for literal in SIMPLE_INTEGER_LITERALS
) + tuple(("cdml", literal, "value") for literal in SIMPLE_FLOAT_LITERALS)


@pytest.mark.parametrize("datatype, literal, name", NUMERIC_DECLARATION_CASES)
def test_parser_builds_numeric_literal_declarations(datatype, literal, name):
    program = Parser(
        Lexer(f"$MEM-GC\nval {datatype} {name} = {literal}.").tokenise()
    ).parse()

    declaration = program.statements[0]
    assert isinstance(declaration, ast.DeclareVariable)
    assert declaration.identifier == name
    assert declaration.datatype.name == datatype
    assert isinstance(declaration.value, ast.Literal)
    if datatype == "caint":
        assert declaration.value.value == int(literal)
    else:
        assert declaration.value.value == pytest.approx(float(literal))
