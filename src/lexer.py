from sys import exit

from src.parser import run as run_parser
from src.tokens import (
    BOOLEAN_LITERALS,
    DIRECTIVES,
    KEYWORDS,
    SYMBOLS,
    TYPE_KEYWORDS,
    Token,
    TokenType,
)

if __name__ == "__main__":
    exit(
        "Cannot run this file directly! Run `python main.py -h` for info on how to start the compiler"
    )

trace = False


class LexerError(Exception):
    def __init__(self, msg, line, col):
        super().__init__(f"Lexer error at {line}:{col}: {msg}")
        self.line = line
        self.col = col


if trace:
    print("Created LexerError class")


class Lexer:
    def __init__(self, source):
        if trace:
            print("Creating Lexer object")
        if trace:
            print(f"Original source: {source!r}")

        self.source = source.replace("\r\n", "\n")

        if self.source != source:
            if trace:
                print("Converted CRLF line endings to LF")
        else:
            if trace:
                print("No CRLF conversion needed")

        self.position = 0
        self.line = 1
        self.col = 1
        self.tokens = []

        if trace:
            print("Initialised lexer position:")
        if trace:
            print(f"  position={self.position}")
        if trace:
            print(f"  line={self.line}")
        if trace:
            print(f"  col={self.col}")

    def current_character(self):
        if self.position >= len(self.source):
            if trace:
                print("Reached end of source")
            return None

        char = self.source[self.position]
        if trace:
            print(f"Current character: {char!r} at {self.line}:{self.col}")
        return char

    def advance(self):
        current = self.current_character()

        if trace:
            print(f"Advancing past character: {current!r}")

        if current == "\n":
            self.line += 1
            self.col = 1
            if trace:
                print("New line detected")
        else:
            self.col += 1

        self.position += 1

        if trace:
            print(
                f"New position: position={self.position}, "
                f"line={self.line}, col={self.col}"
            )

    def tokenise(self):
        directive_seen = False

        while self.current_character() is not None:
            char = self.current_character()

            if char == "$":
                start_line = self.line
                start_col = self.col
                value = ""

                while (
                    self.current_character() is not None
                    and self.current_character() != "\n"
                ):
                    value += self.current_character()
                    self.advance()

                if directive_seen:
                    raise LexerError(
                        "Directive must only appear once", start_line, start_col
                    )

                if value in DIRECTIVES:
                    self.tokens.append(
                        Token(TokenType.DIRECTIVE, value, start_line, start_col)
                    )
                    directive_seen = True
                    continue

                raise LexerError("Invalid directive", start_line, start_col)

            if (
                char == "/"
                and self.position + 1 < len(self.source)
                and self.source[self.position + 1] == "/"
            ):
                if trace:
                    print("Found comment")
                while (
                    self.current_character() is not None
                    and self.current_character() != "\n"
                ):
                    self.advance()
                continue

            if char.isspace():
                if trace:
                    print("Whitespace detected, skipping")
                self.advance()
                continue

            if char.isalpha() or char == "_":
                if trace:
                    print("Identifier or keyword detected")
                token = self.read_word()
                if trace:
                    print(f"Created token: {token}")
                self.tokens.append(token)
                continue

            if char.isdigit():
                if trace:
                    print("Number detected")
                token = self.read_number()
                if trace:
                    print(f"Created token: {token}")
                self.tokens.append(token)
                continue

            if char == '"':
                if trace:
                    print("String detected")
                token = self.read_string()
                if trace:
                    print(f"Created token: {token}")
                self.tokens.append(token)
                continue

            if trace:
                print("Symbol detected")
            token = self.read_symbol()
            if trace:
                print(f"Created token: {token}")
            self.tokens.append(token)

        eof = Token(TokenType.EOF, None, self.line, self.col)
        if trace:
            print(f"Adding EOF token: {eof}")

        self.tokens.append(eof)

        if trace:
            print("Tokenisation complete")
        if trace:
            print(f"Total tokens: {len(self.tokens)}")

        return self.tokens

    def read_word(self):
        if trace:
            print("Reading word")

        start_line = self.line
        start_col = self.col
        value = ""

        while self.current_character() and (
            self.current_character().isalnum() or self.current_character() == "_"
        ):
            char = self.current_character()
            if trace:
                print(f"Adding character to word: {char!r}")

            value += char
            self.advance()

        if trace:
            print(f"Finished word: {value}")

        if value in KEYWORDS:
            token_type = KEYWORDS[value]
            if trace:
                print("Word classified as keyword")

        elif value in TYPE_KEYWORDS:
            token_type = TokenType.TYPE
            if trace:
                print("Word classified as datatype")

        elif value in BOOLEAN_LITERALS:
            token_type = TokenType.BOOLEAN
            if trace:
                print("Word classified as boolean literal")
            if value == "true":
                value = True
            else:
                value = False

        else:
            token_type = TokenType.IDENTIFIER
            if trace:
                print("Word classified as identifier")

        return Token(
            token_type,
            value,
            start_line,
            start_col,
        )

    def read_number(self):
        if trace:
            print("Reading number")

        start_line = self.line
        start_col = self.col
        value = ""
        flt = False

        while self.current_character() and (
            self.current_character().isdigit()
            or (
                self.current_character() == "."
                and self.position + 1 < len(self.source)
                and self.source[self.position + 1].isdigit()
            )
        ):

            char = self.current_character()

            if trace:
                print(f"Adding number character: {char!r}")

            value += char

            if char == ".":
                if flt:
                    raise LexerError(
                        "Found duplicate floating point.", self.line, self.col
                    )

                if trace:
                    print("Detected decimal point")
                flt = True

            self.advance()

        if flt:
            token_type = TokenType.FLOAT
            if trace:
                print("Number classified as FLOAT")
            value = float(value)
        else:
            token_type = TokenType.INTEGER
            if trace:
                print("Number classified as INTEGER")
            value = int(value)

        return Token(
            token_type,
            value,
            start_line,
            start_col,
        )

    def read_symbol(self):
        if trace:
            print("Reading symbol")

        start_line = self.line
        start_col = self.col

        first = self.current_character()

        if trace:
            print(f"First symbol character: {first!r}")

        self.advance()

        second = self.current_character()

        if trace:
            print(f"Second symbol character: {second!r}")

        if second is not None:
            two_char = first + second

            if trace:
                print(f"Checking two character symbol: {two_char}")

            if two_char in SYMBOLS:
                if trace:
                    print("Found two character symbol")

                self.advance()

                return Token(SYMBOLS[two_char], two_char, start_line, start_col)

        if trace:
            print(f"Checking single character symbol: {first}")

        if first in SYMBOLS:
            if trace:
                print("Found single character symbol")

            return Token(SYMBOLS[first], first, start_line, start_col)

        raise LexerError("Invalid symbol.", start_line, start_col)

    def read_string(self):
        if trace:
            print("Reading string")

        start_line = self.line
        start_col = self.col
        value = ""

        # Skip opening quote
        self.advance()

        while self.current_character() is not None and self.current_character() != '"':
            value += self.current_character()
            self.advance()

        if self.current_character() is None:
            raise LexerError("Unterminated string.", start_line, start_col)

        # Skip closing quote
        self.advance()

        return Token(TokenType.STRING, str(value), start_line, start_col)


