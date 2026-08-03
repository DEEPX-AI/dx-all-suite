# DX AI Studio

An all-in-one desktop web workspace for building on the **DEEPX NPU**. Eight
specialized tools — model catalog, compiler, inference, streaming, benchmarking,
hardware monitor, deployment planner, and an agent-driven builder — in one browser
experience, in six languages.

![The DX AI Studio hub — eight module tiles orbiting the launcher home, each with a live status dot and port.](docs/source/resources/hub.png)

## The hub

The **hub** is the studio's home screen and the single place everything launches from.
Eight **module tiles** orbit the center in a constellation; each shows a **live status dot**
(green when its server is up) and the local **port** it's serving on. The center badge names
the suite — module count, the bundled **DXNN SDK** version, the studio **build**, and the
launcher port (`:8890`).

- **One boot, all tools.** The launcher starts every module server for you on a short boot
  screen; when it clears, click any tile to open that tool.
- **Everything stays in one place.** Tiles open the module **embedded** in the hub (not a new
  tab), and a shared **NPU monitor** float follows you across tools, so you never lose the
  telemetry or the home.
- **Tutorial Mode** (top-left toggle) auto-starts an interactive walkthrough the first time you
  open each tool — handy for a first tour, off by default.
- **Built-in references.** The **SDK Library** (DEEPX docs & brochures, fully in-app) and
  **About DEEPX** open right from the hub, alongside the Physical-AI-ecosystem and product
  (DX-M1 / DX-M2) cards.
- **Always reachable.** The top bar carries the **language switch** (6 locales), the store
  (**Buy**), and per-module status dots; the bottom bar has quick links (Homepage, Tech Docs,
  Model Zoo, S/W & Document downloads, GitHub); and the **💬 assistant** (bottom-right) answers
  SDK/module questions from any screen.

## Getting started

**Prerequisites:** Linux (Debian 12/13, Ubuntu 20.04–26.04) with **Python 3.8+** —
and nothing else. DX AI Studio has **zero third-party dependencies** (pure Python
standard library, ModelZoo tab included), and `./launcher.sh` self-installs the
package (editable) on first run, so there's no manual `pip install` step.

**Layout:** DX AI Studio is meant to sit inside a `dx-all-suite` tree, alongside
sibling `dx-runtime` / `dx-compiler`. Running actual NPU inference or compiling models
needs the DEEPX SDK (from those siblings), an NPU + driver, and models fetched into
`dx-runtime/dx_app` — but the whole studio is fully browsable in demo/mock mode without
any hardware, SDK, or models.

```bash
./launcher.sh
```

Then open the address it prints (the studio home). Wait for the boot screen to finish —
it starts all the tools for you — then click any tile on the hub to begin.

`./launcher.sh` uses `.venv/bin/python` if a virtual environment is present, otherwise
your system `python3`. See [`docs/development.md`](docs/development.md) for options
(`--port`, `--no-browser`, …) and environment variables.

## Managed runtime profiles

DX AI Studio treats the DEEPX runtime as an external, versioned host dependency. It
does not modify `dx-runtime` sources. The Studio-owned compatibility matrix in
`config/runtime_profiles.json` declares the supported runtime/driver package pairs,
immutable GitHub revision URLs, and SHA-256 digests. Package discovery uses installed
Debian package metadata, not the version of a source checkout.

- **Supported migration:** Studio can reconcile the declared `2.3.0` rollback profile
  to the target `2.4.1` profile on `x86_64` and `aarch64` hosts.
- **Trust boundary:** packages are staged under Studio's `var/runtime/artifacts/`
  cache only after their declared SHA-256 digest matches. A digest mismatch never
  reaches a privileged package command.
- **Explicit authorization:** installing packages requires an explicit authorized
  Runtime Setup action. Studio invokes a non-interactive privileged `dpkg` command
  only after that authorization; browsing diagnostics and Setup remains available
  without it.
- **Launch gate:** App and Stream inference launches require a journaled `ACTIVE`
  profile that passed full validation. A failure returns a stable contract check ID
  and remediation rather than starting a child process with inherited shell paths.
- **Environment isolation:** inference children receive the Studio-selected Python,
  virtual environment, native library paths, GStreamer plugin directory, and
  postprocess path. `PYTHONPATH`, `VIRTUAL_ENV`, `LD_LIBRARY_PATH`, and
  `GST_PLUGIN_PATH` from the parent shell are not inherited.
- **Recovery:** a failed candidate validation triggers a verified reinstall and
  validation of the prior declared runtime profile. Studio outputs and its artifact
  cache are not runtime-install targets and are preserved during rollback.

Installing or changing a DKMS driver can require a reboot before NPU device nodes are
available. After a reboot, return to Runtime Setup to validate and activate the
installed profile before starting inference.

## What you can do

| Tool | What it's for |
|------|----------------|
| **DX App** | Run NPU inference on images, video, camera or RTSP; live multi-stream, benchmark & compare. → [guide](dx_app/README.md) |
| **DX Stream** | Real-time GStreamer vision-AI pipelines with live WebRTC playback. → [guide](dx_stream/README.md) |
| **DX Model Zoo** | Browse 360+ DEEPX models by task; open details and use them. → [guide](dx_modelzoo/README.md) |
| **DX Compiler** | Compile ONNX → `.dxnn`: config wizard, quantization tuning + diagnosis, re-quantization. → [guide](dx_compiler/README.md) |
| **DX EdgeGuide** | Recommend the best NPU board + host for your workload from real benchmarks. → [guide](dx_planner/README.md) |
| **DX Benchmark** | Browse and compare NPU throughput / latency / multi-stream results. → [guide](dx_benchmark/README.md) |
| **DX Monitor** | Live NPU + system telemetry (temperature, clock, utilization, versions). → [guide](dx_monitor/README.md) |
| **DX Agent Dev** | Describe an NPU app in natural language and have a coding agent build it. → [guide](dx_agent_dev/README.md) |

From the **hub** you can also open the **SDK Library** (DEEPX docs & brochures in-app),
**About DEEPX**, switch **language** (6 locales), and jump to the DEEPX store.

Every tool degrades gracefully to sample/mock data when no NPU or SDK is present, so the
whole studio is browsable without hardware.

## For developers

Maintainer documentation lives in [`docs/`](docs/):

- [`docs/architecture.md`](docs/architecture.md) — launcher hub + module servers + `shared/`, the proxy model, port map.
- [`docs/development.md`](docs/development.md) — Python 3.8+ venv, running modules, env vars, i18n workflow.
- [`docs/testing.md`](docs/testing.md) — test layers and how to run the gates.
