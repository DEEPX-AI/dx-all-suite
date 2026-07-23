# YOLO26 Benchmark Report

**Generated:** 2026-06-30 14:06:16 (Local)

## Test Timing

| # | Type | Start | End | Duration |
|---|------|-------|-----|----------|
| 1 | run | 2026-06-29 17:23:08 | 2026-06-30 14:06:16 | 20h 43m 8s |

## Executive Summary

### Object Detection

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n.dxnn | ON | 24.15 | 198.7 | 161.2 | 5 |
| yolo26n.dxnn | OFF | 22.59 | 218.6 | 190.0 | 6 |
| yolo26s.dxnn | ON | 31.61 | 132.0 | 124.8 | 4 |
| yolo26s.dxnn | OFF | 29.42 | 131.3 | 130.9 | 4 |
| yolo26m.dxnn | ON | 39.50 | 91.5 | 90.7 | 2 |
| yolo26m.dxnn | OFF | 37.79 | 90.8 | 90.4 | 2 |
| yolo26l.dxnn | ON | 47.43 | 66.5 | 66.5 | 2 |
| yolo26l.dxnn | OFF | 45.98 | 66.6 | 66.6 | 2 |
| yolo26x.dxnn | ON | 74.47 | 38.3 | 36.6 | 1 |
| yolo26x.dxnn | OFF | 73.58 | 38.2 | 36.9 | 1 |

### Pose Estimation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-pose.dxnn | ON | 21.46 | 217.5 | 180.2 | 6 |
| yolo26n-pose.dxnn | OFF | 20.27 | 216.9 | 206.7 | 6 |
| yolo26s-pose.dxnn | ON | 28.97 | 126.3 | 125.1 | 4 |
| yolo26s-pose.dxnn | OFF | 28.36 | 126.3 | 125.7 | 4 |
| yolo26m-pose.dxnn | ON | 36.98 | 87.6 | 87.9 | 2 |
| yolo26m-pose.dxnn | OFF | 35.83 | 87.9 | 87.8 | 2 |
| yolo26l-pose.dxnn | ON | 45.17 | 64.9 | 65.1 | 1 |
| yolo26l-pose.dxnn | OFF | 44.00 | 65.0 | 65.3 | 2 |
| yolo26x-pose.dxnn | ON | 72.74 | 37.4 | 36.5 | 1 |
| yolo26x-pose.dxnn | OFF | 71.55 | 37.5 | 36.5 | 1 |

### Segmentation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-seg.dxnn | ON | 38.06 | 123.1 | 97.1 | 3 |
| yolo26n-seg.dxnn | OFF | 35.33 | 133.5 | 109.0 | 3 |
| yolo26s-seg.dxnn | ON | 47.86 | 98.2 | 82.0 | 2 |
| yolo26s-seg.dxnn | OFF | 45.83 | 99.4 | 91.9 | 3 |
| yolo26m-seg.dxnn | ON | 53.64 | 66.1 | 61.1 | 1 |
| yolo26m-seg.dxnn | OFF | 59.80 | 65.0 | 62.6 | 1 |
| yolo26l-seg.dxnn | ON | 69.80 | 51.7 | 49.6 | 1 |
| yolo26l-seg.dxnn | OFF | 67.72 | 51.5 | 49.6 | 1 |
| yolo26x-seg.dxnn | ON | 108.45 | 28.9 | 22.6 | — |
| yolo26x-seg.dxnn | OFF | 106.22 | 29.1 | 22.6 | — |

### Oriented BBox (OBB)

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-obb.dxnn | ON | 37.71 | 74.4 | 74.2 | 2 |
| yolo26n-obb.dxnn | OFF | 35.47 | 74.4 | 74.4 | 2 |
| yolo26s-obb.dxnn | ON | 54.83 | 43.7 | 43.6 | 1 |
| yolo26s-obb.dxnn | OFF | 53.52 | 43.8 | 43.7 | 1 |
| yolo26m-obb.dxnn | ON | 72.67 | 31.9 | 31.8 | 1 |
| yolo26m-obb.dxnn | OFF | 71.27 | 31.8 | 31.8 | 1 |
| yolo26l-obb.dxnn | ON | 93.66 | 23.4 | 22.9 | — |
| yolo26l-obb.dxnn | OFF | 92.35 | 23.3 | 22.9 | — |
| yolo26x-obb.dxnn | ON | 165.67 | 13.5 | 12.1 | — |
| yolo26x-obb.dxnn | OFF | 164.52 | 13.5 | 12.1 | — |

