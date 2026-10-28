# YOLO26 Benchmark Report

**Generated:** 2026-10-25 01:24:21 (UTC+00:00, local)

## Test Timing

| # | Type | Start | End | Duration |
|---|------|-------|-----|----------|
| 1 | run | 2026-10-22 06:29:33 | 2026-10-25 01:24:20 | 66h 54m 46s |

## Executive Summary

### Object Detection

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n_640x640.dxnn | ON | 28.67 | 157.5 | 140.7 | 4 |
| yolo26-n_640x640.dxnn | OFF | 33.77 | 296.6 | 94.7 | 3 |
| yolo26-s_640x640.dxnn | ON | 43.96 | 149.2 | 132.8 | 4 |
| yolo26-s_640x640.dxnn | OFF | 37.36 | 199.7 | 95.7 | 3 |
| yolo26-m_640x640.dxnn | ON | 51.45 | 123.3 | 113.8 | 2 |
| yolo26-m_640x640.dxnn | OFF | 51.41 | 123.2 | 95.2 | 2 |
| yolo26-l_640x640.dxnn | ON | 61.81 | 90.6 | 89.8 | 2 |
| yolo26-l_640x640.dxnn | OFF | 57.37 | 90.6 | 87.9 | 1 |
| yolo26-x_640x640.dxnn | ON | 96.80 | 48.9 | 39.6 | 1 |
| yolo26-x_640x640.dxnn | OFF | 96.76 | 48.9 | 39.1 | 1 |

### Pose Estimation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-pose_640x640.dxnn | ON | 24.03 | 246.4 | 190.1 | 6 |
| yolo26-n-pose_640x640.dxnn | OFF | 26.73 | 304.8 | 227.5 | 8 |
| yolo26-s-pose_640x640.dxnn | ON | 31.86 | 169.0 | 162.4 | 5 |
| yolo26-s-pose_640x640.dxnn | OFF | 34.74 | 181.7 | 180.0 | 5 |
| yolo26-m-pose_640x640.dxnn | ON | 45.61 | 122.0 | 120.2 | 2 |
| yolo26-m-pose_640x640.dxnn | OFF | 41.46 | 122.2 | 121.2 | 2 |
| yolo26-l-pose_640x640.dxnn | ON | 53.29 | 89.0 | 88.2 | 2 |
| yolo26-l-pose_640x640.dxnn | OFF | 50.12 | 87.5 | 89.5 | 2 |
| yolo26-x-pose_640x640.dxnn | ON | 90.09 | 47.6 | 38.2 | 1 |
| yolo26-x-pose_640x640.dxnn | OFF | 82.25 | 47.4 | 39.1 | 1 |

### Segmentation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-seg_640x640.dxnn | ON | 35.24 | 104.6 | 87.9 | 2 |
| yolo26-n-seg_640x640.dxnn | OFF | 34.08 | 160.4 | 79.0 | 2 |
| yolo26-s-seg_640x640.dxnn | ON | 48.08 | 99.8 | 81.0 | 2 |
| yolo26-s-seg_640x640.dxnn | OFF | 45.43 | 137.7 | 76.7 | 2 |
| yolo26-m-seg_640x640.dxnn | ON | 71.82 | 76.3 | 61.0 | 1 |
| yolo26-m-seg_640x640.dxnn | OFF | 55.04 | 78.3 | 65.5 | 1 |
| yolo26-l-seg_640x640.dxnn | ON | 67.35 | 64.7 | 52.8 | 1 |
| yolo26-l-seg_640x640.dxnn | OFF | 66.38 | 64.2 | 54.8 | 1 |
| yolo26-x-seg_640x640.dxnn | ON | 123.48 | 34.4 | 19.5 | — |
| yolo26-x-seg_640x640.dxnn | OFF | 109.34 | 34.1 | 19.6 | — |

### Oriented BBox (OBB)

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-obb_1024x1024.dxnn | ON | 47.47 | 107.1 | 104.6 | 3 |
| yolo26-n-obb_1024x1024.dxnn | OFF | 44.91 | 107.2 | 105.4 | 3 |
| yolo26-s-obb_1024x1024.dxnn | ON | 66.12 | 63.4 | 62.9 | 2 |
| yolo26-s-obb_1024x1024.dxnn | OFF | 64.96 | 63.4 | 62.9 | 2 |
| yolo26-m-obb_1024x1024.dxnn | ON | 85.39 | 41.5 | 38.9 | 1 |
| yolo26-m-obb_1024x1024.dxnn | OFF | 87.70 | 42.5 | 37.2 | 1 |
| yolo26-l-obb_1024x1024.dxnn | ON | 105.45 | 30.8 | 26.1 | — |
| yolo26-l-obb_1024x1024.dxnn | OFF | 107.92 | 30.9 | 25.8 | — |
| yolo26-x-obb_1024x1024.dxnn | ON | 184.48 | 17.0 | 11.0 | — |
| yolo26-x-obb_1024x1024.dxnn | OFF | 178.53 | 17.0 | 11.0 | — |

### Classification

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-cls-n_224x224.dxnn | ON | 2.01 | 3483.0 | 972.9 | — |
| yolo26-cls-n_224x224.dxnn | OFF | 1.48 | 3471.3 | 965.0 | — |
| yolo26-cls-s_224x224.dxnn | ON | 4.86 | 1967.8 | 971.8 | — |
| yolo26-cls-s_224x224.dxnn | OFF | 4.12 | 1970.9 | 988.2 | — |
| yolo26-cls-m_224x224.dxnn | ON | 2.73 | 1379.9 | 983.5 | — |
| yolo26-cls-m_224x224.dxnn | OFF | 2.76 | 1381.6 | 981.6 | — |
| yolo26-cls-l_224x224.dxnn | ON | 3.99 | 886.0 | 866.1 | — |
| yolo26-cls-l_224x224.dxnn | OFF | 3.90 | 887.5 | 870.0 | — |
| yolo26-cls-x_224x224.dxnn | ON | 6.68 | 496.4 | 489.2 | — |
| yolo26-cls-x_224x224.dxnn | OFF | 8.49 | 496.6 | 488.6 | — |

## Environment

| Item | Value |
|------|-------|
| Product | ROCK5B+ |
| Hostname | rock-5b-plus |
| OS | Debian GNU/Linux 12 (bookworm) |
| Kernel | 6.1.43-15-rk2312 |
| CPU | N/A |
| CPU Threads | 8 |
| CPU Governor | ondemand |
| RAM | 7.8 GiB |
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
| NPU PCIe | Gen3 X2 [01:00:00] |

### Tools

