# YOLO26 Benchmark Report

**Generated:** 2026-07-11 02:39:25 (Local)

## Test Timing

| # | Type | Start | End | Duration |
|---|------|-------|-----|----------|
| 1 | run | 2026-07-01 11:37:56 | 2026-07-01 15:49:17 | 4h 11m 20s |
| 2 | retry-failed | 2026-07-10 09:46:41 | 2026-07-11 02:39:25 | 16h 52m 43s |

## Executive Summary

### Object Detection

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n.dxnn | ON | 59.55 | 136.1 | 120.2 | 4 |
| yolo26n.dxnn | OFF | 34.89 | 138.3 | 100.9 | 3 |
| yolo26s.dxnn | ON | 71.95 | 97.2 | 89.0 | 2 |
| yolo26s.dxnn | OFF | 46.95 | 102.9 | 91.5 | 3 |
| yolo26m.dxnn | ON | 79.53 | 75.5 | 72.7 | 2 |
| yolo26m.dxnn | OFF | 53.60 | 76.4 | 75.8 | 2 |
| yolo26l.dxnn | ON | 90.08 | 57.1 | 53.1 | 1 |
| yolo26l.dxnn | OFF | 63.62 | 57.1 | 57.1 | 1 |
| yolo26x.dxnn | ON | 113.49 | 26.9 | 32.8 | 1 |
| yolo26x.dxnn | OFF | 95.79 | 32.7 | 32.8 | 1 |

### Pose Estimation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-pose.dxnn | ON | 46.13 | 157.6 | 145.4 | 4 |
| yolo26n-pose.dxnn | OFF | 30.44 | 163.1 | 156.8 | 5 |
| yolo26s-pose.dxnn | ON | 54.52 | 102.0 | 100.3 | 3 |
| yolo26s-pose.dxnn | OFF | 38.76 | 102.3 | 95.1 | 3 |
| yolo26m-pose.dxnn | ON | 61.57 | 74.6 | 74.4 | 2 |
| yolo26m-pose.dxnn | OFF | 47.54 | 74.6 | 74.6 | 2 |
| yolo26l-pose.dxnn | ON | 76.00 | 56.0 | 56.0 | 1 |
| yolo26l-pose.dxnn | OFF | 56.50 | 56.0 | 56.0 | 1 |
| yolo26x-pose.dxnn | ON | 103.13 | 32.2 | 32.2 | 1 |
| yolo26x-pose.dxnn | OFF | 87.99 | 26.5 | 32.3 | 1 |

### Segmentation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-seg.dxnn | ON | 74.22 | 110.3 | 90.1 | 3 |
| yolo26n-seg.dxnn | OFF | 50.40 | 104.7 | 86.1 | 2 |
| yolo26s-seg.dxnn | ON | 90.24 | 73.9 | 68.2 | 2 |
| yolo26s-seg.dxnn | OFF | 60.49 | 77.9 | 77.0 | 2 |
| yolo26m-seg.dxnn | ON | 108.17 | 55.8 | 54.5 | 1 |
| yolo26m-seg.dxnn | OFF | 76.74 | 56.0 | 55.9 | 1 |
| yolo26l-seg.dxnn | ON | 112.37 | 45.3 | 44.8 | 1 |
| yolo26l-seg.dxnn | OFF | 88.50 | 45.5 | 45.3 | 1 |
| yolo26x-seg.dxnn | ON | 155.64 | 25.6 | 25.6 | — |
| yolo26x-seg.dxnn | OFF | 137.35 | 25.6 | 25.6 | — |

### Oriented BBox (OBB)

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-obb.dxnn | ON | 69.95 | 59.2 | 59.2 | 1 |
| yolo26n-obb.dxnn | OFF | 50.18 | 59.3 | 59.2 | 1 |
| yolo26s-obb.dxnn | ON | 89.16 | 36.4 | 36.4 | 1 |
| yolo26s-obb.dxnn | OFF | 71.91 | 36.4 | 36.4 | 1 |
| yolo26m-obb.dxnn | ON | 110.97 | 27.3 | 27.3 | — |
| yolo26m-obb.dxnn | OFF | 90.88 | 27.3 | 27.3 | — |
| yolo26l-obb.dxnn | ON | 133.98 | 20.4 | 20.5 | — |
| yolo26l-obb.dxnn | OFF | 112.91 | 20.4 | 16.3 | — |
| yolo26x-obb.dxnn | ON | 209.25 | 11.9 | 11.9 | — |
| yolo26x-obb.dxnn | OFF | 191.54 | 11.9 | 11.9 | — |

### Classification

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-cls.dxnn | ON | 2.51 | 2672.8 | 1056.2 | — |
| yolo26n-cls.dxnn | OFF | 2.47 | 2671.9 | 1055.7 | — |
| yolo26s-cls.dxnn | ON | 3.51 | 1618.4 | 1053.5 | — |
| yolo26s-cls.dxnn | OFF | 3.21 | 1616.3 | 1058.8 | — |
| yolo26m-cls.dxnn | ON | 3.96 | 1274.9 | 1052.1 | — |
| yolo26m-cls.dxnn | OFF | 3.86 | 1274.2 | 1057.6 | — |
| yolo26l-cls.dxnn | ON | 5.55 | 797.4 | 785.0 | — |
| yolo26l-cls.dxnn | OFF | 5.47 | 796.7 | 786.9 | — |
| yolo26x-cls.dxnn | ON | 8.43 | 401.6 | 397.4 | — |
| yolo26x-cls.dxnn | OFF | 8.61 | 401.5 | 397.6 | — |

## Environment

