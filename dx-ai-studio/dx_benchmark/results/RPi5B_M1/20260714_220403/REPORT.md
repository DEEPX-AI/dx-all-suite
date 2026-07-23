# YOLO26 Benchmark Report

**Generated:** 2026-07-15 16:31:50 (Local)

## Test Timing

| # | Type | Start | End | Duration |
|---|------|-------|-----|----------|
| 1 | run | 2026-07-14 22:04:03 | 2026-07-15 16:31:50 | 18h 27m 47s |

## Executive Summary

### Object Detection

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n_640x640.dxnn | ON | 23.61 | 100.4 | 64.6 | 2 |
| yolo26-n_640x640.dxnn | OFF | 22.78 | 179.2 | 77.2 | 2 |
| yolo26-s_640x640.dxnn | ON | 29.70 | 100.2 | 64.5 | 2 |
| yolo26-s_640x640.dxnn | OFF | 27.21 | 171.6 | 77.6 | 2 |
| yolo26-m_640x640.dxnn | ON | 36.79 | 99.9 | 63.8 | 2 |
| yolo26-m_640x640.dxnn | OFF | 34.38 | 118.4 | 77.1 | 2 |
| yolo26-l_640x640.dxnn | ON | 43.37 | 90.0 | 64.1 | 2 |
| yolo26-l_640x640.dxnn | OFF | 40.93 | 86.6 | 76.9 | 2 |
| yolo26-x_640x640.dxnn | ON | 69.46 | 48.8 | 48.5 | 1 |
| yolo26-x_640x640.dxnn | OFF | 67.01 | 48.4 | 48.9 | 1 |

### Pose Estimation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-pose_640x640.dxnn | ON | 19.79 | 142.5 | 78.4 | 2 |
| yolo26-n-pose_640x640.dxnn | OFF | 18.06 | 247.6 | 107.5 | 3 |
| yolo26-s-pose_640x640.dxnn | ON | 26.90 | 142.3 | 78.1 | 2 |
| yolo26-s-pose_640x640.dxnn | OFF | 24.23 | 176.3 | 108.0 | 3 |
| yolo26-m-pose_640x640.dxnn | ON | 33.27 | 113.2 | 78.4 | 2 |
| yolo26-m-pose_640x640.dxnn | OFF | 31.02 | 111.6 | 105.7 | 3 |
| yolo26-l-pose_640x640.dxnn | ON | 40.47 | 84.6 | 78.2 | 2 |
| yolo26-l-pose_640x640.dxnn | OFF | 38.78 | 83.8 | 83.9 | 2 |
| yolo26-x-pose_640x640.dxnn | ON | 66.27 | 46.8 | 47.5 | 1 |
| yolo26-x-pose_640x640.dxnn | OFF | 64.80 | 46.2 | 47.6 | 1 |

### Segmentation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-seg_640x640.dxnn | ON | 41.17 | 64.3 | 42.9 | 1 |
| yolo26-n-seg_640x640.dxnn | OFF | 35.84 | 95.7 | 52.2 | 1 |
| yolo26-s-seg_640x640.dxnn | ON | 45.73 | 64.3 | 42.7 | 1 |
| yolo26-s-seg_640x640.dxnn | OFF | 43.72 | 95.7 | 53.0 | 1 |
| yolo26-m-seg_640x640.dxnn | ON | 61.17 | 64.0 | 42.4 | 1 |
| yolo26-m-seg_640x640.dxnn | OFF | 56.67 | 78.3 | 51.9 | 1 |
| yolo26-l-seg_640x640.dxnn | ON | 70.57 | 62.1 | 42.5 | 1 |
| yolo26-l-seg_640x640.dxnn | OFF | 67.13 | 64.4 | 51.6 | 1 |
| yolo26-x-seg_640x640.dxnn | ON | 105.59 | 34.4 | 32.3 | 1 |
| yolo26-x-seg_640x640.dxnn | OFF | 102.30 | 34.8 | 33.3 | 1 |

### Oriented BBox (OBB)

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-obb_1024x1024.dxnn | ON | 35.75 | 103.9 | 66.6 | 2 |
| yolo26-n-obb_1024x1024.dxnn | OFF | 34.15 | 98.1 | 78.5 | 2 |
| yolo26-s-obb_1024x1024.dxnn | ON | 50.88 | 60.6 | 62.2 | 2 |
| yolo26-s-obb_1024x1024.dxnn | OFF | 49.87 | 61.2 | 61.3 | 2 |
| yolo26-m-obb_1024x1024.dxnn | ON | 68.45 | 39.8 | 41.6 | 1 |
| yolo26-m-obb_1024x1024.dxnn | OFF | 66.48 | 40.1 | 41.9 | 1 |
| yolo26-l-obb_1024x1024.dxnn | ON | 86.49 | 29.6 | 30.8 | 1 |
| yolo26-l-obb_1024x1024.dxnn | OFF | 84.95 | 30.1 | 30.9 | 1 |
| yolo26-x-obb_1024x1024.dxnn | ON | 155.31 | 16.5 | 16.9 | — |
| yolo26-x-obb_1024x1024.dxnn | OFF | 153.33 | 16.5 | 16.8 | — |

