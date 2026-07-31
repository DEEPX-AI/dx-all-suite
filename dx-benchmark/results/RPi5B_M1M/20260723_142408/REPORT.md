# YOLO26 Benchmark Report

**Generated:** 2026-07-29 10:29:15 (Local)

## Test Timing

| # | Type | Start | End | Duration |
|---|------|-------|-----|----------|
| 1 | run | 2026-07-23 14:24:08 | 2026-07-24 11:04:34 | 20h 40m 26s |

## Executive Summary

### Object Detection

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n_640x640.dxnn | ON | 26.00 | 102.9 | 68.0 | 2 |
| yolo26-n_640x640.dxnn | OFF | 22.50 | 179.2 | 79.8 | 2 |
| yolo26-s_640x640.dxnn | ON | 31.60 | 105.8 | 67.5 | 2 |
| yolo26-s_640x640.dxnn | OFF | 29.20 | 153.2 | 80.2 | 2 |
| yolo26-m_640x640.dxnn | ON | 39.63 | 74.2 | 67.0 | 1 |
| yolo26-m_640x640.dxnn | OFF | 39.60 | 73.5 | 77.8 | 1 |
| yolo26-l_640x640.dxnn | ON | 48.99 | 59.8 | 56.3 | 1 |
| yolo26-l_640x640.dxnn | OFF | 46.40 | 60.0 | 57.6 | 1 |
| yolo26-x_640x640.dxnn | ON | 79.11 | 25.4 | 21.9 | — |
| yolo26-x_640x640.dxnn | OFF | 75.43 | 26.3 | 21.2 | — |

### Pose Estimation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-pose_640x640.dxnn | ON | 20.76 | 151.5 | 82.3 | 2 |
| yolo26-n-pose_640x640.dxnn | OFF | 19.29 | 229.4 | 112.4 | 3 |
| yolo26-s-pose_640x640.dxnn | ON | 27.55 | 141.7 | 81.9 | 2 |
| yolo26-s-pose_640x640.dxnn | OFF | 27.83 | 142.5 | 112.6 | 3 |
| yolo26-m-pose_640x640.dxnn | ON | 36.96 | 63.2 | 69.9 | 1 |
| yolo26-m-pose_640x640.dxnn | OFF | 35.17 | 60.2 | 69.8 | 1 |
| yolo26-l-pose_640x640.dxnn | ON | 45.89 | 50.0 | 46.0 | 1 |
| yolo26-l-pose_640x640.dxnn | OFF | 43.80 | 51.3 | 49.2 | 1 |
| yolo26-x-pose_640x640.dxnn | ON | 75.78 | 24.3 | 22.7 | — |
| yolo26-x-pose_640x640.dxnn | OFF | 73.13 | 25.6 | 20.6 | — |

### Segmentation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-seg_640x640.dxnn | ON | 40.69 | 67.3 | 44.8 | 1 |
| yolo26-n-seg_640x640.dxnn | OFF | 37.81 | 95.7 | 54.9 | 1 |
| yolo26-s-seg_640x640.dxnn | ON | 48.46 | 67.7 | 44.7 | 1 |
| yolo26-s-seg_640x640.dxnn | OFF | 46.46 | 94.8 | 55.3 | 1 |
| yolo26-m-seg_640x640.dxnn | ON | 64.86 | 38.0 | 35.0 | 1 |
| yolo26-m-seg_640x640.dxnn | OFF | 66.27 | 36.1 | 34.6 | 1 |
| yolo26-l-seg_640x640.dxnn | ON | 73.66 | 31.8 | 29.1 | — |
| yolo26-l-seg_640x640.dxnn | OFF | 70.97 | 31.0 | 26.9 | — |
| yolo26-x-seg_640x640.dxnn | ON | 117.40 | 15.0 | 13.0 | — |
| yolo26-x-seg_640x640.dxnn | OFF | 113.04 | 16.1 | 12.8 | — |

### Oriented BBox (OBB)

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-obb_1024x1024.dxnn | ON | 39.55 | 73.8 | 67.7 | 2 |
| yolo26-n-obb_1024x1024.dxnn | OFF | 39.45 | 73.7 | 72.3 | 2 |
| yolo26-s-obb_1024x1024.dxnn | ON | 58.41 | 44.5 | 44.1 | 1 |
| yolo26-s-obb_1024x1024.dxnn | OFF | 56.03 | 46.0 | 44.1 | 1 |
| yolo26-m-obb_1024x1024.dxnn | ON | 78.34 | 22.8 | 18.2 | — |
| yolo26-m-obb_1024x1024.dxnn | OFF | 76.79 | 23.1 | 18.8 | — |
| yolo26-l-obb_1024x1024.dxnn | ON | 100.57 | 17.6 | 14.3 | — |
| yolo26-l-obb_1024x1024.dxnn | OFF | 98.49 | 20.7 | 16.5 | — |
| yolo26-x-obb_1024x1024.dxnn | ON | 178.33 | 10.3 | 8.6 | — |
| yolo26-x-obb_1024x1024.dxnn | OFF | 176.03 | 10.2 | 8.7 | — |

### Classification

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n_224x224.dxnn | ON | 1.52 | 3018.9 | 189.3 | — |
| yolo26-n_224x224.dxnn | OFF | 1.49 | 3019.9 | 189.1 | — |
| yolo26-s_224x224.dxnn | ON | 2.18 | 1597.6 | 189.0 | — |
| yolo26-s_224x224.dxnn | OFF | 2.27 | 1596.8 | 189.3 | — |
| yolo26-m_224x224.dxnn | ON | 2.92 | 1067.6 | 189.1 | — |
| yolo26-m_224x224.dxnn | OFF | 3.00 | 1066.2 | 189.5 | — |
| yolo26-l_224x224.dxnn | ON | 4.34 | 715.0 | 188.9 | — |
| yolo26-l_224x224.dxnn | OFF | 4.35 | 712.8 | 188.6 | — |
| yolo26-x_224x224.dxnn | ON | 7.24 | 358.9 | 187.7 | — |
| yolo26-x_224x224.dxnn | OFF | 7.22 | 362.5 | 187.2 | — |

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
| DX-AllSuite | v2.4.0 |
| Benchmark Tool | 0.1.0 |
| NPU RT | v3.4.0 |
| NPU RT (commit) | v3.4.0+5474c9f |
| NPU Driver (RT) | v2.5.1 |
| NPU Driver (PCIe) | v2.4.1 |
| NPU Firmware | v2.7.3 |
| NPU Memory | LPDDR4 4200 Mbps, 1.92GiB |
| NPU Board | M.2, Rev 0.0 |
| NPU PCIe | Gen3 X1 [01:00:00] |

### Tools

