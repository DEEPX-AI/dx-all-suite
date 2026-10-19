"""
Installs the dx_com SDK and downloads the sample data.
Paths:
  Studio app:     {all-suite}/dx-ai-studio/dx_compiler/
  SDK package:    {all-suite}/dx-compiler/
  install.sh:     {all-suite}/dx-compiler/install.sh
  Sample scripts: {all-suite}/dx-compiler/example/
"""
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Generator, List, Optional

from dx_compiler.core.config import (
    SDK_ROOT, SDK_EXAMPLE, SDK_PROPS,
    SAMPLE_MODELS_DIR, CALIB_DIR, SCRIPT_DIR
)

# Sample models (as in getting-started)
SAMPLE_MODELS = [
    {"name": "YOLOV5S-1", "onnx": "YOLOV5S-1.onnx", "config": "YOLOV5S-1.json"},
    {"name": "YOLOV5S_Face-1", "onnx": "YOLOV5S_Face-1.onnx", "config": "YOLOV5S_Face-1.json"},
    {"name": "MobileNetV2-1", "onnx": "MobileNetV2-1.onnx", "config": "MobileNetV2-1.json"},
]

# venv lookup order
VENV_CANDIDATES = [
    "venv-dx-compiler-local",  # host
    "venv-dx-compiler",        # container
]

# dx-com requires torch, and the default x86 torch pulls in the CUDA libraries (~5 GB of disk). dxcom compiles
# on the CPU, so they are unused on a host without an NVIDIA GPU and can fill a small board's disk ("No space
# left on device"). Only on such hosts, add the CPU torch index (same torch, +cpu build).
TORCH_CPU_INDEX = "https://download.pytorch.org/whl/cpu"


# The probe starts the venv's python and imports dx_com (and with it torch): ~1.5 s on a board.
# /feature-check and /setup/status both asked on every call, so the Compiler page waited for it on
# every load. The answer changes only when the installed package does — the key is the dx_com
# package folder and its mtime. Only "installed" answers are kept, so an install shows up at once.
_DX_COM_PROBE: Dict[tuple, dict] = {}


def _dx_com_probe_key(venv_python: Path) -> Optional[tuple]:
    venv = Path(venv_python).parent.parent
    for pkg in sorted(venv.glob("lib/python*/site-packages/dx_com")):
        try:
            return (str(pkg), pkg.stat().st_mtime_ns)
        except OSError:
            return None
    return None


def _has_nvidia_gpu() -> bool:
    return Path("/dev/nvidia0").exists() or shutil.which("nvidia-smi") is not None


def _pip_env(env: Dict[str, str]) -> Dict[str, str]:
    """Pick the torch build pip installs to suit this host. A user-chosen index (PIP_INDEX_URL, PIP_EXTRA_INDEX_URL) wins."""
    if not _has_nvidia_gpu() and not env.get("PIP_INDEX_URL") and not env.get("PIP_EXTRA_INDEX_URL"):
        env["PIP_EXTRA_INDEX_URL"] = TORCH_CPU_INDEX
    return env


