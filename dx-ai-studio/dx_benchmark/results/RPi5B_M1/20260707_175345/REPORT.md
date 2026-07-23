# YOLO26 Benchmark Report

**Generated:** 2026-07-08 12:40:23 (Local)

## Test Timing

| # | Type | Start | End | Duration |
|---|------|-------|-----|----------|
| 1 | run | 2026-07-07 17:53:45 | 2026-07-08 12:40:23 | 18h 46m 38s |

## Executive Summary

### Object Detection

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n.dxnn | ON | 33.43 | 96.4 | 61.7 | 2 |
| yolo26n.dxnn | OFF | 25.66 | 146.7 | 79.6 | 2 |
| yolo26s.dxnn | ON | 40.92 | 94.5 | 61.8 | 1 |
| yolo26s.dxnn | OFF | 33.48 | 104.6 | 79.5 | 2 |
| yolo26m.dxnn | ON | 47.70 | 76.3 | 61.6 | 1 |
| yolo26m.dxnn | OFF | 40.26 | 76.3 | 75.5 | 2 |
| yolo26l.dxnn | ON | 56.93 | 57.1 | 56.9 | 1 |
| yolo26l.dxnn | OFF | 49.39 | 57.1 | 57.1 | 1 |
| yolo26x.dxnn | ON | 87.65 | 32.7 | 32.8 | 1 |
| yolo26x.dxnn | OFF | — | 32.7 | 32.8 | 1 |

### Pose Estimation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-pose.dxnn | ON | — | 136.7 | 75.5 | 2 |
| yolo26n-pose.dxnn | OFF | 22.67 | 164.1 | 110.0 | 3 |
| yolo26s-pose.dxnn | ON | 34.98 | 102.1 | 75.8 | 2 |
| yolo26s-pose.dxnn | OFF | 30.95 | 102.1 | 101.5 | 3 |
| yolo26m-pose.dxnn | ON | 42.80 | 74.6 | 74.2 | 2 |
| yolo26m-pose.dxnn | OFF | 37.30 | 74.6 | 74.6 | 2 |
| yolo26l-pose.dxnn | ON | 51.05 | 55.9 | 56.0 | 1 |
| yolo26l-pose.dxnn | OFF | 46.38 | 56.0 | 56.0 | 1 |
| yolo26x-pose.dxnn | ON | 82.15 | 32.2 | 32.2 | 1 |
| yolo26x-pose.dxnn | OFF | 77.44 | 32.2 | 32.2 | 1 |

### Segmentation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-seg.dxnn | ON | 50.94 | 57.6 | 41.4 | 1 |
| yolo26n-seg.dxnn | OFF | 44.04 | 89.7 | 55.0 | 1 |
| yolo26s-seg.dxnn | ON | 59.97 | 58.1 | 41.5 | 1 |
| yolo26s-seg.dxnn | OFF | 51.55 | 77.3 | 55.0 | 1 |
| yolo26m-seg.dxnn | ON | 75.96 | 55.5 | 41.3 | 1 |
| yolo26m-seg.dxnn | OFF | 65.18 | 55.9 | 52.6 | 1 |
| yolo26l-seg.dxnn | ON | 84.97 | 45.4 | 41.2 | 1 |
| yolo26l-seg.dxnn | OFF | 77.18 | 45.4 | 45.2 | 1 |
| yolo26x-seg.dxnn | ON | 126.94 | 25.6 | 25.6 | — |
| yolo26x-seg.dxnn | OFF | 117.48 | 25.6 | 24.1 | — |

### Oriented BBox (OBB)

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-obb.dxnn | ON | 46.93 | 59.3 | 59.1 | 1 |
| yolo26n-obb.dxnn | OFF | 41.69 | 59.2 | 59.2 | 1 |
| yolo26s-obb.dxnn | ON | 65.46 | 36.3 | 36.4 | 1 |
| yolo26s-obb.dxnn | OFF | 60.84 | 36.3 | 36.4 | 1 |
| yolo26m-obb.dxnn | ON | 84.36 | 27.3 | 27.3 | — |
| yolo26m-obb.dxnn | OFF | 79.73 | 27.3 | 27.3 | — |
| yolo26l-obb.dxnn | ON | 106.99 | 20.5 | 20.5 | — |
| yolo26l-obb.dxnn | OFF | 101.55 | 20.5 | 20.5 | — |
| yolo26x-obb.dxnn | ON | 184.61 | 11.9 | 11.9 | — |
| yolo26x-obb.dxnn | OFF | 179.31 | 11.9 | 11.9 | — |

### Classification

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-cls.dxnn | ON | 1.42 | 2657.1 | 187.3 | — |
| yolo26n-cls.dxnn | OFF | 1.44 | 2661.3 | 187.9 | — |
| yolo26s-cls.dxnn | ON | 2.12 | 1601.3 | 188.2 | — |
| yolo26s-cls.dxnn | OFF | 2.11 | 1600.4 | 187.5 | — |
| yolo26m-cls.dxnn | ON | 2.55 | 1280.9 | 187.4 | — |
| yolo26m-cls.dxnn | OFF | 2.57 | 1280.8 | 187.9 | — |
| yolo26l-cls.dxnn | ON | 3.97 | 792.5 | 187.5 | — |
| yolo26l-cls.dxnn | OFF | 3.89 | 791.5 | 187.5 | — |
| yolo26x-cls.dxnn | ON | 6.85 | 400.5 | 187.1 | — |
| yolo26x-cls.dxnn | OFF | 6.78 | 400.7 | 187.4 | — |

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
| NPU RT | v3.2.0 |
| NPU Driver (RT) | v2.1.0 |
| NPU Driver (PCIe) | v2.0.1 |
| NPU Firmware | v2.5.0 |
| NPU Memory | LPDDR5 5600 Mbps, 3.92GiB |
| NPU Board | M.2, Rev 1.0 |
| NPU PCIe | Gen3 X1 [01:00:00] |

