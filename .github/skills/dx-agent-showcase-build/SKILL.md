---
name: dx-agent-showcase-build
description: 'Build a dx-agent-dev showcase end-to-end: KB-based prompt → recorded real build → complete transcript → artifacts
  → GIFs → README/docs. RIGID gates prevent recurring mistakes.'
---

<!-- AUTO-GENERATED from .deepx/ — DO NOT EDIT DIRECTLY -->
<!-- Source: .deepx/skills/dx-agent-showcase-build/SKILL.md -->
<!-- Run: dx-agent-gen generate -->

# Skill: Build a dx-agent-dev Showcase

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
3. **MUST read the routed `.github/toolsets/*` before generating code** — the build
   reads the canonical KB (e.g. `ultralytics-train-eval.md`, `ultralytics-deepx-export.md`)
   rather than improvising from prior outputs/memory. `verify` FAILS a showcase whose
   transcript read **no** toolset (the pills gap).
4. **Tool/model are explicit and verified**: `tool=claude`, `model=claude-opus-4-8`
   (the recommended model) unless the user overrides. `verify` checks them.
5. **Artifacts must actually be copied** into the showcase dir and made portable.
6. **No DONE without `dx-showcase-gen verify` PASS.**
7. **Every showcase MUST have an entry in `dx-agent-dev-showcase/showcases.json`** —
   the manifest is the single source for the root-README card grid, the showcase catalog,
   and the docs `00_Agent_Driven_Development` table. `verify` fails (and `regen-docs` warns) if
   a showcase dir is missing from it — this is how `ultralytics-yolo-deepx-export` once went
   missing from the docs table. NEVER hand-edit the generated `dx-showcase:docs:*` marker
   regions; add to the manifest and run `regen-docs`.
8. **External repos: clone fresh into the build's session dir; NEVER touch a user repo.**
   When the build needs a third-party/DEEPX-fork checkout (e.g. RapidDoc, PaddleOCR-deepx),
   the prompt/build MUST `git clone` it into a **temp/isolated dir** — it MUST NOT
   discover (`find /`) and **reuse, modify, or delete** a pre-existing repo elsewhere on
   disk (e.g. under `~/git/`). Deleting a user's repo is a destructive action and has
   happened. And **provision models with the fork's model-download script in the FOREGROUND**
   — never hand-compile `.dxnn`, and never launch the download/compile as a **background
   task**: a headless `claude -p` cannot resume on the completion notification and deadlocks
   (the recurring PaddlePaddle build freeze).
9. **Fork-based apps MUST be a GENERATED standalone app — not a wrapper around the fork's
   demo.** When the showcase is "build an app on a third-party fork" (RapidDoc, PaddleOCR),
   the deliverable is the agent's **own entry program** that imports the fork's pipeline API
   as a library; the showcase must be **runnable from its own dir**. Concretely: (a) the
   build clones the fork only to obtain source, then **vendors the importable package** into
   the app (the fork is not re-cloned at run time); (b) `run.sh` runs the **generated entry**
   (`pdf_to_markdown.py` / `ocr_video.py`) — a `run.sh` that shells out to the fork's
   `demo/demo_offline.py` (or any `demo/*`/example) is a **FAIL**, not an app; (c) only the
   NPU **models** are downloaded by `setup.sh` (never committed). `verify` enforces (b).
   **(d) Portability verify (HARD GATE):** the verify step MUST **copy the produced app dir to
   a temp dir OUTSIDE the suite and run its entry** there — if it fails because it imported a
   source/showcase dir in-place (no engine/`common`/models when copied out), it is NOT
   self-contained → **FAIL**. **NEVER** import another showcase's `engine/`/package in-place,
   **NEVER** symlink a source dir into the session, and **NEVER** point a model/output dir at
   `dx-agent-dev-showcase/...` — vendor the pipeline INTO the app and keep all code/model
   paths app-relative (`$SCRIPT_DIR`/`APP_DIR`). This applies to **every** fork-based AND
   dx_app showcase (and is the same self-containment retrain-eval requires per §6 of
   `dx-compiler/.github/toolsets/ultralytics-train-eval.md`).
