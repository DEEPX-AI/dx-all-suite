# YOLO26 Benchmark Report

**Generated:** 2026-07-02 04:34:31 (Local)

## Test Timing

| # | Type | Start | End | Duration |
|---|------|-------|-----|----------|
| 1 | run | 2026-07-01 11:20:36 | 2026-07-02 04:34:31 | 17h 13m 55s |

## Executive Summary

### Object Detection

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n.dxnn | ON | 36.94 | 96.2 | 61.9 | 2 |
| yolo26n.dxnn | OFF | 29.14 | 111.0 | 79.9 | 2 |
| yolo26s.dxnn | ON | 45.38 | 72.3 | 62.0 | 1 |
| yolo26s.dxnn | OFF | 38.81 | 72.7 | 71.4 | 2 |
| yolo26m.dxnn | ON | 55.12 | 52.5 | 52.6 | 1 |
| yolo26m.dxnn | OFF | 48.17 | 52.5 | 52.8 | 1 |
| yolo26l.dxnn | ON | 67.74 | 39.5 | 39.9 | 1 |
| yolo26l.dxnn | OFF | 59.22 | 39.6 | 39.9 | 1 |
| yolo26x.dxnn | ON | 103.67 | 23.4 | 18.0 | — |
| yolo26x.dxnn | OFF | 95.63 | 23.4 | 17.1 | — |

### Pose Estimation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-pose.dxnn | ON | 30.36 | 113.3 | 75.6 | 2 |
| yolo26n-pose.dxnn | OFF | 25.55 | 113.6 | 108.0 | 3 |
| yolo26s-pose.dxnn | ON | 40.44 | 70.8 | 71.0 | 2 |
| yolo26s-pose.dxnn | OFF | 35.59 | 71.0 | 70.6 | 2 |
| yolo26m-pose.dxnn | ON | 49.29 | 51.4 | 50.8 | 1 |
| yolo26m-pose.dxnn | OFF | 44.72 | 51.5 | 48.3 | 1 |
| yolo26l-pose.dxnn | ON | 62.63 | 39.0 | 38.8 | 1 |
| yolo26l-pose.dxnn | OFF | 56.71 | 39.0 | 34.9 | 1 |
| yolo26x-pose.dxnn | ON | 97.93 | 23.0 | 18.4 | — |
| yolo26x-pose.dxnn | OFF | 93.17 | 23.0 | 18.4 | — |

### Segmentation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-seg.dxnn | ON | 53.99 | 57.8 | 40.7 | 1 |
| yolo26n-seg.dxnn | OFF | 48.90 | 74.8 | 54.2 | 1 |
| yolo26s-seg.dxnn | ON | 70.68 | 52.6 | 40.8 | 1 |
| yolo26s-seg.dxnn | OFF | 58.00 | 57.1 | 52.7 | 1 |
| yolo26m-seg.dxnn | ON | 83.68 | 40.5 | 34.5 | 1 |
| yolo26m-seg.dxnn | OFF | 74.68 | 40.5 | 32.3 | 1 |
| yolo26l-seg.dxnn | ON | 96.09 | 32.3 | 26.4 | — |
| yolo26l-seg.dxnn | OFF | 85.47 | 32.3 | 26.4 | — |
| yolo26x-seg.dxnn | ON | 145.19 | 18.3 | 13.6 | — |
| yolo26x-seg.dxnn | OFF | 135.34 | 17.8 | 12.5 | — |

### Oriented BBox (OBB)

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-obb.dxnn | ON | 55.53 | 39.9 | 40.1 | 1 |
| yolo26n-obb.dxnn | OFF | 51.12 | 40.1 | 40.2 | 1 |
| yolo26s-obb.dxnn | ON | 80.61 | 24.9 | 25.2 | — |
| yolo26s-obb.dxnn | OFF | 76.04 | 24.8 | 25.2 | — |
| yolo26m-obb.dxnn | ON | 101.74 | 18.8 | 16.8 | — |
| yolo26m-obb.dxnn | OFF | 96.40 | 18.8 | 16.6 | — |
| yolo26l-obb.dxnn | ON | 130.10 | 14.1 | 13.6 | — |
| yolo26l-obb.dxnn | OFF | 125.33 | 14.1 | 12.9 | — |
| yolo26x-obb.dxnn | ON | 222.92 | 8.4 | 7.3 | — |
| yolo26x-obb.dxnn | OFF | 217.44 | 8.4 | 7.0 | — |

