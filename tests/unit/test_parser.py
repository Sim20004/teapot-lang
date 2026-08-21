from teapot.parser import Parser
from teapot.parser import ParserError
from teapot.lexer import Lexer
import teapot.teapot_ast as ast
import teapot.tokens as tokens
from teapot.tokens import Token
from pytest import raises

# Lex each source snippet through the same entry point used by parser tests.
def lex(source):
    lexer = Lexer(source)
    tokens = lexer.tokenise()
    return tokens

# A valid program starts with a memory-management directive.
def test_parser_init():
    tokens = lex("$MEM-GC")
    program = Parser(tokens).parse()
    assert program.statements == []
    assert program.memory_mode == "$MEM-GC"

# Every datatype prefix controls whether the resulting declaration is mutable.
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

    # Keep the expected mutability contract explicit for all supported types.
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
        # Parsing should preserve both the datatype name and its mutability.
        assert isinstance(statement, ast.DeclareVariable)
        assert statement.datatype.name == datatype
        assert statement.datatype.mutable is mutable

    # The parser exposes the token currently under its cursor.
def test_current_token():
    tokens_list = lex("$MEM-GC")
    parser = Parser(tokens_list)

    assert parser.current_token() is tokens_list[0]
    assert parser.current_token().type == tokens.TokenType.DIRECTIVE
    assert parser.current_token().value == "$MEM-GC"

# Once parsing finishes, the cursor remains positioned at the EOF sentinel.
def test_current_token_at_eof():
    tokens_list = lex("$MEM-GC")
    parser = Parser(tokens_list)
    parser.parse()

    assert parser.current_token().type == tokens.TokenType.EOF

# EOF is not considered an unfinished token stream after a complete parse.
def test_at_end_at_eof():
    tokens_list = lex("$MEM-GC")
    parser = Parser(tokens_list)

    assert not parser.at_end()

    parser.parse()

    # The parser deliberately keeps EOF available for callers to inspect.
    assert not parser.at_end()
    assert parser.current_token().type == tokens.TokenType.EOF

# Advance follows the lexical order of a declaration without parsing it.
def test_advance():
    tokens_list = lex("$MEM-GC\nval mui8 foo = 8")
    parser = Parser(tokens_list)

    assert parser.advance().type == tokens.TokenType.DIRECTIVE
    assert parser.advance().type == tokens.TokenType.VAL
    assert parser.advance().type == tokens.TokenType.TYPE
    assert parser.advance().type == tokens.TokenType.IDENTIFIER
    assert parser.advance().type == tokens.TokenType.ASSIGN
    assert parser.advance().type == tokens.TokenType.INTEGER

# Advancing past the final token is stable and continues to return EOF.
def test_advance_at_eof():
    tokens_list = lex("$MEM-GC\nval mui8 foo = 8.")
    parser = Parser(tokens_list)
    parser.parse()

    assert parser.advance().type == tokens.TokenType.EOF

# Each supported memory directive is copied to the parsed program.
def test_memory_directive_gc():
    tokens_list = lex("$MEM-GC")
    parser = Parser(tokens_list)
    program = parser.parse()

    assert program.memory_mode == "$MEM-GC"

# Manual memory management is accepted as an alternative directive.
def test_memory_directive_manual():
    tokens_list = lex("$MEM-MANUAL")
    parser = Parser(tokens_list)
    program = parser.parse()

    assert program.memory_mode == "$MEM-MANUAL"

# A program without a memory directive is rejected before declarations parse.
def test_missing_directive():
    tokens_list = lex("val mui8 foo = 8.")
    parser = Parser(tokens_list)

    with raises(ParserError):
        parser.parse()

# Mutable declarations retain their mutable datatype metadata.
def test_mutable_datatype():
    tokens_list = lex("$MEM-GC\nval mui16 foo = 16.")

    program = Parser(tokens_list).parse()

    statement = program.statements[0]

    assert isinstance(statement, ast.DeclareVariable)
    assert statement.datatype.name == "mui16"
    assert statement.datatype.mutable is True

# Constant declarations retain their non-mutable datatype metadata.
def test_constant_datatype():
    tokens_list = lex("$MEM-GC\nval cui16 foo = 16.")

    program = Parser(tokens_list).parse()

    statement = program.statements[0]

    assert isinstance(statement, ast.DeclareVariable)
    assert statement.datatype.name == "cui16"
    assert statement.datatype.mutable is False

