"""Placeholder and HTML-shape integrity helpers for i18n audit."""
from __future__ import annotations

import bisect
import re
from html.parser import HTMLParser
from typing import Any

from .schema import AuditRecord

# Matches common placeholder styles in sorted-friendly order:
#   ${name}  printf (%s, %03d, %0.2f)  {{name}}  {0}/{name}
_PLACEHOLDER_RE = re.compile(
    r"\$\{[^}]+\}"       # ${device}
    r"|%[-+0#]*\d*(?:\.\d+)?[sdifouxXeEfFgGcr]"  # printf-style specifier
    r"|\{\{[^}]+\}\}"    # {{fps}}
    r"|\{[^{}]+\}"       # {0}, {name}
)


def _token_sort_key(token: str) -> tuple[int, str]:
    """Sort by category (${} < % < {{}} < {}), then lexicographically."""
    if token.startswith("${"):
        return (0, token)
    if token.startswith("%"):
        return (1, token)
    if token.startswith("{{"):
        return (2, token)
    return (3, token)


def placeholder_tokens(text: str) -> tuple[str, ...]:
    """Return deduplicated placeholder tokens sorted by category then name."""
    return tuple(sorted(set(_PLACEHOLDER_RE.findall(text)), key=_token_sort_key))


class _TagCollector(HTMLParser):
    """Collect (tag, safe_attrs) tuples in document order."""

    _SAFE_ATTRS = frozenset({"class", "id", "href", "src", "alt", "title"})

    def __init__(self) -> None:
        super().__init__()
        self.tags: list[tuple[str, tuple[str, ...]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        safe = tuple(sorted(k for k, _ in attrs if k in self._SAFE_ATTRS))
        self.tags.append((tag, safe))


def html_shape(text: str) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Return the structural shape of HTML tags (name + safe attributes)."""
    collector = _TagCollector()
    collector.feed(text)
    return tuple(collector.tags)


def record_integrity_issues(record: AuditRecord) -> list[str]:
    """Check a single record for placeholder/HTML drift across locales.

    Missing locale values are skipped — those are caught by the
    missing-language classifier.
    """
    en_text = record.texts.get("en", "")
    if not en_text:
        return []

    en_tokens = placeholder_tokens(en_text)
    en_shape = html_shape(en_text)
    issues: list[str] = []

    for lang, text in sorted(record.texts.items()):
        if lang == "en" or not text:
            continue
        if placeholder_tokens(text) != en_tokens:
            issues.append(f"{record.record_id}: {lang} placeholder mismatch")
        if html_shape(text) != en_shape:
            issues.append(f"{record.record_id}: {lang} HTML shape mismatch")

    return issues


def check_integrity_gate(records: list[AuditRecord]) -> list[str]:
    """Return all integrity issues across records (empty list = pass)."""
    all_issues: list[str] = []
    for record in records:
        all_issues.extend(record_integrity_issues(record))
    return all_issues


def check_findings_gate(findings: list[Any]) -> str | None:
    """Return an error message if any missing-language findings exist."""
    from .schema import Finding

    count = sum(
        1 for f in findings
        if (isinstance(f, Finding) and f.issue_type == "missing-language")
        or (isinstance(f, dict) and f.get("issue_type") == "missing-language")
    )
    if count:
        return f"{count} missing-language findings"
    return None


# Matches T('...', '...') or T("...", "...") with literal string args only.
# Handles escaped quotes inside strings.
_T_CALL_RE = re.compile(
    r"""T\(\s*"""
    r"""(?:'(?P<en_s>(?:[^'\\]|\\.)*)'|"(?P<en_d>(?:[^"\\]|\\.)*)")"""
    r"""\s*,\s*"""
    r"""(?:'(?P<ko_s>(?:[^'\\]|\\.)*)'|"(?P<ko_d>(?:[^"\\]|\\.)*)")"""
    r"""\s*\)""",
    re.DOTALL,
)

_JS_SIMPLE_ESCAPES = {
    "'": "'",
    '"': '"',
    "\\": "\\",
    "n": "\n",
    "r": "\r",
    "t": "\t",
    "b": "\b",
    "f": "\f",
    "v": "\v",
}


