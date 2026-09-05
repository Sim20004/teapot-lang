from pytest import raises

from teapot.lexer import Lexer
from teapot.parser import Parser
from teapot.semantic import SemanticAnalyser, SemanticError

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


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


# =============================================================================
# NESTED SCOPE TESTS
# =============================================================================


def test_deeply_nested_functions():
    """Test multiple nested function declarations."""

    source = """

        $MEM-GC

        fc outer()!mai8 {

            fc middle()!mai8 {

                fc inner()!mai8 {

                }

            }

        }

    """

    analyser = analyse_program(source)

    outer = analyser.global_scope.lookup("outer")

    assert outer is not None
    assert outer.kind == "function"

    outer_scope = outer.child_scope

    assert outer_scope is not None
    assert outer_scope.parent is analyser.global_scope

    middle = outer_scope.lookup("middle")

    assert middle is not None
    assert middle.kind == "function"
    assert middle.scope is outer_scope

    middle_scope = middle.child_scope

    assert middle_scope is not None
    assert middle_scope.parent is outer_scope

    inner = middle_scope.lookup("inner")

    assert inner is not None
    assert inner.kind == "function"
    assert inner.scope is middle_scope

    inner_scope = inner.child_scope

    assert inner_scope is not None
    assert inner_scope.parent is middle_scope


def test_mixed_declarations_in_function():
    """Test mixed declarations within function bodies."""

    source = """

        $MEM-GC

        val mui8 global_x = 1.

        fc main()!mai8 {

            val mstr local_s = "test".

            fc helper()!mai8 {

            }

            sct Local {}

        }

    """

    analyser = analyse_program(source)

    # Global scope should contain main and global_x.
    assert analyser.global_scope.lookup("global_x") is not None

    main = analyser.global_scope.lookup("main")

    assert main is not None
    assert main.kind == "function"
    assert main.scope is analyser.global_scope

    main_scope = main.child_scope

    assert main_scope is not None
    assert main_scope.parent is analyser.global_scope

    # The local variable belongs to the function scope.
    local_s = main_scope.lookup("local_s")

    assert local_s is not None
    assert local_s.kind == "variable"
    assert local_s.scope is main_scope

    # The nested function belongs to the function scope.
    helper = main_scope.lookup("helper")

    assert helper is not None
    assert helper.kind == "function"
    assert helper.scope is main_scope
    assert helper.child_scope is not None
    assert helper.child_scope.parent is main_scope

    # The nested struct belongs to the function scope.
    local_struct = main_scope.lookup("Local")

    assert local_struct is not None
    assert local_struct.kind == "struct"
    assert local_struct.scope is main_scope
    assert local_struct.child_scope is not None
    assert local_struct.child_scope.parent is main_scope


def test_function_scope_chain():
    """Test that function scope chains are maintained correctly."""

    source = """

        $MEM-GC

        val mui8 g = 1.

        fc f1()!mai8 {

            val mstr v1 = "test".

        }

    """

    analyser = analyse_program(source)

    f1 = analyser.global_scope.lookup("f1")

    assert f1 is not None
    assert f1.kind == "function"

    # The function symbol itself is declared in the global scope.
    assert f1.scope is analyser.global_scope

    # Its body has a separate child scope.
    function_scope = f1.child_scope

    assert function_scope is not None
    assert function_scope is not analyser.global_scope
    assert function_scope.parent is analyser.global_scope

    # The function can access global symbols.
    global_symbol = analyser.global_scope.lookup("g")

    assert global_symbol is not None
    assert function_scope.lookup("g") is global_symbol

    # Local variables belong to the function scope.
    v1 = function_scope.lookup("v1")

    assert v1 is not None
    assert v1.kind == "variable"
    assert v1.scope is function_scope


# =============================================================================
# SYMBOL COUNT AND CAPACITY TESTS
# =============================================================================


