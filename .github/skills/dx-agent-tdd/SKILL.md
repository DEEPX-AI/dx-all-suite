---
name: dx-agent-tdd
description: DEEPX build validation order — factory, pipeline, and integration checks.
---

<!-- AUTO-GENERATED from .deepx/ — DO NOT EDIT DIRECTLY -->
<!-- Source: .deepx/skills/dx-agent-tdd/SKILL.md -->
<!-- Run: dx-agent-gen generate -->

# Skill: DEEPX Build Validation Order

> For the general Red-Green-Verify cycle and classic TDD process, see `dx-swe-tdd`.
> This skill covers DEEPX-specific validation order and checks.

## Scope

This is the **top-level suite** version covering all sub-projects. When working
in a single sub-project, prefer the project-level version:

| Working on... | Use this skill |
|---|---|
| dx_app (standalone inference) | `dx-runtime/dx_app/.github/skills/dx-tdd.md` |
| dx_stream (GStreamer pipelines) | `dx-runtime/dx_stream/.github/skills/dx-tdd.md` |
| Cross-project integration | `dx-runtime/.github/skills/dx-tdd.md` |

## DEEPX Validation Checks

In the DEEPX context, validation checks include:

**Per-project:**
- Syntax check (`py_compile`) for every Python file
- JSON validation for every config.json
- Factory interface compliance check (5 methods) — dx_app
- Pipeline argparse check — dx_stream
- Import resolution test

**Cross-project:**
- Build scripts pass for both sub-projects
- Cross-project imports resolve correctly (dx_stream → dx_app, never reverse)
- Shared model configuration is consistent
- Integration tests pass across sub-projects

## Validation Order — dx_app

| Order | File | Validation |
|---|---|---|
| 1 | `factory/<model>_factory.py` | py_compile + interface check |
| 2 | `factory/__init__.py` | py_compile + import test |
| 3 | `config.json` | JSON parse |
| 4 | `<model>_sync.py` | py_compile |
| 5 | `<model>_async.py` | py_compile |
| 6 | `session.json` | JSON parse |
| 7 | `README.md` | exists |

## Validation Order — dx_stream

| Order | File | Validation |
|---|---|---|
| 1 | `pipeline.py` | py_compile + argparse check |
| 2 | `run_<app>.sh` | bash -n syntax check |
| 3 | `config/*.json` | JSON parse |
| 4 | `session.json` | JSON parse |
| 5 | `README.md` | exists |

## Integration Validation Order

| Order | Check | Validation |
|---|---|---|
| 1 | dx_app build scripts | `./install.sh && ./build.sh` pass |
| 2 | dx_stream install | `./install.sh` passes |
| 3 | Cross-project imports | dx_stream can import from dx_app (never reverse) |
| 4 | Shared model paths | `model_registry.json` and `model_list.json` are consistent |
