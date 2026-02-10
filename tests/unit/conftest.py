import pytest
import nbformat

_SEARCH_MATH_BLOCK_FIXTURE_DIR = "tests/unit/_search_math_block/smb_fixtures.ipynb"
_SEARCH_MATH_INLINE_FIXTURE_DIR = "tests/unit/_search_math_inline/smi_fixtures.ipynb"

@pytest.fixture(scope="session")
def smb_cells()-> list[nbformat.NotebookNode]:
    """Load notebook cells from the specified fixture file."""
    nb = nbformat.read(_SEARCH_MATH_BLOCK_FIXTURE_DIR, as_version=4)
    return nb.cells

@pytest.fixture(scope="session")
def smi_cells() -> list[nbformat.NotebookNode]:
    """Load notebook cells from the specified fixture file."""
    nb = nbformat.read(_SEARCH_MATH_INLINE_FIXTURE_DIR, as_version=4)
    return nb.cells