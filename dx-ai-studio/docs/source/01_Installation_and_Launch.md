# Installation & Launch

!!! warning "Beta release (v0.1.0)"
    DX-AI-Studio is a **beta** release. Features, APIs, and the UI may change before the
    general-availability release.

## Prerequisites

- **Python 3.8+**. `./launcher.sh` installs the package automatically on first run —
  no manual install step, no third-party dependencies.
- For **real** compilation and inference: the **DEEPX SDK** (from `dx-runtime` /
  `dx-compiler`) and a DEEPX **NPU**. Without them the studio still launches in
  **demo / mock mode** for exploring the UI.
- **DX Stream** additionally needs the system **GStreamer + PyGObject** (`python3-gi`,
  `gstreamer1.0-*`) — standard on desktop Linux — to run pipelines.

!!! note "How the studio finds these"
    `./launcher.sh` creates its virtualenv with **`--system-site-packages`**, so it inherits
    the platform-provided `dx_engine` (DEEPX runtime) and `gi` (GStreamer bindings). The
    studio's *own* code stays stdlib-only (no pip third-party); these are platform runtimes,
    like the NPU driver. If `dx_engine` is missing, **DX Monitor** shows mock data and live
    inference is unavailable; if `gi` is missing, **DX Stream** can build but not run pipelines.

!!! note "Check your NPU"
    Once the DEEPX runtime is installed, `dxrt-cli --status` lists each NPU device with its
    driver and firmware versions. **DX Monitor** shows the same info live in the browser.

## Launch

From the `dx-ai-studio` directory:

```bash
./launcher.sh
```

It starts the launcher hub, boots every module server, and opens your browser at the
hub URL. On first load a brief splash appears while servers start — give it a moment if
a tool isn't ready yet.

### Common options

| Option | Effect |
|--------|--------|
| `--port <PORT>` / `-p <PORT>` | Hub port (default **8890**; auto-bumps if busy). |
| `--no-browser` | Start the servers but do not open a browser. |

Run `./launcher.sh --help` for the full flag list. The hub proxies all modules, so you
only ever open the hub port.

## Typical Workflows

Once the hub is running, here are common workflows:

### 🎯 Workflow 1: Model to Inference

The complete path from model to running inference:

1. **[Model Zoo](03_DX_Model_Zoo.md)** — Browse and download AI models (ONNX + .dxnn variants)
2. **[Compiler](04_DX_Compiler.md)** — Convert ONNX to optimized `.dxnn` for DEEPX NPU
3. **[App](05_DX_App.md)** or **[Stream](06_DX_Stream.md)** — Run inference on images, video, or camera
4. **[Monitor](07_DX_Monitor.md)** — Watch real-time NPU performance and utilization

### 🎯 Workflow 2: Hardware Selection

Find the right DEEPX hardware for your workload:

1. **[Benchmark](08_DX_Benchmark.md)** — Review benchmark results across NPU platforms
2. **[EdgeGuide](09_DX_EdgeGuide.md)** — Get hardware recommendations based on your requirements

### 🎯 Workflow 3: Quick Development

Build NPU applications from natural language:

1. **[Agent Dev](10_DX_Agent_Dev.md)** — Describe what you want; the agent generates and runs it

See **[The Hub](02_The_Hub.md)** for details on all eight tools and navigation.

## How to Use This Manual

**📖 Getting Started:**

1. **[Installation & Launch](01_Installation_and_Launch.md)** (this page) — Get the studio running
2. **[The Hub](02_The_Hub.md)** — Understand the interface and navigation

**🔧 Workflow:**

- **[Model Zoo](03_DX_Model_Zoo.md)** — Browse and download AI models
- **[Compiler](04_DX_Compiler.md)** — Convert ONNX to `.dxnn` for DEEPX NPU
- **[App](05_DX_App.md)** — Run image/video inference
- **[Stream](06_DX_Stream.md)** — Build real-time GStreamer pipelines

**📊 Monitoring:**

- **[Monitor](07_DX_Monitor.md)** — Watch NPU performance in real time
- **[Benchmark](08_DX_Benchmark.md)** — Review benchmark results across NPU platforms
- **[EdgeGuide](09_DX_EdgeGuide.md)** — Get hardware recommendations

**🚀 Development:**

- **[Agent Dev](10_DX_Agent_Dev.md)** — Generate NPU apps from natural language

**📚 Reference:**

- **[SDK Library & About](11_SDK_Library_and_About.md)** — In-app documentation and company info

**📋 Appendix:**

