# YOLO26 Benchmark Report

**Generated:** 2026-06-30 08:37:31 (Local)

## Test Timing

| # | Type | Start | End | Duration |
|---|------|-------|-----|----------|
| 1 | run | 2026-06-29 11:52:31 | 2026-06-30 08:37:31 | 20h 44m 59s |

## Executive Summary

### Object Detection

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n.dxnn | ON | 25.12 | 159.2 | 138.9 | 4 |
| yolo26n.dxnn | OFF | 37.00 | 221.4 | 97.4 | 3 |
| yolo26s.dxnn | ON | 43.98 | 131.4 | 120.3 | 4 |
| yolo26s.dxnn | OFF | 41.06 | 130.9 | 98.3 | 3 |
| yolo26m.dxnn | ON | 52.35 | 91.0 | 90.5 | 2 |
| yolo26m.dxnn | OFF | 51.22 | 91.2 | 91.0 | 2 |
| yolo26l.dxnn | ON | 61.29 | 66.8 | 67.0 | 2 |
| yolo26l.dxnn | OFF | 60.83 | 66.8 | 66.8 | 2 |
| yolo26x.dxnn | ON | 97.69 | 38.3 | 38.0 | 1 |
| yolo26x.dxnn | OFF | 93.84 | 38.4 | 38.1 | 1 |

### Pose Estimation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-pose.dxnn | ON | 31.13 | 216.9 | 183.9 | 6 |
| yolo26n-pose.dxnn | OFF | 19.74 | 215.1 | 210.4 | 7 |
| yolo26s-pose.dxnn | ON | 34.84 | 126.2 | 126.0 | 4 |
| yolo26s-pose.dxnn | OFF | 33.79 | 126.3 | 125.5 | 4 |
| yolo26m-pose.dxnn | ON | 46.01 | 88.0 | 88.1 | 2 |
| yolo26m-pose.dxnn | OFF | 39.70 | 87.9 | 87.7 | 2 |
| yolo26l-pose.dxnn | ON | 57.00 | 65.2 | 65.1 | 2 |
| yolo26l-pose.dxnn | OFF | 53.37 | 64.9 | 65.1 | 2 |
| yolo26x-pose.dxnn | ON | 91.70 | 37.5 | 37.3 | 1 |
| yolo26x-pose.dxnn | OFF | 83.58 | 37.4 | 37.3 | 1 |

### Segmentation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-seg.dxnn | ON | 35.30 | 106.8 | 88.5 | 2 |
| yolo26n-seg.dxnn | OFF | 35.14 | 145.8 | 80.5 | 2 |
| yolo26s-seg.dxnn | ON | 47.87 | 96.0 | 78.0 | 2 |
| yolo26s-seg.dxnn | OFF | 44.62 | 100.1 | 80.0 | 2 |
| yolo26m-seg.dxnn | ON | 64.15 | 65.1 | 63.2 | 1 |
| yolo26m-seg.dxnn | OFF | 58.91 | 65.2 | 64.9 | 1 |
| yolo26l-seg.dxnn | ON | 76.46 | 51.9 | 51.4 | 1 |
| yolo26l-seg.dxnn | OFF | 68.80 | 51.7 | 51.1 | 1 |
| yolo26x-seg.dxnn | ON | 127.60 | 29.4 | 26.2 | — |
| yolo26x-seg.dxnn | OFF | 120.17 | 28.9 | 25.9 | — |

### Oriented BBox (OBB)

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-obb.dxnn | ON | 50.96 | 74.5 | 74.3 | 2 |
| yolo26n-obb.dxnn | OFF | 45.20 | 74.4 | 73.8 | 2 |
| yolo26s-obb.dxnn | ON | 67.90 | 43.7 | 43.6 | 1 |
| yolo26s-obb.dxnn | OFF | 66.07 | 43.7 | 43.6 | 1 |
| yolo26m-obb.dxnn | ON | 87.83 | 31.9 | 31.9 | 1 |
| yolo26m-obb.dxnn | OFF | 86.48 | 32.0 | 31.9 | 1 |
| yolo26l-obb.dxnn | ON | 114.22 | 23.3 | 23.4 | — |
| yolo26l-obb.dxnn | OFF | 104.86 | 23.2 | 23.4 | — |
| yolo26x-obb.dxnn | ON | 192.26 | 13.6 | 12.7 | — |
| yolo26x-obb.dxnn | OFF | 182.47 | 13.5 | 12.8 | — |

### Classification

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-cls.dxnn | ON | 1.29 | 3496.5 | 971.8 | — |
| yolo26n-cls.dxnn | OFF | 1.29 | 3500.2 | 964.5 | — |
| yolo26s-cls.dxnn | ON | 2.03 | 1895.9 | 947.8 | — |
| yolo26s-cls.dxnn | OFF | 2.08 | 1896.8 | 979.2 | — |
| yolo26m-cls.dxnn | ON | 4.14 | 1336.2 | 974.5 | — |
| yolo26m-cls.dxnn | OFF | 2.62 | 1336.4 | 953.4 | — |
| yolo26l-cls.dxnn | ON | 3.87 | 838.6 | 803.1 | — |
| yolo26l-cls.dxnn | OFF | 3.91 | 839.7 | 803.3 | — |
| yolo26x-cls.dxnn | ON | 6.54 | 449.5 | 448.6 | — |
| yolo26x-cls.dxnn | OFF | 6.50 | 449.9 | 447.3 | — |

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
| NPU RT | v3.3.2 |
| NPU Driver (RT) | v2.4.1 |
| NPU Driver (PCIe) | v2.2.0 |
| NPU Firmware | v2.5.6 |
| NPU Memory | LPDDR5 5600 Mbps, 3.92GiB |
| NPU Board | M.2, Rev 1.0 |
| NPU PCIe | Gen3 X2 [11:00:00] |