| Tool | Available | Version |
|------|-----------|---------|
| run_model | Yes | DXRT v3.5.0 run_model |
| dxrt-cli | Yes | DXRT v3.5.0 (build: 5.502926e) |
| gst-launch-1.0 | Yes | gst-launch-1.0 version 1.22.9 |
| gst-inspect-1.0 | Yes | gst-inspect-1.0 version 1.22.9 |
| time | Yes | unknown |
| ffprobe | Yes | ffprobe version 5.1.9-0+deb12u1 Copyright (c) 2007-2026 the ... |
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
| NPU Idle Temp (settled) | 49.0 °C |
| Cool-down Target | ≤ 55.0 °C |
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
| yolo26-n_640x640.dxnn | 157.5 ±2.5 | 5 | 196 | 40.0 | 64.1 | 60 | 1000 | ok |
| yolo26-s_640x640.dxnn | 149.2 ±4.8 | 5 | 186 | 72.6 | 79.7 | 62~63 | 1000 | ok |
| yolo26-m_640x640.dxnn | 123.3 ±0.0 | 7 | 158 | 93.0 | 100.0 | 69~70 | 1000 | ok |
| yolo26-l_640x640.dxnn | 90.6 ±0.1 | 6 | 105 | 94.1 | 100.0 | 69~70 | 1000 | ok |
| yolo26-x_640x640.dxnn | 48.9 ±0.0 | 5 | 63 | 92.8 | 100.0 | 70~71 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n_640x640.dxnn | 5 | [3]:120.0 · [4]:141.7 · **[5]:156.0 ★** · [6]:154.5 · [7]:151.6 · [8]:151.4 |
| yolo26-s_640x640.dxnn | 5 | [3]:94.5 · [4]:125.5 · **[5]:152.8 ★** · [6]:152.3 · [7]:149.1 · [8]:150.4 |
| yolo26-m_640x640.dxnn | 7 | [3]:74.7 · [4]:96.0 · [5]:116.9 · [6]:120.8 · **[7]:122.0 ★** · [8]:121.5 · [9]:121.7 · [10]:122.4 |
| yolo26-l_640x640.dxnn | 6 | [3]:62.1 · [4]:80.2 · [5]:89.0 · **[6]:89.6 ★** · [7]:89.7 · [8]:90.0 · [9]:90.0 · [10]:90.1 · [11]:90.1 |
| yolo26-x_640x640.dxnn | 5 | [3]:36.1 · [4]:47.8 · **[5]:48.4 ★** · [6]:48.7 · [7]:48.7 · [8]:48.8 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n_640x640.dxnn | 296.6 ±0.1 | 7 | 203 | 83.5 | 98.3 | 62 | 1000 | ok |
| yolo26-s_640x640.dxnn | 199.7 ±0.7 | 6 | 110 | 95.0 | 100.0 | 64~65 | 1000 | ok |
| yolo26-m_640x640.dxnn | 123.2 ±0.2 | 5 | 72 | 93.9 | 100.0 | 70 | 1000 | ok |
| yolo26-l_640x640.dxnn | 90.6 ±0.1 | 5 | 50 | 92.8 | 100.0 | 69 | 1000 | ok |
| yolo26-x_640x640.dxnn | 48.9 ±0.0 | 5 | 39 | 92.6 | 100.0 | 70~71 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n_640x640.dxnn | 7 | [3]:139.2 · [4]:195.1 · [5]:241.8 · [6]:283.5 · **[7]:325.5 ★** · [8]:326.8 · [9]:327.1 · [10]:319.1 |
| yolo26-s_640x640.dxnn | 6 | [3]:104.9 · [4]:147.8 · [5]:183.0 · **[6]:197.6 ★** · [7]:197.5 · [8]:197.7 · [9]:198.0 |
| yolo26-m_640x640.dxnn | 5 | [3]:84.8 · [4]:112.2 · **[5]:122.1 ★** · [6]:122.7 · [7]:123.0 · [8]:122.8 |
| yolo26-l_640x640.dxnn | 5 | [3]:66.2 · [4]:87.6 · **[5]:89.9 ★** · [6]:90.1 · [7]:90.2 · [8]:90.4 |
| yolo26-x_640x640.dxnn | 5 | [3]:39.8 · [4]:48.3 · **[5]:48.7 ★** · [6]:48.8 · [7]:48.8 · [8]:48.8 · [9]:48.8 · [10]:48.8 |


#### Pose Estimation

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 246.4 ±2.2 | 7 | 217 | 78.8 | 83.9 | 62 | 1000 | ok |
| yolo26-s-pose_640x640.dxnn | 169.0 ±3.3 | 5 | 141 | 86.4 | 97.7 | 64~65 | 1000 | ok |
| yolo26-m-pose_640x640.dxnn | 122.0 ±0.1 | 5 | 98 | 94.5 | 100.0 | 70 | 1000 | ok |
| yolo26-l-pose_640x640.dxnn | 89.0 ±0.2 | 5 | 74 | 94.4 | 100.0 | 69 | 1000 | ok |
| yolo26-x-pose_640x640.dxnn | 47.6 ±0.0 | 5 | 69 | 93.8 | 100.0 | 70 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-pose_640x640.dxnn | 7 | [3]:142.0 · [4]:186.4 · [5]:227.7 · [6]:237.3 · **[7]:245.3 ★** · [8]:245.8 · [9]:241.1 · [10]:237.2 |
| yolo26-s-pose_640x640.dxnn | 5 | [3]:109.6 · [4]:146.7 · **[5]:181.7 ★** · [6]:181.7 · [7]:182.6 · [8]:182.3 |
| yolo26-m-pose_640x640.dxnn | 5 | [3]:81.3 · [4]:110.0 · **[5]:121.3 ★** · [6]:121.7 · [7]:121.7 · [8]:122.0 |
| yolo26-l-pose_640x640.dxnn | 5 | [3]:62.7 · [4]:85.7 · **[5]:88.6 ★** · [6]:88.7 · [7]:88.7 · [8]:89.0 |
| yolo26-x-pose_640x640.dxnn | 5 | [3]:37.0 · [4]:46.5 · **[5]:47.2 ★** · [6]:47.5 · [7]:47.5 · [8]:47.5 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 304.8 ±0.6 | 6 | 128 | 95.2 | 100.0 | 63~64 | 1000 | ok |
| yolo26-s-pose_640x640.dxnn | 181.7 ±0.9 | 5 | 84 | 93.7 | 100.0 | 65 | 1000 | ok |
| yolo26-m-pose_640x640.dxnn | 122.2 ±0.1 | 5 | 70 | 94.2 | 100.0 | 70 | 1000 | ok |
| yolo26-l-pose_640x640.dxnn | 87.5 ±0.1 | 4 | 52 | 90.9 | 100.0 | 68~69 | 1000 | ok |
| yolo26-x-pose_640x640.dxnn | 47.4 ±0.3 | 4 | 47 | 93.0 | 100.0 | 70~71 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-pose_640x640.dxnn | 6 | [3]:146.7 · [4]:202.4 · [5]:266.2 · **[6]:301.6 ★** · [7]:302.9 · [8]:301.7 · [9]:303.8 |
| yolo26-s-pose_640x640.dxnn | 5 | [3]:116.9 · [4]:159.6 · **[5]:180.7 ★** · [6]:182.4 · [7]:181.6 · [8]:182.0 |
| yolo26-m-pose_640x640.dxnn | 5 | [3]:83.8 · [4]:115.3 · **[5]:121.3 ★** · [6]:121.8 · [7]:122.0 · [8]:122.0 |
| yolo26-l-pose_640x640.dxnn | 4 | [3]:69.1 · **[4]:88.3 ★** · [5]:88.8 · [6]:89.0 · [7]:89.0 |
| yolo26-x-pose_640x640.dxnn | 4 | [3]:39.1 · **[4]:47.1 ★** · [5]:47.3 · [6]:47.4 · [7]:47.5 |


