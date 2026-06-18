# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
SquatGameVisualizer — draws the pose skeleton + a squat-game HUD.

Subclasses the framework `PoseVisualizer` so the COCO skeleton/keypoints are
rendered by proven code, then overlays the game layer:
  - rep counter, current state (UP/DOWN), live knee angle
  - a vertical squat-depth bar
  - a transient "GOOD REP! +N" banner after each counted rep

The squat detection itself is delegated to the pure `SquatCounter`
(squat_logic.py); this class only translates per-frame `PoseResult`s into a knee
angle and renders. It is stateful across frames because the SyncRunner creates
one visualizer and calls `visualize()` for every frame.
"""

import logging
from typing import List, Optional

import cv2
import numpy as np

from common.visualizers import PoseVisualizer
from common.base import PoseResult

from .squat_logic import (
    SquatCounter, compute_angle,
    L_HIP, R_HIP, L_KNEE, R_KNEE, L_ANKLE, R_ANKLE,
)

logger = logging.getLogger(__name__)


class SquatGameVisualizer(PoseVisualizer):
    def __init__(self, stand_angle: float = 160.0, squat_angle: float = 100.0,
                 keypoint_confidence: float = 0.3):
        super().__init__(keypoint_confidence_threshold=keypoint_confidence)
        self.counter = SquatCounter(stand_angle=stand_angle, squat_angle=squat_angle)
        self.kpt_conf = keypoint_confidence
        self.frame_idx = 0
        self.last_angle: Optional[float] = None
        self._banner_frames = 0          # countdown for the GOOD REP banner

    # ---- geometry helpers --------------------------------------------------

    @staticmethod
    def _primary_pose(results: List[PoseResult]) -> Optional[PoseResult]:
        """Largest-box person = the main subject."""
        best, best_area = None, -1.0
        for p in results:
            if not p.keypoints or len(p.keypoints) < 17:
                continue
            if p.box and len(p.box) >= 4:
                area = abs((p.box[2] - p.box[0]) * (p.box[3] - p.box[1]))
            else:
                area = 0.0
            if area > best_area:
                best, best_area = p, area
        return best

    def _leg_angle(self, kps, hip_i, knee_i, ankle_i) -> Optional[float]:
        h, k, a = kps[hip_i], kps[knee_i], kps[ankle_i]
        if min(h.confidence, k.confidence, a.confidence) < self.kpt_conf:
            return None
        return compute_angle((h.x, h.y), (k.x, k.y), (a.x, a.y))

    def _knee_angle(self, pose: PoseResult) -> Optional[float]:
        kps = pose.keypoints
        angles = [
            a for a in (
                self._leg_angle(kps, L_HIP, L_KNEE, L_ANKLE),
                self._leg_angle(kps, R_HIP, R_KNEE, R_ANKLE),
            ) if a is not None
        ]
        if not angles:
            return None
        return sum(angles) / len(angles)

    # ---- main entry --------------------------------------------------------

    def visualize(self, image: np.ndarray, results: List[PoseResult]) -> np.ndarray:
        self.frame_idx += 1
        output = super().visualize(image, results)   # skeleton + keypoints

        pose = self._primary_pose(results)
        angle = self._knee_angle(pose) if pose is not None else None
        self.last_angle = angle
        if self.counter.update(angle):
            self._banner_frames = 18      # show banner for ~18 frames
            logger.info("Squat #%d counted (frame %d, knee=%.1f deg)",
                        self.counter.count, self.frame_idx,
                        angle if angle is not None else float("nan"))

        self._draw_hud(output, angle)
        return output

    # ---- HUD ---------------------------------------------------------------

    def _draw_hud(self, img: np.ndarray, angle: Optional[float]) -> None:
        h, w = img.shape[:2]

        # translucent top-left panel
        panel = img.copy()
        cv2.rectangle(panel, (10, 10), (330, 120), (20, 20, 20), -1)
        cv2.addWeighted(panel, 0.55, img, 0.45, 0, img)

        green, white, yellow = (80, 255, 80), (255, 255, 255), (60, 230, 255)
        state_color = green if self.counter.state == SquatCounter.UP else yellow

        cv2.putText(img, f"SQUATS: {self.counter.count}", (22, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.1, green, 3, cv2.LINE_AA)
        cv2.putText(img, f"STATE: {self.counter.state}", (22, 82),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, state_color, 2, cv2.LINE_AA)
        angle_txt = f"{angle:5.1f} deg" if angle is not None else "  --"
        cv2.putText(img, f"KNEE:  {angle_txt}", (22, 108),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, white, 2, cv2.LINE_AA)

        # vertical depth bar (right edge)
        bx2, by1, by2 = w - 25, 30, h - 30
        bx1 = bx2 - 26
        cv2.rectangle(img, (bx1, by1), (bx2, by2), white, 2)
        pct = self.counter.depth_pct(angle) / 100.0
        fill_h = int((by2 - by1) * pct)
        if fill_h > 0:
            cv2.rectangle(img, (bx1 + 2, by2 - fill_h),
                          (bx2 - 2, by2 - 2), yellow, -1)
        cv2.putText(img, "DEPTH", (bx1 - 12, by1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, white, 1, cv2.LINE_AA)

        # transient GOOD REP banner
        if self._banner_frames > 0:
            self._banner_frames -= 1
            txt = f"GOOD REP!  +{self.counter.count}"
            (tw, th), _ = cv2.getTextSize(txt, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 3)
            cx = (w - tw) // 2
            cv2.putText(img, txt, (cx, h // 2), cv2.FONT_HERSHEY_SIMPLEX,
                        1.2, (0, 0, 0), 6, cv2.LINE_AA)
            cv2.putText(img, txt, (cx, h // 2), cv2.FONT_HERSHEY_SIMPLEX,
                        1.2, green, 3, cv2.LINE_AA)
