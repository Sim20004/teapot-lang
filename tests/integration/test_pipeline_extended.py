from pathlib import Path

from pytest import raises

from teapot.lexer import LexerError
from teapot.lexer import run as lexer_run
from teapot.parser import ParserError
from teapot.semantic import SemanticError

REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = REPO_ROOT / "examples"


# ============================================================================
# TOP-LEVEL ENTRY POINT (lexer.run -> parser.run -> semantic.analyse)
# ============================================================================


def test_lexer_run_drives_the_whole_pipeline_for_a_valid_program():
    """`lexer.run` is the single entry point production code calls; make
    sure it really does chain lexing, parsing and semantic analysis rather
    than stopping after tokenising."""
    source = """
        $MEM-GC
        val mui8 x = 1.
        fc double(mui8 n)!mui8 {
        }
        sct Point {
            mui8 x.
            mui8 y.
        }
    """

    # Should not raise anything; the whole pipeline runs to completion.
    result = lexer_run(source, False)
    assert result is None


def test_lexer_run_propagates_lexer_errors():
    """An invalid token must surface as a LexerError from the top-level
    entry point, not just from calling the Lexer class directly."""
    source = """
        $MEM-GC
        val mui8 x = 1 @ 2.
    """

    with raises(LexerError):
        lexer_run(source, False)


def test_lexer_run_propagates_duplicate_directive_lexer_error():
    source = """
        $MEM-GC
        val mui8 x = 1.
        $MEM-GC
    """

    with raises(LexerError):
        lexer_run(source, False)


def test_lexer_run_propagates_unterminated_string_lexer_error():
    source = """
        $MEM-GC
        val mstr x = "never closed.
    """

    with raises(LexerError):
        lexer_run(source, False)


def test_lexer_run_propagates_parser_errors():
    """A syntax error further down the pipeline must still surface all the
    way back through lexer.run, proving the stages are actually chained."""
    source = """
        $MEM-GC
        val mui8 x = .
    """

    with raises(ParserError):
        lexer_run(source, False)


def test_lexer_run_propagates_semantic_errors():
    """A semantically invalid but syntactically valid program must raise a
    SemanticError from the top-level entry point."""
    source = """
        $MEM-GC
        val mui8 dup = 1.
        val mstr dup = "again".
    """

    with raises(SemanticError):
        lexer_run(source, False)


def test_lexer_run_with_trace_enabled_still_completes():
    """Trace mode exercises a large number of extra print statements across
    every stage; it should never change the outcome of a valid compile."""
    source = """
        $MEM-GC
        val mui8 traced = 1.
    """

    assert lexer_run(source, True) is None


def test_lexer_run_with_trace_enabled_still_raises_errors():
    source = """
        $MEM-GC
        val mui8 dup = 1.
        val mui8 dup = 2.
    """

    with raises(SemanticError):
        lexer_run(source, True)


# ============================================================================
# REAL EXAMPLE / FIXTURE FILES
# ============================================================================


def test_fixture_semanticanalysis_compiles_end_to_end():
    """examples/fixtures/semanticanalysis.tp is a small hand-written fixture
    that is expected to compile cleanly through every stage."""
    source = (EXAMPLES / "fixtures" / "semanticanalysis.tp").read_text()

    assert lexer_run(source, False) is None


def test_example_operators_tp_is_pinned_to_current_semantic_scaffold_behaviour():
    """examples/operators.tp lexes and parses correctly, but the semantic
    analyser is documented as a scaffold that only understands top-level
    variables, functions and structs. A top-level `operator` declaration is
    therefore expected to raise SemanticError. This pins that (currently
    correct) behaviour so a regression is caught if the two stages ever
    drift out of sync."""
    source = (EXAMPLES / "operators.tp").read_text()

    with raises(SemanticError):
        lexer_run(source, False)


def test_example_hello_tp_fails_to_parse_on_unsupported_list_type():
    """examples/hello.tp showcases aspirational syntax (e.g. `list<ui8>`)
    that the parser does not currently accept. This pins the real, current
    failure mode (a ParserError, not a crash or silent misparse) so future
    parser work has a clear regression signal."""
    source = (EXAMPLES / "hello.tp").read_text()

    with raises(ParserError):
        lexer_run(source, False)


# ============================================================================
# STRUCT FIELD SYNTAX
# ============================================================================


def test_struct_with_typed_fields_compiles():
    source = """
        $MEM-GC
        sct Point {
            mui8 x.
            mui8 y.
        }
    """

    assert lexer_run(source, False) is None


def test_struct_with_many_field_types_compiles():
    source = """
        $MEM-GC
        sct Record {
            mui8 a.
            mstr b.
            cbln c.
            mf32 d.
            mf64 e.
            cstr f.
        }
    """

    assert lexer_run(source, False) is None


def test_public_struct_with_fields_compiles():
    source = """
        $MEM-GC
        pub sct Public {
            mui8 value.
        }
    """

    assert lexer_run(source, False) is None