### Classification

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-cls.dxnn | ON | 1.57 | 2165.4 | 188.7 | — |
| yolo26n-cls.dxnn | OFF | 1.56 | 2164.7 | 188.4 | — |
| yolo26s-cls.dxnn | ON | 2.38 | 1273.5 | 188.2 | — |
| yolo26s-cls.dxnn | OFF | 2.40 | 1272.2 | 188.0 | — |
| yolo26m-cls.dxnn | ON | 2.94 | 1004.2 | 187.9 | — |
| yolo26m-cls.dxnn | OFF | 2.96 | 1005.8 | 188.4 | — |
| yolo26l-cls.dxnn | ON | 4.42 | 642.6 | 188.1 | — |
| yolo26l-cls.dxnn | OFF | 4.45 | 641.8 | 187.8 | — |
| yolo26x-cls.dxnn | ON | 8.06 | 297.7 | 187.5 | — |
| yolo26x-cls.dxnn | OFF | 8.05 | 297.4 | 188.1 | — |

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
| NPU Memory | LPDDR4 4200 Mbps, 1.92GiB |
| NPU Board | M.2, Rev 0.0 |
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
| yolo26n.dxnn | 96.2 ±0.4 | 218 | 51.4 | 89.0 | 57~62 | 1000 | ok |
| yolo26s.dxnn | 72.3 ±0.2 | 126 | 89.4 | 100.0 | 67~71 | 1000 | ok |
| yolo26m.dxnn | 52.5 ±0.1 | 79 | 90.3 | 100.0 | 69~75 | 1000 | ok |
| yolo26l.dxnn | 39.5 ±0.0 | 62 | 92.3 | 100.0 | 68~73 | 1000 | ok |
| yolo26x.dxnn | 23.4 ±0.1 | 37 | 88.8 | 100.0 | 73~78 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n.dxnn | 111.0 ±0.1 | 75 | 76.7 | 88.2 | 64~69 | 1000 | ok |
| yolo26s.dxnn | 72.7 ±0.1 | 62 | 91.5 | 100.0 | 67~72 | 1000 | ok |
| yolo26m.dxnn | 52.5 ±0.0 | 42 | 88.5 | 100.0 | 68~73 | 1000 | ok |
| yolo26l.dxnn | 39.6 ±0.0 | 31 | 88.3 | 100.0 | 69~73 | 1000 | ok |
| yolo26x.dxnn | 23.4 ±0.1 | 20 | 89.5 | 100.0 | 74~79 | 1000 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-pose.dxnn | 113.3 ±0.1 | 140 | 91.2 | 100.0 | 65~68 | 1000 | ok |
| yolo26s-pose.dxnn | 70.8 ±0.1 | 73 | 90.4 | 100.0 | 65~69 | 1000 | ok |
| yolo26m-pose.dxnn | 51.4 ±0.1 | 52 | 88.8 | 100.0 | 70~76 | 1000 | ok |
| yolo26l-pose.dxnn | 39.0 ±0.1 | 39 | 88.5 | 100.0 | 68~74 | 1000 | ok |
| yolo26x-pose.dxnn | 23.0 ±0.1 | 24 | 87.2 | 100.0 | 73~78 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-pose.dxnn | 113.6 ±0.1 | 64 | 92.4 | 100.0 | 64~68 | 1000 | ok |
| yolo26s-pose.dxnn | 71.0 ±0.1 | 39 | 92.1 | 100.0 | 66~71 | 1000 | ok |
| yolo26m-pose.dxnn | 51.5 ±0.1 | 29 | 90.1 | 100.0 | 71~76 | 1000 | ok |
| yolo26l-pose.dxnn | 39.0 ±0.1 | 21 | 89.2 | 100.0 | 71~78 | 1000 | ok |
| yolo26x-pose.dxnn | 23.0 ±0.1 | 13 | 88.5 | 100.0 | 73~80 | 1000 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-seg.dxnn | 57.8 ±0.2 | 278 | 31.5 | 68.2 | 60~61 | 1000 | ok |
| yolo26s-seg.dxnn | 52.6 ±0.1 | 203 | 70.6 | 88.8 | 64~68 | 1000 | ok |
| yolo26m-seg.dxnn | 40.5 ±0.1 | 109 | 88.3 | 100.0 | 73~81 | 800~1000 | ok |
| yolo26l-seg.dxnn | 32.3 ±0.1 | 78 | 89.2 | 100.0 | 73~81 | 1000 | ok |
| yolo26x-seg.dxnn | 18.3 ±0.8 | 48 | 84.0 | 100.0 | 77~82 | 600~1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-seg.dxnn | 74.8 ±0.0 | 128 | 48.5 | 80.2 | 62~65 | 1000 | ok |
| yolo26s-seg.dxnn | 57.1 ±0.1 | 92 | 81.3 | 95.5 | 67~73 | 1000 | ok |
| yolo26m-seg.dxnn | 40.5 ±0.1 | 59 | 90.5 | 100.0 | 75~82 | 1000 | ok |
| yolo26l-seg.dxnn | 32.3 ±0.1 | 47 | 88.0 | 100.0 | 74~81 | 1000 | ok |
| yolo26x-seg.dxnn | 17.8 ±1.4 | 30 | 86.0 | 100.0 | 78~83 | 600~1000 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-obb.dxnn | 39.9 ±0.1 | 47 | 90.1 | 100.0 | 65~69 | 1000 | ok |
| yolo26s-obb.dxnn | 24.9 ±0.1 | 30 | 90.2 | 100.0 | 66~70 | 1000 | ok |
| yolo26m-obb.dxnn | 18.8 ±0.0 | 22 | 87.8 | 100.0 | 69~76 | 1000 | ok |
| yolo26l-obb.dxnn | 14.1 ±0.1 | 17 | 87.4 | 100.0 | 73~78 | 1000 | ok |
| yolo26x-obb.dxnn | 8.4 ±0.0 | 10 | 86.5 | 100.0 | 75~80 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-obb.dxnn | 40.1 ±0.1 | 27 | 91.6 | 100.0 | 65~69 | 1000 | ok |
| yolo26s-obb.dxnn | 24.8 ±0.1 | 18 | 87.9 | 100.0 | 67~71 | 1000 | ok |
| yolo26m-obb.dxnn | 18.8 ±0.0 | 13 | 88.5 | 100.0 | 71~76 | 1000 | ok |
| yolo26l-obb.dxnn | 14.1 ±0.1 | 10 | 87.3 | 100.0 | 74~80 | 1000 | ok |
| yolo26x-obb.dxnn | 8.4 ±0.0 | 6 | 85.4 | 100.0 | 74~79 | 1000 | ok |

