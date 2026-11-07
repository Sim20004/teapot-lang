from unittest.mock import Mock
from types import SimpleNamespace

from teapot.errors import UndefinedVariableError  
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
                Token(TokenType.TYPE, "aint"),
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
                "aint",
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
    scope = SymbolTable()
    checker = TypeChecker(None, scope)
    left = ast.Literal(1)
    right = ast.Literal(2)
    expression = ast.BinaryExpression(left, "+", right)
    original = checker.infer_expression_type

    def infer_children(node, scope):
        if node is left or node is right:
            return "aint"
        return original(node, scope)

    checker.infer_expression_type = infer_children
    assert original(expression, scope) == "aint"
    assert checker.infer_binary_type("+", "aint", "aint") == "aint"
    assert checker.infer_expression_type(ast.Literal("plain"), scope) == "str"

    with pytest.raises(TypeMismatchError, match="Cannot apply"):
        checker.infer_binary_type("==", "aint", "str")


def test_type_checker_rejects_return_type_mismatch():
    scope = SymbolTable()
    checker = TypeChecker(None, scope)

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
        checker.check_operator(operator, scope)


def test_type_checker_rejects_return_value_outside_bounds():
    scope = SymbolTable()
    checker = TypeChecker(None, scope)

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
        checker.check_operator(operator, scope)


def test_type_checker_ignores_non_return_statements():
    scope = SymbolTable()
    checker = TypeChecker(None, scope)

    operator = ast.Operator(
        "+",
        [],
        [ast.Break()],
        Token(TokenType.TYPE, "mui8"),
    )

    checker.check_operator(operator, scope)


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
    scope = SymbolTable()
    checker = TypeChecker(None, scope)

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

    assert checker.infer_expression_type(expression, scope) == "aint"


def test_type_checker_infer_expression_type_returns_none_for_unknown_literal_type():
    scope = SymbolTable()
    checker = TypeChecker(None, scope)

    assert checker.infer_expression_type(ast.Literal(None), scope) is None


def test_type_checker_infer_expression_type_returns_none_for_unknown_expression():
    scope = SymbolTable()
    checker = TypeChecker(None, scope)

    assert checker.infer_expression_type(object(), scope) is None


def test_identifier_returns_declared_type():
    scope = SymbolTable()
    checker = TypeChecker(None, scope)
    identifier = ast.Identifier("x")
    checker.global_scope.lookup = Mock(return_value=Mock(type="int"))

    result = checker.infer_expression_type(identifier, scope)

    assert result == "int"
    checker.global_scope.lookup.assert_called_once_with("x")


def test_identifier_with_different_type_returns_that_type():
    scope = SymbolTable()
    checker = TypeChecker(None, scope)
    identifier = ast.Identifier("message")
    checker.global_scope.lookup = Mock(return_value=Mock(type="string"))

    result = checker.infer_expression_type(identifier, scope)

    assert result == "string"
    checker.global_scope.lookup.assert_called_once_with("message")


def test_unknown_identifier_propagates_lookup_error():
    scope = SymbolTable()
    checker = TypeChecker(None, scope)
    identifier = ast.Identifier("missing")
    checker.global_scope.lookup = Mock(side_effect=NameError("missing"))

    with pytest.raises(NameError):
        checker.infer_expression_type(identifier, scope)

    checker.global_scope.lookup.assert_called_once_with("missing")


def _node(cls, **attrs):
    """A mock that passes isinstance(..., cls), so `case cls():` matches it."""
    node = Mock(spec=cls)
    node.scope = None
    for key, value in attrs.items():
        setattr(node, key, value)
    return node


def _fake(kind, **attrs):
    """An instance of a throwaway class named `kind` (pass 2 matches by class name)."""
    return type(kind, (), attrs)()


def _scope_with(symbol):
    """A scope whose lookup() always returns `symbol`."""
    scope = Mock()
    scope.lookup.return_value = symbol
    return scope


# --- _attr / _symbol_kind / type_name (125-128, 132, 142, 146, 149) -----


def test_type_checker_attr_returns_first_matching_attribute():
    node = SimpleNamespace(second="b", third="c")

    assert TypeChecker._attr(node, "first", "second", "third") == "b"


def test_type_checker_attr_returns_none_when_nothing_matches():
    assert TypeChecker._attr(SimpleNamespace(), "a", "b") is None


def test_type_checker_symbol_kind():
    assert TypeChecker._symbol_kind(SimpleNamespace(kind="struct")) == "struct"
    assert TypeChecker._symbol_kind(SimpleNamespace()) is None


def test_type_checker_type_name_handles_none_node_and_unknown_objects():
    checker = TypeChecker(None, SymbolTable())
    unknown = object()

    assert checker.type_name(None) is None
    assert checker.type_name(SimpleNamespace(name="mui8")) == "mui8"
    assert checker.type_name(unknown) is unknown