#### Segmentation

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 104.6 ±3.9 | 5 | 242 | 31.5 | 88.8 | 59~60 | 1000 | ok |
| yolo26-s-seg_640x640.dxnn | 99.8 ±0.6 | 6 | 250 | 58.2 | 93.3 | 64 | 1000 | ok |
| yolo26-m-seg_640x640.dxnn | 76.3 ±0.2 | 6 | 174 | 94.1 | 100.0 | 71~72 | 1000 | ok |
| yolo26-l-seg_640x640.dxnn | 64.7 ±0.1 | 6 | 150 | 93.1 | 100.0 | 72 | 1000 | ok |
| yolo26-x-seg_640x640.dxnn | 34.4 ±0.4 | 6 | 76 | 91.8 | 100.0 | 73 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-seg_640x640.dxnn | 5 | [3]:76.4 · [4]:97.1 · **[5]:104.3 ★** · [6]:103.1 · [7]:104.9 · [8]:99.3 |
| yolo26-s-seg_640x640.dxnn | 6 | [3]:60.4 · [4]:77.4 · [5]:94.9 · **[6]:103.0 ★** · [7]:102.9 · [8]:103.2 · [9]:99.3 |
| yolo26-m-seg_640x640.dxnn | 6 | [3]:46.2 · [4]:60.0 · [5]:72.4 · **[6]:76.2 ★** · [7]:76.2 · [8]:76.2 · [9]:75.5 |
| yolo26-l-seg_640x640.dxnn | 6 | [3]:41.5 · [4]:52.4 · [5]:62.3 · **[6]:63.9 ★** · [7]:64.0 · [8]:64.2 · [9]:64.3 |
| yolo26-x-seg_640x640.dxnn | 6 | [3]:24.9 · [4]:32.5 · [5]:33.5 · **[6]:34.0 ★** · [7]:34.2 · [8]:34.2 · [9]:34.0 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 160.4 ±14.7 | 7 | 209 | 54.2 | 93.1 | 61~62 | 1000 | ok |
| yolo26-s-seg_640x640.dxnn | 137.7 ±0.2 | 10 | 183 | 95.1 | 100.0 | 66~67 | 1000 | ok |
| yolo26-m-seg_640x640.dxnn | 78.3 ±1.3 | 6 | 91 | 93.5 | 100.0 | 72 | 1000 | ok |
| yolo26-l-seg_640x640.dxnn | 64.2 ±0.2 | 5 | 93 | 92.5 | 100.0 | 71 | 1000 | ok |
| yolo26-x-seg_640x640.dxnn | 34.1 ±0.2 | 5 | 55 | 92.4 | 100.0 | 72~73 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-seg_640x640.dxnn | 7 | [3]:91.2 · [4]:108.2 · [5]:130.2 · [6]:136.8 · **[7]:139.4 ★** · [8]:138.8 · [9]:137.4 · [10]:140.2 |
| yolo26-s-seg_640x640.dxnn | 10 | [3]:73.0 · [4]:90.4 · [5]:108.6 · [6]:125.7 · [7]:133.5 · [8]:134.5 · [9]:134.3 · **[10]:135.3 ★** · [11]:135.6 · [12]:135.3 · [13]:135.8 |
| yolo26-m-seg_640x640.dxnn | 6 | [3]:50.5 · [4]:66.1 · [5]:75.5 · **[6]:76.8 ★** · [7]:77.0 · [8]:76.3 · [9]:75.9 |
| yolo26-l-seg_640x640.dxnn | 5 | [3]:46.0 · [4]:59.4 · **[5]:63.8 ★** · [6]:64.3 · [7]:64.4 · [8]:64.3 |
| yolo26-x-seg_640x640.dxnn | 5 | [3]:26.7 · [4]:33.1 · **[5]:34.1 ★** · [6]:33.9 · [7]:34.2 · [8]:34.0 |


#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 107.1 ±0.0 | 6 | 96 | 95.9 | 100.0 | 63~64 | 1000 | ok |
| yolo26-s-obb_1024x1024.dxnn | 63.4 ±0.0 | 5 | 69 | 94.1 | 100.0 | 65 | 1000 | ok |
| yolo26-m-obb_1024x1024.dxnn | 41.5 ±0.2 | 4 | 60 | 92.5 | 100.0 | 69 | 1000 | ok |
| yolo26-l-obb_1024x1024.dxnn | 30.8 ±0.0 | 4 | 48 | 91.9 | 100.0 | 69 | 1000 | ok |
| yolo26-x-obb_1024x1024.dxnn | 17.0 ±0.0 | 4 | 43 | 90.8 | 100.0 | 70~71 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-obb_1024x1024.dxnn | 6 | [3]:73.7 · [4]:92.9 · [5]:105.3 · **[6]:106.1 ★** · [7]:106.0 · [8]:106.3 · [9]:106.3 · [10]:106.5 · [11]:106.5 |
| yolo26-s-obb_1024x1024.dxnn | 5 | [3]:47.7 · [4]:60.8 · **[5]:62.9 ★** · [6]:63.1 · [7]:63.1 · [8]:63.2 |
| yolo26-m-obb_1024x1024.dxnn | 4 | [3]:33.0 · **[4]:42.1 ★** · [5]:42.2 · [6]:42.3 · [7]:42.3 |
| yolo26-l-obb_1024x1024.dxnn | 4 | [3]:25.9 · **[4]:30.5 ★** · [5]:30.8 · [6]:30.8 · [7]:30.8 |
| yolo26-x-obb_1024x1024.dxnn | 4 | [3]:14.3 · **[4]:16.8 ★** · [5]:16.9 · [6]:16.9 · [7]:16.9 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 107.2 ±0.1 | 6 | 54 | 95.2 | 100.0 | 63 | 1000 | ok |
| yolo26-s-obb_1024x1024.dxnn | 63.4 ±0.0 | 5 | 42 | 94.9 | 100.0 | 65 | 1000 | ok |
| yolo26-m-obb_1024x1024.dxnn | 42.5 ±0.0 | 5 | 50 | 93.8 | 100.0 | 69~70 | 1000 | ok |
| yolo26-l-obb_1024x1024.dxnn | 30.9 ±0.1 | 4 | 37 | 92.1 | 100.0 | 68~69 | 1000 | ok |
| yolo26-x-obb_1024x1024.dxnn | 17.0 ±0.0 | 4 | 28 | 90.9 | 100.0 | 70 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-obb_1024x1024.dxnn | 6 | [3]:78.0 · [4]:96.9 · [5]:105.7 · **[6]:106.6 ★** · [7]:106.9 · [8]:106.8 · [9]:107.0 · [10]:106.9 |
| yolo26-s-obb_1024x1024.dxnn | 5 | [3]:45.1 · [4]:62.4 · **[5]:63.1 ★** · [6]:63.1 · [7]:63.2 · [8]:63.1 |
| yolo26-m-obb_1024x1024.dxnn | 5 | [3]:31.6 · [4]:41.9 · **[5]:42.3 ★** · [6]:42.4 · [7]:42.4 · [8]:42.4 |
| yolo26-l-obb_1024x1024.dxnn | 4 | [3]:26.8 · **[4]:30.7 ★** · [5]:30.8 · [6]:30.9 · [7]:30.9 |
| yolo26-x-obb_1024x1024.dxnn | 4 | [3]:14.8 · **[4]:16.9 ★** · [5]:16.9 · [6]:16.9 · [7]:16.9 |


