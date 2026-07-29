# YOLO26 Benchmark Report

**Generated:** 2026-07-21 20:13:36 (Local)

## Test Timing

| # | Type | Start | End | Duration |
|---|------|-------|-----|----------|
| 1 | run | 2026-07-20 22:48:55 | 2026-07-21 19:23:20 | 20h 34m 25s |

## Executive Summary

### Object Detection

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n.dxnn | ON | 23.40 | 110.4 | 70.0 | 2 |
| yolo26n.dxnn | OFF | 21.54 | 179.6 | 87.8 | 2 |
| yolo26s.dxnn | ON | 30.10 | 110.9 | 69.7 | 2 |
| yolo26s.dxnn | OFF | 30.03 | 130.9 | 88.2 | 2 |
| yolo26m.dxnn | ON | 37.72 | 91.1 | 69.8 | 2 |
| yolo26m.dxnn | OFF | 36.30 | 90.8 | 87.9 | 2 |
| yolo26l.dxnn | ON | 46.64 | 67.3 | 67.5 | 2 |
| yolo26l.dxnn | OFF | 43.19 | 67.4 | 66.8 | 2 |
| yolo26x.dxnn | ON | 75.15 | 38.9 | 38.9 | 1 |
| yolo26x.dxnn | OFF | 70.80 | 38.8 | 38.7 | 1 |

### Pose Estimation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-pose.dxnn | ON | 20.91 | 163.5 | 85.5 | 2 |
| yolo26n-pose.dxnn | OFF | 18.22 | 219.0 | 126.8 | 4 |
| yolo26s-pose.dxnn | ON | 27.06 | 127.0 | 85.6 | 2 |
| yolo26s-pose.dxnn | OFF | 25.41 | 127.0 | 126.4 | 4 |
| yolo26m-pose.dxnn | ON | 34.61 | 89.1 | 85.5 | 2 |
| yolo26m-pose.dxnn | OFF | 32.88 | 89.3 | 89.2 | 2 |
| yolo26l-pose.dxnn | ON | 42.31 | 66.4 | 64.9 | 2 |
| yolo26l-pose.dxnn | OFF | 40.60 | 66.1 | 65.3 | 2 |
| yolo26x-pose.dxnn | ON | 70.32 | 38.1 | 37.8 | 1 |
| yolo26x-pose.dxnn | OFF | 68.67 | 38.3 | 38.0 | 1 |

### Segmentation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-seg.dxnn | ON | 39.52 | 69.6 | 48.6 | 1 |
| yolo26n-seg.dxnn | OFF | 35.05 | 94.3 | 64.3 | 2 |
| yolo26s-seg.dxnn | ON | 50.23 | 69.9 | 48.3 | 1 |
| yolo26s-seg.dxnn | OFF | 44.41 | 95.7 | 63.3 | 2 |
| yolo26m-seg.dxnn | ON | 61.38 | 66.0 | 48.2 | 1 |
| yolo26m-seg.dxnn | OFF | 61.09 | 65.4 | 64.2 | 2 |
| yolo26l-seg.dxnn | ON | 69.76 | 52.4 | 48.2 | 1 |
| yolo26l-seg.dxnn | OFF | 66.33 | 52.4 | 52.4 | 1 |
| yolo26x-seg.dxnn | ON | 112.99 | 28.9 | 30.0 | 1 |
| yolo26x-seg.dxnn | OFF | 106.58 | 29.4 | 29.4 | — |

### Oriented BBox (OBB)

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-obb.dxnn | ON | 36.73 | 74.4 | 74.3 | 2 |
| yolo26n-obb.dxnn | OFF | 36.34 | 74.3 | 74.1 | 2 |
| yolo26s-obb.dxnn | ON | 54.76 | 43.6 | 43.6 | 1 |
| yolo26s-obb.dxnn | OFF | 52.85 | 43.6 | 43.6 | 1 |
| yolo26m-obb.dxnn | ON | 72.30 | 31.8 | 31.9 | 1 |
| yolo26m-obb.dxnn | OFF | 70.99 | 32.0 | 31.9 | 1 |
| yolo26l-obb.dxnn | ON | 93.71 | 23.3 | 23.4 | — |
| yolo26l-obb.dxnn | OFF | 91.58 | 23.4 | 23.4 | — |
| yolo26x-obb.dxnn | ON | 165.67 | 13.5 | 13.6 | — |
| yolo26x-obb.dxnn | OFF | 163.90 | 13.5 | 13.6 | — |

### Classification

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-cls.dxnn | ON | 1.27 | 3518.0 | 194.5 | — |
| yolo26n-cls.dxnn | OFF | 1.27 | 3513.4 | 194.8 | — |
| yolo26s-cls.dxnn | ON | 1.95 | 1905.5 | 195.1 | — |
| yolo26s-cls.dxnn | OFF | 1.96 | 1905.7 | 194.0 | — |
| yolo26m-cls.dxnn | ON | 2.58 | 1341.7 | 194.0 | — |
| yolo26m-cls.dxnn | OFF | 2.60 | 1341.1 | 195.0 | — |
| yolo26l-cls.dxnn | ON | 3.83 | 847.8 | 194.8 | — |
| yolo26l-cls.dxnn | OFF | 3.83 | 848.1 | 194.1 | — |
| yolo26x-cls.dxnn | ON | 6.47 | 450.3 | 194.0 | — |
| yolo26x-cls.dxnn | OFF | 6.41 | 453.2 | 193.6 | — |

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
| NPU SKU | M1 |
| DX-AllSuite | v2.3.3 |
| NPU RT | v3.3.2 |
| NPU Driver (RT) | v2.4.1 |
| NPU Driver (PCIe) | v2.2.0 |
| NPU Firmware | v2.5.6 |
| NPU Memory | LPDDR5 5600 Mbps, 3.92GiB |
| NPU Board | M.2, Rev 1.0 |
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
| yolo26n.dxnn | 110.4 ±0.5 | 7 | 193 | 29.7 | 77.7 | 41~42 | 1000 | ok |
| yolo26s.dxnn | 110.9 ±0.4 | 7 | 196 | 65.3 | 81.8 | 51~52 | 1000 | ok |
| yolo26m.dxnn | 91.1 ±0.4 | 7 | 133 | 91.5 | 100.0 | 58~60 | 1000 | ok |
| yolo26l.dxnn | 67.3 ±0.2 | 5 | 86 | 90.7 | 100.0 | 57~60 | 1000 | ok |
| yolo26x.dxnn | 38.9 ±0.1 | 4 | 53 | 89.1 | 100.0 | 59~63 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n.dxnn | 7 | [3]:95.4 · [4]:111.6 · [5]:111.5 · [6]:111.1 · **[7]:112.7 ★** · [8]:110.1 |
| yolo26s.dxnn | 7 | [3]:75.0 · [4]:97.0 · [5]:109.5 · [6]:111.3 · **[7]:111.6 ★** · [8]:111.6 |
| yolo26m.dxnn | 7 | [3]:64.9 · [4]:79.0 · [5]:91.3 · [6]:91.6 · **[7]:91.9 ★** · [8]:90.8 |
| yolo26l.dxnn | 5 | [3]:50.4 · [4]:63.4 · **[5]:67.4 ★** · [6]:66.2 · [7]:66.4 · [8]:66.5 |
| yolo26x.dxnn | 4 | [3]:31.9 · **[4]:38.9 ★** · [5]:37.5 · [6]:38.0 · [7]:37.9 · [8]:38.2 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n.dxnn | 179.6 ±0.0 | 7 | 108 | 57.0 | 92.2 | 49~50 | 1000 | ok |
| yolo26s.dxnn | 130.9 ±0.1 | 5 | 70 | 90.2 | 100.0 | 54~56 | 1000 | ok |
| yolo26m.dxnn | 90.8 ±0.2 | 6 | 62 | 92.6 | 100.0 | 58~61 | 1000 | ok |
| yolo26l.dxnn | 67.4 ±0.0 | 4 | 41 | 89.6 | 100.0 | 58~61 | 1000 | ok |
| yolo26x.dxnn | 38.8 ±0.2 | 4 | 26 | 91.9 | 100.0 | 60~63 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n.dxnn | 7 | [3]:116.7 · [4]:135.8 · [5]:170.2 · [6]:179.1 · **[7]:179.4 ★** · [8]:179.3 |
| yolo26s.dxnn | 5 | [3]:82.0 · [4]:115.9 · **[5]:130.5 ★** · [6]:129.9 · [7]:129.4 · [8]:130.3 |
| yolo26m.dxnn | 6 | [3]:64.5 · [4]:87.0 · [5]:91.0 · **[6]:91.0 ★** · [7]:90.4 · [8]:90.9 |
| yolo26l.dxnn | 4 | [3]:52.8 · **[4]:67.2 ★** · [5]:65.7 · [6]:66.5 · [7]:66.4 · [8]:66.5 |
| yolo26x.dxnn | 4 | [3]:32.8 · **[4]:38.8 ★** · [5]:38.2 · [6]:38.0 · [7]:38.1 · [8]:38.1 |


