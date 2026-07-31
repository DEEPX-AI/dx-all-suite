# YOLO26 Benchmark Report

**Generated:** 2026-07-29 10:29:14 (Local)

## Test Timing

| # | Type | Start | End | Duration |
|---|------|-------|-----|----------|
| 1 | run | 2026-07-22 16:53:55 | 2026-07-23 16:59:18 | 24h 5m 23s |

## Executive Summary

### Object Detection

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n_640x640.dxnn | ON | 33.74 | 180.8 | 148.1 | 4 |
| yolo26-n_640x640.dxnn | OFF | 37.07 | 320.3 | 99.6 | 3 |
| yolo26-s_640x640.dxnn | ON | 48.85 | 180.9 | 125.0 | 4 |
| yolo26-s_640x640.dxnn | OFF | 44.01 | 197.6 | 100.0 | 3 |
| yolo26-m_640x640.dxnn | ON | 56.30 | 119.3 | 98.5 | 3 |
| yolo26-m_640x640.dxnn | OFF | 42.93 | 117.4 | 98.6 | 3 |
| yolo26-l_640x640.dxnn | ON | 78.32 | 89.5 | 80.1 | 2 |
| yolo26-l_640x640.dxnn | OFF | 57.78 | 87.2 | 87.8 | 2 |
| yolo26-x_640x640.dxnn | ON | 101.68 | 48.7 | 48.1 | 1 |
| yolo26-x_640x640.dxnn | OFF | 86.21 | 48.0 | 47.8 | 1 |

### Pose Estimation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-pose_640x640.dxnn | ON | 29.04 | 288.8 | 200.7 | 6 |
| yolo26-n-pose_640x640.dxnn | OFF | 24.88 | 296.8 | 243.4 | 8 |
| yolo26-s-pose_640x640.dxnn | ON | 39.99 | 181.5 | 150.6 | 5 |
| yolo26-s-pose_640x640.dxnn | OFF | 33.48 | 180.1 | 169.5 | 5 |
| yolo26-m-pose_640x640.dxnn | ON | 56.39 | 114.8 | 107.2 | 3 |
| yolo26-m-pose_640x640.dxnn | OFF | 43.29 | 113.4 | 111.1 | 3 |
| yolo26-l-pose_640x640.dxnn | ON | 67.47 | 86.4 | 84.0 | 2 |
| yolo26-l-pose_640x640.dxnn | OFF | 49.43 | 85.4 | 83.9 | 2 |
| yolo26-x-pose_640x640.dxnn | ON | 89.40 | 47.3 | 47.1 | 1 |
| yolo26-x-pose_640x640.dxnn | OFF | 77.43 | 47.5 | 47.3 | 1 |

### Segmentation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-seg_640x640.dxnn | ON | 54.17 | 131.3 | 101.5 | 3 |
| yolo26-n-seg_640x640.dxnn | OFF | 44.04 | 191.3 | 84.1 | 2 |
| yolo26-s-seg_640x640.dxnn | ON | 59.44 | 132.6 | 87.4 | 2 |
| yolo26-s-seg_640x640.dxnn | OFF | 53.66 | 140.0 | 83.7 | 2 |
| yolo26-m-seg_640x640.dxnn | ON | 77.03 | 80.4 | 65.5 | 1 |
| yolo26-m-seg_640x640.dxnn | OFF | 68.17 | 80.8 | 74.9 | 2 |
| yolo26-l-seg_640x640.dxnn | ON | 80.36 | 64.8 | 57.4 | 1 |
| yolo26-l-seg_640x640.dxnn | OFF | 76.60 | 64.5 | 63.4 | 1 |
| yolo26-x-seg_640x640.dxnn | ON | 125.38 | 34.4 | 31.8 | 1 |
| yolo26-x-seg_640x640.dxnn | OFF | 117.92 | 34.4 | 32.1 | 1 |

### Oriented BBox (OBB)

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-obb_1024x1024.dxnn | ON | 63.22 | 103.3 | 91.8 | 3 |
| yolo26-n-obb_1024x1024.dxnn | OFF | 44.57 | 99.0 | 100.0 | 3 |
| yolo26-s-obb_1024x1024.dxnn | ON | 72.60 | 62.5 | 61.5 | 2 |
| yolo26-s-obb_1024x1024.dxnn | OFF | 62.25 | 60.4 | 62.3 | 2 |
| yolo26-m-obb_1024x1024.dxnn | ON | 93.27 | 41.9 | 41.3 | 1 |
| yolo26-m-obb_1024x1024.dxnn | OFF | 80.56 | 42.2 | 41.7 | 1 |
| yolo26-l-obb_1024x1024.dxnn | ON | 105.00 | 30.9 | 30.3 | 1 |
| yolo26-l-obb_1024x1024.dxnn | OFF | 97.55 | 30.9 | 30.2 | 1 |
| yolo26-x-obb_1024x1024.dxnn | ON | 189.52 | 16.9 | 16.7 | — |
| yolo26-x-obb_1024x1024.dxnn | OFF | 173.76 | 17.1 | 16.8 | — |

### Classification

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n_224x224.dxnn | ON | 2.63 | 3643.7 | 1072.7 | — |
| yolo26-n_224x224.dxnn | OFF | 3.93 | 3603.2 | 1071.0 | — |
| yolo26-s_224x224.dxnn | ON | 4.86 | 2023.1 | 1060.3 | — |
| yolo26-s_224x224.dxnn | OFF | 4.85 | 2021.9 | 1060.8 | — |
| yolo26-m_224x224.dxnn | ON | 5.49 | 1392.7 | 1073.2 | — |
| yolo26-m_224x224.dxnn | OFF | 5.44 | 1393.2 | 1062.3 | — |
| yolo26-l_224x224.dxnn | ON | 6.82 | 877.0 | 864.2 | — |
| yolo26-l_224x224.dxnn | OFF | 6.96 | 877.6 | 862.5 | — |
| yolo26-x_224x224.dxnn | ON | 9.51 | 484.7 | 481.2 | — |
| yolo26-x_224x224.dxnn | OFF | 9.64 | 485.9 | 481.6 | — |

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
| DX-AllSuite | v2.4.0 |
| Benchmark Tool | 0.1.0 |
| NPU RT | v3.4.0 |
| NPU RT (commit) | v3.4.0+5474c9f |
| NPU Driver (RT) | v2.5.1 |
| NPU Driver (PCIe) | v2.4.1 |
| NPU Firmware | v2.7.3 |
| NPU Memory | LPDDR5 5600 Mbps, 3.92GiB |
| NPU Board | M.2, Rev 1.0 |
| NPU PCIe | Gen3 X4 [01:00:00] |

### Tools