#### Classification

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-cls.dxnn | 2165.4 ±0.5 | 38 | 89.4 | 98.4 | 62~65 | 1000 | ok |
| yolo26s-cls.dxnn | 1273.5 ±1.8 | 24 | 91.6 | 99.0 | 63~66 | 1000 | ok |
| yolo26m-cls.dxnn | 1004.2 ±3.2 | 19 | 90.8 | 99.2 | 67~73 | 1000 | ok |
| yolo26l-cls.dxnn | 642.6 ±0.7 | 12 | 91.6 | 99.7 | 65~70 | 1000 | ok |
| yolo26x-cls.dxnn | 297.7 ±0.2 | 6 | 92.5 | 100.0 | 66~73 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-cls.dxnn | 2164.7 ±0.2 | 38 | 89.5 | 98.3 | 62~65 | 1000 | ok |
| yolo26s-cls.dxnn | 1272.2 ±1.9 | 24 | 90.6 | 99.1 | 63~66 | 1000 | ok |
| yolo26m-cls.dxnn | 1005.8 ±4.6 | 19 | 91.1 | 99.2 | 68~75 | 1000 | ok |
| yolo26l-cls.dxnn | 641.8 ±0.5 | 12 | 91.0 | 99.7 | 67~71 | 1000 | ok |
| yolo26x-cls.dxnn | 297.4 ±0.4 | 6 | 91.2 | 100.0 | 64~71 | 1000 | ok |

### Latency (Single-Core, Sync)

#### Object Detection

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n.dxnn | 27.1 | 36.94 | 29.02 | 7.92 | 47 | ok |
| yolo26s.dxnn | 22.0 | 45.38 | 38.25 | 7.13 | 56 | ok |
| yolo26m.dxnn | 18.1 | 55.12 | 47.41 | 7.71 | 56 | ok |
| yolo26l.dxnn | 14.8 | 67.74 | 60.00 | 7.75 | 57 | ok |
| yolo26x.dxnn | 9.6 | 103.67 | 95.67 | 8.01 | 60 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n.dxnn | 34.3 | 29.14 | 29.14 | 55 | ok |
| yolo26s.dxnn | 25.8 | 38.81 | 38.81 | 56 | ok |
| yolo26m.dxnn | 20.8 | 48.17 | 48.17 | 57 | ok |
| yolo26l.dxnn | 16.9 | 59.22 | 59.22 | 57 | ok |
| yolo26x.dxnn | 10.5 | 95.63 | 95.63 | 60 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-pose.dxnn | 32.9 | 30.36 | 25.52 | 4.84 | 55 | ok |
| yolo26s-pose.dxnn | 24.7 | 40.44 | 35.69 | 4.75 | 55 | ok |
| yolo26m-pose.dxnn | 20.3 | 49.29 | 44.78 | 4.52 | 57 | ok |
| yolo26l-pose.dxnn | 16.0 | 62.63 | 57.82 | 4.81 | 57 | ok |
| yolo26x-pose.dxnn | 10.2 | 97.93 | 93.20 | 4.73 | 61 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-pose.dxnn | 39.1 | 25.55 | 25.55 | 55 | ok |
| yolo26s-pose.dxnn | 28.1 | 35.59 | 35.59 | 56 | ok |
| yolo26m-pose.dxnn | 22.4 | 44.72 | 44.72 | 58 | ok |
| yolo26l-pose.dxnn | 17.6 | 56.71 | 56.71 | 58 | ok |
| yolo26x-pose.dxnn | 10.7 | 93.17 | 93.17 | 60 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-seg.dxnn | 18.5 | 53.99 | 44.94 | 9.06 | 55 | ok |
| yolo26s-seg.dxnn | 14.1 | 70.68 | 61.27 | 9.41 | 55 | ok |
| yolo26m-seg.dxnn | 12.0 | 83.68 | 74.11 | 9.57 | 57 | ok |
| yolo26l-seg.dxnn | 10.4 | 96.09 | 86.55 | 9.54 | 58 | ok |
| yolo26x-seg.dxnn | 6.9 | 145.19 | 135.58 | 9.61 | 61 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-seg.dxnn | 20.5 | 48.90 | 48.90 | 54 | ok |
| yolo26s-seg.dxnn | 17.2 | 58.00 | 58.00 | 56 | ok |
| yolo26m-seg.dxnn | 13.4 | 74.68 | 74.68 | 58 | ok |
| yolo26l-seg.dxnn | 11.7 | 85.47 | 85.47 | 59 | ok |
| yolo26x-seg.dxnn | 7.4 | 135.34 | 135.34 | 62 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-obb.dxnn | 18.0 | 55.53 | 50.34 | 5.19 | 57 | ok |
| yolo26s-obb.dxnn | 12.4 | 80.61 | 75.22 | 5.39 | 58 | ok |
| yolo26m-obb.dxnn | 9.8 | 101.74 | 96.49 | 5.25 | 60 | ok |
| yolo26l-obb.dxnn | 7.7 | 130.10 | 124.58 | 5.52 | 63 | ok |
| yolo26x-obb.dxnn | 4.5 | 222.92 | 217.37 | 5.55 | 65 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-obb.dxnn | 19.6 | 51.12 | 51.12 | 57 | ok |
| yolo26s-obb.dxnn | 13.2 | 76.04 | 76.04 | 58 | ok |
| yolo26m-obb.dxnn | 10.4 | 96.40 | 96.40 | 61 | ok |
| yolo26l-obb.dxnn | 8.0 | 125.33 | 125.33 | 63 | ok |
| yolo26x-obb.dxnn | 4.6 | 217.44 | 217.44 | 64 | ok |