### Classification

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-cls.dxnn | ON | 1.33 | 3504.1 | 281.0 | — |
| yolo26n-cls.dxnn | OFF | 1.31 | 3504.1 | 280.7 | — |
| yolo26s-cls.dxnn | ON | 2.01 | 1894.6 | 291.2 | — |
| yolo26s-cls.dxnn | OFF | 2.01 | 1892.8 | 292.8 | — |
| yolo26m-cls.dxnn | ON | 2.64 | 1337.8 | 292.3 | — |
| yolo26m-cls.dxnn | OFF | 2.64 | 1337.0 | 292.3 | — |
| yolo26l-cls.dxnn | ON | 4.06 | 842.7 | 293.2 | — |
| yolo26l-cls.dxnn | OFF | 4.07 | 841.8 | 293.1 | — |
| yolo26x-cls.dxnn | ON | 7.05 | 450.7 | 290.1 | — |
| yolo26x-cls.dxnn | OFF | 6.85 | 450.9 | 291.3 | — |

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
| yolo26n.dxnn | 198.7 ±0.7 | 244 | 71.2 | 89.0 | 53~56 | 1000 | ok |
| yolo26s.dxnn | 132.0 ±0.1 | 152 | 92.8 | 100.0 | 60~63 | 1000 | ok |
| yolo26m.dxnn | 91.5 ±0.3 | 131 | 91.9 | 100.0 | 63~67 | 1000 | ok |
| yolo26l.dxnn | 66.5 ±0.1 | 103 | 89.5 | 100.0 | 62~66 | 1000 | ok |
| yolo26x.dxnn | 38.3 ±0.2 | 62 | 89.2 | 100.0 | 64~68 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n.dxnn | 218.6 ±1.1 | 177 | 85.9 | 100.0 | 59~61 | 1000 | ok |
| yolo26s.dxnn | 131.3 ±0.3 | 129 | 92.8 | 100.0 | 60~63 | 1000 | ok |
| yolo26m.dxnn | 90.8 ±0.2 | 97 | 91.4 | 100.0 | 63~67 | 1000 | ok |
| yolo26l.dxnn | 66.6 ±0.1 | 76 | 89.1 | 100.0 | 62~66 | 1000 | ok |
| yolo26x.dxnn | 38.2 ±0.1 | 45 | 89.5 | 100.0 | 64~68 | 1000 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-pose.dxnn | 217.5 ±0.3 | 177 | 88.8 | 99.1 | 59~62 | 1000 | ok |
| yolo26s-pose.dxnn | 126.3 ±0.1 | 134 | 90.4 | 100.0 | 60~63 | 1000 | ok |
| yolo26m-pose.dxnn | 87.6 ±0.1 | 102 | 89.0 | 100.0 | 63~67 | 1000 | ok |
| yolo26l-pose.dxnn | 64.9 ±0.1 | 79 | 91.9 | 100.0 | 62~66 | 1000 | ok |
| yolo26x-pose.dxnn | 37.4 ±0.1 | 46 | 89.9 | 100.0 | 63~68 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-pose.dxnn | 216.9 ±0.4 | 157 | 90.6 | 100.0 | 59~62 | 1000 | ok |
| yolo26s-pose.dxnn | 126.3 ±0.4 | 99 | 90.0 | 100.0 | 60~63 | 1000 | ok |
| yolo26m-pose.dxnn | 87.9 ±0.1 | 73 | 92.7 | 100.0 | 63~67 | 1000 | ok |
| yolo26l-pose.dxnn | 65.0 ±0.1 | 58 | 89.8 | 100.0 | 62~66 | 1000 | ok |
| yolo26x-pose.dxnn | 37.5 ±0.1 | 33 | 88.1 | 100.0 | 63~68 | 1000 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-seg.dxnn | 123.1 ±0.2 | 292 | 50.2 | 77.7 | 58~60 | 1000 | ok |
| yolo26s-seg.dxnn | 98.2 ±0.1 | 230 | 84.1 | 97.0 | 61~64 | 1000 | ok |
| yolo26m-seg.dxnn | 66.1 ±0.1 | 158 | 90.1 | 100.0 | 65~70 | 1000 | ok |
| yolo26l-seg.dxnn | 51.7 ±0.2 | 138 | 91.4 | 100.0 | 64~68 | 1000 | ok |
| yolo26x-seg.dxnn | 28.9 ±0.1 | 78 | 89.0 | 100.0 | 65~70 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-seg.dxnn | 133.5 ±0.2 | 255 | 58.6 | 76.5 | 58~60 | 1000 | ok |
| yolo26s-seg.dxnn | 99.4 ±0.5 | 184 | 85.6 | 100.0 | 61~64 | 1000 | ok |
| yolo26m-seg.dxnn | 65.0 ±0.3 | 145 | 90.2 | 100.0 | 64~69 | 1000 | ok |
| yolo26l-seg.dxnn | 51.5 ±0.1 | 121 | 88.6 | 100.0 | 64~68 | 1000 | ok |
| yolo26x-seg.dxnn | 29.1 ±0.3 | 59 | 89.2 | 100.0 | 65~70 | 1000 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-obb.dxnn | 74.4 ±0.1 | 87 | 91.7 | 100.0 | 59~61 | 1000 | ok |
| yolo26s-obb.dxnn | 43.7 ±0.0 | 52 | 90.8 | 100.0 | 60~62 | 1000 | ok |
| yolo26m-obb.dxnn | 31.9 ±0.0 | 38 | 88.4 | 100.0 | 63~66 | 1000 | ok |
| yolo26l-obb.dxnn | 23.4 ±0.0 | 28 | 89.2 | 100.0 | 63~66 | 1000 | ok |
| yolo26x-obb.dxnn | 13.5 ±0.0 | 17 | 87.0 | 100.0 | 64~68 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-obb.dxnn | 74.4 ±0.1 | 60 | 90.5 | 100.0 | 59~61 | 1000 | ok |
| yolo26s-obb.dxnn | 43.8 ±0.0 | 37 | 89.3 | 100.0 | 60~62 | 1000 | ok |
| yolo26m-obb.dxnn | 31.8 ±0.0 | 27 | 90.7 | 100.0 | 63~66 | 1000 | ok |
| yolo26l-obb.dxnn | 23.3 ±0.1 | 21 | 91.1 | 100.0 | 63~66 | 1000 | ok |
| yolo26x-obb.dxnn | 13.5 ±0.0 | 12 | 86.4 | 100.0 | 64~68 | 1000 | ok |