### Tools

| Tool | Available | Version |
|------|-----------|---------|
| run_model | Yes | DXRT v3.3.2 run_model |
| gst-launch-1.0 | Yes | gst-launch-1.0 version 1.22.9 |
| gst-inspect-1.0 | Yes | gst-inspect-1.0 version 1.22.9 |
| dxtop | Yes | DX-TOP 1.1.0 |
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
| yolo26n.dxnn | 159.2 ±3.1 | 204 | 48.2 | 81.3 | 46~49 | 1000 | ok |
| yolo26s.dxnn | 131.4 ±0.1 | 168 | 89.4 | 100.0 | 57~59 | 1000 | ok |
| yolo26m.dxnn | 91.0 ±0.0 | 135 | 91.0 | 100.0 | 59~63 | 1000 | ok |
| yolo26l.dxnn | 66.8 ±0.2 | 100 | 89.6 | 100.0 | 59~63 | 1000 | ok |
| yolo26x.dxnn | 38.3 ±0.2 | 71 | 89.1 | 100.0 | 60~65 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n.dxnn | 221.4 ±3.0 | 148 | 86.8 | 99.9 | 56~58 | 1000 | ok |
| yolo26s.dxnn | 130.9 ±0.4 | 95 | 92.3 | 100.0 | 57~59 | 1000 | ok |
| yolo26m.dxnn | 91.2 ±0.4 | 85 | 91.3 | 100.0 | 60~64 | 1000 | ok |
| yolo26l.dxnn | 66.8 ±0.1 | 86 | 89.4 | 100.0 | 59~63 | 1000 | ok |
| yolo26x.dxnn | 38.4 ±0.1 | 54 | 88.4 | 100.0 | 60~65 | 1000 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-pose.dxnn | 216.9 ±0.7 | 189 | 90.9 | 100.0 | 56~59 | 1000 | ok |
| yolo26s-pose.dxnn | 126.2 ±0.2 | 126 | 90.7 | 100.0 | 57~60 | 1000 | ok |
| yolo26m-pose.dxnn | 88.0 ±0.3 | 104 | 89.9 | 100.0 | 60~64 | 1000 | ok |
| yolo26l-pose.dxnn | 65.2 ±0.3 | 92 | 88.4 | 100.0 | 59~63 | 1000 | ok |
| yolo26x-pose.dxnn | 37.5 ±0.3 | 71 | 88.8 | 100.0 | 61~65 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-pose.dxnn | 215.1 ±0.2 | 109 | 89.3 | 100.0 | 56~59 | 1000 | ok |
| yolo26s-pose.dxnn | 126.3 ±0.0 | 102 | 91.5 | 100.0 | 58~60 | 1000 | ok |
| yolo26m-pose.dxnn | 87.9 ±0.2 | 85 | 90.7 | 100.0 | 60~64 | 1000 | ok |
| yolo26l-pose.dxnn | 64.9 ±0.1 | 75 | 90.5 | 100.0 | 60~63 | 1000 | ok |
| yolo26x-pose.dxnn | 37.4 ±0.0 | 58 | 88.6 | 100.0 | 61~65 | 1000 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-seg.dxnn | 106.8 ±2.2 | 303 | 38.3 | 67.0 | 55~57 | 1000 | ok |
| yolo26s-seg.dxnn | 96.0 ±1.2 | 249 | 80.2 | 92.8 | 57~60 | 1000 | ok |
| yolo26m-seg.dxnn | 65.1 ±0.3 | 152 | 89.9 | 100.0 | 61~66 | 1000 | ok |
| yolo26l-seg.dxnn | 51.9 ±0.3 | 114 | 88.7 | 100.0 | 60~64 | 1000 | ok |
| yolo26x-seg.dxnn | 29.4 ±0.4 | 82 | 89.4 | 100.0 | 62~67 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-seg.dxnn | 145.8 ±1.6 | 225 | 64.3 | 78.2 | 56~58 | 1000 | ok |
| yolo26s-seg.dxnn | 100.1 ±0.2 | 147 | 89.8 | 100.0 | 57~60 | 1000 | ok |
| yolo26m-seg.dxnn | 65.2 ±0.5 | 108 | 89.5 | 100.0 | 61~65 | 1000 | ok |
| yolo26l-seg.dxnn | 51.7 ±0.3 | 93 | 89.6 | 100.0 | 60~65 | 1000 | ok |
| yolo26x-seg.dxnn | 28.9 ±0.3 | 69 | 88.8 | 100.0 | 62~67 | 1000 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-obb.dxnn | 74.5 ±0.1 | 105 | 91.7 | 100.0 | 56~58 | 1000 | ok |
| yolo26s-obb.dxnn | 43.7 ±0.0 | 93 | 88.4 | 100.0 | 57~59 | 1000 | ok |
| yolo26m-obb.dxnn | 31.9 ±0.1 | 63 | 88.5 | 100.0 | 59~63 | 1000 | ok |
| yolo26l-obb.dxnn | 23.3 ±0.1 | 56 | 88.5 | 100.0 | 60~63 | 1000 | ok |
| yolo26x-obb.dxnn | 13.6 ±0.0 | 42 | 86.1 | 100.0 | 61~65 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-obb.dxnn | 74.4 ±0.2 | 85 | 89.4 | 100.0 | 56~58 | 1000 | ok |
| yolo26s-obb.dxnn | 43.7 ±0.0 | 69 | 92.1 | 100.0 | 57~59 | 1000 | ok |
| yolo26m-obb.dxnn | 32.0 ±0.0 | 53 | 88.5 | 100.0 | 60~63 | 1000 | ok |
| yolo26l-obb.dxnn | 23.2 ±0.1 | 42 | 87.8 | 100.0 | 59~63 | 1000 | ok |
| yolo26x-obb.dxnn | 13.5 ±0.0 | 30 | 84.5 | 100.0 | 61~64 | 1000 | ok |

