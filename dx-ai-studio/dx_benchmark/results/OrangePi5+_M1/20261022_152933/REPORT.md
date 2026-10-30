# YOLO26 Benchmark Report

**Generated:** 2026-10-26 09:40:54 (UTC+09:00, local)

## Test Timing

| # | Type | Start | End | Duration |
|---|------|-------|-----|----------|
| 1 | run | 2026-10-22 15:29:33 | 2026-10-24 18:01:28 | 50h 31m 55s |
| 2 | retry-failed | 2026-10-26 09:30:21 | 2026-10-26 09:40:54 | 10m 32s |

## Executive Summary

### Object Detection

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n_640x640.dxnn | ON | 37.84 | 178.3 | 149.2 | 4 |
| yolo26-n_640x640.dxnn | OFF | 36.53 | 324.2 | 95.0 | 3 |
| yolo26-s_640x640.dxnn | ON | 47.32 | 179.9 | 127.1 | 4 |
| yolo26-s_640x640.dxnn | OFF | 52.30 | 200.4 | 98.3 | 3 |
| yolo26-m_640x640.dxnn | ON | 58.31 | 123.1 | 99.2 | 3 |
| yolo26-m_640x640.dxnn | OFF | 53.27 | 123.7 | 97.7 | 3 |
| yolo26-l_640x640.dxnn | ON | 88.27 | 90.3 | 83.0 | 2 |
| yolo26-l_640x640.dxnn | OFF | 61.97 | 90.7 | 90.4 | 2 |
| yolo26-x_640x640.dxnn | ON | 116.47 | 48.8 | 47.8 | 1 |
| yolo26-x_640x640.dxnn | OFF | 85.36 | 48.9 | 48.8 | 1 |

### Pose Estimation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-pose_640x640.dxnn | ON | 29.85 | 284.4 | 202.7 | 6 |
| yolo26-n-pose_640x640.dxnn | OFF | 25.57 | 305.7 | 248.0 | 8 |
| yolo26-s-pose_640x640.dxnn | ON | 45.76 | 184.6 | 155.3 | 5 |
| yolo26-s-pose_640x640.dxnn | OFF | 35.76 | 184.7 | 174.6 | 5 |
| yolo26-m-pose_640x640.dxnn | ON | 57.74 | 122.2 | 115.5 | 3 |
| yolo26-m-pose_640x640.dxnn | OFF | 42.11 | 122.7 | 119.8 | 3 |
| yolo26-l-pose_640x640.dxnn | ON | 57.01 | 88.7 | 88.3 | 2 |
| yolo26-l-pose_640x640.dxnn | OFF | 51.34 | 89.2 | 89.4 | 2 |
| yolo26-x-pose_640x640.dxnn | ON | 91.72 | 47.6 | 46.8 | 1 |
| yolo26-x-pose_640x640.dxnn | OFF | 79.23 | 47.5 | 47.3 | 1 |

### Segmentation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-seg_640x640.dxnn | ON | 51.20 | 131.3 | 100.8 | 3 |
| yolo26-n-seg_640x640.dxnn | OFF | 47.01 | 164.8 | 84.9 | 2 |
| yolo26-s-seg_640x640.dxnn | ON | 62.81 | 132.8 | 88.1 | 2 |
| yolo26-s-seg_640x640.dxnn | OFF | 55.77 | 138.5 | 83.2 | 2 |
| yolo26-m-seg_640x640.dxnn | ON | 75.42 | 77.3 | 67.0 | 1 |
| yolo26-m-seg_640x640.dxnn | OFF | 75.54 | 77.4 | 76.7 | 1 |
| yolo26-l-seg_640x640.dxnn | ON | 85.91 | 64.4 | 59.5 | 1 |
| yolo26-l-seg_640x640.dxnn | OFF | 79.25 | 64.9 | 63.5 | 1 |
| yolo26-x-seg_640x640.dxnn | ON | 123.03 | 34.1 | 25.8 | — |
| yolo26-x-seg_640x640.dxnn | OFF | 118.53 | 34.2 | 26.1 | — |

### Oriented BBox (OBB)

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-obb_1024x1024.dxnn | ON | 52.02 | 106.3 | 96.2 | 3 |
| yolo26-n-obb_1024x1024.dxnn | OFF | 49.42 | 107.1 | 104.7 | 3 |
| yolo26-s-obb_1024x1024.dxnn | ON | 80.96 | 63.8 | 62.4 | 2 |
| yolo26-s-obb_1024x1024.dxnn | OFF | 58.77 | 64.0 | 62.9 | 2 |
| yolo26-m-obb_1024x1024.dxnn | ON | 97.42 | 42.5 | 41.7 | 1 |
| yolo26-m-obb_1024x1024.dxnn | OFF | 80.65 | 42.5 | 41.8 | 1 |
| yolo26-l-obb_1024x1024.dxnn | ON | 120.72 | 30.9 | 30.8 | 1 |
| yolo26-l-obb_1024x1024.dxnn | OFF | 102.70 | 30.9 | 30.9 | 1 |
| yolo26-x-obb_1024x1024.dxnn | ON | 182.85 | 17.0 | 14.4 | — |
| yolo26-x-obb_1024x1024.dxnn | OFF | 173.46 | 17.0 | 14.2 | — |

### Classification

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-cls-n_224x224.dxnn | ON | 4.27 | 3383.9 | 1086.4 | — |
| yolo26-cls-n_224x224.dxnn | OFF | 4.13 | 3380.0 | 1082.1 | — |
| yolo26-cls-s_224x224.dxnn | ON | 4.90 | 1912.8 | 1088.8 | — |
| yolo26-cls-s_224x224.dxnn | OFF | 4.96 | 1911.7 | 1084.6 | — |
| yolo26-cls-m_224x224.dxnn | ON | 5.43 | 1363.0 | 1087.2 | — |
| yolo26-cls-m_224x224.dxnn | OFF | 5.48 | 1362.9 | 1084.2 | — |
| yolo26-cls-l_224x224.dxnn | ON | 6.72 | 874.2 | 859.1 | — |
| yolo26-cls-l_224x224.dxnn | OFF | 6.80 | 873.6 | 861.1 | — |
| yolo26-cls-x_224x224.dxnn | ON | 9.26 | 492.9 | 488.2 | — |
| yolo26-cls-x_224x224.dxnn | OFF | 9.55 | 492.8 | 488.4 | — |

## Environment

| Item | Value |
|------|-------|
| Product | OrangePi5+ |
| Hostname | orangepi5plus |
| OS | Debian GNU/Linux 12 (bookworm) |
| Kernel | 6.1.43-rockchip-rk3588 |
| CPU | Cortex-A55 |
| CPU Threads | 8 |
| CPU Governor | ondemand |
| RAM | 15.6 GiB |
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
| NPU PCIe | Gen3 X4 [01:00:00] |

### Tools

