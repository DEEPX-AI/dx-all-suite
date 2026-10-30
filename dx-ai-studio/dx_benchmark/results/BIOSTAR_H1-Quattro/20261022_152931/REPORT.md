# YOLO26 Benchmark Report

**Generated:** 2026-10-24 02:25:21 (UTC+09:00, local)

## Test Timing

| # | Type | Start | End | Duration |
|---|------|-------|-----|----------|
| 1 | run | 2026-10-22 15:29:31 | 2026-10-24 02:25:21 | 34h 55m 50s |

## Executive Summary

### Object Detection

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n_640x640.dxnn | ON | 10.89 | 1058.1 | 493.6 | 17 |
| yolo26-n_640x640.dxnn | OFF | 10.62 | 1385.2 | 447.0 | 14 |
| yolo26-s_640x640.dxnn | ON | 16.99 | 823.5 | 492.9 | 17 |
| yolo26-s_640x640.dxnn | OFF | 16.80 | 820.7 | 447.4 | 14 |
| yolo26-m_640x640.dxnn | ON | 24.19 | 511.3 | 491.7 | 16 |
| yolo26-m_640x640.dxnn | OFF | 23.83 | 511.0 | 448.7 | 14 |
| yolo26-l_640x640.dxnn | ON | 31.52 | 375.0 | 376.8 | 12 |
| yolo26-l_640x640.dxnn | OFF | 31.17 | 374.8 | 376.8 | 12 |
| yolo26-x_640x640.dxnn | ON | 57.26 | 200.8 | 201.1 | 6 |
| yolo26-x_640x640.dxnn | OFF | 56.88 | 200.8 | 201.0 | 6 |

### Pose Estimation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-pose_640x640.dxnn | ON | 10.52 | 1277.1 | 541.4 | 19 |
| yolo26-n-pose_640x640.dxnn | OFF | 10.35 | 1278.4 | 554.6 | 20 |
| yolo26-s-pose_640x640.dxnn | ON | 17.04 | 752.4 | 539.0 | 19 |
| yolo26-s-pose_640x640.dxnn | OFF | 16.72 | 754.3 | 554.1 | 20 |
| yolo26-m-pose_640x640.dxnn | ON | 23.99 | 499.0 | 501.9 | 16 |
| yolo26-m-pose_640x640.dxnn | OFF | 23.80 | 504.0 | 501.9 | 16 |
| yolo26-l-pose_640x640.dxnn | ON | 31.57 | 367.6 | 366.6 | 12 |
| yolo26-l-pose_640x640.dxnn | OFF | 31.37 | 367.8 | 366.7 | 12 |
| yolo26-x-pose_640x640.dxnn | ON | 57.87 | 195.1 | 195.6 | 6 |
| yolo26-x-pose_640x640.dxnn | OFF | 57.59 | 195.1 | 195.7 | 6 |

### Segmentation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-seg_640x640.dxnn | ON | 18.90 | 561.0 | 359.1 | 11 |
| yolo26-n-seg_640x640.dxnn | OFF | 18.52 | 583.9 | 319.0 | 9 |
| yolo26-s-seg_640x640.dxnn | ON | 26.84 | 573.1 | 361.2 | 11 |
| yolo26-s-seg_640x640.dxnn | OFF | 26.41 | 573.6 | 314.9 | 9 |
| yolo26-m-seg_640x640.dxnn | ON | 40.50 | 320.6 | 320.5 | 7 |
| yolo26-m-seg_640x640.dxnn | OFF | 40.10 | 318.3 | 316.9 | 8 |
| yolo26-l-seg_640x640.dxnn | ON | 47.47 | 269.4 | 268.0 | 8 |
| yolo26-l-seg_640x640.dxnn | OFF | 47.14 | 269.4 | 267.9 | 8 |
| yolo26-x-seg_640x640.dxnn | ON | 85.26 | 141.2 | 141.6 | 4 |
| yolo26-x-seg_640x640.dxnn | OFF | 84.78 | 141.1 | 141.6 | 4 |

### Oriented BBox (OBB)

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-obb_1024x1024.dxnn | ON | 23.51 | 453.9 | 394.6 | 14 |
| yolo26-n-obb_1024x1024.dxnn | OFF | 23.08 | 453.8 | 394.8 | 13 |
| yolo26-s-obb_1024x1024.dxnn | ON | 38.83 | 265.8 | 263.4 | 8 |
| yolo26-s-obb_1024x1024.dxnn | OFF | 38.29 | 265.7 | 263.2 | 8 |
| yolo26-m-obb_1024x1024.dxnn | ON | 56.40 | 179.4 | 176.1 | 5 |
| yolo26-m-obb_1024x1024.dxnn | OFF | 56.22 | 179.5 | 176.0 | 5 |
| yolo26-l-obb_1024x1024.dxnn | ON | 74.88 | 129.7 | 130.0 | 4 |
| yolo26-l-obb_1024x1024.dxnn | OFF | 74.55 | 129.7 | 130.1 | 4 |
| yolo26-x-obb_1024x1024.dxnn | ON | 142.53 | 71.2 | 71.2 | 2 |
| yolo26-x-obb_1024x1024.dxnn | OFF | 142.27 | 71.2 | 71.2 | 2 |

### Classification

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-cls-n_224x224.dxnn | ON | 1.01 | 14280.3 | 809.7 | — |
| yolo26-cls-n_224x224.dxnn | OFF | 0.98 | 14327.0 | 809.3 | — |
| yolo26-cls-s_224x224.dxnn | ON | 1.60 | 7989.3 | 807.9 | — |
| yolo26-cls-s_224x224.dxnn | OFF | 1.60 | 7985.5 | 808.5 | — |
| yolo26-cls-m_224x224.dxnn | ON | 2.20 | 5657.2 | 804.4 | — |
| yolo26-cls-m_224x224.dxnn | OFF | 2.20 | 5661.2 | 805.5 | — |
| yolo26-cls-l_224x224.dxnn | ON | 3.42 | 3598.6 | 800.4 | — |
| yolo26-cls-l_224x224.dxnn | OFF | 3.42 | 3597.3 | 798.8 | — |
| yolo26-cls-x_224x224.dxnn | ON | 5.91 | 2017.2 | 782.0 | — |
| yolo26-cls-x_224x224.dxnn | OFF | 5.92 | 2018.0 | 782.9 | — |

## Environment

| Item | Value |
|------|-------|
| Product | BIOSTAR |
| Hostname | deepx-B650MT |
| OS | Ubuntu 22.04.5 LTS |
| Kernel | 6.8.0-138-generic |
| CPU | AMD Ryzen 5 9600X 6-Core Processor |
| CPU Threads | 12 |
| CPU Governor | powersave |
| RAM | 30.5 GiB |
| NPU SKU | H1-Quattro |
| NPU Chip / Board | M1 · H1, Rev 0.0 |
| NPU Devices | 4 (H1-Quattro) |
| DX-AllSuite | v2.5.0 |
| DX-Stream | 3.2.0 |
| Benchmark Tool | 0.2.0 |
| Tool commit | 4e94aa9 |
| NPU RT | v3.5.0 |
| NPU RT (commit) | v3.5.0 (build: 5.502926e) |
| NPU Driver (RT) | v2.7.0 |
| NPU Driver (PCIe) | v2.7.0 |
| NPU Firmware | v2.7.6 (build: 4.90f4a6f) |
| NPU Memory (per device) | LPDDR5x 6000 Mbps, 3.92GiB |
| NPU Board | H1, Rev 0.0 |
| NPU PCIe | Gen3 X4 ×4 |

### Tools

| Tool | Available | Version |
|------|-----------|---------|
| run_model | Yes | DXRT v3.5.0 run_model |
| dxrt-cli | Yes | DXRT v3.5.0 (build: 5.502926e) |
| gst-launch-1.0 | Yes | gst-launch-1.0 version 1.20.3 |
| gst-inspect-1.0 | Yes | gst-inspect-1.0 version 1.20.3 |
| time | Yes | unknown |
| ffprobe | Yes | ffprobe version 4.4.2-0ubuntu0.22.04.1 Copyright (c) 2007-20... |
| dxtop | Yes | DX-TOP 1.1.0 |

## Benchmark Parameters

| Parameter | Value |
|-----------|-------|
| Throughput duration (-t) | 30 sec |
| Latency loops (-l) | 300 |
| Model warmup runs | 1 |
| Model latency runs | 1 |
| Model throughput runs | 3 |
| E2E pipeline runs | 3 |
| Multi-stream FPS threshold | 30.0 fps |
| ORT modes | ON, OFF |
| Benchmark families | all |

## Measurement Protocol

| Item | Value |
|------|-------|
| Version | v2 |
| Thermal Mode | steady |
| Throughput Time | 30 s |
| Latency Loops | 300 |
| Model Warmup | 1 |
| Throughput Wake-up | 2 s before each run |
| Model Latency Runs | 1 |
| Model Throughput Runs | 3 |
| E2E Runs | 3 |
| FPS Threshold | 30.0 |
| Multi-Stream Search | single-stream-estimate-linear-boundary |
| Stable Capacity Rule | status_ok_and_all_runs_success_and_avg_per_channel_fps_ge_threshold |
| NPU Idle Temp (settled) | 44.0 °C |
| Cool-down Target | ≤ 54.0 °C |
| Buffer-count Sweep | auto-stop |
| Sweep Probe | 10 s x 3 repeats |
| Sweep Tolerance | 1.0 % |
| Sweep Cool-down | dxrun --cool-down-temp, before every repeat |
| Cool-down Before Each Throughput Run | yes |
| Sweep Timeout | 7575 s |
| Cooldown Target ΔT | 10.0 °C |
| Cooldown Absolute Cap | 55.0 °C |
| Hot-Start Block | 60.0 °C |
| Cooldown Max Time | 1000.0 s |
| NPU Warmup | 1.0 s |
| NPU Drain | 0.5 s |

