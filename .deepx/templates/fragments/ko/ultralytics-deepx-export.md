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
수작업 파이프라인(`dx-agent-compiler-convert` → `dxcom`)으로 fallback 하세요.

핵심 사항 (전체 reference: `.deepx/toolsets/ultralytics-deepx-export.md`):

- export는 **x86-64 Linux 전용** (`dx_com`은 ARM64 미지원), **detection 전용**, **INT8 강제**.
- 출력은 **디렉토리** `<model>_deepx_model/` = `{<model>.dxnn, config.json, metadata.yaml}` — 단일 `.dxnn`가 아님.
- Calibration: EMA, 기본 100장 (`data` / `fraction`으로 조정).
- 배포: `YOLO("<model>_deepx_model")` → `model(source)`로 `dx_engine` runtime에서 실행
  (backend가 BCHW float `[0,1]` → HWC uint8 `[0,255]` 변환). inference는 ARM64 제약 없음.
- `dx_com`은 Ultralytics export가 자동설치(버전은 설치된 `ultralytics` 릴리스에 고정).
  **하드코딩된 SDK URL/버전으로 직접 `pip install dx-com` 금지** — 구버전 compiler가
  고정됩니다. 업데이트하려면 `ultralytics`를 upgrade 하세요.
- **배포 전제조건**: `dx_engine` **runtime**은 end-user 설치 — Ultralytics는
  **Debian Trixie/arm64(sixfab-dx)에서만** 자동설치합니다. x86-64 dx-all-suite에서는 backend가
  `OSError: dx_engine is not installed. … Please install dx_engine manually and try again`
  를 raise → 여기서 "수동 설치" = **`dx_rt` runtime 설치**(`dxrt-cli`+`dx_engine` 제공):
  `dx-runtime/scripts/sanity_check.sh --dx_rt` → `dx-runtime/install.sh --all
  --exclude-app --exclude-stream --skip-uninstall --venv-reuse`(dx_app/dx_stream 불필요 →
  제외로 시간 절약) → 재시도. NPU 초기화 실패는 cold boot. x86-64에서 `pip install
  dx_engine`이나 PYTHONPATH import 위장 금지.