#### Classification

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-cls.dxnn | 3496.5 ±3.5 | 119 | 87.2 | 96.0 | 54~55 | 1000 | ok |
| yolo26s-cls.dxnn | 1895.9 ±1.5 | 72 | 89.1 | 97.7 | 55~56 | 1000 | ok |
| yolo26m-cls.dxnn | 1336.2 ±1.5 | 55 | 88.7 | 98.1 | 58~61 | 1000 | ok |
| yolo26l-cls.dxnn | 838.6 ±0.6 | 62 | 89.4 | 98.7 | 56~58 | 1000 | ok |
| yolo26x-cls.dxnn | 449.5 ±0.5 | 49 | 88.1 | 99.3 | 58~61 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26n-cls.dxnn | 3500.2 ±11.1 | 118 | 86.9 | 96.0 | 54~55 | 1000 | ok |
| yolo26s-cls.dxnn | 1896.8 ±2.0 | 69 | 89.0 | 96.8 | 55~56 | 1000 | ok |
| yolo26m-cls.dxnn | 1336.4 ±0.4 | 54 | 86.9 | 97.8 | 58~60 | 1000 | ok |
| yolo26l-cls.dxnn | 839.7 ±0.5 | 60 | 87.7 | 98.0 | 56~59 | 1000 | ok |
| yolo26x-cls.dxnn | 449.9 ±0.1 | 50 | 88.9 | 99.6 | 58~61 | 1000 | ok |

### Latency (Single-Core, Sync)

#### Object Detection

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n.dxnn | 39.8 | 25.12 | 22.14 | 2.98 | 43 | ok |
| yolo26s.dxnn | 22.7 | 43.98 | 37.36 | 6.61 | 53 | ok |
| yolo26m.dxnn | 19.1 | 52.35 | 49.22 | 3.13 | 53 | ok |
| yolo26l.dxnn | 16.3 | 61.29 | 57.36 | 3.93 | 53 | ok |
| yolo26x.dxnn | 10.2 | 97.69 | 91.68 | 6.01 | 54 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n.dxnn | 27.0 | 37.00 | 37.00 | 53 | ok |
| yolo26s.dxnn | 24.4 | 41.06 | 41.06 | 53 | ok |
| yolo26m.dxnn | 19.5 | 51.22 | 51.22 | 54 | ok |
| yolo26l.dxnn | 16.4 | 60.83 | 60.83 | 53 | ok |
| yolo26x.dxnn | 10.7 | 93.84 | 93.84 | 54 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-pose.dxnn | 32.1 | 31.13 | 26.10 | 5.03 | 53 | ok |
| yolo26s-pose.dxnn | 28.7 | 34.84 | 32.61 | 2.23 | 53 | ok |
| yolo26m-pose.dxnn | 21.7 | 46.01 | 41.57 | 4.45 | 54 | ok |
| yolo26l-pose.dxnn | 17.5 | 57.00 | 52.68 | 4.32 | 54 | ok |
| yolo26x-pose.dxnn | 10.9 | 91.70 | 88.76 | 2.94 | 54 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-pose.dxnn | 50.7 | 19.74 | 19.74 | 53 | ok |
| yolo26s-pose.dxnn | 29.6 | 33.79 | 33.79 | 53 | ok |
| yolo26m-pose.dxnn | 25.2 | 39.70 | 39.70 | 54 | ok |
| yolo26l-pose.dxnn | 18.7 | 53.37 | 53.37 | 54 | ok |
| yolo26x-pose.dxnn | 12.0 | 83.58 | 83.58 | 54 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-seg.dxnn | 28.3 | 35.30 | 32.31 | 2.99 | 53 | ok |
| yolo26s-seg.dxnn | 20.9 | 47.87 | 44.14 | 3.72 | 53 | ok |
| yolo26m-seg.dxnn | 15.6 | 64.15 | 60.07 | 4.08 | 54 | ok |
| yolo26l-seg.dxnn | 13.1 | 76.46 | 72.14 | 4.33 | 54 | ok |
| yolo26x-seg.dxnn | 7.8 | 127.60 | 122.16 | 5.44 | 55 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-seg.dxnn | 28.5 | 35.14 | 35.14 | 53 | ok |
| yolo26s-seg.dxnn | 22.4 | 44.62 | 44.62 | 53 | ok |
| yolo26m-seg.dxnn | 17.0 | 58.91 | 58.91 | 54 | ok |
| yolo26l-seg.dxnn | 14.5 | 68.80 | 68.80 | 54 | ok |
| yolo26x-seg.dxnn | 8.3 | 120.17 | 120.17 | 55 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-obb.dxnn | 19.6 | 50.96 | 44.86 | 6.10 | 53 | ok |
| yolo26s-obb.dxnn | 14.7 | 67.90 | 64.25 | 3.66 | 53 | ok |
| yolo26m-obb.dxnn | 11.4 | 87.83 | 84.18 | 3.65 | 54 | ok |
| yolo26l-obb.dxnn | 8.8 | 114.22 | 110.39 | 3.83 | 55 | ok |
| yolo26x-obb.dxnn | 5.2 | 192.26 | 188.30 | 3.95 | 56 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-obb.dxnn | 22.1 | 45.20 | 45.20 | 53 | ok |
| yolo26s-obb.dxnn | 15.1 | 66.07 | 66.07 | 53 | ok |
| yolo26m-obb.dxnn | 11.6 | 86.48 | 86.48 | 54 | ok |
| yolo26l-obb.dxnn | 9.5 | 104.86 | 104.86 | 54 | ok |
| yolo26x-obb.dxnn | 5.5 | 182.47 | 182.47 | 56 | ok |

