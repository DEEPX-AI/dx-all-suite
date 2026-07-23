# YOLO26 Benchmark Report

**Generated:** 2026-07-02 06:48:13 (Local)

## Test Timing

| # | Type | Start | End | Duration |
|---|------|-------|-----|----------|
| 1 | run | 2026-07-01 10:20:40 | 2026-07-02 06:48:13 | 20h 27m 33s |

## Executive Summary

### Object Detection

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n.dxnn | ON | 30.28 | 131.4 | 126.4 | 4 |
| yolo26n.dxnn | OFF | 26.15 | 146.7 | 141.2 | 4 |
| yolo26s.dxnn | ON | 38.61 | 104.3 | 99.6 | 3 |
| yolo26s.dxnn | OFF | 34.62 | 105.1 | 103.0 | 3 |
| yolo26m.dxnn | ON | 46.63 | 76.6 | 75.8 | 2 |
| yolo26m.dxnn | OFF | 42.42 | 76.5 | 76.3 | 2 |
| yolo26l.dxnn | ON | 55.32 | 57.3 | 57.1 | 1 |
| yolo26l.dxnn | OFF | 51.13 | 57.3 | 57.3 | 1 |
| yolo26x.dxnn | ON | 85.47 | 32.9 | 32.5 | 1 |
| yolo26x.dxnn | OFF | 81.60 | 32.9 | 32.4 | 1 |

### Pose Estimation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-pose.dxnn | ON | 27.00 | 163.8 | 149.6 | 5 |
| yolo26n-pose.dxnn | OFF | 23.57 | 164.8 | 159.8 | 5 |
| yolo26s-pose.dxnn | ON | 34.75 | 102.5 | 101.6 | 3 |
| yolo26s-pose.dxnn | OFF | 31.76 | 102.6 | 102.0 | 3 |
| yolo26m-pose.dxnn | ON | 43.18 | 74.9 | 74.7 | 2 |
| yolo26m-pose.dxnn | OFF | 39.89 | 74.9 | 74.8 | 2 |
| yolo26l-pose.dxnn | ON | 52.65 | 56.1 | 56.2 | 1 |
| yolo26l-pose.dxnn | OFF | 49.14 | 56.1 | 56.2 | 1 |
| yolo26x-pose.dxnn | ON | 82.99 | 32.3 | 31.6 | 1 |
| yolo26x-pose.dxnn | OFF | 79.62 | 32.3 | 31.6 | 1 |

### Segmentation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-seg.dxnn | ON | 43.70 | 85.8 | 85.2 | 2 |
| yolo26n-seg.dxnn | OFF | 39.29 | 96.4 | 93.1 | 3 |
| yolo26s-seg.dxnn | ON | 54.27 | 70.4 | 68.1 | 2 |
| yolo26s-seg.dxnn | OFF | 49.80 | 76.6 | 74.6 | 2 |
| yolo26m-seg.dxnn | ON | 68.85 | 56.0 | 54.7 | 1 |
| yolo26m-seg.dxnn | OFF | 64.88 | 56.0 | 55.1 | 1 |
| yolo26l-seg.dxnn | ON | 77.38 | 45.5 | 44.3 | 1 |
| yolo26l-seg.dxnn | OFF | 73.59 | 45.5 | 44.6 | 1 |
| yolo26x-seg.dxnn | ON | 119.52 | 25.7 | 21.2 | — |
| yolo26x-seg.dxnn | OFF | 115.67 | 25.7 | 21.3 | — |

### Oriented BBox (OBB)

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-obb.dxnn | ON | 45.66 | 59.5 | 59.5 | 1 |
| yolo26n-obb.dxnn | OFF | 42.19 | 59.5 | 59.5 | 1 |
| yolo26s-obb.dxnn | ON | 64.25 | 36.5 | 36.5 | 1 |
| yolo26s-obb.dxnn | OFF | 60.76 | 36.5 | 36.5 | 1 |
| yolo26m-obb.dxnn | ON | 83.36 | 27.4 | 27.4 | — |
| yolo26m-obb.dxnn | OFF | 80.12 | 27.4 | 27.4 | — |
| yolo26l-obb.dxnn | ON | 105.24 | 20.5 | 20.4 | — |
| yolo26l-obb.dxnn | OFF | 101.75 | 20.5 | 20.4 | — |
| yolo26x-obb.dxnn | ON | 182.52 | 11.9 | 11.1 | — |
| yolo26x-obb.dxnn | OFF | 178.86 | 11.9 | 11.1 | — |

### Classification

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-cls.dxnn | ON | 1.50 | 2666.6 | 289.9 | — |
| yolo26n-cls.dxnn | OFF | 1.53 | 2661.6 | 290.1 | — |
| yolo26s-cls.dxnn | ON | 2.20 | 1601.8 | 289.6 | — |
| yolo26s-cls.dxnn | OFF | 2.16 | 1601.8 | 290.8 | — |
| yolo26m-cls.dxnn | ON | 2.71 | 1281.4 | 291.7 | — |
| yolo26m-cls.dxnn | OFF | 2.77 | 1281.5 | 290.3 | — |
| yolo26l-cls.dxnn | ON | 4.90 | 794.4 | 291.5 | — |
| yolo26l-cls.dxnn | OFF | 4.62 | 794.2 | 286.3 | — |
| yolo26x-cls.dxnn | ON | 7.87 | 401.4 | 291.1 | — |
| yolo26x-cls.dxnn | OFF | 7.93 | 401.6 | 289.8 | — |

## Environment

| Item | Value |
|------|-------|
| Product | DX-AIPlayer-N97 |
| Hostname | deepx |
| OS | Ubuntu 24.04.4 LTS |
| Kernel | 6.17.0-23-generic |
| CPU | Intel(R) N97 |
| CPU Cores | 4 |
| RAM | 7.5 GB |
| NPU SKU | M1 |
| NPU RT | v3.2.0 |
| NPU Driver (RT) | v2.1.0 |
| NPU Driver (PCIe) | v2.0.1 |
| NPU Firmware | v2.5.0 |
| NPU Memory | LPDDR5 5600 Mbps, 3.92GiB |
| NPU Board | M.2, Rev 1.0 |
| NPU PCIe | Gen3 X2 [03:00:00] |

