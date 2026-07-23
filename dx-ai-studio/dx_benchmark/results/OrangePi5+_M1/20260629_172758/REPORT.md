# YOLO26 Benchmark Report

**Generated:** 2026-06-30 12:43:46 (Local)

## Test Timing

| # | Type | Start | End | Duration |
|---|------|-------|-----|----------|
| 1 | run | 2026-06-29 17:27:58 | 2026-06-30 12:43:46 | 19h 15m 48s |

## Executive Summary

### Object Detection

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n.dxnn | ON | 41.04 | 182.2 | 138.4 | 4 |
| yolo26n.dxnn | OFF | 35.51 | 226.0 | 98.9 | 3 |
| yolo26s.dxnn | ON | 47.74 | 127.5 | 108.5 | 3 |
| yolo26s.dxnn | OFF | 43.08 | 131.5 | 96.6 | 3 |
| yolo26m.dxnn | ON | 57.58 | 91.0 | 83.8 | 2 |
| yolo26m.dxnn | OFF | 50.30 | 90.7 | 90.5 | 2 |
| yolo26l.dxnn | ON | 70.71 | 67.3 | 65.1 | 2 |
| yolo26l.dxnn | OFF | 59.83 | 66.5 | 66.8 | 2 |
| yolo26x.dxnn | ON | 95.53 | 38.7 | 37.7 | 1 |
| yolo26x.dxnn | OFF | 86.94 | 38.1 | 37.8 | 1 |

### Pose Estimation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-pose.dxnn | ON | 30.53 | 210.0 | 180.2 | 6 |
| yolo26n-pose.dxnn | OFF | 25.50 | 217.6 | 205.8 | 6 |
| yolo26s-pose.dxnn | ON | 39.65 | 126.7 | 120.6 | 3 |
| yolo26s-pose.dxnn | OFF | 32.01 | 126.4 | 124.8 | 4 |
| yolo26m-pose.dxnn | ON | 48.70 | 88.2 | 87.5 | 2 |
| yolo26m-pose.dxnn | OFF | 39.69 | 87.7 | 87.5 | 2 |
| yolo26l-pose.dxnn | ON | 60.44 | 65.2 | 65.3 | 2 |
| yolo26l-pose.dxnn | OFF | 50.06 | 64.9 | 65.4 | 2 |
| yolo26x-pose.dxnn | ON | 86.96 | 37.5 | 37.4 | 1 |
| yolo26x-pose.dxnn | OFF | 78.39 | 37.8 | 37.7 | 1 |

### Segmentation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-seg.dxnn | ON | 55.47 | 129.6 | 99.2 | 3 |
| yolo26n-seg.dxnn | OFF | 45.72 | 160.2 | 86.7 | 2 |
| yolo26s-seg.dxnn | ON | 65.54 | 99.0 | 80.4 | 2 |
| yolo26s-seg.dxnn | OFF | 54.16 | 101.9 | 84.0 | 2 |
| yolo26m-seg.dxnn | ON | 83.32 | 65.3 | 58.8 | 1 |
| yolo26m-seg.dxnn | OFF | 70.62 | 65.5 | 63.2 | 1 |
| yolo26l-seg.dxnn | ON | 90.79 | 52.2 | 49.3 | 1 |
| yolo26l-seg.dxnn | OFF | 82.24 | 52.0 | 50.7 | 1 |
| yolo26x-seg.dxnn | ON | 132.01 | 29.2 | 23.5 | — |
| yolo26x-seg.dxnn | OFF | 125.44 | 29.5 | 27.5 | — |

### Oriented BBox (OBB)

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-obb.dxnn | ON | 48.70 | 74.6 | 72.9 | 2 |
| yolo26n-obb.dxnn | OFF | 43.50 | 74.4 | 74.0 | 2 |
| yolo26s-obb.dxnn | ON | 73.68 | 43.6 | 43.4 | 1 |
| yolo26s-obb.dxnn | OFF | 61.99 | 43.6 | 43.5 | 1 |
| yolo26m-obb.dxnn | ON | 91.82 | 31.9 | 31.8 | 1 |
| yolo26m-obb.dxnn | OFF | 79.92 | 31.9 | 31.8 | 1 |
| yolo26l-obb.dxnn | ON | 109.46 | 23.2 | 23.3 | — |
| yolo26l-obb.dxnn | OFF | 101.01 | 23.2 | 23.3 | — |
| yolo26x-obb.dxnn | ON | 184.18 | 13.5 | 13.4 | — |
| yolo26x-obb.dxnn | OFF | 172.89 | 13.5 | 13.5 | — |

### Classification

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-cls.dxnn | ON | 2.10 | 3374.1 | 1048.2 | — |
| yolo26n-cls.dxnn | OFF | 2.47 | 3378.2 | 1050.5 | — |
| yolo26s-cls.dxnn | ON | 2.89 | 1894.5 | 1058.2 | — |
| yolo26s-cls.dxnn | OFF | 2.80 | 1894.0 | 1056.6 | — |
| yolo26m-cls.dxnn | ON | 3.82 | 1331.3 | 1058.0 | — |
| yolo26m-cls.dxnn | OFF | 3.74 | 1332.3 | 1056.0 | — |
| yolo26l-cls.dxnn | ON | 4.89 | 841.5 | 837.5 | — |
| yolo26l-cls.dxnn | OFF | 4.88 | 841.8 | 837.2 | — |
| yolo26x-cls.dxnn | ON | 8.23 | 451.0 | 448.5 | — |
| yolo26x-cls.dxnn | OFF | 7.84 | 450.8 | 447.4 | — |

## Environment