| Tool | Available | Version |
|------|-----------|---------|
| run_model | Yes | DXRT v3.4.0 run_model |
| dxrt-cli | Yes | unknown |
| gst-launch-1.0 | Yes | gst-launch-1.0 version 1.22.0 |
| gst-inspect-1.0 | Yes | gst-inspect-1.0 version 1.22.0 |
| time | Yes | unknown |
| ffprobe | Yes | ffprobe version 5.1.3-4 Copyright (c) 2007-2022 the FFmpeg d... |
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
| Version | v1 |
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
| yolo26-n_640x640.dxnn | 180.8 ±1.7 | 7 | 219 | 43.0 | 71.5 | 46~48 | 1000 | ok |
| yolo26-s_640x640.dxnn | 180.9 ±4.4 | 8 | 208 | 82.6 | 95.0 | 57~60 | 1000 | ok |
| yolo26-m_640x640.dxnn | 119.3 ±1.5 | 9 | 174 | 89.2 | 100.0 | 65~69 | 1000 | ok |
| yolo26-l_640x640.dxnn | 89.5 ±0.1 | 6 | 156 | 88.9 | 100.0 | 63~67 | 1000 | ok |
| yolo26-x_640x640.dxnn | 48.7 ±0.1 | 6 | 120 | 89.3 | 100.0 | 64~68 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n_640x640.dxnn | 7 | [3]:101.2 · [4]:151.2 · [5]:174.3 · [6]:178.3 · **[7]:181.0 ★** · [8]:177.5 |
| yolo26-s_640x640.dxnn | 8 | [3]:70.8 · [4]:107.3 · [5]:140.7 · [6]:171.2 · [7]:171.9 · **[8]:185.3 ★** · [9]:171.4 |
| yolo26-m_640x640.dxnn | 9 | [3]:53.4 · [4]:76.2 · [5]:100.0 · [6]:116.5 · [7]:118.0 · [8]:118.3 · **[9]:122.0 ★** · [10]:119.0 |
| yolo26-l_640x640.dxnn | 6 | [3]:44.7 · [4]:61.2 · [5]:79.5 · **[6]:89.6 ★** · [7]:88.9 · [8]:87.1 |
| yolo26-x_640x640.dxnn | 6 | [3]:27.8 · [4]:40.0 · [5]:48.1 · **[6]:48.8 ★** · [7]:48.7 · [8]:46.8 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n_640x640.dxnn | 320.3 ±0.9 | 8 | 180 | 90.8 | 100.0 | 56~58 | 1000 | ok |
| yolo26-s_640x640.dxnn | 197.6 ±1.2 | 7 | 139 | 90.4 | 100.0 | 58~61 | 1000 | ok |
| yolo26-m_640x640.dxnn | 117.4 ±0.9 | 8 | 108 | 88.9 | 100.0 | 65~69 | 1000 | ok |
| yolo26-l_640x640.dxnn | 87.2 ±1.2 | 8 | 113 | 89.5 | 100.0 | 62~66 | 1000 | ok |
| yolo26-x_640x640.dxnn | 48.0 ±0.5 | 5 | 80 | 88.0 | 100.0 | 64~68 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n_640x640.dxnn | 8 | [3]:128.7 · [4]:176.5 · [5]:236.8 · [6]:273.1 · [7]:306.2 · **[8]:316.7 ★** · [9]:309.1 |
| yolo26-s_640x640.dxnn | 7 | [3]:81.9 · [4]:136.1 · [5]:171.6 · [6]:195.1 · **[7]:197.8 ★** · [8]:196.2 |
| yolo26-m_640x640.dxnn | 8 | [3]:62.3 · [4]:87.3 · [5]:113.4 · [6]:118.9 · [7]:116.5 · **[8]:119.9 ★** · [9]:118.2 · [10]:119.2 |
| yolo26-l_640x640.dxnn | 8 | [3]:53.5 · [4]:71.3 · [5]:86.3 · [6]:87.4 · [7]:85.0 · **[8]:88.3 ★** · [9]:84.9 |
| yolo26-x_640x640.dxnn | 5 | [3]:34.0 · [4]:45.8 · **[5]:48.6 ★** · [6]:46.9 · [7]:47.4 · [8]:47.7 |


#### Pose Estimation

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 288.8 ±1.1 | 8 | 235 | 87.8 | 97.7 | 57~60 | 1000 | ok |
| yolo26-s-pose_640x640.dxnn | 181.5 ±0.6 | 7 | 179 | 90.8 | 100.0 | 58~61 | 1000 | ok |
| yolo26-m-pose_640x640.dxnn | 114.8 ±0.5 | 6 | 157 | 89.8 | 100.0 | 63~67 | 1000 | ok |
| yolo26-l-pose_640x640.dxnn | 86.4 ±0.4 | 6 | 132 | 89.0 | 100.0 | 62~65 | 1000 | ok |
| yolo26-x-pose_640x640.dxnn | 47.3 ±0.3 | 5 | 96 | 88.5 | 100.0 | 64~67 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-pose_640x640.dxnn | 8 | [3]:107.1 · [4]:161.2 · [5]:211.0 · [6]:251.1 · [7]:279.5 · **[8]:289.3 ★** · [9]:283.9 · [10]:281.9 |
| yolo26-s-pose_640x640.dxnn | 7 | [3]:81.5 · [4]:116.1 · [5]:156.3 · [6]:177.7 · **[7]:181.7 ★** · [8]:175.2 |
| yolo26-m-pose_640x640.dxnn | 6 | [3]:55.4 · [4]:84.9 · [5]:106.7 · **[6]:114.2 ★** · [7]:110.0 · [8]:112.2 |
| yolo26-l-pose_640x640.dxnn | 6 | [3]:42.8 · [4]:67.4 · [5]:86.3 · **[6]:87.7 ★** · [7]:85.5 · [8]:81.6 |
| yolo26-x-pose_640x640.dxnn | 5 | [3]:30.0 · [4]:43.0 · **[5]:46.8 ★** · [6]:46.5 · [7]:45.7 · [8]:45.8 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 296.8 ±1.0 | 7 | 148 | 90.0 | 99.7 | 57~59 | 1000 | ok |
| yolo26-s-pose_640x640.dxnn | 180.1 ±0.9 | 6 | 120 | 90.2 | 100.0 | 58~61 | 1000 | ok |
| yolo26-m-pose_640x640.dxnn | 113.4 ±1.3 | 5 | 108 | 89.4 | 100.0 | 63~67 | 1000 | ok |
| yolo26-l-pose_640x640.dxnn | 85.4 ±0.6 | 6 | 94 | 91.6 | 100.0 | 62~66 | 1000 | ok |
| yolo26-x-pose_640x640.dxnn | 47.5 ±0.1 | 4 | 54 | 88.6 | 100.0 | 64~68 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-pose_640x640.dxnn | 7 | [3]:136.8 · [4]:198.1 · [5]:244.9 · [6]:287.0 · **[7]:294.5 ★** · [8]:291.2 |
| yolo26-s-pose_640x640.dxnn | 6 | [3]:87.2 · [4]:127.5 · [5]:173.1 · **[6]:179.6 ★** · [7]:176.0 · [8]:178.1 |
| yolo26-m-pose_640x640.dxnn | 5 | [3]:67.8 · [4]:93.3 · **[5]:113.2 ★** · [6]:111.3 · [7]:112.2 · [8]:113.0 |
| yolo26-l-pose_640x640.dxnn | 6 | [3]:57.0 · [4]:78.1 · [5]:82.4 · **[6]:85.9 ★** · [7]:81.9 · [8]:83.6 |
| yolo26-x-pose_640x640.dxnn | 4 | [3]:35.2 · **[4]:47.1 ★** · [5]:46.7 · [6]:45.8 · [7]:45.6 · [8]:46.9 |