| Tool | Available | Version |
|------|-----------|---------|
| run_model | Yes | DXRT v3.4.0 run_model |
| dxrt-cli | Yes | unknown |
| gst-launch-1.0 | Yes | gst-launch-1.0 version 1.22.0 |
| gst-inspect-1.0 | Yes | gst-inspect-1.0 version 1.22.0 |
| time | Yes | unknown |
| ffprobe | Yes | ffprobe version 5.1.9-0+deb12u1+rpt1 Copyright (c) 2007-2026... |
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
| yolo26-n_640x640.dxnn | 102.9 ±0.5 | 8 | 183 | 28.7 | 76.0 | 54~56 | 1000 | ok |
| yolo26-s_640x640.dxnn | 105.8 ±0.6 | 7 | 187 | 57.3 | 86.3 | 67~69 | 1000 | ok |
| yolo26-m_640x640.dxnn | 74.2 ±9.7 | 6 | 105 | 90.6 | 100.0 | 83~84 | 400~1000 | ok |
| yolo26-l_640x640.dxnn | 59.8 ±5.2 | 5 | 79 | 88.2 | 100.0 | 81~84 | 400~1000 | ok |
| yolo26-x_640x640.dxnn | 25.4 ±2.3 | 4 | 36 | 81.5 | 100.0 | 84~85 | 400~1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n_640x640.dxnn | 8 | [3]:90.4 · [4]:103.6 · [5]:104.4 · [6]:103.6 · [7]:102.9 · **[8]:105.6 ★** · [9]:103.3 |
| yolo26-s_640x640.dxnn | 7 | [3]:75.3 · [4]:93.2 · [5]:103.6 · [6]:103.6 · **[7]:105.5 ★** · [8]:103.7 |
| yolo26-m_640x640.dxnn | 6 | [3]:59.1 · [4]:73.5 · [5]:86.5 · **[6]:89.0 ★** · [7]:82.4 · [8]:84.9 |
| yolo26-l_640x640.dxnn | 5 | [3]:50.2 · [4]:61.6 · **[5]:66.0 ★** · [6]:62.3 · [7]:62.5 · [8]:62.5 |
| yolo26-x_640x640.dxnn | 4 | [3]:30.9 · **[4]:37.6 ★** · [5]:35.5 · [6]:35.4 · [7]:35.8 · [8]:36.0 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n_640x640.dxnn | 179.2 ±0.1 | 6 | 111 | 55.9 | 88.0 | 64~68 | 1000 | ok |
| yolo26-s_640x640.dxnn | 153.2 ±0.5 | 7 | 89 | 93.1 | 100.0 | 76~82 | 1000 | ok |
| yolo26-m_640x640.dxnn | 73.5 ±7.0 | 5 | 47 | 89.4 | 100.0 | 83~85 | 400~1000 | ok |
| yolo26-l_640x640.dxnn | 60.0 ±3.4 | 6 | 40 | 90.6 | 100.0 | 81~85 | 600~1000 | ok |
| yolo26-x_640x640.dxnn | 26.3 ±1.1 | 4 | 17 | 87.7 | 100.0 | 84~85 | 400~1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n_640x640.dxnn | 6 | [3]:108.3 · [4]:134.1 · [5]:165.5 · **[6]:179.1 ★** · [7]:179.1 · [8]:179.0 |
| yolo26-s_640x640.dxnn | 7 | [3]:85.1 · [4]:116.0 · [5]:134.3 · [6]:146.0 · **[7]:152.5 ★** · [8]:142.9 |
| yolo26-m_640x640.dxnn | 5 | [3]:61.4 · [4]:83.0 · **[5]:85.5 ★** · [6]:81.9 · [7]:81.0 · [8]:81.9 |
| yolo26-l_640x640.dxnn | 6 | [3]:52.3 · [4]:66.8 · [5]:61.6 · **[6]:67.1 ★** · [7]:64.4 · [8]:62.6 |
| yolo26-x_640x640.dxnn | 4 | [3]:33.4 · **[4]:37.9 ★** · [5]:35.6 · [6]:35.6 · [7]:36.0 · [8]:35.9 |


#### Pose Estimation

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 151.5 ±0.9 | 7 | 189 | 49.1 | 80.6 | 64~68 | 1000 | ok |
| yolo26-s-pose_640x640.dxnn | 141.7 ±0.9 | 6 | 150 | 91.3 | 100.0 | 76~82 | 1000 | ok |
| yolo26-m-pose_640x640.dxnn | 63.2 ±6.7 | 4 | 57 | 84.7 | 100.0 | 84~85 | 400~1000 | ok |
| yolo26-l-pose_640x640.dxnn | 50.0 ±7.0 | 4 | 45 | 85.8 | 100.0 | 85 | 400~1000 | ok |
| yolo26-x-pose_640x640.dxnn | 24.3 ±1.6 | 4 | 22 | 83.4 | 100.0 | 84~85 | 400~1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-pose_640x640.dxnn | 7 | [3]:109.5 · [4]:135.4 · [5]:146.3 · [6]:151.4 · **[7]:151.9 ★** · [8]:150.8 |
| yolo26-s-pose_640x640.dxnn | 6 | [3]:83.1 · [4]:110.0 · [5]:130.7 · **[6]:139.9 ★** · [7]:139.6 · [8]:132.2 |
| yolo26-m-pose_640x640.dxnn | 4 | [3]:60.9 · **[4]:80.2 ★** · [5]:77.2 · [6]:78.5 · [7]:76.8 · [8]:79.5 |
| yolo26-l-pose_640x640.dxnn | 4 | [3]:51.2 · **[4]:65.1 ★** · [5]:61.0 · [6]:60.6 · [7]:60.5 · [8]:64.3 |
| yolo26-x-pose_640x640.dxnn | 4 | [3]:33.1 · **[4]:36.8 ★** · [5]:34.9 · [6]:34.9 · [7]:35.1 · [8]:35.0 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 229.4 ±1.5 | 7 | 86 | 90.4 | 100.0 | 72~78 | 1000 | ok |
| yolo26-s-pose_640x640.dxnn | 142.5 ±1.1 | 5 | 55 | 90.6 | 100.0 | 77~82 | 1000 | ok |
| yolo26-m-pose_640x640.dxnn | 60.2 ±4.2 | 9 | 27 | 90.0 | 100.0 | 85 | 400~1000 | ok |
| yolo26-l-pose_640x640.dxnn | 51.3 ±8.7 | 4 | 24 | 86.9 | 100.0 | 84~85 | 400~1000 | ok |
| yolo26-x-pose_640x640.dxnn | 25.6 ±3.4 | 5 | 11 | 87.3 | 100.0 | 85 | 400~1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-pose_640x640.dxnn | 7 | [3]:118.7 · [4]:154.6 · [5]:186.6 · [6]:218.5 · **[7]:228.8 ★** · [8]:218.8 |
| yolo26-s-pose_640x640.dxnn | 5 | [3]:94.7 · [4]:120.9 · **[5]:142.1 ★** · [6]:132.9 · [7]:131.9 · [8]:134.5 |
| yolo26-m-pose_640x640.dxnn | 9 | [3]:68.2 · [4]:83.6 · [5]:78.7 · [6]:78.5 · [7]:79.7 · [8]:83.9 · **[9]:86.2 ★** · [10]:79.3 |
| yolo26-l-pose_640x640.dxnn | 4 | [3]:55.6 · **[4]:65.0 ★** · [5]:62.6 · [6]:61.2 · [7]:61.0 · [8]:61.6 |
| yolo26-x-pose_640x640.dxnn | 5 | [3]:33.4 · [4]:36.8 · **[5]:36.8 ★** · [6]:34.8 · [7]:36.0 · [8]:35.2 |


