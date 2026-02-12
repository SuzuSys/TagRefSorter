from typing import Literal

from pylatexenc.macrospec import LatexContextDb
from pylatexenc.macrospec._argparsers import ParsedMacroArgs

class LatexNode:
    pos: int
    len: int
    def __init__(self) -> None: ...

class LatexCharsNode(LatexNode):
    chars: str
    def __init__(self, chars: str) -> None: ...

class LatexCommentNode(LatexNode):
    comment: str
    def __init__(self, comment: str) -> None: ...

class LatexMacroNode(LatexNode):
    macroname: str
    nodeargd: ParsedMacroArgs
    def __init__(self, macroname: str) -> None: ...

class LatexEnvironmentNode(LatexNode):
    environmentname: str
    nodelist: list[LatexNode]
    def __init__(self, environmentname: str, nodelist: list[LatexNode]) -> None: ...

class LatexMathNode(LatexNode):
    nodelist: list[LatexNode]
    def __init__(
        self,
        displaytype: Literal["inline", "display"],
        nodelist: list[LatexNode] = [],
    ) -> None: ...

class LatexWalker:
    def __init__(self, s: str, latex_context: LatexContextDb | None = None) -> None: ...
    def get_latex_nodes(self, pos: int = 0) -> tuple[list[LatexNode], int, int]: ...