| Item | Value |
|------|-------|
| Hostname | orangepi5plus |
| OS | Debian GNU/Linux 12 (bookworm) |
| Kernel | 6.1.43-rockchip-rk3588 |
| CPU | Cortex-A55 |
| CPU Cores | 8 |
| RAM | 15.6 GB |
| NPU SKU | M1 |
| NPU RT | v3.2.0 |
| NPU Driver (RT) | v2.1.0 |
| NPU Driver (PCIe) | v2.0.1 |
| NPU Firmware | v2.5.0 |
| NPU Memory | LPDDR5 5600 Mbps, 3.92GiB |
| NPU Board | M.2, Rev 1.0 |
| NPU PCIe | Gen3 X4 [01:00:00] |

### Tools

| Tool | Available | Version |
|------|-----------|---------|
| run_model | Yes | DXRT v3.2.0 run_model |
| gst-launch-1.0 | Yes | gst-launch-1.0 version 1.22.0 |
| gst-inspect-1.0 | Yes | gst-inspect-1.0 version 1.22.0 |
| dxtop | Yes | DX-TOP 1.0.1 |
| ffprobe | Yes | ffprobe version 5.1.3-4 Copyright (c) 2007-2022 the FFmpeg d... |

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
| yolo26n.dxnn | 136.1 ±1.3 | 215 | 61.9 | 82.4 | 48~51 | 1000 | ok |
| yolo26s.dxnn | 97.2 ±0.9 | 184 | 80.3 | 96.1 | 54~56 | 1000 | ok |
| yolo26m.dxnn | 75.5 ±0.1 | 166 | 87.7 | 100.0 | 58~62 | 1000 | ok |
| yolo26l.dxnn | 57.1 ±0.0 | 152 | 92.0 | 100.0 | 59~61 | 1000 | ok |
| yolo26x.dxnn | 26.9 ±10.0 | 97 | 69.1 | 100.0 | 56~58 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n.dxnn | 138.3 ±3.1 | 175 | 66.8 | 87.1 | 52~53 | 1000 | ok |
| yolo26s.dxnn | 102.9 ±0.5 | 139 | 88.3 | 100.0 | 56~58 | 1000 | ok |
| yolo26m.dxnn | 76.4 ±0.1 | 123 | 88.5 | 100.0 | 60~63 | 1000 | ok |
| yolo26l.dxnn | 57.1 ±0.0 | 105 | 92.8 | 100.0 | 50~54 | 1000 | ok |
| yolo26x.dxnn | 32.7 ±0.0 | 70 | 89.9 | 100.0 | 58~61 | 1000 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-pose.dxnn | 157.6 ±0.3 | 196 | 83.9 | 97.1 | 56~58 | 1000 | ok |
| yolo26s-pose.dxnn | 102.0 ±0.1 | 168 | 90.5 | 100.0 | 56~58 | 1000 | ok |
| yolo26m-pose.dxnn | 74.6 ±0.0 | 135 | 90.6 | 100.0 | 59~62 | 1000 | ok |
| yolo26l-pose.dxnn | 56.0 ±0.0 | 114 | 89.2 | 100.0 | 60~62 | 1000 | ok |
| yolo26x-pose.dxnn | 32.2 ±0.0 | 84 | 88.4 | 100.0 | 61~63 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-pose.dxnn | 163.1 ±0.2 | 148 | 90.1 | 100.0 | 56~58 | 1000 | ok |
| yolo26s-pose.dxnn | 102.3 ±0.0 | 119 | 89.5 | 100.0 | 57~59 | 1000 | ok |
| yolo26m-pose.dxnn | 74.6 ±0.0 | 110 | 89.2 | 100.0 | 60~63 | 1000 | ok |
| yolo26l-pose.dxnn | 56.0 ±0.0 | 82 | 89.0 | 100.0 | 60~63 | 1000 | ok |
| yolo26x-pose.dxnn | 26.5 ±9.9 | 41 | 69.8 | 100.0 | 59~62 | 1000 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-seg.dxnn | 110.3 ±0.9 | 283 | 56.0 | 83.5 | 56~58 | 1000 | ok |
| yolo26s-seg.dxnn | 73.9 ±0.7 | 212 | 71.5 | 91.0 | 56~59 | 1000 | ok |
| yolo26m-seg.dxnn | 55.8 ±0.0 | 168 | 89.0 | 100.0 | 61~65 | 1000 | ok |
| yolo26l-seg.dxnn | 45.3 ±0.0 | 147 | 89.9 | 100.0 | 61~65 | 1000 | ok |
| yolo26x-seg.dxnn | 25.6 ±0.0 | 103 | 87.5 | 100.0 | 62~66 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-seg.dxnn | 104.7 ±0.1 | 200 | 56.6 | 78.5 | 56~58 | 1000 | ok |
| yolo26s-seg.dxnn | 77.9 ±0.3 | 173 | 77.8 | 94.2 | 58~60 | 1000 | ok |
| yolo26m-seg.dxnn | 56.0 ±0.0 | 137 | 89.3 | 100.0 | 63~66 | 1000 | ok |
| yolo26l-seg.dxnn | 45.5 ±0.0 | 116 | 89.3 | 100.0 | 62~65 | 1000 | ok |
| yolo26x-seg.dxnn | 25.6 ±0.0 | 79 | 88.4 | 100.0 | 63~66 | 1000 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-obb.dxnn | 59.2 ±0.1 | 131 | 90.9 | 100.0 | 57~58 | 1000 | ok |
| yolo26s-obb.dxnn | 36.4 ±0.0 | 101 | 89.0 | 100.0 | 56~58 | 1000 | ok |
| yolo26m-obb.dxnn | 27.3 ±0.0 | 85 | 88.8 | 100.0 | 58~61 | 1000 | ok |
| yolo26l-obb.dxnn | 20.4 ±0.0 | 73 | 88.3 | 100.0 | 60~62 | 1000 | ok |
| yolo26x-obb.dxnn | 11.9 ±0.0 | 48 | 90.9 | 100.0 | 61~62 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-obb.dxnn | 59.3 ±0.0 | 91 | 91.6 | 100.0 | 56~57 | 1000 | ok |
| yolo26s-obb.dxnn | 36.4 ±0.0 | 65 | 92.4 | 100.0 | 56~58 | 1000 | ok |
| yolo26m-obb.dxnn | 27.3 ±0.0 | 51 | 91.0 | 100.0 | 59~62 | 1000 | ok |
| yolo26l-obb.dxnn | 20.4 ±0.0 | 42 | 90.8 | 100.0 | 60~62 | 1000 | ok |
| yolo26x-obb.dxnn | 11.9 ±0.0 | 26 | 89.5 | 100.0 | 54~58 | 1000 | ok |

