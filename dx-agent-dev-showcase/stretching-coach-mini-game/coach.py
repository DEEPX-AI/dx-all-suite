#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""Animated stick-figure "coach" avatar for the stretch mini-game.

Draws a clean COCO-17 skeleton inside a panel and animates it by cycling between
a neutral standing pose and the target stretch pose. All template skeletons are
normalized (hip-mid origin, leg length = 1.0) and were derived from the sample
clips by calibrate_coach_poses.py.
"""

import json
import math
from pathlib import Path
from typing import Dict, List, Tuple

# COCO-17 skeleton as keypoint-name pairs (independent of common/, so the coach
# is drawable without the framework loaded).
EDGES: List[Tuple[str, str]] = [
    ("left_ankle", "left_knee"), ("left_knee", "left_hip"),
    ("right_ankle", "right_knee"), ("right_knee", "right_hip"),
    ("left_hip", "right_hip"), ("left_shoulder", "left_hip"),
    ("right_shoulder", "right_hip"), ("left_shoulder", "right_shoulder"),
    ("left_shoulder", "left_elbow"), ("right_shoulder", "right_elbow"),
    ("left_elbow", "left_wrist"), ("right_elbow", "right_wrist"),
    ("left_shoulder", "nose"), ("right_shoulder", "nose"),
]
HEAD_KP = "nose"

# Fixed normalized view box so the figure never rescales mid-animation
# (wrists reach ~ -2.5 in y during the overhead pose).
_VIEW = (-0.85, 0.85, -2.65, 1.20)  # (xmin, xmax, ymin, ymax)

_LIMB_COLOR = (255, 210, 90)    # BGR cyan-ish
_JOINT_COLOR = (60, 220, 255)   # BGR amber
_HEAD_COLOR = (120, 255, 120)


class CoachAvatar:
    def __init__(self, templates: Dict[str, Dict[str, list]]):
        self.t = templates or {}

    @classmethod
    def from_file(cls, path) -> "CoachAvatar":
        p = Path(path)
        if p.is_file():
            return cls(json.loads(p.read_text()))
        return cls({})

    @staticmethod
    def _lerp(a, b, t):
        return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)

    def _interpolated_pose(self, stage_key: str, phase: float) -> Dict[str, Tuple[float, float]]:
        neutral = self.t.get("neutral", {})
        target = self.t.get(stage_key, {})
        if not target:
            target = neutral
        # smooth 0 -> 1 -> 0 demonstration loop
        a = 0.5 - 0.5 * math.cos(2.0 * math.pi * (phase % 1.0))
        names = set(neutral) & set(target)
        pose = {}
        for n in names:
            pose[n] = self._lerp(tuple(neutral[n]), tuple(target[n]), a)
        return pose

    @staticmethod
    def _make_mapper(rect: Tuple[int, int, int, int]):
        x, y, w, h = rect
        xmin, xmax, ymin, ymax = _VIEW
        sx = w / (xmax - xmin)
        sy = h / (ymax - ymin)
        s = min(sx, sy)
        # center the view box inside the rect
        off_x = x + (w - s * (xmax - xmin)) / 2.0
        off_y = y + (h - s * (ymax - ymin)) / 2.0

        def to_px(nx, ny):
            return (int(off_x + (nx - xmin) * s), int(off_y + (ny - ymin) * s))
        return to_px

    def draw(self, frame, stage_key: str, rect: Tuple[int, int, int, int],
             phase: float) -> None:
        """Draw the animated coach figure inside ``rect`` (x, y, w, h) on frame."""
        import cv2
        pose = self._interpolated_pose(stage_key, phase)
        if not pose:
            return
        to_px = self._make_mapper(rect)
        pts: Dict[str, Tuple[int, int]] = {n: to_px(p[0], p[1]) for n, p in pose.items()}

        for a, b in EDGES:
            if a in pts and b in pts:
                cv2.line(frame, pts[a], pts[b], _LIMB_COLOR, 3, cv2.LINE_AA)
        # head circle scaled to figure size
        if HEAD_KP in pts:
            r = max(6, rect[3] // 18)
            cv2.circle(frame, pts[HEAD_KP], r, _HEAD_COLOR, 2, cv2.LINE_AA)
        for n, p in pts.items():
            if n in ("left_eye", "right_eye", "left_ear", "right_ear", HEAD_KP):
                continue
            cv2.circle(frame, p, 4, _JOINT_COLOR, -1, cv2.LINE_AA)
