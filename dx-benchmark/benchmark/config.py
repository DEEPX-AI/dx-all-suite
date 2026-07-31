"""Benchmark configuration and defaults.

Central place for all tunable parameters, paths, and task definitions.
"""

from __future__ import annotations

import json
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ── Path resolution (package-relative) ─────────────────────────────────────
# The benchmark is standalone at runtime: it drives INSTALLED artifacts
# (gst dxstream plugin, run_model, postprocess .so libs) and keeps its own data
# under the package dir. No dx-all-suite source layout is required.
APP_DIR = Path(__file__).resolve().parent

# ── Default paths ──────────────────────────────────────────────────────────
MODEL_DIR = APP_DIR / "assets" / "models"
VIDEO_DIR = APP_DIR / "assets" / "videos"
# Installed dx_stream postprocess libraries (deployed by the DEEPX runtime).
POSTPROCESS_LIB_DIR = Path("/usr/local/share/gstdxstream/lib")
# Self-describing model manifest (single source of truth for download + catalog).
MODEL_LIST_JSON = APP_DIR / "model_list.json"

PROTOCOL_VERSION = "v1"  # v1: first public measurement methodology — adaptive buffer-count probe + pre-E2E cooldown
MULTI_STREAM_SEARCH_MODE = "single-stream-estimate-linear-boundary"
STABLE_CAPACITY_RULE = "status_ok_and_all_runs_success_and_avg_per_channel_fps_ge_threshold"

# ── Task definitions ──────────────────────────────────────────────────────
# model suffix → task name mapping
# Object detection models have no suffix (yolo26-n_640x640.dxnn) → mapped as "od"
TASK_MAP = {
    "od": "object_detection",
    "pose": "pose_estimation",
    "seg": "segmentation",
    "obb": "oriented_bbox",
    "cls": "classification",
}

# Tasks that support E2E (single-stream / multi-stream) pipeline benchmark.
# Classification uses a primary-mode postprocess library (libpostprocess_yolov26cls.so)
# and writes results to frame_meta directly, so it is fully supported in E2E.
E2E_SUPPORTED_TASKS = {"object_detection", "pose_estimation", "segmentation", "oriented_bbox", "classification"}

# Tasks that support multi-stream sweep benchmark.
# Classification is excluded: ~500 fps single-stream capacity means 15+ streams before
# the FPS threshold is hit, which takes a long time and has no practical use case.
MULTI_STREAM_SUPPORTED_TASKS = {"object_detection", "pose_estimation", "segmentation", "oriented_bbox"}

# Task groups for video selection:
#   Group 1 (CLS): classification – objects filling the frame
#   Group 2 (OD/Pose/Seg): detection, pose, segmentation – street/people scenes
#   Group 3 (OBB): oriented bounding box – aerial/rotated objects
TASK_GROUP_MAP = {
    "classification":   "cls",
    "object_detection": "od_pose_seg",
    "pose_estimation":  "od_pose_seg",
    "segmentation":     "od_pose_seg",
    "oriented_bbox":    "obb",
}

# Default video per task group
TASK_GROUP_VIDEOS = {
    "cls":          VIDEO_DIR / "od_benchmark_video.mp4",
    "od_pose_seg":  VIDEO_DIR / "od_benchmark_video.mp4",
    "obb":          VIDEO_DIR / "obb_benchmark_video.mp4",
}

# Model sizes in canonical order
SIZES = ["n", "s", "m", "l", "x"]

# ── Model metadata ─────────────────────────────────────────────────────────
# Static per-task metadata for the report model-info section.
# input_size: (W, H) fed to the model after preprocessing
# output: brief description of the model output
# postprocess: human-readable postprocess stage
TASK_MODEL_META = {
    "object_detection": {
        "input_size": (640, 640),
        "preprocess": "Letterbox resize + pad (pad=114), keep-ratio=true",
        "output": "Bounding boxes + class scores",
        "ort_offload": "Yes (NMS on CPU)",
    },
    "pose_estimation": {
        "input_size": (640, 640),
        "preprocess": "Letterbox resize + pad (pad=114), keep-ratio=true",
        "output": "Bounding boxes + 17 keypoints",
        "ort_offload": "Yes (NMS + keypoint decode on CPU)",
    },
    "segmentation": {
        "input_size": (640, 640),
        "preprocess": "Letterbox resize + pad (pad=114), keep-ratio=true",
        "output": "Bounding boxes + instance masks",
        "ort_offload": "Yes (NMS + mask decode on CPU)",
    },
    "oriented_bbox": {
        "input_size": (1024, 1024),
        "preprocess": "Letterbox resize + pad (pad=114), keep-ratio=true",
        "output": "Rotated bounding boxes (OBB)",
        "ort_offload": "Yes (NMS on CPU)",
    },
    "classification": {
        "input_size": (224, 224),
        "preprocess": "Direct resize, keep-ratio=false",
        "output": "Class index + confidence (ImageNet-1k)",
        "ort_offload": "No (pure NPU inference)",
    },
}

