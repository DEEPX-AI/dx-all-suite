# YOLO26 Benchmark Report

**Generated:** 2026-07-13 14:15:33 (Local)

## Test Timing

| # | Type | Start | End | Duration |
|---|------|-------|-----|----------|
| 1 | retry-failed | 2026-07-13 10:21:39 | 2026-07-13 14:15:33 | 3h 53m 54s |

## Executive Summary

### Object Detection

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n_640x640.dxnn | ON | 10.80 | 972.1 | 478.1 | 17 |
| yolo26-n_640x640.dxnn | OFF | 10.45 | 1285.0 | 421.5 | 13 |
| yolo26-s_640x640.dxnn | ON | 16.52 | 785.4 | 475.7 | 17 |
| yolo26-s_640x640.dxnn | OFF | 16.27 | 774.6 | 425.0 | 13 |
| yolo26-m_640x640.dxnn | ON | 23.52 | 476.4 | 476.6 | 16 |
| yolo26-m_640x640.dxnn | OFF | 23.35 | 471.3 | 424.9 | 13 |
| yolo26-l_640x640.dxnn | ON | 30.78 | 352.9 | 367.3 | 12 |
| yolo26-l_640x640.dxnn | OFF | 30.46 | 352.8 | 367.7 | 12 |
| yolo26-x_640x640.dxnn | ON | 56.32 | 194.4 | 200.1 | 6 |
| yolo26-x_640x640.dxnn | OFF | 56.17 | 193.9 | 200.4 | 6 |

### Pose Estimation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-pose_640x640.dxnn | ON | 10.47 | 1178.7 | 517.9 | 18 |
| yolo26-n-pose_640x640.dxnn | OFF | 10.66 | 1157.9 | 534.8 | 19 |
| yolo26-s-pose_640x640.dxnn | ON | 16.70 | 717.5 | 516.8 | 16 |
| yolo26-s-pose_640x640.dxnn | OFF | 16.58 | 718.9 | 536.3 | 19 |
| yolo26-m-pose_640x640.dxnn | ON | 24.13 | 459.4 | 466.9 | 15 |
| yolo26-m-pose_640x640.dxnn | OFF | 23.90 | 458.4 | 466.1 | 15 |
| yolo26-l-pose_640x640.dxnn | ON | 31.75 | 339.5 | 352.9 | 11 |
| yolo26-l-pose_640x640.dxnn | OFF | 30.97 | 339.1 | 352.6 | 11 |
| yolo26-x-pose_640x640.dxnn | ON | 57.07 | 190.6 | 196.0 | 6 |
| yolo26-x-pose_640x640.dxnn | OFF | 56.79 | 189.9 | 196.2 | 6 |

### Segmentation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-seg_640x640.dxnn | ON | 18.93 | 529.8 | 344.7 | 11 |
| yolo26-n-seg_640x640.dxnn | OFF | 18.48 | 560.8 | 297.9 | 9 |
| yolo26-s-seg_640x640.dxnn | ON | 26.62 | 528.9 | 344.7 | 11 |
| yolo26-s-seg_640x640.dxnn | OFF | 26.39 | 561.5 | 293.0 | 9 |
| yolo26-m-seg_640x640.dxnn | ON | 40.45 | 326.5 | 315.9 | 9 |
| yolo26-m-seg_640x640.dxnn | OFF | 39.81 | 321.5 | 296.4 | 9 |
| yolo26-l-seg_640x640.dxnn | ON | 47.29 | 256.3 | 263.0 | 8 |
| yolo26-l-seg_640x640.dxnn | OFF | 47.06 | 256.4 | 262.2 | 8 |
| yolo26-x-seg_640x640.dxnn | ON | 84.92 | 136.3 | 139.7 | 4 |
| yolo26-x-seg_640x640.dxnn | OFF | 84.32 | 135.8 | 140.6 | 4 |

### Oriented BBox (OBB)

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-obb_1024x1024.dxnn | ON | 23.15 | 410.6 | 364.7 | 13 |
| yolo26-n-obb_1024x1024.dxnn | OFF | 22.80 | 409.8 | 367.1 | 13 |
| yolo26-s-obb_1024x1024.dxnn | ON | 38.05 | 250.9 | 261.7 | 8 |
| yolo26-s-obb_1024x1024.dxnn | OFF | 37.63 | 251.1 | 262.0 | 8 |
| yolo26-m-obb_1024x1024.dxnn | ON | 55.42 | 166.5 | 174.0 | 5 |
| yolo26-m-obb_1024x1024.dxnn | OFF | 55.23 | 166.0 | 173.6 | 5 |
| yolo26-l-obb_1024x1024.dxnn | ON | 73.87 | 123.9 | 129.1 | 4 |
| yolo26-l-obb_1024x1024.dxnn | OFF | 73.77 | 124.0 | 129.2 | 4 |
| yolo26-x-obb_1024x1024.dxnn | ON | 141.26 | 68.6 | 70.8 | 2 |
| yolo26-x-obb_1024x1024.dxnn | OFF | 141.13 | 68.7 | 70.8 | 2 |

### Classification

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n_224x224.dxnn | ON | 1.11 | 13695.5 | 747.7 | — |
| yolo26-n_224x224.dxnn | OFF | 0.98 | 13676.6 | 726.1 | — |
| yolo26-s_224x224.dxnn | ON | 1.69 | 7776.7 | 720.2 | — |
| yolo26-s_224x224.dxnn | OFF | 1.71 | 7806.0 | 734.3 | — |
| yolo26-m_224x224.dxnn | ON | 2.25 | 5472.7 | 734.1 | — |
| yolo26-m_224x224.dxnn | OFF | 2.62 | 5470.5 | 717.4 | — |
| yolo26-l_224x224.dxnn | ON | 3.54 | 3484.3 | 731.1 | — |
| yolo26-l_224x224.dxnn | OFF | 3.44 | 3493.2 | 733.1 | — |
| yolo26-x_224x224.dxnn | ON | 5.95 | 1949.6 | 710.6 | — |
| yolo26-x_224x224.dxnn | OFF | 6.28 | 1945.4 | 719.2 | — |

## Environment

| Item | Value |
|------|-------|
| Hostname | deepx-B650MT |
| OS | Ubuntu 22.04.5 LTS |
| Kernel | 6.8.0-124-generic |
| CPU | AMD Ryzen 5 9600X 6-Core Processor |
| CPU Cores | 12 |
| RAM | 30.5 GB |
| NPU SKU | H1-Quattro |
| NPU RT | v3.4.0 |
| NPU Driver (RT) | v2.5.1 |
| NPU Driver (PCIe) | v2.4.1 |
| NPU Firmware | v2.7.1 |
| NPU Memory | LPDDR5x 6000 Mbps, 3.92GiB |
| NPU Board | H1, Rev 0.0 |
| NPU PCIe | Gen3 X4 [04:00:00] |

