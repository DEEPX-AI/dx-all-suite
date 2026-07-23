# YOLO26 Benchmark Report

**Generated:** 2026-07-11 18:13:50 (Local)

## Test Timing

| # | Type | Start | End | Duration |
|---|------|-------|-----|----------|
| 1 | run | 2026-07-10 18:00:22 | 2026-07-11 18:13:50 | 24h 13m 27s |

## Executive Summary

### Object Detection

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n_640x640.dxnn | ON | 25.05 | 96.3 | 60.9 | 1 |
| yolo26-n_640x640.dxnn | OFF | 24.14 | 178.2 | 67.0 | 2 |
| yolo26-s_640x640.dxnn | ON | 31.15 | 96.2 | 59.8 | 1 |
| yolo26-s_640x640.dxnn | OFF | 29.60 | 148.7 | 66.6 | 2 |
| yolo26-m_640x640.dxnn | ON | 40.14 | 74.6 | 38.8 | 1 |
| yolo26-m_640x640.dxnn | OFF | 38.56 | 72.4 | 56.5 | 1 |
| yolo26-l_640x640.dxnn | ON | 48.66 | 57.0 | 60.2* | — |
| yolo26-l_640x640.dxnn | OFF | 46.10 | 57.7 | 50.1 | 1 |
| yolo26-x_640x640.dxnn | ON | 79.52 | 27.5 | 15.6 | — |
| yolo26-x_640x640.dxnn | OFF | 75.43 | 28.4 | 15.8 | — |

### Pose Estimation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-pose_640x640.dxnn | ON | 21.08 | 139.1 | 73.3 | 2 |
| yolo26-n-pose_640x640.dxnn | OFF | 19.57 | 212.6 | 99.8 | 3 |
| yolo26-s-pose_640x640.dxnn | ON | 28.34 | 134.8 | 73.0 | 2 |
| yolo26-s-pose_640x640.dxnn | OFF | 26.67 | 135.3 | 97.4 | 2 |
| yolo26-m-pose_640x640.dxnn | ON | 37.42 | 70.2 | 37.4 | 1 |
| yolo26-m-pose_640x640.dxnn | OFF | 35.05 | 68.8 | 37.9 | 1 |
| yolo26-l-pose_640x640.dxnn | ON | 45.06 | 54.5 | 37.5 | 1 |
| yolo26-l-pose_640x640.dxnn | OFF | 43.55 | 54.7 | 30.1 | 1 |
| yolo26-x-pose_640x640.dxnn | ON | 74.74 | 27.6 | 15.6 | — |
| yolo26-x-pose_640x640.dxnn | OFF | 73.07 | 27.1 | 16.0 | — |

### Segmentation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-seg_640x640.dxnn | ON | 41.44 | 61.9 | 39.6 | 1 |
| yolo26-n-seg_640x640.dxnn | OFF | 37.97 | 95.6 | 46.6 | 1 |
| yolo26-s-seg_640x640.dxnn | ON | 50.27 | 61.9 | 39.6 | 1 |
| yolo26-s-seg_640x640.dxnn | OFF | 46.91 | 93.8 | 46.3 | 1 |
| yolo26-m-seg_640x640.dxnn | ON | 65.60 | 41.5 | 21.6 | — |
| yolo26-m-seg_640x640.dxnn | OFF | 62.08 | 41.5 | 21.4 | — |
| yolo26-l-seg_640x640.dxnn | ON | 74.44 | 35.1 | 19.7 | — |
| yolo26-l-seg_640x640.dxnn | OFF | 70.57 | 35.2 | 18.9 | — |
| yolo26-x-seg_640x640.dxnn | ON | 117.01 | 16.3 | 9.6 | — |
| yolo26-x-seg_640x640.dxnn | OFF | 113.30 | 16.4 | 9.6 | — |

### Oriented BBox (OBB)

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-obb_1024x1024.dxnn | ON | 39.82 | 70.5 | 60.5 | 1 |
| yolo26-n-obb_1024x1024.dxnn | OFF | 38.63 | 70.7 | 59.8 | 1 |
| yolo26-s-obb_1024x1024.dxnn | ON | 57.87 | 43.5 | 26.8 | — |
| yolo26-s-obb_1024x1024.dxnn | OFF | 56.00 | 43.7 | 33.9 | 1 |
| yolo26-m-obb_1024x1024.dxnn | ON | 78.31 | 24.0 | 12.8 | — |
| yolo26-m-obb_1024x1024.dxnn | OFF | 76.77 | 24.2 | 12.7 | — |
| yolo26-l-obb_1024x1024.dxnn | ON | 101.37 | 18.0 | 9.8 | — |
| yolo26-l-obb_1024x1024.dxnn | OFF | 99.30 | 17.8 | 9.9 | — |
| yolo26-x-obb_1024x1024.dxnn | ON | 178.54 | 8.3 | 5.1 | — |
| yolo26-x-obb_1024x1024.dxnn | OFF | 176.51 | 8.2 | 5.2 | — |

### Classification

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n_224x224.dxnn | ON | 1.57 | 3012.2 | 174.6 | — |
| yolo26-n_224x224.dxnn | OFF | 1.52 | 3007.6 | 175.3 | — |
| yolo26-s_224x224.dxnn | ON | 2.26 | 1593.3 | 177.3 | — |
| yolo26-s_224x224.dxnn | OFF | 2.30 | 1593.4 | 177.1 | — |
| yolo26-m_224x224.dxnn | ON | 3.02 | 1053.0 | 176.7 | — |
| yolo26-m_224x224.dxnn | OFF | 3.01 | 1054.4 | 176.8 | — |
| yolo26-l_224x224.dxnn | ON | 4.37 | 700.9 | 177.2 | — |
| yolo26-l_224x224.dxnn | OFF | 4.37 | 702.1 | 177.0 | — |
| yolo26-x_224x224.dxnn | ON | 7.26 | 357.1 | 176.4 | — |
| yolo26-x_224x224.dxnn | OFF | 7.40 | 357.0 | 176.2 | — |

