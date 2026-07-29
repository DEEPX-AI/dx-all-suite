# YOLO26 Benchmark Report

**Generated:** 2026-07-21 20:13:36 (Local)

## Test Timing

| # | Type | Start | End | Duration |
|---|------|-------|-----|----------|
| 1 | run | 2026-07-16 17:42:31 | 2026-07-17 21:15:15 | 27h 32m 43s |

## Executive Summary

### Object Detection

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n.dxnn | ON | 21.90 | 226.2 | 175.3 | 5 |
| yolo26n.dxnn | OFF | 23.03 | 228.4 | 191.5 | 6 |
| yolo26s.dxnn | ON | 31.80 | 132.0 | 131.3 | 4 |
| yolo26s.dxnn | OFF | 30.21 | 131.7 | 131.0 | 4 |
| yolo26m.dxnn | ON | 39.27 | 91.4 | 91.2 | 2 |
| yolo26m.dxnn | OFF | 37.88 | 91.1 | 90.8 | 2 |
| yolo26l.dxnn | ON | 46.90 | 66.2 | 66.6 | 2 |
| yolo26l.dxnn | OFF | 46.05 | 66.9 | 66.5 | 2 |
| yolo26x.dxnn | ON | 74.94 | 39.0 | 38.8 | 1 |
| yolo26x.dxnn | OFF | 73.36 | 39.0 | 38.6 | 1 |

### Pose Estimation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-pose.dxnn | ON | 21.74 | 218.6 | 183.1 | 6 |
| yolo26n-pose.dxnn | OFF | 20.74 | 217.8 | 211.0 | 7 |
| yolo26s-pose.dxnn | ON | 29.46 | 126.3 | 126.2 | 4 |
| yolo26s-pose.dxnn | OFF | 28.43 | 127.1 | 126.4 | 4 |
| yolo26m-pose.dxnn | ON | 36.92 | 87.8 | 87.7 | 2 |
| yolo26m-pose.dxnn | OFF | 35.85 | 89.3 | 87.7 | 2 |
| yolo26l-pose.dxnn | ON | 44.89 | 66.2 | 64.8 | 2 |
| yolo26l-pose.dxnn | OFF | 44.03 | 66.1 | 65.1 | 2 |
| yolo26x-pose.dxnn | ON | 72.79 | 38.2 | 38.2 | 1 |
| yolo26x-pose.dxnn | OFF | 71.76 | 37.8 | 38.1 | 1 |

### Segmentation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-seg.dxnn | ON | 38.06 | 142.8 | 107.6 | 3 |
| yolo26n-seg.dxnn | OFF | 35.47 | 170.9 | 117.7 | 3 |
| yolo26s-seg.dxnn | ON | 47.60 | 102.1 | 95.8 | 3 |
| yolo26s-seg.dxnn | OFF | 45.37 | 102.7 | 99.7 | 3 |
| yolo26m-seg.dxnn | ON | 61.20 | 66.2 | 66.0 | 1 |
| yolo26m-seg.dxnn | OFF | 58.63 | 65.2 | 65.4 | 1 |
| yolo26l-seg.dxnn | ON | 69.04 | 51.8 | 52.0 | 1 |
| yolo26l-seg.dxnn | OFF | 67.24 | 52.2 | 51.6 | 1 |
| yolo26x-seg.dxnn | ON | 108.06 | 29.2 | 25.9 | — |
| yolo26x-seg.dxnn | OFF | 107.20 | 29.1 | 25.6 | — |

### Oriented BBox (OBB)

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-obb.dxnn | ON | 37.28 | 74.5 | 74.3 | 2 |
| yolo26n-obb.dxnn | OFF | 36.26 | 74.7 | 74.2 | 2 |
| yolo26s-obb.dxnn | ON | 54.76 | 43.7 | 43.7 | 1 |
| yolo26s-obb.dxnn | OFF | 53.18 | 43.7 | 43.7 | 1 |
| yolo26m-obb.dxnn | ON | 72.54 | 32.0 | 32.0 | 1 |
| yolo26m-obb.dxnn | OFF | 71.75 | 32.0 | 31.9 | 1 |
| yolo26l-obb.dxnn | ON | 93.69 | 23.4 | 23.4 | — |
| yolo26l-obb.dxnn | OFF | 92.32 | 23.4 | 23.4 | — |
| yolo26x-obb.dxnn | ON | 166.05 | 13.6 | 12.7 | — |
| yolo26x-obb.dxnn | OFF | 164.45 | 13.6 | 12.7 | — |

### Classification

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-cls.dxnn | ON | 1.33 | 3514.4 | 283.9 | — |
| yolo26n-cls.dxnn | OFF | 1.33 | 3514.0 | 284.9 | — |
| yolo26s-cls.dxnn | ON | 2.00 | 1898.3 | 293.2 | — |
| yolo26s-cls.dxnn | OFF | 2.00 | 1898.4 | 293.3 | — |
| yolo26m-cls.dxnn | ON | 2.68 | 1341.9 | 293.0 | — |
| yolo26m-cls.dxnn | OFF | 2.69 | 1342.4 | 292.4 | — |
| yolo26l-cls.dxnn | ON | 4.35 | 846.7 | 294.1 | — |
| yolo26l-cls.dxnn | OFF | 4.44 | 846.1 | 292.9 | — |
| yolo26x-cls.dxnn | ON | 7.59 | 453.0 | 292.1 | — |
| yolo26x-cls.dxnn | OFF | 7.48 | 452.9 | 291.7 | — |

## Environment

| Item | Value |
|------|-------|
| Product | DX-AIPlayer-N97 |
| Hostname | deepx |
| OS | Ubuntu 24.04.4 LTS |
| Kernel | 6.17.0-35-generic |
| CPU | Intel(R) N97 |
| CPU Cores | 4 |
| RAM | 7.5 GB |
| NPU SKU | M1 |
| DX-AllSuite | v2.3.3 |
| NPU RT | v3.3.2 |
| NPU Driver (RT) | v2.4.1 |
| NPU Driver (PCIe) | v2.2.0 |
| NPU Firmware | v2.5.6 |
| NPU Memory | LPDDR5 5600 Mbps, 3.92GiB |
| NPU Board | M.2, Rev 1.0 |
| NPU PCIe | Gen3 X2 [03:00:00] |

### Tools

| Tool | Available | Version |
|------|-----------|---------|
| run_model | Yes | DXRT v3.3.2 run_model |
| gst-launch-1.0 | Yes | gst-launch-1.0 version 1.24.2 |
| gst-inspect-1.0 | Yes | gst-inspect-1.0 version 1.24.2 |
| dxtop | Yes | DX-TOP 1.1.0 |
| ffprobe | Yes | ffprobe version 6.1.1-3ubuntu5 Copyright (c) 2007-2023 the F... |

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
| Version | v3 |
| Thermal Mode | steady |
| Throughput Time | 30 s |
| Latency Loops | 300 |
| Model Warmup | 1 |
| Model Latency Runs | 1 |
| Model Throughput Runs | 3 |
| E2E Runs | 3 |
| FPS Threshold | 30.0 |
| Multi-Stream Search | single-stream-estimate-linear-boundary |
| Stable Capacity Rule | status_ok_and_all_runs_success_and_avg_per_channel_fps_ge_threshold |
| Cooldown Target ΔT | 10.0 °C |
| Cooldown Absolute Cap | 55.0 °C |
| Hot-Start Block | 60.0 °C |
| Cooldown Max Time | 1000.0 s |
| NPU Warmup | 1.0 s |
| NPU Drain | 0.5 s |

## Benchmarked Models