| Item | Value |
|------|-------|
| Product | OrangePi5+ |
| Hostname | orangepi5plus |
| OS | Debian GNU/Linux 12 (bookworm) |
| Kernel | 6.1.43-rockchip-rk3588 |
| CPU | Cortex-A55 |
| CPU Cores | 8 |
| RAM | 15.6 GB |
| NPU SKU | M1 |
| NPU RT | v3.3.2 |
| NPU Driver (RT) | v2.4.1 |
| NPU Driver (PCIe) | v2.2.0 |
| NPU Firmware | v2.5.6 |
| NPU Memory | LPDDR5 5600 Mbps, 3.92GiB |
| NPU Board | M.2, Rev 1.0 |
| NPU PCIe | Gen3 X4 [01:00:00] |

### Tools

| Tool | Available | Version |
|------|-----------|---------|
| run_model | Yes | DXRT v3.3.2 run_model |
| gst-launch-1.0 | Yes | gst-launch-1.0 version 1.22.0 |
| gst-inspect-1.0 | Yes | gst-inspect-1.0 version 1.22.0 |
| dxtop | Yes | DX-TOP 1.1.0 |
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
| yolo26n.dxnn | 182.2 ±0.6 | 234 | 56.0 | 93.4 | 48~52 | 1000 | ok |
| yolo26s.dxnn | 127.5 ±0.3 | 198 | 85.6 | 99.5 | 59~62 | 1000 | ok |
| yolo26m.dxnn | 91.0 ±0.1 | 170 | 91.9 | 100.0 | 62~66 | 1000 | ok |
| yolo26l.dxnn | 67.3 ±0.1 | 162 | 89.9 | 100.0 | 62~66 | 1000 | ok |
| yolo26x.dxnn | 38.7 ±0.1 | 117 | 89.8 | 100.0 | 63~68 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n.dxnn | 226.0 ±0.4 | 177 | 90.2 | 100.0 | 58~60 | 1000 | ok |
| yolo26s.dxnn | 131.5 ±0.3 | 140 | 92.1 | 100.0 | 59~62 | 1000 | ok |
| yolo26m.dxnn | 90.7 ±0.1 | 122 | 88.8 | 100.0 | 62~66 | 1000 | ok |
| yolo26l.dxnn | 66.5 ±0.1 | 123 | 89.0 | 100.0 | 62~65 | 1000 | ok |
| yolo26x.dxnn | 38.1 ±0.0 | 85 | 88.6 | 100.0 | 63~67 | 1000 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-pose.dxnn | 210.0 ±1.2 | 217 | 84.1 | 96.7 | 58~61 | 1000 | ok |
| yolo26s-pose.dxnn | 126.7 ±0.1 | 177 | 92.7 | 100.0 | 59~62 | 1000 | ok |
| yolo26m-pose.dxnn | 88.2 ±0.1 | 154 | 90.7 | 100.0 | 62~66 | 1000 | ok |
| yolo26l-pose.dxnn | 65.2 ±0.1 | 126 | 89.9 | 100.0 | 61~65 | 1000 | ok |
| yolo26x-pose.dxnn | 37.5 ±0.3 | 102 | 89.2 | 100.0 | 63~67 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-pose.dxnn | 217.6 ±0.8 | 157 | 90.1 | 100.0 | 59~61 | 1000 | ok |
| yolo26s-pose.dxnn | 126.4 ±0.4 | 133 | 89.5 | 100.0 | 59~62 | 1000 | ok |
| yolo26m-pose.dxnn | 87.7 ±0.2 | 121 | 88.8 | 100.0 | 62~66 | 1000 | ok |
| yolo26l-pose.dxnn | 64.9 ±0.2 | 95 | 89.3 | 100.0 | 62~65 | 1000 | ok |
| yolo26x-pose.dxnn | 37.8 ±0.2 | 57 | 88.9 | 100.0 | 63~67 | 1000 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-seg.dxnn | 129.6 ±1.3 | 296 | 50.6 | 84.7 | 57~59 | 1000 | ok |
| yolo26s-seg.dxnn | 99.0 ±1.4 | 235 | 83.5 | 100.0 | 60~64 | 1000 | ok |
| yolo26m-seg.dxnn | 65.3 ±0.0 | 176 | 88.5 | 100.0 | 64~69 | 1000 | ok |
| yolo26l-seg.dxnn | 52.2 ±0.1 | 152 | 88.8 | 100.0 | 64~68 | 1000 | ok |
| yolo26x-seg.dxnn | 29.2 ±0.3 | 111 | 89.1 | 100.0 | 65~70 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-seg.dxnn | 160.2 ±0.5 | 227 | 76.4 | 89.8 | 59~62 | 1000 | ok |
| yolo26s-seg.dxnn | 101.9 ±0.3 | 176 | 88.5 | 100.0 | 60~64 | 1000 | ok |
| yolo26m-seg.dxnn | 65.5 ±0.1 | 147 | 89.3 | 100.0 | 64~69 | 1000 | ok |
| yolo26l-seg.dxnn | 52.0 ±0.3 | 130 | 90.6 | 100.0 | 64~68 | 1000 | ok |
| yolo26x-seg.dxnn | 29.5 ±0.1 | 90 | 89.6 | 100.0 | 64~68 | 1000 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-obb.dxnn | 74.6 ±0.1 | 152 | 92.1 | 100.0 | 56~57 | 1000 | ok |
| yolo26s-obb.dxnn | 43.6 ±0.1 | 126 | 89.2 | 100.0 | 57~59 | 1000 | ok |
| yolo26m-obb.dxnn | 31.9 ±0.0 | 107 | 89.8 | 100.0 | 60~63 | 1000 | ok |
| yolo26l-obb.dxnn | 23.2 ±0.1 | 79 | 88.6 | 100.0 | 60~63 | 1000 | ok |
| yolo26x-obb.dxnn | 13.5 ±0.1 | 46 | 84.8 | 100.0 | 62~65 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-obb.dxnn | 74.4 ±0.1 | 122 | 91.3 | 100.0 | 57~58 | 1000 | ok |
| yolo26s-obb.dxnn | 43.6 ±0.0 | 75 | 92.8 | 100.0 | 58~59 | 1000 | ok |
| yolo26m-obb.dxnn | 31.9 ±0.1 | 54 | 88.8 | 100.0 | 61~64 | 1000 | ok |
| yolo26l-obb.dxnn | 23.2 ±0.0 | 41 | 89.5 | 100.0 | 61~63 | 1000 | ok |
| yolo26x-obb.dxnn | 13.5 ±0.0 | 24 | 84.2 | 100.0 | 62~65 | 1000 | ok |

