import pytest
from markdown_it import MarkdownIt
from mdit_py_plugins.texmath import texmath_plugin


@pytest.fixture(scope="session")
def md_parser() -> MarkdownIt:
    """MarkdownIt parser with texmath plugin enabled."""
    md = MarkdownIt().use(texmath_plugin)
    md.block.ruler.disable("math_block_eqno")
    return md
