# DEEPX Agent-Driven Development - dx-agent-dev (Beta)

!!! note "Beta Feature"  

    Agent-Driven development support is under active development.  
    Skill definitions and routing behavior may change between releases.  

## Introduction

<!-- intro -->
<!-- dx-showcase:docs:intro:start -->
**`dx-agent-dev` (Beta) is here.** Describe the app or model task in plain language and an AI coding agent — Claude Code, Cursor, GitHub Copilot, OpenCode, or Codex — drives the DEEPX knowledge base end to end: brainstorm → plan → TDD → verify, from ONNX/`.pt` compilation to on-device DX-M1 NPU deployment. It is agent-driven development purpose-built for DEEPX NPUs in the **Ultralytics** model ecosystem, and every showcase below was produced this way — checked in with its prompt, measured results, and full build transcript.
<!-- dx-showcase:docs:intro:end -->

Build DEEPX AI applications using natural language instructions. AI coding agents
understand the DEEPX SDK ecosystem — GStreamer pipeline construction, `.dxnn` model
resolution, InferenceEngine configuration, and DxPreprocess/DxInfer element wiring —
so you can describe *what* you want and let the agent handle the implementation details.

Supported workflows include:

- Standalone inference apps with `IFactory`, `SyncRunner`, and `AsyncRunner`
- GStreamer video pipelines using DEEPX's 13 custom elements across 6 categories
- Cross-project builds that span dx_app, dx_stream, and dx-runtime
- Model compilation from ONNX to DXNN format using DX-COM (in dx-compiler)

## Showcases

Every showcase below is a real app built on the DEEPX NPU SDK from a **single
natural-language prompt** — fully autonomously — and checked into the suite with the
prompt, measured results, a one-command reproduce, and the full recorded build-session
transcript.

<!-- showcase-table -->
<!-- dx-showcase:docs:table:start -->
#### NPU-powered AI apps (mini-games)

**Build a fully autonomous DEEPX-NPU app from natural language — in ~20 minutes, for ~$10.** Pose-driven mini-games with arcade HUDs, built end to end from a single prompt.

| Showcase | What it is | Build time | Agent turns | Output tokens | ~Cost |
|---|---|---|---|---|---|
| **[Squat-Counting Mini-Game](../../dx-agent-dev-showcase/mini-game-squat-fitness/)** | Counts squat reps from knee/hip angles with an arcade HUD (reps / score / DOWN·UP·GOOD!). | ≈ 12 min | 132 | ≈ 109K | ≈ $7.3 |
| **[Stretching Coach Mini-Game](../../dx-agent-dev-showcase/mini-game-stretching-coach/)** | Guides 3 stretches with an animated coach avatar that demonstrates each target pose. | ≈ 15 min | 130 | ≈ 142K | ≈ $8.1 |

#### Ultralytics ecosystem integration

**Take any Ultralytics YOLO to the DEEPX NPU in one command — or retrain it for your domain — all in natural language.** `format=deepx` export + 4-way eval (base/retrained × fp32-GPU / INT8-NPU); INT8 ≈ fp32, and the domain model runs faster on the NPU.

| Showcase | What it is | Build time | Agent turns | Output tokens | ~Cost |
|---|---|---|---|---|---|
| **[Ultralytics YOLO → DeepX Export](../../dx-agent-dev-showcase/ultralytics-yolo-deepx-export/)** | Turns an Ultralytics YOLO `.pt` into a deployable DeepX NPU model (`.dxnn`) in a single `yolo export ... format=deepx` command, then runs NPU inference + verify. | ≈ 12 min | 108 | ≈ 84K | ≈ $2.4 |
| **[African Wildlife Monitoring](../../dx-agent-dev-showcase/ultralytics-retrain-eval-deepx-export-wildlife/)** | Retrains `yolo26n` on `african-wildlife` (buffalo/elephant/rhino/zebra) for a safari/conservation camera; 4-way eval base/retrained × fp32/INT8. | ≈ 7 min | 78 | ≈ 85K | ≈ $3.2 |
| **[Construction PPE Safety](../../dx-agent-dev-showcase/ultralytics-retrain-eval-deepx-export-ppe/)** | Retrains `yolo26n` on `construction-ppe` for a site-safety camera (helmet/vest/...); 4-way eval base/retrained × fp32/INT8. | ≈ 17 min | 102 | ≈ 93K | ≈ $4.0 |
| **[Brain-Tumor Screening](../../dx-agent-dev-showcase/ultralytics-retrain-eval-deepx-export-braintumor/)** | Retrains `yolo26n` on `brain-tumor` (MRI/CT) for a medical edge device; 4-way eval base/retrained × fp32/INT8. | ≈ 9 min | 91 | ≈ 103K | ≈ $3.7 |
| **[Pharmaceutical Pill Inspection](../../dx-agent-dev-showcase/ultralytics-retrain-eval-deepx-export-pills/)** | Retrains `yolo26n` on `medical-pills` for a pharma counting station; 4-way eval base/retrained × fp32/INT8. | ≈ 8 min | 118 | ≈ 103K | ≈ $5.1 |

