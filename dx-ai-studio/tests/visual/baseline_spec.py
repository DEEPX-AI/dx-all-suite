"""What the visual-regression suite captures, and why each knob is there.

`settle_ms` and `mask` are not guesses — each was measured by screenshotting the
same commit twice and requiring 0 changed pixels (see the module docstring in
test_visual_regression.py).
"""
from __future__ import annotations

import json
from pathlib import Path

VIEWPORT = {"width": 1280, "height": 800}

_DEFAULT_SETTLE_MS = 6000

SPECS: dict[str, dict] = {
    "launcher": {
        "settle_ms": 8000,                  # hub boots every module server first
        # The gateway row prints the live port, and the test harness binds an
        # ephemeral one — so the digits change every run. It is small enough to
        # sit near the 0.02% limit rather than over it, which is worse than a
        # clean failure: two of the four launcher shots flaked while the other
        # two passed. Masked, like dx_monitor's telemetry.
        "mask": ("#hubLauncherPort",),
    },
    # Five columns of this table depend on **what is installed locally** — models.js's
    # `dl = !!runnable` turns on the C++/PYTHON/MODE columns and adds a Graph button
    # under ACTIONS only for installed models. The whole table reflows, moving the
    # baseline by up to 22%. Installing models is normal use, so developers cannot be
    # asked to capture without them.
    #
    # The harness points at an empty models directory instead (DX_APP_MODELS_DIR in
    # tests/visual/conftest.py), so the picture is the same whatever is installed.
    "dx_app": {"settle_ms": _DEFAULT_SETTLE_MS},
    # The Dashboard's status cards show how far THIS host is set up (NPU, plugin, models
    # 0/17 → 17/17, sample videos), so running Stream Setup would change 8 baselines with no
    # code change. The capture answers /api/status with one fixed host instead — the cards are
    # still drawn and compared, only their numbers do not come from the machine.
    "dx_stream": {"settle_ms": _DEFAULT_SETTLE_MS, "routes": {"**/api/status": {
        "npu": {"ok": True, "devices": ["/dev/dxrt0"]},
        "gstreamer": {"ok": True, "installed": True, "plugin": True},
        "models": {"ok": False, "total": 17, "installed": 0, "missing": [], "installed_list": [],
                   "catalog_source": "manifest"},
        "videos": {"ok": False, "count": 0, "files": []},
        "build": {"ok": True, "path": "/usr/local/lib/gstreamer-1.0/libgstdxstream.so"},
        "webrtc": {"ok": False, "nice_plugin": False},
        "system_info": {"os": "Linux", "gstreamer_version": "GStreamer 1.24.2",
                        "npu_driver_version": "DXRT", "python_version": "3.12"},
        "catalog_source": "manifest",
    }}},
    # The Setup panel shows whether THIS host has dxcom and the samples (collapsed "Setup ready"
    # vs the expanded install steps), so installing dxcom would change 8 baselines with no code change.
    # The capture answers both status endpoints with one fixed, not-yet-set-up host.
    "dx_compiler": {"settle_ms": _DEFAULT_SETTLE_MS, "routes": {
        "**/setup/status": {
            "dx_com_installed": False, "dx_com_version": None, "venv_path": None, "venv_python": None,
            "sample_models": {name: {"downloaded": False, "onnx_path": None, "config_path": None}
                              for name in ("YOLOV5S-1", "YOLOV5S_Face-1", "MobileNetV2-1")},
            "calibration_data": {"downloaded": False, "path": None},
            "install_requires_sudo": True,
        },
        "**/feature-check": {"compile": False, "setup_available": True,
                             "capabilities": {"node_selection": False}, "warnings": []},
    }},
    "dx_modelzoo": {
        "settle_ms": _DEFAULT_SETTLE_MS,
        # These elements render slightly differently on each run, landing at 0.0205-0.0274% —
        # just over the 0.02% limit, so the gate would go red at random. Raising the limit
        # would also pass real regressions, so only the unstable elements are masked.
        #   #sortSelect       a native <select>'s value rendering wobbles per host and per run
        #   .mz-dx-app-status the dx_app connection dot — its colour follows the poll result
        #   #catalogSubtitle  "synced <date>" — the date changes whenever the gitignored local
        #                     catalog cache is rebuilt, unrelated to code. The header chip covers
        #                     the count; tests/dx_modelzoo/test_catalog_freshness.py the date.
        "mask": ("#sortSelect", ".mz-dx-app-status", "#catalogSubtitle"),
    },
    "dx_benchmark": {"settle_ms": _DEFAULT_SETTLE_MS},
    "dx_planner": {
        "settle_ms": _DEFAULT_SETTLE_MS,
        # Same failure as dx_modelzoo's #sortSelect, visible on the 1320-wide axis
        # where TARGET FPS comes into frame: Chromium draws a native
        # <select>'s value through the host font stack, and the resolution wobbles
        # between runs of one commit. Measured — five captures of the same commit
        # gave four at 0 px and one at 278 px in a 45×10 box holding the string
        # "30 FPS", against a 237 px budget. Waiting on document.fonts.ready does
        # not close it; the race is below the page. All three .ops-select controls
        # are the same control, so the mask covers the class rather than waiting
        # for each to scroll into a viewport and go red.
        "mask": (".ops-select",),
    },
    "dx_agent_dev": {
        "settle_ms": _DEFAULT_SETTLE_MS,
        # Showcase thumbnails are animated/lazily decoded, so a capture lands on
        # whichever frame happened to be up. Two captures taken back-to-back agree;
        # captures minutes apart drift 0.97-2.16%, so a stored baseline would not match.
        "mask": (".example-thumb",),
    },
    "dx_monitor": {
        "settle_ms": _DEFAULT_SETTLE_MS,
        # Live NPU/system telemetry. Unmasked this module drifts 0.0788% between
        # two captures of the same commit; masked it is pixel-identical.
        "mask": (
            "#chart-area",
            "#npu-topo",
            "#sysinfo-table",
            "#event-log",
            "#event-count",
            "#status-bar",
        ),
    },
}


