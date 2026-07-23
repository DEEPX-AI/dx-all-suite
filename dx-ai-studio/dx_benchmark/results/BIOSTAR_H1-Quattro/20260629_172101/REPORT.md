# YOLO26 Benchmark Report

**Generated:** 2026-06-30 08:51:49 (Local)

## Test Timing

| # | Type | Start | End | Duration |
|---|------|-------|-----|----------|
| 1 | run | 2026-06-29 17:21:01 | 2026-06-30 08:51:49 | 15h 30m 48s |

## Executive Summary

### Object Detection

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n.dxnn | ON | 11.91 | 928.3 | 497.5 | 17 |
| yolo26n.dxnn | OFF | 11.67 | 927.4 | 457.0 | 14 |
| yolo26s.dxnn | ON | 18.64 | 536.2 | 493.8 | 17 |
| yolo26s.dxnn | OFF | 18.42 | 536.6 | 459.4 | 14 |
| yolo26m.dxnn | ON | 25.86 | 371.8 | 373.3 | 12 |
| yolo26m.dxnn | OFF | 25.57 | 372.3 | 373.4 | 12 |
| yolo26l.dxnn | ON | 34.01 | 272.8 | 276.0 | 9 |
| yolo26l.dxnn | OFF | 33.65 | 273.1 | 275.6 | 9 |
| yolo26x.dxnn | ON | 61.36 | 156.6 | 158.3 | 5 |
| yolo26x.dxnn | OFF | 61.02 | 156.2 | 158.6 | 5 |

### Pose Estimation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-pose.dxnn | ON | 11.60 | 887.5 | 545.1 | 19 |
| yolo26n-pose.dxnn | OFF | 11.33 | 887.4 | 559.2 | 18 |
| yolo26s-pose.dxnn | ON | 18.78 | 517.5 | 515.6 | 17 |
| yolo26s-pose.dxnn | OFF | 18.47 | 516.6 | 518.2 | 17 |
| yolo26m-pose.dxnn | ON | 26.21 | 361.2 | 363.2 | 12 |
| yolo26m-pose.dxnn | OFF | 26.06 | 361.2 | 364.3 | 12 |
| yolo26l-pose.dxnn | ON | 34.38 | 265.5 | 269.6 | 9 |
| yolo26l-pose.dxnn | OFF | 34.07 | 265.7 | 269.9 | 9 |
| yolo26x-pose.dxnn | ON | 62.56 | 153.4 | 155.9 | 5 |
| yolo26x-pose.dxnn | OFF | 62.24 | 152.8 | 155.6 | 5 |

### Segmentation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-seg.dxnn | ON | 20.01 | 580.8 | 363.7 | 12 |
| yolo26n-seg.dxnn | OFF | 19.70 | 607.0 | 323.0 | 10 |
| yolo26s-seg.dxnn | ON | 28.84 | 420.0 | 362.5 | 12 |
| yolo26s-seg.dxnn | OFF | 28.29 | 419.4 | 319.2 | 10 |
| yolo26m-seg.dxnn | ON | 42.62 | 265.7 | 265.8 | 8 |
| yolo26m-seg.dxnn | OFF | 42.21 | 265.6 | 266.2 | 8 |
| yolo26l-seg.dxnn | ON | 50.77 | 209.7 | 210.9 | 7 |
| yolo26l-seg.dxnn | OFF | 50.26 | 209.5 | 212.1 | 7 |
| yolo26x-seg.dxnn | ON | 90.10 | 117.6 | 120.1 | 3 |
| yolo26x-seg.dxnn | OFF | 89.49 | 118.6 | 119.9 | 3 |

### Oriented BBox (OBB)

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-obb.dxnn | ON | 26.01 | 306.6 | 305.4 | 10 |
| yolo26n-obb.dxnn | OFF | 25.78 | 306.3 | 305.5 | 10 |
| yolo26s-obb.dxnn | ON | 43.51 | 179.5 | 178.8 | 5 |
| yolo26s-obb.dxnn | OFF | 43.12 | 179.5 | 179.0 | 5 |
| yolo26m-obb.dxnn | ON | 61.09 | 131.0 | 131.1 | 4 |
| yolo26m-obb.dxnn | OFF | 60.94 | 130.8 | 131.2 | 4 |
| yolo26l-obb.dxnn | ON | 82.03 | 95.6 | 96.0 | 3 |
| yolo26l-obb.dxnn | OFF | 81.82 | 95.6 | 95.9 | 3 |
| yolo26x-obb.dxnn | ON | 153.80 | 55.1 | 55.3 | 1 |
| yolo26x-obb.dxnn | OFF | 153.75 | 55.1 | 55.3 | 1 |

### Classification

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-cls.dxnn | ON | 1.02 | 14099.1 | 777.2 | — |
| yolo26n-cls.dxnn | OFF | 1.00 | 14100.4 | 779.7 | — |
| yolo26s-cls.dxnn | ON | 1.76 | 7680.5 | 775.7 | — |
| yolo26s-cls.dxnn | OFF | 1.68 | 7681.5 | 774.8 | — |
| yolo26m-cls.dxnn | ON | 2.29 | 5418.5 | 778.0 | — |
| yolo26m-cls.dxnn | OFF | 2.31 | 5420.2 | 773.2 | — |
| yolo26l-cls.dxnn | ON | 3.65 | 3399.9 | 761.2 | — |
| yolo26l-cls.dxnn | OFF | — | 3400.2 | 764.6 | — |
| yolo26x-cls.dxnn | ON | 6.27 | 1824.5 | 748.2 | — |
| yolo26x-cls.dxnn | OFF | 6.27 | 1825.3 | 747.4 | — |

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
| NPU RT | v3.3.2 |
| NPU Driver (RT) | v2.4.1 |
| NPU Driver (PCIe) | v2.2.0 |
| NPU Firmware | v2.5.6 |
| NPU Memory | LPDDR5x 6000 Mbps, 3.92GiB |
| NPU Board | H1, Rev 0.0 |
| NPU PCIe | Gen3 X4 [04:00:00] |

### Tools

