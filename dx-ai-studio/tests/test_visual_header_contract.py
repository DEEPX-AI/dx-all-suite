"""Visual Shell Header Contract Tests.

Checks that every surface's shell header follows the shared token contract.
"""
from pathlib import Path
import re

import pytest
from tests.css_rules import css_rule as _css_rule

ROOT = Path(__file__).resolve().parent.parent

SURFACES = {
    "launcher": ("launcher/static/index.html", "launcher/static/style.css"),
    # Modules on the shared App Shell have their header owned by dx-shell.css.
    "dx_app": ("dx_app/templates/index.html", "shared/static/dx-shell.css"),
    "dx_stream": ("dx_stream/templates/index.html", "shared/static/dx-shell.css"),
    "dx_compiler": ("dx_compiler/templates/base.html", "shared/static/dx-shell.css"),
    "dx_monitor": ("dx_monitor/templates/index.html", "shared/static/dx-shell.css"),
    "dx_planner": ("dx_planner/templates/index.html", "shared/static/dx-shell.css"),
    "dx_benchmark": ("dx_benchmark/templates/index.html", "shared/static/dx-shell.css"),
    "dx_modelzoo": ("dx_modelzoo/templates/index.html", "shared/static/dx-shell.css"),
}

# Topbar selector per module
HEADER_SELECTORS = {
    "launcher": ".top-bar",
    "dx_app": ".dx-shell-header",
    "dx_stream": ".dx-shell-header",
    "dx_compiler": ".dx-shell-header",
    "dx_monitor": ".dx-shell-header",
    "dx_planner": ".dx-shell-header",
    "dx_benchmark": ".dx-shell-header",
    "dx_modelzoo": ".dx-shell-header",
}

# Modules that use DXBrand.mount (the launcher may keep its custom .logo)
BRAND_MODULES = [
    "dx_app", "dx_stream", "dx_compiler",
    "dx_monitor", "dx_planner", "dx_benchmark", "dx_modelzoo",
]