| Tool | Available | Version |
|------|-----------|---------|
| run_model | Yes | DXRT v3.5.0 run_model |
| dxrt-cli | Yes | DXRT v3.5.0 (build: 5.502926e) |
| gst-launch-1.0 | Yes | gst-launch-1.0 version 1.22.0 |
| gst-inspect-1.0 | Yes | gst-inspect-1.0 version 1.22.0 |
| time | Yes | unknown |
| ffprobe | Yes | ffprobe version 5.1.3-4 Copyright (c) 2007-2022 the FFmpeg d... |
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
| NPU Idle Temp (settled) | 43.0 °C |
| Cool-down Target | ≤ 53.0 °C |
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
| yolo26-n_640x640.dxnn | 178.3 ±2.6 | 8 | 225 | 44.5 | 73.4 | 56 | 1000 | ok |
| yolo26-s_640x640.dxnn | 179.9 ±3.3 | 9 | 224 | 87.3 | 96.3 | 58 | 1000 | ok |
| yolo26-m_640x640.dxnn | 123.1 ±0.1 | 7 | 175 | 93.3 | 100.0 | 61 | 1000 | ok |
| yolo26-l_640x640.dxnn | 90.3 ±0.1 | 6 | 156 | 93.1 | 100.0 | 61 | 1000 | ok |
| yolo26-x_640x640.dxnn | 48.8 ±0.0 | 5 | 106 | 92.0 | 100.0 | 61~62 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n_640x640.dxnn | 8 | [3]:99.7 · [4]:143.3 · [5]:170.8 · [6]:173.0 · [7]:177.2 · **[8]:182.1 ★** · [9]:177.3 · [10]:175.5 · [11]:174.2 |
| yolo26-s_640x640.dxnn | 9 | [3]:69.8 · [4]:104.8 · [5]:140.3 · [6]:164.4 · [7]:175.6 · [8]:178.3 · **[9]:183.7 ★** · [10]:182.5 · [11]:181.3 · [12]:179.9 |
| yolo26-m_640x640.dxnn | 7 | [3]:54.0 · [4]:73.7 · [5]:99.7 · [6]:118.3 · **[7]:122.3 ★** · [8]:122.8 · [9]:122.9 · [10]:122.9 |
| yolo26-l_640x640.dxnn | 6 | [3]:45.0 · [4]:62.0 · [5]:79.4 · **[6]:89.7 ★** · [7]:90.3 · [8]:90.4 · [9]:90.5 |
| yolo26-x_640x640.dxnn | 5 | [3]:28.5 · [4]:39.9 · **[5]:48.3 ★** · [6]:48.7 · [7]:48.8 · [8]:48.8 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n_640x640.dxnn | 324.2 ±0.1 | 8 | 207 | 92.9 | 99.0 | 58 | 1000 | ok |
| yolo26-s_640x640.dxnn | 200.4 ±0.0 | 7 | 151 | 94.2 | 100.0 | 58~59 | 1000 | ok |
| yolo26-m_640x640.dxnn | 123.7 ±0.2 | 6 | 103 | 93.6 | 100.0 | 61 | 1000 | ok |
| yolo26-l_640x640.dxnn | 90.7 ±0.0 | 6 | 92 | 94.8 | 100.0 | 61 | 1000 | ok |
| yolo26-x_640x640.dxnn | 48.9 ±0.0 | 5 | 68 | 92.1 | 100.0 | 61~62 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n_640x640.dxnn | 8 | [3]:132.1 · [4]:179.8 · [5]:238.7 · [6]:288.2 · [7]:321.5 · **[8]:326.2 ★** · [9]:326.6 · [10]:326.9 · [11]:327.4 |
| yolo26-s_640x640.dxnn | 7 | [3]:85.9 · [4]:131.9 · [5]:167.3 · [6]:197.7 · **[7]:199.7 ★** · [8]:200.1 · [9]:200.1 · [10]:200.3 |
| yolo26-m_640x640.dxnn | 6 | [3]:65.7 · [4]:89.9 · [5]:118.5 · **[6]:123.5 ★** · [7]:123.7 · [8]:123.7 · [9]:123.7 |
| yolo26-l_640x640.dxnn | 6 | [3]:51.9 · [4]:71.8 · [5]:89.1 · **[6]:90.6 ★** · [7]:90.5 · [8]:90.6 · [9]:90.6 |
| yolo26-x_640x640.dxnn | 5 | [3]:34.2 · [4]:47.0 · **[5]:48.7 ★** · [6]:48.8 · [7]:48.8 · [8]:48.8 |


#### Pose Estimation

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 284.4 ±1.5 | 8 | 245 | 87.9 | 97.1 | 57~58 | 1000 | ok |
| yolo26-s-pose_640x640.dxnn | 184.6 ±0.1 | 7 | 173 | 94.1 | 100.0 | 58~59 | 1000 | ok |
| yolo26-m-pose_640x640.dxnn | 122.2 ±0.0 | 6 | 153 | 94.9 | 100.0 | 61 | 1000 | ok |
| yolo26-l-pose_640x640.dxnn | 88.7 ±0.2 | 5 | 130 | 92.5 | 100.0 | 61 | 1000 | ok |
| yolo26-x-pose_640x640.dxnn | 47.6 ±0.0 | 5 | 91 | 93.5 | 100.0 | 62 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-pose_640x640.dxnn | 8 | [3]:108.0 · [4]:159.9 · [5]:214.3 · [6]:248.8 · [7]:271.3 · **[8]:286.0 ★** · [9]:278.3 · [10]:283.3 · [11]:277.3 |
| yolo26-s-pose_640x640.dxnn | 7 | [3]:82.6 · [4]:115.0 · [5]:153.5 · [6]:179.6 · **[7]:183.6 ★** · [8]:183.5 · [9]:183.6 · [10]:183.6 |
| yolo26-m-pose_640x640.dxnn | 6 | [3]:58.5 · [4]:86.8 · [5]:111.8 · **[6]:121.7 ★** · [7]:121.8 · [8]:122.0 · [9]:121.9 |
| yolo26-l-pose_640x640.dxnn | 5 | [3]:45.9 · [4]:69.5 · **[5]:88.5 ★** · [6]:89.0 · [7]:89.0 · [8]:89.2 |
| yolo26-x-pose_640x640.dxnn | 5 | [3]:30.5 · [4]:43.4 · **[5]:47.4 ★** · [6]:47.5 · [7]:47.5 · [8]:47.5 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 305.7 ±0.8 | 7 | 153 | 94.5 | 99.9 | 58 | 1000 | ok |
| yolo26-s-pose_640x640.dxnn | 184.7 ±0.3 | 6 | 121 | 94.5 | 100.0 | 58~59 | 1000 | ok |
| yolo26-m-pose_640x640.dxnn | 122.7 ±0.0 | 6 | 110 | 94.5 | 100.0 | 61 | 1000 | ok |
| yolo26-l-pose_640x640.dxnn | 89.2 ±0.0 | 5 | 78 | 94.3 | 100.0 | 61 | 1000 | ok |
| yolo26-x-pose_640x640.dxnn | 47.5 ±0.0 | 4 | 53 | 92.4 | 100.0 | 61 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-pose_640x640.dxnn | 7 | [3]:126.7 · [4]:192.0 · [5]:243.5 · [6]:295.4 · **[7]:304.7 ★** · [8]:305.6 · [9]:306.2 · [10]:306.4 |
| yolo26-s-pose_640x640.dxnn | 6 | [3]:86.9 · [4]:129.9 · [5]:173.8 · **[6]:184.1 ★** · [7]:184.5 · [8]:184.6 · [9]:184.3 |
| yolo26-m-pose_640x640.dxnn | 6 | [3]:69.2 · [4]:96.3 · [5]:118.8 · **[6]:122.1 ★** · [7]:122.3 · [8]:122.3 · [9]:122.4 |
| yolo26-l-pose_640x640.dxnn | 5 | [3]:55.3 · [4]:79.0 · **[5]:88.9 ★** · [6]:89.1 · [7]:89.1 · [8]:89.1 |
| yolo26-x-pose_640x640.dxnn | 4 | [3]:34.7 · **[4]:47.2 ★** · [5]:47.5 · [6]:47.5 · [7]:47.5 |