#### Classification

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-cls.dxnn | 3504.1 ±1.5 | 118 | 88.3 | 96.7 | 57~59 | 1000 | ok |
| yolo26s-cls.dxnn | 1894.6 ±0.3 | 59 | 90.2 | 97.3 | 59~60 | 1000 | ok |
| yolo26m-cls.dxnn | 1337.8 ±0.7 | 44 | 89.0 | 97.7 | 61~64 | 1000 | ok |
| yolo26l-cls.dxnn | 842.7 ±0.8 | 29 | 89.8 | 98.4 | 60~62 | 1000 | ok |
| yolo26x-cls.dxnn | 450.7 ±0.5 | 17 | 89.5 | 99.6 | 61~64 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-cls.dxnn | 3504.1 ±1.5 | 119 | 88.3 | 96.3 | 58~59 | 1000 | ok |
| yolo26s-cls.dxnn | 1892.8 ±1.2 | 60 | 88.8 | 97.2 | 58~60 | 1000 | ok |
| yolo26m-cls.dxnn | 1337.0 ±0.3 | 43 | 89.4 | 97.8 | 61~64 | 1000 | ok |
| yolo26l-cls.dxnn | 841.8 ±0.1 | 29 | 91.1 | 98.6 | 60~62 | 1000 | ok |
| yolo26x-cls.dxnn | 450.9 ±0.1 | 17 | 90.4 | 99.5 | 61~64 | 1000 | ok |

### Latency (Single-Core, Sync)

#### Object Detection

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n.dxnn | 41.4 | 24.15 | 22.83 | 1.32 | 50 | ok |
| yolo26s.dxnn | 31.6 | 31.61 | 30.29 | 1.32 | 56 | ok |
| yolo26m.dxnn | 25.3 | 39.50 | 38.14 | 1.36 | 57 | ok |
| yolo26l.dxnn | 21.1 | 47.43 | 46.06 | 1.36 | 57 | ok |
| yolo26x.dxnn | 13.4 | 74.47 | 73.12 | 1.35 | 58 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n.dxnn | 44.3 | 22.59 | 22.59 | 56 | ok |
| yolo26s.dxnn | 34.0 | 29.42 | 29.42 | 56 | ok |
| yolo26m.dxnn | 26.5 | 37.79 | 37.79 | 57 | ok |
| yolo26l.dxnn | 21.7 | 45.98 | 45.98 | 57 | ok |
| yolo26x.dxnn | 13.6 | 73.58 | 73.58 | 58 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-pose.dxnn | 46.6 | 21.46 | 20.48 | 0.98 | 56 | ok |
| yolo26s-pose.dxnn | 34.5 | 28.97 | 27.98 | 0.99 | 56 | ok |
| yolo26m-pose.dxnn | 27.0 | 36.98 | 35.99 | 0.99 | 57 | ok |
| yolo26l-pose.dxnn | 22.1 | 45.17 | 44.17 | 0.99 | 57 | ok |
| yolo26x-pose.dxnn | 13.7 | 72.74 | 71.72 | 1.02 | 57 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-pose.dxnn | 49.3 | 20.27 | 20.27 | 56 | ok |
| yolo26s-pose.dxnn | 35.3 | 28.36 | 28.36 | 56 | ok |
| yolo26m-pose.dxnn | 27.9 | 35.83 | 35.83 | 57 | ok |
| yolo26l-pose.dxnn | 22.7 | 44.00 | 44.00 | 57 | ok |
| yolo26x-pose.dxnn | 14.0 | 71.55 | 71.55 | 57 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-seg.dxnn | 26.3 | 38.06 | 36.86 | 1.20 | 56 | ok |
| yolo26s-seg.dxnn | 20.9 | 47.86 | 46.66 | 1.20 | 57 | ok |
| yolo26m-seg.dxnn | 18.6 | 53.64 | 52.34 | 1.30 | 57 | ok |
| yolo26l-seg.dxnn | 14.3 | 69.80 | 68.55 | 1.24 | 57 | ok |
| yolo26x-seg.dxnn | 9.2 | 108.45 | 107.20 | 1.25 | 58 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-seg.dxnn | 28.3 | 35.33 | 35.33 | 56 | ok |
| yolo26s-seg.dxnn | 21.8 | 45.83 | 45.83 | 56 | ok |
| yolo26m-seg.dxnn | 16.7 | 59.80 | 59.80 | 57 | ok |
| yolo26l-seg.dxnn | 14.8 | 67.72 | 67.72 | 57 | ok |
| yolo26x-seg.dxnn | 9.4 | 106.22 | 106.22 | 58 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-obb.dxnn | 26.5 | 37.71 | 36.60 | 1.11 | 56 | ok |
| yolo26s-obb.dxnn | 18.2 | 54.83 | 53.73 | 1.10 | 57 | ok |
| yolo26m-obb.dxnn | 13.8 | 72.67 | 71.57 | 1.10 | 57 | ok |
| yolo26l-obb.dxnn | 10.7 | 93.66 | 92.56 | 1.10 | 57 | ok |
| yolo26x-obb.dxnn | 6.0 | 165.67 | 164.56 | 1.10 | 59 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-obb.dxnn | 28.2 | 35.47 | 35.47 | 56 | ok |
| yolo26s-obb.dxnn | 18.7 | 53.52 | 53.52 | 57 | ok |
| yolo26m-obb.dxnn | 14.0 | 71.27 | 71.27 | 57 | ok |
| yolo26l-obb.dxnn | 10.8 | 92.35 | 92.35 | 58 | ok |
| yolo26x-obb.dxnn | 6.1 | 164.52 | 164.52 | 59 | ok |

