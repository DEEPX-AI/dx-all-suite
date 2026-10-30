# YOLO26 Benchmark Report

**Generated:** 2026-10-23 23:07:41 (UTC+09:00, local)

## Test Timing

| # | Type | Start | End | Duration |
|---|------|-------|-----|----------|
| 1 | run | 2026-10-22 15:29:32 | 2026-10-23 23:07:41 | 31h 38m 8s |

## Executive Summary

### Object Detection

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n_640x640.dxnn | ON | 25.18 | 104.2 | 68.4 | 2 |
| yolo26-n_640x640.dxnn | OFF | 22.69 | 179.5 | 80.0 | 2 |
| yolo26-s_640x640.dxnn | ON | 30.19 | 104.7 | 68.2 | 2 |
| yolo26-s_640x640.dxnn | OFF | 29.99 | 179.2 | 80.2 | 2 |
| yolo26-m_640x640.dxnn | ON | 38.46 | 104.7 | 67.7 | 2 |
| yolo26-m_640x640.dxnn | OFF | 34.20 | 123.1 | 80.2 | 2 |
| yolo26-l_640x640.dxnn | ON | 44.85 | 90.8 | 67.6 | 2 |
| yolo26-l_640x640.dxnn | OFF | 41.43 | 90.7 | 80.4 | 2 |
| yolo26-x_640x640.dxnn | ON | 71.25 | 48.9 | 48.9 | 1 |
| yolo26-x_640x640.dxnn | OFF | 66.82 | 48.9 | 49.0 | 1 |

### Pose Estimation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-pose_640x640.dxnn | ON | 19.32 | 151.8 | 83.3 | 2 |
| yolo26-n-pose_640x640.dxnn | OFF | 18.73 | 264.3 | 113.5 | 3 |
| yolo26-s-pose_640x640.dxnn | ON | 26.67 | 150.8 | 83.2 | 2 |
| yolo26-s-pose_640x640.dxnn | OFF | 24.08 | 184.9 | 113.8 | 3 |
| yolo26-m-pose_640x640.dxnn | ON | 32.67 | 122.5 | 82.9 | 2 |
| yolo26-m-pose_640x640.dxnn | OFF | 31.08 | 122.0 | 110.6 | 3 |
| yolo26-l-pose_640x640.dxnn | ON | 40.61 | 89.2 | 82.2 | 2 |
| yolo26-l-pose_640x640.dxnn | OFF | 37.93 | 89.2 | 89.3 | 2 |
| yolo26-x-pose_640x640.dxnn | ON | 67.96 | 47.6 | 47.7 | 1 |
| yolo26-x-pose_640x640.dxnn | OFF | 65.72 | 47.6 | 47.7 | 1 |

### Segmentation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-seg_640x640.dxnn | ON | 42.58 | 67.5 | 45.4 | 1 |
| yolo26-n-seg_640x640.dxnn | OFF | 39.43 | 95.8 | 55.5 | 1 |
| yolo26-s-seg_640x640.dxnn | ON | 49.23 | 68.3 | 45.4 | 1 |
| yolo26-s-seg_640x640.dxnn | OFF | 43.58 | 95.8 | 55.1 | 1 |
| yolo26-m-seg_640x640.dxnn | ON | 63.21 | 67.7 | 44.7 | 1 |
| yolo26-m-seg_640x640.dxnn | OFF | 60.97 | 77.0 | 54.5 | 1 |
| yolo26-l-seg_640x640.dxnn | ON | 66.93 | 64.9 | 44.5 | 1 |
| yolo26-l-seg_640x640.dxnn | OFF | 68.99 | 64.7 | 53.4 | 1 |
| yolo26-x-seg_640x640.dxnn | ON | 105.55 | 34.4 | 34.0 | 1 |
| yolo26-x-seg_640x640.dxnn | OFF | 105.37 | 34.3 | 34.1 | 1 |

### Oriented BBox (OBB)

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-obb_1024x1024.dxnn | ON | 34.65 | 107.2 | 70.4 | 2 |
| yolo26-n-obb_1024x1024.dxnn | OFF | 34.44 | 106.9 | 82.7 | 2 |
| yolo26-s-obb_1024x1024.dxnn | ON | 52.29 | 62.7 | 62.5 | 2 |
| yolo26-s-obb_1024x1024.dxnn | OFF | 49.80 | 63.5 | 63.0 | 2 |
| yolo26-m-obb_1024x1024.dxnn | ON | 68.03 | 42.5 | 41.8 | 1 |
| yolo26-m-obb_1024x1024.dxnn | OFF | 66.49 | 42.6 | 42.2 | 1 |
| yolo26-l-obb_1024x1024.dxnn | ON | 87.87 | 31.0 | 31.1 | 1 |
| yolo26-l-obb_1024x1024.dxnn | OFF | 85.38 | 30.8 | 31.1 | 1 |
| yolo26-x-obb_1024x1024.dxnn | ON | 156.46 | 17.0 | 16.9 | — |
| yolo26-x-obb_1024x1024.dxnn | OFF | 153.76 | 17.0 | 16.9 | — |

### Classification

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-cls-n_224x224.dxnn | ON | 1.43 | 3460.3 | 188.8 | — |
| yolo26-cls-n_224x224.dxnn | OFF | 1.45 | 3457.9 | 189.7 | — |
| yolo26-cls-s_224x224.dxnn | ON | 2.07 | 1896.1 | 188.9 | — |
| yolo26-cls-s_224x224.dxnn | OFF | 2.10 | 1897.5 | 188.5 | — |
| yolo26-cls-m_224x224.dxnn | ON | 2.58 | 1352.0 | 188.8 | — |
| yolo26-cls-m_224x224.dxnn | OFF | 2.62 | 1341.4 | 188.8 | — |
| yolo26-cls-l_224x224.dxnn | ON | 3.88 | 870.6 | 188.3 | — |
| yolo26-cls-l_224x224.dxnn | OFF | 3.91 | 871.1 | 188.9 | — |
| yolo26-cls-x_224x224.dxnn | ON | 6.30 | 494.7 | 187.8 | — |
| yolo26-cls-x_224x224.dxnn | OFF | 6.31 | 494.6 | 188.2 | — |

## Environment

| Item | Value |
|------|-------|
| Product | RPi5B |
| Hostname | raspberrypi |
| OS | Debian GNU/Linux 12 (bookworm) |
| Kernel | 6.12.93+rpt-rpi-2712 |
| CPU | Cortex-A76 |
| CPU Threads | 4 |
| CPU Governor | ondemand |
| RAM | 7.9 GiB |
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
| NPU PCIe | Gen3 X1 [01:00:00] |
| Host Health | throttled=0x0, EXT5V 5.21 V |

### Tools