#### Classification

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-cls.dxnn | 3374.1 ±3.9 | 138 | 85.1 | 94.4 | 56 | 1000 | ok |
| yolo26s-cls.dxnn | 1894.5 ±0.5 | 102 | 88.6 | 97.3 | 56~57 | 1000 | ok |
| yolo26m-cls.dxnn | 1331.3 ±0.6 | 85 | 89.9 | 97.8 | 60~63 | 1000 | ok |
| yolo26l-cls.dxnn | 841.5 ±0.7 | 65 | 90.8 | 98.5 | 58~60 | 1000 | ok |
| yolo26x-cls.dxnn | 451.0 ±0.2 | 40 | 91.5 | 99.4 | 60~62 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-cls.dxnn | 3378.2 ±2.5 | 137 | 84.9 | 94.7 | 55~56 | 1000 | ok |
| yolo26s-cls.dxnn | 1894.0 ±1.9 | 102 | 87.7 | 96.4 | 56~58 | 1000 | ok |
| yolo26m-cls.dxnn | 1332.3 ±0.2 | 85 | 90.2 | 97.8 | 60~63 | 1000 | ok |
| yolo26l-cls.dxnn | 841.8 ±0.3 | 64 | 91.3 | 98.9 | 59~60 | 1000 | ok |
| yolo26x-cls.dxnn | 450.8 ±0.8 | 39 | 88.4 | 99.4 | 60~62 | 1000 | ok |

### Latency (Single-Core, Sync)

#### Object Detection

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n.dxnn | 24.4 | 41.04 | 35.30 | 5.74 | 44 | ok |
| yolo26s.dxnn | 20.9 | 47.74 | 42.37 | 5.37 | 54 | ok |
| yolo26m.dxnn | 17.4 | 57.58 | 52.84 | 4.74 | 55 | ok |
| yolo26l.dxnn | 14.1 | 70.71 | 65.11 | 5.60 | 55 | ok |
| yolo26x.dxnn | 10.5 | 95.53 | 86.91 | 8.63 | 55 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n.dxnn | 28.2 | 35.51 | 35.51 | 54 | ok |
| yolo26s.dxnn | 23.2 | 43.08 | 43.08 | 54 | ok |
| yolo26m.dxnn | 19.9 | 50.30 | 50.30 | 55 | ok |
| yolo26l.dxnn | 16.7 | 59.83 | 59.83 | 55 | ok |
| yolo26x.dxnn | 11.5 | 86.94 | 86.94 | 56 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-pose.dxnn | 32.8 | 30.53 | 26.81 | 3.73 | 54 | ok |
| yolo26s-pose.dxnn | 25.2 | 39.65 | 35.03 | 4.62 | 54 | ok |
| yolo26m-pose.dxnn | 20.5 | 48.70 | 45.40 | 3.30 | 55 | ok |
| yolo26l-pose.dxnn | 16.5 | 60.44 | 57.42 | 3.02 | 55 | ok |
| yolo26x-pose.dxnn | 11.5 | 86.96 | 83.55 | 3.41 | 56 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-pose.dxnn | 39.2 | 25.50 | 25.50 | 54 | ok |
| yolo26s-pose.dxnn | 31.2 | 32.01 | 32.01 | 54 | ok |
| yolo26m-pose.dxnn | 25.2 | 39.69 | 39.69 | 55 | ok |
| yolo26l-pose.dxnn | 20.0 | 50.06 | 50.06 | 55 | ok |
| yolo26x-pose.dxnn | 12.8 | 78.39 | 78.39 | 56 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-seg.dxnn | 18.0 | 55.47 | 49.33 | 6.14 | 54 | ok |
| yolo26s-seg.dxnn | 15.3 | 65.54 | 58.90 | 6.63 | 54 | ok |
| yolo26m-seg.dxnn | 12.0 | 83.32 | 75.32 | 8.00 | 55 | ok |
| yolo26l-seg.dxnn | 11.0 | 90.79 | 84.95 | 5.84 | 55 | ok |
| yolo26x-seg.dxnn | 7.6 | 132.01 | 125.94 | 6.07 | 56 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-seg.dxnn | 21.9 | 45.72 | 45.72 | 54 | ok |
| yolo26s-seg.dxnn | 18.5 | 54.16 | 54.16 | 54 | ok |
| yolo26m-seg.dxnn | 14.2 | 70.62 | 70.62 | 55 | ok |
| yolo26l-seg.dxnn | 12.2 | 82.24 | 82.24 | 55 | ok |
| yolo26x-seg.dxnn | 8.0 | 125.44 | 125.44 | 55 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-obb.dxnn | 20.5 | 48.70 | 42.69 | 6.02 | 53 | ok |
| yolo26s-obb.dxnn | 13.6 | 73.68 | 69.26 | 4.42 | 53 | ok |
| yolo26m-obb.dxnn | 10.9 | 91.82 | 87.52 | 4.31 | 55 | ok |
| yolo26l-obb.dxnn | 9.1 | 109.46 | 105.64 | 3.82 | 55 | ok |
| yolo26x-obb.dxnn | 5.4 | 184.18 | 179.73 | 4.45 | 56 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-obb.dxnn | 23.0 | 43.50 | 43.50 | 54 | ok |
| yolo26s-obb.dxnn | 16.1 | 61.99 | 61.99 | 54 | ok |
| yolo26m-obb.dxnn | 12.5 | 79.92 | 79.92 | 56 | ok |
| yolo26l-obb.dxnn | 9.9 | 101.01 | 101.01 | 55 | ok |
| yolo26x-obb.dxnn | 5.8 | 172.89 | 172.89 | 56 | ok |

