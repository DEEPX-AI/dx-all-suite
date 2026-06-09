## Ultralytics → DeepX Export (One-Shot Path)

Ultralytics YOLO는 first-class `format=deepx` exporter를 제공합니다. **명령 한 번**으로
배포 가능한 DeepX NPU 모델을 생성하며, 내부적으로 ONNX export → INT8 EMA
calibration → `dx_com` compilation → packaging을 모두 수행합니다:

```bash
yolo export model=yolo26n.pt format=deepx     # 'yolo26n_deepx_model/' 생성
```
```python
from ultralytics import YOLO
YOLO("yolo26n.pt").export(format="deepx")      # int8=True 강제 적용
```

Ultralytics YOLO **detection** 모델을 DeepX로 변환할 때는 **이 경로를 우선 사용**하세요 —
수작업 PT→ONNX→`dxcom` 파이프라인에서 흔한 오류를 피할 수 있습니다. detection이 아닌
task, 비(非)-YOLO/custom graph, 또는 `config.json` 세밀 제어가 필요한 경우에만
수작업 파이프라인(`dx-agentic-compiler-convert` → `dxcom`)으로 fallback 하세요.

핵심 사항 (전체 reference: `.deepx/toolsets/ultralytics-deepx-export.md`):

- export는 **x86-64 Linux 전용** (`dx_com`은 ARM64 미지원), **detection 전용**, **INT8 강제**.
- 출력은 **디렉토리** `<model>_deepx_model/` = `{<model>.dxnn, config.json, metadata.yaml}` — 단일 `.dxnn`가 아님.
- Calibration: EMA, 기본 100장 (`data` / `fraction`으로 조정).
- 배포: `YOLO("<model>_deepx_model")` → `model(source)`로 `dx_engine` runtime에서 실행
  (backend가 BCHW float `[0,1]` → HWC uint8 `[0,255]` 변환). inference는 ARM64 제약 없음.