#### Segmentation

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 131.3 ±1.6 | 7 | 265 | 41.5 | 69.5 | 54~56 | 1000 | ok |
| yolo26-s-seg_640x640.dxnn | 132.6 ±0.8 | 8 | 276 | 86.9 | 97.6 | 61~65 | 1000 | ok |
| yolo26-m-seg_640x640.dxnn | 80.4 ±0.1 | 7 | 183 | 89.3 | 100.0 | 67~73 | 1000 | ok |
| yolo26-l-seg_640x640.dxnn | 64.8 ±0.1 | 7 | 158 | 89.3 | 100.0 | 64~68 | 1000 | ok |
| yolo26-x-seg_640x640.dxnn | 34.4 ±0.2 | 8 | 111 | 89.0 | 100.0 | 67~71 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-seg_640x640.dxnn | 7 | [3]:59.3 · [4]:98.5 · [5]:121.0 · [6]:131.6 · **[7]:132.6 ★** · [8]:131.9 |
| yolo26-s-seg_640x640.dxnn | 8 | [3]:48.6 · [4]:68.8 · [5]:93.0 · [6]:111.5 · [7]:129.7 · **[8]:133.2 ★** · [9]:132.1 · [10]:132.8 |
| yolo26-m-seg_640x640.dxnn | 7 | [3]:35.3 · [4]:50.8 · [5]:64.8 · [6]:77.0 · **[7]:79.5 ★** · [8]:79.5 |
| yolo26-l-seg_640x640.dxnn | 7 | [3]:31.3 · [4]:44.2 · [5]:57.3 · [6]:63.9 · **[7]:64.0 ★** · [8]:64.0 |
| yolo26-x-seg_640x640.dxnn | 8 | [3]:21.3 · [4]:29.5 · [5]:34.1 · [6]:33.6 · [7]:34.1 · **[8]:34.7 ★** · [9]:33.5 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 191.3 ±0.1 | 8 | 213 | 64.6 | 83.0 | 56~59 | 1000 | ok |
| yolo26-s-seg_640x640.dxnn | 140.0 ±0.5 | 7 | 193 | 89.1 | 100.0 | 60~64 | 1000 | ok |
| yolo26-m-seg_640x640.dxnn | 80.8 ±0.1 | 7 | 131 | 89.4 | 100.0 | 67~72 | 1000 | ok |
| yolo26-l-seg_640x640.dxnn | 64.5 ±0.4 | 8 | 124 | 89.1 | 100.0 | 66~70 | 1000 | ok |
| yolo26-x-seg_640x640.dxnn | 34.4 ±0.4 | 7 | 83 | 88.6 | 100.0 | 66~70 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-seg_640x640.dxnn | 8 | [3]:81.3 · [4]:115.0 · [5]:139.0 · [6]:180.8 · [7]:188.8 · **[8]:189.7 ★** · [9]:150.5 |
| yolo26-s-seg_640x640.dxnn | 7 | [3]:58.1 · [4]:79.1 · [5]:107.7 · [6]:133.9 · **[7]:140.0 ★** · [8]:138.1 |
| yolo26-m-seg_640x640.dxnn | 7 | [3]:40.4 · [4]:57.6 · [5]:71.2 · [6]:79.3 · **[7]:80.4 ★** · [8]:80.3 |
| yolo26-l-seg_640x640.dxnn | 8 | [3]:35.6 · [4]:50.4 · [5]:61.6 · [6]:63.9 · [7]:63.9 · **[8]:64.7 ★** · [9]:63.8 · [10]:63.2 |
| yolo26-x-seg_640x640.dxnn | 7 | [3]:23.6 · [4]:32.9 · [5]:33.7 · [6]:34.0 · **[7]:34.6 ★** · [8]:33.9 |


#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 103.3 ±0.2 | 6 | 163 | 89.3 | 100.0 | 55~57 | 1000 | ok |
| yolo26-s-obb_1024x1024.dxnn | 62.5 ±0.4 | 6 | 119 | 92.1 | 100.0 | 57~59 | 1000 | ok |
| yolo26-m-obb_1024x1024.dxnn | 41.9 ±0.4 | 5 | 98 | 89.7 | 100.0 | 62~65 | 1000 | ok |
| yolo26-l-obb_1024x1024.dxnn | 30.9 ±0.0 | 5 | 81 | 88.0 | 100.0 | 61~64 | 1000 | ok |
| yolo26-x-obb_1024x1024.dxnn | 16.9 ±0.1 | 4 | 52 | 86.9 | 100.0 | 64~67 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-obb_1024x1024.dxnn | 6 | [3]:50.7 · [4]:74.6 · [5]:94.8 · **[6]:102.9 ★** · [7]:99.8 · [8]:97.6 |
| yolo26-s-obb_1024x1024.dxnn | 6 | [3]:36.1 · [4]:48.2 · [5]:63.1 · **[6]:63.9 ★** · [7]:60.7 · [8]:59.9 |
| yolo26-m-obb_1024x1024.dxnn | 5 | [3]:27.2 · [4]:37.6 · **[5]:42.1 ★** · [6]:39.5 · [7]:39.7 · [8]:39.4 |
| yolo26-l-obb_1024x1024.dxnn | 5 | [3]:22.7 · [4]:29.4 · **[5]:30.6 ★** · [6]:29.4 · [7]:29.5 · [8]:29.5 |
| yolo26-x-obb_1024x1024.dxnn | 4 | [3]:13.9 · **[4]:16.8 ★** · [5]:16.4 · [6]:16.4 · [7]:16.4 · [8]:16.4 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 99.0 ±0.3 | 6 | 114 | 90.5 | 100.0 | 55~57 | 1000 | ok |
| yolo26-s-obb_1024x1024.dxnn | 60.4 ±0.5 | 7 | 86 | 90.0 | 100.0 | 57~59 | 1000 | ok |
| yolo26-m-obb_1024x1024.dxnn | 42.2 ±0.2 | 5 | 57 | 89.4 | 100.0 | 63~66 | 1000 | ok |
| yolo26-l-obb_1024x1024.dxnn | 30.9 ±0.0 | 4 | 44 | 87.8 | 100.0 | 61~64 | 1000 | ok |
| yolo26-x-obb_1024x1024.dxnn | 17.1 ±0.0 | 4 | 27 | 87.7 | 100.0 | 64~67 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-obb_1024x1024.dxnn | 6 | [3]:57.9 · [4]:78.3 · [5]:99.2 · **[6]:100.9 ★** · [7]:97.8 · [8]:97.8 |
| yolo26-s-obb_1024x1024.dxnn | 7 | [3]:42.8 · [4]:55.6 · [5]:62.2 · [6]:59.7 · **[7]:63.3 ★** · [8]:59.9 |
| yolo26-m-obb_1024x1024.dxnn | 5 | [3]:31.2 · [4]:40.5 · **[5]:42.1 ★** · [6]:39.5 · [7]:39.6 · [8]:41.2 |
| yolo26-l-obb_1024x1024.dxnn | 4 | [3]:24.5 · **[4]:30.7 ★** · [5]:29.6 · [6]:30.5 · [7]:29.5 · [8]:30.1 |
| yolo26-x-obb_1024x1024.dxnn | 4 | [3]:14.2 · **[4]:17.0 ★** · [5]:16.4 · [6]:16.5 · [7]:16.4 · [8]:16.6 |


