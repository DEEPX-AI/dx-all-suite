# YOLO26 Benchmark Report

**Generated:** 2026-07-15 17:15:40 (Local)

## Test Timing

| # | Type | Start | End | Duration |
|---|------|-------|-----|----------|
| 1 | run | 2026-07-14 21:59:44 | 2026-07-15 17:15:40 | 19h 15m 55s |

## Executive Summary

### Object Detection

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n_640x640.dxnn | ON | 31.20 | 180.7 | 147.3 | 4 |
| yolo26-n_640x640.dxnn | OFF | 33.89 | 285.5 | 98.3 | 3 |
| yolo26-s_640x640.dxnn | ON | 50.14 | 173.8 | 126.7 | 4 |
| yolo26-s_640x640.dxnn | OFF | 52.97 | 195.6 | 99.1 | 3 |
| yolo26-m_640x640.dxnn | ON | 56.83 | 117.4 | 98.1 | 3 |
| yolo26-m_640x640.dxnn | OFF | 53.34 | 118.5 | 98.1 | 3 |
| yolo26-l_640x640.dxnn | ON | 72.31 | 89.5 | 80.0 | 2 |
| yolo26-l_640x640.dxnn | OFF | 66.17 | 87.3 | 88.1 | 2 |
| yolo26-x_640x640.dxnn | ON | 96.92 | 48.9 | 46.5 | 1 |
| yolo26-x_640x640.dxnn | OFF | 88.69 | 48.7 | 47.6 | 1 |

### Pose Estimation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-pose_640x640.dxnn | ON | 28.70 | 250.6 | 198.5 | 6 |
| yolo26-n-pose_640x640.dxnn | OFF | 27.01 | 290.7 | 249.1 | 8 |
| yolo26-s-pose_640x640.dxnn | ON | 41.57 | 179.2 | 148.3 | 5 |
| yolo26-s-pose_640x640.dxnn | OFF | 39.01 | 180.4 | 168.8 | 5 |
| yolo26-m-pose_640x640.dxnn | ON | 47.58 | 114.6 | 107.3 | 3 |
| yolo26-m-pose_640x640.dxnn | OFF | 42.76 | 111.1 | 110.6 | 3 |
| yolo26-l-pose_640x640.dxnn | ON | 55.34 | 86.1 | 84.0 | 2 |
| yolo26-l-pose_640x640.dxnn | OFF | 53.75 | 84.9 | 84.0 | 2 |
| yolo26-x-pose_640x640.dxnn | ON | 91.31 | 46.9 | 46.5 | 1 |
| yolo26-x-pose_640x640.dxnn | OFF | 80.66 | 47.0 | 47.1 | 1 |

### Segmentation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-seg_640x640.dxnn | ON | 47.28 | 126.9 | 99.3 | 3 |
| yolo26-n-seg_640x640.dxnn | OFF | 48.93 | 160.3 | 84.5 | 2 |
| yolo26-s-seg_640x640.dxnn | ON | 59.58 | 113.4 | 87.3 | 2 |
| yolo26-s-seg_640x640.dxnn | OFF | 58.50 | 132.1 | 82.8 | 2 |
| yolo26-m-seg_640x640.dxnn | ON | 81.70 | 77.7 | 64.9 | 1 |
| yolo26-m-seg_640x640.dxnn | OFF | 74.71 | 79.8 | 74.5 | 1 |
| yolo26-l-seg_640x640.dxnn | ON | 91.14 | 64.7 | 57.4 | 1 |
| yolo26-l-seg_640x640.dxnn | OFF | 83.16 | 64.6 | 62.3 | 1 |
| yolo26-x-seg_640x640.dxnn | ON | 126.33 | 34.9 | 28.7 | — |
| yolo26-x-seg_640x640.dxnn | OFF | 118.04 | 34.6 | 28.8 | — |

### Oriented BBox (OBB)

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-obb_1024x1024.dxnn | ON | 48.81 | 102.9 | 91.5 | 3 |
| yolo26-n-obb_1024x1024.dxnn | OFF | 43.73 | 98.9 | 100.2 | 3 |
| yolo26-s-obb_1024x1024.dxnn | ON | 76.96 | 62.1 | 61.6 | 2 |
| yolo26-s-obb_1024x1024.dxnn | OFF | 68.50 | 62.2 | 62.3 | 2 |
| yolo26-m-obb_1024x1024.dxnn | ON | 87.77 | 40.5 | 41.2 | 1 |
| yolo26-m-obb_1024x1024.dxnn | OFF | 82.62 | 40.1 | 41.9 | 1 |
| yolo26-l-obb_1024x1024.dxnn | ON | 104.92 | 30.2 | 30.5 | 1 |
| yolo26-l-obb_1024x1024.dxnn | OFF | 101.48 | 29.6 | 30.5 | 1 |
| yolo26-x-obb_1024x1024.dxnn | ON | 175.51 | 16.5 | 15.9 | — |
| yolo26-x-obb_1024x1024.dxnn | OFF | 169.98 | 16.6 | 16.1 | — |

### Classification

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n_224x224.dxnn | ON | 3.75 | 3414.0 | 1074.5 | — |
| yolo26-n_224x224.dxnn | OFF | 3.93 | 3417.1* | 1067.5 | — |
| yolo26-s_224x224.dxnn | ON | 3.29 | 1990.2 | 1055.8 | — |
| yolo26-s_224x224.dxnn | OFF | 4.70 | 1989.1 | 1060.5 | — |
| yolo26-m_224x224.dxnn | ON | 4.51 | 1377.4 | 1054.9 | — |
| yolo26-m_224x224.dxnn | OFF | 5.38 | 1378.0 | 1053.3 | — |
| yolo26-l_224x224.dxnn | ON | 6.25 | 874.5 | 864.2 | — |
| yolo26-l_224x224.dxnn | OFF | 6.78 | 875.3 | 865.4 | — |
| yolo26-x_224x224.dxnn | ON | 8.61 | 484.3 | 482.0 | — |
| yolo26-x_224x224.dxnn | OFF | 9.38 | 484.0 | 481.5 | — |

