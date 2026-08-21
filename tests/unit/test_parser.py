from pytest import raises

import teapot.teapot_ast as ast
from teapot import tokens
from teapot.lexer import Lexer
from teapot.parser import Parser, ParserError


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
    tokens_list = lex("$MEM-GC\nsct Foo {    mui8 bar.    cstr baz.}")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert statement.identifier == "Foo"
    assert statement.body[0].datatype.name == "mui8"
    assert statement.body[0].datatype.mutable is True
    assert statement.body[0].identifier == "bar"
    assert statement.body[1].datatype.name == "cstr"
    assert statement.body[1].datatype.mutable is False
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


# Function declaration must produce valid AST
def test_function_declaration():
    tokens_list = lex("$MEM-GC\nfc foo()!void { val mui8 foo = 8. }")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement, ast.Function)
    assert statement.name == "foo"
    assert statement.body[0].datatype.name == "mui8"
    assert statement.body[0].datatype.mutable is True
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
    tokens_list = lex(
        "$MEM-GC\nfc foo(mui8[] bar, cstr baz)!void { val mui8 qux = 8. }"
    )
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement.arguments[0].datatype, ast.ArrayType)
    assert statement.arguments[0].datatype.datatype == "mui8"
    assert statement.arguments[0].identifier == "bar"


# Default function arguments must produce valid AST
def test_function_default_arg():
    tokens_list = lex(
        "$MEM-GC\nfc foo(mui8 bar=8, cstr baz)!void { val mui8 qux = 8. }"
    )
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert statement.arguments[0].datatype == "mui8"
    assert statement.arguments[0].default.value == 8
    assert statement.arguments[0].identifier == "bar"


# Built-in and user-defined return types produce valid AST
def test_return_type():
    tokens_list = lex(
        "$MEM-GC\nfc foo(mui8 bar, cstr baz)!void { val mui8 qux = 8. val Quux corge = Quux(). exit qux.}"
    )
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert statement.body[2].value.name == "qux"

    tokens_list = lex(
        "$MEM-GC\nfc foo(mui8 bar, cstr baz)!void { val mui8 qux = 8. val Quux corge = Quux(). exit quux.}"
    )
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert statement.body[2].value.name == "quux"


# Public functions are parsed correctly
def test_public_function():
    tokens_list = lex("$MEM-GC\npub fc foo()!void { exit 1. }")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert statement.public is True


# Missing function closing parenthesis must raise ParserError
def test_function_parenthesis_missing():
    tokens_list = lex("$MEM-GC\npub fc foo(!void { exit 1. }")

    with raises(ParserError):
        Parser(tokens_list).parse()


# Missing function closing brace must raise ParserError
def test_missing_function_closing_brace():
    tokens_list = lex("$MEM-GC\npub fc foo()!void { exit 1.")

    with raises(ParserError):
        Parser(tokens_list).parse()


# Operator declaration must be parsed correctly
def test_operator_declaration():
    tokens_list = lex("$MEM-GC\noperator foo(mui8 bar, mui8 baz)!cui8 { exit 8. }")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert statement.symbol == "foo"
    assert statement.arguments[0].datatype.value == "mui8"
    assert statement.arguments[0].name.value == "bar"
    assert statement.arguments[1].datatype.value == "mui8"
    assert statement.arguments[1].name.value == "baz"
    assert statement.return_type.value == "cui8"
    assert statement.body[0].value.value == 8


# Operator declaration must be parsed correctly where the name is a symbol
def test_operator_declaration_with_symbol():
    tokens_list = lex("$MEM-GC\noperator +(mui8 foo, mui8 bar)!cui8 { exit 8. }")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert statement.symbol == "+"
    assert statement.arguments[0].datatype.value == "mui8"
    assert statement.arguments[0].name.value == "foo"
    assert statement.arguments[1].datatype.value == "mui8"
    assert statement.arguments[1].name.value == "bar"
    assert statement.return_type.value == "cui8"
    assert statement.body[0].value.value == 8


