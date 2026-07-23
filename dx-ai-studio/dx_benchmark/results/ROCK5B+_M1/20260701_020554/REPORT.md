# YOLO26 Benchmark Report

**Generated:** 2026-07-01 21:15:03 (Local)

## Test Timing

| # | Type | Start | End | Duration |
|---|------|-------|-----|----------|
| 1 | run | 2026-07-01 02:05:54 | 2026-07-01 21:15:03 | 19h 9m 9s |

## Executive Summary

### Object Detection

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n.dxnn | ON | 36.75 | 150.7 | 129.1 | 3 |
| yolo26n.dxnn | OFF | 34.73 | 157.1 | 98.3 | 3 |
| yolo26s.dxnn | ON | 56.63 | 104.1 | 98.2 | 3 |
| yolo26s.dxnn | OFF | 50.86 | 104.8 | 97.4 | 3 |
| yolo26m.dxnn | ON | 69.59 | 76.5 | 75.9 | 2 |
| yolo26m.dxnn | OFF | 58.51 | 76.4 | 76.4 | 2 |
| yolo26l.dxnn | ON | 82.62 | 57.2 | 57.2 | 1 |
| yolo26l.dxnn | OFF | 60.94 | 57.2 | 57.3 | 1 |
| yolo26x.dxnn | ON | 117.31 | 32.8 | 32.6 | 1 |
| yolo26x.dxnn | OFF | 103.10 | 32.8 | 32.6 | 1 |

### Pose Estimation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-pose.dxnn | ON | 40.34 | 161.8 | 152.7 | 5 |
| yolo26n-pose.dxnn | OFF | 30.92 | 164.5 | 160.2 | 5 |
| yolo26s-pose.dxnn | ON | 47.35 | 102.4 | 102.2 | 3 |
| yolo26s-pose.dxnn | OFF | 40.20 | 102.5 | 102.4 | 3 |
| yolo26m-pose.dxnn | ON | 62.17 | 74.8 | 74.8 | 2 |
| yolo26m-pose.dxnn | OFF | 49.29 | 74.8 | 74.8 | 2 |
| yolo26l-pose.dxnn | ON | 66.78 | 56.1 | 56.1 | 1 |
| yolo26l-pose.dxnn | OFF | 53.96 | 56.1 | 56.1 | 1 |
| yolo26x-pose.dxnn | ON | 101.19 | 32.3 | 31.7 | 1 |
| yolo26x-pose.dxnn | OFF | 89.14 | 32.3 | 31.7 | 1 |

### Segmentation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-seg.dxnn | ON | 46.22 | 99.4 | 82.4 | 2 |
| yolo26n-seg.dxnn | OFF | 41.43 | 113.3 | 78.6 | 2 |
| yolo26s-seg.dxnn | ON | 62.98 | 78.0 | 73.2 | 2 |
| yolo26s-seg.dxnn | OFF | 50.60 | 82.2 | 76.6 | 2 |
| yolo26m-seg.dxnn | ON | 81.83 | 56.0 | 54.4 | 1 |
| yolo26m-seg.dxnn | OFF | 65.62 | 56.0 | 55.5 | 1 |
| yolo26l-seg.dxnn | ON | 88.20 | 45.5 | 44.4 | 1 |
| yolo26l-seg.dxnn | OFF | 73.00 | 45.5 | 44.9 | 1 |
| yolo26x-seg.dxnn | ON | 142.37 | 25.6 | 23.7 | — |
| yolo26x-seg.dxnn | OFF | 120.23 | 25.6 | 23.8 | — |

### Oriented BBox (OBB)

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-obb.dxnn | ON | 64.87 | 59.5 | 59.4 | 1 |
| yolo26n-obb.dxnn | OFF | 52.29 | 59.5 | 59.4 | 1 |
| yolo26s-obb.dxnn | ON | 81.52 | 36.5 | 36.5 | 1 |
| yolo26s-obb.dxnn | OFF | 76.74 | 36.5 | 36.5 | 1 |
| yolo26m-obb.dxnn | ON | 114.21 | 27.3 | 27.4 | — |
| yolo26m-obb.dxnn | OFF | 94.29 | 27.4 | 27.4 | — |
| yolo26l-obb.dxnn | ON | 132.14 | 20.5 | 20.5 | — |
| yolo26l-obb.dxnn | OFF | 116.30 | 20.5 | 20.5 | — |
| yolo26x-obb.dxnn | ON | 226.51 | 11.9 | 11.3 | — |
| yolo26x-obb.dxnn | OFF | 200.01 | 11.9 | 11.3 | — |

### Classification

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-cls.dxnn | ON | 1.55 | 2654.2 | 937.5 | — |
| yolo26n-cls.dxnn | OFF | 1.48 | 2659.1 | 943.5 | — |
| yolo26s-cls.dxnn | ON | 3.58 | 1603.1 | 957.0 | — |
| yolo26s-cls.dxnn | OFF | 3.74 | 1603.7 | 963.5 | — |
| yolo26m-cls.dxnn | ON | 2.70 | 1278.3 | 954.7 | — |
| yolo26m-cls.dxnn | OFF | 4.06 | 1278.5 | 972.3 | — |
| yolo26l-cls.dxnn | ON | 4.02 | 793.7 | 768.2 | — |
| yolo26l-cls.dxnn | OFF | 3.96 | 793.1 | 771.4 | — |
| yolo26x-cls.dxnn | ON | 8.10 | 401.3 | 400.1 | — |
| yolo26x-cls.dxnn | OFF | 7.11 | 401.3 | 399.4 | — |

## Environment