#### Segmentation

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 67.3 ±0.4 | 6 | 220 | 23.7 | 72.0 | 60~62 | 1000 | ok |
| yolo26-s-seg_640x640.dxnn | 67.7 ±0.4 | 10 | 224 | 47.3 | 78.6 | 70~73 | 1000 | ok |
| yolo26-m-seg_640x640.dxnn | 38.0 ±1.3 | 6 | 92 | 90.5 | 100.0 | 85~86 | 300~600 | ok |
| yolo26-l-seg_640x640.dxnn | 31.8 ±1.1 | 5 | 74 | 86.7 | 100.0 | 84~86 | 400~800 | ok |
| yolo26-x-seg_640x640.dxnn | 15.0 ±0.9 | 4 | 36 | 80.4 | 100.0 | 85~86 | 300~1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-seg_640x640.dxnn | 6 | [3]:56.9 · [4]:64.6 · [5]:65.7 · **[6]:67.9 ★** · [7]:67.8 · [8]:67.3 |
| yolo26-s-seg_640x640.dxnn | 10 | [3]:48.2 · [4]:59.0 · [5]:66.6 · [6]:67.1 · [7]:67.5 · [8]:68.0 · [9]:67.9 · **[10]:68.1 ★** |
| yolo26-m-seg_640x640.dxnn | 6 | [3]:37.9 · [4]:47.7 · [5]:55.1 · **[6]:58.7 ★** · [7]:58.7 · [8]:58.6 |
| yolo26-l-seg_640x640.dxnn | 5 | [3]:34.3 · [4]:42.9 · **[5]:48.0 ★** · [6]:47.6 · [7]:47.9 · [8]:47.1 |
| yolo26-x-seg_640x640.dxnn | 4 | [3]:21.5 · **[4]:26.5 ★** · [5]:25.3 · [6]:26.1 · [7]:24.8 · [8]:24.5 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 95.7 ±0.1 | 7 | 119 | 37.9 | 67.5 | 64~66 | 1000 | ok |
| yolo26-s-seg_640x640.dxnn | 94.8 ±0.9 | 8 | 117 | 82.5 | 100.0 | 79~85 | 600~1000 | ok |
| yolo26-m-seg_640x640.dxnn | 36.1 ±3.7 | 5 | 52 | 88.9 | 100.0 | 85~86 | 300~800 | ok |
| yolo26-l-seg_640x640.dxnn | 31.0 ±1.2 | 8 | 45 | 89.2 | 100.0 | 85~86 | 300~600 | ok |
| yolo26-x-seg_640x640.dxnn | 16.1 ±0.7 | 4 | 23 | 80.6 | 100.0 | 84~85 | 300~800 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-seg_640x640.dxnn | 7 | [3]:66.5 · [4]:83.3 · [5]:94.7 · [6]:95.3 · **[7]:95.5 ★** · [8]:95.5 |
| yolo26-s-seg_640x640.dxnn | 8 | [3]:55.8 · [4]:68.6 · [5]:82.2 · [6]:94.4 · [7]:95.3 · **[8]:95.4 ★** · [9]:95.2 · [10]:95.3 |
| yolo26-m-seg_640x640.dxnn | 5 | [3]:45.0 · [4]:53.7 · **[5]:58.7 ★** · [6]:57.3 · [7]:58.6 · [8]:58.2 |
| yolo26-l-seg_640x640.dxnn | 8 | [3]:37.0 · [4]:46.2 · [5]:47.8 · [6]:46.7 · [7]:47.5 · **[8]:48.0 ★** · [9]:46.7 |
| yolo26-x-seg_640x640.dxnn | 4 | [3]:22.8 · **[4]:26.8 ★** · [5]:26.3 · [6]:25.9 · [7]:25.1 · [8]:24.3 |


#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 73.8 ±0.3 | 5 | 69 | 91.8 | 100.0 | 72~77 | 1000 | ok |
| yolo26-s-obb_1024x1024.dxnn | 44.5 ±0.1 | 4 | 43 | 90.7 | 100.0 | 77~82 | 1000 | ok |
| yolo26-m-obb_1024x1024.dxnn | 22.8 ±2.0 | 4 | 24 | 86.0 | 100.0 | 85~86 | 300~1000 | ok |
| yolo26-l-obb_1024x1024.dxnn | 17.6 ±1.3 | 4 | 19 | 84.1 | 100.0 | 85 | 300~1000 | ok |
| yolo26-x-obb_1024x1024.dxnn | 10.3 ±0.7 | 4 | 12 | 83.9 | 100.0 | 84~85 | 400~1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-obb_1024x1024.dxnn | 5 | [3]:53.0 · [4]:68.1 · **[5]:72.3 ★** · [6]:70.2 · [7]:69.9 · [8]:70.1 |
| yolo26-s-obb_1024x1024.dxnn | 4 | [3]:38.5 · **[4]:44.1 ★** · [5]:42.5 · [6]:43.2 · [7]:43.2 · [8]:43.4 |
| yolo26-m-obb_1024x1024.dxnn | 4 | [3]:26.3 · **[4]:29.4 ★** · [5]:28.3 · [6]:27.4 · [7]:28.1 · [8]:28.2 |
| yolo26-l-obb_1024x1024.dxnn | 4 | [3]:20.6 · **[4]:22.0 ★** · [5]:21.0 · [6]:21.1 · [7]:21.2 · [8]:21.3 |
| yolo26-x-obb_1024x1024.dxnn | 4 | [3]:11.6 · **[4]:12.6 ★** · [5]:12.2 · [6]:12.2 · [7]:12.3 · [8]:12.2 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 73.7 ±0.3 | 4 | 35 | 91.0 | 100.0 | 73~78 | 1000 | ok |
| yolo26-s-obb_1024x1024.dxnn | 46.0 ±0.3 | 4 | 23 | 89.8 | 100.0 | 77~83 | 800~1000 | ok |
| yolo26-m-obb_1024x1024.dxnn | 23.1 ±1.8 | 4 | 13 | 83.9 | 100.0 | 84~86 | 300~800 | ok |
| yolo26-l-obb_1024x1024.dxnn | 20.7 ±1.1 | 4 | 10 | 85.4 | 100.0 | 82~84 | 400~1000 | ok |
| yolo26-x-obb_1024x1024.dxnn | 10.2 ±0.3 | 4 | 6 | 84.5 | 100.0 | 84~85 | 400~1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-obb_1024x1024.dxnn | 4 | [3]:55.5 · **[4]:73.2 ★** · [5]:70.7 · [6]:69.5 · [7]:70.1 · [8]:70.2 |
| yolo26-s-obb_1024x1024.dxnn | 4 | [3]:37.6 · **[4]:45.7 ★** · [5]:42.3 · [6]:43.2 · [7]:43.4 · [8]:43.4 |
| yolo26-m-obb_1024x1024.dxnn | 4 | [3]:26.8 · **[4]:29.4 ★** · [5]:28.3 · [6]:27.8 · [7]:28.0 · [8]:28.3 |
| yolo26-l-obb_1024x1024.dxnn | 4 | [3]:19.4 · **[4]:21.7 ★** · [5]:21.1 · [6]:21.0 · [7]:21.0 · [8]:21.1 |
| yolo26-x-obb_1024x1024.dxnn | 4 | [3]:11.6 · **[4]:12.5 ★** · [5]:12.2 · [6]:12.3 · [7]:12.3 · [8]:12.2 |


