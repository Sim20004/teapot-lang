class Symbol:
    def __init__(self, name, kind, type_, scope, child_scope=None):
        self.name = name
        self.kind = kind
        self.type = type_
        self.scope = scope
        self.child_scope = child_scope
