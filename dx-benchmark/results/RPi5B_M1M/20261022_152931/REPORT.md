# YOLO26 Benchmark Report

**Generated:** 2026-10-24 04:22:09 (UTC+09:00, local)

## Test Timing

| # | Type | Start | End | Duration |
|---|------|-------|-----|----------|
| 1 | run | 2026-10-22 15:29:31 | 2026-10-24 04:22:08 | 36h 52m 37s |

## Executive Summary

### Object Detection

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n_640x640.dxnn | ON | 25.39 | 102.3 | 66.2 | 2 |
| yolo26-n_640x640.dxnn | OFF | 22.67 | 179.7 | 79.5 | 2 |
| yolo26-s_640x640.dxnn | ON | 32.38 | 102.2 | 66.3 | 2 |
| yolo26-s_640x640.dxnn | OFF | 30.88 | 154.9 | 80.2 | 2 |
| yolo26-m_640x640.dxnn | ON | 42.37 | 85.3 | 65.5 | 1 |
| yolo26-m_640x640.dxnn | OFF | 38.73 | 85.8 | 75.4 | 1 |
| yolo26-l_640x640.dxnn | ON | 48.88 | 67.2 | 52.1 | 1 |
| yolo26-l_640x640.dxnn | OFF | 45.65 | 67.4 | 53.1 | 1 |
| yolo26-x_640x640.dxnn | ON | 77.62 | 37.1 | 20.6 | — |
| yolo26-x_640x640.dxnn | OFF | 75.22 | 37.1 | 21.8 | — |

### Pose Estimation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-pose_640x640.dxnn | ON | 22.59 | 146.2 | 80.1 | 2 |
| yolo26-n-pose_640x640.dxnn | OFF | 20.21 | 239.5 | 112.0 | 3 |
| yolo26-s-pose_640x640.dxnn | ON | 28.52 | 141.1 | 80.5 | 2 |
| yolo26-s-pose_640x640.dxnn | OFF | 26.38 | 145.5 | 111.9 | 3 |
| yolo26-m-pose_640x640.dxnn | ON | 35.47 | 90.8 | 68.0 | 1 |
| yolo26-m-pose_640x640.dxnn | OFF | 34.85 | 90.5 | 70.7 | 1 |
| yolo26-l-pose_640x640.dxnn | ON | 45.32 | 66.9 | 48.2 | 1 |
| yolo26-l-pose_640x640.dxnn | OFF | 43.62 | 66.9 | 53.0 | 1 |
| yolo26-x-pose_640x640.dxnn | ON | 74.77 | 36.2 | 20.3 | — |
| yolo26-x-pose_640x640.dxnn | OFF | 73.05 | 36.2 | 20.1 | — |

### Segmentation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-seg_640x640.dxnn | ON | 41.21 | 65.9 | 44.1 | 1 |
| yolo26-n-seg_640x640.dxnn | OFF | 41.18 | 95.7 | 54.9 | 1 |
| yolo26-s-seg_640x640.dxnn | ON | 53.46 | 66.0 | 44.1 | 1 |
| yolo26-s-seg_640x640.dxnn | OFF | 48.71 | 95.7 | 54.9 | 1 |
| yolo26-m-seg_640x640.dxnn | ON | 69.46 | 57.2 | 34.1 | 1 |
| yolo26-m-seg_640x640.dxnn | OFF | 64.98 | 57.1 | 33.2 | 1 |
| yolo26-l-seg_640x640.dxnn | ON | 76.89 | 48.6 | 28.2 | — |
| yolo26-l-seg_640x640.dxnn | OFF | 70.14 | 48.6 | 27.8 | — |
| yolo26-x-seg_640x640.dxnn | ON | 116.61 | 27.2 | 13.6 | — |
| yolo26-x-seg_640x640.dxnn | OFF | 116.37 | 27.3 | 13.5 | — |

### Oriented BBox (OBB)

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-obb_1024x1024.dxnn | ON | 40.97 | 75.2 | 68.6 | 2 |
| yolo26-n-obb_1024x1024.dxnn | OFF | 38.23 | 75.5 | 74.0 | 2 |
| yolo26-s-obb_1024x1024.dxnn | ON | 57.67 | 45.5 | 45.1 | 1 |
| yolo26-s-obb_1024x1024.dxnn | OFF | 56.03 | 45.5 | 45.9 | 1 |
| yolo26-m-obb_1024x1024.dxnn | ON | 79.30 | 29.2 | 22.1 | — |
| yolo26-m-obb_1024x1024.dxnn | OFF | 77.11 | 29.3 | 19.3 | — |
| yolo26-l-obb_1024x1024.dxnn | ON | 101.22 | 22.3 | 14.4 | — |
| yolo26-l-obb_1024x1024.dxnn | OFF | 98.96 | 22.3 | 14.5 | — |
| yolo26-x-obb_1024x1024.dxnn | ON | 179.54 | 12.7 | 7.3 | — |
| yolo26-x-obb_1024x1024.dxnn | OFF | 177.70 | 12.7 | 6.6 | — |

### Classification

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-cls-n_224x224.dxnn | ON | 1.59 | 2877.2 | 192.2 | — |
| yolo26-cls-n_224x224.dxnn | OFF | 1.57 | 2860.7 | 192.8 | — |
| yolo26-cls-s_224x224.dxnn | ON | 2.34 | 1516.0 | 192.4 | — |
| yolo26-cls-s_224x224.dxnn | OFF | 2.32 | 1515.4 | 191.9 | — |
| yolo26-cls-m_224x224.dxnn | ON | 3.06 | 1057.7 | 192.3 | — |
| yolo26-cls-m_224x224.dxnn | OFF | 3.03 | 1057.5 | 192.3 | — |
| yolo26-cls-l_224x224.dxnn | ON | 4.36 | 712.0 | 192.6 | — |
| yolo26-cls-l_224x224.dxnn | OFF | 4.36 | 712.1 | 192.1 | — |
| yolo26-cls-x_224x224.dxnn | ON | 7.28 | 384.8 | 191.9 | — |
| yolo26-cls-x_224x224.dxnn | OFF | 7.25 | 384.9 | 192.5 | — |

## Environment

| Item | Value |
|------|-------|
| Product | RPi5B |
| Hostname | deepx |
| OS | Debian GNU/Linux 13 (trixie) |
| Kernel | 6.18.34+rpt-rpi-2712 |
| CPU | Cortex-A76 |
| CPU Threads | 4 |
| CPU Governor | ondemand |
| RAM | 7.9 GiB |
| NPU SKU | M1M |
| NPU Chip / Board | M1M · M.2, Rev 0.0 |
| NPU Devices | 1 (M1M) |
| DX-AllSuite | v2.5.0 |
| DX-Stream | 3.2.0 |
| Benchmark Tool | 0.2.0 |
| Tool commit | 4e94aa9 |
| NPU RT | v3.5.0 |
| NPU RT (commit) | v3.5.0 (build: 5.502926e) |
| NPU Driver (RT) | v2.7.0 |
| NPU Driver (PCIe) | v2.7.0 |
| NPU Firmware | v2.7.6 (build: 4.90f4a6f) |
| NPU Memory | LPDDR4 4200 Mbps, 1.92GiB |
| NPU Board | M.2, Rev 0.0 |
| NPU PCIe | Gen3 X1 [01:00:00] |
| Host Health | throttled=0x0, EXT5V 5.21 V |