### Tools

| Tool | Available | Version |
|------|-----------|---------|
| run_model | Yes | DXRT v3.2.0 run_model |
| gst-launch-1.0 | Yes | gst-launch-1.0 version 1.22.0 |
| gst-inspect-1.0 | Yes | gst-inspect-1.0 version 1.22.0 |
| dxtop | Yes | DX-TOP 1.0.1 |
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
| yolo26n.dxnn | Object Detection | 640×640 | 140.1 | Yes | ✅ |
| yolo26s.dxnn | Object Detection | 640×640 | 147.2 | Yes | ✅ |
| yolo26m.dxnn | Object Detection | 640×640 | 148.4 | Yes | ✅ |
| yolo26l.dxnn | Object Detection | 640×640 | 162.6 | Yes | ✅ |
| yolo26x.dxnn | Object Detection | 640×640 | 271.1 | Yes | ✅ |
| yolo26n-pose.dxnn | Pose Estimation | 640×640 | — | Yes | ✅ |
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
| yolo26n.dxnn | 96.4 ±0.3 | 215 | 33.7 | 67.3 | 44~46 | 1000 | ok |
| yolo26s.dxnn | 94.5 ±0.6 | 215 | 76.2 | 90.0 | 55~56 | 1000 | ok |
| yolo26m.dxnn | 76.3 ±0.0 | 125 | 89.0 | 100.0 | 60~62 | 1000 | ok |
| yolo26l.dxnn | 57.1 ±0.0 | 82 | 92.7 | 100.0 | 59~62 | 1000 | ok |
| yolo26x.dxnn | 32.7 ±0.0 | 49 | 90.1 | 100.0 | 60~64 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n.dxnn | 146.7 ±0.1 | 120 | 67.6 | 82.7 | 53~55 | 1000 | ok |
| yolo26s.dxnn | 104.6 ±0.0 | 81 | 91.7 | 100.0 | 57~59 | 1000 | ok |
| yolo26m.dxnn | 76.3 ±0.0 | 53 | 87.5 | 100.0 | 59~63 | 1000 | ok |
| yolo26l.dxnn | 57.1 ±0.0 | 46 | 92.4 | 100.0 | 59~63 | 1000 | ok |
| yolo26x.dxnn | 32.7 ±0.0 | 26 | 89.6 | 100.0 | 53~58 | 1000 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-pose.dxnn | 136.7 ±0.4 | 216 | 60.9 | 91.1 | 47~50 | 1000 | ok |
| yolo26s-pose.dxnn | 102.1 ±0.0 | 113 | 91.3 | 100.0 | 57~59 | 1000 | ok |
| yolo26m-pose.dxnn | 74.6 ±0.0 | 75 | 89.7 | 100.0 | 60~63 | 1000 | ok |
| yolo26l-pose.dxnn | 55.9 ±0.0 | 58 | 89.8 | 100.0 | 59~62 | 1000 | ok |
| yolo26x-pose.dxnn | 32.2 ±0.0 | 34 | 88.3 | 100.0 | 61~64 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-pose.dxnn | 164.1 ±0.1 | 89 | 92.1 | 100.0 | 56~58 | 1000 | ok |
| yolo26s-pose.dxnn | 102.1 ±0.0 | 53 | 92.3 | 100.0 | 57~59 | 1000 | ok |
| yolo26m-pose.dxnn | 74.6 ±0.0 | 39 | 91.1 | 100.0 | 60~63 | 1000 | ok |
| yolo26l-pose.dxnn | 56.0 ±0.0 | 30 | 92.3 | 100.0 | 59~62 | 1000 | ok |
| yolo26x-pose.dxnn | 32.2 ±0.0 | 18 | 89.0 | 100.0 | 61~64 | 1000 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-seg.dxnn | 57.6 ±0.3 | 281 | 22.5 | 68.4 | 51~52 | 1000 | ok |
| yolo26s-seg.dxnn | 58.1 ±0.2 | 277 | 46.6 | 77.1 | 54~55 | 1000 | ok |
| yolo26m-seg.dxnn | 55.5 ±0.1 | 192 | 88.5 | 100.0 | 61~65 | 1000 | ok |
| yolo26l-seg.dxnn | 45.4 ±0.0 | 121 | 89.3 | 100.0 | 61~65 | 1000 | ok |
| yolo26x-seg.dxnn | 25.6 ±0.0 | 64 | 88.0 | 100.0 | 63~68 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-seg.dxnn | 89.7 ±0.1 | 172 | 39.7 | 69.8 | 51~53 | 1000 | ok |
| yolo26s-seg.dxnn | 77.3 ±0.0 | 136 | 77.0 | 87.5 | 57~59 | 1000 | ok |
| yolo26m-seg.dxnn | 55.9 ±0.0 | 85 | 90.3 | 100.0 | 62~65 | 1000 | ok |
| yolo26l-seg.dxnn | 45.4 ±0.0 | 65 | 90.2 | 100.0 | 61~66 | 1000 | ok |
| yolo26x-seg.dxnn | 25.6 ±0.0 | 41 | 88.1 | 100.0 | 63~68 | 1000 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-obb.dxnn | 59.3 ±0.0 | 68 | 89.6 | 100.0 | 55~57 | 1000 | ok |
| yolo26s-obb.dxnn | 36.3 ±0.0 | 42 | 88.9 | 100.0 | 56~58 | 1000 | ok |
| yolo26m-obb.dxnn | 27.3 ±0.0 | 32 | 91.0 | 100.0 | 59~62 | 1000 | ok |
| yolo26l-obb.dxnn | 20.5 ±0.0 | 24 | 88.8 | 100.0 | 59~62 | 1000 | ok |
| yolo26x-obb.dxnn | 11.9 ±0.0 | 14 | 89.2 | 100.0 | 61~64 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-obb.dxnn | 59.2 ±0.0 | 40 | 91.6 | 100.0 | 55~57 | 1000 | ok |
| yolo26s-obb.dxnn | 36.3 ±0.0 | 24 | 91.5 | 100.0 | 56~57 | 1000 | ok |
| yolo26m-obb.dxnn | 27.3 ±0.0 | 19 | 88.8 | 100.0 | 60~63 | 1000 | ok |
| yolo26l-obb.dxnn | 20.5 ±0.0 | 14 | 89.8 | 100.0 | 59~62 | 1000 | ok |
| yolo26x-obb.dxnn | 11.9 ±0.0 | 8 | 89.8 | 100.0 | 61~64 | 1000 | ok |

