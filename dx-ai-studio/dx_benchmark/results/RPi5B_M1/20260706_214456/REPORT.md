# YOLO26 Benchmark Report

**Generated:** 2026-07-07 16:42:17 (Local)

## Test Timing

| # | Type | Start | End | Duration |
|---|------|-------|-----|----------|
| 1 | run | 2026-07-06 21:44:56 | 2026-07-07 16:42:17 | 18h 57m 20s |

## Executive Summary

### Object Detection

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n.dxnn | ON | 24.53 | 103.9 | 66.5 | 2 |
| yolo26n.dxnn | OFF | 21.93 | 175.0 | 84.8 | 2 |
| yolo26s.dxnn | ON | 32.14 | 104.5 | 66.6 | 2 |
| yolo26s.dxnn | OFF | 30.34 | 129.5 | 85.1 | 2 |
| yolo26m.dxnn | ON | 40.34 | 91.5 | 66.2 | 2 |
| yolo26m.dxnn | OFF | 35.32 | 90.3 | 84.2 | 2 |
| yolo26l.dxnn | ON | 46.37 | 66.4 | 64.8 | 2 |
| yolo26l.dxnn | OFF | 45.15 | 66.3 | 66.0 | 2 |
| yolo26x.dxnn | ON | 73.92 | 38.1 | 38.5 | 1 |
| yolo26x.dxnn | OFF | 71.10 | 38.1 | 37.9 | 1 |

### Pose Estimation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-pose.dxnn | ON | 19.38 | 153.9 | 81.8 | 2 |
| yolo26n-pose.dxnn | OFF | 18.55 | 211.0 | 121.9 | 4 |
| yolo26s-pose.dxnn | ON | 27.35 | 126.6 | 81.8 | 2 |
| yolo26s-pose.dxnn | OFF | 25.56 | 125.2 | 119.9 | 3 |
| yolo26m-pose.dxnn | ON | 35.95 | 87.7 | 82.0 | 2 |
| yolo26m-pose.dxnn | OFF | 32.48 | 87.8 | 87.9 | 2 |
| yolo26l-pose.dxnn | ON | 43.01 | 64.8 | 64.7 | 2 |
| yolo26l-pose.dxnn | OFF | 41.48 | 64.9 | 65.1 | 2 |
| yolo26x-pose.dxnn | ON | 70.91 | 37.5 | 37.7 | 1 |
| yolo26x-pose.dxnn | OFF | 69.91 | 37.4 | 36.7 | 1 |

### Segmentation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-seg.dxnn | ON | 42.12 | 66.6 | 46.1 | 1 |
| yolo26n-seg.dxnn | OFF | 36.03 | 95.7 | 61.5 | 2 |
| yolo26s-seg.dxnn | ON | 50.74 | 67.2 | 45.8 | 1 |
| yolo26s-seg.dxnn | OFF | 45.08 | 95.6 | 61.0 | 2 |
| yolo26m-seg.dxnn | ON | 63.02 | 64.3 | 45.5 | 1 |
| yolo26m-seg.dxnn | OFF | 58.98 | 64.8 | 58.5 | 1 |
| yolo26l-seg.dxnn | ON | 73.42 | 52.4 | 44.9 | 1 |
| yolo26l-seg.dxnn | OFF | 66.54 | 51.2 | 51.2 | 1 |
| yolo26x-seg.dxnn | ON | 110.00 | 28.8 | 24.9 | — |
| yolo26x-seg.dxnn | OFF | 106.78 | 29.0 | 26.5 | — |

### Oriented BBox (OBB)

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-obb.dxnn | ON | 37.38 | 74.1 | 70.1 | 2 |
| yolo26n-obb.dxnn | OFF | 35.52 | 74.1 | 74.1 | 2 |
| yolo26s-obb.dxnn | ON | 55.97 | 43.5 | 43.5 | 1 |
| yolo26s-obb.dxnn | OFF | 53.03 | 43.5 | 43.5 | 1 |
| yolo26m-obb.dxnn | ON | 72.37 | 31.8 | 31.9 | 1 |
| yolo26m-obb.dxnn | OFF | 71.01 | 31.8 | 31.9 | 1 |
| yolo26l-obb.dxnn | ON | 94.52 | 23.3 | 23.3 | — |
| yolo26l-obb.dxnn | OFF | 91.96 | 23.2 | 23.3 | — |
| yolo26x-obb.dxnn | ON | 166.02 | 13.5 | 13.5 | — |
| yolo26x-obb.dxnn | OFF | 164.09 | 13.5 | 13.5 | — |