#### Classification

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-cls-n_224x224.dxnn | 3483.0 ±16.6 | 7 | 98 | 90.2 | 96.2 | 60~61 | 1000 | ok |
| yolo26-cls-s_224x224.dxnn | 1967.8 ±5.2 | 6 | 59 | 92.8 | 98.0 | 62 | 1000 | ok |
| yolo26-cls-m_224x224.dxnn | 1379.9 ±5.3 | 6 | 44 | 93.0 | 98.5 | 66 | 1000 | ok |
| yolo26-cls-l_224x224.dxnn | 886.0 ±0.3 | 5 | 34 | 93.2 | 99.2 | 64~65 | 1000 | ok |
| yolo26-cls-x_224x224.dxnn | 496.4 ±0.1 | 5 | 33 | 95.0 | 99.5 | 66~67 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-cls-n_224x224.dxnn | 7 | [3]:2009.1 · [4]:2670.8 · [5]:3305.0 · [6]:3484.1 · **[7]:3506.1 ★** · [8]:3525.1 · [9]:3461.2 · [10]:3458.6 · [11]:3532.4 |
| yolo26-cls-s_224x224.dxnn | 6 | [3]:1359.9 · [4]:1829.9 · [5]:1902.9 · **[6]:1950.1 ★** · [7]:1921.3 · [8]:1952.5 · [9]:1968.1 |
| yolo26-cls-m_224x224.dxnn | 6 | [3]:740.3 · [4]:1354.0 · [5]:1368.9 · **[6]:1375.0 ★** · [7]:1387.4 · [8]:1379.1 · [9]:1383.9 · [10]:1378.9 |
| yolo26-cls-l_224x224.dxnn | 5 | [3]:461.1 · [4]:866.8 · **[5]:883.5 ★** · [6]:889.7 · [7]:889.2 · [8]:890.5 |
| yolo26-cls-x_224x224.dxnn | 5 | [3]:314.0 · [4]:449.7 · **[5]:495.9 ★** · [6]:496.4 · [7]:496.5 · [8]:496.4 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-cls-n_224x224.dxnn | 3471.3 ±46.6 | 8 | 101 | 90.9 | 96.0 | 60~61 | 1000 | ok |
| yolo26-cls-s_224x224.dxnn | 1970.9 ±1.5 | 8 | 60 | 92.1 | 98.0 | 62~63 | 1000 | ok |
| yolo26-cls-m_224x224.dxnn | 1381.6 ±4.9 | 6 | 45 | 94.8 | 98.5 | 66 | 1000 | ok |
| yolo26-cls-l_224x224.dxnn | 887.5 ±0.7 | 5 | 32 | 93.9 | 99.1 | 64~65 | 1000 | ok |
| yolo26-cls-x_224x224.dxnn | 496.6 ±0.3 | 5 | 32 | 93.9 | 99.8 | 67 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-cls-n_224x224.dxnn | 8 | [3]:2005.7 · [4]:2669.8 · [5]:3306.2 · [6]:3431.6 · [7]:3439.8 · **[8]:3504.8 ★** · [9]:3488.8 · [10]:3522.7 · [11]:3451.8 |
| yolo26-cls-s_224x224.dxnn | 8 | [3]:1379.3 · [4]:1830.7 · [5]:1910.1 · [6]:1937.8 · [7]:1928.2 · **[8]:1949.5 ★** · [9]:1967.4 · [10]:1957.3 · [11]:1968.5 · [12]:1968.2 |
| yolo26-cls-m_224x224.dxnn | 6 | [3]:721.0 · [4]:1342.6 · [5]:1364.4 · **[6]:1375.2 ★** · [7]:1386.3 · [8]:1384.0 · [9]:1381.9 · [10]:1383.8 |
| yolo26-cls-l_224x224.dxnn | 5 | [3]:465.8 · [4]:861.4 · **[5]:882.6 ★** · [6]:889.3 · [7]:889.9 · [8]:890.1 |
| yolo26-cls-x_224x224.dxnn | 5 | [3]:311.7 · [4]:444.7 · **[5]:495.8 ★** · [6]:496.1 · [7]:496.1 · [8]:496.1 |


### Latency (Single-Core, Sync)

#### Object Detection

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_640x640.dxnn | 34.9 | 28.67 | 25.84 | 2.83 | 51 | ok |
| yolo26-s_640x640.dxnn | 22.7 | 43.96 | 40.85 | 3.12 | 57 | ok |
| yolo26-m_640x640.dxnn | 19.4 | 51.45 | 48.02 | 3.43 | 58 | ok |
| yolo26-l_640x640.dxnn | 16.2 | 61.81 | 56.82 | 4.99 | 59 | ok |
| yolo26-x_640x640.dxnn | 10.3 | 96.80 | 91.69 | 5.11 | 60 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_640x640.dxnn | 29.6 | 33.77 | 33.77 | N/A | 57 | ok |
| yolo26-s_640x640.dxnn | 26.8 | 37.36 | 37.36 | N/A | 58 | ok |
| yolo26-m_640x640.dxnn | 19.5 | 51.41 | 51.41 | N/A | 58 | ok |
| yolo26-l_640x640.dxnn | 17.4 | 57.37 | 57.37 | N/A | 58 | ok |
| yolo26-x_640x640.dxnn | 10.3 | 96.76 | 96.76 | N/A | 60 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-pose_640x640.dxnn | 41.6 | 24.03 | 22.03 | 2.00 | 57 | ok |
| yolo26-s-pose_640x640.dxnn | 31.4 | 31.86 | 29.50 | 2.35 | 58 | ok |
| yolo26-m-pose_640x640.dxnn | 21.9 | 45.61 | 42.86 | 2.75 | 59 | ok |
| yolo26-l-pose_640x640.dxnn | 18.8 | 53.29 | 50.35 | 2.93 | 59 | ok |
| yolo26-x-pose_640x640.dxnn | 11.1 | 90.09 | 87.06 | 3.03 | 60 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-pose_640x640.dxnn | 37.4 | 26.73 | 26.73 | N/A | 57 | ok |
| yolo26-s-pose_640x640.dxnn | 28.8 | 34.74 | 34.74 | N/A | 58 | ok |
| yolo26-m-pose_640x640.dxnn | 24.1 | 41.46 | 41.46 | N/A | 59 | ok |
| yolo26-l-pose_640x640.dxnn | 20.0 | 50.12 | 50.12 | N/A | 59 | ok |
| yolo26-x-pose_640x640.dxnn | 12.2 | 82.25 | 82.25 | N/A | 60 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-seg_640x640.dxnn | 28.4 | 35.24 | 32.43 | 2.81 | 57 | ok |
| yolo26-s-seg_640x640.dxnn | 20.8 | 48.08 | 44.45 | 3.64 | 58 | ok |
| yolo26-m-seg_640x640.dxnn | 13.9 | 71.82 | 60.51 | 11.31 | 59 | ok |
| yolo26-l-seg_640x640.dxnn | 14.8 | 67.35 | 63.06 | 4.29 | 60 | ok |
| yolo26-x-seg_640x640.dxnn | 8.1 | 123.48 | 117.55 | 5.93 | 61 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-seg_640x640.dxnn | 29.3 | 34.08 | 34.08 | N/A | 57 | ok |
| yolo26-s-seg_640x640.dxnn | 22.0 | 45.43 | 45.43 | N/A | 58 | ok |
| yolo26-m-seg_640x640.dxnn | 18.2 | 55.04 | 55.04 | N/A | 60 | ok |
| yolo26-l-seg_640x640.dxnn | 15.1 | 66.38 | 66.38 | N/A | 60 | ok |
| yolo26-x-seg_640x640.dxnn | 9.1 | 109.34 | 109.34 | N/A | 62 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-obb_1024x1024.dxnn | 21.1 | 47.47 | 43.67 | 3.80 | 58 | ok |
| yolo26-s-obb_1024x1024.dxnn | 15.1 | 66.12 | 62.52 | 3.60 | 59 | ok |
| yolo26-m-obb_1024x1024.dxnn | 11.7 | 85.39 | 81.58 | 3.81 | 60 | ok |
| yolo26-l-obb_1024x1024.dxnn | 9.5 | 105.45 | 101.47 | 3.97 | 61 | ok |
| yolo26-x-obb_1024x1024.dxnn | 5.4 | 184.48 | 180.56 | 3.93 | 63 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-obb_1024x1024.dxnn | 22.3 | 44.91 | 44.91 | N/A | 58 | ok |
| yolo26-s-obb_1024x1024.dxnn | 15.4 | 64.96 | 64.96 | N/A | 59 | ok |
| yolo26-m-obb_1024x1024.dxnn | 11.4 | 87.70 | 87.70 | N/A | 60 | ok |
| yolo26-l-obb_1024x1024.dxnn | 9.3 | 107.92 | 107.92 | N/A | 61 | ok |
| yolo26-x-obb_1024x1024.dxnn | 5.6 | 178.53 | 178.53 | N/A | 63 | ok |