10. **dx_app-based showcases MUST follow the dx_app relocatable script patterns.** A
    showcase whose app uses a dx_app model / `dx_engine` MUST author `setup.sh`/`run.sh` per
    `dx-runtime/dx_app/.github/skills/dx-agent-app-build-python/SKILL.md` — run.sh: derive the
    model path from `$SUITE_ROOT/dx-runtime/dx_app/assets/models/…`, NEVER an ancestor-walked
    `${DX_APP_ROOT:-}/…` (collapses to an unresolvable path once relocated — the squat
    model-not-found bug); setup.sh: reuse `venv-dx-runtime` or write a `dx_runtime_bridge.pth`,
    NEVER a local venv that only FATALs on missing `dx_engine` (the stretching
    `ModuleNotFoundError` bug). Retrain-eval showcases MUST be self-contained per
    `dx-compiler/.github/toolsets/ultralytics-train-eval.md` §6 (no absolute paths in `*.json`;
    regenerate-if-missing). `verify` enforces all three (model-discovery / venv-bridge / abs-paths).

## Setup

```bash
# Make the tool importable (editable) or use PYTHONPATH:
export PYTHONPATH="$(git rev-parse --show-toplevel)/.deepx/tools/src"
SG() { python3 -m dx_showcase_gen.cli "$@"; }   # or the installed `dx-showcase-gen`
```

## Phase 1 — Requirements + prompt synthesis (KB)

- Gather the showcase scenario (what the showcase demonstrates, the target user).
- Synthesize the **end-user-style** natural-language build prompt — the prompt a real
  user would type, no operator scaffolding. Keep it **short and goal-only**: name NO
  toolset path, KB file, repo branch, or env script — the skill + the routing table supply
  those from the task vocabulary, and a concise prompt that still builds correctly is the
  whole point of the showcase. (Headless/unattended runs may append "work autonomously … /
  Respond in English"; if so, that scaffolding is **trimmed from the displayed prompt** in
  the showcase README — see Phase 7.)
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
SG gif  --input /tmp/sc.crop.mp4 --output docs/source/img/dx-agent-dev-<name>-build.gif \
        --duration <recorded_secs>
```

- **Headless unattended fallback** (no human to run the interactive TUI): launch a
  titled gnome-terminal that runs the build while **LIVE-rendering the stream to the
  screen** so the recording captures the build AS IT HAPPENS. The build command MUST pipe
  stream-json through the renderer to the terminal in real time, NOT redirect-to-file:
  ```bash
  # CORRECT — live: render prints to the terminal as events arrive (tee keeps the raw for the transcript)
  stdbuf -oL claude -p "<PROMPT>" … --output-format stream-json --verbose --dangerously-skip-permissions \
    | tee stream.jsonl | stdbuf -oL python3 render.py
  ```
  The render MUST preserve newlines (so the DEEPX banner renders) and be cropped to the
  terminal rect. **HARD: never `claude … > stream.jsonl` then render at the end** — that
  leaves the screen static during the build, so the GIF shows a frozen "BUILDING" screen
  instead of the real build (a recurring mistake). `verify` rejects a static (no-motion) GIF.
- If the agent stops at the brainstorm approval gate, add
  "work autonomously to completion; produce the actual artifacts" to the prompt.

## Phase 4 — COMPLETE transcript

```bash
SG transcript --stream-json /tmp/sc.stream.jsonl \
   --session-id <uuid> --project "$(git rev-parse --show-toplevel)" \
   --out-dir dx-agent-dev-showcase/<name>