#### Classification

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n_224x224.dxnn | 3018.9 ±8.4 | 8 | 52 | 89.3 | 97.1 | 62~64 | 1000 | ok |
| yolo26-s_224x224.dxnn | 1597.6 ±1.6 | 9 | 34 | 88.5 | 97.4 | 64~67 | 1000 | ok |
| yolo26-m_224x224.dxnn | 1067.6 ±1.9 | 4 | 21 | 91.0 | 97.8 | 75~80 | 1000 | ok |
| yolo26-l_224x224.dxnn | 715.0 ±3.4 | 4 | 15 | 90.6 | 98.5 | 72~76 | 1000 | ok |
| yolo26-x_224x224.dxnn | 358.9 ±1.7 | 6 | 8 | 90.0 | 99.9 | 77~82 | 800~1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n_224x224.dxnn | 8 | [3]:1934.4 · [4]:2612.8 · [5]:2919.2 · [6]:3021.2 · [7]:3022.3 · **[8]:3023.0 ★** · [9]:2961.1 |
| yolo26-s_224x224.dxnn | 9 | [3]:1261.4 · [4]:1565.8 · [5]:1561.9 · [6]:1597.2 · [7]:1599.4 · [8]:1600.9 · **[9]:1603.5 ★** · [10]:1603.4 |
| yolo26-m_224x224.dxnn | 4 | [3]:875.9 · **[4]:1064.0 ★** · [5]:1062.7 · [6]:1057.6 · [7]:1042.7 · [8]:1060.1 |
| yolo26-l_224x224.dxnn | 4 | [3]:625.0 · **[4]:713.4 ★** · [5]:698.5 · [6]:703.5 · [7]:705.0 · [8]:704.5 |
| yolo26-x_224x224.dxnn | 6 | [3]:335.3 · [4]:354.3 · [5]:358.0 · **[6]:358.6 ★** · [7]:356.6 · [8]:353.3 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n_224x224.dxnn | 3019.9 ±3.6 | 9 | 54 | 89.1 | 97.1 | 62~64 | 1000 | ok |
| yolo26-s_224x224.dxnn | 1596.8 ±2.1 | 8 | 33 | 89.6 | 97.4 | 64~67 | 1000 | ok |
| yolo26-m_224x224.dxnn | 1066.2 ±3.0 | 4 | 21 | 88.9 | 97.6 | 76~82 | 1000 | ok |
| yolo26-l_224x224.dxnn | 712.8 ±3.9 | 4 | 14 | 89.6 | 98.3 | 72~77 | 1000 | ok |
| yolo26-x_224x224.dxnn | 362.5 ±0.4 | 4 | 7 | 90.5 | 99.6 | 75~81 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n_224x224.dxnn | 9 | [3]:1939.7 · [4]:2598.6 · [5]:2950.1 · [6]:3015.7 · [7]:3018.7 · [8]:3020.1 · **[9]:3025.4 ★** · [10]:2984.2 |
| yolo26-s_224x224.dxnn | 8 | [3]:1256.6 · [4]:1566.8 · [5]:1558.0 · [6]:1596.3 · [7]:1601.6 · **[8]:1602.9 ★** · [9]:1602.3 · [10]:1600.9 |
| yolo26-m_224x224.dxnn | 4 | [3]:889.6 · **[4]:1065.8 ★** · [5]:1061.3 · [6]:1057.6 · [7]:1042.7 · [8]:1055.8 |
| yolo26-l_224x224.dxnn | 4 | [3]:625.4 · **[4]:705.7 ★** · [5]:701.4 · [6]:703.5 · [7]:701.5 · [8]:703.0 |
| yolo26-x_224x224.dxnn | 4 | [3]:332.6 · **[4]:359.9 ★** · [5]:356.2 · [6]:358.6 · [7]:358.1 · [8]:355.8 |


### Latency (Single-Core, Sync)

#### Object Detection

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_640x640.dxnn | 38.5 ±0.5 | 26.00 | 23.52 | 2.49 | 43 | ok |
| yolo26-s_640x640.dxnn | 31.6 ±0.6 | 31.60 | 29.10 | 2.49 | 52 | ok |
| yolo26-m_640x640.dxnn | 25.2 ±9.7 | 39.63 | 37.32 | 2.31 | 53 | ok |
| yolo26-l_640x640.dxnn | 20.4 ±5.2 | 48.99 | 46.41 | 2.57 | 54 | ok |
| yolo26-x_640x640.dxnn | 12.6 ±2.3 | 79.11 | 76.57 | 2.54 | 56 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_640x640.dxnn | 44.4 ±0.1 | 22.50 | 22.50 | N/A | 51 | ok |
| yolo26-s_640x640.dxnn | 34.2 ±0.5 | 29.20 | 29.20 | N/A | 52 | ok |
| yolo26-m_640x640.dxnn | 25.3 ±7.0 | 39.60 | 39.60 | N/A | 53 | ok |
| yolo26-l_640x640.dxnn | 21.6 ±3.4 | 46.40 | 46.40 | N/A | 54 | ok |
| yolo26-x_640x640.dxnn | 13.3 ±1.1 | 75.43 | 75.43 | N/A | 57 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-pose_640x640.dxnn | 48.2 ±0.9 | 20.76 | 19.35 | 1.41 | 52 | ok |
| yolo26-s-pose_640x640.dxnn | 36.3 ±0.9 | 27.55 | 26.08 | 1.47 | 52 | ok |
| yolo26-m-pose_640x640.dxnn | 27.1 ±6.7 | 36.96 | 35.42 | 1.54 | 54 | ok |
| yolo26-l-pose_640x640.dxnn | 21.8 ±7.0 | 45.89 | 44.41 | 1.47 | 55 | ok |
| yolo26-x-pose_640x640.dxnn | 13.2 ±1.6 | 75.78 | 74.26 | 1.52 | 58 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-pose_640x640.dxnn | 51.8 ±1.5 | 19.29 | 19.29 | N/A | 52 | ok |
| yolo26-s-pose_640x640.dxnn | 35.9 ±1.1 | 27.83 | 27.83 | N/A | 52 | ok |
| yolo26-m-pose_640x640.dxnn | 28.4 ±4.2 | 35.17 | 35.17 | N/A | 54 | ok |
| yolo26-l-pose_640x640.dxnn | 22.8 ±8.7 | 43.80 | 43.80 | N/A | 55 | ok |
| yolo26-x-pose_640x640.dxnn | 13.7 ±3.4 | 73.13 | 73.13 | N/A | 57 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-seg_640x640.dxnn | 24.6 ±0.4 | 40.69 | 37.62 | 3.07 | 52 | ok |
| yolo26-s-seg_640x640.dxnn | 20.6 ±0.4 | 48.46 | 45.58 | 2.88 | 53 | ok |
| yolo26-m-seg_640x640.dxnn | 15.4 ±1.3 | 64.86 | 61.90 | 2.96 | 55 | ok |
| yolo26-l-seg_640x640.dxnn | 13.6 ±1.1 | 73.66 | 70.69 | 2.97 | 56 | ok |
| yolo26-x-seg_640x640.dxnn | 8.5 ±0.9 | 117.40 | 114.29 | 3.11 | 59 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-seg_640x640.dxnn | 26.4 ±0.1 | 37.81 | 37.81 | N/A | 52 | ok |
| yolo26-s-seg_640x640.dxnn | 21.5 ±0.9 | 46.46 | 46.46 | N/A | 53 | ok |
| yolo26-m-seg_640x640.dxnn | 15.1 ±3.7 | 66.27 | 66.27 | N/A | 55 | ok |
| yolo26-l-seg_640x640.dxnn | 14.1 ±1.2 | 70.97 | 70.97 | N/A | 56 | ok |
| yolo26-x-seg_640x640.dxnn | 8.8 ±0.7 | 113.04 | 113.04 | N/A | 59 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-obb_1024x1024.dxnn | 25.3 ±0.3 | 39.55 | 37.87 | 1.68 | 53 | ok |
| yolo26-s-obb_1024x1024.dxnn | 17.1 ±0.1 | 58.41 | 56.66 | 1.74 | 54 | ok |
| yolo26-m-obb_1024x1024.dxnn | 12.8 ±2.0 | 78.34 | 76.62 | 1.71 | 58 | ok |
| yolo26-l-obb_1024x1024.dxnn | 9.9 ±1.4 | 100.57 | 98.82 | 1.74 | 60 | ok |
| yolo26-x-obb_1024x1024.dxnn | 5.6 ±0.8 | 178.33 | 176.49 | 1.83 | 61 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-obb_1024x1024.dxnn | 25.4 ±0.3 | 39.45 | 39.45 | N/A | 53 | ok |
| yolo26-s-obb_1024x1024.dxnn | 17.8 ±0.3 | 56.03 | 56.03 | N/A | 55 | ok |
| yolo26-m-obb_1024x1024.dxnn | 13.0 ±1.8 | 76.79 | 76.79 | N/A | 58 | ok |
| yolo26-l-obb_1024x1024.dxnn | 10.2 ±1.1 | 98.49 | 98.49 | N/A | 59 | ok |
| yolo26-x-obb_1024x1024.dxnn | 5.7 ±0.3 | 176.03 | 176.03 | N/A | 62 | ok |

