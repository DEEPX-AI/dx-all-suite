# SDK Grounding Reference

> **Canonical API registry** — All API names, class names, and method names in
> `.deepx/` instructions MUST be verifiable against this file or the actual
> SDK source code. Do NOT introduce new API names without first verifying them here.

## Purpose

This document lists verified API symbols extracted from:
- **Official SDK source code** (actual `.py`, `.h`, `.cpp` files)
- **Official SDK documentation** (`dx-compiler/source/docs/`, `dx-runtime/dx_app/docs/`, `dx-runtime/dx_stream/docs/`)

**Anti-hallucination rule**: Any API name, class name, method name, or parameter
name mentioned in `.deepx/` instructions MUST either:
1. Appear in this file, OR
2. Be directly verifiable in SDK source code (provide the file path)

If a symbol cannot be verified in either source, it is a hallucination and MUST
be removed from instructions immediately.

---

## IFactory Interface (dx_app)

**Source**: `dx-runtime/dx_app/src/python_example/common/base/i_factory.py`

### Verified Methods (5 methods — all abstract)

| Method | Signature | Description |
|--------|-----------|-------------|
| `create_preprocessor` | `(self, input_width: int, input_height: int) -> IPreprocessor` | Creates the image preprocessor |
| `create_postprocessor` | `(self, input_width: int, input_height: int) -> IPostprocessor` | Creates the output postprocessor |
| `create_visualizer` | `(self) -> IVisualizer` | Creates the result visualizer |
| `get_model_name` | `(self) -> str` | Returns the DXNN model file name |
| `get_task_type` | `(self) -> str` | Returns the AI task type string |

### Verified IFactory Subclasses (from same file)

| Class | Task |
|-------|------|
| `IDetectionFactory` | Object detection |
| `ISegmentationFactory` | Semantic segmentation |
| `IPoseFactory` | Pose estimation |

### BANNED (Hallucinated — do NOT use)

| Symbol | Status |
|--------|--------|
| `create` | ❌ Not an IFactory method |
| `get_input_params` | ❌ Not an IFactory method |
| `run_inference` | ❌ Not an IFactory method |
| `post_processing` | ❌ Not an IFactory method |
| `release` | ❌ Not an IFactory method |

---

## SyncRunner / AsyncRunner (dx_app)

**Source**: `dx-runtime/dx_app/src/python_example/common/runner/`

### SyncRunner

| Symbol | Signature | Description |
|--------|-----------|-------------|
| `SyncRunner.__init__` | `(self, factory: IFactory, ...)` | Constructs with an IFactory instance |
| `SyncRunner.run` | `(self, args) -> None` | Runs the inference loop |

### AsyncRunner

| Symbol | Signature | Description |
|--------|-----------|-------------|
| `AsyncRunner.__init__` | `(self, factories: list[IFactory], ...)` | Constructs with a list of IFactory instances |
| `AsyncRunner.run` | `(self, args) -> None` | Runs multi-model async inference |

---

## dx_com.compile() API (dx-compiler)

**Source**: `dx-compiler/source/docs/02_06_Execution_of_DX-COM.md`

### Verified Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `model` | `Union[str, onnx.ModelProto]` | ONNX model path or loaded model |
| `output_dir` | `str` | Output directory for compiled .dxnn |
| `config` | `Optional[str]` | Config JSON path (mutually exclusive with `dataloader`) |
| `dataloader` | `Optional[DataLoader]` | Custom dataloader (mutually exclusive with `config`) |
| `calibration_method` | `str` | `"ema"` (default) or `"minmax"` |
| `calibration_num` | `int` | Number of calibration samples (default: 100) |
| `quantization_device` | `Optional[str]` | `None` (auto), `"cpu"`, `"cuda"`, `"cuda:0"` |
| `opt_level` | `int` | Optimization level: `0` or `1` (default: 1) |
| `aggressive_partitioning` | `bool` | Experimental — default `False` |
| `input_nodes` | `Optional[List[str]]` | Custom input node names |
| `output_nodes` | `Optional[List[str]]` | Custom output node names |
| `enhanced_scheme` | `Optional[Dict]` | DXQ precision scheme (P0–P5) |
| `gen_log` | `bool` | Generate compilation log |
| `float64_calibration` | `bool` | Use float64 for calibration |

### Correct Import

```python
import dx_com
dx_com.compile(model="model.onnx", output_dir="./output", ...)
```

### BANNED (Hallucinated parameters — do NOT use)

| Parameter | Status |
|-----------|--------|
| `output_path` | ❌ Wrong — use `output_dir` |
| `model_path` | ❌ Wrong — use `model` |
| `calib_num` | ❌ Wrong — use `calibration_num` |
| `quant_device` | ❌ Wrong — use `quantization_device` |

### Calibration Dataset Pattern

Official pattern from `02_07_Common_Use_Cases.md`:
- Dataset class name is **arbitrary** (e.g., `ImageNetDataset`, `StereoDataset`, `CustomDataDataset`)
- Use **real multiple images** from a directory — NOT single-image augmentation
- Standard pattern: `os.listdir(image_dir)` → iterate all files

### BANNED Calibration Symbols

| Symbol | Status |
|--------|--------|
| `SingleImageCalibDataset` | ❌ Hallucinated — does not exist in dx_com SDK |
| `CALIBRATION_OK` | ❌ Hallucinated log marker — not in dx_com output |

---

## dx_stream GStreamer Elements

**Source**: `dx-runtime/dx_stream/docs/source/docs/`

### Verified DEEPX Custom Elements

| Element | Description |
|---------|-------------|
| `dxpreprocess` | Applies model preprocessing (resize, normalize, etc.) |
| `dxinfer` | Runs NPU inference via .dxnn model |
| `dxpostprocess` | Post-processes model output tensors |
| `dxosd` | On-screen display — overlays detection/tracking results |
| `dxtracker` | Multi-object tracking (OC-SORT algorithm) |

### Verified Standard GStreamer Elements (used in dx_stream pipelines)

| Element | Description |
|---------|-------------|
| `urisourcebin` | Video source from URI |
| `decodebin` | Video decoder |
| `queue` | Buffer queue (prevents deadlocks between processing stages) |
| `x264enc` | H.264 encoder (always use `tune=zerolatency` — see common_pitfalls.md #14) |
| `h264parse` | H.264 stream parser |
| `mp4mux` | MP4 container muxer |
| `filesink` | File output sink |
| `fpsdisplaysink` | Display sink with FPS overlay |
| `ximagesink` | X11 display sink |
| `autovideosink` | Auto-select display sink |
| `tee` | Pipeline splitter |
| `videoconvert` | Video format converter |

---

## Hardware Identifiers

**Source**: Official dx-runtime documentation

| Identifier | Value | Description |
|------------|-------|-------------|
| DX-M1 architecture | `"dx_m1"` | DEEPX M1 NPU |

---

## Verification Procedure

When adding a new API name to any `.deepx/` instruction file:

1. **Check this file first** — Is the symbol listed here?
2. **Check SDK source** — Grep the actual source files:
   ```bash
   grep -rn "<symbol>" dx-runtime/dx_app/src/ dx-compiler/source/ dx-runtime/dx_stream/
   ```
3. **Check SDK docs** — Search official documentation:
   ```bash
   grep -rn "<symbol>" dx-compiler/source/docs/ dx-runtime/dx_app/docs/ dx-runtime/dx_stream/docs/
   ```
4. **If not found** → The symbol is a hallucination. Do NOT add it.
5. **If found** → Add it to this file with source reference, then add to instructions.
