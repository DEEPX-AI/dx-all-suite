# Architecture

DX AI Studio is a browser front-end that unifies the DEEPX NPU SDK tools into one
experience. It is a **launcher hub** plus **eight independent module servers**, all
built on the Python standard-library `http.server` (no FastAPI/Flask/Node). It has
**no third-party runtime dependencies** — pure Python standard library (3.8+),
including a tiny built-in template renderer for DX Compiler (no Jinja2) and a stdlib
`html.parser` DOM for the dx_app Model Zoo tab (no BeautifulSoup, no requests).

## Big picture

```
Browser ──▶ Launcher :8890 ──(reverse proxy)──▶ dx_app       :8080  /app/
             (single page shell)               dx_stream    :8093  /stream/
             Home grid · SDK Library ·          dx_modelzoo  :8094  /zoo/
             About DEEPX                        dx_compiler  :8095  /compiler/
                                                dx_planner   :8096  /planner/
                                                dx_benchmark :8097  /benchmark/
                                                dx_monitor   :8098  /dx_monitor/
                                                dx_agent_dev :8099  /agent/

shared/dx_server.py  ← base HTTP handler + server wrapper for ALL servers
shared/chat/         ← ChatEngine (per-module AI assistant)
shared/hardware.py   ← NPU / CPU / memory telemetry (DX Monitor + HW widget)
shared/static/       ← i18n, toolbar, tutorial engine, design tokens
```

## The proxy model

The launcher is both a **process supervisor** and a **reverse proxy**
(`launcher/launcher.py`, ~1470 lines):

1. **Spawn** — on boot it starts each module as a detached subprocess
   (`python3 <module>/server.py --port 0 --no-browser`, `preexec_fn=os.setsid`).
   Modules bind an **OS-assigned ephemeral port** (`--port 0`), so there is zero
   port collision on shared hosts.
2. **Port handshake** — each child writes its real port to `launcher/.ports/<id>.port`
   (path passed via the `DX_PORT_FILE` env var). The launcher blocks up to 20 s on
   `_await_reported_port` and records the discovered port in `_LAUNCHER_PROXY_PORTS`.
   The fixed `80xx` numbers are **defaults/fallbacks** (used for standalone runs and
   the `DX_*_PORT` overrides), not what the launcher uses at runtime.
3. **Route** — incoming requests are mapped to a target port by, in order:
   path prefix (`shared/auth_policy.py::map_launcher_proxy`), then `Referer`
   (`_proxy_by_referer`), then API-path fallback (`_DX_APP_APIS`, `_DX_MONITOR_APIS`)
   for EventSource/fetch calls that lack a usable prefix.
4. **Proxy** — `_proxy()` forwards over `http.client` to `127.0.0.1:<port>`, strips
   hop-by-hop headers, streams SSE line-by-line, and injects the hardware-monitor
   widget into HTML responses (all modules except `dx_monitor` and `dx_agent_dev`).
5. **Supervise** — a watchdog thread polls each module (process alive + port open) and
   restarts a dead module up to 3 times / 120 s, else marks it `unavailable`.

Top-level browser navigations (deep links, F5) are detected via `Sec-Fetch-Dest`/
`Accept` and served the launcher shell, which then routes client-side into an iframe.

## Port map

| Module | Dir | Default port | Launcher prefix | `DX_*_PORT` override |
|--------|-----|--------------|-----------------|----------------------|
| Launcher | `launcher/` | 8890 | *(host)* | `DX_LAUNCHER_PORT` |
| DX App | `dx_app/` | 8080 | `/app/` | `DX_APP_PORT` |
| DX Stream | `dx_stream/` | 8093 | `/stream/` | `DX_STREAM_PORT` |
| DX Model Zoo | `dx_modelzoo/` | 8094 | `/zoo/` | `DX_ZOO_PORT` |
| DX Compiler | `dx_compiler/` | 8095 | `/compiler/` | `DX_COMPILER_PORT` |
| DX EdgeGuide | `dx_planner/` | 8096 | `/planner/` | `DX_PLANNER_PORT` |
| DX Benchmark | `dx_benchmark/` | 8097 | `/benchmark/` | `DX_BENCHMARK_PORT` |
| DX Monitor | `dx_monitor/` | 8098 | `/dx_monitor/` | `DX_MONITOR_PORT` |
| DX Agent Dev | `dx_agent_dev/` | 8099 | `/agent/` | `DX_AGENT_PORT` |

The `DX_*_PORT` variables are read only by `launcher/launcher.py` (as proxy-map
defaults). The module `server.py` files do **not** read them — a standalone module
takes its port from `--port` (falling back to its `DEFAULT_PORT` constant).

