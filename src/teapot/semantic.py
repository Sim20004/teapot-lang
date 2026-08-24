# from typing import ClassVar
# Uncomment above when writing pass 2 code

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
    def __init__(self, name, kind, type_, params, scope):
        self.name = name
        self.kind = kind
        self.type = type_
        self.params = params
        self.scope = scope


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
        self.global_scope = SymbolTable()

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
        self.first_pass_symbol_table()
        self.second_pass_type_check()

    def second_pass_type_check(self):
        pass

    def first_pass_symbol_table(self):
        # Create symbol table by passing over all top-level nodes
        for node in self.ast_tree.statements:
            if self.trace:
                print(type(node).__name__ + ":")

            match node:
                case ast.DeclareVariable():
                    self.define_variable_declaration(node)
                case ast.Struct():
                    self.define_struct_declaration(node)
                case ast.Function():
                    self.define_function_declaration(node)
                case _:
                    raise SemanticError("Unknown node", node)

    def define_function_declaration(self, node):

        identifier = node.name
        return_type = node.return_type

        function_scope = SymbolTable(parent=self.global_scope)

        symbol = Symbol(
            identifier,
            "function",
            return_type,
            None,
            function_scope,
        )

        self.global_scope.define(symbol)

        self.define_function_parameters(node, function_scope)

        if self.trace:
            print(f"  - Found valid function declaration: {identifier}.")

    def define_function_parameters(self, node, function_scope):

        for param in node.arguments:
            function_scope.define(
                Symbol(
                    param.identifier,
                    "function_argument",
                    param.datatype.name,
                    None,
                )
            )

    def define_struct_declaration(self, node):
        identifier = node.identifier
        symbol = Symbol(identifier, "struct", None, None, self.global_scope)
        self.global_scope.define(symbol)

        if self.trace:
            print(f"  - Found valid struct declaration: {identifier}.")

    def define_variable_declaration(self, node):
        identifier = node.identifier
        datatype = node.datatype.name
        symbol = Symbol(identifier, "variable", datatype, None, self.global_scope)

        self.global_scope.define(symbol)

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
        print("\nSYMBOL TABLE:")

        headers = ("IDENTIFIER", "KIND", "DATATYPE")
        symbols = list(table.symbols.values())

        rows = [
            (
                symbol.name,
                symbol.kind,
                symbol.type if symbol.type is not None else "None",
            )
            for symbol in symbols
        ]

        widths = [
            max(len(str(row[i])) for row in [headers, *rows])
            for i in range(len(headers))
        ]

        print(
            f"{headers[0]:<{widths[0]}} | "
            f"{headers[1]:<{widths[1]}} | "
            f"{headers[2]:<{widths[2]}}"
        )

        for row in rows:
            print(
                f"{row[0]:<{widths[0]}} | {row[1]:<{widths[1]}} | {row[2]:<{widths[2]}}"
            )

        print("========= END SEMANTIC ANALYSIS =========")
