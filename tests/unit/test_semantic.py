"""
Comprehensive unit tests for semantic analysis.

Tests cover:
- Symbol creation and properties
- Symbol table operations (define, lookup)
- Scope hierarchy and resolution
- Variable declarations
- Function declarations
- Struct declarations
- Semantic error handling
"""

from pytest import raises

import teapot.teapot_ast as ast
from teapot.lexer import Lexer
from teapot.parser import Parser
from teapot.semantic import SemanticAnalyser, SemanticError, Symbol, SymbolTable

# ============================================================================
# SYMBOL AND SYMBOL TABLE TESTS
# ============================================================================


# Symbol creation must store the correct name, kind, type, parameters, and scope.
def test_symbol_creation():
    """Test that Symbol stores all attributes correctly."""
    global_scope = SymbolTable()
    symbol = Symbol("foo", "variable", "mui8", None, global_scope)

    assert symbol.name == "foo"
    assert symbol.kind == "variable"
    assert symbol.type == "mui8"
    assert symbol.params is None
    assert symbol.scope is global_scope


# Symbol creation must handle different kinds.
def test_symbol_creation_with_different_kinds():
    """Test Symbol creation with various kinds."""
    global_scope = SymbolTable()

    var_symbol = Symbol("var", "variable", "mstr", None, global_scope)
    assert var_symbol.kind == "variable"

    func_symbol = Symbol("func", "function", "mstr", [(("x", "mui8"))], global_scope)
    assert func_symbol.kind == "function"
    assert func_symbol.params == [(("x", "mui8"))]

    struct_symbol = Symbol("MyStruct", "struct", None, None, global_scope)
    assert struct_symbol.kind == "struct"
    assert struct_symbol.type is None


# Symbol must handle different data types.
def test_symbol_creation_with_different_types():
    """Test Symbol creation with various data types."""
    global_scope = SymbolTable()

    types = [
        "mui8",
        "mui16",
        "mui32",
        "mui64",
        "msi8",
        "msi16",
        "msi32",
        "msi64",
        "mstr",
        "mchar",
        "mbln",
        "mf32",
        "mf64",
        "cstr",
        "cchar",
        "cbln",
        "cf32",
        "cf64",
    ]

    for dtype in types:
        symbol = Symbol(f"var_{dtype}", "variable", dtype, None, global_scope)
        assert symbol.type == dtype


# SymbolTable.define() must store the exact Symbol instance under its name.
def test_symbol_define():
    """Test that define() stores symbols in the table."""
    global_scope = SymbolTable()
    symbol = Symbol("foo", "variable", "mui8", None, global_scope)

    global_scope.define(symbol)

    assert global_scope.symbols["foo"] is symbol


# SymbolTable.define() must correctly store multiple symbols.
def test_multiple_symbols_define():
    """Test that multiple symbols can be stored in one scope."""
    global_scope = SymbolTable()

    foo = Symbol("foo", "variable", "mui8", None, global_scope)
    bar = Symbol("bar", "function", "mui8", None, global_scope)
    baz = Symbol("baz", "struct", None, None, global_scope)

    global_scope.define(foo)
    global_scope.define(bar)
    global_scope.define(baz)

    assert global_scope.symbols["foo"] is foo
    assert global_scope.symbols["bar"] is bar
    assert global_scope.symbols["baz"] is baz
    assert len(global_scope.symbols) == 3


# Defining a duplicate symbol must raise SemanticError without replacing the original.
def test_duplicate_definition():
    """Test that duplicate definitions raise SemanticError."""
    global_scope = SymbolTable()

    symbol = Symbol("foo", "variable", "mui8", None, global_scope)
    duplicate = Symbol("foo", "function", "mui8", None, global_scope)

    global_scope.define(symbol)

    with raises(SemanticError):
        global_scope.define(duplicate)

    assert global_scope.symbols["foo"] is symbol


# Duplicate definitions should not be replaced.
def test_duplicate_definition_preserves_original():
    """Test that original symbol is preserved after duplicate definition attempt."""
    global_scope = SymbolTable()

    original = Symbol("var", "variable", "mstr", None, global_scope)
    dup1 = Symbol("var", "function", "mstr", None, global_scope)
    dup2 = Symbol("var", "struct", "mstr", None, global_scope)

    global_scope.define(original)

    with raises(SemanticError):
        global_scope.define(dup1)

    with raises(SemanticError):
        global_scope.define(dup2)

    assert global_scope.symbols["var"] is original
    assert global_scope.symbols["var"].kind == "variable"


