from sys import exit as leave
from dataclasses import is_dataclass
from teapot.debug import print
from teapot.semantic import analyse

if __name__ == "__main__":
    leave(
        "Cannot run this file directly! Run `python main.py -h` for info on how to start the compiler"
    )


import teapot.teapot_ast as ast
from teapot import tokens

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
        # The first datatype letter is reflected here as an explicit semantic flag.
        self.DATATYPES_MUTABILITY = {
            "mstr": True,
            "mbln": True,
            "mchar": True,
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
            "cchar": False,
        }

    def current_token(self):
        # Return a synthetic EOF token if callers move beyond the token list.
        if self.at_end():
            return tokens.Token(tokens.TokenType.EOF)
        else:
            return self.tokens[self.position]

    def at_end(self):
        return self.position >= len(self.tokens)

    def advance(self):
        token = self.current_token()
        if not self.at_end():
            self.position += 1
        return token

    def handle_struct(self, public=False):
        # Struct fields are currently restricted to primitive datatype tokens.
        name = self.expect(tokens.TokenType.IDENTIFIER).value
        self.expect(tokens.TokenType.OPEN_BRACE)
        body = []
        while (
            not self.at_end()
            and self.current_token().type != tokens.TokenType.CLOSE_BRACE
        ):
            member_type = self.expect(tokens.TokenType.TYPE).value
            mutable = self.DATATYPES_MUTABILITY.get(member_type)
            if mutable is None:
                raise ParserError(
                    "Invalid datatype", self.current_token(), self.position
                )
            member_id = self.expect(tokens.TokenType.IDENTIFIER).value
            self.expect(tokens.TokenType.PERIOD)
            body.append(ast.StructField(member_id, ast.Type(member_type, mutable)))
        self.expect(tokens.TokenType.CLOSE_BRACE)
        return ast.Struct(name, body, public)

    def handle_enum(self, public=False):
        name = self.expect(tokens.TokenType.IDENTIFIER).value
        self.expect(tokens.TokenType.OPEN_BRACE)
        body = []
        while (
            not self.at_end()
            and self.current_token().type != tokens.TokenType.CLOSE_BRACE
        ):
            member_name = self.expect(tokens.TokenType.IDENTIFIER).value
            self.expect(tokens.TokenType.PERIOD)
            body.append(ast.EnumMember(member_name))
        self.expect(tokens.TokenType.CLOSE_BRACE)
        return ast.Enum(name, body, public)

    def handle_err(self, public=False):
        name = self.expect(tokens.TokenType.IDENTIFIER).value
        self.expect(tokens.TokenType.OPEN_BRACE)
        body = []
        while (
            not self.at_end()
            and self.current_token().type != tokens.TokenType.CLOSE_BRACE
        ):
            member_datatype = self.expect(tokens.TokenType.TYPE).value
            mutable = self.DATATYPES_MUTABILITY.get(member_datatype)
            if mutable is None:
                raise ParserError(
                    "Invalid datatype", self.current_token(), self.position
                )
            member_name = self.expect(tokens.TokenType.IDENTIFIER).value
            self.expect(tokens.TokenType.PERIOD)
            body.append(ast.ErrorMember(member_name, member_datatype, mutable))
        self.expect(tokens.TokenType.CLOSE_BRACE)
        return ast.Error(name, body, public)

    def handle_operator(self, public=False):
        # Operators may use a symbol token or an identifier as their name.
        operator_tokens = [
            tokens.TokenType.PLUS,
            tokens.TokenType.MINUS,
            tokens.TokenType.MODULO,
            tokens.TokenType.MULTIPLY,
            tokens.TokenType.DIVIDE,
        ]

        if self.current_token().type in operator_tokens:
            name = self.advance().value

        elif self.current_token().type == tokens.TokenType.IDENTIFIER:
            name = self.advance().value

        else:
            raise ParserError(
                "Invalid operator name", self.current_token(), self.position
            )
        args = self.handle_operator_arguments()
        self.expect(tokens.TokenType.EXCLAMATION)
        if self.current_token().type == tokens.TokenType.IDENTIFIER:
            return_type = self.expect(tokens.TokenType.IDENTIFIER)
        elif self.current_token().type == tokens.TokenType.TYPE:
            return_type = self.expect(tokens.TokenType.TYPE)
        body = self.handle_operator_block()
        return ast.Operator(name, args, body, return_type, public)

    def handle_exit(self):
        value = self.handle_expression()
        self.expect(tokens.TokenType.PERIOD)
        return ast.Return(value)

    def handle_operator_block(self):
        self.expect(tokens.TokenType.OPEN_BRACE)
        body = []
        while (
            not self.at_end()
            and self.current_token().type != tokens.TokenType.CLOSE_BRACE
        ):
            body.append(self.handle_statement())
        self.expect(tokens.TokenType.CLOSE_BRACE)
        return body

    def handle_operator_arguments(self):
        args = []
        self.expect(tokens.TokenType.OPEN_PAREN)
        if self.current_token().type != tokens.TokenType.CLOSE_PAREN:
            if self.current_token().type in [
                tokens.TokenType.TYPE,
                tokens.TokenType.IDENTIFIER,
            ]:
                datatype = self.expect(self.current_token().type)
            else:
                raise ParserError("Invalid type", self.current_token(), self.position)

        identifier = self.expect(tokens.TokenType.IDENTIFIER)

        args.append(ast.OperatorArgument(identifier, datatype))

        while (
            not self.at_end()
            and self.current_token().type != tokens.TokenType.CLOSE_PAREN
        ):
            self.expect(tokens.TokenType.COMMA)
            if self.current_token().type in [
                tokens.TokenType.TYPE,
                tokens.TokenType.IDENTIFIER,
            ]:
                datatype = self.expect(self.current_token().type)
            else:
                raise ParserError("Invalid type", self.current_token(), self.position)
            identifier = self.expect(tokens.TokenType.IDENTIFIER)
            args.append(ast.OperatorArgument(identifier, datatype))
        self.expect(tokens.TokenType.CLOSE_PAREN)
        return args

    def handle_block(self):
        # Blocks recursively parse statements until their closing brace.
        self.expect(tokens.TokenType.OPEN_BRACE)
        block = []
        while (
            not self.at_end()
            and self.current_token().type != tokens.TokenType.CLOSE_BRACE
        ):
            block.append(self.handle_statement())
        self.expect(tokens.TokenType.CLOSE_BRACE)
        return block

    def get_precedence(self, token):
        # Higher values bind more tightly in the precedence-climbing parser.
        PRECEDENCES = {
            tokens.TokenType.OR: 0,
            tokens.TokenType.AND: 1,
            tokens.TokenType.EQUALS: 2,
            tokens.TokenType.NOT_EQUAL: 2,
            tokens.TokenType.LESS: 3,
            tokens.TokenType.LESS_EQUAL: 3,
            tokens.TokenType.GREATER: 3,
            tokens.TokenType.GREATER_EQUAL: 3,
            tokens.TokenType.PLUS: 4,
            tokens.TokenType.MINUS: 4,
            tokens.TokenType.MODULO: 5,
            tokens.TokenType.DIVIDE: 5,
            tokens.TokenType.MULTIPLY: 5,
            tokens.TokenType.POWER: 6,
        }

        return PRECEDENCES.get(token.type, -1)

    def handle_function_argument(self):
        args = []
        default = None
        datatype = self.expect(tokens.TokenType.TYPE).value
        if self.current_token().type == tokens.TokenType.OPEN_BRACKET:
            datatype = self.handle_array_type(datatype)
        identifier = self.expect(tokens.TokenType.IDENTIFIER).value
        default = self.handle_default_argument()
        args.append(ast.FunctionArgument(identifier, datatype, default))

        while self.current_token().type == tokens.TokenType.COMMA:
            default = None
            self.advance()
            datatype = self.expect(tokens.TokenType.TYPE).value
            if self.current_token().type == tokens.TokenType.OPEN_BRACKET:
                datatype = self.handle_array_type(datatype)
            identifier = self.expect(tokens.TokenType.IDENTIFIER).value
            default = self.handle_default_argument()

            args.append(ast.FunctionArgument(identifier, datatype, default))

        return args

    def handle_array_type(self, datatype):
        self.expect(tokens.TokenType.OPEN_BRACKET)
        self.expect(tokens.TokenType.CLOSE_BRACKET)
        return ast.ArrayType(datatype)

    def handle_default_argument(self):
        if self.current_token().type != tokens.TokenType.ASSIGN:
            return None
        self.advance()
        return self.handle_expression()

    def handle_if(self):
        elifs = []
        tp_else = None
        self.expect(tokens.TokenType.OPEN_PAREN)
        condition = self.handle_expression()
        self.expect(tokens.TokenType.CLOSE_PAREN)
        body = self.handle_block()
        if self.current_token().type == tokens.TokenType.ELSEIF:
            elifs = self.handle_elif()
        if self.current_token().type == tokens.TokenType.ELSE:
            tp_else = self.handle_else()
        return ast.If(condition, body, elifs, tp_else)

    def handle_elif(self):
        elifs = []
        while self.current_token().type == tokens.TokenType.ELSEIF:
            self.expect(tokens.TokenType.ELSEIF)
            self.expect(tokens.TokenType.OPEN_PAREN)
            condition = self.handle_expression()
            self.expect(tokens.TokenType.CLOSE_PAREN)
            body = self.handle_block()
            elifs.append(ast.Elif(condition, body))
        return elifs

    def handle_else(self):
        self.advance()
        body = self.handle_block()
        return ast.Else(body)

    def handle_reassignement(self):
        target = self.handle_expression()
        operator = self.current_token()
        if operator.type not in [
            tokens.TokenType.ASSIGN,
            tokens.TokenType.ASSIGN_DIVIDE,
            tokens.TokenType.ASSIGN_MINUS,
            tokens.TokenType.ASSIGN_MULTIPLY,
            tokens.TokenType.ASSIGN_PLUS,
        ]:
            raise ParserError(
                "Expected assignment operator", self.current_token(), self.position
            )
        self.advance()
        value = self.handle_expression()
        self.expect(tokens.TokenType.PERIOD)
        return ast.Assignment(target, operator, value)

    def handle_while(self):
        self.expect(tokens.TokenType.OPEN_PAREN)
        expression = self.handle_expression()
        self.expect(tokens.TokenType.CLOSE_PAREN)
        body = self.handle_block()
        return ast.While(expression, body)

    def handle_for(self):
        self.expect(tokens.TokenType.OPEN_PAREN)
        variable = self.expect(tokens.TokenType.IDENTIFIER).value
        self.expect(tokens.TokenType.COLON)
        iterable = self.handle_expression()
        self.expect(tokens.TokenType.CLOSE_PAREN)
        body = self.handle_block()
        return ast.For(variable, iterable, body)

    def handle_function(self, public):
        args = []
        name = self.expect(tokens.TokenType.IDENTIFIER).value
        self.expect(tokens.TokenType.OPEN_PAREN)
        if self.current_token().type != tokens.TokenType.CLOSE_PAREN:
            args = self.handle_function_argument()
        self.expect(tokens.TokenType.CLOSE_PAREN)
        self.expect(tokens.TokenType.EXCLAMATION)

        if self.current_token().type in [
            tokens.TokenType.TYPE,
            tokens.TokenType.IDENTIFIER,
        ]:
            return_type = self.advance().value
        else:
            raise ParserError(
                "Invalid return type", self.current_token(), self.position
            )

        body = self.handle_block()

        return ast.Function(name, args, return_type, body, public)

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
        # A pair of identifiers at the start denotes a user-defined struct value.
        identifier = False
        reference = False
        if self.current_token().type == tokens.TokenType.REFERENCE:
            reference = True
            self.expect(tokens.TokenType.REFERENCE)
        if self.current_token().type == tokens.TokenType.TYPE:
            datatype = self.expect(tokens.TokenType.TYPE).value
        elif self.current_token().type == tokens.TokenType.IDENTIFIER:
            datatype = self.expect(tokens.TokenType.IDENTIFIER).value
            identifier = True
        else:
            raise ParserError("Invalid datatype", self.current_token(), self.position)

        if self.current_token().type == tokens.TokenType.OPEN_BRACKET:
            datatype = self.handle_array_type(datatype)
        
        identifier = self.expect(tokens.TokenType.IDENTIFIER).value

        if self.current_token().type == tokens.TokenType.ASSIGN:
            self.advance()
            value = self.handle_expression()
        else:
            value = ast.Literal(None)

        self.expect(tokens.TokenType.PERIOD)
        if isinstance(datatype, ast.ArrayType):
            mutable = self.DATATYPES_MUTABILITY.get(datatype.datatype)
        else:
            mutable = self.DATATYPES_MUTABILITY.get(datatype)
        # Unknown primitive names are errors, but user-defined types are valid here.
        if mutable is None and not identifier:
            raise ParserError("Invalid datatype", self.current_token(), self.position)
        datatype = ast.Type(datatype, mutable, reference)
        return ast.DeclareVariable(identifier, datatype, value)

    def handle_postfix(self, callee):
        args = []
        self.expect(tokens.TokenType.OPEN_PAREN)
        if self.current_token().type != tokens.TokenType.CLOSE_PAREN:
            args.append(self.handle_expression())
            while (
                not self.at_end()
                and self.current_token().type != tokens.TokenType.CLOSE_PAREN
            ):
                self.expect(tokens.TokenType.COMMA)
                args.append(self.handle_expression())
        self.expect(tokens.TokenType.CLOSE_PAREN)
        return ast.CallExpression(callee, args)

    def handle_array_literal(self):
        elements = []

        self.expect(tokens.TokenType.OPEN_BRACKET)
        if (
            self.current_token().type != tokens.TokenType.CLOSE_BRACKET
            and not self.at_end()
        ):
            elements.append(self.handle_expression())
            while self.current_token().type == tokens.TokenType.COMMA:
                self.advance()
                elements.append(self.handle_expression())
        self.expect(tokens.TokenType.CLOSE_BRACKET)
        return ast.ArrayLiteral(elements)

    def handle_primary(self):
        negative = False
        token = self.current_token()

        if token.type == tokens.TokenType.MINUS:
            negative = True
            self.advance()
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
                if negative:
                    side = ast.Literal(token.value - token.value * 2)
                else:
                    side = ast.Literal(token.value)
        elif token.type == tokens.TokenType.OPEN_PAREN:
            self.advance()
            expr = self.handle_expression()
            self.expect(tokens.TokenType.CLOSE_PAREN)
            return expr
        elif token.type == tokens.TokenType.OPEN_BRACKET:
            return self.handle_array_literal()
        else:
            raise ParserError("Invalid expression", token, self.position)

        return side

    def handle_expression(self, min_precedence=0):
        # Parse primary values, postfix operators, unary NOT, then binary operators.
        operator = None
        token = self.current_token()
        unary = False

        if token.type == tokens.TokenType.NOT:
            unary = True
            operator = token.value
            self.advance()
            token = self.current_token()

        left_side = self.handle_primary()

        while True:
            if self.current_token().type == tokens.TokenType.OPEN_PAREN:
                left_side = self.handle_postfix(left_side)
            elif self.current_token().type == tokens.TokenType.CAST:
                self.advance()
                datatype = self.expect(tokens.TokenType.TYPE).value
                left_side = ast.Cast(left_side, datatype)
            elif self.current_token().type == tokens.TokenType.DOUBLE_COLON:
                while self.current_token().type == tokens.TokenType.DOUBLE_COLON:
                    self.advance()
                    member = self.expect(tokens.TokenType.IDENTIFIER).value
                    left_side = ast.MemberAccess(left_side, member)
            else:
                break

        if unary:
            left_side = ast.UnaryExpression(operator, left_side)

        while True:
            token = self.current_token()
            precedence = self.get_precedence(token)

            if precedence < min_precedence:
                break

            operator = token.value
            self.advance()

            right_side = self.handle_expression(precedence + 1)

            left_side = ast.BinaryExpression(left_side, operator, right_side)

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
        # Identifiers need a short speculative parse to distinguish assignment.
        start = self.position
        public = False

        if self.current_token().type == tokens.TokenType.PUBLIC:
            public = True
            self.advance()

        token = self.current_token()

        if self.current_token().type == tokens.TokenType.IDENTIFIER:
            expr = self.handle_expression()

            if self.current_token().type in [
                tokens.TokenType.ASSIGN,
                tokens.TokenType.ASSIGN_DIVIDE,
                tokens.TokenType.ASSIGN_MINUS,
                tokens.TokenType.ASSIGN_PLUS,
                tokens.TokenType.ASSIGN_MULTIPLY,
            ]:
                operator = self.advance()
                value = self.handle_expression()
                self.expect(tokens.TokenType.PERIOD)
                return ast.Assignment(expr, operator, value)
            # It was not an assignment, so let the normal statement dispatcher retry.
            self.position = start

        handler = self.STMT_HANDLERS.get(token.type)

        if handler is None:
            raise ParserError("Invalid statement", token, self.position)

        if public and token.type not in [
            tokens.TokenType.FUNCTION,
            tokens.TokenType.STRUCT,
            tokens.TokenType.ENUM,
            tokens.TokenType.ERROR,
            tokens.TokenType.OPERATOR,
        ]:
            raise ParserError(
                "Only functions, structs, enums, operators, and errors can be public.",
                token,
                self.position,
            )

        if handler is None:
            raise ParserError("Invalid statement", token, self.position)
        self.advance()

        if token.type in [
            tokens.TokenType.FUNCTION,
            tokens.TokenType.STRUCT,
            tokens.TokenType.ENUM,
            tokens.TokenType.ERROR,
            tokens.TokenType.OPERATOR,
        ]:
            return handler(self, public)
        else:
            return handler(self)

    STMT_HANDLERS = {
        tokens.TokenType.VAL: handle_variable,
        tokens.TokenType.FUNCTION: handle_function,
        tokens.TokenType.STRUCT: handle_struct,
        tokens.TokenType.ENUM: handle_enum,
        tokens.TokenType.ERROR: handle_err,
        tokens.TokenType.OPERATOR: handle_operator,
        tokens.TokenType.EXIT: handle_exit,
        tokens.TokenType.IF: handle_if,
        tokens.TokenType.FOR: handle_for,
        tokens.TokenType.WHILE: handle_while,
    }

    def parse(self):
        # The memory directive is mandatory and must precede every top-level node.
        self.expect_directive()
        while not self.at_end() and self.current_token().type != tokens.TokenType.EOF:
            self.ast_tree.append(self.handle_statement())

        program = ast.Program(self.ast_tree, self.memory_mode)
        return program