> **\***: value came from a degraded (partial/failed) run — see the per-family tables below for the status and reason.

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
| NPU RT | v3.4.0 |
| NPU Driver (RT) | v2.5.1 |
| NPU Driver (PCIe) | v2.4.1 |
| NPU Firmware | v2.7.1 |
| NPU Memory | LPDDR5 5600 Mbps, 3.92GiB |
| NPU Board | M.2, Rev 1.0 |
| NPU PCIe | Gen3 X4 [01:00:00] |

### Tools

| Tool | Available | Version |
|------|-----------|---------|
| run_model | Yes | DXRT v3.4.0 run_model |
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
| yolo26-n_640x640.dxnn | 180.7 ±1.1 | 227 | 43.2 | 71.4 | 44~48 | 1000 | ok |
| yolo26-s_640x640.dxnn | 173.8 ±1.1 | 203 | 79.4 | 92.0 | 56~59 | 1000 | ok |
| yolo26-m_640x640.dxnn | 117.4 ±0.1 | 173 | 86.8 | 100.0 | 60~65 | 1000 | ok |
| yolo26-l_640x640.dxnn | 89.5 ±0.3 | 156 | 89.9 | 100.0 | 59~64 | 1000 | ok |
| yolo26-x_640x640.dxnn | 48.9 ±0.3 | 122 | 88.7 | 100.0 | 60~65 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n_640x640.dxnn | 285.5 ±4.5 | 184 | 78.4 | 92.4 | 55~58 | 1000 | ok |
| yolo26-s_640x640.dxnn | 195.6 ±1.2 | 145 | 89.0 | 100.0 | 56~60 | 1000 | ok |
| yolo26-m_640x640.dxnn | 118.5 ±0.5 | 113 | 91.0 | 100.0 | 60~65 | 1000 | ok |
| yolo26-l_640x640.dxnn | 87.3 ±0.8 | 107 | 89.4 | 100.0 | 59~63 | 1000 | ok |
| yolo26-x_640x640.dxnn | 48.7 ±0.1 | 78 | 88.8 | 100.0 | 60~65 | 1000 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 250.6 ±2.6 | 225 | 72.9 | 86.4 | 54~57 | 1000 | ok |
| yolo26-s-pose_640x640.dxnn | 179.2 ±0.7 | 177 | 88.1 | 99.8 | 56~60 | 1000 | ok |
| yolo26-m-pose_640x640.dxnn | 114.6 ±0.2 | 150 | 88.6 | 100.0 | 60~64 | 1000 | ok |
| yolo26-l-pose_640x640.dxnn | 86.1 ±0.5 | 133 | 89.1 | 100.0 | 59~64 | 1000 | ok |
| yolo26-x-pose_640x640.dxnn | 46.9 ±0.4 | 98 | 88.9 | 100.0 | 61~66 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 290.7 ±2.3 | 147 | 87.7 | 98.6 | 55~58 | 1000 | ok |
| yolo26-s-pose_640x640.dxnn | 180.4 ±0.4 | 123 | 89.5 | 100.0 | 56~60 | 1000 | ok |
| yolo26-m-pose_640x640.dxnn | 111.1 ±1.4 | 105 | 92.5 | 100.0 | 60~64 | 1000 | ok |
| yolo26-l-pose_640x640.dxnn | 84.9 ±1.5 | 102 | 92.1 | 100.0 | 60~64 | 1000 | ok |
| yolo26-x-pose_640x640.dxnn | 47.0 ±0.9 | 65 | 89.1 | 100.0 | 60~65 | 1000 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 126.9 ±1.0 | 291 | 39.0 | 68.1 | 53~54 | 1000 | ok |
| yolo26-s-seg_640x640.dxnn | 113.4 ±1.9 | 242 | 68.8 | 86.4 | 56~59 | 1000 | ok |
| yolo26-m-seg_640x640.dxnn | 77.7 ±0.1 | 191 | 87.2 | 100.0 | 61~66 | 1000 | ok |
| yolo26-l-seg_640x640.dxnn | 64.7 ±0.1 | 164 | 88.2 | 100.0 | 60~65 | 1000 | ok |
| yolo26-x-seg_640x640.dxnn | 34.9 ±0.2 | 112 | 89.5 | 100.0 | 62~67 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 160.3 ±17.9 | 208 | 52.1 | 81.6 | 54~56 | 1000 | ok |
| yolo26-s-seg_640x640.dxnn | 132.1 ±3.7 | 188 | 83.2 | 98.5 | 56~60 | 1000 | ok |
| yolo26-m-seg_640x640.dxnn | 79.8 ±0.2 | 133 | 89.7 | 100.0 | 61~67 | 1000 | ok |
| yolo26-l-seg_640x640.dxnn | 64.6 ±0.3 | 129 | 89.1 | 100.0 | 61~65 | 1000 | ok |
| yolo26-x-seg_640x640.dxnn | 34.6 ±0.2 | 83 | 88.8 | 100.0 | 62~67 | 1000 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 102.9 ±0.2 | 152 | 88.1 | 100.0 | 54~57 | 1000 | ok |
| yolo26-s-obb_1024x1024.dxnn | 62.1 ±1.1 | 118 | 88.6 | 100.0 | 55~58 | 1000 | ok |
| yolo26-m-obb_1024x1024.dxnn | 40.5 ±0.5 | 100 | 88.8 | 100.0 | 59~63 | 1000 | ok |
| yolo26-l-obb_1024x1024.dxnn | 30.2 ±0.6 | 90 | 88.5 | 100.0 | 59~63 | 1000 | ok |
| yolo26-x-obb_1024x1024.dxnn | 16.5 ±0.0 | 53 | 85.3 | 100.0 | 60~64 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 98.9 ±0.2 | 103 | 91.9 | 100.0 | 54~56 | 1000 | ok |
| yolo26-s-obb_1024x1024.dxnn | 62.2 ±1.4 | 88 | 89.3 | 100.0 | 55~58 | 1000 | ok |
| yolo26-m-obb_1024x1024.dxnn | 40.1 ±0.8 | 65 | 90.0 | 100.0 | 59~63 | 1000 | ok |
| yolo26-l-obb_1024x1024.dxnn | 29.6 ±0.0 | 51 | 89.9 | 100.0 | 59~62 | 1000 | ok |
| yolo26-x-obb_1024x1024.dxnn | 16.6 ±0.0 | 30 | 85.4 | 100.0 | 60~64 | 1000 | ok |