#### Classification

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-cls-n_224x224.dxnn | 497.7 | 2.01 | 2.01 | N/A | 57 | ok |
| yolo26-cls-s_224x224.dxnn | 205.7 | 4.86 | 4.86 | N/A | 56 | ok |
| yolo26-cls-m_224x224.dxnn | 365.7 | 2.73 | 2.73 | N/A | 56 | ok |
| yolo26-cls-l_224x224.dxnn | 250.7 | 3.99 | 3.99 | N/A | 57 | ok |
| yolo26-cls-x_224x224.dxnn | 149.6 | 6.68 | 6.68 | N/A | 57 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-cls-n_224x224.dxnn | 677.7 | 1.48 | 1.48 | N/A | 57 | ok |
| yolo26-cls-s_224x224.dxnn | 242.8 | 4.12 | 4.12 | N/A | 56 | ok |
| yolo26-cls-m_224x224.dxnn | 362.3 | 2.76 | 2.76 | N/A | 57 | ok |
| yolo26-cls-l_224x224.dxnn | 256.4 | 3.90 | 3.90 | N/A | 56 | ok |
| yolo26-cls-x_224x224.dxnn | 117.8 | 8.49 | 8.49 | N/A | 57 | ok |

## E2E Pipeline (Single-Stream)

### Object Detection

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | mppvideodec | 3455 | 3 | 140.7 ±0.8 | 24.55 | 243 | 35.8 | 61.8 | 60~62 | 1000 | 222 | ok |
| yolo26-s_640x640.dxnn | mppvideodec | 3455 | 3 | 132.8 ±0.6 | 26.02 | 220 | 58.5 | 76.2 | 63~66 | 1000 | 243 | ok |
| yolo26-m_640x640.dxnn | mppvideodec | 3455 | 3 | 113.8 ±0.6 | 30.37 | 188 | 82.0 | 97.7 | 72~77 | 1000 | 275 | ok |
| yolo26-l_640x640.dxnn | mppvideodec | 3455 | 3 | 89.8 ±1.5 | 38.46 | 140 | 89.5 | 100.0 | 75~80 | 800~1000 | 290 | ok |
| yolo26-x_640x640.dxnn | mppvideodec | 3455 | 3 | 39.6 ±5.1 | 87.27 | 69 | 93.8 | 100.0 | 80~85 | 600~1000 | 416 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | mppvideodec | 3455 | 3 | 94.7 ±0.4 | 36.50 | 189 | 21.3 | 70.9 | 59~60 | 1000 | 235 | ok |
| yolo26-s_640x640.dxnn | mppvideodec | 3455 | 3 | 95.7 ±0.1 | 36.09 | 206 | 40.1 | 67.0 | 62~65 | 1000 | 258 | ok |
| yolo26-m_640x640.dxnn | mppvideodec | 3455 | 3 | 95.2 ±0.3 | 36.31 | 201 | 68.7 | 76.5 | 70~75 | 1000 | 290 | ok |
| yolo26-l_640x640.dxnn | mppvideodec | 3455 | 3 | 87.9 ±3.5 | 39.29 | 183 | 89.4 | 100.0 | 73~81 | 800~1000 | 299 | ok |
| yolo26-x_640x640.dxnn | mppvideodec | 3455 | 3 | 39.1 ±5.6 | 88.25 | 96 | 93.6 | 100.0 | 81~84 | 600~1000 | 402 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n_640x640.dxnn | 140.7 | 94.7 | +46.1 | +48.7% |
| yolo26-s_640x640.dxnn | 132.8 | 95.7 | +37.0 | +38.7% |
| yolo26-m_640x640.dxnn | 113.8 | 95.2 | +18.6 | +19.5% |
| yolo26-l_640x640.dxnn | 89.8 | 87.9 | +1.9 | +2.2% |
| yolo26-x_640x640.dxnn | 39.6 | 39.1 | +0.4 | +1.1% |

### Pose Estimation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 190.1 ±0.9 | 18.17 | 234 | 50.5 | 79.0 | 61~63 | 1000 | 204 | ok |
| yolo26-s-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 162.4 ±1.0 | 21.28 | 195 | 72.8 | 92.8 | 65~67 | 1000 | 226 | ok |
| yolo26-m-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 120.2 ±1.7 | 28.75 | 137 | 86.5 | 100.0 | 73~79 | 800~1000 | 259 | ok |
| yolo26-l-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 88.2 ±2.0 | 39.17 | 98 | 91.0 | 100.0 | 75~79 | 800~1000 | 274 | ok |
| yolo26-x-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 38.2 ±5.6 | 90.54 | 64 | 94.3 | 100.0 | 81~83 | 400~1000 | 416 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 227.5 ±2.5 | 15.19 | 194 | 56.5 | 87.3 | 62~63 | 1000 | 191 | ok |
| yolo26-s-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 180.0 ±0.5 | 19.20 | 149 | 83.8 | 100.0 | 65~68 | 1000 | 214 | ok |
| yolo26-m-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 121.2 ±0.4 | 28.51 | 104 | 87.7 | 100.0 | 72~77 | 800~1000 | 247 | ok |
| yolo26-l-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 89.5 ±0.3 | 38.59 | 80 | 91.0 | 100.0 | 74~80 | 1000 | 262 | ok |
| yolo26-x-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 39.1 ±5.2 | 88.25 | 59 | 94.6 | 100.0 | 80~84 | 600~1000 | 399 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-pose_640x640.dxnn | 190.1 | 227.5 | -37.4 | -16.4% |
| yolo26-s-pose_640x640.dxnn | 162.4 | 180.0 | -17.6 | -9.8% |
| yolo26-m-pose_640x640.dxnn | 120.2 | 121.2 | -1.0 | -0.8% |
| yolo26-l-pose_640x640.dxnn | 88.2 | 89.5 | -1.3 | -1.5% |
| yolo26-x-pose_640x640.dxnn | 38.2 | 39.1 | -1.0 | -2.5% |

