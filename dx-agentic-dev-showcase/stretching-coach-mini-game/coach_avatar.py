#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
Animated stick-figure "coach" avatar.

Renders a clean COCO-17 skeleton (head circle + torso/arms/legs) inside a panel
rectangle, interpolating between a neutral standing pose and the stretch's target
pose by an animation phase in [0, 1]. Target/neutral skeletons come from
coach_poses.json (clip-calibrated, with hand-derived fallback).

Dependency-light: numpy + cv2 only.
"""

from typing import Dict, List, Tuple
import numpy as np
import cv2

# COCO-17 limb edges used for the stick figure (head handled separately).
_EDGES: List[Tuple[int, int]] = [
    (5, 7), (7, 9),        # left arm
    (6, 8), (8, 10),       # right arm
    (5, 6),                # shoulders
    (5, 11), (6, 12),      # torso sides
    (11, 12),              # hips
    (11, 13), (13, 15),    # left leg
    (12, 14), (14, 16),    # right leg
    (0, 5), (0, 6),        # neck -> shoulders
]
NOSE, L_EAR, R_EAR = 0, 3, 4

_LIMB_COLOR = (80, 220, 255)   # warm yellow
_JOINT_COLOR = (60, 180, 255)
_HEAD_COLOR = (120, 235, 255)


class CoachAvatar:
    def __init__(self, coach_poses: Dict):
        self.neutral = np.asarray(coach_poses["neutral"], dtype=np.float32)
        self.targets = {k: np.asarray(v, dtype=np.float32)
                        for k, v in coach_poses["targets"].items()}

    def _interp(self, stretch_key: str, phase: float) -> np.ndarray:
        target = self.targets.get(stretch_key, self.neutral)
        phase = float(np.clip(phase, 0.0, 1.0))
        return (1.0 - phase) * self.neutral + phase * target

    def render(self, canvas: np.ndarray, rect: Tuple[int, int, int, int],
               stretch_key: str, phase: float) -> None:
        """Draw the animated coach figure inside rect = (x, y, w, h)."""
        rx, ry, rw, rh = rect
        pose = self._interp(stretch_key, phase)

        pad = int(min(rw, rh) * 0.12)
        ax, ay = rx + pad, ry + pad
        aw, ah = rw - 2 * pad, rh - 2 * pad

        def to_px(p) -> Tuple[int, int]:
            return (int(ax + float(p[0]) * aw), int(ay + float(p[1]) * ah))

        thickness = max(2, int(min(rw, rh) * 0.025))

        # limbs
        for a, b in _EDGES:
            cv2.line(canvas, to_px(pose[a]), to_px(pose[b]),
                     _LIMB_COLOR, thickness, cv2.LINE_AA)
        # joints
        for i in range(5, 17):
            cv2.circle(canvas, to_px(pose[i]), max(2, thickness),
                       _JOINT_COLOR, -1, cv2.LINE_AA)
        # head circle (radius from ear span, fallback to a fraction of panel)
        head = to_px(pose[NOSE])
        ear_l = to_px(pose[L_EAR])
        ear_r = to_px(pose[R_EAR])
        r = int(max(np.hypot(ear_l[0] - ear_r[0], ear_l[1] - ear_r[1]) * 0.7,
                    min(aw, ah) * 0.07))
        cv2.circle(canvas, head, r, _HEAD_COLOR, thickness, cv2.LINE_AA)


def triangle_phase(frame_index: int, period_frames: int) -> float:
    """Smooth 0->1->0 looping phase for the neutral<->target demonstration."""
    period_frames = max(2, int(period_frames))
    t = (frame_index % period_frames) / float(period_frames)   # 0..1
    return 1.0 - abs(2.0 * t - 1.0)                              # triangle wave
