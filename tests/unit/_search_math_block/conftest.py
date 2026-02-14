from collections.abc import Callable

import pytest
from markdown_it import MarkdownIt
from nbformat import NotebookNode
from pylatexenc.latexwalker import LatexNode

from tagrefsorter.parser import MathBlock

from .test_smb import ExpectedCellResult

_SEARCH_MATH_BLOCK_FIXTURE_DIR = "tests/unit/_search_math_block/smb_fixtures.ipynb"

EXPECTED_RESULTS_STR = [
    [],
    [r"$$x\tag 1$$"],
]


@pytest.fixture(scope="session")
def smb_case(
    md_parser: MarkdownIt,
    load_markdown_cells: Callable[[str], list[NotebookNode]],
    get_layer0_nodes: Callable[[str], list[LatexNode]],
) -> list[ExpectedCellResult]:
    """Fixture that provides test cases for the _search_math_block function.

    It parses the source of each cell in the smb_cells fixture using the md_parser
    and pairs it with the expected results.

    :return: List of ExpectedCellResult objects, each containing
    a list of tuples (list[LatexNode], str) representing expected output
    :rtype: list[ExpectedCellResult]
    """
    smb_cells = load_markdown_cells(_SEARCH_MATH_BLOCK_FIXTURE_DIR)
    expected_results: list[ExpectedCellResult] = []
    for smb_cell, exp_strs in zip(smb_cells, EXPECTED_RESULTS_STR, strict=True):
        expected_cell_result = ExpectedCellResult()
        expected_cell_result.input = md_parser.parse(smb_cell.source)
        for exp_str in exp_strs:
            layer0_nodes = get_layer0_nodes(exp_str)
            expected_cell_result.output.append(
                MathBlock(layer0_nodes=layer0_nodes, content=exp_str),
            )
        expected_results.append(expected_cell_result)
    return expected_results
