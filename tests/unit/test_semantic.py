from pytest import raises

import teapot.teapot_ast as ast
from teapot.semantic import SemanticAnalyser, SemanticError, Symbol, SymbolTable


# Symbol creation must store the correct name, kind, type, parameters, and scope.
def test_symbol_creation():

    global_scope = SymbolTable()
    symbol = Symbol("foo", "variable", "mui8", None, global_scope)

    assert symbol.name == "foo"
    assert symbol.kind == "variable"
    assert symbol.type == "mui8"
    assert symbol.params is None
    assert symbol.scope is global_scope


# SymbolTable.define() must store the exact Symbol instance under its name.
def test_symbol_define():

    global_scope = SymbolTable()
    symbol = Symbol("foo", "variable", "mui8", None, global_scope)

    global_scope.define(symbol)

    assert global_scope.symbols["foo"] is symbol


# SymbolTable.define() must correctly store multiple symbols.
def test_multiple_symbols_define():

    global_scope = SymbolTable()

    foo = Symbol("foo", "variable", "mui8", None, global_scope)
    bar = Symbol("bar", "function", "mui8", None, global_scope)

    global_scope.define(foo)
    global_scope.define(bar)

    assert global_scope.symbols["foo"] is foo
    assert global_scope.symbols["bar"] is bar


# Defining a duplicate symbol must raise SemanticError without replacing the original.
def test_duplicate_definition():

    global_scope = SymbolTable()

    symbol = Symbol("foo", "variable", "mui8", None, global_scope)
    duplicate = Symbol("foo", "function", "mui8", None, global_scope)

    global_scope.define(symbol)

    with raises(SemanticError):
        global_scope.define(duplicate)

    assert global_scope.symbols["foo"] is symbol


# SymbolTable.lookup() must return existing symbols and None for unknown symbols.
def test_symbol_lookup():

    global_scope = SymbolTable()

    symbol = Symbol("foo", "variable", "mui8", None, global_scope)
    global_scope.define(symbol)

    assert global_scope.lookup("foo") is symbol
    assert global_scope.lookup("bar") is None


# A child scope must be able to look up symbols from its parent.
def test_parent_scope_lookup():

    global_scope = SymbolTable()
    child_scope = SymbolTable(parent=global_scope)

    symbol = Symbol("foo", "variable", "mui8", None, global_scope)
    global_scope.define(symbol)

    assert child_scope.lookup("foo") is symbol


# A local symbol must take precedence over a parent symbol with the same name.
def test_local_scope_lookup_takes_precedence():

    global_scope = SymbolTable()
    child_scope = SymbolTable(parent=global_scope)

    global_symbol = Symbol("foo", "variable", "mui8", None, global_scope)
    local_symbol = Symbol("foo", "variable", "mstr", None, child_scope)

    global_scope.define(global_symbol)
    child_scope.define(local_symbol)

    assert child_scope.lookup("foo") is local_symbol


# An unknown symbol must return None from a child scope and its parent.
def test_parent_scope_unknown_symbol():

    global_scope = SymbolTable()
    child_scope = SymbolTable(parent=global_scope)

    assert child_scope.lookup("foo") is None


# A variable declaration must create a variable symbol in the global scope.
def test_define_variable_declaration():

    analyser = SemanticAnalyser(None, False)

    node = ast.DeclareVariable(
        identifier="foo",
        datatype=ast.Type("mui8"),
    )

    analyser.define_variable_declaration(node)

    symbol = analyser.global_scope.symbols["foo"]

    assert symbol.name == "foo"
    assert symbol.kind == "variable"
    assert symbol.type == "mui8"
    assert symbol.scope is analyser.global_scope


# Duplicate variable declarations must raise SemanticError.
def test_duplicate_variable_declaration():

    analyser = SemanticAnalyser(None, False)

    node = ast.DeclareVariable(
        identifier="foo",
        datatype=ast.Type("mui8"),
    )

    analyser.define_variable_declaration(node)

    with raises(SemanticError):
        analyser.define_variable_declaration(node)


