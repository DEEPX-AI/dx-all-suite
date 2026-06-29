#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
Asynchronous inference runner using factory pattern.

Provides a pipelined async runner with separate threads.

Pipeline (5 workers + main-thread display):
    read_worker → preprocess_worker → wait_worker → postprocess_worker → render_worker
    display runs on the **main thread** (cv2.imshow GUI constraint).

Uses ``ie.run_async()`` + ``ie.wait()`` for true asynchronous pipelining so that
preprocessing of the next frame overlaps with inference of the current frame.

Features ported from OLD yolov5 common-feature-alignment:
- True async via run_async / wait with inflight tracking
- Graceful shutdown via stop_event + SENTINEL chain + queue drain
- Worker exception capture and re-raise on main thread
- Display on main thread (cv2.imshow)
- Input + output tensor dump (normal & exception)
- Structured run-directory with run_info.txt
- VideoWriter mp4v → XVID fallback
- Per-image save support (image input via async)
- Multi-loop support (--loop N)
- Display resize to prevent slowdown on 4K input
- Extended async metrics (inflight tracking, sum_save, sum_display)
- DXAPP_SAVE_IMAGE env-var support
- Exception auto-dump with run_dir auto-creation
"""

import glob
import os
import sys
import time
import threading
import traceback
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

import numpy as np
import cv2

from dx_engine import InferenceEngine, InferenceOption
from ..inputs import InputFactory
from ..utility import print_async_performance_summary_legacy, SafeQueue
from ..utility import print_image_processing_summary, print_sync_performance_summary
from .run_dir import create_run_dir, write_run_info, dump_tensors, dump_tensors_on_exception
from .verify_serialize import is_verify_enabled, dump_verify_json

# Import shared validation / version check / helpers from sync_runner
from .sync_runner import (
    _check_dxrt_version, _validate_inputs, _apply_default_input, _has_display,
    _resolve_config_path, _parse_loop_value, _window_should_close,
)

logger = logging.getLogger(__name__)

# Sentinel object for queue termination chain
_SENTINEL = object()
_ASYNC_QUEUE_MAXSIZE = 4
_DEFAULT_DISPLAY_SIZE = (960, 640)


class AsyncRunner:
    """
    Generic asynchronous runner for any model using factory pattern.

    Five-worker pipeline (display on main):
        read_worker → preprocess_worker(+run_async) → wait_worker →
        postprocess_worker → render_worker → display on main thread
    """

    def __init__(
        self,
        factory,
        use_ort: Optional[bool] = None,
        on_engine_init=None,
        display_size: tuple = _DEFAULT_DISPLAY_SIZE,
    ):
        self.factory = factory
        self._use_ort = use_ort
        self._on_engine_init = on_engine_init
        self._display_size = display_size

        self.ie: Optional[InferenceEngine] = None
        self.preprocessor = None
        self.postprocessor = None
        self.visualizer = None
        self.input_width = 0
        self.input_height = 0

        # C++ postprocess support
        self._cpp_postprocessor = None
        self._cpp_convert_fn = None
        self._cpp_visualize_fn = None

        # Runtime options
        self._save = False
        self._save_dir: Optional[str] = None
        self._dump_tensors = False
        self._loop: int = 1
        self._model_path = ""
        self._run_dir: Optional[Path] = None
        self._is_image_input = False
        self._input_path = ""      # For verify dump
        self._verify_dumped = False  # Only dump once per run
        self._verbose = False

        # SR tiled fallback (ESPCN etc.)
        self._sr_cache: Optional[dict] = None

        # Pipeline state
        self._stop_event = threading.Event()
        self._metrics_lock = threading.Lock()
        self._metrics: Dict[str, object] = {}
        self._worker_error: Dict[str, object] = {"name": None, "exc": None}
        self._video_writer = None
        self.frame_count = 0

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    @staticmethod
    def _create_async_metrics() -> Dict[str, object]:
        return {
            "sum_read": 0.0,
            "sum_preprocess": 0.0,
            "sum_inference": 0.0,
            "sum_postprocess": 0.0,
            "sum_render": 0.0,
            "sum_save": 0.0,
            "sum_display": 0.0,
            "infer_completed": 0,
            "render_completed": 0,
            "save_completed": 0,
            "display_completed": 0,
            "infer_first_ts": None,
            "infer_last_ts": None,
            "inflight_last_ts": None,
            "inflight_current": 0,
            "inflight_max": 0,
            "inflight_time_sum": 0.0,
        }

    # ------------------------------------------------------------------
    # Queue factory
    # ------------------------------------------------------------------

    def _create_queues(self) -> dict:
        return {
            "read_queue": SafeQueue(maxsize=_ASYNC_QUEUE_MAXSIZE),
            "reqid_queue": SafeQueue(maxsize=_ASYNC_QUEUE_MAXSIZE),
            "output_queue": SafeQueue(maxsize=_ASYNC_QUEUE_MAXSIZE),
            "render_queue": SafeQueue(maxsize=_ASYNC_QUEUE_MAXSIZE),
            "display_queue": SafeQueue(maxsize=_ASYNC_QUEUE_MAXSIZE),
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, args) -> None:
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
            self._is_image_input = True
            if os.path.isdir(args.image):
                self._run_image_dir(args.image, display)
            elif self._is_sr_tiled():
                self._run_image_sr(args.image, display)
            else:
                self._run_image(args.image, display)
        elif getattr(args, "video", None):
            self._is_image_input = False
            source = args.video
            if self._is_sr_tiled():
                self._run_stream_sr(source, display)
            else:
                self._run_stream(source, display)
        elif getattr(args, "camera", None) is not None:
            self._is_image_input = False
            source = args.camera
            if self._is_sr_tiled():
                self._run_stream_sr(source, display)
            else:
                self._run_stream(source, display)
        elif getattr(args, "rtsp", None):
            self._is_image_input = False
            source = args.rtsp
            if self._is_sr_tiled():
                self._run_stream_sr(source, display)
            else:
                self._run_stream(source, display)
        else:
            logger.error("No input source specified.")
            sys.exit(1)

    # ------------------------------------------------------------------
    # Engine initialisation
    # ------------------------------------------------------------------

    def _init_engine(self, model_path: str,
                     config_path: Optional[str] = None) -> None:
        option = InferenceOption()
        if self._use_ort is False:
            option.set_use_ort(False)
            self.ie = InferenceEngine(model_path, option)
        else:
            self.ie = InferenceEngine(model_path)

        input_info = self.ie.get_input_tensors_info()
        shape = input_info[0]["shape"]
        self._input_dtype = input_info[0].get("dtype", None)
        self._input_shape = shape
        self._nchw = len(shape) >= 4 and shape[1] in (1, 3, 4)
        if len(shape) >= 4:
            if shape[-1] in (1, 3, 4):
                input_h, input_w = shape[1], shape[2]
            else:
                input_h, input_w = shape[2], shape[3]
        elif len(shape) == 3:
            input_h, input_w = shape[1], shape[2]
        elif len(shape) == 2:
            input_h, input_w = 1, shape[1]
        else:
            input_h, input_w = 1, 1

        logger.info(f"\nModel loaded: {model_path}")
        logger.info(f"Model input size (WxH): {input_w}x{input_h}")

        if config_path:
            from ..config import load_config
            config = load_config(config_path, verbose=self._verbose)
            if config:
                self.factory.load_config(config)

        self.preprocessor = self.factory.create_preprocessor(input_w, input_h)
        self.postprocessor = self.factory.create_postprocessor(input_w, input_h)
        self.visualizer = self.factory.create_visualizer()
        self.input_width = input_w
        self.input_height = input_h
        if self._on_engine_init is not None:
            self._on_engine_init(self)

    # ------------------------------------------------------------------
    # Stop / Drain helpers (graceful shutdown)
    # ------------------------------------------------------------------

    def _set_stop(self, queues: dict) -> None:
        """Signal all workers to stop and drain all queues."""
        self._stop_event.set()
        for q in queues.values():
            # Drain
            while True:
                item = q.try_get()
                if item is None:
                    break
            # Push sentinel
            self._push_sentinel(q)

    @staticmethod
    def _push_sentinel(q: SafeQueue) -> None:
        while True:
            if q.put(_SENTINEL, block=False):
                return
            q.try_get()  # make room

    def _enqueue(self, q: SafeQueue, item: object) -> bool:
        """Blocking put with stop_event check and 100ms timeout."""
        while not self._stop_event.is_set():
            if q.put(item, timeout=0.1):
                return True
        return False

    def _dequeue(self, q: SafeQueue, timeout: float = 0.5):
        """Blocking get with stop_event check."""
        while not self._stop_event.is_set():
            item = q.get(timeout=timeout)
            if item is not None:
                return item
        return _SENTINEL

    def _handle_worker_exception(self, name: str, exc: Exception,
                                 queues: dict) -> None:
        with self._metrics_lock:
            if self._worker_error["exc"] is None:
                self._worker_error["name"] = name
                self._worker_error["exc"] = exc
        self._set_stop(queues)

    def _track_inflight_submit(self, timestamp: float) -> None:
        """Update inflight metrics on async submit (call under lock)."""
        m = self._metrics
        if m["infer_first_ts"] is None:
            m["infer_first_ts"] = timestamp
        if m["inflight_last_ts"] is not None:
            dt = timestamp - m["inflight_last_ts"]
            m["inflight_time_sum"] += m["inflight_current"] * dt
        m["inflight_last_ts"] = timestamp
        m["inflight_current"] += 1
        if m["inflight_current"] > m["inflight_max"]:
            m["inflight_max"] = m["inflight_current"]

    def _track_inflight_complete(self, timestamp: float) -> None:
        """Update inflight metrics on wait complete (call under lock)."""
        m = self._metrics
        m["infer_completed"] += 1
        m["infer_last_ts"] = timestamp
        if m["inflight_last_ts"] is not None:
            dt = timestamp - m["inflight_last_ts"]
            m["inflight_time_sum"] += m["inflight_current"] * dt
        m["inflight_last_ts"] = timestamp
        m["inflight_current"] -= 1

    # ------------------------------------------------------------------
    # Workers (5-worker pipeline using run_async/wait)
    # ------------------------------------------------------------------

    def _read_worker(self, input_source, queues: dict) -> None:
        """Read frames from input source and measure read time."""
        read_q = queues["read_queue"]
        try:
            for frame in input_source:
                if self._stop_event.is_set():
                    break
                t_read = time.perf_counter()
                if not self._enqueue(read_q, (frame, t_read)):
                    break
        except Exception as exc:
            self._handle_worker_exception("read_worker", exc, queues)
        finally:
            self._push_sentinel(read_q)

    def _preprocess_worker(self, queues: dict) -> None:
        """Preprocess + submit async inference (run_async)."""
        read_q = queues["read_queue"]
        reqid_q = queues["reqid_queue"]
        try:
            while not self._stop_event.is_set():
                item = self._dequeue(read_q)
                if item is _SENTINEL:
                    break
                frame, t_read_ts = item
                t_read_done = time.perf_counter()

                t0 = time.perf_counter()
                input_tensor, ctx = self.preprocessor.process(frame)
                t1 = time.perf_counter()

                # Submit async inference
                if self._input_dtype is not None and input_tensor.dtype != self._input_dtype:
                    if self._input_dtype == np.float32 and input_tensor.dtype == np.uint8:
                        input_tensor = input_tensor.astype(np.float32) / 255.0
                    else:
                        input_tensor = input_tensor.astype(self._input_dtype)
                # HWC → CHW for NCHW models (e.g., ViT, DeiT)
                # Skip if already CHW (channel dim first); detect HWC by last dim being small channel count
                # and first two dims being spatial (both > 4)
                if getattr(self, "_nchw", False) and input_tensor.ndim == 3:
                    h, w, c = input_tensor.shape
                    if c in (1, 3, 4) and h > 4 and w > 4:
                        input_tensor = np.transpose(input_tensor, (2, 0, 1))
                req_id = self.ie.run_async([input_tensor])
                t_submit = time.perf_counter()

                with self._metrics_lock:
                    self._metrics["sum_read"] += t_read_done - t_read_ts
                    self._metrics["sum_preprocess"] += t1 - t0
                    self._track_inflight_submit(t_submit)

                payload = (frame, input_tensor, req_id, ctx, t_submit)
                if not self._enqueue(reqid_q, payload):
                    break
        except Exception as exc:
            self._handle_worker_exception("preprocess_worker", exc, queues)
        finally:
            self._push_sentinel(reqid_q)

    def _wait_worker(self, queues: dict) -> None:
        """Wait for async inference results."""
        reqid_q = queues["reqid_queue"]
        output_q = queues["output_queue"]
        try:
            while not self._stop_event.is_set():
                item = self._dequeue(reqid_q)
                if item is _SENTINEL:
                    break
                frame, input_tensor, req_id, ctx, t_submit = item

                outputs = self.ie.wait(req_id)
                t_done = time.perf_counter()

                with self._metrics_lock:
                    self._metrics["sum_inference"] += t_done - t_submit
                    self._track_inflight_complete(t_done)

                # --dump-tensors (normal path)
                if self._dump_tensors and self._run_dir:
                    dump_tensors(input_tensor, outputs,
                                 self._run_dir / "tensors",
                                 frame_index=self.frame_count + 1)

                if not self._enqueue(output_q, (frame, input_tensor, outputs, ctx)):
                    break
        except Exception as exc:
            # Auto-dump on exception
            if self._run_dir:
                try:
                    dump_tensors_on_exception(
                        input_tensor if 'input_tensor' in dir() else None,
                        outputs if 'outputs' in dir() else [],
                        self._run_dir / "tensors",
                        frame_index=self.frame_count + 1)
                except Exception:
                    pass
            self._handle_worker_exception("wait_worker", exc, queues)
        finally:
            self._push_sentinel(output_q)

    def _postprocess_worker(self, queues: dict) -> None:
        """Run postprocessing on inference outputs."""
        output_q = queues["output_queue"]
        render_q = queues["render_queue"]
        try:
            while not self._stop_event.is_set():
                item = self._dequeue(output_q)
                if item is _SENTINEL:
                    break
                frame, _, outputs, ctx = item

                t0 = time.perf_counter()
                results = self._run_postprocess(outputs, ctx)
                t1 = time.perf_counter()

                # --- Numerical verification dump (DXAPP_VERIFY=1) ---
                # Only dump from pure-Python postprocess path (skip cpp_postprocess variants)
                if is_verify_enabled() and not self._verify_dumped \
                        and self._cpp_postprocessor is None:
                    self._verify_dumped = True
                    task = self.factory.get_task_type() \
                        if hasattr(self.factory, "get_task_type") else ""
                    dump_verify_json(
                        results, self._input_path, self._model_path,
                        task, (frame.shape[0], frame.shape[1]),
                        verbose=self._verbose)

                with self._metrics_lock:
                    self._metrics["sum_postprocess"] += t1 - t0
                    self.frame_count += 1

                if not self._enqueue(render_q, (frame, results)):
                    break
        except Exception as exc:
            self._handle_worker_exception("postprocess_worker", exc, queues)
        finally:
            self._push_sentinel(render_q)

    def _save_render_output(self, output_img: Optional[np.ndarray],
                            save_enabled: bool, render_idx: int,
                            image_save_paths: Optional[list]) -> None:
        """Save a rendered frame (image or video) and env-var export."""
        if save_enabled and output_img is not None:
            if image_save_paths is not None and render_idx < len(image_save_paths):
                cv2.imwrite(image_save_paths[render_idx], output_img)
                with self._metrics_lock:
                    self._metrics["save_completed"] += 1
            elif self._video_writer is not None:
                self._video_writer.write(output_img)
                with self._metrics_lock:
                    self._metrics["save_completed"] += 1
        env_save = os.environ.get("DXAPP_SAVE_IMAGE")
        if env_save and output_img is not None and render_idx == 0:
            cv2.imwrite(env_save, output_img)

    def _show_output(self, img: Optional[np.ndarray]) -> None:
        """Display image in a screen-aware resizable window."""
        from common.utility import show_output
        show_output(img)

    def _render_worker(self, queues: dict, save_enabled: bool,
                       image_save_paths: Optional[list] = None) -> None:
        """Render + save thread. Pushes frames to display_queue for main."""
        render_q = queues["render_queue"]
        display_q = queues["display_queue"]
        render_idx = 0
        try:
            while not self._stop_event.is_set():
                item = self._dequeue(render_q)
                if item is _SENTINEL:
                    break
                frame, results = item

                t0 = time.perf_counter()
                output_img = self._run_visualize(frame, results)
                t1 = time.perf_counter()
                with self._metrics_lock:
                    self._metrics["sum_render"] += t1 - t0
                    self._metrics["render_completed"] += 1

                t_s0 = time.perf_counter()
                self._save_render_output(
                    output_img, save_enabled, render_idx, image_save_paths)
                with self._metrics_lock:
                    self._metrics["sum_save"] += time.perf_counter() - t_s0

                render_idx += 1
                if not self._enqueue(display_q, output_img):
                    break
        except Exception as exc:
            self._handle_worker_exception("render_worker", exc, queues)
        finally:
            self._push_sentinel(display_q)

    # ------------------------------------------------------------------
    # Display loop (main thread)
    # ------------------------------------------------------------------

    def _run_display_loop(self, queues: dict, display: bool) -> None:
        """Run on main thread. Consumes display_queue."""
        display_q = queues["display_queue"]
        has_gui = _has_display()
        is_image = getattr(self, "_is_image_input", False)
        while not self._stop_event.is_set():
            item = display_q.get(timeout=0.5)
            if item is _SENTINEL:
                break
            if item is None:
                continue
            if not (display and has_gui):
                continue
            t_d0 = time.perf_counter()
            self._show_output(item)
            if is_image:
                # Image mode: pause on each result until user presses a key
                while not _window_should_close("Output"):
                    time.sleep(0.01)
            else:
                # Video/stream mode: check quit on each frame
                if _window_should_close("Output"):
                    self._set_stop(queues)
                    break
            with self._metrics_lock:
                self._metrics["sum_display"] += time.perf_counter() - t_d0
                self._metrics["display_completed"] += 1
            

    # ------------------------------------------------------------------
    # Postprocess / Visualize helpers
    # ------------------------------------------------------------------

    def _run_postprocess(self, outputs: List[np.ndarray], ctx):
        if self._cpp_postprocessor is not None:
            self._preprocess_ctx = ctx
            converted = [
                o.astype(np.float32)
                if o.dtype not in (np.float32, np.float64, np.int32,
                                   np.int64, np.uint8)
                else o for o in outputs
            ]
            results = self._cpp_postprocessor.postprocess(converted)
            if self._cpp_convert_fn is not None:
                try:
                    results = self._cpp_convert_fn(results, ctx)
                except TypeError:
                    results = self._cpp_convert_fn(results)

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

            if isinstance(results, np.ndarray):
                if results.size == 0:
                    return
                cols = results.shape[1] if results.ndim >= 2 else 0
                if cols >= 6:
                    max_coord = float(np.max(np.abs(results[:, :4]))) if results.shape[0] > 0 else 0.0
                    if max_coord <= 1.01 and max_coord > 0:
                        results[:, 0] *= float(self.input_width)
                        results[:, 2] *= float(self.input_width)
                        results[:, 1] *= float(self.input_height)
                        results[:, 3] *= float(self.input_height)
                    for i in range(results.shape[0]):
                        x1, y1 = scale_to_original(float(results[i, 0]), float(results[i, 1]), ctx)
                        x2, y2 = scale_to_original(float(results[i, 2]), float(results[i, 3]), ctx)
                        results[i, 0], results[i, 1] = x1, y1
                        results[i, 2], results[i, 3] = x2, y2
                        if cols > 6:
                            for j in range(6, cols, 2):
                                if j + 1 < cols:
                                    nx, ny = scale_to_original(float(results[i, j]), float(results[i, j+1]), ctx)
                                    results[i, j], results[i, j+1] = nx, ny
                elif cols == 7:
                    scale = getattr(ctx, 'scale', 1.0) or 1.0
                    for i in range(results.shape[0]):
                        nx, ny = scale_to_original(float(results[i, 0]), float(results[i, 1]), ctx)
                        results[i, 0], results[i, 1] = nx, ny
                        results[i, 2] = float(results[i, 2]) / scale
                        results[i, 3] = float(results[i, 3]) / scale
                return

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

    def _run_visualize(self, frame: np.ndarray, results) -> np.ndarray:
        if self._cpp_visualize_fn is not None:
            ctx = getattr(self, '_preprocess_ctx', None)
            return self._cpp_visualize_fn(frame, results, self.visualizer, ctx)
        return self.visualizer.visualize(frame, results)

    # ------------------------------------------------------------------
    # SR tiled fallback (ESPCN etc.) — sync tiled within async runner
    # ------------------------------------------------------------------

    def _is_sr_tiled(self) -> bool:
        """Detect super-resolution model requiring tiled processing."""
        task_type = (self.factory.get_task_type()
                     if hasattr(self.factory, "get_task_type") else "")
        if task_type != "super_resolution":
            return False
        probe = np.zeros((self.input_height, self.input_width, 1),
                         dtype=np.uint8)
        try:
            out = self.ie.run([probe])
            arr = np.squeeze(out[0]) if out else np.array([])
            ph = (arr.shape[1] if arr.ndim == 3
                  else arr.shape[0] if arr.ndim == 2 else 0)
            return ph > self.input_height
        except Exception:
            return False

    def _init_sr_cache(self) -> None:
        """Probe once to cache SR scale info."""
        if self._sr_cache is not None:
            return
        tile_w, tile_h = self.input_width, self.input_height
        probe = np.zeros((tile_h, tile_w, 1), dtype=np.uint8)
        try:
            out = self.ie.run([probe])
            arr = np.squeeze(out[0]) if out else np.array([])
            if arr.ndim == 3:
                oth, otw = arr.shape[1], arr.shape[2]
            elif arr.ndim == 2:
                oth, otw = arr.shape[0], arr.shape[1]
            else:
                oth, otw = tile_h, tile_w
            self._sr_cache = {
                "scale_x": max(1, otw // tile_w),
                "scale_y": max(1, oth // tile_h),
                "oth": oth, "otw": otw, "probe_out": out,
            }
        except Exception:
            self._sr_cache = None

    def _process_sr_frame(self, frame: np.ndarray) -> dict:
        """Tiled super-resolution for one frame (sync). Returns dict with canvas and timings."""
        sr = self._sr_cache
        tile_w, tile_h = self.input_width, self.input_height
        scale_x, scale_y = sr["scale_x"], sr["scale_y"]
        oth, otw = sr["oth"], sr["otw"]

        t0 = time.perf_counter()
        lr_w = tile_w * 20
        lr_h = round(lr_w * frame.shape[0] / frame.shape[1])
        lr_h = max(tile_h, ((lr_h + tile_h - 1) // tile_h) * tile_h)
        lr_bgr = cv2.resize(frame, (lr_w, lr_h))
        lr_gray = cv2.cvtColor(lr_bgr, cv2.COLOR_BGR2GRAY)
        t1 = time.perf_counter()

        out_w, out_h = lr_w * scale_x, lr_h * scale_y
        sr_y = np.zeros((out_h, out_w), dtype=np.uint8)
        tiles_x, tiles_y = lr_w // tile_w, lr_h // tile_h
        tiles_done = 0

        for ty in range(tiles_y):
            for tx in range(tiles_x):
                tile = lr_gray[ty*tile_h:(ty+1)*tile_h,
                               tx*tile_w:(tx+1)*tile_w]
                tile_out = self.ie.run([tile[:, :, np.newaxis]])
                arr = np.squeeze(tile_out[0]) if tile_out else None
                if arr is None:
                    continue
                arr2d = arr[0] if arr.ndim == 3 else arr
                tile_u8 = (np.clip(arr2d, 0.0, 1.0) * 255.0).astype(np.uint8)
                dy, dx = ty * oth, tx * otw
                sr_y[dy:dy+oth, dx:dx+otw] = tile_u8
                tiles_done += 1
        t2 = time.perf_counter()

        # Merge with CrCb from LR
        lr_ycrcb = cv2.cvtColor(lr_bgr, cv2.COLOR_BGR2YCrCb)
        cr_up = cv2.resize(lr_ycrcb[:, :, 1], (out_w, out_h),
                           interpolation=cv2.INTER_CUBIC)
        cb_up = cv2.resize(lr_ycrcb[:, :, 2], (out_w, out_h),
                           interpolation=cv2.INTER_CUBIC)
        sr_bgr = cv2.cvtColor(np.stack([sr_y, cr_up, cb_up], axis=2),
                               cv2.COLOR_YCrCb2BGR)
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

    def _run_stream_sr(self, source, display: bool) -> None:
        """SR fallback: synchronous tiled loop (like C++ async SR path)."""
        source_label = (f"camera:{source}" if isinstance(source, int)
                        else str(source))
        if self._verbose:
            logger.info(f"SR tiled mode (sync within async runner)")

        self._init_sr_cache()
        if self._sr_cache is None:
            logger.warning("SR probe failed, falling back to normal pipeline")
            self._run_stream(source, display)
            return

        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            logger.error(f"Cannot open {source_label}")
            return

        fps = cap.get(cv2.CAP_PROP_FPS)
        need_run_dir = self._save or self._dump_tensors
        run_dir = None
        writer = None

        if need_run_dir:
            src_name = (f"camera{source}" if isinstance(source, int)
                        else os.path.splitext(
                            os.path.basename(str(source)))[0] or "stream")
            run_dir = create_run_dir("stream", src_name, self._save_dir)
            write_run_info(run_dir, self._model_path, source)
        if self._save and run_dir:
            dw, dh = self._display_size
            writer = self._init_video_writer(run_dir, dw, dh,
                                             fps if fps > 0 else 30.0)

        metrics = {"sum_preprocess": 0.0, "sum_inference": 0.0,
                   "sum_postprocess": 0.0, "sum_render": 0.0,
                   "sum_read": 0.0, "sum_save": 0.0, "sum_display": 0.0}
        frame_count = 0
        start = time.perf_counter()
        try:
            while True:
                t_read0 = time.perf_counter()
                ret, frame = cap.read()
                t_read1 = time.perf_counter()
                if not ret:
                    break

                result = self._process_sr_frame(frame)
                canvas = result["output_frame"]
                frame_count += 1

                metrics["sum_read"] += t_read1 - t_read0
                metrics["sum_preprocess"] += result["t_pre"]
                metrics["sum_inference"] += result["t_infer"]
                metrics["sum_postprocess"] += result["t_post"]
                metrics["sum_render"] += result["t_render"]

                if writer is not None:
                    t_s0 = time.perf_counter()
                    ww = int(writer.get(cv2.CAP_PROP_FRAME_WIDTH))
                    wh = int(writer.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    if ww > 0 and wh > 0 and (
                            canvas.shape[1] != ww or canvas.shape[0] != wh):
                        writer.write(cv2.resize(canvas, (ww, wh)))
                    else:
                        writer.write(canvas)
                    metrics["sum_save"] += time.perf_counter() - t_s0

                if display and _has_display():
                    t_d0 = time.perf_counter()
                    self._show_output(canvas)
                    metrics["sum_display"] += time.perf_counter() - t_d0
                    if _window_should_close("Output"):
                        break
        except KeyboardInterrupt:
            logger.info("\nInterrupted by user.")
        finally:
            cap.release()
            if writer is not None:
                writer.release()
            if _has_display():
                cv2.destroyAllWindows()

        elapsed = time.perf_counter() - start
        if frame_count > 0:
            print_sync_performance_summary(
                metrics, frame_count, elapsed,
                display or self._save)

    def _run_image_sr(self, image_path: str, display: bool) -> None:
        """SR tiled path for a single image (mirrors sync runner _run_image_sr_tiled)."""
        if self._verbose:
            logger.info(f"SR tiled image mode")
        self._init_sr_cache()
        if self._sr_cache is None:
            logger.warning("SR probe failed, falling back to normal pipeline")
            self._run_image(image_path, display)
            return

        t_start = time.perf_counter()
        img = cv2.imread(image_path)
        if img is None:
            logger.error(f"Cannot read image: {image_path}")
            return
        t0 = time.perf_counter()

        result = self._process_sr_frame(img)
        canvas = result["output_frame"]
        # Map internal timings to image summary timestamps
        t_i0 = t0 + result["t_pre"]
        t_i1 = t_i0 + result["t_infer"]
        t3 = t_i1 + result["t_post"]
        t4 = t3 + result["t_render"]

        env_save = os.environ.get("DXAPP_SAVE_IMAGE")
        if env_save:
            cv2.imwrite(env_save, canvas)

        t5 = None
        if display and _has_display():
            t_d0 = time.perf_counter()
            self._show_output(canvas)
            t5 = time.perf_counter()

        print_image_processing_summary(t_start, t0, t_i0, t_i1, t3, t4, t5)

        if display and _has_display():
            while not _window_should_close("Output"):
                time.sleep(0.01)
            cv2.destroyAllWindows()

    # ------------------------------------------------------------------
    # VideoWriter with mp4v → XVID fallback
    # ------------------------------------------------------------------

    @staticmethod
    def _init_video_writer(run_dir: Path, w: int, h: int,
                           fps: float) -> cv2.VideoWriter:
        if w <= 0 or h <= 0:
            raise RuntimeError(
                f"Cannot determine video dimensions (w={w}, h={h}).")
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        save_path = str(run_dir / "output.mp4")
        writer = cv2.VideoWriter(save_path, fourcc, fps, (w, h))
        if writer.isOpened():
            return writer
        writer.release()
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        save_path = str(run_dir / "output.avi")
        writer = cv2.VideoWriter(save_path, fourcc, fps, (w, h))
        if writer.isOpened():
            return writer
        writer.release()
        raise RuntimeError("Failed to open VideoWriter for output.")

    # ------------------------------------------------------------------
    # Pipeline orchestration (stream source)
    # ------------------------------------------------------------------

    def _setup_video_writer(self, input_source, save_enabled: bool,
                            run_dir: Optional[Path],
                            is_video: bool) -> None:
        """Probe input source and create VideoWriter if applicable."""
        if save_enabled and run_dir and is_video:
            try:
                source_str = (input_source._source
                              if hasattr(input_source, '_source')
                              else str(input_source))
                probe_cap = cv2.VideoCapture(source_str)
                w = int(probe_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                h = int(probe_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = probe_cap.get(cv2.CAP_PROP_FPS) or 30.0
                probe_cap.release()
                if w > 0 and h > 0:
                    self._video_writer = self._init_video_writer(
                        run_dir, w, h, fps)
            except Exception:
                pass  # video writer probe failure is non-fatal

    def _drain_display_queue(self, queues: dict) -> None:
        """Consume display_queue without showing (headless / no-display)."""
        display_q = queues["display_queue"]
        while not self._stop_event.is_set():
            item = display_q.get(timeout=0.5)
            if item is _SENTINEL:
                break
            if item is None and self._stop_event.is_set():
                break

    def _finalize_metrics(self) -> None:
        """Compute derived metrics fields after pipeline completes."""
        first_ts = self._metrics.get("infer_first_ts")
        last_ts = self._metrics.get("infer_last_ts")
        self._metrics["infer_time_window"] = (
            (last_ts - first_ts)
            if first_ts is not None and last_ts is not None else 0.0)
        if self._metrics["infer_first_ts"] is None:
            self._metrics["infer_first_ts"] = 0.0
        if self._metrics["infer_last_ts"] is None:
            self._metrics["infer_last_ts"] = 0.0

    def _run_pipeline_once(self, input_source, display: bool,
                           save_enabled: bool,
                           run_dir: Optional[Path],
                           image_save_paths: Optional[list] = None,
                           is_video: bool = False) -> dict:
        """Run the 5-worker pipeline once. Returns metrics dict."""
        # Reset state
        self._stop_event.clear()
        self._metrics = self._create_async_metrics()
        self._worker_error = {"name": None, "exc": None}
        self._video_writer = None
        self.frame_count = 0
        self._run_dir = run_dir

        queues = self._create_queues()
        self._setup_video_writer(input_source, save_enabled, run_dir, is_video)

        start_time = time.perf_counter()

        threads = [
            threading.Thread(target=self._read_worker,
                             args=(input_source, queues), daemon=True),
            threading.Thread(target=self._preprocess_worker,
                             args=(queues,), daemon=True),
            threading.Thread(target=self._wait_worker,
                             args=(queues,), daemon=True),
            threading.Thread(target=self._postprocess_worker,
                             args=(queues,), daemon=True),
            threading.Thread(target=self._render_worker,
                             args=(queues, save_enabled, image_save_paths),
                             daemon=True),
        ]
        for t in threads:
            t.start()

        try:
            if display:
                self._run_display_loop(queues, display)
                # Image mode: keep window open until user closes it.
                # Only in a real GUI environment (headless: skip).
                if not is_video and _has_display():
                    while not _window_should_close("Output"):
                        time.sleep(0.01)
            else:
                self._drain_display_queue(queues)
        except KeyboardInterrupt:
            logger.info("\nInterrupted by user.")
            self._set_stop(queues)

        for t in threads:
            t.join(timeout=5.0)

        elapsed = time.perf_counter() - start_time

        if self._video_writer is not None:
            self._video_writer.release()
            if run_dir and self._verbose:
                logger.info(f"Saved output video to: {run_dir}/")

        if _has_display():
            cv2.destroyAllWindows()

        self._finalize_metrics()

        return {
            "metrics": dict(self._metrics),
            "count": self.frame_count,
            "elapsed": elapsed,
            "summary_render": display or save_enabled,
            "quit_requested": self._stop_event.is_set(),
        }

    def _print_summary(self, result: dict) -> None:
        if result["count"] > 0:
            print_async_performance_summary_legacy(
                result["metrics"], result["count"],
                result["elapsed"], result["summary_render"])

    def _print_average_summary(self, results: list) -> None:
        if len(results) <= 1:
            return
        total_count = sum(r["count"] for r in results)
        if total_count <= 0:
            return
        # Aggregate metrics
        agg = self._create_async_metrics()
        for r in results:
            m = r["metrics"]
            for k in ("sum_read", "sum_preprocess", "sum_inference",
                      "sum_postprocess", "sum_render", "sum_save",
                      "sum_display"):
                agg[k] += m.get(k, 0.0)
            agg["infer_completed"] += m.get("infer_completed", 0)
        # Use max inflight from any loop
        agg["inflight_max"] = max(r["metrics"].get("inflight_max", 0)
                                  for r in results)
        total_elapsed = sum(r["elapsed"] for r in results)

        # infer_time_window: sum of all windows
        total_window = sum(r["metrics"].get("infer_time_window", 0.0)
                           for r in results)
        agg["inflight_time_sum"] = sum(r["metrics"].get("inflight_time_sum", 0.0)
                                       for r in results)
        if total_window > 0:
            agg["infer_first_ts"] = 0.0
            agg["infer_last_ts"] = total_window
        else:
            agg["infer_first_ts"] = 0.0
            agg["infer_last_ts"] = 0.0

        processed = len(results)
        if self._verbose:
            logger.info(f"\nAverage performance over {processed}"
                  f"/{self._loop} loops")
        print_async_performance_summary_legacy(
            agg, total_count, total_elapsed,
            any(r["summary_render"] for r in results))

    # ------------------------------------------------------------------
    # Stream dispatch (video / camera / rtsp)
    # ------------------------------------------------------------------

    def _run_stream(self, source: Union[str, int], display: bool) -> None:
        source_label = f"camera:{source}" if isinstance(source, int) else str(source)
        if self._verbose:
            logger.info(f"Input: {source_label}")
            probe_cap = cv2.VideoCapture(source)
            if probe_cap.isOpened():
                w = int(probe_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                h = int(probe_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = probe_cap.get(cv2.CAP_PROP_FPS)
                total = int(probe_cap.get(cv2.CAP_PROP_FRAME_COUNT))
                probe_cap.release()
                logger.info(f"Resolution: {w}x{h}, FPS: {fps:.1f}, "
                      f"Frames: {total if total > 0 else 'N/A'}")
            else:
                probe_cap.release()
        else:
            logger.info("Processing... Only FPS will be displayed.")

        need_run_dir = self._save or self._dump_tensors
        results = []

        for loop_idx in range(self._loop):
            if self._loop > 1 and self._verbose:
                logger.info(f"\n{'='*40}\n Loop [{loop_idx + 1}/{self._loop}]\n{'='*40}")

            save_enabled = self._save and (loop_idx == 0)
            run_dir = None
            if need_run_dir and (save_enabled or self._dump_tensors):
                src_name = f"camera{source}" if isinstance(source, int) \
                    else os.path.splitext(
                        os.path.basename(str(source)))[0] or "stream"
                run_dir = create_run_dir("stream", src_name, self._save_dir)
                write_run_info(run_dir, self._model_path, source)

            input_source = InputFactory.create(
                f"camera:{source}" if isinstance(source, int)
                else str(source))

            result = self._run_pipeline_once(
                input_source, display, save_enabled, run_dir,
                is_video=True)
            results.append(result)

            # Single loop: print immediately
            if self._loop <= 1:
                self._print_summary(result)

            if result.get("quit_requested", False):
                break

        if self._loop > 1:
            self._print_average_summary(results)

        # Re-raise worker exception
        self._reraise_worker_error()

    # ------------------------------------------------------------------
    # Image dispatch
    # ------------------------------------------------------------------

    def _run_image(self, image_path: str, display: bool) -> None:
        self._input_path = image_path
        self._verify_dumped = False
        if self._verbose:
            logger.info(f"Input image: {image_path}")
            img_probe = cv2.imread(image_path)
            if img_probe is not None:
                logger.info(f"Resolution (WxH): "
                      f"{img_probe.shape[1]}x{img_probe.shape[0]}")

        need_run_dir = self._save or self._dump_tensors
        results = []

        for loop_idx in range(self._loop):
            if self._loop > 1 and self._verbose:
                logger.info(f"\n{'='*40}\n Loop [{loop_idx + 1}/{self._loop}]\n{'='*40}")

            save_enabled = self._save and (loop_idx == 0)
            run_dir = None
            image_save_paths = None
            if need_run_dir and (save_enabled or self._dump_tensors):
                run_dir = create_run_dir(
                    "image", os.path.basename(image_path), self._save_dir)
                write_run_info(run_dir, self._model_path, image_path)
                if save_enabled:
                    base = os.path.splitext(os.path.basename(image_path))[0]
                    image_save_paths = [str(run_dir / f"{base}_result.jpg")]

            # Create a single-image iterable
            input_source = iter([cv2.imread(image_path)])

            result = self._run_pipeline_once(
                input_source, display, save_enabled, run_dir,
                image_save_paths=image_save_paths, is_video=False)
            results.append(result)

            if self._loop <= 1:
                self._print_summary(result)

            if result.get("quit_requested", False):
                break

        if self._loop > 1:
            self._print_average_summary(results)

        self._reraise_worker_error()

    def _run_image_dir(self, dir_path: str, display: bool) -> None:
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
        results = []

        for loop_idx in range(self._loop):
            if self._loop > 1 and self._verbose:
                logger.info(f"\n{'='*40}\n Loop [{loop_idx + 1}/{self._loop}]\n{'='*40}")

            save_enabled = self._save and (loop_idx == 0)
            run_dir = None
            image_save_paths = None
            if need_run_dir and (save_enabled or self._dump_tensors):
                run_dir = create_run_dir(
                    "image-dir", os.path.basename(dir_path), self._save_dir)
                write_run_info(run_dir, self._model_path, dir_path)
                if save_enabled:
                    image_save_paths = []
                    for img_p in image_files:
                        base = os.path.splitext(os.path.basename(img_p))[0]
                        image_save_paths.append(
                            str(run_dir / f"{base}_result.jpg"))

            # Create iterator that loads images
            def _load_images():
                for img_p in image_files:
                    img = cv2.imread(img_p)
                    if img is not None:
                        yield img

            result = self._run_pipeline_once(
                _load_images(), display, save_enabled, run_dir,
                image_save_paths=image_save_paths, is_video=False)
            results.append(result)

            if self._loop <= 1:
                self._print_summary(result)

            if result.get("quit_requested", False):
                break

        if self._loop > 1:
            self._print_average_summary(results)

        self._reraise_worker_error()

    # ------------------------------------------------------------------
    # Error re-raise
    # ------------------------------------------------------------------

    def _reraise_worker_error(self) -> None:
        if self._worker_error["exc"] is not None:
            exc = self._worker_error["exc"]
            name = self._worker_error["name"]
            if isinstance(exc, (FileNotFoundError, RuntimeError, ValueError)):
                raise exc
            raise RuntimeError(f"{name} failed: {exc}") from exc
