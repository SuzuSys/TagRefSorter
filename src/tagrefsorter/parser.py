#!/usr/bin/env python3

from pylatexenc.latexwalker import LatexWalker, LatexEnvironmentNode, LatexMacroNode, LatexNode, LatexMathNode, LatexCommentNode, LatexCharsNode
from pylatexenc.macrospec import MacroSpec, LatexContextDb, MacroStandardArgsParser
from markdown_it import MarkdownIt
from markdown_it.token import Token
from mdit_py_plugins.texmath import texmath_plugin
from dataclasses import dataclass

ALIGNER = ['align', 'alignat', 'gather']
""" environments that each line has its own number """

LINE_BREAKER = ["\\", "newline"]

@dataclass
class Replacement:
    start: int
    length: int
    label_start: int | None = None # if length > 0, specify label position
    label_length: int | None = None # if length > 0, specify label length

class TagRenumberer:
    def __init__(self):
        self.update_map: dict[str, str] = {}
        self.next_tag: int = 1
        self.md = MarkdownIt().use(texmath_plugin)
        self.md.block.ruler.disable('math_block_eqno') # disable eqno parsing like "$$...$$ (1)"
    
    def renumber_tags(self, text: str) -> str:
        """
        Renumber tags.

        Args:
            text (str): text of a markdown cell
        Returns:
            str: updated text
        """
        tokens = self.md.parse(text)
        math_blocks: list[str] = self._search_math_block(tokens)
        for block in math_blocks:
            tag_spec = MacroSpec('tag', MacroStandardArgsParser('*{'))
            latex_context = LatexContextDb() # note: The LatexContextDb instance is meant to be (pseudo-)immutable.
            latex_context.add_context_category('custom', prepend=True, macros=[tag_spec])
            latex_walker = LatexWalker(block, latex_context=latex_context)
            root_math_block: list[LatexMathNode] = latex_walker.get_latex_nodes(pos=0)[0]
            layer0_nodes: list[LatexNode] = root_math_block[0].nodelist
            replacements: list[Replacement] = []
            aligner_node = next(
                (
                    token
                    for token in layer0_nodes
                    if isinstance(token, LatexEnvironmentNode)
                    and token.environmentname in ALIGNER
                ),
                None,
            )
            if aligner_node:
                # process each line in aligner environment
                nodes = aligner_node.nodelist
                self._ensure_sentinel_line_breaker_inplace(nodes)
                replacements = self._find_replacements_in_aligner(nodes)
            else:
                # process single line math block
                replacements = self._find_replacement_in_single_line(layer0_nodes)
            # apply replacements in reverse order
            out: list[str] = []
            cur = 0
            for rep in replacements:
                out.append(block[cur:rep.start])
                out.append(rf'\tag{{{self.next_tag}}}')
                if rep.length > 0:
                    old_tag = block[
                        rep.label_start : rep.label_start + rep.label_length # type: ignore
                    ].strip().removeprefix('{').removesuffix('}').strip()
                    if len(old_tag) > 0:
                        self.update_map[old_tag] = str(self.next_tag)
                self.next_tag += 1
                cur = rep.start + rep.length
            out.append(block[cur:])
            # reconstruct math block
            new_block = ''.join(out)
             # replace in text
            text = text.replace(block, new_block, 1)
        return text
    
    def renumber_refs(self, text: str) -> str:
        """
        Renumber refs.

        Args:
            text (str): text of a markdown cell
        Returns:
            str: updated text
        """
        tokens: list[Token] = self.md.parse(text)
        inlines: list[str] = self._search_math_inline(tokens)

        for inline in inlines:
            label = inline.strip('$').strip().removeprefix('(').removesuffix(')').strip()
            if label in self.update_map:
                new_label = self.update_map[label]
                new_inline = rf'$({new_label})'
                text = text.replace(inline, new_inline, 1)
        return text
    
    def _search_math_block(self, tokens: list[Token]) -> list[str]:
        """
        Search math_block tokens recursively.
        1. If token type is "math_block", append its content to results.
        2. If token has children, search children recursively.
        3. Return results.
        Args:
            tokens (list[Token]): List of tokens to search.
        Returns:
            list[str]: List of math block contents.
        """
        results: list[str] = []
        for token in tokens:
            if token.type == "math_block":
                results.append(f"$${token.content}$$")
            elif token.children:
                results += self._search_math_block(token.children)
        return results
    
    def _search_math_inline(self, tokens: list[Token]) -> list[str]:
        """
        Search math_inline tokens recursively.
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
        """
        Add a line breaker node with a sentinel value.

        In the ALIGNER environment, a line breaker is placed at the end of the final line as a sentinel, 
        enabling uniform processing of all lines.

        Args:
            nodes (list[LatexNode]): List of LaTeX nodes in ALIGNER environment.
        """
        need_sentinel = False
        for item in reversed(nodes):
            if isinstance(item, LatexMacroNode):
                if item.macroname in LINE_BREAKER:
                    # sentinel found
                    break
                elif item.macroname == 'tag' or item.macroname == 'notag':
                    # ignore tag, tag*, and notag macros
                    continue
                else:
                    need_sentinel = True
                    break
            elif isinstance(item, LatexCommentNode):
                # ignore comments
                continue
            elif isinstance(item, LatexCharsNode) and item.chars.strip() == '':
                # ignore whitespace
                continue
            else:
                need_sentinel = True
                break
        if need_sentinel:
            # add sentinel line breaker
            nodes.append(LatexMacroNode(macroname='\\'))
    
    def _find_replacements_in_aligner(self, nodes: list[LatexNode]) -> list[Replacement]:
        """
        Find all tag replacements in the ALIGNER environment.

        Args:
            nodes (list[LatexNode]): List of LaTeX nodes in ALIGNER environment. 
                (sentinel line breaker is assumed to be present.)
        Returns:
            list[Replacement]: List of Replacement objects.
        """
        replacements: list[Replacement] = []
        exist_tag: bool = False
        exist_notag: bool = False
        tag: LatexMacroNode | None = None
        for item in nodes:
            if not isinstance(item, LatexMacroNode):
                continue
            elif item.macroname in LINE_BREAKER:
                if tag:
                    # update tag
                    argnlist = tag.nodeargd.argnlist
                    # argnlist[1]: first argument
                    label_start = argnlist[1].pos  # type: ignore
                    label_length = argnlist[-1].pos - label_start + argnlist[-1].len  # type: ignore
                    replacements.append(
                        Replacement(
                            start=tag.pos, # type: ignore
                            length=tag.len, # type: ignore
                            label_start=label_start,
                            label_length=label_length,
                        )
                    )
                elif not (exist_tag or exist_notag): # exist_tag mean tag* found
                    # add tag
                    replacements.append(
                        Replacement(
                            start=item.pos, # type: ignore
                            length=0,
                        )
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
        return replacements
    
    def _find_replacement_in_single_line(self, nodes: list[LatexNode]) -> list[Replacement]:
        """
        Find a tag replacement in a single line math block.

        Args:
            nodes (list[LatexNode]): List of LaTeX nodes in the math block.
        Returns:
            list[Replacement]: List of Replacement objects. (length is 0 or 1)
        """
        no_need_tag = False
        for item in reversed(nodes):
            if not isinstance(item, LatexMacroNode):
                continue
            elif item.macroname == "notag":
                no_need_tag = True
            elif item.macroname == "tag":
                no_need_tag = True
                # judge either tag or tag*
                # argnlist[0]: optional '*'
                star = item.nodeargd.argnlist[0]
                if not (isinstance(star, LatexCharsNode) and star.chars == "*"):
                    # tag, not tag*
                    argnlist = item.nodeargd.argnlist
                    label_start = argnlist[1].pos  # type: ignore
                    label_length = argnlist[-1].pos - label_start + argnlist[-1].len  # type: ignore
                    return [
                        Replacement(
                            start=item.pos, # type: ignore
                            length=item.len, # type: ignore
                            label_start=label_start,
                            label_length=label_length,
                        )
                    ]
        if not no_need_tag:
            # add tag
            return [
                Replacement(
                    start=nodes[-1].pos + nodes[-1].len, # type: ignore
                    length=0,
                )
            ]
        return []