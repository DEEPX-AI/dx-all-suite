# YOLO26 Benchmark Report

**Generated:** 2026-07-03 14:55:11 (Local)

## Test Timing

| # | Type | Start | End | Duration |
|---|------|-------|-----|----------|
| 1 | retry-failed | 2026-07-03 09:30:23 | 2026-07-03 14:55:11 | 5h 24m 47s |

## Executive Summary

### Object Detection

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n.dxnn | ON | 26.61 | 103.9 | 66.8 | 2 |
| yolo26n.dxnn | OFF | 24.11 | 157.6 | 84.8 | 2 |
| yolo26s.dxnn | ON | 34.53 | 92.7 | 66.3 | 2 |
| yolo26s.dxnn | OFF | 32.67 | 91.7 | 85.2 | 2 |
| yolo26m.dxnn | ON | 43.32 | 62.6 | 62.9 | 2 |
| yolo26m.dxnn | OFF | 40.76 | 62.4 | 63.2 | 2 |
| yolo26l.dxnn | ON | 53.79 | 46.1 | 46.3 | 1 |
| yolo26l.dxnn | OFF | 51.02 | 46.1 | 46.5 | 1 |
| yolo26x.dxnn | ON | 86.08 | 27.3 | 27.9 | — |
| yolo26x.dxnn | OFF | 83.38 | 27.3 | 28.2 | — |

### Pose Estimation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-pose.dxnn | ON | 22.47 | 152.9 | 81.5 | 2 |
| yolo26n-pose.dxnn | OFF | 20.75 | 155.4 | 121.2 | 4 |
| yolo26s-pose.dxnn | ON | 30.98 | 88.6 | 81.1 | 2 |
| yolo26s-pose.dxnn | OFF | 29.82 | 88.9 | 88.6 | 3 |
| yolo26m-pose.dxnn | ON | 40.03 | 60.9 | 61.7 | 2 |
| yolo26m-pose.dxnn | OFF | 38.39 | 60.9 | 62.1 | 2 |
| yolo26l-pose.dxnn | ON | 50.32 | 45.3 | 46.2 | 1 |
| yolo26l-pose.dxnn | OFF | 48.53 | 45.2 | 45.8 | 1 |
| yolo26x-pose.dxnn | ON | 82.90 | 27.0 | 27.3 | — |
| yolo26x-pose.dxnn | OFF | 81.23 | 27.0 | 27.8 | — |

### Segmentation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-seg.dxnn | ON | 41.63 | 66.5 | 46.3 | 1 |
| yolo26n-seg.dxnn | OFF | 39.04 | 95.8 | 61.7 | 2 |
| yolo26s-seg.dxnn | ON | 53.58 | 65.7 | 44.8 | 1 |
| yolo26s-seg.dxnn | OFF | 50.21 | 70.9 | 58.8 | 1 |
| yolo26m-seg.dxnn | ON | 70.31 | 46.7 | 43.4 | 1 |
| yolo26m-seg.dxnn | OFF | 66.22 | 46.3 | 45.1 | 1 |
| yolo26l-seg.dxnn | ON | 79.26 | 36.7 | 34.4 | 1 |
| yolo26l-seg.dxnn | OFF | 79.02 | 36.6 | 34.1 | 1 |
| yolo26x-seg.dxnn | ON | 128.27 | 21.6 | 17.4 | — |
| yolo26x-seg.dxnn | OFF | 121.52 | 21.2 | 17.1 | — |

### Oriented BBox (OBB)

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-obb.dxnn | ON | 44.40 | 51.8 | 51.8 | 1 |
| yolo26n-obb.dxnn | OFF | 43.33 | 52.0 | 52.0 | 1 |
| yolo26s-obb.dxnn | ON | 66.17 | 30.1 | 30.1 | 1 |
| yolo26s-obb.dxnn | OFF | 64.69 | 30.1 | 30.3 | 1 |
| yolo26m-obb.dxnn | ON | 87.17 | 21.8 | 22.0 | — |
| yolo26m-obb.dxnn | OFF | 85.11 | 21.7 | 22.1 | — |
| yolo26l-obb.dxnn | ON | 113.87 | 15.9 | 16.3 | — |
| yolo26l-obb.dxnn | OFF | 112.09 | 15.9 | 16.3 | — |
| yolo26x-obb.dxnn | ON | 198.74 | 9.6 | 9.2 | — |
| yolo26x-obb.dxnn | OFF | 196.61 | 9.6 | 9.2 | — |

### Classification

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-cls.dxnn | ON | 1.35 | 3039.2 | 187.9 | — |
| yolo26n-cls.dxnn | OFF | 1.34 | 3033.2 | 188.5 | — |
| yolo26s-cls.dxnn | ON | 2.14 | 1562.8 | 187.9 | — |
| yolo26s-cls.dxnn | OFF | 2.13 | 1562.3 | 188.0 | — |
| yolo26m-cls.dxnn | ON | 2.91 | 1023.2 | 188.3 | — |
| yolo26m-cls.dxnn | OFF | 2.91 | 1024.7 | 188.2 | — |
| yolo26l-cls.dxnn | ON | 4.19 | 686.0 | 187.5 | — |
| yolo26l-cls.dxnn | OFF | 4.26 | 687.3 | 187.7 | — |
| yolo26x-cls.dxnn | ON | 7.41 | 330.2 | 187.3 | — |
| yolo26x-cls.dxnn | OFF | 7.44 | 331.3 | 187.8 | — |

## Environment

