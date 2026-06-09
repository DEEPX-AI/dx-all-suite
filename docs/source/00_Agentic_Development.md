# DEEPX Agentic Development - dx-agentic-dev (Beta)

> **Beta Feature** — Agentic development support is under active development.
> Skill definitions and routing behavior may change between releases.

## Introduction

Build DEEPX AI applications using natural language instructions. AI coding agents
understand the DEEPX SDK ecosystem — GStreamer pipeline construction, `.dxnn` model
resolution, InferenceEngine configuration, and DxPreprocess/DxInfer element wiring —
so you can describe *what* you want and let the agent handle the implementation details.

Supported workflows include:

- Standalone inference apps with `IFactory`, `SyncRunner`, and `AsyncRunner`
- GStreamer video pipelines using DEEPX's 13 custom elements across 6 categories
- Cross-project builds that span dx_app, dx_stream, and dx-runtime
- Model compilation from ONNX to DXNN format using DX-COM (in dx-compiler)

## Demo: a fitness game from one prompt — fully autonomous, ~20 min, ~$10

**You can develop a complete fitness game on the DEEPX NPU — fully autonomously, by
natural language — in about 20 minutes for roughly $10.** No hand-written code: from a
single prompt, the AI coding agent runs the entire brainstorm → plan → TDD → verify
workflow and ships a runnable, on-device-NPU app.

To show what that looks like, here are **two mini-games** built exactly this way. Each is
checked into the suite as a runnable showcase, with its full build-session transcript:

| Showcase | What it is | Build time | Agent turns | Output tokens | ~Cost |
|----------|-----------|-----------|-------------|---------------|-------|
| **[Squat-counting mini-game](../../dx-agentic-dev-showcase/squat-fitness-mini-game/)** | Counts squat reps from knee/hip angles + arcade HUD (reps / score / DOWN·UP·GOOD!) | ≈ 20 min | 81 | ≈ 85K | ≈ $9.9 |
| **[Stretching coach mini-game](../../dx-agentic-dev-showcase/stretching-coach-mini-game/)** | Guides 3 stretches with an animated **coach avatar** that demonstrates each target pose | ≈ 21 min | 75 | ≈ 85K | ≈ $9.4 |

Both were built by **Claude Code** (model **Claude Opus 4.8**) from **one** prompt, fully
autonomously, running the full `dx-skill-router → dx-agentic-brainstorm →
dx-swe-writing-plans → dx-agentic-tdd → dx-agentic-verify` sequence, and both support a
**video-file input and a live camera input** (`--video <file>` / `--camera <id>`).
Per-app metrics + transcripts are in each showcase's `README.md`.

### Showcase 1 — Squat-counting mini-game

**The prompt** (given to Claude Code in the `dx_app` directory):

> Using the yolo26n-pose model on the DEEPX NPU, build a simple squat-counting
> fitness mini-game. Implement and validate it using the sample video at
> `sample/squat_demo.mp4`. The generated app must support **both a video-file
> input and a live camera input, selectable at runtime via command-line options**
> (e.g. `--video <file>` or `--camera <id>`). Detect squat repetitions from body
> keypoints (use knee and hip angles to recognize the down then up motion), count
> the reps in real time, and overlay an arcade-style fitness game UI on each frame
> (rep counter, target reps, a score, and DOWN / UP / GOOD! feedback text). When
> run on a video file, save an annotated output video so the result can be reviewed.

The agent named its game **"SQUAT CHALLENGE"** and added a `yolo26n-pose · DX-M1 NPU`
badge to the HUD — all from that single prompt.

<div align="center">
<table>
<tr>
<td align="center"><img src="./img/dx-agentic-dev-squat-build.gif" width="520"><br><sub><b>The agent building the app — brainstorm → plan → TDD → verify (timelapse)</b></sub></td>
<td align="center"><img src="./img/dx-agentic-dev-squat-gameplay.gif" width="205"><br><sub><b>The generated app running on the DX-M1 NPU</b></sub></td>
</tr>
</table>
</div>

### Showcase 2 — Stretching coach mini-game

An arcade stretching game that guides the player through three stretches, one stage at
a time, drawing an animated stick-figure **coach avatar** (derived from the sample
clips) that demonstrates each target pose for the user to follow.

**The prompt** (given to Claude Code in the `dx_app` directory):

> Using the yolo26n-pose model on the DEEPX NPU, build a simple arcade-style
> stretching mini-game. The game guides the user through three stretch poses, one
> stage at a time: (1) extend both arms straight overhead, (2) bend forward at the
> waist (forward fold), and (3) pull the head to one side with one hand for a neck
> stretch. For each stage, **render a small human-figure "coach" avatar** in a
> top-left panel that demonstrates the current target stretch — a clean stick-figure
> posed in the target stretch, **animated** between a neutral standing pose and the
> full target pose, with each target shape **derived from the corresponding sample
> clip**. Show the stretch name + a short instruction and a HOLD progress bar; when
> the user holds the matching pose, advance; clear when all three are done. The app
> **must support both a video-file input and a live camera input** (`--video <file>`
> or `--camera <id>`). When run on a video file, save an annotated output video.