#### Classification

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-cls.dxnn | 2657.1 ±1.5 | 47 | 91.0 | 98.0 | 54 | 1000 | ok |
| yolo26s-cls.dxnn | 1601.3 ±0.3 | 30 | 90.4 | 98.5 | 53~55 | 1000 | ok |
| yolo26m-cls.dxnn | 1280.9 ±0.4 | 25 | 91.3 | 98.9 | 52~56 | 1000 | ok |
| yolo26l-cls.dxnn | 792.5 ±0.3 | 15 | 91.7 | 99.0 | 56~58 | 1000 | ok |
| yolo26x-cls.dxnn | 400.5 ±0.1 | 8 | 89.6 | 100.0 | 56~59 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-cls.dxnn | 2661.3 ±0.8 | 48 | 91.2 | 97.9 | 52~53 | 1000 | ok |
| yolo26s-cls.dxnn | 1600.4 ±0.3 | 30 | 91.1 | 98.5 | 49~51 | 1000 | ok |
| yolo26m-cls.dxnn | 1280.8 ±0.4 | 24 | 91.0 | 99.1 | 53~56 | 1000 | ok |
| yolo26l-cls.dxnn | 791.5 ±0.1 | 15 | 90.6 | 99.5 | 51~54 | 1000 | ok |
| yolo26x-cls.dxnn | 400.7 ±0.1 | 8 | 91.1 | 99.9 | 58~61 | 1000 | ok |

### Latency (Single-Core, Sync)

#### Object Detection

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n.dxnn | 29.9 | 33.43 | 25.60 | 7.83 | 40 | ok |
| yolo26s.dxnn | 24.4 | 40.92 | 33.37 | 7.55 | 50 | ok |
| yolo26m.dxnn | 21.0 | 47.70 | 40.37 | 7.32 | 52 | ok |
| yolo26l.dxnn | 17.6 | 56.93 | 49.40 | 7.53 | 52 | ok |
| yolo26x.dxnn | 11.4 | 87.65 | 80.12 | 7.52 | 53 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n.dxnn | 39.0 | 25.66 | 25.66 | 49 | ok |
| yolo26s.dxnn | 29.9 | 33.48 | 33.48 | 51 | ok |
| yolo26m.dxnn | 24.8 | 40.26 | 40.26 | 52 | ok |
| yolo26l.dxnn | 20.2 | 49.39 | 49.39 | 52 | ok |
| yolo26x.dxnn | N/A | N/A | N/A | N/A | timeout |

#### Pose Estimation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-pose.dxnn | N/A | N/A | N/A | N/A | N/A | timeout |
| yolo26s-pose.dxnn | 28.6 | 34.98 | 30.03 | 4.95 | 51 | ok |
| yolo26m-pose.dxnn | 23.4 | 42.80 | 37.99 | 4.81 | 52 | ok |
| yolo26l-pose.dxnn | 19.6 | 51.05 | 46.52 | 4.53 | 52 | ok |
| yolo26x-pose.dxnn | 12.2 | 82.15 | 77.48 | 4.67 | 53 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-pose.dxnn | 44.1 | 22.67 | 22.67 | 50 | ok |
| yolo26s-pose.dxnn | 32.3 | 30.95 | 30.95 | 51 | ok |
| yolo26m-pose.dxnn | 26.8 | 37.30 | 37.30 | 52 | ok |
| yolo26l-pose.dxnn | 21.6 | 46.38 | 46.38 | 52 | ok |
| yolo26x-pose.dxnn | 12.9 | 77.44 | 77.44 | 53 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-seg.dxnn | 19.6 | 50.94 | 41.68 | 9.25 | 50 | ok |
| yolo26s-seg.dxnn | 16.7 | 59.97 | 50.73 | 9.23 | 49 | ok |
| yolo26m-seg.dxnn | 13.2 | 75.96 | 66.44 | 9.52 | 50 | ok |
| yolo26l-seg.dxnn | 11.8 | 84.97 | 75.52 | 9.45 | 52 | ok |
| yolo26x-seg.dxnn | 7.9 | 126.94 | 117.52 | 9.42 | 53 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-seg.dxnn | 22.7 | 44.04 | 44.04 | 49 | ok |
| yolo26s-seg.dxnn | 19.4 | 51.55 | 51.55 | 51 | ok |
| yolo26m-seg.dxnn | 15.3 | 65.18 | 65.18 | 52 | ok |
| yolo26l-seg.dxnn | 13.0 | 77.18 | 77.18 | 52 | ok |
| yolo26x-seg.dxnn | 8.5 | 117.48 | 117.48 | 54 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-obb.dxnn | 21.3 | 46.93 | 41.44 | 5.50 | 51 | ok |
| yolo26s-obb.dxnn | 15.3 | 65.46 | 60.24 | 5.22 | 52 | ok |
| yolo26m-obb.dxnn | 11.9 | 84.36 | 79.09 | 5.26 | 53 | ok |
| yolo26l-obb.dxnn | 9.3 | 106.99 | 101.48 | 5.52 | 53 | ok |
| yolo26x-obb.dxnn | 5.4 | 184.61 | 179.10 | 5.51 | 55 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-obb.dxnn | 24.0 | 41.69 | 41.69 | 51 | ok |
| yolo26s-obb.dxnn | 16.4 | 60.84 | 60.84 | 51 | ok |
| yolo26m-obb.dxnn | 12.5 | 79.73 | 79.73 | 53 | ok |
| yolo26l-obb.dxnn | 9.8 | 101.55 | 101.55 | 53 | ok |
| yolo26x-obb.dxnn | 5.6 | 179.31 | 179.31 | 55 | ok |

