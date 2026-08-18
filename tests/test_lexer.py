from teapot.lexer import Lexer

def test_empty_source():
    lexer = Lexer("")
    tokens = lexer.tokenise()

    assert len(tokens) == 1
    assert tokens[0].type == tokens.TokenType.EOF