#### Classification

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n_224x224.dxnn | 3643.7 ±1.8 | 10 | 112 | 85.6 | 96.6 | 53~54 | 1000 | ok |
| yolo26-s_224x224.dxnn | 2023.1 ±4.1 | 8 | 72 | 90.9 | 97.4 | 54~56 | 1000 | ok |
| yolo26-m_224x224.dxnn | 1392.7 ±1.4 | 9 | 67 | 86.7 | 97.7 | 58~61 | 1000 | ok |
| yolo26-l_224x224.dxnn | 877.0 ±0.4 | 7 | 54 | 90.4 | 98.4 | 56~58 | 1000 | ok |
| yolo26-x_224x224.dxnn | 484.7 ±0.7 | 7 | 39 | 90.9 | 99.3 | 58~60 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n_224x224.dxnn | 10 | [3]:1364.4 · [4]:2182.1 · [5]:2835.4 · [6]:3410.6 · [7]:3556.3 · [8]:3596.4 · [9]:3632.0 · **[10]:3633.3 ★** |
| yolo26-s_224x224.dxnn | 8 | [3]:829.8 · [4]:1288.9 · [5]:1751.8 · [6]:1965.0 · [7]:2025.0 · **[8]:2026.2 ★** · [9]:2023.0 · [10]:2022.6 |
| yolo26-m_224x224.dxnn | 9 | [3]:620.0 · [4]:1033.6 · [5]:1275.4 · [6]:1369.8 · [7]:1390.5 · [8]:1392.0 · **[9]:1395.5 ★** · [10]:1393.5 |
| yolo26-l_224x224.dxnn | 7 | [3]:463.0 · [4]:687.2 · [5]:861.5 · [6]:879.3 · **[7]:879.4 ★** · [8]:877.9 |
| yolo26-x_224x224.dxnn | 7 | [3]:318.4 · [4]:432.0 · [5]:484.0 · [6]:485.3 · **[7]:485.8 ★** · [8]:485.1 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n_224x224.dxnn | 3603.2 ±1.7 | 8 | 107 | 85.4 | 96.1 | 52~53 | 1000 | ok |
| yolo26-s_224x224.dxnn | 2021.9 ±5.2 | 9 | 72 | 89.3 | 97.4 | 54~56 | 1000 | ok |
| yolo26-m_224x224.dxnn | 1393.2 ±1.1 | 8 | 67 | 88.3 | 97.8 | 59~61 | 1000 | ok |
| yolo26-l_224x224.dxnn | 877.6 ±1.0 | 6 | 54 | 89.9 | 98.8 | 57~58 | 1000 | ok |
| yolo26-x_224x224.dxnn | 485.9 ±0.4 | 5 | 41 | 90.5 | 99.1 | 58~61 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n_224x224.dxnn | 8 | [3]:1312.4 · [4]:2161.4 · [5]:2913.5 · [6]:3400.8 · [7]:3549.6 · **[8]:3573.2 ★** · [9]:0.0 |
| yolo26-s_224x224.dxnn | 9 | [3]:832.0 · [4]:1285.4 · [5]:1752.8 · [6]:1955.8 · [7]:2026.0 · [8]:2026.6 · **[9]:2027.0 ★** · [10]:2026.2 |
| yolo26-m_224x224.dxnn | 8 | [3]:622.3 · [4]:994.6 · [5]:1295.0 · [6]:1374.0 · [7]:1389.4 · **[8]:1396.7 ★** · [9]:1392.8 · [10]:1395.0 |
| yolo26-l_224x224.dxnn | 6 | [3]:464.5 · [4]:716.9 · [5]:861.9 · **[6]:878.8 ★** · [7]:877.3 · [8]:877.3 |
| yolo26-x_224x224.dxnn | 5 | [3]:317.8 · [4]:431.6 · **[5]:487.7 ★** · [6]:484.5 · [7]:485.5 · [8]:484.5 |


### Latency (Single-Core, Sync)

#### Object Detection

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_640x640.dxnn | 29.6 ±1.7 | 33.74 | 27.75 | 5.99 | 39 | ok |
| yolo26-s_640x640.dxnn | 20.5 ±4.4 | 48.85 | 40.35 | 8.50 | 49 | ok |
| yolo26-m_640x640.dxnn | 17.8 ±1.5 | 56.30 | 48.29 | 8.01 | 50 | ok |
| yolo26-l_640x640.dxnn | 12.8 ±0.1 | 78.32 | 71.57 | 6.75 | 50 | ok |
| yolo26-x_640x640.dxnn | 9.8 ±0.1 | 101.68 | 96.12 | 5.56 | 50 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_640x640.dxnn | 27.0 ±0.9 | 37.07 | 37.07 | N/A | 49 | ok |
| yolo26-s_640x640.dxnn | 22.7 ±1.2 | 44.01 | 44.01 | N/A | 49 | ok |
| yolo26-m_640x640.dxnn | 23.3 ±0.9 | 42.93 | 42.93 | N/A | 50 | ok |
| yolo26-l_640x640.dxnn | 17.3 ±1.1 | 57.78 | 57.78 | N/A | 50 | ok |
| yolo26-x_640x640.dxnn | 11.6 ±0.5 | 86.21 | 86.21 | N/A | 51 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-pose_640x640.dxnn | 34.4 ±1.1 | 29.04 | 25.31 | 3.73 | 49 | ok |
| yolo26-s-pose_640x640.dxnn | 25.0 ±0.6 | 39.99 | 36.51 | 3.48 | 49 | ok |
| yolo26-m-pose_640x640.dxnn | 17.7 ±0.5 | 56.39 | 53.14 | 3.25 | 50 | ok |
| yolo26-l-pose_640x640.dxnn | 14.8 ±0.4 | 67.47 | 64.23 | 3.25 | 49 | ok |
| yolo26-x-pose_640x640.dxnn | 11.2 ±0.3 | 89.40 | 85.96 | 3.44 | 50 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-pose_640x640.dxnn | 40.2 ±1.0 | 24.88 | 24.88 | N/A | 49 | ok |
| yolo26-s-pose_640x640.dxnn | 29.9 ±0.9 | 33.48 | 33.48 | N/A | 49 | ok |
| yolo26-m-pose_640x640.dxnn | 23.1 ±1.3 | 43.29 | 43.29 | N/A | 50 | ok |
| yolo26-l-pose_640x640.dxnn | 20.2 ±0.6 | 49.43 | 49.43 | N/A | 50 | ok |
| yolo26-x-pose_640x640.dxnn | 12.9 ±0.1 | 77.43 | 77.43 | N/A | 51 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-seg_640x640.dxnn | 18.5 ±1.6 | 54.17 | 44.69 | 9.48 | 49 | ok |
| yolo26-s-seg_640x640.dxnn | 16.8 ±0.8 | 59.44 | 53.61 | 5.83 | 49 | ok |
| yolo26-m-seg_640x640.dxnn | 13.0 ±0.1 | 77.03 | 68.12 | 8.90 | 50 | ok |
| yolo26-l-seg_640x640.dxnn | 12.4 ±0.1 | 80.36 | 74.05 | 6.31 | 50 | ok |
| yolo26-x-seg_640x640.dxnn | 8.0 ±0.2 | 125.38 | 117.84 | 7.54 | 51 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-seg_640x640.dxnn | 22.7 ±0.1 | 44.04 | 44.04 | N/A | 49 | ok |
| yolo26-s-seg_640x640.dxnn | 18.6 ±0.6 | 53.66 | 53.66 | N/A | 49 | ok |
| yolo26-m-seg_640x640.dxnn | 14.7 ±0.1 | 68.17 | 68.17 | N/A | 50 | ok |
| yolo26-l-seg_640x640.dxnn | 13.1 ±0.4 | 76.60 | 76.60 | N/A | 50 | ok |
| yolo26-x-seg_640x640.dxnn | 8.5 ±0.4 | 117.92 | 117.92 | N/A | 51 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-obb_1024x1024.dxnn | 15.8 ±0.2 | 63.22 | 58.36 | 4.86 | 49 | ok |
| yolo26-s-obb_1024x1024.dxnn | 13.8 ±0.5 | 72.60 | 68.21 | 4.38 | 49 | ok |
| yolo26-m-obb_1024x1024.dxnn | 10.7 ±0.3 | 93.27 | 89.02 | 4.25 | 50 | ok |
| yolo26-l-obb_1024x1024.dxnn | 9.5 ±0.0 | 105.00 | 99.67 | 5.33 | 50 | ok |
| yolo26-x-obb_1024x1024.dxnn | 5.3 ±0.1 | 189.52 | 184.91 | 4.61 | 51 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-obb_1024x1024.dxnn | 22.4 ±0.3 | 44.57 | 44.57 | N/A | 49 | ok |
| yolo26-s-obb_1024x1024.dxnn | 16.1 ±0.5 | 62.25 | 62.25 | N/A | 49 | ok |
| yolo26-m-obb_1024x1024.dxnn | 12.4 ±0.2 | 80.56 | 80.56 | N/A | 51 | ok |
| yolo26-l-obb_1024x1024.dxnn | 10.3 ±0.0 | 97.55 | 97.55 | N/A | 51 | ok |
| yolo26-x-obb_1024x1024.dxnn | 5.8 ±0.1 | 173.76 | 173.76 | N/A | 52 | ok |

