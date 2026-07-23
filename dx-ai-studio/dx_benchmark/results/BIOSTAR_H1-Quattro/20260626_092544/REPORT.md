# YOLO26 Benchmark Report

**Generated:** 2026-06-27 03:36:00 (Local)

## Test Timing

| # | Type | Start | End | Duration |
|---|------|-------|-----|----------|
| 1 | run | 2026-06-26 09:25:44 | 2026-06-27 03:36:00 | 18h 10m 15s |

## Executive Summary

### Object Detection

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n.dxnn | ON | 15.76 | 654.5 | 484.9 | 17 |
| yolo26n.dxnn | OFF | 15.06 | 653.7 | 441.8 | 14 |
| yolo26s.dxnn | ON | 23.53 | 415.7 | 418.2 | 13 |
| yolo26s.dxnn | OFF | 22.66 | 416.5 | 418.4 | 13 |
| yolo26m.dxnn | ON | 31.22 | 309.2 | 307.5 | 10 |
| yolo26m.dxnn | OFF | 30.24 | 308.8 | 307.7 | 10 |
| yolo26l.dxnn | ON | 40.11 | 230.5 | 230.5 | 7 |
| yolo26l.dxnn | OFF | 39.11 | 230.6 | 230.9 | 7 |
| yolo26x.dxnn | ON | 70.48 | 132.0 | 132.4 | 4 |
| yolo26x.dxnn | OFF | 69.53 | 132.3 | 132.5 | 4 |

### Pose Estimation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-pose.dxnn | ON | 14.87 | 633.8 | 533.7 | 19 |
| yolo26n-pose.dxnn | OFF | 14.07 | 633.4 | 550.4 | 18 |
| yolo26s-pose.dxnn | ON | 22.83 | 406.1 | 407.3 | 13 |
| yolo26s-pose.dxnn | OFF | 22.09 | 405.8 | 407.8 | 13 |
| yolo26m-pose.dxnn | ON | 30.65 | 301.7 | 301.7 | 10 |
| yolo26m-pose.dxnn | OFF | 29.91 | 301.4 | 301.7 | 10 |
| yolo26l-pose.dxnn | ON | 39.65 | 226.1 | 226.9 | 7 |
| yolo26l-pose.dxnn | OFF | 38.99 | 226.6 | 227.1 | 7 |
| yolo26x-pose.dxnn | ON | 70.30 | 130.7 | 131.1 | 4 |
| yolo26x-pose.dxnn | OFF | 69.45 | 130.7 | 131.2 | 4 |

### Segmentation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-seg.dxnn | ON | 22.98 | 531.3 | 351.6 | 11 |
| yolo26n-seg.dxnn | OFF | 21.94 | 538.4 | 316.8 | 10 |
| yolo26s-seg.dxnn | ON | 32.57 | 340.2 | 319.0 | 10 |
| yolo26s-seg.dxnn | OFF | 31.46 | 339.8 | 312.7 | 10 |
| yolo26m-seg.dxnn | ON | 46.86 | 234.0 | 230.4 | 7 |
| yolo26m-seg.dxnn | OFF | 45.75 | 234.0 | 231.3 | 7 |
| yolo26l-seg.dxnn | ON | 55.93 | 185.7 | 185.1 | 6 |
| yolo26l-seg.dxnn | OFF | 54.59 | 185.5 | 185.0 | 6 |
| yolo26x-seg.dxnn | ON | 98.17 | 105.4 | 105.2 | 3 |
| yolo26x-seg.dxnn | OFF | 96.97 | 105.5 | 105.3 | 3 |

### Oriented BBox (OBB)

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-obb.dxnn | ON | 30.32 | 238.7 | 239.1 | 7 |
| yolo26n-obb.dxnn | OFF | 29.59 | 238.9 | 239.6 | 7 |
| yolo26s-obb.dxnn | ON | 49.98 | 148.1 | 148.1 | 4 |
| yolo26s-obb.dxnn | OFF | 49.07 | 148.1 | 148.0 | 4 |
| yolo26m-obb.dxnn | ON | 68.60 | 112.6 | 112.5 | 3 |
| yolo26m-obb.dxnn | OFF | 67.77 | 112.5 | 112.5 | 3 |
| yolo26l-obb.dxnn | ON | 90.66 | 83.4 | 83.6 | 2 |
| yolo26l-obb.dxnn | OFF | 89.60 | 83.6 | 83.6 | 2 |
| yolo26x-obb.dxnn | ON | 167.23 | 48.3 | 48.5 | 1 |
| yolo26x-obb.dxnn | OFF | 166.39 | 48.3 | 48.5 | 1 |

### Classification

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-cls.dxnn | ON | 1.15 | 11010.2 | 779.1 | — |
| yolo26n-cls.dxnn | OFF | 1.16 | 11011.6 | 783.6 | — |
| yolo26s-cls.dxnn | ON | 1.81 | 6437.7 | 780.7 | — |
| yolo26s-cls.dxnn | OFF | 1.89 | 6437.4 | 780.0 | — |
| yolo26m-cls.dxnn | ON | 2.35 | 5011.6 | 775.1 | — |
| yolo26m-cls.dxnn | OFF | 2.34 | 5013.1 | 774.5 | — |
| yolo26l-cls.dxnn | ON | 3.70 | 3207.6 | 767.2 | — |
| yolo26l-cls.dxnn | OFF | 3.72 | 3207.2 | 764.5 | — |
| yolo26x-cls.dxnn | ON | 6.66 | 1650.9 | 742.5 | — |
| yolo26x-cls.dxnn | OFF | 6.63 | 1650.0 | 744.6 | — |

## Environment

| Item | Value |
|------|-------|
| Product | BIOSTAR |
| Hostname | deepx-B650MT |
| OS | Ubuntu 22.04.5 LTS |
| Kernel | 6.8.0-124-generic |
| CPU | AMD Ryzen 5 9600X 6-Core Processor |
| CPU Cores | 12 |
| RAM | 30.5 GB |
| NPU SKU | H1 |
| NPU RT | v3.2.0 |
| NPU Driver (RT) | v2.1.0 |
| NPU Driver (PCIe) | v2.0.1 |
| NPU Firmware | v2.5.6 |
| NPU Memory | LPDDR5x 6000 Mbps, 3.92GiB |
| NPU Board | H1, Rev 0.0 |
| NPU PCIe | Gen3 X4 [04:00:00] |

