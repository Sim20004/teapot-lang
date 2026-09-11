from typing import ClassVar

import teapot.teapot_ast as ast

# from teapot.debug import print
# from teapot.semantic.errors import SemanticError


class TypeChecker:
    TYPES: ClassVar = {
        # Base types
        "void": {
            "base": "void",
            "mutable": False,
            "min": None,
            "max": None,
        },
        "str": {
            "base": "str",
            "mutable": False,
            "min": None,
            "max": None,
        },
        "char": {
            "base": "char",
            "mutable": False,
            "min": None,
            "max": None,
        },
        "bln": {
            "base": "bln",
            "mutable": False,
            "min": None,
            "max": None,
        },
        "aint": {
            "base": "aint",
            "mutable": False,
            "min": None,
            "max": None,
        },
        "dml": {
            "base": "dml",
            "mutable": False,
            "min": None,
            "max": None,
        },
        "f32": {
            "base": "f32",
            "mutable": False,
            "min": None,
            "max": None,
        },
        "f64": {
            "base": "f64",
            "mutable": False,
            "min": None,
            "max": None,
        },
        "si8": {
            "base": "si8",
            "mutable": False,
            "min": -(2**7),
            "max": 2**7 - 1,
        },
        "si16": {
            "base": "si16",
            "mutable": False,
            "min": -(2**15),
            "max": 2**15 - 1,
        },
        "si32": {
            "base": "si32",
            "mutable": False,
            "min": -(2**31),
            "max": 2**31 - 1,
        },
        "si64": {
            "base": "si64",
            "mutable": False,
            "min": -(2**63),
            "max": 2**63 - 1,
        },
        "ui8": {
            "base": "ui8",
            "mutable": False,
            "min": 0,
            "max": 2**8 - 1,
        },
        "ui16": {
            "base": "ui16",
            "mutable": False,
            "min": 0,
            "max": 2**16 - 1,
        },
        "ui32": {
            "base": "ui32",
            "mutable": False,
            "min": 0,
            "max": 2**32 - 1,
        },
        "ui64": {
            "base": "ui64",
            "mutable": False,
            "min": 0,
            "max": 2**64 - 1,
        },
        # Mutable types
        "mstr": {
            "base": "str",
            "mutable": True,
            "min": None,
            "max": None,
        },
        "mchar": {
            "base": "char",
            "mutable": True,
            "min": None,
            "max": None,
        },
        "mbln": {
            "base": "bln",
            "mutable": True,
            "min": None,
            "max": None,
        },
        "maint": {
            "base": "aint",
            "mutable": True,
            "min": None,
            "max": None,
        },
        "mdml": {
            "base": "dml",
            "mutable": True,
            "min": None,
            "max": None,
        },
        "mf32": {
            "base": "f32",
            "mutable": True,
            "min": None,
            "max": None,
        },
        "mf64": {
            "base": "f64",
            "mutable": True,
            "min": None,
            "max": None,
        },
        "msi8": {
            "base": "si8",
            "mutable": True,
            "min": -(2**7),
            "max": 2**7 - 1,
        },
        "msi16": {
            "base": "si16",
            "mutable": True,
            "min": -(2**15),
            "max": 2**15 - 1,
        },
        "msi32": {
            "base": "si32",
            "mutable": True,
            "min": -(2**31),
            "max": 2**31 - 1,
        },
        "msi64": {
            "base": "si64",
            "mutable": True,
            "min": -(2**63),
            "max": 2**63 - 1,
        },
        "mui8": {
            "base": "ui8",
            "mutable": True,
            "min": 0,
            "max": 2**8 - 1,
        },
        "mui16": {
            "base": "ui16",
            "mutable": True,
            "min": 0,
            "max": 2**16 - 1,
        },
        "mui32": {
            "base": "ui32",
            "mutable": True,
            "min": 0,
            "max": 2**32 - 1,
        },
        "mui64": {
            "base": "ui64",
            "mutable": True,
            "min": 0,
            "max": 2**64 - 1,
        },
        # Constant types
        "cstr": {
            "base": "str",
            "mutable": False,
            "min": None,
            "max": None,
        },
        "cchar": {
            "base": "char",
            "mutable": False,
            "min": None,
            "max": None,
        },
        "cbln": {
            "base": "bln",
            "mutable": False,
            "min": None,
            "max": None,
        },
        "caint": {
            "base": "aint",
            "mutable": False,
            "min": None,
            "max": None,
        },
        "cdml": {
            "base": "dml",
            "mutable": False,
            "min": None,
            "max": None,
        },
        "cf32": {
            "base": "f32",
            "mutable": False,
            "min": None,
            "max": None,
        },
        "cf64": {
            "base": "f64",
            "mutable": False,
            "min": None,
            "max": None,
        },
        "csi8": {
            "base": "si8",
            "mutable": False,
            "min": -(2**7),
            "max": 2**7 - 1,
        },
        "csi16": {
            "base": "si16",
            "mutable": False,
            "min": -(2**15),
            "max": 2**15 - 1,
        },
        "csi32": {
            "base": "si32",
            "mutable": False,
            "min": -(2**31),
            "max": 2**31 - 1,
        },
        "csi64": {
            "base": "si64",
            "mutable": False,
            "min": -(2**63),
            "max": 2**63 - 1,
        },
        "cui8": {
            "base": "ui8",
            "mutable": False,
            "min": 0,
            "max": 2**8 - 1,
        },
        "cui16": {
            "base": "ui16",
            "mutable": False,
            "min": 0,
            "max": 2**16 - 1,
        },
        "cui32": {
            "base": "ui32",
            "mutable": False,
            "min": 0,
            "max": 2**32 - 1,
        },
        "cui64": {
            "base": "ui64",
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
        for node in self.ast_tree.statements:
            self.check_node(node, self.global_scope)

    def check_node(self, node, scope):
        match node:
            case ast.DeclareVariable():
                self.check_variable(node, scope)

    def check_variable(node, scope):
        pass
