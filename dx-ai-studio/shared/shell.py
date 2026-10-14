"""Markup generator for the shared App Shell.

If each of the 9 modules copied the rail / header / tab HTML, the shells would drift apart.
It is built here at server render time and injected into the templates. Standard library only.

dx-shell.css draws the frame: 56px rail + 56px header + 42px tab row.
"""
from __future__ import annotations

from dataclasses import dataclass
from html import escape

ICONS = "/static/shared/dx-icons.svg"


@dataclass(frozen=True)
class Module:
    key: str
    name: str
    icon: str
    path: str


# Same order and paths as _SPLASH_MODULES in launcher/static/launcher-state.js.
MODULES: tuple[Module, ...] = (
    Module("app", "DX App", "app", "/app/"),
    Module("stream", "DX Stream", "stream", "/stream/"),
    Module("zoo", "DX Model Zoo", "zoo", "/zoo/"),
    Module("compiler", "DX Compiler", "compiler", "/compiler/"),
    Module("edge", "DX EdgeGuide", "edge", "/planner/"),
    Module("bench", "DX Benchmark", "bench", "/benchmark/"),
    Module("monitor", "DX Monitor", "monitor", "/dx_monitor/"),
    Module("agent", "DX Agent Dev", "agent", "/agent/"),
    # "edge" is taken by DX EdgeGuide (dx_planner), so DX Edge is "cloud" here.
    Module("cloud", "DX Edge", "cloud", "/edge/"),
)

_BY_KEY = {m.key: m for m in MODULES}


def _icon(name: str) -> str:
    return f'<svg aria-hidden="true"><use href="{ICONS}#{escape(name)}"></use></svg>'


def render_rail(active_key: str) -> str:
    """The 56px module rail on the left."""
    if active_key not in _BY_KEY:
        raise ValueError(f"unknown module: {active_key!r}")

    # Module names (DX App etc.) are product names and are not translated. Every other
    # human-readable string goes out as data-i18n-* so shared/static/i18n.js can
    # translate it into the 6 locales.
    items = []
    for m in MODULES:
        current = ' aria-current="page"' if m.key == active_key else ""
        items.append(
            f'<a class="dx-rail-btn" href="{escape(m.path)}"'
            f' title="{escape(m.name)}" aria-label="{escape(m.name)}"{current}>'
            f"{_icon(m.icon)}</a>"
        )

    active = _BY_KEY[active_key]
    return (
        '<nav class="dx-shell-rail" aria-label="Modules" data-i18n-aria-label="Modules">'
        f'<div class="dx-shell-rail-mark">{_icon(active.icon)}</div>'
        f'<div class="dx-shell-rail-list">{"".join(items)}</div>'
        '<div class="dx-shell-rail-foot">'
        '<a class="dx-rail-btn" href="/" title="Hub" aria-label="Hub"'
        ' data-i18n-title="Hub" data-i18n-aria-label="Hub">'
        f"{_icon('home')}</a></div>"
        "</nav>"
    )


def render_header(
    module_name: str,
    page_title: str,
    toolbar_extra: str = "",
    header_extra: str = "",
) -> str:
    """56px header — brand > page name + toolbar slot.

    module_name becomes the aria-label used before the brand mounts or if it fails
    (brand.js inserts the visible text — writing both would show the name twice).

    header_extra goes right of the page name, inside the header's left group — the
    place for page-level status (e.g. dx_modelzoo's model count). Like toolbar_extra
    it is trusted markup owned by the module and is not escaped.

    .toolbar is where DXToolbar.init attaches. There must be exactly one in the
    document (contract: tests/test_shared_css_foundation.py); module-specific controls
    (e.g. the dx_app notification bell) go inside it via toolbar_extra — outside it
    they would not line up with the buttons DXToolbar creates.

    toolbar_extra is trusted markup owned by the module and is not escaped.
    """
    return (
        '<header class="dx-shell-header">'
        '<div class="dx-shell-header-left">'
        # DEEPX brand mount point. brand.js fills it at runtime, so the HTML
        # stays empty.
        f'<div class="dx-brand-slot" id="dxBrand" aria-label="{escape(module_name)}"></div>'
        f'<span class="dx-shell-sep">{_icon("chev")}</span>'
        f'<span class="dx-shell-page" id="dxShellPage">{escape(page_title)}</span>'
        f"{header_extra}"
        "</div>"
        '<div class="dx-shell-header-right toolbar">'
        f"{toolbar_extra}"
        "</div>"
        "</header>"
    )


def render_tabs(pages: list[tuple[str, str, str]], active: str | None) -> str:
    """The 42px page tab row.

    pages: list of (page_id, English label — the i18n dictionary key, icon id).
    Single-screen modules pass an empty list and get an empty string (.dx-shell--no-tabs).
    """
    if not pages:
        return ""

    tabs = []
    for page_id, label, icon in pages:
        current = ' aria-current="page"' if page_id == active else ""
        tabs.append(
            f'<button class="dx-tab" type="button" data-page="{escape(page_id)}"{current}>'
            f"{_icon(icon)}"
            f'<span data-i18n="{escape(label)}">{escape(label)}</span>'
            "</button>"
        )

    # This is page navigation (aria-current="page"), not the tab pattern (role=tablist/tab).
    return (f'<nav class="dx-shell-tabs" aria-label="Pages" data-i18n-aria-label="Pages">'
            f'{"".join(tabs)}</nav>')


# ── Template injection ─────────────────────────────────────────
RAIL_SLOT = "{{DX_SHELL_RAIL}}"
HEADER_SLOT = "{{DX_SHELL_HEADER}}"
TABS_SLOT = "{{DX_SHELL_TABS}}"


@dataclass(frozen=True)
class ShellSpec:
    """Everything a module knows about the shell.

    Empty pages means a single-screen module and no tab row is rendered
    (the template root also carries .dx-shell--no-tabs).
    """

    module_key: str
    pages: tuple[tuple[str, str, str], ...] = ()
    active_page: str | None = None
    toolbar_extra: str = ""
    header_extra: str = ""

    def page_title(self) -> str:
        for page_id, label, _icon_id in self.pages:
            if page_id == self.active_page:
                return label
        return _BY_KEY[self.module_key].name


def apply(html: str, spec: ShellSpec | None) -> str:
    """Fill the template's {{DX_SHELL_*}} slots.

    With spec None the HTML is returned unchanged (a module not on the shell).
    """
    if spec is None:
        return html
    module = _BY_KEY[spec.module_key]
    return (
        html.replace(RAIL_SLOT, render_rail(spec.module_key))
        .replace(
            HEADER_SLOT,
            render_header(
                module.name,
                spec.page_title(),
                spec.toolbar_extra,
                spec.header_extra,
            ),
        )
        .replace(TABS_SLOT, render_tabs(list(spec.pages), spec.active_page))
    )


def context(spec: "ShellSpec | None") -> dict[str, str]:
    """Slot name → markup.

    For modules like dx_compiler whose own template engine substitutes `{{ var }}`
    from a context. That engine's variable pattern overlaps our slot names, so
    rather than running apply() as well, the slots go into the render context.
    """
    if spec is None:
        return {}
    module = _BY_KEY[spec.module_key]
    return {
        "DX_SHELL_RAIL": render_rail(spec.module_key),
        "DX_SHELL_HEADER": render_header(
            module.name, spec.page_title(), spec.toolbar_extra, spec.header_extra
        ),
        "DX_SHELL_TABS": render_tabs(list(spec.pages), spec.active_page),
    }
