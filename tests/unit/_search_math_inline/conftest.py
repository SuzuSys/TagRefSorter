import pytest
from markdown_it.token import Token

EXPECTED_RESULTS = [
    [],
    [r"$x=y$"],
]


@pytest.fixture
def smi_case(md_parser, smi_cells) -> list[tuple[list[Token], list[str]]]:
    """Fixture that provides test cases for the _search_math_inline function.
    It parses the source of each cell in the smi_cells fixture using the md_parser
    and pairs it with the expected results.

    :param md_parser: MarkdownIt parser with texmath plugin enabled
    :type md_parser: MarkdownIt
    :param smi_cells: List of notebook cells loaded from the fixture file
    :type smi_cells: list[NotebookNode]
    :return: List of tuples, where each tuple contains a list of Tokens
    and a list of expected math inline strings
    :rtype: list[tuple[list[Token], list[str]]]
    """
    return [(md_parser.parse(cell.source), EXPECTED_RESULTS[i]) for i, cell in enumerate(smi_cells)]