### Classification

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-cls.dxnn | ON | 1.30 | 3502.6 | 187.7 | — |
| yolo26n-cls.dxnn | OFF | 1.27 | 3502.4 | 187.1 | — |
| yolo26s-cls.dxnn | ON | 1.96 | 1894.9 | 187.7 | — |
| yolo26s-cls.dxnn | OFF | 1.98 | 1896.0 | 187.2 | — |
| yolo26m-cls.dxnn | ON | 2.59 | 1333.7 | 188.0 | — |
| yolo26m-cls.dxnn | OFF | 2.57 | 1336.3 | 188.0 | — |
| yolo26l-cls.dxnn | ON | 3.85 | 841.1 | 187.1 | — |
| yolo26l-cls.dxnn | OFF | 3.87 | 840.8 | 187.0 | — |
| yolo26x-cls.dxnn | ON | 6.43 | 449.5 | 186.8 | — |
| yolo26x-cls.dxnn | OFF | 6.45 | 449.2 | 186.9 | — |

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
| yolo26n.dxnn | 103.9 ±0.3 | 193 | 28.1 | 83.7 | 48~49 | 1000 | ok |
| yolo26s.dxnn | 104.5 ±0.6 | 194 | 58.5 | 88.2 | 54~56 | 1000 | ok |
| yolo26m.dxnn | 91.5 ±0.0 | 146 | 90.6 | 100.0 | 64~68 | 1000 | ok |
| yolo26l.dxnn | 66.4 ±0.1 | 94 | 91.6 | 100.0 | 64~67 | 1000 | ok |
| yolo26x.dxnn | 38.1 ±0.3 | 57 | 89.3 | 100.0 | 66~70 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n.dxnn | 175.0 ±2.1 | 121 | 56.6 | 89.7 | 53~54 | 1000 | ok |
| yolo26s.dxnn | 129.5 ±0.1 | 83 | 90.5 | 100.0 | 60~62 | 1000 | ok |
| yolo26m.dxnn | 90.3 ±0.1 | 62 | 90.6 | 100.0 | 65~68 | 1000 | ok |
| yolo26l.dxnn | 66.3 ±0.0 | 51 | 90.6 | 100.0 | 64~67 | 1000 | ok |
| yolo26x.dxnn | 38.1 ±0.0 | 31 | 89.4 | 100.0 | 66~70 | 1000 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-pose.dxnn | 153.9 ±1.4 | 201 | 50.6 | 80.1 | 57~58 | 1000 | ok |
| yolo26s-pose.dxnn | 126.6 ±0.3 | 129 | 90.7 | 100.0 | 59~61 | 1000 | ok |
| yolo26m-pose.dxnn | 87.7 ±0.2 | 82 | 89.5 | 100.0 | 65~69 | 1000 | ok |
| yolo26l-pose.dxnn | 64.8 ±0.1 | 67 | 89.6 | 100.0 | 64~67 | 1000 | ok |
| yolo26x-pose.dxnn | 37.5 ±0.3 | 38 | 89.5 | 100.0 | 66~70 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-pose.dxnn | 211.0 ±0.7 | 88 | 87.2 | 98.2 | 56~58 | 1000 | ok |
| yolo26s-pose.dxnn | 125.2 ±0.3 | 62 | 91.6 | 100.0 | 61~63 | 1000 | ok |
| yolo26m-pose.dxnn | 87.8 ±0.1 | 40 | 91.5 | 100.0 | 65~68 | 1000 | ok |
| yolo26l-pose.dxnn | 64.9 ±0.2 | 30 | 90.5 | 100.0 | 64~67 | 1000 | ok |
| yolo26x-pose.dxnn | 37.4 ±0.1 | 20 | 89.2 | 100.0 | 66~70 | 1000 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-seg.dxnn | 66.6 ±0.4 | 237 | 21.6 | 69.6 | 55~56 | 1000 | ok |
| yolo26s-seg.dxnn | 67.2 ±0.4 | 241 | 45.4 | 75.3 | 53~54 | 1000 | ok |
| yolo26m-seg.dxnn | 64.3 ±0.1 | 197 | 86.7 | 100.0 | 67~70 | 1000 | ok |
| yolo26l-seg.dxnn | 52.4 ±0.2 | 139 | 90.7 | 100.0 | 66~70 | 1000 | ok |
| yolo26x-seg.dxnn | 28.8 ±0.3 | 74 | 89.1 | 100.0 | 68~72 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-seg.dxnn | 95.7 ±0.2 | 137 | 32.7 | 58.8 | 51~52 | 1000 | ok |
| yolo26s-seg.dxnn | 95.6 ±0.1 | 127 | 79.6 | 89.8 | 59~61 | 1000 | ok |
| yolo26m-seg.dxnn | 64.8 ±0.4 | 87 | 89.5 | 100.0 | 66~70 | 1000 | ok |
| yolo26l-seg.dxnn | 51.2 ±0.4 | 74 | 88.7 | 100.0 | 66~70 | 1000 | ok |
| yolo26x-seg.dxnn | 29.0 ±0.4 | 43 | 89.1 | 100.0 | 67~72 | 1000 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-obb.dxnn | 74.1 ±0.1 | 75 | 91.3 | 100.0 | 58~59 | 1000 | ok |
| yolo26s-obb.dxnn | 43.5 ±0.0 | 48 | 92.1 | 100.0 | 59~60 | 1000 | ok |
| yolo26m-obb.dxnn | 31.8 ±0.0 | 34 | 87.7 | 100.0 | 63~65 | 1000 | ok |
| yolo26l-obb.dxnn | 23.3 ±0.1 | 24 | 87.4 | 100.0 | 63~65 | 1000 | ok |
| yolo26x-obb.dxnn | 13.5 ±0.0 | 15 | 86.4 | 100.0 | 64~67 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-obb.dxnn | 74.1 ±0.1 | 41 | 90.7 | 100.0 | 57~58 | 1000 | ok |
| yolo26s-obb.dxnn | 43.5 ±0.1 | 24 | 90.3 | 100.0 | 60~61 | 1000 | ok |
| yolo26m-obb.dxnn | 31.8 ±0.1 | 16 | 88.7 | 100.0 | 64~66 | 1000 | ok |
| yolo26l-obb.dxnn | 23.2 ±0.1 | 12 | 88.7 | 100.0 | 61~64 | 1000 | ok |
| yolo26x-obb.dxnn | 13.5 ±0.0 | 7 | 84.4 | 100.0 | 64~66 | 1000 | ok |

