"""
Profiling utilities for measuring inference performance.
"""

import time
from typing import List, Optional, Dict
from dataclasses import dataclass, field
import threading


@dataclass
class ProfilingMetrics:
    """
    Performance metrics collection for synchronous inference.
    
    Tracks preprocessing, inference, and postprocessing times
    to provide overall and per-stage performance analysis.
    """
    preprocess_times: List[float] = field(default_factory=list)
    inference_times: List[float] = field(default_factory=list)
    postprocess_times: List[float] = field(default_factory=list)
    total_times: List[float] = field(default_factory=list)
    
    def add_preprocess_time(self, time_sec: float) -> None:
        """Add preprocessing time measurement."""
        self.preprocess_times.append(time_sec)
    
    def add_inference_time(self, time_sec: float) -> None:
        """Add inference time measurement."""
        self.inference_times.append(time_sec)
    
    def add_postprocess_time(self, time_sec: float) -> None:
        """Add postprocessing time measurement."""
        self.postprocess_times.append(time_sec)
    
    def add_total_time(self, time_sec: float) -> None:
        """Add total frame time measurement."""
        self.total_times.append(time_sec)
    
    def get_frame_count(self) -> int:
        """Get the number of processed frames."""
        return len(self.total_times) if self.total_times else len(self.inference_times)
    
    def _get_avg(self, times: List[float]) -> float:
        """Calculate average time in milliseconds."""
        return (sum(times) / len(times) * 1000) if times else 0.0
    
    def get_avg_preprocess_ms(self) -> float:
        return self._get_avg(self.preprocess_times)
    
    def get_avg_inference_ms(self) -> float:
        return self._get_avg(self.inference_times)
    
    def get_avg_postprocess_ms(self) -> float:
        return self._get_avg(self.postprocess_times)
    
    def get_avg_total_ms(self) -> float:
        return self._get_avg(self.total_times)
    
    def get_fps(self) -> float:
        """Calculate average frames per second."""
        if not self.total_times:
            return 0.0
        avg_time = sum(self.total_times) / len(self.total_times)
        return 1.0 / avg_time if avg_time > 0 else 0.0
    
    def reset(self) -> None:
        """Reset all measurements."""
        self.preprocess_times.clear()
        self.inference_times.clear()
        self.postprocess_times.clear()
        self.total_times.clear()


@dataclass
class AsyncProfilingMetrics:
    """
    Performance metrics for asynchronous pipeline inference.
    
    Tracks queue sizes, throughput, and latency for async processing.
    """
    preprocess_times: List[float] = field(default_factory=list)
    inference_times: List[float] = field(default_factory=list)
    postprocess_times: List[float] = field(default_factory=list)
    end_to_end_times: List[float] = field(default_factory=list)
    queue_sizes: List[int] = field(default_factory=list)
    _lock: threading.Lock = field(default_factory=threading.Lock)
    
    def add_preprocess_time(self, time_sec: float) -> None:
        with self._lock:
            self.preprocess_times.append(time_sec)
    
    def add_inference_time(self, time_sec: float) -> None:
        with self._lock:
            self.inference_times.append(time_sec)
    
    def add_postprocess_time(self, time_sec: float) -> None:
        with self._lock:
            self.postprocess_times.append(time_sec)
    
    def add_end_to_end_time(self, time_sec: float) -> None:
        with self._lock:
            self.end_to_end_times.append(time_sec)
    
    def add_queue_size(self, size: int) -> None:
        with self._lock:
            self.queue_sizes.append(size)
    
    def get_frame_count(self) -> int:
        with self._lock:
            return len(self.end_to_end_times) if self.end_to_end_times else len(self.inference_times)
    
    def _get_avg(self, times: List[float]) -> float:
        return (sum(times) / len(times) * 1000) if times else 0.0
    
    def get_avg_preprocess_ms(self) -> float:
        with self._lock:
            return self._get_avg(self.preprocess_times)
    
    def get_avg_inference_ms(self) -> float:
        with self._lock:
            return self._get_avg(self.inference_times)
    
    def get_avg_postprocess_ms(self) -> float:
        with self._lock:
            return self._get_avg(self.postprocess_times)
    
    def get_avg_end_to_end_ms(self) -> float:
        with self._lock:
            return self._get_avg(self.end_to_end_times)
    
    def get_throughput(self) -> float:
        with self._lock:
            if not self.end_to_end_times:
                return 0.0
            avg_time = sum(self.end_to_end_times) / len(self.end_to_end_times)
            return 1.0 / avg_time if avg_time > 0 else 0.0
    
    def get_avg_queue_size(self) -> float:
        with self._lock:
            return sum(self.queue_sizes) / len(self.queue_sizes) if self.queue_sizes else 0.0
    
    def reset(self) -> None:
        with self._lock:
            self.preprocess_times.clear()
            self.inference_times.clear()
            self.postprocess_times.clear()
            self.end_to_end_times.clear()
            self.queue_sizes.clear()


