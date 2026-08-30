"""File is here to allow TeapotLang to be used in-browser as a demo/integrated system."""

from dataclasses import fields, is_dataclass
from enum import Enum

from teapot.lexer import Lexer
from teapot.parser import Parser
from teapot.semantic import SemanticAnalyser


def _serialise(value):
    if isinstance(value, Enum):
        return value.name

    if is_dataclass(value):
        return {
            field.name: _serialise(getattr(value, field.name))
            for field in fields(value)
        }

    if isinstance(value, list):
        return [_serialise(item) for item in value]

    if isinstance(value, tuple):
        return [_serialise(item) for item in value]

    if isinstance(value, dict):
        return {
            str(key): _serialise(item)
            for key, item in value.items()
        }

    return value


def _scope_name(scope, global_scope):
    if scope is global_scope:
        return "module"

    for name, symbol in global_scope.symbols.items():
        if symbol.scope is scope:
            return name

    return "local"


def compile_source(source):
    """Run the real lexer, parser, and semantic pass and return plain data."""

    tokens = Lexer(source).tokenise()
    tree = Parser(tokens).parse()

    analyser = SemanticAnalyser(tree, False)
    analyser.analyse()

    global_scope = analyser.global_scope

    symbols = []

    for name, symbol in global_scope.symbols.items():
        symbols.append(
            {
                "name": name,
                "kind": symbol.kind,
                "type": _serialise(symbol.type),
                "scope": "module",
                "members": [],
            }
        )

        if symbol.scope is not global_scope:
            for child_name, child in symbol.scope.symbols.items():
                symbols.append(
                    {
                        "name": child_name,
                        "kind": child.kind,
                        "type": _serialise(child.type),
                        "scope": _scope_name(
                            symbol.scope,
                            global_scope,
                        ),
                        "members": [],
                    }
                )

    return {
        "tokens": [
            {
                "type": token.type.name,
                "value": _serialise(token.value),
                "line": token.line,
                "col": token.col,
            }
            for token in tokens
        ],
        "ast": _serialise(tree),
        "symbols": symbols,
        "memory_mode": _serialise(tree.memory_mode),
    }