### Tools

| Tool | Available | Version |
|------|-----------|---------|
| run_model | Yes | DXRT v3.4.0 run_model |
| gst-launch-1.0 | Yes | gst-launch-1.0 version 1.20.3 |
| gst-inspect-1.0 | Yes | gst-inspect-1.0 version 1.20.3 |
| dxtop | Yes | DX-TOP 1.1.0 |
| ffprobe | Yes | ffprobe version 4.4.2-0ubuntu0.22.04.1 Copyright (c) 2007-20... |

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
| yolo26-n_640x640.dxnn | 972.1 ±7.0 | 313 | 62.5 | 80.5 | 50~52 | 1000 | ok |
| yolo26-s_640x640.dxnn | 785.4 ±2.9 | 216 | 91.5 | 100.0 | 59~61 | 1000 | ok |
| yolo26-m_640x640.dxnn | 476.4 ±2.3 | 123 | 89.9 | 100.0 | 61~65 | 1000 | ok |
| yolo26-l_640x640.dxnn | 352.9 ±1.3 | 91 | 91.7 | 100.0 | 60~64 | 1000 | ok |
| yolo26-x_640x640.dxnn | 194.4 ±0.8 | 48 | 90.6 | 100.0 | 61~65 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n_640x640.dxnn | 1285.0 ±4.1 | 266 | 89.3 | 100.0 | 58~60 | 1000 | ok |
| yolo26-s_640x640.dxnn | 774.6 ±5.9 | 140 | 89.8 | 100.0 | 59~61 | 1000 | ok |
| yolo26-m_640x640.dxnn | 471.3 ±1.6 | 83 | 93.3 | 100.0 | 61~65 | 1000 | ok |
| yolo26-l_640x640.dxnn | 352.8 ±0.9 | 61 | 91.7 | 100.0 | 60~64 | 1000 | ok |
| yolo26-x_640x640.dxnn | 193.9 ±0.3 | 33 | 90.3 | 100.0 | 61~65 | 1000 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 1178.7 ±3.0 | 234 | 93.0 | 100.0 | 58~59 | 1000 | ok |
| yolo26-s-pose_640x640.dxnn | 717.5 ±1.7 | 132 | 93.5 | 100.0 | 59~61 | 1000 | ok |
| yolo26-m-pose_640x640.dxnn | 459.4 ±2.4 | 80 | 92.6 | 100.0 | 61~65 | 1000 | ok |
| yolo26-l-pose_640x640.dxnn | 339.5 ±1.9 | 60 | 90.9 | 100.0 | 60~64 | 1000 | ok |
| yolo26-x-pose_640x640.dxnn | 190.6 ±0.8 | 33 | 89.4 | 100.0 | 61~65 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 1157.9 ±2.3 | 148 | 91.1 | 100.0 | 58~60 | 1000 | ok |
| yolo26-s-pose_640x640.dxnn | 718.9 ±2.4 | 84 | 92.1 | 100.0 | 59~61 | 1000 | ok |
| yolo26-m-pose_640x640.dxnn | 458.4 ±2.1 | 52 | 91.0 | 100.0 | 61~65 | 1000 | ok |
| yolo26-l-pose_640x640.dxnn | 339.1 ±0.4 | 41 | 89.8 | 100.0 | 60~64 | 1000 | ok |
| yolo26-x-pose_640x640.dxnn | 189.9 ±0.5 | 22 | 89.7 | 100.0 | 61~65 | 1000 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 529.8 ±1.8 | 510 | 39.5 | 72.1 | 56~57 | 1000 | ok |
| yolo26-s-seg_640x640.dxnn | 528.9 ±2.1 | 501 | 81.6 | 94.9 | 59~62 | 1000 | ok |
| yolo26-m-seg_640x640.dxnn | 326.5 ±1.3 | 276 | 91.1 | 100.0 | 62~67 | 1000 | ok |
| yolo26-l-seg_640x640.dxnn | 256.3 ±1.1 | 213 | 91.4 | 100.0 | 61~65 | 1000 | ok |
| yolo26-x-seg_640x640.dxnn | 136.3 ±1.2 | 108 | 88.8 | 100.0 | 62~66 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 560.8 ±4.5 | 414 | 45.2 | 72.7 | 56~58 | 1000 | ok |
| yolo26-s-seg_640x640.dxnn | 561.5 ±1.7 | 412 | 89.3 | 100.0 | 59~62 | 1000 | ok |
| yolo26-m-seg_640x640.dxnn | 321.5 ±1.7 | 221 | 90.2 | 100.0 | 62~67 | 1000 | ok |
| yolo26-l-seg_640x640.dxnn | 256.4 ±1.3 | 175 | 90.1 | 100.0 | 61~65 | 1000 | ok |
| yolo26-x-seg_640x640.dxnn | 135.8 ±0.3 | 91 | 88.8 | 100.0 | 62~66 | 1000 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 410.6 ±0.9 | 85 | 92.5 | 100.0 | 58~59 | 1000 | ok |
| yolo26-s-obb_1024x1024.dxnn | 250.9 ±1.0 | 51 | 91.6 | 100.0 | 59~61 | 1000 | ok |
| yolo26-m-obb_1024x1024.dxnn | 166.5 ±0.8 | 32 | 90.2 | 100.0 | 61~64 | 1000 | ok |
| yolo26-l-obb_1024x1024.dxnn | 123.9 ±0.3 | 25 | 89.9 | 100.0 | 60~64 | 1000 | ok |
| yolo26-x-obb_1024x1024.dxnn | 68.6 ±0.1 | 14 | 88.6 | 100.0 | 61~65 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 409.8 ±0.6 | 60 | 91.9 | 100.0 | 58~59 | 1000 | ok |
| yolo26-s-obb_1024x1024.dxnn | 251.1 ±0.8 | 35 | 90.9 | 100.0 | 58~61 | 1000 | ok |
| yolo26-m-obb_1024x1024.dxnn | 166.0 ±0.4 | 23 | 91.2 | 100.0 | 60~64 | 1000 | ok |
| yolo26-l-obb_1024x1024.dxnn | 124.0 ±0.1 | 18 | 89.4 | 100.0 | 60~64 | 1000 | ok |
| yolo26-x-obb_1024x1024.dxnn | 68.7 ±0.1 | 10 | 88.8 | 100.0 | 61~65 | 1000 | ok |