#### Classification

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-cls.dxnn | 776.6 | 1.29 | 1.29 | N/A | 52 | ok |
| yolo26s-cls.dxnn | 493.6 | 2.03 | 2.03 | N/A | 52 | ok |
| yolo26m-cls.dxnn | 241.4 | 4.14 | 4.14 | N/A | 53 | ok |
| yolo26l-cls.dxnn | 258.5 | 3.87 | 3.87 | N/A | 52 | ok |
| yolo26x-cls.dxnn | 152.9 | 6.54 | 6.54 | N/A | 53 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|-------------|--------|
| yolo26n-cls.dxnn | 774.0 | 1.29 | 1.29 | 52 | ok |
| yolo26s-cls.dxnn | 480.2 | 2.08 | 2.08 | 53 | ok |
| yolo26m-cls.dxnn | 381.4 | 2.62 | 2.62 | 53 | ok |
| yolo26l-cls.dxnn | 255.7 | 3.91 | 3.91 | 53 | ok |
| yolo26x-cls.dxnn | 153.8 | 6.50 | 6.50 | 53 | ok |

## E2E Pipeline (Single-Stream)

### Object Detection

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | mppvideodec | 3455 | 3 | 138.9 ±4.0 | 24.88 | 239 | 44.5 | 77.3 | 50~52 | 1000 | 175 | ok |
| yolo26s.dxnn | mppvideodec | 3455 | 3 | 120.3 ±2.0 | 28.72 | 200 | 78.6 | 95.4 | 61~62 | 1000 | 189 | ok |
| yolo26m.dxnn | mppvideodec | 3455 | 3 | 90.5 ±0.4 | 38.16 | 149 | 90.5 | 100.0 | 67~70 | 1000 | 211 | ok |
| yolo26l.dxnn | mppvideodec | 3455 | 3 | 67.0 ±0.1 | 51.55 | 112 | 92.4 | 100.0 | 67~72 | 1000 | 221 | ok |
| yolo26x.dxnn | mppvideodec | 3455 | 3 | 38.0 ±1.2 | 90.86 | 73 | 95.4 | 100.0 | 73~79 | 1000 | 346 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | mppvideodec | 3455 | 3 | 97.4 ±0.3 | 35.47 | 185 | 25.4 | 83.6 | 57 | 1000 | 190 | ok |
| yolo26s.dxnn | mppvideodec | 3455 | 3 | 98.3 ±0.2 | 35.14 | 194 | 51.6 | 86.9 | 60~61 | 1000 | 204 | ok |
| yolo26m.dxnn | mppvideodec | 3455 | 3 | 91.0 ±0.2 | 37.97 | 191 | 92.5 | 100.0 | 67~70 | 1000 | 222 | ok |
| yolo26l.dxnn | mppvideodec | 3455 | 3 | 66.8 ±0.1 | 51.73 | 141 | 93.0 | 100.0 | 67~71 | 1000 | 234 | ok |
| yolo26x.dxnn | mppvideodec | 3455 | 3 | 38.1 ±1.1 | 90.76 | 101 | 95.5 | 100.0 | 73~79 | 1000 | 346 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n.dxnn | 138.9 | 97.4 | +41.5 | +42.6% |
| yolo26s.dxnn | 120.3 | 98.3 | +22.0 | +22.4% |
| yolo26m.dxnn | 90.5 | 91.0 | -0.4 | -0.5% |
| yolo26l.dxnn | 67.0 | 66.8 | +0.2 | +0.4% |
| yolo26x.dxnn | 38.0 | 38.1 | -0.0 | -0.1% |

### Pose Estimation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | mppvideodec | 3455 | 3 | 183.9 ±4.3 | 18.79 | 227 | 64.5 | 84.9 | 59 | 1000 | 167 | ok |
| yolo26s-pose.dxnn | mppvideodec | 3455 | 3 | 126.0 ±0.5 | 27.42 | 149 | 89.6 | 100.0 | 61~63 | 1000 | 181 | ok |
| yolo26m-pose.dxnn | mppvideodec | 3455 | 3 | 88.1 ±0.1 | 39.21 | 110 | 91.1 | 100.0 | 67~70 | 1000 | 204 | ok |
| yolo26l-pose.dxnn | mppvideodec | 3455 | 3 | 65.1 ±0.0 | 53.08 | 91 | 92.9 | 100.0 | 67~71 | 1000 | 212 | ok |
| yolo26x-pose.dxnn | mppvideodec | 3455 | 3 | 37.3 ±1.0 | 92.62 | 73 | 94.9 | 100.0 | 73~79 | 1000 | 358 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | mppvideodec | 3455 | 3 | 210.4 ±0.1 | 16.42 | 168 | 79.6 | 98.4 | 51~58 | 1000 | 157 | ok |
| yolo26s-pose.dxnn | mppvideodec | 3455 | 3 | 125.5 ±0.2 | 27.52 | 119 | 87.9 | 100.0 | 61~62 | 1000 | 172 | ok |
| yolo26m-pose.dxnn | mppvideodec | 3455 | 3 | 87.7 ±0.5 | 39.42 | 97 | 90.7 | 100.0 | 67~70 | 1000 | 195 | ok |
| yolo26l-pose.dxnn | mppvideodec | 3455 | 3 | 65.1 ±0.1 | 53.04 | 82 | 92.8 | 100.0 | 68~71 | 1000 | 202 | ok |
| yolo26x-pose.dxnn | mppvideodec | 3455 | 3 | 37.3 ±1.1 | 92.56 | 68 | 95.1 | 100.0 | 73~78 | 1000 | 358 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-pose.dxnn | 183.9 | 210.4 | -26.5 | -12.6% |
| yolo26s-pose.dxnn | 126.0 | 125.5 | +0.5 | +0.4% |
| yolo26m-pose.dxnn | 88.1 | 87.7 | +0.5 | +0.5% |
| yolo26l-pose.dxnn | 65.1 | 65.1 | -0.0 | -0.1% |
| yolo26x-pose.dxnn | 37.3 | 37.3 | -0.0 | -0.1% |