def run(source, trace):
    lexer = Lexer(source)

    tokens = lexer.tokenise()

    if trace:
        print("\nToken Object list:")

    for token in tokens:
        if trace:
            print(token)

    if trace:
        print("\nToken List\n")

    for token in tokens:
        if trace:
            print(str(token.type).replace("TokenType.", ""))

    return run_parser(tokens, trace)


# TODO: Lexer improvements
#
# [x] Add memory management thing and make main main file
# [x] Add single-line comments
#     Example: // This is a comment
#
# [x] Syntax error trace fix with identifier consumation
#
# [ ] Add multi-line comments (if supported)
#     Example:
#         /*
#             Comment
#         */
#
# [ ] Add character literal support
#     Example: 'A'
#
# [ ] Add string escape sequence handling
#     Support:
#         \n  newline
#         \t  tab
#         \"  quote
#         \\  backslash
#
# [ ] Improve unterminated string errors
#     Include the starting position of the string
#
# [ ] Improve invalid symbol error positions
#     Report the actual invalid character location
#
# [ ] Decide whether invalid identifiers are allowed
#     Example: 123abc
#
# [ ] Add hexadecimal integer support (optional)
#     Example: 0xFF
#
# [ ] Add binary integer support (optional)
#     Example: 0b1010
#
# [ ] Add numeric separators (optional)
#     Example: 1_000_000
#
# [ ] Add scientific notation support (optional)
#     Example: 1.5e10
#
# [ ] Add negative number handling decision
#     Decide whether lexer or parser handles unary minus
#
# [ ] Add lexer unit tests
#     Test:
#         - keywords
#         - identifiers
#         - types
#         - numbers
#         - strings
#         - operators
#         - errors
#
# [ ] Replace print debugging with logging module
#
# [ ] Add token pretty printer
#     Example:
#         LINE:COL  TYPE            VALUE
#
# [ ] Add documentation/comments for lexer functions
#
# [ ] Verify all TokenType values are handled
#     Ensure no token exists without lexer support