#### Pose Estimation

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-pose.dxnn | 163.5 ±0.3 | 8 | 203 | 54.4 | 86.1 | 51 | 1000 | ok |
| yolo26s-pose.dxnn | 127.0 ±0.1 | 5 | 107 | 91.7 | 100.0 | 53~55 | 1000 | ok |
| yolo26m-pose.dxnn | 89.1 ±0.3 | 6 | 83 | 91.9 | 100.0 | 59~62 | 1000 | ok |
| yolo26l-pose.dxnn | 66.4 ±0.0 | 4 | 56 | 90.5 | 100.0 | 58~61 | 1000 | ok |
| yolo26x-pose.dxnn | 38.1 ±0.0 | 4 | 33 | 89.7 | 100.0 | 60~63 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-pose.dxnn | 8 | [3]:117.1 · [4]:146.1 · [5]:162.2 · [6]:164.4 · [7]:160.3 · **[8]:165.0 ★** · [9]:162.1 · [10]:159.6 |
| yolo26s-pose.dxnn | 5 | [3]:83.4 · [4]:109.3 · **[5]:126.9 ★** · [6]:126.6 · [7]:125.5 · [8]:126.3 |
| yolo26m-pose.dxnn | 6 | [3]:66.7 · [4]:84.3 · [5]:89.0 · **[6]:89.4 ★** · [7]:89.1 · [8]:88.9 |
| yolo26l-pose.dxnn | 4 | [3]:53.6 · **[4]:65.9 ★** · [5]:64.4 · [6]:64.6 · [7]:64.9 · [8]:64.8 |
| yolo26x-pose.dxnn | 4 | [3]:33.4 · **[4]:38.1 ★** · [5]:37.3 · [6]:37.4 · [7]:37.3 · [8]:37.4 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-pose.dxnn | 219.0 ±0.1 | 7 | 81 | 92.7 | 100.0 | 51~53 | 1000 | ok |
| yolo26s-pose.dxnn | 127.0 ±0.2 | 5 | 55 | 91.7 | 100.0 | 54~56 | 1000 | ok |
| yolo26m-pose.dxnn | 89.3 ±0.1 | 4 | 36 | 92.1 | 100.0 | 59~62 | 1000 | ok |
| yolo26l-pose.dxnn | 66.1 ±0.0 | 4 | 28 | 89.4 | 100.0 | 58~61 | 1000 | ok |
| yolo26x-pose.dxnn | 38.3 ±0.0 | 4 | 16 | 88.4 | 100.0 | 59~61 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-pose.dxnn | 7 | [3]:123.7 · [4]:167.6 · [5]:196.2 · [6]:217.0 · **[7]:219.0 ★** · [8]:214.3 |
| yolo26s-pose.dxnn | 5 | [3]:85.5 · [4]:122.5 · **[5]:127.1 ★** · [6]:126.5 · [7]:126.7 · [8]:126.0 |
| yolo26m-pose.dxnn | 4 | [3]:67.5 · **[4]:89.3 ★** · [5]:86.5 · [6]:88.0 · [7]:88.7 · [8]:88.9 |
| yolo26l-pose.dxnn | 4 | [3]:58.5 · **[4]:65.9 ★** · [5]:64.1 · [6]:64.7 · [7]:64.8 · [8]:64.9 |
| yolo26x-pose.dxnn | 4 | [3]:33.0 · **[4]:38.2 ★** · [5]:37.3 · [6]:37.2 · [7]:37.2 · [8]:37.4 |


