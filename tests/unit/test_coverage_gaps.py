import importlib
import runpy
import sys

import pytest

import teapot.teapot_ast as ast
from teapot import lexer
from teapot.debug import print as debug_print
from teapot.errors import TypeMismatchError
from teapot.lexer import Lexer, LexerError
from teapot.main import TeapotError
from teapot.parser import Parser, ParserError, print_ast
from teapot.semantic import SemanticAnalyser, SemanticError, SymbolTable
from teapot.semantic.analyser import analyse
from teapot.semantic.pass1 import SymbolTableBuilder
from teapot.semantic.symbols import Symbol
from teapot.tokens import Token, TokenType
from teapot.web import _scope_name, _serialise


def parse(source):
    return Parser(Lexer(source).tokenise()).parse()


def test_lexer_trace_exercises_dispatch_and_normalisation(monkeypatch, capsys):
    monkeypatch.setattr(lexer, "trace", True)
    tokens = Lexer(
        '$MEM-GC\r\n// comment\nval mstr name = "hello\\nworld". 42 1.25 + >='
    ).tokenise()

    assert [token.type for token in tokens] == [
        TokenType.DIRECTIVE,
        TokenType.VAL,
        TokenType.TYPE,
        TokenType.IDENTIFIER,
        TokenType.ASSIGN,
        TokenType.STRING,
        TokenType.PERIOD,
        TokenType.INTEGER,
        TokenType.FLOAT,
        TokenType.PLUS,
        TokenType.GREATER_EQUAL,
        TokenType.EOF,
    ]
    output = capsys.readouterr().out
    assert "Converted CRLF line endings to LF" in output
    assert "Found comment" in output
    assert "Created token" in output


def test_lexer_direct_cursor_and_trace_branches(monkeypatch, capsys):
    monkeypatch.setattr(lexer, "trace", True)
    scanner = Lexer("a\n")
    assert scanner.current_character() == "a"
    scanner.advance()
    assert scanner.current_character() == "\n"
    scanner.advance()
    assert scanner.current_character() is None
    scanner.advance()
    assert scanner.position == 3
    assert "Reached end of source" in capsys.readouterr().out


def test_lexer_number_and_symbol_errors():
    with pytest.raises(LexerError) as number_error:
        Lexer("1.2.3").tokenise()
    assert number_error.value.line == 1
    assert number_error.value.col == 4

    with pytest.raises(LexerError) as symbol_error:
        Lexer("£").tokenise()
    assert symbol_error.value.col == 1


def test_lexer_trace_without_crlf_and_duplicate_decimal(monkeypatch):
    monkeypatch.setattr(lexer, "trace", True)
    Lexer("true plain").tokenise()
    with pytest.raises(LexerError):
        Lexer("1.2.3").tokenise()


def test_lexer_run_forwards_parser_and_trace(monkeypatch):
    seen = {}

    def fake_parser(tokens, trace):
        seen["tokens"] = tokens
        seen["trace"] = trace
        return "parsed"

    monkeypatch.setattr(lexer, "run_parser", fake_parser)
    assert lexer.run("$MEM-GC", True) == "parsed"
    assert seen["trace"] is True
    assert seen["tokens"][-1].type is TokenType.EOF


def test_parser_trace_and_print_ast(capsys):
    tree = parse("$MEM-GC\nval mui8 value = 1.")
    print_ast(tree)
    output = capsys.readouterr().out
    assert "Program" in output
    assert "memory_mode" in output

    recursive = []
    recursive.append(recursive)
    print_ast(["text", (1,), {"key": True}, {"nested": None}, recursive, object()])
    output = capsys.readouterr().out
    assert "<recursive reference>" in output
    assert "'text'" in output


def test_parser_rejects_invalid_operator_return_type():
    with pytest.raises(ParserError):
        parse("$MEM-GC\noperator foo()!1 {}")