### Classification

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n_224x224.dxnn | ON | 1.42 | 3504.7 | 190.6 | — |
| yolo26-n_224x224.dxnn | OFF | 1.43 | 3508.6 | 190.1 | — |
| yolo26-s_224x224.dxnn | ON | 2.03 | 2007.6 | 190.1 | — |
| yolo26-s_224x224.dxnn | OFF | 2.03 | 2009.5 | 190.4 | — |
| yolo26-m_224x224.dxnn | ON | 2.62 | 1374.0 | 190.3 | — |
| yolo26-m_224x224.dxnn | OFF | 2.67 | 1374.4 | 190.3 | — |
| yolo26-l_224x224.dxnn | ON | 3.87 | 875.2 | 190.1 | — |
| yolo26-l_224x224.dxnn | OFF | 3.89 | 874.7 | 190.2 | — |
| yolo26-x_224x224.dxnn | ON | 6.31 | 484.3 | 189.0 | — |
| yolo26-x_224x224.dxnn | OFF | 6.32 | 484.5 | 189.4 | — |

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
| NPU RT | v3.4.0 |
| NPU Driver (RT) | v2.5.1 |
| NPU Driver (PCIe) | v2.4.1 |
| NPU Firmware | v2.7.1 |
| NPU Memory | LPDDR5 5600 Mbps, 3.92GiB |
| NPU Board | M.2, Rev 1.0 |
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
| yolo26-n_640x640.dxnn | 100.4 ±1.1 | 191 | 22.3 | 74.9 | 38~40 | 1000 | ok |
| yolo26-s_640x640.dxnn | 100.2 ±1.9 | 185 | 42.2 | 73.3 | 45~47 | 1000 | ok |
| yolo26-m_640x640.dxnn | 99.9 ±0.7 | 185 | 73.5 | 87.3 | 53~56 | 1000 | ok |
| yolo26-l_640x640.dxnn | 90.0 ±0.1 | 136 | 90.5 | 100.0 | 54~58 | 1000 | ok |
| yolo26-x_640x640.dxnn | 48.8 ±0.7 | 70 | 88.6 | 100.0 | 55~60 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n_640x640.dxnn | 179.2 ±0.2 | 119 | 43.1 | 74.0 | 45~46 | 1000 | ok |
| yolo26-s_640x640.dxnn | 171.6 ±1.7 | 115 | 80.6 | 91.8 | 50~53 | 1000 | ok |
| yolo26-m_640x640.dxnn | 118.4 ±1.8 | 72 | 92.1 | 100.0 | 54~59 | 1000 | ok |
| yolo26-l_640x640.dxnn | 86.6 ±1.2 | 62 | 90.3 | 100.0 | 53~58 | 1000 | ok |
| yolo26-x_640x640.dxnn | 48.4 ±0.8 | 34 | 88.2 | 100.0 | 55~60 | 1000 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 142.5 ±1.3 | 183 | 36.6 | 71.4 | 47 | 1000 | ok |
| yolo26-s-pose_640x640.dxnn | 142.3 ±0.6 | 181 | 69.2 | 84.2 | 49~51 | 1000 | ok |
| yolo26-m-pose_640x640.dxnn | 113.2 ±0.2 | 114 | 91.1 | 100.0 | 54~59 | 1000 | ok |
| yolo26-l-pose_640x640.dxnn | 84.6 ±2.2 | 81 | 90.7 | 100.0 | 54~58 | 1000 | ok |
| yolo26-x-pose_640x640.dxnn | 46.8 ±0.5 | 48 | 89.3 | 100.0 | 55~60 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 247.6 ±0.1 | 101 | 73.6 | 86.5 | 47~49 | 1000 | ok |
| yolo26-s-pose_640x640.dxnn | 176.3 ±1.3 | 72 | 91.1 | 100.0 | 51~54 | 1000 | ok |
| yolo26-m-pose_640x640.dxnn | 111.6 ±0.6 | 49 | 90.7 | 100.0 | 54~59 | 1000 | ok |
| yolo26-l-pose_640x640.dxnn | 83.8 ±1.7 | 40 | 90.3 | 100.0 | 54~58 | 1000 | ok |
| yolo26-x-pose_640x640.dxnn | 46.2 ±0.3 | 22 | 88.5 | 100.0 | 55~60 | 1000 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 64.3 ±0.7 | 228 | 18.2 | 59.8 | 45 | 1000 | ok |
| yolo26-s-seg_640x640.dxnn | 64.3 ±0.2 | 228 | 35.0 | 65.9 | 45~46 | 1000 | ok |
| yolo26-m-seg_640x640.dxnn | 64.0 ±0.3 | 208 | 68.1 | 86.4 | 53~57 | 1000 | ok |
| yolo26-l-seg_640x640.dxnn | 62.1 ±0.7 | 185 | 85.4 | 100.0 | 54~59 | 1000 | ok |
| yolo26-x-seg_640x640.dxnn | 34.4 ±0.4 | 83 | 89.8 | 100.0 | 56~62 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 95.7 ±0.1 | 136 | 27.5 | 84.1 | 44~45 | 1000 | ok |
| yolo26-s-seg_640x640.dxnn | 95.7 ±0.0 | 134 | 53.5 | 87.1 | 49~51 | 1000 | ok |
| yolo26-m-seg_640x640.dxnn | 78.3 ±0.9 | 110 | 89.4 | 100.0 | 56~61 | 1000 | ok |
| yolo26-l-seg_640x640.dxnn | 64.4 ±0.4 | 94 | 89.7 | 100.0 | 55~60 | 1000 | ok |
| yolo26-x-seg_640x640.dxnn | 34.8 ±0.1 | 51 | 88.6 | 100.0 | 56~62 | 1000 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 103.9 ±0.4 | 115 | 90.2 | 100.0 | 49~52 | 1000 | ok |
| yolo26-s-obb_1024x1024.dxnn | 60.6 ±0.1 | 70 | 91.3 | 100.0 | 50~53 | 1000 | ok |
| yolo26-m-obb_1024x1024.dxnn | 39.8 ±0.2 | 45 | 90.8 | 100.0 | 53~57 | 1000 | ok |
| yolo26-l-obb_1024x1024.dxnn | 29.6 ±0.0 | 33 | 89.6 | 100.0 | 53~57 | 1000 | ok |
| yolo26-x-obb_1024x1024.dxnn | 16.5 ±0.0 | 18 | 87.3 | 100.0 | 55~59 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 98.1 ±0.0 | 56 | 91.4 | 100.0 | 49~51 | 1000 | ok |
| yolo26-s-obb_1024x1024.dxnn | 61.2 ±0.5 | 34 | 90.4 | 100.0 | 50~53 | 1000 | ok |
| yolo26-m-obb_1024x1024.dxnn | 40.1 ±1.0 | 23 | 90.7 | 100.0 | 53~58 | 1000 | ok |
| yolo26-l-obb_1024x1024.dxnn | 30.1 ±1.0 | 16 | 90.8 | 100.0 | 54~58 | 1000 | ok |
| yolo26-x-obb_1024x1024.dxnn | 16.5 ±0.1 | 10 | 86.4 | 100.0 | 56~60 | 1000 | ok |

