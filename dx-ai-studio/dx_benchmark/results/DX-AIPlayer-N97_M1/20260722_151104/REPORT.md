# YOLO26 Benchmark Report

**Generated:** 2026-07-28 16:50:36 (Local)

## Test Timing

| # | Type | Start | End | Duration |
|---|------|-------|-----|----------|
| 1 | run | 2026-07-22 15:11:04 | 2026-07-23 17:05:51 | 25h 54m 47s |

## Executive Summary

### Object Detection

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n_640x640.dxnn | ON | 23.52 | 240.0 | 161.2 | 5 |
| yolo26-n_640x640.dxnn | OFF | 22.35 | 314.9 | 184.9 | 6 |
| yolo26-s_640x640.dxnn | ON | 29.96 | 196.6 | 139.7 | 4 |
| yolo26-s_640x640.dxnn | OFF | 28.78 | 197.8 | 164.1 | 5 |
| yolo26-m_640x640.dxnn | ON | 37.54 | 119.8 | 114.7 | 3 |
| yolo26-m_640x640.dxnn | OFF | 36.43 | 120.1 | 116.6 | 3 |
| yolo26-l_640x640.dxnn | ON | 45.21 | 89.1 | 86.7 | 2 |
| yolo26-l_640x640.dxnn | OFF | 43.64 | 85.6 | 85.1 | 2 |
| yolo26-x_640x640.dxnn | ON | 71.15 | 48.3 | 48.4 | 1 |
| yolo26-x_640x640.dxnn | OFF | 69.57 | 47.4 | 49.0 | 1 |

### Pose Estimation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-pose_640x640.dxnn | ON | 20.63 | 293.1 | 177.1 | 6 |
| yolo26-n-pose_640x640.dxnn | OFF | 19.57 | 298.6 | 197.3 | 7 |
| yolo26-s-pose_640x640.dxnn | ON | 27.21 | 182.5 | 154.5 | 5 |
| yolo26-s-pose_640x640.dxnn | OFF | 26.35 | 182.0 | 175.2 | 5 |
| yolo26-m-pose_640x640.dxnn | ON | 35.98 | 114.6 | 110.2 | 3 |
| yolo26-m-pose_640x640.dxnn | OFF | 34.61 | 111.2 | 110.7 | 3 |
| yolo26-l-pose_640x640.dxnn | ON | 42.44 | 83.4 | 82.6 | 2 |
| yolo26-l-pose_640x640.dxnn | OFF | 42.27 | 87.2 | 83.6 | 2 |
| yolo26-x-pose_640x640.dxnn | ON | 69.32 | 46.9 | 47.4 | 1 |
| yolo26-x-pose_640x640.dxnn | OFF | 68.15 | 47.9 | 47.4 | 1 |

### Segmentation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-seg_640x640.dxnn | ON | 37.96 | 137.0 | 96.5 | 3 |
| yolo26-n-seg_640x640.dxnn | OFF | 36.58 | 180.4 | 108.3 | 3 |
| yolo26-s-seg_640x640.dxnn | ON | 46.46 | 134.8 | 86.4 | 2 |
| yolo26-s-seg_640x640.dxnn | OFF | 45.22 | 138.2 | 98.9 | 3 |
| yolo26-m-seg_640x640.dxnn | ON | 61.88 | 80.6 | 69.7 | 1 |
| yolo26-m-seg_640x640.dxnn | OFF | 60.15 | 80.4 | 76.0 | 1 |
| yolo26-l-seg_640x640.dxnn | ON | 67.95 | 64.9 | 63.1 | 1 |
| yolo26-l-seg_640x640.dxnn | OFF | 66.21 | 64.5 | 64.1 | 1 |
| yolo26-x-seg_640x640.dxnn | ON | 104.53 | 34.8 | 28.6 | — |
| yolo26-x-seg_640x640.dxnn | OFF | 104.77 | 34.2 | 28.9 | — |

### Oriented BBox (OBB)

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-obb_1024x1024.dxnn | ON | 35.00 | 103.8 | 98.9 | 3 |
| yolo26-n-obb_1024x1024.dxnn | OFF | 34.02 | 99.2 | 98.2 | 3 |
| yolo26-s-obb_1024x1024.dxnn | ON | 50.74 | 64.6 | 61.5 | 2 |
| yolo26-s-obb_1024x1024.dxnn | OFF | 48.91 | 61.3 | 61.9 | 2 |
| yolo26-m-obb_1024x1024.dxnn | ON | 68.65 | 42.3 | 41.7 | 1 |
| yolo26-m-obb_1024x1024.dxnn | OFF | 67.28 | 42.2 | 42.1 | 1 |
| yolo26-l-obb_1024x1024.dxnn | ON | 86.97 | 31.0 | 30.9 | 1 |
| yolo26-l-obb_1024x1024.dxnn | OFF | 85.76 | 31.1 | 30.9 | 1 |
| yolo26-x-obb_1024x1024.dxnn | ON | 155.20 | 17.3 | 15.0 | — |
| yolo26-x-obb_1024x1024.dxnn | OFF | 154.37 | 17.2 | 15.0 | — |

### Classification

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n_224x224.dxnn | ON | 1.44 | 3629.3 | 278.4 | — |
| yolo26-n_224x224.dxnn | OFF | 1.45 | 3629.4 | 278.6 | — |
| yolo26-s_224x224.dxnn | ON | 2.05 | 2006.3 | 289.0 | — |
| yolo26-s_224x224.dxnn | OFF | 2.11 | 2021.7 | 288.4 | — |
| yolo26-m_224x224.dxnn | ON | 2.71 | 1394.6 | 287.9 | — |
| yolo26-m_224x224.dxnn | OFF | 2.65 | 1390.6 | 288.7 | — |
| yolo26-l_224x224.dxnn | ON | 3.91 | 883.7 | 291.4 | — |
| yolo26-l_224x224.dxnn | OFF | 3.93 | 885.7 | 291.9 | — |
| yolo26-x_224x224.dxnn | ON | 6.68 | 487.9 | 290.2 | — |
| yolo26-x_224x224.dxnn | OFF | 6.65 | 488.5 | 288.9 | — |

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
| DX-AllSuite | v2.4.0 |
| Benchmark Tool | 0.1.0 |
| NPU RT | v3.4.0 |
| NPU RT (commit) | v3.4.0+5474c9f |
| NPU Driver (RT) | v2.5.1 |
| NPU Driver (PCIe) | v2.4.1 |
| NPU Firmware | v2.7.3 |
| NPU Memory | LPDDR5 5600 Mbps, 3.92GiB |
| NPU Board | M.2, Rev 1.0 |
| NPU PCIe | Gen3 X2 [03:00:00] |

### Tools

| Tool | Available | Version |
|------|-----------|---------|
| run_model | Yes | DXRT v3.4.0 run_model |
| dxrt-cli | Yes | unknown |
| gst-launch-1.0 | Yes | gst-launch-1.0 version 1.24.2 |
| gst-inspect-1.0 | Yes | gst-inspect-1.0 version 1.24.2 |
| time | Yes | unknown |
| ffprobe | Yes | ffprobe version 6.1.1-3ubuntu5 Copyright (c) 2007-2023 the F... |
| dxtop | Yes | DX-TOP 1.1.0 |

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
| Version | v3 |
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

> **Buffer-count sweep (★)** — the _Buffer-count sweep_ tables below list throughput fps per `--buffer-count`; ★ marks the winner (highest measured throughput, at full probe precision; fps rounded to 1 decimal). A smaller buffer-count wins only on an exact tie. The sweep's goal is the throughput ceiling — the winning buffer-count value itself is secondary, since tied buffer-counts deliver effectively equal throughput.