### Segmentation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | mppvideodec | 3455 | 3 | 88.5 ±0.9 | 39.05 | 318 | 36.7 | 62.3 | 57~59 | 1000 | 270 | ok |
| yolo26s-seg.dxnn | mppvideodec | 3455 | 3 | 78.0 ±3.4 | 44.32 | 273 | 59.5 | 82.9 | 61~63 | 1000 | 285 | ok |
| yolo26m-seg.dxnn | mppvideodec | 3455 | 3 | 63.2 ±0.0 | 54.68 | 220 | 88.0 | 98.9 | 71~76 | 1000 | 311 | ok |
| yolo26l-seg.dxnn | mppvideodec | 3455 | 3 | 51.4 ±0.8 | 67.19 | 166 | 93.8 | 100.0 | 72~77 | 1000 | 321 | ok |
| yolo26x-seg.dxnn | mppvideodec | 3455 | 3 | 26.2 ±2.3 | 131.92 | 98 | 93.4 | 100.0 | 79~83 | 600~1000 | 391 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | mppvideodec | 3455 | 3 | 80.5 ±1.3 | 42.94 | 276 | 26.3 | 85.0 | 57 | 1000 | 300 | ok |
| yolo26s-seg.dxnn | mppvideodec | 3455 | 3 | 80.0 ±1.3 | 43.17 | 272 | 56.9 | 93.5 | 61~63 | 1000 | 316 | ok |
| yolo26m-seg.dxnn | mppvideodec | 3455 | 3 | 64.9 ±0.8 | 53.26 | 213 | 93.1 | 100.0 | 72~77 | 1000 | 326 | ok |
| yolo26l-seg.dxnn | mppvideodec | 3455 | 3 | 51.1 ±0.8 | 67.60 | 149 | 93.3 | 100.0 | 71~77 | 1000 | 347 | ok |
| yolo26x-seg.dxnn | mppvideodec | 3455 | 3 | 25.9 ±2.0 | 133.43 | 102 | 93.5 | 100.0 | 80~84 | 600~1000 | 406 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-seg.dxnn | 88.5 | 80.5 | +8.0 | +10.0% |
| yolo26s-seg.dxnn | 78.0 | 80.0 | -2.1 | -2.6% |
| yolo26m-seg.dxnn | 63.2 | 64.9 | -1.7 | -2.6% |
| yolo26l-seg.dxnn | 51.4 | 51.1 | +0.3 | +0.6% |
| yolo26x-seg.dxnn | 26.2 | 25.9 | +0.3 | +1.2% |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | mppvideodec | 2640 | 3 | 74.3 ±0.1 | 35.55 | 118 | 91.2 | 100.0 | 59~61 | 1000 | 192 | ok |
| yolo26s-obb.dxnn | mppvideodec | 2640 | 3 | 43.6 ±0.1 | 60.56 | 84 | 93.7 | 100.0 | 61~64 | 1000 | 209 | ok |
| yolo26m-obb.dxnn | mppvideodec | 2640 | 3 | 31.9 ±0.1 | 82.83 | 72 | 93.9 | 100.0 | 69~74 | 1000 | 231 | ok |
| yolo26l-obb.dxnn | mppvideodec | 2640 | 3 | 23.4 ±0.1 | 113.06 | 58 | 95.0 | 100.0 | 70~75 | 1000 | 241 | ok |
| yolo26x-obb.dxnn | mppvideodec | 2640 | 3 | 12.7 ±0.5 | 207.22 | 47 | 94.6 | 100.0 | 77~80 | 1000 | 366 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | mppvideodec | 2640 | 3 | 73.8 ±0.1 | 35.76 | 130 | 90.2 | 100.0 | 59~60 | 1000 | 193 | ok |
| yolo26s-obb.dxnn | mppvideodec | 2640 | 3 | 43.6 ±0.1 | 60.61 | 95 | 93.1 | 100.0 | 62~64 | 1000 | 206 | ok |
| yolo26m-obb.dxnn | mppvideodec | 2640 | 3 | 31.9 ±0.1 | 82.64 | 76 | 94.3 | 100.0 | 69~73 | 1000 | 230 | ok |
| yolo26l-obb.dxnn | mppvideodec | 2640 | 3 | 23.4 ±0.0 | 112.88 | 58 | 95.3 | 100.0 | 71~75 | 1000 | 242 | ok |
| yolo26x-obb.dxnn | mppvideodec | 2640 | 3 | 12.8 ±0.5 | 205.59 | 44 | 94.0 | 100.0 | 77~80 | 1000 | 366 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-obb.dxnn | 74.3 | 73.8 | +0.4 | +0.6% |
| yolo26s-obb.dxnn | 43.6 | 43.6 | +0.0 | +0.1% |
| yolo26m-obb.dxnn | 31.9 | 31.9 | -0.1 | -0.3% |
| yolo26l-obb.dxnn | 23.4 | 23.4 | -0.0 | -0.2% |
| yolo26x-obb.dxnn | 12.7 | 12.8 | -0.1 | -0.8% |

