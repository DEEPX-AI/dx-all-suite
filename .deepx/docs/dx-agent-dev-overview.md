# DEEPX Agent-Driven Development - dx-agent-dev (Beta) — `.deepx/` Structure Comprehensive Guide

> Basis: static analysis of the `.deepx/` directories across the 5 repos — dx-all-suite, dx-runtime, dx_app, dx_stream, dx-compiler
> Date: 2026-05-12 · Branch: `merge2.3.2/dx-agent-dev`

---

## 0. One-line Summary

The DEEPX Agent-Driven Development (dx-agent-dev) feature treats **`.deepx/` as the canonical source (SoT)**, and the `dx-agent-dev-gen` generator automatically produces files for 4 platforms — Claude Code / Copilot / Cursor / OpenCode — making it a **single-source / multi-target** architecture. The 5 repos (suite, runtime, dx_app, dx_stream, compiler) share the same skeleton (agents/, skills/, memory/, templates/, instructions/, toolsets/) while being specialized per domain, and 4 enforcement rules — **HARD GATE / Skill Router / Session Sentinel / Output Isolation** — automatically guarantee consistency.

---

## 1. DEEPX Agent-Driven Development (dx-agent-dev) Feature Overview

### 1.1 Core Concept

Generate DEEPX SDK-based AI applications from natural-language prompts. The AI agent understands the following:

- **dx_app**: IFactory · SyncRunner · AsyncRunner-based standalone inference (Python/C++)
- **dx_stream**: 13 GStreamer elements × 6 pipeline categories
- **dx-compiler**: ONNX → DXNN conversion (DX-COM, PPU auto-detection)
- **cross-project**: compile + app build + verification chain

### 1.2 Supported AI Tools (5 types)

| Tool | Auto-load mechanism | Agent invocation |
|------|---------------------|------------------|
| **Claude Code** | `CLAUDE.md` + `.claude/agents/` | natural language + Context Routing Table |
| **GitHub Copilot** | `.github/copilot-instructions.md` + `.github/agents/` | `@agent-name "prompt"` |
| **Cursor** | `.cursor/rules/*.mdc` (`alwaysApply` / `globs`) | natural language |
| **OpenCode** | `AGENTS.md` + `opencode.json` + `.opencode/agents/` + slash commands | `@agent-name` or `/skill-name` |
| **Codex CLI** | `AGENTS.md` + `.codex/skills/dx-codex-identity/SKILL.md` | `codex exec --json -s danger-full-access -m <model> -C <workdir>` (default model: `gpt-5.3-codex`, Copilot provider auth) |

### 1.3 Hierarchical Routing Structure

```
[dx-all-suite] dx-suite-builder (top-level classifier)
       ├── [dx-compiler]   dx-compiler-builder → model-converter / dxnn-compiler
       └── [dx-runtime]    dx-runtime-builder
                              ├── [dx_app]    dx-app-builder → python/cpp/benchmark/model-manager/validator
                              └── [dx_stream] dx-stream-builder → pipeline-builder / model-manager / validator
```

### 1.4 Output Isolation Rule (HARD GATE)

All AI-generated code is written under `dx-agent-dev/<session_id>/` (default). The only exception is when the user explicitly instructs writing to `src/`.

- Session ID format: `YYYYMMDD-HHMMSS_<agent>_<coding_model>_<target_model>_<task>` (system local timezone, UTC prohibited)
- `<agent>`: `claude` / `codex` / `copilot` / `cursor` / `opencode`
- `<coding_model>`: `sonnet46`, `opus46`, `gpt53codex`, `gpt55`
- Cross-project suite tasks require creation of **2 session directories** (R41 rule):
  - `dx-compiler/dx-agent-dev/<id>_compile/`
  - `dx-runtime/dx_app/dx-agent-dev/<id>_inference/`

### 1.5 Session Sentinels (for automated testing)

| Marker | Output position |
|--------|-----------------|
| `[DX-AGENT-DEV: START]` | the **absolute first line** of the first response |
| `[DX-AGENT-DEV: DONE (output-dir: <relative_path>)]` | the last line after all work, validation, and file generation is complete |

---

## 2. `.deepx/` Common Architecture

### 2.1 Single-Source → Multi-Platform Generation