> **\***: value came from a degraded (partial/failed) run — see the per-family tables below for the status and reason.

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
| NPU SKU | M1M |
| NPU RT | v3.4.0 |
| NPU Driver (RT) | v2.5.1 |
| NPU Driver (PCIe) | v2.4.1 |
| NPU Firmware | v2.7.1 |
| NPU Memory | LPDDR4 4200 Mbps, 1.92GiB |
| NPU Board | M.2, Rev 0.0 |
| NPU PCIe | Gen3 X1 [01:00:00] |

### Tools

| Tool | Available | Version |
|------|-----------|---------|
| run_model | Yes | DXRT v3.4.0 run_model |
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
| Cooldown Max Time | 1000.0 s |
| NPU Warmup | 1.0 s |
| NPU Drain | 0.5 s |

## Benchmarked Models

| Model | Task | Input Size | NPU Memory (MB) | ORT CPU Offload | Multi-Stream Sweep |
|-------|------|------------|:----------------:|:---------------:|:------------------:|
| yolo26-n_640x640.dxnn | Object Detection | 640×640 | 117.8 | Yes | ✅ |
| yolo26-s_640x640.dxnn | Object Detection | 640×640 | 151.9 | Yes | ✅ |
| yolo26-m_640x640.dxnn | Object Detection | 640×640 | 244.6 | Yes | ✅ |
| yolo26-l_640x640.dxnn | Object Detection | 640×640 | 297.6 | Yes | ✅ |
| yolo26-x_640x640.dxnn | Object Detection | 640×640 | 528.8 | Yes | ✅ |
| yolo26-n-pose_640x640.dxnn | Pose Estimation | 640×640 | 119.8 | Yes | ✅ |
| yolo26-s-pose_640x640.dxnn | Pose Estimation | 640×640 | 157.9 | Yes | ✅ |
| yolo26-m-pose_640x640.dxnn | Pose Estimation | 640×640 | 256.7 | Yes | ✅ |
| yolo26-l-pose_640x640.dxnn | Pose Estimation | 640×640 | 309.6 | Yes | ✅ |
| yolo26-x-pose_640x640.dxnn | Pose Estimation | 640×640 | 522.6 | Yes | ✅ |
| yolo26-n-seg_640x640.dxnn | Segmentation | 640×640 | 140.2 | Yes | ✅ |
| yolo26-s-seg_640x640.dxnn | Segmentation | 640×640 | 177.9 | Yes | ✅ |
| yolo26-m-seg_640x640.dxnn | Segmentation | 640×640 | 272.8 | Yes | ✅ |
| yolo26-l-seg_640x640.dxnn | Segmentation | 640×640 | 325.8 | Yes | ✅ |
| yolo26-x-seg_640x640.dxnn | Segmentation | 640×640 | 561.1 | Yes | ✅ |
| yolo26-n-obb_1024x1024.dxnn | Oriented BBox (OBB) | 1024×1024 | 243.5 | Yes | ✅ |
| yolo26-s-obb_1024x1024.dxnn | Oriented BBox (OBB) | 1024×1024 | 379.6 | Yes | ✅ |
| yolo26-m-obb_1024x1024.dxnn | Oriented BBox (OBB) | 1024×1024 | 651.2 | Yes | ✅ |
| yolo26-l-obb_1024x1024.dxnn | Oriented BBox (OBB) | 1024×1024 | 799.0 | Yes | ✅ |
| yolo26-x-obb_1024x1024.dxnn | Oriented BBox (OBB) | 1024×1024 | 1330.5 | Yes | ✅ |
| yolo26-n_224x224.dxnn | Classification | 224×224 | 5.1 | No | — |
| yolo26-s_224x224.dxnn | Classification | 224×224 | 10.0 | No | — |
| yolo26-m_224x224.dxnn | Classification | 224×224 | 14.8 | No | — |
| yolo26-l_224x224.dxnn | Classification | 224×224 | 19.9 | No | — |
| yolo26-x_224x224.dxnn | Classification | 224×224 | 49.2 | No | — |

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
| yolo26-n_640x640.dxnn | 96.3 ±1.1 | 185 | 26.6 | 76.7 | 56~60 | 1000 | ok |
| yolo26-s_640x640.dxnn | 96.2 ±2.1 | 189 | 49.0 | 82.4 | 68~74 | 1000 | ok |
| yolo26-m_640x640.dxnn | 74.6 ±14.2 | 117 | 90.0 | 100.0 | 81~86 | 300~1000 | ok |
| yolo26-l_640x640.dxnn | 57.0 ±9.2 | 83 | 89.9 | 100.0 | 79~86 | 400~1000 | ok |
| yolo26-x_640x640.dxnn | 27.5 ±6.2 | 44 | 88.1 | 100.0 | 83~86 | 300~1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n_640x640.dxnn | 178.2 ±0.5 | 124 | 55.4 | 87.3 | 68~73 | 1000 | ok |
| yolo26-s_640x640.dxnn | 148.7 ±2.0 | 95 | 90.1 | 100.0 | 74~83 | 1000 | ok |
| yolo26-m_640x640.dxnn | 72.4 ±13.0 | 50 | 90.5 | 100.0 | 79~86 | 300~1000 | ok |
| yolo26-l_640x640.dxnn | 57.7 ±9.1 | 43 | 90.8 | 100.0 | 79~86 | 400~1000 | ok |
| yolo26-x_640x640.dxnn | 28.4 ±6.1 | 22 | 88.6 | 100.0 | 83~87 | 400~1000 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 139.1 ±0.6 | 183 | 44.3 | 74.9 | 65~70 | 1000 | ok |
| yolo26-s-pose_640x640.dxnn | 134.8 ±0.5 | 175 | 86.1 | 96.1 | 73~82 | 1000 | ok |
| yolo26-m-pose_640x640.dxnn | 70.2 ±11.5 | 71 | 91.3 | 100.0 | 80~86 | 400~1000 | ok |
| yolo26-l-pose_640x640.dxnn | 54.5 ±8.5 | 57 | 90.1 | 100.0 | 80~86 | 400~1000 | ok |
| yolo26-x-pose_640x640.dxnn | 27.6 ±5.5 | 30 | 88.0 | 100.0 | 82~86 | 300~1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 212.6 ±3.5 | 96 | 84.6 | 96.6 | 70~78 | 1000 | ok |
| yolo26-s-pose_640x640.dxnn | 135.3 ±1.4 | 64 | 91.4 | 100.0 | 73~82 | 1000 | ok |
| yolo26-m-pose_640x640.dxnn | 68.8 ±13.4 | 31 | 90.7 | 100.0 | 81~86 | 300~1000 | ok |
| yolo26-l-pose_640x640.dxnn | 54.7 ±8.0 | 26 | 89.6 | 100.0 | 79~86 | 400~1000 | ok |
| yolo26-x-pose_640x640.dxnn | 27.1 ±6.1 | 14 | 88.1 | 100.0 | 83~86 | 300~1000 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 61.9 ±0.3 | 222 | 21.6 | 68.8 | 62~65 | 1000 | ok |
| yolo26-s-seg_640x640.dxnn | 61.9 ±0.1 | 221 | 41.9 | 73.8 | 68~74 | 1000 | ok |
| yolo26-m-seg_640x640.dxnn | 41.5 ±11.2 | 110 | 89.1 | 100.0 | 83~86 | 200~1000 | ok |
| yolo26-l-seg_640x640.dxnn | 35.1 ±9.3 | 92 | 88.9 | 100.0 | 83~86 | 300~1000 | ok |
| yolo26-x-seg_640x640.dxnn | 16.3 ±3.9 | 43 | 88.6 | 100.0 | 84~87 | 300~1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 95.6 ±0.1 | 131 | 38.4 | 66.9 | 66~71 | 1000 | ok |
| yolo26-s-seg_640x640.dxnn | 93.8 ±0.9 | 138 | 77.8 | 90.6 | 75~84 | 800~1000 | ok |
| yolo26-m-seg_640x640.dxnn | 41.5 ±10.7 | 56 | 88.4 | 100.0 | 84~87 | 300~1000 | ok |
| yolo26-l-seg_640x640.dxnn | 35.2 ±8.3 | 52 | 88.6 | 100.0 | 83~87 | 300~1000 | ok |
| yolo26-x-seg_640x640.dxnn | 16.4 ±3.6 | 25 | 87.3 | 100.0 | 84~86 | 200~1000 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 70.5 ±0.3 | 80 | 91.4 | 100.0 | 71~79 | 1000 | ok |
| yolo26-s-obb_1024x1024.dxnn | 43.5 ±0.2 | 50 | 90.3 | 100.0 | 75~84 | 1000 | ok |
| yolo26-m-obb_1024x1024.dxnn | 24.0 ±4.1 | 27 | 89.3 | 100.0 | 82~87 | 300~1000 | ok |
| yolo26-l-obb_1024x1024.dxnn | 18.0 ±3.1 | 21 | 86.2 | 100.0 | 83~87 | 300~1000 | ok |
| yolo26-x-obb_1024x1024.dxnn | 8.3 ±1.3 | 10 | 85.6 | 100.0 | 85~87 | 300~1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 70.7 ±0.3 | 44 | 91.8 | 100.0 | 72~79 | 1000 | ok |
| yolo26-s-obb_1024x1024.dxnn | 43.7 ±0.1 | 26 | 90.6 | 100.0 | 74~83 | 1000 | ok |
| yolo26-m-obb_1024x1024.dxnn | 24.2 ±3.9 | 15 | 91.2 | 100.0 | 82~87 | 300~1000 | ok |
| yolo26-l-obb_1024x1024.dxnn | 17.8 ±3.3 | 10 | 87.0 | 100.0 | 83~87 | 300~1000 | ok |
| yolo26-x-obb_1024x1024.dxnn | 8.2 ±1.5 | 5 | 84.6 | 100.0 | 86~87 | 300~1000 | ok |