#### Classification

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n_224x224.dxnn | 13695.5 ±86.6 | 64 | 84.8 | 92.4 | 56~57 | 1000 | ok |
| yolo26-s_224x224.dxnn | 7776.7 ±28.2 | 36 | 87.8 | 95.7 | 57~59 | 1000 | ok |
| yolo26-m_224x224.dxnn | 5472.7 ±29.7 | 25 | 87.0 | 97.0 | 60~62 | 1000 | ok |
| yolo26-l_224x224.dxnn | 3484.3 ±21.9 | 16 | 89.3 | 98.0 | 58~61 | 1000 | ok |
| yolo26-x_224x224.dxnn | 1949.6 ±8.1 | 9 | 87.9 | 99.3 | 59~62 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n_224x224.dxnn | 13676.6 ±69.0 | 64 | 82.9 | 92.2 | 56~57 | 1000 | ok |
| yolo26-s_224x224.dxnn | 7806.0 ±26.7 | 36 | 87.6 | 95.6 | 57~59 | 1000 | ok |
| yolo26-m_224x224.dxnn | 5470.5 ±27.6 | 25 | 85.9 | 96.5 | 59~62 | 1000 | ok |
| yolo26-l_224x224.dxnn | 3493.2 ±5.7 | 16 | 89.1 | 98.4 | 59~60 | 1000 | ok |
| yolo26-x_224x224.dxnn | 1945.4 ±10.5 | 9 | 88.6 | 99.2 | 59~62 | 1000 | ok |

### Latency (Single-Core, Sync)

#### Object Detection

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_640x640.dxnn | 92.6 | 10.80 | 10.50 | 0.30 | 47 | ok |
| yolo26-s_640x640.dxnn | 60.5 | 16.52 | 16.26 | 0.26 | 55 | ok |
| yolo26-m_640x640.dxnn | 42.5 | 23.52 | 23.26 | 0.26 | 55 | ok |
| yolo26-l_640x640.dxnn | 32.5 | 30.78 | 30.52 | 0.26 | 55 | ok |
| yolo26-x_640x640.dxnn | 17.8 | 56.32 | 56.03 | 0.29 | 55 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_640x640.dxnn | 95.7 | 10.45 | 10.45 | N/A | 55 | ok |
| yolo26-s_640x640.dxnn | 61.5 | 16.27 | 16.27 | N/A | 55 | ok |
| yolo26-m_640x640.dxnn | 42.8 | 23.35 | 23.35 | N/A | 55 | ok |
| yolo26-l_640x640.dxnn | 32.8 | 30.46 | 30.46 | N/A | 55 | ok |
| yolo26-x_640x640.dxnn | 17.8 | 56.17 | 56.17 | N/A | 55 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-pose_640x640.dxnn | 95.5 | 10.47 | 10.28 | 0.19 | 55 | ok |
| yolo26-s-pose_640x640.dxnn | 59.9 | 16.70 | 16.46 | 0.24 | 55 | ok |
| yolo26-m-pose_640x640.dxnn | 41.4 | 24.13 | 23.91 | 0.22 | 55 | ok |
| yolo26-l-pose_640x640.dxnn | 31.5 | 31.75 | 31.54 | 0.21 | 55 | ok |
| yolo26-x-pose_640x640.dxnn | 17.5 | 57.07 | 56.81 | 0.25 | 55 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-pose_640x640.dxnn | 93.8 | 10.66 | 10.66 | N/A | 55 | ok |
| yolo26-s-pose_640x640.dxnn | 60.3 | 16.58 | 16.58 | N/A | 55 | ok |
| yolo26-m-pose_640x640.dxnn | 41.8 | 23.90 | 23.90 | N/A | 55 | ok |
| yolo26-l-pose_640x640.dxnn | 32.3 | 30.97 | 30.97 | N/A | 55 | ok |
| yolo26-x-pose_640x640.dxnn | 17.6 | 56.79 | 56.79 | N/A | 55 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-seg_640x640.dxnn | 52.8 | 18.93 | 18.54 | 0.39 | 55 | ok |
| yolo26-s-seg_640x640.dxnn | 37.6 | 26.62 | 26.24 | 0.37 | 55 | ok |
| yolo26-m-seg_640x640.dxnn | 24.7 | 40.45 | 40.06 | 0.39 | 55 | ok |
| yolo26-l-seg_640x640.dxnn | 21.1 | 47.29 | 46.91 | 0.38 | 55 | ok |
| yolo26-x-seg_640x640.dxnn | 11.8 | 84.92 | 84.54 | 0.37 | 55 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-seg_640x640.dxnn | 54.1 | 18.48 | 18.48 | N/A | 55 | ok |
| yolo26-s-seg_640x640.dxnn | 37.9 | 26.39 | 26.39 | N/A | 55 | ok |
| yolo26-m-seg_640x640.dxnn | 25.1 | 39.81 | 39.81 | N/A | 55 | ok |
| yolo26-l-seg_640x640.dxnn | 21.3 | 47.06 | 47.06 | N/A | 55 | ok |
| yolo26-x-seg_640x640.dxnn | 11.9 | 84.32 | 84.32 | N/A | 55 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-obb_1024x1024.dxnn | 43.2 | 23.15 | 22.92 | 0.23 | 55 | ok |
| yolo26-s-obb_1024x1024.dxnn | 26.3 | 38.05 | 37.80 | 0.25 | 55 | ok |
| yolo26-m-obb_1024x1024.dxnn | 18.0 | 55.42 | 55.22 | 0.20 | 55 | ok |
| yolo26-l-obb_1024x1024.dxnn | 13.5 | 73.87 | 73.65 | 0.22 | 55 | ok |
| yolo26-x-obb_1024x1024.dxnn | 7.1 | 141.26 | 141.02 | 0.24 | 55 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-obb_1024x1024.dxnn | 43.9 | 22.80 | 22.80 | N/A | 55 | ok |
| yolo26-s-obb_1024x1024.dxnn | 26.6 | 37.63 | 37.63 | N/A | 55 | ok |
| yolo26-m-obb_1024x1024.dxnn | 18.1 | 55.23 | 55.23 | N/A | 55 | ok |
| yolo26-l-obb_1024x1024.dxnn | 13.6 | 73.77 | 73.77 | N/A | 55 | ok |
| yolo26-x-obb_1024x1024.dxnn | 7.1 | 141.13 | 141.13 | N/A | 55 | ok |

#### Classification

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_224x224.dxnn | 898.8 | 1.11 | 1.11 | N/A | 55 | ok |
| yolo26-s_224x224.dxnn | 592.0 | 1.69 | 1.69 | N/A | 55 | ok |
| yolo26-m_224x224.dxnn | 445.2 | 2.25 | 2.25 | N/A | 55 | ok |
| yolo26-l_224x224.dxnn | 282.6 | 3.54 | 3.54 | N/A | 55 | ok |
| yolo26-x_224x224.dxnn | 168.1 | 5.95 | 5.95 | N/A | 55 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_224x224.dxnn | 1025.1 | 0.98 | 0.98 | N/A | 55 | ok |
| yolo26-s_224x224.dxnn | 583.9 | 1.71 | 1.71 | N/A | 55 | ok |
| yolo26-m_224x224.dxnn | 381.3 | 2.62 | 2.62 | N/A | 55 | ok |
| yolo26-l_224x224.dxnn | 290.6 | 3.44 | 3.44 | N/A | 55 | ok |
| yolo26-x_224x224.dxnn | 159.2 | 6.28 | 6.28 | N/A | 55 | ok |