#### Classification

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_224x224.dxnn | 655.8 ±8.4 | 1.52 | 1.52 | N/A | 50 | ok |
| yolo26-s_224x224.dxnn | 458.8 ±1.6 | 2.18 | 2.18 | N/A | 46 | ok |
| yolo26-m_224x224.dxnn | 342.8 ±1.9 | 2.92 | 2.92 | N/A | 50 | ok |
| yolo26-l_224x224.dxnn | 230.3 ±3.4 | 4.34 | 4.34 | N/A | 51 | ok |
| yolo26-x_224x224.dxnn | 138.1 ±1.7 | 7.24 | 7.24 | N/A | 52 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_224x224.dxnn | 669.4 ±3.6 | 1.49 | 1.49 | N/A | 48 | ok |
| yolo26-s_224x224.dxnn | 440.2 ±2.1 | 2.27 | 2.27 | N/A | 46 | ok |
| yolo26-m_224x224.dxnn | 332.9 ±3.0 | 3.00 | 3.00 | N/A | 51 | ok |
| yolo26-l_224x224.dxnn | 229.9 ±3.9 | 4.35 | 4.35 | N/A | 50 | ok |
| yolo26-x_224x224.dxnn | 138.5 ±0.4 | 7.22 | 7.22 | N/A | 52 | ok |

## E2E Pipeline (Single-Stream)

### Object Detection

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | avdec_h264 | 3455 | 3 | 68.0 ±0.1 | 50.84 | 313 | 21.0 | 45.9 | 52~53 | 1000 | 320 | ok |
| yolo26-s_640x640.dxnn | avdec_h264 | 3455 | 3 | 67.5 ±0.1 | 51.21 | 308 | 36.9 | 66.7 | 60~62 | 1000 | 343 | ok |
| yolo26-m_640x640.dxnn | avdec_h264 | 3455 | 3 | 67.0 ±0.1 | 51.54 | 282 | 64.9 | 86.5 | 75~83 | 800~1000 | 374 | ok |
| yolo26-l_640x640.dxnn | avdec_h264 | 3455 | 3 | 56.3 ±8.1 | 61.38 | 200 | 88.5 | 100.0 | 79~84 | 400~1000 | 387 | ok |
| yolo26-x_640x640.dxnn | avdec_h264 | 3455 | 3 | 21.9 ±1.5 | 157.88 | 67 | 93.6 | 100.0 | 85~86 | 300~1000 | 480 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | avdec_h264 | 3455 | 3 | 79.8 ±0.2 | 43.29 | 306 | 22.1 | 64.2 | 54~55 | 1000 | 353 | ok |
| yolo26-s_640x640.dxnn | avdec_h264 | 3455 | 3 | 80.2 ±0.5 | 43.09 | 304 | 40.5 | 75.8 | 58~63 | 1000 | 373 | ok |
| yolo26-m_640x640.dxnn | avdec_h264 | 3455 | 3 | 77.8 ±4.1 | 44.40 | 287 | 83.1 | 100.0 | 75~84 | 400~1000 | 403 | ok |
| yolo26-l_640x640.dxnn | avdec_h264 | 3455 | 3 | 57.6 ±8.0 | 60.01 | 197 | 92.2 | 100.0 | 79~85 | 400~1000 | 401 | ok |
| yolo26-x_640x640.dxnn | avdec_h264 | 3455 | 3 | 21.2 ±1.4 | 163.00 | 73 | 94.2 | 100.0 | 85~86 | 300~1000 | 493 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n_640x640.dxnn | 68.0 | 79.8 | -11.9 | -14.9% |
| yolo26-s_640x640.dxnn | 67.5 | 80.2 | -12.7 | -15.9% |
| yolo26-m_640x640.dxnn | 67.0 | 77.8 | -10.8 | -13.9% |
| yolo26-l_640x640.dxnn | 56.3 | 57.6 | -1.3 | -2.2% |
| yolo26-x_640x640.dxnn | 21.9 | 21.2 | +0.7 | +3.2% |

### Pose Estimation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 82.3 ±0.2 | 41.96 | 321 | 26.7 | 57.6 | 56~58 | 1000 | 309 | ok |
| yolo26-s-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 81.9 ±0.4 | 42.18 | 313 | 48.3 | 75.4 | 62~67 | 1000 | 333 | ok |
| yolo26-m-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 69.9 ±11.2 | 49.41 | 211 | 89.5 | 100.0 | 78~85 | 400~1000 | 365 | ok |
| yolo26-l-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 46.0 ±12.2 | 75.04 | 123 | 93.0 | 100.0 | 83~86 | 300~1000 | 381 | ok |
| yolo26-x-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 22.7 ±4.5 | 151.94 | 61 | 93.4 | 100.0 | 85~87 | 300~1000 | 475 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 112.4 ±0.1 | 30.75 | 302 | 36.2 | 68.0 | 57~60 | 1000 | 295 | ok |
| yolo26-s-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 112.6 ±1.0 | 30.69 | 296 | 68.6 | 88.4 | 64~70 | 1000 | 323 | ok |
| yolo26-m-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 69.8 ±11.9 | 49.48 | 150 | 90.0 | 100.0 | 79~85 | 400~1000 | 353 | ok |
| yolo26-l-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 49.2 ±10.7 | 70.27 | 103 | 93.1 | 100.0 | 82~86 | 300~1000 | 370 | ok |
| yolo26-x-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 20.6 ±2.1 | 168.03 | 46 | 94.0 | 100.0 | 85~86 | 300~1000 | 464 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-pose_640x640.dxnn | 82.3 | 112.4 | -30.0 | -26.7% |
| yolo26-s-pose_640x640.dxnn | 81.9 | 112.6 | -30.7 | -27.2% |
| yolo26-m-pose_640x640.dxnn | 69.9 | 69.8 | +0.1 | +0.1% |
| yolo26-l-pose_640x640.dxnn | 46.0 | 49.2 | -3.1 | -6.4% |
| yolo26-x-pose_640x640.dxnn | 22.7 | 20.6 | +2.2 | +10.6% |

