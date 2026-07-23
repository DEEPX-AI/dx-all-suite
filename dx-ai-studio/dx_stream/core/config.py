"""DX Stream 서버 경로 상수 및 기본 설정.

DX App의 core/config.py 패턴을 따른다.
경로 계산: SCRIPT_DIR(dx_stream/) → SUITE_ROOT(dx-all-suite/) → DX_STREAM_ROOT(dx-runtime/dx_stream/)
"""
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent          # dx_stream/
from shared.paths import SUITE_ROOT

# DX Stream 소스 경로 (환경변수 오버라이드 지원)
DX_STREAM_ROOT = Path(os.environ["DX_STREAM_ROOT"]) if os.environ.get("DX_STREAM_ROOT") \
    else SUITE_ROOT / "dx-runtime" / "dx_stream"

# DX Runtime (dx_rt) 경로 — 모델 메타데이터 파싱용
DX_RT_ROOT = SUITE_ROOT / "dx-runtime" / "dx_rt"

# DX Stream 하위 경로
DX_STREAM_SRC = DX_STREAM_ROOT / "dx_stream"
SAMPLES_DIR = DX_STREAM_SRC / "samples"
MODELS_DIR = SAMPLES_DIR / "models"
VIDEOS_DIR = SAMPLES_DIR / "videos"
PIPELINES_DIR = DX_STREAM_SRC / "pipelines"
CONFIGS_DIR = DX_STREAM_SRC / "configs"
MODEL_LIST_JSON = DX_STREAM_ROOT / "model_list.json"

# 서버 디렉토리
STATIC_DIR = SCRIPT_DIR / "static"
TEMPLATES_DIR = SCRIPT_DIR / "templates"

# 기본 설정
DEFAULT_PORT = 8093
SERVER_NAME = "DX Stream"
