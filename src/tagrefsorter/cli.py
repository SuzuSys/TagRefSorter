#!/usr/bin/env python3
import argparse
import pathlib
import sys
import nbformat
from . import __version__
from .parser import TagRenumberer

def parse_args():
    parser = argparse.ArgumentParser(
        description="Read a Jupyter Notebook (.ipynb) file and normalize LaTeX \\tag numbering"
    )
    parser.add_argument(
        "notebook",
        type=pathlib.Path,
        help="Path to the .ipynb file to be modified",
    )
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        help="Path to save the modified .ipynb file (if not provided, overwrites the input file)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show the program version and exit",
    )
    return parser.parse_args()

def update_nb(nb: nbformat.NotebookNode) -> nbformat.NotebookNode:
    renumberer = TagRenumberer()
    for cell in nb.cells:
        if cell.cell_type == 'markdown':
            cell.source = renumberer.renumber_tags(cell.source)
    for cell in nb.cells:
        if cell.cell_type == 'markdown':
            cell.source = renumberer.renumber_refs(cell.source)
    return nb


def main():
    args = parse_args()
    nb_path: pathlib.Path = args.notebook
    onb_path: pathlib.Path = args.output if args.output else nb_path

    if not nb_path.exists():
        print(f"Error: file not found: {nb_path}", file=sys.stderr)
        sys.exit(1)

    if nb_path.suffix != ".ipynb":
        print("Error: input file must be .ipynb", file=sys.stderr)
        sys.exit(1)
    
    if args.output and onb_path.suffix != ".ipynb":
        print("Error: output file must be .ipynb", file=sys.stderr)
        sys.exit(1)

    nb = nbformat.read(nb_path, as_version=4)
    updated_nb = update_nb(nb)
    nbformat.write(updated_nb, onb_path)

    if args.output:
        print(f"Written: {onb_path}")
    else:
        print(f"Overwritten: {nb_path}")