#### Classification

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n_224x224.dxnn | 3504.7 ±0.8 | 56 | 87.6 | 95.1 | 47~48 | 1000 | ok |
| yolo26-s_224x224.dxnn | 2007.6 ±4.2 | 38 | 91.1 | 97.4 | 47~49 | 1000 | ok |
| yolo26-m_224x224.dxnn | 1374.0 ±2.2 | 27 | 88.9 | 97.8 | 51~54 | 1000 | ok |
| yolo26-l_224x224.dxnn | 875.2 ±0.7 | 18 | 88.4 | 98.3 | 50~52 | 1000 | ok |
| yolo26-x_224x224.dxnn | 484.3 ±0.2 | 10 | 90.0 | 99.3 | 51~54 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n_224x224.dxnn | 3508.6 ±3.9 | 56 | 86.9 | 95.4 | 45~46 | 1000 | ok |
| yolo26-s_224x224.dxnn | 2009.5 ±3.7 | 38 | 90.0 | 97.6 | 48~50 | 1000 | ok |
| yolo26-m_224x224.dxnn | 1374.4 ±0.2 | 27 | 91.2 | 97.4 | 51~55 | 1000 | ok |
| yolo26-l_224x224.dxnn | 874.7 ±0.5 | 18 | 89.3 | 98.2 | 50~52 | 1000 | ok |
| yolo26-x_224x224.dxnn | 484.5 ±0.5 | 10 | 89.1 | 99.3 | 51~54 | 1000 | ok |

### Latency (Single-Core, Sync)

#### Object Detection

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_640x640.dxnn | 42.3 | 23.61 | 20.98 | 2.64 | 36 | ok |
| yolo26-s_640x640.dxnn | 33.7 | 29.70 | 27.14 | 2.56 | 43 | ok |
| yolo26-m_640x640.dxnn | 27.2 | 36.79 | 34.25 | 2.53 | 46 | ok |
| yolo26-l_640x640.dxnn | 23.1 | 43.37 | 40.83 | 2.55 | 46 | ok |
| yolo26-x_640x640.dxnn | 14.4 | 69.46 | 66.95 | 2.51 | 46 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_640x640.dxnn | 43.9 | 22.78 | 22.78 | N/A | 43 | ok |
| yolo26-s_640x640.dxnn | 36.8 | 27.21 | 27.21 | N/A | 46 | ok |
| yolo26-m_640x640.dxnn | 29.1 | 34.38 | 34.38 | N/A | 46 | ok |
| yolo26-l_640x640.dxnn | 24.4 | 40.93 | 40.93 | N/A | 46 | ok |
| yolo26-x_640x640.dxnn | 14.9 | 67.01 | 67.01 | N/A | 47 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-pose_640x640.dxnn | 50.5 | 19.79 | 18.22 | 1.57 | 45 | ok |
| yolo26-s-pose_640x640.dxnn | 37.2 | 26.90 | 25.31 | 1.59 | 45 | ok |
| yolo26-m-pose_640x640.dxnn | 30.1 | 33.27 | 31.69 | 1.58 | 46 | ok |
| yolo26-l-pose_640x640.dxnn | 24.7 | 40.47 | 38.87 | 1.60 | 46 | ok |
| yolo26-x-pose_640x640.dxnn | 15.1 | 66.27 | 64.71 | 1.56 | 47 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-pose_640x640.dxnn | 55.4 | 18.06 | 18.06 | N/A | 44 | ok |
| yolo26-s-pose_640x640.dxnn | 41.3 | 24.23 | 24.23 | N/A | 46 | ok |
| yolo26-m-pose_640x640.dxnn | 32.2 | 31.02 | 31.02 | N/A | 46 | ok |
| yolo26-l-pose_640x640.dxnn | 25.8 | 38.78 | 38.78 | N/A | 46 | ok |
| yolo26-x-pose_640x640.dxnn | 15.4 | 64.80 | 64.80 | N/A | 47 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-seg_640x640.dxnn | 24.3 | 41.17 | 38.16 | 3.01 | 45 | ok |
| yolo26-s-seg_640x640.dxnn | 21.9 | 45.73 | 42.69 | 3.04 | 43 | ok |
| yolo26-m-seg_640x640.dxnn | 16.3 | 61.17 | 58.00 | 3.17 | 46 | ok |
| yolo26-l-seg_640x640.dxnn | 14.2 | 70.57 | 67.58 | 2.99 | 46 | ok |
| yolo26-x-seg_640x640.dxnn | 9.5 | 105.59 | 102.47 | 3.12 | 47 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-seg_640x640.dxnn | 27.9 | 35.84 | 35.84 | N/A | 43 | ok |
| yolo26-s-seg_640x640.dxnn | 22.9 | 43.72 | 43.72 | N/A | 45 | ok |
| yolo26-m-seg_640x640.dxnn | 17.6 | 56.67 | 56.67 | N/A | 46 | ok |
| yolo26-l-seg_640x640.dxnn | 14.9 | 67.13 | 67.13 | N/A | 46 | ok |
| yolo26-x-seg_640x640.dxnn | 9.8 | 102.30 | 102.30 | N/A | 47 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-obb_1024x1024.dxnn | 28.0 | 35.75 | 33.95 | 1.80 | 46 | ok |
| yolo26-s-obb_1024x1024.dxnn | 19.7 | 50.88 | 49.09 | 1.79 | 46 | ok |
| yolo26-m-obb_1024x1024.dxnn | 14.6 | 68.45 | 66.64 | 1.81 | 46 | ok |
| yolo26-l-obb_1024x1024.dxnn | 11.6 | 86.49 | 84.78 | 1.71 | 47 | ok |
| yolo26-x-obb_1024x1024.dxnn | 6.4 | 155.31 | 153.54 | 1.77 | 48 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-obb_1024x1024.dxnn | 29.3 | 34.15 | 34.15 | N/A | 46 | ok |
| yolo26-s-obb_1024x1024.dxnn | 20.1 | 49.87 | 49.87 | N/A | 46 | ok |
| yolo26-m-obb_1024x1024.dxnn | 15.0 | 66.48 | 66.48 | N/A | 47 | ok |
| yolo26-l-obb_1024x1024.dxnn | 11.8 | 84.95 | 84.95 | N/A | 47 | ok |
| yolo26-x-obb_1024x1024.dxnn | 6.5 | 153.33 | 153.33 | N/A | 48 | ok |

