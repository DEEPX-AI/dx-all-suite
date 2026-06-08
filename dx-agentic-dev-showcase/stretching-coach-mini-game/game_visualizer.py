#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
StretchGameVisualizer — the arcade stretching-game state machine + UI overlay.

Subclasses the stock PoseVisualizer so the player's body skeleton is drawn with
the framework's renderer, then overlays the game UI: STAGE x/3 header, an animated
coach avatar (top-left), the stretch name + instruction, a HOLD progress bar, and
GOOD! / CLEAR! feedback. All game state lives on the instance and persists across
frames (the runner reuses one visualizer for the whole stream — SyncRunner keeps
frames ordered, which is required for correct hold-timing).
"""

from typing import List, Optional
import json
import os

import numpy as np
import cv2

from common.visualizers import PoseVisualizer
from common.base import PoseResult

from stretch_pose_rules import STRETCHES, StretchTracker, DEFAULT_RULE_CFG
from coach_avatar import CoachAvatar, triangle_phase

# arcade palette (BGR)
_C_HEADER_BG = (40, 30, 20)
_C_ACCENT = (80, 220, 255)
_C_WHITE = (255, 255, 255)
_C_GOOD = (90, 255, 90)
_C_CLEAR = (90, 255, 255)
_C_BAR_BG = (60, 60, 60)
_C_BAR_FG = (90, 230, 120)


def _pose_to_kp(pose: PoseResult) -> np.ndarray:
    kp = np.zeros((17, 3), dtype=np.float32)
    for i, k in enumerate(pose.keypoints[:17]):
        kp[i] = (k.x, k.y, k.confidence)
    return kp


def _largest_person(results: List[PoseResult]) -> Optional[PoseResult]:
    people = [r for r in results if r.keypoints and len(r.keypoints) >= 17]
    if not people:
        return None
    return max(people, key=lambda r: (r.box[2] - r.box[0]) * (r.box[3] - r.box[1])
               if r.box and len(r.box) >= 4 else 0.0)


def _text(img, s, org, scale, color, thick=2):
    cv2.putText(img, s, org, cv2.FONT_HERSHEY_DUPLEX, scale, (0, 0, 0),
                thick + 3, cv2.LINE_AA)
    cv2.putText(img, s, org, cv2.FONT_HERSHEY_DUPLEX, scale, color,
                thick, cv2.LINE_AA)


def _panel(img, x, y, w, h, alpha=0.55):
    sub = img[y:y + h, x:x + w]
    if sub.size == 0:
        return
    dark = np.zeros_like(sub)
    img[y:y + h, x:x + w] = cv2.addWeighted(sub, 1 - alpha, dark, alpha, 0)
    cv2.rectangle(img, (x, y), (x + w, y + h), _C_ACCENT, 2, cv2.LINE_AA)


class StretchGameVisualizer(PoseVisualizer):

    def __init__(self, config: dict = None, coach_poses: dict = None):
        super().__init__(draw_box=False, keypoint_radius=4, skeleton_thickness=3)
        cfg = config or {}
        self.rules_cfg = {**DEFAULT_RULE_CFG, **cfg.get("rules", {})}
        game = cfg.get("game", {})
        self.assumed_fps = float(game.get("assumed_fps", 24))
        self.hold_seconds = float(game.get("hold_seconds", 1.5))
        self.coach_loop_seconds = float(game.get("coach_loop_seconds", 2.4))
        miss_tol = int(game.get("miss_tolerance", 6))

        hold_frames = max(1, int(self.hold_seconds * self.assumed_fps))
        self.period_frames = max(2, int(self.coach_loop_seconds * self.assumed_fps))
        self.trackers = [StretchTracker(hold_frames, miss_tol) for _ in STRETCHES]

        if coach_poses is None:
            coach_poses = _load_default_coach_poses()
        self.coach = CoachAvatar(coach_poses)

        self.stage_idx = 0
        self.frame_index = 0
        self.cleared = False
        self.good_timer = 0
        self.feedback_frames = max(1, int(0.9 * self.assumed_fps))

    # -- main per-frame hook --------------------------------------------
    def visualize(self, image: np.ndarray, results: List[PoseResult]) -> np.ndarray:
        out = super().visualize(image, results)  # draws player skeleton
        self.frame_index += 1
        H, W = out.shape[:2]

        person = _largest_person(results)
        matched = False
        if not self.cleared and person is not None:
            kp = _pose_to_kp(person)
            stretch = STRETCHES[self.stage_idx]
            matched = bool(stretch["fn"](kp, self.rules_cfg))
            tracker = self.trackers[self.stage_idx]
            tracker.update(matched)
            if tracker.complete:
                self._advance_stage()

        if self.good_timer > 0:
            self.good_timer -= 1

        self._draw_header(out, W)
        self._draw_coach_panel(out, W, H)
        self._draw_hold_bar(out, W, H, person is not None)
        self._draw_feedback(out, W, H, matched)
        self._draw_footer_hint(out, W, H, person is not None)
        return out

    def _advance_stage(self):
        self.good_timer = self.feedback_frames
        self.stage_idx += 1
        if self.stage_idx >= len(STRETCHES):
            self.stage_idx = len(STRETCHES) - 1
            self.cleared = True

    # -- UI pieces ------------------------------------------------------
    def _draw_header(self, out, W):
        cv2.rectangle(out, (0, 0), (W, 46), _C_HEADER_BG, -1)
        cv2.line(out, (0, 46), (W, 46), _C_ACCENT, 2)
        done = len(STRETCHES) if self.cleared else self.stage_idx + 1
        stretch = STRETCHES[self.stage_idx]
        _text(out, f"STAGE {done}/{len(STRETCHES)}", (14, 34), 0.9, _C_ACCENT, 2)
        _text(out, stretch["name"], (210, 34), 0.9, _C_WHITE, 2)
        _text(out, "STRETCH ARCADE", (W - 290, 34), 0.7, _C_ACCENT, 2)

    def _draw_coach_panel(self, out, W, H):
        pw = int(min(0.26 * W, 300))
        ph = int(pw * 1.25)
        px, py = 14, 58
        _panel(out, px, py, pw, ph)
        _text(out, "COACH", (px + 10, py + 26), 0.6, _C_ACCENT, 1)
        fig_rect = (px, py + 30, pw, ph - 40)
        phase = triangle_phase(self.frame_index, self.period_frames)
        self.coach.render(out, fig_rect, STRETCHES[self.stage_idx]["key"], phase)
        # name + instruction below the panel
        stretch = STRETCHES[self.stage_idx]
        _text(out, stretch["name"], (px, py + ph + 26), 0.62, _C_ACCENT, 2)
        _wrap_text(out, stretch["instruction"], px, py + ph + 50, 0.5,
                   _C_WHITE, max_w=pw + 80)

    def _draw_hold_bar(self, out, W, H, has_person):
        if self.cleared:
            return
        progress = self.trackers[self.stage_idx].progress
        bw, bh = int(W * 0.5), 26
        bx, by = (W - bw) // 2, H - 54
        cv2.rectangle(out, (bx, by), (bx + bw, by + bh), _C_BAR_BG, -1)
        fill = int(bw * progress)
        if fill > 0:
            cv2.rectangle(out, (bx, by), (bx + fill, by + bh), _C_BAR_FG, -1)
        cv2.rectangle(out, (bx, by), (bx + bw, by + bh), _C_ACCENT, 2)
        _text(out, f"HOLD  {int(progress * 100)}%", (bx + 10, by + 21), 0.6, _C_WHITE, 1)

    def _draw_feedback(self, out, W, H, matched):
        if self.cleared:
            _big_center(out, "CLEAR!", W, H, _C_CLEAR)
            _text(out, "All stretches complete - great job!",
                  (W // 2 - 230, H // 2 + 50), 0.8, _C_WHITE, 2)
        elif self.good_timer > 0:
            _big_center(out, "GOOD!", W, H, _C_GOOD)

    def _draw_footer_hint(self, out, W, H, has_person):
        if self.cleared:
            return
        if not has_person:
            _text(out, "STEP INTO FRAME", (W // 2 - 150, H // 2), 0.9, _C_ACCENT, 2)


def _big_center(out, s, W, H, color):
    scale = 3.2
    (tw, th), _ = cv2.getTextSize(s, cv2.FONT_HERSHEY_DUPLEX, scale, 6)
    org = (W // 2 - tw // 2, H // 2)
    _text(out, s, org, scale, color, 6)


def _wrap_text(out, s, x, y, scale, color, max_w):
    words = s.split()
    line, yy = "", y
    for w in words:
        trial = (line + " " + w).strip()
        (tw, _), _ = cv2.getTextSize(trial, cv2.FONT_HERSHEY_DUPLEX, scale, 1)
        if tw > max_w and line:
            _text(out, line, (x, yy), scale, color, 1)
            line, yy = w, yy + int(26 * scale / 0.5)
        else:
            line = trial
    if line:
        _text(out, line, (x, yy), scale, color, 1)


def _load_default_coach_poses() -> dict:
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "coach_poses.json")) as f:
        return json.load(f)
