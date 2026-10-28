# YOLO26 × DEEPX NPU — Benchmark Analysis

> **What this report answers.** For each YOLO26 task and model size, what inference
> throughput a DEEPX NPU reaches on different host systems, and what E2E FPS and channel
> capacity a video application gets from it; which host-side factors (video decoding, CPU,
> PCIe link, cooling, memory) cause the difference; and how to choose a host and an NPU
> module for a target workload.
>
> **Data.** dx-all-suite **v2.5.0**, six host + NPU environments, five YOLO26 tasks × five
> model sizes, every cell measured with ONNX Runtime ON and OFF. Every figure can be
> re-derived from the per-run result files under [`results/`](../results/) or explored in
> the [dashboard](https://deepx-ai.github.io/dx-all-suite/dx-benchmark/).
>

---

## Contents

1. [Summary](#1-summary)
2. [Choosing a Configuration](#2-choosing-a-configuration)
3. [Inference Throughput](#3-inference-throughput)
4. [Inference Latency](#4-inference-latency)
5. [Video Pipeline: E2E FPS and Channel Capacity](#5-video-pipeline-e2e-fps-and-channel-capacity)
6. [Host-Side Limiting Factors](#6-host-side-limiting-factors)
7. [Choosing the ORT Mode](#7-choosing-the-ort-mode)
8. [Method and Limitations](#8-method-and-limitations)
9. [Appendix](#9-appendix)

**Metrics used throughout.** The report keeps model-level and video-pipeline figures apart
and always names which one it means (definitions in [§8.3](#83-metrics-and-procedure)):

| Metric | Level | What it measures |
|--------|-------|------------------|
| **Inference throughput** (FPS) | Model | Frames per second the NPU completes when fed as fast as possible (`dxrun`, asynchronous, no video). Quoted for the complete model (ORT ON) |
| **Inference latency** (ms) | Model | Time for one frame through the model, one request at a time |
| **E2E FPS** | Video pipeline | Frame rate of one 1920×1080 30 fps H.264 stream through the complete GStreamer pipeline (decode → pre-process → NPU → post-process), whose NPU stages are DX-Stream elements (`dxpreprocess`, `dxinfer`, `dxpostprocess`) |
| **Aggregate E2E FPS** | Video pipeline | Sum of the E2E FPS of all concurrent streams |
| **Channel capacity** | Video pipeline | Largest number of concurrent 1920×1080 30 fps streams that all sustain ≥ 30 fps |

**Model sizes.** YOLO26 comes in five sizes: **n** (nano), **s** (small), **m** (medium), **l**
(large) and **x** (extra-large). Larger sizes are more accurate and need more NPU time per
frame. This report calls sizes n and s *light models* and sizes l and x *heavy models*. Tables
label the sizes n…x; the text writes "size n" or the model name, for example "YOLO26-n".

**ORT ON / OFF.** A compiled YOLO26 model leaves part of its graph (the *CPU part*) to the
host. ORT ON runs the CPU part inside the inference call through ONNX Runtime and returns the
complete model's output. ORT OFF returns the raw NPU tensors; in the GStreamer pipeline the
`dxpostprocess` element then computes the CPU part with DX-Stream's post-processing library,
so both modes give the same final detections. Inference throughput and latency are therefore quoted with ORT ON; E2E FPS and
channel capacity compare both modes.

---

## 1. Summary

### 1.1 YOLO26-n E2E FPS and Channel Capacity

Single-stream E2E FPS and channel capacity of each environment with the smallest model,
YOLO26-n, on 1920×1080 30 fps H.264 video. Larger models give equal or lower E2E FPS;
results for every size are in [§5](#5-video-pipeline-e2e-fps-and-channel-capacity).

**Table 1. YOLO26-n (nano): single-stream E2E FPS / channel capacity at 30 fps per channel
(ORT mode used), dx-all-suite v2.5.0.** Input: 1920×1080 30 fps H.264.

| Environment | Object Detection | Pose Estimation | Segmentation | Oriented Bounding Box | Classification (FPS) |
|-------------|------------------|-----------------|--------------|-----------------------|----------------------|
| **BIOSTAR_H1-Quattro** | 493.6 / 17 (ON) | 554.6 / 20 (OFF) | 359.1 / 11 (ON) | 394.6 / 14 (ON) | 809.7 |
| **DX-AIPlayer-N97_M1** | 178.0 / 6 (OFF) | 192.2 / 7 (OFF) | 106.5 / 3 (OFF) | 105.3 / 3 (OFF) | 276.7 |
| **OrangePi5+_M1** | 149.2 / 4 (ON) | 248.0 / 8 (OFF) | 100.8 / 3 (ON) | 104.7 / 3 (OFF) | 1086.4 |
| **ROCK5B+_M1** | 140.7 / 4 (ON) | 227.5 / 8 (OFF) | 87.9 / 2 (ON) | 105.4 / 3 (OFF) | 972.9 |
| **RPi5B_M1** | 80.0 / 2 (OFF) | 113.5 / 3 (OFF) | 55.5 / 1 (OFF) | 82.7 / 2 (OFF) | 189.7 |
| **RPi5B_M1M** | 79.5 / 2 (OFF) | 112.0 / 3 (OFF) | 54.9 / 1 (OFF) | 74.0 / 2 (OFF) | 192.8 |

> Each cell uses one ORT mode for both values: the mode with the higher channel capacity,
> or, on a tie, the mode with the higher single-stream E2E FPS. Classification is not part of
> the multi-stream measurement and shows the higher single-stream E2E FPS of the two modes.
> Source: `pipeline_results.json` and `multi_stream_results.json` of each v2.5.0 run.

### 1.2 Key findings

1. **Heavy models (sizes l, x): inference throughput is the same on every host.**
   The NPU is the bottleneck, and the host's per-frame work finishes within the NPU's time
   per frame. → [§3](#3-inference-throughput)

2. **Inference throughput scales with the NPU module.**
   The H1-Quattro card (four M1 chips) reaches about 4× one M1. The M1M, a lower-tier module
   with slower and smaller memory, reaches 0.72–0.82×. → [§3](#3-inference-throughput)

3. **Light models (sizes n, s): the host, not the NPU, sets E2E FPS.**
   The NPU finishes a light-model frame in a few milliseconds, so decoding, pre-processing
   and post-processing on the host set the pace; at size n a single stream keeps the NPU less than
   half busy. → [§5.1](#51-results-by-task)

4. **A hardware video decoder is the first host requirement.**
   Without one, H.264 decoding competes for the CPU with the rest of the pipeline: the
   Raspberry Pi 5 fits 2 YOLO26-n detection channels, against 4–6 on hosts with a hardware
   decoder and the same M1. → [§6.1](#61-video-decoding)

5. **Heavy models: cooling decides sustained E2E FPS.**
   A hot NPU lowers its clock (thermal throttling), and E2E FPS falls with it — on the most
   thermally limited board to 57% of the inference throughput at size x. → [§6.4](#64-thermal-behavior-and-cooling)

6. **Choose the ORT mode per host, by measurement.**
   The two modes give the same output but compute the CPU part in different software, whose
   relative speed depends on the host CPU. → [§7](#7-choosing-the-ort-mode)

---

## 2. Choosing a Configuration

Recommended configurations are drawn from the six measured environments only; each
recommendation is backed by a measured result.

**Table 2. Recommended configuration by requirement (dx-all-suite v2.5.0, 1920×1080 30 fps
H.264, channel capacity at 30 fps per channel).**

| Requirement | Recommended configuration | Evidence |
|-------------|---------------------------|----------|
| 10 or more channels of detection, pose or segmentation | **H1-Quattro** on an x86 host | 17 / 20 / 11 channels at size n for detection / pose / segmentation; 16 detection channels at size m ([§5](#5-video-pipeline-e2e-fps-and-channel-capacity)) |
| 3–8 channels with light models (sizes n, s) | **M1** on a host with a hardware video decoder (Intel N97, RK3588) | 4–6 detection and 7–8 pose channels at size n ([§5](#5-video-pipeline-e2e-fps-and-channel-capacity)) |
| Heavy models (sizes l, x) | **M1** on any measured host, with adequate cooling | Inference throughput identical across hosts ([§3](#3-inference-throughput)); sustained E2E FPS drops only under thermal throttling ([§6.4](#64-thermal-behavior-and-cooling)) |
| 1–2 channels at the lowest system cost | **Raspberry Pi 5 + M1** | 2 detection channels from size n to l, 3 pose channels from size n to m; limited by software decoding ([§6.1](#61-video-decoding)) |
| Lower-tier NPU module | **M1M**, 0.72–0.82× the inference throughput of M1 and half its memory | `RPi5B_M1M`: 2 detection channels at sizes n and s, 1 at sizes m and l, none at size x ([§3](#3-inference-throughput), [§6.5](#65-memory)) |

**Host checklist.** What to check on a host, in order of measured impact:

1. **Hardware video decoder.** Software decoding runs on the same CPU as the rest of the
   pipeline, so it limits E2E FPS regardless of the NPU. On the Raspberry Pi 5 detection E2E
   FPS stays at ~80 fps from size n to l (2 channels), while hosts with a hardware decoder reach
   4–6 detection channels at size n ([§6.1](#61-video-decoding)).
2. **Cooling.** When the NPU reaches its thermal limit it lowers its clock below the nominal
   1000 MHz (thermal throttling), and E2E FPS falls with it. Under sustained load the clock
   dropped as low as 300 MHz, and on the most thermally limited board size-x E2E FPS
   fell to 57% of the inference throughput ([§6.4](#64-thermal-behavior-and-cooling)).
3. **CPU.** With ORT ON the CPU part of the model runs on the host for every frame, so for
   light models the CPU limits inference throughput: at size n it is 53–58% of the NPU-only figure
   on the ARM hosts and 75–76% on x86 ([§6.2](#62-host-cpu-and-the-cpu-part-of-the-model)).
4. **PCIe link width** (number of lanes: Gen3 ×1, Gen3 ×2, Gen3 ×4). A narrow link can limit light 640×640
   models: at size n the Raspberry Pi 5, whose PCIe connector has a single lane (Gen3 ×1), had 39–47% lower NPU-only inference throughput for detection and segmentation. On that host
   the CPU and software decoding limited first, so a link of two or more lanes (Gen3 ×2 or wider) is headroom rather than a
   measured gain ([§6.3](#63-pcie-link-width)).
5. **Host RAM.** Pipeline memory grows with every channel (median about 32 MiB per channel),
   so a many-channel system needs host RAM budgeted alongside the NPU ([§6.5](#65-memory)).

---

## 3. Inference Throughput

Inference throughput is the number of frames per second the **complete model (ORT ON)**
completes when the NPU is fed as fast as possible — no video decoding is involved. It is the
upper bound for any application on that host.

**Table 3. Inference throughput (FPS), complete model (ORT ON), dx-all-suite v2.5.0.** Inputs: 640×640
(detection, pose, segmentation), 1024×1024 (oriented bounding box), 224×224
(classification).

| Task | Environment | n | s | m | l | x |
|------|-------------|--:|--:|--:|--:|--:|
| Object detection | BIOSTAR_H1-Quattro | 1058.1 | 823.5 | 511.3 | 375.0 | 200.8 |
| Object detection | DX-AIPlayer-N97_M1 | 244.0 | 199.5 | 123.6 | 90.8 | 48.8 |
| Object detection | OrangePi5+_M1 | 178.3 | 179.9 | 123.1 | 90.3 | 48.8 |
| Object detection | ROCK5B+_M1 | 157.5 | 149.2 | 123.3 | 90.6 | 48.9 |
| Object detection | RPi5B_M1 | 104.2 | 104.7 | 104.7 | 90.8 | 48.9 |
| Object detection | RPi5B_M1M | 102.3 | 102.2 | 85.3 | 67.2 | 37.1 |
| Pose estimation | BIOSTAR_H1-Quattro | 1277.1 | 752.4 | 499.0 | 367.6 | 195.1 |
| Pose estimation | DX-AIPlayer-N97_M1 | 303.8 | 183.9 | 122.6 | 89.3 | 47.5 |
| Pose estimation | OrangePi5+_M1 | 284.4 | 184.6 | 122.2 | 88.7 | 47.6 |
| Pose estimation | ROCK5B+_M1 | 246.4 | 169.0 | 122.0 | 89.0 | 47.6 |
| Pose estimation | RPi5B_M1 | 151.8 | 150.8 | 122.5 | 89.2 | 47.6 |
| Pose estimation | RPi5B_M1M | 146.2 | 141.1 | 90.8 | 66.9 | 36.2 |
| Segmentation | BIOSTAR_H1-Quattro | 561.0 | 573.1 | 320.6 | 269.4 | 141.2 |
| Segmentation | DX-AIPlayer-N97_M1 | 138.1 | 134.7 | 77.1 | 64.9 | 34.3 |
| Segmentation | OrangePi5+_M1 | 131.3 | 132.8 | 77.3 | 64.4 | 34.1 |
| Segmentation | ROCK5B+_M1 | 104.6 | 99.8 | 76.3 | 64.7 | 34.4 |
| Segmentation | RPi5B_M1 | 67.5 | 68.3 | 67.7 | 64.9 | 34.4 |
| Segmentation | RPi5B_M1M | 65.9 | 66.0 | 57.2 | 48.6 | 27.2 |
| Oriented bounding box | BIOSTAR_H1-Quattro | 453.9 | 265.8 | 179.4 | 129.7 | 71.2 |
| Oriented bounding box | DX-AIPlayer-N97_M1 | 107.1 | 64.1 | 42.4 | 31.0 | 17.0 |
| Oriented bounding box | OrangePi5+_M1 | 106.3 | 63.8 | 42.5 | 30.9 | 17.0 |
| Oriented bounding box | ROCK5B+_M1 | 107.1 | 63.4 | 41.5 | 30.8 | 17.0 |
| Oriented bounding box | RPi5B_M1 | 107.2 | 62.7 | 42.5 | 31.0 | 17.0 |
| Oriented bounding box | RPi5B_M1M | 75.2 | 45.5 | 29.2 | 22.3 | 12.7 |
| Classification | BIOSTAR_H1-Quattro | 14280.3 | 7989.3 | 5657.2 | 3598.6 | 2017.2 |
| Classification | DX-AIPlayer-N97_M1 | 3512.5 | 1958.0 | 1381.8 | 888.2 | 496.5 |
| Classification | OrangePi5+_M1 | 3383.9 | 1912.8 | 1363.0 | 874.2 | 492.9 |
| Classification | ROCK5B+_M1 | 3483.0 | 1967.8 | 1379.9 | 886.0 | 496.4 |
| Classification | RPi5B_M1 | 3460.3 | 1896.1 | 1352.0 | 870.6 | 494.7 |
| Classification | RPi5B_M1M | 2877.2 | 1516.0 | 1057.7 | 712.0 | 384.8 |

> Source: `model_results.json`, family = throughput, ORT ON. Mean of three 30-second runs,
> each started from a cooled NPU.

**Table 4. Inference throughput by NPU module at sizes l and x, ORT ON, v2.5.0.**

| Task | Spread across the four M1 hosts (max. CV) | H1-Quattro ÷ M1 | M1M ÷ M1 (same Raspberry Pi 5 host type) |
|------|:-----------------------------------------:|:---------------:|:----------------------------------------:|
| Object detection | 0.2 % | 4.11–4.14× | 0.74–0.76× |
| Pose estimation | 0.2 % | 4.10–4.13× | 0.75–0.76× |
| Segmentation | 0.3 % | 4.12–4.16× | 0.75–0.79× |
| Oriented bounding box | 0.2 % | 4.18–4.20× | 0.72–0.75× |
| Classification | 0.8 % | 4.07–4.09× | 0.78–0.82× |
> CV = population standard deviation ÷ mean of the four single-M1 hosts, larger of sizes l and x.
> H1-Quattro is `BIOSTAR_H1-Quattro` divided by the mean of the four single-M1 hosts.
> M1M ÷ M1 is `RPi5B_M1M` divided by `RPi5B_M1`.

**What this means.**

- **From size l upwards the host does not matter.** The four single-M1 hosts agree within
  0.8% for every task. The NPU is the bottleneck: it is 90–96% busy, and the CPU part
  (1–6 ms per frame) finishes within the NPU's time per frame (11–59 ms). Most hosts are
  already NPU-bound at size m; the Raspberry Pi 5 is not for detection and segmentation (104.7
  against 123.1–123.6 fps for YOLO26-m detection).
- **At sizes n and s the host sets inference throughput.** The same M1 reaches 244.0 fps for YOLO26-n detection on the
  Intel N97 box but 104.2 fps on the Raspberry Pi 5, because the host executes the CPU part
  of the model for every frame ([§6.2](#62-host-cpu-and-the-cpu-part-of-the-model)). Read
  these columns for the specific host.
- **H1-Quattro scales inference throughput by four.** `dxrun` distributes inference across
  all four chips and reaches 4.07–4.20× the single-M1 mean.
- **M1M has slower and smaller memory, not a slower clock.** Both modules run at 1000 MHz; the M1M
  carries LPDDR4 (4200 Mbps, 1.92 GiB) against the M1's LPDDR5 (5600 Mbps, 3.92 GiB). The ratio
  also includes a difference between two Raspberry Pi 5 units ([§8.4](#84-limitations)).

---

## 4. Inference Latency

Inference latency is the time for **one** frame through the model, measured synchronously on
a single NPU core (`dxrun`, 300 loops). It reflects responsiveness, not inference throughput.

**Table 5. YOLO26 object detection inference latency (ms), complete model (ORT ON), v2.5.0.**

| Environment | n | s | m | l | x |
|-------------|--:|--:|--:|--:|--:|
| BIOSTAR_H1-Quattro | 10.89 | 16.99 | 24.19 | 31.52 | 57.26 |
| DX-AIPlayer-N97_M1 | 24.39 | 30.70 | 38.52 | 45.98 | 71.11 |
| OrangePi5+_M1 | 37.84 | 47.32 | 58.31 | 88.27 | 116.47 |
| ROCK5B+_M1 | 28.67 | 43.96 | 51.45 | 61.81 | 96.80 |
| RPi5B_M1 | 25.18 | 30.19 | 38.46 | 44.85 | 71.25 |
| RPi5B_M1M | 25.39 | 32.38 | 42.37 | 48.88 | 77.62 |

> Source: `total_ms` of `model_results.json`, family = latency, ORT ON. One 300-loop run per
> cell after a discarded warm-up run.

- **Inference latency depends on the host, unlike inference throughput.** With the same M1, YOLO26-n takes
  24.4 ms on the Intel N97 box and 25.2 ms on the Raspberry Pi 5, but 28.7–37.8 ms on the
  RK3588 boards. `BIOSTAR_H1-Quattro` is the fastest at every size.
- **The CPU part adds 0.31–1.36 ms on x86 and 2.31–5.79 ms on ARM** (object detection,
  sizes n, m and x). On the RK3588 boards latency also varies with the CPU core the process
  lands on ([§8.4](#84-limitations)).
- **Inference latency does not convert to inference throughput.** On the Intel N97 box
  YOLO26-n detection takes 24.4 ms, yet its inference throughput is 244.0 fps — far above
  1 ÷ 24.4 ms ≈ 41 fps — because several frames are in flight at once. Use
  [§3](#3-inference-throughput) and [§5](#5-video-pipeline-e2e-fps-and-channel-capacity) for
  sizing.

---

## 5. Video Pipeline: E2E FPS and Channel Capacity

### 5.1 Results by task

Each cell gives **single-stream E2E FPS / channel capacity at 30 fps per channel (ORT
mode)**. Both values come from the same mode: the mode with the higher channel capacity, or on
a tie the mode with the higher single-stream E2E FPS. Input: 1920×1080 30 fps H.264; dx-all-suite v2.5.0.

**Table 6. Object detection (640×640).**

| Environment | n | s | m | l | x |
|-------------|---|---|---|---|---|
| BIOSTAR_H1-Quattro | 493.6 / 17 (ON) | 492.9 / 17 (ON) | 491.7 / 16 (ON) | 376.8 / 12 (ON) | 201.1 / 6 (ON) |
| DX-AIPlayer-N97_M1 | 178.0 / 6 (OFF) | 165.1 / 5 (OFF) | 117.1 / 3 (ON) | 91.1 / 2 (OFF) | 49.0 / 1 (OFF) |
| OrangePi5+_M1 | 149.2 / 4 (ON) | 127.1 / 4 (ON) | 99.2 / 3 (ON) | 90.4 / 2 (OFF) | 48.8 / 1 (OFF) |
| ROCK5B+_M1 | 140.7 / 4 (ON) | 132.8 / 4 (ON) | 113.8 / 2 (ON) | 89.8 / 2 (ON) | 39.6 / 1 (ON) |
| RPi5B_M1 | 80.0 / 2 (OFF) | 80.2 / 2 (OFF) | 80.2 / 2 (OFF) | 80.4 / 2 (OFF) | 49.0 / 1 (OFF) |
| RPi5B_M1M | 79.5 / 2 (OFF) | 80.2 / 2 (OFF) | 75.4 / 1 (OFF) | 53.1 / 1 (OFF) | 21.8 / 0 (OFF) |

**Table 7. Pose estimation (640×640).**

| Environment | n | s | m | l | x |
|-------------|---|---|---|---|---|
| BIOSTAR_H1-Quattro | 554.6 / 20 (OFF) | 554.1 / 20 (OFF) | 501.9 / 16 (ON) | 366.7 / 12 (OFF) | 195.7 / 6 (OFF) |
| DX-AIPlayer-N97_M1 | 192.2 / 7 (OFF) | 179.1 / 5 (OFF) | 121.2 / 3 (OFF) | 89.4 / 2 (OFF) | 47.8 / 1 (ON) |
| OrangePi5+_M1 | 248.0 / 8 (OFF) | 174.6 / 5 (OFF) | 119.8 / 3 (OFF) | 89.4 / 2 (OFF) | 47.3 / 1 (OFF) |
| ROCK5B+_M1 | 227.5 / 8 (OFF) | 180.0 / 5 (OFF) | 121.2 / 2 (OFF) | 89.5 / 2 (OFF) | 39.1 / 1 (OFF) |
| RPi5B_M1 | 113.5 / 3 (OFF) | 113.8 / 3 (OFF) | 110.6 / 3 (OFF) | 89.3 / 2 (OFF) | 47.7 / 1 (OFF) |
| RPi5B_M1M | 112.0 / 3 (OFF) | 111.9 / 3 (OFF) | 70.7 / 1 (OFF) | 53.0 / 1 (OFF) | 20.3 / 0 (ON) |

**Table 8. Segmentation (640×640).**

| Environment | n | s | m | l | x |
|-------------|---|---|---|---|---|
| BIOSTAR_H1-Quattro | 359.1 / 11 (ON) | 361.2 / 11 (ON) | 316.9 / 8 (OFF) | 268.0 / 8 (ON) | 141.6 / 4 (ON) |
| DX-AIPlayer-N97_M1 | 106.5 / 3 (OFF) | 97.4 / 3 (OFF) | 76.3 / 1 (OFF) | 64.5 / 1 (OFF) | 30.5 / 1 (OFF) |
| OrangePi5+_M1 | 100.8 / 3 (ON) | 88.1 / 2 (ON) | 76.7 / 1 (OFF) | 63.5 / 1 (OFF) | 26.1 / 0 (OFF) |
| ROCK5B+_M1 | 87.9 / 2 (ON) | 81.0 / 2 (ON) | 65.5 / 1 (OFF) | 54.8 / 1 (OFF) | 19.6 / 0 (OFF) |
| RPi5B_M1 | 55.5 / 1 (OFF) | 55.1 / 1 (OFF) | 54.5 / 1 (OFF) | 53.4 / 1 (OFF) | 34.1 / 1 (OFF) |
| RPi5B_M1M | 54.9 / 1 (OFF) | 54.9 / 1 (OFF) | 34.1 / 1 (ON) | 28.2 / 0 (ON) | 13.6 / 0 (ON) |

**Table 9. Oriented bounding box (1024×1024).**

| Environment | n | s | m | l | x |
|-------------|---|---|---|---|---|
| BIOSTAR_H1-Quattro | 394.6 / 14 (ON) | 263.4 / 8 (ON) | 176.1 / 5 (ON) | 130.1 / 4 (OFF) | 71.2 / 2 (OFF) |
| DX-AIPlayer-N97_M1 | 105.3 / 3 (OFF) | 63.5 / 2 (OFF) | 42.3 / 1 (OFF) | 31.0 / 1 (OFF) | 14.6 / 0 (ON) |
| OrangePi5+_M1 | 104.7 / 3 (OFF) | 62.9 / 2 (OFF) | 41.8 / 1 (OFF) | 30.9 / 1 (OFF) | 14.4 / 0 (ON) |
| ROCK5B+_M1 | 105.4 / 3 (OFF) | 62.9 / 2 (ON) | 38.9 / 1 (ON) | 26.1 / 0 (ON) | 11.0 / 0 (ON) |
| RPi5B_M1 | 82.7 / 2 (OFF) | 63.0 / 2 (OFF) | 42.2 / 1 (OFF) | 31.1 / 1 (ON) | 16.9 / 0 (ON) |
| RPi5B_M1M | 74.0 / 2 (OFF) | 45.9 / 1 (OFF) | 22.1 / 0 (ON) | 14.5 / 0 (OFF) | 7.3 / 0 (ON) |

> Source for Tables 6–9: `pipeline_results.json` (single-stream E2E FPS) and
> `multi_stream_results.json` (channel capacity: largest stream count whose run completed with every
> stream at ≥ 30 fps) of each v2.5.0 run. E2E and multi-stream are sustained-load values
> ([§6.4](#64-thermal-behavior-and-cooling)).

**Reading the tables.**

- **Light models (sizes n, s): the host sets E2E FPS.** With one M1, detection channel capacity at
  size n ranges from 2 (Raspberry Pi 5, software decoding) to 6 (Intel N97). H1-Quattro reaches 17 —
  about three times the best single-M1 host, not four, because the single-stream pipeline
  uses only 21% of its NPU at size n (Table 10).
- **Larger models can be free up to a point.** Where the host limits the pipeline, a larger
  model costs no E2E FPS: detection E2E FPS stays the same from size n to m on `BIOSTAR_H1-Quattro`
  (493.6 → 491.7 fps) and from size n to l on `RPi5B_M1` (80.0 → 80.4 fps).
- **Heavy models (sizes l, x): the NPU and cooling set E2E FPS.** On single-M1 hosts, detection and pose
  E2E FPS converges on 89–91 at size l and 47–49 at size x, except where the NPU throttles
  ([§6.4](#64-thermal-behavior-and-cooling)) or software decoding still caps E2E FPS
  (`RPi5B_M1`, YOLO26-l detection: 80.4 fps).
- **Segmentation and oriented bounding box are the heaviest pipelines.** At size x only
  `BIOSTAR_H1-Quattro` sustains more than one channel, and no single-M1 host sustains one
  oriented-bounding-box stream at 30 fps at size x.

**Table 10. NPU utilization of the single-stream pipeline, YOLO26 object detection, same mode
as Table 6, v2.5.0.**

| Environment | n | s | m | l | x |
|-------------|--:|--:|--:|--:|--:|
| BIOSTAR_H1-Quattro | 21 % | 38 % | 67 % | 73 % | 84 % |
| DX-AIPlayer-N97_M1 | 42 % | 74 % | 87 % | 90 % | 94 % |
| OrangePi5+_M1 | 38 % | 58 % | 74 % | 90 % | 93 % |
| ROCK5B+_M1 | 36 % | 59 % | 82 % | 90 % | 94 % |
| RPi5B_M1 | 18 % | 34 % | 55 % | 80 % | 94 % |
| RPi5B_M1M | 22 % | 41 % | 83 % | 94 % | 95 % |

> Source: `npu_total_avg_pct` of `pipeline_results.json`, task = object_detection.

At size n the NPU is busy 18–42% of the time on every environment; the remaining NPU time is
unused because the host pipeline (decode → preprocess → post-process) cannot feed it from a
single stream.

### 5.2 Estimating channel capacity from single-stream E2E FPS

Channel capacity = ⌊aggregate E2E FPS at N streams ÷ 30⌋, and aggregate E2E FPS stays close
to single-stream E2E FPS — for YOLO26-n detection within −1% to +8% on every environment. A single-stream measurement therefore gives a good first estimate:
it is exact in 98 of 120 cells.

**Table 11. Measured channel capacity minus ⌊single-stream E2E FPS ÷ 30⌋, 120 cells (6 environments
× 4 video tasks × 5 sizes), same mode as Tables 6–9, v2.5.0.**

| Size | Equal | +1 | +2 | −1 | −2 |
|:----:|:-----:|:--:|:--:|:--:|:--:|
| n | 18 | 5 | 1 | 0 | 0 |
| s | 21 | 1 | 1 | 1 | 0 |
| m | 15 | 0 | 0 | 7 | 2 |
| l | 20 | 0 | 0 | 4 | 0 |
| x | 24 | 0 | 0 | 0 | 0 |

- **Sizes n and s: the estimate is conservative.** Several streams can overlap work that a single
  stream performs in sequence, so aggregate E2E FPS reaches up to 1.21× single-stream E2E FPS
  (`DX-AIPlayer-N97_M1`, YOLO26-n pose: 233.4 fps at 7 channels against 192.2 fps single-stream).
  Near a threshold, a 1% gain is enough for one more channel (`DX-AIPlayer-N97_M1`, YOLO26-n
  detection: 178.0 fps → 5.93, measured 6 channels).
- **Sizes m and l: the estimate is optimistic on boards that throttle.** All 13 cells below the
  estimate throttled to 300–600 MHz under multi-stream load; at the first failing stream count
  aggregate E2E FPS fell to 0.58–0.88× single-stream E2E FPS.
- **Size x: the estimate is exact.**

**Rule of thumb:** channel capacity ≈ ⌊single-stream E2E FPS ÷ 30⌋. For light models expect up to
1–2 more; for sizes m and l without cooling margin, plan for 1–2 fewer.

---

## 6. Host-Side Limiting Factors

A video application rarely reaches the inference throughput of [§3](#3-inference-throughput).
This section shows the host-side factors that decide how much of it turns into E2E FPS and
channel capacity. The host checklist in [§2](#2-choosing-a-configuration) summarises them in
order of impact.

### 6.1 Video decoding

**Table 12. Pipeline ceiling of each host: YOLO26-cls-n single-stream E2E FPS, 1920×1080
30 fps H.264, v2.5.0.** The classifier needs little NPU time (NPU 3–12% busy), so this E2E
FPS is set by decoding and pre-processing on the host.

| Environment | Video decoder | Pipeline ceiling (FPS) | Host CPU busy |
|-------------|---------------|-----------------------:|--------------:|
| OrangePi5+_M1 | mppvideodec (HW) | 1086.4 | 176 % of 800 % |
| ROCK5B+_M1 | mppvideodec (HW) | 972.9 | 150 % of 800 % |
| BIOSTAR_H1-Quattro | vaapidecodebin (HW) | 809.7 | 37 % of 1200 % |
| DX-AIPlayer-N97_M1 | vah264dec (HW) | 276.7 | 86 % of 400 % |
| RPi5B_M1M | avdec_h264 (SW) | 192.8 | 287 % of 400 % |
| RPi5B_M1 | avdec_h264 (SW) | 189.7 | 269 % of 400 % |

> Source: `avg_e2e_fps`, `decoder`, `avg_cpu_pct` and `npu_total_avg_pct` of
> `pipeline_results.json`, task = classification, size = n, higher of the two ORT modes.

- **Software decoding uses most of a Raspberry Pi 5.** At ~190 fps the decoder already
  occupies about 270–290% of the four cores. With a detection model the remaining CPU is
  shared with post-processing, and E2E FPS settles at **80.0–80.4 fps from size n to l** on
  `RPi5B_M1` — while its inference throughput is 104.2–104.7 fps from size n to m (Table 3). Two 30 fps detection channels fit; three do not.
- **Hardware decoders lift the ceiling** to 810–1086 fps on the RK3588 boards and the
  Ryzen host. The Intel N97 box is lower (277 fps) with its CPU mostly idle, so its hardware
  decoder sets that ceiling.

### 6.2 Host CPU and the CPU part of the model

YOLO26 models compiled for the NPU keep part of the graph on the host (the CPU part). It
runs on the host CPU for every frame — inside the inference call with ORT ON, in the
application's post-processing with ORT OFF. The ratio below shows how much inference
throughput this host work costs; NPU-only inference throughput (ORT OFF) serves here only as
the reference point.

**Table 13. Inference throughput ratio, complete model (ORT ON) ÷ NPU only (ORT OFF), YOLO26
object detection, v2.5.0.**

| Environment | n | s | m | l | x |
|-------------|--:|--:|--:|--:|--:|
| BIOSTAR_H1-Quattro | 0.76 | 1.00 | 1.00 | 1.00 | 1.00 |
| DX-AIPlayer-N97_M1 | 0.75 | 1.00 | 1.00 | 1.00 | 1.00 |
| OrangePi5+_M1 | 0.55 | 0.90 | 1.00 | 1.00 | 1.00 |
| ROCK5B+_M1 | 0.53 | 0.75 | 1.00 | 1.00 | 1.00 |
| RPi5B_M1 | 0.58 | 0.58 | 0.85 | 1.00 | 1.00 |
| RPi5B_M1M | 0.57 | 0.66 | 1.00 | 1.00 | 1.00 |

> Source: `model_results.json`, task = object_detection, family = throughput, ORT ON fps ÷
> ORT OFF fps.

- **At sizes m, l and x the CPU part costs no inference throughput** (ratio 1.00), except on
  `RPi5B_M1` at size m (0.85).
- **At size n the complete model reaches about half of the NPU-only inference throughput on ARM
  hosts** (0.53–0.58) and three quarters on x86 (0.75–0.76). Inference throughput is then
  nearly independent of model size — `RPi5B_M1` gives 104.2, 104.7 and 104.7 fps at sizes n, s and m — which
  points to a fixed per-frame host cost.
- **ORT OFF does not remove this cost; it moves it** into the application's
  post-processing, where it is measured as part of E2E FPS ([§7](#7-choosing-the-ort-mode)).

### 6.3 PCIe link width

PCIe link width is the number of lanes between the host and the NPU module: Gen3 ×1, Gen3 ×2 or Gen3 ×4. A
PCIe Gen3 lane carries about 1 GB/s in each direction, so a Gen3 ×1 link has a quarter of the
bandwidth of a Gen3 ×4 link. The measured hosts provide Gen3 ×1 (Raspberry Pi 5), Gen3 ×2 (Intel N97,
`ROCK5B+_M1`) and Gen3 ×4 (`OrangePi5+_M1`, `BIOSTAR_H1-Quattro`).

This section uses NPU-only inference throughput (ORT OFF) as a diagnostic: it is the only measurement
in which the link, rather than the host CPU, can become the limit. It is not a sizing figure.

**Table 14. NPU-only inference throughput (FPS) at size n by PCIe link, ORT OFF, v2.5.0.**

| Environment | Link | Object detection | Pose estimation | Segmentation | Oriented bounding box | Classification |
|-------------|:----:|-----------------:|----------------:|-------------:|----------------------:|---------------:|
| DX-AIPlayer-N97_M1 | Gen3 ×2 | 326.2 | 305.3 | 180.2 | 107.2 | 3521.3 |
| OrangePi5+_M1 | Gen3 ×4 | 324.2 | 305.7 | 164.8 | 107.1 | 3380.0 |
| ROCK5B+_M1 | Gen3 ×2 | 296.6 | 304.8 | 160.4 | 107.2 | 3471.3 |
| RPi5B_M1 | Gen3 ×1 | 179.5 | 264.3 | 95.8 | 106.9 | 3457.9 |

> Source: `model_results.json`, size = n, family = throughput, ORT OFF; link from
> `environment.json`.

The Raspberry Pi 5 (Gen3 ×1 link) reaches 39–47% lower NPU-only inference throughput for detection and
segmentation at size n than the hosts with Gen3 ×2 or Gen3 ×4 links, while its NPU is only 45% busy (detection). Oriented bounding box (1024×1024) and classification
(224×224) are unaffected, and from size m upwards all links agree (Table 4). The pattern is
consistent with a link limit for light 640×640 models; it was not isolated from host-CPU
effects, because no Gen3 ×1 and Gen3 ×4 link were compared on the same host.

**In practice the Gen3 ×1 link was not the limit on the Raspberry Pi 5.** With the complete model the
Raspberry Pi 5 reaches an inference throughput of 104.2 fps for YOLO26-n detection — below the
179.5 fps its link carried — and its E2E FPS is limited by software decoding ([§6.1](#61-video-decoding)). A wider
link is headroom for hosts whose CPU and decoder do not limit first; it was not a measured gain here.

### 6.4 Thermal behavior and cooling

When the NPU reaches its thermal limit, it lowers its clock below the nominal 1000 MHz to
protect itself. This is **thermal throttling**: inference throughput and E2E FPS fall with the
clock. A cell counts as throttled when the NPU clock fell below 1000 MHz at
any sample during the measurement; in the throttled cells the clock fell to 300–800 MHz. The benchmark
cools the NPU before each model-level measurement, so inference throughput (Table 3) is a
cooled value; the E2E and multi-stream phases then run continuously, as a deployed pipeline does.

**Table 15. E2E and multi-stream cells with a throttled NPU, and peak NPU temperature, v2.5.0
(all tasks, sizes and ORT modes).**

| Environment (v2.5.0) | E2E cells throttled | Multi-stream cells throttled | Max NPU temp |
|----------------------|:-------------------:|:----------------------------:|:------------:|
| BIOSTAR_H1-Quattro (active cooling) | 0 / 50 | 40 / 93 | 87 °C |
| DX-AIPlayer-N97_M1 (active cooling) | 4 / 50 | 35 / 82 | 86 °C |
| OrangePi5+_M1 | 8 / 50 | 36 / 76 | 86 °C |
| ROCK5B+_M1 | 21 / 50 | 53 / 77 | 88 °C |
| RPi5B_M1 | 1 / 50 | 7 / 78 | 81 °C |
| RPi5B_M1M | 10 / 50 | 19 / 66 | 96 °C |

> Source: `npu_throttled` and `npu_temp_max_c` of every row in `model_results.json`,
> `pipeline_results.json` and `multi_stream_results.json`. None of the 300 inference throughput cells
> throttled.

**Table 16. Sustained single-stream E2E FPS at size x as a share of the cooled inference
throughput (ORT ON), and lowest NPU clock in that E2E cell, v2.5.0.**

| Environment | Object detection | Pose estimation | Segmentation | Oriented bounding box |
|-------------|:----------------:|:---------------:|:------------:|:---------------------:|
| BIOSTAR_H1-Quattro | 100 % | 100 % | 100 % | 100 % |
| DX-AIPlayer-N97_M1 | 100 % | 100 % | 89 % (600 MHz) | 86 % (600 MHz) |
| OrangePi5+_M1 | 100 % | 99 % (800 MHz) | 77 % (400 MHz) | 85 % (600 MHz) |
| ROCK5B+_M1 | 81 % (600 MHz) | 82 % (600 MHz) | 57 % (400 MHz) | 65 % (400 MHz) |
| RPi5B_M1 | 100 % | 100 % | 99 % | 99 % |
| RPi5B_M1M | 59 % (300 MHz) | 56 % | 50 % | 58 % |

> E2E FPS of the mode used in [§5](#5-video-pipeline-e2e-fps-and-channel-capacity) ÷ Table 3. A
> clock is shown where the NPU throttled in the E2E cell.

- **Where the NPU holds 1000 MHz, E2E FPS of a heavy model equals its inference
  throughput** (99–100% on `BIOSTAR_H1-Quattro` and `RPi5B_M1`; `DX-AIPlayer-N97_M1` for
  detection and pose).
- **`ROCK5B+_M1` is the most thermally limited board** (21 of 50 E2E and 53 of 77
  multi-stream cells throttled). Thermal throttling lowered its NPU clock to 400–600 MHz in every YOLO26-x video task,
  so its YOLO26-x E2E FPS is 57–82% of the inference throughput — for detection 39.6 fps
  against 48.8–49.0 fps on the other single-M1 hosts.
- **Throttling also reduces channel capacity** at sizes m and l
  ([§5.2](#52-estimating-channel-capacity-from-single-stream-e2e-fps)).
- At size x, E2E FPS of `RPi5B_M1M` is only 50–59% of its inference throughput although only
  its detection cell throttled; the cause was not determined ([§8.4](#84-limitations)).

### 6.5 Memory

**Table 17. NPU memory occupied by one loaded model (MiB), dx-all-suite v2.5.0.**

| Task | n | s | m | l | x |
|------|--:|--:|--:|--:|--:|
| Object detection | 118 | 152 | 245 | 298 | 529 |
| Pose estimation | 120 | 158 | 257 | 310 | 523 |
| Segmentation | 140 | 178 | 273 | 326 | 561 |
| Oriented bounding box | 243 | 383 | 651 | 799 | 1330 |
| Classification | 5 | 10 | 15 | 20 | 49 |

> Source: `npu_model_mem_bytes` of the latency rows of `model_results.json` (identical on
> every environment).

- **NPU memory does not grow with the number of streams** — all streams share the loaded
  model. What limits co-residence is the number and size of *different* models: the M1
  provides 3.92 GiB, the M1M 1.92 GiB. A YOLO26-x oriented bounding box model alone occupies
  1.3 GiB, two thirds of an M1M.
- **Host memory grows with channels.** Across the v2.5.0 multi-stream runs, pipeline memory
  (RSS) at the highest passing channel count ranged from ≈243 MiB to ≈1599 MiB, and each
  additional channel added a median of about 32 MiB (90th percentile about 121 MiB). On the
  single-M1 boards it stayed below 0.75 GiB; only the four-chip server, with its high channel
  counts, needs host RAM budgeted alongside the NPU.

---

## 7. Choosing the ORT Mode

**Table 18. Better ORT mode for single-stream E2E FPS and its gain, sizes n and s, v2.5.0.**

| Environment | Object Detection | Pose Estimation | Segmentation | OBB | Classification |
|-------------|:----------------:|:---------------:|:------------:|:---:|:--------------:|
| BIOSTAR_H1-Quattro | **ON** (+10.2–10.4 %) | tie | **ON** (+12.6–14.7 %) | tie | tie |
| DX-AIPlayer-N97_M1 | **OFF** (+11.3–18.5 %) | OFF (+12.7–13.1 %) | **OFF** (+12.1–12.7 %) | tie | tie |
| OrangePi5+_M1 | **ON** (+29.2–57.0 %) | OFF (+12.5–22.3 %) | **ON** (+5.9–18.7 %) | OFF (+0.8–8.8 %) | tie |
| ROCK5B+_M1 | **ON** (+38.7–48.7 %) | OFF (+10.8–19.7 %) | **ON** (+5.6–11.2 %) | tie | tie |
| RPi5B_M1 | **OFF** (+17.0–17.6 %) | OFF (+36.2–36.8 %) | **OFF** (+21.3–22.2 %) | OFF (+0.8–17.5 %) | tie |
| RPi5B_M1M | **OFF** (+20.1–20.9 %) | OFF (+39.0–39.9 %) | **OFF** (+24.6–24.7 %) | OFF (+1.8–7.9 %) | tie |

> Source: `avg_e2e_fps` of `pipeline_results.json`, sizes n and s; gain = higher ÷ lower E2E FPS − 1.
> "tie": both sizes differ by less than 5%. Classification has no CPU part, so the two modes
> coincide.

- **Both modes deliver the same final output; they differ in where the CPU part runs.**
  With ORT OFF the CPU part is skipped inside the `dxinfer` element and DX-Stream's
  post-processing library computes the result from the raw tensors. Which
  mode gives the higher E2E FPS depends on the host. On `OrangePi5+_M1` (YOLO26-n detection) ORT ON
  gives 57% higher E2E FPS (149.2 against 95.0 fps) even though ORT OFF uses less CPU (212%
  against 247% of 800%); on the Raspberry Pi 5, where software decoding already occupies the
  CPU, ORT OFF gives 17–21% higher E2E FPS for detection.
- **From size m upwards the choice matters little** — the NPU is the bottleneck in both
  modes.
- **Functional requirement first:** an application that needs output identical to the
  source ONNX model must use ORT ON. Where both are possible, measure both on the target
  host — `./run.sh run` records them side by side.

---

## 8. Method and Limitations

### 8.1 Test environments

| Environment | Host CPU | Arch | RAM | DEEPX NPU | Chips | PCIe link | CPU governor | Video decoder |
|-------------|----------|:----:|----:|-----------|:-----:|:---------:|:------------:|---------------|
| **BIOSTAR_H1-Quattro** | AMD Ryzen 5 9600X (6-core) | x86_64 | 30.5 GB | H1-Quattro card | 4 | Gen3 ×4 | powersave | vaapidecodebin (HW) |
| **DX-AIPlayer-N97_M1** | Intel N97 (4-core) | x86_64 | 7.5 GB | M1 module | 1 | Gen3 ×2 | powersave | vah264dec (HW) |
| **OrangePi5+_M1** | Rockchip RK3588 (A76/A55) | aarch64 | 15.6 GB | M1 module | 1 | Gen3 ×4 | ondemand | mppvideodec (HW) |
| **ROCK5B+_M1** | Rockchip RK3588 (A76/A55) | aarch64 | 7.8 GB | M1 module | 1 | Gen3 ×2 | ondemand | mppvideodec (HW) |
| **RPi5B_M1** | Broadcom BCM2712 (Cortex-A76) | aarch64 | 7.9 GB | M1 module | 1 | Gen3 ×1 | ondemand | avdec_h264 (SW) |
| **RPi5B_M1M** | Broadcom BCM2712 (Cortex-A76) | aarch64 | 7.9 GB | **M1M** module | 1 | Gen3 ×1 | ondemand | avdec_h264 (SW) |

> Source: `host` and `npu` of each v2.5.0 `environment.json`; decoder from
> `pipeline_results.json`. All environments ran the same software stack: DX-RT v3.5.0, NPU
> firmware v2.7.6, DX-Stream 3.2.0, models compiled with DX-COM v2.5.0-rc.1. All NPU modules
> run at a nominal 1000 MHz.

### 8.2 Workload

- **Model inputs:** 640×640 for object detection, pose estimation and segmentation; 1024×1024 for
  oriented bounding box; 224×224 for classification.
- **Video:** two 1920×1080 30 fps H.264 clips — `od_benchmark_video.mp4` (3455 frames) for
  detection, pose, segmentation and classification, and `obb_benchmark_video.mp4`
  (2640 frames) for oriented bounding box.

### 8.3 Metrics and procedure

| Metric | How it is measured |
|--------|--------------------|
| Inference throughput | `dxrun`, asynchronous on all NPU cores, 30 s, mean of 3 runs. Each run starts after the NPU cools to min(idle + 10 °C, 55 °C). The buffer count is swept and the best value is reported. Measured in both ORT modes; reported as ORT ON, with ORT OFF used for diagnosis only. |
| Inference latency | `dxrun`, synchronous on one core, 300 loops, one run after a discarded warm-up. |
| E2E FPS | GStreamer pipeline (`gst-launch-1.0`), one stream, mean of 3 back-to-back runs after a warm-up. Starts from a cooled NPU; runs continuously. |
| Channel capacity | Multi-stream runs immediately after E2E (no cooldown), increasing the stream count until any stream falls below 30 fps. A count passes only if every run completed with every stream at ≥ 30 fps. |
| NPU utilization, clock, temperature | Sampled by `dxtop` during each measurement. A cell is *throttled* when the NPU clock fell below 1000 MHz. |

Protocol parameters are listed in [§9.2](#92-measurement-protocol--key-parameters).

### 8.4 Limitations

- **Sustained values.** E2E FPS and channel capacity include the thermal state reached
  under continuous load; a 24/7 deployment can run hotter than the benchmark. Inference
  throughput figures are cooled values and an upper bound for continuous duty.
- **One video format.** Only 1920×1080 H.264 was measured. H.265, other resolutions or
  object densities change decoding and post-processing load.
- **30 fps threshold.** Channel capacity assumes 30 fps per channel. Re-run with
  `--fps-threshold <fps>` for another service level.
- **RK3588 core placement.** The RK3588 boards mix fast (A76) and efficient (A55) cores and
  the benchmark does not pin processes. Single runs can land on either, so these two hosts
  show the widest run-to-run spread (up to 3.8% in inference throughput: `ROCK5B+_M1`,
  YOLO26-n segmentation). Small differences on these hosts, in single-run inference latency especially, should
  not be over-interpreted.
- **M1 and M1M on different units.** `RPi5B_M1M` was measured on a different Raspberry Pi 5
  (Debian 13, kernel 6.18) than `RPi5B_M1` (Debian 12, kernel 6.12). Never average M1 and M1M
  figures.
- **Buffer count.** Inference throughput is reported at the best buffer count found by
  `dxrun --max-throughput` (median 6 at sizes n and s, 5 at sizes m and l, 4 at size x). An application that
  keeps the default can fall short in a minority of cells, mostly at size n.
- **Causes not isolated.** At size x, E2E FPS of `RPi5B_M1M` is only 50–59% of its inference throughput
  although its NPU throttled only in the detection cell; the H1-Quattro scales slightly above
  4× one M1; the relative speed of the two ORT modes varies by host. The data shows these
  effects but does not pin down their cause.
- **Not measured:** model accuracy, power consumption, per-stage pipeline timing, and the
  effect of different cooling solutions.

---

## 9. Appendix

### 9.1 Reproducing the benchmark

Run from the `dx-benchmark/` directory; setup is described in the [`README.md`](../README.md).

```bash
./run.sh preflight                                   # check the environment
./run.sh dry-run                                     # preview the benchmark matrix
./run.sh run                                         # full suite (model-level + E2E + multi-stream)
./run.sh run --sizes n,s --task object_detection     # a subset
./run.sh run --resume results/<env>/<run_id> --retry-failed
python3 -m benchmark report results/<env>/<run_id>   # regenerate REPORT.md
python3 -m benchmark dashboard results               # rebuild the dashboard
```

### 9.2 Measurement protocol — key parameters

| Parameter | Value |
|-----------|-------|
| Protocol version | v2 (thermal mode: steady) |
| Throughput measurement duration | 30 seconds |
| Latency loop count | 300 loops (single-core, synchronous) |
| Throughput repetitions | 3, each preceded by a cooldown and a 2-second wake-up run |
| Buffer-count selection | `dxrun` auto-stop sweep (`dxrun --max-throughput`): 10-second probe, 3 repeats, 1% tolerance, `--cool-down-temp` before every repeat |
| End-to-end repetitions | 3 (back to back) |
| Warm-up runs | 1 (discarded) before latency and before end-to-end |
| Multi-stream per-channel threshold | 30 fps |
| Channel-capacity pass rule | status ok + all runs completed + per-channel FPS ≥ 30 |
| Thermal hot-start block | 60 °C (run rejected above this) |
| Cooldown points | start of each model × ORT cell; before every sweep repeat; before each measured inference throughput run; immediately before the E2E phase. None between E2E and multi-stream. |
| Cooldown target | min(settled idle + 10 °C, 55 °C) — 44–55 °C across the six environments |
| Video input | Two H.264 clips, 1920×1080, 30 fps ([§8.2](#82-workload)) |

> Source: `protocol` and `thermal` blocks of each run's `environment.json`.

### 9.3 Per-environment reports

| Environment | Report |
|-------------|--------|
| BIOSTAR_H1-Quattro | [`results/BIOSTAR_H1-Quattro/20261022_152931/REPORT.md`](../results/BIOSTAR_H1-Quattro/20261022_152931/REPORT.md) |
| DX-AIPlayer-N97_M1 | [`results/DX-AIPlayer-N97_M1/20261022_152931/REPORT.md`](../results/DX-AIPlayer-N97_M1/20261022_152931/REPORT.md) |
| OrangePi5+_M1 | [`results/OrangePi5+_M1/20261022_152933/REPORT.md`](../results/OrangePi5+_M1/20261022_152933/REPORT.md) |
| ROCK5B+_M1 | [`results/ROCK5B+_M1/20261022_062933/REPORT.md`](../results/ROCK5B+_M1/20261022_062933/REPORT.md) |
| RPi5B_M1 | [`results/RPi5B_M1/20261022_152932/REPORT.md`](../results/RPi5B_M1/20261022_152932/REPORT.md) |
| RPi5B_M1M | [`results/RPi5B_M1M/20261022_152931/REPORT.md`](../results/RPi5B_M1M/20261022_152931/REPORT.md) |

### 9.4 Glossary

| Term | Meaning |
|------|---------|
| **Coefficient of variation (CV)** | Population standard deviation ÷ mean, in percent |
| **Complete model (ORT ON)** | NPU part plus CPU part, the latter run on the host through ONNX Runtime; output identical to the source ONNX model |
| **CPU part** | The portion of a compiled model that the NPU does not execute |
| **NPU only (ORT OFF)** | The NPU part alone; returns raw NPU tensors that the application post-processes. At model level a diagnostic figure only |
| **NPU utilization** | Average NPU core utilization during a measurement, sampled by `dxtop` |
| **PCIe link width** | Number of PCIe lanes between host and NPU module (Gen3 ×1, Gen3 ×2, Gen3 ×4); a Gen3 lane carries about 1 GB/s per direction |
| **Throttling** | NPU clock reduction below 1000 MHz at high temperature |

---

*Generated from the measurement data committed by the `dx-benchmark` tool. Every value in
this document can be re-derived from the result files under `results/`.*

