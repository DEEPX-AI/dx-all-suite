# YOLO26 Benchmark Report

**Generated:** 2026-07-11 15:10:21 (Local)

## Test Timing

| # | Type | Start | End | Duration |
|---|------|-------|-----|----------|
| 1 | run | 2026-07-10 18:04:16 | 2026-07-11 15:10:21 | 21h 6m 4s |

## Executive Summary

### Object Detection

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n_640x640.dxnn | ON | 24.03 | 211.1 | 162.6 | 5 |
| yolo26-n_640x640.dxnn | OFF | 23.00 | 235.9 | 181.4 | 6 |
| yolo26-s_640x640.dxnn | ON | 30.82 | 174.5 | 140.3 | 4 |
| yolo26-s_640x640.dxnn | OFF | 29.82 | 193.4 | 163.8 | 5 |
| yolo26-m_640x640.dxnn | ON | 38.15 | 121.1 | 115.2 | 3 |
| yolo26-m_640x640.dxnn | OFF | 37.09 | 115.2 | 116.0 | 3 |
| yolo26-l_640x640.dxnn | ON | 46.12 | 85.8 | 87.4 | 2 |
| yolo26-l_640x640.dxnn | OFF | 44.21 | 86.7 | 85.8 | 2 |
| yolo26-x_640x640.dxnn | ON | 71.87 | 47.3 | 45.0 | 1 |
| yolo26-x_640x640.dxnn | OFF | 69.94 | 47.6 | 45.2 | 1 |

### Pose Estimation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-pose_640x640.dxnn | ON | 21.22 | 234.1 | 172.9 | 6 |
| yolo26-n-pose_640x640.dxnn | OFF | 20.34 | 278.7 | 195.1 | 7 |
| yolo26-s-pose_640x640.dxnn | ON | 27.92 | 182.5 | 155.4 | 5 |
| yolo26-s-pose_640x640.dxnn | OFF | 27.01 | 175.1 | 175.4 | 5 |
| yolo26-m-pose_640x640.dxnn | ON | 35.94 | 111.4 | 110.4 | 3 |
| yolo26-m-pose_640x640.dxnn | OFF | 34.85 | 112.1 | 110.2 | 3 |
| yolo26-l-pose_640x640.dxnn | ON | 42.69 | 83.9 | 82.4 | 2 |
| yolo26-l-pose_640x640.dxnn | OFF | 41.97 | 83.2 | 83.2 | 2 |
| yolo26-x-pose_640x640.dxnn | ON | 69.55 | 46.2 | 43.9 | 1 |
| yolo26-x-pose_640x640.dxnn | OFF | 66.57 | 46.9 | 44.3 | 1 |

### Segmentation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-seg_640x640.dxnn | ON | 37.34 | 120.5 | 95.2 | 3 |
| yolo26-n-seg_640x640.dxnn | OFF | 36.08 | 138.8 | 106.7 | 3 |
| yolo26-s-seg_640x640.dxnn | ON | 47.04 | 106.0 | 86.3 | 2 |
| yolo26-s-seg_640x640.dxnn | OFF | 44.88 | 112.4 | 98.4 | 3 |
| yolo26-m-seg_640x640.dxnn | ON | 61.02 | 79.4 | 67.7 | 1 |
| yolo26-m-seg_640x640.dxnn | OFF | 59.19 | 79.8 | 70.8 | 1 |
| yolo26-l-seg_640x640.dxnn | ON | 67.88 | 65.0 | 58.7 | 1 |
| yolo26-l-seg_640x640.dxnn | OFF | 66.89 | 64.0 | 59.8 | 1 |
| yolo26-x-seg_640x640.dxnn | ON | 105.00 | 34.1 | 24.7 | — |
| yolo26-x-seg_640x640.dxnn | OFF | 102.38 | 34.1 | 24.6 | — |

### Oriented BBox (OBB)

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-obb_1024x1024.dxnn | ON | 36.33 | 97.9 | 98.3 | 3 |
| yolo26-n-obb_1024x1024.dxnn | OFF | 35.03 | 97.9 | 98.0 | 3 |
| yolo26-s-obb_1024x1024.dxnn | ON | 51.65 | 60.2 | 61.5 | 2 |
| yolo26-s-obb_1024x1024.dxnn | OFF | 50.42 | 59.9 | 61.7 | 2 |
| yolo26-m-obb_1024x1024.dxnn | ON | 69.43 | 39.7 | 40.9 | 1 |
| yolo26-m-obb_1024x1024.dxnn | OFF | 68.37 | 39.9 | 41.1 | 1 |
| yolo26-l-obb_1024x1024.dxnn | ON | 87.59 | 29.6 | 29.6 | — |
| yolo26-l-obb_1024x1024.dxnn | OFF | 87.00 | 29.6 | 29.7 | — |
| yolo26-x-obb_1024x1024.dxnn | ON | 155.98 | 16.5 | 13.4 | — |
| yolo26-x-obb_1024x1024.dxnn | OFF | 154.56 | 16.5 | 13.4 | — |

### Classification

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n_224x224.dxnn | ON | 1.43 | 3523.0 | 276.7 | — |
| yolo26-n_224x224.dxnn | OFF | 1.45 | 3527.4 | 278.3 | — |
| yolo26-s_224x224.dxnn | ON | 2.05 | 1998.3 | 288.3 | — |
| yolo26-s_224x224.dxnn | OFF | 2.05 | 1998.4 | 288.8 | — |
| yolo26-m_224x224.dxnn | ON | 2.68 | 1377.3 | 288.4 | — |
| yolo26-m_224x224.dxnn | OFF | 2.67 | 1376.0 | 289.0 | — |
| yolo26-l_224x224.dxnn | ON | 3.96 | 871.3 | 291.3 | — |
| yolo26-l_224x224.dxnn | OFF | 3.97 | 874.4 | 291.0 | — |
| yolo26-x_224x224.dxnn | ON | 6.78 | 484.7 | 289.4 | — |
| yolo26-x_224x224.dxnn | OFF | 6.77 | 484.2 | 289.7 | — |

## Environment