#### Classification

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-cls.dxnn | 753.0 | 1.33 | 1.33 | N/A | 56 | ok |
| yolo26s-cls.dxnn | 498.2 | 2.01 | 2.01 | N/A | 56 | ok |
| yolo26m-cls.dxnn | 378.6 | 2.64 | 2.64 | N/A | 56 | ok |
| yolo26l-cls.dxnn | 246.5 | 4.06 | 4.06 | N/A | 56 | ok |
| yolo26x-cls.dxnn | 141.8 | 7.05 | 7.05 | N/A | 56 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-cls.dxnn | 763.9 | 1.31 | 1.31 | 56 | ok |
| yolo26s-cls.dxnn | 498.1 | 2.01 | 2.01 | 56 | ok |
| yolo26m-cls.dxnn | 379.0 | 2.64 | 2.64 | 56 | ok |
| yolo26l-cls.dxnn | 245.4 | 4.07 | 4.07 | 56 | ok |
| yolo26x-cls.dxnn | 146.0 | 6.85 | 6.85 | 56 | ok |

## E2E Pipeline (Single-Stream)

### Object Detection

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | vah264dec | 3455 | 3 | 161.2 ±0.2 | 21.44 | 271 | 54.8 | 75.4 | 56~58 | 1000 | 236 | ok |
| yolo26s.dxnn | vah264dec | 3455 | 3 | 124.8 ±0.1 | 27.68 | 229 | 83.1 | 96.7 | 64~66 | 1000 | 247 | ok |
| yolo26m.dxnn | vah264dec | 3455 | 3 | 90.7 ±0.3 | 38.11 | 147 | 89.8 | 100.0 | 71~75 | 1000 | 269 | ok |
| yolo26l.dxnn | vah264dec | 3455 | 3 | 66.5 ±0.1 | 51.99 | 122 | 94.0 | 100.0 | 71~75 | 1000 | 278 | ok |
| yolo26x.dxnn | vah264dec | 3455 | 3 | 36.6 ±2.1 | 94.51 | 74 | 95.0 | 100.0 | 78~83 | 800~1000 | 346 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | vah264dec | 3455 | 3 | 190.0 ±0.4 | 18.19 | 301 | 59.7 | 85.0 | 61~62 | 1000 | 232 | ok |
| yolo26s.dxnn | vah264dec | 3455 | 3 | 130.9 ±0.3 | 26.40 | 237 | 89.1 | 100.0 | 64~66 | 1000 | 253 | ok |
| yolo26m.dxnn | vah264dec | 3455 | 3 | 90.4 ±0.1 | 38.21 | 159 | 92.8 | 100.0 | 71~74 | 1000 | 274 | ok |
| yolo26l.dxnn | vah264dec | 3455 | 3 | 66.6 ±0.1 | 51.85 | 135 | 93.0 | 100.0 | 71~76 | 1000 | 283 | ok |
| yolo26x.dxnn | vah264dec | 3455 | 3 | 36.9 ±2.0 | 93.74 | 82 | 95.8 | 100.0 | 78~83 | 800~1000 | 346 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n.dxnn | 161.2 | 190.0 | -28.8 | -15.2% |
| yolo26s.dxnn | 124.8 | 130.9 | -6.0 | -4.6% |
| yolo26m.dxnn | 90.7 | 90.4 | +0.2 | +0.3% |
| yolo26l.dxnn | 66.5 | 66.6 | -0.2 | -0.3% |
| yolo26x.dxnn | 36.6 | 36.9 | -0.3 | -0.8% |

### Pose Estimation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | vah264dec | 3455 | 3 | 180.2 ±0.5 | 19.18 | 247 | 61.2 | 84.2 | 62~63 | 1000 | 220 | ok |
| yolo26s-pose.dxnn | vah264dec | 3455 | 3 | 125.1 ±0.2 | 27.62 | 160 | 87.4 | 100.0 | 65~67 | 1000 | 238 | ok |
| yolo26m-pose.dxnn | vah264dec | 3455 | 3 | 87.9 ±0.3 | 39.32 | 125 | 92.8 | 100.0 | 71~75 | 1000 | 260 | ok |
| yolo26l-pose.dxnn | vah264dec | 3455 | 3 | 65.1 ±0.0 | 53.08 | 104 | 94.3 | 100.0 | 71~76 | 1000 | 269 | ok |
| yolo26x-pose.dxnn | vah264dec | 3455 | 3 | 36.5 ±1.6 | 94.64 | 61 | 95.5 | 100.0 | 78~83 | 600~1000 | 357 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | vah264dec | 3455 | 3 | 206.7 ±0.5 | 16.72 | 200 | 76.3 | 94.4 | 62~63 | 1000 | 202 | ok |
| yolo26s-pose.dxnn | vah264dec | 3455 | 3 | 125.7 ±0.1 | 27.48 | 130 | 89.0 | 100.0 | 65~66 | 1000 | 226 | ok |
| yolo26m-pose.dxnn | vah264dec | 3455 | 3 | 87.8 ±0.3 | 39.35 | 105 | 92.1 | 100.0 | 71~75 | 1000 | 246 | ok |
| yolo26l-pose.dxnn | vah264dec | 3455 | 3 | 65.3 ±0.3 | 52.90 | 88 | 94.0 | 100.0 | 71~75 | 1000 | 255 | ok |
| yolo26x-pose.dxnn | vah264dec | 3455 | 3 | 36.5 ±2.0 | 94.70 | 49 | 95.4 | 100.0 | 78~83 | 600~1000 | 357 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-pose.dxnn | 180.2 | 206.7 | -26.5 | -12.8% |
| yolo26s-pose.dxnn | 125.1 | 125.7 | -0.7 | -0.5% |
| yolo26m-pose.dxnn | 87.9 | 87.8 | +0.1 | +0.1% |
| yolo26l-pose.dxnn | 65.1 | 65.3 | -0.2 | -0.3% |
| yolo26x-pose.dxnn | 36.5 | 36.5 | +0.0 | +0.1% |

