# YOLO26 Benchmark Report

**Generated:** 2026-07-29 10:29:15 (Local)

## Test Timing

| # | Type | Start | End | Duration |
|---|------|-------|-----|----------|
| 1 | run | 2026-07-22 15:04:37 | 2026-07-23 13:12:03 | 22h 7m 26s |

## Executive Summary

### Object Detection

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n_640x640.dxnn | ON | 23.41 | 103.8 | 67.7 | 2 |
| yolo26-n_640x640.dxnn | OFF | 21.13 | 179.5 | 80.1 | 2 |
| yolo26-s_640x640.dxnn | ON | 29.35 | 104.5 | 67.4 | 2 |
| yolo26-s_640x640.dxnn | OFF | 27.04 | 179.1 | 80.1 | 2 |
| yolo26-m_640x640.dxnn | ON | 36.60 | 105.1 | 67.2 | 2 |
| yolo26-m_640x640.dxnn | OFF | 33.26 | 118.7 | 79.5 | 2 |
| yolo26-l_640x640.dxnn | ON | 43.88 | 90.4 | 66.5 | 2 |
| yolo26-l_640x640.dxnn | OFF | 41.32 | 86.8 | 80.3 | 2 |
| yolo26-x_640x640.dxnn | ON | 69.19 | 48.1 | 48.1 | 1 |
| yolo26-x_640x640.dxnn | OFF | 66.79 | 49.2 | 48.8 | 1 |

### Pose Estimation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-pose_640x640.dxnn | ON | 19.93 | 151.9 | 82.3 | 2 |
| yolo26-n-pose_640x640.dxnn | OFF | 17.82 | 264.5 | 112.2 | 3 |
| yolo26-s-pose_640x640.dxnn | ON | 25.98 | 149.0 | 82.1 | 2 |
| yolo26-s-pose_640x640.dxnn | OFF | 24.04 | 176.0 | 112.8 | 3 |
| yolo26-m-pose_640x640.dxnn | ON | 32.47 | 115.1 | 81.8 | 2 |
| yolo26-m-pose_640x640.dxnn | OFF | 31.47 | 112.6 | 108.7 | 3 |
| yolo26-l-pose_640x640.dxnn | ON | 39.80 | 82.4 | 80.9 | 2 |
| yolo26-l-pose_640x640.dxnn | OFF | 39.10 | 84.5 | 84.2 | 2 |
| yolo26-x-pose_640x640.dxnn | ON | 66.50 | 47.9 | 47.6 | 1 |
| yolo26-x-pose_640x640.dxnn | OFF | 64.51 | 48.0 | 47.6 | 1 |

### Segmentation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-seg_640x640.dxnn | ON | 37.49 | 67.4 | 44.7 | 1 |
| yolo26-n-seg_640x640.dxnn | OFF | 35.45 | 95.7 | 55.1 | 1 |
| yolo26-s-seg_640x640.dxnn | ON | 45.53 | 67.2 | 44.7 | 1 |
| yolo26-s-seg_640x640.dxnn | OFF | 43.58 | 95.7 | 55.2 | 1 |
| yolo26-m-seg_640x640.dxnn | ON | 60.09 | 67.3 | 44.6 | 1 |
| yolo26-m-seg_640x640.dxnn | OFF | 56.78 | 80.0 | 54.8 | 1 |
| yolo26-l-seg_640x640.dxnn | ON | 67.72 | 64.9 | 44.2 | 1 |
| yolo26-l-seg_640x640.dxnn | OFF | 65.01 | 64.3 | 53.1 | 1 |
| yolo26-x-seg_640x640.dxnn | ON | 105.59 | 34.6 | 33.5 | 1 |
| yolo26-x-seg_640x640.dxnn | OFF | 102.35 | 34.6 | 34.4 | 1 |

### Oriented BBox (OBB)

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-obb_1024x1024.dxnn | ON | 35.24 | 103.5 | 69.2 | 2 |
| yolo26-n-obb_1024x1024.dxnn | OFF | 33.71 | 102.9 | 81.8 | 2 |
| yolo26-s-obb_1024x1024.dxnn | ON | 50.64 | 60.1 | 62.4 | 2 |
| yolo26-s-obb_1024x1024.dxnn | OFF | 48.76 | 62.7 | 61.7 | 2 |
| yolo26-m-obb_1024x1024.dxnn | ON | 68.34 | 42.2 | 41.6 | 1 |
| yolo26-m-obb_1024x1024.dxnn | OFF | 66.41 | 42.2 | 41.6 | 1 |
| yolo26-l-obb_1024x1024.dxnn | ON | 86.81 | 30.1 | 30.7 | 1 |
| yolo26-l-obb_1024x1024.dxnn | OFF | 84.96 | 30.4 | 30.8 | 1 |
| yolo26-x-obb_1024x1024.dxnn | ON | 155.03 | 17.2 | 17.1 | — |
| yolo26-x-obb_1024x1024.dxnn | OFF | 153.57 | 17.0 | 17.1 | — |

### Classification

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n_224x224.dxnn | ON | 1.40 | 3627.9 | 189.1 | — |
| yolo26-n_224x224.dxnn | OFF | 1.40 | 3632.1 | 188.9 | — |
| yolo26-s_224x224.dxnn | ON | 2.03 | 2028.9 | 189.0 | — |
| yolo26-s_224x224.dxnn | OFF | 2.04 | 2030.3 | 189.4 | — |
| yolo26-m_224x224.dxnn | ON | 2.65 | 1399.9 | 188.6 | — |
| yolo26-m_224x224.dxnn | OFF | 2.57 | 1401.1 | 189.1 | — |
| yolo26-l_224x224.dxnn | ON | 3.89 | 886.0 | 188.9 | — |
| yolo26-l_224x224.dxnn | OFF | 3.87 | 882.0 | 188.7 | — |
| yolo26-x_224x224.dxnn | ON | 6.39 | 488.9 | 187.8 | — |
| yolo26-x_224x224.dxnn | OFF | 6.31 | 488.2 | 187.9 | — |

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
| DX-AllSuite | v2.4.0 |
| Benchmark Tool | 0.1.0 |
| NPU RT | v3.4.0 |
| NPU RT (commit) | v3.4.0+5474c9f |
| NPU Driver (RT) | v2.5.1 |
| NPU Driver (PCIe) | v2.4.1 |
| NPU Firmware | v2.7.3 |
| NPU Memory | LPDDR5 5600 Mbps, 3.92GiB |
| NPU Board | M.2, Rev 1.0 |
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
| yolo26-n_640x640.dxnn | 103.8 ±1.1 | 5 | 186 | 23.9 | 73.6 | 38~39 | 1000 | ok |
| yolo26-s_640x640.dxnn | 104.5 ±1.8 | 5 | 183 | 43.4 | 74.7 | 44 | 1000 | ok |
| yolo26-m_640x640.dxnn | 105.1 ±0.4 | 6 | 189 | 76.9 | 88.2 | 55~57 | 1000 | ok |
| yolo26-l_640x640.dxnn | 90.4 ±0.3 | 6 | 134 | 90.4 | 100.0 | 56~60 | 1000 | ok |
| yolo26-x_640x640.dxnn | 48.1 ±0.7 | 4 | 66 | 88.0 | 100.0 | 60~64 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n_640x640.dxnn | 5 | [3]:89.2 · [4]:102.7 · **[5]:105.2 ★** · [6]:104.1 · [7]:102.9 · [8]:104.8 |
| yolo26-s_640x640.dxnn | 5 | [3]:81.1 · [4]:98.2 · **[5]:105.7 ★** · [6]:103.1 · [7]:103.9 · [8]:102.4 |
| yolo26-m_640x640.dxnn | 6 | [3]:67.9 · [4]:84.9 · [5]:98.0 · **[6]:106.0 ★** · [7]:105.6 · [8]:104.0 |
| yolo26-l_640x640.dxnn | 6 | [3]:58.1 · [4]:73.7 · [5]:87.7 · **[6]:89.7 ★** · [7]:87.9 · [8]:88.4 |
| yolo26-x_640x640.dxnn | 4 | [3]:36.7 · **[4]:48.6 ★** · [5]:46.1 · [6]:47.1 · [7]:47.0 · [8]:48.1 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n_640x640.dxnn | 179.5 ±0.3 | 7 | 125 | 43.7 | 73.1 | 42~43 | 1000 | ok |
| yolo26-s_640x640.dxnn | 179.1 ±0.2 | 9 | 99 | 84.2 | 97.3 | 51~53 | 1000 | ok |
| yolo26-m_640x640.dxnn | 118.7 ±1.6 | 6 | 78 | 91.5 | 100.0 | 57~61 | 1000 | ok |
| yolo26-l_640x640.dxnn | 86.8 ±1.1 | 7 | 57 | 91.6 | 100.0 | 57~61 | 1000 | ok |
| yolo26-x_640x640.dxnn | 49.2 ±0.0 | 4 | 30 | 88.6 | 100.0 | 60~64 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n_640x640.dxnn | 7 | [3]:117.5 · [4]:143.3 · [5]:175.2 · [6]:178.8 · **[7]:179.1 ★** · [8]:178.9 |
| yolo26-s_640x640.dxnn | 9 | [3]:91.8 · [4]:123.0 · [5]:151.2 · [6]:174.0 · [7]:178.5 · [8]:178.8 · **[9]:179.1 ★** · [10]:179.1 |
| yolo26-m_640x640.dxnn | 6 | [3]:75.7 · [4]:100.7 · [5]:119.8 · **[6]:121.0 ★** · [7]:118.6 · [8]:120.9 |
| yolo26-l_640x640.dxnn | 7 | [3]:60.4 · [4]:82.7 · [5]:85.3 · [6]:86.9 · **[7]:87.0 ★** · [8]:85.9 |
| yolo26-x_640x640.dxnn | 4 | [3]:39.8 · **[4]:49.2 ★** · [5]:46.9 · [6]:48.1 · [7]:48.9 · [8]:48.7 |


