"""Studio-owned pre-launch contracts for DX App and DX Stream."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Optional

from shared.runtime_profile import ContractCheck


@dataclass(frozen=True)
class ContractResult:
    checks: tuple[ContractCheck, ...]

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)

    @property
    def first_failure(self) -> Optional[ContractCheck]:
        return next((check for check in self.checks if not check.passed), None)


def _path_check(check_id: str, path: Path, remediation: str) -> ContractCheck:
    return ContractCheck(
        check_id=check_id,
        required=str(path),
        observed="present" if path.is_file() else "missing",
        passed=path.is_file(),
        remediation=remediation,
    )


def _selected_assets(demo: Mapping[str, object]) -> Iterable[str]:
    model = demo.get("model_file") or demo.get("model")
    if isinstance(model, str) and model:
        yield model
    models = demo.get("model_files") or demo.get("models") or ()
    if isinstance(models, (list, tuple)):
        for name in models:
            if isinstance(name, str) and name:
                yield name


def _selected_video_path(videos_root: Path, name: str) -> Path:
    """Resolve a declared sample video even when the bundle uses subdirectories."""
    direct = videos_root / name
    if direct.is_file() or not videos_root.is_dir():
        return direct
    return next((path for path in videos_root.rglob(name) if path.is_file()), direct)


def validate_stream_contract(
    profile: object,
    demo: Mapping[str, object],
    root: Path | None = None,
    *,
    models_dir: Path | None = None,
    videos_dir: Path | None = None,
    configs_dir: Path | None = None,
    pipelines_dir: Path | None = None,
) -> ContractResult:
    """Validate only the selected Stream demo's declared runtime dependencies."""
    if root is None and not all((models_dir, videos_dir, configs_dir)):
        raise ValueError("Stream contract requires a root or explicit asset directories.")
    asset_root = Path(root) if root is not None else None
    models_root = Path(models_dir) if models_dir is not None else asset_root / "models"
    videos_root = Path(videos_dir) if videos_dir is not None else asset_root / "videos"
    configs_root = Path(configs_dir) if configs_dir is not None else asset_root / "configs"
    pipelines_root = (
        Path(pipelines_dir)
        if pipelines_dir is not None
        else (asset_root / "pipelines" if asset_root is not None else configs_root.parent / "pipelines")
    )
    plugin_dir = Path(getattr(profile, "plugin_dir", ""))
    postprocess_dir = Path(getattr(profile, "postprocess_lib_dir", ""))
    checks = [
        _path_check(
            "gst.plugin",
            plugin_dir / "libgstdxstream.so",
            "Install the Studio-declared DX Stream GStreamer plugin.",
        )
    ]
    for model in dict.fromkeys(_selected_assets(demo)):
        checks.append(
            _path_check(
                "asset.selected_model",
                models_root / model,
                "Download or select the model required by this demo.",
            )
        )
    for video in demo.get("required_videos", ()):
        if isinstance(video, str) and video:
            checks.append(
                _path_check(
                    "asset.selected_video",
                    _selected_video_path(videos_root, video),
                    "Download the sample video required by this demo.",
                )
            )
    for config_dir in demo.get("required_configs", ()):
        if isinstance(config_dir, str) and config_dir:
            for config_name in (
                "preprocess_config.json",
                "inference_config.json",
                "postprocess_config.json",
            ):
                checks.append(
                    _path_check(
                        "asset.selected_config",
                        configs_root / config_dir / config_name,
                        "Install the configuration required by this demo.",
                    )
                )
    for required_file in demo.get("required_files", ()):
        if isinstance(required_file, str) and required_file:
            checks.append(
                _path_check(
                    "asset.selected_config",
                    configs_root / required_file,
                    "Install the configuration required by this demo.",
                )
            )
    runtime_script = demo.get("runtime_script")
    if isinstance(runtime_script, str) and runtime_script:
        checks.append(
            _path_check(
                "asset.selected_runtime_script",
                pipelines_root / runtime_script,
                "Install the runtime script required by this demo.",
            )
        )
    postproc = demo.get("postproc_lib")
    if isinstance(postproc, str) and postproc:
        postproc_path = Path(postproc)
        if not postproc_path.is_absolute():
            postproc_path = postprocess_dir / postproc_path
        checks.append(
            _path_check(
                "gst.postprocess_library",
                postproc_path,
                "Install the postprocess library required by this demo.",
            )
        )
    return ContractResult(tuple(checks))


def validate_app_contract(
    profile: object,
    model_path: Path,
    media_path: Path,
    executable_path: Path,
) -> ContractResult:
    """Validate a selected DX App executable and its exact model/input pair."""
    interpreter = Path(getattr(profile, "python_executable", ""))
    checks = (
        _path_check(
            "app.python",
            interpreter,
            "Repair the Studio-owned inference environment.",
        ),
        _path_check(
            "asset.selected_model",
            Path(model_path),
            "Download or select the requested DXNN model.",
        ),
        _path_check(
            "asset.selected_media",
            Path(media_path),
            "Choose an existing input image or video.",
        ),
        _path_check(
            "app.executable",
            Path(executable_path),
            "Build or select the requested DX App runner.",
        ),
    )
    return ContractResult(checks)