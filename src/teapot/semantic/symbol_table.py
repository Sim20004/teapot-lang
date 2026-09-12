from teapot.errors import DuplicateDeclarationError


class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def define(self, symbol):
        if symbol.name in self.symbols:
            existing = self.symbols[symbol.name]
            raise DuplicateDeclarationError(
                symbol.name,
                symbol.kind.replace("_", " "),
                location=getattr(existing, "location", None),
                node=existing,
            )

        symbol.location = getattr(self, "current_location", None)
        self.symbols[symbol.name] = symbol

    def lookup(self, name):
        if name in self.symbols:
            return self.symbols[name]

        if self.parent is not None:
            return self.parent.lookup(name)

        return None