### Segmentation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 44.8 ±0.2 | 77.07 | 311 | 18.5 | 42.3 | 57~59 | 1000 | 417 | ok |
| yolo26-s-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 44.7 ±0.4 | 77.32 | 301 | 32.5 | 65.4 | 64~69 | 1000 | 443 | ok |
| yolo26-m-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 35.0 ±5.6 | 98.68 | 178 | 86.4 | 100.0 | 85~86 | 300~1000 | 474 | ok |
| yolo26-l-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 29.1 ±4.5 | 118.89 | 135 | 91.1 | 100.0 | 85~86 | 300~1000 | 487 | ok |
| yolo26-x-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 13.0 ±0.1 | 266.52 | 55 | 95.0 | 100.0 | 85~86 | 300~600 | 596 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 54.9 ±0.1 | 62.89 | 342 | 21.3 | 55.8 | 58~60 | 1000 | 460 | ok |
| yolo26-s-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 55.3 ±0.5 | 62.48 | 331 | 39.3 | 74.0 | 66~69 | 1000 | 484 | ok |
| yolo26-m-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 34.6 ±6.9 | 99.73 | 164 | 91.7 | 100.0 | 84~86 | 300~1000 | 496 | ok |
| yolo26-l-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 26.9 ±1.2 | 128.69 | 120 | 94.6 | 100.0 | 85 | 300~800 | 505 | ok |
| yolo26-x-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 12.8 ±0.2 | 269.22 | 58 | 95.3 | 100.0 | 85~86 | 300~700 | 612 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-seg_640x640.dxnn | 44.8 | 54.9 | -10.1 | -18.4% |
| yolo26-s-seg_640x640.dxnn | 44.7 | 55.3 | -10.6 | -19.2% |
| yolo26-m-seg_640x640.dxnn | 35.0 | 34.6 | +0.4 | +1.1% |
| yolo26-l-seg_640x640.dxnn | 29.1 | 26.9 | +2.2 | +8.2% |
| yolo26-x-seg_640x640.dxnn | 13.0 | 12.8 | +0.1 | +1.0% |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 67.7 ±0.2 | 39.02 | 280 | 79.3 | 96.4 | 65~72 | 1000 | 344 | ok |
| yolo26-s-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 44.1 ±0.7 | 59.80 | 145 | 91.4 | 100.0 | 75~85 | 600~1000 | 371 | ok |
| yolo26-m-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 18.2 ±0.4 | 144.92 | 61 | 95.8 | 100.0 | 86 | 200~700 | 408 | ok |
| yolo26-l-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 14.3 ±0.9 | 184.86 | 49 | 92.9 | 100.0 | 84~87 | 200~1000 | 422 | ok |
| yolo26-x-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 8.6 ±0.1 | 306.35 | 30 | 92.4 | 100.0 | 84~85 | 300~800 | 524 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 72.3 ±0.5 | 36.51 | 247 | 88.9 | 100.0 | 66~74 | 1000 | 346 | ok |
| yolo26-s-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 44.1 ±0.3 | 59.82 | 143 | 91.1 | 100.0 | 75~84 | 800~1000 | 372 | ok |
| yolo26-m-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 18.8 ±2.0 | 140.52 | 63 | 95.9 | 100.0 | 86 | 200~1000 | 401 | ok |
| yolo26-l-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 16.5 ±1.0 | 160.14 | 56 | 92.7 | 100.0 | 85 | 300~1000 | 418 | ok |
| yolo26-x-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 8.7 ±0.3 | 302.83 | 31 | 93.0 | 100.0 | 84~85 | 300~1000 | 519 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-obb_1024x1024.dxnn | 67.7 | 72.3 | -4.7 | -6.4% |
| yolo26-s-obb_1024x1024.dxnn | 44.1 | 44.1 | +0.0 | +0.0% |
| yolo26-m-obb_1024x1024.dxnn | 18.2 | 18.8 | -0.6 | -3.0% |
| yolo26-l-obb_1024x1024.dxnn | 14.3 | 16.5 | -2.2 | -13.4% |
| yolo26-x-obb_1024x1024.dxnn | 8.6 | 8.7 | -0.1 | -1.1% |

### Classification

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_224x224.dxnn | avdec_h264 | 3455 | 3 | 189.3 ±0.7 | 18.25 | 270 | 4.8 | 14.5 | 48~50 | 1000 | 202 | ok |
| yolo26-s_224x224.dxnn | avdec_h264 | 3455 | 3 | 189.0 ±0.3 | 18.28 | 269 | 8.9 | 25.8 | 46~47 | 1000 | 217 | ok |
| yolo26-m_224x224.dxnn | avdec_h264 | 3455 | 3 | 189.1 ±1.0 | 18.27 | 269 | 13.2 | 34.9 | 52~53 | 1000 | 228 | ok |
| yolo26-l_224x224.dxnn | avdec_h264 | 3455 | 3 | 188.9 ±0.4 | 18.29 | 268 | 20.8 | 47.3 | 52~53 | 1000 | 250 | ok |
| yolo26-x_224x224.dxnn | avdec_h264 | 3455 | 3 | 187.7 ±0.3 | 18.41 | 267 | 39.9 | 68.9 | 56~59 | 1000 | 296 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_224x224.dxnn | avdec_h264 | 3455 | 3 | 189.1 ±0.9 | 18.28 | 270 | 4.7 | 14.5 | 46~50 | 1000 | 218 | ok |
| yolo26-s_224x224.dxnn | avdec_h264 | 3455 | 3 | 189.3 ±0.3 | 18.25 | 270 | 9.0 | 26.0 | 49~50 | 1000 | 229 | ok |
| yolo26-m_224x224.dxnn | avdec_h264 | 3455 | 3 | 189.5 ±0.3 | 18.24 | 270 | 13.1 | 35.1 | 52 | 1000 | 243 | ok |
| yolo26-l_224x224.dxnn | avdec_h264 | 3455 | 3 | 188.6 ±0.4 | 18.32 | 268 | 20.4 | 48.0 | 52~53 | 1000 | 253 | ok |
| yolo26-x_224x224.dxnn | avdec_h264 | 3455 | 3 | 187.2 ±0.8 | 18.45 | 267 | 38.1 | 67.4 | 54~58 | 1000 | 286 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n_224x224.dxnn | 189.3 | 189.1 | +0.3 | +0.1% |
| yolo26-s_224x224.dxnn | 189.0 | 189.3 | -0.3 | -0.2% |
| yolo26-m_224x224.dxnn | 189.1 | 189.5 | -0.3 | -0.2% |
| yolo26-l_224x224.dxnn | 188.9 | 188.6 | +0.3 | +0.2% |
| yolo26-x_224x224.dxnn | 187.7 | 187.2 | +0.4 | +0.2% |