#### PaddlePaddle ecosystem integration

**PaddleOCR (PP-OCRv5) on the DEEPX NPU — real-time video & webcam OCR from a single, concise prompt.** Baidu's PaddlePaddle OCR (text detection → orientation → recognition) running on the DX-M1 NPU.

| Showcase | What it is | Build time | Agent turns | Output tokens | ~Cost |
|---|---|---|---|---|---|
| **[Video / Webcam OCR (PP-OCRv5)](../../dx-agent-dev-showcase/paddleocr-video-ocr/)** | Real-time text detection + recognition on the DX-M1 NPU — one code path for a video file and a live webcam, overlaying detected boxes + recognized strings. | ≈ 18 min | 175 | ≈ 184K | ≈ $12.0 |

#### RapidAI ecosystem integration

**A PDF → Markdown document-conversion app on the DEEPX NPU — from a single, concise natural-language prompt.** RapidAI's RapidDoc (PP-StructureV3): layout, OCR, tables, formulas — running PaddlePaddle-trained models on the DX-M1 NPU. A standalone, self-contained app generated from the fork's pipeline.

| Showcase | What it is | Build time | Agent turns | Output tokens | ~Cost |
|---|---|---|---|---|---|
| **[PDF → Markdown (document conversion app)](../../dx-agent-dev-showcase/rapiddoc-pdf2md/)** | Converts a PDF (digital or scanned) to structured Markdown + JSON — layout analysis, OCR, tables and formulas — on the DEEPX DX-M1 NPU via the RapidDoc fork. Supports `--parse-method auto|txt|ocr`. | ≈ 12 min | 133 | ≈ 148.5K | ≈ $6.2 |
<!-- dx-showcase:docs:table:end -->

**Full catalog + per-showcase summaries (with build GIFs) →**
[`dx-agent-dev-showcase/README.md`](../../dx-agent-dev-showcase/README.md). Each row's
link opens that showcase's own README — the verbatim prompt, the 4-way eval / gameplay
detail, and its session transcript.

### How it works — the harness, not (just) the model

Each app ships its **complete agent session transcript**, the most direct way to see that
the result comes less from the raw model and more from the **instructions, skills, and
verification gates** the harness imposes. Reading a transcript you can watch:

- **Instruction-following** — the agent honors the suite HARD GATES: session sentinels
  (`[DX-AGENT-DEV: START]` / `DONE`), output isolated to a session directory (never
  touching existing source), and no placeholder/stub code.
- **Skill & agent utilization** — it invokes the mandatory sequence as real tool calls —
  `dx-skill-router → dx-agent-brainstorm → dx-swe-writing-plans → dx-agent-tdd →
  dx-agent-verify` — rather than just *mentioning* them.
- **Actual reasoning** — inspecting the closest existing example, confirming real
  framework APIs from the knowledge base, writing validation first (RED), then
  generating + verifying file-by-file before declaring done.

## Prerequisites

| Requirement | Details |
|---|---|
| **DEEPX development environment** | DX-RT SDK installed and `setup_env.sh` sourced |
| **AI coding agent** (one of) | Claude Code, GitHub Copilot (VS Code), Cursor, OpenCode, or Codex CLI |
| **Python** | 3.10+ with the dx-all-suite packages installed |

## Architecture Overview