| Tool | Available | Version |
|------|-----------|---------|
| run_model | Yes | DXRT v3.3.2 run_model |
| gst-launch-1.0 | Yes | gst-launch-1.0 version 1.20.3 |
| gst-inspect-1.0 | Yes | gst-inspect-1.0 version 1.20.3 |
| dxtop | Yes | DX-TOP 1.1.0 |
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

#### Object Detection

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n.dxnn | 928.3 ±0.6 | 266 | 91.2 | 100.0 | 48~50 | 1000 | ok |
| yolo26s.dxnn | 536.2 ±0.2 | 134 | 92.4 | 100.0 | 58~59 | 1000 | ok |
| yolo26m.dxnn | 371.8 ±0.2 | 89 | 90.6 | 100.0 | 59~62 | 1000 | ok |
| yolo26l.dxnn | 272.8 ±0.2 | 66 | 90.8 | 100.0 | 59~61 | 1000 | ok |
| yolo26x.dxnn | 156.6 ±0.6 | 38 | 88.7 | 100.0 | 59~62 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n.dxnn | 927.4 ±0.1 | 171 | 93.2 | 100.0 | 57~58 | 1000 | ok |
| yolo26s.dxnn | 536.6 ±0.2 | 91 | 92.6 | 100.0 | 58~59 | 1000 | ok |
| yolo26m.dxnn | 372.3 ±0.4 | 61 | 92.2 | 100.0 | 59~62 | 1000 | ok |
| yolo26l.dxnn | 273.1 ±0.4 | 45 | 89.6 | 100.0 | 59~61 | 1000 | ok |
| yolo26x.dxnn | 156.2 ±0.8 | 26 | 90.5 | 100.0 | 59~61 | 1000 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-pose.dxnn | 887.5 ±0.3 | 156 | 92.2 | 100.0 | 57 | 1000 | ok |
| yolo26s-pose.dxnn | 517.5 ±0.2 | 87 | 90.6 | 100.0 | 58~59 | 1000 | ok |
| yolo26m-pose.dxnn | 361.2 ±0.1 | 58 | 91.6 | 100.0 | 59~62 | 1000 | ok |
| yolo26l-pose.dxnn | 265.5 ±0.3 | 45 | 89.6 | 100.0 | 58~61 | 1000 | ok |
| yolo26x-pose.dxnn | 153.4 ±0.6 | 29 | 90.1 | 100.0 | 59~61 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-pose.dxnn | 887.4 ±0.5 | 100 | 92.8 | 100.0 | 58~59 | 1000 | ok |
| yolo26s-pose.dxnn | 516.6 ±0.1 | 56 | 92.1 | 100.0 | 57~59 | 1000 | ok |
| yolo26m-pose.dxnn | 361.2 ±0.5 | 38 | 91.3 | 100.0 | 59~61 | 1000 | ok |
| yolo26l-pose.dxnn | 265.7 ±0.1 | 29 | 91.7 | 100.0 | 59~61 | 1000 | ok |
| yolo26x-pose.dxnn | 152.8 ±0.5 | 19 | 89.7 | 100.0 | 59~61 | 1000 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-seg.dxnn | 580.8 ±2.6 | 522 | 56.8 | 87.3 | 56 | 1000 | ok |
| yolo26s-seg.dxnn | 420.0 ±0.5 | 358 | 92.3 | 100.0 | 59~61 | 1000 | ok |
| yolo26m-seg.dxnn | 265.7 ±0.3 | 214 | 91.9 | 100.0 | 60~64 | 1000 | ok |
| yolo26l-seg.dxnn | 209.7 ±0.5 | 167 | 93.3 | 100.0 | 59~62 | 1000 | ok |
| yolo26x-seg.dxnn | 117.6 ±0.1 | 91 | 89.1 | 100.0 | 59~63 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-seg.dxnn | 607.0 ±5.3 | 435 | 60.6 | 90.1 | 57~58 | 1000 | ok |
| yolo26s-seg.dxnn | 419.4 ±0.3 | 291 | 92.1 | 100.0 | 58~60 | 1000 | ok |
| yolo26m-seg.dxnn | 265.6 ±0.3 | 177 | 90.7 | 100.0 | 60~63 | 1000 | ok |
| yolo26l-seg.dxnn | 209.5 ±0.5 | 141 | 88.7 | 100.0 | 59~62 | 1000 | ok |
| yolo26x-seg.dxnn | 118.6 ±0.7 | 77 | 89.0 | 100.0 | 59~63 | 1000 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-obb.dxnn | 306.6 ±0.1 | 41 | 31.1 | 100.0 | 56 | 1000 | ok |
| yolo26s-obb.dxnn | 179.5 ±0.1 | 34 | 90.8 | 100.0 | 57~58 | 1000 | ok |
| yolo26m-obb.dxnn | 131.0 ±0.2 | 26 | 93.2 | 100.0 | 58~60 | 1000 | ok |
| yolo26l-obb.dxnn | 95.6 ±0.1 | 20 | 88.8 | 100.0 | 58~60 | 1000 | ok |
| yolo26x-obb.dxnn | 55.1 ±0.2 | 13 | 86.8 | 100.0 | 57~60 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-obb.dxnn | 306.3 ±0.1 | 37 | 92.0 | 100.0 | 57 | 1000 | ok |
| yolo26s-obb.dxnn | 179.5 ±0.1 | 23 | 92.3 | 100.0 | 57~58 | 1000 | ok |
| yolo26m-obb.dxnn | 130.8 ±0.4 | 17 | 90.0 | 100.0 | 58~60 | 1000 | ok |
| yolo26l-obb.dxnn | 95.6 ±0.2 | 13 | 91.9 | 100.0 | 58~60 | 1000 | ok |
| yolo26x-obb.dxnn | 55.1 ±0.1 | 8 | 86.6 | 100.0 | 57~59 | 1000 | ok |

