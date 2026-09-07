from teapot.debug import print


class SemanticError(Exception):
    def __init__(self, msg, node):
        super().__init__(f"Semantic analysis error at {node}: {msg}")
        self.node = node
        print(f"\nSemantic analysis error at {node}: {msg}")
