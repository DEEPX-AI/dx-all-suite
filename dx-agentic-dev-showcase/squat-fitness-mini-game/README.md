# Squat Fitness Mini-Game — built by dx-agentic-dev

> **This whole app was generated end-to-end by [dx-agentic-dev](../../docs/source/agentic_development.md)
> from a single natural-language prompt** — no hand-written code. It runs the
> **yolo26n-pose** model on the **DEEPX NPU**, counts squat reps from body
> keypoints, and overlays an arcade-style **SQUAT CHALLENGE** game HUD.

<div align="center">
<table>
<tr>
<td align="center"><img src="../../docs/source/img/dx-agentic-dev-squat-build.gif" width="470"><br><sub><b>dx-agentic-dev building this app (timelapse)</b></sub></td>
<td align="center"><img src="../../docs/source/img/dx-agentic-dev-squat-gameplay.gif" width="188"><br><sub><b>The generated app running on the DX-M1 NPU</b></sub></td>
</tr>
</table>
</div>

The agent detects body keypoints, recognizes the squat down→up motion from
knee/hip angles, counts reps in real time, and overlays a game HUD (rep counter,
target, score, DOWN / UP / GOOD! / WIN! feedback, depth gauge). On a video file
it saves an annotated output video for review; it also runs on a live camera.

## See how the agent built it (session transcript)

This directory ships the **full Claude Code session** that produced the app, so
you can see exactly how the agent followed the harness instructions, used the
project skills/agents, and reasoned through brainstorm → plan → TDD → verify:

- **[`claude-code-session.md`](./claude-code-session.md)** — renders directly on GitHub *(recommended)*
- **`claude-code-session.html`** — same content; **open locally in a browser** for a richer view

See the [Agentic Development guide](../../docs/source/agentic_development.md) for
what to look for in the transcript.

## Prerequisites

- **dx-runtime built** with a working `dx_engine` venv at `dx-runtime/venv-dx-runtime`
  (see the suite setup). `setup.sh` verifies this and the NPU sanity check.
- **Model**: `yolo26n-pose.dxnn` (a large binary, not committed). Download it once:
  ```bash
  (cd ../../dx-runtime/dx_app && ./setup.sh --models yolo26n-pose)
  ```
  `run.sh` checks for it and prints this hint if it is missing.
- **Sample video**: `sample/squat_demo.mp4` is bundled here, so the video demo is
  self-contained.

## Quick start

```bash
# 1. one-time environment setup (reuses dx-runtime/venv-dx-runtime)
./setup.sh

# 2a. run on the bundled sample video -> saves annotated output.mp4 (headless)
./run.sh

# 2b. run on a live camera (needs a display)
./run.sh --camera 0

# 2c. custom video, saving annotated output
./run.sh --video /path/to/clip.mp4 --save
```

The annotated video is written under `artifacts/<run-dir>/output.mp4`.

### Run the app directly

```bash
source ../../dx-runtime/venv-dx-runtime/bin/activate
MODEL=../../dx-runtime/dx_app/assets/models/yolo26n-pose.dxnn

# video file (annotated output saved) — uses the bundled sample
python yolo26n_pose_squat_sync.py -m $MODEL --video sample/squat_demo.mp4 --save --no-display

# live camera
python yolo26n_pose_squat_sync.py -m $MODEL --camera 0
```

## Architecture (skeleton-first, IFactory + SyncRunner)

Built by copying the stock `src/python_example/pose_estimation/yolo26n_pose/`
skeleton and customizing only the game-specific parts:

| Component | Source |
|-----------|--------|
| Preprocessor | `LetterboxPreprocessor` (framework, unchanged) |
| Postprocessor | `YOLOv8PosePostprocessor` (framework, unchanged) |
| **Visualizer** | `SquatGameVisualizer` — **custom**: rep state machine + arcade HUD |
| Factory | `SquatGameFactory(IPoseFactory)` |
| Runner | `SyncRunner` (framework) |

The game state lives in `SquatGameVisualizer`, which `SyncRunner` instantiates
once and calls per frame — so the rep count and score persist across the stream.
Input source (`--video` / `--camera`) and annotated-video saving (`--save`) come
from the framework's `parse_common_args()` + `SyncRunner`; no custom I/O.

## Squat detection

- **Knee angle** = `angle(hip, knee, ankle)`; left = COCO (11,13,15), right = (12,14,16),
  averaged over whichever side has confident keypoints.
- **Hip angle** = `angle(shoulder, hip, knee)` — informs the depth gauge.
- **Hysteresis state machine** (`SquatCounter`): `UP → DOWN` when knee angle
  `< down_angle`; `DOWN → UP` (rep++) when knee angle `> up_angle`. The
  `down_angle < up_angle` dead-band rejects jitter.
- **Calibration**: 2D YOLO-pose knee angles bottom out near **120–140°** (not the
  textbook 90°) due to camera projection. Defaults `down_angle=140`, `up_angle=160`.
  `target_reps` is set from a **data-driven measurement** of the demo clip
  (`measure_angles.py`), cross-checked between the hysteresis counter and an
  independent valley detector.

## Configuration (`config.json`)

| Key | Default | Meaning |
|-----|---------|---------|
| `down_angle` | 140.0 | knee angle below which the player is "DOWN" |
| `up_angle` | 160.0 | knee angle above which a rep completes |
| `target_reps` | 2 | reps to win (= measured completed reps in `sample/squat_demo.mp4`; raise for live play) |
| `points_per_rep` | 10 | score awarded per completed rep |
| `keypoint_confidence` | 0.3 | min keypoint confidence to use a joint |
| `score_threshold` / `nms_threshold` | 0.4 / 0.45 | pose detection thresholds |

## Files

```
yolo26n_pose_squat_sync.py     entry wrapper (SyncRunner + SquatGameFactory)
factory/squat_game_factory.py  IFactory (5 methods)
factory/__init__.py
squat_game/squat_counter.py    pure-Python angle math + hysteresis counter
squat_game/game_visualizer.py  SquatGameVisualizer (rep logic + arcade HUD)
squat_game/__init__.py
config.json                    thresholds, target, scoring
measure_angles.py              NPU calibration / rep cross-check
tests/test_squat_counter.py    unit tests (10) for the rep core
conftest.py                    pytest path setup
setup.sh / run.sh              environment + launcher
sample/squat_demo.mp4          bundled demo input
session.log                    real validation output
claude-code-session.md / .html the full agent session that built this app
```

## Validation

- **Unit tests**: `python -m pytest tests/ -v` → 10 passed (angle math + state machine).
- **Calibration** (`measure_angles.py` on the demo clip): 240 frames, 238 with pose,
  knee min 132.1° / median 166.3°; hysteresis count = valley count = **2 reps** (agree).
- **End-to-end**: ran on `sample/squat_demo.mp4`, ~53 FPS overall (13 ms NPU
  inference/frame), annotated `output.mp4` written, HUD reaches **REPS 2/2,
  SCORE 20, WIN!** See `session.log`.