| Tool | Available | Version |
|------|-----------|---------|
| run_model | Yes | DXRT v3.5.0 run_model |
| dxrt-cli | Yes | DXRT v3.5.0 (build: 5.502926e) |
| gst-launch-1.0 | Yes | gst-launch-1.0 version 1.22.0 |
| gst-inspect-1.0 | Yes | gst-inspect-1.0 version 1.22.0 |
| time | Yes | unknown |
| ffprobe | Yes | ffprobe version 5.1.9-0+deb12u1+rpt1 Copyright (c) 2007-2026... |
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
| NPU Idle Temp (settled) | 34.0 °C |
| Cool-down Target | ≤ 44.0 °C |
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
| yolo26-n_640x640.dxnn | 104.2 ±0.8 | 5 | 190 | 24.6 | 75.8 | 40~41 | 1000 | ok |
| yolo26-s_640x640.dxnn | 104.7 ±1.7 | 6 | 192 | 45.0 | 75.2 | 46~47 | 1000 | ok |
| yolo26-m_640x640.dxnn | 104.7 ±0.9 | 6 | 186 | 81.1 | 88.7 | 50 | 1000 | ok |
| yolo26-l_640x640.dxnn | 90.8 ±0.0 | 6 | 144 | 93.3 | 100.0 | 51 | 1000 | ok |
| yolo26-x_640x640.dxnn | 48.9 ±0.0 | 5 | 68 | 93.6 | 100.0 | 51 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n_640x640.dxnn | 5 | [3]:89.4 · [4]:102.7 · **[5]:105.0 ★** · [6]:104.6 · [7]:103.5 · [8]:104.4 |
| yolo26-s_640x640.dxnn | 6 | [3]:81.3 · [4]:98.6 · [5]:104.4 · **[6]:106.0 ★** · [7]:105.0 · [8]:106.1 · [9]:104.0 |
| yolo26-m_640x640.dxnn | 6 | [3]:67.4 · [4]:85.0 · [5]:98.5 · **[6]:105.1 ★** · [7]:105.3 · [8]:103.6 · [9]:104.9 |
| yolo26-l_640x640.dxnn | 6 | [3]:55.9 · [4]:71.8 · [5]:86.1 · **[6]:90.5 ★** · [7]:90.5 · [8]:90.6 · [9]:90.6 |
| yolo26-x_640x640.dxnn | 5 | [3]:36.0 · [4]:47.5 · **[5]:48.7 ★** · [6]:48.8 · [7]:48.8 · [8]:48.8 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n_640x640.dxnn | 179.5 ±0.2 | 6 | 124 | 45.3 | 74.8 | 46 | 1000 | ok |
| yolo26-s_640x640.dxnn | 179.2 ±0.1 | 7 | 110 | 85.9 | 92.8 | 48~49 | 1000 | ok |
| yolo26-m_640x640.dxnn | 123.1 ±0.4 | 5 | 72 | 97.1 | 100.0 | 51 | 1000 | ok |
| yolo26-l_640x640.dxnn | 90.7 ±0.0 | 5 | 53 | 93.0 | 100.0 | 51 | 1000 | ok |
| yolo26-x_640x640.dxnn | 48.9 ±0.0 | 4 | 35 | 93.2 | 100.0 | 51~52 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n_640x640.dxnn | 6 | [3]:113.8 · [4]:139.3 · [5]:173.2 · **[6]:179.1 ★** · [7]:179.2 · [8]:179.2 · [9]:179.1 |
| yolo26-s_640x640.dxnn | 7 | [3]:92.4 · [4]:121.7 · [5]:147.2 · [6]:174.2 · **[7]:178.8 ★** · [8]:179.2 · [9]:179.2 · [10]:179.2 |
| yolo26-m_640x640.dxnn | 5 | [3]:77.5 · [4]:99.1 · **[5]:123.0 ★** · [6]:123.4 · [7]:123.5 · [8]:123.4 |
| yolo26-l_640x640.dxnn | 5 | [3]:63.4 · [4]:86.1 · **[5]:90.5 ★** · [6]:90.6 · [7]:90.6 · [8]:90.7 |
| yolo26-x_640x640.dxnn | 4 | [3]:38.3 · **[4]:48.8 ★** · [5]:48.9 · [6]:48.9 · [7]:48.9 |


#### Pose Estimation

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 151.8 ±1.5 | 6 | 188 | 41.2 | 72.1 | 46 | 1000 | ok |
| yolo26-s-pose_640x640.dxnn | 150.8 ±0.6 | 7 | 186 | 75.5 | 85.1 | 48 | 1000 | ok |
| yolo26-m-pose_640x640.dxnn | 122.5 ±0.1 | 6 | 107 | 98.0 | 100.0 | 51 | 1000 | ok |
| yolo26-l-pose_640x640.dxnn | 89.2 ±0.0 | 5 | 79 | 96.2 | 100.0 | 50~51 | 1000 | ok |
| yolo26-x-pose_640x640.dxnn | 47.6 ±0.0 | 4 | 43 | 94.3 | 100.0 | 51 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-pose_640x640.dxnn | 6 | [3]:112.7 · [4]:137.3 · [5]:149.1 · **[6]:151.2 ★** · [7]:151.3 · [8]:150.9 · [9]:151.1 |
| yolo26-s-pose_640x640.dxnn | 7 | [3]:92.8 · [4]:118.4 · [5]:138.2 · [6]:149.6 · **[7]:152.4 ★** · [8]:152.8 · [9]:152.4 · [10]:151.0 |
| yolo26-m-pose_640x640.dxnn | 6 | [3]:75.8 · [4]:98.8 · [5]:120.4 · **[6]:122.3 ★** · [7]:122.4 · [8]:122.4 · [9]:122.4 |
| yolo26-l-pose_640x640.dxnn | 5 | [3]:62.0 · [4]:81.2 · **[5]:89.0 ★** · [6]:89.1 · [7]:89.1 · [8]:89.1 |
| yolo26-x-pose_640x640.dxnn | 4 | [3]:38.2 · **[4]:47.4 ★** · [5]:47.5 · [6]:47.5 · [7]:47.5 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 264.3 ±0.7 | 7 | 106 | 82.7 | 88.6 | 47~48 | 1000 | ok |
| yolo26-s-pose_640x640.dxnn | 184.9 ±0.6 | 6 | 73 | 94.4 | 100.0 | 49 | 1000 | ok |
| yolo26-m-pose_640x640.dxnn | 122.0 ±0.1 | 5 | 51 | 95.0 | 100.0 | 51 | 1000 | ok |
| yolo26-l-pose_640x640.dxnn | 89.2 ±0.0 | 5 | 41 | 93.6 | 100.0 | 51 | 1000 | ok |
| yolo26-x-pose_640x640.dxnn | 47.6 ±0.0 | 4 | 21 | 94.2 | 100.0 | 51 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-pose_640x640.dxnn | 7 | [3]:128.5 · [4]:175.7 · [5]:209.4 · [6]:247.7 · **[7]:262.9 ★** · [8]:264.3 · [9]:264.7 · [10]:264.3 |
| yolo26-s-pose_640x640.dxnn | 6 | [3]:107.2 · [4]:141.2 · [5]:181.8 · **[6]:183.9 ★** · [7]:184.1 · [8]:184.2 · [9]:184.1 |
| yolo26-m-pose_640x640.dxnn | 5 | [3]:82.3 · [4]:115.1 · **[5]:121.8 ★** · [6]:121.8 · [7]:121.9 · [8]:121.9 |
| yolo26-l-pose_640x640.dxnn | 5 | [3]:65.1 · [4]:87.7 · **[5]:89.0 ★** · [6]:89.1 · [7]:89.1 · [8]:89.1 |
| yolo26-x-pose_640x640.dxnn | 4 | [3]:40.7 · **[4]:47.5 ★** · [5]:47.5 · [6]:47.5 · [7]:47.5 |


