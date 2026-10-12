"""DX Stream server path constants and defaults.

Same layout as DX App's core/config.py.
Paths: SCRIPT_DIR(dx_stream/) → SUITE_ROOT(dx-all-suite/) → DX_STREAM_ROOT(dx-runtime/dx_stream/)
"""
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent          # dx_stream/
from shared.paths import SUITE_ROOT

# DX Stream source tree (DX_STREAM_ROOT overrides it)
DX_STREAM_ROOT = Path(os.environ["DX_STREAM_ROOT"]) if os.environ.get("DX_STREAM_ROOT") \
    else SUITE_ROOT / "dx-runtime" / "dx_stream"

# DX Runtime (dx_rt), used to parse model metadata
DX_RT_ROOT = SUITE_ROOT / "dx-runtime" / "dx_rt"

# Paths inside DX Stream
DX_STREAM_SRC = DX_STREAM_ROOT / "dx_stream"
SAMPLES_DIR = DX_STREAM_SRC / "samples"
MODELS_DIR = SAMPLES_DIR / "models"
VIDEOS_DIR = SAMPLES_DIR / "videos"
PIPELINES_DIR = DX_STREAM_SRC / "pipelines"
CONFIGS_DIR = DX_STREAM_SRC / "configs"
MODEL_LIST_JSON = DX_STREAM_ROOT / "model_list.json"

# Server directories
STATIC_DIR = SCRIPT_DIR / "static"
TEMPLATES_DIR = SCRIPT_DIR / "templates"

# Defaults
DEFAULT_PORT = 8093
SERVER_NAME = "DX Stream"
