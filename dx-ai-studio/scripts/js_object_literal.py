"""JS object literal parser: the minimum needed to read the i18n dictionaries.

The dictionaries are JS literals of the form `window._DX_I18N_DICT = { ... };`, so json cannot
read them, and node is not available here. The grammar needed is narrow (string keys, string
values, one level of nesting, trailing commas, line/block comments), so it is parsed directly.

Source spans of the values are returned too: to report "what differs" instead of overwriting
existing entries, a migration needs the original positions.
"""
from __future__ import annotations


class JSParseError(ValueError):
    pass


_WS = " \t\r\n"


class _Reader:
    def __init__(self, text: str, pos: int = 0) -> None:
        self.s = text
        self.i = pos

    def skip(self) -> None:
        s, n = self.s, len(self.s)
        while self.i < n:
            c = s[self.i]
            if c in _WS:
                self.i += 1
            elif s.startswith("//", self.i):
                nl = s.find("\n", self.i)
                self.i = n if nl < 0 else nl + 1
            elif s.startswith("/*", self.i):
                end = s.find("*/", self.i + 2)
                if end < 0:
                    raise JSParseError("unterminated block comment")
                self.i = end + 2
            else:
                return

    def expect(self, ch: str) -> None:
        self.skip()
        if self.i >= len(self.s) or self.s[self.i] != ch:
            got = self.s[self.i : self.i + 20] if self.i < len(self.s) else "<eof>"
            raise JSParseError(f"expected {ch!r} at {self.i}, got {got!r}")
        self.i += 1

    def string(self) -> str:
        self.skip()
        quote = self.s[self.i]
        if quote not in "'\"":
            raise JSParseError(f"expected string at {self.i}")
        self.i += 1
        out = []
        while True:
            if self.i >= len(self.s):
                raise JSParseError("unterminated string")
            c = self.s[self.i]
            if c == "\\":
                nxt = self.s[self.i + 1]
                out.append(
                    {"n": "\n", "t": "\t", "r": "\r"}.get(nxt, nxt)
                    if nxt != "u"
                    else chr(int(self.s[self.i + 2 : self.i + 6], 16))
                )
                self.i += 6 if nxt == "u" else 2
            elif c == quote:
                self.i += 1
                return "".join(out)
            else:
                out.append(c)
                self.i += 1

    def ident(self) -> str:
        self.skip()
        start = self.i
        while self.i < len(self.s) and (self.s[self.i].isalnum() or self.s[self.i] in "_$"):
            self.i += 1
        if start == self.i:
            raise JSParseError(f"expected identifier at {start}")
        return self.s[start : self.i]

    def key(self) -> str:
        self.skip()
        return self.string() if self.s[self.i] in "'\"" else self.ident()

    def value(self):
        self.skip()
        c = self.s[self.i]
        if c in "'\"":
            return self.string()
        if c == "{":
            return self.obj()
        if c == "[":
            return self.arr()
        start = self.i
        while self.i < len(self.s) and self.s[self.i] not in ",}]":
            self.i += 1
        raw = self.s[start : self.i].strip()
        return {"true": True, "false": False, "null": None}.get(raw, raw)

    def arr(self) -> list:
        self.expect("[")
        out = []
        while True:
            self.skip()
            if self.s[self.i] == "]":
                self.i += 1
                return out
            out.append(self.value())
            self.skip()
            if self.s[self.i] == ",":
                self.i += 1

    def obj(self) -> dict:
        self.expect("{")
        out: dict = {}
        while True:
            self.skip()
            if self.s[self.i] == "}":
                self.i += 1
                return out
            k = self.key()
            self.expect(":")
            out[k] = self.value()
            self.skip()
            if self.s[self.i] == ",":
                self.i += 1


def parse_object_after(text: str, marker: str) -> dict:
    """Return the first object literal after `marker` as a dict."""
    at = text.find(marker)
    if at < 0:
        raise JSParseError(f"marker {marker!r} not found")
    r = _Reader(text, at + len(marker))
    r.skip()
    while r.i < len(text) and text[r.i] != "{":
        r.i += 1
    return r.obj()


def object_span(text: str, marker: str) -> tuple[int, int]:
    """(start, end) indices of the object literal after `marker`. End is just past the '}'."""
    at = text.find(marker)
    if at < 0:
        raise JSParseError(f"marker {marker!r} not found")
    r = _Reader(text, at + len(marker))
    r.skip()
    while r.i < len(text) and text[r.i] != "{":
        r.i += 1
    start = r.i
    r.obj()
    return start, r.i


def value_spans(text: str, marker: str) -> dict[str, dict[str, tuple[int, int]]]:
    """For each dictionary entry, the (start, end) indices of each language value, quotes included.

    Rewriting a single value needs its position. Re-emitting the whole literal would lose the
    comments and the hand-tuned line breaks.
    """
    at = text.find(marker)
    if at < 0:
        raise JSParseError(f"marker {marker!r} not found")
    r = _Reader(text, at + len(marker))
    r.skip()
    while r.i < len(text) and text[r.i] != "{":
        r.i += 1
    r.expect("{")
    out: dict[str, dict[str, tuple[int, int]]] = {}
    while True:
        r.skip()
        if r.s[r.i] == "}":
            r.i += 1
            return out
        key = r.key()
        r.expect(":")
        r.skip()
        if r.s[r.i] == "{":
            r.expect("{")
            langs: dict[str, tuple[int, int]] = {}
            while True:
                r.skip()
                if r.s[r.i] == "}":
                    r.i += 1
                    break
                lang = r.key()
                r.expect(":")
                r.skip()
                start = r.i
                r.value()
                langs[lang] = (start, r.i)
                r.skip()
                if r.s[r.i] == ",":
                    r.i += 1
            out[key] = langs
        else:
            r.value()
        r.skip()
        if r.s[r.i] == ",":
            r.i += 1