#### Segmentation

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-seg.dxnn | 69.6 ±0.3 | 6 | 245 | 22.3 | 71.7 | 46 | 1000 | ok |
| yolo26s-seg.dxnn | 69.9 ±0.7 | 6 | 243 | 46.8 | 79.4 | 47~48 | 1000 | ok |
| yolo26m-seg.dxnn | 66.0 ±0.1 | 7 | 190 | 91.3 | 100.0 | 58~61 | 1000 | ok |
| yolo26l-seg.dxnn | 52.4 ±0.2 | 6 | 130 | 88.5 | 100.0 | 58~61 | 1000 | ok |
| yolo26x-seg.dxnn | 28.9 ±0.4 | 6 | 75 | 89.0 | 100.0 | 60~63 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-seg.dxnn | 6 | [3]:59.7 · [4]:68.4 · [5]:70.3 · **[6]:70.3 ★** · [7]:69.1 · [8]:69.7 |
| yolo26s-seg.dxnn | 6 | [3]:50.5 · [4]:63.0 · [5]:69.7 · **[6]:70.4 ★** · [7]:69.8 · [8]:68.9 |
| yolo26m-seg.dxnn | 7 | [3]:40.1 · [4]:51.7 · [5]:59.9 · [6]:65.6 · **[7]:65.7 ★** · [8]:65.1 |
| yolo26l-seg.dxnn | 6 | [3]:35.3 · [4]:45.9 · [5]:51.8 · **[6]:52.2 ★** · [7]:52.2 · [8]:50.8 |
| yolo26x-seg.dxnn | 6 | [3]:22.1 · [4]:28.5 · [5]:29.4 · **[6]:29.5 ★** · [7]:28.9 · [8]:28.3 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-seg.dxnn | 94.3 ±2.5 | 7 | 130 | 33.5 | 62.0 | 45 | 1000 | ok |
| yolo26s-seg.dxnn | 95.7 ±0.0 | 7 | 119 | 79.9 | 89.5 | 52~54 | 1000 | ok |
| yolo26m-seg.dxnn | 65.4 ±0.5 | 6 | 97 | 92.6 | 100.0 | 59~63 | 1000 | ok |
| yolo26l-seg.dxnn | 52.4 ±0.2 | 5 | 62 | 91.4 | 100.0 | 58~61 | 1000 | ok |
| yolo26x-seg.dxnn | 29.4 ±0.3 | 8 | 45 | 88.6 | 100.0 | 62~66 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-seg.dxnn | 7 | [3]:74.0 · [4]:75.5 · [5]:95.4 · [6]:95.4 · **[7]:95.5 ★** · [8]:95.4 |
| yolo26s-seg.dxnn | 7 | [3]:63.7 · [4]:68.5 · [5]:88.4 · [6]:95.2 · **[7]:95.4 ★** · [8]:95.4 |
| yolo26m-seg.dxnn | 6 | [3]:47.8 · [4]:59.1 · [5]:65.6 · **[6]:66.4 ★** · [7]:64.9 · [8]:65.2 |
| yolo26l-seg.dxnn | 5 | [3]:41.4 · [4]:49.9 · **[5]:52.4 ★** · [6]:50.8 · [7]:51.8 · [8]:50.9 |
| yolo26x-seg.dxnn | 8 | [3]:24.1 · [4]:28.9 · [5]:27.8 · [6]:29.4 · [7]:28.2 · **[8]:29.6 ★** · [9]:29.5 · [10]:28.3 |


#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-obb.dxnn | 74.4 ±0.2 | 5 | 74 | 90.3 | 100.0 | 51 | 1000 | ok |
| yolo26s-obb.dxnn | 43.6 ±0.0 | 7 | 48 | 90.2 | 100.0 | 52~54 | 1000 | ok |
| yolo26m-obb.dxnn | 31.8 ±0.0 | 9 | 34 | 87.9 | 100.0 | 57~60 | 1000 | ok |
| yolo26l-obb.dxnn | 23.3 ±0.1 | 5 | 26 | 91.5 | 100.0 | 56~59 | 1000 | ok |
| yolo26x-obb.dxnn | 13.5 ±0.0 | 5 | 15 | 84.8 | 100.0 | 59~61 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-obb.dxnn | 5 | [3]:58.5 · [4]:70.4 · **[5]:74.4 ★** · [6]:74.0 · [7]:74.0 · [8]:74.1 |
| yolo26s-obb.dxnn | 7 | [3]:37.9 · [4]:43.4 · [5]:43.0 · [6]:43.5 · **[7]:43.5 ★** · [8]:43.4 |
| yolo26m-obb.dxnn | 9 | [3]:29.2 · [4]:31.8 · [5]:31.6 · [6]:31.8 · [7]:31.8 · [8]:31.8 · **[9]:31.9 ★** · [10]:31.8 |
| yolo26l-obb.dxnn | 5 | [3]:21.7 · [4]:23.3 · **[5]:23.3 ★** · [6]:23.1 · [7]:23.0 · [8]:23.2 |
| yolo26x-obb.dxnn | 5 | [3]:12.8 · [4]:13.5 · **[5]:13.5 ★** · [6]:13.4 · [7]:13.5 · [8]:13.3 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-obb.dxnn | 74.3 ±0.1 | 7 | 38 | 92.1 | 100.0 | 51~52 | 1000 | ok |
| yolo26s-obb.dxnn | 43.6 ±0.0 | 8 | 23 | 89.2 | 100.0 | 53~55 | 1000 | ok |
| yolo26m-obb.dxnn | 32.0 ±0.0 | 4 | 15 | 89.9 | 100.0 | 57~59 | 1000 | ok |
| yolo26l-obb.dxnn | 23.4 ±0.0 | 4 | 11 | 90.4 | 100.0 | 56~58 | 1000 | ok |
| yolo26x-obb.dxnn | 13.5 ±0.0 | 5 | 7 | 85.8 | 100.0 | 58~60 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-obb.dxnn | 7 | [3]:54.5 · [4]:73.9 · [5]:73.2 · [6]:73.9 · **[7]:74.0 ★** · [8]:74.0 |
| yolo26s-obb.dxnn | 8 | [3]:38.3 · [4]:43.4 · [5]:43.0 · [6]:43.5 · [7]:43.5 · **[8]:43.6 ★** · [9]:43.6 · [10]:43.5 |
| yolo26m-obb.dxnn | 4 | [3]:29.7 · **[4]:31.9 ★** · [5]:31.6 · [6]:31.8 · [7]:31.8 · [8]:31.8 |
| yolo26l-obb.dxnn | 4 | [3]:22.2 · **[4]:23.3 ★** · [5]:23.2 · [6]:23.2 · [7]:23.2 · [8]:23.2 |
| yolo26x-obb.dxnn | 5 | [3]:12.7 · [4]:13.4 · **[5]:13.5 ★** · [6]:13.3 · [7]:13.4 · [8]:13.4 |


#### Classification

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-cls.dxnn | 3518.0 ±1.1 | 6 | 60 | 88.7 | 96.2 | 50 | 1000 | ok |
| yolo26s-cls.dxnn | 1905.5 ±1.1 | 6 | 34 | 89.4 | 97.9 | 49~50 | 1000 | ok |
| yolo26m-cls.dxnn | 1341.7 ±0.5 | 7 | 25 | 89.8 | 97.7 | 55~58 | 1000 | ok |
| yolo26l-cls.dxnn | 847.8 ±0.8 | 4 | 15 | 89.6 | 98.5 | 53~55 | 1000 | ok |
| yolo26x-cls.dxnn | 450.3 ±0.8 | 7 | 9 | 89.9 | 99.4 | 56~58 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-cls.dxnn | 6 | [3]:2367.7 · [4]:3137.7 · [5]:3498.9 · **[6]:3533.1 ★** · [7]:3532.3 · [8]:3530.5 |
| yolo26s-cls.dxnn | 6 | [3]:1524.8 · [4]:1874.2 · [5]:1886.4 · **[6]:1909.3 ★** · [7]:1902.7 · [8]:1906.6 |
| yolo26m-cls.dxnn | 7 | [3]:1123.5 · [4]:1339.9 · [5]:1344.4 · [6]:1344.9 · **[7]:1345.9 ★** · [8]:1345.6 |
| yolo26l-cls.dxnn | 4 | [3]:756.0 · **[4]:851.1 ★** · [5]:844.4 · [6]:846.7 · [7]:846.2 · [8]:846.5 |
| yolo26x-cls.dxnn | 7 | [3]:424.2 · [4]:452.1 · [5]:450.5 · [6]:451.0 · **[7]:452.5 ★** · [8]:451.4 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-cls.dxnn | 3513.4 ±7.1 | 6 | 59 | 88.5 | 96.6 | 48~49 | 1000 | ok |
| yolo26s-cls.dxnn | 1905.7 ±0.9 | 6 | 35 | 90.7 | 97.9 | 50~51 | 1000 | ok |
| yolo26m-cls.dxnn | 1341.1 ±1.7 | 7 | 25 | 90.2 | 98.3 | 55~58 | 1000 | ok |
| yolo26l-cls.dxnn | 848.1 ±1.1 | 4 | 16 | 90.9 | 98.4 | 53~55 | 1000 | ok |
| yolo26x-cls.dxnn | 453.2 ±0.1 | 4 | 9 | 90.2 | 99.3 | 56~59 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-cls.dxnn | 6 | [3]:2349.0 · [4]:3124.0 · [5]:3510.3 · **[6]:3533.2 ★** · [7]:3530.7 · [8]:3530.5 |
| yolo26s-cls.dxnn | 6 | [3]:1525.4 · [4]:1876.9 · [5]:1871.6 · **[6]:1915.1 ★** · [7]:1908.6 · [8]:1907.5 |
| yolo26m-cls.dxnn | 7 | [3]:1123.6 · [4]:1339.0 · [5]:1346.5 · [6]:1346.6 · **[7]:1347.2 ★** · [8]:1345.0 |
| yolo26l-cls.dxnn | 4 | [3]:754.2 · **[4]:849.5 ★** · [5]:844.2 · [6]:846.0 · [7]:846.7 · [8]:847.5 |
| yolo26x-cls.dxnn | 4 | [3]:426.2 · **[4]:453.3 ★** · [5]:450.5 · [6]:451.0 · [7]:450.5 · [8]:451.3 |