#### Segmentation

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 67.5 ±0.7 | 5 | 233 | 19.4 | 62.0 | 44 | 1000 | ok |
| yolo26-s-seg_640x640.dxnn | 68.3 ±0.2 | 6 | 235 | 39.4 | 70.7 | 46~47 | 1000 | ok |
| yolo26-m-seg_640x640.dxnn | 67.7 ±0.2 | 7 | 231 | 75.7 | 89.2 | 51 | 1000 | ok |
| yolo26-l-seg_640x640.dxnn | 64.9 ±0.0 | 7 | 177 | 94.8 | 100.0 | 52 | 1000 | ok |
| yolo26-x-seg_640x640.dxnn | 34.4 ±0.3 | 5 | 75 | 92.1 | 100.0 | 52 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-seg_640x640.dxnn | 5 | [3]:55.6 · [4]:64.8 · **[5]:67.2 ★** · [6]:67.3 · [7]:67.5 · [8]:67.8 |
| yolo26-s-seg_640x640.dxnn | 6 | [3]:50.8 · [4]:60.3 · [5]:66.8 · **[6]:67.4 ★** · [7]:67.4 · [8]:67.5 · [9]:67.3 · [10]:67.4 · [11]:67.5 |
| yolo26-m-seg_640x640.dxnn | 7 | [3]:40.7 · [4]:52.1 · [5]:59.8 · [6]:66.2 · **[7]:66.9 ★** · [8]:67.2 · [9]:67.0 · [10]:67.0 |
| yolo26-l-seg_640x640.dxnn | 7 | [3]:37.8 · [4]:48.6 · [5]:57.9 · [6]:63.7 · **[7]:64.5 ★** · [8]:64.6 · [9]:64.7 · [10]:64.7 |
| yolo26-x-seg_640x640.dxnn | 5 | [3]:24.6 · [4]:32.5 · **[5]:34.3 ★** · [6]:34.0 · [7]:34.1 · [8]:34.5 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 95.8 ±0.0 | 5 | 137 | 28.5 | 88.0 | 46 | 1000 | ok |
| yolo26-s-seg_640x640.dxnn | 95.8 ±0.0 | 6 | 148 | 55.1 | 88.4 | 47~48 | 1000 | ok |
| yolo26-m-seg_640x640.dxnn | 77.0 ±0.1 | 6 | 93 | 95.0 | 100.0 | 52 | 1000 | ok |
| yolo26-l-seg_640x640.dxnn | 64.7 ±0.2 | 5 | 83 | 93.7 | 100.0 | 51~52 | 1000 | ok |
| yolo26-x-seg_640x640.dxnn | 34.3 ±0.2 | 5 | 40 | 92.4 | 100.0 | 52~53 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-seg_640x640.dxnn | 5 | [3]:77.5 · [4]:90.3 · **[5]:95.5 ★** · [6]:95.6 · [7]:95.6 · [8]:95.5 |
| yolo26-s-seg_640x640.dxnn | 6 | [3]:61.1 · [4]:72.1 · [5]:90.3 · **[6]:95.5 ★** · [7]:95.5 · [8]:95.5 · [9]:95.4 |
| yolo26-m-seg_640x640.dxnn | 6 | [3]:49.3 · [4]:63.7 · [5]:75.5 · **[6]:77.0 ★** · [7]:77.1 · [8]:76.8 · [9]:77.1 |
| yolo26-l-seg_640x640.dxnn | 5 | [3]:44.2 · [4]:55.8 · **[5]:64.6 ★** · [6]:64.7 · [7]:64.8 · [8]:64.8 |
| yolo26-x-seg_640x640.dxnn | 5 | [3]:26.8 · [4]:33.9 · **[5]:34.2 ★** · [6]:34.4 · [7]:34.3 · [8]:34.4 · [9]:34.1 |


#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 107.2 ±0.0 | 6 | 106 | 96.3 | 100.0 | 47~48 | 1000 | ok |
| yolo26-s-obb_1024x1024.dxnn | 62.7 ±0.2 | 5 | 64 | 96.0 | 100.0 | 48~49 | 1000 | ok |
| yolo26-m-obb_1024x1024.dxnn | 42.5 ±0.0 | 4 | 44 | 94.5 | 100.0 | 51 | 1000 | ok |
| yolo26-l-obb_1024x1024.dxnn | 31.0 ±0.0 | 4 | 34 | 92.7 | 100.0 | 50~51 | 1000 | ok |
| yolo26-x-obb_1024x1024.dxnn | 17.0 ±0.0 | 4 | 18 | 90.4 | 100.0 | 51 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-obb_1024x1024.dxnn | 6 | [3]:65.8 · [4]:85.5 · [5]:101.0 · **[6]:106.8 ★** · [7]:106.9 · [8]:106.9 · [9]:106.9 |
| yolo26-s-obb_1024x1024.dxnn | 5 | [3]:46.7 · [4]:59.8 · **[5]:62.4 ★** · [6]:62.4 · [7]:62.4 · [8]:62.4 |
| yolo26-m-obb_1024x1024.dxnn | 4 | [3]:34.2 · **[4]:42.4 ★** · [5]:42.4 · [6]:42.4 · [7]:42.4 |
| yolo26-l-obb_1024x1024.dxnn | 4 | [3]:26.8 · **[4]:30.9 ★** · [5]:30.9 · [6]:30.9 · [7]:30.9 |
| yolo26-x-obb_1024x1024.dxnn | 4 | [3]:15.5 · **[4]:16.9 ★** · [5]:16.9 · [6]:16.9 · [7]:16.9 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 106.9 ±0.1 | 5 | 54 | 96.0 | 100.0 | 48 | 1000 | ok |
| yolo26-s-obb_1024x1024.dxnn | 63.5 ±0.0 | 5 | 35 | 95.2 | 100.0 | 49 | 1000 | ok |
| yolo26-m-obb_1024x1024.dxnn | 42.6 ±0.0 | 5 | 22 | 96.3 | 100.0 | 51 | 1000 | ok |
| yolo26-l-obb_1024x1024.dxnn | 30.8 ±0.1 | 4 | 17 | 92.1 | 100.0 | 50~51 | 1000 | ok |
| yolo26-x-obb_1024x1024.dxnn | 17.0 ±0.0 | 4 | 10 | 91.8 | 100.0 | 51~52 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-obb_1024x1024.dxnn | 5 | [3]:65.9 · [4]:90.4 · **[5]:106.6 ★** · [6]:107.0 · [7]:107.0 · [8]:107.0 |
| yolo26-s-obb_1024x1024.dxnn | 5 | [3]:48.2 · [4]:59.5 · **[5]:63.3 ★** · [6]:63.4 · [7]:63.4 · [8]:63.4 |
| yolo26-m-obb_1024x1024.dxnn | 5 | [3]:35.2 · [4]:42.0 · **[5]:42.4 ★** · [6]:42.5 · [7]:42.5 · [8]:42.5 |
| yolo26-l-obb_1024x1024.dxnn | 4 | [3]:27.9 · **[4]:30.8 ★** · [5]:30.9 · [6]:30.9 · [7]:30.9 |
| yolo26-x-obb_1024x1024.dxnn | 4 | [3]:15.3 · **[4]:16.9 ★** · [5]:16.9 · [6]:16.9 · [7]:16.9 |


