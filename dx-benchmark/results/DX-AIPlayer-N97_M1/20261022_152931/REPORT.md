# YOLO26 Benchmark Report

**Generated:** 2026-10-24 12:06:33 (UTC+09:00, local)

## Test Timing

| # | Type | Start | End | Duration |
|---|------|-------|-----|----------|
| 1 | run | 2026-10-22 15:29:31 | 2026-10-24 12:06:33 | 44h 37m 1s |

## Executive Summary

### Object Detection

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n_640x640.dxnn | ON | 24.39 | 244.0 | 159.9 | 5 |
| yolo26-n_640x640.dxnn | OFF | 23.32 | 326.2 | 178.0 | 6 |
| yolo26-s_640x640.dxnn | ON | 30.70 | 199.5 | 139.3 | 4 |
| yolo26-s_640x640.dxnn | OFF | 29.61 | 199.6 | 165.1 | 5 |
| yolo26-m_640x640.dxnn | ON | 38.52 | 123.6 | 117.1 | 3 |
| yolo26-m_640x640.dxnn | OFF | 36.67 | 123.9 | 121.3 | 2 |
| yolo26-l_640x640.dxnn | ON | 45.98 | 90.8 | 90.6 | 2 |
| yolo26-l_640x640.dxnn | OFF | 44.27 | 90.7 | 91.1 | 2 |
| yolo26-x_640x640.dxnn | ON | 71.11 | 48.8 | 49.0 | 1 |
| yolo26-x_640x640.dxnn | OFF | 69.84 | 48.9 | 49.0 | 1 |

### Pose Estimation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-pose_640x640.dxnn | ON | 20.48 | 303.8 | 170.6 | 6 |
| yolo26-n-pose_640x640.dxnn | OFF | 20.29 | 305.3 | 192.2 | 7 |
| yolo26-s-pose_640x640.dxnn | ON | 28.01 | 183.9 | 158.4 | 5 |
| yolo26-s-pose_640x640.dxnn | OFF | 26.88 | 184.2 | 179.1 | 5 |
| yolo26-m-pose_640x640.dxnn | ON | 35.05 | 122.6 | 120.0 | 2 |
| yolo26-m-pose_640x640.dxnn | OFF | 34.25 | 122.7 | 121.2 | 3 |
| yolo26-l-pose_640x640.dxnn | ON | 42.53 | 89.3 | 89.4 | 2 |
| yolo26-l-pose_640x640.dxnn | OFF | 41.82 | 89.4 | 89.4 | 2 |
| yolo26-x-pose_640x640.dxnn | ON | 69.36 | 47.5 | 47.8 | 1 |
| yolo26-x-pose_640x640.dxnn | OFF | 68.40 | 47.6 | 47.7 | 1 |

### Segmentation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-seg_640x640.dxnn | ON | 37.89 | 138.1 | 95.0 | 3 |
| yolo26-n-seg_640x640.dxnn | OFF | 36.58 | 180.2 | 106.5 | 3 |
| yolo26-s-seg_640x640.dxnn | ON | 46.85 | 134.7 | 86.4 | 2 |
| yolo26-s-seg_640x640.dxnn | OFF | 45.21 | 138.1 | 97.4 | 3 |
| yolo26-m-seg_640x640.dxnn | ON | 60.89 | 77.1 | 72.0 | 1 |
| yolo26-m-seg_640x640.dxnn | OFF | 59.41 | 76.7 | 76.3 | 1 |
| yolo26-l-seg_640x640.dxnn | ON | 67.89 | 64.9 | 63.7 | 1 |
| yolo26-l-seg_640x640.dxnn | OFF | 66.74 | 65.0 | 64.5 | 1 |
| yolo26-x-seg_640x640.dxnn | ON | 104.70 | 34.3 | 29.3 | — |
| yolo26-x-seg_640x640.dxnn | OFF | 104.21 | 34.2 | 30.5 | 1 |

### Oriented BBox (OBB)

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-obb_1024x1024.dxnn | ON | 35.91 | 107.1 | 104.7 | 3 |
| yolo26-n-obb_1024x1024.dxnn | OFF | 35.09 | 107.2 | 105.3 | 3 |
| yolo26-s-obb_1024x1024.dxnn | ON | 51.28 | 64.1 | 63.5 | 2 |
| yolo26-s-obb_1024x1024.dxnn | OFF | 50.34 | 63.5 | 63.5 | 2 |
| yolo26-m-obb_1024x1024.dxnn | ON | 69.40 | 42.4 | 42.3 | 1 |
| yolo26-m-obb_1024x1024.dxnn | OFF | 68.28 | 42.6 | 42.3 | 1 |
| yolo26-l-obb_1024x1024.dxnn | ON | 88.11 | 31.0 | 30.9 | 1 |
| yolo26-l-obb_1024x1024.dxnn | OFF | 86.97 | 30.9 | 31.0 | 1 |
| yolo26-x-obb_1024x1024.dxnn | ON | 156.28 | 17.0 | 14.6 | — |
| yolo26-x-obb_1024x1024.dxnn | OFF | 155.07 | 17.0 | 14.5 | — |

### Classification

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-cls-n_224x224.dxnn | ON | 1.44 | 3512.5 | 276.5 | — |
| yolo26-cls-n_224x224.dxnn | OFF | 1.45 | 3521.3 | 276.7 | — |
| yolo26-cls-s_224x224.dxnn | ON | 2.08 | 1958.0 | 288.7 | — |
| yolo26-cls-s_224x224.dxnn | OFF | 2.07 | 1963.5 | 288.4 | — |
| yolo26-cls-m_224x224.dxnn | ON | 2.68 | 1381.8 | 288.8 | — |
| yolo26-cls-m_224x224.dxnn | OFF | 2.68 | 1382.3 | 288.4 | — |
| yolo26-cls-l_224x224.dxnn | ON | 3.92 | 888.2 | 291.2 | — |
| yolo26-cls-l_224x224.dxnn | OFF | 3.98 | 888.9 | 291.6 | — |
| yolo26-cls-x_224x224.dxnn | ON | 6.78 | 496.5 | 288.0 | — |
| yolo26-cls-x_224x224.dxnn | OFF | 6.73 | 496.7 | 288.6 | — |

## Environment

| Item | Value |
|------|-------|
| Product | DX-AIPlayer-N97 |
| Hostname | deepx |
| OS | Ubuntu 24.04.4 LTS |
| Kernel | 6.17.0-35-generic |
| CPU | Intel(R) N97 |
| CPU Threads | 4 |
| CPU Governor | powersave |
| RAM | 7.5 GiB |
| NPU SKU | M1 |
| NPU Chip / Board | M1 · M.2, Rev 1.0 |
| NPU Devices | 1 (M1) |
| DX-AllSuite | v2.5.0 |
| DX-Stream | 3.2.0 |
| Benchmark Tool | 0.2.0 |
| Tool commit | 4e94aa9 |
| NPU RT | v3.5.0 |
| NPU RT (commit) | v3.5.0 (build: 5.502926e) |
| NPU Driver (RT) | v2.7.0 |
| NPU Driver (PCIe) | v2.7.0 |
| NPU Firmware | v2.7.6 (build: 4.90f4a6f) |
| NPU Memory | LPDDR5 5600 Mbps, 3.92GiB |
| NPU Board | M.2, Rev 1.0 |
| NPU PCIe | Gen3 X2 [03:00:00] |

### Tools

