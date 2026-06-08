# Squat Fitness Mini-Game — built by dx-agentic-dev

> **Generated end-to-end by [dx-agentic-dev](../../docs/source/agentic_development.md)
> from a single natural-language prompt** — no hand-written code. The folder is
> **self-contained & portable**: it vendors the framework into `./common`, so it runs
> even when copied outside dx-all-suite (any machine with the DEEPX runtime).

<div align="center">
<table>
<tr>
<td align="center"><img src="../../docs/source/img/dx-agentic-dev-squat-build.gif" width="470"><br><sub><b>dx-agentic-dev building this app (timelapse)</b></sub></td>
<td align="center"><img src="../../docs/source/img/dx-agentic-dev-squat-gameplay.gif" width="188"><br><sub><b>The generated app running on the DX-M1 NPU</b></sub></td>
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
| Build wall-clock | **≈ 20 min** (1,188,799 ms) |
| Agent turns | **81** |
| Clarifying questions | 1 (`AskUserQuestion`, auto-resolved from the knowledge base) |
| Tools used | `Bash` ×33, `Write` ×17, `Read` ×15, `Skill` ×5, `Edit` ×3, `TaskCreate` ×1, `AskUserQuestion` ×1 |
| Skills invoked (in order) | `dx-skill-router` → `dx-agentic-brainstorm` → `dx-swe-writing-plans` → `dx-agentic-tdd` → `dx-agentic-verify` |
| Output tokens | **≈ 85.3K** (input 7.9K; cached-context reads ≈ 12.5M) |
| Approx. cost | **≈ $9.9** |

The full brainstorm → plan → TDD → verify skill sequence ran end-to-end before the
app was declared done — the transcript shows each step as a real tool call.

An arcade-style squat counter. Runs **yolo26n-pose** on the DEEPX NPU, detects
squat repetitions from body keypoints (knee + hip angles), counts reps in real
time, and overlays a game HUD (rep counter, target, score, **DOWN / UP / GOOD!**
feedback, progress bar). Works on a **video file** or a **live camera**,
selectable at runtime. On a video file it saves an **annotated output video**.

## Quick start

```bash
./setup.sh                 # vendor framework into ./common, bundle model + sample
./run.sh                   # play on the bundled demo video (saves annotated output.mp4)
./run.sh --camera 0        # live camera
./run.sh --video my.mp4 --save
./run.sh --target-reps 15 --camera 0
```

Direct invocation (equivalent):

```bash
python yolo26n_pose_squat_sync.py -m yolo26n-pose.dxnn --video sample/squat_demo.mp4 --save
python yolo26n_pose_squat_sync.py -m yolo26n-pose.dxnn --camera 0
```

## Runtime options

| Option | Meaning |
|--------|---------|
| `--video, -v <file>` | Use a video file as input |
| `--camera, -c <id>` | Use a live camera (e.g. `0`) |
| `--image, -i <path>` | Single image / image directory |
| `--save, -s` | Save an annotated output video (video/camera) |
| `--no-display` | Run headless (no window); still saves with `--save` |
| `--target-reps <N>` | Game goal (default from `config.json`, 10) |
| `--config <path>` | Override config.json |

Press **q** or **ESC** in the display window to quit.

## How squat detection works

- **Knee angle** = angle at the knee between hip→knee and ankle→knee (COCO-17
  indices: hip 11/12, knee 13/14, ankle 15/16). Left + right are averaged when
  both legs are visible.
- **Hip angle** = angle at the hip (shoulder 5/6 → hip → knee). Used as a
  corroborating gate.
- A two-state FSM (UP↔DOWN) with **hysteresis** counts one rep per full
  DOWN→UP cycle. Thresholds are **auto-calibrated** from `sample/squat_demo.mp4`
  (2D knee angles bottom out near ~135°, not the textbook 90°, so fixed cutoffs
  miscount — see `calibrate.py`).

## Recalibrate thresholds

```bash
python calibrate.py --video sample/squat_demo.mp4   # rewrites config.json
```

## Verify

```bash
python verify.py        # NPU E2E: 17-keypoint pose + reps counted -> RESULT: PASS
```

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

## Files

| File | Purpose |
|------|---------|
| `yolo26n_pose_squat_sync.py` | Entry — builds factory, runs `SyncRunner` |
| `factory/squat_game_factory.py` | `SquatGameFactory` (IFactory) |
| `factory/squat_game_visualizer.py` | `SquatGameVisualizer` (game hook + HUD) |
| `factory/squat_logic.py` | Pure `angle_3pt` + `SquatCounter` FSM |
| `factory/__init__.py` | Factory export |
| `config.json` | Thresholds (calibrated) + target_reps |
| `calibrate.py` | Derive thresholds from the sample video |
| `verify.py` | NPU end-to-end verification |
| `test_squat_logic.py` | Unit tests for angle math + FSM (10 tests) |
| `setup.sh` / `run.sh` | Self-contained setup + relocatable launcher |
| `session.json` / `session.log` | Session metadata + command log |

## Self-contained / portable

`setup.sh` vendors the shared framework into `./common`; the entry walker prefers
that vendored `./common` (no `PYTHONPATH`). With the model + sample bundled, the
folder runs even when copied outside dx-all-suite — `dx_engine` (DEEPX runtime)
is the one external prerequisite.