### Classification

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-cls.dxnn | mppvideodec | 3455 | 3 | 971.8 ±35.1 | 3.56 | 155 | 11.7 | 44.9 | 53~54 | 1000 | 85 | ok |
| yolo26s-cls.dxnn | mppvideodec | 3455 | 3 | 947.8 ±3.4 | 3.65 | 152 | 22.0 | 63.2 | 55 | 1000 | 100 | ok |
| yolo26m-cls.dxnn | mppvideodec | 3455 | 3 | 974.5 ±34.6 | 3.54 | 155 | 38.8 | 83.2 | 59 | 1000 | 123 | ok |
| yolo26l-cls.dxnn | mppvideodec | 3455 | 3 | 803.1 ±13.6 | 4.30 | 135 | 60.9 | 98.1 | 57 | 1000 | 136 | ok |
| yolo26x-cls.dxnn | mppvideodec | 3455 | 3 | 448.6 ±0.9 | 7.70 | 95 | 69.2 | 98.9 | 61 | 1000 | 212 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-cls.dxnn | mppvideodec | 3455 | 3 | 964.5 ±42.7 | 3.58 | 154 | 13.5 | 45.8 | 53~54 | 1000 | 86 | ok |
| yolo26s-cls.dxnn | mppvideodec | 3455 | 3 | 979.2 ±28.4 | 3.53 | 153 | 28.4 | 66.6 | 54 | 1000 | 100 | ok |
| yolo26m-cls.dxnn | mppvideodec | 3455 | 3 | 953.4 ±39.8 | 3.62 | 150 | 35.0 | 82.1 | 58 | 1000 | 123 | ok |
| yolo26l-cls.dxnn | mppvideodec | 3455 | 3 | 803.3 ±10.0 | 4.30 | 133 | 56.9 | 98.4 | 57 | 1000 | 136 | ok |
| yolo26x-cls.dxnn | mppvideodec | 3455 | 3 | 447.3 ±0.9 | 7.72 | 98 | 66.6 | 99.4 | 60~61 | 1000 | 212 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-cls.dxnn | 971.8 | 964.5 | +7.3 | +0.8% |
| yolo26s-cls.dxnn | 947.8 | 979.2 | -31.4 | -3.2% |
| yolo26m-cls.dxnn | 974.5 | 953.4 | +21.1 | +2.2% |
| yolo26l-cls.dxnn | 803.1 | 803.3 | -0.2 | -0.0% |
| yolo26x-cls.dxnn | 448.6 | 447.3 | +1.3 | +0.3% |

## E2E Pipeline (Multi-Stream)

### Object Detection

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | 4 | 3 | 141.2 ±1.2 | 35.3 | 247 | 48.8 | 76.2 | 56~59 | 1000 | 198 | ok |
| yolo26n.dxnn | 5 | 3 | 142.1 ±0.2 | 28.4 | 252 | 49.6 | 77.6 | 61~62 | 1000 | 203 | ok |
| yolo26s.dxnn | 4 | 3 | 120.9 ±0.8 | 30.2 | 208 | 84.4 | 94.9 | 67~71 | 1000 | 212 | ok |
| yolo26s.dxnn | 5 | 3 | 120.0 ±1.8 | 24.0 | 204 | 84.5 | 96.4 | 72~74 | 1000 | 217 | ok |
| yolo26m.dxnn | 3 | 3 | 85.5 ±3.0 | 28.5 | 138 | 95.7 | 100.0 | 77~81 | 1000 | 228 | ok |
| yolo26m.dxnn | 2 | 3 | 83.1 ±0.2 | 41.5 | 132 | 95.0 | 100.0 | 80~82 | 1000 | 222 | ok |
| yolo26l.dxnn | 2 | 3 | 63.8 ±2.3 | 31.9 | 109 | 95.6 | 100.0 | 76~79 | 1000 | 232 | ok |
| yolo26l.dxnn | 3 | 3 | 61.5 ±0.1 | 20.5 | 104 | 96.7 | 100.0 | 81~82 | 1000 | 239 | ok |
| yolo26x.dxnn | 1 | 3 | 38.0 ±1.2 | 38.0 | 73 | 95.4 | 100.0 | 73~79 | 1000 | 346 | ok |
| yolo26x.dxnn | 2 | 3 | 33.6 ±0.8 | 16.8 | 80 | 94.3 | 100.0 | 82~83 | 600~1000 | 346 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | 3 | 3 | 98.6 ±0.4 | 32.9 | 205 | 27.0 | 84.6 | 57~58 | 1000 | 213 | ok |
| yolo26n.dxnn | 4 | 3 | 98.5 ±0.3 | 24.6 | 204 | 27.2 | 86.2 | 59 | 1000 | 221 | ok |
| yolo26s.dxnn | 3 | 3 | 98.0 ±0.5 | 32.7 | 196 | 54.5 | 86.6 | 64~66 | 1000 | 227 | ok |
| yolo26s.dxnn | 4 | 3 | 98.1 ±0.2 | 24.5 | 201 | 55.0 | 86.7 | 67~69 | 1000 | 235 | ok |
| yolo26m.dxnn | 3 | 3 | 85.7 ±2.9 | 28.6 | 177 | 96.1 | 100.0 | 77~80 | 1000 | 241 | ok |
| yolo26m.dxnn | 2 | 3 | 83.4 ±0.0 | 41.7 | 170 | 95.5 | 100.0 | 80~82 | 1000 | 238 | ok |
| yolo26l.dxnn | 2 | 3 | 63.8 ±2.2 | 31.9 | 136 | 95.8 | 100.0 | 76~79 | 1000 | 248 | ok |
| yolo26l.dxnn | 3 | 3 | 61.4 ±0.2 | 20.5 | 128 | 96.5 | 100.0 | 81~82 | 1000 | 257 | ok |
| yolo26x.dxnn | 1 | 3 | 38.1 ±1.1 | 38.1 | 101 | 95.5 | 100.0 | 73~79 | 1000 | 346 | ok |
| yolo26x.dxnn | 2 | 3 | 34.0 ±1.0 | 17.0 | 103 | 95.0 | 100.0 | 83 | 800~1000 | 346 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n.dxnn | 4 | 35.3 | 3 | 32.9 |
| yolo26s.dxnn | 4 | 30.2 | 3 | 32.7 |
| yolo26m.dxnn | 2 | 41.5 | 2 | 41.7 |
| yolo26l.dxnn | 2 | 31.9 | 2 | 31.9 |
| yolo26x.dxnn | 1 | 38.0 | 1 | 38.1 |

