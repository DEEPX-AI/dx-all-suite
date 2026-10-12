#!/usr/bin/env python3
"""Replace groups of per-language sibling spans with a single data-i18n span.

The markup writes each phrase six times, once per language:

    <span class="ko">...</span><span class="ja">保存</span><span class="zh-CN">保存</span>
    <span class="zh-TW">儲存</span><span class="en">Save</span><span class="es">Guardar</span>

The same phrase is also in the dictionary (_DX_I18N_DICT), so translations live in two places. i18n.js
already supports data-i18n, so the markup only needs the English text:

    <span data-i18n="Save">Save</span>

    python -m scripts.migrate_i18n_spans            # only print what would change
    python -m scripts.migrate_i18n_spans --apply    # apply the changes

The dictionary is never overwritten. Translations found only in the markup are added as new keys; when
markup and dictionary disagree, the dictionary value is kept and the mismatch is reported, since a person
has to decide which one is right.
"""
from __future__ import annotations

import argparse
import html as _html
import re
from pathlib import Path

from scripts.js_object_literal import object_span, parse_object_after, value_spans

ROOT = Path(__file__).resolve().parent.parent
LANGS = ("ko", "ja", "zh-CN", "zh-TW", "en", "es")

# module → (markup glob, dictionary file). The launcher dictionary is inline in its HTML.
MODULES = {
    "dx_app": ("dx_app", "dx_app/static/js/i18n.js"),
    "dx_stream": ("dx_stream", "dx_stream/static/js/stream-i18n.js"),
    "dx_compiler": ("dx_compiler", "dx_compiler/static/js/compiler-i18n.js"),
    "dx_planner": ("dx_planner", "dx_planner/static/js/i18n.js"),
    "dx_monitor": ("dx_monitor", "dx_monitor/static/js/i18n.js"),
    "dx_agent_dev": ("dx_agent_dev", "dx_agent_dev/static/js/i18n.js"),
    "launcher": ("launcher", "launcher/static/index.html"),
}

# A language class anywhere in the class list makes it a language span; matching only class="ko"
# misses spans like `class="deepx-link-label ko"`.
_ONE = (
    r'<span class="(?:[^"]*\s)?(ko|ja|zh-CN|zh-TW|en|es)(?:\s[^"]*)?">'
    r'((?:(?!</?span).)*?)</span>'
)
# Whitespace before the first span is kept: the space in "🎬 <group>" is visible on screen.
# Whitespace between spans is consumed: only one span is visible, so it collapses into the surrounding space.
_GROUP = re.compile(_ONE + r"(?:\s*" + _ONE + r")+", re.S)
_SINGLE = re.compile(_ONE, re.S)

# Spans built by string concatenation inside JS are code, not text.
_CONCAT = re.compile(r"""['"]\s*\+|\+\s*['"]""")


def _texts(block: str) -> dict[str, str]:
    """The per-language text in a group. If a language appears twice, the first wins."""
    out: dict[str, str] = {}
    for lang, value in _SINGLE.findall(block):
        out.setdefault(lang, value.strip())
    return out


def _is_solo(text: str, start: int, end: int) -> bool:
    """Whether the group is the only content of its parent element."""
    before = text[max(0, start - 400) : start].rstrip()
    after = text[end : end + 200].lstrip()
    return before.endswith(">") and after.startswith("</")


# Void tags. A span group after one of these is a sibling, not a child.
_VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}


def _parent_tag(text: str, start: int) -> tuple[int, str] | None:
    """(start index, raw tag) of the opening tag right before the group."""
    close = text.rfind(">", 0, start)
    if close < 0:
        return None
    open_at = text.rfind("<", 0, close)
    if open_at < 0:
        return None
    tag = text[open_at : close + 1]
    if tag.startswith("</") or tag.endswith("/>") or "<" in tag[1:]:
        return None
    if tag.count('"') % 2 or tag.count("'") % 2:
        # A fragment cut at a '>' inside an attribute value (onclick="f(a>b)"). Leave it alone.
        return None
    name = re.match(r"<([a-zA-Z][a-zA-Z0-9]*)", tag)
    if not name or name.group(1).lower() in _VOID:
        return None
    return open_at, tag


def _attr_escape(value: str) -> str:
    return _html.escape(value, quote=True)


_ENTITY = re.compile(r"&[a-zA-Z#][a-zA-Z0-9]*;")


class Finding:
    __slots__ = (
        "path", "key", "translations", "mode", "start", "end", "replacement",
    )

    def __init__(self, path, key, translations, mode, start, end, replacement):
        self.path = path
        self.key = key
        self.translations = translations
        self.mode = mode
        self.start = start
        self.end = end
        self.replacement = replacement


