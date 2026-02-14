from dataclasses import dataclass, field

from pylatexenc.latexwalker import LatexNode

from tagrefsorter.parser import Insertion, Replacement, TagRenumberer


@dataclass
class SingleLineInsertionSpecData:
    pass


@dataclass
class ReplacementSpecData:
    tag: str
    label: str
    nth: int = 1


@dataclass
class CellResultSpec:
    content: str
    input: list[LatexNode]
    specs: list[SingleLineInsertionSpecData | ReplacementSpecData] = field(default_factory=list)


def find_nth(s: str, sub: str, n: int) -> int:
    pos = -1
    for _ in range(n):
        pos = s.index(sub, pos + 1)
    return pos


def assert_single_line_insertion(content: str, act: Insertion) -> None:
    assert act.start == len(content) - 2
    assert act.length == 0


def assert_replacement(content: str, act: Replacement, spec: ReplacementSpecData) -> None:
    # tag start pos
    pos = find_nth(content, spec.tag, spec.nth)
    assert act.start == pos
    # tag length
    assert act.length == len(spec.tag)
    # range of act.label_start
    assert act.start + 4 <= act.label_start  # 4 = len(r"\tag")
    assert act.label_start < act.start + act.length
    # range of act.label_length
    assert act.label_length + 4 <= act.length
    # labels match
    act_label = content[act.label_start : act.label_start + act.label_length]
    assert act_label.strip() == spec.label.strip()


def test_frisl(frisl_case: list[CellResultSpec]) -> None:
    tag_renumberer = TagRenumberer()
    for case in frisl_case:
        rewrites = tag_renumberer._find_rewrite_in_single_line(case.input)
        for rewrite, spec in zip(rewrites, case.specs, strict=True):
            if isinstance(spec, SingleLineInsertionSpecData):
                assert isinstance(rewrite, Insertion)
                assert_single_line_insertion(case.content, rewrite)
            else:
                assert isinstance(rewrite, Replacement)
                assert_replacement(case.content, rewrite, spec)