### Segmentation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 87.9 ±0.7 | 39.30 | 314 | 30.0 | 52.2 | 61~63 | 1000 | 342 | ok |
| yolo26-s-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 81.0 ±0.3 | 42.65 | 279 | 49.2 | 81.6 | 66~69 | 1000 | 365 | ok |
| yolo26-m-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 61.0 ±6.9 | 56.67 | 209 | 83.0 | 100.0 | 78~83 | 400~1000 | 402 | ok |
| yolo26-l-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 52.8 ±6.3 | 65.39 | 181 | 90.9 | 100.0 | 80~85 | 400~1000 | 413 | ok |
| yolo26-x-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 19.5 ±3.1 | 176.96 | 73 | 94.2 | 100.0 | 83~84 | 400~1000 | 523 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 79.0 ±2.0 | 43.71 | 274 | 22.5 | 75.7 | 60~62 | 1000 | 371 | ok |
| yolo26-s-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 76.7 ±2.2 | 45.02 | 255 | 43.3 | 74.2 | 65~69 | 1000 | 394 | ok |
| yolo26-m-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 65.5 ±9.3 | 52.73 | 231 | 89.1 | 100.0 | 79~83 | 400~1000 | 418 | ok |
| yolo26-l-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 54.8 ±5.8 | 63.04 | 184 | 92.9 | 100.0 | 80~85 | 600~1000 | 425 | ok |
| yolo26-x-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 19.6 ±3.6 | 176.42 | 78 | 94.8 | 100.0 | 83~84 | 400~1000 | 530 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-seg_640x640.dxnn | 87.9 | 79.0 | +8.9 | +11.2% |
| yolo26-s-seg_640x640.dxnn | 81.0 | 76.7 | +4.3 | +5.6% |
| yolo26-m-seg_640x640.dxnn | 61.0 | 65.5 | -4.5 | -6.9% |
| yolo26-l-seg_640x640.dxnn | 52.8 | 54.8 | -2.0 | -3.6% |
| yolo26-x-seg_640x640.dxnn | 19.5 | 19.6 | -0.1 | -0.3% |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 104.6 ±0.6 | 25.25 | 156 | 82.3 | 100.0 | 64~67 | 1000 | 257 | ok |
| yolo26-s-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 62.9 ±0.5 | 41.95 | 95 | 90.8 | 100.0 | 69~74 | 1000 | 281 | ok |
| yolo26-m-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 38.9 ±3.0 | 67.88 | 72 | 94.0 | 100.0 | 78~83 | 600~1000 | 314 | ok |
| yolo26-l-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 26.1 ±3.8 | 101.34 | 62 | 93.5 | 100.0 | 81~84 | 400~1000 | 330 | ok |
| yolo26-x-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 11.0 ±0.7 | 239.49 | 41 | 94.8 | 100.0 | 82~84 | 400~1000 | 441 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 105.4 ±0.8 | 25.06 | 155 | 87.6 | 100.0 | 65~67 | 1000 | 260 | ok |
| yolo26-s-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 62.9 ±0.4 | 41.96 | 100 | 90.8 | 100.0 | 69~75 | 1000 | 277 | ok |
| yolo26-m-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 37.2 ±4.6 | 70.88 | 78 | 93.4 | 100.0 | 79~83 | 400~1000 | 310 | ok |
| yolo26-l-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 25.8 ±4.5 | 102.21 | 63 | 94.5 | 100.0 | 81~84 | 400~1000 | 324 | ok |
| yolo26-x-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 11.0 ±1.1 | 240.12 | 39 | 94.0 | 100.0 | 83~84 | 400~1000 | 427 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-obb_1024x1024.dxnn | 104.6 | 105.4 | -0.8 | -0.8% |
| yolo26-s-obb_1024x1024.dxnn | 62.9 | 62.9 | +0.0 | +0.0% |
| yolo26-m-obb_1024x1024.dxnn | 38.9 | 37.2 | +1.6 | +4.4% |
| yolo26-l-obb_1024x1024.dxnn | 26.1 | 25.8 | +0.2 | +0.9% |
| yolo26-x-obb_1024x1024.dxnn | 11.0 | 11.0 | +0.0 | +0.3% |

### Classification

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-cls-n_224x224.dxnn | mppvideodec | 3455 | 3 | 972.9 ±33.8 | 3.55 | 150 | 12.3 | 43.1 | 57 | 1000 | 89 | ok |
| yolo26-cls-s_224x224.dxnn | mppvideodec | 3455 | 3 | 971.8 ±30.2 | 3.56 | 150 | 22.8 | 63.8 | 58 | 1000 | 103 | ok |
| yolo26-cls-m_224x224.dxnn | mppvideodec | 3455 | 3 | 983.5 ±28.1 | 3.51 | 149 | 31.1 | 80.1 | 59~61 | 1000 | 127 | ok |
| yolo26-cls-l_224x224.dxnn | mppvideodec | 3455 | 3 | 866.1 ±4.1 | 3.99 | 134 | 56.6 | 99.2 | 60~61 | 1000 | 140 | ok |
| yolo26-cls-x_224x224.dxnn | mppvideodec | 3455 | 3 | 489.2 ±3.5 | 7.06 | 101 | 67.6 | 99.5 | 63~65 | 1000 | 216 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-cls-n_224x224.dxnn | mppvideodec | 3455 | 3 | 965.0 ±25.1 | 3.58 | 153 | 11.1 | 44.9 | 57 | 1000 | 89 | ok |
| yolo26-cls-s_224x224.dxnn | mppvideodec | 3455 | 3 | 988.2 ±11.5 | 3.50 | 152 | 23.1 | 63.2 | 58 | 1000 | 103 | ok |
| yolo26-cls-m_224x224.dxnn | mppvideodec | 3455 | 3 | 981.6 ±18.0 | 3.52 | 151 | 26.9 | 80.4 | 59~60 | 1000 | 127 | ok |
| yolo26-cls-l_224x224.dxnn | mppvideodec | 3455 | 3 | 870.0 ±3.4 | 3.97 | 135 | 56.5 | 99.1 | 60~61 | 1000 | 140 | ok |
| yolo26-cls-x_224x224.dxnn | mppvideodec | 3455 | 3 | 488.6 ±3.9 | 7.07 | 108 | 67.9 | 99.6 | 63~65 | 1000 | 216 | ok |

> Classification has no CPU part, so ORT ON and OFF run the same model; differences between the two tables are measurement noise.

## E2E Pipeline (Multi-Stream)