| Item | Value |
|------|-------|
| Product | DX-AIPlayer-N97 |
| Hostname | deepx |
| OS | Ubuntu 24.04.4 LTS |
| Kernel | 6.17.0-35-generic |
| CPU | Intel(R) N97 |
| CPU Cores | 4 |
| RAM | 7.5 GB |
| NPU SKU | M1 |
| NPU RT | v3.4.0 |
| NPU Driver (RT) | v2.5.1 |
| NPU Driver (PCIe) | v2.4.1 |
| NPU Firmware | v2.7.1 |
| NPU Memory | LPDDR5 5600 Mbps, 3.92GiB |
| NPU Board | M.2, Rev 1.0 |
| NPU PCIe | Gen3 X2 [03:00:00] |

### Tools

| Tool | Available | Version |
|------|-----------|---------|
| run_model | Yes | DXRT v3.4.0 run_model |
| gst-launch-1.0 | Yes | gst-launch-1.0 version 1.24.2 |
| gst-inspect-1.0 | Yes | gst-inspect-1.0 version 1.24.2 |
| dxtop | Yes | DX-TOP 1.1.0 |
| ffprobe | Yes | ffprobe version 6.1.1-3ubuntu5 Copyright (c) 2007-2023 the F... |

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
| yolo26-n_640x640.dxnn | 211.1 ±1.8 | 237 | 53.2 | 76.8 | 49~52 | 1000 | ok |
| yolo26-s_640x640.dxnn | 174.5 ±0.6 | 208 | 79.3 | 92.9 | 60~62 | 1000 | ok |
| yolo26-m_640x640.dxnn | 121.1 ±0.7 | 143 | 90.3 | 100.0 | 63~68 | 1000 | ok |
| yolo26-l_640x640.dxnn | 85.8 ±1.0 | 121 | 91.4 | 100.0 | 62~67 | 1000 | ok |
| yolo26-x_640x640.dxnn | 47.3 ±0.5 | 74 | 88.5 | 100.0 | 64~68 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n_640x640.dxnn | 235.9 ±0.8 | 204 | 62.5 | 79.2 | 58~60 | 1000 | ok |
| yolo26-s_640x640.dxnn | 193.4 ±1.1 | 148 | 89.2 | 100.0 | 60~63 | 1000 | ok |
| yolo26-m_640x640.dxnn | 115.2 ±0.6 | 111 | 90.7 | 100.0 | 63~67 | 1000 | ok |
| yolo26-l_640x640.dxnn | 86.7 ±1.5 | 88 | 91.6 | 100.0 | 62~67 | 1000 | ok |
| yolo26-x_640x640.dxnn | 47.6 ±0.8 | 51 | 90.1 | 100.0 | 64~68 | 1000 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 234.1 ±1.3 | 220 | 66.4 | 83.6 | 58~60 | 1000 | ok |
| yolo26-s-pose_640x640.dxnn | 182.5 ±0.5 | 155 | 90.3 | 100.0 | 60~63 | 1000 | ok |
| yolo26-m-pose_640x640.dxnn | 111.4 ±0.7 | 114 | 90.6 | 100.0 | 63~68 | 1000 | ok |
| yolo26-l-pose_640x640.dxnn | 83.9 ±0.6 | 94 | 90.3 | 100.0 | 62~67 | 1000 | ok |
| yolo26-x-pose_640x640.dxnn | 46.2 ±0.5 | 53 | 90.1 | 100.0 | 63~68 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 278.7 ±1.4 | 159 | 83.9 | 97.8 | 59~61 | 1000 | ok |
| yolo26-s-pose_640x640.dxnn | 175.1 ±0.9 | 121 | 90.9 | 100.0 | 60~63 | 1000 | ok |
| yolo26-m-pose_640x640.dxnn | 112.1 ±1.1 | 80 | 91.3 | 100.0 | 63~68 | 1000 | ok |
| yolo26-l-pose_640x640.dxnn | 83.2 ±1.9 | 64 | 91.0 | 100.0 | 62~67 | 1000 | ok |
| yolo26-x-pose_640x640.dxnn | 46.9 ±0.8 | 37 | 88.9 | 100.0 | 64~68 | 1000 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 120.5 ±0.1 | 280 | 37.4 | 69.2 | 57~58 | 1000 | ok |
| yolo26-s-seg_640x640.dxnn | 106.0 ±0.3 | 246 | 63.9 | 82.5 | 59~62 | 1000 | ok |
| yolo26-m-seg_640x640.dxnn | 79.4 ±0.6 | 173 | 89.4 | 100.0 | 65~70 | 1000 | ok |
| yolo26-l-seg_640x640.dxnn | 65.0 ±0.1 | 159 | 90.5 | 100.0 | 64~70 | 1000 | ok |
| yolo26-x-seg_640x640.dxnn | 34.1 ±0.1 | 98 | 88.7 | 100.0 | 65~71 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 138.8 ±1.0 | 242 | 45.9 | 74.8 | 58~59 | 1000 | ok |
| yolo26-s-seg_640x640.dxnn | 112.4 ±0.7 | 221 | 69.9 | 85.3 | 60~63 | 1000 | ok |
| yolo26-m-seg_640x640.dxnn | 79.8 ±0.6 | 146 | 90.7 | 100.0 | 65~70 | 1000 | ok |
| yolo26-l-seg_640x640.dxnn | 64.0 ±0.2 | 128 | 90.6 | 100.0 | 64~69 | 1000 | ok |
| yolo26-x-seg_640x640.dxnn | 34.1 ±0.5 | 72 | 89.0 | 100.0 | 66~71 | 1000 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 97.9 ±0.2 | 108 | 92.0 | 100.0 | 59~61 | 1000 | ok |
| yolo26-s-obb_1024x1024.dxnn | 60.2 ±0.6 | 69 | 91.3 | 100.0 | 60~63 | 1000 | ok |
| yolo26-m-obb_1024x1024.dxnn | 39.7 ±0.2 | 48 | 89.6 | 100.0 | 63~67 | 1000 | ok |
| yolo26-l-obb_1024x1024.dxnn | 29.6 ±0.0 | 35 | 90.9 | 100.0 | 63~67 | 1000 | ok |
| yolo26-x-obb_1024x1024.dxnn | 16.5 ±0.0 | 19 | 87.6 | 100.0 | 65~69 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 97.9 ±0.1 | 75 | 90.1 | 100.0 | 59~61 | 1000 | ok |
| yolo26-s-obb_1024x1024.dxnn | 59.9 ±0.2 | 49 | 91.4 | 100.0 | 60~63 | 1000 | ok |
| yolo26-m-obb_1024x1024.dxnn | 39.9 ±0.5 | 33 | 91.1 | 100.0 | 63~67 | 1000 | ok |
| yolo26-l-obb_1024x1024.dxnn | 29.6 ±0.0 | 24 | 91.2 | 100.0 | 63~67 | 1000 | ok |
| yolo26-x-obb_1024x1024.dxnn | 16.5 ±0.0 | 13 | 87.3 | 100.0 | 65~69 | 1000 | ok |