#### Object Detection

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n_640x640.dxnn | 240.0 ±1.7 | 8 | 268 | 62.5 | 81.7 | 51~54 | 1000 | ok |
| yolo26-s_640x640.dxnn | 196.6 ±0.5 | 9 | 231 | 90.8 | 100.0 | 63~65 | 1000 | ok |
| yolo26-m_640x640.dxnn | 119.8 ±1.3 | 7 | 142 | 91.6 | 100.0 | 66~70 | 1000 | ok |
| yolo26-l_640x640.dxnn | 89.1 ±0.1 | 5 | 109 | 90.6 | 100.0 | 66~70 | 1000 | ok |
| yolo26-x_640x640.dxnn | 48.3 ±0.6 | 8 | 69 | 90.4 | 100.0 | 70~74 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n_640x640.dxnn | 8 | [3]:120.8 · [4]:158.7 · [5]:178.2 · [6]:210.3 · [7]:230.8 · **[8]:240.3 ★** · [9]:235.5 |
| yolo26-s_640x640.dxnn | 9 | [3]:87.2 · [4]:120.8 · [5]:158.3 · [6]:174.1 · [7]:185.3 · [8]:192.6 · **[9]:197.9 ★** · [10]:194.3 · [11]:192.1 |
| yolo26-m_640x640.dxnn | 7 | [3]:66.5 · [4]:92.1 · [5]:119.3 · [6]:121.5 · **[7]:121.6 ★** · [8]:119.7 |
| yolo26-l_640x640.dxnn | 5 | [3]:56.0 · [4]:77.4 · **[5]:89.4 ★** · [6]:88.6 · [7]:84.8 · [8]:86.5 |
| yolo26-x_640x640.dxnn | 8 | [3]:35.7 · [4]:48.7 · [5]:46.2 · [6]:47.5 · [7]:47.0 · **[8]:48.9 ★** · [9]:48.5 · [10]:47.1 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n_640x640.dxnn | 314.9 ±1.8 | 10 | 239 | 91.1 | 99.7 | 61~63 | 1000 | ok |
| yolo26-s_640x640.dxnn | 197.8 ±0.1 | 7 | 149 | 90.7 | 100.0 | 61~64 | 1000 | ok |
| yolo26-m_640x640.dxnn | 120.1 ±0.3 | 5 | 100 | 90.3 | 100.0 | 66~70 | 1000 | ok |
| yolo26-l_640x640.dxnn | 85.6 ±0.3 | 5 | 81 | 90.3 | 100.0 | 66~70 | 1000 | ok |
| yolo26-x_640x640.dxnn | 47.4 ±0.4 | 7 | 51 | 88.8 | 100.0 | 69~72 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n_640x640.dxnn | 10 | [3]:114.0 · [4]:163.8 · [5]:204.1 · [6]:236.4 · [7]:260.5 · [8]:289.0 · [9]:308.8 · **[10]:314.7 ★** · [11]:309.9 · [12]:302.4 |
| yolo26-s_640x640.dxnn | 7 | [3]:93.5 · [4]:131.5 · [5]:174.7 · [6]:192.8 · **[7]:198.3 ★** · [8]:197.0 |
| yolo26-m_640x640.dxnn | 5 | [3]:70.2 · [4]:99.4 · **[5]:120.0 ★** · [6]:115.9 · [7]:116.5 · [8]:118.6 |
| yolo26-l_640x640.dxnn | 5 | [3]:58.3 · [4]:82.9 · **[5]:86.5 ★** · [6]:83.9 · [7]:84.8 · [8]:84.8 |
| yolo26-x_640x640.dxnn | 7 | [3]:36.9 · [4]:48.9 · [5]:46.7 · [6]:46.9 · **[7]:49.1 ★** · [8]:47.1 |


#### Pose Estimation

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 293.1 ±0.5 | 9 | 240 | 88.1 | 99.4 | 62~64 | 1000 | ok |
| yolo26-s-pose_640x640.dxnn | 182.5 ±0.2 | 6 | 156 | 90.0 | 100.0 | 62~65 | 1000 | ok |
| yolo26-m-pose_640x640.dxnn | 114.6 ±0.4 | 5 | 103 | 91.4 | 100.0 | 67~71 | 1000 | ok |
| yolo26-l-pose_640x640.dxnn | 83.4 ±0.9 | 6 | 91 | 89.8 | 100.0 | 66~70 | 1000 | ok |
| yolo26-x-pose_640x640.dxnn | 46.9 ±0.7 | 5 | 53 | 88.0 | 100.0 | 69~73 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-pose_640x640.dxnn | 9 | [3]:128.2 · [4]:177.4 · [5]:213.1 · [6]:233.9 · [7]:260.6 · [8]:283.1 · **[9]:294.7 ★** · [10]:291.9 · [11]:289.4 |
| yolo26-s-pose_640x640.dxnn | 6 | [3]:95.4 · [4]:128.3 · [5]:171.9 · **[6]:182.5 ★** · [7]:177.4 · [8]:174.3 |
| yolo26-m-pose_640x640.dxnn | 5 | [3]:70.3 · [4]:97.8 · **[5]:115.6 ★** · [6]:112.8 · [7]:112.1 · [8]:114.4 |
| yolo26-l-pose_640x640.dxnn | 6 | [3]:58.1 · [4]:79.3 · [5]:84.5 · **[6]:86.6 ★** · [7]:84.7 · [8]:83.0 |
| yolo26-x-pose_640x640.dxnn | 5 | [3]:36.9 · [4]:47.8 · **[5]:48.0 ★** · [6]:45.7 · [7]:46.9 · [8]:48.0 · [9]:46.8 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 298.6 ±0.8 | 7 | 157 | 90.5 | 99.6 | 61~63 | 1000 | ok |
| yolo26-s-pose_640x640.dxnn | 182.0 ±0.3 | 5 | 109 | 89.4 | 100.0 | 62~65 | 1000 | ok |
| yolo26-m-pose_640x640.dxnn | 111.2 ±0.9 | 7 | 80 | 91.0 | 100.0 | 67~70 | 1000 | ok |
| yolo26-l-pose_640x640.dxnn | 87.2 ±0.4 | 4 | 57 | 90.2 | 100.0 | 66~70 | 1000 | ok |
| yolo26-x-pose_640x640.dxnn | 47.9 ±0.0 | 4 | 35 | 89.9 | 100.0 | 68~72 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-pose_640x640.dxnn | 7 | [3]:134.8 · [4]:184.3 · [5]:244.9 · [6]:281.1 · **[7]:298.9 ★** · [8]:291.1 |
| yolo26-s-pose_640x640.dxnn | 5 | [3]:103.1 · [4]:143.3 · **[5]:181.7 ★** · [6]:173.1 · [7]:175.1 · [8]:177.6 |
| yolo26-m-pose_640x640.dxnn | 7 | [3]:73.1 · [4]:107.1 · [5]:109.5 · [6]:109.1 · **[7]:112.1 ★** · [8]:111.6 |
| yolo26-l-pose_640x640.dxnn | 4 | [3]:59.8 · **[4]:86.8 ★** · [5]:81.3 · [6]:82.6 · [7]:82.0 · [8]:84.5 |
| yolo26-x-pose_640x640.dxnn | 4 | [3]:37.0 · **[4]:47.7 ★** · [5]:47.1 · [6]:47.2 · [7]:45.7 · [8]:46.5 |