# Public operator declaration must be parsed correctly
def test_public_operator_declaration():
    tokens_list = lex("$MEM-GC\npub operator foo(mui8 bar, mui8 baz)!cui8 { exit 8. }")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert statement.symbol == "foo"
    assert statement.public is True
    assert statement.arguments[0].datatype.value == "mui8"
    assert statement.arguments[0].name.value == "bar"
    assert statement.arguments[1].datatype.value == "mui8"
    assert statement.arguments[1].name.value == "baz"
    assert statement.return_type.value == "cui8"
    assert statement.body[0].value.value == 8


# Missing return period raises ParserError
def test_missing_return_period():
    tokens_list = lex("$MEM-GC\nfc foo()!void { exit 1 }")
    with raises(ParserError):
        Parser(tokens_list).parse()


# If statements produce valid AST
def test_if_statement():
    tokens_list = lex("$MEM-GC\nif (1 == 1) { val mui8 foo = 8. }")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement, ast.If)
    assert statement.condition.left.value == 1
    assert statement.condition.operator == "=="
    assert statement.condition.right.value == 1

    assert isinstance(statement.body[0], ast.DeclareVariable)
    assert statement.body[0].datatype.name == "mui8"
    assert statement.body[0].identifier == "foo"
    assert statement.body[0].value.value == 8


# If statements produce valid AST with elif
def test_if_elif():
    tokens_list = lex(
        "$MEM-GC\nif (1 == 1) { val mui8 foo = 8. } elif (2 == 2) { val mui8 foo = 9. }"
    )
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement, ast.If)
    assert statement.condition.left.value == 1
    assert statement.condition.operator == "=="
    assert statement.condition.right.value == 1

    assert isinstance(statement.body[0], ast.DeclareVariable)
    assert statement.body[0].datatype.name == "mui8"
    assert statement.body[0].identifier == "foo"
    assert statement.body[0].value.value == 8

    assert isinstance(statement.elifs[0], ast.Elif)
    assert statement.elifs[0].condition.left.value == 2
    assert statement.elifs[0].condition.operator == "=="
    assert statement.elifs[0].condition.right.value == 2

    assert isinstance(statement.elifs[0].body[0], ast.DeclareVariable)
    assert statement.elifs[0].body[0].datatype.name == "mui8"
    assert statement.elifs[0].body[0].identifier == "foo"
    assert statement.elifs[0].body[0].value.value == 9


# If statements produce valid AST with multiple elifs
def test_if_multiple_elif():
    tokens_list = lex(
        "$MEM-GC\nif (1 == 1) { val mui8 foo = 8. } elif (2 == 2) { val mui8 foo = 9. } elif (3 == 3) { val mui8 foo = 10. }"
    )
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement, ast.If)
    assert statement.condition.left.value == 1
    assert statement.condition.operator == "=="
    assert statement.condition.right.value == 1

    assert isinstance(statement.body[0], ast.DeclareVariable)
    assert statement.body[0].datatype.name == "mui8"
    assert statement.body[0].identifier == "foo"
    assert statement.body[0].value.value == 8

    assert isinstance(statement.elifs[0], ast.Elif)
    assert statement.elifs[0].condition.left.value == 2
    assert statement.elifs[0].condition.operator == "=="
    assert statement.elifs[0].condition.right.value == 2

    assert isinstance(statement.elifs[0].body[0], ast.DeclareVariable)
    assert statement.elifs[0].body[0].datatype.name == "mui8"
    assert statement.elifs[0].body[0].identifier == "foo"
    assert statement.elifs[0].body[0].value.value == 9

    assert isinstance(statement.elifs[0], ast.Elif)
    assert statement.elifs[1].condition.left.value == 3
    assert statement.elifs[1].condition.operator == "=="
    assert statement.elifs[1].condition.right.value == 3

    assert isinstance(statement.elifs[0].body[0], ast.DeclareVariable)
    assert statement.elifs[1].body[0].datatype.name == "mui8"
    assert statement.elifs[1].body[0].identifier == "foo"
    assert statement.elifs[1].body[0].value.value == 10