#### Classification

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-cls-n_224x224.dxnn | 3460.3 ±5.5 | 9 | 62 | 90.8 | 94.5 | 46 | 1000 | ok |
| yolo26-cls-s_224x224.dxnn | 1896.1 ±1.1 | 5 | 37 | 89.0 | 94.1 | 47 | 1000 | ok |
| yolo26-cls-m_224x224.dxnn | 1352.0 ±1.1 | 6 | 28 | 91.5 | 96.2 | 49~50 | 1000 | ok |
| yolo26-cls-l_224x224.dxnn | 870.6 ±0.3 | 4 | 18 | 94.1 | 98.1 | 48~49 | 1000 | ok |
| yolo26-cls-x_224x224.dxnn | 494.7 ±0.1 | 4 | 10 | 93.8 | 99.9 | 49~50 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-cls-n_224x224.dxnn | 9 | [3]:1966.3 · [4]:2640.5 · [5]:3243.6 · [6]:3363.9 · [7]:3388.2 · [8]:3423.9 · **[9]:3455.2 ★** · [10]:3460.9 · [11]:3463.1 · [12]:3465.0 · [13]:3458.9 |
| yolo26-cls-s_224x224.dxnn | 5 | [3]:1336.0 · [4]:1786.1 · **[5]:1894.5 ★** · [6]:1902.6 · [7]:1900.6 · [8]:1911.2 |
| yolo26-cls-m_224x224.dxnn | 6 | [3]:1025.4 · [4]:1327.7 · [5]:1339.8 · **[6]:1352.3 ★** · [7]:1353.9 · [8]:1357.7 · [9]:1357.6 |
| yolo26-cls-l_224x224.dxnn | 4 | [3]:728.4 · **[4]:871.2 ★** · [5]:878.7 · [6]:879.0 · [7]:878.9 |
| yolo26-cls-x_224x224.dxnn | 4 | [3]:428.5 · **[4]:494.5 ★** · [5]:494.4 · [6]:494.4 · [7]:494.7 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-cls-n_224x224.dxnn | 3457.9 ±14.2 | 9 | 62 | 89.3 | 95.6 | 46 | 1000 | ok |
| yolo26-cls-s_224x224.dxnn | 1897.5 ±3.1 | 5 | 34 | 90.6 | 94.6 | 47 | 1000 | ok |
| yolo26-cls-m_224x224.dxnn | 1341.4 ±1.3 | 5 | 27 | 91.5 | 96.4 | 49 | 1000 | ok |
| yolo26-cls-l_224x224.dxnn | 871.1 ±0.6 | 4 | 18 | 93.6 | 98.1 | 48~49 | 1000 | ok |
| yolo26-cls-x_224x224.dxnn | 494.6 ±0.1 | 4 | 10 | 93.5 | 99.7 | 50 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-cls-n_224x224.dxnn | 9 | [3]:1940.4 · [4]:2647.6 · [5]:3235.3 · [6]:3377.8 · [7]:3400.9 · [8]:3427.4 · **[9]:3468.1 ★** · [10]:3476.0 · [11]:3478.3 · [12]:3475.4 |
| yolo26-cls-s_224x224.dxnn | 5 | [3]:1334.6 · [4]:1800.7 · **[5]:1893.7 ★** · [6]:1895.4 · [7]:1900.6 · [8]:1909.8 |
| yolo26-cls-m_224x224.dxnn | 5 | [3]:1026.1 · [4]:1330.4 · **[5]:1343.2 ★** · [6]:1342.1 · [7]:1348.4 · [8]:1352.2 · [9]:1351.8 · [10]:1354.0 |
| yolo26-cls-l_224x224.dxnn | 4 | [3]:723.1 · **[4]:870.2 ★** · [5]:878.5 · [6]:878.6 · [7]:878.7 |
| yolo26-cls-x_224x224.dxnn | 4 | [3]:420.6 · **[4]:494.4 ★** · [5]:494.5 · [6]:494.6 · [7]:494.6 |


### Latency (Single-Core, Sync)

#### Object Detection

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_640x640.dxnn | 39.7 | 25.18 | 22.60 | 2.59 | 35 | ok |
| yolo26-s_640x640.dxnn | 33.1 | 30.19 | 27.79 | 2.40 | 43 | ok |
| yolo26-m_640x640.dxnn | 26.0 | 38.46 | 35.92 | 2.53 | 46 | ok |
| yolo26-l_640x640.dxnn | 22.3 | 44.85 | 42.38 | 2.47 | 46 | ok |
| yolo26-x_640x640.dxnn | 14.0 | 71.25 | 68.66 | 2.59 | 46 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_640x640.dxnn | 44.1 | 22.69 | 22.69 | N/A | 43 | ok |
| yolo26-s_640x640.dxnn | 33.3 | 29.99 | 29.99 | N/A | 45 | ok |
| yolo26-m_640x640.dxnn | 29.2 | 34.20 | 34.20 | N/A | 46 | ok |
| yolo26-l_640x640.dxnn | 24.1 | 41.43 | 41.43 | N/A | 46 | ok |
| yolo26-x_640x640.dxnn | 15.0 | 66.82 | 66.82 | N/A | 46 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-pose_640x640.dxnn | 51.8 | 19.32 | 17.92 | 1.40 | 45 | ok |
| yolo26-s-pose_640x640.dxnn | 37.5 | 26.67 | 25.12 | 1.55 | 45 | ok |
| yolo26-m-pose_640x640.dxnn | 30.6 | 32.67 | 31.14 | 1.53 | 46 | ok |
| yolo26-l-pose_640x640.dxnn | 24.6 | 40.61 | 39.17 | 1.44 | 46 | ok |
| yolo26-x-pose_640x640.dxnn | 14.7 | 67.96 | 66.46 | 1.50 | 46 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-pose_640x640.dxnn | 53.4 | 18.73 | 18.73 | N/A | 44 | ok |
| yolo26-s-pose_640x640.dxnn | 41.5 | 24.08 | 24.08 | N/A | 45 | ok |
| yolo26-m-pose_640x640.dxnn | 32.2 | 31.08 | 31.08 | N/A | 46 | ok |
| yolo26-l-pose_640x640.dxnn | 26.4 | 37.93 | 37.93 | N/A | 46 | ok |
| yolo26-x-pose_640x640.dxnn | 15.2 | 65.72 | 65.72 | N/A | 47 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-seg_640x640.dxnn | 23.5 | 42.58 | 39.59 | 2.99 | 44 | ok |
| yolo26-s-seg_640x640.dxnn | 20.3 | 49.23 | 46.37 | 2.86 | 43 | ok |
| yolo26-m-seg_640x640.dxnn | 15.8 | 63.21 | 60.32 | 2.89 | 46 | ok |
| yolo26-l-seg_640x640.dxnn | 14.9 | 66.93 | 64.02 | 2.91 | 46 | ok |
| yolo26-x-seg_640x640.dxnn | 9.5 | 105.55 | 102.53 | 3.02 | 47 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-seg_640x640.dxnn | 25.4 | 39.43 | 39.43 | N/A | 43 | ok |
| yolo26-s-seg_640x640.dxnn | 22.9 | 43.58 | 43.58 | N/A | 45 | ok |
| yolo26-m-seg_640x640.dxnn | 16.4 | 60.97 | 60.97 | N/A | 46 | ok |
| yolo26-l-seg_640x640.dxnn | 14.5 | 68.99 | 68.99 | N/A | 46 | ok |
| yolo26-x-seg_640x640.dxnn | 9.5 | 105.37 | 105.37 | N/A | 46 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-obb_1024x1024.dxnn | 28.9 | 34.65 | 33.03 | 1.62 | 45 | ok |
| yolo26-s-obb_1024x1024.dxnn | 19.1 | 52.29 | 50.54 | 1.75 | 45 | ok |
| yolo26-m-obb_1024x1024.dxnn | 14.7 | 68.03 | 66.37 | 1.66 | 47 | ok |
| yolo26-l-obb_1024x1024.dxnn | 11.4 | 87.87 | 86.15 | 1.72 | 47 | ok |
| yolo26-x-obb_1024x1024.dxnn | 6.4 | 156.46 | 154.67 | 1.80 | 48 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-obb_1024x1024.dxnn | 29.0 | 34.44 | 34.44 | N/A | 45 | ok |
| yolo26-s-obb_1024x1024.dxnn | 20.1 | 49.80 | 49.80 | N/A | 46 | ok |
| yolo26-m-obb_1024x1024.dxnn | 15.0 | 66.49 | 66.49 | N/A | 47 | ok |
| yolo26-l-obb_1024x1024.dxnn | 11.7 | 85.38 | 85.38 | N/A | 47 | ok |
| yolo26-x-obb_1024x1024.dxnn | 6.5 | 153.76 | 153.76 | N/A | 48 | ok |

