"""
dx_com SDK 설치 및 샘플 데이터 다운로드를 관리하는 서비스.
경로 관계:
  Studio 앱:   {all-suite}/dx-ai-studio/dx_compiler/
  SDK 패키지:  {all-suite}/dx-compiler/
  install.sh:  {all-suite}/dx-compiler/install.sh
  샘플 스크립트: {all-suite}/dx-compiler/example/
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, Generator, List, Optional

from dx_compiler.core.config import (
    SDK_ROOT, SDK_EXAMPLE, SDK_PROPS,
    SAMPLE_MODELS_DIR, CALIB_DIR, SCRIPT_DIR
)

# 샘플 모델 목록 (getting-started 기준)
SAMPLE_MODELS = [
    {"name": "YOLOV5S-1", "onnx": "YOLOV5S-1.onnx", "config": "YOLOV5S-1.json"},
    {"name": "YOLOV5S_Face-1", "onnx": "YOLOV5S_Face-1.onnx", "config": "YOLOV5S_Face-1.json"},
    {"name": "MobileNetV2-1", "onnx": "MobileNetV2-1.onnx", "config": "MobileNetV2-1.json"},
]

# venv 탐색 순서
VENV_CANDIDATES = [
    "venv-dx-compiler-local",  # 호스트
    "venv-dx-compiler",        # 컨테이너
]


class SetupService:
    """dx_com SDK 설치 및 샘플 데이터 다운로드를 관리"""

    def __init__(self):
        self._props = self._load_properties()


    def check_status(self) -> dict:
        """전체 셋업 상태 반환 (/setup/status 응답)"""
        venv_python = self.get_venv_python()
        dx_com_info = self._check_dx_com(venv_python)
        venv = self._find_venv()

        return {
            "dx_com_installed": dx_com_info["installed"],
            "dx_com_version": dx_com_info.get("version"),
            "venv_path": str(venv) if venv else None,
            "venv_python": str(venv_python) if venv_python else None,
            "sample_models": self._check_samples(),
            "calibration_data": self._check_calibration(),
        }

    def get_venv_python(self) -> Optional[Path]:
        """venv의 python3 경로 반환"""
        venv = self._find_venv()
        if venv:
            py = venv / "bin" / "python3"
            if py.exists():
                return py
        return None

    def get_sample_models(self) -> List[dict]:
        """다운로드된 샘플 모델 목록 + 경로"""
        result = []
        for m in SAMPLE_MODELS:
            onnx_path = SAMPLE_MODELS_DIR / "onnx" / m["onnx"]
            config_path = SAMPLE_MODELS_DIR / "json" / m["config"]
            result.append({
                "name": m["name"],
                "downloaded": onnx_path.exists() and config_path.exists(),
                "onnx_path": str(onnx_path) if onnx_path.exists() else None,
                "config_path": str(config_path) if config_path.exists() else None,
            })
        return result


    def install_sdk(self) -> Generator[dict, None, None]:
        """dx_com 설치/재설치. venv가 있으면 pip으로 직접 설치, 없으면 install.sh 안내"""
        venv_python = self.get_venv_python()

        if venv_python:
            # venv 존재 → pip으로 직접 wheel 설치 (sudo 불필요)
            yield from self._pip_install_dx_com(venv_python)
        else:
            # venv 미존재 → 터미널에서 install.sh 실행 안내
            yield {"type": "error",
                   "message": "Virtual environment not found. "
                              "Please run install.sh from the terminal first: "
                              f"cd {SDK_ROOT} && bash install.sh --target=dx_com"}

    def _pip_install_dx_com(self, venv_python) -> Generator[dict, None, None]:
        """venv pip으로 dx_com wheel 설치"""
        dx_com_dir = SDK_ROOT / "dx_com"
        py_tag = f"cp{sys.version_info.major}{sys.version_info.minor}"
        wheels = list(dx_com_dir.glob("*.whl"))

        if not wheels:
            yield {"type": "error", "message": f"No wheel file found in {dx_com_dir}"}
            return

        # Python 버전에 맞는 wheel 찾기
        matching = [w for w in wheels if py_tag in w.name]
        wheel = matching[0] if matching else wheels[0]

        yield {"type": "progress", "progress": 10, "message": f"Found wheel: {wheel.name}"}

        pip_path = venv_python.parent / "pip3"
        if not pip_path.exists():
            pip_path = venv_python.parent / "pip"
        cmd = [str(venv_python), "-m", "pip", "install", "--force-reinstall", str(wheel)]

        try:
            yield {"type": "progress", "progress": 20, "message": "Installing with pip..."}
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, cwd=str(SDK_ROOT)
            )
            total_lines = 0
            for line in proc.stdout:
                total_lines += 1
                line = line.rstrip()
                progress = min(90, 20 + total_lines * 3)
                yield {"type": "progress", "progress": progress, "message": line}

            proc.wait()
            if proc.returncode == 0:
                yield {"type": "complete", "progress": 100, "message": "dx_com reinstalled successfully"}
            else:
                yield {"type": "error", "message": f"pip install failed (exit {proc.returncode})"}
        except Exception as e:
            yield {"type": "error", "message": str(e)}


    def download_samples(self) -> Generator[dict, None, None]:
        """샘플 모델 + 캘리브레이션 데이터 다운로드"""
        scripts = [
            (SDK_EXAMPLE / "1-download_sample_models.sh", "Downloading sample models..."),
            (SDK_EXAMPLE / "2-download_sample_calibration_dataset.sh", "Downloading calibration data..."),
        ]
        total_scripts = len(scripts)

        for idx, (script, desc) in enumerate(scripts):
            if not script.exists():
                yield {"type": "error", "message": f"Script not found: {script}"}
                return

            yield {"type": "progress", "progress": int(idx / total_scripts * 100), "message": desc}

            try:
                proc = subprocess.Popen(
                    ["bash", str(script)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, cwd=str(SDK_EXAMPLE)
                )
                for line in proc.stdout:
                    line = line.rstrip()
                    if line:
                        yield {"type": "log", "message": line}

                proc.wait()
                if proc.returncode != 0:
                    yield {"type": "error", "message": f"{script.name} failed (exit {proc.returncode})"}
                    return
            except Exception as e:
                yield {"type": "error", "message": str(e)}
                return

        yield {"type": "complete", "progress": 100, "message": "All downloads complete"}


    def _find_venv(self) -> Optional[Path]:
        for name in VENV_CANDIDATES:
            venv = SDK_ROOT / name
            if venv.is_dir() and (venv / "bin" / "python3").exists():
                return venv
        return None

    def _check_dx_com(self, venv_python: Optional[Path]) -> dict:
        if not venv_python:
            return {"installed": False}
        try:
            result = subprocess.run(
                [str(venv_python), "-c",
                 "import dx_com; print(getattr(dx_com, '__version__', 'unknown'))"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return {"installed": True, "version": result.stdout.strip()}
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return {"installed": False}

    def _check_samples(self) -> dict:
        result = {}
        for m in SAMPLE_MODELS:
            onnx_path = SAMPLE_MODELS_DIR / "onnx" / m["onnx"]
            config_path = SAMPLE_MODELS_DIR / "json" / m["config"]
            downloaded = onnx_path.exists() and config_path.exists()
            result[m["name"]] = {
                "downloaded": downloaded,
                "onnx_path": str(onnx_path) if downloaded else None,
                "config_path": str(config_path) if downloaded else None,
            }
        return result

    def _check_calibration(self) -> dict:
        downloaded = CALIB_DIR.is_dir() and any(CALIB_DIR.iterdir())
        return {
            "downloaded": downloaded,
            "path": str(CALIB_DIR) if downloaded else None,
        }

    def _load_properties(self) -> dict:
        props = {}
        if SDK_PROPS.exists():
            for line in SDK_PROPS.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    props[key.strip()] = val.strip()
        return props


# 싱글턴
setup_service = SetupService()
