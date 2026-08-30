"""
Comprehensive integration test suite for the Teapot compiler pipeline.

Tests cover end-to-end scenarios from lexing through semantic analysis:
- Basic programs with various memory modes
- Variable declarations and scoping
- Function declarations and scope hierarchy
- Struct declarations
- Complex nested scopes
- Error handling through the pipeline
- Mixed declaration types
"""

from pytest import raises

from teapot.lexer import Lexer
from teapot.parser import Parser
from teapot.semantic import SemanticAnalyser, SemanticError

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def compile_to_ast(source):
    """Helper: Lex and parse source code to AST."""
    lexer = Lexer(source)
    tokens = lexer.tokenise()
    parser = Parser(tokens)
    return parser.parse()


def analyse_program(source, trace=False):
    """Helper: Full pipeline from source to semantic analysis."""
    ast_tree = compile_to_ast(source)
    analyser = SemanticAnalyser(ast_tree, trace)
    analyser.analyse()
    return analyser


# ============================================================================
# BASIC PROGRAM TESTS
# ============================================================================


def test_basic_program_memory_gc():
    """Test basic program with garbage collection memory mode."""
    source = """
        $MEM-GC

        val mui8 foo = 8.
        val cstr bar = "baz".
    """

    analyser = analyse_program(source)

    assert analyser.ast_tree.memory_mode == "$MEM-GC"
    assert len(analyser.ast_tree.statements) == 2

    foo = analyser.global_scope.lookup("foo")
    bar = analyser.global_scope.lookup("bar")

    assert foo is not None
    assert foo.kind == "variable"
    assert foo.type == "mui8"

    assert bar is not None
    assert bar.kind == "variable"
    assert bar.type == "cstr"


def test_basic_program_memory_manual():
    """Test basic program with manual memory mode."""
    source = """
        $MEM-MANUAL

        val mui8 count = 0.
    """

    analyser = analyse_program(source)

    assert analyser.ast_tree.memory_mode == "$MEM-MANUAL"
    count = analyser.global_scope.lookup("count")
    assert count is not None


def test_empty_program():
    """Test empty program with just memory directive."""
    source = """
        $MEM-GC
    """

    analyser = analyse_program(source)

    assert analyser.ast_tree.memory_mode == "$MEM-GC"
    assert len(analyser.ast_tree.statements) == 0
    assert len(analyser.global_scope.symbols) == 0


# ============================================================================
# VARIABLE DECLARATION TESTS
# ============================================================================


def test_single_variable_declaration():
    """Test analysis of single variable."""
    source = """
        $MEM-GC
        val mui8 x = 42.
    """

    analyser = analyse_program(source)

    x = analyser.global_scope.lookup("x")
    assert x is not None
    assert x.name == "x"
    assert x.kind == "variable"
    assert x.type == "mui8"


def test_multiple_variable_declarations():
    """Test analysis of multiple variables in global scope."""
    source = """
        $MEM-GC
        val mui8 a = 1.
        val mstr b = "hello".
        val cbln c = true.
        val mf32 d = 3.14.
    """

    analyser = analyse_program(source)

    a = analyser.global_scope.lookup("a")
    b = analyser.global_scope.lookup("b")
    c = analyser.global_scope.lookup("c")
    d = analyser.global_scope.lookup("d")

    assert a.type == "mui8"
    assert b.type == "mstr"
    assert c.type == "cbln"
    assert d.type == "mf32"
    assert len(analyser.global_scope.symbols) == 4


def test_variable_declaration_all_types():
    """Test variable declarations with all supported types."""
    types = [
        ("mui8", "mui8"),
        ("mui16", "mui16"),
        ("mui32", "mui32"),
        ("mui64", "mui64"),
        ("msi8", "msi8"),
        ("msi16", "msi16"),
        ("msi32", "msi32"),
        ("msi64", "msi64"),
        ("mstr", "mstr"),
        ("mchar", "mchar"),
        ("mbln", "mbln"),
        ("mf32", "mf32"),
        ("mf64", "mf64"),
        ("cui8", "cui8"),
        ("cbln", "cbln"),
        ("cstr", "cstr"),
    ]

    source_lines = ["$MEM-GC"]
    for i, (type_name, expected_type) in enumerate(types):
        var_name = f"v{i}"
        source_lines.append(f"val {type_name} {var_name} = 0.")

    source = "\n".join(source_lines)
    analyser = analyse_program(source)

    for i, (_, expected_type) in enumerate(types):
        var_name = f"v{i}"
        symbol = analyser.global_scope.lookup(var_name)
        assert symbol is not None
        assert symbol.type == expected_type


