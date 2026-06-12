#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""Arcade stretch-game visualizer.

A PoseVisualizer subclass created once by the factory, so it persists across
frames (SyncRunner reuses the same instance). Each frame it:
  * draws the player's skeleton (base class),
  * runs the current stage's recognizer on the largest detected person,
  * advances the StretchGame hold/stage state machine,
  * overlays the arcade UI: STAGE n/3, an animated coach avatar demonstrating the
    target pose, the stretch name + instruction, a HOLD progress ring, and
    GOOD! / CLEAR! feedback.
"""

from typing import List

import cv2
import numpy as np

from common.visualizers import PoseVisualizer

import pose_logic as pl
from coach import CoachAvatar

_FONT = cv2.FONT_HERSHEY_DUPLEX
_PANEL_BG = (35, 28, 20)
_ACCENT = (60, 220, 255)     # amber
_GREEN = (90, 240, 120)
_WHITE = (245, 245, 245)
_GREY = (180, 180, 180)
_RED = (80, 90, 240)


def _alpha_rect(img, x, y, w, h, color, alpha):
    x2, y2 = min(img.shape[1], x + w), min(img.shape[0], y + h)
    x, y = max(0, x), max(0, y)
    if x2 <= x or y2 <= y:
        return
    roi = img[y:y2, x:x2]
    overlay = np.full_like(roi, color, dtype=np.uint8)
    cv2.addWeighted(overlay, alpha, roi, 1 - alpha, 0, roi)


def _text(img, s, org, scale, color, thick=1, font=_FONT):
    cv2.putText(img, s, org, font, scale, color, thick, cv2.LINE_AA)


def _text_centered(img, s, cx, y, scale, color, thick=2, font=_FONT):
    (tw, th), _ = cv2.getTextSize(s, font, scale, thick)
    cv2.putText(img, s, (int(cx - tw / 2), int(y)), font, scale, color, thick, cv2.LINE_AA)


class StretchGameVisualizer(PoseVisualizer):
    def __init__(self, config: dict = None, templates: dict = None):
        super().__init__(draw_box=False, keypoint_radius=4, skeleton_thickness=2)
        cfg = (config or {}).get("game", {}) if config else {}
        self.cfg = {**pl.DEFAULT_CFG, **{k: cfg[k] for k in pl.DEFAULT_CFG if k in cfg}}
        self.assumed_fps = float(cfg.get("assumed_fps", 24.0))
        hold_seconds = float(cfg.get("hold_seconds", 1.5))
        grace = int(cfg.get("grace_frames", 8))
        hold_frames = max(1, round(hold_seconds * self.assumed_fps))
        self.game = pl.StretchGame(pl.STAGE_DEFS, hold_frames=hold_frames, grace=grace)
        self.coach = CoachAvatar(templates or {})
        self.frame_idx = 0
        self._cycle = max(1, round(2.6 * self.assumed_fps))

    # -- game step -------------------------------------------------------
    def _match_current(self, results: List) -> bool:
        stage = self.game.current_stage
        if stage is None or not results:
            return False
        pose = max(results, key=lambda p: (
            (p.box[2] - p.box[0]) * (p.box[3] - p.box[1]) if p.box and len(p.box) >= 4 else 0))
        P = pl.extract_keypoints(pose, self.cfg["kpt_conf"])
        scale = pl.leg_scale(P)
        return pl.detect_stage(stage["key"], P, scale, self.cfg)

    # -- main entry ------------------------------------------------------
    def visualize(self, image: np.ndarray, results: List) -> np.ndarray:
        output = super().visualize(image, results)
        matched = self._match_current(results)
        self.game.update(matched)
        self._draw_overlay(output, matched)
        self.frame_idx += 1
        return output

    # -- UI --------------------------------------------------------------
    def _draw_overlay(self, img, matched: bool) -> None:
        H, W = img.shape[:2]
        g = self.game

        # Top banner
        _alpha_rect(img, 0, 0, W, 46, (20, 16, 12), 0.55)
        _text(img, "STRETCH ARCADE", (16, 32), 0.9, _ACCENT, 2)
        stage_txt = "COMPLETE" if g.cleared else f"STAGE {g.stage_number}/{g.total_stages}"
        (tw, _), _ = cv2.getTextSize(stage_txt, _FONT, 0.9, 2)
        _text(img, stage_txt, (W - tw - 16, 32), 0.9, _GREEN if g.cleared else _WHITE, 2)

        # Coach panel (top-left)
        px, py = 14, 56
        pw, ph = min(330, int(W * 0.30)), min(360, int(H * 0.55))
        _alpha_rect(img, px, py, pw, ph, _PANEL_BG, 0.62)
        cv2.rectangle(img, (px, py), (px + pw, py + ph), _ACCENT, 2, cv2.LINE_AA)
        _text(img, "COACH", (px + 12, py + 26), 0.6, _ACCENT, 1)

        stage = g.current_stage
        stage_key = stage["key"] if stage else "neutral"
        fig_rect = (px + 8, py + 34, pw - 16, int(ph * 0.60))
        phase = (self.frame_idx % self._cycle) / self._cycle
        self.coach.draw(img, stage_key, fig_rect, phase)

        # Name + instruction
        ty = py + 34 + int(ph * 0.60) + 22
        name = stage["name"] if stage else "ALL STRETCHES DONE"
        instr = stage["instruction"] if stage else "Great work!"
        _text(img, name, (px + 12, ty), 0.62, _GREEN, 1)
        self._wrap_text(img, instr, px + 12, ty + 24, pw - 24, 0.46, _GREY)

        # HOLD progress bar (bottom of panel)
        by = py + ph - 30
        bw = pw - 24
        cv2.rectangle(img, (px + 12, by), (px + 12 + bw, by + 16), (70, 70, 70), -1)
        if stage is not None:
            fillw = int(bw * g.hold_progress)
            col = _GREEN if matched else _ACCENT
            if fillw > 0:
                cv2.rectangle(img, (px + 12, by), (px + 12 + fillw, by + 16), col, -1)
            _text(img, f"HOLD {int(g.hold_progress * 100):3d}%", (px + 12, by - 6), 0.5, _WHITE, 1)

        # Feedback flashes
        if g.good_flash > 0 and not g.cleared:
            _text_centered(img, "GOOD!", W / 2, H * 0.42, 2.4, _GREEN, 5)
        if g.cleared and g.clear_flash > 0:
            _text_centered(img, "CLEAR!", W / 2, H * 0.46, 3.0, _ACCENT, 6)
            _text_centered(img, "All 3 stretches complete", W / 2, H * 0.54, 0.9, _WHITE, 2)
        elif g.cleared:
            _text_centered(img, "CLEAR!", W / 2, 90, 1.4, _GREEN, 3)

    @staticmethod
    def _wrap_text(img, text, x, y, max_w, scale, color):
        words = text.split()
        line = ""
        ln = 0
        for w in words:
            trial = (line + " " + w).strip()
            (tw, th), _ = cv2.getTextSize(trial, _FONT, scale, 1)
            if tw > max_w and line:
                _text(img, line, (x, y + ln * 20), scale, color, 1)
                line = w
                ln += 1
            else:
                line = trial
        if line:
            _text(img, line, (x, y + ln * 20), scale, color, 1)