# Uninitialised variables gets ast.Literal(None)
def test_uninitialised_variable():
    tokens_list = lex("$MEM-GC\nval mui8 foo.")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert statement.value == ast.Literal(None)

# References correctly set the `ref` flag to True
def test_reference_variable():
    tokens_list = lex("$MEM-GC\nval ref mui8 foo = 3.")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert statement.datatype.reference is True

# User-defined datatypes are accepted
def test_user_defined_datatype():
    tokens_list = lex("$MEM-GC\nval Foo bar = Foo().")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert statement.datatype.name == "Foo"

# Array datatype produces the correct ast.ArrayType
def test_array_variable_type():
    tokens_list = lex("$MEM-GC\nval mui8[] foo = [2, 3, 4].")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement.datatype, ast.Type)
    assert isinstance(statement.datatype.name, ast.ArrayType)
    assert statement.datatype.name.datatype == "mui8"

# Array variable can be initialised with values
def test_initialised_array_variable():
    tokens_list = lex("$MEM-GC\nval mui8[] foo = [2, 3, 4].")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement.value, ast.ArrayLiteral)
    assert statement.value.values[0].value == 2
    assert statement.value.values[1].value == 3
    assert statement.value.values[2].value == 4

# A variable without a variable name raises ParserError
def test_missing_variable_name():
    tokens_list = lex("$MEM-GC\n val mui8 = 4")
    with raises(ParserError):
        Parser(tokens_list).parse()

# A variable declaration that is not terminated with a period raises ParserError
def test_missing_declaration_terminator():
    tokens_list = lex("$MEM-GC\nval mui8 foo = 8")
    with raises(ParserError):
        Parser(tokens_list).parse()

# Struct declaration is handled correctly
def test_struct_declaration_handling():
    tokens_list = lex("$MEM-GC\nsct Foo {" \
                      "    mui8 bar." \
                      "    cstr baz." \
                      "}")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert statement.identifier == "Foo"
    assert statement.body[0].datatype.name == "mui8"
    assert statement.body[0].datatype.mutable is True
    assert statement.body[0].identifier == "bar"
    assert statement.body[1].datatype.name == "cstr"
    assert statement.body[1].datatype.mutable == False
    assert statement.body[1].identifier == "baz"

# Empty structs are allowed
def test_empty_struct():
    tokens_list = lex("$MEM-GC\nsct Foo { }")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert statement.identifier == "Foo"
    assert not statement.body

# Struct fields must end with periods
def test_missing_struct_field_terminator():
    tokens_list = lex("$MEM-GC\nsct Foo { mui8 bar }")
    with raises(ParserError):
        Parser(tokens_list).parse()

# Structs must be closed with a closing brace
def test_missing_struct_close_brace():
    tokens_list = lex("$MEM-GC\nsct Foo { mui8 bar.")
    with raises(ParserError):
        Parser(tokens_list).parse()

# Public structs have the public flag set to True
def test_public_struct():
    tokens_list = lex("$MEM-GC\npub sct Foo { mui8 bar. cstr baz. }")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert statement.public is True

# Enums must produce valid AST
def test_enum():
    tokens_list = lex("$MEM-GC\nenm Foo { Bar. Baz. }")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement, ast.Enum)
    assert statement.identifier == "Foo"
    assert statement.body[0].name == "Bar"
    assert statement.body[1].name == "Baz"

# Empty enums must be accepted
def test_empty_enum():
    tokens_list = lex("$MEM-GC\nenm Foo { }")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert not statement.body

# Enum members must be terminated with a period
def test_missing_enum_member_terminator():
    tokens_list = lex("$MEM-GC\nenm Foo { Bar }")
    with raises(ParserError):
        Parser(tokens_list).parse()

# Enums must be closed with a closing brace
def test_missing_enum_close_brace():
    tokens_list = lex("$MEM-GC\nenm Foo { Bar. ")
    with raises(ParserError):
        Parser(tokens_list).parse()