#### Classification

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n_224x224.dxnn | 3012.2 ±1.0 | 52 | 89.9 | 96.8 | 66~72 | 1000 | ok |
| yolo26-s_224x224.dxnn | 1593.3 ±2.5 | 33 | 88.9 | 97.6 | 68~74 | 1000 | ok |
| yolo26-m_224x224.dxnn | 1053.0 ±8.9 | 22 | 89.7 | 98.5 | 74~83 | 800~1000 | ok |
| yolo26-l_224x224.dxnn | 700.9 ±1.3 | 16 | 91.1 | 98.7 | 72~80 | 1000 | ok |
| yolo26-x_224x224.dxnn | 357.1 ±2.7 | 8 | 90.2 | 100.0 | 73~83 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n_224x224.dxnn | 3007.6 ±0.9 | 52 | 90.5 | 96.8 | 65~71 | 1000 | ok |
| yolo26-s_224x224.dxnn | 1593.4 ±3.6 | 32 | 89.7 | 97.5 | 68~75 | 1000 | ok |
| yolo26-m_224x224.dxnn | 1054.4 ±3.5 | 22 | 90.3 | 98.2 | 74~84 | 1000 | ok |
| yolo26-l_224x224.dxnn | 702.1 ±0.9 | 15 | 89.1 | 98.8 | 71~81 | 1000 | ok |
| yolo26-x_224x224.dxnn | 357.0 ±2.3 | 8 | 89.5 | 99.8 | 74~84 | 1000 | ok |

### Latency (Single-Core, Sync)