### Segmentation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | vah264dec | 3455 | 3 | 97.1 ±0.2 | 35.57 | 303 | 40.4 | 64.2 | 61~62 | 1000 | 339 | ok |
| yolo26s-seg.dxnn | vah264dec | 3455 | 3 | 82.0 ±0.9 | 42.16 | 264 | 67.5 | 85.5 | 66~69 | 1000 | 356 | ok |
| yolo26m-seg.dxnn | vah264dec | 3455 | 3 | 61.1 ±3.5 | 56.50 | 181 | 91.9 | 100.0 | 78~83 | 800~1000 | 370 | ok |
| yolo26l-seg.dxnn | vah264dec | 3455 | 3 | 49.6 ±2.5 | 69.65 | 140 | 93.7 | 100.0 | 77~82 | 800~1000 | 380 | ok |
| yolo26x-seg.dxnn | vah264dec | 3455 | 3 | 22.6 ±2.1 | 153.01 | 71 | 94.7 | 100.0 | 83~85 | 400~1000 | 450 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | vah264dec | 3455 | 3 | 109.0 ±0.9 | 31.71 | 332 | 47.4 | 69.4 | 61~63 | 1000 | 361 | ok |
| yolo26s-seg.dxnn | vah264dec | 3455 | 3 | 91.9 ±0.2 | 37.61 | 271 | 78.7 | 95.2 | 67~70 | 1000 | 367 | ok |
| yolo26m-seg.dxnn | vah264dec | 3455 | 3 | 62.6 ±3.3 | 55.20 | 177 | 92.6 | 100.0 | 77~82 | 800~1000 | 383 | ok |
| yolo26l-seg.dxnn | vah264dec | 3455 | 3 | 49.6 ±2.6 | 69.59 | 136 | 94.8 | 100.0 | 77~83 | 800~1000 | 396 | ok |
| yolo26x-seg.dxnn | vah264dec | 3455 | 3 | 22.6 ±2.6 | 152.93 | 70 | 94.5 | 100.0 | 83~84 | 400~1000 | 468 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-seg.dxnn | 97.1 | 109.0 | -11.8 | -10.8% |
| yolo26s-seg.dxnn | 82.0 | 91.9 | -9.9 | -10.8% |
| yolo26m-seg.dxnn | 61.1 | 62.6 | -1.4 | -2.3% |
| yolo26l-seg.dxnn | 49.6 | 49.6 | -0.0 | -0.1% |
| yolo26x-seg.dxnn | 22.6 | 22.6 | -0.0 | -0.0% |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | vah264dec | 2640 | 3 | 74.2 ±0.1 | 35.57 | 115 | 90.1 | 100.0 | 62~64 | 1000 | 257 | ok |
| yolo26s-obb.dxnn | vah264dec | 2640 | 3 | 43.6 ±0.0 | 60.53 | 79 | 93.6 | 100.0 | 66~69 | 1000 | 270 | ok |
| yolo26m-obb.dxnn | vah264dec | 2640 | 3 | 31.8 ±0.3 | 83.07 | 60 | 94.7 | 100.0 | 74~79 | 1000 | 293 | ok |
| yolo26l-obb.dxnn | vah264dec | 2640 | 3 | 22.9 ±0.9 | 115.42 | 44 | 95.6 | 100.0 | 75~80 | 1000 | 303 | ok |
| yolo26x-obb.dxnn | vah264dec | 2640 | 3 | 12.1 ±0.6 | 217.69 | 24 | 94.4 | 100.0 | 82~84 | 600~1000 | 366 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | vah264dec | 2640 | 3 | 74.4 ±0.1 | 35.50 | 116 | 91.1 | 100.0 | 63~64 | 1000 | 240 | ok |
| yolo26s-obb.dxnn | vah264dec | 2640 | 3 | 43.7 ±0.0 | 60.42 | 81 | 94.1 | 100.0 | 66~69 | 1000 | 256 | ok |
| yolo26m-obb.dxnn | vah264dec | 2640 | 3 | 31.8 ±0.3 | 82.98 | 61 | 94.6 | 100.0 | 74~79 | 1000 | 289 | ok |
| yolo26l-obb.dxnn | vah264dec | 2640 | 3 | 22.9 ±0.9 | 115.34 | 44 | 95.3 | 100.0 | 75~80 | 1000 | 288 | ok |
| yolo26x-obb.dxnn | vah264dec | 2640 | 3 | 12.1 ±0.6 | 217.60 | 23 | 94.9 | 100.0 | 82~84 | 600~1000 | 366 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-obb.dxnn | 74.2 | 74.4 | -0.2 | -0.2% |
| yolo26s-obb.dxnn | 43.6 | 43.7 | -0.1 | -0.2% |
| yolo26m-obb.dxnn | 31.8 | 31.8 | -0.0 | -0.1% |
| yolo26l-obb.dxnn | 22.9 | 22.9 | -0.0 | -0.1% |
| yolo26x-obb.dxnn | 12.1 | 12.1 | +0.0 | +0.0% |

