"""DX Monitor 서버 경로 상수 및 기본 설정.

DX Stream의 core/config.py 패턴을 따른다.
경로 계산: SCRIPT_DIR(dx_monitor/) → SUITE_ROOT(dx-all-suite/) → SDK 경로
"""
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent          # dx_monitor/
STUDIO_DIR = SCRIPT_DIR.parent                               # dx-ai-studio/

from shared.paths import SUITE_ROOT

# DX App 경로 (release.ver 등 참조용)
DX_APP_ROOT = STUDIO_DIR / "dx_app"

# 서버 디렉토리
STATIC_DIR = SCRIPT_DIR / "static"
TEMPLATES_DIR = SCRIPT_DIR / "templates"

# 기본 설정
DEFAULT_PORT = 8098
SERVER_NAME = "DX Monitor"

# 임계치 상수 — 프론트엔드로 /api/system_info를 통해 전달
THRESHOLDS = {
    "npu_temp":  {"warn": 70, "crit": 85, "unit": "°C"},
    "core_temp": {"warn": 70, "crit": 85, "unit": "°C"},
    "npu_dram":  {"warn": 80, "crit": 95, "unit": "%"},
    "memory":    {"warn": 80, "crit": 95, "unit": "%"},
    "cpu_load":  {"warn_factor": 0.8, "crit_factor": 1.0, "note": "×cpu_cores"},
}