#### Segmentation

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 137.0 ±1.3 | 12 | 348 | 44.2 | 75.8 | 59~61 | 1000 | ok |
| yolo26-s-seg_640x640.dxnn | 134.8 ±0.9 | 10 | 335 | 87.2 | 99.8 | 65~69 | 1000 | ok |
| yolo26-m-seg_640x640.dxnn | 80.6 ±0.1 | 7 | 170 | 91.5 | 100.0 | 69~75 | 1000 | ok |
| yolo26-l-seg_640x640.dxnn | 64.9 ±0.1 | 6 | 151 | 89.8 | 100.0 | 69~73 | 1000 | ok |
| yolo26-x-seg_640x640.dxnn | 34.8 ±0.0 | 5 | 75 | 89.2 | 100.0 | 71~76 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-seg_640x640.dxnn | 12 | [3]:77.4 · [4]:93.8 · [5]:103.8 · [6]:119.6 · [7]:128.3 · [8]:132.8 · [9]:134.9 · [10]:136.4 · [11]:134.8 · **[12]:137.7 ★** |
| yolo26-s-seg_640x640.dxnn | 10 | [3]:47.9 · [4]:83.3 · [5]:93.7 · [6]:104.5 · [7]:119.5 · [8]:126.9 · [9]:132.4 · **[10]:135.1 ★** · [11]:133.4 · [12]:133.5 |
| yolo26-m-seg_640x640.dxnn | 7 | [3]:37.0 · [4]:54.9 · [5]:74.6 · [6]:78.8 · **[7]:80.3 ★** · [8]:78.8 |
| yolo26-l-seg_640x640.dxnn | 6 | [3]:34.0 · [4]:48.4 · [5]:64.0 · **[6]:64.7 ★** · [7]:64.1 · [8]:63.1 |
| yolo26-x-seg_640x640.dxnn | 5 | [3]:23.7 · [4]:33.8 · **[5]:34.7 ★** · [6]:33.7 · [7]:34.7 · [8]:34.6 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 180.4 ±0.6 | 14 | 329 | 64.6 | 84.9 | 61~63 | 1000 | ok |
| yolo26-s-seg_640x640.dxnn | 138.2 ±0.4 | 8 | 242 | 89.1 | 100.0 | 64~68 | 1000 | ok |
| yolo26-m-seg_640x640.dxnn | 80.4 ±0.4 | 7 | 135 | 90.5 | 100.0 | 69~75 | 1000 | ok |
| yolo26-l-seg_640x640.dxnn | 64.5 ±0.1 | 5 | 96 | 91.3 | 100.0 | 68~73 | 1000 | ok |
| yolo26-x-seg_640x640.dxnn | 34.2 ±0.4 | 8 | 74 | 88.9 | 100.0 | 73~77 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-seg_640x640.dxnn | 14 | [3]:58.0 · [4]:93.5 · [5]:115.3 · [6]:138.0 · [7]:153.4 · [8]:167.3 · [9]:175.2 · [10]:177.1 · [11]:174.9 · [12]:179.2 · [13]:179.8 · **[14]:180.2 ★** |
| yolo26-s-seg_640x640.dxnn | 8 | [3]:46.0 · [4]:75.3 · [5]:103.0 · [6]:111.8 · [7]:129.5 · **[8]:137.2 ★** · [9]:135.5 · [10]:136.3 |
| yolo26-m-seg_640x640.dxnn | 7 | [3]:39.0 · [4]:54.9 · [5]:74.8 · [6]:79.8 · **[7]:79.9 ★** · [8]:79.9 |
| yolo26-l-seg_640x640.dxnn | 5 | [3]:33.9 · [4]:49.0 · **[5]:64.4 ★** · [6]:64.3 · [7]:63.0 · [8]:63.9 |
| yolo26-x-seg_640x640.dxnn | 8 | [3]:23.2 · [4]:34.1 · [5]:34.5 · [6]:34.5 · [7]:33.0 · **[8]:34.7 ★** · [9]:34.0 · [10]:34.1 |


#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 103.8 ±0.2 | 5 | 99 | 91.6 | 100.0 | 61~63 | 1000 | ok |
| yolo26-s-obb_1024x1024.dxnn | 64.6 ±0.1 | 4 | 63 | 90.4 | 100.0 | 63~65 | 1000 | ok |
| yolo26-m-obb_1024x1024.dxnn | 42.3 ±0.1 | 4 | 44 | 89.3 | 100.0 | 67~71 | 1000 | ok |
| yolo26-l-obb_1024x1024.dxnn | 31.0 ±0.1 | 4 | 33 | 89.2 | 100.0 | 66~70 | 1000 | ok |
| yolo26-x-obb_1024x1024.dxnn | 17.3 ±0.0 | 4 | 20 | 87.8 | 100.0 | 69~72 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-obb_1024x1024.dxnn | 5 | [3]:67.8 · [4]:90.7 · **[5]:103.1 ★** · [6]:98.8 · [7]:97.8 · [8]:97.6 |
| yolo26-s-obb_1024x1024.dxnn | 4 | [3]:46.5 · **[4]:64.2 ★** · [5]:63.0 · [6]:59.8 · [7]:59.6 · [8]:59.8 |
| yolo26-m-obb_1024x1024.dxnn | 4 | [3]:34.9 · **[4]:41.1 ★** · [5]:41.0 · [6]:40.2 · [7]:39.4 · [8]:39.5 |
| yolo26-l-obb_1024x1024.dxnn | 4 | [3]:27.0 · **[4]:30.8 ★** · [5]:29.3 · [6]:29.5 · [7]:29.4 · [8]:29.5 |
| yolo26-x-obb_1024x1024.dxnn | 4 | [3]:15.5 · **[4]:17.2 ★** · [5]:16.5 · [6]:16.5 · [7]:16.2 · [8]:16.5 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 99.2 ±0.6 | 5 | 70 | 89.6 | 100.0 | 61~63 | 1000 | ok |
| yolo26-s-obb_1024x1024.dxnn | 61.3 ±0.7 | 4 | 43 | 90.6 | 100.0 | 62~64 | 1000 | ok |
| yolo26-m-obb_1024x1024.dxnn | 42.2 ±0.1 | 4 | 31 | 90.4 | 100.0 | 67~71 | 1000 | ok |
| yolo26-l-obb_1024x1024.dxnn | 31.1 ±0.2 | 4 | 24 | 90.0 | 100.0 | 66~70 | 1000 | ok |
| yolo26-x-obb_1024x1024.dxnn | 17.2 ±0.0 | 4 | 14 | 87.9 | 100.0 | 69~73 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-obb_1024x1024.dxnn | 5 | [3]:66.8 · [4]:94.0 · **[5]:98.8 ★** · [6]:97.6 · [7]:97.8 · [8]:97.2 |
| yolo26-s-obb_1024x1024.dxnn | 4 | [3]:47.6 · **[4]:61.0 ★** · [5]:59.4 · [6]:59.9 · [7]:60.3 · [8]:60.2 |
| yolo26-m-obb_1024x1024.dxnn | 4 | [3]:33.1 · **[4]:41.9 ★** · [5]:40.6 · [6]:39.4 · [7]:39.6 · [8]:39.6 |
| yolo26-l-obb_1024x1024.dxnn | 4 | [3]:25.8 · **[4]:30.8 ★** · [5]:30.6 · [6]:29.5 · [7]:29.5 · [8]:29.5 |
| yolo26-x-obb_1024x1024.dxnn | 4 | [3]:15.1 · **[4]:17.1 ★** · [5]:17.1 · [6]:16.5 · [7]:16.4 · [8]:16.5 |


