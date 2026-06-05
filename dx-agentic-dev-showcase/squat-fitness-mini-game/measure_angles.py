#!/usr/bin/env python3
"""Calibration / validation for the squat mini-game.

Runs the REAL NPU pipeline (identical components to the game) over an input
clip, reports the knee-angle distribution, and computes the rep count two
independent ways:

  1. the production ``SquatCounter`` hysteresis state machine, and
  2. a standalone valley detector (local minima that dip below ``down_angle``
     and recover above ``up_angle``).

Both must agree before the count is trusted. This exists because
``sample/squat_demo.mp4`` is an untracked file that is replaced between
sessions, so thresholds / target_reps must be re-derived from data every time.

Usage:
    python measure_angles.py -m <model.dxnn> --video sample/squat_demo.mp4
"""
import logging
import sys
from pathlib import Path
from statistics import median

import cv2

_session_dir = Path(__file__).resolve().parent
_walk = _session_dir
for _ in range(8):
    _cand = _walk / "src" / "python_example"
    if _cand.is_dir():
        if str(_cand) not in sys.path:
            sys.path.insert(0, str(_cand))
        break
    _walk = _walk.parent
if str(_session_dir) not in sys.path:
    sys.path.insert(0, str(_session_dir))

from common.runner import SyncRunner, parse_common_args  # noqa: E402
from common.config import load_config  # noqa: E402
from squat_game.squat_counter import SquatCounter  # noqa: E402
from factory import SquatGameFactory  # noqa: E402

logger = logging.getLogger(__name__)


def percentile(values, p):
    if not values:
        return float("nan")
    s = sorted(values)
    k = (len(s) - 1) * (p / 100.0)
    lo = int(k)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


def valley_rep_count(angles, down_angle, up_angle):
    """Independent counter: a rep = went below down_angle then back above up_angle."""
    reps = 0
    armed = False  # True once we have dipped below down_angle
    for a in angles:
        if a is None:
            continue
        if a < down_angle:
            armed = True
        elif a > up_angle and armed:
            reps += 1
            armed = False
    return reps


def main():
    args = parse_common_args("Squat angle calibration")
    if not args.video:
        logger.error("calibration requires --video <clip>")
        sys.exit(1)
    config_path = args.config or str(_session_dir / "config.json")

    cfg = load_config(config_path) or {}
    down_angle = float(cfg.get("down_angle", 140.0))
    up_angle = float(cfg.get("up_angle", 160.0))

    factory = SquatGameFactory(cfg)
    runner = SyncRunner(factory)
    runner._init_engine(args.model, config_path)
    viz = runner.visualizer  # SquatGameVisualizer (reuse its angle helpers)

    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        logger.error("cannot open %s", args.video)
        sys.exit(1)

    angles = []
    frames = 0
    frames_with_pose = 0
    counter = SquatCounter(down_angle=down_angle, up_angle=up_angle)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames += 1
        tensor, ctx = runner.preprocess(frame)
        outputs = runner.infer(tensor)
        results = runner.postprocess(outputs, ctx)
        pose = viz._largest_pose(results)
        knee = viz._knee_angle(pose.keypoints) if pose else None
        if knee is not None:
            frames_with_pose += 1
        angles.append(knee)
        counter.update(knee)
    cap.release()

    valid = [a for a in angles if a is not None]
    hyst_reps = counter.reps
    valley_reps = valley_rep_count(angles, down_angle, up_angle)

    bar = "=" * 60
    logger.info(bar)
    logger.info("SQUAT ANGLE CALIBRATION")
    logger.info(bar)
    logger.info("video                : %s", args.video)
    logger.info("frames               : %d", frames)
    logger.info("frames with pose     : %d", frames_with_pose)
    logger.info("thresholds           : down=%s  up=%s", down_angle, up_angle)
    if valid:
        logger.info("knee angle min       : %.1f deg", min(valid))
        logger.info("knee angle median    : %.1f deg", median(valid))
        logger.info("knee angle max       : %.1f deg", max(valid))
        logger.info("knee angle p10/p90   : %.1f / %.1f deg",
                    percentile(valid, 10), percentile(valid, 90))
    logger.info("-" * 60)
    logger.info("reps (hysteresis)    : %d", hyst_reps)
    logger.info("reps (valley detect) : %d", valley_reps)
    agree = hyst_reps == valley_reps
    logger.info("counters agree       : %s", agree)
    logger.info(bar)
    if not agree:
        logger.warning("counters disagree — review thresholds before trusting count.")
        sys.exit(2)
    logger.info("RESULT: PASS  (recommended target_reps = %d)", hyst_reps)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    main()