```
.deepx/ (canonical source)
   ├── agents/      ←┐
   ├── skills/      ←┤
   ├── templates/   ←┤  dx-agent-gen generate
   ├── fragments/   ←┘
                          ↓
   ┌──────────────────────┼──────────────────────┐
   ↓                      ↓                      ↓
CLAUDE.md          .github/copilot-       .cursor/rules/*.mdc
AGENTS.md          instructions.md        (Cursor)
.claude/agents/    .github/agents/        .opencode/agents/
```

The `dx-agent-gen` package (`.deepx/tools/`) handles the conversion, and the pre-commit hook (`install-hooks.sh` → `pre-commit-hook.sh`) blocks drift.

### 2.2 Directory Catalog (existence per repo)

| Directory | suite | runtime | dx_app | dx_stream | compiler | Role |
|-----------|:-----:|:-------:|:------:|:---------:|:--------:|------|
| `agents/` | ✅ | ✅ | ✅ | ✅ | ✅ | Domain agent definitions (.md) |
| `skills/` | ✅ | ✅ | ✅ | ✅ | ✅ | Slash commands / procedural skills |
| `templates/en,ko` | ✅ | ✅ | ✅ | ✅ | ✅ | CLAUDE/AGENTS/copilot-instructions tmpl |
| `templates/fragments/` | ✅ (16×2) | — | — | — | — | Shared rule fragments injected into all levels |
| `memory/` | ✅ | ✅ | ✅ | ✅ | ✅ | Persistent knowledge (pitfalls, model_zoo, …) |
| `instructions/` | — | ✅ | ✅ | ✅ | ✅ | Architecture · coding standards · protocols |
| `knowledge/` | — | ✅ | ✅ | ✅ | — | YAML-form rules / model DB |
| `toolsets/` | — | — | ✅ | ✅ | ✅ | SDK API reference |
| `contextual-rules/` | — | — | ✅ | ✅ | — | glob-based rule enforcement |
| `prompts/` | — | — | ✅ | ✅ | — | Agent input templates |
| `scripts/` | — | ✅ | ✅ | ✅ | ✅ | validate / feedback / generate |
| `docs/` | ✅ | — | — | — | — | Framework self-guides (skill-architecture, etc.) |
| `tools/` | ✅ | — | — | — | — | Tooling packages: `src/{dx_agent_dev_gen, dx_transcripts}` + mirrored `tests/` + `scripts/` |
| `tests/` | ✅ | — | — | — | — | Suite **conformance** tests (`conformance/`) — KB / generated-output policy checks |
| `e2e/` | ✅ | — | — | — | — | E2E harness: `e2e_runner`/`e2e_monitor`, `test_agent_e2e_scenarios/`, `agent_analyzer/`, `test.sh` |

---

## 3. dx-all-suite `.deepx/` (Top-Level Routing + Generator)

### 3.1 agents/ — 2 Top-Level Routers

| Agent | Responsibility | HARD GATE |
|-------|---------------|-----------|
| **`dx-suite-builder.md`** | Task classification → routing to dx-compiler / dx_app / dx_stream / cross-project | Re-brainstorm required when transitioning between cross-project phases |
| **`dx-suite-validator.md`** | Validation orchestration across 3 levels (framework) | 5-step workflow (validate → collect → apply → re-validate) |

### 3.2 docs/ — Framework Self-Guides

| File | Content |
|------|---------|
| `skill-architecture.md` (+ KO) | 3-tier separation, mandatory skill sequence, classification of end-user / SDK / harness scenarios |
| `fragment-authoring-guide.md` (+ KO) | Fragment 4 rules: EN+KO simultaneous generation, structural marker preservation, lint verification, no Korean in body (with exceptions) |

### 3.3 memory/sdk_grounding_reference.md

Grounding document to prevent API hallucination. Lists only verified symbols:
- `IFactory` 5 methods, `SyncRunner`, `AsyncRunner`
- `dx_com.compile(...)` (the `from dxcom import dxcom` pattern is forbidden)
- 13 GStreamer elements
- All API names in every instruction must be cross-validated against this document

### 3.4 templates/fragments/ — 16 Shared Rule Fragments (EN+KO 32 total)

