from teapot.debug import print

class SemanticAnalyser:
    def __init__(self, ast_tree, trace):
        self.ast_tree = ast_tree
        self.trace = trace

    def analyse(self):
        for node in self.ast_tree.statements:
            if self.trace:
                print(type(node).__name__)

def analyse(ast_tree, trace_arg):
    trace = trace_arg
    if trace:
        print("========= BEGIN SEMANTIC ANALYSIS =========")
    analyser = SemanticAnalyser(ast_tree, trace)
    analyser.analyse()
    if trace:
        print("========= END SEMANTIC ANALYSIS =========")