# If statements produce valid AST with else
def test_if_else():
    tokens_list = lex(
        "$MEM-GC\nif (1 == 1) { val mui8 foo = 8. } else { val mui8 foo = 9. }"
    )
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement, ast.If)
    assert statement.condition.left.value == 1
    assert statement.condition.operator == "=="
    assert statement.condition.right.value == 1

    assert isinstance(statement.body[0], ast.DeclareVariable)
    assert statement.body[0].datatype.name == "mui8"
    assert statement.body[0].identifier == "foo"
    assert statement.body[0].value.value == 8

    assert isinstance(statement.else_body, ast.Else)
    assert isinstance(statement.else_body.body[0], ast.DeclareVariable)
    assert statement.else_body.body[0].datatype.name == "mui8"
    assert statement.else_body.body[0].identifier == "foo"
    assert statement.else_body.body[0].value.value == 9


# If-elif-else statements produce valid AST
def test_if_elif_else():
    tokens_list = lex(
        "$MEM-GC\nif (1 == 1) { val mui8 foo = 8. } elif (2 == 2) { val mui8 foo = 9. } else { val mui8 foo = 10. }"
    )
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement, ast.If)
    assert statement.condition.left.value == 1
    assert statement.condition.operator == "=="
    assert statement.condition.right.value == 1

    assert isinstance(statement.body[0], ast.DeclareVariable)
    assert statement.body[0].datatype.name == "mui8"
    assert statement.body[0].identifier == "foo"
    assert statement.body[0].value.value == 8

    assert isinstance(statement.elifs[0], ast.Elif)
    assert statement.elifs[0].condition.left.value == 2
    assert statement.elifs[0].condition.operator == "=="
    assert statement.elifs[0].condition.right.value == 2

    assert isinstance(statement.elifs[0].body[0], ast.DeclareVariable)
    assert statement.elifs[0].body[0].datatype.name == "mui8"
    assert statement.elifs[0].body[0].identifier == "foo"
    assert statement.elifs[0].body[0].value.value == 9

    assert isinstance(statement.else_body, ast.Else)
    assert isinstance(statement.else_body.body[0], ast.DeclareVariable)
    assert statement.else_body.body[0].datatype.name == "mui8"
    assert statement.else_body.body[0].identifier == "foo"
    assert statement.else_body.body[0].value.value == 10


# Missing if parenthesis raise ParserError
def test_missing_if_close_parenthesis():
    tokens_list = lex("$MEM-GC\nif (1 == 1 { val mui8 foo = 8. }")
    with raises(ParserError):
        Parser(tokens_list).parse()


# Missing if body raises ParserError
def test_missing_if_body():
    tokens_list = lex("$MEM-GC\nif (1 == 1)")
    with raises(ParserError):
        Parser(tokens_list).parse()


# While loop produces valid AST
def test_while_loop():
    tokens_list = lex("$MEM-GC\nwhile (1 == 1) { val mui8 foo = 8. }")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement, ast.While)
    assert statement.condition.left.value == 1
    assert statement.condition.operator == "=="
    assert statement.condition.right.value == 1
    assert isinstance(statement.body[0], ast.DeclareVariable)
    assert statement.body[0].datatype.name == "mui8"
    assert statement.body[0].identifier == "foo"
    assert statement.body[0].value.value == 8


# While loop with complex condition produces valid AST
def test_while_complex_condition():
    tokens_list = lex("$MEM-GC\nwhile (1 > 10 && 2 ~= 0) { val mui8 foo = 8. }")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement, ast.While)
    assert statement.condition.left.left.value == 1
    assert statement.condition.left.operator == ">"
    assert statement.condition.left.right.value == 10
    assert statement.condition.operator == "&&"
    assert statement.condition.right.left.value == 2
    assert statement.condition.right.operator == "~="
    assert statement.condition.right.right.value == 0

    assert isinstance(statement.body[0], ast.DeclareVariable)
    assert statement.body[0].datatype.name == "mui8"
    assert statement.body[0].identifier == "foo"
    assert statement.body[0].value.value == 8


# While loop with missing closing parenthesis raises ParserError
def test_while_missing_close_paren():
    tokens_list = lex("$MEM-GC\nwhile (1 > 10 { val mui8 foo = 8. }")
    with raises(ParserError):
        Parser(tokens_list).parse()


