from sys import exit as leave

if __name__ == "__main__":
    leave("Cannot run this file directly! Run `python main.py -h` for info on how to start the compiler")

class ASTError(Exception):
    pass

class ASTNode:
    pass

class Import(ASTNode):
    def __init__(self, module, alias=None, imported_object="*"):
        self.module = module
        self.alias = alias
        self.imported_object = imported_object

class Function(ASTNode):
    def __init__(self, name, arguments, return_type, body):
        self.name = name
        self.arguments = arguments
        self.return_type = return_type
        self.body = body

class FunctionArgument(ASTNode):
    def __init__(self, identifier, datatype, default=None):
        self.identifier = identifier
        self.datatype = datatype
        self.default = default

class Return(ASTNode):
    def __init__(self, value=None):
        self.value = value

class Operator(ASTNode):
    def __init__(self, symbol, arguments, body):
        self.symbol = symbol
        self.arguments = arguments
        self.body = body

class Cast(ASTNode):
    def __init__(self, expression, datatype):
        self.expression = expression
        self.datatype = datatype

class DeclareVariable(ASTNode):
    def __init__(self, identifier, datatype, value=None):
        self.identifier = identifier
        self.datatype = datatype
        self.value = value

class FreeMemory(ASTNode):
    def __init__(self, expression):
        self.expression = expression

class Identifier(ASTNode):
    def __init__(self, name):
        self.name = name

class If(ASTNode):
    def __init__(self, condition, body, elifs=None, else_body=None):
        self.condition = condition
        self.body = body
        self.elifs = elifs or []
        self.else_body = else_body

class Elif(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class Else(ASTNode):
    def __init__(self, body):
        self.body = body

class Block(ASTNode):
    def __init__(self, statements):
        self.statements = statements

class While(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class For(ASTNode):
    def __init__(self, variable, iterable, body):
        self.variable = variable
        self.iterable = iterable
        self.body = body

class Assignment(ASTNode):
    def __init__(self, target, operator, value):
        self.target = target
        self.operator = operator
        self.value = value

class Break(ASTNode):
    pass

class Continue(ASTNode):
    pass

class Do(ASTNode):
    def __init__(self, body, fail):
        self.body = body
        self.fail = fail

class Fail(ASTNode):
    def __init__(self, body, error, identifier):
        self.body = body
        self.error = error
        self.identifier = identifier

class Struct(ASTNode):
    def __init__(self, identifier, body):
        self.body = body
        self.identifier = identifier

class Enum(ASTNode):
    def __init__(self, identifier, body):
        self.body = body
        self.identifier = identifier

class ListLiteral(ASTNode):
    def __init__(self, values):
        self.values = values

class MapLiteral(ASTNode):
    def __init__(self, entries):
        self.entries = entries

class Literal(ASTNode):
    def __init__(self, value):
        self.value = value

class BinaryExpression(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

class UnaryExpression(ASTNode):
    def __init__(self, operator, value):
        self.operator = operator
        self.value = value

class FunctionCall(ASTNode):
    def __init__(self, function, arguments):
        self.function = function
        self.arguments = arguments

class Type(ASTNode):
    def __init__(self, name, mutable=False, reference=False, subtype=None):
        self.name = name
        self.mutable = mutable
        self.reference = reference
        self.subtype = subtype

class StructField(ASTNode):
    def __init__(self, identifier, datatype):
        self.identifier = identifier
        self.datatype = datatype

class EnumMember(ASTNode):
    def __init__(self, name):
        self.name = name

class MemberAccess(ASTNode):
    def __init__(self, instance, member):
        self.instance = instance
        self.member = member

class ArrayLiteral(ASTNode):
    def __init__(self, values):
        self.values = values

class Reference(ASTNode):
    def __init__(self, expression):
        self.expression = expression

class Error(ASTNode):
    def __init__(self, identifier, body):
        self.identifier = identifier
        self.body = body

class Directive(ASTNode):
    def __init__(self, name):
        self.name = name

class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements