from pytest import raises

import teapot.teapot_ast as ast
from teapot.lexer import Lexer
from teapot.parser import Parser
from teapot.semantic import SemanticAnalyser, SemanticError, Symbol, SymbolTable

# ============================================================================
# SYMBOL AND SYMBOL TABLE TESTS
# ============================================================================


def test_symbol_creation():
    """Test that Symbol stores all attributes correctly."""
    global_scope = SymbolTable()
    symbol = Symbol("foo", "variable", "mui8", global_scope)

    assert symbol.name == "foo"
    assert symbol.kind == "variable"
    assert symbol.type == "mui8"
    assert symbol.scope is global_scope


def test_symbol_creation_with_different_kinds():
    """Test Symbol creation with various kinds."""
    global_scope = SymbolTable()

    var_symbol = Symbol("var", "variable", "mstr", global_scope)
    assert var_symbol.kind == "variable"

    func_symbol = Symbol("func", "function", "mstr", global_scope)
    assert func_symbol.kind == "function"
    assert func_symbol.type == "mstr"

    struct_symbol = Symbol("MyStruct", "struct", None, global_scope)
    assert struct_symbol.kind == "struct"
    assert struct_symbol.type is None


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
        symbol = Symbol(f"var_{dtype}", "variable", dtype, global_scope)
        assert symbol.type == dtype
        assert symbol.scope is global_scope


def test_symbol_define():
    """Test that define() stores symbols in the table."""
    global_scope = SymbolTable()
    symbol = Symbol("foo", "variable", "mui8", global_scope)

    global_scope.define(symbol)

    assert global_scope.symbols["foo"] is symbol


def test_multiple_symbols_define():
    """Test that multiple symbols can be stored in one scope."""
    global_scope = SymbolTable()

    foo = Symbol("foo", "variable", "mui8", global_scope)
    bar = Symbol("bar", "function", "mui8", global_scope)
    baz = Symbol("baz", "struct", None, global_scope)

    global_scope.define(foo)
    global_scope.define(bar)
    global_scope.define(baz)

    assert global_scope.symbols["foo"] is foo
    assert global_scope.symbols["bar"] is bar
    assert global_scope.symbols["baz"] is baz
    assert len(global_scope.symbols) == 3


def test_duplicate_definition():
    """Test that duplicate definitions raise SemanticError."""
    global_scope = SymbolTable()

    symbol = Symbol("foo", "variable", "mui8", global_scope)
    duplicate = Symbol("foo", "function", "mui8", global_scope)

    global_scope.define(symbol)

    with raises(SemanticError):
        global_scope.define(duplicate)

    assert global_scope.symbols["foo"] is symbol


def test_duplicate_definition_preserves_original():
    """Test that original symbol is preserved after duplicate definition."""
    global_scope = SymbolTable()

    original = Symbol("var", "variable", "mstr", global_scope)
    dup1 = Symbol("var", "function", "mstr", global_scope)
    dup2 = Symbol("var", "struct", None, global_scope)

    global_scope.define(original)

    with raises(SemanticError):
        global_scope.define(dup1)

    with raises(SemanticError):
        global_scope.define(dup2)

    assert global_scope.symbols["var"] is original
    assert global_scope.symbols["var"].kind == "variable"


def test_symbol_lookup():
    """Test that lookup returns symbols or None."""
    global_scope = SymbolTable()

    symbol = Symbol("foo", "variable", "mui8", global_scope)
    global_scope.define(symbol)

    assert global_scope.lookup("foo") is symbol
    assert global_scope.lookup("bar") is None
    assert global_scope.lookup("unknown") is None


# ============================================================================
# SCOPE HIERARCHY TESTS
# ============================================================================


def test_parent_scope_lookup():
    """Test that child scope can access parent symbols."""
    global_scope = SymbolTable()
    child_scope = SymbolTable(parent=global_scope)

    symbol = Symbol("foo", "variable", "mui8", global_scope)
    global_scope.define(symbol)

    assert child_scope.lookup("foo") is symbol


def test_local_scope_lookup_takes_precedence():
    """Test that local symbols shadow parent symbols."""
    global_scope = SymbolTable()
    child_scope = SymbolTable(parent=global_scope)

    global_symbol = Symbol("foo", "variable", "mui8", global_scope)
    local_symbol = Symbol("foo", "variable", "mstr", child_scope)

    global_scope.define(global_symbol)
    child_scope.define(local_symbol)

    assert child_scope.lookup("foo") is local_symbol
    assert child_scope.lookup("foo").type == "mstr"