| Item | Value |
|------|-------|
| Product | ROCK5B+ |
| Hostname | rock-5b-plus |
| OS | Debian GNU/Linux 12 (bookworm) |
| Kernel | 6.1.43-15-rk2312 |
| CPU | - |
| CPU Cores | 8 |
| RAM | 7.8 GB |
| NPU SKU | M1 |
| NPU RT | v3.2.0 |
| NPU Driver (RT) | v2.1.0 |
| NPU Driver (PCIe) | v2.0.1 |
| NPU Firmware | v2.5.0 |
| NPU Memory | LPDDR5 5600 Mbps, 3.92GiB |
| NPU Board | M.2, Rev 1.0 |
| NPU PCIe | Gen3 X2 [17:00:00] |

### Tools

| Tool | Available | Version |
|------|-----------|---------|
| run_model | Yes | DXRT v3.2.0 run_model |
| gst-launch-1.0 | Yes | gst-launch-1.0 version 1.22.9 |
| gst-inspect-1.0 | Yes | gst-inspect-1.0 version 1.22.9 |
| dxtop | Yes | DX-TOP 1.0.1 |
| ffprobe | Yes | ffprobe version 5.1.9-0+deb12u1 Copyright (c) 2007-2026 the ... |

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
| yolo26n.dxnn | 150.7 ±0.4 | 221 | 70.2 | 80.2 | 51~54 | 1000 | ok |
| yolo26s.dxnn | 104.1 ±0.3 | 161 | 91.0 | 100.0 | 59~62 | 1000 | ok |
| yolo26m.dxnn | 76.5 ±0.1 | 108 | 89.4 | 100.0 | 61~64 | 1000 | ok |
| yolo26l.dxnn | 57.2 | 78 | 94.1 | 100.0 | 61 | 1000 | ok |
| yolo26x.dxnn | 32.8 ±0.0 | 62 | 90.1 | 100.0 | 61~64 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n.dxnn | 157.1 ±0.1 | 124 | 77.1 | 91.0 | 59~60 | 1000 | ok |
| yolo26s.dxnn | 104.8 ±0.1 | 96 | 91.2 | 100.0 | 60~62 | 1000 | ok |
| yolo26m.dxnn | 76.4 ±0.2 | 73 | 90.9 | 100.0 | 61~64 | 1000 | ok |
| yolo26l.dxnn | 57.2 ±0.0 | 59 | 89.9 | 100.0 | 61~64 | 1000 | ok |
| yolo26x.dxnn | 32.8 ±0.0 | 41 | 90.1 | 100.0 | 61~64 | 1000 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-pose.dxnn | 161.8 ±0.7 | 168 | 87.1 | 99.9 | 58~60 | 1000 | ok |
| yolo26s-pose.dxnn | 102.4 ±0.0 | 98 | 90.4 | 100.0 | 59~61 | 1000 | ok |
| yolo26m-pose.dxnn | 74.8 ±0.0 | 80 | 90.0 | 100.0 | 61~64 | 1000 | ok |
| yolo26l-pose.dxnn | 56.1 ±0.0 | 68 | 89.2 | 100.0 | 61~64 | 1000 | ok |
| yolo26x-pose.dxnn | 32.3 ±0.0 | 70 | 88.5 | 100.0 | 62~65 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-pose.dxnn | 164.5 ±0.1 | 103 | 92.0 | 100.0 | 58~60 | 1000 | ok |
| yolo26s-pose.dxnn | 102.5 ±0.0 | 82 | 91.7 | 100.0 | 59~61 | 1000 | ok |
| yolo26m-pose.dxnn | 74.8 ±0.0 | 64 | 91.9 | 100.0 | 61~64 | 1000 | ok |
| yolo26l-pose.dxnn | 56.1 ±0.0 | 67 | 89.1 | 100.0 | 61~64 | 1000 | ok |
| yolo26x-pose.dxnn | 32.3 ±0.0 | 50 | 89.0 | 100.0 | 62~66 | 1000 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-seg.dxnn | 99.4 ±1.6 | 308 | 47.4 | 80.5 | 58~59 | 1000 | ok |
| yolo26s-seg.dxnn | 78.0 ±0.8 | 220 | 78.0 | 93.5 | 59~62 | 1000 | ok |
| yolo26m-seg.dxnn | 56.0 ±0.1 | 141 | 89.1 | 100.0 | 62~66 | 1000 | ok |
| yolo26l-seg.dxnn | 45.5 ±0.0 | 106 | 89.2 | 100.0 | 62~66 | 1000 | ok |
| yolo26x-seg.dxnn | 25.6 ±0.0 | 73 | 87.8 | 100.0 | 64~67 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-seg.dxnn | 113.3 ±0.8 | 202 | 58.9 | 83.1 | 58~60 | 1000 | ok |
| yolo26s-seg.dxnn | 82.2 ±0.1 | 144 | 83.0 | 98.2 | 60~62 | 1000 | ok |
| yolo26m-seg.dxnn | 56.0 ±0.1 | 99 | 89.9 | 100.0 | 63~67 | 1000 | ok |
| yolo26l-seg.dxnn | 45.5 ±0.0 | 89 | 89.3 | 100.0 | 62~66 | 1000 | ok |
| yolo26x-seg.dxnn | 25.6 ±0.0 | 56 | 87.9 | 100.0 | 64~68 | 1000 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-obb.dxnn | 59.5 ±0.0 | 81 | 89.9 | 100.0 | 58~60 | 1000 | ok |
| yolo26s-obb.dxnn | 36.5 ±0.0 | 83 | 90.0 | 100.0 | 59~61 | 1000 | ok |
| yolo26m-obb.dxnn | 27.3 ±0.0 | 71 | 89.8 | 100.0 | 61~64 | 1000 | ok |
| yolo26l-obb.dxnn | 20.5 ±0.0 | 48 | 88.7 | 100.0 | 61~64 | 1000 | ok |
| yolo26x-obb.dxnn | 11.9 ±0.0 | 39 | 90.1 | 100.0 | 62~65 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-obb.dxnn | 59.5 ±0.0 | 68 | 91.1 | 100.0 | 59~60 | 1000 | ok |
| yolo26s-obb.dxnn | 36.5 ±0.0 | 55 | 90.1 | 100.0 | 59~61 | 1000 | ok |
| yolo26m-obb.dxnn | 27.4 ±0.0 | 46 | 89.2 | 100.0 | 61~64 | 1000 | ok |
| yolo26l-obb.dxnn | 20.5 ±0.0 | 37 | 88.9 | 100.0 | 61~64 | 1000 | ok |
| yolo26x-obb.dxnn | 11.9 ±0.0 | 33 | 90.2 | 100.0 | 63~65 | 1000 | ok |

