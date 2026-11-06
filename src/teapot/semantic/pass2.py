from time import sleep
from typing import ClassVar

import teapot.teapot_ast as ast
from teapot.errors import (
    InvalidDatatypeError,
    ReturnTypeMismatchError,
    TypeBoundsExceededError,
    TypeMismatchError,
    UndefinedVariableError,
    VoidDatatypeError,
)

# TODO: implement type flexibility

INT_BASES = ("aint", "si8", "si16", "si32", "si64", "ui8", "ui16", "ui32", "ui64")
FLOAT_BASES = ("dml", "f32", "f64")
NUMERIC_BASES = INT_BASES + FLOAT_BASES
SIZED_INT_BASES = tuple(b for b in INT_BASES if b != "aint")

# Datatype names that are not in TYPES but are valid (compound types).
COMPOUND_TYPE_NAMES = ("list", "map", "ref", "arr", "array", "set")


def _make_types():
    """Builds the same table as the old hand-written TYPES dict.

    Layout: void, base types, then m-prefixed (mutable) and c-prefixed (constant)
    versions of every base type except void.
    """
    specs = {
        "str": (str, None, None),
        "char": (str, None, None),
        "bln": (bool, None, None),
        "aint": (int, None, None),
        "dml": (float, None, None),
        "f32": (float, None, None),
        "f64": (float, None, None),
    }
    for bits in (8, 16, 32, 64):
        specs[f"si{bits}"] = (int, -(2 ** (bits - 1)), 2 ** (bits - 1) - 1)
    for bits in (8, 16, 32, 64):
        specs[f"ui{bits}"] = (int, 0, 2**bits - 1)

    def entry(base, py_type, low, high, mutable):
        return {
            "base": base,
            "type": py_type,
            "mutable": mutable,
            "min": low,
            "max": high,
        }

    types = {"void": entry("void", type(None), None, None, False)}
    for base, (py_type, low, high) in specs.items():
        types[base] = entry(base, py_type, low, high, False)
    for base, (py_type, low, high) in specs.items():
        types["m" + base] = entry(base, py_type, low, high, True)
    for base, (py_type, low, high) in specs.items():
        types["c" + base] = entry(base, py_type, low, high, False)
    return types


def _make_binary_types():
    """Kept for reference / backwards compatibility.

    TypeChecker.infer_binary_type no longer reads this table; it applies rules
    instead so that sized integers, constants and mutables all work.
    """
    arith = ("aint", "dml", "f32", "f64")
    equality = ("str", "char", "bln", "aint", "dml", "f32", "f64") + SIZED_INT_BASES
    ordering = arith + SIZED_INT_BASES

    return {
        "+": {**{(t, t): t for t in arith}, ("str", "str"): "str"},
        "-": {(t, t): t for t in arith},
        "*": {(t, t): t for t in arith},
        "/": {
            ("aint", "aint"): "dml",
            ("dml", "dml"): "dml",
            ("f32", "f32"): "f32",
            ("f64", "f64"): "f64",
        },
        "==": {(t, t): "bln" for t in equality},
        "!=": {(t, t): "bln" for t in equality},
        "<": {(t, t): "bln" for t in ordering},
        ">": {(t, t): "bln" for t in ordering},
        "<=": {(t, t): "bln" for t in ordering},
        ">=": {(t, t): "bln" for t in ordering},
    }