# SymbolTable.lookup() must return existing symbols and None for unknown symbols.
def test_symbol_lookup():
    """Test that lookup returns symbols or None."""
    global_scope = SymbolTable()
    symbol = Symbol("foo", "variable", "mui8", None, global_scope)

    global_scope.define(symbol)

    assert global_scope.lookup("foo") is symbol
    assert global_scope.lookup("bar") is None
    assert global_scope.lookup("unknown") is None


# ============================================================================
# SCOPE HIERARCHY TESTS
# ============================================================================


# A child scope must be able to look up symbols from its parent.
def test_parent_scope_lookup():
    """Test that child scope can access parent symbols."""
    global_scope = SymbolTable()
    child_scope = SymbolTable(parent=global_scope)

    symbol = Symbol("foo", "variable", "mui8", None, global_scope)
    global_scope.define(symbol)

    assert child_scope.lookup("foo") is symbol


# A local symbol must take precedence over a parent symbol with the same name.
def test_local_scope_lookup_takes_precedence():
    """Test that local symbols shadow parent symbols."""
    global_scope = SymbolTable()
    child_scope = SymbolTable(parent=global_scope)

    global_symbol = Symbol("foo", "variable", "mui8", None, global_scope)
    local_symbol = Symbol("foo", "variable", "mstr", None, child_scope)

    global_scope.define(global_symbol)
    child_scope.define(local_symbol)

    assert child_scope.lookup("foo") is local_symbol
    assert child_scope.lookup("foo").type == "mstr"


# An unknown symbol must return None from a child scope and its parent.
def test_parent_scope_unknown_symbol():
    """Test that lookup returns None for unknown symbols in hierarchy."""
    global_scope = SymbolTable()
    child_scope = SymbolTable(parent=global_scope)

    assert child_scope.lookup("foo") is None
    assert global_scope.lookup("foo") is None


# Multiple level scope hierarchy must work correctly.
def test_deep_scope_hierarchy():
    """Test scope resolution through multiple levels."""
    global_scope = SymbolTable()
    level1 = SymbolTable(parent=global_scope)
    level2 = SymbolTable(parent=level1)
    level3 = SymbolTable(parent=level2)

    global_sym = Symbol("global_var", "variable", "mui8", None, global_scope)
    level1_sym = Symbol("level1_var", "variable", "mstr", None, level1)
    level2_sym = Symbol("level2_var", "variable", "cbln", None, level2)

    global_scope.define(global_sym)
    level1.define(level1_sym)
    level2.define(level2_sym)

    # Level 3 can access all symbols above
    assert level3.lookup("global_var") is global_sym
    assert level3.lookup("level1_var") is level1_sym
    assert level3.lookup("level2_var") is level2_sym
    assert level3.lookup("unknown") is None


# Shadowing at multiple levels must work correctly.
def test_shadowing_at_multiple_levels():
    """Test that shadowing works correctly through multiple scope levels."""
    global_scope = SymbolTable()
    child_scope = SymbolTable(parent=global_scope)
    grandchild_scope = SymbolTable(parent=child_scope)

    global_sym = Symbol("x", "variable", "mui8", None, global_scope)
    child_sym = Symbol("x", "variable", "mstr", None, child_scope)
    grandchild_sym = Symbol("x", "variable", "cbln", None, grandchild_scope)

    global_scope.define(global_sym)
    child_scope.define(child_sym)
    grandchild_scope.define(grandchild_sym)

    assert global_scope.lookup("x").type == "mui8"
    assert child_scope.lookup("x").type == "mstr"
    assert grandchild_scope.lookup("x").type == "cbln"


# ============================================================================
# SEMANTIC ANALYSER TESTS
# ============================================================================


# SemanticAnalyser must be initializable with AST and trace flag.
def test_semantic_analyser_initialization():
    """Test SemanticAnalyser initialization."""
    ast_tree = ast.Program(statements=[], memory_mode="$MEM-GC")
    analyser = SemanticAnalyser(ast_tree, trace=False)

    assert analyser.ast_tree is ast_tree
    assert analyser.trace is False


# SemanticAnalyser must handle empty AST trees.
def test_analyser_empty_program():
    """Test analysis of empty program."""
    ast_tree = ast.Program(statements=[], memory_mode="$MEM-GC")
    analyser = SemanticAnalyser(ast_tree, trace=False)

    analyser.analyse()

    assert hasattr(analyser, "global_scope")
    assert len(analyser.global_scope.symbols) == 0


# ============================================================================
# VARIABLE DECLARATION TESTS
# ============================================================================


