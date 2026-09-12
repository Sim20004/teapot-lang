import argparse
import os
import shutil
import sys
from pathlib import Path

from teapot import __version__, lexer
from teapot.errors import TeapotCompilerError
from teapot.output import configure_output, get_output


class TeapotError(Exception):
    def __init__(self, msg):
        super().__init__(f"Teapot error: {msg}")
        self.msg = msg


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "input",
        help="Input source file",
    )

    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument(
        "-q",
        "--quiet",
        help="Suppress informational and trace output",
        action="store_true",
    )
    verbosity.add_argument(
        "-v",
        "--verbose",
        help="Increase informational output (repeat for more detail)",
        action="count",
        default=0,
    )

    parser.add_argument(
        "-t",
        "--trace",
        "--debug",
        help="Enable compiler trace output",
        action="store_true",
    )
    parser.add_argument(
        "--color",
        choices=("auto", "always", "never"),
        default="auto",
        help="Control ANSI colours in terminal output (default: auto)",
    )
    parser.add_argument(
        "--diagnostic-format",
        choices=("text", "json"),
        default="text",
        help="Choose human-readable or machine-readable diagnostics",
    )
    parser.add_argument(
        "--diagnostic-detail",
        choices=("concise", "normal", "full"),
        default="normal",
        help="Control the amount of detail in diagnostics",
    )
    log_group = parser.add_mutually_exclusive_group()
    log_group.add_argument(
        "--log-file",
        type=Path,
        help="Write trace and diagnostic output to this file",
    )
    log_group.add_argument(
        "--no-log",
        help="Disable compiler log file output",
        action="store_true",
    )

    parser.add_argument(
        "--version",
        help="Show the TeapotLang version and exit",
        action="version",
        version=f"TeapotLang {__version__}",
    )

    args = parser.parse_args()

    trace = args.trace
    log_file = None if args.no_log else args.log_file or Path("build/build.log")
    configure_output(
        quiet=args.quiet,
        verbosity=args.verbose,
        color=args.color,
        diagnostic_format=args.diagnostic_format,
        diagnostic_detail=args.diagnostic_detail,
        log_file=log_file,
    )
    extension = Path(args.input).suffix

    if extension != ".tp":
        raise TeapotError("Inputted file is not a Teapot file!")

    try:
        with open(args.input, "r") as input_file:
            source = input_file.read()
    except FileNotFoundError:
        raise TeapotError("Input file does not exist!")

    if not os.path.exists("build"):
        os.makedirs("build")
    else:
        shutil.rmtree("build")
        os.makedirs("build")

    get_output().verbose(f"Compiling {args.input}")
    try:
        lexer.run(source, trace)
    except TeapotCompilerError as error:
        print(f"{type(error).__name__}: compilation failed", file=sys.stderr)
        raise SystemExit(1) from None