def test_parent_scope_unknown_symbol():
    """Test that lookup returns None for unknown symbols in hierarchy."""
    global_scope = SymbolTable()
    child_scope = SymbolTable(parent=global_scope)

    assert child_scope.lookup("foo") is None
    assert global_scope.lookup("foo") is None


def test_deep_scope_hierarchy():
    """Test symbol resolution through multiple scope levels."""
    global_scope = SymbolTable()
    level1 = SymbolTable(parent=global_scope)
    level2 = SymbolTable(parent=level1)
    level3 = SymbolTable(parent=level2)

    global_sym = Symbol("global_var", "variable", "mui8", global_scope)
    level1_sym = Symbol("level1_var", "variable", "mstr", level1)
    level2_sym = Symbol("level2_var", "variable", "cbln", level2)

    global_scope.define(global_sym)
    level1.define(level1_sym)
    level2.define(level2_sym)

    assert level3.lookup("global_var") is global_sym
    assert level3.lookup("level1_var") is level1_sym
    assert level3.lookup("level2_var") is level2_sym
    assert level3.lookup("unknown") is None


def test_shadowing_at_multiple_levels():
    """Test that shadowing works through multiple scope levels."""
    global_scope = SymbolTable()
    child_scope = SymbolTable(parent=global_scope)
    grandchild_scope = SymbolTable(parent=child_scope)

    global_sym = Symbol("x", "variable", "mui8", global_scope)
    child_sym = Symbol("x", "variable", "mstr", child_scope)
    grandchild_sym = Symbol("x", "variable", "cbln", grandchild_scope)

    global_scope.define(global_sym)
    child_scope.define(child_sym)
    grandchild_scope.define(grandchild_sym)

    assert global_scope.lookup("x").type == "mui8"
    assert child_scope.lookup("x").type == "mstr"
    assert grandchild_scope.lookup("x").type == "cbln"


# ============================================================================
# SEMANTIC ANALYSER TESTS
# ============================================================================


def test_semantic_analyser_initialization():
    """Test SemanticAnalyser initialization."""
    ast_tree = ast.Program(
        statements=[],
        memory_mode="$MEM-GC",
    )

    analyser = SemanticAnalyser(ast_tree, trace=False)

    assert analyser.ast_tree is ast_tree
    assert analyser.trace is False


def test_analyser_empty_program():
    """Test analysis of empty program."""
    ast_tree = ast.Program(
        statements=[],
        memory_mode="$MEM-GC",
    )

    analyser = SemanticAnalyser(ast_tree, trace=False)
    analyser.analyse()

    assert hasattr(analyser, "global_scope")
    assert len(analyser.global_scope.symbols) == 0


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def lex_and_parse(source):
    """Helper to lex and parse source code."""
    lexer = Lexer(source)
    tokens = lexer.tokenise()
    parser = Parser(tokens)
    return parser.parse()


# ============================================================================
# VARIABLE DECLARATION TESTS
# ============================================================================


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
    assert symbol.scope is analyser.global_scope


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


def test_function_declaration_no_params():
    """Test analysis of function with no parameters."""
    source = """
        $MEM-GC

        fc get_answer()!mui8 {
        }
    """

    program = lex_and_parse(source)
    analyser = SemanticAnalyser(program, trace=False)
    analyser.analyse()

    func_symbol = analyser.global_scope.lookup("get_answer")

    assert func_symbol is not None
    assert func_symbol.kind == "function"
    assert func_symbol.type == "mui8"
    assert func_symbol.scope is not analyser.global_scope


def test_function_declaration_with_params():
    """Test analysis of function with parameters."""
    source = """
        $MEM-GC

        fc add(mui8 a, mui8 b)!mui8 {
        }
    """

    program = lex_and_parse(source)
    analyser = SemanticAnalyser(program, trace=False)
    analyser.analyse()

    func_symbol = analyser.global_scope.lookup("add")

    assert func_symbol is not None
    assert func_symbol.kind == "function"
    assert func_symbol.type == "mui8"
    assert func_symbol.scope is not analyser.global_scope
    assert func_symbol.scope.parent is analyser.global_scope


def test_duplicate_function_declarations():
    """Test that duplicate function declarations raise SemanticError."""
    source = """
        $MEM-GC

        fc get_value()!mui8 {
        }

        fc get_value()!mui8 {
        }
    """

    program = lex_and_parse(source)
    analyser = SemanticAnalyser(program, trace=False)

    with raises(SemanticError):
        analyser.analyse()


def test_function_scope_isolation():
    """Test that a function creates its own scope."""
    source = """
        $MEM-GC

        val mui8 x = 10.

        fc test()!mui8 {
        }
    """

    program = lex_and_parse(source)
    analyser = SemanticAnalyser(program, trace=False)
    analyser.analyse()

    func_symbol = analyser.global_scope.lookup("test")

    assert func_symbol.scope is not analyser.global_scope
    assert func_symbol.scope.parent is analyser.global_scope