def test_struct_with_invalid_field_type_raises_parser_error():
    source = """
        $MEM-GC
        sct Broken {
            notatype x.
        }
    """

    with raises(ParserError):
        lexer_run(source, False)


# ============================================================================
# NESTED DECLARATIONS (function/struct nested inside a function body)
# ============================================================================


def test_function_nested_inside_function_body_compiles():
    source = """
        $MEM-GC
        fc outer()!void {
            fc inner()!void {
            }
        }
    """

    assert lexer_run(source, False) is None


def test_struct_nested_inside_function_body_compiles():
    source = """
        $MEM-GC
        fc outer()!void {
            sct Local {
                mui8 value.
            }
        }
    """

    assert lexer_run(source, False) is None


def test_deeply_nested_function_declarations_compile():
    source = """
        $MEM-GC
        fc level1()!void {
            fc level2()!void {
                fc level3()!void {
                    val mui8 deep = 1.
                }
            }
        }
    """

    assert lexer_run(source, False) is None


def test_mixed_nested_declarations_compile():
    source = """
        $MEM-GC
        fc outer()!void {
            val mui8 a = 1.
            sct Inner {
                mui8 field.
            }
            fc helper()!void {
                val mstr b = "nested".
            }
        }
    """

    assert lexer_run(source, False) is None


def test_duplicate_name_inside_nested_function_scope_raises():
    source = """
        $MEM-GC
        fc outer()!void {
            val mui8 a = 1.
            val mstr a = "dup".
        }
    """

    with raises(SemanticError):
        lexer_run(source, False)


def test_same_name_in_sibling_function_scopes_does_not_conflict():
    """Two different functions may each declare a local variable with the
    same name, since each has its own child scope."""
    source = """
        $MEM-GC
        fc first()!void {
            val mui8 shared = 1.
        }
        fc second()!void {
            val mui8 shared = 2.
        }
    """

    assert lexer_run(source, False) is None


# ============================================================================
# SOURCE-LEVEL EDGE CASES THROUGH THE WHOLE PIPELINE
# ============================================================================


def test_crlf_line_endings_flow_through_whole_pipeline():
    source = "$MEM-GC\r\nval mui8 x = 1.\r\nfc f()!void {\r\n}\r\n"

    assert lexer_run(source, False) is None


def test_comments_are_ignored_through_whole_pipeline():
    source = """
        $MEM-GC
        // this is a leading comment
        val mui8 x = 1. // trailing comment
        // another comment
        fc f()!void {
            // comment inside a function body
        }
    """

    assert lexer_run(source, False) is None


def test_negative_integer_literal_through_whole_pipeline():
    source = """
        $MEM-GC
        val msi32 x = -5.
    """

    assert lexer_run(source, False) is None


def test_float_literal_through_whole_pipeline():
    source = """
        $MEM-GC
        val mf64 pi = 3.14159265359.
    """

    assert lexer_run(source, False) is None


def test_large_integer_literal_through_whole_pipeline():
    source = """
        $MEM-GC
        val mui64 huge = 999999999999999999.
    """

    assert lexer_run(source, False) is None


def test_boolean_literals_through_whole_pipeline():
    source = """
        $MEM-GC
        val cbln yes = true.
        val cbln no = false.
    """

    assert lexer_run(source, False) is None


def test_string_literal_through_whole_pipeline():
    source = """
        $MEM-GC
        val mstr greeting = "Hello, Teapot!".
    """

    assert lexer_run(source, False) is None


def test_empty_string_literal_through_whole_pipeline():
    source = """
        $MEM-GC
        val mstr empty = "".
    """

    assert lexer_run(source, False) is None


def test_manual_memory_mode_through_whole_pipeline():
    source = """
        $MEM-MANUAL
        val mui8 x = 1.
    """

    assert lexer_run(source, False) is None


def test_program_with_only_whitespace_and_directive_compiles():
    source = "$MEM-GC\n\n\n   \n\t\n"

    assert lexer_run(source, False) is None


# ============================================================================
# ERROR DETAIL PROPAGATION
# ============================================================================


def test_lexer_error_carries_correct_line_and_column_through_pipeline():
    source = "$MEM-GC\nval mui8 x = 1.\n$MEM-GC\n"

    with raises(LexerError) as exc_info:
        lexer_run(source, False)

    assert exc_info.value.line == 3
    assert exc_info.value.col == 1


def test_semantic_error_names_the_offending_symbol():
    source = """
        $MEM-GC
        fc collision()!void {
        }
        sct collision {
        }
    """

    with raises(SemanticError) as exc_info:
        lexer_run(source, False)

    assert "collision" in str(exc_info.value)


def test_parser_error_message_mentions_position():
    source = """
        $MEM-GC
        val mui8 = 1.
    """

    with raises(ParserError) as exc_info:
        lexer_run(source, False)

    assert exc_info.value.position is not None