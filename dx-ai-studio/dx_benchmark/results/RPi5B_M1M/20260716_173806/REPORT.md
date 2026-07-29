# YOLO26 Benchmark Report

**Generated:** 2026-07-21 20:13:36 (Local)

## Test Timing

| # | Type | Start | End | Duration |
|---|------|-------|-----|----------|
| 1 | run | 2026-07-16 17:38:06 | 2026-07-17 13:48:37 | 20h 10m 31s |

## Executive Summary

### Object Detection

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n.dxnn | ON | 27.74 | 107.7 | 69.6 | 2 |
| yolo26n.dxnn | OFF | 23.88 | 165.9 | 87.4 | 2 |
| yolo26s.dxnn | ON | 35.10 | 94.1 | 69.8 | 2 |
| yolo26s.dxnn | OFF | 34.00 | 93.9 | 88.4 | 2 |
| yolo26m.dxnn | ON | 43.86 | 55.1 | 56.1 | 1 |
| yolo26m.dxnn | OFF | 40.58 | 55.7 | 53.8 | 1 |
| yolo26l.dxnn | ON | 54.27 | 42.2 | 38.0 | 1 |
| yolo26l.dxnn | OFF | 51.08 | 41.8 | 37.0 | 1 |
| yolo26x.dxnn | ON | 85.99 | 20.3 | 16.6 | — |
| yolo26x.dxnn | OFF | 83.03 | 20.5 | 17.4 | — |

### Pose Estimation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-pose.dxnn | ON | 23.48 | 160.4 | 85.7 | 2 |
| yolo26n-pose.dxnn | OFF | 20.61 | 160.5 | 127.2 | 4 |
| yolo26s-pose.dxnn | ON | 32.42 | 91.3 | 85.0 | 2 |
| yolo26s-pose.dxnn | OFF | 29.71 | 91.5 | 89.0 | 2 |
| yolo26m-pose.dxnn | ON | 40.25 | 50.1 | 49.9 | 1 |
| yolo26m-pose.dxnn | OFF | 39.20 | 52.9 | 48.1 | 1 |
| yolo26l-pose.dxnn | ON | 49.96 | 39.4 | 34.0 | 1 |
| yolo26l-pose.dxnn | OFF | 48.76 | 40.8 | 34.2 | 1 |
| yolo26x-pose.dxnn | ON | 82.68 | 19.5 | 16.8 | — |
| yolo26x-pose.dxnn | OFF | 80.95 | 19.7 | 16.6 | — |

### Segmentation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-seg.dxnn | ON | 42.56 | 69.8 | 48.5 | 1 |
| yolo26n-seg.dxnn | OFF | 38.77 | 95.7 | 63.9 | 2 |
| yolo26s-seg.dxnn | ON | 56.64 | 70.0 | 47.6 | 1 |
| yolo26s-seg.dxnn | OFF | 49.64 | 71.1 | 63.2 | 1 |
| yolo26m-seg.dxnn | ON | 69.18 | 32.1 | 28.8 | — |
| yolo26m-seg.dxnn | OFF | 64.89 | 31.8 | 29.6 | — |
| yolo26l-seg.dxnn | ON | 79.44 | 26.7 | 22.2 | — |
| yolo26l-seg.dxnn | OFF | 75.49 | 27.1 | 22.7 | — |
| yolo26x-seg.dxnn | ON | 127.90 | 13.7 | 11.3 | — |
| yolo26x-seg.dxnn | OFF | 121.10 | 13.9 | 11.2 | — |

### Oriented BBox (OBB)

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-obb.dxnn | ON | 43.73 | 52.8 | 52.2 | 1 |
| yolo26n-obb.dxnn | OFF | 42.37 | 52.5 | 52.1 | 1 |
| yolo26s-obb.dxnn | ON | 66.22 | 30.6 | 30.2 | 1 |
| yolo26s-obb.dxnn | OFF | 64.49 | 30.5 | 29.2 | — |
| yolo26m-obb.dxnn | ON | 86.54 | 19.1 | 17.2 | — |
| yolo26m-obb.dxnn | OFF | 84.75 | 19.2 | 15.4 | — |
| yolo26l-obb.dxnn | ON | 113.51 | 13.9 | 11.1 | — |
| yolo26l-obb.dxnn | OFF | 111.80 | 13.6 | 12.2 | — |
| yolo26x-obb.dxnn | ON | 199.12 | 7.3 | 6.2 | — |
| yolo26x-obb.dxnn | OFF | 196.35 | 7.5 | 6.2 | — |

### Classification

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-cls.dxnn | ON | 1.40 | 3027.9 | 194.0 | — |
| yolo26n-cls.dxnn | OFF | 1.37 | 3028.2 | 194.9 | — |
| yolo26s-cls.dxnn | ON | 2.18 | 1566.8 | 194.3 | — |
| yolo26s-cls.dxnn | OFF | 2.17 | 1566.8 | 194.9 | — |
| yolo26m-cls.dxnn | ON | 2.88 | 1009.2 | 194.4 | — |
| yolo26m-cls.dxnn | OFF | 2.89 | 1005.9 | 193.9 | — |
| yolo26l-cls.dxnn | ON | 4.24 | 696.2 | 194.1 | — |
| yolo26l-cls.dxnn | OFF | 4.28 | 695.8 | 193.8 | — |
| yolo26x-cls.dxnn | ON | 7.46 | 322.6 | 194.2 | — |
| yolo26x-cls.dxnn | OFF | 7.41 | 324.2 | 193.6 | — |

## Environment

| Item | Value |
|------|-------|
| Product | RPi5B |
| Hostname | raspberrypi |
| OS | Debian GNU/Linux 12 (bookworm) |
| Kernel | 6.12.93+rpt-rpi-2712 |
| CPU | Cortex-A76 |
| CPU Cores | 4 |
| RAM | 7.9 GB |
| NPU SKU | M1M |
| DX-AllSuite | v2.3.3 |
| NPU RT | v3.3.2 |
| NPU Driver (RT) | v2.4.1 |
| NPU Driver (PCIe) | v2.2.0 |
| NPU Firmware | v2.5.6 |
| NPU Memory | LPDDR4 4200 Mbps, 1.92GiB |
| NPU Board | M.2, Rev 0.0 |
| NPU PCIe | Gen3 X1 [01:00:00] |

### Tools

