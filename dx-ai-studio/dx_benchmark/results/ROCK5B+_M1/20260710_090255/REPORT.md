# YOLO26 Benchmark Report

**Generated:** 2026-07-11 06:39:57 (Local)

## Test Timing

| # | Type | Start | End | Duration |
|---|------|-------|-----|----------|
| 1 | run | 2026-07-10 09:02:55 | 2026-07-11 06:39:57 | 21h 37m 2s |

## Executive Summary

### Object Detection

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n_640x640.dxnn | ON | 23.87 | 157.2 | 140.6 | 4 |
| yolo26-n_640x640.dxnn | OFF | 36.17 | 264.7 | 95.4 | 3 |
| yolo26-s_640x640.dxnn | ON | 46.34 | 151.4 | 132.6 | 4 |
| yolo26-s_640x640.dxnn | OFF | 43.31 | 194.9 | 95.1 | 3 |
| yolo26-m_640x640.dxnn | ON | 55.87 | 119.5 | 94.9 | 2 |
| yolo26-m_640x640.dxnn | OFF | 49.47 | 116.2 | 94.8 | 2 |
| yolo26-l_640x640.dxnn | ON | 60.01 | 87.5 | 74.6 | 1 |
| yolo26-l_640x640.dxnn | OFF | 58.77 | 86.6 | 76.2 | 2 |
| yolo26-x_640x640.dxnn | ON | 94.21 | 47.9 | 33.3 | 1 |
| yolo26-x_640x640.dxnn | OFF | 91.68 | 47.3 | 33.5 | 1 |

### Pose Estimation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-pose_640x640.dxnn | ON | 25.12 | 235.2 | 190.7 | 6 |
| yolo26-n-pose_640x640.dxnn | OFF | 28.25 | 282.5 | 234.0 | 7 |
| yolo26-s-pose_640x640.dxnn | ON | 37.88 | 181.8 | 161.6 | 5 |
| yolo26-s-pose_640x640.dxnn | OFF | 32.33 | 176.9 | 176.0 | 5 |
| yolo26-m-pose_640x640.dxnn | ON | 44.46 | 111.9 | 97.1 | 2 |
| yolo26-m-pose_640x640.dxnn | OFF | 41.21 | 112.7 | 98.6 | 2 |
| yolo26-l-pose_640x640.dxnn | ON | 54.73 | 83.6 | 74.6 | 2 |
| yolo26-l-pose_640x640.dxnn | OFF | 50.17 | 83.1 | 75.7 | 2 |
| yolo26-x-pose_640x640.dxnn | ON | 83.11 | 46.2 | 32.7 | 1 |
| yolo26-x-pose_640x640.dxnn | OFF | 79.72 | 46.2 | 33.6 | 1 |

### Segmentation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-seg_640x640.dxnn | ON | 32.83 | 101.1 | 85.9 | 2 |
| yolo26-n-seg_640x640.dxnn | OFF | 30.70 | 152.1 | 78.6 | 2 |
| yolo26-s-seg_640x640.dxnn | ON | 45.47 | 104.9 | 78.2 | 2 |
| yolo26-s-seg_640x640.dxnn | OFF | 45.16 | 127.1 | 75.5 | 2 |
| yolo26-m-seg_640x640.dxnn | ON | 64.23 | 74.7 | 48.1 | 1 |
| yolo26-m-seg_640x640.dxnn | OFF | 54.71 | 74.9 | 48.7 | 1 |
| yolo26-l-seg_640x640.dxnn | ON | 81.19 | 62.3 | 41.1 | 1 |
| yolo26-l-seg_640x640.dxnn | OFF | 65.71 | 62.2 | 41.2 | 1 |
| yolo26-x-seg_640x640.dxnn | ON | 116.93 | 31.3 | 18.8 | — |
| yolo26-x-seg_640x640.dxnn | OFF | 111.40 | 31.0 | 18.6 | — |

### Oriented BBox (OBB)

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-obb_1024x1024.dxnn | ON | 44.47 | 100.5 | 101.9 | 3 |
| yolo26-n-obb_1024x1024.dxnn | OFF | 43.70 | 98.0 | 100.2 | 3 |
| yolo26-s-obb_1024x1024.dxnn | ON | 63.84 | 61.6 | 61.5 | 2 |
| yolo26-s-obb_1024x1024.dxnn | OFF | 63.26 | 60.9 | 61.0 | 2 |
| yolo26-m-obb_1024x1024.dxnn | ON | 85.89 | 40.7 | 29.4 | — |
| yolo26-m-obb_1024x1024.dxnn | OFF | 78.28 | 39.7 | 30.1 | 1 |
| yolo26-l-obb_1024x1024.dxnn | ON | 103.49 | 30.3 | 22.5 | — |
| yolo26-l-obb_1024x1024.dxnn | OFF | 102.82 | 29.6 | 22.3 | — |
| yolo26-x-obb_1024x1024.dxnn | ON | 178.91 | 16.3 | 10.5 | — |
| yolo26-x-obb_1024x1024.dxnn | OFF | 175.58 | 16.2 | 10.4 | — |

### Classification

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n_224x224.dxnn | ON | 1.47 | 3588.7 | 974.6 | — |
| yolo26-n_224x224.dxnn | OFF | 2.63 | 3580.6 | 975.3 | — |
| yolo26-s_224x224.dxnn | ON | 2.11 | 2002.0 | 952.1 | — |
| yolo26-s_224x224.dxnn | OFF | 2.16 | 2000.7 | 969.0 | — |
| yolo26-m_224x224.dxnn | ON | 2.93 | 1380.3 | 956.5 | — |
| yolo26-m_224x224.dxnn | OFF | 3.02 | 1379.4 | 963.9 | — |
| yolo26-l_224x224.dxnn | ON | 4.05 | 875.6 | 848.2 | — |
| yolo26-l_224x224.dxnn | OFF | 4.00 | 876.0 | 847.0 | — |
| yolo26-x_224x224.dxnn | ON | 8.64 | 483.8 | 479.3 | — |
| yolo26-x_224x224.dxnn | OFF | 8.34 | 484.7 | 479.3 | — |

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
| NPU RT | v3.4.0 |
| NPU Driver (RT) | v2.5.1 |
| NPU Driver (PCIe) | v2.4.1 |
| NPU Firmware | v2.7.1 |
| NPU Memory | LPDDR5 5600 Mbps, 3.92GiB |
| NPU Board | M.2, Rev 1.0 |
| NPU PCIe | Gen3 X2 [01:00:00] |

