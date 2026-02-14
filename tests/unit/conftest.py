from collections.abc import Callable

import nbformat
import pytest
from pylatexenc.latexwalker import LatexEnvironmentNode, LatexMathNode, LatexNode, LatexWalker
from pylatexenc.macrospec import LatexContextDb

from tagrefsorter.parser import ALIGNER
from tests.constants import RE_BLOCK, RE_INLINE


@pytest.fixture(scope="session")
def load_markdown_cells() -> Callable[[str], list[nbformat.NotebookNode]]:
    """
    Factory fixture that returns a function to load markdown cells from a Jupyter notebook.

    :return: Function that takes a file path and returns a list of markdown cells
    :rtype: Callable[[str], list[nbformat.NotebookNode]]
    """

    def _loader(path: str) -> list[nbformat.NotebookNode]:
        nb = nbformat.read(path, as_version=4)
        return [cell for cell in nb.cells if cell.cell_type == "markdown"]

    return _loader


@pytest.fixture(scope="session")
def get_layer0_nodes(latex_context: LatexContextDb) -> Callable[[str], list[LatexNode]]:
    """
    Factory fixture that returns a function to parse LaTeX content and return the layer 0 nodes.

    :return: Function that takes LaTeX content and returns a list of layer 0 nodes
    :rtype: Callable[[str], list[LatexNode]]
    """

    def _getter(content: str) -> list[LatexNode]:
        assert RE_BLOCK.fullmatch(content) or RE_INLINE.fullmatch(content)
        latex_walker = LatexWalker(content, latex_context=latex_context)
        root_math_block = latex_walker.get_latex_nodes(pos=0)[0]
        assert isinstance(root_math_block[0], LatexMathNode)  # Unexpected error check
        return root_math_block[0].nodelist

    return _getter


@pytest.fixture(scope="session")
def get_aligner_contents(
    get_layer0_nodes: Callable[[str], list[LatexNode]],
) -> Callable[[str], list[LatexNode]]:
    """
    Factory fixture that returns a function
      to extract the contents of an aligner environment from LaTeX content.

    :return: Function that
      takes LaTeX content and returns a list of nodes within the aligner environment
    :rtype: Callable[[str], list[LatexNode]]
    """

    def _getter(content: str) -> list[LatexNode]:
        layer0_nodes: list[LatexNode] = get_layer0_nodes(content)
        aligner_node = next(
            (
                token
                for token in layer0_nodes
                if isinstance(token, LatexEnvironmentNode) and token.environmentname in ALIGNER
            ),
            None,
        )
        assert aligner_node is not None  # Unexpected error check
        return aligner_node.nodelist

    return _getter