#### Object Detection

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_640x640.dxnn | 39.9 | 25.05 | 22.48 | 2.57 | 50 | ok |
| yolo26-s_640x640.dxnn | 32.1 | 31.15 | 28.71 | 2.44 | 58 | ok |
| yolo26-m_640x640.dxnn | 24.9 | 40.14 | 37.64 | 2.50 | 59 | ok |
| yolo26-l_640x640.dxnn | 20.6 | 48.66 | 46.07 | 2.59 | 59 | ok |
| yolo26-x_640x640.dxnn | 12.6 | 79.52 | 76.85 | 2.67 | 62 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_640x640.dxnn | 41.4 | 24.14 | 24.14 | N/A | 57 | ok |
| yolo26-s_640x640.dxnn | 33.8 | 29.60 | 29.60 | N/A | 58 | ok |
| yolo26-m_640x640.dxnn | 25.9 | 38.56 | 38.56 | N/A | 60 | ok |
| yolo26-l_640x640.dxnn | 21.7 | 46.10 | 46.10 | N/A | 59 | ok |
| yolo26-x_640x640.dxnn | 13.3 | 75.43 | 75.43 | N/A | 62 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-pose_640x640.dxnn | 47.4 | 21.08 | 19.44 | 1.64 | 56 | ok |
| yolo26-s-pose_640x640.dxnn | 35.3 | 28.34 | 26.70 | 1.64 | 57 | ok |
| yolo26-m-pose_640x640.dxnn | 26.7 | 37.42 | 35.78 | 1.64 | 59 | ok |
| yolo26-l-pose_640x640.dxnn | 22.2 | 45.06 | 43.47 | 1.59 | 60 | ok |
| yolo26-x-pose_640x640.dxnn | 13.4 | 74.74 | 73.07 | 1.67 | 62 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-pose_640x640.dxnn | 51.1 | 19.57 | 19.57 | N/A | 56 | ok |
| yolo26-s-pose_640x640.dxnn | 37.5 | 26.67 | 26.67 | N/A | 57 | ok |
| yolo26-m-pose_640x640.dxnn | 28.5 | 35.05 | 35.05 | N/A | 59 | ok |
| yolo26-l-pose_640x640.dxnn | 23.0 | 43.55 | 43.55 | N/A | 60 | ok |
| yolo26-x-pose_640x640.dxnn | 13.7 | 73.07 | 73.07 | N/A | 62 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-seg_640x640.dxnn | 24.1 | 41.44 | 38.16 | 3.28 | 57 | ok |
| yolo26-s-seg_640x640.dxnn | 19.9 | 50.27 | 47.02 | 3.25 | 58 | ok |
| yolo26-m-seg_640x640.dxnn | 15.2 | 65.60 | 62.46 | 3.15 | 60 | ok |
| yolo26-l-seg_640x640.dxnn | 13.4 | 74.44 | 71.29 | 3.15 | 61 | ok |
| yolo26-x-seg_640x640.dxnn | 8.5 | 117.01 | 113.76 | 3.24 | 65 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-seg_640x640.dxnn | 26.3 | 37.97 | 37.97 | N/A | 56 | ok |
| yolo26-s-seg_640x640.dxnn | 21.3 | 46.91 | 46.91 | N/A | 58 | ok |
| yolo26-m-seg_640x640.dxnn | 16.1 | 62.08 | 62.08 | N/A | 60 | ok |
| yolo26-l-seg_640x640.dxnn | 14.2 | 70.57 | 70.57 | N/A | 61 | ok |
| yolo26-x-seg_640x640.dxnn | 8.8 | 113.30 | 113.30 | N/A | 65 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-obb_1024x1024.dxnn | 25.1 | 39.82 | 38.07 | 1.75 | 58 | ok |
| yolo26-s-obb_1024x1024.dxnn | 17.3 | 57.87 | 56.02 | 1.85 | 60 | ok |
| yolo26-m-obb_1024x1024.dxnn | 12.8 | 78.31 | 76.51 | 1.80 | 64 | ok |
| yolo26-l-obb_1024x1024.dxnn | 9.9 | 101.37 | 99.54 | 1.83 | 65 | ok |
| yolo26-x-obb_1024x1024.dxnn | 5.6 | 178.54 | 176.62 | 1.92 | 71 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-obb_1024x1024.dxnn | 25.9 | 38.63 | 38.63 | N/A | 58 | ok |
| yolo26-s-obb_1024x1024.dxnn | 17.9 | 56.00 | 56.00 | N/A | 60 | ok |
| yolo26-m-obb_1024x1024.dxnn | 13.0 | 76.77 | 76.77 | N/A | 64 | ok |
| yolo26-l-obb_1024x1024.dxnn | 10.1 | 99.30 | 99.30 | N/A | 65 | ok |
| yolo26-x-obb_1024x1024.dxnn | 5.7 | 176.51 | 176.51 | N/A | 71 | ok |

#### Classification

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_224x224.dxnn | 638.5 | 1.57 | 1.57 | N/A | 56 | ok |
| yolo26-s_224x224.dxnn | 442.6 | 2.26 | 2.26 | N/A | 56 | ok |
| yolo26-m_224x224.dxnn | 330.7 | 3.02 | 3.02 | N/A | 56 | ok |
| yolo26-l_224x224.dxnn | 228.8 | 4.37 | 4.37 | N/A | 56 | ok |
| yolo26-x_224x224.dxnn | 137.8 | 7.26 | 7.26 | N/A | 56 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_224x224.dxnn | 658.5 | 1.52 | 1.52 | N/A | 55 | ok |
| yolo26-s_224x224.dxnn | 435.2 | 2.30 | 2.30 | N/A | 56 | ok |
| yolo26-m_224x224.dxnn | 332.3 | 3.01 | 3.01 | N/A | 56 | ok |
| yolo26-l_224x224.dxnn | 229.0 | 4.37 | 4.37 | N/A | 56 | ok |
| yolo26-x_224x224.dxnn | 135.2 | 7.40 | 7.40 | N/A | 56 | ok |

## E2E Pipeline (Single-Stream)

