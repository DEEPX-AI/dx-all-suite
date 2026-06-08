# Arcade Stretching Mini-Game — built by dx-agentic-dev

> **This whole app was generated end-to-end by [dx-agentic-dev](../../docs/source/agentic_development.md)
> from a single natural-language prompt** — no hand-written code. It runs
> **yolo26n-pose** on the **DEEPX NPU** and guides the player through three
> stretches with an **animated coach avatar** derived from the sample clips.

<div align="center">
<table>
<tr>
<td align="center"><img src="../../docs/source/img/dx-agentic-dev-stretch-build.gif" width="470"><br><sub><b>dx-agentic-dev building this app (timelapse)</b></sub></td>
<td align="center"><img src="../../docs/source/img/dx-agentic-dev-stretch-gameplay.gif" width="300"><br><sub><b>The generated app running on the DX-M1 NPU</b></sub></td>
</tr>
</table>
</div>

The game guides the player through three stretches, one stage at a time, with a
top-left **coach** panel that demonstrates the target pose:

```
STAGE 1/3  REACH FOR THE SKY   — extend both arms straight overhead
STAGE 2/3  TOUCH YOUR TOES     — bend forward at the waist (forward fold)
STAGE 3/3  NECK RELEASE        — pull your head to one side with one hand
```

Hold the matching pose until the HOLD bar fills → `GOOD!` → next stage. Clear all
three → `CLEAR!`. Both a video file (`--video`) and a live camera (`--camera`) are
supported.

## See how the agent built it (session transcript)

This directory ships the **full Claude Code session** that produced the app, so you
can see how it followed the harness instructions, used the project skills/agents,
and reasoned through brainstorm → plan → TDD → verify:

- **[`claude-code-session.md`](./claude-code-session.md)** — renders directly on GitHub *(recommended)*
- **`claude-code-session.html`** — same content; **open locally in a browser** for a richer view

See the [Agentic Development guide](../../docs/source/agentic_development.md) for what to look for.

## Prerequisites

- **dx-runtime built** with a working `dx_engine` venv (`dx-runtime/venv-dx-runtime`),
  or run `./setup.sh` here to build an isolated session venv.
- **Model**: `yolo26n-pose.dxnn` (large binary, not committed). Download once:
  `(cd ../../dx-runtime/dx_app && ./setup.sh --models yolo26n-pose)`. `run.sh` checks
  for it and prints this hint if missing.
- **Sample video**: the concatenated `stretching_demo.mp4` is **bundled** under `sample/`,
  so the `./run.sh` demo is self-contained. (`verify.py` / `calibrate_templates.py`
  use the three individual source clips at `dx_app/sample/`, which are not bundled.)

## Quick start

```bash
# 1) one-time environment setup (python3.12 venv + dx_engine wheel + GUI opencv)
./setup.sh

# 2a) demo: run on the bundled video, save an annotated output (headless)
./run.sh

# 2b) a specific video file (annotated output video is saved)
./run.sh --video /path/to/clip.mp4

# 2c) live camera with an on-screen window
./run.sh --camera 0
```

`run.sh` auto-detects the suite root, prefers the bundled `sample/stretching_demo.mp4`,
guards for the model, and activates the local venv (or falls back to the shared
`dx-runtime/venv-dx-runtime`).

## Command-line options (via the framework `parse_common_args`)

| Option | Meaning |
|--------|---------|
| `-m, --model` | Path to `yolo26n-pose.dxnn` (set by `run.sh`) |
| `--video <file>` | Input video file |
| `--camera <id>` | Live camera device id (e.g. `0`) |
| `--save` | Save an annotated output video (auto for the file demo) |
| `--save-dir <dir>` | Where to save (default: `artifacts/...`) |
| `--no-display` | Headless (no window) — required on servers |
| `--show-log` | Verbose per-frame/perf logs |

Direct invocation (no manual `PYTHONPATH` needed):
```bash
python yolo26n_pose_stretch_game_sync.py -m <model.dxnn> --video sample/stretching_demo.mp4 --save
```

## How pose recognition works

Each frame the dominant person's COCO-17 keypoints are classified with
**scale-normalized geometry**, where the unit is the body's leg length
(hip→ankle) — the torso collapses during a forward fold, so torso height is not
used as the scale.

- **Overhead reach** — both wrists above the head (`wrist.y < nose.y − margin`).
- **Forward fold** — torso compressed (shoulder→hip vertical gap small) *and* the
  head dropped to/below shoulder level.
- **Neck stretch** — exactly one wrist raised beside the head (above shoulders and
  horizontally near the head) while the other arm hangs low.

Thresholds live in `config.json`. Hold/animation timing is **frame-based** at the
configured `fps`, so the HOLD bar fills over `hold_seconds` of video time
identically on replay and in `verify.py`.

## Coach avatar (derived from the sample clips)

`calibrate_templates.py` runs pose inference over each sample clip, keeps the
frames where the matching pose fires, normalizes the skeleton into a canonical
figure space, and writes the per-coordinate median to `pose_templates.json`. At
runtime the coach panel interpolates between a neutral standing pose and the
stage's derived target pose on a loop, so it visibly demonstrates the motion.
If `pose_templates.json` is absent, hand-authored fallback templates are used.
(`coach_preview.png` / `coach_calibrated.png` show the rendered coach.)

Rebuild templates:
```bash
python calibrate_templates.py -m <model.dxnn>
```

## Files

| File | Purpose |
|------|---------|
| `yolo26n_pose_stretch_game_sync.py` | Entry point (SyncRunner + StretchGameFactory) |
| `factory/yolo26n_pose_stretch_game_factory.py` | `StretchGameFactory(IPoseFactory)` |
| `factory/__init__.py` | factory export |
| `stretch_game_engine.py` | `StretchGameVisualizer` + `StretchClassifier` (game engine) |
| `coach_avatar.py` | coach templates + stick-figure renderer |
| `calibrate_templates.py` | derive `pose_templates.json` from the sample clips |
| `pose_templates.json` | baked coach templates (calibration output) |
| `config.json` | thresholds, hold/fps, pose geometry |
| `setup.sh` / `run.sh` | environment setup / launcher |
| `verify.py` | headless validation over the 3 clips → `RESULT: PASS` |
| `sample/stretching_demo.mp4` | bundled demo input (3 stretches concatenated) |
| `coach_preview.png`, `coach_calibrated.png` | rendered coach evidence |
| `session.log` | real captured command output |
| `claude-code-session.md` / `.html` | the full agent session that built this app |

## Validation evidence

- `verify.py` (NPU, session venv): per-clip stage clears for overhead / fold / neck,
  and the end-to-end 3-clip sequence reaches `GAME_CLEAR` → `RESULT: PASS` (exit 0).
- Full game run on `sample/stretching_demo.mp4` (1280×720, 721 frames): progressed
  STAGE 1→2→3→CLEAR!, annotated `output.mp4` saved under `artifacts/`.
- NPU inference ≈ 65 FPS (15 ms/frame), overall pipeline ≈ 43 FPS.

## Notes

- Variant: **sync only** — the game is a stateful, ordered-frame experience; the
  framework's `AsyncRunner` reorders frames and is unsuitable for hold timing.
- Recognizes the single dominant person.
