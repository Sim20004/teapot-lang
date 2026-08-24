import importlib.metadata
import subprocess
from pathlib import Path

import pytest

import teapot

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "src"


def run_cli(*args, cwd=None):
    return subprocess.run(
        ["teapot", *args],
        cwd=cwd or REPO_ROOT,
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
