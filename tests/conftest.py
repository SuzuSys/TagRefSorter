import pytest
from markdown_it import MarkdownIt
from mdit_py_plugins.texmath import texmath_plugin
from pylatexenc.macrospec import LatexContextDb, MacroSpec
from pylatexenc.macrospec._argparsers import MacroStandardArgsParser


@pytest.fixture(scope="session")
def md_parser() -> MarkdownIt:
    """MarkdownIt parser with texmath plugin enabled."""
    md = MarkdownIt().use(texmath_plugin)
    md.block.ruler.disable("math_block_eqno")
    return md


@pytest.fixture(scope="session")
def latex_context() -> LatexContextDb:
    """LatexContextDb with custom tag macro specifications."""
    tag_spec = MacroSpec("tag", MacroStandardArgsParser("*{"))
    latex_context = LatexContextDb()
    latex_context.add_context_category(None, macros=[tag_spec], prepend=True)
    return latex_context