| Tool | Available | Version |
|------|-----------|---------|
| run_model | Yes | DXRT v3.3.2 run_model |
| gst-launch-1.0 | Yes | gst-launch-1.0 version 1.22.0 |
| gst-inspect-1.0 | Yes | gst-inspect-1.0 version 1.22.0 |
| dxtop | Yes | DX-TOP 1.1.0 |
| ffprobe | Yes | ffprobe version 5.1.9-0+deb12u1+rpt1 Copyright (c) 2007-2026... |

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
| yolo26n.dxnn | 107.7 ±1.1 | 7 | 189 | 39.2 | 69.9 | 61~64 | 1000 | ok |
| yolo26s.dxnn | 94.1 ±0.4 | 6 | 140 | 91.6 | 100.0 | 76~79 | 1000 | ok |
| yolo26m.dxnn | 55.1 ±6.1 | 5 | 73 | 89.1 | 100.0 | 84~86 | 300~1000 | ok |
| yolo26l.dxnn | 42.2 ±3.6 | 4 | 58 | 87.2 | 100.0 | 83~86 | 400~1000 | ok |
| yolo26x.dxnn | 20.3 ±1.1 | 4 | 29 | 83.0 | 100.0 | 84~86 | 300~800 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n.dxnn | 7 | [3]:86.7 · [4]:105.7 · [5]:107.9 · [6]:106.8 · **[7]:109.1 ★** · [8]:106.5 |
| yolo26s.dxnn | 6 | [3]:67.0 · [4]:82.6 · [5]:92.2 · **[6]:93.0 ★** · [7]:91.7 · [8]:91.5 |
| yolo26m.dxnn | 5 | [3]:50.5 · [4]:61.2 · **[5]:62.9 ★** · [6]:62.4 · [7]:61.9 · [8]:62.2 |
| yolo26l.dxnn | 4 | [3]:40.5 · **[4]:46.8 ★** · [5]:45.8 · [6]:46.0 · [7]:46.0 · [8]:46.3 |
| yolo26x.dxnn | 4 | [3]:25.6 · **[4]:27.8 ★** · [5]:26.9 · [6]:27.6 · [7]:27.4 · [8]:27.5 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n.dxnn | 165.9 ±0.2 | 7 | 104 | 91.3 | 100.0 | 73~77 | 1000 | ok |
| yolo26s.dxnn | 93.9 ±0.4 | 5 | 58 | 91.6 | 100.0 | 75~80 | 1000 | ok |
| yolo26m.dxnn | 55.7 ±5.5 | 4 | 36 | 86.3 | 100.0 | 84~85 | 400~1000 | ok |
| yolo26l.dxnn | 41.8 ±4.6 | 4 | 26 | 88.3 | 100.0 | 84~86 | 300~1000 | ok |
| yolo26x.dxnn | 20.5 ±0.9 | 5 | 15 | 87.5 | 100.0 | 85~86 | 300~800 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n.dxnn | 7 | [3]:100.6 · [4]:118.0 · [5]:148.7 · [6]:161.3 · **[7]:165.3 ★** · [8]:162.9 |
| yolo26s.dxnn | 5 | [3]:67.6 · [4]:88.2 · **[5]:92.3 ★** · [6]:92.2 · [7]:91.5 · [8]:91.3 |
| yolo26m.dxnn | 4 | [3]:50.0 · **[4]:63.0 ★** · [5]:62.8 · [6]:62.3 · [7]:62.3 · [8]:62.8 |
| yolo26l.dxnn | 4 | [3]:39.6 · **[4]:47.0 ★** · [5]:45.7 · [6]:46.1 · [7]:46.2 · [8]:46.7 |
| yolo26x.dxnn | 5 | [3]:25.2 · [4]:28.0 · **[5]:28.0 ★** · [6]:28.0 · [7]:27.5 · [8]:27.4 |


#### Pose Estimation

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-pose.dxnn | 160.4 ±0.5 | 7 | 186 | 91.3 | 100.0 | 74~79 | 1000 | ok |
| yolo26s-pose.dxnn | 91.3 ±0.3 | 5 | 82 | 91.5 | 100.0 | 77~82 | 1000 | ok |
| yolo26m-pose.dxnn | 50.1 ±6.1 | 4 | 43 | 86.8 | 100.0 | 85~86 | 300~1000 | ok |
| yolo26l-pose.dxnn | 39.4 ±5.1 | 4 | 35 | 89.8 | 100.0 | 85~86 | 300~1000 | ok |
| yolo26x-pose.dxnn | 19.5 ±1.8 | 4 | 19 | 85.2 | 100.0 | 85~86 | 300~1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-pose.dxnn | 7 | [3]:102.6 · [4]:127.8 · [5]:147.8 · [6]:156.0 · **[7]:159.4 ★** · [8]:156.3 |
| yolo26s-pose.dxnn | 5 | [3]:71.0 · [4]:86.9 · **[5]:89.9 ★** · [6]:88.6 · [7]:88.7 · [8]:89.3 |
| yolo26m-pose.dxnn | 4 | [3]:53.5 · **[4]:61.8 ★** · [5]:60.9 · [6]:60.7 · [7]:61.3 · [8]:61.1 |
| yolo26l-pose.dxnn | 4 | [3]:41.3 · **[4]:46.2 ★** · [5]:44.6 · [6]:45.1 · [7]:45.4 · [8]:45.5 |
| yolo26x-pose.dxnn | 4 | [3]:25.5 · **[4]:27.6 ★** · [5]:26.7 · [6]:26.9 · [7]:27.1 · [8]:27.0 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-pose.dxnn | 160.5 ±0.7 | 5 | 58 | 90.7 | 100.0 | 74~78 | 1000 | ok |
| yolo26s-pose.dxnn | 91.5 ±0.3 | 4 | 41 | 90.4 | 100.0 | 78~83 | 1000 | ok |
| yolo26m-pose.dxnn | 52.9 ±4.5 | 4 | 22 | 90.1 | 100.0 | 84~86 | 400~1000 | ok |
| yolo26l-pose.dxnn | 40.8 ±4.1 | 4 | 17 | 89.0 | 100.0 | 84~85 | 400~1000 | ok |
| yolo26x-pose.dxnn | 19.7 ±0.4 | 4 | 9 | 86.6 | 100.0 | 85~86 | 300~700 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-pose.dxnn | 5 | [3]:102.9 · [4]:139.2 · **[5]:159.5 ★** · [6]:154.8 · [7]:155.4 · [8]:155.9 |
| yolo26s-pose.dxnn | 4 | [3]:70.9 · **[4]:90.6 ★** · [5]:87.8 · [6]:88.8 · [7]:88.2 · [8]:89.0 |
| yolo26m-pose.dxnn | 4 | [3]:50.0 · **[4]:61.9 ★** · [5]:59.7 · [6]:60.5 · [7]:61.8 · [8]:61.4 |
| yolo26l-pose.dxnn | 4 | [3]:41.0 · **[4]:46.4 ★** · [5]:45.1 · [6]:45.0 · [7]:45.4 · [8]:45.6 |
| yolo26x-pose.dxnn | 4 | [3]:25.4 · **[4]:27.6 ★** · [5]:27.0 · [6]:27.0 · [7]:27.0 · [8]:27.1 |