#### Classification

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-cls-n_224x224.dxnn | 700.7 | 1.43 | 1.43 | N/A | 45 | ok |
| yolo26-cls-s_224x224.dxnn | 483.9 | 2.07 | 2.07 | N/A | 43 | ok |
| yolo26-cls-m_224x224.dxnn | 387.1 | 2.58 | 2.58 | N/A | 44 | ok |
| yolo26-cls-l_224x224.dxnn | 257.5 | 3.88 | 3.88 | N/A | 44 | ok |
| yolo26-cls-x_224x224.dxnn | 158.6 | 6.30 | 6.30 | N/A | 45 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-cls-n_224x224.dxnn | 690.2 | 1.45 | 1.45 | N/A | 44 | ok |
| yolo26-cls-s_224x224.dxnn | 477.1 | 2.10 | 2.10 | N/A | 44 | ok |
| yolo26-cls-m_224x224.dxnn | 381.6 | 2.62 | 2.62 | N/A | 44 | ok |
| yolo26-cls-l_224x224.dxnn | 256.0 | 3.91 | 3.91 | N/A | 44 | ok |
| yolo26-cls-x_224x224.dxnn | 158.6 | 6.31 | 6.31 | N/A | 45 | ok |

## E2E Pipeline (Single-Stream)

### Object Detection

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | avdec_h264 | 3455 | 3 | 68.4 ±0.2 | 50.54 | 312 | 17.1 | 40.1 | 41 | 1000 | 420 | ok |
| yolo26-s_640x640.dxnn | avdec_h264 | 3455 | 3 | 68.2 ±0.2 | 50.62 | 309 | 29.9 | 59.7 | 46~47 | 1000 | 442 | ok |
| yolo26-m_640x640.dxnn | avdec_h264 | 3455 | 3 | 67.7 ±0.3 | 51.00 | 298 | 48.4 | 74.0 | 51~53 | 1000 | 478 | ok |
| yolo26-l_640x640.dxnn | avdec_h264 | 3455 | 3 | 67.6 ±0.2 | 51.09 | 280 | 66.9 | 87.1 | 53~57 | 1000 | 489 | ok |
| yolo26-x_640x640.dxnn | avdec_h264 | 3455 | 3 | 48.9 ±0.1 | 70.66 | 135 | 93.6 | 100.0 | 61~68 | 1000 | 584 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | avdec_h264 | 3455 | 3 | 80.0 ±0.2 | 43.18 | 304 | 18.3 | 57.2 | 43~45 | 1000 | 449 | ok |
| yolo26-s_640x640.dxnn | avdec_h264 | 3455 | 3 | 80.2 ±0.1 | 43.06 | 304 | 33.6 | 70.8 | 47 | 1000 | 471 | ok |
| yolo26-m_640x640.dxnn | avdec_h264 | 3455 | 3 | 80.2 ±0.4 | 43.06 | 298 | 55.3 | 85.4 | 51~55 | 1000 | 500 | ok |
| yolo26-l_640x640.dxnn | avdec_h264 | 3455 | 3 | 80.4 ±0.4 | 42.95 | 300 | 79.8 | 92.1 | 53~58 | 1000 | 517 | ok |
| yolo26-x_640x640.dxnn | avdec_h264 | 3455 | 3 | 49.0 ±0.1 | 70.52 | 149 | 93.6 | 100.0 | 61~69 | 1000 | 583 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n_640x640.dxnn | 68.4 | 80.0 | -11.6 | -14.5% |
| yolo26-s_640x640.dxnn | 68.2 | 80.2 | -12.0 | -14.9% |
| yolo26-m_640x640.dxnn | 67.7 | 80.2 | -12.5 | -15.6% |
| yolo26-l_640x640.dxnn | 67.6 | 80.4 | -12.8 | -15.9% |
| yolo26-x_640x640.dxnn | 48.9 | 49.0 | -0.1 | -0.2% |

### Pose Estimation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 83.3 ±0.2 | 41.46 | 321 | 22.1 | 48.9 | 45 | 1000 | 401 | ok |
| yolo26-s-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 83.2 ±0.1 | 41.53 | 317 | 39.4 | 68.3 | 47~48 | 1000 | 424 | ok |
| yolo26-m-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 82.9 ±0.3 | 41.69 | 303 | 59.3 | 83.2 | 52~55 | 1000 | 458 | ok |
| yolo26-l-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 82.2 ±0.2 | 42.02 | 272 | 84.6 | 96.7 | 54~59 | 1000 | 472 | ok |
| yolo26-x-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 47.7 ±0.1 | 72.42 | 105 | 94.5 | 100.0 | 61~70 | 1000 | 568 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 113.5 ±0.2 | 30.43 | 300 | 29.2 | 60.0 | 46 | 1000 | 375 | ok |
| yolo26-s-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 113.8 ±0.9 | 30.36 | 299 | 52.8 | 77.0 | 48~49 | 1000 | 408 | ok |
| yolo26-m-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 110.6 ±0.2 | 31.23 | 277 | 81.8 | 96.4 | 53~58 | 1000 | 448 | ok |
| yolo26-l-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 89.3 ±0.3 | 38.68 | 180 | 90.8 | 100.0 | 55~59 | 1000 | 463 | ok |
| yolo26-x-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 47.7 ±0.1 | 72.40 | 86 | 95.3 | 100.0 | 61~70 | 1000 | 556 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-pose_640x640.dxnn | 83.3 | 113.5 | -30.2 | -26.6% |
| yolo26-s-pose_640x640.dxnn | 83.2 | 113.8 | -30.6 | -26.9% |
| yolo26-m-pose_640x640.dxnn | 82.9 | 110.6 | -27.8 | -25.1% |
| yolo26-l-pose_640x640.dxnn | 82.2 | 89.3 | -7.1 | -7.9% |
| yolo26-x-pose_640x640.dxnn | 47.7 | 47.7 | -0.0 | -0.0% |