#### Classification

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n_224x224.dxnn | 3414.0 ±4.4 | 100 | 83.1 | 92.6 | 52~53 | 1000 | ok |
| yolo26-s_224x224.dxnn | 1990.2 ±3.0 | 70 | 89.6 | 96.9 | 54~55 | 1000 | ok |
| yolo26-m_224x224.dxnn | 1377.4 ±1.9 | 64 | 87.6 | 97.3 | 57~60 | 1000 | ok |
| yolo26-l_224x224.dxnn | 874.5 ±1.1 | 53 | 90.1 | 98.3 | 55~58 | 1000 | ok |
| yolo26-x_224x224.dxnn | 484.3 ±1.4 | 38 | 90.3 | 99.3 | 57~60 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n_224x224.dxnn | 3417.1 ±17.5 | 100 | 83.6 | 94.2 | 53 | 1000 | partial — avg of 2/3 runs (backfill exhausted after 5 attempts: 0 timeout, 3 unparsable) |
| yolo26-s_224x224.dxnn | 1989.1 ±6.9 | 70 | 87.8 | 97.2 | 54~55 | 1000 | ok |
| yolo26-m_224x224.dxnn | 1378.0 ±0.7 | 65 | 86.0 | 97.6 | 55~58 | 1000 | ok |
| yolo26-l_224x224.dxnn | 875.3 ±1.0 | 53 | 90.1 | 98.4 | 55~58 | 1000 | ok |
| yolo26-x_224x224.dxnn | 484.0 ±0.7 | 35 | 89.1 | 99.3 | 57~60 | 1000 | ok |

### Latency (Single-Core, Sync)

#### Object Detection

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_640x640.dxnn | 32.0 | 31.20 | 26.19 | 5.01 | 40 | ok |
| yolo26-s_640x640.dxnn | 19.9 | 50.14 | 42.02 | 8.12 | 50 | ok |
| yolo26-m_640x640.dxnn | 17.6 | 56.83 | 48.36 | 8.47 | 51 | ok |
| yolo26-l_640x640.dxnn | 13.8 | 72.31 | 66.77 | 5.54 | 51 | ok |
| yolo26-x_640x640.dxnn | 10.3 | 96.92 | 90.33 | 6.59 | 51 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_640x640.dxnn | 29.5 | 33.89 | 33.89 | N/A | 50 | ok |
| yolo26-s_640x640.dxnn | 18.9 | 52.97 | 52.97 | N/A | 50 | ok |
| yolo26-m_640x640.dxnn | 18.7 | 53.34 | 53.34 | N/A | 51 | ok |
| yolo26-l_640x640.dxnn | 15.1 | 66.17 | 66.17 | N/A | 51 | ok |
| yolo26-x_640x640.dxnn | 11.3 | 88.69 | 88.69 | N/A | 52 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-pose_640x640.dxnn | 34.8 | 28.70 | 25.54 | 3.16 | 50 | ok |
| yolo26-s-pose_640x640.dxnn | 24.1 | 41.57 | 38.18 | 3.39 | 50 | ok |
| yolo26-m-pose_640x640.dxnn | 21.0 | 47.58 | 43.16 | 4.42 | 51 | ok |
| yolo26-l-pose_640x640.dxnn | 18.1 | 55.34 | 50.65 | 4.68 | 51 | ok |
| yolo26-x-pose_640x640.dxnn | 11.0 | 91.31 | 87.07 | 4.24 | 51 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-pose_640x640.dxnn | 37.0 | 27.01 | 27.01 | N/A | 50 | ok |
| yolo26-s-pose_640x640.dxnn | 25.6 | 39.01 | 39.01 | N/A | 50 | ok |
| yolo26-m-pose_640x640.dxnn | 23.4 | 42.76 | 42.76 | N/A | 51 | ok |
| yolo26-l-pose_640x640.dxnn | 18.6 | 53.75 | 53.75 | N/A | 51 | ok |
| yolo26-x-pose_640x640.dxnn | 12.4 | 80.66 | 80.66 | N/A | 52 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-seg_640x640.dxnn | 21.1 | 47.28 | 42.73 | 4.56 | 50 | ok |
| yolo26-s-seg_640x640.dxnn | 16.8 | 59.58 | 53.82 | 5.76 | 50 | ok |
| yolo26-m-seg_640x640.dxnn | 12.2 | 81.70 | 73.83 | 7.88 | 50 | ok |
| yolo26-l-seg_640x640.dxnn | 11.0 | 91.14 | 80.30 | 10.83 | 50 | ok |
| yolo26-x-seg_640x640.dxnn | 7.9 | 126.33 | 117.79 | 8.54 | 51 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-seg_640x640.dxnn | 20.4 | 48.93 | 48.93 | N/A | 50 | ok |
| yolo26-s-seg_640x640.dxnn | 17.1 | 58.50 | 58.50 | N/A | 50 | ok |
| yolo26-m-seg_640x640.dxnn | 13.4 | 74.71 | 74.71 | N/A | 51 | ok |
| yolo26-l-seg_640x640.dxnn | 12.0 | 83.16 | 83.16 | N/A | 51 | ok |
| yolo26-x-seg_640x640.dxnn | 8.5 | 118.04 | 118.04 | N/A | 52 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-obb_1024x1024.dxnn | 20.5 | 48.81 | 44.21 | 4.60 | 50 | ok |
| yolo26-s-obb_1024x1024.dxnn | 13.0 | 76.96 | 72.44 | 4.53 | 50 | ok |
| yolo26-m-obb_1024x1024.dxnn | 11.4 | 87.77 | 83.06 | 4.71 | 51 | ok |
| yolo26-l-obb_1024x1024.dxnn | 9.5 | 104.92 | 97.90 | 7.03 | 51 | ok |
| yolo26-x-obb_1024x1024.dxnn | 5.7 | 175.51 | 169.87 | 5.64 | 53 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-obb_1024x1024.dxnn | 22.9 | 43.73 | 43.73 | N/A | 50 | ok |
| yolo26-s-obb_1024x1024.dxnn | 14.6 | 68.50 | 68.50 | N/A | 50 | ok |
| yolo26-m-obb_1024x1024.dxnn | 12.1 | 82.62 | 82.62 | N/A | 52 | ok |
| yolo26-l-obb_1024x1024.dxnn | 9.9 | 101.48 | 101.48 | N/A | 52 | ok |
| yolo26-x-obb_1024x1024.dxnn | 5.9 | 169.98 | 169.98 | N/A | 53 | ok |