### Tools

| Tool | Available | Version |
|------|-----------|---------|
| run_model | Yes | DXRT v3.2.0 run_model |
| gst-launch-1.0 | Yes | gst-launch-1.0 version 1.24.2 |
| gst-inspect-1.0 | Yes | gst-inspect-1.0 version 1.24.2 |
| dxtop | Yes | DX-TOP 1.0.1 |
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
| Version | v2 |
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
| Cooldown Max Time | 1800.0 s |
| NPU Warmup | 1.0 s |
| NPU Drain | 0.5 s |

## Benchmarked Models

| Model | Task | Input Size | NPU Memory (MB) | ORT CPU Offload | Multi-Stream Sweep |
|-------|------|------------|:----------------:|:---------------:|:------------------:|
| yolo26n.dxnn | Object Detection | 640×640 | 140.1 | Yes | ✅ |
| yolo26s.dxnn | Object Detection | 640×640 | 147.2 | Yes | ✅ |
| yolo26m.dxnn | Object Detection | 640×640 | 148.4 | Yes | ✅ |
| yolo26l.dxnn | Object Detection | 640×640 | 162.6 | Yes | ✅ |
| yolo26x.dxnn | Object Detection | 640×640 | 271.1 | Yes | ✅ |
| yolo26n-pose.dxnn | Pose Estimation | 640×640 | 151.5 | Yes | ✅ |
| yolo26s-pose.dxnn | Pose Estimation | 640×640 | 159.0 | Yes | ✅ |
| yolo26m-pose.dxnn | Pose Estimation | 640×640 | 152.3 | Yes | ✅ |
| yolo26l-pose.dxnn | Pose Estimation | 640×640 | 158.2 | Yes | ✅ |
| yolo26x-pose.dxnn | Pose Estimation | 640×640 | 253.3 | Yes | ✅ |
| yolo26n-seg.dxnn | Segmentation | 640×640 | 160.7 | Yes | ✅ |
| yolo26s-seg.dxnn | Segmentation | 640×640 | 168.4 | Yes | ✅ |
| yolo26m-seg.dxnn | Segmentation | 640×640 | 187.2 | Yes | ✅ |
| yolo26l-seg.dxnn | Segmentation | 640×640 | 192.0 | Yes | ✅ |
| yolo26x-seg.dxnn | Segmentation | 640×640 | 308.1 | Yes | ✅ |
| yolo26n-obb.dxnn | Oriented BBox (OBB) | 1024×1024 | 357.9 | Yes | ✅ |
| yolo26s-obb.dxnn | Oriented BBox (OBB) | 1024×1024 | 365.7 | Yes | ✅ |
| yolo26m-obb.dxnn | Oriented BBox (OBB) | 1024×1024 | 369.6 | Yes | ✅ |
| yolo26l-obb.dxnn | Oriented BBox (OBB) | 1024×1024 | 369.8 | Yes | ✅ |
| yolo26x-obb.dxnn | Oriented BBox (OBB) | 1024×1024 | 567.7 | Yes | ✅ |
| yolo26n-cls.dxnn | Classification | 224×224 | 10.8 | No | — |
| yolo26s-cls.dxnn | Classification | 224×224 | 14.6 | No | — |
| yolo26m-cls.dxnn | Classification | 224×224 | 17.7 | No | — |
| yolo26l-cls.dxnn | Classification | 224×224 | 20.4 | No | — |
| yolo26x-cls.dxnn | Classification | 224×224 | 44.7 | No | — |

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