| Model | Task | Input Size | NPU Memory (MB) | ORT CPU Offload | Multi-Stream Sweep |
|-------|------|------------|:----------------:|:---------------:|:------------------:|
| yolo26n.dxnn | Object Detection | 640×640 | 116.5 | Yes | ✅ |
| yolo26s.dxnn | Object Detection | 640×640 | 151.6 | Yes | ✅ |
| yolo26m.dxnn | Object Detection | 640×640 | 241.9 | Yes | ✅ |
| yolo26l.dxnn | Object Detection | 640×640 | 293.5 | Yes | ✅ |
| yolo26x.dxnn | Object Detection | 640×640 | 522.7 | Yes | ✅ |
| yolo26n-pose.dxnn | Pose Estimation | 640×640 | 118.5 | Yes | ✅ |
| yolo26s-pose.dxnn | Pose Estimation | 640×640 | 158.7 | Yes | ✅ |
| yolo26m-pose.dxnn | Pose Estimation | 640×640 | 254.0 | Yes | ✅ |
| yolo26l-pose.dxnn | Pose Estimation | 640×640 | 305.6 | Yes | ✅ |
| yolo26x-pose.dxnn | Pose Estimation | 640×640 | 516.5 | Yes | ✅ |
| yolo26n-seg.dxnn | Segmentation | 640×640 | 138.8 | Yes | ✅ |
| yolo26s-seg.dxnn | Segmentation | 640×640 | 177.6 | Yes | ✅ |
| yolo26m-seg.dxnn | Segmentation | 640×640 | 270.2 | Yes | ✅ |
| yolo26l-seg.dxnn | Segmentation | 640×640 | 321.8 | Yes | ✅ |
| yolo26x-seg.dxnn | Segmentation | 640×640 | 555.0 | Yes | ✅ |
| yolo26n-obb.dxnn | Oriented BBox (OBB) | 1024×1024 | 240.6 | Yes | ✅ |
| yolo26s-obb.dxnn | Oriented BBox (OBB) | 1024×1024 | 447.2 | Yes | ✅ |
| yolo26m-obb.dxnn | Oriented BBox (OBB) | 1024×1024 | 645.3 | Yes | ✅ |
| yolo26l-obb.dxnn | Oriented BBox (OBB) | 1024×1024 | 790.1 | Yes | ✅ |
| yolo26x-obb.dxnn | Oriented BBox (OBB) | 1024×1024 | 1316.5 | Yes | ✅ |
| yolo26n-cls.dxnn | Classification | 224×224 | 4.5 | No | — |
| yolo26s-cls.dxnn | Classification | 224×224 | 9.0 | No | — |
| yolo26m-cls.dxnn | Classification | 224×224 | 15.8 | No | — |
| yolo26l-cls.dxnn | Classification | 224×224 | 19.5 | No | — |
| yolo26x-cls.dxnn | Classification | 224×224 | 48.6 | No | — |

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

> **Buffer-count sweep (★)** — the _Buffer-count sweep_ tables below list throughput fps per `--buffer-count`; ★ marks the winner (highest measured throughput, at full probe precision; fps rounded to 1 decimal). A smaller buffer-count wins only on an exact tie. The sweep's goal is the throughput ceiling — the winning buffer-count value itself is secondary, since tied buffer-counts deliver effectively equal throughput.

#### Object Detection

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n.dxnn | 226.2 ±0.6 | 9 | 254 | 90.0 | 100.0 | 52~56 | 1000 | ok |
| yolo26s.dxnn | 132.0 ±0.1 | 6 | 153 | 91.4 | 100.0 | 60~63 | 1000 | ok |
| yolo26m.dxnn | 91.4 ±0.3 | 7 | 129 | 92.7 | 100.0 | 64~67 | 1000 | ok |
| yolo26l.dxnn | 66.2 ±0.2 | 5 | 95 | 88.9 | 100.0 | 64~67 | 1000 | ok |
| yolo26x.dxnn | 39.0 ±0.1 | 4 | 55 | 91.6 | 100.0 | 66~70 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n.dxnn | 9 | [3]:114.0 · [4]:154.3 · [5]:179.6 · [6]:197.4 · [7]:214.0 · [8]:222.8 · **[9]:227.1 ★** · [10]:225.9 · [11]:224.9 |
| yolo26s.dxnn | 6 | [3]:76.2 · [4]:102.8 · [5]:129.0 · **[6]:131.6 ★** · [7]:130.9 · [8]:130.9 |
| yolo26m.dxnn | 7 | [3]:58.9 · [4]:80.9 · [5]:91.7 · [6]:91.2 · **[7]:91.8 ★** · [8]:90.3 |
| yolo26l.dxnn | 5 | [3]:47.7 · [4]:64.6 · **[5]:66.8 ★** · [6]:66.3 · [7]:66.3 · [8]:66.7 |
| yolo26x.dxnn | 4 | [3]:31.7 · **[4]:38.8 ★** · [5]:37.7 · [6]:38.0 · [7]:38.1 · [8]:38.0 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n.dxnn | 228.4 ±0.3 | 7 | 166 | 90.7 | 100.0 | 59~61 | 1000 | ok |
| yolo26s.dxnn | 131.7 ±0.1 | 5 | 107 | 90.7 | 100.0 | 60~62 | 1000 | ok |
| yolo26m.dxnn | 91.1 ±0.2 | 5 | 87 | 92.3 | 100.0 | 64~68 | 1000 | ok |
| yolo26l.dxnn | 66.9 ±0.1 | 4 | 62 | 90.4 | 100.0 | 64~67 | 1000 | ok |
| yolo26x.dxnn | 39.0 ±0.1 | 4 | 41 | 89.2 | 100.0 | 66~70 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n.dxnn | 7 | [3]:109.5 · [4]:142.6 · [5]:200.3 · [6]:220.8 · **[7]:228.2 ★** · [8]:226.5 |
| yolo26s.dxnn | 5 | [3]:76.6 · [4]:105.2 · **[5]:131.4 ★** · [6]:130.9 · [7]:130.8 · [8]:130.6 |
| yolo26m.dxnn | 5 | [3]:62.3 · [4]:84.3 · **[5]:91.0 ★** · [6]:90.9 · [7]:90.9 · [8]:90.3 |
| yolo26l.dxnn | 4 | [3]:49.3 · **[4]:66.7 ★** · [5]:65.9 · [6]:66.6 · [7]:66.5 · [8]:66.5 |
| yolo26x.dxnn | 4 | [3]:31.2 · **[4]:38.8 ★** · [5]:38.2 · [6]:37.9 · [7]:38.5 · [8]:38.1 |