#### Classification

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-cls.dxnn | 475.1 | 2.10 | 2.10 | N/A | 54 | ok |
| yolo26s-cls.dxnn | 346.1 | 2.89 | 2.89 | N/A | 53 | ok |
| yolo26m-cls.dxnn | 261.5 | 3.82 | 3.82 | N/A | 54 | ok |
| yolo26l-cls.dxnn | 204.4 | 4.89 | 4.89 | N/A | 54 | ok |
| yolo26x-cls.dxnn | 121.6 | 8.23 | 8.23 | N/A | 54 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-cls.dxnn | 405.3 | 2.47 | 2.47 | 53 | ok |
| yolo26s-cls.dxnn | 356.8 | 2.80 | 2.80 | 53 | ok |
| yolo26m-cls.dxnn | 267.2 | 3.74 | 3.74 | 54 | ok |
| yolo26l-cls.dxnn | 204.9 | 4.88 | 4.88 | 54 | ok |
| yolo26x-cls.dxnn | 127.5 | 7.84 | 7.84 | 54 | ok |

## E2E Pipeline (Single-Stream)

### Object Detection

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | mppvideodec | 3455 | 3 | 138.4 ±2.0 | 24.95 | 248 | 45.9 | 74.5 | 53~54 | 1000 | 175 | ok |
| yolo26s.dxnn | mppvideodec | 3455 | 3 | 108.5 ±0.9 | 31.86 | 211 | 71.1 | 89.9 | 62~64 | 1000 | 189 | ok |
| yolo26m.dxnn | mppvideodec | 3455 | 3 | 83.8 ±0.4 | 41.25 | 192 | 82.6 | 100.0 | 69~73 | 1000 | 210 | ok |
| yolo26l.dxnn | mppvideodec | 3455 | 3 | 65.1 ±0.3 | 53.09 | 171 | 89.7 | 100.0 | 70~74 | 1000 | 220 | ok |
| yolo26x.dxnn | mppvideodec | 3455 | 3 | 37.7 ±1.1 | 91.55 | 127 | 95.1 | 100.0 | 76~81 | 800~1000 | 346 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | mppvideodec | 3455 | 3 | 98.9 ±0.3 | 34.95 | 216 | 25.7 | 86.0 | 57 | 1000 | 189 | ok |
| yolo26s.dxnn | mppvideodec | 3455 | 3 | 96.6 ±5.0 | 35.78 | 215 | 51.8 | 87.9 | 62~63 | 1000 | 203 | ok |
| yolo26m.dxnn | mppvideodec | 3455 | 3 | 90.5 ±0.2 | 38.19 | 227 | 90.8 | 100.0 | 69~73 | 1000 | 224 | ok |
| yolo26l.dxnn | mppvideodec | 3455 | 3 | 66.8 ±0.2 | 51.72 | 199 | 92.9 | 100.0 | 70~74 | 1000 | 232 | ok |
| yolo26x.dxnn | mppvideodec | 3455 | 3 | 37.8 ±1.3 | 91.43 | 146 | 95.1 | 100.0 | 76~81 | 800~1000 | 346 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n.dxnn | 138.4 | 98.9 | +39.6 | +40.0% |
| yolo26s.dxnn | 108.5 | 96.6 | +11.9 | +12.3% |
| yolo26m.dxnn | 83.8 | 90.5 | -6.7 | -7.4% |
| yolo26l.dxnn | 65.1 | 66.8 | -1.7 | -2.6% |
| yolo26x.dxnn | 37.7 | 37.8 | -0.0 | -0.1% |

### Pose Estimation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | mppvideodec | 3455 | 3 | 180.2 ±0.9 | 19.17 | 238 | 67.7 | 88.9 | 61~62 | 1000 | 166 | ok |
| yolo26s-pose.dxnn | mppvideodec | 3455 | 3 | 120.6 ±0.5 | 28.64 | 198 | 84.5 | 99.7 | 63~65 | 1000 | 181 | ok |
| yolo26m-pose.dxnn | mppvideodec | 3455 | 3 | 87.5 ±0.3 | 39.47 | 163 | 90.4 | 100.0 | 69~73 | 1000 | 202 | ok |
| yolo26l-pose.dxnn | mppvideodec | 3455 | 3 | 65.3 ±0.2 | 52.91 | 140 | 92.7 | 100.0 | 69~73 | 1000 | 212 | ok |
| yolo26x-pose.dxnn | mppvideodec | 3455 | 3 | 37.4 ±1.1 | 92.29 | 101 | 94.8 | 100.0 | 75~80 | 800~1000 | 358 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | mppvideodec | 3455 | 3 | 205.8 ±0.6 | 16.79 | 202 | 77.4 | 95.5 | 61~62 | 1000 | 157 | ok |
| yolo26s-pose.dxnn | mppvideodec | 3455 | 3 | 124.8 ±0.3 | 27.69 | 166 | 87.3 | 100.0 | 63~65 | 1000 | 170 | ok |
| yolo26m-pose.dxnn | mppvideodec | 3455 | 3 | 87.5 ±0.2 | 39.51 | 136 | 91.8 | 100.0 | 69~73 | 1000 | 193 | ok |
| yolo26l-pose.dxnn | mppvideodec | 3455 | 3 | 65.4 ±0.1 | 52.85 | 112 | 94.1 | 100.0 | 69~73 | 1000 | 202 | ok |
| yolo26x-pose.dxnn | mppvideodec | 3455 | 3 | 37.7 ±0.9 | 91.71 | 82 | 95.0 | 100.0 | 75~80 | 800~1000 | 358 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-pose.dxnn | 180.2 | 205.8 | -25.6 | -12.4% |
| yolo26s-pose.dxnn | 120.6 | 124.8 | -4.2 | -3.3% |
| yolo26m-pose.dxnn | 87.5 | 87.5 | +0.1 | +0.1% |
| yolo26l-pose.dxnn | 65.3 | 65.4 | -0.1 | -0.1% |
| yolo26x-pose.dxnn | 37.4 | 37.7 | -0.2 | -0.6% |

