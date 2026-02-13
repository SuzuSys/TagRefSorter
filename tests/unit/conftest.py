import nbformat
import pytest

_SEARCH_MATH_BLOCK_FIXTURE_DIR = "tests/unit/_search_math_block/smb_fixtures.ipynb"
_SEARCH_MATH_INLINE_FIXTURE_DIR = "tests/unit/_search_math_inline/smi_fixtures.ipynb"
_ENSURE_SENTINEL_LINE_BREAKER_INPLACE_FIXTURE_DIR = (
    "tests/unit/_ensure_sentinel_line_breaker_inplace/eslbi_fixtures.ipynb"
)


@pytest.fixture(scope="session")
def smb_cells() -> list[nbformat.NotebookNode]:
    """Load notebook cells from the specified fixture file.
    Cells that type is 'markdown' are returned. Cells that type is 'cell' are ignored.
    """
    nb = nbformat.read(_SEARCH_MATH_BLOCK_FIXTURE_DIR, as_version=4)
    return [cell for cell in nb.cells if cell.cell_type == "markdown"]


@pytest.fixture(scope="session")
def smi_cells() -> list[nbformat.NotebookNode]:
    """Load notebook cells from the specified fixture file.
    Cells that type is 'markdown' are returned. Cells that type is 'cell' are ignored.
    """
    nb = nbformat.read(_SEARCH_MATH_INLINE_FIXTURE_DIR, as_version=4)
    return [cell for cell in nb.cells if cell.cell_type == "markdown"]


@pytest.fixture(scope="session")
def eslbi_cells() -> list[nbformat.NotebookNode]:
    """Load notebook cells from the specified fixture file.
    Cells that type is 'markdown' are returned. Cells that type is 'cell' are ignored.
    """
    nb = nbformat.read(_ENSURE_SENTINEL_LINE_BREAKER_INPLACE_FIXTURE_DIR, as_version=4)
    return [cell for cell in nb.cells if cell.cell_type == "markdown"]