# While loop with missing body raises ParserError
def test_while_missing_body():
    tokens_list = lex("$MEM-GC\nwhile (1 > 10)")
    with raises(ParserError):
        Parser(tokens_list).parse()


# For loop produces valid AST
def test_for_loop():
    tokens_list = lex("$MEM-GC\nfor (foo : bar) { val mui8 foo = 8. }")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement, ast.For)
    assert statement.variable == "foo"
    assert statement.iterable.name == "bar"
    assert isinstance(statement.body[0], ast.DeclareVariable)
    assert statement.body[0].datatype.name == "mui8"
    assert statement.body[0].identifier == "foo"
    assert statement.body[0].value.value == 8


# For loop produces valid AST when the iterable is an expression
def test_for_iterable_expression():
    tokens_list = lex("$MEM-GC\nfor (foo : 4 + 10) { val mui8 foo = 8. }")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement, ast.For)
    assert statement.variable == "foo"
    assert statement.iterable.left.value == 4
    assert statement.iterable.operator == "+"
    assert statement.iterable.right.value == 10
    assert isinstance(statement.body[0], ast.DeclareVariable)
    assert statement.body[0].datatype.name == "mui8"
    assert statement.body[0].identifier == "foo"
    assert statement.body[0].value.value == 8


# For loop with missing colon raises ParserError
def test_for_missing_colon():
    tokens_list = lex("$MEM-GC\nfor (foo  bar) { val mui8 foo = 8. }")
    with raises(ParserError):
        Parser(tokens_list).parse()


# For loop with missing closing parenthesis raises ParserError
def test_for_missing_close_paren():
    tokens_list = lex("$MEM-GC\nfor (foo : bar { val mui8 foo = 8. }")
    with raises(ParserError):
        Parser(tokens_list).parse()


# For loop with empty block produces False when checking the truthiness of body
def test_for_empty_block():
    tokens_list = lex("$MEM-GC\nfor (foo : bar) { }")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement, ast.For)
    assert statement.variable == "foo"
    assert statement.iterable.name == "bar"
    assert not statement.body


# For loop with multiple statements is parsed correctly in source order
def test_for_multiple_statements_in_block():
    tokens_list = lex(
        "$MEM-GC\nfor (foo : bar) { val mui8 baz = 1. val mui8 qux = 2. val mui8 quux = 3. }"
    )
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement, ast.For)
    assert statement.variable == "foo"
    assert statement.iterable.name == "bar"

    assert isinstance(statement.body[0], ast.DeclareVariable)
    assert statement.body[0].datatype.name == "mui8"
    assert statement.body[0].identifier == "baz"
    assert statement.body[0].value.value == 1

    assert isinstance(statement.body[1], ast.DeclareVariable)
    assert statement.body[1].datatype.name == "mui8"
    assert statement.body[1].identifier == "qux"
    assert statement.body[1].value.value == 2

    assert isinstance(statement.body[2], ast.DeclareVariable)
    assert statement.body[2].datatype.name == "mui8"
    assert statement.body[2].identifier == "quux"
    assert statement.body[2].value.value == 3


# Nested blocks must produce correct AST
def test_nested_blocks():
    tokens_list = lex("$MEM-GC\nfc foo()!void { fc bar()!void { fc baz()!void { } } }")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement, ast.Function)
    assert statement.name == "foo"
    assert statement.return_type == "void"

    assert isinstance(statement.body[0], ast.Function)
    assert statement.body[0].name == "bar"
    assert statement.body[0].return_type == "void"

    assert isinstance(statement.body[0].body[0], ast.Function)
    assert statement.body[0].body[0].name == "baz"
    assert statement.body[0].body[0].return_type == "void"


# Public variables must be rejected
def test_public_variable():
    tokens_list = lex("$MEM-GC\npub val mui8 foo = 1.")
    with raises(ParserError):
        Parser(tokens_list).parse()


# Public ifs must be rejected
def test_public_if():
    tokens_list = lex("$MEM-GC\npub if (1 == 1) { }")
    with raises(ParserError):
        Parser(tokens_list).parse()


