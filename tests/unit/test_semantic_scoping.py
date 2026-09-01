import pytest

from teapot.lexer import Lexer
from teapot.parser import Parser
from teapot.semantic import SemanticAnalyser, SemanticError, Symbol, SymbolTable

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def lex_and_parse(source):
    """Helper to lex and parse source code."""
    lexer = Lexer(source)
    tokens = lexer.tokenise()
    parser = Parser(tokens)
    return parser.parse()


def analyse_program(source, trace=False):
    """Helper for full pipeline analysis."""
    program = lex_and_parse(source)
    analyser = SemanticAnalyser(program, trace)
    analyser.analyse()
    return analyser


# ============================================================================
# BASIC SCOPE TESTS
# ============================================================================


def test_empty_symbol_table():
    """Test that an empty symbol table has no symbols."""
    table = SymbolTable()

    assert len(table.symbols) == 0
    assert table.lookup("any_symbol") is None


def test_symbol_table_without_parent():
    """Test symbol table with no parent scope."""
    table = SymbolTable(parent=None)
    symbol = Symbol("var", "variable", "mui8", table)

    table.define(symbol)

    assert table.lookup("var") is symbol
    assert table.lookup("unknown") is None


def test_symbol_table_parent_chain():
    """Test that the parent chain is maintained correctly."""
    grandparent = SymbolTable()
    parent = SymbolTable(parent=grandparent)
    child = SymbolTable(parent=parent)

    assert child.parent is parent
    assert parent.parent is grandparent
    assert grandparent.parent is None


def test_lookup_stops_at_root():
    """Test that lookup stops at the root scope."""
    root = SymbolTable(parent=None)
    level1 = SymbolTable(parent=root)
    level2 = SymbolTable(parent=level1)

    root_symbol = Symbol("root_var", "variable", "mui8", root)
    root.define(root_symbol)

    assert level2.lookup("root_var") is root_symbol
    assert level2.lookup("nonexistent") is None


# ============================================================================
# SHADOWING TESTS
# ============================================================================


def test_simple_shadowing():
    """Test simple variable shadowing."""
    parent = SymbolTable()
    child = SymbolTable(parent=parent)

    parent_symbol = Symbol("x", "variable", "mui8", parent)
    child_symbol = Symbol("x", "variable", "mstr", child)

    parent.define(parent_symbol)
    child.define(child_symbol)

    assert parent.lookup("x") is parent_symbol
    assert child.lookup("x") is child_symbol


def test_shadowing_different_kinds():
    """Test shadowing with different symbol kinds."""
    parent = SymbolTable()
    child = SymbolTable(parent=parent)

    parent_func = Symbol("process", "function", "mai8", parent)
    parent.define(parent_func)

    child_var = Symbol("process", "variable", "mui8", child)
    child.define(child_var)

    assert parent.lookup("process").kind == "function"
    assert child.lookup("process").kind == "variable"


def test_multiple_levels_shadowing():
    """Test shadowing across multiple scope levels."""
    global_scope = SymbolTable()
    level1 = SymbolTable(parent=global_scope)
    level2 = SymbolTable(parent=level1)
    level3 = SymbolTable(parent=level2)

    for scope, type_name in [
        (global_scope, "mui8"),
        (level1, "mstr"),
        (level2, "cbln"),
        (level3, "mf32"),
    ]:
        symbol = Symbol("data", "variable", type_name, scope)
        scope.define(symbol)

    assert global_scope.lookup("data").type == "mui8"
    assert level1.lookup("data").type == "mstr"
    assert level2.lookup("data").type == "cbln"
    assert level3.lookup("data").type == "mf32"


def test_unshadowing_lookup():
    """Test that a shadowed parent symbol is hidden by the child symbol."""
    parent = SymbolTable()
    child = SymbolTable(parent=parent)

    parent_symbol = Symbol("x", "variable", "mui8", parent)
    parent.define(parent_symbol)

    assert child.lookup("x") is parent_symbol

    child_symbol = Symbol("x", "variable", "mstr", child)
    child.define(child_symbol)

    assert child.lookup("x") is child_symbol


# ============================================================================
# COMPLEX SCOPE HIERARCHY TESTS
# ============================================================================