### Segmentation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 45.4 ±0.0 | 76.12 | 312 | 14.4 | 34.3 | 43 | 1000 | 540 | ok |
| yolo26-s-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 45.4 ±0.2 | 76.11 | 303 | 26.1 | 58.9 | 47 | 1000 | 564 | ok |
| yolo26-m-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 44.7 ±0.1 | 77.26 | 285 | 49.2 | 76.9 | 54~58 | 1000 | 605 | ok |
| yolo26-l-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 44.5 ±0.4 | 77.67 | 268 | 60.9 | 88.1 | 57~60 | 1000 | 618 | ok |
| yolo26-x-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 34.0 ±0.5 | 101.63 | 143 | 94.4 | 100.0 | 68~76 | 800~1000 | 724 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 55.5 ±0.5 | 62.27 | 336 | 16.7 | 50.0 | 45 | 1000 | 583 | ok |
| yolo26-s-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 55.1 ±0.0 | 62.76 | 334 | 31.5 | 68.6 | 47~48 | 1000 | 607 | ok |
| yolo26-m-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 54.5 ±0.0 | 63.42 | 318 | 60.4 | 81.4 | 56~61 | 1000 | 650 | ok |
| yolo26-l-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 53.4 ±1.1 | 64.72 | 294 | 75.0 | 94.9 | 58~63 | 1000 | 650 | ok |
| yolo26-x-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 34.1 ±0.5 | 101.23 | 147 | 94.6 | 100.0 | 73~80 | 1000 | 733 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-seg_640x640.dxnn | 45.4 | 55.5 | -10.1 | -18.2% |
| yolo26-s-seg_640x640.dxnn | 45.4 | 55.1 | -9.7 | -17.5% |
| yolo26-m-seg_640x640.dxnn | 44.7 | 54.5 | -9.8 | -17.9% |
| yolo26-l-seg_640x640.dxnn | 44.5 | 53.4 | -8.9 | -16.7% |
| yolo26-x-seg_640x640.dxnn | 34.0 | 34.1 | -0.1 | -0.4% |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 70.4 ±0.4 | 37.52 | 313 | 54.1 | 79.3 | 47~49 | 1000 | 450 | ok |
| yolo26-s-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 62.5 ±0.3 | 42.24 | 225 | 91.4 | 100.0 | 51~55 | 1000 | 480 | ok |
| yolo26-m-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 41.8 ±0.5 | 63.12 | 127 | 92.4 | 100.0 | 59~65 | 1000 | 513 | ok |
| yolo26-l-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 31.1 ±0.1 | 84.86 | 94 | 93.7 | 100.0 | 61~68 | 1000 | 530 | ok |
| yolo26-x-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 16.9 ±0.3 | 155.88 | 55 | 94.2 | 100.0 | 70~78 | 1000 | 629 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 82.7 ±0.5 | 31.94 | 308 | 62.7 | 84.3 | 48~50 | 1000 | 432 | ok |
| yolo26-s-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 63.0 ±0.4 | 41.91 | 202 | 90.0 | 100.0 | 51~54 | 1000 | 475 | ok |
| yolo26-m-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 42.2 ±0.5 | 62.56 | 127 | 93.6 | 100.0 | 59~66 | 1000 | 504 | ok |
| yolo26-l-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 31.1 ±0.1 | 84.86 | 94 | 94.1 | 100.0 | 61~68 | 1000 | 522 | ok |
| yolo26-x-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 16.9 ±0.3 | 155.90 | 57 | 94.2 | 100.0 | 70~78 | 1000 | 622 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-obb_1024x1024.dxnn | 70.4 | 82.7 | -12.3 | -14.9% |
| yolo26-s-obb_1024x1024.dxnn | 62.5 | 63.0 | -0.5 | -0.8% |
| yolo26-m-obb_1024x1024.dxnn | 41.8 | 42.2 | -0.4 | -0.9% |
| yolo26-l-obb_1024x1024.dxnn | 31.1 | 31.1 | +0.0 | +0.0% |
| yolo26-x-obb_1024x1024.dxnn | 16.9 | 16.9 | +0.0 | +0.1% |

### Classification

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-cls-n_224x224.dxnn | avdec_h264 | 3455 | 3 | 188.8 ±1.1 | 18.30 | 268 | 4.1 | 13.2 | 43~44 | 1000 | 267 | ok |
| yolo26-cls-s_224x224.dxnn | avdec_h264 | 3455 | 3 | 188.9 ±0.5 | 18.29 | 268 | 7.5 | 22.5 | 44~45 | 1000 | 281 | ok |
| yolo26-cls-m_224x224.dxnn | avdec_h264 | 3455 | 3 | 188.8 ±0.8 | 18.30 | 266 | 10.7 | 30.9 | 44~45 | 1000 | 293 | ok |
| yolo26-cls-l_224x224.dxnn | avdec_h264 | 3455 | 3 | 188.3 ±0.4 | 18.34 | 266 | 17.4 | 43.0 | 45 | 1000 | 300 | ok |
| yolo26-cls-x_224x224.dxnn | avdec_h264 | 3455 | 3 | 187.8 ±0.9 | 18.39 | 265 | 31.7 | 61.3 | 46~47 | 1000 | 350 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-cls-n_224x224.dxnn | avdec_h264 | 3455 | 3 | 189.7 ±0.3 | 18.22 | 269 | 4.1 | 13.1 | 43~44 | 1000 | 267 | ok |
| yolo26-cls-s_224x224.dxnn | avdec_h264 | 3455 | 3 | 188.5 ±0.6 | 18.33 | 267 | 7.6 | 22.6 | 44 | 1000 | 278 | ok |
| yolo26-cls-m_224x224.dxnn | avdec_h264 | 3455 | 3 | 188.8 ±0.5 | 18.30 | 267 | 10.8 | 30.7 | 44~45 | 1000 | 295 | ok |
| yolo26-cls-l_224x224.dxnn | avdec_h264 | 3455 | 3 | 188.9 ±0.5 | 18.29 | 266 | 17.4 | 43.0 | 45~46 | 1000 | 301 | ok |
| yolo26-cls-x_224x224.dxnn | avdec_h264 | 3455 | 3 | 188.2 ±0.6 | 18.36 | 266 | 31.7 | 60.2 | 47 | 1000 | 348 | ok |

> Classification has no CPU part, so ORT ON and OFF run the same model; differences between the two tables are measurement noise.

## E2E Pipeline (Multi-Stream)