| Item | Value |
|------|-------|
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
| NPU Memory | LPDDR4 4200 Mbps, 1.92GiB |
| NPU Board | M.2, Rev 0.0 |
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
| yolo26n.dxnn | 103.9 ±1.2 | 196 | 37.7 | 69.3 | 52~56 | 1000 | ok |
| yolo26s.dxnn | 92.7 ±0.3 | 141 | 91.6 | 100.0 | 58~60 | 1000 | ok |
| yolo26m.dxnn | 62.6 ±0.1 | 89 | 90.4 | 100.0 | 63~67 | 1000 | ok |
| yolo26l.dxnn | 46.1 ±0.1 | 66 | 89.4 | 100.0 | 62~66 | 1000 | ok |
| yolo26x.dxnn | 27.3 ±0.0 | 41 | 88.8 | 100.0 | 66~71 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n.dxnn | 157.6 ±3.1 | 109 | 85.6 | 100.0 | 59~61 | 1000 | ok |
| yolo26s.dxnn | 91.7 ±0.4 | 63 | 91.2 | 100.0 | 59~62 | 1000 | ok |
| yolo26m.dxnn | 62.4 ±0.0 | 47 | 91.4 | 100.0 | 64~68 | 1000 | ok |
| yolo26l.dxnn | 46.1 ±0.1 | 36 | 90.7 | 100.0 | 62~65 | 1000 | ok |
| yolo26x.dxnn | 27.3 ±0.0 | 20 | 89.7 | 100.0 | 66~70 | 1000 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-pose.dxnn | 152.9 ±0.6 | 187 | 81.8 | 93.5 | 59~61 | 1000 | ok |
| yolo26s-pose.dxnn | 88.6 ±0.3 | 86 | 91.5 | 100.0 | 63~67 | 1000 | ok |
| yolo26m-pose.dxnn | 60.9 ±0.3 | 59 | 91.0 | 100.0 | 67~73 | 1000 | ok |
| yolo26l-pose.dxnn | 45.3 ±0.1 | 45 | 91.8 | 100.0 | 67~71 | 1000 | ok |
| yolo26x-pose.dxnn | 27.0 ±0.1 | 27 | 89.5 | 100.0 | 70~75 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-pose.dxnn | 155.4 ±0.2 | 75 | 90.9 | 100.0 | 62~65 | 1000 | ok |
| yolo26s-pose.dxnn | 88.9 ±0.3 | 42 | 90.8 | 100.0 | 62~64 | 1000 | ok |
| yolo26m-pose.dxnn | 60.9 ±0.6 | 32 | 89.8 | 100.0 | 67~72 | 1000 | ok |
| yolo26l-pose.dxnn | 45.2 ±0.0 | 21 | 92.0 | 100.0 | 68~73 | 1000 | ok |
| yolo26x-pose.dxnn | 27.0 ±0.1 | 13 | 88.8 | 100.0 | 67~72 | 1000 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-seg.dxnn | 66.5 ±0.2 | 249 | 28.0 | 76.3 | 49~52 | 1000 | ok |
| yolo26s-seg.dxnn | 65.7 ±0.3 | 230 | 70.1 | 85.7 | 61~64 | 1000 | ok |
| yolo26m-seg.dxnn | 46.7 ±0.2 | 120 | 88.6 | 100.0 | 70~76 | 1000 | ok |
| yolo26l-seg.dxnn | 36.7 ±0.1 | 93 | 90.0 | 100.0 | 70~77 | 1000 | ok |
| yolo26x-seg.dxnn | 21.6 ±0.3 | 58 | 86.7 | 100.0 | 73~80 | 800~1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-seg.dxnn | 95.8 ±0.0 | 126 | 47.4 | 79.9 | 57~58 | 1000 | ok |
| yolo26s-seg.dxnn | 70.9 ±0.3 | 101 | 90.4 | 100.0 | 63~67 | 1000 | ok |
| yolo26m-seg.dxnn | 46.3 ±0.2 | 64 | 91.7 | 100.0 | 70~76 | 1000 | ok |
| yolo26l-seg.dxnn | 36.6 ±0.1 | 55 | 88.5 | 100.0 | 71~77 | 1000 | ok |
| yolo26x-seg.dxnn | 21.2 ±0.2 | 33 | 88.7 | 100.0 | 74~81 | 800~1000 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-obb.dxnn | 51.8 ±0.2 | 57 | 90.9 | 100.0 | 62~65 | 1000 | ok |
| yolo26s-obb.dxnn | 30.1 ±0.0 | 34 | 88.2 | 100.0 | 63~67 | 1000 | ok |
| yolo26m-obb.dxnn | 21.8 ±0.1 | 25 | 88.6 | 100.0 | 65~69 | 1000 | ok |
| yolo26l-obb.dxnn | 15.9 ±0.0 | 18 | 88.0 | 100.0 | 64~67 | 1000 | ok |
| yolo26x-obb.dxnn | 9.6 ±0.0 | 11 | 85.9 | 100.0 | 70~74 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-obb.dxnn | 52.0 ±0.1 | 30 | 91.4 | 100.0 | 63~67 | 1000 | ok |
| yolo26s-obb.dxnn | 30.1 ±0.1 | 16 | 88.3 | 100.0 | 61~63 | 1000 | ok |
| yolo26m-obb.dxnn | 21.7 ±0.1 | 13 | 91.3 | 100.0 | 65~69 | 1000 | ok |
| yolo26l-obb.dxnn | 15.9 ±0.0 | 9 | 87.8 | 100.0 | 66~70 | 1000 | ok |
| yolo26x-obb.dxnn | 9.6 ±0.0 | 5 | 86.4 | 100.0 | 72~77 | 1000 | ok |