#### Classification

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_224x224.dxnn | 266.8 | 3.75 | 3.75 | N/A | 50 | ok |
| yolo26-s_224x224.dxnn | 303.8 | 3.29 | 3.29 | N/A | 50 | ok |
| yolo26-m_224x224.dxnn | 221.7 | 4.51 | 4.51 | N/A | 50 | ok |
| yolo26-l_224x224.dxnn | 160.0 | 6.25 | 6.25 | N/A | 50 | ok |
| yolo26-x_224x224.dxnn | 116.1 | 8.61 | 8.61 | N/A | 50 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_224x224.dxnn | 254.4 | 3.93 | 3.93 | N/A | 50 | ok |
| yolo26-s_224x224.dxnn | 213.0 | 4.70 | 4.70 | N/A | 50 | ok |
| yolo26-m_224x224.dxnn | 186.0 | 5.38 | 5.38 | N/A | 50 | ok |
| yolo26-l_224x224.dxnn | 147.4 | 6.78 | 6.78 | N/A | 50 | ok |
| yolo26-x_224x224.dxnn | 106.6 | 9.38 | 9.38 | N/A | 50 | ok |

## E2E Pipeline (Single-Stream)

### Object Detection

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | mppvideodec | 3455 | 3 | 147.3 ±1.2 | 23.45 | 250 | 38.0 | 66.3 | 49~51 | 1000 | 187 | ok |
| yolo26-s_640x640.dxnn | mppvideodec | 3455 | 3 | 126.7 ±1.3 | 27.27 | 217 | 58.2 | 81.4 | 60~61 | 1000 | 209 | ok |
| yolo26-m_640x640.dxnn | mppvideodec | 3455 | 3 | 98.1 ±2.8 | 35.22 | 187 | 74.2 | 95.7 | 68~71 | 1000 | 240 | ok |
| yolo26-l_640x640.dxnn | mppvideodec | 3455 | 3 | 80.0 ±0.2 | 43.18 | 174 | 83.3 | 98.7 | 68~72 | 1000 | 254 | ok |
| yolo26-x_640x640.dxnn | mppvideodec | 3455 | 3 | 46.5 ±2.0 | 74.33 | 133 | 91.6 | 100.0 | 74~79 | 800~1000 | 354 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | mppvideodec | 3455 | 3 | 98.3 ±0.2 | 35.15 | 217 | 22.0 | 72.1 | 57 | 1000 | 198 | ok |
| yolo26-s_640x640.dxnn | mppvideodec | 3455 | 3 | 99.1 ±1.0 | 34.86 | 221 | 41.1 | 69.3 | 59~60 | 1000 | 220 | ok |
| yolo26-m_640x640.dxnn | mppvideodec | 3455 | 3 | 98.1 ±0.3 | 35.23 | 221 | 73.3 | 82.3 | 67~70 | 1000 | 252 | ok |
| yolo26-l_640x640.dxnn | mppvideodec | 3455 | 3 | 88.1 ±0.4 | 39.21 | 212 | 91.2 | 100.0 | 68~72 | 1000 | 265 | ok |
| yolo26-x_640x640.dxnn | mppvideodec | 3455 | 3 | 47.6 ±1.1 | 72.54 | 157 | 93.2 | 100.0 | 74~79 | 800~1000 | 354 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n_640x640.dxnn | 147.3 | 98.3 | +49.0 | +49.9% |
| yolo26-s_640x640.dxnn | 126.7 | 99.1 | +27.6 | +27.8% |
| yolo26-m_640x640.dxnn | 98.1 | 98.1 | +0.0 | +0.0% |
| yolo26-l_640x640.dxnn | 80.0 | 88.1 | -8.1 | -9.2% |
| yolo26-x_640x640.dxnn | 46.5 | 47.6 | -1.2 | -2.4% |

### Pose Estimation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 198.5 ±2.5 | 17.41 | 242 | 50.9 | 74.5 | 57~58 | 1000 | 179 | ok |
| yolo26-s-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 148.3 ±1.2 | 23.29 | 202 | 72.5 | 93.2 | 61~62 | 1000 | 201 | ok |
| yolo26-m-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 107.3 ±0.1 | 32.19 | 169 | 85.2 | 100.0 | 69~72 | 1000 | 233 | ok |
| yolo26-l-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 84.0 ±0.1 | 41.13 | 146 | 89.4 | 100.0 | 69~72 | 1000 | 248 | ok |
| yolo26-x-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 46.5 ±0.9 | 74.32 | 108 | 92.3 | 100.0 | 74~79 | 800~1000 | 369 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 249.1 ±4.6 | 13.87 | 211 | 65.2 | 91.8 | 58~59 | 1000 | 166 | ok |
| yolo26-s-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 168.8 ±1.1 | 20.47 | 178 | 80.4 | 96.0 | 61~62 | 1000 | 190 | ok |
| yolo26-m-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 110.6 ±0.1 | 31.23 | 150 | 88.4 | 100.0 | 69~72 | 1000 | 220 | ok |
| yolo26-l-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 84.0 ±0.2 | 41.15 | 124 | 91.0 | 100.0 | 69~72 | 1000 | 237 | ok |
| yolo26-x-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 47.1 ±0.0 | 73.31 | 89 | 93.3 | 100.0 | 72~78 | 1000 | 352 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-pose_640x640.dxnn | 198.5 | 249.1 | -50.6 | -20.3% |
| yolo26-s-pose_640x640.dxnn | 148.3 | 168.8 | -20.5 | -12.1% |
| yolo26-m-pose_640x640.dxnn | 107.3 | 110.6 | -3.3 | -3.0% |
| yolo26-l-pose_640x640.dxnn | 84.0 | 84.0 | +0.1 | +0.1% |
| yolo26-x-pose_640x640.dxnn | 46.5 | 47.1 | -0.6 | -1.4% |