def test_parser_direct_token_error_and_eof_paths():
    parser = Parser([Token(TokenType.DIRECTIVE, "$MEM-GC")])
    parser.position = len(parser.tokens)
    assert parser.current_token().type is TokenType.EOF
    assert parser.advance().type is TokenType.EOF
    with pytest.raises(ParserError):
        parser.expect(TokenType.TYPE)

    with pytest.raises(ParserError):
        Parser(
            [
                Token(TokenType.DIRECTIVE, "$MEM-GC"),
                Token(TokenType.STRUCT, "sct"),
                Token(TokenType.IDENTIFIER, "Record"),
                Token(TokenType.OPEN_BRACE, "{"),
                Token(TokenType.IDENTIFIER, "Unknown"),
            ]
        ).parse()
    with pytest.raises(ParserError):
        Parser(
            [
                Token(TokenType.DIRECTIVE, "$MEM-GC"),
                Token(TokenType.ERROR, "err"),
                Token(TokenType.IDENTIFIER, "Failure"),
                Token(TokenType.OPEN_BRACE, "{"),
                Token(TokenType.IDENTIFIER, "Unknown"),
            ]
        ).parse()


def test_parser_invalid_operator_name_and_argument_type():
    with pytest.raises(ParserError):
        parse("$MEM-GC\noperator !()!void {}")
    with pytest.raises(ParserError):
        parse("$MEM-GC\noperator foo(1 value)!void {}")
    with pytest.raises(ParserError):
        parse("$MEM-GC\noperator foo(mui8 value, 1 other)!void {}")


def test_parser_function_argument_variants_and_invalid_return():
    tree = parse("$MEM-GC\nfc collect(mui8[] values, cstr[] labels)!Result {}")
    assert isinstance(tree.statements[0].arguments[1].datatype, ast.ArrayType)
    assert tree.statements[0].return_type == "Result"
    with pytest.raises(ParserError):
        parse("$MEM-GC\nfc broken()!1 {}")


def test_parser_rejects_unknown_primitive_token():
    with pytest.raises(ParserError):
        Parser(
            [
                Token(TokenType.DIRECTIVE, "$MEM-GC"),
                Token(TokenType.VAL, "val"),
                Token(TokenType.TYPE, "unknown"),
                Token(TokenType.IDENTIFIER, "value"),
                Token(TokenType.PERIOD, "."),
            ]
        ).parse()


def test_parser_struct_error_and_operator_alternative_paths():
    for declaration in [TokenType.STRUCT, TokenType.ERROR]:
        parser = Parser(
            [
                Token(TokenType.DIRECTIVE, "$MEM-GC"),
                Token(declaration, "declaration"),
                Token(TokenType.IDENTIFIER, "Named"),
                Token(TokenType.OPEN_BRACE, "{"),
                Token(TokenType.TYPE, "unknown"),
                Token(TokenType.IDENTIFIER, "field"),
                Token(TokenType.PERIOD, "."),
                Token(TokenType.CLOSE_BRACE, "}"),
            ]
        )
        with pytest.raises(ParserError):
            parser.parse()

    tree = parse("$MEM-GC\noperator foo()!Custom {}")
    assert tree.statements[0].return_type.value == "Custom"


def test_parser_reassignment_helper_success_and_error_paths():
    parser = Parser(
        [
            Token(TokenType.IDENTIFIER, "value"),
            Token(TokenType.ASSIGN_PLUS, "+="),
            Token(TokenType.INTEGER, 2),
            Token(TokenType.PERIOD, "."),
        ]
    )
    assignment = parser.handle_reassignement()
    assert assignment.target.name == "value"
    assert assignment.operator.type is TokenType.ASSIGN_PLUS
    assert assignment.value.value == 2

    parser = Parser(
        [
            Token(TokenType.IDENTIFIER, "value"),
            Token(TokenType.CLOSE_BRACE, "}"),
        ]
    )
    with pytest.raises(ParserError):
        parser.handle_reassignement()