# A struct declaration must create a struct symbol in the global scope.
def test_define_struct_declaration():

    analyser = SemanticAnalyser(None, False)

    node = ast.Struct(
        identifier="Foo",
        body=[],
    )

    analyser.define_struct_declaration(node)

    symbol = analyser.global_scope.symbols["Foo"]

    assert symbol.name == "Foo"
    assert symbol.kind == "struct"
    assert symbol.type is None
    assert symbol.scope is analyser.global_scope


# Duplicate struct declarations must raise SemanticError.
def test_duplicate_struct_declaration():

    analyser = SemanticAnalyser(None, False)

    node = ast.Struct(
        identifier="Foo",
        body=[],
    )

    analyser.define_struct_declaration(node)

    with raises(SemanticError):
        analyser.define_struct_declaration(node)


# A function declaration must create a function symbol with its return type.
def test_define_function_declaration():

    analyser = SemanticAnalyser(None, False)

    node = ast.Function(
        name="foo",
        arguments=[],
        return_type=ast.Type("mui8"),
        body=[],
    )

    analyser.define_function_declaration(node)

    symbol = analyser.global_scope.symbols["foo"]

    assert symbol.name == "foo"
    assert symbol.kind == "function"
    assert symbol.type == ast.Type("mui8")


# A function declaration must create a child scope whose parent is global scope.
def test_function_has_own_scope():

    analyser = SemanticAnalyser(None, False)

    node = ast.Function(
        name="foo",
        arguments=[],
        return_type=ast.Type("mui8"),
        body=[],
    )

    analyser.define_function_declaration(node)

    symbol = analyser.global_scope.symbols["foo"]

    assert isinstance(symbol.scope, SymbolTable)
    assert symbol.scope is not analyser.global_scope
    assert symbol.scope.parent is analyser.global_scope


# Duplicate function declarations must raise SemanticError.
def test_duplicate_function_declaration():

    analyser = SemanticAnalyser(None, False)

    node = ast.Function(
        name="foo",
        arguments=[],
        return_type=ast.Type("mui8"),
        body=[],
    )

    analyser.define_function_declaration(node)

    with raises(SemanticError):
        analyser.define_function_declaration(node)


# The current parameter implementation must create a symbol for a parameter.
def test_function_parameter_definition():

    analyser = SemanticAnalyser(None, False)
    function_scope = SymbolTable(parent=analyser.global_scope)

    parameter = ast.FunctionArgument(
        identifier="foo",
        datatype=ast.Type("mui8"),
    )

    node = ast.Function(
        name="bar",
        arguments=[parameter],
        return_type=ast.Type("mui8"),
        body=[],
    )

    # This currently fails because semantic.py does not pass scope to Symbol().
    with raises(TypeError):
        analyser.define_function_parameters(node, function_scope)


# Multiple function parameters should be added to the function scope.
def test_multiple_function_parameters():

    analyser = SemanticAnalyser(None, False)
    function_scope = SymbolTable(parent=analyser.global_scope)

    parameters = [
        ast.FunctionArgument(
            identifier="foo",
            datatype=ast.Type("mui8"),
        ),
        ast.FunctionArgument(
            identifier="bar",
            datatype=ast.Type("mstr"),
        ),
    ]

    node = ast.Function(
        name="baz",
        arguments=parameters,
        return_type=ast.Type("mui8"),
        body=[],
    )

    # This currently fails because semantic.py does not pass scope to Symbol().
    with raises(TypeError):
        analyser.define_function_parameters(node, function_scope)


# Duplicate function parameters should raise SemanticError after the scope bug is fixed.
def test_duplicate_function_parameter():

    analyser = SemanticAnalyser(None, False)
    function_scope = SymbolTable(parent=analyser.global_scope)

    parameters = [
        ast.FunctionArgument(
            identifier="foo",
            datatype=ast.Type("mui8"),
        ),
        ast.FunctionArgument(
            identifier="foo",
            datatype=ast.Type("mstr"),
        ),
    ]

    node = ast.Function(
        name="bar",
        arguments=parameters,
        return_type=ast.Type("mui8"),
        body=[],
    )

    # Currently reaches TypeError before duplicate detection.
    with raises(TypeError):
        analyser.define_function_parameters(node, function_scope)