#### Classification

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n_224x224.dxnn | 3629.3 ±2.3 | 10 | 103 | 89.2 | 96.3 | 58~59 | 1000 | ok |
| yolo26-s_224x224.dxnn | 2006.3 ±7.0 | 7 | 67 | 87.8 | 97.7 | 59~60 | 1000 | ok |
| yolo26-m_224x224.dxnn | 1394.6 ±0.7 | 4 | 41 | 88.9 | 97.1 | 63~66 | 1000 | ok |
| yolo26-l_224x224.dxnn | 883.7 ±2.7 | 4 | 26 | 89.7 | 98.1 | 62~64 | 1000 | ok |
| yolo26-x_224x224.dxnn | 487.9 ±1.1 | 4 | 15 | 89.9 | 99.1 | 64~67 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n_224x224.dxnn | 10 | [3]:1908.9 · [4]:2683.2 · [5]:3356.0 · [6]:3535.4 · [7]:3600.3 · [8]:3618.0 · [9]:3628.6 · **[10]:3633.5 ★** |
| yolo26-s_224x224.dxnn | 7 | [3]:1350.4 · [4]:1869.2 · [5]:2001.4 · [6]:2010.9 · **[7]:2014.3 ★** · [8]:2013.9 |
| yolo26-m_224x224.dxnn | 4 | [3]:1032.7 · **[4]:1396.6 ★** · [5]:1354.4 · [6]:1381.7 · [7]:1384.2 · [8]:1366.9 |
| yolo26-l_224x224.dxnn | 4 | [3]:715.4 · **[4]:887.0 ★** · [5]:876.0 · [6]:874.9 · [7]:878.5 · [8]:877.9 |
| yolo26-x_224x224.dxnn | 4 | [3]:425.8 · **[4]:489.2 ★** · [5]:484.6 · [6]:485.8 · [7]:482.6 · [8]:485.9 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n_224x224.dxnn | 3629.4 ±0.8 | 10 | 103 | 88.1 | 96.9 | 58~59 | 1000 | ok |
| yolo26-s_224x224.dxnn | 2021.7 ±1.7 | 5 | 62 | 89.3 | 97.2 | 59~60 | 1000 | ok |
| yolo26-m_224x224.dxnn | 1390.6 ±1.8 | 4 | 41 | 86.8 | 97.1 | 63~66 | 1000 | ok |
| yolo26-l_224x224.dxnn | 885.7 ±1.6 | 4 | 26 | 90.0 | 98.1 | 61~64 | 1000 | ok |
| yolo26-x_224x224.dxnn | 488.5 ±0.7 | 4 | 15 | 90.5 | 99.1 | 64~67 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n_224x224.dxnn | 10 | [3]:1905.4 · [4]:2662.1 · [5]:3304.5 · [6]:3540.3 · [7]:3592.7 · [8]:3605.1 · [9]:3632.1 · **[10]:3636.4 ★** |
| yolo26-s_224x224.dxnn | 5 | [3]:1351.0 · [4]:1865.7 · **[5]:2024.1 ★** · [6]:2007.8 · [7]:2014.3 · [8]:2016.0 |
| yolo26-m_224x224.dxnn | 4 | [3]:1031.7 · **[4]:1397.5 ★** · [5]:1384.4 · [6]:1381.4 · [7]:1386.9 · [8]:1384.1 |
| yolo26-l_224x224.dxnn | 4 | [3]:719.2 · **[4]:887.5 ★** · [5]:876.1 · [6]:876.7 · [7]:875.7 · [8]:878.7 |
| yolo26-x_224x224.dxnn | 4 | [3]:425.2 · **[4]:488.8 ★** · [5]:485.5 · [6]:484.7 · [7]:485.5 · [8]:485.0 |


### Latency (Single-Core, Sync)

#### Object Detection

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_640x640.dxnn | 42.5 ±1.7 | 23.52 | 22.22 | 1.30 | 45 | ok |
| yolo26-s_640x640.dxnn | 33.4 ±0.5 | 29.96 | 28.69 | 1.27 | 55 | ok |
| yolo26-m_640x640.dxnn | 26.6 ±1.3 | 37.54 | 36.23 | 1.31 | 55 | ok |
| yolo26-l_640x640.dxnn | 22.1 ±0.1 | 45.21 | 43.86 | 1.36 | 55 | ok |
| yolo26-x_640x640.dxnn | 14.1 ±0.6 | 71.15 | 69.77 | 1.38 | 56 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_640x640.dxnn | 44.7 ±1.8 | 22.35 | 22.35 | N/A | 55 | ok |
| yolo26-s_640x640.dxnn | 34.8 ±0.1 | 28.78 | 28.78 | N/A | 55 | ok |
| yolo26-m_640x640.dxnn | 27.4 ±0.3 | 36.43 | 36.43 | N/A | 55 | ok |
| yolo26-l_640x640.dxnn | 22.9 ±0.3 | 43.64 | 43.64 | N/A | 55 | ok |
| yolo26-x_640x640.dxnn | 14.4 ±0.4 | 69.57 | 69.57 | N/A | 56 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-pose_640x640.dxnn | 48.5 ±0.5 | 20.63 | 19.68 | 0.95 | 55 | ok |
| yolo26-s-pose_640x640.dxnn | 36.7 ±0.2 | 27.21 | 26.23 | 0.99 | 55 | ok |
| yolo26-m-pose_640x640.dxnn | 27.8 ±0.4 | 35.98 | 34.99 | 0.99 | 55 | ok |
| yolo26-l-pose_640x640.dxnn | 23.6 ±0.9 | 42.44 | 41.47 | 0.98 | 55 | ok |
| yolo26-x-pose_640x640.dxnn | 14.4 ±0.7 | 69.32 | 68.33 | 0.99 | 56 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-pose_640x640.dxnn | 51.1 ±0.8 | 19.57 | 19.57 | N/A | 55 | ok |
| yolo26-s-pose_640x640.dxnn | 38.0 ±0.3 | 26.35 | 26.35 | N/A | 55 | ok |
| yolo26-m-pose_640x640.dxnn | 28.9 ±0.9 | 34.61 | 34.61 | N/A | 55 | ok |
| yolo26-l-pose_640x640.dxnn | 23.7 ±0.4 | 42.27 | 42.27 | N/A | 55 | ok |
| yolo26-x-pose_640x640.dxnn | 14.7 ±0.0 | 68.15 | 68.15 | N/A | 56 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-seg_640x640.dxnn | 26.3 ±1.3 | 37.96 | 36.74 | 1.21 | 55 | ok |
| yolo26-s-seg_640x640.dxnn | 21.5 ±0.9 | 46.46 | 45.27 | 1.19 | 55 | ok |
| yolo26-m-seg_640x640.dxnn | 16.2 ±0.1 | 61.88 | 60.67 | 1.21 | 55 | ok |
| yolo26-l-seg_640x640.dxnn | 14.7 ±0.1 | 67.95 | 66.74 | 1.21 | 56 | ok |
| yolo26-x-seg_640x640.dxnn | 9.6 ±0.1 | 104.53 | 103.30 | 1.24 | 57 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-seg_640x640.dxnn | 27.3 ±0.6 | 36.58 | 36.58 | N/A | 55 | ok |
| yolo26-s-seg_640x640.dxnn | 22.1 ±0.4 | 45.22 | 45.22 | N/A | 55 | ok |
| yolo26-m-seg_640x640.dxnn | 16.6 ±0.4 | 60.15 | 60.15 | N/A | 56 | ok |
| yolo26-l-seg_640x640.dxnn | 15.1 ±0.1 | 66.21 | 66.21 | N/A | 56 | ok |
| yolo26-x-seg_640x640.dxnn | 9.5 ±0.4 | 104.77 | 104.77 | N/A | 57 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-obb_1024x1024.dxnn | 28.6 ±0.2 | 35.00 | 33.90 | 1.09 | 55 | ok |
| yolo26-s-obb_1024x1024.dxnn | 19.7 ±0.1 | 50.74 | 49.62 | 1.11 | 55 | ok |
| yolo26-m-obb_1024x1024.dxnn | 14.6 ±0.1 | 68.65 | 67.58 | 1.07 | 56 | ok |
| yolo26-l-obb_1024x1024.dxnn | 11.5 ±0.1 | 86.97 | 85.92 | 1.05 | 56 | ok |
| yolo26-x-obb_1024x1024.dxnn | 6.4 ±0.0 | 155.20 | 154.11 | 1.10 | 57 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-obb_1024x1024.dxnn | 29.4 ±0.6 | 34.02 | 34.02 | N/A | 55 | ok |
| yolo26-s-obb_1024x1024.dxnn | 20.4 ±0.7 | 48.91 | 48.91 | N/A | 55 | ok |
| yolo26-m-obb_1024x1024.dxnn | 14.9 ±0.1 | 67.28 | 67.28 | N/A | 56 | ok |
| yolo26-l-obb_1024x1024.dxnn | 11.7 ±0.2 | 85.76 | 85.76 | N/A | 56 | ok |
| yolo26-x-obb_1024x1024.dxnn | 6.5 ±0.0 | 154.37 | 154.37 | N/A | 58 | ok |