# ── Capture axes ───────────────────────────────────────────────
# A single-axis baseline (1280 · en · dark) misses regressions in theme and copy.
# Semantic tokens / the light theme change colour and translation length changes layout,
# so both are axes.
THEMES = ("dark", "light")

# es has the longest labels (Benchmark -> Evaluación de rendimiento) and pushes tab
# overflow and header width. en is the reference.
LOCALES = ("en", "es")


def axes() -> list[tuple[str, str, str]]:
    """(module, theme, locale) combinations — the basis of the baseline file names."""
    return [
        (module, theme, locale)
        for module in sorted(SPECS)
        for theme in THEMES
        for locale in LOCALES
    ]


def baseline_name(module: str, theme: str, locale: str) -> str:
    return f"{module}__{theme}__{locale}.png"


# ── Responsive axis ────────────────────────────────────────────
# The baselines above are all 1280 wide, so they cannot show what changes when a
# breakpoint moves. The product switches layout at many widths (600·640·700·720·768·
# 769·900·960·980·1024·1100·1200·1280·1360·1440·1600·1979); consolidating them into a
# scale needs each range pinned first.
#
# Each width sits mid-range between breakpoints — capturing at a boundary flips the
# result on a 1px difference and makes the gate unstable.
#   650  = between 600 and 768   (just above where the grid folds to one column)
#   860  = between 768 and 900   (mobile → tablet range)
#   1150 = between 1100 and 1200 (tablet → desktop range)
#   1320 = between 1200 and 1440 (desktop → wide range)
RESPONSIVE_WIDTHS = (650, 860, 1150, 1320)
RESPONSIVE_HEIGHT = 900

# This axis checks layout, not colour, so one theme and locale is enough.
RESPONSIVE_THEME = "dark"
RESPONSIVE_LOCALE = "en"


def responsive_axes() -> list[tuple[str, int]]:
    return [(module, width) for module in sorted(SPECS) for width in RESPONSIVE_WIDTHS]


def responsive_baseline_name(module: str, width: int) -> str:
    return f"{module}__w{width}.png"


# ── Page axis ──────────────────────────────────────────────────
# The axes above capture landing pages. A page behind a tab whose content is drawn from data needs its own: the
# Graph Composer's canvas, palette and memory bar come from the graph API, so the capture answers it with fixed
# payloads (the catalog would show what THIS host has installed, the memory bar THIS host's NPU) and opens one
# shipped example. ko is the locale axis here instead of es: the canvas draws CJK text itself (DX CJK fonts), which
# a landing page never does.
_GRAPH_FIX = Path(__file__).resolve().parents[1] / "dx_app" / "fixtures" / "graph"


