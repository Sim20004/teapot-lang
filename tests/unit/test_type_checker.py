from unittest.mock import Mock

import pytest

import teapot.teapot_ast as ast
from teapot.errors import (
    InvalidDatatypeError,
    ReturnTypeMismatchError,
    TypeBoundsExceededError,
    TypeMismatchError,
    VoidDatatypeError,
)
from teapot.semantic import SymbolTable
from teapot.semantic.pass2 import TypeChecker
from teapot.tokens import Token, TokenType


@pytest.mark.parametrize(
    "datatype, value, expected_error",
    [
        ("void", 0, VoidDatatypeError),
        ("mui8", 1.5, TypeMismatchError),
        ("cchar", "too long", TypeBoundsExceededError),
        ("mui8", 256, TypeBoundsExceededError),
        ("mui8", -1, TypeBoundsExceededError),
    ],
)
def test_type_checker_rejects_invalid_values(datatype, value, expected_error):
    checker = TypeChecker(None, SymbolTable())
    node = ast.DeclareVariable("value", ast.Type(datatype), ast.Literal(value))

    with pytest.raises(expected_error):
        checker.check_variable(node, checker.global_scope)


def test_type_checker_rejects_unknown_datatypes():
    checker = TypeChecker(None, SymbolTable())
    node = ast.DeclareVariable("value", ast.Type("missing"), ast.Literal(0))

    with pytest.raises(InvalidDatatypeError):
        checker.check_variable(node, checker.global_scope)


def test_type_checker_check_none_tree():
    checker = TypeChecker(None, SymbolTable())
    checker.check()


def test_type_checker_check_dispatches_variables_and_operators():
    tree = ast.Program(
        [
            ast.DeclareVariable(
                "value",
                ast.Type("mui8"),
                ast.Literal(1),
            ),
            ast.Operator(
                "+",
                [],
                [ast.Return(ast.Literal(1))],
                Token(TokenType.TYPE, "mui8"),
            ),
        ],
        "gc",
    )

    checker = TypeChecker(tree, SymbolTable())
    checker.check()


def test_type_checker_check_dispatches_functions_with_string_return_types():
    tree = ast.Program(
        [
            ast.Function(
                "identity",
                [],
                "mui8",
                [ast.Return(ast.Literal(1))],
            ),
        ],
        "gc",
    )

    TypeChecker(tree, SymbolTable()).check()


def test_type_checker_allows_unknown_function_return_types():
    tree = ast.Program(
        [ast.Function("factory", [], "CustomResult", [])],
        "gc",
    )

    TypeChecker(tree, SymbolTable()).check()


def test_type_checker_infers_valid_binary_types_and_rejects_invalid_pairs():
    checker = TypeChecker(None, SymbolTable())
    left = ast.Literal(1)
    right = ast.Literal(2)
    expression = ast.BinaryExpression(left, "+", right)
    original = checker.infer_expression_type

    def infer_children(node):
        if node is left or node is right:
            return "aint"
        return original(node)

    checker.infer_expression_type = infer_children
    assert original(expression) == "aint"
    assert checker.infer_binary_type("+", "aint", "aint") == "aint"
    assert checker.infer_expression_type(ast.Literal("plain")) == "str"

    with pytest.raises(TypeMismatchError, match="Cannot apply"):
        checker.infer_binary_type("==", "aint", "str")


def test_type_checker_rejects_return_type_mismatch():
    checker = TypeChecker(None, SymbolTable())

    operator = ast.Operator(
        "+",
        [],
        [ast.Return(ast.Literal("wrong"))],
        Token(TokenType.TYPE, "mui8"),
    )

    with pytest.raises(
        ReturnTypeMismatchError,
        match="return a str value",
    ):
        checker.check_operator(operator)


def test_type_checker_rejects_return_value_outside_bounds():
    checker = TypeChecker(None, SymbolTable())

    operator = ast.Operator(
        "+",
        [],
        [ast.Return(ast.Literal(256))],
        Token(TokenType.TYPE, "mui8"),
    )

    with pytest.raises(
        ReturnTypeMismatchError,
        match="outside the bounds of mui8",
    ):
        checker.check_operator(operator)


