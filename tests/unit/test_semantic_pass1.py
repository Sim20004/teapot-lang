import pytest

import teapot.teapot_ast as ast
from teapot.semantic import SemanticError, SymbolTable
from teapot.semantic.pass1 import SymbolTableBuilder
from teapot.tokens import Token, TokenType


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