### Object Detection

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | avdec_h264 | 3455 | 3 | 60.9 ±1.0 | 56.72 | 317 | 18.7 | 42.5 | 62~65 | 1000 | 319 | ok |
| yolo26-s_640x640.dxnn | avdec_h264 | 3455 | 3 | 59.8 ±0.1 | 57.82 | 315 | 32.4 | 62.3 | 75~77 | 1000 | 342 | ok |
| yolo26-m_640x640.dxnn | avdec_h264 | 3455 | 3 | 38.8 ±1.0 | 89.03 | 131 | 94.3 | 100.0 | 87~88 | 200~400 | 374 | ok |
| yolo26-l_640x640.dxnn | avdec_h264 | 3455 | 2/3 | 60.2 ±0.2 | 57.38 | 256 | 81.7 | 97.4 | 75~77 | 300~1000 | 387 | partial — 2/3 runs after backfill exhausted (3 timeout, 0 unparsable over 5 attempts) |
| yolo26-x_640x640.dxnn | avdec_h264 | 3455 | 3 | 15.6 ±0.1 | 222.07 | 50 | 95.9 | 100.0 | 87 | 200~400 | 480 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | avdec_h264 | 3455 | 3 | 67.0 ±0.4 | 51.60 | 300 | 18.3 | 58.2 | 69~70 | 1000 | 350 | ok |
| yolo26-s_640x640.dxnn | avdec_h264 | 3455 | 3 | 66.6 ±1.1 | 51.86 | 299 | 33.2 | 73.8 | 81 | 1000 | 373 | ok |
| yolo26-m_640x640.dxnn | avdec_h264 | 3455 | 3 | 56.5 ±14.9 | 61.20 | 231 | 84.9 | 100.0 | 82~87 | 200~1000 | 400 | ok |
| yolo26-l_640x640.dxnn | avdec_h264 | 3455 | 3 | 50.1 ±14.1 | 68.99 | 191 | 92.6 | 100.0 | 77~87 | 200~1000 | 402 | ok |
| yolo26-x_640x640.dxnn | avdec_h264 | 3455 | 3 | 15.8 ±0.3 | 219.22 | 56 | 95.6 | 100.0 | 87~88 | 200~600 | 494 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n_640x640.dxnn | 60.9 | 67.0 | -6.0 | -9.0% |
| yolo26-s_640x640.dxnn | 59.8 | 66.6 | -6.9 | -10.3% |
| yolo26-m_640x640.dxnn | 38.8 | 56.5 | -17.6 | -31.3% |
| yolo26-l_640x640.dxnn | 60.2 | 50.1 | +10.1 | +20.2% |
| yolo26-x_640x640.dxnn | 15.6 | 15.8 | -0.2 | -1.3% |

### Pose Estimation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 73.3 ±0.6 | 47.12 | 321 | 23.9 | 53.0 | 70~71 | 1000 | 310 | ok |
| yolo26-s-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 73.0 ±0.5 | 47.33 | 318 | 43.0 | 69.5 | 82 | 1000 | 334 | ok |
| yolo26-m-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 37.4 ±0.8 | 92.48 | 99 | 94.8 | 100.0 | 87 | 200~600 | 364 | ok |
| yolo26-l-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 37.5 ±11.2 | 92.13 | 104 | 94.5 | 100.0 | 86~88 | 200~1000 | 380 | ok |
| yolo26-x-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 15.6 ±0.2 | 221.76 | 43 | 94.4 | 100.0 | 87 | 200~600 | 475 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 99.8 ±1.7 | 34.62 | 302 | 32.3 | 62.3 | 76 | 1000 | 288 | ok |
| yolo26-s-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 97.4 ±8.4 | 35.47 | 280 | 70.7 | 100.0 | 85~87 | 300~1000 | 323 | ok |
| yolo26-m-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 37.9 ±1.1 | 91.12 | 83 | 95.0 | 100.0 | 87 | 200~400 | 354 | ok |
| yolo26-l-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 30.1 ±0.2 | 114.86 | 67 | 95.4 | 100.0 | 87 | 200~500 | 368 | ok |
| yolo26-x-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 16.0 ±0.4 | 216.03 | 37 | 94.1 | 100.0 | 87~88 | 200~400 | 462 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-pose_640x640.dxnn | 73.3 | 99.8 | -26.5 | -26.5% |
| yolo26-s-pose_640x640.dxnn | 73.0 | 97.4 | -24.4 | -25.1% |
| yolo26-m-pose_640x640.dxnn | 37.4 | 37.9 | -0.6 | -1.5% |
| yolo26-l-pose_640x640.dxnn | 37.5 | 30.1 | +7.4 | +24.7% |
| yolo26-x-pose_640x640.dxnn | 15.6 | 16.0 | -0.4 | -2.6% |

