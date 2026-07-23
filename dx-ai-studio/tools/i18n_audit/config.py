from __future__ import annotations

from pathlib import PurePosixPath

LANGUAGES = ("en", "ja", "ko", "es", "zh-CN", "zh-TW")
DISPLAY_ORDER = ("EN", "JA", "KO", "ES", "简", "繁")

MODULES = {
    "launcher": ("launcher",),
    "dx_app": ("dx_app",),
    "dx_stream": ("dx_stream",),
    "dx_modelzoo": ("dx_modelzoo",),
    "dx_compiler": ("dx_compiler",),
    "dx_planner": ("dx_planner",),
    "dx_benchmark": ("dx_benchmark",),
    "dx_monitor": ("dx_monitor",),
    "dx_agent_dev": ("dx_agent_dev",),
    "shared": ("shared",),
}

SOURCE_EXTENSIONS = (".html", ".js", ".json", ".py")

BRAND_TERMS = {
    "DX AI Studio",
    "DX App",
    "DX Stream",
    "DX Model Zoo",
    "DX Compiler",
    "DX EdgeGuide",
    "DX Benchmark",
    "DX Monitor",
    "DX Agent Dev",
    "DX All Suite",
    "DX Runtime",
    "DX Firmware",
    "DXNN SDK",
    "ModelZoo",
    "EdgeGuide",
    "NPU",
    "SDK",
    "DX-M1",
    "DX-H1",
    "GStreamer",
    "WebRTC",
    "OpenCV",
    "Netron",
}

_EXCLUDED_PARTS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "tests",
    "dc_dx_studio",
    ".venv",
    ".venv-i18n-audit",
    "venv",
    "site-packages",
}

_EXCLUDED_PREFIXES = (
    "docs/superpowers/reports/",
    "docs/site/",
    "tools/data/",
    "shared/static/vendor/mermaid.min.js",
    "CHECKLIST.html",
    "dx_modelzoo/data/generated_catalog.json",
    "dx_modelzoo/data/generated_catalog.cache.json",
    "dx_modelzoo/data/sync_report.json",
    "dx_modelzoo/data/metadata_sync_config.json",
)


def is_excluded_path(rel_path: str) -> bool:
    if any(rel_path.startswith(prefix) for prefix in _EXCLUDED_PREFIXES):
        return True
    parts = set(PurePosixPath(rel_path).parts)
    return bool(parts & _EXCLUDED_PARTS) or rel_path.endswith(".pyc")