## Glossary

| Term | Meaning |
|------|---------|
| **ORT ON / OFF** | ONNX Runtime executes the model's CPU part on the host CPU. ON = NPU + CPU part; OFF = NPU part only, returning raw NPU output tensors. Classification has no CPU part. |
| **BC** | I/O buffer count (`--buffer-count`) recommended by the sweep (★): the smallest count whose throughput is within the sweep tolerance of the sweep's peak. |
| **Throughput** | Multi-core async `run_model` over the throughput duration, at the recommended BC. |
| **Latency** | Single-core sync. Total ms = profiler NPU task + CPU task per inference; it excludes host-side submit/wait overhead, so it is slightly below wall-clock latency. |
| **E2E FPS** | Frames/s of the full DX-Stream pipeline (decode, preprocess, inference, postprocess) into a fakesink. |
| **NPU Avg% / Max%** | NPU core utilization sampled by dxtop, averaged over all cores and devices. |
| **NPU MHz** | Min~max NPU core clock during the run; below 1000 MHz means the clock was lowered (thermal throttling). |
| **Max Channels** | Highest stream count where every run succeeded and per-channel FPS >= the FPS threshold. |

## Benchmarked Models

Model source: https://sdk.deepx.ai/modelzoo/q-lite-dxnn/2_5_0

| Model | Task | Input Size | NPU Memory (MiB) | ORT CPU Offload | Multi-Stream Sweep | Format | DX-COM | SHA256 |
|-------|------|------------|:----------------:|:---------------:|:------------------:|--------|--------|--------|
| yolo26-n_640x640.dxnn | Object Detection | 640×640 | 117.8 | Yes | ✅ | v9 | v2.5.0-rc.1+c6ae2e3 | 44d906adc564 |
| yolo26-s_640x640.dxnn | Object Detection | 640×640 | 151.9 | Yes | ✅ | v9 | v2.5.0-rc.1+c6ae2e3 | 9100636f0633 |
| yolo26-m_640x640.dxnn | Object Detection | 640×640 | 244.6 | Yes | ✅ | v9 | v2.5.0-rc.1+c6ae2e3 | 2cb24bd29a2b |
| yolo26-l_640x640.dxnn | Object Detection | 640×640 | 297.6 | Yes | ✅ | v9 | v2.5.0-rc.1+c6ae2e3 | 9ca9edb6efec |
| yolo26-x_640x640.dxnn | Object Detection | 640×640 | 528.7 | Yes | ✅ | v9 | v2.5.0-rc.1+c6ae2e3 | 4ffd65d004c9 |
| yolo26-n-pose_640x640.dxnn | Pose Estimation | 640×640 | 119.8 | Yes | ✅ | v9 | v2.5.0-rc.1+c6ae2e3 | 6bea052f3a83 |
| yolo26-s-pose_640x640.dxnn | Pose Estimation | 640×640 | 157.9 | Yes | ✅ | v9 | v2.5.0-rc.1+c6ae2e3 | d44de43bfa33 |
| yolo26-m-pose_640x640.dxnn | Pose Estimation | 640×640 | 256.6 | Yes | ✅ | v9 | v2.5.0-rc.1+c6ae2e3 | ce69468c956d |
| yolo26-l-pose_640x640.dxnn | Pose Estimation | 640×640 | 309.6 | Yes | ✅ | v9 | v2.5.0-rc.1+c6ae2e3 | 23074e93c4be |
| yolo26-x-pose_640x640.dxnn | Pose Estimation | 640×640 | 522.5 | Yes | ✅ | v9 | v2.5.0-rc.1+c6ae2e3 | c22452d91742 |
| yolo26-n-seg_640x640.dxnn | Segmentation | 640×640 | 140.2 | Yes | ✅ | v9 | v2.5.0-rc.1+c6ae2e3 | 98c1553f14cd |
| yolo26-s-seg_640x640.dxnn | Segmentation | 640×640 | 177.9 | Yes | ✅ | v9 | v2.5.0-rc.1+c6ae2e3 | 3c9847f6fa8d |
| yolo26-m-seg_640x640.dxnn | Segmentation | 640×640 | 272.8 | Yes | ✅ | v9 | v2.5.0-rc.1+c6ae2e3 | eac19b9f258a |
| yolo26-l-seg_640x640.dxnn | Segmentation | 640×640 | 325.8 | Yes | ✅ | v9 | v2.5.0-rc.1+c6ae2e3 | 88b5df7a8336 |
| yolo26-x-seg_640x640.dxnn | Segmentation | 640×640 | 561.0 | Yes | ✅ | v9 | v2.5.0-rc.1+c6ae2e3 | 2a3f3e11e61f |
| yolo26-n-obb_1024x1024.dxnn | Oriented BBox (OBB) | 1024×1024 | 243.5 | Yes | ✅ | v9 | v2.5.0-rc.1+c6ae2e3 | 85aaaa0d354b |
| yolo26-s-obb_1024x1024.dxnn | Oriented BBox (OBB) | 1024×1024 | 383.3 | Yes | ✅ | v9 | v2.5.0-rc.1+c6ae2e3 | c5558f063e2a |
| yolo26-m-obb_1024x1024.dxnn | Oriented BBox (OBB) | 1024×1024 | 651.2 | Yes | ✅ | v9 | v2.5.0-rc.1+c6ae2e3 | cb788b7a0538 |
| yolo26-l-obb_1024x1024.dxnn | Oriented BBox (OBB) | 1024×1024 | 799.0 | Yes | ✅ | v9 | v2.5.0-rc.1+c6ae2e3 | a027ceef2b7e |
| yolo26-x-obb_1024x1024.dxnn | Oriented BBox (OBB) | 1024×1024 | 1329.8 | Yes | ✅ | v9 | v2.5.0-rc.1+c6ae2e3 | 975672b1454a |
| yolo26-cls-n_224x224.dxnn | Classification | 224×224 | 4.9 | No | — | v9 | v2.5.0-rc.1+c6ae2e3 | 2c0dd4a6f59d |
| yolo26-cls-s_224x224.dxnn | Classification | 224×224 | 9.7 | No | — | v9 | v2.5.0-rc.1+c6ae2e3 | f23cc153cc56 |
| yolo26-cls-m_224x224.dxnn | Classification | 224×224 | 14.9 | No | — | v9 | v2.5.0-rc.1+c6ae2e3 | 84461e2c046f |
| yolo26-cls-l_224x224.dxnn | Classification | 224×224 | 19.9 | No | — | v9 | v2.5.0-rc.1+c6ae2e3 | e437b91249e8 |
| yolo26-cls-x_224x224.dxnn | Classification | 224×224 | 49.2 | No | — | v9 | v2.5.0-rc.1+c6ae2e3 | 0a95422e4f95 |

## Input Videos

### Object Detection / Pose / Segmentation

| Item | Value |
|------|-------|
| File | od_benchmark_video.mp4 |
| Resolution | 1920 x 1080 |
| Codec | h264 |
| FPS | 30.0 |
| Frames | 3455 |
| Duration | 115.3 sec |
| Bitrate | 4.47 Mbps |
| Format | QuickTime / MOV |
| Pixel Format | yuv420p |

### Oriented BBox (OBB)

| Item | Value |
|------|-------|
| File | obb_benchmark_video.mp4 |
| Resolution | 1920 x 1080 |
| Codec | h264 |
| FPS | 30.0 |
| Frames | 2640 |
| Duration | 88.0 sec |
| Bitrate | 4.87 Mbps |
| Format | QuickTime / MOV |
| Pixel Format | yuv420p |

### Classification

| Item | Value |
|------|-------|
| File | od_benchmark_video.mp4 |
| Resolution | 1920 x 1080 |
| Codec | h264 |
| FPS | 30.0 |
| Frames | 3455 |
| Duration | 115.3 sec |
| Bitrate | 4.47 Mbps |
| Format | QuickTime / MOV |
| Pixel Format | yuv420p |

## Model-Level Benchmarks

### Throughput (Multi-Core, Async)

> **Buffer-count sweep (★)** — the _Buffer-count sweep_ tables below list throughput fps per `--buffer-count`, averaged over repeated probes (fps rounded to 1 decimal). ★ marks dxrun's recommendation: the smallest buffer-count whose throughput is within the sweep tolerance of the sweep's peak. The sweep stops by itself once the curve flattens, so only the counts up to that point appear. The goal is the throughput ceiling — the recommended value itself is secondary, since buffer-counts inside the tolerance deliver effectively equal throughput.