#### Segmentation

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 131.3 ±0.3 | 7 | 297 | 42.9 | 69.6 | 56 | 1000 | ok |
| yolo26-s-seg_640x640.dxnn | 132.8 ±0.3 | 8 | 277 | 89.0 | 96.9 | 59 | 1000 | ok |
| yolo26-m-seg_640x640.dxnn | 77.3 ±0.4 | 7 | 181 | 92.5 | 100.0 | 61~62 | 1000 | ok |
| yolo26-l-seg_640x640.dxnn | 64.4 ±0.1 | 6 | 157 | 92.7 | 100.0 | 62 | 1000 | ok |
| yolo26-x-seg_640x640.dxnn | 34.1 ±0.1 | 5 | 105 | 91.7 | 100.0 | 62~63 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-seg_640x640.dxnn | 7 | [3]:62.2 · [4]:91.8 · [5]:117.9 · [6]:126.9 · **[7]:130.3 ★** · [8]:130.2 · [9]:130.7 · [10]:130.0 |
| yolo26-s-seg_640x640.dxnn | 8 | [3]:50.6 · [4]:72.4 · [5]:95.1 · [6]:116.6 · [7]:129.8 · **[8]:133.3 ★** · [9]:133.1 · [10]:132.3 · [11]:133.1 |
| yolo26-m-seg_640x640.dxnn | 7 | [3]:36.1 · [4]:49.2 · [5]:65.8 · [6]:76.2 · **[7]:76.7 ★** · [8]:76.1 · [9]:77.1 · [10]:76.7 · [11]:76.3 · [12]:76.8 |
| yolo26-l-seg_640x640.dxnn | 6 | [3]:32.9 · [4]:46.6 · [5]:59.3 · **[6]:64.1 ★** · [7]:64.5 · [8]:64.6 · [9]:64.6 |
| yolo26-x-seg_640x640.dxnn | 5 | [3]:20.4 · [4]:29.7 · **[5]:34.0 ★** · [6]:33.7 · [7]:34.1 · [8]:34.1 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 164.8 ±22.0 | 8 | 209 | 57.8 | 83.3 | 56~58 | 1000 | ok |
| yolo26-s-seg_640x640.dxnn | 138.5 ±0.2 | 7 | 197 | 93.4 | 100.0 | 59~60 | 1000 | ok |
| yolo26-m-seg_640x640.dxnn | 77.4 ±0.2 | 6 | 137 | 93.6 | 100.0 | 62 | 1000 | ok |
| yolo26-l-seg_640x640.dxnn | 64.9 ±0.0 | 6 | 112 | 93.3 | 100.0 | 62 | 1000 | ok |
| yolo26-x-seg_640x640.dxnn | 34.2 ±0.2 | 5 | 79 | 92.1 | 100.0 | 63 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-seg_640x640.dxnn | 8 | [3]:80.8 · [4]:127.4 · [5]:156.3 · [6]:180.5 · [7]:188.9 · **[8]:190.7 ★** · [9]:191.0 · [10]:190.8 · [11]:191.1 · [12]:191.2 |
| yolo26-s-seg_640x640.dxnn | 7 | [3]:59.6 · [4]:84.0 · [5]:115.2 · [6]:136.7 · **[7]:137.8 ★** · [8]:138.0 · [9]:138.1 · [10]:138.4 · [11]:138.3 · [12]:138.6 |
| yolo26-m-seg_640x640.dxnn | 6 | [3]:42.2 · [4]:58.9 · [5]:75.5 · **[6]:76.9 ★** · [7]:77.0 · [8]:76.9 · [9]:76.7 |
| yolo26-l-seg_640x640.dxnn | 6 | [3]:37.2 · [4]:52.4 · [5]:63.6 · **[6]:64.6 ★** · [7]:64.7 · [8]:64.8 · [9]:64.8 |
| yolo26-x-seg_640x640.dxnn | 5 | [3]:22.4 · [4]:32.0 · **[5]:34.1 ★** · [6]:34.3 · [7]:34.4 · [8]:34.1 |


#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 106.3 ±0.1 | 6 | 159 | 95.2 | 100.0 | 57~58 | 1000 | ok |
| yolo26-s-obb_1024x1024.dxnn | 63.8 ±0.1 | 6 | 111 | 92.9 | 100.0 | 58~59 | 1000 | ok |
| yolo26-m-obb_1024x1024.dxnn | 42.5 ±0.0 | 5 | 98 | 92.9 | 100.0 | 61 | 1000 | ok |
| yolo26-l-obb_1024x1024.dxnn | 30.9 ±0.0 | 5 | 84 | 92.2 | 100.0 | 60~61 | 1000 | ok |
| yolo26-x-obb_1024x1024.dxnn | 17.0 ±0.0 | 5 | 53 | 90.8 | 100.0 | 61 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-obb_1024x1024.dxnn | 6 | [3]:51.1 · [4]:75.9 · [5]:96.5 · **[6]:106.0 ★** · [7]:106.6 · [8]:106.7 · [9]:106.7 |
| yolo26-s-obb_1024x1024.dxnn | 6 | [3]:37.0 · [4]:49.1 · [5]:62.9 · **[6]:63.6 ★** · [7]:63.4 · [8]:63.3 · [9]:63.5 |
| yolo26-m-obb_1024x1024.dxnn | 5 | [3]:27.6 · [4]:37.7 · **[5]:42.3 ★** · [6]:42.3 · [7]:42.4 · [8]:42.3 |
| yolo26-l-obb_1024x1024.dxnn | 5 | [3]:21.7 · [4]:29.6 · **[5]:30.8 ★** · [6]:30.8 · [7]:30.8 · [8]:30.8 |
| yolo26-x-obb_1024x1024.dxnn | 5 | [3]:13.2 · [4]:16.8 · **[5]:16.9 ★** · [6]:16.9 · [7]:16.9 · [8]:16.9 · [9]:16.9 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 107.1 ±0.0 | 6 | 107 | 95.4 | 100.0 | 57~58 | 1000 | ok |
| yolo26-s-obb_1024x1024.dxnn | 64.0 ±0.0 | 5 | 72 | 94.0 | 100.0 | 58~59 | 1000 | ok |
| yolo26-m-obb_1024x1024.dxnn | 42.5 ±0.0 | 5 | 56 | 94.2 | 100.0 | 61 | 1000 | ok |
| yolo26-l-obb_1024x1024.dxnn | 30.9 ±0.0 | 4 | 44 | 91.9 | 100.0 | 60~61 | 1000 | ok |
| yolo26-x-obb_1024x1024.dxnn | 17.0 ±0.0 | 4 | 28 | 90.8 | 100.0 | 61 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-obb_1024x1024.dxnn | 6 | [3]:60.0 · [4]:80.2 · [5]:101.9 · **[6]:106.8 ★** · [7]:106.9 · [8]:106.9 · [9]:106.9 |
| yolo26-s-obb_1024x1024.dxnn | 5 | [3]:43.3 · [4]:58.3 · **[5]:63.4 ★** · [6]:63.3 · [7]:63.4 · [8]:63.3 |
| yolo26-m-obb_1024x1024.dxnn | 5 | [3]:31.6 · [4]:41.1 · **[5]:42.4 ★** · [6]:42.4 · [7]:42.4 · [8]:42.4 |
| yolo26-l-obb_1024x1024.dxnn | 4 | [3]:25.0 · **[4]:30.8 ★** · [5]:30.9 · [6]:30.9 · [7]:30.9 |
| yolo26-x-obb_1024x1024.dxnn | 4 | [3]:14.7 · **[4]:16.9 ★** · [5]:16.9 · [6]:16.9 · [7]:16.9 |