#### Classification

**ORT = ON**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n_224x224.dxnn | 3523.0 ±8.9 | 90 | 87.9 | 95.4 | 57~58 | 1000 | ok |
| yolo26-s_224x224.dxnn | 1998.3 ±3.6 | 66 | 88.2 | 97.3 | 59~60 | 1000 | ok |
| yolo26-m_224x224.dxnn | 1377.3 ±4.6 | 44 | 88.7 | 97.7 | 61~64 | 1000 | ok |
| yolo26-l_224x224.dxnn | 871.3 ±5.0 | 28 | 89.8 | 98.4 | 60~62 | 1000 | ok |
| yolo26-x_224x224.dxnn | 484.7 ±0.5 | 16 | 91.7 | 99.3 | 61~65 | 1000 | ok |

**ORT = OFF**

| Model | FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|------|----------|----------|-------------|---------|--------|
| yolo26-n_224x224.dxnn | 3527.4 ±10.0 | 90 | 86.6 | 95.5 | 57~58 | 1000 | ok |
| yolo26-s_224x224.dxnn | 1998.4 ±5.7 | 66 | 89.6 | 97.2 | 58~60 | 1000 | ok |
| yolo26-m_224x224.dxnn | 1376.0 ±3.2 | 44 | 87.9 | 97.7 | 61~64 | 1000 | ok |
| yolo26-l_224x224.dxnn | 874.4 ±0.7 | 28 | 89.9 | 98.4 | 60~62 | 1000 | ok |
| yolo26-x_224x224.dxnn | 484.2 ±1.0 | 16 | 90.5 | 99.3 | 61~65 | 1000 | ok |

### Latency (Single-Core, Sync)

#### Object Detection

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_640x640.dxnn | 41.6 | 24.03 | 22.72 | 1.30 | 46 | ok |
| yolo26-s_640x640.dxnn | 32.5 | 30.82 | 29.50 | 1.32 | 56 | ok |
| yolo26-m_640x640.dxnn | 26.2 | 38.15 | 36.77 | 1.37 | 56 | ok |
| yolo26-l_640x640.dxnn | 21.7 | 46.12 | 44.74 | 1.38 | 56 | ok |
| yolo26-x_640x640.dxnn | 13.9 | 71.87 | 70.49 | 1.38 | 57 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_640x640.dxnn | 43.5 | 23.00 | 23.00 | N/A | 56 | ok |
| yolo26-s_640x640.dxnn | 33.5 | 29.82 | 29.82 | N/A | 56 | ok |
| yolo26-m_640x640.dxnn | 27.0 | 37.09 | 37.09 | N/A | 56 | ok |
| yolo26-l_640x640.dxnn | 22.6 | 44.21 | 44.21 | N/A | 56 | ok |
| yolo26-x_640x640.dxnn | 14.3 | 69.94 | 69.94 | N/A | 57 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-pose_640x640.dxnn | 47.1 | 21.22 | 20.22 | 0.99 | 55 | ok |
| yolo26-s-pose_640x640.dxnn | 35.8 | 27.92 | 26.90 | 1.02 | 55 | ok |
| yolo26-m-pose_640x640.dxnn | 27.8 | 35.94 | 34.94 | 1.00 | 56 | ok |
| yolo26-l-pose_640x640.dxnn | 23.4 | 42.69 | 41.71 | 0.98 | 56 | ok |
| yolo26-x-pose_640x640.dxnn | 14.4 | 69.55 | 68.56 | 0.99 | 57 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-pose_640x640.dxnn | 49.2 | 20.34 | 20.34 | N/A | 55 | ok |
| yolo26-s-pose_640x640.dxnn | 37.0 | 27.01 | 27.01 | N/A | 56 | ok |
| yolo26-m-pose_640x640.dxnn | 28.7 | 34.85 | 34.85 | N/A | 56 | ok |
| yolo26-l-pose_640x640.dxnn | 23.8 | 41.97 | 41.97 | N/A | 56 | ok |
| yolo26-x-pose_640x640.dxnn | 15.0 | 66.57 | 66.57 | N/A | 57 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-seg_640x640.dxnn | 26.8 | 37.34 | 36.14 | 1.20 | 55 | ok |
| yolo26-s-seg_640x640.dxnn | 21.3 | 47.04 | 45.84 | 1.20 | 55 | ok |
| yolo26-m-seg_640x640.dxnn | 16.4 | 61.02 | 59.80 | 1.22 | 56 | ok |
| yolo26-l-seg_640x640.dxnn | 14.7 | 67.88 | 66.66 | 1.22 | 56 | ok |
| yolo26-x-seg_640x640.dxnn | 9.5 | 105.00 | 103.78 | 1.22 | 57 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-seg_640x640.dxnn | 27.7 | 36.08 | 36.08 | N/A | 55 | ok |
| yolo26-s-seg_640x640.dxnn | 22.3 | 44.88 | 44.88 | N/A | 55 | ok |
| yolo26-m-seg_640x640.dxnn | 16.9 | 59.19 | 59.19 | N/A | 56 | ok |
| yolo26-l-seg_640x640.dxnn | 15.0 | 66.89 | 66.89 | N/A | 56 | ok |
| yolo26-x-seg_640x640.dxnn | 9.8 | 102.38 | 102.38 | N/A | 57 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-obb_1024x1024.dxnn | 27.5 | 36.33 | 35.21 | 1.12 | 55 | ok |
| yolo26-s-obb_1024x1024.dxnn | 19.4 | 51.65 | 50.54 | 1.12 | 56 | ok |
| yolo26-m-obb_1024x1024.dxnn | 14.4 | 69.43 | 68.36 | 1.07 | 57 | ok |
| yolo26-l-obb_1024x1024.dxnn | 11.4 | 87.59 | 86.52 | 1.08 | 57 | ok |
| yolo26-x-obb_1024x1024.dxnn | 6.4 | 155.98 | 154.90 | 1.08 | 58 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-obb_1024x1024.dxnn | 28.5 | 35.03 | 35.03 | N/A | 55 | ok |
| yolo26-s-obb_1024x1024.dxnn | 19.8 | 50.42 | 50.42 | N/A | 56 | ok |
| yolo26-m-obb_1024x1024.dxnn | 14.6 | 68.37 | 68.37 | N/A | 57 | ok |
| yolo26-l-obb_1024x1024.dxnn | 11.5 | 87.00 | 87.00 | N/A | 57 | ok |
| yolo26-x-obb_1024x1024.dxnn | 6.5 | 154.56 | 154.56 | N/A | 58 | ok |

