"""
Example usage:

    $ python3 main.py sample.txt
    $ python3 main.py --outdir /tmp sample-0.txt sample-1.txt sample-2.txt
"""

from __future__ import annotations

import argparse
import itertools
import pathlib
import re
from typing import TextIO

import rules

regular_typos: list[tuple[re.Pattern, str]] = []


def fix_regular_typo(line: str) -> str:
    """
    Regular typo means that they can be simply replaced by a regular expression.
    Fixing them does not require any context information.
    """
    for typo, replace in regular_typos:
        line = typo.sub(replace, line)
    return line


def correct(input: TextIO, output: TextIO) -> None:
    """
    Corrects typos from input file and write to output file.
    """
    for line in input:
        stripped_line = line.strip()
        if len(stripped_line) <= 1:
            output.write(stripped_line + "\n")
            continue
        fixed = fix_regular_typo(stripped_line)
        fixed = rules.apply_contextual_rules(fixed)
        output.write(fixed + "\n")


def main():
    parser = argparse.ArgumentParser(description="Fix Cantonese typo.")
    parser.add_argument(
        "--inputs", type=str, nargs="+",
        help="Input text files, each line is a sentence. If the input is a folder, all text files will be globbed.")
    parser.add_argument(
        "--outdir", type=str, default="output", nargs="?",
        help="Output directory. Defaults to ‘output’.")
    args = parser.parse_args()

    # Read regular typos
    for line in open("regular.txt", "r", encoding="utf-8"):
        typo, replace = line.strip().split(",")
        regular_typos.append(
            (re.compile(typo.replace(" ", "\s*"), re.I), replace))

    outdir = pathlib.Path(args.outdir)
    for input, output in itertools.chain.from_iterable(
        [(input, input.name)] if input.is_file() else [
            (path, path.relative_to(input)) for path in input.rglob("*.txt")]
        for input in map(pathlib.Path, args.inputs)
    ):
        output = outdir / output
        output.parent.mkdir(parents=True, exist_ok=True)
        print(f"Correcting {input} -> {output}")
        with open(input, "r", encoding="utf-8") as input_f, open(output, "w", encoding="utf-8") as output_f:
            correct(input_f, output_f)


if __name__ == "__main__":
    main()