### Tools

| Tool | Available | Version |
|------|-----------|---------|
| run_model | Yes | DXRT v3.2.0 run_model |
| gst-launch-1.0 | Yes | gst-launch-1.0 version 1.20.3 |
| gst-inspect-1.0 | Yes | gst-inspect-1.0 version 1.20.3 |
| dxtop | Yes | DX-TOP 1.0.1 |
| ffprobe | Yes | ffprobe version 4.4.2-0ubuntu0.22.04.1 Copyright (c) 2007-20... |

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
| yolo26n.dxnn | 654.5 ±1.2 | 194 | 92.0 | 100.0 | 43~46 | 1000 | ok |
| yolo26s.dxnn | 415.7 ±0.8 | 115 | 91.2 | 100.0 | 52~54 | 1000 | ok |
| yolo26m.dxnn | 309.2 ±0.1 | 80 | 91.8 | 100.0 | 54~57 | 1000 | ok |
| yolo26l.dxnn | 230.5 ±0.1 | 60 | 90.5 | 100.0 | 53~56 | 1000 | ok |
| yolo26x.dxnn | 132.0 ±0.1 | 36 | 90.7 | 100.0 | 54~57 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n.dxnn | 653.7 ±0.2 | 131 | 91.9 | 100.0 | 52~53 | 1000 | ok |
| yolo26s.dxnn | 416.5 ±0.2 | 79 | 93.2 | 100.0 | 52~54 | 1000 | ok |
| yolo26m.dxnn | 308.8 ±0.5 | 57 | 92.0 | 100.0 | 54~57 | 1000 | ok |
| yolo26l.dxnn | 230.6 ±0.1 | 43 | 89.8 | 100.0 | 54~56 | 1000 | ok |
| yolo26x.dxnn | 132.3 ±0.2 | 25 | 89.2 | 100.0 | 54~57 | 1000 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-pose.dxnn | 633.8 ±0.2 | 129 | 93.0 | 100.0 | 52~53 | 1000 | ok |
| yolo26s-pose.dxnn | 406.1 ±1.1 | 77 | 93.3 | 100.0 | 52~54 | 1000 | ok |
| yolo26m-pose.dxnn | 301.7 ±0.2 | 55 | 89.7 | 100.0 | 54~57 | 1000 | ok |
| yolo26l-pose.dxnn | 226.1 ±0.0 | 43 | 91.0 | 100.0 | 54~56 | 1000 | ok |
| yolo26x-pose.dxnn | 130.7 ±0.0 | 26 | 90.8 | 100.0 | 54~58 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-pose.dxnn | 633.4 ±0.1 | 84 | 91.5 | 100.0 | 52~54 | 1000 | ok |
| yolo26s-pose.dxnn | 405.8 ±0.4 | 51 | 93.0 | 100.0 | 52~54 | 1000 | ok |
| yolo26m-pose.dxnn | 301.4 ±0.6 | 37 | 92.0 | 100.0 | 54~57 | 1000 | ok |
| yolo26l-pose.dxnn | 226.6 ±0.3 | 29 | 92.3 | 100.0 | 54~57 | 1000 | ok |
| yolo26x-pose.dxnn | 130.7 ±0.1 | 18 | 91.6 | 100.0 | 54~57 | 1000 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-seg.dxnn | 531.3 ±0.4 | 503 | 84.6 | 97.9 | 52~54 | 1000 | ok |
| yolo26s-seg.dxnn | 340.2 ±0.1 | 297 | 91.0 | 100.0 | 53~55 | 1000 | ok |
| yolo26m-seg.dxnn | 234.0 ±0.4 | 195 | 89.6 | 100.0 | 55~59 | 1000 | ok |
| yolo26l-seg.dxnn | 185.7 ±0.1 | 151 | 92.9 | 100.0 | 55~58 | 1000 | ok |
| yolo26x-seg.dxnn | 105.4 ±0.3 | 83 | 89.2 | 100.0 | 55~59 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-seg.dxnn | 538.4 ±0.2 | 400 | 88.1 | 98.9 | 52~54 | 1000 | ok |
| yolo26s-seg.dxnn | 339.8 ±0.5 | 245 | 91.1 | 100.0 | 53~55 | 1000 | ok |
| yolo26m-seg.dxnn | 234.0 ±0.1 | 162 | 91.9 | 100.0 | 55~59 | 1000 | ok |
| yolo26l-seg.dxnn | 185.5 ±0.5 | 127 | 92.8 | 100.0 | 55~58 | 1000 | ok |
| yolo26x-seg.dxnn | 105.5 ±0.4 | 71 | 89.2 | 100.0 | 55~59 | 1000 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-obb.dxnn | 238.7 ±0.4 | 48 | 92.6 | 100.0 | 52~53 | 1000 | ok |
| yolo26s-obb.dxnn | 148.1 ±0.4 | 32 | 89.1 | 100.0 | 52~54 | 1000 | ok |
| yolo26m-obb.dxnn | 112.6 ±0.0 | 26 | 89.8 | 100.0 | 54~56 | 1000 | ok |
| yolo26l-obb.dxnn | 83.4 ±0.1 | 19 | 91.8 | 100.0 | 53~55 | 1000 | ok |
| yolo26x-obb.dxnn | 48.3 ±0.1 | 12 | 90.1 | 100.0 | 53~56 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-obb.dxnn | 238.9 ±0.2 | 34 | 91.3 | 100.0 | 52~53 | 1000 | ok |
| yolo26s-obb.dxnn | 148.1 ±0.2 | 23 | 92.7 | 100.0 | 52~54 | 1000 | ok |
| yolo26m-obb.dxnn | 112.5 ±0.1 | 18 | 90.1 | 100.0 | 53~56 | 1000 | ok |
| yolo26l-obb.dxnn | 83.6 ±0.0 | 13 | 91.1 | 100.0 | 53~55 | 1000 | ok |
| yolo26x-obb.dxnn | 48.3 ±0.0 | 8 | 89.7 | 100.0 | 53~56 | 1000 | ok |

