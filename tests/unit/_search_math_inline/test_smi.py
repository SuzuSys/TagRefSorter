from tagrefsorter import parser
def test_smi(smi_case):
    tag_renumberer = parser.TagRenumberer()
    for source, expected in smi_case:
        math_inlines = tag_renumberer._search_math_inline(source)
        assert all(math_inline == exp for math_inline, exp in zip(math_inlines, expected))