### Tools

| Tool | Available | Version |
|------|-----------|---------|
| run_model | Yes | DXRT v3.5.0 run_model |
| dxrt-cli | Yes | DXRT v3.5.0 (build: 5.502926e) |
| gst-launch-1.0 | Yes | gst-launch-1.0 version 1.26.2 |
| gst-inspect-1.0 | Yes | gst-inspect-1.0 version 1.26.2 |
| time | Yes | unknown |
| ffprobe | Yes | ffprobe version 7.1.4-0+deb13u1+rpt1 Copyright (c) 2007-2026... |
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
| yolo26-n_640x640.dxnn | 102.3 ±0.0 | 5 | 191 | 29.6 | 72.3 | 56~58 | 1000 | ok |
| yolo26-s_640x640.dxnn | 102.2 ±0.4 | 6 | 194 | 56.2 | 85.2 | 61~62 | 1000 | ok |
| yolo26-m_640x640.dxnn | 85.3 ±0.2 | 5 | 134 | 90.3 | 100.0 | 68~69 | 1000 | ok |
| yolo26-l_640x640.dxnn | 67.2 ±0.0 | 5 | 85 | 94.9 | 100.0 | 68~69 | 1000 | ok |
| yolo26-x_640x640.dxnn | 37.1 ±0.0 | 4 | 56 | 93.4 | 100.0 | 70 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n_640x640.dxnn | 5 | [3]:87.3 · [4]:99.4 · **[5]:102.0 ★** · [6]:101.3 · [7]:101.3 · [8]:101.9 |
| yolo26-s_640x640.dxnn | 6 | [3]:74.5 · [4]:91.0 · [5]:100.9 · **[6]:102.1 ★** · [7]:102.5 · [8]:102.2 · [9]:101.6 |
| yolo26-m_640x640.dxnn | 5 | [3]:60.4 · [4]:74.8 · **[5]:85.6 ★** · [6]:85.6 · [7]:85.7 · [8]:85.7 |
| yolo26-l_640x640.dxnn | 5 | [3]:48.8 · [4]:62.2 · **[5]:67.0 ★** · [6]:66.9 · [7]:66.9 · [8]:67.0 |
| yolo26-x_640x640.dxnn | 4 | [3]:31.3 · **[4]:36.9 ★** · [5]:37.0 · [6]:37.0 · [7]:36.9 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n_640x640.dxnn | 179.7 ±0.1 | 6 | 127 | 58.0 | 91.3 | 60~61 | 1000 | ok |
| yolo26-s_640x640.dxnn | 154.9 ±0.1 | 6 | 107 | 95.0 | 100.0 | 64~65 | 1000 | ok |
| yolo26-m_640x640.dxnn | 85.8 ±0.1 | 5 | 51 | 97.7 | 100.0 | 67~69 | 1000 | ok |
| yolo26-l_640x640.dxnn | 67.4 ±0.0 | 5 | 42 | 95.6 | 100.0 | 68~69 | 1000 | ok |
| yolo26-x_640x640.dxnn | 37.1 ±0.0 | 4 | 29 | 92.6 | 100.0 | 70 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n_640x640.dxnn | 6 | [3]:112.3 · [4]:134.4 · [5]:165.6 · **[6]:178.8 ★** · [7]:179.2 · [8]:179.3 · [9]:179.3 |
| yolo26-s_640x640.dxnn | 6 | [3]:96.5 · [4]:120.0 · [5]:145.0 · **[6]:154.7 ★** · [7]:154.9 · [8]:154.9 · [9]:154.8 |
| yolo26-m_640x640.dxnn | 5 | [3]:66.3 · [4]:84.0 · **[5]:85.5 ★** · [6]:85.5 · [7]:85.5 · [8]:85.5 |
| yolo26-l_640x640.dxnn | 5 | [3]:54.4 · [4]:64.8 · **[5]:67.2 ★** · [6]:67.2 · [7]:67.2 · [8]:67.2 |
| yolo26-x_640x640.dxnn | 4 | [3]:33.4 · **[4]:36.9 ★** · [5]:37.0 · [6]:37.0 · [7]:37.0 |


#### Pose Estimation

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 146.2 ±1.0 | 7 | 188 | 48.8 | 77.0 | 60~61 | 1000 | ok |
| yolo26-s-pose_640x640.dxnn | 141.1 ±0.1 | 6 | 170 | 94.4 | 100.0 | 65 | 1000 | ok |
| yolo26-m-pose_640x640.dxnn | 90.8 ±0.0 | 5 | 86 | 97.2 | 100.0 | 69~70 | 1000 | ok |
| yolo26-l-pose_640x640.dxnn | 66.9 ±0.0 | 5 | 57 | 93.9 | 100.0 | 68~69 | 1000 | ok |
| yolo26-x-pose_640x640.dxnn | 36.2 ±0.0 | 4 | 35 | 93.5 | 100.0 | 70 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-pose_640x640.dxnn | 7 | [3]:113.5 · [4]:137.6 · [5]:146.3 · [6]:146.5 · **[7]:148.5 ★** · [8]:148.1 · [9]:147.9 · [10]:147.9 |
| yolo26-s-pose_640x640.dxnn | 6 | [3]:91.1 · [4]:112.3 · [5]:132.4 · **[6]:144.2 ★** · [7]:144.7 · [8]:144.5 · [9]:144.5 |
| yolo26-m-pose_640x640.dxnn | 5 | [3]:64.8 · [4]:82.0 · **[5]:90.4 ★** · [6]:90.5 · [7]:90.5 · [8]:90.5 |
| yolo26-l-pose_640x640.dxnn | 5 | [3]:53.0 · [4]:64.5 · **[5]:66.8 ★** · [6]:66.7 · [7]:66.8 · [8]:66.7 |
| yolo26-x-pose_640x640.dxnn | 4 | [3]:32.4 · **[4]:36.0 ★** · [5]:36.0 · [6]:36.0 · [7]:36.0 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 239.5 ±0.7 | 7 | 103 | 96.2 | 100.0 | 64~65 | 1000 | ok |
| yolo26-s-pose_640x640.dxnn | 145.5 ±0.1 | 5 | 59 | 95.1 | 100.0 | 65 | 1000 | ok |
| yolo26-m-pose_640x640.dxnn | 90.5 ±0.0 | 5 | 45 | 93.9 | 100.0 | 69~70 | 1000 | ok |
| yolo26-l-pose_640x640.dxnn | 66.9 ±0.0 | 4 | 32 | 93.1 | 100.0 | 69 | 1000 | ok |
| yolo26-x-pose_640x640.dxnn | 36.2 ±0.0 | 4 | 18 | 94.5 | 100.0 | 70~71 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-pose_640x640.dxnn | 7 | [3]:120.9 · [4]:168.8 · [5]:199.5 · [6]:235.0 · **[7]:238.5 ★** · [8]:238.7 · [9]:238.7 · [10]:238.8 |
| yolo26-s-pose_640x640.dxnn | 5 | [3]:93.8 · [4]:126.7 · **[5]:145.1 ★** · [6]:145.2 · [7]:145.2 · [8]:145.3 |
| yolo26-m-pose_640x640.dxnn | 5 | [3]:71.8 · [4]:86.4 · **[5]:90.3 ★** · [6]:90.3 · [7]:90.3 · [8]:90.2 |
| yolo26-l-pose_640x640.dxnn | 4 | [3]:56.0 · **[4]:66.8 ★** · [5]:66.8 · [6]:66.8 · [7]:66.8 |
| yolo26-x-pose_640x640.dxnn | 4 | [3]:33.2 · **[4]:36.0 ★** · [5]:36.0 · [6]:36.0 · [7]:36.0 |