### Segmentation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 39.6 ±0.2 | 87.19 | 320 | 16.2 | 37.7 | 67~69 | 1000 | 419 | ok |
| yolo26-s-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 39.6 ±0.2 | 87.34 | 309 | 29.0 | 57.9 | 78~80 | 1000 | 442 | ok |
| yolo26-m-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 21.6 ±0.1 | 159.97 | 97 | 96.4 | 100.0 | 87 | 200~400 | 474 | ok |
| yolo26-l-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 19.7 ±2.0 | 175.19 | 90 | 94.4 | 100.0 | 87 | 200~800 | 488 | ok |
| yolo26-x-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 9.6 ±0.2 | 359.56 | 46 | 93.4 | 100.0 | 87~88 | 200~500 | 597 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 46.6 ±0.7 | 74.13 | 339 | 17.0 | 52.7 | 70~71 | 1000 | 460 | ok |
| yolo26-s-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 46.3 ±0.6 | 74.65 | 334 | 31.4 | 74.7 | 83~84 | 1000 | 483 | ok |
| yolo26-m-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 21.4 ±0.3 | 161.71 | 99 | 96.7 | 100.0 | 87~88 | 200~600 | 489 | ok |
| yolo26-l-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 18.9 ±0.5 | 182.47 | 90 | 94.6 | 100.0 | 87 | 200~700 | 503 | ok |
| yolo26-x-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 9.6 ±0.1 | 361.14 | 47 | 93.7 | 100.0 | 87 | 200~600 | 612 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-seg_640x640.dxnn | 39.6 | 46.6 | -7.0 | -15.0% |
| yolo26-s-seg_640x640.dxnn | 39.6 | 46.3 | -6.7 | -14.5% |
| yolo26-m-seg_640x640.dxnn | 21.6 | 21.4 | +0.2 | +1.1% |
| yolo26-l-seg_640x640.dxnn | 19.7 | 18.9 | +0.8 | +4.1% |
| yolo26-x-seg_640x640.dxnn | 9.6 | 9.6 | +0.0 | +0.4% |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 60.5 ±1.1 | 43.62 | 306 | 67.5 | 91.2 | 82~87 | 800~1000 | 342 | ok |
| yolo26-s-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 26.8 ±0.9 | 98.44 | 95 | 93.8 | 100.0 | 87 | 200~400 | 374 | ok |
| yolo26-m-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 12.8 ±0.1 | 207.02 | 44 | 94.5 | 100.0 | 87~88 | 200~400 | 405 | ok |
| yolo26-l-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 9.8 ±0.1 | 270.87 | 35 | 95.0 | 100.0 | 87 | 200~600 | 420 | ok |
| yolo26-x-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 5.1 ±0.0 | 515.69 | 20 | 85.2 | 100.0 | 87~88 | 200~400 | 522 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 59.8 ±8.9 | 44.12 | 224 | 91.5 | 100.0 | 86~87 | 300~1000 | 339 | ok |
| yolo26-s-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 33.9 ±8.8 | 77.93 | 119 | 93.2 | 100.0 | 84~87 | 200~1000 | 366 | ok |
| yolo26-m-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 12.7 ±0.0 | 207.88 | 44 | 94.5 | 100.0 | 87~88 | 200~300 | 403 | ok |
| yolo26-l-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 9.9 ±0.1 | 267.84 | 36 | 95.2 | 100.0 | 87~88 | 200~400 | 419 | ok |
| yolo26-x-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 5.2 ±0.0 | 509.86 | 19 | 85.6 | 100.0 | 87 | 200~600 | 524 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-obb_1024x1024.dxnn | 60.5 | 59.8 | +0.7 | +1.2% |
| yolo26-s-obb_1024x1024.dxnn | 26.8 | 33.9 | -7.1 | -20.8% |
| yolo26-m-obb_1024x1024.dxnn | 12.8 | 12.7 | +0.1 | +0.4% |
| yolo26-l-obb_1024x1024.dxnn | 9.8 | 9.9 | -0.1 | -1.1% |
| yolo26-x-obb_1024x1024.dxnn | 5.1 | 5.2 | -0.1 | -1.2% |

### Classification

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_224x224.dxnn | avdec_h264 | 3455 | 3 | 174.6 ±2.4 | 19.78 | 271 | 4.4 | 13.6 | 65~67 | 1000 | 216 | ok |
| yolo26-s_224x224.dxnn | avdec_h264 | 3455 | 3 | 177.3 ±0.3 | 19.49 | 271 | 8.4 | 24.6 | 66~68 | 1000 | 227 | ok |
| yolo26-m_224x224.dxnn | avdec_h264 | 3455 | 3 | 176.7 ±0.5 | 19.55 | 269 | 12.2 | 33.7 | 74~77 | 1000 | 246 | ok |
| yolo26-l_224x224.dxnn | avdec_h264 | 3455 | 3 | 177.2 ±0.6 | 19.50 | 270 | 19.4 | 47.3 | 72~74 | 1000 | 238 | ok |
| yolo26-x_224x224.dxnn | avdec_h264 | 3455 | 3 | 176.4 ±0.3 | 19.59 | 268 | 37.0 | 65.0 | 80~81 | 1000 | 287 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_224x224.dxnn | avdec_h264 | 3455 | 3 | 175.3 ±2.1 | 19.71 | 272 | 4.5 | 13.8 | 64~66 | 1000 | 203 | ok |
| yolo26-s_224x224.dxnn | avdec_h264 | 3455 | 3 | 177.1 ±0.6 | 19.51 | 271 | 8.6 | 24.5 | 66~68 | 1000 | 219 | ok |
| yolo26-m_224x224.dxnn | avdec_h264 | 3455 | 3 | 176.8 ±0.4 | 19.55 | 270 | 12.3 | 34.1 | 73~76 | 1000 | 227 | ok |
| yolo26-l_224x224.dxnn | avdec_h264 | 3455 | 3 | 177.0 ±0.3 | 19.52 | 270 | 19.4 | 46.8 | 73~75 | 1000 | 238 | ok |
| yolo26-x_224x224.dxnn | avdec_h264 | 3455 | 3 | 176.2 ±0.5 | 19.61 | 268 | 35.2 | 66.3 | 60~64 | 1000 | 296 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n_224x224.dxnn | 174.6 | 175.3 | -0.7 | -0.4% |
| yolo26-s_224x224.dxnn | 177.3 | 177.1 | +0.2 | +0.1% |
| yolo26-m_224x224.dxnn | 176.7 | 176.8 | -0.1 | -0.0% |
| yolo26-l_224x224.dxnn | 177.2 | 177.0 | +0.2 | +0.1% |
| yolo26-x_224x224.dxnn | 176.4 | 176.2 | +0.2 | +0.1% |

## E2E Pipeline (Multi-Stream)

