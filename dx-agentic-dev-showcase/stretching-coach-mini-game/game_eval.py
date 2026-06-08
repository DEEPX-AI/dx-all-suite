#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""Dev/test helper: drive the REAL dx_app SyncRunner pipeline over a video and
yield the largest detected pose per frame.

Used by calibrate_coach_poses.py and verify.py. NOT part of the deployed game
(which is stretch_game_sync.py + factory + visualizer). It reuses SyncRunner's
own preprocess/infer/postprocess so measurement matches the runtime path exactly.
"""

import _bootstrap
_bootstrap.setup()

import cv2  # noqa: E402

from common.base import IPoseFactory  # noqa: E402
from common.processors import LetterboxPreprocessor, YOLOv8PosePostprocessor  # noqa: E402
from common.visualizers import PoseVisualizer  # noqa: E402
from common.runner import SyncRunner  # noqa: E402


class _MeasureFactory(IPoseFactory):
    """Plain yolo26n-pose factory (no game state) for measurement runs."""

    def __init__(self, config: dict = None):
        self.config = config or {}

    def create_preprocessor(self, input_width, input_height):
        return LetterboxPreprocessor(input_width, input_height)

    def create_postprocessor(self, input_width, input_height):
        return YOLOv8PosePostprocessor(input_width, input_height, self.config)

    def create_visualizer(self):
        return PoseVisualizer()

    def get_model_name(self):
        return "yolo26n_pose"

    def get_task_type(self):
        return "pose_estimation"

    def get_num_keypoints(self):
        return 17


def build_runner(model_path: str, config_path: str = None) -> SyncRunner:
    """Construct a SyncRunner and initialise the engine + processors."""
    runner = SyncRunner(_MeasureFactory())
    runner._init_engine(model_path, config_path)
    return runner


def _box_area(pose) -> float:
    b = getattr(pose, "box", None)
    if not b or len(b) < 4:
        return 0.0
    return max(0.0, (b[2] - b[0])) * max(0.0, (b[3] - b[1]))


def largest_pose(results):
    """Return the PoseResult with the largest bounding box, or None."""
    if not results:
        return None
    return max(results, key=_box_area)


def iter_results(runner: SyncRunner, video_path: str):
    """Yield (frame_idx, frame_bgr, results_list) for each video frame."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video: {video_path}")
    idx = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            idx += 1
            tensor, ctx = runner.preprocess(frame)
            outputs = runner.infer(tensor)
            results = runner.postprocess(outputs, ctx)
            yield idx, frame, results
    finally:
        cap.release()


def iter_poses(runner: SyncRunner, video_path: str):
    """Yield (frame_idx, frame_bgr, largest_pose_or_None) for each video frame."""
    for idx, frame, results in iter_results(runner, video_path):
        yield idx, frame, largest_pose(results)