#### Classification

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-cls.dxnn | 3502.6 ±0.9 | 60 | 88.3 | 95.9 | 57 | 1000 | ok |
| yolo26s-cls.dxnn | 1894.9 ±2.0 | 36 | 89.3 | 97.6 | 53~54 | 1000 | ok |
| yolo26m-cls.dxnn | 1333.7 ±4.4 | 25 | 89.7 | 98.1 | 56~59 | 1000 | ok |
| yolo26l-cls.dxnn | 841.1 ±0.7 | 17 | 90.5 | 98.5 | 60~61 | 1000 | ok |
| yolo26x-cls.dxnn | 449.5 ±0.4 | 9 | 90.1 | 99.6 | 61~64 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-cls.dxnn | 3502.4 ±0.3 | 59 | 89.0 | 96.6 | 53~54 | 1000 | ok |
| yolo26s-cls.dxnn | 1896.0 ±0.7 | 36 | 90.2 | 97.3 | 48~51 | 1000 | ok |
| yolo26m-cls.dxnn | 1336.3 ±0.7 | 26 | 90.4 | 98.2 | 60~63 | 1000 | ok |
| yolo26l-cls.dxnn | 840.8 ±1.9 | 17 | 91.4 | 98.8 | 59~61 | 1000 | ok |
| yolo26x-cls.dxnn | 449.2 ±0.3 | 9 | 90.4 | 99.6 | 63~65 | 1000 | ok |

### Latency (Single-Core, Sync)

#### Object Detection

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n.dxnn | 40.8 | 24.53 | 21.84 | 2.68 | 46 | ok |
| yolo26s.dxnn | 31.1 | 32.14 | 29.63 | 2.51 | 50 | ok |
| yolo26m.dxnn | 24.8 | 40.34 | 37.81 | 2.53 | 56 | ok |
| yolo26l.dxnn | 21.6 | 46.37 | 43.87 | 2.50 | 56 | ok |
| yolo26x.dxnn | 13.5 | 73.92 | 71.26 | 2.66 | 57 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n.dxnn | 45.6 | 21.93 | 21.93 | 49 | ok |
| yolo26s.dxnn | 33.0 | 30.34 | 30.34 | 55 | ok |
| yolo26m.dxnn | 28.3 | 35.32 | 35.32 | 56 | ok |
| yolo26l.dxnn | 22.2 | 45.15 | 45.15 | 57 | ok |
| yolo26x.dxnn | 14.1 | 71.10 | 71.10 | 58 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-pose.dxnn | 51.6 | 19.38 | 17.92 | 1.45 | 55 | ok |
| yolo26s-pose.dxnn | 36.6 | 27.35 | 25.77 | 1.57 | 54 | ok |
| yolo26m-pose.dxnn | 27.8 | 35.95 | 34.36 | 1.59 | 56 | ok |
| yolo26l-pose.dxnn | 23.2 | 43.01 | 41.39 | 1.62 | 57 | ok |
| yolo26x-pose.dxnn | 14.1 | 70.91 | 69.32 | 1.58 | 57 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-pose.dxnn | 53.9 | 18.55 | 18.55 | 51 | ok |
| yolo26s-pose.dxnn | 39.1 | 25.56 | 25.56 | 56 | ok |
| yolo26m-pose.dxnn | 30.8 | 32.48 | 32.48 | 57 | ok |
| yolo26l-pose.dxnn | 24.1 | 41.48 | 41.48 | 57 | ok |
| yolo26x-pose.dxnn | 14.3 | 69.91 | 69.91 | 58 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-seg.dxnn | 23.7 | 42.12 | 39.11 | 3.01 | 55 | ok |
| yolo26s-seg.dxnn | 19.7 | 50.74 | 47.74 | 2.99 | 49 | ok |
| yolo26m-seg.dxnn | 15.9 | 63.02 | 59.85 | 3.17 | 56 | ok |
| yolo26l-seg.dxnn | 13.6 | 73.42 | 70.33 | 3.09 | 56 | ok |
| yolo26x-seg.dxnn | 9.1 | 110.00 | 106.88 | 3.12 | 57 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-seg.dxnn | 27.8 | 36.03 | 36.03 | 48 | ok |
| yolo26s-seg.dxnn | 22.2 | 45.08 | 45.08 | 53 | ok |
| yolo26m-seg.dxnn | 17.0 | 58.98 | 58.98 | 56 | ok |
| yolo26l-seg.dxnn | 15.0 | 66.54 | 66.54 | 57 | ok |
| yolo26x-seg.dxnn | 9.4 | 106.78 | 106.78 | 57 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-obb.dxnn | 26.8 | 37.38 | 35.58 | 1.79 | 55 | ok |
| yolo26s-obb.dxnn | 17.9 | 55.97 | 54.18 | 1.78 | 55 | ok |
| yolo26m-obb.dxnn | 13.8 | 72.37 | 70.62 | 1.76 | 56 | ok |
| yolo26l-obb.dxnn | 10.6 | 94.52 | 92.73 | 1.79 | 57 | ok |
| yolo26x-obb.dxnn | 6.0 | 166.02 | 164.16 | 1.86 | 57 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-obb.dxnn | 28.2 | 35.52 | 35.52 | 54 | ok |
| yolo26s-obb.dxnn | 18.9 | 53.03 | 53.03 | 56 | ok |
| yolo26m-obb.dxnn | 14.1 | 71.01 | 71.01 | 57 | ok |
| yolo26l-obb.dxnn | 10.9 | 91.96 | 91.96 | 55 | ok |
| yolo26x-obb.dxnn | 6.1 | 164.09 | 164.09 | 58 | ok |