#### Classification

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-cls.dxnn | 14099.1 ±10.3 | 87 | 88.7 | 97.2 | 55 | 1000 | ok |
| yolo26s-cls.dxnn | 7680.5 ±5.8 | 45 | 90.9 | 98.5 | 54~55 | 1000 | ok |
| yolo26m-cls.dxnn | 5418.5 ±1.0 | 32 | 91.3 | 99.1 | 57~59 | 1000 | ok |
| yolo26l-cls.dxnn | 3399.9 ±0.6 | 20 | 91.1 | 99.5 | 57~58 | 1000 | ok |
| yolo26x-cls.dxnn | 1824.5 ±0.2 | 11 | 90.3 | 100.0 | 58~60 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-cls.dxnn | 14100.4 ±2.3 | 87 | 88.8 | 97.2 | 54 | 1000 | ok |
| yolo26s-cls.dxnn | 7681.5 ±3.2 | 45 | 91.2 | 98.5 | 55 | 1000 | ok |
| yolo26m-cls.dxnn | 5420.2 ±2.2 | 32 | 90.8 | 99.0 | 59~60 | 1000 | ok |
| yolo26l-cls.dxnn | 3400.2 ±6.6 | 20 | 60.5 | 99.6 | 58 | 1000 | ok |
| yolo26x-cls.dxnn | 1825.3 ±0.9 | 11 | 92.2 | 100.0 | 58~60 | 1000 | ok |

### Latency (Single-Core, Sync)

#### Object Detection

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n.dxnn | 83.9 | 11.91 | 11.62 | 0.30 | 45 | ok |
| yolo26s.dxnn | 53.6 | 18.64 | 18.35 | 0.30 | 55 | ok |
| yolo26m.dxnn | 38.7 | 25.86 | 25.56 | 0.30 | 55 | ok |
| yolo26l.dxnn | 29.4 | 34.01 | 33.70 | 0.31 | 55 | ok |
| yolo26x.dxnn | 16.3 | 61.36 | 61.03 | 0.33 | 54 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n.dxnn | 85.7 | 11.67 | 11.67 | 56 | ok |
| yolo26s.dxnn | 54.3 | 18.42 | 18.42 | 55 | ok |
| yolo26m.dxnn | 39.1 | 25.57 | 25.57 | 55 | ok |
| yolo26l.dxnn | 29.7 | 33.65 | 33.65 | 55 | ok |
| yolo26x.dxnn | 16.4 | 61.02 | 61.02 | 55 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-pose.dxnn | 86.2 | 11.60 | 11.38 | 0.23 | 55 | ok |
| yolo26s-pose.dxnn | 53.3 | 18.78 | 18.51 | 0.27 | 55 | ok |
| yolo26m-pose.dxnn | 38.2 | 26.21 | 25.96 | 0.25 | 55 | ok |
| yolo26l-pose.dxnn | 29.1 | 34.38 | 34.11 | 0.27 | 55 | ok |
| yolo26x-pose.dxnn | 16.0 | 62.56 | 62.24 | 0.32 | 54 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-pose.dxnn | 88.2 | 11.33 | 11.33 | 56 | ok |
| yolo26s-pose.dxnn | 54.1 | 18.47 | 18.47 | 55 | ok |
| yolo26m-pose.dxnn | 38.4 | 26.06 | 26.06 | 55 | ok |
| yolo26l-pose.dxnn | 29.4 | 34.07 | 34.07 | 55 | ok |
| yolo26x-pose.dxnn | 16.1 | 62.24 | 62.24 | 55 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-seg.dxnn | 50.0 | 20.01 | 19.61 | 0.40 | 55 | ok |
| yolo26s-seg.dxnn | 34.7 | 28.84 | 28.46 | 0.37 | 55 | ok |
| yolo26m-seg.dxnn | 23.5 | 42.62 | 42.20 | 0.41 | 55 | ok |
| yolo26l-seg.dxnn | 19.7 | 50.77 | 50.37 | 0.39 | 55 | ok |
| yolo26x-seg.dxnn | 11.1 | 90.10 | 89.69 | 0.41 | 54 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-seg.dxnn | 50.8 | 19.70 | 19.70 | 55 | ok |
| yolo26s-seg.dxnn | 35.3 | 28.29 | 28.29 | 55 | ok |
| yolo26m-seg.dxnn | 23.7 | 42.21 | 42.21 | 55 | ok |
| yolo26l-seg.dxnn | 19.9 | 50.26 | 50.26 | 54 | ok |
| yolo26x-seg.dxnn | 11.2 | 89.49 | 89.49 | 54 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-obb.dxnn | 38.4 | 26.01 | 25.70 | 0.30 | 55 | ok |
| yolo26s-obb.dxnn | 23.0 | 43.51 | 43.21 | 0.30 | 55 | ok |
| yolo26m-obb.dxnn | 16.4 | 61.09 | 60.78 | 0.31 | 55 | ok |
| yolo26l-obb.dxnn | 12.2 | 82.03 | 81.71 | 0.32 | 54 | ok |
| yolo26x-obb.dxnn | 6.5 | 153.80 | 153.47 | 0.33 | 53 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-obb.dxnn | 38.8 | 25.78 | 25.78 | 55 | ok |
| yolo26s-obb.dxnn | 23.2 | 43.12 | 43.12 | 55 | ok |
| yolo26m-obb.dxnn | 16.4 | 60.94 | 60.94 | 54 | ok |
| yolo26l-obb.dxnn | 12.2 | 81.82 | 81.82 | 54 | ok |
| yolo26x-obb.dxnn | 6.5 | 153.75 | 153.75 | 53 | ok |

#### Classification

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-cls.dxnn | 983.5 | 1.02 | 1.02 | N/A | 55 | ok |
| yolo26s-cls.dxnn | 569.7 | 1.76 | 1.76 | N/A | 52 | ok |
| yolo26m-cls.dxnn | 436.7 | 2.29 | 2.29 | N/A | 53 | ok |
| yolo26l-cls.dxnn | 273.7 | 3.65 | 3.65 | N/A | 55 | ok |
| yolo26x-cls.dxnn | 159.5 | 6.27 | 6.27 | N/A | 55 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-cls.dxnn | 996.8 | 1.00 | 1.00 | 53 | ok |
| yolo26s-cls.dxnn | 593.8 | 1.68 | 1.68 | 53 | ok |
| yolo26m-cls.dxnn | 433.1 | 2.31 | 2.31 | 55 | ok |
| yolo26l-cls.dxnn | N/A | N/A | N/A | N/A | error |
| yolo26x-cls.dxnn | 159.5 | 6.27 | 6.27 | 55 | ok |

