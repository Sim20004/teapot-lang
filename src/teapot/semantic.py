# from typing import ClassVar
# ABOVE: Uncomment above when writing pass 2 code

import teapot.teapot_ast as ast
from teapot.debug import print


# SemanticError class for errors
class SemanticError(Exception):
    def __init__(self, msg, node):

        super().__init__(f"Semantic analysis error at {node}: {msg}")

        self.node = node

        print(f"\nSemantic analysis error at {node}: {msg}")


# Symbol class stores a symbol for the symbol table
class Symbol:
    def __init__(self, name, kind, type_, scope, child_scope=None):

        self.name = name
        self.kind = kind
        self.type = type_
        self.scope = scope
        self.child_scope = child_scope


# Symbol table stores Symbols
class SymbolTable:
    def __init__(self, parent=None):

        self.symbols = {}
        self.parent = parent

    def define(self, symbol):

        if symbol.name in self.symbols:
            raise SemanticError(
                f"{symbol.kind.capitalize()} `{symbol.name}` already declared as a symbol!",
                symbol,
            )

        self.symbols[symbol.name] = symbol

    def lookup(self, name):

        if name in self.symbols:
            return self.symbols[name]

        if self.parent is not None:
            return self.parent.lookup(name)

        return None


# Semantic validation is currently a traversal scaffold for future checks.
class SemanticAnalyser:
    def __init__(self, ast_tree, trace):

        self.ast_tree = ast_tree
        self.trace = trace

    """
    datatypes: ClassVar = {

        "mstr",
        "mchar",
        "mbln",
        "maint",
        "mdml",
        "mf32",
        "mf64",
        "msi8",
        "msi16",
        "msi32",
        "msi64",
        "mui8",
        "mui16",
        "mui32",
        "mui64",

        "cstr",
        "cchar",
        "cbln",
        "caint",
        "cdml",
        "cf32",
        "cf64",
        "csi8",
        "csi16",
        "csi32",
        "csi64",
        "cui8",
        "cui16",
        "cui32",
        "cui64",
    }
    """  # Uncomment when writing pass 2 code

    def analyse(self):

        self.build_symbol_table()
        self.type_check()

    def type_check(self):

        pass

    def build_symbol_table(self):

        global_scope = SymbolTable()

        for node in self.ast_tree.statements:
            if self.trace:
                print(type(node).__name__ + ":")

            self.register_node(node, global_scope)

        self.global_scope = global_scope

    def register_node(self, node, scope):

        match node:
            case ast.DeclareVariable():
                self.register_variable(node, scope)

            case ast.Struct():
                self.register_struct(node, scope)

            case ast.Function():
                self.register_function(node, scope)

            case ast.Enum():
                self.register_enum(node, scope)

            case ast.EnumMember():
                self.register_enum_member(node, scope)

            case ast.StructField():
                self.register_struct_field(node, scope)

            case ast.Error():
                self.register_error(node, scope)

            case ast.ErrorMember():
                self.register_error_member(node, scope)

            case _:
                raise SemanticError("Unknown node", node)

    def register_error(self, node, scope):

        error_scope = SymbolTable(parent=scope)

        identifier = node.identifier

        self.register_error_members(node, error_scope)

        symbol = Symbol(
            identifier,
            "error",
            None,
            scope,
            error_scope,
        )

        scope.define(symbol)

    def register_error_members(self, node, scope):

        for member in node.body:
            self.register_node(member, scope)

    def register_error_member(self, node, scope):

        symbol = Symbol(
            node.name,
            "error_member",
            node.datatype,
            scope,
        )

        scope.define(symbol)

    def register_enum_member(self, node, scope):

        symbol = Symbol(
            node.name,
            "enum_member",
            None,
            scope,
        )

        scope.define(symbol)

    def register_struct_field(self, node, scope):

        symbol = Symbol(
            node.identifier,
            "struct_field",
            node.datatype.name,
            scope,
        )

        scope.define(symbol)

    def register_enum(self, node, scope):

        enum_scope = SymbolTable(parent=scope)

        self.register_enum_members(node, enum_scope)

        identifier = node.identifier

        symbol = Symbol(
            identifier,
            "enum",
            None,
            scope,
            enum_scope,
        )

        scope.define(symbol)

        if self.trace:
            print(f"  - Found valid enum declaration: {identifier}.")

    def register_enum_members(self, node, scope):

        for member in node.body:
            self.register_node(member, scope)

    def register_function(self, node, scope):

        identifier = node.name
        return_type = node.return_type

        function_scope = SymbolTable(parent=scope)

        for param in node.arguments:
            function_scope.define(
                Symbol(
                    param.identifier,
                    "function_parameter",
                    param.datatype,
                    function_scope,
                )
            )

        symbol = Symbol(
            identifier,
            "function",
            return_type,
            scope,
            function_scope,
        )

        scope.define(symbol)

        self.register_function_body(node, function_scope)

        if self.trace:
            print(f"  - Found valid function declaration: {identifier}.")

    def register_function_body(self, node, scope):

        for statement in node.body:
            self.register_node(statement, scope)

    def register_struct_members(self, node, scope):

        for member in node.body:
            self.register_node(member, scope)

    def register_struct(self, node, scope):

        identifier = node.identifier

        struct_scope = SymbolTable(parent=scope)

        self.register_struct_members(node, struct_scope)

        symbol = Symbol(
            identifier,
            "struct",
            None,
            scope,
            struct_scope,
        )

        scope.define(symbol)

        if self.trace:
            print(f"  - Found valid struct declaration: {identifier}.")

    def register_variable(self, node, scope):

        identifier = node.identifier
        datatype = node.datatype.name

        symbol = Symbol(
            identifier,
            "variable",
            datatype,
            scope,
        )

        scope.define(symbol)

        if self.trace:
            print(f"  - Found valid variable declaration: {identifier}, {datatype}.")