#### Segmentation

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-seg.dxnn | 69.8 ±0.4 | 7 | 248 | 29.4 | 70.1 | 66~67 | 1000 | ok |
| yolo26s-seg.dxnn | 70.0 ±0.2 | 7 | 248 | 81.0 | 91.0 | 79~82 | 1000 | ok |
| yolo26m-seg.dxnn | 32.1 ±3.8 | 6 | 82 | 88.6 | 100.0 | 85~86 | 200~600 | ok |
| yolo26l-seg.dxnn | 26.7 ±2.3 | 5 | 67 | 88.8 | 100.0 | 85 | 300~1000 | ok |
| yolo26x-seg.dxnn | 13.7 ±0.6 | 4 | 35 | 83.2 | 100.0 | 85 | 300~800 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-seg.dxnn | 7 | [3]:56.9 · [4]:66.4 · [5]:69.9 · [6]:70.0 · **[7]:70.0 ★** · [8]:69.8 |
| yolo26s-seg.dxnn | 7 | [3]:45.8 · [4]:56.9 · [5]:63.7 · [6]:68.9 · **[7]:69.6 ★** · [8]:69.5 |
| yolo26m-seg.dxnn | 6 | [3]:36.6 · [4]:43.4 · [5]:46.5 · **[6]:46.8 ★** · [7]:45.9 · [8]:46.2 |
| yolo26l-seg.dxnn | 5 | [3]:30.6 · [4]:35.9 · **[5]:37.3 ★** · [6]:36.6 · [7]:36.6 · [8]:36.6 |
| yolo26x-seg.dxnn | 4 | [3]:18.3 · **[4]:21.6 ★** · [5]:21.0 · [6]:21.2 · [7]:21.0 · [8]:20.4 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-seg.dxnn | 95.7 ±0.0 | 6 | 130 | 47.2 | 79.6 | 72~75 | 1000 | ok |
| yolo26s-seg.dxnn | 71.1 ±1.6 | 5 | 87 | 87.7 | 100.0 | 80~85 | 800~1000 | ok |
| yolo26m-seg.dxnn | 31.8 ±2.5 | 5 | 48 | 88.2 | 100.0 | 85~86 | 300~800 | ok |
| yolo26l-seg.dxnn | 27.1 ±3.2 | 4 | 38 | 86.5 | 100.0 | 85~86 | 300~1000 | ok |
| yolo26x-seg.dxnn | 13.9 ±1.1 | 4 | 23 | 83.0 | 100.0 | 85 | 300~1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-seg.dxnn | 6 | [3]:70.3 · [4]:69.3 · [5]:94.2 · **[6]:95.4 ★** · [7]:95.4 · [8]:95.4 · [9]:95.3 · [10]:95.4 |
| yolo26s-seg.dxnn | 5 | [3]:53.8 · [4]:65.8 · **[5]:72.1 ★** · [6]:70.4 · [7]:70.8 · [8]:70.8 |
| yolo26m-seg.dxnn | 5 | [3]:40.4 · [4]:45.7 · **[5]:46.8 ★** · [6]:46.4 · [7]:46.2 · [8]:46.5 |
| yolo26l-seg.dxnn | 4 | [3]:30.5 · **[4]:37.2 ★** · [5]:36.2 · [6]:36.4 · [7]:36.7 · [8]:36.7 |
| yolo26x-seg.dxnn | 4 | [3]:17.7 · **[4]:21.7 ★** · [5]:20.9 · [6]:21.2 · [7]:21.0 · [8]:20.5 |


#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-obb.dxnn | 52.8 ±0.2 | 4 | 52 | 90.6 | 100.0 | 73~76 | 1000 | ok |
| yolo26s-obb.dxnn | 30.6 ±0.1 | 4 | 33 | 90.8 | 100.0 | 75~79 | 1000 | ok |
| yolo26m-obb.dxnn | 19.1 ±2.1 | 4 | 20 | 83.0 | 100.0 | 84~86 | 300~1000 | ok |
| yolo26l-obb.dxnn | 13.9 ±1.3 | 4 | 16 | 86.2 | 100.0 | 85~86 | 300~1000 | ok |
| yolo26x-obb.dxnn | 7.3 ±0.2 | 4 | 8 | 79.7 | 100.0 | 85~86 | 300~800 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-obb.dxnn | 4 | [3]:44.2 · **[4]:52.6 ★** · [5]:51.4 · [6]:51.6 · [7]:51.6 · [8]:51.9 |
| yolo26s-obb.dxnn | 4 | [3]:28.7 · **[4]:30.4 ★** · [5]:30.0 · [6]:30.1 · [7]:30.2 · [8]:30.2 |
| yolo26m-obb.dxnn | 4 | [3]:21.0 · **[4]:22.1 ★** · [5]:21.8 · [6]:21.6 · [7]:22.0 · [8]:22.0 |
| yolo26l-obb.dxnn | 4 | [3]:15.4 · **[4]:16.1 ★** · [5]:16.1 · [6]:15.9 · [7]:16.0 · [8]:16.1 |
| yolo26x-obb.dxnn | 4 | [3]:9.4 · **[4]:9.7 ★** · [5]:9.7 · [6]:9.6 · [7]:9.7 · [8]:9.4 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-obb.dxnn | 52.5 ±0.6 | 4 | 27 | 89.0 | 100.0 | 74~78 | 1000 | ok |
| yolo26s-obb.dxnn | 30.5 ±0.1 | 9 | 17 | 92.4 | 100.0 | 78~81 | 1000 | ok |
| yolo26m-obb.dxnn | 19.2 ±2.0 | 7 | 10 | 87.6 | 100.0 | 85~86 | 300~1000 | ok |
| yolo26l-obb.dxnn | 13.6 ±0.8 | 4 | 7 | 85.3 | 100.0 | 86 | 300~1000 | ok |
| yolo26x-obb.dxnn | 7.5 ±0.1 | 4 | 4 | 79.2 | 100.0 | 85~86 | 300~900 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-obb.dxnn | 4 | [3]:41.0 · **[4]:52.3 ★** · [5]:51.6 · [6]:51.7 · [7]:51.9 · [8]:52.1 |
| yolo26s-obb.dxnn | 9 | [3]:27.3 · [4]:30.0 · [5]:29.8 · [6]:30.1 · [7]:30.1 · [8]:30.1 · **[9]:30.1 ★** · [10]:30.0 |
| yolo26m-obb.dxnn | 7 | [3]:20.3 · [4]:22.2 · [5]:21.9 · [6]:22.1 · **[7]:22.3 ★** · [8]:22.0 |
| yolo26l-obb.dxnn | 4 | [3]:15.2 · **[4]:16.1 ★** · [5]:16.0 · [6]:16.0 · [7]:16.0 · [8]:16.1 · [9]:16.0 · [10]:16.0 |
| yolo26x-obb.dxnn | 4 | [3]:9.2 · **[4]:9.7 ★** · [5]:9.6 · [6]:9.6 · [7]:9.7 · [8]:9.4 |