# --- infer_expression_type (207, 216-217, 222-223, 226-230, 237, 240) ----


def test_type_checker_unknown_identifier_raises_undefined_variable():
    checker = TypeChecker(None, SymbolTable())
    scope = _scope_with(None)

    with pytest.raises(UndefinedVariableError, match="Unknown identifier 'ghost'"):
        checker.infer_expression_type(ast.Identifier("ghost"), scope)


def test_type_checker_infers_grouped_expression_type():
    checker = TypeChecker(None, SymbolTable())
    scope = SymbolTable()

    grouped = _fake("Grouping", expression=ast.Literal(1))
    empty = _fake("Grouping")

    assert checker.infer_expression_type(grouped, scope) == "aint"
    assert checker.infer_expression_type(empty, scope) is None


def test_type_checker_infers_cast_target_base_type():
    checker = TypeChecker(None, SymbolTable())
    scope = SymbolTable()

    by_name = _fake("Cast", target_type="mui8")
    by_node = _fake("Cast", datatype=ast.Type("cstr"))

    assert checker.infer_expression_type(by_name, scope) == "ui8"
    assert checker.infer_expression_type(by_node, scope) == "str"


@pytest.mark.parametrize("operator", ["!", "~"])
def test_type_checker_infers_logical_not_as_bln(operator):
    checker = TypeChecker(None, SymbolTable())
    expression = _fake("Unary", operator=operator, operand=ast.Literal(1))

    assert checker.infer_expression_type(expression, SymbolTable()) == "bln"


def test_type_checker_infers_unary_type_from_operand():
    checker = TypeChecker(None, SymbolTable())
    scope = SymbolTable()

    negated = _fake("Unary", operator="-", operand=ast.Literal(1.5))
    no_operand = _fake("Unary", operator="-")

    assert checker.infer_expression_type(negated, scope) == "dml"
    assert checker.infer_expression_type(no_operand, scope) is None


def test_type_checker_dispatches_call_nodes():
    checker = TypeChecker(None, SymbolTable())
    scope = _scope_with(SimpleNamespace(kind="function", type="mui8"))

    assert checker.infer_expression_type(_fake("Call", name="f"), scope) == "ui8"


def test_type_checker_dispatches_enum_access_nodes():
    checker = TypeChecker(None, SymbolTable())
    scope = _scope_with(SimpleNamespace(kind="enum", type=None))

    expression = _fake("EnumAccess", left="Color")

    assert checker.infer_expression_type(expression, scope) == "Color"


# --- infer_call_type (245-258) -------------------------------------------


def test_type_checker_infer_call_type_without_a_usable_name():
    checker = TypeChecker(None, SymbolTable())
    scope = _scope_with(None)

    assert checker.infer_call_type(_fake("Call"), scope) is None


def test_type_checker_infer_call_type_unknown_callee_is_quiet():
    checker = TypeChecker(None, SymbolTable())
    scope = _scope_with(None)

    assert checker.infer_call_type(_fake("Call", name="missing"), scope) is None
    scope.lookup.assert_called_once_with("missing")


def test_type_checker_infer_call_type_struct_constructor_returns_struct_name():
    checker = TypeChecker(None, SymbolTable())
    scope = _scope_with(SimpleNamespace(kind="struct", type=None))

    assert checker.infer_call_type(_fake("Call", name="Point"), scope) == "Point"


def test_type_checker_infer_call_type_uses_callee_node_and_symbol_type():
    checker = TypeChecker(None, SymbolTable())
    scope = _scope_with(SimpleNamespace(kind="function", type="mf64"))
    call = _fake("Call", callee=SimpleNamespace(name="g"))

    assert checker.infer_call_type(call, scope) == "f64"
    scope.lookup.assert_called_once_with("g")


# --- infer_enum_access_type (261-269) ------------------------------------


def test_type_checker_infer_enum_access_without_a_usable_owner():
    checker = TypeChecker(None, SymbolTable())

    assert checker.infer_enum_access_type(_fake("EnumAccess"), _scope_with(None)) is None


def test_type_checker_infer_enum_access_returns_enum_name():
    checker = TypeChecker(None, SymbolTable())
    scope = _scope_with(SimpleNamespace(kind="enum", type=None))
    expression = _fake("EnumAccess", object=SimpleNamespace(name="Color"))

    assert checker.infer_enum_access_type(expression, scope) == "Color"


@pytest.mark.parametrize(
    "symbol",
    [None, SimpleNamespace(kind="struct", type=None)],
)
def test_type_checker_infer_enum_access_ignores_non_enums(symbol):
    checker = TypeChecker(None, SymbolTable())
    expression = _fake("EnumAccess", left="Thing")

    assert checker.infer_enum_access_type(expression, _scope_with(symbol)) is None