| Fragment | Role |
|----------|------|
| `mandatory-process-skill-sequence.md` | Enforces router → brainstorm → plan → tdd → verify order |
| `swe-process-gates-internal-dev.md` | SWE discipline when developing internal dx-agent-dev |
| `artifact-verification-gate.md` | Output verification checklist |
| `session-sentinels.md` | START/DONE marker definitions |
| `rule-conflict-resolution.md` | Priority on rule conflict (user > skill > default) |
| `git-safety-superpowers.md` / `git-operations-user-handles.md` | docs/superpowers/ commit prohibition, git operation delegation |
| `no-placeholder-code.md` / `experimental-features-prohibited.md` | TODO / experimental feature prohibition |
| `response-language.md` / `recommended-model.md` / `skill-router-mandatory.md` | Response language matching, Claude Sonnet 4.6+ recommendation, forced router invocation |
| `autopilot-mode-guard.md` | Autopilot mode guard ("no asking, but follow all rules") |
| `brainstorming-spec-before-plan.md` / `plan-output.md` / `instruction-verification-loop.md` | Procedure enforcement |

These 16 fragments are **selectively injected** into the `CLAUDE.md` / `AGENTS.md` / `copilot-instructions.md` of the 5 repos, creating a consistent rule base.

### 3.5 skills/ — 14 Common Skills

| Category | Skill | One-line description |
|----------|-------|----------------------|
| **SWE process** | `dx-swe-brainstorm` | Before code writing: 2-3 approaches + spec self-review + user approval gate |
| | `dx-swe-tdd` | Red-Green-Verify, immediate verification right after file creation |
| | `dx-swe-verify` | Fresh evidence required before claiming completion |
| | `dx-swe-debugging` | No fix without Phase 1 root cause analysis |
| | `dx-swe-writing-plans` / `dx-swe-executing-plans` / `dx-swe-subagent-dev` / `dx-swe-parallel-agents` | Plan writing/execution/parallel dispatch |
| | `dx-swe-receiving-review` / `dx-swe-requesting-review` | Review reception/request |
| **DEEPX domain** | `dx-agent-brainstorm` / `dx-agent-tdd` / `dx-agent-verify` | DEEPX-specific (model registry check, etc.) |
| **Harness** | `dx-harness-validate` / `dx-harness-writing-skills` | `.deepx/` self-integrity verification / skill creation |
| **Meta** | `dx-skill-router` | "Invoke if even 1% probability of applicability" rule |

### 3.6 tools/ — Tooling Packages + Generator

`tools/src/` holds two importable packages, each mirrored under `tools/tests/`:

| Package (`tools/src/`) | Tests (`tools/tests/`) | Role |
|------------------------|------------------------|------|
| `dx_agent_dev_gen` | `dx_agent_dev_gen/` | The `dx-agent-gen` generator (cli, generator, transformers, frontmatter, constants) |
| `dx_transcripts` | `dx_transcripts/` | Shared session parsers + transcript renderer (`parse_*_session`, `session_common`, `generate_transcripts`, `backfill_claude_html`) — used by the session-sentinel DONE-line generation, the e2e harness, and the analyzer |

| Component | Role |
|-----------|------|
| `pyproject.toml` | `dx-agent-gen` CLI (Python 3.10+); `packages.find where=["src"]` discovers both packages |
| `scripts/run_all.sh generate\|check\|lint\|prune` | Batch ops across 5 repos (`.`, dx-compiler, dx-runtime, dx-runtime/dx_app, dx-runtime/dx_stream) |
| `scripts/install-hooks.sh` / `pre-commit-hook.sh` | Pre-commit hooks: `.deepx/`↔non-`.deepx/` mix warning + drift check + EN/KO lint |

### 3.7 tests/ — Suite Conformance

- `conformance/`: ~700 fast static checks (no CLI/NPU needed) — guide structure, routing consistency, scenario references, cross-project handoff, instruction sync, sdk grounding, forbidden patterns. Run `pytest .deepx/tests/conformance/ --collect-only -q` for the live count.

### 3.8 e2e/ — End-to-End Harness (separated)

