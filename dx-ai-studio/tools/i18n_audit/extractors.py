from __future__ import annotations

import ast
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path

from .config import BRAND_TERMS, LANGUAGES, MODULES, SOURCE_EXTENSIONS, is_excluded_path
from .integrity import decode_js_string_value
from .schema import AuditRecord

_CLASS_RE = re.compile(r'class=["\']([^"\']+)["\']')
_ATTR_RE = re.compile(r'(?<![a-zA-Z0-9_-])(placeholder|title|aria-label)=["\']([^"\']+)["\']')
_DATA_I18N_ATTR_RE = re.compile(r'data-i18n-(placeholder|title|aria-label)=["\']([^"\']+)["\']')

_LANG_SET = set(LANGUAGES)
_LANG_MAP_KEYS = _LANG_SET
_HTML_VOID_ELEMENTS = frozenset(
    {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
)
_JS_LANG_RE = re.compile(
    r"['\"]?(en|ja|ko|es|zh-CN|zh-TW)['\"]?\s*:\s*"
    r"(?:'(?P<value_s>(?:\\.|[^'\\])*)'|\"(?P<value_d>(?:\\.|[^\"\\])*)\")"
)


def _attach_brand_terms(record: AuditRecord) -> AuditRecord:
    """Return a new record with brand_terms set if English text is a pure brand term."""
    en_text = record.texts.get("en", "").strip()
    if en_text and en_text in BRAND_TERMS:
        return AuditRecord(
            module=record.module,
            surface=record.surface,
            route_or_state=record.route_or_state,
            source_file=record.source_file,
            selector_or_key=record.selector_or_key,
            text_role=record.text_role,
            texts=record.texts,
            brand_terms=(en_text,),
        )
    return record


def _class_tokens_lang(class_attr: str) -> str | None:
    """Return the language code if exactly one class token is a known language."""
    for token in class_attr.split():
        if token in _LANG_SET:
            return token
        if token.startswith("lang-") and token[5:] in _LANG_SET:
            return token[5:]
    return None


class _SpanGroupParser(HTMLParser):
    """Parse HTML to find wrapper elements containing ≥2 locale spans."""

    def __init__(self) -> None:
        super().__init__()
        self.results: list[tuple[str, dict[str, str], dict[str, str]]] = []
        self._stack: list[tuple[str, dict[str, str], dict[str, str], int]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in _HTML_VOID_ELEMENTS:
            return
        attr_dict = {k: (v or "") for k, v in attrs}
        self._stack.append((tag.lower(), attr_dict, {}, 0))

    def handle_endtag(self, tag: str) -> None:
        # Find matching open tag (outermost match for same tag)
        for i in range(len(self._stack) - 1, -1, -1):
            if self._stack[i][0] == tag:
                t, attrs, spans, _depth = self._stack.pop(i)
                # If this element itself is a locale span, propagate text up
                class_val = attrs.get("class", "")
                lang = _class_tokens_lang(class_val)
                emitted = False
                if lang and t == "span":
                    # Propagate to parent
                    if self._stack:
                        p_tag, p_attrs, p_spans, p_depth = self._stack[-1]
                        p_spans[lang] = spans.get("_text_", "")
                        self._stack[-1] = (p_tag, p_attrs, p_spans, p_depth)
                else:
                    lang_spans = {k: v for k, v in spans.items() if k != "_text_"}
                    if len(lang_spans) >= 2 and "en" in lang_spans:
                        # This is a wrapper with locale spans
                        self.results.append((tag, attrs, spans))
                        emitted = True
                # Propagate collected spans to parent only if not yet emitted
                if not lang and not emitted and self._stack:
                    p_tag, p_attrs, p_spans, p_depth = self._stack[-1]
                    for k, v in spans.items():
                        if k != "_text_":
                            p_spans.setdefault(k, v)
                    self._stack[-1] = (p_tag, p_attrs, p_spans, p_depth)
                return
        # Unmatched close tag; ignore

    def handle_data(self, data: str) -> None:
        if self._stack:
            t, attrs, spans, depth = self._stack[-1]
            clean = re.sub(r"\s+", " ", data).strip()
            if clean:
                spans["_text_"] = spans.get("_text_", "") + (" " + clean if spans.get("_text_") else clean)
            self._stack[-1] = (t, attrs, spans, depth)


def _clean_text(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value)
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def _class_selector(attrs: str) -> str:
    match = _CLASS_RE.search(attrs)
    if not match:
        return "html-block"
    return _class_selector_from_str(match.group(1))


def _class_selector_from_str(class_val: str) -> str:
    if not class_val:
        return "html-block"
    classes = [c for c in class_val.split() if c not in _LANG_SET and not c.startswith(("lang-",))]
    return "." + ".".join(classes) if classes else "html-block"


def iter_source_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if is_excluded_path(rel):
            continue
        if path.suffix in SOURCE_EXTENSIONS:
            yield path


def module_for_path(path: Path, root: Path) -> str:
    rel = path.relative_to(root).as_posix()
    for module, prefixes in MODULES.items():
        if any(rel == prefix or rel.startswith(prefix + "/") for prefix in prefixes):
            return module
    return "unknown"


def extract_from_html(source: str, *, module: str, source_file: str) -> list[AuditRecord]:
    records: list[AuditRecord] = []

    parser = _SpanGroupParser()
    parser.feed(source)

    for _tag, attrs, spans in parser.results:
        clean_spans = {k: v for k, v in spans.items() if k != "_text_"}
        if len(clean_spans) < 2 or "en" not in clean_spans:
            continue
        class_val = attrs.get("class", "")
        selector = _class_selector_from_str(class_val)
        records.append(_attach_brand_terms(AuditRecord(
            module=module,
            surface="static-html",
            route_or_state="source",
            source_file=source_file,
            selector_or_key=selector,
            text_role="body",
            texts={lang: clean_spans.get(lang, "") for lang in LANGUAGES},
        )))

    # Attributes whose value is also present as a data-i18n-* key are managed
    # by the JS i18n runtime and therefore not standalone missing-language
    # candidates — skip them to avoid false-positive extraction.
    data_i18n_keys = {v for _, v in _DATA_I18N_ATTR_RE.findall(source)}

    for attr, value in _ATTR_RE.findall(source):
        clean = _clean_text(value)
        if not clean:
            continue
        if clean in data_i18n_keys:
            continue
        records.append(_attach_brand_terms(AuditRecord(
            module=module,
            surface="static-html-attribute",
            route_or_state="source",
            source_file=source_file,
            selector_or_key=f"{attr}:{clean}",
            text_role=attr,
            texts={"en": clean},
        )))
    return records


def extract_from_json_obj(obj, *, module: str, source_file: str, path: str = "") -> list[AuditRecord]:
    records: list[AuditRecord] = []
    if isinstance(obj, dict):
        keys = set(obj)
        if keys & _LANG_MAP_KEYS:
            texts = {lang: str(obj.get(lang, "")) for lang in LANGUAGES}
            records.append(_attach_brand_terms(AuditRecord(
                module=module,
                surface="json-language-map",
                route_or_state="source",
                source_file=source_file,
                selector_or_key=path or "$",
                text_role="data",
                texts=texts,
            )))
        else:
            for key, value in obj.items():
                child = f"{path}.{key}" if path else str(key)
                records.extend(extract_from_json_obj(value, module=module, source_file=source_file, path=child))
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            records.extend(extract_from_json_obj(value, module=module, source_file=source_file, path=f"{path}[{index}]"))
    return records


def _scan_balanced_brace(source: str, start: int) -> str | None:
    """Extract text between balanced braces starting at source[start] == '{'.

    Ignores braces inside single- or double-quoted strings and handles
    escaped quotes/backslashes.  Returns the content between the outermost
    braces (exclusive) or *None* if no balanced match is found.
    """
    if start >= len(source) or source[start] != "{":
        return None
    depth = 0
    in_quote: str | None = None
    i = start
    while i < len(source):
        ch = source[i]
        if in_quote:
            if ch == "\\" and i + 1 < len(source):
                i += 2  # skip escaped character
                continue
            if ch == in_quote:
                in_quote = None
        else:
            if ch in ("'", '"'):
                in_quote = ch
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return source[start + 1 : i]
        i += 1
    return None


# Matches a quoted key followed by ':' and '{'. Opposite quote characters are
# valid inside JS strings and must not terminate the key.
_JS_KEY_OPEN_RE = re.compile(
    r"(?:'(?P<key_s>(?:\\.|[^'\\])*)'|\"(?P<key_d>(?:\\.|[^\"\\])*)\")\s*:\s*\{"
)


def extract_inventory(root: Path) -> list[AuditRecord]:
    records: list[AuditRecord] = []
    for path in iter_source_files(root):
        rel = path.relative_to(root).as_posix()
        module = module_for_path(path, root)
        source = path.read_text(encoding="utf-8", errors="replace")
        if path.suffix == ".html":
            records.extend(extract_from_html(source, module=module, source_file=rel))
        elif path.suffix == ".json":
            try:
                records.extend(extract_from_json_obj(json.loads(source), module=module, source_file=rel))
            except json.JSONDecodeError:
                continue
        elif path.suffix == ".js":
            records.extend(extract_js_i18n_entries(source, module=module, source_file=rel))
        elif path.suffix == ".py":
            records.extend(extract_from_python_source(source, module=module, source_file=rel))
    return records


def extract_js_i18n_entries(source: str, *, module: str, source_file: str) -> list[AuditRecord]:
    records: list[AuditRecord] = []
    for match in _JS_KEY_OPEN_RE.finditer(source):
        raw_key = match.group("key_s") if match.group("key_s") is not None else match.group("key_d")
        key = html.unescape(decode_js_string_value(raw_key))
        if key in LANGUAGES:
            continue
        brace_start = match.end() - 1  # position of '{'
        body = _scan_balanced_brace(source, brace_start)
        if body is None:
            continue
        lang_values = {
            m.group(1): html.unescape(
                decode_js_string_value(
                    m.group("value_s") if m.group("value_s") is not None else m.group("value_d")
                )
            )
            for m in _JS_LANG_RE.finditer(body)
        }
        if not lang_values:
            continue
        texts = {"en": key}
        texts.update(lang_values)
        records.append(_attach_brand_terms(AuditRecord(
            module=module,
            surface="js-i18n-dictionary",
            route_or_state="source",
            source_file=source_file,
            selector_or_key=key,
            text_role="dictionary",
            texts={lang: texts.get(lang, "") for lang in LANGUAGES},
        )))
    return records


def _ast_to_obj(node: ast.expr) -> object | None:
    """Convert a simple AST literal node to a Python object. Returns None for complex nodes."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (str, int, float, bool)):
        return node.value
    if isinstance(node, ast.Dict):
        result = {}
        for k, v in zip(node.keys, node.values):
            if k is None:
                return None
            key = _ast_to_obj(k)
            if not isinstance(key, str):
                return None
            val = _ast_to_obj(v)
            if val is None:
                return None
            result[key] = val
        return result
    if isinstance(node, ast.List):
        items = []
        for elt in node.elts:
            val = _ast_to_obj(elt)
            if val is None:
                return None
            items.append(val)
        return items
    return None


def extract_from_python_source(source: str, *, module: str, source_file: str) -> list[AuditRecord]:
    """Extract i18n records from Python source using AST parsing (stdlib only)."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    records: list[AuditRecord] = []
    for node in ast.walk(tree):
        target: ast.expr | None = None
        value: ast.expr | None = None
        if isinstance(node, ast.Assign):
            if node.targets:
                target = node.targets[0]
                value = node.value
        elif isinstance(node, ast.AnnAssign):
            target = node.target
            value = node.value
        else:
            continue
        if value is None or not isinstance(value, (ast.Dict, ast.List)):
            continue
        obj = _ast_to_obj(value)
        if obj is None:
            continue
        prefix = ""
        if isinstance(target, ast.Name):
            prefix = target.id
        records.extend(
            extract_from_json_obj(obj, module=module, source_file=source_file, path=prefix)
        )
    return records