| Tool | Available | Version |
|------|-----------|---------|
| run_model | Yes | DXRT v3.5.0 run_model |
| dxrt-cli | Yes | DXRT v3.5.0 (build: 5.502926e) |
| gst-launch-1.0 | Yes | gst-launch-1.0 version 1.24.2 |
| gst-inspect-1.0 | Yes | gst-inspect-1.0 version 1.24.2 |
| time | Yes | unknown |
| ffprobe | Yes | ffprobe version 6.1.1-3ubuntu5 Copyright (c) 2007-2023 the F... |
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
| yolo26-n_640x640.dxnn | 244.0 ±0.6 | 9 | 275 | 67.5 | 82.6 | 56~57 | 1000 | ok |
| yolo26-s_640x640.dxnn | 199.5 ±0.2 | 9 | 227 | 96.7 | 100.0 | 58 | 1000 | ok |
| yolo26-m_640x640.dxnn | 123.6 ±0.1 | 6 | 124 | 93.2 | 100.0 | 60 | 1000 | ok |
| yolo26-l_640x640.dxnn | 90.8 ±0.0 | 5 | 105 | 93.9 | 100.0 | 60 | 1000 | ok |
| yolo26-x_640x640.dxnn | 48.8 ±0.0 | 4 | 63 | 92.8 | 100.0 | 60 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n_640x640.dxnn | 9 | [3]:119.3 · [4]:155.6 · [5]:175.9 · [6]:206.2 · [7]:227.3 · [8]:236.8 · **[9]:243.3 ★** · [10]:243.1 · [11]:245.4 · [12]:245.1 |
| yolo26-s_640x640.dxnn | 9 | [3]:82.8 · [4]:120.3 · [5]:156.4 · [6]:174.5 · [7]:188.0 · [8]:195.4 · **[9]:198.9 ★** · [10]:199.5 · [11]:200.0 · [12]:200.2 |
| yolo26-m_640x640.dxnn | 6 | [3]:64.7 · [4]:90.4 · [5]:120.9 · **[6]:123.2 ★** · [7]:123.3 · [8]:123.4 · [9]:123.4 |
| yolo26-l_640x640.dxnn | 5 | [3]:54.6 · [4]:78.4 · **[5]:90.5 ★** · [6]:90.6 · [7]:90.6 · [8]:90.6 |
| yolo26-x_640x640.dxnn | 4 | [3]:35.4 · **[4]:48.5 ★** · [5]:48.7 · [6]:48.8 · [7]:48.8 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n_640x640.dxnn | 326.2 ±0.8 | 11 | 232 | 94.0 | 99.9 | 57~58 | 1000 | ok |
| yolo26-s_640x640.dxnn | 199.6 ±0.1 | 6 | 141 | 94.0 | 100.0 | 58 | 1000 | ok |
| yolo26-m_640x640.dxnn | 123.9 ±0.0 | 5 | 94 | 93.0 | 100.0 | 60 | 1000 | ok |
| yolo26-l_640x640.dxnn | 90.7 ±0.0 | 5 | 76 | 95.8 | 100.0 | 59~60 | 1000 | ok |
| yolo26-x_640x640.dxnn | 48.9 ±0.0 | 4 | 46 | 93.7 | 100.0 | 60 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n_640x640.dxnn | 11 | [3]:111.1 · [4]:158.8 · [5]:207.7 · [6]:234.1 · [7]:261.8 · [8]:295.5 · [9]:320.3 · [10]:326.7 · **[11]:327.7 ★** · [12]:330.1 · [13]:329.1 · [14]:328.8 · [15]:330.8 |
| yolo26-s_640x640.dxnn | 6 | [3]:86.5 · [4]:128.5 · [5]:176.5 · **[6]:198.6 ★** · [7]:199.9 · [8]:200.3 · [9]:200.4 |
| yolo26-m_640x640.dxnn | 5 | [3]:68.1 · [4]:102.4 · **[5]:123.5 ★** · [6]:123.6 · [7]:123.6 · [8]:123.7 |
| yolo26-l_640x640.dxnn | 5 | [3]:56.5 · [4]:85.1 · **[5]:90.5 ★** · [6]:90.5 · [7]:90.5 · [8]:90.5 |
| yolo26-x_640x640.dxnn | 4 | [3]:36.6 · **[4]:48.8 ★** · [5]:48.8 · [6]:48.9 · [7]:48.9 |


#### Pose Estimation

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 303.8 ±0.5 | 10 | 242 | 92.3 | 100.0 | 57 | 1000 | ok |
| yolo26-s-pose_640x640.dxnn | 183.9 ±0.1 | 6 | 133 | 94.5 | 100.0 | 58 | 1000 | ok |
| yolo26-m-pose_640x640.dxnn | 122.6 ±0.0 | 5 | 108 | 93.4 | 100.0 | 60 | 1000 | ok |
| yolo26-l-pose_640x640.dxnn | 89.3 ±0.0 | 5 | 79 | 96.0 | 100.0 | 59~60 | 1000 | ok |
| yolo26-x-pose_640x640.dxnn | 47.5 ±0.1 | 4 | 48 | 94.4 | 100.0 | 60 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-pose_640x640.dxnn | 10 | [3]:127.2 · [4]:182.0 · [5]:212.6 · [6]:235.3 · [7]:269.6 · [8]:295.1 · [9]:300.4 · **[10]:303.2 ★** · [11]:303.9 · [12]:304.0 · [13]:304.3 · [14]:304.4 |
| yolo26-s-pose_640x640.dxnn | 6 | [3]:92.3 · [4]:131.1 · [5]:176.5 · **[6]:183.7 ★** · [7]:183.9 · [8]:184.1 · [9]:184.2 |
| yolo26-m-pose_640x640.dxnn | 5 | [3]:72.0 · [4]:103.1 · **[5]:122.2 ★** · [6]:122.4 · [7]:122.5 · [8]:122.5 |
| yolo26-l-pose_640x640.dxnn | 5 | [3]:58.3 · [4]:84.9 · **[5]:89.1 ★** · [6]:89.2 · [7]:89.1 · [8]:89.1 |
| yolo26-x-pose_640x640.dxnn | 4 | [3]:37.0 · **[4]:47.4 ★** · [5]:47.5 · [6]:47.5 · [7]:47.5 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 305.3 ±0.0 | 7 | 153 | 95.3 | 100.0 | 57 | 1000 | ok |
| yolo26-s-pose_640x640.dxnn | 184.2 ±0.0 | 5 | 110 | 97.0 | 100.0 | 58 | 1000 | ok |
| yolo26-m-pose_640x640.dxnn | 122.7 ±0.0 | 5 | 75 | 97.9 | 100.0 | 60 | 1000 | ok |
| yolo26-l-pose_640x640.dxnn | 89.4 ±0.0 | 5 | 59 | 93.4 | 100.0 | 59 | 1000 | ok |
| yolo26-x-pose_640x640.dxnn | 47.6 ±0.0 | 4 | 36 | 95.4 | 100.0 | 60 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-pose_640x640.dxnn | 7 | [3]:131.6 · [4]:188.4 · [5]:255.8 · [6]:301.1 · **[7]:304.6 ★** · [8]:305.4 · [9]:305.5 · [10]:305.8 |
| yolo26-s-pose_640x640.dxnn | 5 | [3]:98.5 · [4]:145.1 · **[5]:183.7 ★** · [6]:183.9 · [7]:183.9 · [8]:184.0 |
| yolo26-m-pose_640x640.dxnn | 5 | [3]:75.4 · [4]:113.9 · **[5]:122.3 ★** · [6]:122.4 · [7]:122.5 · [8]:122.5 |
| yolo26-l-pose_640x640.dxnn | 5 | [3]:60.7 · [4]:87.5 · **[5]:89.2 ★** · [6]:89.2 · [7]:89.2 · [8]:89.2 |
| yolo26-x-pose_640x640.dxnn | 4 | [3]:37.9 · **[4]:47.5 ★** · [5]:47.5 · [6]:47.5 · [7]:47.5 |