class Timer:
    """
    Context manager for timing code blocks.
    
    Usage:
        with Timer() as t:
            do_something()
        print(f"Elapsed: {t.elapsed_ms:.2f}ms")
    """
    
    def __init__(self):
        self._start: float = 0.0
        self._end: float = 0.0
        self._elapsed: float = 0.0
    
    def __enter__(self) -> 'Timer':
        self._start = time.perf_counter()
        return self
    
    def __exit__(self, *args) -> None:
        self._end = time.perf_counter()
        self._elapsed = self._end - self._start
    
    @property
    def elapsed(self) -> float:
        """Elapsed time in seconds."""
        return self._elapsed
    
    @property
    def elapsed_ms(self) -> float:
        """Elapsed time in milliseconds."""
        return self._elapsed * 1000


def print_performance_summary(metrics: ProfilingMetrics, 
                              model_name: str = "Model",
                              show_individual: bool = False) -> None:
    """
    Print a formatted performance summary.
    
    Args:
        metrics: ProfilingMetrics object with collected data
        model_name: Name of the model for display
        show_individual: Whether to show individual stage times
    """
    print(f"\n{'='*60}")
    print(f" Performance Summary: {model_name}")
    print(f"{'='*60}")
    print(f"  Total Frames Processed: {metrics.get_frame_count()}")
    print(f"  Average FPS: {metrics.get_fps():.2f}")
    print(f"{'='*60}")
    
    if show_individual:
        print("  Stage Breakdown:")
        print(f"    Preprocessing:  {metrics.get_avg_preprocess_ms():>8.2f} ms")
        print(f"    Inference:      {metrics.get_avg_inference_ms():>8.2f} ms")
        print(f"    Postprocessing: {metrics.get_avg_postprocess_ms():>8.2f} ms")
        print(f"{'='*60}")
    
    print(f"  Average Total:    {metrics.get_avg_total_ms():>8.2f} ms/frame")
    print(f"{'='*60}\n")


def print_async_performance_summary(metrics: AsyncProfilingMetrics,
                                    model_name: str = "Model") -> None:
    """
    Print a formatted performance summary for async processing.
    
    Args:
        metrics: AsyncProfilingMetrics object with collected data
        model_name: Name of the model for display
    """
    print(f"\n{'='*60}")
    print(f" Async Performance Summary: {model_name}")
    print(f"{'='*60}")
    print(f"  Total Frames Processed: {metrics.get_frame_count()}")
    print(f"  Throughput: {metrics.get_throughput():.2f} FPS")
    print(f"{'='*60}")
    print("  Stage Breakdown (avg):")
    print(f"    Preprocessing:  {metrics.get_avg_preprocess_ms():>8.2f} ms")
    print(f"    Inference:      {metrics.get_avg_inference_ms():>8.2f} ms")
    print(f"    Postprocessing: {metrics.get_avg_postprocess_ms():>8.2f} ms")
    print(f"{'='*60}")
    print(f"  End-to-End Latency: {metrics.get_avg_end_to_end_ms():>8.2f} ms")
    print(f"  Avg Queue Size:     {metrics.get_avg_queue_size():>8.1f}")
    print(f"{'='*60}\n")