#### Classification

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-cls.dxnn | 638.5 | 1.57 | 1.57 | N/A | 54 | ok |
| yolo26s-cls.dxnn | 420.8 | 2.38 | 2.38 | N/A | 53 | ok |
| yolo26m-cls.dxnn | 340.5 | 2.94 | 2.94 | N/A | 54 | ok |
| yolo26l-cls.dxnn | 226.0 | 4.42 | 4.42 | N/A | 55 | ok |
| yolo26x-cls.dxnn | 124.0 | 8.06 | 8.06 | N/A | 54 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-cls.dxnn | 639.3 | 1.56 | 1.56 | 54 | ok |
| yolo26s-cls.dxnn | 417.5 | 2.40 | 2.40 | 54 | ok |
| yolo26m-cls.dxnn | 337.9 | 2.96 | 2.96 | 54 | ok |
| yolo26l-cls.dxnn | 224.7 | 4.45 | 4.45 | 55 | ok |
| yolo26x-cls.dxnn | 124.2 | 8.05 | 8.05 | 50 | ok |

## E2E Pipeline (Single-Stream)

### Object Detection

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | avdec_h264 | 3455 | 3 | 61.9 ±0.1 | 55.80 | 340 | 33.3 | 62.2 | 54~62 | 1000 | 320 | ok |
| yolo26s.dxnn | avdec_h264 | 3455 | 3 | 62.0 ±0.3 | 55.74 | 315 | 65.1 | 86.3 | 72~73 | 1000 | 335 | ok |
| yolo26m.dxnn | avdec_h264 | 3455 | 3 | 52.6 ±0.0 | 65.73 | 187 | 93.1 | 100.0 | 78~81 | 1000 | 358 | ok |
| yolo26l.dxnn | avdec_h264 | 3455 | 3 | 39.9 ±0.0 | 86.70 | 121 | 94.9 | 100.0 | 80~82 | 1000 | 366 | ok |
| yolo26x.dxnn | avdec_h264 | 3455 | 3 | 18.0 ±0.1 | 192.01 | 56 | 91.8 | 100.0 | 84~85 | 300~1000 | 427 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | avdec_h264 | 3455 | 3 | 79.9 ±0.5 | 43.25 | 322 | 39.4 | 71.9 | 67~68 | 1000 | 351 | ok |
| yolo26s.dxnn | avdec_h264 | 3455 | 3 | 71.4 ±0.3 | 48.39 | 268 | 88.6 | 100.0 | 75~77 | 1000 | 350 | ok |
| yolo26m.dxnn | avdec_h264 | 3455 | 3 | 52.8 ±0.1 | 65.41 | 182 | 94.4 | 100.0 | 79~80 | 1000 | 363 | ok |
| yolo26l.dxnn | avdec_h264 | 3455 | 3 | 39.9 ±0.0 | 86.68 | 129 | 95.0 | 100.0 | 80~82 | 1000 | 373 | ok |
| yolo26x.dxnn | avdec_h264 | 3455 | 3 | 17.1 ±5.0 | 201.66 | 64 | 73.9 | 100.0 | 69~85 | 400~1000 | 430 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n.dxnn | 61.9 | 79.9 | -18.0 | -22.5% |
| yolo26s.dxnn | 62.0 | 71.4 | -9.4 | -13.2% |
| yolo26m.dxnn | 52.6 | 52.8 | -0.3 | -0.5% |
| yolo26l.dxnn | 39.9 | 39.9 | -0.0 | -0.0% |
| yolo26x.dxnn | 18.0 | 17.1 | +0.9 | +5.0% |

### Pose Estimation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | avdec_h264 | 3455 | 3 | 75.6 ±0.3 | 45.71 | 344 | 44.2 | 71.2 | 62~63 | 1000 | 309 | ok |
| yolo26s-pose.dxnn | avdec_h264 | 3455 | 3 | 71.0 ±0.1 | 48.65 | 214 | 93.7 | 100.0 | 71~73 | 1000 | 325 | ok |
| yolo26m-pose.dxnn | avdec_h264 | 3455 | 3 | 50.8 ±1.2 | 68.05 | 126 | 93.8 | 100.0 | 82~84 | 600~1000 | 347 | ok |
| yolo26l-pose.dxnn | avdec_h264 | 3455 | 3 | 38.8 ±0.4 | 89.09 | 96 | 95.1 | 100.0 | 82~84 | 800~1000 | 356 | ok |
| yolo26x-pose.dxnn | avdec_h264 | 3455 | 3 | 18.4 ±0.5 | 188.15 | 49 | 91.7 | 100.0 | 83~84 | 300~1000 | 420 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | avdec_h264 | 3455 | 3 | 108.0 ±0.6 | 32.00 | 295 | 80.9 | 94.9 | 53~60 | 1000 | 301 | ok |
| yolo26s-pose.dxnn | avdec_h264 | 3455 | 3 | 70.6 ±0.5 | 48.93 | 143 | 91.8 | 100.0 | 58~68 | 1000 | 312 | ok |
| yolo26m-pose.dxnn | avdec_h264 | 3455 | 3 | 48.3 ±3.3 | 71.55 | 99 | 93.4 | 100.0 | 83~85 | 400~1000 | 337 | ok |
| yolo26l-pose.dxnn | avdec_h264 | 3455 | 3 | 34.9 ±3.4 | 99.00 | 75 | 95.1 | 100.0 | 84~85 | 400~1000 | 343 | ok |
| yolo26x-pose.dxnn | avdec_h264 | 3455 | 3 | 18.4 ±1.0 | 187.68 | 42 | 92.4 | 100.0 | 84~85 | 300~1000 | 405 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-pose.dxnn | 75.6 | 108.0 | -32.4 | -30.0% |
| yolo26s-pose.dxnn | 71.0 | 70.6 | +0.4 | +0.6% |
| yolo26m-pose.dxnn | 50.8 | 48.3 | +2.5 | +5.1% |
| yolo26l-pose.dxnn | 38.8 | 34.9 | +3.9 | +11.1% |
| yolo26x-pose.dxnn | 18.4 | 18.4 | -0.1 | -0.3% |