#### Classification

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-cls.dxnn | 11010.2 ±4.6 | 51 | 89.4 | 97.9 | 51 | 1000 | ok |
| yolo26s-cls.dxnn | 6437.7 ±1.4 | 30 | 91.0 | 98.7 | 52~53 | 1000 | ok |
| yolo26m-cls.dxnn | 5011.6 ±3.7 | 24 | 90.5 | 99.1 | 53~56 | 1000 | ok |
| yolo26l-cls.dxnn | 3207.6 ±1.8 | 15 | 90.9 | 99.7 | 53~55 | 1000 | ok |
| yolo26x-cls.dxnn | 1650.9 ±0.7 | 8 | 91.0 | 100.0 | 54~56 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-cls.dxnn | 11011.6 ±3.6 | 51 | 90.0 | 97.9 | 51~52 | 1000 | ok |
| yolo26s-cls.dxnn | 6437.4 ±1.2 | 30 | 91.0 | 98.7 | 52~53 | 1000 | ok |
| yolo26m-cls.dxnn | 5013.1 ±3.4 | 24 | 90.4 | 99.0 | 53~55 | 1000 | ok |
| yolo26l-cls.dxnn | 3207.2 ±1.8 | 15 | 91.8 | 99.7 | 53~54 | 1000 | ok |
| yolo26x-cls.dxnn | 1650.0 ±0.6 | 8 | 91.7 | 100.0 | 53~56 | 1000 | ok |

### Latency (Single-Core, Sync)

#### Object Detection

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n.dxnn | 63.4 | 15.76 | 14.92 | 0.84 | 39 | ok |
| yolo26s.dxnn | 42.5 | 23.53 | 22.64 | 0.89 | 50 | ok |
| yolo26m.dxnn | 32.0 | 31.22 | 30.29 | 0.92 | 49 | ok |
| yolo26l.dxnn | 24.9 | 40.11 | 39.19 | 0.92 | 49 | ok |
| yolo26x.dxnn | 14.2 | 70.48 | 69.53 | 0.96 | 49 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n.dxnn | 66.4 | 15.06 | 15.06 | 50 | ok |
| yolo26s.dxnn | 44.1 | 22.66 | 22.66 | 50 | ok |
| yolo26m.dxnn | 33.1 | 30.24 | 30.24 | 50 | ok |
| yolo26l.dxnn | 25.6 | 39.11 | 39.11 | 50 | ok |
| yolo26x.dxnn | 14.4 | 69.53 | 69.53 | 49 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-pose.dxnn | 67.2 | 14.87 | 14.12 | 0.76 | 50 | ok |
| yolo26s-pose.dxnn | 43.8 | 22.83 | 22.06 | 0.77 | 50 | ok |
| yolo26m-pose.dxnn | 32.6 | 30.65 | 29.86 | 0.79 | 50 | ok |
| yolo26l-pose.dxnn | 25.2 | 39.65 | 38.87 | 0.78 | 50 | ok |
| yolo26x-pose.dxnn | 14.2 | 70.30 | 69.47 | 0.83 | 49 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-pose.dxnn | 71.1 | 14.07 | 14.07 | 50 | ok |
| yolo26s-pose.dxnn | 45.3 | 22.09 | 22.09 | 49 | ok |
| yolo26m-pose.dxnn | 33.4 | 29.91 | 29.91 | 50 | ok |
| yolo26l-pose.dxnn | 25.6 | 38.99 | 38.99 | 49 | ok |
| yolo26x-pose.dxnn | 14.4 | 69.45 | 69.45 | 49 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-seg.dxnn | 43.5 | 22.98 | 21.92 | 1.06 | 49 | ok |
| yolo26s-seg.dxnn | 30.7 | 32.57 | 31.50 | 1.07 | 50 | ok |
| yolo26m-seg.dxnn | 21.3 | 46.86 | 45.77 | 1.09 | 50 | ok |
| yolo26l-seg.dxnn | 17.9 | 55.93 | 54.78 | 1.15 | 49 | ok |
| yolo26x-seg.dxnn | 10.2 | 98.17 | 97.06 | 1.12 | 49 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-seg.dxnn | 45.6 | 21.94 | 21.94 | 50 | ok |
| yolo26s-seg.dxnn | 31.8 | 31.46 | 31.46 | 49 | ok |
| yolo26m-seg.dxnn | 21.9 | 45.75 | 45.75 | 50 | ok |
| yolo26l-seg.dxnn | 18.3 | 54.59 | 54.59 | 49 | ok |
| yolo26x-seg.dxnn | 10.3 | 96.97 | 96.97 | 49 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-obb.dxnn | 33.0 | 30.32 | 29.51 | 0.81 | 49 | ok |
| yolo26s-obb.dxnn | 20.0 | 49.98 | 49.05 | 0.93 | 49 | ok |
| yolo26m-obb.dxnn | 14.6 | 68.60 | 67.69 | 0.91 | 49 | ok |
| yolo26l-obb.dxnn | 11.0 | 90.66 | 89.69 | 0.97 | 49 | ok |
| yolo26x-obb.dxnn | 6.0 | 167.23 | 166.27 | 0.96 | 48 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-obb.dxnn | 33.8 | 29.59 | 29.59 | 50 | ok |
| yolo26s-obb.dxnn | 20.4 | 49.07 | 49.07 | 49 | ok |
| yolo26m-obb.dxnn | 14.8 | 67.77 | 67.77 | 49 | ok |
| yolo26l-obb.dxnn | 11.2 | 89.60 | 89.60 | 49 | ok |
| yolo26x-obb.dxnn | 6.0 | 166.39 | 166.39 | 48 | ok |