#### Object Detection

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n_640x640.dxnn | 1058.1 ±3.0 | 4 | 287 | 71.6 | 80.4 | 53~55 | 1000 | ok |
| yolo26-s_640x640.dxnn | 823.5 ±0.1 | 5 | 199 | 95.0 | 100.0 | 57 | 1000 | ok |
| yolo26-m_640x640.dxnn | 511.3 ±0.2 | 4 | 116 | 95.4 | 100.0 | 58~59 | 1000 | ok |
| yolo26-l_640x640.dxnn | 375.0 ±0.0 | 4 | 84 | 94.1 | 100.0 | 58~59 | 1000 | ok |
| yolo26-x_640x640.dxnn | 200.8 ±0.0 | 4 | 44 | 93.1 | 100.0 | 58~59 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n_640x640.dxnn | 4 | [3]:881.4 · **[4]:1070.2 ★** · [5]:1058.9 · [6]:1070.5 · [7]:1060.3 |
| yolo26-s_640x640.dxnn | 5 | [3]:612.9 · [4]:798.0 · **[5]:822.5 ★** · [6]:822.4 · [7]:822.5 · [8]:822.4 |
| yolo26-m_640x640.dxnn | 4 | [3]:424.9 · **[4]:510.3 ★** · [5]:510.7 · [6]:510.7 · [7]:510.8 |
| yolo26-l_640x640.dxnn | 4 | [3]:320.5 · **[4]:374.2 ★** · [5]:374.5 · [6]:374.6 · [7]:374.7 |
| yolo26-x_640x640.dxnn | 4 | [3]:181.9 · **[4]:200.2 ★** · [5]:200.4 · [6]:200.6 · [7]:200.4 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n_640x640.dxnn | 1385.2 ±0.5 | 5 | 248 | 94.2 | 100.0 | 56~57 | 1000 | ok |
| yolo26-s_640x640.dxnn | 820.7 ±0.3 | 4 | 135 | 96.7 | 100.0 | 57 | 1000 | ok |
| yolo26-m_640x640.dxnn | 511.0 ±0.1 | 4 | 81 | 95.8 | 100.0 | 58~59 | 1000 | ok |
| yolo26-l_640x640.dxnn | 374.8 ±0.3 | 4 | 55 | 94.7 | 100.0 | 58~59 | 1000 | ok |
| yolo26-x_640x640.dxnn | 200.8 ±0.1 | 4 | 30 | 94.7 | 100.0 | 58~59 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n_640x640.dxnn | 5 | [3]:924.2 · [4]:1178.7 · **[5]:1383.6 ★** · [6]:1389.0 · [7]:1387.9 · [8]:1390.0 |
| yolo26-s_640x640.dxnn | 4 | [3]:616.6 · **[4]:819.0 ★** · [5]:821.9 · [6]:821.6 · [7]:821.7 |
| yolo26-m_640x640.dxnn | 4 | [3]:415.5 · **[4]:510.4 ★** · [5]:511.0 · [6]:511.2 · [7]:511.0 |
| yolo26-l_640x640.dxnn | 4 | [3]:313.5 · **[4]:374.3 ★** · [5]:374.7 · [6]:374.7 · [7]:374.8 |
| yolo26-x_640x640.dxnn | 4 | [3]:172.6 · **[4]:200.3 ★** · [5]:200.4 · [6]:200.6 · [7]:200.3 |


#### Pose Estimation

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 1277.1 ±0.0 | 5 | 221 | 97.3 | 100.0 | 57 | 1000 | ok |
| yolo26-s-pose_640x640.dxnn | 752.4 ±0.0 | 4 | 122 | 94.7 | 100.0 | 57 | 1000 | ok |
| yolo26-m-pose_640x640.dxnn | 499.0 ±5.3 | 4 | 81 | 94.3 | 100.0 | 58~59 | 1000 | ok |
| yolo26-l-pose_640x640.dxnn | 367.6 ±0.1 | 4 | 56 | 93.9 | 100.0 | 58~59 | 1000 | ok |
| yolo26-x-pose_640x640.dxnn | 195.1 ±0.0 | 4 | 31 | 92.8 | 100.0 | 59 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-pose_640x640.dxnn | 5 | [3]:933.5 · [4]:1211.3 · **[5]:1275.9 ★** · [6]:1276.2 · [7]:1276.4 · [8]:1276.8 |
| yolo26-s-pose_640x640.dxnn | 4 | [3]:624.5 · **[4]:751.7 ★** · [5]:752.3 · [6]:752.9 · [7]:752.9 |
| yolo26-m-pose_640x640.dxnn | 4 | [3]:441.0 · **[4]:502.9 ★** · [5]:503.2 · [6]:503.9 · [7]:503.8 |
| yolo26-l-pose_640x640.dxnn | 4 | [3]:320.9 · **[4]:366.9 ★** · [5]:367.1 · [6]:367.1 · [7]:367.3 |
| yolo26-x-pose_640x640.dxnn | 4 | [3]:174.7 · **[4]:194.6 ★** · [5]:194.7 · [6]:194.6 · [7]:194.7 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 1278.4 ±0.1 | 5 | 136 | 95.0 | 100.0 | 57 | 1000 | ok |
| yolo26-s-pose_640x640.dxnn | 754.3 ±0.2 | 4 | 76 | 94.9 | 100.0 | 57~58 | 1000 | ok |
| yolo26-m-pose_640x640.dxnn | 504.0 ±1.0 | 4 | 51 | 95.2 | 100.0 | 58~59 | 1000 | ok |
| yolo26-l-pose_640x640.dxnn | 367.8 ±0.0 | 4 | 36 | 94.9 | 100.0 | 58~59 | 1000 | ok |
| yolo26-x-pose_640x640.dxnn | 195.1 ±0.1 | 4 | 21 | 93.2 | 100.0 | 59 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-pose_640x640.dxnn | 5 | [3]:944.4 · [4]:1264.2 · **[5]:1277.7 ★** · [6]:1277.7 · [7]:1277.8 · [8]:1278.3 |
| yolo26-s-pose_640x640.dxnn | 4 | [3]:608.0 · **[4]:753.7 ★** · [5]:753.9 · [6]:754.1 · [7]:754.3 |
| yolo26-m-pose_640x640.dxnn | 4 | [3]:416.1 · **[4]:503.9 ★** · [5]:503.7 · [6]:504.5 · [7]:503.6 |
| yolo26-l-pose_640x640.dxnn | 4 | [3]:302.8 · **[4]:367.1 ★** · [5]:367.4 · [6]:367.5 · [7]:367.5 |
| yolo26-x-pose_640x640.dxnn | 4 | [3]:166.8 · **[4]:194.7 ★** · [5]:194.7 · [6]:194.8 · [7]:194.8 |


#### Segmentation

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 561.0 ±5.8 | 4 | 487 | 43.9 | 71.7 | 55~56 | 1000 | ok |
| yolo26-s-seg_640x640.dxnn | 573.1 ±0.5 | 6 | 488 | 95.8 | 100.0 | 57~58 | 1000 | ok |
| yolo26-m-seg_640x640.dxnn | 320.6 ±2.6 | 5 | 243 | 94.6 | 100.0 | 59~60 | 1000 | ok |
| yolo26-l-seg_640x640.dxnn | 269.4 ±0.2 | 5 | 199 | 95.2 | 100.0 | 59~60 | 1000 | ok |
| yolo26-x-seg_640x640.dxnn | 141.2 ±0.2 | 4 | 103 | 92.8 | 100.0 | 59~60 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-seg_640x640.dxnn | 4 | [3]:519.2 · **[4]:564.0 ★** · [5]:567.0 · [6]:568.0 · [7]:565.6 |
| yolo26-s-seg_640x640.dxnn | 6 | [3]:392.2 · [4]:493.8 · [5]:558.3 · **[6]:574.3 ★** · [7]:574.7 · [8]:575.2 · [9]:574.5 |
| yolo26-m-seg_640x640.dxnn | 5 | [3]:259.1 · [4]:315.2 · **[5]:322.4 ★** · [6]:318.4 · [7]:318.4 · [8]:318.5 |
| yolo26-l-seg_640x640.dxnn | 5 | [3]:222.7 · [4]:265.1 · **[5]:268.6 ★** · [6]:268.7 · [7]:268.7 · [8]:269.0 |
| yolo26-x-seg_640x640.dxnn | 4 | [3]:126.7 · **[4]:140.6 ★** · [5]:140.9 · [6]:140.9 · [7]:140.9 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 583.9 ±5.6 | 5 | 413 | 47.4 | 72.9 | 56 | 1000 | ok |
| yolo26-s-seg_640x640.dxnn | 573.6 ±0.2 | 5 | 382 | 93.6 | 100.0 | 57~58 | 1000 | ok |
| yolo26-m-seg_640x640.dxnn | 318.3 ±0.0 | 4 | 201 | 92.8 | 100.0 | 59~60 | 1000 | ok |
| yolo26-l-seg_640x640.dxnn | 269.4 ±0.1 | 5 | 168 | 92.7 | 100.0 | 59~60 | 1000 | ok |
| yolo26-x-seg_640x640.dxnn | 141.1 ±0.2 | 4 | 87 | 93.5 | 100.0 | 59~60 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-seg_640x640.dxnn | 5 | [3]:559.8 · [4]:588.3 · **[5]:593.6 ★** · [6]:593.5 · [7]:595.0 · [8]:593.3 · [9]:594.2 · [10]:585.9 |
| yolo26-s-seg_640x640.dxnn | 5 | [3]:411.5 · [4]:516.9 · **[5]:573.6 ★** · [6]:575.1 · [7]:578.4 · [8]:575.0 |
| yolo26-m-seg_640x640.dxnn | 4 | [3]:267.8 · **[4]:317.7 ★** · [5]:320.1 · [6]:318.6 · [7]:318.5 |
| yolo26-l-seg_640x640.dxnn | 5 | [3]:228.0 · [4]:266.0 · **[5]:268.2 ★** · [6]:268.6 · [7]:268.9 · [8]:268.7 · [9]:268.8 · [10]:268.7 |
| yolo26-x-seg_640x640.dxnn | 4 | [3]:127.7 · **[4]:140.7 ★** · [5]:140.9 · [6]:141.1 · [7]:140.8 |