#### Classification

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-cls.dxnn | 704.1 | 1.42 | 1.42 | N/A | 50 | ok |
| yolo26s-cls.dxnn | 472.7 | 2.12 | 2.12 | N/A | 48 | ok |
| yolo26m-cls.dxnn | 392.1 | 2.55 | 2.55 | N/A | 43 | ok |
| yolo26l-cls.dxnn | 252.1 | 3.97 | 3.97 | N/A | 49 | ok |
| yolo26x-cls.dxnn | 146.0 | 6.85 | 6.85 | N/A | 49 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-cls.dxnn | 696.2 | 1.44 | 1.44 | 49 | ok |
| yolo26s-cls.dxnn | 473.9 | 2.11 | 2.11 | 43 | ok |
| yolo26m-cls.dxnn | 388.4 | 2.57 | 2.57 | 44 | ok |
| yolo26l-cls.dxnn | 257.1 | 3.89 | 3.89 | 44 | ok |
| yolo26x-cls.dxnn | 147.4 | 6.78 | 6.78 | 50 | ok |

## E2E Pipeline (Single-Stream)

### Object Detection

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | avdec_h264 | 3455 | 3 | 61.7 ±0.0 | 56.01 | 328 | 23.2 | 52.0 | 45~48 | 1000 | 319 | ok |
| yolo26s.dxnn | avdec_h264 | 3455 | 3 | 61.8 ±0.1 | 55.90 | 328 | 42.2 | 71.2 | 53~55 | 1000 | 336 | ok |
| yolo26m.dxnn | avdec_h264 | 3455 | 3 | 61.6 ±0.3 | 56.13 | 315 | 65.9 | 86.0 | 62~65 | 1000 | 356 | ok |
| yolo26l.dxnn | avdec_h264 | 3455 | 3 | 56.9 ±0.0 | 60.77 | 203 | 93.6 | 100.0 | 66~69 | 1000 | 365 | ok |
| yolo26x.dxnn | avdec_h264 | 3455 | 2/3 | 32.8 ±0.0 | 105.44 | 96 | 96.7 | 100.0 | 72~75 | 1000 | 427 | partial |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | avdec_h264 | 3455 | 3 | 79.6 ±0.1 | 43.41 | 328 | 27.7 | 70.7 | 52 | 1000 | 349 | ok |
| yolo26s.dxnn | avdec_h264 | 3455 | 3 | 79.5 ±0.3 | 43.48 | 325 | 53.9 | 85.4 | 49~52 | 1000 | 367 | ok |
| yolo26m.dxnn | avdec_h264 | 3455 | 3 | 75.5 ±0.1 | 45.77 | 289 | 92.2 | 100.0 | 65~68 | 1000 | 373 | ok |
| yolo26l.dxnn | avdec_h264 | 3455 | 3 | 57.1 ±0.0 | 60.52 | 185 | 92.9 | 100.0 | 65~69 | 1000 | 372 | ok |
| yolo26x.dxnn | avdec_h264 | 3455 | 2/3 | 32.8 ±0.0 | 105.46 | 106 | 96.8 | 100.0 | 70~73 | 1000 | 430 | partial |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n.dxnn | 61.7 | 79.6 | -17.9 | -22.5% |
| yolo26s.dxnn | 61.8 | 79.5 | -17.6 | -22.2% |
| yolo26m.dxnn | 61.6 | 75.5 | -13.9 | -18.4% |
| yolo26l.dxnn | 56.9 | 57.1 | -0.2 | -0.4% |
| yolo26x.dxnn | 32.8 | 32.8 | +0.0 | +0.0% |

### Pose Estimation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | avdec_h264 | 3455 | 3 | 75.5 ±0.3 | 45.79 | 347 | 30.5 | 61.5 | 46~48 | 1000 | 310 | ok |
| yolo26s-pose.dxnn | avdec_h264 | 3455 | 3 | 75.8 ±0.1 | 45.55 | 337 | 58.5 | 80.7 | 58~59 | 1000 | 324 | ok |
| yolo26m-pose.dxnn | avdec_h264 | 3455 | 3 | 74.2 ±0.1 | 46.55 | 241 | 93.4 | 100.0 | 66~69 | 1000 | 348 | ok |
| yolo26l-pose.dxnn | avdec_h264 | 3455 | 3 | 56.0 ±0.0 | 61.72 | 140 | 94.1 | 100.0 | 67~70 | 1000 | 355 | ok |
| yolo26x-pose.dxnn | avdec_h264 | 3455 | 3 | 32.2 ±0.0 | 107.16 | 81 | 95.2 | 100.0 | 73~78 | 1000 | 417 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | avdec_h264 | 3455 | 3 | 110.0 ±0.6 | 31.39 | 323 | 48.1 | 73.2 | 56 | 1000 | 284 | ok |
| yolo26s-pose.dxnn | avdec_h264 | 3455 | 3 | 101.5 ±0.2 | 34.03 | 246 | 89.8 | 100.0 | 60~61 | 1000 | 315 | ok |
| yolo26m-pose.dxnn | avdec_h264 | 3455 | 3 | 74.6 ±0.1 | 46.34 | 153 | 92.7 | 100.0 | 65~69 | 1000 | 334 | ok |
| yolo26l-pose.dxnn | avdec_h264 | 3455 | 3 | 56.0 ±0.0 | 61.70 | 112 | 94.1 | 100.0 | 67~70 | 1000 | 344 | ok |
| yolo26x-pose.dxnn | avdec_h264 | 3455 | 3 | 32.2 ±0.0 | 107.17 | 68 | 95.4 | 100.0 | 73~78 | 1000 | 407 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-pose.dxnn | 75.5 | 110.0 | -34.6 | -31.4% |
| yolo26s-pose.dxnn | 75.8 | 101.5 | -25.7 | -25.3% |
| yolo26m-pose.dxnn | 74.2 | 74.6 | -0.3 | -0.5% |
| yolo26l-pose.dxnn | 56.0 | 56.0 | -0.0 | -0.1% |
| yolo26x-pose.dxnn | 32.2 | 32.2 | +0.0 | +0.0% |

