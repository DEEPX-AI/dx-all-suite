# Installation & Launch

!!! warning "Beta release (v0.1.0)"
    DX-AI-Studio is a **beta** release. Features, APIs, and the UI may change before the
    general-availability release.

## Prerequisites

- **Python 3.8+**. `./launcher.sh` installs the package automatically on first run —
  no manual install step, no third-party dependencies.
- For **real** compilation and inference: the **DEEPX SDK** (from `dx-runtime` /
  `dx-compiler`) and a DEEPX **NPU**. Without them the studio still launches and every
  tool stays browsable; tools say when the NPU or SDK is missing.
- **DX Stream** additionally needs the system **GStreamer + PyGObject** (`python3-gi`,
  `gstreamer1.0-*`) — standard on desktop Linux — to run pipelines.
- **Live DX App runs** (camera, RTSP, Continuous, and Run Demo video) draw the example's
  window on a virtual display and stream it to the browser. They need the OS packages
  **`xvfb`** and **`python3-pil`** (`sudo apt install xvfb python3-pil`). Image and batch
  video runs do not. If they are missing, the run stops with a message that names them.

!!! note "How the studio finds these"
    `./launcher.sh` creates its virtualenv with **`--system-site-packages`**, so it inherits
    the platform-provided `dx_engine` (DEEPX runtime) and `gi` (GStreamer bindings). The
    studio's *own* code stays stdlib-only (no pip third-party); these are platform runtimes,
    like the NPU driver. If `dx_engine` is missing, **DX Monitor** shows *NPU telemetry
    unavailable* and live inference is unavailable; if `gi` is missing, **DX Stream** can build but not run pipelines.

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
| `--port <PORT>` / `-p <PORT>` | Preferred hub port (default **8890**). If another service holds it, the next free port is used; the last port is remembered in `.launcher-port`. Open the URL the launcher prints. |
| `--no-browser` | Start the servers but do not open a browser. |
| `--no-kill` | Keep a studio that is already running (by default a new launch replaces your previous one). |
| `--fast` | Skip the boot animation in the terminal. |
| `--debug[=PATH]` | Log user actions to `var/log/studio-debug.log` (or to `PATH`). |

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

See **[The Hub](02_The_Hub.md)** for details on all nine tools and navigation.

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
- **[DX Cloud](13_DX_Edge_AWS.md)** — Compile on AWS and deploy to edge devices

**📚 Reference:**

- **[SDK Library & About](11_SDK_Library_and_About.md)** — In-app documentation and company info

**📋 Appendix:**

- **[Change Log](Appendix_Change_Log.md)** — Version history and updates
- **[Third Party License](12_Appendix_Third_Party_License.md)** — Open source licenses

## Stopping

`Ctrl+C` in the terminal running `./launcher.sh`. Running `./launcher.sh` again replaces your
previous studio; pass `--no-kill` to leave it running (the new one then takes the next free
port).

## Remote access & security

By default the hub listens on **all network interfaces**, so a studio running on a headless
NPU board can be opened from another machine's browser. The launcher prints that address
under **other computers:** in its URL banner (for example `http://192.168.0.42:8890`), and the
**Connected browsers** button in the top bar shows it too.
Remote browsers must be **paired** first — nobody on the network can use the studio without
the code shown on the board. The module servers behind the hub (App, Stream, Compiler …)
only listen on the board's `127.0.0.1`; everything goes through the hub.

| Who | What they need |
|-----|----------------|
| You, on the board itself (or through an SSH / VS Code tunnel) | Nothing — works as before. |
| A browser on another machine | The **6-digit code** printed in the board's `./launcher.sh` terminal — once per browser. |
| A script / API client | `DX_API_TOKEN` (header `Authorization: Bearer <token>` or `X-DX-Api-Token`). |

### Pair a browser (open LAN access)

1. On the board, run `./launcher.sh`. Next to the URL banner it prints
   **`Remote access code: 123456`**.
2. On your laptop, open the address printed under **other computers:** (or shown in
   **Connected browsers** on the board). You see **Connect this browser** — type the code.