#### Segmentation

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 65.9 ±0.2 | 6 | 245 | 23.4 | 72.4 | 58 | 1000 | ok |
| yolo26-s-seg_640x640.dxnn | 66.0 ±0.1 | 6 | 230 | 47.8 | 76.1 | 62 | 1000 | ok |
| yolo26-m-seg_640x640.dxnn | 57.2 ±0.1 | 6 | 163 | 94.5 | 100.0 | 71~72 | 1000 | ok |
| yolo26-l-seg_640x640.dxnn | 48.6 ±0.0 | 5 | 96 | 94.9 | 100.0 | 71 | 1000 | ok |
| yolo26-x-seg_640x640.dxnn | 27.2 ±0.0 | 5 | 61 | 92.7 | 100.0 | 73 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-seg_640x640.dxnn | 6 | [3]:54.5 · [4]:62.3 · [5]:65.0 · **[6]:65.5 ★** · [7]:65.7 · [8]:64.9 · [9]:65.3 · [10]:65.3 |
| yolo26-s-seg_640x640.dxnn | 6 | [3]:48.1 · [4]:58.4 · [5]:64.0 · **[6]:65.1 ★** · [7]:65.3 · [8]:65.2 · [9]:65.6 |
| yolo26-m-seg_640x640.dxnn | 6 | [3]:38.1 · [4]:47.2 · [5]:53.7 · **[6]:56.6 ★** · [7]:56.7 · [8]:56.7 · [9]:56.9 |
| yolo26-l-seg_640x640.dxnn | 5 | [3]:33.9 · [4]:42.7 · **[5]:48.2 ★** · [6]:48.3 · [7]:48.3 · [8]:48.3 |
| yolo26-x-seg_640x640.dxnn | 5 | [3]:21.0 · [4]:25.9 · **[5]:27.0 ★** · [6]:27.0 · [7]:27.0 · [8]:27.0 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 95.7 ±0.1 | 5 | 152 | 40.4 | 66.6 | 60 | 1000 | ok |
| yolo26-s-seg_640x640.dxnn | 95.7 ±0.0 | 7 | 141 | 87.4 | 93.6 | 65~66 | 1000 | ok |
| yolo26-m-seg_640x640.dxnn | 57.1 ±0.0 | 5 | 74 | 93.2 | 100.0 | 71~72 | 1000 | ok |
| yolo26-l-seg_640x640.dxnn | 48.6 ±0.0 | 5 | 58 | 93.8 | 100.0 | 71 | 1000 | ok |
| yolo26-x-seg_640x640.dxnn | 27.3 ±0.0 | 4 | 40 | 92.9 | 100.0 | 73 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-seg_640x640.dxnn | 5 | [3]:78.2 · [4]:89.4 · **[5]:95.5 ★** · [6]:95.5 · [7]:95.5 · [8]:95.4 |
| yolo26-s-seg_640x640.dxnn | 7 | [3]:60.1 · [4]:75.1 · [5]:84.2 · [6]:93.9 · **[7]:95.3 ★** · [8]:95.4 · [9]:95.2 · [10]:95.2 |
| yolo26-m-seg_640x640.dxnn | 5 | [3]:44.6 · [4]:52.6 · **[5]:56.9 ★** · [6]:56.9 · [7]:56.8 · [8]:57.0 |
| yolo26-l-seg_640x640.dxnn | 5 | [3]:36.7 · [4]:44.8 · **[5]:48.2 ★** · [6]:48.3 · [7]:48.3 · [8]:48.3 |
| yolo26-x-seg_640x640.dxnn | 4 | [3]:22.8 · **[4]:27.0 ★** · [5]:27.0 · [6]:27.0 · [7]:27.0 |


#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 75.2 ±0.0 | 5 | 80 | 93.2 | 100.0 | 64 | 1000 | ok |
| yolo26-s-obb_1024x1024.dxnn | 45.5 ±0.1 | 5 | 47 | 93.9 | 100.0 | 65~66 | 1000 | ok |
| yolo26-m-obb_1024x1024.dxnn | 29.2 ±0.0 | 4 | 31 | 92.9 | 100.0 | 68~69 | 1000 | ok |
| yolo26-l-obb_1024x1024.dxnn | 22.3 ±0.0 | 4 | 24 | 91.5 | 100.0 | 68 | 1000 | ok |
| yolo26-x-obb_1024x1024.dxnn | 12.7 ±0.0 | 4 | 14 | 90.4 | 100.0 | 70 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-obb_1024x1024.dxnn | 5 | [3]:56.5 · [4]:69.0 · **[5]:74.7 ★** · [6]:74.7 · [7]:74.6 · [8]:74.6 |
| yolo26-s-obb_1024x1024.dxnn | 5 | [3]:38.2 · [4]:44.3 · **[5]:45.3 ★** · [6]:45.3 · [7]:45.3 · [8]:45.3 |
| yolo26-m-obb_1024x1024.dxnn | 4 | [3]:26.8 · **[4]:29.1 ★** · [5]:29.1 · [6]:29.1 · [7]:29.1 |
| yolo26-l-obb_1024x1024.dxnn | 4 | [3]:20.4 · **[4]:22.2 ★** · [5]:22.2 · [6]:22.2 · [7]:22.2 |
| yolo26-x-obb_1024x1024.dxnn | 4 | [3]:11.6 · **[4]:12.6 ★** · [5]:12.6 · [6]:12.6 · [7]:12.6 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 75.5 ±0.0 | 5 | 41 | 94.7 | 100.0 | 64 | 1000 | ok |
| yolo26-s-obb_1024x1024.dxnn | 45.5 ±0.0 | 4 | 27 | 96.5 | 100.0 | 65 | 1000 | ok |
| yolo26-m-obb_1024x1024.dxnn | 29.3 ±0.0 | 4 | 18 | 93.7 | 100.0 | 68~69 | 1000 | ok |
| yolo26-l-obb_1024x1024.dxnn | 22.3 ±0.0 | 4 | 13 | 91.9 | 100.0 | 68 | 1000 | ok |
| yolo26-x-obb_1024x1024.dxnn | 12.7 ±0.0 | 4 | 8 | 90.3 | 100.0 | 70 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-obb_1024x1024.dxnn | 5 | [3]:52.6 · [4]:72.3 · **[5]:74.9 ★** · [6]:74.9 · [7]:74.9 · [8]:75.0 |
| yolo26-s-obb_1024x1024.dxnn | 4 | [3]:36.7 · **[4]:45.2 ★** · [5]:45.3 · [6]:45.3 · [7]:45.3 |
| yolo26-m-obb_1024x1024.dxnn | 4 | [3]:26.3 · **[4]:29.1 ★** · [5]:29.2 · [6]:29.1 · [7]:29.2 |
| yolo26-l-obb_1024x1024.dxnn | 4 | [3]:19.8 · **[4]:22.2 ★** · [5]:22.2 · [6]:22.2 · [7]:22.2 |
| yolo26-x-obb_1024x1024.dxnn | 4 | [3]:11.4 · **[4]:12.6 ★** · [5]:12.6 · [6]:12.6 · [7]:12.6 |


