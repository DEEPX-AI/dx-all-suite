# Squat Fitness Mini-Game — built by dx-agentic-dev

> **This whole app was generated end-to-end by [dx-agentic-dev](../../docs/source/agentic_development.md)
> from a single natural-language prompt** — no hand-written code. It runs
> `yolo26n-pose` on the **DEEPX NPU**, counts squat reps from body keypoints, and
> overlays an arcade-style game HUD.

<div align="center">
<table>
<tr>
<td align="center"><img src="../../docs/source/img/dx-agentic-dev-squat-build.gif" width="470"><br><sub><b>dx-agentic-dev building this app (timelapse)</b></sub></td>
<td align="center"><img src="../../docs/source/img/dx-agentic-dev-squat-gameplay.gif" width="188"><br><sub><b>The generated app running on the DX-M1 NPU</b></sub></td>
</tr>
</table>
</div>

Real-time **squat rep counter** running on the DEEPX DX-M1 NPU with the
`yolo26n-pose` model. Detects squats from body keypoints (knee + hip angles),
counts reps live, and overlays an arcade-style game HUD on every frame.

## See how the agent built it (session transcript)

The **full Claude Code session** that produced this app is included, so you can see
how it followed the harness instructions, used the project skills/agents, and reasoned
through brainstorm → plan → TDD → verify:

- **[`claude-code-session.md`](./claude-code-session.md)** — renders on GitHub *(recommended)*
- **`claude-code-session.html`** — same content; open locally in a browser for a richer view

```
 ┌─────────────────────────────────────────────┐
 │ SQUAT ARCADE        REPS 02/10   SCORE 0020  │   ← translucent HUD panel
 │ ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  bar │   ← progress to target
 │ knee 134.0deg                                │
 │                                              │
 │                 (skeleton overlay)           │
 │                    DOWN / UP                 │   ← big feedback text
 │                  GOOD!  /  GOAL!             │
 └─────────────────────────────────────────────┘
```

## Quick start

```bash
# 0. one-time sanity check (venv / dx_engine / OpenCV / model)
./setup.sh

# 1. run on the bundled demo clip — saves an annotated output video
./run.sh
#    -> output video: ./output/.../output.mp4

# 2. run on a custom video (also saves annotated output)
./run.sh --video /path/to/clip.mp4

# 3. run on a live camera
./run.sh --camera 0

# stop the window any time with 'q' or ESC
```

`run.sh` is **relocatable**: it auto-detects the dx_app root, falls back across
venvs (local `venv`/`.venv` → `dx-runtime/venv-dx-runtime`), guards against a
missing model with a download hint, and prefers a bundled `sample/` clip.

## How it works (framework-compliant)

Built strictly on the dx_app **IFactory + SyncRunner** pattern — no standalone
inference loops, no direct engine calls.

| Stage | Component | Notes |
|-------|-----------|-------|
| preprocess | `LetterboxPreprocessor` | framework default, unchanged |
| infer | `dx_engine.InferenceEngine` | yolo26n-pose on NPU (driven by SyncRunner) |
| postprocess | `YOLOv8PosePostprocessor` | → `PoseResult` (COCO-17 keypoints) |
| **game + draw** | **`SquatGameVisualizer`** | rep state machine + arcade HUD, called per frame |

The squat logic is split into two pieces:

* **`squat_rep_counter.py`** — pure, dependency-free `SquatRepCounter` state
  machine (`UP`↔`DOWN`) with sliding-window smoothing, hysteresis, and a
  consecutive-frame debounce. Fully unit-tested.
* **`squat_game_visualizer.py`** — extracts knee angle = ∠(hip, knee, ankle) and
  hip angle = ∠(shoulder, hip, knee) from COCO keypoints (averaged L/R by
  confidence), drives the counter, and renders the HUD on the skeleton frame.

### Rep detection & calibration

A squat is one full `UP → DOWN → UP` knee cycle. Thresholds were **calibrated
from `sample/squat_demo.mp4`** (`calibrate_squat.py`), not guessed — in a 2D
view the knee angle bottoms out around **133°**, never 90°:

| param | value | meaning |
|-------|-------|---------|
| `knee_down_angle` | 148° | enter DOWN when smoothed knee ≤ this |
| `knee_up_angle` | 160° | DOWN→UP (rep counted) when smoothed knee ≥ this |
| `smoothing_window` | 5 | sliding-mean frames |
| `min_state_frames` | 3 | debounce: frames a transition must persist |

On the demo clip these detect **2 reps** (two complete squats; a third
incomplete dip at clip-end is correctly not counted).

Re-calibrate for a new clip:
```bash
python calibrate_squat.py --model ../../assets/models/yolo26n-pose.dxnn --video <clip.mp4>
```

## Game tuning (`config.json`)

```json
{
  "game": {
    "target_reps": 10, "score_per_rep": 10,
    "knee_down_angle": 148.0, "knee_up_angle": 160.0,
    "smoothing_window": 5, "min_state_frames": 3,
    "keypoint_confidence_threshold": 0.3
  }
}
```

## Files

| File | Purpose |
|------|---------|
| `yolo26n_pose_squat_sync.py` | App entrypoint (IFactory + SyncRunner) |
| `factory/yolo26n_pose_squat_factory.py` | `Yolo26nPoseSquatFactory` (5 IFactory methods) |
| `squat_game_visualizer.py` | Arcade HUD + per-frame game logic |
| `squat_rep_counter.py` | Pure rep state machine |
| `test_squat_rep_counter.py` | Unit tests (pytest or standalone) |
| `calibrate_squat.py` | Knee-angle threshold calibration tool |
| `config.json` | Model + game configuration |
| `setup.sh` / `run.sh` | Environment check / launcher |
| `session.json` / `session.log` | Build metadata / run log |

## Requirements

DEEPX DX-M1 NPU + dx-runtime (`dx_engine`), Python 3.12, GUI-capable
`opencv-python` (display is auto-skipped on headless hosts; `--save` still works).