#### Classification

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_224x224.dxnn | 705.9 | 1.42 | 1.42 | N/A | 45 | ok |
| yolo26-s_224x224.dxnn | 493.0 | 2.03 | 2.03 | N/A | 43 | ok |
| yolo26-m_224x224.dxnn | 381.6 | 2.62 | 2.62 | N/A | 45 | ok |
| yolo26-l_224x224.dxnn | 258.4 | 3.87 | 3.87 | N/A | 45 | ok |
| yolo26-x_224x224.dxnn | 158.4 | 6.31 | 6.31 | N/A | 45 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_224x224.dxnn | 701.5 | 1.43 | 1.43 | N/A | 43 | ok |
| yolo26-s_224x224.dxnn | 493.7 | 2.03 | 2.03 | N/A | 45 | ok |
| yolo26-m_224x224.dxnn | 374.7 | 2.67 | 2.67 | N/A | 45 | ok |
| yolo26-l_224x224.dxnn | 257.4 | 3.89 | 3.89 | N/A | 45 | ok |
| yolo26-x_224x224.dxnn | 158.1 | 6.32 | 6.32 | N/A | 45 | ok |

## E2E Pipeline (Single-Stream)

### Object Detection

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | avdec_h264 | 3455 | 3 | 64.6 ±0.0 | 53.51 | 317 | 15.9 | 37.7 | 40~41 | 1000 | 322 | ok |
| yolo26-s_640x640.dxnn | avdec_h264 | 3455 | 3 | 64.5 ±0.2 | 53.55 | 312 | 28.0 | 60.3 | 47 | 1000 | 343 | ok |
| yolo26-m_640x640.dxnn | avdec_h264 | 3455 | 3 | 63.8 ±0.4 | 54.14 | 303 | 45.0 | 76.2 | 57~58 | 1000 | 374 | ok |
| yolo26-l_640x640.dxnn | avdec_h264 | 3455 | 3 | 64.1 ±0.3 | 53.93 | 287 | 62.7 | 85.6 | 57~60 | 1000 | 388 | ok |
| yolo26-x_640x640.dxnn | avdec_h264 | 3455 | 3 | 48.5 ±0.1 | 71.29 | 153 | 93.4 | 100.0 | 68~74 | 1000 | 481 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | avdec_h264 | 3455 | 3 | 77.2 ±0.2 | 44.76 | 310 | 17.7 | 55.8 | 45 | 1000 | 352 | ok |
| yolo26-s_640x640.dxnn | avdec_h264 | 3455 | 3 | 77.6 ±0.2 | 44.52 | 304 | 32.3 | 74.3 | 51 | 1000 | 372 | ok |
| yolo26-m_640x640.dxnn | avdec_h264 | 3455 | 3 | 77.1 ±0.6 | 44.80 | 302 | 52.3 | 82.9 | 59~60 | 1000 | 402 | ok |
| yolo26-l_640x640.dxnn | avdec_h264 | 3455 | 3 | 76.9 ±0.1 | 44.92 | 305 | 76.1 | 90.4 | 61~64 | 1000 | 416 | ok |
| yolo26-x_640x640.dxnn | avdec_h264 | 3455 | 3 | 48.9 ±0.2 | 70.70 | 160 | 93.5 | 100.0 | 68~73 | 1000 | 492 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n_640x640.dxnn | 64.6 | 77.2 | -12.6 | -16.4% |
| yolo26-s_640x640.dxnn | 64.5 | 77.6 | -13.1 | -16.9% |
| yolo26-m_640x640.dxnn | 63.8 | 77.1 | -13.3 | -17.3% |
| yolo26-l_640x640.dxnn | 64.1 | 76.9 | -12.8 | -16.7% |
| yolo26-x_640x640.dxnn | 48.5 | 48.9 | -0.4 | -0.8% |

### Pose Estimation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 78.4 ±0.1 | 44.09 | 323 | 20.2 | 45.5 | 45~46 | 1000 | 312 | ok |
| yolo26-s-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 78.1 ±0.3 | 44.24 | 318 | 36.5 | 64.7 | 50~51 | 1000 | 333 | ok |
| yolo26-m-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 78.4 ±0.2 | 44.05 | 307 | 59.3 | 83.3 | 60~62 | 1000 | 366 | ok |
| yolo26-l-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 78.2 ±0.3 | 44.17 | 275 | 82.6 | 95.5 | 62~65 | 1000 | 382 | ok |
| yolo26-x-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 47.5 ±0.2 | 72.74 | 116 | 94.8 | 100.0 | 66~69 | 1000 | 477 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 107.5 ±0.1 | 32.15 | 303 | 27.1 | 59.4 | 48 | 1000 | 292 | ok |
| yolo26-s-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 108.0 ±0.7 | 31.98 | 301 | 48.9 | 74.8 | 53~54 | 1000 | 316 | ok |
| yolo26-m-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 105.7 ±1.0 | 32.67 | 276 | 82.6 | 95.7 | 62~65 | 1000 | 355 | ok |
| yolo26-l-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 83.9 ±0.7 | 41.17 | 184 | 90.7 | 100.0 | 63~66 | 1000 | 369 | ok |
| yolo26-x-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 47.6 ±0.2 | 72.64 | 94 | 94.5 | 100.0 | 69~75 | 1000 | 464 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-pose_640x640.dxnn | 78.4 | 107.5 | -29.1 | -27.1% |
| yolo26-s-pose_640x640.dxnn | 78.1 | 108.0 | -29.9 | -27.7% |
| yolo26-m-pose_640x640.dxnn | 78.4 | 105.7 | -27.3 | -25.8% |
| yolo26-l-pose_640x640.dxnn | 78.2 | 83.9 | -5.7 | -6.8% |
| yolo26-x-pose_640x640.dxnn | 47.5 | 47.6 | -0.1 | -0.1% |