## E2E Pipeline (Multi-Stream)

### Object Detection

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | 2 | 3 | 67.4 ±0.2 | 33.7 | 313 | 21.0 | 48.2 | 55~56 | 1000 | 458 | ok |
| yolo26-n_640x640.dxnn | 3 | 3 | 67.2 ±0.1 | 22.4 | 314 | 21.1 | 47.0 | 55 | 1000 | 555 | ok |
| yolo26-s_640x640.dxnn | 2 | 3 | 66.2 ±0.3 | 33.1 | 308 | 36.4 | 67.8 | 64~65 | 1000 | 475 | ok |
| yolo26-s_640x640.dxnn | 3 | 3 | 66.3 ±1.2 | 22.1 | 307 | 37.2 | 67.0 | 65 | 1000 | 576 | ok |
| yolo26-m_640x640.dxnn | 2 | 3 | 57.5 ±1.3 | 28.7 | 193 | 92.1 | 100.0 | 85 | 300~800 | 508 | ok |
| yolo26-m_640x640.dxnn | 1 | 3 | 67.0 ±0.1 | 67.0 | 282 | 64.9 | 86.5 | 75~83 | 800~1000 | 374 | ok |
| yolo26-l_640x640.dxnn | 1 | 3 | 56.3 ±8.1 | 56.3 | 200 | 88.5 | 100.0 | 79~84 | 400~1000 | 387 | ok |
| yolo26-l_640x640.dxnn | 2 | 3 | 48.1 ±0.7 | 24.0 | 159 | 92.2 | 100.0 | 83~84 | 400~1000 | 519 | ok |
| yolo26-x_640x640.dxnn | 1 | 3 | 21.9 ±1.5 | 21.9 | 67 | 93.6 | 100.0 | 85~86 | 300~1000 | 480 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | 2 | 3 | 80.0 ±0.2 | 40.0 | 309 | 22.7 | 65.5 | 56~58 | 1000 | 483 | ok |
| yolo26-n_640x640.dxnn | 3 | 3 | 80.2 ±0.4 | 26.8 | 303 | 23.0 | 66.0 | 58 | 1000 | 582 | ok |
| yolo26-s_640x640.dxnn | 2 | 3 | 80.3 ±0.4 | 40.1 | 306 | 42.0 | 76.0 | 68~70 | 1000 | 502 | ok |
| yolo26-s_640x640.dxnn | 3 | 3 | 80.1 ±0.8 | 26.7 | 307 | 42.0 | 75.8 | 68 | 1000 | 604 | ok |
| yolo26-m_640x640.dxnn | 2 | 3 | 58.1 ±0.6 | 29.0 | 199 | 93.9 | 100.0 | 84~85 | 300~1000 | 518 | ok |
| yolo26-m_640x640.dxnn | 1 | 3 | 77.8 ±4.1 | 77.8 | 287 | 83.1 | 100.0 | 75~84 | 400~1000 | 403 | ok |
| yolo26-l_640x640.dxnn | 1 | 3 | 57.6 ±8.0 | 57.6 | 197 | 92.2 | 100.0 | 79~85 | 400~1000 | 401 | ok |
| yolo26-l_640x640.dxnn | 2 | 3 | 45.1 ±0.9 | 22.5 | 153 | 93.2 | 100.0 | 84~85 | 400~800 | 534 | ok |
| yolo26-x_640x640.dxnn | 1 | 3 | 21.2 ±1.4 | 21.2 | 73 | 94.2 | 100.0 | 85~86 | 300~1000 | 493 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n_640x640.dxnn | 2 | 33.7 | 2 | 40.0 |
| yolo26-s_640x640.dxnn | 2 | 33.1 | 2 | 40.1 |
| yolo26-m_640x640.dxnn | 1 | 67.0 | 1 | 77.8 |
| yolo26-l_640x640.dxnn | 1 | 56.3 | 1 | 57.6 |

### Pose Estimation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 2 | 3 | 80.4 ±1.1 | 40.2 | 322 | 27.4 | 54.3 | 62 | 1000 | 449 | ok |
| yolo26-n-pose_640x640.dxnn | 3 | 3 | 79.8 ±1.1 | 26.6 | 321 | 27.3 | 56.5 | 62 | 1000 | 553 | ok |
| yolo26-s-pose_640x640.dxnn | 2 | 3 | 79.4 ±0.7 | 39.7 | 315 | 47.7 | 76.0 | 72~73 | 1000 | 471 | ok |
| yolo26-s-pose_640x640.dxnn | 3 | 3 | 80.3 ±0.3 | 26.8 | 316 | 49.2 | 74.6 | 74~75 | 1000 | 574 | ok |
| yolo26-m-pose_640x640.dxnn | 2 | 3 | 59.1 ±9.5 | 29.5 | 165 | 93.5 | 100.0 | 84~86 | 300~1000 | 500 | ok |
| yolo26-m-pose_640x640.dxnn | 1 | 3 | 69.9 ±11.2 | 69.9 | 211 | 89.5 | 100.0 | 78~85 | 400~1000 | 365 | ok |
| yolo26-l-pose_640x640.dxnn | 1 | 3 | 46.0 ±12.2 | 46.0 | 123 | 93.0 | 100.0 | 83~86 | 300~1000 | 381 | ok |
| yolo26-l-pose_640x640.dxnn | 2 | 3 | 42.5 ±8.3 | 21.2 | 111 | 94.9 | 100.0 | 85 | 300~1000 | 513 | ok |
| yolo26-x-pose_640x640.dxnn | 1 | 3 | 22.7 ±4.5 | 22.7 | 61 | 93.4 | 100.0 | 85~87 | 300~1000 | 475 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 3 | 3 | 112.0 ±1.1 | 37.3 | 328 | 41.1 | 62.5 | 65~66 | 1000 | 556 | ok |
| yolo26-n-pose_640x640.dxnn | 4 | 3 | 111.7 ±0.9 | 27.9 | 330 | 41.0 | 62.9 | 67~68 | 1000 | 649 | ok |
| yolo26-s-pose_640x640.dxnn | 3 | 3 | 110.3 ±0.8 | 36.8 | 312 | 71.4 | 88.6 | 82~83 | 800~1000 | 563 | ok |
| yolo26-s-pose_640x640.dxnn | 4 | 3 | 109.6 ±0.4 | 27.4 | 310 | 73.7 | 96.4 | 83~85 | 600~1000 | 667 | ok |
| yolo26-m-pose_640x640.dxnn | 2 | 3 | 50.2 ±0.9 | 25.1 | 107 | 95.5 | 100.0 | 86 | 300~800 | 490 | ok |
| yolo26-m-pose_640x640.dxnn | 1 | 3 | 69.8 ±11.9 | 69.8 | 150 | 90.0 | 100.0 | 79~85 | 400~1000 | 353 | ok |
| yolo26-l-pose_640x640.dxnn | 1 | 3 | 49.2 ±10.7 | 49.2 | 103 | 93.1 | 100.0 | 82~86 | 300~1000 | 370 | ok |
| yolo26-l-pose_640x640.dxnn | 2 | 3 | 37.5 ±2.1 | 18.8 | 81 | 95.6 | 100.0 | 85~86 | 300~800 | 500 | ok |
| yolo26-x-pose_640x640.dxnn | 1 | 3 | 20.6 ±2.1 | 20.6 | 46 | 94.0 | 100.0 | 85~86 | 300~1000 | 464 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-pose_640x640.dxnn | 2 | 40.2 | 3 | 37.3 |
| yolo26-s-pose_640x640.dxnn | 2 | 39.7 | 3 | 36.8 |
| yolo26-m-pose_640x640.dxnn | 1 | 69.9 | 1 | 69.8 |
| yolo26-l-pose_640x640.dxnn | 1 | 46.0 | 1 | 49.2 |