def test_duplicate_variable_declaration_error():
    """Test that duplicate variable declarations raise SemanticError."""
    source = """
        $MEM-GC
        val mui8 x = 1.
        val mstr x = "test".
    """

    with raises(SemanticError):
        analyse_program(source)


def test_variable_shadowing_not_allowed_same_scope():
    """Test that shadowing in the same scope raises error."""
    source = """
        $MEM-GC
        val mui8 var = 1.
        val mstr var = "test".
    """

    with raises(SemanticError):
        analyse_program(source)


# ============================================================================
# FUNCTION DECLARATION TESTS
# ============================================================================


def test_function_declaration_no_params():
    """Test function declaration with no parameters."""
    source = """
        $MEM-GC
        fc get_answer()!mai8 {
        } """

    analyser = analyse_program(source)

    fc = analyser.global_scope.lookup("get_answer")
    assert fc is not None
    assert fc.kind == "function"
    assert fc.type == "mai8"
    assert fc.params == []


def test_function_declaration_with_params():
    """Test function declaration with parameters."""
    source = """
        $MEM-GC
        fc add(mui8 a, mui8 b)!mui8 {
        } """

    analyser = analyse_program(source)

    add_func = analyser.global_scope.lookup("add")
    assert add_func is not None
    assert add_func.kind == "function"
    assert add_func.type == "mui8"
    assert len(add_func.params) == 2


def test_function_declaration_multiple():
    """Test multiple function declarations."""
    source = """
        $MEM-GC
        fc func_a()!mai8 {
        }
        fc func_b(mui8 x)!mstr {
        }
        fc func_c(mstr a, mstr b)!cbln {
        } """

    analyser = analyse_program(source)

    func_a = analyser.global_scope.lookup("func_a")
    func_b = analyser.global_scope.lookup("func_b")
    func_c = analyser.global_scope.lookup("func_c")

    assert func_a is not None
    assert func_b is not None
    assert func_c is not None
    assert len(analyser.global_scope.symbols) == 3


def test_duplicate_function_declaration_error():
    """Test that duplicate function declarations raise SemanticError."""
    source = """
        $MEM-GC
        fc get_value()!mai8 {
        }
        fc get_value()!mstr {
        } """

    with raises(SemanticError):
        analyse_program(source)


def test_function_with_many_parameters():
    """Test function with many parameters."""
    source = """
        $MEM-GC
        fc process(mui8 a, mstr b, cbln c, mf32 d, mf64 e, mchar f)!mai8 {
        } """

    analyser = analyse_program(source)

    process_func = analyser.global_scope.lookup("process")
    assert process_func is not None
    assert len(process_func.params) == 6


# ============================================================================
# STRUCT DECLARATION TESTS
# ============================================================================


def test_struct_declaration_simple():
    """Test simple sct declaration."""
    source = """
        $MEM-GC
        sct Point {
        } """

    analyser = analyse_program(source)

    point = analyser.global_scope.lookup("Point")
    assert point is not None
    assert point.kind == "struct"
    assert point.type is None


def test_struct_declaration_multiple():
    """Test multiple sct declarations."""
    source = """
        $MEM-GC
        sct Point {
        }
        sct Rectangle {
        }
        sct Circle {
        } """

    analyser = analyse_program(source)

    point = analyser.global_scope.lookup("Point")
    rectangle = analyser.global_scope.lookup("Rectangle")
    circle = analyser.global_scope.lookup("Circle")

    assert point is not None
    assert rectangle is not None
    assert circle is not None
    assert len(analyser.global_scope.symbols) == 3


def test_duplicate_struct_declaration_error():
    """Test that duplicate sct declarations raise SemanticError."""
    source = """
        $MEM-GC
        sct Point {
        }
        sct Point {
        } """

    with raises(SemanticError):
        analyse_program(source)


# ============================================================================
# MIXED DECLARATION TESTS
# ============================================================================