# ============================================================================
# STRUCT DECLARATION TESTS
# ============================================================================


def test_struct_declaration():
    """Test analysis of sct declaration."""
    source = """
        $MEM-GC

        sct Point {
        }
    """

    program = lex_and_parse(source)
    analyser = SemanticAnalyser(program, trace=False)
    analyser.analyse()

    struct_symbol = analyser.global_scope.lookup("Point")

    assert struct_symbol is not None
    assert struct_symbol.kind == "struct"
    assert struct_symbol.type is None
    assert struct_symbol.scope is analyser.global_scope


def test_duplicate_struct_declarations():
    """Test that duplicate sct declarations raise SemanticError."""
    source = """
        $MEM-GC

        sct Point {
        }

        sct Point {
        }
    """

    program = lex_and_parse(source)
    analyser = SemanticAnalyser(program, trace=False)

    with raises(SemanticError):
        analyser.analyse()


# ============================================================================
# MIXED DECLARATION TESTS
# ============================================================================


def test_mixed_declarations():
    """Test analysis of mixed variable, function, and sct declarations."""
    source = """
        $MEM-GC

        val mui8 count = 0.

        fc get_count()!mui8 {
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


def test_duplicate_variable_and_struct():
    """Test that variable and sct with same name raises SemanticError."""
    source = """
        $MEM-GC

        val mui8 Item = 0.

        sct Item {
        }
    """

    program = lex_and_parse(source)
    analyser = SemanticAnalyser(program, trace=False)

    with raises(SemanticError):
        analyser.analyse()


# ============================================================================
# DIRECT DECLARATION TESTS
# ============================================================================


def test_define_variable_declaration():
    """Test that a variable declaration creates a variable symbol."""
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


def test_duplicate_variable_declaration():
    """Test that duplicate variable declarations raise SemanticError."""
    analyser = SemanticAnalyser(None, False)
    scope = SymbolTable()

    node = ast.DeclareVariable(
        identifier="foo",
        datatype=ast.Type("mui8"),
    )

    analyser.define_variable_declaration(node, scope)

    with raises(SemanticError):
        analyser.define_variable_declaration(node, scope)


def test_define_struct_declaration():
    """Test that a sct declaration creates a struct symbol."""
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


def test_duplicate_struct_declaration():
    """Test that duplicate sct declarations raise SemanticError."""
    analyser = SemanticAnalyser(None, False)
    scope = SymbolTable()

    node = ast.Struct(
        identifier="Foo",
        body=[],
    )

    analyser.define_struct_declaration(node, scope)

    with raises(SemanticError):
        analyser.define_struct_declaration(node, scope)


def test_define_function_declaration():
    """Test that a function declaration creates a function symbol."""
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


def test_function_has_own_scope():
    """Test that a function creates a child scope."""
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


def test_duplicate_function_declaration():
    """Test that duplicate function declarations raise SemanticError."""
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


# ============================================================================
# FIRST PASS TESTS
# ============================================================================


def test_first_pass_variable():
    """Test that the first pass processes variable declarations."""
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


def test_first_pass_struct():
    """Test that the first pass processes sct declarations."""
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


def test_first_pass_function():
    """Test that the first pass processes function declarations."""
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


def test_first_pass_multiple_declarations():
    """Test that the first pass processes multiple supported AST nodes."""
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


def test_first_pass_unknown_node():
    """Test that the first pass rejects an unsupported AST node."""
    tree = ast.Program(
        statements=[ast.Break()],
        memory_mode="manual",
    )

    analyser = SemanticAnalyser(tree, False)

    with raises(SemanticError):
        analyser.first_pass_symbol_table()


def test_first_pass_empty_ast():
    """Test that the first pass handles an empty program."""
    tree = ast.Program(
        statements=[],
        memory_mode="manual",
    )

    analyser = SemanticAnalyser(tree, False)
    analyser.first_pass_symbol_table()

    assert analyser.global_scope.symbols == {}


# ============================================================================
# FULL ANALYSIS TESTS
# ============================================================================


def test_analyse():
    """Test that analyse() builds the symbol table."""
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


def test_second_pass_type_check():
    """Test that the second pass completes successfully."""
    analyser = SemanticAnalyser(None, False)
    analyser.second_pass_type_check()


def test_analyse_empty_ast():
    """Test that analyse() successfully processes an empty program."""
    tree = ast.Program(
        statements=[],
        memory_mode="manual",
    )

    analyser = SemanticAnalyser(tree, False)
    analyser.analyse()

    assert analyser.global_scope.symbols == {}