#### Classification

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-cls.dxnn | 869.9 | 1.15 | 1.15 | N/A | 50 | ok |
| yolo26s-cls.dxnn | 553.9 | 1.81 | 1.81 | N/A | 50 | ok |
| yolo26m-cls.dxnn | 425.9 | 2.35 | 2.35 | N/A | 50 | ok |
| yolo26l-cls.dxnn | 270.5 | 3.70 | 3.70 | N/A | 50 | ok |
| yolo26x-cls.dxnn | 150.2 | 6.66 | 6.66 | N/A | 50 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-cls.dxnn | 865.4 | 1.16 | 1.16 | 50 | ok |
| yolo26s-cls.dxnn | 530.4 | 1.89 | 1.89 | 50 | ok |
| yolo26m-cls.dxnn | 427.5 | 2.34 | 2.34 | 50 | ok |
| yolo26l-cls.dxnn | 268.6 | 3.72 | 3.72 | 50 | ok |
| yolo26x-cls.dxnn | 150.9 | 6.63 | 6.63 | 50 | ok |

## E2E Pipeline (Single-Stream)

### Object Detection

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | vaapidecodebin | 3455 | 3 | 484.9 ±1.7 | 7.12 | 255 | 38.1 | 78.1 | 46 | 1000 | 375 | ok |
| yolo26s.dxnn | vaapidecodebin | 3455 | 3 | 418.2 ±0.8 | 8.26 | 215 | 76.2 | 100.0 | 54~55 | 1000 | 498 | ok |
| yolo26m.dxnn | vaapidecodebin | 3455 | 3 | 307.5 ±0.5 | 11.24 | 138 | 81.6 | 100.0 | 57~58 | 1000 | 530 | ok |
| yolo26l.dxnn | vaapidecodebin | 3455 | 3 | 230.5 ±0.3 | 14.99 | 96 | 84.5 | 100.0 | 57~58 | 1000 | 544 | ok |
| yolo26x.dxnn | vaapidecodebin | 3455 | 3 | 132.4 ±0.1 | 26.09 | 50 | 90.3 | 100.0 | 59~61 | 1000 | 590 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | vaapidecodebin | 3455 | 3 | 441.8 ±0.4 | 7.82 | 282 | 33.7 | 69.5 | 52~53 | 1000 | 471 | ok |
| yolo26s.dxnn | vaapidecodebin | 3455 | 3 | 418.4 ±0.9 | 8.26 | 266 | 74.8 | 100.0 | 54 | 1000 | 569 | ok |
| yolo26m.dxnn | vaapidecodebin | 3455 | 3 | 307.7 ±1.5 | 11.23 | 174 | 77.5 | 100.0 | 57~58 | 1000 | 591 | ok |
| yolo26l.dxnn | vaapidecodebin | 3455 | 3 | 230.9 ±0.3 | 14.96 | 122 | 84.7 | 100.0 | 57~58 | 1000 | 603 | ok |
| yolo26x.dxnn | vaapidecodebin | 3455 | 3 | 132.5 ±0.1 | 26.08 | 65 | 88.4 | 100.0 | 59~61 | 1000 | 646 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n.dxnn | 484.9 | 441.8 | +43.1 | +9.8% |
| yolo26s.dxnn | 418.2 | 418.4 | -0.2 | -0.0% |
| yolo26m.dxnn | 307.5 | 307.7 | -0.2 | -0.1% |
| yolo26l.dxnn | 230.5 | 230.9 | -0.4 | -0.2% |
| yolo26x.dxnn | 132.4 | 132.5 | -0.0 | -0.0% |

### Pose Estimation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | vaapidecodebin | 3455 | 3 | 533.7 ±0.6 | 6.47 | 199 | 44.7 | 88.4 | 53 | 1000 | 355 | ok |
| yolo26s-pose.dxnn | vaapidecodebin | 3455 | 3 | 407.3 ±1.1 | 8.48 | 141 | 75.5 | 100.0 | 55 | 1000 | 445 | ok |
| yolo26m-pose.dxnn | vaapidecodebin | 3455 | 3 | 301.7 ±0.4 | 11.45 | 98 | 79.9 | 100.0 | 58 | 1000 | 478 | ok |
| yolo26l-pose.dxnn | vaapidecodebin | 3455 | 3 | 226.9 ±0.2 | 15.23 | 68 | 85.8 | 100.0 | 57~58 | 1000 | 495 | ok |
| yolo26x-pose.dxnn | vaapidecodebin | 3455 | 3 | 131.1 ±0.1 | 26.35 | 38 | 88.8 | 100.0 | 60~62 | 1000 | 544 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | vaapidecodebin | 3455 | 3 | 550.4 ±0.9 | 6.28 | 159 | 44.1 | 86.4 | 53 | 1000 | 351 | ok |
| yolo26s-pose.dxnn | vaapidecodebin | 3455 | 3 | 407.8 ±1.3 | 8.47 | 112 | 75.5 | 100.0 | 54 | 1000 | 474 | ok |
| yolo26m-pose.dxnn | vaapidecodebin | 3455 | 3 | 301.7 ±0.7 | 11.45 | 77 | 82.4 | 100.0 | 57~58 | 1000 | 508 | ok |
| yolo26l-pose.dxnn | vaapidecodebin | 3455 | 3 | 227.1 ±0.2 | 15.21 | 54 | 83.1 | 100.0 | 58~59 | 1000 | 520 | ok |
| yolo26x-pose.dxnn | vaapidecodebin | 3455 | 3 | 131.2 ±0.1 | 26.34 | 30 | 89.8 | 100.0 | 59~61 | 1000 | 560 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-pose.dxnn | 533.7 | 550.4 | -16.7 | -3.0% |
| yolo26s-pose.dxnn | 407.3 | 407.8 | -0.5 | -0.1% |
| yolo26m-pose.dxnn | 301.7 | 301.7 | -0.0 | -0.0% |
| yolo26l-pose.dxnn | 226.9 | 227.1 | -0.2 | -0.1% |
| yolo26x-pose.dxnn | 131.1 | 131.2 | -0.0 | -0.0% |

