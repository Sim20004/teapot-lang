import argparse

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
    help="Enable exhaustive debug output",
    action="store_true"
)

args = parser.parse_args()

trace = args.trace

with open(args.input, "r") as input_file:
    source = input_file.read()

import lexer

lexer.run(source, trace)