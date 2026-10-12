"""DX Monitor server path constants and defaults.

Follows the DX Stream core/config.py pattern.
Path resolution: SCRIPT_DIR (dx_monitor/) → SUITE_ROOT (dx-all-suite/) → SDK paths
"""
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent          # dx_monitor/
STUDIO_DIR = SCRIPT_DIR.parent                               # dx-ai-studio/

from shared.paths import SUITE_ROOT

# DX App path (for release.ver and similar)
DX_APP_ROOT = STUDIO_DIR / "dx_app"

# Server directories
STATIC_DIR = SCRIPT_DIR / "static"
TEMPLATES_DIR = SCRIPT_DIR / "templates"

# Defaults
DEFAULT_PORT = 8098
SERVER_NAME = "DX Monitor"

# Threshold constants — sent to the frontend via /api/system_info
THRESHOLDS = {
    "npu_temp":  {"warn": 70, "crit": 85, "unit": "°C"},
    "core_temp": {"warn": 70, "crit": 85, "unit": "°C"},
    "npu_dram":  {"warn": 80, "crit": 95, "unit": "%"},
    "memory":    {"warn": 80, "crit": 95, "unit": "%"},
    "cpu_load":  {"warn_factor": 0.8, "crit_factor": 1.0, "note": "×cpu_cores"},
}