#### Classification

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-cls.dxnn | 2672.8 ±2.0 | 120 | 90.8 | 97.6 | 53~54 | 1000 | ok |
| yolo26s-cls.dxnn | 1618.4 ±2.3 | 85 | 90.5 | 99.0 | 54~56 | 1000 | ok |
| yolo26m-cls.dxnn | 1274.9 ±1.9 | 75 | 88.9 | 99.2 | 58~61 | 1000 | ok |
| yolo26l-cls.dxnn | 797.4 ±0.3 | 65 | 91.3 | 99.5 | 59~60 | 1000 | ok |
| yolo26x-cls.dxnn | 401.6 ±0.1 | 38 | 89.2 | 100.0 | 60~62 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-cls.dxnn | 2671.9 ±1.7 | 120 | 88.8 | 97.7 | 54 | 1000 | ok |
| yolo26s-cls.dxnn | 1616.3 ±0.5 | 86 | 89.9 | 99.1 | 55~56 | 1000 | ok |
| yolo26m-cls.dxnn | 1274.2 ±4.8 | 75 | 89.0 | 98.8 | 60~62 | 1000 | ok |
| yolo26l-cls.dxnn | 796.7 ±0.5 | 64 | 91.6 | 99.5 | 59~60 | 1000 | ok |
| yolo26x-cls.dxnn | 401.5 ±0.2 | 37 | 92.0 | 100.0 | 60~62 | 1000 | ok |

### Latency (Single-Core, Sync)

#### Object Detection

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n.dxnn | 16.8 | 59.55 | 40.90 | 18.65 | 44 | ok |
| yolo26s.dxnn | 13.9 | 71.95 | 54.24 | 17.70 | 49 | ok |
| yolo26m.dxnn | 12.6 | 79.53 | 53.58 | 25.95 | 52 | ok |
| yolo26l.dxnn | 11.1 | 90.08 | 64.81 | 25.27 | 54 | ok |
| yolo26x.dxnn | 8.8 | 113.49 | 97.60 | 15.89 | 50 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n.dxnn | 28.7 | 34.89 | 34.89 | 48 | ok |
| yolo26s.dxnn | 21.3 | 46.95 | 46.95 | 51 | ok |
| yolo26m.dxnn | 18.7 | 53.60 | 53.60 | 55 | ok |
| yolo26l.dxnn | 15.7 | 63.62 | 63.62 | 43 | ok |
| yolo26x.dxnn | 10.4 | 95.79 | 95.79 | 52 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-pose.dxnn | 21.7 | 46.13 | 32.29 | 13.84 | 53 | ok |
| yolo26s-pose.dxnn | 18.3 | 54.52 | 44.86 | 9.66 | 52 | ok |
| yolo26m-pose.dxnn | 16.2 | 61.57 | 52.55 | 9.02 | 53 | ok |
| yolo26l-pose.dxnn | 13.2 | 76.00 | 65.03 | 10.97 | 55 | ok |
| yolo26x-pose.dxnn | 9.7 | 103.13 | 90.46 | 12.67 | 55 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-pose.dxnn | 32.9 | 30.44 | 30.44 | 52 | ok |
| yolo26s-pose.dxnn | 25.8 | 38.76 | 38.76 | 53 | ok |
| yolo26m-pose.dxnn | 21.0 | 47.54 | 47.54 | 55 | ok |
| yolo26l-pose.dxnn | 17.7 | 56.50 | 56.50 | 55 | ok |
| yolo26x-pose.dxnn | 11.4 | 87.99 | 87.99 | 56 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-seg.dxnn | 13.5 | 74.22 | 53.90 | 20.32 | 53 | ok |
| yolo26s-seg.dxnn | 11.1 | 90.24 | 72.86 | 17.38 | 52 | ok |
| yolo26m-seg.dxnn | 9.2 | 108.17 | 88.61 | 19.55 | 54 | ok |
| yolo26l-seg.dxnn | 8.9 | 112.37 | 93.00 | 19.37 | 54 | ok |
| yolo26x-seg.dxnn | 6.4 | 155.64 | 136.33 | 19.30 | 55 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-seg.dxnn | 19.8 | 50.40 | 50.40 | 53 | ok |
| yolo26s-seg.dxnn | 16.5 | 60.49 | 60.49 | 53 | ok |
| yolo26m-seg.dxnn | 13.0 | 76.74 | 76.74 | 55 | ok |
| yolo26l-seg.dxnn | 11.3 | 88.50 | 88.50 | 55 | ok |
| yolo26x-seg.dxnn | 7.3 | 137.35 | 137.35 | 55 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-obb.dxnn | 14.3 | 69.95 | 55.91 | 14.05 | 54 | ok |
| yolo26s-obb.dxnn | 11.2 | 89.16 | 77.24 | 11.92 | 52 | ok |
| yolo26m-obb.dxnn | 9.0 | 110.97 | 96.88 | 14.09 | 53 | ok |
| yolo26l-obb.dxnn | 7.5 | 133.98 | 120.70 | 13.29 | 55 | ok |
| yolo26x-obb.dxnn | 4.8 | 209.25 | 191.24 | 18.02 | 56 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-obb.dxnn | 19.9 | 50.18 | 50.18 | 53 | ok |
| yolo26s-obb.dxnn | 13.9 | 71.91 | 71.91 | 53 | ok |
| yolo26m-obb.dxnn | 11.0 | 90.88 | 90.88 | 55 | ok |
| yolo26l-obb.dxnn | 8.9 | 112.91 | 112.91 | 55 | ok |
| yolo26x-obb.dxnn | 5.2 | 191.54 | 191.54 | 48 | ok |