- **[Change Log](Appendix_Change_Log.md)** — Version history and updates
- **[Third Party License](12_Appendix_Third_Party_License.md)** — Open source licenses

## Stopping

`Ctrl+C` in the terminal running `./launcher.sh`. Re-running on a busy port auto-bumps
to the next free port unless you pass `--no-kill`.

## Remote access & security

By default the hub binds **all network interfaces**, so a studio running on a headless
NPU board is reachable from another machine's browser at `http://<board-ip>:8890`.
Convenient — but it also means **anyone on the same network can open it** (no login), and
they share the board's files (uploads, runs, downloads). Choose the access model that fits:

### Private access via SSH tunnel (recommended)

Keeps the studio invisible to the network — only someone who can SSH into the board can
reach it. No password feature needed; it reuses the SSH login you already have.

1. On the board, bind to localhost only:
   ```bash
   DX_BIND_LOCAL=1 ./launcher.sh
   ```
   The studio now listens on `127.0.0.1:8890` and is **not** visible on the network.
2. From your laptop (Windows PowerShell, macOS/Linux terminal), forward the port over SSH:
   ```bash
   ssh -L 8890:localhost:8890 <user>@<board-ip>
   ```
   (On Windows, PuTTY/MobaXterm can save this as a stored port-forward.)
3. Open `http://localhost:8890` in your laptop browser — traffic rides the encrypted SSH
   tunnel to the board. Keep the SSH session open while you use it.

!!! note "Worked example — laptop → board at `192.168.0.42`"
    Find the board's IP on the board with `hostname -I` (or `ip addr`) — say it's
    `192.168.0.42`, login `deepx`.

    - **On the board:** `DX_BIND_LOCAL=1 ./launcher.sh`
    - **On your laptop** (Windows PowerShell / macOS / Linux terminal):
      ```bash
      ssh -L 8890:localhost:8890 deepx@192.168.0.42
      ```
    - **In your laptop browser:** open `http://localhost:8890`

    Nobody else on the network can reach it — even though the studio runs on the board,
    it only answers on the board's `localhost`, and the tunnel is yours alone.

### Open LAN access

Just run `./launcher.sh` (default) and open `http://<board-ip>:8890` from any machine on the
network — e.g. a board at `192.168.0.42` → `http://192.168.0.42:8890` in your laptop
browser (find the IP with `hostname -I` on the board). Use this only on a **trusted** network — there is no browser login, so treat it as
"anyone who can reach the port can use the studio". For programmatic/API clients you can
require a token:

```bash
DX_API_TOKEN=<your-secret> ./launcher.sh   # module API calls must send this token
```

(The token gates the module API; it does not add a browser login screen — for private
browser access use the SSH tunnel above.)

### Multiple people

- **Different machines** — fully independent studios. On an open LAN, remember each is
  reachable by anyone via its board IP (use SSH tunnels to keep them private).
- **Same board, same Linux account** — relaunching `./launcher.sh` **stops the previous
  instance** (it clears stale studio processes owned by your user on start). Two people
  sharing one login will interrupt each other; pass `--no-kill` to leave a running instance
  alone, but they'll then contend for the port and shared files.
- **Same board, separate Linux accounts** — instances don't kill each other (the cleanup is
  per-user) and the port auto-bumps (8890 → 8891 …). Give each user their **own copy** of
  `dx-ai-studio` so they don't share `outputs/`, sessions, and downloads.

### Environment variables

| Variable | Effect |
|----------|--------|
| `DX_BIND_LOCAL=1` | Bind `127.0.0.1` only — no network exposure (use with an SSH tunnel). |
| `DX_BIND_HOST=<host>` | Bind an explicit interface/address. |
| `DX_API_TOKEN=<secret>` | Require this token on module API requests (`Authorization` / `X-DX-Api-Token`). |

## Troubleshooting

- **Everything shows sample / mock data** — the NPU or SDK isn't detected. Confirm the
  driver is loaded with `lsmod | grep dx` (expect `dxrt_driver` and `dx_dma`) and the
  device with `dxrt-cli --status`; **DX Monitor**'s version panel shows what the studio sees.
- **A tool stays on the splash / "not ready"** — module servers may still be starting;
  wait a moment and reload. If it persists, check the terminal running `./launcher.sh` for errors.
- **"Port already in use"** — 8890 auto-bumps to the next free port; pin one with `-p`, or
  pass `--no-kill` to leave an existing instance alone.
- **UI works but compile / inference fails** — the DEEPX SDK is missing. Use the in-app
  **Setup** panel in DX App and DX Compiler to check and install the required runtime.