### Classification

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-cls.dxnn | vah264dec | 3455 | 3 | 281.0 ±0.8 | 12.29 | 87 | 5.7 | 22.3 | 57 | 1000 | 113 | ok |
| yolo26s-cls.dxnn | vah264dec | 3455 | 3 | 291.2 ±0.5 | 11.86 | 84 | 11.6 | 42.4 | 58~59 | 1000 | 143 | ok |
| yolo26m-cls.dxnn | vah264dec | 3455 | 3 | 292.3 ±0.8 | 11.82 | 84 | 16.2 | 55.5 | 62 | 1000 | 134 | ok |
| yolo26l-cls.dxnn | vah264dec | 3455 | 3 | 293.2 ±0.5 | 11.78 | 83 | 26.5 | 75.2 | 61 | 1000 | 158 | ok |
| yolo26x-cls.dxnn | vah264dec | 3455 | 3 | 290.1 ±1.3 | 11.91 | 84 | 48.3 | 80.8 | 64 | 1000 | 212 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-cls.dxnn | vah264dec | 3455 | 3 | 280.7 ±0.4 | 12.31 | 87 | 5.7 | 22.4 | 57 | 1000 | 132 | ok |
| yolo26s-cls.dxnn | vah264dec | 3455 | 3 | 292.8 ±0.9 | 11.80 | 83 | 11.7 | 42.6 | 58 | 1000 | 121 | ok |
| yolo26m-cls.dxnn | vah264dec | 3455 | 3 | 292.3 ±0.4 | 11.82 | 83 | 16.0 | 55.4 | 61~62 | 1000 | 153 | ok |
| yolo26l-cls.dxnn | vah264dec | 3455 | 3 | 293.1 ±0.9 | 11.79 | 83 | 25.7 | 76.9 | 61 | 1000 | 139 | ok |
| yolo26x-cls.dxnn | vah264dec | 3455 | 3 | 291.3 ±0.9 | 11.86 | 84 | 49.1 | 80.9 | 64 | 1000 | 212 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-cls.dxnn | 281.0 | 280.7 | +0.3 | +0.1% |
| yolo26s-cls.dxnn | 291.2 | 292.8 | -1.6 | -0.5% |
| yolo26m-cls.dxnn | 292.3 | 292.3 | -0.1 | -0.0% |
| yolo26l-cls.dxnn | 293.2 | 293.1 | +0.1 | +0.0% |
| yolo26x-cls.dxnn | 290.1 | 291.3 | -1.2 | -0.4% |

## E2E Pipeline (Multi-Stream)

### Object Detection

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | 5 | 3 | 167.1 ±0.4 | 33.4 | 286 | 60.8 | 80.5 | 63~67 | 1000 | 423 | ok |
| yolo26n.dxnn | 6 | 3 | 167.3 ±0.4 | 27.9 | 287 | 61.2 | 77.4 | 69~71 | 1000 | 462 | ok |
| yolo26s.dxnn | 4 | 3 | 127.3 ±0.3 | 31.8 | 234 | 91.0 | 99.3 | 72~76 | 1000 | 400 | ok |
| yolo26s.dxnn | 5 | 3 | 127.2 ±0.2 | 25.4 | 233 | 91.6 | 99.1 | 70~76 | 1000 | 429 | ok |
| yolo26m.dxnn | 3 | 3 | 80.2 ±4.1 | 26.7 | 147 | 95.7 | 100.0 | 82~84 | 600~1000 | 378 | ok |
| yolo26m.dxnn | 2 | 3 | 73.9 ±0.2 | 36.9 | 142 | 94.1 | 100.0 | 84~85 | 600~1000 | 338 | ok |
| yolo26l.dxnn | 2 | 3 | 61.1 ±1.1 | 30.5 | 126 | 95.8 | 100.0 | 81~84 | 800~1000 | 349 | ok |
| yolo26l.dxnn | 3 | 3 | 56.7 ±0.9 | 18.9 | 120 | 95.6 | 100.0 | 84~85 | 600~1000 | 388 | ok |
| yolo26x.dxnn | 1 | 3 | 36.6 ±2.1 | 36.6 | 74 | 95.0 | 100.0 | 78~83 | 800~1000 | 346 | ok |
| yolo26x.dxnn | 2 | 3 | 29.9 ±0.4 | 14.9 | 66 | 95.4 | 100.0 | 84 | 400~1000 | 410 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | 6 | 3 | 188.0 ±0.1 | 31.3 | 323 | 71.7 | 87.1 | 67~70 | 1000 | 488 | ok |
| yolo26n.dxnn | 7 | 3 | 186.8 ±0.3 | 26.7 | 323 | 71.7 | 85.3 | 72~74 | 1000 | 522 | ok |
| yolo26s.dxnn | 4 | 3 | 131.3 ±0.1 | 32.8 | 239 | 95.7 | 100.0 | 72~77 | 1000 | 409 | ok |
| yolo26s.dxnn | 5 | 3 | 122.3 ±1.4 | 24.5 | 223 | 96.9 | 100.0 | 79~81 | 1000 | 449 | ok |
| yolo26m.dxnn | 3 | 3 | 79.7 ±4.4 | 26.6 | 160 | 95.9 | 100.0 | 82~84 | 600~1000 | 394 | ok |
| yolo26m.dxnn | 2 | 3 | 73.8 ±0.3 | 36.9 | 153 | 94.4 | 100.0 | 84~85 | 600~1000 | 349 | ok |
| yolo26l.dxnn | 2 | 3 | 61.2 ±1.3 | 30.6 | 133 | 95.8 | 100.0 | 81~84 | 800~1000 | 358 | ok |
| yolo26l.dxnn | 3 | 3 | 56.0 ±0.6 | 18.7 | 128 | 96.0 | 100.0 | 84~85 | 600~1000 | 406 | ok |
| yolo26x.dxnn | 1 | 3 | 36.9 ±2.0 | 36.9 | 82 | 95.8 | 100.0 | 78~83 | 800~1000 | 346 | ok |
| yolo26x.dxnn | 2 | 3 | 29.8 ±0.2 | 14.9 | 71 | 95.3 | 100.0 | 84 | 400~1000 | 422 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n.dxnn | 5 | 33.4 | 6 | 31.3 |
| yolo26s.dxnn | 4 | 31.8 | 4 | 32.8 |
| yolo26m.dxnn | 2 | 36.9 | 2 | 36.9 |
| yolo26l.dxnn | 2 | 30.5 | 2 | 30.6 |
| yolo26x.dxnn | 1 | 36.6 | 1 | 36.9 |