## E2E Pipeline (Single-Stream)

### Object Detection

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | vaapidecodebin | 3455 | 3 | 478.1 ±0.8 | 7.23 | 228 | 22.0 | 81.8 | 52~53 | 1000 | 336 | ok |
| yolo26-s_640x640.dxnn | vaapidecodebin | 3455 | 3 | 475.7 ±2.1 | 7.26 | 228 | 38.0 | 81.5 | 61 | 1000 | 500 | ok |
| yolo26-m_640x640.dxnn | vaapidecodebin | 3455 | 3 | 476.6 ±0.4 | 7.25 | 224 | 66.8 | 94.0 | 66 | 1000 | 563 | ok |
| yolo26-l_640x640.dxnn | vaapidecodebin | 3455 | 3 | 367.3 ±1.9 | 9.41 | 163 | 78.3 | 100.0 | 65 | 1000 | 637 | ok |
| yolo26-x_640x640.dxnn | vaapidecodebin | 3455 | 3 | 200.1 ±1.5 | 17.26 | 78 | 83.9 | 100.0 | 67~69 | 1000 | 825 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | vaapidecodebin | 3455 | 3 | 421.5 ±0.7 | 8.20 | 246 | 18.5 | 76.3 | 59 | 1000 | 443 | ok |
| yolo26-s_640x640.dxnn | vaapidecodebin | 3455 | 3 | 425.0 ±3.0 | 8.13 | 245 | 34.9 | 74.5 | 60~61 | 1000 | 540 | ok |
| yolo26-m_640x640.dxnn | vaapidecodebin | 3455 | 3 | 424.9 ±1.5 | 8.13 | 244 | 59.0 | 85.5 | 65 | 1000 | 640 | ok |
| yolo26-l_640x640.dxnn | vaapidecodebin | 3455 | 3 | 367.7 ±3.2 | 9.40 | 211 | 76.6 | 100.0 | 65 | 1000 | 699 | ok |
| yolo26-x_640x640.dxnn | vaapidecodebin | 3455 | 3 | 200.4 ±0.7 | 17.24 | 102 | 82.0 | 100.0 | 67~69 | 1000 | 882 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n_640x640.dxnn | 478.1 | 421.5 | +56.7 | +13.4% |
| yolo26-s_640x640.dxnn | 475.7 | 425.0 | +50.7 | +11.9% |
| yolo26-m_640x640.dxnn | 476.6 | 424.9 | +51.7 | +12.2% |
| yolo26-l_640x640.dxnn | 367.3 | 367.7 | -0.4 | -0.1% |
| yolo26-x_640x640.dxnn | 200.1 | 200.4 | -0.3 | -0.1% |

### Pose Estimation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | vaapidecodebin | 3455 | 3 | 517.9 ±1.1 | 6.67 | 178 | 26.9 | 67.0 | 59 | 1000 | 367 | ok |
| yolo26-s-pose_640x640.dxnn | vaapidecodebin | 3455 | 3 | 516.8 ±3.8 | 6.68 | 177 | 47.0 | 81.5 | 61 | 1000 | 458 | ok |
| yolo26-m-pose_640x640.dxnn | vaapidecodebin | 3455 | 3 | 466.9 ±3.8 | 7.40 | 165 | 74.1 | 100.0 | 65~66 | 1000 | 563 | ok |
| yolo26-l-pose_640x640.dxnn | vaapidecodebin | 3455 | 3 | 352.9 ±1.8 | 9.79 | 114 | 78.3 | 100.0 | 65 | 1000 | 593 | ok |
| yolo26-x-pose_640x640.dxnn | vaapidecodebin | 3455 | 3 | 196.0 ±1.2 | 17.62 | 58 | 83.7 | 100.0 | 67~69 | 1000 | 781 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | vaapidecodebin | 3455 | 3 | 534.8 ±0.1 | 6.46 | 135 | 26.3 | 62.1 | 59 | 1000 | 310 | ok |
| yolo26-s-pose_640x640.dxnn | vaapidecodebin | 3455 | 3 | 536.3 ±0.9 | 6.44 | 135 | 50.4 | 78.5 | 60~61 | 1000 | 474 | ok |
| yolo26-m-pose_640x640.dxnn | vaapidecodebin | 3455 | 3 | 466.1 ±3.6 | 7.41 | 125 | 65.8 | 100.0 | 65~66 | 1000 | 582 | ok |
| yolo26-l-pose_640x640.dxnn | vaapidecodebin | 3455 | 3 | 352.6 ±1.7 | 9.80 | 89 | 78.4 | 100.0 | 65 | 1000 | 610 | ok |
| yolo26-x-pose_640x640.dxnn | vaapidecodebin | 3455 | 3 | 196.2 ±0.4 | 17.61 | 45 | 84.8 | 100.0 | 67~69 | 1000 | 801 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-pose_640x640.dxnn | 517.9 | 534.8 | -16.9 | -3.2% |
| yolo26-s-pose_640x640.dxnn | 516.8 | 536.3 | -19.5 | -3.6% |
| yolo26-m-pose_640x640.dxnn | 466.9 | 466.1 | +0.8 | +0.2% |
| yolo26-l-pose_640x640.dxnn | 352.9 | 352.6 | +0.3 | +0.1% |
| yolo26-x-pose_640x640.dxnn | 196.0 | 196.2 | -0.1 | -0.1% |