def print_ast(node, indent=0, visited=None):
    if visited is None:
        visited = set()

    spacing = " " * indent

    # Primitive values
    if isinstance(node, (str, int, float, bool, type(None))):
        print(f"{spacing}{repr(node)}")
        return

    # Recursion protection
    obj_id = id(node)
    if obj_id in visited:
        print(f"{spacing}<recursive reference>")
        return

    visited.add(obj_id)

    # Dataclass nodes
    if is_dataclass(node):
        print(f"{spacing}{type(node).__name__}")

        for field_name in node.__dataclass_fields__:
            value = getattr(node, field_name)

            print(f"{spacing}  {field_name}:")
            print_ast(value, indent + 4, visited)

        return

    # Lists / tuples / sets
    if isinstance(node, (list, tuple, set)):
        print(f"{spacing}[")
        for item in node:
            print_ast(item, indent + 4, visited)
        print(f"{spacing}]")
        return

    # Dictionaries
    if isinstance(node, dict):
        print(f"{spacing}{{")
        for key, value in node.items():
            print(f"{spacing}  {key}:")
            print_ast(value, indent + 4, visited)
        print(f"{spacing}}}")
        return

    # Fallback
    print(f"{spacing}{repr(node)}")


def run(tokens_from_lexer, trace_arg):
    trace = trace_arg
    if trace:
        print("========= BEGIN ABSTRACT SYNTAX TREE CONSTRUCTION =========")
    parser = Parser(tokens_from_lexer)
    ast_tree = parser.parse()

    if trace:
        print("\nAST Tree:\n")
        print_ast(ast_tree)

    if trace:
        print("========= END ABSTRACT SYNTAX TREE CONSTRUCTION =========")

    return analyse(ast_tree, trace_arg)