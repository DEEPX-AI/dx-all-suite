"""통합 App Shell(Option A)의 마크업 생성기.

8개 모듈이 레일·헤더·탭 HTML을 각자 복제하면 그 순간 shell이 다시 갈라진다.
서버 렌더 시점에 여기서 만들어 템플릿에 주입한다.
신규 의존성 없음 — 표준 라이브러리만 쓴다.

골격은 dx-shell.css가 그린다: 56px 레일 + 56px 헤더 + 42px 탭 행.
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


# launcher/static/launcher-state.js 의 _SPLASH_MODULES 와 같은 순서·같은 경로.
MODULES: tuple[Module, ...] = (
    Module("app", "DX App", "app", "/app/"),
    Module("stream", "DX Stream", "stream", "/stream/"),
    Module("zoo", "DX Model Zoo", "zoo", "/zoo/"),
    Module("compiler", "DX Compiler", "compiler", "/compiler/"),
    Module("edge", "DX EdgeGuide", "edge", "/planner/"),
    Module("bench", "DX Benchmark", "bench", "/benchmark/"),
    Module("monitor", "DX Monitor", "monitor", "/dx_monitor/"),
    Module("agent", "DX Agent Dev", "agent", "/agent/"),
)

_BY_KEY = {m.key: m for m in MODULES}


def _icon(name: str) -> str:
    return f'<svg aria-hidden="true"><use href="{ICONS}#{escape(name)}"></use></svg>'


def render_rail(active_key: str) -> str:
    """좌측 56px 모듈 레일."""
    if active_key not in _BY_KEY:
        raise ValueError(f"unknown module: {active_key!r}")

    # 모듈명(DX App 등)은 제품명이라 번역하지 않는다. 그 외 사람이 읽는 문자열은
    # data-i18n-* 로 내보내 shared/static/i18n.js 가 6개 로케일로 바꾼다 —
    # 영어로 굳으면 i18n audit이 High finding으로 잡는다.
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
    """56px 헤더 — 브랜드 > 페이지명 + 툴바 슬롯.

    module_name 은 브랜드가 마운트되기 전/실패 시를 위한 aria-label 로 쓴다
    (표시 텍스트는 brand.js 가 넣는다 — 둘 다 쓰면 이름이 두 번 보인다).

    header_extra 는 페이지명 오른쪽, 헤더 좌측 그룹 안에 들어간다 — 페이지 수준
    상태(dx_modelzoo 의 모델 개수 등)의 자리다. toolbar_extra 와 마찬가지로
    모듈이 소유한 신뢰 가능한 마크업이므로 escape 하지 않는다.

    .toolbar 는 DXToolbar.init 이 붙는 자리다. 문서 전체에 정확히 하나만
    있어야 하고(tests/test_shared_css_foundation.py 계약), 모듈 고유 컨트롤
    (dx_app 알림 벨 등)은 toolbar_extra 로 그 안에 들어간다 — 밖에 두면
    DXToolbar가 만드는 버튼들과 정렬이 어긋난다.

    toolbar_extra 는 모듈이 소유한 신뢰 가능한 마크업이므로 escape하지 않는다.
    """
    return (
        '<header class="dx-shell-header">'
        '<div class="dx-shell-header-left">'
        # DEEPX 브랜드 마운트 지점. 구 레이아웃에서는 240px 사이드바 상단이
        # 이 자리였다 — 사이드바가 사라졌으므로 헤더 좌측이 물려받는다.
        # brand.js 가 런타임에 채우므로 HTML은 비워 둔다.
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
    """42px 페이지 탭 행.

    pages: (page_id, English label — i18n 사전 키, icon id) 목록.
    단일 화면 모듈은 빈 목록을 넘겨 빈 문자열을 받는다 (.dx-shell--no-tabs).
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

    # 페이지 이동이다 (aria-current="page") — tab 패턴 (role=tablist/tab) 이 아니다. axe 2026-10-11.
    return (f'<nav class="dx-shell-tabs" aria-label="Pages" data-i18n-aria-label="Pages">'
            f'{"".join(tabs)}</nav>')


# ── 템플릿 주입 ────────────────────────────────────────────────
RAIL_SLOT = "{{DX_SHELL_RAIL}}"
HEADER_SLOT = "{{DX_SHELL_HEADER}}"
TABS_SLOT = "{{DX_SHELL_TABS}}"


@dataclass(frozen=True)
class ShellSpec:
    """모듈 하나가 shell에 대해 아는 전부.

    pages 가 비면 단일 화면 모듈이고 탭 행이 렌더되지 않는다
    (템플릿 루트에 .dx-shell--no-tabs 를 함께 붙인다).
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
    """템플릿의 {{DX_SHELL_*}} 자리를 채운다.

    spec 이 None 이면 원문 그대로 — 아직 이관하지 않은 모듈이 그렇다.
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
    """슬롯 이름 → 마크업 매핑.

    dx_compiler 처럼 자체 템플릿 엔진이 `{{ var }}` 를 컨텍스트에서 치환하는
    모듈용이다. 그쪽 엔진의 변수 패턴이 우리 슬롯 이름과 겹치므로, 문자열
    치환(apply)을 또 돌리는 대신 렌더 컨텍스트로 넘겨 한 번에 채운다.
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