#### Pose Estimation

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 151.9 ±0.7 | 10 | 191 | 39.6 | 71.9 | 47~48 | 1000 | ok |
| yolo26-s-pose_640x640.dxnn | 149.0 ±2.8 | 8 | 183 | 72.9 | 85.7 | 52~53 | 1000 | ok |
| yolo26-m-pose_640x640.dxnn | 115.1 ±0.3 | 5 | 94 | 89.3 | 100.0 | 58~62 | 1000 | ok |
| yolo26-l-pose_640x640.dxnn | 82.4 ±1.3 | 5 | 74 | 89.4 | 100.0 | 57~60 | 1000 | ok |
| yolo26-x-pose_640x640.dxnn | 47.9 ±0.0 | 4 | 40 | 90.9 | 100.0 | 59~63 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-pose_640x640.dxnn | 10 | [3]:116.2 · [4]:137.6 · [5]:148.9 · [6]:151.1 · [7]:149.5 · [8]:151.2 · [9]:151.4 · **[10]:151.8 ★** |
| yolo26-s-pose_640x640.dxnn | 8 | [3]:93.4 · [4]:120.9 · [5]:139.8 · [6]:146.3 · [7]:150.6 · **[8]:151.7 ★** · [9]:151.5 · [10]:150.1 |
| yolo26-m-pose_640x640.dxnn | 5 | [3]:71.5 · [4]:96.8 · **[5]:114.8 ★** · [6]:112.0 · [7]:110.2 · [8]:113.4 |
| yolo26-l-pose_640x640.dxnn | 5 | [3]:60.0 · [4]:79.9 · **[5]:83.5 ★** · [6]:81.9 · [7]:81.8 · [8]:81.7 |
| yolo26-x-pose_640x640.dxnn | 4 | [3]:39.5 · **[4]:47.5 ★** · [5]:47.3 · [6]:45.9 · [7]:45.6 · [8]:47.3 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 264.5 ±0.2 | 9 | 95 | 81.3 | 90.4 | 50~52 | 1000 | ok |
| yolo26-s-pose_640x640.dxnn | 176.0 ±0.4 | 6 | 71 | 91.6 | 100.0 | 53~56 | 1000 | ok |
| yolo26-m-pose_640x640.dxnn | 112.6 ±0.8 | 6 | 48 | 91.1 | 100.0 | 58~62 | 1000 | ok |
| yolo26-l-pose_640x640.dxnn | 84.5 ±1.8 | 6 | 37 | 90.3 | 100.0 | 57~61 | 1000 | ok |
| yolo26-x-pose_640x640.dxnn | 48.0 ±0.1 | 4 | 20 | 89.7 | 100.0 | 59~63 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-pose_640x640.dxnn | 9 | [3]:130.2 · [4]:170.0 · [5]:207.8 · [6]:248.2 · [7]:262.1 · [8]:263.6 · **[9]:264.2 ★** · [10]:262.7 |
| yolo26-s-pose_640x640.dxnn | 6 | [3]:105.5 · [4]:137.9 · [5]:171.2 · **[6]:178.2 ★** · [7]:173.6 · [8]:174.1 |
| yolo26-m-pose_640x640.dxnn | 6 | [3]:79.1 · [4]:110.7 · [5]:111.8 · **[6]:112.6 ★** · [7]:110.4 · [8]:112.2 |
| yolo26-l-pose_640x640.dxnn | 6 | [3]:67.2 · [4]:86.8 · [5]:84.7 · **[6]:87.7 ★** · [7]:84.5 · [8]:82.7 |
| yolo26-x-pose_640x640.dxnn | 4 | [3]:41.5 · **[4]:47.9 ★** · [5]:47.7 · [6]:45.8 · [7]:45.7 · [8]:46.8 |


