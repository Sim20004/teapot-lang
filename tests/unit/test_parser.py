from teapot.parser import Parser
from teapot.parser import ParserError
from teapot.lexer import Lexer
import teapot.teapot_ast as ast
import teapot.tokens as tokens
from teapot.tokens import Token
import pytest

def lex(source):
    lexer = Lexer(source)
    tokens = lexer.tokenise()
    return tokens

def test_parser_init():
    tokens = lex("$MEM-GC")
    program = Parser(tokens).parse()
    assert program.statements == []
    assert program.memory_mode == "$MEM-GC"

def test_datatype_mutability():
    tokens_list = lex("""
    $MEM-GC

    val mstr foo = "foo".
    val cstr bar = "bar".

    val mbln baz = true.
    val cbln qux = false.

    val mchar quux.
    val cchar corge.

    val msi8 grault = 8.
    val csi8 garply = 8.

    val msi16 waldo = 16.
    val csi16 fred = 16.

    val msi32 plugh = 32.
    val csi32 xyzzy = 32.

    val msi64 thud = 64.
    val csi64 foo2 = 64.

    val mui8 bar2 = 8.
    val cui8 baz2 = 8.

    val mui16 qux2 = 16.
    val cui16 quux2 = 16.

    val mui32 corge2 = 32.
    val cui32 grault2 = 32.

    val mui64 garply2 = 64.
    val cui64 waldo2 = 64.

    val maint fred2 = 100.
    val caint plugh2 = 100.

    val mf32 xyzzy2 = 3.14.
    val cf32 thud2 = 3.14.

    val mf64 foo3 = 3.14159.
    val cf64 bar3 = 3.14159.

    val mdml baz3 = 2.5.
    val cdml qux3 = 2.5.

    val void quux3.
    """)

    program = Parser(tokens_list).parse()

    expected = [
        ("mstr", True),
        ("cstr", False),
        ("mbln", True),
        ("cbln", False),
        ("mchar", True),
        ("cchar", False),
        ("msi8", True),
        ("csi8", False),
        ("msi16", True),
        ("csi16", False),
        ("msi32", True),
        ("csi32", False),
        ("msi64", True),
        ("csi64", False),
        ("mui8", True),
        ("cui8", False),
        ("mui16", True),
        ("cui16", False),
        ("mui32", True),
        ("cui32", False),
        ("mui64", True),
        ("cui64", False),
        ("maint", True),
        ("caint", False),
        ("mf32", True),
        ("cf32", False),
        ("mf64", True),
        ("cf64", False),
        ("mdml", True),
        ("cdml", False),
        ("void", False),
    ]

    assert len(program.statements) == len(expected)

    for statement, (datatype, mutable) in zip(program.statements, expected):
        assert isinstance(statement, ast.DeclareVariable)
        assert statement.datatype.name == datatype
        assert statement.datatype.mutable is mutable

def test_current_token():
    tokens_list = lex("$MEM-GC")
    parser = Parser(tokens_list)

    assert parser.current_token() is tokens_list[0]
    assert parser.current_token().type == tokens.TokenType.DIRECTIVE
    assert parser.current_token().value == "$MEM-GC"

def test_current_token_at_eof():
    tokens_list = lex("$MEM-GC")
    parser = Parser(tokens_list)
    parser.parse()

    assert parser.current_token().type == tokens.TokenType.EOF

def test_at_end():
    tokens_list = lex("$MEM-GC")
    parser = Parser(tokens_list)

    assert not parser.at_end()

    parser.parse()

    assert not parser.at_end()
    assert parser.current_token().type == tokens.TokenType.EOF

def test_advance():
    tokens_list = lex("$MEM-GC\nval mui8 foo = 8")
    parser = Parser(tokens_list)

    assert parser.advance().type == tokens.TokenType.DIRECTIVE
    assert parser.advance().type == tokens.TokenType.VAL
    assert parser.advance().type == tokens.TokenType.TYPE
    assert parser.advance().type == tokens.TokenType.IDENTIFIER
    assert parser.advance().type == tokens.TokenType.ASSIGN
    assert parser.advance().type == tokens.TokenType.INTEGER

def test_advance_at_eof():
    tokens_list = lex("$MEM-GC\nval mui8 foo = 8.")
    parser = Parser(tokens_list)
    parser.parse()

    assert parser.advance().type == tokens.TokenType.EOF

def test_memory_directive_gc():
    tokens_list = lex("$MEM-GC")
    parser = Parser(tokens_list)
    program = parser.parse()

    assert program.memory_mode == "$MEM-GC"

def test_memory_directive_manual():
    tokens_list = lex("$MEM-MANUAL")
    parser = Parser(tokens_list)
    program = parser.parse()

    assert program.memory_mode == "$MEM-MANUAL"

def test_missing_directive():
    tokens_list = lex("val mui8 foo = 8.")
    parser = Parser(tokens_list)

    with pytest.raises(ParserError):
        program = parser.parse()

def test_mutable_datatype():
    tokens_list = lex("$MEM-GC\nval cui16 foo = 16.")

    program = Parser(tokens_list).parse()

    statement = program.statements[0]

    assert isinstance(statement, ast.DeclareVariable)
    assert statement.datatype.name == "cui16"
    assert statement.datatype.mutable is False