# Public while loops must be rejected
def test_public_while():
    tokens_list = lex("$MEM-GC\npub while (1 == 1) { }")
    with raises(ParserError):
        Parser(tokens_list).parse()


# Public for loops must be rejected
def test_public_for():
    tokens_list = lex("$MEM-GC\npub for (foo : bar) { }")
    with raises(ParserError):
        Parser(tokens_list).parse()


# Public exits must be rejected
def test_public_exit():
    tokens_list = lex("$MEM-GC\nfc foo()!void { pub exit 1. }")
    with raises(ParserError):
        Parser(tokens_list).parse()


# Assignment produces valid AST
def test_assignment():
    tokens_list = lex("$MEM-GC\nfoo = 4.")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert statement.target.name == "foo"
    assert statement.operator.value == "="
    assert statement.value.value == 4


# Compound assignment produces valid AST
def test_compound_assignment():
    tokens_list = lex("$MEM-GC\nfoo += 4.")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert statement.target.name == "foo"
    assert statement.operator.value == "+="
    assert statement.value.value == 4

    tokens_list = lex("$MEM-GC\nfoo -= 4.")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert statement.target.name == "foo"
    assert statement.operator.value == "-="
    assert statement.value.value == 4

    tokens_list = lex("$MEM-GC\nfoo *= 4.")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert statement.target.name == "foo"
    assert statement.operator.value == "*="
    assert statement.value.value == 4

    tokens_list = lex("$MEM-GC\nfoo /= 4.")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert statement.target.name == "foo"
    assert statement.operator.value == "/="
    assert statement.value.value == 4


# Member assignment produces valid AST
def test_member_assignment():
    tokens_list = lex("$MEM-GC\nfoo::bar = 4.")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert statement.target.obj.name == "foo"
    assert statement.target.member == "bar"
    assert statement.operator.value == "="
    assert statement.value.value == 4


# Invalid assignment operator raises ParserError
def test_invalid_assignment_operator():
    tokens_list = lex("$MEM-GC\nfoo .= 4.")
    with raises(ParserError):
        Parser(tokens_list).parse()


# Missing assignment terminator period raises ParserError
def test_missing_assignment_period():
    tokens_list = lex("$MEM-GC\nfoo = 4")
    with raises(ParserError):
        Parser(tokens_list).parse()


# Integer literal produces valid AST
def test_integer_literal():
    tokens_list = lex("$MEM-GC\nfoo = 4.")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement.value, ast.Literal)
    assert statement.value.value == 4


# Float literal produces valid AST
def test_float_literal():
    tokens_list = lex("$MEM-GC\nfoo = 4.3.")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement.value, ast.Literal)
    assert statement.value.value == 4.3


# Boolean literal produces valid AST
def test_boolean_literal():
    tokens_list = lex("$MEM-GC\nfoo = true.")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement.value, ast.Literal)
    assert statement.value.value is True


# String literal produces valid AST
def test_string_literal():
    tokens_list = lex('$MEM-GC\nfoo = "Bar".')
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement.value, ast.Literal)
    assert statement.value.value == "Bar"


# Identifiers produce ast.Identifier
def test_identifier_expression():
    tokens_list = lex("$MEM-GC\nval mbln foo = bar && baz.")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert statement.value.left.name == "bar"
    assert statement.value.operator == "&&"
    assert statement.value.right.name == "baz"


# Negative integer literal produces valid AST
def test_negative_integer():
    tokens_list = lex("$MEM-GC\nfoo = -4.")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement.value, ast.Literal)
    assert statement.value.value == -4


# Negative float literal produces valid AST
def test_negative_float():
    tokens_list = lex("$MEM-GC\nfoo = -4.3.")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement.value, ast.Literal)
    assert statement.value.value == -4.3


