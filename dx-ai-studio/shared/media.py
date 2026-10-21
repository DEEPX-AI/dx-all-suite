"""Run OpenCV operations without importing native packages into Studio."""
import json
import os
import shutil
import subprocess
import sys
import threading
from functools import lru_cache
from pathlib import Path

from shared import runtime


class MediaError(RuntimeError):
    """A compatible media interpreter or operation is unavailable."""


def _environment():
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)
    return env


_FAILURE_LOCK = threading.Lock()
_FAILURE = []   # the cached MediaError text, when no compatible interpreter was found


def media_python():
    """The first interpreter that imports numpy + cv2. Success and failure are both cached for the
    process: a board without OpenCV must not repeat probes of up to 15 s each on every request.
    ``media_python.cache_clear()`` (called when a Setup step finishes) probes again."""
    with _FAILURE_LOCK:
        if _FAILURE:
            raise MediaError(_FAILURE[0])
        try:
            return _probe_media_python()
        except MediaError as error:
            _FAILURE[:] = [str(error)]
            raise


def _media_cache_clear():
    with _FAILURE_LOCK:
        _probe_media_python.cache_clear()
        _FAILURE.clear()


media_python.cache_clear = _media_cache_clear


@lru_cache(maxsize=1)
def _probe_media_python():
    candidates = [
        root / "bin" / "python3"
        for root in [runtime.STUDIO_INFER_VENV, *runtime.runtime_venv_roots()]
    ]
    candidates.extend([sys.executable, shutil.which("python3"), "/usr/bin/python3"])
    errors = []
    for candidate in dict.fromkeys(str(path) for path in candidates if path):
        if not Path(candidate).is_file():
            continue
        try:
            result = subprocess.run(
                [candidate, "-I", "-B", "-c", "import numpy, cv2; print(cv2.__version__)"],
                env=_environment(), capture_output=True, text=True, timeout=15,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            errors.append(f"{candidate}: {error}")
            continue
        if result.returncode == 0:
            return candidate
        errors.append(f"{candidate}: {result.stderr.strip()[-1000:]}")
    detail = "\n".join(errors) or "No Python interpreter found"
    raise MediaError(
        "OpenCV media runtime unavailable. Check Python/OpenCV in Studio Setup "
        f"and repair the compatible environment.\n{detail}"
    )


def run_media(operation, **params):
    worker = Path(__file__).with_name("media_worker.py")
    try:
        result = subprocess.run(
            [media_python(), "-I", "-B", str(worker), operation],
            input=json.dumps(params), env=_environment(),
            capture_output=True, text=True, timeout=30,
        )
    except subprocess.TimeoutExpired as error:
        raise MediaError(f"Media {operation} timed out") from error
    except OSError as error:
        raise MediaError(f"Media {operation} could not start: {error}") from error
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise MediaError(f"Media {operation} failed: {detail}")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise MediaError(f"Media {operation} returned invalid JSON") from error
    if not isinstance(payload, dict):
        raise MediaError(f"Media {operation} returned an invalid result")
    return payload