- `e2e_runner.py` / `e2e_monitor.py` / `migrate_results_to_run_id.py` / `_cli_env.py` / `test.sh` — round orchestration, monitoring, results migration, shared runner.
- `test_agent_e2e_scenarios/`: ~586 collected across 5 CLI autopilot markers (copilot, cursor, opencode, claude-code, codex) — real CLI invocation → static verification (file existence, AST, JSON). Plus interactive manual modes (shell).
- `agent_analyzer/`: run-id-aware result analyzer (reports / insights; its own `lib/` + `tests/`).

---

## 4. dx-runtime `.deepx/` (Integrated Routing + Integrated Verification)

### 4.1 agents/

| Agent | Role | Routing decision |
|-------|------|------------------|
| **`dx-runtime-builder.md`** | dx_app vs dx_stream classifier | Python/C++ + IFactory → dx_app, GStreamer + RTSP + DxInfer → dx_stream |
| **`dx-validator.md`** | 3-level integrated verification + feedback loop | 5 steps: framework verification → feedback collection → approval → apply → re-verification |

**3 HARD GATEs**:
1. `sanity_check.sh --dx_rt` passes (judged by output text, ignoring exit code)
2. Brainstorm 3 questions (app type / AI task / input source)
3. Skill router invoke

### 4.2 memory/common_pitfalls.md (25 items, 16KB)

Pitfall collection categorized by 5 domain tags (`[UNIVERSAL]`, `[DX_APP]`, `[DX_STREAM]`, `[PPU]`, `[INTEGRATION]`):
- Model name casing / preprocess-id matching / async frame_id non-use / RTSP DxRate omission / PPU postprocessor / OBB nms_threshold ignore / DxMsgConv placement / headless DISPLAY check / Python import separation

### 4.3 instructions/

| File | Content |
|------|---------|
| `agent-protocols.md` | 3 protocols: Cross-project consistency / Sub-agent routing / Memory feedback |
| `integration.md` | Model path resolution differences (dx_app: model_registry.json, dx_stream: model_list.json), build order (`dx_rt → dx_app → dx_stream`), Python import separation |

### 4.4 knowledge/feedback_rules.yaml

Mapping from verification patterns (regex) → `.deepx/` file updates. 8 action types:
`append_pitfall`, `append_rule`, `fix_reference`, `add_domain_tag`, `update_skill`, …

### 4.5 scripts/ — 5 Python Tools

| Script | Role |
|--------|------|
| `validate_framework.py` | `.deepx/` structure / cross-reference / routing table verification |
| `validate_app.py` | App code pattern verification (IFactory, parse_common_args, relative imports) |
| `feedback_collector.py` | Normalize verification results → match `feedback_rules.yaml` → JSON suggestions |
| `apply_feedback.py` | Apply approved suggestions to `.deepx/` (dry-run supported) |

### 4.6 skills/

12 skills (same 8 swe-* as suite + 3 agent-driven-* + dx-skill-router + unique `dx-agent-runtime-validate`)

---

## 5. dx_app `.deepx/` (Standalone Inference — IFactory)

### 5.1 agents/ (6)

| Agent | Responsibility |
|-------|---------------|
| **`dx-app-builder`** | Master router — delegates to specialists after collecting 3 mandatory questions (language/task/model) |
| **`dx-python-builder`** | Generates 4 variants (sync / async / cpp_postprocess / async_cpp_postprocess) |
| **`dx-cpp-builder`** | C++ app + CMakeLists.txt + SIGINT handler / RAII / C++14 |
| **`dx-benchmark-builder`** | Runs `--verbose --loop 3`, analyzes 7-field metrics |
| **`dx-model-manager`** | `config/model_registry.json` query, download, compatibility verification |
| **`dx-validator`** | 5-step verification pyramid (static → config → component → smoke → accuracy) |

### 5.2 skills/ (4 domain + 4 process + common)

| Domain skill | Core |
|--------------|------|
| `dx-agent-app-build-python` | Python variants, IFactory 5 methods |
| `dx-agent-app-build-cpp` | C++ + CMakeLists.txt |
| `dx-agent-app-build-async` | AsyncRunner frame overlap |
| `dx-agent-app-model-management` | model_registry.json query/download |
| `dx-agent-app-validate` | 5-step verification |

### 5.3 memory/ (5 files)

