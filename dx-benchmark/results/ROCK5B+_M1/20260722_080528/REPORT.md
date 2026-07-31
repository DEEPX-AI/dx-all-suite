# YOLO26 Benchmark Report

**Generated:** 2026-07-29 10:29:15 (Local)

## Test Timing

| # | Type | Outcome | Start | End | Duration |
|---|------|--------|-------|-----|----------|
| 1 | run | interrupted | 2026-07-22 08:05:28 | 2026-07-22 08:05:28 | N/A |
| 2 | retry-failed | completed | 2026-07-22 11:36:39 | 2026-07-23 14:23:03 | 26h 46m 24s |

## Executive Summary

### Object Detection

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n_640x640.dxnn | ON | 34.57 | 157.6 | 141.5 | 4 |
| yolo26-n_640x640.dxnn | OFF | 34.29 | 319.3 | 95.1 | 3 |
| yolo26-s_640x640.dxnn | ON | 39.87 | 155.3 | 130.4 | 4 |
| yolo26-s_640x640.dxnn | OFF | 35.72 | 188.0 | 95.5 | 3 |
| yolo26-m_640x640.dxnn | ON | 51.90 | 106.0 | 108.1 | 1 |
| yolo26-m_640x640.dxnn | OFF | 50.14 | 107.5 | 94.7 | 2 |
| yolo26-l_640x640.dxnn | ON | 66.52 | 80.3 | 85.5 | 1 |
| yolo26-l_640x640.dxnn | OFF | 59.30 | 84.9 | 85.6 | 1 |
| yolo26-x_640x640.dxnn | ON | 95.73 | 43.6 | 36.5 | 1 |
| yolo26-x_640x640.dxnn | OFF | 88.51 | 42.7 | 35.6 | 1 |

### Pose Estimation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-pose_640x640.dxnn | ON | 25.39 | 242.7 | 193.3 | 6 |
| yolo26-n-pose_640x640.dxnn | OFF | 25.77 | 287.4 | 237.9 | 8 |
| yolo26-s-pose_640x640.dxnn | ON | 35.66 | 180.8 | 162.8 | 5 |
| yolo26-s-pose_640x640.dxnn | OFF | 32.11 | 175.9 | 177.1 | 5 |
| yolo26-m-pose_640x640.dxnn | ON | 44.85 | 103.8 | 109.6 | 2 |
| yolo26-m-pose_640x640.dxnn | OFF | 41.11 | 102.4 | 110.3 | 2 |
| yolo26-l-pose_640x640.dxnn | ON | 53.71 | 81.4 | 82.3 | 1 |
| yolo26-l-pose_640x640.dxnn | OFF | 49.09 | 83.6 | 82.4 | 1 |
| yolo26-x-pose_640x640.dxnn | ON | 84.90 | 40.8 | 34.7 | 1 |
| yolo26-x-pose_640x640.dxnn | OFF | 82.24 | 41.0 | 35.2 | 1 |

### Segmentation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-seg_640x640.dxnn | ON | 32.83 | 104.8 | 86.8 | 2 |
| yolo26-n-seg_640x640.dxnn | OFF | 30.51 | 166.6 | 77.9 | 2 |
| yolo26-s-seg_640x640.dxnn | ON | 44.68 | 103.1 | 78.5 | 2 |
| yolo26-s-seg_640x640.dxnn | OFF | 44.98 | 139.0 | 75.5 | 2 |
| yolo26-m-seg_640x640.dxnn | ON | 61.20 | 61.6 | 60.2 | 1 |
| yolo26-m-seg_640x640.dxnn | OFF | 55.72 | 65.0 | 62.5 | 1 |
| yolo26-l-seg_640x640.dxnn | ON | 86.00 | 52.9 | 49.6 | 1 |
| yolo26-l-seg_640x640.dxnn | OFF | 64.61 | 54.0 | 48.6 | 1 |
| yolo26-x-seg_640x640.dxnn | ON | 120.96 | 26.7 | 19.3 | — |
| yolo26-x-seg_640x640.dxnn | OFF | 105.36 | 26.0 | 18.3 | — |

### Oriented BBox (OBB)

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-obb_1024x1024.dxnn | ON | 42.70 | 100.9 | 101.8 | 3 |
| yolo26-n-obb_1024x1024.dxnn | OFF | 43.59 | 98.2 | 99.9 | 3 |
| yolo26-s-obb_1024x1024.dxnn | ON | 64.80 | 62.8 | 62.4 | 1 |
| yolo26-s-obb_1024x1024.dxnn | OFF | 62.87 | 60.1 | 61.0 | 1 |
| yolo26-m-obb_1024x1024.dxnn | ON | 86.25 | 38.8 | 35.8 | 1 |
| yolo26-m-obb_1024x1024.dxnn | OFF | 83.42 | 40.1 | 37.0 | 1 |
| yolo26-l-obb_1024x1024.dxnn | ON | 105.50 | 29.5 | 25.2 | — |
| yolo26-l-obb_1024x1024.dxnn | OFF | 96.08 | 29.9 | 25.3 | — |
| yolo26-x-obb_1024x1024.dxnn | ON | 182.09 | 14.6 | 10.5 | — |
| yolo26-x-obb_1024x1024.dxnn | OFF | 173.19 | 14.7 | 10.4 | — |

### Classification

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n_224x224.dxnn | ON | 2.24 | 3633.5 | 957.9 | — |
| yolo26-n_224x224.dxnn | OFF | 1.52 | 3630.8 | 946.0 | — |
| yolo26-s_224x224.dxnn | ON | 4.27 | 2003.4 | 972.4 | — |
| yolo26-s_224x224.dxnn | OFF | 3.89 | 2004.8 | 985.7 | — |
| yolo26-m_224x224.dxnn | ON | 5.52 | 1383.9 | 954.6 | — |
| yolo26-m_224x224.dxnn | OFF | 2.76 | 1386.4 | 967.8 | — |
| yolo26-l_224x224.dxnn | ON | 3.92 | 876.7 | 844.8 | — |
| yolo26-l_224x224.dxnn | OFF | 3.99 | 873.3 | 836.2 | — |
| yolo26-x_224x224.dxnn | ON | 6.52 | 484.2 | 480.1 | — |
| yolo26-x_224x224.dxnn | OFF | 8.27 | 483.4 | 479.8 | — |

## Environment

| Item | Value |
|------|-------|
| Hostname | rock-5b-plus |
| OS | Debian GNU/Linux 12 (bookworm) |
| Kernel | 6.1.43-15-rk2312 |
| CPU | - |
| CPU Cores | 8 |
| RAM | 7.8 GB |
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
| NPU PCIe | Gen3 X2 [01:00:00] |

### Tools