#### Classification

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-cls.dxnn | 3027.9 ±0.9 | 6 | 54 | 88.8 | 97.5 | 68~71 | 1000 | ok |
| yolo26s-cls.dxnn | 1566.8 ±3.4 | 5 | 29 | 90.4 | 97.9 | 70~74 | 1000 | ok |
| yolo26m-cls.dxnn | 1009.2 ±32.2 | 4 | 19 | 90.4 | 98.4 | 80~84 | 800~1000 | ok |
| yolo26l-cls.dxnn | 696.2 ±0.5 | 4 | 13 | 90.7 | 98.3 | 77~82 | 1000 | ok |
| yolo26x-cls.dxnn | 322.6 ±9.2 | 4 | 7 | 90.5 | 99.8 | 81~85 | 800~1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-cls.dxnn | 6 | [3]:2161.9 · [4]:2856.0 · [5]:2994.7 · **[6]:3044.1 ★** · [7]:3033.0 · [8]:3031.2 |
| yolo26s-cls.dxnn | 5 | [3]:1327.0 · [4]:1561.4 · **[5]:1572.2 ★** · [6]:1564.9 · [7]:1569.9 · [8]:1564.9 |
| yolo26m-cls.dxnn | 4 | [3]:911.3 · **[4]:1031.1 ★** · [5]:1027.6 · [6]:1024.7 · [7]:1025.2 · [8]:1023.9 |
| yolo26l-cls.dxnn | 4 | [3]:628.3 · **[4]:696.7 ★** · [5]:686.1 · [6]:684.0 · [7]:685.6 · [8]:684.3 |
| yolo26x-cls.dxnn | 4 | [3]:318.6 · **[4]:331.4 ★** · [5]:327.7 · [6]:329.8 · [7]:329.6 · [8]:330.2 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-cls.dxnn | 3028.2 ±4.1 | 6 | 54 | 89.2 | 96.9 | 67~70 | 1000 | ok |
| yolo26s-cls.dxnn | 1566.8 ±3.1 | 5 | 29 | 90.5 | 98.1 | 70~74 | 1000 | ok |
| yolo26m-cls.dxnn | 1005.9 ±41.0 | 4 | 19 | 89.3 | 98.6 | 80~84 | 800~1000 | ok |
| yolo26l-cls.dxnn | 695.8 ±0.3 | 4 | 13 | 89.6 | 98.5 | 77~82 | 1000 | ok |
| yolo26x-cls.dxnn | 324.2 ±7.7 | 4 | 6 | 92.0 | 100.0 | 80~84 | 600~1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-cls.dxnn | 6 | [3]:2149.7 · [4]:2860.3 · [5]:2995.3 · **[6]:3041.5 ★** · [7]:3034.8 · [8]:3020.5 |
| yolo26s-cls.dxnn | 5 | [3]:1323.1 · [4]:1563.7 · **[5]:1572.1 ★** · [6]:1567.0 · [7]:1567.1 · [8]:1556.9 |
| yolo26m-cls.dxnn | 4 | [3]:917.5 · **[4]:1033.8 ★** · [5]:1026.9 · [6]:1023.2 · [7]:1024.8 · [8]:1026.5 |
| yolo26l-cls.dxnn | 4 | [3]:629.3 · **[4]:696.1 ★** · [5]:685.1 · [6]:688.2 · [7]:685.8 · [8]:685.6 |
| yolo26x-cls.dxnn | 4 | [3]:317.6 · **[4]:331.2 ★** · [5]:327.1 · [6]:329.1 · [7]:329.3 · [8]:328.9 |


### Latency (Single-Core, Sync)

#### Object Detection

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n.dxnn | 36.0 ±1.1 | 27.74 | 25.22 | 2.52 | 47 | ok |
| yolo26s.dxnn | 28.5 ±0.4 | 35.10 | 32.63 | 2.47 | 57 | ok |
| yolo26m.dxnn | 22.8 ±6.2 | 43.86 | 41.31 | 2.55 | 58 | ok |
| yolo26l.dxnn | 18.4 ±3.6 | 54.27 | 51.66 | 2.61 | 59 | ok |
| yolo26x.dxnn | 11.6 ±1.1 | 85.99 | 83.45 | 2.54 | 62 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n.dxnn | 41.9 ±0.2 | 23.88 | 23.88 | N/A | 57 | ok |
| yolo26s.dxnn | 29.4 ±0.4 | 34.00 | 34.00 | N/A | 57 | ok |
| yolo26m.dxnn | 24.6 ±5.5 | 40.58 | 40.58 | N/A | 59 | ok |
| yolo26l.dxnn | 19.6 ±4.6 | 51.08 | 51.08 | N/A | 60 | ok |
| yolo26x.dxnn | 12.0 ±0.9 | 83.03 | 83.03 | N/A | 63 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-pose.dxnn | 42.6 ±0.5 | 23.48 | 21.98 | 1.50 | 56 | ok |
| yolo26s-pose.dxnn | 30.8 ±0.3 | 32.42 | 30.89 | 1.53 | 58 | ok |
| yolo26m-pose.dxnn | 24.8 ±6.1 | 40.25 | 38.70 | 1.55 | 59 | ok |
| yolo26l-pose.dxnn | 20.0 ±5.1 | 49.96 | 48.47 | 1.49 | 60 | ok |
| yolo26x-pose.dxnn | 12.1 ±1.8 | 82.68 | 81.15 | 1.53 | 62 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-pose.dxnn | 48.5 ±0.7 | 20.61 | 20.61 | N/A | 57 | ok |
| yolo26s-pose.dxnn | 33.7 ±0.3 | 29.71 | 29.71 | N/A | 57 | ok |
| yolo26m-pose.dxnn | 25.5 ±4.5 | 39.20 | 39.20 | N/A | 59 | ok |
| yolo26l-pose.dxnn | 20.5 ±4.1 | 48.76 | 48.76 | N/A | 61 | ok |
| yolo26x-pose.dxnn | 12.4 ±0.4 | 80.95 | 80.95 | N/A | 63 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-seg.dxnn | 23.5 ±0.4 | 42.56 | 39.51 | 3.05 | 57 | ok |
| yolo26s-seg.dxnn | 17.7 ±0.2 | 56.64 | 53.58 | 3.06 | 57 | ok |
| yolo26m-seg.dxnn | 14.5 ±3.8 | 69.18 | 66.11 | 3.07 | 59 | ok |
| yolo26l-seg.dxnn | 12.6 ±2.3 | 79.44 | 76.37 | 3.07 | 60 | ok |
| yolo26x-seg.dxnn | 7.8 ±0.6 | 127.90 | 124.89 | 3.01 | 63 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-seg.dxnn | 25.8 ±0.0 | 38.77 | 38.77 | N/A | 57 | ok |
| yolo26s-seg.dxnn | 20.1 ±1.6 | 49.64 | 49.64 | N/A | 58 | ok |
| yolo26m-seg.dxnn | 15.4 ±2.5 | 64.89 | 64.89 | N/A | 60 | ok |
| yolo26l-seg.dxnn | 13.2 ±3.2 | 75.49 | 75.49 | N/A | 60 | ok |
| yolo26x-seg.dxnn | 8.3 ±1.1 | 121.10 | 121.10 | N/A | 63 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-obb.dxnn | 22.9 ±0.2 | 43.73 | 42.06 | 1.67 | 58 | ok |
| yolo26s-obb.dxnn | 15.1 ±0.1 | 66.22 | 64.46 | 1.76 | 59 | ok |
| yolo26m-obb.dxnn | 11.6 ±2.1 | 86.54 | 84.81 | 1.73 | 63 | ok |
| yolo26l-obb.dxnn | 8.8 ±1.3 | 113.51 | 111.69 | 1.82 | 64 | ok |
| yolo26x-obb.dxnn | 5.0 ±0.2 | 199.12 | 197.32 | 1.80 | 69 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-obb.dxnn | 23.6 ±0.6 | 42.37 | 42.37 | N/A | 58 | ok |
| yolo26s-obb.dxnn | 15.5 ±0.1 | 64.49 | 64.49 | N/A | 60 | ok |
| yolo26m-obb.dxnn | 11.8 ±2.0 | 84.75 | 84.75 | N/A | 63 | ok |
| yolo26l-obb.dxnn | 8.9 ±0.8 | 111.80 | 111.80 | N/A | 65 | ok |
| yolo26x-obb.dxnn | 5.1 ±0.1 | 196.35 | 196.35 | N/A | 68 | ok |

