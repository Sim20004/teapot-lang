from teapot.lexer import Lexer
import teapot.tokens as tokens
import pytest
from teapot.lexer import LexerError

def test_empty_source():
    lexer = Lexer("")
    tokens_list = lexer.tokenise()

    assert len(tokens_list) == 1
    assert tokens_list[0].type == tokens.TokenType.EOF

def test_eof_position():
    lexer = Lexer("foo")
    tokens_list = lexer.tokenise()

    assert tokens_list[-1].type == tokens.TokenType.EOF
    assert tokens_list[-1].line == 1
    assert tokens_list[-1].col == 4

def test_whitespace_is_ignored():
    lexer = Lexer("foo bar baz qux quux")
    tokens_list = lexer.tokenise()

    assert len(tokens_list) == 6

    for token in tokens_list[:-1]:
        assert token.type == tokens.TokenType.IDENTIFIER

def test_crlf_is_normalised():
    lexer = Lexer("foo\r\nbar")
    tokens_list = lexer.tokenise()

    assert tokens_list[0].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[1].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[1].line == 2
    assert tokens_list[1].col == 1
    assert tokens_list[2].type == tokens.TokenType.EOF

def test_single_line_comment_is_ignored():
    lexer = Lexer("// foo,\n// bar\n// baz\n// qux?\n$MEM-GC")
    tokens_list = lexer.tokenise()

    assert tokens_list[0].type == tokens.TokenType.DIRECTIVE

def test_comment_at_eof():
    lexer = Lexer("$MEM-GC\n// foo")
    tokens_list = lexer.tokenise()

    assert tokens_list[0].type == tokens.TokenType.DIRECTIVE
    assert tokens_list[1].type == tokens.TokenType.EOF

def test_identifier():
    lexer = Lexer("val mui8 foo = 8.")
    tokens_list = lexer.tokenise()

    assert tokens_list[2].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[2].value == "foo"

def test_identifier_with_underscores():
    lexer = Lexer("val cui16 foo_bar_baz = 12.")
    tokens_list = lexer.tokenise()

    assert tokens_list[0].type == tokens.TokenType.VAL
    assert tokens_list[1].type == tokens.TokenType.TYPE
    assert tokens_list[2].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[3].type == tokens.TokenType.ASSIGN
    assert tokens_list[4].type == tokens.TokenType.INTEGER
    assert tokens_list[5].type == tokens.TokenType.PERIOD
    assert tokens_list[6].type == tokens.TokenType.EOF

def test_identifier_starting_with_underscore():
    lexer = Lexer('val mstr _foo = "bar".')
    tokens_list = lexer.tokenise()

    assert tokens_list[0].type == tokens.TokenType.VAL
    assert tokens_list[1].type == tokens.TokenType.TYPE
    assert tokens_list[2].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[2].value == "_foo"
    assert tokens_list[3].type == tokens.TokenType.ASSIGN
    assert tokens_list[4].type == tokens.TokenType.STRING
    assert tokens_list[5].type == tokens.TokenType.PERIOD
    assert tokens_list[6].type == tokens.TokenType.EOF

def test_identifier_with_numbers():
    lexer = Lexer('val cstr foo2bar3 = "baz".')
    tokens_list = lexer.tokenise()

    assert tokens_list[0].type == tokens.TokenType.VAL
    assert tokens_list[1].type == tokens.TokenType.TYPE
    assert tokens_list[2].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[2].value == "foo2bar3"
    assert tokens_list[3].type == tokens.TokenType.ASSIGN
    assert tokens_list[4].type == tokens.TokenType.STRING
    assert tokens_list[5].type == tokens.TokenType.PERIOD
    assert tokens_list[6].type == tokens.TokenType.EOF

def test_keywords():
    lexer = Lexer(" ".join(tokens.KEYWORDS.keys()))
    tokens_list = lexer.tokenise()

    for token, (keyword, expected_type) in zip(
        tokens_list[:-1], tokens.KEYWORDS.items()
    ):
        assert token.type == expected_type
        assert token.value == keyword

def test_datatypes():
    lexer = Lexer(" ".join(tokens.TYPE_KEYWORDS))
    tokens_list = lexer.tokenise()

    for token, datatype in zip(tokens_list[:-1], tokens.TYPE_KEYWORDS):
        assert token.type == tokens.TokenType.TYPE
        assert token.value == datatype

def test_boolean_literals():
    lexer = Lexer("true false")
    tokens_list = lexer.tokenise()

    assert tokens_list[0].type == tokens.TokenType.BOOLEAN
    assert tokens_list[0].value is True

    assert tokens_list[1].type == tokens.TokenType.BOOLEAN
    assert tokens_list[1].value is False

    assert tokens_list[2].type == tokens.TokenType.EOF

def test_integer():
    lexer = Lexer("val mui8 foo = 8.")
    tokens_list = lexer.tokenise()

    assert tokens_list[0].type == tokens.TokenType.VAL
    assert tokens_list[1].type == tokens.TokenType.TYPE
    assert tokens_list[2].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[3].type == tokens.TokenType.ASSIGN
    assert tokens_list[4].type == tokens.TokenType.INTEGER
    assert tokens_list[4].value == 8
    assert tokens_list[5].type == tokens.TokenType.PERIOD
    assert tokens_list[6].type == tokens.TokenType.EOF

