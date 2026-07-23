# Development

## Requirements

- **Python 3.8+** — the only hard prerequisite (tested on Debian 12/13, Ubuntu 20.04–26.04).
  The studio has **zero third-party runtime dependencies** (pure standard library, ModelZoo
  tab included); `./launcher.sh` self-installs the package (`pip install -e .`) on first
  run, so no manual install is needed.
- Optional, per module: the sibling SDKs (`dx-runtime`, `dx-compiler`, `dx-modelzoo`)
  and NPU hardware. Each module degrades to mock data when its SDK is absent, so the
  GUI is fully browsable without an NPU.
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
./launcher.sh --port 9000     # pin a launcher port
./launcher.sh --no-browser    # do not auto-open a browser
./launcher.sh --fast          # skip the cosmetic boot animation
./launcher.sh --no-kill       # do not kill our own stale servers first
```

`launcher.sh` kills only *our own* stale `launcher.py` / `dx_*/server.py` processes,
picks a free launcher port (remembered in `launcher/.launcher-port`), then execs
`python3 launcher/launcher.py`. The launcher spawns all eight modules on ephemeral
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
| `DX_BIND_LOCAL=1` | Bind servers to loopback (127.0.0.1) only |
| `DX_BIND_HOST=<host>` | Explicit bind host |
| `DX_API_TOKEN=<secret>` | Require `Authorization: Bearer <secret>` or `X-DX-Api-Token` |
| `DX_<MODULE>_PORT` | Launcher proxy-map port override (see architecture port table) |
| `DX_APP_ROOT` / `DX_COMPILER_ROOT` / `DX_RUNTIME_ROOT` / `DX_STREAM_ROOT` | SDK source-tree locations (default: sibling suite dirs) |
| `DX_NO_BROWSER=1` | Suppress browser auto-open (also implied under SSH/VS Code remote) |
| `DX_MONITOR_SKIP_HARDWARE_INIT=1` | DX Monitor mock mode (no `dx_engine`) |
| `DX_AGENT_ADAPTER=mock` | DX Agent Dev deterministic mock adapter (closed-net) |
| `DX_HARNESS_ROOT=<path>` | Path to the `dx-all-suite` checkout root, for the `.deepx` harness (agent knowledge/skills) that `dx_agent_dev` needs. Defaults to the auto-detected suite root when run from within the suite; without it (and no discoverable default) agent-dev degrades to a harness-missing notice. |
| `DX_CHAT_KNOWLEDGE_SYNC=1` | Regenerate the chat SDK-knowledge cache from the suite docs |

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
- The product is **dark-mode only** (light mode was removed).
- Do not stage runtime artifacts (`launcher/.ports/`, `*.launcher-*`, generated
  catalogs); see `.gitignore`.
- Gotcha: avoid `Path.is_relative_to()` (3.9+) — the studio supports Python 3.8, so
  use `path.resolve().relative_to(root.resolve())` and catch `ValueError` instead
  (see `dx_modelzoo/server.py`).