| Tool | Available | Version |
|------|-----------|---------|
| run_model | Yes | DXRT v3.4.0 run_model |
| dxrt-cli | Yes | unknown |
| gst-launch-1.0 | Yes | gst-launch-1.0 version 1.22.9 |
| gst-inspect-1.0 | Yes | gst-inspect-1.0 version 1.22.9 |
| time | Yes | unknown |
| ffprobe | Yes | ffprobe version 5.1.9-0+deb12u1 Copyright (c) 2007-2026 the ... |
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
| yolo26-n_640x640.dxnn | 157.6 ±2.4 | 8 | 184 | 37.8 | 64.0 | 58~60 | 1000 | ok |
| yolo26-s_640x640.dxnn | 155.3 ±0.5 | 7 | 186 | 71.9 | 81.1 | 70~74 | 1000 | ok |
| yolo26-m_640x640.dxnn | 106.0 ±7.6 | 6 | 139 | 88.0 | 100.0 | 80~83 | 600~1000 | ok |
| yolo26-l_640x640.dxnn | 80.3 ±4.8 | 8 | 109 | 88.7 | 100.0 | 80~82 | 600~1000 | ok |
| yolo26-x_640x640.dxnn | 43.6 ±1.3 | 5 | 71 | 87.1 | 100.0 | 80~83 | 800~1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n_640x640.dxnn | 8 | [3]:126.8 · [4]:157.2 · [5]:154.6 · [6]:157.2 · [7]:155.1 · **[8]:157.6 ★** · [9]:155.9 · [10]:155.8 |
| yolo26-s_640x640.dxnn | 7 | [3]:97.4 · [4]:125.0 · [5]:146.3 · [6]:154.7 · **[7]:156.3 ★** · [8]:155.2 |
| yolo26-m_640x640.dxnn | 6 | [3]:75.2 · [4]:96.7 · [5]:117.8 · **[6]:118.7 ★** · [7]:118.5 · [8]:116.0 |
| yolo26-l_640x640.dxnn | 8 | [3]:60.0 · [4]:79.5 · [5]:86.5 · [6]:86.9 · [7]:85.7 · **[8]:87.8 ★** · [9]:84.9 |
| yolo26-x_640x640.dxnn | 5 | [3]:36.7 · [4]:48.4 · **[5]:49.1 ★** · [6]:47.9 · [7]:48.0 · [8]:47.0 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n_640x640.dxnn | 319.3 ±0.1 | 7 | 181 | 88.7 | 98.8 | 68~70 | 1000 | ok |
| yolo26-s_640x640.dxnn | 188.0 ±7.4 | 5 | 105 | 85.2 | 98.9 | 72~74 | 1000 | ok |
| yolo26-m_640x640.dxnn | 107.5 ±5.3 | 8 | 77 | 88.7 | 100.0 | 80~82 | 600~1000 | ok |
| yolo26-l_640x640.dxnn | 84.9 ±1.9 | 4 | 58 | 84.3 | 100.0 | 78~81 | 800~1000 | ok |
| yolo26-x_640x640.dxnn | 42.7 ±1.7 | 4 | 39 | 85.8 | 100.0 | 80~81 | 600~1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n_640x640.dxnn | 7 | [3]:139.8 · [4]:196.1 · [5]:221.7 · [6]:260.3 · **[7]:320.8 ★** · [8]:297.4 |
| yolo26-s_640x640.dxnn | 5 | [3]:109.0 · [4]:140.4 · **[5]:194.8 ★** · [6]:185.4 · [7]:188.4 · [8]:186.0 |
| yolo26-m_640x640.dxnn | 8 | [3]:82.8 · [4]:112.1 · [5]:114.6 · [6]:116.8 · [7]:116.1 · **[8]:117.5 ★** · [9]:115.7 · [10]:114.3 |
| yolo26-l_640x640.dxnn | 4 | [3]:68.3 · **[4]:89.8 ★** · [5]:87.5 · [6]:85.4 · [7]:88.1 · [8]:88.5 |
| yolo26-x_640x640.dxnn | 4 | [3]:39.7 · **[4]:49.0 ★** · [5]:46.6 · [6]:48.3 · [7]:47.3 · [8]:46.9 |


#### Pose Estimation

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 242.7 ±6.3 | 9 | 209 | 72.6 | 85.0 | 68~71 | 1000 | ok |
| yolo26-s-pose_640x640.dxnn | 180.8 ±1.0 | 6 | 150 | 88.7 | 100.0 | 72~75 | 1000 | ok |
| yolo26-m-pose_640x640.dxnn | 103.8 ±3.2 | 8 | 100 | 92.1 | 100.0 | 79~82 | 600~1000 | ok |
| yolo26-l-pose_640x640.dxnn | 81.4 ±2.4 | 6 | 85 | 88.8 | 100.0 | 78~81 | 800~1000 | ok |
| yolo26-x-pose_640x640.dxnn | 40.8 ±2.3 | 4 | 57 | 84.3 | 100.0 | 79~81 | 600~1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-pose_640x640.dxnn | 9 | [3]:143.2 · [4]:177.4 · [5]:224.6 · [6]:238.3 · [7]:246.4 · [8]:247.8 · **[9]:248.2 ★** · [10]:247.5 |
| yolo26-s-pose_640x640.dxnn | 6 | [3]:109.0 · [4]:139.8 · [5]:174.3 · **[6]:178.6 ★** · [7]:174.1 · [8]:173.2 |
| yolo26-m-pose_640x640.dxnn | 8 | [3]:76.3 · [4]:102.3 · [5]:111.4 · [6]:111.7 · [7]:113.3 · **[8]:115.0 ★** · [9]:108.8 |
| yolo26-l-pose_640x640.dxnn | 6 | [3]:64.3 · [4]:83.0 · [5]:85.9 · **[6]:87.7 ★** · [7]:85.1 · [8]:81.7 |
| yolo26-x-pose_640x640.dxnn | 4 | [3]:37.8 · **[4]:47.0 ★** · [5]:46.8 · [6]:46.3 · [7]:45.8 · [8]:45.5 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 287.4 ±1.9 | 7 | 109 | 90.6 | 100.0 | 69~71 | 1000 | ok |
| yolo26-s-pose_640x640.dxnn | 175.9 ±0.5 | 5 | 86 | 88.8 | 100.0 | 71~74 | 1000 | ok |
| yolo26-m-pose_640x640.dxnn | 102.4 ±3.5 | 9 | 72 | 90.0 | 100.0 | 80~82 | 600~1000 | ok |
| yolo26-l-pose_640x640.dxnn | 83.6 ±3.0 | 4 | 48 | 86.6 | 100.0 | 78~80 | 800~1000 | ok |
| yolo26-x-pose_640x640.dxnn | 41.0 ±2.3 | 7 | 48 | 87.3 | 100.0 | 79~81 | 600~1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-pose_640x640.dxnn | 7 | [3]:154.2 · [4]:214.1 · [5]:260.8 · [6]:284.1 · **[7]:287.4 ★** · [8]:283.1 |
| yolo26-s-pose_640x640.dxnn | 5 | [3]:78.4 · [4]:148.9 · **[5]:178.4 ★** · [6]:177.7 · [7]:176.7 · [8]:177.1 |
| yolo26-m-pose_640x640.dxnn | 9 | [3]:86.9 · [4]:111.3 · [5]:112.7 · [6]:109.8 · [7]:111.4 · [8]:113.2 · **[9]:114.0 ★** · [10]:109.9 |
| yolo26-l-pose_640x640.dxnn | 4 | [3]:69.0 · **[4]:87.6 ★** · [5]:84.5 · [6]:83.1 · [7]:81.7 · [8]:82.9 |
| yolo26-x-pose_640x640.dxnn | 7 | [3]:35.6 · [4]:47.5 · [5]:47.5 · [6]:45.9 · **[7]:47.5 ★** · [8]:45.3 |