## Shared foundation (`shared/`)

Every server subclasses `DXBaseHandler` (`shared/dx_server.py`) and overrides one
method, `route()`, whose canonical order is:

```
handle_chat_routes(_chat_engine)   # /api/chat* (SSE), config, local models
  → route_common()                 # /, /index.html, /static/*, /static/shared/*
  → module GET/POST branches       # /api/... business endpoints
  → route_legacy()                 # 404 fallback
```

`DXBaseHandler` provides: JSON/HTML/file/bytes responses, static serving with ETag +
gzip + 304 + content-hash cache-busting (`render_html_with_asset_hashes`), multipart
parsing, SSE helpers, optional `DX_API_TOKEN` auth, CORS/origin checks, and a
corporate-TLS CA bridge. `DXServer` wraps CLI parsing, IPv6 dual-stack bind,
port-collision retry, and ephemeral-port reporting via `DX_PORT_FILE`.

- **`shared/chat/`** — `ChatEngine` powers the per-module "DX Chat" assistant.
  Providers: OpenAI, Anthropic, Google (Gemini), a local OpenAI-compatible endpoint,
  and an `agent-cli` backend. Rule-based `FallbackEngine` answers when no key is set.
  Module knowledge lives in `shared/chat/knowledge/*.md` and is auto-synced from the
  suite docs — no manual regen. The launcher pre-syncs it once, unconditionally, at
  boot (single writer, before any module starts); `ChatEngine.stream()` also does a
  lazy, env-gated (`DX_CHAT_KNOWLEDGE_SYNC=1`) fallback sync for a module server run
  standalone without the launcher. Both paths call `knowledge_sync.sync_if_stale()`,
  which writes atomically (temp file + `os.replace()`).
- **`shared/hardware.py`** — `get_hw()` / `get_sysinfo()` collect NPU telemetry (via
  the `dx_engine` SDK + the `dx_npu_stats` helper binary) plus CPU/memory/disk from
  `/proc`. Falls back to synthetic mock data when no NPU/SDK is present.
- **`shared/static/`** — the 6-language i18n runtime (`i18n.js`, `window.DXI18n`),
  unified toolbar, tutorial engine, and design-token CSS (`dx-tokens/base/utilities`).

## DX Agent Dev

`dx_agent_dev` drives installed, authenticated coding-agent CLIs headlessly and
streams their output into the browser console. Five CLI adapters live under
`dx_agent_dev/core/adapters/`: `claude.py`, `copilot.py`, `codex.py`, `cursor.py`,
`opencode.py` (plus a `mock.py` used under `DX_AGENT_ADAPTER=mock` for closed-net/CI
runs). Cursor and OpenCode enumerate models dynamically (`cursor-agent
--list-models`, `opencode models`); both fall back to a static table in
`dx_agent_dev/core/agents_config.py` when the dynamic call fails or times out. It
depends on the `.deepx` harness (agent knowledge/skills) resolved via
`DX_HARNESS_ROOT` — see [`development.md`](development.md#environment-variables).

## Where it sits in dx-all-suite

`dx-ai-studio/` is a sibling of the SDK repos inside the parent suite:

```
dx-all-suite/
├── dx-runtime/     (dx_app, dx_stream, dx_rt — NPU runtime + examples)
├── dx-compiler/    (dx_com — the ONNX→DXNN compiler SDK)
├── dx-modelzoo/    (model assets)
└── dx-ai-studio/   ← this project (the GUI layer)
```

The GUI is a **thin orchestration layer** over those SDKs. It locates them via env
roots (`DX_APP_ROOT`, `DX_COMPILER_ROOT`, `DX_RUNTIME_ROOT`, `DX_STREAM_ROOT`,
defaulting to the sibling suite paths). SDK coupling is deliberately **optional**:

- **`dx_com`** (dx-compiler) — DX Compiler invokes it in-process or via a venv
  subprocess (`compile_worker.py`). Without it, graph parsing / config wizard / setup
  still work; only the actual compile + HTML summary need it.
- **`dx_engine` / dx-runtime** — DX App runs inference through the sibling
  `dx-runtime/dx_app` example binaries; DX Monitor reads NPU stats via `dx_engine`;
  DX Benchmark's CLI needs the full NPU stack. All degrade to mock data when absent,
  so the GUI is fully browsable on a machine with no NPU.

## Further reading

- [`development.md`](development.md) — environment, running modules, i18n workflow.
- [`testing.md`](testing.md) — test layers and gates.
- Per-module `README.md` in each `<module>/` directory.