#### Classification

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_224x224.dxnn | 380.8 | 2.63 | 2.63 | N/A | 49 | ok |
| yolo26-s_224x224.dxnn | 205.8 ±4.1 | 4.86 | 4.86 | N/A | 48 | ok |
| yolo26-m_224x224.dxnn | 182.3 | 5.49 | 5.49 | N/A | 49 | ok |
| yolo26-l_224x224.dxnn | 146.5 ±0.4 | 6.82 | 6.82 | N/A | 49 | ok |
| yolo26-x_224x224.dxnn | 105.2 ±0.7 | 9.51 | 9.51 | N/A | 49 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_224x224.dxnn | 254.2 ±0.1 | 3.93 | 3.93 | N/A | 48 | ok |
| yolo26-s_224x224.dxnn | 206.1 ±6.6 | 4.85 | 4.85 | N/A | 48 | ok |
| yolo26-m_224x224.dxnn | 184.0 ±0.3 | 5.44 | 5.44 | N/A | 49 | ok |
| yolo26-l_224x224.dxnn | 143.8 ±1.1 | 6.96 | 6.96 | N/A | 49 | ok |
| yolo26-x_224x224.dxnn | 103.8 ±0.4 | 9.64 | 9.64 | N/A | 49 | ok |

## E2E Pipeline (Single-Stream)

### Object Detection

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | mppvideodec | 3455 | 3 | 148.1 ±2.4 | 23.33 | 250 | 37.3 | 63.9 | 49~50 | 1000 | 188 | ok |
| yolo26-s_640x640.dxnn | mppvideodec | 3455 | 3 | 125.0 ±2.5 | 27.65 | 218 | 57.7 | 79.6 | 53~55 | 1000 | 209 | ok |
| yolo26-m_640x640.dxnn | mppvideodec | 3455 | 3 | 98.5 ±0.4 | 35.09 | 190 | 75.0 | 92.9 | 58~63 | 1000 | 240 | ok |
| yolo26-l_640x640.dxnn | mppvideodec | 3455 | 3 | 80.1 ±0.7 | 43.11 | 175 | 83.5 | 99.4 | 60~65 | 1000 | 254 | ok |
| yolo26-x_640x640.dxnn | mppvideodec | 3455 | 3 | 48.1 ±0.2 | 71.88 | 136 | 92.8 | 100.0 | 66~74 | 1000 | 354 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | mppvideodec | 3455 | 3 | 99.6 ±0.1 | 34.70 | 211 | 22.0 | 73.2 | 50~51 | 1000 | 201 | ok |
| yolo26-s_640x640.dxnn | mppvideodec | 3455 | 3 | 100.0 ±1.2 | 34.54 | 218 | 41.2 | 69.5 | 52~54 | 1000 | 220 | ok |
| yolo26-m_640x640.dxnn | mppvideodec | 3455 | 3 | 98.6 ±0.4 | 35.04 | 220 | 73.2 | 82.7 | 58~62 | 1000 | 253 | ok |
| yolo26-l_640x640.dxnn | mppvideodec | 3455 | 3 | 87.8 ±0.2 | 39.34 | 223 | 90.5 | 100.0 | 60~65 | 1000 | 266 | ok |
| yolo26-x_640x640.dxnn | mppvideodec | 3455 | 3 | 47.8 ±0.4 | 72.24 | 166 | 93.9 | 100.0 | 66~74 | 1000 | 358 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n_640x640.dxnn | 148.1 | 99.6 | +48.5 | +48.8% |
| yolo26-s_640x640.dxnn | 125.0 | 100.0 | +24.9 | +24.9% |
| yolo26-m_640x640.dxnn | 98.5 | 98.6 | -0.1 | -0.1% |
| yolo26-l_640x640.dxnn | 80.1 | 87.8 | -7.7 | -8.8% |
| yolo26-x_640x640.dxnn | 48.1 | 47.8 | +0.2 | +0.5% |

### Pose Estimation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 200.7 ±1.9 | 17.22 | 241 | 54.0 | 75.6 | 52~53 | 1000 | 180 | ok |
| yolo26-s-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 150.6 ±1.2 | 22.94 | 203 | 73.5 | 91.9 | 53~55 | 1000 | 201 | ok |
| yolo26-m-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 107.2 ±0.9 | 32.24 | 171 | 84.4 | 100.0 | 58~63 | 1000 | 233 | ok |
| yolo26-l-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 84.0 ±0.6 | 41.14 | 155 | 88.9 | 100.0 | 60~65 | 1000 | 247 | ok |
| yolo26-x-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 47.1 ±0.2 | 73.40 | 114 | 92.3 | 100.0 | 66~74 | 1000 | 369 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 243.4 ±0.8 | 14.20 | 217 | 65.7 | 89.7 | 52~53 | 1000 | 169 | ok |
| yolo26-s-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 169.5 ±0.8 | 20.38 | 178 | 80.2 | 97.4 | 54~56 | 1000 | 190 | ok |
| yolo26-m-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 111.1 ±0.4 | 31.10 | 148 | 88.2 | 100.0 | 58~63 | 1000 | 223 | ok |
| yolo26-l-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 83.9 ±0.6 | 41.20 | 124 | 90.0 | 100.0 | 59~65 | 1000 | 236 | ok |
| yolo26-x-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 47.3 ±0.1 | 72.99 | 96 | 94.0 | 100.0 | 66~73 | 1000 | 352 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-pose_640x640.dxnn | 200.7 | 243.4 | -42.7 | -17.6% |
| yolo26-s-pose_640x640.dxnn | 150.6 | 169.5 | -18.9 | -11.1% |
| yolo26-m-pose_640x640.dxnn | 107.2 | 111.1 | -3.9 | -3.5% |
| yolo26-l-pose_640x640.dxnn | 84.0 | 83.9 | +0.1 | +0.1% |
| yolo26-x-pose_640x640.dxnn | 47.1 | 47.3 | -0.3 | -0.6% |