#### Pose Estimation

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-pose.dxnn | 218.6 ±0.0 | 7 | 180 | 91.0 | 100.0 | 59~61 | 1000 | ok |
| yolo26s-pose.dxnn | 126.3 ±0.3 | 6 | 132 | 90.9 | 100.0 | 60~63 | 1000 | ok |
| yolo26m-pose.dxnn | 87.8 ±0.2 | 8 | 102 | 92.0 | 100.0 | 66~69 | 1000 | ok |
| yolo26l-pose.dxnn | 66.2 ±0.0 | 4 | 66 | 89.6 | 100.0 | 63~67 | 1000 | ok |
| yolo26x-pose.dxnn | 38.2 ±0.0 | 4 | 43 | 88.4 | 100.0 | 66~69 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-pose.dxnn | 7 | [3]:119.9 · [4]:153.8 · [5]:202.2 · [6]:217.3 · **[7]:218.6 ★** · [8]:216.6 |
| yolo26s-pose.dxnn | 6 | [3]:79.7 · [4]:108.5 · [5]:126.5 · **[6]:127.0 ★** · [7]:126.1 · [8]:125.8 |
| yolo26m-pose.dxnn | 8 | [3]:62.3 · [4]:84.3 · [5]:86.9 · [6]:87.5 · [7]:87.8 · **[8]:87.9 ★** · [9]:87.5 · [10]:87.2 |
| yolo26l-pose.dxnn | 4 | [3]:49.5 · **[4]:66.0 ★** · [5]:64.3 · [6]:64.7 · [7]:64.8 · [8]:65.0 |
| yolo26x-pose.dxnn | 4 | [3]:32.1 · **[4]:38.1 ★** · [5]:37.5 · [6]:37.3 · [7]:37.1 · [8]:37.4 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-pose.dxnn | 217.8 ±0.1 | 6 | 152 | 90.9 | 100.0 | 59~61 | 1000 | ok |
| yolo26s-pose.dxnn | 127.1 ±0.2 | 5 | 88 | 91.5 | 100.0 | 60~63 | 1000 | ok |
| yolo26m-pose.dxnn | 89.3 ±0.0 | 4 | 61 | 90.6 | 100.0 | 64~68 | 1000 | ok |
| yolo26l-pose.dxnn | 66.1 ±0.0 | 4 | 50 | 90.9 | 100.0 | 64~67 | 1000 | ok |
| yolo26x-pose.dxnn | 37.8 ±0.4 | 6 | 33 | 89.9 | 100.0 | 65~69 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-pose.dxnn | 6 | [3]:118.0 · [4]:167.6 · [5]:210.7 · **[6]:217.2 ★** · [7]:215.6 · [8]:215.4 |
| yolo26s-pose.dxnn | 5 | [3]:82.9 · [4]:113.2 · **[5]:126.6 ★** · [6]:125.8 · [7]:126.4 · [8]:126.1 |
| yolo26m-pose.dxnn | 4 | [3]:65.2 · **[4]:88.7 ★** · [5]:86.9 · [6]:88.2 · [7]:87.6 · [8]:87.9 |
| yolo26l-pose.dxnn | 4 | [3]:52.2 · **[4]:65.9 ★** · [5]:64.1 · [6]:64.5 · [7]:64.7 · [8]:64.7 |
| yolo26x-pose.dxnn | 6 | [3]:32.3 · [4]:37.9 · [5]:37.2 · **[6]:38.2 ★** · [7]:37.3 · [8]:37.2 |


#### Segmentation

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-seg.dxnn | 142.8 ±0.5 | 12 | 373 | 62.9 | 83.1 | 59~61 | 1000 | ok |
| yolo26s-seg.dxnn | 102.1 ±0.1 | 7 | 234 | 90.9 | 100.0 | 61~65 | 1000 | ok |
| yolo26m-seg.dxnn | 66.2 ±0.1 | 6 | 167 | 89.3 | 100.0 | 66~71 | 1000 | ok |
| yolo26l-seg.dxnn | 51.8 ±0.4 | 7 | 128 | 88.8 | 100.0 | 66~70 | 1000 | ok |
| yolo26x-seg.dxnn | 29.2 ±0.6 | 5 | 70 | 89.4 | 100.0 | 68~73 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-seg.dxnn | 12 | [3]:77.5 · [4]:93.1 · [5]:105.4 · [6]:122.1 · [7]:131.1 · [8]:138.0 · [9]:136.9 · [10]:141.3 · [11]:142.3 · **[12]:142.8 ★** |
| yolo26s-seg.dxnn | 7 | [3]:45.1 · [4]:77.0 · [5]:90.3 · [6]:99.2 · **[7]:101.7 ★** · [8]:101.3 |
| yolo26m-seg.dxnn | 6 | [3]:35.4 · [4]:50.3 · [5]:64.4 · **[6]:66.0 ★** · [7]:65.7 · [8]:64.9 |
| yolo26l-seg.dxnn | 7 | [3]:30.8 · [4]:42.5 · [5]:51.2 · [6]:51.1 · **[7]:52.0 ★** · [8]:51.9 |
| yolo26x-seg.dxnn | 5 | [3]:22.2 · [4]:28.8 · **[5]:29.2 ★** · [6]:28.3 · [7]:28.3 · [8]:28.5 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-seg.dxnn | 170.9 ±0.4 | 9 | 306 | 90.1 | 100.0 | 61~63 | 1000 | ok |
| yolo26s-seg.dxnn | 102.7 ±0.1 | 7 | 168 | 90.9 | 100.0 | 61~64 | 1000 | ok |
| yolo26m-seg.dxnn | 65.2 ±0.2 | 8 | 139 | 91.7 | 100.0 | 68~72 | 1000 | ok |
| yolo26l-seg.dxnn | 52.2 ±0.1 | 5 | 82 | 90.8 | 100.0 | 66~70 | 1000 | ok |
| yolo26x-seg.dxnn | 29.1 ±0.0 | 4 | 54 | 89.4 | 100.0 | 68~73 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-seg.dxnn | 9 | [3]:57.3 · [4]:100.1 · [5]:116.3 · [6]:131.0 · [7]:152.1 · [8]:166.0 · **[9]:170.3 ★** · [10]:169.0 · [11]:169.1 |
| yolo26s-seg.dxnn | 7 | [3]:42.9 · [4]:65.2 · [5]:97.3 · [6]:99.2 · **[7]:102.8 ★** · [8]:101.0 |
| yolo26m-seg.dxnn | 8 | [3]:34.2 · [4]:46.4 · [5]:65.2 · [6]:65.2 · [7]:65.4 · **[8]:66.0 ★** · [9]:65.2 · [10]:64.8 |
| yolo26l-seg.dxnn | 5 | [3]:31.2 · [4]:42.3 · **[5]:52.0 ★** · [6]:51.2 · [7]:51.0 · [8]:51.2 |
| yolo26x-seg.dxnn | 4 | [3]:21.7 · **[4]:28.8 ★** · [5]:28.8 · [6]:28.3 · [7]:28.5 · [8]:28.5 |


#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-obb.dxnn | 74.5 ±0.2 | 9 | 84 | 92.5 | 100.0 | 60~61 | 1000 | ok |
| yolo26s-obb.dxnn | 43.7 ±0.0 | 10 | 52 | 93.0 | 100.0 | 61~63 | 1000 | ok |
| yolo26m-obb.dxnn | 32.0 ±0.0 | 4 | 39 | 89.8 | 100.0 | 64~67 | 1000 | ok |
| yolo26l-obb.dxnn | 23.4 ±0.1 | 7 | 28 | 89.3 | 100.0 | 64~67 | 1000 | ok |
| yolo26x-obb.dxnn | 13.6 ±0.0 | 5 | 17 | 86.0 | 100.0 | 66~69 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-obb.dxnn | 9 | [3]:56.3 · [4]:72.1 · [5]:74.0 · [6]:74.2 · [7]:74.0 · [8]:74.4 · **[9]:74.4 ★** · [10]:74.3 |
| yolo26s-obb.dxnn | 10 | [3]:36.2 · [4]:43.5 · [5]:43.0 · [6]:43.5 · [7]:43.7 · [8]:43.7 · [9]:43.6 · **[10]:43.7 ★** |
| yolo26m-obb.dxnn | 4 | [3]:28.7 · **[4]:32.0 ★** · [5]:31.5 · [6]:31.6 · [7]:31.8 · [8]:31.9 |
| yolo26l-obb.dxnn | 7 | [3]:21.9 · [4]:23.3 · [5]:23.2 · [6]:23.1 · **[7]:23.3 ★** · [8]:23.2 |
| yolo26x-obb.dxnn | 5 | [3]:12.7 · [4]:13.5 · **[5]:13.5 ★** · [6]:13.4 · [7]:13.4 · [8]:13.4 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-obb.dxnn | 74.7 ±0.2 | 4 | 55 | 91.7 | 100.0 | 60~61 | 1000 | ok |
| yolo26s-obb.dxnn | 43.7 ±0.0 | 8 | 38 | 91.6 | 100.0 | 61~63 | 1000 | ok |
| yolo26m-obb.dxnn | 32.0 ±0.0 | 7 | 27 | 91.7 | 100.0 | 64~68 | 1000 | ok |
| yolo26l-obb.dxnn | 23.4 ±0.0 | 4 | 20 | 88.0 | 100.0 | 64~67 | 1000 | ok |
| yolo26x-obb.dxnn | 13.6 ±0.0 | 5 | 12 | 85.3 | 100.0 | 66~70 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-obb.dxnn | 4 | [3]:56.7 · **[4]:74.5 ★** · [5]:74.4 · [6]:74.2 · [7]:74.2 · [8]:74.5 · [9]:74.1 · [10]:74.4 |
| yolo26s-obb.dxnn | 8 | [3]:37.6 · [4]:43.6 · [5]:43.0 · [6]:43.7 · [7]:43.7 · **[8]:43.8 ★** · [9]:43.7 · [10]:43.8 |
| yolo26m-obb.dxnn | 7 | [3]:28.0 · [4]:31.9 · [5]:31.6 · [6]:31.6 · **[7]:31.9 ★** · [8]:31.8 |
| yolo26l-obb.dxnn | 4 | [3]:21.2 · **[4]:23.4 ★** · [5]:23.3 · [6]:23.3 · [7]:23.2 · [8]:23.2 |
| yolo26x-obb.dxnn | 5 | [3]:12.7 · [4]:13.5 · **[5]:13.6 ★** · [6]:13.4 · [7]:13.4 · [8]:13.4 |