#### Classification

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-cls.dxnn | 2654.2 ±1.1 | 88 | 88.0 | 97.5 | 57~58 | 1000 | ok |
| yolo26s-cls.dxnn | 1603.1 ±0.3 | 64 | 90.6 | 98.5 | 58~59 | 1000 | ok |
| yolo26m-cls.dxnn | 1278.3 ±1.3 | 52 | 89.5 | 98.7 | 60~62 | 1000 | ok |
| yolo26l-cls.dxnn | 793.7 ±0.4 | 57 | 88.4 | 99.0 | 59~61 | 1000 | ok |
| yolo26x-cls.dxnn | 401.3 ±0.3 | 44 | 91.7 | 100.0 | 60~62 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-cls.dxnn | 2659.1 ±2.8 | 86 | 89.4 | 97.7 | 57~58 | 1000 | ok |
| yolo26s-cls.dxnn | 1603.7 ±0.9 | 64 | 90.5 | 98.7 | 58~59 | 1000 | ok |
| yolo26m-cls.dxnn | 1278.5 ±2.6 | 51 | 88.3 | 98.8 | 60~63 | 1000 | ok |
| yolo26l-cls.dxnn | 793.1 ±1.2 | 57 | 88.8 | 99.4 | 60~61 | 1000 | ok |
| yolo26x-cls.dxnn | 401.3 ±0.2 | 43 | 90.5 | 100.0 | 60~62 | 1000 | ok |

### Latency (Single-Core, Sync)

#### Object Detection

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n.dxnn | 27.2 | 36.75 | 28.72 | 8.03 | 47 | ok |
| yolo26s.dxnn | 17.7 | 56.63 | 47.03 | 9.60 | 56 | ok |
| yolo26m.dxnn | 14.4 | 69.59 | 54.60 | 15.00 | 56 | ok |
| yolo26l.dxnn | 12.1 | 82.62 | 68.65 | 13.97 | 56 | ok |
| yolo26x.dxnn | 8.5 | 117.31 | 101.58 | 15.73 | 56 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n.dxnn | 28.8 | 34.73 | 34.73 | 56 | ok |
| yolo26s.dxnn | 19.7 | 50.86 | 50.86 | 56 | ok |
| yolo26m.dxnn | 17.1 | 58.51 | 58.51 | 56 | ok |
| yolo26l.dxnn | 16.4 | 60.94 | 60.94 | 56 | ok |
| yolo26x.dxnn | 9.7 | 103.10 | 103.10 | 56 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-pose.dxnn | 24.8 | 40.34 | 31.21 | 9.13 | 56 | ok |
| yolo26s-pose.dxnn | 21.1 | 47.35 | 38.54 | 8.80 | 56 | ok |
| yolo26m-pose.dxnn | 16.1 | 62.17 | 48.18 | 13.98 | 56 | ok |
| yolo26l-pose.dxnn | 15.0 | 66.78 | 57.60 | 9.19 | 56 | ok |
| yolo26x-pose.dxnn | 9.9 | 101.19 | 92.60 | 8.59 | 56 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-pose.dxnn | 32.3 | 30.92 | 30.92 | 55 | ok |
| yolo26s-pose.dxnn | 24.9 | 40.20 | 40.20 | 56 | ok |
| yolo26m-pose.dxnn | 20.3 | 49.29 | 49.29 | 56 | ok |
| yolo26l-pose.dxnn | 18.5 | 53.96 | 53.96 | 57 | ok |
| yolo26x-pose.dxnn | 11.2 | 89.14 | 89.14 | 57 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-seg.dxnn | 21.6 | 46.22 | 36.57 | 9.65 | 55 | ok |
| yolo26s-seg.dxnn | 15.9 | 62.98 | 50.63 | 12.34 | 56 | ok |
| yolo26m-seg.dxnn | 12.2 | 81.83 | 67.58 | 14.25 | 56 | ok |
| yolo26l-seg.dxnn | 11.3 | 88.20 | 75.25 | 12.95 | 57 | ok |
| yolo26x-seg.dxnn | 7.0 | 142.37 | 123.95 | 18.42 | 57 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-seg.dxnn | 24.1 | 41.43 | 41.43 | 56 | ok |
| yolo26s-seg.dxnn | 19.8 | 50.60 | 50.60 | 56 | ok |
| yolo26m-seg.dxnn | 15.2 | 65.62 | 65.62 | 56 | ok |
| yolo26l-seg.dxnn | 13.7 | 73.00 | 73.00 | 57 | ok |
| yolo26x-seg.dxnn | 8.3 | 120.23 | 120.23 | 57 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-obb.dxnn | 15.4 | 64.87 | 47.11 | 17.76 | 55 | ok |
| yolo26s-obb.dxnn | 12.3 | 81.52 | 70.45 | 11.06 | 56 | ok |
| yolo26m-obb.dxnn | 8.8 | 114.21 | 91.75 | 22.45 | 57 | ok |
| yolo26l-obb.dxnn | 7.6 | 132.14 | 119.65 | 12.49 | 57 | ok |
| yolo26x-obb.dxnn | 4.4 | 226.51 | 200.16 | 26.35 | 57 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-obb.dxnn | 19.1 | 52.29 | 52.29 | 56 | ok |
| yolo26s-obb.dxnn | 13.0 | 76.74 | 76.74 | 56 | ok |
| yolo26m-obb.dxnn | 10.6 | 94.29 | 94.29 | 57 | ok |
| yolo26l-obb.dxnn | 8.6 | 116.30 | 116.30 | 57 | ok |
| yolo26x-obb.dxnn | 5.0 | 200.01 | 200.01 | 58 | ok |

