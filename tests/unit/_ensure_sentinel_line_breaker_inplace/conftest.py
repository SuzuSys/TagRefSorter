from dataclasses import dataclass, field

import pytest
from pylatexenc.latexwalker import LatexEnvironmentNode, LatexMathNode, LatexNode, LatexWalker

from tagrefsorter.parser import ALIGNER

# Whether to add a sentinel line breaker
EXPECTED_RESULTS = [
    False,
    True,
]


@dataclass
class ExpectedCellResult:
    input: list[LatexNode] = field(default_factory=list)
    should_add: bool = False


@pytest.fixture(scope="session")
def eslbi_case(eslbi_cells, latex_context) -> list[ExpectedCellResult]:
    """Fixture that provides test cases for the _ensure_sentinel_line_breaker_inplace function.

    It pairs input LatexNode lists with expected boolean outputs.

    :return: List of ExpectedCellResult objects, each containing
    a list of LatexNode objects and a boolean output
    :rtype: list[ExpectedCellResult]
    """
    expected_results: list[ExpectedCellResult] = []
    for eslbi_case, exp in zip(eslbi_cells, EXPECTED_RESULTS, strict=True):
        latex_walker = LatexWalker(eslbi_case.source, latex_context=latex_context)
        root_math_block = latex_walker.get_latex_nodes(pos=0)[0]
        assert isinstance(root_math_block[0], LatexMathNode)  # Unexpected error check
        layer0_nodes: list[LatexNode] = root_math_block[0].nodelist
        aligner_node = next(
            (
                token
                for token in layer0_nodes
                if isinstance(token, LatexEnvironmentNode) and token.environmentname in ALIGNER
            ),
            None,
        )
        assert aligner_node is not None  # Unexpected error check
        expected_results.append(
            ExpectedCellResult(
                input=aligner_node.nodelist,
                should_add=exp,
            ),
        )
    return expected_results