# ── Per-task pipeline configuration ───────────────────────────────────────
# Common preprocess settings (YOLO26 uses 640x640 letterbox for most tasks)
_COMMON_PREPROCESS = {
    "preprocess_id": 1,
    "resize_width": 640,
    "resize_height": 640,
    "pad_value": 114,
    "keep_ratio": True,
}
# OBB models require 1024x1024 input
_OBB_PREPROCESS = {
    "preprocess_id": 1,
    "resize_width": 1024,
    "resize_height": 1024,
    "pad_value": 114,
    "keep_ratio": True,
}
# Classification models require 224x224 input with no aspect-ratio padding
_CLS_PREPROCESS = {
    "preprocess_id": 1,
    "resize_width": 224,
    "resize_height": 224,
    "pad_value": 0,
    "keep_ratio": False,
}
_COMMON_INFERENCE = {
    "preprocess_id": 1,
    "inference_id": 1,
}

# Postprocess library per task suffix
TASK_POSTPROCESS_LIBS = {
    "od":   POSTPROCESS_LIB_DIR / "libpostprocess_yolo26od.so",
    "pose": POSTPROCESS_LIB_DIR / "libpostprocess_yolo26pose.so",
    "seg":  POSTPROCESS_LIB_DIR / "libpostprocess_yolo26seg.so",
    "obb":  POSTPROCESS_LIB_DIR / "libpostprocess_yolo26obb.so",
    "cls":  POSTPROCESS_LIB_DIR / "libpostprocess_yolo26cls.so",
}


def _resolve_postprocess_lib(task_suffix: str) -> Path:
    """Resolve postprocess library path from installed location."""
    lib = TASK_POSTPROCESS_LIBS.get(task_suffix)
    if lib is None:
        raise ValueError(f"No postprocess library configured for task suffix '{task_suffix}'")
    return lib


def get_task_preprocess(task_suffix: str = "") -> dict:
    if task_suffix == "obb":
        return dict(_OBB_PREPROCESS)
    if task_suffix == "cls":
        return dict(_CLS_PREPROCESS)
    return dict(_COMMON_PREPROCESS)


def get_task_inference() -> dict:
    return dict(_COMMON_INFERENCE)


def get_postprocess_config_path(task_suffix: str) -> Path:
    """Generate a temporary postprocess_config.json for the given task."""
    lib_path = _resolve_postprocess_lib(task_suffix)
    cfg = {
        "inference_id": 1,
        "library_file_path": str(lib_path),
        "function_name": "PostProcess",
    }
    # Write to a deterministic temp path so it persists for the benchmark run
    cfg_dir = Path(tempfile.gettempdir()) / "dx_benchmark_configs"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    cfg_path = cfg_dir / f"postprocess_{task_suffix}.json"
    with open(cfg_path, "w") as f:
        json.dump(cfg, f, indent=2)
    return cfg_path