### Tools

| Tool | Available | Version |
|------|-----------|---------|
| run_model | Yes | DXRT v3.4.0 run_model |
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
| yolo26-n_640x640.dxnn | 157.2 ±3.2 | 183 | 37.2 | 63.9 | 52~55 | 1000 | ok |
| yolo26-s_640x640.dxnn | 151.4 ±6.5 | 183 | 70.8 | 83.4 | 65~68 | 1000 | ok |
| yolo26-m_640x640.dxnn | 119.5 ±0.6 | 146 | 91.1 | 100.0 | 74~79 | 1000 | ok |
| yolo26-l_640x640.dxnn | 87.5 ±1.0 | 112 | 89.4 | 100.0 | 72~77 | 1000 | ok |
| yolo26-x_640x640.dxnn | 47.9 ±1.6 | 70 | 88.7 | 100.0 | 74~78 | 800~1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n_640x640.dxnn | 264.7 ±2.1 | 141 | 73.2 | 87.9 | 63~66 | 1000 | ok |
| yolo26-s_640x640.dxnn | 194.9 ±1.8 | 102 | 91.8 | 100.0 | 67~71 | 1000 | ok |
| yolo26-m_640x640.dxnn | 116.2 ±0.4 | 78 | 88.7 | 100.0 | 73~78 | 1000 | ok |
| yolo26-l_640x640.dxnn | 86.6 ±1.4 | 67 | 89.0 | 100.0 | 72~77 | 1000 | ok |
| yolo26-x_640x640.dxnn | 47.3 ±1.9 | 45 | 88.6 | 100.0 | 74~78 | 800~1000 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 235.2 ±6.8 | 195 | 68.6 | 84.1 | 63~65 | 1000 | ok |
| yolo26-s-pose_640x640.dxnn | 181.8 ±1.1 | 152 | 91.9 | 100.0 | 67~70 | 1000 | ok |
| yolo26-m-pose_640x640.dxnn | 111.9 ±0.5 | 99 | 92.4 | 100.0 | 72~77 | 1000 | ok |
| yolo26-l-pose_640x640.dxnn | 83.6 ±1.8 | 83 | 90.4 | 100.0 | 71~76 | 1000 | ok |
| yolo26-x-pose_640x640.dxnn | 46.2 ±1.4 | 70 | 88.8 | 100.0 | 74~78 | 800~1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 282.5 ±1.4 | 108 | 88.8 | 99.1 | 64~67 | 1000 | ok |
| yolo26-s-pose_640x640.dxnn | 176.9 ±1.5 | 89 | 90.0 | 100.0 | 67~70 | 1000 | ok |
| yolo26-m-pose_640x640.dxnn | 112.7 ±1.1 | 70 | 89.0 | 100.0 | 73~77 | 1000 | ok |
| yolo26-l-pose_640x640.dxnn | 83.1 ±1.1 | 65 | 89.8 | 100.0 | 72~76 | 1000 | ok |
| yolo26-x-pose_640x640.dxnn | 46.2 ±1.9 | 46 | 89.7 | 100.0 | 74~78 | 800~1000 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 101.1 ±4.6 | 248 | 28.2 | 86.7 | 59~61 | 1000 | ok |
| yolo26-s-seg_640x640.dxnn | 104.9 ±1.2 | 239 | 61.0 | 88.1 | 66~69 | 1000 | ok |
| yolo26-m-seg_640x640.dxnn | 74.7 ±4.0 | 154 | 88.5 | 100.0 | 76~80 | 800~1000 | ok |
| yolo26-l-seg_640x640.dxnn | 62.3 ±2.4 | 131 | 89.2 | 100.0 | 75~79 | 800~1000 | ok |
| yolo26-x-seg_640x640.dxnn | 31.3 ±1.2 | 70 | 88.3 | 100.0 | 76~80 | 800~1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 152.1 ±10.8 | 198 | 48.9 | 85.2 | 61~64 | 1000 | ok |
| yolo26-s-seg_640x640.dxnn | 127.1 ±0.4 | 160 | 81.3 | 92.4 | 67~71 | 1000 | ok |
| yolo26-m-seg_640x640.dxnn | 74.9 ±2.9 | 90 | 88.8 | 100.0 | 76~80 | 800~1000 | ok |
| yolo26-l-seg_640x640.dxnn | 62.2 ±2.2 | 85 | 89.5 | 100.0 | 75~80 | 800~1000 | ok |
| yolo26-x-seg_640x640.dxnn | 31.0 ±1.3 | 58 | 87.8 | 100.0 | 76~80 | 600~1000 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 100.5 ±0.8 | 109 | 88.7 | 100.0 | 64~66 | 1000 | ok |
| yolo26-s-obb_1024x1024.dxnn | 61.6 ±0.3 | 74 | 88.7 | 100.0 | 67~70 | 1000 | ok |
| yolo26-m-obb_1024x1024.dxnn | 40.7 ±1.0 | 78 | 89.4 | 100.0 | 73~79 | 1000 | ok |
| yolo26-l-obb_1024x1024.dxnn | 30.3 ±0.7 | 56 | 88.1 | 100.0 | 73~77 | 1000 | ok |
| yolo26-x-obb_1024x1024.dxnn | 16.3 ±0.3 | 41 | 86.6 | 100.0 | 75~80 | 800~1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 98.0 ±0.2 | 74 | 90.2 | 100.0 | 64~67 | 1000 | ok |
| yolo26-s-obb_1024x1024.dxnn | 60.9 ±1.1 | 60 | 88.9 | 100.0 | 67~70 | 1000 | ok |
| yolo26-m-obb_1024x1024.dxnn | 39.7 ±0.3 | 49 | 89.3 | 100.0 | 73~78 | 1000 | ok |
| yolo26-l-obb_1024x1024.dxnn | 29.6 ±0.0 | 45 | 88.7 | 100.0 | 73~77 | 1000 | ok |
| yolo26-x-obb_1024x1024.dxnn | 16.2 ±0.4 | 31 | 86.7 | 100.0 | 75~80 | 800~1000 | ok |

