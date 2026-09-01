"""
Error handling and semantic error detection tests.

Tests cover:
- Semantic error messages
- Error detection in various scenarios
- Error recovery behavior
- Multiple errors in sequence
- Error reporting accuracy
"""

from pytest import raises

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
# SEMANTIC ERROR DETECTION
# ============================================================================


def test_semantic_error_raised_on_duplicate():
    """Test that SemanticError is raised for duplicate symbols."""
    table = SymbolTable()
    symbol1 = Symbol("var", "variable", "mui8", table)
    symbol2 = Symbol("var", "variable", "mstr", table)

    table.define(symbol1)

    with raises(SemanticError):
        table.define(symbol2)


def test_semantic_error_contains_symbol_info():
    """Test that SemanticError stores the node information."""
    table = SymbolTable()
    symbol1 = Symbol("var", "variable", "mui8", table)
    symbol2 = Symbol("var", "variable", "mstr", table)

    table.define(symbol1)

    try:
        table.define(symbol2)
        assert False, "Should have raised SemanticError"
    except SemanticError as e:
        assert e.node is not None


def test_semantic_error_message_format():
    """Test that SemanticError message contains useful information."""
    table = SymbolTable()
    symbol1 = Symbol("my_var", "variable", "mui8", table)
    symbol2 = Symbol("my_var", "variable", "mstr", table)

    table.define(symbol1)

    try:
        table.define(symbol2)
        assert False, "Should have raised SemanticError"
    except SemanticError as e:
        error_message = str(e)
        # Message should mention it's already declared
        assert (
            "already declared" in error_message.lower()
            or "duplicate" in error_message.lower()
        )


# ============================================================================
# DUPLICATE VARIABLE DETECTION
# ============================================================================


def test_duplicate_variable_error():
    """Test duplicate variable declaration is detected."""
    source = """
        $MEM-GC
        val mui8 x = 1.
        val mstr x = "dup".
    """

    with raises(SemanticError):
        analyse_program(source)


def test_duplicate_variables_different_positions():
    """Test duplicate variables at different positions."""
    source = """
        $MEM-GC
        val mui8 first = 1.
        val mstr second = "test".
        val cbln third = true.
        val mui8 first = 2.
    """

    with raises(SemanticError):
        analyse_program(source)


def test_duplicate_among_many_variables():
    """Test duplicate detection among many variables."""
    source = """
        $MEM-GC
        val mui8 a = 1.
        val mstr b = "b".
        val cbln c = true.
        val mf32 d = 1.5.
        val mf64 e = 2.5.
        val mchar f = "c".
        val maint g = 100.
        val mdml h = 3.14.
        val msi8 i = -1.
        val msi16 j = -100.
        val msi32 k = -1000.
        val msi64 l = -10000.
        val mui16 m = 100.
        val mui32 n = 1000.
        val mui64 o = 10000.
        val cstr p = "const".
        val cchar q = "a".
        val cbln r = false.
        val caint s = 200.
        val cdml t = 6.28.
        val cf32 u = 1.5.
        val cf64 v = 2.5.
        val csi8 w = -2.
        val csi16 x = -200.
        val csi32 y = -2000.
        val csi64 z = -20000.
        val cui8 a = 50.
    """

    with raises(SemanticError):
        analyse_program(source)


def test_variable_duplicate_with_itself():
    """Test that immediately redeclaring a variable raises error."""
    source = """
        $MEM-GC
        val mui8 x = 1.
        val mui8 x = 2.
    """

    with raises(SemanticError):
        analyse_program(source)


# ============================================================================
# DUPLICATE FUNCTION DETECTION
# ============================================================================


def test_duplicate_function_error():
    """Test duplicate function declaration is detected."""
    source = """
        $MEM-GC
        fc test()!mai8 {
        }
        fc test()!mstr {
        } """

    with raises(SemanticError):
        analyse_program(source)


def test_duplicate_functions_with_params():
    """Test duplicate function detection with parameters."""
    source = """
        $MEM-GC
        fc add(mui8 a, mui8 b)!mai8 {
        }
        fc add(mstr x, mstr y)!mstr {
        } """

    with raises(SemanticError):
        analyse_program(source)


def test_duplicate_function_after_many():
    """Test duplicate function after many declarations."""
    source = """
        $MEM-GC
        fc func1()!mai8 {}
        fc func2()!mai8 {}
        fc func3()!mai8 {}
        fc func4()!mai8 {}
        fc func5()!mai8 {}
        fc func1()!mai8 {} """

    with raises(SemanticError):
        analyse_program(source)


# ============================================================================
# DUPLICATE STRUCT DETECTION
# ============================================================================


def test_duplicate_struct_error():
    """Test duplicate sct declaration is detected."""
    source = """
        $MEM-GC
        sct Point {
        }
        sct Point {
        } """

    with raises(SemanticError):
        analyse_program(source)


def test_duplicate_structs_with_gap():
    """Test duplicate sct detection with other declarations in between."""
    source = """
        $MEM-GC
        sct Point {
        }
        val mui8 x = 1.
        fc test()!mai8 {}
        sct Point {
        } """

    with raises(SemanticError):
        analyse_program(source)


