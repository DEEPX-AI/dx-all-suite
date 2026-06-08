# Arcade Stretching Mini-Game — built by dx-agentic-dev

> **This whole app was generated end-to-end by [dx-agentic-dev](../../docs/source/agentic_development.md)
> from a single natural-language prompt** — no hand-written code. It runs
> `yolo26n-pose` on the **DEEPX NPU** and guides the player through three stretches
> with an **animated coach avatar** derived from the sample clips.

<div align="center">
<table>
<tr>
<td align="center"><img src="../../docs/source/img/dx-agentic-dev-stretch-build.gif" width="470"><br><sub><b>dx-agentic-dev building this app (timelapse)</b></sub></td>
<td align="center"><img src="../../docs/source/img/dx-agentic-dev-stretch-gameplay.gif" width="300"><br><sub><b>The generated app running on the DX-M1 NPU</b></sub></td>
</tr>
</table>
</div>

A frame-sequential arcade game driven by live body-pose keypoints from the DX-M1
NPU. It guides the player through **three stretches**, one stage at a time, with an
animated stick-figure **coach**, a **HOLD** meter, and **GOOD! / CLEAR!** feedback.

## See how the agent built it (session transcript)

The **full Claude Code session** that produced this app is included:

- **[`claude-code-session.md`](./claude-code-session.md)** — renders on GitHub *(recommended)*
- **`claude-code-session.html`** — same content; open locally in a browser for a richer view

| Stage | Stretch | Recognition (COCO-17, leg-normalized) |
|-------|---------|----------------------------------------|
| 1/3 | **Overhead Reach** | both wrists above the head (above nose + shoulders) |
| 2/3 | **Forward Fold** | torso folded at the waist + hands dropped toward the hips |
| 3/3 | **Neck Stretch** | exactly one hand raised beside the head |

## Quick start

```bash
./setup.sh                      # python3.12 venv + GUI opencv + dx_engine wheel
./run.sh                        # default: bundled sample clip, saves annotated video
./run.sh --video /path/clip.mp4 --save     # a specific video file (annotated mp4 saved)
./run.sh --camera 0             # live camera (display window)
```

`run.sh` is relocatable: it picks the first venv that can import `dx_engine`
(local `venv` → `dx-runtime/venv-dx-runtime`), guards on the model file, and
falls back to a bundled sample when no input is given.

Direct invocation (IFactory + SyncRunner):
```bash
python stretch_game_sync.py -m <yolo26n-pose.dxnn> --video sample/stretching_demo.mp4 --save
```

## How it works (framework-compliant)

- **IFactory + SyncRunner only.** `StretchGameFactory` (an `IPoseFactory`) wires the
  stock `LetterboxPreprocessor` + `YOLOv8PosePostprocessor` with the custom
  `StretchGameVisualizer`. The game's whole state machine + arcade UI live in the
  visualizer — engine calls stay inside `SyncRunner`. **Sync** is required: the game
  is frame-sequential (hold timers), and `AsyncRunner` would reorder frames.
- **Coach poses derived from the clips.** `calibrate_coach_poses.py` runs the model
  over each sample clip, takes the median normalized skeleton of the matching frames,
  and writes `coach_poses.json`. The coach animates neutral↔target.
- **Scale-invariant recognition with the leg-scale fix.** Distances are normalized by
  a hip→ankle leg scale (NOT torso — the torso collapses in a forward fold).

## Files

| File | Purpose |
|------|---------|
| `stretch_game_sync.py` | Entry point — `SyncRunner(StretchGameFactory)` |
| `factory/stretch_game_factory.py` | IFactory: stock pre/post + game visualizer |
| `factory/__init__.py` | Exports `StretchGameFactory` |
| `game_visualizer.py` | `StretchGameVisualizer` — state machine + arcade UI |
| `stretch_pose_rules.py` | Pure keypoint recognizers + `StretchTracker` (hold) |
| `coach_avatar.py` | Animated stick-figure coach renderer |
| `coach_poses.json` | Clip-calibrated neutral + 3 target skeletons |
| `calibrate_coach_poses.py` | Offline: derive coach poses from the sample clips |
| `config.json` | Model thresholds + game tuning (hold/loop/miss tolerance) |
| `test_stretch_rules.py` | Unit tests for recognizers + tracker |
| `verify.py` | E2E: per-clip separation + combined-demo CLEAR! check |
| `setup.sh` / `run.sh` | Environment setup / relocatable launcher |
| `sample/stretching_demo.mp4` | bundled demo input (3 stretches concatenated) |
| `session.log` | Real validation command output |
| `claude-code-session.md` / `.html` | the full agent session that built this app |

## Validation results

- `pytest test_stretch_rules.py` → **7 passed**.
- `verify.py` → **RESULT: PASS** (exit 0). Per-clip separation:
  overhead 115 / fold 98 / neck 122 own-clip matches, near-zero cross-talk.
  End-to-end `stretching_demo.mp4` (721 frames) → **CLEAR!**.
- Annotated demo runs at ~34–37 FPS on the DX-M1 (`./run.sh` writes `output.mp4`).

## CLI options

`-m/--model` (required), `--video <f>` | `--camera <id>` | `--image <f>` | `--rtsp <url>`,
`--save` (+ `--save-dir`), `--no-display`, `--config`, `--show-log`.
