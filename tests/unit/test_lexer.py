import pytest

from teapot import tokens
from teapot.lexer import Lexer, LexerError


# Basic cursor behavior and source normalization.
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


# Words are classified as identifiers, keywords, datatypes, or literals.
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


# Numeric scanning separates declaration periods from decimal points.
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
    lexer = Lexer(
        "val cdml foo = 0.1.\nval mdml bar = 0.2.\nval cf32 baz = 0.3.\nval mf32 qux = 0.4.\nval cf64 quux = 0.5.\nval mf64 corge = 0.6."
    )
    tokens_list = lexer.tokenise()

    count = 0.1
    offset = 0
    for i in range(6):
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


# Strings preserve their contents and report missing closing quotes.
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


# Symbol matching covers both single-character punctuation and compound operators.
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

    for expected_type in single_character_symbols.values():
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

    for expected_type in two_character_symbols.values():
        assert tokens_list.pop(0).type == expected_type


def test_invalid_symbol():
    lexer = Lexer("£")
    with pytest.raises(LexerError):
        lexer.tokenise()


def test_directives():
    lexer = Lexer("$MEM-MANUAL")
    tokens_list = lexer.tokenise()

    assert tokens_list[0].type == tokens.TokenType.DIRECTIVE
    assert tokens_list[0].value == "$MEM-MANUAL"
    lexer = Lexer("$MEM-GC")
    tokens_list = lexer.tokenise()

    assert tokens_list[0].type == tokens.TokenType.DIRECTIVE
    assert tokens_list[0].value == "$MEM-GC"


def test_invalid_directive():
    lexer = Lexer("$FOO")
    with pytest.raises(LexerError):
        lexer.tokenise()


def test_multiple_directive():
    lexer = Lexer("$MEM-GC\n$MEM-MANUAL")
    with pytest.raises(LexerError):
        lexer.tokenise()


# Token coordinates are measured from one-based line and column positions.
def test_line_and_col_tracking():
    lexer = Lexer("$MEM-MANUAL\nval mui8 foo = 8\nval mui8 bar = 10\n")
    tokens_list = lexer.tokenise()

    assert tokens_list[0].line == 1
    assert tokens_list[0].col == 1

    assert tokens_list[1].line == 2
    assert tokens_list[1].col == 1
    assert tokens_list[2].line == 2
    assert tokens_list[2].col == 5
    assert tokens_list[3].line == 2
    assert tokens_list[3].col == 10
    assert tokens_list[4].line == 2
    assert tokens_list[4].col == 14
    assert tokens_list[5].line == 2
    assert tokens_list[5].col == 16

    assert tokens_list[6].line == 3
    assert tokens_list[6].col == 1
    assert tokens_list[7].line == 3
    assert tokens_list[7].col == 5
    assert tokens_list[8].line == 3
    assert tokens_list[8].col == 10
    assert tokens_list[9].line == 3
    assert tokens_list[9].col == 14
    assert tokens_list[10].line == 3
    assert tokens_list[10].col == 16


def test_error_position():
    lexer = Lexer("val mui8 foo = 8\n$FOO")
    with pytest.raises(LexerError) as err_info:
        lexer.tokenise()
    err_line = err_info.value.line
    err_col = err_info.value.col
    assert err_line == 2
    assert err_col == 1


