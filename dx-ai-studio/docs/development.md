# Development

## Requirements

- **Python 3.8+** — the only hard prerequisite (tested on Debian 12/13, Ubuntu 20.04–26.04).
  The studio has **zero third-party runtime dependencies** (pure standard library, ModelZoo
  tab included); `./launcher.sh` self-installs the package (`pip install -e .`) on first
  run, so no manual install is needed.
- Optional, per feature: the sibling SDKs (`dx-runtime`, `dx-compiler`, `dx-modelzoo`)
  and NPU hardware. Setup/reference views do not require a running NPU job, but
  execution needs the relevant runtime, models and runners. Missing SDKs do **not**
  automatically turn inference or Monitor telemetry into mock data.
- DX Cloud AWS operations only: optional `boto3` (`python3 -m pip install -e '.[aws]'`
  from the Studio root in its launch environment). The page/guide work without it.
  Credentials are resolved on the Studio host; AWS CLI is a setup/SSO helper, not
  the backend API transport.
- Tests only: `pip install -r requirements-ci.txt` (pytest, numpy, onnx, playwright, …).

A virtual environment is optional but recommended for running the test suite:

```bash
cd dx-ai-studio
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements-ci.txt   # test/CI extras only
```

## Running everything (the launcher)

```bash
./launcher.sh                 # http://localhost:8890 (sticky port; auto-bumps if busy)
./launcher.sh --port 9000     # preferred launcher port (still bumps if busy)
./launcher.sh --no-browser    # do not auto-open a browser
./launcher.sh --fast          # skip the cosmetic boot animation
./launcher.sh --no-kill       # do not kill our own stale servers first
```

`launcher.sh` kills only *our own* stale `launcher.py` / `dx_*/server.py` processes,
picks a free launcher port (remembered in `dx-ai-studio/.launcher-port`), then execs
`python3 launcher/launcher.py`. The launcher spawns all nine modules on ephemeral
ports and reverse-proxies them — you only ever touch the one launcher port.

## Running a single module standalone

Each module is a self-contained server. Run it directly for focused work
(faster startup, no proxy, easier logs):

```bash
# Run any module's server directly (port defaults to its DEFAULT_PORT):
./.venv/bin/python dx_app/server.py       --port 8080 --no-browser
./.venv/bin/python dx_stream/server.py    --port 8093 --no-browser
./.venv/bin/python dx_modelzoo/server.py  --port 8094 --no-browser
./.venv/bin/python dx_compiler/server.py  --port 8095 --no-browser
./.venv/bin/python dx_planner/server.py   --port 8096 --no-browser
./.venv/bin/python dx_benchmark/server.py --port 8097 --no-browser
./.venv/bin/python dx_monitor/server.py   --port 8098 --no-browser
./.venv/bin/python dx_agent_dev/server.py --port 8099 --no-browser
./.venv/bin/python dx_edge/server.py      --port 8100 --no-browser
```

`--port 0` picks a free ephemeral port. The full studio (all modules + proxy) is
started with `./launcher.sh`.

Common flags for every module server: `--port/-p <N>`, `--no-browser`.

> **Note:** `dx_benchmark`'s server is a pure viewer — it serves the bundled
> `dataset.json` as-is and does not perform runtime aggregation. Actually *running*
> benchmarks happens in the standalone `dx-benchmark` CLI (sibling repo, not part of
> this studio): `cd dx-benchmark && ./run.sh run` (needs the NPU stack).

### Live editing

The servers read static files (JS/CSS/JSON) and templates from disk on **every
request**. Edit a front-end file and just refresh the browser — no server restart
needed. Only Python changes require a restart.

## Environment variables

| Variable | Effect |
|----------|--------|
| `DX_BIND_LOCAL=1` | Bind the launcher to loopback (127.0.0.1) only — module servers always are |
| `DX_BIND_HOST=<host>` | Explicit launcher bind host. A module run on its own and bound off loopback refuses to start without `DX_API_TOKEN` |
| `DX_API_TOKEN=<secret>` | Lets remote API clients in with `Authorization: Bearer <secret>` or `X-DX-Api-Token`; local requests never need it |
| `DX_PAIRING=off` | No browser pairing — remote access only with `DX_API_TOKEN` |
| `DX_SESSION_DAYS=<n>` | How long a paired remote browser stays connected (default 30) |
| `DX_ALLOWED_HOSTS=<a,b>` | Extra host names the servers answer to (IP hosts and localhost always do) |
| `DX_COMPILER_ALLOWED_ROOTS=<dir:dir>` | Extra folders `/compile` may read from and write to |
| `DX_<MODULE>_PORT` | Launcher proxy-map port override (see architecture port table) |
| `DX_APP_ROOT` / `DX_COMPILER_ROOT` / `DX_RUNTIME_ROOT` / `DX_STREAM_ROOT` | SDK source-tree locations (default: sibling suite dirs) |
| `DX_NO_BROWSER=1` | Suppress browser auto-open (also implied under SSH/VS Code remote) |
| `DX_MONITOR_SKIP_HARDWARE_INIT=1` | Bypass Monitor hardware initialization; NPU telemetry stays unavailable, not synthetic |
| `DX_MONITOR_EXPLICIT_MOCK=1` | Explicit demo telemetry, labelled Mock, when Monitor initialization is enabled; not a hardware test |
| `DX_AGENT_ADAPTER=mock` | DX Agent Dev deterministic mock adapter (closed-net) |
| `DX_HARNESS_ROOT=<path>` | Path to the `dx-all-suite` checkout root, for the `.deepx` harness (agent knowledge/skills) that `dx_agent_dev` needs. Defaults to the auto-detected suite root when run from within the suite; without it (and no discoverable default) agent-dev degrades to a harness-missing notice. |
| `DX_CHAT_KNOWLEDGE_SYNC=1` | Regenerate the chat SDK-knowledge cache from the suite docs |

