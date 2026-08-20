"""Read-only proof that an installed runtime can support Studio launches."""
from __future__ import annotations

import os
import subprocess
import sysconfig
from pathlib import Path
from typing import Callable, Mapping, Optional, Sequence

from shared.runtime import installed_runtime_lib_dirs, runtime_python
from shared.runtime_contract import ContractResult
from shared.runtime_profile import ContractCheck, RuntimeDefinition


DEFAULT_POSTPROCESS_DIR = Path("/usr/local/share/gstdxstream/lib")
PLUGIN_FILENAME = "libgstdxstream.so"
# The dxstream plugin installs under the running arch's GStreamer multiarch dir (e.g.
# .../x86_64-linux-gnu/gstreamer-1.0 or .../aarch64-linux-gnu/gstreamer-1.0). Derive the current
# arch's triplet dynamically, then list explicit x86_64/aarch64 fallbacks so ARM boards aren't
# left relying on the rglob search in default_plugin_path().
_MULTIARCH = sysconfig.get_config_var("MULTIARCH") or ""
KNOWN_PLUGIN_DIRECTORIES = tuple(
    d for d in (
        (Path("/usr/local/lib") / _MULTIARCH / "gstreamer-1.0") if _MULTIARCH else None,
        (Path("/usr/lib") / _MULTIARCH / "gstreamer-1.0") if _MULTIARCH else None,
        Path("/usr/local/lib/x86_64-linux-gnu/gstreamer-1.0"),
        Path("/usr/local/lib/aarch64-linux-gnu/gstreamer-1.0"),
        Path("/usr/local/lib/gstreamer-1.0"),
        Path("/usr/lib/x86_64-linux-gnu/gstreamer-1.0"),
        Path("/usr/lib/aarch64-linux-gnu/gstreamer-1.0"),
        Path("/usr/lib/gstreamer-1.0"),
    ) if d is not None
)
_PLUGIN_SEARCH_ROOTS = (Path("/usr/local/lib"), Path("/usr/lib"))
_STREAM_PIPELINE_PARSE_PROBE = """
import sys

import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst

Gst.init(None)
pipeline = None
try:
    pipeline = Gst.parse_launch(sys.stdin.read())
finally:
    del pipeline
"""


