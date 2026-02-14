import logging
from dataclasses import dataclass

from markdown_it import MarkdownIt
from markdown_it.token import Token
from mdit_py_plugins.texmath import texmath_plugin
from pylatexenc.latexwalker import (
    LatexCharsNode,
    LatexCommentNode,
    LatexEnvironmentNode,
    LatexMacroNode,
    LatexMathNode,
    LatexNode,
    LatexWalker,
)
from pylatexenc.macrospec import LatexContextDb, MacroSpec, MacroStandardArgsParser

logger = logging.getLogger(__name__)

ALIGNER = ["align", "alignat", "gather"]
""" environments that each line has its own number """

LINE_BREAKER = ["\\", "newline"]


@dataclass
class Rewrite:
    start: int
    length: int


@dataclass
class Insertion(Rewrite):
    length: int = 0


@dataclass
class Replacement(Rewrite):
    label_start: int
    label_length: int


@dataclass
class MathBlock:
    content: str
    layer0_nodes: list[LatexNode]


class TagRenumberer:
    def __init__(self) -> None:
        self.update_map: dict[str, str] = {}
        self.next_tag: int = 1
        self.md = MarkdownIt().use(texmath_plugin)
        self.md.block.ruler.disable("math_block_eqno")  # disable eqno parsing like "$$...$$ (1)"
        tag_spec = MacroSpec("tag", MacroStandardArgsParser("*{"))
        self.latex_context = LatexContextDb()
        # note: The LatexContextDb instance is meant to be (pseudo-)immutable.
        self.latex_context.add_context_category(None, macros=[tag_spec], prepend=True)

    def renumber_tags(self, text: str) -> str:
        """Renumber tags.

        Args:
            text (str): text of a markdown cell
        Returns:
            str: updated text

        """
        tokens = self.md.parse(text)
        math_blocks: list[MathBlock] = self._search_math_block(tokens)
        split_text: list[str] = []
        pos = 0
        for math_block in math_blocks:
            layer0_nodes = math_block.layer0_nodes
            content = math_block.content
            rewrites: list[Rewrite] = []
            aligner_node = next(
                (
                    token
                    for token in layer0_nodes
                    if isinstance(token, LatexEnvironmentNode) and token.environmentname in ALIGNER
                ),
                None,
            )
            if aligner_node:
                # process each line in aligner environment
                nodes = aligner_node.nodelist
                self._ensure_sentinel_line_breaker_inplace(nodes)
                rewrites = self._find_rewrites_in_aligner(nodes)
            else:
                # process single line math block
                rewrites = self._find_rewrite_in_single_line(layer0_nodes)
            # apply replacements in reverse order
            out: list[str] = []
            cur = 0
            for rep in rewrites:
                out.append(content[cur : rep.start])
                out.append(rf"\tag{{{self.next_tag}}}")
                if isinstance(rep, Replacement):
                    old_tag = (
                        content[rep.label_start : rep.label_start + rep.label_length]
                        .strip()
                        .removeprefix("{")
                        .removesuffix("}")
                        .strip()
                    )
                    if len(old_tag) > 0:
                        self.update_map[old_tag] = str(self.next_tag)
                self.next_tag += 1
                cur = rep.start + rep.length
            out.append(content[cur:])
            # reconstruct math block
            new_block = "".join(out)
            # replace in text
            idx = text.find(content, pos)
            split_text.append(text[pos:idx])
            split_text.append(new_block)
            pos = idx + len(content)
        split_text.append(text[pos:])
        return "".join(split_text)

    def renumber_refs(self, text: str) -> str:
        """Renumber refs.

        Args:
            text (str): text of a markdown cell
        Returns:
            str: updated text

        """
        tokens: list[Token] = self.md.parse(text)
        inlines: list[str] = self._search_math_inline(tokens)
        split_text: list[str] = []
        pos = 0
        for inline in inlines:
            if inline[:2] == "$(" and inline[-2:] == ")$":
                label = inline.strip("$").removeprefix("(").removesuffix(")").strip()
                if label in self.update_map:
                    new_label = self.update_map[label]
                    new_inline = rf"$({new_label})$"
                    idx = text.find(inline, pos)
                    split_text.append(text[pos:idx])
                    split_text.append(new_inline)
                    pos = idx + len(inline)
        split_text.append(text[pos:])
        return "".join(split_text)

    def _search_math_block(self, tokens: list[Token]) -> list[MathBlock]:
        """Search math_block tokens recursively.

        1. If token type is "math_block", append its content to results.
        2. If token has children, search children recursively.
        3. Return results.

        Args:
            tokens (list[Token]): List of tokens to search.

        Returns:
            list[tuple[list[LatexNode], str]]: List of tuples of
            LaTeX nodes and their original content.

        """
        results: list[MathBlock] = []
        for token in tokens:
            if token.type == "math_block":
                content = f"$${token.content}$$"
                latex_walker = LatexWalker(content, latex_context=self.latex_context)
                root_math_block = latex_walker.get_latex_nodes(pos=0)[0]
                if not isinstance(root_math_block[0], LatexMathNode):
                    logger.warning(
                        "Unexpected structure in math block. The content of token: %s",
                        token.content,
                    )
                    continue
                layer0_nodes: list[LatexNode] = root_math_block[0].nodelist
                results.append(MathBlock(layer0_nodes=layer0_nodes, content=f"$${token.content}$$"))
            elif token.children:
                results += self._search_math_block(token.children)
        return results

    def _search_math_inline(self, tokens: list[Token]) -> list[str]:
        """Search math_inline tokens recursively.

        1. If token type is "math_inline", append its content to results.
        2. If token has children, search children recursively.
        3. Return results.

        Args:
            tokens (list[Token]): List of tokens to search.

        Returns:
            list[str]: List of math inline contents.

        """
        results: list[str] = []
        for token in tokens:
            if token.type == "math_inline":
                results.append(f"${token.content}$")
            elif token.children:
                results += self._search_math_inline(token.children)
        return results

    def _ensure_sentinel_line_breaker_inplace(self, nodes: list[LatexNode]) -> None:
        """Add a line breaker node with a sentinel value.

        In the ALIGNER environment, a line breaker is placed at the end of the final line
        as a sentinel, enabling uniform processing of all lines.

        Args:
            nodes (list[LatexNode]): List of LaTeX nodes in ALIGNER environment.

        """
        need_sentinel = False
        for item in reversed(nodes):
            if isinstance(item, LatexMacroNode):
                if item.macroname in LINE_BREAKER:
                    # sentinel found
                    break
                if item.macroname in {"tag", "notag"}:
                    # ignore tag, tag*, and notag macros
                    continue
                need_sentinel = True
                break
            if isinstance(item, LatexCommentNode):
                # ignore comments
                continue
            if isinstance(item, LatexCharsNode) and item.chars.strip() == "":
                # ignore whitespace
                continue
            need_sentinel = True
            break
        if need_sentinel:
            # add sentinel line breaker
            nodes.append(LatexMacroNode(macroname="\\"))

    def _find_rewrites_in_aligner(self, nodes: list[LatexNode]) -> list[Rewrite]:
        """Find all tag replacements and insertion in the ALIGNER environment.

        Args:
            nodes (list[LatexNode]): List of LaTeX nodes in ALIGNER environment.
                (sentinel line breaker is assumed to be present.)

        Returns:
            list[Rewrite]: List of Rewrite objects.

        """
        rewrites: list[Rewrite] = []
        exist_tag: bool = False
        exist_notag: bool = False
        tag: LatexMacroNode | None = None
        for item in nodes:
            if not isinstance(item, LatexMacroNode):
                continue
            if item.macroname in LINE_BREAKER:
                if tag:
                    # update tag
                    argnlist = tag.nodeargd.argnlist
                    # argnlist[1]: first argument
                    label_start = argnlist[1].pos
                    label_length = argnlist[-1].pos - label_start + argnlist[-1].len
                    rewrites.append(
                        Replacement(
                            start=tag.pos,
                            length=tag.len,
                            label_start=label_start,
                            label_length=label_length,
                        ),
                    )
                elif not (exist_tag or exist_notag):  # exist_tag mean tag* found
                    # add tag
                    rewrites.append(
                        Insertion(
                            start=item.pos,
                        ),
                    )
                # reset for next line
                exist_tag = False
                exist_notag = False
                tag = None
            elif not exist_tag:
                if item.macroname == "tag":
                    # tag found
                    exist_tag = True
                    # judge either tag or tag*
                    # argnlist[0]: optional '*'
                    star = item.nodeargd.argnlist[0]
                    if not (isinstance(star, LatexCharsNode) and star.chars == "*"):
                        # tag, not tag*
                        tag = item

                elif item.macroname == "notag":
                    # notag found
                    exist_notag = True
        return rewrites

    def _find_rewrite_in_single_line(self, nodes: list[LatexNode]) -> list[Rewrite]:
        """Find a tag replacement or a insertion in a single line math block.

        Args:
            nodes (list[LatexNode]): List of LaTeX nodes in the math block.

        Returns:
            list[Replacement]: List of Replacement objects. (length is 0 or 1)

        """
        no_need_tag = False
        for item in reversed(nodes):
            if not isinstance(item, LatexMacroNode):
                continue
            if item.macroname == "notag":
                no_need_tag = True
            elif item.macroname == "tag":
                no_need_tag = True
                # judge either tag or tag*
                # argnlist[0]: optional '*'
                star = item.nodeargd.argnlist[0]
                if not (isinstance(star, LatexCharsNode) and star.chars == "*"):
                    # tag, not tag*
                    argnlist = item.nodeargd.argnlist
                    label_start = argnlist[1].pos
                    label_length = argnlist[-1].pos - label_start + argnlist[-1].len
                    return [
                        Replacement(
                            start=item.pos,
                            length=item.len,
                            label_start=label_start,
                            label_length=label_length,
                        ),
                    ]
        if not no_need_tag:
            # add tag
            return [
                Insertion(
                    start=nodes[-1].pos + nodes[-1].len,
                ),
            ]
        return []