### Segmentation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | vaapidecodebin | 3455 | 3 | 344.7 ±1.0 | 10.02 | 533 | 20.9 | 77.9 | 57 | 1000 | 747 | ok |
| yolo26-s-seg_640x640.dxnn | vaapidecodebin | 3455 | 3 | 344.7 ±0.7 | 10.02 | 535 | 38.7 | 77.8 | 62 | 1000 | 830 | ok |
| yolo26-m-seg_640x640.dxnn | vaapidecodebin | 3455 | 3 | 315.9 ±2.2 | 10.94 | 442 | 79.3 | 100.0 | 68~69 | 1000 | 912 | ok |
| yolo26-l-seg_640x640.dxnn | vaapidecodebin | 3455 | 3 | 263.0 ±1.3 | 13.14 | 316 | 79.2 | 100.0 | 67~68 | 1000 | 941 | ok |
| yolo26-x-seg_640x640.dxnn | vaapidecodebin | 3455 | 3 | 139.7 ±0.5 | 24.73 | 152 | 87.6 | 100.0 | 70~73 | 1000 | 1153 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | vaapidecodebin | 3455 | 3 | 297.9 ±0.4 | 11.60 | 418 | 17.7 | 66.8 | 57 | 1000 | 735 | ok |
| yolo26-s-seg_640x640.dxnn | vaapidecodebin | 3455 | 3 | 293.0 ±0.5 | 11.79 | 403 | 33.6 | 67.3 | 62 | 1000 | 812 | ok |
| yolo26-m-seg_640x640.dxnn | vaapidecodebin | 3455 | 3 | 296.4 ±2.1 | 11.65 | 404 | 71.7 | 93.9 | 68~69 | 1000 | 1003 | ok |
| yolo26-l-seg_640x640.dxnn | vaapidecodebin | 3455 | 3 | 262.2 ±1.8 | 13.18 | 345 | 79.8 | 100.0 | 67~68 | 1000 | 1026 | ok |
| yolo26-x-seg_640x640.dxnn | vaapidecodebin | 3455 | 3 | 140.6 ±0.7 | 24.58 | 166 | 87.3 | 100.0 | 70~72 | 1000 | 1234 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-seg_640x640.dxnn | 344.7 | 297.9 | +46.8 | +15.7% |
| yolo26-s-seg_640x640.dxnn | 344.7 | 293.0 | +51.6 | +17.6% |
| yolo26-m-seg_640x640.dxnn | 315.9 | 296.4 | +19.4 | +6.6% |
| yolo26-l-seg_640x640.dxnn | 263.0 | 262.2 | +0.8 | +0.3% |
| yolo26-x-seg_640x640.dxnn | 139.7 | 140.6 | -0.8 | -0.6% |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | vaapidecodebin | 2640 | 3 | 364.7 ±2.0 | 7.24 | 154 | 55.5 | 83.7 | 59 | 1000 | 531 | ok |
| yolo26-s-obb_1024x1024.dxnn | vaapidecodebin | 2640 | 3 | 261.7 ±1.4 | 10.09 | 116 | 78.3 | 100.0 | 61~62 | 1000 | 610 | ok |
| yolo26-m-obb_1024x1024.dxnn | vaapidecodebin | 2640 | 3 | 174.0 ±1.2 | 15.17 | 73 | 83.3 | 100.0 | 66~68 | 1000 | 678 | ok |
| yolo26-l-obb_1024x1024.dxnn | vaapidecodebin | 2640 | 3 | 129.1 ±0.4 | 20.45 | 53 | 86.8 | 100.0 | 66~68 | 1000 | 717 | ok |
| yolo26-x-obb_1024x1024.dxnn | vaapidecodebin | 2640 | 3 | 70.8 ±0.4 | 37.31 | 29 | 90.9 | 100.0 | 69~72 | 1000 | 922 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | vaapidecodebin | 2640 | 3 | 367.1 ±4.2 | 7.19 | 160 | 54.9 | 83.8 | 59 | 1000 | 519 | ok |
| yolo26-s-obb_1024x1024.dxnn | vaapidecodebin | 2640 | 3 | 262.0 ±5.5 | 10.08 | 123 | 75.9 | 100.0 | 62 | 1000 | 628 | ok |
| yolo26-m-obb_1024x1024.dxnn | vaapidecodebin | 2640 | 3 | 173.6 ±1.6 | 15.21 | 77 | 83.6 | 100.0 | 66~67 | 1000 | 700 | ok |
| yolo26-l-obb_1024x1024.dxnn | vaapidecodebin | 2640 | 3 | 129.2 ±1.0 | 20.44 | 56 | 86.5 | 100.0 | 66~68 | 1000 | 731 | ok |
| yolo26-x-obb_1024x1024.dxnn | vaapidecodebin | 2640 | 3 | 70.8 ±0.3 | 37.29 | 30 | 91.1 | 100.0 | 69~72 | 1000 | 940 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-obb_1024x1024.dxnn | 364.7 | 367.1 | -2.4 | -0.6% |
| yolo26-s-obb_1024x1024.dxnn | 261.7 | 262.0 | -0.2 | -0.1% |
| yolo26-m-obb_1024x1024.dxnn | 174.0 | 173.6 | +0.4 | +0.2% |
| yolo26-l-obb_1024x1024.dxnn | 129.1 | 129.2 | -0.1 | -0.0% |
| yolo26-x-obb_1024x1024.dxnn | 70.8 | 70.8 | -0.0 | -0.1% |

### Classification

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_224x224.dxnn | vaapidecodebin | 3455 | 3 | 747.7 ±9.9 | 4.62 | 46 | 3.0 | 14.4 | 56 | 1000 | 198 | ok |
| yolo26-s_224x224.dxnn | vaapidecodebin | 3455 | 3 | 720.2 ±15.9 | 4.80 | 47 | 6.1 | 26.0 | 57~58 | 1000 | 259 | ok |
| yolo26-m_224x224.dxnn | vaapidecodebin | 3455 | 3 | 734.1 ±16.5 | 4.71 | 47 | 8.1 | 37.1 | 61 | 1000 | 288 | ok |
| yolo26-l_224x224.dxnn | vaapidecodebin | 3455 | 3 | 731.1 ±17.2 | 4.73 | 46 | 12.6 | 59.3 | 59~60 | 1000 | 304 | ok |
| yolo26-x_224x224.dxnn | vaapidecodebin | 3455 | 3 | 710.6 ±5.7 | 4.86 | 49 | 23.1 | 69.3 | 61 | 1000 | 395 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_224x224.dxnn | vaapidecodebin | 3455 | 3 | 726.1 ±11.7 | 4.76 | 46 | 3.0 | 14.4 | 56 | 1000 | 240 | ok |
| yolo26-s_224x224.dxnn | vaapidecodebin | 3455 | 3 | 734.3 ±23.4 | 4.71 | 46 | 5.9 | 25.9 | 57~58 | 1000 | 259 | ok |
| yolo26-m_224x224.dxnn | vaapidecodebin | 3455 | 3 | 717.4 ±6.3 | 4.82 | 48 | 8.2 | 36.9 | 61 | 1000 | 287 | ok |
| yolo26-l_224x224.dxnn | vaapidecodebin | 3455 | 3 | 733.1 ±6.3 | 4.71 | 47 | 12.7 | 59.0 | 59~60 | 1000 | 303 | ok |
| yolo26-x_224x224.dxnn | vaapidecodebin | 3455 | 3 | 719.2 ±2.1 | 4.80 | 48 | 20.8 | 68.4 | 61 | 1000 | 395 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n_224x224.dxnn | 747.7 | 726.1 | +21.6 | +3.0% |
| yolo26-s_224x224.dxnn | 720.2 | 734.3 | -14.1 | -1.9% |
| yolo26-m_224x224.dxnn | 734.1 | 717.4 | +16.6 | +2.3% |
| yolo26-l_224x224.dxnn | 731.1 | 733.1 | -2.0 | -0.3% |
| yolo26-x_224x224.dxnn | 710.6 | 719.2 | -8.6 | -1.2% |