# This fixture exercises the lexer across a representative complete source file.
def test_mixed_source():
    lexer = Lexer(
        """
        $MEM-GC

        pub sct Person {
            cstr name.
            csi32 age.
        }

        pub enm Colour {
            Red.
            Green.
            Blue.
        }

        pub err DatabaseError {
            cstr message.
            csi32 code.
        }

        pub fc add(csi32 a, csi32 b = 5)!csi32 {
            exit a + b.
        }

        fc test(csi32 start, csi32 end)!void {

            val csi32 x = 10.
            val csi32 y = -5.
            val cbln flag = true.
            val cstr name = "Simar".
            val csi32[] numbers = [1, 2, 3, 4].

            x += 5.
            x *= 2.
            x /= 3.

            val csi32 z = (x + y) * 2.

            if (x > y && flag) {

                x = add(x, y).

            }
            elif (x == y) {

                x = 0.

            }
            else {

                x = 100.

            }

            while (x > 0) {
                x -= 1.
            }

            for (item : numbers) {
                exit 1.
            }

            val csi32 converted = x >> csi32.

            exit 1.
        }
        """
    )

    tokens_list = lexer.tokenise()

    assert tokens_list[0].type == tokens.TokenType.DIRECTIVE
    assert tokens_list[0].value == "$MEM-GC"

    assert tokens_list[1].type == tokens.TokenType.PUBLIC
    assert tokens_list[1].value == "pub"
    assert tokens_list[2].type == tokens.TokenType.STRUCT
    assert tokens_list[2].value == "sct"
    assert tokens_list[3].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[3].value == "Person"
    assert tokens_list[4].type == tokens.TokenType.OPEN_BRACE
    assert tokens_list[4].value == "{"
    assert tokens_list[5].type == tokens.TokenType.TYPE
    assert tokens_list[5].value == "cstr"
    assert tokens_list[6].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[6].value == "name"
    assert tokens_list[7].type == tokens.TokenType.PERIOD
    assert tokens_list[7].value == "."
    assert tokens_list[8].type == tokens.TokenType.TYPE
    assert tokens_list[8].value == "csi32"
    assert tokens_list[9].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[9].value == "age"
    assert tokens_list[10].type == tokens.TokenType.PERIOD
    assert tokens_list[10].value == "."
    assert tokens_list[11].type == tokens.TokenType.CLOSE_BRACE
    assert tokens_list[11].value == "}"

    assert tokens_list[12].type == tokens.TokenType.PUBLIC
    assert tokens_list[12].value == "pub"
    assert tokens_list[13].type == tokens.TokenType.ENUM
    assert tokens_list[13].value == "enm"
    assert tokens_list[14].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[14].value == "Colour"
    assert tokens_list[15].type == tokens.TokenType.OPEN_BRACE
    assert tokens_list[15].value == "{"
    assert tokens_list[16].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[16].value == "Red"
    assert tokens_list[17].type == tokens.TokenType.PERIOD
    assert tokens_list[17].value == "."
    assert tokens_list[18].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[18].value == "Green"
    assert tokens_list[19].type == tokens.TokenType.PERIOD
    assert tokens_list[19].value == "."
    assert tokens_list[20].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[20].value == "Blue"
    assert tokens_list[21].type == tokens.TokenType.PERIOD
    assert tokens_list[21].value == "."
    assert tokens_list[22].type == tokens.TokenType.CLOSE_BRACE
    assert tokens_list[22].value == "}"

    assert tokens_list[23].type == tokens.TokenType.PUBLIC
    assert tokens_list[23].value == "pub"
    assert tokens_list[24].type == tokens.TokenType.ERROR
    assert tokens_list[24].value == "err"
    assert tokens_list[25].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[25].value == "DatabaseError"
    assert tokens_list[26].type == tokens.TokenType.OPEN_BRACE
    assert tokens_list[26].value == "{"
    assert tokens_list[27].type == tokens.TokenType.TYPE
    assert tokens_list[27].value == "cstr"
    assert tokens_list[28].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[28].value == "message"
    assert tokens_list[29].type == tokens.TokenType.PERIOD
    assert tokens_list[29].value == "."
    assert tokens_list[30].type == tokens.TokenType.TYPE
    assert tokens_list[30].value == "csi32"
    assert tokens_list[31].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[31].value == "code"
    assert tokens_list[32].type == tokens.TokenType.PERIOD
    assert tokens_list[32].value == "."
    assert tokens_list[33].type == tokens.TokenType.CLOSE_BRACE
    assert tokens_list[33].value == "}"

    assert tokens_list[34].type == tokens.TokenType.PUBLIC
    assert tokens_list[34].value == "pub"
    assert tokens_list[35].type == tokens.TokenType.FUNCTION
    assert tokens_list[35].value == "fc"
    assert tokens_list[36].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[36].value == "add"
    assert tokens_list[37].type == tokens.TokenType.OPEN_PAREN
    assert tokens_list[37].value == "("
    assert tokens_list[38].type == tokens.TokenType.TYPE
    assert tokens_list[38].value == "csi32"
    assert tokens_list[39].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[39].value == "a"
    assert tokens_list[40].type == tokens.TokenType.COMMA
    assert tokens_list[40].value == ","
    assert tokens_list[41].type == tokens.TokenType.TYPE
    assert tokens_list[41].value == "csi32"
    assert tokens_list[42].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[42].value == "b"
    assert tokens_list[43].type == tokens.TokenType.ASSIGN
    assert tokens_list[43].value == "="
    assert tokens_list[44].type == tokens.TokenType.INTEGER
    assert tokens_list[44].value == 5
    assert tokens_list[45].type == tokens.TokenType.CLOSE_PAREN
    assert tokens_list[45].value == ")"
    assert tokens_list[46].type == tokens.TokenType.EXCLAMATION
    assert tokens_list[46].value == "!"
    assert tokens_list[47].type == tokens.TokenType.TYPE
    assert tokens_list[47].value == "csi32"
    assert tokens_list[48].type == tokens.TokenType.OPEN_BRACE
    assert tokens_list[48].value == "{"
    assert tokens_list[49].type == tokens.TokenType.EXIT
    assert tokens_list[49].value == "exit"
    assert tokens_list[50].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[50].value == "a"
    assert tokens_list[51].type == tokens.TokenType.PLUS
    assert tokens_list[51].value == "+"
    assert tokens_list[52].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[52].value == "b"
    assert tokens_list[53].type == tokens.TokenType.PERIOD
    assert tokens_list[53].value == "."
    assert tokens_list[54].type == tokens.TokenType.CLOSE_BRACE
    assert tokens_list[54].value == "}"

    assert tokens_list[55].type == tokens.TokenType.FUNCTION
    assert tokens_list[55].value == "fc"
    assert tokens_list[56].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[56].value == "test"
    assert tokens_list[57].type == tokens.TokenType.OPEN_PAREN
    assert tokens_list[57].value == "("
    assert tokens_list[58].type == tokens.TokenType.TYPE
    assert tokens_list[58].value == "csi32"
    assert tokens_list[59].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[59].value == "start"
    assert tokens_list[60].type == tokens.TokenType.COMMA
    assert tokens_list[60].value == ","
    assert tokens_list[61].type == tokens.TokenType.TYPE
    assert tokens_list[61].value == "csi32"
    assert tokens_list[62].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[62].value == "end"
    assert tokens_list[63].type == tokens.TokenType.CLOSE_PAREN
    assert tokens_list[63].value == ")"
    assert tokens_list[64].type == tokens.TokenType.EXCLAMATION
    assert tokens_list[64].value == "!"
    assert tokens_list[65].type == tokens.TokenType.TYPE
    assert tokens_list[65].value == "void"
    assert tokens_list[66].type == tokens.TokenType.OPEN_BRACE
    assert tokens_list[66].value == "{"

    assert tokens_list[67].type == tokens.TokenType.VAL
    assert tokens_list[67].value == "val"
    assert tokens_list[68].type == tokens.TokenType.TYPE
    assert tokens_list[68].value == "csi32"
    assert tokens_list[69].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[69].value == "x"
    assert tokens_list[70].type == tokens.TokenType.ASSIGN
    assert tokens_list[70].value == "="
    assert tokens_list[71].type == tokens.TokenType.INTEGER
    assert tokens_list[71].value == 10
    assert tokens_list[72].type == tokens.TokenType.PERIOD
    assert tokens_list[72].value == "."

    assert tokens_list[73].type == tokens.TokenType.VAL
    assert tokens_list[73].value == "val"
    assert tokens_list[74].type == tokens.TokenType.TYPE
    assert tokens_list[74].value == "csi32"
    assert tokens_list[75].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[75].value == "y"
    assert tokens_list[76].type == tokens.TokenType.ASSIGN
    assert tokens_list[76].value == "="
    assert tokens_list[77].type == tokens.TokenType.MINUS
    assert tokens_list[77].value == "-"
    assert tokens_list[78].type == tokens.TokenType.INTEGER
    assert tokens_list[78].value == 5
    assert tokens_list[79].type == tokens.TokenType.PERIOD
    assert tokens_list[79].value == "."

    assert tokens_list[80].type == tokens.TokenType.VAL
    assert tokens_list[80].value == "val"
    assert tokens_list[81].type == tokens.TokenType.TYPE
    assert tokens_list[81].value == "cbln"
    assert tokens_list[82].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[82].value == "flag"
    assert tokens_list[83].type == tokens.TokenType.ASSIGN
    assert tokens_list[83].value == "="
    assert tokens_list[84].type == tokens.TokenType.BOOLEAN
    assert tokens_list[84].value is True
    assert tokens_list[85].type == tokens.TokenType.PERIOD
    assert tokens_list[85].value == "."

    assert tokens_list[86].type == tokens.TokenType.VAL
    assert tokens_list[86].value == "val"
    assert tokens_list[87].type == tokens.TokenType.TYPE
    assert tokens_list[87].value == "cstr"
    assert tokens_list[88].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[88].value == "name"
    assert tokens_list[89].type == tokens.TokenType.ASSIGN
    assert tokens_list[89].value == "="
    assert tokens_list[90].type == tokens.TokenType.STRING
    assert tokens_list[90].value == "Simar"
    assert tokens_list[91].type == tokens.TokenType.PERIOD
    assert tokens_list[91].value == "."

    assert tokens_list[92].type == tokens.TokenType.VAL
    assert tokens_list[92].value == "val"
    assert tokens_list[93].type == tokens.TokenType.TYPE
    assert tokens_list[93].value == "csi32"
    assert tokens_list[94].type == tokens.TokenType.OPEN_BRACKET
    assert tokens_list[94].value == "["
    assert tokens_list[95].type == tokens.TokenType.CLOSE_BRACKET
    assert tokens_list[95].value == "]"
    assert tokens_list[96].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[96].value == "numbers"
    assert tokens_list[97].type == tokens.TokenType.ASSIGN
    assert tokens_list[97].value == "="
    assert tokens_list[98].type == tokens.TokenType.OPEN_BRACKET
    assert tokens_list[98].value == "["
    assert tokens_list[99].type == tokens.TokenType.INTEGER
    assert tokens_list[99].value == 1
    assert tokens_list[100].type == tokens.TokenType.COMMA
    assert tokens_list[100].value == ","
    assert tokens_list[101].type == tokens.TokenType.INTEGER
    assert tokens_list[101].value == 2
    assert tokens_list[102].type == tokens.TokenType.COMMA
    assert tokens_list[102].value == ","
    assert tokens_list[103].type == tokens.TokenType.INTEGER
    assert tokens_list[103].value == 3
    assert tokens_list[104].type == tokens.TokenType.COMMA
    assert tokens_list[104].value == ","
    assert tokens_list[105].type == tokens.TokenType.INTEGER
    assert tokens_list[105].value == 4
    assert tokens_list[106].type == tokens.TokenType.CLOSE_BRACKET
    assert tokens_list[106].value == "]"
    assert tokens_list[107].type == tokens.TokenType.PERIOD
    assert tokens_list[107].value == "."

    assert tokens_list[108].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[108].value == "x"
    assert tokens_list[109].type == tokens.TokenType.ASSIGN_PLUS
    assert tokens_list[109].value == "+="
    assert tokens_list[110].type == tokens.TokenType.INTEGER
    assert tokens_list[110].value == 5
    assert tokens_list[111].type == tokens.TokenType.PERIOD
    assert tokens_list[111].value == "."

    assert tokens_list[112].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[112].value == "x"
    assert tokens_list[113].type == tokens.TokenType.ASSIGN_MULTIPLY
    assert tokens_list[113].value == "*="
    assert tokens_list[114].type == tokens.TokenType.INTEGER
    assert tokens_list[114].value == 2
    assert tokens_list[115].type == tokens.TokenType.PERIOD
    assert tokens_list[115].value == "."

    assert tokens_list[116].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[116].value == "x"
    assert tokens_list[117].type == tokens.TokenType.ASSIGN_DIVIDE
    assert tokens_list[117].value == "/="
    assert tokens_list[118].type == tokens.TokenType.INTEGER
    assert tokens_list[118].value == 3
    assert tokens_list[119].type == tokens.TokenType.PERIOD
    assert tokens_list[119].value == "."

    assert tokens_list[120].type == tokens.TokenType.VAL
    assert tokens_list[120].value == "val"
    assert tokens_list[121].type == tokens.TokenType.TYPE
    assert tokens_list[121].value == "csi32"
    assert tokens_list[122].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[122].value == "z"
    assert tokens_list[123].type == tokens.TokenType.ASSIGN
    assert tokens_list[123].value == "="
    assert tokens_list[124].type == tokens.TokenType.OPEN_PAREN
    assert tokens_list[124].value == "("
    assert tokens_list[125].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[125].value == "x"
    assert tokens_list[126].type == tokens.TokenType.PLUS
    assert tokens_list[126].value == "+"
    assert tokens_list[127].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[127].value == "y"
    assert tokens_list[128].type == tokens.TokenType.CLOSE_PAREN
    assert tokens_list[128].value == ")"
    assert tokens_list[129].type == tokens.TokenType.MULTIPLY
    assert tokens_list[129].value == "*"
    assert tokens_list[130].type == tokens.TokenType.INTEGER
    assert tokens_list[130].value == 2
    assert tokens_list[131].type == tokens.TokenType.PERIOD
    assert tokens_list[131].value == "."

    assert tokens_list[132].type == tokens.TokenType.IF
    assert tokens_list[132].value == "if"
    assert tokens_list[133].type == tokens.TokenType.OPEN_PAREN
    assert tokens_list[133].value == "("
    assert tokens_list[134].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[134].value == "x"
    assert tokens_list[135].type == tokens.TokenType.GREATER
    assert tokens_list[135].value == ">"
    assert tokens_list[136].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[136].value == "y"
    assert tokens_list[137].type == tokens.TokenType.AND
    assert tokens_list[137].value == "&&"
    assert tokens_list[138].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[138].value == "flag"
    assert tokens_list[139].type == tokens.TokenType.CLOSE_PAREN
    assert tokens_list[139].value == ")"
    assert tokens_list[140].type == tokens.TokenType.OPEN_BRACE
    assert tokens_list[140].value == "{"

    assert tokens_list[141].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[141].value == "x"
    assert tokens_list[142].type == tokens.TokenType.ASSIGN
    assert tokens_list[142].value == "="
    assert tokens_list[143].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[143].value == "add"
    assert tokens_list[144].type == tokens.TokenType.OPEN_PAREN
    assert tokens_list[144].value == "("
    assert tokens_list[145].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[145].value == "x"
    assert tokens_list[146].type == tokens.TokenType.COMMA
    assert tokens_list[146].value == ","
    assert tokens_list[147].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[147].value == "y"
    assert tokens_list[148].type == tokens.TokenType.CLOSE_PAREN
    assert tokens_list[148].value == ")"
    assert tokens_list[149].type == tokens.TokenType.PERIOD
    assert tokens_list[149].value == "."

    assert tokens_list[150].type == tokens.TokenType.CLOSE_BRACE
    assert tokens_list[150].value == "}"

    assert tokens_list[151].type == tokens.TokenType.ELSEIF
    assert tokens_list[151].value == "elif"
    assert tokens_list[152].type == tokens.TokenType.OPEN_PAREN
    assert tokens_list[152].value == "("
    assert tokens_list[153].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[153].value == "x"
    assert tokens_list[154].type == tokens.TokenType.EQUALS
    assert tokens_list[154].value == "=="
    assert tokens_list[155].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[155].value == "y"
    assert tokens_list[156].type == tokens.TokenType.CLOSE_PAREN
    assert tokens_list[156].value == ")"
    assert tokens_list[157].type == tokens.TokenType.OPEN_BRACE
    assert tokens_list[157].value == "{"

    assert tokens_list[158].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[158].value == "x"
    assert tokens_list[159].type == tokens.TokenType.ASSIGN
    assert tokens_list[159].value == "="
    assert tokens_list[160].type == tokens.TokenType.INTEGER
    assert tokens_list[160].value == 0
    assert tokens_list[161].type == tokens.TokenType.PERIOD
    assert tokens_list[161].value == "."

    assert tokens_list[162].type == tokens.TokenType.CLOSE_BRACE
    assert tokens_list[162].value == "}"

    assert tokens_list[163].type == tokens.TokenType.ELSE
    assert tokens_list[163].value == "else"
    assert tokens_list[164].type == tokens.TokenType.OPEN_BRACE
    assert tokens_list[164].value == "{"

    assert tokens_list[165].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[165].value == "x"
    assert tokens_list[166].type == tokens.TokenType.ASSIGN
    assert tokens_list[166].value == "="
    assert tokens_list[167].type == tokens.TokenType.INTEGER
    assert tokens_list[167].value == 100
    assert tokens_list[168].type == tokens.TokenType.PERIOD
    assert tokens_list[168].value == "."

    assert tokens_list[169].type == tokens.TokenType.CLOSE_BRACE
    assert tokens_list[169].value == "}"

    assert tokens_list[170].type == tokens.TokenType.WHILE
    assert tokens_list[170].value == "while"
    assert tokens_list[171].type == tokens.TokenType.OPEN_PAREN
    assert tokens_list[171].value == "("
    assert tokens_list[172].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[172].value == "x"
    assert tokens_list[173].type == tokens.TokenType.GREATER
    assert tokens_list[173].value == ">"
    assert tokens_list[174].type == tokens.TokenType.INTEGER
    assert tokens_list[174].value == 0
    assert tokens_list[175].type == tokens.TokenType.CLOSE_PAREN
    assert tokens_list[175].value == ")"
    assert tokens_list[176].type == tokens.TokenType.OPEN_BRACE
    assert tokens_list[176].value == "{"

    assert tokens_list[177].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[177].value == "x"
    assert tokens_list[178].type == tokens.TokenType.ASSIGN_MINUS
    assert tokens_list[178].value == "-="
    assert tokens_list[179].type == tokens.TokenType.INTEGER
    assert tokens_list[179].value == 1
    assert tokens_list[180].type == tokens.TokenType.PERIOD
    assert tokens_list[180].value == "."

    assert tokens_list[181].type == tokens.TokenType.CLOSE_BRACE
    assert tokens_list[181].value == "}"

    assert tokens_list[182].type == tokens.TokenType.FOR
    assert tokens_list[182].value == "for"
    assert tokens_list[183].type == tokens.TokenType.OPEN_PAREN
    assert tokens_list[183].value == "("
    assert tokens_list[184].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[184].value == "item"
    assert tokens_list[185].type == tokens.TokenType.COLON
    assert tokens_list[185].value == ":"
    assert tokens_list[186].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[186].value == "numbers"
    assert tokens_list[187].type == tokens.TokenType.CLOSE_PAREN
    assert tokens_list[187].value == ")"
    assert tokens_list[188].type == tokens.TokenType.OPEN_BRACE
    assert tokens_list[188].value == "{"

    assert tokens_list[189].type == tokens.TokenType.EXIT
    assert tokens_list[189].value == "exit"
    assert tokens_list[190].type == tokens.TokenType.INTEGER
    assert tokens_list[190].value == 1
    assert tokens_list[191].type == tokens.TokenType.PERIOD
    assert tokens_list[191].value == "."

    assert tokens_list[192].type == tokens.TokenType.CLOSE_BRACE
    assert tokens_list[192].value == "}"

    assert tokens_list[193].type == tokens.TokenType.VAL
    assert tokens_list[193].value == "val"
    assert tokens_list[194].type == tokens.TokenType.TYPE
    assert tokens_list[194].value == "csi32"
    assert tokens_list[195].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[195].value == "converted"
    assert tokens_list[196].type == tokens.TokenType.ASSIGN
    assert tokens_list[196].value == "="
    assert tokens_list[197].type == tokens.TokenType.IDENTIFIER
    assert tokens_list[197].value == "x"
    assert tokens_list[198].type == tokens.TokenType.CAST
    assert tokens_list[198].value == ">>"
    assert tokens_list[199].type == tokens.TokenType.TYPE
    assert tokens_list[199].value == "csi32"
    assert tokens_list[200].type == tokens.TokenType.PERIOD
    assert tokens_list[200].value == "."

    assert tokens_list[201].type == tokens.TokenType.EXIT
    assert tokens_list[201].value == "exit"
    assert tokens_list[202].type == tokens.TokenType.INTEGER
    assert tokens_list[202].value == 1
    assert tokens_list[203].type == tokens.TokenType.PERIOD
    assert tokens_list[203].value == "."

    assert tokens_list[204].type == tokens.TokenType.CLOSE_BRACE
    assert tokens_list[204].value == "}"

    assert tokens_list[205].type == tokens.TokenType.EOF
    assert tokens_list[205].value is None