### Latency (Single-Core, Sync)

#### Object Detection

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n.dxnn | 42.7 ±0.5 | 23.40 | 20.99 | 2.41 | 37 | ok |
| yolo26s.dxnn | 33.2 ±0.4 | 30.10 | 27.82 | 2.28 | 46 | ok |
| yolo26m.dxnn | 26.5 ±0.4 | 37.72 | 35.35 | 2.37 | 48 | ok |
| yolo26l.dxnn | 21.4 ±0.2 | 46.64 | 44.03 | 2.61 | 48 | ok |
| yolo26x.dxnn | 13.3 ±0.1 | 75.15 | 72.70 | 2.45 | 48 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n.dxnn | 46.4 ±0.0 | 21.54 | 21.54 | N/A | 45 | ok |
| yolo26s.dxnn | 33.3 ±0.1 | 30.03 | 30.03 | N/A | 47 | ok |
| yolo26m.dxnn | 27.5 ±0.1 | 36.30 | 36.30 | N/A | 47 | ok |
| yolo26l.dxnn | 23.2 ±0.0 | 43.19 | 43.19 | N/A | 48 | ok |
| yolo26x.dxnn | 14.1 ±0.2 | 70.80 | 70.80 | N/A | 48 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-pose.dxnn | 47.8 ±0.3 | 20.91 | 19.41 | 1.49 | 47 | ok |
| yolo26s-pose.dxnn | 37.0 ±0.1 | 27.06 | 25.55 | 1.51 | 47 | ok |
| yolo26m-pose.dxnn | 28.9 ±0.3 | 34.61 | 33.09 | 1.53 | 48 | ok |
| yolo26l-pose.dxnn | 23.6 ±0.0 | 42.31 | 40.85 | 1.47 | 48 | ok |
| yolo26x-pose.dxnn | 14.2 ±0.0 | 70.32 | 68.83 | 1.49 | 49 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-pose.dxnn | 54.9 ±0.1 | 18.22 | 18.22 | N/A | 46 | ok |
| yolo26s-pose.dxnn | 39.4 ±0.2 | 25.41 | 25.41 | N/A | 47 | ok |
| yolo26m-pose.dxnn | 30.4 ±0.1 | 32.88 | 32.88 | N/A | 48 | ok |
| yolo26l-pose.dxnn | 24.6 ±0.0 | 40.60 | 40.60 | N/A | 48 | ok |
| yolo26x-pose.dxnn | 14.6 ±0.0 | 68.67 | 68.67 | N/A | 48 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-seg.dxnn | 25.3 ±0.3 | 39.52 | 36.41 | 3.10 | 47 | ok |
| yolo26s-seg.dxnn | 19.9 ±0.7 | 50.23 | 47.35 | 2.88 | 42 | ok |
| yolo26m-seg.dxnn | 16.3 ±0.1 | 61.38 | 58.33 | 3.05 | 47 | ok |
| yolo26l-seg.dxnn | 14.3 ±0.2 | 69.76 | 66.78 | 2.97 | 47 | ok |
| yolo26x-seg.dxnn | 8.9 ±0.4 | 112.99 | 109.96 | 3.04 | 48 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-seg.dxnn | 28.5 ±2.5 | 35.05 | 35.05 | N/A | 41 | ok |
| yolo26s-seg.dxnn | 22.5 ±0.0 | 44.41 | 44.41 | N/A | 47 | ok |
| yolo26m-seg.dxnn | 16.4 ±0.5 | 61.09 | 61.09 | N/A | 47 | ok |
| yolo26l-seg.dxnn | 15.1 ±0.2 | 66.33 | 66.33 | N/A | 47 | ok |
| yolo26x-seg.dxnn | 9.4 ±0.3 | 106.58 | 106.58 | N/A | 48 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-obb.dxnn | 27.2 ±0.2 | 36.73 | 35.09 | 1.64 | 47 | ok |
| yolo26s-obb.dxnn | 18.3 ±0.0 | 54.76 | 53.03 | 1.72 | 47 | ok |
| yolo26m-obb.dxnn | 13.8 ±0.0 | 72.30 | 70.60 | 1.70 | 48 | ok |
| yolo26l-obb.dxnn | 10.7 ±0.1 | 93.71 | 91.90 | 1.81 | 48 | ok |
| yolo26x-obb.dxnn | 6.0 ±0.0 | 165.67 | 163.86 | 1.81 | 49 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-obb.dxnn | 27.5 ±0.1 | 36.34 | 36.34 | N/A | 47 | ok |
| yolo26s-obb.dxnn | 18.9 ±0.0 | 52.85 | 52.85 | N/A | 47 | ok |
| yolo26m-obb.dxnn | 14.1 ±0.0 | 70.99 | 70.99 | N/A | 48 | ok |
| yolo26l-obb.dxnn | 10.9 ±0.0 | 91.58 | 91.58 | N/A | 48 | ok |
| yolo26x-obb.dxnn | 6.1 ±0.0 | 163.90 | 163.90 | N/A | 49 | ok |

