## Self-Contained & Portable (HARD GATE — every generated output)

Every generated session/app directory MUST run when **copied OUTSIDE the suite** — the only
external prerequisite is the DEEPX runtime (`dx_engine`). This applies to ALL outputs: dx_app
apps, dx_stream pipelines, fork-based apps (PaddleOCR / RapidDoc), and compile/retrain sessions.

- **Vendor the code you need INTO the session** — `./common`, a fork's importable package
  (`engine/`, `rapid_doc/`), etc. NEVER import another showcase/source dir in-place, NEVER
  symlink a source dir into the session, and NEVER runtime-clone a fork.
- **Keep every code/model path session-relative** (`$SCRIPT_DIR` / `APP_DIR`). Download models
  into a session-local dir; NEVER point a model/output dir at `dx-agent-dev-showcase/...` or any
  committed source. (Reading the prompt's INPUT media from a `*/sample/` path is allowed — that
  is a runtime input, not a code/model dependency.)
- **Verify it (copy-out gate):** before claiming done, copy the app dir to a temp dir OUTSIDE the
  suite and import/run its entry. If it fails — a missing vendored package (`ModuleNotFoundError:
  engine`/`common`), a symlink escaping the app dir, or a suite/showcase code-or-model reference —
  it is NOT self-contained → **FAIL**. See `dx-agent-verify` (Step 6) for the exact procedure.