3. That browser is remembered for 30 days (`DX_SESSION_DAYS`). The code works once; a new one
   is printed after each use, and after 5 wrong tries the studio pauses for a minute and
   prints a new code.

**Connected browsers** (top bar) lists every paired browser — browser and OS, IP, last
active, paired date — with **Disconnect**. On the board you see and disconnect all of them;
a paired browser sees only itself and can **Disconnect this browser**. Scripts can use
`GET /api/auth/sessions`, `POST /api/auth/sessions/revoke` (board only) and
`POST /api/auth/logout`.

!!! tip "Watching DX Stream from another computer"
    Choose **Playback → Remote (MJPEG)** in DX Stream. **Local (WebRTC)** is for the board
    itself or the same LAN segment and does not cross an SSH tunnel.

!!! note "Worked example — laptop → board at `192.168.0.42`"
    - **On the board:** `./launcher.sh` → note `Remote access code: 482915`.
    - **In your laptop browser:** open `http://192.168.0.42:8890`, enter `482915`.

### Private access via SSH tunnel (no network exposure)

Keeps the studio invisible to the network — only someone who can SSH into the board can
reach it, and no code is needed (the tunnel arrives on the board's `localhost`).

1. On the board, bind to localhost only:
   ```bash
   DX_BIND_LOCAL=1 ./launcher.sh
   ```
2. From your laptop, forward the port over SSH:
   ```bash
   ssh -L 8890:localhost:8890 <user>@<board-ip>
   ```
   (On Windows, PuTTY/MobaXterm can save this as a stored port-forward.)
3. Open `http://localhost:8890` in your laptop browser.

### What the studio refuses

- Requests whose `Host` is a name other than `localhost`, this machine's hostname or an
  address listed in `DX_ALLOWED_HOSTS` (an IP address is always fine) — this blocks DNS
  rebinding.
- Cross-site requests: no `Access-Control-Allow-Origin: *`, and a state-changing request
  (POST/PUT/PATCH/DELETE) carrying another site's `Origin`/`Referer` is refused, even on the
  board itself.
- Compile paths outside the allowed folders — the suite folder, the studio's `var/`, your home
  folder, `/media` and `/mnt` (add more with `DX_COMPILER_ALLOWED_ROOTS`).
- For HTTPS or access from outside the LAN, put the hub behind an approved reverse proxy
  that terminates TLS; requests that come through a proxy (`X-Forwarded-For`) are treated as
  remote and must be paired.

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
| `DX_BIND_HOST=<host>` | Bind the hub to an explicit interface/address. |
| `DX_API_TOKEN=<secret>` | Lets scripts call the studio from another machine (`Authorization: Bearer` / `X-DX-Api-Token`). Required to run a module server on its own beyond `127.0.0.1`. |
| `DX_PAIRING=off` | Disable browser pairing — remote access only with `DX_API_TOKEN`. |
| `DX_SESSION_DAYS=<n>` | How long a paired browser stays connected (default 30). |
| `DX_ALLOWED_HOSTS=<a,b>` | Extra host names the studio answers to (e.g. a DNS alias). |
| `DX_COMPILER_ALLOWED_ROOTS=<dir:dir>` | Extra folders the compiler may read from and write to. |

## Troubleshooting

- **DX Monitor says *NPU telemetry unavailable* / tools say the SDK is missing** — the NPU or SDK isn't detected. Confirm the
  driver is loaded with `lsmod | grep dx` (expect `dxrt_driver` and `dx_dma`) and the
  device with `dxrt-cli --status`; **DX Monitor**'s version panel shows what the studio sees.
- **A tool stays on the splash / "not ready"** — module servers may still be starting;
  wait a moment and reload. If it persists, check the terminal running `./launcher.sh` for errors.
- **"Port already in use"** — 8890 auto-bumps to the next free port; pin one with `-p`, or
  pass `--no-kill` to leave an existing instance alone.
- **UI works but compile / inference fails** — the DEEPX SDK is missing. Use the in-app
  **Setup** panel in DX App, DX Stream or DX Compiler to check and install the required runtime.
