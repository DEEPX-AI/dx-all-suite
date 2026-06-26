---
name: dx-agent-brainstorm
description: "DEEPX build brainstorming with model registry check and sub-project routing."
---

# Skill: DEEPX Build Brainstorming

> For the general brainstorming process (key decisions, propose approaches,
> present plan, get approval, spec self-review), see `dx-swe-brainstorm`.
> This skill covers DEEPX-specific pre-flight checks and routing.

## Scope

This is the **top-level suite** version covering all sub-projects. When working
in a single sub-project, prefer the project-level version:

| Working on... | Use this skill |
|---|---|
| dx_app (standalone inference) | `dx-runtime/dx_app/.deepx/skills/dx-brainstorm-and-plan.md` |
| dx_stream (GStreamer pipelines) | `dx-runtime/dx_stream/.deepx/skills/dx-brainstorm-and-plan.md` |
| Cross-project integration | `dx-runtime/.deepx/skills/dx-brainstorm-and-plan.md` |

## When to Use

Use this skill (in addition to `dx-swe-brainstorm`) when the task involves
any DEEPX-specific concern:

- New Python or C++ inference app (dx_app)
- New GStreamer pipeline (dx_stream)
- Cross-project build coordination (dx_app + dx_stream)
- Shared model configuration
- Integration testing across sub-projects
- Modifying existing DEEPX applications or conventions

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

### Step 3: Follow General Brainstorming Process

Continue with the general brainstorming process defined in `dx-swe-brainstorm`:
key decisions, propose approaches, present plan, get approval, spec self-review,
then route to implementation.

## 5-Condition Pre-Flight Check

Before presenting the build plan, verify ALL of these:

| # | Check | Action if Failed |
|---|---|---|
| 1 | Model exists in registry | List available models, ask user to choose |
| 2 | Target directory doesn't exist | Ask user: modify existing, specialize, or fresh build? |
| 3 | Task type is supported | List supported tasks, suggest closest match |
| 4 | Required components exist | Check preprocessor/postprocessor availability |
| 5 | Output path is dx-agent-dev/ | Confirm isolation (never default to src/) |

## Red Flags — STOP

- Skipping the model registry check
- Creating files in src/ without explicit user request
- Assuming the user wants the same thing as an existing app
- Proceeding without confirming variant and input source