#### Classification

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-cls.dxnn | 784.8 ±1.1 | 1.27 | 1.27 | N/A | 47 | ok |
| yolo26s-cls.dxnn | 513.7 ±1.1 | 1.95 | 1.95 | N/A | 43 | ok |
| yolo26m-cls.dxnn | 388.3 ±0.5 | 2.58 | 2.58 | N/A | 45 | ok |
| yolo26l-cls.dxnn | 261.3 ±0.8 | 3.83 | 3.83 | N/A | 46 | ok |
| yolo26x-cls.dxnn | 154.6 ±0.8 | 6.47 | 6.47 | N/A | 46 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-cls.dxnn | 785.8 ±7.1 | 1.27 | 1.27 | N/A | 45 | ok |
| yolo26s-cls.dxnn | 510.8 ±0.8 | 1.96 | 1.96 | N/A | 45 | ok |
| yolo26m-cls.dxnn | 385.2 ±1.7 | 2.60 | 2.60 | N/A | 46 | ok |
| yolo26l-cls.dxnn | 260.8 ±1.1 | 3.83 | 3.83 | N/A | 46 | ok |
| yolo26x-cls.dxnn | 156.1 ±0.1 | 6.41 | 6.41 | N/A | 47 | ok |

## E2E Pipeline (Single-Stream)

### Object Detection

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | avdec_h264 | 3455 | 3 | 70.0 ±0.3 | 49.38 | 341 | 18.6 | 58.9 | 43 | 1000 | 285 | ok |
| yolo26s.dxnn | avdec_h264 | 3455 | 3 | 69.7 ±0.5 | 49.56 | 342 | 34.8 | 72.1 | 49~50 | 1000 | 303 | ok |
| yolo26m.dxnn | avdec_h264 | 3455 | 3 | 69.8 ±0.1 | 49.50 | 342 | 57.9 | 86.3 | 54~56 | 1000 | 325 | ok |
| yolo26l.dxnn | avdec_h264 | 3455 | 3 | 67.5 ±0.0 | 51.23 | 244 | 93.9 | 100.0 | 56~61 | 1000 | 334 | ok |
| yolo26x.dxnn | avdec_h264 | 3455 | 3 | 38.9 ±0.2 | 88.74 | 113 | 96.2 | 100.0 | 63~69 | 1000 | 387 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | avdec_h264 | 3455 | 3 | 87.8 ±0.5 | 39.37 | 308 | 23.3 | 70.4 | 46 | 1000 | 316 | ok |
| yolo26s.dxnn | avdec_h264 | 3455 | 3 | 88.2 ±0.8 | 39.19 | 308 | 46.9 | 78.3 | 50~51 | 1000 | 331 | ok |
| yolo26m.dxnn | avdec_h264 | 3455 | 3 | 87.9 ±0.3 | 39.29 | 305 | 87.3 | 99.1 | 54~58 | 1000 | 353 | ok |
| yolo26l.dxnn | avdec_h264 | 3455 | 3 | 66.8 ±0.1 | 51.69 | 214 | 93.5 | 100.0 | 56~61 | 1000 | 341 | ok |
| yolo26x.dxnn | avdec_h264 | 3455 | 3 | 38.7 ±0.2 | 89.20 | 118 | 95.8 | 100.0 | 62~69 | 1000 | 401 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n.dxnn | 70.0 | 87.8 | -17.8 | -20.3% |
| yolo26s.dxnn | 69.7 | 88.2 | -18.5 | -20.9% |
| yolo26m.dxnn | 69.8 | 87.9 | -18.1 | -20.6% |
| yolo26l.dxnn | 67.5 | 66.8 | +0.6 | +0.9% |
| yolo26x.dxnn | 38.9 | 38.7 | +0.2 | +0.5% |

### Pose Estimation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | avdec_h264 | 3455 | 3 | 85.5 ±0.4 | 40.41 | 349 | 25.1 | 68.4 | 47 | 1000 | 270 | ok |
| yolo26s-pose.dxnn | avdec_h264 | 3455 | 3 | 85.6 ±0.2 | 40.35 | 348 | 49.5 | 79.1 | 50~51 | 1000 | 290 | ok |
| yolo26m-pose.dxnn | avdec_h264 | 3455 | 3 | 85.5 ±0.3 | 40.43 | 339 | 87.5 | 99.2 | 55~60 | 1000 | 316 | ok |
| yolo26l-pose.dxnn | avdec_h264 | 3455 | 3 | 64.9 ±0.0 | 53.21 | 175 | 93.7 | 100.0 | 58~62 | 1000 | 328 | ok |
| yolo26x-pose.dxnn | avdec_h264 | 3455 | 3 | 37.8 ±0.5 | 91.32 | 93 | 94.3 | 100.0 | 63~70 | 1000 | 382 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | avdec_h264 | 3455 | 3 | 126.8 ±0.2 | 27.24 | 316 | 40.7 | 70.4 | 49 | 1000 | 251 | ok |
| yolo26s-pose.dxnn | avdec_h264 | 3455 | 3 | 126.4 ±0.2 | 27.33 | 302 | 90.2 | 100.0 | 51~53 | 1000 | 285 | ok |
| yolo26m-pose.dxnn | avdec_h264 | 3455 | 3 | 89.2 ±0.2 | 38.75 | 168 | 93.0 | 100.0 | 55~60 | 1000 | 304 | ok |
| yolo26l-pose.dxnn | avdec_h264 | 3455 | 3 | 65.3 ±0.3 | 52.93 | 124 | 93.6 | 100.0 | 57~62 | 1000 | 316 | ok |
| yolo26x-pose.dxnn | avdec_h264 | 3455 | 3 | 38.0 ±0.5 | 90.93 | 72 | 95.1 | 100.0 | 61~68 | 1000 | 371 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-pose.dxnn | 85.5 | 126.8 | -41.3 | -32.6% |
| yolo26s-pose.dxnn | 85.6 | 126.4 | -40.8 | -32.3% |
| yolo26m-pose.dxnn | 85.5 | 89.2 | -3.7 | -4.2% |
| yolo26l-pose.dxnn | 64.9 | 65.3 | -0.3 | -0.5% |
| yolo26x-pose.dxnn | 37.8 | 38.0 | -0.2 | -0.4% |

