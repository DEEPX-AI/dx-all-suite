---
name: dx-agentic-showcase-build
description: "Build a dx-agentic-dev showcase end-to-end: KB-based prompt → recorded real build → complete transcript → artifacts → GIFs → README/docs. RIGID gates prevent recurring mistakes."
---

# Skill: Build a dx-agentic-dev Showcase

> **RIGID skill.** Follow every phase and gate in order. The gates exist because
> each one corresponds to a mistake that has actually happened. Do NOT declare a
> showcase DONE until Phase 8 `verify` passes.

Pairs with the **`dx-showcase-gen`** tool (`.deepx/tools/src/dx_showcase_gen/`),
which owns the deterministic mechanics. This skill owns the orchestration, the
KB-based judgment, and the human-in-the-loop steps a tool cannot do.

## Trigger Words

"add a showcase", "create a showcase", "showcase 만들/추가/제작", "build a demo for the README", <!-- KOREAN-OK: trigger words include Korean so agents recognize Korean showcase requests -->
"promote this as a showcase".

## Hard rules (the recurring mistakes, as gates)

1. **Record the REAL claude code screen** — never a synthetic/rendered substitute.
   The build runs in a visible terminal and is captured with `dx-showcase-gen`'s
   x11grab path. (If a human is present, prefer the real interactive claude TUI.)
2. **Capture the build's `--output-format stream-json` STDOUT to a file.** The
   COMPLETE transcript (with Wall-clock + Cost + the closing narration) is rendered
   from that capture AFTER the process exits — the in-session sentinel reads the
   session store, which has no `result` event and is therefore incomplete.
3. **MUST read the routed `.deepx/toolsets/*` before generating code** — the build
   reads the canonical KB (e.g. `ultralytics-train-eval.md`, `ultralytics-deepx-export.md`)
   rather than improvising from prior outputs/memory. `verify` FAILS a showcase whose
   transcript read **no** toolset (the pills gap).
4. **Tool/model are explicit and verified**: `tool=claude`, `model=claude-opus-4-8`
   (the recommended model) unless the user overrides. `verify` checks them.
5. **Artifacts must actually be copied** into the showcase dir and made portable.
6. **No DONE without `dx-showcase-gen verify` PASS.**
7. **Every showcase MUST have an entry in `dx-agentic-dev-showcase/showcases.json`** —
   the manifest is the single source for the root-README card grid, the showcase catalog,
   and the docs `00_Agentic_Development` table. `verify` fails (and `regen-docs` warns) if
   a showcase dir is missing from it — this is how `ultralytics-yolo-deepx-export` once went
   missing from the docs table. NEVER hand-edit the generated `dx-showcase:docs:*` marker
   regions; add to the manifest and run `regen-docs`.

## Setup

```bash
# Make the tool importable (editable) or use PYTHONPATH:
export PYTHONPATH="$(git rev-parse --show-toplevel)/.deepx/tools/src"
SG() { python3 -m dx_showcase_gen.cli "$@"; }   # or the installed `dx-showcase-gen`
```

## Phase 1 — Requirements + prompt synthesis (KB)

- Gather the showcase scenario (what the showcase demonstrates, the target user).
- Synthesize the **end-user-style** natural-language build prompt — the prompt a real
  user would type, no operator scaffolding. (Headless/unattended runs may append
  "work autonomously … / Respond in English"; if so, that scaffolding is **trimmed
  from the displayed prompt** in the showcase README — see Phase 7.)
- The prompt MUST also require a **visualized detection sample**: an annotated image of
  the (retrained/exported) model run on a representative domain sample, saved as
  `sample_detect.jpg` — this is shown beside the build GIF in the README (Phase 7).
- Fix `tool=claude`, `model=claude-opus-4-8`.
- In autopilot (user absent), pick scenario defaults from the KB; do not block.

## Phase 2 — Recording-prep gate (human-in-the-loop)

- Guide the user to **clear a screen region** and open a terminal there; the build
  terminal must not be overlapped by other windows for the whole recording.
- WAIT for explicit "ready" before starting. In autopilot, launch the build terminal
  in an already-cleared region and crop to its rect (capture full screen, post-crop).

## Phase 3 — Recorded build (real claude screen)

```bash
SG keepawake start --pidfile /tmp/sc.ka.pid                 # stop GNOME blanking
SG capture-start --output /tmp/sc.raw.mp4 --pidfile /tmp/sc.ff.pid   # full-screen
# Run the build in the prepared, titled terminal, TEEING stream-json:
#   claude -p "<PROMPT>" --model claude-opus-4-8 \
#     --output-format stream-json --verbose | tee /tmp/sc.stream.jsonl
# (interactive real-TUI runs are captured the same way — the human runs claude.)
SG capture-stop --pidfile /tmp/sc.ff.pid ; SG keepawake stop --pidfile /tmp/sc.ka.pid
SG crop --input /tmp/sc.raw.mp4 --output /tmp/sc.crop.mp4 --title DEEPXBUILDREC
SG gif  --input /tmp/sc.crop.mp4 --output docs/source/img/dx-agentic-dev-<name>-build.gif \
        --duration <recorded_secs>
```