### Segmentation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | mppvideodec | 3455 | 3 | 99.2 ±0.4 | 34.81 | 334 | 40.9 | 67.3 | 60~62 | 1000 | 275 | ok |
| yolo26s-seg.dxnn | mppvideodec | 3455 | 3 | 80.4 ±1.6 | 42.96 | 271 | 67.2 | 89.3 | 66~68 | 1000 | 290 | ok |
| yolo26m-seg.dxnn | mppvideodec | 3455 | 3 | 58.8 ±1.1 | 58.78 | 226 | 83.3 | 99.8 | 75~80 | 800~1000 | 315 | ok |
| yolo26l-seg.dxnn | mppvideodec | 3455 | 3 | 49.3 ±1.5 | 70.14 | 201 | 89.8 | 100.0 | 75~81 | 1000 | 321 | ok |
| yolo26x-seg.dxnn | mppvideodec | 3455 | 3 | 23.5 ±2.4 | 147.06 | 123 | 91.6 | 100.0 | 81~82 | 400~1000 | 395 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | mppvideodec | 3455 | 3 | 86.7 ±0.3 | 39.86 | 268 | 27.8 | 89.5 | 61~62 | 1000 | 300 | ok |
| yolo26s-seg.dxnn | mppvideodec | 3455 | 3 | 84.0 ±2.8 | 41.12 | 276 | 61.1 | 95.3 | 65~68 | 1000 | 315 | ok |
| yolo26m-seg.dxnn | mppvideodec | 3455 | 3 | 63.2 ±2.3 | 54.63 | 229 | 91.4 | 100.0 | 75~81 | 800~1000 | 336 | ok |
| yolo26l-seg.dxnn | mppvideodec | 3455 | 3 | 50.7 ±1.9 | 68.17 | 204 | 93.0 | 100.0 | 75~81 | 800~1000 | 344 | ok |
| yolo26x-seg.dxnn | mppvideodec | 3455 | 3 | 27.5 ±1.4 | 125.78 | 136 | 93.2 | 100.0 | 77~80 | 800~1000 | 406 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-seg.dxnn | 99.2 | 86.7 | +12.6 | +14.5% |
| yolo26s-seg.dxnn | 80.4 | 84.0 | -3.6 | -4.3% |
| yolo26m-seg.dxnn | 58.8 | 63.2 | -4.5 | -7.1% |
| yolo26l-seg.dxnn | 49.3 | 50.7 | -1.4 | -2.8% |
| yolo26x-seg.dxnn | 23.5 | 27.5 | -4.0 | -14.5% |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | mppvideodec | 2640 | 3 | 72.9 ±0.4 | 36.20 | 170 | 88.9 | 100.0 | 56~58 | 1000 | 192 | ok |
| yolo26s-obb.dxnn | mppvideodec | 2640 | 3 | 43.4 ±0.1 | 60.85 | 121 | 92.9 | 100.0 | 60~63 | 1000 | 208 | ok |
| yolo26m-obb.dxnn | mppvideodec | 2640 | 3 | 31.8 ±0.1 | 83.03 | 103 | 94.0 | 100.0 | 67~72 | 1000 | 230 | ok |
| yolo26l-obb.dxnn | mppvideodec | 2640 | 3 | 23.3 ±0.0 | 113.42 | 88 | 95.3 | 100.0 | 70~75 | 1000 | 244 | ok |
| yolo26x-obb.dxnn | mppvideodec | 2640 | 3 | 13.4 ±0.2 | 196.43 | 57 | 92.9 | 100.0 | 76~79 | 1000 | 366 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | mppvideodec | 2640 | 3 | 74.0 ±0.1 | 35.66 | 179 | 90.0 | 100.0 | 57~58 | 1000 | 194 | ok |
| yolo26s-obb.dxnn | mppvideodec | 2640 | 3 | 43.5 ±0.1 | 60.74 | 132 | 93.5 | 100.0 | 60~61 | 1000 | 212 | ok |
| yolo26m-obb.dxnn | mppvideodec | 2640 | 3 | 31.8 ±0.0 | 82.95 | 114 | 94.1 | 100.0 | 69~74 | 1000 | 233 | ok |
| yolo26l-obb.dxnn | mppvideodec | 2640 | 3 | 23.3 ±0.0 | 113.30 | 94 | 94.8 | 100.0 | 71~75 | 1000 | 245 | ok |
| yolo26x-obb.dxnn | mppvideodec | 2640 | 3 | 13.5 ±0.1 | 195.29 | 56 | 92.6 | 100.0 | 76~79 | 1000 | 366 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-obb.dxnn | 72.9 | 74.0 | -1.1 | -1.5% |
| yolo26s-obb.dxnn | 43.4 | 43.5 | -0.1 | -0.2% |
| yolo26m-obb.dxnn | 31.8 | 31.8 | -0.0 | -0.1% |
| yolo26l-obb.dxnn | 23.3 | 23.3 | -0.0 | -0.1% |
| yolo26x-obb.dxnn | 13.4 | 13.5 | -0.1 | -0.6% |