<div align="center">
<table>
<tr>
<td align="center"><img src="./img/dx-agentic-dev-stretch-build.gif" width="520"><br><sub><b>The agent building the stretching game (timelapse)</b></sub></td>
<td align="center"><img src="./img/dx-agentic-dev-stretch-gameplay.gif" width="205"><br><sub><b>The generated app on the DX-M1 NPU — coach avatar + 3 stages</b></sub></td>
</tr>
</table>
</div>

### What the agent did

Prompted once, the agent ran the full DEEPX agentic workflow on its own:

1. **`dx-skill-router`** → **`dx-agentic-brainstorm`** — inspected the existing
   `yolo26n_pose` example, confirmed the model and framework APIs, and wrote a design spec.
2. **`dx-swe-writing-plans`** — produced a step-by-step implementation plan.
3. **`dx-agentic-tdd`** — generated the app file-by-file, verifying each one.
4. **`dx-agentic-verify`** — ran the framework validator and a fresh on-NPU run,
   confirming the app counts squats and saves an annotated video before declaring done.

The result lands in an isolated session directory
(`dx_app/dx-agentic-dev/<session>/`) and never touches existing source.

### How the generated app is structured

The agent followed the dx_app **skeleton-first + `IFactory`** rules — it did *not*
write a standalone script. The generated app:

- **reuses** the framework's standard pose preprocessor/postprocessor (the DXNN
  model self-describes its input size; the YOLO-pose postprocessor emits COCO
  17-point body keypoints);
- adds **only a custom visualizer** that carries the game's logic — a knee-angle
  **squat rep counter** (one rep per full DOWN→UP cycle) plus the on-frame HUD
  (reps / target / score / DOWN·UP·GOOD! feedback);
- executes through the framework's **`SyncRunner`** (single ordered video →
  sequential, stateful counting), which drives the read → NPU inference →
  visualize → save loop;
- keeps game tuning (target reps, knee-angle thresholds, score per rep) in
  `config.json`, so behavior changes without touching code.

Run it like any other dx_app example — point the generated `*_sync.py` app at the
`.dxnn` model and the input video with `--save`, and it writes an annotated
output video.

> **Note:** dx-agentic-dev generates fresh code on each run, so the exact class
> names, filenames, and config values vary between builds. What stays constant is
> the **pattern** above — `IFactory` reuse + a custom visualizer + `SyncRunner` —
> which is what these docs describe.

> **Reproducibility note:** this build was repeated multiple times from the same
> prompt; each run independently produced a runnable app that correctly counts the
> squats — with different but valid code structures, confirming the result is
> re-derived from the knowledge base rather than memorized.

### Run the generated sample yourself

One representative build of this demo is **checked into the suite** so you can run
it without re-generating anything:

📂 **[`dx-agentic-dev-showcase/squat-fitness-mini-game/`](../../dx-agentic-dev-showcase/squat-fitness-mini-game/)**
 — start with its **[README](../../dx-agentic-dev-showcase/squat-fitness-mini-game/README.md)**.

```bash
cd dx-agentic-dev-showcase/squat-fitness-mini-game

./setup.sh                       # verify the dx-runtime venv + NPU sanity, install deps
./run.sh                         # video demo on the bundled sample -> annotated output.mp4
./run.sh --camera 0              # live camera (needs a display)
./run.sh --video /path/clip.mp4 --save
```

The sample video is **bundled** with the showcase, and `run.sh` auto-detects the
suite root (so it works from this relocated path) and prints a clear hint if the
`yolo26n-pose.dxnn` model still needs to be downloaded. Because dx-agentic-dev
generates fresh code each run, the class names and filenames in that directory are
one concrete instance of the **pattern** described above — yours may differ.

The **stretching coach mini-game** showcase (Showcase 2 above) runs exactly the same
way — `./setup.sh` then `./run.sh` (or `./run.sh --camera 0`) from
[`dx-agentic-dev-showcase/stretching-coach-mini-game/`](../../dx-agentic-dev-showcase/stretching-coach-mini-game/).
Build/run metrics for both showcases are in the table at the top and in each
showcase's `README.md`.

### Inspect the agent's session — how it followed the harness

The showcase also ships the **complete Claude Code session** that produced the app.
This is the most direct way to see how much of the result comes from *harness
engineering* — the layered `CLAUDE.md` / `.deepx/` instructions, agents, and skills
that steer the model — rather than the model improvising:

- **[`claude-code-session.md`](../../dx-agentic-dev-showcase/squat-fitness-mini-game/claude-code-session.md)**
  — renders directly on GitHub *(recommended for a quick read)*.
- **`claude-code-session.html`** — the same transcript; **open it locally in a
  browser** for a richer, styled view (GitHub shows HTML as source, not rendered).

Reading the transcript, you can watch the harness in action:

- **Instruction-following** — the agent honors the suite HARD GATES: it emits the
  `[DX-AGENTIC-DEV: START]` / `DONE` session sentinels, keeps all output inside an
  isolated session directory (never touching existing source), and refuses to write
  placeholder/stub code.
- **Skill & agent utilization** — it invokes the mandatory skill sequence as real
  tool calls — `dx-skill-router` → `dx-agentic-brainstorm` → `dx-swe-writing-plans`
  → `dx-agentic-tdd` → `dx-agentic-verify` — instead of just *mentioning* them.
- **Actual reasoning** — you can follow how it inspected the existing
  `yolo26n_pose` example, confirmed the real framework APIs from the knowledge base,
  calibrated the knee-angle thresholds from measured data, wrote unit tests first
  (RED), then generated and verified the app file-by-file before declaring done.

This is the point of the showcase: the quality comes less from the raw model and
more from the **instructions, skills, and verification gates** the harness imposes.

## Prerequisites

| Requirement | Details |
|---|---|
| **DEEPX development environment** | DX-RT SDK installed and `setup_env.sh` sourced |
| **AI coding agent** (one of) | Claude Code, GitHub Copilot (VS Code), Cursor, OpenCode, or Codex CLI |
| **Python** | 3.10+ with the dx-all-suite packages installed |

## Architecture Overview

The agentic knowledge base is organized into three independent layers. Each layer
ships its own `.deepx/` directory containing skills, instructions, and memory files
that the agent reads at task time.

### dx_app — Standalone Inference

Python and C++ applications that run inference without GStreamer. Key abstractions:

- **IFactory** — creates model-specific pre/post-processing pipelines
- **SyncRunner / AsyncRunner** — blocking and non-blocking inference executors
- **DxInfer** — low-level inference wrapper around InferenceEngine

The `.deepx/` knowledge base covers model loading, `.dxnn` resolution, batch
processing, and result visualization.

### dx_stream — GStreamer Pipelines

Real-time video analytics built on GStreamer. The agent understands all 13 DEEPX
elements organized into 6 functional categories (source, inference, overlay,
encoding, streaming, and sink) and can assemble multi-branch pipelines from a
single natural-language prompt.

### dx-runtime — Integration Layer

Cross-project routing and unified validation. dx-runtime sits above the other two
layers, dispatching tasks to the correct sub-project builder and applying
consistent coding standards, testing patterns, and model-management rules.

### dx-compiler — Model Compilation

DXNN model compilation powered by DX-COM. The agent understands the full
compilation pipeline — ONNX model validation, config.json generation with auto-inferred
parameters, calibration data preparation, INT8 quantization, and PPU configuration —
and can compile models from a single natural-language prompt. Before compilation, the
agent asks mandatory brainstorming questions about NMS-free model detection, ONNX
simplification, and PPU compilation to ensure correct configuration.

## Available Agents and Skills

Agents and skills are available at every level of the repository. The top-level
dx-all-suite provides routing agents that classify tasks and dispatch to the
correct submodule.

### Agents by Level

| Level | Agent | Description |
|---|---|---|
| **dx-all-suite** | `@dx-suite-builder` | Top-level router — classifies tasks and routes to the appropriate submodule |
| **dx-all-suite** | `@dx-suite-validator` | Suite-wide validation — runs framework checks across all 3 levels |
| **dx-runtime** | `@dx-runtime-builder` | Cross-project builder — routes to dx_app or dx_stream |
| **dx-runtime** | `@dx-validator` | Unified validation orchestrator with feedback loop |
| **dx_app** | `@dx-app-builder` | Standalone inference builder — routes to specialist builders |
| **dx_app** | `@dx-python-builder` | Python inference app builder (4 variants: sync, async, cpp_postprocess, async_cpp_postprocess) |
| **dx_app** | `@dx-cpp-builder` | C++ inference app builder |
| **dx_app** | `@dx-model-manager` | Model download and registry manager |
| **dx_app** | `@dx-validator` | dx_app validation and feedback loop |
| **dx_stream** | `@dx-stream-builder` | GStreamer pipeline builder — routes to specialist builders |
| **dx_stream** | `@dx-pipeline-builder` | Pipeline construction (6 categories incl. broker) |
| **dx_stream** | `@dx-validator` | dx_stream validation and feedback loop |
| **dx-compiler** | `@dx-compiler-builder` | Model compilation router — routes to converter or compiler |
| **dx-compiler** | `@dx-model-converter` | PyTorch to ONNX model converter |
| **dx-compiler** | `@dx-dxnn-compiler` | ONNX to DXNN compiler (DX-COM) |

### Skills (OpenCode only)