#### Object Detection

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n.dxnn | 131.4 ±0.2 | 218 | 62.2 | 84.2 | 50~53 | 1000 | ok |
| yolo26s.dxnn | 104.3 ±0.0 | 143 | 89.9 | 99.9 | 59~62 | 1000 | ok |
| yolo26m.dxnn | 76.6 ±0.0 | 113 | 89.6 | 100.0 | 61~65 | 1000 | ok |
| yolo26l.dxnn | 57.3 ±0.0 | 83 | 90.0 | 100.0 | 61~64 | 1000 | ok |
| yolo26x.dxnn | 32.9 ±0.0 | 52 | 90.7 | 100.0 | 62~66 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n.dxnn | 146.7 ±0.4 | 173 | 73.6 | 87.5 | 59~60 | 1000 | ok |
| yolo26s.dxnn | 105.1 ±0.1 | 112 | 92.3 | 100.0 | 59~62 | 1000 | ok |
| yolo26m.dxnn | 76.5 ±0.1 | 85 | 90.5 | 100.0 | 61~65 | 1000 | ok |
| yolo26l.dxnn | 57.3 ±0.0 | 61 | 91.9 | 100.0 | 61~65 | 1000 | ok |
| yolo26x.dxnn | 32.9 ±0.0 | 40 | 89.7 | 100.0 | 62~66 | 1000 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-pose.dxnn | 163.8 ±0.1 | 155 | 89.5 | 100.0 | 59~61 | 1000 | ok |
| yolo26s-pose.dxnn | 102.5 ±0.1 | 113 | 90.7 | 100.0 | 59~62 | 1000 | ok |
| yolo26m-pose.dxnn | 74.9 ±0.0 | 78 | 92.3 | 100.0 | 61~65 | 1000 | ok |
| yolo26l-pose.dxnn | 56.1 ±0.0 | 62 | 89.2 | 100.0 | 62~65 | 1000 | ok |
| yolo26x-pose.dxnn | 32.3 ±0.0 | 41 | 89.1 | 100.0 | 63~66 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-pose.dxnn | 164.8 ±0.2 | 125 | 91.5 | 100.0 | 59~61 | 1000 | ok |
| yolo26s-pose.dxnn | 102.6 ±0.0 | 79 | 91.6 | 100.0 | 59~62 | 1000 | ok |
| yolo26m-pose.dxnn | 74.9 ±0.0 | 59 | 92.3 | 100.0 | 61~65 | 1000 | ok |
| yolo26l-pose.dxnn | 56.1 ±0.0 | 47 | 91.9 | 100.0 | 62~65 | 1000 | ok |
| yolo26x-pose.dxnn | 32.3 ±0.0 | 31 | 91.2 | 100.0 | 63~66 | 1000 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-seg.dxnn | 85.8 ±0.9 | 253 | 46.9 | 72.9 | 58~59 | 1000 | ok |
| yolo26s-seg.dxnn | 70.4 ±0.7 | 217 | 69.2 | 92.1 | 59~62 | 1000 | ok |
| yolo26m-seg.dxnn | 56.0 ±0.0 | 125 | 88.4 | 100.0 | 63~67 | 1000 | ok |
| yolo26l-seg.dxnn | 45.5 ±0.0 | 102 | 90.0 | 100.0 | 63~67 | 1000 | ok |
| yolo26x-seg.dxnn | 25.7 ±0.0 | 61 | 88.3 | 100.0 | 64~68 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-seg.dxnn | 96.4 ±0.4 | 238 | 53.6 | 76.1 | 58~60 | 1000 | ok |
| yolo26s-seg.dxnn | 76.6 ±0.3 | 186 | 77.8 | 95.0 | 60~62 | 1000 | ok |
| yolo26m-seg.dxnn | 56.0 ±0.0 | 104 | 88.6 | 100.0 | 63~67 | 1000 | ok |
| yolo26l-seg.dxnn | 45.5 ±0.0 | 83 | 88.5 | 100.0 | 63~67 | 1000 | ok |
| yolo26x-seg.dxnn | 25.7 ±0.0 | 51 | 87.2 | 100.0 | 64~68 | 1000 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-obb.dxnn | 59.5 ±0.0 | 71 | 90.1 | 100.0 | 59~61 | 1000 | ok |
| yolo26s-obb.dxnn | 36.5 ±0.0 | 49 | 91.3 | 100.0 | 60~62 | 1000 | ok |
| yolo26m-obb.dxnn | 27.4 ±0.0 | 39 | 92.5 | 100.0 | 62~65 | 1000 | ok |
| yolo26l-obb.dxnn | 20.5 ±0.0 | 29 | 88.9 | 100.0 | 62~65 | 1000 | ok |
| yolo26x-obb.dxnn | 11.9 ±0.0 | 17 | 90.7 | 100.0 | 63~67 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-obb.dxnn | 59.5 ±0.0 | 55 | 91.4 | 100.0 | 59~61 | 1000 | ok |
| yolo26s-obb.dxnn | 36.5 ±0.0 | 38 | 91.3 | 100.0 | 59~62 | 1000 | ok |
| yolo26m-obb.dxnn | 27.4 ±0.0 | 29 | 88.5 | 100.0 | 62~65 | 1000 | ok |
| yolo26l-obb.dxnn | 20.5 ±0.0 | 22 | 91.5 | 100.0 | 62~65 | 1000 | ok |
| yolo26x-obb.dxnn | 11.9 ±0.0 | 13 | 90.0 | 100.0 | 63~67 | 1000 | ok |

#### Classification

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-cls.dxnn | 2666.6 ±0.5 | 85 | 90.0 | 97.8 | 58~59 | 1000 | ok |
| yolo26s-cls.dxnn | 1601.8 ±1.2 | 48 | 91.1 | 98.4 | 59~60 | 1000 | ok |
| yolo26m-cls.dxnn | 1281.4 ±1.1 | 39 | 91.4 | 98.9 | 61~64 | 1000 | ok |
| yolo26l-cls.dxnn | 794.4 ±0.4 | 25 | 90.3 | 99.5 | 60~62 | 1000 | ok |
| yolo26x-cls.dxnn | 401.4 ±0.4 | 15 | 91.3 | 100.0 | 61~64 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-cls.dxnn | 2661.6 ±9.1 | 86 | 90.8 | 97.8 | 58~59 | 1000 | ok |
| yolo26s-cls.dxnn | 1601.8 ±0.2 | 49 | 89.9 | 98.0 | 59~60 | 1000 | ok |
| yolo26m-cls.dxnn | 1281.5 ±0.8 | 38 | 91.0 | 98.8 | 60~64 | 1000 | ok |
| yolo26l-cls.dxnn | 794.2 ±0.7 | 25 | 91.1 | 99.4 | 60~62 | 1000 | ok |
| yolo26x-cls.dxnn | 401.6 ±0.2 | 15 | 90.6 | 100.0 | 61~64 | 1000 | ok |

### Latency (Single-Core, Sync)

