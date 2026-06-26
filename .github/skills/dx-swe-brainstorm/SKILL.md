---
name: dx-swe-brainstorm
description: 'Brainstorm and plan before any code generation. HARD-GATE: no code without approved plan.'
---

<!-- AUTO-GENERATED from .deepx/ — DO NOT EDIT DIRECTLY -->
<!-- Source: .deepx/skills/dx-swe-brainstorm/SKILL.md -->
<!-- Run: dx-agent-gen generate -->

# Skill: Brainstorm and Plan

> **RIGID skill** — follow this process exactly. No shortcuts, no exceptions.

## Overview

Collaborative design session before any code generation. Explores user intent,
gathers requirements, proposes approaches, and produces an approved plan.

<HARD-GATE>
Do NOT generate any application code, create any files, or take any implementation
action until you have presented a build plan and the user has approved it.
This applies to EVERY request regardless of perceived simplicity.
</HARD-GATE>

## Anti-Pattern: "This Is Too Simple"

Every build goes through this process. A single-file change, a config update,
a variant addition — all of them. "Simple" projects are where unexamined
assumptions cause the most wasted work.

## Process

### Step 1: Ask Key Decisions (one at a time)

Gather these decisions through focused questions:

1. **What are you building?** (component type, purpose, scope)
2. **What variant?** (language, framework, execution model)
3. **What inputs/outputs?** (data sources, expected results)
4. **Any special requirements?** (constraints, performance targets, compatibility)

Rules:
- One question at a time
- Provide concrete options (not open-ended)
- Default to the simplest working configuration

### Step 2: Propose 2-3 Approaches

Before committing to a single design, propose 2-3 different approaches with
trade-offs:

- **Lead with your recommendation** and explain why
- For each approach, briefly describe: architecture, complexity, and trade-offs
- Examples of approach dimensions: sync vs async, monolithic vs modular,
  simple vs extensible

Wait for the user to choose or ask for more detail before proceeding.

### Step 3: Present Build Plan

Present a concise plan covering all affected components.

### Step 4: Get User Approval

Wait for explicit user approval before proceeding.

### Step 5: Spec Self-Review

After the user approves, do a quick self-review of the plan before implementation:

1. **Placeholder scan:** Any "TBD", "TODO", incomplete sections, or vague requirements? Fix them.
2. **Internal consistency:** Do any parts of the plan contradict each other? Does the architecture match the feature descriptions?
3. **Scope check:** Is this focused enough for a single implementation pass, or does it need decomposition?
4. **Ambiguity check:** Could any requirement be interpreted two different ways? If so, pick one and make it explicit.

Fix any issues inline — no need for a separate review cycle. If changes are
significant, re-confirm with the user.

### Step 6: Route to Implementation

After approval, route to the appropriate implementation skill or workflow.

## Red Flags — STOP

- Generating code without user approval
- Creating files before the plan is approved
- Assuming the user wants the same thing as an existing component
- Proceeding without confirming key decisions

## Key Principle

**Ask first, build second.** Every minute spent clarifying saves ten minutes
of rework. The user's intent is never obvious — even seemingly clear requests
have multiple valid interpretations.