#### Classification

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-cls.dxnn | 769.4 | 1.30 | 1.30 | N/A | 55 | ok |
| yolo26s-cls.dxnn | 509.4 | 1.96 | 1.96 | N/A | 48 | ok |
| yolo26m-cls.dxnn | 385.7 | 2.59 | 2.59 | N/A | 46 | ok |
| yolo26l-cls.dxnn | 259.8 | 3.85 | 3.85 | N/A | 54 | ok |
| yolo26x-cls.dxnn | 155.5 | 6.43 | 6.43 | N/A | 54 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-cls.dxnn | 785.5 | 1.27 | 1.27 | 50 | ok |
| yolo26s-cls.dxnn | 505.5 | 1.98 | 1.98 | 42 | ok |
| yolo26m-cls.dxnn | 389.2 | 2.57 | 2.57 | 52 | ok |
| yolo26l-cls.dxnn | 258.3 | 3.87 | 3.87 | 53 | ok |
| yolo26x-cls.dxnn | 155.2 | 6.45 | 6.45 | 55 | ok |

## E2E Pipeline (Single-Stream)

### Object Detection

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | avdec_h264 | 3455 | 3 | 66.5 ±0.1 | 51.93 | 333 | 20.3 | 44.5 | 48~49 | 1000 | 307 | ok |
| yolo26s.dxnn | avdec_h264 | 3455 | 3 | 66.6 ±0.2 | 51.88 | 326 | 38.0 | 67.2 | 55 | 1000 | 323 | ok |
| yolo26m.dxnn | avdec_h264 | 3455 | 3 | 66.2 ±0.2 | 52.21 | 306 | 58.1 | 81.2 | 66~68 | 1000 | 347 | ok |
| yolo26l.dxnn | avdec_h264 | 3455 | 3 | 64.8 ±0.3 | 53.31 | 258 | 88.4 | 99.7 | 70~73 | 1000 | 354 | ok |
| yolo26x.dxnn | avdec_h264 | 3455 | 3 | 38.5 ±0.2 | 89.77 | 112 | 95.2 | 100.0 | 70~78 | 1000 | 415 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | avdec_h264 | 3455 | 3 | 84.8 ±0.6 | 40.75 | 309 | 22.6 | 69.5 | 52~53 | 1000 | 338 | ok |
| yolo26s.dxnn | avdec_h264 | 3455 | 3 | 85.1 ±0.4 | 40.62 | 305 | 44.8 | 77.3 | 60 | 1000 | 355 | ok |
| yolo26m.dxnn | avdec_h264 | 3455 | 3 | 84.2 ±0.1 | 41.03 | 309 | 82.2 | 91.4 | 70~72 | 1000 | 375 | ok |
| yolo26l.dxnn | avdec_h264 | 3455 | 3 | 66.0 ±0.1 | 52.31 | 222 | 93.3 | 100.0 | 70~73 | 1000 | 368 | ok |
| yolo26x.dxnn | avdec_h264 | 3455 | 3 | 37.9 ±0.8 | 91.25 | 120 | 95.3 | 100.0 | 77~81 | 800~1000 | 430 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n.dxnn | 66.5 | 84.8 | -18.2 | -21.5% |
| yolo26s.dxnn | 66.6 | 85.1 | -18.5 | -21.7% |
| yolo26m.dxnn | 66.2 | 84.2 | -18.0 | -21.4% |
| yolo26l.dxnn | 64.8 | 66.0 | -1.2 | -1.9% |
| yolo26x.dxnn | 38.5 | 37.9 | +0.6 | +1.7% |

### Pose Estimation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | avdec_h264 | 3455 | 3 | 81.8 ±0.1 | 42.26 | 343 | 26.4 | 54.8 | 53~54 | 1000 | 299 | ok |
| yolo26s-pose.dxnn | avdec_h264 | 3455 | 3 | 81.8 ±0.3 | 42.22 | 334 | 51.1 | 74.2 | 59 | 1000 | 314 | ok |
| yolo26m-pose.dxnn | avdec_h264 | 3455 | 3 | 82.0 ±0.4 | 42.15 | 296 | 81.7 | 95.2 | 70~72 | 1000 | 337 | ok |
| yolo26l-pose.dxnn | avdec_h264 | 3455 | 3 | 64.7 ±0.2 | 53.39 | 171 | 92.6 | 100.0 | 71~74 | 1000 | 346 | ok |
| yolo26x-pose.dxnn | avdec_h264 | 3455 | 3 | 37.7 ±0.6 | 91.74 | 93 | 94.5 | 100.0 | 64~80 | 800~1000 | 408 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | avdec_h264 | 3455 | 3 | 121.9 ±0.9 | 28.34 | 314 | 39.2 | 68.4 | 55 | 1000 | 282 | ok |
| yolo26s-pose.dxnn | avdec_h264 | 3455 | 3 | 119.9 ±1.1 | 28.81 | 294 | 82.5 | 98.6 | 63~64 | 1000 | 305 | ok |
| yolo26m-pose.dxnn | avdec_h264 | 3455 | 3 | 87.9 ±0.3 | 39.30 | 179 | 91.8 | 100.0 | 71~73 | 1000 | 326 | ok |
| yolo26l-pose.dxnn | avdec_h264 | 3455 | 3 | 65.1 ±0.2 | 53.04 | 130 | 93.7 | 100.0 | 71~74 | 1000 | 337 | ok |
| yolo26x-pose.dxnn | avdec_h264 | 3455 | 3 | 36.7 ±1.5 | 94.15 | 75 | 93.9 | 100.0 | 78~82 | 800~1000 | 399 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-pose.dxnn | 81.8 | 121.9 | -40.1 | -32.9% |
| yolo26s-pose.dxnn | 81.8 | 119.9 | -38.1 | -31.8% |
| yolo26m-pose.dxnn | 82.0 | 87.9 | -5.9 | -6.8% |
| yolo26l-pose.dxnn | 64.7 | 65.1 | -0.4 | -0.6% |
| yolo26x-pose.dxnn | 37.7 | 36.7 | +1.0 | +2.6% |