The agent-driven knowledge base is organized into three independent layers. Each layer
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
| **dx-runtime** | `/dx-agent-runtime-validate` | Validate, collect feedback, apply fixes, verify |
| **dx_app** | `/dx-agent-app-build-python` | Build Python inference app |
| **dx_app** | `/dx-agent-app-build-cpp` | Build C++ inference app |
| **dx_app** | `/dx-agent-app-build-async` | Build async high-performance app |
| **dx_app** | `/dx-agent-app-model-management` | Download and configure models |
| **dx_app** | `/dx-agent-app-validate` | Run validation checks |
| **dx_stream** | `/dx-agent-stream-build-pipeline` | Build GStreamer pipeline app |
| **dx_stream** | `/dx-agent-stream-build-mqtt-kafka` | Build MQTT/Kafka pipeline app |
| **dx_stream** | `/dx-agent-stream-validate` | Run validation checks |
| **dx_stream** | `/dx-agent-stream-model-management` | Download and configure models |
| **dx-compiler** | `/dx-agent-compiler-convert` | Convert PyTorch model to ONNX |
| **dx-compiler** | `/dx-agent-compiler-compile` | Compile ONNX model to DXNN |
| **dx-compiler** | `/dx-agent-compiler-validate` | Validate compiled DXNN output |
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

!!! note "Tip"  

    If you are unsure which submodule to target, use `@dx-suite-builder` at the top level — it will classify your task and route to the correct builder.  

## Supported AI Tools

Agent-Driven development works with five AI coding tools. Each tool auto-loads
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

!!! note "Git submodule boundary*"  

    Copilot Chat/CLI, Claude Code, and Codex CLI only see files at the current git root. When opened at `dx-all-suite/`, they do NOT auto-load sub-project files in `dx-compiler/`, `dx-runtime/`, etc. (these are separate git submodules). OpenCode bridges this boundary via explicit path references in `opencode.json`.  

#### Auto-Loaded Files

| File | Auto-loaded by | Loading |
|------|----------------|---------|
| `.github/copilot-instructions.md` | Copilot Chat/CLI | Auto |
| `CLAUDE.md` | Claude Code | Auto |
| `AGENTS.md` + `opencode.json` | OpenCode | Auto |
| `AGENTS.md` + `.codex/skills/dx-codex-identity/SKILL.md` | Codex CLI | Auto |
| `.cursor/rules/dx-all-suite.mdc` | Cursor | Auto |

#### Agent Files (Manual @mention)

| Agent | Copilot (`@mention`) | OpenCode (`@mention`) |
|-------|------|---------|
| `dx-suite-builder` | `.github/agents/dx-suite-builder.agent.md` | `.opencode/agents/dx-suite-builder.md` |
| `dx-suite-validator` | `.github/agents/dx-suite-validator.agent.md` | `.opencode/agents/dx-suite-validator.md` |

!!! note "NOTE"  

    Claude Code has generated agent files in `.claude/agents/` (e.g., `dx-suite-builder.md`).  
    Cursor has agent `.mdc` files in `.cursor/rules/` (e.g., `dx-suite-builder.mdc`).  
    Claude Code also uses the Context Routing Table in `CLAUDE.md` to dispatch tasks.  

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
platform-agnostic format. The `dx-agent-gen` generator transforms this into
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

All platform-specific files are generated from `.deepx/` by the `dx-agent-dev-gen`
package. Never edit generated files directly.

