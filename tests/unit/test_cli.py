import importlib
import importlib.metadata
import os
import runpy
import subprocess
import sys
from pathlib import Path

import pytest

import teapot
import teapot.teapot_ast as ast
from teapot.debug import print as debug_print
from teapot.errors import TypeMismatchError
from teapot.lexer import Lexer, LexerError
from teapot.main import TeapotError
from teapot.semantic import SemanticError

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "src"


def run_cli(*args, cwd=None):
    env = os.environ.copy()
    pythonpath = [str(SRC)]
    if existing_pythonpath := env.get("PYTHONPATH"):
        pythonpath.append(existing_pythonpath)
    env["PYTHONPATH"] = os.pathsep.join(pythonpath)

    return subprocess.run(
        [sys.executable, "-m", "teapot", *args],
        cwd=cwd or REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_version_prints_name_and_version():
    result = run_cli("--version")

    assert result.stdout.strip() == f"TeapotLang {teapot.__version__}"


def test_version_exits_successfully():
    result = run_cli("--version")

    assert result.returncode == 0
    assert result.stderr == ""


def test_version_does_not_require_an_input_file():
    # --input is a required argument; the version action has to short-circuit
    # parsing before argparse enforces that, or --version is unusable on its own.
    result = run_cli("--version")

    assert result.returncode == 0
    assert "required" not in result.stderr


def test_version_does_not_run_the_compiler(tmp_path):
    # Reporting the version must not touch the build directory main.py wipes
    # and recreates on a real run.
    result = run_cli("--version", cwd=tmp_path)

    assert result.returncode == 0
    assert not (tmp_path / "build").exists()


def test_version_is_listed_in_help():
    result = run_cli("--help")

    assert result.returncode == 0
    assert "--version" in result.stdout


def test_missing_input_still_errors():
    result = run_cli()

    assert result.returncode != 0
    assert "required" in result.stderr


def test_package_version_matches_distribution_metadata():
    # pyproject.toml reads the version from teapot.__version__, so an installed
    # build must report the same string the CLI does.
    try:
        installed = importlib.metadata.version("teapot")
    except importlib.metadata.PackageNotFoundError:
        pytest.skip("teapot is not installed in this environment")

    assert installed == teapot.__version__


def test_cli_main_direct_paths(monkeypatch, tmp_path):
    import teapot.main as cli

    source = tmp_path / "program.tp"
    source.write_text("$MEM-GC")
    calls = []
    monkeypatch.setattr(
        cli.lexer, "run", lambda source, trace: calls.append((source, trace))
    )
    monkeypatch.chdir(tmp_path)

    monkeypatch.setattr(sys, "argv", ["teapot", "program.tp"])
    cli.main()
    assert calls[-1] == ("$MEM-GC", False)
    (tmp_path / "build" / "old").write_text("stale")

    monkeypatch.setattr(sys, "argv", ["teapot", "-t", "program.tp"])
    cli.main()
    assert calls[-1] == ("$MEM-GC", True)
    assert not (tmp_path / "build" / "old").exists()

    monkeypatch.setattr(sys, "argv", ["teapot", "bad.txt"])
    with pytest.raises(TeapotError):
        cli.main()
    monkeypatch.setattr(sys, "argv", ["teapot", "missing.tp"])
    with pytest.raises(TeapotError):
        cli.main()


def test_module_entrypoint_delegates(monkeypatch):
    calls = []
    monkeypatch.setattr("teapot.main.main", lambda: calls.append(True))
    runpy.run_module("teapot", run_name="__main__")
    assert calls == [True]


def test_module_entrypoint_import_path_covers_guard_false_branch():
    importlib.import_module("teapot.__main__")


def test_debug_print_rejects_unsupported_options():
    with pytest.raises(TypeError, match="unsupported output options"):
        debug_print("message", unsupported=True)


def test_cli_converts_compiler_errors_to_clean_exit(monkeypatch, tmp_path, capsys):
    import teapot.main as cli

    source = tmp_path / "broken.tp"
    source.write_text("$MEM-GC\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["teapot", "broken.tp"])

    def fail_compile(source_text, trace):
        raise TypeMismatchError("bad type")

    monkeypatch.setattr(cli.lexer, "run", fail_compile)

    with pytest.raises(SystemExit, match="1"):
        cli.main()

    assert "SemanticError: compilation failed" in capsys.readouterr().err


@pytest.mark.parametrize("module_name", ["teapot.tokens", "teapot.teapot_ast"])
def test_internal_modules_reject_direct_execution(module_name):
    with pytest.raises(SystemExit, match="Cannot run this file directly"):
        runpy.run_module(module_name, run_name="__main__")


def test_phase_public_api_modules_and_compiler_pipeline():
    ast_api = importlib.import_module("teapot.ast")
    compiler_api = importlib.import_module("teapot.compiler")
    lexing_api = importlib.import_module("teapot.lexing")
    lexing_errors = importlib.import_module("teapot.lexing.errors")
    parsing_errors = importlib.import_module("teapot.parsing.errors")
    semantic_errors = importlib.import_module("teapot.semantic.errors")

    assert ast_api.Program is ast.Program
    assert compiler_api.compile_source("$MEM-GC\n")
    assert lexing_api.Lexer is Lexer
    assert lexing_errors.LexerError is LexerError
    assert parsing_errors.__all__ == []
    assert semantic_errors.SemanticError is SemanticError