def lex_and_parse(source):
    """Helper to lex and parse source code."""
    lexer = Lexer(source)
    tokens = lexer.tokenise()
    parser = Parser(tokens)
    return parser.parse()


# Analyse single variable declaration in global scope.
def test_single_variable_declaration():
    """Test analysis of a single variable declaration."""
    source = """
        $MEM-GC
        val mui8 x = 42.
    """
    program = lex_and_parse(source)
    analyser = SemanticAnalyser(program, trace=False)
    analyser.analyse()

    symbol = analyser.global_scope.lookup("x")
    assert symbol is not None
    assert symbol.name == "x"
    assert symbol.kind == "variable"
    assert symbol.type == "mui8"


# Analyse multiple variable declarations.
def test_multiple_variable_declarations():
    """Test analysis of multiple variable declarations."""
    source = """
        $MEM-GC
        val mui8 a = 1.
        val mstr b = "test".
        val cbln c = true.
    """
    program = lex_and_parse(source)
    analyser = SemanticAnalyser(program, trace=False)
    analyser.analyse()

    a = analyser.global_scope.lookup("a")
    b = analyser.global_scope.lookup("b")
    c = analyser.global_scope.lookup("c")

    assert a.type == "mui8"
    assert b.type == "mstr"
    assert c.type == "cbln"


# Duplicate variable declarations must raise error.
def test_duplicate_variable_declarations():
    """Test that duplicate variable declarations raise SemanticError."""
    source = """
        $MEM-GC
        val mui8 x = 1.
        val mstr x = "test".
    """
    program = lex_and_parse(source)
    analyser = SemanticAnalyser(program, trace=False)

    with raises(SemanticError):
        analyser.analyse()


# ============================================================================
# FUNCTION DECLARATION TESTS
# ============================================================================


# Analyse function declaration with no parameters.
def test_function_declaration_no_params():
    """Test analysis of function with no parameters."""
    source = """
        $MEM-GC
        fc get_answer()!mui8 {
        } """
    program = lex_and_parse(source)
    analyser = SemanticAnalyser(program, trace=False)
    analyser.analyse()

    func_symbol = analyser.global_scope.lookup("get_answer")
    assert func_symbol is not None
    assert func_symbol.kind == "function"
    assert func_symbol.type == "mui8"
    assert func_symbol.params == []


# Analyse function declaration with parameters.
def test_function_declaration_with_params():
    """Test analysis of function with parameters."""
    source = """
        $MEM-GC
        fc add(mui8 a, mui8 b)!mui8 {
        } """
    program = lex_and_parse(source)
    analyser = SemanticAnalyser(program, trace=False)
    analyser.analyse()

    func_symbol = analyser.global_scope.lookup("add")
    assert func_symbol is not None
    assert func_symbol.kind == "function"
    assert func_symbol.type == "mui8"
    assert len(func_symbol.params) == 2


# Duplicate function declarations must raise error.
def test_duplicate_function_declarations():
    """Test that duplicate function declarations raise SemanticError."""
    source = """
        $MEM-GC
        fc get_value()!void {
        }
        fc get_value()!void {
        } """
    program = lex_and_parse(source)
    analyser = SemanticAnalyser(program, trace=False)

    with raises(SemanticError):
        analyser.analyse()


# Function scope must have its own symbol table.
def test_function_scope_isolation():
    """Test that function creates its own scope."""
    source = """
        $MEM-GC
        val mui8 x = 10.
        fc test()!void {
        } """
    program = lex_and_parse(source)
    analyser = SemanticAnalyser(program, trace=False)
    analyser.analyse()

    func_symbol = analyser.global_scope.lookup("test")
    assert func_symbol.scope is not analyser.global_scope


# ============================================================================
# STRUCT DECLARATION TESTS
# ============================================================================


# Analyse sct declaration.
def test_struct_declaration():
    """Test analysis of sct declaration."""
    source = """
        $MEM-GC
        sct Point {
        } """
    program = lex_and_parse(source)
    analyser = SemanticAnalyser(program, trace=False)
    analyser.analyse()

    struct_symbol = analyser.global_scope.lookup("Point")
    assert struct_symbol is not None
    assert struct_symbol.kind == "struct"


# Duplicate sct declarations must raise error.
def test_duplicate_struct_declarations():
    """Test that duplicate sct declarations raise SemanticError."""
    source = """
        $MEM-GC
        sct Point {
        }
        sct Point {
        } """
    program = lex_and_parse(source)
    analyser = SemanticAnalyser(program, trace=False)

    with raises(SemanticError):
        analyser.analyse()


# ============================================================================
# MIXED DECLARATION TESTS
# ============================================================================