| Level | Skill | Description |
|---|---|---|
| **dx-runtime** | `/dx-agentic-runtime-validate` | Validate, collect feedback, apply fixes, verify |
| **dx_app** | `/dx-agentic-app-build-python` | Build Python inference app |
| **dx_app** | `/dx-agentic-app-build-cpp` | Build C++ inference app |
| **dx_app** | `/dx-agentic-app-build-async` | Build async high-performance app |
| **dx_app** | `/dx-agentic-app-model-management` | Download and configure models |
| **dx_app** | `/dx-agentic-app-validate` | Run validation checks |
| **dx_stream** | `/dx-agentic-stream-build-pipeline` | Build GStreamer pipeline app |
| **dx_stream** | `/dx-agentic-stream-build-mqtt-kafka` | Build MQTT/Kafka pipeline app |
| **dx_stream** | `/dx-agentic-stream-validate` | Run validation checks |
| **dx_stream** | `/dx-agentic-stream-model-management` | Download and configure models |
| **dx-compiler** | `/dx-agentic-compiler-convert` | Convert PyTorch model to ONNX |
| **dx-compiler** | `/dx-agentic-compiler-compile` | Compile ONNX model to DXNN |
| **dx-compiler** | `/dx-agentic-compiler-validate` | Validate compiled DXNN output |
| **DX All Suite** | `/dx-swe-brainstorm` | Process: collaborative design session before any work |
| **DX All Suite** | `/dx-swe-tdd` | Process: test-driven development — validate incrementally |
| **DX All Suite** | `/dx-swe-verify` | Process: verify before claiming completion — evidence before assertions |
| **dx-runtime** | `/dx-swe-brainstorm` | Process: collaborative design session before code generation |
| **dx-runtime** | `/dx-swe-tdd` | Process: test-driven development — validate each file immediately after creation |
| **dx-runtime** | `/dx-swe-verify` | Process: verify before claiming completion — evidence before assertions |
| **dx_app** | `/dx-swe-brainstorm` | Process: collaborative design session before code generation |
| **dx_app** | `/dx-swe-tdd` | Process: test-driven development — validate each file immediately after creation |
| **dx_app** | `/dx-swe-verify` | Process: verify before claiming completion — evidence before assertions |
| **dx_stream** | `/dx-swe-brainstorm` | Process: collaborative design session before code generation |
| **dx_stream** | `/dx-swe-tdd` | Process: test-driven development — validate each file immediately after creation |
| **dx_stream** | `/dx-swe-verify` | Process: verify before claiming completion — evidence before assertions |
| **dx-compiler** | `/dx-swe-brainstorm` | Process: collaborative design session before compilation |
| **dx-compiler** | `/dx-swe-tdd` | Process: test-driven development — validate each step incrementally |
| **dx-compiler** | `/dx-swe-verify` | Process: verify before claiming completion — evidence before assertions |

> **Tip:** If you are unsure which submodule to target, use `@dx-suite-builder`
> at the top level — it will classify your task and route to the correct builder.

## Supported AI Tools

Agentic development works with five AI coding tools. Each tool auto-loads
the `.deepx/` knowledge base through its own configuration mechanism.

| Tool | Type | Auto-Load Mechanism | Agent Invocation | Skill Invocation |
|---|---|---|---|---|
| **Claude Code** | CLI | `CLAUDE.md` at project root | Free-form conversation; Context Routing Table dispatches automatically | — |
| **GitHub Copilot** | VS Code | `.github/copilot-instructions.md` | `@agent-name "prompt"` in Copilot Chat | — |
| **Cursor** | IDE | `.cursor/rules/*.mdc` | Free-form conversation; rules loaded by `alwaysApply` or `globs` | — |
| **OpenCode** | CLI | `AGENTS.md` + `opencode.json` | `@agent-name "prompt"` | `/skill-name` slash command |
| **Codex CLI** | CLI | `AGENTS.md` + `.codex/skills/dx-codex-identity/SKILL.md` | Free-form conversation (`~/bin/codex exec ...`) | `cat .deepx/skills/<name>/SKILL.md` (read directly) |

### What Gets Auto-Loaded

| Tool | Global Context | File-Specific Context | Agents | Skills |
|---|---|---|---|---|
| Claude Code | `CLAUDE.md` | Context Routing Table (manual) | `.claude/agents/*.md` (generated) | `.deepx/skills/` (read directly) |
| Copilot | `.github/copilot-instructions.md` | `.github/instructions/*.instructions.md` (`applyTo:` glob) | `.github/agents/*.agent.md` | `.github/skills/` (inline copies) |
| Cursor | `.cursor/rules/dx-*.mdc` (`alwaysApply: true`) | `.cursor/rules/*.mdc` (`globs: [...]`) | `.cursor/rules/` agent `.mdc` files | `.cursor/rules/` skill `.mdc` files |
| OpenCode | `AGENTS.md` + `opencode.json` instructions | — | `.opencode/agents/*.md` | `.deepx/skills/*/SKILL.md` |
| Codex CLI | `AGENTS.md` | — | `.deepx/agents/*.md` (direct `cat`) | `.codex/skills/dx-codex-identity/` (auto) + `.deepx/skills/` (manual `cat`) |

### First-Time Setup

No additional configuration is needed. Open the project directory in your
preferred tool and the configuration files are loaded automatically:

```bash
# Claude Code
cd dx-all-suite
claude

# OpenCode
cd dx-all-suite
opencode

# Codex CLI
cd dx-all-suite
~/bin/codex

# GitHub Copilot — open folder in VS Code
code dx-all-suite

# Cursor CLI
cd dx-all-suite
cursor-agent
```

### Platform File Loading Reference

Each AI coding agent auto-loads different configuration files at the suite level.
Files marked **Auto** are loaded on every conversation; **@mention** files are invoked
manually via agent or skill commands.

> **Git submodule boundary**: Copilot Chat/CLI, Claude Code, and Codex CLI only see
> files at the current git root. When opened at `dx-all-suite/`, they do NOT auto-load
> sub-project files in `dx-compiler/`, `dx-runtime/`, etc. (these are separate
> git submodules). OpenCode bridges this boundary via explicit path references
> in `opencode.json`.

#### Auto-Loaded Files

| File | Copilot Chat/CLI | OpenCode | Claude Code | Cursor | Loading |
|------|:---:|:---:|:---:|:---:|---------|
| `.github/copilot-instructions.md` | ✅ | — | — | — | Auto |
| `CLAUDE.md` | — | — | ✅ | — | Auto |
| `AGENTS.md` + `opencode.json` | — | ✅ | — | — | Auto |
| `.cursor/rules/dx-all-suite.mdc` | — | — | — | ✅ | Auto |

#### Agent Files (Manual @mention)

| Agent | Copilot (`@mention`) | OpenCode (`@mention`) |
|-------|------|---------|
| `dx-suite-builder` | `.github/agents/dx-suite-builder.agent.md` | `.opencode/agents/dx-suite-builder.md` |
| `dx-suite-validator` | `.github/agents/dx-suite-validator.agent.md` | `.opencode/agents/dx-suite-validator.md` |

> Claude Code has generated agent files in `.claude/agents/` (e.g., `dx-suite-builder.md`).
> Cursor has agent `.mdc` files in `.cursor/rules/` (e.g., `dx-suite-builder.mdc`).
> Claude Code also uses the Context Routing Table in `CLAUDE.md` to dispatch tasks.

#### Skill Files (OpenCode Only — `/slash-command`)

| Skill | File |
|-------|------|
| `/dx-swe-brainstorm` | `.deepx/skills/dx-swe-brainstorm/SKILL.md` |
| `/dx-swe-verify` | `.deepx/skills/dx-swe-verify/SKILL.md` |
| `/dx-swe-tdd` | `.deepx/skills/dx-swe-tdd/SKILL.md` |
| `/dx-swe-parallel-agents` | `.deepx/skills/dx-swe-parallel-agents/SKILL.md` |
| `/dx-swe-executing-plans` | `.deepx/skills/dx-swe-executing-plans/SKILL.md` |
| `/dx-swe-receiving-review` | `.deepx/skills/dx-swe-receiving-review/SKILL.md` |
| `/dx-swe-requesting-review` | `.deepx/skills/dx-swe-requesting-review/SKILL.md` |
| `/dx-skill-router` | `.deepx/skills/dx-skill-router/SKILL.md` |
| `/dx-swe-subagent-dev` | `.deepx/skills/dx-swe-subagent-dev/SKILL.md` |
| `/dx-swe-debugging` | `.deepx/skills/dx-swe-debugging/SKILL.md` |
| `/dx-swe-writing-plans` | `.deepx/skills/dx-swe-writing-plans/SKILL.md` |

#### Shared Knowledge Base (`.deepx/`)

The `.deepx/` directory is the **canonical source** (single source of truth) for all
platform-specific files. It contains agents, skills, templates, and fragments in a
platform-agnostic format. The `dx-agentic-gen` generator transforms this into
platform-specific files for Copilot (`.github/`), Claude Code (`.claude/`),
OpenCode (`.opencode/`), and Cursor (`.cursor/rules/`).

| Directory | Contents |
|-----------|----------|
| `agents/` | `dx-suite-builder`, `dx-suite-validator` |
| `skills/` | 13 skills (domain + shared process skills) |
| `templates/` | `{en,ko}/*.tmpl` — instruction file templates |
| `templates/fragments/` | `{en,ko}/*.md` — shared sections reused across repos |
| `memory/` | Persistent cross-session knowledge |
| `knowledge/` | Structured reference data |
| `instructions/` | Internal agent instructions |
| `toolsets/` | Tool reference documentation |

Instruction files (`CLAUDE.md`, `AGENTS.md`, `copilot-instructions.md`, EN+KO) are
also generated from templates and fragments — they should not be edited directly.

#### Platform File Generation

All platform-specific files are generated from `.deepx/` by the `dx-agentic-dev-gen`
package. Never edit generated files directly.

```bash
pip install -e .deepx/tools   # Install generator
dx-agentic-gen generate                    # Generate platform files
dx-agentic-gen check                       # Verify no drift
```

A pre-commit hook enforces that generated files stay in sync:
```bash
.deepx/tools/scripts/install-hooks.sh   # One-time setup
```