### Object Detection

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | 2 | 3 | 67.6 ±0.3 | 33.8 | 313 | 17.0 | 40.0 | 42 | 1000 | 554 | ok |
| yolo26-n_640x640.dxnn | 3 | 3 | 65.7 ±0.1 | 21.9 | 313 | 16.7 | 39.8 | 43 | 1000 | 656 | ok |
| yolo26-s_640x640.dxnn | 2 | 3 | 66.3 ±0.8 | 33.1 | 309 | 29.9 | 59.0 | 47 | 1000 | 575 | ok |
| yolo26-s_640x640.dxnn | 3 | 3 | 66.3 ±0.3 | 22.1 | 309 | 30.1 | 60.8 | 47 | 1000 | 680 | ok |
| yolo26-m_640x640.dxnn | 2 | 3 | 65.4 ±0.2 | 32.7 | 301 | 47.0 | 76.2 | 57~59 | 1000 | 605 | ok |
| yolo26-m_640x640.dxnn | 3 | 3 | 65.2 ±0.0 | 21.7 | 302 | 47.9 | 73.9 | 60 | 1000 | 708 | ok |
| yolo26-l_640x640.dxnn | 2 | 3 | 65.6 ±1.0 | 32.8 | 285 | 66.1 | 84.8 | 62~63 | 1000 | 620 | ok |
| yolo26-l_640x640.dxnn | 3 | 3 | 65.0 ±0.2 | 21.7 | 286 | 66.5 | 84.6 | 65 | 1000 | 720 | ok |
| yolo26-x_640x640.dxnn | 1 | 3 | 48.9 ±0.1 | 48.9 | 135 | 93.6 | 100.0 | 61~68 | 1000 | 584 | ok |
| yolo26-x_640x640.dxnn | 2 | 3 | 47.8 ±1.1 | 23.9 | 137 | 95.8 | 100.0 | 76~78 | 800~1000 | 713 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | 2 | 3 | 79.9 ±0.3 | 39.9 | 305 | 19.0 | 58.0 | 43 | 1000 | 580 | ok |
| yolo26-n_640x640.dxnn | 3 | 3 | 79.7 ±0.5 | 26.6 | 306 | 19.0 | 57.9 | 43 | 1000 | 680 | ok |
| yolo26-s_640x640.dxnn | 2 | 3 | 79.7 ±0.3 | 39.8 | 302 | 34.5 | 73.2 | 48~49 | 1000 | 606 | ok |
| yolo26-s_640x640.dxnn | 3 | 3 | 79.4 ±0.6 | 26.5 | 307 | 34.6 | 71.9 | 48~49 | 1000 | 702 | ok |
| yolo26-m_640x640.dxnn | 2 | 3 | 78.6 ±0.5 | 39.3 | 303 | 55.5 | 87.6 | 59~61 | 1000 | 633 | ok |
| yolo26-m_640x640.dxnn | 3 | 3 | 78.1 ±0.0 | 26.1 | 305 | 55.9 | 83.5 | 62 | 1000 | 737 | ok |
| yolo26-l_640x640.dxnn | 2 | 3 | 79.0 ±0.1 | 39.5 | 307 | 80.8 | 93.8 | 64~67 | 1000 | 646 | ok |
| yolo26-l_640x640.dxnn | 3 | 3 | 78.9 ±0.4 | 26.3 | 307 | 81.3 | 97.7 | 69~70 | 1000 | 746 | ok |
| yolo26-x_640x640.dxnn | 1 | 3 | 49.0 ±0.1 | 49.0 | 149 | 93.6 | 100.0 | 61~69 | 1000 | 583 | ok |
| yolo26-x_640x640.dxnn | 2 | 3 | 47.0 ±1.4 | 23.5 | 148 | 96.3 | 100.0 | 78~79 | 800~1000 | 721 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n_640x640.dxnn | 2 | 33.8 | 2 | 39.9 |
| yolo26-s_640x640.dxnn | 2 | 33.1 | 2 | 39.8 |
| yolo26-m_640x640.dxnn | 2 | 32.7 | 2 | 39.3 |
| yolo26-l_640x640.dxnn | 2 | 32.8 | 2 | 39.5 |
| yolo26-x_640x640.dxnn | 1 | 48.9 | 1 | 49.0 |

### Pose Estimation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 2 | 3 | 80.0 ±0.3 | 40.0 | 322 | 22.0 | 46.9 | 45 | 1000 | 539 | ok |
| yolo26-n-pose_640x640.dxnn | 3 | 3 | 80.7 ±1.3 | 26.9 | 321 | 22.5 | 49.0 | 45 | 1000 | 643 | ok |
| yolo26-s-pose_640x640.dxnn | 2 | 3 | 81.2 ±1.6 | 40.6 | 317 | 39.1 | 69.2 | 49~50 | 1000 | 562 | ok |
| yolo26-s-pose_640x640.dxnn | 3 | 3 | 80.5 ±1.2 | 26.8 | 317 | 39.3 | 68.8 | 50 | 1000 | 663 | ok |
| yolo26-m-pose_640x640.dxnn | 2 | 3 | 80.2 ±0.7 | 40.1 | 307 | 60.4 | 81.5 | 60~63 | 1000 | 590 | ok |
| yolo26-m-pose_640x640.dxnn | 3 | 3 | 80.2 ±0.5 | 26.7 | 307 | 61.6 | 83.5 | 64~65 | 1000 | 696 | ok |
| yolo26-l-pose_640x640.dxnn | 2 | 3 | 80.9 ±1.1 | 40.5 | 278 | 86.0 | 96.4 | 66~69 | 1000 | 605 | ok |
| yolo26-l-pose_640x640.dxnn | 3 | 3 | 80.4 ±0.4 | 26.8 | 278 | 86.4 | 96.3 | 71~72 | 1000 | 707 | ok |
| yolo26-x-pose_640x640.dxnn | 1 | 3 | 47.7 ±0.1 | 47.7 | 105 | 94.5 | 100.0 | 61~70 | 1000 | 568 | ok |
| yolo26-x-pose_640x640.dxnn | 2 | 3 | 46.0 ±1.2 | 23.0 | 104 | 96.1 | 100.0 | 78 | 800~1000 | 700 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 3 | 3 | 113.3 ±1.1 | 37.8 | 329 | 32.6 | 55.0 | 47 | 1000 | 633 | ok |
| yolo26-n-pose_640x640.dxnn | 4 | 3 | 112.3 ±0.5 | 28.1 | 331 | 32.5 | 54.4 | 47 | 1000 | 735 | ok |
| yolo26-s-pose_640x640.dxnn | 3 | 3 | 112.5 ±1.4 | 37.5 | 321 | 56.4 | 77.3 | 52~53 | 1000 | 656 | ok |
| yolo26-s-pose_640x640.dxnn | 4 | 3 | 112.2 ±0.8 | 28.0 | 323 | 56.8 | 78.7 | 54 | 1000 | 760 | ok |
| yolo26-m-pose_640x640.dxnn | 3 | 3 | 108.8 ±0.7 | 36.3 | 293 | 85.6 | 98.0 | 66~70 | 1000 | 683 | ok |
| yolo26-m-pose_640x640.dxnn | 4 | 3 | 109.1 ±1.3 | 27.3 | 294 | 86.7 | 96.7 | 73~74 | 1000 | 788 | ok |
| yolo26-l-pose_640x640.dxnn | 2 | 3 | 89.2 ±0.3 | 44.6 | 188 | 94.9 | 100.0 | 67~71 | 1000 | 592 | ok |
| yolo26-l-pose_640x640.dxnn | 3 | 3 | 89.2 ±0.2 | 29.7 | 190 | 96.0 | 100.0 | 74~76 | 1000 | 697 | ok |
| yolo26-x-pose_640x640.dxnn | 1 | 3 | 47.7 ±0.1 | 47.7 | 86 | 95.3 | 100.0 | 61~70 | 1000 | 556 | ok |
| yolo26-x-pose_640x640.dxnn | 2 | 3 | 45.2 ±1.4 | 22.6 | 90 | 95.8 | 100.0 | 78~79 | 800~1000 | 686 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-pose_640x640.dxnn | 2 | 40.0 | 3 | 37.8 |
| yolo26-s-pose_640x640.dxnn | 2 | 40.6 | 3 | 37.5 |
| yolo26-m-pose_640x640.dxnn | 2 | 40.1 | 3 | 36.3 |
| yolo26-l-pose_640x640.dxnn | 2 | 40.5 | 2 | 44.6 |
| yolo26-x-pose_640x640.dxnn | 1 | 47.7 | 1 | 47.7 |