#### Segmentation

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 67.4 ±0.4 | 7 | 223 | 18.9 | 61.7 | 45 | 1000 | ok |
| yolo26-s-seg_640x640.dxnn | 67.2 ±0.2 | 6 | 226 | 36.9 | 71.8 | 47~48 | 1000 | ok |
| yolo26-m-seg_640x640.dxnn | 67.3 ±0.5 | 10 | 227 | 73.9 | 91.7 | 59~62 | 1000 | ok |
| yolo26-l-seg_640x640.dxnn | 64.9 ±0.2 | 7 | 189 | 90.4 | 100.0 | 59~63 | 1000 | ok |
| yolo26-x-seg_640x640.dxnn | 34.6 ±0.3 | 8 | 82 | 89.0 | 100.0 | 63~68 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-seg_640x640.dxnn | 7 | [3]:55.6 · [4]:65.3 · [5]:66.2 · [6]:67.5 · **[7]:67.5 ★** · [8]:66.8 |
| yolo26-s-seg_640x640.dxnn | 6 | [3]:53.4 · [4]:62.1 · [5]:66.6 · **[6]:67.8 ★** · [7]:67.3 · [8]:67.5 |
| yolo26-m-seg_640x640.dxnn | 10 | [3]:41.7 · [4]:54.0 · [5]:58.9 · [6]:66.6 · [7]:66.9 · [8]:67.0 · [9]:67.4 · **[10]:67.8 ★** |
| yolo26-l-seg_640x640.dxnn | 7 | [3]:37.5 · [4]:48.6 · [5]:55.9 · [6]:63.4 · **[7]:64.9 ★** · [8]:64.4 |
| yolo26-x-seg_640x640.dxnn | 8 | [3]:24.6 · [4]:32.7 · [5]:34.2 · [6]:33.8 · [7]:33.3 · **[8]:34.5 ★** · [9]:34.1 · [10]:33.9 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 95.7 ±0.1 | 8 | 119 | 27.2 | 78.8 | 45~46 | 1000 | ok |
| yolo26-s-seg_640x640.dxnn | 95.7 ±0.1 | 9 | 129 | 53.9 | 87.3 | 51~53 | 1000 | ok |
| yolo26-m-seg_640x640.dxnn | 80.0 ±0.6 | 8 | 107 | 89.8 | 100.0 | 62~67 | 1000 | ok |
| yolo26-l-seg_640x640.dxnn | 64.3 ±0.4 | 7 | 80 | 90.5 | 100.0 | 60~64 | 1000 | ok |
| yolo26-x-seg_640x640.dxnn | 34.6 ±0.0 | 8 | 52 | 89.3 | 100.0 | 63~68 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-seg_640x640.dxnn | 8 | [3]:75.7 · [4]:86.3 · [5]:95.5 · [6]:95.4 · [7]:95.5 · **[8]:95.6 ★** · [9]:95.3 · [10]:95.5 |
| yolo26-s-seg_640x640.dxnn | 9 | [3]:60.9 · [4]:75.7 · [5]:93.1 · [6]:95.4 · [7]:94.9 · [8]:95.4 · **[9]:95.5 ★** · [10]:95.4 |
| yolo26-m-seg_640x640.dxnn | 8 | [3]:47.9 · [4]:62.2 · [5]:70.5 · [6]:77.5 · [7]:79.8 · **[8]:80.3 ★** · [9]:80.1 · [10]:78.0 |
| yolo26-l-seg_640x640.dxnn | 7 | [3]:43.2 · [4]:56.6 · [5]:64.5 · [6]:64.3 · **[7]:64.7 ★** · [8]:64.5 |
| yolo26-x-seg_640x640.dxnn | 8 | [3]:26.3 · [4]:34.3 · [5]:34.2 · [6]:33.4 · [7]:33.5 · **[8]:34.9 ★** · [9]:34.1 |


#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 103.5 ±0.1 | 6 | 108 | 92.5 | 100.0 | 51~53 | 1000 | ok |
| yolo26-s-obb_1024x1024.dxnn | 60.1 ±0.6 | 5 | 61 | 89.1 | 100.0 | 53~55 | 1000 | ok |
| yolo26-m-obb_1024x1024.dxnn | 42.2 ±0.1 | 4 | 41 | 90.6 | 100.0 | 58~62 | 1000 | ok |
| yolo26-l-obb_1024x1024.dxnn | 30.1 ±0.5 | 5 | 32 | 89.2 | 100.0 | 57~60 | 1000 | ok |
| yolo26-x-obb_1024x1024.dxnn | 17.2 ±0.1 | 4 | 18 | 88.1 | 100.0 | 58~62 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-obb_1024x1024.dxnn | 6 | [3]:66.7 · [4]:83.9 · [5]:98.7 · **[6]:103.4 ★** · [7]:97.8 · [8]:96.8 |
| yolo26-s-obb_1024x1024.dxnn | 5 | [3]:46.8 · [4]:61.2 · **[5]:63.7 ★** · [6]:59.8 · [7]:59.8 · [8]:59.7 |
| yolo26-m-obb_1024x1024.dxnn | 4 | [3]:35.2 · **[4]:42.1 ★** · [5]:40.4 · [6]:39.7 · [7]:40.9 · [8]:39.6 |
| yolo26-l-obb_1024x1024.dxnn | 5 | [3]:26.8 · [4]:30.9 · **[5]:30.9 ★** · [6]:29.5 · [7]:29.4 · [8]:30.5 |
| yolo26-x-obb_1024x1024.dxnn | 4 | [3]:15.5 · **[4]:17.0 ★** · [5]:16.4 · [6]:16.5 · [7]:16.5 · [8]:16.5 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 102.9 ±0.2 | 5 | 51 | 90.1 | 100.0 | 51~53 | 1000 | ok |
| yolo26-s-obb_1024x1024.dxnn | 62.7 ±1.7 | 4 | 32 | 89.1 | 100.0 | 52~55 | 1000 | ok |
| yolo26-m-obb_1024x1024.dxnn | 42.2 ±0.1 | 4 | 22 | 90.4 | 100.0 | 58~61 | 1000 | ok |
| yolo26-l-obb_1024x1024.dxnn | 30.4 ±0.3 | 5 | 17 | 89.2 | 100.0 | 57~60 | 1000 | ok |
| yolo26-x-obb_1024x1024.dxnn | 17.0 ±0.1 | 4 | 9 | 87.5 | 100.0 | 58~62 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-obb_1024x1024.dxnn | 5 | [3]:67.6 · [4]:86.6 · **[5]:103.3 ★** · [6]:99.3 · [7]:97.9 · [8]:97.9 |
| yolo26-s-obb_1024x1024.dxnn | 4 | [3]:49.3 · **[4]:64.1 ★** · [5]:58.5 · [6]:60.3 · [7]:59.9 · [8]:60.1 |
| yolo26-m-obb_1024x1024.dxnn | 4 | [3]:34.2 · **[4]:42.2 ★** · [5]:39.6 · [6]:39.4 · [7]:39.5 · [8]:39.5 |
| yolo26-l-obb_1024x1024.dxnn | 5 | [3]:26.2 · [4]:30.8 · **[5]:31.0 ★** · [6]:29.4 · [7]:29.4 · [8]:29.4 |
| yolo26-x-obb_1024x1024.dxnn | 4 | [3]:15.8 · **[4]:17.2 ★** · [5]:16.5 · [6]:16.4 · [7]:16.4 · [8]:16.5 |