## E2E Pipeline (Single-Stream)

### Object Detection

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | vaapidecodebin | 3455 | 3 | 497.5 ±0.3 | 6.94 | 224 | 26.7 | 62.9 | 50 | 1000 | 313 | ok |
| yolo26s.dxnn | vaapidecodebin | 3455 | 3 | 493.8 ±0.1 | 7.00 | 224 | 59.2 | 87.5 | 59 | 1000 | 421 | ok |
| yolo26m.dxnn | vaapidecodebin | 3455 | 3 | 373.3 ±1.0 | 9.26 | 152 | 75.5 | 100.0 | 62~63 | 1000 | 494 | ok |
| yolo26l.dxnn | vaapidecodebin | 3455 | 3 | 276.0 ±0.3 | 12.52 | 104 | 81.0 | 100.0 | 61~62 | 1000 | 508 | ok |
| yolo26x.dxnn | vaapidecodebin | 3455 | 3 | 158.3 ±0.4 | 21.82 | 53 | 87.7 | 100.0 | 63~64 | 1000 | 556 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | vaapidecodebin | 3455 | 3 | 457.0 ±1.2 | 7.56 | 246 | 24.4 | 79.5 | 57 | 1000 | 431 | ok |
| yolo26s.dxnn | vaapidecodebin | 3455 | 3 | 459.4 ±0.6 | 7.52 | 242 | 52.4 | 77.3 | 58 | 1000 | 481 | ok |
| yolo26m.dxnn | vaapidecodebin | 3455 | 3 | 373.4 ±0.8 | 9.25 | 193 | 81.3 | 100.0 | 62 | 1000 | 563 | ok |
| yolo26l.dxnn | vaapidecodebin | 3455 | 3 | 275.6 ±0.2 | 12.54 | 135 | 82.6 | 100.0 | 61~62 | 1000 | 572 | ok |
| yolo26x.dxnn | vaapidecodebin | 3455 | 3 | 158.6 ±0.3 | 21.79 | 71 | 85.9 | 100.0 | 63~64 | 1000 | 607 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n.dxnn | 497.5 | 457.0 | +40.6 | +8.9% |
| yolo26s.dxnn | 493.8 | 459.4 | +34.4 | +7.5% |
| yolo26m.dxnn | 373.3 | 373.4 | -0.1 | -0.0% |
| yolo26l.dxnn | 276.0 | 275.6 | +0.4 | +0.1% |
| yolo26x.dxnn | 158.3 | 158.6 | -0.2 | -0.2% |

### Pose Estimation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | vaapidecodebin | 3455 | 3 | 545.1 ±1.0 | 6.34 | 172 | 33.6 | 69.1 | 56~57 | 1000 | 300 | ok |
| yolo26s-pose.dxnn | vaapidecodebin | 3455 | 3 | 515.6 ±0.4 | 6.70 | 169 | 75.4 | 100.0 | 59 | 1000 | 415 | ok |
| yolo26m-pose.dxnn | vaapidecodebin | 3455 | 3 | 363.2 ±0.7 | 9.51 | 104 | 76.2 | 100.0 | 62 | 1000 | 448 | ok |
| yolo26l-pose.dxnn | vaapidecodebin | 3455 | 3 | 269.6 ±0.7 | 12.82 | 74 | 81.8 | 100.0 | 61~62 | 1000 | 461 | ok |
| yolo26x-pose.dxnn | vaapidecodebin | 3455 | 3 | 155.9 ±0.1 | 22.16 | 41 | 88.3 | 100.0 | 63~64 | 1000 | 513 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | vaapidecodebin | 3455 | 3 | 559.2 ±1.9 | 6.18 | 132 | 32.5 | 70.3 | 58 | 1000 | 280 | ok |
| yolo26s-pose.dxnn | vaapidecodebin | 3455 | 3 | 518.2 ±0.7 | 6.67 | 127 | 71.8 | 100.0 | 58 | 1000 | 441 | ok |
| yolo26m-pose.dxnn | vaapidecodebin | 3455 | 3 | 364.3 ±1.2 | 9.48 | 80 | 76.4 | 100.0 | 62 | 1000 | 477 | ok |
| yolo26l-pose.dxnn | vaapidecodebin | 3455 | 3 | 269.9 ±0.6 | 12.80 | 57 | 83.2 | 100.0 | 61~62 | 1000 | 490 | ok |
| yolo26x-pose.dxnn | vaapidecodebin | 3455 | 3 | 155.6 ±0.5 | 22.21 | 31 | 87.1 | 100.0 | 62~64 | 1000 | 531 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-pose.dxnn | 545.1 | 559.2 | -14.1 | -2.5% |
| yolo26s-pose.dxnn | 515.6 | 518.2 | -2.6 | -0.5% |
| yolo26m-pose.dxnn | 363.2 | 364.3 | -1.1 | -0.3% |
| yolo26l-pose.dxnn | 269.6 | 269.9 | -0.3 | -0.1% |
| yolo26x-pose.dxnn | 155.9 | 155.6 | +0.4 | +0.3% |