#### Classification

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n_224x224.dxnn | 3588.7 ±9.8 | 98 | 87.6 | 96.0 | 61~63 | 1000 | ok |
| yolo26-s_224x224.dxnn | 2002.0 ±0.2 | 60 | 88.3 | 97.2 | 63~66 | 1000 | ok |
| yolo26-m_224x224.dxnn | 1380.3 ±0.2 | 44 | 86.8 | 97.7 | 69~73 | 1000 | ok |
| yolo26-l_224x224.dxnn | 875.6 ±0.5 | 35 | 88.8 | 98.2 | 66~69 | 1000 | ok |
| yolo26-x_224x224.dxnn | 483.8 ±0.2 | 44 | 88.1 | 99.0 | 68~71 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n_224x224.dxnn | 3580.6 ±12.0 | 98 | 87.4 | 96.5 | 61~64 | 1000 | ok |
| yolo26-s_224x224.dxnn | 2000.7 ±1.6 | 60 | 87.9 | 97.1 | 64~66 | 1000 | ok |
| yolo26-m_224x224.dxnn | 1379.4 ±0.4 | 44 | 88.6 | 97.5 | 69~73 | 1000 | ok |
| yolo26-l_224x224.dxnn | 876.0 ±1.0 | 37 | 91.0 | 98.2 | 66~68 | 1000 | ok |
| yolo26-x_224x224.dxnn | 484.7 ±0.7 | 42 | 90.6 | 99.3 | 68~72 | 1000 | ok |

### Latency (Single-Core, Sync)

#### Object Detection

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_640x640.dxnn | 41.9 | 23.87 | 21.19 | 2.68 | 47 | ok |
| yolo26-s_640x640.dxnn | 21.6 | 46.34 | 39.70 | 6.64 | 57 | ok |
| yolo26-m_640x640.dxnn | 17.9 | 55.87 | 49.06 | 6.81 | 58 | ok |
| yolo26-l_640x640.dxnn | 16.7 | 60.01 | 54.99 | 5.02 | 58 | ok |
| yolo26-x_640x640.dxnn | 10.6 | 94.21 | 85.84 | 8.37 | 58 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_640x640.dxnn | 27.6 | 36.17 | 36.17 | N/A | 56 | ok |
| yolo26-s_640x640.dxnn | 23.1 | 43.31 | 43.31 | N/A | 57 | ok |
| yolo26-m_640x640.dxnn | 20.2 | 49.47 | 49.47 | N/A | 58 | ok |
| yolo26-l_640x640.dxnn | 17.0 | 58.77 | 58.77 | N/A | 58 | ok |
| yolo26-x_640x640.dxnn | 10.9 | 91.68 | 91.68 | N/A | 59 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-pose_640x640.dxnn | 39.8 | 25.12 | 23.18 | 1.94 | 56 | ok |
| yolo26-s-pose_640x640.dxnn | 26.4 | 37.88 | 33.82 | 4.06 | 56 | ok |
| yolo26-m-pose_640x640.dxnn | 22.5 | 44.46 | 40.58 | 3.88 | 57 | ok |
| yolo26-l-pose_640x640.dxnn | 18.3 | 54.73 | 49.69 | 5.04 | 58 | ok |
| yolo26-x-pose_640x640.dxnn | 12.0 | 83.11 | 80.18 | 2.93 | 59 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-pose_640x640.dxnn | 35.4 | 28.25 | 28.25 | N/A | 56 | ok |
| yolo26-s-pose_640x640.dxnn | 30.9 | 32.33 | 32.33 | N/A | 56 | ok |
| yolo26-m-pose_640x640.dxnn | 24.3 | 41.21 | 41.21 | N/A | 58 | ok |
| yolo26-l-pose_640x640.dxnn | 19.9 | 50.17 | 50.17 | N/A | 58 | ok |
| yolo26-x-pose_640x640.dxnn | 12.5 | 79.72 | 79.72 | N/A | 59 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-seg_640x640.dxnn | 30.5 | 32.83 | 30.13 | 2.70 | 56 | ok |
| yolo26-s-seg_640x640.dxnn | 22.0 | 45.47 | 41.54 | 3.93 | 57 | ok |
| yolo26-m-seg_640x640.dxnn | 15.6 | 64.23 | 59.92 | 4.31 | 58 | ok |
| yolo26-l-seg_640x640.dxnn | 12.3 | 81.19 | 69.79 | 11.40 | 58 | ok |
| yolo26-x-seg_640x640.dxnn | 8.6 | 116.93 | 110.94 | 5.98 | 60 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-seg_640x640.dxnn | 32.6 | 30.70 | 30.70 | N/A | 56 | ok |
| yolo26-s-seg_640x640.dxnn | 22.1 | 45.16 | 45.16 | N/A | 57 | ok |
| yolo26-m-seg_640x640.dxnn | 18.3 | 54.71 | 54.71 | N/A | 58 | ok |
| yolo26-l-seg_640x640.dxnn | 15.2 | 65.71 | 65.71 | N/A | 58 | ok |
| yolo26-x-seg_640x640.dxnn | 9.0 | 111.40 | 111.40 | N/A | 60 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-obb_1024x1024.dxnn | 22.5 | 44.47 | 41.14 | 3.32 | 56 | ok |
| yolo26-s-obb_1024x1024.dxnn | 15.7 | 63.84 | 60.15 | 3.69 | 58 | ok |
| yolo26-m-obb_1024x1024.dxnn | 11.6 | 85.89 | 82.22 | 3.67 | 60 | ok |
| yolo26-l-obb_1024x1024.dxnn | 9.7 | 103.49 | 96.57 | 6.92 | 60 | ok |
| yolo26-x-obb_1024x1024.dxnn | 5.6 | 178.91 | 175.01 | 3.89 | 62 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-obb_1024x1024.dxnn | 22.9 | 43.70 | 43.70 | N/A | 57 | ok |
| yolo26-s-obb_1024x1024.dxnn | 15.8 | 63.26 | 63.26 | N/A | 58 | ok |
| yolo26-m-obb_1024x1024.dxnn | 12.8 | 78.28 | 78.28 | N/A | 60 | ok |
| yolo26-l-obb_1024x1024.dxnn | 9.7 | 102.82 | 102.82 | N/A | 60 | ok |
| yolo26-x-obb_1024x1024.dxnn | 5.7 | 175.58 | 175.58 | N/A | 62 | ok |

