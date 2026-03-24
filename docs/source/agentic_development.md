# AI-Powered Development (Beta)

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

## Prerequisites

| Requirement | Details |
|---|---|
| **DEEPX development environment** | DX-RT SDK installed and `setup_env.sh` sourced |
| **AI coding agent** (one of) | Claude Code, GitHub Copilot (VS Code), Cursor, or OpenCode |
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

DXNN model compilation powered by DX-COM v2.2.1. The agent understands the full
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
| **dx-all-suite** | `/dx-validate-all` | Full validation across all 3 levels |
| **dx-runtime** | `/dx-validate-and-fix` | Validate, collect feedback, apply fixes, verify |
| **dx_app** | `/dx-build-python-app` | Build Python inference app |
| **dx_app** | `/dx-build-cpp-app` | Build C++ inference app |
| **dx_app** | `/dx-build-async-app` | Build async high-performance app |
| **dx_app** | `/dx-model-management` | Download and configure models |
| **dx_app** | `/dx-validate` | Run validation checks |
| **dx_stream** | `/dx-build-pipeline-app` | Build GStreamer pipeline app |
| **dx_stream** | `/dx-build-mqtt-kafka-app` | Build MQTT/Kafka pipeline app |
| **dx_stream** | `/dx-validate` | Run validation checks |
| **dx_stream** | `/dx-model-management` | Download and configure models |
| **dx-compiler** | `/dx-convert-model` | Convert PyTorch model to ONNX |
| **dx-compiler** | `/dx-compile-model` | Compile ONNX model to DXNN |
| **dx-compiler** | `/dx-validate-compile` | Validate compiled DXNN output |
| **DX All Suite** | `/dx-brainstorm-and-plan` | Process: collaborative design session before any work |
| **DX All Suite** | `/dx-tdd` | Process: test-driven development — validate incrementally |
| **DX All Suite** | `/dx-verify-completion` | Process: verify before claiming completion — evidence before assertions |
| **dx-runtime** | `/dx-brainstorm-and-plan` | Process: collaborative design session before code generation |
| **dx-runtime** | `/dx-tdd` | Process: test-driven development — validate each file immediately after creation |
| **dx-runtime** | `/dx-verify-completion` | Process: verify before claiming completion — evidence before assertions |
| **dx_app** | `/dx-brainstorm-and-plan` | Process: collaborative design session before code generation |
| **dx_app** | `/dx-tdd` | Process: test-driven development — validate each file immediately after creation |
| **dx_app** | `/dx-verify-completion` | Process: verify before claiming completion — evidence before assertions |
| **dx_stream** | `/dx-brainstorm-and-plan` | Process: collaborative design session before code generation |
| **dx_stream** | `/dx-tdd` | Process: test-driven development — validate each file immediately after creation |
| **dx_stream** | `/dx-verify-completion` | Process: verify before claiming completion — evidence before assertions |
| **dx-compiler** | `/dx-brainstorm-and-plan` | Process: collaborative design session before compilation |
| **dx-compiler** | `/dx-tdd` | Process: test-driven development — validate each step incrementally |
| **dx-compiler** | `/dx-verify-completion` | Process: verify before claiming completion — evidence before assertions |

> **Tip:** If you are unsure which submodule to target, use `@dx-suite-builder`
> at the top level — it will classify your task and route to the correct builder.

## Supported AI Tools

Agentic development works with four AI coding tools. Each tool auto-loads
the `.deepx/` knowledge base through its own configuration mechanism.

| Tool | Type | Auto-Load Mechanism | Agent Invocation | Skill Invocation |
|---|---|---|---|---|
| **Claude Code** | CLI | `CLAUDE.md` at project root | Free-form conversation; Context Routing Table dispatches automatically | — |
| **GitHub Copilot** | VS Code | `.github/copilot-instructions.md` | `@agent-name "prompt"` in Copilot Chat | — |
| **Cursor** | IDE | `.cursor/rules/*.mdc` | Free-form conversation; rules loaded by `alwaysApply` or `globs` | — |
| **OpenCode** | CLI | `AGENTS.md` + `opencode.json` | `@agent-name "prompt"` | `/skill-name` slash command |

### What Gets Auto-Loaded

| Tool | Global Context | File-Specific Context | Agents | Skills |
|---|---|---|---|---|
| Claude Code | `CLAUDE.md` | Context Routing Table (manual) | Built into `CLAUDE.md` routing | `.deepx/skills/` (read directly) |
| Copilot | `.github/copilot-instructions.md` | `.github/instructions/*.instructions.md` (`applyTo:` glob) | `.github/agents/*.agent.md` | — |
| Cursor | `.cursor/rules/dx-*.mdc` (`alwaysApply: true`) | `.cursor/rules/*.mdc` (`globs: [...]`) | — | — |
| OpenCode | `AGENTS.md` + `opencode.json` instructions | — | `.opencode/agents/*.md` | `.opencode/skills/*/SKILL.md` |

### First-Time Setup

No additional configuration is needed. Open the project directory in your
preferred tool and the configuration files are loaded automatically:

```bash
# Claude Code
cd dx-all-suite/dx-runtime/dx_app
claude

# OpenCode
cd dx-all-suite/dx-runtime/dx_app
opencode

# GitHub Copilot — open folder in VS Code
code dx-all-suite/dx-runtime/dx_app

# Cursor — open folder in Cursor
cursor dx-all-suite/dx-runtime/dx_app
```

### Platform File Loading Reference

Each AI coding agent auto-loads different configuration files at the suite level.
Files marked **Auto** are loaded on every conversation; **@mention** files are invoked
manually via agent or skill commands.

> **Git submodule boundary**: Copilot Chat/CLI and Claude Code only see files at
> the current git root. When opened at `dx-all-suite/`, they do NOT auto-load
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

> Claude Code and Cursor do not have a separate agent system at this level.
> Claude Code uses the Context Routing Table in `CLAUDE.md` to dispatch tasks.

#### Skill Files (OpenCode Only — `/slash-command`)

| Skill | File |
|-------|------|
| `/dx-brainstorm-and-plan` | `.opencode/skills/dx-brainstorm-and-plan/SKILL.md` |
| `/dx-verify-completion` | `.opencode/skills/dx-verify-completion/SKILL.md` |
| `/dx-validate-all` | `.opencode/skills/dx-validate-all/SKILL.md` |
| `/dx-tdd` | `.opencode/skills/dx-tdd/SKILL.md` |

#### Shared Knowledge Base (`.deepx/`)

No `.deepx/` directory exists at the suite level. Suite-level instruction files
(`CLAUDE.md`, `copilot-instructions.md`, `AGENTS.md`) duplicate critical sub-project
rules inline to compensate for git submodule visibility limitations.

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

## Output Isolation

By default, all AI-generated code is placed in `dx-agentic-dev/<session_id>/`
within the target sub-project. This prevents accidental modifications to existing
production code.

| Output Type | Path | When |
|---|---|---|
| **Default (isolated)** | `dx-agentic-dev/<session_id>/` | Always, unless user says otherwise |
| **Production** | `src/` | Only when explicitly requested by the user |

Session ID format: `YYYYMMDD-HHMMSS_model_task`.

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

These markers are used by `test.sh agentic-e2e-manual` for automatic session
termination and `/share html` (Copilot CLI only) transcript saving. Sub-agents invoked via handoff
do not output sentinels — only the top-level agent does.

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