#### Object Detection

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n.dxnn | 33.0 | 30.28 | 26.46 | 3.82 | 47 | ok |
| yolo26s.dxnn | 25.9 | 38.61 | 34.71 | 3.90 | 56 | ok |
| yolo26m.dxnn | 21.4 | 46.63 | 42.65 | 3.98 | 56 | ok |
| yolo26l.dxnn | 18.1 | 55.32 | 51.35 | 3.97 | 57 | ok |
| yolo26x.dxnn | 11.7 | 85.47 | 81.51 | 3.96 | 57 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n.dxnn | 38.2 | 26.15 | 26.15 | 56 | ok |
| yolo26s.dxnn | 28.9 | 34.62 | 34.62 | 56 | ok |
| yolo26m.dxnn | 23.6 | 42.42 | 42.42 | 57 | ok |
| yolo26l.dxnn | 19.6 | 51.13 | 51.13 | 57 | ok |
| yolo26x.dxnn | 12.3 | 81.60 | 81.60 | 57 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-pose.dxnn | 37.0 | 27.00 | 24.08 | 2.92 | 56 | ok |
| yolo26s-pose.dxnn | 28.8 | 34.75 | 31.87 | 2.88 | 56 | ok |
| yolo26m-pose.dxnn | 23.2 | 43.18 | 40.28 | 2.90 | 56 | ok |
| yolo26l-pose.dxnn | 19.0 | 52.65 | 49.70 | 2.95 | 57 | ok |
| yolo26x-pose.dxnn | 12.1 | 82.99 | 80.02 | 2.96 | 57 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-pose.dxnn | 42.4 | 23.57 | 23.57 | 56 | ok |
| yolo26s-pose.dxnn | 31.5 | 31.76 | 31.76 | 56 | ok |
| yolo26m-pose.dxnn | 25.1 | 39.89 | 39.89 | 57 | ok |
| yolo26l-pose.dxnn | 20.4 | 49.14 | 49.14 | 57 | ok |
| yolo26x-pose.dxnn | 12.6 | 79.62 | 79.62 | 57 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-seg.dxnn | 22.9 | 43.70 | 40.15 | 3.55 | 56 | ok |
| yolo26s-seg.dxnn | 18.4 | 54.27 | 50.74 | 3.53 | 56 | ok |
| yolo26m-seg.dxnn | 14.5 | 68.85 | 65.26 | 3.60 | 57 | ok |
| yolo26l-seg.dxnn | 12.9 | 77.38 | 73.83 | 3.55 | 57 | ok |
| yolo26x-seg.dxnn | 8.4 | 119.52 | 115.96 | 3.56 | 58 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-seg.dxnn | 25.4 | 39.29 | 39.29 | 56 | ok |
| yolo26s-seg.dxnn | 20.1 | 49.80 | 49.80 | 56 | ok |
| yolo26m-seg.dxnn | 15.4 | 64.88 | 64.88 | 57 | ok |
| yolo26l-seg.dxnn | 13.6 | 73.59 | 73.59 | 57 | ok |
| yolo26x-seg.dxnn | 8.6 | 115.67 | 115.67 | 58 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-obb.dxnn | 21.9 | 45.66 | 42.41 | 3.25 | 56 | ok |
| yolo26s-obb.dxnn | 15.6 | 64.25 | 61.05 | 3.20 | 56 | ok |
| yolo26m-obb.dxnn | 12.0 | 83.36 | 80.11 | 3.25 | 57 | ok |
| yolo26l-obb.dxnn | 9.5 | 105.24 | 101.97 | 3.27 | 58 | ok |
| yolo26x-obb.dxnn | 5.5 | 182.52 | 179.19 | 3.33 | 59 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-obb.dxnn | 23.7 | 42.19 | 42.19 | 56 | ok |
| yolo26s-obb.dxnn | 16.5 | 60.76 | 60.76 | 56 | ok |
| yolo26m-obb.dxnn | 12.5 | 80.12 | 80.12 | 57 | ok |
| yolo26l-obb.dxnn | 9.8 | 101.75 | 101.75 | 58 | ok |
| yolo26x-obb.dxnn | 5.6 | 178.86 | 178.86 | 59 | ok |

#### Classification

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-cls.dxnn | 668.0 | 1.50 | 1.50 | N/A | 56 | ok |
| yolo26s-cls.dxnn | 454.2 | 2.20 | 2.20 | N/A | 56 | ok |
| yolo26m-cls.dxnn | 369.3 | 2.71 | 2.71 | N/A | 56 | ok |
| yolo26l-cls.dxnn | 204.1 | 4.90 | 4.90 | N/A | 56 | ok |
| yolo26x-cls.dxnn | 127.1 | 7.87 | 7.87 | N/A | 56 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-cls.dxnn | 655.5 | 1.53 | 1.53 | 56 | ok |
| yolo26s-cls.dxnn | 462.6 | 2.16 | 2.16 | 56 | ok |
| yolo26m-cls.dxnn | 361.4 | 2.77 | 2.77 | 56 | ok |
| yolo26l-cls.dxnn | 216.6 | 4.62 | 4.62 | 56 | ok |
| yolo26x-cls.dxnn | 126.0 | 7.93 | 7.93 | 56 | ok |

## E2E Pipeline (Single-Stream)

### Object Detection

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | vah264dec | 3455 | 3 | 126.4 ±1.6 | 27.34 | 255 | 58.0 | 80.6 | 55~56 | 1000 | 252 | ok |
| yolo26s.dxnn | vah264dec | 3455 | 3 | 99.6 ±0.2 | 34.69 | 189 | 85.3 | 98.2 | 63~66 | 1000 | 262 | ok |
| yolo26m.dxnn | vah264dec | 3455 | 3 | 75.8 ±0.1 | 45.58 | 137 | 93.2 | 100.0 | 69~73 | 1000 | 283 | ok |
| yolo26l.dxnn | vah264dec | 3455 | 3 | 57.1 ±0.0 | 60.48 | 109 | 94.3 | 100.0 | 69~73 | 1000 | 294 | ok |
| yolo26x.dxnn | vah264dec | 3455 | 3 | 32.5 ±0.7 | 106.17 | 66 | 96.4 | 100.0 | 74~80 | 1000 | 356 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | vah264dec | 3455 | 3 | 141.2 ±0.5 | 24.47 | 266 | 68.0 | 86.7 | 61~62 | 1000 | 261 | ok |
| yolo26s.dxnn | vah264dec | 3455 | 3 | 103.0 ±0.1 | 33.54 | 205 | 89.0 | 100.0 | 64~66 | 1000 | 275 | ok |
| yolo26m.dxnn | vah264dec | 3455 | 3 | 76.3 ±0.1 | 45.27 | 151 | 92.8 | 100.0 | 69~72 | 1000 | 287 | ok |
| yolo26l.dxnn | vah264dec | 3455 | 3 | 57.3 ±0.0 | 60.33 | 117 | 94.4 | 100.0 | 69~74 | 1000 | 296 | ok |
| yolo26x.dxnn | vah264dec | 3455 | 3 | 32.4 ±0.9 | 106.80 | 71 | 96.4 | 100.0 | 75~80 | 1000 | 357 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n.dxnn | 126.4 | 141.2 | -14.8 | -10.5% |
| yolo26s.dxnn | 99.6 | 103.0 | -3.4 | -3.3% |
| yolo26m.dxnn | 75.8 | 76.3 | -0.5 | -0.7% |
| yolo26l.dxnn | 57.1 | 57.3 | -0.1 | -0.2% |
| yolo26x.dxnn | 32.5 | 32.4 | +0.2 | +0.6% |