### Segmentation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 101.5 ±2.1 | 34.03 | 318 | 33.8 | 57.4 | 52~54 | 1000 | 287 | ok |
| yolo26-s-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 87.4 ±0.1 | 39.53 | 282 | 52.8 | 75.0 | 54~58 | 1000 | 310 | ok |
| yolo26-m-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 65.5 ±0.9 | 52.74 | 233 | 76.3 | 95.7 | 63~71 | 1000 | 348 | ok |
| yolo26-l-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 57.4 ±0.5 | 60.15 | 216 | 83.4 | 100.0 | 63~70 | 1000 | 360 | ok |
| yolo26-x-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 31.8 ±2.1 | 108.62 | 148 | 91.4 | 100.0 | 73~79 | 800~1000 | 464 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 84.1 ±2.8 | 41.08 | 273 | 23.9 | 79.1 | 52~53 | 1000 | 306 | ok |
| yolo26-s-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 83.7 ±0.1 | 41.26 | 272 | 46.8 | 77.6 | 55~58 | 1000 | 329 | ok |
| yolo26-m-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 74.9 ±0.5 | 46.10 | 260 | 86.2 | 100.0 | 64~71 | 1000 | 368 | ok |
| yolo26-l-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 63.4 ±0.3 | 54.51 | 222 | 91.3 | 100.0 | 63~72 | 1000 | 381 | ok |
| yolo26-x-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 32.1 ±2.2 | 107.67 | 148 | 92.5 | 100.0 | 73~79 | 800~1000 | 479 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-seg_640x640.dxnn | 101.5 | 84.1 | +17.4 | +20.7% |
| yolo26-s-seg_640x640.dxnn | 87.4 | 83.7 | +3.7 | +4.4% |
| yolo26-m-seg_640x640.dxnn | 65.5 | 74.9 | -9.4 | -12.6% |
| yolo26-l-seg_640x640.dxnn | 57.4 | 63.4 | -6.0 | -9.4% |
| yolo26-x-seg_640x640.dxnn | 31.8 | 32.1 | -0.3 | -0.9% |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 91.8 ±0.5 | 28.74 | 180 | 79.1 | 98.3 | 52~54 | 1000 | 215 | ok |
| yolo26-s-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 61.5 ±0.4 | 42.94 | 146 | 89.4 | 100.0 | 56~59 | 1000 | 239 | ok |
| yolo26-m-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 41.3 ±0.1 | 63.89 | 117 | 91.8 | 100.0 | 63~69 | 1000 | 272 | ok |
| yolo26-l-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 30.3 ±0.1 | 87.05 | 103 | 93.7 | 100.0 | 64~71 | 1000 | 288 | ok |
| yolo26-x-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 16.7 ±0.3 | 157.88 | 65 | 93.8 | 100.0 | 72~78 | 800~1000 | 391 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 100.0 ±0.5 | 26.40 | 201 | 85.6 | 100.0 | 53~55 | 1000 | 219 | ok |
| yolo26-s-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 62.3 ±0.5 | 42.36 | 152 | 90.4 | 100.0 | 56~59 | 1000 | 240 | ok |
| yolo26-m-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 41.7 ±0.7 | 63.33 | 119 | 93.1 | 100.0 | 63~69 | 1000 | 271 | ok |
| yolo26-l-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 30.2 ±0.2 | 87.35 | 107 | 93.6 | 100.0 | 65~71 | 1000 | 285 | ok |
| yolo26-x-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 16.8 ±0.5 | 157.52 | 70 | 93.3 | 100.0 | 73~79 | 800~1000 | 389 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-obb_1024x1024.dxnn | 91.8 | 100.0 | -8.1 | -8.1% |
| yolo26-s-obb_1024x1024.dxnn | 61.5 | 62.3 | -0.8 | -1.3% |
| yolo26-m-obb_1024x1024.dxnn | 41.3 | 41.7 | -0.4 | -0.9% |
| yolo26-l-obb_1024x1024.dxnn | 30.3 | 30.2 | +0.1 | +0.4% |
| yolo26-x-obb_1024x1024.dxnn | 16.7 | 16.8 | -0.0 | -0.2% |

### Classification

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_224x224.dxnn | mppvideodec | 3455 | 3 | 1072.7 ±5.8 | 3.22 | 177 | 15.0 | 51.8 | 49 | 1000 | 91 | ok |
| yolo26-s_224x224.dxnn | mppvideodec | 3455 | 3 | 1060.3 ±0.5 | 3.26 | 176 | 23.9 | 68.2 | 49~50 | 1000 | 101 | ok |
| yolo26-m_224x224.dxnn | mppvideodec | 3455 | 3 | 1073.2 ±1.9 | 3.22 | 174 | 38.3 | 83.8 | 51 | 1000 | 115 | ok |
| yolo26-l_224x224.dxnn | mppvideodec | 3455 | 3 | 864.2 ±5.9 | 4.00 | 157 | 56.1 | 98.0 | 51 | 1000 | 128 | ok |
| yolo26-x_224x224.dxnn | mppvideodec | 3455 | 3 | 481.2 ±1.1 | 7.18 | 127 | 65.9 | 98.8 | 52~53 | 1000 | 204 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_224x224.dxnn | mppvideodec | 3455 | 3 | 1071.0 ±2.6 | 3.23 | 178 | 15.3 | 52.8 | 49 | 1000 | 91 | ok |
| yolo26-s_224x224.dxnn | mppvideodec | 3455 | 3 | 1060.8 ±1.7 | 3.26 | 177 | 26.6 | 69.6 | 49 | 1000 | 100 | ok |
| yolo26-m_224x224.dxnn | mppvideodec | 3455 | 3 | 1062.3 ±8.9 | 3.25 | 175 | 38.9 | 83.1 | 51 | 1000 | 115 | ok |
| yolo26-l_224x224.dxnn | mppvideodec | 3455 | 3 | 862.5 ±0.7 | 4.01 | 157 | 56.1 | 97.9 | 51 | 1000 | 128 | ok |
| yolo26-x_224x224.dxnn | mppvideodec | 3455 | 3 | 481.6 ±1.6 | 7.17 | 121 | 66.5 | 98.9 | 53 | 1000 | 204 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n_224x224.dxnn | 1072.7 | 1071.0 | +1.7 | +0.2% |
| yolo26-s_224x224.dxnn | 1060.3 | 1060.8 | -0.5 | -0.0% |
| yolo26-m_224x224.dxnn | 1073.2 | 1062.3 | +10.8 | +1.0% |
| yolo26-l_224x224.dxnn | 864.2 | 862.5 | +1.7 | +0.2% |
| yolo26-x_224x224.dxnn | 481.2 | 481.6 | -0.4 | -0.1% |

## E2E Pipeline (Multi-Stream)