```bash
pip install -e .deepx/tools   # Install generator
dx-agent-gen generate                    # Generate platform files
dx-agent-gen check                       # Verify no drift
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

- **dx-runtime scenarios** (cross-project builds, unified validation): See the [dx-runtime guide](../../../dx-runtime/docs/source/agent_development.md)
- **dx_app scenarios** (Python/C++ inference apps): See the [dx_app guide](../../../dx_app/docs/source/docs/12_DX-APP_Agent_Driven_Development.md)
- **dx_stream scenarios** (GStreamer pipelines): See the [dx_stream guide](../../../dx_stream/docs/source/docs/08_DX-STREAM_Agent_Driven_Development.md)
- **dx-compiler scenarios** (model compilation): See the [dx-compiler guide](../../dx-compiler/source/docs/05_DX-COMPILER_Agent_Driven_Development.md)

!!! note "Tip"  

    You don't need to navigate to sub-project directories. Use `@dx-suite-builder` at the dx-all-suite level — it routes to any sub-project automatically.  

## Sub-Project Guides

Each sub-project has a detailed agent-driven development guide covering its specific
skills, element catalogs, and worked examples:

| Sub-Project | Guide |
|---|---|
| **dx-runtime** | [`dx-runtime/docs/source/agent_development.md`](../../../dx-runtime/docs/source/agent_development.md) |
| **dx_app** | [`dx_app/docs/source/docs/12_DX-APP_Agent_Driven_Development.md`](../../../dx_app/docs/source/docs/12_DX-APP_Agent_Driven_Development.md) |
| **dx_stream** | [`dx_stream/docs/source/docs/08_DX-STREAM_Agent_Driven_Development.md`](../../../dx_stream/docs/source/docs/08_DX-STREAM_Agent_Driven_Development.md) |
| **dx-compiler** | [`dx-compiler/source/docs/05_DX-COMPILER_Agent_Driven_Development.md`](../../dx-compiler/source/docs/05_DX-COMPILER_Agent_Driven_Development.md) |

## Internal Reference Documents

For a deeper view of the `.deepx/` canonical source, generator pipeline, and
harness development model (intended for contributors, not end users):

| Document | Scope |
|---|---|
| [`.deepx/docs/dx-agent-dev-overview.md`](../../.deepx/docs/dx-agent-dev-overview.md) | Comprehensive walk-through of every `.deepx/` directory across all 5 repos |
| [`.deepx/README.md`](../../.deepx/README.md) | Top-level master index for the `.deepx/` knowledge base |
| [`.deepx/docs/skill-architecture.md`](../../.deepx/docs/skill-architecture.md) | 3-tier skill model (SWE / Agent-Driven / Harness) |
| [`.deepx/tools/README.md`](../../.deepx/tools/README.md) | `dx-agent-gen` generator package guide |
| [`.deepx/tools/scripts/README.md`](../../.deepx/tools/scripts/README.md) | Operational scripts (`run_all.sh`, hooks, E2E loop) |

## Output Isolation

By default, all agent-generated code is placed in `dx-agent-dev/<session_id>/`
within the target sub-project. This prevents accidental modifications to existing
production code.

| Output Type | Path | When |
|---|---|---|
| **Default (isolated)** | `dx-agent-dev/<session_id>/` | Always, unless user says otherwise |
| **Production** | `src/` | Only when explicitly requested by the user |

Session ID format: `YYYYMMDD-HHMMSS_<agent>_<model>_<task>` where `<agent>` is `claude`, `codex`, `copilot`, `cursor`, or `opencode`.

Each session directory contains:
- `README.md` — session metadata, generated file list, run instructions
- `session.json` — machine-readable session configuration

The `dx-agent-dev/` directory is git-ignored in both dx_app and dx_stream.

### dx-compiler Session Directories

For dx-compiler, session directories additionally contain:
- `calibration_dataset` — symlink to `dx_com/calibration_dataset/`
- `config.json` — auto-generated DX-COM config with relative calibration path
- `compiler.log` — compilation log (when `--gen_log` is used)

The agent automatically sets up calibration data (checking `dx_com/calibration_dataset/`,
running setup scripts if needed, and creating symlinks with relative paths).

### Suite-Level Cross-Project Output

When running cross-project tasks from the dx-all-suite level (e.g., compile + deploy),
artifacts are created in each target sub-project's `dx-agent-dev/` directory.
Additionally, symbolic links are created in `dx-all-suite/dx-agent-dev/` for
unified access:

```
dx-all-suite/dx-agent-dev/
├── dx-compiler_20260409-070940_yolo26n_pt_to_dxnn -> ../dx-compiler/dx-agent-dev/20260409-...
└── dx_app_20260409-071500_yolo26n_detection_app -> ../dx-runtime/dx_app/dx-agent-dev/20260409-...
```

Symlink naming convention: `{subproject}_{session_id}`.

## Session Sentinels

Agents output fixed markers at the start and end of each task for automated testing:

| Marker | When |
|---|---|
| `[DX-AGENT-DEV: START]` | **CRITICAL** — Absolute first line of the agent's first response, before ANY other text, tool calls, or reasoning. Non-negotiable even if the user says "just proceed" — automated tests WILL fail without it. |
| `[DX-AGENT-DEV: DONE (output-dir: <relative_path>)]` | Last line after all work is complete. `<relative_path>` is the session output directory relative to the project root. If no files were generated, omit the `(output-dir: ...)` part. |

**Important**: DONE means all deliverables are produced — implementation code, scripts,
configs, and validation results. If the agent only produced planning artifacts (specs,
plans, design documents) without implementing actual code, DONE must NOT be output.

---