#### Classification

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-cls.dxnn | 3514.4 ±0.6 | 10 | 124 | 87.9 | 96.6 | 57~58 | 1000 | ok |
| yolo26s-cls.dxnn | 1898.3 ±1.8 | 8 | 59 | 89.2 | 97.2 | 58~60 | 1000 | ok |
| yolo26m-cls.dxnn | 1341.9 ±1.0 | 5 | 43 | 88.7 | 97.3 | 62~65 | 1000 | ok |
| yolo26l-cls.dxnn | 846.7 ±0.2 | 4 | 27 | 90.5 | 97.9 | 60~62 | 1000 | ok |
| yolo26x-cls.dxnn | 453.0 ±0.0 | 4 | 17 | 90.6 | 99.0 | 62~65 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-cls.dxnn | 10 | [3]:2199.4 · [4]:2945.2 · [5]:3423.9 · [6]:3507.8 · [7]:3518.9 · [8]:3523.3 · [9]:3524.1 · **[10]:3525.7 ★** |
| yolo26s-cls.dxnn | 8 | [3]:1473.4 · [4]:1859.3 · [5]:1873.5 · [6]:1896.4 · [7]:1904.4 · **[8]:1907.0 ★** · [9]:1902.3 · [10]:1900.3 |
| yolo26m-cls.dxnn | 5 | [3]:1090.1 · [4]:1330.6 · **[5]:1347.0 ★** · [6]:1340.9 · [7]:1342.6 · [8]:1344.2 |
| yolo26l-cls.dxnn | 4 | [3]:737.2 · **[4]:848.4 ★** · [5]:842.7 · [6]:844.1 · [7]:845.3 · [8]:843.2 |
| yolo26x-cls.dxnn | 4 | [3]:373.5 · **[4]:453.9 ★** · [5]:450.7 · [6]:448.7 · [7]:452.2 · [8]:451.5 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-cls.dxnn | 3514.0 ±0.6 | 9 | 119 | 88.3 | 96.3 | 56~58 | 1000 | ok |
| yolo26s-cls.dxnn | 1898.4 ±1.1 | 7 | 59 | 90.0 | 97.7 | 57~59 | 1000 | ok |
| yolo26m-cls.dxnn | 1342.4 ±0.9 | 5 | 43 | 90.7 | 97.9 | 62~65 | 1000 | ok |
| yolo26l-cls.dxnn | 846.1 ±0.7 | 4 | 27 | 90.5 | 98.6 | 60~62 | 1000 | ok |
| yolo26x-cls.dxnn | 452.9 ±0.3 | 4 | 17 | 90.8 | 99.6 | 62~65 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-cls.dxnn | 9 | [3]:2209.2 · [4]:2945.8 · [5]:3424.2 · [6]:3508.4 · [7]:3514.7 · [8]:3523.5 · **[9]:3524.7 ★** · [10]:3518.8 |
| yolo26s-cls.dxnn | 7 | [3]:1467.1 · [4]:1858.1 · [5]:1864.8 · [6]:1898.1 · **[7]:1905.2 ★** · [8]:1902.9 |
| yolo26m-cls.dxnn | 5 | [3]:1087.3 · [4]:1332.7 · **[5]:1345.2 ★** · [6]:1342.4 · [7]:1343.1 · [8]:1341.7 |
| yolo26l-cls.dxnn | 4 | [3]:739.0 · **[4]:848.6 ★** · [5]:843.1 · [6]:845.0 · [7]:844.9 · [8]:844.3 |
| yolo26x-cls.dxnn | 4 | [3]:370.7 · **[4]:453.4 ★** · [5]:450.8 · [6]:451.5 · [7]:451.1 · [8]:451.1 |


### Latency (Single-Core, Sync)

#### Object Detection

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n.dxnn | 45.7 ±0.6 | 21.90 | 20.68 | 1.21 | 43 | ok |
| yolo26s.dxnn | 31.4 ±0.1 | 31.80 | 30.47 | 1.32 | 53 | ok |
| yolo26m.dxnn | 25.5 ±0.3 | 39.27 | 37.91 | 1.36 | 54 | ok |
| yolo26l.dxnn | 21.3 ±0.2 | 46.90 | 45.55 | 1.35 | 54 | ok |
| yolo26x.dxnn | 13.3 ±0.1 | 74.94 | 73.54 | 1.39 | 55 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n.dxnn | 43.4 ±0.3 | 23.03 | 23.03 | N/A | 53 | ok |
| yolo26s.dxnn | 33.1 ±0.1 | 30.21 | 30.21 | N/A | 53 | ok |
| yolo26m.dxnn | 26.4 ±0.2 | 37.88 | 37.88 | N/A | 54 | ok |
| yolo26l.dxnn | 21.7 ±0.1 | 46.05 | 46.05 | N/A | 54 | ok |
| yolo26x.dxnn | 13.6 ±0.1 | 73.36 | 73.36 | N/A | 55 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-pose.dxnn | 46.0 ±0.0 | 21.74 | 20.74 | 1.01 | 53 | ok |
| yolo26s-pose.dxnn | 33.9 ±0.3 | 29.46 | 28.45 | 1.01 | 53 | ok |
| yolo26m-pose.dxnn | 27.1 ±0.2 | 36.92 | 35.93 | 0.99 | 54 | ok |
| yolo26l-pose.dxnn | 22.3 ±0.0 | 44.89 | 43.91 | 0.98 | 54 | ok |
| yolo26x-pose.dxnn | 13.7 ±0.0 | 72.79 | 71.77 | 1.03 | 55 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-pose.dxnn | 48.2 ±0.1 | 20.74 | 20.74 | N/A | 53 | ok |
| yolo26s-pose.dxnn | 35.2 ±0.2 | 28.43 | 28.43 | N/A | 53 | ok |
| yolo26m-pose.dxnn | 27.9 ±0.1 | 35.85 | 35.85 | N/A | 54 | ok |
| yolo26l-pose.dxnn | 22.7 ±0.0 | 44.03 | 44.03 | N/A | 54 | ok |
| yolo26x-pose.dxnn | 13.9 ±0.4 | 71.76 | 71.76 | N/A | 55 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-seg.dxnn | 26.3 ±0.5 | 38.06 | 36.84 | 1.21 | 53 | ok |
| yolo26s-seg.dxnn | 21.0 ±0.1 | 47.60 | 46.40 | 1.20 | 54 | ok |
| yolo26m-seg.dxnn | 16.3 ±0.1 | 61.20 | 59.97 | 1.24 | 54 | ok |
| yolo26l-seg.dxnn | 14.5 ±0.4 | 69.04 | 67.81 | 1.23 | 54 | ok |
| yolo26x-seg.dxnn | 9.3 ±0.6 | 108.06 | 106.82 | 1.24 | 55 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-seg.dxnn | 28.2 ±0.3 | 35.47 | 35.47 | N/A | 53 | ok |
| yolo26s-seg.dxnn | 22.0 ±0.1 | 45.37 | 45.37 | N/A | 53 | ok |
| yolo26m-seg.dxnn | 17.1 ±0.2 | 58.63 | 58.63 | N/A | 54 | ok |
| yolo26l-seg.dxnn | 14.9 ±0.1 | 67.24 | 67.24 | N/A | 54 | ok |
| yolo26x-seg.dxnn | 9.3 ±0.0 | 107.20 | 107.20 | N/A | 55 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-obb.dxnn | 26.8 ±0.2 | 37.28 | 36.17 | 1.11 | 53 | ok |
| yolo26s-obb.dxnn | 18.3 ±0.0 | 54.76 | 53.71 | 1.05 | 54 | ok |
| yolo26m-obb.dxnn | 13.8 ±0.0 | 72.54 | 71.48 | 1.06 | 55 | ok |
| yolo26l-obb.dxnn | 10.7 ±0.1 | 93.69 | 92.64 | 1.05 | 55 | ok |
| yolo26x-obb.dxnn | 6.0 ±0.0 | 166.05 | 164.98 | 1.07 | 56 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-obb.dxnn | 27.6 ±0.2 | 36.26 | 36.26 | N/A | 54 | ok |
| yolo26s-obb.dxnn | 18.8 ±0.0 | 53.18 | 53.18 | N/A | 54 | ok |
| yolo26m-obb.dxnn | 13.9 ±0.0 | 71.75 | 71.75 | N/A | 55 | ok |
| yolo26l-obb.dxnn | 10.8 ±0.0 | 92.32 | 92.32 | N/A | 55 | ok |
| yolo26x-obb.dxnn | 6.1 ±0.0 | 164.45 | 164.45 | N/A | 57 | ok |

