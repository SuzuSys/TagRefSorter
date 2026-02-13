from pylatexenc.latexwalker import LatexNode

class ParsedMacroArgs:
    argnlist: list[LatexNode]
    def __init__(
        self,
        argnlist: list[LatexNode | None] | None = None,
        argspec: str = "",
    ) -> None: ...
    def to_json_object(self) -> dict: ...

class MacroStandardArgsParser:
    def __init__(
        self,
        argspec: str | None = None,
        optional_arg_no_space: bool = False,
        args_math_mode: list[bool | None] | None = None,
        **kwargs: object,
    ) -> None: ...
