from collections.abc import Callable

import pytest
from nbformat import NotebookNode

from .test_fr import (
    AlignerCellResultSpec,
    AlignerInsertionSpecData,
    LatexNode,
    ReplacementSpecData,
    SingleLineCellResultSpec,
    SingleLineInsertionSpecData,
)

_FIND_REWRITE_IN_SINGLE_LINE_FIXTURE_DIR = "tests/unit/_find_rewrite/frisl_fixtures.ipynb"

_FIND_REWRITES_IN_ALIGNER_FIXTURE_DIR = "tests/unit/_find_rewrite/fria_fixtures.ipynb"


FRISL_SPECS: list[list[SingleLineInsertionSpecData | ReplacementSpecData]] = [
    [SingleLineInsertionSpecData()],
    [ReplacementSpecData(tag="\\tag 1", label="1")],
]

FRIA_SPECS: list[list[AlignerInsertionSpecData | ReplacementSpecData]] = [
    [AlignerInsertionSpecData(line_label="\na &= b ")],
    [ReplacementSpecData(tag="\\tag 1", label="1")],
]


# Note: 1 Cell = 1 math block
@pytest.fixture(scope="session")
def frisl_case(
    load_markdown_cells: Callable[[str], list[NotebookNode]],
    get_layer0_nodes: Callable[[str], list[LatexNode]],
) -> list[SingleLineCellResultSpec]:
    """Fixture that provides test cases for the _find_rewrite_in_single_line function."""
    frisl_cells = load_markdown_cells(_FIND_REWRITE_IN_SINGLE_LINE_FIXTURE_DIR)
    expected_results: list[SingleLineCellResultSpec] = []
    for fria_cell, specs in zip(frisl_cells, FRISL_SPECS, strict=True):
        aligner_contents: list[LatexNode] = get_layer0_nodes(fria_cell.source)
        expected_results.append(
            SingleLineCellResultSpec(
                content=fria_cell.source,
                input=aligner_contents,
                specs=specs,
            ),
        )
    return expected_results


# Note: 1 Cell = 1 math block = 1 Environment(ALIGNER)
@pytest.fixture(scope="session")
def fria_case(
    load_markdown_cells: Callable[[str], list[NotebookNode]],
    get_aligner_contents: Callable[[str], list[LatexNode]],
) -> list[AlignerCellResultSpec]:
    """Fixture that provides test cases for the _find_rewrites_in_aligner function."""
    fria_cells = load_markdown_cells(_FIND_REWRITES_IN_ALIGNER_FIXTURE_DIR)
    expected_results: list[AlignerCellResultSpec] = []
    for fria_cell, specs in zip(fria_cells, FRIA_SPECS, strict=True):
        aligner_contents: list[LatexNode] = get_aligner_contents(fria_cell.source)
        expected_results.append(
            AlignerCellResultSpec(
                content=fria_cell.source,
                input=aligner_contents,
                specs=specs,
            ),
        )
    return expected_results