#### Classification

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-cls.dxnn | 3039.2 ±0.9 | 55 | 89.2 | 97.8 | 58~60 | 1000 | ok |
| yolo26s-cls.dxnn | 1562.8 ±2.1 | 29 | 90.8 | 97.9 | 57~61 | 1000 | ok |
| yolo26m-cls.dxnn | 1023.2 ±2.5 | 20 | 91.3 | 98.5 | 64~70 | 1000 | ok |
| yolo26l-cls.dxnn | 686.0 ±2.4 | 13 | 90.0 | 99.2 | 63~67 | 1000 | ok |
| yolo26x-cls.dxnn | 330.2 ±1.1 | 7 | 90.2 | 100.0 | 65~71 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-cls.dxnn | 3033.2 ±1.0 | 55 | 89.5 | 97.7 | 53~57 | 1000 | ok |
| yolo26s-cls.dxnn | 1562.3 ±2.1 | 29 | 89.9 | 98.4 | 58~61 | 1000 | ok |
| yolo26m-cls.dxnn | 1024.7 ±2.1 | 20 | 89.7 | 98.6 | 62~69 | 1000 | ok |
| yolo26l-cls.dxnn | 687.3 ±0.5 | 13 | 90.1 | 98.9 | 64~67 | 1000 | ok |
| yolo26x-cls.dxnn | 331.3 ±1.4 | 7 | 89.8 | 99.9 | 65~70 | 1000 | ok |

### Latency (Single-Core, Sync)

#### Object Detection

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n.dxnn | 37.6 | 26.61 | 24.03 | 2.57 | 44 | ok |
| yolo26s.dxnn | 29.0 | 34.53 | 32.03 | 2.50 | 50 | ok |
| yolo26m.dxnn | 23.1 | 43.32 | 40.76 | 2.56 | 52 | ok |
| yolo26l.dxnn | 18.6 | 53.79 | 51.24 | 2.54 | 53 | ok |
| yolo26x.dxnn | 11.6 | 86.08 | 83.44 | 2.64 | 55 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n.dxnn | 41.5 | 24.11 | 24.11 | 52 | ok |
| yolo26s.dxnn | 30.6 | 32.67 | 32.67 | 52 | ok |
| yolo26m.dxnn | 24.5 | 40.76 | 40.76 | 53 | ok |
| yolo26l.dxnn | 19.6 | 51.02 | 51.02 | 52 | ok |
| yolo26x.dxnn | 12.0 | 83.38 | 83.38 | 54 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-pose.dxnn | 44.5 | 22.47 | 20.91 | 1.56 | 52 | ok |
| yolo26s-pose.dxnn | 32.3 | 30.98 | 29.44 | 1.54 | 53 | ok |
| yolo26m-pose.dxnn | 25.0 | 40.03 | 38.51 | 1.52 | 54 | ok |
| yolo26l-pose.dxnn | 19.9 | 50.32 | 48.76 | 1.56 | 55 | ok |
| yolo26x-pose.dxnn | 12.1 | 82.90 | 81.32 | 1.58 | 56 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-pose.dxnn | 48.2 | 20.75 | 20.75 | 53 | ok |
| yolo26s-pose.dxnn | 33.5 | 29.82 | 29.82 | 53 | ok |
| yolo26m-pose.dxnn | 26.1 | 38.39 | 38.39 | 55 | ok |
| yolo26l-pose.dxnn | 20.6 | 48.53 | 48.53 | 56 | ok |
| yolo26x-pose.dxnn | 12.3 | 81.23 | 81.23 | 56 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-seg.dxnn | 24.0 | 41.63 | 38.54 | 3.09 | 48 | ok |
| yolo26s-seg.dxnn | 18.7 | 53.58 | 50.42 | 3.17 | 51 | ok |
| yolo26m-seg.dxnn | 14.2 | 70.31 | 67.05 | 3.26 | 54 | ok |
| yolo26l-seg.dxnn | 12.6 | 79.26 | 76.11 | 3.16 | 55 | ok |
| yolo26x-seg.dxnn | 7.8 | 128.27 | 125.11 | 3.17 | 57 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-seg.dxnn | 25.6 | 39.04 | 39.04 | 51 | ok |
| yolo26s-seg.dxnn | 19.9 | 50.21 | 50.21 | 52 | ok |
| yolo26m-seg.dxnn | 15.1 | 66.22 | 66.22 | 54 | ok |
| yolo26l-seg.dxnn | 12.7 | 79.02 | 79.02 | 56 | ok |
| yolo26x-seg.dxnn | 8.2 | 121.52 | 121.52 | 58 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-obb.dxnn | 22.5 | 44.40 | 42.56 | 1.84 | 54 | ok |
| yolo26s-obb.dxnn | 15.1 | 66.17 | 64.44 | 1.73 | 55 | ok |
| yolo26m-obb.dxnn | 11.5 | 87.17 | 85.39 | 1.78 | 56 | ok |
| yolo26l-obb.dxnn | 8.8 | 113.87 | 112.08 | 1.78 | 55 | ok |
| yolo26x-obb.dxnn | 5.0 | 198.74 | 196.88 | 1.86 | 60 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-obb.dxnn | 23.1 | 43.33 | 43.33 | 54 | ok |
| yolo26s-obb.dxnn | 15.5 | 64.69 | 64.69 | 54 | ok |
| yolo26m-obb.dxnn | 11.7 | 85.11 | 85.11 | 56 | ok |
| yolo26l-obb.dxnn | 8.9 | 112.09 | 112.09 | 56 | ok |
| yolo26x-obb.dxnn | 5.1 | 196.61 | 196.61 | 61 | ok |