### Segmentation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | vaapidecodebin | 3455 | 3 | 351.6 ±0.1 | 9.83 | 572 | 32.8 | 66.0 | 54 | 1000 | 733 | ok |
| yolo26s-seg.dxnn | vaapidecodebin | 3455 | 3 | 319.0 ±0.9 | 10.83 | 468 | 68.8 | 95.5 | 56 | 1000 | 776 | ok |
| yolo26m-seg.dxnn | vaapidecodebin | 3455 | 3 | 230.4 ±0.8 | 15.00 | 269 | 81.3 | 100.0 | 61~62 | 1000 | 814 | ok |
| yolo26l-seg.dxnn | vaapidecodebin | 3455 | 3 | 185.1 ±0.0 | 18.66 | 199 | 85.4 | 100.0 | 60~62 | 1000 | 831 | ok |
| yolo26x-seg.dxnn | vaapidecodebin | 3455 | 3 | 105.2 ±0.3 | 32.83 | 109 | 89.6 | 100.0 | 63~66 | 1000 | 878 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | vaapidecodebin | 3455 | 3 | 316.8 ±0.5 | 10.91 | 458 | 28.0 | 68.8 | 54 | 1000 | 716 | ok |
| yolo26s-seg.dxnn | vaapidecodebin | 3455 | 3 | 312.7 ±0.1 | 11.05 | 452 | 67.1 | 92.1 | 56 | 1000 | 874 | ok |
| yolo26m-seg.dxnn | vaapidecodebin | 3455 | 3 | 231.3 ±0.2 | 14.94 | 289 | 85.2 | 100.0 | 61~62 | 1000 | 911 | ok |
| yolo26l-seg.dxnn | vaapidecodebin | 3455 | 3 | 185.0 ±0.2 | 18.67 | 218 | 85.6 | 100.0 | 60~61 | 1000 | 922 | ok |
| yolo26x-seg.dxnn | vaapidecodebin | 3455 | 3 | 105.3 ±0.1 | 32.81 | 119 | 89.6 | 100.0 | 62~65 | 1000 | 968 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-seg.dxnn | 351.6 | 316.8 | +34.8 | +11.0% |
| yolo26s-seg.dxnn | 319.0 | 312.7 | +6.3 | +2.0% |
| yolo26m-seg.dxnn | 230.4 | 231.3 | -0.9 | -0.4% |
| yolo26l-seg.dxnn | 185.1 | 185.0 | +0.1 | +0.0% |
| yolo26x-seg.dxnn | 105.2 | 105.3 | -0.1 | -0.0% |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | vaapidecodebin | 2640 | 3 | 239.1 ±1.0 | 11.04 | 102 | 80.3 | 100.0 | 53 | 1000 | 535 | ok |
| yolo26s-obb.dxnn | vaapidecodebin | 2640 | 3 | 148.1 ±0.0 | 17.83 | 58 | 83.9 | 100.0 | 54~55 | 1000 | 552 | ok |
| yolo26m-obb.dxnn | vaapidecodebin | 2640 | 3 | 112.5 ±0.0 | 23.47 | 44 | 87.2 | 100.0 | 58~59 | 1000 | 584 | ok |
| yolo26l-obb.dxnn | vaapidecodebin | 2640 | 3 | 83.6 ±0.1 | 31.57 | 33 | 90.1 | 100.0 | 57~59 | 1000 | 601 | ok |
| yolo26x-obb.dxnn | vaapidecodebin | 2640 | 3 | 48.5 ±0.0 | 54.45 | 20 | 93.3 | 100.0 | 60~63 | 1000 | 649 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | vaapidecodebin | 2640 | 3 | 239.6 ±0.2 | 11.02 | 106 | 77.8 | 100.0 | 53~54 | 1000 | 552 | ok |
| yolo26s-obb.dxnn | vaapidecodebin | 2640 | 3 | 148.0 ±0.1 | 17.84 | 60 | 85.8 | 100.0 | 54~55 | 1000 | 575 | ok |
| yolo26m-obb.dxnn | vaapidecodebin | 2640 | 3 | 112.5 ±0.1 | 23.46 | 46 | 86.5 | 100.0 | 57~59 | 1000 | 608 | ok |
| yolo26l-obb.dxnn | vaapidecodebin | 2640 | 3 | 83.6 ±0.1 | 31.58 | 34 | 91.4 | 100.0 | 57~59 | 1000 | 626 | ok |
| yolo26x-obb.dxnn | vaapidecodebin | 2640 | 3 | 48.5 ±0.1 | 54.48 | 21 | 93.6 | 100.0 | 60~63 | 1000 | 673 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-obb.dxnn | 239.1 | 239.6 | -0.5 | -0.2% |
| yolo26s-obb.dxnn | 148.1 | 148.0 | +0.1 | +0.1% |
| yolo26m-obb.dxnn | 112.5 | 112.5 | -0.1 | -0.1% |
| yolo26l-obb.dxnn | 83.6 | 83.6 | +0.0 | +0.0% |
| yolo26x-obb.dxnn | 48.5 | 48.5 | +0.0 | +0.1% |

### Classification

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-cls.dxnn | vaapidecodebin | 3455 | 3 | 779.1 ±9.2 | 4.43 | 41 | 3.5 | 18.9 | 50 | 1000 | 174 | ok |
| yolo26s-cls.dxnn | vaapidecodebin | 3455 | 3 | 780.7 ±4.0 | 4.43 | 40 | 6.3 | 31.8 | 52 | 1000 | 186 | ok |
| yolo26m-cls.dxnn | vaapidecodebin | 3455 | 3 | 775.1 ±0.6 | 4.46 | 41 | 8.8 | 41.8 | 54 | 1000 | 197 | ok |
| yolo26l-cls.dxnn | vaapidecodebin | 3455 | 3 | 767.2 ±0.9 | 4.50 | 41 | 14.3 | 66.9 | 53~54 | 1000 | 208 | ok |
| yolo26x-cls.dxnn | vaapidecodebin | 3455 | 3 | 742.5 ±9.2 | 4.65 | 44 | 24.6 | 61.8 | 54~55 | 1000 | 304 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-cls.dxnn | vaapidecodebin | 3455 | 3 | 783.6 ±4.6 | 4.41 | 40 | 3.6 | 18.9 | 51 | 1000 | 176 | ok |
| yolo26s-cls.dxnn | vaapidecodebin | 3455 | 3 | 780.0 ±2.8 | 4.43 | 40 | 6.9 | 32.0 | 52 | 1000 | 181 | ok |
| yolo26m-cls.dxnn | vaapidecodebin | 3455 | 3 | 774.5 ±3.3 | 4.46 | 41 | 9.1 | 41.8 | 54 | 1000 | 197 | ok |
| yolo26l-cls.dxnn | vaapidecodebin | 3455 | 3 | 764.5 ±4.7 | 4.52 | 42 | 14.3 | 66.6 | 53 | 1000 | 212 | ok |
| yolo26x-cls.dxnn | vaapidecodebin | 3455 | 3 | 744.6 ±3.4 | 4.64 | 44 | 27.1 | 61.5 | 54~55 | 1000 | 261 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-cls.dxnn | 779.1 | 783.6 | -4.5 | -0.6% |
| yolo26s-cls.dxnn | 780.7 | 780.0 | +0.7 | +0.1% |
| yolo26m-cls.dxnn | 775.1 | 774.5 | +0.7 | +0.1% |
| yolo26l-cls.dxnn | 767.2 | 764.5 | +2.8 | +0.4% |
| yolo26x-cls.dxnn | 742.5 | 744.6 | -2.1 | -0.3% |