### Object Detection

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | 2 | 3 | 59.3 ±0.2 | 29.6 | 316 | 18.5 | 44.0 | 68~69 | 1000 | 458 | ok |
| yolo26-n_640x640.dxnn | 1 | 3 | 60.9 ±1.0 | 60.9 | 317 | 18.7 | 42.5 | 62~65 | 1000 | 319 | ok |
| yolo26-s_640x640.dxnn | 1 | 3 | 59.8 ±0.1 | 59.8 | 315 | 32.4 | 62.3 | 75~77 | 1000 | 342 | ok |
| yolo26-s_640x640.dxnn | 2 | 3 | 59.0 ±0.1 | 29.5 | 313 | 32.5 | 62.3 | 78~79 | 1000 | 476 | ok |
| yolo26-m_640x640.dxnn | 1 | 3 | 38.8 ±1.0 | 38.8 | 131 | 94.3 | 100.0 | 87~88 | 200~400 | 374 | ok |
| yolo26-m_640x640.dxnn | 2 | 3 | 36.1 ±0.1 | 18.1 | 126 | 95.6 | 100.0 | 87 | 200~600 | 507 | ok |
| yolo26-l_640x640.dxnn | 2 | 3 | 29.4 ±0.6 | 14.7 | 94 | 96.2 | 100.0 | 87~88 | 200~700 | 520 | ok |
| yolo26-l_640x640.dxnn | 1 | 2/3 | 60.2 ±0.2 | 60.2 | 256 | 81.7 | 97.4 | 75~77 | 300~1000 | 387 | partial |
| yolo26-x_640x640.dxnn | 1 | 3 | 15.6 ±0.1 | 15.6 | 50 | 95.9 | 100.0 | 87 | 200~400 | 480 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | 2 | 3 | 64.8 ±0.6 | 32.4 | 299 | 18.2 | 56.7 | 68~69 | 1000 | 484 | ok |
| yolo26-n_640x640.dxnn | 3 | 3 | 64.5 ±0.8 | 21.5 | 294 | 18.3 | 58.5 | 69~71 | 1000 | 581 | ok |
| yolo26-s_640x640.dxnn | 2 | 3 | 63.8 ±0.2 | 31.9 | 301 | 32.3 | 72.9 | 81 | 1000 | 502 | ok |
| yolo26-s_640x640.dxnn | 3 | 3 | 63.3 ±0.2 | 21.1 | 299 | 32.3 | 76.8 | 81~82 | 1000 | 602 | ok |
| yolo26-m_640x640.dxnn | 1 | 3 | 56.5 ±14.9 | 56.5 | 231 | 84.9 | 100.0 | 82~87 | 200~1000 | 400 | ok |
| yolo26-m_640x640.dxnn | 2 | 3 | 36.7 ±0.2 | 18.4 | 144 | 96.2 | 100.0 | 87~88 | 200~700 | 519 | ok |
| yolo26-l_640x640.dxnn | 1 | 3 | 50.1 ±14.1 | 50.1 | 191 | 92.6 | 100.0 | 77~87 | 200~1000 | 402 | ok |
| yolo26-l_640x640.dxnn | 2 | 3 | 28.6 ±0.4 | 14.3 | 106 | 96.4 | 100.0 | 87 | 200~600 | 531 | ok |
| yolo26-x_640x640.dxnn | 1 | 3 | 15.8 ±0.3 | 15.8 | 56 | 95.6 | 100.0 | 87~88 | 200~600 | 494 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n_640x640.dxnn | 1 | 60.9 | 2 | 32.4 |
| yolo26-s_640x640.dxnn | 1 | 59.8 | 2 | 31.9 |
| yolo26-m_640x640.dxnn | 1 | 38.8 | 1 | 56.5 |
| yolo26-l_640x640.dxnn | < 1 | — | 1 | 50.1 |

### Pose Estimation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 2 | 3 | 71.7 ±0.4 | 35.9 | 325 | 24.5 | 50.3 | 72~73 | 1000 | 449 | ok |
| yolo26-n-pose_640x640.dxnn | 3 | 3 | 71.7 ±0.4 | 23.9 | 325 | 24.8 | 52.6 | 73~74 | 1000 | 552 | ok |
| yolo26-s-pose_640x640.dxnn | 2 | 3 | 71.6 ±0.1 | 35.8 | 320 | 43.0 | 70.6 | 85~86 | 800~1000 | 471 | ok |
| yolo26-s-pose_640x640.dxnn | 3 | 3 | 71.6 ±0.3 | 23.9 | 320 | 44.9 | 79.9 | 86~87 | 400~1000 | 573 | ok |
| yolo26-m-pose_640x640.dxnn | 1 | 3 | 37.4 ±0.8 | 37.4 | 99 | 94.8 | 100.0 | 87 | 200~600 | 364 | ok |
| yolo26-m-pose_640x640.dxnn | 2 | 3 | 35.5 ±0.3 | 17.7 | 102 | 96.6 | 100.0 | 87 | 200~400 | 500 | ok |
| yolo26-l-pose_640x640.dxnn | 1 | 3 | 37.5 ±11.2 | 37.5 | 104 | 94.5 | 100.0 | 86~88 | 200~1000 | 380 | ok |
| yolo26-l-pose_640x640.dxnn | 2 | 3 | 28.1 ±0.4 | 14.1 | 78 | 96.0 | 100.0 | 87 | 200~700 | 513 | ok |
| yolo26-x-pose_640x640.dxnn | 1 | 3 | 15.6 ±0.2 | 15.6 | 43 | 94.4 | 100.0 | 87 | 200~600 | 475 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 3 | 3 | 98.0 ±1.0 | 32.6 | 333 | 35.6 | 56.8 | 78 | 1000 | 544 | ok |
| yolo26-n-pose_640x640.dxnn | 4 | 3 | 96.7 ±0.1 | 24.2 | 335 | 34.9 | 58.2 | 79 | 1000 | 646 | ok |
| yolo26-s-pose_640x640.dxnn | 3 | 3 | 76.5 ±0.7 | 25.5 | 210 | 95.4 | 100.0 | 87~88 | 300~900 | 563 | ok |
| yolo26-s-pose_640x640.dxnn | 2 | 3 | 76.1 ±2.5 | 38.0 | 212 | 94.1 | 100.0 | 87~88 | 300~700 | 458 | ok |
| yolo26-m-pose_640x640.dxnn | 1 | 3 | 37.9 ±1.1 | 37.9 | 83 | 95.0 | 100.0 | 87 | 200~400 | 354 | ok |
| yolo26-m-pose_640x640.dxnn | 2 | 3 | 35.8 ±0.6 | 17.9 | 84 | 96.6 | 100.0 | 87 | 200~500 | 489 | ok |
| yolo26-l-pose_640x640.dxnn | 1 | 3 | 30.1 ±0.2 | 30.1 | 67 | 95.4 | 100.0 | 87 | 200~500 | 368 | ok |
| yolo26-l-pose_640x640.dxnn | 2 | 3 | 28.7 ±0.4 | 14.4 | 66 | 96.6 | 100.0 | 87~88 | 200~400 | 500 | ok |
| yolo26-x-pose_640x640.dxnn | 1 | 3 | 16.0 ±0.4 | 16.0 | 37 | 94.1 | 100.0 | 87~88 | 200~400 | 462 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-pose_640x640.dxnn | 2 | 35.9 | 3 | 32.6 |
| yolo26-s-pose_640x640.dxnn | 2 | 35.8 | 2 | 38.0 |
| yolo26-m-pose_640x640.dxnn | 1 | 37.4 | 1 | 37.9 |
| yolo26-l-pose_640x640.dxnn | 1 | 37.5 | 1 | 30.1 |