### Segmentation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | avdec_h264 | 3455 | 3 | 46.1 ±0.0 | 74.94 | 333 | 17.8 | 40.4 | 47~52 | 1000 | 408 | ok |
| yolo26s-seg.dxnn | avdec_h264 | 3455 | 3 | 45.8 ±0.2 | 75.45 | 322 | 32.7 | 63.9 | 53~54 | 1000 | 421 | ok |
| yolo26m-seg.dxnn | avdec_h264 | 3455 | 3 | 45.5 ±0.4 | 75.92 | 293 | 58.1 | 87.5 | 70~72 | 1000 | 447 | ok |
| yolo26l-seg.dxnn | avdec_h264 | 3455 | 3 | 44.9 ±0.5 | 76.90 | 262 | 76.8 | 96.0 | 73~76 | 1000 | 456 | ok |
| yolo26x-seg.dxnn | avdec_h264 | 3455 | 3 | 24.9 ±1.6 | 139.03 | 114 | 91.3 | 100.0 | 80~81 | 600~1000 | 525 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | avdec_h264 | 3455 | 3 | 61.5 ±0.6 | 56.15 | 355 | 20.5 | 63.2 | 50~51 | 1000 | 450 | ok |
| yolo26s-seg.dxnn | avdec_h264 | 3455 | 3 | 61.0 ±0.1 | 56.67 | 353 | 42.1 | 74.0 | 58 | 1000 | 465 | ok |
| yolo26m-seg.dxnn | avdec_h264 | 3455 | 3 | 58.5 ±0.9 | 59.08 | 308 | 79.8 | 94.9 | 58~75 | 1000 | 478 | ok |
| yolo26l-seg.dxnn | avdec_h264 | 3455 | 3 | 51.2 ±0.4 | 67.49 | 245 | 91.8 | 100.0 | 74~78 | 800~1000 | 467 | ok |
| yolo26x-seg.dxnn | avdec_h264 | 3455 | 3 | 26.5 ±2.6 | 130.33 | 117 | 93.6 | 100.0 | 68~80 | 600~1000 | 544 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-seg.dxnn | 46.1 | 61.5 | -15.4 | -25.1% |
| yolo26s-seg.dxnn | 45.8 | 61.0 | -15.2 | -24.9% |
| yolo26m-seg.dxnn | 45.5 | 58.5 | -13.0 | -22.2% |
| yolo26l-seg.dxnn | 44.9 | 51.2 | -6.3 | -12.2% |
| yolo26x-seg.dxnn | 24.9 | 26.5 | -1.7 | -6.3% |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | avdec_h264 | 2640 | 3 | 70.1 ±0.0 | 37.64 | 304 | 79.6 | 96.2 | 58~59 | 1000 | 321 | ok |
| yolo26s-obb.dxnn | avdec_h264 | 2640 | 3 | 43.5 ±0.1 | 60.72 | 139 | 92.9 | 100.0 | 61~62 | 1000 | 340 | ok |
| yolo26m-obb.dxnn | avdec_h264 | 2640 | 3 | 31.9 ±0.1 | 82.84 | 100 | 94.1 | 100.0 | 69~72 | 1000 | 363 | ok |
| yolo26l-obb.dxnn | avdec_h264 | 2640 | 3 | 23.3 ±0.0 | 113.24 | 74 | 95.3 | 100.0 | 59~68 | 1000 | 373 | ok |
| yolo26x-obb.dxnn | avdec_h264 | 2640 | 3 | 13.5 ±0.0 | 195.42 | 46 | 92.9 | 100.0 | 66~77 | 1000 | 441 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | avdec_h264 | 2640 | 3 | 74.1 ±0.1 | 35.61 | 242 | 91.1 | 100.0 | 58~59 | 1000 | 325 | ok |
| yolo26s-obb.dxnn | avdec_h264 | 2640 | 3 | 43.5 ±0.0 | 60.64 | 129 | 93.5 | 100.0 | 62~64 | 1000 | 337 | ok |
| yolo26m-obb.dxnn | avdec_h264 | 2640 | 3 | 31.9 ±0.0 | 82.84 | 99 | 94.7 | 100.0 | 71~75 | 1000 | 358 | ok |
| yolo26l-obb.dxnn | avdec_h264 | 2640 | 3 | 23.3 ±0.0 | 113.13 | 74 | 95.1 | 100.0 | 70~73 | 1000 | 369 | ok |
| yolo26x-obb.dxnn | avdec_h264 | 2640 | 3 | 13.5 ±0.1 | 196.21 | 44 | 92.4 | 100.0 | 77~79 | 800~1000 | 440 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-obb.dxnn | 70.1 | 74.1 | -4.0 | -5.4% |
| yolo26s-obb.dxnn | 43.5 | 43.5 | -0.1 | -0.1% |
| yolo26m-obb.dxnn | 31.9 | 31.9 | +0.0 | +0.0% |
| yolo26l-obb.dxnn | 23.3 | 23.3 | -0.0 | -0.1% |
| yolo26x-obb.dxnn | 13.5 | 13.5 | +0.0 | +0.4% |