### Pose Estimation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | vah264dec | 3455 | 3 | 149.6 ±0.4 | 23.09 | 245 | 79.5 | 91.9 | 62~63 | 1000 | 235 | ok |
| yolo26s-pose.dxnn | vah264dec | 3455 | 3 | 101.6 ±0.3 | 34.01 | 146 | 91.7 | 100.0 | 64~66 | 1000 | 250 | ok |
| yolo26m-pose.dxnn | vah264dec | 3455 | 3 | 74.7 ±0.1 | 46.24 | 112 | 94.3 | 100.0 | 69~73 | 1000 | 272 | ok |
| yolo26l-pose.dxnn | vah264dec | 3455 | 3 | 56.2 ±0.0 | 61.48 | 87 | 94.9 | 100.0 | 70~75 | 1000 | 282 | ok |
| yolo26x-pose.dxnn | vah264dec | 3455 | 3 | 31.6 ±1.0 | 109.51 | 54 | 95.8 | 100.0 | 76~81 | 1000 | 362 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | vah264dec | 3455 | 3 | 159.8 ±0.5 | 21.62 | 181 | 83.2 | 98.9 | 62~63 | 1000 | 223 | ok |
| yolo26s-pose.dxnn | vah264dec | 3455 | 3 | 102.0 ±0.1 | 33.87 | 123 | 91.5 | 100.0 | 64~66 | 1000 | 238 | ok |
| yolo26m-pose.dxnn | vah264dec | 3455 | 3 | 74.8 ±0.1 | 46.17 | 94 | 94.5 | 100.0 | 69~73 | 1000 | 260 | ok |
| yolo26l-pose.dxnn | vah264dec | 3455 | 3 | 56.2 ±0.0 | 61.47 | 75 | 95.1 | 100.0 | 70~74 | 1000 | 268 | ok |
| yolo26x-pose.dxnn | vah264dec | 3455 | 3 | 31.6 ±1.0 | 109.19 | 46 | 95.8 | 100.0 | 76~81 | 1000 | 362 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-pose.dxnn | 149.6 | 159.8 | -10.2 | -6.4% |
| yolo26s-pose.dxnn | 101.6 | 102.0 | -0.4 | -0.4% |
| yolo26m-pose.dxnn | 74.7 | 74.8 | -0.1 | -0.2% |
| yolo26l-pose.dxnn | 56.2 | 56.2 | -0.0 | -0.0% |
| yolo26x-pose.dxnn | 31.6 | 31.6 | -0.1 | -0.3% |

### Segmentation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | vah264dec | 3455 | 3 | 85.2 ±0.4 | 40.56 | 293 | 44.7 | 69.7 | 61~63 | 1000 | 355 | ok |
| yolo26s-seg.dxnn | vah264dec | 3455 | 3 | 68.1 ±0.3 | 50.74 | 244 | 68.3 | 87.7 | 65~68 | 1000 | 369 | ok |
| yolo26m-seg.dxnn | vah264dec | 3455 | 3 | 54.7 ±1.5 | 63.14 | 163 | 91.9 | 100.0 | 75~81 | 1000 | 387 | ok |
| yolo26l-seg.dxnn | vah264dec | 3455 | 3 | 44.3 ±1.5 | 77.93 | 126 | 94.8 | 100.0 | 75~81 | 1000 | 397 | ok |
| yolo26x-seg.dxnn | vah264dec | 3455 | 3 | 21.2 ±2.9 | 162.78 | 64 | 93.2 | 100.0 | 82~84 | 600~1000 | 466 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | vah264dec | 3455 | 3 | 93.1 ±0.2 | 37.12 | 306 | 50.7 | 71.3 | 61~63 | 1000 | 381 | ok |
| yolo26s-seg.dxnn | vah264dec | 3455 | 3 | 74.6 ±0.1 | 46.31 | 244 | 75.6 | 91.7 | 66~69 | 1000 | 388 | ok |
| yolo26m-seg.dxnn | vah264dec | 3455 | 3 | 55.1 ±1.5 | 62.65 | 160 | 94.5 | 100.0 | 75~80 | 1000 | 403 | ok |
| yolo26l-seg.dxnn | vah264dec | 3455 | 3 | 44.6 ±1.4 | 77.53 | 127 | 94.5 | 100.0 | 75~81 | 1000 | 406 | ok |
| yolo26x-seg.dxnn | vah264dec | 3455 | 3 | 21.3 ±2.8 | 162.15 | 64 | 92.5 | 100.0 | 82~84 | 400~1000 | 476 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-seg.dxnn | 85.2 | 93.1 | -7.9 | -8.5% |
| yolo26s-seg.dxnn | 68.1 | 74.6 | -6.5 | -8.7% |
| yolo26m-seg.dxnn | 54.7 | 55.1 | -0.4 | -0.8% |
| yolo26l-seg.dxnn | 44.3 | 44.6 | -0.2 | -0.5% |
| yolo26x-seg.dxnn | 21.2 | 21.3 | -0.1 | -0.4% |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | vah264dec | 2640 | 3 | 59.5 ±0.0 | 44.38 | 108 | 93.1 | 100.0 | 63~65 | 1000 | 272 | ok |
| yolo26s-obb.dxnn | vah264dec | 2640 | 3 | 36.5 ±0.0 | 72.34 | 74 | 95.0 | 100.0 | 66~69 | 1000 | 288 | ok |
| yolo26m-obb.dxnn | vah264dec | 2640 | 3 | 27.4 ±0.0 | 96.25 | 60 | 95.8 | 100.0 | 72~77 | 1000 | 317 | ok |
| yolo26l-obb.dxnn | vah264dec | 2640 | 3 | 20.4 ±0.2 | 129.09 | 47 | 95.9 | 100.0 | 74~78 | 1000 | 320 | ok |
| yolo26x-obb.dxnn | vah264dec | 2640 | 3 | 11.1 ±0.4 | 237.41 | 25 | 93.5 | 100.0 | 80~83 | 800~1000 | 393 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | vah264dec | 2640 | 3 | 59.5 ±0.1 | 44.41 | 110 | 92.6 | 100.0 | 63~65 | 1000 | 259 | ok |
| yolo26s-obb.dxnn | vah264dec | 2640 | 3 | 36.5 ±0.0 | 72.38 | 77 | 95.5 | 100.0 | 66~69 | 1000 | 287 | ok |
| yolo26m-obb.dxnn | vah264dec | 2640 | 3 | 27.4 ±0.0 | 96.26 | 61 | 95.4 | 100.0 | 73~77 | 1000 | 299 | ok |
| yolo26l-obb.dxnn | vah264dec | 2640 | 3 | 20.4 ±0.3 | 129.21 | 47 | 95.9 | 100.0 | 74~79 | 1000 | 320 | ok |
| yolo26x-obb.dxnn | vah264dec | 2640 | 3 | 11.1 ±0.4 | 237.51 | 25 | 93.4 | 100.0 | 80~84 | 800~1000 | 377 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-obb.dxnn | 59.5 | 59.5 | +0.0 | +0.1% |
| yolo26s-obb.dxnn | 36.5 | 36.5 | +0.0 | +0.1% |
| yolo26m-obb.dxnn | 27.4 | 27.4 | +0.0 | +0.0% |
| yolo26l-obb.dxnn | 20.4 | 20.4 | +0.0 | +0.1% |
| yolo26x-obb.dxnn | 11.1 | 11.1 | +0.0 | +0.0% |