def _probe_dxinfer_element(plugin_dir: Path, library_dirs: tuple[Path, ...]) -> bool:
    """Return whether the installed plugin exposes the required ``dxinfer`` factory."""
    environment = {
        "PATH": os.defpath,
        "GST_PLUGIN_PATH": str(plugin_dir),
        "LD_LIBRARY_PATH": os.pathsep.join(str(path) for path in library_dirs),
    }
    try:
        result = subprocess.run(
            ["gst-inspect-1.0", "--exists", "dxinfer"],
            env=environment,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return result.returncode == 0


def default_plugin_path() -> Path:
    """Find the installed dxstream plugin without reading GST_PLUGIN_PATH."""
    for directory in KNOWN_PLUGIN_DIRECTORIES:
        candidate = directory / PLUGIN_FILENAME
        if candidate.is_file():
            return candidate
    for root in _PLUGIN_SEARCH_ROOTS:
        try:
            candidate = next(root.rglob(PLUGIN_FILENAME), None)
        except OSError:
            candidate = None
        if candidate is not None:
            return candidate
    return KNOWN_PLUGIN_DIRECTORIES[0] / PLUGIN_FILENAME


def default_plugin_directory() -> Path:
    """Return the deterministic plugin directory for an active runtime context."""
    return default_plugin_path().parent


def _check(check_id: str, path: Path, remediation: str, *, directory: bool = False) -> ContractCheck:
    present = path.is_dir() if directory else path.is_file()
    return ContractCheck(
        check_id=check_id,
        required=str(path),
        observed="present" if present else "missing",
        passed=present,
        remediation=remediation,
    )


def _pipeline_check(*, passed: bool, observed: str) -> ContractResult:
    return ContractResult((ContractCheck(
        check_id="gst.selected_pipeline",
        required="constructible selected GStreamer pipeline",
        observed=observed,
        passed=passed,
        remediation=(
            "Repair the selected Stream graph or its installed GStreamer dependencies, "
            "then rerun Runtime Setup."
        ),
    ),))


def _probe_diagnostic(output: object, fallback: str) -> str:
    text = " ".join(str(output or "").split())
    return text[:500] if text else fallback


def validate_stream_pipeline(
    pipeline: str,
    *,
    python_executable: Path,
    environment: Mapping[str, str],
    timeout: float = 15.0,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> ContractResult:
    """Prove that an exact Stream graph can be constructed without starting it.

    The subprocess receives only the profile-owned environment and performs
    ``Gst.parse_launch()``.  It never changes a GStreamer state, so source reads,
    decoding, and NPU inference cannot start during this admission check.
    """
    if not pipeline.strip():
        return _pipeline_check(passed=False, observed="parse failed: empty pipeline")
    try:
        result = runner(
            [str(python_executable), "-c", _STREAM_PIPELINE_PARSE_PROBE],
            input=pipeline,
            text=True,
            capture_output=True,
            env=dict(environment),
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return _pipeline_check(
            passed=False,
            observed="parse failed: probe timed out after {:.1f}s".format(timeout),
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return _pipeline_check(
            passed=False,
            observed="parse failed: {}".format(_probe_diagnostic(exc, "probe could not start")),
        )

    if result.returncode == 0:
        return _pipeline_check(passed=True, observed="parsed")
    diagnostic = _probe_diagnostic(
        result.stderr or result.stdout,
        "probe exited with status {}".format(result.returncode),
    )
    return _pipeline_check(passed=False, observed="parse failed: {}".format(diagnostic))


def validate_base_runtime(
    *,
    python_probe: Callable[[], Optional[str | Path]] = runtime_python,
    plugin_path: Optional[Path] = None,
    postprocess_dir: Path = DEFAULT_POSTPROCESS_DIR,
    library_dirs: Optional[Sequence[Path]] = None,
    element_probe: Callable[[Path, tuple[Path, ...]], bool] = _probe_dxinfer_element,
) -> ContractResult:
    """Validate base App/Stream launch prerequisites without starting inference.

    ``runtime_python`` only returns interpreters that independently import ``numpy``,
    ``cv2``, and ``dx_engine``. The remaining checks use fixed installed locations,
    never inherited shell paths or source checkout artifacts.
    """
    interpreter_value = python_probe()
    interpreter = Path(interpreter_value) if interpreter_value else Path("<missing-python>")
    plugin = Path(plugin_path) if plugin_path is not None else default_plugin_path()
    postprocess = Path(postprocess_dir)
    libraries = tuple(
        Path(path)
        for path in (library_dirs if library_dirs is not None else installed_runtime_lib_dirs())
        if Path(path).is_dir()
    )
    element_available = plugin.is_file() and element_probe(plugin.parent, libraries)
    return ContractResult((
        _check(
            "app.python",
            interpreter,
            "Repair the Studio-owned inference environment before activation.",
        ),
        _check(
            "gst.plugin",
            plugin,
            "Install or build the Studio-declared dxstream GStreamer plugin.",
        ),
        ContractCheck(
            check_id="gst.dxinfer",
            required="dxinfer GStreamer element factory",
            observed="available" if element_available else "unavailable",
            passed=element_available,
            remediation="Repair the installed dxstream plugin and its native dependencies.",
        ),
        _check(
            "gst.postprocess_directory",
            postprocess,
            "Install the DX Stream postprocess libraries before activation.",
            directory=True,
        ),
    ))


# Which base-runtime contracts each inference module actually needs to launch. dx_stream is a
# pure C++/GStreamer pipeline (no python inference venv); dx_app's python-variant demos need the
# venv. Splitting these lets one module's broken half not gate the other.
_MODULE_CONTRACT_IDS = {
    "dx_stream": frozenset({"gst.plugin", "gst.dxinfer", "gst.postprocess_directory"}),
    "dx_app": frozenset({"app.python"}),
}


def validate_module_contracts(module: str, **validation_options: object) -> ContractResult:
    """ContractResult of only the launch contracts the given module needs.

    Falls back to the full base-runtime result for unknown modules. Used by the launch gate so a
    box with (say) a working Stream plugin but no python inference venv can still run dx_stream."""
    full = validate_base_runtime(**validation_options)
    ids = _MODULE_CONTRACT_IDS.get(module)
    if ids is None:
        return full
    return ContractResult(tuple(c for c in full.checks if c.check_id in ids))


class RuntimeCandidateValidator:
    """Bootstrap adapter that retains details while returning the required boolean."""

    def __init__(self, *, self_heal: bool = True, **validation_options: object) -> None:
        self.self_heal = self_heal
        self.validation_options = validation_options
        self.last_result: Optional[ContractResult] = None

    def validate(self, _definition: RuntimeDefinition) -> bool:
        self.last_result = validate_base_runtime(**self.validation_options)
        if not self.last_result.passed and self.self_heal:
            # Self-heal the one prerequisite the Studio can provision itself: the isolated
            # inference venv (numpy+cv2+dx_engine, the `app.python` check). On a fresh pull or a
            # mixed/partial runtime install the venv may not exist yet, so build it once and
            # re-validate — activation then succeeds without a manual "run Setup, relaunch"
            # dance. gst.*/postprocess failures need real build/install steps and are left to
            # surface as-is. ensure_inference_venv is idempotent (fast no-op once satisfied).
            failed = {c.check_id for c in self.last_result.checks if not c.passed}
            if "app.python" in failed:
                try:
                    from shared.runtime import ensure_inference_venv
                    ensure_inference_venv()
                except Exception:
                    pass
                self.last_result = validate_base_runtime(**self.validation_options)
        return self.last_result.passed
