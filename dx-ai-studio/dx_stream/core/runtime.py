"""Runtime contract adapter for dx-runtime/dx_stream."""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
import json
from pathlib import Path


CONFIG_FILENAMES = ("preprocess_config.json", "inference_config.json", "postprocess_config.json")


@dataclass(frozen=True)
class ModelManifest:
    source: str
    models: list[str]
    version: str | None = None
    error: str | None = None


def load_model_manifest(runtime_root: Path) -> ModelManifest:
    manifest_path = runtime_root / "model_list.json"
    if not manifest_path.exists():
        return ModelManifest(source="fallback", models=[])
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        models = data.get("models", [])
        if not isinstance(models, list) or not all(isinstance(m, str) for m in models):
            return ModelManifest(source="manifest", models=[], version=data.get("version"), error="Invalid model_list.json models")
        return ModelManifest(source="manifest", models=list(models), version=data.get("version"))
    except (OSError, json.JSONDecodeError) as exc:
        return ModelManifest(source="manifest", models=[], error=str(exc))


def runtime_src(runtime_root: Path) -> Path:
    return runtime_root / "dx_stream"


def configs_dir(runtime_root: Path) -> Path:
    return runtime_src(runtime_root) / "configs"


def pipelines_dir(runtime_root: Path) -> Path:
    return runtime_src(runtime_root) / "pipelines"


def samples_dir(runtime_root: Path) -> Path:
    return runtime_src(runtime_root) / "samples"


def models_dir(runtime_root: Path) -> Path:
    return samples_dir(runtime_root) / "models"


def videos_dir(runtime_root: Path) -> Path:
    return samples_dir(runtime_root) / "videos"


def required_config_files(runtime_root: Path, config_dir_name: str) -> list[Path]:
    base = configs_dir(runtime_root) / config_dir_name
    return [base / name for name in CONFIG_FILENAMES]


def tracker_config_file(runtime_root: Path) -> Path:
    return configs_dir(runtime_root) / "tracker_config.json"


def pipeline_script(runtime_root: Path, relative_path: str | Path) -> Path:
    return pipelines_dir(runtime_root) / relative_path


def missing_paths(paths: Sequence[Path]) -> list[Path]:
    return [p for p in paths if not p.exists()]


def build_step_command(runtime_root: Path, *, clean: bool = False, debug: bool = False) -> list[str]:
    cmd = ["bash", str(runtime_root / "build.sh")]
    if clean:
        cmd.append("--clean")
    cmd.append("--type=Debug" if debug else "--type=Release")
    return cmd


def setup_assets_command(runtime_root: Path) -> list[str]:
    return ["bash", str(runtime_root / "setup.sh")]


def setup_single_model_command(runtime_root: Path, model_name: str) -> list[str]:
    return ["bash", str(runtime_root / "setup.sh"), f"--model={model_name}"]
