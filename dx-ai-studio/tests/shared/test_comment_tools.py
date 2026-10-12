"""Comment tools for the release cleanup (2026-10-12): a lexer that tells comments from code, a gate that keeps Korean
out of comments, and a checker that proves a rewrite touched comments only.

The lexer must not mistake code for a comment: a URL in a string, a regex literal with a slash, a template literal,
a CSS url(//cdn…), inline <script>/<style> in HTML. A wrong split would let a code change pass as "comments only".
"""
from __future__ import annotations

import pytest

from scripts.comment_lexer import code_tokens, comments


@pytest.mark.parametrize(("src", "want"), [
    ("var u = 'http://x.y/z'; // real\n", ["// real"]),
    ('let s = "a /* not */ b"; /* yes */', ["/* yes */"]),
    ("const r = /a\\/\\/b/g; // after regex\n", ["// after regex"]),
    ("x = a / b / c; // div\n", ["// div"]),
    ("const t = `x ${'//'} // in template`; // out\n", ["// out"]),
    ("if (/^\\/\\//.test(p)) {} /* c */", ["/* c */"]),
    ("return /[/]/.test(s); // class slash\n", ["// class slash"]),
])
def test_js_comments(src, want):
    assert comments(src, "js") == want


def test_css_url_is_not_a_comment():
    src = "a{background:url(//cdn.example/x.png)} /* note */ b{c:d}"
    assert comments(src, "css") == ["/* note */"]


def test_python_comments_and_docstrings():
    src = '"""Module doc."""\nimport os  # why\ns = "# not a comment"\n\ndef f():\n    """Func doc."""\n    return 1\n'
    got = comments(src, "py")
    assert "# why" in got and '"""Module doc."""' in got and '"""Func doc."""' in got
    assert all("not a comment" not in c for c in got)


def test_html_comments_and_inline_code():
    src = ('<p>// not a comment</p><!-- note --><script>var a = "x"; // js note\n</script>'
           '<style>p{color:red} /* css note */</style>')
    got = comments(src, "html")
    assert got == ["<!-- note -->", "// js note", "/* css note */"]


def test_shell_comments():
    src = 'echo "# not" # yes\n# whole line\nx=$((1#0))\n'
    got = comments(src, "sh")
    assert "# yes" in got and "# whole line" in got and all("not" not in c for c in got)


@pytest.mark.parametrize("kind,a,b", [
    ("js", "var x = 1; // 한글 주석\nfoo('http://a');\n", "var x = 1; // English\nfoo('http://a');\n"),
    ("js", "/* 블록\n 주석 */\nf();\n", "f();\n"),
    ("css", "/* 색 */ a{color:red}", "/* colour */\na { color:red }"),
    ("html", "<!-- 메모 --><div class=\"a\">x</div>", "<div class=\"a\">x</div>"),
    ("sh", "# 설명\nls -la # 목록\n", "# list\nls -la\n"),
])
def test_comment_only_changes_keep_the_code_tokens(kind, a, b):
    assert code_tokens(a, kind) == code_tokens(b, kind)


@pytest.mark.parametrize("kind,a,b", [
    ("js", "foo('http://a');", "foo('http://b');"),
    ("js", "x = 1;", "x = 2;"),
    ("css", "a{color:red}", "a{color:blue}"),
    ("html", "<div>x</div>", "<div>y</div>"),
    ("sh", 'echo "a b"', 'echo "a  b"'),
])
def test_code_changes_are_seen(kind, a, b):
    assert code_tokens(a, kind) != code_tokens(b, kind)


def test_python_equivalence_ignores_comments_and_docstrings_only():
    from scripts.comment_lexer import python_equivalent
    a = '"""한글 문서."""\nx = 1  # 한글\ndef f():\n    """설명."""\n    return "문자열"\n'
    b = '"""English doc."""\nx = 1  # English\ndef f():\n    return "문자열"\n'
    assert python_equivalent(a, b)
    assert not python_equivalent(a, b.replace('"문자열"', '"string"'))


def test_the_gate_counts_korean_comment_lines_not_strings():
    from scripts.comment_language_gate import hangul_comment_lines
    assert hangul_comment_lines("var a = '한글 문자열'; // 한글 주석\n/* 둘째\n 셋째 */", "js") == 3   # the line comment + both lines of the block
    assert hangul_comment_lines('T("한글")  # English\n', "py") == 0


def test_the_gate_passes_and_the_baseline_is_tight():
    import json
    import subprocess
    import sys
    from scripts.comment_language_gate import BASELINE_PATH, ROOT, count
    r = subprocess.run([sys.executable, "-m", "scripts.comment_language_gate"], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    current = count()
    stale = {k: (current.get(k, 0), v) for k, v in baseline.items() if current.get(k, 0) < v}
    assert not stale, f"baseline has headroom; run `python -m scripts.comment_language_gate --update`: {stale}"


def test_the_comment_only_checker_flags_a_code_change(tmp_path):
    from scripts.comment_only_diff import same_code
    assert same_code("x = 1  # 한글\n", "x = 1  # English\n", "py")
    assert not same_code("x = 1\n", "x = 2\n", "py")
    assert not same_code("a{color:red}", "a{color:blue}", "css")