#### Classification

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-cls.dxnn | 751.8 ±0.6 | 1.33 | 1.33 | N/A | 53 | ok |
| yolo26s-cls.dxnn | 501.2 ±1.9 | 2.00 | 2.00 | N/A | 53 | ok |
| yolo26m-cls.dxnn | 373.6 ±1.0 | 2.68 | 2.68 | N/A | 52 | ok |
| yolo26l-cls.dxnn | 230.0 ±0.2 | 4.35 | 4.35 | N/A | 53 | ok |
| yolo26x-cls.dxnn | 131.8 ±0.0 | 7.59 | 7.59 | N/A | 53 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-cls.dxnn | 752.5 ±0.6 | 1.33 | 1.33 | N/A | 52 | ok |
| yolo26s-cls.dxnn | 500.2 ±1.1 | 2.00 | 2.00 | N/A | 53 | ok |
| yolo26m-cls.dxnn | 371.6 ±0.9 | 2.69 | 2.69 | N/A | 53 | ok |
| yolo26l-cls.dxnn | 225.1 ±0.7 | 4.44 | 4.44 | N/A | 53 | ok |
| yolo26x-cls.dxnn | 133.7 ±0.3 | 7.48 | 7.48 | N/A | 53 | ok |

## E2E Pipeline (Single-Stream)

### Object Detection

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | vah264dec | 3455 | 3 | 175.3 ±0.7 | 19.71 | 283 | 54.0 | 83.5 | 55~56 | 1000 | 204 | ok |
| yolo26s.dxnn | vah264dec | 3455 | 3 | 131.3 ±0.1 | 26.32 | 235 | 89.1 | 100.0 | 57~59 | 1000 | 219 | ok |
| yolo26m.dxnn | vah264dec | 3455 | 3 | 91.2 ±0.3 | 37.87 | 156 | 89.9 | 100.0 | 61~66 | 1000 | 240 | ok |
| yolo26l.dxnn | vah264dec | 3455 | 3 | 66.6 ±0.1 | 51.85 | 132 | 91.7 | 100.0 | 62~68 | 1000 | 249 | ok |
| yolo26x.dxnn | vah264dec | 3455 | 3 | 38.8 ±0.3 | 88.95 | 79 | 96.0 | 100.0 | 69~78 | 1000 | 315 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | vah264dec | 3455 | 3 | 191.5 ±0.7 | 18.04 | 300 | 58.6 | 83.4 | 55~56 | 1000 | 205 | ok |
| yolo26s.dxnn | vah264dec | 3455 | 3 | 131.0 ±0.2 | 26.37 | 233 | 89.8 | 100.0 | 57~60 | 1000 | 229 | ok |
| yolo26m.dxnn | vah264dec | 3455 | 3 | 90.8 ±0.2 | 38.07 | 167 | 91.1 | 100.0 | 61~66 | 1000 | 244 | ok |
| yolo26l.dxnn | vah264dec | 3455 | 3 | 66.5 ±0.0 | 51.92 | 138 | 91.2 | 100.0 | 62~69 | 1000 | 254 | ok |
| yolo26x.dxnn | vah264dec | 3455 | 3 | 38.6 ±0.1 | 89.50 | 86 | 94.9 | 100.0 | 69~78 | 1000 | 316 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n.dxnn | 175.3 | 191.5 | -16.2 | -8.5% |
| yolo26s.dxnn | 131.3 | 131.0 | +0.3 | +0.2% |
| yolo26m.dxnn | 91.2 | 90.8 | +0.5 | +0.5% |
| yolo26l.dxnn | 66.6 | 66.5 | +0.1 | +0.2% |
| yolo26x.dxnn | 38.8 | 38.6 | +0.2 | +0.6% |

### Pose Estimation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | vah264dec | 3455 | 3 | 183.1 ±0.9 | 18.87 | 251 | 62.5 | 86.8 | 55~56 | 1000 | 182 | ok |
| yolo26s-pose.dxnn | vah264dec | 3455 | 3 | 126.2 ±0.2 | 27.38 | 159 | 90.5 | 100.0 | 57~60 | 1000 | 211 | ok |
| yolo26m-pose.dxnn | vah264dec | 3455 | 3 | 87.7 ±0.2 | 39.38 | 131 | 93.4 | 100.0 | 61~67 | 1000 | 232 | ok |
| yolo26l-pose.dxnn | vah264dec | 3455 | 3 | 64.8 ±0.0 | 53.29 | 110 | 94.2 | 100.0 | 62~69 | 1000 | 243 | ok |
| yolo26x-pose.dxnn | vah264dec | 3455 | 3 | 38.2 ±0.3 | 90.43 | 63 | 95.0 | 100.0 | 69~78 | 1000 | 326 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | vah264dec | 3455 | 3 | 211.0 ±0.2 | 16.38 | 205 | 79.2 | 98.6 | 55~57 | 1000 | 176 | ok |
| yolo26s-pose.dxnn | vah264dec | 3455 | 3 | 126.4 ±0.2 | 27.33 | 131 | 90.7 | 100.0 | 57~60 | 1000 | 196 | ok |
| yolo26m-pose.dxnn | vah264dec | 3455 | 3 | 87.7 ±0.2 | 39.39 | 109 | 93.0 | 100.0 | 61~66 | 1000 | 218 | ok |
| yolo26l-pose.dxnn | vah264dec | 3455 | 3 | 65.1 ±0.2 | 53.10 | 89 | 93.8 | 100.0 | 63~69 | 1000 | 228 | ok |
| yolo26x-pose.dxnn | vah264dec | 3455 | 3 | 38.1 ±0.4 | 90.73 | 51 | 94.2 | 100.0 | 69~78 | 1000 | 326 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-pose.dxnn | 183.1 | 211.0 | -27.9 | -13.2% |
| yolo26s-pose.dxnn | 126.2 | 126.4 | -0.2 | -0.2% |
| yolo26m-pose.dxnn | 87.7 | 87.7 | +0.0 | +0.0% |
| yolo26l-pose.dxnn | 64.8 | 65.1 | -0.2 | -0.3% |
| yolo26x-pose.dxnn | 38.2 | 38.1 | +0.1 | +0.3% |