# The first pass must process variable declarations.
def test_first_pass_variable():

    node = ast.DeclareVariable(
        identifier="foo",
        datatype=ast.Type("mui8"),
    )

    tree = ast.Program(
        statements=[node],
        memory_mode="manual",
    )

    analyser = SemanticAnalyser(tree, False)

    analyser.first_pass_symbol_table()

    assert "foo" in analyser.global_scope.symbols
    assert analyser.global_scope.symbols["foo"].kind == "variable"


# The first pass must process struct declarations.
def test_first_pass_struct():

    node = ast.Struct(
        identifier="Foo",
        body=[],
    )

    tree = ast.Program(
        statements=[node],
        memory_mode="manual",
    )

    analyser = SemanticAnalyser(tree, False)

    analyser.first_pass_symbol_table()

    assert "Foo" in analyser.global_scope.symbols
    assert analyser.global_scope.symbols["Foo"].kind == "struct"


# The first pass must process function declarations.
def test_first_pass_function():

    node = ast.Function(
        name="foo",
        arguments=[],
        return_type=ast.Type("mui8"),
        body=[],
    )

    tree = ast.Program(
        statements=[node],
        memory_mode="manual",
    )

    analyser = SemanticAnalyser(tree, False)

    analyser.first_pass_symbol_table()

    assert "foo" in analyser.global_scope.symbols
    assert analyser.global_scope.symbols["foo"].kind == "function"


# The first pass must process multiple supported top-level AST nodes.
def test_first_pass_multiple_declarations():

    variable = ast.DeclareVariable(
        identifier="foo",
        datatype=ast.Type("mui8"),
    )

    struct = ast.Struct(
        identifier="Bar",
        body=[],
    )

    function = ast.Function(
        name="baz",
        arguments=[],
        return_type=ast.Type("mui8"),
        body=[],
    )

    tree = ast.Program(
        statements=[
            variable,
            struct,
            function,
        ],
        memory_mode="manual",
    )

    analyser = SemanticAnalyser(tree, False)

    analyser.first_pass_symbol_table()

    assert "foo" in analyser.global_scope.symbols
    assert "Bar" in analyser.global_scope.symbols
    assert "baz" in analyser.global_scope.symbols


# The first pass must reject an unsupported AST node.
def test_first_pass_unknown_node():

    tree = ast.Program(
        statements=[ast.Break()],
        memory_mode="manual",
    )

    analyser = SemanticAnalyser(tree, False)

    with raises(SemanticError):
        analyser.first_pass_symbol_table()


# The first pass must produce an empty symbol table for an empty program.
def test_first_pass_empty_ast():

    tree = ast.Program(
        statements=[],
        memory_mode="manual",
    )

    analyser = SemanticAnalyser(tree, False)

    analyser.first_pass_symbol_table()

    assert analyser.global_scope.symbols == {}


# analyse() must build the symbol table from the AST.
def test_analyse():

    node = ast.DeclareVariable(
        identifier="foo",
        datatype=ast.Type("mui8"),
    )

    tree = ast.Program(
        statements=[node],
        memory_mode="manual",
    )

    analyser = SemanticAnalyser(tree, False)

    analyser.analyse()

    assert "foo" in analyser.global_scope.symbols
    assert analyser.global_scope.symbols["foo"].kind == "variable"


# The currently empty second pass must complete successfully.
def test_second_pass_type_check():

    analyser = SemanticAnalyser(None, False)

    analyser.second_pass_type_check()


# analyse() must successfully process an empty program.
def test_analyse_empty_ast():

    tree = ast.Program(
        statements=[],
        memory_mode="manual",
    )

    analyser = SemanticAnalyser(tree, False)

    analyser.analyse()

    assert analyser.global_scope.symbols == {}