#### Classification

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-cls.dxnn | 740.6 | 1.35 | 1.35 | N/A | 53 | ok |
| yolo26s-cls.dxnn | 467.0 | 2.14 | 2.14 | N/A | 48 | ok |
| yolo26m-cls.dxnn | 343.2 | 2.91 | 2.91 | N/A | 51 | ok |
| yolo26l-cls.dxnn | 238.8 | 4.19 | 4.19 | N/A | 52 | ok |
| yolo26x-cls.dxnn | 134.9 | 7.41 | 7.41 | N/A | 53 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-cls.dxnn | 744.7 | 1.34 | 1.34 | 44 | ok |
| yolo26s-cls.dxnn | 470.3 | 2.13 | 2.13 | 51 | ok |
| yolo26m-cls.dxnn | 343.4 | 2.91 | 2.91 | 48 | ok |
| yolo26l-cls.dxnn | 234.9 | 4.26 | 4.26 | 53 | ok |
| yolo26x-cls.dxnn | 134.4 | 7.44 | 7.44 | 53 | ok |

## E2E Pipeline (Single-Stream)

### Object Detection

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | avdec_h264 | 3455 | 3 | 66.8 ±0.2 | 51.71 | 330 | 27.0 | 55.1 | 54 | 1000 | 310 | ok |
| yolo26s.dxnn | avdec_h264 | 3455 | 3 | 66.3 ±0.1 | 52.14 | 313 | 54.1 | 78.3 | 48~49 | 1000 | 323 | ok |
| yolo26m.dxnn | avdec_h264 | 3455 | 3 | 62.9 ±0.1 | 54.90 | 235 | 91.5 | 100.0 | 69~71 | 1000 | 345 | ok |
| yolo26l.dxnn | avdec_h264 | 3455 | 3 | 46.3 ±0.1 | 74.56 | 147 | 94.1 | 100.0 | 69~71 | 1000 | 353 | ok |
| yolo26x.dxnn | avdec_h264 | 3455 | 2/3 | 27.9 ±0.4 | 124.08 | 81 | 95.3 | 100.0 | 69~78 | 1000 | 417 | partial |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | avdec_h264 | 3455 | 3 | 84.8 ±0.5 | 40.74 | 310 | 29.4 | 78.4 | 54~55 | 1000 | 338 | ok |
| yolo26s.dxnn | avdec_h264 | 3455 | 3 | 85.2 ±0.6 | 40.57 | 310 | 72.6 | 88.0 | 60~61 | 1000 | 353 | ok |
| yolo26m.dxnn | avdec_h264 | 3455 | 3 | 63.2 ±0.2 | 54.66 | 203 | 93.6 | 100.0 | 70~73 | 1000 | 355 | ok |
| yolo26l.dxnn | avdec_h264 | 3455 | 3 | 46.5 ±0.1 | 74.22 | 150 | 94.6 | 100.0 | 65~69 | 1000 | 367 | ok |
| yolo26x.dxnn | avdec_h264 | 3455 | 3 | 28.2 ±0.1 | 122.70 | 90 | 94.8 | 100.0 | 77~79 | 800~1000 | 430 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n.dxnn | 66.8 | 84.8 | -18.0 | -21.2% |
| yolo26s.dxnn | 66.3 | 85.2 | -18.9 | -22.2% |
| yolo26m.dxnn | 62.9 | 63.2 | -0.3 | -0.4% |
| yolo26l.dxnn | 46.3 | 46.5 | -0.2 | -0.5% |
| yolo26x.dxnn | 27.9 | 28.2 | -0.3 | -1.1% |

### Pose Estimation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | avdec_h264 | 3455 | 3 | 81.5 ±0.2 | 42.41 | 339 | 35.7 | 62.8 | 48~52 | 1000 | 298 | ok |
| yolo26s-pose.dxnn | avdec_h264 | 3455 | 3 | 81.1 ±0.2 | 42.58 | 306 | 75.2 | 92.0 | 66~67 | 1000 | 316 | ok |
| yolo26m-pose.dxnn | avdec_h264 | 3455 | 3 | 61.7 ±0.4 | 55.97 | 163 | 92.7 | 100.0 | 76~79 | 1000 | 337 | ok |
| yolo26l-pose.dxnn | avdec_h264 | 3455 | 3 | 46.2 ±0.2 | 74.71 | 116 | 93.7 | 100.0 | 78~80 | 1000 | 347 | ok |
| yolo26x-pose.dxnn | avdec_h264 | 3455 | 3 | 27.3 ±0.1 | 126.40 | 71 | 95.3 | 100.0 | 81 | 800~1000 | 408 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | avdec_h264 | 3455 | 3 | 121.2 ±0.2 | 28.50 | 313 | 56.2 | 79.1 | 62~63 | 1000 | 289 | ok |
| yolo26s-pose.dxnn | avdec_h264 | 3455 | 3 | 88.6 ±0.8 | 39.00 | 176 | 92.1 | 100.0 | 54~65 | 1000 | 305 | ok |
| yolo26m-pose.dxnn | avdec_h264 | 3455 | 3 | 62.1 ±0.3 | 55.59 | 118 | 93.4 | 100.0 | 76~79 | 1000 | 327 | ok |
| yolo26l-pose.dxnn | avdec_h264 | 3455 | 3 | 45.8 ±0.6 | 75.46 | 91 | 93.7 | 100.0 | 80~83 | 600~1000 | 337 | ok |
| yolo26x-pose.dxnn | avdec_h264 | 3455 | 3 | 27.8 ±0.0 | 124.52 | 55 | 95.3 | 100.0 | 79 | 1000 | 399 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-pose.dxnn | 81.5 | 121.2 | -39.7 | -32.8% |
| yolo26s-pose.dxnn | 81.1 | 88.6 | -7.5 | -8.4% |
| yolo26m-pose.dxnn | 61.7 | 62.1 | -0.4 | -0.7% |
| yolo26l-pose.dxnn | 46.2 | 45.8 | +0.5 | +1.0% |
| yolo26x-pose.dxnn | 27.3 | 27.8 | -0.4 | -1.5% |