#### Classification

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_224x224.dxnn | 694.7 ±2.3 | 1.44 | 1.44 | N/A | 55 | ok |
| yolo26-s_224x224.dxnn | 486.9 ±7.0 | 2.05 | 2.05 | N/A | 54 | ok |
| yolo26-m_224x224.dxnn | 368.6 ±0.7 | 2.71 | 2.71 | N/A | 54 | ok |
| yolo26-l_224x224.dxnn | 255.8 ±2.7 | 3.91 | 3.91 | N/A | 55 | ok |
| yolo26-x_224x224.dxnn | 149.8 ±1.1 | 6.68 | 6.68 | N/A | 55 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_224x224.dxnn | 689.1 ±0.8 | 1.45 | 1.45 | N/A | 54 | ok |
| yolo26-s_224x224.dxnn | 475.0 ±1.7 | 2.11 | 2.11 | N/A | 54 | ok |
| yolo26-m_224x224.dxnn | 376.9 ±1.8 | 2.65 | 2.65 | N/A | 55 | ok |
| yolo26-l_224x224.dxnn | 254.5 ±1.6 | 3.93 | 3.93 | N/A | 55 | ok |
| yolo26-x_224x224.dxnn | 150.5 ±0.7 | 6.65 | 6.65 | N/A | 55 | ok |

## E2E Pipeline (Single-Stream)

### Object Detection

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | vah264dec | 3455 | 3 | 161.2 ±0.8 | 21.43 | 263 | 40.0 | 68.5 | 55~56 | 1000 | 250 | ok |
| yolo26-s_640x640.dxnn | vah264dec | 3455 | 3 | 139.7 ±0.4 | 24.73 | 241 | 63.8 | 81.2 | 57~59 | 1000 | 268 | ok |
| yolo26-m_640x640.dxnn | vah264dec | 3455 | 3 | 114.7 ±0.2 | 30.12 | 194 | 84.5 | 98.9 | 61~66 | 1000 | 294 | ok |
| yolo26-l_640x640.dxnn | vah264dec | 3455 | 3 | 86.7 ±0.3 | 39.86 | 141 | 88.1 | 100.0 | 63~69 | 1000 | 308 | ok |
| yolo26-x_640x640.dxnn | vah264dec | 3455 | 3 | 48.4 ±0.4 | 71.45 | 91 | 93.6 | 100.0 | 70~79 | 800~1000 | 401 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | vah264dec | 3455 | 3 | 184.9 ±1.4 | 18.69 | 287 | 43.6 | 75.4 | 56 | 1000 | 254 | ok |
| yolo26-s_640x640.dxnn | vah264dec | 3455 | 3 | 164.1 ±1.4 | 21.06 | 257 | 73.9 | 93.4 | 57~59 | 1000 | 278 | ok |
| yolo26-m_640x640.dxnn | vah264dec | 3455 | 3 | 116.6 ±0.6 | 29.64 | 203 | 87.6 | 100.0 | 61~66 | 1000 | 298 | ok |
| yolo26-l_640x640.dxnn | vah264dec | 3455 | 3 | 85.1 ±0.5 | 40.60 | 155 | 90.4 | 100.0 | 63~69 | 1000 | 317 | ok |
| yolo26-x_640x640.dxnn | vah264dec | 3455 | 3 | 49.0 ±0.1 | 70.47 | 99 | 93.5 | 100.0 | 70~79 | 1000 | 409 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n_640x640.dxnn | 161.2 | 184.9 | -23.6 | -12.8% |
| yolo26-s_640x640.dxnn | 139.7 | 164.1 | -24.4 | -14.8% |
| yolo26-m_640x640.dxnn | 114.7 | 116.6 | -1.9 | -1.6% |
| yolo26-l_640x640.dxnn | 86.7 | 85.1 | +1.6 | +1.8% |
| yolo26-x_640x640.dxnn | 48.4 | 49.0 | -0.7 | -1.4% |

### Pose Estimation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | vah264dec | 3455 | 3 | 177.1 ±0.9 | 19.51 | 240 | 45.5 | 77.4 | 56~57 | 1000 | 232 | ok |
| yolo26-s-pose_640x640.dxnn | vah264dec | 3455 | 3 | 154.5 ±0.4 | 22.37 | 225 | 73.4 | 92.1 | 58~60 | 1000 | 266 | ok |
| yolo26-m-pose_640x640.dxnn | vah264dec | 3455 | 3 | 110.2 ±1.2 | 31.36 | 142 | 88.2 | 100.0 | 62~67 | 1000 | 298 | ok |
| yolo26-l-pose_640x640.dxnn | vah264dec | 3455 | 3 | 82.6 ±0.2 | 41.84 | 118 | 89.3 | 100.0 | 63~69 | 1000 | 304 | ok |
| yolo26-x-pose_640x640.dxnn | vah264dec | 3455 | 3 | 47.4 ±0.0 | 72.83 | 74 | 94.6 | 100.0 | 70~79 | 1000 | 399 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | vah264dec | 3455 | 3 | 197.3 ±2.3 | 17.51 | 202 | 50.9 | 79.4 | 56~57 | 1000 | 217 | ok |
| yolo26-s-pose_640x640.dxnn | vah264dec | 3455 | 3 | 175.2 ±0.3 | 19.72 | 179 | 81.5 | 98.5 | 58~60 | 1000 | 244 | ok |
| yolo26-m-pose_640x640.dxnn | vah264dec | 3455 | 3 | 110.7 ±0.2 | 31.20 | 118 | 89.4 | 100.0 | 62~67 | 1000 | 273 | ok |
| yolo26-l-pose_640x640.dxnn | vah264dec | 3455 | 3 | 83.6 ±0.3 | 41.34 | 100 | 91.4 | 100.0 | 63~69 | 1000 | 287 | ok |
| yolo26-x-pose_640x640.dxnn | vah264dec | 3455 | 3 | 47.4 ±0.3 | 72.91 | 62 | 94.7 | 100.0 | 69~78 | 1000 | 385 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-pose_640x640.dxnn | 177.1 | 197.3 | -20.3 | -10.3% |
| yolo26-s-pose_640x640.dxnn | 154.5 | 175.2 | -20.7 | -11.8% |
| yolo26-m-pose_640x640.dxnn | 110.2 | 110.7 | -0.5 | -0.5% |
| yolo26-l-pose_640x640.dxnn | 82.6 | 83.6 | -1.0 | -1.2% |
| yolo26-x-pose_640x640.dxnn | 47.4 | 47.4 | +0.0 | +0.1% |