## E2E Pipeline (Multi-Stream)

### Object Detection

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | 15 | 3 | 513.6 ±0.7 | 34.2 | 313 | 30.1 | 84.0 | 54~56 | 1000 | 695 | ok |
| yolo26-n_640x640.dxnn | 16 | 3 | 512.4 ±0.8 | 32.0 | 313 | 30.3 | 84.1 | 57~58 | 1000 | 703 | ok |
| yolo26-n_640x640.dxnn | 17 | 3 | 513.5 ±1.0 | 30.2 | 313 | 30.4 | 83.3 | 57~58 | 1000 | 694 | ok |
| yolo26-n_640x640.dxnn | 18 | 3 | 512.1 ±0.1 | 28.4 | 313 | 30.3 | 83.2 | 58 | 1000 | 751 | ok |
| yolo26-s_640x640.dxnn | 15 | 3 | 511.6 ±0.8 | 34.1 | 317 | 57.0 | 86.7 | 62~64 | 1000 | 789 | ok |
| yolo26-s_640x640.dxnn | 16 | 3 | 511.9 ±1.8 | 32.0 | 316 | 57.3 | 86.5 | 56~61 | 1000 | 796 | ok |
| yolo26-s_640x640.dxnn | 17 | 3 | 510.1 ±1.0 | 30.0 | 315 | 57.2 | 86.5 | 62~64 | 1000 | 833 | ok |
| yolo26-s_640x640.dxnn | 18 | 3 | 510.6 ±1.4 | 28.4 | 315 | 57.7 | 86.6 | 65 | 1000 | 846 | ok |
| yolo26-m_640x640.dxnn | 15 | 3 | 489.3 ±0.4 | 32.6 | 305 | 94.6 | 100.0 | 62~74 | 1000 | 854 | ok |
| yolo26-m_640x640.dxnn | 16 | 3 | 482.7 ±4.9 | 30.2 | 299 | 94.2 | 100.0 | 80~82 | 800~1000 | 875 | ok |
| yolo26-m_640x640.dxnn | 17 | 3 | 463.0 ±1.1 | 27.2 | 283 | 93.2 | 100.0 | 83 | 600~1000 | 899 | ok |
| yolo26-l_640x640.dxnn | 12 | 3 | 366.3 ±0.5 | 30.5 | 187 | 95.3 | 100.0 | 75~79 | 1000 | 855 | ok |
| yolo26-l_640x640.dxnn | 13 | 3 | 361.8 ±4.0 | 27.8 | 186 | 94.8 | 100.0 | 81~82 | 800~1000 | 878 | ok |
| yolo26-x_640x640.dxnn | 6 | 3 | 197.4 ±2.8 | 32.9 | 85 | 95.2 | 100.0 | 78~81 | 800~1000 | 922 | ok |
| yolo26-x_640x640.dxnn | 7 | 3 | 186.8 ±0.6 | 26.7 | 81 | 94.4 | 100.0 | 83 | 800~1000 | 934 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | 14 | 3 | 415.5 ±1.3 | 29.7 | 256 | 24.0 | 76.3 | 57~58 | 1000 | 756 | ok |
| yolo26-n_640x640.dxnn | 13 | 3 | 415.5 ±0.7 | 32.0 | 257 | 23.9 | 75.7 | 57 | 1000 | 716 | ok |
| yolo26-s_640x640.dxnn | 14 | 2/3 | 416.7 ±0.1 | 29.8 | 256 | 45.4 | 73.1 | 61~62 | 1000 | 835 | partial — 2/3 runs after backfill exhausted (1 timeout, 2 unparsable over 5 attempts) |
| yolo26-s_640x640.dxnn | 13 | 3 | 416.7 ±1.6 | 32.0 | 255 | 45.0 | 73.2 | 58~60 | 1000 | 807 | ok |
| yolo26-m_640x640.dxnn | 14 | 3 | 412.4 ±1.0 | 29.4 | 257 | 77.9 | 86.6 | 73~76 | 1000 | 953 | ok |
| yolo26-m_640x640.dxnn | 13 | 3 | 414.3 ±2.6 | 31.9 | 257 | 78.0 | 86.9 | 61~79 | 1000 | 933 | ok |
| yolo26-l_640x640.dxnn | 12 | 3 | 368.2 ±0.1 | 30.7 | 239 | 96.0 | 100.0 | 75~79 | 1000 | 927 | ok |
| yolo26-l_640x640.dxnn | 13 | 3 | 362.8 ±1.7 | 27.9 | 237 | 95.3 | 100.0 | 82 | 800~1000 | 952 | ok |
| yolo26-x_640x640.dxnn | 6 | 3 | 198.5 ±3.3 | 33.1 | 113 | 95.3 | 100.0 | 78~81 | 800~1000 | 1006 | ok |
| yolo26-x_640x640.dxnn | 7 | 3 | 186.6 ±1.3 | 26.7 | 106 | 94.1 | 100.0 | 83 | 600~1000 | 1020 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n_640x640.dxnn | 17 | 30.2 | 13 | 32.0 |
| yolo26-s_640x640.dxnn | 17 | 30.0 | 13 | 32.0 |
| yolo26-m_640x640.dxnn | 16 | 30.2 | 13 | 31.9 |
| yolo26-l_640x640.dxnn | 12 | 30.5 | 12 | 30.7 |
| yolo26-x_640x640.dxnn | 6 | 32.9 | 6 | 33.1 |