#### Classification

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-cls-n_224x224.dxnn | 2877.2 ±12.4 | 6 | 56 | 89.9 | 94.9 | 61 | 1000 | ok |
| yolo26-cls-s_224x224.dxnn | 1516.0 ±0.9 | 5 | 33 | 91.2 | 94.8 | 62 | 1000 | ok |
| yolo26-cls-m_224x224.dxnn | 1057.7 ±1.0 | 5 | 23 | 92.5 | 97.0 | 66 | 1000 | ok |
| yolo26-cls-l_224x224.dxnn | 712.0 ±0.3 | 4 | 16 | 94.8 | 98.7 | 64~65 | 1000 | ok |
| yolo26-cls-x_224x224.dxnn | 384.8 ±0.2 | 4 | 9 | 94.6 | 99.9 | 67 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-cls-n_224x224.dxnn | 6 | [3]:1786.8 · [4]:2397.0 · [5]:2707.2 · **[6]:2855.9 ★** · [7]:2860.6 · [8]:2865.2 · [9]:2864.8 |
| yolo26-cls-s_224x224.dxnn | 5 | [3]:1194.9 · [4]:1481.4 · **[5]:1515.7 ★** · [6]:1524.3 · [7]:1522.4 · [8]:1524.9 |
| yolo26-cls-m_224x224.dxnn | 5 | [3]:877.9 · [4]:1037.5 · **[5]:1057.2 ★** · [6]:1057.5 · [7]:1057.0 · [8]:1058.0 |
| yolo26-cls-l_224x224.dxnn | 4 | [3]:607.3 · **[4]:711.7 ★** · [5]:712.1 · [6]:712.7 · [7]:712.6 |
| yolo26-cls-x_224x224.dxnn | 4 | [3]:335.1 · **[4]:384.3 ★** · [5]:384.4 · [6]:384.5 · [7]:384.6 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-cls-n_224x224.dxnn | 2860.7 ±6.9 | 6 | 57 | 90.7 | 94.8 | 61~62 | 1000 | ok |
| yolo26-cls-s_224x224.dxnn | 1515.4 ±1.2 | 5 | 33 | 89.9 | 94.7 | 62 | 1000 | ok |
| yolo26-cls-m_224x224.dxnn | 1057.5 ±1.0 | 5 | 23 | 93.2 | 96.8 | 66~67 | 1000 | ok |
| yolo26-cls-l_224x224.dxnn | 712.1 ±0.1 | 4 | 16 | 94.4 | 98.7 | 64~65 | 1000 | ok |
| yolo26-cls-x_224x224.dxnn | 384.9 ±0.2 | 4 | 9 | 96.2 | 99.9 | 66~67 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = recommended):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-cls-n_224x224.dxnn | 6 | [3]:1794.5 · [4]:2436.0 · [5]:2714.8 · **[6]:2866.8 ★** · [7]:2871.4 · [8]:2875.2 · [9]:2874.7 |
| yolo26-cls-s_224x224.dxnn | 5 | [3]:1192.5 · [4]:1484.0 · **[5]:1513.9 ★** · [6]:1525.1 · [7]:1523.2 · [8]:1523.4 |
| yolo26-cls-m_224x224.dxnn | 5 | [3]:878.8 · [4]:1033.5 · **[5]:1056.3 ★** · [6]:1057.6 · [7]:1057.9 · [8]:1057.4 |
| yolo26-cls-l_224x224.dxnn | 4 | [3]:605.2 · **[4]:711.3 ★** · [5]:712.0 · [6]:712.4 · [7]:712.6 |
| yolo26-cls-x_224x224.dxnn | 4 | [3]:335.3 · **[4]:384.3 ★** · [5]:384.2 · [6]:384.5 · [7]:384.4 |


### Latency (Single-Core, Sync)

#### Object Detection

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_640x640.dxnn | 39.4 | 25.39 | 23.08 | 2.31 | 46 | ok |
| yolo26-s_640x640.dxnn | 30.9 | 32.38 | 29.94 | 2.44 | 56 | ok |
| yolo26-m_640x640.dxnn | 23.6 | 42.37 | 39.75 | 2.62 | 57 | ok |
| yolo26-l_640x640.dxnn | 20.5 | 48.88 | 46.26 | 2.62 | 58 | ok |
| yolo26-x_640x640.dxnn | 12.9 | 77.62 | 75.07 | 2.56 | 60 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_640x640.dxnn | 44.1 | 22.67 | 22.67 | N/A | 55 | ok |
| yolo26-s_640x640.dxnn | 32.4 | 30.88 | 30.88 | N/A | 56 | ok |
| yolo26-m_640x640.dxnn | 25.8 | 38.73 | 38.73 | N/A | 57 | ok |
| yolo26-l_640x640.dxnn | 21.9 | 45.65 | 45.65 | N/A | 58 | ok |
| yolo26-x_640x640.dxnn | 13.3 | 75.22 | 75.22 | N/A | 60 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-pose_640x640.dxnn | 44.3 | 22.59 | 21.02 | 1.57 | 56 | ok |
| yolo26-s-pose_640x640.dxnn | 35.1 | 28.52 | 26.93 | 1.60 | 56 | ok |
| yolo26-m-pose_640x640.dxnn | 28.2 | 35.47 | 33.98 | 1.49 | 57 | ok |
| yolo26-l-pose_640x640.dxnn | 22.1 | 45.32 | 43.81 | 1.51 | 58 | ok |
| yolo26-x-pose_640x640.dxnn | 13.4 | 74.77 | 73.20 | 1.57 | 61 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-pose_640x640.dxnn | 49.5 | 20.21 | 20.21 | N/A | 56 | ok |
| yolo26-s-pose_640x640.dxnn | 37.9 | 26.38 | 26.38 | N/A | 57 | ok |
| yolo26-m-pose_640x640.dxnn | 28.7 | 34.85 | 34.85 | N/A | 57 | ok |
| yolo26-l-pose_640x640.dxnn | 22.9 | 43.62 | 43.62 | N/A | 58 | ok |
| yolo26-x-pose_640x640.dxnn | 13.7 | 73.05 | 73.05 | N/A | 61 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-seg_640x640.dxnn | 24.3 | 41.21 | 38.13 | 3.08 | 55 | ok |
| yolo26-s-seg_640x640.dxnn | 18.7 | 53.46 | 50.35 | 3.11 | 56 | ok |
| yolo26-m-seg_640x640.dxnn | 14.4 | 69.46 | 66.40 | 3.06 | 59 | ok |
| yolo26-l-seg_640x640.dxnn | 13.0 | 76.89 | 73.88 | 3.01 | 59 | ok |
| yolo26-x-seg_640x640.dxnn | 8.6 | 116.61 | 113.50 | 3.11 | 63 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-seg_640x640.dxnn | 24.3 | 41.18 | 41.18 | N/A | 55 | ok |
| yolo26-s-seg_640x640.dxnn | 20.5 | 48.71 | 48.71 | N/A | 56 | ok |
| yolo26-m-seg_640x640.dxnn | 15.4 | 64.98 | 64.98 | N/A | 59 | ok |
| yolo26-l-seg_640x640.dxnn | 14.3 | 70.14 | 70.14 | N/A | 59 | ok |
| yolo26-x-seg_640x640.dxnn | 8.6 | 116.37 | 116.37 | N/A | 63 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-obb_1024x1024.dxnn | 24.4 | 40.97 | 39.18 | 1.79 | 57 | ok |
| yolo26-s-obb_1024x1024.dxnn | 17.3 | 57.67 | 56.00 | 1.67 | 58 | ok |
| yolo26-m-obb_1024x1024.dxnn | 12.6 | 79.30 | 77.57 | 1.73 | 61 | ok |
| yolo26-l-obb_1024x1024.dxnn | 9.9 | 101.22 | 99.46 | 1.77 | 63 | ok |
| yolo26-x-obb_1024x1024.dxnn | 5.6 | 179.54 | 177.69 | 1.85 | 67 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-obb_1024x1024.dxnn | 26.2 | 38.23 | 38.23 | N/A | 57 | ok |
| yolo26-s-obb_1024x1024.dxnn | 17.8 | 56.03 | 56.03 | N/A | 59 | ok |
| yolo26-m-obb_1024x1024.dxnn | 13.0 | 77.11 | 77.11 | N/A | 62 | ok |
| yolo26-l-obb_1024x1024.dxnn | 10.1 | 98.96 | 98.96 | N/A | 63 | ok |
| yolo26-x-obb_1024x1024.dxnn | 5.6 | 177.70 | 177.70 | N/A | 68 | ok |