#### Segmentation

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 138.1 ±0.6 | 15 | 349 | 45.4 | 77.5 | 56~57 | 1000 | ok |
| yolo26-s-seg_640x640.dxnn | 134.7 ±0.4 | 10 | 334 | 89.8 | 100.0 | 58~59 | 1000 | ok |
| yolo26-m-seg_640x640.dxnn | 77.1 ±0.9 | 8 | 147 | 93.9 | 100.0 | 61 | 1000 | ok |
| yolo26-l-seg_640x640.dxnn | 64.9 ±0.0 | 6 | 120 | 94.6 | 100.0 | 60~61 | 1000 | ok |
| yolo26-x-seg_640x640.dxnn | 34.3 ±0.3 | 6 | 70 | 91.7 | 100.0 | 61 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-seg_640x640.dxnn | 15 | [3]:77.0 · [4]:93.2 · [5]:106.4 · [6]:119.8 · [7]:127.0 · [8]:132.1 · [9]:133.3 · [10]:135.2 · [11]:136.0 · [12]:136.3 · [13]:137.8 · [14]:138.1 · **[15]:139.2 ★** · [16]:139.8 · [17]:139.8 · [18]:139.4 |
| yolo26-s-seg_640x640.dxnn | 10 | [3]:50.0 · [4]:81.7 · [5]:92.2 · [6]:107.1 · [7]:119.2 · [8]:126.9 · [9]:133.2 · **[10]:134.4 ★** · [11]:135.2 · [12]:135.2 · [13]:135.5 · [14]:135.4 |
| yolo26-m-seg_640x640.dxnn | 8 | [3]:36.6 · [4]:54.5 · [5]:74.4 · [6]:76.5 · [7]:77.3 · **[8]:78.3 ★** · [9]:77.7 · [10]:77.2 · [11]:76.5 |
| yolo26-l-seg_640x640.dxnn | 6 | [3]:33.4 · [4]:45.1 · [5]:63.2 · **[6]:64.7 ★** · [7]:64.7 · [8]:64.8 · [9]:64.8 |
| yolo26-x-seg_640x640.dxnn | 6 | [3]:23.7 · [4]:33.5 · [5]:33.9 · **[6]:34.2 ★** · [7]:34.5 · [8]:34.2 · [9]:34.1 · [10]:34.5 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 180.2 ±0.5 | 15 | 327 | 66.3 | 85.0 | 57 | 1000 | ok |
| yolo26-s-seg_640x640.dxnn | 138.1 ±0.1 | 8 | 237 | 93.6 | 100.0 | 58 | 1000 | ok |
| yolo26-m-seg_640x640.dxnn | 76.7 ±0.0 | 7 | 108 | 93.9 | 100.0 | 60~61 | 1000 | ok |
| yolo26-l-seg_640x640.dxnn | 65.0 ±0.0 | 6 | 94 | 94.3 | 100.0 | 60~61 | 1000 | ok |
| yolo26-x-seg_640x640.dxnn | 34.2 ±0.1 | 4 | 58 | 91.8 | 100.0 | 61 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-seg_640x640.dxnn | 15 | [3]:60.8 · [4]:97.8 · [5]:115.8 · [6]:139.0 · [7]:157.0 · [8]:167.9 · [9]:173.7 · [10]:176.6 · [11]:178.2 · [12]:179.5 · [13]:180.5 · [14]:180.6 · **[15]:182.4 ★** · [16]:181.7 · [17]:181.0 · [18]:179.5 |
| yolo26-s-seg_640x640.dxnn | 8 | [3]:47.4 · [4]:80.6 · [5]:103.9 · [6]:116.9 · [7]:132.2 · **[8]:137.1 ★** · [9]:137.6 · [10]:137.5 · [11]:137.9 |
| yolo26-m-seg_640x640.dxnn | 7 | [3]:36.2 · [4]:55.5 · [5]:75.8 · [6]:77.4 · **[7]:78.7 ★** · [8]:77.0 · [9]:76.5 · [10]:76.5 |
| yolo26-l-seg_640x640.dxnn | 6 | [3]:33.2 · [4]:50.9 · [5]:64.3 · **[6]:64.8 ★** · [7]:64.8 · [8]:64.9 · [9]:64.8 · [10]:64.9 · [11]:64.9 |
| yolo26-x-seg_640x640.dxnn | 4 | [3]:23.2 · **[4]:34.0 ★** · [5]:33.9 · [6]:34.2 · [7]:33.8 |


#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 107.1 ±0.0 | 5 | 99 | 94.0 | 100.0 | 57 | 1000 | ok |
| yolo26-s-obb_1024x1024.dxnn | 64.1 ±0.2 | 5 | 63 | 94.4 | 100.0 | 58 | 1000 | ok |
| yolo26-m-obb_1024x1024.dxnn | 42.4 ±0.3 | 4 | 45 | 92.9 | 100.0 | 60 | 1000 | ok |
| yolo26-l-obb_1024x1024.dxnn | 31.0 ±0.0 | 4 | 34 | 92.9 | 100.0 | 59~60 | 1000 | ok |
| yolo26-x-obb_1024x1024.dxnn | 17.0 ±0.0 | 4 | 20 | 90.6 | 100.0 | 60 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-obb_1024x1024.dxnn | 5 | [3]:65.6 · [4]:88.8 · **[5]:106.6 ★** · [6]:106.8 · [7]:106.9 · [8]:107.0 |
| yolo26-s-obb_1024x1024.dxnn | 5 | [3]:46.9 · [4]:60.2 · **[5]:63.8 ★** · [6]:63.6 · [7]:63.5 · [8]:63.6 |
| yolo26-m-obb_1024x1024.dxnn | 4 | [3]:34.5 · **[4]:42.4 ★** · [5]:42.4 · [6]:42.4 · [7]:42.4 |
| yolo26-l-obb_1024x1024.dxnn | 4 | [3]:27.0 · **[4]:30.8 ★** · [5]:30.8 · [6]:30.9 · [7]:30.9 |
| yolo26-x-obb_1024x1024.dxnn | 4 | [3]:15.4 · **[4]:16.9 ★** · [5]:16.9 · [6]:16.9 · [7]:16.9 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 107.2 ±0.0 | 5 | 69 | 97.1 | 100.0 | 57~58 | 1000 | ok |
| yolo26-s-obb_1024x1024.dxnn | 63.5 ±0.0 | 5 | 45 | 94.5 | 100.0 | 58 | 1000 | ok |
| yolo26-m-obb_1024x1024.dxnn | 42.6 ±0.0 | 4 | 32 | 95.6 | 100.0 | 60 | 1000 | ok |
| yolo26-l-obb_1024x1024.dxnn | 30.9 ±0.0 | 4 | 24 | 92.9 | 100.0 | 60 | 1000 | ok |
| yolo26-x-obb_1024x1024.dxnn | 17.0 ±0.0 | 4 | 14 | 90.9 | 100.0 | 60 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-obb_1024x1024.dxnn | 5 | [3]:66.9 · [4]:97.1 · **[5]:106.9 ★** · [6]:106.9 · [7]:107.0 · [8]:106.9 |
| yolo26-s-obb_1024x1024.dxnn | 5 | [3]:46.5 · [4]:61.7 · **[5]:63.3 ★** · [6]:63.3 · [7]:63.3 · [8]:63.3 |
| yolo26-m-obb_1024x1024.dxnn | 4 | [3]:32.8 · **[4]:42.4 ★** · [5]:42.4 · [6]:42.5 · [7]:42.4 |
| yolo26-l-obb_1024x1024.dxnn | 4 | [3]:25.5 · **[4]:30.8 ★** · [5]:30.8 · [6]:30.8 · [7]:30.8 |
| yolo26-x-obb_1024x1024.dxnn | 4 | [3]:15.1 · **[4]:16.9 ★** · [5]:16.9 · [6]:16.9 · [7]:16.9 |