def analyse(ast_tree, trace_arg):

    # Keep phase banners in one place for callers that enable compiler tracing.
    trace = trace_arg

    if trace:
        print("========= BEGIN SEMANTIC ANALYSIS =========")

    analyser = SemanticAnalyser(ast_tree, trace)

    analyser.analyse()

    table = analyser.global_scope

    if trace:

        def display_scope(scope, name="GLOBAL", indent=0):

            prefix = " " * indent

            print(f"\n{prefix}{name} SCOPE:")

            headers = ("IDENTIFIER", "KIND", "DATATYPE")

            rows = [
                (
                    symbol.name,
                    symbol.kind,
                    symbol.type if symbol.type is not None else "None",
                )
                for symbol in scope.symbols.values()
            ]

            if rows:
                widths = [
                    max(len(str(row[column])) for row in (headers, *rows))
                    for column in range(len(headers))
                ]

                print(
                    f"{prefix}{headers[0]:<{widths[0]}} | "
                    f"{headers[1]:<{widths[1]}} | "
                    f"{headers[2]:<{widths[2]}}"
                )

                print(
                    f"{prefix}{'-' * widths[0]}-+-{'-' * widths[1]}-+-{'-' * widths[2]}"
                )

                for row in rows:
                    print(
                        f"{prefix}{row[0]:<{widths[0]}} | "
                        f"{row[1]:<{widths[1]}} | "
                        f"{row[2]:<{widths[2]}}"
                    )

            else:
                print(f"{prefix}(empty)")

            for symbol in scope.symbols.values():
                if symbol.child_scope is not None:
                    display_scope(
                        symbol.child_scope,
                        f"{symbol.name.upper()}",
                        indent + 2,
                    )

        print("\nSYMBOL TABLE:")

        display_scope(table)

        print("========= END SEMANTIC ANALYSIS =========")