### Segmentation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | vaapidecodebin | 3455 | 3 | 363.7 ±0.1 | 9.50 | 539 | 24.9 | 77.6 | 55~56 | 1000 | 589 | ok |
| yolo26s-seg.dxnn | vaapidecodebin | 3455 | 3 | 362.5 ±0.3 | 9.53 | 540 | 56.1 | 82.0 | 60 | 1000 | 682 | ok |
| yolo26m-seg.dxnn | vaapidecodebin | 3455 | 3 | 265.8 ±0.2 | 13.00 | 300 | 83.5 | 100.0 | 65 | 1000 | 775 | ok |
| yolo26l-seg.dxnn | vaapidecodebin | 3455 | 3 | 210.9 ±1.0 | 16.38 | 223 | 83.6 | 100.0 | 63~64 | 1000 | 793 | ok |
| yolo26x-seg.dxnn | vaapidecodebin | 3455 | 3 | 120.1 ±0.4 | 28.76 | 120 | 89.6 | 100.0 | 66~68 | 1000 | 841 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | vaapidecodebin | 3455 | 3 | 323.0 ±0.7 | 10.70 | 432 | 22.4 | 82.6 | 57 | 1000 | 663 | ok |
| yolo26s-seg.dxnn | vaapidecodebin | 3455 | 3 | 319.2 ±1.3 | 10.82 | 423 | 46.4 | 89.3 | 59 | 1000 | 756 | ok |
| yolo26m-seg.dxnn | vaapidecodebin | 3455 | 3 | 266.2 ±0.4 | 12.98 | 327 | 83.3 | 100.0 | 64~65 | 1000 | 869 | ok |
| yolo26l-seg.dxnn | vaapidecodebin | 3455 | 3 | 212.1 ±0.5 | 16.29 | 245 | 82.6 | 100.0 | 63~64 | 1000 | 884 | ok |
| yolo26x-seg.dxnn | vaapidecodebin | 3455 | 3 | 119.9 ±0.4 | 28.81 | 133 | 89.8 | 100.0 | 65~68 | 1000 | 937 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-seg.dxnn | 363.7 | 323.0 | +40.7 | +12.6% |
| yolo26s-seg.dxnn | 362.5 | 319.2 | +43.3 | +13.6% |
| yolo26m-seg.dxnn | 265.8 | 266.2 | -0.4 | -0.1% |
| yolo26l-seg.dxnn | 210.9 | 212.1 | -1.1 | -0.5% |
| yolo26x-seg.dxnn | 120.1 | 119.9 | +0.2 | +0.2% |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | vaapidecodebin | 2640 | 3 | 305.4 ±0.5 | 8.65 | 116 | 76.7 | 100.0 | 56 | 1000 | 468 | ok |
| yolo26s-obb.dxnn | vaapidecodebin | 2640 | 3 | 178.8 ±0.2 | 14.76 | 63 | 85.2 | 100.0 | 58 | 1000 | 481 | ok |
| yolo26m-obb.dxnn | vaapidecodebin | 2640 | 3 | 131.1 ±0.1 | 20.14 | 46 | 88.4 | 100.0 | 61~62 | 1000 | 513 | ok |
| yolo26l-obb.dxnn | vaapidecodebin | 2640 | 3 | 96.0 ±0.0 | 27.51 | 34 | 91.0 | 100.0 | 61~62 | 1000 | 532 | ok |
| yolo26x-obb.dxnn | vaapidecodebin | 2640 | 3 | 55.3 ±0.0 | 47.73 | 20 | 88.6 | 100.0 | 63~66 | 1000 | 579 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | vaapidecodebin | 2640 | 3 | 305.5 ±0.1 | 8.64 | 119 | 74.5 | 100.0 | 57 | 1000 | 488 | ok |
| yolo26s-obb.dxnn | vaapidecodebin | 2640 | 3 | 179.0 ±0.1 | 14.75 | 65 | 82.6 | 100.0 | 58 | 1000 | 506 | ok |
| yolo26m-obb.dxnn | vaapidecodebin | 2640 | 3 | 131.2 ±0.1 | 20.13 | 48 | 85.4 | 100.0 | 61~62 | 1000 | 536 | ok |
| yolo26l-obb.dxnn | vaapidecodebin | 2640 | 3 | 95.9 ±0.0 | 27.52 | 35 | 88.9 | 100.0 | 61~62 | 1000 | 553 | ok |
| yolo26x-obb.dxnn | vaapidecodebin | 2640 | 3 | 55.3 ±0.0 | 47.75 | 21 | 89.2 | 100.0 | 62~65 | 1000 | 602 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-obb.dxnn | 305.4 | 305.5 | -0.2 | -0.1% |
| yolo26s-obb.dxnn | 178.8 | 179.0 | -0.2 | -0.1% |
| yolo26m-obb.dxnn | 131.1 | 131.2 | -0.0 | -0.0% |
| yolo26l-obb.dxnn | 96.0 | 95.9 | +0.0 | +0.0% |
| yolo26x-obb.dxnn | 55.3 | 55.3 | +0.0 | +0.0% |

### Classification

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-cls.dxnn | vaapidecodebin | 3455 | 3 | 777.2 ±9.2 | 4.45 | 42 | 3.1 | 15.5 | 53~54 | 1000 | 171 | ok |
| yolo26s-cls.dxnn | vaapidecodebin | 3455 | 3 | 775.7 ±6.4 | 4.45 | 41 | 5.8 | 28.7 | 53~54 | 1000 | 197 | ok |
| yolo26m-cls.dxnn | vaapidecodebin | 3455 | 3 | 778.0 ±1.1 | 4.44 | 42 | 8.5 | 40.6 | 57 | 1000 | 196 | ok |
| yolo26l-cls.dxnn | vaapidecodebin | 3455 | 3 | 761.2 ±3.5 | 4.54 | 44 | 13.9 | 63.3 | 56~57 | 1000 | 212 | ok |
| yolo26x-cls.dxnn | vaapidecodebin | 3455 | 3 | 748.2 ±2.9 | 4.62 | 45 | 26.0 | 59.5 | 58~59 | 1000 | 260 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-cls.dxnn | vaapidecodebin | 3455 | 3 | 779.7 ±10.0 | 4.43 | 42 | 3.2 | 15.6 | 53 | 1000 | 223 | ok |
| yolo26s-cls.dxnn | vaapidecodebin | 3455 | 3 | 774.8 ±7.0 | 4.46 | 42 | 5.9 | 28.5 | 54 | 1000 | 218 | ok |
| yolo26m-cls.dxnn | vaapidecodebin | 3455 | 3 | 773.2 ±3.2 | 4.47 | 42 | 9.0 | 40.6 | 58~59 | 1000 | 197 | ok |
| yolo26l-cls.dxnn | vaapidecodebin | 3455 | 3 | 764.6 ±1.9 | 4.52 | 43 | 14.5 | 63.8 | 56~57 | 1000 | 208 | ok |
| yolo26x-cls.dxnn | vaapidecodebin | 3455 | 3 | 747.4 ±2.0 | 4.62 | 45 | 24.2 | 59.7 | 58~59 | 1000 | 266 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-cls.dxnn | 777.2 | 779.7 | -2.5 | -0.3% |
| yolo26s-cls.dxnn | 775.7 | 774.8 | +0.9 | +0.1% |
| yolo26m-cls.dxnn | 778.0 | 773.2 | +4.8 | +0.6% |
| yolo26l-cls.dxnn | 761.2 | 764.6 | -3.4 | -0.4% |
| yolo26x-cls.dxnn | 748.2 | 747.4 | +0.8 | +0.1% |

