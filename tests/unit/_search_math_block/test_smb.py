from dataclasses import dataclass, field

from markdown_it.token import Token
from pylatexenc.latexwalker import (
    LatexCharsNode,
    LatexCommentNode,
    LatexEnvironmentNode,
    LatexMacroNode,
    LatexMathNode,
    LatexNode,
)

from tagrefsorter import parser


@dataclass
class ExpectedCellResult:
    input: list[Token] = field(default_factory=list)
    output: list[parser.MathBlock] = field(default_factory=list)


def _compare_math_nodes(actual: LatexMathNode, expected: LatexMathNode) -> None:
    for act_node, exp_node in zip(actual.nodelist, expected.nodelist, strict=True):
        compare_latex_nodes(act_node, exp_node)


def _compare_chars_nodes(actual: LatexCharsNode, expected: LatexCharsNode) -> None:
    assert actual.chars == expected.chars


def _compare_comment_nodes(actual: LatexCommentNode, expected: LatexCommentNode) -> None:
    assert actual.comment == expected.comment


def _compare_macro_nodes(actual: LatexMacroNode, expected: LatexMacroNode) -> None:
    assert actual.macroname == expected.macroname
    assert type(actual.nodeargd.argnlist) is type(expected.nodeargd.argnlist)
    if actual.nodeargd.argnlist is None and expected.nodeargd.argnlist is None:
        return
    for act_node, exp_node in zip(
        actual.nodeargd.argnlist,
        expected.nodeargd.argnlist,
        strict=True,
    ):
        assert type(act_node) is type(exp_node)
        if act_node is None and exp_node is None:
            continue
        compare_latex_nodes(act_node, exp_node)


def _compare_environment_nodes(
    actual: LatexEnvironmentNode,
    expected: LatexEnvironmentNode,
) -> None:
    assert actual.environmentname == expected.environmentname
    for act_node, exp_node in zip(actual.nodelist, expected.nodelist, strict=True):
        compare_latex_nodes(act_node, exp_node)


def compare_latex_nodes(actual: LatexNode, expected: LatexNode) -> None:
    assert type(actual) is type(expected)
    assert actual.pos == expected.pos
    assert actual.len == expected.len

    if isinstance(actual, LatexMathNode) and isinstance(expected, LatexMathNode):
        _compare_math_nodes(actual, expected)
    elif isinstance(actual, LatexCharsNode) and isinstance(expected, LatexCharsNode):
        _compare_chars_nodes(actual, expected)
    elif isinstance(actual, LatexCommentNode) and isinstance(expected, LatexCommentNode):
        _compare_comment_nodes(actual, expected)
    elif isinstance(actual, LatexMacroNode) and isinstance(expected, LatexMacroNode):
        _compare_macro_nodes(actual, expected)
    elif isinstance(actual, LatexEnvironmentNode) and isinstance(expected, LatexEnvironmentNode):
        _compare_environment_nodes(actual, expected)


def test_smb(smb_case: list[ExpectedCellResult]) -> None:
    tag_renumberer = parser.TagRenumberer()
    for expected_cell_result in smb_case:
        math_blocks = tag_renumberer._search_math_block(expected_cell_result.input)
        for math_block, exp in zip(math_blocks, expected_cell_result.output, strict=True):
            assert math_block.content == exp.content
            for math_node, exp_node in zip(math_block.layer0_nodes, exp.layer0_nodes, strict=True):
                compare_latex_nodes(math_node, exp_node)