#### Classification

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-cls.dxnn | 715.2 ±0.9 | 1.40 | 1.40 | N/A | 56 | ok |
| yolo26s-cls.dxnn | 459.1 ±3.4 | 2.18 | 2.18 | N/A | 54 | ok |
| yolo26m-cls.dxnn | 346.9 ±32.2 | 2.88 | 2.88 | N/A | 55 | ok |
| yolo26l-cls.dxnn | 235.6 ±0.5 | 4.24 | 4.24 | N/A | 56 | ok |
| yolo26x-cls.dxnn | 134.1 ±9.2 | 7.46 | 7.46 | N/A | 56 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-cls.dxnn | 732.1 ±4.1 | 1.37 | 1.37 | N/A | 54 | ok |
| yolo26s-cls.dxnn | 460.6 ±3.1 | 2.17 | 2.17 | N/A | 55 | ok |
| yolo26m-cls.dxnn | 346.2 ±41.0 | 2.89 | 2.89 | N/A | 56 | ok |
| yolo26l-cls.dxnn | 233.9 ±0.3 | 4.28 | 4.28 | N/A | 56 | ok |
| yolo26x-cls.dxnn | 135.0 ±7.7 | 7.41 | 7.41 | N/A | 56 | ok |

## E2E Pipeline (Single-Stream)

### Object Detection

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | avdec_h264 | 3455 | 3 | 69.6 ±0.4 | 49.66 | 339 | 23.5 | 70.0 | 58~60 | 1000 | 284 | ok |
| yolo26s.dxnn | avdec_h264 | 3455 | 3 | 69.8 ±0.2 | 49.48 | 340 | 50.1 | 81.2 | 68~73 | 1000 | 304 | ok |
| yolo26m.dxnn | avdec_h264 | 3455 | 3 | 56.1 ±7.3 | 61.54 | 187 | 93.5 | 100.0 | 81~85 | 300~1000 | 326 | ok |
| yolo26l.dxnn | avdec_h264 | 3455 | 3 | 38.0 ±4.7 | 90.92 | 118 | 95.4 | 100.0 | 84~86 | 300~1000 | 334 | ok |
| yolo26x.dxnn | avdec_h264 | 3455 | 3 | 16.6 ±0.6 | 207.83 | 53 | 94.1 | 100.0 | 86 | 200~700 | 390 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | avdec_h264 | 3455 | 3 | 87.4 ±0.4 | 39.53 | 308 | 30.4 | 74.1 | 61~64 | 1000 | 317 | ok |
| yolo26s.dxnn | avdec_h264 | 3455 | 3 | 88.4 ±0.5 | 39.09 | 305 | 79.7 | 92.9 | 69~75 | 1000 | 331 | ok |
| yolo26m.dxnn | avdec_h264 | 3455 | 3 | 53.8 ±8.3 | 64.21 | 174 | 93.8 | 100.0 | 82~86 | 300~1000 | 326 | ok |
| yolo26l.dxnn | avdec_h264 | 3455 | 3 | 37.0 ±6.0 | 93.37 | 120 | 95.1 | 100.0 | 84~86 | 300~1000 | 341 | ok |
| yolo26x.dxnn | avdec_h264 | 3455 | 3 | 17.4 ±0.5 | 198.77 | 58 | 94.4 | 100.0 | 86 | 300~700 | 399 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n.dxnn | 69.6 | 87.4 | -17.8 | -20.4% |
| yolo26s.dxnn | 69.8 | 88.4 | -18.5 | -21.0% |
| yolo26m.dxnn | 56.1 | 53.8 | +2.3 | +4.3% |
| yolo26l.dxnn | 38.0 | 37.0 | +1.0 | +2.7% |
| yolo26x.dxnn | 16.6 | 17.4 | -0.8 | -4.4% |

### Pose Estimation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | avdec_h264 | 3455 | 3 | 85.7 ±0.3 | 40.33 | 348 | 33.3 | 69.6 | 63~66 | 1000 | 273 | ok |
| yolo26s-pose.dxnn | avdec_h264 | 3455 | 3 | 85.0 ±0.3 | 40.67 | 343 | 79.2 | 93.2 | 71~77 | 1000 | 295 | ok |
| yolo26m-pose.dxnn | avdec_h264 | 3455 | 3 | 49.9 ±8.9 | 69.20 | 131 | 94.7 | 100.0 | 83~86 | 300~1000 | 317 | ok |
| yolo26l-pose.dxnn | avdec_h264 | 3455 | 3 | 34.0 ±4.9 | 101.47 | 89 | 94.7 | 100.0 | 85~86 | 300~1000 | 321 | ok |
| yolo26x-pose.dxnn | avdec_h264 | 3455 | 3 | 16.8 ±0.2 | 205.41 | 44 | 95.3 | 100.0 | 86 | 300~700 | 384 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | avdec_h264 | 3455 | 3 | 127.2 ±0.8 | 27.16 | 314 | 60.1 | 81.9 | 65~69 | 1000 | 256 | ok |
| yolo26s-pose.dxnn | avdec_h264 | 3455 | 3 | 89.0 ±0.4 | 38.80 | 176 | 92.6 | 100.0 | 71~75 | 1000 | 286 | ok |
| yolo26m-pose.dxnn | avdec_h264 | 3455 | 3 | 48.1 ±11.5 | 71.89 | 96 | 94.9 | 100.0 | 82~86 | 200~1000 | 307 | ok |
| yolo26l-pose.dxnn | avdec_h264 | 3455 | 3 | 34.2 ±6.9 | 101.03 | 68 | 95.0 | 100.0 | 85~86 | 300~1000 | 316 | ok |
| yolo26x-pose.dxnn | avdec_h264 | 3455 | 3 | 16.6 ±0.2 | 208.11 | 34 | 95.5 | 100.0 | 86 | 300~800 | 373 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-pose.dxnn | 85.7 | 127.2 | -41.5 | -32.7% |
| yolo26s-pose.dxnn | 85.0 | 89.0 | -4.1 | -4.6% |
| yolo26m-pose.dxnn | 49.9 | 48.1 | +1.9 | +3.9% |
| yolo26l-pose.dxnn | 34.0 | 34.2 | -0.2 | -0.4% |
| yolo26x-pose.dxnn | 16.8 | 16.6 | +0.2 | +1.3% |