## E2E Pipeline (Multi-Stream)

### Object Detection

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | 16 | 3 | 538.6 ±0.7 | 33.7 | 310 | 39.4 | 77.2 | 52~54 | 1000 | 687 | ok |
| yolo26n.dxnn | 17 | 3 | 538.4 ±1.1 | 31.7 | 310 | 39.4 | 77.4 | 56~57 | 1000 | 684 | ok |
| yolo26n.dxnn | 18 | 3 | 537.0 ±0.9 | 29.8 | 309 | 39.4 | 78.8 | 57 | 1000 | 694 | ok |
| yolo26s.dxnn | 16 | 3 | 527.3 ±0.4 | 33.0 | 309 | 92.7 | 100.0 | 63~65 | 1000 | 721 | ok |
| yolo26s.dxnn | 17 | 2/3 | 526.9 ±0.1 | 31.0 | 308 | 92.9 | 99.6 | 66~67 | 1000 | 738 | partial |
| yolo26m.dxnn | 12 | 3 | 373.2 ±0.1 | 31.1 | 175 | 95.7 | 100.0 | 70~73 | 1000 | 704 | ok |
| yolo26m.dxnn | 13 | 3 | 373.7 ±0.2 | 28.7 | 177 | 96.2 | 100.0 | 75~76 | 1000 | 721 | ok |
| yolo26l.dxnn | 9 | 3 | 275.9 ±0.1 | 30.6 | 117 | 96.1 | 100.0 | 68~72 | 1000 | 669 | ok |
| yolo26l.dxnn | 10 | 3 | 276.1 ±0.1 | 27.6 | 117 | 96.4 | 100.0 | 74 | 1000 | 668 | ok |
| yolo26x.dxnn | 5 | 3 | 157.9 ±0.3 | 31.6 | 57 | 96.1 | 100.0 | 70~74 | 1000 | 634 | ok |
| yolo26x.dxnn | 6 | 3 | 158.3 ±0.2 | 26.4 | 57 | 96.3 | 100.0 | 75~76 | 1000 | 650 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | 15 | 3 | 448.9 ±0.7 | 29.9 | 257 | 30.7 | 88.8 | 56 | 1000 | 743 | ok |
| yolo26n.dxnn | 14 | 3 | 447.5 ±0.8 | 32.0 | 258 | 30.5 | 88.6 | 56 | 1000 | 717 | ok |
| yolo26s.dxnn | 15 | 3 | 448.2 ±0.7 | 29.9 | 259 | 67.5 | 82.6 | 61~63 | 1000 | 834 | ok |
| yolo26s.dxnn | 14 | 3 | 446.6 ±1.8 | 31.9 | 260 | 66.9 | 81.4 | 63~64 | 1000 | 796 | ok |
| yolo26m.dxnn | 12 | 3 | 374.3 ±0.1 | 31.2 | 221 | 95.7 | 100.0 | 69~73 | 1000 | 793 | ok |
| yolo26m.dxnn | 13 | 3 | 374.1 ±0.1 | 28.8 | 223 | 96.4 | 100.0 | 76~77 | 1000 | 810 | ok |
| yolo26l.dxnn | 9 | 3 | 276.1 ±0.1 | 30.7 | 149 | 96.3 | 100.0 | 68~72 | 1000 | 741 | ok |
| yolo26l.dxnn | 10 | 3 | 276.2 ±0.1 | 27.6 | 150 | 96.8 | 100.0 | 73~74 | 1000 | 779 | ok |
| yolo26x.dxnn | 5 | 3 | 157.9 ±0.1 | 31.6 | 75 | 96.0 | 100.0 | 70~74 | 1000 | 708 | ok |
| yolo26x.dxnn | 6 | 3 | 158.1 ±0.1 | 26.3 | 76 | 96.4 | 100.0 | 76 | 1000 | 735 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n.dxnn | 17 | 31.7 | 14 | 32.0 |
| yolo26s.dxnn | 17+ | 31.0 | 14 | 31.9 |
| yolo26m.dxnn | 12 | 31.1 | 12 | 31.2 |
| yolo26l.dxnn | 9 | 30.6 | 9 | 30.7 |
| yolo26x.dxnn | 5 | 31.6 | 5 | 31.6 |

> **+** 표시: 마지막 측정 스트림에서도 기준 FPS를 만족함. 스위프가 FPS 임계값 미달전에 중단된 경우로, 실제 최대 처리 가능 스트림 수는 더 클 수 있음.