@dataclass
class BenchmarkConfig:
    """Runtime benchmark configuration."""

    # ── Benchmark scope ───────────────────────────────────────────────
    task: str = "all"  # "all" runs every discovered task
    sizes: list = field(default_factory=lambda: list(SIZES))
    ort_modes: list = field(default_factory=lambda: [True, False])

    # ── Model-level params ────────────────────────────────────────────
    model_time_sec: int = 30        # duration of each throughput measurement (seconds, -t)
    model_latency_loops: int = 300  # inference loops per latency measurement (-l; run_model -s ignores -t)
    model_warmup: int = 1           # warmup runs before measurement
    model_warmup_retries: int = 1   # extra warmup attempts on timeout before giving up the cell
    model_run_retries: int = 2      # extra measured-run attempts to backfill failed runs up to the target count
    model_latency_runs: int = 1     # repeated measurements per latency benchmark
    model_throughput_runs: int = 3  # repeated measurements per throughput benchmark

    # ── buffer-count adaptive probe (protocol v1, throughput only) ────
    # Throughput vs run_model --buffer-count is a unimodal saturation curve; probe
    # ascending from the per-chip core-count floor and measure at the knee.
    buffer_count_probe_start: int = 3      # M1/M1M/H1 = 3 cores per chip
    buffer_count_probe_floor_max: int = 8  # always probe start..8 (covers default 6 + margin)
    buffer_count_probe_sec: int = 10       # per-probe duration (-t)
    buffer_count_probe_retries: int = 1    # retry a probe that returns 0 fps (transient stall)
    buffer_count_improve_eps: float = 0.01
    buffer_count_decline_eps: float = 0.02
    buffer_count_max_probe: int = 16

    # ── E2E pipeline params ───────────────────────────────────────────
    e2e_runs: int = 3               # repeated measurements per condition
    e2e_stall_timeout: float = 90.0   # no-progress window (s) → HANG
    e2e_hard_cap: float = 1800.0      # anti-runaway absolute ceiling (s)
    video: Optional[str] = None     # override video path (overrides per-task)

    # ── Multi-stream params ───────────────────────────────────────────
    fps_threshold: float = 30.0     # per-channel FPS threshold

    # ── NPU monitoring ────────────────────────────────────────────────
    npu_core_ids: list = field(default_factory=lambda: [0, 1, 2])
    npu_warmup_sec: float = 1.0
    npu_drain_sec: float = 0.5

    # ── Thermal steady-state (always enforced) ────────────────────────
    thermal_cooldown_target_delta_c: float = 10.0  # target Δ from idle temp for cooldown
    thermal_cooldown_abs_cap_c: float = 55.0  # hard cap for cooldown target temperature
    thermal_hot_start_block_c: float = 60.0  # abort benchmark start above this temperature
    thermal_cooldown_max_sec: float = 1000.0   # max cooldown wait seconds
    thermal_idle_temp_c: Optional[float] = None  # measured at start; None = auto-detect

    # ── Device-death circuit breaker (conservative abort) ─────────────
    # Abort the run ONLY when a dxrt-cli liveness probe confirms the device is
    # unrecoverable (DEAD). An ALIVE device never aborts — the failed cell is
    # recorded and the run continues, exactly as before.
    enable_circuit_breaker: bool = True     # master switch for the abort-on-dead logic
    device_probe_timeout_sec: int = 15      # dxrt-cli -s liveness probe timeout
    circuit_breaker_backstop_models: int = 2  # last-resort: N consecutive fully-failed models (device ALIVE) → abort

    # ── Output ────────────────────────────────────────────────────────
    output_dir: Optional[str] = None
    # ── Product info (optional, shown in report Environment) ───────
    product_name: Optional[str] = None
    # ── dx-all-suite version (optional; shown in Version Trend axis) ──
    dx_all_suite_version: Optional[str] = None

    def get_video(self, task: str | None = None) -> Path:
        """Get video path, optionally task-specific."""
        if self.video:
            return Path(self.video)
        if task:
            group = TASK_GROUP_MAP.get(task, "od_pose_seg")
            return TASK_GROUP_VIDEOS.get(group, TASK_GROUP_VIDEOS["od_pose_seg"])
        return TASK_GROUP_VIDEOS["od_pose_seg"]

    def get_output_dir(self) -> Path:
        if self.output_dir:
            return Path(self.output_dir)
        # Results live at the dx-benchmark root (sibling of the package), so the
        # per-run raw data is git-tracked and results/dashboard/ is git-ignored.
        return APP_DIR.parent / "results"


def get_protocol_metadata(cfg: BenchmarkConfig) -> dict:
    """Return the fixed measurement protocol metadata for the current run."""
    return {
        "version": PROTOCOL_VERSION,
        "thermal_mode": "steady",
        "model_time_sec": cfg.model_time_sec,
        "model_latency_loops": cfg.model_latency_loops,
        "model_warmup_runs": cfg.model_warmup,
        "model_warmup_retries": cfg.model_warmup_retries,
        "model_run_retries": cfg.model_run_retries,
        "model_latency_runs": cfg.model_latency_runs,
        "model_throughput_runs": cfg.model_throughput_runs,
        "buffer_count_probe_start": cfg.buffer_count_probe_start,
        "buffer_count_probe_floor_max": cfg.buffer_count_probe_floor_max,
        "buffer_count_probe_sec": cfg.buffer_count_probe_sec,
        "buffer_count_probe_retries": cfg.buffer_count_probe_retries,
        "buffer_count_max_probe": cfg.buffer_count_max_probe,
        "e2e_runs": cfg.e2e_runs,
        "e2e_stall_timeout": cfg.e2e_stall_timeout,
        "e2e_hard_cap": cfg.e2e_hard_cap,
        "fps_threshold": cfg.fps_threshold,
        "multi_stream_search": MULTI_STREAM_SEARCH_MODE,
        "stable_capacity_rule": STABLE_CAPACITY_RULE,
        "ort_modes": ["ON", "OFF"],

        "thermal_cooldown_target_delta_c": cfg.thermal_cooldown_target_delta_c,
        "thermal_cooldown_abs_cap_c": cfg.thermal_cooldown_abs_cap_c,
        "thermal_hot_start_block_c": cfg.thermal_hot_start_block_c,
        "thermal_cooldown_max_sec": cfg.thermal_cooldown_max_sec,
        "npu_warmup_sec": cfg.npu_warmup_sec,
        "npu_drain_sec": cfg.npu_drain_sec,

        "enable_circuit_breaker": cfg.enable_circuit_breaker,
        "device_probe_timeout_sec": cfg.device_probe_timeout_sec,
        "circuit_breaker_backstop_models": cfg.circuit_breaker_backstop_models,
    }
