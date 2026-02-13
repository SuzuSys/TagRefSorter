from copy import deepcopy

from pylatexenc.latexwalker import LatexMacroNode

from tagrefsorter import parser


def test_eslbi(eslbi_case):
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