def test_100_variables_no_duplicates():
    """Test program with 100 variables without duplicates."""

    source_lines = ["$MEM-GC"]

    for i in range(100):
        source_lines.append(f"val mui8 var{i:03d} = {i % 256}.")

    source = "\n".join(source_lines)

    analyser = analyse_program(source)

    assert len(analyser.global_scope.symbols) == 100


def test_50_functions_no_duplicates():
    """Test program with 50 functions without duplicates."""

    source_lines = ["$MEM-GC"]

    for i in range(50):
        source_lines.append(f"fc func{i:02d}()!mai8 {{}}")

    source = "\n".join(source_lines)

    analyser = analyse_program(source)

    assert len(analyser.global_scope.symbols) == 50


def test_50_structs_no_duplicates():
    """Test program with 50 structs without duplicates."""

    source_lines = ["$MEM-GC"]

    for i in range(50):
        source_lines.append(f"sct Struct{i:02d} {{}}")

    source = "\n".join(source_lines)

    analyser = analyse_program(source)

    assert len(analyser.global_scope.symbols) == 50


def test_mixed_200_declarations():
    """Test program with 200 mixed declarations."""

    source_lines = ["$MEM-GC"]

    # Add 100 variables.
    for i in range(100):
        source_lines.append(f"val mui8 v{i:03d} = {i % 256}.")

    # Add 50 functions.
    i = 0
    functions_added = 0

    while functions_added < 50:
        name = f"f{i:02d}"

        if name != "f32":
            source_lines.append(f"fc {name}()!mui8 {{}}")
            functions_added += 1

        i += 1

    # Add 50 structs.
    for i in range(50):
        source_lines.append(f"sct S{i:02d} {{}}")

    source = "\n".join(source_lines)

    analyser = analyse_program(source)

    assert len(analyser.global_scope.symbols) == 200


# =============================================================================
# LONG IDENTIFIER TESTS
# =============================================================================


def test_very_long_identifier():
    """Test declarations with very long identifiers."""

    long_name = (
        "this_is_an_extremely_long_identifier_name_with_many_"
        "underscores_for_testing_purposes"
    )

    source = f"""

        $MEM-GC

        val mui8 {long_name} = 1.

        fc func_{long_name}()!mai8 {{}}

        sct Struct_{long_name} {{}}

    """

    analyser = analyse_program(source)

    assert analyser.global_scope.lookup(long_name) is not None
    assert analyser.global_scope.lookup(f"func_{long_name}") is not None
    assert analyser.global_scope.lookup(f"Struct_{long_name}") is not None


def test_identifier_patterns():
    """Test program behavior with valid identifier patterns."""

    source = """

        $MEM-GC

        val mui8 _private = 1.

        val mstr _123var = "test".

        val cbln var123 = true.

    """

    analyser = analyse_program(source)

    assert len(analyser.global_scope.symbols) == 3


# =============================================================================
# DECLARATION ORDER TESTS
# =============================================================================


def test_function_before_variable():
    """Test that declarations can appear in this order."""

    source = """

        $MEM-GC

        fc get_count()!mai8 {}

        val mui8 count = 0.

    """

    analyser = analyse_program(source)

    assert analyser.global_scope.lookup("get_count") is not None
    assert analyser.global_scope.lookup("count") is not None


def test_struct_before_variable():
    """Test struct declared before a variable."""

    source = """

        $MEM-GC

        sct Point {}

        val mui8 x = 0.

    """

    analyser = analyse_program(source)

    assert analyser.global_scope.lookup("Point") is not None
    assert analyser.global_scope.lookup("x") is not None


def test_struct_before_function():
    """Test struct declared before a function."""

    source = """

        $MEM-GC

        sct Config {}

        fc load_config()!mai8 {}

    """

    analyser = analyse_program(source)

    assert analyser.global_scope.lookup("Config") is not None
    assert analyser.global_scope.lookup("load_config") is not None


def test_interleaved_declarations():
    """Test interleaved declarations in various orders."""

    source = """

        $MEM-GC

        val mui8 a = 1.

        sct S1 {}

        val mstr b = "test".

        fc f1()!mai8 {}

        sct S2 {}

        val cbln c = true.

        fc f2()!mstr {}

        val mf32 d = 1.5.

        sct S3 {}

    """

    analyser = analyse_program(source)

    assert len(analyser.global_scope.symbols) == 9


