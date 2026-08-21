from teapot.debug import print


# Semantic validation is currently a traversal scaffold for future checks.
class SemanticAnalyser:
    def __init__(self, ast_tree, trace):
        self.ast_tree = ast_tree
        self.trace = trace

    def analyse(self):
        # Trace the top-level node kinds while semantic rules are being built out.
        for node in self.ast_tree.statements:
            if self.trace:
                print(type(node).__name__)

def analyse(ast_tree, trace_arg):
    # Keep phase banners in one place for callers that enable compiler tracing.
    trace = trace_arg
    if trace:
        print("========= BEGIN SEMANTIC ANALYSIS =========")
    analyser = SemanticAnalyser(ast_tree, trace)
    analyser.analyse()
    if trace:
        print("========= END SEMANTIC ANALYSIS =========")