### Segmentation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 99.3 ±0.5 | 34.80 | 324 | 33.1 | 58.2 | 55~57 | 1000 | 286 | ok |
| yolo26-s-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 87.3 ±1.6 | 39.58 | 278 | 54.1 | 78.2 | 60~62 | 1000 | 310 | ok |
| yolo26-m-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 64.9 ±2.0 | 53.24 | 224 | 74.2 | 96.4 | 71~75 | 1000 | 347 | ok |
| yolo26-l-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 57.4 ±0.4 | 60.24 | 214 | 82.6 | 100.0 | 72~76 | 1000 | 361 | ok |
| yolo26-x-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 28.7 ±1.6 | 120.50 | 137 | 89.8 | 100.0 | 78~81 | 600~1000 | 466 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 84.5 ±0.2 | 40.91 | 262 | 24.0 | 80.0 | 56 | 1000 | 306 | ok |
| yolo26-s-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 82.8 ±0.2 | 41.72 | 264 | 45.2 | 77.7 | 61~62 | 1000 | 329 | ok |
| yolo26-m-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 74.5 ±1.6 | 46.39 | 246 | 85.1 | 100.0 | 73~77 | 800~1000 | 366 | ok |
| yolo26-l-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 62.3 ±1.2 | 55.45 | 227 | 90.1 | 100.0 | 72~77 | 800~1000 | 374 | ok |
| yolo26-x-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 28.8 ±1.9 | 119.82 | 137 | 91.4 | 100.0 | 78~80 | 600~1000 | 478 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-seg_640x640.dxnn | 99.3 | 84.5 | +14.8 | +17.6% |
| yolo26-s-seg_640x640.dxnn | 87.3 | 82.8 | +4.5 | +5.4% |
| yolo26-m-seg_640x640.dxnn | 64.9 | 74.5 | -9.6 | -12.9% |
| yolo26-l-seg_640x640.dxnn | 57.4 | 62.3 | -4.9 | -7.9% |
| yolo26-x-seg_640x640.dxnn | 28.7 | 28.8 | -0.2 | -0.6% |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 91.5 ±1.2 | 28.84 | 180 | 79.1 | 96.3 | 57~58 | 1000 | 215 | ok |
| yolo26-s-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 61.6 ±0.6 | 42.82 | 146 | 90.4 | 100.0 | 61~64 | 1000 | 239 | ok |
| yolo26-m-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 41.2 ±0.5 | 64.09 | 111 | 92.5 | 100.0 | 70~74 | 1000 | 272 | ok |
| yolo26-l-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 30.5 ±0.2 | 86.62 | 96 | 93.7 | 100.0 | 71~76 | 1000 | 288 | ok |
| yolo26-x-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 15.9 ±0.8 | 165.76 | 65 | 91.5 | 100.0 | 77~80 | 800~1000 | 390 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 100.2 ±0.4 | 26.36 | 197 | 86.0 | 100.0 | 58~59 | 1000 | 221 | ok |
| yolo26-s-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 62.3 ±0.7 | 42.36 | 153 | 90.2 | 100.0 | 61~63 | 1000 | 240 | ok |
| yolo26-m-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 41.9 ±0.4 | 63.04 | 119 | 92.9 | 100.0 | 70~74 | 1000 | 274 | ok |
| yolo26-l-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 30.5 ±0.1 | 86.66 | 105 | 93.9 | 100.0 | 71~75 | 1000 | 286 | ok |
| yolo26-x-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 16.1 ±1.0 | 164.19 | 65 | 93.7 | 100.0 | 78~80 | 800~1000 | 390 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-obb_1024x1024.dxnn | 91.5 | 100.2 | -8.6 | -8.6% |
| yolo26-s-obb_1024x1024.dxnn | 61.6 | 62.3 | -0.7 | -1.1% |
| yolo26-m-obb_1024x1024.dxnn | 41.2 | 41.9 | -0.7 | -1.6% |
| yolo26-l-obb_1024x1024.dxnn | 30.5 | 30.5 | +0.0 | +0.0% |
| yolo26-x-obb_1024x1024.dxnn | 15.9 | 16.1 | -0.1 | -0.9% |

### Classification

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_224x224.dxnn | mppvideodec | 3455 | 3 | 1074.5 ±7.3 | 3.21 | 176 | 14.2 | 51.7 | 52 | 1000 | 91 | ok |
| yolo26-s_224x224.dxnn | mppvideodec | 3455 | 3 | 1055.8 ±9.9 | 3.27 | 176 | 23.2 | 69.3 | 54 | 1000 | 100 | ok |
| yolo26-m_224x224.dxnn | mppvideodec | 3455 | 3 | 1054.9 ±5.7 | 3.27 | 177 | 38.1 | 83.2 | 58~59 | 1000 | 115 | ok |
| yolo26-l_224x224.dxnn | mppvideodec | 3455 | 3 | 864.2 ±4.4 | 4.00 | 158 | 56.1 | 98.0 | 57 | 1000 | 128 | ok |
| yolo26-x_224x224.dxnn | mppvideodec | 3455 | 3 | 482.0 ±0.5 | 7.17 | 121 | 66.8 | 99.1 | 60 | 1000 | 204 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_224x224.dxnn | mppvideodec | 3455 | 3 | 1067.5 ±8.4 | 3.24 | 175 | 11.7 | 51.0 | 52 | 1000 | 91 | ok |
| yolo26-s_224x224.dxnn | mppvideodec | 3455 | 3 | 1060.5 ±3.6 | 3.26 | 177 | 27.0 | 67.7 | 54 | 1000 | 100 | ok |
| yolo26-m_224x224.dxnn | mppvideodec | 3455 | 3 | 1053.3 ±17.8 | 3.28 | 175 | 35.8 | 83.8 | 57 | 1000 | 115 | ok |
| yolo26-l_224x224.dxnn | mppvideodec | 3455 | 3 | 865.4 ±2.9 | 3.99 | 157 | 56.1 | 97.9 | 57 | 1000 | 128 | ok |
| yolo26-x_224x224.dxnn | mppvideodec | 3455 | 3 | 481.5 ±1.5 | 7.17 | 121 | 67.4 | 98.9 | 60 | 1000 | 204 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n_224x224.dxnn | 1074.5 | 1067.5 | +7.0 | +0.7% |
| yolo26-s_224x224.dxnn | 1055.8 | 1060.5 | -4.8 | -0.4% |
| yolo26-m_224x224.dxnn | 1054.9 | 1053.3 | +1.6 | +0.1% |
| yolo26-l_224x224.dxnn | 864.2 | 865.4 | -1.1 | -0.1% |
| yolo26-x_224x224.dxnn | 482.0 | 481.5 | +0.5 | +0.1% |

