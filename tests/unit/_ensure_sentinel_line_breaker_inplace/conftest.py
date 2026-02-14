from collections.abc import Callable

import pytest
from nbformat import NotebookNode

from .test_eslbi import ExpectedCellResult, LatexNode

_ENSURE_SENTINEL_LINE_BREAKER_INPLACE_FIXTURE_DIR = (
    "tests/unit/_ensure_sentinel_line_breaker_inplace/eslbi_fixtures.ipynb"
)

# Whether to add a sentinel line breaker
EXPECTED_RESULTS = [
    False,
    True,
]


@pytest.fixture(scope="session")
def eslbi_case(
    load_markdown_cells: Callable[[str], list[NotebookNode]],
    get_aligner_contents: Callable[[str], list[LatexNode]],
) -> list[ExpectedCellResult]:
    """Fixture that provides test cases for the _ensure_sentinel_line_breaker_inplace function.

    It pairs input LatexNode lists with expected boolean outputs.

    :return: List of ExpectedCellResult objects, each containing
    a list of LatexNode objects and a boolean output
    :rtype: list[ExpectedCellResult]
    """
    eslbi_cells = load_markdown_cells(_ENSURE_SENTINEL_LINE_BREAKER_INPLACE_FIXTURE_DIR)
    expected_results: list[ExpectedCellResult] = []
    for eslbi_case, exp in zip(eslbi_cells, EXPECTED_RESULTS, strict=True):
        aligner_contents: list[LatexNode] = get_aligner_contents(eslbi_case.source)
        expected_results.append(
            ExpectedCellResult(
                input=aligner_contents,
                should_add=exp,
            ),
        )
    return expected_results