### Segmentation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | avdec_h264 | 3455 | 3 | 41.4 ±0.1 | 83.42 | 335 | 18.8 | 42.2 | 49~50 | 1000 | 420 | ok |
| yolo26s-seg.dxnn | avdec_h264 | 3455 | 3 | 41.5 ±0.1 | 83.16 | 330 | 34.2 | 62.3 | 49~54 | 1000 | 435 | ok |
| yolo26m-seg.dxnn | avdec_h264 | 3455 | 3 | 41.3 ±0.2 | 83.68 | 312 | 58.8 | 86.1 | 66~69 | 1000 | 460 | ok |
| yolo26l-seg.dxnn | avdec_h264 | 3455 | 3 | 41.2 ±0.0 | 83.80 | 275 | 80.7 | 95.6 | 70~73 | 1000 | 469 | ok |
| yolo26x-seg.dxnn | avdec_h264 | 3455 | 3 | 25.6 ±0.0 | 134.90 | 111 | 94.8 | 100.0 | 68~79 | 1000 | 535 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | avdec_h264 | 3455 | 3 | 55.0 ±0.3 | 62.86 | 368 | 23.6 | 65.9 | 51 | 1000 | 464 | ok |
| yolo26s-seg.dxnn | avdec_h264 | 3455 | 3 | 55.0 ±0.4 | 62.78 | 361 | 46.2 | 75.2 | 58 | 1000 | 479 | ok |
| yolo26m-seg.dxnn | avdec_h264 | 3455 | 3 | 52.6 ±0.7 | 65.72 | 317 | 83.5 | 96.3 | 71~74 | 1000 | 498 | ok |
| yolo26l-seg.dxnn | avdec_h264 | 3455 | 3 | 45.2 ±0.0 | 76.50 | 231 | 94.6 | 100.0 | 72~76 | 1000 | 480 | ok |
| yolo26x-seg.dxnn | avdec_h264 | 3455 | 3 | 24.1 ±1.3 | 143.12 | 108 | 93.6 | 100.0 | 79~81 | 800~1000 | 543 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-seg.dxnn | 41.4 | 55.0 | -13.5 | -24.6% |
| yolo26s-seg.dxnn | 41.5 | 55.0 | -13.5 | -24.5% |
| yolo26m-seg.dxnn | 41.3 | 52.6 | -11.3 | -21.5% |
| yolo26l-seg.dxnn | 41.2 | 45.2 | -3.9 | -8.7% |
| yolo26x-seg.dxnn | 25.6 | 24.1 | +1.5 | +6.1% |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | avdec_h264 | 2640 | 3 | 59.1 ±0.0 | 44.66 | 243 | 92.3 | 100.0 | 58~60 | 1000 | 343 | ok |
| yolo26s-obb.dxnn | avdec_h264 | 2640 | 3 | 36.4 ±0.0 | 72.58 | 124 | 94.9 | 100.0 | 61~63 | 1000 | 360 | ok |
| yolo26m-obb.dxnn | avdec_h264 | 2640 | 3 | 27.3 ±0.0 | 96.64 | 94 | 95.7 | 100.0 | 69~72 | 1000 | 382 | ok |
| yolo26l-obb.dxnn | avdec_h264 | 2640 | 3 | 20.5 ±0.0 | 128.94 | 74 | 96.8 | 100.0 | 61~69 | 1000 | 390 | ok |
| yolo26x-obb.dxnn | avdec_h264 | 2640 | 3 | 11.9 ±0.0 | 221.69 | 46 | 98.0 | 100.0 | 76~80 | 1000 | 461 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | avdec_h264 | 2640 | 3 | 59.2 ±0.0 | 44.60 | 199 | 91.2 | 100.0 | 57~59 | 1000 | 337 | ok |
| yolo26s-obb.dxnn | avdec_h264 | 2640 | 3 | 36.4 ±0.0 | 72.61 | 122 | 94.9 | 100.0 | 61~63 | 1000 | 355 | ok |
| yolo26m-obb.dxnn | avdec_h264 | 2640 | 3 | 27.3 ±0.0 | 96.67 | 94 | 95.8 | 100.0 | 63~70 | 1000 | 373 | ok |
| yolo26l-obb.dxnn | avdec_h264 | 2640 | 3 | 20.5 ±0.0 | 128.87 | 74 | 96.6 | 100.0 | 70~74 | 1000 | 386 | ok |
| yolo26x-obb.dxnn | avdec_h264 | 2640 | 3 | 11.9 ±0.0 | 221.69 | 47 | 97.9 | 100.0 | 76~80 | 1000 | 460 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-obb.dxnn | 59.1 | 59.2 | -0.1 | -0.1% |
| yolo26s-obb.dxnn | 36.4 | 36.4 | +0.0 | +0.0% |
| yolo26m-obb.dxnn | 27.3 | 27.3 | +0.0 | +0.0% |
| yolo26l-obb.dxnn | 20.5 | 20.5 | -0.0 | -0.1% |
| yolo26x-obb.dxnn | 11.9 | 11.9 | +0.0 | +0.0% |