#### Classification

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-cls-n_224x224.dxnn | 3383.9 ±14.5 | 9 | 103 | 88.7 | 92.4 | 56 | 1000 | ok |
| yolo26-cls-s_224x224.dxnn | 1912.8 ±2.6 | 7 | 71 | 89.0 | 95.4 | 57~58 | 1000 | ok |
| yolo26-cls-m_224x224.dxnn | 1363.0 ±0.6 | 7 | 66 | 93.3 | 97.1 | 59~60 | 1000 | ok |
| yolo26-cls-l_224x224.dxnn | 874.2 ±0.1 | 6 | 54 | 93.2 | 98.8 | 58 | 1000 | ok |
| yolo26-cls-x_224x224.dxnn | 492.9 ±0.3 | 5 | 41 | 95.1 | 99.6 | 59~60 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-cls-n_224x224.dxnn | 9 | [3]:1228.9 · [4]:2009.6 · [5]:2678.3 · [6]:3139.2 · [7]:3281.5 · [8]:3337.4 · **[9]:3392.0 ★** · [10]:3401.5 · [11]:3399.3 · [12]:3397.7 |
| yolo26-cls-s_224x224.dxnn | 7 | [3]:801.2 · [4]:1240.1 · [5]:1650.4 · [6]:1879.0 · **[7]:1904.5 ★** · [8]:1913.2 · [9]:1911.5 · [10]:1915.3 |
| yolo26-cls-m_224x224.dxnn | 7 | [3]:610.9 · [4]:976.2 · [5]:1252.9 · [6]:1350.8 · **[7]:1364.0 ★** · [8]:1364.4 · [9]:1367.0 · [10]:1367.3 · [11]:1368.1 |
| yolo26-cls-l_224x224.dxnn | 6 | [3]:479.9 · [4]:679.1 · [5]:845.3 · **[6]:873.8 ★** · [7]:874.9 · [8]:876.0 · [9]:875.9 |
| yolo26-cls-x_224x224.dxnn | 5 | [3]:319.3 · [4]:436.9 · **[5]:492.2 ★** · [6]:493.4 · [7]:493.4 · [8]:494.1 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-cls-n_224x224.dxnn | 3380.0 ±5.8 | 9 | 102 | 89.6 | 91.9 | 56~57 | 1000 | ok |
| yolo26-cls-s_224x224.dxnn | 1911.7 ±2.2 | 7 | 71 | 88.5 | 95.9 | 57~58 | 1000 | ok |
| yolo26-cls-m_224x224.dxnn | 1362.9 ±0.4 | 7 | 66 | 92.1 | 97.0 | 59~60 | 1000 | ok |
| yolo26-cls-l_224x224.dxnn | 873.6 ±0.4 | 6 | 54 | 94.0 | 98.8 | 58~59 | 1000 | ok |
| yolo26-cls-x_224x224.dxnn | 492.8 ±0.4 | 5 | 41 | 94.2 | 99.7 | 60 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-cls-n_224x224.dxnn | 9 | [3]:1232.2 · [4]:2003.9 · [5]:2678.2 · [6]:3129.7 · [7]:3271.9 · [8]:3331.3 · **[9]:3393.7 ★** · [10]:3394.8 · [11]:3397.2 · [12]:3395.9 |
| yolo26-cls-s_224x224.dxnn | 7 | [3]:798.0 · [4]:1233.8 · [5]:1646.9 · [6]:1876.3 · **[7]:1905.7 ★** · [8]:1913.3 · [9]:1913.9 · [10]:1914.1 |
| yolo26-cls-m_224x224.dxnn | 7 | [3]:605.6 · [4]:969.8 · [5]:1254.7 · [6]:1349.1 · **[7]:1364.0 ★** · [8]:1363.1 · [9]:1365.9 · [10]:1367.2 |
| yolo26-cls-l_224x224.dxnn | 6 | [3]:469.1 · [4]:682.1 · [5]:845.5 · **[6]:874.0 ★** · [7]:874.1 · [8]:875.0 · [9]:876.2 |
| yolo26-cls-x_224x224.dxnn | 5 | [3]:318.8 · [4]:441.9 · **[5]:492.6 ★** · [6]:493.1 · [7]:493.4 · [8]:494.0 |


### Latency (Single-Core, Sync)

#### Object Detection

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_640x640.dxnn | 26.4 | 37.84 | 32.89 | 4.95 | 44 | ok |
| yolo26-s_640x640.dxnn | 21.1 | 47.32 | 42.38 | 4.94 | 54 | ok |
| yolo26-m_640x640.dxnn | 17.1 | 58.31 | 52.53 | 5.79 | 55 | ok |
| yolo26-l_640x640.dxnn | 11.3 | 88.27 | 82.70 | 5.57 | 55 | ok |
| yolo26-x_640x640.dxnn | 8.6 | 116.47 | 110.74 | 5.73 | 56 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_640x640.dxnn | 27.4 | 36.53 | 36.53 | N/A | 54 | ok |
| yolo26-s_640x640.dxnn | 19.1 | 52.30 | 52.30 | N/A | 54 | ok |
| yolo26-m_640x640.dxnn | 18.8 | 53.27 | 53.27 | N/A | 55 | ok |
| yolo26-l_640x640.dxnn | 16.1 | 61.97 | 61.97 | N/A | 55 | ok |
| yolo26-x_640x640.dxnn | 11.7 | 85.36 | 85.36 | N/A | 56 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-pose_640x640.dxnn | 33.5 | 29.85 | 26.79 | 3.07 | 54 | ok |
| yolo26-s-pose_640x640.dxnn | 21.9 | 45.76 | 42.45 | 3.31 | 54 | ok |
| yolo26-m-pose_640x640.dxnn | 17.3 | 57.74 | 54.41 | 3.33 | 55 | ok |
| yolo26-l-pose_640x640.dxnn | 17.5 | 57.01 | 53.74 | 3.27 | 55 | ok |
| yolo26-x-pose_640x640.dxnn | 10.9 | 91.72 | 88.58 | 3.13 | 56 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-pose_640x640.dxnn | 39.1 | 25.57 | 25.57 | N/A | 54 | ok |
| yolo26-s-pose_640x640.dxnn | 28.0 | 35.76 | 35.76 | N/A | 54 | ok |
| yolo26-m-pose_640x640.dxnn | 23.7 | 42.11 | 42.11 | N/A | 55 | ok |
| yolo26-l-pose_640x640.dxnn | 19.5 | 51.34 | 51.34 | N/A | 56 | ok |
| yolo26-x-pose_640x640.dxnn | 12.6 | 79.23 | 79.23 | N/A | 56 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-seg_640x640.dxnn | 19.5 | 51.20 | 45.44 | 5.76 | 54 | ok |
| yolo26-s-seg_640x640.dxnn | 15.9 | 62.81 | 57.31 | 5.50 | 54 | ok |
| yolo26-m-seg_640x640.dxnn | 13.3 | 75.42 | 70.45 | 4.97 | 55 | ok |
| yolo26-l-seg_640x640.dxnn | 11.6 | 85.91 | 80.39 | 5.53 | 55 | ok |
| yolo26-x-seg_640x640.dxnn | 8.1 | 123.03 | 117.81 | 5.22 | 57 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-seg_640x640.dxnn | 21.3 | 47.01 | 47.01 | N/A | 54 | ok |
| yolo26-s-seg_640x640.dxnn | 17.9 | 55.77 | 55.77 | N/A | 55 | ok |
| yolo26-m-seg_640x640.dxnn | 13.2 | 75.54 | 75.54 | N/A | 56 | ok |
| yolo26-l-seg_640x640.dxnn | 12.6 | 79.25 | 79.25 | N/A | 56 | ok |
| yolo26-x-seg_640x640.dxnn | 8.4 | 118.53 | 118.53 | N/A | 57 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-obb_1024x1024.dxnn | 19.2 | 52.02 | 48.20 | 3.82 | 54 | ok |
| yolo26-s-obb_1024x1024.dxnn | 12.4 | 80.96 | 76.69 | 4.27 | 55 | ok |
| yolo26-m-obb_1024x1024.dxnn | 10.3 | 97.42 | 93.20 | 4.22 | 56 | ok |
| yolo26-l-obb_1024x1024.dxnn | 8.3 | 120.72 | 116.37 | 4.35 | 56 | ok |
| yolo26-x-obb_1024x1024.dxnn | 5.5 | 182.85 | 178.50 | 4.35 | 58 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-obb_1024x1024.dxnn | 20.2 | 49.42 | 49.42 | N/A | 55 | ok |
| yolo26-s-obb_1024x1024.dxnn | 17.0 | 58.77 | 58.77 | N/A | 56 | ok |
| yolo26-m-obb_1024x1024.dxnn | 12.4 | 80.65 | 80.65 | N/A | 57 | ok |
| yolo26-l-obb_1024x1024.dxnn | 9.7 | 102.70 | 102.70 | N/A | 57 | ok |
| yolo26-x-obb_1024x1024.dxnn | 5.8 | 173.46 | 173.46 | N/A | 58 | ok |

