# `dx-showcase-gen` — Showcase-Generation Automation

> Deterministic mechanics for building **dx-agent-dev showcases**, paired with the
> RIGID skill [`dx-agent-showcase-build`](../../../skills/dx-agent-showcase-build/SKILL.md).
> Together they turn "add a showcase" into a repeatable, verified workflow whose
> recurring mistakes are caught by code + gates instead of by memory.

Korean: [`README-ko.md`](./README-ko.md).

## Why (the split)

A showcase = a real agent-driven build of a DEEPX app, captured as a build GIF + a complete
transcript + the generated artifacts, then promoted in the READMEs and docs. Some of
that is **non-deterministic / human** (the agent-driven build itself, the KB-based prompt,
clearing the screen for recording, writing prose); the rest is **deterministic and was
the source of every recurring mistake** we hit. So:

- **Tool (`dx-showcase-gen`, this package)** owns the deterministic mechanics — tested.
- **Skill (`dx-agent-showcase-build`)** owns the orchestration + judgment + the
  human-in-the-loop gates, and runs the tool's `verify` before declaring DONE.

## Recurring mistakes this prevents

| Mistake (seen in real builds) | Where it's prevented |
|---|---|
| GIF showed a synthetic render, not the real claude screen | skill records the real window; tool crops it |
| GIF cropped wrong / failed on off-screen terminal | `recorder` captures full screen + post-crops to the window rect |
| GIF > 10MB (won't inline on GitHub) | `recorder.make_gif` auto-reduces |
| Transcript missing **Wall-clock / Cost** | `transcript.render` requires `--stream-json` (the `result` event); errors otherwise |
| Wrong tool/model in the showcase | `verify` checks `tool=claude`, `model=claude-opus-4-8` |
| Generated artifacts never copied / not portable | `artifacts.copy_session_artifacts` + `scan_nonportable` |
| README/docs not augmented (or double-inserted) | `augment` is idempotent + marker-anchored |
| Declared DONE while broken | skill's Phase-8 `verify` gate must PASS |

## Install / run

```bash
pip install -e .deepx/tools          # registers `dx-showcase-gen`
# or, without installing:
export PYTHONPATH=.deepx/tools/src
python3 -m dx_showcase_gen.cli --help
```

## Subcommands

| Command | Purpose |
|---|---|
| `transcript` | Render `claude-code-session.{md,html,jsonl}` from a `--stream-json` capture (fails if it lacks a `result` event → no Wall-clock/Cost) |
| `verify` | Run the showcase verification gate; exit 1 on any failure |
| `copy-artifacts` | Copy a build session's files into the showcase dir (skips venv/`*.pt`/`*.onnx`/`*.dxnn`); print portability flags |
| `augment` | Upsert a GIF block into a README/doc (idempotent, marker-anchored) |
| `gif` | Encode a timelapse GIF from a captured mp4 (target-secs speedup, <10MB) |
| `crop` | Post-crop a full-screen capture to a window rect (`--title` or `--rect WxH+X+Y`) |
| `window-rect` | Print a window's rect via `xwininfo` |
| `capture-start` / `capture-stop` | Start/stop a backgrounded x11grab full-screen capture |
| `keepawake start|stop` | Stop GNOME from blanking the display during a long recording |

## Modules

| Module | Responsibility |
|---|---|
| `recorder.py` | x11grab capture, window-rect crop, timelapse GIF; pure helpers (`clamp_crop`, `speedup_factor`, ffmpeg arg builders) are unit-tested |
| `transcript.py` | COMPLETE transcript render (reuses `dx_transcripts`), `--stream-json` enforced |
| `verify.py` | PASS/FAIL gate (`Report`/`Check`) covering transcript, model/tool, GIFs, artifacts, augmentation |
| `artifacts.py` | session→showcase copy + non-portable path scan |
| `augment.py` | idempotent marker-anchored block upsert |
| `constants.py` | defaults (`model=claude-opus-4-8`, GIF policy, paths) |
| `cli.py` | argparse dispatch (has a real `__main__` guard, so `-m` works) |

## Tests

```bash
PYTHONPATH=.deepx/tools/src python3 -m pytest .deepx/tools/tests/dx_showcase_gen/ -v
```

Cover the pure/deterministic surface: crop clamping, speedup, ffmpeg args, transcript
metrics/completeness, idempotent augmentation, and the verify gate flagging a missing
file / wrong model. x11grab/ffmpeg side-effects are thin wrappers (not unit-tested).

## The workflow (skill drives the tool)

1. KB-based build prompt (skill) → 2. recording-prep gate, human clears a screen region
(skill) → 3. recorded REAL build + `--output-format stream-json` capture (skill + tool
`keepawake`/`capture`/`crop`/`gif`) → 4. `transcript` (complete) → 5. `copy-artifacts`
+ portability fixes → 6. run GIF → 7. `augment` README/docs → 8. `verify` PASS.

See the skill: [`dx-agent-showcase-build`](../../../skills/dx-agent-showcase-build/SKILL.md).