### Segmentation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | avdec_h264 | 3455 | 3 | 48.5 ±0.2 | 71.22 | 335 | 20.3 | 63.4 | 61~63 | 1000 | 377 | ok |
| yolo26s-seg.dxnn | avdec_h264 | 3455 | 3 | 47.6 ±0.7 | 72.53 | 344 | 40.1 | 71.9 | 71~76 | 1000 | 399 | ok |
| yolo26m-seg.dxnn | avdec_h264 | 3455 | 3 | 28.8 ±3.4 | 120.11 | 137 | 94.5 | 100.0 | 86 | 200~1000 | 416 | ok |
| yolo26l-seg.dxnn | avdec_h264 | 3455 | 3 | 22.2 ±0.1 | 155.45 | 106 | 94.5 | 100.0 | 86~87 | 200~600 | 431 | ok |
| yolo26x-seg.dxnn | avdec_h264 | 3455 | 3 | 11.3 ±0.1 | 306.25 | 49 | 95.2 | 100.0 | 86 | 200~500 | 494 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | avdec_h264 | 3455 | 3 | 63.9 ±0.7 | 54.08 | 353 | 27.4 | 75.0 | 64~67 | 1000 | 432 | ok |
| yolo26s-seg.dxnn | avdec_h264 | 3455 | 3 | 63.2 ±0.2 | 54.63 | 354 | 65.1 | 86.1 | 75~82 | 1000 | 448 | ok |
| yolo26m-seg.dxnn | avdec_h264 | 3455 | 3 | 29.6 ±3.5 | 116.94 | 127 | 94.3 | 100.0 | 85~86 | 200~1000 | 429 | ok |
| yolo26l-seg.dxnn | avdec_h264 | 3455 | 3 | 22.7 ±1.9 | 152.24 | 98 | 95.1 | 100.0 | 86 | 200~1000 | 439 | ok |
| yolo26x-seg.dxnn | avdec_h264 | 3455 | 3 | 11.2 ±0.2 | 307.86 | 48 | 94.9 | 100.0 | 86 | 200~500 | 508 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-seg.dxnn | 48.5 | 63.9 | -15.4 | -24.1% |
| yolo26s-seg.dxnn | 47.6 | 63.2 | -15.6 | -24.7% |
| yolo26m-seg.dxnn | 28.8 | 29.6 | -0.8 | -2.7% |
| yolo26l-seg.dxnn | 22.2 | 22.7 | -0.5 | -2.0% |
| yolo26x-seg.dxnn | 11.3 | 11.2 | +0.1 | +0.5% |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | avdec_h264 | 2640 | 3 | 52.2 ±0.4 | 50.58 | 172 | 92.1 | 100.0 | 71~77 | 1000 | 302 | ok |
| yolo26s-obb.dxnn | avdec_h264 | 2640 | 3 | 30.2 ±0.4 | 87.48 | 99 | 94.8 | 100.0 | 80~86 | 600~1000 | 321 | ok |
| yolo26m-obb.dxnn | avdec_h264 | 2640 | 3 | 17.2 ±2.5 | 153.20 | 57 | 93.9 | 100.0 | 86 | 200~1000 | 338 | ok |
| yolo26l-obb.dxnn | avdec_h264 | 2640 | 3 | 11.1 ±0.2 | 237.59 | 38 | 95.1 | 100.0 | 86 | 200~700 | 348 | ok |
| yolo26x-obb.dxnn | avdec_h264 | 2640 | 3 | 6.2 ±0.1 | 428.12 | 22 | 93.9 | 100.0 | 86 | 200~800 | 418 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | avdec_h264 | 2640 | 3 | 52.1 ±0.1 | 50.68 | 157 | 93.1 | 100.0 | 71~77 | 1000 | 300 | ok |
| yolo26s-obb.dxnn | avdec_h264 | 2640 | 3 | 29.2 ±1.8 | 90.37 | 91 | 94.9 | 100.0 | 80~86 | 300~1000 | 313 | ok |
| yolo26m-obb.dxnn | avdec_h264 | 2640 | 3 | 15.4 ±1.2 | 170.88 | 49 | 94.1 | 100.0 | 86 | 200~1000 | 335 | ok |
| yolo26l-obb.dxnn | avdec_h264 | 2640 | 3 | 12.2 ±1.6 | 216.18 | 40 | 95.4 | 100.0 | 86 | 200~1000 | 348 | ok |
| yolo26x-obb.dxnn | avdec_h264 | 2640 | 3 | 6.2 ±0.0 | 425.18 | 21 | 94.3 | 100.0 | 86~87 | 200~700 | 414 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-obb.dxnn | 52.2 | 52.1 | +0.1 | +0.2% |
| yolo26s-obb.dxnn | 30.2 | 29.2 | +1.0 | +3.3% |
| yolo26m-obb.dxnn | 17.2 | 15.4 | +1.8 | +11.5% |
| yolo26l-obb.dxnn | 11.1 | 12.2 | -1.1 | -9.0% |
| yolo26x-obb.dxnn | 6.2 | 6.2 | -0.0 | -0.6% |

### Classification

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-cls.dxnn | avdec_h264 | 3455 | 3 | 194.0 ±0.4 | 17.81 | 276 | 4.7 | 15.8 | 54~55 | 1000 | 183 | ok |
| yolo26s-cls.dxnn | avdec_h264 | 3455 | 3 | 194.3 ±0.3 | 17.79 | 276 | 9.2 | 29.7 | 55~56 | 1000 | 192 | ok |
| yolo26m-cls.dxnn | avdec_h264 | 3455 | 3 | 194.4 ±0.4 | 17.77 | 276 | 13.2 | 37.4 | 57~58 | 1000 | 193 | ok |
| yolo26l-cls.dxnn | avdec_h264 | 3455 | 3 | 194.1 ±0.8 | 17.80 | 275 | 20.0 | 49.0 | 57 | 1000 | 209 | ok |
| yolo26x-cls.dxnn | avdec_h264 | 3455 | 3 | 194.2 ±0.9 | 17.79 | 274 | 41.4 | 69.8 | 60~62 | 1000 | 237 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-cls.dxnn | avdec_h264 | 3455 | 3 | 194.9 ±0.2 | 17.73 | 277 | 4.8 | 16.0 | 55 | 1000 | 168 | ok |
| yolo26s-cls.dxnn | avdec_h264 | 3455 | 3 | 194.9 ±0.2 | 17.73 | 277 | 9.3 | 28.8 | 55~56 | 1000 | 183 | ok |
| yolo26m-cls.dxnn | avdec_h264 | 3455 | 3 | 193.9 ±1.1 | 17.82 | 275 | 13.6 | 37.5 | 57 | 1000 | 192 | ok |
| yolo26l-cls.dxnn | avdec_h264 | 3455 | 3 | 193.8 ±0.3 | 17.83 | 275 | 20.1 | 48.9 | 58 | 1000 | 198 | ok |
| yolo26x-cls.dxnn | avdec_h264 | 3455 | 3 | 193.6 ±0.3 | 17.84 | 274 | 41.2 | 69.7 | 61~64 | 1000 | 236 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-cls.dxnn | 194.0 | 194.9 | -0.9 | -0.4% |
| yolo26s-cls.dxnn | 194.3 | 194.9 | -0.6 | -0.3% |
| yolo26m-cls.dxnn | 194.4 | 193.9 | +0.4 | +0.2% |
| yolo26l-cls.dxnn | 194.1 | 193.8 | +0.3 | +0.2% |
| yolo26x-cls.dxnn | 194.2 | 193.6 | +0.5 | +0.3% |