#### Classification

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n_224x224.dxnn | 3627.9 ±6.8 | 10 | 66 | 88.5 | 96.5 | 47~48 | 1000 | ok |
| yolo26-s_224x224.dxnn | 2028.9 ±3.9 | 5 | 36 | 90.5 | 97.7 | 47~49 | 1000 | ok |
| yolo26-m_224x224.dxnn | 1399.9 ±3.0 | 4 | 27 | 87.4 | 97.8 | 51~54 | 1000 | ok |
| yolo26-l_224x224.dxnn | 886.0 ±1.7 | 4 | 18 | 88.7 | 98.2 | 50~52 | 1000 | ok |
| yolo26-x_224x224.dxnn | 488.9 ±0.1 | 4 | 10 | 90.7 | 99.0 | 53~55 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n_224x224.dxnn | 10 | [3]:2070.7 · [4]:2814.5 · [5]:3365.6 · [6]:3520.9 · [7]:3597.4 · [8]:3610.4 · [9]:3631.5 · **[10]:3634.7 ★** |
| yolo26-s_224x224.dxnn | 5 | [3]:1441.2 · [4]:1892.6 · **[5]:2035.6 ★** · [6]:1980.3 · [7]:2019.7 · [8]:2018.7 |
| yolo26-m_224x224.dxnn | 4 | [3]:1078.6 · **[4]:1409.6 ★** · [5]:1381.5 · [6]:1375.4 · [7]:1384.2 · [8]:1383.7 |
| yolo26-l_224x224.dxnn | 4 | [3]:737.4 · **[4]:889.0 ★** · [5]:873.7 · [6]:877.5 · [7]:877.6 · [8]:867.7 |
| yolo26-x_224x224.dxnn | 4 | [3]:443.5 · **[4]:488.9 ★** · [5]:485.0 · [6]:481.2 · [7]:485.5 · [8]:484.5 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n_224x224.dxnn | 3632.1 ±0.7 | 10 | 66 | 90.3 | 96.3 | 46~47 | 1000 | ok |
| yolo26-s_224x224.dxnn | 2030.3 ±3.2 | 5 | 36 | 88.8 | 97.7 | 47~49 | 1000 | ok |
| yolo26-m_224x224.dxnn | 1401.1 ±4.3 | 4 | 27 | 89.3 | 97.3 | 51~54 | 1000 | ok |
| yolo26-l_224x224.dxnn | 882.0 ±1.5 | 4 | 17 | 90.5 | 98.4 | 50~52 | 1000 | ok |
| yolo26-x_224x224.dxnn | 488.2 ±0.4 | 4 | 10 | 89.7 | 98.9 | 53~56 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n_224x224.dxnn | 10 | [3]:2081.4 · [4]:2839.2 · [5]:3371.8 · [6]:3509.5 · [7]:3597.3 · [8]:3613.6 · [9]:3634.8 · **[10]:3637.8 ★** |
| yolo26-s_224x224.dxnn | 5 | [3]:1435.1 · [4]:1892.6 · **[5]:2033.7 ★** · [6]:2021.4 · [7]:2020.0 · [8]:2022.7 |
| yolo26-m_224x224.dxnn | 4 | [3]:1075.0 · **[4]:1406.0 ★** · [5]:1384.4 · [6]:1379.6 · [7]:1383.0 · [8]:1372.0 |
| yolo26-l_224x224.dxnn | 4 | [3]:738.4 · **[4]:888.3 ★** · [5]:874.6 · [6]:877.5 · [7]:878.0 · [8]:877.6 |
| yolo26-x_224x224.dxnn | 4 | [3]:439.0 · **[4]:488.9 ★** · [5]:484.9 · [6]:482.6 · [7]:485.2 · [8]:485.1 |


### Latency (Single-Core, Sync)

#### Object Detection

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_640x640.dxnn | 42.7 ±1.1 | 23.41 | 20.86 | 2.56 | 35 | ok |
| yolo26-s_640x640.dxnn | 34.1 ±1.8 | 29.35 | 26.82 | 2.53 | 40 | ok |
| yolo26-m_640x640.dxnn | 27.3 ±0.4 | 36.60 | 34.04 | 2.56 | 45 | ok |
| yolo26-l_640x640.dxnn | 22.8 ±0.3 | 43.88 | 41.34 | 2.53 | 45 | ok |
| yolo26-x_640x640.dxnn | 14.5 ±0.7 | 69.19 | 66.66 | 2.53 | 46 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_640x640.dxnn | 47.3 ±0.3 | 21.13 | 21.13 | N/A | 39 | ok |
| yolo26-s_640x640.dxnn | 37.0 ±0.2 | 27.04 | 27.04 | N/A | 44 | ok |
| yolo26-m_640x640.dxnn | 30.1 ±1.6 | 33.26 | 33.26 | N/A | 45 | ok |
| yolo26-l_640x640.dxnn | 24.2 ±1.1 | 41.32 | 41.32 | N/A | 46 | ok |
| yolo26-x_640x640.dxnn | 15.0 ±0.0 | 66.79 | 66.79 | N/A | 46 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-pose_640x640.dxnn | 50.2 ±0.7 | 19.93 | 18.50 | 1.43 | 45 | ok |
| yolo26-s-pose_640x640.dxnn | 38.5 ±2.8 | 25.98 | 24.45 | 1.53 | 45 | ok |
| yolo26-m-pose_640x640.dxnn | 30.8 ±0.2 | 32.47 | 30.98 | 1.49 | 45 | ok |
| yolo26-l-pose_640x640.dxnn | 25.1 ±1.3 | 39.80 | 38.34 | 1.46 | 45 | ok |
| yolo26-x-pose_640x640.dxnn | 15.0 ±0.0 | 66.50 | 64.95 | 1.55 | 46 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-pose_640x640.dxnn | 56.1 ±0.2 | 17.82 | 17.82 | N/A | 44 | ok |
| yolo26-s-pose_640x640.dxnn | 41.6 ±0.4 | 24.04 | 24.04 | N/A | 45 | ok |
| yolo26-m-pose_640x640.dxnn | 31.8 ±0.8 | 31.47 | 31.47 | N/A | 45 | ok |
| yolo26-l-pose_640x640.dxnn | 25.6 ±1.8 | 39.10 | 39.10 | N/A | 45 | ok |
| yolo26-x-pose_640x640.dxnn | 15.5 ±0.1 | 64.51 | 64.51 | N/A | 46 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-seg_640x640.dxnn | 26.7 ±0.5 | 37.49 | 34.54 | 2.95 | 44 | ok |
| yolo26-s-seg_640x640.dxnn | 22.0 ±0.2 | 45.53 | 42.68 | 2.85 | 44 | ok |
| yolo26-m-seg_640x640.dxnn | 16.6 ±0.5 | 60.09 | 57.04 | 3.06 | 45 | ok |
| yolo26-l-seg_640x640.dxnn | 14.8 ±0.2 | 67.72 | 64.64 | 3.08 | 45 | ok |
| yolo26-x-seg_640x640.dxnn | 9.5 ±0.3 | 105.59 | 102.51 | 3.08 | 46 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-seg_640x640.dxnn | 28.2 ±0.1 | 35.45 | 35.45 | N/A | 42 | ok |
| yolo26-s-seg_640x640.dxnn | 22.9 ±0.1 | 43.58 | 43.58 | N/A | 44 | ok |
| yolo26-m-seg_640x640.dxnn | 17.6 ±0.6 | 56.78 | 56.78 | N/A | 45 | ok |
| yolo26-l-seg_640x640.dxnn | 15.4 ±0.4 | 65.01 | 65.01 | N/A | 46 | ok |
| yolo26-x-seg_640x640.dxnn | 9.8 ±0.0 | 102.35 | 102.35 | N/A | 46 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-obb_1024x1024.dxnn | 28.4 ±0.1 | 35.24 | 33.48 | 1.77 | 45 | ok |
| yolo26-s-obb_1024x1024.dxnn | 19.7 ±0.6 | 50.64 | 48.89 | 1.74 | 45 | ok |
| yolo26-m-obb_1024x1024.dxnn | 14.6 ±0.1 | 68.34 | 66.62 | 1.71 | 46 | ok |
| yolo26-l-obb_1024x1024.dxnn | 11.5 ±0.5 | 86.81 | 85.08 | 1.73 | 46 | ok |
| yolo26-x-obb_1024x1024.dxnn | 6.5 ±0.1 | 155.03 | 153.25 | 1.78 | 47 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-obb_1024x1024.dxnn | 29.7 ±0.2 | 33.71 | 33.71 | N/A | 44 | ok |
| yolo26-s-obb_1024x1024.dxnn | 20.5 ±1.7 | 48.76 | 48.76 | N/A | 45 | ok |
| yolo26-m-obb_1024x1024.dxnn | 15.1 ±0.1 | 66.41 | 66.41 | N/A | 46 | ok |
| yolo26-l-obb_1024x1024.dxnn | 11.8 ±0.3 | 84.96 | 84.96 | N/A | 46 | ok |
| yolo26-x-obb_1024x1024.dxnn | 6.5 ±0.1 | 153.57 | 153.57 | N/A | 47 | ok |

