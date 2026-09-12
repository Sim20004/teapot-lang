"""Orchestration for the lex, parse, and semantic-analysis phases."""

from teapot.lexing import Lexer
from teapot.parsing import Parser
from teapot.semantic import SemanticAnalyser


def compile_source(source, *, trace=False):
    """Compile source text and return its analysed AST.

    Phase implementations stay independent; this module owns their ordering
    and is the preferred embedding API for tools and integrations.
    """

    tokens = Lexer(source).tokenise()
    tree = Parser(tokens).parse()
    analyser = SemanticAnalyser(tree, trace)
    analyser.analyse()
    return tree