### Pose Estimation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | 6 | 3 | 190.9 ±0.2 | 31.8 | 274 | 77.9 | 90.3 | 69~72 | 1000 | 464 | ok |
| yolo26n-pose.dxnn | 7 | 3 | 191.1 ±0.2 | 27.3 | 273 | 78.2 | 90.7 | 74~76 | 1000 | 486 | ok |
| yolo26s-pose.dxnn | 4 | 3 | 125.9 ±0.1 | 31.5 | 180 | 95.0 | 100.0 | 73~77 | 1000 | 392 | ok |
| yolo26s-pose.dxnn | 5 | 3 | 118.9 ±2.2 | 23.8 | 174 | 95.8 | 100.0 | 79~80 | 1000 | 426 | ok |
| yolo26m-pose.dxnn | 2 | 3 | 81.8 ±2.5 | 40.9 | 133 | 95.4 | 100.0 | 80~83 | 800~1000 | 333 | ok |
| yolo26m-pose.dxnn | 3 | 3 | 71.8 ±0.4 | 23.9 | 127 | 95.1 | 100.0 | 84 | 600~1000 | 374 | ok |
| yolo26l-pose.dxnn | 2 | 3 | 59.7 ±1.1 | 29.9 | 108 | 95.4 | 100.0 | 81~84 | 800~1000 | 343 | ok |
| yolo26l-pose.dxnn | 1 | 3 | 65.1 ±0.0 | 65.1 | 104 | 94.3 | 100.0 | 71~76 | 1000 | 269 | ok |
| yolo26x-pose.dxnn | 1 | 3 | 36.5 ±1.6 | 36.5 | 61 | 95.5 | 100.0 | 78~83 | 600~1000 | 357 | ok |
| yolo26x-pose.dxnn | 2 | 3 | 29.7 ±0.2 | 14.9 | 54 | 95.7 | 100.0 | 84~85 | 400~1000 | 406 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | 6 | 3 | 208.9 ±0.2 | 34.8 | 258 | 88.5 | 96.9 | 68~72 | 1000 | 456 | ok |
| yolo26n-pose.dxnn | 7 | 3 | 209.7 ±0.4 | 30.0 | 259 | 89.1 | 97.5 | 75~76 | 1000 | 483 | ok |
| yolo26s-pose.dxnn | 4 | 3 | 126.3 ±0.2 | 31.6 | 155 | 95.1 | 100.0 | 72~76 | 1000 | 388 | ok |
| yolo26s-pose.dxnn | 5 | 3 | 121.9 ±3.3 | 24.4 | 152 | 96.4 | 100.0 | 78~79 | 1000 | 416 | ok |
| yolo26m-pose.dxnn | 2 | 3 | 81.9 ±2.2 | 41.0 | 115 | 95.5 | 100.0 | 80~83 | 800~1000 | 319 | ok |
| yolo26m-pose.dxnn | 3 | 3 | 72.6 ±1.0 | 24.2 | 110 | 95.1 | 100.0 | 84 | 600~1000 | 364 | ok |
| yolo26l-pose.dxnn | 2 | 3 | 60.2 ±1.2 | 30.1 | 89 | 95.5 | 100.0 | 81~84 | 800~1000 | 328 | ok |
| yolo26l-pose.dxnn | 3 | 3 | 56.0 ±0.3 | 18.7 | 85 | 96.2 | 100.0 | 84 | 600~1000 | 372 | ok |
| yolo26x-pose.dxnn | 1 | 3 | 36.5 ±2.0 | 36.5 | 49 | 95.4 | 100.0 | 78~83 | 600~1000 | 357 | ok |
| yolo26x-pose.dxnn | 2 | 3 | 29.8 ±0.4 | 14.9 | 43 | 95.9 | 100.0 | 84 | 600~1000 | 393 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-pose.dxnn | 6 | 31.8 | 6 | 34.8 |
| yolo26s-pose.dxnn | 4 | 31.5 | 4 | 31.6 |
| yolo26m-pose.dxnn | 2 | 40.9 | 2 | 41.0 |
| yolo26l-pose.dxnn | 1 | 65.1 | 2 | 30.1 |
| yolo26x-pose.dxnn | 1 | 36.5 | 1 | 36.5 |

