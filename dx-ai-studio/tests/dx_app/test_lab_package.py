"""RED contracts for portable Lab Composer package exports."""

import json
import subprocess
from pathlib import Path
import zipfile

import pytest

from dx_app.core.lab_package import build_workflow_package


def _workflow(model_file="assets/models/model.dxnn", asset_path="sample/img/sample.jpg"):
    return {
        "schema_version": 1,
        "id": "workflow_package_test",
        "model": {
            "name": "model",
            "category": "classification",
            "model_file": model_file,
            "language": "cpp",
            "variant": "sync",
        },
        "input": {"kind": "image", "path": asset_path},
        "nodes": [
            {"id": "input", "kind": "input", "enabled": True, "params": {}},
            {"id": "preprocess", "kind": "builtin_preprocess", "enabled": True, "params": {}},
            {"id": "inference", "kind": "inference", "enabled": True, "params": {}},
            {"id": "postprocess", "kind": "builtin_postprocess", "enabled": True, "params": {}},
            {"id": "visualize", "kind": "builtin_visualizer", "enabled": True, "params": {}},
        ],
        "plugins": [],
        "execution": {"save_output": True},
    }


def _source_tree(tmp_path):
    source = tmp_path / "studio-source"
    model = source / "assets" / "models" / "model.dxnn"
    asset = source / "sample" / "img" / "sample.jpg"
    model.parent.mkdir(parents=True)
    asset.parent.mkdir(parents=True)
    model.write_bytes(b"DXNN model bytes")
    asset.write_bytes(b"JPEG sample bytes")
    runner = source / "src" / "python_example" / "classification" / "model" / "model_sync.py"
    runner.parent.mkdir(parents=True)
    runner.write_text(
        "import argparse\n"
        "parser = argparse.ArgumentParser()\n"
        "parser.add_argument('--model', required=True)\n"
        "parser.add_argument('--image')\n"
        "parser.add_argument('--video')\n"
        "parser.add_argument('--no-display', action='store_true')\n"
        "parser.parse_args()\n",
        encoding="utf-8",
    )
    common = source / "src" / "python_example" / "common" / "runtime_support.py"
    common.parent.mkdir(parents=True)
    common.write_text("VALUE = 'bundled common support'\n", encoding="utf-8")
    return source, model, asset


def test_run_package_contains_manifest_model_asset_and_launcher(tmp_path):
    source, model, asset = _source_tree(tmp_path)

    result = build_workflow_package(
        workflow=_workflow(),
        package_type="run",
        source_root=source,
        output_root=tmp_path / "output",
    )

    package = result["package_dir"]
    assert (package / "workflow.json").is_file()
    assert (package / "models" / "model.dxnn").is_file()
    assert (package / "assets" / "sample.jpg").is_file()
    assert (package / "setup.sh").is_file()
    assert (package / "run.sh").is_file()
    assert (package / "verify.py").is_file()
    assert (package / "README.md").is_file()
    assert (package / "runtime" / "python" / "classification" / "model" / "model_sync.py").is_file()
    assert (package / "runtime" / "python" / "common" / "runtime_support.py").is_file()
    assert (package / "models" / "model.dxnn").read_bytes() == model.read_bytes()
    assert (package / "assets" / "sample.jpg").read_bytes() == asset.read_bytes()

    manifest = json.loads((package / "workflow.json").read_text(encoding="utf-8"))
    assert manifest["model"]["model_file"] == "models/model.dxnn"
    assert manifest["input"]["path"] == "assets/sample.jpg"
    assert not Path(manifest["model"]["model_file"]).is_absolute()
    assert not Path(manifest["input"]["path"]).is_absolute()
    assert all(not entry.is_symlink() for entry in package.rglob("*"))


def test_package_output_is_scoped_under_lab_packages(tmp_path):
    source, _, _ = _source_tree(tmp_path)
    output_root = tmp_path / "output"

    result = build_workflow_package(
        workflow=_workflow(),
        package_type="run",
        source_root=source,
        output_root=output_root,
    )

    assert result["package_dir"].parent == output_root / "lab_packages"
    assert result["archive_path"].parent == output_root / "lab_packages"


def test_package_rejects_symlinked_lab_package_namespace(tmp_path):
    source, _, _ = _source_tree(tmp_path)
    output_root = tmp_path / "output"
    output_root.mkdir()
    external = tmp_path / "external-packages"
    external.mkdir()
    try:
        (output_root / "lab_packages").symlink_to(external, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"Symlinks are unavailable in this test environment: {exc}")

    with pytest.raises(ValueError, match="unsafe package output path"):
        build_workflow_package(
            workflow=_workflow(),
            package_type="run",
            source_root=source,
            output_root=output_root,
        )