#### Classification

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_224x224.dxnn | 711.9 ±6.8 | 1.40 | 1.40 | N/A | 44 | ok |
| yolo26-s_224x224.dxnn | 491.6 ±3.9 | 2.03 | 2.03 | N/A | 42 | ok |
| yolo26-m_224x224.dxnn | 377.5 ±3.0 | 2.65 | 2.65 | N/A | 41 | ok |
| yolo26-l_224x224.dxnn | 257.2 ±1.7 | 3.89 | 3.89 | N/A | 43 | ok |
| yolo26-x_224x224.dxnn | 156.4 ±0.1 | 6.39 | 6.39 | N/A | 44 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_224x224.dxnn | 714.2 ±0.7 | 1.40 | 1.40 | N/A | 42 | ok |
| yolo26-s_224x224.dxnn | 490.3 ±3.1 | 2.04 | 2.04 | N/A | 42 | ok |
| yolo26-m_224x224.dxnn | 388.8 ±4.3 | 2.57 | 2.57 | N/A | 41 | ok |
| yolo26-l_224x224.dxnn | 258.4 ±1.5 | 3.87 | 3.87 | N/A | 43 | ok |
| yolo26-x_224x224.dxnn | 158.4 ±0.4 | 6.31 | 6.31 | N/A | 44 | ok |

## E2E Pipeline (Single-Stream)

### Object Detection

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | avdec_h264 | 3455 | 3 | 67.7 ±0.3 | 51.06 | 316 | 16.6 | 37.5 | 38~39 | 1000 | 320 | ok |
| yolo26-s_640x640.dxnn | avdec_h264 | 3455 | 3 | 67.4 ±0.1 | 51.23 | 312 | 29.5 | 59.9 | 44 | 1000 | 342 | ok |
| yolo26-m_640x640.dxnn | avdec_h264 | 3455 | 3 | 67.2 ±0.1 | 51.41 | 301 | 47.8 | 76.5 | 50~52 | 1000 | 374 | ok |
| yolo26-l_640x640.dxnn | avdec_h264 | 3455 | 3 | 66.5 ±0.0 | 51.99 | 282 | 66.0 | 86.3 | 52~56 | 1000 | 388 | ok |
| yolo26-x_640x640.dxnn | avdec_h264 | 3455 | 3 | 48.1 ±0.1 | 71.85 | 144 | 93.5 | 100.0 | 61~68 | 1000 | 481 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | avdec_h264 | 3455 | 3 | 80.1 ±0.8 | 43.15 | 304 | 18.3 | 57.3 | 42~43 | 1000 | 352 | ok |
| yolo26-s_640x640.dxnn | avdec_h264 | 3455 | 3 | 80.1 ±0.6 | 43.16 | 303 | 33.6 | 73.1 | 46 | 1000 | 372 | ok |
| yolo26-m_640x640.dxnn | avdec_h264 | 3455 | 3 | 79.5 ±0.2 | 43.48 | 304 | 54.7 | 83.3 | 51~53 | 1000 | 402 | ok |
| yolo26-l_640x640.dxnn | avdec_h264 | 3455 | 3 | 80.3 ±0.5 | 43.01 | 300 | 79.7 | 92.8 | 53~58 | 1000 | 417 | ok |
| yolo26-x_640x640.dxnn | avdec_h264 | 3455 | 3 | 48.8 ±0.3 | 70.85 | 153 | 94.0 | 100.0 | 61~69 | 1000 | 491 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n_640x640.dxnn | 67.7 | 80.1 | -12.4 | -15.5% |
| yolo26-s_640x640.dxnn | 67.4 | 80.1 | -12.6 | -15.8% |
| yolo26-m_640x640.dxnn | 67.2 | 79.5 | -12.2 | -15.4% |
| yolo26-l_640x640.dxnn | 66.5 | 80.3 | -13.9 | -17.3% |
| yolo26-x_640x640.dxnn | 48.1 | 48.8 | -0.7 | -1.4% |

### Pose Estimation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 82.3 ±0.3 | 41.97 | 323 | 21.5 | 49.4 | 45 | 1000 | 310 | ok |
| yolo26-s-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 82.1 ±0.2 | 42.10 | 318 | 38.5 | 68.0 | 47 | 1000 | 335 | ok |
| yolo26-m-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 81.8 ±0.1 | 42.25 | 302 | 62.6 | 84.5 | 51~55 | 1000 | 367 | ok |
| yolo26-l-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 80.9 ±0.1 | 42.71 | 262 | 85.5 | 99.1 | 53~58 | 1000 | 381 | ok |
| yolo26-x-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 47.6 ±0.1 | 72.57 | 113 | 94.2 | 100.0 | 60~69 | 1000 | 474 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 112.2 ±0.3 | 30.79 | 302 | 28.7 | 59.2 | 46 | 1000 | 292 | ok |
| yolo26-s-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 112.8 ±0.8 | 30.64 | 301 | 51.8 | 75.2 | 47~49 | 1000 | 324 | ok |
| yolo26-m-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 108.7 ±1.1 | 31.78 | 265 | 83.0 | 98.5 | 53~57 | 1000 | 358 | ok |
| yolo26-l-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 84.2 ±1.1 | 41.06 | 175 | 90.9 | 100.0 | 54~59 | 1000 | 370 | ok |
| yolo26-x-pose_640x640.dxnn | avdec_h264 | 3455 | 3 | 47.6 ±0.1 | 72.62 | 94 | 94.0 | 100.0 | 61~69 | 1000 | 463 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-pose_640x640.dxnn | 82.3 | 112.2 | -29.9 | -26.6% |
| yolo26-s-pose_640x640.dxnn | 82.1 | 112.8 | -30.7 | -27.2% |
| yolo26-m-pose_640x640.dxnn | 81.8 | 108.7 | -26.9 | -24.8% |
| yolo26-l-pose_640x640.dxnn | 80.9 | 84.2 | -3.2 | -3.9% |
| yolo26-x-pose_640x640.dxnn | 47.6 | 47.6 | +0.0 | +0.1% |

