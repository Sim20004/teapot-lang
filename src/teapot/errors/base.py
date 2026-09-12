from teapot.errors.location import SourceLocation
from teapot.output import get_output


class TeapotCompilerError(Exception):
    phase = "compiler"
    code = "compiler-error"
    default_hint = "Check the source near this location."

    def __init__(self, message, *, location=None, **details):
        self.message = message
        self.location = location or SourceLocation()
        self.hint = details.pop("hint", self.default_hint)
        self.details = details
        super().__init__(self._format())
        get_output().diagnostic(self)

    def _format(self):
        return (
            f"{self.phase.capitalize()} error at {self.location}: {self.message}\n"
            f"  Hint: {self.hint}"
        )


class LexicalError(TeapotCompilerError):
    phase = "lexical"
    code = "lexical-error"


class LexerError(LexicalError):
    """Compatibility base for the original public lexer exception."""

    phase = "lexer"

    def __init__(self, message, line=None, col=None, *, location=None, **details):
        self.line = line if line is not None else getattr(location, "line", None)
        self.col = col if col is not None else getattr(location, "column", None)
        super().__init__(
            message,
            location=location or SourceLocation(line, col),
            **details,
        )


class ParseError(TeapotCompilerError):
    phase = "parser"
    code = "parser-error"


class ParserError(ParseError):
    """Compatibility base for the original public parser exception."""

    def __init__(self, message, token=None, position=None, *, location=None, **details):
        self.token = token
        self.position = position
        super().__init__(
            message,
            location=location
            or SourceLocation(
                getattr(token, "line", None),
                getattr(token, "col", None),
                position,
            ),
            **details,
        )


class SemanticError(TeapotCompilerError):
    phase = "semantic analysis"
    code = "semantic-error"

    def __init__(self, message, node=None, *, location=None, **details):
        self.node = node
        super().__init__(
            message,
            location=location or getattr(node, "location", None),
            node=node,
            **details,
        )


class UnexpectedTokenError(ParserError):
    code = "unexpected-token"
    default_hint = "Use the expected token here or remove the unexpected token."

    def __init__(self, expected, actual, *, location=None, position=None):
        self.expected = expected
        self.actual = actual
        actual_name = getattr(actual, "value", None)
        actual_type = getattr(getattr(actual, "type", None), "name", actual)
        shown_actual = repr(actual_name) if actual_name is not None else actual_type
        super().__init__(
            f"expected {getattr(expected, 'name', expected)}, found {shown_actual}",
            location=location,
            expected=expected,
            actual=actual,
            position=position,
        )


class UnexpectedEOFError(ParserError):
    code = "unexpected-eof"
    default_hint = "Add the missing closing token or complete the statement."

    def __init__(self, expected, *, location=None, position=None):
        self.expected = expected
        super().__init__(
            f"expected {getattr(expected, 'name', expected)} before end of input",
            location=location,
            expected=expected,
            position=position,
        )


class InvalidExpressionError(ParserError):
    code = "invalid-expression"
    default_hint = (
        "Start the expression with a literal, identifier, or parenthesised expression."
    )


class InvalidTypeError(ParserError):
    code = "invalid-type"
    default_hint = (
        "Use a built-in Teapot type or a type declared earlier in the source."
    )


class InvalidStatementError(ParserError):
    code = "invalid-statement"
    default_hint = "Use a valid Teapot statement at this location."


class InvalidAssignmentError(ParserError):
    code = "invalid-assignment"
    default_hint = (
        "Assign to a declared, writable variable with a valid assignment operator."
    )


class InvalidVisibilityError(ParserError):
    code = "invalid-visibility"
    default_hint = (
        "Only functions, structs, enums, operators, and errors may be public."
    )


class InvalidMapKeyError(ParserError):
    code = "invalid-map-key"
    default_hint = "Use a literal value for the map key."


class InvalidDirectiveError(LexerError):
    code = "invalid-directive"
    default_hint = "Use `$MEM-GC` or `$MEM-MANUAL` as the memory directive."


class DuplicateDirectiveError(LexerError):
    code = "duplicate-directive"
    default_hint = "Keep exactly one memory directive at the beginning of the source."


class InvalidSymbolError(LexerError):
    code = "invalid-symbol"
    default_hint = (
        "Replace this character with a supported Teapot operator or delimiter."
    )


class UnterminatedStringError(LexerError):
    code = "unterminated-string"
    default_hint = "Add a closing double quote to the string literal."


class InvalidNumberError(LexerError):
    code = "invalid-number"
    default_hint = "Write a number with at most one decimal point."


class DuplicateDeclarationError(SemanticError):
    code = "duplicate-declaration"
    default_hint = (
        "Rename the declaration or remove the earlier declaration in this scope."
    )

    def __init__(self, name, kind, *, location=None, node=None):
        self.name = name
        self.kind = kind
        super().__init__(
            f"{kind} `{name}` is already declared in this scope",
            location=location,
            name=name,
            kind=kind,
            node=node,
        )


class UndefinedVariableError(SemanticError):
    code = "undefined-variable"
    default_hint = "Declare the variable before assigning to or using it."


class InvalidControlFlowError(SemanticError):
    code = "invalid-control-flow"
    default_hint = (
        "Move this control-flow statement into a compatible enclosing construct."
    )


class UnknownNodeError(SemanticError):
    code = "unknown-node"
    default_hint = (
        "Use a supported language construct or update the compiler phase handling it."
    )


class TypeMismatchError(SemanticError):
    code = "type-mismatch"
    default_hint = "Change the value or declared type so the two types agree."


# Keep legacy traceback names stable while callers can still catch precise types.
for _error_type in LexerError.__subclasses__():
    _error_type.__name__ = "LexerError"
    _error_type.__qualname__ = "LexerError"
for _error_type in ParserError.__subclasses__():
    _error_type.__name__ = "ParserError"
    _error_type.__qualname__ = "ParserError"
for _error_type in SemanticError.__subclasses__():
    _error_type.__name__ = "SemanticError"
    _error_type.__qualname__ = "SemanticError"