## E2E Pipeline (Multi-Stream)

### Object Detection

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | 2 | 3 | 69.4 ±0.7 | 34.7 | 337 | 24.1 | 71.0 | 62 | 1000 | 422 | ok |
| yolo26n.dxnn | 3 | 3 | 67.6 ±1.2 | 22.5 | 334 | 23.6 | 69.0 | 62~63 | 1000 | 526 | ok |
| yolo26s.dxnn | 2 | 3 | 68.4 ±0.8 | 34.2 | 337 | 49.4 | 80.6 | 76~78 | 1000 | 435 | ok |
| yolo26s.dxnn | 3 | 3 | 67.9 ±0.5 | 22.6 | 335 | 49.2 | 84.9 | 79 | 1000 | 540 | ok |
| yolo26m.dxnn | 1 | 3 | 56.1 ±7.3 | 56.1 | 187 | 93.5 | 100.0 | 81~85 | 300~1000 | 326 | ok |
| yolo26m.dxnn | 2 | 3 | 43.1 ±0.8 | 21.5 | 130 | 96.0 | 100.0 | 85~86 | 300~700 | 457 | ok |
| yolo26l.dxnn | 1 | 3 | 38.0 ±4.7 | 38.0 | 118 | 95.4 | 100.0 | 84~86 | 300~1000 | 334 | ok |
| yolo26l.dxnn | 2 | 3 | 32.3 ±1.0 | 16.1 | 100 | 97.5 | 100.0 | 86 | 300~800 | 465 | ok |
| yolo26x.dxnn | 1 | 3 | 16.6 ±0.6 | 16.6 | 53 | 94.1 | 100.0 | 86 | 200~700 | 390 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | 2 | 3 | 87.5 ±0.4 | 43.8 | 309 | 31.0 | 75.5 | 67~68 | 1000 | 459 | ok |
| yolo26n.dxnn | 3 | 3 | 87.3 ±0.6 | 29.1 | 308 | 31.3 | 73.9 | 67~68 | 1000 | 566 | ok |
| yolo26s.dxnn | 2 | 3 | 86.5 ±0.6 | 43.2 | 312 | 76.8 | 89.2 | 82~84 | 800~1000 | 481 | ok |
| yolo26s.dxnn | 3 | 3 | 81.1 ±2.2 | 27.0 | 279 | 92.5 | 100.0 | 85~86 | 300~1000 | 576 | ok |
| yolo26m.dxnn | 1 | 3 | 53.8 ±8.3 | 53.8 | 174 | 93.8 | 100.0 | 82~86 | 300~1000 | 326 | ok |
| yolo26m.dxnn | 2 | 3 | 44.1 ±0.8 | 22.1 | 140 | 96.5 | 100.0 | 85~87 | 300~700 | 466 | ok |
| yolo26l.dxnn | 1 | 3 | 37.0 ±6.0 | 37.0 | 120 | 95.1 | 100.0 | 84~86 | 300~1000 | 341 | ok |
| yolo26l.dxnn | 2 | 3 | 31.9 ±1.0 | 15.9 | 103 | 97.5 | 100.0 | 86 | 300~600 | 475 | ok |
| yolo26x.dxnn | 1 | 3 | 17.4 ±0.5 | 17.4 | 58 | 94.4 | 100.0 | 86 | 300~700 | 399 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n.dxnn | 2 | 34.7 | 2 | 43.8 |
| yolo26s.dxnn | 2 | 34.2 | 2 | 43.2 |
| yolo26m.dxnn | 1 | 56.1 | 1 | 53.8 |
| yolo26l.dxnn | 1 | 38.0 | 1 | 37.0 |

### Pose Estimation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | 2 | 3 | 82.7 ±0.8 | 41.3 | 346 | 31.7 | 73.8 | 68~69 | 1000 | 416 | ok |
| yolo26n-pose.dxnn | 3 | 3 | 82.8 ±0.3 | 27.6 | 344 | 32.2 | 71.3 | 68~69 | 1000 | 520 | ok |
| yolo26s-pose.dxnn | 2 | 3 | 81.1 ±0.6 | 40.5 | 313 | 83.0 | 100.0 | 85~86 | 400~1000 | 432 | ok |
| yolo26s-pose.dxnn | 3 | 3 | 77.5 ±2.2 | 25.8 | 243 | 94.2 | 100.0 | 85~86 | 300~1000 | 536 | ok |
| yolo26m-pose.dxnn | 1 | 3 | 49.9 ±8.9 | 49.9 | 131 | 94.7 | 100.0 | 83~86 | 300~1000 | 317 | ok |
| yolo26m-pose.dxnn | 2 | 3 | 41.1 ±1.3 | 20.6 | 106 | 96.7 | 100.0 | 86 | 300~600 | 450 | ok |
| yolo26l-pose.dxnn | 1 | 3 | 34.0 ±4.9 | 34.0 | 89 | 94.7 | 100.0 | 85~86 | 300~1000 | 321 | ok |
| yolo26l-pose.dxnn | 2 | 3 | 30.0 ±0.6 | 15.0 | 76 | 96.4 | 100.0 | 86 | 300~800 | 461 | ok |
| yolo26x-pose.dxnn | 1 | 3 | 16.8 ±0.2 | 16.8 | 44 | 95.3 | 100.0 | 86 | 300~700 | 384 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | 4 | 3 | 126.7 ±0.5 | 31.7 | 372 | 63.1 | 83.4 | 77~79 | 1000 | 624 | ok |
| yolo26n-pose.dxnn | 5 | 3 | 127.9 ±0.8 | 25.6 | 371 | 64.6 | 87.8 | 78~79 | 1000 | 725 | ok |
| yolo26s-pose.dxnn | 2 | 3 | 82.0 ±6.2 | 41.0 | 166 | 95.2 | 100.0 | 84~85 | 400~1000 | 422 | ok |
| yolo26s-pose.dxnn | 3 | 3 | 78.8 ±0.9 | 26.2 | 159 | 96.0 | 100.0 | 85~86 | 300~1000 | 526 | ok |
| yolo26m-pose.dxnn | 1 | 3 | 48.1 ±11.5 | 48.1 | 96 | 94.9 | 100.0 | 82~86 | 200~1000 | 307 | ok |
| yolo26m-pose.dxnn | 2 | 3 | 39.8 ±0.3 | 19.9 | 81 | 97.4 | 100.0 | 86 | 300~700 | 443 | ok |
| yolo26l-pose.dxnn | 1 | 3 | 34.2 ±6.9 | 34.2 | 68 | 95.0 | 100.0 | 85~86 | 300~1000 | 316 | ok |
| yolo26l-pose.dxnn | 2 | 3 | 30.2 ±1.0 | 15.1 | 59 | 96.4 | 100.0 | 86 | 200~700 | 453 | ok |
| yolo26x-pose.dxnn | 1 | 3 | 16.6 ±0.2 | 16.6 | 34 | 95.5 | 100.0 | 86 | 300~800 | 373 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-pose.dxnn | 2 | 41.3 | 4 | 31.7 |
| yolo26s-pose.dxnn | 2 | 40.5 | 2 | 41.0 |
| yolo26m-pose.dxnn | 1 | 49.9 | 1 | 48.1 |
| yolo26l-pose.dxnn | 1 | 34.0 | 1 | 34.2 |