#### Classification

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-cls.dxnn | 643.2 | 1.55 | 1.55 | N/A | 56 | ok |
| yolo26s-cls.dxnn | 279.6 | 3.58 | 3.58 | N/A | 56 | ok |
| yolo26m-cls.dxnn | 369.7 | 2.70 | 2.70 | N/A | 56 | ok |
| yolo26l-cls.dxnn | 248.5 | 4.02 | 4.02 | N/A | 56 | ok |
| yolo26x-cls.dxnn | 123.4 | 8.10 | 8.10 | N/A | 55 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-cls.dxnn | 675.0 | 1.48 | 1.48 | 56 | ok |
| yolo26s-cls.dxnn | 267.6 | 3.74 | 3.74 | 56 | ok |
| yolo26m-cls.dxnn | 246.2 | 4.06 | 4.06 | 56 | ok |
| yolo26l-cls.dxnn | 252.6 | 3.96 | 3.96 | 56 | ok |
| yolo26x-cls.dxnn | 140.7 | 7.11 | 7.11 | 56 | ok |

## E2E Pipeline (Single-Stream)

### Object Detection

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | mppvideodec | 3455 | 3 | 129.1 ±0.5 | 26.76 | 244 | 56.2 | 85.8 | 55~57 | 1000 | 187 | ok |
| yolo26s.dxnn | mppvideodec | 3455 | 3 | 98.2 ±1.0 | 35.18 | 181 | 82.6 | 96.4 | 63~66 | 1000 | 201 | ok |
| yolo26m.dxnn | mppvideodec | 3455 | 3 | 75.9 ±0.1 | 45.51 | 141 | 92.2 | 100.0 | 67~70 | 1000 | 223 | ok |
| yolo26l.dxnn | mppvideodec | 3455 | 3 | 57.2 ±0.0 | 60.43 | 99 | 94.3 | 100.0 | 57~64 | 1000 | 233 | ok |
| yolo26x.dxnn | mppvideodec | 3455 | 3 | 32.6 ±0.4 | 105.89 | 70 | 96.4 | 100.0 | 72~77 | 1000 | 350 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | mppvideodec | 3455 | 3 | 98.3 ±0.5 | 35.13 | 208 | 33.8 | 57.8 | 59~60 | 1000 | 200 | ok |
| yolo26s.dxnn | mppvideodec | 3455 | 3 | 97.4 ±0.2 | 35.48 | 211 | 80.9 | 89.8 | 63~65 | 1000 | 215 | ok |
| yolo26m.dxnn | mppvideodec | 3455 | 3 | 76.4 ±0.1 | 45.21 | 162 | 92.2 | 100.0 | 66~70 | 1000 | 232 | ok |
| yolo26l.dxnn | mppvideodec | 3455 | 3 | 57.3 ±0.0 | 60.31 | 121 | 94.1 | 100.0 | 69~73 | 1000 | 244 | ok |
| yolo26x.dxnn | mppvideodec | 3455 | 3 | 32.6 ±0.4 | 105.92 | 91 | 96.4 | 100.0 | 72~76 | 1000 | 350 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n.dxnn | 129.1 | 98.3 | +30.8 | +31.3% |
| yolo26s.dxnn | 98.2 | 97.4 | +0.8 | +0.9% |
| yolo26m.dxnn | 75.9 | 76.4 | -0.5 | -0.7% |
| yolo26l.dxnn | 57.2 | 57.3 | -0.1 | -0.2% |
| yolo26x.dxnn | 32.6 | 32.6 | +0.0 | +0.0% |

### Pose Estimation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | mppvideodec | 3455 | 3 | 152.7 ±0.6 | 22.63 | 195 | 78.6 | 95.0 | 60~61 | 1000 | 176 | ok |
| yolo26s-pose.dxnn | mppvideodec | 3455 | 3 | 102.2 ±0.1 | 33.79 | 130 | 90.8 | 100.0 | 62~63 | 1000 | 193 | ok |
| yolo26m-pose.dxnn | mppvideodec | 3455 | 3 | 74.8 ±0.0 | 46.20 | 94 | 93.3 | 100.0 | 67~71 | 1000 | 215 | ok |
| yolo26l-pose.dxnn | mppvideodec | 3455 | 3 | 56.1 ±0.0 | 61.62 | 79 | 94.3 | 100.0 | 68~72 | 1000 | 224 | ok |
| yolo26x-pose.dxnn | mppvideodec | 3455 | 3 | 31.7 ±0.8 | 108.94 | 69 | 95.4 | 100.0 | 73~78 | 1000 | 362 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | mppvideodec | 3455 | 3 | 160.2 ±0.6 | 21.56 | 151 | 82.7 | 99.1 | 59~60 | 1000 | 166 | ok |
| yolo26s-pose.dxnn | mppvideodec | 3455 | 3 | 102.4 ±0.1 | 33.74 | 95 | 90.9 | 100.0 | 61~63 | 1000 | 182 | ok |
| yolo26m-pose.dxnn | mppvideodec | 3455 | 3 | 74.8 ±0.0 | 46.20 | 81 | 93.0 | 100.0 | 67~71 | 1000 | 202 | ok |
| yolo26l-pose.dxnn | mppvideodec | 3455 | 3 | 56.1 ±0.0 | 61.56 | 73 | 94.5 | 100.0 | 68~72 | 1000 | 211 | ok |
| yolo26x-pose.dxnn | mppvideodec | 3455 | 3 | 31.7 ±0.8 | 108.86 | 71 | 95.1 | 100.0 | 73~78 | 1000 | 362 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-pose.dxnn | 152.7 | 160.2 | -7.6 | -4.7% |
| yolo26s-pose.dxnn | 102.2 | 102.4 | -0.1 | -0.1% |
| yolo26m-pose.dxnn | 74.8 | 74.8 | +0.0 | +0.0% |
| yolo26l-pose.dxnn | 56.1 | 56.1 | -0.0 | -0.1% |
| yolo26x-pose.dxnn | 31.7 | 31.7 | -0.0 | -0.1% |