def _mask_js_comments(source: str) -> str:
    """Replace JS comments with spaces while preserving offsets and line breaks."""
    chars = list(source)
    i = 0
    quote: str | None = None
    escaped = False
    while i < len(chars):
        ch = chars[i]
        nxt = chars[i + 1] if i + 1 < len(chars) else ""

        if quote:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == quote:
                quote = None
            i += 1
            continue

        if ch in ("'", '"', "`"):
            quote = ch
            i += 1
            continue

        if ch == "/" and nxt == "/":
            chars[i] = " "
            chars[i + 1] = " "
            i += 2
            while i < len(chars) and chars[i] != "\n":
                chars[i] = " "
                i += 1
            continue

        if ch == "/" and nxt == "*":
            chars[i] = " "
            chars[i + 1] = " "
            i += 2
            while i < len(chars) - 1:
                if chars[i] == "*" and chars[i + 1] == "/":
                    chars[i] = " "
                    chars[i + 1] = " "
                    i += 2
                    break
                if chars[i] != "\n":
                    chars[i] = " "
                i += 1
            continue

        i += 1

    return "".join(chars)


def decode_js_string_value(text: str) -> str:
    chars: list[str] = []
    i = 0
    while i < len(text):
        if text[i] != "\\":
            chars.append(text[i])
            i += 1
            continue

        if i + 1 >= len(text):
            chars.append("\\")
            i += 1
            continue

        escape = text[i + 1]
        if escape == "u" and i + 5 < len(text):
            raw_code = text[i + 2 : i + 6]
            if re.fullmatch(r"[0-9a-fA-F]{4}", raw_code):
                codepoint = int(raw_code, 16)
                i += 6
                if (
                    0xD800 <= codepoint <= 0xDBFF
                    and i + 5 < len(text)
                    and text[i : i + 2] == "\\u"
                    and re.fullmatch(r"[0-9a-fA-F]{4}", text[i + 2 : i + 6])
                ):
                    low = int(text[i + 2 : i + 6], 16)
                    if 0xDC00 <= low <= 0xDFFF:
                        codepoint = 0x10000 + ((codepoint - 0xD800) << 10) + (low - 0xDC00)
                        i += 6
                chars.append(chr(codepoint))
                continue

        if escape == "x" and i + 3 < len(text):
            raw_code = text[i + 2 : i + 4]
            if re.fullmatch(r"[0-9a-fA-F]{2}", raw_code):
                chars.append(chr(int(raw_code, 16)))
                i += 4
                continue

        chars.append(_JS_SIMPLE_ESCAPES.get(escape, escape))
        i += 2

    return "".join(chars)


def extract_t_calls(source: str, *, source_file: str) -> list[dict[str, object]]:
    """Extract literal two-argument T('en', 'ko') calls from source text.

    Returns dicts with source_file, line, column, key, ko_fallback, and disposition.
    Non-literal or non-two-arg calls are intentionally skipped.
    """
    results: list[dict[str, object]] = []
    # Precompute line start offsets for 1-based line numbers
    line_starts = [0]
    for i, ch in enumerate(source):
        if ch == "\n":
            line_starts.append(i + 1)

    search_source = _mask_js_comments(source)
    for m in _T_CALL_RE.finditer(search_source):
        en_text = m.group("en_s") if m.group("en_s") is not None else m.group("en_d")
        ko_text = m.group("ko_s") if m.group("ko_s") is not None else m.group("ko_d")
        en_text = decode_js_string_value(en_text)
        ko_text = decode_js_string_value(ko_text)
        # Find 1-based line number
        line_num = bisect.bisect_right(line_starts, m.start())
        line_start = line_starts[line_num - 1]
        record: dict[str, object] = {
            "source_file": source_file,
            "line": line_num,
            "column": m.start() - line_start + 1,
            "key": en_text or None,
            "ko_fallback": ko_text,
            "disposition": "unclassified",
        }
        if not en_text:
            record["disposition"] = "needs-manual-key"
            record["rationale"] = "empty English T() key requires manual migration"
        results.append(record)
    return results


def check_runtime_switching_gate(
    coverage_states: list[dict[str, Any]] | None,
) -> str | None:
    """Return an error message if any coverage state has runtime-not-switching."""
    if not coverage_states:
        return None
    bad = [cs for cs in coverage_states if cs.get("issue_type") == "runtime-not-switching"]
    if bad:
        return f"{len(bad)} runtime-not-switching issue(s) detected"
    return None