### Classification

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-cls.dxnn | vah264dec | 3455 | 3 | 289.9 ±1.1 | 11.92 | 84 | 7.4 | 28.1 | 57~58 | 1000 | 135 | ok |
| yolo26s-cls.dxnn | vah264dec | 3455 | 3 | 289.6 ±0.9 | 11.93 | 84 | 12.7 | 47.8 | 58~59 | 1000 | 121 | ok |
| yolo26m-cls.dxnn | vah264dec | 3455 | 3 | 291.7 ±0.9 | 11.85 | 83 | 16.7 | 53.4 | 61~62 | 1000 | 131 | ok |
| yolo26l-cls.dxnn | vah264dec | 3455 | 3 | 291.5 ±0.3 | 11.85 | 83 | 26.4 | 69.0 | 61 | 1000 | 139 | ok |
| yolo26x-cls.dxnn | vah264dec | 3455 | 3 | 291.1 ±0.9 | 11.87 | 83 | 55.8 | 85.4 | 63~64 | 1000 | 213 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-cls.dxnn | vah264dec | 3455 | 3 | 290.1 ±0.7 | 11.91 | 84 | 7.5 | 28.2 | 57~58 | 1000 | 114 | ok |
| yolo26s-cls.dxnn | vah264dec | 3455 | 3 | 290.8 ±0.7 | 11.88 | 83 | 13.0 | 47.2 | 58~59 | 1000 | 121 | ok |
| yolo26m-cls.dxnn | vah264dec | 3455 | 3 | 290.3 ±0.3 | 11.90 | 83 | 16.4 | 53.9 | 61~62 | 1000 | 131 | ok |
| yolo26l-cls.dxnn | vah264dec | 3455 | 3 | 286.3 ±1.7 | 12.07 | 84 | 27.3 | 69.2 | 61 | 1000 | 136 | ok |
| yolo26x-cls.dxnn | vah264dec | 3455 | 3 | 289.8 ±1.1 | 11.92 | 83 | 55.5 | 85.3 | 63~64 | 1000 | 213 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-cls.dxnn | 289.9 | 290.1 | -0.1 | -0.0% |
| yolo26s-cls.dxnn | 289.6 | 290.8 | -1.2 | -0.4% |
| yolo26m-cls.dxnn | 291.7 | 290.3 | +1.4 | +0.5% |
| yolo26l-cls.dxnn | 291.5 | 286.3 | +5.2 | +1.8% |
| yolo26x-cls.dxnn | 291.1 | 289.8 | +1.2 | +0.4% |

## E2E Pipeline (Multi-Stream)

### Object Detection

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | 4 | 3 | 128.1 ±0.3 | 32.0 | 265 | 63.8 | 80.0 | 62~66 | 1000 | 404 | ok |
| yolo26n.dxnn | 5 | 3 | 127.8 ±0.6 | 25.6 | 265 | 64.2 | 80.9 | 69~70 | 1000 | 432 | ok |
| yolo26s.dxnn | 3 | 3 | 99.5 ±0.1 | 33.2 | 201 | 89.2 | 98.2 | 70~73 | 1000 | 375 | ok |
| yolo26s.dxnn | 4 | 3 | 99.8 ±0.1 | 24.9 | 202 | 89.4 | 98.6 | 76~77 | 1000 | 419 | ok |
| yolo26m.dxnn | 2 | 3 | 73.1 ±2.5 | 36.5 | 144 | 94.9 | 100.0 | 78~80 | 1000 | 354 | ok |
| yolo26m.dxnn | 3 | 3 | 69.7 ±0.2 | 23.2 | 140 | 95.9 | 100.0 | 83~84 | 800~1000 | 397 | ok |
| yolo26l.dxnn | 1 | 3 | 57.1 ±0.0 | 57.1 | 109 | 94.3 | 100.0 | 69~73 | 1000 | 294 | ok |
| yolo26l.dxnn | 2 | 3 | 54.5 ±1.8 | 27.3 | 111 | 96.7 | 100.0 | 78~80 | 1000 | 364 | ok |
| yolo26x.dxnn | 1 | 3 | 32.5 ±0.7 | 32.5 | 66 | 96.4 | 100.0 | 74~80 | 1000 | 356 | ok |
| yolo26x.dxnn | 2 | 3 | 29.1 ±0.7 | 14.6 | 63 | 95.1 | 100.0 | 84 | 600~1000 | 426 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | 4 | 3 | 139.8 ±0.5 | 34.9 | 275 | 71.9 | 86.3 | 66~69 | 1000 | 422 | ok |
| yolo26n.dxnn | 5 | 3 | 140.1 ±0.2 | 28.0 | 275 | 72.9 | 87.0 | 71~73 | 1000 | 459 | ok |
| yolo26s.dxnn | 3 | 3 | 103.0 ±0.2 | 34.3 | 213 | 93.9 | 100.0 | 71~74 | 1000 | 392 | ok |
| yolo26s.dxnn | 4 | 3 | 102.7 ±0.6 | 25.7 | 213 | 95.0 | 100.0 | 77~78 | 1000 | 425 | ok |
| yolo26m.dxnn | 2 | 3 | 73.4 ±2.7 | 36.7 | 154 | 96.1 | 100.0 | 78~80 | 1000 | 361 | ok |
| yolo26m.dxnn | 3 | 3 | 70.1 ±0.1 | 23.4 | 148 | 96.8 | 100.0 | 83~84 | 1000 | 403 | ok |
| yolo26l.dxnn | 1 | 3 | 57.3 ±0.0 | 57.3 | 117 | 94.4 | 100.0 | 69~74 | 1000 | 296 | ok |
| yolo26l.dxnn | 2 | 3 | 54.3 ±1.7 | 27.1 | 116 | 96.5 | 100.0 | 79~81 | 1000 | 370 | ok |
| yolo26x.dxnn | 1 | 3 | 32.4 ±0.9 | 32.4 | 71 | 96.4 | 100.0 | 75~80 | 1000 | 357 | ok |
| yolo26x.dxnn | 2 | 3 | 29.0 ±0.6 | 14.5 | 67 | 94.5 | 100.0 | 84 | 800~1000 | 429 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n.dxnn | 4 | 32.0 | 4 | 34.9 |
| yolo26s.dxnn | 3 | 33.2 | 3 | 34.3 |
| yolo26m.dxnn | 2 | 36.5 | 2 | 36.7 |
| yolo26l.dxnn | 1 | 57.1 | 1 | 57.3 |
| yolo26x.dxnn | 1 | 32.5 | 1 | 32.4 |