### Segmentation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | avdec_h264 | 3455 | 3 | 46.3 ±0.1 | 74.66 | 327 | 23.8 | 50.6 | 54~56 | 1000 | 408 | ok |
| yolo26s-seg.dxnn | avdec_h264 | 3455 | 3 | 44.8 ±0.2 | 77.05 | 306 | 44.6 | 74.1 | 61 | 1000 | 424 | ok |
| yolo26m-seg.dxnn | avdec_h264 | 3455 | 3 | 43.4 ±0.5 | 79.53 | 250 | 81.4 | 99.4 | 80~81 | 800~1000 | 446 | ok |
| yolo26l-seg.dxnn | avdec_h264 | 3455 | 3 | 34.4 ±0.8 | 100.53 | 155 | 91.9 | 100.0 | 82~83 | 600~1000 | 459 | ok |
| yolo26x-seg.dxnn | avdec_h264 | 3455 | 3 | 17.4 ±0.0 | 198.61 | 79 | 92.8 | 100.0 | 82~83 | 300~1000 | 525 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | avdec_h264 | 3455 | 3 | 61.7 ±0.5 | 55.99 | 354 | 26.7 | 72.1 | 52~53 | 1000 | 450 | ok |
| yolo26s-seg.dxnn | avdec_h264 | 3455 | 3 | 58.8 ±0.3 | 58.73 | 337 | 63.8 | 85.2 | 65~66 | 1000 | 464 | ok |
| yolo26m-seg.dxnn | avdec_h264 | 3455 | 3 | 45.1 ±1.1 | 76.68 | 201 | 93.1 | 100.0 | 81~82 | 600~1000 | 464 | ok |
| yolo26l-seg.dxnn | avdec_h264 | 3455 | 3 | 34.1 ±0.5 | 101.16 | 153 | 92.8 | 100.0 | 82~83 | 400~1000 | 478 | ok |
| yolo26x-seg.dxnn | avdec_h264 | 3455 | 3 | 17.1 ±0.2 | 201.67 | 76 | 93.4 | 100.0 | 83 | 400~1000 | 538 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-seg.dxnn | 46.3 | 61.7 | -15.4 | -25.0% |
| yolo26s-seg.dxnn | 44.8 | 58.8 | -14.0 | -23.8% |
| yolo26m-seg.dxnn | 43.4 | 45.1 | -1.6 | -3.6% |
| yolo26l-seg.dxnn | 34.4 | 34.1 | +0.2 | +0.6% |
| yolo26x-seg.dxnn | 17.4 | 17.1 | +0.3 | +1.6% |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | avdec_h264 | 2640 | 3 | 51.8 ±0.2 | 50.99 | 174 | 92.5 | 100.0 | 61~68 | 1000 | 325 | ok |
| yolo26s-obb.dxnn | avdec_h264 | 2640 | 3 | 30.1 ±0.3 | 87.72 | 97 | 94.9 | 100.0 | 59~73 | 1000 | 340 | ok |
| yolo26m-obb.dxnn | avdec_h264 | 2640 | 3 | 22.0 ±0.1 | 119.78 | 71 | 93.7 | 100.0 | 67~75 | 1000 | 365 | ok |
| yolo26l-obb.dxnn | avdec_h264 | 2640 | 3 | 16.3 ±0.1 | 162.22 | 53 | 93.9 | 100.0 | 75~77 | 1000 | 374 | ok |
| yolo26x-obb.dxnn | avdec_h264 | 2640 | 3 | 9.2 ±0.1 | 287.43 | 32 | 92.6 | 100.0 | 82 | 400~1000 | 443 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | avdec_h264 | 2640 | 3 | 52.0 ±0.1 | 50.76 | 161 | 92.8 | 100.0 | 69~73 | 1000 | 326 | ok |
| yolo26s-obb.dxnn | avdec_h264 | 2640 | 3 | 30.3 ±0.1 | 87.25 | 94 | 95.2 | 100.0 | 65~66 | 1000 | 339 | ok |
| yolo26m-obb.dxnn | avdec_h264 | 2640 | 3 | 22.1 ±0.2 | 119.50 | 70 | 94.5 | 100.0 | 65~76 | 1000 | 359 | ok |
| yolo26l-obb.dxnn | avdec_h264 | 2640 | 3 | 16.3 ±0.1 | 162.11 | 52 | 93.8 | 100.0 | 75~79 | 1000 | 376 | ok |
| yolo26x-obb.dxnn | avdec_h264 | 2640 | 3 | 9.2 ±0.4 | 286.32 | 31 | 93.4 | 100.0 | 81~84 | 400~1000 | 441 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-obb.dxnn | 51.8 | 52.0 | -0.2 | -0.5% |
| yolo26s-obb.dxnn | 30.1 | 30.3 | -0.2 | -0.5% |
| yolo26m-obb.dxnn | 22.0 | 22.1 | -0.1 | -0.2% |
| yolo26l-obb.dxnn | 16.3 | 16.3 | -0.0 | -0.1% |
| yolo26x-obb.dxnn | 9.2 | 9.2 | -0.0 | -0.3% |