#### Segmentation

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 104.8 ±1.2 | 8 | 240 | 30.0 | 78.8 | 64~66 | 1000 | ok |
| yolo26-s-seg_640x640.dxnn | 103.1 ±4.6 | 7 | 252 | 58.7 | 88.7 | 70~72 | 1000 | ok |
| yolo26-m-seg_640x640.dxnn | 61.6 ±5.9 | 6 | 133 | 89.2 | 100.0 | 81~82 | 400~1000 | ok |
| yolo26-l-seg_640x640.dxnn | 52.9 ±3.9 | 8 | 106 | 88.8 | 100.0 | 81~83 | 600~1000 | ok |
| yolo26-x-seg_640x640.dxnn | 26.7 ±1.3 | 5 | 65 | 87.3 | 100.0 | 81~82 | 600~1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-seg_640x640.dxnn | 8 | [3]:75.8 · [4]:94.0 · [5]:102.7 · [6]:103.9 · [7]:102.8 · **[8]:104.3 ★** · [9]:102.9 · [10]:104.2 |
| yolo26-s-seg_640x640.dxnn | 7 | [3]:62.4 · [4]:79.7 · [5]:97.0 · [6]:103.5 · **[7]:104.7 ★** · [8]:103.0 |
| yolo26-m-seg_640x640.dxnn | 6 | [3]:47.5 · [4]:59.1 · [5]:70.6 · **[6]:79.3 ★** · [7]:78.2 · [8]:76.8 |
| yolo26-l-seg_640x640.dxnn | 8 | [3]:42.1 · [4]:52.7 · [5]:63.6 · [6]:64.1 · [7]:64.3 · **[8]:64.3 ★** · [9]:62.7 |
| yolo26-x-seg_640x640.dxnn | 5 | [3]:26.6 · [4]:33.0 · **[5]:33.8 ★** · [6]:33.1 · [7]:31.8 · [8]:31.1 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 166.6 ±0.6 | 8 | 206 | 54.1 | 90.2 | 67~69 | 1000 | ok |
| yolo26-s-seg_640x640.dxnn | 139.0 ±2.9 | 7 | 183 | 87.6 | 100.0 | 74~77 | 1000 | ok |
| yolo26-m-seg_640x640.dxnn | 65.0 ±3.5 | 6 | 79 | 88.4 | 100.0 | 81~83 | 600~1000 | ok |
| yolo26-l-seg_640x640.dxnn | 54.0 ±3.4 | 6 | 72 | 87.8 | 100.0 | 81~82 | 600~1000 | ok |
| yolo26-x-seg_640x640.dxnn | 26.0 ±1.1 | 5 | 53 | 87.1 | 100.0 | 80~82 | 400~1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-seg_640x640.dxnn | 8 | [3]:94.2 · [4]:103.0 · [5]:135.5 · [6]:160.1 · [7]:134.8 · **[8]:162.9 ★** · [9]:140.6 |
| yolo26-s-seg_640x640.dxnn | 7 | [3]:74.5 · [4]:92.3 · [5]:109.1 · [6]:128.4 · **[7]:139.9 ★** · [8]:134.9 |
| yolo26-m-seg_640x640.dxnn | 6 | [3]:52.8 · [4]:63.5 · [5]:78.6 · **[6]:79.8 ★** · [7]:78.6 · [8]:76.2 |
| yolo26-l-seg_640x640.dxnn | 6 | [3]:46.0 · [4]:58.7 · [5]:64.1 · **[6]:64.5 ★** · [7]:63.0 · [8]:64.2 |
| yolo26-x-seg_640x640.dxnn | 5 | [3]:27.6 · [4]:34.2 · **[5]:34.7 ★** · [6]:33.4 · [7]:31.0 · [8]:31.2 |


#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 100.9 ±0.9 | 5 | 103 | 87.5 | 100.0 | 68~71 | 1000 | ok |
| yolo26-s-obb_1024x1024.dxnn | 62.8 ±0.3 | 5 | 73 | 89.6 | 100.0 | 72~75 | 1000 | ok |
| yolo26-m-obb_1024x1024.dxnn | 38.8 ±1.7 | 5 | 68 | 87.0 | 100.0 | 79~82 | 600~1000 | ok |
| yolo26-l-obb_1024x1024.dxnn | 29.5 ±0.4 | 5 | 59 | 86.9 | 100.0 | 78~81 | 800~1000 | ok |
| yolo26-x-obb_1024x1024.dxnn | 14.6 ±0.5 | 4 | 41 | 80.2 | 100.0 | 80~82 | 600~1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-obb_1024x1024.dxnn | 5 | [3]:71.8 · [4]:93.8 · **[5]:99.9 ★** · [6]:98.9 · [7]:98.0 · [8]:97.8 |
| yolo26-s-obb_1024x1024.dxnn | 5 | [3]:48.6 · [4]:59.5 · **[5]:63.4 ★** · [6]:59.8 · [7]:59.8 · [8]:61.6 |
| yolo26-m-obb_1024x1024.dxnn | 5 | [3]:34.8 · [4]:41.4 · **[5]:42.1 ★** · [6]:41.3 · [7]:41.1 · [8]:41.1 |
| yolo26-l-obb_1024x1024.dxnn | 5 | [3]:26.1 · [4]:30.6 · **[5]:31.1 ★** · [6]:29.4 · [7]:29.5 · [8]:29.4 |
| yolo26-x-obb_1024x1024.dxnn | 4 | [3]:14.7 · **[4]:16.9 ★** · [5]:16.4 · [6]:16.4 · [7]:16.2 · [8]:16.4 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 98.2 ±0.3 | 7 | 76 | 89.0 | 100.0 | 68~70 | 1000 | ok |
| yolo26-s-obb_1024x1024.dxnn | 60.1 ±0.1 | 7 | 66 | 90.3 | 100.0 | 72~75 | 1000 | ok |
| yolo26-m-obb_1024x1024.dxnn | 40.1 ±0.9 | 5 | 54 | 87.5 | 100.0 | 78~81 | 800~1000 | ok |
| yolo26-l-obb_1024x1024.dxnn | 29.9 ±1.0 | 4 | 39 | 86.7 | 100.0 | 78~81 | 800~1000 | ok |
| yolo26-x-obb_1024x1024.dxnn | 14.7 ±0.8 | 4 | 28 | 81.8 | 100.0 | 80~81 | 600~1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-obb_1024x1024.dxnn | 7 | [3]:77.9 · [4]:99.9 · [5]:100.5 · [6]:98.1 · **[7]:103.3 ★** · [8]:97.7 |
| yolo26-s-obb_1024x1024.dxnn | 7 | [3]:47.6 · [4]:60.1 · [5]:58.6 · [6]:59.5 · **[7]:62.6 ★** · [8]:59.8 |
| yolo26-m-obb_1024x1024.dxnn | 5 | [3]:35.1 · [4]:41.8 · **[5]:42.1 ★** · [6]:39.5 · [7]:39.4 · [8]:41.5 |
| yolo26-l-obb_1024x1024.dxnn | 4 | [3]:26.4 · **[4]:30.8 ★** · [5]:29.6 · [6]:29.4 · [7]:29.4 · [8]:29.4 |
| yolo26-x-obb_1024x1024.dxnn | 4 | [3]:14.8 · **[4]:17.0 ★** · [5]:16.9 · [6]:16.4 · [7]:16.4 · [8]:16.5 |


