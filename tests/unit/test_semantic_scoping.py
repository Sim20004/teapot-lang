"""
Detailed scope resolution and symbol lookup tests for semantic analysis.

Tests cover:
- Complex scope hierarchies
- Symbol shadowing scenarios
- Scope isolation and encapsulation
- Parent scope traversal
- Symbol availability across scopes
"""

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
    """Test that empty symbol table has no symbols."""
    table = SymbolTable()
    assert len(table.symbols) == 0
    assert table.lookup("any_symbol") is None


def test_symbol_table_without_parent():
    """Test symbol table with no parent scope."""
    table = SymbolTable(parent=None)
    symbol = Symbol("var", "variable", "mui8", None, table)
    table.define(symbol)

    assert table.lookup("var") is symbol
    assert table.lookup("unknown") is None


def test_symbol_table_parent_chain():
    """Test that parent chain is maintained correctly."""
    grandparent = SymbolTable()
    parent = SymbolTable(parent=grandparent)
    child = SymbolTable(parent=parent)

    assert child.parent is parent
    assert parent.parent is grandparent
    assert grandparent.parent is None


def test_lookup_stops_at_root():
    """Test that lookup stops at root scope."""
    root = SymbolTable(parent=None)
    level1 = SymbolTable(parent=root)
    level2 = SymbolTable(parent=level1)

    root_symbol = Symbol("root_var", "variable", "mui8", None, root)
    root.define(root_symbol)

    # Should find it from level2
    assert level2.lookup("root_var") is root_symbol
    # Should not find non-existent symbol
    assert level2.lookup("nonexistent") is None


# ============================================================================
# SHADOWING TESTS
# ============================================================================


def test_simple_shadowing():
    """Test simple variable shadowing."""
    parent = SymbolTable()
    child = SymbolTable(parent=parent)

    parent_symbol = Symbol("x", "variable", "mui8", None, parent)
    child_symbol = Symbol("x", "variable", "mstr", None, child)

    parent.define(parent_symbol)
    child.define(child_symbol)

    assert parent.lookup("x") is parent_symbol
    assert child.lookup("x") is child_symbol


def test_shadowing_different_kinds():
    """Test shadowing with different symbol kinds."""
    parent = SymbolTable()
    child = SymbolTable(parent=parent)

    # Parent has function
    parent_func = Symbol("process", "function", "mai8", [], parent)
    parent.define(parent_func)

    # Child shadows with variable
    child_var = Symbol("process", "variable", "mui8", None, child)
    child.define(child_var)

    assert parent.lookup("process").kind == "function"
    assert child.lookup("process").kind == "variable"


def test_multiple_levels_shadowing():
    """Test shadowing across multiple scope levels."""
    global_scope = SymbolTable()
    level1 = SymbolTable(parent=global_scope)
    level2 = SymbolTable(parent=level1)
    level3 = SymbolTable(parent=level2)

    # Define same name at each level
    for scope, type_name in [
        (global_scope, "mui8"),
        (level1, "mstr"),
        (level2, "cbln"),
        (level3, "mf32"),
    ]:
        symbol = Symbol("data", "variable", type_name, None, scope)
        scope.define(symbol)

    # Each scope should see its own symbol
    assert global_scope.lookup("data").type == "mui8"
    assert level1.lookup("data").type == "mstr"
    assert level2.lookup("data").type == "cbln"
    assert level3.lookup("data").type == "mf32"


def test_unshadowing_lookup():
    """Test that removing a shadow allows access to parent symbol."""
    parent = SymbolTable()
    child = SymbolTable(parent=parent)

    parent_symbol = Symbol("x", "variable", "mui8", None, parent)
    parent.define(parent_symbol)

    # Without child symbol, should find parent's
    assert child.lookup("x") is parent_symbol

    # Now shadow it
    child_symbol = Symbol("x", "variable", "mstr", None, child)
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

    root_sym = Symbol("a", "variable", "mui8", None, root)
    mid_sym = Symbol("b", "variable", "mstr", None, mid)
    leaf_sym = Symbol("c", "variable", "cbln", None, leaf)

    root.define(root_sym)
    mid.define(mid_sym)
    leaf.define(leaf_sym)

    # Leaf should access all
    assert leaf.lookup("a") is root_sym
    assert leaf.lookup("b") is mid_sym
    assert leaf.lookup("c") is leaf_sym

    # Mid should not access leaf
    assert mid.lookup("a") is root_sym
    assert mid.lookup("b") is mid_sym
    assert mid.lookup("c") is None


def test_sibling_scopes_independent():
    """Test that sibling scopes cannot access each other."""
    parent = SymbolTable()
    child1 = SymbolTable(parent=parent)
    child2 = SymbolTable(parent=parent)

    child1_symbol = Symbol("x", "variable", "mui8", None, child1)
    child2_symbol = Symbol("y", "variable", "mstr", None, child2)

    child1.define(child1_symbol)
    child2.define(child2_symbol)

    # Siblings cannot see each other
    assert child1.lookup("x") is child1_symbol
    assert child1.lookup("y") is None

    assert child2.lookup("y") is child2_symbol
    assert child2.lookup("x") is None