### Segmentation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | mppvideodec | 3455 | 3 | 82.4 ±0.3 | 41.92 | 344 | 41.1 | 73.2 | 60~61 | 1000 | 287 | ok |
| yolo26s-seg.dxnn | mppvideodec | 3455 | 3 | 73.2 ±0.9 | 47.22 | 272 | 70.2 | 85.4 | 64~67 | 1000 | 301 | ok |
| yolo26m-seg.dxnn | mppvideodec | 3455 | 3 | 54.4 ±0.8 | 63.50 | 206 | 89.4 | 99.3 | 72~77 | 1000 | 324 | ok |
| yolo26l-seg.dxnn | mppvideodec | 3455 | 3 | 44.4 ±1.1 | 77.81 | 152 | 94.3 | 100.0 | 73~78 | 1000 | 334 | ok |
| yolo26x-seg.dxnn | mppvideodec | 3455 | 3 | 23.7 ±1.2 | 145.57 | 91 | 95.0 | 100.0 | 79~83 | 800~1000 | 405 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | mppvideodec | 3455 | 3 | 78.6 ±1.8 | 43.96 | 304 | 31.9 | 77.7 | 60~61 | 1000 | 314 | ok |
| yolo26s-seg.dxnn | mppvideodec | 3455 | 3 | 76.6 ±0.1 | 45.12 | 289 | 76.7 | 90.6 | 64~67 | 1000 | 329 | ok |
| yolo26m-seg.dxnn | mppvideodec | 3455 | 3 | 55.5 ±0.9 | 62.23 | 196 | 93.5 | 100.0 | 72~77 | 1000 | 347 | ok |
| yolo26l-seg.dxnn | mppvideodec | 3455 | 3 | 44.9 ±1.1 | 77.03 | 152 | 94.5 | 100.0 | 73~77 | 1000 | 355 | ok |
| yolo26x-seg.dxnn | mppvideodec | 3455 | 3 | 23.8 ±1.2 | 145.17 | 92 | 94.6 | 100.0 | 78~83 | 800~1000 | 412 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-seg.dxnn | 82.4 | 78.6 | +3.8 | +4.9% |
| yolo26s-seg.dxnn | 73.2 | 76.6 | -3.4 | -4.4% |
| yolo26m-seg.dxnn | 54.4 | 55.5 | -1.1 | -2.0% |
| yolo26l-seg.dxnn | 44.4 | 44.9 | -0.5 | -1.0% |
| yolo26x-seg.dxnn | 23.7 | 23.8 | -0.1 | -0.3% |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | mppvideodec | 2640 | 3 | 59.4 ±0.0 | 44.42 | 97 | 93.1 | 100.0 | 62~64 | 1000 | 213 | ok |
| yolo26s-obb.dxnn | mppvideodec | 2640 | 3 | 36.5 ±0.0 | 72.41 | 76 | 94.7 | 100.0 | 63~66 | 1000 | 230 | ok |
| yolo26m-obb.dxnn | mppvideodec | 2640 | 3 | 27.4 ±0.0 | 96.43 | 77 | 95.3 | 100.0 | 70~74 | 1000 | 251 | ok |
| yolo26l-obb.dxnn | mppvideodec | 2640 | 3 | 20.5 ±0.0 | 128.59 | 78 | 95.7 | 100.0 | 71~75 | 1000 | 262 | ok |
| yolo26x-obb.dxnn | mppvideodec | 2640 | 3 | 11.3 ±0.4 | 232.52 | 50 | 94.5 | 100.0 | 76~79 | 1000 | 374 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | mppvideodec | 2640 | 3 | 59.4 ±0.1 | 44.44 | 100 | 93.4 | 100.0 | 61~63 | 1000 | 218 | ok |
| yolo26s-obb.dxnn | mppvideodec | 2640 | 3 | 36.5 ±0.0 | 72.39 | 87 | 94.7 | 100.0 | 63~66 | 1000 | 226 | ok |
| yolo26m-obb.dxnn | mppvideodec | 2640 | 3 | 27.4 ±0.0 | 96.43 | 81 | 95.2 | 100.0 | 69~74 | 1000 | 243 | ok |
| yolo26l-obb.dxnn | mppvideodec | 2640 | 3 | 20.5 ±0.0 | 128.56 | 72 | 95.7 | 100.0 | 71~75 | 1000 | 256 | ok |
| yolo26x-obb.dxnn | mppvideodec | 2640 | 3 | 11.3 ±0.4 | 232.83 | 60 | 94.5 | 100.0 | 76~79 | 1000 | 374 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-obb.dxnn | 59.4 | 59.4 | +0.0 | +0.1% |
| yolo26s-obb.dxnn | 36.5 | 36.5 | -0.0 | -0.0% |
| yolo26m-obb.dxnn | 27.4 | 27.4 | +0.0 | +0.0% |
| yolo26l-obb.dxnn | 20.5 | 20.5 | -0.0 | -0.0% |
| yolo26x-obb.dxnn | 11.3 | 11.3 | +0.0 | +0.1% |