#### Classification

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_224x224.dxnn | 681.2 | 1.47 | 1.47 | N/A | 56 | ok |
| yolo26-s_224x224.dxnn | 473.8 | 2.11 | 2.11 | N/A | 56 | ok |
| yolo26-m_224x224.dxnn | 341.3 | 2.93 | 2.93 | N/A | 56 | ok |
| yolo26-l_224x224.dxnn | 246.7 | 4.05 | 4.05 | N/A | 56 | ok |
| yolo26-x_224x224.dxnn | 115.7 | 8.64 | 8.64 | N/A | 56 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_224x224.dxnn | 380.8 | 2.63 | 2.63 | N/A | 56 | ok |
| yolo26-s_224x224.dxnn | 462.8 | 2.16 | 2.16 | N/A | 56 | ok |
| yolo26-m_224x224.dxnn | 330.9 | 3.02 | 3.02 | N/A | 56 | ok |
| yolo26-l_224x224.dxnn | 249.8 | 4.00 | 4.00 | N/A | 56 | ok |
| yolo26-x_224x224.dxnn | 119.9 | 8.34 | 8.34 | N/A | 56 | ok |

## E2E Pipeline (Single-Stream)

### Object Detection

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | mppvideodec | 3455 | 3 | 140.6 ±0.3 | 24.57 | 244 | 35.5 | 61.5 | 57~59 | 1000 | 188 | ok |
| yolo26-s_640x640.dxnn | mppvideodec | 3455 | 3 | 132.6 ±1.8 | 26.07 | 215 | 59.1 | 77.8 | 69~70 | 1000 | 208 | ok |
| yolo26-m_640x640.dxnn | mppvideodec | 3455 | 3 | 94.9 ±4.1 | 36.40 | 156 | 86.4 | 100.0 | 82~83 | 600~1000 | 240 | ok |
| yolo26-l_640x640.dxnn | mppvideodec | 3455 | 3 | 74.6 ±5.5 | 46.30 | 124 | 89.3 | 100.0 | 82~83 | 600~1000 | 254 | ok |
| yolo26-x_640x640.dxnn | mppvideodec | 3455 | 3 | 33.3 ±1.9 | 103.68 | 71 | 93.1 | 100.0 | 82 | 400~1000 | 354 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | mppvideodec | 3455 | 3 | 95.4 ±0.3 | 36.20 | 194 | 21.2 | 70.3 | 63 | 1000 | 202 | ok |
| yolo26-s_640x640.dxnn | mppvideodec | 3455 | 3 | 95.1 ±0.2 | 36.33 | 197 | 40.0 | 66.7 | 68~69 | 1000 | 222 | ok |
| yolo26-m_640x640.dxnn | mppvideodec | 3455 | 3 | 94.8 ±0.5 | 36.44 | 201 | 71.3 | 87.4 | 80~82 | 600~1000 | 252 | ok |
| yolo26-l_640x640.dxnn | mppvideodec | 3455 | 3 | 76.2 ±4.8 | 45.36 | 167 | 90.5 | 100.0 | 81~82 | 600~1000 | 264 | ok |
| yolo26-x_640x640.dxnn | mppvideodec | 3455 | 3 | 33.5 ±2.2 | 103.21 | 95 | 93.2 | 100.0 | 82~83 | 400~800 | 354 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n_640x640.dxnn | 140.6 | 95.4 | +45.2 | +47.3% |
| yolo26-s_640x640.dxnn | 132.6 | 95.1 | +37.4 | +39.4% |
| yolo26-m_640x640.dxnn | 94.9 | 94.8 | +0.1 | +0.1% |
| yolo26-l_640x640.dxnn | 74.6 | 76.2 | -1.5 | -2.0% |
| yolo26-x_640x640.dxnn | 33.3 | 33.5 | -0.2 | -0.5% |

### Pose Estimation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 190.7 ±0.4 | 18.12 | 228 | 51.3 | 80.8 | 65~66 | 1000 | 178 | ok |
| yolo26-s-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 161.6 ±1.9 | 21.38 | 181 | 76.6 | 95.5 | 72~73 | 1000 | 201 | ok |
| yolo26-m-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 97.1 ±5.5 | 35.59 | 117 | 88.6 | 100.0 | 81~82 | 600~1000 | 233 | ok |
| yolo26-l-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 74.6 ±5.4 | 46.30 | 97 | 90.6 | 100.0 | 81~83 | 600~1000 | 248 | ok |
| yolo26-x-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 32.7 ±2.0 | 105.73 | 62 | 93.7 | 100.0 | 82~83 | 400~1000 | 369 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 234.0 ±2.8 | 14.77 | 206 | 63.0 | 87.2 | 66~67 | 1000 | 166 | ok |
| yolo26-s-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 176.0 ±0.6 | 19.63 | 150 | 81.5 | 98.6 | 71~73 | 1000 | 190 | ok |
| yolo26-m-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 98.6 ±5.0 | 35.05 | 96 | 88.8 | 100.0 | 81~82 | 600~1000 | 224 | ok |
| yolo26-l-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 75.7 ±4.1 | 45.62 | 85 | 90.7 | 100.0 | 81~82 | 600~1000 | 235 | ok |
| yolo26-x-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 33.6 ±1.8 | 102.78 | 57 | 94.6 | 100.0 | 82~83 | 400~1000 | 352 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-pose_640x640.dxnn | 190.7 | 234.0 | -43.3 | -18.5% |
| yolo26-s-pose_640x640.dxnn | 161.6 | 176.0 | -14.5 | -8.2% |
| yolo26-m-pose_640x640.dxnn | 97.1 | 98.6 | -1.5 | -1.5% |
| yolo26-l-pose_640x640.dxnn | 74.6 | 75.7 | -1.1 | -1.5% |
| yolo26-x-pose_640x640.dxnn | 32.7 | 33.6 | -0.9 | -2.8% |