#### Classification

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-cls-n_224x224.dxnn | 234.4 | 4.27 | 4.27 | N/A | 54 | ok |
| yolo26-cls-s_224x224.dxnn | 204.1 | 4.90 | 4.90 | N/A | 54 | ok |
| yolo26-cls-m_224x224.dxnn | 184.1 | 5.43 | 5.43 | N/A | 54 | ok |
| yolo26-cls-l_224x224.dxnn | 148.7 | 6.72 | 6.72 | N/A | 54 | ok |
| yolo26-cls-x_224x224.dxnn | 107.9 | 9.26 | 9.26 | N/A | 54 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-cls-n_224x224.dxnn | 241.9 | 4.13 | 4.13 | N/A | 54 | ok |
| yolo26-cls-s_224x224.dxnn | 201.4 | 4.96 | 4.96 | N/A | 54 | ok |
| yolo26-cls-m_224x224.dxnn | 182.6 | 5.48 | 5.48 | N/A | 54 | ok |
| yolo26-cls-l_224x224.dxnn | 147.1 | 6.80 | 6.80 | N/A | 54 | ok |
| yolo26-cls-x_224x224.dxnn | 104.8 | 9.55 | 9.55 | N/A | 55 | ok |

## E2E Pipeline (Single-Stream)

### Object Detection

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | mppvideodec | 3455 | 3 | 149.2 ±1.6 | 23.16 | 247 | 37.6 | 63.0 | 56~57 | 1000 | 223 | ok |
| yolo26-s_640x640.dxnn | mppvideodec | 3455 | 3 | 127.1 ±0.5 | 27.18 | 219 | 57.7 | 77.8 | 58~60 | 1000 | 244 | ok |
| yolo26-m_640x640.dxnn | mppvideodec | 3455 | 3 | 99.2 ±1.0 | 34.83 | 191 | 73.9 | 95.3 | 63~68 | 1000 | 275 | ok |
| yolo26-l_640x640.dxnn | mppvideodec | 3455 | 3 | 83.0 ±0.8 | 41.65 | 176 | 82.3 | 98.8 | 64~70 | 1000 | 290 | ok |
| yolo26-x_640x640.dxnn | mppvideodec | 3455 | 3 | 47.8 ±1.5 | 72.26 | 132 | 93.7 | 100.0 | 72~80 | 800~1000 | 417 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | mppvideodec | 3455 | 3 | 95.0 ±5.9 | 36.35 | 212 | 21.4 | 73.3 | 56~57 | 1000 | 236 | ok |
| yolo26-s_640x640.dxnn | mppvideodec | 3455 | 3 | 98.3 ±1.0 | 35.13 | 214 | 40.3 | 68.9 | 58~59 | 1000 | 254 | ok |
| yolo26-m_640x640.dxnn | mppvideodec | 3455 | 3 | 97.7 ±0.7 | 35.35 | 219 | 72.0 | 80.0 | 63~68 | 1000 | 288 | ok |
| yolo26-l_640x640.dxnn | mppvideodec | 3455 | 3 | 90.4 ±0.2 | 38.23 | 220 | 89.9 | 100.0 | 65~72 | 1000 | 302 | ok |
| yolo26-x_640x640.dxnn | mppvideodec | 3455 | 3 | 48.8 ±0.2 | 70.74 | 155 | 92.9 | 100.0 | 71~80 | 1000 | 403 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n_640x640.dxnn | 149.2 | 95.0 | +54.2 | +57.0% |
| yolo26-s_640x640.dxnn | 127.1 | 98.3 | +28.8 | +29.2% |
| yolo26-m_640x640.dxnn | 99.2 | 97.7 | +1.5 | +1.5% |
| yolo26-l_640x640.dxnn | 83.0 | 90.4 | -7.4 | -8.2% |
| yolo26-x_640x640.dxnn | 47.8 | 48.8 | -1.0 | -2.1% |

### Pose Estimation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 202.7 ±0.9 | 17.04 | 240 | 54.3 | 76.7 | 57~58 | 1000 | 204 | ok |
| yolo26-s-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 155.3 ±1.1 | 22.25 | 206 | 72.8 | 91.6 | 59~61 | 1000 | 227 | ok |
| yolo26-m-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 115.5 ±0.3 | 29.91 | 177 | 84.4 | 100.0 | 63~68 | 1000 | 259 | ok |
| yolo26-l-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 88.3 ±0.5 | 39.11 | 154 | 89.5 | 100.0 | 65~70 | 1000 | 273 | ok |
| yolo26-x-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 46.8 ±1.5 | 73.89 | 106 | 94.7 | 100.0 | 72~81 | 800~1000 | 417 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 248.0 ±2.5 | 13.93 | 219 | 62.7 | 89.7 | 56~58 | 1000 | 194 | ok |
| yolo26-s-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 174.6 ±0.6 | 19.78 | 179 | 78.8 | 97.9 | 59~61 | 1000 | 214 | ok |
| yolo26-m-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 119.8 ±0.4 | 28.85 | 151 | 88.1 | 100.0 | 63~68 | 1000 | 247 | ok |
| yolo26-l-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 89.4 ±0.1 | 38.66 | 116 | 91.1 | 100.0 | 65~71 | 1000 | 262 | ok |
| yolo26-x-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 47.3 ±0.8 | 73.10 | 87 | 95.0 | 100.0 | 71~78 | 800~1000 | 400 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-pose_640x640.dxnn | 202.7 | 248.0 | -45.2 | -18.2% |
| yolo26-s-pose_640x640.dxnn | 155.3 | 174.6 | -19.4 | -11.1% |
| yolo26-m-pose_640x640.dxnn | 115.5 | 119.8 | -4.2 | -3.5% |
| yolo26-l-pose_640x640.dxnn | 88.3 | 89.4 | -1.0 | -1.2% |
| yolo26-x-pose_640x640.dxnn | 46.8 | 47.3 | -0.5 | -1.1% |