### Segmentation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | avdec_h264 | 3455 | 3 | 40.7 ±0.8 | 84.82 | 338 | 25.6 | 60.5 | 59~61 | 1000 | 420 | ok |
| yolo26s-seg.dxnn | avdec_h264 | 3455 | 3 | 40.8 ±0.5 | 84.64 | 323 | 47.8 | 73.2 | 67~69 | 1000 | 435 | ok |
| yolo26m-seg.dxnn | avdec_h264 | 3455 | 3 | 34.5 ±1.3 | 100.21 | 183 | 90.6 | 100.0 | 83 | 400~1000 | 460 | ok |
| yolo26l-seg.dxnn | avdec_h264 | 3455 | 3 | 26.4 ±0.5 | 130.64 | 116 | 94.1 | 100.0 | 83~84 | 300~1000 | 469 | ok |
| yolo26x-seg.dxnn | avdec_h264 | 3455 | 3 | 13.6 ±2.6 | 254.29 | 60 | 92.5 | 100.0 | 84~85 | 200~1000 | 537 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | avdec_h264 | 3455 | 3 | 54.2 ±0.7 | 63.76 | 370 | 32.6 | 67.9 | 62~63 | 1000 | 464 | ok |
| yolo26s-seg.dxnn | avdec_h264 | 3455 | 3 | 52.7 ±0.1 | 65.60 | 328 | 71.1 | 88.1 | 73~75 | 1000 | 474 | ok |
| yolo26m-seg.dxnn | avdec_h264 | 3455 | 3 | 32.3 ±1.2 | 107.00 | 148 | 93.6 | 100.0 | 83~84 | 300~1000 | 465 | ok |
| yolo26l-seg.dxnn | avdec_h264 | 3455 | 3 | 26.4 ±0.3 | 131.08 | 117 | 93.5 | 100.0 | 84~85 | 300~1000 | 471 | ok |
| yolo26x-seg.dxnn | avdec_h264 | 3455 | 3 | 12.5 ±0.3 | 275.64 | 57 | 92.7 | 100.0 | 84~85 | 300~800 | 542 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-seg.dxnn | 40.7 | 54.2 | -13.5 | -24.8% |
| yolo26s-seg.dxnn | 40.8 | 52.7 | -11.8 | -22.5% |
| yolo26m-seg.dxnn | 34.5 | 32.3 | +2.2 | +6.8% |
| yolo26l-seg.dxnn | 26.4 | 26.4 | +0.1 | +0.3% |
| yolo26x-seg.dxnn | 13.6 | 12.5 | +1.1 | +8.5% |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | avdec_h264 | 2640 | 3 | 40.1 ±0.1 | 65.76 | 139 | 94.2 | 100.0 | 73~74 | 1000 | 346 | ok |
| yolo26s-obb.dxnn | avdec_h264 | 2640 | 3 | 25.2 ±0.0 | 104.79 | 88 | 94.4 | 100.0 | 81~82 | 1000 | 358 | ok |
| yolo26m-obb.dxnn | avdec_h264 | 2640 | 3 | 16.8 ±0.5 | 156.97 | 63 | 92.5 | 100.0 | 85~86 | 300~1000 | 383 | ok |
| yolo26l-obb.dxnn | avdec_h264 | 2640 | 3 | 13.6 ±0.4 | 193.72 | 52 | 92.0 | 100.0 | 81~85 | 400~1000 | 392 | ok |
| yolo26x-obb.dxnn | avdec_h264 | 2640 | 3 | 7.3 ±0.1 | 363.16 | 29 | 86.7 | 100.0 | 85~86 | 300~1000 | 459 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | avdec_h264 | 2640 | 3 | 40.2 ±0.0 | 65.61 | 133 | 93.3 | 100.0 | 73~75 | 1000 | 340 | ok |
| yolo26s-obb.dxnn | avdec_h264 | 2640 | 3 | 25.2 ±0.0 | 104.80 | 88 | 94.5 | 100.0 | 79~81 | 1000 | 359 | ok |
| yolo26m-obb.dxnn | avdec_h264 | 2640 | 3 | 16.6 ±0.5 | 159.55 | 62 | 92.9 | 100.0 | 84~85 | 200~1000 | 377 | ok |
| yolo26l-obb.dxnn | avdec_h264 | 2640 | 3 | 12.9 ±0.2 | 205.17 | 49 | 90.4 | 100.0 | 84~85 | 300~1000 | 391 | ok |
| yolo26x-obb.dxnn | avdec_h264 | 2640 | 3 | 7.0 ±0.1 | 375.46 | 29 | 86.9 | 100.0 | 85 | 300~1000 | 464 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-obb.dxnn | 40.1 | 40.2 | -0.1 | -0.2% |
| yolo26s-obb.dxnn | 25.2 | 25.2 | +0.0 | +0.0% |
| yolo26m-obb.dxnn | 16.8 | 16.6 | +0.3 | +1.6% |
| yolo26l-obb.dxnn | 13.6 | 12.9 | +0.8 | +5.9% |
| yolo26x-obb.dxnn | 7.3 | 7.0 | +0.2 | +3.4% |