### Segmentation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 85.9 ±0.2 | 40.24 | 309 | 29.3 | 50.9 | 63~64 | 1000 | 282 | ok |
| yolo26-s-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 78.2 ±0.9 | 44.15 | 274 | 48.0 | 76.9 | 70~72 | 1000 | 305 | ok |
| yolo26-m-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 48.1 ±3.3 | 71.82 | 160 | 89.6 | 100.0 | 82~83 | 400~1000 | 344 | ok |
| yolo26-l-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 41.1 ±3.5 | 83.98 | 141 | 90.7 | 100.0 | 82~83 | 400~1000 | 361 | ok |
| yolo26-x-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 18.8 ±0.2 | 183.70 | 79 | 89.6 | 100.0 | 82~83 | 400~800 | 465 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 78.6 ±1.7 | 43.94 | 276 | 22.3 | 74.6 | 63~64 | 1000 | 312 | ok |
| yolo26-s-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 75.5 ±1.8 | 45.76 | 273 | 42.7 | 73.4 | 70~72 | 1000 | 336 | ok |
| yolo26-m-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 48.7 ±2.8 | 70.92 | 161 | 90.9 | 100.0 | 82~83 | 400~800 | 353 | ok |
| yolo26-l-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 41.2 ±3.4 | 83.94 | 133 | 91.5 | 100.0 | 82~83 | 400~1000 | 380 | ok |
| yolo26-x-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 18.6 ±0.3 | 185.69 | 83 | 90.0 | 100.0 | 82~83 | 400~800 | 478 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-seg_640x640.dxnn | 85.9 | 78.6 | +7.2 | +9.2% |
| yolo26-s-seg_640x640.dxnn | 78.2 | 75.5 | +2.7 | +3.6% |
| yolo26-m-seg_640x640.dxnn | 48.1 | 48.7 | -0.6 | -1.3% |
| yolo26-l-seg_640x640.dxnn | 41.1 | 41.2 | -0.0 | -0.0% |
| yolo26-x-seg_640x640.dxnn | 18.8 | 18.6 | +0.2 | +1.1% |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 101.9 ±0.8 | 25.90 | 154 | 85.1 | 100.0 | 68~70 | 1000 | 216 | ok |
| yolo26-s-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 61.5 ±0.2 | 42.95 | 99 | 90.5 | 100.0 | 75~79 | 1000 | 239 | ok |
| yolo26-m-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 29.4 ±2.5 | 89.89 | 71 | 91.2 | 100.0 | 83 | 400~1000 | 272 | ok |
| yolo26-l-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 22.5 ±1.6 | 117.15 | 62 | 91.8 | 100.0 | 83 | 400~1000 | 288 | ok |
| yolo26-x-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 10.5 ±0.2 | 252.17 | 39 | 89.3 | 100.0 | 83 | 300~1000 | 392 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 100.2 ±0.4 | 26.34 | 151 | 87.1 | 100.0 | 69~71 | 1000 | 221 | ok |
| yolo26-s-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 61.0 ±0.6 | 43.29 | 106 | 90.7 | 100.0 | 75~78 | 1000 | 238 | ok |
| yolo26-m-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 30.1 ±2.3 | 87.59 | 76 | 91.9 | 100.0 | 83 | 400~1000 | 272 | ok |
| yolo26-l-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 22.3 ±1.6 | 118.60 | 62 | 92.3 | 100.0 | 83~84 | 400~1000 | 286 | ok |
| yolo26-x-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 10.4 ±0.1 | 253.85 | 37 | 89.7 | 100.0 | 83 | 300~800 | 389 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-obb_1024x1024.dxnn | 101.9 | 100.2 | +1.7 | +1.7% |
| yolo26-s-obb_1024x1024.dxnn | 61.5 | 61.0 | +0.5 | +0.8% |
| yolo26-m-obb_1024x1024.dxnn | 29.4 | 30.1 | -0.8 | -2.6% |
| yolo26-l-obb_1024x1024.dxnn | 22.5 | 22.3 | +0.3 | +1.3% |
| yolo26-x-obb_1024x1024.dxnn | 10.5 | 10.4 | +0.1 | +0.7% |