def test_mixed_declarations_global_scope():
    """Test mixed variables, functions, and structs in global scope."""
    source = """
        $MEM-GC
        val mui8 count = 0.
        fc get_count()!mai8 {
        }
        sct Result {
        }
        val mstr status = "ready".
        fc is_ready()!cbln {
        } """

    analyser = analyse_program(source)

    count = analyser.global_scope.lookup("count")
    get_count = analyser.global_scope.lookup("get_count")
    result = analyser.global_scope.lookup("Result")
    status = analyser.global_scope.lookup("status")
    is_ready = analyser.global_scope.lookup("is_ready")

    assert count.kind == "variable"
    assert get_count.kind == "function"
    assert result.kind == "struct"
    assert status.kind == "variable"
    assert is_ready.kind == "function"
    assert len(analyser.global_scope.symbols) == 5


def test_conflicts_variable_and_function():
    """Test that variable and function with same name raises error."""
    source = """
        $MEM-GC
        val mui8 item = 0.
        fc item()!mai8 {
        } """

    with raises(SemanticError):
        analyse_program(source)


def test_conflicts_variable_and_struct():
    """Test that variable and sct with same name raises error."""
    source = """
        $MEM-GC
        val mui8 item = 0.
        sct item {
        } """

    with raises(SemanticError):
        analyse_program(source)


def test_conflicts_function_and_struct():
    """Test that function and sct with same name raises error."""
    source = """
        $MEM-GC
        fc item()!mai8 {
        }
        sct item {
        } """

    with raises(SemanticError):
        analyse_program(source)


# ============================================================================
# SCOPE HIERARCHY TESTS
# ============================================================================


def test_function_creates_new_scope():
    """Test that function creates a new scope."""
    source = """
        $MEM-GC
        val mui8 global_var = 10.
        fc test_func()!mai8 {
        } """

    analyser = analyse_program(source)

    test_func = analyser.global_scope.lookup("test_func")

    assert test_func.scope is not analyser.global_scope
    # Function scope should have access to global scope
    assert test_func.scope.parent is analyser.global_scope


def test_function_parameter_in_scope():
    """Test that function parameters are accessible in function scope."""
    source = """
        $MEM-GC
        fc add(mui8 a, mui8 b)!mui8 {
        } """

    analyser = analyse_program(source)

    add_func = analyser.global_scope.lookup("add")
    # Parameters should be defined in function scope
    assert add_func.scope is not None
    assert len(add_func.params) == 2


def test_nested_function_scope():
    """Test nested function scope hierarchy."""
    source = """
        $MEM-GC
        val mui8 outer_var = 1.
        fc outer_func()!mai8 {
            val mstr inner_var = "test".
        }
    """

    analyser = analyse_program(source)

    outer_func = analyser.global_scope.lookup("outer_func")
    assert outer_func is not None
    # The function has its own scope
    assert outer_func.scope.parent is analyser.global_scope


# ============================================================================
# COMPLEX SCENARIOS
# ============================================================================


def test_comprehensive_program():
    """Test a comprehensive program with multiple declaration types."""
    source = """
        $MEM-GC
        
        sct Config {
        }
        val mui8 version = 1.
        val mstr name = "MyApp".
        
        fc initialize()!cbln {
        }
        fc get_config()!mstr {
        }
        sct State {
        }
        val cbln initialized = false.
        
        fc main()!mai8 {
        } """

    analyser = analyse_program(source)

    symbols = {
        "Config": analyser.global_scope.lookup("Config"),
        "version": analyser.global_scope.lookup("version"),
        "name": analyser.global_scope.lookup("name"),
        "initialize": analyser.global_scope.lookup("initialize"),
        "get_config": analyser.global_scope.lookup("get_config"),
        "State": analyser.global_scope.lookup("State"),
        "initialized": analyser.global_scope.lookup("initialized"),
        "main": analyser.global_scope.lookup("main"),
    }

    # Verify all symbols exist
    for name, symbol in symbols.items():
        assert symbol is not None, f"Symbol '{name}' not found"

    # Verify kinds
    assert symbols["Config"].kind == "struct"
    assert symbols["version"].kind == "variable"
    assert symbols["initialize"].kind == "function"

    assert len(analyser.global_scope.symbols) == 8


