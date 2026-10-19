"""Tell comments from code in the studio's source (py, js, css, html, sh).

Used by scripts/comment_language_gate.py (no Korean in comments) and scripts/comment_only_diff.py (prove that a
rewrite changed comments only). The lexers are deliberately small but handle what the tree contains: strings with
URLs, regex literals, template literals with ${…}, CSS url(//…), inline <script>/<style>, shell quoting.
"""
from __future__ import annotations

import ast
import io
import re
import tokenize

KINDS = {".py": "py", ".js": "js", ".mjs": "js", ".css": "css", ".html": "html", ".htm": "html", ".sh": "sh"}

_REGEX_PREV = set("(,=:[!&|?{};+-*%~^<>")
_REGEX_KW = {"return", "typeof", "case", "do", "else", "in", "of", "new", "delete", "void", "throw", "yield", "await"}
_WORD = re.compile(r"[A-Za-z0-9_$\u0080-￿]+")


# ── JavaScript ──────────────────────────────────────────────────────────────

def _scan_template(s: str, i: int) -> int:
    """s[i] == '`'. Return the index after the closing backtick (nested ${…} skipped by brace depth)."""
    i += 1
    while i < len(s):
        c = s[i]
        if c == "\\":
            i += 2
            continue
        if c == "`":
            return i + 1
        if c == "$" and s.startswith("${", i):
            i += 2
            depth = 1
            while i < len(s) and depth:
                ch = s[i]
                if ch in "'\"":
                    i = _scan_string(s, i)
                    continue
                if ch == "`":
                    i = _scan_template(s, i)
                    continue
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                i += 1
            continue
        i += 1
    return i


def _scan_string(s: str, i: int) -> int:
    q = s[i]
    i += 1
    while i < len(s):
        c = s[i]
        if c == "\\":
            i += 2
            continue
        if c == q or c == "\n":
            return i + 1
        i += 1
    return i


def _scan_regex(s: str, i: int) -> int:
    i += 1
    in_class = False
    while i < len(s):
        c = s[i]
        if c == "\\":
            i += 2
            continue
        if c == "\n":
            return i
        if in_class:
            if c == "]":
                in_class = False
        elif c == "[":
            in_class = True
        elif c == "/":
            i += 1
            while i < len(s) and (s[i].isalpha()):
                i += 1
            return i
        i += 1
    return i