### Object Detection

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | 4 | 3 | 138.8 ±1.4 | 34.7 | 258 | 38.5 | 61.7 | 67~69 | 1000 | 245 | ok |
| yolo26-n_640x640.dxnn | 5 | 3 | 139.6 ±0.2 | 27.9 | 258 | 38.8 | 62.3 | 71~72 | 1000 | 250 | ok |
| yolo26-s_640x640.dxnn | 4 | 3 | 131.7 ±0.2 | 32.9 | 229 | 63.1 | 80.5 | 74~76 | 1000 | 266 | ok |
| yolo26-s_640x640.dxnn | 5 | 3 | 131.6 ±0.5 | 26.3 | 229 | 62.8 | 79.0 | 80~81 | 1000 | 270 | ok |
| yolo26-m_640x640.dxnn | 3 | 3 | 79.9 ±8.2 | 26.6 | 128 | 96.0 | 100.0 | 84 | 400~800 | 293 | ok |
| yolo26-m_640x640.dxnn | 2 | 3 | 73.2 ±1.1 | 36.6 | 117 | 95.4 | 100.0 | 84 | 400~800 | 286 | ok |
| yolo26-l_640x640.dxnn | 2 | 3 | 61.7 ±4.2 | 30.9 | 98 | 95.4 | 100.0 | 84~85 | 400~1000 | 300 | ok |
| yolo26-l_640x640.dxnn | 3 | 3 | 54.8 ±0.6 | 18.3 | 86 | 96.0 | 100.0 | 83~84 | 400~800 | 307 | ok |
| yolo26-x_640x640.dxnn | 1 | 3 | 39.6 ±5.1 | 39.6 | 69 | 93.8 | 100.0 | 80~85 | 600~1000 | 416 | ok |
| yolo26-x_640x640.dxnn | 2 | 3 | 28.6 ±1.0 | 14.3 | 65 | 95.9 | 100.0 | 83~84 | 400~1000 | 416 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | 3 | 3 | 95.3 ±0.2 | 31.8 | 198 | 22.6 | 71.2 | 63~65 | 1000 | 259 | ok |
| yolo26-n_640x640.dxnn | 4 | 3 | 95.5 ±0.1 | 23.9 | 203 | 22.7 | 71.3 | 66~67 | 1000 | 267 | ok |
| yolo26-s_640x640.dxnn | 3 | 3 | 95.7 ±0.2 | 31.9 | 210 | 42.4 | 67.1 | 69~71 | 1000 | 281 | ok |
| yolo26-s_640x640.dxnn | 4 | 3 | 95.7 ±0.0 | 23.9 | 207 | 42.7 | 67.1 | 73~74 | 1000 | 289 | ok |
| yolo26-m_640x640.dxnn | 3 | 3 | 75.2 ±6.7 | 25.1 | 158 | 95.9 | 100.0 | 83~84 | 400~1000 | 309 | ok |
| yolo26-m_640x640.dxnn | 2 | 3 | 69.0 ±1.4 | 34.5 | 141 | 94.6 | 100.0 | 84~85 | 400~1000 | 298 | ok |
| yolo26-l_640x640.dxnn | 2 | 3 | 58.7 ±2.8 | 29.3 | 124 | 95.6 | 100.0 | 83~84 | 400~800 | 312 | ok |
| yolo26-l_640x640.dxnn | 1 | 3 | 87.9 ±3.5 | 87.9 | 183 | 89.4 | 100.0 | 73~81 | 800~1000 | 299 | ok |
| yolo26-x_640x640.dxnn | 1 | 3 | 39.1 ±5.6 | 39.1 | 96 | 93.6 | 100.0 | 81~84 | 600~1000 | 402 | ok |
| yolo26-x_640x640.dxnn | 2 | 3 | 28.6 ±0.3 | 14.3 | 83 | 96.0 | 100.0 | 84 | 400~800 | 402 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n_640x640.dxnn | 4 | 34.7 | 3 | 31.8 |
| yolo26-s_640x640.dxnn | 4 | 32.9 | 3 | 31.9 |
| yolo26-m_640x640.dxnn | 2 | 36.6 | 2 | 34.5 |
| yolo26-l_640x640.dxnn | 2 | 30.9 | 1 | 87.9 |
| yolo26-x_640x640.dxnn | 1 | 39.6 | 1 | 39.1 |

### Pose Estimation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 6 | 3 | 190.4 ±1.5 | 31.7 | 245 | 57.3 | 80.0 | 70~74 | 1000 | 243 | ok |
| yolo26-n-pose_640x640.dxnn | 7 | 3 | 189.3 ±0.8 | 27.1 | 248 | 57.1 | 79.5 | 76 | 1000 | 247 | ok |
| yolo26-s-pose_640x640.dxnn | 5 | 3 | 165.0 ±1.2 | 33.0 | 203 | 86.2 | 98.8 | 79~83 | 800~1000 | 260 | ok |
| yolo26-s-pose_640x640.dxnn | 6 | 3 | 146.9 ±7.0 | 24.5 | 181 | 92.8 | 100.0 | 84~85 | 600~1000 | 266 | ok |
| yolo26-m-pose_640x640.dxnn | 4 | 3 | 70.3 ±1.7 | 17.6 | 88 | 96.8 | 100.0 | 84 | 400~1000 | 288 | ok |
| yolo26-m-pose_640x640.dxnn | 3 | 3 | 71.4 ±13.3 | 23.8 | 91 | 96.5 | 100.0 | 84~88 | 400~1000 | 280 | ok |
| yolo26-m-pose_640x640.dxnn | 2 | 3 | 68.5 ±1.9 | 34.2 | 86 | 95.4 | 100.0 | 84 | 400~800 | 272 | ok |
| yolo26-l-pose_640x640.dxnn | 2 | 3 | 61.5 ±6.9 | 30.7 | 78 | 95.5 | 100.0 | 83~85 | 400~1000 | 287 | ok |
| yolo26-l-pose_640x640.dxnn | 3 | 3 | 58.0 ±6.3 | 19.3 | 76 | 96.5 | 100.0 | 83~86 | 400~1000 | 295 | ok |
| yolo26-x-pose_640x640.dxnn | 1 | 3 | 38.2 ±5.6 | 38.2 | 64 | 94.3 | 100.0 | 81~83 | 400~1000 | 416 | ok |
| yolo26-x-pose_640x640.dxnn | 2 | 3 | 28.7 ±1.1 | 14.3 | 57 | 96.1 | 100.0 | 82~83 | 400~800 | 416 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 7 | 3 | 246.0 ±2.6 | 35.1 | 219 | 76.6 | 88.8 | 72~76 | 1000 | 242 | ok |
| yolo26-n-pose_640x640.dxnn | 8 | 3 | 245.0 ±0.8 | 30.6 | 225 | 76.8 | 88.3 | 79~81 | 1000 | 249 | ok |
| yolo26-n-pose_640x640.dxnn | 9 | 3 | 248.1 ±2.2 | 27.6 | 215 | 77.4 | 91.2 | 81~82 | 1000 | 253 | ok |
| yolo26-s-pose_640x640.dxnn | 5 | 3 | 176.6 ±5.8 | 35.3 | 160 | 93.2 | 100.0 | 78~83 | 800~1000 | 254 | ok |
| yolo26-s-pose_640x640.dxnn | 6 | 3 | 151.7 ±1.9 | 25.3 | 136 | 94.4 | 100.0 | 84 | 600~1000 | 261 | ok |
| yolo26-m-pose_640x640.dxnn | 4 | 3 | 76.8 ±2.8 | 19.2 | 78 | 96.7 | 100.0 | 84 | 400~1000 | 280 | ok |
| yolo26-m-pose_640x640.dxnn | 3 | 3 | 70.1 ±1.4 | 23.4 | 75 | 95.9 | 100.0 | 83~84 | 400~600 | 269 | ok |
| yolo26-m-pose_640x640.dxnn | 2 | 3 | 73.0 ±1.6 | 36.5 | 75 | 94.3 | 100.0 | 83~84 | 400~800 | 261 | ok |
| yolo26-l-pose_640x640.dxnn | 2 | 3 | 62.8 ±7.6 | 31.4 | 68 | 95.5 | 100.0 | 83~85 | 400~1000 | 277 | ok |
| yolo26-l-pose_640x640.dxnn | 3 | 3 | 57.4 ±4.6 | 19.1 | 67 | 96.5 | 100.0 | 82~84 | 400~800 | 284 | ok |
| yolo26-x-pose_640x640.dxnn | 1 | 3 | 39.1 ±5.2 | 39.1 | 59 | 94.6 | 100.0 | 80~84 | 600~1000 | 399 | ok |
| yolo26-x-pose_640x640.dxnn | 2 | 3 | 29.0 ±1.5 | 14.5 | 52 | 96.7 | 100.0 | 82~83 | 400~800 | 399 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-pose_640x640.dxnn | 6 | 31.7 | 8 | 30.6 |
| yolo26-s-pose_640x640.dxnn | 5 | 33.0 | 5 | 35.3 |
| yolo26-m-pose_640x640.dxnn | 2 | 34.2 | 2 | 36.5 |
| yolo26-l-pose_640x640.dxnn | 2 | 30.7 | 2 | 31.4 |
| yolo26-x-pose_640x640.dxnn | 1 | 38.2 | 1 | 39.1 |

