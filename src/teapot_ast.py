from dataclasses import dataclass
from sys import exit as leave

if __name__ == "__main__":
    leave(
        "Cannot run this file directly! Run `python main.py -h` for info on how to start the compiler"
    )

@dataclass
class ASTError(Exception):
    pass


@dataclass
class ASTNode:
    pass


@dataclass
class Import(ASTNode):
    def __init__(self, module, alias=None, imported_object="*"):
        self.module = module
        self.alias = alias
        self.imported_object = imported_object


@dataclass
class Function(ASTNode):
    def __init__(self, name, arguments, return_type, body, public=False):
        self.name = name
        self.arguments = arguments
        self.return_type = return_type
        self.body = body
        self.public = public


@dataclass
class FunctionArgument(ASTNode):
    def __init__(self, identifier, datatype, default=None):
        self.identifier = identifier
        self.datatype = datatype
        self.default = default


@dataclass
class Return(ASTNode):
    def __init__(self, value=None):
        self.value = value

class OperatorArgument(ASTNode):
    def __init__(self, name, datatype):
        self.name = name
        self.datatype = datatype

@dataclass
class Operator(ASTNode):
    def __init__(self, symbol, arguments, body, public=False):
        self.symbol = symbol
        self.arguments = arguments
        self.body = body
        self.public = public

class ErrorMember(ASTNode):
    def __init__(self, name, datatype, mutable=False):
        self.name = name
        self.datatype = datatype
        self.mutable = mutable
@dataclass
class Cast(ASTNode):
    def __init__(self, expression, datatype):
        self.expression = expression
        self.datatype = datatype


@dataclass
class DeclareVariable(ASTNode):
    def __init__(self, identifier, datatype, value=None):
        self.identifier = identifier
        self.datatype = datatype
        self.value = value


@dataclass
class FreeMemory(ASTNode):
    def __init__(self, expression):
        self.expression = expression


@dataclass
class Identifier(ASTNode):
    def __init__(self, name):
        self.name = name


@dataclass
class If(ASTNode):
    def __init__(self, condition, body, elifs=None, else_body=None):
        self.condition = condition
        self.body = body
        self.elifs = elifs or []
        self.else_body = else_body


@dataclass
class Elif(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body


@dataclass
class Else(ASTNode):
    def __init__(self, body):
        self.body = body


@dataclass
class Block(ASTNode):
    def __init__(self, statements):
        self.statements = statements


@dataclass
class While(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body


@dataclass
class For(ASTNode):
    def __init__(self, variable, iterable, body):
        self.variable = variable
        self.iterable = iterable
        self.body = body


@dataclass
class Assignment(ASTNode):
    def __init__(self, target, operator, value):
        self.target = target
        self.operator = operator
        self.value = value


@dataclass
class Break(ASTNode):
    pass


@dataclass
class Continue(ASTNode):
    pass


@dataclass
class Do(ASTNode):
    def __init__(self, body, fail):
        self.body = body
        self.fail = fail


@dataclass
class Fail(ASTNode):
    def __init__(self, body, error, identifier):
        self.body = body
        self.error = error
        self.identifier = identifier


@dataclass
class Struct(ASTNode):
    def __init__(self, identifier, body, public=False):
        self.body = body
        self.identifier = identifier
        self.public = public

@dataclass
class Enum(ASTNode):
    def __init__(self, identifier, body, public=False):
        self.body = body
        self.identifier = identifier
        self.public = public


@dataclass
class ListLiteral(ASTNode):
    def __init__(self, values):
        self.values = values


@dataclass
class MapLiteral(ASTNode):
    def __init__(self, entries):
        self.entries = entries


@dataclass
class Literal(ASTNode):
    def __init__(self, value):
        self.value = value


@dataclass
class BinaryExpression(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right


@dataclass
class UnaryExpression(ASTNode):
    def __init__(self, operator, value):
        self.operator = operator
        self.value = value


@dataclass
class FunctionCall(ASTNode):
    def __init__(self, function, arguments):
        self.function = function
        self.arguments = arguments


@dataclass
class Type(ASTNode):
    def __init__(self, name, mutable=False, reference=False, subtype=None):
        self.name = name
        self.mutable = mutable
        self.reference = reference
        self.subtype = subtype


@dataclass
class StructField(ASTNode):
    def __init__(self, identifier, datatype):
        self.identifier = identifier
        self.datatype = datatype


@dataclass
class EnumMember(ASTNode):
    def __init__(self, name):
        self.name = name


@dataclass
class MemberAccess(ASTNode):
    def __init__(self, instance, member):
        self.instance = instance
        self.member = member


@dataclass
class ArrayLiteral(ASTNode):
    def __init__(self, values):
        self.values = values


@dataclass
class Reference(ASTNode):
    def __init__(self, expression):
        self.expression = expression


@dataclass
class Error(ASTNode):
    def __init__(self, identifier, body, public=False):
        self.identifier = identifier
        self.body = body
        self.public = public


@dataclass
class Directive(ASTNode):
    def __init__(self, name):
        self.name = name


@dataclass
class Program(ASTNode):
    def __init__(self, statements, memory_mode):
        self.statements = statements
        self.memory_mode = memory_mode