### Pose Estimation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | 4 | 3 | 152.5 ±0.1 | 38.1 | 256 | 85.3 | 93.7 | 67~70 | 1000 | 395 | ok |
| yolo26n-pose.dxnn | 5 | 3 | 152.8 ±0.1 | 30.6 | 256 | 86.1 | 94.7 | 72~74 | 1000 | 426 | ok |
| yolo26n-pose.dxnn | 6 | 3 | 152.3 ±0.2 | 25.4 | 256 | 85.6 | 94.0 | 75 | 1000 | 471 | ok |
| yolo26s-pose.dxnn | 3 | 3 | 101.8 ±0.1 | 33.9 | 160 | 95.6 | 100.0 | 71~74 | 1000 | 366 | ok |
| yolo26s-pose.dxnn | 4 | 3 | 101.9 ±0.1 | 25.5 | 161 | 96.5 | 100.0 | 76~77 | 1000 | 406 | ok |
| yolo26m-pose.dxnn | 2 | 3 | 71.6 ±2.7 | 35.8 | 116 | 96.2 | 100.0 | 78~81 | 1000 | 345 | ok |
| yolo26m-pose.dxnn | 3 | 3 | 68.7 ±0.0 | 22.9 | 113 | 98.0 | 100.0 | 83~84 | 1000 | 385 | ok |
| yolo26l-pose.dxnn | 1 | 3 | 56.2 ±0.0 | 56.2 | 87 | 94.9 | 100.0 | 70~75 | 1000 | 282 | ok |
| yolo26l-pose.dxnn | 2 | 3 | 52.6 ±1.0 | 26.3 | 87 | 96.7 | 100.0 | 80~82 | 1000 | 354 | ok |
| yolo26x-pose.dxnn | 1 | 3 | 31.6 ±1.0 | 31.6 | 54 | 95.8 | 100.0 | 76~81 | 1000 | 362 | ok |
| yolo26x-pose.dxnn | 2 | 3 | 27.5 ±0.6 | 13.7 | 50 | 94.3 | 100.0 | 84 | 400~1000 | 417 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | 5 | 3 | 160.1 ±0.1 | 32.0 | 208 | 93.0 | 99.6 | 68~71 | 1000 | 414 | ok |
| yolo26n-pose.dxnn | 6 | 3 | 160.0 ±0.2 | 26.7 | 209 | 93.8 | 100.0 | 74~75 | 1000 | 459 | ok |
| yolo26s-pose.dxnn | 3 | 3 | 102.2 ±0.1 | 34.1 | 137 | 96.2 | 100.0 | 70~73 | 1000 | 351 | ok |
| yolo26s-pose.dxnn | 4 | 3 | 102.3 ±0.0 | 25.6 | 138 | 97.2 | 100.0 | 75~77 | 1000 | 399 | ok |
| yolo26m-pose.dxnn | 2 | 3 | 71.9 ±2.7 | 35.9 | 98 | 96.3 | 100.0 | 78~81 | 1000 | 331 | ok |
| yolo26m-pose.dxnn | 3 | 3 | 68.5 ±0.5 | 22.9 | 94 | 97.7 | 100.0 | 83~84 | 800~1000 | 372 | ok |
| yolo26l-pose.dxnn | 1 | 3 | 56.2 ±0.0 | 56.2 | 75 | 95.1 | 100.0 | 70~74 | 1000 | 268 | ok |
| yolo26l-pose.dxnn | 2 | 3 | 52.8 ±1.1 | 26.4 | 76 | 96.3 | 100.0 | 80~82 | 1000 | 340 | ok |
| yolo26x-pose.dxnn | 1 | 3 | 31.6 ±1.0 | 31.6 | 46 | 95.8 | 100.0 | 76~81 | 1000 | 362 | ok |
| yolo26x-pose.dxnn | 2 | 3 | 27.8 ±0.5 | 13.9 | 43 | 94.1 | 100.0 | 84 | 600~1000 | 402 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-pose.dxnn | 5 | 30.6 | 5 | 32.0 |
| yolo26s-pose.dxnn | 3 | 33.9 | 3 | 34.1 |
| yolo26m-pose.dxnn | 2 | 35.8 | 2 | 35.9 |
| yolo26l-pose.dxnn | 1 | 56.2 | 1 | 56.2 |
| yolo26x-pose.dxnn | 1 | 31.6 | 1 | 31.6 |

