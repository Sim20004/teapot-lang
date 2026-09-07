from teapot.semantic.errors import SemanticError


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