### Classification

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-cls.dxnn | avdec_h264 | 3455 | 2/3 | 187.9 ±0.1 | 18.39 | 276 | 4.5 | 15.0 | 44 | 1000 | 197 | partial |
| yolo26s-cls.dxnn | avdec_h264 | 3455 | 3 | 187.9 ±0.1 | 18.39 | 275 | 8.9 | 28.6 | 51~53 | 1000 | 221 | ok |
| yolo26m-cls.dxnn | avdec_h264 | 3455 | 3 | 188.3 ±0.5 | 18.35 | 276 | 13.3 | 37.8 | 47~48 | 1000 | 214 | ok |
| yolo26l-cls.dxnn | avdec_h264 | 3455 | 3 | 187.5 ±0.4 | 18.42 | 275 | 21.0 | 48.7 | 56~57 | 1000 | 220 | ok |
| yolo26x-cls.dxnn | avdec_h264 | 3455 | 3 | 187.3 ±0.6 | 18.44 | 274 | 41.8 | 69.3 | 63 | 1000 | 266 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-cls.dxnn | avdec_h264 | 3455 | 3 | 188.5 ±0.5 | 18.33 | 277 | 4.8 | 15.7 | 49~50 | 1000 | 197 | ok |
| yolo26s-cls.dxnn | avdec_h264 | 3455 | 3 | 188.0 ±0.9 | 18.38 | 275 | 8.9 | 27.8 | 51~53 | 1000 | 205 | ok |
| yolo26m-cls.dxnn | avdec_h264 | 3455 | 3 | 188.2 ±0.2 | 18.36 | 276 | 13.1 | 36.7 | 56~58 | 1000 | 215 | ok |
| yolo26l-cls.dxnn | avdec_h264 | 3455 | 3 | 187.7 ±0.2 | 18.41 | 274 | 20.8 | 49.6 | 56~57 | 1000 | 220 | ok |
| yolo26x-cls.dxnn | avdec_h264 | 3455 | 3 | 187.8 ±0.9 | 18.40 | 273 | 42.2 | 68.7 | 63 | 1000 | 253 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-cls.dxnn | 187.9 | 188.5 | -0.7 | -0.4% |
| yolo26s-cls.dxnn | 187.9 | 188.0 | -0.1 | -0.0% |
| yolo26m-cls.dxnn | 188.3 | 188.2 | +0.1 | +0.1% |
| yolo26l-cls.dxnn | 187.5 | 187.7 | -0.1 | -0.1% |
| yolo26x-cls.dxnn | 187.3 | 187.8 | -0.5 | -0.3% |

## E2E Pipeline (Multi-Stream)

### Object Detection

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | 2 | 3 | 66.5 ±0.1 | 33.3 | 330 | 27.4 | 57.8 | 55 | 1000 | 443 | ok |
| yolo26n.dxnn | 3 | 3 | 66.0 ±1.1 | 22.0 | 329 | 27.4 | 55.9 | 56 | 1000 | 544 | ok |
| yolo26s.dxnn | 2 | 3 | 66.4 ±0.3 | 33.2 | 316 | 54.6 | 79.3 | 57~58 | 1000 | 458 | ok |
| yolo26s.dxnn | 3 | 3 | 66.5 ±0.1 | 22.1 | 316 | 54.9 | 79.1 | 58~60 | 1000 | 559 | ok |
| yolo26m.dxnn | 2 | 3 | 63.0 ±0.1 | 31.5 | 228 | 94.9 | 100.0 | 70~71 | 1000 | 479 | ok |
| yolo26m.dxnn | 3 | 3 | 63.0 ±0.1 | 21.0 | 240 | 95.0 | 100.0 | 72~73 | 1000 | 579 | ok |
| yolo26l.dxnn | 1 | 3 | 46.3 ±0.1 | 46.3 | 147 | 94.1 | 100.0 | 69~71 | 1000 | 353 | ok |
| yolo26l.dxnn | 2 | 3 | 46.4 ±0.1 | 23.2 | 147 | 95.9 | 100.0 | 69~70 | 1000 | 487 | ok |
| yolo26x.dxnn | 1 | 2/3 | 27.9 ±0.4 | 27.9 | 81 | 95.3 | 100.0 | 69~78 | 1000 | 417 | partial |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | 2 | 3 | 84.7 ±0.5 | 42.4 | 308 | 30.1 | 78.4 | 54 | 1000 | 470 | ok |
| yolo26n.dxnn | 3 | 3 | 84.9 ±0.5 | 28.3 | 305 | 30.5 | 78.2 | 49~54 | 1000 | 571 | ok |
| yolo26s.dxnn | 2 | 3 | 85.4 ±0.6 | 42.7 | 307 | 75.7 | 87.8 | 62~65 | 1000 | 487 | ok |
| yolo26s.dxnn | 3 | 3 | 84.9 ±0.2 | 28.3 | 313 | 75.4 | 90.9 | 61~62 | 1000 | 586 | ok |
| yolo26m.dxnn | 2 | 3 | 62.8 ±0.5 | 31.4 | 205 | 96.0 | 100.0 | 66~72 | 1000 | 493 | ok |
| yolo26m.dxnn | 3 | 3 | 63.4 ±0.1 | 21.1 | 209 | 96.7 | 100.0 | 73 | 1000 | 594 | ok |
| yolo26l.dxnn | 1 | 3 | 46.5 ±0.1 | 46.5 | 150 | 94.6 | 100.0 | 65~69 | 1000 | 367 | ok |
| yolo26l.dxnn | 2 | 3 | 46.8 ±0.2 | 23.4 | 153 | 96.3 | 100.0 | 71~72 | 1000 | 501 | ok |
| yolo26x.dxnn | 1 | 3 | 28.2 ±0.1 | 28.2 | 90 | 94.8 | 100.0 | 77~79 | 800~1000 | 430 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n.dxnn | 2 | 33.3 | 2 | 42.4 |
| yolo26s.dxnn | 2 | 33.2 | 2 | 42.7 |
| yolo26m.dxnn | 2 | 31.5 | 2 | 31.4 |
| yolo26l.dxnn | 1 | 46.3 | 1 | 46.5 |