def test_parser_public_identifier_statement_is_rejected():
    with pytest.raises(ParserError):
        parse("$MEM-GC\npub value = 1.")


def test_parser_operator_and_empty_optional_paths():
    tree = parse("$MEM-GC\noperator +(mui8 left, Custom right)!void {}")
    operator = tree.statements[0]
    assert operator.symbol == "+"
    assert [argument.datatype for argument in operator.arguments] == [
        "mui8",
        "Custom",
    ]
    assert operator.return_type.value == "void"

    tree = parse("$MEM-GC\nif (true) {}")
    statement = tree.statements[0]
    assert statement.elifs == []
    assert statement.else_body is None


def test_parser_new_datatypes_and_expression_suffixes():
    parser = Parser(
        [
            Token(TokenType.LIST, "list"),
            Token(TokenType.LESS, "<"),
            Token(TokenType.TYPE, "mui8"),
            Token(TokenType.GREATER, ">"),
        ]
    )
    datatype, user_defined = parser.handle_datatype()
    assert isinstance(datatype, ast.ListType)
    assert user_defined is False
    assert parser.datatype_mutability(datatype) is True

    parser = Parser(
        [
            Token(TokenType.MAP, "map"),
            Token(TokenType.OPEN_BRACKET, "["),
            Token(TokenType.TYPE, "mui8"),
            Token(TokenType.CLOSE_BRACKET, "]"),
            Token(TokenType.TYPE, "mstr"),
        ]
    )
    datatype, user_defined = parser.handle_datatype()
    assert isinstance(datatype, ast.MapType)
    assert user_defined is False
    assert parser.datatype_mutability(datatype) is False

    parser = Parser(
        [
            Token(TokenType.LIST, "list"),
            Token(TokenType.LESS, "<"),
            Token(TokenType.LIST, "list"),
            Token(TokenType.LESS, "<"),
            Token(TokenType.TYPE, "mui8"),
            Token(TokenType.CAST, ">>"),
        ]
    )
    nested, _ = parser.handle_datatype()
    assert isinstance(nested.datatype, ast.ListType)
    assert parser.pending_generic_closes == 0

    with pytest.raises(ParserError):
        Parser([Token(TokenType.PLUS, "+")]).expect_generic_close()

    parser = Parser([Token(TokenType.GREATER, ">")])
    parser.pending_generic_closes = 1
    parser.expect_generic_close()
    assert parser.pending_generic_closes == 0

    parser = Parser(
        [
            Token(TokenType.IDENTIFIER, "items"),
            Token(TokenType.OPEN_BRACKET, "["),
            Token(TokenType.INTEGER, 0),
            Token(TokenType.CLOSE_BRACKET, "]"),
        ]
    )
    indexed = parser.handle_expression()
    assert isinstance(indexed, ast.IndexExpression)

    parser = Parser(
        [
            Token(TokenType.OPEN_PAREN, "("),
            Token(TokenType.OPEN_BRACKET, "["),
            Token(TokenType.STRING, "key"),
            Token(TokenType.COMMA, ","),
            Token(TokenType.INTEGER, 1),
            Token(TokenType.CLOSE_BRACKET, "]"),
            Token(TokenType.CLOSE_PAREN, ")"),
        ]
    )
    map_literal = parser.handle_expression()
    assert isinstance(map_literal, ast.MapLiteral)
    assert map_literal.entries["key"].value == 1

    invalid_map = Parser(
        [
            Token(TokenType.OPEN_PAREN, "("),
            Token(TokenType.OPEN_BRACKET, "["),
            Token(TokenType.IDENTIFIER, "key"),
            Token(TokenType.COMMA, ","),
            Token(TokenType.INTEGER, 1),
            Token(TokenType.CLOSE_BRACKET, "]"),
            Token(TokenType.CLOSE_PAREN, ")"),
        ]
    )
    with pytest.raises(ParserError, match="Map keys must be literals"):
        invalid_map.handle_expression()