#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 453.9 ±0.2 | 4 | 81 | 94.2 | 100.0 | 57 | 1000 | ok |
| yolo26-s-obb_1024x1024.dxnn | 265.8 ±0.2 | 4 | 46 | 95.5 | 100.0 | 57~58 | 1000 | ok |
| yolo26-m-obb_1024x1024.dxnn | 179.4 ±0.0 | 4 | 30 | 93.4 | 100.0 | 58 | 1000 | ok |
| yolo26-l-obb_1024x1024.dxnn | 129.7 ±0.0 | 4 | 24 | 93.3 | 100.0 | 58 | 1000 | ok |
| yolo26-x-obb_1024x1024.dxnn | 71.2 ±0.1 | 4 | 15 | 93.8 | 100.0 | 58~59 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-obb_1024x1024.dxnn | 4 | [3]:363.5 · **[4]:453.1 ★** · [5]:453.6 · [6]:453.7 · [7]:453.6 |
| yolo26-s-obb_1024x1024.dxnn | 4 | [3]:225.6 · **[4]:265.2 ★** · [5]:265.7 · [6]:265.8 · [7]:265.7 |
| yolo26-m-obb_1024x1024.dxnn | 4 | [3]:150.4 · **[4]:178.7 ★** · [5]:178.7 · [6]:178.8 · [7]:178.8 |
| yolo26-l-obb_1024x1024.dxnn | 4 | [3]:109.5 · **[4]:129.2 ★** · [5]:129.3 · [6]:129.3 · [7]:129.3 |
| yolo26-x-obb_1024x1024.dxnn | 4 | [3]:60.4 · **[4]:70.5 ★** · [5]:70.7 · [6]:70.8 · [7]:70.7 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 453.8 ±0.1 | 4 | 54 | 97.5 | 100.0 | 57 | 1000 | ok |
| yolo26-s-obb_1024x1024.dxnn | 265.7 ±0.1 | 4 | 32 | 95.8 | 100.0 | 57~58 | 1000 | ok |
| yolo26-m-obb_1024x1024.dxnn | 179.5 ±0.0 | 4 | 20 | 94.9 | 100.0 | 58~59 | 1000 | ok |
| yolo26-l-obb_1024x1024.dxnn | 129.7 ±0.0 | 4 | 16 | 94.5 | 100.0 | 58~59 | 1000 | ok |
| yolo26-x-obb_1024x1024.dxnn | 71.2 ±0.0 | 5 | 10 | 93.8 | 100.0 | 59 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-obb_1024x1024.dxnn | 4 | [3]:346.8 · **[4]:452.8 ★** · [5]:453.4 · [6]:453.5 · [7]:453.5 |
| yolo26-s-obb_1024x1024.dxnn | 4 | [3]:211.9 · **[4]:264.9 ★** · [5]:265.5 · [6]:265.4 · [7]:265.5 |
| yolo26-m-obb_1024x1024.dxnn | 4 | [3]:143.9 · **[4]:178.7 ★** · [5]:179.1 · [6]:178.9 · [7]:178.9 |
| yolo26-l-obb_1024x1024.dxnn | 4 | [3]:105.4 · **[4]:129.1 ★** · [5]:129.3 · [6]:129.3 · [7]:129.3 |
| yolo26-x-obb_1024x1024.dxnn | 5 | [3]:56.2 · [4]:69.6 · **[5]:70.7 ★** · [6]:70.7 · [7]:70.8 · [8]:70.8 |


#### Classification

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-cls-n_224x224.dxnn | 14280.3 ±58.8 | 6 | 57 | 92.6 | 96.0 | 56 | 1000 | ok |
| yolo26-cls-s_224x224.dxnn | 7989.3 ±2.6 | 5 | 32 | 93.7 | 98.0 | 56~57 | 1000 | ok |
| yolo26-cls-m_224x224.dxnn | 5657.2 ±3.1 | 4 | 22 | 95.6 | 98.6 | 58 | 1000 | ok |
| yolo26-cls-l_224x224.dxnn | 3598.6 ±1.2 | 4 | 14 | 96.6 | 99.2 | 57~58 | 1000 | ok |
| yolo26-cls-x_224x224.dxnn | 2017.2 ±0.8 | 4 | 8 | 95.4 | 99.9 | 57~58 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-cls-n_224x224.dxnn | 6 | [3]:9704.8 · [4]:13669.5 · [5]:14047.6 · **[6]:14324.5 ★** · [7]:14335.6 · [8]:14339.7 · [9]:14369.5 |
| yolo26-cls-s_224x224.dxnn | 5 | [3]:5854.4 · [4]:7877.2 · **[5]:7985.4 ★** · [6]:8002.5 · [7]:8015.5 · [8]:8019.8 |
| yolo26-cls-m_224x224.dxnn | 4 | [3]:4203.2 · **[4]:5658.8 ★** · [5]:5659.9 · [6]:5651.5 · [7]:5661.1 |
| yolo26-cls-l_224x224.dxnn | 4 | [3]:2720.8 · **[4]:3594.6 ★** · [5]:3594.2 · [6]:3592.8 · [7]:3589.3 |
| yolo26-cls-x_224x224.dxnn | 4 | [3]:1512.6 · **[4]:2017.2 ★** · [5]:2017.8 · [6]:2017.4 · [7]:2017.8 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-cls-n_224x224.dxnn | 14327.0 ±84.6 | 6 | 58 | 92.0 | 96.2 | 56 | 1000 | ok |
| yolo26-cls-s_224x224.dxnn | 7985.5 ±1.1 | 5 | 32 | 94.0 | 98.0 | 56 | 1000 | ok |
| yolo26-cls-m_224x224.dxnn | 5661.2 ±2.1 | 4 | 22 | 94.1 | 98.6 | 57~58 | 1000 | ok |
| yolo26-cls-l_224x224.dxnn | 3597.3 ±3.2 | 4 | 14 | 95.7 | 99.3 | 57 | 1000 | ok |
| yolo26-cls-x_224x224.dxnn | 2018.0 ±0.9 | 4 | 8 | 94.0 | 99.9 | 58 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-cls-n_224x224.dxnn | 6 | [3]:9675.0 · [4]:13652.5 · [5]:14034.6 · **[6]:14277.7 ★** · [7]:14317.5 · [8]:14288.9 · [9]:14351.9 |
| yolo26-cls-s_224x224.dxnn | 5 | [3]:5924.2 · [4]:7896.0 · **[5]:7994.1 ★** · [6]:8016.4 · [7]:8023.9 · [8]:8027.8 |
| yolo26-cls-m_224x224.dxnn | 4 | [3]:4178.4 · **[4]:5659.0 ★** · [5]:5658.0 · [6]:5658.2 · [7]:5655.4 |
| yolo26-cls-l_224x224.dxnn | 4 | [3]:2730.1 · **[4]:3591.1 ★** · [5]:3593.5 · [6]:3589.2 · [7]:3590.5 |
| yolo26-cls-x_224x224.dxnn | 4 | [3]:1500.1 · **[4]:2016.4 ★** · [5]:2016.9 · [6]:2016.8 · [7]:2016.8 |


### Latency (Single-Core, Sync)