### Pose Estimation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | 2 | 3 | 81.2 ±0.3 | 40.6 | 338 | 36.5 | 64.9 | 55~56 | 1000 | 436 | ok |
| yolo26n-pose.dxnn | 3 | 3 | 80.7 ±0.9 | 26.9 | 337 | 36.4 | 64.7 | 57~58 | 1000 | 540 | ok |
| yolo26s-pose.dxnn | 2 | 3 | 81.3 ±0.2 | 40.6 | 311 | 77.1 | 92.1 | 68 | 1000 | 451 | ok |
| yolo26s-pose.dxnn | 3 | 3 | 81.7 ±0.5 | 27.2 | 311 | 78.2 | 92.9 | 67~68 | 1000 | 557 | ok |
| yolo26m-pose.dxnn | 2 | 3 | 61.7 ±0.2 | 30.8 | 162 | 95.6 | 100.0 | 81 | 800~1000 | 473 | ok |
| yolo26m-pose.dxnn | 3 | 3 | 62.0 ±0.1 | 20.6 | 161 | 97.1 | 100.0 | 80~81 | 800~1000 | 575 | ok |
| yolo26l-pose.dxnn | 1 | 3 | 46.2 ±0.2 | 46.2 | 116 | 93.7 | 100.0 | 78~80 | 1000 | 347 | ok |
| yolo26l-pose.dxnn | 2 | 3 | 46.1 ±0.2 | 23.1 | 122 | 96.1 | 100.0 | 81~82 | 800~1000 | 482 | ok |
| yolo26x-pose.dxnn | 1 | 3 | 27.3 ±0.1 | 27.3 | 71 | 95.3 | 100.0 | 81 | 800~1000 | 408 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | 4 | 3 | 122.1 ±0.9 | 30.5 | 352 | 63.7 | 83.8 | 65 | 1000 | 636 | ok |
| yolo26n-pose.dxnn | 5 | 3 | 122.9 ±0.5 | 24.6 | 353 | 64.8 | 82.6 | 67~68 | 1000 | 736 | ok |
| yolo26s-pose.dxnn | 2 | 3 | 89.8 ±0.1 | 44.9 | 194 | 94.1 | 100.0 | 68~71 | 1000 | 444 | ok |
| yolo26s-pose.dxnn | 3 | 3 | 90.0 ±0.3 | 30.0 | 194 | 95.4 | 100.0 | 74~77 | 1000 | 548 | ok |
| yolo26s-pose.dxnn | 4 | 3 | 90.5 ±0.1 | 22.6 | 191 | 96.1 | 100.0 | 76~80 | 1000 | 649 | ok |
| yolo26m-pose.dxnn | 2 | 3 | 62.3 ±0.0 | 31.1 | 125 | 96.5 | 100.0 | 77~81 | 800~1000 | 463 | ok |
| yolo26m-pose.dxnn | 3 | 3 | 61.7 ±0.5 | 20.6 | 127 | 96.8 | 100.0 | 68~80 | 1000 | 569 | ok |
| yolo26l-pose.dxnn | 1 | 3 | 45.8 ±0.6 | 45.8 | 91 | 93.7 | 100.0 | 80~83 | 600~1000 | 337 | ok |
| yolo26l-pose.dxnn | 2 | 3 | 42.6 ±1.2 | 21.3 | 90 | 95.2 | 100.0 | 82~84 | 400~1000 | 472 | ok |
| yolo26x-pose.dxnn | 1 | 3 | 27.8 ±0.0 | 27.8 | 55 | 95.3 | 100.0 | 79 | 1000 | 399 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-pose.dxnn | 2 | 40.6 | 4 | 30.5 |
| yolo26s-pose.dxnn | 2 | 40.6 | 3 | 30.0 |
| yolo26m-pose.dxnn | 2 | 30.8 | 2 | 31.1 |
| yolo26l-pose.dxnn | 1 | 46.2 | 1 | 45.8 |