### Segmentation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 42.9 ±0.2 | 80.47 | 313 | 13.7 | 32.8 | 44 | 1000 | 418 | ok |
| yolo26-s-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 42.7 ±0.3 | 80.93 | 307 | 24.8 | 56.8 | 47 | 1000 | 440 | ok |
| yolo26-m-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 42.4 ±0.1 | 81.48 | 291 | 46.1 | 73.3 | 59 | 1000 | 475 | ok |
| yolo26-l-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 42.5 ±0.1 | 81.21 | 277 | 58.7 | 82.5 | 61~63 | 1000 | 488 | ok |
| yolo26-x-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 32.3 ±2.1 | 106.91 | 157 | 91.7 | 100.0 | 74~78 | 800~1000 | 594 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 52.2 ±0.4 | 66.17 | 340 | 15.5 | 47.0 | 44~45 | 1000 | 460 | ok |
| yolo26-s-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 53.0 ±0.2 | 65.24 | 333 | 30.1 | 68.2 | 47~48 | 1000 | 484 | ok |
| yolo26-m-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 51.9 ±0.2 | 66.61 | 324 | 57.3 | 85.6 | 63~64 | 1000 | 528 | ok |
| yolo26-l-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 51.6 ±0.6 | 66.98 | 303 | 71.8 | 87.8 | 60~65 | 1000 | 533 | ok |
| yolo26-x-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 33.3 ±1.7 | 103.63 | 157 | 93.0 | 100.0 | 75~79 | 800~1000 | 612 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-seg_640x640.dxnn | 42.9 | 52.2 | -9.3 | -17.8% |
| yolo26-s-seg_640x640.dxnn | 42.7 | 53.0 | -10.3 | -19.4% |
| yolo26-m-seg_640x640.dxnn | 42.4 | 51.9 | -9.5 | -18.3% |
| yolo26-l-seg_640x640.dxnn | 42.5 | 51.6 | -9.0 | -17.5% |
| yolo26-x-seg_640x640.dxnn | 32.3 | 33.3 | -1.0 | -3.1% |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 66.6 ±0.2 | 39.61 | 316 | 50.6 | 75.7 | 47~51 | 1000 | 342 | ok |
| yolo26-s-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 62.2 ±0.2 | 42.47 | 248 | 90.2 | 100.0 | 56~58 | 1000 | 371 | ok |
| yolo26-m-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 41.6 ±0.2 | 63.51 | 135 | 92.9 | 100.0 | 63~69 | 1000 | 404 | ok |
| yolo26-l-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 30.8 ±0.1 | 85.78 | 94 | 94.4 | 100.0 | 66~71 | 1000 | 423 | ok |
| yolo26-x-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 16.9 ±0.3 | 156.17 | 55 | 93.9 | 100.0 | 72~78 | 1000 | 526 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 78.5 ±0.2 | 33.62 | 310 | 59.0 | 85.9 | 51~52 | 1000 | 334 | ok |
| yolo26-s-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 61.3 ±0.1 | 43.07 | 210 | 91.5 | 100.0 | 56~58 | 1000 | 365 | ok |
| yolo26-m-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 41.9 ±0.4 | 63.05 | 138 | 92.3 | 100.0 | 62~68 | 1000 | 400 | ok |
| yolo26-l-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 30.9 ±0.1 | 85.42 | 94 | 93.5 | 100.0 | 65~69 | 1000 | 422 | ok |
| yolo26-x-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 16.8 ±0.3 | 156.86 | 54 | 94.1 | 100.0 | 73~77 | 1000 | 520 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-obb_1024x1024.dxnn | 66.6 | 78.5 | -11.9 | -15.1% |
| yolo26-s-obb_1024x1024.dxnn | 62.2 | 61.3 | +0.9 | +1.4% |
| yolo26-m-obb_1024x1024.dxnn | 41.6 | 41.9 | -0.3 | -0.7% |
| yolo26-l-obb_1024x1024.dxnn | 30.8 | 30.9 | -0.1 | -0.4% |
| yolo26-x-obb_1024x1024.dxnn | 16.9 | 16.8 | +0.1 | +0.5% |

### Classification

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_224x224.dxnn | avdec_h264 | 3455 | 3 | 190.6 ±0.3 | 18.13 | 270 | 4.1 | 13.5 | 43~46 | 1000 | 217 | ok |
| yolo26-s_224x224.dxnn | avdec_h264 | 3455 | 3 | 190.1 ±0.1 | 18.17 | 270 | 7.4 | 22.6 | 45~47 | 1000 | 218 | ok |
| yolo26-m_224x224.dxnn | avdec_h264 | 3455 | 3 | 190.3 ±0.3 | 18.16 | 268 | 10.8 | 31.0 | 50~51 | 1000 | 227 | ok |
| yolo26-l_224x224.dxnn | avdec_h264 | 3455 | 3 | 190.1 ±0.4 | 18.17 | 269 | 17.3 | 43.2 | 49~50 | 1000 | 250 | ok |
| yolo26-x_224x224.dxnn | avdec_h264 | 3455 | 3 | 189.0 ±0.4 | 18.28 | 268 | 31.5 | 60.6 | 52~53 | 1000 | 296 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_224x224.dxnn | avdec_h264 | 3455 | 3 | 190.1 ±0.4 | 18.17 | 269 | 4.1 | 13.1 | 44 | 1000 | 202 | ok |
| yolo26-s_224x224.dxnn | avdec_h264 | 3455 | 3 | 190.4 ±0.6 | 18.14 | 269 | 7.4 | 22.3 | 46~47 | 1000 | 225 | ok |
| yolo26-m_224x224.dxnn | avdec_h264 | 3455 | 3 | 190.3 ±0.1 | 18.16 | 268 | 10.4 | 30.6 | 46~47 | 1000 | 242 | ok |
| yolo26-l_224x224.dxnn | avdec_h264 | 3455 | 3 | 190.2 ±0.3 | 18.17 | 269 | 17.3 | 43.0 | 49~50 | 1000 | 248 | ok |
| yolo26-x_224x224.dxnn | avdec_h264 | 3455 | 3 | 189.4 ±0.2 | 18.24 | 268 | 31.5 | 60.5 | 52 | 1000 | 293 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n_224x224.dxnn | 190.6 | 190.1 | +0.5 | +0.2% |
| yolo26-s_224x224.dxnn | 190.1 | 190.4 | -0.3 | -0.2% |
| yolo26-m_224x224.dxnn | 190.3 | 190.3 | +0.0 | +0.0% |
| yolo26-l_224x224.dxnn | 190.1 | 190.2 | -0.0 | -0.0% |
| yolo26-x_224x224.dxnn | 189.0 | 189.4 | -0.4 | -0.2% |