### Classification

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-cls.dxnn | avdec_h264 | 3455 | 3 | 187.7 ±0.1 | 18.41 | 276 | 4.3 | 13.7 | 50~52 | 1000 | 197 | ok |
| yolo26s-cls.dxnn | avdec_h264 | 3455 | 3 | 187.7 ±0.2 | 18.41 | 276 | 7.8 | 24.9 | 42~43 | 1000 | 214 | ok |
| yolo26m-cls.dxnn | avdec_h264 | 3455 | 3 | 188.0 ±0.2 | 18.38 | 277 | 11.3 | 34.0 | 52~53 | 1000 | 214 | ok |
| yolo26l-cls.dxnn | avdec_h264 | 3455 | 3 | 187.1 ±0.6 | 18.47 | 274 | 18.0 | 45.3 | 55~56 | 1000 | 234 | ok |
| yolo26x-cls.dxnn | avdec_h264 | 3455 | 3 | 186.8 ±0.3 | 18.49 | 273 | 33.1 | 61.4 | 58~59 | 1000 | 268 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-cls.dxnn | avdec_h264 | 3455 | 3 | 187.1 ±0.6 | 18.47 | 275 | 4.2 | 13.8 | 48~49 | 1000 | 197 | ok |
| yolo26s-cls.dxnn | avdec_h264 | 3455 | 3 | 187.2 ±0.4 | 18.46 | 276 | 7.8 | 24.4 | 47 | 1000 | 204 | ok |
| yolo26m-cls.dxnn | avdec_h264 | 3455 | 3 | 188.0 ±0.5 | 18.38 | 276 | 11.3 | 33.2 | 54~56 | 1000 | 230 | ok |
| yolo26l-cls.dxnn | avdec_h264 | 3455 | 3 | 187.0 ±0.7 | 18.48 | 275 | 17.9 | 44.6 | 54~55 | 1000 | 235 | ok |
| yolo26x-cls.dxnn | avdec_h264 | 3455 | 3 | 186.9 ±0.3 | 18.48 | 274 | 31.9 | 61.6 | 47~49 | 1000 | 263 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-cls.dxnn | 187.7 | 187.1 | +0.6 | +0.3% |
| yolo26s-cls.dxnn | 187.7 | 187.2 | +0.5 | +0.3% |
| yolo26m-cls.dxnn | 188.0 | 188.0 | -0.0 | -0.0% |
| yolo26l-cls.dxnn | 187.1 | 187.0 | +0.1 | +0.1% |
| yolo26x-cls.dxnn | 186.8 | 186.9 | -0.1 | -0.0% |

## E2E Pipeline (Multi-Stream)

### Object Detection

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | 2 | 3 | 66.3 ±0.1 | 33.1 | 330 | 20.5 | 46.2 | 49 | 1000 | 443 | ok |
| yolo26n.dxnn | 3 | 3 | 65.7 ±1.0 | 21.9 | 331 | 20.5 | 50.0 | 49~50 | 1000 | 545 | ok |
| yolo26s.dxnn | 2 | 3 | 66.4 ±0.2 | 33.2 | 325 | 38.3 | 69.0 | 55~56 | 1000 | 458 | ok |
| yolo26s.dxnn | 3 | 3 | 66.0 ±0.5 | 22.0 | 324 | 38.4 | 67.2 | 56~57 | 1000 | 558 | ok |
| yolo26m.dxnn | 2 | 3 | 63.8 ±0.3 | 31.9 | 315 | 57.2 | 85.3 | 69~70 | 1000 | 479 | ok |
| yolo26m.dxnn | 3 | 3 | 64.5 ±0.8 | 21.5 | 314 | 58.5 | 81.6 | 70 | 1000 | 579 | ok |
| yolo26l.dxnn | 2 | 3 | 64.0 ±0.2 | 32.0 | 268 | 88.6 | 99.7 | 75~78 | 1000 | 489 | ok |
| yolo26l.dxnn | 3 | 3 | 63.6 ±0.7 | 21.2 | 270 | 88.1 | 98.8 | 78~79 | 1000 | 589 | ok |
| yolo26x.dxnn | 1 | 3 | 38.5 ±0.2 | 38.5 | 112 | 95.2 | 100.0 | 70~78 | 1000 | 415 | ok |
| yolo26x.dxnn | 2 | 3 | 35.2 ±0.7 | 17.6 | 113 | 94.8 | 100.0 | 81~82 | 400~1000 | 548 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | 2 | 3 | 85.0 ±0.5 | 42.5 | 307 | 23.4 | 69.4 | 52 | 1000 | 470 | ok |
| yolo26n.dxnn | 3 | 3 | 84.3 ±0.1 | 28.1 | 312 | 23.5 | 72.1 | 51 | 1000 | 573 | ok |
| yolo26s.dxnn | 2 | 3 | 84.2 ±1.0 | 42.1 | 309 | 46.3 | 77.4 | 59 | 1000 | 484 | ok |
| yolo26s.dxnn | 3 | 3 | 84.9 ±0.4 | 28.3 | 305 | 46.9 | 77.9 | 59~60 | 1000 | 590 | ok |
| yolo26m.dxnn | 2 | 3 | 84.0 ±1.3 | 42.0 | 308 | 83.3 | 92.4 | 73~75 | 1000 | 505 | ok |
| yolo26m.dxnn | 3 | 3 | 84.5 ±0.9 | 28.2 | 304 | 85.2 | 95.4 | 69~75 | 1000 | 606 | ok |
| yolo26l.dxnn | 2 | 3 | 66.3 ±0.1 | 33.1 | 223 | 95.5 | 100.0 | 76~79 | 1000 | 505 | ok |
| yolo26l.dxnn | 3 | 3 | 66.0 ±0.2 | 22.0 | 225 | 96.2 | 100.0 | 80~81 | 800~1000 | 608 | ok |
| yolo26x.dxnn | 1 | 3 | 37.9 ±0.8 | 37.9 | 120 | 95.3 | 100.0 | 77~81 | 800~1000 | 430 | ok |
| yolo26x.dxnn | 2 | 3 | 35.0 ±0.6 | 17.5 | 116 | 95.7 | 100.0 | 81~82 | 600~1000 | 560 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n.dxnn | 2 | 33.1 | 2 | 42.5 |
| yolo26s.dxnn | 2 | 33.2 | 2 | 42.1 |
| yolo26m.dxnn | 2 | 31.9 | 2 | 42.0 |
| yolo26l.dxnn | 2 | 32.0 | 2 | 33.1 |
| yolo26x.dxnn | 1 | 38.5 | 1 | 37.9 |