### Classification

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-cls.dxnn | avdec_h264 | 3455 | 3 | 187.3 ±0.7 | 18.45 | 274 | 5.2 | 16.8 | 49~50 | 1000 | 197 | ok |
| yolo26s-cls.dxnn | avdec_h264 | 3455 | 3 | 188.2 ±0.4 | 18.35 | 277 | 8.8 | 27.9 | 43 | 1000 | 204 | ok |
| yolo26m-cls.dxnn | avdec_h264 | 3455 | 3 | 187.4 ±0.6 | 18.44 | 276 | 11.6 | 34.0 | 44 | 1000 | 214 | ok |
| yolo26l-cls.dxnn | avdec_h264 | 3455 | 3 | 187.5 ±0.2 | 18.43 | 276 | 18.9 | 47.7 | 43~53 | 1000 | 231 | ok |
| yolo26x-cls.dxnn | avdec_h264 | 3455 | 3 | 187.1 ±0.8 | 18.46 | 274 | 36.0 | 64.3 | 55~56 | 1000 | 253 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-cls.dxnn | avdec_h264 | 3455 | 3 | 187.9 ±0.3 | 18.38 | 276 | 5.2 | 16.7 | 48~49 | 1000 | 197 | ok |
| yolo26s-cls.dxnn | avdec_h264 | 3455 | 3 | 187.5 ±0.8 | 18.42 | 275 | 8.5 | 27.8 | 42~43 | 1000 | 205 | ok |
| yolo26m-cls.dxnn | avdec_h264 | 3455 | 3 | 187.9 ±0.5 | 18.39 | 276 | 11.6 | 34.2 | 50~51 | 1000 | 214 | ok |
| yolo26l-cls.dxnn | avdec_h264 | 3455 | 3 | 187.5 ±0.3 | 18.43 | 275 | 18.9 | 47.3 | 49~50 | 1000 | 219 | ok |
| yolo26x-cls.dxnn | avdec_h264 | 3455 | 3 | 187.4 ±0.1 | 18.44 | 274 | 36.4 | 63.5 | 56~57 | 1000 | 252 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-cls.dxnn | 187.3 | 187.9 | -0.7 | -0.4% |
| yolo26s-cls.dxnn | 188.2 | 187.5 | +0.7 | +0.4% |
| yolo26m-cls.dxnn | 187.4 | 187.9 | -0.5 | -0.3% |
| yolo26l-cls.dxnn | 187.5 | 187.5 | +0.0 | +0.0% |
| yolo26x-cls.dxnn | 187.1 | 187.4 | -0.3 | -0.1% |

## E2E Pipeline (Multi-Stream)

### Object Detection

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | 2 | 3 | 61.6 ±0.1 | 30.8 | 338 | 23.9 | 52.8 | 46~48 | 1000 | 456 | ok |
| yolo26n.dxnn | 3 | 3 | 60.6 ±0.9 | 20.2 | 337 | 23.7 | 53.8 | 49~50 | 1000 | 557 | ok |
| yolo26s.dxnn | 2 | 3 | 59.5 ±0.1 | 29.8 | 334 | 41.9 | 70.3 | 55~56 | 1000 | 471 | ok |
| yolo26s.dxnn | 1 | 3 | 61.8 ±0.1 | 61.8 | 328 | 42.2 | 71.2 | 53~55 | 1000 | 336 | ok |
| yolo26m.dxnn | 2 | 3 | 59.7 ±0.3 | 29.9 | 320 | 64.1 | 85.1 | 66~67 | 1000 | 494 | ok |
| yolo26m.dxnn | 1 | 3 | 61.6 ±0.3 | 61.6 | 315 | 65.9 | 86.0 | 62~65 | 1000 | 356 | ok |
| yolo26l.dxnn | 1 | 3 | 56.9 ±0.0 | 56.9 | 203 | 93.6 | 100.0 | 66~69 | 1000 | 365 | ok |
| yolo26l.dxnn | 2 | 3 | 56.8 ±0.0 | 28.4 | 211 | 96.3 | 100.0 | 72~73 | 1000 | 500 | ok |
| yolo26x.dxnn | 1 | 2/3 | 32.8 ±0.0 | 32.8 | 96 | 96.7 | 100.0 | 72~75 | 1000 | 427 | partial |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | 2 | 3 | 79.8 ±0.4 | 39.9 | 319 | 28.0 | 71.7 | 50~51 | 1000 | 485 | ok |
| yolo26n.dxnn | 3 | 3 | 79.3 ±0.2 | 26.4 | 328 | 28.6 | 73.1 | 51~52 | 1000 | 588 | ok |
| yolo26s.dxnn | 2 | 3 | 79.7 ±0.3 | 39.9 | 325 | 57.2 | 85.3 | 56~57 | 1000 | 497 | ok |
| yolo26s.dxnn | 3 | 3 | 79.3 ±0.1 | 26.4 | 326 | 57.1 | 85.8 | 58~59 | 1000 | 597 | ok |
| yolo26m.dxnn | 2 | 3 | 75.4 ±0.1 | 37.7 | 289 | 94.7 | 100.0 | 70~72 | 1000 | 515 | ok |
| yolo26m.dxnn | 3 | 3 | 75.3 ±0.2 | 25.1 | 292 | 95.4 | 100.0 | 73~74 | 1000 | 615 | ok |
| yolo26l.dxnn | 1 | 3 | 57.1 ±0.0 | 57.1 | 185 | 92.9 | 100.0 | 65~69 | 1000 | 372 | ok |
| yolo26l.dxnn | 2 | 3 | 57.1 ±0.0 | 28.6 | 197 | 96.8 | 100.0 | 72~74 | 1000 | 511 | ok |
| yolo26x.dxnn | 1 | 2/3 | 32.8 ±0.0 | 32.8 | 106 | 96.8 | 100.0 | 70~73 | 1000 | 430 | partial |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n.dxnn | 2 | 30.8 | 2 | 39.9 |
| yolo26s.dxnn | 1 | 61.8 | 2 | 39.9 |
| yolo26m.dxnn | 1 | 61.6 | 2 | 37.7 |
| yolo26l.dxnn | 1 | 56.9 | 1 | 57.1 |
| yolo26x.dxnn | 1+ | 32.8 | 1+ | 32.8 |