## E2E Pipeline (Multi-Stream)

### Object Detection

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | 2 | 3 | 64.4 ±0.2 | 32.2 | 314 | 16.2 | 38.5 | 42~43 | 1000 | 455 | ok |
| yolo26-n_640x640.dxnn | 3 | 3 | 63.6 ±0.7 | 21.2 | 313 | 16.1 | 38.3 | 43 | 1000 | 555 | ok |
| yolo26-s_640x640.dxnn | 2 | 3 | 63.6 ±1.2 | 31.8 | 312 | 28.7 | 59.4 | 46~47 | 1000 | 476 | ok |
| yolo26-s_640x640.dxnn | 3 | 3 | 63.5 ±0.5 | 21.2 | 312 | 28.7 | 60.0 | 47 | 1000 | 575 | ok |
| yolo26-m_640x640.dxnn | 2 | 3 | 62.2 ±0.5 | 31.1 | 306 | 44.3 | 73.0 | 59 | 1000 | 506 | ok |
| yolo26-m_640x640.dxnn | 3 | 3 | 62.5 ±0.2 | 20.9 | 306 | 45.7 | 75.3 | 59~60 | 1000 | 607 | ok |
| yolo26-l_640x640.dxnn | 2 | 3 | 63.1 ±0.9 | 31.6 | 292 | 63.5 | 85.6 | 61~63 | 1000 | 523 | ok |
| yolo26-l_640x640.dxnn | 3 | 3 | 61.9 ±0.3 | 20.6 | 293 | 62.6 | 84.9 | 65~66 | 1000 | 621 | ok |
| yolo26-x_640x640.dxnn | 1 | 3 | 48.5 ±0.1 | 48.5 | 153 | 93.4 | 100.0 | 68~74 | 1000 | 481 | ok |
| yolo26-x_640x640.dxnn | 2 | 3 | 45.6 ±0.7 | 22.8 | 148 | 95.3 | 100.0 | 78~79 | 800~1000 | 613 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | 2 | 3 | 77.1 ±0.2 | 38.5 | 311 | 18.1 | 57.3 | 43~44 | 1000 | 482 | ok |
| yolo26-n_640x640.dxnn | 3 | 3 | 77.1 ±0.1 | 25.7 | 310 | 18.2 | 57.2 | 43~44 | 1000 | 580 | ok |
| yolo26-s_640x640.dxnn | 2 | 3 | 77.1 ±0.0 | 38.5 | 310 | 32.9 | 71.6 | 49~50 | 1000 | 503 | ok |
| yolo26-s_640x640.dxnn | 3 | 3 | 77.3 ±0.2 | 25.8 | 308 | 33.6 | 71.4 | 49 | 1000 | 602 | ok |
| yolo26-m_640x640.dxnn | 2 | 3 | 76.4 ±0.4 | 38.2 | 309 | 53.9 | 84.4 | 61~62 | 1000 | 538 | ok |
| yolo26-m_640x640.dxnn | 3 | 3 | 76.8 ±0.9 | 25.6 | 305 | 54.4 | 83.2 | 63 | 1000 | 636 | ok |
| yolo26-l_640x640.dxnn | 2 | 3 | 76.4 ±0.4 | 38.2 | 309 | 77.2 | 89.1 | 67~69 | 1000 | 549 | ok |
| yolo26-l_640x640.dxnn | 3 | 3 | 76.8 ±0.1 | 25.6 | 310 | 78.8 | 92.1 | 70~71 | 1000 | 650 | ok |
| yolo26-x_640x640.dxnn | 1 | 3 | 48.9 ±0.2 | 48.9 | 160 | 93.5 | 100.0 | 68~73 | 1000 | 492 | ok |
| yolo26-x_640x640.dxnn | 2 | 3 | 45.7 ±0.9 | 22.8 | 159 | 94.8 | 100.0 | 78~79 | 800~1000 | 624 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n_640x640.dxnn | 2 | 32.2 | 2 | 38.5 |
| yolo26-s_640x640.dxnn | 2 | 31.8 | 2 | 38.5 |
| yolo26-m_640x640.dxnn | 2 | 31.1 | 2 | 38.2 |
| yolo26-l_640x640.dxnn | 2 | 31.6 | 2 | 38.2 |
| yolo26-x_640x640.dxnn | 1 | 48.5 | 1 | 48.9 |