### Classification

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-cls.dxnn | avdec_h264 | 3455 | 3 | 188.7 ±0.2 | 18.31 | 277 | 5.9 | 19.0 | 54~57 | 1000 | 198 | ok |
| yolo26s-cls.dxnn | avdec_h264 | 3455 | 3 | 188.2 ±0.6 | 18.35 | 275 | 10.4 | 31.5 | 55~57 | 1000 | 205 | ok |
| yolo26m-cls.dxnn | avdec_h264 | 3455 | 3 | 187.9 ±0.3 | 18.39 | 275 | 13.6 | 38.2 | 57~61 | 1000 | 215 | ok |
| yolo26l-cls.dxnn | avdec_h264 | 3455 | 3 | 188.1 ±0.1 | 18.37 | 275 | 22.0 | 51.8 | 58~61 | 1000 | 220 | ok |
| yolo26x-cls.dxnn | avdec_h264 | 3455 | 3 | 187.5 ±0.1 | 18.43 | 274 | 48.3 | 70.5 | 50~55 | 1000 | 256 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-cls.dxnn | avdec_h264 | 3455 | 3 | 188.4 ±0.1 | 18.34 | 276 | 6.1 | 18.9 | 54~56 | 1000 | 197 | ok |
| yolo26s-cls.dxnn | avdec_h264 | 3455 | 3 | 188.0 ±0.6 | 18.38 | 275 | 10.3 | 31.7 | 54~56 | 1000 | 205 | ok |
| yolo26m-cls.dxnn | avdec_h264 | 3455 | 3 | 188.4 ±0.3 | 18.34 | 276 | 13.5 | 36.9 | 59~63 | 1000 | 215 | ok |
| yolo26l-cls.dxnn | avdec_h264 | 3455 | 3 | 187.8 ±0.3 | 18.40 | 274 | 22.1 | 51.9 | 59~61 | 1000 | 220 | ok |
| yolo26x-cls.dxnn | avdec_h264 | 3455 | 3 | 188.1 ±0.1 | 18.37 | 275 | 48.1 | 71.6 | 65 | 1000 | 253 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-cls.dxnn | 188.7 | 188.4 | +0.3 | +0.2% |
| yolo26s-cls.dxnn | 188.2 | 188.0 | +0.2 | +0.1% |
| yolo26m-cls.dxnn | 187.9 | 188.4 | -0.5 | -0.3% |
| yolo26l-cls.dxnn | 188.1 | 187.8 | +0.3 | +0.2% |
| yolo26x-cls.dxnn | 187.5 | 188.1 | -0.6 | -0.3% |

## E2E Pipeline (Multi-Stream)

### Object Detection

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | 2 | 3 | 60.3 ±0.8 | 30.2 | 337 | 32.3 | 62.2 | 61~62 | 1000 | 458 | ok |
| yolo26n.dxnn | 3 | 3 | 60.0 ±0.2 | 20.0 | 336 | 32.4 | 64.9 | 63 | 1000 | 557 | ok |
| yolo26s.dxnn | 2 | 3 | 60.0 ±0.3 | 30.0 | 320 | 63.3 | 84.7 | 73~74 | 1000 | 470 | ok |
| yolo26s.dxnn | 1 | 3 | 62.0 ±0.3 | 62.0 | 315 | 65.1 | 86.3 | 72~73 | 1000 | 335 | ok |
| yolo26m.dxnn | 1 | 3 | 52.6 ±0.0 | 52.6 | 187 | 93.1 | 100.0 | 78~81 | 1000 | 358 | ok |
| yolo26m.dxnn | 2 | 3 | 51.7 ±0.6 | 25.8 | 187 | 94.7 | 100.0 | 83~84 | 400~1000 | 492 | ok |
| yolo26l.dxnn | 1 | 3 | 39.9 ±0.0 | 39.9 | 121 | 94.9 | 100.0 | 80~82 | 1000 | 366 | ok |
| yolo26l.dxnn | 2 | 3 | 39.6 ±0.2 | 19.8 | 125 | 96.3 | 100.0 | 82 | 600~1000 | 502 | ok |
| yolo26x.dxnn | 1 | 3 | 18.0 ±0.1 | 18.0 | 56 | 91.8 | 100.0 | 84~85 | 300~1000 | 427 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | 2 | 3 | 79.7 ±0.2 | 39.8 | 325 | 40.4 | 72.7 | 66~67 | 1000 | 482 | ok |
| yolo26n.dxnn | 3 | 3 | 78.7 ±0.2 | 26.2 | 328 | 40.3 | 71.8 | 67 | 1000 | 587 | ok |
| yolo26s.dxnn | 2 | 3 | 71.4 ±0.2 | 35.7 | 275 | 90.7 | 100.0 | 75~78 | 1000 | 488 | ok |
| yolo26s.dxnn | 3 | 3 | 71.1 ±0.1 | 23.7 | 273 | 91.5 | 100.0 | 73~74 | 1000 | 596 | ok |
| yolo26m.dxnn | 1 | 3 | 52.8 ±0.1 | 52.8 | 182 | 94.4 | 100.0 | 79~80 | 1000 | 363 | ok |
| yolo26m.dxnn | 2 | 3 | 52.5 ±0.1 | 26.2 | 182 | 95.9 | 100.0 | 83 | 600~1000 | 511 | ok |
| yolo26l.dxnn | 1 | 3 | 39.9 ±0.0 | 39.9 | 129 | 95.0 | 100.0 | 80~82 | 1000 | 373 | ok |
| yolo26l.dxnn | 2 | 3 | 36.0 ±0.6 | 18.0 | 120 | 94.7 | 100.0 | 84 | 300~1000 | 507 | ok |
| yolo26x.dxnn | 1 | 3 | 17.1 ±5.0 | 17.1 | 64 | 73.9 | 100.0 | 69~85 | 400~1000 | 430 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n.dxnn | 2 | 30.2 | 2 | 39.8 |
| yolo26s.dxnn | 1 | 62.0 | 2 | 35.7 |
| yolo26m.dxnn | 1 | 52.6 | 1 | 52.8 |
| yolo26l.dxnn | 1 | 39.9 | 1 | 39.9 |