def _plan_file(path: Path) -> list[Finding]:
    text = path.read_text()
    found: list[Finding] = []
    for m in _GROUP.finditer(text):
        block = m.group(0)
        if _CONCAT.search(block):
            # Assembled like '<span class="ko">' + t.ko + '</span>'. That is code, not a
            # string, so no key can be extracted.
            continue
        tr = _texts(block)
        key = tr.get("en")
        if not key:
            # A group without English cannot produce a key. Leave it alone.
            continue
        has_html = any("<" in v for v in tr.values())
        attr = "data-i18n-html" if has_html else "data-i18n"
        # data-i18n writes textContent, so both the dictionary key and the displayed text
        # must have entities decoded. data-i18n-html keeps the raw source.
        if has_html:
            key_attr = key
            body = key
        else:
            key_attr = _html.unescape(key)
            body = _html.escape(key_attr, quote=False)
            tr = {lang: _html.unescape(v) for lang, v in tr.items()}
        solo = _is_solo(text, m.start(), m.end())
        parent = _parent_tag(text, m.start()) if solo else None
        if parent and "data-i18n" not in parent[1]:
            open_at, tag = parent
            new_tag = tag[:-1].rstrip() + f' {attr}="{_attr_escape(key_attr)}">'
            found.append(
                Finding(path, key_attr, tr, "hoist", open_at, m.end(), new_tag + body)
            )
        else:
            found.append(
                Finding(
                    path,
                    key_attr,
                    tr,
                    "wrap",
                    m.start(),
                    m.end(),
                    f'<span {attr}="{_attr_escape(key_attr)}">{body}</span>',
                )
            )
    return found


def _markup_files(root: str) -> list[Path]:
    base = ROOT / root
    return sorted(
        p
        for p in list(base.rglob("*.html")) + list(base.rglob("*.js"))
        if "/node_modules/" not in p.as_posix()
    )


def _load_dict(rel: str) -> dict:
    return parse_object_after((ROOT / rel).read_text(), "_DX_I18N_DICT")


def _render_entry(key: str, tr: dict[str, str]) -> str:
    """Render in the multi-line form the dictionary already uses.

    A one-line entry is unreadable to the contract tests: dx_compiler's
    dict_entry() reads the body from the line after `'key': {` up to `\n  },`.
    """
    lines = [f"  {_js_str(key)}: {{"]
    for lang in LANGS:
        if lang == "en" or lang not in tr:
            continue
        name = lang if lang.isalpha() else _js_str(lang)
        lines.append(f"    {name}: {_js_str(tr[lang])},")
    lines.append("  },")
    return "\n".join(lines)