# Analyse multiple different types of declarations.
def test_mixed_declarations():
    """Test analysis of mixed variable, function, and sct declarations."""
    source = """
        $MEM-GC
        val mui8 count = 0.
        fc get_count()!void {
        }
        sct Result {
        }
        val mstr status = "ready".
    """
    program = lex_and_parse(source)
    analyser = SemanticAnalyser(program, trace=False)
    analyser.analyse()

    count = analyser.global_scope.lookup("count")
    get_count = analyser.global_scope.lookup("get_count")
    result = analyser.global_scope.lookup("Result")
    status = analyser.global_scope.lookup("status")

    assert count.kind == "variable"
    assert get_count.kind == "function"
    assert result.kind == "struct"
    assert status.kind == "variable"
    assert len(analyser.global_scope.symbols) == 4


# Mixing variable and sct with same name must raise error.
def test_duplicate_variable_and_struct():
    """Test that variable and sct with same name raises SemanticError."""
    source = """
        $MEM-GC
        val mui8 Item = 0.
        sct Item {
        } """
    program = lex_and_parse(source)
    analyser = SemanticAnalyser(program, trace=False)

    with raises(SemanticError):
        analyser.analyse()


# A variable declaration must create a variable symbol in the supplied scope.
def test_define_variable_declaration():
    analyser = SemanticAnalyser(None, False)
    scope = SymbolTable()

    node = ast.DeclareVariable(
        identifier="foo",
        datatype=ast.Type("mui8"),
    )

    analyser.define_variable_declaration(node, scope)

    symbol = scope.symbols["foo"]

    assert symbol.name == "foo"
    assert symbol.kind == "variable"
    assert symbol.type == "mui8"
    assert symbol.scope is scope


# Duplicate variable declarations must raise SemanticError.
def test_duplicate_variable_declaration():
    analyser = SemanticAnalyser(None, False)
    scope = SymbolTable()

    node = ast.DeclareVariable(
        identifier="foo",
        datatype=ast.Type("mui8"),
    )

    analyser.define_variable_declaration(node, scope)

    with raises(SemanticError):
        analyser.define_variable_declaration(node, scope)


# A sct declaration must create a sct symbol in the supplied scope.
def test_define_struct_declaration():
    analyser = SemanticAnalyser(None, False)
    scope = SymbolTable()

    node = ast.Struct(
        identifier="Foo",
        body=[],
    )

    analyser.define_struct_declaration(node, scope)

    symbol = scope.symbols["Foo"]

    assert symbol.name == "Foo"
    assert symbol.kind == "struct"
    assert symbol.type is None
    assert symbol.scope is scope


# Duplicate sct declarations must raise SemanticError.
def test_duplicate_struct_declaration():
    analyser = SemanticAnalyser(None, False)
    scope = SymbolTable()

    node = ast.Struct(
        identifier="Foo",
        body=[],
    )

    analyser.define_struct_declaration(node, scope)

    with raises(SemanticError):
        analyser.define_struct_declaration(node, scope)


# A function declaration must create a function symbol with its return type.
def test_define_function_declaration():
    analyser = SemanticAnalyser(None, False)
    scope = SymbolTable()

    node = ast.Function(
        name="foo",
        arguments=[],
        return_type=ast.Type("mui8"),
        body=[],
    )

    analyser.define_function_declaration(node, scope)

    symbol = scope.symbols["foo"]

    assert symbol.name == "foo"
    assert symbol.kind == "function"
    assert symbol.type == ast.Type("mui8")


# A function declaration must create a child scope whose parent is the supplied scope.
def test_function_has_own_scope():
    analyser = SemanticAnalyser(None, False)
    scope = SymbolTable()

    node = ast.Function(
        name="foo",
        arguments=[],
        return_type=ast.Type("mui8"),
        body=[],
    )

    analyser.define_function_declaration(node, scope)

    symbol = scope.symbols["foo"]

    assert isinstance(symbol.scope, SymbolTable)
    assert symbol.scope is not scope
    assert symbol.scope.parent is scope


# Duplicate function declarations must raise SemanticError.
def test_duplicate_function_declaration():
    analyser = SemanticAnalyser(None, False)
    scope = SymbolTable()

    node = ast.Function(
        name="foo",
        arguments=[],
        return_type=ast.Type("mui8"),
        body=[],
    )

    analyser.define_function_declaration(node, scope)

    with raises(SemanticError):
        analyser.define_function_declaration(node, scope)


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


# The first pass must process sct declarations.
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

    sct = ast.Struct(
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
            sct,
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