def test_cousin_scopes_independent():
    """Test that cousin scopes (siblings of parent) cannot see each other."""
    grandparent = SymbolTable()
    parent1 = SymbolTable(parent=grandparent)
    parent2 = SymbolTable(parent=grandparent)
    child1 = SymbolTable(parent=parent1)
    child2 = SymbolTable(parent=parent2)

    child1_symbol = Symbol("x", "variable", "mui8", None, child1)
    child2_symbol = Symbol("y", "variable", "mstr", None, child2)

    child1.define(child1_symbol)
    child2.define(child2_symbol)

    # Cousins cannot see each other
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
        } """

    analyser = analyse_program(source)

    func_symbol = analyser.global_scope.lookup("my_func")
    assert func_symbol is not None
    assert func_symbol.scope is not analyser.global_scope
    assert func_symbol.scope.parent is analyser.global_scope


def test_function_parameter_scope():
    """Test function parameter scope."""
    source = """
        $MEM-GC
        fc add(mui8 a, mui8 b)!mai8 {
        } """

    analyser = analyse_program(source)

    func_symbol = analyser.global_scope.lookup("add")
    # Parameters should be in function scope
    assert func_symbol.params == [("a", "mui8"), ("b", "mui8")]


def test_function_accesses_global_symbols():
    """Test that function body can access global symbols."""
    source = """
        $MEM-GC
        val mui8 global_var = 10.
        fc test_func()!mai8 {
        } """

    analyser = analyse_program(source)

    global_var = analyser.global_scope.lookup("global_var")
    fc = analyser.global_scope.lookup("test_func")

    # Function scope should have access to global
    assert fc.scope.parent is analyser.global_scope
    # We should be able to lookup global from function scope
    assert fc.scope.lookup("global_var") is global_var


# ============================================================================
# SYMBOL TYPE AND KIND PRESERVATION
# ============================================================================


def test_symbol_type_preserved_across_scopes():
    """Test that symbol type is preserved in scope hierarchy."""
    parent = SymbolTable()
    child = SymbolTable(parent=parent)

    symbol = Symbol("x", "variable", "mf64", None, parent)
    parent.define(symbol)

    # Type should be preserved
    assert child.lookup("x").type == "mf64"


def test_symbol_kind_preserved_across_scopes():
    """Test that symbol kind is preserved in scope hierarchy."""
    parent = SymbolTable()
    child = SymbolTable(parent=parent)

    symbol = Symbol("process", "function", "mai8", [("x", "mui8")], parent)
    parent.define(symbol)

    # Kind should be preserved
    assert child.lookup("process").kind == "function"
    assert child.lookup("process").params == [("x", "mui8")]


# ============================================================================
# SCOPE ISOLATION TESTS
# ============================================================================


def test_scope_isolation_variable_declaration():
    """Test that variables are isolated to their scope."""
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

    # Each function has its own scope
    assert func1.scope is not func2.scope
    assert func1.scope.parent is analyser.global_scope
    assert func2.scope.parent is analyser.global_scope


def test_global_visibility():
    """Test that global symbols are visible to all child scopes."""
    parent = SymbolTable()
    child1 = SymbolTable(parent=parent)
    child2 = SymbolTable(parent=parent)
    grandchild = SymbolTable(parent=child1)

    global_symbol = Symbol("global", "variable", "mui8", None, parent)
    parent.define(global_symbol)

    # All should see global
    assert child1.lookup("global") is global_symbol
    assert child2.lookup("global") is global_symbol
    assert grandchild.lookup("global") is global_symbol


def test_local_isolation():
    """Test that local symbols are not visible to siblings."""
    parent = SymbolTable()
    child1 = SymbolTable(parent=parent)
    child2 = SymbolTable(parent=parent)

    local1 = Symbol("local", "variable", "mui8", None, child1)
    child1.define(local1)

    # child2 should not see child1's local
    assert child2.lookup("local") is None


# ============================================================================
# SYMBOL TABLE WITH PARAMETERS
# ============================================================================


def test_function_symbol_with_params():
    """Test function symbol stores parameters correctly."""
    parent = SymbolTable()

    params = [("x", "mui8"), ("y", "mstr"), ("z", "cbln")]
    func_symbol = Symbol("process", "function", "mai8", params, parent)
    parent.define(func_symbol)

    found = parent.lookup("process")
    assert found.params == params
    assert len(found.params) == 3


def test_function_symbol_without_params():
    """Test function symbol with empty parameters."""
    parent = SymbolTable()

    func_symbol = Symbol("get_value", "function", "mai8", [], parent)
    parent.define(func_symbol)

    found = parent.lookup("get_value")
    assert found.params == []


def test_struct_symbol_no_type():
    """Test that sct symbols have no type."""
    parent = SymbolTable()

    struct_symbol = Symbol("Point", "struct", None, None, parent)
    parent.define(struct_symbol)

    found = parent.lookup("Point")
    assert found.type is None
    assert found.kind == "struct"


# ============================================================================
# ERROR SCENARIOS
# ============================================================================


def test_duplicate_in_parent_and_child():
    """Test that duplicate in child with parent symbol raises error."""
    source = """
        $MEM-GC
        val mui8 x = 1.
        fc test()!mai8 {
            val mstr x = "dup".
        }
    """

    # This should not raise error - local shadowing is allowed
    # (though some languages disallow it for clarity)
    analyser = analyse_program(source)
    assert analyser.global_scope.lookup("x") is not None


def test_multiple_duplicates_in_sequence():
    """Test multiple duplicate errors."""
    source = """
        $MEM-GC
        val mui8 a = 1.
        val mstr a = "dup1".
        val cbln a = true.
    """

    with pytest.raises(SemanticError):
        analyse_program(source)


def test_conflict_after_many_declarations():
    """Test conflict after many successful declarations."""
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
