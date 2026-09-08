from teapot.debug import print
from teapot.semantic.pass1 import SymbolTableBuilder
from teapot.semantic.pass2 import TypeChecker


class SemanticAnalyser:
    def __init__(self, ast_tree, trace):
        self.ast_tree = ast_tree
        self.trace = trace
        self.symbol_table_builder = SymbolTableBuilder(trace)

    def analyse(self):
        self.build_symbol_table()
        self.type_check()

    def build_symbol_table(self):
        self.global_scope = self.symbol_table_builder.build(self.ast_tree)

    def type_check(self):
        self.type_checker = TypeChecker(
            self.ast_tree,
            getattr(self, "global_scope", None),
            self.trace,
        )
        self.type_checker.check()

    def __getattr__(self, name):
        if name.startswith("register_"):
            return getattr(self.symbol_table_builder, name)
        raise AttributeError(name)


def _display_scope(scope, name="GLOBAL", indent=0):
    prefix = " " * indent
    print(f"\n{prefix}{name} SCOPE:")
    headers = ("IDENTIFIER", "KIND", "DATATYPE")

    rows = [
        (
            str(symbol.name),
            str(symbol.kind),
            str(symbol.type) if symbol.type is not None else "None",
        )
        for symbol in scope.symbols.values()
    ]

    if rows:
        widths = [
            max(len(row[column]) for row in (headers, *rows))
            for column in range(len(headers))
        ]

        print(
            f"{prefix}{headers[0]:<{widths[0]}} | "
            f"{headers[1]:<{widths[1]}} | "
            f"{headers[2]:<{widths[2]}}"
        )
        print(f"{prefix}{'-' * widths[0]}-+-{'-' * widths[1]}-+-{'-' * widths[2]}")

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
            _display_scope(symbol.child_scope, symbol.name.upper(), indent + 2)


def analyse(ast_tree, trace_arg):
    trace = trace_arg

    if trace:
        print("========= BEGIN SEMANTIC ANALYSIS =========")

    analyser = SemanticAnalyser(ast_tree, trace)
    analyser.analyse()

    if trace:
        print("\nSYMBOL TABLE:")
        _display_scope(analyser.global_scope)
        print("========= END SEMANTIC ANALYSIS =========")
