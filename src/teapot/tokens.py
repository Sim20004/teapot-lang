from dataclasses import dataclass
from enum import Enum, auto
from sys import exit as leave

if __name__ == "__main__":
    leave(
        "Cannot run this file directly! Run `teapot -h` for info on how to start the compiler"
    )


class TokenType(Enum):
    # Memory management
    DIRECTIVE = auto()
    # Modules and visibility
    IMPORT = auto()
    AS = auto()
    PUBLIC = auto()
    # Functions
    FUNCTION = auto()
    EXIT = auto()
    OPERATOR = auto()
    # Variables and memory
    VAL = auto()
    REFERENCE = auto()
    FREE = auto()
    NULL = auto()
    # Control flow
    IF = auto()
    ELSEIF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    BREAK = auto()
    CONTINUE = auto()
    # Error handling
    DO = auto()
    FAIL = auto()
    ERROR = auto()
    # Data structures
    STRUCT = auto()
    ENUM = auto()
    LIST = auto()
    MAP = auto()
    # Primitive data types
    TYPE = auto()
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    CHARACTER = auto()
    BOOLEAN = auto()
    IDENTIFIER = auto()
    # Arithmetic
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    MODULO = auto()
    POWER = auto()
    # Comparison
    EQUALS = auto()
    GREATER = auto()
    LESS = auto()
    GREATER_EQUAL = auto()
    LESS_EQUAL = auto()
    NOT_EQUAL = auto()
    # Logical
    AND = auto()
    OR = auto()
    NOT = auto()
    # Assign
    ASSIGN = auto()
    ASSIGN_PLUS = auto()
    ASSIGN_MINUS = auto()
    ASSIGN_MULTIPLY = auto()
    ASSIGN_DIVIDE = auto()
    # Punctuation
    OPEN_PAREN = auto()
    CLOSE_PAREN = auto()
    OPEN_BRACE = auto()
    CLOSE_BRACE = auto()
    OPEN_BRACKET = auto()
    CLOSE_BRACKET = auto()
    COMMA = auto()
    PERIOD = auto()
    PIPE = auto()
    COLON = auto()
    DOUBLE_COLON = auto()
    EXCLAMATION = auto()
    CAST = auto()
    # End of file
    EOF = auto()


# Lexical spellings that map directly to parser statement and expression tokens.
KEYWORDS = {
    "attach": TokenType.IMPORT,
    "as": TokenType.AS,
    "pub": TokenType.PUBLIC,
    "fc": TokenType.FUNCTION,
    "exit": TokenType.EXIT,
    "operator": TokenType.OPERATOR,
    "val": TokenType.VAL,
    "ref": TokenType.REFERENCE,
    "free": TokenType.FREE,
    "null": TokenType.NULL,
    "if": TokenType.IF,
    "elif": TokenType.ELSEIF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "for": TokenType.FOR,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "do": TokenType.DO,
    "fail": TokenType.FAIL,
    "err": TokenType.ERROR,
    "sct": TokenType.STRUCT,
    "enm": TokenType.ENUM,
    "list": TokenType.LIST,
    "map": TokenType.MAP,
}

# Longer operators are checked before their one-character prefixes by the lexer.
SYMBOLS = {
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.MULTIPLY,
    "/": TokenType.DIVIDE,
    "%": TokenType.MODULO,
    "**": TokenType.POWER,
    "==": TokenType.EQUALS,
    ">": TokenType.GREATER,
    "<": TokenType.LESS,
    ">=": TokenType.GREATER_EQUAL,
    "<=": TokenType.LESS_EQUAL,
    "~=": TokenType.NOT_EQUAL,
    "&&": TokenType.AND,
    "||": TokenType.OR,
    "~": TokenType.NOT,
    "=": TokenType.ASSIGN,
    "+=": TokenType.ASSIGN_PLUS,
    "-=": TokenType.ASSIGN_MINUS,
    "*=": TokenType.ASSIGN_MULTIPLY,
    "/=": TokenType.ASSIGN_DIVIDE,
    "(": TokenType.OPEN_PAREN,
    ")": TokenType.CLOSE_PAREN,
    "{": TokenType.OPEN_BRACE,
    "}": TokenType.CLOSE_BRACE,
    "[": TokenType.OPEN_BRACKET,
    "]": TokenType.CLOSE_BRACKET,
    ",": TokenType.COMMA,
    ".": TokenType.PERIOD,
    "|": TokenType.PIPE,
    ":": TokenType.COLON,
    "::": TokenType.DOUBLE_COLON,
    "!": TokenType.EXCLAMATION,
    ">>": TokenType.CAST,
}

# A source file must select exactly one memory-management strategy.
DIRECTIVES = {
    "$MEM-GC": TokenType.DIRECTIVE,
    "$MEM-MANUAL": TokenType.DIRECTIVE,
}

# Prefixes beginning with m/c encode mutable/constant primitive types.
TYPE_KEYWORDS = {
    "void",
    "str",
    "char",
    "bln",
    "aint",
    "dml",
    "f32",
    "f64",
    "si8",
    "si16",
    "si32",
    "si64",
    "ui8",
    "ui16",
    "ui32",
    "ui64",
    "mstr",
    "mbln",
    "msi8",
    "msi16",
    "msi32",
    "msi64",
    "mui8",
    "mui16",
    "mui32",
    "mui64",
    "maint",
    "mf32",
    "mf64",
    "mdml",
    "cstr",
    "cbln",
    "csi8",
    "csi16",
    "csi32",
    "csi64",
    "cui8",
    "cui16",
    "cui32",
    "cui64",
    "caint",
    "cf32",
    "cf64",
    "cdml",
    "cchar",
    "mchar",
}


# These are converted from source words to Python booleans during lexing.
BOOLEAN_LITERALS = {
    "true",
    "false",
}


@dataclass
class Token:
    # Source coordinates are retained so lexer and parser errors can be precise.
    type: TokenType
    value: str | None = None
    line: int | None = None
    col: int | None = None