### Object Detection

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | 4 | 3 | 150.8 ±3.0 | 37.7 | 257 | 41.5 | 65.5 | 54~57 | 1000 | 211 | ok |
| yolo26-n_640x640.dxnn | 5 | 3 | 148.4 ±1.9 | 29.7 | 255 | 41.5 | 65.2 | 59~60 | 1000 | 215 | ok |
| yolo26-s_640x640.dxnn | 4 | 3 | 126.9 ±1.2 | 31.7 | 222 | 62.6 | 79.7 | 60~63 | 1000 | 232 | ok |
| yolo26-s_640x640.dxnn | 5 | 3 | 126.1 ±0.5 | 25.2 | 225 | 63.3 | 79.6 | 66~67 | 1000 | 237 | ok |
| yolo26-m_640x640.dxnn | 3 | 3 | 98.2 ±0.7 | 32.7 | 195 | 78.6 | 92.7 | 73~79 | 1000 | 257 | ok |
| yolo26-m_640x640.dxnn | 4 | 3 | 91.2 ±1.2 | 22.8 | 188 | 81.4 | 97.0 | 82 | 600~1000 | 263 | ok |
| yolo26-l_640x640.dxnn | 2 | 3 | 80.0 ±0.1 | 40.0 | 178 | 85.8 | 99.7 | 73~78 | 1000 | 266 | ok |
| yolo26-l_640x640.dxnn | 3 | 3 | 73.5 ±0.8 | 24.5 | 169 | 86.8 | 100.0 | 82 | 800~1000 | 271 | ok |
| yolo26-x_640x640.dxnn | 1 | 3 | 48.1 ±0.2 | 48.1 | 136 | 92.8 | 100.0 | 66~74 | 1000 | 354 | ok |
| yolo26-x_640x640.dxnn | 2 | 3 | 41.2 ±0.8 | 20.6 | 126 | 91.9 | 100.0 | 80~81 | 800~1000 | 360 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | 3 | 3 | 98.3 ±0.7 | 32.8 | 220 | 22.9 | 73.2 | 52~53 | 1000 | 224 | ok |
| yolo26-n_640x640.dxnn | 4 | 3 | 99.0 ±0.4 | 24.8 | 218 | 23.3 | 73.2 | 54 | 1000 | 233 | ok |
| yolo26-s_640x640.dxnn | 3 | 3 | 100.1 ±0.6 | 33.4 | 224 | 43.4 | 69.6 | 59~62 | 1000 | 245 | ok |
| yolo26-s_640x640.dxnn | 4 | 3 | 98.5 ±0.5 | 24.6 | 221 | 43.5 | 68.6 | 64 | 1000 | 254 | ok |
| yolo26-m_640x640.dxnn | 3 | 3 | 94.1 ±0.5 | 31.4 | 225 | 71.7 | 84.0 | 72~77 | 1000 | 276 | ok |
| yolo26-m_640x640.dxnn | 4 | 3 | 93.3 ±2.0 | 23.3 | 225 | 81.0 | 100.0 | 81~82 | 600~1000 | 284 | ok |
| yolo26-l_640x640.dxnn | 2 | 3 | 88.3 ±0.4 | 44.1 | 228 | 94.3 | 100.0 | 74~79 | 1000 | 280 | ok |
| yolo26-l_640x640.dxnn | 3 | 3 | 77.1 ±0.6 | 25.7 | 212 | 93.2 | 100.0 | 81~82 | 600~1000 | 286 | ok |
| yolo26-x_640x640.dxnn | 1 | 3 | 47.8 ±0.4 | 47.8 | 166 | 93.9 | 100.0 | 66~74 | 1000 | 358 | ok |
| yolo26-x_640x640.dxnn | 2 | 3 | 41.5 ±0.9 | 20.7 | 158 | 94.1 | 100.0 | 81~82 | 800~1000 | 368 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n_640x640.dxnn | 4 | 37.7 | 3 | 32.8 |
| yolo26-s_640x640.dxnn | 4 | 31.7 | 3 | 33.4 |
| yolo26-m_640x640.dxnn | 3 | 32.7 | 3 | 31.4 |
| yolo26-l_640x640.dxnn | 2 | 40.0 | 2 | 44.1 |
| yolo26-x_640x640.dxnn | 1 | 48.1 | 1 | 47.8 |

### Pose Estimation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 6 | 3 | 202.9 ±1.1 | 33.8 | 254 | 62.3 | 78.8 | 59~63 | 1000 | 218 | ok |
| yolo26-n-pose_640x640.dxnn | 7 | 3 | 203.4 ±1.1 | 29.1 | 254 | 62.6 | 78.8 | 65~67 | 1000 | 222 | ok |
| yolo26-s-pose_640x640.dxnn | 5 | 3 | 150.7 ±0.8 | 30.1 | 210 | 80.7 | 93.4 | 64~68 | 1000 | 235 | ok |
| yolo26-s-pose_640x640.dxnn | 6 | 3 | 150.2 ±0.9 | 25.0 | 211 | 80.7 | 94.6 | 72~73 | 1000 | 241 | ok |
| yolo26-m-pose_640x640.dxnn | 3 | 3 | 106.0 ±1.6 | 35.3 | 175 | 89.2 | 99.8 | 74~79 | 800~1000 | 254 | ok |
| yolo26-m-pose_640x640.dxnn | 4 | 3 | 95.3 ±0.4 | 23.8 | 166 | 91.0 | 100.0 | 81 | 800~1000 | 262 | ok |
| yolo26-l-pose_640x640.dxnn | 2 | 3 | 84.2 ±0.2 | 42.1 | 155 | 93.1 | 100.0 | 73~78 | 1000 | 261 | ok |
| yolo26-l-pose_640x640.dxnn | 3 | 3 | 76.4 ±1.9 | 25.5 | 150 | 93.4 | 100.0 | 81 | 800~1000 | 269 | ok |
| yolo26-x-pose_640x640.dxnn | 1 | 3 | 47.1 ±0.2 | 47.1 | 114 | 92.3 | 100.0 | 66~74 | 1000 | 369 | ok |
| yolo26-x-pose_640x640.dxnn | 2 | 3 | 40.4 ±0.8 | 20.2 | 114 | 91.2 | 100.0 | 80~81 | 600~1000 | 370 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 8 | 3 | 250.3 ±6.2 | 31.3 | 225 | 79.8 | 91.5 | 61~65 | 1000 | 226 | ok |
| yolo26-n-pose_640x640.dxnn | 9 | 3 | 245.3 ±0.6 | 27.3 | 229 | 78.0 | 90.6 | 68~70 | 1000 | 230 | ok |
| yolo26-s-pose_640x640.dxnn | 5 | 3 | 169.8 ±0.1 | 34.0 | 185 | 88.0 | 97.9 | 64~69 | 1000 | 232 | ok |
| yolo26-s-pose_640x640.dxnn | 6 | 3 | 170.6 ±1.0 | 28.4 | 183 | 89.9 | 98.5 | 72~73 | 1000 | 237 | ok |
| yolo26-m-pose_640x640.dxnn | 3 | 3 | 110.6 ±1.9 | 36.9 | 150 | 93.9 | 100.0 | 74~79 | 800~1000 | 245 | ok |
| yolo26-m-pose_640x640.dxnn | 4 | 3 | 97.6 ±0.7 | 24.4 | 142 | 93.1 | 100.0 | 81 | 600~1000 | 254 | ok |
| yolo26-l-pose_640x640.dxnn | 2 | 3 | 84.4 ±0.6 | 42.2 | 127 | 94.7 | 100.0 | 73~77 | 1000 | 250 | ok |
| yolo26-l-pose_640x640.dxnn | 3 | 3 | 78.1 ±1.5 | 26.1 | 125 | 94.7 | 100.0 | 81 | 800~1000 | 257 | ok |
| yolo26-x-pose_640x640.dxnn | 1 | 3 | 47.3 ±0.1 | 47.3 | 96 | 94.0 | 100.0 | 66~73 | 1000 | 352 | ok |
| yolo26-x-pose_640x640.dxnn | 2 | 3 | 41.2 ±1.1 | 20.6 | 92 | 92.9 | 100.0 | 80~81 | 800~1000 | 352 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-pose_640x640.dxnn | 6 | 33.8 | 8 | 31.3 |
| yolo26-s-pose_640x640.dxnn | 5 | 30.1 | 5 | 34.0 |
| yolo26-m-pose_640x640.dxnn | 3 | 35.3 | 3 | 36.9 |
| yolo26-l-pose_640x640.dxnn | 2 | 42.1 | 2 | 42.2 |
| yolo26-x-pose_640x640.dxnn | 1 | 47.1 | 1 | 47.3 |