# Public enums have the public flag set to True
def test_public_enum():
    tokens_list = lex("$MEM-GC\npub enm Foo { Bar. Baz. }")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert statement.public is True

# Error declaration must produce correct AST
def test_error_declaration():
    tokens_list = lex("$MEM-GC\nerr Foo { mstr bar. mui8 baz. }")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement, ast.Error)
    assert statement.identifier == "Foo"
    assert statement.body[0].datatype == "mstr"
    assert statement.body[0].name == "bar"
    assert statement.body[1].datatype == "mui8"
    assert statement.body[1].name == "baz"

# Empty error must be accepted
def test_empty_error():
    tokens_list = lex("$MEM-GC\nerr Foo { }")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert not statement.body
    assert statement.identifier == "Foo"

# Invalid Error datatype must raise ParserError
def test_invalid_error_datatype():
    tokens_list = lex("$MEM-GC\nerr Foo { bar baz. }")
    with raises(ParserError):
        Parser(tokens_list).parse()

# Missing Error member terminator must raise ParserError
def test_missing_error_member_terminator():
    tokens_list = lex("$MEM-GC\nerr Foo { mui8 bar }")
    with raises(ParserError):
        Parser(tokens_list).parse()

# Missing Error close brace must raise ParserError
def test_missing_error_close_brace():
    tokens_list = lex("$MEM-GC\nerr Foo { mui8 bar. ")
    with raises(ParserError):
        Parser(tokens_list).parse()

# Public errors have the public flag set to True
def test_public_error():
    tokens_list = lex("$MEM-GC\npub err Foo { mui8 bar. cstr baz. }")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert statement.public is True

# NOT IMPLEMENTED IN PARSER
"""
# Structs can be instantiated with the correct AST
def test_struct_instantiation():
    tokens_list = lex('$MEM-GC\nval Foo bar = Foo(1, "baz").')
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement, ast.DeclareVariable)
    assert isinstance(statement.value, ast.StructInstantiation)
    assert statement.identifier == "bar"
    assert statement.datatype.name == "Foo"
"""

# Function declaration must produce valid AST
def test_function_declaration():
    tokens_list = lex("$MEM-GC\nfc foo()!void { val mui8 foo = 8. }")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement, ast.Function)
    assert statement.name == "foo"
    assert statement.body[0].datatype.name == "mui8"
    assert statement.body[0].datatype.mutable == True
    assert statement.body[0].identifier == "foo"
    assert statement.body[0].value.value == 8

# Function arguments must be valid and in source order
def test_function_args():
    tokens_list = lex("$MEM-GC\nfc foo(mui8 bar, cstr baz)!void { val mui8 qux = 8. }")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert statement.arguments[0].datatype == "mui8"
    assert statement.arguments[0].identifier == "bar"
    assert statement.arguments[1].datatype == "cstr"
    assert statement.arguments[1].identifier == "baz"

# Array function arguments must produce valid AST
def test_function_array_arg():
    tokens_list = lex("$MEM-GC\nfc foo(mui8[] bar, cstr baz)!void { val mui8 qux = 8. }")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement.arguments[0].datatype, ast.ArrayType)
    assert statement.arguments[0].datatype.datatype == "mui8"
    assert statement.arguments[0].identifier == "bar"

# Default function arguments must produce valid AST
def test_function_default_arg():
    tokens_list = lex('$MEM-GC\nfc foo(mui8 bar=8, cstr baz)!void { val mui8 qux = 8. }')
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert statement.arguments[0].datatype == "mui8"
    assert statement.arguments[0].default.value == 8
    assert statement.arguments[0].identifier == "bar"

# Built-in and user-defined return types produce valid AST
def test_return_type():
    tokens_list = lex("$MEM-GC\nfc foo(mui8 bar, cstr baz)!void { val mui8 qux = 8. val Quux corge = Quux(). exit qux.}")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert statement.body[2].value.name == "qux"

    tokens_list = lex("$MEM-GC\nfc foo(mui8 bar, cstr baz)!void { val mui8 qux = 8. val Quux corge = Quux(). exit quux.}")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert statement.body[2].value.name == "quux"

# Public functions are parsed correctly
def test_public_function():
    tokens_list = lex("$MEM-GC\npub fc foo()!void { exit 1. }")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert statement.public == True