#### Classification

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n_224x224.dxnn | 3633.5 ±10.9 | 9 | 107 | 88.7 | 96.8 | 64~66 | 1000 | ok |
| yolo26-s_224x224.dxnn | 2003.4 ±8.7 | 5 | 60 | 88.1 | 97.2 | 67~69 | 1000 | ok |
| yolo26-m_224x224.dxnn | 1383.9 ±1.2 | 10 | 50 | 89.0 | 97.9 | 76~79 | 1000 | ok |
| yolo26-l_224x224.dxnn | 876.7 ±0.5 | 10 | 38 | 88.4 | 98.2 | 73~75 | 1000 | ok |
| yolo26-x_224x224.dxnn | 484.2 ±0.3 | 7 | 42 | 89.2 | 99.3 | 74~78 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n_224x224.dxnn | 9 | [3]:2010.5 · [4]:2669.1 · [5]:3317.5 · [6]:3614.3 · [7]:3623.5 · [8]:3640.8 · **[9]:3644.8 ★** · [10]:3642.6 |
| yolo26-s_224x224.dxnn | 5 | [3]:1191.6 · [4]:1857.2 · **[5]:2025.1 ★** · [6]:2011.5 · [7]:2008.4 · [8]:2010.5 |
| yolo26-m_224x224.dxnn | 10 | [3]:835.9 · [4]:1367.2 · [5]:1376.5 · [6]:1382.2 · [7]:1368.3 · [8]:1388.5 · [9]:1385.5 · **[10]:1389.3 ★** |
| yolo26-l_224x224.dxnn | 10 | [3]:513.4 · [4]:800.8 · [5]:870.0 · [6]:877.4 · [7]:876.0 · [8]:877.5 · [9]:877.6 · **[10]:878.9 ★** |
| yolo26-x_224x224.dxnn | 7 | [3]:338.9 · [4]:463.0 · [5]:484.0 · [6]:484.4 · **[7]:485.5 ★** · [8]:484.0 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n_224x224.dxnn | 3630.8 ±6.7 | 9 | 107 | 88.8 | 96.8 | 65~67 | 1000 | ok |
| yolo26-s_224x224.dxnn | 2004.8 ±15.9 | 5 | 60 | 88.3 | 97.3 | 67~69 | 1000 | ok |
| yolo26-m_224x224.dxnn | 1386.4 ±1.1 | 8 | 47 | 88.1 | 97.8 | 75~79 | 1000 | ok |
| yolo26-l_224x224.dxnn | 873.3 ±1.2 | 7 | 36 | 89.3 | 98.3 | 71~74 | 1000 | ok |
| yolo26-x_224x224.dxnn | 483.4 ±0.7 | 6 | 41 | 91.5 | 99.3 | 75~77 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n_224x224.dxnn | 9 | [3]:2050.4 · [4]:2644.3 · [5]:3287.4 · [6]:3621.6 · [7]:3627.9 · [8]:3641.9 · **[9]:3642.4 ★** · [10]:3642.2 |
| yolo26-s_224x224.dxnn | 5 | [3]:1115.5 · [4]:1841.1 · **[5]:2014.5 ★** · [6]:2004.5 · [7]:2007.8 · [8]:2010.1 |
| yolo26-m_224x224.dxnn | 8 | [3]:808.0 · [4]:1339.7 · [5]:1366.9 · [6]:1384.3 · [7]:1370.8 · **[8]:1387.5 ★** · [9]:1382.4 · [10]:1385.4 |
| yolo26-l_224x224.dxnn | 7 | [3]:517.5 · [4]:805.5 · [5]:864.6 · [6]:876.4 · **[7]:877.7 ★** · [8]:877.6 |
| yolo26-x_224x224.dxnn | 6 | [3]:334.9 · [4]:462.2 · [5]:483.1 · **[6]:485.6 ★** · [7]:485.0 · [8]:484.8 |


### Latency (Single-Core, Sync)

#### Object Detection

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_640x640.dxnn | 28.9 ±2.4 | 34.57 | 27.22 | 7.35 | 50 | ok |
| yolo26-s_640x640.dxnn | 25.1 ±0.5 | 39.87 | 33.27 | 6.60 | 58 | ok |
| yolo26-m_640x640.dxnn | 19.3 ±7.6 | 51.90 | 46.01 | 5.88 | 59 | ok |
| yolo26-l_640x640.dxnn | 15.0 ±4.8 | 66.52 | 61.60 | 4.92 | 59 | ok |
| yolo26-x_640x640.dxnn | 10.4 ±1.3 | 95.73 | 89.85 | 5.88 | 60 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_640x640.dxnn | 29.2 ±0.1 | 34.29 | 34.29 | N/A | 57 | ok |
| yolo26-s_640x640.dxnn | 28.0 ±7.4 | 35.72 | 35.72 | N/A | 57 | ok |
| yolo26-m_640x640.dxnn | 19.9 ±5.3 | 50.14 | 50.14 | N/A | 58 | ok |
| yolo26-l_640x640.dxnn | 16.9 ±1.9 | 59.30 | 59.30 | N/A | 58 | ok |
| yolo26-x_640x640.dxnn | 11.3 ±1.7 | 88.51 | 88.51 | N/A | 60 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-pose_640x640.dxnn | 39.4 ±6.3 | 25.39 | 23.40 | 1.99 | 57 | ok |
| yolo26-s-pose_640x640.dxnn | 28.0 ±1.0 | 35.66 | 31.06 | 4.60 | 58 | ok |
| yolo26-m-pose_640x640.dxnn | 22.3 ±3.2 | 44.85 | 41.00 | 3.84 | 58 | ok |
| yolo26-l-pose_640x640.dxnn | 18.6 ±2.4 | 53.71 | 50.77 | 2.94 | 58 | ok |
| yolo26-x-pose_640x640.dxnn | 11.8 ±2.3 | 84.90 | 81.08 | 3.82 | 60 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-pose_640x640.dxnn | 38.8 ±1.9 | 25.77 | 25.77 | N/A | 57 | ok |
| yolo26-s-pose_640x640.dxnn | 31.1 ±0.5 | 32.11 | 32.11 | N/A | 57 | ok |
| yolo26-m-pose_640x640.dxnn | 24.3 ±3.5 | 41.11 | 41.11 | N/A | 59 | ok |
| yolo26-l-pose_640x640.dxnn | 20.4 ±3.0 | 49.09 | 49.09 | N/A | 59 | ok |
| yolo26-x-pose_640x640.dxnn | 12.2 ±2.3 | 82.24 | 82.24 | N/A | 60 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-seg_640x640.dxnn | 30.5 ±1.2 | 32.83 | 29.77 | 3.06 | 57 | ok |
| yolo26-s-seg_640x640.dxnn | 22.4 ±4.6 | 44.68 | 40.72 | 3.95 | 58 | ok |
| yolo26-m-seg_640x640.dxnn | 16.3 ±5.8 | 61.20 | 56.98 | 4.22 | 59 | ok |
| yolo26-l-seg_640x640.dxnn | 11.6 ±4.0 | 86.00 | 74.07 | 11.92 | 59 | ok |
| yolo26-x-seg_640x640.dxnn | 8.3 ±1.3 | 120.96 | 108.76 | 12.20 | 61 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-seg_640x640.dxnn | 32.8 ±0.6 | 30.51 | 30.51 | N/A | 57 | ok |
| yolo26-s-seg_640x640.dxnn | 22.2 ±2.9 | 44.98 | 44.98 | N/A | 57 | ok |
| yolo26-m-seg_640x640.dxnn | 17.9 ±3.5 | 55.72 | 55.72 | N/A | 60 | ok |
| yolo26-l-seg_640x640.dxnn | 15.5 ±3.4 | 64.61 | 64.61 | N/A | 60 | ok |
| yolo26-x-seg_640x640.dxnn | 9.5 ±1.1 | 105.36 | 105.36 | N/A | 62 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-obb_1024x1024.dxnn | 23.4 ±0.9 | 42.70 | 40.11 | 2.59 | 58 | ok |
| yolo26-s-obb_1024x1024.dxnn | 15.4 ±0.3 | 64.80 | 60.95 | 3.84 | 58 | ok |
| yolo26-m-obb_1024x1024.dxnn | 11.6 ±1.7 | 86.25 | 82.20 | 4.05 | 60 | ok |
| yolo26-l-obb_1024x1024.dxnn | 9.5 ±0.4 | 105.50 | 97.98 | 7.52 | 61 | ok |
| yolo26-x-obb_1024x1024.dxnn | 5.5 ±0.5 | 182.09 | 176.73 | 5.36 | 63 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-obb_1024x1024.dxnn | 22.9 ±0.3 | 43.59 | 43.59 | N/A | 58 | ok |
| yolo26-s-obb_1024x1024.dxnn | 15.9 ±0.1 | 62.87 | 62.87 | N/A | 59 | ok |
| yolo26-m-obb_1024x1024.dxnn | 12.0 ±0.9 | 83.42 | 83.42 | N/A | 60 | ok |
| yolo26-l-obb_1024x1024.dxnn | 10.4 ±1.0 | 96.08 | 96.08 | N/A | 61 | ok |
| yolo26-x-obb_1024x1024.dxnn | 5.8 ±0.8 | 173.19 | 173.19 | N/A | 63 | ok |