## E2E Pipeline (Multi-Stream)

### Object Detection

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | 4 | 3 | 147.8 ±0.7 | 36.9 | 259 | 41.3 | 63.8 | 56~60 | 1000 | 210 | ok |
| yolo26-n_640x640.dxnn | 5 | 3 | 149.2 ±3.5 | 29.8 | 255 | 42.0 | 66.0 | 62~64 | 1000 | 215 | ok |
| yolo26-s_640x640.dxnn | 4 | 3 | 125.5 ±0.9 | 31.4 | 225 | 62.0 | 80.9 | 66~68 | 1000 | 232 | ok |
| yolo26-s_640x640.dxnn | 5 | 3 | 125.8 ±0.3 | 25.2 | 226 | 63.4 | 80.3 | 70~71 | 1000 | 236 | ok |
| yolo26-m_640x640.dxnn | 3 | 3 | 96.2 ±2.3 | 32.1 | 191 | 78.7 | 95.3 | 77~80 | 800~1000 | 257 | ok |
| yolo26-m_640x640.dxnn | 4 | 3 | 91.1 ±0.8 | 22.8 | 187 | 81.8 | 97.2 | 82 | 600~1000 | 263 | ok |
| yolo26-l_640x640.dxnn | 2 | 3 | 79.4 ±1.0 | 39.7 | 174 | 86.1 | 99.3 | 77~80 | 800~1000 | 265 | ok |
| yolo26-l_640x640.dxnn | 3 | 3 | 73.8 ±1.3 | 24.6 | 169 | 87.8 | 100.0 | 81~82 | 600~1000 | 273 | ok |
| yolo26-x_640x640.dxnn | 1 | 3 | 46.5 ±2.0 | 46.5 | 133 | 91.6 | 100.0 | 74~79 | 800~1000 | 354 | ok |
| yolo26-x_640x640.dxnn | 2 | 3 | 39.9 ±0.6 | 19.9 | 122 | 93.5 | 100.0 | 81~82 | 600~1000 | 359 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | 3 | 3 | 98.0 ±0.6 | 32.7 | 221 | 23.0 | 72.0 | 57~58 | 1000 | 223 | ok |
| yolo26-n_640x640.dxnn | 4 | 3 | 98.2 ±0.1 | 24.6 | 222 | 23.2 | 72.0 | 58~59 | 1000 | 232 | ok |
| yolo26-s_640x640.dxnn | 3 | 3 | 99.5 ±0.7 | 33.2 | 227 | 43.4 | 68.8 | 62~63 | 1000 | 245 | ok |
| yolo26-s_640x640.dxnn | 4 | 3 | 99.3 ±0.6 | 24.8 | 227 | 43.3 | 68.7 | 64~65 | 1000 | 253 | ok |
| yolo26-m_640x640.dxnn | 3 | 3 | 98.0 ±0.4 | 32.7 | 229 | 76.3 | 84.5 | 76~81 | 1000 | 276 | ok |
| yolo26-m_640x640.dxnn | 4 | 3 | 92.9 ±1.8 | 23.2 | 222 | 90.9 | 100.0 | 82 | 600~1000 | 285 | ok |
| yolo26-l_640x640.dxnn | 2 | 3 | 84.7 ±4.2 | 42.4 | 213 | 92.4 | 100.0 | 78~81 | 800~1000 | 277 | ok |
| yolo26-l_640x640.dxnn | 3 | 3 | 75.6 ±0.4 | 25.2 | 207 | 94.4 | 100.0 | 82 | 600~1000 | 286 | ok |
| yolo26-x_640x640.dxnn | 1 | 3 | 47.6 ±1.1 | 47.6 | 157 | 93.2 | 100.0 | 74~79 | 800~1000 | 354 | ok |
| yolo26-x_640x640.dxnn | 2 | 3 | 39.0 ±0.8 | 19.5 | 141 | 93.4 | 100.0 | 80~81 | 600~1000 | 371 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n_640x640.dxnn | 4 | 36.9 | 3 | 32.7 |
| yolo26-s_640x640.dxnn | 4 | 31.4 | 3 | 33.2 |
| yolo26-m_640x640.dxnn | 3 | 32.1 | 3 | 32.7 |
| yolo26-l_640x640.dxnn | 2 | 39.7 | 2 | 42.4 |
| yolo26-x_640x640.dxnn | 1 | 46.5 | 1 | 47.6 |