#### Classification

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_224x224.dxnn | 697.6 | 1.43 | 1.43 | N/A | 55 | ok |
| yolo26-s_224x224.dxnn | 486.9 | 2.05 | 2.05 | N/A | 55 | ok |
| yolo26-m_224x224.dxnn | 373.0 | 2.68 | 2.68 | N/A | 55 | ok |
| yolo26-l_224x224.dxnn | 252.5 | 3.96 | 3.96 | N/A | 55 | ok |
| yolo26-x_224x224.dxnn | 147.5 | 6.78 | 6.78 | N/A | 56 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_224x224.dxnn | 688.4 | 1.45 | 1.45 | N/A | 56 | ok |
| yolo26-s_224x224.dxnn | 488.1 | 2.05 | 2.05 | N/A | 55 | ok |
| yolo26-m_224x224.dxnn | 374.3 | 2.67 | 2.67 | N/A | 55 | ok |
| yolo26-l_224x224.dxnn | 251.6 | 3.97 | 3.97 | N/A | 55 | ok |
| yolo26-x_224x224.dxnn | 147.7 | 6.77 | 6.77 | N/A | 56 | ok |

## E2E Pipeline (Single-Stream)

### Object Detection

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | vah264dec | 3455 | 3 | 162.6 ±2.5 | 21.25 | 266 | 39.0 | 73.1 | 53~54 | 1000 | 243 | ok |
| yolo26-s_640x640.dxnn | vah264dec | 3455 | 3 | 140.3 ±0.6 | 24.63 | 242 | 63.6 | 83.9 | 64~65 | 1000 | 266 | ok |
| yolo26-m_640x640.dxnn | vah264dec | 3455 | 3 | 115.2 ±0.1 | 30.00 | 193 | 87.7 | 99.8 | 72~75 | 1000 | 294 | ok |
| yolo26-l_640x640.dxnn | vah264dec | 3455 | 3 | 87.4 ±0.3 | 39.54 | 140 | 90.1 | 100.0 | 72~76 | 1000 | 308 | ok |
| yolo26-x_640x640.dxnn | vah264dec | 3455 | 3 | 45.0 ±3.1 | 76.78 | 90 | 93.5 | 100.0 | 78~83 | 800~1000 | 401 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | vah264dec | 3455 | 3 | 181.4 ±0.7 | 19.05 | 283 | 42.4 | 75.7 | 60 | 1000 | 247 | ok |
| yolo26-s_640x640.dxnn | vah264dec | 3455 | 3 | 163.8 ±1.3 | 21.10 | 260 | 75.8 | 93.5 | 65~66 | 1000 | 287 | ok |
| yolo26-m_640x640.dxnn | vah264dec | 3455 | 3 | 116.0 ±0.7 | 29.79 | 205 | 89.5 | 100.0 | 71~75 | 1000 | 298 | ok |
| yolo26-l_640x640.dxnn | vah264dec | 3455 | 3 | 85.8 ±0.8 | 40.26 | 155 | 91.0 | 100.0 | 72~76 | 1000 | 313 | ok |
| yolo26-x_640x640.dxnn | vah264dec | 3455 | 3 | 45.2 ±3.4 | 76.37 | 98 | 93.1 | 100.0 | 78~83 | 800~1000 | 407 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n_640x640.dxnn | 162.6 | 181.4 | -18.8 | -10.4% |
| yolo26-s_640x640.dxnn | 140.3 | 163.8 | -23.5 | -14.3% |
| yolo26-m_640x640.dxnn | 115.2 | 116.0 | -0.8 | -0.7% |
| yolo26-l_640x640.dxnn | 87.4 | 85.8 | +1.6 | +1.8% |
| yolo26-x_640x640.dxnn | 45.0 | 45.2 | -0.2 | -0.5% |

### Pose Estimation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | vah264dec | 3455 | 3 | 172.9 ±0.5 | 19.98 | 237 | 43.3 | 75.3 | 60~61 | 1000 | 232 | ok |
| yolo26-s-pose_640x640.dxnn | vah264dec | 3455 | 3 | 155.4 ±1.6 | 22.24 | 223 | 75.0 | 92.4 | 64~66 | 1000 | 261 | ok |
| yolo26-m-pose_640x640.dxnn | vah264dec | 3455 | 3 | 110.4 ±0.3 | 31.30 | 142 | 88.4 | 100.0 | 72~75 | 1000 | 294 | ok |
| yolo26-l-pose_640x640.dxnn | vah264dec | 3455 | 3 | 82.4 ±0.4 | 41.95 | 118 | 90.5 | 100.0 | 72~76 | 1000 | 304 | ok |
| yolo26-x-pose_640x640.dxnn | vah264dec | 3455 | 3 | 43.9 ±3.8 | 78.74 | 72 | 93.3 | 100.0 | 78~82 | 600~1000 | 399 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | vah264dec | 3455 | 3 | 195.1 ±0.8 | 17.71 | 197 | 49.8 | 79.3 | 61~62 | 1000 | 203 | ok |
| yolo26-s-pose_640x640.dxnn | vah264dec | 3455 | 3 | 175.4 ±1.4 | 19.70 | 179 | 84.0 | 98.5 | 64~66 | 1000 | 245 | ok |
| yolo26-m-pose_640x640.dxnn | vah264dec | 3455 | 3 | 110.2 ±0.3 | 31.36 | 119 | 90.0 | 100.0 | 72~75 | 1000 | 274 | ok |
| yolo26-l-pose_640x640.dxnn | vah264dec | 3455 | 3 | 83.2 ±0.5 | 41.52 | 101 | 91.4 | 100.0 | 72~76 | 1000 | 289 | ok |
| yolo26-x-pose_640x640.dxnn | vah264dec | 3455 | 3 | 44.3 ±3.2 | 78.06 | 60 | 94.1 | 100.0 | 78~83 | 800~1000 | 382 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-pose_640x640.dxnn | 172.9 | 195.1 | -22.2 | -11.4% |
| yolo26-s-pose_640x640.dxnn | 155.4 | 175.4 | -20.0 | -11.4% |
| yolo26-m-pose_640x640.dxnn | 110.4 | 110.2 | +0.2 | +0.2% |
| yolo26-l-pose_640x640.dxnn | 82.4 | 83.2 | -0.8 | -1.0% |
| yolo26-x-pose_640x640.dxnn | 43.9 | 44.3 | -0.4 | -0.9% |