#### Classification

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_224x224.dxnn | 447.4 ±10.9 | 2.24 | 2.24 | N/A | 56 | ok |
| yolo26-s_224x224.dxnn | 234.1 ±8.7 | 4.27 | 4.27 | N/A | 56 | ok |
| yolo26-m_224x224.dxnn | 181.1 ±1.2 | 5.52 | 5.52 | N/A | 56 | ok |
| yolo26-l_224x224.dxnn | 254.9 ±0.5 | 3.92 | 3.92 | N/A | 56 | ok |
| yolo26-x_224x224.dxnn | 153.3 ±0.3 | 6.52 | 6.52 | N/A | 57 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_224x224.dxnn | 656.1 ±6.7 | 1.52 | 1.52 | N/A | 56 | ok |
| yolo26-s_224x224.dxnn | 256.8 ±15.9 | 3.89 | 3.89 | N/A | 56 | ok |
| yolo26-m_224x224.dxnn | 362.9 ±1.1 | 2.76 | 2.76 | N/A | 56 | ok |
| yolo26-l_224x224.dxnn | 250.5 ±1.2 | 3.99 | 3.99 | N/A | 57 | ok |
| yolo26-x_224x224.dxnn | 120.9 ±0.7 | 8.27 | 8.27 | N/A | 57 | ok |

## E2E Pipeline (Single-Stream)

### Object Detection

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | mppvideodec | 3455 | 3 | 141.5 ±0.9 | 24.42 | 248 | 34.8 | 63.0 | 60~61 | 1000 | 188 | ok |
| yolo26-s_640x640.dxnn | mppvideodec | 3455 | 3 | 130.4 ±2.6 | 26.48 | 218 | 58.4 | 90.8 | 64~67 | 1000 | 210 | ok |
| yolo26-m_640x640.dxnn | mppvideodec | 3455 | 3 | 108.1 ±0.8 | 31.97 | 182 | 78.3 | 96.1 | 74~80 | 1000 | 240 | ok |
| yolo26-l_640x640.dxnn | mppvideodec | 3455 | 3 | 85.5 ±2.4 | 40.40 | 140 | 88.3 | 100.0 | 74~80 | 800~1000 | 254 | ok |
| yolo26-x_640x640.dxnn | mppvideodec | 3455 | 3 | 36.5 ±6.6 | 94.80 | 75 | 92.7 | 100.0 | 81~83 | 400~1000 | 354 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | mppvideodec | 3455 | 3 | 95.1 ±0.1 | 36.32 | 195 | 21.2 | 69.4 | 60~61 | 1000 | 202 | ok |
| yolo26-s_640x640.dxnn | mppvideodec | 3455 | 3 | 95.5 ±0.2 | 36.19 | 198 | 40.0 | 66.8 | 62~65 | 1000 | 224 | ok |
| yolo26-m_640x640.dxnn | mppvideodec | 3455 | 3 | 94.7 ±0.3 | 36.49 | 200 | 69.2 | 79.1 | 70~76 | 1000 | 254 | ok |
| yolo26-l_640x640.dxnn | mppvideodec | 3455 | 3 | 85.6 ±1.8 | 40.36 | 185 | 89.7 | 100.0 | 74~81 | 800~1000 | 264 | ok |
| yolo26-x_640x640.dxnn | mppvideodec | 3455 | 3 | 35.6 ±7.0 | 96.97 | 102 | 92.3 | 100.0 | 81~83 | 400~1000 | 358 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n_640x640.dxnn | 141.5 | 95.1 | +46.4 | +48.8% |
| yolo26-s_640x640.dxnn | 130.4 | 95.5 | +35.0 | +36.6% |
| yolo26-m_640x640.dxnn | 108.1 | 94.7 | +13.4 | +14.2% |
| yolo26-l_640x640.dxnn | 85.5 | 85.6 | -0.1 | -0.1% |
| yolo26-x_640x640.dxnn | 36.5 | 35.6 | +0.8 | +2.3% |

### Pose Estimation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 193.3 ±1.7 | 17.88 | 232 | 49.1 | 79.6 | 62~63 | 1000 | 178 | ok |
| yolo26-s-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 162.8 ±0.7 | 21.23 | 188 | 76.6 | 93.9 | 65~68 | 1000 | 201 | ok |
| yolo26-m-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 109.6 ±1.8 | 31.52 | 128 | 87.6 | 100.0 | 73~79 | 800~1000 | 234 | ok |
| yolo26-l-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 82.3 ±1.6 | 41.96 | 103 | 89.4 | 100.0 | 74~81 | 800~1000 | 248 | ok |
| yolo26-x-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 34.7 ±6.6 | 99.66 | 66 | 92.1 | 100.0 | 81~83 | 400~1000 | 369 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 237.9 ±2.4 | 14.52 | 192 | 63.7 | 89.8 | 62~63 | 1000 | 166 | ok |
| yolo26-s-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 177.1 ±0.5 | 19.51 | 148 | 79.8 | 100.0 | 65~68 | 1000 | 190 | ok |
| yolo26-m-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 110.3 ±1.3 | 31.32 | 102 | 87.2 | 100.0 | 73~78 | 800~1000 | 221 | ok |
| yolo26-l-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 82.4 ±1.5 | 41.91 | 87 | 88.2 | 100.0 | 74~80 | 800~1000 | 237 | ok |
| yolo26-x-pose_640x640.dxnn | mppvideodec | 3455 | 3 | 35.2 ±5.8 | 98.04 | 60 | 93.0 | 100.0 | 80~83 | 400~1000 | 352 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-pose_640x640.dxnn | 193.3 | 237.9 | -44.6 | -18.7% |
| yolo26-s-pose_640x640.dxnn | 162.8 | 177.1 | -14.3 | -8.1% |
| yolo26-m-pose_640x640.dxnn | 109.6 | 110.3 | -0.7 | -0.6% |
| yolo26-l-pose_640x640.dxnn | 82.3 | 82.4 | -0.1 | -0.1% |
| yolo26-x-pose_640x640.dxnn | 34.7 | 35.2 | -0.6 | -1.6% |