def test_parser_struct_array_and_control_flow_helpers():
    parser = Parser(
        [
            Token(TokenType.IDENTIFIER, "Record"),
            Token(TokenType.OPEN_BRACE, "{"),
            Token(TokenType.TYPE, "mui8"),
            Token(TokenType.OPEN_BRACKET, "["),
            Token(TokenType.CLOSE_BRACKET, "]"),
            Token(TokenType.IDENTIFIER, "values"),
            Token(TokenType.PERIOD, "."),
            Token(TokenType.CLOSE_BRACE, "}"),
        ]
    )
    record = parser.handle_struct()
    assert isinstance(record.body[0].datatype.name, ast.ArrayType)

    assert isinstance(
        Parser(
            [Token(TokenType.INTEGER, 1), Token(TokenType.PERIOD, ".")]
        ).handle_free(),
        ast.FreeMemory,
    )
    assert isinstance(Parser([Token(TokenType.PERIOD, ".")]).handle_break(), ast.Break)
    assert isinstance(
        Parser([Token(TokenType.PERIOD, ".")]).handle_continue(), ast.Continue
    )

    do_parser = Parser(
        [
            Token(TokenType.OPEN_BRACE, "{"),
            Token(TokenType.CLOSE_BRACE, "}"),
            Token(TokenType.FAIL, "fail"),
            Token(TokenType.OPEN_PAREN, "("),
            Token(TokenType.IDENTIFIER, "Failure"),
            Token(TokenType.IDENTIFIER, "error"),
            Token(TokenType.CLOSE_PAREN, ")"),
            Token(TokenType.OPEN_BRACE, "{"),
            Token(TokenType.CLOSE_BRACE, "}"),
        ]
    )
    statement = do_parser.handle_do()
    assert statement.fail.error == "Failure"


def test_pass1_registers_all_supported_node_kinds():
    builder = SymbolTableBuilder()
    scope = SymbolTable()
    builder.register_node(ast.DeclareVariable("value", ast.Type("mui8")), scope)
    builder.register_node(
        ast.Assignment(
            ast.Identifier("value"), Token(TokenType.ASSIGN, "="), ast.Literal(1)
        ),
        scope,
    )
    builder.register_node(ast.EnumMember("Ready"), scope)
    builder.register_node(ast.StructField("field", ast.Type("mui8")), scope)
    builder.register_node(ast.ErrorMember("message", "mstr"), scope)
    builder.register_node(ast.Return(ast.Literal(1)), scope)
    builder.register_node(ast.If(ast.Literal(True), []), scope)
    builder.register_node(ast.For("item", ast.Identifier("items"), []), scope)
    builder.register_node(ast.While(ast.Literal(True), []), scope)

    assert {"value", "Ready", "field", "message"} <= set(scope.symbols)


def test_pass1_registers_nested_declarations_and_operator():
    builder = SymbolTableBuilder()
    scope = SymbolTable()
    operator = ast.Operator(
        "+",
        [ast.OperatorArgument("left", "mui8")],
        [ast.DeclareVariable("local", ast.Type("mui8"))],
        "mui8",
    )
    builder.register_node(operator, scope)
    symbol = scope.lookup("+")
    assert symbol.kind == "operator"
    assert symbol.child_scope.lookup("left").kind == "operator_argument"
    assert symbol.child_scope.lookup("local").kind == "variable"

    error = ast.Error("Failure", [ast.ErrorMember("message", "mstr")])
    builder.register_node(error, scope)
    assert scope.lookup("Failure").child_scope.lookup("message").kind == "error_member"

    enum = ast.Enum("State", [ast.EnumMember("Ready")])
    builder.register_node(enum, scope)
    assert scope.lookup("State").child_scope.lookup("Ready").kind == "enum_member"

    struct = ast.Struct("Record", [ast.StructField("id", ast.Type("mui8"))])
    builder.register_node(struct, scope)
    assert scope.lookup("Record").child_scope.lookup("id").kind == "struct_field"