### Pose Estimation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 2 | 3 | 77.9 ±0.3 | 39.0 | 322 | 21.2 | 47.8 | 45 | 1000 | 448 | ok |
| yolo26-n-pose_640x640.dxnn | 3 | 3 | 77.1 ±1.6 | 25.7 | 322 | 21.2 | 47.0 | 44 | 1000 | 553 | ok |
| yolo26-s-pose_640x640.dxnn | 2 | 3 | 76.1 ±1.4 | 38.0 | 320 | 36.9 | 66.9 | 50 | 1000 | 472 | ok |
| yolo26-s-pose_640x640.dxnn | 3 | 3 | 76.3 ±1.4 | 25.4 | 319 | 37.6 | 68.3 | 50 | 1000 | 576 | ok |
| yolo26-m-pose_640x640.dxnn | 2 | 3 | 75.3 ±0.8 | 37.7 | 310 | 59.1 | 81.6 | 63~64 | 1000 | 500 | ok |
| yolo26-m-pose_640x640.dxnn | 3 | 3 | 76.6 ±1.4 | 25.6 | 310 | 60.8 | 82.6 | 60~65 | 1000 | 604 | ok |
| yolo26-l-pose_640x640.dxnn | 2 | 3 | 75.6 ±0.6 | 37.8 | 284 | 82.2 | 96.4 | 69~70 | 1000 | 514 | ok |
| yolo26-l-pose_640x640.dxnn | 3 | 3 | 75.5 ±0.2 | 25.2 | 285 | 82.6 | 95.7 | 72 | 1000 | 622 | ok |
| yolo26-x-pose_640x640.dxnn | 1 | 3 | 47.5 ±0.2 | 47.5 | 116 | 94.8 | 100.0 | 66~69 | 1000 | 477 | ok |
| yolo26-x-pose_640x640.dxnn | 2 | 3 | 45.6 ±1.4 | 22.8 | 118 | 95.5 | 100.0 | 78 | 800~1000 | 609 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 3 | 3 | 107.9 ±1.4 | 36.0 | 331 | 30.8 | 53.2 | 47 | 1000 | 542 | ok |
| yolo26-n-pose_640x640.dxnn | 4 | 3 | 107.8 ±0.3 | 26.9 | 332 | 30.7 | 52.0 | 46~47 | 1000 | 651 | ok |
| yolo26-s-pose_640x640.dxnn | 3 | 3 | 107.5 ±1.6 | 35.8 | 325 | 54.2 | 75.0 | 54 | 1000 | 568 | ok |
| yolo26-s-pose_640x640.dxnn | 4 | 3 | 106.5 ±0.3 | 26.6 | 326 | 54.1 | 76.4 | 55 | 1000 | 672 | ok |
| yolo26-m-pose_640x640.dxnn | 3 | 3 | 104.0 ±0.7 | 34.7 | 294 | 86.5 | 96.2 | 70~73 | 1000 | 594 | ok |
| yolo26-m-pose_640x640.dxnn | 4 | 3 | 103.1 ±0.1 | 25.8 | 295 | 86.0 | 96.2 | 75 | 1000 | 696 | ok |
| yolo26-l-pose_640x640.dxnn | 2 | 3 | 84.0 ±0.1 | 42.0 | 194 | 94.3 | 100.0 | 71~74 | 1000 | 503 | ok |
| yolo26-l-pose_640x640.dxnn | 3 | 3 | 83.5 ±0.9 | 27.9 | 197 | 95.3 | 100.0 | 76~77 | 1000 | 607 | ok |
| yolo26-x-pose_640x640.dxnn | 1 | 3 | 47.6 ±0.2 | 47.6 | 94 | 94.5 | 100.0 | 69~75 | 1000 | 464 | ok |
| yolo26-x-pose_640x640.dxnn | 2 | 3 | 43.7 ±0.8 | 21.9 | 99 | 94.6 | 100.0 | 78~79 | 800~1000 | 599 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-pose_640x640.dxnn | 2 | 39.0 | 3 | 36.0 |
| yolo26-s-pose_640x640.dxnn | 2 | 38.0 | 3 | 35.8 |
| yolo26-m-pose_640x640.dxnn | 2 | 37.7 | 3 | 34.7 |
| yolo26-l-pose_640x640.dxnn | 2 | 37.8 | 2 | 42.0 |
| yolo26-x-pose_640x640.dxnn | 1 | 47.5 | 1 | 47.6 |