> **+** 표시: 마지막 측정 스트림에서도 기준 FPS를 만족함. 스위프가 FPS 임계값 미달전에 중단된 경우로, 실제 최대 처리 가능 스트림 수는 더 클 수 있음.

### Pose Estimation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | 2 | 3 | 74.8 ±0.7 | 37.4 | 344 | 31.4 | 60.4 | 50~51 | 1000 | 446 | ok |
| yolo26n-pose.dxnn | 3 | 3 | 74.1 ±0.8 | 24.7 | 344 | 31.2 | 62.7 | 52 | 1000 | 548 | ok |
| yolo26s-pose.dxnn | 2 | 3 | 74.2 ±1.2 | 37.1 | 338 | 57.9 | 84.8 | 59~60 | 1000 | 460 | ok |
| yolo26s-pose.dxnn | 3 | 3 | 74.0 ±0.7 | 24.7 | 338 | 57.9 | 79.4 | 60 | 1000 | 562 | ok |
| yolo26m-pose.dxnn | 2 | 3 | 74.1 ±0.1 | 37.1 | 247 | 95.9 | 100.0 | 72~74 | 1000 | 483 | ok |
| yolo26m-pose.dxnn | 3 | 3 | 73.1 ±0.4 | 24.4 | 272 | 94.9 | 100.0 | 75~76 | 1000 | 585 | ok |
| yolo26l-pose.dxnn | 1 | 3 | 56.0 ±0.0 | 56.0 | 140 | 94.1 | 100.0 | 67~70 | 1000 | 355 | ok |
| yolo26l-pose.dxnn | 2 | 3 | 55.9 ±0.0 | 28.0 | 146 | 95.7 | 100.0 | 61~70 | 1000 | 491 | ok |
| yolo26x-pose.dxnn | 1 | 3 | 32.2 ±0.0 | 32.2 | 81 | 95.2 | 100.0 | 73~78 | 1000 | 417 | ok |
| yolo26x-pose.dxnn | 2 | 3 | 31.6 ±0.4 | 15.8 | 82 | 95.4 | 100.0 | 80~81 | 800~1000 | 554 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | 3 | 3 | 109.0 ±0.6 | 36.3 | 363 | 52.1 | 73.2 | 56 | 1000 | 544 | ok |
| yolo26n-pose.dxnn | 4 | 3 | 109.3 ±0.2 | 27.3 | 363 | 53.3 | 73.9 | 56~57 | 1000 | 646 | ok |
| yolo26s-pose.dxnn | 3 | 3 | 101.3 ±0.0 | 33.8 | 265 | 95.9 | 100.0 | 64~66 | 1000 | 552 | ok |
| yolo26s-pose.dxnn | 4 | 3 | 101.3 ±0.1 | 25.3 | 264 | 96.3 | 100.0 | 67 | 1000 | 658 | ok |
| yolo26m-pose.dxnn | 2 | 3 | 74.6 ±0.0 | 37.3 | 167 | 96.3 | 100.0 | 72~74 | 1000 | 471 | ok |
| yolo26m-pose.dxnn | 3 | 3 | 74.5 ±0.0 | 24.8 | 166 | 97.3 | 100.0 | 63~72 | 1000 | 574 | ok |
| yolo26l-pose.dxnn | 1 | 3 | 56.0 ±0.0 | 56.0 | 112 | 94.1 | 100.0 | 67~70 | 1000 | 344 | ok |
| yolo26l-pose.dxnn | 2 | 3 | 56.0 ±0.0 | 28.0 | 120 | 96.5 | 100.0 | 73~75 | 1000 | 480 | ok |
| yolo26x-pose.dxnn | 1 | 3 | 32.2 ±0.0 | 32.2 | 68 | 95.4 | 100.0 | 73~78 | 1000 | 407 | ok |
| yolo26x-pose.dxnn | 2 | 3 | 31.7 ±0.2 | 15.8 | 70 | 96.1 | 100.0 | 81 | 800~1000 | 543 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-pose.dxnn | 2 | 37.4 | 3 | 36.3 |
| yolo26s-pose.dxnn | 2 | 37.1 | 3 | 33.8 |
| yolo26m-pose.dxnn | 2 | 37.1 | 2 | 37.3 |
| yolo26l-pose.dxnn | 1 | 56.0 | 1 | 56.0 |
| yolo26x-pose.dxnn | 1 | 32.2 | 1 | 32.2 |