### Segmentation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | 2 | 3 | 85.2 ±0.7 | 42.6 | 298 | 45.8 | 68.5 | 65~68 | 1000 | 436 | ok |
| yolo26n-seg.dxnn | 3 | 3 | 85.1 ±0.1 | 28.4 | 298 | 46.4 | 69.9 | 70~71 | 1000 | 479 | ok |
| yolo26s-seg.dxnn | 2 | 3 | 69.4 ±0.3 | 34.7 | 247 | 71.5 | 90.2 | 72~75 | 1000 | 448 | ok |
| yolo26s-seg.dxnn | 3 | 3 | 69.1 ±0.0 | 23.0 | 247 | 71.3 | 87.7 | 66~73 | 1000 | 505 | ok |
| yolo26m-seg.dxnn | 1 | 3 | 54.7 ±1.5 | 54.7 | 163 | 91.9 | 100.0 | 75~81 | 1000 | 387 | ok |
| yolo26m-seg.dxnn | 2 | 3 | 40.4 ±0.8 | 20.2 | 133 | 93.6 | 100.0 | 84 | 400~1000 | 470 | ok |
| yolo26l-seg.dxnn | 1 | 3 | 44.3 ±1.5 | 44.3 | 126 | 94.8 | 100.0 | 75~81 | 1000 | 397 | ok |
| yolo26l-seg.dxnn | 2 | 3 | 35.0 ±0.2 | 17.5 | 107 | 94.9 | 100.0 | 84~85 | 400~1000 | 476 | ok |
| yolo26x-seg.dxnn | 1 | 3 | 21.2 ±2.9 | 21.2 | 64 | 93.2 | 100.0 | 82~84 | 600~1000 | 466 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | 3 | 3 | 92.9 ±0.5 | 31.0 | 313 | 52.3 | 73.5 | 67~70 | 1000 | 506 | ok |
| yolo26n-seg.dxnn | 4 | 3 | 93.3 ±0.1 | 23.3 | 314 | 53.0 | 73.5 | 65~70 | 1000 | 562 | ok |
| yolo26s-seg.dxnn | 2 | 3 | 75.0 ±0.1 | 37.5 | 246 | 79.2 | 93.4 | 73~77 | 1000 | 483 | ok |
| yolo26s-seg.dxnn | 3 | 3 | 72.7 ±0.5 | 24.2 | 236 | 83.6 | 95.0 | 79~81 | 1000 | 521 | ok |
| yolo26m-seg.dxnn | 1 | 3 | 55.1 ±1.5 | 55.1 | 160 | 94.5 | 100.0 | 75~80 | 1000 | 403 | ok |
| yolo26m-seg.dxnn | 2 | 3 | 40.9 ±3.8 | 20.5 | 129 | 94.6 | 100.0 | 84~85 | 400~1000 | 487 | ok |
| yolo26l-seg.dxnn | 1 | 3 | 44.6 ±1.4 | 44.6 | 127 | 94.5 | 100.0 | 75~81 | 1000 | 406 | ok |
| yolo26l-seg.dxnn | 2 | 3 | 35.2 ±0.6 | 17.6 | 107 | 94.2 | 100.0 | 84~85 | 400~1000 | 491 | ok |
| yolo26x-seg.dxnn | 1 | 3 | 21.3 ±2.8 | 21.3 | 64 | 92.5 | 100.0 | 82~84 | 400~1000 | 476 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-seg.dxnn | 2 | 42.6 | 3 | 31.0 |
| yolo26s-seg.dxnn | 2 | 34.7 | 2 | 37.5 |
| yolo26m-seg.dxnn | 1 | 54.7 | 1 | 55.1 |
| yolo26l-seg.dxnn | 1 | 44.3 | 1 | 44.6 |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | 1 | 3 | 59.5 ±0.0 | 59.5 | 108 | 93.1 | 100.0 | 63~65 | 1000 | 272 | ok |
| yolo26n-obb.dxnn | 2 | 3 | 59.5 ±0.0 | 29.8 | 122 | 95.9 | 100.0 | 68~70 | 1000 | 346 | ok |
| yolo26s-obb.dxnn | 1 | 3 | 36.5 ±0.0 | 36.5 | 74 | 95.0 | 100.0 | 66~69 | 1000 | 288 | ok |
| yolo26s-obb.dxnn | 2 | 2/3 | 36.5 ±0.1 | 18.2 | 82 | 96.9 | 100.0 | 57~73 | 1000 | 362 | partial |
| yolo26m-obb.dxnn | 1 | 3 | 27.4 ±0.0 | 27.4 | 60 | 95.8 | 100.0 | 72~77 | 1000 | 317 | ok |
| yolo26l-obb.dxnn | 1 | 3 | 20.4 ±0.2 | 20.4 | 47 | 95.9 | 100.0 | 74~78 | 1000 | 320 | ok |
| yolo26x-obb.dxnn | 1 | 3 | 11.1 ±0.4 | 11.1 | 25 | 93.5 | 100.0 | 80~83 | 800~1000 | 393 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | 1 | 3 | 59.5 ±0.1 | 59.5 | 110 | 92.6 | 100.0 | 63~65 | 1000 | 259 | ok |
| yolo26n-obb.dxnn | 2 | 3 | 59.5 ±0.0 | 29.8 | 127 | 96.0 | 100.0 | 68~70 | 1000 | 336 | ok |
| yolo26s-obb.dxnn | 1 | 3 | 36.5 ±0.0 | 36.5 | 77 | 95.5 | 100.0 | 66~69 | 1000 | 287 | ok |
| yolo26s-obb.dxnn | 2 | 3 | 36.5 ±0.0 | 18.3 | 86 | 96.6 | 100.0 | 73~75 | 1000 | 352 | ok |
| yolo26m-obb.dxnn | 1 | 3 | 27.4 ±0.0 | 27.4 | 61 | 95.4 | 100.0 | 73~77 | 1000 | 299 | ok |
| yolo26l-obb.dxnn | 1 | 3 | 20.4 ±0.3 | 20.4 | 47 | 95.9 | 100.0 | 74~79 | 1000 | 320 | ok |
| yolo26x-obb.dxnn | 1 | 3 | 11.1 ±0.4 | 11.1 | 25 | 93.4 | 100.0 | 80~84 | 800~1000 | 377 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-obb.dxnn | 1 | 59.5 | 1 | 59.5 |
| yolo26s-obb.dxnn | 1 | 36.5 | 1 | 36.5 |

---
*Report generated by dx_stream benchmark tool*