### Segmentation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 100.8 ±0.4 | 34.29 | 323 | 33.1 | 57.5 | 57~59 | 1000 | 346 | ok |
| yolo26-s-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 88.1 ±0.0 | 39.22 | 284 | 54.2 | 74.4 | 60~64 | 1000 | 374 | ok |
| yolo26-m-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 67.0 ±0.1 | 51.58 | 233 | 75.1 | 96.2 | 68~76 | 1000 | 405 | ok |
| yolo26-l-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 59.5 ±0.5 | 58.02 | 217 | 84.7 | 100.0 | 70~78 | 1000 | 418 | ok |
| yolo26-x-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 25.8 ±6.3 | 133.98 | 126 | 94.2 | 100.0 | 80~83 | 400~1000 | 523 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 84.9 ±0.4 | 40.72 | 253 | 24.1 | 79.4 | 56~58 | 1000 | 371 | ok |
| yolo26-s-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 83.2 ±0.2 | 41.51 | 260 | 45.3 | 77.6 | 59~63 | 1000 | 388 | ok |
| yolo26-m-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 76.7 ±0.7 | 45.06 | 246 | 89.6 | 100.0 | 69~77 | 1000 | 426 | ok |
| yolo26-l-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 63.5 ±0.9 | 54.40 | 227 | 90.5 | 100.0 | 70~78 | 800~1000 | 434 | ok |
| yolo26-x-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 26.1 ±6.1 | 132.26 | 129 | 95.1 | 100.0 | 79~83 | 400~1000 | 543 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-seg_640x640.dxnn | 100.8 | 84.9 | +15.9 | +18.7% |
| yolo26-s-seg_640x640.dxnn | 88.1 | 83.2 | +4.9 | +5.9% |
| yolo26-m-seg_640x640.dxnn | 67.0 | 76.7 | -9.7 | -12.6% |
| yolo26-l-seg_640x640.dxnn | 59.5 | 63.5 | -4.0 | -6.2% |
| yolo26-x-seg_640x640.dxnn | 25.8 | 26.1 | -0.3 | -1.3% |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 96.2 ±1.4 | 27.44 | 185 | 79.2 | 99.5 | 58~61 | 1000 | 257 | ok |
| yolo26-s-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 62.4 ±0.4 | 42.30 | 143 | 89.6 | 100.0 | 62~66 | 1000 | 281 | ok |
| yolo26-m-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 41.7 ±0.5 | 63.32 | 114 | 92.6 | 100.0 | 69~78 | 1000 | 314 | ok |
| yolo26-l-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 30.8 ±0.3 | 85.70 | 103 | 93.0 | 100.0 | 71~80 | 1000 | 330 | ok |
| yolo26-x-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 14.4 ±2.0 | 182.97 | 59 | 94.0 | 100.0 | 81~83 | 600~1000 | 440 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 104.7 ±0.6 | 25.22 | 197 | 87.5 | 100.0 | 59~62 | 1000 | 258 | ok |
| yolo26-s-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 62.9 ±0.5 | 41.99 | 150 | 89.6 | 100.0 | 62~67 | 1000 | 283 | ok |
| yolo26-m-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 41.8 ±0.6 | 63.15 | 133 | 92.2 | 100.0 | 69~77 | 1000 | 312 | ok |
| yolo26-l-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 30.9 ±0.4 | 85.49 | 110 | 93.7 | 100.0 | 72~80 | 1000 | 326 | ok |
| yolo26-x-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 14.2 ±1.9 | 185.51 | 63 | 94.5 | 100.0 | 81~83 | 600~1000 | 426 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-obb_1024x1024.dxnn | 96.2 | 104.7 | -8.5 | -8.1% |
| yolo26-s-obb_1024x1024.dxnn | 62.4 | 62.9 | -0.5 | -0.7% |
| yolo26-m-obb_1024x1024.dxnn | 41.7 | 41.8 | -0.1 | -0.3% |
| yolo26-l-obb_1024x1024.dxnn | 30.8 | 30.9 | -0.1 | -0.3% |
| yolo26-x-obb_1024x1024.dxnn | 14.4 | 14.2 | +0.2 | +1.4% |

### Classification

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-cls-n_224x224.dxnn | mppvideodec | 3455 | 3 | 1086.4 ±4.3 | 3.18 | 176 | 10.4 | 50.4 | 54 | 1000 | 91 | ok |
| yolo26-cls-s_224x224.dxnn | mppvideodec | 3455 | 3 | 1088.8 ±2.6 | 3.17 | 173 | 25.0 | 66.9 | 55 | 1000 | 104 | ok |
| yolo26-cls-m_224x224.dxnn | mppvideodec | 3455 | 3 | 1087.2 ±1.7 | 3.18 | 176 | 37.1 | 83.6 | 56 | 1000 | 127 | ok |
| yolo26-cls-l_224x224.dxnn | mppvideodec | 3455 | 3 | 859.1 ±3.2 | 4.02 | 152 | 54.5 | 98.1 | 56 | 1000 | 140 | ok |
| yolo26-cls-x_224x224.dxnn | mppvideodec | 3455 | 3 | 488.2 ±2.6 | 7.08 | 126 | 68.9 | 99.6 | 58 | 1000 | 216 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-cls-n_224x224.dxnn | mppvideodec | 3455 | 3 | 1082.1 ±7.6 | 3.19 | 177 | 14.1 | 50.1 | 54 | 1000 | 91 | ok |
| yolo26-cls-s_224x224.dxnn | mppvideodec | 3455 | 3 | 1084.6 ±5.5 | 3.19 | 176 | 26.9 | 67.5 | 54~55 | 1000 | 104 | ok |
| yolo26-cls-m_224x224.dxnn | mppvideodec | 3455 | 3 | 1084.2 ±3.8 | 3.19 | 174 | 35.4 | 83.4 | 56 | 1000 | 127 | ok |
| yolo26-cls-l_224x224.dxnn | mppvideodec | 3455 | 3 | 861.1 ±4.6 | 4.01 | 153 | 52.3 | 98.5 | 56~57 | 1000 | 140 | ok |
| yolo26-cls-x_224x224.dxnn | mppvideodec | 3455 | 3 | 488.4 ±2.3 | 7.08 | 125 | 67.8 | 99.5 | 58~59 | 1000 | 216 | ok |

> Classification has no CPU part, so ORT ON and OFF run the same model; differences between the two tables are measurement noise.

## E2E Pipeline (Multi-Stream)

