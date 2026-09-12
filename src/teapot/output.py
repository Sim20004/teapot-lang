"""Unified terminal, trace, log, and diagnostic output for TeapotLang."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

ANSI = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "red": "\033[31m",
    "yellow": "\033[33m",
    "green": "\033[32m",
    "cyan": "\033[36m",
    "dim": "\033[2m",
}


@dataclass
class OutputOptions:
    quiet: bool = False
    verbosity: int = 0
    color: str = "auto"
    diagnostic_format: str = "text"
    diagnostic_detail: str = "normal"
    log_file: Path | None = None


class Output:
    def __init__(self, options=None, *, stdout=None, stderr=None):
        self.options = options or OutputOptions()
        self.stdout = stdout
        self.stderr = stderr

    def configure(self, **values):
        for name, value in values.items():
            if hasattr(self.options, name):
                setattr(self.options, name, value)

    def _use_color(self, stream):
        if self.options.color == "always":
            return True
        if self.options.color == "never":
            return False
        return bool(getattr(stream, "isatty", lambda: False)())

    def style(self, text, color, *, stream=None):
        stream = stream or self.stdout or sys.stdout
        if not self._use_color(stream):
            return text
        return f"{ANSI[color]}{text}{ANSI['reset']}"

    def _write_log(self, text):
        if self.options.log_file is None:
            return
        path = Path(self.options.log_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as log:
            log.write(text.rstrip("\n") + "\n")

    def write(self, text, *, level="info", stream=None, force=False):
        if self.options.quiet and level in {"trace", "info"} and not force:
            return
        stream = stream or self.stdout
        colors = {"error": "red", "warning": "yellow", "info": "cyan"}
        rendered = self.style(text, colors.get(level, "dim"), stream=stream)
        print(rendered, file=stream)
        self._write_log(text)

    def trace(self, text):
        self.write(text, level="trace")

    def warning(self, text):
        self.write(text, level="warning")

    def verbose(self, text):
        if self.options.verbosity:
            self.write(text, level="info")

    def diagnostic(self, error):
        if self.options.diagnostic_format == "json":
            payload = {
                "code": error.code,
                "phase": error.phase,
                "location": str(error.location),
                "message": error.message,
                "hint": error.hint,
            }
            if self.options.diagnostic_detail == "full":
                payload["details"] = {
                    key: self._detail_value(value)
                    for key, value in error.details.items()
                    if key != "node"
                }
            self.write(json.dumps(payload, sort_keys=True), level="error", force=True)
            return

        message = error.message
        if self.options.diagnostic_detail == "concise":
            text = f"{error.phase.capitalize()} error at {error.location}: {message}"
        elif self.options.diagnostic_detail == "full":
            text = (
                f"{error.phase.capitalize()} error [{error.code}] at "
                f"{error.location}: {message}\n"
                f"  Hint: {error.hint}"
            )
        else:
            text = (
                f"{error.phase.capitalize()} error at {error.location}: {message}\n"
                f"  Hint: {error.hint}"
            )
        self.write(text, level="error", force=True)

    @staticmethod
    def _detail_value(value):
        if value is None or isinstance(value, (bool, int, float, str)):
            return value
        if hasattr(value, "name") and isinstance(value.name, str):
            return value.name
        if hasattr(value, "value") and isinstance(value.value, (bool, int, float, str)):
            return value.value
        return type(value).__name__


_output = Output(OutputOptions(log_file=Path("build/build.log")))


def get_output():
    return _output


def configure_output(**values):
    _output.configure(**values)


__all__ = ["Output", "OutputOptions", "configure_output", "get_output"]
