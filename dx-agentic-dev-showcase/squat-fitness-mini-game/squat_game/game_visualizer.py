"""Arcade-style squat fitness-game visualizer for yolo26n_pose.

Subclasses the framework PoseVisualizer (so the skeleton is still drawn), then
runs a stateful squat rep counter and overlays a game HUD on every frame. A
single instance is created by the factory and reused across all frames by
SyncRunner, which is what lets the rep count and score persist over the video.
"""
import cv2
import numpy as np
from typing import List, Optional

from common.base import PoseResult
from common.visualizers import PoseVisualizer

from squat_game.squat_counter import compute_angle, SquatCounter

# COCO-17 keypoint indices
L_SHO, R_SHO = 5, 6
L_HIP, R_HIP = 11, 12
L_KNEE, R_KNEE = 13, 14
L_ANK, R_ANK = 15, 16

# Depth bar maps knee angle [UP_REF .. DOWN_REF] -> [empty .. full]
_DEPTH_UP_REF = 165.0
_DEPTH_DOWN_REF = 120.0


class SquatGameVisualizer(PoseVisualizer):
    """Pose visualizer + squat rep counter + arcade HUD."""

    def __init__(self, config: dict = None):
        super().__init__()
        cfg = config or {}
        self.counter = SquatCounter(
            down_angle=float(cfg.get("down_angle", 140.0)),
            up_angle=float(cfg.get("up_angle", 160.0)),
        )
        self.target_reps = int(cfg.get("target_reps", 5))
        self.points_per_rep = int(cfg.get("points_per_rep", 10))
        self.kp_conf = float(cfg.get("keypoint_confidence", 0.3))
        self.score = 0
        self._flash = 0  # frames remaining to show the GOOD! pop

    # ------------------------------------------------------------------
    # keypoint -> angle helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _largest_pose(results: List[PoseResult]) -> Optional[PoseResult]:
        """The closest player = the pose with the largest bounding-box area."""
        best, best_area = None, -1.0
        for r in results:
            if not r.keypoints:
                continue
            area = r.area() if hasattr(r, "area") else 0.0
            if area > best_area:
                best, best_area = r, area
        return best

    def _joint(self, kps, idx):
        if idx >= len(kps):
            return None
        kp = kps[idx]
        if kp.confidence < self.kp_conf:
            return None
        return (kp.x, kp.y)

    def _side_angle(self, kps, hip, knee, ankle):
        h = self._joint(kps, hip)
        k = self._joint(kps, knee)
        a = self._joint(kps, ankle)
        if h is None or k is None or a is None:
            return None
        return compute_angle(h, k, a)

    def _knee_angle(self, kps) -> Optional[float]:
        """Mean of whichever knee angles (L/R) have confident keypoints."""
        angles = [a for a in (
            self._side_angle(kps, L_HIP, L_KNEE, L_ANK),
            self._side_angle(kps, R_HIP, R_KNEE, R_ANK),
        ) if a is not None]
        return sum(angles) / len(angles) if angles else None

    def _hip_angle(self, kps) -> Optional[float]:
        """Mean torso-thigh (shoulder-hip-knee) angle; gates / informs depth."""
        angles = [a for a in (
            self._side_angle(kps, L_SHO, L_HIP, L_KNEE),
            self._side_angle(kps, R_SHO, R_HIP, R_KNEE),
        ) if a is not None]
        return sum(angles) / len(angles) if angles else None

    # ------------------------------------------------------------------
    # main entry (called per frame by SyncRunner)
    # ------------------------------------------------------------------
    def visualize(self, image: np.ndarray, results: List[PoseResult]) -> np.ndarray:
        output = super().visualize(image, results)
        pose = self._largest_pose(results)
        knee = self._knee_angle(pose.keypoints) if pose else None
        hip = self._hip_angle(pose.keypoints) if pose else None

        if self.counter.update(knee):
            self.score += self.points_per_rep
            self._flash = 12

        self._draw_ui(output, knee, hip, pose is not None)
        if self._flash > 0:
            self._flash -= 1
        return output

    # ------------------------------------------------------------------
    # HUD
    # ------------------------------------------------------------------
    def _draw_ui(self, img: np.ndarray, knee, hip, has_pose: bool) -> None:
        h, w = img.shape[:2]
        won = self.counter.reps >= self.target_reps

        # --- top scoreboard ---
        cv2.rectangle(img, (0, 0), (w, 72), (0, 0, 0), -1)
        cv2.rectangle(img, (0, 0), (w, 72), (0, 215, 255), 2)
        cv2.putText(img, f"REPS {self.counter.reps}/{self.target_reps}",
                    (16, 50), cv2.FONT_HERSHEY_DUPLEX, 1.1,
                    (0, 215, 255), 2, cv2.LINE_AA)
        score_txt = f"SCORE {self.score}"
        (sw, _), _ = cv2.getTextSize(score_txt, cv2.FONT_HERSHEY_DUPLEX, 1.1, 2)
        cv2.putText(img, score_txt, (w - sw - 16, 50),
                    cv2.FONT_HERSHEY_DUPLEX, 1.1, (80, 255, 80), 2, cv2.LINE_AA)

        # --- depth gauge (left) from knee angle ---
        if knee is not None:
            frac = (_DEPTH_UP_REF - knee) / (_DEPTH_UP_REF - _DEPTH_DOWN_REF)
            frac = max(0.0, min(1.0, frac))
            bx, by, bw, bh = 16, 92, 30, max(40, h - 170)
            cv2.rectangle(img, (bx, by), (bx + bw, by + bh), (255, 255, 255), 2)
            fill = int(bh * frac)
            cv2.rectangle(img, (bx, by + bh - fill), (bx + bw, by + bh),
                          (0, 165, 255), -1)
            cv2.putText(img, "DEPTH", (bx - 2, by + bh + 22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1,
                        cv2.LINE_AA)
            cv2.putText(img, f"{int(knee)}deg", (bx - 2, by - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 1,
                        cv2.LINE_AA)

        # --- big state text (bottom-center) ---
        if won:
            txt, col = "WIN!", (0, 255, 0)
        elif not has_pose:
            txt, col = "STAND IN VIEW", (200, 200, 200)
        elif self._flash > 0:
            txt, col = "GOOD!", (0, 255, 0)
        elif self.counter.state == "DOWN":
            txt, col = "DOWN", (0, 165, 255)
        else:
            txt, col = "UP", (255, 200, 0)

        scale = 2.2 if txt != "STAND IN VIEW" else 1.2
        (tw, th), _ = cv2.getTextSize(txt, cv2.FONT_HERSHEY_DUPLEX, scale, 4)
        org = ((w - tw) // 2, h - 40)
        cv2.putText(img, txt, org, cv2.FONT_HERSHEY_DUPLEX, scale,
                    (0, 0, 0), 8, cv2.LINE_AA)
        cv2.putText(img, txt, org, cv2.FONT_HERSHEY_DUPLEX, scale,
                    col, 4, cv2.LINE_AA)

        # --- win banner ---
        if won:
            banner = "TARGET REACHED!"
            (bwid, bht), _ = cv2.getTextSize(
                banner, cv2.FONT_HERSHEY_DUPLEX, 1.3, 3)
            cv2.putText(img, banner, ((w - bwid) // 2, h // 2),
                        cv2.FONT_HERSHEY_DUPLEX, 1.3, (0, 0, 0), 7, cv2.LINE_AA)
            cv2.putText(img, banner, ((w - bwid) // 2, h // 2),
                        cv2.FONT_HERSHEY_DUPLEX, 1.3, (0, 255, 0), 3,
                        cv2.LINE_AA)