### Pose Estimation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | 6 | 3 | 184.3 ±0.5 | 30.7 | 233 | 73.8 | 86.7 | 64~67 | 1000 | 206 | ok |
| yolo26n-pose.dxnn | 7 | 3 | 185.3 ±0.6 | 26.5 | 234 | 74.7 | 84.9 | 68~69 | 1000 | 210 | ok |
| yolo26s-pose.dxnn | 4 | 3 | 126.0 ±0.0 | 31.5 | 157 | 94.8 | 100.0 | 68~72 | 1000 | 210 | ok |
| yolo26s-pose.dxnn | 5 | 3 | 126.2 ±0.1 | 25.2 | 157 | 95.4 | 100.0 | 73~75 | 1000 | 215 | ok |
| yolo26m-pose.dxnn | 2 | 3 | 85.3 ±2.9 | 42.6 | 109 | 94.4 | 100.0 | 75~78 | 1000 | 217 | ok |
| yolo26m-pose.dxnn | 3 | 3 | 81.0 ±0.3 | 27.0 | 103 | 96.3 | 100.0 | 80~82 | 1000 | 225 | ok |
| yolo26l-pose.dxnn | 2 | 3 | 62.2 ±2.1 | 31.1 | 89 | 95.4 | 100.0 | 76~79 | 1000 | 226 | ok |
| yolo26l-pose.dxnn | 3 | 3 | 60.0 ±0.2 | 20.0 | 85 | 96.5 | 100.0 | 81~82 | 1000 | 234 | ok |
| yolo26x-pose.dxnn | 1 | 3 | 37.3 ±1.0 | 37.3 | 73 | 94.9 | 100.0 | 73~79 | 1000 | 358 | ok |
| yolo26x-pose.dxnn | 2 | 3 | 33.2 ±1.0 | 16.6 | 69 | 95.1 | 100.0 | 83 | 600~1000 | 358 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | 7 | 3 | 212.1 ±1.0 | 30.3 | 178 | 91.2 | 98.1 | 60~65 | 1000 | 206 | ok |
| yolo26n-pose.dxnn | 8 | 3 | 211.7 ±0.0 | 26.5 | 183 | 90.9 | 97.6 | 68~70 | 1000 | 213 | ok |
| yolo26s-pose.dxnn | 4 | 3 | 125.6 ±0.1 | 31.4 | 119 | 95.4 | 100.0 | 68~71 | 1000 | 206 | ok |
| yolo26s-pose.dxnn | 5 | 3 | 125.5 ±0.1 | 25.1 | 120 | 95.5 | 100.0 | 72~74 | 1000 | 210 | ok |
| yolo26m-pose.dxnn | 2 | 3 | 85.5 ±2.7 | 42.8 | 95 | 94.7 | 100.0 | 74~78 | 1000 | 206 | ok |
| yolo26m-pose.dxnn | 3 | 3 | 81.1 ±0.4 | 27.0 | 89 | 96.4 | 100.0 | 80~81 | 1000 | 216 | ok |
| yolo26l-pose.dxnn | 2 | 3 | 62.2 ±2.1 | 31.1 | 86 | 95.8 | 100.0 | 76~79 | 1000 | 217 | ok |
| yolo26l-pose.dxnn | 3 | 3 | 60.2 ±0.2 | 20.1 | 79 | 96.9 | 100.0 | 80~82 | 1000 | 225 | ok |
| yolo26x-pose.dxnn | 1 | 3 | 37.3 ±1.1 | 37.3 | 68 | 95.1 | 100.0 | 73~78 | 1000 | 358 | ok |
| yolo26x-pose.dxnn | 2 | 3 | 33.1 ±1.0 | 16.6 | 64 | 95.7 | 100.0 | 83~84 | 600~1000 | 358 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-pose.dxnn | 6 | 30.7 | 7 | 30.3 |
| yolo26s-pose.dxnn | 4 | 31.5 | 4 | 31.4 |
| yolo26m-pose.dxnn | 2 | 42.6 | 2 | 42.8 |
| yolo26l-pose.dxnn | 2 | 31.1 | 2 | 31.1 |
| yolo26x-pose.dxnn | 1 | 37.3 | 1 | 37.3 |