### Segmentation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 44.7 ±0.1 | 77.27 | 313 | 14.4 | 32.7 | 43~44 | 1000 | 418 | ok |
| yolo26-s-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 44.7 ±0.0 | 77.26 | 307 | 26.3 | 55.3 | 46~47 | 1000 | 443 | ok |
| yolo26-m-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 44.6 ±0.3 | 77.45 | 285 | 48.7 | 78.9 | 54~58 | 1000 | 474 | ok |
| yolo26-l-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 44.2 ±0.4 | 78.19 | 269 | 61.2 | 83.3 | 56~61 | 1000 | 490 | ok |
| yolo26-x-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 33.5 ±1.4 | 103.06 | 152 | 93.6 | 100.0 | 71~78 | 800~1000 | 595 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 55.1 ±0.4 | 62.72 | 338 | 16.5 | 48.0 | 44~45 | 1000 | 460 | ok |
| yolo26-s-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 55.2 ±0.4 | 62.56 | 332 | 31.1 | 71.4 | 47~48 | 1000 | 485 | ok |
| yolo26-m-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 54.8 ±0.8 | 63.00 | 320 | 60.5 | 85.2 | 55~61 | 1000 | 531 | ok |
| yolo26-l-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 53.1 ±0.7 | 65.07 | 293 | 73.3 | 92.8 | 56~63 | 1000 | 536 | ok |
| yolo26-x-seg_640x640.dxnn | avdec_h264 | 3455 | 3 | 34.4 ±0.6 | 100.56 | 152 | 93.2 | 100.0 | 67~77 | 800~1000 | 613 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-seg_640x640.dxnn | 44.7 | 55.1 | -10.4 | -18.8% |
| yolo26-s-seg_640x640.dxnn | 44.7 | 55.2 | -10.5 | -19.0% |
| yolo26-m-seg_640x640.dxnn | 44.6 | 54.8 | -10.2 | -18.7% |
| yolo26-l-seg_640x640.dxnn | 44.2 | 53.1 | -8.9 | -16.8% |
| yolo26-x-seg_640x640.dxnn | 33.5 | 34.4 | -0.8 | -2.4% |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 69.2 ±0.2 | 38.15 | 313 | 52.8 | 79.5 | 47~48 | 1000 | 344 | ok |
| yolo26-s-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 62.4 ±0.2 | 42.30 | 229 | 90.3 | 100.0 | 51~54 | 1000 | 371 | ok |
| yolo26-m-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 41.6 ±0.1 | 63.44 | 131 | 93.2 | 100.0 | 60~67 | 1000 | 404 | ok |
| yolo26-l-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 30.7 ±0.1 | 86.07 | 95 | 92.9 | 100.0 | 60~66 | 1000 | 424 | ok |
| yolo26-x-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 17.1 ±0.1 | 154.68 | 56 | 94.0 | 100.0 | 68~75 | 1000 | 525 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 81.8 ±0.1 | 32.25 | 310 | 62.1 | 85.3 | 47~49 | 1000 | 338 | ok |
| yolo26-s-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 61.7 ±0.6 | 42.76 | 200 | 90.0 | 100.0 | 50~53 | 1000 | 365 | ok |
| yolo26-m-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 41.6 ±0.2 | 63.49 | 129 | 93.5 | 100.0 | 58~64 | 1000 | 403 | ok |
| yolo26-l-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 30.8 ±0.1 | 85.66 | 97 | 93.1 | 100.0 | 60~68 | 1000 | 417 | ok |
| yolo26-x-obb_1024x1024.dxnn | avdec_h264 | 2640 | 3 | 17.1 ±0.0 | 154.16 | 56 | 94.4 | 100.0 | 68~75 | 1000 | 518 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-obb_1024x1024.dxnn | 69.2 | 81.8 | -12.6 | -15.5% |
| yolo26-s-obb_1024x1024.dxnn | 62.4 | 61.7 | +0.7 | +1.1% |
| yolo26-m-obb_1024x1024.dxnn | 41.6 | 41.6 | +0.0 | +0.1% |
| yolo26-l-obb_1024x1024.dxnn | 30.7 | 30.8 | -0.1 | -0.5% |
| yolo26-x-obb_1024x1024.dxnn | 17.1 | 17.1 | -0.1 | -0.3% |

### Classification

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_224x224.dxnn | avdec_h264 | 3455 | 3 | 189.1 ±0.2 | 18.27 | 270 | 4.1 | 12.8 | 42~43 | 1000 | 217 | ok |
| yolo26-s_224x224.dxnn | avdec_h264 | 3455 | 3 | 189.0 ±0.7 | 18.28 | 270 | 7.5 | 22.1 | 42~43 | 1000 | 213 | ok |
| yolo26-m_224x224.dxnn | avdec_h264 | 3455 | 3 | 188.6 ±0.4 | 18.32 | 269 | 10.8 | 30.2 | 41~42 | 1000 | 231 | ok |
| yolo26-l_224x224.dxnn | avdec_h264 | 3455 | 3 | 188.9 ±0.1 | 18.29 | 269 | 17.2 | 44.2 | 44 | 1000 | 238 | ok |
| yolo26-x_224x224.dxnn | avdec_h264 | 3455 | 3 | 187.8 ±0.7 | 18.40 | 267 | 31.4 | 61.1 | 45 | 1000 | 296 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_224x224.dxnn | avdec_h264 | 3455 | 3 | 188.9 ±0.8 | 18.29 | 270 | 4.1 | 13.0 | 42~43 | 1000 | 202 | ok |
| yolo26-s_224x224.dxnn | avdec_h264 | 3455 | 3 | 189.4 ±0.4 | 18.24 | 270 | 7.4 | 22.5 | 41 | 1000 | 228 | ok |
| yolo26-m_224x224.dxnn | avdec_h264 | 3455 | 3 | 189.1 ±0.3 | 18.27 | 269 | 10.7 | 30.2 | 43~44 | 1000 | 243 | ok |
| yolo26-l_224x224.dxnn | avdec_h264 | 3455 | 3 | 188.7 ±0.7 | 18.31 | 268 | 17.4 | 42.6 | 44 | 1000 | 239 | ok |
| yolo26-x_224x224.dxnn | avdec_h264 | 3455 | 3 | 187.9 ±0.3 | 18.39 | 267 | 31.6 | 60.0 | 45 | 1000 | 296 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n_224x224.dxnn | 189.1 | 188.9 | +0.2 | +0.1% |
| yolo26-s_224x224.dxnn | 189.0 | 189.4 | -0.4 | -0.2% |
| yolo26-m_224x224.dxnn | 188.6 | 189.1 | -0.5 | -0.3% |
| yolo26-l_224x224.dxnn | 188.9 | 188.7 | +0.3 | +0.2% |
| yolo26-x_224x224.dxnn | 187.8 | 187.9 | -0.1 | -0.0% |

## E2E Pipeline (Multi-Stream)