### Classification

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_224x224.dxnn | mppvideodec | 3455 | 3 | 974.6 ±18.0 | 3.54 | 153 | 12.9 | 43.8 | 61~62 | 1000 | 90 | ok |
| yolo26-s_224x224.dxnn | mppvideodec | 3455 | 3 | 952.1 ±30.7 | 3.63 | 152 | 24.7 | 64.1 | 63~64 | 1000 | 100 | ok |
| yolo26-m_224x224.dxnn | mppvideodec | 3455 | 3 | 956.5 ±18.9 | 3.61 | 151 | 31.8 | 78.3 | 69~71 | 1000 | 114 | ok |
| yolo26-l_224x224.dxnn | mppvideodec | 3455 | 3 | 848.2 ±8.2 | 4.07 | 136 | 57.5 | 97.9 | 67 | 1000 | 127 | ok |
| yolo26-x_224x224.dxnn | mppvideodec | 3455 | 3 | 479.3 ±3.3 | 7.21 | 96 | 67.8 | 98.8 | 71 | 1000 | 204 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_224x224.dxnn | mppvideodec | 3455 | 3 | 975.3 ±9.9 | 3.54 | 152 | 13.1 | 44.0 | 61~62 | 1000 | 91 | ok |
| yolo26-s_224x224.dxnn | mppvideodec | 3455 | 3 | 969.0 ±27.1 | 3.56 | 152 | 23.4 | 64.0 | 63~64 | 1000 | 100 | ok |
| yolo26-m_224x224.dxnn | mppvideodec | 3455 | 3 | 963.9 ±15.6 | 3.58 | 152 | 33.5 | 78.7 | 69~71 | 1000 | 114 | ok |
| yolo26-l_224x224.dxnn | mppvideodec | 3455 | 3 | 847.0 ±5.0 | 4.08 | 136 | 55.9 | 97.9 | 66~67 | 1000 | 127 | ok |
| yolo26-x_224x224.dxnn | mppvideodec | 3455 | 3 | 479.3 ±2.2 | 7.21 | 100 | 65.6 | 99.2 | 71 | 1000 | 204 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n_224x224.dxnn | 974.6 | 975.3 | -0.7 | -0.1% |
| yolo26-s_224x224.dxnn | 952.1 | 969.0 | -16.9 | -1.7% |
| yolo26-m_224x224.dxnn | 956.5 | 963.9 | -7.4 | -0.8% |
| yolo26-l_224x224.dxnn | 848.2 | 847.0 | +1.2 | +0.1% |
| yolo26-x_224x224.dxnn | 479.3 | 479.3 | +0.1 | +0.0% |

## E2E Pipeline (Multi-Stream)

### Object Detection

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | 4 | 3 | 137.8 ±1.8 | 34.4 | 256 | 38.3 | 61.4 | 64~66 | 1000 | 211 | ok |
| yolo26-n_640x640.dxnn | 5 | 3 | 139.1 ±0.7 | 27.8 | 252 | 38.9 | 61.9 | 68~69 | 1000 | 216 | ok |
| yolo26-s_640x640.dxnn | 4 | 3 | 130.4 ±0.6 | 32.6 | 226 | 63.2 | 81.1 | 75~77 | 1000 | 231 | ok |
| yolo26-s_640x640.dxnn | 5 | 3 | 130.2 ±0.4 | 26.0 | 227 | 63.1 | 82.3 | 78~79 | 1000 | 237 | ok |
| yolo26-m_640x640.dxnn | 3 | 3 | 73.1 ±1.0 | 24.4 | 125 | 92.7 | 100.0 | 83 | 400~1000 | 257 | ok |
| yolo26-m_640x640.dxnn | 2 | 3 | 72.8 ±0.6 | 36.4 | 124 | 92.0 | 100.0 | 84 | 400~1000 | 251 | ok |
| yolo26-l_640x640.dxnn | 2 | 3 | 59.2 ±1.4 | 29.6 | 105 | 93.8 | 100.0 | 83~84 | 400~1000 | 265 | ok |
| yolo26-l_640x640.dxnn | 1 | 3 | 74.6 ±5.5 | 74.6 | 124 | 89.3 | 100.0 | 82~83 | 600~1000 | 254 | ok |
| yolo26-x_640x640.dxnn | 1 | 3 | 33.3 ±1.9 | 33.3 | 71 | 93.1 | 100.0 | 82 | 400~1000 | 354 | ok |
| yolo26-x_640x640.dxnn | 2 | 3 | 29.9 ±0.2 | 14.9 | 71 | 93.5 | 100.0 | 82~84 | 400~1000 | 359 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | 3 | 3 | 95.0 ±0.1 | 31.7 | 199 | 22.4 | 70.1 | 64~65 | 1000 | 224 | ok |
| yolo26-n_640x640.dxnn | 4 | 3 | 95.0 ±0.2 | 23.7 | 196 | 22.5 | 70.1 | 65 | 1000 | 232 | ok |
| yolo26-s_640x640.dxnn | 3 | 3 | 95.0 ±0.1 | 31.7 | 206 | 42.2 | 66.7 | 71 | 1000 | 242 | ok |
| yolo26-s_640x640.dxnn | 4 | 3 | 95.3 ±0.5 | 23.8 | 207 | 42.6 | 66.8 | 72 | 1000 | 253 | ok |
| yolo26-m_640x640.dxnn | 3 | 3 | 74.1 ±1.1 | 24.7 | 166 | 93.3 | 100.0 | 82~83 | 400~1000 | 273 | ok |
| yolo26-m_640x640.dxnn | 2 | 3 | 73.9 ±1.3 | 36.9 | 163 | 91.6 | 100.0 | 83 | 400~1000 | 263 | ok |
| yolo26-l_640x640.dxnn | 2 | 3 | 68.5 ±15.7 | 34.3 | 152 | 94.8 | 100.0 | 74~84 | 400~1000 | 277 | ok |
| yolo26-l_640x640.dxnn | 3 | 3 | 64.4 ±4.7 | 21.5 | 148 | 95.3 | 100.0 | 83 | 400~1000 | 289 | ok |
| yolo26-x_640x640.dxnn | 1 | 3 | 33.5 ±2.2 | 33.5 | 95 | 93.2 | 100.0 | 82~83 | 400~800 | 354 | ok |
| yolo26-x_640x640.dxnn | 2 | 3 | 29.9 ±0.2 | 14.9 | 90 | 94.2 | 100.0 | 83 | 400~1000 | 369 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n_640x640.dxnn | 4 | 34.4 | 3 | 31.7 |
| yolo26-s_640x640.dxnn | 4 | 32.6 | 3 | 31.7 |
| yolo26-m_640x640.dxnn | 2 | 36.4 | 2 | 36.9 |
| yolo26-l_640x640.dxnn | 1 | 74.6 | 2 | 34.3 |
| yolo26-x_640x640.dxnn | 1 | 33.3 | 1 | 33.5 |