### Segmentation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | vah264dec | 3455 | 3 | 107.6 ±0.7 | 32.12 | 349 | 38.0 | 71.3 | 55~57 | 1000 | 310 | ok |
| yolo26s-seg.dxnn | vah264dec | 3455 | 3 | 95.8 ±0.3 | 36.05 | 285 | 78.5 | 92.3 | 58~62 | 1000 | 322 | ok |
| yolo26m-seg.dxnn | vah264dec | 3455 | 3 | 66.0 ±0.1 | 52.35 | 188 | 93.6 | 100.0 | 66~74 | 1000 | 338 | ok |
| yolo26l-seg.dxnn | vah264dec | 3455 | 3 | 52.0 ±0.1 | 66.42 | 160 | 94.3 | 100.0 | 67~76 | 1000 | 351 | ok |
| yolo26x-seg.dxnn | vah264dec | 3455 | 3 | 25.9 ±3.5 | 133.40 | 93 | 94.3 | 100.0 | 76~84 | 600~1000 | 421 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | vah264dec | 3455 | 3 | 117.7 ±1.0 | 29.35 | 358 | 47.0 | 75.1 | 55~57 | 1000 | 340 | ok |
| yolo26s-seg.dxnn | vah264dec | 3455 | 3 | 99.7 ±0.1 | 34.67 | 281 | 87.1 | 100.0 | 59~63 | 1000 | 341 | ok |
| yolo26m-seg.dxnn | vah264dec | 3455 | 3 | 65.4 ±0.3 | 52.80 | 197 | 94.3 | 100.0 | 65~74 | 1000 | 350 | ok |
| yolo26l-seg.dxnn | vah264dec | 3455 | 3 | 51.6 ±0.2 | 66.89 | 164 | 95.1 | 100.0 | 67~76 | 1000 | 360 | ok |
| yolo26x-seg.dxnn | vah264dec | 3455 | 3 | 25.6 ±3.8 | 135.24 | 87 | 94.7 | 100.0 | 76~83 | 400~1000 | 433 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-seg.dxnn | 107.6 | 117.7 | -10.1 | -8.6% |
| yolo26s-seg.dxnn | 95.8 | 99.7 | -3.8 | -3.8% |
| yolo26m-seg.dxnn | 66.0 | 65.4 | +0.6 | +0.9% |
| yolo26l-seg.dxnn | 52.0 | 51.6 | +0.4 | +0.7% |
| yolo26x-seg.dxnn | 25.9 | 25.6 | +0.3 | +1.4% |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | vah264dec | 2640 | 3 | 74.3 ±0.1 | 35.54 | 116 | 92.5 | 100.0 | 57~60 | 1000 | 230 | ok |
| yolo26s-obb.dxnn | vah264dec | 2640 | 3 | 43.7 ±0.0 | 60.43 | 82 | 94.2 | 100.0 | 60~65 | 1000 | 241 | ok |
| yolo26m-obb.dxnn | vah264dec | 2640 | 3 | 32.0 ±0.1 | 82.52 | 62 | 94.6 | 100.0 | 66~74 | 1000 | 266 | ok |
| yolo26l-obb.dxnn | vah264dec | 2640 | 3 | 23.4 ±0.1 | 112.69 | 45 | 95.7 | 100.0 | 69~77 | 1000 | 274 | ok |
| yolo26x-obb.dxnn | vah264dec | 2640 | 3 | 12.7 ±0.8 | 207.39 | 25 | 94.3 | 100.0 | 78~84 | 800~1000 | 344 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | vah264dec | 2640 | 3 | 74.2 ±0.0 | 35.58 | 121 | 92.1 | 100.0 | 57~60 | 1000 | 211 | ok |
| yolo26s-obb.dxnn | vah264dec | 2640 | 3 | 43.7 ±0.0 | 60.39 | 85 | 93.8 | 100.0 | 60~65 | 1000 | 228 | ok |
| yolo26m-obb.dxnn | vah264dec | 2640 | 3 | 31.9 ±0.0 | 82.67 | 63 | 94.4 | 100.0 | 66~74 | 1000 | 262 | ok |
| yolo26l-obb.dxnn | vah264dec | 2640 | 3 | 23.4 ±0.0 | 112.60 | 46 | 95.5 | 100.0 | 69~77 | 1000 | 265 | ok |
| yolo26x-obb.dxnn | vah264dec | 2640 | 3 | 12.7 ±0.9 | 207.67 | 24 | 94.1 | 100.0 | 78~84 | 600~1000 | 335 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-obb.dxnn | 74.3 | 74.2 | +0.1 | +0.1% |
| yolo26s-obb.dxnn | 43.7 | 43.7 | -0.0 | -0.1% |
| yolo26m-obb.dxnn | 32.0 | 31.9 | +0.1 | +0.2% |
| yolo26l-obb.dxnn | 23.4 | 23.4 | -0.0 | -0.1% |
| yolo26x-obb.dxnn | 12.7 | 12.7 | +0.0 | +0.2% |

### Classification

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-cls.dxnn | vah264dec | 3455 | 3 | 283.9 ±0.6 | 12.17 | 85 | 5.9 | 22.6 | 53 | 1000 | 82 | ok |
| yolo26s-cls.dxnn | vah264dec | 3455 | 3 | 293.2 ±1.3 | 11.78 | 83 | 11.6 | 42.7 | 53 | 1000 | 94 | ok |
| yolo26m-cls.dxnn | vah264dec | 3455 | 3 | 293.0 ±1.1 | 11.79 | 82 | 15.9 | 53.2 | 53~54 | 1000 | 122 | ok |
| yolo26l-cls.dxnn | vah264dec | 3455 | 3 | 294.1 ±0.2 | 11.75 | 82 | 25.2 | 77.2 | 53~54 | 1000 | 112 | ok |
| yolo26x-cls.dxnn | vah264dec | 3455 | 3 | 292.1 ±0.5 | 11.83 | 82 | 45.2 | 80.9 | 55 | 1000 | 180 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-cls.dxnn | vah264dec | 3455 | 3 | 284.9 ±0.5 | 12.13 | 85 | 6.0 | 22.7 | 52~53 | 1000 | 82 | ok |
| yolo26s-cls.dxnn | vah264dec | 3455 | 3 | 293.3 ±1.1 | 11.78 | 82 | 11.8 | 42.6 | 53 | 1000 | 91 | ok |
| yolo26m-cls.dxnn | vah264dec | 3455 | 3 | 292.4 ±0.6 | 11.82 | 82 | 15.4 | 54.7 | 53~54 | 1000 | 104 | ok |
| yolo26l-cls.dxnn | vah264dec | 3455 | 3 | 292.9 ±1.1 | 11.79 | 82 | 25.3 | 76.5 | 53~54 | 1000 | 109 | ok |
| yolo26x-cls.dxnn | vah264dec | 3455 | 3 | 291.7 ±1.4 | 11.85 | 83 | 44.3 | 80.2 | 55 | 1000 | 180 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-cls.dxnn | 283.9 | 284.9 | -0.9 | -0.3% |
| yolo26s-cls.dxnn | 293.2 | 293.3 | -0.1 | -0.0% |
| yolo26m-cls.dxnn | 293.0 | 292.4 | +0.6 | +0.2% |
| yolo26l-cls.dxnn | 294.1 | 292.9 | +1.1 | +0.4% |
| yolo26x-cls.dxnn | 292.1 | 291.7 | +0.4 | +0.1% |

