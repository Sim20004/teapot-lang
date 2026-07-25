import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "-i",
    "--input",
    help="Input source file",
    required=True
)

parser.add_argument(
    "-t",
    "--trace",
    help="Enable exhaustive debug output",
    action="store_true"
)

args = parser.parse_args()

trace = args.trace

from tokens import Token, TokenType, TYPE_KEYWORDS, KEYWORDS, SYMBOLS, BOOLEAN_LITERALS

class LexerError(Exception):
    def __init__(self, msg, line, col):
        super().__init__(f"Lexer error at {line}:{col}: {msg}")
        self.line = line
        self.col = col

if trace: print("Created LexerError class")


class Lexer:
    def __init__(self, source):
        if trace: print("Creating Lexer object")
        if trace: print(f"Original source: {repr(source)}")

        self.source = source.replace("\r\n", "\n")

        if self.source != source:
            if trace: print("Converted CRLF line endings to LF")
        else:
            if trace: print("No CRLF conversion needed")

        self.position = 0
        self.line = 1
        self.col = 1

        if trace: print("Initialised lexer position:")
        if trace: print(f"  position={self.position}")
        if trace: print(f"  line={self.line}")
        if trace: print(f"  col={self.col}")


    def current_character(self):
        if self.position >= len(self.source):
            if trace: print("Reached end of source")
            return None

        char = self.source[self.position]
        if trace: print(f"Current character: {repr(char)} at {self.line}:{self.col}")
        return char


    def advance(self):
        current = self.current_character()

        if trace: print(f"Advancing past character: {repr(current)}")

        if current == "\n":
            self.line += 1
            self.col = 1
            if trace: print("New line detected")
        else:
            self.col += 1

        self.position += 1

        if trace: print(
            f"New position: position={self.position}, "
            f"line={self.line}, col={self.col}"
        )


    def tokenise(self):
        if trace: print("Starting tokenisation")

        tokens = []

        while self.current_character() is not None:
            char = self.current_character()

            if trace: print(f"\nProcessing character: {repr(char)}")

            if char.isspace():
                if trace: print("Whitespace detected, skipping")
                self.advance()
                continue


            if char.isalpha() or char == "_":
                if trace: print("Identifier or keyword detected")
                token = self.read_word()
                if trace: print(f"Created token: {token}")
                tokens.append(token)
                continue


            if char.isdigit():
                if trace: print("Number detected")
                token = self.read_number()
                if trace: print(f"Created token: {token}")
                tokens.append(token)
                continue


            if char == '"':
                if trace: print("String detected")
                token = self.read_string()
                if trace: print(f"Created token: {token}")
                tokens.append(token)
                continue


            if trace: print("Symbol detected")
            token = self.read_symbol()
            if trace: print(f"Created token: {token}")
            tokens.append(token)


        eof = Token(TokenType.EOF, None, self.line, self.col)
        if trace: print(f"Adding EOF token: {eof}")

        tokens.append(eof)

        if trace: print("Tokenisation complete")
        if trace: print(f"Total tokens: {len(tokens)}")

        return tokens


    def read_word(self):
        if trace: print("Reading word")

        start_line = self.line
        start_col = self.col
        value = ""

        while self.current_character() and (
            self.current_character().isalnum()
            or self.current_character() == "_"
        ):
            char = self.current_character()
            if trace: print(f"Adding character to word: {repr(char)}")

            value += char
            self.advance()


        if trace: print(f"Finished word: {value}")


        if value in KEYWORDS:
            token_type = KEYWORDS[value]
            if trace: print("Word classified as keyword")

        elif value in TYPE_KEYWORDS:
            token_type = TokenType.TYPE
            if trace: print("Word classified as datatype")

        elif value in BOOLEAN_LITERALS:
            token_type = TokenType.BOOLEAN
            if trace: print("Word classified as boolean literal")

        else:
            token_type = TokenType.IDENTIFIER
            if trace: print("Word classified as identifier")


        return Token(
            token_type,
            value,
            start_line,
            start_col,
        )


    def read_number(self):
        if trace: print("Reading number")

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

            if trace: print(f"Adding number character: {repr(char)}")

            value += char


            if char == ".":
                if flt:
                    raise LexerError(
                        "Found duplicate floating point.",
                        self.line,
                        self.col
                    )

                if trace: print("Detected decimal point")
                flt = True


            self.advance()


        if flt:
            token_type = TokenType.FLOAT
            if trace: print("Number classified as FLOAT")
        else:
            token_type = TokenType.INTEGER
            if trace: print("Number classified as INTEGER")


        return Token(
            token_type,
            value,
            start_line,
            start_col,
        )


    def read_symbol(self):
        if trace: print("Reading symbol")

        start_line = self.line
        start_col = self.col

        first = self.current_character()

        if trace: print(f"First symbol character: {repr(first)}")

        self.advance()

        second = self.current_character()

        if trace: print(f"Second symbol character: {repr(second)}")


        if second is not None:
            two_char = first + second

            if trace: print(f"Checking two character symbol: {two_char}")

            if two_char in SYMBOLS:
                if trace: print("Found two character symbol")

                self.advance()

                return Token(
                    SYMBOLS[two_char],
                    two_char,
                    start_line,
                    start_col
                )


        if trace: print(f"Checking single character symbol: {first}")

        if first in SYMBOLS:
            if trace: print("Found single character symbol")

            return Token(
                SYMBOLS[first],
                first,
                start_line,
                start_col
            )


        raise LexerError(
            "Invalid symbol.",
            self.line,
            self.col
        )

    def read_string(self):
        if trace: print("Reading string")

        start_line = self.line
        start_col = self.col
        value = ""

        # Skip opening quote
        self.advance()

        while self.current_character() is not None and self.current_character() != '"':
            value += self.current_character()
            self.advance()

        if self.current_character() is None:
            raise LexerError(
                "Unterminated string.",
                start_line,
                start_col
            )

        # Skip closing quote
        self.advance()

        return Token(
            TokenType.STRING,
            value,
            start_line,
            start_col
        )

with open(args.input, "r") as input_file:
    source = input_file.read()

lexer = Lexer(source)

tokens = lexer.tokenise()

if trace: print("\nToken Object list:")

for token in tokens:
    if trace: print(token)

if trace: print("\nToken List\n")

for token in tokens:
    if trace:
        print(str(token.type).replace("TokenType.", ""))