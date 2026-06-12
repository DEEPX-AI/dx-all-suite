# RapidDoc PDF->Markdown — NPU Performance Summary

- **Date**: 2026-06-12 14:58:47
- **Pipeline Mode**: finegrained
- **Files**: 1 (sample_input)
- **Total Pages**: 9
- **Wall Time**: 14.65 s
- **Throughput**: 0.61 pages/s

## Model Loading

| Model | Load Time |
|:---|---:|
| formula | 1.03 s |
| layout | 0.17 s |
| ocr | 0.54 s |
| table | 0.04 s |

## Per-Stage Performance (NPU pipeline)

| Pipeline Step | Count | Avg Latency | Throughput | Time (s) | Ratio |
|:---|---:|---:|---:|---:|---:|
| Layout (NPU) | 9 | 374.81 ms | 2.7 FPS | 3.37 | 17.4% |
| OCR det (NPU) | 63 | 55.73 ms | 17.9 FPS | 3.51 | 18.1% |
| Table (NPU) | 13 | 833.94 ms | 1.2 FPS | 10.84 | 56.0% |
| OCR rec (NPU) | 102 | 16.14 ms | 62.0 FPS | 1.65 | 8.5% |

- **Total Stage Time**: 19.37 s
- **Avg per Page**: 2.15 s