### Segmentation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | vah264dec | 3455 | 3 | 96.5 ±0.5 | 35.79 | 292 | 32.1 | 55.8 | 57~58 | 1000 | 346 | ok |
| yolo26-s-seg_640x640.dxnn | vah264dec | 3455 | 3 | 86.4 ±0.7 | 39.97 | 263 | 53.3 | 73.8 | 59~62 | 1000 | 367 | ok |
| yolo26-m-seg_640x640.dxnn | vah264dec | 3455 | 3 | 69.7 ±0.4 | 49.57 | 221 | 80.8 | 96.0 | 66~74 | 1000 | 400 | ok |
| yolo26-l-seg_640x640.dxnn | vah264dec | 3455 | 3 | 63.1 ±0.4 | 54.71 | 175 | 91.0 | 100.0 | 67~76 | 1000 | 410 | ok |
| yolo26-x-seg_640x640.dxnn | vah264dec | 3455 | 3 | 28.6 ±5.2 | 120.67 | 89 | 93.9 | 100.0 | 77~84 | 600~1000 | 519 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | vah264dec | 3455 | 3 | 108.3 ±0.2 | 31.91 | 315 | 35.9 | 60.5 | 57~58 | 1000 | 373 | ok |
| yolo26-s-seg_640x640.dxnn | vah264dec | 3455 | 3 | 98.9 ±0.6 | 34.94 | 277 | 61.5 | 79.9 | 59~62 | 1000 | 389 | ok |
| yolo26-m-seg_640x640.dxnn | vah264dec | 3455 | 3 | 76.0 ±0.8 | 45.49 | 215 | 87.3 | 100.0 | 66~74 | 1000 | 410 | ok |
| yolo26-l-seg_640x640.dxnn | vah264dec | 3455 | 3 | 64.1 ±0.2 | 53.90 | 172 | 91.2 | 100.0 | 67~76 | 1000 | 421 | ok |
| yolo26-x-seg_640x640.dxnn | vah264dec | 3455 | 3 | 28.9 ±5.1 | 119.47 | 88 | 93.0 | 100.0 | 77~84 | 600~1000 | 534 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-seg_640x640.dxnn | 96.5 | 108.3 | -11.8 | -10.9% |
| yolo26-s-seg_640x640.dxnn | 86.4 | 98.9 | -12.5 | -12.6% |
| yolo26-m-seg_640x640.dxnn | 69.7 | 76.0 | -6.2 | -8.2% |
| yolo26-l-seg_640x640.dxnn | 63.1 | 64.1 | -0.9 | -1.5% |
| yolo26-x-seg_640x640.dxnn | 28.6 | 28.9 | -0.3 | -1.0% |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | vah264dec | 2640 | 3 | 98.9 ±0.7 | 26.69 | 145 | 86.9 | 100.0 | 58~60 | 1000 | 270 | ok |
| yolo26-s-obb_1024x1024.dxnn | vah264dec | 2640 | 3 | 61.5 ±0.4 | 42.95 | 103 | 91.2 | 100.0 | 61~64 | 1000 | 294 | ok |
| yolo26-m-obb_1024x1024.dxnn | vah264dec | 2640 | 3 | 41.7 ±0.3 | 63.32 | 75 | 93.5 | 100.0 | 67~75 | 1000 | 324 | ok |
| yolo26-l-obb_1024x1024.dxnn | vah264dec | 2640 | 3 | 30.9 ±0.1 | 85.34 | 57 | 92.9 | 100.0 | 69~78 | 1000 | 342 | ok |
| yolo26-x-obb_1024x1024.dxnn | vah264dec | 2640 | 3 | 15.0 ±1.9 | 175.62 | 29 | 93.3 | 100.0 | 79~83 | 600~1000 | 445 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | vah264dec | 2640 | 3 | 98.2 ±0.2 | 26.89 | 146 | 87.6 | 100.0 | 58~60 | 1000 | 264 | ok |
| yolo26-s-obb_1024x1024.dxnn | vah264dec | 2640 | 3 | 61.9 ±1.0 | 42.62 | 107 | 90.3 | 100.0 | 60~64 | 1000 | 288 | ok |
| yolo26-m-obb_1024x1024.dxnn | vah264dec | 2640 | 3 | 42.1 ±0.3 | 62.77 | 78 | 94.6 | 100.0 | 67~75 | 1000 | 314 | ok |
| yolo26-l-obb_1024x1024.dxnn | vah264dec | 2640 | 3 | 30.9 ±0.1 | 85.43 | 59 | 93.9 | 100.0 | 69~77 | 1000 | 330 | ok |
| yolo26-x-obb_1024x1024.dxnn | vah264dec | 2640 | 3 | 15.0 ±2.0 | 176.53 | 28 | 93.1 | 100.0 | 79~83 | 400~1000 | 435 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-obb_1024x1024.dxnn | 98.9 | 98.2 | +0.8 | +0.8% |
| yolo26-s-obb_1024x1024.dxnn | 61.5 | 61.9 | -0.5 | -0.8% |
| yolo26-m-obb_1024x1024.dxnn | 41.7 | 42.1 | -0.4 | -0.9% |
| yolo26-l-obb_1024x1024.dxnn | 30.9 | 30.9 | +0.0 | +0.1% |
| yolo26-x-obb_1024x1024.dxnn | 15.0 | 15.0 | +0.1 | +0.5% |

### Classification

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_224x224.dxnn | vah264dec | 3455 | 3 | 278.4 ±1.7 | 12.41 | 86 | 5.8 | 21.5 | 54 | 1000 | 118 | ok |
| yolo26-s_224x224.dxnn | vah264dec | 3455 | 3 | 289.0 ±0.2 | 11.96 | 84 | 10.3 | 40.2 | 54 | 1000 | 129 | ok |
| yolo26-m_224x224.dxnn | vah264dec | 3455 | 3 | 287.9 ±2.0 | 12.00 | 83 | 14.9 | 57.5 | 55 | 1000 | 165 | ok |
| yolo26-l_224x224.dxnn | vah264dec | 3455 | 3 | 291.4 ±0.9 | 11.86 | 83 | 24.0 | 75.4 | 55 | 1000 | 167 | ok |
| yolo26-x_224x224.dxnn | vah264dec | 3455 | 3 | 290.2 ±1.0 | 11.90 | 83 | 43.3 | 78.2 | 56~57 | 1000 | 203 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_224x224.dxnn | vah264dec | 3455 | 3 | 278.6 ±1.6 | 12.40 | 86 | 5.8 | 21.5 | 54~55 | 1000 | 117 | ok |
| yolo26-s_224x224.dxnn | vah264dec | 3455 | 3 | 288.4 ±0.4 | 11.98 | 84 | 9.9 | 40.3 | 54~55 | 1000 | 132 | ok |
| yolo26-m_224x224.dxnn | vah264dec | 3455 | 3 | 288.7 ±2.0 | 11.97 | 83 | 14.4 | 57.3 | 55 | 1000 | 165 | ok |
| yolo26-l_224x224.dxnn | vah264dec | 3455 | 3 | 291.9 ±0.1 | 11.84 | 83 | 23.2 | 73.8 | 55 | 1000 | 154 | ok |
| yolo26-x_224x224.dxnn | vah264dec | 3455 | 3 | 288.9 ±1.5 | 11.96 | 83 | 45.2 | 78.1 | 56~57 | 1000 | 215 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n_224x224.dxnn | 278.4 | 278.6 | -0.2 | -0.1% |
| yolo26-s_224x224.dxnn | 289.0 | 288.4 | +0.6 | +0.2% |
| yolo26-m_224x224.dxnn | 287.9 | 288.7 | -0.8 | -0.3% |
| yolo26-l_224x224.dxnn | 291.4 | 291.9 | -0.4 | -0.1% |
| yolo26-x_224x224.dxnn | 290.2 | 288.9 | +1.4 | +0.5% |

## E2E Pipeline (Multi-Stream)