## E2E Pipeline (Multi-Stream)

### Object Detection

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | 5 | 3 | 180.9 ±0.4 | 36.2 | 312 | 61.5 | 81.2 | 62~66 | 1000 | 410 | ok |
| yolo26n.dxnn | 6 | 3 | 173.8 ±4.8 | 29.0 | 306 | 58.7 | 80.8 | 69~71 | 1000 | 456 | ok |
| yolo26s.dxnn | 4 | 3 | 131.6 ±0.2 | 32.9 | 231 | 95.8 | 100.0 | 68~74 | 1000 | 380 | ok |
| yolo26s.dxnn | 5 | 3 | 127.5 ±4.1 | 25.5 | 216 | 96.6 | 100.0 | 78~79 | 1000 | 410 | ok |
| yolo26m.dxnn | 3 | 3 | 86.7 ±4.5 | 28.9 | 159 | 96.4 | 100.0 | 78~83 | 800~1000 | 356 | ok |
| yolo26m.dxnn | 2 | 3 | 77.1 ±1.5 | 38.5 | 152 | 94.8 | 100.0 | 84 | 600~1000 | 314 | ok |
| yolo26l.dxnn | 2 | 3 | 64.1 ±2.6 | 32.1 | 137 | 96.0 | 100.0 | 77~81 | 1000 | 325 | ok |
| yolo26l.dxnn | 3 | 3 | 58.5 ±0.4 | 19.5 | 127 | 95.9 | 100.0 | 84 | 600~1000 | 365 | ok |
| yolo26x.dxnn | 1 | 3 | 38.8 ±0.3 | 38.8 | 79 | 96.0 | 100.0 | 69~78 | 1000 | 315 | ok |
| yolo26x.dxnn | 2 | 3 | 30.6 ±0.7 | 15.3 | 69 | 96.0 | 100.0 | 84 | 600~1000 | 385 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | 6 | 3 | 196.1 ±1.0 | 32.7 | 348 | 72.8 | 89.0 | 63~68 | 1000 | 501 | ok |
| yolo26n.dxnn | 7 | 3 | 194.9 ±1.2 | 27.9 | 348 | 73.0 | 88.2 | 71~74 | 1000 | 530 | ok |
| yolo26s.dxnn | 4 | 3 | 131.2 ±0.2 | 32.8 | 235 | 96.4 | 100.0 | 69~74 | 1000 | 392 | ok |
| yolo26s.dxnn | 5 | 3 | 126.2 ±4.3 | 25.2 | 226 | 96.9 | 100.0 | 78~80 | 1000 | 441 | ok |
| yolo26m.dxnn | 3 | 3 | 86.2 ±4.1 | 28.7 | 170 | 96.4 | 100.0 | 78~83 | 800~1000 | 358 | ok |
| yolo26m.dxnn | 2 | 3 | 75.9 ±0.7 | 37.9 | 157 | 94.9 | 100.0 | 84 | 600~1000 | 319 | ok |
| yolo26l.dxnn | 2 | 3 | 63.9 ±2.6 | 31.9 | 141 | 96.5 | 100.0 | 78~82 | 1000 | 328 | ok |
| yolo26l.dxnn | 3 | 3 | 57.7 ±0.7 | 19.2 | 131 | 96.4 | 100.0 | 84 | 600~1000 | 371 | ok |
| yolo26x.dxnn | 1 | 3 | 38.6 ±0.1 | 38.6 | 86 | 94.9 | 100.0 | 69~78 | 1000 | 316 | ok |
| yolo26x.dxnn | 2 | 3 | 31.1 ±0.7 | 15.5 | 75 | 96.5 | 100.0 | 84 | 600~1000 | 392 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n.dxnn | 5 | 36.2 | 6 | 32.7 |
| yolo26s.dxnn | 4 | 32.9 | 4 | 32.8 |
| yolo26m.dxnn | 2 | 38.5 | 2 | 37.9 |
| yolo26l.dxnn | 2 | 32.1 | 2 | 31.9 |
| yolo26x.dxnn | 1 | 38.8 | 1 | 38.6 |

### Pose Estimation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | 6 | 3 | 209.4 ±0.8 | 34.9 | 282 | 88.0 | 96.4 | 64~70 | 1000 | 443 | ok |
| yolo26n-pose.dxnn | 7 | 3 | 209.1 ±0.5 | 29.9 | 283 | 87.5 | 96.0 | 74~76 | 1000 | 491 | ok |
| yolo26s-pose.dxnn | 4 | 3 | 126.5 ±0.1 | 31.6 | 183 | 96.8 | 100.0 | 69~74 | 1000 | 374 | ok |
| yolo26s-pose.dxnn | 5 | 3 | 123.1 ±3.5 | 24.6 | 180 | 96.8 | 100.0 | 78~79 | 1000 | 411 | ok |
| yolo26m-pose.dxnn | 2 | 3 | 86.4 ±2.4 | 43.2 | 146 | 96.1 | 100.0 | 75~80 | 1000 | 307 | ok |
| yolo26m-pose.dxnn | 3 | 3 | 75.5 ±2.1 | 25.2 | 131 | 96.1 | 100.0 | 84 | 600~1000 | 351 | ok |
| yolo26l-pose.dxnn | 2 | 3 | 62.6 ±2.4 | 31.3 | 114 | 96.4 | 100.0 | 77~82 | 1000 | 317 | ok |
| yolo26l-pose.dxnn | 3 | 3 | 57.3 ±0.4 | 19.1 | 108 | 96.6 | 100.0 | 84 | 800~1000 | 361 | ok |
| yolo26x-pose.dxnn | 1 | 3 | 38.2 ±0.3 | 38.2 | 63 | 95.0 | 100.0 | 69~78 | 1000 | 326 | ok |
| yolo26x-pose.dxnn | 2 | 3 | 30.7 ±1.2 | 15.4 | 58 | 96.4 | 100.0 | 84 | 600~1000 | 382 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | 7 | 3 | 216.5 ±0.1 | 30.9 | 257 | 94.6 | 99.7 | 65~71 | 1000 | 480 | ok |
| yolo26n-pose.dxnn | 8 | 3 | 216.6 ±0.1 | 27.1 | 257 | 94.8 | 99.3 | 74~76 | 1000 | 513 | ok |
| yolo26s-pose.dxnn | 4 | 3 | 126.4 ±0.1 | 31.6 | 163 | 96.6 | 100.0 | 68~73 | 1000 | 370 | ok |
| yolo26s-pose.dxnn | 5 | 3 | 126.0 ±0.9 | 25.2 | 164 | 97.3 | 100.0 | 77~78 | 1000 | 402 | ok |
| yolo26m-pose.dxnn | 2 | 3 | 86.9 ±1.9 | 43.4 | 124 | 95.6 | 100.0 | 75~80 | 1000 | 295 | ok |
| yolo26m-pose.dxnn | 3 | 3 | 76.7 ±2.4 | 25.6 | 113 | 96.4 | 100.0 | 84 | 600~1000 | 341 | ok |
| yolo26l-pose.dxnn | 2 | 3 | 62.6 ±2.4 | 31.3 | 98 | 96.2 | 100.0 | 77~81 | 1000 | 306 | ok |
| yolo26l-pose.dxnn | 3 | 3 | 57.4 ±0.7 | 19.1 | 90 | 96.3 | 100.0 | 84 | 800~1000 | 350 | ok |
| yolo26x-pose.dxnn | 1 | 3 | 38.1 ±0.4 | 38.1 | 51 | 94.2 | 100.0 | 69~78 | 1000 | 326 | ok |
| yolo26x-pose.dxnn | 2 | 3 | 30.7 ±0.8 | 15.3 | 46 | 96.6 | 100.0 | 84 | 400~1000 | 370 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-pose.dxnn | 6 | 34.9 | 7 | 30.9 |
| yolo26s-pose.dxnn | 4 | 31.6 | 4 | 31.6 |
| yolo26m-pose.dxnn | 2 | 43.2 | 2 | 43.4 |
| yolo26l-pose.dxnn | 2 | 31.3 | 2 | 31.3 |
| yolo26x-pose.dxnn | 1 | 38.2 | 1 | 38.1 |

