"""DX Compiler Configuration — paths, constants, and shared state."""
import hashlib
import os
import tempfile
from pathlib import Path

from shared.paths import SUITE_ROOT, is_safe_path as _shared_is_safe_path, var_dir

SCRIPT_DIR    = Path(__file__).resolve().parent.parent   # dx_compiler/
STATIC_DIR    = SCRIPT_DIR / "static"
TEMPLATES_DIR = SCRIPT_DIR / "templates"
CORE_DIR      = SCRIPT_DIR / "core"
SDK_ROOT      = SUITE_ROOT / "dx-compiler"               # SDK 패키지 (install.sh, example/)
SDK_EXAMPLE   = SDK_ROOT / "example"
SDK_PROPS     = SDK_ROOT / "compiler.properties"
SAMPLE_MODELS_DIR = SDK_ROOT / "dx_com" / "sample_models"
CALIB_DIR         = SDK_ROOT / "dx_com" / "calibration_dataset"

DEFAULT_PORT = 8095
SERVER_NAME  = "DX Compiler"

UPLOAD_DIR = var_dir("compiler", "uploads")

# Allowed base directories for file-system access.
_ALLOWED_ROOTS: list = [
    Path("/home"), Path("/tmp"), Path(tempfile.gettempdir()),
    Path("/data"), Path("/mnt"), Path("/opt"),
]


def is_safe_path(p: str) -> bool:
    """Check that *p* resolves to a location under an allowed root."""
    try:
        Path(p).resolve()
    except (OSError, ValueError):
        return False
    return _shared_is_safe_path(p, [UPLOAD_DIR] + _ALLOWED_ROOTS)


def static_version() -> str:
    """Generate a short hash from key static file contents for cache-busting."""
    h = hashlib.md5()
    for name in (
        "compiler-i18n.js",
        "viewer_panel.js",
        "config_wizard.js",
        "setup_panel.js",
        "tutorial.js",
        "graph_renderer.js",
        "graph_viewer.js",
    ):
        p = STATIC_DIR / "js" / name
        if p.exists():
            h.update(p.read_bytes())
    for name in ("graph_viewer.css", "style.css"):
        p = STATIC_DIR / "css" / name
        if p.exists():
            h.update(p.read_bytes())
    return h.hexdigest()[:8]
