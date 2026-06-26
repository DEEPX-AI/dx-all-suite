# Squat Fitness Mini-Game — built by dx-agent-dev

> **Generated end-to-end by [dx-agent-dev](../../docs/source/00_Agent_Driven_Development.md)
> from a single natural-language prompt** — no hand-written code. The folder is
> **self-contained & portable**: it vendors the framework into `./common`, so it runs
> even when copied outside dx-all-suite (any machine with the DEEPX runtime).

<div align="center">
<table>
<tr>
<td align="center"><img src="../../docs/source/img/dx-agent-dev-squat-build.gif" width="470"><br><sub><b>dx-agent-dev building this app (timelapse)</b></sub></td>
<td align="center"><img src="../../docs/source/img/dx-agent-dev-squat-gameplay.gif" width="188"><br><sub><b>The generated app running on the DX-M1 NPU</b></sub></td>
</tr>
</table>
</div>

> **See how the agent built it:** [`claude-code-session.md`](./claude-code-session.md)
> (renders on GitHub; `claude-code-session.html` opens in a local browser).

### How this app was built — session metrics

Extracted from the build session transcript (`claude-code-session.*`):

| Metric | Value |
|--------|-------|
| Coding agent | **Claude Code** (`claude` CLI, headless `-p`) |
| Model | **Claude Opus 4.8** (`claude-opus-4-8`) |
| Human input | **1 natural-language prompt** — fully autonomous, no hand-written code |
| Build wall-clock | **≈ 11.5 min** |
| Agent turns | **132** |
| Tools used | `Bash` ×25, `Read` ×14, `Write` ×13, `Skill` ×5, `Edit` ×2 |
| Skills invoked (in order) | `dx-skill-router` → `dx-agent-brainstorm` → `dx-swe-writing-plans` → `dx-agent-tdd` → `dx-agent-verify` |
| Output tokens | **≈ 109K** |
| Approx. cost | **≈ $7.3** |

The full brainstorm → plan → TDD → verify skill sequence ran end-to-end before the
app was declared done — the transcript shows each step as a real tool call.

An arcade-style squat counter. Runs **yolo26n-pose** on the DEEPX NPU, detects
squat repetitions from body keypoints (knee + hip angles), counts reps in real
time, and overlays a game HUD (rep counter, depth bar, **GOOD REP** banner).
Works on a **video file** or a **live camera**. On a video file it saves an
**annotated output video**.

## The prompt

> The exact natural-language prompt given to the agent (verbatim):

```
Build a squat-counting fitness mini-game using yolo26n-pose on DEEPX NPU, validate with dx-agent-dev-showcase/mini-game-squat-fitness/sample/squat_demo.mp4
```

> **Run this prompt from the dx-all-suite root** — the sample video path is relative to the suite root, which is where DEEPX Agent-Driven Development routing starts.

## Quick start

```bash
./setup.sh                          # vendor framework into ./common, bridge dx_engine, install deps
./run.sh                            # headless validation on the bundled demo video (saves annotated output)
DISPLAY_MODE=1 ./run.sh             # live on-screen window
VIDEO=/path/to/clip.mp4 ./run.sh    # use a different video
DXNN_MODEL=/path/to/yolo26n-pose.dxnn ./run.sh   # point at an explicit model
```

`run.sh` resolves the model automatically: it prefers a bundled
`./yolo26n-pose.dxnn`, then falls back to
`$SUITE_ROOT/dx-runtime/dx_app/assets/models/` (including `models-*/`). The input
defaults to the bundled `sample/squat_demo.mp4`.

Direct invocation (equivalent):

```bash
python yolo26n_pose_squat_sync.py --model yolo26n-pose.dxnn --video sample/squat_demo.mp4 --no-display --save
python yolo26n_pose_squat_sync.py --model yolo26n-pose.dxnn --camera 0 --display
```

## Runtime options (run.sh)

| Variable | Meaning |
|----------|---------|
| `DISPLAY_MODE=1` | Live on-screen window (default is headless + save annotated video) |
| `VIDEO=<file>` | Use a specific video file as input (default: `sample/squat_demo.mp4`) |
| `DXNN_MODEL=<path>` | Use a specific `.dxnn` model (default: auto-resolved) |

Press **q** or **ESC** in the display window to quit.

## How squat detection works

- **Knee angle** = interior angle at the knee between hip→knee and ankle→knee
  (COCO-17 indices: hip 11/12, knee 13/14, ankle 15/16). Left + right are
  averaged when both legs are visible (`min_visible_legs` configurable).
- A two-state hysteresis FSM (`SquatCounter`) counts one rep per full DOWN→UP
  cycle, gated by `squat_angle` (down) and `stand_angle` (up). Defaults
  (`squat_angle=140`, `stand_angle=160`) are tuned to the sample clip's
  front-facing camera, where the 2D-projected knee angle reads ~126–179° rather
  than the textbook 90°. Adjust the thresholds in `config.json` for steeper
  side-view setups.

## Architecture (IFactory + SyncRunner, skeleton-first)

| Component | Implementation |
|-----------|----------------|
| Preprocessor | `LetterboxPreprocessor` (framework) |
| Postprocessor | `YOLOv8PosePostprocessor` (framework) → `PoseResult` w/ COCO-17 |
| Visualizer | **`SquatGameVisualizer`** — stateful rep FSM + arcade HUD |
| Factory | **`SquatGameFactory`** (`IPoseFactory`, 5 methods + `get_num_keypoints`) |
| Runner | `SyncRunner` (single model, frame-ordered) |

Game logic lives entirely inside the visualizer's `visualize(frame, results)`
hook — no direct `InferenceEngine` calls, fully within the framework pattern.
The pure geometry + FSM (`compute_angle`, `SquatCounter`) is isolated in
`squat_logic.py` so it is unit-testable without hardware.

## Files

| File | Purpose |
|------|---------|
| `yolo26n_pose_squat_sync.py` | Entry — builds factory, runs `SyncRunner` |
| `factory/squat_game_factory.py` | `SquatGameFactory` (IFactory) |
| `factory/squat_game_visualizer.py` | `SquatGameVisualizer` (game hook + HUD) |
| `factory/squat_logic.py` | Pure `compute_angle` + `SquatCounter` FSM |
| `factory/__init__.py` | Factory export |
| `config.json` | Detection + `squat_game` thresholds (target reps, angles) |
| `test_squat_logic.py` | Unit tests for angle math + FSM (10 tests) |
| `setup.sh` / `run.sh` | Self-contained setup + relocatable launcher |
| `session.json` / `session.log` | Session metadata + command log |

## Self-contained / portable

`setup.sh` vendors the shared framework into `./common` and bridges `dx_engine`
from the dx-runtime venv; the entry walker prefers that vendored `./common` (no
`PYTHONPATH`). With the sample bundled and the model auto-resolved, the folder
runs even when copied outside dx-all-suite — `dx_engine` (DEEPX runtime) is the
one external prerequisite.
</content>
</invoke>