## Quick Start by Tool

### From dx-all-suite (Top-Level Routing)

If you are working at the top-level dx-all-suite directory and want the agent to
automatically route to the correct submodule:

**Prompt:**

```
"Compile yolo26n.onnx to DXNN and build a person detection Python app with it"
```

| Tool | How to Use |
|---|---|
| **Claude Code** | Open `dx-all-suite/` and type the prompt. `CLAUDE.md` routes to dx-compiler for compilation and dx_app for app generation. |
| **GitHub Copilot** | Open Copilot Chat: `@dx-suite-builder` followed by the prompt. The agent classifies the task and routes to the correct submodules. |
| **Cursor** | Open `dx-all-suite/` and type the prompt. The `alwaysApply` rule routes to the appropriate submodules. |
| **OpenCode** | Open `dx-all-suite/`: `@dx-suite-builder` followed by the prompt. The agent routes automatically. |
| **Codex CLI** | Open `dx-all-suite/` and type the prompt (or `~/bin/codex exec "<prompt>"`). `AGENTS.md` is read automatically and routes across submodules. |

### From a Submodule (Direct Access)

When working directly in a submodule, use prompts tailored to that submodule's scope:

| Submodule | Example Prompt |
|---|---|
| **dx-compiler** | `"Convert my yolo26x.pt to ONNX and compile it to DXNN for DX-M1"` |
| **dx_app** | `"Build a yolo26n person detection app using Python"` |
| **dx_stream** | `"Build a detection pipeline with RTSP camera and tracking"` |

| Tool | How to Use |
|---|---|
| **Claude Code** | Open the submodule directory and type the prompt directly. `CLAUDE.md` is read automatically. The Context Routing Table dispatches to the correct `.deepx/` skill files. |
| **GitHub Copilot** | Open Copilot Chat: `@dx-app-builder`, `@dx-stream-builder`, or `@dx-compiler-builder` followed by the prompt. Copilot reads `.github/copilot-instructions.md` on every chat. |
| **Cursor** | Open the submodule folder and type the prompt directly. Rules with `alwaysApply: true` are loaded on every conversation. Rules with `globs:` patterns activate when editing matching files. |
| **OpenCode** | Open the submodule directory and use the appropriate agent (`@dx-app-builder`, `@dx-stream-builder`, or `@dx-compiler-builder`) or the corresponding skill slash command. |
| **Codex CLI** | Open the submodule directory and type the prompt (or `~/bin/codex exec "<prompt>"`). `AGENTS.md` is read automatically; `cat` the relevant `.deepx/skills/<name>/SKILL.md` directly as needed. |

## End-to-End Scenarios

These scenarios demonstrate cross-project workflows that span multiple submodules.
For sub-project-specific scenarios, see the individual guides linked below.

### Scenario 1: Custom Model Conversion + SDK Porting + Validation

A full pipeline that compiles a custom model, ports inference code to the DEEPX SDK,
and validates the result.

**Prompt:**

```
"I have yolo26x-custom.onnx at ./models/ and my inference code at ./inference.py using onnxruntime. Convert it to DXNN and port my code to DEEPX SDK."
```

| Tool | How to Use |
|---|---|
| **Claude Code** | Open `dx-all-suite/` and type the prompt. The suite builder orchestrates: (a) dx-compiler compiles the ONNX model to DXNN, (b) dx_app ports the inference code, (c) validation confirms the ported app works. |
| **GitHub Copilot** | `@dx-suite-builder` followed by the prompt. The agent routes compilation to dx-compiler and porting to dx_app. |
| **Cursor** | Open `dx-all-suite/` and type the prompt. The router dispatches to the correct submodules. |
| **OpenCode** | `@dx-suite-builder` followed by the prompt. |
| **Codex CLI** | Open `dx-all-suite/` and type the prompt. `AGENTS.md` orchestrates the cross-submodule work. |

This scenario involves three stages:
1. **dx-compiler**: Compile `yolo26x-custom.onnx` → `yolo26x-custom.dxnn` with auto-inferred config
2. **dx_app**: Generate Python inference app using `InferenceEngine` with the compiled model
3. **Validation**: Run the ported app and compare outputs against the original onnxruntime code

### Scenario 2: Model Compilation + Sample App Generation

Compile a model and generate a standalone inference app that uses the compiled output.
This cross-project scenario spans dx-compiler and dx_app.

**Prompt:**

```
"Compile yolo26n.onnx to DXNN and generate a Python detection app that uses the compiled model"
```

| Tool | How to Use |
|---|---|
| **Claude Code** | Open `dx-all-suite/` and type the prompt. The suite builder orchestrates: (a) dx-compiler compiles ONNX to DXNN, (b) dx_app generates a Python app referencing the compiled model. |
| **GitHub Copilot** | `@dx-suite-builder` followed by the prompt. Routes compilation to dx-compiler and app generation to dx_app. |
| **Cursor** | Open `dx-all-suite/` and type the prompt. The router dispatches to both submodules. |
| **OpenCode** | `@dx-suite-builder` followed by the prompt. |
| **Codex CLI** | Open `dx-all-suite/` and type the prompt. `AGENTS.md` orchestrates the cross-submodule work. |