### Segmentation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 86.8 ±0.2 | 39.80 | 310 | 29.3 | 51.1 | 61~64 | 1000 | 286 | ok |
| yolo26-s-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 78.5 ±1.1 | 44.02 | 276 | 47.4 | 80.4 | 65~69 | 1000 | 310 | ok |
| yolo26-m-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 60.2 ±5.5 | 57.35 | 205 | 79.6 | 100.0 | 77~81 | 400~1000 | 344 | ok |
| yolo26-l-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 49.6 ±7.6 | 69.69 | 174 | 88.4 | 100.0 | 79~83 | 400~1000 | 358 | ok |
| yolo26-x-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 19.3 ±2.6 | 178.96 | 83 | 89.9 | 100.0 | 81~83 | 400~1000 | 468 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 77.9 ±2.0 | 44.37 | 272 | 22.3 | 74.5 | 61~63 | 1000 | 313 | ok |
| yolo26-s-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 75.5 ±2.1 | 45.77 | 265 | 42.7 | 73.3 | 65~68 | 1000 | 336 | ok |
| yolo26-m-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 62.5 ±8.9 | 55.28 | 210 | 87.3 | 100.0 | 79~82 | 400~1000 | 367 | ok |
| yolo26-l-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 48.6 ±9.9 | 71.09 | 166 | 90.0 | 100.0 | 80~83 | 400~1000 | 380 | ok |
| yolo26-x-seg_640x640.dxnn | mppvideodec | 3455 | 3 | 18.3 ±2.1 | 188.81 | 81 | 92.4 | 100.0 | 82~84 | 400~800 | 478 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-seg_640x640.dxnn | 86.8 | 77.9 | +8.9 | +11.5% |
| yolo26-s-seg_640x640.dxnn | 78.5 | 75.5 | +3.0 | +4.0% |
| yolo26-m-seg_640x640.dxnn | 60.2 | 62.5 | -2.3 | -3.6% |
| yolo26-l-seg_640x640.dxnn | 49.6 | 48.6 | +1.0 | +2.0% |
| yolo26-x-seg_640x640.dxnn | 19.3 | 18.3 | +1.0 | +5.5% |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 101.8 ±0.5 | 25.92 | 154 | 84.2 | 100.0 | 65~68 | 1000 | 215 | ok |
| yolo26-s-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 62.4 ±0.9 | 42.31 | 97 | 91.3 | 100.0 | 69~75 | 1000 | 239 | ok |
| yolo26-m-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 35.8 ±4.6 | 73.76 | 78 | 90.5 | 100.0 | 79~82 | 400~1000 | 272 | ok |
| yolo26-l-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 25.2 ±3.8 | 104.62 | 65 | 91.3 | 100.0 | 80~83 | 400~1000 | 288 | ok |
| yolo26-x-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 10.5 ±0.8 | 250.60 | 39 | 89.2 | 100.0 | 82~83 | 400~1000 | 391 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 99.9 ±0.1 | 26.41 | 152 | 86.8 | 100.0 | 65~68 | 1000 | 221 | ok |
| yolo26-s-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 61.0 ±0.8 | 43.31 | 108 | 89.0 | 100.0 | 69~74 | 1000 | 237 | ok |
| yolo26-m-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 37.0 ±4.5 | 71.41 | 82 | 92.7 | 100.0 | 79~81 | 400~1000 | 271 | ok |
| yolo26-l-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 25.3 ±4.0 | 104.52 | 69 | 92.2 | 100.0 | 80~83 | 400~1000 | 286 | ok |
| yolo26-x-obb_1024x1024.dxnn | mppvideodec | 2640 | 3 | 10.4 ±0.9 | 253.10 | 38 | 91.0 | 100.0 | 83~84 | 400~1000 | 389 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-obb_1024x1024.dxnn | 101.8 | 99.9 | +1.9 | +1.9% |
| yolo26-s-obb_1024x1024.dxnn | 62.4 | 61.0 | +1.4 | +2.4% |
| yolo26-m-obb_1024x1024.dxnn | 35.8 | 37.0 | -1.2 | -3.2% |
| yolo26-l-obb_1024x1024.dxnn | 25.2 | 25.3 | -0.0 | -0.1% |
| yolo26-x-obb_1024x1024.dxnn | 10.5 | 10.4 | +0.1 | +1.0% |

### Classification

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_224x224.dxnn | mppvideodec | 3455 | 3 | 957.9 ±39.0 | 3.61 | 150 | 10.4 | 43.8 | 57 | 1000 | 91 | ok |
| yolo26-s_224x224.dxnn | mppvideodec | 3455 | 3 | 972.4 ±22.6 | 3.55 | 152 | 20.4 | 63.1 | 57~58 | 1000 | 100 | ok |
| yolo26-m_224x224.dxnn | mppvideodec | 3455 | 3 | 954.6 ±34.2 | 3.62 | 152 | 34.3 | 79.0 | 59~60 | 1000 | 114 | ok |
| yolo26-l_224x224.dxnn | mppvideodec | 3455 | 3 | 844.8 ±7.0 | 4.09 | 136 | 56.0 | 97.8 | 60~61 | 1000 | 127 | ok |
| yolo26-x_224x224.dxnn | mppvideodec | 3455 | 3 | 480.1 ±1.1 | 7.20 | 98 | 64.0 | 98.9 | 63~65 | 1000 | 203 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_224x224.dxnn | mppvideodec | 3455 | 3 | 946.0 ±13.4 | 3.65 | 153 | 10.6 | 42.7 | 57 | 1000 | 91 | ok |
| yolo26-s_224x224.dxnn | mppvideodec | 3455 | 3 | 985.7 ±7.7 | 3.50 | 153 | 20.8 | 63.7 | 57~58 | 1000 | 100 | ok |
| yolo26-m_224x224.dxnn | mppvideodec | 3455 | 3 | 967.8 ±20.8 | 3.57 | 151 | 33.8 | 79.4 | 59~60 | 1000 | 114 | ok |
| yolo26-l_224x224.dxnn | mppvideodec | 3455 | 3 | 836.2 ±23.3 | 4.13 | 134 | 55.1 | 97.8 | 60~62 | 1000 | 127 | ok |
| yolo26-x_224x224.dxnn | mppvideodec | 3455 | 3 | 479.8 ±1.1 | 7.20 | 101 | 64.8 | 99.1 | 63~65 | 1000 | 203 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n_224x224.dxnn | 957.9 | 946.0 | +11.9 | +1.3% |
| yolo26-s_224x224.dxnn | 972.4 | 985.7 | -13.3 | -1.3% |
| yolo26-m_224x224.dxnn | 954.6 | 967.8 | -13.2 | -1.4% |
| yolo26-l_224x224.dxnn | 844.8 | 836.2 | +8.7 | +1.0% |
| yolo26-x_224x224.dxnn | 480.1 | 479.8 | +0.3 | +0.1% |

## E2E Pipeline (Multi-Stream)