### Segmentation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | avdec_h264 | 3455 | 3 | 48.6 ±0.2 | 71.14 | 340 | 15.9 | 52.3 | 43~44 | 1000 | 376 | ok |
| yolo26s-seg.dxnn | avdec_h264 | 3455 | 3 | 48.3 ±0.0 | 71.52 | 346 | 30.2 | 75.1 | 46~47 | 1000 | 399 | ok |
| yolo26m-seg.dxnn | avdec_h264 | 3455 | 3 | 48.2 ±0.0 | 71.61 | 341 | 57.4 | 89.3 | 56~59 | 1000 | 423 | ok |
| yolo26l-seg.dxnn | avdec_h264 | 3455 | 3 | 48.2 ±0.1 | 71.64 | 324 | 82.7 | 92.6 | 58~63 | 1000 | 430 | ok |
| yolo26x-seg.dxnn | avdec_h264 | 3455 | 3 | 30.0 ±0.0 | 115.03 | 153 | 96.9 | 100.0 | 67~75 | 1000 | 493 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | avdec_h264 | 3455 | 3 | 64.3 ±0.7 | 53.70 | 349 | 21.2 | 66.3 | 43 | 1000 | 433 | ok |
| yolo26s-seg.dxnn | avdec_h264 | 3455 | 3 | 63.3 ±0.1 | 54.55 | 353 | 42.1 | 75.6 | 49~50 | 1000 | 448 | ok |
| yolo26m-seg.dxnn | avdec_h264 | 3455 | 3 | 64.2 ±0.7 | 53.80 | 347 | 90.0 | 100.0 | 58~63 | 1000 | 475 | ok |
| yolo26l-seg.dxnn | avdec_h264 | 3455 | 3 | 52.4 ±0.2 | 65.94 | 244 | 92.2 | 100.0 | 59~64 | 1000 | 439 | ok |
| yolo26x-seg.dxnn | avdec_h264 | 3455 | 3 | 29.4 ±0.2 | 117.46 | 123 | 96.0 | 100.0 | 69~75 | 1000 | 510 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-seg.dxnn | 48.6 | 64.3 | -15.8 | -24.5% |
| yolo26s-seg.dxnn | 48.3 | 63.3 | -15.0 | -23.7% |
| yolo26m-seg.dxnn | 48.2 | 64.2 | -16.0 | -24.9% |
| yolo26l-seg.dxnn | 48.2 | 52.4 | -4.2 | -8.0% |
| yolo26x-seg.dxnn | 30.0 | 29.4 | +0.6 | +2.1% |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | avdec_h264 | 2640 | 3 | 74.3 ±0.0 | 35.55 | 329 | 89.5 | 100.0 | 45~47 | 1000 | 297 | ok |
| yolo26s-obb.dxnn | avdec_h264 | 2640 | 3 | 43.6 ±0.0 | 60.56 | 141 | 93.9 | 100.0 | 53~56 | 1000 | 317 | ok |
| yolo26m-obb.dxnn | avdec_h264 | 2640 | 3 | 31.9 ±0.0 | 82.69 | 98 | 93.8 | 100.0 | 59~65 | 1000 | 340 | ok |
| yolo26l-obb.dxnn | avdec_h264 | 2640 | 3 | 23.4 ±0.0 | 112.83 | 72 | 95.1 | 100.0 | 61~66 | 1000 | 347 | ok |
| yolo26x-obb.dxnn | avdec_h264 | 2640 | 3 | 13.6 ±0.0 | 194.56 | 40 | 92.8 | 100.0 | 68~72 | 1000 | 409 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | avdec_h264 | 2640 | 3 | 74.1 ±0.1 | 35.61 | 231 | 92.3 | 100.0 | 50~51 | 1000 | 299 | ok |
| yolo26s-obb.dxnn | avdec_h264 | 2640 | 3 | 43.6 ±0.0 | 60.50 | 128 | 93.4 | 100.0 | 53~56 | 1000 | 314 | ok |
| yolo26m-obb.dxnn | avdec_h264 | 2640 | 3 | 31.9 ±0.1 | 82.74 | 95 | 94.5 | 100.0 | 58~64 | 1000 | 333 | ok |
| yolo26l-obb.dxnn | avdec_h264 | 2640 | 3 | 23.4 ±0.0 | 112.96 | 70 | 95.4 | 100.0 | 61~64 | 1000 | 349 | ok |
| yolo26x-obb.dxnn | avdec_h264 | 2640 | 3 | 13.6 ±0.0 | 194.48 | 42 | 92.6 | 100.0 | 66~71 | 1000 | 404 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-obb.dxnn | 74.3 | 74.1 | +0.1 | +0.2% |
| yolo26s-obb.dxnn | 43.6 | 43.6 | -0.0 | -0.1% |
| yolo26m-obb.dxnn | 31.9 | 31.9 | +0.0 | +0.0% |
| yolo26l-obb.dxnn | 23.4 | 23.4 | +0.0 | +0.1% |
| yolo26x-obb.dxnn | 13.6 | 13.6 | +0.0 | +0.0% |

### Classification

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-cls.dxnn | avdec_h264 | 3455 | 3 | 194.5 ±0.6 | 17.77 | 278 | 4.5 | 14.1 | 45~46 | 1000 | 180 | ok |
| yolo26s-cls.dxnn | avdec_h264 | 3455 | 3 | 195.1 ±0.4 | 17.71 | 277 | 8.2 | 25.9 | 45~46 | 1000 | 190 | ok |
| yolo26m-cls.dxnn | avdec_h264 | 3455 | 3 | 194.0 ±0.3 | 17.81 | 276 | 11.1 | 33.8 | 46~47 | 1000 | 191 | ok |
| yolo26l-cls.dxnn | avdec_h264 | 3455 | 3 | 194.8 ±0.5 | 17.73 | 276 | 18.3 | 45.8 | 47 | 1000 | 209 | ok |
| yolo26x-cls.dxnn | avdec_h264 | 3455 | 3 | 194.0 ±0.4 | 17.81 | 274 | 32.7 | 62.9 | 48 | 1000 | 228 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-cls.dxnn | avdec_h264 | 3455 | 3 | 194.8 ±0.3 | 17.74 | 277 | 4.4 | 14.1 | 43~46 | 1000 | 168 | ok |
| yolo26s-cls.dxnn | avdec_h264 | 3455 | 3 | 194.0 ±0.5 | 17.81 | 276 | 8.0 | 25.5 | 45~46 | 1000 | 182 | ok |
| yolo26m-cls.dxnn | avdec_h264 | 3455 | 3 | 195.0 ±0.1 | 17.72 | 278 | 11.3 | 34.2 | 46~47 | 1000 | 192 | ok |
| yolo26l-cls.dxnn | avdec_h264 | 3455 | 3 | 194.1 ±0.6 | 17.80 | 275 | 17.9 | 44.8 | 46~47 | 1000 | 206 | ok |
| yolo26x-cls.dxnn | avdec_h264 | 3455 | 3 | 193.6 ±0.5 | 17.85 | 275 | 33.0 | 63.4 | 48 | 1000 | 228 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-cls.dxnn | 194.5 | 194.8 | -0.3 | -0.2% |
| yolo26s-cls.dxnn | 195.1 | 194.0 | +1.1 | +0.6% |
| yolo26m-cls.dxnn | 194.0 | 195.0 | -0.9 | -0.5% |
| yolo26l-cls.dxnn | 194.8 | 194.1 | +0.7 | +0.4% |
| yolo26x-cls.dxnn | 194.0 | 193.6 | +0.4 | +0.2% |

## E2E Pipeline (Multi-Stream)

