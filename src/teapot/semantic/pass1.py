import teapot.teapot_ast as ast
from teapot.debug import print
from teapot.errors import (
    InvalidControlFlowError,
    UndefinedVariableError,
    UnknownNodeError,
)
from teapot.semantic.symbol_table import SymbolTable
from teapot.semantic.symbols import Symbol


class SymbolTableBuilder:
    def __init__(self, trace=False):
        self.trace = trace
        self.loop_depth = 0

    def build(self, ast_tree):
        global_scope = SymbolTable()

        for node in ast_tree.statements:
            if self.trace:
                print(type(node).__name__ + ":")
            self.register_node(node, global_scope)

        return global_scope

    def register_node(self, node, scope):
        scope.current_location = getattr(node, "location", None)
        match node:
            case ast.DeclareVariable():
                self.register_variable(node, scope)
            case ast.Assignment():
                self.register_assignment(node, scope)
            case ast.Struct():
                self.register_struct(node, scope)
            case ast.Function():
                self.register_function(node, scope)
            case ast.Enum():
                self.register_enum(node, scope)
            case ast.EnumMember():
                self.register_enum_member(node, scope)
            case ast.StructField():
                self.register_struct_field(node, scope)
            case ast.Error():
                self.register_error(node, scope)
            case ast.ErrorMember():
                self.register_error_member(node, scope)
            case ast.Operator():
                self.register_operator(node, scope)
            case ast.OperatorArgument():
                self.register_operator_argument(node, scope)
            case ast.Return():
                pass
            case ast.Break() | ast.Continue():
                if self.loop_depth > 0:
                    return
                raise InvalidControlFlowError(
                    f"{type(node).__name__} statements are not valid in this scope.",
                    node,
                )
            case ast.If():
                self.register_if(node, scope)
            case ast.For():
                self.register_for(node, scope)
            case ast.While():
                self.register_while(node, scope)
            case ast.Do():
                self.register_do_block(node, scope)
            case _:
                raise UnknownNodeError(
                    f"unsupported AST node `{type(node).__name__}`",
                    node,
                )

    def register_if(self, node, scope):
        if_scope = SymbolTable(scope)

        for statement in node.body:
            self.register_node(statement, if_scope)

        for elif_node in node.elifs:
            elif_scope = SymbolTable(scope)

            for statement in elif_node.body:
                self.register_node(statement, elif_scope)

        if node.else_body is not None:
            else_scope = SymbolTable(scope)

            for statement in node.else_body.body:
                self.register_node(statement, else_scope)

    def register_for(self, node, scope):
        for_scope = SymbolTable(scope)

        for_scope.define(
            Symbol(
                node.variable,
                "for_variable",
                None,
                for_scope,
            )
        )

        self.loop_depth += 1
        try:
            for statement in node.body:
                self.register_node(statement, for_scope)
        finally:
            self.loop_depth -= 1

    def register_while(self, node, scope):
        while_scope = SymbolTable(scope)

        self.loop_depth += 1
        try:
            for statement in node.body:
                self.register_node(statement, while_scope)
        finally:
            self.loop_depth -= 1

    def register_do_block(self, node, scope):
        do_scope = SymbolTable(scope)

        for statement in node.body:
            self.register_node(statement, do_scope)

        self.register_fail(node.fail, scope)

    def register_fail(self, node, scope):
        fail_scope = SymbolTable(scope)

        fail_scope.define(
            Symbol(
                node.identifier,
                "error_variable",
                node.error,
                fail_scope,
            )
        )

        for statement in node.body:
            self.register_node(statement, fail_scope)

    def register_assignment(self, node, scope):
        target = node.target

        if not isinstance(target, ast.Identifier):
            return

        if scope.lookup(target.name) is None:
            raise UndefinedVariableError(
                f"Variable `{target.name}` cannot be assigned because it does not exist!",
                node,
            )

    def register_operator(self, node, scope):
        operator_scope = SymbolTable(scope)

        scope.define(
            Symbol(
                node.symbol,
                "operator",
                node.return_type,
                scope,
                operator_scope,
            )
        )

        self.register_operator_arguments(node, operator_scope)
        self.register_operator_body(node, operator_scope)

    def register_operator_body(self, node, scope):
        for statement in node.body:
            self.register_node(statement, scope)

    def register_operator_arguments(self, node, scope):
        for argument in node.arguments:
            self.register_node(argument, scope)

    def register_operator_argument(self, node, scope):
        scope.define(
            Symbol(
                node.name,
                "operator_argument",
                node.datatype,
                scope,
            )
        )

    def register_error(self, node, scope):
        error_scope = SymbolTable(parent=scope)

        scope.define(
            Symbol(
                node.identifier,
                "error",
                None,
                scope,
                error_scope,
            )
        )

        self.register_error_members(node, error_scope)

    def register_error_members(self, node, scope):
        for member in node.body:
            self.register_node(member, scope)

    def register_error_member(self, node, scope):
        scope.define(
            Symbol(
                node.name,
                "error_member",
                node.datatype,
                scope,
            )
        )

    def register_enum_member(self, node, scope):
        scope.define(
            Symbol(
                node.name,
                "enum_member",
                None,
                scope,
            )
        )

    def register_struct_field(self, node, scope):
        scope.define(
            Symbol(
                node.identifier,
                "struct_field",
                node.datatype.name,
                scope,
            )
        )

    def register_enum(self, node, scope):
        enum_scope = SymbolTable(parent=scope)

        scope.define(
            Symbol(
                node.identifier,
                "enum",
                None,
                scope,
                enum_scope,
            )
        )

        self.register_enum_members(node, enum_scope)

        if self.trace:
            print(f"  - Found valid enum declaration: {node.identifier}.")

    def register_enum_members(self, node, scope):
        for member in node.body:
            self.register_node(member, scope)

    def register_function(self, node, scope):
        function_scope = SymbolTable(parent=scope)

        scope.define(
            Symbol(
                node.name,
                "function",
                node.return_type,
                scope,
                function_scope,
            )
        )

        for param in node.arguments:
            function_scope.define(
                Symbol(
                    param.identifier,
                    "function_parameter",
                    param.datatype,
                    function_scope,
                )
            )

        previous_loop_depth = self.loop_depth
        self.loop_depth = 0
        try:
            self.register_function_body(node, function_scope)
        finally:
            self.loop_depth = previous_loop_depth

        if self.trace:
            print(f"  - Found valid function declaration: {node.name}.")

    def register_function_body(self, node, scope):
        for statement in node.body:
            self.register_node(statement, scope)

    def register_struct_members(self, node, scope):
        for member in node.body:
            self.register_node(member, scope)

    def register_struct(self, node, scope):
        struct_scope = SymbolTable(parent=scope)

        scope.define(
            Symbol(
                node.identifier,
                "struct",
                None,
                scope,
                struct_scope,
            )
        )

        self.register_struct_members(node, struct_scope)

        if self.trace:
            print(f"  - Found valid struct declaration: {node.identifier}.")

    def register_variable(self, node, scope):
        datatype = node.datatype.name

        scope.define(
            Symbol(
                node.identifier,
                "variable",
                datatype,
                scope,
            )
        )

        if self.trace:
            print(
                f"  - Found valid variable declaration: {node.identifier}, {datatype}."
            )
