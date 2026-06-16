"""Idempotent, marker-anchored augmentation of READMEs and docs.

Each inserted block is wrapped in ``<!-- dx-showcase:<name>:start/end -->`` markers
so re-running replaces (not duplicates) it. Used to drop the build-GIF block + the
metrics line into the suite README (EN/KO), the showcase README (EN/KO), and the
00_Agent_Driven_Development docs.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional


def marker(name: str, kind: str = "gif") -> str:
    return f"dx-showcase:{name}:{kind}"


def gif_block(gif_rel: str, caption: str, width: int = 760) -> str:
    return ('<div align="center">\n'
            f'<img src="{gif_rel}" width="{width}"><br>'
            f'<sub><b>{caption}</b></sub>\n'
            '</div>')


def two_col_block(gif_rel: str, sample_rel: str, caption_gif: str,
                  caption_sample: str, gif_w: int = 470, sample_w: int = 280) -> str:
    """A 2-column block (build GIF | result sample image), like the squat showcase."""
    return ('<div align="center">\n<table><tr>\n'
            f'<td align="center"><img src="{gif_rel}" width="{gif_w}"><br>'
            f'<sub><b>{caption_gif}</b></sub></td>\n'
            f'<td align="center"><img src="{sample_rel}" width="{sample_w}"><br>'
            f'<sub><b>{caption_sample}</b></sub></td>\n'
            '</tr></table>\n</div>')


def upsert_block(path: str, *, anchor: str, block: str, mk: str) -> bool:
    """Insert ``block`` (wrapped in markers ``mk``) after the first line containing
    ``anchor`` — or replace the existing marked region. Returns True if changed."""
    p = Path(path)
    if not p.exists():
        return False
    text = p.read_text()
    start = f"<!-- {mk}:start -->"
    end = f"<!-- {mk}:end -->"
    wrapped = f"{start}\n{block}\n{end}"

    if start in text and end in text:
        new = re.sub(re.escape(start) + r".*?" + re.escape(end), wrapped, text,
                     count=1, flags=re.DOTALL)
        if new != text:
            p.write_text(new)
            return True
        return False

    # insert after the anchor line (keep the anchor)
    lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if anchor in line:
            insert_at = i + 1
            sep = "\n" + wrapped + "\n"
            lines.insert(insert_at, sep + ("" if lines[insert_at:i+1] else "\n"))
            p.write_text("".join(lines))
            return True
    # anchor not found → append
    p.write_text(text.rstrip() + "\n\n" + wrapped + "\n")
    return True


def has_marker(path: str, name: str, kind: str = "gif") -> bool:
    p = Path(path)
    if not p.exists():
        return False
    return f"<!-- {marker(name, kind)}:start -->" in p.read_text(errors="replace")


def augment_readme_gif(path: str, *, name: str, anchor: str, gif_rel: str,
                       caption: str, width: int = 760, sample_rel: str = "",
                       sample_caption: str = "") -> bool:
    """Upsert a GIF block under ``anchor``. With ``sample_rel`` → a 2-column
    block (build GIF | result sample image)."""
    if sample_rel:
        block = two_col_block(gif_rel, sample_rel, caption, sample_caption or "result sample")
    else:
        block = gif_block(gif_rel, caption, width)
    return upsert_block(path, anchor=anchor, block=block, mk=marker(name, "gif"))


# ---------------------------------------------------------------------------
# Manifest-driven doc regions (root README card grid / catalog / 00-docs table)
#
# One manifest (dx-agent-dev-showcase/showcases.json) feeds three surfaces.
# Each surface references the same GIFs and showcase dirs but from a different
# location, so paths are computed per "surface":
#   root    — repo-root README.md / README-KO.md
#   catalog — dx-agent-dev-showcase/README.md / README-ko.md  (one dir deep)
#   docs    — docs/source/00_Agent_Driven_Development.md / _kor.md
# ---------------------------------------------------------------------------

_IMG_PREFIX = {"root": "./docs/source/img", "catalog": "../docs/source/img", "docs": "./img"}


def _media_src(surface: str, basename: str) -> str:
    return f"{_IMG_PREFIX[surface]}/{basename}"


def _showcase_link(surface: str, name: str, lang: str) -> str:
    rd = "README-ko.md" if lang == "ko" else "README.md"
    if surface == "root":
        return f"dx-agent-dev-showcase/{name}/{rd}"
    if surface == "catalog":
        return f"./{name}/{rd}"
    return f"../../dx-agent-dev-showcase/{name}/"   # docs surface → dir link


def _media_html(s, *, surface: str, height: int, extra: str = "") -> str:
    """Render a showcase's card media (gif/sample image) at a UNIFORM HEIGHT so
    cards line up regardless of portrait/landscape aspect.

    For ``card_media == "video"`` we render the GIF rendition of the clip (same
    basename, ``.gif``) rather than an HTML5 ``<video>`` — GitHub's Markdown
    renderer does NOT play inline ``<video>`` tags, so an autoplaying GIF is the
    portable equivalent. (The source ``.mp4`` is not committed.)"""
    if s.card_media == "video" and s.video:
        gif_name = s.video.rsplit(".", 1)[0] + ".gif"
        return f'<img src="{_media_src(surface, gif_name)}" height="{height}"{extra}>'
    return f'<img src="{_media_src(surface, s.card_asset())}" height="{height}"{extra}>'


def _cells_table(cells, cols: int) -> str:
    rows = []
    for i in range(0, len(cells), cols):
        row = cells[i:i + cols] + ["<td></td>"] * (cols - len(cells[i:i + cols]))
        rows.append("<tr>\n " + "\n ".join(row) + "\n</tr>")
    return "<table>\n" + "\n".join(rows) + "\n</table>"


def _card_cell(s, *, lang: str, surface: str, height: int, cols: int) -> str:
    media = _media_html(s, surface=surface, height=height)
    return (f'<td width="{100 // cols}%" align="center">'
            f'<a href="{_showcase_link(surface, s.name, lang)}">{media}</a><br>'
            f'<b>{s.title(lang)}</b><br><sub>{s.tagline(lang)}</sub></td>')


def _gif_cell(s, *, lang: str, surface: str, height: int, cols: int, caption: str) -> str:
    """A cell showing a showcase's build GIF (used by the feature-first layout).
    Prefers ``build_gif`` (when the primary ``gif`` is a gameplay/demo clip)."""
    return (f'<td width="{100 // cols}%" align="center">'
            f'<a href="{_showcase_link(surface, s.name, lang)}">'
            f'<img src="{_media_src(surface, s.build_gif or s.gif)}" height="{height}"></a><br>'
            f'<sub><b>{caption}</b></sub></td>')


def card_grid(showcases, *, lang: str, surface: str = "root", cols: int = 3,
              height: int = 150) -> str:
    """An N-column HTML card grid (media + title + tagline, linked to the showcase).
    Media is rendered at a uniform HEIGHT so rows align across mixed aspect ratios."""
    return _cells_table(
        [_card_cell(s, lang=lang, surface=surface, height=height, cols=cols)
         for s in showcases], cols)


def intro_region(manifest, *, lang: str) -> str:
    """Shared hero block (Beta announcement) reused in the root README and the docs
    00_Agent_Driven_Development intro. The per-category catchphrases live under each
    category heading (the "~20 min / ~$10" line belongs to the mini-games)."""
    return manifest.announcement(lang)


def _coming_soon_label(lang: str) -> str:
    return "곧 공개" if lang == "ko" else "coming soon"


def cardgrid_region(manifest, *, lang: str, cols: int = 2) -> str:
    """Root-README marker region: Beta announcement + per-category card grids (2-col)
    + links. A category with root_layout='feature-first' gives its first showcase a
    2-cell feature row (primary media | its build GIF) before the rest of the grid."""
    build_cap = "빌드 캡처 (timelapse)" if lang == "ko" else "build capture (timelapse)"
    sections = []
    for cat in manifest.categories:
        scs = manifest.by_category(cat.id)
        if cat.status == "coming-soon" or not scs:
            note = cat.note(lang) or _coming_soon_label(lang)
            sections.append(f"#### {cat.title(lang)} — _{note}_")
            continue
        blurb = f"{cat.blurb(lang)}\n\n" if cat.blurb(lang) else ""
        if cat.root_layout == "feature-first":
            feat, rest = scs[0], scs[1:]
            cells = [_card_cell(feat, lang=lang, surface="root", height=150, cols=cols),
                     _gif_cell(feat, lang=lang, surface="root", height=150, cols=cols,
                               caption=build_cap)]
            cells += [_card_cell(s, lang=lang, surface="root", height=150, cols=cols)
                      for s in rest]
            grid = _cells_table(cells, cols)
        else:
            grid = card_grid(scs, lang=lang, surface="root", cols=cols)
        sections.append(f"#### {cat.title(lang)}\n\n{blurb}{grid}")
    body = "\n\n".join(sections)
    if lang == "ko":
        link = ("**전체 showcase 목록 + 요약 →** "
                "[`dx-agent-dev-showcase/README-ko.md`](./dx-agent-dev-showcase/README-ko.md)  ·  "
                "**기능 설명 →** [Agent-Driven Development 문서](./docs/source/00_Agent_Driven_Development_kor.md)")
    else:
        link = ("**All showcases + summaries →** "
                "[`dx-agent-dev-showcase/README.md`](./dx-agent-dev-showcase/README.md)  ·  "
                "**About the feature →** [Agent-Driven Development docs](./docs/source/00_Agent_Driven_Development.md)")
    return f"{intro_region(manifest, lang=lang)}\n\n{body}\n\n{link}"


def showcase_table(showcases, *, lang: str, surface: str = "docs") -> str:
    """The all-showcase table (Showcase | what | build | turns | tokens | cost)."""
    if lang == "ko":
        head = "| Showcase | 설명 | 빌드 시간 | Agent turns | Output tokens | ~비용 |"
    else:
        head = "| Showcase | What it is | Build time | Agent turns | Output tokens | ~Cost |"
    rows = [head, "|---|---|---|---|---|---|"]
    for s in showcases:
        link = _showcase_link(surface, s.name, lang)
        rows.append(f"| **[{s.title(lang)}]({link})** | {s.what(lang)} | "
                    f"{s.build} | {s.turns} | {s.tokens} | {s.cost} |")
    return "\n".join(rows)


def categorized_table(manifest, *, lang: str, surface: str = "docs") -> str:
    """The all-showcase table grouped under per-category sub-headings, with a
    'coming soon' line for categories that have no showcases yet."""
    out = []
    for cat in manifest.categories:
        scs = manifest.by_category(cat.id)
        out.append(f"#### {cat.title(lang)}")
        if cat.blurb(lang):
            out.append(f"{cat.blurb(lang)}")
        if cat.status == "coming-soon" or not scs:
            out.append(f"> _{cat.note(lang) or _coming_soon_label(lang)}_")
        else:
            out.append(showcase_table(scs, lang=lang, surface=surface))
    return "\n\n".join(out)


def catalog_region(manifest, *, lang: str) -> str:
    """Catalog README marker region: per-category sections, each a summary table +
    per-showcase short blocks (media + what + detail link). Coming-soon categories
    show a note. This is the showcase index that mkdocs surfaces via include-markdown."""
    if lang == "ko":
        thead = "| Showcase | 유형 | 핵심 결과 |\n|---|---|---|"
        kind_label = {"game": "게임", "export": "export", "retrain": "재학습", "app": "앱"}
        detail, hi = "상세", "핵심"
    else:
        thead = "| Showcase | Kind | Highlight |\n|---|---|---|"
        kind_label = {"game": "game", "export": "export", "retrain": "retrain", "app": "app"}
        detail, hi = "details", "Highlight"

    out = []
    for cat in manifest.categories:
        scs = manifest.by_category(cat.id)
        out.append(f"## {cat.title(lang)}")
        if cat.blurb(lang):
            out.append(cat.blurb(lang))
        if cat.status == "coming-soon" or not scs:
            out.append(f"> _{cat.note(lang) or _coming_soon_label(lang)}_")
            continue
        table = [thead]
        for s in scs:
            link = _showcase_link("catalog", s.name, lang)
            table.append(f"| [{s.title(lang)}]({link}) | {kind_label.get(s.kind, s.kind)} | {s.highlight(lang)} |")
        out.append("\n".join(table))
        for s in scs:
            link = _showcase_link("catalog", s.name, lang)
            # uniform-height media floated right — keeps portrait (squat) from leaving a
            # big empty left column the way a fixed-width portrait GIF did.
            media = _media_html(s, surface="catalog", height=170, extra=' align="right"')
            out.append(
                f'### {s.title(lang)}\n\n'
                f'<a href="{link}">{media}</a>\n\n'
                f'{s.what(lang)}\n\n'
                f'**{hi}:** {s.highlight(lang)} · '
                f'**{s.model}** · {s.build} · {s.cost} — '
                f'[{detail} →]({link})\n\n'
                '<br clear="right">')
    return "\n\n".join(out)
