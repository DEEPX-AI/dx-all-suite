## Ultralytics → DeepX Export (One-Shot Path)

Ultralytics YOLO ships a first-class `format=deepx` exporter that produces a
deployable DeepX NPU model in **one command** — it runs ONNX export → INT8 EMA
calibration → `dx_com` compilation → packaging internally:

```bash
yolo export model=yolo26n.pt format=deepx     # creates 'yolo26n_deepx_model/'
```
```python
from ultralytics import YOLO
YOLO("yolo26n.pt").export(format="deepx")      # int8=True is enforced
```

**Prefer this path** for Ultralytics YOLO **detection** models targeting DeepX —
it avoids the common manual PT→ONNX→`dxcom` errors. Fall back to the manual
pipeline (`dx-agentic-compiler-convert` → `dxcom`) only for non-detection tasks,
non-YOLO/custom graphs, or when fine control over `config.json` is required.

Key facts (full reference: `.deepx/toolsets/ultralytics-deepx-export.md`):

- **x86-64 Linux only** for export (`dx_com` has no ARM64); **detection only**; **INT8 enforced**.
- Output is a **directory** `<model>_deepx_model/` = `{<model>.dxnn, config.json, metadata.yaml}` — not a bare `.dxnn`.
- Calibration: EMA, default 100 images (`data` / `fraction` to tune).
- Deploy: `YOLO("<model>_deepx_model")` → `model(source)` on the `dx_engine` runtime
  (backend converts BCHW float `[0,1]` → HWC uint8 `[0,255]`). Inference is not ARM64-restricted.
