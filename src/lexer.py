from tokens import Token, TokenType, TYPE_KEYWORDS, KEYWORDS, BOOLEAN_LITERALS

class Lexer:
    def __init__(self, source):
        self.source = source.replace("\r\n", "\n")
        self.position = 0
        self.line = 1
        self.col = 1

    def current_character(self):
        if self.position >= len(self.source):
            return None
        return self.source[self.position]

    def advance(self):
        if self.current_character() == "\n":
            self.line += 1
            self.col += 1
        else:
            self.col += 1   

        self.position += 1

    def tokenise(self):
        tokens = []

        while self.current_character() is not None:
            char = self.current_character()

            # Whitespace
            if char.isspace():
                self.advance()
                continue
            # Identifiers/keywords
            if char.isalpha() or char == "_":
                tokens.append(self.read_word())
                continue
            # Numbers
            if char.isdigit():
                tokens.append(self.read_number())
                continue
            # Strings
            if char == '"':
                tokens.append(self.read_string())
                continue

            tokens.append(self.read_symbol())

        tokens.append(Token(TokenType.EOF))

        return tokens

    def read_word(self):
        start_col = self.col
        value = ""

        while self.current_character() and (
            self.current_character().isalnum()
            or self.current_character() == "_"
        ):
            value += self.current_character()
            self.advance()
        if value in KEYWORDS:
            token_type = KEYWORDS[value]

        elif value in TYPE_KEYWORDS:
            token_type = TokenType.TYPE

        elif value in BOOLEAN_LITERALS:
            token_type = TokenType.BOOLEAN

        else:
            token_type = TokenType.IDENTIFIER

        return Token (
            token_type,
            value,
            self.line,
            start_col
        )
        
lexer = Lexer("val ui8 x = 5.")
tokens = lexer.tokenise()
print(tokens)