class TypeChecker:
    TYPES: ClassVar = _make_types()
    BINARY_TYPES: ClassVar = _make_binary_types()

    # ------------------------------------------------------------------
    # AST adapters.
    # I only know the node classes that pass 1 uses. If your AST names these
    # differently, edit the tuples below. Anything not recognised is treated
    # as "type unknown" and skipped rather than raising.
    # ------------------------------------------------------------------
    CALL_NODES: ClassVar = ("Call", "FunctionCall", "CallExpression")
    CAST_NODES: ClassVar = ("Cast", "CastExpression", "TypeCast")
    GROUP_NODES: ClassVar = ("Grouping", "GroupExpression", "Parenthesized", "Group")
    UNARY_NODES: ClassVar = ("Unary", "UnaryExpression", "UnaryOperation")
    ENUM_ACCESS_NODES: ClassVar = (
        "EnumAccess",
        "EnumMemberAccess",
        "ScopeAccess",
        "ScopeResolution",
        "MemberAccess",
    )

    def __init__(self, ast_tree, global_scope, trace=False):
        self.ast_tree = ast_tree
        self.global_scope = global_scope
        self.trace = trace

    # ------------------------------------------------------------------
    # Small helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _attr(node, *names):
        for name in names:
            if hasattr(node, name):
                return getattr(node, name)
        return None

    @staticmethod
    def _symbol_kind(symbol):
        return getattr(symbol, "kind", None)

    @staticmethod
    def scope_of(node, default):
        """The scope pass 1 attached to `node`, or `default` if there is none."""
        return getattr(node, "scope", None) or default

    def type_name(self, t):
        """Turn a symbol type (str, datatype node, or None) into a plain string."""
        if t is None:
            return None
        if isinstance(t, str):
            return t
        if hasattr(t, "name"):
            return t.name
        if hasattr(t, "value"):
            return t.value
        return t

    def base(self, t):
        """cui8 / mui8 / ui8 -> ui8. Unknown names (structs, enums) pass through."""
        if t in self.TYPES:
            return self.TYPES[t]["base"]
        return t

    # ------------------------------------------------------------------
    # Entry points
    # ------------------------------------------------------------------
    def check(self):
        if self.ast_tree is None:
            return

        for node in self.ast_tree.statements:
            self.check_node(node, self.global_scope)

    def check_node(self, node, scope):
        match node:
            case ast.DeclareVariable():
                self.check_variable(node, scope)
            case ast.Operator() | ast.Function():
                self.check_operator_or_function(node, scope)
            case ast.Struct() | ast.Enum() | ast.Error():
                pass
            case _:
                # pass  # Comment if developing but uncomment when using or running tests
                print(f"Unknown node: {node.__repr__()}")
                sleep(3)
            # Uncomment above if developing but keep commented when using or running tests

    # ------------------------------------------------------------------
    # Expression typing (always returns a BASE type name, or None = unknown)
    # ------------------------------------------------------------------
    def infer_expression_type(self, expression, scope):
        if isinstance(expression, ast.Literal):
            value = expression.value
            if type(value) is bool:
                return "bln"
            if type(value) is int:
                return "aint"
            if type(value) is float:
                return "dml"
            if type(value) is str:
                return "str"
            return None

        if isinstance(expression, ast.BinaryExpression):
            left_type = self.infer_expression_type(expression.left, scope)
            right_type = self.infer_expression_type(expression.right, scope)
            return self.infer_binary_type(
                expression.operator, left_type, right_type, scope
            )

        if isinstance(expression, ast.Identifier):
            symbol = scope.lookup(expression.name)
            if symbol is None:
                raise UndefinedVariableError(
                    f"Unknown identifier '{expression.name}'.",
                    expression,
                )
            return self.base(self.type_name(symbol.type))

        kind = type(expression).__name__

        if kind in self.GROUP_NODES:
            inner = self._attr(expression, "expression", "inner", "value", "node")
            return (
                self.infer_expression_type(inner, scope) if inner is not None else None
            )

        if kind in self.CAST_NODES:
            target = self._attr(expression, "target_type", "datatype", "type", "target")
            return self.base(self.type_name(target))

        if kind in self.UNARY_NODES:
            operator = self._attr(expression, "operator", "op")
            if operator in ("~", "!"):
                return "bln"
            operand = self._attr(expression, "operand", "right", "expression", "value")
            return (
                self.infer_expression_type(operand, scope)
                if operand is not None
                else None
            )

        if kind in self.CALL_NODES:
            return self.infer_call_type(expression, scope)

        if kind in self.ENUM_ACCESS_NODES:
            return self.infer_enum_access_type(expression, scope)

        return None  # unsupported expression: unknown, don't check

    def infer_call_type(self, expression, scope):
        callee = self._attr(expression, "name", "callee", "identifier", "function")
        name = callee if isinstance(callee, str) else getattr(callee, "name", None)
        if not isinstance(name, str):
            return None

        symbol = scope.lookup(name)
        if symbol is None:
            # Overloads / builtins aren't modelled yet, so stay quiet.
            return None

        if self._symbol_kind(symbol) == "struct":
            return name  # constructor call

        return self.base(self.type_name(symbol.type))

    def infer_enum_access_type(self, expression, scope):
        owner = self._attr(expression, "left", "object", "enum", "base", "scope")
        name = owner if isinstance(owner, str) else getattr(owner, "name", None)
        if not isinstance(name, str):
            return None

        symbol = scope.lookup(name)
        if symbol is not None and self._symbol_kind(symbol) == "enum":
            return name
        return None  # struct field access etc.: not modelled yet

    def infer_binary_type(self, operator, left_type, right_type, scope=None):
        if left_type is None or right_type is None:
            return None

        left = self.base(left_type)
        right = self.base(right_type)

        # Operator overloads on user-defined types (structs, enums, ...).
        if left not in self.TYPES or right not in self.TYPES:
            if scope is not None:
                symbol = scope.lookup(operator)
                if symbol is not None and self._symbol_kind(symbol) == "operator":
                    return self.base(self.type_name(symbol.type))
            if left == right and operator in ("==", "!=", "~="):
                return "bln"
            raise TypeMismatchError(
                f"Cannot apply {operator} to {left_type} and {right_type} types."
            )

        # An untyped integer adopts the other numeric operand's type.
        if left == "aint" and right in NUMERIC_BASES:
            left = right
        elif right == "aint" and left in NUMERIC_BASES:
            right = left

        if left == right:
            if operator in ("+", "-", "*", "/"):
                if left in NUMERIC_BASES:
                    if operator == "/" and left == "aint":
                        return "dml"
                    return left
                if left == "str" and operator == "+":
                    return "str"
            elif operator in ("<", ">", "<=", ">="):
                if left in NUMERIC_BASES:
                    return "bln"
            elif operator in ("==", "!=", "~="):
                return "bln"
            elif operator in ("&&", "||"):
                if left == "bln":
                    return "bln"

        raise TypeMismatchError(
            f"Cannot apply {operator} to {left_type} and {right_type} types."
        )

    # ------------------------------------------------------------------
    # Functions / operators and their bodies
    # ------------------------------------------------------------------
    def check_operator_or_function(self, node, scope):
        expected_type = self.type_name(node.return_type)
        local_scope = self.scope_of(node, scope)
        self.check_return_type(node, expected_type, local_scope)

    def check_operator(self, node, scope):
        self.check_operator_or_function(node, scope)

    def check_return_type(self, node, expected_type, scope):
        """Check a whole callable body: returns, and local variable declarations."""
        self.check_body(node.body, scope, expected_type)

    def check_body(self, body, scope, expected_type=None):
        for statement in body:
            self.check_statement(statement, scope, expected_type)

    def check_statement(self, statement, scope, expected_type):
        match statement:
            case ast.DeclareVariable():
                self.check_variable(statement, scope)
            case ast.Return():
                if expected_type is not None:
                    self.check_return(statement, expected_type, scope)
            case ast.If():
                self.check_body(
                    statement.body, self.scope_of(statement, scope), expected_type
                )
                for elif_node in statement.elifs:
                    self.check_body(
                        elif_node.body, self.scope_of(elif_node, scope), expected_type
                    )
                if statement.else_body is not None:
                    self.check_body(
                        statement.else_body.body,
                        self.scope_of(statement.else_body, scope),
                        expected_type,
                    )
            case ast.For() | ast.While():
                self.check_body(
                    statement.body, self.scope_of(statement, scope), expected_type
                )
            case ast.Do():
                self.check_body(
                    statement.body, self.scope_of(statement, scope), expected_type
                )
                fail = statement.fail
                self.check_body(fail.body, self.scope_of(fail, scope), expected_type)
            case _:
                pass

    def check_return(self, statement, expected_type, scope):
        if statement.value is None:
            return

        actual_type = self.infer_expression_type(statement.value, scope)
        if actual_type is None:
            return  # couldn't infer, so don't guess

        if not self.is_type_compatible(actual_type, expected_type, statement.value):
            raise ReturnTypeMismatchError(
                f"You tried to return a {actual_type} value "
                f"but chose {expected_type} as your callable's return type!"
            )

    # ------------------------------------------------------------------
    # Variables
    # ------------------------------------------------------------------
    def check_variable(self, node, scope):
        name = node.datatype.name

        if name in self.TYPES:
            self.check_type(node, self.TYPES[name], scope)
            return

        # User-defined type (struct / enum / error) or compound type.
        symbol = scope.lookup(name) if isinstance(name, str) else None
        is_plain_name = isinstance(name, str) and name.isidentifier()

        if symbol is None and is_plain_name and name not in COMPOUND_TYPE_NAMES:
            raise InvalidDatatypeError(
                f"Unknown datatype '{name}'.",
                node,
            )

        if symbol is None or node.value is None:
            return
        if isinstance(node.value, ast.Literal):
            return

        actual = self.infer_expression_type(node.value, scope)
        if actual is not None and actual != name:
            raise TypeMismatchError(
                f"Invalid type for '{node.identifier}': expected {name}, found {actual}",
                node,
            )

    def check_type(self, node, datatype, scope=None):
        if node.datatype.name == "void":
            raise VoidDatatypeError("Void cannot be used as a datatype!", node)

        value = node.value
        if value is None:
            return

        if isinstance(value, ast.Literal):
            self.check_literal(node, datatype)
            return

        if scope is None:
            return

        actual = self.infer_expression_type(value, scope)
        if actual is None:
            return

        if not self.is_type_compatible(actual, node.datatype.name, value):
            raise TypeMismatchError(
                f"Invalid type for '{node.identifier}': "
                f"expected {datatype['base']}, found {actual}",
                node,
            )

    def check_literal(self, node, datatype):
        literal = node.value.value
        if literal is None:
            return

        expected = datatype["type"]
        actual = type(literal)

        if actual is not expected:
            raise TypeMismatchError(
                f"Invalid type for '{node.identifier}': "
                f"expected {expected.__name__}, found {actual.__name__}",
                node,
            )

        if (datatype["max"] is not None and literal > datatype["max"]) or (
            datatype["min"] is not None and literal < datatype["min"]
        ):
            raise TypeBoundsExceededError(
                "Type bounds exceeded.",
                node,
            )

        if node.datatype.name in ["cchar", "mchar"] and len(literal) != 1:
            raise TypeBoundsExceededError(
                "Characters must only have a length of 1!",
                node,
            )

    # ------------------------------------------------------------------
    # Compatibility
    # ------------------------------------------------------------------
    def is_type_compatible(self, actual, expected, expression):
        if actual is None or expected is None:
            return False

        # Structs, enums and other user types aren't in TYPES: compare names.
        if actual not in self.TYPES or expected not in self.TYPES:
            return self.base(actual) == self.base(expected)

        actual_type = self.TYPES[actual]
        expected_type = self.TYPES[expected]

        if actual_type["base"] == expected_type["base"]:
            return True

        # A one-character string literal can be a char.
        if (
            actual_type["base"] == "str"
            and expected_type["base"] == "char"
            and isinstance(expression, ast.Literal)
            and isinstance(expression.value, str)
        ):
            return len(expression.value) == 1

        # Guard: different underlying Python types never match.
        if actual_type["type"] != expected_type["type"]:
            return False

        # Untyped integers fit any integer type.
        if actual_type["base"] == "aint":
            if isinstance(expression, ast.Literal):
                value = expression.value

                minimum = expected_type["min"]
                maximum = expected_type["max"]

                if minimum is not None and value < minimum:
                    return False

                return maximum is not None and value > maximum

            # Non-literal integer expression such as (5 + 2) * 3.
            # TODO: constant-fold these so bounds can be checked too.
            return True

        return False
