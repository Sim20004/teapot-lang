from teapot.lexer import Lexer
from teapot.parser import Parser
from teapot.semantic import SemanticAnalyser


# Test that a basic program successfully passes through the pipeline.
def test_basic_program():
    source = """
        $MEM-GC

        val mui8 foo = 8.
        val cstr bar = "baz".
    """

    lexer = Lexer(source)
    token_list = lexer.tokenise()

    parser = Parser(token_list)
    program = parser.parse()

    analyser = SemanticAnalyser(program, False)
    analyser.analyse()

    assert program.memory_mode == "$MEM-GC"
    assert len(program.statements) == 2

    foo = analyser.global_scope.lookup("foo")
    bar = analyser.global_scope.lookup("bar")

    assert foo is not None
    assert foo.kind == "variable"
    assert foo.type == "mui8"

    assert bar is not None
    assert bar.kind == "variable"
    assert bar.type == "cstr"
