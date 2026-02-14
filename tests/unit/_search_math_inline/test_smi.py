from markdown_it.token import Token

from tagrefsorter import parser


def test_smi(smi_case: list[tuple[list[Token], list[str]]]) -> None:
    tag_renumberer = parser.TagRenumberer()
    for source, expected in smi_case:
        math_inlines = tag_renumberer._search_math_inline(source)
        for math_inline, exp in zip(math_inlines, expected, strict=True):
            assert math_inline == exp