### Object Detection

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | 2 | 3 | 67.3 ±0.2 | 33.7 | 315 | 16.8 | 41.8 | 39 | 1000 | 455 | ok |
| yolo26-n_640x640.dxnn | 3 | 3 | 67.6 ±0.2 | 22.5 | 313 | 17.1 | 42.0 | 39~40 | 1000 | 556 | ok |
| yolo26-s_640x640.dxnn | 2 | 3 | 67.4 ±0.2 | 33.7 | 311 | 30.3 | 60.6 | 44~45 | 1000 | 479 | ok |
| yolo26-s_640x640.dxnn | 3 | 3 | 67.3 ±0.2 | 22.4 | 311 | 30.6 | 60.0 | 45 | 1000 | 577 | ok |
| yolo26-m_640x640.dxnn | 2 | 3 | 66.8 ±0.1 | 33.4 | 304 | 48.7 | 77.0 | 55~56 | 1000 | 504 | ok |
| yolo26-m_640x640.dxnn | 3 | 3 | 66.8 ±0.3 | 22.3 | 301 | 49.2 | 76.5 | 58 | 1000 | 611 | ok |
| yolo26-l_640x640.dxnn | 2 | 3 | 66.4 ±0.4 | 33.2 | 284 | 67.5 | 86.5 | 60~63 | 1000 | 523 | ok |
| yolo26-l_640x640.dxnn | 3 | 3 | 65.5 ±0.6 | 21.8 | 285 | 66.9 | 86.6 | 64~66 | 1000 | 625 | ok |
| yolo26-x_640x640.dxnn | 1 | 3 | 48.1 ±0.1 | 48.1 | 144 | 93.5 | 100.0 | 61~68 | 1000 | 481 | ok |
| yolo26-x_640x640.dxnn | 2 | 3 | 46.8 ±1.0 | 23.4 | 145 | 95.6 | 100.0 | 77~79 | 800~1000 | 618 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | 2 | 3 | 80.1 ±0.4 | 40.1 | 306 | 18.8 | 57.3 | 40~41 | 1000 | 483 | ok |
| yolo26-n_640x640.dxnn | 3 | 3 | 80.2 ±0.5 | 26.7 | 306 | 19.2 | 57.3 | 40 | 1000 | 582 | ok |
| yolo26-s_640x640.dxnn | 2 | 3 | 80.2 ±0.6 | 40.1 | 306 | 34.7 | 72.0 | 46 | 1000 | 503 | ok |
| yolo26-s_640x640.dxnn | 3 | 3 | 80.2 ±0.5 | 26.8 | 306 | 34.9 | 72.0 | 47 | 1000 | 602 | ok |
| yolo26-m_640x640.dxnn | 2 | 3 | 79.4 ±0.2 | 39.7 | 307 | 56.7 | 85.0 | 56~58 | 1000 | 535 | ok |
| yolo26-m_640x640.dxnn | 3 | 3 | 79.6 ±0.5 | 26.5 | 305 | 57.2 | 85.3 | 60~61 | 1000 | 636 | ok |
| yolo26-l_640x640.dxnn | 2 | 3 | 79.5 ±0.5 | 39.8 | 308 | 81.6 | 95.5 | 65~68 | 1000 | 549 | ok |
| yolo26-l_640x640.dxnn | 3 | 3 | 79.5 ±0.5 | 26.5 | 308 | 81.8 | 94.6 | 70~71 | 1000 | 650 | ok |
| yolo26-x_640x640.dxnn | 1 | 3 | 48.8 ±0.3 | 48.8 | 153 | 94.0 | 100.0 | 61~69 | 1000 | 491 | ok |
| yolo26-x_640x640.dxnn | 2 | 3 | 47.0 ±1.3 | 23.5 | 157 | 96.0 | 100.0 | 77~79 | 800~1000 | 626 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n_640x640.dxnn | 2 | 33.7 | 2 | 40.1 |
| yolo26-s_640x640.dxnn | 2 | 33.7 | 2 | 40.1 |
| yolo26-m_640x640.dxnn | 2 | 33.4 | 2 | 39.7 |
| yolo26-l_640x640.dxnn | 2 | 33.2 | 2 | 39.8 |
| yolo26-x_640x640.dxnn | 1 | 48.1 | 1 | 48.8 |

### Pose Estimation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 2 | 3 | 80.2 ±0.4 | 40.1 | 322 | 21.7 | 48.7 | 45 | 1000 | 449 | ok |
| yolo26-n-pose_640x640.dxnn | 3 | 3 | 80.5 ±0.7 | 26.8 | 321 | 22.1 | 48.6 | 44~45 | 1000 | 552 | ok |
| yolo26-s-pose_640x640.dxnn | 2 | 3 | 79.8 ±0.9 | 39.9 | 318 | 38.7 | 70.0 | 49~50 | 1000 | 470 | ok |
| yolo26-s-pose_640x640.dxnn | 3 | 3 | 80.3 ±0.8 | 26.8 | 319 | 39.2 | 67.5 | 50 | 1000 | 576 | ok |
| yolo26-m-pose_640x640.dxnn | 2 | 3 | 79.4 ±0.6 | 39.7 | 307 | 62.8 | 83.9 | 60~63 | 1000 | 501 | ok |
| yolo26-m-pose_640x640.dxnn | 3 | 3 | 79.3 ±1.1 | 26.4 | 307 | 63.3 | 85.9 | 64~65 | 1000 | 604 | ok |
| yolo26-l-pose_640x640.dxnn | 2 | 3 | 80.2 ±1.4 | 40.1 | 270 | 87.1 | 97.8 | 66~69 | 1000 | 514 | ok |
| yolo26-l-pose_640x640.dxnn | 3 | 3 | 80.0 ±1.1 | 26.7 | 271 | 88.2 | 99.0 | 72~73 | 1000 | 618 | ok |
| yolo26-x-pose_640x640.dxnn | 1 | 3 | 47.6 ±0.1 | 47.6 | 113 | 94.2 | 100.0 | 60~69 | 1000 | 474 | ok |
| yolo26-x-pose_640x640.dxnn | 2 | 3 | 46.5 ±1.0 | 23.3 | 115 | 95.9 | 100.0 | 76~78 | 800~1000 | 610 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 3 | 3 | 113.0 ±1.8 | 37.6 | 330 | 32.4 | 54.9 | 46 | 1000 | 546 | ok |
| yolo26-n-pose_640x640.dxnn | 4 | 3 | 111.2 ±0.4 | 27.8 | 332 | 32.0 | 53.1 | 47 | 1000 | 649 | ok |
| yolo26-s-pose_640x640.dxnn | 3 | 3 | 111.0 ±0.1 | 37.0 | 323 | 56.1 | 77.9 | 52~53 | 1000 | 569 | ok |
| yolo26-s-pose_640x640.dxnn | 4 | 3 | 111.2 ±0.5 | 27.8 | 324 | 56.7 | 78.9 | 54 | 1000 | 668 | ok |
| yolo26-m-pose_640x640.dxnn | 3 | 3 | 106.5 ±0.9 | 35.5 | 282 | 87.9 | 98.4 | 67~71 | 1000 | 592 | ok |
| yolo26-m-pose_640x640.dxnn | 4 | 3 | 106.3 ±0.1 | 26.6 | 281 | 89.0 | 99.6 | 73~74 | 1000 | 696 | ok |
| yolo26-l-pose_640x640.dxnn | 2 | 3 | 83.8 ±0.3 | 41.9 | 189 | 93.5 | 100.0 | 67~70 | 1000 | 502 | ok |
| yolo26-l-pose_640x640.dxnn | 3 | 3 | 84.1 ±0.5 | 28.0 | 187 | 95.8 | 100.0 | 74~75 | 1000 | 608 | ok |
| yolo26-x-pose_640x640.dxnn | 1 | 3 | 47.6 ±0.1 | 47.6 | 94 | 94.0 | 100.0 | 61~69 | 1000 | 463 | ok |
| yolo26-x-pose_640x640.dxnn | 2 | 3 | 46.0 ±1.3 | 23.0 | 96 | 95.3 | 100.0 | 77~78 | 800~1000 | 600 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-pose_640x640.dxnn | 2 | 40.1 | 3 | 37.6 |
| yolo26-s-pose_640x640.dxnn | 2 | 39.9 | 3 | 37.0 |
| yolo26-m-pose_640x640.dxnn | 2 | 39.7 | 3 | 35.5 |
| yolo26-l-pose_640x640.dxnn | 2 | 40.1 | 2 | 41.9 |
| yolo26-x-pose_640x640.dxnn | 1 | 47.6 | 1 | 47.6 |