| File | Content |
|------|---------|
| `MEMORY.md` | Index + update protocol + domain tags |
| `common_pitfalls.md` (32KB) | 10 core pitfalls (`[UNIVERSAL]`, `[DX_APP]`, `[PPU]`) |
| `model_zoo.md` | 133 models (object_detection 50, classification 15, instance_seg 8, pose 6, face 8 …) — for exact counts, use jq query on `model_registry.json` |
| `platform_api.md` | DX-M1 NPU, DX-RT 3.0.x, cold boot requirement, `DXRT_DYNAMIC_CPU_THREAD=ON` |
| `performance_patterns.md` | 7-field metrics (read/preprocess/inference/postprocess/render/save/display) + optimization techniques |

### 5.4 instructions/ (6 files)

| File | Content |
|------|---------|
| `architecture.md` | 3-layer architecture (app → framework → C++ core), 37 postprocess bindings |
| `factory-pattern.md` | IFactory 5 methods, `_FactoryConfigMixin.load_config(dict)` mechanism |
| `coding-standards.md` | Python `sys.path` 2-parent pattern, logging, C++14 RAII |
| `agent-protocols.md` | Routing format, handoff messages |
| `orchestration.md` | Multi-agent TDD order, artifact generation order |
| `testing-patterns.md` | pytest, `DXAPP_VERIFY`, NPU skip, smoke test, mocking |

### 5.5 toolsets/ (5 files, SDK API reference)

| File | API scope |
|------|-----------|
| `common-framework-api.md` (~1200L) | `SyncRunner`, `AsyncRunner`, `parse_common_args` (11 flags), IFactory 11 interfaces |
| `dx-engine-api.md` (~200L) | `InferenceEngine` (run, run_async, wait, tensor info), `InferenceOption` |
| `dx-postprocess-api.md` (~600L) | 37 pybind11 bindings (Det 11 / Cls 4 / Seg 4 / Pose 2 / Face 3 / PPU 5 / others) |
| `model-registry.md` | `model_registry.json` schema + query patterns |
| `dx-model-format.md` | `.dxnn` tensor spec, INT8/UINT8/FP16, compile flow |

### 5.6 contextual-rules/ vs prompts/

| Category | contextual-rules/ | prompts/ |
|----------|-------------------|----------|
| Purpose | **Rule enforcement** (glob-based) | **Agent input templates** (variable filling) |
| Files | `python-example.md`, `cpp-example.md`, `postprocess.md`, `tests.md` | `new-python-detection.md`, `new-python-segmentation.md`, `new-cpp-app.md`, `orchestrated-build.md` |
| Example | "All Python apps require `parse_common_args()`" | "Build a `{model_name}` `{variant}` app with `{input_source}`" |

### 5.7 14 Mandatory Artifacts (every session)

`config.json`, `session.json`, `README.md`, `setup.sh`, `run.sh`, `session.log` (6 common) + `factory/<model>_factory.py`, `factory/__init__.py`, `<model>_sync.py` (3 mandatory for Python) + async/cpp_postprocess variant options + C++ variant options.

### 5.8 HARD GATE Summary

1. **skeleton-first**: copy `src/python_example/<task>/<model>/` → modify only model-specific parts
2. **IFactory 5 methods**: `create_preprocessor / create_postprocessor / create_visualizer / get_model_name / get_task_type`
3. **SyncRunner / AsyncRunner only**: direct `InferenceEngine` calls forbidden
4. **`model_registry.json` query required**: model name fabrication forbidden
5. **Output Isolation**: writing outside `dx-agent-dev/<session_id>/` forbidden
6. **PPU auto-detection**: `_ppu` suffix → use `src/python_example/ppu/` path
7. **Self-contained & portable**: `setup.sh` vendors `common` → `./common` and the `<model>_sync.py` walker prefers that vendored `./common` (no `PYTHONPATH`), so the app runs even when copied outside the suite — verified out-of-suite (`dx_engine` is the only external dep)

---

## 6. dx_stream `.deepx/` (GStreamer Pipelines)

### 6.1 agents/ (4)

| Agent | Role |
|-------|------|
| **`dx-stream-builder`** | Master router — Phase 0~6 (prerequisites → understanding → context load → build → cleanup → verification → report) |
| **`dx-pipeline-builder`** | Direct GStreamer pipeline writing + Python/Shell scripts + 3-step verification |
| **`dx-model-manager`** | `model_list.json` query, download, PPU/non-PPU compatibility verification |
| **`dx-validator`** | preprocess-id/inference-id matching, queue placement, model/library path existence, element registration check |