### Segmentation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | 3 | 3 | 105.2 ±0.3 | 35.0 | 351 | 39.4 | 72.6 | 62~65 | 1000 | 447 | ok |
| yolo26n-seg.dxnn | 4 | 3 | 104.6 ±0.2 | 26.1 | 351 | 39.4 | 71.6 | 68~69 | 1000 | 496 | ok |
| yolo26s-seg.dxnn | 3 | 3 | 95.5 ±0.1 | 31.8 | 287 | 82.8 | 91.1 | 72~77 | 1000 | 453 | ok |
| yolo26s-seg.dxnn | 4 | 3 | 91.1 ±0.1 | 22.8 | 271 | 90.4 | 98.4 | 82~84 | 1000 | 496 | ok |
| yolo26m-seg.dxnn | 2 | 3 | 48.5 ±5.0 | 24.2 | 167 | 95.9 | 100.0 | 84 | 400~1000 | 427 | ok |
| yolo26m-seg.dxnn | 1 | 3 | 66.0 ±0.1 | 66.0 | 188 | 93.6 | 100.0 | 66~74 | 1000 | 338 | ok |
| yolo26l-seg.dxnn | 1 | 3 | 52.0 ±0.1 | 52.0 | 160 | 94.3 | 100.0 | 67~76 | 1000 | 351 | ok |
| yolo26l-seg.dxnn | 2 | 3 | 39.9 ±2.8 | 19.9 | 145 | 95.7 | 100.0 | 84 | 400~1000 | 437 | ok |
| yolo26x-seg.dxnn | 1 | 3 | 25.9 ±3.5 | 25.9 | 93 | 94.3 | 100.0 | 76~84 | 600~1000 | 421 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | 3 | 3 | 115.5 ±0.4 | 38.5 | 368 | 47.4 | 74.5 | 62~66 | 1000 | 499 | ok |
| yolo26n-seg.dxnn | 4 | 3 | 114.8 ±0.2 | 28.7 | 368 | 47.8 | 73.0 | 69~70 | 1000 | 546 | ok |
| yolo26s-seg.dxnn | 3 | 3 | 100.4 ±0.3 | 33.5 | 286 | 92.2 | 100.0 | 72~78 | 1000 | 486 | ok |
| yolo26s-seg.dxnn | 4 | 3 | 93.3 ±0.1 | 23.3 | 266 | 94.8 | 100.0 | 82~84 | 1000 | 530 | ok |
| yolo26m-seg.dxnn | 2 | 3 | 47.9 ±5.8 | 23.9 | 161 | 95.1 | 100.0 | 84 | 400~1000 | 442 | ok |
| yolo26m-seg.dxnn | 1 | 3 | 65.4 ±0.3 | 65.4 | 197 | 94.3 | 100.0 | 65~74 | 1000 | 350 | ok |
| yolo26l-seg.dxnn | 1 | 3 | 51.6 ±0.2 | 51.6 | 164 | 95.1 | 100.0 | 67~76 | 1000 | 360 | ok |
| yolo26l-seg.dxnn | 2 | 3 | 39.8 ±2.4 | 19.9 | 142 | 95.6 | 100.0 | 84 | 400~1000 | 445 | ok |
| yolo26x-seg.dxnn | 1 | 3 | 25.6 ±3.8 | 25.6 | 87 | 94.7 | 100.0 | 76~83 | 400~1000 | 433 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-seg.dxnn | 3 | 35.0 | 3 | 38.5 |
| yolo26s-seg.dxnn | 3 | 31.8 | 3 | 33.5 |
| yolo26m-seg.dxnn | 1 | 66.0 | 1 | 65.4 |
| yolo26l-seg.dxnn | 1 | 52.0 | 1 | 51.6 |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | 2 | 3 | 74.3 ±0.0 | 37.1 | 153 | 94.8 | 100.0 | 64~67 | 1000 | 300 | ok |
| yolo26n-obb.dxnn | 3 | 3 | 74.4 ±0.1 | 24.8 | 153 | 96.3 | 100.0 | 70~72 | 1000 | 348 | ok |
| yolo26s-obb.dxnn | 1 | 3 | 43.7 ±0.0 | 43.7 | 82 | 94.2 | 100.0 | 60~65 | 1000 | 241 | ok |
| yolo26s-obb.dxnn | 2 | 3 | 43.8 ±0.0 | 21.9 | 95 | 96.2 | 100.0 | 71~74 | 1000 | 316 | ok |
| yolo26m-obb.dxnn | 1 | 3 | 32.0 ±0.1 | 32.0 | 62 | 94.6 | 100.0 | 66~74 | 1000 | 266 | ok |
| yolo26m-obb.dxnn | 2 | 3 | 28.6 ±0.5 | 14.3 | 61 | 95.3 | 100.0 | 82~84 | 600~1000 | 339 | ok |
| yolo26l-obb.dxnn | 1 | 3 | 23.4 ±0.1 | 23.4 | 45 | 95.7 | 100.0 | 69~77 | 1000 | 274 | ok |
| yolo26x-obb.dxnn | 1 | 3 | 12.7 ±0.8 | 12.7 | 25 | 94.3 | 100.0 | 78~84 | 800~1000 | 344 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | 2 | 3 | 74.3 ±0.1 | 37.1 | 152 | 95.7 | 100.0 | 64~67 | 1000 | 297 | ok |
| yolo26n-obb.dxnn | 3 | 3 | 74.5 ±0.0 | 24.8 | 153 | 96.0 | 100.0 | 70~72 | 1000 | 338 | ok |
| yolo26s-obb.dxnn | 1 | 3 | 43.7 ±0.0 | 43.7 | 85 | 93.8 | 100.0 | 60~65 | 1000 | 228 | ok |
| yolo26s-obb.dxnn | 2 | 3 | 43.8 ±0.1 | 21.9 | 96 | 96.1 | 100.0 | 71~74 | 1000 | 309 | ok |
| yolo26m-obb.dxnn | 1 | 3 | 31.9 ±0.0 | 31.9 | 63 | 94.4 | 100.0 | 66~74 | 1000 | 262 | ok |
| yolo26m-obb.dxnn | 2 | 3 | 28.5 ±0.6 | 14.2 | 61 | 95.8 | 100.0 | 82~84 | 800~1000 | 335 | ok |
| yolo26l-obb.dxnn | 1 | 3 | 23.4 ±0.0 | 23.4 | 46 | 95.5 | 100.0 | 69~77 | 1000 | 265 | ok |
| yolo26x-obb.dxnn | 1 | 3 | 12.7 ±0.9 | 12.7 | 24 | 94.1 | 100.0 | 78~84 | 600~1000 | 335 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-obb.dxnn | 2 | 37.1 | 2 | 37.1 |
| yolo26s-obb.dxnn | 1 | 43.7 | 1 | 43.7 |
| yolo26m-obb.dxnn | 1 | 32.0 | 1 | 31.9 |

---
*Report generated by dx-benchmark tool*