def test_three_level_hierarchy():
    """Test three-level scope hierarchy."""
    root = SymbolTable()
    mid = SymbolTable(parent=root)
    leaf = SymbolTable(parent=mid)

    root_sym = Symbol("a", "variable", "mui8", root)
    mid_sym = Symbol("b", "variable", "mstr", mid)
    leaf_sym = Symbol("c", "variable", "cbln", leaf)

    root.define(root_sym)
    mid.define(mid_sym)
    leaf.define(leaf_sym)

    assert leaf.lookup("a") is root_sym
    assert leaf.lookup("b") is mid_sym
    assert leaf.lookup("c") is leaf_sym

    assert mid.lookup("a") is root_sym
    assert mid.lookup("b") is mid_sym
    assert mid.lookup("c") is None


def test_sibling_scopes_independent():
    """Test that sibling scopes cannot access each other."""
    parent = SymbolTable()
    child1 = SymbolTable(parent=parent)
    child2 = SymbolTable(parent=parent)

    child1_symbol = Symbol("x", "variable", "mui8", child1)
    child2_symbol = Symbol("y", "variable", "mstr", child2)

    child1.define(child1_symbol)
    child2.define(child2_symbol)

    assert child1.lookup("x") is child1_symbol
    assert child1.lookup("y") is None

    assert child2.lookup("y") is child2_symbol
    assert child2.lookup("x") is None


def test_cousin_scopes_independent():
    """Test that cousin scopes cannot access each other."""
    grandparent = SymbolTable()
    parent1 = SymbolTable(parent=grandparent)
    parent2 = SymbolTable(parent=grandparent)
    child1 = SymbolTable(parent=parent1)
    child2 = SymbolTable(parent=parent2)

    child1_symbol = Symbol("x", "variable", "mui8", child1)
    child2_symbol = Symbol("y", "variable", "mstr", child2)

    child1.define(child1_symbol)
    child2.define(child2_symbol)

    assert child1.lookup("x") is child1_symbol
    assert child1.lookup("y") is None

    assert child2.lookup("y") is child2_symbol
    assert child2.lookup("x") is None


# ============================================================================
# FUNCTION SCOPE TESTS
# ============================================================================


def test_function_creates_scope():
    """Test that function declaration creates a new scope."""
    source = """
        $MEM-GC
        val mui8 global_x = 1.
        fc my_func()!mai8 {
        }
    """

    analyser = analyse_program(source)

    func_symbol = analyser.global_scope.lookup("my_func")

    assert func_symbol is not None
    assert func_symbol.kind == "function"
    assert func_symbol.type == "mai8"
    assert func_symbol.scope is not analyser.global_scope
    assert func_symbol.scope.parent is analyser.global_scope


def test_function_scope_is_separate():
    """Test that a function has its own scope."""
    source = """
        $MEM-GC
        fc func1()!mai8 {
        }

        fc func2()!mai8 {
        }
    """

    analyser = analyse_program(source)

    func1 = analyser.global_scope.lookup("func1")
    func2 = analyser.global_scope.lookup("func2")

    assert func1.scope is not func2.scope
    assert func1.scope.parent is analyser.global_scope
    assert func2.scope.parent is analyser.global_scope


def test_function_accesses_global_symbols():
    """Test that a function scope can access global symbols."""
    source = """
        $MEM-GC
        val mui8 global_var = 10.

        fc test_func()!mai8 {
        }
    """

    analyser = analyse_program(source)

    global_var = analyser.global_scope.lookup("global_var")
    func = analyser.global_scope.lookup("test_func")

    assert func.scope.parent is analyser.global_scope
    assert func.scope.lookup("global_var") is global_var


# ============================================================================
# SYMBOL PROPERTIES
# ============================================================================


def test_symbol_name_preserved():
    """Test that a symbol preserves its name."""
    scope = SymbolTable()
    symbol = Symbol("my_variable", "variable", "mui8", scope)

    scope.define(symbol)

    assert symbol.name == "my_variable"
    assert scope.lookup("my_variable") is symbol


def test_symbol_type_preserved():
    """Test that a symbol preserves its type."""
    scope = SymbolTable()
    symbol = Symbol("x", "variable", "mf64", scope)

    scope.define(symbol)

    assert symbol.type == "mf64"
    assert scope.lookup("x").type == "mf64"


