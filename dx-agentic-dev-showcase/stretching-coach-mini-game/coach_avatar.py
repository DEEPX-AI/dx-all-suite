#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
Coach avatar — animated stick-figure demonstrator for the stretch game.

The coach is drawn from COCO-17 *pose templates* expressed in a canonical
figure space:
    - origin (0, 0) = mid-hip
    - +x = figure's right-on-screen, +y = DOWN (image convention)
    - unit length ~= one leg (hip -> ankle), so ankles sit near y = +1.0

Templates for the three target stretches are derived from the sample clips at
build time (see calibrate_templates.py -> pose_templates.json). Hand-authored
fallbacks live here so the avatar always renders even without calibration.
"""

import json
import os
from typing import Dict, Optional

import numpy as np
import cv2

# ---- COCO-17 keypoint indices ------------------------------------------------
NOSE = 0
L_EYE, R_EYE = 1, 2
L_EAR, R_EAR = 3, 4
L_SH, R_SH = 5, 6
L_EL, R_EL = 7, 8
L_WR, R_WR = 9, 10
L_HIP, R_HIP = 11, 12
L_KNEE, R_KNEE = 13, 14
L_ANKLE, R_ANKLE = 15, 16

# Limbs used for the clean stick figure (subset of COCO skeleton).
LIMBS = [
    (L_SH, R_SH),                     # shoulders
    (L_SH, L_HIP), (R_SH, R_HIP),     # torso sides
    (L_HIP, R_HIP),                   # hips
    (L_SH, L_EL), (L_EL, L_WR),       # left arm
    (R_SH, R_EL), (R_EL, R_WR),       # right arm
    (L_HIP, L_KNEE), (L_KNEE, L_ANKLE),   # left leg
    (R_HIP, R_KNEE), (R_KNEE, R_ANKLE),   # right leg
]

STAGE_KEYS = ("overhead", "fold", "neck")


def _tmpl(points: Dict[int, tuple]) -> np.ndarray:
    """Build a (17, 2) template from an index->(x, y) dict (missing -> 0)."""
    arr = np.zeros((17, 2), dtype=np.float32)
    for idx, (x, y) in points.items():
        arr[idx] = (x, y)
    return arr


# Neutral standing figure — arms relaxed at the sides.
NEUTRAL_TEMPLATE = _tmpl({
    NOSE: (0.00, -0.95),
    L_EYE: (-0.05, -1.00), R_EYE: (0.05, -1.00),
    L_EAR: (-0.09, -0.97), R_EAR: (0.09, -0.97),
    L_SH: (-0.20, -0.70), R_SH: (0.20, -0.70),
    L_EL: (-0.24, -0.40), R_EL: (0.24, -0.40),
    L_WR: (-0.26, -0.10), R_WR: (0.26, -0.10),
    L_HIP: (-0.12, 0.00), R_HIP: (0.12, 0.00),
    L_KNEE: (-0.12, 0.50), R_KNEE: (0.12, 0.50),
    L_ANKLE: (-0.12, 1.00), R_ANKLE: (0.12, 1.00),
})

# Stage 1 — both arms straight overhead.
_OVERHEAD = _tmpl({
    NOSE: (0.00, -0.95),
    L_EYE: (-0.05, -1.00), R_EYE: (0.05, -1.00),
    L_EAR: (-0.09, -0.97), R_EAR: (0.09, -0.97),
    L_SH: (-0.20, -0.70), R_SH: (0.20, -0.70),
    L_EL: (-0.22, -1.05), R_EL: (0.22, -1.05),
    L_WR: (-0.15, -1.45), R_WR: (0.15, -1.45),
    L_HIP: (-0.12, 0.00), R_HIP: (0.12, 0.00),
    L_KNEE: (-0.12, 0.50), R_KNEE: (0.12, 0.50),
    L_ANKLE: (-0.12, 1.00), R_ANKLE: (0.12, 1.00),
})

# Stage 2 — forward fold: torso dropped toward hips, hands reaching down.
_FOLD = _tmpl({
    NOSE: (0.00, 0.05),
    L_EYE: (-0.05, 0.00), R_EYE: (0.05, 0.00),
    L_EAR: (-0.09, -0.05), R_EAR: (0.09, -0.05),
    L_SH: (-0.18, -0.15), R_SH: (0.18, -0.15),
    L_EL: (-0.20, 0.25), R_EL: (0.20, 0.25),
    L_WR: (-0.15, 0.75), R_WR: (0.15, 0.75),
    L_HIP: (-0.12, 0.00), R_HIP: (0.12, 0.00),
    L_KNEE: (-0.12, 0.50), R_KNEE: (0.12, 0.50),
    L_ANKLE: (-0.12, 1.00), R_ANKLE: (0.12, 1.00),
})

# Stage 3 — neck stretch: right hand raised beside the head, left arm relaxed.
_NECK = _tmpl({
    NOSE: (-0.04, -0.95),
    L_EYE: (-0.09, -1.00), R_EYE: (0.01, -1.00),
    L_EAR: (-0.12, -0.97), R_EAR: (0.05, -0.97),
    L_SH: (-0.20, -0.70), R_SH: (0.20, -0.70),
    L_EL: (-0.24, -0.40), R_EL: (0.34, -1.02),
    L_WR: (-0.26, -0.10), R_WR: (0.06, -1.18),
    L_HIP: (-0.12, 0.00), R_HIP: (0.12, 0.00),
    L_KNEE: (-0.12, 0.50), R_KNEE: (0.12, 0.50),
    L_ANKLE: (-0.12, 1.00), R_ANKLE: (0.12, 1.00),
})

FALLBACK_TEMPLATES: Dict[str, np.ndarray] = {
    "overhead": _OVERHEAD,
    "fold": _FOLD,
    "neck": _NECK,
}


def load_templates(path: Optional[str]) -> Dict[str, np.ndarray]:
    """Load baked templates, layering them over the hand-authored fallbacks.

    Never raises: a missing/corrupt file simply yields the fallbacks, so the
    avatar always has something to draw.
    """
    templates = {k: v.copy() for k, v in FALLBACK_TEMPLATES.items()}
    templates["neutral"] = NEUTRAL_TEMPLATE.copy()
    if not path or not os.path.isfile(path):
        return templates
    try:
        with open(path) as f:
            data = json.load(f)
        for key, pts in data.items():
            arr = np.asarray(pts, dtype=np.float32)
            if arr.shape == (17, 2):
                templates[key] = arr
    except (OSError, ValueError, TypeError):
        pass
    return templates


def _smoothstep(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def lerp_pose(a: np.ndarray, b: np.ndarray, t: float) -> np.ndarray:
    """Eased interpolation between two (17, 2) templates."""
    s = _smoothstep(t)
    return a * (1.0 - s) + b * s


def _to_px(template: np.ndarray, origin_px, scale_px: float) -> np.ndarray:
    out = np.empty_like(template)
    out[:, 0] = origin_px[0] + template[:, 0] * scale_px
    out[:, 1] = origin_px[1] + template[:, 1] * scale_px
    return out


def draw_figure(canvas: np.ndarray, template: np.ndarray, origin_px,
                scale_px: float, color=(0, 235, 255),
                thickness: int = 3) -> None:
    """Draw a clean stick figure (limbs + head circle) for a template."""
    pts = _to_px(template, origin_px, scale_px)

    # Head: circle centered between nose and mid-shoulder.
    mid_sh = (pts[L_SH] + pts[R_SH]) * 0.5
    head_c = (pts[NOSE] * 0.6 + mid_sh * 0.4)
    head_r = max(6, int(scale_px * 0.16))
    cv2.circle(canvas, (int(head_c[0]), int(head_c[1])), head_r, color, thickness, cv2.LINE_AA)
    # Neck: mid-shoulder -> head.
    cv2.line(canvas, (int(mid_sh[0]), int(mid_sh[1])),
             (int(head_c[0]), int(head_c[1] + head_r)), color, thickness, cv2.LINE_AA)

    for a, b in LIMBS:
        pa = (int(pts[a][0]), int(pts[a][1]))
        pb = (int(pts[b][0]), int(pts[b][1]))
        cv2.line(canvas, pa, pb, color, thickness, cv2.LINE_AA)
    # Joint dots.
    for i in (L_SH, R_SH, L_EL, R_EL, L_WR, R_WR, L_HIP, R_HIP,
              L_KNEE, R_KNEE, L_ANKLE, R_ANKLE):
        cv2.circle(canvas, (int(pts[i][0]), int(pts[i][1])), max(2, thickness),
                   color, -1, cv2.LINE_AA)


def _wrap_text(text: str, max_chars: int):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= max_chars:
            cur = (cur + " " + w).strip()
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def render_coach_panel(panel_w: int, panel_h: int,
                       template_neutral: np.ndarray,
                       template_target: np.ndarray,
                       phase: float, name: str, instruction: str,
                       accent=(0, 235, 255)) -> np.ndarray:
    """Render the top-left coach panel: title, animated figure, instruction."""
    panel = np.full((panel_h, panel_w, 3), 28, dtype=np.uint8)
    # Border + header bar.
    cv2.rectangle(panel, (0, 0), (panel_w - 1, panel_h - 1), accent, 2)
    cv2.rectangle(panel, (0, 0), (panel_w - 1, 30), accent, -1)
    cv2.putText(panel, "COACH", (10, 21), cv2.FONT_HERSHEY_DUPLEX, 0.6,
                (20, 20, 20), 1, cv2.LINE_AA)

    # Animated figure (neutral <-> target by phase).
    pose = lerp_pose(template_neutral, template_target, phase)
    scale_px = panel_h * 0.26
    origin_px = (panel_w * 0.5, panel_h * 0.62)
    draw_figure(panel, pose, origin_px, scale_px, accent, 3)

    # Stretch name.
    cv2.putText(panel, name, (10, panel_h - 52), cv2.FONT_HERSHEY_DUPLEX,
                0.6, (255, 255, 255), 1, cv2.LINE_AA)
    # Instruction (wrapped, small).
    max_chars = max(8, int(panel_w / 9))
    for i, line in enumerate(_wrap_text(instruction, max_chars)[:2]):
        cv2.putText(panel, line, (10, panel_h - 32 + i * 16),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (180, 220, 255), 1, cv2.LINE_AA)
    return panel


if __name__ == "__main__":
    # Smoke test: render each stage panel to a PNG montage.
    tmpls = load_templates(None)
    panels = []
    names = {"overhead": "REACH FOR THE SKY", "fold": "TOUCH YOUR TOES",
             "neck": "NECK RELEASE"}
    instr = {"overhead": "Extend both arms straight overhead",
             "fold": "Bend forward, reach down to your feet",
             "neck": "Pull your head to one side with one hand"}
    for k in STAGE_KEYS:
        panels.append(render_coach_panel(240, 320, tmpls["neutral"], tmpls[k],
                                         0.85, names[k], instr[k]))
    montage = np.hstack(panels)
    out = os.path.join(os.path.dirname(__file__), "coach_preview.png")
    cv2.imwrite(out, montage)
    print(f"PASS: wrote coach preview -> {out} shape={montage.shape}")
