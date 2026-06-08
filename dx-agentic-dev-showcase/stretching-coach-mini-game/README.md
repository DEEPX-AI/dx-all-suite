# Stretch Arcade Mini-Game — built by dx-agentic-dev

> **Generated end-to-end by [dx-agentic-dev](../../docs/source/agentic_development.md)
> from a single natural-language prompt** — no hand-written code. The folder is
> **self-contained & portable** (vendored `./common`): it runs even when copied
> outside dx-all-suite (any machine with the DEEPX runtime).

<div align="center">
<table>
<tr>
<td align="center"><img src="../../docs/source/img/dx-agentic-dev-stretch-build.gif" width="470"><br><sub><b>dx-agentic-dev building this app (timelapse)</b></sub></td>
<td align="center"><img src="../../docs/source/img/dx-agentic-dev-stretch-gameplay.gif" width="300"><br><sub><b>The generated app running on the DX-M1 NPU</b></sub></td>
</tr>
</table>
</div>

> **See how the agent built it:** [`claude-code-session.md`](./claude-code-session.md)
> (renders on GitHub; `claude-code-session.html` opens in a local browser).

An arcade-style stretching mini-game running `yolo26n-pose` on the DEEPX NPU. It
guides the player through **three stretches, one stage at a time**, with an
animated stick-figure **coach** demonstrating each target pose:

| Stage | Stretch | How it's recognised (COCO-17, leg-normalized) |
|-------|---------|------------------------------------------------|
| 1/3 | **Overhead reach** | both wrists above the nose **and** the shoulders |
| 2/3 | **Forward fold** | shoulders dropped toward the hips **and** hands reaching to/below hip level |
| 3/3 | **Neck stretch** | exactly **one** hand raised beside the head (near head height + close to an ear) |

Hold the matching pose briefly (a frame-based HOLD bar fills) → **GOOD!**, advance
to the next stage. Finish all three → **CLEAR!**

## Arcade UI (overlaid on every frame)
- Top banner: title + `STAGE n/3` (→ `COMPLETE`).
- Top-left **coach panel**: an animated stick figure that cycles between a neutral
  standing pose and the target stretch (both **derived from the sample clips** by
  `calibrate_coach_poses.py` → `pose_templates.json`), plus the stretch **name** and
  a short **instruction**, and a **HOLD %** progress bar.
- Center **GOOD! / CLEAR!** feedback text.
- The player's live skeleton is drawn over the video.

## Architecture (framework-compliant)
- **IFactory** `StretchGameFactory`: `LetterboxPreprocessor` + `YOLOv8PosePostprocessor`
  + custom `StretchGameVisualizer`.
- **SyncRunner** (not AsyncRunner): the game is stateful and needs strictly ordered
  frames. The visualizer instance persists across frames and holds the game state.
- Recognition + state machine live in `pose_logic.py` (pure, NPU-free, unit-tested).

## Quick start
```bash
./setup.sh                                   # resolve dx_engine venv + vendor ./common
./run.sh --video sample/stretching_demo.mp4  # video file → saves annotated output/
./run.sh --camera 0                          # live camera input
# explicit model: MODEL=/path/yolo26n-pose.dxnn ./run.sh --camera 0
```
`run.sh` is **relocatable**: venv fallback chain, a model-existence guard with a
download hint, bundled-sample-first input, and it saves into the app's own `output/`
so the folder runs even when copied outside dx-all-suite (it carries a vendored
`./common`; `dx_engine` is the one external prerequisite).

## Files
| File | Role |
|------|------|
| `stretch_game_sync.py` | Entry point (SyncRunner + factory; portable `common` walker). |
| `factory/stretch_game_factory.py`, `factory/__init__.py` | IFactory (5 methods). |
| `stretch_game_visualizer.py` | Stateful game + arcade UI overlay. |
| `coach.py` | Animated stick-figure coach avatar. |
| `pose_logic.py` | NPU-free recognizers + `StretchGame` state machine. |
| `config.json` | thresholds + game params (hold, grace). |
| `pose_templates.json` | coach skeletons baked from the clips. |
| `calibrate_coach_poses.py` | OFFLINE dev tool: measure clips → thresholds + templates. |
| `verify.py` | end-to-end validation (per-clip clears + demo CLEAR), saves videos. |
| `game_eval.py` | dev helper: drives the real SyncRunner pipeline over a video. |
| `test_pose_logic.py` | unit tests (7) for the recognizers + state machine. |
| `setup.sh`, `run.sh` | env setup (vendors `common`) + relocatable launcher. |
| `sample/stretching_demo.mp4` | bundled demo input (3 stretches concatenated). |
| `claude-code-session.md` / `.html` | the full agent session that built this app. |

## Validation evidence (see `session.log`)
- Unit tests: **7 passed**.
- Fresh clip measurement — pose separation on own clip: **overhead 47.9% / fold 40.8% / neck 50.8%**, ~0 cross-talk.
- `verify.py`: **RESULT: PASS** — each clip clears its target stage; `stretching_demo.mp4` reaches full **CLEAR (3/3)**.
- Runtime: **~35 FPS** on the NPU. Annotated `output.mp4` saved for video inputs.
- Portability: runs outside the suite on the vendored `./common`.