# Parenthesised expressions produce the correct AST nesting
def test_parenthesised_expression():
    tokens_list = lex("$MEM-GC\nfoo = (((3 + 4) * 8) == 8) && (((1 * 4) + 3) == 9).")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert statement.value.left.left.left.left.value == 3
    assert statement.value.left.left.left.right.value == 4
    assert statement.value.left.left.operator == "*"
    assert statement.value.left.left.right.value == 8
    assert statement.value.left.operator == "=="
    assert statement.value.left.right.value == 8
    assert statement.value.operator == "&&"
    assert statement.value.right.left.left.left.value == 1
    assert statement.value.right.left.left.operator == "*"
    assert statement.value.right.left.left.right.value == 4
    assert statement.value.right.left.operator == "+"
    assert statement.value.right.left.right.value == 3
    assert statement.value.right.operator == "=="
    assert statement.value.right.right.value == 9


# Array literals produce the correct ast.ArrayLiteral
def test_array_literal():
    tokens_list = lex("$MEM-GC\nval mui8[] foo = [1, 2, 3, 4].")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement.value, ast.ArrayLiteral)
    assert statement.value.values[0].value == 1
    assert statement.value.values[1].value == 2
    assert statement.value.values[2].value == 3
    assert statement.value.values[3].value == 4


# Empty literals produce the correct ast.ArrayLiteral with empty values[]
def test_empty_array_literal():
    tokens_list = lex("$MEM-GC\nval mui8[] foo = [].")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement.value, ast.ArrayLiteral)
    assert not statement.value.values


# Unary not produces correct ast.UnaryExpression
def test_unary_not():
    tokens_list = lex("$MEM-GC\nval mbln foo = ~bar.")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement.value, ast.UnaryExpression)
    assert statement.value.value.name == "bar"
    assert statement.value.operator == "~"


# Function calls must produce correct ast.CallExpression
def test_function_call():
    tokens_list = lex("$MEM-GC\nval mui8 foo = bar(3, 4).")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement.value, ast.CallExpression)
    assert statement.value.callee.name == "bar"
    assert statement.value.arguments[0].value == 3
    assert statement.value.arguments[1].value == 4


# Empty function calls must produce correct ast.CallExpression
def test_empty_function_call():
    tokens_list = lex("$MEM-GC\nval mui8 foo = bar().")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement.value, ast.CallExpression)
    assert statement.value.callee.name == "bar"
    assert not statement.value.arguments


# Chained member access creates correct nested ast.MemberAccess
def test_chained_member_access():
    tokens_list = lex("$MEM-GC\nfoo::bar::baz::qux::quux::corge = 1.")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement.target, ast.MemberAccess)
    assert isinstance(statement.target.obj, ast.MemberAccess)
    assert isinstance(statement.target.obj.obj, ast.MemberAccess)
    assert isinstance(statement.target.obj.obj.obj, ast.MemberAccess)
    assert isinstance(statement.target.obj.obj.obj.obj, ast.MemberAccess)
    assert statement.target.member == "corge"
    assert statement.target.obj.member == "quux"
    assert statement.target.obj.obj.member == "qux"
    assert statement.target.obj.obj.obj.member == "baz"
    assert statement.target.obj.obj.obj.obj.member == "bar"
    assert statement.target.obj.obj.obj.obj.obj.name == "foo"


# Casting produces correct ast.Cast
def test_cast():
    tokens_list = lex("$MEM-GC\nval mstr foo = 4 >> mstr.")
    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement.value, ast.Cast)
    assert statement.value.expression.value == 4
    assert statement.value.datatype == "mstr"