#### Classification

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-cls-n_224x224.dxnn | 3512.5 ±8.2 | 9 | 86 | 91.8 | 95.8 | 56~57 | 1000 | ok |
| yolo26-cls-s_224x224.dxnn | 1958.0 ±3.8 | 5 | 60 | 92.8 | 97.9 | 57 | 1000 | ok |
| yolo26-cls-m_224x224.dxnn | 1381.8 ±1.3 | 4 | 40 | 92.9 | 98.3 | 59 | 1000 | ok |
| yolo26-cls-l_224x224.dxnn | 888.2 ±1.0 | 4 | 26 | 95.2 | 99.1 | 58 | 1000 | ok |
| yolo26-cls-x_224x224.dxnn | 496.5 ±0.1 | 4 | 15 | 96.0 | 99.6 | 59 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-cls-n_224x224.dxnn | 9 | [3]:1903.4 · [4]:2692.1 · [5]:3345.7 · [6]:3466.3 · [7]:3468.5 · [8]:3471.4 · **[9]:3522.7 ★** · [10]:3533.4 · [11]:3534.2 · [12]:3526.1 |
| yolo26-cls-s_224x224.dxnn | 5 | [3]:1345.4 · [4]:1855.2 · **[5]:1958.6 ★** · [6]:1961.6 · [7]:1959.8 · [8]:1970.4 |
| yolo26-cls-m_224x224.dxnn | 4 | [3]:1034.7 · **[4]:1381.2 ★** · [5]:1383.8 · [6]:1386.6 · [7]:1384.6 |
| yolo26-cls-l_224x224.dxnn | 4 | [3]:716.3 · **[4]:887.6 ★** · [5]:890.5 · [6]:886.9 · [7]:887.1 |
| yolo26-cls-x_224x224.dxnn | 4 | [3]:424.5 · **[4]:496.4 ★** · [5]:496.5 · [6]:496.6 · [7]:496.4 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-cls-n_224x224.dxnn | 3521.3 ±12.7 | 9 | 86 | 92.5 | 96.1 | 56~57 | 1000 | ok |
| yolo26-cls-s_224x224.dxnn | 1963.5 ±5.6 | 6 | 64 | 92.7 | 97.9 | 57 | 1000 | ok |
| yolo26-cls-m_224x224.dxnn | 1382.3 ±1.2 | 4 | 40 | 94.4 | 98.3 | 58~59 | 1000 | ok |
| yolo26-cls-l_224x224.dxnn | 888.9 ±0.4 | 4 | 26 | 94.7 | 99.2 | 58 | 1000 | ok |
| yolo26-cls-x_224x224.dxnn | 496.7 ±0.3 | 4 | 15 | 95.2 | 99.6 | 59 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-cls-n_224x224.dxnn | 9 | [3]:1896.6 · [4]:2699.2 · [5]:3343.3 · [6]:3451.3 · [7]:3470.6 · [8]:3468.1 · **[9]:3499.1 ★** · [10]:3499.3 · [11]:3505.7 · [12]:3482.4 |
| yolo26-cls-s_224x224.dxnn | 6 | [3]:1353.4 · [4]:1857.5 · [5]:1950.5 · **[6]:1962.2 ★** · [7]:1963.2 · [8]:1971.3 · [9]:1971.4 · [10]:1971.7 · [11]:1971.3 |
| yolo26-cls-m_224x224.dxnn | 4 | [3]:1033.6 · **[4]:1380.6 ★** · [5]:1381.7 · [6]:1380.6 · [7]:1385.0 |
| yolo26-cls-l_224x224.dxnn | 4 | [3]:717.0 · **[4]:887.7 ★** · [5]:889.4 · [6]:887.7 · [7]:890.1 |
| yolo26-cls-x_224x224.dxnn | 4 | [3]:425.9 · **[4]:496.2 ★** · [5]:496.3 · [6]:496.3 · [7]:496.2 |


### Latency (Single-Core, Sync)

#### Object Detection

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_640x640.dxnn | 41.0 | 24.39 | 23.05 | 1.34 | 45 | ok |
| yolo26-s_640x640.dxnn | 32.6 | 30.70 | 29.40 | 1.30 | 55 | ok |
| yolo26-m_640x640.dxnn | 26.0 | 38.52 | 37.17 | 1.35 | 55 | ok |
| yolo26-l_640x640.dxnn | 21.7 | 45.98 | 44.61 | 1.37 | 56 | ok |
| yolo26-x_640x640.dxnn | 14.1 | 71.11 | 69.75 | 1.36 | 56 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_640x640.dxnn | 42.9 | 23.32 | 23.32 | N/A | 55 | ok |
| yolo26-s_640x640.dxnn | 33.8 | 29.61 | 29.61 | N/A | 55 | ok |
| yolo26-m_640x640.dxnn | 27.3 | 36.67 | 36.67 | N/A | 56 | ok |
| yolo26-l_640x640.dxnn | 22.6 | 44.27 | 44.27 | N/A | 55 | ok |
| yolo26-x_640x640.dxnn | 14.3 | 69.84 | 69.84 | N/A | 56 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-pose_640x640.dxnn | 48.8 | 20.48 | 19.52 | 0.96 | 55 | ok |
| yolo26-s-pose_640x640.dxnn | 35.7 | 28.01 | 27.00 | 1.01 | 55 | ok |
| yolo26-m-pose_640x640.dxnn | 28.5 | 35.05 | 34.06 | 0.99 | 55 | ok |
| yolo26-l-pose_640x640.dxnn | 23.5 | 42.53 | 41.55 | 0.98 | 55 | ok |
| yolo26-x-pose_640x640.dxnn | 14.4 | 69.36 | 68.40 | 0.97 | 56 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-pose_640x640.dxnn | 49.3 | 20.29 | 20.29 | N/A | 55 | ok |
| yolo26-s-pose_640x640.dxnn | 37.2 | 26.88 | 26.88 | N/A | 55 | ok |
| yolo26-m-pose_640x640.dxnn | 29.2 | 34.25 | 34.25 | N/A | 55 | ok |
| yolo26-l-pose_640x640.dxnn | 23.9 | 41.82 | 41.82 | N/A | 56 | ok |
| yolo26-x-pose_640x640.dxnn | 14.6 | 68.40 | 68.40 | N/A | 56 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-seg_640x640.dxnn | 26.4 | 37.89 | 36.68 | 1.21 | 55 | ok |
| yolo26-s-seg_640x640.dxnn | 21.3 | 46.85 | 45.67 | 1.18 | 55 | ok |
| yolo26-m-seg_640x640.dxnn | 16.4 | 60.89 | 59.67 | 1.22 | 56 | ok |
| yolo26-l-seg_640x640.dxnn | 14.7 | 67.89 | 66.67 | 1.21 | 56 | ok |
| yolo26-x-seg_640x640.dxnn | 9.6 | 104.70 | 103.46 | 1.24 | 57 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-seg_640x640.dxnn | 27.3 | 36.58 | 36.58 | N/A | 55 | ok |
| yolo26-s-seg_640x640.dxnn | 22.1 | 45.21 | 45.21 | N/A | 55 | ok |
| yolo26-m-seg_640x640.dxnn | 16.8 | 59.41 | 59.41 | N/A | 56 | ok |
| yolo26-l-seg_640x640.dxnn | 15.0 | 66.74 | 66.74 | N/A | 56 | ok |
| yolo26-x-seg_640x640.dxnn | 9.6 | 104.21 | 104.21 | N/A | 57 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-obb_1024x1024.dxnn | 27.9 | 35.91 | 34.79 | 1.11 | 55 | ok |
| yolo26-s-obb_1024x1024.dxnn | 19.5 | 51.28 | 50.19 | 1.09 | 56 | ok |
| yolo26-m-obb_1024x1024.dxnn | 14.4 | 69.40 | 68.35 | 1.06 | 56 | ok |
| yolo26-l-obb_1024x1024.dxnn | 11.3 | 88.11 | 87.05 | 1.07 | 57 | ok |
| yolo26-x-obb_1024x1024.dxnn | 6.4 | 156.28 | 155.21 | 1.07 | 58 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-obb_1024x1024.dxnn | 28.5 | 35.09 | 35.09 | N/A | 55 | ok |
| yolo26-s-obb_1024x1024.dxnn | 19.9 | 50.34 | 50.34 | N/A | 56 | ok |
| yolo26-m-obb_1024x1024.dxnn | 14.6 | 68.28 | 68.28 | N/A | 57 | ok |
| yolo26-l-obb_1024x1024.dxnn | 11.5 | 86.97 | 86.97 | N/A | 57 | ok |
| yolo26-x-obb_1024x1024.dxnn | 6.4 | 155.07 | 155.07 | N/A | 58 | ok |