# =============================================================================
# REAL-WORLD PATTERN TESTS
# =============================================================================


def test_typical_application_structure():
    """Test typical application structure."""

    source = """

        $MEM-GC

        sct Config {}

        sct State {}

        sct Result {}

        val mui8 version = 1.

        val mstr app_name = "MyApp".

        val cbln debug_mode = false.

        fc initialize()!mai8 {}

        fc run()!mai8 {}

        fc cleanup()!mai8 {}

        fc is_configured()!cbln {}

        fc get_status()!mstr {}

    """

    analyser = analyse_program(source)

    structs = [
        "Config",
        "State",
        "Result",
    ]

    variables = [
        "version",
        "app_name",
        "debug_mode",
    ]

    functions = [
        "initialize",
        "run",
        "cleanup",
        "is_configured",
        "get_status",
    ]

    for name in structs:
        symbol = analyser.global_scope.lookup(name)

        assert symbol is not None
        assert symbol.kind == "struct"
        assert symbol.scope is analyser.global_scope
        assert symbol.child_scope is not None

    for name in variables:
        symbol = analyser.global_scope.lookup(name)

        assert symbol is not None
        assert symbol.kind == "variable"
        assert symbol.scope is analyser.global_scope

    for name in functions:
        symbol = analyser.global_scope.lookup(name)

        assert symbol is not None
        assert symbol.kind == "function"
        assert symbol.scope is analyser.global_scope
        assert symbol.child_scope is not None


def test_module_like_structure():
    """Test module-like code structure."""

    source = """

        $MEM-GC

        // Constants

        val mui8 MAX_SIZE = 255.

        val mstr VERSION = "1.0.0".

        // Data structures

        sct Entry {}

        sct Cache {}

        // Utilities

        fc is_valid(mui8 size)!cbln {}

        fc hash(mstr key)!mai8 {}

        // Main API

        fc init()!mai8 {}

        fc set(mstr key, mstr value)!mai8 {}

        fc get(mstr key)!mstr {}

        fc clear()!mai8 {}

    """

    analyser = analyse_program(source)

    assert len(analyser.global_scope.symbols) == 10


def test_error_handling_structure():
    """Test error handling structure."""

    source = """

        $MEM-GC

        sct Error {}

        sct Success {}

        sct ErrorInfo {}

        fc has_error()!cbln {}

        fc get_error_message()!mstr {}

        fc handle_error()!mai8 {}

    """

    analyser = analyse_program(source)

    assert len(analyser.global_scope.symbols) == 6


# =============================================================================
# BOUNDARY AND STRESS TESTS
# =============================================================================


def test_minimal_valid_program():
    """Test minimal valid program."""

    source = """

        $MEM-GC

    """

    analyser = analyse_program(source)

    assert len(analyser.global_scope.symbols) == 0


def test_single_element_programs():
    """Test programs with one element of each declaration type."""

    programs = [
        ("$MEM-GC\nval mui8 x = 1.", "x"),
        ("$MEM-GC\nfc f()!mai8 {}", "f"),
        ("$MEM-GC\nsct S {}", "S"),
    ]

    for source, expected_name in programs:
        analyser = analyse_program(source)

        assert len(analyser.global_scope.symbols) == 1
        assert analyser.global_scope.lookup(expected_name) is not None


def test_duplicate_at_end_of_long_program():
    """Test duplicate declaration at the end of a long program."""

    source_lines = ["$MEM-GC"]

    # Add 50 unique variables.
    for i in range(50):
        source_lines.append(f"val mui8 var{i:02d} = {i}.")

    # Redeclare the first variable.
    source_lines.append('val mstr var00 = "duplicate".')

    source = "\n".join(source_lines)

    with raises(SemanticError):
        analyse_program(source)


