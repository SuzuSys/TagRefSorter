from copy import deepcopy
from dataclasses import dataclass, field

from pylatexenc.latexwalker import LatexMacroNode, LatexNode

from tagrefsorter import parser


@dataclass
class ExpectedCellResult:
    input: list[LatexNode] = field(default_factory=list)
    should_add: bool = False


def test_eslbi(eslbi_case: list[ExpectedCellResult]) -> None:
    tag_renumberer = parser.TagRenumberer()
    for case in eslbi_case:
        input_copy = deepcopy(case.input)
        tag_renumberer._ensure_sentinel_line_breaker_inplace(
            nodes=input_copy,
        )
        assert case.should_add == (len(input_copy) == len(case.input) + 1)
        if case.should_add:
            assert isinstance(input_copy[-1], LatexMacroNode)
            assert input_copy[-1].macroname == "\\"