### Pose Estimation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | 2 | 3 | 75.5 ±0.2 | 37.7 | 342 | 44.3 | 71.5 | 63~64 | 1000 | 447 | ok |
| yolo26n-pose.dxnn | 3 | 3 | 74.6 ±0.7 | 24.9 | 343 | 44.0 | 72.8 | 63 | 1000 | 551 | ok |
| yolo26s-pose.dxnn | 2 | 3 | 71.1 ±0.1 | 35.5 | 223 | 95.7 | 100.0 | 74~76 | 1000 | 462 | ok |
| yolo26s-pose.dxnn | 3 | 3 | 71.4 ±0.1 | 23.8 | 227 | 97.0 | 100.0 | 76~77 | 1000 | 563 | ok |
| yolo26m-pose.dxnn | 1 | 3 | 50.8 ±1.2 | 50.8 | 126 | 93.8 | 100.0 | 82~84 | 600~1000 | 347 | ok |
| yolo26m-pose.dxnn | 2 | 3 | 48.4 ±0.8 | 24.2 | 125 | 95.4 | 100.0 | 84 | 400~1000 | 483 | ok |
| yolo26l-pose.dxnn | 1 | 3 | 38.8 ±0.4 | 38.8 | 96 | 95.1 | 100.0 | 82~84 | 800~1000 | 356 | ok |
| yolo26l-pose.dxnn | 2 | 3 | 36.8 ±2.4 | 18.4 | 94 | 95.4 | 100.0 | 81~85 | 400~1000 | 492 | ok |
| yolo26x-pose.dxnn | 1 | 3 | 18.4 ±0.5 | 18.4 | 49 | 91.7 | 100.0 | 83~84 | 300~1000 | 420 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | 3 | 3 | 108.2 ±0.4 | 36.0 | 317 | 84.4 | 93.7 | 69~70 | 1000 | 542 | ok |
| yolo26n-pose.dxnn | 4 | 3 | 108.0 ±0.4 | 27.0 | 322 | 83.9 | 94.0 | 71~73 | 1000 | 646 | ok |
| yolo26s-pose.dxnn | 2 | 3 | 71.4 ±0.1 | 35.7 | 158 | 96.1 | 100.0 | 74~76 | 1000 | 449 | ok |
| yolo26s-pose.dxnn | 3 | 3 | 71.6 ±0.0 | 23.9 | 158 | 97.2 | 100.0 | 78 | 1000 | 553 | ok |
| yolo26m-pose.dxnn | 1 | 3 | 48.3 ±3.3 | 48.3 | 99 | 93.4 | 100.0 | 83~85 | 400~1000 | 337 | ok |
| yolo26m-pose.dxnn | 2 | 3 | 49.0 ±1.1 | 24.5 | 106 | 95.0 | 100.0 | 83~84 | 400~1000 | 470 | ok |
| yolo26l-pose.dxnn | 1 | 3 | 34.9 ±3.4 | 34.9 | 75 | 95.1 | 100.0 | 84~85 | 400~1000 | 343 | ok |
| yolo26l-pose.dxnn | 2 | 3 | 33.4 ±0.5 | 16.7 | 73 | 95.8 | 100.0 | 85 | 300~1000 | 480 | ok |
| yolo26x-pose.dxnn | 1 | 3 | 18.4 ±1.0 | 18.4 | 42 | 92.4 | 100.0 | 84~85 | 300~1000 | 405 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-pose.dxnn | 2 | 37.7 | 3 | 36.0 |
| yolo26s-pose.dxnn | 2 | 35.5 | 2 | 35.7 |
| yolo26m-pose.dxnn | 1 | 50.8 | 1 | 48.3 |
| yolo26l-pose.dxnn | 1 | 38.8 | 1 | 34.9 |

