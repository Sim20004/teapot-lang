from time import sleep

sleep(0)
from typing import ClassVar

import teapot.teapot_ast as ast
from teapot.errors import (
    InvalidDatatypeError,
    ReturnTypeMismatchError,
    TypeBoundsExceededError,
    TypeMismatchError,
    VoidDatatypeError,
)


class TypeChecker:
    TYPES: ClassVar = {
        # Base types
        "void": {
            "base": "void",
            "type": type(None),
            "mutable": False,
            "min": None,
            "max": None,
        },
        "str": {
            "base": "str",
            "type": str,
            "mutable": False,
            "min": None,
            "max": None,
        },
        "char": {
            "base": "char",
            "type": str,
            "mutable": False,
            "min": None,
            "max": None,
        },
        "bln": {
            "base": "bln",
            "type": bool,
            "mutable": False,
            "min": None,
            "max": None,
        },
        "aint": {
            "base": "aint",
            "type": int,
            "mutable": False,
            "min": None,
            "max": None,
        },
        "dml": {
            "base": "dml",
            "type": float,
            "mutable": False,
            "min": None,
            "max": None,
        },
        "f32": {
            "base": "f32",
            "type": float,
            "mutable": False,
            "min": None,
            "max": None,
        },
        "f64": {
            "base": "f64",
            "type": float,
            "mutable": False,
            "min": None,
            "max": None,
        },
        "si8": {
            "base": "si8",
            "type": int,
            "mutable": False,
            "min": -(2**7),
            "max": 2**7 - 1,
        },
        "si16": {
            "base": "si16",
            "type": int,
            "mutable": False,
            "min": -(2**15),
            "max": 2**15 - 1,
        },
        "si32": {
            "base": "si32",
            "type": int,
            "mutable": False,
            "min": -(2**31),
            "max": 2**31 - 1,
        },
        "si64": {
            "base": "si64",
            "type": int,
            "mutable": False,
            "min": -(2**63),
            "max": 2**63 - 1,
        },
        "ui8": {
            "base": "ui8",
            "type": int,
            "mutable": False,
            "min": 0,
            "max": 2**8 - 1,
        },
        "ui16": {
            "base": "ui16",
            "type": int,
            "mutable": False,
            "min": 0,
            "max": 2**16 - 1,
        },
        "ui32": {
            "base": "ui32",
            "type": int,
            "mutable": False,
            "min": 0,
            "max": 2**32 - 1,
        },
        "ui64": {
            "base": "ui64",
            "type": int,
            "mutable": False,
            "min": 0,
            "max": 2**64 - 1,
        },
        # Mutable types
        "mstr": {
            "base": "str",
            "type": str,
            "mutable": True,
            "min": None,
            "max": None,
        },
        "mchar": {
            "base": "char",
            "type": str,
            "mutable": True,
            "min": None,
            "max": None,
        },
        "mbln": {
            "base": "bln",
            "type": bool,
            "mutable": True,
            "min": None,
            "max": None,
        },
        "maint": {
            "base": "aint",
            "type": int,
            "mutable": True,
            "min": None,
            "max": None,
        },
        "mdml": {
            "base": "dml",
            "type": float,
            "mutable": True,
            "min": None,
            "max": None,
        },
        "mf32": {
            "base": "f32",
            "type": float,
            "mutable": True,
            "min": None,
            "max": None,
        },
        "mf64": {
            "base": "f64",
            "type": float,
            "mutable": True,
            "min": None,
            "max": None,
        },
        "msi8": {
            "base": "si8",
            "type": int,
            "mutable": True,
            "min": -(2**7),
            "max": 2**7 - 1,
        },
        "msi16": {
            "base": "si16",
            "type": int,
            "mutable": True,
            "min": -(2**15),
            "max": 2**15 - 1,
        },
        "msi32": {
            "base": "si32",
            "type": int,
            "mutable": True,
            "min": -(2**31),
            "max": 2**31 - 1,
        },
        "msi64": {
            "base": "si64",
            "type": int,
            "mutable": True,
            "min": -(2**63),
            "max": 2**63 - 1,
        },
        "mui8": {
            "base": "ui8",
            "type": int,
            "mutable": True,
            "min": 0,
            "max": 2**8 - 1,
        },
        "mui16": {
            "base": "ui16",
            "type": int,
            "mutable": True,
            "min": 0,
            "max": 2**16 - 1,
        },
        "mui32": {
            "base": "ui32",
            "type": int,
            "mutable": True,
            "min": 0,
            "max": 2**32 - 1,
        },
        "mui64": {
            "base": "ui64",
            "type": int,
            "mutable": True,
            "min": 0,
            "max": 2**64 - 1,
        },
        # Constant types
        "cstr": {
            "base": "str",
            "type": str,
            "mutable": False,
            "min": None,
            "max": None,
        },
        "cchar": {
            "base": "char",
            "type": str,
            "mutable": False,
            "min": None,
            "max": None,
        },
        "cbln": {
            "base": "bln",
            "type": bool,
            "mutable": False,
            "min": None,
            "max": None,
        },
        "caint": {
            "base": "aint",
            "type": int,
            "mutable": False,
            "min": None,
            "max": None,
        },
        "cdml": {
            "base": "dml",
            "type": float,
            "mutable": False,
            "min": None,
            "max": None,
        },
        "cf32": {
            "base": "f32",
            "type": float,
            "mutable": False,
            "min": None,
            "max": None,
        },
        "cf64": {
            "base": "f64",
            "type": float,
            "mutable": False,
            "min": None,
            "max": None,
        },
        "csi8": {
            "base": "si8",
            "type": int,
            "mutable": False,
            "min": -(2**7),
            "max": 2**7 - 1,
        },
        "csi16": {
            "base": "si16",
            "type": int,
            "mutable": False,
            "min": -(2**15),
            "max": 2**15 - 1,
        },
        "csi32": {
            "base": "si32",
            "type": int,
            "mutable": False,
            "min": -(2**31),
            "max": 2**31 - 1,
        },
        "csi64": {
            "base": "si64",
            "type": int,
            "mutable": False,
            "min": -(2**63),
            "max": 2**63 - 1,
        },
        "cui8": {
            "base": "ui8",
            "type": int,
            "mutable": False,
            "min": 0,
            "max": 2**8 - 1,
        },
        "cui16": {
            "base": "ui16",
            "type": int,
            "mutable": False,
            "min": 0,
            "max": 2**16 - 1,
        },
        "cui32": {
            "base": "ui32",
            "type": int,
            "mutable": False,
            "min": 0,
            "max": 2**32 - 1,
        },
        "cui64": {
            "base": "ui64",
            "type": int,
            "mutable": False,
            "min": 0,
            "max": 2**64 - 1,
        },
    }

    def __init__(self, ast_tree, global_scope, trace=False):
        self.ast_tree = ast_tree
        self.global_scope = global_scope
        self.trace = trace

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
                self.check_operator_or_function(node)
            case ast.Struct() | ast.Enum() | ast.Error():
                pass
            case _:
                pass  # Comment if developing but uncomment when using or running tests
            # print(f"Unknown node: {node.__repr__()}")
            # sleep(3)
            # Uncomment above if developing but keep commented when using or running tests

    def check_operator_or_function(self, node):
        expected_type = node.return_type
        if hasattr(expected_type, "value"):
            expected_type = expected_type.value
        if expected_type in self.TYPES:
            self.check_return_type(node, expected_type)

    def check_operator(self, node):
        self.check_operator_or_function(node)

    def check_return_type(self, node, expected_type):
        datatype = self.TYPES[expected_type]

        for statement in node.body:
            if not isinstance(statement, ast.Return):
                continue

            value = statement.value.value

            if type(value) is not datatype["type"]:
                raise ReturnTypeMismatchError(
                    f"You tried to return a {type(value).__name__} value "
                    f"but chose {expected_type} as your callable's return type!"
                )

            if (datatype["min"] is not None and value < datatype["min"]) or (
                datatype["max"] is not None and value > datatype["max"]
            ):
                raise ReturnTypeMismatchError(
                    f"You tried to return a value outside the bounds of "
                    f"{expected_type}!"
                )

    def check_type(self, node, datatype):
        if node.datatype.name == "void":
            raise VoidDatatypeError("Void cannot be used as a datatype!", node)

        if node.value is None or node.value.value is None:
            return

        expected = datatype["type"]
        actual = type(node.value.value)

        if actual is not expected:
            raise TypeMismatchError(
                f"Invalid type for '{node.identifier}': "
                f"expected {expected.__name__}, found {actual.__name__}",
                node,
            )

        if node.datatype.name in ["cchar", "mchar"] and len(node.value.value) != 1:
            raise TypeBoundsExceededError(
                "Characters must only have a length of 1!",
                node,
            )

        if (datatype["max"] is not None and node.value.value > datatype["max"]) or (
            datatype["min"] is not None and node.value.value < datatype["min"]
        ):
            raise TypeBoundsExceededError(
                "Type bounds exceeded.",
                node,
            )

    def check_variable(self, node, scope):
        try:
            datatype = self.TYPES[node.datatype.name]
        except KeyError:
            raise InvalidDatatypeError(
                f"Unknown datatype '{node.datatype.name}'.",
                node,
            )

        self.check_type(node, datatype)
