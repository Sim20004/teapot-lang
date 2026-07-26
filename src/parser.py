from sys import exit as leave
import src.teapot_ast as ast
import src.tokens as tokens

trace = False

if __name__ == "__main__":
    leave("Cannot run this file directly! Run `python main.py -h` for info on how to start the compiler")

class ParserError(Exception):
    def __init__(self, msg, token, position):
        super().__init__(f"Parser error at token {token} at position {position}: {msg}")
        self.token = token
        self.position = position

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0
        self.ast_tree = []

    def current_token(self):
        if not self.at_end():
            return self.tokens[self.position]

    def at_end(self):
        return self.position >= len(self.tokens)

    def advance(self):
        token = self.current_token()
        if not self.at_end():
            self.position += 1
        return token

    def expect(self, token):
        if self.at_end():
            raise ParserError("Tried to expect a nonexistent token", token, self.position)
        if self.current_token() != token:
            raise ParserError(f"Expected token {token}, found {self.current_token()} instead.")
        return self.advance()
    
    def handle_variable(self):
        if self.current_token() == tokens.TokenType.TYPE:
            datatype = self.current_token().value
            self.advance()
            if self.current_token() == tokens.TokenType.IDENTIFIER:
                identifier = self.current_token().value
                self.advance()
                if self.current_token() == tokens.TokenType.ASSIGN:
                    self.advance()
                    if self.current_token() == tokens.TokenType.FLOAT or tokens.TokenType.INTEGER:
                        value = self.current_token().value
                        self.advance()
                        return ast.DeclareVariable (
                            identifier,
                            datatype,
                            value
                        )

    def parse(self):
        while self.current_token():
            if self.current_token() == tokens.TokenType.VAL:
                self.advance()
                self.ast_tree.append(self.handle_variable())
                
        return self.ast_tree
                
            


def run(tokens_from_lexer, trace_arg):
    trace = trace_arg
    parser = Parser(tokens_from_lexer)
    ast_tree = parser.parse()