#### Classification

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-cls-n_224x224.dxnn | 628.4 | 1.59 | 1.59 | N/A | 55 | ok |
| yolo26-cls-s_224x224.dxnn | 427.4 | 2.34 | 2.34 | N/A | 54 | ok |
| yolo26-cls-m_224x224.dxnn | 326.3 | 3.06 | 3.06 | N/A | 54 | ok |
| yolo26-cls-l_224x224.dxnn | 229.5 | 4.36 | 4.36 | N/A | 55 | ok |
| yolo26-cls-x_224x224.dxnn | 137.3 | 7.28 | 7.28 | N/A | 56 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-cls-n_224x224.dxnn | 637.9 | 1.57 | 1.57 | N/A | 54 | ok |
| yolo26-cls-s_224x224.dxnn | 430.8 | 2.32 | 2.32 | N/A | 54 | ok |
| yolo26-cls-m_224x224.dxnn | 329.6 | 3.03 | 3.03 | N/A | 55 | ok |
| yolo26-cls-l_224x224.dxnn | 229.4 | 4.36 | 4.36 | N/A | 55 | ok |
| yolo26-cls-x_224x224.dxnn | 137.9 | 7.25 | 7.25 | N/A | 56 | ok |

## E2E Pipeline (Single-Stream)

### Object Detection

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | avdec_h264 | 3455 | 3 | 66.2 ±0.0 | 52.23 | 328 | 19.8 | 49.3 | 55~56 | 1000 | 420 | ok |
| yolo26-s_640x640.dxnn | avdec_h264 | 3455 | 3 | 66.3 ±0.1 | 52.08 | 320 | 35.0 | 67.1 | 59~63 | 1000 | 437 | ok |
| yolo26-m_640x640.dxnn | avdec_h264 | 3455 | 3 | 65.5 ±0.4 | 52.72 | 298 | 64.9 | 97.6 | 76~85 | 400~1000 | 472 | ok |
| yolo26-l_640x640.dxnn | avdec_h264 | 3455 | 3 | 52.1 ±9.6 | 66.34 | 176 | 92.5 | 100.0 | 82~86 | 400~1000 | 486 | ok |
| yolo26-x_640x640.dxnn | avdec_h264 | 3455 | 3 | 20.6 ±1.1 | 167.35 | 60 | 94.9 | 100.0 | 86~87 | 300~800 | 580 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | avdec_h264 | 3455 | 3 | 79.5 ±0.5 | 43.48 | 307 | 21.7 | 65.5 | 58~59 | 1000 | 445 | ok |
| yolo26-s_640x640.dxnn | avdec_h264 | 3455 | 3 | 80.2 ±0.7 | 43.09 | 305 | 40.6 | 75.0 | 63~66 | 1000 | 465 | ok |
| yolo26-m_640x640.dxnn | avdec_h264 | 3455 | 3 | 75.4 ±6.3 | 45.83 | 280 | 82.5 | 100.0 | 77~85 | 400~1000 | 496 | ok |
| yolo26-l_640x640.dxnn | avdec_h264 | 3455 | 3 | 53.1 ±11.4 | 65.11 | 182 | 93.6 | 100.0 | 83~86 | 400~1000 | 489 | ok |
| yolo26-x_640x640.dxnn | avdec_h264 | 3455 | 3 | 21.8 ±2.0 | 158.33 | 73 | 94.6 | 100.0 | 86~90 | 300~1000 | 584 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n_640x640.dxnn | 66.2 | 79.5 | -13.3 | -16.8% |
| yolo26-s_640x640.dxnn | 66.3 | 80.2 | -13.8 | -17.3% |
| yolo26-m_640x640.dxnn | 65.5 | 75.4 | -9.9 | -13.1% |
| yolo26-l_640x640.dxnn | 52.1 | 53.1 | -1.0 | -1.8% |
| yolo26-x_640x640.dxnn | 20.6 | 21.8 | -1.2 | -5.4% |

### Pose Estimation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 80.1 ±0.1 | 43.15 | 342 | 26.3 | 55.7 | 59~61 | 1000 | 398 | ok |
| yolo26-s-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 80.5 ±0.2 | 42.93 | 330 | 47.0 | 74.3 | 64~66 | 1000 | 420 | ok |
| yolo26-m-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 68.0 ±10.8 | 50.80 | 213 | 87.7 | 100.0 | 82~86 | 400~1000 | 453 | ok |
| yolo26-l-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 48.2 ±13.4 | 71.61 | 122 | 94.2 | 100.0 | 84~87 | 300~1000 | 466 | ok |
| yolo26-x-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 20.3 ±0.8 | 170.01 | 48 | 51.3 | 100.0 | 88~90 | 1000 | 561 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 112.0 ±0.2 | 30.84 | 327 | 36.1 | 65.1 | 60~63 | 1000 | 382 | ok |
| yolo26-s-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 111.9 ±0.1 | 30.88 | 314 | 67.5 | 86.8 | 67~70 | 1000 | 413 | ok |
| yolo26-m-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 70.7 ±16.3 | 48.87 | 152 | 92.1 | 100.0 | 82~86 | 300~1000 | 439 | ok |
| yolo26-l-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 53.0 ±13.8 | 65.18 | 108 | 80.3 | 100.0 | 85~90 | 400~1000 | 454 | ok |
| yolo26-x-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 20.1 ±1.4 | 171.53 | 41 | 51.0 | 100.0 | 88~90 | 1000 | 548 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-pose_640x640.dxnn | 80.1 | 112.0 | -32.0 | -28.5% |
| yolo26-s-pose_640x640.dxnn | 80.5 | 111.9 | -31.4 | -28.1% |
| yolo26-m-pose_640x640.dxnn | 68.0 | 70.7 | -2.7 | -3.8% |
| yolo26-l-pose_640x640.dxnn | 48.2 | 53.0 | -4.8 | -9.0% |
| yolo26-x-pose_640x640.dxnn | 20.3 | 20.1 | +0.2 | +0.9% |

