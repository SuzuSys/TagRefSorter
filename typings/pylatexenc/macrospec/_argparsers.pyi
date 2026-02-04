from _typeshed import Incomplete
from typing import Optional

from pylatexenc.latexwalker import LatexNode


def unicode(s): ...

class ParsedMacroArgs:
    argnlist: list[LatexNode]
    argspec: Incomplete
    legacy_nodeoptarg_nodeargs: Incomplete
    def __init__(self, argnlist=[], argspec: str = '', **kwargs) -> None: ...
    def to_json_object(self): ...

class MacroStandardArgsParser:
    argspec: Incomplete
    optional_arg_no_space: Incomplete
    args_math_mode: Incomplete
    def __init__(self, argspec: Optional[str] = None, optional_arg_no_space: bool = False, args_math_mode=None, **kwargs) -> None: ...
    def parse_args(self, w, pos, parsing_state=None): ...

class ParsedVerbatimArgs(ParsedMacroArgs):
    verbatim_text: Incomplete
    verbatim_delimiters: Incomplete
    def __init__(self, verbatim_chars_node, verbatim_delimiters=None, **kwargs) -> None: ...

class VerbatimArgsParser(MacroStandardArgsParser):
    verbatim_arg_type: Incomplete
    def __init__(self, verbatim_arg_type, **kwargs) -> None: ...
    def parse_args(self, w, pos, parsing_state=None): ...