### Segmentation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 1 | 3 | 44.8 ±0.2 | 44.8 | 311 | 18.5 | 42.3 | 57~59 | 1000 | 417 | ok |
| yolo26-n-seg_640x640.dxnn | 2 | 3 | 43.5 ±0.5 | 21.8 | 314 | 17.7 | 40.6 | 59~61 | 1000 | 560 | ok |
| yolo26-s-seg_640x640.dxnn | 1 | 3 | 44.7 ±0.4 | 44.7 | 301 | 32.5 | 65.4 | 64~69 | 1000 | 443 | ok |
| yolo26-s-seg_640x640.dxnn | 2 | 3 | 44.0 ±0.8 | 22.0 | 303 | 32.7 | 63.4 | 70~71 | 1000 | 584 | ok |
| yolo26-m-seg_640x640.dxnn | 1 | 3 | 35.0 ±5.6 | 35.0 | 178 | 86.4 | 100.0 | 85~86 | 300~1000 | 474 | ok |
| yolo26-m-seg_640x640.dxnn | 2 | 3 | 30.9 ±0.6 | 15.4 | 141 | 95.5 | 100.0 | 85~86 | 300~700 | 616 | ok |
| yolo26-l-seg_640x640.dxnn | 1 | 3 | 29.1 ±4.5 | 29.1 | 135 | 91.1 | 100.0 | 85~86 | 300~1000 | 487 | ok |
| yolo26-x-seg_640x640.dxnn | 1 | 3 | 13.0 ±0.1 | 13.0 | 55 | 95.0 | 100.0 | 85~86 | 300~600 | 596 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 1 | 3 | 54.9 ±0.1 | 54.9 | 342 | 21.3 | 55.8 | 58~60 | 1000 | 460 | ok |
| yolo26-n-seg_640x640.dxnn | 2 | 3 | 54.5 ±0.1 | 27.2 | 340 | 21.0 | 57.5 | 61~62 | 1000 | 603 | ok |
| yolo26-s-seg_640x640.dxnn | 1 | 3 | 55.3 ±0.5 | 55.3 | 331 | 39.3 | 74.0 | 66~69 | 1000 | 484 | ok |
| yolo26-s-seg_640x640.dxnn | 2 | 3 | 54.2 ±0.9 | 27.1 | 335 | 39.4 | 73.0 | 74~75 | 1000 | 626 | ok |
| yolo26-m-seg_640x640.dxnn | 1 | 3 | 34.6 ±6.9 | 34.6 | 164 | 91.7 | 100.0 | 84~86 | 300~1000 | 496 | ok |
| yolo26-m-seg_640x640.dxnn | 2 | 3 | 30.8 ±0.3 | 15.4 | 139 | 96.0 | 100.0 | 85~86 | 200~700 | 638 | ok |
| yolo26-l-seg_640x640.dxnn | 1 | 3 | 26.9 ±1.2 | 26.9 | 120 | 94.6 | 100.0 | 85 | 300~800 | 505 | ok |
| yolo26-x-seg_640x640.dxnn | 1 | 3 | 12.8 ±0.2 | 12.8 | 58 | 95.3 | 100.0 | 85~86 | 300~700 | 612 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-seg_640x640.dxnn | 1 | 44.8 | 1 | 54.9 |
| yolo26-s-seg_640x640.dxnn | 1 | 44.7 | 1 | 55.3 |
| yolo26-m-seg_640x640.dxnn | 1 | 35.0 | 1 | 34.6 |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 2 | 3 | 67.6 ±0.3 | 33.8 | 290 | 79.6 | 94.9 | 80~83 | 1000 | 481 | ok |
| yolo26-n-obb_1024x1024.dxnn | 3 | 3 | 67.0 ±0.4 | 22.3 | 288 | 80.9 | 97.4 | 83~85 | 600~1000 | 586 | ok |
| yolo26-s-obb_1024x1024.dxnn | 1 | 3 | 44.1 ±0.7 | 44.1 | 145 | 91.4 | 100.0 | 75~85 | 600~1000 | 371 | ok |
| yolo26-s-obb_1024x1024.dxnn | 2 | 3 | 36.0 ±1.4 | 18.0 | 125 | 93.5 | 100.0 | 85~86 | 300~1000 | 505 | ok |
| yolo26-m-obb_1024x1024.dxnn | 1 | 3 | 18.2 ±0.4 | 18.2 | 61 | 95.8 | 100.0 | 86 | 200~700 | 408 | ok |
| yolo26-l-obb_1024x1024.dxnn | 1 | 3 | 14.3 ±0.9 | 14.3 | 49 | 92.9 | 100.0 | 84~87 | 200~1000 | 422 | ok |
| yolo26-x-obb_1024x1024.dxnn | 1 | 3 | 8.6 ±0.1 | 8.6 | 30 | 92.4 | 100.0 | 84~85 | 300~800 | 524 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 2 | 3 | 71.5 ±0.9 | 35.8 | 255 | 91.5 | 100.0 | 84~86 | 600~1000 | 480 | ok |
| yolo26-n-obb_1024x1024.dxnn | 3 | 3 | 66.8 ±1.5 | 22.3 | 235 | 92.8 | 100.0 | 85~86 | 400~1000 | 583 | ok |
| yolo26-s-obb_1024x1024.dxnn | 1 | 3 | 44.1 ±0.3 | 44.1 | 143 | 91.1 | 100.0 | 75~84 | 800~1000 | 372 | ok |
| yolo26-s-obb_1024x1024.dxnn | 2 | 3 | 37.0 ±1.5 | 18.5 | 125 | 93.7 | 100.0 | 85~86 | 400~1000 | 501 | ok |
| yolo26-m-obb_1024x1024.dxnn | 1 | 3 | 18.8 ±2.0 | 18.8 | 63 | 95.9 | 100.0 | 86 | 200~1000 | 401 | ok |
| yolo26-l-obb_1024x1024.dxnn | 1 | 3 | 16.5 ±1.0 | 16.5 | 56 | 92.7 | 100.0 | 85 | 300~1000 | 418 | ok |
| yolo26-x-obb_1024x1024.dxnn | 1 | 3 | 8.7 ±0.3 | 8.7 | 31 | 93.0 | 100.0 | 84~85 | 300~1000 | 519 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-obb_1024x1024.dxnn | 2 | 33.8 | 2 | 35.8 |
| yolo26-s-obb_1024x1024.dxnn | 1 | 44.1 | 1 | 44.1 |

---
*Report generated by dx-benchmark tool*