# --- infer_binary_type (273, 280-286, 294, 300, 302-311) -----------------


@pytest.mark.parametrize("left, right", [(None, "aint"), ("aint", None)])
def test_type_checker_infer_binary_type_unknown_operand_is_quiet(left, right):
    checker = TypeChecker(None, SymbolTable())

    assert checker.infer_binary_type("+", left, right) is None


def test_type_checker_infer_binary_type_uses_operator_overload():
    checker = TypeChecker(None, SymbolTable())
    scope = _scope_with(SimpleNamespace(kind="operator", type="Vec"))

    assert checker.infer_binary_type("+", "Vec", "Vec", scope) == "Vec"
    scope.lookup.assert_called_once_with("+")


@pytest.mark.parametrize("operator", ["==", "!=", "~="])
@pytest.mark.parametrize("scope", [None, _scope_with(None)])
def test_type_checker_infer_binary_type_user_types_support_equality(operator, scope):
    checker = TypeChecker(None, SymbolTable())

    assert checker.infer_binary_type(operator, "Vec", "Vec", scope) == "bln"


def test_type_checker_infer_binary_type_user_types_reject_other_operators():
    checker = TypeChecker(None, SymbolTable())
    scope = _scope_with(SimpleNamespace(kind="struct", type=None))

    with pytest.raises(TypeMismatchError, match="Cannot apply"):
        checker.infer_binary_type("+", "Vec", "Vec", scope)

    with pytest.raises(TypeMismatchError, match="Cannot apply"):
        checker.infer_binary_type("==", "Vec", "Other", None)


@pytest.mark.parametrize(
    "operator, left, right, expected",
    [
        ("+", "mui8", "aint", "ui8"),  # right aint adopts left's type
        ("*", "aint", "f32", "f32"),  # left aint adopts right's type
        ("/", "aint", "aint", "dml"),
        ("+", "str", "str", "str"),
        ("<", "si32", "si32", "bln"),
        (">=", "f64", "f64", "bln"),
        ("==", "str", "str", "bln"),
        ("!=", "bln", "bln", "bln"),
        ("~=", "char", "char", "bln"),
        ("&&", "bln", "bln", "bln"),
        ("||", "bln", "bln", "bln"),
    ],
)
def test_type_checker_infer_binary_type_rules(operator, left, right, expected):
    checker = TypeChecker(None, SymbolTable())

    assert checker.infer_binary_type(operator, left, right) == expected


# --- check_statement: control flow (344-352, 358, 362-366) ---------------


@pytest.mark.parametrize("branch", ["body", "elif", "else"])
def test_type_checker_check_statement_reaches_every_if_branch(branch):
    scope = SymbolTable()
    checker = TypeChecker(None, scope)
    bodies = {"body": [], "elif": [], "else": []}
    bodies[branch] = [ast.Return(ast.Literal("wrong"))]
    statement = _node(
        ast.If,
        body=bodies["body"],
        elifs=[SimpleNamespace(body=bodies["elif"], scope=None)],
        else_body=SimpleNamespace(body=bodies["else"], scope=None),
    )

    with pytest.raises(ReturnTypeMismatchError):
        checker.check_statement(statement, scope, "mui8")


def test_type_checker_check_statement_allows_if_without_else():
    scope = SymbolTable()
    checker = TypeChecker(None, scope)
    statement = _node(
        ast.If,
        body=[ast.Return(ast.Literal(1))],
        elifs=[],
        else_body=None,
    )

    checker.check_statement(statement, scope, "aint")


@pytest.mark.parametrize("node_type", [ast.For, ast.While])
def test_type_checker_check_statement_checks_loop_bodies(node_type):
    scope = SymbolTable()
    checker = TypeChecker(None, scope)
    statement = _node(node_type, body=[ast.Return(ast.Literal("wrong"))])

    with pytest.raises(ReturnTypeMismatchError):
        checker.check_statement(statement, scope, "mui8")


@pytest.mark.parametrize("branch", ["body", "fail"])
def test_type_checker_check_statement_checks_do_and_fail_bodies(branch):
    scope = SymbolTable()
    checker = TypeChecker(None, scope)
    bodies = {"body": [], "fail": []}
    bodies[branch] = [ast.Return(ast.Literal("wrong"))]
    statement = _node(
        ast.Do,
        body=bodies["body"],
        fail=SimpleNamespace(body=bodies["fail"], scope=None),
    )

    with pytest.raises(ReturnTypeMismatchError):
        checker.check_statement(statement, scope, "mui8")


# --- check_return early exits (372, 376) ---------------------------------


def test_type_checker_check_return_ignores_bare_return():
    scope = SymbolTable()
    checker = TypeChecker(None, scope)

    checker.check_return(ast.Return(None), "aint", scope)


