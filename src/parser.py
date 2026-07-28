from sys import exit as leave
import src.teapot_ast as ast
import src.tokens as tokens

trace = False

if __name__ == "__main__":
    leave(
        "Cannot run this file directly! Run `python main.py -h` for info on how to start the compiler"
    )


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
            raise ParserError(
                "Tried to expect a nonexistent token", token, self.position
            )
        if self.current_token().type != token:
            raise ParserError(
                f"Expected token {token}, found {self.current_token()} instead.",
                token,
                self.position,
            )
        return self.advance()

    def handle_variable(self):
        datatype = self.expect(tokens.TokenType.TYPE).value
        identifier = self.expect(tokens.TokenType.IDENTIFIER).value
        self.expect(tokens.TokenType.ASSIGN)
        value = self.handle_expression()
        self.expect(tokens.TokenType.PERIOD)
        return ast.DeclareVariable(identifier, datatype, value)

    def handle_primary(self):
        token = self.current_token()
        if token.type in [
            tokens.TokenType.INTEGER,
            tokens.TokenType.FLOAT,
            tokens.TokenType.BOOLEAN,
            tokens.TokenType.STRING,
            tokens.TokenType.IDENTIFIER,
        ]:
            self.advance()
            if token.type == tokens.TokenType.IDENTIFIER:
                side = ast.Identifier(token.value)
            else:
                side = ast.Literal(token.value)
        else:
            raise ParserError("Invalid expression", token, self.position)
        
        return side

    def handle_expression(self):
        operator = None
        token = self.current_token()
        unary = False

        if token.type == tokens.TokenType.NOT:
            unary = True
            operator = token.value
            self.advance()
            token = self.current_token()

        left_side = self.handle_primary()

        if unary:
            return ast.UnaryExpression(operator, left_side)

        while (
            not self.at_end() and self.current_token().type != tokens.TokenType.PERIOD
        ):
            token = self.current_token()
            if token.type in [
                tokens.TokenType.PLUS,
                tokens.TokenType.MINUS,
                tokens.TokenType.MULTIPLY,
                tokens.TokenType.DIVIDE,
                tokens.TokenType.MODULO,
                tokens.TokenType.POWER,
            ]:
                operator = token.value
                self.advance()
                token = self.current_token()
            else:
                raise ParserError("Invalid operator found", token, self.position)

            right_side = self.handle_primary()

            left_side = ast.BinaryExpression(left_side, operator, right_side)

        return left_side

    def parse(self):
        while self.current_token().type != tokens.TokenType.EOF:
            if self.current_token().type == tokens.TokenType.VAL:
                self.advance()
                self.ast_tree.append(self.handle_variable())
            else:
                raise ParserError(
                    "Invalid token found", self.current_token(), self.position
                )
        program = ast.Program(self.ast_tree)
        return program


def run(tokens_from_lexer, trace_arg):
    trace = trace_arg
    parser = Parser(tokens_from_lexer)
    ast_tree = parser.parse()

    def print_ast(node, indent=0):  # Temporary debugging
        spacing = " " * indent

        if hasattr(node, "__dict__"):
            print(f"{spacing}{type(node).__name__}:")
            for key, value in vars(node).items():
                print(f"{spacing}  {key}:")
                if hasattr(value, "__dict__"):
                    print_ast(value, indent + 4)
                elif isinstance(value, list):
                    for item in value:
                        if hasattr(item, "__dict__"):
                            print_ast(item, indent + 4)
                        else:
                            print(f"{spacing}    {item}")
                else:
                    print(f"{spacing}    {value}")
        else:
            print(f"{spacing}{node}")
    if trace:
        print_ast(ast_tree)