def _js_str(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


def _referenced_outside_spans(files: list[Path], key: str) -> list[str]:
    """Whether the key is referenced by anything other than lang-span groups.

    If so, aligning the dictionary value with the markup would also change those
    other screens. That is not for a script to decide, so such keys are left alone.
    """
    pat = re.escape(key)
    probes = (
        re.compile(r'data-i18n(?:-html)?="' + pat + r'"'),
        re.compile(r"T\(\s*['\"]" + pat + r"['\"]"),
    )
    hits = []
    for path in files:
        text = path.read_text()
        for probe in probes:
            m = probe.search(text)
            if m:
                hits.append(f"{path.relative_to(ROOT)}:{text[: m.start()].count(chr(10)) + 1}")
                break
    return hits


def _apply_dict_edits(rel: str, edits: dict[str, dict[str, str]]) -> None:
    """Replace individual language values in the dictionary in place."""
    path = ROOT / rel
    src = path.read_text()
    spans = value_spans(src, "_DX_I18N_DICT")
    patches = []
    for key, langs in edits.items():
        for lang, value in langs.items():
            start, end = spans[key][lang]
            patches.append((start, end, _js_str(value)))
    for start, end, text in sorted(patches, reverse=True):
        src = src[:start] + text + src[end:]
    path.write_text(src)


def _plan_module(name: str) -> dict:
    """The migration plan for one module.

    A key can hold only one set of translations. When screens use different text
    for the same key (markup disagrees with itself, or with the dictionary while
    other screens also use the key), a script cannot choose, so the key is left as is.
    """
    root, dict_rel = MODULES[name]
    dictionary = _load_dict(dict_rel)
    files = _markup_files(root)

    findings: list[Finding] = []
    for path in files:
        findings.extend(_plan_file(path))

    # 1) Collect the translations the markup claims for each key.
    claims: dict[str, dict[str, set[str]]] = {}
    for f in findings:
        per_key = claims.setdefault(f.key, {})
        for lang, value in f.translations.items():
            if lang != "en":
                per_key.setdefault(lang, set()).add(value)

    # 2) Set aside the keys that cannot be touched.
    blocked: dict[str, str] = {}
    edits: dict[str, dict[str, str]] = {}
    additions: dict[str, dict[str, str]] = {}
    for key, langs in claims.items():
        split = {lang: vs for lang, vs in langs.items() if len(vs) > 1}
        if split:
            lang, values = next(iter(split.items()))
            blocked[key] = (
                f"[{lang}] 마크업끼리 " + " ≠ ".join(sorted(repr(v) for v in values))
            )
            continue
        settled = {lang: next(iter(vs)) for lang, vs in langs.items()}
        existing = dictionary.get(key)
        if existing is None:
            additions[key] = settled
            continue
        if not isinstance(existing, dict):
            blocked[key] = "사전 항목이 문자열 (구형 포맷)"
            continue
        differing = {
            lang: value
            for lang, value in settled.items()
            if lang in existing and existing[lang] != value
        }
        if not differing:
            continue
        refs = _referenced_outside_spans(files, key)
        if refs:
            lang, value = next(iter(differing.items()))
            blocked[key] = (
                f"[{lang}] 사전 {existing[lang]!r} ≠ 마크업 {value!r} — "
                f"{refs[0]} 도 이 key 를 쓴다"
            )
        else:
            edits[key] = differing

    return {
        "dict_rel": dict_rel,
        "findings": [f for f in findings if f.key not in blocked],
        "blocked": blocked,
        "edits": edits,
        "additions": {k: v for k, v in additions.items() if k not in blocked},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="실제로 고친다")
    ap.add_argument("--module", action="append", help="특정 모듈만")
    args = ap.parse_args()

    totals = {"groups": 0, "hoist": 0, "wrap": 0, "add": 0, "fix": 0, "hold": 0}
    holds: list[str] = []

    for name in args.module or list(MODULES):
        try:
            plan = _plan_module(name)
        except Exception as exc:  # noqa: BLE001
            print(f"[{name}] 계획 실패: {type(exc).__name__}: {exc}")
            return 2

        findings = plan["findings"]
        per_file: dict[Path, list[Finding]] = {}
        for f in findings:
            per_file.setdefault(f.path, []).append(f)

        totals["groups"] += len(findings)
        totals["hoist"] += sum(1 for f in findings if f.mode == "hoist")
        totals["wrap"] += sum(1 for f in findings if f.mode == "wrap")
        totals["add"] += len(plan["additions"])
        totals["fix"] += len(plan["edits"])
        totals["hold"] += len(plan["blocked"])
        holds += [f"  {name} {k!r} — {v}" for k, v in sorted(plan["blocked"].items())]

        print(
            f"[{name}] 그룹 {len(findings)} "
            f"(hoist {sum(1 for f in findings if f.mode == 'hoist')}, "
            f"wrap {sum(1 for f in findings if f.mode == 'wrap')}) · "
            f"사전 신규 {len(plan['additions'])} · 값 정정 {len(plan['edits'])} · "
            f"보류 {len(plan['blocked'])} · 파일 {len(per_file)}"
        )

        if not args.apply:
            continue

        for path, items in per_file.items():
            text = path.read_text()
            for f in sorted(items, key=lambda x: x.start, reverse=True):
                text = text[: f.start] + f.replacement + text[f.end :]
            path.write_text(text)

        if plan["edits"]:
            _apply_dict_edits(plan["dict_rel"], plan["edits"])

        if plan["additions"]:
            dpath = ROOT / plan["dict_rel"]
            src = dpath.read_text()
            start, end = object_span(src, "_DX_I18N_DICT")
            block = "\n".join(
                _render_entry(k, plan["additions"][k])
                for k in sorted(plan["additions"])
            )
            insert_at = src.rfind("}", start, end)
            headsrc = src[:insert_at].rstrip()
            if not headsrc.endswith((",", "{")):
                headsrc += ","
            marker = "\n  // ── 마크업 lang-span 에서 옮겨온 항목 ──\n"
            dpath.write_text(headsrc + marker + block + "\n" + src[insert_at:])

    print(
        f"\n합계: 그룹 {totals['groups']} "
        f"(hoist {totals['hoist']} / wrap {totals['wrap']}) · "
        f"사전 신규 {totals['add']} · 값 정정 {totals['fix']} · "
        f"보류 key {totals['hold']}"
    )
    if holds:
        print("\n보류 — key 하나에 문구가 둘이라 사람이 정해야 한다:")
        for line in holds:
            print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