## E2E Pipeline (Multi-Stream)

### Object Detection

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | 16 | 3 | 514.1 ±1.4 | 32.1 | 361 | 56.4 | 82.0 | 51~55 | 1000 | 749 | ok |
| yolo26n.dxnn | 17 | 1/3 | 510.9 | 30.1 | 363 | 55.7 | 83.8 | 57 | 1000 | 763 | partial |
| yolo26s.dxnn | 13 | 3 | 417.4 ±0.1 | 32.1 | 251 | 95.0 | 100.0 | 60~63 | 1000 | 735 | ok |
| yolo26s.dxnn | 14 | 3 | 418.0 ±0.2 | 29.9 | 254 | 95.4 | 100.0 | 64~65 | 1000 | 718 | ok |
| yolo26m.dxnn | 10 | 3 | 308.1 ±0.1 | 30.8 | 155 | 96.2 | 100.0 | 65~69 | 1000 | 686 | ok |
| yolo26m.dxnn | 11 | 3 | 307.7 ±0.3 | 28.0 | 156 | 96.6 | 100.0 | 71~72 | 1000 | 718 | ok |
| yolo26l.dxnn | 7 | 3 | 230.8 ±0.1 | 33.0 | 106 | 95.7 | 100.0 | 64~67 | 1000 | 649 | ok |
| yolo26l.dxnn | 8 | 3 | 231.1 ±0.2 | 28.9 | 105 | 96.4 | 100.0 | 69~70 | 1000 | 674 | ok |
| yolo26x.dxnn | 4 | 3 | 132.5 ±0.0 | 33.1 | 52 | 96.2 | 100.0 | 66~69 | 1000 | 645 | ok |
| yolo26x.dxnn | 5 | 3 | 132.5 ±0.1 | 26.5 | 53 | 96.8 | 100.0 | 71~72 | 1000 | 670 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | 14 | 3 | 435.5 ±2.0 | 31.1 | 299 | 42.6 | 72.6 | 54~56 | 1000 | 789 | ok |
| yolo26n.dxnn | 15 | 2/3 | 433.8 ±0.4 | 28.9 | 298 | 42.6 | 70.7 | 57 | 1000 | 828 | partial |
| yolo26s.dxnn | 13 | 3 | 418.7 ±0.2 | 32.2 | 303 | 95.7 | 100.0 | 60~63 | 1000 | 811 | ok |
| yolo26s.dxnn | 14 | 2/3 | 418.6 ±0.6 | 29.9 | 304 | 95.8 | 100.0 | 65 | 1000 | 852 | partial |
| yolo26m.dxnn | 10 | 3 | 308.3 ±0.1 | 30.8 | 194 | 96.2 | 100.0 | 65~69 | 1000 | 802 | ok |
| yolo26m.dxnn | 11 | 3 | 308.3 ±0.2 | 28.0 | 195 | 96.8 | 100.0 | 71~72 | 1000 | 797 | ok |
| yolo26l.dxnn | 7 | 3 | 231.3 ±0.0 | 33.0 | 133 | 95.8 | 100.0 | 64~68 | 1000 | 746 | ok |
| yolo26l.dxnn | 8 | 3 | 231.3 ±0.1 | 28.9 | 133 | 96.3 | 100.0 | 70~71 | 1000 | 750 | ok |
| yolo26x.dxnn | 4 | 3 | 132.6 ±0.1 | 33.1 | 68 | 95.7 | 100.0 | 67~70 | 1000 | 714 | ok |
| yolo26x.dxnn | 5 | 3 | 132.4 ±0.2 | 26.5 | 68 | 96.9 | 100.0 | 71~72 | 1000 | 744 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n.dxnn | 17+ | 30.1 | 14 | 31.1 |
| yolo26s.dxnn | 13 | 32.1 | 13 | 32.2 |
| yolo26m.dxnn | 10 | 30.8 | 10 | 30.8 |
| yolo26l.dxnn | 7 | 33.0 | 7 | 33.0 |
| yolo26x.dxnn | 4 | 33.1 | 4 | 33.1 |

> **+** 표시: 마지막 측정 스트림에서도 기준 FPS를 만족함. 스위프가 FPS 임계값 미달전에 중단된 경우로, 실제 최대 처리 가능 스트림 수는 더 클 수 있음.