### Object Detection

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | 4 | 3 | 147.8 ±0.1 | 36.9 | 255 | 40.6 | 63.8 | 62~66 | 1000 | 246 | ok |
| yolo26-n_640x640.dxnn | 5 | 3 | 149.1 ±2.7 | 29.8 | 252 | 41.1 | 64.6 | 69~70 | 1000 | 250 | ok |
| yolo26-s_640x640.dxnn | 4 | 3 | 127.4 ±0.8 | 31.9 | 226 | 62.2 | 79.7 | 67~71 | 1000 | 267 | ok |
| yolo26-s_640x640.dxnn | 5 | 3 | 127.3 ±1.4 | 25.4 | 226 | 62.9 | 78.6 | 75~77 | 1000 | 272 | ok |
| yolo26-m_640x640.dxnn | 3 | 3 | 95.5 ±5.6 | 31.8 | 192 | 80.7 | 97.1 | 79~82 | 600~1000 | 292 | ok |
| yolo26-m_640x640.dxnn | 4 | 3 | 79.0 ±3.9 | 19.7 | 175 | 90.0 | 100.0 | 82~84 | 400~800 | 298 | ok |
| yolo26-l_640x640.dxnn | 2 | 3 | 78.5 ±4.0 | 39.3 | 174 | 88.4 | 100.0 | 80~83 | 800~1000 | 300 | ok |
| yolo26-l_640x640.dxnn | 3 | 3 | 64.7 ±0.6 | 21.6 | 164 | 93.1 | 100.0 | 83~84 | 600~1000 | 307 | ok |
| yolo26-x_640x640.dxnn | 1 | 3 | 47.8 ±1.5 | 47.8 | 132 | 93.7 | 100.0 | 72~80 | 800~1000 | 417 | ok |
| yolo26-x_640x640.dxnn | 2 | 3 | 34.6 ±0.3 | 17.3 | 114 | 96.1 | 100.0 | 83 | 600~1000 | 417 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | 3 | 3 | 96.1 ±0.5 | 32.0 | 211 | 22.5 | 73.3 | 59~61 | 1000 | 259 | ok |
| yolo26-n_640x640.dxnn | 4 | 3 | 97.5 ±0.6 | 24.4 | 212 | 23.2 | 73.3 | 63~64 | 1000 | 268 | ok |
| yolo26-s_640x640.dxnn | 3 | 3 | 98.1 ±1.5 | 32.7 | 220 | 43.0 | 68.9 | 65~68 | 1000 | 280 | ok |
| yolo26-s_640x640.dxnn | 4 | 3 | 97.8 ±1.4 | 24.4 | 222 | 42.8 | 67.9 | 70~72 | 1000 | 289 | ok |
| yolo26-m_640x640.dxnn | 3 | 3 | 93.3 ±2.9 | 31.1 | 220 | 77.7 | 100.0 | 78~83 | 600~1000 | 311 | ok |
| yolo26-m_640x640.dxnn | 4 | 3 | 75.2 ±1.2 | 18.8 | 204 | 96.4 | 100.0 | 82~83 | 400~800 | 316 | ok |
| yolo26-l_640x640.dxnn | 3 | 3 | 72.0 ±7.3 | 24.0 | 199 | 96.2 | 100.0 | 82~83 | 600~1000 | 322 | ok |
| yolo26-l_640x640.dxnn | 2 | 3 | 65.1 ±0.1 | 32.5 | 188 | 94.7 | 100.0 | 84 | 600~800 | 308 | ok |
| yolo26-x_640x640.dxnn | 1 | 3 | 48.8 ±0.2 | 48.8 | 155 | 92.9 | 100.0 | 71~80 | 1000 | 403 | ok |
| yolo26-x_640x640.dxnn | 2 | 3 | 34.5 ±0.6 | 17.3 | 134 | 96.5 | 100.0 | 83 | 600~1000 | 403 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n_640x640.dxnn | 4 | 36.9 | 3 | 32.0 |
| yolo26-s_640x640.dxnn | 4 | 31.9 | 3 | 32.7 |
| yolo26-m_640x640.dxnn | 3 | 31.8 | 3 | 31.1 |
| yolo26-l_640x640.dxnn | 2 | 39.3 | 2 | 32.5 |
| yolo26-x_640x640.dxnn | 1 | 47.8 | 1 | 48.8 |

### Pose Estimation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 6 | 3 | 205.4 ±1.4 | 34.2 | 255 | 62.8 | 78.0 | 65~70 | 1000 | 244 | ok |
| yolo26-n-pose_640x640.dxnn | 7 | 3 | 205.7 ±0.2 | 29.4 | 256 | 62.6 | 77.4 | 73~76 | 1000 | 248 | ok |
| yolo26-s-pose_640x640.dxnn | 5 | 3 | 155.0 ±0.8 | 31.0 | 213 | 81.1 | 93.7 | 70~75 | 1000 | 262 | ok |
| yolo26-s-pose_640x640.dxnn | 6 | 3 | 152.2 ±3.4 | 25.4 | 212 | 82.7 | 94.1 | 79~81 | 1000 | 267 | ok |
| yolo26-m-pose_640x640.dxnn | 3 | 3 | 106.8 ±8.3 | 35.6 | 172 | 91.7 | 100.0 | 79~82 | 600~1000 | 280 | ok |
| yolo26-m-pose_640x640.dxnn | 4 | 3 | 89.1 ±4.0 | 22.3 | 160 | 95.4 | 100.0 | 83~84 | 600~1000 | 286 | ok |
| yolo26-l-pose_640x640.dxnn | 2 | 3 | 82.4 ±4.5 | 41.2 | 153 | 93.9 | 100.0 | 79~83 | 800~1000 | 287 | ok |
| yolo26-l-pose_640x640.dxnn | 3 | 3 | 66.5 ±0.7 | 22.2 | 128 | 95.6 | 100.0 | 83 | 600~1000 | 295 | ok |
| yolo26-x-pose_640x640.dxnn | 1 | 3 | 46.8 ±1.5 | 46.8 | 106 | 94.7 | 100.0 | 72~81 | 800~1000 | 417 | ok |
| yolo26-x-pose_640x640.dxnn | 2 | 3 | 32.6 ±1.3 | 16.3 | 90 | 96.9 | 100.0 | 82~84 | 400~1000 | 417 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 8 | 3 | 251.2 ±1.1 | 31.4 | 231 | 78.2 | 90.9 | 67~72 | 1000 | 249 | ok |
| yolo26-n-pose_640x640.dxnn | 9 | 3 | 251.5 ±0.3 | 27.9 | 232 | 78.5 | 91.6 | 76~78 | 1000 | 254 | ok |
| yolo26-s-pose_640x640.dxnn | 5 | 3 | 174.5 ±0.7 | 34.9 | 184 | 91.4 | 99.1 | 69~75 | 1000 | 256 | ok |
| yolo26-s-pose_640x640.dxnn | 6 | 3 | 171.3 ±3.1 | 28.6 | 185 | 91.8 | 98.3 | 78~80 | 1000 | 262 | ok |
| yolo26-m-pose_640x640.dxnn | 3 | 3 | 109.5 ±9.6 | 36.5 | 143 | 94.4 | 100.0 | 79~82 | 600~1000 | 269 | ok |
| yolo26-m-pose_640x640.dxnn | 4 | 3 | 88.9 ±0.2 | 22.2 | 125 | 96.7 | 100.0 | 83 | 600~800 | 279 | ok |
| yolo26-l-pose_640x640.dxnn | 2 | 3 | 82.2 ±4.7 | 41.1 | 114 | 95.0 | 100.0 | 79~82 | 800~1000 | 274 | ok |
| yolo26-l-pose_640x640.dxnn | 3 | 3 | 66.7 ±0.9 | 22.2 | 109 | 96.6 | 100.0 | 83 | 600~1000 | 285 | ok |
| yolo26-x-pose_640x640.dxnn | 1 | 3 | 47.3 ±0.8 | 47.3 | 87 | 95.0 | 100.0 | 71~78 | 800~1000 | 400 | ok |
| yolo26-x-pose_640x640.dxnn | 2 | 3 | 38.6 ±1.9 | 19.3 | 78 | 96.1 | 100.0 | 81~82 | 600~1000 | 400 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-pose_640x640.dxnn | 6 | 34.2 | 8 | 31.4 |
| yolo26-s-pose_640x640.dxnn | 5 | 31.0 | 5 | 34.9 |
| yolo26-m-pose_640x640.dxnn | 3 | 35.6 | 3 | 36.5 |
| yolo26-l-pose_640x640.dxnn | 2 | 41.2 | 2 | 41.1 |
| yolo26-x-pose_640x640.dxnn | 1 | 46.8 | 1 | 47.3 |

