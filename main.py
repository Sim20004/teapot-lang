import argparse
from pathlib import Path
import os
import shutil

from src import lexer

class TeapotError(Exception):
    def __init__(self, msg):
        super().__init__(f"Teapot error: {msg}")
        self.msg = msg

parser = argparse.ArgumentParser()

parser.add_argument(
    "-i",
    "--input",
    help="Input source file",
    required=True
)

parser.add_argument(
    "-t",
    "--trace",
    help="Enable debug output",
    action="store_true"
)


args = parser.parse_args()

trace = args.trace

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


lexer.run(source, trace)