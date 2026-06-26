# Stretch Coach — Arcade Stretching Mini-Game (yolo26n-pose · DX-M1 NPU)

> **The story.** From a single natural-language prompt, dx-agent-dev builds a complete
> on-device **arcade stretching game**: `yolo26n-pose` COCO-17 keypoints run on the DEEPX
> **DX-M1 NPU**, guiding the player through **3 stretches** (overhead reach → forward fold →
> neck stretch) with a HOLD-to-advance loop and GOOD!/CLEAR! feedback.
>
> A top-left **coach avatar** — a filled, person-like humanoid (round head, filled
> torso/pelvis, tapered limb capsules with shaded joints) — demonstrates each target
> stretch, looping between a neutral stance and the pose so the player can copy it.

<div align="center"><table><tr>
<td align="center"><img src="../../docs/source/img/dx-agent-dev-stretch-gameplay.gif" width="460"><br><sub><b>gameplay — filled humanoid coach (top-left) + live NPU pose tracking</b></sub></td>
<td align="center"><img src="../../docs/source/img/dx-agent-dev-stretch-build.gif" width="320"><br><sub><b>dx-agent-dev building it (timelapse)</b></sub></td>
</tr></table></div>

> **See how the agent built it:** [`claude-code-session.md`](./claude-code-session.md).

### Session metrics

| Metric | Value |
|--------|-------|
| Coding agent / model | **Claude Code** / **Claude Opus 4.8** (`claude-opus-4-8`) |
| Human input | **1 natural-language prompt** — fully autonomous |
| Skills | `dx-skill-router` → `dx-agent-brainstorm` → `dx-swe-writing-plans` → `dx-agent-tdd` → `dx-agent-verify` |
| Build wall-clock / turns | ≈ 15.3 min / 130 |
| Output tokens / approx. cost | ≈ 142K / ≈ $8.1 |
| Tools | `Bash`×27, `Read`×17, `Write`×12, `Skill`×5, `Edit`×2 |

## The prompt

The prompt (verbatim below) asks for the coach avatar to be a **filled procedural
humanoid** built from the pose keypoints:

```
Using the yolo26n-pose model on the DEEPX NPU, build a simple arcade-style stretching mini-game. The game guides the user through three stretch poses, one stage at a time: (1) extend both arms straight overhead, (2) bend forward at the waist (forward fold), and (3) pull the head to one side with one hand for a neck stretch.

For each stage, render a small coach avatar in a top-left panel that demonstrates the current target stretch. IMPORTANT — the coach must look like a REAL PERSON, not a stick figure: draw it as a FILLED, PROCEDURAL HUMANOID built from the pose keypoints — a round head, a filled torso/pelvis body, and tapered LIMB CAPSULES (filled rounded segments for upper-arm/forearm and thigh/shin) with smooth filled joints, shaded so it reads as a human body silhouette. Do NOT draw it as thin stick-figure lines or a bare keypoint skeleton. Animate the coach so it feels alive — cycle smoothly between a neutral standing pose and the full target stretch pose (a looped demonstration). Show the stretch name and a short text instruction next to the coach.

Recognize each pose from the player's body keypoints (wrists above the head for the overhead reach; torso folded forward with shoulders dropped toward hips for the waist bend; one hand raised beside the head for the neck stretch). When the user holds the matching pose briefly, advance to the next stage; clear the game when all three are done.

Overlay an arcade-style UI on each frame: STAGE n/3, the animated humanoid coach avatar, the target stretch name + instruction, a HOLD progress indicator, and GOOD! / CLEAR! feedback. The generated app must support both a video-file input and a live camera input, selectable at runtime (e.g. --video <file> or --camera <id>). Implement and validate it using the provided demo video at dx-agent-dev-showcase/mini-game-stretching-coach/sample/stretching_demo.mp4, which contains a person performing the three stretches in sequence; derive the coach target-pose shapes as needed (procedurally or from representative frames of that video). When run on a video file, save an annotated output video so the result can be reviewed.

Work autonomously to completion without asking for confirmation or approval; make default decisions per the knowledge base and PRODUCE THE ACTUAL ARTIFACTS (runnable app + setup.sh + run.sh, validated headless --no-display --save on the demo video). Respond in English.
```

> **Run this prompt from the dx-all-suite root** — the sample video path is relative to the suite root, which is where DEEPX Agent-Driven Development routing starts.

## The game

| Stage | Stretch | Recognised from keypoints |
|------:|---------|---------------------------|
| 1/3 | **OVERHEAD REACH** | both wrists above the head |
| 2/3 | **FORWARD FOLD** | head/shoulders drop toward the hips (torso folds) |
| 3/3 | **NECK STRETCH** | one hand raised beside the head, other arm low |

Hold the matching pose ~1.2 s → **GOOD!** + advance; finish all three → **CLEAR!**
On-screen: STAGE n/3, the animated **humanoid coach** (top-left), stretch name + instruction,
a HOLD progress bar, your live skeleton, and a model · NPU · FPS status line.
Recognition is **scale-invariant** — every threshold is normalized by the player's
shoulder width, so the game works regardless of distance from the camera.

## Architecture

Standard dx_app pose pipeline — `StretchGameFactory` (`IPoseFactory`, reusing
`LetterboxPreprocessor` + `YOLOv8PosePostprocessor`) + `SyncRunner`. The entry
(`yolo26n_pose_sync.py`) only wires the factory into `SyncRunner`; all game logic lives
in the visualizer. `stretch_coach.py` holds `StretchCoachVisualizer` — the per-frame
state machine, the pose recognizers, the filled-humanoid coach renderer
(`cv2.fillConvexPoly` torso + tapered limb capsules), and the arcade HUD.

## Reproduce

```bash
bash setup.sh        # venv (dx-runtime) + GUI OpenCV + vendor framework
bash run.sh          # runs the bundled demo video → annotated output/<run>/output.mp4
bash run.sh --camera 0          # live camera (needs a display)
bash run.sh --video clip.mp4    # any video
```

`run.sh` with **no arguments** plays the bundled `sample/stretching_demo.mp4` headless and
saves an annotated mp4 under `output/<run>/`. Any arguments you pass are forwarded to the
app (e.g. `--camera 0`, `--video path.mp4`). Override the model with
`DXNN_MODEL=/path/yolo26n-pose.dxnn bash run.sh`.

> x86-64 Linux + DeepX DX-M1 runtime (`yolo26n-pose.dxnn`). Self-contained: `common/` is
> vendored and `sample/stretching_demo.mp4` is bundled; the app runs once moved out of the suite.

## Files

| File | Purpose |
|------|---------|
| `yolo26n_pose_sync.py` | Entry — `StretchGameFactory` + `SyncRunner` (standalone import walker) |
| `stretch_coach.py` | `StretchCoachVisualizer` — pose recognizers, **filled-humanoid coach renderer**, `StretchGame` state machine + arcade HUD |
| `factory/` | `IPoseFactory` base + `StretchGameFactory` (Letterbox + YOLOv8Pose) |
| `common/` | vendored dx_app framework (runner, processors, base, …) |
| `config.json` | pose thresholds + hold timing (calibrated from the demo) |
| `test_recognizers.py` | unit test — asserts each stage recognizer fires on the right pose |
| `setup.sh` / `run.sh` | relocatable setup / one-command launcher |
| `sample/stretching_demo.mp4` | bundled demo input |
| `session.json` / `session.log` | build metadata / real command output log |
| `claude-code-session.md` | full agent build transcript |

Korean: [`README-ko.md`](./README-ko.md).