#### Classification

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-cls.dxnn | 398.5 | 2.51 | 2.51 | N/A | 51 | ok |
| yolo26s-cls.dxnn | 284.9 | 3.51 | 3.51 | N/A | 51 | ok |
| yolo26m-cls.dxnn | 252.6 | 3.96 | 3.96 | N/A | 53 | ok |
| yolo26l-cls.dxnn | 180.1 | 5.55 | 5.55 | N/A | 55 | ok |
| yolo26x-cls.dxnn | 118.6 | 8.43 | 8.43 | N/A | 55 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-cls.dxnn | 404.1 | 2.47 | 2.47 | 51 | ok |
| yolo26s-cls.dxnn | 311.6 | 3.21 | 3.21 | 52 | ok |
| yolo26m-cls.dxnn | 259.1 | 3.86 | 3.86 | 55 | ok |
| yolo26l-cls.dxnn | 182.7 | 5.47 | 5.47 | 55 | ok |
| yolo26x-cls.dxnn | 116.2 | 8.61 | 8.61 | 55 | ok |

## E2E Pipeline (Single-Stream)

### Object Detection

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | mppvideodec | 3455 | 3 | 120.2 ±1.1 | 28.74 | 236 | 54.8 | 74.8 | 42~45 | 1000 | 187 | ok |
| yolo26s.dxnn | mppvideodec | 3455 | 3 | 89.0 ±0.7 | 38.84 | 200 | 73.0 | 90.3 | 52~55 | 1000 | 201 | ok |
| yolo26m.dxnn | mppvideodec | 3455 | 3 | 72.7 ±0.2 | 47.50 | 184 | 86.8 | 100.0 | 56~61 | 1000 | 222 | ok |
| yolo26l.dxnn | mppvideodec | 3455 | 3 | 53.1 ±5.2 | 65.11 | 162 | 83.6 | 100.0 | 57~61 | 1000 | 232 | ok |
| yolo26x.dxnn | mppvideodec | 3455 | 3 | 32.8 ±0.0 | 105.42 | 126 | 96.5 | 100.0 | 63~69 | 1000 | 351 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | mppvideodec | 3455 | 3 | 100.9 ±0.3 | 34.25 | 223 | 35.6 | 59.0 | 49~51 | 1000 | 201 | ok |
| yolo26s.dxnn | mppvideodec | 3455 | 3 | 91.5 ±0.5 | 37.74 | 231 | 72.2 | 87.0 | 51~54 | 1000 | 214 | ok |
| yolo26m.dxnn | mppvideodec | 3455 | 3 | 75.8 ±0.0 | 45.57 | 219 | 92.1 | 100.0 | 56~61 | 1000 | 232 | ok |
| yolo26l.dxnn | mppvideodec | 3455 | 2/3 | 57.1 ±0.0 | 60.48 | 188 | 93.8 | 100.0 | 60~63 | 1000 | 238 | partial |
| yolo26x.dxnn | mppvideodec | 3455 | 3 | 32.8 ±0.0 | 105.37 | 144 | 96.4 | 100.0 | 63~71 | 1000 | 350 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n.dxnn | 120.2 | 100.9 | +19.3 | +19.2% |
| yolo26s.dxnn | 89.0 | 91.5 | -2.6 | -2.8% |
| yolo26m.dxnn | 72.7 | 75.8 | -3.1 | -4.1% |
| yolo26l.dxnn | 53.1 | 57.1 | -4.1 | -7.1% |
| yolo26x.dxnn | 32.8 | 32.8 | -0.0 | -0.1% |

### Pose Estimation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | mppvideodec | 3455 | 3 | 145.4 ±0.5 | 23.75 | 227 | 75.1 | 92.9 | 50~52 | 1000 | 175 | ok |
| yolo26s-pose.dxnn | mppvideodec | 3455 | 3 | 100.3 ±0.1 | 34.45 | 186 | 88.2 | 100.0 | 52~55 | 1000 | 191 | ok |
| yolo26m-pose.dxnn | mppvideodec | 3455 | 3 | 74.4 ±0.1 | 46.42 | 157 | 92.9 | 100.0 | 56~61 | 1000 | 212 | ok |
| yolo26l-pose.dxnn | mppvideodec | 3455 | 3 | 56.0 ±0.0 | 61.74 | 131 | 93.7 | 100.0 | 58~64 | 1000 | 222 | ok |
| yolo26x-pose.dxnn | mppvideodec | 3455 | 3 | 32.2 ±0.0 | 107.15 | 103 | 95.3 | 100.0 | 64~70 | 1000 | 362 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | mppvideodec | 3455 | 3 | 156.8 ±0.6 | 22.04 | 189 | 83.4 | 98.2 | 50~52 | 1000 | 167 | ok |
| yolo26s-pose.dxnn | mppvideodec | 3455 | 3 | 95.1 ±10.0 | 36.32 | 152 | 82.3 | 100.0 | 52~54 | 1000 | 180 | ok |
| yolo26m-pose.dxnn | mppvideodec | 3455 | 3 | 74.6 ±0.0 | 46.31 | 124 | 93.5 | 100.0 | 56~61 | 1000 | 200 | ok |
| yolo26l-pose.dxnn | mppvideodec | 3455 | 3 | 56.0 ±0.0 | 61.73 | 118 | 94.3 | 100.0 | 57~63 | 1000 | 211 | ok |
| yolo26x-pose.dxnn | mppvideodec | 3455 | 3 | 32.3 ±0.0 | 107.08 | 75 | 95.6 | 100.0 | 64~72 | 1000 | 362 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-pose.dxnn | 145.4 | 156.8 | -11.3 | -7.2% |
| yolo26s-pose.dxnn | 100.3 | 95.1 | +5.2 | +5.4% |
| yolo26m-pose.dxnn | 74.4 | 74.6 | -0.2 | -0.2% |
| yolo26l-pose.dxnn | 56.0 | 56.0 | -0.0 | -0.0% |
| yolo26x-pose.dxnn | 32.2 | 32.3 | -0.0 | -0.0% |

