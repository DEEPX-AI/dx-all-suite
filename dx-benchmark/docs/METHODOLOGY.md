# DX-Benchmark Methodology

How DX-Benchmark measures, normalizes for temperature and recovers from hangs.
Back to the [README](../README.md).

## Measurement Protocol

| Parameter | Value |
|-----------|-------|
| Protocol version | v2 |
| Throughput duration (`-t`) | 30s |
| Latency loops (`-l`) | 300 loops (`dxrun -s` mode ignores `-t`, uses `-l` only) |
| Warmup | 1 run (latency, E2E, multi-stream) |
| Latency runs | 1 |
| Throughput buffer-count | `dxrun --max-throughput` auto-stop sweep: 10s probe × 3 repeats, 1% tolerance; `--cool-down-temp` = the cooldown target before every repeat |
| Throughput runs | 3 — each after its own cooldown, preceded by a 2s throw-away `dxrun` (wake-up run) |
| E2E runs | 3 (uniform across all tasks) |
| ORT modes | ON + OFF |
| Thermal mode | steady |
| Hot-start block | settled NPU idle above 60°C is rejected; at or above the 55°C cap it is rejected unless `--allow-hot-start` (target raised, run flagged) |
| Cooldown points | ① before model-level (fatal) · before each throughput run · ④ before E2E/multi |
| Cooldown target | `min(settled idle + Δ10°C, 55°C)` — the settled idle temperature is recorded in `environment.json` (`thermal`) |
| Cooldown timeout | 1000s — model-level: RuntimeError; pre-E2E: warn + proceed |
| NPU warmup / drain | 1.0s / 0.5s |
| NPU clock monitoring | dxtop Core Clock MHz (during measurement) + dxrt-cli pre/post snapshots |
| CPU clock monitoring | sysfs scaling_cur_freq pre/post snapshots |
| Multi-stream per-channel threshold | 30 fps (every channel must sustain ≥ 30 fps) |
| Multi-stream 1ch | Reuses single-stream result |
| Multi-stream search | jump to a single-stream-FPS ÷ 30 estimate, then boundary-walk up/down (not 1-by-1) |
| Multi-stream max streams | 128 (safety cap) |
| Process timeout | `dxrun`: 600s/run; E2E/multi: 90s no-progress stall + 1800s hard cap |
| Graceful shutdown | SIGTERM → 10s wait → SIGKILL → 5s reap |
| Retry (model / E2E / multi) | warmup: 1 retry on timeout; measured runs: up to 2 backfill attempts |
| NPU recovery | Automatic dxrt.service restart after SIGKILL |
| Circuit breaker | abort the run if the device probes dead, or after 2 consecutive fully-failed models |

> **Reading NPU %** — Throughput/E2E/Multi report NPU **core utilization** sampled by
> dxtop over the run (sustained load). Latency reports NPU **occupancy**
> (`npu_task_ms / total_ms`, from the profiler): a sub-second single-core run is too
> short for dxtop's ~1 Hz sampler, so its clock/throttle are omitted and shown only for
> the sustained metrics. A red clock elsewhere means it dropped below the nominal rated
> clock under load (throttling) — idle DVFS downclock is not throttling.

## Per-Model Execution Order (Thermal Normalization)

Each model × ORT combination follows these steps sequentially. The protocol cools the NPU
before the model-level phase, before **each** measured throughput run, and before the E2E
phase, so each of those measurements starts from a controlled thermal state (E2E and
multi-stream then run back to back by design — see below):

```
── [1/N] yolo26-n_640x640.dxnn  ORT=ON  (object_detection) ──

  ① Cooldown → wait until ≤ min(settled idle + Δ10°C, 55°C)   (when the model family is included)
  ② Latency    → single-core sync mode (-l 300 loops), profiler-based NPU/CPU ms   (cold state)
  ③ Throughput → dxrun auto-stop buffer-count sweep, then 3 measured runs, each after a
                  cooldown and a 2s wake-up run (multi-core async mode, FPS)
  ④ Cooldown → shed the throughput burst's residual heat            (when the e2e/multi family is included)
  ⑤ E2E Single-Stream → full GStreamer pipeline FPS (3 runs)
  ⑥ Multi-Stream → jump to an FPS-based estimate (single-stream FPS ÷ 30), then boundary-search
                    up/down for the max channels (each ≥ 30 fps) — not measured 1-by-1

→ next model × ORT combination (repeat from ①)
```

- ① Cooldown gives each model a comparable thermal baseline — the run is rejected if it
  starts above 60 °C, then waits until the NPU is at ≤ min(idle + Δ10 °C, 55 °C), so a
  previous model's residual heat cannot bias the next one.