### Checking runtime-dependent paths

- **App/Stream:** the managed launch gate requires an active profile or successful
  live validation of that module's own contracts. If blocked, open Stream **Setup →
  DX-Runtime Dependencies**, resolve the reported driver/runtime/plugin issues,
  validate and retry. Do not replace a missing-runtime error with fabricated output.
- **DX App's Graph Composer:** build/provide `multi_model_graph_sync` or
  `multi_model_graph_async` in `DX_APP_ROOT`'s build/bin search paths, prepare the
  graph's model artifacts, validate, then run. Validation calls the runner's `--check`;
  it is not just browser schema validation. Graph Live also needs its display/capture
  tools (Xvfb/libxcb/Pillow); video frame extraction uses `ffmpeg`. Projects, run
  artifacts and C++ ZIP exports are separate under `outputs/dx_app/graph/`.
  Project history retains the newest 50 saves.
- **NPU contention:** graph run-once, graph Live, Run-page Live and gallery builds
  share `dx_app/core/npu_jobs.py`. Run-page Live slots may coexist, but graph/gallery
  jobs exclude them. Stop or wait for the named holder, then retry. This registry
  does not lock arbitrary NPU programs outside Studio App.
- **Monitor:** native telemetry runs in `telemetry_worker.py` under its runtime
  interpreter/environment. The HTTP process reads the supervisor cache. Check the
  displayed `real` / `stale` / `unavailable` / explicit `mock` state and diagnostics,
  not just SSE connectivity. For an unavailable NPU, restore the runtime/driver and
  inspect worker errors; use explicit mock only for a clearly labelled UI exercise.

For example, compare these standalone Monitor starts (run one at a time; stop it
before the next). The first bypasses hardware and shows unavailable NPU telemetry;
the second explicitly requests demo values if real telemetry is unavailable:

```bash
DX_MONITOR_SKIP_HARDWARE_INIT=1 python3 dx_monitor/server.py --port 8098 --no-browser
# Separate run: do not combine SKIP_HARDWARE_INIT with EXPLICIT_MOCK
DX_MONITOR_EXPLICIT_MOCK=1 python3 dx_monitor/server.py --port 8098 --no-browser
```

Visual fixtures and mock runners test UI/contracts, not actual NPU performance or
AWS deployment. Keep their results separate from hardware measurements and
documentation screenshots; see the pixel visual regression section in
[testing.md](testing.md).

## i18n workflow

Six locales: `en`, `ko`, `ja`, `es`, `zh-CN`, `zh-TW`. Two mechanisms coexist:

1. **Static markup** — `[data-i18n]` attributes and per-language spans
   (`<span class="en">…</span><span class="ko">…</span>`), toggled by
   `body.lang-<code>` and `shared/static/i18n.js` (`window.DXI18n`).
2. **Dynamic strings** — `T('English key')` looked up in each module's dictionary
   (`static/js/i18n.js`, or `stream-i18n.js` / `compiler-i18n.js`). Language is stored
   in `localStorage['dx-lang']`; the launcher drives module iframes via
   `postMessage {type:'dx-lang-change'}`.

When adding UI strings: add the key to the module dictionary, re-render it from the
module's lang-refresh hook (so a language switch does not leave stale text), then run
the audit:

```bash
./.venv/bin/python -m tools.i18n_audit --repo . \
  --output-json /tmp/i18n.json --output-md /tmp/i18n.md \
  --fail-on-findings --fail-on-runtime-gaps
# expect: findings=0
```

`tools.i18n_audit` extracts the full copy inventory across modules, flags
missing-language findings and JS runtime lang-hook gaps, and (with the `--fail-on-*`
flags) exits 2 when a gate is violated. `bash scripts/i18n_audit_gate.sh` bundles the
audit + `pytest tests/i18n_audit/`. Browser copy/zoom audits across all 6 locales run
via Playwright (`bash scripts/run_ci.sh --browser`).

## Conventions

- Python: stdlib-first, minimal dependencies. HTTP transport in `server.py`, business
  logic in `core/`.
- Front-end: vanilla JavaScript, no framework. Module-local CSS loads last, after the
  shared `dx-tokens/base/utilities` foundation in `shared/static/`.
- Themes: dark, light and system (`shared/static/dx-theme.js`, default `system`). Colours come from
  tokens (`dx-tokens.css`, `dx-theme-light.css`); a new raw hex fails the CSS-token ratchet.
- Do not stage runtime artifacts (`launcher/.ports/`, `*.launcher-*`, generated
  catalogs); see `.gitignore`.
- Gotcha: avoid `Path.is_relative_to()` and `str.removeprefix/removesuffix` (3.9+) —
  `tests/shared/test_python_floor.py` guards the string ones. The studio supports Python 3.8, so
  use `path.resolve().relative_to(root.resolve())` and catch `ValueError` instead
  (see `dx_modelzoo/server.py`).