#### Object Detection

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_640x640.dxnn | 91.8 | 10.89 | 10.58 | 0.31 | 44 | ok |
| yolo26-s_640x640.dxnn | 58.8 | 16.99 | 16.68 | 0.31 | 55 | ok |
| yolo26-m_640x640.dxnn | 41.3 | 24.19 | 23.87 | 0.32 | 55 | ok |
| yolo26-l_640x640.dxnn | 31.7 | 31.52 | 31.18 | 0.34 | 54 | ok |
| yolo26-x_640x640.dxnn | 17.5 | 57.26 | 56.92 | 0.35 | 55 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_640x640.dxnn | 94.2 | 10.62 | 10.62 | N/A | 55 | ok |
| yolo26-s_640x640.dxnn | 59.5 | 16.80 | 16.80 | N/A | 55 | ok |
| yolo26-m_640x640.dxnn | 42.0 | 23.83 | 23.83 | N/A | 55 | ok |
| yolo26-l_640x640.dxnn | 32.1 | 31.17 | 31.17 | N/A | 55 | ok |
| yolo26-x_640x640.dxnn | 17.6 | 56.88 | 56.88 | N/A | 55 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-pose_640x640.dxnn | 95.1 | 10.52 | 10.29 | 0.22 | 55 | ok |
| yolo26-s-pose_640x640.dxnn | 58.7 | 17.04 | 16.77 | 0.28 | 55 | ok |
| yolo26-m-pose_640x640.dxnn | 41.7 | 23.99 | 23.71 | 0.28 | 55 | ok |
| yolo26-l-pose_640x640.dxnn | 31.7 | 31.57 | 31.27 | 0.30 | 55 | ok |
| yolo26-x-pose_640x640.dxnn | 17.3 | 57.87 | 57.57 | 0.31 | 54 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-pose_640x640.dxnn | 96.6 | 10.35 | 10.35 | N/A | 55 | ok |
| yolo26-s-pose_640x640.dxnn | 59.8 | 16.72 | 16.72 | N/A | 55 | ok |
| yolo26-m-pose_640x640.dxnn | 42.0 | 23.80 | 23.80 | N/A | 55 | ok |
| yolo26-l-pose_640x640.dxnn | 31.9 | 31.37 | 31.37 | N/A | 54 | ok |
| yolo26-x-pose_640x640.dxnn | 17.4 | 57.59 | 57.59 | N/A | 54 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-seg_640x640.dxnn | 52.9 | 18.90 | 18.50 | 0.40 | 55 | ok |
| yolo26-s-seg_640x640.dxnn | 37.3 | 26.84 | 26.44 | 0.40 | 55 | ok |
| yolo26-m-seg_640x640.dxnn | 24.7 | 40.50 | 40.08 | 0.42 | 55 | ok |
| yolo26-l-seg_640x640.dxnn | 21.1 | 47.47 | 47.07 | 0.41 | 55 | ok |
| yolo26-x-seg_640x640.dxnn | 11.7 | 85.26 | 84.84 | 0.42 | 54 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-seg_640x640.dxnn | 54.0 | 18.52 | 18.52 | N/A | 55 | ok |
| yolo26-s-seg_640x640.dxnn | 37.9 | 26.41 | 26.41 | N/A | 55 | ok |
| yolo26-m-seg_640x640.dxnn | 24.9 | 40.10 | 40.10 | N/A | 55 | ok |
| yolo26-l-seg_640x640.dxnn | 21.2 | 47.14 | 47.14 | N/A | 54 | ok |
| yolo26-x-seg_640x640.dxnn | 11.8 | 84.78 | 84.78 | N/A | 54 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-obb_1024x1024.dxnn | 42.5 | 23.51 | 23.22 | 0.29 | 55 | ok |
| yolo26-s-obb_1024x1024.dxnn | 25.8 | 38.83 | 38.52 | 0.31 | 55 | ok |
| yolo26-m-obb_1024x1024.dxnn | 17.7 | 56.40 | 56.10 | 0.30 | 55 | ok |
| yolo26-l-obb_1024x1024.dxnn | 13.4 | 74.88 | 74.57 | 0.31 | 55 | ok |
| yolo26-x-obb_1024x1024.dxnn | 7.0 | 142.53 | 142.21 | 0.32 | 54 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-obb_1024x1024.dxnn | 43.3 | 23.08 | 23.08 | N/A | 55 | ok |
| yolo26-s-obb_1024x1024.dxnn | 26.1 | 38.29 | 38.29 | N/A | 55 | ok |
| yolo26-m-obb_1024x1024.dxnn | 17.8 | 56.22 | 56.22 | N/A | 54 | ok |
| yolo26-l-obb_1024x1024.dxnn | 13.4 | 74.55 | 74.55 | N/A | 54 | ok |
| yolo26-x-obb_1024x1024.dxnn | 7.0 | 142.27 | 142.27 | N/A | 54 | ok |

#### Classification

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-cls-n_224x224.dxnn | 986.4 | 1.01 | 1.01 | N/A | 55 | ok |
| yolo26-cls-s_224x224.dxnn | 624.4 | 1.60 | 1.60 | N/A | 55 | ok |
| yolo26-cls-m_224x224.dxnn | 455.5 | 2.20 | 2.20 | N/A | 54 | ok |
| yolo26-cls-l_224x224.dxnn | 292.2 | 3.42 | 3.42 | N/A | 55 | ok |
| yolo26-cls-x_224x224.dxnn | 169.3 | 5.91 | 5.91 | N/A | 55 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-cls-n_224x224.dxnn | 1023.0 | 0.98 | 0.98 | N/A | 54 | ok |
| yolo26-cls-s_224x224.dxnn | 623.4 | 1.60 | 1.60 | N/A | 54 | ok |
| yolo26-cls-m_224x224.dxnn | 455.0 | 2.20 | 2.20 | N/A | 54 | ok |
| yolo26-cls-l_224x224.dxnn | 292.7 | 3.42 | 3.42 | N/A | 54 | ok |
| yolo26-cls-x_224x224.dxnn | 169.0 | 5.92 | 5.92 | N/A | 55 | ok |

## E2E Pipeline (Single-Stream)

### Object Detection

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | vaapidecodebin | 3455 | 3 | 493.6 ±0.4 | 7.00 | 215 | 20.6 | 79.3 | 55 | 1000 | 513 | ok |
| yolo26-s_640x640.dxnn | vaapidecodebin | 3455 | 3 | 492.9 ±0.8 | 7.01 | 212 | 37.9 | 85.0 | 55 | 1000 | 588 | ok |
| yolo26-m_640x640.dxnn | vaapidecodebin | 3455 | 3 | 491.7 ±0.7 | 7.03 | 213 | 67.1 | 99.7 | 57~58 | 1000 | 703 | ok |
| yolo26-l_640x640.dxnn | vaapidecodebin | 3455 | 3 | 376.8 ±2.7 | 9.17 | 148 | 73.1 | 100.0 | 57~58 | 1000 | 788 | ok |
| yolo26-x_640x640.dxnn | vaapidecodebin | 3455 | 3 | 201.1 ±0.4 | 17.18 | 69 | 83.8 | 100.0 | 58~61 | 1000 | 975 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | vaapidecodebin | 3455 | 3 | 447.0 ±0.7 | 7.73 | 243 | 19.9 | 81.5 | 55 | 1000 | 628 | ok |
| yolo26-s_640x640.dxnn | vaapidecodebin | 3455 | 3 | 447.4 ±1.8 | 7.72 | 240 | 34.6 | 78.1 | 55 | 1000 | 705 | ok |
| yolo26-m_640x640.dxnn | vaapidecodebin | 3455 | 3 | 448.7 ±1.6 | 7.70 | 235 | 58.2 | 88.3 | 56~57 | 1000 | 779 | ok |
| yolo26-l_640x640.dxnn | vaapidecodebin | 3455 | 3 | 376.8 ±2.7 | 9.17 | 191 | 75.4 | 100.0 | 57~58 | 1000 | 842 | ok |
| yolo26-x_640x640.dxnn | vaapidecodebin | 3455 | 3 | 201.0 ±0.3 | 17.19 | 91 | 83.6 | 100.0 | 59~61 | 1000 | 1021 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n_640x640.dxnn | 493.6 | 447.0 | +46.6 | +10.4% |
| yolo26-s_640x640.dxnn | 492.9 | 447.4 | +45.6 | +10.2% |
| yolo26-m_640x640.dxnn | 491.7 | 448.7 | +43.1 | +9.6% |
| yolo26-l_640x640.dxnn | 376.8 | 376.8 | +0.0 | +0.0% |
| yolo26-x_640x640.dxnn | 201.1 | 201.0 | +0.1 | +0.0% |

### Pose Estimation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | vaapidecodebin | 3455 | 3 | 541.4 ±1.9 | 6.38 | 166 | 26.0 | 62.6 | 55 | 1000 | 429 | ok |
| yolo26-s-pose_640x640.dxnn | vaapidecodebin | 3455 | 3 | 539.0 ±2.1 | 6.41 | 166 | 49.6 | 78.0 | 55~56 | 1000 | 512 | ok |
| yolo26-m-pose_640x640.dxnn | vaapidecodebin | 3455 | 3 | 501.9 ±0.9 | 6.88 | 162 | 67.4 | 100.0 | 57~58 | 1000 | 676 | ok |
| yolo26-l-pose_640x640.dxnn | vaapidecodebin | 3455 | 3 | 366.6 ±0.0 | 9.42 | 99 | 75.0 | 100.0 | 57~58 | 1000 | 705 | ok |
| yolo26-x-pose_640x640.dxnn | vaapidecodebin | 3455 | 3 | 195.6 ±0.6 | 17.66 | 50 | 81.1 | 100.0 | 59~62 | 1000 | 895 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | vaapidecodebin | 3455 | 3 | 554.6 ±2.9 | 6.23 | 127 | 25.3 | 61.6 | 55 | 1000 | 417 | ok |
| yolo26-s-pose_640x640.dxnn | vaapidecodebin | 3455 | 3 | 554.1 ±2.0 | 6.24 | 127 | 50.9 | 77.4 | 55 | 1000 | 501 | ok |
| yolo26-m-pose_640x640.dxnn | vaapidecodebin | 3455 | 3 | 501.9 ±1.0 | 6.88 | 123 | 67.8 | 100.0 | 57~58 | 1000 | 690 | ok |
| yolo26-l-pose_640x640.dxnn | vaapidecodebin | 3455 | 3 | 366.7 ±0.1 | 9.42 | 79 | 77.8 | 100.0 | 57~58 | 1000 | 717 | ok |
| yolo26-x-pose_640x640.dxnn | vaapidecodebin | 3455 | 3 | 195.7 ±0.6 | 17.66 | 40 | 81.6 | 100.0 | 58~61 | 1000 | 907 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-pose_640x640.dxnn | 541.4 | 554.6 | -13.2 | -2.4% |
| yolo26-s-pose_640x640.dxnn | 539.0 | 554.1 | -15.1 | -2.7% |
| yolo26-m-pose_640x640.dxnn | 501.9 | 501.9 | +0.0 | +0.0% |
| yolo26-l-pose_640x640.dxnn | 366.6 | 366.7 | -0.1 | -0.0% |
| yolo26-x-pose_640x640.dxnn | 195.6 | 195.7 | -0.1 | -0.0% |