#### Classification

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-cls-n_224x224.dxnn | 695.7 | 1.44 | 1.44 | N/A | 55 | ok |
| yolo26-cls-s_224x224.dxnn | 480.0 | 2.08 | 2.08 | N/A | 54 | ok |
| yolo26-cls-m_224x224.dxnn | 372.9 | 2.68 | 2.68 | N/A | 55 | ok |
| yolo26-cls-l_224x224.dxnn | 254.9 | 3.92 | 3.92 | N/A | 55 | ok |
| yolo26-cls-x_224x224.dxnn | 147.5 | 6.78 | 6.78 | N/A | 55 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-cls-n_224x224.dxnn | 690.5 | 1.45 | 1.45 | N/A | 54 | ok |
| yolo26-cls-s_224x224.dxnn | 483.6 | 2.07 | 2.07 | N/A | 55 | ok |
| yolo26-cls-m_224x224.dxnn | 373.8 | 2.68 | 2.68 | N/A | 55 | ok |
| yolo26-cls-l_224x224.dxnn | 251.3 | 3.98 | 3.98 | N/A | 55 | ok |
| yolo26-cls-x_224x224.dxnn | 148.6 | 6.73 | 6.73 | N/A | 55 | ok |

## E2E Pipeline (Single-Stream)

### Object Detection

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | vah264dec | 3455 | 3 | 159.9 ±0.9 | 21.60 | 259 | 38.2 | 72.8 | 56~57 | 1000 | 282 | ok |
| yolo26-s_640x640.dxnn | vah264dec | 3455 | 3 | 139.3 ±0.4 | 24.80 | 238 | 61.8 | 81.8 | 58~59 | 1000 | 301 | ok |
| yolo26-m_640x640.dxnn | vah264dec | 3455 | 3 | 117.1 ±0.1 | 29.51 | 198 | 87.1 | 99.1 | 62~67 | 1000 | 336 | ok |
| yolo26-l_640x640.dxnn | vah264dec | 3455 | 3 | 90.6 ±0.1 | 38.14 | 136 | 89.7 | 100.0 | 63~69 | 1000 | 346 | ok |
| yolo26-x_640x640.dxnn | vah264dec | 3455 | 3 | 49.0 ±0.0 | 70.51 | 86 | 94.0 | 100.0 | 70~78 | 1000 | 440 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | vah264dec | 3455 | 3 | 178.0 ±0.1 | 19.41 | 277 | 41.9 | 75.3 | 57 | 1000 | 282 | ok |
| yolo26-s_640x640.dxnn | vah264dec | 3455 | 3 | 165.1 ±0.3 | 20.93 | 258 | 74.0 | 92.6 | 58~60 | 1000 | 312 | ok |
| yolo26-m_640x640.dxnn | vah264dec | 3455 | 3 | 121.3 ±0.4 | 28.48 | 221 | 89.0 | 100.0 | 62~67 | 1000 | 334 | ok |
| yolo26-l_640x640.dxnn | vah264dec | 3455 | 3 | 91.1 ±0.4 | 37.92 | 153 | 90.4 | 100.0 | 63~69 | 1000 | 345 | ok |
| yolo26-x_640x640.dxnn | vah264dec | 3455 | 3 | 49.0 ±0.1 | 70.50 | 95 | 94.2 | 100.0 | 69~79 | 1000 | 435 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n_640x640.dxnn | 159.9 | 178.0 | -18.1 | -10.2% |
| yolo26-s_640x640.dxnn | 139.3 | 165.1 | -25.7 | -15.6% |
| yolo26-m_640x640.dxnn | 117.1 | 121.3 | -4.2 | -3.5% |
| yolo26-l_640x640.dxnn | 90.6 | 91.1 | -0.5 | -0.6% |
| yolo26-x_640x640.dxnn | 49.0 | 49.0 | -0.0 | -0.0% |

### Pose Estimation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | vah264dec | 3455 | 3 | 170.6 ±1.2 | 20.25 | 234 | 42.3 | 76.1 | 57 | 1000 | 252 | ok |
| yolo26-s-pose_640x640.dxnn | vah264dec | 3455 | 3 | 158.4 ±0.6 | 21.82 | 226 | 72.0 | 92.8 | 58~60 | 1000 | 282 | ok |
| yolo26-m-pose_640x640.dxnn | vah264dec | 3455 | 3 | 120.0 ±0.3 | 28.79 | 146 | 88.9 | 100.0 | 62~67 | 1000 | 320 | ok |
| yolo26-l-pose_640x640.dxnn | vah264dec | 3455 | 3 | 89.4 ±0.2 | 38.66 | 117 | 91.6 | 100.0 | 63~68 | 1000 | 330 | ok |
| yolo26-x-pose_640x640.dxnn | vah264dec | 3455 | 3 | 47.8 ±0.1 | 72.34 | 71 | 95.0 | 100.0 | 69~79 | 1000 | 426 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | vah264dec | 3455 | 3 | 192.2 ±0.7 | 17.98 | 194 | 46.6 | 79.5 | 56~57 | 1000 | 222 | ok |
| yolo26-s-pose_640x640.dxnn | vah264dec | 3455 | 3 | 179.1 ±0.7 | 19.29 | 179 | 83.4 | 99.4 | 58~60 | 1000 | 271 | ok |
| yolo26-m-pose_640x640.dxnn | vah264dec | 3455 | 3 | 121.2 ±0.2 | 28.50 | 120 | 89.6 | 100.0 | 62~67 | 1000 | 298 | ok |
| yolo26-l-pose_640x640.dxnn | vah264dec | 3455 | 3 | 89.4 ±0.3 | 38.64 | 100 | 92.1 | 100.0 | 63~68 | 1000 | 313 | ok |
| yolo26-x-pose_640x640.dxnn | vah264dec | 3455 | 3 | 47.7 ±0.1 | 72.38 | 60 | 94.6 | 100.0 | 70~79 | 1000 | 408 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-pose_640x640.dxnn | 170.6 | 192.2 | -21.6 | -11.3% |
| yolo26-s-pose_640x640.dxnn | 158.4 | 179.1 | -20.7 | -11.6% |
| yolo26-m-pose_640x640.dxnn | 120.0 | 121.2 | -1.2 | -1.0% |
| yolo26-l-pose_640x640.dxnn | 89.4 | 89.4 | -0.0 | -0.1% |
| yolo26-x-pose_640x640.dxnn | 47.8 | 47.7 | +0.0 | +0.1% |

