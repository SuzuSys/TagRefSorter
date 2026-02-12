from collections.abc import Iterable

from ._argparsers import MacroStandardArgsParser as MacroStandardArgsParser
from ._argparsers import ParsedMacroArgs as ParsedMacroArgs

class MacroSpec:
    def __init__(self, macroname: str, args_parser: MacroStandardArgsParser = ...) -> None: ...

class LatexContextDb:
    def __init__(self) -> None: ...
    def add_context_category(
        self,
        category: str | None,
        macros: Iterable[MacroSpec] = [],
        prepend: bool = False,
    ) -> None: ...
