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
pipeline (`dx-agent-compiler-convert` → `dxcom`) only for non-detection tasks,
non-YOLO/custom graphs, or when fine control over `config.json` is required.

Key facts (full reference: `.deepx/toolsets/ultralytics-deepx-export.md`):

- **x86-64 Linux only** for export (`dx_com` has no ARM64); **detection only**; **INT8 enforced**.
- Output is a **directory** `<model>_deepx_model/` = `{<model>.dxnn, config.json, metadata.yaml}` — not a bare `.dxnn`.
- Calibration: EMA, default 100 images (`data` / `fraction` to tune).
- Deploy: `YOLO("<model>_deepx_model")` → `model(source)` on the `dx_engine` runtime
  (backend converts BCHW float `[0,1]` → HWC uint8 `[0,255]`). Inference is not ARM64-restricted.
- `dx_com` auto-installs via Ultralytics' export (version pinned by the installed
  `ultralytics` release). **Do NOT manually `pip install dx-com` from a hardcoded SDK
  URL/version** — it pins a stale compiler; to update, upgrade `ultralytics`.
- **Deployment prerequisite**: the `dx_engine` **runtime** is end-user-installed —
  Ultralytics auto-installs it **only on Debian Trixie/arm64** (sixfab-dx). On the
  x86-64 dx-all-suite the backend raises `OSError: dx_engine is not installed. … Please
  install dx_engine manually and try again` → here "install manually" = **install the
  `dx_rt` runtime** (provides `dxrt-cli`+`dx_engine`): `dx-runtime/scripts/sanity_check.sh
  --dx_rt`, then `dx-runtime/install.sh --all --exclude-app --exclude-stream
  --skip-uninstall --venv-reuse` (dx_app/dx_stream NOT needed → skip to save time), retry.
  NPU init failure → cold boot. Never `pip install dx_engine` on x86-64 or fake via PYTHONPATH.