def test_large_number_of_declarations():
    """Test program with many declarations."""
    source_lines = ["$MEM-GC"]

    # Add 20 variables
    for i in range(20):
        source_lines.append(f"val mui8 var{i} = {i}.")

    # Add 10 functions
    for i in range(10):
        source_lines.append(f"fc func{i}()!mai8 {{}}")

    # Add 5 structs
    for i in range(5):
        source_lines.append(f"sct Struct{i} {{}}")

    source = "\n".join(source_lines)
    analyser = analyse_program(source)

    assert len(analyser.global_scope.symbols) == 35

    # Verify samples
    assert analyser.global_scope.lookup("var0") is not None
    assert analyser.global_scope.lookup("var19") is not None
    assert analyser.global_scope.lookup("func0") is not None
    assert analyser.global_scope.lookup("func9") is not None
    assert analyser.global_scope.lookup("Struct0") is not None
    assert analyser.global_scope.lookup("Struct4") is not None


def test_multiple_declarations_same_type():
    """Test multiple declarations of the same kind."""
    source = """
        $MEM-GC
        
        val mui8 a = 1.
        val mui8 b = 2.
        val mui8 c = 3.
        val mui8 d = 4.
        
        fc func_a()!mai8 {}
        fc func_b()!mai8 {}
        fc func_c()!mai8 {}
        sct Point {}
        sct Rectangle {}
        sct Circle {} """

    analyser = analyse_program(source)

    variables = [analyser.global_scope.lookup(name) for name in ["a", "b", "c", "d"]]
    functions = [
        analyser.global_scope.lookup(name) for name in ["func_a", "func_b", "func_c"]
    ]
    structs = [
        analyser.global_scope.lookup(name) for name in ["Point", "Rectangle", "Circle"]
    ]

    assert all(v is not None and v.kind == "variable" for v in variables)
    assert all(f is not None and f.kind == "function" for f in functions)
    assert all(s is not None and s.kind == "struct" for s in structs)


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================


def test_error_message_on_duplicate():
    """Test that SemanticError is raised with duplicate names."""
    source = """
        $MEM-GC
        val mui8 x = 1.
        val mstr x = "duplicate".
    """

    with raises(SemanticError):
        analyse_program(source)


def test_error_at_different_positions():
    """Test errors at different positions in the file."""
    source = """
        $MEM-GC
        val mui8 a = 1.
        val mstr b = "test".
        val cbln c = true.
        val mui8 a = 2.
    """

    with raises(SemanticError):
        analyse_program(source)


def test_multiple_variables_then_duplicate():
    """Test duplicate after several successful declarations."""
    source = """
        $MEM-GC
        val mui8 a = 1.
        val mstr b = "test".
        val cbln c = true.
        val mf32 d = 1.5.
        val mf64 e = 2.5.
        val mui8 a = 10.
    """

    with raises(SemanticError):
        analyse_program(source)


# ============================================================================
# EDGE CASES
# ============================================================================


def test_single_statement_program():
    """Test program with single variable declaration."""
    source = """
        $MEM-GC
        val mui8 x = 42.
    """

    analyser = analyse_program(source)
    assert len(analyser.global_scope.symbols) == 1


def test_function_with_no_body_statements():
    """Test function with empty body."""
    source = """
        $MEM-GC
        fc empty_func()!mai8 {
        } """

    analyser = analyse_program(source)

    fc = analyser.global_scope.lookup("empty_func")
    assert fc is not None
    assert fc.kind == "function"


def test_struct_with_empty_body():
    """Test sct with empty body."""
    source = """
        $MEM-GC
        sct Empty {
        } """

    analyser = analyse_program(source)

    sct = analyser.global_scope.lookup("Empty")
    assert sct is not None
    assert sct.kind == "struct"


def test_long_identifier_names():
    """Test declarations with long identifier names."""
    source = """
        $MEM-GC
        val mui8 this_is_a_very_long_variable_name_for_testing = 42.
        fc this_is_a_very_long_function_name_for_testing()!mai8 {}
        sct ThisIsAVeryLongStructNameForTesting {} """

    analyser = analyse_program(source)

    assert (
        analyser.global_scope.lookup("this_is_a_very_long_variable_name_for_testing")
        is not None
    )
    assert (
        analyser.global_scope.lookup("this_is_a_very_long_function_name_for_testing")
        is not None
    )
    assert (
        analyser.global_scope.lookup("ThisIsAVeryLongStructNameForTesting") is not None
    )