This scenario involves two stages:
1. **dx-compiler**: Compile `yolo26n.onnx` → `yolo26n.dxnn` with auto-inferred config
2. **dx_app**: Generate a Python detection app using the compiled `.dxnn` model

### Scenario 3: Model Compilation + Streaming Pipeline Generation

Compile a model and generate a GStreamer streaming pipeline that uses the compiled output.
This cross-project scenario spans dx-compiler and dx_stream.

**Prompt:**

```
"Compile yolo26n.onnx to DXNN and build a detection streaming pipeline with RTSP output"
```

| Tool | How to Use |
|---|---|
| **Claude Code** | Open `dx-all-suite/` and type the prompt. The suite builder orchestrates: (a) dx-compiler compiles ONNX to DXNN, (b) dx_stream generates a GStreamer pipeline with RTSP output. |
| **GitHub Copilot** | `@dx-suite-builder` followed by the prompt. Routes compilation to dx-compiler and pipeline to dx_stream. |
| **Cursor** | Open `dx-all-suite/` and type the prompt. The router dispatches to both submodules. |
| **OpenCode** | `@dx-suite-builder` followed by the prompt. |
| **Codex CLI** | Open `dx-all-suite/` and type the prompt. `AGENTS.md` orchestrates the cross-submodule work. |

This scenario involves two stages:
1. **dx-compiler**: Compile `yolo26n.onnx` → `yolo26n.dxnn` with auto-inferred config
2. **dx_stream**: Generate a detection pipeline with DxInfer using the compiled model and RTSP streaming output

### Scenario 4: PPU Model Compilation + Detection App

Compile a YOLO model with PPU (Pre/Post Processing Unit) support for hardware-accelerated
post-processing, then generate an app that uses the PPU model.

**Prompt:**

```
"Compile yolo26n.onnx with PPU support and generate a detection app for the PPU model"
```

| Tool | How to Use |
|---|---|
| **Claude Code** | Open `dx-all-suite/` and type the prompt. The suite builder orchestrates: (a) dx-compiler compiles with PPU config (auto-detected type based on YOLO version), (b) dx_app generates a PPU-specific app with simplified postprocessing. |
| **GitHub Copilot** | `@dx-suite-builder` followed by the prompt. Routes to dx-compiler for PPU compilation and dx_app for PPU app generation. |
| **Cursor** | Open `dx-all-suite/` and type the prompt. The router dispatches to both submodules. |
| **OpenCode** | `@dx-suite-builder` followed by the prompt. |
| **Codex CLI** | Open `dx-all-suite/` and type the prompt. `AGENTS.md` orchestrates the cross-submodule work. |

This scenario involves two stages:
1. **dx-compiler**: Compile with PPU config — the agent auto-detects PPU type (Type 0 for anchor-based YOLO, Type 1 for anchor-free YOLO)
2. **dx_app**: Generate a PPU-specific detection app under `src/python_example/ppu/` with simplified postprocessing (bounding boxes decoded by hardware)

## Cross-Project Routing

The dx-all-suite meta guide provides routing to all sub-project scenarios. If your
task matches a scenario in a sub-project guide, the suite builder will route you
there automatically.

- **dx-runtime scenarios** (cross-project builds, unified validation): See the [dx-runtime guide](../../../dx-runtime/docs/source/agentic_development.md)
- **dx_app scenarios** (Python/C++ inference apps): See the [dx_app guide](../../../dx_app/docs/source/docs/12_DX-APP_Agentic_Development.md)
- **dx_stream scenarios** (GStreamer pipelines): See the [dx_stream guide](../../../dx_stream/docs/source/docs/08_DX-STREAM_Agentic_Development.md)
- **dx-compiler scenarios** (model compilation): See the [dx-compiler guide](../../dx-compiler/source/docs/05_DX-COMPILER_Agentic_Development.md)

> **Tip:** You don't need to navigate to sub-project directories. Use `@dx-suite-builder`
> at the dx-all-suite level — it routes to any sub-project automatically.

## Sub-Project Guides

Each sub-project has a detailed agentic development guide covering its specific
skills, element catalogs, and worked examples:

| Sub-Project | Guide |
|---|---|
| **dx-runtime** | [`dx-runtime/docs/source/agentic_development.md`](../../../dx-runtime/docs/source/agentic_development.md) |
| **dx_app** | [`dx_app/docs/source/docs/12_DX-APP_Agentic_Development.md`](../../../dx_app/docs/source/docs/12_DX-APP_Agentic_Development.md) |
| **dx_stream** | [`dx_stream/docs/source/docs/08_DX-STREAM_Agentic_Development.md`](../../../dx_stream/docs/source/docs/08_DX-STREAM_Agentic_Development.md) |
| **dx-compiler** | [`dx-compiler/source/docs/05_DX-COMPILER_Agentic_Development.md`](../../dx-compiler/source/docs/05_DX-COMPILER_Agentic_Development.md) |