def test_run_package_bundles_exact_runner_and_help_works_from_copy_out(tmp_path):
    source, _, _ = _source_tree(tmp_path)

    result = build_workflow_package(
        workflow=_workflow(),
        package_type="run",
        source_root=source,
        output_root=tmp_path / "output",
    )

    manifest = json.loads((result["package_dir"] / "workflow.json").read_text(encoding="utf-8"))
    runner = manifest["packaged_runner"]
    assert runner["language"] == "python"
    assert runner["path"] == "runtime/python/classification/model/model_sync.py"
    completed = subprocess.run(
        ["sh", "run.sh", "--help"],
        cwd=result["copy_out_dir"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout
    assert "Usage: run.sh" in completed.stdout


def test_run_package_bundles_selected_cpp_postprocess_runner_and_merged_config(tmp_path):
    source, _, _ = _source_tree(tmp_path)
    model_dir = source / "src" / "python_example" / "classification" / "model"
    (model_dir / "model_sync_cpp_postprocess.py").write_text(
        "import argparse\n"
        "parser = argparse.ArgumentParser()\n"
        "parser.add_argument('--model', required=True)\n"
        "parser.add_argument('--config')\n"
        "parser.add_argument('--image')\n"
        "parser.add_argument('--video')\n"
        "parser.add_argument('--no-display', action='store_true')\n"
        "parser.parse_args()\n",
        encoding="utf-8",
    )
    (model_dir / "config.json").write_text(
        json.dumps({"top_k": 5, "model_default": "preserved"}), encoding="utf-8"
    )
    workflow = _workflow()
    workflow["model"].update({"language": "python", "variant": "sync_cpp_postprocess"})
    workflow["execution"]["config_overrides"] = {"top_k": 3}

    result = build_workflow_package(
        workflow=workflow,
        package_type="run",
        source_root=source,
        output_root=tmp_path / "output",
    )

    package = result["package_dir"]
    manifest = json.loads((package / "workflow.json").read_text(encoding="utf-8"))
    assert manifest["packaged_runner"]["path"] == (
        "runtime/python/classification/model/model_sync_cpp_postprocess.py"
    )
    assert (package / manifest["packaged_runner"]["path"]).is_file()
    assert json.loads((package / "config.json").read_text(encoding="utf-8")) == {
        "top_k": 3,
        "model_default": "preserved",
    }
    run_script = (package / "run.sh").read_text(encoding="utf-8")
    assert "model_sync_cpp_postprocess.py" in run_script
    assert '--config "$SCRIPT_DIR/config.json"' in run_script


def test_run_package_rejects_missing_exact_runner(tmp_path):
    source, _, _ = _source_tree(tmp_path)
    for path in (source / "src").rglob("model_sync.py"):
        path.unlink()

    with pytest.raises(ValueError, match="exact runner source is unavailable"):
        build_workflow_package(
            workflow=_workflow(),
            package_type="run",
            source_root=source,
            output_root=tmp_path / "output",
        )


def test_package_rejects_source_symlink_that_escapes_studio_root(tmp_path):
    source, model, _ = _source_tree(tmp_path)
    external = tmp_path / "outside.dxnn"
    external.write_bytes(b"not packageable")
    model.unlink()
    try:
        model.symlink_to(external)
    except OSError as exc:
        pytest.skip(f"Symlinks are unavailable in this test environment: {exc}")

    with pytest.raises(ValueError, match="symlink|outside|unsafe"):
        build_workflow_package(
            workflow=_workflow(),
            package_type="run",
            source_root=source,
            output_root=tmp_path / "output",
        )


def test_package_rejects_absolute_studio_paths_in_workflow(tmp_path):
    source, model, _ = _source_tree(tmp_path)

    with pytest.raises(ValueError, match="absolute|relative|unsafe"):
        build_workflow_package(
            workflow=_workflow(model_file=str(model)),
            package_type="run",
            source_root=source,
            output_root=tmp_path / "output",
        )


def test_recipe_contains_identity_without_model_bytes_or_studio_paths(tmp_path):
    source, _, _ = _source_tree(tmp_path)

    result = build_workflow_package(
        workflow=_workflow(),
        package_type="recipe",
        source_root=source,
        output_root=tmp_path / "output",
    )

    recipe = result["package_dir"] / "workflow.recipe.json"
    data = json.loads(recipe.read_text(encoding="utf-8"))
    assert data["model"] == {
        "name": "model",
        "category": "classification",
        "language": "cpp",
        "variant": "sync",
    }
    assert data["input"] == {"kind": "image"}
    assert "model_file" not in recipe.read_text(encoding="utf-8")
    assert '"path"' not in recipe.read_text(encoding="utf-8")
    assert '"asset"' not in recipe.read_text(encoding="utf-8")
    assert "model.dxnn" not in {path.name for path in result["package_dir"].rglob("*") if path.is_file()}
    assert b"DXNN model bytes" not in recipe.read_bytes()
    assert str(source) not in recipe.read_text(encoding="utf-8")


def test_package_builder_reports_successful_copy_out_verification(tmp_path):
    source, _, _ = _source_tree(tmp_path)

    result = build_workflow_package(
        workflow=_workflow(),
        package_type="run",
        source_root=source,
        output_root=tmp_path / "output",
    )

    assert result["copy_out_verified"] is True
    assert result["copy_out_dir"].is_dir()
    assert source not in result["copy_out_dir"].parents
    archive = result["archive_path"]
    assert archive.is_file()
    assert result["download_name"] == archive.name
    with zipfile.ZipFile(archive) as bundle:
        assert {
            "workflow.json",
            "models/model.dxnn",
            "assets/sample.jpg",
            "run.sh",
            "verify.py",
        } <= set(bundle.namelist())


def test_developer_package_copies_declared_python_plugin_without_mutating_workflow(tmp_path):
    source, _, _ = _source_tree(tmp_path)
    plugin_root = tmp_path / "plugin-workspace"
    plugin = plugin_root / "plugins" / "preprocess" / "normalize.py"
    plugin.parent.mkdir(parents=True)
    plugin.write_text(
        "def preprocess(image, context):\n"
        "    return image\n",
        encoding="utf-8",
    )
    workflow = _workflow()
    workflow["plugins"] = [{
        "id": "normalize",
        "stage": "preprocess",
        "language": "python",
        "enabled": True,
        "entrypoint": "plugins/preprocess/normalize.py",
    }, {
        "id": "disabled-normalize",
        "stage": "preprocess",
        "language": "python",
        "enabled": False,
        "entrypoint": "plugins/preprocess/disabled_normalize.py",
    }]
    (plugin.parent / "disabled_normalize.py").write_text("VALUE = 'disabled plugin'\n", encoding="utf-8")
    original = json.loads(json.dumps(workflow))

    result = build_workflow_package(
        workflow=workflow,
        package_type="developer",
        source_root=source,
        output_root=tmp_path / "output",
        plugin_root=plugin_root,
    )

    package = result["package_dir"]
    assert workflow == original
    assert (package / "plugins" / "preprocess" / "normalize.py").is_file()
    assert (package / "plugins" / "preprocess" / "disabled_normalize.py").is_file()
    assert (package / "plugins" / "plugin_loader.py").is_file()
    manifest = json.loads((package / "workflow.json").read_text(encoding="utf-8"))
    assert manifest["plugins"][0]["entrypoint"] == "plugins/preprocess/normalize.py"
    assert manifest["plugins"][1]["entrypoint"] == "plugins/preprocess/disabled_normalize.py"
    recipe = json.loads((package / "workflow.recipe.json").read_text(encoding="utf-8"))
    assert "model_file" not in recipe["model"]
    assert "path" not in recipe["input"]
    assert "entrypoint" not in recipe["plugins"][0]

    loader_spec = __import__("importlib.util").util.spec_from_file_location(
        "package_plugin_loader", package / "plugins" / "plugin_loader.py"
    )
    loader = __import__("importlib.util").util.module_from_spec(loader_spec)
    loader_spec.loader.exec_module(loader)
    assert loader.load_plugin("plugins/preprocess/normalize.py").preprocess("image", {}) == "image"


def test_run_package_copies_enabled_and_disabled_plugins(tmp_path):
    source, _, _ = _source_tree(tmp_path)
    plugin_root = tmp_path / "plugin-workspace"
    for name in ("enabled.py", "disabled.py"):
        path = plugin_root / "plugins" / "postprocess" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("def postprocess(result, context):\n    return result\n", encoding="utf-8")
    workflow = _workflow()
    workflow["plugins"] = [
        {"id": "enabled", "stage": "postprocess", "language": "python", "enabled": True,
         "entrypoint": "plugins/postprocess/enabled.py"},
        {"id": "disabled", "stage": "postprocess", "language": "python", "enabled": False,
         "entrypoint": "plugins/postprocess/disabled.py"},
    ]

    result = build_workflow_package(
        workflow=workflow,
        package_type="run",
        source_root=source,
        output_root=tmp_path / "output",
        plugin_root=plugin_root,
    )

    manifest = json.loads((result["package_dir"] / "workflow.json").read_text(encoding="utf-8"))
    assert [plugin["entrypoint"] for plugin in manifest["plugins"]] == [
        "plugins/postprocess/enabled.py", "plugins/postprocess/disabled.py",
    ]
    assert (result["package_dir"] / "plugins" / "postprocess" / "enabled.py").is_file()
    assert (result["package_dir"] / "plugins" / "postprocess" / "disabled.py").is_file()


def test_developer_cpp_plugins_define_and_link_package_target(tmp_path):
    source, _, _ = _source_tree(tmp_path)
    cpp_dir = source / "src" / "cpp_example" / "classification" / "model"
    cpp_dir.mkdir(parents=True)
    (cpp_dir / "model_sync.cpp").write_text("int main() { return 0; }\n", encoding="utf-8")
    (cpp_dir / "CMakeLists.txt").write_text(
        "cmake_minimum_required(VERSION 3.16)\n"
        "project(model_sync)\n"
        "add_executable(model_sync model_sync.cpp)\n",
        encoding="utf-8",
    )
    plugin_root = tmp_path / "plugin-workspace"
    plugin = plugin_root / "plugins" / "postprocess" / "labels.cpp"
    plugin.parent.mkdir(parents=True)
    plugin.write_text("void labels() {}\n", encoding="utf-8")
    workflow = _workflow()
    workflow["plugins"] = [{
        "id": "labels", "stage": "postprocess", "language": "cpp", "enabled": True,
        "entrypoint": "plugins/postprocess/labels.cpp",
    }]

    result = build_workflow_package(
        workflow=workflow,
        package_type="developer",
        source_root=source,
        output_root=tmp_path / "output",
        plugin_root=plugin_root,
    )

    plugin_cmake = (result["package_dir"] / "plugins" / "CMakeLists.txt").read_text(encoding="utf-8")
    runtime_cmake = (result["package_dir"] / "runtime" / "cpp" / "classification" / "model" / "CMakeLists.txt").read_text(encoding="utf-8")
    assert "add_library(dx_app_lab_plugins INTERFACE)" in plugin_cmake
    assert "target_sources(dx_app_lab_plugins INTERFACE" in plugin_cmake
    assert "labels.cpp" in plugin_cmake
    assert "add_subdirectory(${CMAKE_CURRENT_LIST_DIR}/../../../../plugins" in runtime_cmake
    assert "target_link_libraries(model_sync PRIVATE dx_app_lab_plugins)" in runtime_cmake


def test_package_builder_prevents_publication_when_copy_out_verification_fails(tmp_path, monkeypatch):
    from dx_app.core import lab_package

    source, _, _ = _source_tree(tmp_path)
    published = tmp_path / "output"
    calls = []

    def fail_copy_out(*args, **kwargs):
        calls.append((args, kwargs))
        raise RuntimeError("forced copy-out validation failure")

    monkeypatch.setattr(lab_package, "validate_copy_out", fail_copy_out)

    with pytest.raises(RuntimeError, match="forced copy-out validation failure"):
        build_workflow_package(
            workflow=_workflow(),
            package_type="run",
            source_root=source,
            output_root=published,
        )

    assert calls
    assert not list((published / "lab_packages").rglob("*.zip"))
    assert not list((published / "lab_packages").rglob("*.download"))

def test_validation_failure_cleans_temporary_copy_out_directory(tmp_path, monkeypatch):
    """When validate_copy_out raises (e.g. verification script fails), the temporary
    copy-out directory must be cleaned up - not leaked on disk."""
    import tempfile
    from dx_app.core import lab_package

    source, _, _ = _source_tree(tmp_path)
    published = tmp_path / "output"

    created_temps = []
    original_mkdtemp = tempfile.mkdtemp

    def tracking_mkdtemp(**kwargs):
        d = original_mkdtemp(**kwargs)
        created_temps.append(d)
        return d

    monkeypatch.setattr(tempfile, "mkdtemp", tracking_mkdtemp)

    # Make the verify.py inside the package fail so validate_copy_out raises
    original_validate = lab_package.validate_copy_out

    def fail_validate(package_dir, source_root=None):
        # Call real validate but inject a failing verify.py
        from pathlib import Path
        package_dir = Path(package_dir)
        (package_dir / "verify.py").write_text(
            "import sys\nprint('RESULT: FAIL')\nsys.exit(1)\n"
        )
        return original_validate(package_dir, source_root=source_root)

    monkeypatch.setattr(lab_package, "validate_copy_out", fail_validate)

    with pytest.raises(RuntimeError, match="copy-out verification failed"):
        build_workflow_package(
            workflow=_workflow(),
            package_type="run",
            source_root=source,
            output_root=published,
        )

    # The temporary copy-out directory must have been cleaned up
    from pathlib import Path
    for temp_dir in created_temps:
        if "dx-app-lab-copy-out" in temp_dir:
            assert not Path(temp_dir).exists(), (
                f"Temp copy-out dir was leaked: {temp_dir}"
            )