# Operator precedence and associativity are parsed correctly
def test_precedence():
    tokens_list = lex(
        "$MEM-GC\n"
        "foo = (((2 + 3) * 4) ** 2 == 400) && "
        "((10 - 3 * 2) == 4) || "
        "((20 - 5 - 3) == 12)."
    )

    statement = Parser(tokens_list).parse().statements[0]

    assert isinstance(statement.value, ast.BinaryExpression)
    assert statement.value.operator == "||"

    # && has higher precedence than ||
    logical_and = statement.value.left

    assert isinstance(logical_and, ast.BinaryExpression)
    assert logical_and.operator == "&&"

    # == has higher precedence than &&
    first_comparison = logical_and.left

    assert isinstance(first_comparison, ast.BinaryExpression)
    assert first_comparison.operator == "=="

    # ** has higher precedence than ==
    power = first_comparison.left

    assert isinstance(power, ast.BinaryExpression)
    assert power.operator == "**"
    assert power.right.value == 2

    # * has higher precedence than **
    multiplication = power.left

    assert isinstance(multiplication, ast.BinaryExpression)
    assert multiplication.operator == "*"
    assert multiplication.right.value == 4

    # Parentheses force 2 + 3 to be evaluated first
    addition = multiplication.left

    assert isinstance(addition, ast.BinaryExpression)
    assert addition.operator == "+"
    assert addition.left.value == 2
    assert addition.right.value == 3

    assert first_comparison.right.value == 400

    # * has higher precedence than -
    second_comparison = logical_and.right

    assert isinstance(second_comparison, ast.BinaryExpression)
    assert second_comparison.operator == "=="

    subtraction = second_comparison.left

    assert isinstance(subtraction, ast.BinaryExpression)
    assert subtraction.operator == "-"
    assert subtraction.left.value == 10

    multiplication = subtraction.right

    assert isinstance(multiplication, ast.BinaryExpression)
    assert multiplication.operator == "*"
    assert multiplication.left.value == 3
    assert multiplication.right.value == 2

    assert second_comparison.right.value == 4

    # Equal-precedence subtraction is left-associative:
    # (20 - 5) - 3, rather than 20 - (5 - 3)
    third_comparison = statement.value.right

    assert isinstance(third_comparison, ast.BinaryExpression)
    assert third_comparison.operator == "=="
    assert third_comparison.right.value == 12

    subtraction = third_comparison.left

    assert isinstance(subtraction, ast.BinaryExpression)
    assert subtraction.operator == "-"

    assert isinstance(subtraction.left, ast.BinaryExpression)
    assert subtraction.left.operator == "-"
    assert subtraction.left.left.value == 20
    assert subtraction.left.right.value == 5
    assert subtraction.right.value == 3


def test_call_and_member_access():
    tokens_list = lex("$MEM-GC\nval mui8 foo = bar::baz(3).")

    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement, ast.DeclareVariable)
    assert isinstance(statement.value, ast.CallExpression)

    call = statement.value

    assert isinstance(call.callee, ast.MemberAccess)
    assert call.callee.member == "baz"

    assert isinstance(call.callee.obj, ast.Identifier)
    assert call.callee.obj.name == "bar"

    assert len(call.arguments) == 1
    assert call.arguments[0].value == 3


def test_cast_expression():
    tokens_list = lex("$MEM-GC\nval mui16 foo = bar >> mui16.")

    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement, ast.DeclareVariable)
    assert isinstance(statement.value, ast.Cast)

    assert isinstance(statement.value.expression, ast.Identifier)
    assert statement.value.expression.name == "bar"
    assert statement.value.datatype == "mui16"


def test_member_and_call():
    tokens_list = lex("$MEM-GC\nval mui8 foo = bar::baz::qux(3, 4).")

    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement.value, ast.CallExpression)

    call = statement.value

    assert isinstance(call.callee, ast.MemberAccess)
    assert call.callee.member == "qux"

    assert isinstance(call.callee.obj, ast.MemberAccess)
    assert call.callee.obj.member == "baz"

    assert isinstance(call.callee.obj.obj, ast.Identifier)
    assert call.callee.obj.obj.name == "bar"

    assert len(call.arguments) == 2
    assert call.arguments[0].value == 3
    assert call.arguments[1].value == 4


def test_binary_parentheses():
    tokens_list = lex("$MEM-GC\nval mui8 foo = (2 + 3) * 4.")

    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    expression = statement.value

    assert isinstance(expression, ast.BinaryExpression)
    assert expression.operator == "*"

    assert isinstance(expression.left, ast.BinaryExpression)
    assert expression.left.operator == "+"
    assert expression.left.left.value == 2
    assert expression.left.right.value == 3

    assert expression.right.value == 4


def test_unary_binary_expression():
    tokens_list = lex("$MEM-GC\nval mui8 foo = ~true && false.")

    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    expression = statement.value

    assert isinstance(expression, ast.BinaryExpression)
    assert expression.operator == "&&"

    assert isinstance(expression.left, ast.UnaryExpression)
    assert expression.left.operator == "~"
    assert expression.left.value.value is True

    assert expression.right.value is False


