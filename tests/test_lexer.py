from teapot.lexer import Lexer
import teapot.tokens as tokens

def test_empty_source():
    lexer = Lexer("")
    tokens_list = lexer.tokenise()

    assert len(tokens_list) == 1
    assert tokens_list[0].type == tokens.TokenType.EOF