### Object Detection

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | 4 | 3 | 139.9 ±0.1 | 35.0 | 260 | 38.8 | 62.0 | 65~67 | 1000 | 212 | ok |
| yolo26-n_640x640.dxnn | 5 | 3 | 140.6 ±1.3 | 28.1 | 255 | 39.1 | 62.4 | 70~71 | 1000 | 216 | ok |
| yolo26-s_640x640.dxnn | 4 | 3 | 130.6 ±0.2 | 32.7 | 227 | 62.4 | 78.6 | 76~82 | 1000 | 232 | ok |
| yolo26-s_640x640.dxnn | 5 | 3 | 127.5 ±3.0 | 25.5 | 219 | 68.8 | 91.6 | 85 | 600~1000 | 236 | ok |
| yolo26-m_640x640.dxnn | 3 | 3 | 62.4 ±3.2 | 20.8 | 105 | 96.1 | 100.0 | 85~86 | 300~1000 | 258 | ok |
| yolo26-m_640x640.dxnn | 2 | 3 | 59.9 ±2.0 | 29.9 | 102 | 95.3 | 100.0 | 85~86 | 300~800 | 251 | ok |
| yolo26-m_640x640.dxnn | 1 | 3 | 108.1 ±0.8 | 108.1 | 182 | 78.3 | 96.1 | 74~80 | 1000 | 240 | ok |
| yolo26-l_640x640.dxnn | 2 | 3 | 57.4 ±4.3 | 28.7 | 104 | 93.8 | 100.0 | 83 | 400~1000 | 265 | ok |
| yolo26-l_640x640.dxnn | 1 | 3 | 85.5 ±2.4 | 85.5 | 140 | 88.3 | 100.0 | 74~80 | 800~1000 | 254 | ok |
| yolo26-x_640x640.dxnn | 1 | 3 | 36.5 ±6.6 | 36.5 | 75 | 92.7 | 100.0 | 81~83 | 400~1000 | 354 | ok |
| yolo26-x_640x640.dxnn | 2 | 3 | 26.9 ±0.2 | 13.5 | 71 | 92.5 | 100.0 | 83 | 400~800 | 359 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | 3 | 3 | 94.8 ±0.3 | 31.6 | 197 | 22.2 | 70.1 | 65~67 | 1000 | 224 | ok |
| yolo26-n_640x640.dxnn | 4 | 3 | 95.1 ±0.1 | 23.8 | 202 | 22.4 | 70.1 | 68~69 | 1000 | 233 | ok |
| yolo26-s_640x640.dxnn | 3 | 3 | 95.5 ±0.1 | 31.8 | 205 | 42.3 | 66.8 | 70~73 | 1000 | 245 | ok |
| yolo26-s_640x640.dxnn | 4 | 3 | 95.4 ±0.3 | 23.9 | 205 | 42.4 | 66.7 | 75 | 1000 | 254 | ok |
| yolo26-m_640x640.dxnn | 3 | 3 | 71.2 ±4.4 | 23.7 | 157 | 93.5 | 100.0 | 83~84 | 400~1000 | 273 | ok |
| yolo26-m_640x640.dxnn | 2 | 3 | 67.6 ±0.8 | 33.8 | 150 | 92.8 | 100.0 | 83~84 | 400~1000 | 262 | ok |
| yolo26-l_640x640.dxnn | 2 | 3 | 56.3 ±3.5 | 28.1 | 137 | 93.1 | 100.0 | 83~85 | 400~1000 | 277 | ok |
| yolo26-l_640x640.dxnn | 1 | 3 | 85.6 ±1.8 | 85.6 | 185 | 89.7 | 100.0 | 74~81 | 800~1000 | 264 | ok |
| yolo26-x_640x640.dxnn | 1 | 3 | 35.6 ±7.0 | 35.6 | 102 | 92.3 | 100.0 | 81~83 | 400~1000 | 358 | ok |
| yolo26-x_640x640.dxnn | 2 | 3 | 26.9 ±0.2 | 13.4 | 88 | 92.9 | 100.0 | 83 | 400~800 | 369 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n_640x640.dxnn | 4 | 35.0 | 3 | 31.6 |
| yolo26-s_640x640.dxnn | 4 | 32.7 | 3 | 31.8 |
| yolo26-m_640x640.dxnn | 1 | 108.1 | 2 | 33.8 |
| yolo26-l_640x640.dxnn | 1 | 85.5 | 1 | 85.6 |
| yolo26-x_640x640.dxnn | 1 | 36.5 | 1 | 35.6 |

### Pose Estimation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 6 | 3 | 190.8 ±0.8 | 31.8 | 246 | 58.1 | 80.9 | 71~76 | 1000 | 219 | ok |
| yolo26-n-pose_640x640.dxnn | 7 | 3 | 190.5 ±0.5 | 27.2 | 246 | 58.2 | 78.4 | 79~80 | 1000 | 225 | ok |
| yolo26-s-pose_640x640.dxnn | 5 | 3 | 161.3 ±3.0 | 32.2 | 192 | 86.0 | 99.7 | 79~84 | 800~1000 | 235 | ok |
| yolo26-s-pose_640x640.dxnn | 6 | 3 | 136.9 ±0.7 | 22.8 | 167 | 92.3 | 100.0 | 84~85 | 600~1000 | 241 | ok |
| yolo26-m-pose_640x640.dxnn | 3 | 3 | 69.9 ±5.7 | 23.3 | 94 | 93.6 | 100.0 | 83~84 | 400~1000 | 254 | ok |
| yolo26-m-pose_640x640.dxnn | 2 | 3 | 66.1 ±1.1 | 33.0 | 89 | 93.0 | 100.0 | 83 | 400~1000 | 246 | ok |
| yolo26-l-pose_640x640.dxnn | 2 | 3 | 55.1 ±2.8 | 27.5 | 82 | 93.6 | 100.0 | 83~84 | 400~1000 | 260 | ok |
| yolo26-l-pose_640x640.dxnn | 1 | 3 | 82.3 ±1.6 | 82.3 | 103 | 89.4 | 100.0 | 74~81 | 800~1000 | 248 | ok |
| yolo26-x-pose_640x640.dxnn | 1 | 3 | 34.7 ±6.6 | 34.7 | 66 | 92.1 | 100.0 | 81~83 | 400~1000 | 369 | ok |
| yolo26-x-pose_640x640.dxnn | 2 | 3 | 25.6 ±0.1 | 12.8 | 58 | 92.8 | 100.0 | 83 | 400~1000 | 369 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 7 | 3 | 237.3 ±0.4 | 33.9 | 215 | 73.5 | 89.3 | 73~77 | 1000 | 218 | ok |
| yolo26-n-pose_640x640.dxnn | 8 | 3 | 240.3 ±3.9 | 30.0 | 211 | 76.0 | 91.4 | 80~82 | 1000 | 224 | ok |
| yolo26-n-pose_640x640.dxnn | 9 | 3 | 240.2 ±4.3 | 26.7 | 212 | 75.5 | 91.7 | 82~83 | 1000 | 231 | ok |
| yolo26-s-pose_640x640.dxnn | 5 | 3 | 173.2 ±6.0 | 34.6 | 155 | 91.7 | 99.4 | 79~84 | 800~1000 | 230 | ok |
| yolo26-s-pose_640x640.dxnn | 6 | 3 | 148.1 ±1.5 | 24.7 | 137 | 94.1 | 100.0 | 84 | 600~1000 | 236 | ok |
| yolo26-m-pose_640x640.dxnn | 3 | 3 | 70.8 ±2.2 | 23.6 | 82 | 93.6 | 100.0 | 82~83 | 400~800 | 245 | ok |
| yolo26-m-pose_640x640.dxnn | 2 | 3 | 67.3 ±0.6 | 33.7 | 84 | 92.7 | 100.0 | 83~84 | 400~1000 | 237 | ok |
| yolo26-l-pose_640x640.dxnn | 2 | 3 | 54.9 ±2.6 | 27.5 | 76 | 93.7 | 100.0 | 82~83 | 400~1000 | 250 | ok |
| yolo26-l-pose_640x640.dxnn | 1 | 3 | 82.4 ±1.5 | 82.4 | 87 | 88.2 | 100.0 | 74~80 | 800~1000 | 237 | ok |
| yolo26-x-pose_640x640.dxnn | 1 | 3 | 35.2 ±5.8 | 35.2 | 60 | 93.0 | 100.0 | 80~83 | 400~1000 | 352 | ok |
| yolo26-x-pose_640x640.dxnn | 2 | 3 | 26.5 ±0.2 | 13.2 | 54 | 94.5 | 100.0 | 83 | 400~1000 | 352 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-pose_640x640.dxnn | 6 | 31.8 | 8 | 30.0 |
| yolo26-s-pose_640x640.dxnn | 5 | 32.2 | 5 | 34.6 |
| yolo26-m-pose_640x640.dxnn | 2 | 33.0 | 2 | 33.7 |
| yolo26-l-pose_640x640.dxnn | 1 | 82.3 | 1 | 82.4 |
| yolo26-x-pose_640x640.dxnn | 1 | 34.7 | 1 | 35.2 |