### Segmentation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | 1 | 3 | 46.3 ±0.1 | 46.3 | 327 | 23.8 | 50.6 | 54~56 | 1000 | 408 | ok |
| yolo26n-seg.dxnn | 2 | 3 | 44.8 ±0.3 | 22.4 | 326 | 23.3 | 51.8 | 52~53 | 1000 | 550 | ok |
| yolo26s-seg.dxnn | 1 | 3 | 44.8 ±0.2 | 44.8 | 306 | 44.6 | 74.1 | 61 | 1000 | 424 | ok |
| yolo26s-seg.dxnn | 2 | 3 | 43.5 ±0.7 | 21.8 | 308 | 44.0 | 69.6 | 60~61 | 1000 | 570 | ok |
| yolo26m-seg.dxnn | 1 | 3 | 43.4 ±0.5 | 43.4 | 250 | 81.4 | 99.4 | 80~81 | 800~1000 | 446 | ok |
| yolo26m-seg.dxnn | 2 | 3 | 43.2 ±0.7 | 21.6 | 248 | 83.9 | 100.0 | 75~81 | 600~1000 | 589 | ok |
| yolo26l-seg.dxnn | 1 | 3 | 34.4 ±0.8 | 34.4 | 155 | 91.9 | 100.0 | 82~83 | 600~1000 | 459 | ok |
| yolo26l-seg.dxnn | 2 | 3 | 33.3 ±0.4 | 16.6 | 154 | 93.9 | 100.0 | 83~84 | 400~1000 | 597 | ok |
| yolo26x-seg.dxnn | 1 | 3 | 17.4 ±0.0 | 17.4 | 79 | 92.8 | 100.0 | 82~83 | 300~1000 | 525 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | 2 | 3 | 61.1 ±0.1 | 30.5 | 354 | 27.4 | 71.3 | 52~54 | 1000 | 591 | ok |
| yolo26n-seg.dxnn | 3 | 3 | 60.6 ±0.6 | 20.2 | 347 | 27.3 | 72.5 | 55 | 1000 | 701 | ok |
| yolo26s-seg.dxnn | 1 | 3 | 58.8 ±0.3 | 58.8 | 337 | 63.8 | 85.2 | 65~66 | 1000 | 464 | ok |
| yolo26s-seg.dxnn | 2 | 3 | 59.5 ±0.3 | 29.7 | 341 | 64.9 | 85.5 | 67 | 1000 | 606 | ok |
| yolo26m-seg.dxnn | 1 | 3 | 45.1 ±1.1 | 45.1 | 201 | 93.1 | 100.0 | 81~82 | 600~1000 | 464 | ok |
| yolo26m-seg.dxnn | 2 | 3 | 41.9 ±0.3 | 20.9 | 192 | 93.6 | 100.0 | 82 | 400~1000 | 611 | ok |
| yolo26l-seg.dxnn | 1 | 3 | 34.1 ±0.5 | 34.1 | 153 | 92.8 | 100.0 | 82~83 | 400~1000 | 478 | ok |
| yolo26l-seg.dxnn | 2 | 3 | 33.8 ±0.6 | 16.9 | 155 | 93.7 | 100.0 | 82~83 | 400~1000 | 620 | ok |
| yolo26x-seg.dxnn | 1 | 3 | 17.1 ±0.2 | 17.1 | 76 | 93.4 | 100.0 | 83 | 400~1000 | 538 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-seg.dxnn | 1 | 46.3 | 2 | 30.5 |
| yolo26s-seg.dxnn | 1 | 44.8 | 1 | 58.8 |
| yolo26m-seg.dxnn | 1 | 43.4 | 1 | 45.1 |
| yolo26l-seg.dxnn | 1 | 34.4 | 1 | 34.1 |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | 1 | 3 | 51.8 ±0.2 | 51.8 | 174 | 92.5 | 100.0 | 61~68 | 1000 | 325 | ok |
| yolo26n-obb.dxnn | 2 | 3 | 52.0 ±0.2 | 26.0 | 186 | 94.2 | 100.0 | 70~75 | 1000 | 460 | ok |
| yolo26s-obb.dxnn | 1 | 3 | 30.1 ±0.3 | 30.1 | 97 | 94.9 | 100.0 | 59~73 | 1000 | 340 | ok |
| yolo26s-obb.dxnn | 2 | 3 | 30.3 ±0.0 | 15.2 | 99 | 96.8 | 100.0 | 67~68 | 1000 | 475 | ok |
| yolo26m-obb.dxnn | 1 | 3 | 22.0 ±0.1 | 22.0 | 71 | 93.7 | 100.0 | 67~75 | 1000 | 365 | ok |
| yolo26l-obb.dxnn | 1 | 3 | 16.3 ±0.1 | 16.3 | 53 | 93.9 | 100.0 | 75~77 | 1000 | 374 | ok |
| yolo26x-obb.dxnn | 1 | 3 | 9.2 ±0.1 | 9.2 | 32 | 92.6 | 100.0 | 82 | 400~1000 | 443 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | 1 | 3 | 52.0 ±0.1 | 52.0 | 161 | 92.8 | 100.0 | 69~73 | 1000 | 326 | ok |
| yolo26n-obb.dxnn | 2 | 3 | 52.2 ±0.0 | 26.1 | 167 | 94.7 | 100.0 | 73~75 | 1000 | 458 | ok |
| yolo26s-obb.dxnn | 1 | 3 | 30.3 ±0.1 | 30.3 | 94 | 95.2 | 100.0 | 65~66 | 1000 | 339 | ok |
| yolo26s-obb.dxnn | 2 | 3 | 30.2 ±0.1 | 15.1 | 96 | 96.6 | 100.0 | 63~68 | 1000 | 473 | ok |
| yolo26m-obb.dxnn | 1 | 3 | 22.1 ±0.2 | 22.1 | 70 | 94.5 | 100.0 | 65~76 | 1000 | 359 | ok |
| yolo26l-obb.dxnn | 1 | 3 | 16.3 ±0.1 | 16.3 | 52 | 93.8 | 100.0 | 75~79 | 1000 | 376 | ok |
| yolo26x-obb.dxnn | 1 | 3 | 9.2 ±0.4 | 9.2 | 31 | 93.4 | 100.0 | 81~84 | 400~1000 | 441 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-obb.dxnn | 1 | 51.8 | 1 | 52.0 |
| yolo26s-obb.dxnn | 1 | 30.1 | 1 | 30.3 |

---
*Report generated by dx_stream benchmark tool*