def _lex_js(s: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    i, prev = 0, None
    n = len(s)
    while i < n:
        c = s[i]
        if c.isspace():
            j = i
            while j < n and s[j].isspace():
                j += 1
            out.append(("ws", s[i:j]))
            i = j
            continue
        if s.startswith("//", i):
            j = s.find("\n", i)
            j = n if j == -1 else j
            out.append(("comment", s[i:j]))
            i = j
            continue
        if s.startswith("/*", i):
            j = s.find("*/", i + 2)
            j = n if j == -1 else j + 2
            out.append(("comment", s[i:j]))
            i = j
            continue
        if c in "'\"":
            j = _scan_string(s, i)
            out.append(("string", s[i:j]))
            prev, i = "str", j
            continue
        if c == "`":
            j = _scan_template(s, i)
            out.append(("string", s[i:j]))
            prev, i = "str", j
            continue
        if c == "/" and (prev is None or prev in _REGEX_PREV or prev in _REGEX_KW):
            j = _scan_regex(s, i)
            out.append(("string", s[i:j]))
            prev, i = "regex", j
            continue
        m = _WORD.match(s, i)
        if m:
            out.append(("code", m.group()))
            prev, i = m.group(), m.end()
            continue
        out.append(("code", c))
        prev, i = c, i + 1
    return out


# ── CSS ─────────────────────────────────────────────────────────────────────

def _lex_css(s: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c.isspace():
            j = i
            while j < n and s[j].isspace():
                j += 1
            out.append(("ws", s[i:j]))
            i = j
        elif s.startswith("/*", i):
            j = s.find("*/", i + 2)
            j = n if j == -1 else j + 2
            out.append(("comment", s[i:j]))
            i = j
        elif c in "'\"":
            j = _scan_string(s, i)
            out.append(("string", s[i:j]))
            i = j
        else:
            m = _WORD.match(s, i)
            if m:
                out.append(("code", m.group()))
                i = m.end()
            else:
                out.append(("code", c))
                i += 1
    return out


# ── HTML ────────────────────────────────────────────────────────────────────

_OPEN_RAW = re.compile(r"<(script|style)\b[^>]*>", re.I)


def _lex_html(s: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    i, n = 0, len(s)

    def text(chunk: str) -> None:
        for m in re.finditer(r"\s+|\S+", chunk):
            out.append(("ws" if m.group().isspace() else "code", m.group()))

    while i < n:
        c_at = s.find("<!--", i)
        r = _OPEN_RAW.search(s, i)
        nxt = min([p for p in (c_at, r.start() if r else -1) if p != -1], default=-1)
        if nxt == -1:
            text(s[i:])
            break
        text(s[i:nxt])
        if nxt == c_at:
            j = s.find("-->", c_at + 4)
            j = n if j == -1 else j + 3
            out.append(("comment", s[c_at:j]))
            i = j
            continue
        tag = r.group(1).lower()
        text(r.group())
        body_start = r.end()
        close = re.compile(r"</" + tag + r"\s*>", re.I).search(s, body_start)
        body_end = close.start() if close else n
        body = s[body_start:body_end]
        out.extend(_lex_js(body) if tag == "script" else _lex_css(body))
        if close:
            text(close.group())
            i = close.end()
        else:
            i = n
    return out


# ── shell ───────────────────────────────────────────────────────────────────

def _lex_sh(s: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    i, n = 0, len(s)
    word = ""

    def flush():
        nonlocal word
        if word:
            out.append(("code", word))
            word = ""

    while i < n:
        c = s[i]
        if c == "#" and (i == 0 or s[i - 1].isspace() or s[i - 1] in ";(") and not word:
            flush()
            j = s.find("\n", i)
            j = n if j == -1 else j
            out.append(("comment", s[i:j]))
            i = j
        elif c in "'\"":
            flush()
            q = c
            j = i + 1
            while j < n and s[j] != q:
                j += 2 if (s[j] == "\\" and q == '"') else 1
            out.append(("string", s[i:j + 1]))
            i = j + 1
        elif c.isspace():
            flush()
            j = i
            while j < n and s[j].isspace():
                j += 1
            out.append(("ws", s[i:j]))
            i = j
        else:
            word += c
            i += 1
    flush()
    return out


# ── Python ──────────────────────────────────────────────────────────────────

def _docstring_nodes(tree: ast.AST):
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
                    and isinstance(body[0].value.value, str):
                yield node, body[0]


def _python_comments(src: str) -> list[str]:
    found: list[tuple[int, int, str]] = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokenize.COMMENT:
                found.append((tok.start[0], tok.start[1], tok.string))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        pass
    try:
        tree = ast.parse(src)
        for _node, expr in _docstring_nodes(tree):
            seg = ast.get_source_segment(src, expr) or ""
            found.append((expr.lineno, expr.col_offset, seg))
    except SyntaxError:
        pass
    return [t for _l, _c, t in sorted(found)]


def _strip_docstrings(tree: ast.AST) -> ast.AST:
    for node, expr in list(_docstring_nodes(tree)):
        node.body.remove(expr)
        if not node.body:
            node.body.append(ast.Pass())
    return tree


def python_equivalent(a: str, b: str) -> bool:
    """Same program once comments and docstrings are set aside."""
    da = ast.dump(_strip_docstrings(ast.parse(a)), include_attributes=False)
    db = ast.dump(_strip_docstrings(ast.parse(b)), include_attributes=False)
    return da == db


# ── API ─────────────────────────────────────────────────────────────────────

_LEXERS = {"js": _lex_js, "css": _lex_css, "html": _lex_html, "sh": _lex_sh}


def comments(src: str, kind: str) -> list[str]:
    if kind == "py":
        return _python_comments(src)
    return [t for k, t in _LEXERS[kind](src) if k == "comment"]


def code_tokens(src: str, kind: str) -> list[str]:
    """Everything but comments and whitespace, in order (strings verbatim)."""
    if kind == "py":
        raise ValueError("use python_equivalent for Python")
    return [t for k, t in _LEXERS[kind](src) if k in ("code", "string")]