### Segmentation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | vah264dec | 3455 | 3 | 95.0 ±0.6 | 36.36 | 288 | 31.3 | 56.5 | 57~59 | 1000 | 417 | ok |
| yolo26-s-seg_640x640.dxnn | vah264dec | 3455 | 3 | 86.4 ±0.9 | 39.97 | 262 | 52.3 | 75.1 | 59~62 | 1000 | 430 | ok |
| yolo26-m-seg_640x640.dxnn | vah264dec | 3455 | 3 | 72.0 ±0.9 | 48.01 | 218 | 83.2 | 98.3 | 67~74 | 1000 | 462 | ok |
| yolo26-l-seg_640x640.dxnn | vah264dec | 3455 | 3 | 63.7 ±0.0 | 54.22 | 173 | 92.0 | 100.0 | 68~77 | 1000 | 474 | ok |
| yolo26-x-seg_640x640.dxnn | vah264dec | 3455 | 3 | 29.3 ±5.0 | 117.76 | 82 | 95.0 | 100.0 | 77~84 | 600~1000 | 578 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | vah264dec | 3455 | 3 | 106.5 ±0.7 | 32.44 | 316 | 36.0 | 60.9 | 57~59 | 1000 | 429 | ok |
| yolo26-s-seg_640x640.dxnn | vah264dec | 3455 | 3 | 97.4 ±0.3 | 35.48 | 278 | 59.9 | 80.1 | 59~63 | 1000 | 452 | ok |
| yolo26-m-seg_640x640.dxnn | vah264dec | 3455 | 3 | 76.3 ±0.4 | 45.30 | 211 | 90.5 | 100.0 | 67~75 | 1000 | 467 | ok |
| yolo26-l-seg_640x640.dxnn | vah264dec | 3455 | 3 | 64.5 ±0.1 | 53.54 | 173 | 93.1 | 100.0 | 68~77 | 1000 | 478 | ok |
| yolo26-x-seg_640x640.dxnn | vah264dec | 3455 | 3 | 30.5 ±3.8 | 113.20 | 84 | 94.7 | 100.0 | 77~85 | 600~1000 | 584 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-seg_640x640.dxnn | 95.0 | 106.5 | -11.5 | -10.8% |
| yolo26-s-seg_640x640.dxnn | 86.4 | 97.4 | -10.9 | -11.2% |
| yolo26-m-seg_640x640.dxnn | 72.0 | 76.3 | -4.3 | -5.7% |
| yolo26-l-seg_640x640.dxnn | 63.7 | 64.5 | -0.8 | -1.3% |
| yolo26-x-seg_640x640.dxnn | 29.3 | 30.5 | -1.2 | -3.9% |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | vah264dec | 2640 | 3 | 104.7 ±0.7 | 25.21 | 148 | 87.1 | 100.0 | 58~61 | 1000 | 315 | ok |
| yolo26-s-obb_1024x1024.dxnn | vah264dec | 2640 | 3 | 63.5 ±0.1 | 41.58 | 101 | 92.3 | 100.0 | 62~66 | 1000 | 345 | ok |
| yolo26-m-obb_1024x1024.dxnn | vah264dec | 2640 | 3 | 42.3 ±0.5 | 62.48 | 76 | 93.5 | 100.0 | 68~76 | 1000 | 372 | ok |
| yolo26-l-obb_1024x1024.dxnn | vah264dec | 2640 | 3 | 30.9 ±0.4 | 85.40 | 59 | 94.1 | 100.0 | 70~79 | 1000 | 386 | ok |
| yolo26-x-obb_1024x1024.dxnn | vah264dec | 2640 | 3 | 14.6 ±2.0 | 180.41 | 30 | 94.6 | 100.0 | 80~85 | 600~1000 | 486 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | vah264dec | 2640 | 3 | 105.3 ±0.8 | 25.07 | 148 | 88.1 | 100.0 | 58~61 | 1000 | 300 | ok |
| yolo26-s-obb_1024x1024.dxnn | vah264dec | 2640 | 3 | 63.5 ±0.0 | 41.57 | 105 | 92.4 | 100.0 | 61~66 | 1000 | 337 | ok |
| yolo26-m-obb_1024x1024.dxnn | vah264dec | 2640 | 3 | 42.3 ±0.6 | 62.45 | 79 | 92.8 | 100.0 | 68~77 | 1000 | 356 | ok |
| yolo26-l-obb_1024x1024.dxnn | vah264dec | 2640 | 3 | 31.0 ±0.2 | 85.25 | 62 | 94.2 | 100.0 | 71~79 | 1000 | 372 | ok |
| yolo26-x-obb_1024x1024.dxnn | vah264dec | 2640 | 3 | 14.5 ±2.1 | 181.90 | 30 | 94.8 | 100.0 | 81~84 | 400~1000 | 473 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-obb_1024x1024.dxnn | 104.7 | 105.3 | -0.6 | -0.5% |
| yolo26-s-obb_1024x1024.dxnn | 63.5 | 63.5 | -0.0 | -0.0% |
| yolo26-m-obb_1024x1024.dxnn | 42.3 | 42.3 | -0.0 | -0.0% |
| yolo26-l-obb_1024x1024.dxnn | 30.9 | 31.0 | -0.1 | -0.2% |
| yolo26-x-obb_1024x1024.dxnn | 14.6 | 14.5 | +0.1 | +0.8% |

### Classification

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-cls-n_224x224.dxnn | vah264dec | 3455 | 3 | 276.5 ±1.6 | 12.49 | 86 | 5.8 | 21.9 | 55 | 1000 | 112 | ok |
| yolo26-cls-s_224x224.dxnn | vah264dec | 3455 | 3 | 288.7 ±0.4 | 11.97 | 83 | 10.4 | 41.0 | 55 | 1000 | 124 | ok |
| yolo26-cls-m_224x224.dxnn | vah264dec | 3455 | 3 | 288.8 ±0.8 | 11.96 | 83 | 15.1 | 58.4 | 55 | 1000 | 141 | ok |
| yolo26-cls-l_224x224.dxnn | vah264dec | 3455 | 3 | 291.2 ±0.6 | 11.86 | 83 | 24.1 | 75.9 | 56 | 1000 | 150 | ok |
| yolo26-cls-x_224x224.dxnn | vah264dec | 3455 | 3 | 288.0 ±1.1 | 11.99 | 83 | 43.8 | 78.9 | 57 | 1000 | 216 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-cls-n_224x224.dxnn | vah264dec | 3455 | 3 | 276.7 ±0.8 | 12.49 | 86 | 5.7 | 21.6 | 55 | 1000 | 113 | ok |
| yolo26-cls-s_224x224.dxnn | vah264dec | 3455 | 3 | 288.4 ±1.0 | 11.98 | 83 | 10.6 | 41.2 | 55 | 1000 | 127 | ok |
| yolo26-cls-m_224x224.dxnn | vah264dec | 3455 | 3 | 288.4 ±0.4 | 11.98 | 83 | 14.9 | 58.4 | 55 | 1000 | 141 | ok |
| yolo26-cls-l_224x224.dxnn | vah264dec | 3455 | 3 | 291.6 ±0.6 | 11.85 | 83 | 24.4 | 75.2 | 55~56 | 1000 | 150 | ok |
| yolo26-cls-x_224x224.dxnn | vah264dec | 3455 | 3 | 288.6 ±1.4 | 11.97 | 83 | 42.3 | 78.4 | 57 | 1000 | 216 | ok |

> Classification has no CPU part, so ORT ON and OFF run the same model; differences between the two tables are measurement noise.

## E2E Pipeline (Multi-Stream)