### Segmentation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 44.1 ±0.2 | 78.35 | 319 | 17.4 | 41.7 | 59~60 | 1000 | 539 | ok |
| yolo26-s-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 44.1 ±0.2 | 78.40 | 311 | 31.5 | 64.9 | 66~69 | 1000 | 562 | ok |
| yolo26-m-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 34.1 ±7.3 | 101.45 | 228 | 49.8 | 83.7 | 88~91 | 1000 | 600 | ok |
| yolo26-l-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 28.2 ±5.1 | 122.62 | 173 | 53.0 | 94.9 | 89 | 1000 | 612 | ok |
| yolo26-x-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 13.6 ±0.5 | 254.58 | 55 | 46.9 | 100.0 | 94~95 | 1000 | 718 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 54.9 ±0.3 | 62.88 | 352 | 20.4 | 59.7 | 60~62 | 1000 | 582 | ok |
| yolo26-s-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 54.9 ±0.3 | 62.88 | 345 | 38.3 | 72.2 | 68~73 | 1000 | 605 | ok |
| yolo26-m-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 33.2 ±3.0 | 103.97 | 191 | 52.0 | 94.4 | 88~90 | 1000 | 626 | ok |
| yolo26-l-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 27.8 ±6.3 | 124.16 | 143 | 52.2 | 100.0 | 89~91 | 1000 | 624 | ok |
| yolo26-x-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 13.5 ±0.3 | 255.92 | 60 | 46.6 | 100.0 | 94~96 | 1000 | 735 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-seg_640x640.dxnn | 44.1 | 54.9 | -10.8 | -19.7% |
| yolo26-s-seg_640x640.dxnn | 44.1 | 54.9 | -10.9 | -19.8% |
| yolo26-m-seg_640x640.dxnn | 34.1 | 33.2 | +0.8 | +2.5% |
| yolo26-l-seg_640x640.dxnn | 28.2 | 27.8 | +0.4 | +1.3% |
| yolo26-x-seg_640x640.dxnn | 13.6 | 13.5 | +0.1 | +0.5% |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 68.6 ±0.1 | 38.49 | 316 | 78.2 | 93.8 | 67~75 | 1000 | 451 | ok |
| yolo26-s-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 45.1 ±0.5 | 58.55 | 149 | 91.7 | 100.0 | 77~88 | 1000 | 477 | ok |
| yolo26-m-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 22.1 ±4.0 | 119.74 | 72 | 73.2 | 100.0 | 90~92 | 1000 | 511 | ok |
| yolo26-l-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 14.4 ±1.0 | 183.89 | 47 | 60.8 | 100.0 | 89~92 | 1000 | 527 | ok |
| yolo26-x-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 7.3 ±0.9 | 360.39 | 26 | 53.7 | 100.0 | 89~91 | 1000 | 622 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 74.0 ±0.8 | 35.68 | 258 | 89.2 | 100.0 | 70~76 | 1000 | 447 | ok |
| yolo26-s-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 45.9 ±0.0 | 57.49 | 143 | 93.3 | 100.0 | 80~88 | 1000 | 466 | ok |
| yolo26-m-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 19.3 ±3.2 | 136.97 | 61 | 63.5 | 100.0 | 91~92 | 1000 | 502 | ok |
| yolo26-l-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 14.5 ±1.2 | 182.30 | 48 | 62.7 | 100.0 | 91~92 | 1000 | 523 | ok |
| yolo26-x-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 6.6 ±0.1 | 402.33 | 23 | 50.5 | 100.0 | 91~93 | 1000 | 621 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-obb_1024x1024.dxnn | 68.6 | 74.0 | -5.4 | -7.3% |
| yolo26-s-obb_1024x1024.dxnn | 45.1 | 45.9 | -0.8 | -1.8% |
| yolo26-m-obb_1024x1024.dxnn | 22.1 | 19.3 | +2.8 | +14.4% |
| yolo26-l-obb_1024x1024.dxnn | 14.4 | 14.5 | -0.1 | -0.8% |
| yolo26-x-obb_1024x1024.dxnn | 7.3 | 6.6 | +0.8 | +11.7% |

### Classification

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-cls-n_224x224.dxnn | avdec_h264 | 3455 | 3 | 192.2 ±0.4 | 17.98 | 288 | 4.6 | 15.3 | 54~55 | 1000 | 260 | ok |
| yolo26-cls-s_224x224.dxnn | avdec_h264 | 3455 | 3 | 192.4 ±0.7 | 17.96 | 287 | 8.9 | 27.7 | 55 | 1000 | 272 | ok |
| yolo26-cls-m_224x224.dxnn | avdec_h264 | 3455 | 3 | 192.3 ±0.5 | 17.96 | 287 | 13.1 | 35.4 | 56~57 | 1000 | 286 | ok |
| yolo26-cls-l_224x224.dxnn | avdec_h264 | 3455 | 3 | 192.6 ±0.3 | 17.94 | 286 | 20.7 | 47.4 | 58 | 1000 | 295 | ok |
| yolo26-cls-x_224x224.dxnn | avdec_h264 | 3455 | 3 | 191.9 ±0.2 | 18.01 | 285 | 39.3 | 68.6 | 61~64 | 1000 | 346 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-cls-n_224x224.dxnn | avdec_h264 | 3455 | 3 | 192.8 ±0.1 | 17.92 | 287 | 4.5 | 15.0 | 53~54 | 1000 | 261 | ok |
| yolo26-cls-s_224x224.dxnn | avdec_h264 | 3455 | 3 | 191.9 ±0.3 | 18.01 | 287 | 8.9 | 27.4 | 55 | 1000 | 272 | ok |
| yolo26-cls-m_224x224.dxnn | avdec_h264 | 3455 | 3 | 192.3 ±0.7 | 17.97 | 287 | 13.1 | 36.1 | 56~57 | 1000 | 288 | ok |
| yolo26-cls-l_224x224.dxnn | avdec_h264 | 3455 | 3 | 192.1 ±0.6 | 17.99 | 286 | 20.5 | 48.8 | 57~58 | 1000 | 295 | ok |
| yolo26-cls-x_224x224.dxnn | avdec_h264 | 3455 | 3 | 192.5 ±0.6 | 17.95 | 285 | 39.6 | 69.6 | 61~64 | 1000 | 346 | ok |

