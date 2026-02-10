import pytest
from markdown_it.token import Token

EXPECTED_RESULTS = [
    [],
    [r"$$x\tag 1$$"],
]

@pytest.fixture
def smb_case(md_parser, smb_cells) -> list[tuple[list[Token], list[str]]]:
    """
    Fixture that provides test cases for the _search_math_block function. 
    It parses the source of each cell in the smb_cells fixture using the md_parser
    and pairs it with the expected results.
    
    :param md_parser: MarkdownIt parser with texmath plugin enabled
    :type md_parser: MarkdownIt
    :param smb_cells: List of notebook cells loaded from the fixture file
    :type smb_cells: list[NotebookNode]
    :return: List of tuples, where each tuple contains a list of Tokens and a list of expected math block strings
    :rtype: list[tuple[list[Token], list[str]]]
    """
    return [(md_parser.parse(cell.source), EXPECTED_RESULTS[i]) for i, cell in enumerate(smb_cells)]