### Object Detection

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | 5 | 3 | 162.3 ±0.8 | 32.5 | 275 | 43.3 | 69.4 | 61~65 | 1000 | 473 | ok |
| yolo26-n_640x640.dxnn | 6 | 3 | 162.0 ±0.4 | 27.0 | 275 | 43.5 | 68.1 | 67~68 | 1000 | 507 | ok |
| yolo26-s_640x640.dxnn | 4 | 3 | 143.0 ±0.3 | 35.7 | 248 | 69.0 | 84.2 | 66~71 | 1000 | 452 | ok |
| yolo26-s_640x640.dxnn | 5 | 3 | 144.1 ±0.8 | 28.8 | 250 | 70.0 | 85.8 | 72~75 | 1000 | 486 | ok |
| yolo26-m_640x640.dxnn | 3 | 3 | 109.6 ±8.9 | 36.5 | 184 | 93.3 | 100.0 | 78~84 | 600~1000 | 444 | ok |
| yolo26-m_640x640.dxnn | 4 | 3 | 86.1 ±0.8 | 21.5 | 145 | 96.4 | 100.0 | 84 | 400~800 | 480 | ok |
| yolo26-l_640x640.dxnn | 3 | 3 | 80.8 ±7.1 | 26.9 | 138 | 95.5 | 100.0 | 81~84 | 600~1000 | 455 | ok |
| yolo26-l_640x640.dxnn | 2 | 3 | 72.7 ±5.1 | 36.4 | 127 | 95.2 | 100.0 | 84~86 | 600~1000 | 417 | ok |
| yolo26-x_640x640.dxnn | 1 | 3 | 49.0 ±0.0 | 49.0 | 86 | 94.0 | 100.0 | 70~78 | 1000 | 440 | ok |
| yolo26-x_640x640.dxnn | 2 | 3 | 35.8 ±0.6 | 17.9 | 71 | 96.5 | 100.0 | 84 | 600~1000 | 510 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | 5 | 3 | 180.9 ±0.5 | 36.2 | 314 | 49.6 | 69.4 | 62~65 | 1000 | 499 | ok |
| yolo26-n_640x640.dxnn | 6 | 3 | 180.5 ±0.2 | 30.1 | 315 | 50.3 | 72.6 | 68~69 | 1000 | 538 | ok |
| yolo26-n_640x640.dxnn | 7 | 3 | 179.7 ±1.0 | 25.7 | 317 | 49.9 | 71.8 | 70 | 1000 | 579 | ok |
| yolo26-s_640x640.dxnn | 5 | 3 | 165.8 ±0.2 | 33.2 | 272 | 81.3 | 92.1 | 69~74 | 1000 | 515 | ok |
| yolo26-s_640x640.dxnn | 6 | 3 | 164.3 ±1.6 | 27.4 | 271 | 82.6 | 93.6 | 78~81 | 1000 | 558 | ok |
| yolo26-m_640x640.dxnn | 4 | 3 | 102.2 ±14.4 | 25.6 | 188 | 96.2 | 100.0 | 81~84 | 600~1000 | 490 | ok |
| yolo26-m_640x640.dxnn | 3 | 3 | 83.5 ±5.6 | 27.8 | 153 | 96.6 | 100.0 | 84~85 | 400~800 | 448 | ok |
| yolo26-m_640x640.dxnn | 2 | 3 | 88.2 ±0.7 | 44.1 | 158 | 95.0 | 100.0 | 84 | 600~1000 | 408 | ok |
| yolo26-l_640x640.dxnn | 3 | 3 | 78.6 ±8.7 | 26.2 | 145 | 95.9 | 100.0 | 81~84 | 600~1000 | 461 | ok |
| yolo26-l_640x640.dxnn | 2 | 3 | 68.9 ±0.5 | 34.5 | 130 | 95.6 | 100.0 | 84 | 600~800 | 423 | ok |
| yolo26-x_640x640.dxnn | 1 | 3 | 49.0 ±0.1 | 49.0 | 95 | 94.2 | 100.0 | 69~79 | 1000 | 435 | ok |
| yolo26-x_640x640.dxnn | 2 | 3 | 36.0 ±1.3 | 18.0 | 79 | 96.7 | 100.0 | 84 | 600~1000 | 516 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n_640x640.dxnn | 5 | 32.5 | 6 | 30.1 |
| yolo26-s_640x640.dxnn | 4 | 35.7 | 5 | 33.2 |
| yolo26-m_640x640.dxnn | 3 | 36.5 | 2 | 44.1 |
| yolo26-l_640x640.dxnn | 2 | 36.4 | 2 | 34.5 |
| yolo26-x_640x640.dxnn | 1 | 49.0 | 1 | 49.0 |

### Pose Estimation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 5 | 3 | 194.7 ±0.6 | 38.9 | 270 | 57.8 | 76.2 | 63~66 | 1000 | 458 | ok |
| yolo26-n-pose_640x640.dxnn | 6 | 3 | 194.9 ±0.2 | 32.5 | 269 | 57.8 | 78.5 | 69~71 | 1000 | 497 | ok |
| yolo26-n-pose_640x640.dxnn | 7 | 3 | 194.5 ±0.2 | 27.8 | 269 | 57.5 | 77.3 | 72 | 1000 | 529 | ok |
| yolo26-s-pose_640x640.dxnn | 5 | 3 | 162.2 ±0.3 | 32.5 | 240 | 84.2 | 94.6 | 68~73 | 1000 | 477 | ok |
| yolo26-s-pose_640x640.dxnn | 6 | 3 | 162.4 ±0.7 | 27.1 | 241 | 85.0 | 94.7 | 75~77 | 1000 | 516 | ok |
| yolo26-m-pose_640x640.dxnn | 4 | 3 | 105.3 ±13.3 | 26.3 | 149 | 95.8 | 100.0 | 81~84 | 600~1000 | 468 | ok |
| yolo26-m-pose_640x640.dxnn | 3 | 3 | 89.7 ±0.3 | 29.9 | 131 | 95.5 | 100.0 | 84 | 600~1000 | 429 | ok |
| yolo26-m-pose_640x640.dxnn | 2 | 3 | 90.9 ±1.2 | 45.5 | 134 | 94.0 | 100.0 | 84 | 600~800 | 389 | ok |
| yolo26-l-pose_640x640.dxnn | 2 | 3 | 86.6 ±3.0 | 43.3 | 127 | 95.6 | 100.0 | 77~82 | 800~1000 | 403 | ok |
| yolo26-l-pose_640x640.dxnn | 3 | 3 | 69.7 ±1.1 | 23.2 | 108 | 95.8 | 100.0 | 83~84 | 600~1000 | 443 | ok |
| yolo26-x-pose_640x640.dxnn | 1 | 3 | 47.8 ±0.1 | 47.8 | 71 | 95.0 | 100.0 | 69~79 | 1000 | 426 | ok |
| yolo26-x-pose_640x640.dxnn | 2 | 3 | 35.6 ±1.3 | 17.8 | 59 | 96.6 | 100.0 | 84 | 600~1000 | 498 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 6 | 3 | 233.8 ±0.5 | 39.0 | 254 | 71.1 | 85.2 | 63~67 | 1000 | 495 | ok |
| yolo26-n-pose_640x640.dxnn | 7 | 3 | 233.4 ±0.5 | 33.3 | 253 | 71.3 | 87.2 | 71~72 | 1000 | 526 | ok |
| yolo26-n-pose_640x640.dxnn | 8 | 3 | 233.1 ±0.6 | 29.1 | 253 | 71.7 | 84.9 | 74~75 | 1000 | 554 | ok |
| yolo26-s-pose_640x640.dxnn | 5 | 3 | 178.6 ±0.2 | 35.7 | 215 | 93.1 | 99.4 | 70~74 | 1000 | 467 | ok |
| yolo26-s-pose_640x640.dxnn | 6 | 3 | 176.3 ±2.6 | 29.4 | 210 | 92.8 | 100.0 | 78~80 | 1000 | 508 | ok |
| yolo26-m-pose_640x640.dxnn | 4 | 3 | 106.6 ±13.1 | 26.7 | 129 | 96.8 | 100.0 | 80~84 | 600~1000 | 456 | ok |
| yolo26-m-pose_640x640.dxnn | 3 | 3 | 91.9 ±0.6 | 30.6 | 114 | 95.6 | 100.0 | 84 | 600~1000 | 412 | ok |
| yolo26-l-pose_640x640.dxnn | 2 | 3 | 87.3 ±2.7 | 43.6 | 108 | 94.7 | 100.0 | 77~82 | 800~1000 | 384 | ok |
| yolo26-l-pose_640x640.dxnn | 3 | 3 | 72.6 ±3.1 | 24.2 | 93 | 96.2 | 100.0 | 84 | 600~1000 | 430 | ok |
| yolo26-x-pose_640x640.dxnn | 1 | 3 | 47.7 ±0.1 | 47.7 | 60 | 94.6 | 100.0 | 70~79 | 1000 | 408 | ok |
| yolo26-x-pose_640x640.dxnn | 2 | 3 | 34.4 ±1.0 | 17.2 | 49 | 96.5 | 100.0 | 84 | 600~1000 | 479 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-pose_640x640.dxnn | 6 | 32.5 | 7 | 33.3 |
| yolo26-s-pose_640x640.dxnn | 5 | 32.5 | 5 | 35.7 |
| yolo26-m-pose_640x640.dxnn | 2 | 45.5 | 3 | 30.6 |
| yolo26-l-pose_640x640.dxnn | 2 | 43.3 | 2 | 43.6 |
| yolo26-x-pose_640x640.dxnn | 1 | 47.8 | 1 | 47.7 |

