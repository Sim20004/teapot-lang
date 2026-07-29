from sys import exit as leave

from src.debug import print

if __name__ == "__main__":
    leave(
        "Cannot run this file directly! Run `python main.py -h` for info on how to start the compiler"
    )


import src.teapot_ast as ast
from src import tokens

trace = False


class ParserError(Exception):
    def __init__(self, msg, token, position):
        super().__init__(f"Parser error at token {token} at position {position}: {msg}")
        self.token = token
        self.position = position
        print(f"\nParser error at token {token} at position {position}: {msg}")


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0
        self.ast_tree = []
        self.memory_mode = None
        self.DATATYPES_MUTABILITY = {
            "mstr": True,
            "mbln": True,
            "msi8": True,
            "msi16": True,
            "msi32": True,
            "msi64": True,
            "mui8": True,
            "mui16": True,
            "mui32": True,
            "mui64": True,
            "maint": True,
            "mf32": True,
            "mf64": True,
            "mdml": True,
            "cstr": False,
            "cbln": False,
            "csi8": False,
            "csi16": False,
            "csi32": False,
            "csi64": False,
            "cui8": False,
            "cui16": False,
            "cui32": False,
            "cui64": False,
            "caint": False,
            "cf32": False,
            "cf64": False,
            "cdml": False,
            "void": False,
        }


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

    def handle_block(self):
        self.expect(tokens.TokenType.OPEN_BRACE)
        block = []
        while not self.at_end() and self.current_token().type != tokens.TokenType.CLOSE_BRACE:
            block.append(self.handle_statement())
        self.advance()
        return block

    def get_precedence(self, token):
        PRECEDENCES = {
            tokens.TokenType.PLUS: 1,
            tokens.TokenType.MINUS: 1,

            tokens.TokenType.MODULO: 2,
            tokens.TokenType.DIVIDE: 2,
            tokens.TokenType.MULTIPLY: 2,

            tokens.TokenType.POWER: 3,
        }

        return PRECEDENCES.get(token.type, -1)

    def handle_function_argument(self):
        args = []

        datatype = self.expect(tokens.TokenType.TYPE).value
        identifier = self.expect(tokens.TokenType.IDENTIFIER).value
        args.append(ast.FunctionArgument(identifier, datatype))

        while self.current_token().type == tokens.TokenType.COMMA:
            self.advance()
            datatype = self.expect(tokens.TokenType.TYPE).value
            identifier = self.expect(tokens.TokenType.IDENTIFIER).value
            args.append(ast.FunctionArgument(identifier, datatype))

        return args

    def handle_function(self):
        args = []
        name = self.expect(tokens.TokenType.IDENTIFIER).value
        self.expect(tokens.TokenType.OPEN_PAREN)
        if self.current_token().type != tokens.TokenType.CLOSE_PAREN:
            args = self.handle_function_argument()
        self.expect(tokens.TokenType.CLOSE_PAREN)
        self.expect(tokens.TokenType.EXCLAMATION)

        if self.current_token().type == tokens.TokenType.TYPE:
            return_type = self.advance().value
        else:
            raise ParserError(
                "Invalid return type",
                self.current_token(),
                self.position
            )

        body = self.handle_block()

        return ast.Function(name, args, return_type, body)

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

        if self.current_token().type == tokens.TokenType.ASSIGN:
            self.advance()
            value = self.handle_expression()
        else:
            value = ast.Literal(None)

        self.expect(tokens.TokenType.PERIOD)
        mutable = self.DATATYPES_MUTABILITY.get(datatype)
        if mutable is None:
            raise ParserError("Invalid datatype", self.current_token(), self.position)
        datatype = ast.Type(datatype, mutable)
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
        elif token.type == tokens.TokenType.OPEN_PAREN:
            self.advance()
            expr = self.handle_expression()
            self.expect(tokens.TokenType.CLOSE_PAREN)
            return expr
        else:
            raise ParserError("Invalid expression", token, self.position)

        return side

    def handle_expression(self, min_precedence=0):
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

        while True:
            token = self.current_token()
            precedence = self.get_precedence(token)

            if precedence < min_precedence:
                break

            operator = token.value
            self.advance()

            right_side = self.handle_expression(precedence + 1)

            left_side = ast.BinaryExpression (
                left_side,
                operator,
                right_side
            )

        return left_side
    
    def expect_directive(self):
        token = self.current_token()
        if token.type == tokens.TokenType.DIRECTIVE and token.value in [
            "$MEM-MANUAL",
            "$MEM-GC",
        ]:
            self.memory_mode = token.value
            self.advance()
        else:
            raise ParserError(
                "No directive found. Specify $MEM-GC for garbage collection or $MEM-MANUAL for manual memory freeing.",
                token,
                self.position,
            )

    def handle_statement(self):
        token = self.current_token()
        handler = self.STMT_HANDLERS.get(token.type)
        if handler is None:
            raise ParserError("Invalid statement", token, self.position)
        self.advance()

        return handler(self)

    STMT_HANDLERS = {
        tokens.TokenType.VAL: handle_variable,
        tokens.TokenType.FUNCTION: handle_function
    }

    def parse(self):
        self.expect_directive()
        while not self.at_end() and self.current_token().type != tokens.TokenType.EOF:
            self.ast_tree.append(self.handle_statement())

        program = ast.Program(self.ast_tree, self.memory_mode)
        return program


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


def run(tokens_from_lexer, trace_arg):
    trace = trace_arg
    parser = Parser(tokens_from_lexer)
    ast_tree = parser.parse()

    if trace:
        print("\nAST Tree:\n")
        print_ast(ast_tree)
