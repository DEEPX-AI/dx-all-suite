#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
Synchronous inference runner using factory pattern.

Provides a generic runner that accepts any factory implementation,
mirroring the C++ SyncDetectionRunner / SyncClassificationRunner / etc.

Usage:
    from common.runner import SyncRunner
    from factory import Yolov5Factory
    runner = SyncRunner(Yolov5Factory())
    runner.run(parse_args())
"""

import glob
import os
import subprocess
import sys
import time
import traceback
import logging
from pathlib import Path
from typing import Callable, Dict, List, Optional, Union

import numpy as np
import cv2

from dx_engine import InferenceEngine, InferenceOption
from ..config import load_config
from ..utility import print_image_processing_summary, print_sync_performance_summary
from .run_dir import create_run_dir, write_run_info, dump_tensors, dump_tensors_on_exception
from .verify_serialize import is_verify_enabled, dump_verify_json

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

_MSG_HEADLESS_SKIP = "Headless environment - display skipped"


def _has_display() -> bool:
    """Return True if a graphical display server is available."""
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


def _window_should_close(winname: str = "Output") -> bool:
    """Return True if user requested quit (q/ESC) or closed the window.

    This handles both keypress and window-close (X) events. When window is
    closed we destroy the window to avoid stale state.
    """
    if not _has_display():
        return False
    try:
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q") or key == 27:
            return True
    except Exception:
        pass
    try:
        # getWindowProperty returns -1 when window was destroyed (user closed),
        # 0 during initial creation on some backends, and 1 when fully visible.
        # Use <= 0 to detect window closed; the probe-based approach in C++
        # handles GTK2 backends that always return -1.
        vis = cv2.getWindowProperty(winname, cv2.WND_PROP_VISIBLE)
        if vis <= 0.0:
            return True
    except Exception:
        pass
    return False

# ======================================================================
# Metrics helpers (sync — 7 fields)
# ======================================================================

_SYNC_METRIC_KEYS = (
    "sum_read",
    "sum_preprocess",
    "sum_inference",
    "sum_postprocess",
    "sum_render",
    "sum_save",
    "sum_display",
)


def _create_sync_metrics() -> Dict[str, float]:
    return dict.fromkeys(_SYNC_METRIC_KEYS, 0.0)


def _add_sync_metrics(dst: Dict[str, float], src: Dict[str, float]) -> None:
    for k in _SYNC_METRIC_KEYS:
        dst[k] += src.get(k, 0.0)


# ======================================================================
# DX-RT version check
# ======================================================================

def _check_dxrt_version(minimum: str = "3.0.0") -> None:
    """Exit early if DX-RT is too old."""
    try:
        from dx_engine import Configuration
        from packaging import version
        rt_ver = Configuration().get_version()
        if version.parse(rt_ver) < version.parse(minimum):
            logger.error(f"DX-RT v{minimum} or higher is required "
                f"(current: {rt_ver}). Please update DX-RT.")
            sys.exit(1)
    except ImportError:
        pass


def _check_model_version(ie, minimum_format: int = 7) -> None:
    """Warn if model format version is too old."""
    try:
        fmt_ver = ie.get_model_version()
        if isinstance(fmt_ver, int) and fmt_ver < minimum_format:
            logger.warning(f"Model format version ({fmt_ver}) is older than "
                f"recommended minimum ({minimum_format}). "
                f"Re-compile with latest DX-Compiler for best results.")
    except (AttributeError, RuntimeError):
        pass  # API not available or model doesn't report version


_DEFAULT_DISPLAY_SIZE = (960, 640)


# ======================================================================
# Config / loop resolution
# ======================================================================

def _resolve_config_path(args) -> Optional[str]:
    """Locate config.json next to model or next to the main script."""
    config_path = getattr(args, "config", None)
    if config_path is not None:
        return config_path
    candidate = os.path.join(os.path.dirname(args.model), "config.json")
    if os.path.isfile(candidate):
        return candidate
    import __main__
    pkg_dir = os.path.dirname(os.path.abspath(
        getattr(__main__, '__file__', '')))
    candidate = os.path.join(pkg_dir, "config.json")
    return candidate if os.path.isfile(candidate) else None


def _parse_loop_value(args) -> int:
    """Normalise the --loop argument to an integer >= 1."""
    loop_val = getattr(args, "loop", 1)
    if isinstance(loop_val, bool):
        return 2 if loop_val else 1
    if isinstance(loop_val, int):
        return max(1, loop_val)
    return 1


# ======================================================================
# Default sample image per task type (bundled in sample/)
# ======================================================================

_IMG_STREET = "sample/img/sample_street.jpg"
_IMG_PARKING = "sample/img/sample_parking.jpg"
_VID_DANCE_GROUP = "assets/videos/dance-group.mov"
_VID_BLACKBOX = "assets/videos/blackbox-city-road.mp4"
_VID_DOGS = "assets/videos/dogs.mp4"
_VID_SNOWBOARD = "assets/videos/snowboard.mp4"

_DEFAULT_SAMPLE_IMAGE = {
    "object_detection":       _IMG_STREET,
    "face_detection":         "sample/img/sample_face.jpg",
    "obb_detection":          "sample/dota8_test/P0284.png",
    "pose_estimation":        "sample/img/sample_people.jpg",
    "hand_landmark":          "sample/img/sample_hand.jpg",
    "face_alignment":         "sample/img/sample_face_a1.jpg",
    "instance_segmentation":  _IMG_STREET,
    "semantic_segmentation":  _IMG_PARKING,
    "classification":         "sample/img/sample_dog.jpg",
    "depth_estimation":       _IMG_PARKING,
    "image_denoising":        "sample/img/sample_denoising.jpg",
    "super_resolution":       "sample/img/sample_superresolution.png",
    "image_enhancement":      "sample/img/sample_lowlight.jpg",
    "embedding":              "sample/img/face_pair",
    "attribute_recognition":  "sample/img/sample_person_a1.jpg",
    "reid":                   "sample/img/person_pair",
    "ppu":                    _IMG_STREET,
}

# ======================================================================
# Default sample video per task type (downloaded to assets/videos/)
# ======================================================================

_DEFAULT_SAMPLE_VIDEO = {
    "object_detection":       _VID_SNOWBOARD,
    "face_detection":         _VID_DANCE_GROUP,
    "obb_detection":          "assets/videos/obb.mp4",
    "pose_estimation":        "assets/videos/dance-solo.mov",
    "hand_landmark":          "assets/videos/hand.mp4",
    "face_alignment":         "assets/videos/face-alignment-closeup.mp4",
    "instance_segmentation":  _VID_DOGS,
    "semantic_segmentation":  _VID_BLACKBOX,
    "classification":         _VID_DOGS,
    "depth_estimation":       _VID_BLACKBOX,
    "image_denoising":        "assets/videos/noisy_hand.mp4",
    "super_resolution":       _VID_DANCE_GROUP,
    "image_enhancement":      "assets/videos/lowlight.mp4",
    "embedding":              None,   # image-only task
    "attribute_recognition":  None,   # image-only task
    "reid":                   None,   # image-only task
    "ppu":                    _VID_SNOWBOARD,
}


def _apply_default_input(args, factory=None) -> None:
    """If no input source was specified, fall back to a bundled sample image."""
    has_input = any([
        getattr(args, "image", None),
        getattr(args, "video", None),
        getattr(args, "camera", None) is not None and getattr(args, "camera", None) != -1,
        getattr(args, "rtsp", None),
    ])
    if has_input:
        return

    task_type = factory.get_task_type() if factory else None
    default_image = _DEFAULT_SAMPLE_IMAGE.get(
        task_type, "sample/img/sample_street.jpg")
    args.image = default_image
    logger.info(f"No input specified. Using default sample: {default_image}")


def _find_script(name: str) -> Optional[str]:
    """Locate a setup script relative to dx_app root."""
    # Walk up from this file to find dx_app root (contains setup.sh)
    candidate = Path(__file__).resolve()
    for _ in range(10):
        candidate = candidate.parent
        if (candidate / name).is_file():
            return str(candidate / name)
    return None


def _auto_download_model(model_path: Path) -> bool:
    """Attempt to download a missing model via setup_sample_models.sh."""
    script = _find_script("setup_sample_models.sh")
    if not script:
        return False
    model_stem = model_path.stem
    models_dir = str(model_path.parent) if str(model_path.parent) != "." else "./assets/models"
    logger.info(f"Model not found: {model_path} — attempting auto-download...")
    result = subprocess.run(
        [script, f"--output={models_dir}", "--models", model_stem],
        timeout=300)
    return result.returncode == 0 and model_path.is_file()


def _auto_download_videos() -> bool:
    """Attempt to download sample videos via setup_sample_videos.sh."""
    script = _find_script("setup_sample_videos.sh")
    if not script:
        return False
    logger.info("Videos not found — attempting auto-download...")
    result = subprocess.run(
        [script, "--output=./assets/videos"],
        timeout=600)
    return result.returncode == 0


# ======================================================================
# Input validation
# ======================================================================

def _validate_model(args) -> None:
    """Validate model file exists, auto-download if needed."""
    model = Path(args.model)
    if model.is_file():
        return
    if _auto_download_model(model):
        logger.info(f"Model downloaded successfully: {args.model}")
        return
    model_stem = model.stem
    logger.error(
        f"Model file not found: {args.model}\n"
        f"        → Download:  ./setup.sh --models {model_stem}\n"
        f"        → Or use:    ./run_demo.sh  (auto-downloads demo models)")
    sys.exit(1)


def _validate_media(args) -> None:
    """Validate image/video paths exist, auto-download videos if needed."""
    if getattr(args, "image", None):
        p = Path(args.image)
        if not p.exists():
            logger.error(f"Image path does not exist: {args.image}")
            sys.exit(1)
        if not p.is_file() and not p.is_dir():
            logger.error(f"Image path must be a valid file or directory: {args.image}")
            sys.exit(1)

    if not getattr(args, "video", None):
        return
    p = Path(args.video)
    if p.is_file():
        return
    _auto_download_videos()
    if p.is_file():
        logger.info(f"Video downloaded successfully: {args.video}")
        return
    logger.error(
        f"Video file not found: {args.video}\n"
        f"        → Download videos: ./setup_sample_videos.sh")
    sys.exit(1)


def _validate_loop(args) -> None:
    """Validate loop and live-source options."""
    loop = getattr(args, "loop", 1)
    if isinstance(loop, bool):
        loop = 2 if loop else 1
    if isinstance(loop, int) and loop < 1:
        logger.error("--loop must be >= 1.")
        sys.exit(1)
    is_live = (getattr(args, "camera", None) is not None) or \
              (getattr(args, "rtsp", None) is not None)
    if is_live and isinstance(loop, int) and loop > 1:
        logger.error("--loop is not valid with --camera or --rtsp.")
        sys.exit(1)


def _validate_inputs(args) -> None:
    """Pre-validate input paths before starting inference."""
    _validate_model(args)
    _validate_media(args)
    _validate_loop(args)


# ======================================================================
# SyncRunner
# ======================================================================

class SyncRunner:
    """
    Generic synchronous runner for any model using factory pattern.

    Features ported from OLD yolov5 common-feature-alignment:
    - Structured run-directory with ``run_info.txt``
    - Multi-loop with averaged performance summary
    - Automatic tensor dump on exception (input + output + reason.txt)
    - 7-field metrics (read/pre/infer/post/render/save/display)
    - VideoWriter mp4v → XVID fallback
    - DX-RT version check, input pre-validation
    """

    def __init__(
        self,
        factory,
        use_ort: Optional[bool] = None,
        cpp_postprocessor=None,
        cpp_convert_fn=None,
        cpp_visualize_fn=None,
        on_engine_init=None,
        display_size: tuple = None,
    ):
        self.factory = factory
        self._use_ort = use_ort
        self._cpp_postprocessor = cpp_postprocessor
        self._cpp_convert_fn = cpp_convert_fn
        self._cpp_visualize_fn = cpp_visualize_fn
        self._on_engine_init = on_engine_init
        self._display_size = display_size or _DEFAULT_DISPLAY_SIZE

        self.ie: Optional[InferenceEngine] = None
        self.input_width = 0
        self.input_height = 0
        self.preprocessor = None
        self.postprocessor = None
        self.visualizer = None

        self._save = False
        self._save_dir: Optional[str] = None
        self._loop: int = 1
        self._dump_tensors = False
        self._model_path = ""
        self._verbose = False
        self._sr_cache: Optional[dict] = None  # cached SR probe info

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, args) -> None:
        """Main entry point."""
        _check_dxrt_version()
        _apply_default_input(args, self.factory)
        _validate_inputs(args)

        self._verbose = getattr(args, "show_log", False)
        self._model_path = args.model
        self._init_engine(args.model, _resolve_config_path(args))

        self._save = getattr(args, "save", False)
        self._save_dir = getattr(args, "save_dir", None)
        self._dump_tensors = getattr(args, "dump_tensors", False)
        self._loop = _parse_loop_value(args)

        logger.info("\nStarting inference...")
        self._dispatch_input(args)

    _IMAGE_ONLY_TASKS = {"embedding", "reid", "attribute_recognition"}

    def _dispatch_input(self, args) -> None:
        """Route to the correct inference method based on input args."""
        display = args.display
        task = self.factory.get_task_type() if hasattr(self.factory, "get_task_type") else ""
        if task in self._IMAGE_ONLY_TASKS and not getattr(args, "image", None):
            logger.error(
                f"Task '{task}' supports image input only "
                f"(--image). Video/camera input requires a "
                f"detection crop pipeline and is not supported "
                f"in single-model examples.")
            sys.exit(1)
        if getattr(args, "image", None):
            if os.path.isdir(args.image):
                self._image_dir_inference(args.image, display)
            else:
                self._image_inference(args.image, display)
        elif getattr(args, "video", None):
            self._stream_inference(args.video, display)
        elif getattr(args, "camera", None) is not None:
            self._stream_inference(args.camera, display)
        elif getattr(args, "rtsp", None):
            self._stream_inference(args.rtsp, display)

    # ------------------------------------------------------------------
    # Engine initialisation
    # ------------------------------------------------------------------

    def _init_engine(self, model_path: str, config_path: Optional[str] = None) -> None:
        option = InferenceOption()
        if self._use_ort is None:
            if not option.get_use_ort():
                logger.error("USE_ORT=OFF is not supported in this example.")
                sys.exit(1)
            self.ie = InferenceEngine(model_path)
        elif self._use_ort is False:
            option.set_use_ort(False)
            self.ie = InferenceEngine(model_path, option)
        else:
            self.ie = InferenceEngine(model_path)

        _check_model_version(self.ie)

        input_info = self.ie.get_input_tensors_info()
        shape = input_info[0]["shape"]
        self._input_dtype = input_info[0].get("dtype", np.uint8)
        self._input_shape = shape
        self._nchw = len(shape) >= 4 and shape[1] in (1, 3, 4)
        self.input_height, self.input_width = self._resolve_input_shape(shape)
        logger.info(f"\nModel loaded: {model_path}")
        logger.info(f"Model input size (WxH): {self.input_width}x{self.input_height}")
        if len(shape) < 3:
            logger.warning(f"Non-image model detected (shape={shape}).")

        if config_path:
            config = load_config(config_path, verbose=self._verbose)
            if config:
                self.factory.load_config(config)

        self.preprocessor = self.factory.create_preprocessor(self.input_width, self.input_height)
        self.postprocessor = self.factory.create_postprocessor(self.input_width, self.input_height)
        self.visualizer = self.factory.create_visualizer()
        if self._on_engine_init is not None:
            self._on_engine_init(self)

    @staticmethod
    def _resolve_input_shape(shape):
        if len(shape) >= 4:
            if shape[-1] in (1, 3, 4):
                return shape[1], shape[2]
            return shape[2], shape[3]
        if len(shape) == 3:
            return shape[1], shape[2]
        if len(shape) == 2:
            return 1, shape[1]
        return 1, 1

    # ------------------------------------------------------------------
    # Pipeline steps
    # ------------------------------------------------------------------

    def preprocess(self, image: np.ndarray):
        return self.preprocessor.process(image)

    def infer(self, input_tensor: np.ndarray) -> List[np.ndarray]:
        expected = getattr(self, "_input_dtype", None)
        if expected is not None and input_tensor.dtype != expected:
            if expected == np.float32 and input_tensor.dtype == np.uint8:
                input_tensor = input_tensor.astype(np.float32) / 255.0
            else:
                input_tensor = input_tensor.astype(expected)
        # HWC → CHW for NCHW models (e.g., ViT, DeiT)
        # Skip if already CHW (channel dim first); detect HWC by last dim being small channel count
        # and first two dims being spatial (both > 4)
        if getattr(self, "_nchw", False) and input_tensor.ndim == 3:
            h, w, c = input_tensor.shape
            if c in (1, 3, 4) and h > 4 and w > 4:
                input_tensor = np.transpose(input_tensor, (2, 0, 1))
        return self.ie.run([input_tensor])

    def postprocess(self, outputs: List[np.ndarray], ctx):
        if self._cpp_postprocessor is not None:
            self._preprocess_ctx = ctx
            converted = [
                o.astype(np.float32)
                if o.dtype not in (np.float32, np.float64, np.int32, np.int64, np.uint8)
                else o for o in outputs
            ]
            cpp_result = self._cpp_postprocessor.postprocess(converted)
            if self._cpp_convert_fn is not None:
                try:
                    results = self._cpp_convert_fn(cpp_result, ctx)
                except TypeError:
                    results = self._cpp_convert_fn(cpp_result)
            else:
                results = cpp_result

            # Scale C++ results to original coords. Skip when _cpp_convert_fn
            # is None — that indicates PythonFallbackPostProcess which already
            # returns results in original image coordinates.
            if ctx is not None and results is not None and self._cpp_convert_fn is not None:
                self._scale_cpp_results_to_original(results, ctx)

            return results
        return self.postprocessor.process(outputs, ctx)

    def _scale_cpp_results_to_original(self, results, ctx):
        """Scale C++ postprocessor results from model input space to original image space."""
        try:
            from ..utility.preprocessing import scale_to_original

            for r in results:
                if hasattr(r, 'box') and r.box and len(r.box) >= 4:
                    bx = [float(v) for v in r.box[:4]]
                    if all(v <= 1.01 for v in bx) and any(v > 0 for v in bx):
                        bx[0] *= self.input_width
                        bx[1] *= self.input_height
                        bx[2] *= self.input_width
                        bx[3] *= self.input_height
                    x1, y1 = scale_to_original(bx[0], bx[1], ctx)
                    x2, y2 = scale_to_original(bx[2], bx[3], ctx)
                    r.box = [x1, y1, x2, y2]

                elif hasattr(r, 'cx') and hasattr(r, 'cy') and hasattr(r, 'width') and hasattr(r, 'height'):
                    nx, ny = scale_to_original(r.cx, r.cy, ctx)
                    scale = getattr(ctx, 'scale', 1.0) or 1.0
                    r.cx = float(nx)
                    r.cy = float(ny)
                    r.width = float(r.width / scale)
                    r.height = float(r.height / scale)

                if hasattr(r, 'keypoints') and r.keypoints:
                    for kp in r.keypoints:
                        if hasattr(kp, 'x') and hasattr(kp, 'y'):
                            kp.x, kp.y = scale_to_original(kp.x, kp.y, ctx)
                            kp.x = float(kp.x)
                            kp.y = float(kp.y)
        except Exception:
            pass

    def visualize(self, image: np.ndarray, results) -> np.ndarray:
        if self._cpp_visualize_fn is not None:
            ctx = getattr(self, '_preprocess_ctx', None)
            return self._cpp_visualize_fn(image, results, self.visualizer, ctx)
        return self.visualizer.visualize(image, results)

    # ------------------------------------------------------------------
    # Looped execution wrapper
    # ------------------------------------------------------------------

    def _run_looped(self, *, loop: int, display: bool, save: bool,
                    run_once: Callable[[int, bool], dict]) -> dict:
        """Execute *run_once* up to *loop* times. Save only on first loop."""
        agg_metrics = _create_sync_metrics()
        agg_count = 0
        agg_elapsed = 0.0
        processed_loops = 0
        summary_render = display or save

        for loop_idx in range(loop):
            if loop > 1 and self._verbose:
                logger.info(f"\n{'='*40}\n Loop [{loop_idx + 1}/{loop}]\n{'='*40}")
            save_enabled = save and (loop_idx == 0)
            result = run_once(loop_idx, save_enabled)
            _add_sync_metrics(agg_metrics, result["metrics"])
            agg_count += result["count"]
            agg_elapsed += result["elapsed"]
            processed_loops += 1
            if result.get("quit_requested", False):
                break

        return {"metrics": agg_metrics, "count": agg_count,
                "elapsed": agg_elapsed, "processed_loops": processed_loops,
                "summary_render": summary_render}

    def _print_average_summary(self, result: dict, *, loop: int) -> None:
        count = result["count"]
        if loop <= 1 or count <= 0:
            return
        processed = result["processed_loops"]
        if self._verbose:
            if processed < loop:
                logger.info(f"\nAverage performance over {processed}/{loop} loops "
                      "(stopped early)")
            else:
                logger.info(f"\nAverage performance over {loop} loops")
        print_sync_performance_summary(
            result["metrics"], count, result["elapsed"],
            result["summary_render"])

    # ------------------------------------------------------------------
    # Image inference
    # ------------------------------------------------------------------

    def _image_inference_once(self, image_path: str, display: bool,
                              save_enabled: bool,
                              run_dir: Optional[Path]) -> dict:
        metrics = _create_sync_metrics()
        t_start = time.perf_counter()

        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"Failed to load image: {image_path}")
        t_read = time.perf_counter()

        input_tensor: Optional[np.ndarray] = None
        outputs: List[np.ndarray] = []
        try:
            t0 = time.perf_counter()
            input_tensor, ctx = self.preprocess(img)
            t1 = time.perf_counter()
            outputs = self.infer(input_tensor)
            t2 = time.perf_counter()
            results = self.postprocess(outputs, ctx)
            t3 = time.perf_counter()

            self._try_verify_dump(results, image_path, img)

            output_img = self.visualize(img, results)
            t4 = time.perf_counter()

            metrics["sum_read"] += t_read - t_start
            metrics["sum_preprocess"] += t1 - t0
            metrics["sum_inference"] += t2 - t1
            metrics["sum_postprocess"] += t3 - t2
            metrics["sum_render"] += t4 - t3

            if self._dump_tensors and run_dir:
                dump_tensors(input_tensor, outputs, run_dir / "tensors")

            metrics["sum_save"] += self._save_image_output(
                output_img, image_path, save_enabled, run_dir)
            metrics["sum_display"] += self._display_image_output(
                output_img, display)

            if self._verbose:
                logger.info(
                    f"  Read: {(t_read-t_start)*1000:.2f}ms  Pre: {(t1-t0)*1000:.2f}ms  "
                    f"Infer: {(t2-t1)*1000:.2f}ms  Post: {(t3-t2)*1000:.2f}ms  "
                    f"Render: {(t4-t3)*1000:.2f}ms")

        except Exception:
            dump_dir = run_dir if run_dir else create_run_dir(
                "image-exception", os.path.basename(image_path),
                self._save_dir)
            dump_tensors_on_exception(input_tensor, outputs,
                                      dump_dir / "tensors")
            logger.warning(f"Exception — tensors dumped → {dump_dir / 'tensors'}")
            raise

        return {"metrics": metrics, "count": 1,
                "elapsed": time.perf_counter() - t_start,
                "quit_requested": False}

    def _show_output(self, img: np.ndarray) -> None:
        """Display image in a screen-aware resizable window."""
        from common.utility import show_output
        show_output(img)

    def _try_verify_dump(self, results, image_path: str,
                         img: np.ndarray) -> None:
        """Dump numerical verification JSON if DXAPP_VERIFY=1."""
        if not is_verify_enabled():
            return
        if self._cpp_postprocessor is not None:
            return
        task = self.factory.get_task_type() \
            if hasattr(self.factory, "get_task_type") else ""
        dump_verify_json(
            results, image_path, self._model_path,
            task, (img.shape[0], img.shape[1]),
            verbose=self._verbose)

    def _save_image_output(self, output_img: np.ndarray, image_path: str,
                           save_enabled: bool,
                           run_dir: Optional[Path]) -> float:
        """Save output image to run_dir and/or DXAPP_SAVE_IMAGE. Returns time."""
        env_save = os.environ.get("DXAPP_SAVE_IMAGE")
        if not save_enabled and not env_save:
            return 0.0
        t0 = time.perf_counter()
        if save_enabled and run_dir and output_img is not None:
            base = os.path.splitext(os.path.basename(image_path))[0]
            cv2.imwrite(str(run_dir / f"{base}_result.jpg"), output_img)
        if env_save and output_img is not None:
            cv2.imwrite(env_save, output_img)
        return time.perf_counter() - t0

    def _display_image_output(self, output_img: np.ndarray,
                              display: bool) -> float:
        """Show image and return imshow time (excludes user wait)."""
        if not display or output_img is None:
            return 0.0
        t0 = time.perf_counter()
        if _has_display():
            self._show_output(output_img)
        elif self._verbose:
            logger.info(_MSG_HEADLESS_SKIP)
        t_display = time.perf_counter() - t0
        # Block until user closes — outside timing.
        if _has_display():
            while not _window_should_close("Output"):
                time.sleep(0.01)
        return t_display

    def _image_inference(self, image_path: str, display: bool) -> None:
        if self._verbose:
            logger.info(f"Input image: {image_path}")
            img_probe = cv2.imread(image_path)
            if img_probe is not None:
                logger.info(f"Resolution (WxH): "
                      f"{img_probe.shape[1]}x{img_probe.shape[0]}")

        if self._is_sr_tiled():
            img = cv2.imread(image_path)
            if img is not None:
                self._run_image_sr_tiled(img, display, image_path)
            return

        need_run_dir = self._save or self._dump_tensors

        def run_once(loop_idx: int, save_enabled: bool) -> dict:
            run_dir = None
            if need_run_dir and (save_enabled or self._dump_tensors):
                run_dir = create_run_dir(
                    "image", os.path.basename(image_path), self._save_dir)
                write_run_info(run_dir, self._model_path, image_path)
            return self._image_inference_once(
                image_path, display, save_enabled, run_dir)

        result = self._run_looped(
            loop=self._loop, display=display, save=self._save,
            run_once=run_once)
        if self._loop <= 1 and result["count"] > 0:
            print_sync_performance_summary(
                result["metrics"], result["count"], result["elapsed"],
                display or self._save)
        self._print_average_summary(result, loop=self._loop)
        if display and _has_display():
            cv2.destroyAllWindows()

    def _image_dir_inference(self, dir_path: str, display: bool) -> None:
        extensions = ("*.jpg", "*.jpeg", "*.png", "*.bmp",
                      "*.tiff", "*.tif", "*.webp")
        image_files: List[str] = []
        for ext in extensions:
            image_files.extend(glob.glob(os.path.join(dir_path, ext)))
            image_files.extend(glob.glob(os.path.join(dir_path, ext.upper())))
        image_files = sorted(set(image_files))
        if not image_files:
            raise FileNotFoundError(f"No images found in: {dir_path}")

        if self._verbose:
            logger.info(f"Processing {len(image_files)} images from: {dir_path}")
        need_run_dir = self._save or self._dump_tensors

        def run_once(loop_idx: int, save_enabled: bool) -> dict:
            batch_metrics = _create_sync_metrics()
            batch_count = 0
            batch_start = time.perf_counter()
            batch_run_dir = None
            if need_run_dir and (save_enabled or self._dump_tensors):
                batch_run_dir = create_run_dir(
                    "image-dir", os.path.basename(dir_path), self._save_dir)
                write_run_info(batch_run_dir, self._model_path, dir_path)

            for i, img_path in enumerate(image_files, 1):
                if self._verbose:
                    logger.info(f"\n[{i}/{len(image_files)}] "
                          f"{os.path.basename(img_path)}")
                sub_dir = None
                if batch_run_dir:
                    base = os.path.splitext(os.path.basename(img_path))[0]
                    sub_dir = batch_run_dir / base
                    sub_dir.mkdir(parents=True, exist_ok=True)
                result = self._image_inference_once(
                    img_path, display, save_enabled, sub_dir)
                _add_sync_metrics(batch_metrics, result["metrics"])
                batch_count += result["count"]

            return {"metrics": batch_metrics, "count": batch_count,
                    "elapsed": time.perf_counter() - batch_start,
                    "quit_requested": False}

        result = self._run_looped(
            loop=self._loop, display=display, save=self._save,
            run_once=run_once)
        if self._loop <= 1 and result["count"] > 0:
            print_sync_performance_summary(
                result["metrics"], result["count"], result["elapsed"],
                display or self._save)
        self._print_average_summary(result, loop=self._loop)
        if display and _has_display():
            cv2.destroyAllWindows()

    # ------------------------------------------------------------------
    # Stream inference
    # ------------------------------------------------------------------

    def _process_stream_frame(self, frame: np.ndarray,
                              frame_count: int, run_dir: Optional[Path],
                              source_label: str) -> dict:
        """Run pre/infer/post/viz on a single frame. Returns timing dict + output."""
        input_tensor: Optional[np.ndarray] = None
        outputs: List[np.ndarray] = []
        try:
            t0 = time.perf_counter()
            input_tensor, ctx = self.preprocess(frame)
            t1 = time.perf_counter()
            outputs = self.infer(input_tensor)
            t2 = time.perf_counter()

            if self._dump_tensors and run_dir:
                dump_tensors(input_tensor, outputs,
                             run_dir / "tensors",
                             frame_index=frame_count)

            results = self.postprocess(outputs, ctx)
            t3 = time.perf_counter()
            output_frame = self.visualize(frame, results)
            t4 = time.perf_counter()
        except Exception:
            dump_target = run_dir if run_dir else create_run_dir(
                "stream-exception", source_label.replace(":", "_"),
                self._save_dir)
            dump_tensors_on_exception(
                input_tensor, outputs, dump_target / "tensors",
                frame_index=frame_count)
            logger.warning(f"Exception at frame {frame_count} — "
                  f"tensors dumped → {dump_target / 'tensors'}")
            raise

        return {"output_frame": output_frame,
                "t_pre": t1 - t0, "t_infer": t2 - t1,
                "t_post": t3 - t2, "t_render": t4 - t3}

    def _init_sr_cache(self) -> None:
        """Probe once to cache SR scale info for tiled video processing."""
        if self._sr_cache is not None:
            return
        tile_w, tile_h = self.input_width, self.input_height
        probe = np.zeros((tile_h, tile_w, 1), dtype=np.uint8)
        try:
            out = self.infer(probe)
            arr = np.squeeze(out[0]) if out else np.array([])
            if arr.ndim == 3:
                oth, otw = arr.shape[1], arr.shape[2]
            elif arr.ndim == 2:
                oth, otw = arr.shape[0], arr.shape[1]
            else:
                oth, otw = tile_h, tile_w
            scale_x = max(1, otw // tile_w)
            scale_y = max(1, oth // tile_h)
            self._sr_cache = {
                "scale_x": scale_x, "scale_y": scale_y,
                "oth": oth, "otw": otw,
                "probe_out": out,
            }
        except Exception:
            self._sr_cache = None

    def _process_sr_stream_frame(self, frame: np.ndarray,
                                 frame_count: int) -> dict:
        """Tiled super-resolution for a single video frame."""
        tile_w, tile_h = self.input_width, self.input_height
        sr = self._sr_cache
        scale_x, scale_y = sr["scale_x"], sr["scale_y"]
        oth, otw = sr["oth"], sr["otw"]

        t0 = time.perf_counter()
        # Create LR image: 20 tiles wide, proportional height
        lr_w = tile_w * 20
        lr_h = round(lr_w * frame.shape[0] / frame.shape[1])
        lr_h = max(tile_h, ((lr_h + tile_h - 1) // tile_h) * tile_h)
        lr_bgr = cv2.resize(frame, (lr_w, lr_h))
        lr_gray = cv2.cvtColor(lr_bgr, cv2.COLOR_BGR2GRAY)
        t1 = time.perf_counter()

        out_w, out_h = lr_w * scale_x, lr_h * scale_y

        # Use cached probe for tile (0,0), infer the rest
        probe_out = sr["probe_out"] if frame_count == 1 else None
        if probe_out is None:
            # Re-probe with actual frame data for tile (0,0)
            tile0 = lr_gray[0:tile_h, 0:tile_w]
            probe_out = self.infer(tile0[:, :, np.newaxis])

        sr_y, tiles_done = self._tile_sr_pass(
            lr_gray, tile_h, tile_w, oth, otw, probe_out, out_h, out_w)
        t2 = time.perf_counter()

        sr_bgr = self._merge_ycrcb(sr_y, lr_bgr, out_w, out_h)
        t3 = time.perf_counter()

        # Side-by-side canvas
        lr_up = cv2.resize(lr_bgr, (out_w, out_h),
                           interpolation=cv2.INTER_CUBIC)
        canvas = np.zeros((out_h, out_w * 2 + 4, 3), dtype=np.uint8)
        canvas[:, :out_w] = lr_up
        canvas[:, out_w + 4:] = sr_bgr
        cv2.putText(canvas, f"Bicubic ({lr_w}x{lr_h})",
                    (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 2)
        cv2.putText(canvas,
                    f"ESPCN x{scale_x} ({out_w}x{out_h}, {tiles_done} tiles)",
                    (out_w + 14, 25), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 255, 100), 2)
        t4 = time.perf_counter()

        return {"output_frame": canvas,
                "t_pre": t1 - t0, "t_infer": t2 - t1,
                "t_post": t3 - t2, "t_render": t4 - t3}

    def _save_stream_frame(self, output_frame: np.ndarray,
                           writer: Optional[cv2.VideoWriter]) -> float:
        """Write frame to video writer. Returns time spent."""
        if writer is None or output_frame is None:
            return 0.0
        t0 = time.perf_counter()
        # Resize to match writer dimensions if needed
        ww = int(writer.get(cv2.CAP_PROP_FRAME_WIDTH))
        wh = int(writer.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if ww > 0 and wh > 0 and (
                output_frame.shape[1] != ww or output_frame.shape[0] != wh):
            output_frame = cv2.resize(output_frame, (ww, wh))
        writer.write(output_frame)
        return time.perf_counter() - t0

    def _display_stream_frame(self, output_frame: np.ndarray,
                              display: bool, frame_count: int) -> tuple:
        """Show frame if display enabled. Returns (time_spent, quit_requested)."""
        if not display or output_frame is None:
            return 0.0, False
        t0 = time.perf_counter()
        quit_requested = False
        if _has_display():
            self._show_output(output_frame)
            if _window_should_close("Output"):
                quit_requested = True
        elif frame_count == 1 and self._verbose:
            logger.info(_MSG_HEADLESS_SKIP)
        return time.perf_counter() - t0, quit_requested

    def _stream_loop_body(self, cap, frame_count, run_dir, source_label,
                          display, metrics):
        """Process one frame from the capture source. Returns (frame_count, quit)."""
        t_read_start = time.perf_counter()
        ret, frame = cap.read()
        t_read_end = time.perf_counter()
        if not ret:
            return frame_count, True  # end-of-stream

        frame_count += 1
        result = self._process_stream_frame(
            frame, frame_count, run_dir, source_label)

        metrics["sum_read"] += t_read_end - t_read_start
        metrics["sum_preprocess"] += result["t_pre"]
        metrics["sum_inference"] += result["t_infer"]
        metrics["sum_postprocess"] += result["t_post"]
        metrics["sum_render"] += result["t_render"]

        metrics["sum_save"] += self._save_stream_frame(
            result["output_frame"], None)  # writer handled outside

        t_disp, quit_requested = self._display_stream_frame(
            result["output_frame"], display, frame_count)
        metrics["sum_display"] += t_disp
        return frame_count, quit_requested

    @staticmethod
    def _classify_source(source: Union[str, int]):
        """Classify video source and return (is_live, source_label)."""
        is_live = isinstance(source, int) or (
            isinstance(source, str) and source.lower().startswith("rtsp://"))
        label = f"camera:{source}" if isinstance(source, int) else str(source)
        return is_live, label

    @staticmethod
    def _accumulate_stream_metrics(metrics: dict, result: dict, t_read: float):
        """Accumulate per-frame timing metrics."""
        metrics["sum_read"] += t_read
        metrics["sum_preprocess"] += result["t_pre"]
        metrics["sum_inference"] += result["t_infer"]
        metrics["sum_postprocess"] += result["t_post"]
        metrics["sum_render"] += result["t_render"]

    @staticmethod
    def _release_capture(writer, cap):
        """Release video capture resources."""
        if writer is not None:
            writer.release()
        cap.release()
        if _has_display():
            cv2.destroyAllWindows()

    def _stream_inference_once(self, source: Union[str, int],
                               display: bool, save_enabled: bool,
                               run_dir: Optional[Path]) -> dict:
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            raise RuntimeError(f"Failed to open source: {source}")

        is_live, source_label = self._classify_source(source)
        if is_live:
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        if self._verbose:
            logger.info(f"Input: {source_label}")
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            logger.info(f"Resolution: {w}x{h}, FPS: {fps:.1f}, "
                  f"Frames: {total if total > 0 else 'N/A'}")
        else:
            logger.info("Processing... Only FPS will be displayed.")

        metrics = _create_sync_metrics()
        frame_count = 0
        quit_requested = False
        writer = self._init_video_writer_probed(cap, run_dir) if (save_enabled and run_dir) else None

        # Detect if this model needs tiled super-resolution
        use_sr_tiled = self._is_sr_tiled()
        if use_sr_tiled:
            self._init_sr_cache()
            use_sr_tiled = self._sr_cache is not None

        start_time = time.perf_counter()

        try:
            while True:
                t_read_start = time.perf_counter()
                ret, frame = cap.read()
                t_read = time.perf_counter() - t_read_start
                if not ret:
                    break

                frame_count += 1
                if use_sr_tiled:
                    result = self._process_sr_stream_frame(
                        frame, frame_count)
                else:
                    result = self._process_stream_frame(
                        frame, frame_count, run_dir, source_label)

                self._accumulate_stream_metrics(metrics, result, t_read)
                metrics["sum_save"] += self._save_stream_frame(
                    result["output_frame"], writer)

                t_disp, quit_requested = self._display_stream_frame(
                    result["output_frame"], display, frame_count)
                metrics["sum_display"] += t_disp

                if quit_requested:
                    break
        except KeyboardInterrupt:
            logger.info("\nInterrupted by user.")
        finally:
            self._release_capture(writer, cap)

        elapsed = time.perf_counter() - start_time
        if frame_count > 0 and self._loop <= 1:
            print_sync_performance_summary(
                metrics, frame_count, elapsed, display or save_enabled)

        return {"metrics": metrics, "count": frame_count,
                "elapsed": elapsed, "quit_requested": quit_requested}

    def _stream_inference(self, source: Union[str, int],
                          display: bool) -> None:
        need_run_dir = self._save or self._dump_tensors

        def run_once(loop_idx: int, save_enabled: bool) -> dict:
            run_dir = None
            if need_run_dir and (save_enabled or self._dump_tensors):
                src_name = f"camera{source}" if isinstance(source, int) \
                    else os.path.splitext(
                        os.path.basename(str(source)))[0] or "stream"
                run_dir = create_run_dir("stream", src_name, self._save_dir)
                write_run_info(run_dir, self._model_path, source)
            return self._stream_inference_once(
                source, display, save_enabled, run_dir)

        result = self._run_looped(
            loop=self._loop, display=display, save=self._save,
            run_once=run_once)
        self._print_average_summary(result, loop=self._loop)

    # ------------------------------------------------------------------
    # VideoWriter with mp4v → XVID fallback
    # ------------------------------------------------------------------

    def _init_video_writer_probed(self, cap: cv2.VideoCapture,
                                  run_dir: Path) -> cv2.VideoWriter:
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        if w <= 0 or h <= 0:
            raise RuntimeError(
                f"Cannot determine video dimensions (w={w}, h={h}).")

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        save_path = str(run_dir / "output.mp4")
        writer = cv2.VideoWriter(save_path, fourcc, fps, (w, h))
        if writer.isOpened():
            if self._verbose:
                logger.info(f"Saving output video: {save_path}")
            return writer
        writer.release()

        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        save_path = str(run_dir / "output.avi")
        writer = cv2.VideoWriter(save_path, fourcc, fps, (w, h))
        if writer.isOpened():
            if self._verbose:
                logger.info(f"Saving output video: {save_path} (XVID fallback)")
            return writer
        writer.release()
        raise RuntimeError("Failed to open VideoWriter for output.")

    # ------------------------------------------------------------------
    # Super-resolution helpers
    # ------------------------------------------------------------------

    def _probe_sr_output_size(self, lr_gray, tile_h, tile_w):
        probe_tile = lr_gray[0:tile_h, 0:tile_w]
        probe_out = self.infer(probe_tile[:, :, np.newaxis])
        arr = np.squeeze(probe_out[0]) if probe_out else np.array([])
        if arr.ndim == 3:
            return probe_out, arr.shape[1], arr.shape[2]
        if arr.ndim == 2:
            return probe_out, arr.shape[0], arr.shape[1]
        return probe_out, tile_h * 2, tile_w * 2

    def _tile_sr_pass(self, lr_gray, tile_h, tile_w, out_tile_h, out_tile_w,
                      probe_out, out_h, out_w):
        sr_y = np.zeros((out_h, out_w), dtype=np.uint8)
        tiles_x = lr_gray.shape[1] // tile_w
        tiles_y = lr_gray.shape[0] // tile_h
        tiles_done = 0
        for ty in range(tiles_y):
            for tx in range(tiles_x):
                if ty == 0 and tx == 0:
                    tile_out = probe_out
                else:
                    tile = lr_gray[ty*tile_h:(ty+1)*tile_h,
                                   tx*tile_w:(tx+1)*tile_w]
                    tile_out = self.infer(tile[:, :, np.newaxis])
                arr = np.squeeze(tile_out[0]) if tile_out else None
                if arr is None:
                    continue
                arr2d = arr[0] if arr.ndim == 3 else arr
                tile_uint8 = (np.clip(arr2d, 0.0, 1.0) * 255.0).astype(np.uint8)
                dst_y = ty * out_tile_h
                dst_x = tx * out_tile_w
                sr_y[dst_y:dst_y+out_tile_h, dst_x:dst_x+out_tile_w] = tile_uint8
                tiles_done += 1
        return sr_y, tiles_done

    @staticmethod
    def _merge_ycrcb(sr_y, lr_bgr, out_w, out_h):
        lr_ycrcb = cv2.cvtColor(lr_bgr, cv2.COLOR_BGR2YCrCb)
        cr_up = cv2.resize(lr_ycrcb[:, :, 1], (out_w, out_h),
                           interpolation=cv2.INTER_CUBIC)
        cb_up = cv2.resize(lr_ycrcb[:, :, 2], (out_w, out_h),
                           interpolation=cv2.INTER_CUBIC)
        return cv2.cvtColor(np.stack([sr_y, cr_up, cb_up], axis=2),
                            cv2.COLOR_YCrCb2BGR)

    def _run_image_sr_tiled(self, img: np.ndarray, display: bool,
                             image_path: str = "") -> None:
        t_start = time.perf_counter()
        tile_w, tile_h = self.input_width, self.input_height
        lr_w = tile_w * 20
        lr_h = round(lr_w * img.shape[0] / img.shape[1])
        lr_h = max(tile_h, ((lr_h + tile_h - 1) // tile_h) * tile_h)
        lr_bgr = cv2.resize(img, (lr_w, lr_h))
        lr_gray = cv2.cvtColor(lr_bgr, cv2.COLOR_BGR2GRAY)

        t0 = time.perf_counter()
        probe_out, oth, otw = self._probe_sr_output_size(lr_gray, tile_h, tile_w)
        scale_x = max(1, otw // tile_w)
        out_w, out_h = lr_w * scale_x, lr_h * max(1, oth // tile_h)

        t_i0 = time.perf_counter()
        sr_y, tiles_done = self._tile_sr_pass(
            lr_gray, tile_h, tile_w, oth, otw, probe_out, out_h, out_w)
        t_i1 = time.perf_counter()

        sr_bgr = self._merge_ycrcb(sr_y, lr_bgr, out_w, out_h)
        t3 = time.perf_counter()

        lr_up = cv2.resize(lr_bgr, (out_w, out_h),
                           interpolation=cv2.INTER_CUBIC)
        canvas = np.zeros((out_h, out_w * 2 + 4, 3), dtype=np.uint8)
        canvas[:, :out_w] = lr_up
        canvas[:, out_w+4:] = sr_bgr
        cv2.putText(canvas, f"Bicubic ({lr_w}x{lr_h})",
                    (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 2)
        cv2.putText(canvas,
                    f"ESPCN x{scale_x} ({out_w}x{out_h}, {tiles_done} tiles)",
                    (out_w + 14, 25), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 255, 100), 2)
        t4 = time.perf_counter()

        tiles_x = lr_w // tile_w
        tiles_y = lr_h // tile_h
        logger.info(f"\nSR tiled: {tiles_x}x{tiles_y}={tiles_done} tiles, "
              f"LR {lr_w}x{lr_h} -> SR {out_w}x{out_h} (x{scale_x})")
        env_save = os.environ.get("DXAPP_SAVE_IMAGE")
        if env_save:
            cv2.imwrite(env_save, canvas)

        if self._save:
            run_dir = create_run_dir(
                "image", os.path.basename(image_path) if image_path else "sr_output",
                self._save_dir)
            write_run_info(run_dir, self._model_path, image_path or "unknown")
            cv2.imwrite(str(run_dir / "sr_result.jpg"), canvas)

        t5 = None
        if display:
            if _has_display():
                t_d0 = time.perf_counter()
                self._show_output(canvas)
                t5 = time.perf_counter()
            elif self._verbose:
                logger.info(_MSG_HEADLESS_SKIP)

        print_image_processing_summary(t_start, t0, t_i0, t_i1, t3, t4, t5)

        if display and _has_display():
            while not _window_should_close("Output"):
                time.sleep(0.01)
            cv2.destroyAllWindows()

    def _is_sr_tiled(self) -> bool:
        task_type = self.factory.get_task_type() \
            if hasattr(self.factory, "get_task_type") else ""
        if task_type != "super_resolution":
            return False
        probe = np.zeros((self.input_height, self.input_width, 1),
                         dtype=np.uint8)
        try:
            out = self.infer(probe)
            arr = np.squeeze(out[0]) if out else np.array([])
            if arr.ndim == 3:
                ph = arr.shape[1]
            elif arr.ndim == 2:
                ph = arr.shape[0]
            else:
                ph = 0
            return ph > self.input_height
        except Exception:
            return False