### Segmentation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 1 | 3 | 45.4 ±0.0 | 45.4 | 312 | 14.4 | 34.3 | 43 | 1000 | 540 | ok |
| yolo26-n-seg_640x640.dxnn | 2 | 3 | 45.2 ±0.3 | 22.6 | 311 | 14.6 | 34.9 | 43 | 1000 | 682 | ok |
| yolo26-s-seg_640x640.dxnn | 1 | 3 | 45.4 ±0.2 | 45.4 | 303 | 26.1 | 58.9 | 47 | 1000 | 564 | ok |
| yolo26-s-seg_640x640.dxnn | 2 | 3 | 45.1 ±0.1 | 22.6 | 307 | 26.7 | 57.4 | 48 | 1000 | 708 | ok |
| yolo26-m-seg_640x640.dxnn | 1 | 3 | 44.7 ±0.1 | 44.7 | 285 | 49.2 | 76.9 | 54~58 | 1000 | 605 | ok |
| yolo26-m-seg_640x640.dxnn | 2 | 3 | 43.3 ±0.4 | 21.7 | 291 | 48.1 | 75.4 | 62~63 | 1000 | 744 | ok |
| yolo26-l-seg_640x640.dxnn | 1 | 3 | 44.5 ±0.4 | 44.5 | 268 | 60.9 | 88.1 | 57~60 | 1000 | 618 | ok |
| yolo26-l-seg_640x640.dxnn | 2 | 3 | 43.3 ±0.1 | 21.6 | 275 | 60.5 | 85.1 | 66~68 | 1000 | 755 | ok |
| yolo26-x-seg_640x640.dxnn | 1 | 3 | 34.0 ±0.5 | 34.0 | 143 | 94.4 | 100.0 | 68~76 | 800~1000 | 724 | ok |
| yolo26-x-seg_640x640.dxnn | 2 | 3 | 30.8 ±0.0 | 15.4 | 133 | 95.8 | 100.0 | 80~81 | 800~1000 | 862 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 1 | 3 | 55.5 ±0.5 | 55.5 | 336 | 16.7 | 50.0 | 45 | 1000 | 583 | ok |
| yolo26-n-seg_640x640.dxnn | 2 | 3 | 55.0 ±0.3 | 27.5 | 338 | 16.8 | 49.9 | 44 | 1000 | 727 | ok |
| yolo26-s-seg_640x640.dxnn | 1 | 3 | 55.1 ±0.0 | 55.1 | 334 | 31.5 | 68.6 | 47~48 | 1000 | 607 | ok |
| yolo26-s-seg_640x640.dxnn | 2 | 3 | 55.3 ±0.5 | 27.6 | 332 | 31.6 | 68.5 | 48~50 | 1000 | 759 | ok |
| yolo26-m-seg_640x640.dxnn | 1 | 3 | 54.5 ±0.0 | 54.5 | 318 | 60.4 | 81.4 | 56~61 | 1000 | 650 | ok |
| yolo26-m-seg_640x640.dxnn | 2 | 3 | 53.8 ±0.3 | 26.9 | 324 | 60.7 | 83.3 | 66~68 | 1000 | 788 | ok |
| yolo26-l-seg_640x640.dxnn | 1 | 3 | 53.4 ±1.1 | 53.4 | 294 | 75.0 | 94.9 | 58~63 | 1000 | 650 | ok |
| yolo26-l-seg_640x640.dxnn | 2 | 3 | 52.5 ±0.7 | 26.3 | 303 | 75.2 | 91.5 | 69~70 | 1000 | 796 | ok |
| yolo26-x-seg_640x640.dxnn | 1 | 3 | 34.1 ±0.5 | 34.1 | 147 | 94.6 | 100.0 | 73~80 | 1000 | 733 | ok |
| yolo26-x-seg_640x640.dxnn | 2 | 3 | 29.8 ±0.1 | 14.9 | 126 | 96.4 | 100.0 | 81 | 800~1000 | 874 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-seg_640x640.dxnn | 1 | 45.4 | 1 | 55.5 |
| yolo26-s-seg_640x640.dxnn | 1 | 45.4 | 1 | 55.1 |
| yolo26-m-seg_640x640.dxnn | 1 | 44.7 | 1 | 54.5 |
| yolo26-l-seg_640x640.dxnn | 1 | 44.5 | 1 | 53.4 |
| yolo26-x-seg_640x640.dxnn | 1 | 34.0 | 1 | 34.1 |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 2 | 3 | 68.2 ±0.8 | 34.1 | 319 | 53.6 | 77.4 | 51~52 | 1000 | 588 | ok |
| yolo26-n-obb_1024x1024.dxnn | 3 | 3 | 67.9 ±0.3 | 22.6 | 320 | 53.8 | 77.5 | 52~53 | 1000 | 691 | ok |
| yolo26-s-obb_1024x1024.dxnn | 2 | 3 | 62.3 ±0.3 | 31.1 | 230 | 94.2 | 100.0 | 59~62 | 1000 | 614 | ok |
| yolo26-s-obb_1024x1024.dxnn | 3 | 3 | 62.3 ±0.3 | 20.8 | 243 | 95.2 | 100.0 | 64~65 | 1000 | 717 | ok |
| yolo26-m-obb_1024x1024.dxnn | 1 | 3 | 41.8 ±0.5 | 41.8 | 127 | 92.4 | 100.0 | 59~65 | 1000 | 513 | ok |
| yolo26-m-obb_1024x1024.dxnn | 2 | 3 | 41.8 ±0.5 | 20.9 | 133 | 96.3 | 100.0 | 73~75 | 1000 | 641 | ok |
| yolo26-l-obb_1024x1024.dxnn | 1 | 3 | 31.1 ±0.1 | 31.1 | 94 | 93.7 | 100.0 | 61~68 | 1000 | 530 | ok |
| yolo26-l-obb_1024x1024.dxnn | 2 | 3 | 31.1 ±0.1 | 15.5 | 97 | 95.4 | 100.0 | 74~76 | 1000 | 657 | ok |
| yolo26-x-obb_1024x1024.dxnn | 1 | 3 | 16.9 ±0.3 | 16.9 | 55 | 94.2 | 100.0 | 70~78 | 1000 | 629 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 2 | 3 | 81.2 ±0.5 | 40.6 | 331 | 67.4 | 86.0 | 52~53 | 1000 | 607 | ok |
| yolo26-n-obb_1024x1024.dxnn | 3 | 3 | 81.6 ±0.9 | 27.2 | 330 | 68.2 | 85.7 | 54 | 1000 | 706 | ok |
| yolo26-s-obb_1024x1024.dxnn | 2 | 3 | 63.2 ±0.0 | 31.6 | 209 | 94.9 | 100.0 | 60~61 | 1000 | 605 | ok |
| yolo26-s-obb_1024x1024.dxnn | 3 | 3 | 63.1 ±0.0 | 21.0 | 209 | 96.0 | 100.0 | 65 | 1000 | 707 | ok |
| yolo26-m-obb_1024x1024.dxnn | 1 | 3 | 42.2 ±0.5 | 42.2 | 127 | 93.6 | 100.0 | 59~66 | 1000 | 504 | ok |
| yolo26-m-obb_1024x1024.dxnn | 2 | 3 | 41.9 ±0.6 | 20.9 | 130 | 96.2 | 100.0 | 73~76 | 1000 | 643 | ok |
| yolo26-l-obb_1024x1024.dxnn | 1 | 3 | 31.1 ±0.1 | 31.1 | 94 | 94.1 | 100.0 | 61~68 | 1000 | 522 | ok |
| yolo26-l-obb_1024x1024.dxnn | 2 | 3 | 31.0 ±0.1 | 15.5 | 97 | 95.5 | 100.0 | 75~76 | 1000 | 654 | ok |
| yolo26-x-obb_1024x1024.dxnn | 1 | 3 | 16.9 ±0.3 | 16.9 | 57 | 94.2 | 100.0 | 70~78 | 1000 | 622 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-obb_1024x1024.dxnn | 2 | 34.1 | 2 | 40.6 |
| yolo26-s-obb_1024x1024.dxnn | 2 | 31.1 | 2 | 31.6 |
| yolo26-m-obb_1024x1024.dxnn | 1 | 41.8 | 1 | 42.2 |
| yolo26-l-obb_1024x1024.dxnn | 1 | 31.1 | 1 | 31.1 |

---
*Report generated by dx-benchmark tool*