### Pose Estimation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 6 | 3 | 200.5 ±1.0 | 33.4 | 255 | 61.8 | 78.7 | 62~65 | 1000 | 218 | ok |
| yolo26-n-pose_640x640.dxnn | 7 | 3 | 201.0 ±0.4 | 28.7 | 255 | 61.7 | 77.2 | 67~68 | 1000 | 223 | ok |
| yolo26-s-pose_640x640.dxnn | 4 | 3 | 150.8 ±0.8 | 37.7 | 210 | 79.8 | 93.1 | 67~70 | 1000 | 229 | ok |
| yolo26-s-pose_640x640.dxnn | 5 | 3 | 150.3 ±0.6 | 30.1 | 209 | 80.1 | 94.1 | 72~74 | 1000 | 235 | ok |
| yolo26-s-pose_640x640.dxnn | 6 | 3 | 150.7 ±0.7 | 25.1 | 208 | 80.7 | 94.2 | 75 | 1000 | 242 | ok |
| yolo26-m-pose_640x640.dxnn | 3 | 3 | 100.9 ±5.2 | 33.6 | 169 | 89.8 | 100.0 | 79~81 | 800~1000 | 255 | ok |
| yolo26-m-pose_640x640.dxnn | 4 | 3 | 92.7 ±0.7 | 23.2 | 158 | 92.6 | 100.0 | 82 | 600~1000 | 262 | ok |
| yolo26-l-pose_640x640.dxnn | 2 | 3 | 79.3 ±4.0 | 39.6 | 149 | 91.8 | 100.0 | 78~80 | 800~1000 | 260 | ok |
| yolo26-l-pose_640x640.dxnn | 3 | 3 | 72.7 ±0.5 | 24.2 | 145 | 90.8 | 100.0 | 81~82 | 600~1000 | 270 | ok |
| yolo26-x-pose_640x640.dxnn | 1 | 3 | 46.5 ±0.9 | 46.5 | 108 | 92.3 | 100.0 | 74~79 | 800~1000 | 369 | ok |
| yolo26-x-pose_640x640.dxnn | 2 | 3 | 39.3 ±0.8 | 19.6 | 101 | 95.3 | 100.0 | 82 | 600~1000 | 369 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 8 | 3 | 249.1 ±6.5 | 31.1 | 226 | 78.6 | 92.7 | 65~68 | 1000 | 223 | ok |
| yolo26-n-pose_640x640.dxnn | 9 | 3 | 248.9 ±6.4 | 27.7 | 227 | 79.1 | 92.1 | 70~71 | 1000 | 229 | ok |
| yolo26-s-pose_640x640.dxnn | 5 | 3 | 169.1 ±0.2 | 33.8 | 183 | 88.3 | 98.2 | 68~72 | 1000 | 230 | ok |
| yolo26-s-pose_640x640.dxnn | 6 | 3 | 170.7 ±1.1 | 28.4 | 179 | 90.7 | 98.4 | 74~75 | 1000 | 236 | ok |
| yolo26-m-pose_640x640.dxnn | 3 | 3 | 103.2 ±4.8 | 34.4 | 147 | 92.2 | 100.0 | 79~81 | 800~1000 | 243 | ok |
| yolo26-m-pose_640x640.dxnn | 4 | 3 | 95.1 ±0.5 | 23.8 | 139 | 94.5 | 100.0 | 82~83 | 800~1000 | 254 | ok |
| yolo26-l-pose_640x640.dxnn | 2 | 3 | 81.5 ±2.4 | 40.8 | 128 | 93.5 | 100.0 | 77~81 | 800~1000 | 250 | ok |
| yolo26-l-pose_640x640.dxnn | 3 | 3 | 73.5 ±0.6 | 24.5 | 120 | 92.0 | 100.0 | 81 | 600~1000 | 258 | ok |
| yolo26-x-pose_640x640.dxnn | 1 | 3 | 47.1 ±0.0 | 47.1 | 89 | 93.3 | 100.0 | 72~78 | 1000 | 352 | ok |
| yolo26-x-pose_640x640.dxnn | 2 | 3 | 40.8 ±0.2 | 20.4 | 89 | 92.4 | 100.0 | 80~81 | 800~1000 | 352 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-pose_640x640.dxnn | 6 | 33.4 | 8 | 31.1 |
| yolo26-s-pose_640x640.dxnn | 5 | 30.1 | 5 | 33.8 |
| yolo26-m-pose_640x640.dxnn | 3 | 33.6 | 3 | 34.4 |
| yolo26-l-pose_640x640.dxnn | 2 | 39.6 | 2 | 40.8 |
| yolo26-x-pose_640x640.dxnn | 1 | 46.5 | 1 | 47.1 |