> Classification has no CPU part, so ORT ON and OFF run the same model; differences between the two tables are measurement noise.

## E2E Pipeline (Multi-Stream)

### Object Detection

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | 2 | 3 | 64.7 ±0.4 | 32.3 | 321 | 19.7 | 47.1 | 57~58 | 1000 | 536 | ok |
| yolo26-n_640x640.dxnn | 3 | 3 | 65.8 ±0.7 | 21.9 | 320 | 20.4 | 47.7 | 56~58 | 1000 | 619 | ok |
| yolo26-s_640x640.dxnn | 2 | 3 | 66.1 ±0.1 | 33.1 | 316 | 36.3 | 67.2 | 66~68 | 1000 | 554 | ok |
| yolo26-s_640x640.dxnn | 3 | 3 | 63.8 ±0.3 | 21.3 | 315 | 35.1 | 67.5 | 67~68 | 1000 | 640 | ok |
| yolo26-m_640x640.dxnn | 2 | 3 | 55.6 ±0.9 | 27.8 | 186 | 94.9 | 100.0 | 85~87 | 300~600 | 584 | ok |
| yolo26-m_640x640.dxnn | 1 | 3 | 65.5 ±0.4 | 65.5 | 298 | 64.9 | 97.6 | 76~85 | 400~1000 | 472 | ok |
| yolo26-l_640x640.dxnn | 1 | 3 | 52.1 ±9.6 | 52.1 | 176 | 92.5 | 100.0 | 82~86 | 400~1000 | 486 | ok |
| yolo26-l_640x640.dxnn | 2 | 3 | 46.4 ±7.9 | 23.2 | 149 | 95.8 | 100.0 | 85~86 | 300~1000 | 598 | ok |
| yolo26-x_640x640.dxnn | 1 | 3 | 20.6 ±1.1 | 20.6 | 60 | 94.9 | 100.0 | 86~87 | 300~800 | 580 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | 2 | 3 | 79.0 ±0.1 | 39.5 | 308 | 22.3 | 66.1 | 57~60 | 1000 | 558 | ok |
| yolo26-n_640x640.dxnn | 3 | 3 | 78.7 ±0.4 | 26.2 | 301 | 22.4 | 66.2 | 60~61 | 1000 | 644 | ok |
| yolo26-s_640x640.dxnn | 2 | 3 | 79.7 ±0.5 | 39.8 | 302 | 41.5 | 75.4 | 70~71 | 1000 | 579 | ok |
| yolo26-s_640x640.dxnn | 3 | 3 | 77.8 ±0.1 | 25.9 | 305 | 41.2 | 75.3 | 71~72 | 1000 | 665 | ok |
| yolo26-m_640x640.dxnn | 2 | 3 | 56.2 ±1.2 | 28.1 | 191 | 96.0 | 100.0 | 86~87 | 300~700 | 597 | ok |
| yolo26-m_640x640.dxnn | 1 | 3 | 75.4 ±6.3 | 75.4 | 280 | 82.5 | 100.0 | 77~85 | 400~1000 | 496 | ok |
| yolo26-l_640x640.dxnn | 1 | 3 | 53.1 ±11.4 | 53.1 | 182 | 93.6 | 100.0 | 83~86 | 400~1000 | 489 | ok |
| yolo26-l_640x640.dxnn | 2 | 3 | 43.2 ±1.6 | 21.6 | 140 | 96.0 | 100.0 | 86~88 | 300~1000 | 606 | ok |
| yolo26-x_640x640.dxnn | 1 | 3 | 21.8 ±2.0 | 21.8 | 73 | 94.6 | 100.0 | 86~90 | 300~1000 | 584 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n_640x640.dxnn | 2 | 32.3 | 2 | 39.5 |
| yolo26-s_640x640.dxnn | 2 | 33.1 | 2 | 39.8 |
| yolo26-m_640x640.dxnn | 1 | 65.5 | 1 | 75.4 |
| yolo26-l_640x640.dxnn | 1 | 52.1 | 1 | 53.1 |

### Pose Estimation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 2 | 3 | 79.1 ±0.9 | 39.6 | 339 | 26.3 | 56.4 | 62~63 | 1000 | 517 | ok |
| yolo26-n-pose_640x640.dxnn | 3 | 3 | 79.4 ±0.8 | 26.5 | 335 | 26.6 | 56.7 | 63~64 | 1000 | 605 | ok |
| yolo26-s-pose_640x640.dxnn | 2 | 3 | 80.2 ±0.1 | 40.1 | 330 | 47.8 | 75.2 | 73~76 | 1000 | 539 | ok |
| yolo26-s-pose_640x640.dxnn | 3 | 3 | 80.1 ±0.2 | 26.7 | 328 | 47.9 | 77.3 | 77 | 1000 | 627 | ok |
| yolo26-m-pose_640x640.dxnn | 2 | 3 | 53.2 ±4.5 | 26.6 | 137 | 95.1 | 100.0 | 86~89 | 300~1000 | 570 | ok |
| yolo26-m-pose_640x640.dxnn | 1 | 3 | 68.0 ±10.8 | 68.0 | 213 | 87.7 | 100.0 | 82~86 | 400~1000 | 453 | ok |
| yolo26-l-pose_640x640.dxnn | 1 | 3 | 48.2 ±13.4 | 48.2 | 122 | 94.2 | 100.0 | 84~87 | 300~1000 | 466 | ok |
| yolo26-l-pose_640x640.dxnn | 2 | 3 | 40.9 ±3.3 | 20.4 | 101 | 96.8 | 100.0 | 87~91 | 300~1000 | 584 | ok |
| yolo26-x-pose_640x640.dxnn | 1 | 3 | 20.3 ±0.8 | 20.3 | 48 | 51.3 | 100.0 | 88~90 | 1000 | 561 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 3 | 3 | 112.7 ±1.0 | 37.6 | 351 | 40.6 | 63.7 | 68~70 | 1000 | 598 | ok |
| yolo26-n-pose_640x640.dxnn | 4 | 3 | 111.8 ±0.8 | 27.9 | 351 | 40.6 | 62.6 | 70~71 | 1000 | 687 | ok |
| yolo26-s-pose_640x640.dxnn | 3 | 3 | 110.2 ±2.4 | 36.7 | 322 | 74.6 | 100.0 | 82~85 | 400~1000 | 618 | ok |
| yolo26-s-pose_640x640.dxnn | 4 | 3 | 103.8 ±5.6 | 25.9 | 279 | 86.7 | 100.0 | 85~87 | 400~1000 | 710 | ok |
| yolo26-m-pose_640x640.dxnn | 2 | 3 | 56.3 ±11.3 | 28.1 | 125 | 95.9 | 100.0 | 86~88 | 300~1000 | 556 | ok |
| yolo26-m-pose_640x640.dxnn | 1 | 3 | 70.7 ±16.3 | 70.7 | 152 | 92.1 | 100.0 | 82~86 | 300~1000 | 439 | ok |
| yolo26-l-pose_640x640.dxnn | 1 | 3 | 53.0 ±13.8 | 53.0 | 108 | 80.3 | 100.0 | 85~90 | 400~1000 | 454 | ok |
| yolo26-l-pose_640x640.dxnn | 2 | 3 | 38.2 ±1.1 | 19.1 | 83 | 54.7 | 100.0 | 89~90 | 1000 | 572 | ok |
| yolo26-x-pose_640x640.dxnn | 1 | 3 | 20.1 ±1.4 | 20.1 | 41 | 51.0 | 100.0 | 88~90 | 1000 | 548 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-pose_640x640.dxnn | 2 | 39.6 | 3 | 37.6 |
| yolo26-s-pose_640x640.dxnn | 2 | 40.1 | 3 | 36.7 |
| yolo26-m-pose_640x640.dxnn | 1 | 68.0 | 1 | 70.7 |
| yolo26-l-pose_640x640.dxnn | 1 | 48.2 | 1 | 53.0 |