### Segmentation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 1 | 3 | 42.9 ±0.2 | 42.9 | 313 | 13.7 | 32.8 | 44 | 1000 | 418 | ok |
| yolo26-n-seg_640x640.dxnn | 2 | 3 | 41.6 ±0.2 | 20.8 | 312 | 13.3 | 33.0 | 43~44 | 1000 | 557 | ok |
| yolo26-s-seg_640x640.dxnn | 1 | 3 | 42.7 ±0.3 | 42.7 | 307 | 24.8 | 56.8 | 47 | 1000 | 440 | ok |
| yolo26-s-seg_640x640.dxnn | 2 | 3 | 41.8 ±0.4 | 20.9 | 310 | 24.7 | 59.5 | 47 | 1000 | 584 | ok |
| yolo26-m-seg_640x640.dxnn | 1 | 3 | 42.4 ±0.1 | 42.4 | 291 | 46.1 | 73.3 | 59 | 1000 | 475 | ok |
| yolo26-m-seg_640x640.dxnn | 2 | 3 | 41.7 ±0.7 | 20.9 | 296 | 46.0 | 73.2 | 61 | 1000 | 614 | ok |
| yolo26-l-seg_640x640.dxnn | 1 | 3 | 42.5 ±0.1 | 42.5 | 277 | 58.7 | 82.5 | 61~63 | 1000 | 488 | ok |
| yolo26-l-seg_640x640.dxnn | 2 | 3 | 41.4 ±0.9 | 20.7 | 282 | 57.6 | 86.7 | 64~66 | 1000 | 630 | ok |
| yolo26-x-seg_640x640.dxnn | 1 | 3 | 32.3 ±2.1 | 32.3 | 157 | 91.7 | 100.0 | 74~78 | 800~1000 | 594 | ok |
| yolo26-x-seg_640x640.dxnn | 2 | 3 | 29.2 ±0.0 | 14.6 | 142 | 91.4 | 100.0 | 80 | 600~1000 | 738 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 1 | 3 | 52.2 ±0.4 | 52.2 | 340 | 15.5 | 47.0 | 44~45 | 1000 | 460 | ok |
| yolo26-n-seg_640x640.dxnn | 2 | 3 | 52.9 ±0.4 | 26.5 | 336 | 16.0 | 49.5 | 43~44 | 1000 | 603 | ok |
| yolo26-s-seg_640x640.dxnn | 1 | 3 | 53.0 ±0.2 | 53.0 | 333 | 30.1 | 68.2 | 47~48 | 1000 | 484 | ok |
| yolo26-s-seg_640x640.dxnn | 2 | 3 | 52.2 ±0.0 | 26.1 | 338 | 29.9 | 69.4 | 48 | 1000 | 626 | ok |
| yolo26-m-seg_640x640.dxnn | 1 | 3 | 51.9 ±0.2 | 51.9 | 324 | 57.3 | 85.6 | 63~64 | 1000 | 528 | ok |
| yolo26-m-seg_640x640.dxnn | 2 | 3 | 51.6 ±0.3 | 25.8 | 329 | 57.6 | 81.7 | 65~66 | 1000 | 669 | ok |
| yolo26-l-seg_640x640.dxnn | 1 | 3 | 51.6 ±0.6 | 51.6 | 303 | 71.8 | 87.8 | 60~65 | 1000 | 533 | ok |
| yolo26-l-seg_640x640.dxnn | 2 | 3 | 51.1 ±0.3 | 25.5 | 308 | 72.8 | 89.6 | 68~69 | 1000 | 677 | ok |
| yolo26-x-seg_640x640.dxnn | 1 | 3 | 33.3 ±1.7 | 33.3 | 157 | 93.0 | 100.0 | 75~79 | 800~1000 | 612 | ok |
| yolo26-x-seg_640x640.dxnn | 2 | 3 | 29.5 ±0.1 | 14.8 | 146 | 91.8 | 100.0 | 79~80 | 800~1000 | 762 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-seg_640x640.dxnn | 1 | 42.9 | 1 | 52.2 |
| yolo26-s-seg_640x640.dxnn | 1 | 42.7 | 1 | 53.0 |
| yolo26-m-seg_640x640.dxnn | 1 | 42.4 | 1 | 51.9 |
| yolo26-l-seg_640x640.dxnn | 1 | 42.5 | 1 | 51.6 |
| yolo26-x-seg_640x640.dxnn | 1 | 32.3 | 1 | 33.3 |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 2 | 3 | 66.2 ±0.2 | 33.1 | 322 | 52.5 | 76.7 | 50~51 | 1000 | 482 | ok |
| yolo26-n-obb_1024x1024.dxnn | 3 | 3 | 65.7 ±0.5 | 21.9 | 323 | 52.5 | 76.9 | 51~52 | 1000 | 586 | ok |
| yolo26-s-obb_1024x1024.dxnn | 2 | 3 | 62.1 ±0.2 | 31.1 | 253 | 93.2 | 100.0 | 59~62 | 1000 | 506 | ok |
| yolo26-s-obb_1024x1024.dxnn | 3 | 3 | 62.0 ±0.1 | 20.7 | 252 | 93.3 | 100.0 | 63~64 | 1000 | 609 | ok |
| yolo26-m-obb_1024x1024.dxnn | 1 | 3 | 41.6 ±0.2 | 41.6 | 135 | 92.9 | 100.0 | 63~69 | 1000 | 404 | ok |
| yolo26-m-obb_1024x1024.dxnn | 2 | 3 | 41.2 ±0.3 | 20.6 | 155 | 95.3 | 100.0 | 74~76 | 1000 | 534 | ok |
| yolo26-l-obb_1024x1024.dxnn | 1 | 3 | 30.8 ±0.1 | 30.8 | 94 | 94.4 | 100.0 | 66~71 | 1000 | 423 | ok |
| yolo26-l-obb_1024x1024.dxnn | 2 | 3 | 30.6 ±0.1 | 15.3 | 98 | 95.3 | 100.0 | 75~76 | 1000 | 552 | ok |
| yolo26-x-obb_1024x1024.dxnn | 1 | 3 | 16.9 ±0.3 | 16.9 | 55 | 93.9 | 100.0 | 72~78 | 1000 | 526 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 2 | 3 | 78.8 ±0.1 | 39.4 | 331 | 65.8 | 83.6 | 52~53 | 1000 | 502 | ok |
| yolo26-n-obb_1024x1024.dxnn | 3 | 3 | 79.2 ±0.7 | 26.4 | 333 | 67.2 | 88.3 | 51~53 | 1000 | 600 | ok |
| yolo26-s-obb_1024x1024.dxnn | 2 | 3 | 61.5 ±0.4 | 30.8 | 221 | 94.4 | 100.0 | 60~62 | 1000 | 505 | ok |
| yolo26-s-obb_1024x1024.dxnn | 3 | 3 | 61.6 ±0.2 | 20.6 | 220 | 95.5 | 100.0 | 64~65 | 1000 | 604 | ok |
| yolo26-m-obb_1024x1024.dxnn | 1 | 3 | 41.9 ±0.4 | 41.9 | 138 | 92.3 | 100.0 | 62~68 | 1000 | 400 | ok |
| yolo26-m-obb_1024x1024.dxnn | 2 | 3 | 41.7 ±0.2 | 20.9 | 133 | 95.6 | 100.0 | 72~75 | 1000 | 536 | ok |
| yolo26-l-obb_1024x1024.dxnn | 1 | 3 | 30.9 ±0.1 | 30.9 | 94 | 93.5 | 100.0 | 65~69 | 1000 | 422 | ok |
| yolo26-l-obb_1024x1024.dxnn | 2 | 3 | 30.9 ±0.1 | 15.4 | 98 | 95.3 | 100.0 | 73~76 | 1000 | 546 | ok |
| yolo26-x-obb_1024x1024.dxnn | 1 | 3 | 16.8 ±0.3 | 16.8 | 54 | 94.1 | 100.0 | 73~77 | 1000 | 520 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-obb_1024x1024.dxnn | 2 | 33.1 | 2 | 39.4 |
| yolo26-s-obb_1024x1024.dxnn | 2 | 31.1 | 2 | 30.8 |
| yolo26-m-obb_1024x1024.dxnn | 1 | 41.6 | 1 | 41.9 |
| yolo26-l-obb_1024x1024.dxnn | 1 | 30.8 | 1 | 30.9 |

---
*Report generated by dx-benchmark tool*