### Segmentation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 2 | 3 | 88.8 ±1.3 | 44.4 | 314 | 31.4 | 52.3 | 67~69 | 1000 | 364 | ok |
| yolo26-n-seg_640x640.dxnn | 3 | 3 | 88.5 ±0.0 | 29.5 | 323 | 31.6 | 52.9 | 72 | 1000 | 374 | ok |
| yolo26-s-seg_640x640.dxnn | 2 | 3 | 82.0 ±1.6 | 41.0 | 280 | 51.2 | 81.2 | 76~80 | 1000 | 390 | ok |
| yolo26-s-seg_640x640.dxnn | 3 | 3 | 81.4 ±0.2 | 27.1 | 286 | 51.2 | 82.2 | 82~84 | 800~1000 | 397 | ok |
| yolo26-m-seg_640x640.dxnn | 2 | 3 | 40.0 ±1.3 | 20.0 | 133 | 95.5 | 100.0 | 85 | 300~600 | 422 | ok |
| yolo26-m-seg_640x640.dxnn | 1 | 3 | 61.0 ±6.9 | 61.0 | 209 | 83.0 | 100.0 | 78~83 | 400~1000 | 402 | ok |
| yolo26-l-seg_640x640.dxnn | 1 | 3 | 52.8 ±6.3 | 52.8 | 181 | 90.9 | 100.0 | 80~85 | 400~1000 | 413 | ok |
| yolo26-l-seg_640x640.dxnn | 2 | 3 | 34.0 ±0.6 | 17.0 | 108 | 96.4 | 100.0 | 85 | 400~800 | 434 | ok |
| yolo26-x-seg_640x640.dxnn | 1 | 3 | 19.5 ±3.1 | 19.5 | 73 | 94.2 | 100.0 | 83~84 | 400~1000 | 523 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 2 | 3 | 79.8 ±0.6 | 39.9 | 268 | 23.2 | 75.8 | 66~68 | 1000 | 394 | ok |
| yolo26-n-seg_640x640.dxnn | 3 | 3 | 80.2 ±0.1 | 26.7 | 277 | 23.7 | 76.7 | 69~70 | 1000 | 408 | ok |
| yolo26-s-seg_640x640.dxnn | 2 | 3 | 75.6 ±1.9 | 37.8 | 270 | 44.0 | 73.9 | 75~78 | 1000 | 418 | ok |
| yolo26-s-seg_640x640.dxnn | 3 | 3 | 77.8 ±0.3 | 25.9 | 267 | 45.0 | 76.3 | 81~82 | 1000 | 432 | ok |
| yolo26-m-seg_640x640.dxnn | 2 | 3 | 40.9 ±0.5 | 20.4 | 132 | 96.0 | 100.0 | 85~86 | 300~600 | 450 | ok |
| yolo26-m-seg_640x640.dxnn | 1 | 3 | 65.5 ±9.3 | 65.5 | 231 | 89.1 | 100.0 | 79~83 | 400~1000 | 418 | ok |
| yolo26-l-seg_640x640.dxnn | 1 | 3 | 54.8 ±5.8 | 54.8 | 184 | 92.9 | 100.0 | 80~85 | 600~1000 | 425 | ok |
| yolo26-l-seg_640x640.dxnn | 2 | 3 | 33.7 ±0.1 | 16.9 | 105 | 97.1 | 100.0 | 84~85 | 300~600 | 453 | ok |
| yolo26-x-seg_640x640.dxnn | 1 | 3 | 19.6 ±3.6 | 19.6 | 78 | 94.8 | 100.0 | 83~84 | 400~1000 | 530 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-seg_640x640.dxnn | 2 | 44.4 | 2 | 39.9 |
| yolo26-s-seg_640x640.dxnn | 2 | 41.0 | 2 | 37.8 |
| yolo26-m-seg_640x640.dxnn | 1 | 61.0 | 1 | 65.5 |
| yolo26-l-seg_640x640.dxnn | 1 | 52.8 | 1 | 54.8 |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 3 | 3 | 104.3 ±0.7 | 34.8 | 165 | 92.0 | 100.0 | 74~79 | 1000 | 285 | ok |
| yolo26-n-obb_1024x1024.dxnn | 4 | 3 | 104.1 ±0.8 | 26.0 | 166 | 93.5 | 100.0 | 82~84 | 1000 | 293 | ok |
| yolo26-s-obb_1024x1024.dxnn | 2 | 3 | 62.0 ±1.9 | 31.0 | 95 | 94.3 | 100.0 | 81~84 | 800~1000 | 296 | ok |
| yolo26-s-obb_1024x1024.dxnn | 3 | 3 | 53.6 ±0.3 | 17.9 | 88 | 95.9 | 100.0 | 84~85 | 600~1000 | 308 | ok |
| yolo26-m-obb_1024x1024.dxnn | 1 | 3 | 38.9 ±3.0 | 38.9 | 72 | 94.0 | 100.0 | 78~83 | 600~1000 | 314 | ok |
| yolo26-m-obb_1024x1024.dxnn | 2 | 3 | 26.5 ±0.1 | 13.2 | 65 | 96.0 | 100.0 | 83~84 | 400~800 | 327 | ok |
| yolo26-l-obb_1024x1024.dxnn | 1 | 3 | 26.1 ±3.8 | 26.1 | 62 | 93.5 | 100.0 | 81~84 | 400~1000 | 330 | ok |
| yolo26-x-obb_1024x1024.dxnn | 1 | 3 | 11.0 ±0.7 | 11.0 | 41 | 94.8 | 100.0 | 82~84 | 400~1000 | 441 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 3 | 3 | 105.4 ±0.8 | 35.1 | 160 | 93.6 | 100.0 | 74~78 | 1000 | 289 | ok |
| yolo26-n-obb_1024x1024.dxnn | 4 | 3 | 105.3 ±1.0 | 26.3 | 164 | 95.4 | 100.0 | 82~84 | 1000 | 300 | ok |
| yolo26-s-obb_1024x1024.dxnn | 2 | 3 | 62.6 ±0.8 | 31.3 | 104 | 94.6 | 100.0 | 81~84 | 800~1000 | 293 | ok |
| yolo26-s-obb_1024x1024.dxnn | 3 | 3 | 53.2 ±0.4 | 17.8 | 93 | 96.0 | 100.0 | 84~85 | 600~1000 | 306 | ok |
| yolo26-m-obb_1024x1024.dxnn | 1 | 3 | 37.2 ±4.6 | 37.2 | 78 | 93.4 | 100.0 | 79~83 | 400~1000 | 310 | ok |
| yolo26-m-obb_1024x1024.dxnn | 2 | 3 | 25.1 ±0.0 | 12.5 | 65 | 97.1 | 100.0 | 84 | 400~600 | 323 | ok |
| yolo26-l-obb_1024x1024.dxnn | 1 | 3 | 25.8 ±4.5 | 25.8 | 63 | 94.5 | 100.0 | 81~84 | 400~1000 | 324 | ok |
| yolo26-x-obb_1024x1024.dxnn | 1 | 3 | 11.0 ±1.1 | 11.0 | 39 | 94.0 | 100.0 | 83~84 | 400~1000 | 427 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-obb_1024x1024.dxnn | 3 | 34.8 | 3 | 35.1 |
| yolo26-s-obb_1024x1024.dxnn | 2 | 31.0 | 2 | 31.3 |
| yolo26-m-obb_1024x1024.dxnn | 1 | 38.9 | 1 | 37.2 |

---
*Report generated by dx-benchmark tool*
