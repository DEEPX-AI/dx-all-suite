"""Portable Lab Composer workflow package creation.

The builder deliberately depends only on the standard library. Generated packages
likewise have no Studio import or suite-relative dependency.
"""

from __future__ import annotations

import copy
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
import zipfile
from pathlib import Path, PurePosixPath

from dx_app.core.run_config import RUN_TUNABLE_KEYS


_PACKAGE_TYPES = {"run", "developer", "recipe"}
_WORKFLOW_ID = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,127}$")


def _require_workflow_id(workflow: dict) -> str:
    workflow_id = workflow.get("id") if isinstance(workflow, dict) else None
    if not isinstance(workflow_id, str) or not _WORKFLOW_ID.fullmatch(workflow_id):
        raise ValueError("unsafe workflow id")
    return workflow_id


def _relative_path(value: object, label: str) -> PurePosixPath:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty relative path")
    if "\\" in value:
        raise ValueError(f"unsafe {label}: use a relative POSIX path")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or path == PurePosixPath("."):
        raise ValueError(f"unsafe {label}: absolute or traversal path")
    return path


def _is_under(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _safe_source_file(source_root: Path, relative: object, label: str) -> Path:
    """Resolve one source file without allowing an escaping symlink chain."""
    path = _relative_path(relative, label)
    candidate = source_root.joinpath(*path.parts)
    current = source_root
    for part in path.parts:
        current = current / part
        if current.is_symlink():
            resolved_link = current.resolve(strict=False)
            if not _is_under(resolved_link, source_root):
                raise ValueError(f"unsafe {label}: symlink resolves outside source root")
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise ValueError(f"{label} not found") from exc
    if not _is_under(resolved, source_root) or not resolved.is_file():
        raise ValueError(f"unsafe {label}")
    return resolved


def _safe_destination(package_dir: Path, relative: PurePosixPath) -> Path:
    destination = package_dir.joinpath(*relative.parts)
    if not _is_under(destination.resolve(strict=False), package_dir):
        raise ValueError("unsafe package output path")
    return destination


def _copy_regular(source: Path, destination: Path) -> None:
    if source.is_symlink() or not source.is_file():
        raise ValueError("unsafe source file")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    os.chmod(destination, source.stat().st_mode & 0o777)
    if destination.is_symlink() or not destination.is_file():
        raise ValueError("package copy is not a regular file")


def _copy_tree_regular(source: Path, destination: Path) -> None:
    """Copy a directory while rejecting every source or output symlink."""
    if source.is_symlink() or not source.is_dir():
        raise ValueError("unsafe source directory")
    for path in source.rglob("*"):
        if path.is_symlink():
            raise ValueError("unsafe source directory symlink")
        target = destination / path.relative_to(source)
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif path.is_file():
            _copy_regular(path, target)
        else:
            raise ValueError("unsafe source directory entry")


def _model_identifier(model: dict) -> tuple[str, str]:
    category = model.get("category")
    name = model.get("name")
    if not isinstance(category, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", category):
        raise ValueError("workflow model category is invalid")
    if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", name):
        raise ValueError("workflow model name is invalid")
    return category, name


def _runner_source(
    source_root: Path, category: str, model: str, language: str, variant: str
) -> Path | None:
    if language == "python":
        if variant not in {"sync", "sync_cpp_postprocess"}:
            return None
        relative = PurePosixPath("src/python_example") / category / model / f"{model}_{variant}.py"
    else:
        if variant != "sync":
            return None
        relative = PurePosixPath("src/cpp_example") / category / model / f"{model}_sync.cpp"
    try:
        return _safe_source_file(source_root, relative.as_posix(), "exact runner source")
    except ValueError:
        return None


def _copy_extracted_runner(extracted_root: Path, runner_name: str, destination: Path) -> bool:
    candidates = [path for path in extracted_root.rglob(runner_name) if path.is_file()]
    if len(candidates) != 1:
        return False
    _copy_tree_regular(candidates[0].parent, destination)
    common = extracted_root / "common"
    if common.is_dir():
        _copy_tree_regular(common, destination.parent.parent / "common")
    return True


def _bundle_exact_runner(package_dir: Path, source_root: Path, model: dict) -> dict:
    category, name = _model_identifier(model)
    requested = model.get("language")
    requested = "python" if requested in {"python", "py"} else "cpp" if requested == "cpp" else "python"
    requested_variant = model.get("variant", "sync")
    if not isinstance(requested_variant, str):
        raise ValueError("workflow model variant is invalid")
    if requested == "cpp" and requested_variant != "sync":
        raise ValueError("workflow C++ runner variant is invalid")
    candidates = [(requested, requested_variant)]
    if requested != "python":
        candidates.append(("python", "sync"))

    selected = next(
        (
            (language, variant, _runner_source(source_root, category, name, language, variant))
            for language, variant in candidates
            if _runner_source(source_root, category, name, language, variant)
        ),
        None,
    )
    if selected is None:
        raise ValueError(
            f"exact runner source is unavailable for {category}/{name}; expected "
            f"src/{'cpp' if requested == 'cpp' else 'python'}_example/{category}/{name}/{name}_{requested_variant}."
            f"{'cpp' if requested == 'cpp' else 'py'}"
        )
    language, variant, runner_source = selected
    runtime_root = PurePosixPath("runtime") / language / category / name
    destination = _safe_destination(package_dir, runtime_root)
    extractor = source_root / "scripts" / "extract_model_package.sh"
    if extractor.is_file():
        with tempfile.TemporaryDirectory(prefix="dx-app-lab-extract-") as extracted:
            completed = subprocess.run(
                ["bash", str(extractor), f"{category}/{name}", "--lang", "py" if language == "python" else "cpp",
                 "--output-dir", extracted],
                cwd=source_root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            runner_name = runner_source.name
            if completed.returncode != 0 or not _copy_extracted_runner(Path(extracted), runner_name, destination):
                raise ValueError("extract_model_package.sh did not produce the exact requested runner source")
    else:
        _copy_tree_regular(runner_source.parent, destination)
        if language == "python":
            common = source_root / "src" / "python_example" / "common"
            if common.is_dir():
                _copy_tree_regular(common, _safe_destination(package_dir, PurePosixPath("runtime/python/common")))

    runner_relative = runtime_root / runner_source.name
    if language == "cpp" and not (destination / "CMakeLists.txt").is_file():
        raise ValueError("exact C++ runner source lacks CMakeLists.txt")
    return {
        "language": language,
        "variant": variant,
        "path": runner_relative.as_posix(),
        "requested_language": requested,
        "requested_variant": requested_variant,
        "executable": name + "_sync" if language == "cpp" else None,
        "source_dir": runner_source.parent,
    }


def _write_text(package_dir: Path, relative: str, content: str, executable: bool = False) -> Path:
    destination = _safe_destination(package_dir, PurePosixPath(relative))
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")
    if executable:
        destination.chmod(destination.stat().st_mode | 0o111)
    return destination


def _recipe(workflow: dict) -> dict:
    recipe = copy.deepcopy(workflow)
    model = recipe.get("model")
    if isinstance(model, dict):
        model.pop("model_file", None)
    input_data = recipe.get("input")
    if isinstance(input_data, dict):
        input_data.pop("path", None)
        input_data.pop("asset", None)
    plugins = recipe.get("plugins")
    if isinstance(plugins, list):
        for plugin in plugins:
            if isinstance(plugin, dict):
                plugin.pop("entrypoint", None)
    return recipe


def _plugin_source(plugin_root: Path, plugin: dict) -> tuple[Path, PurePosixPath]:
    stage = plugin.get("stage")
    entrypoint = _relative_path(plugin.get("entrypoint"), "plugin entrypoint")
    if stage not in {"preprocess", "postprocess"} or len(entrypoint.parts) < 3:
        raise ValueError("unsafe plugin entrypoint")
    if entrypoint.parts[0] != "plugins" or entrypoint.parts[1] != stage:
        raise ValueError("unsafe plugin entrypoint")
    source = _safe_source_file(plugin_root, entrypoint.as_posix(), "plugin entrypoint")
    target = PurePosixPath("plugins") / stage / source.name
    return source, target


def _copy_plugins(package_dir: Path, workflow: dict, plugin_root: Path | None) -> list[dict]:
    plugins = workflow.get("plugins", [])
    if not isinstance(plugins, list):
        raise ValueError("plugins must be a list")
    declared = [plugin for plugin in plugins if isinstance(plugin, dict)]
    if declared and plugin_root is None:
        raise ValueError("plugin_root is required when workflow declares plugins")

    copied = []
    for plugin in declared:
        source, target = _plugin_source(plugin_root, plugin)
        _copy_regular(source, _safe_destination(package_dir, target))
        packaged = copy.deepcopy(plugin)
        packaged["entrypoint"] = target.as_posix()
        copied.append(packaged)
    return copied


def _write_cpp_plugin_cmake(package_dir: Path, copied_plugins: list[dict], runner: dict) -> None:
    cpp_sources = [plugin["entrypoint"] for plugin in copied_plugins if plugin.get("language") == "cpp"]
    if not cpp_sources or runner["language"] != "cpp":
        return
    source_list = "\n".join(
        f'    "${{CMAKE_CURRENT_LIST_DIR}}/../{source}"' for source in cpp_sources
    )
    _write_text(
        package_dir,
        "plugins/CMakeLists.txt",
        "add_library(dx_app_lab_plugins INTERFACE)\n"
        "target_sources(dx_app_lab_plugins INTERFACE\n" + source_list + "\n)\n"
        "target_include_directories(dx_app_lab_plugins INTERFACE \"${CMAKE_CURRENT_LIST_DIR}\")\n",
    )
    runtime_cmake = _safe_destination(package_dir, PurePosixPath(runner["path"])).parent / "CMakeLists.txt"
    if not runtime_cmake.is_file():
        raise ValueError("exact C++ runner source lacks CMakeLists.txt for plugin integration")
    cmake = runtime_cmake.read_text(encoding="utf-8")
    targets = re.findall(r"add_executable\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)", cmake)
    if not targets:
        raise ValueError("exact C++ runner CMakeLists.txt has no executable target for plugin integration")
    integration = (
        "\nadd_subdirectory(${CMAKE_CURRENT_LIST_DIR}/../../../../plugins "
        "${CMAKE_CURRENT_BINARY_DIR}/dx_app_lab_plugins)\n"
        + "".join(f"target_link_libraries({target} PRIVATE dx_app_lab_plugins)\n" for target in targets)
    )
    runtime_cmake.write_text(cmake.rstrip() + integration, encoding="utf-8")

def _validated_config_overrides(workflow: dict) -> dict:
    execution = workflow.get("execution") if isinstance(workflow, dict) else None
    if not isinstance(execution, dict):
        raise ValueError("workflow execution is invalid")
    overrides = execution.get("config_overrides")
    if overrides is None:
        return {}
    if not isinstance(overrides, dict):
        raise ValueError("workflow config_overrides is invalid")
    clean = {}
    for key, value in overrides.items():
        if (
            key not in RUN_TUNABLE_KEYS
            or isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(float(value))
        ):
            raise ValueError("workflow config_overrides is invalid")
        clean[key] = value
    return clean


def _write_packaged_config(package_dir: Path, runner: dict, workflow: dict) -> str | None:
    overrides = _validated_config_overrides(workflow)
    if not overrides:
        return None
    source_dir = runner.get("source_dir")
    source_config = Path(source_dir) / "config.json" if isinstance(source_dir, Path) else None
    merged = {}
    if source_config is not None and source_config.exists():
        if source_config.is_symlink() or not source_config.is_file():
            raise ValueError("unsafe runner configuration source")
        try:
            loaded = json.loads(source_config.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError("runner configuration is invalid") from exc
        if not isinstance(loaded, dict):
            raise ValueError("runner configuration is invalid")
        merged.update(loaded)
    merged.update(overrides)
    relative = "config.json"
    _write_text(package_dir, relative, json.dumps(merged, indent=2, sort_keys=True) + "\n")
    return relative


def _setup_script(runner: dict) -> str:
    if runner["language"] == "cpp":
        return f"""#!/usr/bin/env sh
set -eu
SCRIPT_DIR=$(CDPATH= cd -- \"$(dirname -- \"$0\")\" && pwd -P)
python3 \"$SCRIPT_DIR/verify.py\"
cmake -S \"$SCRIPT_DIR/{PurePosixPath(runner['path']).parent.as_posix()}\" -B \"$SCRIPT_DIR/build\"
cmake --build \"$SCRIPT_DIR/build\"
"""
    return f"""#!/usr/bin/env sh
set -eu
SCRIPT_DIR=$(CDPATH= cd -- \"$(dirname -- \"$0\")\" && pwd -P)
python3 \"$SCRIPT_DIR/verify.py\"
python3 -m py_compile \"$SCRIPT_DIR/{runner['path']}\"
"""


def _run_script(runner: dict, workflow: dict) -> str:
    input_data = workflow.get("input") if isinstance(workflow.get("input"), dict) else {}
    input_path = input_data.get("path")
    input_flag = "--video" if input_data.get("kind") == "video" else "--image"
    if not isinstance(input_path, str):
        raise ValueError("workflow input path is invalid")
    config_argument = (
        f' --config "$SCRIPT_DIR/{runner["config_path"]}"'
        if isinstance(runner.get("config_path"), str) and runner["config_path"]
        else ""
    )
    if runner["language"] == "cpp":
        return f"""#!/usr/bin/env sh
set -eu
SCRIPT_DIR=$(CDPATH= cd -- \"$(dirname -- \"$0\")\" && pwd -P)
if [ \"${{1:-}}\" = \"--help\" ] || [ \"${{1:-}}\" = \"-h\" ]; then
    printf '%s\\n' 'Usage: run.sh [runner arguments]'
    printf '%s\\n' 'Build first with ./setup.sh, then run the bundled C++ runner.'
    exit 0
fi
python3 \"$SCRIPT_DIR/verify.py\"
RUNNER=\"$SCRIPT_DIR/build/{runner['executable']}\"
if [ ! -x \"$RUNNER\" ]; then
    printf '%s\\n' 'ERROR: C++ runner is not built. Run ./setup.sh with CMake and the DEEPX runtime installed.' >&2
    exit 1
fi
exec \"$RUNNER\" --model \"$SCRIPT_DIR/models/{PurePosixPath(workflow['model']['model_file']).name}\" {input_flag} \"$SCRIPT_DIR/{input_path}\" --no-display{config_argument} \"$@\"
"""
    return f"""#!/usr/bin/env sh
set -eu
SCRIPT_DIR=$(CDPATH= cd -- \"$(dirname -- \"$0\")\" && pwd -P)
if [ \"${{1:-}}\" = \"--help\" ] || [ \"${{1:-}}\" = \"-h\" ]; then
    printf '%s\\n' 'Usage: run.sh [runner arguments]'
    printf '%s\\n' 'Runs the bundled exact Python runner with packaged model and input assets.'
    exit 0
fi
python3 \"$SCRIPT_DIR/verify.py\"
if ! python3 -c 'import dx_engine' >/dev/null 2>&1; then
    printf '%s\\n' 'ERROR: dx_engine is required. Install a compatible DEEPX runtime.' >&2
    exit 1
fi
exec python3 \"$SCRIPT_DIR/{runner['path']}\" --model \"$SCRIPT_DIR/models/{PurePosixPath(workflow['model']['model_file']).name}\" {input_flag} \"$SCRIPT_DIR/{input_path}\" --no-display{config_argument} \"$@\"
"""


def _verify_script() -> str:
    return r'''#!/usr/bin/env python3
"""Validate portable package integrity without importing DX AI Studio."""
import json
import sys
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parent


def fail(message):
    print("RESULT: FAIL - " + message)
    return 1


def safe_file(value, label):
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError(label + " is not a safe relative path")
    relative = PurePosixPath(value)
    if relative.is_absolute() or ".." in relative.parts or relative == PurePosixPath("."):
        raise ValueError(label + " is not a safe relative path")
    candidate = ROOT.joinpath(*relative.parts)
    resolved = candidate.resolve(strict=True)
    resolved.relative_to(ROOT)
    if candidate.is_symlink() or not resolved.is_file():
        raise ValueError(label + " is missing or is not a regular file")


def main():
    for path in ROOT.rglob("*"):
        if path.is_symlink():
            return fail("package contains a symlink")
    manifest_path = ROOT / "workflow.json"
    try:
        workflow = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(workflow, dict):
            raise ValueError("workflow manifest is not an object")
        model = workflow.get("model")
        if not isinstance(model, dict):
            raise ValueError("model is missing")
        safe_file(model.get("model_file"), "model_file")
        input_data = workflow.get("input", {})
        if input_data.get("path"):
            safe_file(input_data["path"], "input path")
        plugins = workflow.get("plugins", [])
        if not isinstance(plugins, list):
            raise ValueError("plugins is not a list")
        for plugin in plugins:
            if isinstance(plugin, dict):
                safe_file(plugin.get("entrypoint"), "plugin entrypoint")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return fail(str(exc))
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''


def _readme(package_type: str, runner: dict) -> str:
    return f"""# Portable Lab Workflow Package

Package type: `{package_type}`

Run `./setup.sh` to prepare the bundled runner. `./run.sh --help` is available without
the DEEPX runtime. Normal execution requires an installed compatible DEEPX runtime.
Bundled runner: `{runner['path']}` ({runner['language']}).
"""


def _create_archive(package_dir: Path, archive_path: Path) -> None:
    with zipfile.ZipFile(archive_path, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(package_dir.rglob("*")):
            if path.is_symlink():
                raise ValueError("package contains symlink")
            if path.is_file():
                archive.write(path, path.relative_to(package_dir).as_posix())


def validate_copy_out(package_dir, source_root=None):
    """Copy a package outside the source tree and execute its integrity checker."""
    package_dir = Path(package_dir).resolve(strict=True)
    source_root = Path(source_root).resolve() if source_root is not None else None
    for entry in package_dir.rglob("*"):
        if entry.is_symlink():
            raise ValueError("copy-out rejected package symlink")

    copy_parent = Path(tempfile.mkdtemp(prefix="dx-app-lab-copy-out-"))
    copy_dir = copy_parent / package_dir.name
    try:
        if source_root is not None and _is_under(copy_dir.resolve(strict=False), source_root):
            raise RuntimeError("copy-out directory is inside source root")
        shutil.copytree(package_dir, copy_dir, symlinks=False)

        forbidden = [str(source_root)] if source_root is not None else []
        for path in copy_dir.rglob("*"):
            if path.is_symlink():
                raise ValueError("copy-out package contains symlink")
            if path.is_file() and path.suffix in {".py", ".sh", ".json", ".md", ".txt"}:
                content = path.read_text(encoding="utf-8", errors="replace")
                if any(reference and reference in content for reference in forbidden):
                    raise ValueError("copy-out package references source root")

        verifier = copy_dir / "verify.py"
        if verifier.exists():
            completed = subprocess.run(
                [sys.executable, str(verifier)], cwd=copy_dir, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
            )
            if completed.returncode != 0 or "RESULT: PASS" not in completed.stdout:
                raise RuntimeError("copy-out verification failed: " + completed.stdout.strip())
        scripts = [script for script in (copy_dir / "setup.sh", copy_dir / "run.sh") if script.is_file()]
        for script in scripts:
            completed = subprocess.run(
                ["sh", "-n", str(script)], cwd=copy_dir, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
            )
            if completed.returncode != 0:
                raise RuntimeError("copy-out script syntax failed: " + completed.stdout.strip())
        if (copy_dir / "run.sh").is_file():
            completed = subprocess.run(
                ["sh", "run.sh", "--help"], cwd=copy_dir, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
            )
            if completed.returncode != 0:
                raise RuntimeError("copy-out runner help failed: " + completed.stdout.strip())
    except Exception:
        shutil.rmtree(copy_parent, ignore_errors=True)
        raise
    return copy_dir


def build_workflow_package(workflow, package_type, source_root, output_root, *, plugin_root=None):
    """Build a self-contained run, developer, or recipe package.

    The caller's workflow is deep-copied before normalization and never mutated.
    """
    if package_type not in _PACKAGE_TYPES:
        raise ValueError("package_type must be run, developer, or recipe")
    if not isinstance(workflow, dict):
        raise ValueError("workflow must be an object")
    workflow_id = _require_workflow_id(workflow)
    source_root = Path(source_root).resolve(strict=True)
    if not source_root.is_dir():
        raise ValueError("source_root must be a directory")
    output_root = Path(output_root).resolve(strict=False)
    output_root.mkdir(parents=True, exist_ok=True)
    if not output_root.is_dir():
        raise ValueError("output_root must be a directory")

    package_root = output_root / "lab_packages"
    if package_root.is_symlink():
        raise ValueError("unsafe package output path")
    package_root.mkdir(mode=0o700, exist_ok=True)
    if package_root.is_symlink() or not package_root.is_dir():
        raise ValueError("unsafe package output path")
    if not _is_under(package_root.resolve(strict=True), output_root):
        raise ValueError("unsafe package output path")
    package_dir = package_root / f"{workflow_id}-{uuid.uuid4().hex}"
    if not _is_under(package_dir.resolve(strict=False), package_root) or package_dir.exists():
        raise ValueError("unsafe package output path")
    package_dir.mkdir(mode=0o700)
    local_workflow = copy.deepcopy(workflow)

    try:
        if package_type == "recipe":
            _write_text(
                package_dir,
                "workflow.recipe.json",
                json.dumps(_recipe(local_workflow), indent=2, sort_keys=True) + "\n",
            )
        else:
            model = local_workflow.get("model")
            if not isinstance(model, dict):
                raise ValueError("workflow model is invalid")
            model_source = _safe_source_file(source_root, model.get("model_file"), "model_file")
            model_target = PurePosixPath("models") / model_source.name
            _copy_regular(model_source, _safe_destination(package_dir, model_target))
            model["model_file"] = model_target.as_posix()

            input_data = local_workflow.get("input")
            if isinstance(input_data, dict) and input_data.get("path"):
                asset_source = _safe_source_file(source_root, input_data["path"], "input path")
                asset_target = PurePosixPath("assets") / asset_source.name
                _copy_regular(asset_source, _safe_destination(package_dir, asset_target))
                input_data["path"] = asset_target.as_posix()

            runner = _bundle_exact_runner(package_dir, source_root, model)
            copied_plugins = _copy_plugins(
                package_dir,
                local_workflow,
                Path(plugin_root).resolve() if plugin_root is not None else None,
            )
            local_workflow["plugins"] = copied_plugins
            config_path = _write_packaged_config(package_dir, runner, local_workflow)
            if config_path:
                runner["config_path"] = config_path
            local_workflow["packaged_runner"] = {
                key: value for key, value in runner.items()
                if value is not None and key != "source_dir"
            }
            _write_text(package_dir, "workflow.json", json.dumps(local_workflow, indent=2, sort_keys=True) + "\n")
            _write_text(package_dir, "setup.sh", _setup_script(runner), executable=True)
            _write_text(package_dir, "run.sh", _run_script(runner, local_workflow), executable=True)
            _write_text(package_dir, "verify.py", _verify_script(), executable=True)
            _write_text(package_dir, "README.md", _readme(package_type, runner))
            if package_type == "developer":
                _write_text(
                    package_dir,
                    "workflow.recipe.json",
                    json.dumps(_recipe(local_workflow), indent=2, sort_keys=True) + "\n",
                )
                _write_cpp_plugin_cmake(package_dir, copied_plugins, runner)
                python_plugins = [plugin["entrypoint"] for plugin in copied_plugins if plugin.get("language") == "python"]
                if python_plugins:
                    _write_text(
                        package_dir,
                        "plugins/plugin_loader.py",
                        "import importlib.util\nfrom pathlib import Path\n\ndef load_plugin(relative_path):\n    path = Path(__file__).resolve().parent.parent / relative_path\n    spec = importlib.util.spec_from_file_location(path.stem, path)\n    module = importlib.util.module_from_spec(spec)\n    spec.loader.exec_module(module)\n    return module\n",
                    )

        copy_out_dir = validate_copy_out(package_dir, source_root=source_root)
        archive_path = package_root / f"{package_dir.name}.zip"
        _create_archive(package_dir, archive_path)
    except Exception:
        shutil.rmtree(package_dir, ignore_errors=True)
        archive_path = package_root / f"{package_dir.name}.zip"
        archive_path.unlink(missing_ok=True)
        if "copy_out_dir" in dir() and copy_out_dir is not None:
            shutil.rmtree(copy_out_dir.parent, ignore_errors=True)
        raise

    return {
        "package_dir": package_dir,
        "archive_path": archive_path,
        "download_name": archive_path.name,
        "copy_out_dir": copy_out_dir,
        "copy_out_verified": True,
    }