### Classification

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-cls.dxnn | mppvideodec | 3455 | 3 | 937.5 ±38.8 | 3.69 | 149 | 14.9 | 54.2 | 56~57 | 1000 | 85 | ok |
| yolo26s-cls.dxnn | mppvideodec | 3455 | 3 | 957.0 ±39.7 | 3.61 | 149 | 29.1 | 67.4 | 57 | 1000 | 100 | ok |
| yolo26m-cls.dxnn | mppvideodec | 3455 | 3 | 954.7 ±18.8 | 3.62 | 150 | 35.8 | 84.7 | 60 | 1000 | 124 | ok |
| yolo26l-cls.dxnn | mppvideodec | 3455 | 3 | 768.2 ±6.8 | 4.50 | 125 | 56.3 | 99.0 | 59 | 1000 | 137 | ok |
| yolo26x-cls.dxnn | mppvideodec | 3455 | 3 | 400.1 ±0.4 | 8.63 | 87 | 73.2 | 100.0 | 61~62 | 1000 | 213 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-cls.dxnn | mppvideodec | 3455 | 3 | 943.5 ±10.7 | 3.66 | 150 | 15.1 | 54.7 | 56 | 1000 | 85 | ok |
| yolo26s-cls.dxnn | mppvideodec | 3455 | 3 | 963.5 ±42.9 | 3.59 | 150 | 25.3 | 66.4 | 57 | 1000 | 100 | ok |
| yolo26m-cls.dxnn | mppvideodec | 3455 | 3 | 972.3 ±32.5 | 3.55 | 149 | 37.4 | 85.6 | 60 | 1000 | 124 | ok |
| yolo26l-cls.dxnn | mppvideodec | 3455 | 3 | 771.4 ±6.3 | 4.48 | 128 | 58.0 | 99.3 | 59~60 | 1000 | 137 | ok |
| yolo26x-cls.dxnn | mppvideodec | 3455 | 3 | 399.4 ±1.6 | 8.65 | 94 | 74.2 | 100.0 | 61~62 | 1000 | 213 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-cls.dxnn | 937.5 | 943.5 | -6.1 | -0.6% |
| yolo26s-cls.dxnn | 957.0 | 963.5 | -6.5 | -0.7% |
| yolo26m-cls.dxnn | 954.7 | 972.3 | -17.6 | -1.8% |
| yolo26l-cls.dxnn | 768.2 | 771.4 | -3.2 | -0.4% |
| yolo26x-cls.dxnn | 400.1 | 399.4 | +0.7 | +0.2% |

## E2E Pipeline (Multi-Stream)

### Object Detection

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | 4 | 3 | 114.1 ±21.3 | 28.5 | 224 | 51.5 | 100.0 | 61~63 | 1000 | 210 | ok |
| yolo26n.dxnn | 3 | 3 | 130.2 ±0.8 | 43.4 | 253 | 60.6 | 88.4 | 64~66 | 1000 | 204 | ok |
| yolo26s.dxnn | 3 | 3 | 98.3 ±0.7 | 32.8 | 188 | 86.7 | 95.3 | 69~72 | 1000 | 218 | ok |
| yolo26s.dxnn | 4 | 3 | 98.7 ±0.2 | 24.7 | 189 | 88.0 | 95.6 | 74~75 | 1000 | 224 | ok |
| yolo26m.dxnn | 2 | 3 | 75.0 ±1.6 | 37.5 | 141 | 94.9 | 100.0 | 74~76 | 1000 | 234 | ok |
| yolo26m.dxnn | 3 | 3 | 70.7 ±0.5 | 23.6 | 129 | 96.7 | 100.0 | 78~79 | 1000 | 240 | ok |
| yolo26l.dxnn | 1 | 3 | 57.2 ±0.0 | 57.2 | 99 | 94.3 | 100.0 | 57~64 | 1000 | 233 | ok |
| yolo26l.dxnn | 2 | 3 | 56.6 ±1.0 | 28.3 | 102 | 96.8 | 100.0 | 72~76 | 1000 | 244 | ok |
| yolo26x.dxnn | 1 | 3 | 32.6 ±0.4 | 32.6 | 70 | 96.4 | 100.0 | 72~77 | 1000 | 350 | ok |
| yolo26x.dxnn | 2 | 3 | 30.6 ±0.1 | 15.3 | 69 | 96.9 | 100.0 | 80~81 | 1000 | 350 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | 3 | 3 | 96.0 ±3.1 | 32.0 | 206 | 34.5 | 100.0 | 62 | 1000 | 223 | ok |
| yolo26n.dxnn | 4 | 3 | 98.3 ±0.4 | 24.6 | 218 | 36.0 | 61.3 | 64~65 | 1000 | 232 | ok |
| yolo26s.dxnn | 3 | 3 | 97.0 ±0.3 | 32.4 | 214 | 84.2 | 89.6 | 69~72 | 1000 | 237 | ok |
| yolo26s.dxnn | 4 | 3 | 97.2 ±0.3 | 24.3 | 217 | 84.7 | 90.7 | 73 | 1000 | 247 | ok |
| yolo26m.dxnn | 2 | 3 | 75.0 ±2.0 | 37.5 | 161 | 95.9 | 100.0 | 74~77 | 1000 | 240 | ok |
| yolo26m.dxnn | 3 | 3 | 70.6 ±0.4 | 23.5 | 151 | 96.7 | 100.0 | 78~79 | 1000 | 259 | ok |
| yolo26l.dxnn | 1 | 3 | 57.3 ±0.0 | 57.3 | 121 | 94.1 | 100.0 | 69~73 | 1000 | 244 | ok |
| yolo26l.dxnn | 2 | 3 | 54.7 ±1.3 | 27.4 | 116 | 96.8 | 100.0 | 76~78 | 1000 | 256 | ok |
| yolo26x.dxnn | 1 | 3 | 32.6 ±0.4 | 32.6 | 91 | 96.4 | 100.0 | 72~76 | 1000 | 350 | ok |
| yolo26x.dxnn | 2 | 3 | 30.6 ±0.1 | 15.3 | 88 | 96.9 | 100.0 | 79~80 | 1000 | 350 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n.dxnn | 3 | 43.4 | 3 | 32.0 |
| yolo26s.dxnn | 3 | 32.8 | 3 | 32.4 |
| yolo26m.dxnn | 2 | 37.5 | 2 | 37.5 |
| yolo26l.dxnn | 1 | 57.2 | 1 | 57.3 |
| yolo26x.dxnn | 1 | 32.6 | 1 | 32.6 |