def test_symbol_kind_preserved():
    """Test that a symbol preserves its kind."""
    scope = SymbolTable()
    symbol = Symbol("process", "function", "mai8", scope)

    scope.define(symbol)

    assert symbol.kind == "function"
    assert scope.lookup("process").kind == "function"


def test_symbol_scope_preserved():
    """Test that a symbol stores the scope it belongs to."""
    scope = SymbolTable()
    symbol = Symbol("x", "variable", "mui8", scope)

    scope.define(symbol)

    assert symbol.scope is scope


def test_symbol_properties_across_scopes():
    """Test that symbol properties remain intact when accessed through a child."""
    parent = SymbolTable()
    child = SymbolTable(parent=parent)

    symbol = Symbol("process", "function", "mai8", parent)
    parent.define(symbol)

    found = child.lookup("process")

    assert found is symbol
    assert found.name == "process"
    assert found.kind == "function"
    assert found.type == "mai8"
    assert found.scope is parent


def test_struct_symbol_no_type():
    """Test that struct symbols can have no type."""
    parent = SymbolTable()

    struct_symbol = Symbol("Point", "struct", None, parent)
    parent.define(struct_symbol)

    found = parent.lookup("Point")

    assert found.type is None
    assert found.kind == "struct"
    assert found.name == "Point"
    assert found.scope is parent


# ============================================================================
# SCOPE ISOLATION TESTS
# ============================================================================


def test_scope_isolation_variable_declaration():
    """Test that variables are isolated to their function scopes."""
    source = """
        $MEM-GC

        fc func1()!mai8 {
            val mstr local1 = "test".
        }

        fc func2()!mai8 {
            val cbln local2 = true.
        }
    """

    analyser = analyse_program(source)

    func1 = analyser.global_scope.lookup("func1")
    func2 = analyser.global_scope.lookup("func2")

    assert func1.scope is not func2.scope
    assert func1.scope.parent is analyser.global_scope
    assert func2.scope.parent is analyser.global_scope

    assert func1.scope.lookup("local1") is not None
    assert func1.scope.lookup("local2") is None

    assert func2.scope.lookup("local2") is not None
    assert func2.scope.lookup("local1") is None


def test_global_visibility():
    """Test that global symbols are visible to all child scopes."""
    parent = SymbolTable()
    child1 = SymbolTable(parent=parent)
    child2 = SymbolTable(parent=parent)
    grandchild = SymbolTable(parent=child1)

    global_symbol = Symbol("global", "variable", "mui8", parent)
    parent.define(global_symbol)

    assert child1.lookup("global") is global_symbol
    assert child2.lookup("global") is global_symbol
    assert grandchild.lookup("global") is global_symbol


def test_local_isolation():
    """Test that local symbols are not visible to sibling scopes."""
    parent = SymbolTable()
    child1 = SymbolTable(parent=parent)
    child2 = SymbolTable(parent=parent)

    local1 = Symbol("local", "variable", "mui8", child1)
    child1.define(local1)

    assert child1.lookup("local") is local1
    assert child2.lookup("local") is None


# ============================================================================
# ERROR SCENARIOS
# ============================================================================


def test_duplicate_in_parent_and_child():
    """Test that local shadowing of a parent symbol is allowed."""
    source = """
        $MEM-GC
        val mui8 x = 1.

        fc test()!mai8 {
            val mstr x = "dup".
        }
    """

    analyser = analyse_program(source)

    global_x = analyser.global_scope.lookup("x")
    func = analyser.global_scope.lookup("test")

    assert global_x is not None
    assert func.scope.lookup("x") is not None
    assert func.scope.lookup("x") is not global_x


def test_multiple_duplicates_in_sequence():
    """Test that duplicate declarations in the same scope raise an error."""
    source = """
        $MEM-GC
        val mui8 a = 1.
        val mstr a = "dup1".
        val cbln a = true.
    """

    with pytest.raises(SemanticError):
        analyse_program(source)


def test_conflict_after_many_declarations():
    """Test duplicate declaration after several successful declarations."""
    source = """
        $MEM-GC
        val mui8 v1 = 1.
        val mui8 v2 = 2.
        val mui8 v3 = 3.
        val mui8 v4 = 4.
        val mui8 v5 = 5.
        val mui8 v1 = 10.
    """

    with pytest.raises(SemanticError):
        analyse_program(source)