### Segmentation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | 3 | 3 | 97.5 ±0.1 | 32.5 | 309 | 42.0 | 65.2 | 65~68 | 1000 | 457 | ok |
| yolo26n-seg.dxnn | 4 | 3 | 97.5 ±0.4 | 24.4 | 309 | 42.6 | 65.4 | 60~69 | 1000 | 498 | ok |
| yolo26s-seg.dxnn | 2 | 3 | 81.8 ±1.8 | 40.9 | 258 | 68.7 | 86.0 | 73~76 | 1000 | 432 | ok |
| yolo26s-seg.dxnn | 3 | 3 | 81.6 ±1.3 | 27.2 | 265 | 73.3 | 88.0 | 79~80 | 1000 | 472 | ok |
| yolo26m-seg.dxnn | 2 | 3 | 42.8 ±1.1 | 21.4 | 152 | 93.4 | 100.0 | 84 | 400~800 | 453 | ok |
| yolo26m-seg.dxnn | 1 | 3 | 61.1 ±3.5 | 61.1 | 181 | 91.9 | 100.0 | 78~83 | 800~1000 | 370 | ok |
| yolo26l-seg.dxnn | 1 | 3 | 49.6 ±2.5 | 49.6 | 140 | 93.7 | 100.0 | 77~82 | 800~1000 | 380 | ok |
| yolo26l-seg.dxnn | 2 | 3 | 37.4 ±1.8 | 18.7 | 120 | 95.3 | 100.0 | 84~85 | 400~800 | 463 | ok |
| yolo26x-seg.dxnn | 1 | 3 | 22.6 ±2.1 | 22.6 | 71 | 94.7 | 100.0 | 83~85 | 400~1000 | 450 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | 3 | 3 | 109.5 ±0.2 | 36.5 | 342 | 48.5 | 70.5 | 66~68 | 1000 | 490 | ok |
| yolo26n-seg.dxnn | 4 | 3 | 109.2 ±0.1 | 27.3 | 342 | 49.0 | 72.0 | 70~71 | 1000 | 547 | ok |
| yolo26s-seg.dxnn | 3 | 3 | 91.5 ±1.9 | 30.5 | 269 | 84.5 | 99.6 | 76~80 | 1000 | 499 | ok |
| yolo26s-seg.dxnn | 4 | 3 | 88.1 ±0.2 | 22.0 | 260 | 87.4 | 98.8 | 83~84 | 800~1000 | 543 | ok |
| yolo26m-seg.dxnn | 2 | 3 | 42.8 ±1.4 | 21.4 | 145 | 93.1 | 100.0 | 84 | 400~1000 | 473 | ok |
| yolo26m-seg.dxnn | 1 | 3 | 62.6 ±3.3 | 62.6 | 177 | 92.6 | 100.0 | 77~82 | 800~1000 | 383 | ok |
| yolo26l-seg.dxnn | 1 | 3 | 49.6 ±2.6 | 49.6 | 136 | 94.8 | 100.0 | 77~83 | 800~1000 | 396 | ok |
| yolo26l-seg.dxnn | 2 | 3 | 36.6 ±1.8 | 18.3 | 120 | 94.4 | 100.0 | 84~85 | 400~1000 | 480 | ok |
| yolo26x-seg.dxnn | 1 | 3 | 22.6 ±2.6 | 22.6 | 70 | 94.5 | 100.0 | 83~84 | 400~1000 | 468 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-seg.dxnn | 3 | 32.5 | 3 | 36.5 |
| yolo26s-seg.dxnn | 2 | 40.9 | 3 | 30.5 |
| yolo26m-seg.dxnn | 1 | 61.1 | 1 | 62.6 |
| yolo26l-seg.dxnn | 1 | 49.6 | 1 | 49.6 |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | 2 | 3 | 74.2 ±0.1 | 37.1 | 141 | 93.9 | 100.0 | 67~69 | 1000 | 324 | ok |
| yolo26n-obb.dxnn | 3 | 3 | 74.2 ±0.1 | 24.7 | 141 | 95.2 | 100.0 | 71~72 | 1000 | 368 | ok |
| yolo26s-obb.dxnn | 1 | 3 | 43.6 ±0.0 | 43.6 | 79 | 93.6 | 100.0 | 66~69 | 1000 | 270 | ok |
| yolo26s-obb.dxnn | 2 | 3 | 43.7 ±0.0 | 21.8 | 89 | 95.7 | 100.0 | 72~74 | 1000 | 340 | ok |
| yolo26m-obb.dxnn | 1 | 3 | 31.8 ±0.3 | 31.8 | 60 | 94.7 | 100.0 | 74~79 | 1000 | 293 | ok |
| yolo26m-obb.dxnn | 2 | 3 | 28.3 ±0.5 | 14.2 | 60 | 95.2 | 100.0 | 83~84 | 600~1000 | 362 | ok |
| yolo26l-obb.dxnn | 1 | 3 | 22.9 ±0.9 | 22.9 | 44 | 95.6 | 100.0 | 75~80 | 1000 | 303 | ok |
| yolo26x-obb.dxnn | 1 | 3 | 12.1 ±0.6 | 12.1 | 24 | 94.4 | 100.0 | 82~84 | 600~1000 | 366 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | 2 | 3 | 74.3 ±0.1 | 37.2 | 147 | 94.6 | 100.0 | 67~69 | 1000 | 315 | ok |
| yolo26n-obb.dxnn | 3 | 3 | 74.3 ±0.1 | 24.8 | 148 | 95.9 | 100.0 | 71~72 | 1000 | 360 | ok |
| yolo26s-obb.dxnn | 1 | 3 | 43.7 ±0.0 | 43.7 | 81 | 94.1 | 100.0 | 66~69 | 1000 | 256 | ok |
| yolo26s-obb.dxnn | 2 | 3 | 43.8 ±0.0 | 21.9 | 92 | 95.8 | 100.0 | 72~75 | 1000 | 331 | ok |
| yolo26m-obb.dxnn | 1 | 3 | 31.8 ±0.3 | 31.8 | 61 | 94.6 | 100.0 | 74~79 | 1000 | 289 | ok |
| yolo26m-obb.dxnn | 2 | 3 | 28.2 ±0.4 | 14.1 | 60 | 95.3 | 100.0 | 83~84 | 600~1000 | 355 | ok |
| yolo26l-obb.dxnn | 1 | 3 | 22.9 ±0.9 | 22.9 | 44 | 95.3 | 100.0 | 75~80 | 1000 | 288 | ok |
| yolo26x-obb.dxnn | 1 | 3 | 12.1 ±0.6 | 12.1 | 23 | 94.9 | 100.0 | 82~84 | 600~1000 | 366 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-obb.dxnn | 2 | 37.1 | 2 | 37.2 |
| yolo26s-obb.dxnn | 1 | 43.6 | 1 | 43.7 |
| yolo26m-obb.dxnn | 1 | 31.8 | 1 | 31.8 |

---
*Report generated by dx_stream benchmark tool*