### Segmentation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | vaapidecodebin | 3455 | 3 | 359.1 ±0.6 | 9.62 | 532 | 20.1 | 80.7 | 55 | 1000 | 958 | ok |
| yolo26-s-seg_640x640.dxnn | vaapidecodebin | 3455 | 3 | 361.2 ±0.5 | 9.57 | 512 | 38.5 | 80.7 | 56~57 | 1000 | 1005 | ok |
| yolo26-m-seg_640x640.dxnn | vaapidecodebin | 3455 | 3 | 320.5 ±2.9 | 10.78 | 392 | 74.5 | 100.0 | 58~60 | 1000 | 1173 | ok |
| yolo26-l-seg_640x640.dxnn | vaapidecodebin | 3455 | 3 | 268.0 ±0.3 | 12.89 | 292 | 79.0 | 100.0 | 58~60 | 1000 | 1205 | ok |
| yolo26-x-seg_640x640.dxnn | vaapidecodebin | 3455 | 3 | 141.6 ±0.4 | 24.40 | 133 | 86.0 | 100.0 | 61~66 | 1000 | 1416 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | vaapidecodebin | 3455 | 3 | 319.0 ±0.3 | 10.83 | 412 | 18.7 | 71.2 | 55 | 1000 | 1031 | ok |
| yolo26-s-seg_640x640.dxnn | vaapidecodebin | 3455 | 3 | 314.9 ±0.4 | 10.97 | 397 | 36.1 | 71.7 | 56 | 1000 | 1116 | ok |
| yolo26-m-seg_640x640.dxnn | vaapidecodebin | 3455 | 3 | 316.9 ±0.8 | 10.90 | 405 | 75.3 | 100.0 | 58~60 | 1000 | 1265 | ok |
| yolo26-l-seg_640x640.dxnn | vaapidecodebin | 3455 | 3 | 267.9 ±0.2 | 12.89 | 317 | 79.3 | 100.0 | 58~61 | 1000 | 1284 | ok |
| yolo26-x-seg_640x640.dxnn | vaapidecodebin | 3455 | 3 | 141.6 ±0.4 | 24.41 | 146 | 87.0 | 100.0 | 61~65 | 1000 | 1490 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-seg_640x640.dxnn | 359.1 | 319.0 | +40.1 | +12.6% |
| yolo26-s-seg_640x640.dxnn | 361.2 | 314.9 | +46.3 | +14.7% |
| yolo26-m-seg_640x640.dxnn | 320.5 | 316.9 | +3.6 | +1.1% |
| yolo26-l-seg_640x640.dxnn | 268.0 | 267.9 | +0.1 | +0.0% |
| yolo26-x-seg_640x640.dxnn | 141.6 | 141.6 | +0.0 | +0.0% |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | vaapidecodebin | 2640 | 3 | 394.6 ±1.9 | 6.69 | 153 | 62.0 | 90.6 | 55~56 | 1000 | 614 | ok |
| yolo26-s-obb_1024x1024.dxnn | vaapidecodebin | 2640 | 3 | 263.4 ±1.8 | 10.02 | 105 | 73.9 | 100.0 | 56~57 | 1000 | 797 | ok |
| yolo26-m-obb_1024x1024.dxnn | vaapidecodebin | 2640 | 3 | 176.1 ±2.5 | 14.99 | 65 | 80.7 | 100.0 | 59~62 | 1000 | 852 | ok |
| yolo26-l-obb_1024x1024.dxnn | vaapidecodebin | 2640 | 3 | 130.0 ±0.4 | 20.31 | 48 | 85.3 | 100.0 | 59~63 | 1000 | 887 | ok |
| yolo26-x-obb_1024x1024.dxnn | vaapidecodebin | 2640 | 3 | 71.2 ±0.0 | 37.06 | 27 | 91.3 | 100.0 | 62~67 | 1000 | 1086 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | vaapidecodebin | 2640 | 3 | 394.8 ±1.5 | 6.69 | 159 | 60.3 | 90.5 | 55~56 | 1000 | 636 | ok |
| yolo26-s-obb_1024x1024.dxnn | vaapidecodebin | 2640 | 3 | 263.2 ±1.7 | 10.03 | 108 | 74.6 | 100.0 | 56~57 | 1000 | 810 | ok |
| yolo26-m-obb_1024x1024.dxnn | vaapidecodebin | 2640 | 3 | 176.0 ±2.6 | 15.00 | 70 | 82.7 | 100.0 | 58~60 | 1000 | 870 | ok |
| yolo26-l-obb_1024x1024.dxnn | vaapidecodebin | 2640 | 3 | 130.1 ±0.4 | 20.29 | 50 | 85.6 | 100.0 | 59~61 | 1000 | 905 | ok |
| yolo26-x-obb_1024x1024.dxnn | vaapidecodebin | 2640 | 3 | 71.2 ±0.1 | 37.05 | 29 | 91.4 | 100.0 | 62~67 | 1000 | 1102 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-obb_1024x1024.dxnn | 394.6 | 394.8 | -0.1 | -0.0% |
| yolo26-s-obb_1024x1024.dxnn | 263.4 | 263.2 | +0.2 | +0.1% |
| yolo26-m-obb_1024x1024.dxnn | 176.1 | 176.0 | +0.1 | +0.0% |
| yolo26-l-obb_1024x1024.dxnn | 130.0 | 130.1 | -0.1 | -0.1% |
| yolo26-x-obb_1024x1024.dxnn | 71.2 | 71.2 | -0.0 | -0.0% |

### Classification

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-cls-n_224x224.dxnn | vaapidecodebin | 3455 | 3 | 809.7 ±2.0 | 4.27 | 37 | 3.2 | 15.4 | 54 | 1000 | 168 | ok |
| yolo26-cls-s_224x224.dxnn | vaapidecodebin | 3455 | 3 | 807.9 ±0.3 | 4.28 | 36 | 5.7 | 27.9 | 54~55 | 1000 | 199 | ok |
| yolo26-cls-m_224x224.dxnn | vaapidecodebin | 3455 | 3 | 804.4 ±0.9 | 4.29 | 37 | 8.3 | 39.7 | 55 | 1000 | 230 | ok |
| yolo26-cls-l_224x224.dxnn | vaapidecodebin | 3455 | 3 | 800.4 ±1.4 | 4.32 | 38 | 13.4 | 64.0 | 55 | 1000 | 249 | ok |
| yolo26-cls-x_224x224.dxnn | vaapidecodebin | 3455 | 3 | 782.0 ±0.6 | 4.42 | 41 | 22.7 | 57.6 | 55 | 1000 | 340 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-cls-n_224x224.dxnn | vaapidecodebin | 3455 | 3 | 809.3 ±1.2 | 4.27 | 37 | 3.1 | 15.4 | 55 | 1000 | 169 | ok |
| yolo26-cls-s_224x224.dxnn | vaapidecodebin | 3455 | 3 | 808.5 ±1.5 | 4.27 | 36 | 5.9 | 27.9 | 54~55 | 1000 | 199 | ok |
| yolo26-cls-m_224x224.dxnn | vaapidecodebin | 3455 | 3 | 805.5 ±0.8 | 4.29 | 37 | 8.4 | 39.9 | 55 | 1000 | 230 | ok |
| yolo26-cls-l_224x224.dxnn | vaapidecodebin | 3455 | 3 | 798.8 ±2.2 | 4.33 | 38 | 13.4 | 63.7 | 55 | 1000 | 249 | ok |
| yolo26-cls-x_224x224.dxnn | vaapidecodebin | 3455 | 3 | 782.9 ±1.1 | 4.41 | 41 | 22.8 | 57.6 | 55 | 1000 | 340 | ok |

> Classification has no CPU part, so ORT ON and OFF run the same model; differences between the two tables are measurement noise.

## E2E Pipeline (Multi-Stream)

