# YOLO26 × DEEPX NPU — Benchmark Analysis

> **Scope.** This report is derived from the measurement data committed under
> [`dx-benchmark/results/`](../results/): **6 hardware environments × 2 dx-all-suite
> releases (v2.3.3, v2.4.0) = 12 benchmark runs.** Every run used the same tool and the
> same protocol, so all cross-environment and cross-version comparisons are directly
> comparable. The v2.4.0 runs are the current release and the subject of this report; the
> v2.3.3 runs establish the release-over-release trend presented in
> [§9](#9-performance-trend-across-dx-all-suite-releases).
>
> **Traceability.** Every table states its exact source coordinates — environment,
> dx-all-suite version, task, model size, and ONNX-Runtime mode — so any value can be
> re-checked against the per-run `*_results.json` files or the interactive dashboard
> ([`results/dashboard/index.html`](../results/dashboard/index.html)).
>
> **Caveats.** Several cells reflect real platform behaviour that must be interpreted
> correctly: thermal throttling on the boards that reached their thermal limit, and
> metrics that are host-bound rather than NPU-bound. These are stated explicitly in
> [§2](#2-how-to-read-these-numbers) rather than smoothed over.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [How to Read These Numbers](#2-how-to-read-these-numbers)
3. [What Was Measured — Terms and Method](#3-what-was-measured--terms-and-method)
4. [Test Environments](#4-test-environments)
5. [NPU Compute Performance (Model-Level Throughput)](#5-npu-compute-performance-model-level-throughput)
6. [Inference Latency](#6-inference-latency)
7. [End-to-End Video Pipeline (Single Stream)](#7-end-to-end-video-pipeline-single-stream)
8. [Multi-Stream Channel Capacity](#8-multi-stream-channel-capacity)
9. [Performance Trend Across dx-all-suite Releases](#9-performance-trend-across-dx-all-suite-releases)
10. [Deployment Guidance by Environment](#10-deployment-guidance-by-environment)
11. [Appendix](#11-appendix)

---

## 1. Executive Summary

The table below reports the practical performance of the lightest model (**nano**) in
each environment on the current release (**dx-all-suite v2.4.0**), with **Full HD
(1920×1080) 30 fps** video as input.

Reading the table:

- The format is **`single-stream end-to-end FPS / maximum concurrent channels`**. The
  first value is the FPS obtained when **one** Full HD stream is processed through the
  complete pipeline (decode → preprocess → NPU → post-process); the second is the largest
  number of streams that can be processed concurrently while every stream still sustains at
  least 30 fps.
- Each cell takes whichever of the two ONNX-Runtime modes (ORT ON / OFF — defined in
  [§3](#3-what-was-measured--terms-and-method)) produced the higher single-stream
  end-to-end FPS.
- Classification reports single-stream end-to-end FPS only, because it is not part of the
  multi-stream measurement (see [§8](#8-multi-stream-channel-capacity)).

| Environment | Object Detection | Pose Estimation | Segmentation | Oriented Bounding Box | Classification |
|-------------|------------------|-----------------|--------------|-----------------------|----------------|
| **BIOSTAR_H1-Quattro** | 496.8 fps / 17 ch | 553.9 fps / 20 ch | 360.8 fps / 12 ch | 392.9 fps / 14 ch | 772.4 fps |
| **DX-AIPlayer-N97_M1** | 184.9 fps / 6 ch | 197.3 fps / 7 ch | 108.3 fps / 3 ch | 98.9 fps / 3 ch | 278.6 fps |
| **OrangePi5+_M1** | 148.1 fps / 4 ch | 243.4 fps / 8 ch | 101.5 fps / 3 ch | 100.0 fps / 3 ch | 1072.7 fps |
| **ROCK5B+_M1** | 141.5 fps / 4 ch | 237.9 fps / 8 ch | 86.8 fps / 2 ch | 101.8 fps / 3 ch | 957.9 fps |
| **RPi5B_M1** | 80.1 fps / 2 ch | 112.2 fps / 3 ch | 55.1 fps / 1 ch | 81.8 fps / 2 ch | 189.1 fps |
| **RPi5B_M1M** | 79.8 fps / 2 ch | 112.4 fps / 3 ch | 54.9 fps / 1 ch | 72.3 fps / 2 ch | 189.3 fps |

> **Source:** `results/<env>/<v2.4.0 run>/`, task = each column, size = `n` (nano),
> ORT = better of ON/OFF. End-to-end FPS from `pipeline_results.json`; channel count from
> `multi_stream_results.json` at the 30-fps-per-channel threshold.

### Principal findings

1. **The DEEPX M1 NPU delivers near-identical compute across markedly different host
   CPUs.** For the medium, large and x-large models — where the NPU rather than the host
   is the bottleneck — the four single-M1 machines (an Intel N97, a Rockchip OrangePi, a
   Rockchip ROCK5B, and a Raspberry Pi 5) agree to within a few percent
   ([§5](#5-npu-compute-performance-model-level-throughput)). The NPU is the performance
   anchor; the host and its interconnect mainly affect the lightest models and the video
   pipeline surrounding the NPU.

2. **Model-level throughput in the NPU-bound range (medium, large, x-large) improved by a
   median of +28.4% on the v2.4.0 stack relative to the v2.3.3 stack.** 14 of the 18 cells
   (6 environments × 3 sizes) fall in the +25–35% band and every cell improved. This follows
   from DX-COM, DX-RT, the drivers and the firmware changing together
   ([§9](#9-performance-trend-across-dx-all-suite-releases),
   [§2.1](#21-the-version-trend-reflects-the-entire-release-stack-not-one-component)).

3. **The H1-Quattro card scales model-level throughput by approximately 4× with its four
   M1 chips** — the `run_model` throughput of object detection at medium, large and x-large
   is 4.24–4.32× the mean of the four single-M1 hosts
   ([§5.2](#52-h1-quattro-scales-model-level-throughput-by-approximately-4-with-its-four-chips)).
   Single-stream end-to-end FPS does not scale by the same factor, because the host supply
   rate limits it first
   ([§7.1](#71-for-light-models-the-ceiling-is-the-host-not-the-npu)).

4. **For light models the end-to-end ceiling is the host, not the NPU.** At nano and small
   sizes, single-stream end-to-end FPS reaches only 45–82% of the model throughput
   measured under the same conditions, with NPU utilisation at 18–41%
   ([§7.1](#71-for-light-models-the-ceiling-is-the-host-not-the-npu)). The remaining NPU
   headroom is recovered through multi-stream operation.

5. **The optimal ORT mode depends on the environment × task combination, and for light
   models the difference reaches +48.8%.** There is no single default, so the choice should
   be confirmed before deployment
   ([§7.2](#72-the-optimal-ort-mode-is-determined-by-the-environment--task-combination)).

---

## 2. How to Read These Numbers

The five points below should be read before drawing conclusions from any individual figure.

### 2.1 The version trend reflects the entire release stack, not one component

Between the two releases it is not one component that changed but **the whole stack that
dx-all-suite ships**. The differences recorded in each run's metadata are:

| Component | v2.3.3 runs | v2.4.0 runs | In the model-level path | In the E2E / multi-stream path |
|-----------|:---------------:|:---------------:|:-----------------------:|:------------------------------:|
| DX-COM (model recompilation) | v2.3.0-rc.5 | v2.4.0-rc.4 | yes | yes |
| DX-RT runtime | v3.3.2 | v3.4.0 | yes | yes |
| RT driver | v2.4.1 | v2.5.1 | yes | yes |
| PCIe driver | v2.2.0 | v2.4.1 | yes | yes |
| NPU firmware | v2.5.6 | v2.7.3 | yes | yes |
| DX-Stream | 3.0.1 | 3.1.0 | no | yes |

> **Source:** `benchmarked_models[].dxcom_version`, the `npu` block (`rt_version` /
> `driver` / `pcie_driver` / `firmware`) and `software.dx_stream` of each run's
> `environment.json`. All six environments used the same version combination per release.

The following conditions were held constant: the DXNN binary format is `v8` in both sets
of runs, each environment's host OS and kernel are unchanged, and the measurement
protocol values (30-second throughput, 300-loop latency, repetition counts, the 30 fps
threshold, the cooldown targets) are identical. The only tool changes were internal
failure-handling safeguards; the procedure for a successful measurement did not change.

The accurate reading of [§9](#9-performance-trend-across-dx-all-suite-releases) is
therefore "**model-level throughput** in the medium-to-x-large range improved by a median of
+28.4% on the v2.4.0 stack relative to the v2.3.3 stack", and **the contribution of any
individual component cannot be separated out from this dataset.**

The same trend must also **not be applied to single-stream E2E FPS.** As the last column of
the table above shows, the components differ in which path they affect, and in cells where
the host is already the ceiling a model-level gain has nowhere to land
([§2.4](#24-several-metrics-are-host-bound-rather-than-npu-bound),
[§7.1](#71-for-light-models-the-ceiling-is-the-host-not-the-npu)). For those cells E2E FPS is
comparable between the two releases, and in some environment/task combinations it measures
slightly lower. That difference arises inside the E2E path (decode → preprocess → inference →
post-process) rather than in NPU performance, but **attributing it to an individual component
requires further measurement, so this document does not assert a cause.** It will be updated
in a later release's document.

### 2.2 M1 and M1M are different products and must not be combined

`RPi5B_M1` and `RPi5B_M1M` are the **same Raspberry Pi 5 host** fitted with **two
different DEEPX modules**. On NPU-bound models the M1M is materially slower — same host,
same release (v2.4.0), object detection, ORT OFF:

| Size | RPi5B_M1 throughput | RPi5B_M1M throughput | M1M ÷ M1 |
|------|--------------------:|---------------------:|:--------:|
| m | 118.7 fps | 73.5 fps | 0.62 |
| l | 86.8 fps | 60.0 fps | 0.69 |
| x | 49.2 fps | 26.3 fps | 0.53 |

> **Source:** [`results/RPi5B_M1/20260722_150437/`](../results/RPi5B_M1/20260722_150437/)
> and [`results/RPi5B_M1M/20260723_142408/`](../results/RPi5B_M1M/20260723_142408/),
> `model_results.json`, family = `throughput`, ORT OFF.

The M1M is a distinct SKU that is 31–47% slower on these models (m −38%, l −31%, x −47%). Both
modules report a nominal 1000 MHz core clock, so the difference is architectural rather
than a clock difference; the M1M is also fitted with LPDDR4 (4200 Mbps, 1.92 GiB) against
the M1's LPDDR5 (5600 Mbps, 3.92 GiB). On the largest models the gap widens further
because this M1M unit additionally throttles — see
[§2.3](#23-boards-that-reach-their-thermal-limit-throttle-in-the-sustained-phases).

The dashboard and this report therefore keep the two as separate environments. **M1 and
M1M figures must never be averaged together.**

### 2.3 Boards that reach their thermal limit throttle in the sustained phases

Protocol v1 runs each model × ORT cell in the following order, with **a cooldown at two
points**:

```
① cooldown → ② latency → ③ throughput → ④ cooldown (before E2E) → ⑤ E2E → ⑥ multi-stream
```

The E2E phase therefore does not inherit the residual heat of the preceding phases: the
cooldown at ④ returns each board to min(idle + 10 °C, 55 °C), and E2E entry temperatures in
the v2.4.0 runs were 39–55 °C. Throttling during the E2E phase is consequently caused by
**the sustained load of the E2E phase itself**, not by heat accumulated in the earlier phases.

**There is, however, no cooldown between ⑤ E2E and ⑥ multi-stream.** Multi-stream starts
from the thermal state left by E2E and then processes N concurrent streams, making it the
heaviest load in the measurement. This structure is reflected in the throttled-cell counts,
which are highest in the multi-stream phase in every environment.

On a board whose cooling cannot dissipate the sustained load, the NPU reaches its thermal
limit and reduces its clock from 1000 MHz into the 200–800 MHz range. This is real thermal
behaviour, not a software regression. Throttled cells carry `npu_throttled = true` in the
raw data and a clock badge in the dashboard.

> **Source:** `cooldown_temp_c` / `cooldown_wait_sec` in each v2.4.0 `pipeline_results.json`;
> `npu_clock_mhz_min` in the three result files.

| Environment (v2.4.0) | Model-level cells throttled | End-to-end cells throttled | Multi-stream cells throttled | Max NPU temp |
|----------------------|:---------------------------:|:--------------------------:|:----------------------------:|:------------:|
| BIOSTAR_H1-Quattro (active cooling) | 0 / 100 | 0 / 50 | 16 / 90 | 83 °C |
| DX-AIPlayer-N97_M1 (active cooling) | 0 / 100 | 5 / 50 | 33 / 78 | 84 °C |
| OrangePi5+_M1 | 0 / 100 | 4 / 50 | 29 / 78 | 82 °C |
| ROCK5B+_M1 | 24 / 100 | 22 / 50 | 51 / 76 | 86 °C |
| RPi5B_M1 | 0 / 100 | 2 / 50 | 8 / 78 | 80 °C |
| RPi5B_M1M | 28 / 100 | 26 / 50 | 43 / 66 | 87 °C |

> **Source:** per-cell `npu_throttled` / `npu_temp_max_c` in `model_results.json`,
> `pipeline_results.json` and `multi_stream_results.json` of each v2.4.0 run.

Two boards reach the thermal limit already in the *model-level* phase — the latency and
throughput runs that follow a single cooldown: **ROCK5B+_M1** (24 cells) and **RPi5B_M1M**
(28 cells). Every board throttles to some degree in the multi-stream phase, while the
actively cooled x86 boards and `RPi5B_M1` hold their clock throughout the model phase.

For the two thermally limited boards, their medium, large and x-large figures should be
read as a **sustained-load floor** rather than the module's ceiling — improved cooling
raises them.

Throttling does not only lower the mean; it also **widens the measurement spread.** Across
the 300 model-throughput cells of the v2.4.0 runs, the run-to-run spread (fps standard
deviation ÷ mean) has a median of 0.31% for the 249 cells that did not throttle (90th
percentile 1.15%), against a median of 5.46% and a maximum of 17.0% for the 51 cells that
did — among those model-level cells the clock settles anywhere in the 300–800 MHz range from
one run to the next.
**A cell with an unusually wide spread is therefore itself a thermal signal.**

> **Source:** `fps_std` / `fps` / `npu_throttled` / `npu_clock_mhz_min` of every
> family = throughput cell in each v2.4.0 `model_results.json`.

### 2.4 Several metrics are host-bound rather than NPU-bound

- **PCIe lane width caps the lightest models.** ORT-OFF nano and small throughput is
  limited by how fast frames cross the PCIe link, not by NPU compute. Both single-lane
  (**Gen3 ×1**) boards — `RPi5B_M1` and `RPi5B_M1M` — reach a ceiling of **~179 fps** on
  nano object detection, whereas the ×2 and ×4 boards reach **~315–320 fps** on the
  *same* NPU and release. This is the dominant reason the nano cross-host spread is wide
  while the medium/large/x-large spread is narrow
  ([§5.1](#51-the-npu-is-the-performance-anchor)).

  NPU utilisation confirms this directly. During the nano throughput measurement, average
  NPU core utilisation stays at 44% (`RPi5B_M1`) and 56% (`RPi5B_M1M`) on the Gen3 ×1
  boards, against **89–91%** on the ×2 and ×4 boards — the ×1 boards' NPU spends more than
  half of the time waiting for input. On the same boards, utilisation recovers to 89–92%
  from medium upwards, because the longer compute time reduces the relative weight of the
  transfer. For reference, theoretical one-way PCIe bandwidth is ≈1.0 GB/s for Gen3 ×1,
  ≈2.0 GB/s for ×2 and ≈3.9 GB/s for ×4.

- **Latency is bounded by the host CPU and the interconnect.** Same M1 module, same
  v2.4.0 release, object detection nano: `RPi5B_M1` measures 21.1 ms against
  `OrangePi5+_M1` at 37.1 ms. That spread is a host property, not an NPU property
  ([§6](#6-inference-latency)).

- **Classification end-to-end FPS is decoder-bound, not NPU-bound.** The classification
  model is small (224×224 input), so the NPU is only lightly loaded; under this light
  load the ARM boards' hardware decoders sustained a higher decoded-frame rate than the
  x86 decode path (OrangePi 1072.7 fps against H1-Quattro 772.4 fps end-to-end).
  Classification end-to-end FPS should therefore be read as a *pipeline and decoder*
  figure, not as an NPU-capability figure.

### 2.5 These are normalised benchmark conditions, not a production duty cycle

The protocol deliberately controls conditions so that numbers are comparable. A production
deployment differs in four ways that matter when sizing a system:

| Benchmark condition | Production reality | Implication |
|---|---|---|
| Each model × ORT cell starts from a controlled thermal state (cooldown to ≤ min(idle + Δ10 °C, 55 °C); a start above 60 °C is rejected) | A 24/7 pipeline never cools down between models | On thermally-limited boards, sustained operation can throttle **more** than [§2.3](#23-boards-that-reach-their-thermal-limit-throttle-in-the-sustained-phases) shows. Treat those figures as an upper bound for continuous duty. |
| One Full HD (1920×1080) 30 fps **H.264** clip per task | Other codecs (H.265), resolutions, bitrates, and object densities | The decoder and post-processing load change with the stream. H.265 or higher resolutions shift the host-bound ceiling of [§7.1](#71-for-light-models-the-ceiling-is-the-host-not-the-npu). |
| Latency is a cold, single-core, synchronous single-shot | A warm, asynchronous, multi-core serving path | Use latency for *relative* host responsiveness ([§6](#6-inference-latency)), not as a production per-frame budget. |
| Channel capacity uses a **30 fps per-channel** threshold | An SLA of 15 fps or 60 fps per channel | Capacity is threshold-dependent. Re-run with `--fps-threshold <fps>` to size against your own SLA. |

---

## 3. What Was Measured — Terms and Method

This section defines every term used in the remainder of the report.

### 3.1 Workload

**Model sizes.** YOLO26 ships in five sizes — `n` (nano) < `s` (small) < `m` (medium) <
`l` (large) < `x` (extra-large). Larger models are more accurate but slower.

**Input resolutions.** Object detection, pose estimation and segmentation use 640×640;
oriented bounding box uses 1024×1024; classification uses 224×224. All video input is
Full HD (1920×1080) at 30 fps.

### 3.2 Hardware

**NPU (Neural Processing Unit).** The DEEPX accelerator — module `M1` or `M1M`, or the
four-chip `H1-Quattro` card — that executes the neural network. All modules run at a
nominal 1000 MHz core clock.

### 3.3 Metrics

**Throughput (model-level, FPS).** Sustained frame rate from the DEEPX `run_model` tool,
driving the NPU **asynchronously across all cores** for 30 seconds. This is the purest
measure of **NPU compute capacity**: no video decoding and no rendering are involved.

**Latency (ms).** Time to process a **single frame**, measured **single-core and
synchronously** (`run_model` 300-loop mode). It reflects the responsiveness of one
inference call, including the host↔NPU round trip.

**End-to-end FPS.** Frame rate of the **complete GStreamer video pipeline** — decode →
preprocess → NPU inference → post-process — measured through the DEEPX dx_stream
elements. This is the figure a real video-analytics application experiences.

**Maximum channels.** The largest number of simultaneous video streams for which
**every** stream still sustains at least 30 fps (the per-channel threshold). It is found
by a boundary search that increases the stream count until any stream drops below
30 fps. A result is counted only when its status is ok, all repetitions completed, and
the per-channel FPS meets the threshold.

### 3.4 ONNX-Runtime mode (ORT ON / OFF) — where the model's CPU part is executed

Where necessary, the DEEPX compiler partitions a model graph into an **NPU part** and a
**CPU part**. The ORT mode selects whether that CPU part is executed through ONNX Runtime:

| Mode | What the runtime executes | Returned output | Cost |
|------|---------------------------|-----------------|------|
| **ORT ON** | NPU part **+** CPU part, the latter offloaded to the **host CPU** through the ONNX Runtime library | Identical to the source ONNX model — directly usable | Adds host-CPU work to every frame |
| **ORT OFF** | NPU part only | Raw NPU output tensors | No host-CPU offload; the application must implement the equivalent computation itself |

Both modes are measured and published for every cell, so the mode can be selected
according to whether the application requires output identical to the source ONNX model,
or according to which mode performs better.

### 3.5 Measurement Details

**Repetitions.** Latency = one run of 300 loops; throughput = mean of three 30-second
runs; end-to-end = mean of three runs. Each measurement is preceded by one warm-up run,
which is discarded. Tables quote the mean with `±` the standard deviation of those runs; how
that dispersion relates to throttling is covered in
[§2.3](#23-boards-that-reach-their-thermal-limit-throttle-in-the-sustained-phases). The full
protocol parameters are listed in the [Appendix](#112-measurement-protocol--key-parameters).

**Buffer-count — how the throughput ceiling is found.** Throughput against
`run_model --buffer-count` is a saturation curve, so **every throughput cell here is a sweep**:
the published figure is the ceiling, not the value at the default (6). Across the v2.4.0 cells the
median winning buffer-count falls as the model grows — **7 (nano, small) → 6 (medium) →
5 (large) → 4 (x-large)** — so an application that drives asynchronous inference itself and
leaves the flag at a default can fall short of these numbers. The flag applies to the model-level
path only — not to latency, and not to the E2E/multi-stream pipelines.

---

## 4. Test Environments

Six environments were measured, ranging from a four-chip x86 server down to a Raspberry
Pi 5, each fitted with a DEEPX NPU. The environment name — used as the identity key
throughout this report and the dashboard — encodes both the host and the NPU module.

| Environment | Host CPU | Arch | RAM | DEEPX NPU | Chips | PCIe link | CPU governor | Video decoder |
|-------------|----------|:----:|----:|-----------|:-----:|:---------:|:------------:|---------------|
| **BIOSTAR_H1-Quattro** | AMD Ryzen 5 9600X (6-core) | x86_64 | 30.5 GB | H1-Quattro card | 4 | Gen3 ×4 | powersave | vaapidecodebin (HW) |
| **DX-AIPlayer-N97_M1** | Intel N97 (4-core) | x86_64 | 7.5 GB | M1 module | 1 | Gen3 ×2 | powersave | vah264dec (HW) |
| **OrangePi5+_M1** | Rockchip RK3588 (A76/A55) | aarch64 | 15.6 GB | M1 module | 1 | Gen3 ×4 | ondemand | mppvideodec (HW) |
| **ROCK5B+_M1** | Rockchip RK3588 (A76/A55) | aarch64 | 7.8 GB | M1 module | 1 | Gen3 ×2 | ondemand | mppvideodec (HW) |
| **RPi5B_M1** | Broadcom BCM2712 (Cortex-A76) | aarch64 | 7.9 GB | M1 module | 1 | Gen3 ×1 | ondemand | avdec_h264 (SW) |
| **RPi5B_M1M** | Broadcom BCM2712 (Cortex-A76) | aarch64 | 7.9 GB | **M1M** module | 1 | Gen3 ×1 | ondemand | avdec_h264 (SW) |

> **Source:** `host` / `npu` fields of each v2.4.0 `environment.json`, and the `decoder`
> field of `pipeline_results.json`.

Within each release, all six environments ran the identical software stack listed in
[§2.1](#21-the-version-trend-reflects-the-entire-release-stack-not-one-component).

---

## 5. NPU Compute Performance (Model-Level Throughput)

This is the **purest measure of the DEEPX NPU**: sustained multi-core throughput from
`run_model`, with no video decoding or rendering in the path.

**Object detection, throughput (fps), ORT OFF, current release (v2.4.0):**

| Environment | n | s | m | l | x |
|-------------|--:|--:|--:|--:|--:|
| BIOSTAR_H1-Quattro | 1326.0 | 794.0 | 491.1 | 372.5 | 201.8 |
| DX-AIPlayer-N97_M1 | 314.9 | 197.8 | 120.1 | 85.6 | 47.4 |
| OrangePi5+_M1 | 320.3 | 197.6 | 117.4 | 87.2 | 48.0 |
| ROCK5B+_M1 | 319.3 | 188.0 | 107.5 | 84.9 | 42.7 |
| RPi5B_M1 | 179.5 | 179.1 | 118.7 | 86.8 | 49.2 |
| RPi5B_M1M | 179.2 | 153.2 | 73.5 | 60.0 | 26.3 |

> **Source:** `results/<env>/<v2.4.0 run>/model_results.json`, task = object_detection,
> family = throughput, `use_ort` = false.

### 5.1 The NPU is the performance anchor

Across the four single-M1 machines, the medium and larger models — where the NPU is the
bottleneck — agree closely, while the light models spread out for reasons that are
entirely host-side:

| Size | N97 | OrangePi | ROCK5B | RPi5B_M1 | Mean | Spread (coefficient of variation) |
|------|----:|---------:|-------:|---------:|-----:|:--------------------------------:|
| l | 85.6 | 87.2 | 84.9 | 86.8 | 86.1 | **1.0 %** |
| m | 120.1 | 117.4 | 107.5 | 118.7 | 115.9 | 4.3 % |
| x | 47.4 | 48.0 | 42.7 | 49.2 | 46.8 | 5.3 % |
| s | 197.8 | 197.6 | 188.0 | 179.1 | 190.6 | 4.1 % |
| n | 314.9 | 320.3 | 319.3 | 179.5 | 283.5 | 21.2 % |

> **Source:** the object-detection v2.4.0 ORT-OFF table above; coefficient of variation =
> the **population standard deviation ÷ mean** of the four M1 host values, computed from the
> unrounded fps figures.

**Interpretation.**

- At size **l** the four hosts agree to within **1.0%**. The host barely matters here,
  because the DEEPX NPU performs essentially all of the work and the module is identical.
- The residual spread at **m** and **x** is driven by `ROCK5B+_M1` thermal throttling
  ([§2.3](#23-boards-that-reach-their-thermal-limit-throttle-in-the-sustained-phases)),
  which trims that board's figures below the other three.
- The wide spread at **nano** is a PCIe-bandwidth effect, not a host-CPU one: the ×1 boards
  cap at ~179 fps against ~315–320 fps on the ×2/×4 boards, with NPU utilisation at only 44%
  ([§2.4](#24-several-metrics-are-host-bound-rather-than-npu-bound)).

**Implication for capacity planning.** Deployments should be sized on the medium, large
and x-large figures, which are portable across hosts. The nano and small figures depend
on the host's PCIe link and CPU.

### 5.2 H1-Quattro scales model-level throughput by approximately 4× with its four chips

The H1-Quattro card carries four M1 chips. The comparison below covers **`run_model`
model-level throughput only** (object detection, ORT OFF); at medium, large and x-large,
where the NPU is the bottleneck, it reaches close to four times the mean of the four
single-M1 hosts:

| Object detection (v2.4.0, ORT OFF) | H1-Quattro | M1 mean | Ratio |
|------------------------------------|-----------:|--------:|:-----:|
| m | 491.1 | 115.9 | 4.24× |
| l | 372.5 | 86.1 | 4.32× |
| x | 201.8 | 46.8 | 4.31× |

> **Source:** the object-detection v2.4.0 ORT-OFF table in
> [§5](#5-npu-compute-performance-model-level-throughput); M1 mean taken over the four
> M1 hosts (which include ROCK5B's throttled figures).

This ratio applies to **model-level throughput only.** Single-stream end-to-end FPS runs
into the host supply limit first and reaches just 47% of throughput at nano; the four chips'
spare capacity instead shows up as channel count (17 channels at nano) — see
[§7.1](#71-for-light-models-the-ceiling-is-the-host-not-the-npu) and
[§8](#8-multi-stream-channel-capacity).

### 5.3 Task difficulty ordering is consistent across environments

A more complex output head and a larger input both cost throughput. At size m, v2.4.0,
ORT OFF, the ordering is the same in every environment (values shown for
`BIOSTAR_H1-Quattro` / `RPi5B_M1`):

| Task | Input | H1-Quattro | RPi5B_M1 |
|------|:-----:|-----------:|---------:|
| Classification (minimal head) | 224×224 | 5514.7 fps | 1401.1 fps |
| Object detection | 640×640 | 491.1 fps | 118.7 fps |
| Pose estimation | 640×640 | 468.6 fps | 112.6 fps |
| Segmentation (mask output) | 640×640 | 321.5 fps | 80.0 fps |
| Oriented bounding box (largest input) | 1024×1024 | 174.4 fps | 42.2 fps |

> **Source:** `model_results.json`, size = m, family = throughput, ORT OFF, v2.4.0 runs of
> the two environments named.

---

## 6. Inference Latency

Latency is a single-frame, single-core measurement. It is a **responsiveness** figure and
is partly **host- and interconnect-bound**.

**Object detection latency (ms), ORT OFF, v2.4.0:**

| Environment | n | s | m | l | x |
|-------------|--:|--:|--:|--:|--:|
| BIOSTAR_H1-Quattro | 10.38 | 16.28 | 23.31 | 30.80 | 56.22 |
| DX-AIPlayer-N97_M1 | 22.35 | 28.78 | 36.43 | 43.64 | 69.57 |
| OrangePi5+_M1 | 37.07 | 44.01 | 42.93 | 57.78 | 86.21 |
| ROCK5B+_M1 | 34.29 | 35.72 | 50.14 | 59.30 | 88.51 |
| RPi5B_M1 | 21.13 | 27.04 | 33.26 | 41.32 | 66.79 |
| RPi5B_M1M | 22.50 | 29.20 | 39.60 | 46.40 | 75.43 |

> **Source:** `results/<env>/<v2.4.0 run>/model_results.json`, task = object_detection,
> family = latency, ORT OFF.

**Interpretation.** Unlike throughput, latency varies substantially across the M1 hosts:
at nano, 21.1 ms on `RPi5B_M1` against 37.1 ms on `OrangePi5+_M1`, on the *same NPU
module and release*. A single synchronous call is dominated by the host CPU and the
host↔NPU interconnect rather than by raw NPU compute — the two Raspberry Pi 5 hosts
return lower latency than the RK3588 boards even though the NPU module is identical.

Latency should therefore be used to judge single-request responsiveness on a specific
host, and throughput ([§5](#5-npu-compute-performance-model-level-throughput)) to judge
NPU capacity.

**ORT ON latency includes the host-CPU segment.** In the ORT ON measurements, `run_model`
also reports the execution time of the model's CPU part (`cpu_0_ms`). For object detection
at sizes n, m and x, that time is 0.26–1.38 ms on the x86 boards and 2.3–8.0 ms on the ARM
boards. Latency-sensitive applications should weigh the convenience of ORT ON against this
additional time
([§3.4](#34-onnx-runtime-mode-ort-on--off--where-the-models-cpu-part-is-executed)).

> **Source:** `cpu_0_ms` in each v2.4.0 `model_results.json`, task = object_detection,
> family = latency, `use_ort` = true.

---

## 7. End-to-End Video Pipeline (Single Stream)

End-to-end FPS measures the complete pipeline (decode → preprocess → NPU →
post-process) on a single Full HD 30 fps stream — the figure a real application observes.

**Object detection end-to-end FPS, v2.4.0, shown for the better ORT mode:**

| Environment | ORT | n | s | m | l | x | Video decoder |
|-------------|:---:|--:|--:|--:|--:|--:|---------------|
| BIOSTAR_H1-Quattro | ON | 496.8 | 494.4 | 491.7 | 367.8 | 202.6 | vaapidecodebin (HW) |
| DX-AIPlayer-N97_M1 | OFF | 184.9 | 164.1 | 116.6 | 85.1 | 49.0 | vah264dec (HW) |
| OrangePi5+_M1 | ON | 148.1 | 125.0 | 98.5 | 80.1 | 48.1 | mppvideodec (HW) |
| ROCK5B+_M1 | ON | 141.5 | 130.4 | 108.1 | 85.5 | 36.5 | mppvideodec (HW) |
| RPi5B_M1 | OFF | 80.1 | 80.1 | 79.5 | 80.3 | 48.8 | avdec_h264 (SW) |
| RPi5B_M1M | OFF | 79.8 | 80.2 | 77.8 | 57.6 | 21.2 | avdec_h264 (SW) |

> **Source:** `results/<env>/<v2.4.0 run>/pipeline_results.json`, task = object_detection.
> The ORT mode shown per row is the one that produced the higher nano FPS; "HW" and "SW"
> mark a hardware or software video decoder. Both modes for every environment are present
> in the raw data and the dashboard.

**Interpretation.**

- **The video decoder can cap light models.** On `RPi5B_M1`, nano through large all land
  at ~80 fps regardless of model size: the **software** H.264 decoder (`avdec_h264`),
  not the NPU, is the ceiling for light models. Boards with hardware decoders
  (`vaapidecodebin`, `vah264dec`, `mppvideodec`) do not meet this wall until far higher
  rates.

- **For heavy models the NPU becomes the ceiling again**, and end-to-end FPS tracks the
  throughput ordering of [§5](#5-npu-compute-performance-model-level-throughput). On
  `RPi5B_M1` the x-large model runs at 48.8 fps end-to-end — below the ~80 fps decoder
  cap — because the NPU is now the slower stage. On `RPi5B_M1M` the large and x-large
  figures fall further (57.6 / 21.2 fps) as a result of the slower SKU combined with
  throttling.

- **Which ORT mode wins reverses with the environment and the task.** For light models the
  difference reaches +48.8%, and there is no single default. The full comparison and its
  cause are covered in
  [§7.2](#72-the-optimal-ort-mode-is-determined-by-the-environment--task-combination).

### 7.1 For light models the ceiling is the host, not the NPU

Comparing end-to-end FPS against the model throughput of
[§5](#5-npu-compute-performance-model-level-throughput) in the same ORT mode reveals that
more than half of the NPU's compute capacity is unused at light model sizes.

**Object detection, v2.4.0 — `end-to-end ÷ model throughput` / average NPU utilisation
during the end-to-end measurement:**

| Size | BIOSTAR_H1-Quattro | OrangePi5+_M1 | RPi5B_M1 |
|:----:|:------------------:|:-------------:|:--------:|
| n | 47 % / NPU 21 % | 82 % / NPU 37 % | 45 % / NPU 18 % |
| s | 63 % / NPU 41 % | 69 % / NPU 58 % | 45 % / NPU 34 % |
| m | 100 % / NPU 70 % | 84 % / NPU 73 % | 67 % / NPU 55 % |
| l | 99 % / NPU 74 % | 101 % / NPU 91 % | 92 % / NPU 80 % |
| x | 100 % / NPU 83 % | 99 % / NPU 93 % | 99 % / NPU 94 % |

> **Source:** `avg_e2e_fps` from `pipeline_results.json` ÷ the throughput `fps` of the same
> ORT mode in `model_results.json`, together with `npu_total_avg_pct` from
> `pipeline_results.json`. Each size uses whichever ORT mode produced the higher
> end-to-end figure.

**Interpretation.**

- At light sizes (n, s) the ratio is only 45–82% and NPU utilisation stays at 18–41%. The
  ceiling is not the NPU but the host-side rate of a single pipeline (decode → preprocess
  → submit → post-process).
- From medium upwards the ratio rises to 92–101% and utilisation to 55–94%, because the
  NPU compute time becomes long enough for the host to keep up.
- **Deployment implication:** at light sizes the spare NPU capacity is recovered **only
  through multi-stream operation.** A single nano stream on `BIOSTAR_H1-Quattro` reaches
  just 47% of its throughput, yet the same board sustains 17 channels in multi-stream
  ([§8](#8-multi-stream-channel-capacity)). Conversely, from medium upwards a single stream
  already saturates the NPU, so there is little room for channel scaling.

### 7.2 The optimal ORT mode is determined by the environment × task combination

For light models (n, s) the end-to-end difference between the two modes reaches +48.8%
(OrangePi5+_M1 object detection, nano), and which mode wins reverses with the environment
and the task.

| Environment | Object Detection | Pose Estimation | Segmentation | OBB | Classification |
|-------------|:----------------:|:---------------:|:------------:|:---:|:--------------:|
| BIOSTAR_H1-Quattro | **ON** (+9.9–10.6 %) | tie | **ON** (+12.9–14.6 %) | tie | tie |
| DX-AIPlayer-N97_M1 | **OFF** (+14.6–17.4 %) | OFF (+11.4–13.4 %) | **OFF** (+12.2–14.4 %) | tie | tie |
| OrangePi5+_M1 | **ON** (+24.9–48.8 %) | OFF (+12.5–21.3 %) | **ON** (+4.4–20.7 %) | OFF (+1.3–8.9 %) | tie |
| ROCK5B+_M1 | **ON** (+36.6–48.8 %) | OFF (+8.8–23.1 %) | **ON** (+4.0–11.5 %) | tie | tie |
| RPi5B_M1 | **OFF** (+18.3–18.7 %) | OFF (+36.3–37.4 %) | **OFF** (+23.2–23.5 %) | OFF (+1.1–18.3 %) | tie |
| RPi5B_M1M | **OFF** (+17.5–18.9 %) | OFF (+36.5–37.4 %) | **OFF** (+22.6–23.8 %) | OFF (+0.0–6.9 %) | tie |

> **Source:** `results/<env>/<v2.4.0 run>/pipeline_results.json`, sizes n and s. The
> bracketed figures are the winning mode's relative gain — **the range spanned by the nano
> and small values** — computed directly from `avg_e2e_fps` (e.g. OrangePi5+_M1 object
> detection nano = 148.1 ÷ 99.6 − 1 = +48.8 %). **"tie" marks cells where both nano and
> small differ by less than 5%.** Classification has no CPU part, so the two modes coincide
> ([§3.4](#34-onnx-runtime-mode-ort-on--off--where-the-models-cpu-part-is-executed)).

**Why it reverses.** ORT OFF reduces host-CPU work inside the inference element, but the
computation does not disappear from the pipeline — it moves to the post-processing stage
that the application owns. Object detection on the Rockchip boards is the clearest case.

| OrangePi5+_M1, OD nano (v2.4.0) | ORT ON | ORT OFF |
|---------------------------------|-------:|--------:|
| End-to-end FPS | 148.1 | 99.6 |
| Host CPU utilisation | 250 % | 211 % |
| Average NPU utilisation | 37.3 % | 22.0 % |

> **Source:** `avg_e2e_fps` / `avg_cpu_pct` / `npu_total_avg_pct` of
> `pipeline_results.json`, task = object_detection, size = n.

In ORT OFF the CPU utilisation is *lower*, yet FPS and NPU utilisation both fall. The cause
is therefore not CPU saturation but a single serial stage (post-processing) becoming
slower. Every queue in the measured pipeline is `leaky=no`, so the stall propagates upstream
as backpressure and the NPU is left idle for want of new frames. With ORT ON, ONNX Runtime
handles the model's CPU part, so the tensors reaching the post-processing stage are already
reduced and the stall does not occur.

The reverse case follows the same principle: on `RPi5B_M1` and `RPi5B_M1M` the software
decoder already consumes a large share of the CPU, so the extra work of ORT ON competes
with decoding and ORT OFF wins for every task.

**Segmentation carries the highest host post-processing cost of any task.** In the same
environment at nano with ORT ON, host CPU utilisation on `BIOSTAR_H1-Quattro` is 213% for
object detection against 517% for segmentation, because the mask output must be
reconstructed on the host. This is the main reason segmentation channel capacity trails
detection ([§8](#8-multi-stream-channel-capacity)).

### 7.3 Where the host sets the ceiling, a larger model costs no FPS

Restating [§7.1](#71-for-light-models-the-ceiling-is-the-host-not-the-npu) in deployment
terms: while the host is the ceiling, increasing the model size barely changes end-to-end
FPS. Accuracy is available at no throughput cost in that range.

| Environment | Largest size within 5 % of nano | Evidence (object detection end-to-end FPS) |
|-------------|:-------------------------------:|--------------------------------------------|
| BIOSTAR_H1-Quattro | **m** | n 496.8 → s 494.4 → m 491.7 → l 367.8 |
| DX-AIPlayer-N97_M1 | n | n 184.9 → s 164.1 (−11 %) |
| OrangePi5+_M1 | n | n 148.1 → s 125.0 (−16 %) |
| ROCK5B+_M1 | n | n 141.5 → s 130.4 (−8 %) |
| RPi5B_M1 | **l** | n 80.1 → s 80.1 → m 79.5 → l 80.3 |
| RPi5B_M1M | **m** | n 79.8 → s 80.2 → m 77.8 → l 57.6 |

> **Source:** `pipeline_results.json`, task = object_detection, taking the higher of the two
> ORT modes at each size. The criterion is retaining at least 95% of the nano figure.

The same calculation holds per task. On `RPi5B_M1`, pose estimation is free up to medium and
segmentation up to large; on `BIOSTAR_H1-Quattro`, both pose estimation and segmentation are
free up to small. By contrast, `DX-AIPlayer-N97_M1`, `OrangePi5+_M1` and `ROCK5B+_M1` are
already NPU- or pipeline-limited at nano, so FPS falls as soon as the size increases.

**Deployment guidance:** selecting the largest model that still meets the target FPS raises
accuracy on the same hardware. This headroom originates in the host ceiling, however — once
the host is improved (hardware decoder, wider PCIe link), model size governs FPS again.

---

## 8. Multi-Stream Channel Capacity

Channel capacity is the maximum number of Full HD 30 fps streams for which each stream
still sustains ≥30 fps.

**Object detection, maximum channels, v2.4.0 (better of ORT ON/OFF):**

| Environment | n | s | m | l | x |
|-------------|--:|--:|--:|--:|--:|
| BIOSTAR_H1-Quattro | 17 | 17 | 16 | 12 | 6 |
| DX-AIPlayer-N97_M1 | 6 | 5 | 3 | 2 | 1 |
| OrangePi5+_M1 | 4 | 4 | 3 | 2 | 1 |
| ROCK5B+_M1 | 4 | 4 | 2 | 1 | 1 |
| RPi5B_M1 | 2 | 2 | 2 | 2 | 1 |
| RPi5B_M1M | 2 | 2 | 1 | 1 | 0 |

> **Source:** `results/<env>/<v2.4.0 run>/multi_stream_results.json`, task =
> object_detection, maximum `stream_count` satisfying the stable-capacity rule (status ok + all runs completed + per-channel FPS ≥ 30).

**Interpretation.** Channel capacity is the multi-stream generalisation of end-to-end FPS
and inherits the same bottlenecks:

- The H1-Quattro's four chips give it a substantial lead — up to 17 object-detection
  channels at nano — while the single-M1 boards land in the 2–6 channel range depending
  on host CPU, PCIe link and cooling.
- The two Gen3 ×1 boards (`RPi5B_M1`, `RPi5B_M1M`) cap at 2 channels for light detection
  because of the PCIe link
  ([§2.4](#24-several-metrics-are-host-bound-rather-than-npu-bound)).
- `RPi5B_M1M` records 0 channels at x-large: the slower M1M SKU
  ([§2.2](#22-m1-and-m1m-are-different-products-and-must-not-be-combined)) combined with
  throttling ([§2.3](#23-boards-that-reach-their-thermal-limit-throttle-in-the-sustained-phases))
  leaves it unable to sustain even one x-large stream at 30 fps.

**Classification is intentionally not measured for multi-stream.** A 224×224 classifier
is not representative of real multi-stream video-analytics workloads, and its end-to-end
figure is decoder-bound
([§2.4](#24-several-metrics-are-host-bound-rather-than-npu-bound)).

---

## 9. Performance Trend Across dx-all-suite Releases

The same environments were measured on the two releases committed under `results/`
(v2.3.3 and v2.4.0). Because DX-COM (model recompilation), the DX-RT runtime, the RT
driver, the PCIe driver and the NPU firmware all changed between the two sets of runs
([§2.1](#21-the-version-trend-reflects-the-entire-release-stack-not-one-component)), this
trend reflects the **combined** improvement of that whole stack and cannot be attributed to
any individual component.

**Object detection throughput (fps), ORT OFF, v2.3.3 → v2.4.0:**

| Environment | Size | v2.3.3 | v2.4.0 | Change |
|-------------|:----:|-------:|-------:|:------:|
| BIOSTAR_H1-Quattro | m | 376.6 | 491.1 | **+30.4 %** |
| BIOSTAR_H1-Quattro | l | 277.2 | 372.5 | **+34.3 %** |
| BIOSTAR_H1-Quattro | x | 158.2 | 201.8 | **+27.5 %** |
| DX-AIPlayer-N97_M1 | m | 91.1 | 120.1 | +31.8 % |
| DX-AIPlayer-N97_M1 | l | 66.9 | 85.6 | +27.9 % |
| OrangePi5+_M1 | m | 90.5 | 117.4 | +29.7 % |
| OrangePi5+_M1 | l | 67.3 | 87.2 | +29.5 % |
| RPi5B_M1 | m | 90.8 | 118.7 | +30.6 % |
| RPi5B_M1 | l | 67.4 | 86.8 | +28.9 % |
| RPi5B_M1M | m | 55.7 | 73.5 | +32.0 % |
| RPi5B_M1M | l | 41.8 | 60.0 | +43.4 % |

> **Source:** `model_results.json` of each environment's v2.3.3 and v2.4.0 runs, task =
> object_detection, family = throughput, ORT OFF, matched by (task, size, ORT mode).

**Interpretation.** Across the 18 cells of the NPU-bound range (medium, large, x-large) the
model-level throughput change has a median of **+28.4%**, with 14 of the 18 in the +25–35%
band. The lowest is `ROCK5B+_M1` at x-large (+12.9%), whose v2.4.0 run throttled
([§2.3](#23-boards-that-reach-their-thermal-limit-throttle-in-the-sustained-phases)); the
highest is `RPi5B_M1M` at large (+43.4%). Every cell improved.

Across the 12 light-model cells (nano, small) the change is far wider: −0.1% to +63.2%. That
range is governed by the host and PCIe ceilings rather than the NPU
([§2.4](#24-several-metrics-are-host-bound-rather-than-npu-bound),
[§7.1](#71-for-light-models-the-ceiling-is-the-host-not-the-npu)), so it is not summarised as
a single band. `RPi5B_M1` at nano is −0.1%: both releases sit at the same Gen3 ×1 link
ceiling of ~179 fps.

This is the clearest single argument for **upgrading to the latest dx-all-suite
release**: **at the model level**, identical hardware runs materially faster. Single-stream
E2E, however, does not track this improvement rate in cells governed by the host ceiling
([§2.1](#21-the-version-trend-reflects-the-entire-release-stack-not-one-component)).

---

## 10. Deployment Guidance by Environment

The guidance below is grounded in the tables above; all figures are v2.4.0.

- **BIOSTAR_H1-Quattro (four-chip x86 server).** The high-density option: 16–17
  object-detection channels, or 20 pose channels, at nano. It is actively cooled and
  holds its clock throughout the model phase (0 throttled model cells). Recommended
  where channel density is the primary requirement.

- **DX-AIPlayer-N97_M1 (compact x86 AI box).** A balanced single-M1 appliance: 6
  object-detection and 7 pose channels at nano, with a hardware decoder and active
  cooling. A sound general-purpose edge box.

- **OrangePi5+_M1 (ARM SBC, single M1).** A capable single-NPU board with a ×4 PCIe link
  and a hardware decoder: 4 object-detection and 8 pose channels at nano, and the best
  nano/small model throughput among the ARM boards. It held its clock throughout the
  model phase; additional cooling is recommended for sustained multi-stream operation.

- **ROCK5B+_M1 (ARM SBC, single M1).** The same RK3588 class as the OrangePi, but this
  unit reached its thermal limit earlier (24 throttled model-level cells), which trims
  its medium, large and x-large figures. It is capable of 2–4 detection channels and up
  to 8 pose channels; **active cooling is recommended** to recover the throttled
  headroom.

- **RPi5B_M1 (Raspberry Pi 5, single M1).** An entry-level configuration, viable for 1–2
  channels of detection or segmentation. Two ceilings apply: its **software** video
  decoder caps light-model end-to-end FPS at approximately 80 fps, and its **Gen3 ×1**
  PCIe link caps nano/small model throughput at approximately 179 fps. A host with
  hardware decoding and a wider PCIe link removes both.

- **RPi5B_M1M (Raspberry Pi 5, M1M module).** The lowest tier measured: the M1M SKU is
  31–47% slower than the M1 on heavy models
  ([§2.2](#22-m1-and-m1m-are-different-products-and-must-not-be-combined)), and this unit
  additionally throttled
  ([§2.3](#23-boards-that-reach-their-thermal-limit-throttle-in-the-sustained-phases)).
  Deployments should be sized conservatively, treating its heavy-model figures as a
  floor.

### Memory footprint and deployment fit

Compute is not the only constraint: host RAM also has to be budgeted, and NPU-side memory has to
be verified on the target.

**Host memory scales with channel count.** At the measured channel-capacity points, pipeline RSS
ranged from **≈211 MiB** (OrangePi5+_M1, detection nano, 4 channels) to **≈1376 MiB**
(BIOSTAR_H1-Quattro, segmentation x-large, 5 channels), with each additional channel adding roughly
tens of MiB. High channel counts and heavy models therefore need host RAM budgeted alongside NPU
capacity — on an 8 GB SBC, host memory can bind before the NPU does.

**NPU memory budgets differ by module.** The M1 carries LPDDR5 3.92 GiB, the M1M LPDDR4
1.92 GiB — roughly half
([§2.2](#22-m1-and-m1m-are-different-products-and-must-not-be-combined)). A model's NPU footprint
grows with input resolution and size, so choose the task/size combination — and whether several
models must be resident at once — against the budget of the module being deployed on. Confirm the
actual figure on the target device.

### General rules of thumb

- Plan NPU capacity from the **medium/large/x-large throughput** figures, which are
  host-portable ([§5.1](#51-the-npu-is-the-performance-anchor)). Reserve the nano and
  small figures for cases where the host's PCIe link and CPU have been verified to keep
  up.
- **Light models need multi-stream to use the full NPU.** A single stream reaches only
  45–82% of throughput
  ([§7.1](#71-for-light-models-the-ceiling-is-the-host-not-the-npu)).
- **Choose the largest model that still meets the target FPS.** Where the host is the
  ceiling, increasing the size costs almost no FPS, so accuracy comes for free
  ([§7.3](#73-where-the-host-sets-the-ceiling-a-larger-model-costs-no-fps)).
- **Select the ORT mode from the environment × task matrix**
  ([§7.2](#72-the-optimal-ort-mode-is-determined-by-the-environment--task-combination)).
  Independently of performance, an application that requires output identical to the source
  ONNX model needs **ORT ON**; one that implements the equivalent computation itself may
  also use **ORT OFF**
  ([§3.4](#34-onnx-runtime-mode-ort-on--off--where-the-models-cpu-part-is-executed)).
- For sustained multi-stream operation on passively cooled boards, budget for cooling or
  plan against the throttled figures rather than the peak ones, and treat an unusually wide
  measurement spread as a thermal signal
  ([§2.3](#23-boards-that-reach-their-thermal-limit-throttle-in-the-sustained-phases)).

---

## 11. Appendix

### 11.1 Reproducing the Benchmark

Run the following from the `dx-benchmark/` directory; setup instructions are in the
tool's [`README.md`](../README.md).

```bash
# Check the environment and print a fingerprint
./run.sh preflight

# Preview the benchmark matrix without running it
./run.sh dry-run

# Run the full suite (model-level + end-to-end + multi-stream)
./run.sh run

# Run only specific sizes / task
./run.sh run --sizes n,s --task object_detection

# Rerun only the failed items of an existing result directory
./run.sh run --resume results/<env>/<run_id> --retry-failed

# Regenerate a report from an existing result directory
python3 -m benchmark report results/<env>/<run_id>

# Rebuild the dashboard from all results
python3 -m benchmark dashboard results
```

### 11.2 Measurement Protocol — Key Parameters

| Parameter | Value |
|-----------|-------|
| Protocol version | v1 (thermal mode: steady) |
| Throughput measurement duration | 30 seconds |
| Latency loop count | 300 loops (single-core, synchronous) |
| Throughput repetitions | 3 |
| End-to-end repetitions | 3 |
| Warm-up runs | 1 (discarded) |
| Multi-stream per-channel threshold | 30 fps |
| Stable-capacity rule | status ok + all runs completed + per-channel FPS ≥ 30 |
| Thermal hot-start block | 60 °C (run rejected above this) |
| Cooldown points | once at the start of each model × ORT cell + once immediately before the E2E phase (protocol v1) |
| Cooldown target | min(idle + 10 °C, 55 °C) |
| Video input | Full HD (1920×1080), 30 fps |

> **Source:** `protocol` block of each run's `environment.json`.

### 11.3 Detailed Results by Environment (current release)

Full machine-readable results for each environment's v2.4.0 run:

| Environment | Report |
|-------------|--------|
| BIOSTAR_H1-Quattro | [`results/BIOSTAR_H1-Quattro/20260722_151413/REPORT.md`](../results/BIOSTAR_H1-Quattro/20260722_151413/REPORT.md) |
| DX-AIPlayer-N97_M1 | [`results/DX-AIPlayer-N97_M1/20260722_151104/REPORT.md`](../results/DX-AIPlayer-N97_M1/20260722_151104/REPORT.md) |
| OrangePi5+_M1 | [`results/OrangePi5+_M1/20260722_165355/REPORT.md`](../results/OrangePi5+_M1/20260722_165355/REPORT.md) |
| ROCK5B+_M1 | [`results/ROCK5B+_M1/20260722_080528/REPORT.md`](../results/ROCK5B+_M1/20260722_080528/REPORT.md) |
| RPi5B_M1 | [`results/RPi5B_M1/20260722_150437/REPORT.md`](../results/RPi5B_M1/20260722_150437/REPORT.md) |
| RPi5B_M1M | [`results/RPi5B_M1M/20260723_142408/REPORT.md`](../results/RPi5B_M1M/20260723_142408/REPORT.md) |

Each environment also has a v2.3.3 run under `results/<env>/`. The interactive dashboard
([`results/dashboard/index.html`](../results/dashboard/index.html)) allows any
combination of environment, version, task, size and ORT mode to be compared.

### 11.4 Glossary

| Term | Meaning |
|------|---------|
| **Backpressure** | The mechanism by which a downstream element's processing delay propagates upstream through non-leaky queues, limiting both overall throughput and the supply of frames to the NPU. Every queue in the measured pipeline is `leaky=no` |
| **Coefficient of variation** | Standard deviation ÷ mean, expressed as a percentage — used here to quantify cross-host spread |
| **CPU part (CPU offload)** | The portion of a compiled model's graph that the NPU cannot execute — for YOLO26, NMS plus the keypoint or mask decode. Executed on the host CPU only when ORT is ON. Distinct from the pipeline's post-processing stage. |
| **NPU · ORT · Throughput · Latency · End-to-end FPS · Maximum channels** | Defined in [§3](#3-what-was-measured--terms-and-method) |
| **NPU utilisation** | Average NPU core utilisation sampled by dxtop over the measurement window (`npu_total_avg_pct`). A low value indicates a host-bound state in which the NPU is waiting for input |
| **Thermal throttling** | NPU clock reduction under high temperature (the NPU steps its clock down from 1000 MHz) |

---

*Generated from the measurement data committed by the `dx-benchmark` tool
([`dx-benchmark/results/`](../results/)). To regenerate the underlying numbers or explore
them interactively, see [§11.1](#111-reproducing-the-benchmark) and the dashboard.*