### Segmentation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | 1 | 3 | 40.7 ±0.8 | 40.7 | 338 | 25.6 | 60.5 | 59~61 | 1000 | 420 | ok |
| yolo26n-seg.dxnn | 2 | 3 | 40.8 ±0.2 | 20.4 | 339 | 25.9 | 56.5 | 58~60 | 1000 | 567 | ok |
| yolo26s-seg.dxnn | 1 | 3 | 40.8 ±0.5 | 40.8 | 323 | 47.8 | 73.2 | 67~69 | 1000 | 435 | ok |
| yolo26s-seg.dxnn | 2 | 3 | 40.7 ±0.4 | 20.3 | 324 | 48.1 | 76.9 | 69~70 | 1000 | 580 | ok |
| yolo26m-seg.dxnn | 1 | 3 | 34.5 ±1.3 | 34.5 | 183 | 90.6 | 100.0 | 83 | 400~1000 | 460 | ok |
| yolo26m-seg.dxnn | 2 | 3 | 32.7 ±1.3 | 16.3 | 161 | 93.1 | 100.0 | 82~83 | 300~1000 | 603 | ok |
| yolo26l-seg.dxnn | 1 | 3 | 26.4 ±0.5 | 26.4 | 116 | 94.1 | 100.0 | 83~84 | 300~1000 | 469 | ok |
| yolo26x-seg.dxnn | 1 | 3 | 13.6 ±2.6 | 13.6 | 60 | 92.5 | 100.0 | 84~85 | 200~1000 | 537 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | 1 | 3 | 54.2 ±0.7 | 54.2 | 370 | 32.6 | 67.9 | 62~63 | 1000 | 464 | ok |
| yolo26n-seg.dxnn | 2 | 3 | 54.4 ±0.8 | 27.2 | 366 | 33.0 | 70.7 | 62~63 | 1000 | 610 | ok |
| yolo26s-seg.dxnn | 1 | 3 | 52.7 ±0.1 | 52.7 | 328 | 71.1 | 88.1 | 73~75 | 1000 | 474 | ok |
| yolo26s-seg.dxnn | 2 | 3 | 53.1 ±0.3 | 26.6 | 329 | 73.8 | 91.5 | 74~76 | 1000 | 624 | ok |
| yolo26m-seg.dxnn | 1 | 3 | 32.3 ±1.2 | 32.3 | 148 | 93.6 | 100.0 | 83~84 | 300~1000 | 465 | ok |
| yolo26m-seg.dxnn | 2 | 3 | 31.7 ±0.8 | 15.8 | 146 | 94.2 | 100.0 | 83~84 | 300~1000 | 612 | ok |
| yolo26l-seg.dxnn | 1 | 3 | 26.4 ±0.3 | 26.4 | 117 | 93.5 | 100.0 | 84~85 | 300~1000 | 471 | ok |
| yolo26x-seg.dxnn | 1 | 3 | 12.5 ±0.3 | 12.5 | 57 | 92.7 | 100.0 | 84~85 | 300~800 | 542 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-seg.dxnn | 1 | 40.7 | 1 | 54.2 |
| yolo26s-seg.dxnn | 1 | 40.8 | 1 | 52.7 |
| yolo26m-seg.dxnn | 1 | 34.5 | 1 | 32.3 |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | 1 | 3 | 40.1 ±0.1 | 40.1 | 139 | 94.2 | 100.0 | 73~74 | 1000 | 346 | ok |
| yolo26n-obb.dxnn | 2 | 2/3 | 40.0 ±0.3 | 20.0 | 144 | 95.6 | 100.0 | 67~73 | 1000 | 479 | partial |
| yolo26s-obb.dxnn | 1 | 3 | 25.2 ±0.0 | 25.2 | 88 | 94.4 | 100.0 | 81~82 | 1000 | 358 | ok |
| yolo26m-obb.dxnn | 1 | 3 | 16.8 ±0.5 | 16.8 | 63 | 92.5 | 100.0 | 85~86 | 300~1000 | 383 | ok |
| yolo26l-obb.dxnn | 1 | 3 | 13.6 ±0.4 | 13.6 | 52 | 92.0 | 100.0 | 81~85 | 400~1000 | 392 | ok |
| yolo26x-obb.dxnn | 1 | 3 | 7.3 ±0.1 | 7.3 | 29 | 86.7 | 100.0 | 85~86 | 300~1000 | 459 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | 1 | 3 | 40.2 ±0.0 | 40.2 | 133 | 93.3 | 100.0 | 73~75 | 1000 | 340 | ok |
| yolo26n-obb.dxnn | 2 | 3 | 40.2 ±0.0 | 20.1 | 136 | 95.6 | 100.0 | 74~75 | 1000 | 469 | ok |
| yolo26s-obb.dxnn | 1 | 3 | 25.2 ±0.0 | 25.2 | 88 | 94.5 | 100.0 | 79~81 | 1000 | 359 | ok |
| yolo26m-obb.dxnn | 1 | 3 | 16.6 ±0.5 | 16.6 | 62 | 92.9 | 100.0 | 84~85 | 200~1000 | 377 | ok |
| yolo26l-obb.dxnn | 1 | 3 | 12.9 ±0.2 | 12.9 | 49 | 90.4 | 100.0 | 84~85 | 300~1000 | 391 | ok |
| yolo26x-obb.dxnn | 1 | 3 | 7.0 ±0.1 | 7.0 | 29 | 86.9 | 100.0 | 85 | 300~1000 | 464 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-obb.dxnn | 1 | 40.1 | 1 | 40.2 |

---
*Report generated by dx_stream benchmark tool*
