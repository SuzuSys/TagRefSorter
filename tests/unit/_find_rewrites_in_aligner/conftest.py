from collections.abc import Callable

import pytest
from nbformat import NotebookNode

from .test_fria import CellResultSpec, InsertionSpecData, LatexNode, ReplacementSpecData

_FIND_REWRITES_IN_ALIGNER_FIXTURE_DIR = "tests/unit/_find_rewrites_in_aligner/fria_fixtures.ipynb"


REWRITE_SPECS: list[list[InsertionSpecData | ReplacementSpecData]] = [
    [InsertionSpecData(line_label="\na &= b ")],
    [ReplacementSpecData(tag="\\tag 1", label="1")],
]


# Note: 1 Cell = 1 math block = 1 Environment(ALIGNER)
@pytest.fixture(scope="session")
def fria_case(
    load_markdown_cells: Callable[[str], list[NotebookNode]],
    get_aligner_contents: Callable[[str], list[LatexNode]],
) -> list[CellResultSpec]:
    """Fixture that provides test cases for the _find_rewrites_in_aligner function.

    It pairs input LatexNode lists with expected output Rewrite lists.

    :return: List of ExpectedCellResult objects, each containing
    a list of LatexNode objects and a list of Rewrite objects
    :rtype: list[ExpectedCellResult]
    """
    fria_cells = load_markdown_cells(_FIND_REWRITES_IN_ALIGNER_FIXTURE_DIR)
    expected_results: list[CellResultSpec] = []
    for fria_cell, specs in zip(fria_cells, REWRITE_SPECS, strict=True):
        aligner_contents: list[LatexNode] = get_aligner_contents(fria_cell.source)
        expected_results.append(
            CellResultSpec(
                content=fria_cell.source,
                input=aligner_contents,
                specs=specs,
            ),
        )
    return expected_results