### Pose Estimation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | 5 | 3 | 153.6 ±0.3 | 30.7 | 209 | 86.4 | 94.8 | 65~68 | 1000 | 210 | ok |
| yolo26n-pose.dxnn | 6 | 3 | 154.2 ±0.2 | 25.7 | 207 | 87.7 | 94.4 | 68~70 | 1000 | 217 | ok |
| yolo26s-pose.dxnn | 3 | 3 | 102.3 ±0.0 | 34.1 | 134 | 96.1 | 100.0 | 67~70 | 1000 | 214 | ok |
| yolo26s-pose.dxnn | 4 | 3 | 102.4 ±0.1 | 25.6 | 135 | 96.9 | 100.0 | 71~72 | 1000 | 221 | ok |
| yolo26m-pose.dxnn | 2 | 3 | 72.5 ±2.2 | 36.3 | 94 | 95.9 | 100.0 | 74~77 | 1000 | 227 | ok |
| yolo26m-pose.dxnn | 3 | 3 | 69.0 ±0.3 | 23.0 | 92 | 97.5 | 100.0 | 79~80 | 1000 | 237 | ok |
| yolo26l-pose.dxnn | 1 | 3 | 56.1 ±0.0 | 56.1 | 79 | 94.3 | 100.0 | 68~72 | 1000 | 224 | ok |
| yolo26l-pose.dxnn | 2 | 3 | 53.6 ±1.6 | 26.8 | 77 | 96.1 | 100.0 | 76~78 | 1000 | 236 | ok |
| yolo26x-pose.dxnn | 1 | 3 | 31.7 ±0.8 | 31.7 | 69 | 95.4 | 100.0 | 73~78 | 1000 | 362 | ok |
| yolo26x-pose.dxnn | 2 | 3 | 29.8 ±0.3 | 14.9 | 65 | 97.9 | 100.0 | 81~82 | 800~1000 | 362 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | 5 | 3 | 161.0 ±0.3 | 32.2 | 155 | 93.6 | 99.6 | 64~67 | 1000 | 205 | ok |
| yolo26n-pose.dxnn | 6 | 3 | 161.1 ±0.4 | 26.9 | 156 | 93.7 | 99.7 | 68~69 | 1000 | 212 | ok |
| yolo26s-pose.dxnn | 3 | 3 | 102.4 ±0.0 | 34.1 | 99 | 96.3 | 100.0 | 66~69 | 1000 | 203 | ok |
| yolo26s-pose.dxnn | 4 | 3 | 102.5 ±0.1 | 25.6 | 99 | 97.1 | 100.0 | 70~72 | 1000 | 215 | ok |
| yolo26m-pose.dxnn | 2 | 3 | 72.8 ±2.2 | 36.4 | 81 | 95.9 | 100.0 | 74~77 | 1000 | 216 | ok |
| yolo26m-pose.dxnn | 3 | 3 | 69.0 ±0.3 | 23.0 | 75 | 97.5 | 100.0 | 79~80 | 1000 | 225 | ok |
| yolo26l-pose.dxnn | 1 | 3 | 56.1 ±0.0 | 56.1 | 73 | 94.5 | 100.0 | 68~72 | 1000 | 211 | ok |
| yolo26l-pose.dxnn | 2 | 3 | 53.8 ±1.4 | 26.9 | 78 | 96.3 | 100.0 | 76~78 | 1000 | 227 | ok |
| yolo26x-pose.dxnn | 1 | 3 | 31.7 ±0.8 | 31.7 | 71 | 95.1 | 100.0 | 73~78 | 1000 | 362 | ok |
| yolo26x-pose.dxnn | 2 | 3 | 30.0 ±0.1 | 15.0 | 69 | 98.2 | 100.0 | 81~82 | 1000 | 362 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-pose.dxnn | 5 | 30.7 | 5 | 32.2 |
| yolo26s-pose.dxnn | 3 | 34.1 | 3 | 34.1 |
| yolo26m-pose.dxnn | 2 | 36.3 | 2 | 36.4 |
| yolo26l-pose.dxnn | 1 | 56.1 | 1 | 56.1 |
| yolo26x-pose.dxnn | 1 | 31.7 | 1 | 31.7 |

