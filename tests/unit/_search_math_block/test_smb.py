from tagrefsorter import parser


def test_smb(smb_case):
    tag_renumberer = parser.TagRenumberer()
    for source, expected in smb_case:
        math_blocks = tag_renumberer._search_math_block(source)
        assert all(
            math_block[1] == exp for math_block, exp in zip(math_blocks, expected, strict=True)
        )