### Classification

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-cls.dxnn | mppvideodec | 3455 | 3 | 1048.2 ±10.6 | 3.30 | 183 | 15.5 | 51.4 | 54 | 1000 | 86 | ok |
| yolo26s-cls.dxnn | mppvideodec | 3455 | 3 | 1058.2 ±6.6 | 3.27 | 183 | 26.5 | 69.6 | 54 | 1000 | 100 | ok |
| yolo26m-cls.dxnn | mppvideodec | 3455 | 3 | 1058.0 ±1.9 | 3.27 | 182 | 41.7 | 83.9 | 59 | 1000 | 124 | ok |
| yolo26l-cls.dxnn | mppvideodec | 3455 | 3 | 837.5 ±4.2 | 4.12 | 162 | 49.5 | 98.1 | 58 | 1000 | 136 | ok |
| yolo26x-cls.dxnn | mppvideodec | 3455 | 3 | 448.5 ±1.8 | 7.70 | 120 | 70.8 | 99.1 | 61 | 1000 | 212 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-cls.dxnn | mppvideodec | 3455 | 3 | 1050.5 ±11.9 | 3.29 | 182 | 15.8 | 51.2 | 53 | 1000 | 86 | ok |
| yolo26s-cls.dxnn | mppvideodec | 3455 | 3 | 1056.6 ±8.4 | 3.27 | 183 | 28.0 | 70.7 | 55 | 1000 | 100 | ok |
| yolo26m-cls.dxnn | mppvideodec | 3455 | 3 | 1056.0 ±8.9 | 3.27 | 182 | 44.5 | 85.4 | 59 | 1000 | 124 | ok |
| yolo26l-cls.dxnn | mppvideodec | 3455 | 3 | 837.2 ±0.6 | 4.13 | 161 | 58.4 | 98.0 | 58 | 1000 | 136 | ok |
| yolo26x-cls.dxnn | mppvideodec | 3455 | 3 | 447.4 ±0.8 | 7.72 | 121 | 66.1 | 98.7 | 61 | 1000 | 212 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-cls.dxnn | 1048.2 | 1050.5 | -2.3 | -0.2% |
| yolo26s-cls.dxnn | 1058.2 | 1056.6 | +1.6 | +0.1% |
| yolo26m-cls.dxnn | 1058.0 | 1056.0 | +2.0 | +0.2% |
| yolo26l-cls.dxnn | 837.5 | 837.2 | +0.3 | +0.0% |
| yolo26x-cls.dxnn | 448.5 | 447.4 | +1.1 | +0.2% |

## E2E Pipeline (Multi-Stream)

### Object Detection

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | 4 | 3 | 139.9 ±2.8 | 35.0 | 254 | 50.1 | 75.6 | 59~62 | 1000 | 199 | ok |
| yolo26n.dxnn | 5 | 3 | 138.4 ±0.7 | 27.7 | 257 | 49.7 | 73.9 | 63~64 | 1000 | 205 | ok |
| yolo26s.dxnn | 3 | 3 | 108.3 ±0.9 | 36.1 | 216 | 74.8 | 95.6 | 68~71 | 1000 | 207 | ok |
| yolo26s.dxnn | 4 | 3 | 108.3 ±0.8 | 27.1 | 216 | 75.9 | 93.1 | 73~74 | 1000 | 212 | ok |
| yolo26m.dxnn | 2 | 3 | 82.8 ±1.4 | 41.4 | 191 | 86.2 | 99.7 | 77~80 | 1000 | 222 | ok |
| yolo26m.dxnn | 3 | 3 | 77.6 ±0.9 | 25.9 | 186 | 89.0 | 100.0 | 82~83 | 600~1000 | 229 | ok |
| yolo26l.dxnn | 2 | 3 | 62.8 ±2.3 | 31.4 | 172 | 92.9 | 100.0 | 79~81 | 1000 | 231 | ok |
| yolo26l.dxnn | 3 | 3 | 59.6 ±0.6 | 19.9 | 169 | 93.7 | 100.0 | 82 | 800~1000 | 238 | ok |
| yolo26x.dxnn | 1 | 3 | 37.7 ±1.1 | 37.7 | 127 | 95.1 | 100.0 | 76~81 | 800~1000 | 346 | ok |
| yolo26x.dxnn | 2 | 3 | 32.8 ±0.2 | 16.4 | 118 | 94.3 | 100.0 | 83 | 600~1000 | 346 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | 3 | 3 | 99.8 ±0.4 | 33.3 | 215 | 27.4 | 85.2 | 57~59 | 1000 | 213 | ok |
| yolo26n.dxnn | 4 | 3 | 100.0 ±0.1 | 25.0 | 219 | 27.5 | 85.5 | 61~62 | 1000 | 221 | ok |
| yolo26s.dxnn | 3 | 3 | 100.0 ±0.4 | 33.3 | 225 | 55.9 | 88.5 | 67~69 | 1000 | 226 | ok |
| yolo26s.dxnn | 4 | 3 | 100.5 ±0.2 | 25.1 | 230 | 56.7 | 88.8 | 71~72 | 1000 | 234 | ok |
| yolo26m.dxnn | 3 | 3 | 83.8 ±4.0 | 27.9 | 221 | 95.5 | 100.0 | 80~83 | 800~1000 | 244 | ok |
| yolo26m.dxnn | 2 | 3 | 80.2 ±1.3 | 40.1 | 219 | 94.0 | 100.0 | 82~83 | 600~1000 | 234 | ok |
| yolo26l.dxnn | 2 | 3 | 63.2 ±3.0 | 31.6 | 198 | 95.8 | 100.0 | 79~81 | 1000 | 243 | ok |
| yolo26l.dxnn | 3 | 3 | 59.7 ±0.5 | 19.9 | 189 | 95.8 | 100.0 | 82~83 | 800~1000 | 252 | ok |
| yolo26x.dxnn | 1 | 3 | 37.8 ±1.3 | 37.8 | 146 | 95.1 | 100.0 | 76~81 | 800~1000 | 346 | ok |
| yolo26x.dxnn | 2 | 3 | 32.6 ±0.2 | 16.3 | 136 | 94.6 | 100.0 | 83 | 600~1000 | 346 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n.dxnn | 4 | 35.0 | 3 | 33.3 |
| yolo26s.dxnn | 3 | 36.1 | 3 | 33.3 |
| yolo26m.dxnn | 2 | 41.4 | 2 | 40.1 |
| yolo26l.dxnn | 2 | 31.4 | 2 | 31.6 |
| yolo26x.dxnn | 1 | 37.7 | 1 | 37.8 |