def test_type_checker_check_return_skips_uninferable_values():
    scope = SymbolTable()
    checker = TypeChecker(None, scope)

    checker.check_return(ast.Return(ast.Literal(None)), "mui8", scope)


# --- check_variable: user-defined / compound types (422-429) -------------


@pytest.mark.parametrize(
    "datatype, value, symbol",
    [
        ("list", ast.Literal(1), None),  # compound type, no symbol
        ("Point", None, SimpleNamespace(kind="struct", type=None)),  # no value
        ("Point", ast.Literal(1), SimpleNamespace(kind="struct", type=None)),
        ("Point", object(), SimpleNamespace(kind="struct", type=None)),  # unknown
    ],
)
def test_type_checker_check_variable_user_types_that_pass_quietly(
    datatype, value, symbol
):
    checker = TypeChecker(None, SymbolTable())
    node = ast.DeclareVariable("value", ast.Type(datatype), value)

    checker.check_variable(node, _scope_with(symbol))


def test_type_checker_check_variable_accepts_matching_struct_constructor():
    checker = TypeChecker(None, SymbolTable())
    scope = _scope_with(SimpleNamespace(kind="struct", type=None))
    node = ast.DeclareVariable("value", ast.Type("Point"), _fake("Call", name="Point"))

    checker.check_variable(node, scope)


def test_type_checker_check_variable_rejects_mismatched_struct_constructor():
    checker = TypeChecker(None, SymbolTable())
    scope = _scope_with(SimpleNamespace(kind="struct", type=None))
    node = ast.DeclareVariable("value", ast.Type("Point"), _fake("Call", name="Other"))

    with pytest.raises(TypeMismatchError, match="expected Point, found Other"):
        checker.check_variable(node, scope)


# --- check_type (447, 451, 454) ------------------------------------------


def test_type_checker_check_type_without_scope_skips_expressions():
    checker = TypeChecker(None, SymbolTable())
    node = ast.DeclareVariable("value", ast.Type("mui8"), ast.Identifier("x"))

    checker.check_type(node, TypeChecker.TYPES["mui8"])


def test_type_checker_check_type_skips_uninferable_expressions():
    checker = TypeChecker(None, SymbolTable())
    node = ast.DeclareVariable("value", ast.Type("mui8"), object())

    checker.check_type(node, TypeChecker.TYPES["mui8"], SymbolTable())


def test_type_checker_check_type_rejects_incompatible_expression():
    checker = TypeChecker(None, SymbolTable())
    scope = _scope_with(SimpleNamespace(type="str"))
    node = ast.DeclareVariable("value", ast.Type("mui8"), ast.Identifier("x"))

    with pytest.raises(TypeMismatchError, match="expected ui8, found str"):
        checker.check_type(node, TypeChecker.TYPES["mui8"], scope)


# --- is_type_compatible (494, 498, 513, 520-536) -------------------------


@pytest.mark.parametrize("actual, expected", [(None, "aint"), ("aint", None)])
def test_type_checker_is_type_compatible_false_when_a_type_is_unknown(actual, expected):
    checker = TypeChecker(None, SymbolTable())

    assert checker.is_type_compatible(actual, expected, None) is False


@pytest.mark.parametrize(
    "actual, expected, result",
    [("Point", "Point", True), ("Point", "Other", False), ("Point", "mui8", False)],
)
def test_type_checker_is_type_compatible_compares_user_type_names(
    actual, expected, result
):
    checker = TypeChecker(None, SymbolTable())

    assert checker.is_type_compatible(actual, expected, None) is result


@pytest.mark.parametrize(
    "expression, result",
    [
        (ast.Literal("x"), True),
        (ast.Literal("xy"), False),
        (ast.Identifier("x"), False),  # not a literal: falls through to the end
    ],
)
def test_type_checker_is_type_compatible_str_to_char(expression, result):
    checker = TypeChecker(None, SymbolTable())

    assert checker.is_type_compatible("str", "cchar", expression) is result


@pytest.mark.parametrize(
    "value, result",
    [(0, True), (255, True), (-1, False), (256, False)],
)
def test_type_checker_is_type_compatible_aint_literal_bounds(value, result):
    checker = TypeChecker(None, SymbolTable())

    assert checker.is_type_compatible("aint", "mui8", ast.Literal(value)) is result


def test_type_checker_is_type_compatible_aint_non_literal_is_accepted():
    checker = TypeChecker(None, SymbolTable())
    expression = ast.BinaryExpression(ast.Literal(5), "+", ast.Literal(2))

    assert checker.is_type_compatible("aint", "mui8", expression) is True


@pytest.mark.parametrize("actual, expected", [("ui8", "si8"), ("f32", "f64")])
def test_type_checker_is_type_compatible_rejects_different_sized_types(
    actual, expected
):
    checker = TypeChecker(None, SymbolTable())

    assert checker.is_type_compatible(actual, expected, ast.Literal(1)) is False