### Segmentation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | 2 | 3 | 84.1 ±0.2 | 42.1 | 346 | 43.1 | 75.2 | 63~65 | 1000 | 305 | ok |
| yolo26n-seg.dxnn | 3 | 3 | 82.5 ±1.3 | 27.5 | 352 | 42.8 | 76.3 | 66~67 | 1000 | 313 | ok |
| yolo26s-seg.dxnn | 2 | 3 | 72.3 ±0.3 | 36.2 | 285 | 70.8 | 83.3 | 69~72 | 1000 | 318 | ok |
| yolo26s-seg.dxnn | 3 | 3 | 72.8 ±0.7 | 24.3 | 278 | 72.7 | 88.1 | 74~75 | 1000 | 330 | ok |
| yolo26m-seg.dxnn | 1 | 3 | 54.4 ±0.8 | 54.4 | 206 | 89.4 | 99.3 | 72~77 | 1000 | 324 | ok |
| yolo26m-seg.dxnn | 2 | 3 | 49.9 ±1.4 | 24.9 | 189 | 92.9 | 100.0 | 82~84 | 800~1000 | 344 | ok |
| yolo26l-seg.dxnn | 1 | 3 | 44.4 ±1.1 | 44.4 | 152 | 94.3 | 100.0 | 73~78 | 1000 | 334 | ok |
| yolo26l-seg.dxnn | 2 | 3 | 40.9 ±0.9 | 20.5 | 149 | 96.0 | 100.0 | 82~84 | 800~1000 | 355 | ok |
| yolo26x-seg.dxnn | 1 | 3 | 23.7 ±1.2 | 23.7 | 91 | 95.0 | 100.0 | 79~83 | 800~1000 | 405 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | 2 | 3 | 79.5 ±1.8 | 39.8 | 305 | 33.8 | 77.5 | 63~64 | 1000 | 337 | ok |
| yolo26n-seg.dxnn | 3 | 3 | 79.3 ±1.8 | 26.4 | 306 | 33.9 | 77.4 | 65~66 | 1000 | 351 | ok |
| yolo26s-seg.dxnn | 2 | 3 | 76.7 ±0.0 | 38.3 | 293 | 79.2 | 90.1 | 70~73 | 1000 | 353 | ok |
| yolo26s-seg.dxnn | 3 | 3 | 62.2 ±18.0 | 20.7 | 245 | 64.5 | 100.0 | 71~76 | 1000 | 367 | ok |
| yolo26m-seg.dxnn | 1 | 3 | 55.5 ±0.9 | 55.5 | 196 | 93.5 | 100.0 | 72~77 | 1000 | 347 | ok |
| yolo26m-seg.dxnn | 2 | 3 | 50.4 ±1.6 | 25.2 | 172 | 95.6 | 100.0 | 82~84 | 800~1000 | 363 | ok |
| yolo26l-seg.dxnn | 1 | 3 | 44.9 ±1.1 | 44.9 | 152 | 94.5 | 100.0 | 73~77 | 1000 | 355 | ok |
| yolo26l-seg.dxnn | 2 | 3 | 41.5 ±0.8 | 20.7 | 137 | 96.8 | 100.0 | 81~83 | 800~1000 | 372 | ok |
| yolo26x-seg.dxnn | 1 | 3 | 23.8 ±1.2 | 23.8 | 92 | 94.6 | 100.0 | 78~83 | 800~1000 | 412 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-seg.dxnn | 2 | 42.1 | 2 | 39.8 |
| yolo26s-seg.dxnn | 2 | 36.2 | 2 | 38.3 |
| yolo26m-seg.dxnn | 1 | 54.4 | 1 | 55.5 |
| yolo26l-seg.dxnn | 1 | 44.4 | 1 | 44.9 |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | 1 | 3 | 59.4 ±0.0 | 59.4 | 97 | 93.1 | 100.0 | 62~64 | 1000 | 213 | ok |
| yolo26n-obb.dxnn | 2 | 3 | 59.5 ±0.0 | 29.7 | 100 | 95.7 | 100.0 | 67~69 | 1000 | 230 | ok |
| yolo26s-obb.dxnn | 1 | 3 | 36.5 ±0.0 | 36.5 | 76 | 94.7 | 100.0 | 63~66 | 1000 | 230 | ok |
| yolo26s-obb.dxnn | 2 | 3 | 36.5 ±0.0 | 18.2 | 76 | 96.4 | 100.0 | 69~71 | 1000 | 244 | ok |
| yolo26m-obb.dxnn | 1 | 3 | 27.4 ±0.0 | 27.4 | 77 | 95.3 | 100.0 | 70~74 | 1000 | 251 | ok |
| yolo26l-obb.dxnn | 1 | 3 | 20.5 ±0.0 | 20.5 | 78 | 95.7 | 100.0 | 71~75 | 1000 | 262 | ok |
| yolo26x-obb.dxnn | 1 | 3 | 11.3 ±0.4 | 11.3 | 50 | 94.5 | 100.0 | 76~79 | 1000 | 374 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | 1 | 3 | 59.4 ±0.1 | 59.4 | 100 | 93.4 | 100.0 | 61~63 | 1000 | 218 | ok |
| yolo26n-obb.dxnn | 2 | 3 | 59.5 ±0.0 | 29.7 | 101 | 96.0 | 100.0 | 65~67 | 1000 | 223 | ok |
| yolo26s-obb.dxnn | 1 | 3 | 36.5 ±0.0 | 36.5 | 87 | 94.7 | 100.0 | 63~66 | 1000 | 226 | ok |
| yolo26s-obb.dxnn | 2 | 3 | 36.5 ±0.0 | 18.2 | 91 | 96.3 | 100.0 | 69~71 | 1000 | 246 | ok |
| yolo26m-obb.dxnn | 1 | 3 | 27.4 ±0.0 | 27.4 | 81 | 95.2 | 100.0 | 69~74 | 1000 | 243 | ok |
| yolo26l-obb.dxnn | 1 | 3 | 20.5 ±0.0 | 20.5 | 72 | 95.7 | 100.0 | 71~75 | 1000 | 256 | ok |
| yolo26x-obb.dxnn | 1 | 3 | 11.3 ±0.4 | 11.3 | 60 | 94.5 | 100.0 | 76~79 | 1000 | 374 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-obb.dxnn | 1 | 59.4 | 1 | 59.4 |
| yolo26s-obb.dxnn | 1 | 36.5 | 1 | 36.5 |

---
*Report generated by dx_stream benchmark tool*