def test_type_checker_ignores_non_return_statements():
    checker = TypeChecker(None, SymbolTable())

    operator = ast.Operator(
        "+",
        [],
        [ast.Break()],
        Token(TokenType.TYPE, "mui8"),
    )

    checker.check_operator(operator)


def test_type_checker_check_node_ignores_non_typechecking_nodes():
    checker = TypeChecker(None, SymbolTable())

    checker.check_node(
        ast.Struct("Record", []),
        checker.global_scope,
    )
    checker.check_node(
        ast.Enum("State", []),
        checker.global_scope,
    )
    checker.check_node(
        ast.Error("Failure", []),
        checker.global_scope,
    )
    checker.check_node(
        ast.Break(),
        checker.global_scope,
    )


@pytest.mark.parametrize(
    "datatype, value",
    [
        ("mui8", 0),
        ("mui8", 255),
        ("aint", 123),
        ("str", "hello"),
        ("cchar", "x"),
        ("mchar", "x"),
    ],
)
def test_type_checker_accepts_valid_values(datatype, value):
    checker = TypeChecker(None, SymbolTable())

    node = ast.DeclareVariable(
        "value",
        ast.Type(datatype),
        ast.Literal(value),
    )

    checker.check_variable(node, checker.global_scope)


def test_type_checker_accepts_missing_variable_value():
    checker = TypeChecker(None, SymbolTable())

    node = ast.DeclareVariable(
        "value",
        ast.Type("mui8"),
    )

    checker.check_variable(node, checker.global_scope)


def test_type_checker_void_none_value_returns_without_checking():
    checker = TypeChecker(None, SymbolTable())

    node = ast.DeclareVariable(
        "value",
        ast.Type("mui8"),
        None,
    )

    checker.check_variable(node, checker.global_scope)


def test_type_checker_void_literal_none_returns_without_checking():
    checker = TypeChecker(None, SymbolTable())

    node = ast.DeclareVariable(
        "value",
        ast.Type("mui8"),
        ast.Literal(None),
    )

    checker.check_variable(node, checker.global_scope)


def test_type_checker_infers_nested_binary_expression_types():
    checker = TypeChecker(None, SymbolTable())

    left = ast.BinaryExpression(
        ast.Literal(1),
        "+",
        ast.Literal(2),
    )
    right = ast.BinaryExpression(
        ast.Literal(3),
        "+",
        ast.Literal(4),
    )
    expression = ast.BinaryExpression(left, "+", right)

    assert checker.infer_expression_type(expression) == "aint"


def test_type_checker_infer_expression_type_returns_none_for_unknown_literal_type():
    checker = TypeChecker(None, SymbolTable())

    assert checker.infer_expression_type(ast.Literal(None)) is None


def test_type_checker_infer_expression_type_returns_none_for_unknown_expression():
    checker = TypeChecker(None, SymbolTable())

    assert checker.infer_expression_type(object()) is None


def test_identifier_returns_declared_type():
    checker = TypeChecker(None, SymbolTable())
    identifier = ast.Identifier("x")
    checker.global_scope.lookup = Mock(return_value=Mock(type="int"))

    result = checker.infer_expression_type(identifier)

    assert result == "int"
    checker.global_scope.lookup.assert_called_once_with("x")


def test_identifier_with_different_type_returns_that_type():
    checker = TypeChecker(None, SymbolTable())
    identifier = ast.Identifier("message")
    checker.global_scope.lookup = Mock(return_value=Mock(type="string"))

    result = checker.infer_expression_type(identifier)

    assert result == "string"
    checker.global_scope.lookup.assert_called_once_with("message")


def test_unknown_identifier_propagates_lookup_error():
    checker = TypeChecker(None, SymbolTable())
    identifier = ast.Identifier("missing")
    checker.global_scope.lookup = Mock(side_effect=NameError("missing"))

    with pytest.raises(NameError):
        checker.infer_expression_type(identifier)

    checker.global_scope.lookup.assert_called_once_with("missing")