### Segmentation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | vah264dec | 3455 | 3 | 95.2 ±0.2 | 36.30 | 289 | 32.2 | 58.2 | 59~60 | 1000 | 351 | ok |
| yolo26-s-seg_640x640.dxnn | vah264dec | 3455 | 3 | 86.3 ±0.8 | 40.01 | 265 | 53.0 | 73.9 | 65~67 | 1000 | 371 | ok |
| yolo26-m-seg_640x640.dxnn | vah264dec | 3455 | 3 | 67.7 ±1.7 | 51.07 | 216 | 82.6 | 96.8 | 77~82 | 800~1000 | 401 | ok |
| yolo26-l-seg_640x640.dxnn | vah264dec | 3455 | 3 | 58.7 ±4.3 | 58.88 | 173 | 90.3 | 100.0 | 78~83 | 600~1000 | 410 | ok |
| yolo26-x-seg_640x640.dxnn | vah264dec | 3455 | 3 | 24.7 ±2.6 | 139.87 | 76 | 94.4 | 100.0 | 83~84 | 400~1000 | 516 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | vah264dec | 3455 | 3 | 106.7 ±1.0 | 32.37 | 318 | 36.8 | 58.9 | 60~61 | 1000 | 369 | ok |
| yolo26-s-seg_640x640.dxnn | vah264dec | 3455 | 3 | 98.4 ±0.7 | 35.12 | 279 | 60.9 | 80.6 | 65~67 | 1000 | 393 | ok |
| yolo26-m-seg_640x640.dxnn | vah264dec | 3455 | 3 | 70.8 ±5.2 | 48.79 | 208 | 88.7 | 100.0 | 78~82 | 600~1000 | 418 | ok |
| yolo26-l-seg_640x640.dxnn | vah264dec | 3455 | 3 | 59.8 ±4.2 | 57.81 | 169 | 91.8 | 100.0 | 78~83 | 800~1000 | 432 | ok |
| yolo26-x-seg_640x640.dxnn | vah264dec | 3455 | 3 | 24.6 ±2.9 | 140.75 | 75 | 94.8 | 100.0 | 83~84 | 400~1000 | 534 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-seg_640x640.dxnn | 95.2 | 106.7 | -11.6 | -10.8% |
| yolo26-s-seg_640x640.dxnn | 86.3 | 98.4 | -12.0 | -12.2% |
| yolo26-m-seg_640x640.dxnn | 67.7 | 70.8 | -3.2 | -4.4% |
| yolo26-l-seg_640x640.dxnn | 58.7 | 59.8 | -1.1 | -1.8% |
| yolo26-x-seg_640x640.dxnn | 24.7 | 24.6 | +0.1 | +0.6% |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | vah264dec | 2640 | 3 | 98.3 ±0.3 | 26.84 | 144 | 87.1 | 100.0 | 63~64 | 1000 | 271 | ok |
| yolo26-s-obb_1024x1024.dxnn | vah264dec | 2640 | 3 | 61.5 ±0.6 | 42.96 | 103 | 92.4 | 100.0 | 66~69 | 1000 | 306 | ok |
| yolo26-m-obb_1024x1024.dxnn | vah264dec | 2640 | 3 | 40.9 ±1.5 | 64.55 | 75 | 94.1 | 100.0 | 75~81 | 1000 | 326 | ok |
| yolo26-l-obb_1024x1024.dxnn | vah264dec | 2640 | 3 | 29.6 ±1.3 | 89.27 | 57 | 94.3 | 100.0 | 77~82 | 800~1000 | 340 | ok |
| yolo26-x-obb_1024x1024.dxnn | vah264dec | 2640 | 3 | 13.4 ±1.1 | 197.07 | 26 | 93.4 | 100.0 | 83~84 | 400~1000 | 445 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | vah264dec | 2640 | 3 | 98.0 ±0.4 | 26.95 | 145 | 86.9 | 100.0 | 63~64 | 1000 | 272 | ok |
| yolo26-s-obb_1024x1024.dxnn | vah264dec | 2640 | 3 | 61.7 ±0.9 | 42.76 | 107 | 92.1 | 100.0 | 66~69 | 1000 | 298 | ok |
| yolo26-m-obb_1024x1024.dxnn | vah264dec | 2640 | 3 | 41.1 ±1.5 | 64.15 | 78 | 93.7 | 100.0 | 75~81 | 800~1000 | 314 | ok |
| yolo26-l-obb_1024x1024.dxnn | vah264dec | 2640 | 3 | 29.7 ±1.3 | 88.86 | 58 | 94.6 | 100.0 | 77~82 | 800~1000 | 334 | ok |
| yolo26-x-obb_1024x1024.dxnn | vah264dec | 2640 | 3 | 13.4 ±1.2 | 197.62 | 25 | 93.1 | 100.0 | 83~84 | 400~1000 | 435 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-obb_1024x1024.dxnn | 98.3 | 98.0 | +0.4 | +0.4% |
| yolo26-s-obb_1024x1024.dxnn | 61.5 | 61.7 | -0.3 | -0.4% |
| yolo26-m-obb_1024x1024.dxnn | 40.9 | 41.1 | -0.2 | -0.6% |
| yolo26-l-obb_1024x1024.dxnn | 29.6 | 29.7 | -0.1 | -0.5% |
| yolo26-x-obb_1024x1024.dxnn | 13.4 | 13.4 | +0.0 | +0.3% |