### Pose Estimation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | 18 | 3 | 598.8 ±1.0 | 33.3 | 238 | 49.2 | 75.5 | 57~58 | 1000 | 697 | ok |
| yolo26n-pose.dxnn | 19 | 1/3 | 597.3 | 31.4 | 238 | 49.1 | 75.2 | 59 | 1000 | 684 | partial |
| yolo26s-pose.dxnn | 17 | 3 | 519.0 ±0.3 | 30.5 | 200 | 96.0 | 100.0 | 63~66 | 1000 | 706 | ok |
| yolo26s-pose.dxnn | 18 | 3 | 519.0 ±0.4 | 28.8 | 199 | 96.1 | 100.0 | 67~68 | 1000 | 728 | ok |
| yolo26m-pose.dxnn | 12 | 3 | 363.3 ±0.8 | 30.3 | 120 | 96.2 | 100.0 | 69~73 | 1000 | 665 | ok |
| yolo26m-pose.dxnn | 13 | 3 | 364.1 ±0.2 | 28.0 | 120 | 96.5 | 100.0 | 75 | 1000 | 691 | ok |
| yolo26l-pose.dxnn | 8 | 3 | 269.9 ±0.1 | 33.7 | 83 | 95.7 | 100.0 | 67~71 | 1000 | 602 | ok |
| yolo26l-pose.dxnn | 9 | 3 | 270.4 ±0.2 | 30.0 | 83 | 96.3 | 100.0 | 72~73 | 1000 | 634 | ok |
| yolo26l-pose.dxnn | 10 | 3 | 270.1 ±0.1 | 27.0 | 83 | 96.5 | 100.0 | 74 | 1000 | 627 | ok |
| yolo26x-pose.dxnn | 5 | 3 | 155.8 ±0.1 | 31.1 | 42 | 96.9 | 100.0 | 70~73 | 1000 | 599 | ok |
| yolo26x-pose.dxnn | 6 | 3 | 155.9 ±0.1 | 26.0 | 43 | 97.4 | 100.0 | 75~76 | 1000 | 613 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | 18 | 2/3 | 609.6 ±4.7 | 33.9 | 184 | 49.9 | 76.6 | 58 | 1000 | 712 | partial |
| yolo26n-pose.dxnn | 17 | 3 | 609.7 ±0.7 | 35.9 | 185 | 49.8 | 76.4 | 58~59 | 1000 | 712 | ok |
| yolo26s-pose.dxnn | 17 | 3 | 518.2 ±0.2 | 30.5 | 153 | 95.9 | 100.0 | 63~65 | 1000 | 748 | ok |
| yolo26s-pose.dxnn | 18 | 3 | 518.1 ±0.5 | 28.8 | 155 | 95.3 | 100.0 | 65~66 | 1000 | 776 | ok |
| yolo26m-pose.dxnn | 12 | 3 | 364.6 ±0.6 | 30.4 | 94 | 96.3 | 100.0 | 69~72 | 1000 | 704 | ok |
| yolo26m-pose.dxnn | 13 | 3 | 364.6 ±0.2 | 28.1 | 94 | 96.6 | 100.0 | 74~75 | 1000 | 729 | ok |
| yolo26l-pose.dxnn | 8 | 3 | 270.5 ±0.1 | 33.8 | 65 | 95.9 | 100.0 | 67~70 | 1000 | 636 | ok |
| yolo26l-pose.dxnn | 9 | 3 | 270.3 ±0.1 | 30.0 | 65 | 96.4 | 100.0 | 72~73 | 1000 | 667 | ok |
| yolo26l-pose.dxnn | 10 | 3 | 270.3 ±0.1 | 27.0 | 66 | 96.8 | 100.0 | 73~74 | 1000 | 662 | ok |
| yolo26x-pose.dxnn | 5 | 3 | 155.8 ±0.1 | 31.2 | 34 | 96.9 | 100.0 | 70~73 | 1000 | 623 | ok |
| yolo26x-pose.dxnn | 6 | 3 | 155.9 ±0.0 | 26.0 | 34 | 97.3 | 100.0 | 74~75 | 1000 | 636 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-pose.dxnn | 19+ | 31.4 | 18+ | 33.9 |
| yolo26s-pose.dxnn | 17 | 30.5 | 17 | 30.5 |
| yolo26m-pose.dxnn | 12 | 30.3 | 12 | 30.4 |
| yolo26l-pose.dxnn | 9 | 30.0 | 9 | 30.0 |
| yolo26x-pose.dxnn | 5 | 31.1 | 5 | 31.2 |

> **+** 표시: 마지막 측정 스트림에서도 기준 FPS를 만족함. 스위프가 FPS 임계값 미달전에 중단된 경우로, 실제 최대 처리 가능 스트림 수는 더 클 수 있음.

