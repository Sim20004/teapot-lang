class SemanticAnalyser:
    def __init__(self, ast_tree):
        self.ast_tree = ast_tree

    def analyse(self):
        for node in self.ast_tree.statements:
            print(type(node).__name__)

def analyse(ast_tree, trace_arg):
    trace = trace_arg
    if trace:
        print("========= BEGIN SEMANTIC ANALYSIS =========")
    analyser = SemanticAnalyser(ast_tree)
    analyser.analyse()
    if trace:
        print("========= END SEMANTIC ANALYSIS =========")