### Classification

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_224x224.dxnn | vah264dec | 3455 | 3 | 276.7 ±0.5 | 12.48 | 86 | 5.7 | 21.6 | 57 | 1000 | 142 | ok |
| yolo26-s_224x224.dxnn | vah264dec | 3455 | 3 | 288.3 ±0.8 | 11.98 | 83 | 11.0 | 40.1 | 59 | 1000 | 129 | ok |
| yolo26-m_224x224.dxnn | vah264dec | 3455 | 3 | 288.4 ±1.3 | 11.98 | 83 | 15.2 | 56.7 | 62~63 | 1000 | 168 | ok |
| yolo26-l_224x224.dxnn | vah264dec | 3455 | 3 | 291.3 ±1.4 | 11.86 | 83 | 24.7 | 72.9 | 61 | 1000 | 173 | ok |
| yolo26-x_224x224.dxnn | vah264dec | 3455 | 3 | 289.4 ±0.6 | 11.94 | 83 | 45.2 | 78.6 | 64 | 1000 | 203 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_224x224.dxnn | vah264dec | 3455 | 3 | 278.3 ±1.4 | 12.41 | 86 | 5.9 | 21.6 | 57~58 | 1000 | 140 | ok |
| yolo26-s_224x224.dxnn | vah264dec | 3455 | 3 | 288.8 ±0.7 | 11.96 | 83 | 10.9 | 40.1 | 58~59 | 1000 | 142 | ok |
| yolo26-m_224x224.dxnn | vah264dec | 3455 | 3 | 289.0 ±0.5 | 11.96 | 83 | 15.3 | 57.1 | 62~63 | 1000 | 159 | ok |
| yolo26-l_224x224.dxnn | vah264dec | 3455 | 3 | 291.0 ±1.8 | 11.87 | 83 | 25.0 | 74.1 | 61 | 1000 | 173 | ok |
| yolo26-x_224x224.dxnn | vah264dec | 3455 | 3 | 289.7 ±0.1 | 11.93 | 83 | 44.5 | 77.6 | 64 | 1000 | 203 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n_224x224.dxnn | 276.7 | 278.3 | -1.6 | -0.6% |
| yolo26-s_224x224.dxnn | 288.3 | 288.8 | -0.5 | -0.2% |
| yolo26-m_224x224.dxnn | 288.4 | 289.0 | -0.6 | -0.2% |
| yolo26-l_224x224.dxnn | 291.3 | 291.0 | +0.3 | +0.1% |
| yolo26-x_224x224.dxnn | 289.4 | 289.7 | -0.3 | -0.1% |

## E2E Pipeline (Multi-Stream)

### Object Detection

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | 5 | 3 | 164.4 ±1.3 | 32.9 | 282 | 44.6 | 71.2 | 60~63 | 1000 | 440 | ok |
| yolo26-n_640x640.dxnn | 6 | 3 | 164.9 ±0.3 | 27.5 | 282 | 44.6 | 72.6 | 66~67 | 1000 | 474 | ok |
| yolo26-s_640x640.dxnn | 4 | 3 | 143.8 ±0.2 | 36.0 | 253 | 69.9 | 86.1 | 70~73 | 1000 | 418 | ok |
| yolo26-s_640x640.dxnn | 5 | 3 | 143.9 ±0.3 | 28.8 | 254 | 70.4 | 84.5 | 75~77 | 1000 | 452 | ok |
| yolo26-m_640x640.dxnn | 3 | 3 | 94.4 ±9.8 | 31.5 | 166 | 93.6 | 100.0 | 83~84 | 600~1000 | 402 | ok |
| yolo26-m_640x640.dxnn | 4 | 3 | 83.6 ±1.6 | 20.9 | 149 | 95.4 | 100.0 | 84 | 600~1000 | 440 | ok |
| yolo26-l_640x640.dxnn | 2 | 3 | 76.1 ±5.6 | 38.0 | 142 | 93.4 | 100.0 | 82~84 | 600~1000 | 378 | ok |
| yolo26-l_640x640.dxnn | 3 | 3 | 68.0 ±1.4 | 22.7 | 133 | 94.3 | 100.0 | 84 | 600~1000 | 416 | ok |
| yolo26-x_640x640.dxnn | 1 | 3 | 45.0 ±3.1 | 45.0 | 90 | 93.5 | 100.0 | 78~83 | 800~1000 | 401 | ok |
| yolo26-x_640x640.dxnn | 2 | 3 | 34.7 ±0.1 | 17.4 | 78 | 93.8 | 100.0 | 84 | 600~1000 | 475 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | 6 | 3 | 185.1 ±0.7 | 30.9 | 323 | 52.0 | 72.5 | 64~66 | 1000 | 507 | ok |
| yolo26-n_640x640.dxnn | 7 | 3 | 183.5 ±1.0 | 26.2 | 322 | 51.4 | 72.0 | 68~69 | 1000 | 545 | ok |
| yolo26-s_640x640.dxnn | 5 | 3 | 165.8 ±0.7 | 33.1 | 275 | 82.8 | 93.6 | 72~76 | 1000 | 480 | ok |
| yolo26-s_640x640.dxnn | 6 | 3 | 165.6 ±0.4 | 27.6 | 273 | 83.0 | 94.0 | 70~76 | 1000 | 525 | ok |
| yolo26-m_640x640.dxnn | 3 | 3 | 95.2 ±10.0 | 31.7 | 180 | 94.9 | 100.0 | 83~85 | 600~1000 | 417 | ok |
| yolo26-m_640x640.dxnn | 4 | 3 | 84.5 ±0.3 | 21.1 | 160 | 96.4 | 100.0 | 84~85 | 600~1000 | 462 | ok |
| yolo26-l_640x640.dxnn | 2 | 3 | 76.6 ±5.0 | 38.3 | 156 | 93.6 | 100.0 | 82~84 | 600~1000 | 394 | ok |
| yolo26-l_640x640.dxnn | 3 | 3 | 67.4 ±1.7 | 22.5 | 143 | 94.8 | 100.0 | 84 | 600~1000 | 436 | ok |
| yolo26-x_640x640.dxnn | 1 | 3 | 45.2 ±3.4 | 45.2 | 98 | 93.1 | 100.0 | 78~83 | 800~1000 | 407 | ok |
| yolo26-x_640x640.dxnn | 2 | 3 | 34.7 ±0.1 | 17.3 | 84 | 94.1 | 100.0 | 84 | 600~1000 | 482 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n_640x640.dxnn | 5 | 32.9 | 6 | 30.9 |
| yolo26-s_640x640.dxnn | 4 | 36.0 | 5 | 33.1 |
| yolo26-m_640x640.dxnn | 3 | 31.5 | 3 | 31.7 |
| yolo26-l_640x640.dxnn | 2 | 38.0 | 2 | 38.3 |
| yolo26-x_640x640.dxnn | 1 | 45.0 | 1 | 45.2 |