### Object Detection

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | 2 | 3 | 68.9 ±0.9 | 34.4 | 336 | 18.8 | 59.7 | 44~45 | 1000 | 421 | ok |
| yolo26n.dxnn | 3 | 3 | 68.3 ±0.3 | 22.8 | 335 | 18.8 | 58.0 | 45 | 1000 | 529 | ok |
| yolo26s.dxnn | 2 | 3 | 69.0 ±0.2 | 34.5 | 337 | 35.8 | 72.6 | 51 | 1000 | 437 | ok |
| yolo26s.dxnn | 3 | 3 | 68.7 ±0.5 | 22.9 | 336 | 36.1 | 74.5 | 51 | 1000 | 539 | ok |
| yolo26m.dxnn | 2 | 3 | 67.9 ±0.2 | 33.9 | 338 | 56.8 | 85.3 | 60~62 | 1000 | 458 | ok |
| yolo26m.dxnn | 3 | 3 | 67.9 ±0.4 | 22.6 | 335 | 57.6 | 86.5 | 63~64 | 1000 | 564 | ok |
| yolo26l.dxnn | 2 | 3 | 67.3 ±0.1 | 33.7 | 277 | 95.3 | 100.0 | 67~69 | 1000 | 470 | ok |
| yolo26l.dxnn | 3 | 3 | 67.3 ±0.0 | 22.4 | 275 | 95.9 | 100.0 | 71~72 | 1000 | 571 | ok |
| yolo26x.dxnn | 1 | 3 | 38.9 ±0.2 | 38.9 | 113 | 96.2 | 100.0 | 63~69 | 1000 | 387 | ok |
| yolo26x.dxnn | 2 | 3 | 38.9 ±0.1 | 19.5 | 106 | 97.7 | 100.0 | 74~76 | 1000 | 525 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | 2 | 3 | 87.9 ±0.6 | 43.9 | 310 | 24.2 | 70.6 | 46 | 1000 | 459 | ok |
| yolo26n.dxnn | 3 | 3 | 87.2 ±0.3 | 29.1 | 307 | 24.4 | 70.4 | 46 | 1000 | 568 | ok |
| yolo26s.dxnn | 2 | 3 | 87.6 ±0.3 | 43.8 | 312 | 48.2 | 79.7 | 52~53 | 1000 | 472 | ok |
| yolo26s.dxnn | 3 | 3 | 87.7 ±0.5 | 29.2 | 307 | 48.8 | 78.9 | 54 | 1000 | 581 | ok |
| yolo26m.dxnn | 2 | 3 | 87.5 ±0.7 | 43.7 | 305 | 87.7 | 96.4 | 64~67 | 1000 | 493 | ok |
| yolo26m.dxnn | 3 | 3 | 86.6 ±0.5 | 28.9 | 307 | 88.3 | 99.7 | 70 | 1000 | 600 | ok |
| yolo26l.dxnn | 2 | 3 | 66.7 ±0.0 | 33.3 | 217 | 96.6 | 100.0 | 67~70 | 1000 | 487 | ok |
| yolo26l.dxnn | 3 | 3 | 66.8 ±0.1 | 22.3 | 219 | 97.4 | 100.0 | 72~73 | 1000 | 582 | ok |
| yolo26x.dxnn | 1 | 3 | 38.7 ±0.2 | 38.7 | 118 | 95.8 | 100.0 | 62~69 | 1000 | 401 | ok |
| yolo26x.dxnn | 2 | 3 | 38.8 ±0.2 | 19.4 | 114 | 97.4 | 100.0 | 74~76 | 1000 | 536 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n.dxnn | 2 | 34.4 | 2 | 43.9 |
| yolo26s.dxnn | 2 | 34.5 | 2 | 43.8 |
| yolo26m.dxnn | 2 | 33.9 | 2 | 43.7 |
| yolo26l.dxnn | 2 | 33.7 | 2 | 33.3 |
| yolo26x.dxnn | 1 | 38.9 | 1 | 38.7 |

### Pose Estimation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | 2 | 3 | 83.3 ±0.9 | 41.6 | 347 | 24.4 | 66.3 | 47 | 1000 | 417 | ok |
| yolo26n-pose.dxnn | 3 | 3 | 84.2 ±0.5 | 28.1 | 346 | 25.4 | 71.8 | 46 | 1000 | 522 | ok |
| yolo26s-pose.dxnn | 2 | 3 | 82.4 ±0.7 | 41.2 | 346 | 48.3 | 80.4 | 52~53 | 1000 | 431 | ok |
| yolo26s-pose.dxnn | 3 | 3 | 82.5 ±0.1 | 27.5 | 346 | 48.6 | 82.1 | 54 | 1000 | 537 | ok |
| yolo26m-pose.dxnn | 2 | 3 | 83.8 ±1.4 | 41.9 | 339 | 86.7 | 97.9 | 62~66 | 1000 | 451 | ok |
| yolo26m-pose.dxnn | 3 | 3 | 82.0 ±0.4 | 27.3 | 340 | 84.6 | 98.3 | 69~70 | 1000 | 557 | ok |
| yolo26l-pose.dxnn | 2 | 3 | 65.1 ±0.1 | 32.5 | 169 | 95.6 | 100.0 | 68~71 | 1000 | 459 | ok |
| yolo26l-pose.dxnn | 3 | 3 | 65.2 ±0.1 | 21.8 | 174 | 97.2 | 100.0 | 73 | 1000 | 570 | ok |
| yolo26x-pose.dxnn | 1 | 3 | 37.8 ±0.5 | 37.8 | 93 | 94.3 | 100.0 | 63~70 | 1000 | 382 | ok |
| yolo26x-pose.dxnn | 2 | 3 | 38.1 ±0.2 | 19.1 | 91 | 96.4 | 100.0 | 72~75 | 1000 | 522 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | 4 | 3 | 130.2 ±1.0 | 32.5 | 377 | 46.2 | 72.9 | 50 | 1000 | 627 | ok |
| yolo26n-pose.dxnn | 5 | 3 | 129.4 ±0.6 | 25.9 | 376 | 45.9 | 73.8 | 50 | 1000 | 731 | ok |
| yolo26s-pose.dxnn | 4 | 3 | 125.3 ±0.2 | 31.3 | 336 | 93.8 | 100.0 | 59~61 | 1000 | 633 | ok |
| yolo26s-pose.dxnn | 5 | 3 | 124.6 ±0.0 | 24.9 | 341 | 93.7 | 100.0 | 62 | 1000 | 733 | ok |
| yolo26m-pose.dxnn | 2 | 3 | 89.2 ±0.2 | 44.6 | 180 | 96.5 | 100.0 | 66~70 | 1000 | 440 | ok |
| yolo26m-pose.dxnn | 3 | 3 | 89.1 ±0.3 | 29.7 | 175 | 96.2 | 100.0 | 73~75 | 1000 | 547 | ok |
| yolo26l-pose.dxnn | 2 | 3 | 65.2 ±0.1 | 32.6 | 129 | 95.6 | 100.0 | 65~70 | 1000 | 451 | ok |
| yolo26l-pose.dxnn | 3 | 3 | 65.2 ±0.1 | 21.7 | 131 | 97.4 | 100.0 | 73~74 | 1000 | 558 | ok |
| yolo26x-pose.dxnn | 1 | 3 | 38.0 ±0.5 | 38.0 | 72 | 95.1 | 100.0 | 61~68 | 1000 | 371 | ok |
| yolo26x-pose.dxnn | 2 | 3 | 38.4 ±0.1 | 19.2 | 72 | 96.6 | 100.0 | 75~76 | 1000 | 508 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-pose.dxnn | 2 | 41.6 | 4 | 32.5 |
| yolo26s-pose.dxnn | 2 | 41.2 | 4 | 31.3 |
| yolo26m-pose.dxnn | 2 | 41.9 | 2 | 44.6 |
| yolo26l-pose.dxnn | 2 | 32.5 | 2 | 32.6 |
| yolo26x-pose.dxnn | 1 | 37.8 | 1 | 38.0 |