### Segmentation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 1 | 3 | 39.6 ±0.2 | 39.6 | 320 | 16.2 | 37.7 | 67~69 | 1000 | 419 | ok |
| yolo26-n-seg_640x640.dxnn | 2 | 3 | 39.3 ±0.0 | 19.6 | 321 | 16.1 | 38.1 | 70 | 1000 | 562 | ok |
| yolo26-s-seg_640x640.dxnn | 1 | 3 | 39.6 ±0.2 | 39.6 | 309 | 29.0 | 57.9 | 78~80 | 1000 | 442 | ok |
| yolo26-s-seg_640x640.dxnn | 2 | 3 | 38.9 ±0.1 | 19.4 | 315 | 28.6 | 59.8 | 82 | 1000 | 590 | ok |
| yolo26-m-seg_640x640.dxnn | 1 | 3 | 21.6 ±0.1 | 21.6 | 97 | 96.4 | 100.0 | 87 | 200~400 | 474 | ok |
| yolo26-l-seg_640x640.dxnn | 1 | 3 | 19.7 ±2.0 | 19.7 | 90 | 94.4 | 100.0 | 87 | 200~800 | 488 | ok |
| yolo26-x-seg_640x640.dxnn | 1 | 3 | 9.6 ±0.2 | 9.6 | 46 | 93.4 | 100.0 | 87~88 | 200~500 | 597 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 1 | 3 | 46.6 ±0.7 | 46.6 | 339 | 17.0 | 52.7 | 70~71 | 1000 | 460 | ok |
| yolo26-n-seg_640x640.dxnn | 2 | 3 | 45.4 ±0.1 | 22.7 | 336 | 16.6 | 51.6 | 73 | 1000 | 604 | ok |
| yolo26-s-seg_640x640.dxnn | 1 | 3 | 46.3 ±0.6 | 46.3 | 334 | 31.4 | 74.7 | 83~84 | 1000 | 483 | ok |
| yolo26-s-seg_640x640.dxnn | 2 | 3 | 45.3 ±0.6 | 22.7 | 329 | 30.8 | 74.4 | 85~86 | 600~1000 | 626 | ok |
| yolo26-m-seg_640x640.dxnn | 1 | 3 | 21.4 ±0.3 | 21.4 | 99 | 96.7 | 100.0 | 87~88 | 200~600 | 489 | ok |
| yolo26-l-seg_640x640.dxnn | 1 | 3 | 18.9 ±0.5 | 18.9 | 90 | 94.6 | 100.0 | 87 | 200~700 | 503 | ok |
| yolo26-x-seg_640x640.dxnn | 1 | 3 | 9.6 ±0.1 | 9.6 | 47 | 93.7 | 100.0 | 87 | 200~600 | 612 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-seg_640x640.dxnn | 1 | 39.6 | 1 | 46.6 |
| yolo26-s-seg_640x640.dxnn | 1 | 39.6 | 1 | 46.3 |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 2 | 3 | 46.1 ±0.6 | 23.1 | 206 | 94.2 | 100.0 | 88 | 200~800 | 484 | ok |
| yolo26-n-obb_1024x1024.dxnn | 1 | 3 | 60.5 ±1.1 | 60.5 | 306 | 67.5 | 91.2 | 82~87 | 800~1000 | 342 | ok |
| yolo26-s-obb_1024x1024.dxnn | 1 | 3 | 26.8 ±0.9 | 26.8 | 95 | 93.8 | 100.0 | 87 | 200~400 | 374 | ok |
| yolo26-m-obb_1024x1024.dxnn | 1 | 3 | 12.8 ±0.1 | 12.8 | 44 | 94.5 | 100.0 | 87~88 | 200~400 | 405 | ok |
| yolo26-l-obb_1024x1024.dxnn | 1 | 3 | 9.8 ±0.1 | 9.8 | 35 | 95.0 | 100.0 | 87 | 200~600 | 420 | ok |
| yolo26-x-obb_1024x1024.dxnn | 1 | 3 | 5.1 ±0.0 | 5.1 | 20 | 85.2 | 100.0 | 87~88 | 200~400 | 522 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 1 | 3 | 59.8 ±8.9 | 59.8 | 224 | 91.5 | 100.0 | 86~87 | 300~1000 | 339 | ok |
| yolo26-n-obb_1024x1024.dxnn | 2 | 3 | 46.5 ±2.1 | 23.3 | 190 | 94.8 | 100.0 | 87~88 | 200~700 | 478 | ok |
| yolo26-s-obb_1024x1024.dxnn | 1 | 3 | 33.9 ±8.8 | 33.9 | 119 | 93.2 | 100.0 | 84~87 | 200~1000 | 366 | ok |
| yolo26-s-obb_1024x1024.dxnn | 2 | 3 | 24.4 ±0.1 | 12.2 | 89 | 95.0 | 100.0 | 87~88 | 200~700 | 505 | ok |
| yolo26-m-obb_1024x1024.dxnn | 1 | 3 | 12.7 ±0.0 | 12.7 | 44 | 94.5 | 100.0 | 87~88 | 200~300 | 403 | ok |
| yolo26-l-obb_1024x1024.dxnn | 1 | 3 | 9.9 ±0.1 | 9.9 | 36 | 95.2 | 100.0 | 87~88 | 200~400 | 419 | ok |
| yolo26-x-obb_1024x1024.dxnn | 1 | 3 | 5.2 ±0.0 | 5.2 | 19 | 85.6 | 100.0 | 87 | 200~600 | 524 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-obb_1024x1024.dxnn | 1 | 60.5 | 1 | 59.8 |
| yolo26-s-obb_1024x1024.dxnn | < 1 | — | 1 | 33.9 |

---
*Report generated by dx-benchmark tool*