### Pose Estimation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | 17 | 3 | 580.0 ±0.8 | 34.1 | 279 | 73.5 | 90.1 | 56~59 | 1000 | 726 | ok |
| yolo26n-pose.dxnn | 18 | 3 | 579.0 ±1.0 | 32.2 | 279 | 72.9 | 89.4 | 60~61 | 1000 | 747 | ok |
| yolo26n-pose.dxnn | 19 | 3 | 580.7 ±0.5 | 30.6 | 278 | 73.8 | 89.2 | 54~62 | 1000 | 766 | ok |
| yolo26n-pose.dxnn | 20 | 3 | 578.6 ±0.1 | 28.9 | 279 | 73.3 | 91.3 | 61~62 | 1000 | 774 | ok |
| yolo26s-pose.dxnn | 13 | 3 | 407.2 ±0.2 | 31.3 | 163 | 95.4 | 100.0 | 60~63 | 1000 | 693 | ok |
| yolo26s-pose.dxnn | 14 | 3 | 407.4 ±0.4 | 29.1 | 165 | 96.0 | 100.0 | 65 | 1000 | 680 | ok |
| yolo26m-pose.dxnn | 10 | 3 | 302.0 ±0.1 | 30.2 | 109 | 96.0 | 100.0 | 66~69 | 1000 | 641 | ok |
| yolo26m-pose.dxnn | 11 | 3 | 301.9 ±0.3 | 27.4 | 109 | 96.4 | 100.0 | 71~72 | 1000 | 676 | ok |
| yolo26l-pose.dxnn | 7 | 3 | 227.3 ±0.2 | 32.5 | 75 | 96.3 | 100.0 | 65~68 | 1000 | 608 | ok |
| yolo26l-pose.dxnn | 8 | 3 | 227.3 ±0.1 | 28.4 | 76 | 97.1 | 100.0 | 70~71 | 1000 | 636 | ok |
| yolo26x-pose.dxnn | 4 | 3 | 131.2 ±0.0 | 32.8 | 40 | 96.8 | 100.0 | 68~71 | 1000 | 606 | ok |
| yolo26x-pose.dxnn | 5 | 3 | 131.2 ±0.1 | 26.2 | 40 | 97.4 | 100.0 | 73~74 | 1000 | 632 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | 18 | 2/3 | 596.7 ±1.2 | 33.1 | 226 | 78.2 | 93.3 | 48~50 | 1000 | 780 | partial |
| yolo26n-pose.dxnn | 17 | 2/3 | 594.7 ±0.5 | 35.0 | 226 | 78.1 | 92.1 | 54~56 | 1000 | 759 | partial |
| yolo26n-pose.dxnn | 16 | 3 | 594.2 ±0.2 | 37.1 | 229 | 77.7 | 93.8 | 59~61 | 1000 | 741 | ok |
| yolo26s-pose.dxnn | 13 | 3 | 407.5 ±0.5 | 31.3 | 131 | 95.6 | 100.0 | 59~62 | 1000 | 730 | ok |
| yolo26s-pose.dxnn | 14 | 3 | 407.5 ±0.3 | 29.1 | 131 | 96.0 | 100.0 | 64 | 1000 | 715 | ok |
| yolo26m-pose.dxnn | 10 | 3 | 302.4 ±0.2 | 30.2 | 87 | 95.9 | 100.0 | 65~69 | 1000 | 683 | ok |
| yolo26m-pose.dxnn | 11 | 3 | 302.3 ±0.1 | 27.5 | 88 | 96.6 | 100.0 | 71~72 | 1000 | 712 | ok |
| yolo26l-pose.dxnn | 7 | 3 | 227.5 ±0.1 | 32.5 | 61 | 96.4 | 100.0 | 65~68 | 1000 | 636 | ok |
| yolo26l-pose.dxnn | 8 | 3 | 227.5 ±0.1 | 28.4 | 61 | 97.0 | 100.0 | 71~72 | 1000 | 671 | ok |
| yolo26x-pose.dxnn | 4 | 3 | 131.2 ±0.1 | 32.8 | 32 | 96.9 | 100.0 | 68~71 | 1000 | 627 | ok |
| yolo26x-pose.dxnn | 5 | 3 | 131.2 ±0.0 | 26.2 | 32 | 97.1 | 100.0 | 72~74 | 1000 | 652 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-pose.dxnn | 19 | 30.6 | 18+ | 33.1 |
| yolo26s-pose.dxnn | 13 | 31.3 | 13 | 31.3 |
| yolo26m-pose.dxnn | 10 | 30.2 | 10 | 30.2 |
| yolo26l-pose.dxnn | 7 | 32.5 | 7 | 32.5 |
| yolo26x-pose.dxnn | 4 | 32.8 | 4 | 32.8 |

> **+** 표시: 마지막 측정 스트림에서도 기준 FPS를 만족함. 스위프가 FPS 임계값 미달전에 중단된 경우로, 실제 최대 처리 가능 스트림 수는 더 클 수 있음.

