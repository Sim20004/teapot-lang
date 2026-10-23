import pytest

import teapot.teapot_ast as ast
from teapot.lexer import Lexer
from teapot.parser import Parser
from teapot.semantic import SemanticAnalyser, SymbolTable
from teapot.semantic.analyser import analyse


def parse(source):
    return Parser(Lexer(source).tokenise()).parse()


def test_semantic_analyser_delegates_and_rejects_unknown_attributes():
    analyser = SemanticAnalyser(None, False)
    scope = SymbolTable()
    analyser.register_variable(ast.DeclareVariable("x", ast.Type("mui8")), scope)
    assert scope.lookup("x").type == "mui8"
    with pytest.raises(AttributeError):
        _ = analyser.not_a_registration_method


def test_semantic_trace_displays_populated_scopes(capsys):
    tree = parse("$MEM-GC\nval mui8 value = 1.\nfc work()!void {}")
    analyse(tree, True)
    output = capsys.readouterr().out
    assert "SYMBOL TABLE" in output
    assert "WORK SCOPE" in output