### Pose Estimation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 5 | 3 | 196.3 ±0.4 | 39.2 | 273 | 58.7 | 77.6 | 65~67 | 1000 | 442 | ok |
| yolo26-n-pose_640x640.dxnn | 6 | 3 | 196.2 ±0.5 | 32.7 | 274 | 59.1 | 77.7 | 70~71 | 1000 | 474 | ok |
| yolo26-n-pose_640x640.dxnn | 7 | 3 | 195.5 ±0.1 | 27.9 | 273 | 59.1 | 78.6 | 72~73 | 1000 | 507 | ok |
| yolo26-s-pose_640x640.dxnn | 5 | 3 | 159.3 ±0.2 | 31.9 | 244 | 84.2 | 93.4 | 72~76 | 1000 | 450 | ok |
| yolo26-s-pose_640x640.dxnn | 6 | 3 | 158.0 ±1.4 | 26.3 | 243 | 85.6 | 95.9 | 79~80 | 1000 | 490 | ok |
| yolo26-m-pose_640x640.dxnn | 3 | 3 | 90.6 ±7.9 | 30.2 | 144 | 93.7 | 100.0 | 83~84 | 600~1000 | 403 | ok |
| yolo26-m-pose_640x640.dxnn | 4 | 3 | 82.4 ±0.5 | 20.6 | 134 | 95.2 | 100.0 | 84 | 600~1000 | 442 | ok |
| yolo26-l-pose_640x640.dxnn | 2 | 3 | 74.7 ±2.8 | 37.3 | 126 | 94.2 | 100.0 | 82~84 | 800~1000 | 376 | ok |
| yolo26-l-pose_640x640.dxnn | 3 | 3 | 65.9 ±0.9 | 22.0 | 116 | 94.5 | 100.0 | 84 | 600~1000 | 417 | ok |
| yolo26-x-pose_640x640.dxnn | 1 | 3 | 43.9 ±3.8 | 43.9 | 72 | 93.3 | 100.0 | 78~82 | 600~1000 | 399 | ok |
| yolo26-x-pose_640x640.dxnn | 2 | 3 | 34.3 ±0.2 | 17.1 | 66 | 93.5 | 100.0 | 83~84 | 600~1000 | 472 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 6 | 3 | 232.1 ±0.3 | 38.7 | 258 | 72.1 | 85.9 | 66~69 | 1000 | 469 | ok |
| yolo26-n-pose_640x640.dxnn | 7 | 3 | 232.3 ±0.1 | 33.2 | 259 | 72.1 | 86.1 | 72~73 | 1000 | 500 | ok |
| yolo26-n-pose_640x640.dxnn | 8 | 3 | 232.2 ±0.8 | 29.0 | 259 | 72.6 | 86.1 | 74~75 | 1000 | 528 | ok |
| yolo26-s-pose_640x640.dxnn | 5 | 3 | 175.9 ±0.0 | 35.2 | 214 | 93.0 | 98.8 | 66~73 | 1000 | 437 | ok |
| yolo26-s-pose_640x640.dxnn | 6 | 3 | 173.6 ±2.9 | 28.9 | 210 | 93.2 | 99.6 | 78~80 | 1000 | 486 | ok |
| yolo26-m-pose_640x640.dxnn | 3 | 3 | 92.9 ±8.6 | 31.0 | 126 | 94.3 | 100.0 | 82~84 | 600~1000 | 387 | ok |
| yolo26-m-pose_640x640.dxnn | 4 | 3 | 83.2 ±0.6 | 20.8 | 115 | 96.0 | 100.0 | 84 | 600~1000 | 433 | ok |
| yolo26-l-pose_640x640.dxnn | 2 | 3 | 75.6 ±3.0 | 37.8 | 108 | 94.5 | 100.0 | 82~84 | 600~1000 | 361 | ok |
| yolo26-l-pose_640x640.dxnn | 3 | 3 | 66.0 ±2.0 | 22.0 | 98 | 94.6 | 100.0 | 84 | 600~1000 | 401 | ok |
| yolo26-x-pose_640x640.dxnn | 1 | 3 | 44.3 ±3.2 | 44.3 | 60 | 94.1 | 100.0 | 78~83 | 800~1000 | 382 | ok |
| yolo26-x-pose_640x640.dxnn | 2 | 3 | 34.6 ±0.4 | 17.3 | 52 | 95.0 | 100.0 | 84 | 400~800 | 455 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-pose_640x640.dxnn | 6 | 32.7 | 7 | 33.2 |
| yolo26-s-pose_640x640.dxnn | 5 | 31.9 | 5 | 35.2 |
| yolo26-m-pose_640x640.dxnn | 3 | 30.2 | 3 | 31.0 |
| yolo26-l-pose_640x640.dxnn | 2 | 37.3 | 2 | 37.8 |
| yolo26-x-pose_640x640.dxnn | 1 | 43.9 | 1 | 44.3 |