### Segmentation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 3 | 3 | 101.5 ±0.1 | 33.8 | 331 | 35.0 | 60.5 | 64~68 | 1000 | 377 | ok |
| yolo26-n-seg_640x640.dxnn | 4 | 3 | 100.8 ±0.2 | 25.2 | 333 | 35.2 | 60.4 | 70~71 | 1000 | 388 | ok |
| yolo26-s-seg_640x640.dxnn | 2 | 3 | 89.9 ±1.8 | 44.9 | 285 | 57.0 | 75.2 | 69~73 | 1000 | 390 | ok |
| yolo26-s-seg_640x640.dxnn | 3 | 3 | 88.0 ±0.2 | 29.3 | 289 | 56.5 | 75.7 | 77~80 | 1000 | 404 | ok |
| yolo26-m-seg_640x640.dxnn | 2 | 3 | 50.0 ±4.4 | 25.0 | 189 | 91.9 | 100.0 | 83~84 | 400~1000 | 423 | ok |
| yolo26-m-seg_640x640.dxnn | 1 | 3 | 67.0 ±0.1 | 67.0 | 233 | 75.1 | 96.2 | 68~76 | 1000 | 405 | ok |
| yolo26-l-seg_640x640.dxnn | 1 | 3 | 59.5 ±0.5 | 59.5 | 217 | 84.7 | 100.0 | 70~78 | 1000 | 418 | ok |
| yolo26-l-seg_640x640.dxnn | 2 | 3 | 43.2 ±5.5 | 21.6 | 178 | 94.4 | 100.0 | 84~86 | 400~1000 | 437 | ok |
| yolo26-x-seg_640x640.dxnn | 1 | 3 | 25.8 ±6.3 | 25.8 | 126 | 94.2 | 100.0 | 80~83 | 400~1000 | 523 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 2 | 3 | 85.1 ±0.1 | 42.6 | 273 | 25.0 | 81.2 | 61~63 | 1000 | 394 | ok |
| yolo26-n-seg_640x640.dxnn | 3 | 3 | 84.9 ±0.2 | 28.3 | 274 | 25.0 | 82.1 | 65~67 | 1000 | 409 | ok |
| yolo26-s-seg_640x640.dxnn | 2 | 3 | 83.2 ±0.1 | 41.6 | 265 | 48.3 | 79.2 | 69~72 | 1000 | 411 | ok |
| yolo26-s-seg_640x640.dxnn | 3 | 3 | 82.8 ±0.2 | 27.6 | 273 | 48.3 | 79.3 | 76~78 | 1000 | 433 | ok |
| yolo26-m-seg_640x640.dxnn | 2 | 3 | 50.1 ±4.1 | 25.1 | 198 | 94.6 | 100.0 | 83~84 | 400~1000 | 447 | ok |
| yolo26-m-seg_640x640.dxnn | 1 | 3 | 76.7 ±0.7 | 76.7 | 246 | 89.6 | 100.0 | 69~77 | 1000 | 426 | ok |
| yolo26-l-seg_640x640.dxnn | 2 | 3 | 43.0 ±3.4 | 21.5 | 178 | 95.7 | 100.0 | 83~85 | 400~1000 | 455 | ok |
| yolo26-l-seg_640x640.dxnn | 1 | 3 | 63.5 ±0.9 | 63.5 | 227 | 90.5 | 100.0 | 70~78 | 800~1000 | 434 | ok |
| yolo26-x-seg_640x640.dxnn | 1 | 3 | 26.1 ±6.1 | 26.1 | 129 | 95.1 | 100.0 | 79~83 | 400~1000 | 543 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-seg_640x640.dxnn | 3 | 33.8 | 2 | 42.6 |
| yolo26-s-seg_640x640.dxnn | 2 | 44.9 | 2 | 41.6 |
| yolo26-m-seg_640x640.dxnn | 1 | 67.0 | 1 | 76.7 |
| yolo26-l-seg_640x640.dxnn | 1 | 59.5 | 1 | 63.5 |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 3 | 3 | 96.7 ±0.9 | 32.2 | 192 | 85.9 | 99.0 | 68~72 | 1000 | 285 | ok |
| yolo26-n-obb_1024x1024.dxnn | 4 | 3 | 96.2 ±1.7 | 24.1 | 190 | 86.3 | 98.9 | 76~78 | 1000 | 293 | ok |
| yolo26-s-obb_1024x1024.dxnn | 2 | 3 | 62.3 ±0.4 | 31.1 | 151 | 94.4 | 100.0 | 73~77 | 1000 | 296 | ok |
| yolo26-s-obb_1024x1024.dxnn | 3 | 3 | 58.1 ±0.5 | 19.4 | 141 | 95.7 | 100.0 | 81~82 | 1000 | 308 | ok |
| yolo26-m-obb_1024x1024.dxnn | 1 | 3 | 41.7 ±0.5 | 41.7 | 114 | 92.6 | 100.0 | 69~78 | 1000 | 314 | ok |
| yolo26-m-obb_1024x1024.dxnn | 2 | 3 | 30.9 ±2.7 | 15.4 | 106 | 95.6 | 100.0 | 82~85 | 400~800 | 330 | ok |
| yolo26-l-obb_1024x1024.dxnn | 1 | 3 | 30.8 ±0.3 | 30.8 | 103 | 93.0 | 100.0 | 71~80 | 1000 | 330 | ok |
| yolo26-l-obb_1024x1024.dxnn | 2 | 3 | 24.0 ±0.3 | 12.0 | 91 | 96.8 | 100.0 | 83~84 | 600~1000 | 343 | ok |
| yolo26-x-obb_1024x1024.dxnn | 1 | 3 | 14.4 ±2.0 | 14.4 | 59 | 94.0 | 100.0 | 81~83 | 600~1000 | 440 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 3 | 3 | 104.7 ±0.7 | 34.9 | 208 | 92.9 | 100.0 | 68~72 | 1000 | 284 | ok |
| yolo26-n-obb_1024x1024.dxnn | 4 | 3 | 102.7 ±3.0 | 25.7 | 209 | 94.2 | 100.0 | 76~78 | 1000 | 296 | ok |
| yolo26-s-obb_1024x1024.dxnn | 2 | 3 | 62.9 ±0.5 | 31.4 | 156 | 94.8 | 100.0 | 73~77 | 1000 | 297 | ok |
| yolo26-s-obb_1024x1024.dxnn | 3 | 3 | 58.4 ±0.5 | 19.5 | 154 | 96.1 | 100.0 | 81~82 | 1000 | 310 | ok |
| yolo26-m-obb_1024x1024.dxnn | 1 | 3 | 41.8 ±0.6 | 41.8 | 133 | 92.2 | 100.0 | 69~77 | 1000 | 312 | ok |
| yolo26-m-obb_1024x1024.dxnn | 2 | 3 | 31.0 ±3.2 | 15.5 | 112 | 95.4 | 100.0 | 82~84 | 400~1000 | 323 | ok |
| yolo26-l-obb_1024x1024.dxnn | 1 | 3 | 30.9 ±0.4 | 30.9 | 110 | 93.7 | 100.0 | 72~80 | 1000 | 326 | ok |
| yolo26-l-obb_1024x1024.dxnn | 2 | 3 | 24.2 ±0.3 | 12.1 | 94 | 97.1 | 100.0 | 83~84 | 600~1000 | 341 | ok |
| yolo26-x-obb_1024x1024.dxnn | 1 | 3 | 14.2 ±1.9 | 14.2 | 63 | 94.5 | 100.0 | 81~83 | 600~1000 | 426 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-obb_1024x1024.dxnn | 3 | 32.2 | 3 | 34.9 |
| yolo26-s-obb_1024x1024.dxnn | 2 | 31.1 | 2 | 31.4 |
| yolo26-m-obb_1024x1024.dxnn | 1 | 41.7 | 1 | 41.8 |
| yolo26-l-obb_1024x1024.dxnn | 1 | 30.8 | 1 | 30.9 |

---
*Report generated by dx-benchmark tool*
