---
name: dx-brainstorm-and-plan
description: "Brainstorm and plan before any code generation. HARD-GATE: no code without approved plan."
---

# Skill: Brainstorm and Plan (Suite-Level)

> **RIGID skill** — follow this process exactly. No shortcuts, no exceptions.

## Scope

This is the **top-level suite** version covering all sub-projects. When working
in a single sub-project, prefer the project-level version:

| Working on... | Use this skill |
|---|---|
| dx_app (standalone inference) | `dx-runtime/dx_app/.deepx/skills/dx-brainstorm-and-plan.md` |
| dx_stream (GStreamer pipelines) | `dx-runtime/dx_stream/.deepx/skills/dx-brainstorm-and-plan.md` |
| Cross-project integration | `dx-runtime/.deepx/skills/dx-brainstorm-and-plan.md` |

## Overview

Collaborative design session before any code generation across the DEEPX suite.
Explores user intent, gathers requirements, proposes approaches, and produces an
approved build plan.

<HARD-GATE>
Do NOT generate any application code, create any files, or take any implementation
action until you have presented a build plan and the user has approved it.
This applies to EVERY request regardless of perceived simplicity.
</HARD-GATE>

## When to Use

**Always** — before any work in the DEEPX suite:
- New Python inference app (dx_app)
- New C++ inference app (dx_app)
- New GStreamer pipeline (dx_stream)
- Cross-project build coordination (dx_app + dx_stream)
- Shared model configuration
- Integration testing across sub-projects
- Modifying existing applications or conventions
- Any request that would create or modify code files

## Anti-Pattern: "This Is Too Simple"

Every build goes through this process. A single-model detection app, a config
change, a variant addition — all of them. "Simple" projects are where unexamined
assumptions cause the most wasted work.

## Process

### Step 1: Route to Sub-Project

Determine which sub-project(s) are involved:
1. If **only dx_app** → delegate to `dx-runtime/dx_app/.deepx/skills/dx-brainstorm-and-plan.md`
2. If **only dx_stream** → delegate to `dx-runtime/dx_stream/.deepx/skills/dx-brainstorm-and-plan.md`
3. If **cross-project** → use the integration version at `dx-runtime/.deepx/skills/dx-brainstorm-and-plan.md`
4. If **unclear** → ask the user which sub-project they're targeting

### Step 2: Context Check

Before asking any questions:
1. Check the relevant model registry (`model_registry.json` for dx_app, `model_list.json` for dx_stream)
2. Check if the target directory already exists
3. If the model/app already exists, inform the user and ask their intent

### Step 3: Ask Key Decisions (one at a time)

Gather these decisions through focused questions:

1. **What are you building?** (app type, task, model)
2. **What variant?** (Python sync/async, C++, pipeline category)
3. **What input source?** (image, video, USB camera, RTSP)
4. **Any special requirements?** (custom thresholds, specific classes, tracking, broker)

Rules:
- One question at a time
- Provide concrete options (not open-ended)
- Default to the simplest working configuration

### Step 4: Present Build Plan

Present a concise plan covering all affected sub-projects.

### Step 5: Get User Approval

Wait for explicit user approval before proceeding.

### Step 6: Route to Implementation

After approval, route to the appropriate project-level skill.

## 5-Condition Pre-Flight Check

Before presenting the build plan, verify ALL of these:

| # | Check | Action if Failed |
|---|---|---|
| 1 | Model exists in registry | List available models, ask user to choose |
| 2 | Target directory doesn't exist | Ask user: modify existing, specialize, or fresh build? |
| 3 | Task type is supported | List supported tasks, suggest closest match |
| 4 | Required components exist | Check preprocessor/postprocessor availability |
| 5 | Output path is dx-agentic-dev/ | Confirm isolation (never default to src/) |

## Red Flags — STOP

- Generating code without user approval
- Skipping the model registry check
- Creating files in src/ without explicit user request
- Assuming the user wants the same thing as an existing app
- Proceeding without confirming variant and input source

## Key Principle

**Ask first, build second.** Every minute spent clarifying saves ten minutes
of rework. The user's intent is never obvious — even "build a yolo26n app"
has multiple valid interpretations.
