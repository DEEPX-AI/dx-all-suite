# Architecture

DX AI Studio is a browser front-end that unifies the DEEPX NPU SDK tools into one
experience. It is a **launcher hub** plus **nine independent module servers**, all
built on the Python standard-library `http.server` (no FastAPI/Flask/Node). It has
**no third-party runtime dependencies** — pure Python standard library (3.8+),
including a tiny built-in template renderer for DX Compiler (no Jinja2) and a stdlib
`html.parser` DOM for the dx_app Model Zoo tab (no BeautifulSoup, no requests). The one
optional AWS extra is `boto3` (`pip install -e '.[aws]'`), needed for DX Cloud's
actual AWS API operations, not for opening its page or guide. SDKs, native runtimes
and feature-specific tools remain separate requirements.

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
                                                dx_edge      :8100  /cloud/

shared/dx_server.py  ← base HTTP handler + server wrapper for ALL servers
shared/chat/         ← ChatEngine (per-module AI assistant)
shared/hardware.py   ← telemetry cache adapter + host CPU / memory / disk
shared/static/       ← i18n, toolbar, tutorial engine, design tokens
```

## The proxy model

The launcher is both a **process supervisor** and a **reverse proxy**
(`launcher/launcher.py`):

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
   widget into HTML responses (all modules except `dx_monitor`, `dx_agent_dev` and `dx_edge`).
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
| DX Cloud | `dx_edge/` | 8100 | `/cloud/` | `DX_EDGE_PORT` |

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
parsing, SSE helpers, the remote-access gate (Host allowlist, same-origin checks for
state-changing requests, no CORS; local requests pass, remote ones need `DX_API_TOKEN`
or a paired-browser session from `shared/remote_access.py`), and a corporate-TLS CA
bridge. Module servers bind 127.0.0.1 and trust the launcher's proxied requests by the
per-run `DX_PROXY_SECRET` it puts in their env. `DXServer` wraps CLI parsing, the 127.0.0.1 default bind,
port-collision retry, and ephemeral-port reporting via `DX_PORT_FILE`.

- **`shared/chat/`** — `ChatEngine` powers the per-module "DX Chat" assistant.
  Providers: OpenAI, Anthropic, Google (Gemini), GitHub Models, a Custom OpenAI-compatible
  endpoint, a local (Ollama-compatible) server, and an `agent-cli` backend. Rule-based `FallbackEngine` answers when no key is set.
  Module knowledge lives in `shared/chat/knowledge/*.md` and is auto-synced from the
  suite docs — no manual regen. The launcher pre-syncs it once, unconditionally, at
  boot (single writer, before any module starts); `ChatEngine.stream()` also does a
  lazy, env-gated (`DX_CHAT_KNOWLEDGE_SYNC=1`) fallback sync for a module server run
  standalone without the launcher. Both paths call `knowledge_sync.sync_if_stale()`,
  which writes atomically (temp file + `os.replace()`).
- **`shared/hardware.py`** — `get_hw()` / `get_sysinfo()` merge cached NPU telemetry
  with host CPU/memory/disk metrics from `/proc`. DX Monitor's
  `core/telemetry_supervisor.py` owns an isolated `telemetry_worker.py` subprocess
  running with the runtime-specific Python/environment. Native `dx_engine` access
  stays in that worker, not in the Monitor HTTP process. The supervisor validates
  worker records, caches snapshots/events and bounds restart attempts.
  Missing hardware/SDK or a failed worker produces `unavailable`; stale data is
  marked `stale`, not current measurement. Demo telemetry requires
  `DX_MONITOR_EXPLICIT_MOCK=1`. `DX_MONITOR_SKIP_HARDWARE_INIT=1` bypasses initialization
  and leaves NPU telemetry unavailable; it is not mock mode. An SSE connection only
  establishes transport, not telemetry health.
- **`shared/static/`** — the 6-language i18n runtime (`i18n.js`, `window.DXI18n`),
  unified toolbar, tutorial engine, and design-token CSS (`dx-tokens/base/utilities`).

## DX Agent Dev

`dx_agent_dev` drives installed, authenticated coding-agent CLIs headlessly and
streams their output into the browser console. Five CLI adapters live under
`dx_agent_dev/core/adapters/`: `claude.py`, `copilot.py`, `codex.py`, `cursor.py`,
`opencode.py` (plus a `mock.py` used under `DX_AGENT_ADAPTER=mock` for closed-net/CI
runs). Copilot (the account's models, over ACP), Cursor and OpenCode enumerate models
dynamically (`cursor-agent --list-models`, `opencode models`); all fall back to a static table in
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
  `dx-runtime/dx_app` runners; DX Monitor's isolated worker reads NPU stats;
  DX Benchmark's separate CLI needs the NPU stack (Studio is a dataset viewer).
  Missing prerequisites do **not** imply automatic mock inference. Setup/status and
  reference views can be used without running an NPU job; execution paths report
  their missing requirements.
- **Managed runtime** — `shared/runtime_*` tracks installation/validation state and
  resolves App/Stream child-process environments. The inference launch gate accepts
  an active runtime profile, or a degraded path when that module's own contracts
  validate live. Otherwise it blocks launch with remediation rather than fabricating
  a result. For example, use Stream **Setup → DX-Runtime Dependencies**, resolve the
  reported failed checks, validate and retry the operation.
- **Graph Composer inside DX App** — `core/graph_cli.py` discovers
  `multi_model_graph_sync` / `multi_model_graph_async` and invokes them as bounded
  subprocesses; `graph_validate.py` delegates graph rules to the runner's `--check`
  and maps diagnostics to nodes/edges. `graph_run.py` owns run-once jobs/results;
  `graph_live.py` owns Live display/stream lifecycles. `graph_projects.py` stores
  projects under `outputs/dx_app/graph/projects` with the newest 50 saved versions;
  runs and C++ project exports have separate `graph/runs` and `graph/exports`
  directories. JSON project export is distinct from a C++ project ZIP generated
  through the sibling app's exporter. None of this provides a missing-runner mock.
  For example, prepare models, validate a graph, then Run once and inspect its
  report; a valid editor layout alone does not establish runnable artifacts.
- **NPU arbitration inside DX App** — `core/npu_jobs.py` reserves the NPU for graph
  run-once, graph Live, Run-page Live and gallery builds. Run-page Live slots may
  coexist with one another; they cannot overlap a graph job or gallery build.
  Reservations track attached runner processes and release on exit, with a timeout
  for abandoned preparation. This is a Studio App registry, not a system-wide lock
  on unrelated external processes. Stop/wait for the reported holder before
  retrying a conflicting job.
- **DX Cloud** — the internal `dx_edge` package serves `/cloud/`, independently of
  DX EdgeGuide and the suite's `dx-edge` product. boto3 uses the Studio host's
  credential chain/profile for subscription probes, stacks, compile jobs/logs/results
  and Greengrass queries. A generated registration script runs manually on the
  device; Studio neither SSH-executes it nor automatically deploys compiled models.
  See the [Cloud manual](source/13_DX_Edge_AWS.md) for storage, cost and cleanup limits.

## Further reading

- [`development.md`](development.md) — environment, running modules, i18n workflow.
- [`testing.md`](testing.md) — test layers and gates.
- Per-module `README.md` in each `<module>/` directory.