### Segmentation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 1 | 3 | 44.1 ±0.2 | 44.1 | 319 | 17.4 | 41.7 | 59~60 | 1000 | 539 | ok |
| yolo26-n-seg_640x640.dxnn | 2 | 3 | 43.9 ±0.1 | 21.9 | 319 | 17.5 | 42.8 | 61~62 | 1000 | 661 | ok |
| yolo26-s-seg_640x640.dxnn | 1 | 3 | 44.1 ±0.2 | 44.1 | 311 | 31.5 | 64.9 | 66~69 | 1000 | 562 | ok |
| yolo26-s-seg_640x640.dxnn | 2 | 3 | 43.9 ±0.0 | 22.0 | 312 | 32.2 | 63.9 | 72 | 1000 | 686 | ok |
| yolo26-m-seg_640x640.dxnn | 1 | 3 | 34.1 ±7.3 | 34.1 | 228 | 49.8 | 83.7 | 88~91 | 1000 | 600 | ok |
| yolo26-m-seg_640x640.dxnn | 2 | 3 | 29.5 ±0.0 | 14.7 | 192 | 42.6 | 85.3 | 90 | 1000 | 719 | ok |
| yolo26-l-seg_640x640.dxnn | 1 | 3 | 28.2 ±5.1 | 28.2 | 173 | 53.0 | 94.9 | 89 | 1000 | 612 | ok |
| yolo26-x-seg_640x640.dxnn | 1 | 3 | 13.6 ±0.5 | 13.6 | 55 | 46.9 | 100.0 | 94~95 | 1000 | 718 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 1 | 3 | 54.9 ±0.3 | 54.9 | 352 | 20.4 | 59.7 | 60~62 | 1000 | 582 | ok |
| yolo26-n-seg_640x640.dxnn | 2 | 3 | 54.6 ±0.0 | 27.3 | 351 | 20.7 | 60.8 | 63~64 | 1000 | 704 | ok |
| yolo26-s-seg_640x640.dxnn | 1 | 3 | 54.9 ±0.3 | 54.9 | 345 | 38.3 | 72.2 | 68~73 | 1000 | 605 | ok |
| yolo26-s-seg_640x640.dxnn | 2 | 3 | 54.5 ±0.3 | 27.3 | 343 | 38.2 | 73.1 | 77 | 1000 | 728 | ok |
| yolo26-m-seg_640x640.dxnn | 1 | 3 | 33.2 ±3.0 | 33.2 | 191 | 52.0 | 94.4 | 88~90 | 1000 | 626 | ok |
| yolo26-m-seg_640x640.dxnn | 2 | 3 | 29.9 ±1.1 | 14.9 | 171 | 47.0 | 94.6 | 89 | 1000 | 750 | ok |
| yolo26-l-seg_640x640.dxnn | 1 | 3 | 27.8 ±6.3 | 27.8 | 143 | 52.2 | 100.0 | 89~91 | 1000 | 624 | ok |
| yolo26-x-seg_640x640.dxnn | 1 | 3 | 13.5 ±0.3 | 13.5 | 60 | 46.6 | 100.0 | 94~96 | 1000 | 735 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-seg_640x640.dxnn | 1 | 44.1 | 1 | 54.9 |
| yolo26-s-seg_640x640.dxnn | 1 | 44.1 | 1 | 54.9 |
| yolo26-m-seg_640x640.dxnn | 1 | 34.1 | 1 | 33.2 |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 2 | 3 | 68.1 ±0.3 | 34.1 | 322 | 79.5 | 96.2 | 82~86 | 1000 | 565 | ok |
| yolo26-n-obb_1024x1024.dxnn | 3 | 3 | 67.6 ±0.4 | 22.5 | 326 | 79.5 | 95.5 | 86 | 1000 | 653 | ok |
| yolo26-s-obb_1024x1024.dxnn | 1 | 3 | 45.1 ±0.5 | 45.1 | 149 | 91.7 | 100.0 | 77~88 | 1000 | 477 | ok |
| yolo26-s-obb_1024x1024.dxnn | 2 | 3 | 38.7 ±0.7 | 19.4 | 139 | 80.8 | 100.0 | 91~93 | 1000 | 590 | ok |
| yolo26-m-obb_1024x1024.dxnn | 1 | 3 | 22.1 ±4.0 | 22.1 | 72 | 73.2 | 100.0 | 90~92 | 1000 | 511 | ok |
| yolo26-l-obb_1024x1024.dxnn | 1 | 3 | 14.4 ±1.0 | 14.4 | 47 | 60.8 | 100.0 | 89~92 | 1000 | 527 | ok |
| yolo26-x-obb_1024x1024.dxnn | 1 | 3 | 7.3 ±0.9 | 7.3 | 26 | 53.7 | 100.0 | 89~91 | 1000 | 622 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 2 | 3 | 74.3 ±1.0 | 37.2 | 271 | 92.4 | 100.0 | 84~87 | 1000 | 564 | ok |
| yolo26-n-obb_1024x1024.dxnn | 3 | 3 | 74.1 ±1.0 | 24.7 | 273 | 92.9 | 100.0 | 89~91 | 1000 | 649 | ok |
| yolo26-s-obb_1024x1024.dxnn | 1 | 3 | 45.9 ±0.0 | 45.9 | 143 | 93.3 | 100.0 | 80~88 | 1000 | 466 | ok |
| yolo26-s-obb_1024x1024.dxnn | 2 | 3 | 39.0 ±1.1 | 19.5 | 130 | 81.7 | 100.0 | 92~94 | 1000 | 587 | ok |
| yolo26-m-obb_1024x1024.dxnn | 1 | 3 | 19.3 ±3.2 | 19.3 | 61 | 63.5 | 100.0 | 91~92 | 1000 | 502 | ok |
| yolo26-l-obb_1024x1024.dxnn | 1 | 3 | 14.5 ±1.2 | 14.5 | 48 | 62.7 | 100.0 | 91~92 | 1000 | 523 | ok |
| yolo26-x-obb_1024x1024.dxnn | 1 | 3 | 6.6 ±0.1 | 6.6 | 23 | 50.5 | 100.0 | 91~93 | 1000 | 621 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-obb_1024x1024.dxnn | 2 | 34.1 | 2 | 37.2 |
| yolo26-s-obb_1024x1024.dxnn | 1 | 45.1 | 1 | 45.9 |

---
*Report generated by dx-benchmark tool*