### Segmentation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | 1 | 3 | 48.5 ±0.2 | 48.5 | 335 | 20.3 | 63.4 | 61~63 | 1000 | 377 | ok |
| yolo26n-seg.dxnn | 2 | 3 | 47.4 ±0.6 | 23.7 | 342 | 20.0 | 63.4 | 64~65 | 1000 | 526 | ok |
| yolo26s-seg.dxnn | 1 | 3 | 47.6 ±0.7 | 47.6 | 344 | 40.1 | 71.9 | 71~76 | 1000 | 399 | ok |
| yolo26s-seg.dxnn | 2 | 3 | 46.8 ±0.1 | 23.4 | 342 | 39.7 | 73.4 | 78~80 | 1000 | 543 | ok |
| yolo26m-seg.dxnn | 1 | 3 | 28.8 ±3.4 | 28.8 | 137 | 94.5 | 100.0 | 86 | 200~1000 | 416 | ok |
| yolo26l-seg.dxnn | 1 | 3 | 22.2 ±0.1 | 22.2 | 106 | 94.5 | 100.0 | 86~87 | 200~600 | 431 | ok |
| yolo26x-seg.dxnn | 1 | 3 | 11.3 ±0.1 | 11.3 | 49 | 95.2 | 100.0 | 86 | 200~500 | 494 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | 2 | 3 | 63.6 ±0.6 | 31.8 | 350 | 27.8 | 73.8 | 68~69 | 1000 | 583 | ok |
| yolo26n-seg.dxnn | 3 | 3 | 63.3 ±0.1 | 21.1 | 354 | 27.9 | 74.8 | 68~70 | 1000 | 695 | ok |
| yolo26s-seg.dxnn | 2 | 3 | 58.9 ±4.3 | 29.5 | 299 | 84.8 | 100.0 | 82~86 | 300~1000 | 598 | ok |
| yolo26s-seg.dxnn | 1 | 3 | 63.2 ±0.2 | 63.2 | 354 | 65.1 | 86.1 | 75~82 | 1000 | 448 | ok |
| yolo26m-seg.dxnn | 1 | 3 | 29.6 ±3.5 | 29.6 | 127 | 94.3 | 100.0 | 85~86 | 200~1000 | 429 | ok |
| yolo26l-seg.dxnn | 1 | 3 | 22.7 ±1.9 | 22.7 | 98 | 95.1 | 100.0 | 86 | 200~1000 | 439 | ok |
| yolo26x-seg.dxnn | 1 | 3 | 11.2 ±0.2 | 11.2 | 48 | 94.9 | 100.0 | 86 | 200~500 | 508 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-seg.dxnn | 1 | 48.5 | 2 | 31.8 |
| yolo26s-seg.dxnn | 1 | 47.6 | 1 | 63.2 |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | 1 | 3 | 52.2 ±0.4 | 52.2 | 172 | 92.1 | 100.0 | 71~77 | 1000 | 302 | ok |
| yolo26n-obb.dxnn | 2 | 3 | 52.4 ±0.2 | 26.2 | 181 | 96.1 | 100.0 | 84~85 | 800~1000 | 440 | ok |
| yolo26s-obb.dxnn | 1 | 3 | 30.2 ±0.4 | 30.2 | 99 | 94.8 | 100.0 | 80~86 | 600~1000 | 321 | ok |
| yolo26s-obb.dxnn | 2 | 3 | 26.2 ±1.2 | 13.1 | 85 | 96.1 | 100.0 | 86 | 300~1000 | 453 | ok |
| yolo26m-obb.dxnn | 1 | 3 | 17.2 ±2.5 | 17.2 | 57 | 93.9 | 100.0 | 86 | 200~1000 | 338 | ok |
| yolo26l-obb.dxnn | 1 | 3 | 11.1 ±0.2 | 11.1 | 38 | 95.1 | 100.0 | 86 | 200~700 | 348 | ok |
| yolo26x-obb.dxnn | 1 | 3 | 6.2 ±0.1 | 6.2 | 22 | 93.9 | 100.0 | 86 | 200~800 | 418 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | 1 | 3 | 52.1 ±0.1 | 52.1 | 157 | 93.1 | 100.0 | 71~77 | 1000 | 300 | ok |
| yolo26n-obb.dxnn | 2 | 3 | 52.5 ±0.1 | 26.3 | 165 | 95.9 | 100.0 | 83~84 | 1000 | 437 | ok |
| yolo26s-obb.dxnn | 1 | 3 | 29.2 ±1.8 | 29.2 | 91 | 94.9 | 100.0 | 80~86 | 300~1000 | 313 | ok |
| yolo26m-obb.dxnn | 1 | 3 | 15.4 ±1.2 | 15.4 | 49 | 94.1 | 100.0 | 86 | 200~1000 | 335 | ok |
| yolo26l-obb.dxnn | 1 | 3 | 12.2 ±1.6 | 12.2 | 40 | 95.4 | 100.0 | 86 | 200~1000 | 348 | ok |
| yolo26x-obb.dxnn | 1 | 3 | 6.2 ±0.0 | 6.2 | 21 | 94.3 | 100.0 | 86~87 | 200~700 | 414 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-obb.dxnn | 1 | 52.2 | 1 | 52.1 |
| yolo26s-obb.dxnn | 1 | 30.2 | < 1 | — |

---
*Report generated by dx-benchmark tool*