### Object Detection

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | 5 | 3 | 164.8 ±0.8 | 33.0 | 279 | 44.1 | 69.7 | 60~62 | 1000 | 439 | ok |
| yolo26-n_640x640.dxnn | 6 | 3 | 165.3 ±0.5 | 27.5 | 279 | 44.7 | 71.7 | 65 | 1000 | 472 | ok |
| yolo26-s_640x640.dxnn | 4 | 3 | 143.5 ±0.4 | 35.9 | 252 | 69.7 | 85.3 | 65~69 | 1000 | 417 | ok |
| yolo26-s_640x640.dxnn | 5 | 3 | 143.1 ±0.6 | 28.6 | 252 | 69.7 | 86.2 | 72~73 | 1000 | 447 | ok |
| yolo26-m_640x640.dxnn | 3 | 3 | 111.3 ±5.5 | 37.1 | 194 | 91.7 | 100.0 | 77~83 | 800~1000 | 402 | ok |
| yolo26-m_640x640.dxnn | 4 | 3 | 89.3 ±2.3 | 22.3 | 160 | 92.8 | 100.0 | 84 | 600~1000 | 442 | ok |
| yolo26-l_640x640.dxnn | 2 | 3 | 83.6 ±4.2 | 41.8 | 149 | 93.3 | 100.0 | 78~83 | 800~1000 | 378 | ok |
| yolo26-l_640x640.dxnn | 3 | 3 | 67.5 ±1.8 | 22.5 | 132 | 93.6 | 100.0 | 84 | 600~1000 | 417 | ok |
| yolo26-x_640x640.dxnn | 1 | 3 | 48.4 ±0.4 | 48.4 | 91 | 93.6 | 100.0 | 70~79 | 800~1000 | 401 | ok |
| yolo26-x_640x640.dxnn | 2 | 3 | 34.7 ±0.6 | 17.4 | 76 | 93.4 | 100.0 | 84 | 600~1000 | 472 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | 6 | 3 | 186.6 ±1.4 | 31.1 | 320 | 51.5 | 71.6 | 61~64 | 1000 | 512 | ok |
| yolo26-n_640x640.dxnn | 7 | 3 | 184.4 ±0.7 | 26.3 | 321 | 51.6 | 71.0 | 66~67 | 1000 | 565 | ok |
| yolo26-s_640x640.dxnn | 5 | 3 | 166.3 ±0.3 | 33.3 | 271 | 81.8 | 93.0 | 67~72 | 1000 | 512 | ok |
| yolo26-s_640x640.dxnn | 6 | 3 | 165.7 ±0.8 | 27.6 | 271 | 82.6 | 94.5 | 74~77 | 1000 | 518 | ok |
| yolo26-m_640x640.dxnn | 3 | 3 | 109.6 ±7.5 | 36.5 | 203 | 94.5 | 100.0 | 78~84 | 800~1000 | 421 | ok |
| yolo26-m_640x640.dxnn | 4 | 3 | 85.6 ±0.8 | 21.4 | 163 | 95.3 | 100.0 | 84 | 600~800 | 462 | ok |
| yolo26-l_640x640.dxnn | 2 | 3 | 82.4 ±3.4 | 41.2 | 162 | 93.5 | 100.0 | 78~83 | 800~1000 | 392 | ok |
| yolo26-l_640x640.dxnn | 3 | 3 | 66.6 ±1.0 | 22.2 | 140 | 93.7 | 100.0 | 84 | 600~1000 | 435 | ok |
| yolo26-x_640x640.dxnn | 1 | 3 | 49.0 ±0.1 | 49.0 | 99 | 93.5 | 100.0 | 70~79 | 1000 | 409 | ok |
| yolo26-x_640x640.dxnn | 2 | 3 | 35.2 ±0.6 | 17.6 | 83 | 94.3 | 100.0 | 84 | 600~1000 | 485 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n_640x640.dxnn | 5 | 33.0 | 6 | 31.1 |
| yolo26-s_640x640.dxnn | 4 | 35.9 | 5 | 33.3 |
| yolo26-m_640x640.dxnn | 3 | 37.1 | 3 | 36.5 |
| yolo26-l_640x640.dxnn | 2 | 41.8 | 2 | 41.2 |
| yolo26-x_640x640.dxnn | 1 | 48.4 | 1 | 49.0 |

### Pose Estimation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 5 | 3 | 196.4 ±0.7 | 39.3 | 272 | 57.9 | 77.3 | 62~66 | 1000 | 442 | ok |
| yolo26-n-pose_640x640.dxnn | 6 | 3 | 195.8 ±0.9 | 32.6 | 272 | 58.6 | 77.2 | 68~70 | 1000 | 472 | ok |
| yolo26-n-pose_640x640.dxnn | 7 | 3 | 195.6 ±0.5 | 27.9 | 271 | 58.7 | 78.2 | 71~72 | 1000 | 508 | ok |
| yolo26-s-pose_640x640.dxnn | 5 | 3 | 159.1 ±0.2 | 31.8 | 242 | 83.9 | 94.3 | 69~74 | 1000 | 453 | ok |
| yolo26-s-pose_640x640.dxnn | 6 | 3 | 158.7 ±0.5 | 26.5 | 242 | 84.0 | 94.4 | 78~79 | 1000 | 492 | ok |
| yolo26-m-pose_640x640.dxnn | 3 | 3 | 102.7 ±8.5 | 34.2 | 153 | 93.3 | 100.0 | 78~83 | 600~1000 | 402 | ok |
| yolo26-m-pose_640x640.dxnn | 4 | 3 | 83.1 ±0.7 | 20.8 | 133 | 95.0 | 100.0 | 84 | 600~1000 | 440 | ok |
| yolo26-l-pose_640x640.dxnn | 2 | 3 | 79.8 ±3.4 | 39.9 | 132 | 94.0 | 100.0 | 78~82 | 800~1000 | 377 | ok |
| yolo26-l-pose_640x640.dxnn | 3 | 3 | 67.3 ±2.8 | 22.4 | 116 | 94.8 | 100.0 | 84 | 600~1000 | 417 | ok |
| yolo26-x-pose_640x640.dxnn | 1 | 3 | 47.4 ±0.0 | 47.4 | 74 | 94.6 | 100.0 | 70~79 | 1000 | 399 | ok |
| yolo26-x-pose_640x640.dxnn | 2 | 3 | 35.0 ±0.4 | 17.5 | 65 | 94.3 | 100.0 | 83~84 | 600~1000 | 471 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 6 | 3 | 231.8 ±0.2 | 38.6 | 258 | 71.4 | 87.6 | 63~66 | 1000 | 467 | ok |
| yolo26-n-pose_640x640.dxnn | 7 | 3 | 232.5 ±0.3 | 33.2 | 258 | 70.7 | 86.0 | 70~72 | 1000 | 498 | ok |
| yolo26-n-pose_640x640.dxnn | 8 | 3 | 232.2 ±0.4 | 29.0 | 258 | 72.6 | 86.2 | 73~74 | 1000 | 531 | ok |
| yolo26-s-pose_640x640.dxnn | 5 | 3 | 175.9 ±0.4 | 35.2 | 212 | 91.2 | 99.0 | 69~74 | 1000 | 441 | ok |
| yolo26-s-pose_640x640.dxnn | 6 | 3 | 172.9 ±2.8 | 28.8 | 206 | 92.9 | 99.8 | 78~80 | 1000 | 482 | ok |
| yolo26-m-pose_640x640.dxnn | 3 | 3 | 104.4 ±6.6 | 34.8 | 133 | 94.8 | 100.0 | 78~84 | 800~1000 | 388 | ok |
| yolo26-m-pose_640x640.dxnn | 4 | 3 | 84.0 ±1.1 | 21.0 | 115 | 94.3 | 100.0 | 83~84 | 600~1000 | 435 | ok |
| yolo26-l-pose_640x640.dxnn | 2 | 3 | 80.8 ±3.2 | 40.4 | 111 | 93.9 | 100.0 | 77~82 | 800~1000 | 360 | ok |
| yolo26-l-pose_640x640.dxnn | 3 | 3 | 67.9 ±3.2 | 22.6 | 98 | 94.8 | 100.0 | 84 | 600~1000 | 401 | ok |
| yolo26-x-pose_640x640.dxnn | 1 | 3 | 47.4 ±0.3 | 47.4 | 62 | 94.7 | 100.0 | 69~78 | 1000 | 385 | ok |
| yolo26-x-pose_640x640.dxnn | 2 | 3 | 35.1 ±0.1 | 17.6 | 53 | 93.9 | 100.0 | 83~84 | 600~1000 | 455 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-pose_640x640.dxnn | 6 | 32.6 | 7 | 33.2 |
| yolo26-s-pose_640x640.dxnn | 5 | 31.8 | 5 | 35.2 |
| yolo26-m-pose_640x640.dxnn | 3 | 34.2 | 3 | 34.8 |
| yolo26-l-pose_640x640.dxnn | 2 | 39.9 | 2 | 40.4 |
| yolo26-x-pose_640x640.dxnn | 1 | 47.4 | 1 | 47.4 |

