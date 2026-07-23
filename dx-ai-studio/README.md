# DX AI Studio

An all-in-one desktop web workspace for building on the **DEEPX NPU**. Eight
specialized tools — model catalog, compiler, inference, streaming, benchmarking,
hardware monitor, deployment planner, and an agent-driven builder — in one browser
experience, in six languages.

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