### Segmentation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 3 | 3 | 101.8 ±1.8 | 34.0 | 324 | 35.4 | 60.0 | 59~61 | 1000 | 318 | ok |
| yolo26-n-seg_640x640.dxnn | 4 | 3 | 101.3 ±0.3 | 25.3 | 330 | 35.7 | 60.8 | 64~65 | 1000 | 328 | ok |
| yolo26-s-seg_640x640.dxnn | 2 | 3 | 87.9 ±0.8 | 44.0 | 288 | 56.4 | 75.3 | 63~67 | 1000 | 330 | ok |
| yolo26-s-seg_640x640.dxnn | 3 | 3 | 88.2 ±1.7 | 29.4 | 282 | 57.9 | 76.0 | 71~73 | 1000 | 341 | ok |
| yolo26-m-seg_640x640.dxnn | 2 | 3 | 55.3 ±5.2 | 27.6 | 214 | 83.9 | 100.0 | 81~82 | 400~1000 | 366 | ok |
| yolo26-m-seg_640x640.dxnn | 1 | 3 | 65.5 ±0.9 | 65.5 | 233 | 76.3 | 95.7 | 63~71 | 1000 | 348 | ok |
| yolo26-l-seg_640x640.dxnn | 1 | 3 | 57.4 ±0.5 | 57.4 | 216 | 83.4 | 100.0 | 63~70 | 1000 | 360 | ok |
| yolo26-l-seg_640x640.dxnn | 2 | 3 | 53.4 ±2.7 | 26.7 | 209 | 85.8 | 100.0 | 79~82 | 600~1000 | 380 | ok |
| yolo26-x-seg_640x640.dxnn | 1 | 3 | 31.8 ±2.1 | 31.8 | 148 | 91.4 | 100.0 | 73~79 | 800~1000 | 464 | ok |
| yolo26-x-seg_640x640.dxnn | 2 | 3 | 26.1 ±0.5 | 13.1 | 127 | 92.1 | 100.0 | 81 | 400~1000 | 488 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 2 | 3 | 85.3 ±0.1 | 42.7 | 265 | 25.2 | 81.8 | 56~58 | 1000 | 334 | ok |
| yolo26-n-seg_640x640.dxnn | 3 | 3 | 85.4 ±0.2 | 28.5 | 275 | 25.3 | 82.7 | 61 | 1000 | 342 | ok |
| yolo26-s-seg_640x640.dxnn | 2 | 3 | 83.6 ±0.1 | 41.8 | 274 | 48.5 | 80.4 | 63~66 | 1000 | 358 | ok |
| yolo26-s-seg_640x640.dxnn | 3 | 3 | 83.4 ±0.1 | 27.8 | 275 | 48.8 | 80.4 | 70~71 | 1000 | 366 | ok |
| yolo26-m-seg_640x640.dxnn | 2 | 3 | 60.9 ±5.5 | 30.4 | 228 | 91.7 | 100.0 | 81~82 | 600~1000 | 382 | ok |
| yolo26-m-seg_640x640.dxnn | 3 | 3 | 54.9 ±1.2 | 18.3 | 214 | 94.0 | 100.0 | 82 | 400~1000 | 400 | ok |
| yolo26-l-seg_640x640.dxnn | 2 | 3 | 54.7 ±2.9 | 27.4 | 214 | 92.0 | 100.0 | 80~82 | 600~1000 | 399 | ok |
| yolo26-l-seg_640x640.dxnn | 1 | 3 | 63.4 ±0.3 | 63.4 | 222 | 91.3 | 100.0 | 63~72 | 1000 | 381 | ok |
| yolo26-x-seg_640x640.dxnn | 1 | 3 | 32.1 ±2.2 | 32.1 | 148 | 92.5 | 100.0 | 73~79 | 800~1000 | 479 | ok |
| yolo26-x-seg_640x640.dxnn | 2 | 3 | 25.5 ±0.4 | 12.8 | 131 | 92.7 | 100.0 | 80~81 | 600~1000 | 501 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-seg_640x640.dxnn | 3 | 34.0 | 2 | 42.7 |
| yolo26-s-seg_640x640.dxnn | 2 | 44.0 | 2 | 41.8 |
| yolo26-m-seg_640x640.dxnn | 1 | 65.5 | 2 | 30.4 |
| yolo26-l-seg_640x640.dxnn | 1 | 57.4 | 1 | 63.4 |
| yolo26-x-seg_640x640.dxnn | 1 | 31.8 | 1 | 32.1 |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 3 | 3 | 92.3 ±0.3 | 30.8 | 188 | 82.9 | 99.2 | 59~61 | 1000 | 243 | ok |
| yolo26-n-obb_1024x1024.dxnn | 4 | 3 | 91.8 ±0.2 | 22.9 | 188 | 84.1 | 99.3 | 65 | 1000 | 251 | ok |
| yolo26-s-obb_1024x1024.dxnn | 2 | 3 | 61.8 ±0.3 | 30.9 | 151 | 93.1 | 100.0 | 64~66 | 1000 | 254 | ok |
| yolo26-s-obb_1024x1024.dxnn | 3 | 3 | 62.0 ±0.3 | 20.6 | 150 | 93.8 | 100.0 | 69~70 | 1000 | 267 | ok |
| yolo26-m-obb_1024x1024.dxnn | 1 | 3 | 41.3 ±0.1 | 41.3 | 117 | 91.8 | 100.0 | 63~69 | 1000 | 272 | ok |
| yolo26-m-obb_1024x1024.dxnn | 2 | 3 | 40.2 ±1.6 | 20.1 | 121 | 94.3 | 100.0 | 77~79 | 800~1000 | 287 | ok |
| yolo26-l-obb_1024x1024.dxnn | 1 | 3 | 30.3 ±0.1 | 30.3 | 103 | 93.7 | 100.0 | 64~71 | 1000 | 288 | ok |
| yolo26-l-obb_1024x1024.dxnn | 2 | 3 | 29.9 ±0.9 | 14.9 | 104 | 95.7 | 100.0 | 77~79 | 800~1000 | 300 | ok |
| yolo26-x-obb_1024x1024.dxnn | 1 | 3 | 16.7 ±0.3 | 16.7 | 65 | 93.8 | 100.0 | 72~78 | 800~1000 | 391 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 3 | 3 | 100.5 ±0.2 | 33.5 | 208 | 93.0 | 100.0 | 60~63 | 1000 | 250 | ok |
| yolo26-n-obb_1024x1024.dxnn | 4 | 3 | 100.5 ±0.1 | 25.1 | 209 | 93.6 | 100.0 | 65~67 | 1000 | 255 | ok |
| yolo26-s-obb_1024x1024.dxnn | 2 | 3 | 62.3 ±0.2 | 31.2 | 159 | 93.9 | 100.0 | 64~67 | 1000 | 256 | ok |
| yolo26-s-obb_1024x1024.dxnn | 3 | 3 | 62.2 ±0.5 | 20.7 | 160 | 94.9 | 100.0 | 69~70 | 1000 | 269 | ok |
| yolo26-m-obb_1024x1024.dxnn | 1 | 3 | 41.7 ±0.7 | 41.7 | 119 | 93.1 | 100.0 | 63~69 | 1000 | 271 | ok |
| yolo26-m-obb_1024x1024.dxnn | 2 | 3 | 39.3 ±2.1 | 19.7 | 133 | 95.4 | 100.0 | 78~80 | 800~1000 | 288 | ok |
| yolo26-l-obb_1024x1024.dxnn | 1 | 3 | 30.2 ±0.2 | 30.2 | 107 | 93.6 | 100.0 | 65~71 | 1000 | 285 | ok |
| yolo26-l-obb_1024x1024.dxnn | 2 | 3 | 29.9 ±0.7 | 14.9 | 110 | 95.2 | 100.0 | 78~79 | 800~1000 | 299 | ok |
| yolo26-x-obb_1024x1024.dxnn | 1 | 3 | 16.8 ±0.5 | 16.8 | 70 | 93.3 | 100.0 | 73~79 | 800~1000 | 389 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-obb_1024x1024.dxnn | 3 | 30.8 | 3 | 33.5 |
| yolo26-s-obb_1024x1024.dxnn | 2 | 30.9 | 2 | 31.2 |
| yolo26-m-obb_1024x1024.dxnn | 1 | 41.3 | 1 | 41.7 |
| yolo26-l-obb_1024x1024.dxnn | 1 | 30.3 | 1 | 30.2 |

---
*Report generated by dx-benchmark tool*