### Segmentation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | mppvideodec | 3455 | 3 | 90.1 ±0.4 | 38.36 | 321 | 47.1 | 71.7 | 51~54 | 1000 | 287 | ok |
| yolo26s-seg.dxnn | mppvideodec | 3455 | 3 | 68.2 ±0.4 | 50.63 | 261 | 67.9 | 87.3 | 54~59 | 1000 | 307 | ok |
| yolo26m-seg.dxnn | mppvideodec | 3455 | 3 | 54.5 ±0.1 | 63.37 | 228 | 89.4 | 100.0 | 61~69 | 1000 | 326 | ok |
| yolo26l-seg.dxnn | mppvideodec | 3455 | 3 | 44.8 ±0.1 | 77.16 | 194 | 93.1 | 100.0 | 63~70 | 1000 | 334 | ok |
| yolo26x-seg.dxnn | mppvideodec | 3455 | 3 | 25.6 ±0.1 | 134.92 | 134 | 94.6 | 100.0 | 70~79 | 800~1000 | 401 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | mppvideodec | 3455 | 3 | 86.1 ±0.0 | 40.15 | 294 | 38.0 | 63.3 | 51~54 | 1000 | 313 | ok |
| yolo26s-seg.dxnn | mppvideodec | 3455 | 3 | 77.0 ±0.4 | 44.87 | 278 | 79.7 | 95.8 | 54~59 | 1000 | 322 | ok |
| yolo26m-seg.dxnn | mppvideodec | 3455 | 3 | 55.9 ±0.1 | 61.87 | 226 | 92.9 | 100.0 | 61~69 | 1000 | 341 | ok |
| yolo26l-seg.dxnn | mppvideodec | 3455 | 3 | 45.3 ±0.0 | 76.22 | 198 | 94.5 | 100.0 | 63~71 | 1000 | 351 | ok |
| yolo26x-seg.dxnn | mppvideodec | 3455 | 3 | 25.6 ±0.1 | 134.97 | 142 | 94.7 | 100.0 | 71~79 | 800~1000 | 412 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-seg.dxnn | 90.1 | 86.1 | +4.0 | +4.7% |
| yolo26s-seg.dxnn | 68.2 | 77.0 | -8.8 | -11.4% |
| yolo26m-seg.dxnn | 54.5 | 55.9 | -1.3 | -2.4% |
| yolo26l-seg.dxnn | 44.8 | 45.3 | -0.5 | -1.2% |
| yolo26x-seg.dxnn | 25.6 | 25.6 | +0.0 | +0.0% |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | mppvideodec | 2640 | 3 | 59.2 ±0.0 | 44.59 | 158 | 92.3 | 100.0 | 52~55 | 1000 | 212 | ok |
| yolo26s-obb.dxnn | mppvideodec | 2640 | 3 | 36.4 ±0.0 | 72.61 | 128 | 95.5 | 100.0 | 55~60 | 1000 | 228 | ok |
| yolo26m-obb.dxnn | mppvideodec | 2640 | 3 | 27.3 ±0.0 | 96.73 | 107 | 95.6 | 100.0 | 61~68 | 1000 | 250 | ok |
| yolo26l-obb.dxnn | mppvideodec | 2640 | 3 | 20.5 ±0.0 | 128.85 | 88 | 95.4 | 100.0 | 63~69 | 1000 | 264 | ok |
| yolo26x-obb.dxnn | mppvideodec | 2640 | 3 | 11.9 ±0.0 | 221.44 | 62 | 97.9 | 100.0 | 70~76 | 1000 | 374 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | mppvideodec | 2640 | 3 | 59.2 ±0.0 | 44.57 | 167 | 93.8 | 100.0 | 52~55 | 1000 | 208 | ok |
| yolo26s-obb.dxnn | mppvideodec | 2640 | 3 | 36.4 ±0.0 | 72.63 | 136 | 95.4 | 100.0 | 55~59 | 1000 | 223 | ok |
| yolo26m-obb.dxnn | mppvideodec | 2640 | 3 | 27.3 ±0.0 | 96.67 | 111 | 96.0 | 100.0 | 61~67 | 1000 | 242 | ok |
| yolo26l-obb.dxnn | mppvideodec | 2640 | 3 | 16.3 ±5.1 | 161.86 | 85 | 74.2 | 100.0 | 61~67 | 1000 | 254 | ok |
| yolo26x-obb.dxnn | mppvideodec | 2640 | 3 | 11.9 ±0.0 | 221.50 | 63 | 98.0 | 100.0 | 70~74 | 1000 | 374 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-obb.dxnn | 59.2 | 59.2 | -0.0 | -0.1% |
| yolo26s-obb.dxnn | 36.4 | 36.4 | +0.0 | +0.0% |
| yolo26m-obb.dxnn | 27.3 | 27.3 | -0.0 | -0.1% |
| yolo26l-obb.dxnn | 20.5 | 16.3 | +4.2 | +25.6% |
| yolo26x-obb.dxnn | 11.9 | 11.9 | +0.0 | +0.0% |