### 6.2 13 GStreamer Elements (toolsets/`dx-stream-elements.md`)

| # | Element | Role |
|---|---------|------|
| 1 | `DxPreprocess` | resize / normalize / letterbox / secondary ROI |
| 2 | `DxInfer` | NPU `.dxnn` execution |
| 3 | `DxPostprocess` | tensor → object metadata (`libpostprocess_*.so`) |
| 4 | `DxTracker` | OC-SORT multi-object tracking |
| 5 | `DxOsd` | box/label/confidence OSD |
| 6 | `DxRate` | frame rate control (RTSP buffer prevention) |
| 7 | `DxScale` | frame size resize |
| 8 | `DxConvert` | color conversion |
| 9 | `DxGather` | N:1 multiplexing (cascaded) |
| 10 | `DxInputSelector` | N:1 round-robin |
| 11 | `DxOutputSelector` | 1:N demultiplexing |
| 12 | `DxTile` | high-resolution input splitting |
| 13 | `DxDeTile` | tile result reassembly |

Additional messaging elements (`architecture.md`): `DxMsgConv`, `DxMsgBroker`.

### 6.3 6 Pipeline Categories

| Category | Core chain | Domain skill |
|----------|-----------|--------------|
| Single-model | `src ! DxPreprocess ! queue ! DxInfer ! queue ! DxPostprocess ! queue ! DxOsd ! sink` | `build-pipeline` |
| Multi-stream | N × (preprocess→infer→postprocess→osd→DxScale) ! compositor ! sink | `build-pipeline` |
| Tracking | `... ! DxPostprocess ! queue ! DxTracker ! queue ! DxOsd ! ...` | `build-pipeline` |
| Cascaded (Secondary) | `... ! primary ! tee ! t. ! sec_A ! gather.sink_0  t. ! sec_B ! gather.sink_1  DxGather ! ...` | `build-pipeline` |
| RTSP | `urisourcebin ! decodebin ! DxRate ! DxInputSelector ! ...` | `build-pipeline` |
| Broker | `... ! DxPostprocess ! queue ! DxMsgConv ! queue ! DxMsgBroker` | `build-mqtt-kafka` |

### 6.4 skills/ (4 domain + common)

| Domain skill | Core difference |
|--------------|-----------------|
| `dx-agent-stream-build-pipeline` | Pipeline **construction** (elements + order) |
| `dx-agent-stream-build-mqtt-kafka` | Pipeline **messaging** (result external transmission) |
| `dx-agent-stream-model-management` | Model **registry** (`model_list.json`) |
| `dx-agent-stream-validate` | Verification **system** (validate_app / validate_framework) |

### 6.5 memory/ (4 files)

| File | Content |
|------|---------|
| `MEMORY.md` | Index + update protocol |
| `common_pitfalls.md` | 14 domain-tagged pitfalls |
| `pipeline_optimization.md` | Throughput/latency tuning |
| `platform_api.md` | DX-RT platform detection / version check |

### 6.6 instructions/ (6 files)

`architecture.md`, `agent-protocols.md`, `coding-standards.md`, **`gstreamer-pipeline.md`** (13 elements in detail, each 15-25 lines), `orchestration.md`, `testing-patterns.md`

### 6.7 toolsets/ (4 files)

| File | Scope |
|------|-------|
| `dx-stream-elements.md` | All 13 elements (properties / Pads / examples / pitfalls) |
| `dx-stream-metadata.md` | `pydxs` Python bindings (`DXFrameMeta`, `DXObjectMeta`, `DXTensorMeta`) |
| `dx-engine-api.md` | Common with dx_app |
| `model-registry.md` | v2.3.0 / 14 models / task ↔ postprocess `.so` mapping |

### 6.8 11 Core HARD GATEs