### Pose Estimation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | 6 | 3 | 180.7 ±1.4 | 30.1 | 245 | 74.1 | 88.4 | 67~70 | 1000 | 206 | ok |
| yolo26n-pose.dxnn | 7 | 3 | 180.8 ±0.1 | 25.8 | 245 | 74.4 | 89.9 | 71~73 | 1000 | 211 | ok |
| yolo26s-pose.dxnn | 4 | 3 | 119.7 ±0.1 | 29.9 | 200 | 89.0 | 99.7 | 70~74 | 1000 | 209 | ok |
| yolo26s-pose.dxnn | 3 | 3 | 120.2 ±0.7 | 40.1 | 200 | 88.4 | 100.0 | 74~75 | 1000 | 202 | ok |
| yolo26m-pose.dxnn | 2 | 3 | 85.6 ±3.0 | 42.8 | 166 | 94.2 | 100.0 | 77~80 | 1000 | 216 | ok |
| yolo26m-pose.dxnn | 3 | 3 | 78.0 ±1.0 | 26.0 | 161 | 94.1 | 100.0 | 82~83 | 800~1000 | 224 | ok |
| yolo26l-pose.dxnn | 2 | 3 | 63.3 ±2.3 | 31.6 | 141 | 95.4 | 100.0 | 78~80 | 1000 | 225 | ok |
| yolo26l-pose.dxnn | 3 | 3 | 59.5 ±0.3 | 19.8 | 137 | 96.1 | 100.0 | 81~82 | 800~1000 | 234 | ok |
| yolo26x-pose.dxnn | 1 | 3 | 37.4 ±1.1 | 37.4 | 101 | 94.8 | 100.0 | 75~80 | 800~1000 | 358 | ok |
| yolo26x-pose.dxnn | 2 | 3 | 32.4 ±0.2 | 16.2 | 105 | 93.5 | 100.0 | 82 | 800~1000 | 358 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | 6 | 3 | 206.8 ±0.5 | 34.5 | 206 | 88.5 | 96.9 | 66~70 | 1000 | 202 | ok |
| yolo26n-pose.dxnn | 7 | 3 | 207.2 ±0.2 | 29.6 | 205 | 89.0 | 97.3 | 71~73 | 1000 | 208 | ok |
| yolo26s-pose.dxnn | 4 | 3 | 125.0 ±0.1 | 31.3 | 169 | 94.4 | 100.0 | 69~72 | 1000 | 204 | ok |
| yolo26s-pose.dxnn | 5 | 3 | 125.2 ±0.1 | 25.0 | 167 | 94.7 | 100.0 | 74~76 | 1000 | 211 | ok |
| yolo26m-pose.dxnn | 2 | 3 | 86.4 ±2.5 | 43.2 | 137 | 94.3 | 100.0 | 77~80 | 1000 | 205 | ok |
| yolo26m-pose.dxnn | 3 | 3 | 79.4 ±1.4 | 26.5 | 129 | 95.5 | 100.0 | 81~82 | 800~1000 | 216 | ok |
| yolo26l-pose.dxnn | 2 | 3 | 63.8 ±2.0 | 31.9 | 112 | 95.8 | 100.0 | 77~80 | 1000 | 215 | ok |
| yolo26l-pose.dxnn | 3 | 3 | 59.8 ±0.5 | 19.9 | 108 | 96.6 | 100.0 | 81 | 800~1000 | 224 | ok |
| yolo26x-pose.dxnn | 1 | 3 | 37.7 ±0.9 | 37.7 | 82 | 95.0 | 100.0 | 75~80 | 800~1000 | 358 | ok |
| yolo26x-pose.dxnn | 2 | 3 | 32.9 ±0.2 | 16.4 | 78 | 94.9 | 100.0 | 82 | 800~1000 | 358 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-pose.dxnn | 6 | 30.1 | 6 | 34.5 |
| yolo26s-pose.dxnn | 3 | 40.1 | 4 | 31.3 |
| yolo26m-pose.dxnn | 2 | 42.8 | 2 | 43.2 |
| yolo26l-pose.dxnn | 2 | 31.6 | 2 | 31.9 |
| yolo26x-pose.dxnn | 1 | 37.4 | 1 | 37.7 |