def test_unexpected_eof():
    tokens_list = lex("$MEM-GC\nval mui8 foo = (3 + 4")

    with raises(ParserError):
        Parser(tokens_list).parse()


def test_unexpected_token():
    tokens_list = lex("$MEM-GC\nval mui8 foo = 3 + * 4.")

    with raises(ParserError):
        Parser(tokens_list).parse()


def test_invalid_statement():
    tokens_list = lex("$MEM-GC\n123.")

    with raises(ParserError):
        Parser(tokens_list).parse()


def test_parser_error_position():
    tokens_list = lex("$MEM-GC\nval mui8 foo = 3 + * 4.")

    parser = Parser(tokens_list)

    with raises(ParserError) as error:
        parser.parse()

    assert error.value.position is not None
    assert error.value.position >= 0


def test_parser_error_token():
    tokens_list = lex("$MEM-GC\nval mui8 foo = 3 + * 4.")

    parser = Parser(tokens_list)

    with raises(ParserError) as error:
        parser.parse()

    assert error.value.token is not None
    assert isinstance(error.value.token, tokens.Token)


def test_lexer_to_parser():
    tokens_list = Lexer("$MEM-GC\nval mui8 foo = 3 + 4.").tokenise()

    program = Parser(tokens_list).parse()

    assert program.memory_mode == "$MEM-GC"
    assert len(program.statements) == 1

    statement = program.statements[0]

    assert isinstance(statement, ast.DeclareVariable)
    assert statement.identifier == "foo"
    assert statement.datatype.name == "mui8"

    assert isinstance(statement.value, ast.BinaryExpression)
    assert statement.value.operator == "+"
    assert statement.value.left.value == 3
    assert statement.value.right.value == 4


def test_complete_valid_program():
    tokens_list = lex(
        "$MEM-GC\n"
        "val mui8 foo = 3.\n"
        "val mui8 bar = foo + 4.\n"
        "sct Example {\n"
        "    mui8 value.\n"
        "}\n"
        "enm Status {\n"
        "    Ready.\n"
        "    Done.\n"
        "}"
    )

    program = Parser(tokens_list).parse()

    assert program.memory_mode == "$MEM-GC"
    assert len(program.statements) == 4

    declaration = program.statements[0]

    assert isinstance(declaration, ast.DeclareVariable)
    assert declaration.identifier == "foo"
    assert declaration.value.value == 3

    declaration = program.statements[1]

    assert isinstance(declaration, ast.DeclareVariable)
    assert declaration.identifier == "bar"
    assert isinstance(declaration.value, ast.BinaryExpression)
    assert declaration.value.operator == "+"
    assert declaration.value.left.name == "foo"
    assert declaration.value.right.value == 4

    struct = program.statements[2]

    assert isinstance(struct, ast.Struct)
    assert struct.identifier == "Example"
    assert len(struct.body) == 1
    assert struct.body[0].identifier == "value"
    assert struct.body[0].datatype.name == "mui8"

    enum = program.statements[3]

    assert isinstance(enum, ast.Enum)
    assert enum.identifier == "Status"
    assert enum.body[0].name == "Ready"
    assert enum.body[1].name == "Done"


def test_invalid_complete_program():
    tokens_list = lex(
        "$MEM-GC\nval mui8 foo = 3.\nval mui8 bar = 4 + * 2.\nval mui8 baz = 5."
    )

    with raises(ParserError):
        Parser(tokens_list).parse()


def test_ast_regression():
    tokens_list = lex("$MEM-GC\nval mui8 foo = 3 + 4 * 5.")

    program = Parser(tokens_list).parse()
    statement = program.statements[0]

    assert isinstance(statement, ast.DeclareVariable)
    assert statement.identifier == "foo"

    expression = statement.value

    assert isinstance(expression, ast.BinaryExpression)
    assert expression.operator == "+"

    assert expression.left.value == 3

    multiplication = expression.right

    assert isinstance(multiplication, ast.BinaryExpression)
    assert multiplication.operator == "*"
    assert multiplication.left.value == 4
    assert multiplication.right.value == 5