### Segmentation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | 2 | 3 | 88.6 ±0.1 | 44.3 | 326 | 37.9 | 61.3 | 60~62 | 1000 | 289 | ok |
| yolo26n-seg.dxnn | 3 | 3 | 87.7 ±0.4 | 29.2 | 327 | 37.8 | 62.7 | 62~64 | 1000 | 304 | ok |
| yolo26s-seg.dxnn | 2 | 3 | 76.8 ±1.0 | 38.4 | 278 | 60.5 | 82.0 | 65~68 | 1000 | 305 | ok |
| yolo26s-seg.dxnn | 3 | 3 | 79.2 ±1.4 | 26.4 | 272 | 63.4 | 81.3 | 69~71 | 1000 | 319 | ok |
| yolo26m-seg.dxnn | 2 | 3 | 56.3 ±2.3 | 28.1 | 193 | 92.6 | 100.0 | 81~83 | 600~1000 | 334 | ok |
| yolo26m-seg.dxnn | 1 | 3 | 63.2 ±0.0 | 63.2 | 220 | 88.0 | 98.9 | 71~76 | 1000 | 311 | ok |
| yolo26l-seg.dxnn | 1 | 3 | 51.4 ±0.8 | 51.4 | 166 | 93.8 | 100.0 | 72~77 | 1000 | 321 | ok |
| yolo26l-seg.dxnn | 2 | 3 | 45.5 ±1.6 | 22.8 | 149 | 94.5 | 100.0 | 82~83 | 800~1000 | 344 | ok |
| yolo26x-seg.dxnn | 1 | 3 | 26.2 ±2.3 | 26.2 | 98 | 93.4 | 100.0 | 79~83 | 600~1000 | 391 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | 2 | 3 | 79.8 ±0.1 | 39.9 | 280 | 26.7 | 84.9 | 58~59 | 1000 | 323 | ok |
| yolo26n-seg.dxnn | 3 | 3 | 79.5 ±0.3 | 26.5 | 262 | 26.9 | 84.9 | 59 | 1000 | 337 | ok |
| yolo26s-seg.dxnn | 2 | 3 | 78.3 ±0.1 | 39.2 | 267 | 56.8 | 92.9 | 65~68 | 1000 | 339 | ok |
| yolo26s-seg.dxnn | 3 | 3 | 78.7 ±0.2 | 26.2 | 266 | 57.8 | 93.1 | 69~70 | 1000 | 354 | ok |
| yolo26m-seg.dxnn | 2 | 3 | 55.3 ±3.7 | 27.7 | 179 | 94.2 | 100.0 | 82~83 | 600~1000 | 349 | ok |
| yolo26m-seg.dxnn | 1 | 3 | 64.9 ±0.8 | 64.9 | 213 | 93.1 | 100.0 | 72~77 | 1000 | 326 | ok |
| yolo26l-seg.dxnn | 1 | 3 | 51.1 ±0.8 | 51.1 | 149 | 93.3 | 100.0 | 71~77 | 1000 | 347 | ok |
| yolo26l-seg.dxnn | 2 | 3 | 45.8 ±1.5 | 22.9 | 138 | 94.9 | 100.0 | 82~83 | 800~1000 | 373 | ok |
| yolo26x-seg.dxnn | 1 | 3 | 25.9 ±2.0 | 25.9 | 102 | 93.5 | 100.0 | 80~84 | 600~1000 | 406 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-seg.dxnn | 2 | 44.3 | 2 | 39.9 |
| yolo26s-seg.dxnn | 2 | 38.4 | 2 | 39.2 |
| yolo26m-seg.dxnn | 1 | 63.2 | 1 | 64.9 |
| yolo26l-seg.dxnn | 1 | 51.4 | 1 | 51.1 |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | 2 | 3 | 74.3 ±0.0 | 37.1 | 117 | 94.4 | 100.0 | 63~65 | 1000 | 208 | ok |
| yolo26n-obb.dxnn | 3 | 3 | 74.3 ±0.1 | 24.8 | 118 | 95.2 | 100.0 | 66~68 | 1000 | 219 | ok |
| yolo26s-obb.dxnn | 1 | 3 | 43.6 ±0.1 | 43.6 | 84 | 93.7 | 100.0 | 61~64 | 1000 | 209 | ok |
| yolo26s-obb.dxnn | 2 | 3 | 43.6 ±0.1 | 21.8 | 84 | 95.5 | 100.0 | 67~69 | 1000 | 227 | ok |
| yolo26m-obb.dxnn | 1 | 3 | 31.9 ±0.1 | 31.9 | 72 | 93.9 | 100.0 | 69~74 | 1000 | 231 | ok |
| yolo26m-obb.dxnn | 2 | 3 | 29.5 ±0.6 | 14.7 | 68 | 96.3 | 100.0 | 77~79 | 1000 | 246 | ok |
| yolo26l-obb.dxnn | 1 | 3 | 23.4 ±0.1 | 23.4 | 58 | 95.0 | 100.0 | 70~75 | 1000 | 241 | ok |
| yolo26x-obb.dxnn | 1 | 3 | 12.7 ±0.5 | 12.7 | 47 | 94.6 | 100.0 | 77~80 | 1000 | 366 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | 2 | 3 | 74.2 ±0.0 | 37.1 | 124 | 93.9 | 100.0 | 62~65 | 1000 | 211 | ok |
| yolo26n-obb.dxnn | 3 | 3 | 74.1 ±0.1 | 24.7 | 124 | 95.2 | 100.0 | 65~67 | 1000 | 222 | ok |
| yolo26s-obb.dxnn | 1 | 3 | 43.6 ±0.1 | 43.6 | 95 | 93.1 | 100.0 | 62~64 | 1000 | 206 | ok |
| yolo26s-obb.dxnn | 2 | 3 | 43.7 ±0.0 | 21.9 | 95 | 95.7 | 100.0 | 68~69 | 1000 | 228 | ok |
| yolo26m-obb.dxnn | 1 | 3 | 31.9 ±0.1 | 31.9 | 76 | 94.3 | 100.0 | 69~73 | 1000 | 230 | ok |
| yolo26m-obb.dxnn | 2 | 3 | 29.5 ±0.6 | 14.7 | 71 | 96.2 | 100.0 | 77~79 | 1000 | 246 | ok |
| yolo26l-obb.dxnn | 1 | 3 | 23.4 ±0.0 | 23.4 | 58 | 95.3 | 100.0 | 71~75 | 1000 | 242 | ok |
| yolo26x-obb.dxnn | 1 | 3 | 12.8 ±0.5 | 12.8 | 44 | 94.0 | 100.0 | 77~80 | 1000 | 366 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-obb.dxnn | 2 | 37.1 | 2 | 37.1 |
| yolo26s-obb.dxnn | 1 | 43.6 | 1 | 43.6 |
| yolo26m-obb.dxnn | 1 | 31.9 | 1 | 31.9 |

---
*Report generated by dx_stream benchmark tool*