### Segmentation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | 3 | 3 | 98.5 ±0.8 | 32.8 | 335 | 42.3 | 65.0 | 65~68 | 1000 | 306 | ok |
| yolo26n-seg.dxnn | 4 | 3 | 99.9 ±1.5 | 25.0 | 331 | 43.3 | 68.3 | 70~72 | 1000 | 315 | ok |
| yolo26s-seg.dxnn | 2 | 3 | 80.2 ±0.2 | 40.1 | 279 | 67.5 | 86.2 | 72~75 | 1000 | 310 | ok |
| yolo26s-seg.dxnn | 3 | 3 | 79.7 ±0.2 | 26.6 | 278 | 69.2 | 85.7 | 76~78 | 1000 | 321 | ok |
| yolo26m-seg.dxnn | 1 | 3 | 58.8 ±1.1 | 58.8 | 226 | 83.3 | 99.8 | 75~80 | 800~1000 | 315 | ok |
| yolo26m-seg.dxnn | 2 | 3 | 47.5 ±1.5 | 23.7 | 194 | 91.7 | 100.0 | 83~84 | 400~1000 | 335 | ok |
| yolo26l-seg.dxnn | 1 | 3 | 49.3 ±1.5 | 49.3 | 201 | 89.8 | 100.0 | 75~81 | 1000 | 321 | ok |
| yolo26l-seg.dxnn | 2 | 3 | 40.4 ±1.1 | 20.2 | 178 | 92.1 | 100.0 | 82~83 | 600~1000 | 345 | ok |
| yolo26x-seg.dxnn | 1 | 3 | 23.5 ±2.4 | 23.5 | 123 | 91.6 | 100.0 | 81~82 | 400~1000 | 395 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | 2 | 3 | 85.6 ±1.6 | 42.8 | 274 | 28.3 | 89.6 | 63~65 | 1000 | 323 | ok |
| yolo26n-seg.dxnn | 3 | 3 | 86.6 ±0.2 | 28.9 | 268 | 29.1 | 89.4 | 66~67 | 1000 | 338 | ok |
| yolo26s-seg.dxnn | 2 | 3 | 84.5 ±2.1 | 42.2 | 268 | 62.4 | 95.3 | 71~74 | 1000 | 339 | ok |
| yolo26s-seg.dxnn | 3 | 3 | 85.1 ±0.4 | 28.4 | 277 | 65.3 | 97.0 | 77~79 | 1000 | 354 | ok |
| yolo26m-seg.dxnn | 2 | 3 | 47.3 ±2.9 | 23.6 | 199 | 93.8 | 100.0 | 83~84 | 400~1000 | 357 | ok |
| yolo26m-seg.dxnn | 1 | 3 | 63.2 ±2.3 | 63.2 | 229 | 91.4 | 100.0 | 75~81 | 800~1000 | 336 | ok |
| yolo26l-seg.dxnn | 1 | 3 | 50.7 ±1.9 | 50.7 | 204 | 93.0 | 100.0 | 75~81 | 800~1000 | 344 | ok |
| yolo26l-seg.dxnn | 2 | 3 | 40.9 ±0.9 | 20.4 | 178 | 93.8 | 100.0 | 83 | 600~1000 | 367 | ok |
| yolo26x-seg.dxnn | 1 | 3 | 27.5 ±1.4 | 27.5 | 136 | 93.2 | 100.0 | 77~80 | 800~1000 | 406 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-seg.dxnn | 3 | 32.8 | 2 | 42.8 |
| yolo26s-seg.dxnn | 2 | 40.1 | 2 | 42.2 |
| yolo26m-seg.dxnn | 1 | 58.8 | 1 | 63.2 |
| yolo26l-seg.dxnn | 1 | 49.3 | 1 | 50.7 |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | 2 | 3 | 72.8 ±0.2 | 36.4 | 174 | 91.1 | 100.0 | 58~60 | 1000 | 207 | ok |
| yolo26n-obb.dxnn | 3 | 3 | 72.8 ±0.1 | 24.3 | 172 | 92.0 | 100.0 | 61 | 1000 | 219 | ok |
| yolo26s-obb.dxnn | 1 | 3 | 43.4 ±0.1 | 43.4 | 121 | 92.9 | 100.0 | 60~63 | 1000 | 208 | ok |
| yolo26s-obb.dxnn | 2 | 3 | 43.5 ±0.0 | 21.7 | 123 | 95.4 | 100.0 | 64~67 | 1000 | 223 | ok |
| yolo26m-obb.dxnn | 1 | 3 | 31.8 ±0.1 | 31.8 | 103 | 94.0 | 100.0 | 67~72 | 1000 | 230 | ok |
| yolo26m-obb.dxnn | 2 | 3 | 31.8 ±0.0 | 15.9 | 106 | 95.7 | 100.0 | 75~77 | 1000 | 246 | ok |
| yolo26l-obb.dxnn | 1 | 3 | 23.3 ±0.0 | 23.3 | 88 | 95.3 | 100.0 | 70~75 | 1000 | 244 | ok |
| yolo26x-obb.dxnn | 1 | 3 | 13.4 ±0.2 | 13.4 | 57 | 92.9 | 100.0 | 76~79 | 1000 | 366 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | 2 | 3 | 74.0 ±0.2 | 37.0 | 183 | 94.5 | 100.0 | 59~62 | 1000 | 211 | ok |
| yolo26n-obb.dxnn | 3 | 3 | 74.0 ±0.1 | 24.6 | 183 | 95.2 | 100.0 | 62~63 | 1000 | 220 | ok |
| yolo26s-obb.dxnn | 1 | 3 | 43.5 ±0.1 | 43.5 | 132 | 93.5 | 100.0 | 60~61 | 1000 | 212 | ok |
| yolo26s-obb.dxnn | 2 | 3 | 43.5 ±0.1 | 21.7 | 134 | 95.6 | 100.0 | 64 | 1000 | 226 | ok |
| yolo26m-obb.dxnn | 1 | 3 | 31.8 ±0.0 | 31.8 | 114 | 94.1 | 100.0 | 69~74 | 1000 | 233 | ok |
| yolo26m-obb.dxnn | 2 | 3 | 31.5 ±0.5 | 15.8 | 115 | 96.0 | 100.0 | 77~79 | 1000 | 247 | ok |
| yolo26l-obb.dxnn | 1 | 3 | 23.3 ±0.0 | 23.3 | 94 | 94.8 | 100.0 | 71~75 | 1000 | 245 | ok |
| yolo26x-obb.dxnn | 1 | 3 | 13.5 ±0.1 | 13.5 | 56 | 92.6 | 100.0 | 76~79 | 1000 | 366 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-obb.dxnn | 2 | 36.4 | 2 | 37.0 |
| yolo26s-obb.dxnn | 1 | 43.4 | 1 | 43.5 |
| yolo26m-obb.dxnn | 1 | 31.8 | 1 | 31.8 |

---
*Report generated by dx_stream benchmark tool*