### Classification

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-cls.dxnn | mppvideodec | 3455 | 3 | 1056.2 ±6.0 | 3.27 | 183 | 16.3 | 57.7 | 47 | 1000 | 86 | ok |
| yolo26s-cls.dxnn | mppvideodec | 3455 | 3 | 1053.5 ±8.3 | 3.28 | 182 | 33.5 | 72.6 | 47 | 1000 | 100 | ok |
| yolo26m-cls.dxnn | mppvideodec | 3455 | 3 | 1052.1 ±1.0 | 3.28 | 180 | 39.7 | 88.0 | 47~48 | 1000 | 124 | ok |
| yolo26l-cls.dxnn | mppvideodec | 3455 | 3 | 785.0 ±2.5 | 4.40 | 155 | 60.3 | 99.4 | 49 | 1000 | 137 | ok |
| yolo26x-cls.dxnn | mppvideodec | 3455 | 3 | 397.4 ±0.9 | 8.70 | 118 | 72.9 | 99.8 | 50~51 | 1000 | 213 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-cls.dxnn | mppvideodec | 3455 | 3 | 1055.7 ±5.0 | 3.27 | 182 | 15.6 | 58.5 | 46 | 1000 | 86 | ok |
| yolo26s-cls.dxnn | mppvideodec | 3455 | 3 | 1058.8 ±4.4 | 3.26 | 181 | 28.5 | 72.2 | 47 | 1000 | 100 | ok |
| yolo26m-cls.dxnn | mppvideodec | 3455 | 3 | 1057.6 ±3.4 | 3.27 | 180 | 44.3 | 88.6 | 48 | 1000 | 124 | ok |
| yolo26l-cls.dxnn | mppvideodec | 3455 | 3 | 786.9 ±3.0 | 4.39 | 153 | 60.9 | 99.4 | 48~49 | 1000 | 137 | ok |
| yolo26x-cls.dxnn | mppvideodec | 3455 | 3 | 397.6 ±0.6 | 8.69 | 118 | 76.9 | 100.0 | 50~51 | 1000 | 213 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-cls.dxnn | 1056.2 | 1055.7 | +0.5 | +0.0% |
| yolo26s-cls.dxnn | 1053.5 | 1058.8 | -5.4 | -0.5% |
| yolo26m-cls.dxnn | 1052.1 | 1057.6 | -5.4 | -0.5% |
| yolo26l-cls.dxnn | 785.0 | 786.9 | -1.9 | -0.2% |
| yolo26x-cls.dxnn | 397.4 | 397.6 | -0.3 | -0.1% |

## E2E Pipeline (Multi-Stream)

### Object Detection

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | 4 | 3 | 120.3 ±0.2 | 30.1 | 239 | 59.3 | 77.7 | 54~59 | 1000 | 210 | ok |
| yolo26n.dxnn | 5 | 3 | 120.2 ±1.1 | 24.0 | 241 | 59.4 | 79.5 | 62~63 | 1000 | 214 | ok |
| yolo26s.dxnn | 2 | 3 | 88.8 ±0.5 | 44.4 | 204 | 75.8 | 91.3 | 59~62 | 1000 | 212 | ok |
| yolo26s.dxnn | 3 | 3 | 88.6 ±0.3 | 29.5 | 203 | 76.4 | 92.8 | 64~65 | 1000 | 218 | ok |
| yolo26m.dxnn | 2 | 3 | 72.6 ±0.3 | 36.3 | 186 | 89.9 | 100.0 | 67~71 | 1000 | 234 | ok |
| yolo26m.dxnn | 3 | 3 | 72.5 ±0.2 | 24.2 | 187 | 90.0 | 100.0 | 73~75 | 1000 | 239 | ok |
| yolo26l.dxnn | 1 | 3 | 53.1 ±5.2 | 53.1 | 162 | 83.6 | 100.0 | 57~61 | 1000 | 232 | ok |
| yolo26l.dxnn | 2 | 3 | 56.5 ±0.1 | 28.2 | 170 | 95.3 | 100.0 | 68~72 | 1000 | 243 | ok |
| yolo26x.dxnn | 1 | 3 | 32.8 ±0.0 | 32.8 | 126 | 96.5 | 100.0 | 63~69 | 1000 | 351 | ok |
| yolo26x.dxnn | 2 | 3 | 32.8 ±0.0 | 16.4 | 127 | 98.0 | 100.0 | 75~78 | 1000 | 351 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | 3 | 3 | 97.3 ±1.0 | 32.4 | 236 | 35.5 | 81.8 | 54~56 | 1000 | 224 | ok |
| yolo26n.dxnn | 4 | 3 | 98.4 ±0.3 | 24.6 | 232 | 36.2 | 75.3 | 57~58 | 1000 | 233 | ok |
| yolo26s.dxnn | 3 | 3 | 92.3 ±0.7 | 30.8 | 234 | 75.8 | 96.6 | 60~64 | 1000 | 238 | ok |
| yolo26s.dxnn | 4 | 3 | 93.2 ±0.5 | 23.3 | 233 | 77.9 | 95.5 | 65~67 | 1000 | 246 | ok |
| yolo26m.dxnn | 2 | 3 | 76.0 ±0.1 | 38.0 | 221 | 95.0 | 100.0 | 68~72 | 1000 | 245 | ok |
| yolo26m.dxnn | 3 | 3 | 76.0 ±0.0 | 25.3 | 222 | 95.8 | 100.0 | 75~77 | 1000 | 255 | ok |
| yolo26l.dxnn | 1 | 2/3 | 57.1 ±0.0 | 57.1 | 188 | 93.8 | 100.0 | 60~63 | 1000 | 238 | partial |
| yolo26x.dxnn | 1 | 3 | 32.8 ±0.0 | 32.8 | 144 | 96.4 | 100.0 | 63~71 | 1000 | 350 | ok |
| yolo26x.dxnn | 2 | 3 | 32.9 ±0.0 | 16.4 | 146 | 98.0 | 100.0 | 76~78 | 1000 | 351 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n.dxnn | 4 | 30.1 | 3 | 32.4 |
| yolo26s.dxnn | 2 | 44.4 | 3 | 30.8 |
| yolo26m.dxnn | 2 | 36.3 | 2 | 38.0 |
| yolo26l.dxnn | 1 | 53.1 | 1+ | 57.1 |
| yolo26x.dxnn | 1 | 32.8 | 1 | 32.8 |