### Segmentation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | 12 | 3 | 374.4 ±0.5 | 31.2 | 636 | 32.9 | 76.6 | 56~57 | 1000 | 997 | ok |
| yolo26n-seg.dxnn | 13 | 3 | 374.4 ±0.2 | 28.8 | 639 | 32.7 | 79.0 | 58 | 1000 | 1010 | ok |
| yolo26s-seg.dxnn | 12 | 3 | 364.5 ±0.8 | 30.4 | 605 | 75.1 | 90.2 | 64~67 | 1000 | 1007 | ok |
| yolo26s-seg.dxnn | 13 | 3 | 364.0 ±0.7 | 28.0 | 605 | 74.8 | 92.4 | 67~68 | 1000 | 1030 | ok |
| yolo26m-seg.dxnn | 8 | 3 | 266.5 ±0.2 | 33.3 | 323 | 95.9 | 100.0 | 74~78 | 1000 | 944 | ok |
| yolo26m-seg.dxnn | 9 | 3 | 264.5 ±1.4 | 29.4 | 325 | 95.1 | 100.0 | 80~81 | 800~1000 | 980 | ok |
| yolo26l-seg.dxnn | 7 | 3 | 212.2 ±0.2 | 30.3 | 235 | 96.3 | 100.0 | 72~76 | 1000 | 932 | ok |
| yolo26l-seg.dxnn | 8 | 3 | 212.3 ±0.2 | 26.5 | 235 | 96.3 | 100.0 | 78~79 | 1000 | 961 | ok |
| yolo26x-seg.dxnn | 4 | 3 | 119.6 ±1.1 | 29.9 | 124 | 95.6 | 100.0 | 76~79 | 800~1000 | 921 | ok |
| yolo26x-seg.dxnn | 3 | 3 | 118.7 ±1.2 | 39.6 | 123 | 94.7 | 100.0 | 80 | 800~1000 | 901 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | 10 | 3 | 318.8 ±0.3 | 31.9 | 438 | 26.1 | 83.0 | 56~57 | 1000 | 959 | ok |
| yolo26n-seg.dxnn | 11 | 3 | 318.4 ±0.8 | 28.9 | 440 | 26.0 | 84.0 | 56 | 1000 | 1004 | ok |
| yolo26s-seg.dxnn | 10 | 3 | 312.7 ±0.9 | 31.3 | 433 | 55.0 | 90.1 | 62~63 | 1000 | 1055 | ok |
| yolo26s-seg.dxnn | 11 | 3 | 311.7 ±1.6 | 28.3 | 432 | 54.9 | 87.8 | 64~65 | 1000 | 1077 | ok |
| yolo26m-seg.dxnn | 8 | 3 | 266.5 ±0.2 | 33.3 | 351 | 95.6 | 100.0 | 73~78 | 1000 | 1058 | ok |
| yolo26m-seg.dxnn | 9 | 3 | 265.5 ±1.6 | 29.5 | 352 | 95.8 | 100.0 | 80~82 | 800~1000 | 1092 | ok |
| yolo26l-seg.dxnn | 7 | 3 | 212.8 ±0.1 | 30.4 | 255 | 96.3 | 100.0 | 72~76 | 1000 | 1046 | ok |
| yolo26l-seg.dxnn | 8 | 3 | 212.9 ±0.3 | 26.6 | 255 | 96.7 | 100.0 | 78~79 | 1000 | 1062 | ok |
| yolo26x-seg.dxnn | 3 | 3 | 120.9 ±0.2 | 40.3 | 137 | 95.0 | 100.0 | 74~77 | 1000 | 1000 | ok |
| yolo26x-seg.dxnn | 4 | 3 | 118.1 ±2.1 | 29.5 | 135 | 95.3 | 100.0 | 80~81 | 800~1000 | 1018 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-seg.dxnn | 12 | 31.2 | 10 | 31.9 |
| yolo26s-seg.dxnn | 12 | 30.4 | 10 | 31.3 |
| yolo26m-seg.dxnn | 8 | 33.3 | 8 | 33.3 |
| yolo26l-seg.dxnn | 7 | 30.3 | 7 | 30.4 |
| yolo26x-seg.dxnn | 3 | 39.6 | 3 | 40.3 |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | 10 | 3 | 305.1 ±0.1 | 30.5 | 131 | 94.1 | 100.0 | 58~60 | 1000 | 658 | ok |
| yolo26n-obb.dxnn | 11 | 3 | 305.3 ±0.3 | 27.8 | 132 | 94.4 | 100.0 | 61~62 | 1000 | 680 | ok |
| yolo26s-obb.dxnn | 5 | 3 | 179.2 ±0.1 | 35.8 | 68 | 95.2 | 100.0 | 60~62 | 1000 | 576 | ok |
| yolo26s-obb.dxnn | 6 | 3 | 179.3 ±0.1 | 29.9 | 69 | 95.6 | 100.0 | 63~64 | 1000 | 595 | ok |
| yolo26m-obb.dxnn | 4 | 3 | 131.2 ±0.1 | 32.8 | 49 | 95.4 | 100.0 | 66~69 | 1000 | 587 | ok |
| yolo26m-obb.dxnn | 5 | 3 | 131.1 ±0.1 | 26.2 | 49 | 96.3 | 100.0 | 71~72 | 1000 | 612 | ok |
| yolo26l-obb.dxnn | 3 | 3 | 95.9 ±0.0 | 32.0 | 35 | 96.0 | 100.0 | 65~67 | 1000 | 586 | ok |
| yolo26l-obb.dxnn | 4 | 3 | 96.0 ±0.0 | 24.0 | 36 | 96.9 | 100.0 | 69~70 | 1000 | 604 | ok |
| yolo26x-obb.dxnn | 1 | 3 | 55.3 ±0.0 | 55.3 | 20 | 88.6 | 100.0 | 63~66 | 1000 | 579 | ok |
| yolo26x-obb.dxnn | 2 | 3 | 55.3 ±0.0 | 27.6 | 21 | 92.0 | 100.0 | 69~71 | 1000 | 614 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | 10 | 3 | 305.9 ±0.0 | 30.6 | 136 | 94.4 | 100.0 | 59~61 | 1000 | 686 | ok |
| yolo26n-obb.dxnn | 11 | 3 | 305.9 ±0.0 | 27.8 | 136 | 94.8 | 100.0 | 62 | 1000 | 706 | ok |
| yolo26s-obb.dxnn | 5 | 3 | 179.2 ±0.1 | 35.8 | 71 | 95.8 | 100.0 | 60~62 | 1000 | 607 | ok |
| yolo26s-obb.dxnn | 6 | 3 | 179.3 ±0.0 | 29.9 | 72 | 95.7 | 100.0 | 63 | 1000 | 627 | ok |
| yolo26m-obb.dxnn | 4 | 3 | 131.2 ±0.1 | 32.8 | 51 | 95.8 | 100.0 | 66~68 | 1000 | 612 | ok |
| yolo26m-obb.dxnn | 5 | 3 | 131.2 ±0.0 | 26.2 | 51 | 96.6 | 100.0 | 70~72 | 1000 | 638 | ok |
| yolo26l-obb.dxnn | 3 | 3 | 96.0 ±0.0 | 32.0 | 37 | 95.6 | 100.0 | 65~68 | 1000 | 609 | ok |
| yolo26l-obb.dxnn | 4 | 3 | 95.9 ±0.0 | 24.0 | 37 | 97.3 | 100.0 | 69~70 | 1000 | 628 | ok |
| yolo26x-obb.dxnn | 1 | 3 | 55.3 ±0.0 | 55.3 | 21 | 89.2 | 100.0 | 62~65 | 1000 | 602 | ok |
| yolo26x-obb.dxnn | 2 | 3 | 55.3 ±0.0 | 27.6 | 22 | 91.7 | 100.0 | 68~70 | 1000 | 634 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-obb.dxnn | 10 | 30.5 | 10 | 30.6 |
| yolo26s-obb.dxnn | 5 | 35.8 | 5 | 35.8 |
| yolo26m-obb.dxnn | 4 | 32.8 | 4 | 32.8 |
| yolo26l-obb.dxnn | 3 | 32.0 | 3 | 32.0 |
| yolo26x-obb.dxnn | 1 | 55.3 | 1 | 55.3 |

---
*Report generated by dx_stream benchmark tool*
