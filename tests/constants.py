import re

RE_BLOCK = re.compile(r"^\${2}([^$]*?)\${2}$", re.MULTILINE)
RE_INLINE = re.compile(r"^\$(\S[^$]*?[^\s\\]{1}?)\$$")
