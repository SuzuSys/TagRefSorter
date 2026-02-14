from collections.abc import Callable

import pytest
from markdown_it import MarkdownIt
from markdown_it.token import Token
from nbformat import NotebookNode

_SEARCH_MATH_INLINE_FIXTURE_DIR = "tests/unit/_search_math_inline/smi_fixtures.ipynb"

EXPECTED_RESULTS = [
    [],
    [r"$x=y$"],
]


@pytest.fixture(scope="session")
def smi_case(
    md_parser: MarkdownIt,
    load_markdown_cells: Callable[[str], list[NotebookNode]],
) -> list[tuple[list[Token], list[str]]]:
    """Fixture that provides test cases for the _search_math_inline function.
    It parses the source of each cell in the smi_cells fixture using the md_parser
    and pairs it with the expected results.

    :return: List of tuples, where each tuple contains a list of Tokens
    and a list of expected math inline strings
    :rtype: list[tuple[list[Token], list[str]]]
    """
    smi_cells = load_markdown_cells(_SEARCH_MATH_INLINE_FIXTURE_DIR)
    return [
        (md_parser.parse(cell.source), expected)
        for cell, expected in zip(smi_cells, EXPECTED_RESULTS, strict=True)
    ]