### Segmentation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | 1 | 3 | 48.6 ±0.2 | 48.6 | 340 | 15.9 | 52.3 | 43~44 | 1000 | 376 | ok |
| yolo26n-seg.dxnn | 2 | 3 | 48.2 ±0.6 | 24.1 | 338 | 16.0 | 51.1 | 42 | 1000 | 524 | ok |
| yolo26s-seg.dxnn | 1 | 3 | 48.3 ±0.0 | 48.3 | 346 | 30.2 | 75.1 | 46~47 | 1000 | 399 | ok |
| yolo26s-seg.dxnn | 2 | 3 | 47.8 ±0.7 | 23.9 | 338 | 30.5 | 75.1 | 47~48 | 1000 | 542 | ok |
| yolo26m-seg.dxnn | 1 | 3 | 48.2 ±0.0 | 48.2 | 341 | 57.4 | 89.3 | 56~59 | 1000 | 423 | ok |
| yolo26m-seg.dxnn | 2 | 3 | 46.7 ±0.1 | 23.4 | 340 | 55.9 | 87.7 | 62~63 | 1000 | 570 | ok |
| yolo26l-seg.dxnn | 1 | 3 | 48.2 ±0.1 | 48.2 | 324 | 82.7 | 92.6 | 58~63 | 1000 | 430 | ok |
| yolo26l-seg.dxnn | 2 | 3 | 47.1 ±0.2 | 23.6 | 326 | 80.7 | 95.8 | 68 | 1000 | 573 | ok |
| yolo26x-seg.dxnn | 1 | 3 | 30.0 ±0.0 | 30.0 | 153 | 96.9 | 100.0 | 67~75 | 1000 | 493 | ok |
| yolo26x-seg.dxnn | 2 | 3 | 27.8 ±0.3 | 13.9 | 124 | 96.8 | 100.0 | 77~78 | 800~1000 | 642 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | 2 | 3 | 64.0 ±0.6 | 32.0 | 349 | 21.7 | 66.3 | 43 | 1000 | 582 | ok |
| yolo26n-seg.dxnn | 3 | 3 | 64.3 ±0.1 | 21.4 | 343 | 22.1 | 69.0 | 43 | 1000 | 697 | ok |
| yolo26s-seg.dxnn | 2 | 3 | 63.6 ±0.5 | 31.8 | 345 | 43.5 | 76.6 | 51 | 1000 | 600 | ok |
| yolo26s-seg.dxnn | 3 | 3 | 63.6 ±0.6 | 21.2 | 344 | 43.9 | 76.5 | 51 | 1000 | 711 | ok |
| yolo26m-seg.dxnn | 2 | 3 | 62.5 ±0.3 | 31.3 | 354 | 88.2 | 99.4 | 68~70 | 1000 | 625 | ok |
| yolo26m-seg.dxnn | 3 | 3 | 62.1 ±0.4 | 20.7 | 354 | 87.3 | 99.1 | 72 | 1000 | 738 | ok |
| yolo26l-seg.dxnn | 1 | 3 | 52.4 ±0.2 | 52.4 | 244 | 92.2 | 100.0 | 59~64 | 1000 | 439 | ok |
| yolo26l-seg.dxnn | 2 | 3 | 52.2 ±0.4 | 26.1 | 241 | 95.7 | 100.0 | 70~73 | 1000 | 608 | ok |
| yolo26x-seg.dxnn | 1 | 3 | 29.4 ±0.2 | 29.4 | 123 | 96.0 | 100.0 | 69~75 | 1000 | 510 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-seg.dxnn | 1 | 48.6 | 2 | 32.0 |
| yolo26s-seg.dxnn | 1 | 48.3 | 2 | 31.8 |
| yolo26m-seg.dxnn | 1 | 48.2 | 2 | 31.3 |
| yolo26l-seg.dxnn | 1 | 48.2 | 1 | 52.4 |
| yolo26x-seg.dxnn | 1 | 30.0 | < 1 | — |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | 2 | 3 | 73.8 ±0.1 | 36.9 | 342 | 92.2 | 100.0 | 51~53 | 1000 | 440 | ok |
| yolo26n-obb.dxnn | 3 | 3 | 73.6 ±0.6 | 24.5 | 342 | 92.5 | 100.0 | 55 | 1000 | 543 | ok |
| yolo26s-obb.dxnn | 1 | 3 | 43.6 ±0.0 | 43.6 | 141 | 93.9 | 100.0 | 53~56 | 1000 | 317 | ok |
| yolo26s-obb.dxnn | 2 | 3 | 43.6 ±0.0 | 21.8 | 141 | 96.0 | 100.0 | 57~59 | 1000 | 456 | ok |
| yolo26m-obb.dxnn | 1 | 3 | 31.9 ±0.0 | 31.9 | 98 | 93.8 | 100.0 | 59~65 | 1000 | 340 | ok |
| yolo26m-obb.dxnn | 2 | 3 | 31.9 ±0.0 | 16.0 | 99 | 96.3 | 100.0 | 70~71 | 1000 | 478 | ok |
| yolo26l-obb.dxnn | 1 | 3 | 23.4 ±0.0 | 23.4 | 72 | 95.1 | 100.0 | 61~66 | 1000 | 347 | ok |
| yolo26x-obb.dxnn | 1 | 3 | 13.6 ±0.0 | 13.6 | 40 | 92.8 | 100.0 | 68~72 | 1000 | 409 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | 2 | 3 | 74.2 ±0.1 | 37.1 | 239 | 95.3 | 100.0 | 53~55 | 1000 | 439 | ok |
| yolo26n-obb.dxnn | 3 | 3 | 74.2 ±0.0 | 24.8 | 237 | 96.4 | 100.0 | 56 | 1000 | 539 | ok |
| yolo26s-obb.dxnn | 1 | 3 | 43.6 ±0.0 | 43.6 | 128 | 93.4 | 100.0 | 53~56 | 1000 | 314 | ok |
| yolo26s-obb.dxnn | 2 | 3 | 43.7 ±0.0 | 21.9 | 133 | 96.1 | 100.0 | 58~59 | 1000 | 451 | ok |
| yolo26m-obb.dxnn | 1 | 3 | 31.9 ±0.1 | 31.9 | 95 | 94.5 | 100.0 | 58~64 | 1000 | 333 | ok |
| yolo26m-obb.dxnn | 2 | 3 | 31.9 ±0.0 | 16.0 | 95 | 96.2 | 100.0 | 70~71 | 1000 | 474 | ok |
| yolo26l-obb.dxnn | 1 | 3 | 23.4 ±0.0 | 23.4 | 70 | 95.4 | 100.0 | 61~64 | 1000 | 349 | ok |
| yolo26x-obb.dxnn | 1 | 3 | 13.6 ±0.0 | 13.6 | 42 | 92.6 | 100.0 | 66~71 | 1000 | 404 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-obb.dxnn | 2 | 36.9 | 2 | 37.1 |
| yolo26s-obb.dxnn | 1 | 43.6 | 1 | 43.6 |
| yolo26m-obb.dxnn | 1 | 31.9 | 1 | 31.9 |

---
*Report generated by dx-benchmark tool*