### Pose Estimation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 17 | 3 | 566.2 ±1.3 | 33.3 | 242 | 36.9 | 75.2 | 59 | 1000 | 716 | ok |
| yolo26-n-pose_640x640.dxnn | 18 | 3 | 564.4 ±1.6 | 31.4 | 243 | 36.9 | 75.9 | 59 | 1000 | 738 | ok |
| yolo26-n-pose_640x640.dxnn | 19 | 2/3 | 567.0 ±0.4 | 29.8 | 242 | 36.9 | 78.8 | 59 | 1000 | 761 | partial — 2/3 runs after backfill exhausted (0 timeout, 3 unparsable over 5 attempts) |
| yolo26-s-pose_640x640.dxnn | 17 | 2/3 | 564.4 ±1.8 | 33.2 | 246 | 70.7 | 85.7 | 65 | 1000 | 792 | partial — 2/3 runs after backfill exhausted (0 timeout, 3 unparsable over 5 attempts) |
| yolo26-s-pose_640x640.dxnn | 16 | 3 | 564.0 ±1.1 | 35.2 | 247 | 70.5 | 85.6 | 67 | 1000 | 777 | ok |
| yolo26-m-pose_640x640.dxnn | 15 | 3 | 464.1 ±1.6 | 30.9 | 194 | 95.4 | 100.0 | 76~80 | 800~1000 | 821 | ok |
| yolo26-m-pose_640x640.dxnn | 16 | 3 | 447.6 ±4.4 | 28.0 | 184 | 93.5 | 100.0 | 83 | 800~1000 | 845 | ok |
| yolo26-l-pose_640x640.dxnn | 11 | 3 | 351.8 ±0.3 | 32.0 | 130 | 95.1 | 100.0 | 74~79 | 1000 | 803 | ok |
| yolo26-l-pose_640x640.dxnn | 12 | 3 | 346.8 ±1.7 | 28.9 | 130 | 95.3 | 100.0 | 81~82 | 800~1000 | 817 | ok |
| yolo26-x-pose_640x640.dxnn | 6 | 3 | 192.7 ±2.6 | 32.1 | 64 | 95.4 | 100.0 | 78~81 | 800~1000 | 886 | ok |
| yolo26-x-pose_640x640.dxnn | 7 | 3 | 183.9 ±2.0 | 26.3 | 62 | 94.7 | 100.0 | 83 | 600~1000 | 902 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 17 | 3 | 588.8 ±0.3 | 34.6 | 192 | 38.6 | 72.6 | 59 | 1000 | 737 | ok |
| yolo26-n-pose_640x640.dxnn | 18 | 3 | 588.4 ±0.8 | 32.7 | 192 | 38.4 | 74.0 | 59 | 1000 | 778 | ok |
| yolo26-n-pose_640x640.dxnn | 19 | 3 | 589.8 ±1.5 | 31.0 | 192 | 38.8 | 74.0 | 60 | 1000 | 799 | ok |
| yolo26-n-pose_640x640.dxnn | 20 | 3 | 589.0 ±0.6 | 29.4 | 192 | 38.5 | 74.5 | 60 | 1000 | 797 | ok |
| yolo26-s-pose_640x640.dxnn | 17 | 3 | 585.1 ±1.0 | 34.4 | 193 | 73.0 | 88.4 | 64~66 | 1000 | 825 | ok |
| yolo26-s-pose_640x640.dxnn | 18 | 3 | 585.0 ±1.4 | 32.5 | 194 | 73.0 | 89.1 | 67~68 | 1000 | 848 | ok |
| yolo26-s-pose_640x640.dxnn | 19 | 3 | 584.9 ±1.5 | 30.8 | 194 | 73.3 | 88.5 | 68 | 1000 | 867 | ok |
| yolo26-s-pose_640x640.dxnn | 20 | 3 | 583.5 ±2.0 | 29.2 | 195 | 72.9 | 88.6 | 68 | 1000 | 895 | ok |
| yolo26-m-pose_640x640.dxnn | 15 | 3 | 463.8 ±1.3 | 30.9 | 151 | 95.3 | 100.0 | 76~80 | 800~1000 | 849 | ok |
| yolo26-m-pose_640x640.dxnn | 16 | 3 | 448.1 ±2.5 | 28.0 | 144 | 94.5 | 100.0 | 82~83 | 800~1000 | 875 | ok |
| yolo26-l-pose_640x640.dxnn | 11 | 3 | 352.2 ±1.0 | 32.0 | 104 | 95.7 | 100.0 | 74~78 | 1000 | 813 | ok |
| yolo26-l-pose_640x640.dxnn | 12 | 3 | 347.4 ±1.9 | 28.9 | 103 | 95.4 | 100.0 | 81 | 800~1000 | 850 | ok |
| yolo26-x-pose_640x640.dxnn | 6 | 3 | 193.3 ±1.9 | 32.2 | 51 | 95.2 | 100.0 | 77~81 | 800~1000 | 911 | ok |
| yolo26-x-pose_640x640.dxnn | 7 | 3 | 184.7 ±0.9 | 26.4 | 49 | 94.8 | 100.0 | 83 | 800~1000 | 921 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-pose_640x640.dxnn | 18 | 31.4 | 19 | 31.0 |
| yolo26-s-pose_640x640.dxnn | 16 | 35.2 | 19 | 30.8 |
| yolo26-m-pose_640x640.dxnn | 15 | 30.9 | 15 | 30.9 |
| yolo26-l-pose_640x640.dxnn | 11 | 32.0 | 11 | 32.0 |
| yolo26-x-pose_640x640.dxnn | 6 | 32.1 | 6 | 32.2 |