def test_pass1_registers_nonempty_block_and_trace_paths(capsys):
    builder = SymbolTableBuilder(trace=True)
    scope = SymbolTable()
    builder.register_node(
        ast.If(
            ast.Literal(True),
            [ast.DeclareVariable("inside", ast.Type("mui8"))],
        ),
        scope,
    )
    builder.register_node(ast.Enum("State", []), scope)
    builder.register_node(ast.Struct("Record", []), scope)
    builder.register_node(ast.Function("work", [], "void", []), scope)
    builder.register_node(ast.DeclareVariable("value", ast.Type("mui8")), scope)
    output = capsys.readouterr().out
    assert "Found valid enum declaration" in output
    assert "Found valid struct declaration" in output
    assert "Found valid function declaration" in output
    assert "Found valid variable declaration" in output


def test_pass1_coverage_for_control_flow_and_unknown_nodes():
    builder = SymbolTableBuilder()
    scope = SymbolTable()

    builder.register_node(
        ast.If(
            ast.Literal(True),
            [ast.DeclareVariable("then_value", ast.Type("mui8"))],
            elifs=[
                ast.Elif(
                    ast.Literal(False),
                    [ast.DeclareVariable("elif_value", ast.Type("mui8"))],
                )
            ],
            else_body=ast.Else([ast.DeclareVariable("else_value", ast.Type("mui8"))]),
        ),
        scope,
    )
    builder.register_node(
        ast.For(
            "item",
            ast.Identifier("items"),
            [ast.DeclareVariable("loop_value", ast.Type("mui8"))],
        ),
        scope,
    )
    builder.register_node(
        ast.While(
            ast.Literal(True),
            [ast.DeclareVariable("while_value", ast.Type("mui8"))],
        ),
        scope,
    )
    builder.register_node(
        ast.Do(
            [ast.DeclareVariable("do_value", ast.Type("mui8"))],
            ast.Fail(
                [ast.DeclareVariable("fail_value", ast.Type("mui8"))],
                "Failure",
                "error",
            ),
        ),
        scope,
    )

    with pytest.raises(SemanticError):
        builder.register_node(ast.Program([], "manual"), scope)


def test_pass1_assignment_and_unknown_node_errors():
    builder = SymbolTableBuilder()
    scope = SymbolTable()
    with pytest.raises(SemanticError):
        builder.register_node(
            ast.Assignment(
                ast.Identifier("missing"), Token(TokenType.ASSIGN, "="), ast.Literal(1)
            ),
            scope,
        )
    builder.register_node(
        ast.Assignment(ast.Literal(0), Token(TokenType.ASSIGN, "="), ast.Literal(1)),
        scope,
    )
    with pytest.raises(SemanticError):
        builder.register_node(ast.Break(), scope)


def test_semantic_analyser_delegates_and_rejects_unknown_attributes():
    analyser = SemanticAnalyser(None, False)
    scope = SymbolTable()
    analyser.register_variable(ast.DeclareVariable("x", ast.Type("mui8")), scope)
    assert scope.lookup("x").type == "mui8"
    with pytest.raises(AttributeError):
        _ = analyser.not_a_registration_method


def test_semantic_trace_displays_populated_scopes(capsys):
    tree = parse("$MEM-GC\nval mui8 value = 1.\nfc work()!void {}")
    analyse(tree, True)
    output = capsys.readouterr().out
    assert "SYMBOL TABLE" in output
    assert "WORK SCOPE" in output


def test_serialisation_and_scope_name_fallbacks():
    assert _serialise(TokenType.TYPE) == "TYPE"
    marker = object()
    assert _serialise(marker) is marker

    global_scope = SymbolTable()
    child_scope = SymbolTable(global_scope)
    global_scope.define(Symbol("child", "function", "void", global_scope, child_scope))
    assert _scope_name(global_scope, global_scope) == "module"
    owner_scope = SymbolTable()
    global_scope.define(Symbol("owned", "variable", "mui8", owner_scope))
    assert _scope_name(owner_scope, global_scope) == "owned"
    assert _scope_name(SymbolTable(), global_scope) == "local"