### Segmentation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 3 | 3 | 95.7 ±0.1 | 31.9 | 298 | 33.2 | 58.2 | 63~65 | 1000 | 475 | ok |
| yolo26-n-seg_640x640.dxnn | 4 | 3 | 95.9 ±0.1 | 24.0 | 299 | 33.4 | 60.6 | 66~67 | 1000 | 515 | ok |
| yolo26-s-seg_640x640.dxnn | 2 | 3 | 86.5 ±0.0 | 43.2 | 268 | 55.0 | 74.2 | 70~73 | 1000 | 454 | ok |
| yolo26-s-seg_640x640.dxnn | 3 | 3 | 86.8 ±0.1 | 28.9 | 269 | 56.0 | 75.9 | 75~77 | 1000 | 492 | ok |
| yolo26-m-seg_640x640.dxnn | 2 | 3 | 49.4 ±2.7 | 24.7 | 156 | 93.0 | 100.0 | 84 | 400~1000 | 476 | ok |
| yolo26-m-seg_640x640.dxnn | 1 | 3 | 67.7 ±1.7 | 67.7 | 216 | 82.6 | 96.8 | 77~82 | 800~1000 | 401 | ok |
| yolo26-l-seg_640x640.dxnn | 1 | 3 | 58.7 ±4.3 | 58.7 | 173 | 90.3 | 100.0 | 78~83 | 600~1000 | 410 | ok |
| yolo26-l-seg_640x640.dxnn | 2 | 3 | 41.9 ±1.2 | 20.9 | 131 | 93.9 | 100.0 | 84 | 400~1000 | 489 | ok |
| yolo26-x-seg_640x640.dxnn | 1 | 3 | 24.7 ±2.6 | 24.7 | 76 | 94.4 | 100.0 | 83~84 | 400~1000 | 516 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 3 | 3 | 106.9 ±0.4 | 35.6 | 328 | 38.0 | 60.3 | 64~66 | 1000 | 502 | ok |
| yolo26-n-seg_640x640.dxnn | 4 | 3 | 106.6 ±0.1 | 26.6 | 328 | 38.1 | 60.7 | 67~68 | 1000 | 559 | ok |
| yolo26-s-seg_640x640.dxnn | 3 | 3 | 98.6 ±0.5 | 32.9 | 286 | 64.4 | 82.7 | 73~76 | 1000 | 521 | ok |
| yolo26-s-seg_640x640.dxnn | 4 | 3 | 97.5 ±0.5 | 24.4 | 284 | 65.8 | 79.9 | 79~80 | 1000 | 578 | ok |
| yolo26-m-seg_640x640.dxnn | 2 | 3 | 48.4 ±2.9 | 24.2 | 151 | 93.1 | 100.0 | 84 | 400~1000 | 496 | ok |
| yolo26-m-seg_640x640.dxnn | 1 | 3 | 70.8 ±5.2 | 70.8 | 208 | 88.7 | 100.0 | 78~82 | 600~1000 | 418 | ok |
| yolo26-l-seg_640x640.dxnn | 1 | 3 | 59.8 ±4.2 | 59.8 | 169 | 91.8 | 100.0 | 78~83 | 800~1000 | 432 | ok |
| yolo26-l-seg_640x640.dxnn | 2 | 3 | 43.4 ±4.1 | 21.7 | 130 | 94.5 | 100.0 | 84~85 | 400~1000 | 518 | ok |
| yolo26-x-seg_640x640.dxnn | 1 | 3 | 24.6 ±2.9 | 24.6 | 75 | 94.8 | 100.0 | 83~84 | 400~1000 | 534 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-seg_640x640.dxnn | 3 | 31.9 | 3 | 35.6 |
| yolo26-s-seg_640x640.dxnn | 2 | 43.2 | 3 | 32.9 |
| yolo26-m-seg_640x640.dxnn | 1 | 67.7 | 1 | 70.8 |
| yolo26-l-seg_640x640.dxnn | 1 | 58.7 | 1 | 59.8 |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 3 | 3 | 100.1 ±0.2 | 33.4 | 180 | 93.0 | 100.0 | 69~72 | 1000 | 390 | ok |
| yolo26-n-obb_1024x1024.dxnn | 4 | 3 | 100.0 ±0.1 | 25.0 | 179 | 93.6 | 100.0 | 74~76 | 1000 | 431 | ok |
| yolo26-s-obb_1024x1024.dxnn | 2 | 3 | 61.8 ±0.4 | 30.9 | 124 | 94.5 | 100.0 | 74~76 | 1000 | 370 | ok |
| yolo26-s-obb_1024x1024.dxnn | 3 | 3 | 59.3 ±0.8 | 19.8 | 117 | 96.1 | 100.0 | 79~80 | 1000 | 414 | ok |
| yolo26-m-obb_1024x1024.dxnn | 1 | 3 | 40.9 ±1.5 | 40.9 | 75 | 94.1 | 100.0 | 75~81 | 1000 | 326 | ok |
| yolo26-m-obb_1024x1024.dxnn | 2 | 3 | 32.0 ±1.2 | 16.0 | 70 | 95.0 | 100.0 | 84 | 400~1000 | 400 | ok |
| yolo26-l-obb_1024x1024.dxnn | 1 | 3 | 29.6 ±1.3 | 29.6 | 57 | 94.3 | 100.0 | 77~82 | 800~1000 | 340 | ok |
| yolo26-x-obb_1024x1024.dxnn | 1 | 3 | 13.4 ±1.1 | 13.4 | 26 | 93.4 | 100.0 | 83~84 | 400~1000 | 445 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 3 | 3 | 99.9 ±0.3 | 33.3 | 184 | 92.9 | 100.0 | 68~71 | 1000 | 383 | ok |
| yolo26-n-obb_1024x1024.dxnn | 4 | 3 | 100.6 ±0.3 | 25.1 | 184 | 94.3 | 100.0 | 74~76 | 1000 | 431 | ok |
| yolo26-s-obb_1024x1024.dxnn | 2 | 3 | 62.7 ±0.7 | 31.3 | 128 | 94.7 | 100.0 | 74~77 | 1000 | 362 | ok |
| yolo26-s-obb_1024x1024.dxnn | 3 | 3 | 59.5 ±0.7 | 19.8 | 122 | 96.3 | 100.0 | 79~80 | 1000 | 405 | ok |
| yolo26-m-obb_1024x1024.dxnn | 1 | 3 | 41.1 ±1.5 | 41.1 | 78 | 93.7 | 100.0 | 75~81 | 800~1000 | 314 | ok |
| yolo26-m-obb_1024x1024.dxnn | 2 | 3 | 32.1 ±0.7 | 16.1 | 71 | 94.9 | 100.0 | 84 | 600~1000 | 392 | ok |
| yolo26-l-obb_1024x1024.dxnn | 1 | 3 | 29.7 ±1.3 | 29.7 | 58 | 94.6 | 100.0 | 77~82 | 800~1000 | 334 | ok |
| yolo26-x-obb_1024x1024.dxnn | 1 | 3 | 13.4 ±1.2 | 13.4 | 25 | 93.1 | 100.0 | 83~84 | 400~1000 | 435 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-obb_1024x1024.dxnn | 3 | 33.4 | 3 | 33.3 |
| yolo26-s-obb_1024x1024.dxnn | 2 | 30.9 | 2 | 31.3 |
| yolo26-m-obb_1024x1024.dxnn | 1 | 40.9 | 1 | 41.1 |

---
*Report generated by dx-benchmark tool*