- **Headless unattended fallback** (no human to run the interactive TUI): launch a
  titled gnome-terminal that `tail -f`s a styled render of the streamed events while
  `claude -p … --output-format stream-json | tee … | render >> log` runs separately.
  This is still a real screen capture. The render MUST preserve newlines (so the
  DEEPX banner renders) and must be cropped to the terminal rect.
- If the agent stops at the brainstorm approval gate, add
  "work autonomously to completion; produce the actual artifacts" to the prompt.

## Phase 4 — COMPLETE transcript

```bash
SG transcript --stream-json /tmp/sc.stream.jsonl \
   --session-id <uuid> --project "$(git rev-parse --show-toplevel)" \
   --out-dir dx-agentic-dev-showcase/<name>
```

- This writes `claude-code-session.{md,html,jsonl}` and **fails** unless the stream
  carries a `result` event (⇒ Wall-clock + Cost). Never substitute the in-session
  sentinel output for the showcase transcript.

## Phase 5 — Artifact copy + portability

```bash
SG copy-artifacts --session-dir <build_session_dir> --showcase-dir dx-agentic-dev-showcase/<name>
```

- Copies the generated files (skips venv / *.pt / *.onnx / *.dxnn / caches) and prints
  any absolute/session-specific path refs. **Fix every flagged ref** so the showcase
  runs standalone (SCRIPT_DIR / SUITE_ROOT relative; auto-download instead of /tmp).

## Phase 6 — Run/result GIF

- Record the generated app running (or the report/eval run) → a second GIF
  `docs/source/img/dx-agentic-dev-<name>-run.gif` via the same capture→crop→gif path.
  Optional when the showcase has no visual runtime (then the build GIF suffices).

## Phase 7 — Catalog + docs (manifest-driven, single source)

The showcase's OWN README is written in its dir; the THREE cross-showcase surfaces (root
README card grid, showcase catalog, docs `00_Agentic_Development` table) are GENERATED from
one manifest — never hand-edited.

1. Write the showcase's `README.md` / `README-ko.md` in its dir: the **verbatim end-user
   prompt** (scaffolding trimmed), the session-metrics table (model, **Wall-clock**,
   **Cost**, turns, skills), the **2-column GIF | sample** block, transcript links, run steps.
2. Add an entry to **`dx-agentic-dev-showcase/showcases.json`** (order = display order):
   `name, kind (game|export|retrain), category (one of the `categories[].id`, e.g.
   `ultralytics` / `npu-apps` — showcases are grouped by category in every surface;
   add a new category to `categories[]` if none fits), title_en/ko, tagline_en/ko, what_en/ko,
   highlight_en/ko, model, build, turns, tokens, cost`, plus the **card media**:
   `card_media` = `gif` (games → `gif` basename), `sample` (retrain → `sample` basename,
   prefer a **landscape** annotated detection image), or `video` (export → `video` +
   `poster` basenames, an mp4 clip). All media basenames live under `docs/source/img/`;
   the card grid renders them at a **uniform height** so mixed aspect ratios still align.
3. Regenerate all three surfaces (EN+KO), idempotently:
   ```bash
   SG regen-docs --repo-root "$(git rev-parse --show-toplevel)"
   ```
   This fills the `dx-showcase:docs:{cardgrid,catalog,table}` marker regions in the root
   README(-KO), `dx-agentic-dev-showcase/README(.md/-ko.md)`, and
   `docs/source/00_Agentic_Development(.md/_kor.md)`. The catalog is surfaced in the mkdocs
   nav via `docs/source/00b_Agentic_Development_Showcases.md` (include-markdown) — no nav
   edit needed per showcase.

Do NOT duplicate per-showcase detail into the suite README or 00_Agentic_Development, and
do NOT hand-edit the marker regions — they are regenerated from the manifest.

## Phase 8 — VERIFY gate (no DONE without PASS)

```bash
SG verify --showcase-dir dx-agentic-dev-showcase/<name> --name <name> \
   --stream-json /tmp/sc.stream.jsonl --model claude-opus-4-8 --tool claude \
   --gif docs/source/img/dx-agentic-dev-<name>-build.gif \
   --require-file run.sh --require-file README.md \
   --augment-target README.md --augment-target README-KO.md
```

Must print `RESULT: PASS`. The gate checks: transcript present + complete
(Wall-clock/Cost), model/tool match, GIF(s) exist/<10MB/non-black, required files
present + syntax-OK, README/docs carry the showcase marker. Fix any FAIL and re-run.

## Anti-patterns (STOP)

- Using the in-session sentinel transcript for the showcase (missing Wall-clock/Cost).
- A synthetic/rendered "build screen" presented as the real claude UI.
- Declaring DONE before `verify` PASS.
- Committing model binaries (`*.pt`/`*.onnx`/`*.dxnn`) or `venv/` into the showcase.
- Leaving absolute / `/tmp` / session-specific paths in the copied scripts.

## Verification loop (this skill is `.deepx/` source)

Edits here propagate via `dx-agentic-gen generate` → `check` (drift 0) →
`pytest .deepx/tests/conformance/`.