### Pose Estimation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | 2 | 3 | 81.4 ±0.4 | 40.7 | 341 | 27.2 | 56.2 | 52 | 1000 | 435 | ok |
| yolo26n-pose.dxnn | 3 | 3 | 80.9 ±0.7 | 27.0 | 340 | 27.3 | 55.6 | 52 | 1000 | 540 | ok |
| yolo26s-pose.dxnn | 2 | 3 | 81.5 ±0.2 | 40.7 | 335 | 51.2 | 76.9 | 59~60 | 1000 | 452 | ok |
| yolo26s-pose.dxnn | 3 | 3 | 80.2 ±1.0 | 26.8 | 336 | 50.6 | 76.9 | 60 | 1000 | 555 | ok |
| yolo26m-pose.dxnn | 2 | 3 | 79.3 ±0.8 | 39.6 | 309 | 80.8 | 95.3 | 74~76 | 1000 | 474 | ok |
| yolo26m-pose.dxnn | 3 | 3 | 79.6 ±0.7 | 26.5 | 306 | 82.1 | 96.3 | 77~79 | 1000 | 576 | ok |
| yolo26l-pose.dxnn | 2 | 3 | 64.8 ±0.1 | 32.4 | 180 | 95.2 | 100.0 | 77~79 | 1000 | 482 | ok |
| yolo26l-pose.dxnn | 3 | 3 | 64.1 ±0.8 | 21.4 | 176 | 95.9 | 100.0 | 80~81 | 800~1000 | 584 | ok |
| yolo26x-pose.dxnn | 1 | 3 | 37.7 ±0.6 | 37.7 | 93 | 94.5 | 100.0 | 64~80 | 800~1000 | 408 | ok |
| yolo26x-pose.dxnn | 2 | 3 | 34.9 ±1.9 | 17.4 | 95 | 95.3 | 100.0 | 81~82 | 600~1000 | 546 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | 4 | 3 | 123.4 ±1.6 | 30.8 | 363 | 46.4 | 66.1 | 55 | 1000 | 654 | ok |
| yolo26n-pose.dxnn | 5 | 3 | 123.3 ±0.5 | 24.7 | 363 | 46.5 | 65.6 | 55 | 1000 | 735 | ok |
| yolo26s-pose.dxnn | 3 | 3 | 119.0 ±1.1 | 39.6 | 320 | 86.4 | 96.6 | 66~67 | 1000 | 546 | ok |
| yolo26s-pose.dxnn | 4 | 3 | 119.5 ±0.5 | 29.9 | 319 | 87.7 | 98.7 | 67~68 | 1000 | 652 | ok |
| yolo26m-pose.dxnn | 2 | 3 | 87.8 ±0.1 | 43.9 | 187 | 95.2 | 100.0 | 77~79 | 1000 | 464 | ok |
| yolo26m-pose.dxnn | 3 | 3 | 85.7 ±1.4 | 28.6 | 187 | 95.5 | 100.0 | 80~81 | 800~1000 | 567 | ok |
| yolo26l-pose.dxnn | 2 | 3 | 65.2 ±0.2 | 32.6 | 137 | 95.7 | 100.0 | 77~80 | 1000 | 474 | ok |
| yolo26l-pose.dxnn | 3 | 3 | 64.9 ±0.8 | 21.6 | 134 | 96.4 | 100.0 | 80~81 | 800~1000 | 578 | ok |
| yolo26x-pose.dxnn | 1 | 3 | 36.7 ±1.5 | 36.7 | 75 | 93.9 | 100.0 | 78~82 | 800~1000 | 399 | ok |
| yolo26x-pose.dxnn | 2 | 3 | 36.3 ±2.2 | 18.1 | 77 | 95.7 | 100.0 | 73~82 | 600~1000 | 533 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-pose.dxnn | 2 | 40.7 | 4 | 30.8 |
| yolo26s-pose.dxnn | 2 | 40.7 | 3 | 39.6 |
| yolo26m-pose.dxnn | 2 | 39.6 | 2 | 43.9 |
| yolo26l-pose.dxnn | 2 | 32.4 | 2 | 32.6 |
| yolo26x-pose.dxnn | 1 | 37.7 | 1 | 36.7 |