class SetupService:
    """Installs the dx_com SDK and downloads the sample data."""

    def __init__(self):
        self._props = self._load_properties()


    def check_status(self) -> dict:
        """Return the full setup status (the /setup/status response)."""
        venv_python = self.get_venv_python()
        dx_com_info = self._check_dx_com(venv_python)
        venv = self._find_venv()

        # dx_com may be importable in the *main* process (plain `pip install`, or any layout
        # without a sibling `venv-dx-compiler*`). /feature-check already honors this in-process
        # path; the Setup panel must too — otherwise it greys out & disables the whole compile
        # form even though compilation works (reported as "Input UI is unusable"). Treat
        # in-process availability as installed.
        version = dx_com_info.get("version")
        in_process = False
        import importlib.util
        if importlib.util.find_spec("dx_com") is not None:
            try:
                import dx_com
            except ImportError:
                pass
            else:
                in_process = True
                if not version:
                    version = getattr(dx_com, "__version__", "unknown")

        sdk_present = SDK_ROOT.exists() and (SDK_ROOT / "install.sh").exists()
        return {
            "dx_com_installed": dx_com_info["installed"] or in_process,
            "dx_com_version": version,
            "venv_path": str(venv) if venv else None,
            "venv_python": str(venv_python) if venv_python else None,
            "sample_models": self._check_samples(),
            "calibration_data": self._check_calibration(),
            # True when install-sdk will call install.sh (no local wheel) and needs sudo up front.
            "install_requires_sudo": sdk_present and not self._local_wheel_available(),
        }

    def get_venv_python(self) -> Optional[Path]:
        """Return the path of the venv's python3."""
        venv = self._find_venv()
        if venv:
            py = venv / "bin" / "python3"
            if py.exists():
                return py
        return None

    def get_sample_models(self) -> List[dict]:
        """Downloaded sample models and their paths."""
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


    def install_sdk(self, sudo_password: str = None) -> Generator[dict, None, None]:
        """Install or reinstall dx_com.

        - Wheel already on disk: create the venv if missing, then pip install. No sudo or network needed.
        - No wheel (fresh): download and install with install.sh. It runs `sudo apt` inside, so it needs the
          admin password, passed non-interactively through SUDO_ASKPASS (entered on the web page).
          Safe to re-run (idempotent)."""
        if self._local_wheel_available():
            venv_python = self.get_venv_python()
            if not venv_python:
                yield from self._create_venv()
                venv_python = self.get_venv_python()
            if venv_python:
                yield from self._pip_install_dx_com(venv_python)
            else:
                yield {"type": "error",
                       "message": "Could not create a virtual environment automatically. "
                                  "Please run install.sh from the terminal: "
                                  f"cd {SDK_ROOT} && bash install.sh --target=dx_com"}
            return

        # No local wheel: install.sh must download and install it (needs sudo).
        if not SDK_ROOT.exists() or not (SDK_ROOT / "install.sh").exists():
            yield {"type": "error",
                   "message": f"DX Compiler SDK not found at {SDK_ROOT}. "
                              "Fetch it first (git submodule update --init dx-compiler)."}
            return
        if not sudo_password:
            # Tell the front end to show the password dialog; it retries with the password.
            yield {"type": "need_sudo",
                   "message": "Administrator (sudo) password is required to download and "
                              "install the DX Compiler SDK."}
            return
        yield from self._run_install_sh(sudo_password)

    def _local_wheel_available(self) -> bool:
        try:
            return bool(list((SDK_ROOT / "dx_com").glob("*.whl")))
        except OSError:
            return False

    def _run_install_sh(self, sudo_password: str) -> Generator[dict, None, None]:
        """Stream `install.sh --target=dx_com` (download, venv, dx_com install).

        The inner `sudo apt` authenticates non-interactively through SUDO_ASKPASS (shared). Safe to re-run:
        an existing venv is kept with --venv-reuse and only dx_com is reinstalled."""
        import threading
        from shared.sudo_askpass import configure_sudo_env, preauthorize_sudo, keep_sudo_alive

        env = _pip_env(os.environ.copy())
        # PEP 668 (Ubuntu 24.04+): keep the inner pip fallback from failing hard on the system Python.
        env.setdefault("PIP_BREAK_SYSTEM_PACKAGES", "1")
        cleanup = configure_sudo_env(env, sudo_password)
        sudo_err = preauthorize_sudo(sudo_password, env)
        if sudo_err:
            cleanup()
            # A separate type so the front end can tell a wrong password apart and ask again.
            yield {"type": "sudo_auth", "message": f"sudo authentication failed: {sudo_err}"}
            return

        # Just --target=dx_com. install.sh's defaults (--force reinstall + venv-force-remove)
        # make re-runs idempotent. Do NOT add --venv-reuse: force-remove is ON by default, and
        # install.sh rejects both together ("Cannot use both --venv-force-remove and
        # --venv-reuse") → exit 1. Letting it recreate the (compiler-only) venv is fine.
        args = ["bash", str(SDK_ROOT / "install.sh"), "--target=dx_com"]

        yield {"type": "progress", "progress": 3, "message": "Running install.sh --target=dx_com…"}
        stop = threading.Event()
        try:
            threading.Thread(target=keep_sudo_alive, args=(stop,), daemon=True).start()
            proc = subprocess.Popen(
                args, cwd=str(SDK_ROOT), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1, env=env,
            )
            n = 0
            for line in proc.stdout:
                # install.sh emits ANSI color codes → strip them so the web log stays readable.
                line = re.sub(r"\x1b\[[0-9;?]*[a-zA-Z]", "", line).rstrip()
                if not line:
                    continue
                n += 1
                yield {"type": "progress", "progress": min(95, 5 + n // 3), "message": line}
            proc.wait()
            if proc.returncode == 0:
                yield {"type": "complete", "progress": 100,
                       "message": "DX Compiler SDK installed successfully."}
            else:
                yield {"type": "error",
                       "message": f"install.sh failed (exit {proc.returncode}). See the log above."}
        except Exception as exc:
            yield {"type": "error", "message": f"install.sh execution failed: {exc}"}
        finally:
            stop.set()
            cleanup()

    def _create_venv(self) -> Generator[dict, None, None]:
        """Create the dx_com virtualenv (SDK_ROOT/venv-dx-compiler-local) with the studio's python,
        inheriting platform packages through --system-site-packages."""
        venv_path = SDK_ROOT / VENV_CANDIDATES[0]
        if not SDK_ROOT.exists():
            yield {"type": "error",
                   "message": f"DX Compiler SDK not found at {SDK_ROOT}. "
                              "Install the dx-compiler SDK first."}
            return
        yield {"type": "progress", "progress": 2,
               "message": f"Creating virtual environment ({venv_path.name})…"}
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "venv", "--system-site-packages", str(venv_path)],
                capture_output=True, text=True, timeout=180,
            )
        except (subprocess.TimeoutExpired, OSError) as exc:
            yield {"type": "error", "message": f"Failed to create virtual environment: {exc}"}
            return
        if proc.returncode != 0 or not (venv_path / "bin" / "python3").exists():
            detail = (proc.stderr or proc.stdout or "").strip()[:300]
            yield {"type": "error",
                   "message": f"Failed to create virtual environment: {detail or 'unknown error'}"}
            return
        yield {"type": "progress", "progress": 8, "message": "Virtual environment created."}

    def _pip_install_dx_com(self, venv_python) -> Generator[dict, None, None]:
        """Install the dx_com wheel with the venv's pip."""
        dx_com_dir = SDK_ROOT / "dx_com"
        py_tag = f"cp{sys.version_info.major}{sys.version_info.minor}"
        wheels = list(dx_com_dir.glob("*.whl"))

        if not wheels:
            yield {"type": "error", "message": f"No wheel file found in {dx_com_dir}"}
            return

        # Find the wheel matching this Python version
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
                text=True, cwd=str(SDK_ROOT), env=_pip_env(os.environ.copy())
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
        """Download the sample models and calibration data."""
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
        key = _dx_com_probe_key(venv_python)
        if key is not None and key in _DX_COM_PROBE:
            return dict(_DX_COM_PROBE[key])
        found = {"installed": False}
        try:
            result = subprocess.run(
                [str(venv_python), "-c",
                 "import dx_com; print(getattr(dx_com, '__version__', 'unknown'))"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                found = {"installed": True, "version": result.stdout.strip()}
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        if key is not None and found["installed"]:
            _DX_COM_PROBE[key] = dict(found)
        return found

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


# Singleton
setup_service = SetupService()
