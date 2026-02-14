from collections.abc import Callable

import pytest
from nbformat import NotebookNode

from .test_frisl import CellResultSpec, LatexNode, ReplacementSpecData, SingleLineInsertionSpecData

_FIND_REWRITE_IN_SINGLE_LINE_FIXTURE_DIR = (
    "tests/unit/_find_rewrite_in_single_line/frisl_fixtures.ipynb"
)


REWRITE_SPECS: list[list[SingleLineInsertionSpecData | ReplacementSpecData]] = [
    [SingleLineInsertionSpecData()],
    [ReplacementSpecData(tag="\\tag 1", label="1")],
]


# Note: 1 Cell = 1 math block
@pytest.fixture(scope="session")
def frisl_case(
    load_markdown_cells: Callable[[str], list[NotebookNode]],
    get_layer0_nodes: Callable[[str], list[LatexNode]],
) -> list[CellResultSpec]:
    """Fixture that provides test cases for the _find_rewrite_in_aligner function.

    It pairs input LatexNode lists with expected output Rewrite lists.

    :return: List of ExpectedCellResult objects, each containing
    a list of LatexNode objects and a list of Rewrite objects
    :rtype: list[ExpectedCellResult]
    """
    frisl_cells = load_markdown_cells(_FIND_REWRITE_IN_SINGLE_LINE_FIXTURE_DIR)
    expected_results: list[CellResultSpec] = []
    for fria_cell, specs in zip(frisl_cells, REWRITE_SPECS, strict=True):
        aligner_contents: list[LatexNode] = get_layer0_nodes(fria_cell.source)
        expected_results.append(
            CellResultSpec(
                content=fria_cell.source,
                input=aligner_contents,
                specs=specs,
            ),
        )
    return expected_results