### Segmentation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 3 | 3 | 94.9 ±0.1 | 31.6 | 294 | 32.5 | 57.4 | 62~65 | 1000 | 533 | ok |
| yolo26-n-seg_640x640.dxnn | 4 | 3 | 94.6 ±0.1 | 23.6 | 294 | 32.4 | 58.5 | 67~68 | 1000 | 570 | ok |
| yolo26-s-seg_640x640.dxnn | 2 | 3 | 86.6 ±0.9 | 43.3 | 266 | 54.9 | 75.7 | 68~71 | 1000 | 521 | ok |
| yolo26-s-seg_640x640.dxnn | 3 | 3 | 86.1 ±0.4 | 28.7 | 266 | 55.2 | 74.2 | 75~77 | 1000 | 556 | ok |
| yolo26-m-seg_640x640.dxnn | 2 | 3 | 52.3 ±7.5 | 26.2 | 150 | 93.7 | 100.0 | 84~85 | 400~1000 | 538 | ok |
| yolo26-m-seg_640x640.dxnn | 1 | 3 | 72.0 ±0.9 | 72.0 | 218 | 83.2 | 98.3 | 67~74 | 1000 | 462 | ok |
| yolo26-l-seg_640x640.dxnn | 2 | 3 | 45.0 ±3.6 | 22.5 | 126 | 95.9 | 100.0 | 84~86 | 400~1000 | 552 | ok |
| yolo26-l-seg_640x640.dxnn | 1 | 3 | 63.7 ±0.0 | 63.7 | 173 | 92.0 | 100.0 | 68~77 | 1000 | 474 | ok |
| yolo26-x-seg_640x640.dxnn | 1 | 3 | 29.3 ±5.0 | 29.3 | 82 | 95.0 | 100.0 | 77~84 | 600~1000 | 578 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 3 | 3 | 104.8 ±0.2 | 34.9 | 323 | 37.0 | 60.0 | 63~66 | 1000 | 561 | ok |
| yolo26-n-seg_640x640.dxnn | 4 | 3 | 104.7 ±0.1 | 26.2 | 323 | 36.7 | 62.5 | 69~70 | 1000 | 621 | ok |
| yolo26-s-seg_640x640.dxnn | 3 | 3 | 97.9 ±0.4 | 32.6 | 283 | 62.7 | 78.5 | 70~75 | 1000 | 587 | ok |
| yolo26-s-seg_640x640.dxnn | 4 | 3 | 97.4 ±0.3 | 24.4 | 283 | 63.2 | 80.2 | 76~79 | 1000 | 641 | ok |
| yolo26-m-seg_640x640.dxnn | 2 | 3 | 52.9 ±10.3 | 26.5 | 149 | 95.7 | 100.0 | 85 | 400~1000 | 559 | ok |
| yolo26-m-seg_640x640.dxnn | 1 | 3 | 76.3 ±0.4 | 76.3 | 211 | 90.5 | 100.0 | 67~75 | 1000 | 467 | ok |
| yolo26-l-seg_640x640.dxnn | 2 | 3 | 44.0 ±4.2 | 22.0 | 124 | 95.7 | 100.0 | 83~84 | 400~1000 | 566 | ok |
| yolo26-l-seg_640x640.dxnn | 1 | 3 | 64.5 ±0.1 | 64.5 | 173 | 93.1 | 100.0 | 68~77 | 1000 | 478 | ok |
| yolo26-x-seg_640x640.dxnn | 1 | 3 | 30.5 ±3.8 | 30.5 | 84 | 94.7 | 100.0 | 77~85 | 600~1000 | 584 | ok |
| yolo26-x-seg_640x640.dxnn | 2 | 3 | 21.2 ±2.2 | 10.6 | 63 | 96.0 | 100.0 | 82~85 | 400~800 | 675 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-seg_640x640.dxnn | 3 | 31.6 | 3 | 34.9 |
| yolo26-s-seg_640x640.dxnn | 2 | 43.3 | 3 | 32.6 |
| yolo26-m-seg_640x640.dxnn | 1 | 72.0 | 1 | 76.3 |
| yolo26-l-seg_640x640.dxnn | 1 | 63.7 | 1 | 64.5 |
| yolo26-x-seg_640x640.dxnn | < 1 | — | 1 | 30.5 |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 3 | 3 | 104.2 ±0.7 | 34.8 | 183 | 93.7 | 100.0 | 67~71 | 1000 | 435 | ok |
| yolo26-n-obb_1024x1024.dxnn | 4 | 3 | 104.7 ±0.5 | 26.2 | 183 | 95.1 | 100.0 | 75~78 | 1000 | 475 | ok |
| yolo26-s-obb_1024x1024.dxnn | 2 | 3 | 63.0 ±0.7 | 31.5 | 122 | 94.9 | 100.0 | 72~77 | 1000 | 411 | ok |
| yolo26-s-obb_1024x1024.dxnn | 3 | 3 | 58.9 ±0.9 | 19.6 | 114 | 95.8 | 100.0 | 80~81 | 1000 | 456 | ok |
| yolo26-m-obb_1024x1024.dxnn | 1 | 3 | 42.3 ±0.5 | 42.3 | 76 | 93.5 | 100.0 | 68~76 | 1000 | 372 | ok |
| yolo26-m-obb_1024x1024.dxnn | 2 | 3 | 31.5 ±3.9 | 15.8 | 67 | 95.9 | 100.0 | 84~85 | 400~1000 | 445 | ok |
| yolo26-l-obb_1024x1024.dxnn | 1 | 3 | 30.9 ±0.4 | 30.9 | 59 | 94.1 | 100.0 | 70~79 | 1000 | 386 | ok |
| yolo26-l-obb_1024x1024.dxnn | 2 | 3 | 23.9 ±0.7 | 11.9 | 51 | 96.8 | 100.0 | 84~85 | 400~800 | 461 | ok |
| yolo26-x-obb_1024x1024.dxnn | 1 | 3 | 14.6 ±2.0 | 14.6 | 30 | 94.6 | 100.0 | 80~85 | 600~1000 | 486 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 3 | 3 | 106.2 ±0.1 | 35.4 | 187 | 95.0 | 100.0 | 67~72 | 1000 | 423 | ok |
| yolo26-n-obb_1024x1024.dxnn | 4 | 3 | 104.9 ±1.3 | 26.2 | 188 | 95.4 | 100.0 | 76~78 | 1000 | 469 | ok |
| yolo26-s-obb_1024x1024.dxnn | 2 | 3 | 63.1 ±0.4 | 31.5 | 126 | 95.0 | 100.0 | 72~76 | 1000 | 402 | ok |
| yolo26-s-obb_1024x1024.dxnn | 3 | 3 | 59.1 ±0.8 | 19.7 | 119 | 96.4 | 100.0 | 80~81 | 1000 | 446 | ok |
| yolo26-m-obb_1024x1024.dxnn | 1 | 3 | 42.3 ±0.6 | 42.3 | 79 | 92.8 | 100.0 | 68~77 | 1000 | 356 | ok |
| yolo26-m-obb_1024x1024.dxnn | 2 | 3 | 32.6 ±2.1 | 16.3 | 71 | 95.6 | 100.0 | 84~85 | 400~1000 | 432 | ok |
| yolo26-l-obb_1024x1024.dxnn | 1 | 3 | 31.0 ±0.2 | 31.0 | 62 | 94.2 | 100.0 | 71~79 | 1000 | 372 | ok |
| yolo26-l-obb_1024x1024.dxnn | 2 | 3 | 24.1 ±0.3 | 12.1 | 53 | 97.0 | 100.0 | 84 | 600~1000 | 446 | ok |
| yolo26-x-obb_1024x1024.dxnn | 1 | 3 | 14.5 ±2.1 | 14.5 | 30 | 94.8 | 100.0 | 81~84 | 400~1000 | 473 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-obb_1024x1024.dxnn | 3 | 34.8 | 3 | 35.4 |
| yolo26-s-obb_1024x1024.dxnn | 2 | 31.5 | 2 | 31.5 |
| yolo26-m-obb_1024x1024.dxnn | 1 | 42.3 | 1 | 42.3 |
| yolo26-l-obb_1024x1024.dxnn | 1 | 30.9 | 1 | 31.0 |

---
*Report generated by dx-benchmark tool*