### Segmentation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | 1 | 3 | 46.1 ±0.0 | 46.1 | 333 | 17.8 | 40.4 | 47~52 | 1000 | 408 | ok |
| yolo26n-seg.dxnn | 2 | 3 | 46.1 ±0.2 | 23.1 | 330 | 17.9 | 41.9 | 49 | 1000 | 551 | ok |
| yolo26s-seg.dxnn | 1 | 3 | 45.8 ±0.2 | 45.8 | 322 | 32.7 | 63.9 | 53~54 | 1000 | 421 | ok |
| yolo26s-seg.dxnn | 2 | 3 | 46.0 ±0.3 | 23.0 | 322 | 33.5 | 63.0 | 54 | 1000 | 568 | ok |
| yolo26m-seg.dxnn | 1 | 3 | 45.5 ±0.4 | 45.5 | 293 | 58.1 | 87.5 | 70~72 | 1000 | 447 | ok |
| yolo26m-seg.dxnn | 2 | 3 | 45.5 ±0.3 | 22.7 | 295 | 58.8 | 83.7 | 73~74 | 1000 | 590 | ok |
| yolo26l-seg.dxnn | 1 | 3 | 44.9 ±0.5 | 44.9 | 262 | 76.8 | 96.0 | 73~76 | 1000 | 456 | ok |
| yolo26l-seg.dxnn | 2 | 3 | 44.3 ±0.2 | 22.2 | 267 | 76.6 | 93.4 | 78~79 | 800~1000 | 599 | ok |
| yolo26x-seg.dxnn | 1 | 3 | 24.9 ±1.6 | 24.9 | 114 | 91.3 | 100.0 | 80~81 | 600~1000 | 525 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | 2 | 3 | 61.2 ±0.4 | 30.6 | 353 | 20.8 | 64.1 | 50 | 1000 | 592 | ok |
| yolo26n-seg.dxnn | 3 | 3 | 61.3 ±0.7 | 20.4 | 351 | 21.0 | 65.2 | 50 | 1000 | 698 | ok |
| yolo26s-seg.dxnn | 2 | 3 | 61.2 ±0.6 | 30.6 | 350 | 42.1 | 73.8 | 58~59 | 1000 | 606 | ok |
| yolo26s-seg.dxnn | 3 | 3 | 61.5 ±0.6 | 20.5 | 346 | 42.6 | 74.3 | 59~60 | 1000 | 713 | ok |
| yolo26m-seg.dxnn | 1 | 3 | 58.5 ±0.9 | 58.5 | 308 | 79.8 | 94.9 | 58~75 | 1000 | 478 | ok |
| yolo26m-seg.dxnn | 2 | 3 | 58.1 ±0.2 | 29.1 | 313 | 81.1 | 94.7 | 72~78 | 800~1000 | 630 | ok |
| yolo26l-seg.dxnn | 1 | 3 | 51.2 ±0.4 | 51.2 | 245 | 91.8 | 100.0 | 74~78 | 800~1000 | 467 | ok |
| yolo26l-seg.dxnn | 2 | 3 | 48.0 ±0.6 | 24.0 | 228 | 92.4 | 100.0 | 80~81 | 800~1000 | 614 | ok |
| yolo26x-seg.dxnn | 1 | 3 | 26.5 ±2.6 | 26.5 | 117 | 93.6 | 100.0 | 68~80 | 600~1000 | 544 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-seg.dxnn | 1 | 46.1 | 2 | 30.6 |
| yolo26s-seg.dxnn | 1 | 45.8 | 2 | 30.6 |
| yolo26m-seg.dxnn | 1 | 45.5 | 1 | 58.5 |
| yolo26l-seg.dxnn | 1 | 44.9 | 1 | 51.2 |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | 2 | 3 | 70.0 ±0.3 | 35.0 | 312 | 81.9 | 95.0 | 50~59 | 1000 | 458 | ok |
| yolo26n-obb.dxnn | 3 | 3 | 69.8 ±0.3 | 23.2 | 312 | 82.2 | 97.0 | 52~57 | 1000 | 565 | ok |
| yolo26s-obb.dxnn | 1 | 3 | 43.5 ±0.1 | 43.5 | 139 | 92.9 | 100.0 | 61~62 | 1000 | 340 | ok |
| yolo26s-obb.dxnn | 2 | 3 | 43.5 ±0.0 | 21.8 | 144 | 95.4 | 100.0 | 64~65 | 1000 | 475 | ok |
| yolo26m-obb.dxnn | 1 | 3 | 31.9 ±0.1 | 31.9 | 100 | 94.1 | 100.0 | 69~72 | 1000 | 363 | ok |
| yolo26m-obb.dxnn | 2 | 3 | 31.8 ±0.0 | 15.9 | 103 | 95.9 | 100.0 | 76~78 | 1000 | 498 | ok |
| yolo26l-obb.dxnn | 1 | 3 | 23.3 ±0.0 | 23.3 | 74 | 95.3 | 100.0 | 59~68 | 1000 | 373 | ok |
| yolo26x-obb.dxnn | 1 | 3 | 13.5 ±0.0 | 13.5 | 46 | 92.9 | 100.0 | 66~77 | 1000 | 441 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | 2 | 3 | 74.0 ±0.1 | 37.0 | 251 | 94.1 | 100.0 | 58~60 | 1000 | 457 | ok |
| yolo26n-obb.dxnn | 3 | 3 | 74.1 ±0.0 | 24.7 | 249 | 95.6 | 100.0 | 60 | 1000 | 556 | ok |
| yolo26s-obb.dxnn | 1 | 3 | 43.5 ±0.0 | 43.5 | 129 | 93.5 | 100.0 | 62~64 | 1000 | 337 | ok |
| yolo26s-obb.dxnn | 2 | 3 | 43.5 ±0.0 | 21.8 | 135 | 95.6 | 100.0 | 64~65 | 1000 | 474 | ok |
| yolo26m-obb.dxnn | 1 | 3 | 31.9 ±0.0 | 31.9 | 99 | 94.7 | 100.0 | 71~75 | 1000 | 358 | ok |
| yolo26m-obb.dxnn | 2 | 3 | 31.9 ±0.0 | 16.0 | 99 | 96.0 | 100.0 | 77~78 | 1000 | 492 | ok |
| yolo26l-obb.dxnn | 1 | 3 | 23.3 ±0.0 | 23.3 | 74 | 95.1 | 100.0 | 70~73 | 1000 | 369 | ok |
| yolo26x-obb.dxnn | 1 | 3 | 13.5 ±0.1 | 13.5 | 44 | 92.4 | 100.0 | 77~79 | 800~1000 | 440 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-obb.dxnn | 2 | 35.0 | 2 | 37.0 |
| yolo26s-obb.dxnn | 1 | 43.5 | 1 | 43.5 |
| yolo26m-obb.dxnn | 1 | 31.9 | 1 | 31.9 |

---
*Report generated by dx_stream benchmark tool*