### Pose Estimation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 6 | 3 | 191.0 ±1.2 | 31.8 | 238 | 58.2 | 78.8 | 71~73 | 1000 | 218 | ok |
| yolo26-n-pose_640x640.dxnn | 7 | 3 | 187.7 ±0.1 | 26.8 | 244 | 57.5 | 81.5 | 75 | 1000 | 224 | ok |
| yolo26-s-pose_640x640.dxnn | 5 | 3 | 161.3 ±1.9 | 32.2 | 199 | 85.4 | 94.8 | 80~83 | 800~1000 | 235 | ok |
| yolo26-s-pose_640x640.dxnn | 6 | 3 | 152.6 ±0.1 | 25.4 | 190 | 88.8 | 97.4 | 84 | 800~1000 | 240 | ok |
| yolo26-m-pose_640x640.dxnn | 3 | 3 | 71.7 ±1.7 | 23.9 | 94 | 94.2 | 100.0 | 83 | 400~1000 | 254 | ok |
| yolo26-m-pose_640x640.dxnn | 2 | 3 | 71.0 ±1.4 | 35.5 | 94 | 93.2 | 100.0 | 83 | 400~1000 | 246 | ok |
| yolo26-l-pose_640x640.dxnn | 2 | 3 | 60.6 ±1.6 | 30.3 | 83 | 95.1 | 100.0 | 83~84 | 400~1000 | 260 | ok |
| yolo26-l-pose_640x640.dxnn | 3 | 3 | 56.6 ±0.7 | 18.9 | 82 | 95.2 | 100.0 | 82~84 | 400~1000 | 269 | ok |
| yolo26-x-pose_640x640.dxnn | 1 | 3 | 32.7 ±2.0 | 32.7 | 62 | 93.7 | 100.0 | 82~83 | 400~1000 | 369 | ok |
| yolo26-x-pose_640x640.dxnn | 2 | 3 | 29.1 ±0.2 | 14.6 | 61 | 94.6 | 100.0 | 82~83 | 400~1000 | 369 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 7 | 3 | 238.8 ±3.6 | 34.1 | 208 | 74.7 | 90.6 | 73~76 | 1000 | 220 | ok |
| yolo26-n-pose_640x640.dxnn | 8 | 3 | 238.3 ±4.1 | 29.8 | 209 | 75.1 | 90.1 | 77~78 | 1000 | 225 | ok |
| yolo26-s-pose_640x640.dxnn | 5 | 3 | 174.7 ±3.7 | 34.9 | 157 | 92.7 | 99.5 | 80~82 | 800~1000 | 231 | ok |
| yolo26-s-pose_640x640.dxnn | 6 | 3 | 160.6 ±0.6 | 26.8 | 144 | 93.9 | 100.0 | 84 | 800~1000 | 235 | ok |
| yolo26-m-pose_640x640.dxnn | 3 | 3 | 73.4 ±1.8 | 24.5 | 81 | 94.8 | 100.0 | 82~83 | 400~1000 | 244 | ok |
| yolo26-m-pose_640x640.dxnn | 2 | 3 | 73.6 ±1.9 | 36.8 | 86 | 93.7 | 100.0 | 82~83 | 400~1000 | 236 | ok |
| yolo26-l-pose_640x640.dxnn | 2 | 3 | 61.4 ±1.1 | 30.7 | 74 | 95.3 | 100.0 | 83 | 400~1000 | 250 | ok |
| yolo26-l-pose_640x640.dxnn | 3 | 3 | 58.3 ±1.1 | 19.4 | 73 | 95.5 | 100.0 | 82~83 | 400~1000 | 259 | ok |
| yolo26-x-pose_640x640.dxnn | 1 | 3 | 33.6 ±1.8 | 33.6 | 57 | 94.6 | 100.0 | 82~83 | 400~1000 | 352 | ok |
| yolo26-x-pose_640x640.dxnn | 2 | 3 | 30.8 ±0.9 | 15.4 | 58 | 95.9 | 100.0 | 81~83 | 400~800 | 352 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-pose_640x640.dxnn | 6 | 31.8 | 7 | 34.1 |
| yolo26-s-pose_640x640.dxnn | 5 | 32.2 | 5 | 34.9 |
| yolo26-m-pose_640x640.dxnn | 2 | 35.5 | 2 | 36.8 |
| yolo26-l-pose_640x640.dxnn | 2 | 30.3 | 2 | 30.7 |
| yolo26-x-pose_640x640.dxnn | 1 | 32.7 | 1 | 33.6 |