def print_image_processing_summary(t_start, t0, t1, t2, t3, t4=None, t5=None):
    """
    Print legacy-format image processing summary.
    
    Args:
        t_start: Start time (before read)
        t0: After read
        t1: After preprocess
        t2: After inference
        t3: After postprocess
        t4: After render (optional)
        t5: After display (optional, requires t4)
    """
    read_time = (t0 - t_start) * 1000.0
    preprocess_time = (t1 - t0) * 1000.0
    inference_time = (t2 - t1) * 1000.0
    postprocess_time = (t3 - t2) * 1000.0

    def _row(label, ms):
        fps = 1000.0 / ms if ms > 0 else 0.0
        print(f" {label:<15} {ms:8.2f} ms     {fps:6.1f} FPS")

    print("\n" + "=" * 50)
    print(f"{'PERFORMANCE SUMMARY':^50}")
    print("=" * 50)
    print(f" {'Pipeline Step':<15} {'Avg Latency':<15} {'Throughput':<15}")
    print("-" * 50)
    _row("Read", read_time)
    _row("Preprocess", preprocess_time)
    _row("Inference", inference_time)
    _row("Postprocess", postprocess_time)

    last_ts = t3
    if t4 is not None:
        draw_time = (t4 - t3) * 1000.0
        _row("Render", draw_time)
        last_ts = t4
    if t5 is not None and t4 is not None:
        display_time = (t5 - t4) * 1000.0
        _row("Display", display_time)
        last_ts = t5

    total_time = (last_ts - t_start) * 1000.0
    print("-" * 50)
    print(f" {'Total Frames':<15} : {'1':>6}")
    print(f" {'Total Time':<15} : {total_time / 1000.0:6.1f} s")
    overall_fps = 1000.0 / total_time if total_time > 0 else 0.0
    print(f" {'Overall FPS':<15} : {overall_fps:6.1f} FPS")
    print("=" * 50)


def _print_metric_line(label: str, total_sum: float, cnt: int) -> None:
    """Print a single metric line if sum > 0."""
    avg = total_sum / cnt * 1000.0
    fps = 1000.0 / avg if avg > 0 else 0.0
    print(f" {label:<15} {avg:8.2f} ms     {fps:6.1f} FPS")


def _print_optional_metrics(metrics: dict, cnt: int) -> None:
    """Print render/save/display metrics when present."""
    if cnt <= 0:
        return
    sum_render = metrics.get("sum_render", 0.0)
    if sum_render > 0:
        _print_metric_line("Render", sum_render, cnt)
    sum_save = metrics.get("sum_save", 0.0)
    if sum_save > 0:
        _print_metric_line("Save", sum_save, cnt)
    sum_display = metrics.get("sum_display", 0.0)
    if sum_display > 0:
        _print_metric_line("Display", sum_display, cnt)


def print_sync_performance_summary(
    metrics: dict, cnt: int, elapsed: float, display: bool
):
    """Print legacy-format performance metrics for video/stream."""
    overall_fps = cnt / elapsed if elapsed > 0 else 0.0
    avg_read = metrics["sum_read"] / cnt * 1000.0
    avg_pre = metrics["sum_preprocess"] / cnt * 1000.0
    avg_inf = metrics["sum_inference"] / cnt * 1000.0
    avg_post = metrics["sum_postprocess"] / cnt * 1000.0
    read_fps = 1000.0 / avg_read if avg_read > 0 else 0.0
    pre_fps = 1000.0 / avg_pre if avg_pre > 0 else 0.0
    inf_fps = 1000.0 / avg_inf if avg_inf > 0 else 0.0
    post_fps = 1000.0 / avg_post if avg_post > 0 else 0.0
    
    print("\n" + "=" * 50)
    print(f"{'PERFORMANCE SUMMARY':^50}")
    print("=" * 50)
    print(f" {'Pipeline Step':<15} {'Avg Latency':<15} {'Throughput':<15}")
    print("-" * 50)
    print(f" {'Read':<15} {avg_read:8.2f} ms     {read_fps:6.1f} FPS")
    print(f" {'Preprocess':<15} {avg_pre:8.2f} ms     {pre_fps:6.1f} FPS")
    print(f" {'Inference':<15} {avg_inf:8.2f} ms     {inf_fps:6.1f} FPS")
    print(f" {'Postprocess':<15} {avg_post:8.2f} ms     {post_fps:6.1f} FPS")

    if display:
        _print_optional_metrics(metrics, cnt)

    print("-" * 50)
    print(f" {'Total Frames':<15} : {cnt:6d}")
    print(f" {'Total Time':<15} : {elapsed:6.1f} s")
    print(f" {'Overall FPS':<15} : {overall_fps:6.1f} FPS")
    print("=" * 50)