> **+** 표시: 마지막 측정 스트림에서도 기준 FPS를 만족함. 스위프가 FPS 임계값 미달전에 중단된 경우로, 실제 최대 처리 가능 스트림 수는 더 클 수 있음.

### Pose Estimation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | 4 | 3 | 144.9 ±0.7 | 36.2 | 229 | 80.1 | 93.1 | 58~62 | 1000 | 204 | ok |
| yolo26n-pose.dxnn | 5 | 3 | 145.8 ±1.1 | 29.2 | 230 | 81.6 | 92.1 | 63~65 | 1000 | 209 | ok |
| yolo26s-pose.dxnn | 3 | 3 | 100.2 ±0.1 | 33.4 | 187 | 94.3 | 100.0 | 61~65 | 1000 | 211 | ok |
| yolo26s-pose.dxnn | 4 | 3 | 99.9 ±0.1 | 25.0 | 187 | 94.0 | 100.0 | 67~68 | 1000 | 219 | ok |
| yolo26m-pose.dxnn | 2 | 3 | 74.5 ±0.0 | 37.2 | 160 | 96.5 | 100.0 | 67~72 | 1000 | 225 | ok |
| yolo26m-pose.dxnn | 3 | 3 | 74.5 ±0.0 | 24.8 | 162 | 97.0 | 100.0 | 74~75 | 1000 | 234 | ok |
| yolo26l-pose.dxnn | 1 | 3 | 56.0 ±0.0 | 56.0 | 131 | 93.7 | 100.0 | 58~64 | 1000 | 222 | ok |
| yolo26l-pose.dxnn | 2 | 3 | 56.0 ±0.0 | 28.0 | 132 | 96.4 | 100.0 | 69~72 | 1000 | 236 | ok |
| yolo26x-pose.dxnn | 1 | 3 | 32.2 ±0.0 | 32.2 | 103 | 95.3 | 100.0 | 64~70 | 1000 | 362 | ok |
| yolo26x-pose.dxnn | 2 | 3 | 32.3 ±0.0 | 16.1 | 105 | 96.9 | 100.0 | 75~77 | 1000 | 362 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | 5 | 3 | 156.4 ±0.5 | 31.3 | 194 | 90.3 | 98.3 | 59~63 | 1000 | 206 | ok |
| yolo26n-pose.dxnn | 6 | 3 | 156.8 ±0.0 | 26.1 | 194 | 90.9 | 98.2 | 65~66 | 1000 | 212 | ok |
| yolo26s-pose.dxnn | 3 | 3 | 102.0 ±0.1 | 34.0 | 160 | 96.2 | 100.0 | 61~64 | 1000 | 200 | ok |
| yolo26s-pose.dxnn | 4 | 3 | 102.1 ±0.1 | 25.5 | 159 | 96.9 | 100.0 | 66~67 | 1000 | 213 | ok |
| yolo26m-pose.dxnn | 2 | 3 | 74.7 ±0.0 | 37.4 | 129 | 96.7 | 100.0 | 67~71 | 1000 | 213 | ok |
| yolo26m-pose.dxnn | 3 | 3 | 74.8 ±0.0 | 24.9 | 126 | 97.5 | 100.0 | 74~75 | 1000 | 222 | ok |
| yolo26l-pose.dxnn | 1 | 3 | 56.0 ±0.0 | 56.0 | 118 | 94.3 | 100.0 | 57~63 | 1000 | 211 | ok |
| yolo26l-pose.dxnn | 2 | 3 | 56.1 ±0.0 | 28.0 | 119 | 96.4 | 100.0 | 69~73 | 1000 | 223 | ok |
| yolo26x-pose.dxnn | 1 | 3 | 32.3 ±0.0 | 32.3 | 75 | 95.6 | 100.0 | 64~72 | 1000 | 362 | ok |
| yolo26x-pose.dxnn | 2 | 3 | 32.3 ±0.0 | 16.1 | 74 | 96.9 | 100.0 | 77~79 | 1000 | 362 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-pose.dxnn | 4 | 36.2 | 5 | 31.3 |
| yolo26s-pose.dxnn | 3 | 33.4 | 3 | 34.0 |
| yolo26m-pose.dxnn | 2 | 37.2 | 2 | 37.4 |
| yolo26l-pose.dxnn | 1 | 56.0 | 1 | 56.0 |
| yolo26x-pose.dxnn | 1 | 32.2 | 1 | 32.3 |

