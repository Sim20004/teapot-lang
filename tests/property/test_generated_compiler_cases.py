import itertools
import string

import pytest

import teapot.teapot_ast as ast
from teapot import tokens
from teapot.lexer import Lexer
from teapot.parser import Parser

RESERVED_WORDS = (
    set(tokens.KEYWORDS) | set(tokens.TYPE_KEYWORDS) | set(tokens.BOOLEAN_LITERALS)
)


def _generated_simple_identifiers():
    starts = string.ascii_letters + "_"
    continues = string.ascii_letters + string.digits + "_"
    for start in starts:
        if start not in RESERVED_WORDS:
            yield start
        for cont in continues:
            name = start + cont
            if name not in RESERVED_WORDS:
                yield name


SIMPLE_IDENTIFIERS = tuple(_generated_simple_identifiers())

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


@pytest.mark.parametrize("name", SIMPLE_IDENTIFIERS)
def test_lexer_classifies_generated_simple_identifiers(name):
    for prefix, suffix in (("", ""), (" ", " "), ("\n", "\t")):
        tokenised = Lexer(prefix + name + suffix).tokenise()

        assert tokenised[0].type == tokens.TokenType.IDENTIFIER
        assert tokenised[0].value == name
        assert tokenised[-1].type == tokens.TokenType.EOF


@pytest.mark.parametrize("name", SIMPLE_IDENTIFIERS)
def test_parser_accepts_generated_simple_identifier_names(name):
    program = Parser(Lexer(f"$MEM-GC\nval aint {name} = 1.").tokenise()).parse()

    declaration = program.statements[0]
    assert isinstance(declaration, ast.DeclareVariable)
    assert declaration.identifier == name
    assert declaration.datatype.name == "aint"
    assert declaration.value is not None
