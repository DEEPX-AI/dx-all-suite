# RapidDoc PDF->Markdown — NPU Performance Summary

- **Date**: 2026-06-12 15:47:48
- **Pipeline Mode**: finegrained
- **Files**: 1 (sample_input)
- **Total Pages**: 9
- **Wall Time**: 12.50 s
- **Throughput**: 0.72 pages/s

## Model Loading

| Model | Load Time |
|:---|---:|
| formula | 0.98 s |
| layout | 0.17 s |
| ocr | 0.54 s |
| table | 0.04 s |

## Per-Stage Performance (NPU pipeline)

| Pipeline Step | Count | Avg Latency | Throughput | Time (s) | Ratio |
|:---|---:|---:|---:|---:|---:|
| Layout (NPU) | 9 | 281.81 ms | 3.5 FPS | 2.54 | 22.0% |
| PDF text-det | 82 | 0.46 ms | 2156.9 FPS | 0.04 | 0.3% |
| Table (NPU) | 13 | 689.69 ms | 1.4 FPS | 8.97 | 77.7% |

- **Total Stage Time**: 11.54 s
- **Avg per Page**: 1.28 s