def test_duplicate_structs_many():
    """Test duplicate among many sct declarations."""
    source = """
        $MEM-GC
        sct A {}
        sct B {}
        sct C {}
        sct D {}
        sct E {}
        sct A {} """

    with raises(SemanticError):
        analyse_program(source)


# ============================================================================
# CROSS-KIND CONFLICT DETECTION
# ============================================================================


def test_variable_function_conflict():
    """Test that variable and function with same name conflict."""
    source = """
        $MEM-GC
        val mui8 item = 0.
        fc item()!mai8 {} """

    with raises(SemanticError):
        analyse_program(source)


def test_variable_struct_conflict():
    """Test that variable and sct with same name conflict."""
    source = """
        $MEM-GC
        val mui8 item = 0.
        sct item {} """

    with raises(SemanticError):
        analyse_program(source)


def test_function_struct_conflict():
    """Test that function and sct with same name conflict."""
    source = """
        $MEM-GC
        fc item()!mai8 {}
        sct item {} """

    with raises(SemanticError):
        analyse_program(source)


def test_struct_variable_conflict_reverse_order():
    """Test struct-then-variable conflict."""
    source = """
        $MEM-GC
        sct item {}
        val mui8 item = 0.
    """

    with raises(SemanticError):
        analyse_program(source)


def test_function_variable_conflict_reverse_order():
    """Test function-then-variable conflict."""
    source = """
        $MEM-GC
        fc item()!mai8 {}
        val mui8 item = 0.
    """

    with raises(SemanticError):
        analyse_program(source)


# ============================================================================
# ERROR PREVENTION TESTS
# ============================================================================


def test_similar_names_not_conflict():
    """Test that similar but different names don't conflict."""
    source = """
        $MEM-GC
        val mui8 var = 1.
        val mstr var_name = "test".
        val cbln var_count = true.
        fc var_process()!mai8 {}
        sct var_data {} """

    analyser = analyse_program(source)

    assert analyser.global_scope.lookup("var") is not None
    assert analyser.global_scope.lookup("var_name") is not None
    assert analyser.global_scope.lookup("var_count") is not None
    assert analyser.global_scope.lookup("var_process") is not None
    assert analyser.global_scope.lookup("var_data") is not None


def test_case_sensitive_identifiers():
    """Test that identifiers are case-sensitive."""
    source = """
        $MEM-GC
        val mui8 var = 1.
        val mstr Var = "test".
        val cbln VAR = true.
    """

    analyser = analyse_program(source)

    assert analyser.global_scope.lookup("var") is not None
    assert analyser.global_scope.lookup("Var") is not None
    assert analyser.global_scope.lookup("VAR") is not None
    assert len(analyser.global_scope.symbols) == 3


def test_underscore_variants():
    """Test that underscore variations don't conflict."""
    source = """
        $MEM-GC
        val mui8 my_var = 1.
        val mstr myvar = "test".
        val cbln my_var_name = true.
    """

    analyser = analyse_program(source)

    assert len(analyser.global_scope.symbols) == 3


# ============================================================================
# EARLY ERROR DETECTION
# ============================================================================


def test_error_stops_analysis():
    """Test that first error stops further analysis."""
    source = """
        $MEM-GC
        val mui8 x = 1.
        val mstr x = "dup1".
        val cbln x = true.
    """

    with raises(SemanticError):
        analyse_program(source)


def test_single_error_per_duplicate():
    """Test that duplicate raises exactly one error (not cascading)."""
    source = """
        $MEM-GC
        val mui8 x = 1.
        val mstr x = "dup".
    """

    error_count = 0
    try:
        analyse_program(source)
    except SemanticError:
        error_count += 1

    assert error_count == 1


# ============================================================================
# COMPREHENSIVE ERROR SCENARIOS
# ============================================================================


def test_mixed_conflicts_first_error():
    """Test that first conflict error is caught."""
    source = """
        $MEM-GC
        val mui8 a = 1.
        val mstr a = "dup".
        fc b()!mai8 {}
        sct b {} """

    with raises(SemanticError):
        analyse_program(source)


def test_all_declaration_types_no_error():
    """Test all declaration types together without errors."""
    source = """
        $MEM-GC
        val mui8 var1 = 1.
        fc func1()!mai8 {}
        sct Struct1 {}
        val mstr var2 = "test".
        fc func2()!cbln {}
        sct Struct2 {} """

    analyser = analyse_program(source)
    assert len(analyser.global_scope.symbols) == 6


def test_comprehensive_conflict_combinations():
    """Test various conflict combinations."""
    conflict_sources = [
        # Variable-function conflict
        """
        $MEM-GC
        val mui8 name = 1.
        fc name()!mai8 {} """,
        # Variable-sct conflict
        """
        $MEM-GC
        val mui8 name = 1.
        sct name {} """,
        # Function-sct conflict
        """
        $MEM-GC
        fc name()!mai8 {}
        sct name {} """,
        # Triple conflict
        """
        $MEM-GC
        val mui8 x = 1.
        fc x()!mai8 {}
        sct x {} """,
    ]

    for source in conflict_sources:
        with raises(SemanticError):
            analyse_program(source)
