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
    def __init__(self, name, kind, type_):
        self.name = name
        self.kind = kind
        self.type = type_


# Symbol table stores Symbols
class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def define(self, symbol):
        if symbol.name in self.symbols:
            raise SemanticError("Variable already declared!", symbol)
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

    def analyse(self):
        # Trace the top-level node kinds while semantic rules are being built out.
        for node in self.ast_tree.statements:
            if self.trace:
                print(type(node).__name__)

            match node:
                case ast.DeclareVariable():
                    self.analyse_variable_declaration(node)

                case _:
                    raise SemanticError("Unknown node", node)

    def analyse_variable_declaration(self, node):
        identifier = node.identifier
        datatype = node.datatype.name
        symbol = Symbol(identifier, "variable", datatype)
        self.global_scope.define(symbol)

        if self.trace:
            print(f"Found valid variable declaration: {identifier}, {datatype}.")


def analyse(ast_tree, trace_arg):
    # Keep phase banners in one place for callers that enable compiler tracing.
    trace = trace_arg
    if trace:
        print("========= BEGIN SEMANTIC ANALYSIS =========")
    analyser = SemanticAnalyser(ast_tree, trace)
    analyser.analyse()
    if trace:
        print("========= END SEMANTIC ANALYSIS =========")