def test_cli_main_direct_paths(monkeypatch, tmp_path):
    import teapot.main as cli

    source = tmp_path / "program.tp"
    source.write_text("$MEM-GC")
    calls = []
    monkeypatch.setattr(
        cli.lexer, "run", lambda source, trace: calls.append((source, trace))
    )
    monkeypatch.chdir(tmp_path)

    monkeypatch.setattr(sys, "argv", ["teapot", "program.tp"])
    cli.main()
    assert calls[-1] == ("$MEM-GC", False)
    (tmp_path / "build" / "old").write_text("stale")

    monkeypatch.setattr(sys, "argv", ["teapot", "-t", "program.tp"])
    cli.main()
    assert calls[-1] == ("$MEM-GC", True)
    assert not (tmp_path / "build" / "old").exists()

    monkeypatch.setattr(sys, "argv", ["teapot", "bad.txt"])
    with pytest.raises(TeapotError):
        cli.main()
    monkeypatch.setattr(sys, "argv", ["teapot", "missing.tp"])
    with pytest.raises(TeapotError):
        cli.main()


def test_module_entrypoint_delegates(monkeypatch):
    calls = []
    monkeypatch.setattr("teapot.main.main", lambda: calls.append(True))
    runpy.run_module("teapot", run_name="__main__")
    assert calls == [True]


def test_module_entrypoint_import_path_covers_guard_false_branch():
    importlib.import_module("teapot.__main__")


def test_lexer_module_guard():
    with pytest.raises(SystemExit, match="Cannot run this file directly"):
        runpy.run_module("teapot.lexer", run_name="__main__")


def test_parser_module_guard():
    with pytest.raises(SystemExit, match="Cannot run this file directly"):
        runpy.run_module("teapot.parser", run_name="__main__")


def test_parser_core_module_guard():
    with pytest.raises(SystemExit, match="Cannot run this file directly"):
        runpy.run_module("teapot.parsing.core", run_name="__main__")


def test_debug_print_rejects_unsupported_options():
    with pytest.raises(TypeError, match="unsupported output options"):
        debug_print("message", unsupported=True)


def test_cli_converts_compiler_errors_to_clean_exit(monkeypatch, tmp_path, capsys):
    import teapot.main as cli

    source = tmp_path / "broken.tp"
    source.write_text("$MEM-GC\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["teapot", "broken.tp"])

    def fail_compile(source_text, trace):
        raise TypeMismatchError("bad type")

    monkeypatch.setattr(cli.lexer, "run", fail_compile)

    with pytest.raises(SystemExit, match="1"):
        cli.main()

    assert "SemanticError: compilation failed" in capsys.readouterr().err


@pytest.mark.parametrize("module_name", ["teapot.tokens", "teapot.teapot_ast"])
def test_internal_modules_reject_direct_execution(module_name):
    with pytest.raises(SystemExit, match="Cannot run this file directly"):
        runpy.run_module(module_name, run_name="__main__")


def test_phase_public_api_modules_and_compiler_pipeline():
    ast_api = importlib.import_module("teapot.ast")
    compiler_api = importlib.import_module("teapot.compiler")
    lexing_api = importlib.import_module("teapot.lexing")
    lexing_errors = importlib.import_module("teapot.lexing.errors")
    parsing_errors = importlib.import_module("teapot.parsing.errors")
    semantic_errors = importlib.import_module("teapot.semantic.errors")

    assert ast_api.Program is ast.Program
    assert compiler_api.compile_source("$MEM-GC\n")
    assert lexing_api.Lexer is Lexer
    assert lexing_errors.LexerError is LexerError
    assert parsing_errors.__all__ == []
    assert semantic_errors.SemanticError is SemanticError