1. Prerequisites (`sanity_check.sh --dx_rt`, `gst-inspect-1.0 dxinfer`)
2. Existing pipeline search (`dx_stream/pipelines/`)
3. Generation of 8 mandatory artifacts
4. `x264enc tune=zerolatency` (deadlock without it)
5. preprocess-id / inference-id matching
6. Queue placement (preprocess ↔ infer ↔ postprocess ↔ tracker)
7. DxTracker comes after DxPostprocess (forbidden immediately after DxInfer)
8. DxMsgConv → DxMsgBroker order
9. DxRate mandatory for RTSP
10. Absolute paths (`/usr/local/share/gstdxstream/lib/...`)
11. PPU model auto-detection (`_ppu` suffix → omit DxPostprocess)

---

## 7. dx-compiler `.deepx/` (Reference: ONNX → DXNN)

> Outside the 4 repos the user specified, but a summary is included because of its core role in dx-agent-dev cross-project scenarios.

### 7.1 agents/ (3)

| Agent | Role |
|-------|------|
| `dx-compiler-builder.md` | converter / dxnn-compiler routing |
| `dx-dxnn-compiler.md` (48KB) | ONNX → DXNN (DX-COM, PPU auto-detection, calibration) |
| `dx-model-converter.md` | PyTorch → ONNX |

### 7.2 Core Rules

- `import dx_com; dx_com.compile(...)` (NOT `from dxcom import dxcom`)
- `compiler.properties` modification forbidden (system file)
- For cross-project, use the `SUITE_ROOT` auto-detection pattern (`../../` hardcoding forbidden)
- Background compilation + parallel artifact generation (sleep-poll forbidden)
- Pre-DONE `.dxnn` existence check (R-X4 gate)

### 7.3 toolsets/

`dxcom-cli.md`, `dxcom-api.md`, `config-schema.md` — must be referenced when fabrication is a risk, to prevent API hallucination.

---

## 8. Core 5-Step Workflow (every code-generation session)

```
1. /dx-skill-router          ← Universal Pre-Flight (HARD GATE, every user message)
2. /dx-agent-brainstorm    ← Requirements + 2-3 approaches + user approval
3. /dx-swe-writing-plans     ← Structured plan
4. /dx-agent-tdd           ← Red(criteria) → Green(generate) → Verify(immediate)
5. /dx-agent-verify        ← Final evidence (execution output, no conscientious assertions)
```

**All steps apply even in autonomous mode (autopilot, `--yolo`)**. The only difference is replacing `ask_user` with knowledge base defaults.

---

## 9. Verification Infrastructure (`.deepx/tests/`)

### 9.1 Conformance (~700 tests, ~1 sec)

| Module | Verification items |
|--------|--------------------|
| `test_guide_structure.py` | Guide document headings, scenario numbers, EN/KO synchronization |
| `test_routing_consistency.py` | CLAUDE.md, AGENTS.md, copilot-instructions.md, .cursorrules routing consistency |
| `test_scenario_references.py` | Agent/skill references matched to actual infrastructure |
| `test_cross_project_scenarios.py` | Handoff chain, validation scripts, output isolation |

### 9.2 E2E Scenarios (~586 pytest + manual)

| Tool | autopilot flags | Auto-approve / question blocking | Session export |
|------|------------------|---------------------------------|----------------|
| Copilot CLI | `--yolo --no-ask-user -s` | `--yolo` / `--no-ask-user` | `--share=<file>` (HTML via `/share html`) |
| Cursor CLI (`agent`) | `-p --force --output-format stream-json` | `--force` / prompt instruction | stream-json stdout |
| OpenCode | `run --format json` | `run` mode auto / prompt instruction | `/export` → `session-*.md` |
| Claude Code (`claude`) | `-p --dangerously-skip-permissions --output-format stream-json` | `--dangerously-skip-permissions` / prompt instruction | `/export` → `*.txt` |
| Codex CLI (`codex`) | `exec --json -s danger-full-access -m <model>` | `-s danger-full-access` / prompt instruction | `~/.codex/sessions/YYYY/MM/DD/rollout-*-<thread_id>.jsonl` |

5 scenarios × 5 tools = 25 scenarios. Verification is **static analysis only** (file existence, AST, JSON, patterns) — actual HW inference is not performed.

---

## 10. 5-Repo Comparison at a Glance