### Object Detection

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | 16 | 3 | 532.4 ±0.8 | 33.3 | 304 | 31.2 | 77.6 | 57~59 | 1000 | 812 | ok |
| yolo26-n_640x640.dxnn | 17 | 3 | 532.4 ±1.1 | 31.3 | 305 | 31.8 | 77.6 | 60~61 | 1000 | 825 | ok |
| yolo26-n_640x640.dxnn | 18 | 3 | 531.9 ±0.9 | 29.6 | 303 | 31.6 | 79.1 | 61~62 | 1000 | 844 | ok |
| yolo26-s_640x640.dxnn | 16 | 3 | 529.3 ±0.4 | 33.1 | 311 | 60.1 | 89.0 | 62~65 | 1000 | 1043 | ok |
| yolo26-s_640x640.dxnn | 17 | 3 | 528.6 ±2.4 | 31.1 | 310 | 59.9 | 88.9 | 67~68 | 1000 | 1058 | ok |
| yolo26-s_640x640.dxnn | 18 | 3 | 528.3 ±0.8 | 29.4 | 309 | 59.1 | 89.2 | 69 | 1000 | 1064 | ok |
| yolo26-m_640x640.dxnn | 16 | 3 | 501.9 ±5.0 | 31.4 | 294 | 95.7 | 100.0 | 73~81 | 1000 | 1027 | ok |
| yolo26-m_640x640.dxnn | 17 | 3 | 455.9 ±18.9 | 26.8 | 256 | 94.8 | 100.0 | 84~85 | 600~1000 | 1039 | ok |
| yolo26-l_640x640.dxnn | 12 | 3 | 376.7 ±2.4 | 31.4 | 183 | 95.9 | 100.0 | 74~80 | 1000 | 1002 | ok |
| yolo26-l_640x640.dxnn | 13 | 3 | 361.5 ±5.1 | 27.8 | 170 | 95.5 | 100.0 | 83~84 | 600~1000 | 1033 | ok |
| yolo26-x_640x640.dxnn | 6 | 3 | 199.5 ±1.2 | 33.2 | 76 | 95.4 | 100.0 | 77~81 | 800~1000 | 1085 | ok |
| yolo26-x_640x640.dxnn | 7 | 3 | 170.5 ±17.4 | 24.4 | 67 | 91.2 | 100.0 | 84~86 | 400~1000 | 1096 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | 14 | 3 | 434.9 ±4.2 | 31.1 | 255 | 25.3 | 81.7 | 56~58 | 1000 | 933 | ok |
| yolo26-n_640x640.dxnn | 15 | 3 | 435.8 ±1.5 | 29.1 | 255 | 25.5 | 80.2 | 59 | 1000 | 961 | ok |
| yolo26-s_640x640.dxnn | 14 | 3 | 432.6 ±3.6 | 30.9 | 254 | 46.4 | 76.5 | 61~63 | 1000 | 1096 | ok |
| yolo26-s_640x640.dxnn | 15 | 3 | 434.2 ±0.9 | 28.9 | 254 | 46.5 | 75.3 | 65 | 1000 | 1130 | ok |
| yolo26-m_640x640.dxnn | 14 | 3 | 424.5 ±13.4 | 30.3 | 252 | 79.6 | 89.6 | 70~77 | 1000 | 1090 | ok |
| yolo26-m_640x640.dxnn | 15 | 3 | 429.9 ±6.1 | 28.7 | 253 | 80.6 | 91.9 | 80~82 | 800~1000 | 1112 | ok |
| yolo26-l_640x640.dxnn | 12 | 3 | 376.6 ±2.7 | 31.4 | 234 | 95.6 | 100.0 | 74~80 | 1000 | 1080 | ok |
| yolo26-l_640x640.dxnn | 13 | 3 | 356.8 ±9.2 | 27.4 | 215 | 95.8 | 100.0 | 83~84 | 600~1000 | 1108 | ok |
| yolo26-x_640x640.dxnn | 6 | 3 | 198.3 ±3.0 | 33.1 | 98 | 95.2 | 100.0 | 74~83 | 800~1000 | 1159 | ok |
| yolo26-x_640x640.dxnn | 7 | 3 | 172.0 ±16.6 | 24.6 | 89 | 91.5 | 100.0 | 84~85 | 400~1000 | 1174 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n_640x640.dxnn | 17 | 31.3 | 14 | 31.1 |
| yolo26-s_640x640.dxnn | 17 | 31.1 | 14 | 30.9 |
| yolo26-m_640x640.dxnn | 16 | 31.4 | 14 | 30.3 |
| yolo26-l_640x640.dxnn | 12 | 31.4 | 12 | 31.4 |
| yolo26-x_640x640.dxnn | 6 | 33.2 | 6 | 33.1 |

### Pose Estimation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 18 | 3 | 588.4 ±2.1 | 32.7 | 241 | 38.7 | 76.0 | 58~61 | 1000 | 897 | ok |
| yolo26-n-pose_640x640.dxnn | 19 | 3 | 590.3 ±2.4 | 31.1 | 239 | 38.7 | 75.2 | 62~63 | 1000 | 926 | ok |
| yolo26-n-pose_640x640.dxnn | 20 | 3 | 590.8 ±0.6 | 29.5 | 239 | 39.0 | 73.7 | 63 | 1000 | 934 | ok |
| yolo26-s-pose_640x640.dxnn | 17 | 3 | 586.2 ±2.0 | 34.5 | 239 | 73.1 | 88.7 | 62~67 | 1000 | 1018 | ok |
| yolo26-s-pose_640x640.dxnn | 18 | 3 | 587.1 ±3.2 | 32.6 | 238 | 73.1 | 89.8 | 69~71 | 1000 | 1052 | ok |
| yolo26-s-pose_640x640.dxnn | 19 | 3 | 587.1 ±0.2 | 30.9 | 237 | 73.5 | 89.3 | 71~72 | 1000 | 1069 | ok |
| yolo26-s-pose_640x640.dxnn | 20 | 3 | 585.5 ±1.0 | 29.3 | 238 | 73.4 | 89.2 | 71~72 | 1000 | 1093 | ok |
| yolo26-m-pose_640x640.dxnn | 16 | 3 | 502.1 ±1.1 | 31.4 | 201 | 95.8 | 100.0 | 74~81 | 1000 | 950 | ok |
| yolo26-m-pose_640x640.dxnn | 17 | 3 | 432.6 ±45.3 | 25.4 | 168 | 91.7 | 100.0 | 83~85 | 400~1000 | 969 | ok |
| yolo26-l-pose_640x640.dxnn | 12 | 3 | 367.6 ±1.7 | 30.6 | 122 | 96.0 | 100.0 | 72~80 | 1000 | 933 | ok |
| yolo26-l-pose_640x640.dxnn | 13 | 3 | 356.9 ±5.3 | 27.5 | 122 | 95.3 | 100.0 | 82~85 | 600~1000 | 959 | ok |
| yolo26-x-pose_640x640.dxnn | 6 | 3 | 195.2 ±0.5 | 32.5 | 54 | 94.6 | 100.0 | 76~81 | 800~1000 | 1010 | ok |
| yolo26-x-pose_640x640.dxnn | 7 | 3 | 169.7 ±19.1 | 24.2 | 53 | 91.3 | 100.0 | 83~85 | 400~1000 | 1023 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 18 | 3 | 605.7 ±0.5 | 33.6 | 185 | 40.1 | 74.2 | 59~61 | 1000 | 901 | ok |
| yolo26-n-pose_640x640.dxnn | 19 | 3 | 605.1 ±1.3 | 31.9 | 186 | 40.0 | 76.6 | 62~63 | 1000 | 927 | ok |
| yolo26-n-pose_640x640.dxnn | 20 | 3 | 605.9 ±0.8 | 30.3 | 185 | 40.1 | 74.2 | 63 | 1000 | 944 | ok |
| yolo26-n-pose_640x640.dxnn | 21 | 3 | 605.5 ±1.3 | 28.8 | 184 | 40.0 | 74.3 | 63 | 1000 | 973 | ok |
| yolo26-s-pose_640x640.dxnn | 18 | 3 | 602.7 ±0.7 | 33.5 | 185 | 75.9 | 91.2 | 64~67 | 1000 | 1085 | ok |
| yolo26-s-pose_640x640.dxnn | 19 | 3 | 603.1 ±2.1 | 31.7 | 185 | 76.0 | 90.8 | 70~71 | 1000 | 1110 | ok |
| yolo26-s-pose_640x640.dxnn | 20 | 3 | 601.3 ±1.6 | 30.1 | 185 | 75.6 | 91.2 | 72 | 1000 | 1135 | ok |
| yolo26-s-pose_640x640.dxnn | 21 | 3 | 601.8 ±1.5 | 28.7 | 185 | 76.2 | 91.2 | 72 | 1000 | 1167 | ok |
| yolo26-m-pose_640x640.dxnn | 16 | 3 | 502.1 ±1.0 | 31.4 | 154 | 95.7 | 100.0 | 75~81 | 1000 | 979 | ok |
| yolo26-m-pose_640x640.dxnn | 17 | 3 | 457.3 ±11.0 | 26.9 | 138 | 95.3 | 100.0 | 85 | 600~1000 | 1000 | ok |
| yolo26-l-pose_640x640.dxnn | 12 | 3 | 367.4 ±1.9 | 30.6 | 95 | 96.0 | 100.0 | 72~81 | 800~1000 | 956 | ok |
| yolo26-l-pose_640x640.dxnn | 13 | 3 | 358.6 ±1.5 | 27.6 | 96 | 96.1 | 100.0 | 82~83 | 800~1000 | 982 | ok |
| yolo26-x-pose_640x640.dxnn | 6 | 3 | 193.8 ±1.0 | 32.3 | 44 | 94.4 | 100.0 | 76~82 | 800~1000 | 1028 | ok |
| yolo26-x-pose_640x640.dxnn | 7 | 3 | 169.4 ±18.7 | 24.2 | 42 | 92.1 | 100.0 | 83~85 | 400~1000 | 1042 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-pose_640x640.dxnn | 19 | 31.1 | 20 | 30.3 |
| yolo26-s-pose_640x640.dxnn | 19 | 30.9 | 20 | 30.1 |
| yolo26-m-pose_640x640.dxnn | 16 | 31.4 | 16 | 31.4 |
| yolo26-l-pose_640x640.dxnn | 12 | 30.6 | 12 | 30.6 |
| yolo26-x-pose_640x640.dxnn | 6 | 32.5 | 6 | 32.3 |