- ② Latency runs from cold — the profiler cleanly separates NPU/CPU time with minimal heating.
- ③ Throughput finds the buffer-count with dxrun's sweep (it waits for `--cool-down-temp`
  before every repeat), then measures 3 × 30s runs. Each run is preceded by a cooldown to
  the same target and by a 2s throw-away `dxrun`: the first process after minutes of
  idle measures a few percent slower however many warm-up runs it does itself, and a
  throw-away run removes that without re-heating the NPU. Throughput is therefore a
  cooled-state value; consecutive runs cannot inherit each other's heat.
- ④ The **pre-E2E cooldown** sheds the throughput burst's residual heat so
  E2E and multi-stream measure their *own* sustained steady state, rather than a state
  inflated by the preceding throughput burst.
- ⑤/⑥ E2E then multi-stream are continuous sustained-load measurements: the E2E runs
  follow one another after a single warm-up, and multi-stream follows E2E without a
  cooldown. On a board that throttles, the mean therefore includes the thermal ramp, and
  a wide run-to-run spread is a sign of throttling; this is intended, not a bias to remove.
- **Cooldown failure differs by point:** the model-level cooldown ① is fatal (RuntimeError
  on the 1000s timeout); the pre-E2E cooldown ④ is non-fatal — it warns and proceeds
  (E2E measured hot). If both latency and throughput time out, E2E/Multi-Stream are skipped
  for that model.

## Timeout Recovery and Retry Strategy

GStreamer pipelines or `dxrun` processes can occasionally hang (deadlock, NPU hang).
The tool has **three per-hang recovery layers**, plus a **run-level circuit breaker** that
aborts early when recovery cannot help.

**Layer 1 — Graceful shutdown (SIGTERM → SIGKILL).** On a `dxrun` 600s timeout, an
E2E/multi 90s no-progress stall, or the 1800s hard cap: SIGTERM to the process group →
10s wait → SIGKILL if needed (→ 5s reap) → NPU device recovery (Layer 3).

> Force-killing `gst-launch-1.0` destroys dxrtd's IPC message queue (Error 43: Identifier
> removed), so all subsequent NPU inference fails — device recovery is mandatory.

**Layer 2 — Python-level retry.** Two parameters — `model_warmup_retries` (default 1) and
`model_run_retries` (default 2):

| Phase | Retries | Notes |
|-------|:-------:|-------|
| Warmup (latency / E2E / multi) | 1 | one retry on timeout before giving up the cell (throughput has no separate warmup: its wake-up run is best effort) |
| Measured runs (model / E2E / multi) | up to 2 | backfill failed/timed-out runs toward the target (`e2e_runs` = 3); the successful runs are averaged |
| Multi-stream sweep (per stream count) | 1 | a stream count whose whole measurement times out is retried once — on top of the per-run backfill above |

When a model's model-level phase fails on **both** latency and throughput, its E2E and
multi-stream phases are skipped for that model × ORT combination.

**Layer 3 — NPU device recovery** (triggered when Layer 1 needed a SIGKILL): kill orphaned
`gst-launch-1.0` / `run_model` (the `dxrun` processes) → `sudo -n systemctl restart dxrt.service` (3s settle).
Mandatory because the SIGKILL tears down dxrtd's IPC message queue (the Error-43 case above),
leaving the NPU unusable until the daemon restarts.

> Passwordless sudo is required for NPU recovery and incident diagnostics. Run
> `sudo ./setup_host.sh` — it writes `/etc/sudoers.d/benchmark-dxrt` granting the current
> user NOPASSWD for exactly these commands (and nothing else):
> `systemctl restart dxrt.service`, `dmesg`, `journalctl -u dxrt.service`, and `lspci`
> (the last three are for incident-diagnostic collection on timeouts).

**Circuit breaker — run-level abort** (`enable_circuit_breaker`, default on). When a model's
model-level benchmarks both fail, the tool runs Layer-3 recovery once, then a deterministic
`dxrt-cli -s` liveness probe (15s) and decides:

- device **dead** (cannot be enumerated) → **abort the run** — the NPU needs a cold
  power-cycle; resume afterwards with `--resume <dir> --retry-failed`.
- device **alive** but **2 consecutive models fully failed** → abort as an anti-runaway
  backstop (`circuit_breaker_backstop_models`).
- otherwise → continue (only the failed model is skipped).

This stops the run from churning for hours when the NPU has actually died mid-run.

**Incident diagnostics** (cross-cutting, not a recovery layer; capped at 40 bundles/run). On a
timeout or a detected dxrt error, a snapshot is saved to `incidents/`: `dxrt-cli -s` status,
`systemctl status dxrt.service`, recent `journalctl`/`dmesg`, a process-tree dump, and an NPU
temperature/clock snapshot.