### Segmentation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 3 | 3 | 95.7 ±0.2 | 31.9 | 296 | 32.8 | 58.7 | 61~64 | 1000 | 476 | ok |
| yolo26-n-seg_640x640.dxnn | 4 | 3 | 96.0 ±0.1 | 24.0 | 297 | 33.4 | 59.2 | 66 | 1000 | 510 | ok |
| yolo26-s-seg_640x640.dxnn | 2 | 3 | 86.6 ±0.1 | 43.3 | 268 | 54.4 | 76.4 | 66~70 | 1000 | 454 | ok |
| yolo26-s-seg_640x640.dxnn | 3 | 3 | 87.0 ±0.4 | 29.0 | 269 | 56.0 | 75.6 | 73~75 | 1000 | 498 | ok |
| yolo26-m-seg_640x640.dxnn | 2 | 3 | 53.9 ±7.5 | 26.9 | 172 | 91.0 | 100.0 | 83~84 | 400~1000 | 479 | ok |
| yolo26-m-seg_640x640.dxnn | 1 | 3 | 69.7 ±0.4 | 69.7 | 221 | 80.8 | 96.0 | 66~74 | 1000 | 400 | ok |
| yolo26-l-seg_640x640.dxnn | 2 | 3 | 45.0 ±2.5 | 22.5 | 136 | 93.5 | 100.0 | 83~84 | 400~1000 | 492 | ok |
| yolo26-l-seg_640x640.dxnn | 1 | 3 | 63.1 ±0.4 | 63.1 | 175 | 91.0 | 100.0 | 67~76 | 1000 | 410 | ok |
| yolo26-x-seg_640x640.dxnn | 1 | 3 | 28.6 ±5.2 | 28.6 | 89 | 93.9 | 100.0 | 77~84 | 600~1000 | 519 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 3 | 3 | 107.6 ±0.2 | 35.9 | 327 | 37.6 | 62.5 | 61~64 | 1000 | 517 | ok |
| yolo26-n-seg_640x640.dxnn | 4 | 3 | 108.2 ±0.4 | 27.0 | 328 | 38.6 | 62.4 | 66~67 | 1000 | 555 | ok |
| yolo26-s-seg_640x640.dxnn | 3 | 3 | 98.8 ±0.5 | 32.9 | 284 | 64.5 | 80.8 | 70~74 | 1000 | 523 | ok |
| yolo26-s-seg_640x640.dxnn | 4 | 3 | 97.3 ±2.1 | 24.3 | 282 | 64.0 | 79.9 | 78~80 | 1000 | 572 | ok |
| yolo26-m-seg_640x640.dxnn | 2 | 3 | 52.6 ±6.0 | 26.3 | 160 | 93.1 | 100.0 | 83~84 | 400~1000 | 506 | ok |
| yolo26-m-seg_640x640.dxnn | 1 | 3 | 76.0 ±0.8 | 76.0 | 215 | 87.3 | 100.0 | 66~74 | 1000 | 410 | ok |
| yolo26-l-seg_640x640.dxnn | 2 | 3 | 44.4 ±3.0 | 22.2 | 133 | 93.8 | 100.0 | 83~84 | 400~1000 | 517 | ok |
| yolo26-l-seg_640x640.dxnn | 1 | 3 | 64.1 ±0.2 | 64.1 | 172 | 91.2 | 100.0 | 67~76 | 1000 | 421 | ok |
| yolo26-x-seg_640x640.dxnn | 1 | 3 | 28.9 ±5.1 | 28.9 | 88 | 93.0 | 100.0 | 77~84 | 600~1000 | 534 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-seg_640x640.dxnn | 3 | 31.9 | 3 | 35.9 |
| yolo26-s-seg_640x640.dxnn | 2 | 43.3 | 3 | 32.9 |
| yolo26-m-seg_640x640.dxnn | 1 | 69.7 | 1 | 76.0 |
| yolo26-l-seg_640x640.dxnn | 1 | 63.1 | 1 | 64.1 |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 3 | 3 | 100.0 ±0.3 | 33.3 | 179 | 92.7 | 100.0 | 65~69 | 1000 | 390 | ok |
| yolo26-n-obb_1024x1024.dxnn | 4 | 3 | 99.7 ±0.3 | 24.9 | 178 | 92.0 | 100.0 | 73~75 | 1000 | 431 | ok |
| yolo26-s-obb_1024x1024.dxnn | 2 | 3 | 61.6 ±0.5 | 30.8 | 122 | 93.4 | 100.0 | 70~73 | 1000 | 369 | ok |
| yolo26-s-obb_1024x1024.dxnn | 3 | 3 | 61.1 ±0.7 | 20.4 | 120 | 95.4 | 100.0 | 77~79 | 1000 | 414 | ok |
| yolo26-m-obb_1024x1024.dxnn | 1 | 3 | 41.7 ±0.3 | 41.7 | 75 | 93.5 | 100.0 | 67~75 | 1000 | 324 | ok |
| yolo26-m-obb_1024x1024.dxnn | 2 | 3 | 34.5 ±1.9 | 17.2 | 73 | 93.8 | 100.0 | 83~84 | 600~1000 | 399 | ok |
| yolo26-l-obb_1024x1024.dxnn | 1 | 3 | 30.9 ±0.1 | 30.9 | 57 | 92.9 | 100.0 | 69~78 | 1000 | 342 | ok |
| yolo26-l-obb_1024x1024.dxnn | 2 | 3 | 25.8 ±0.4 | 12.9 | 54 | 94.6 | 100.0 | 84 | 600~1000 | 415 | ok |
| yolo26-x-obb_1024x1024.dxnn | 1 | 3 | 15.0 ±1.9 | 15.0 | 29 | 93.3 | 100.0 | 79~83 | 600~1000 | 445 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 3 | 3 | 99.9 ±0.3 | 33.3 | 183 | 92.8 | 100.0 | 66~70 | 1000 | 384 | ok |
| yolo26-n-obb_1024x1024.dxnn | 4 | 3 | 100.3 ±0.4 | 25.1 | 183 | 93.9 | 100.0 | 73~74 | 1000 | 430 | ok |
| yolo26-s-obb_1024x1024.dxnn | 2 | 3 | 62.8 ±0.3 | 31.4 | 126 | 94.2 | 100.0 | 70~74 | 1000 | 362 | ok |
| yolo26-s-obb_1024x1024.dxnn | 3 | 3 | 61.7 ±1.1 | 20.6 | 123 | 96.0 | 100.0 | 77~79 | 1000 | 405 | ok |
| yolo26-m-obb_1024x1024.dxnn | 1 | 3 | 42.1 ±0.3 | 42.1 | 78 | 94.6 | 100.0 | 67~75 | 1000 | 314 | ok |
| yolo26-m-obb_1024x1024.dxnn | 2 | 3 | 34.5 ±2.1 | 17.2 | 73 | 95.1 | 100.0 | 83~84 | 400~1000 | 392 | ok |
| yolo26-l-obb_1024x1024.dxnn | 1 | 3 | 30.9 ±0.1 | 30.9 | 59 | 93.9 | 100.0 | 69~77 | 1000 | 330 | ok |
| yolo26-l-obb_1024x1024.dxnn | 2 | 3 | 25.5 ±0.8 | 12.8 | 54 | 95.5 | 100.0 | 84 | 400~1000 | 409 | ok |
| yolo26-x-obb_1024x1024.dxnn | 1 | 3 | 15.0 ±2.0 | 15.0 | 28 | 93.1 | 100.0 | 79~83 | 400~1000 | 435 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-obb_1024x1024.dxnn | 3 | 33.3 | 3 | 33.3 |
| yolo26-s-obb_1024x1024.dxnn | 2 | 30.8 | 2 | 31.4 |
| yolo26-m-obb_1024x1024.dxnn | 1 | 41.7 | 1 | 42.1 |
| yolo26-l-obb_1024x1024.dxnn | 1 | 30.9 | 1 | 30.9 |

---
*Report generated by dx-benchmark tool*