### Segmentation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | 3 | 3 | 91.1 ±0.7 | 30.4 | 334 | 49.8 | 77.9 | 60~65 | 1000 | 318 | ok |
| yolo26n-seg.dxnn | 4 | 3 | 90.5 ±0.3 | 22.6 | 328 | 49.9 | 74.5 | 66~68 | 1000 | 329 | ok |
| yolo26s-seg.dxnn | 2 | 3 | 67.9 ±0.7 | 34.0 | 257 | 69.1 | 92.2 | 64~68 | 1000 | 323 | ok |
| yolo26s-seg.dxnn | 3 | 3 | 67.8 ±0.2 | 22.6 | 261 | 69.8 | 87.8 | 70~72 | 1000 | 337 | ok |
| yolo26m-seg.dxnn | 1 | 3 | 54.5 ±0.1 | 54.5 | 228 | 89.4 | 100.0 | 61~69 | 1000 | 326 | ok |
| yolo26m-seg.dxnn | 2 | 3 | 53.2 ±1.7 | 26.6 | 219 | 91.5 | 100.0 | 78~81 | 800~1000 | 349 | ok |
| yolo26l-seg.dxnn | 1 | 3 | 44.8 ±0.1 | 44.8 | 194 | 93.1 | 100.0 | 63~70 | 1000 | 334 | ok |
| yolo26l-seg.dxnn | 2 | 3 | 43.7 ±1.5 | 21.9 | 196 | 95.6 | 100.0 | 78~81 | 800~1000 | 355 | ok |
| yolo26x-seg.dxnn | 1 | 3 | 25.6 ±0.1 | 25.6 | 134 | 94.6 | 100.0 | 70~79 | 800~1000 | 401 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | 2 | 3 | 86.0 ±0.2 | 43.0 | 296 | 39.3 | 65.5 | 57~60 | 1000 | 337 | ok |
| yolo26n-seg.dxnn | 3 | 3 | 86.0 ±0.2 | 28.7 | 290 | 39.7 | 67.8 | 63~64 | 1000 | 351 | ok |
| yolo26s-seg.dxnn | 2 | 3 | 76.8 ±0.5 | 38.4 | 280 | 81.8 | 95.2 | 65~69 | 1000 | 345 | ok |
| yolo26s-seg.dxnn | 3 | 3 | 76.8 ±0.7 | 25.6 | 280 | 82.1 | 94.8 | 73~75 | 1000 | 366 | ok |
| yolo26m-seg.dxnn | 1 | 3 | 55.9 ±0.1 | 55.9 | 226 | 92.9 | 100.0 | 61~69 | 1000 | 341 | ok |
| yolo26m-seg.dxnn | 2 | 3 | 53.9 ±2.0 | 26.9 | 227 | 95.3 | 100.0 | 78~81 | 800~1000 | 363 | ok |
| yolo26l-seg.dxnn | 1 | 3 | 45.3 ±0.0 | 45.3 | 198 | 94.5 | 100.0 | 63~71 | 1000 | 351 | ok |
| yolo26l-seg.dxnn | 2 | 3 | 43.7 ±1.7 | 21.9 | 189 | 96.4 | 100.0 | 78~81 | 800~1000 | 381 | ok |
| yolo26x-seg.dxnn | 1 | 3 | 25.6 ±0.1 | 25.6 | 142 | 94.7 | 100.0 | 71~79 | 800~1000 | 412 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-seg.dxnn | 3 | 30.4 | 2 | 43.0 |
| yolo26s-seg.dxnn | 2 | 34.0 | 2 | 38.4 |
| yolo26m-seg.dxnn | 1 | 54.5 | 1 | 55.9 |
| yolo26l-seg.dxnn | 1 | 44.8 | 1 | 45.3 |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | 1 | 3 | 59.2 ±0.0 | 59.2 | 158 | 92.3 | 100.0 | 52~55 | 1000 | 212 | ok |
| yolo26n-obb.dxnn | 2 | 3 | 59.2 ±0.0 | 29.6 | 163 | 95.6 | 100.0 | 59~62 | 1000 | 227 | ok |
| yolo26s-obb.dxnn | 1 | 3 | 36.4 ±0.0 | 36.4 | 128 | 95.5 | 100.0 | 55~60 | 1000 | 228 | ok |
| yolo26s-obb.dxnn | 2 | 3 | 36.4 ±0.0 | 18.2 | 129 | 96.7 | 100.0 | 64~68 | 1000 | 244 | ok |
| yolo26m-obb.dxnn | 1 | 3 | 27.3 ±0.0 | 27.3 | 107 | 95.6 | 100.0 | 61~68 | 1000 | 250 | ok |
| yolo26l-obb.dxnn | 1 | 3 | 20.5 ±0.0 | 20.5 | 88 | 95.4 | 100.0 | 63~69 | 1000 | 264 | ok |
| yolo26x-obb.dxnn | 1 | 3 | 11.9 ±0.0 | 11.9 | 62 | 97.9 | 100.0 | 70~76 | 1000 | 374 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | 1 | 3 | 59.2 ±0.0 | 59.2 | 167 | 93.8 | 100.0 | 52~55 | 1000 | 208 | ok |
| yolo26n-obb.dxnn | 2 | 3 | 59.3 ±0.0 | 29.6 | 171 | 95.5 | 100.0 | 59~62 | 1000 | 224 | ok |
| yolo26s-obb.dxnn | 1 | 3 | 36.4 ±0.0 | 36.4 | 136 | 95.4 | 100.0 | 55~59 | 1000 | 223 | ok |
| yolo26s-obb.dxnn | 2 | 3 | 36.4 ±0.0 | 18.2 | 139 | 97.0 | 100.0 | 63~66 | 1000 | 238 | ok |
| yolo26m-obb.dxnn | 1 | 3 | 27.3 ±0.0 | 27.3 | 111 | 96.0 | 100.0 | 61~67 | 1000 | 242 | ok |
| yolo26l-obb.dxnn | 1 | 3 | 16.3 ±5.1 | 16.3 | 85 | 74.2 | 100.0 | 61~67 | 1000 | 254 | ok |
| yolo26x-obb.dxnn | 1 | 3 | 11.9 ±0.0 | 11.9 | 63 | 98.0 | 100.0 | 70~74 | 1000 | 374 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-obb.dxnn | 1 | 59.2 | 1 | 59.2 |
| yolo26s-obb.dxnn | 1 | 36.4 | 1 | 36.4 |

---
*Report generated by dx_stream benchmark tool*