```

- This writes `claude-code-session.{md,html,jsonl}` and **fails** unless the stream
  carries a `result` event (⇒ Wall-clock + Cost). Never substitute the in-session
  sentinel output for the showcase transcript.

## Phase 5 — Artifact copy + portability

```bash
SG copy-artifacts --session-dir <build_session_dir> --showcase-dir dx-agent-dev-showcase/<name>
```

- Copies the generated files (skips venv / caches / heavy recordings / runtime-download
  dirs) and prints any absolute/session-specific path refs **in scripts AND data files
  (`*.json`)**. **Fix every flagged ref** so the showcase runs standalone (SCRIPT_DIR /
  SUITE_ROOT relative; auto-download instead of /tmp; no absolute `best_pt`/`save_dir` in
  `train_result.json`).
- **Curated run-evidence is a committed deliverable (retrain/export showcases).** The
  produced models and training evidence MUST be copied in and committed so a fresh
  `git clone` carries the real artifacts (no recompile needed) — this is the recurring
  "`runs/` + `*_deepx_model/` were regenerated locally but never committed" gap:
  - `*_deepx_model/` — the DeepX export dir(s) **with `config.json` + `metadata.yaml` +
    the `.dxnn`** (base and retrained).
  - `runs/<train>/` training evidence: `results.png`, `confusion_matrix*.png`,
    `Box*_curve.png`, `results.csv`, `args.yaml`, `val_batch*_pred.jpg`, and
    `weights/best.pt` (the retrained weights). `last.pt` is optional.
  - `metrics.json` + `sample_detect.jpg`.
  The `.gitignore` re-includes `*.dxnn/*.onnx/*.pt` under `dx-agent-dev-showcase/**`
  (only env/cache/`download`/`dxnn_models`/`output` dirs stay ignored), and
  `verify` FAILS a retrain/export showcase missing this evidence. After copy, **`git add`
  the deliverables explicitly** (they are untracked until added).

## Phase 6 — Run/result GIF

- Record the generated app running (or the report/eval run) → a second GIF
  `docs/source/img/dx-agent-dev-<name>-run.gif` via the same capture→crop→gif path.
  Optional when the showcase has no visual runtime (then the build GIF suffices).

## Phase 7 — Catalog + docs (manifest-driven, single source)

The showcase's OWN README is written in its dir; the THREE cross-showcase surfaces (root
README card grid, showcase catalog, docs `00_Agent_Driven_Development` table) are GENERATED from
one manifest — never hand-edited.

1. Write the showcase's `README.md` / `README-ko.md` in its dir: the **verbatim end-user
   prompt** (scaffolding trimmed), the session-metrics table (model, **Wall-clock**,
   **Cost**, turns, skills), the **2-column GIF | sample** block, transcript links, run steps.
2. Add an entry to **`dx-agent-dev-showcase/showcases.json`** (order = display order):
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
   README(-KO), `dx-agent-dev-showcase/README(.md/-ko.md)`, and
   `docs/source/00_Agent_Driven_Development(.md/_kor.md)`. The catalog is surfaced in the mkdocs
   nav via `docs/source/00b_Agent_Driven_Development_Showcases.md` (include-markdown) — no nav
   edit needed per showcase.

Do NOT duplicate per-showcase detail into the suite README or 00_Agent_Driven_Development, and
do NOT hand-edit the marker regions — they are regenerated from the manifest.

## Phase 8 — VERIFY gate (no DONE without PASS)

```bash
SG verify --showcase-dir dx-agent-dev-showcase/<name> --name <name> \
   --stream-json /tmp/sc.stream.jsonl --model claude-opus-4-8 --tool claude \
   --gif docs/source/img/dx-agent-dev-<name>-build.gif \
   --require-file run.sh --require-file README.md \
   --augment-target README.md --augment-target README-KO.md
```

Must print `RESULT: PASS`. The gate checks: transcript present + complete
(Wall-clock/Cost), model/tool match, GIF(s) exist/<10MB/non-black, required files
present + syntax-OK, README/docs carry the showcase marker. Fix any FAIL and re-run.

## Anti-patterns (STOP)

- Using the in-session sentinel transcript for the showcase (missing Wall-clock/Cost).
- A synthetic/rendered "build screen" presented as the real claude UI.
- A **static build GIF** — redirecting the stream to a file and rendering only after the
  build leaves the screen frozen on "BUILDING …". The screen MUST be live-rendered during
  the build (Phase 3); `verify`'s gif-not-static check fails otherwise.
- Declaring DONE before `verify` PASS.
- Committing `venv/`, caches, or **runtime-download** dirs (`download/`, `dxnn_models/`,
  `onnx_models/`, `output/`) into the showcase. (The produced model artifacts —
  `*.dxnn`/`*.onnx`/`best.pt` **directly in a retrain/export showcase**, e.g. under
  `*_deepx_model/` or `runs/**/weights/` — ARE curated deliverables and MUST be committed;
  see Phase 5. Only fork/game showcases keep their downloaded model-zoo binaries under the
  ignored download dirs.)
- **Omitting the curated run-evidence** (`runs/` plots + `*_deepx_model/{config,metadata,.dxnn}`
  + `best.pt`) from a retrain/export showcase — `verify` FAILS on it (Phase 5 / Phase 8).
- Leaving absolute / `/tmp` / session-specific paths in the copied scripts.
- **Reusing or deleting a pre-existing user repo** found via `find` — clone fresh into the
  session dir instead (see hard rule 8).
- **Backgrounding the model download/compile** in a headless build, or hand-compiling
  `.dxnn` instead of running the fork's model-download script in the foreground — both deadlock the build.
- **A fork-based showcase whose `run.sh` just calls the fork's `demo/demo_offline.py`** — that
  is wrapping the example, not generating an app, and the showcase isn't runnable once moved
  (the clone isn't copied). Generate a standalone entry over the vendored package (hard rule 9).
- **A dx_app-based showcase whose `run.sh` ancestor-walks for `DX_APP_ROOT`** (model not found
  once relocated) or whose `setup.sh` makes a local venv without a `dx_engine` bridge — follow
  the dx_app skill's relocatable templates (hard rule 10).
- **An absolute build-session path serialized into a showcase data file** (`train_result.json`
  `best_pt`) — the showcase must be self-contained (regenerate-if-missing; ultralytics §6).

## Fixing the KB when a build repeats a mistake (template > prose)

A showcase build is the KB's test: when the generated `setup.sh` / `run.sh` / app **repeats
a known mistake**, the fix belongs in the KB — but HOW you write it decides whether the
NEXT build is actually different. This was proven the hard way (squat/stretching/ppe
regeneration):

- **Template code or a concrete copy-paste pattern changes agent output. A bare "don't do
  X" prose note usually does NOT.** The squat `run.sh` regenerated the exact
  `${DX_APP_ROOT:-}/assets/models` ancestor-walk **despite** a prose anti-pattern note — it
  only changed once the KB shipped a **canonical model-resolution block + a WRONG✗/RIGHT✓
  example**. By contrast the stretching fix landed first try (a setup.sh **template code**
  change: venv-search broadening + dx_engine bridge) and the ppe fix landed first try (the
  KB gave a **concrete pattern to copy** — the wildlife self-contained `pipeline.py`,
  HERE-relative, regenerate-if-missing).
- **Pair every KB fix with a `dx-showcase-gen verify` check** that statically fails the
  mistake. The gate is the backstop when a regenerated build still drifts; prose + no gate
  = a silent regression that ships. (`verify` already enforces the run.sh model-discovery /
  setup.sh dx_engine-bridge / build-session-path checks — extend it when you add a rule.)
- **Order**: (1) add/strengthen a `verify` check that FAILS the current artifact (RED),
  (2) put the corrected pattern in the KB as **template code or a copy-paste block with a
  WRONG✗/RIGHT✓ pair** (not just a warning), (3) regenerate via the build prompt and confirm
  the check now PASSES (GREEN). If the rebuild still repeats the mistake, the KB statement
  was prose — make it concrete code, do not just reword it.

## Verification loop (this skill is `.deepx/` source)

Edits here propagate via `dx-agent-gen generate` → `check` (drift 0) →
`pytest .deepx/tests/conformance/`.