| Aspect | dx-all-suite | dx-runtime | dx_app | dx_stream | dx-compiler |
|--------|--------------|-----------|--------|-----------|-------------|
| **Number of agents** | 2 | 2 | 6 | 4 | 3 |
| **Number of domain skills** | 0 (meta only) | 1 | 5 | 4 | 3 |
| **Number of memory files** | 1 | 1 | 5 | 4 | 2 |
| **toolsets/** | — | — | 5 | 4 | 3 |
| **instructions/** | — | 2 | 6 | 6 | 2 |
| **knowledge/** | — | feedback_rules.yaml | knowledge_base.yaml | knowledge_base.yaml | — |
| **scripts/** | tools/ generator | 5 | 3 | 3 | 1 |
| **contextual-rules/** | — | — | 4 | 3 | — |
| **prompts/** | — | — | 4 | 3 | — |
| **Unique responsibility** | Routing + generator + tests | Integrated verification + routing | IFactory inference apps | GStreamer pipelines | ONNX → DXNN |

---

## 11. Conclusion and Impressions

1. **Single-Source-of-Truth (SoT) design is robust**: `.deepx/` → `dx-agent-gen` → 4 platforms. Drift is blocked by the pre-commit hook.
2. **Multi-layered HARD GATE enforcement**: skill router (meta) → process sequence → domain rules (IFactory, preprocess-id, etc.) → artifact verification. Focused on preventing silent failures.
3. **Wide test automation coverage**: ~700 conformance + ~586 E2E + 5-tool cross-validation. The same rules are enforced even in autonomous mode (`--yolo`).
4. **Per-module autonomy + common backbone**: Each sub-project has its own `.deepx/` enabling independent work, while consistency is maintained via 16 fragments + skill router + Output Isolation rule.
5. **Extension points**: When adding a new domain, writing the 5 items — ① `.deepx/agents/` ② `.deepx/skills/` ③ `.deepx/memory/common_pitfalls.md` ④ `.deepx/toolsets/` ⑤ `instructions/` — is automatically reflected on all 4 platforms.

---

## Appendix A. Key Command Cheatsheet

```bash
# Generator (canonical → platforms)
pip install -e .deepx/tools
dx-agent-gen generate                                 # single repo
dx-agent-gen check                                    # drift check
bash .deepx/tools/scripts/run_all.sh generate           # batch across 5 repos
bash .deepx/tools/scripts/run_all.sh check
bash .deepx/tools/scripts/install-hooks.sh              # one-time hook install

# Verification
python dx-runtime/.deepx/scripts/validate_framework.py
python dx-runtime/dx_app/.deepx/scripts/validate_framework.py
python dx-runtime/dx_stream/.deepx/scripts/validate_framework.py
python dx-compiler/.deepx/scripts/validate_framework.py
python dx-runtime/.deepx/scripts/feedback_collector.py --framework-only

# Tests
cd .deepx/e2e
./test.sh agent-driven                                       # ~700 conformance tests
./test.sh agent-driven-e2e-claude-code-autopilot             # Claude Code E2E
./test.sh agent-driven-e2e-copilot-cli-autopilot
./test.sh agent-driven-e2e-cursor-cli-autopilot
./test.sh agent-driven-e2e-opencode-cli-autopilot
./test.sh agent-driven-e2e-codex-cli-autopilot               # Codex CLI E2E
```

## Appendix B. Environment Variables (E2E Tests)

| Variable | Default | Purpose |
|----------|---------|---------|
| `DX_AGENT_E2E_MODEL` | `claude-sonnet-4.6` | Copilot CLI model |
| `DX_AGENT_E2E_TIMEOUT` | `300` | Copilot CLI timeout |
| `DX_AGENT_E2E_CURSOR_MODEL` | `claude-4.6-sonnet-medium` | Cursor CLI model |
| `DX_AGENT_E2E_OPENCODE_MODEL` | `github-copilot/claude-sonnet-4.6` | OpenCode model |
| `DX_AGENT_E2E_CLAUDE_CODE_MODEL` | `claude-sonnet-4-6` | Claude Code model |
| `DX_AGENT_E2E_CODEX_MODEL` | `gpt-5.3-codex` | Codex CLI model |
| `DX_AGENT_E2E_CODEX_TIMEOUT` | `600` | Codex CLI timeout (sec) |
| `DX_AGENT_E2E_CLEANUP_ARTIFACTS` | (unset) | 1 = delete artifacts after success |

---

*End of report.*