### Segmentation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | 11 | 3 | 350.0 ±1.6 | 31.8 | 666 | 43.1 | 73.0 | 57~59 | 1000 | 998 | ok |
| yolo26n-seg.dxnn | 12 | 3 | 354.9 ±5.6 | 29.6 | 664 | 43.8 | 74.3 | 60 | 1000 | 1030 | ok |
| yolo26s-seg.dxnn | 10 | 3 | 317.5 ±0.5 | 31.8 | 510 | 82.7 | 95.7 | 62~66 | 1000 | 977 | ok |
| yolo26s-seg.dxnn | 11 | 3 | 316.7 ±1.1 | 28.8 | 517 | 82.9 | 96.1 | 67~68 | 1000 | 1011 | ok |
| yolo26m-seg.dxnn | 7 | 3 | 230.9 ±0.2 | 33.0 | 291 | 94.8 | 100.0 | 71~76 | 1000 | 968 | ok |
| yolo26m-seg.dxnn | 8 | 3 | 231.4 ±0.3 | 28.9 | 291 | 95.3 | 100.0 | 78~80 | 1000 | 993 | ok |
| yolo26l-seg.dxnn | 6 | 3 | 185.2 ±0.1 | 30.9 | 207 | 95.8 | 100.0 | 70~74 | 1000 | 952 | ok |
| yolo26l-seg.dxnn | 7 | 3 | 185.3 ±0.1 | 26.5 | 210 | 95.6 | 100.0 | 77~78 | 1000 | 980 | ok |
| yolo26x-seg.dxnn | 3 | 3 | 105.2 ±0.1 | 35.0 | 111 | 94.9 | 100.0 | 72~76 | 1000 | 940 | ok |
| yolo26x-seg.dxnn | 4 | 3 | 105.3 ±0.2 | 26.3 | 111 | 96.1 | 100.0 | 79 | 800~1000 | 962 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | 10 | 3 | 311.0 ±0.8 | 31.1 | 474 | 32.6 | 82.6 | 56~58 | 1000 | 1030 | ok |
| yolo26n-seg.dxnn | 11 | 3 | 308.1 ±1.3 | 28.0 | 479 | 32.3 | 86.1 | 58~59 | 1000 | 1090 | ok |
| yolo26s-seg.dxnn | 10 | 3 | 306.3 ±1.5 | 30.6 | 465 | 75.5 | 90.8 | 62~65 | 1000 | 1121 | ok |
| yolo26s-seg.dxnn | 11 | 3 | 300.9 ±0.8 | 27.4 | 474 | 72.2 | 91.5 | 66~67 | 1000 | 1128 | ok |
| yolo26m-seg.dxnn | 7 | 3 | 231.6 ±0.0 | 33.1 | 309 | 95.1 | 100.0 | 71~76 | 1000 | 1081 | ok |
| yolo26m-seg.dxnn | 8 | 3 | 231.6 ±0.1 | 28.9 | 311 | 95.5 | 100.0 | 79~80 | 1000 | 1092 | ok |
| yolo26l-seg.dxnn | 6 | 3 | 185.1 ±0.1 | 30.8 | 226 | 95.8 | 100.0 | 69~74 | 1000 | 1066 | ok |
| yolo26l-seg.dxnn | 7 | 3 | 185.2 ±0.1 | 26.5 | 227 | 95.9 | 100.0 | 77~78 | 1000 | 1087 | ok |
| yolo26x-seg.dxnn | 3 | 3 | 105.4 ±0.2 | 35.1 | 121 | 95.1 | 100.0 | 72~76 | 1000 | 1035 | ok |
| yolo26x-seg.dxnn | 4 | 3 | 105.2 ±0.5 | 26.3 | 121 | 95.8 | 100.0 | 78~79 | 800~1000 | 1058 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-seg.dxnn | 11 | 31.8 | 10 | 31.1 |
| yolo26s-seg.dxnn | 10 | 31.8 | 10 | 30.6 |
| yolo26m-seg.dxnn | 7 | 33.0 | 7 | 33.1 |
| yolo26l-seg.dxnn | 6 | 30.9 | 6 | 30.8 |
| yolo26x-seg.dxnn | 3 | 35.0 | 3 | 35.1 |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | 7 | 3 | 238.9 ±0.3 | 34.1 | 113 | 94.9 | 100.0 | 56~58 | 1000 | 658 | ok |
| yolo26n-obb.dxnn | 8 | 3 | 239.1 ±0.1 | 29.9 | 114 | 95.7 | 100.0 | 60~61 | 1000 | 694 | ok |
| yolo26s-obb.dxnn | 4 | 3 | 148.0 ±0.1 | 37.0 | 62 | 94.2 | 100.0 | 58~60 | 1000 | 621 | ok |
| yolo26s-obb.dxnn | 5 | 3 | 148.2 ±0.1 | 29.6 | 62 | 95.1 | 100.0 | 61~62 | 1000 | 648 | ok |
| yolo26m-obb.dxnn | 3 | 3 | 112.6 ±0.1 | 37.5 | 47 | 93.3 | 100.0 | 63~65 | 1000 | 642 | ok |
| yolo26m-obb.dxnn | 4 | 3 | 112.7 ±0.0 | 28.2 | 47 | 94.5 | 100.0 | 67~69 | 1000 | 659 | ok |
| yolo26l-obb.dxnn | 2 | 3 | 83.7 ±0.0 | 41.9 | 34 | 94.5 | 100.0 | 62~64 | 1000 | 632 | ok |
| yolo26l-obb.dxnn | 3 | 3 | 83.7 ±0.0 | 27.9 | 35 | 96.1 | 100.0 | 66~67 | 1000 | 661 | ok |
| yolo26x-obb.dxnn | 1 | 3 | 48.5 ±0.0 | 48.5 | 20 | 93.3 | 100.0 | 60~63 | 1000 | 649 | ok |
| yolo26x-obb.dxnn | 2 | 3 | 48.5 ±0.0 | 24.3 | 21 | 95.7 | 100.0 | 66~68 | 1000 | 680 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | 7 | 3 | 239.3 ±0.3 | 34.2 | 116 | 95.5 | 100.0 | 57~58 | 1000 | 688 | ok |
| yolo26n-obb.dxnn | 8 | 3 | 239.5 ±0.3 | 29.9 | 117 | 95.5 | 100.0 | 60~61 | 1000 | 719 | ok |
| yolo26s-obb.dxnn | 4 | 3 | 148.0 ±0.2 | 37.0 | 65 | 94.1 | 100.0 | 58~60 | 1000 | 648 | ok |
| yolo26s-obb.dxnn | 5 | 3 | 148.3 ±0.0 | 29.6 | 64 | 94.8 | 100.0 | 61~62 | 1000 | 677 | ok |
| yolo26m-obb.dxnn | 3 | 3 | 112.6 ±0.1 | 37.5 | 48 | 93.7 | 100.0 | 62~65 | 1000 | 666 | ok |
| yolo26m-obb.dxnn | 4 | 3 | 112.7 ±0.0 | 28.2 | 48 | 94.3 | 100.0 | 67~68 | 1000 | 685 | ok |
| yolo26l-obb.dxnn | 2 | 3 | 83.7 ±0.0 | 41.9 | 36 | 95.8 | 100.0 | 62~64 | 1000 | 657 | ok |
| yolo26l-obb.dxnn | 3 | 3 | 83.7 ±0.1 | 27.9 | 36 | 96.6 | 100.0 | 66~67 | 1000 | 681 | ok |
| yolo26x-obb.dxnn | 1 | 3 | 48.5 ±0.1 | 48.5 | 21 | 93.6 | 100.0 | 60~63 | 1000 | 673 | ok |
| yolo26x-obb.dxnn | 2 | 3 | 48.5 ±0.0 | 24.3 | 21 | 95.5 | 100.0 | 66~68 | 1000 | 703 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-obb.dxnn | 7 | 34.1 | 7 | 34.2 |
| yolo26s-obb.dxnn | 4 | 37.0 | 4 | 37.0 |
| yolo26m-obb.dxnn | 3 | 37.5 | 3 | 37.5 |
| yolo26l-obb.dxnn | 2 | 41.9 | 2 | 41.9 |
| yolo26x-obb.dxnn | 1 | 48.5 | 1 | 48.5 |

---
*Report generated by dx_stream benchmark tool*