### Segmentation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 2 | 3 | 86.4 ±1.4 | 43.2 | 308 | 30.8 | 53.6 | 67~68 | 1000 | 302 | ok |
| yolo26-n-seg_640x640.dxnn | 3 | 3 | 85.9 ±0.3 | 28.6 | 315 | 30.9 | 52.0 | 70 | 1000 | 316 | ok |
| yolo26-s-seg_640x640.dxnn | 2 | 3 | 79.1 ±0.7 | 39.6 | 279 | 49.9 | 78.0 | 76~77 | 1000 | 328 | ok |
| yolo26-s-seg_640x640.dxnn | 3 | 3 | 80.0 ±1.7 | 26.6 | 276 | 51.1 | 82.7 | 79~80 | 1000 | 336 | ok |
| yolo26-m-seg_640x640.dxnn | 1 | 3 | 48.1 ±3.3 | 48.1 | 160 | 89.6 | 100.0 | 82~83 | 400~1000 | 344 | ok |
| yolo26-m-seg_640x640.dxnn | 2 | 3 | 42.0 ±0.4 | 21.0 | 140 | 96.0 | 100.0 | 83~84 | 400~800 | 362 | ok |
| yolo26-l-seg_640x640.dxnn | 1 | 3 | 41.1 ±3.5 | 41.1 | 141 | 90.7 | 100.0 | 82~83 | 400~1000 | 361 | ok |
| yolo26-l-seg_640x640.dxnn | 2 | 3 | 36.2 ±0.0 | 18.1 | 125 | 92.4 | 100.0 | 83 | 400~800 | 377 | ok |
| yolo26-x-seg_640x640.dxnn | 1 | 3 | 18.8 ±0.2 | 18.8 | 79 | 89.6 | 100.0 | 82~83 | 400~800 | 465 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 2 | 3 | 79.1 ±1.0 | 39.5 | 269 | 23.3 | 75.5 | 66~67 | 1000 | 335 | ok |
| yolo26-n-seg_640x640.dxnn | 3 | 3 | 77.7 ±1.7 | 25.9 | 280 | 23.2 | 74.6 | 68~69 | 1000 | 342 | ok |
| yolo26-s-seg_640x640.dxnn | 2 | 3 | 76.9 ±1.6 | 38.4 | 273 | 44.4 | 75.5 | 75~77 | 1000 | 358 | ok |
| yolo26-s-seg_640x640.dxnn | 3 | 3 | 76.2 ±1.3 | 25.4 | 268 | 44.7 | 75.7 | 78~79 | 1000 | 366 | ok |
| yolo26-m-seg_640x640.dxnn | 1 | 3 | 48.7 ±2.8 | 48.7 | 161 | 90.9 | 100.0 | 82~83 | 400~800 | 353 | ok |
| yolo26-m-seg_640x640.dxnn | 2 | 3 | 42.1 ±0.1 | 21.1 | 138 | 96.1 | 100.0 | 83~84 | 400~800 | 382 | ok |
| yolo26-l-seg_640x640.dxnn | 1 | 3 | 41.2 ±3.4 | 41.2 | 133 | 91.5 | 100.0 | 82~83 | 400~1000 | 380 | ok |
| yolo26-l-seg_640x640.dxnn | 2 | 3 | 36.0 ±0.1 | 18.0 | 120 | 93.5 | 100.0 | 83 | 400~800 | 403 | ok |
| yolo26-x-seg_640x640.dxnn | 1 | 3 | 18.6 ±0.3 | 18.6 | 83 | 90.0 | 100.0 | 82~83 | 400~800 | 478 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-seg_640x640.dxnn | 2 | 43.2 | 2 | 39.5 |
| yolo26-s-seg_640x640.dxnn | 2 | 39.6 | 2 | 38.4 |
| yolo26-m-seg_640x640.dxnn | 1 | 48.1 | 1 | 48.7 |
| yolo26-l-seg_640x640.dxnn | 1 | 41.1 | 1 | 41.2 |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 3 | 3 | 101.8 ±0.3 | 33.9 | 162 | 92.5 | 100.0 | 75~78 | 1000 | 243 | ok |
| yolo26-n-obb_1024x1024.dxnn | 4 | 3 | 101.7 ±0.2 | 25.4 | 161 | 93.7 | 100.0 | 80~81 | 1000 | 254 | ok |
| yolo26-s-obb_1024x1024.dxnn | 2 | 3 | 60.1 ±1.5 | 30.0 | 103 | 92.8 | 100.0 | 83 | 800~1000 | 257 | ok |
| yolo26-s-obb_1024x1024.dxnn | 3 | 3 | 57.0 ±0.2 | 19.0 | 97 | 94.9 | 100.0 | 84 | 600~1000 | 267 | ok |
| yolo26-m-obb_1024x1024.dxnn | 1 | 3 | 29.4 ±2.5 | 29.4 | 71 | 91.2 | 100.0 | 83 | 400~1000 | 272 | ok |
| yolo26-l-obb_1024x1024.dxnn | 1 | 3 | 22.5 ±1.6 | 22.5 | 62 | 91.8 | 100.0 | 83 | 400~1000 | 288 | ok |
| yolo26-x-obb_1024x1024.dxnn | 1 | 3 | 10.5 ±0.2 | 10.5 | 39 | 89.3 | 100.0 | 83 | 300~1000 | 392 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 3 | 3 | 100.2 ±0.1 | 33.4 | 159 | 93.4 | 100.0 | 76~78 | 1000 | 246 | ok |
| yolo26-n-obb_1024x1024.dxnn | 4 | 3 | 100.3 ±0.2 | 25.1 | 157 | 94.7 | 100.0 | 80~81 | 1000 | 263 | ok |
| yolo26-s-obb_1024x1024.dxnn | 2 | 3 | 60.2 ±1.2 | 30.1 | 108 | 93.7 | 100.0 | 82~83 | 600~1000 | 255 | ok |
| yolo26-s-obb_1024x1024.dxnn | 3 | 3 | 57.0 ±0.6 | 19.0 | 104 | 94.8 | 100.0 | 84 | 600~1000 | 266 | ok |
| yolo26-m-obb_1024x1024.dxnn | 1 | 3 | 30.1 ±2.3 | 30.1 | 76 | 91.9 | 100.0 | 83 | 400~1000 | 272 | ok |
| yolo26-m-obb_1024x1024.dxnn | 2 | 3 | 26.6 ±0.1 | 13.3 | 74 | 93.5 | 100.0 | 83~84 | 400~1000 | 283 | ok |
| yolo26-l-obb_1024x1024.dxnn | 1 | 3 | 22.3 ±1.6 | 22.3 | 62 | 92.3 | 100.0 | 83~84 | 400~1000 | 286 | ok |
| yolo26-x-obb_1024x1024.dxnn | 1 | 3 | 10.4 ±0.1 | 10.4 | 37 | 89.7 | 100.0 | 83 | 300~800 | 389 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-obb_1024x1024.dxnn | 3 | 33.9 | 3 | 33.4 |
| yolo26-s-obb_1024x1024.dxnn | 2 | 30.0 | 2 | 30.1 |
| yolo26-m-obb_1024x1024.dxnn | < 1 | — | 1 | 30.1 |

---
*Report generated by dx-benchmark tool*