### Segmentation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | 1 | 3 | 41.4 ±0.1 | 41.4 | 335 | 18.8 | 42.2 | 49~50 | 1000 | 420 | ok |
| yolo26n-seg.dxnn | 2 | 3 | 40.6 ±0.3 | 20.3 | 339 | 18.9 | 44.3 | 49 | 1000 | 565 | ok |
| yolo26s-seg.dxnn | 1 | 3 | 41.5 ±0.1 | 41.5 | 330 | 34.2 | 62.3 | 49~54 | 1000 | 435 | ok |
| yolo26s-seg.dxnn | 2 | 3 | 40.9 ±0.5 | 20.4 | 335 | 34.3 | 65.4 | 54~55 | 1000 | 578 | ok |
| yolo26m-seg.dxnn | 1 | 3 | 41.3 ±0.2 | 41.3 | 312 | 58.8 | 86.1 | 66~69 | 1000 | 460 | ok |
| yolo26m-seg.dxnn | 2 | 3 | 40.6 ±0.6 | 20.3 | 318 | 58.7 | 82.1 | 70 | 1000 | 608 | ok |
| yolo26l-seg.dxnn | 1 | 3 | 41.2 ±0.0 | 41.2 | 275 | 80.7 | 95.6 | 70~73 | 1000 | 469 | ok |
| yolo26l-seg.dxnn | 2 | 3 | 40.6 ±0.2 | 20.3 | 278 | 79.7 | 96.7 | 73~76 | 1000 | 613 | ok |
| yolo26x-seg.dxnn | 1 | 3 | 25.6 ±0.0 | 25.6 | 111 | 94.8 | 100.0 | 68~79 | 1000 | 535 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | 1 | 3 | 55.0 ±0.3 | 55.0 | 368 | 23.6 | 65.9 | 51 | 1000 | 464 | ok |
| yolo26n-seg.dxnn | 2 | 3 | 55.0 ±0.2 | 27.5 | 363 | 23.7 | 65.8 | 51 | 1000 | 607 | ok |
| yolo26s-seg.dxnn | 1 | 3 | 55.0 ±0.4 | 55.0 | 361 | 46.2 | 75.2 | 58 | 1000 | 479 | ok |
| yolo26s-seg.dxnn | 2 | 3 | 54.5 ±0.1 | 27.3 | 364 | 46.6 | 76.1 | 59 | 1000 | 626 | ok |
| yolo26m-seg.dxnn | 1 | 3 | 52.6 ±0.7 | 52.6 | 317 | 83.5 | 96.3 | 71~74 | 1000 | 498 | ok |
| yolo26m-seg.dxnn | 2 | 3 | 52.5 ±0.5 | 26.3 | 323 | 84.1 | 96.3 | 77~78 | 1000 | 637 | ok |
| yolo26l-seg.dxnn | 1 | 3 | 45.2 ±0.0 | 45.2 | 231 | 94.6 | 100.0 | 72~76 | 1000 | 480 | ok |
| yolo26l-seg.dxnn | 2 | 3 | 44.2 ±0.8 | 22.1 | 225 | 95.0 | 100.0 | 79~81 | 800~1000 | 624 | ok |
| yolo26x-seg.dxnn | 1 | 3 | 24.1 ±1.3 | 24.1 | 108 | 93.6 | 100.0 | 79~81 | 800~1000 | 543 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-seg.dxnn | 1 | 41.4 | 1 | 55.0 |
| yolo26s-seg.dxnn | 1 | 41.5 | 1 | 55.0 |
| yolo26m-seg.dxnn | 1 | 41.3 | 1 | 52.6 |
| yolo26l-seg.dxnn | 1 | 41.2 | 1 | 45.2 |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | 1 | 3 | 59.1 ±0.0 | 59.1 | 243 | 92.3 | 100.0 | 58~60 | 1000 | 343 | ok |
| yolo26n-obb.dxnn | 2 | 3 | 59.1 ±0.0 | 29.6 | 253 | 95.4 | 100.0 | 60~62 | 1000 | 480 | ok |
| yolo26s-obb.dxnn | 1 | 3 | 36.4 ±0.0 | 36.4 | 124 | 94.9 | 100.0 | 61~63 | 1000 | 360 | ok |
| yolo26s-obb.dxnn | 2 | 3 | 36.4 ±0.0 | 18.2 | 131 | 96.7 | 100.0 | 64~65 | 1000 | 496 | ok |
| yolo26m-obb.dxnn | 1 | 3 | 27.3 ±0.0 | 27.3 | 94 | 95.7 | 100.0 | 69~72 | 1000 | 382 | ok |
| yolo26l-obb.dxnn | 1 | 3 | 20.5 ±0.0 | 20.5 | 74 | 96.8 | 100.0 | 61~69 | 1000 | 390 | ok |
| yolo26x-obb.dxnn | 1 | 3 | 11.9 ±0.0 | 11.9 | 46 | 98.0 | 100.0 | 76~80 | 1000 | 461 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | 1 | 3 | 59.2 ±0.0 | 59.2 | 199 | 91.2 | 100.0 | 57~59 | 1000 | 337 | ok |
| yolo26n-obb.dxnn | 2 | 3 | 59.2 ±0.1 | 29.6 | 214 | 95.4 | 100.0 | 60~61 | 1000 | 472 | ok |
| yolo26s-obb.dxnn | 1 | 3 | 36.4 ±0.0 | 36.4 | 122 | 94.9 | 100.0 | 61~63 | 1000 | 355 | ok |
| yolo26s-obb.dxnn | 2 | 3 | 36.4 ±0.0 | 18.2 | 124 | 96.7 | 100.0 | 65~66 | 1000 | 486 | ok |
| yolo26m-obb.dxnn | 1 | 3 | 27.3 ±0.0 | 27.3 | 94 | 95.8 | 100.0 | 63~70 | 1000 | 373 | ok |
| yolo26l-obb.dxnn | 1 | 3 | 20.5 ±0.0 | 20.5 | 74 | 96.6 | 100.0 | 70~74 | 1000 | 386 | ok |
| yolo26x-obb.dxnn | 1 | 3 | 11.9 ±0.0 | 11.9 | 47 | 97.9 | 100.0 | 76~80 | 1000 | 460 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-obb.dxnn | 1 | 59.1 | 1 | 59.2 |
| yolo26s-obb.dxnn | 1 | 36.4 | 1 | 36.4 |

---
*Report generated by dx_stream benchmark tool*
