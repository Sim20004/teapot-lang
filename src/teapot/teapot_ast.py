from dataclasses import dataclass, field
from sys import exit as leave

if __name__ == "__main__":
    leave(
        "Cannot run this file directly! Run `python main.py -h` for info on how to start the compiler"
    )


# Base exception used when an AST operation cannot represent the source program.
@dataclass
class ASTError(Exception):
    pass


# All syntax nodes share this marker so consumers can type-check AST values.
@dataclass
class ASTNode:
    pass


# Declarations and executable statements.
@dataclass
class Import(ASTNode):
    module: str
    alias: str | None = None
    imported_object: str = "*"


@dataclass
class Function(ASTNode):
    name: str
    arguments: list
    return_type: object
    body: list
    public: bool = False


@dataclass
class StructInstantiation(ASTNode):
    struct_name: object
    arguments: list
    identifier: object


@dataclass
class FunctionArgument(ASTNode):
    identifier: str
    datatype: object
    default: object = None


@dataclass
class Return(ASTNode):
    value: object = None
    datatype: object = None


@dataclass
class CallExpression(ASTNode):
    callee: object
    arguments: list


@dataclass
class MemberAccess(ASTNode):
    obj: object
    member: str


@dataclass
class OperatorArgument(ASTNode):
    name: object
    datatype: object


@dataclass
class Operator(ASTNode):
    symbol: str
    arguments: list
    body: list
    return_type: object
    public: bool = False


@dataclass
class ErrorMember(ASTNode):
    name: str
    datatype: object
    mutable: bool = False


@dataclass
class Cast(ASTNode):
    expression: object
    datatype: object


@dataclass
class DeclareVariable(ASTNode):
    identifier: str
    datatype: object
    value: object = None


@dataclass
class FreeMemory(ASTNode):
    expression: object


@dataclass
class Identifier(ASTNode):
    name: str


@dataclass
class If(ASTNode):
    condition: object
    body: list
    elifs: list = field(default_factory=list)
    else_body: object = None


@dataclass
class Elif(ASTNode):
    condition: object
    body: list


@dataclass
class Else(ASTNode):
    body: list


@dataclass
class Block(ASTNode):
    statements: list


@dataclass
class While(ASTNode):
    condition: object
    body: list


@dataclass
class For(ASTNode):
    variable: str
    iterable: object
    body: list


@dataclass
class Assignment(ASTNode):
    target: object
    operator: object
    value: object


@dataclass
class Break(ASTNode):
    pass


@dataclass
class Continue(ASTNode):
    pass


# Structured error-handling and user-defined type declarations.
@dataclass
class Do(ASTNode):
    body: list
    fail: object


@dataclass
class Fail(ASTNode):
    body: list
    error: object
    identifier: str


@dataclass
class Struct(ASTNode):
    identifier: str
    body: list
    public: bool = False


@dataclass
class Enum(ASTNode):
    identifier: str
    body: list
    public: bool = False


# Literal and operator expression nodes.
@dataclass
class ListLiteral(ASTNode):
    values: list


@dataclass
class MapLiteral(ASTNode):
    entries: dict


@dataclass
class Literal(ASTNode):
    value: object


@dataclass
class BinaryExpression(ASTNode):
    left: object
    operator: object
    right: object


@dataclass
class UnaryExpression(ASTNode):
    operator: object
    value: object


@dataclass
class FunctionCall(ASTNode):
    function: object
    arguments: list


# Type metadata is kept in the AST so later phases can enforce mutability and references.
@dataclass
class Type(ASTNode):
    name: str
    mutable: bool = False
    reference: bool = False
    subtype: object = None


# Remaining type, reference, directive, and program nodes.
@dataclass
class StructField(ASTNode):
    identifier: str
    datatype: object


@dataclass
class ArrayType(ASTNode):
    datatype: object


@dataclass
class EnumMember(ASTNode):
    name: str


@dataclass
class ArrayLiteral(ASTNode):
    values: list


@dataclass
class Reference(ASTNode):
    expression: object


@dataclass
class Error(ASTNode):
    identifier: str
    body: list
    public: bool = False


@dataclass
class Directive(ASTNode):
    name: str


@dataclass
class Program(ASTNode):
    statements: list
    memory_mode: str