def test_float():
    lexer = Lexer("val cdml foo = 0.1.\nval mdml bar = 0.2.\nval cf32 baz = 0.3.\nval mf32 qux = 0.4.\nval cf64 quux = 0.5.\nval mf64 corge = 0.6.")
    tokens_list = lexer.tokenise()

    count = 0.1
    offset = 0
    for i in range(0, 6):
        assert tokens_list[0 + offset].type == tokens.TokenType.VAL
        assert tokens_list[1 + offset].type == tokens.TokenType.TYPE
        assert tokens_list[2 + offset].type == tokens.TokenType.IDENTIFIER
        assert tokens_list[3 + offset].type == tokens.TokenType.ASSIGN
        assert tokens_list[4 + offset].type == tokens.TokenType.FLOAT
        assert tokens_list[4 + offset].value == pytest.approx(count)
        assert tokens_list[5 + offset].type == tokens.TokenType.PERIOD
        offset += 6
        count += 0.1

    assert tokens_list[-1].type == tokens.TokenType.EOF

def test_multiple_numbers():
    lexer = Lexer("10 + 20 * 30")
    tokens_list = lexer.tokenise()

    assert tokens_list[0].type == tokens.TokenType.INTEGER
    assert tokens_list[0].value == 10
    assert tokens_list[1].type == tokens.TokenType.PLUS
    assert tokens_list[2].type == tokens.TokenType.INTEGER
    assert tokens_list[2].value == 20
    assert tokens_list[3].type == tokens.TokenType.MULTIPLY
    assert tokens_list[4].type == tokens.TokenType.INTEGER
    assert tokens_list[4].value == 30
    assert tokens_list[5].type == tokens.TokenType.EOF

def test_float_followed_by_symbol():
    lexer = Lexer("2.4.")
    tokens_list = lexer.tokenise()

    assert tokens_list[0].type == tokens.TokenType.FLOAT
    assert tokens_list[0].value == 2.4
    assert tokens_list[1].type == tokens.TokenType.PERIOD
    assert tokens_list[2].type == tokens.TokenType.EOF

def test_duplicate_decimal_point():
    lexer = Lexer("1.2.3")

    with pytest.raises(LexerError):
        lexer.tokenise()

def test_string():
    lexer = Lexer('"foo"')
    tokens_list = lexer.tokenise()

    assert tokens_list[0].type == tokens.TokenType.STRING
    assert tokens_list[0].value == "foo"

def test_empty_string():
    lexer = Lexer('""')
    tokens_list = lexer.tokenise()

    assert tokens_list[0].type == tokens.TokenType.STRING
    assert tokens_list[0].value == ""

def test_string_with_spaces():
    lexer = Lexer('"foo bar baz"')
    tokens_list = lexer.tokenise()

    assert tokens_list[0].type == tokens.TokenType.STRING
    assert tokens_list[0].value == "foo bar baz"

def test_string_with_symbols():
    lexer = Lexer('"foo*bar.baz|qux"')
    tokens_list = lexer.tokenise()

    assert tokens_list[0].type == tokens.TokenType.STRING
    assert tokens_list[0].value == "foo*bar.baz|qux"

def test_unterminated_string():
    lexer = Lexer('"foo')
    with pytest.raises(LexerError):
        lexer.tokenise()

def test_single_character_symbols():
    single_character_symbols = {
        "+": tokens.TokenType.PLUS,
        "-": tokens.TokenType.MINUS,
        "*": tokens.TokenType.MULTIPLY,
        "/": tokens.TokenType.DIVIDE,
        "%": tokens.TokenType.MODULO,
        ">": tokens.TokenType.GREATER,
        "<": tokens.TokenType.LESS,
        "~": tokens.TokenType.NOT,
        "=": tokens.TokenType.ASSIGN,
        "(": tokens.TokenType.OPEN_PAREN,
        ")": tokens.TokenType.CLOSE_PAREN,
        "{": tokens.TokenType.OPEN_BRACE,
        "}": tokens.TokenType.CLOSE_BRACE,
        "[": tokens.TokenType.OPEN_BRACKET,
        "]": tokens.TokenType.CLOSE_BRACKET,
        ",": tokens.TokenType.COMMA,
        ".": tokens.TokenType.PERIOD,
        "|": tokens.TokenType.PIPE,
        ":": tokens.TokenType.COLON,
        "!": tokens.TokenType.EXCLAMATION,
    }

    lexer = Lexer("+-*/%><~ =(){}[],.|:!")
    tokens_list = lexer.tokenise()

    for _, expected_type in single_character_symbols.items():
        assert tokens_list.pop(0).type == expected_type

def test_two_character_symbols_and_precedence():
    two_character_symbols = {
        "**": tokens.TokenType.POWER,
        "==": tokens.TokenType.EQUALS,
        ">=": tokens.TokenType.GREATER_EQUAL,
        "<=": tokens.TokenType.LESS_EQUAL,
        "~=": tokens.TokenType.NOT_EQUAL,
        "&&": tokens.TokenType.AND,
        "||": tokens.TokenType.OR,
        "+=": tokens.TokenType.ASSIGN_PLUS,
        "-=": tokens.TokenType.ASSIGN_MINUS,
        "*=": tokens.TokenType.ASSIGN_MULTIPLY,
        "/=": tokens.TokenType.ASSIGN_DIVIDE,
        "::": tokens.TokenType.DOUBLE_COLON,
        ">>": tokens.TokenType.CAST,
    }

    lexer = Lexer("**  ==  >=  <=  ~=  &&  ||  +=  -=  *=  /=  ::  >>")
    tokens_list = lexer.tokenise()

    for _, expected_type in two_character_symbols.items():
        assert tokens_list.pop(0).type == expected_type

def test_invalid_symbol():
    lexer = Lexer("£")
    with pytest.raises(LexerError):
        lexer.tokenise()

def test_directive():
    lexer = Lexer("$MEM-MANUAL")
    tokens_list = lexer.tokenise()

    assert tokens_list[0].type == tokens.TokenType.DIRECTIVE
    assert tokens_list[0].value == "$MEM-MANUAL"