### Segmentation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 1 | 3 | 44.7 ±0.1 | 44.7 | 313 | 14.4 | 32.7 | 43~44 | 1000 | 418 | ok |
| yolo26-n-seg_640x640.dxnn | 2 | 3 | 44.6 ±0.3 | 22.3 | 315 | 14.3 | 33.5 | 43 | 1000 | 563 | ok |
| yolo26-s-seg_640x640.dxnn | 1 | 3 | 44.7 ±0.0 | 44.7 | 307 | 26.3 | 55.3 | 46~47 | 1000 | 443 | ok |
| yolo26-s-seg_640x640.dxnn | 2 | 3 | 43.1 ±0.1 | 21.6 | 309 | 25.4 | 56.5 | 47~48 | 1000 | 586 | ok |
| yolo26-m-seg_640x640.dxnn | 1 | 3 | 44.6 ±0.3 | 44.6 | 285 | 48.7 | 78.9 | 54~58 | 1000 | 474 | ok |
| yolo26-m-seg_640x640.dxnn | 2 | 3 | 43.4 ±0.3 | 21.7 | 292 | 48.0 | 76.5 | 62~63 | 1000 | 621 | ok |
| yolo26-l-seg_640x640.dxnn | 1 | 3 | 44.2 ±0.4 | 44.2 | 269 | 61.2 | 83.3 | 56~61 | 1000 | 490 | ok |
| yolo26-l-seg_640x640.dxnn | 2 | 3 | 42.8 ±0.5 | 21.4 | 277 | 59.8 | 82.9 | 65~67 | 1000 | 634 | ok |
| yolo26-x-seg_640x640.dxnn | 1 | 3 | 33.5 ±1.4 | 33.5 | 152 | 93.6 | 100.0 | 71~78 | 800~1000 | 595 | ok |
| yolo26-x-seg_640x640.dxnn | 2 | 3 | 29.5 ±0.1 | 14.7 | 140 | 91.2 | 100.0 | 80 | 800~1000 | 738 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 1 | 3 | 55.1 ±0.4 | 55.1 | 338 | 16.5 | 48.0 | 44~45 | 1000 | 460 | ok |
| yolo26-n-seg_640x640.dxnn | 2 | 3 | 55.0 ±0.9 | 27.5 | 334 | 16.6 | 54.4 | 44 | 1000 | 603 | ok |
| yolo26-s-seg_640x640.dxnn | 1 | 3 | 55.2 ±0.4 | 55.2 | 332 | 31.1 | 71.4 | 47~48 | 1000 | 485 | ok |
| yolo26-s-seg_640x640.dxnn | 2 | 3 | 54.9 ±0.4 | 27.4 | 336 | 31.4 | 69.5 | 48~49 | 1000 | 626 | ok |
| yolo26-m-seg_640x640.dxnn | 1 | 3 | 54.8 ±0.8 | 54.8 | 320 | 60.5 | 85.2 | 55~61 | 1000 | 531 | ok |
| yolo26-m-seg_640x640.dxnn | 2 | 3 | 54.0 ±0.5 | 27.0 | 324 | 60.9 | 83.7 | 66~67 | 1000 | 666 | ok |
| yolo26-l-seg_640x640.dxnn | 1 | 3 | 53.1 ±0.7 | 53.1 | 293 | 73.3 | 92.8 | 56~63 | 1000 | 536 | ok |
| yolo26-l-seg_640x640.dxnn | 2 | 3 | 52.2 ±0.3 | 26.1 | 300 | 74.3 | 91.8 | 70~71 | 1000 | 675 | ok |
| yolo26-x-seg_640x640.dxnn | 1 | 3 | 34.4 ±0.6 | 34.4 | 152 | 93.2 | 100.0 | 67~77 | 800~1000 | 613 | ok |
| yolo26-x-seg_640x640.dxnn | 2 | 3 | 29.4 ±0.1 | 14.7 | 137 | 91.8 | 100.0 | 80 | 800~1000 | 761 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-seg_640x640.dxnn | 1 | 44.7 | 1 | 55.1 |
| yolo26-s-seg_640x640.dxnn | 1 | 44.7 | 1 | 55.2 |
| yolo26-m-seg_640x640.dxnn | 1 | 44.6 | 1 | 54.8 |
| yolo26-l-seg_640x640.dxnn | 1 | 44.2 | 1 | 53.1 |
| yolo26-x-seg_640x640.dxnn | 1 | 33.5 | 1 | 34.4 |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 2 | 3 | 69.1 ±0.6 | 34.6 | 320 | 54.8 | 79.6 | 50~52 | 1000 | 482 | ok |
| yolo26-n-obb_1024x1024.dxnn | 3 | 3 | 68.6 ±0.5 | 22.9 | 320 | 55.4 | 79.6 | 53 | 1000 | 588 | ok |
| yolo26-s-obb_1024x1024.dxnn | 2 | 3 | 62.3 ±0.2 | 31.2 | 235 | 93.1 | 100.0 | 59~61 | 1000 | 506 | ok |
| yolo26-s-obb_1024x1024.dxnn | 3 | 3 | 62.3 ±0.1 | 20.8 | 236 | 94.5 | 100.0 | 63~64 | 1000 | 612 | ok |
| yolo26-m-obb_1024x1024.dxnn | 1 | 3 | 41.6 ±0.1 | 41.6 | 131 | 93.2 | 100.0 | 60~67 | 1000 | 404 | ok |
| yolo26-m-obb_1024x1024.dxnn | 2 | 3 | 41.9 ±0.3 | 20.9 | 137 | 95.9 | 100.0 | 73~75 | 1000 | 534 | ok |
| yolo26-l-obb_1024x1024.dxnn | 1 | 3 | 30.7 ±0.1 | 30.7 | 95 | 92.9 | 100.0 | 60~66 | 1000 | 424 | ok |
| yolo26-l-obb_1024x1024.dxnn | 2 | 3 | 30.7 ±0.3 | 15.3 | 98 | 94.9 | 100.0 | 73~75 | 1000 | 556 | ok |
| yolo26-x-obb_1024x1024.dxnn | 1 | 3 | 17.1 ±0.1 | 17.1 | 56 | 94.0 | 100.0 | 68~75 | 1000 | 525 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 2 | 3 | 82.2 ±0.2 | 41.1 | 327 | 69.8 | 88.4 | 52~53 | 1000 | 502 | ok |
| yolo26-n-obb_1024x1024.dxnn | 3 | 3 | 82.2 ±0.3 | 27.4 | 330 | 70.1 | 88.3 | 54~55 | 1000 | 601 | ok |
| yolo26-s-obb_1024x1024.dxnn | 2 | 3 | 61.6 ±0.4 | 30.8 | 211 | 94.5 | 100.0 | 57~60 | 1000 | 506 | ok |
| yolo26-s-obb_1024x1024.dxnn | 3 | 3 | 61.4 ±0.2 | 20.5 | 211 | 94.9 | 100.0 | 61~63 | 1000 | 603 | ok |
| yolo26-m-obb_1024x1024.dxnn | 1 | 3 | 41.6 ±0.2 | 41.6 | 129 | 93.5 | 100.0 | 58~64 | 1000 | 403 | ok |
| yolo26-m-obb_1024x1024.dxnn | 2 | 3 | 41.9 ±0.1 | 20.9 | 134 | 96.5 | 100.0 | 71~74 | 1000 | 531 | ok |
| yolo26-l-obb_1024x1024.dxnn | 1 | 3 | 30.8 ±0.1 | 30.8 | 97 | 93.1 | 100.0 | 60~68 | 1000 | 417 | ok |
| yolo26-l-obb_1024x1024.dxnn | 2 | 3 | 30.8 ±0.1 | 15.4 | 99 | 95.6 | 100.0 | 74~75 | 1000 | 548 | ok |
| yolo26-x-obb_1024x1024.dxnn | 1 | 3 | 17.1 ±0.0 | 17.1 | 56 | 94.4 | 100.0 | 68~75 | 1000 | 518 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-obb_1024x1024.dxnn | 2 | 34.6 | 2 | 41.1 |
| yolo26-s-obb_1024x1024.dxnn | 2 | 31.2 | 2 | 30.8 |
| yolo26-m-obb_1024x1024.dxnn | 1 | 41.6 | 1 | 41.6 |
| yolo26-l-obb_1024x1024.dxnn | 1 | 30.7 | 1 | 30.8 |

---
*Report generated by dx-benchmark tool*