### Segmentation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 2 | 3 | 86.6 ±0.4 | 43.3 | 316 | 30.7 | 51.9 | 68~71 | 1000 | 306 | ok |
| yolo26-n-seg_640x640.dxnn | 3 | 3 | 87.4 ±0.1 | 29.1 | 318 | 31.2 | 53.3 | 74~75 | 1000 | 313 | ok |
| yolo26-s-seg_640x640.dxnn | 2 | 3 | 79.6 ±0.1 | 39.8 | 279 | 50.1 | 79.0 | 74~78 | 1000 | 328 | ok |
| yolo26-s-seg_640x640.dxnn | 3 | 3 | 79.1 ±0.3 | 26.4 | 281 | 50.1 | 79.2 | 81~82 | 1000 | 340 | ok |
| yolo26-m-seg_640x640.dxnn | 2 | 3 | 40.5 ±1.1 | 20.2 | 135 | 95.8 | 100.0 | 84 | 300~1000 | 362 | ok |
| yolo26-m-seg_640x640.dxnn | 1 | 3 | 60.2 ±5.5 | 60.2 | 205 | 79.6 | 100.0 | 77~81 | 400~1000 | 344 | ok |
| yolo26-l-seg_640x640.dxnn | 1 | 3 | 49.6 ±7.6 | 49.6 | 174 | 88.4 | 100.0 | 79~83 | 400~1000 | 358 | ok |
| yolo26-l-seg_640x640.dxnn | 2 | 3 | 33.3 ±0.2 | 16.7 | 100 | 96.0 | 100.0 | 84~85 | 300~800 | 378 | ok |
| yolo26-x-seg_640x640.dxnn | 1 | 3 | 19.3 ±2.6 | 19.3 | 83 | 89.9 | 100.0 | 81~83 | 400~1000 | 468 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 2 | 3 | 78.5 ±1.9 | 39.2 | 276 | 23.1 | 74.6 | 67~69 | 1000 | 334 | ok |
| yolo26-n-seg_640x640.dxnn | 3 | 3 | 78.7 ±1.6 | 26.2 | 276 | 23.5 | 75.5 | 72 | 1000 | 342 | ok |
| yolo26-s-seg_640x640.dxnn | 2 | 3 | 77.6 ±0.2 | 38.8 | 265 | 44.5 | 73.7 | 74~77 | 1000 | 358 | ok |
| yolo26-s-seg_640x640.dxnn | 3 | 3 | 77.2 ±0.3 | 25.8 | 273 | 44.8 | 76.0 | 80~81 | 1000 | 366 | ok |
| yolo26-m-seg_640x640.dxnn | 2 | 3 | 38.9 ±1.0 | 19.4 | 129 | 95.9 | 100.0 | 84~85 | 300~800 | 380 | ok |
| yolo26-m-seg_640x640.dxnn | 1 | 3 | 62.5 ±8.9 | 62.5 | 210 | 87.3 | 100.0 | 79~82 | 400~1000 | 367 | ok |
| yolo26-l-seg_640x640.dxnn | 1 | 3 | 48.6 ±9.9 | 48.6 | 166 | 90.0 | 100.0 | 80~83 | 400~1000 | 380 | ok |
| yolo26-l-seg_640x640.dxnn | 2 | 3 | 33.2 ±0.4 | 16.6 | 107 | 96.5 | 100.0 | 84~85 | 300~800 | 395 | ok |
| yolo26-x-seg_640x640.dxnn | 1 | 3 | 18.3 ±2.1 | 18.3 | 81 | 92.4 | 100.0 | 82~84 | 400~800 | 478 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-seg_640x640.dxnn | 2 | 43.3 | 2 | 39.2 |
| yolo26-s-seg_640x640.dxnn | 2 | 39.8 | 2 | 38.8 |
| yolo26-m-seg_640x640.dxnn | 1 | 60.2 | 1 | 62.5 |
| yolo26-l-seg_640x640.dxnn | 1 | 49.6 | 1 | 48.6 |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 3 | 3 | 102.0 ±0.4 | 34.0 | 162 | 91.0 | 100.0 | 75~80 | 1000 | 243 | ok |
| yolo26-n-obb_1024x1024.dxnn | 4 | 3 | 101.0 ±1.5 | 25.2 | 162 | 92.7 | 100.0 | 84~85 | 800~1000 | 254 | ok |
| yolo26-s-obb_1024x1024.dxnn | 2 | 3 | 58.7 ±2.8 | 29.3 | 102 | 92.6 | 100.0 | 82~84 | 600~1000 | 255 | ok |
| yolo26-s-obb_1024x1024.dxnn | 1 | 3 | 62.4 ±0.9 | 62.4 | 97 | 91.3 | 100.0 | 69~75 | 1000 | 239 | ok |
| yolo26-m-obb_1024x1024.dxnn | 1 | 3 | 35.8 ±4.6 | 35.8 | 78 | 90.5 | 100.0 | 79~82 | 400~1000 | 272 | ok |
| yolo26-m-obb_1024x1024.dxnn | 2 | 3 | 25.4 ±0.5 | 12.7 | 68 | 94.7 | 100.0 | 83~84 | 400~800 | 285 | ok |
| yolo26-l-obb_1024x1024.dxnn | 1 | 3 | 25.2 ±3.8 | 25.2 | 65 | 91.3 | 100.0 | 80~83 | 400~1000 | 288 | ok |
| yolo26-x-obb_1024x1024.dxnn | 1 | 3 | 10.5 ±0.8 | 10.5 | 39 | 89.2 | 100.0 | 82~83 | 400~1000 | 391 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 3 | 3 | 100.3 ±0.2 | 33.4 | 162 | 93.7 | 100.0 | 75~80 | 1000 | 248 | ok |
| yolo26-n-obb_1024x1024.dxnn | 4 | 3 | 100.0 ±0.8 | 25.0 | 161 | 94.5 | 100.0 | 83~84 | 800~1000 | 259 | ok |
| yolo26-s-obb_1024x1024.dxnn | 2 | 3 | 59.0 ±3.5 | 29.5 | 106 | 93.4 | 100.0 | 82~84 | 600~1000 | 252 | ok |
| yolo26-s-obb_1024x1024.dxnn | 1 | 3 | 61.0 ±0.8 | 61.0 | 108 | 89.0 | 100.0 | 69~74 | 1000 | 237 | ok |
| yolo26-m-obb_1024x1024.dxnn | 1 | 3 | 37.0 ±4.5 | 37.0 | 82 | 92.7 | 100.0 | 79~81 | 400~1000 | 271 | ok |
| yolo26-m-obb_1024x1024.dxnn | 2 | 3 | 25.5 ±0.3 | 12.8 | 73 | 94.6 | 100.0 | 83 | 400~800 | 284 | ok |
| yolo26-l-obb_1024x1024.dxnn | 1 | 3 | 25.3 ±4.0 | 25.3 | 69 | 92.2 | 100.0 | 80~83 | 400~1000 | 286 | ok |
| yolo26-x-obb_1024x1024.dxnn | 1 | 3 | 10.4 ±0.9 | 10.4 | 38 | 91.0 | 100.0 | 83~84 | 400~1000 | 389 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-obb_1024x1024.dxnn | 3 | 34.0 | 3 | 33.4 |
| yolo26-s-obb_1024x1024.dxnn | 1 | 62.4 | 1 | 61.0 |
| yolo26-m-obb_1024x1024.dxnn | 1 | 35.8 | 1 | 37.0 |

---
*Report generated by dx-benchmark tool*