### Segmentation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 11 | 3 | 365.6 ±1.4 | 33.2 | 611 | 26.8 | 78.3 | 57~58 | 1000 | 1374 | ok |
| yolo26-n-seg_640x640.dxnn | 12 | 3 | 357.0 ±10.8 | 29.8 | 622 | 26.3 | 69.3 | 60 | 1000 | 1405 | ok |
| yolo26-s-seg_640x640.dxnn | 12 | 3 | 355.4 ±13.8 | 29.6 | 614 | 52.3 | 80.0 | 64~66 | 1000 | 1450 | ok |
| yolo26-s-seg_640x640.dxnn | 11 | 3 | 362.0 ±4.1 | 32.9 | 619 | 52.8 | 79.7 | 67~68 | 1000 | 1421 | ok |
| yolo26-m-seg_640x640.dxnn | 10 | 3 | 292.7 ±22.5 | 29.3 | 454 | 90.9 | 100.0 | 78~85 | 400~1000 | 1391 | ok |
| yolo26-m-seg_640x640.dxnn | 9 | 3 | 250.0 ±14.8 | 27.8 | 304 | 88.1 | 100.0 | 85~86 | 400~1000 | 1394 | ok |
| yolo26-m-seg_640x640.dxnn | 8 | 3 | 229.6 ±14.6 | 28.7 | 276 | 84.8 | 100.0 | 85~86 | 400~1000 | 1365 | ok |
| yolo26-m-seg_640x640.dxnn | 7 | 3 | 255.8 ±9.4 | 36.5 | 311 | 90.8 | 100.0 | 86~87 | 400~1000 | 1329 | ok |
| yolo26-l-seg_640x640.dxnn | 8 | 3 | 256.2 ±12.2 | 32.0 | 327 | 94.5 | 100.0 | 79~85 | 600~1000 | 1387 | ok |
| yolo26-l-seg_640x640.dxnn | 9 | 3 | 212.5 ±6.7 | 23.6 | 241 | 85.8 | 100.0 | 84~85 | 400~1000 | 1426 | ok |
| yolo26-x-seg_640x640.dxnn | 4 | 3 | 128.0 ±8.9 | 32.0 | 129 | 94.1 | 100.0 | 82~84 | 600~1000 | 1508 | ok |
| yolo26-x-seg_640x640.dxnn | 5 | 3 | 109.2 ±6.6 | 21.8 | 110 | 87.6 | 100.0 | 83~87 | 400~1000 | 1528 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 10 | 3 | 289.5 ±18.9 | 28.9 | 415 | 20.6 | 70.4 | 57 | 1000 | 1394 | ok |
| yolo26-n-seg_640x640.dxnn | 9 | 3 | 286.9 ±25.6 | 31.9 | 416 | 20.7 | 71.2 | 58~59 | 1000 | 1349 | ok |
| yolo26-s-seg_640x640.dxnn | 10 | 3 | 292.0 ±20.7 | 29.2 | 407 | 41.6 | 71.7 | 61~65 | 1000 | 1455 | ok |
| yolo26-s-seg_640x640.dxnn | 9 | 3 | 303.1 ±1.9 | 33.7 | 410 | 42.9 | 71.5 | 66 | 1000 | 1432 | ok |
| yolo26-m-seg_640x640.dxnn | 10 | 3 | 296.5 ±15.2 | 29.6 | 410 | 90.2 | 100.0 | 77~85 | 400~1000 | 1520 | ok |
| yolo26-m-seg_640x640.dxnn | 9 | 3 | 250.3 ±11.6 | 27.8 | 332 | 87.8 | 100.0 | 85 | 400~1000 | 1486 | ok |
| yolo26-m-seg_640x640.dxnn | 8 | 3 | 241.2 ±2.6 | 30.1 | 316 | 82.8 | 100.0 | 85 | 400~1000 | 1467 | ok |
| yolo26-l-seg_640x640.dxnn | 8 | 3 | 264.7 ±4.0 | 33.1 | 344 | 94.9 | 100.0 | 76~84 | 800~1000 | 1483 | ok |
| yolo26-l-seg_640x640.dxnn | 9 | 3 | 200.1 ±16.1 | 22.2 | 253 | 87.2 | 100.0 | 85~86 | 400~1000 | 1517 | ok |
| yolo26-x-seg_640x640.dxnn | 4 | 3 | 132.2 ±10.2 | 33.0 | 146 | 94.0 | 100.0 | 78~85 | 400~1000 | 1599 | ok |
| yolo26-x-seg_640x640.dxnn | 5 | 3 | 112.3 ±5.9 | 22.5 | 125 | 91.3 | 100.0 | 84~85 | 400~1000 | 1632 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-seg_640x640.dxnn | 11 | 33.2 | 9 | 31.9 |
| yolo26-s-seg_640x640.dxnn | 11 | 32.9 | 9 | 33.7 |
| yolo26-m-seg_640x640.dxnn | 7 | 36.5 | 8 | 30.1 |
| yolo26-l-seg_640x640.dxnn | 8 | 32.0 | 8 | 33.1 |
| yolo26-x-seg_640x640.dxnn | 4 | 32.0 | 4 | 33.0 |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 13 | 3 | 420.2 ±7.1 | 32.3 | 211 | 87.3 | 98.8 | 63~68 | 1000 | 1107 | ok |
| yolo26-n-obb_1024x1024.dxnn | 14 | 3 | 424.6 ±1.3 | 30.3 | 211 | 88.7 | 98.8 | 70~71 | 1000 | 1102 | ok |
| yolo26-n-obb_1024x1024.dxnn | 15 | 3 | 424.7 ±1.4 | 28.3 | 211 | 88.2 | 98.9 | 72 | 1000 | 1129 | ok |
| yolo26-s-obb_1024x1024.dxnn | 8 | 3 | 264.4 ±1.7 | 33.0 | 120 | 94.3 | 100.0 | 64~70 | 1000 | 1016 | ok |
| yolo26-s-obb_1024x1024.dxnn | 9 | 3 | 263.0 ±1.6 | 29.2 | 121 | 94.2 | 100.0 | 74~75 | 1000 | 1061 | ok |
| yolo26-m-obb_1024x1024.dxnn | 5 | 3 | 175.8 ±2.6 | 35.1 | 75 | 93.3 | 100.0 | 72~76 | 1000 | 968 | ok |
| yolo26-m-obb_1024x1024.dxnn | 6 | 3 | 174.8 ±3.5 | 29.1 | 73 | 95.5 | 100.0 | 81~85 | 600~1000 | 984 | ok |
| yolo26-l-obb_1024x1024.dxnn | 4 | 3 | 130.1 ±0.7 | 32.5 | 51 | 95.1 | 100.0 | 71~76 | 1000 | 969 | ok |
| yolo26-l-obb_1024x1024.dxnn | 5 | 3 | 120.3 ±10.4 | 24.1 | 52 | 93.1 | 100.0 | 82~85 | 400~1000 | 994 | ok |
| yolo26-x-obb_1024x1024.dxnn | 2 | 3 | 70.8 ±0.5 | 35.4 | 28 | 94.6 | 100.0 | 74~82 | 800~1000 | 1118 | ok |
| yolo26-x-obb_1024x1024.dxnn | 3 | 3 | 66.1 ±2.0 | 22.0 | 28 | 92.8 | 100.0 | 83~84 | 600~1000 | 1152 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 13 | 3 | 428.3 ±2.6 | 32.9 | 217 | 88.4 | 98.8 | 61~66 | 1000 | 1143 | ok |
| yolo26-n-obb_1024x1024.dxnn | 14 | 3 | 418.6 ±10.4 | 29.9 | 219 | 86.8 | 98.6 | 70~71 | 1000 | 1132 | ok |
| yolo26-s-obb_1024x1024.dxnn | 8 | 3 | 263.4 ±1.6 | 32.9 | 125 | 94.4 | 100.0 | 64~70 | 1000 | 1037 | ok |
| yolo26-s-obb_1024x1024.dxnn | 9 | 3 | 263.0 ±1.4 | 29.2 | 124 | 94.5 | 100.0 | 73~74 | 1000 | 1074 | ok |
| yolo26-m-obb_1024x1024.dxnn | 5 | 3 | 175.8 ±2.6 | 35.2 | 76 | 91.8 | 100.0 | 69~77 | 1000 | 982 | ok |
| yolo26-m-obb_1024x1024.dxnn | 6 | 3 | 169.3 ±3.8 | 28.2 | 77 | 93.7 | 100.0 | 83 | 600~1000 | 1007 | ok |
| yolo26-l-obb_1024x1024.dxnn | 4 | 3 | 129.7 ±0.6 | 32.4 | 54 | 94.6 | 100.0 | 70~79 | 1000 | 985 | ok |
| yolo26-l-obb_1024x1024.dxnn | 5 | 3 | 128.6 ±0.9 | 25.7 | 56 | 94.4 | 100.0 | 82 | 800~1000 | 1017 | ok |
| yolo26-x-obb_1024x1024.dxnn | 2 | 3 | 70.4 ±0.7 | 35.2 | 30 | 93.9 | 100.0 | 78~82 | 800~1000 | 1136 | ok |
| yolo26-x-obb_1024x1024.dxnn | 3 | 3 | 65.7 ±0.6 | 21.9 | 29 | 92.8 | 100.0 | 83 | 600~1000 | 1171 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-obb_1024x1024.dxnn | 14 | 30.3 | 13 | 32.9 |
| yolo26-s-obb_1024x1024.dxnn | 8 | 33.0 | 8 | 32.9 |
| yolo26-m-obb_1024x1024.dxnn | 5 | 35.1 | 5 | 35.2 |
| yolo26-l-obb_1024x1024.dxnn | 4 | 32.5 | 4 | 32.4 |
| yolo26-x-obb_1024x1024.dxnn | 2 | 35.4 | 2 | 35.2 |

---
*Report generated by dx-benchmark tool*