def _fixture(name: str):
    return json.loads((_GRAPH_FIX / name).read_text(encoding="utf-8"))


PAGE_SPECS: dict[str, dict] = {
    "dx_app_graph": {
        "module": "dx_app",
        "settle_ms": _DEFAULT_SETTLE_MS,
        "routes": {
            "**/api/graph/catalog*": _fixture("catalog.json"),
            "**/api/graph/validate": _fixture("visual_check.json"),
            "**/api/graph/memory": _fixture("visual_memory.json"),
            "**/api/graph/projects": {"projects": []},
        },
        "setup": "async () => { nav('graph'); await GraphComposer.open(); GraphComposer.loadExample('cascade_od_attr'); }",
        "wait": "() => { const s = GraphComposer.state(); return !!(s.check && s.memory); }",
    },
    # Phase 2: a scenario template with logic blocks, its zone block selected (the inspector's schema form and zone
    # preview), the Templates and Logic palette groups, the run panel's Run once / Live tabs.
    "dx_app_graph_logic": {
        "module": "dx_app",
        "settle_ms": _DEFAULT_SETTLE_MS,
        "routes": {
            "**/api/graph/catalog*": _fixture("visual_catalog_logic.json"),
            "**/api/graph/validate": _fixture("visual_check_logic.json"),
            "**/api/graph/memory": _fixture("visual_memory_logic.json"),
            "**/api/graph/projects": {"projects": []},
        },
        "setup": ("async () => { nav('graph'); await GraphComposer.open(); "
                  "GraphComposer.loadExample('zone_intrusion'); "
                  "GraphComposer.canvas().select({nodes: ['zone']}); }"),
        "wait": "() => { const s = GraphComposer.state(); return !!(s.check && s.memory) && !!document.querySelector('.gc-zone-preview'); }",
    },
    # Phase 3: the Export C++ project dialog over the cascade example, with the recorded plan (one model, one stub).
    "dx_app_graph_export": {
        "module": "dx_app",
        "settle_ms": _DEFAULT_SETTLE_MS,
        "routes": {
            "**/api/graph/catalog*": _fixture("catalog.json"),
            "**/api/graph/validate": _fixture("visual_check.json"),
            "**/api/graph/memory": _fixture("visual_memory.json"),
            "**/api/graph/projects": {"projects": []},
            "**/api/graph/export/plan": _fixture("export_plan.json"),
        },
        "setup": ("async () => { nav('graph'); await GraphComposer.open(); "
                  "GraphComposer.loadExample('cascade_od_attr'); await GraphExport.open(); }"),
        "wait": "() => !!(GraphExport.state().plan && document.querySelector('#gc-export-dialog[open] .gc-export-table')) && document.fonts.status === 'loaded'",
    },
}
PAGE_LOCALES = ("en", "ko")


def page_axes() -> list[tuple[str, str, str]]:
    return [(page, theme, locale) for page in sorted(PAGE_SPECS) for theme in THEMES for locale in PAGE_LOCALES]


def page_baseline_name(page: str, theme: str, locale: str) -> str:
    return f"{page}__{theme}__{locale}.png"


# ── Intro axis ─────────────────────────────────────────────────
# The baselines above plant dx-splash-seen before capture and skip the intro entirely.
# Capturing the animation by time is unstable even on one commit — the typing is off by
# a character and the sweep sits a few px elsewhere.
#
# So instead of waiting, the state is set directly — classes, data-beat and copy are set
# to their final values, then captured with animations="disabled". What gets pinned is
# "the settled hero", not "the screen at 2.6 s": timing changes stay green, composition
# changes go red.
#
# Repeat captures are pixel-identical (1280x800, 3 runs, 0/1024000 for hero and work).
# close is the intro's conclusion and matters most — quote and attribution must read
# together in one frame; if either breaks, the claim reads as ours.
INTRO_STATES = ("hero", "work", "close")


def intro_baseline_name(state: str) -> str:
    return f"launcher__intro__{state}.png"