SHARED_CSS_ORDER = [
    "/static/shared/module-chrome.css",
    "/static/shared/brand.css",
    "/static/shared/toolbar.css",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# Modules on the shared App Shell — header/brand/toolbar are injected at server render
# time, so reading the template file alone does not show them. Add a line per migrated module.
MIGRATED_SHELL_MODULES = {
    "dx_app": ("dx_app.server", "DX_APP_SHELL"),
    "dx_stream": ("dx_stream.server", "DX_STREAM_SHELL"),
    "dx_benchmark": ("dx_benchmark.server", "DX_BENCHMARK_SHELL"),
    "dx_monitor": ("dx_monitor.server", "DX_MONITOR_SHELL"),
    "dx_agent_dev": ("dx_agent_dev.server", "DX_AGENT_DEV_SHELL"),
    "dx_modelzoo": ("dx_modelzoo.server", "DX_MODELZOO_SHELL"),
    "dx_planner": ("dx_planner.server", "DX_PLANNER_SHELL"),
    "dx_compiler": ("dx_compiler.server", "DX_COMPILER_SHELL"),
}


def surface_html(name: str) -> str:
    """The HTML the server actually serves."""
    template_rel, _ = SURFACES[name]
    html = read_text(ROOT / template_rel)
    if name not in MIGRATED_SHELL_MODULES:
        return html

    import importlib

    mod_path, spec_name = MIGRATED_SHELL_MODULES[name]
    from shared.shell import apply as apply_shell

    return apply_shell(html, getattr(importlib.import_module(mod_path), spec_name))


class TestSharedCSSLoadOrder:
    """Every template loads module-chrome.css, brand.css and toolbar.css before its local CSS."""

    @pytest.mark.parametrize("name", SURFACES.keys())
    def test_shared_css_before_local(self, name):
        template_rel, css_rel = SURFACES[name]
        html = read_text(ROOT / template_rel)

        # The shared CSS files are referenced
        for href in SHARED_CSS_ORDER:
            base = href.split("?")[0]
            assert base in html, f"{name}: {href} missing from template"

        # Local CSS href (matched exactly against each module's local path)
        LOCAL_CSS_TOKENS = {
            "launcher": '/style.css',
            "dx_app": '/static/css/style.css',
            "dx_stream": '/static/css/stream.css',
            "dx_compiler": '/static/css/style.css',
            "dx_monitor": '/static/css/style.css',
            "dx_planner": '/static/css/style.css',
            "dx_benchmark": '/static/css/style.css',
            "dx_modelzoo": '/static/css/style.css',
        }
        local_token = LOCAL_CSS_TOKENS[name]

        # Shared CSS appears before local CSS
        toolbar_base = "/static/shared/toolbar.css"
        toolbar_pos = html.find(toolbar_base)
        assert toolbar_pos >= 0, f"{name}: toolbar.css not found"

        # Find it exactly as href="<local_token>"
        local_href = f'href="{local_token}'
        local_pos = html.find(local_href)
        if local_pos >= 0:
            assert toolbar_pos < local_pos, (
                f"{name}: shared toolbar.css must load before local {local_token}"
            )


class TestDXBrandSlot:
    """Every module that uses DXBrand.mount has id='dxBrand'."""

    @pytest.mark.parametrize("name", BRAND_MODULES)
    def test_brand_slot_has_id(self, name):
        html = surface_html(name)

        assert 'id="dxBrand"' in html, (
            f"{name}: id='dxBrand' 슬롯이 반드시 존재해야 한다"
        )

    @pytest.mark.parametrize("name", BRAND_MODULES)
    def test_brand_subtitle_has_spanish_locale(self, name):
        template_rel, _ = SURFACES[name]
        html = read_text(ROOT / template_rel)

        subtitle_match = re.search(r"subtitle:\s*\{(?P<body>.*?)\n\s*\}", html, re.S)
        assert subtitle_match, f"{name}: DXBrand subtitle map missing"
        subtitle_body = subtitle_match.group("body")

        assert re.search(r"(?:^|[\s,])(?:'es'|\"es\"|es)\s*:", subtitle_body), (
            f"{name}: DXBrand subtitle map must define es to avoid English fallback"
        )


class TestShellHeightUsesSharedToken:
    """Every module's shell height uses --dx-module-header-h or a documented responsive alias."""

    # Allowed height value patterns
    ALLOWED_HEIGHT_TOKENS = [
        "var(--dx-module-header-h)",
    ]

    # Allowed local aliases per module (the value must reference --dx-module-header-h)
    ALLOWED_LOCAL_ALIASES = {
        "launcher": "--launcher-topbar-h",
        "dx_benchmark": "--benchmark-topbar-h",
        "dx_planner": "--topbar-h",
    }

    @pytest.mark.parametrize("name", SURFACES.keys())
    def test_header_height_token(self, name):
        _, css_rel = SURFACES[name]
        css = read_text(ROOT / css_rel)
        selector = HEADER_SELECTORS[name]

        body = _css_rule(css, selector)

        # Find the height or min-height property
        height_match = re.search(
            r"(?:min-)?height\s*:\s*([^;]+)", body
        )
        if not height_match:
            pytest.skip(f"{name}: no height property on {selector}")

        height_val = height_match.group(1).strip()

        # Using --dx-module-header-h directly is always allowed
        if "var(--dx-module-header-h)" in height_val:
            return

        # A local alias must itself reference --dx-module-header-h
        if name in self.ALLOWED_LOCAL_ALIASES:
            alias = self.ALLOWED_LOCAL_ALIASES[name]
            if f"var({alias})" in height_val:
                # The alias definition references --dx-module-header-h
                alias_pattern = re.escape(alias) + r"\s*:\s*([^;]+)"
                alias_match = re.search(alias_pattern, css)
                assert alias_match, f"{name}: alias {alias} not defined"
                alias_def = alias_match.group(1).strip()
                assert "var(--dx-module-header-h)" in alias_def, (
                    f"{name}: alias {alias} must reference --dx-module-header-h, "
                    f"got: {alias_def}"
                )
                return

        pytest.fail(
            f"{name}: {selector} height uses {height_val!r}, "
            f"must use var(--dx-module-header-h) or an allowed alias"
        )


class TestShellStylesUseSharedTokens:
    """Every module's shell style uses the shared background/border/elevation tokens."""

    REQUIRED_TOKENS = [
        ("background", "var(--dx-module-header-bg)"),
        ("border-bottom", "var(--dx-module-header-border)"),
        ("box-shadow", "var(--dx-module-header-elevation)"),
    ]

    @pytest.mark.parametrize("name", SURFACES.keys())
    def test_header_uses_shared_tokens(self, name):
        _, css_rel = SURFACES[name]
        css = read_text(ROOT / css_rel)
        selector = HEADER_SELECTORS[name]

        body = _css_rule(css, selector)

        for prop_hint, token in self.REQUIRED_TOKENS:
            assert token in body, (
                f"{name}: {selector} missing {token}"
            )


class TestBackdropFilterOnShellHeaders:
    """Module shell headers other than the compiler's have a backdrop-filter.

    The compiler is excluded here; TestKnownExceptions checks it separately.
    """

    MODULES_REQUIRING_BACKDROP = [
        "dx_app", "dx_stream",
        "launcher", "dx_monitor", "dx_planner", "dx_benchmark", "dx_modelzoo",
    ]

    @pytest.mark.parametrize("name", MODULES_REQUIRING_BACKDROP)
    def test_backdrop_filter_present(self, name):
        _, css_rel = SURFACES[name]
        css = read_text(ROOT / css_rel)
        selector = HEADER_SELECTORS[name]

        body = _css_rule(css, selector)
        assert "backdrop-filter" in body, (
            f"{name}: {selector} missing backdrop-filter: var(--glass-blur)"
        )


class TestLanguageDropdownStacking:
    """The shared language dropdown in app/stream shows above content cards."""

    CONTENT_LAYER_MAX = 100
    POPUP_LAYER_MIN = 300

    @pytest.mark.parametrize("name", ["dx_app", "dx_stream"])
    def test_topbar_stacks_language_menu_between_content_and_popups(self, name):
        _, css_rel = SURFACES[name]
        css = read_text(ROOT / css_rel)
        header_sel = HEADER_SELECTORS[name]
        host_sel = (
            ".dx-shell-header-right" if header_sel == ".dx-shell-header" else ".topbar-right"
        )
        topbar = _css_rule(css, header_sel)
        toolbar_host = _css_rule(css, host_sel)

        normalized_topbar = topbar.replace(" ", "")
        topbar_z = re.search(r"z-index\s*:\s*(\d+)\s*;", topbar)
        assert "position:relative" in normalized_topbar, (
            f"{name}: {header_sel} must be positioned so z-index lifts "
            "the language dropdown above page cards"
        )
        assert topbar_z, f"{name}: {header_sel} must declare explicit z-index"
        topbar_z_value = int(topbar_z.group(1))
        assert topbar_z_value > self.CONTENT_LAYER_MAX, (
            f"{name}: {header_sel} must stack above page content layers"
        )
        assert topbar_z_value < self.POPUP_LAYER_MIN, (
            f"{name}: {header_sel} must stay below popup/modal layers"
        )
        assert "overflow:visible" in normalized_topbar, (
            f"{name}: {header_sel} must not clip the language dropdown menu"
        )

        normalized_host = toolbar_host.replace(" ", "")
        toolbar_z = re.search(r"z-index\s*:\s*(\d+)\s*;", toolbar_host)
        assert "position:relative" in normalized_host, (
            f"{name}: .topbar-right must create a positioned host for "
            "the shared language dropdown"
        )
        assert toolbar_z, f"{name}: .topbar-right must declare explicit z-index"
        assert int(toolbar_z.group(1)) >= 1



class TestShellHeaderZIndexLayerLadder:
    """The shared shell header sits above page content and below popups/modals.

    There is one header for every module, so the z-index ladder is checked in one place.
    """

    SHARED_POPUP_Z = 10000  # shared toolbar.css .dx-lang-menu
    CONTENT_LAYER_MAX = 100

    def _shell_header_z(self) -> int:
        css = read_text(ROOT / "shared/static/dx-shell.css")
        body = _css_rule(css, ".dx-shell-header")
        z = re.search(r"z-index\s*:\s*(\d+)", body)
        assert z, ".dx-shell-header must declare z-index"
        return int(z.group(1))

    def test_shell_header_sits_above_page_content(self):
        assert self._shell_header_z() > self.CONTENT_LAYER_MAX

    def test_shell_header_sits_below_the_shared_popup_layer(self):
        """A header above popups would hide the language dropdown behind it."""
        assert self._shell_header_z() < self.SHARED_POPUP_Z

    def test_shell_rail_sits_below_the_header(self):
        """A rail above the header would clip the header's dropdowns."""
        css = read_text(ROOT / "shared/static/dx-shell.css")
        rail = _css_rule(css, ".dx-shell-rail")
        z = re.search(r"z-index\s*:\s*(\d+)", rail)
        assert z, ".dx-shell-rail must declare z-index"
        assert int(z.group(1)) < self._shell_header_z()

    @pytest.mark.parametrize("name", sorted(MIGRATED_SHELL_MODULES))
    def test_migrated_module_content_stays_below_the_shell_header(self, name):
        """Module content above the header would cover it.

        Overlays (toast, modal, chat picker) belong above the header and are excluded —
        only the content layer is checked.
        """
        module_css_rel = {
            "dx_app": "dx_app/static/css/style.css",
            "dx_stream": "dx_stream/static/css/stream.css",
            "dx_benchmark": "dx_benchmark/static/css/style.css",
            "dx_monitor": "dx_monitor/static/css/style.css",
            "dx_agent_dev": "dx_agent_dev/static/css/console.css",
            "dx_modelzoo": "dx_modelzoo/static/css/style.css",
            "dx_planner": "dx_planner/static/css/style.css",
            "dx_compiler": "dx_compiler/static/css/style.css",
        }[name]
        css = read_text(ROOT / module_css_rel)
        header_z = self._shell_header_z()
        # Allowed above the header: popups/modals and floating widgets (chat FAB,
        # NPU monitor float). Covering the header is their intended behavior.
        overlay = re.compile(
            r"toast|modal|overlay|picker|menu|dropdown|lightbox|tooltip|drawer|popup"
            r"|chat|fab|float|widget|banner|spotlight|backdrop"
        )
        for m in re.finditer(r"([^{}]+)\{([^}]*z-index\s*:\s*(\d+)[^}]*)\}", css):
            selector, _body, z = m.group(1).strip().splitlines()[-1], m.group(2), int(m.group(3))
            if z <= header_z or overlay.search(selector.lower()):
                continue
            raise AssertionError(
                f"{name}: {selector!r} has z-index {z} above the shell header "
                f"({header_z}) but is not an overlay — it would cover the header"
            )


class TestKnownExceptions:
    """The documented exceptions hold."""

    def test_launcher_custom_logo_allowed_but_topbar_h_references_shared(self):
        """The launcher may keep its custom .logo, but --launcher-topbar-h must reference --dx-module-header-h."""
        css = read_text(ROOT / "launcher/static/style.css")
        # --launcher-topbar-h references --dx-module-header-h
        match = re.search(r"--launcher-topbar-h\s*:\s*([^;]+)", css)
        assert match, "--launcher-topbar-h not defined"
        val = match.group(1).strip()
        assert "var(--dx-module-header-h)" in val, (
            f"--launcher-topbar-h must reference --dx-module-header-h, got: {val}"
        )

    def test_compiler_no_longer_needs_the_hash_header_exception(self):
        """The compiler needs no #header exception: the shared shell owns its header.

        An exception kept without a reason gets copied by the next author, so none is kept.
        """
        css = read_text(ROOT / "dx_compiler/static/css/style.css")
        assert not re.search(r"^\s*#header\s*\{", css, re.M), (
            "#header 가 다시 생겼다 — 헤더는 shared/static/dx-shell.css 가 소유한다"
        )

    def test_benchmark_responsive_88px_via_named_alias(self):
        """The benchmark's responsive 88px height is allowed only via a named local alias or an explicit media rule."""
        css = read_text(ROOT / "dx_benchmark/static/css/style.css")

        # If 88px appears, it is allowed only inside an @media rule
        if "88px" in css:
            # 88px is inside an @media rule
            media_blocks = re.findall(r"@media[^{]*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}", css)
            found_in_media = any("88px" in block for block in media_blocks)
            assert found_in_media, (
                "benchmark 88px must appear only inside @media rule"
            )

            # 88px must be assigned to a named alias variable
            alias_pattern = r"--(?:benchmark-topbar-h|topbar-h)\s*:\s*88px"
            assert re.search(alias_pattern, css), (
                "benchmark 88px must be assigned to a named alias variable"
            )