### Segmentation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 3 | 3 | 99.5 ±0.2 | 33.2 | 330 | 34.9 | 61.6 | 60~62 | 1000 | 321 | ok |
| yolo26-n-seg_640x640.dxnn | 4 | 3 | 99.1 ±0.7 | 24.8 | 330 | 35.1 | 59.7 | 63~64 | 1000 | 327 | ok |
| yolo26-s-seg_640x640.dxnn | 2 | 3 | 86.3 ±0.2 | 43.2 | 287 | 54.3 | 74.3 | 66~68 | 1000 | 330 | ok |
| yolo26-s-seg_640x640.dxnn | 3 | 3 | 86.5 ±0.2 | 28.8 | 288 | 55.4 | 74.1 | 70~71 | 1000 | 342 | ok |
| yolo26-m-seg_640x640.dxnn | 2 | 3 | 59.1 ±1.5 | 29.6 | 211 | 82.5 | 100.0 | 80~82 | 600~1000 | 365 | ok |
| yolo26-m-seg_640x640.dxnn | 1 | 3 | 64.9 ±2.0 | 64.9 | 224 | 74.2 | 96.4 | 71~75 | 1000 | 347 | ok |
| yolo26-l-seg_640x640.dxnn | 1 | 3 | 57.4 ±0.4 | 57.4 | 214 | 82.6 | 100.0 | 72~76 | 1000 | 361 | ok |
| yolo26-l-seg_640x640.dxnn | 2 | 3 | 51.2 ±1.1 | 25.6 | 197 | 88.0 | 100.0 | 81~82 | 600~1000 | 380 | ok |
| yolo26-x-seg_640x640.dxnn | 1 | 3 | 28.7 ±1.6 | 28.7 | 137 | 89.8 | 100.0 | 78~81 | 600~1000 | 466 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 2 | 3 | 84.7 ±0.1 | 42.3 | 275 | 24.6 | 80.9 | 58~59 | 1000 | 334 | ok |
| yolo26-n-seg_640x640.dxnn | 3 | 3 | 84.7 ±0.0 | 28.2 | 275 | 25.1 | 80.9 | 60~61 | 1000 | 342 | ok |
| yolo26-s-seg_640x640.dxnn | 2 | 3 | 82.7 ±0.2 | 41.3 | 275 | 47.6 | 79.0 | 65~67 | 1000 | 358 | ok |
| yolo26-s-seg_640x640.dxnn | 3 | 3 | 82.6 ±0.1 | 27.5 | 275 | 48.2 | 78.9 | 68~69 | 1000 | 368 | ok |
| yolo26-m-seg_640x640.dxnn | 2 | 3 | 59.4 ±1.7 | 29.7 | 223 | 91.6 | 100.0 | 81~82 | 600~1000 | 386 | ok |
| yolo26-m-seg_640x640.dxnn | 1 | 3 | 74.5 ±1.6 | 74.5 | 246 | 85.1 | 100.0 | 73~77 | 800~1000 | 366 | ok |
| yolo26-l-seg_640x640.dxnn | 2 | 3 | 50.0 ±1.8 | 25.0 | 198 | 92.2 | 100.0 | 81 | 600~1000 | 400 | ok |
| yolo26-l-seg_640x640.dxnn | 1 | 3 | 62.3 ±1.2 | 62.3 | 227 | 90.1 | 100.0 | 72~77 | 800~1000 | 374 | ok |
| yolo26-x-seg_640x640.dxnn | 1 | 3 | 28.8 ±1.9 | 28.8 | 137 | 91.4 | 100.0 | 78~80 | 600~1000 | 478 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-seg_640x640.dxnn | 3 | 33.2 | 2 | 42.3 |
| yolo26-s-seg_640x640.dxnn | 2 | 43.2 | 2 | 41.3 |
| yolo26-m-seg_640x640.dxnn | 1 | 64.9 | 1 | 74.5 |
| yolo26-l-seg_640x640.dxnn | 1 | 57.4 | 1 | 62.3 |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 3 | 3 | 92.0 ±0.9 | 30.7 | 185 | 84.1 | 99.4 | 62~64 | 1000 | 245 | ok |
| yolo26-n-obb_1024x1024.dxnn | 4 | 3 | 92.0 ±0.4 | 23.0 | 185 | 84.6 | 97.7 | 66~67 | 1000 | 254 | ok |
| yolo26-s-obb_1024x1024.dxnn | 2 | 3 | 61.5 ±0.3 | 30.8 | 148 | 92.6 | 100.0 | 67~69 | 1000 | 254 | ok |
| yolo26-s-obb_1024x1024.dxnn | 3 | 3 | 61.6 ±0.1 | 20.5 | 149 | 94.4 | 100.0 | 71~72 | 1000 | 266 | ok |
| yolo26-m-obb_1024x1024.dxnn | 1 | 3 | 41.2 ±0.5 | 41.2 | 111 | 92.5 | 100.0 | 70~74 | 1000 | 272 | ok |
| yolo26-m-obb_1024x1024.dxnn | 2 | 3 | 38.0 ±1.1 | 19.0 | 111 | 94.2 | 100.0 | 79~80 | 800~1000 | 287 | ok |
| yolo26-l-obb_1024x1024.dxnn | 1 | 3 | 30.5 ±0.2 | 30.5 | 96 | 93.7 | 100.0 | 71~76 | 1000 | 288 | ok |
| yolo26-l-obb_1024x1024.dxnn | 2 | 3 | 28.4 ±0.7 | 14.2 | 97 | 95.2 | 100.0 | 79~80 | 800~1000 | 301 | ok |
| yolo26-x-obb_1024x1024.dxnn | 1 | 3 | 15.9 ±0.8 | 15.9 | 65 | 91.5 | 100.0 | 77~80 | 800~1000 | 390 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 3 | 3 | 100.0 ±0.1 | 33.3 | 204 | 93.1 | 100.0 | 63~65 | 1000 | 247 | ok |
| yolo26-n-obb_1024x1024.dxnn | 4 | 3 | 100.1 ±0.2 | 25.0 | 204 | 93.2 | 100.0 | 67~68 | 1000 | 255 | ok |
| yolo26-s-obb_1024x1024.dxnn | 2 | 3 | 62.3 ±0.2 | 31.1 | 160 | 94.5 | 100.0 | 67~70 | 1000 | 255 | ok |
| yolo26-s-obb_1024x1024.dxnn | 3 | 3 | 62.2 ±0.2 | 20.7 | 160 | 95.6 | 100.0 | 72 | 1000 | 266 | ok |
| yolo26-m-obb_1024x1024.dxnn | 1 | 3 | 41.9 ±0.4 | 41.9 | 119 | 92.9 | 100.0 | 70~74 | 1000 | 274 | ok |
| yolo26-m-obb_1024x1024.dxnn | 2 | 3 | 37.9 ±0.9 | 18.9 | 122 | 94.0 | 100.0 | 79~80 | 800~1000 | 286 | ok |
| yolo26-l-obb_1024x1024.dxnn | 1 | 3 | 30.5 ±0.1 | 30.5 | 105 | 93.9 | 100.0 | 71~75 | 1000 | 286 | ok |
| yolo26-l-obb_1024x1024.dxnn | 2 | 3 | 28.9 ±0.9 | 14.4 | 103 | 95.5 | 100.0 | 79~80 | 800~1000 | 299 | ok |
| yolo26-x-obb_1024x1024.dxnn | 1 | 3 | 16.1 ±1.0 | 16.1 | 65 | 93.7 | 100.0 | 78~80 | 800~1000 | 390 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-obb_1024x1024.dxnn | 3 | 30.7 | 3 | 33.3 |
| yolo26-s-obb_1024x1024.dxnn | 2 | 30.8 | 2 | 31.1 |
| yolo26-m-obb_1024x1024.dxnn | 1 | 41.2 | 1 | 41.9 |
| yolo26-l-obb_1024x1024.dxnn | 1 | 30.5 | 1 | 30.5 |

---
*Report generated by dx-benchmark tool*