## Internal Reference Documents

For a deeper view of the `.deepx/` canonical source, generator pipeline, and
harness development model (intended for contributors, not end users):

| Document | Scope |
|---|---|
| [`.deepx/docs/dx-agentic-dev-overview.md`](../../.deepx/docs/dx-agentic-dev-overview.md) | Comprehensive walk-through of every `.deepx/` directory across all 5 repos |
| [`.deepx/README.md`](../../.deepx/README.md) | Top-level master index for the `.deepx/` knowledge base |
| [`.deepx/docs/skill-architecture.md`](../../.deepx/docs/skill-architecture.md) | 3-tier skill model (SWE / Agentic / Harness) |
| [`.deepx/tools/README.md`](../../.deepx/tools/README.md) | `dx-agentic-gen` generator package guide |
| [`.deepx/tools/scripts/README.md`](../../.deepx/tools/scripts/README.md) | Operational scripts (`run_all.sh`, hooks, E2E loop) |

## Output Isolation

By default, all agent-generated code is placed in `dx-agentic-dev/<session_id>/`
within the target sub-project. This prevents accidental modifications to existing
production code.

| Output Type | Path | When |
|---|---|---|
| **Default (isolated)** | `dx-agentic-dev/<session_id>/` | Always, unless user says otherwise |
| **Production** | `src/` | Only when explicitly requested by the user |

Session ID format: `YYYYMMDD-HHMMSS_<agent>_<model>_<task>` where `<agent>` is `claude`, `codex`, `copilot`, `cursor`, or `opencode`.

Each session directory contains:
- `README.md` — session metadata, generated file list, run instructions
- `session.json` — machine-readable session configuration

The `dx-agentic-dev/` directory is git-ignored in both dx_app and dx_stream.

### dx-compiler Session Directories

For dx-compiler, session directories additionally contain:
- `calibration_dataset` — symlink to `dx_com/calibration_dataset/`
- `config.json` — auto-generated DX-COM config with relative calibration path
- `compiler.log` — compilation log (when `--gen_log` is used)

The agent automatically sets up calibration data (checking `dx_com/calibration_dataset/`,
running setup scripts if needed, and creating symlinks with relative paths).

### Suite-Level Cross-Project Output

When running cross-project tasks from the dx-all-suite level (e.g., compile + deploy),
artifacts are created in each target sub-project's `dx-agentic-dev/` directory.
Additionally, symbolic links are created in `dx-all-suite/dx-agentic-dev/` for
unified access:

```
dx-all-suite/dx-agentic-dev/
├── dx-compiler_20260409-070940_yolo26n_pt_to_dxnn -> ../dx-compiler/dx-agentic-dev/20260409-...
└── dx_app_20260409-071500_yolo26n_detection_app -> ../dx-runtime/dx_app/dx-agentic-dev/20260409-...
```

Symlink naming convention: `{subproject}_{session_id}`.

## Session Sentinels

Agents output fixed markers at the start and end of each task for automated testing:

| Marker | When |
|---|---|
| `[DX-AGENTIC-DEV: START]` | **CRITICAL** — Absolute first line of the agent's first response, before ANY other text, tool calls, or reasoning. Non-negotiable even if the user says "just proceed" — automated tests WILL fail without it. |
| `[DX-AGENTIC-DEV: DONE (output-dir: <relative_path>)]` | Last line after all work is complete. `<relative_path>` is the session output directory relative to the project root. If no files were generated, omit the `(output-dir: ...)` part. |

**Important**: DONE means all deliverables are produced — implementation code, scripts,
configs, and validation results. If the agent only produced planning artifacts (specs,
plans, design documents) without implementing actual code, DONE must NOT be output.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Agent cannot find `.dxnn` model | Model name or architecture mismatch | Verify the model exists in `resources/models/` and matches your target chip (DX-M1, DX-H1) |
| `DxInfer` element reports "device not found" | DX-RT SDK not loaded or device not connected | Run `source setup_env.sh` and confirm `dx-rt list-devices` shows your accelerator |
| Pipeline starts but produces black frames | Camera source misconfigured | Use `--input usb` for auto-detection instead of hardcoding a `/dev/video` path |
| Agent generates code for the wrong sub-project | Ambiguous prompt | Use `@dx-suite-builder` at the top level for automatic routing, or prefix with the target builder name, e.g. `@dx-stream-builder` or `@dx-app-builder` |
| Compilation fails with "unsupported opset" | ONNX opset version outside 11-21 range | Re-export the model with `opset_version=17` |
| Compiled DXNN has low accuracy | Calibration data not representative | Use real inference images and increase `calibration_num` to 200+ |
| Agent skips mandatory questions | HARD-GATE enforcement not in agent instructions | Ensure agent files include `<HARD-GATE>` tags around mandatory question sections |
