import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "src"


def run_cli(*args, cwd):
    """Run `python -m teapot <args>` in `cwd` and return the CompletedProcess."""
    env = os.environ.copy()
    pythonpath = [str(SRC)]
    if existing_pythonpath := env.get("PYTHONPATH"):
        pythonpath.append(existing_pythonpath)
    env["PYTHONPATH"] = os.pathsep.join(pythonpath)

    return subprocess.run(
        [sys.executable, "-m", "teapot", *args],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def write_source(tmp_path, name, source):
    path = tmp_path / name
    path.write_text(source)
    return path


VALID_SOURCE = """
$MEM-GC
val mui8 x = 1.
fc foo()!void {
}
sct Bar {
    mui8 field.
}
"""


# ============================================================================
# SUCCESSFUL COMPILATION
# ============================================================================


def test_valid_program_compiles_with_exit_code_zero(tmp_path):
    write_source(tmp_path, "ok.tp", VALID_SOURCE)

    result = run_cli("ok.tp", cwd=tmp_path)

    assert result.returncode == 0
    assert result.stderr == ""


def test_valid_program_produces_no_stdout_output_without_trace(tmp_path):
    write_source(tmp_path, "ok.tp", VALID_SOURCE)

    result = run_cli("ok.tp", cwd=tmp_path)

    assert result.stdout == ""


def test_successful_compile_creates_build_directory(tmp_path):
    write_source(tmp_path, "ok.tp", VALID_SOURCE)

    run_cli("ok.tp", cwd=tmp_path)

    assert (tmp_path / "build").is_dir()


def test_build_directory_is_recreated_on_second_run(tmp_path):
    write_source(tmp_path, "ok.tp", VALID_SOURCE)
    build_dir = tmp_path / "build"

    run_cli("ok.tp", cwd=tmp_path)
    assert build_dir.is_dir()

    # Drop a marker file into build/ to prove it gets wiped, not reused.
    marker = build_dir / "marker.txt"
    marker.write_text("stale")

    run_cli("ok.tp", cwd=tmp_path)

    assert build_dir.is_dir()
    assert not marker.exists()


def test_relative_path_input_works_from_the_compile_directory(tmp_path):
    subdir = tmp_path / "proj"
    subdir.mkdir()
    write_source(subdir, "main.tp", VALID_SOURCE)

    result = run_cli("main.tp", cwd=subdir)

    assert result.returncode == 0
    assert (subdir / "build").is_dir()


def test_fixture_file_compiles_successfully_via_cli(tmp_path):
    fixture = REPO_ROOT / "examples" / "fixtures" / "semanticanalysis.tp"
    write_source(tmp_path, "fixture.tp", fixture.read_text())

    result = run_cli("fixture.tp", cwd=tmp_path)

    assert result.returncode == 0


# ============================================================================
# INPUT / FILE ERRORS
# ============================================================================


def test_non_tp_extension_is_rejected(tmp_path):
    write_source(tmp_path, "not_teapot.txt", "hello")

    result = run_cli("not_teapot.txt", cwd=tmp_path)

    assert result.returncode != 0
    assert "not a Teapot file" in result.stderr


def test_missing_file_is_reported(tmp_path):
    result = run_cli("does_not_exist.tp", cwd=tmp_path)

    assert result.returncode != 0
    assert "does not exist" in result.stderr


def test_non_tp_extension_does_not_create_build_directory(tmp_path):
    write_source(tmp_path, "not_teapot.txt", "hello")

    run_cli("not_teapot.txt", cwd=tmp_path)

    assert not (tmp_path / "build").exists()


def test_missing_file_does_not_create_build_directory(tmp_path):
    run_cli("does_not_exist.tp", cwd=tmp_path)

    assert not (tmp_path / "build").exists()


def test_directory_with_tp_extension_is_reported_as_missing_or_unreadable(tmp_path):
    # A directory named like a .tp file is neither a valid source file nor
    # cleanly "missing"; the CLI should still fail rather than succeed.
    (tmp_path / "adir.tp").mkdir()

    result = run_cli("adir.tp", cwd=tmp_path)

    assert result.returncode != 0


# ============================================================================
# LEXER / PARSER / SEMANTIC ERRORS SURFACED THROUGH THE CLI
# ============================================================================


def test_lexer_error_surfaces_through_cli(tmp_path):
    source = """
        $MEM-GC
        val mui8 x = 1.
        $MEM-GC
    """
    write_source(tmp_path, "lex_err.tp", source)

    result = run_cli("lex_err.tp", cwd=tmp_path)

    assert result.returncode != 0
    assert "Lexer error" in result.stdout
    assert "LexerError" in result.stderr


def test_parser_error_surfaces_through_cli(tmp_path):
    source = """
        $MEM-GC
        val mui8 x = .
    """
    write_source(tmp_path, "parse_err.tp", source)

    result = run_cli("parse_err.tp", cwd=tmp_path)

    assert result.returncode != 0
    assert "Parser error" in result.stdout
    assert "ParserError" in result.stderr


def test_semantic_error_surfaces_through_cli(tmp_path):
    source = """
        $MEM-GC
        val mui8 dup = 1.
        val mstr dup = "again".
    """
    write_source(tmp_path, "sem_err.tp", source)

    result = run_cli("sem_err.tp", cwd=tmp_path)

    assert result.returncode != 0
    assert "Semantic analysis error" in result.stdout
    assert "SemanticError" in result.stderr


def test_error_run_still_creates_build_directory(tmp_path):
    # main.py creates build/ before invoking the compiler, so even a run
    # that fails partway through should leave the directory behind.
    source = """
        $MEM-GC
        val mui8 dup = 1.
        val mui8 dup = 2.
    """
    write_source(tmp_path, "sem_err.tp", source)

    run_cli("sem_err.tp", cwd=tmp_path)

    assert (tmp_path / "build").is_dir()


# ============================================================================
# TRACE MODE
# ============================================================================


def test_trace_flag_produces_verbose_stdout(tmp_path):
    write_source(tmp_path, "ok.tp", VALID_SOURCE)

    result = run_cli("-t", "ok.tp", cwd=tmp_path)

    # Note: the lexer's own "BEGIN LEXICAL ANALYSIS" banner is gated on a
    # module-level flag that `-t` does not actually set, so it never prints;
    # these are the trace markers that genuinely do appear.
    assert result.returncode == 0
    assert "Token Object list" in result.stdout
    assert "END LEXICAL ANALYSIS" in result.stdout
    assert "BEGIN ABSTRACT SYNTAX TREE CONSTRUCTION" in result.stdout
    assert "BEGIN SEMANTIC ANALYSIS" in result.stdout
    assert "SYMBOL TABLE" in result.stdout


def test_trace_flag_long_form_matches_short_form(tmp_path):
    write_source(tmp_path, "ok.tp", VALID_SOURCE)

    short = run_cli("-t", "ok.tp", cwd=tmp_path)

    build_dir = tmp_path / "build"
    if build_dir.exists():
        for item in build_dir.iterdir():
            item.unlink()

    long = run_cli("--trace", "ok.tp", cwd=tmp_path)

    assert short.returncode == long.returncode == 0
    assert "BEGIN ABSTRACT SYNTAX TREE CONSTRUCTION" in short.stdout
    assert "BEGIN ABSTRACT SYNTAX TREE CONSTRUCTION" in long.stdout


def test_trace_flag_writes_build_log(tmp_path):
    write_source(tmp_path, "ok.tp", VALID_SOURCE)

    run_cli("-t", "ok.tp", cwd=tmp_path)

    build_log = tmp_path / "build" / "build.log"
    assert build_log.is_file()
    assert "BEGIN SEMANTIC ANALYSIS" in build_log.read_text()


def test_without_trace_no_build_log_is_written_on_success(tmp_path):
    write_source(tmp_path, "ok.tp", VALID_SOURCE)

    run_cli("ok.tp", cwd=tmp_path)

    build_log = tmp_path / "build" / "build.log"
    assert not build_log.exists()