def _print_async_optional_metrics(metrics: dict, infer_completed: int) -> None:
    """Print render/save/display metrics using async-specific counters."""
    render_cnt = metrics.get("render_completed", infer_completed)
    if render_cnt > 0:
        _print_metric_line("Render", metrics["sum_render"], render_cnt)

    save_cnt = metrics.get("save_completed", 0)
    sum_save = metrics.get("sum_save", 0.0)
    if save_cnt > 0 and sum_save > 0:
        _print_metric_line("Save", sum_save, save_cnt)

    disp_cnt = metrics.get("display_completed", 0)
    sum_disp = metrics.get("sum_display", 0.0)
    if disp_cnt > 0 and sum_disp > 0:
        _print_metric_line("Display", sum_disp, disp_cnt)


def print_async_performance_summary_legacy(
    metrics: dict, cnt: int, elapsed: float, display: bool
):
    """Print legacy-format async performance metrics (matches C++ async format)."""
    if metrics.get("infer_completed", 0) == 0:
        print("[WARNING] No frames were processed.")
        return

    overall_fps = cnt / elapsed if elapsed > 0 else 0.0
    infer_completed = metrics["infer_completed"]
    avg_read = metrics["sum_read"] / infer_completed * 1000.0
    avg_pre = metrics["sum_preprocess"] / infer_completed * 1000.0
    avg_inf = metrics["sum_inference"] / infer_completed * 1000.0
    avg_post = metrics["sum_postprocess"] / infer_completed * 1000.0

    infer_first = metrics.get("infer_first_ts", 0.0) or 0.0
    infer_last = metrics.get("infer_last_ts", 0.0) or 0.0
    inflight_time_window = infer_last - infer_first
    infer_tp = infer_completed / inflight_time_window if inflight_time_window > 0 else 0.0

    inflight_avg = metrics["inflight_time_sum"] / inflight_time_window if inflight_time_window > 0 else 0.0
    inflight_max = metrics["inflight_max"]

    read_fps = 1000.0 / avg_read if avg_read > 0 else 0.0
    pre_fps = 1000.0 / avg_pre if avg_pre > 0 else 0.0
    post_fps = 1000.0 / avg_post if avg_post > 0 else 0.0

    print("\n" + "=" * 50)
    print(f"{'PERFORMANCE SUMMARY':^50}")
    print("=" * 50)
    print(f" {'Pipeline Step':<15} {'Avg Latency':<15} {'Throughput':<15}")
    print("-" * 50)
    print(f" {'Read':<15} {avg_read:8.2f} ms     {read_fps:6.1f} FPS")
    print(f" {'Preprocess':<15} {avg_pre:8.2f} ms     {pre_fps:6.1f} FPS")
    print(f" {'Inference':<15} {avg_inf:8.2f} ms     {infer_tp:6.1f} FPS*")
    print(f" {'Postprocess':<15} {avg_post:8.2f} ms     {post_fps:6.1f} FPS")

    # Render/Save/Display rows (conditional)
    _print_async_optional_metrics(metrics, infer_completed)

    print("-" * 50)
    print(" * Async: turnaround latency (submit to callback)")
    print("   Throughput measured independently")
    print("-" * 50)
    print(f" {'Infer Completed':<19} :    {infer_completed}")
    print(f" {'Infer Inflight Avg':<19} :    {inflight_avg:.1f}")
    print(f" {'Infer Inflight Max':<19} :      {inflight_max}")
    print("-" * 50)
    print(f" {'Total Frames':<19} :    {cnt}")
    print(f" {'Total Time':<19} :    {elapsed:.1f} s")
    print(f" {'Overall FPS':<19} :   {overall_fps:.1f} FPS")
    print("=" * 50)