### Segmentation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 11 | 3 | 351.4 ±0.7 | 31.9 | 615 | 25.8 | 77.4 | 57~58 | 1000 | 1032 | ok |
| yolo26-n-seg_640x640.dxnn | 12 | 3 | 351.1 ±0.1 | 29.3 | 617 | 25.9 | 76.6 | 59 | 1000 | 1062 | ok |
| yolo26-s-seg_640x640.dxnn | 11 | 3 | 347.3 ±2.7 | 31.6 | 606 | 50.7 | 78.4 | 64~66 | 1000 | 1085 | ok |
| yolo26-s-seg_640x640.dxnn | 12 | 3 | 348.7 ±0.7 | 29.1 | 612 | 50.8 | 79.6 | 66~67 | 1000 | 1113 | ok |
| yolo26-m-seg_640x640.dxnn | 10 | 3 | 298.8 ±12.0 | 29.9 | 439 | 90.1 | 100.0 | 80~83 | 600~1000 | 1122 | ok |
| yolo26-m-seg_640x640.dxnn | 9 | 3 | 271.6 ±0.3 | 30.2 | 367 | 89.4 | 100.0 | 84 | 600~1000 | 1123 | ok |
| yolo26-l-seg_640x640.dxnn | 8 | 3 | 256.1 ±6.7 | 32.0 | 332 | 93.7 | 100.0 | 79~82 | 800~1000 | 1120 | ok |
| yolo26-l-seg_640x640.dxnn | 9 | 3 | 232.2 ±4.5 | 25.8 | 294 | 90.0 | 100.0 | 83~84 | 400~1000 | 1149 | ok |
| yolo26-x-seg_640x640.dxnn | 4 | 3 | 127.7 ±6.6 | 31.9 | 143 | 91.2 | 100.0 | 81~83 | 600~1000 | 1233 | ok |
| yolo26-x-seg_640x640.dxnn | 5 | 3 | 117.5 ±3.6 | 23.5 | 129 | 89.7 | 100.0 | 83 | 600~1000 | 1257 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 9 | 3 | 293.5 ±0.8 | 32.6 | 425 | 21.1 | 69.5 | 57 | 1000 | 968 | ok |
| yolo26-n-seg_640x640.dxnn | 10 | 3 | 294.3 ±0.3 | 29.4 | 424 | 21.2 | 69.5 | 57 | 1000 | 1012 | ok |
| yolo26-s-seg_640x640.dxnn | 9 | 3 | 288.9 ±0.4 | 32.1 | 414 | 40.8 | 70.0 | 63 | 1000 | 1090 | ok |
| yolo26-s-seg_640x640.dxnn | 10 | 3 | 288.2 ±0.3 | 28.8 | 414 | 41.1 | 70.2 | 64 | 1000 | 1115 | ok |
| yolo26-m-seg_640x640.dxnn | 9 | 3 | 291.4 ±1.4 | 32.4 | 419 | 83.5 | 100.0 | 74~80 | 800~1000 | 1218 | ok |
| yolo26-m-seg_640x640.dxnn | 10 | 3 | 276.9 ±3.1 | 27.7 | 404 | 88.2 | 100.0 | 83~84 | 600~1000 | 1253 | ok |
| yolo26-l-seg_640x640.dxnn | 8 | 3 | 257.3 ±6.0 | 32.2 | 363 | 93.7 | 100.0 | 78~83 | 600~1000 | 1213 | ok |
| yolo26-l-seg_640x640.dxnn | 9 | 3 | 234.9 ±3.2 | 26.1 | 322 | 91.3 | 100.0 | 84 | 600~1000 | 1249 | ok |
| yolo26-x-seg_640x640.dxnn | 4 | 3 | 128.4 ±5.2 | 32.1 | 158 | 91.7 | 100.0 | 81~83 | 600~1000 | 1332 | ok |
| yolo26-x-seg_640x640.dxnn | 5 | 3 | 116.5 ±0.4 | 23.3 | 140 | 89.5 | 100.0 | 83 | 600~1000 | 1359 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-seg_640x640.dxnn | 11 | 31.9 | 9 | 32.6 |
| yolo26-s-seg_640x640.dxnn | 11 | 31.6 | 9 | 32.1 |
| yolo26-m-seg_640x640.dxnn | 9 | 30.2 | 9 | 32.4 |
| yolo26-l-seg_640x640.dxnn | 8 | 32.0 | 8 | 32.2 |
| yolo26-x-seg_640x640.dxnn | 4 | 31.9 | 4 | 32.1 |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 12 | 3 | 405.4 ±1.8 | 33.8 | 213 | 83.6 | 95.7 | 62~64 | 1000 | 815 | ok |
| yolo26-n-obb_1024x1024.dxnn | 13 | 3 | 404.6 ±0.5 | 31.1 | 213 | 84.5 | 97.6 | 66~67 | 1000 | 847 | ok |
| yolo26-n-obb_1024x1024.dxnn | 14 | 3 | 402.6 ±0.6 | 28.8 | 213 | 83.9 | 97.3 | 68 | 1000 | 838 | ok |
| yolo26-s-obb_1024x1024.dxnn | 8 | 3 | 258.8 ±0.6 | 32.4 | 129 | 94.1 | 100.0 | 59~65 | 1000 | 775 | ok |
| yolo26-s-obb_1024x1024.dxnn | 9 | 3 | 259.3 ±0.3 | 28.8 | 129 | 93.8 | 100.0 | 69~71 | 1000 | 805 | ok |
| yolo26-m-obb_1024x1024.dxnn | 5 | 3 | 173.1 ±0.8 | 34.6 | 80 | 95.6 | 100.0 | 74~78 | 1000 | 779 | ok |
| yolo26-m-obb_1024x1024.dxnn | 6 | 3 | 171.1 ±1.1 | 28.5 | 80 | 95.2 | 100.0 | 80~82 | 800~1000 | 798 | ok |
| yolo26-l-obb_1024x1024.dxnn | 4 | 3 | 127.5 ±0.3 | 31.9 | 57 | 94.3 | 100.0 | 74~77 | 1000 | 784 | ok |
| yolo26-l-obb_1024x1024.dxnn | 5 | 3 | 127.7 ±0.2 | 25.6 | 57 | 95.3 | 100.0 | 79~81 | 800~1000 | 811 | ok |
| yolo26-x-obb_1024x1024.dxnn | 2 | 3 | 70.5 ±0.6 | 35.2 | 30 | 94.1 | 100.0 | 77~80 | 800~1000 | 946 | ok |
| yolo26-x-obb_1024x1024.dxnn | 3 | 3 | 66.8 ±0.3 | 22.3 | 30 | 92.6 | 100.0 | 82 | 600~1000 | 977 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 12 | 3 | 406.3 ±1.2 | 33.9 | 219 | 85.1 | 96.2 | 63~65 | 1000 | 841 | ok |
| yolo26-n-obb_1024x1024.dxnn | 13 | 3 | 405.4 ±1.1 | 31.2 | 219 | 84.5 | 96.6 | 57~67 | 1000 | 874 | ok |
| yolo26-n-obb_1024x1024.dxnn | 14 | 3 | 402.9 ±0.2 | 28.8 | 219 | 83.9 | 97.6 | 56~64 | 1000 | 864 | ok |
| yolo26-s-obb_1024x1024.dxnn | 8 | 3 | 259.4 ±0.3 | 32.4 | 135 | 93.9 | 100.0 | 67~70 | 1000 | 796 | ok |
| yolo26-s-obb_1024x1024.dxnn | 9 | 3 | 259.3 ±0.1 | 28.8 | 135 | 94.0 | 100.0 | 71~72 | 1000 | 828 | ok |
| yolo26-m-obb_1024x1024.dxnn | 5 | 3 | 173.0 ±0.6 | 34.6 | 84 | 94.8 | 100.0 | 73~77 | 1000 | 801 | ok |
| yolo26-m-obb_1024x1024.dxnn | 6 | 3 | 170.7 ±1.1 | 28.4 | 84 | 94.8 | 100.0 | 80~81 | 800~1000 | 822 | ok |
| yolo26-l-obb_1024x1024.dxnn | 4 | 3 | 128.2 ±0.3 | 32.0 | 60 | 94.8 | 100.0 | 74~77 | 1000 | 799 | ok |
| yolo26-l-obb_1024x1024.dxnn | 5 | 3 | 128.1 ±0.5 | 25.6 | 60 | 95.0 | 100.0 | 80 | 800~1000 | 830 | ok |
| yolo26-x-obb_1024x1024.dxnn | 2 | 3 | 70.6 ±0.1 | 35.3 | 32 | 94.7 | 100.0 | 77~80 | 1000 | 961 | ok |
| yolo26-x-obb_1024x1024.dxnn | 3 | 3 | 67.0 ±0.8 | 22.3 | 31 | 92.5 | 100.0 | 82 | 600~1000 | 992 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-obb_1024x1024.dxnn | 13 | 31.1 | 13 | 31.2 |
| yolo26-s-obb_1024x1024.dxnn | 8 | 32.4 | 8 | 32.4 |
| yolo26-m-obb_1024x1024.dxnn | 5 | 34.6 | 5 | 34.6 |
| yolo26-l-obb_1024x1024.dxnn | 4 | 31.9 | 4 | 32.0 |
| yolo26-x-obb_1024x1024.dxnn | 2 | 35.2 | 2 | 35.3 |

---
*Report generated by dx-benchmark tool*
