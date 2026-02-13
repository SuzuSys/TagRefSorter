from dataclasses import dataclass, field

import pytest
from markdown_it.token import Token
from pylatexenc.latexwalker import LatexMathNode, LatexNode, LatexWalker

from tagrefsorter.parser import MathBlock

EXPECTED_RESULTS_STR = [
    [],
    [r"$$x\tag 1$$"],
]


@dataclass
class ExpectedCellResult:
    input: list[Token] = field(default_factory=list)
    output: list[MathBlock] = field(default_factory=list)


@pytest.fixture(scope="session")
def smb_case(md_parser, smb_cells, latex_context) -> list[ExpectedCellResult]:
    """Fixture that provides test cases for the _search_math_block function.

    It parses the source of each cell in the smb_cells fixture using the md_parser
    and pairs it with the expected results.

    :return: List of ExpectedCellResult objects, each containing
    a list of tuples (list[LatexNode], str) representing expected output
    :rtype: list[ExpectedCellResult]
    """
    expected_results: list[ExpectedCellResult] = []
    for smb_cell, exp_strs in zip(smb_cells, EXPECTED_RESULTS_STR, strict=True):
        expected_cell_result = ExpectedCellResult()
        expected_cell_result.input = md_parser.parse(smb_cell.source)
        for exp_str in exp_strs:
            latex_walker = LatexWalker(exp_str, latex_context=latex_context)
            root_math_block = latex_walker.get_latex_nodes(pos=0)[0]
            assert isinstance(root_math_block[0], LatexMathNode)  # Unexpected error check
            layer0_nodes: list[LatexNode] = root_math_block[0].nodelist
            expected_cell_result.output.append(
                MathBlock(layer0_nodes=layer0_nodes, content=exp_str),
            )
        expected_results.append(expected_cell_result)
    return expected_results