def test_many_parameters_function():
    """Test function with many parameters."""

    params = ", ".join([f"mui8 p{i}" for i in range(20)])

    source = f"""

        $MEM-GC

        fc many_params({params})!mai8 {{}}

    """

    analyser = analyse_program(source)

    func = analyser.global_scope.lookup("many_params")

    assert func is not None
    assert func.kind == "function"

    # The function symbol belongs to the global scope.
    assert func.scope is analyser.global_scope

    # Its parameters belong to its child scope.
    function_scope = func.child_scope

    assert function_scope is not None
    assert function_scope is not analyser.global_scope
    assert function_scope.parent is analyser.global_scope

    for i in range(20):
        param = function_scope.lookup(f"p{i}")

        assert param is not None
        assert param.name == f"p{i}"
        assert param.kind == "function_parameter"
        assert param.type == "mui8"
        assert param.scope is function_scope


# =============================================================================
# SYMBOL PROPERTIES PRESERVATION
# =============================================================================


def test_all_symbol_properties_preserved():
    """Test that all function symbol properties are preserved."""

    source = """

        $MEM-GC

        fc add(mui8 x, mui8 y)!mui8 {}

    """

    analyser = analyse_program(source)

    func = analyser.global_scope.lookup("add")

    assert func is not None
    assert func.name == "add"
    assert func.kind == "function"
    assert func.type == "mui8"

    # The function declaration belongs to the global scope.
    assert func.scope is analyser.global_scope

    # The function owns a separate child scope.
    function_scope = func.child_scope

    assert function_scope is not None
    assert function_scope is not analyser.global_scope
    assert function_scope.parent is analyser.global_scope

    x = function_scope.lookup("x")
    y = function_scope.lookup("y")

    assert x is not None
    assert x.name == "x"
    assert x.kind == "function_parameter"
    assert x.type == "mui8"
    assert x.scope is function_scope

    assert y is not None
    assert y.name == "y"
    assert y.kind == "function_parameter"
    assert y.type == "mui8"
    assert y.scope is function_scope


def test_all_variable_types_properties():
    """Test that all data types are preserved."""

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
        "cui8",
        "cui16",
        "cui32",
        "cui64",
        "csi8",
        "csi16",
        "csi32",
        "csi64",
        "cstr",
        "cchar",
        "cbln",
        "cf32",
        "cf64",
    ]

    source_lines = ["$MEM-GC"]

    for i, dtype in enumerate(types):
        source_lines.append(f"val {dtype} v{i} = 0.")

    source = "\n".join(source_lines)

    analyser = analyse_program(source)

    for i, dtype in enumerate(types):
        symbol = analyser.global_scope.lookup(f"v{i}")

        assert symbol is not None
        assert symbol.type == dtype
        assert symbol.scope is analyser.global_scope
        assert symbol.child_scope is None


# =============================================================================
# SCOPE ISOLATION IN COMPLEX PROGRAMS
# =============================================================================


def test_function_scope_isolation():
    """Test that each function has an isolated child scope."""

    source = """

        $MEM-GC

        fc func1()!mai8 {}

        fc func2()!mai8 {}

        fc func3()!mai8 {}

    """

    analyser = analyse_program(source)

    f1 = analyser.global_scope.lookup("func1")
    f2 = analyser.global_scope.lookup("func2")
    f3 = analyser.global_scope.lookup("func3")

    assert f1 is not None
    assert f2 is not None
    assert f3 is not None

    # All function declarations belong to the global scope.
    assert f1.scope is analyser.global_scope
    assert f2.scope is analyser.global_scope
    assert f3.scope is analyser.global_scope

    # Each function owns a different child scope.
    assert f1.child_scope is not f2.child_scope
    assert f2.child_scope is not f3.child_scope
    assert f1.child_scope is not f3.child_scope

    # All function child scopes have the global scope as their parent.
    assert f1.child_scope.parent is analyser.global_scope
    assert f2.child_scope.parent is analyser.global_scope
    assert f3.child_scope.parent is analyser.global_scope
