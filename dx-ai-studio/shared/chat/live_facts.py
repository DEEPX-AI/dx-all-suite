"""Facts about this PC's installation for the chat system prompt.

The knowledge pages describe both dx_app example layouts (legacy and per-model). Answering from them, a model gave
the legacy path and an invented `--input` flag on a box with the per-model layout (2026-10-11 real-use audit), so
the prompt carries the layout Studio detected and a command that runs here.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from shared import dx_app_layout
from shared.paths import DX_APP_ROOT

# an example most questions are about; the first found wins, else the first object_detection example
_PREFERRED = ("yolo26-n_640x640", "yolo26n", "yolov8-n_640x640", "yolov8n", "yolov5-s_640x640", "yolov5s")
_SAMPLE = "sample/img/sample_dog.jpg"


def _pick(root: Path):
    exs = [e for e in dx_app_layout.examples(root) if e.py_dir is not None]
    by_name = {e.name: e for e in exs}
    for name in _PREFERRED:
        if name in by_name:
            return by_name[name]
    det = sorted((e for e in exs if e.task == "object_detection"), key=lambda e: e.name)
    return det[0] if det else (sorted(exs, key=lambda e: (e.task, e.name))[0] if exs else None)


def _runtime_venv() -> str:
    try:
        from shared.runtime import runtime_venv_roots
        for venv in runtime_venv_roots():
            if (Path(venv) / "bin" / "python3").is_file():
                return str(venv)
    except (ImportError, OSError):
        pass
    return ""


@lru_cache(maxsize=4)
def _facts(root: str) -> str:
    base = Path(root)
    if not (base / "src").is_dir():
        return ""
    ex = _pick(base)
    if ex is None:
        return ""
    per_model = dx_app_layout.detect(base) == dx_app_layout.PER_MODEL
    script = (ex.py_dir / f"{ex.name}_sync.py").relative_to(base).as_posix()
    model = f"assets/models/{ex.name}.dxnn"
    lines = [
        f"- dx_app: {base}",
        ("- 예제 폴더 모양: per-model — model 마다 한 폴더, 폴더 · 파일 · binary 이름이 .dxnn 이름 (stem) 과 같다. "
         "knowledge 의 다른 모양 (legacy) 경로는 이 PC 에 없다.") if per_model else
        ("- 예제 폴더 모양: legacy — model 이름 폴더 (예: object_detection/yolo26n/). "
         "knowledge 의 per-model 경로는 이 PC 에 없다."),
        f"- Python 예제 실행 (dx_app 폴더에서): python {script} -m {model} -i {_SAMPLE}",
        "- Python 입력 옵션: --image/-i (이미지), --video/-v, --camera/-c, --rtsp/-r. 화면 없이: --no-display. "
        "-m 을 빼면 예제의 기본 model 을 받는다.",
    ]
    venv = _runtime_venv()
    if venv:
        lines.append(f"- dx_engine 이 든 venv: {venv} (먼저 source {venv}/bin/activate)")
    # dx_app 이 C++ binary 를 찾는 순서 그대로 (dx_app/core/config.py _BUILD_DIR_CANDIDATES)
    dirs = [d for d in (base / "build_x86_64" / "src" / "cpp_example", base / "build_aarch64" / "src" / "cpp_example",
                        base / "bin") if d.is_dir()]
    exe = next((d / f"{ex.name}_sync" for d in dirs if os.access(d / f"{ex.name}_sync", os.X_OK)), None)
    if exe is not None:
        lines.append(f"- C++ 예제 실행: ./{exe.relative_to(base).as_posix()} -m {model} -i {_SAMPLE}")
    elif dirs and any(os.access(f, os.X_OK) and f.is_file() for f in dirs[0].iterdir()):
        lines.append(f"- C++ binary 는 {dirs[0].relative_to(base).as_posix()}/<model>_sync 에 있다 — {ex.name} 은 아직 "
                     "build 되지 않았다 (dx_app 폴더에서 ./build.sh).")
    else:
        lines.append("- C++ 예제는 이 PC 에서 아직 build 되지 않았다 (dx_app 폴더에서 ./build.sh).")
    lines.append("- RTSP · udp 입력은 -r <URL> (-v 는 디스크의 파일만 받는다).")
    return "## 이 PC 의 dx_app (Studio 가 확인한 사실 — knowledge 와 다르면 이것을 따른다)\n" + "\n".join(lines)


def dx_app_facts(root=DX_APP_ROOT) -> str:
    try:
        return _facts(str(root))
    except (OSError, ValueError):
        return ""


def clear_cache() -> None:
    _facts.cache_clear()


def system_facts() -> str:
    return dx_app_facts()
