"""DX App model registry contracts."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_models_exposes_configured_build_dir():
    from dx_app.core import config, models

    assert models.BUILD_DIR == config.BUILD_DIR


def _make_executable(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    path.chmod(0o755)


def _configure_minimal_example(
    monkeypatch, tmp_path, *, language="cpp", model_exists=True, python_runtime=True
):
    import models

    name = "demo_model"
    category = "classification"
    fake_root = tmp_path / "dx_app_root"
    model_file = "assets/models/demo_model.dxnn"
    example_root = (
        fake_root
        / "src"
        / ("cpp_example" if language == "cpp" else "python_example")
        / category
        / name
    )
    example_root.mkdir(parents=True)
    suffix = ".cpp" if language == "cpp" else ".py"
    (example_root / f"{name}_sync{suffix}").write_text("", encoding="utf-8")
    if model_exists:
        model_path = fake_root / model_file
        model_path.parent.mkdir(parents=True)
        model_path.write_bytes(b"dxnn")

    monkeypatch.setattr(models, "CONFIG_FILE", fake_root / "config" / "test_models.conf")
    monkeypatch.setattr(models, "DX_APP_ROOT", fake_root)
    monkeypatch.setattr(models, "CPP_DIR", fake_root / "src" / "cpp_example")
    monkeypatch.setattr(models, "PY_DIR", fake_root / "src" / "python_example")
    monkeypatch.setattr(models, "BUILD_DIR", fake_root / "bin", raising=False)
    monkeypatch.setattr(models, "_REG", {name: {"category": category, "file": model_file}})
    monkeypatch.setattr(models, "_download_index", lambda: {})
    monkeypatch.setattr(models, "_python_runtime_ready", lambda: python_runtime, raising=False)
    return fake_root, name, category, model_file


def test_get_models_uses_bundled_catalog_when_runtime_conf_is_missing(tmp_path, monkeypatch):
    """Bundled assets must be usable before a ModelZoo download or Compiler deploy writes test_models.conf."""
    import models

    catalog = json.loads((ROOT / "dx_modelzoo" / "data" / "model_catalog.json").read_text(encoding="utf-8"))
    catalog_model = next(model for model in catalog["models"] if model["id"] == "efficientnet_lite0")

    fake_root = tmp_path / "dx_app_root"
    (fake_root / "config").mkdir(parents=True)
    model_path = fake_root / catalog_model["model_file"]
    model_path.parent.mkdir(parents=True)
    model_path.write_bytes(b"dxnn")

    monkeypatch.setattr(models, "CONFIG_FILE", fake_root / "config" / "test_models.conf")
    monkeypatch.setattr(models, "DX_APP_ROOT", fake_root)
    monkeypatch.setattr(models, "CPP_DIR", fake_root / "src" / "cpp_example")
    monkeypatch.setattr(models, "PY_DIR", fake_root / "src" / "python_example")
    monkeypatch.setattr(models, "BUILD_DIR", fake_root / "bin", raising=False)
    monkeypatch.setattr(models, "_REG", models._load_reg())
    _make_executable(fake_root / "bin" / "efficientnet_sync")

    discovered = {model["name"]: model for model in models.get_models()}

    assert discovered["efficientnet"]["model_file"] == catalog_model["model_file"]
    assert discovered["efficientnet"]["model_exists"] is True


def test_get_models_keeps_bundled_catalog_when_runtime_conf_exists(tmp_path, monkeypatch):
    """A compiler/modelzoo-created test_models.conf must not hide bundled sample models."""
    import models

    catalog = json.loads((ROOT / "dx_modelzoo" / "data" / "model_catalog.json").read_text(encoding="utf-8"))
    catalog_model = next(model for model in catalog["models"] if model["id"] == "efficientnet_lite0")

    fake_root = tmp_path / "dx_app_root"
    config_dir = fake_root / "config"
    config_dir.mkdir(parents=True)
    model_path = fake_root / catalog_model["model_file"]
    model_path.parent.mkdir(parents=True)
    model_path.write_bytes(b"dxnn")
    (config_dir / "test_models.conf").write_text(
        "custom_model\tclassification\tassets/models/custom.dxnn\n",
        encoding="utf-8",
    )
    (fake_root / "assets" / "models" / "custom.dxnn").write_bytes(b"dxnn")

    monkeypatch.setattr(models, "CONFIG_FILE", config_dir / "test_models.conf")
    monkeypatch.setattr(models, "DX_APP_ROOT", fake_root)
    monkeypatch.setattr(models, "CPP_DIR", fake_root / "src" / "cpp_example")
    monkeypatch.setattr(models, "PY_DIR", fake_root / "src" / "python_example")
    monkeypatch.setattr(models, "BUILD_DIR", fake_root / "bin", raising=False)
    monkeypatch.setattr(models, "_REG", models._load_reg())
    _make_executable(fake_root / "bin" / "efficientnet_sync")

    discovered = {model["name"]: model for model in models.get_models()}

    assert discovered["efficientnet"]["model_file"] == catalog_model["model_file"]
    assert "custom_model" in discovered


def test_get_models_excludes_example_when_required_dxnn_is_missing(tmp_path, monkeypatch):
    _, name, _, _ = _configure_minimal_example(
        monkeypatch, tmp_path, model_exists=False
    )

    assert name not in {model["name"] for model in __import__("models").get_models()}


def test_get_models_excludes_cpp_source_without_an_executable_runner(tmp_path, monkeypatch):
    _, name, _, _ = _configure_minimal_example(monkeypatch, tmp_path, language="cpp")

    assert name not in {model["name"] for model in __import__("models").get_models()}


def test_get_models_uses_executable_cpp_fallback_when_direct_runner_is_not_executable(
    tmp_path, monkeypatch
):
    root, name, _, _ = _configure_minimal_example(monkeypatch, tmp_path, language="cpp")
    direct_runner = root / "bin" / f"{name}_sync"
    _make_executable(direct_runner)
    direct_runner.chmod(0o644)
    _make_executable(root / "bin" / "mobilenetv2_sync")

    assert name in {model["name"] for model in __import__("models").get_models()}


def test_get_models_excludes_cpp_source_when_direct_and_fallback_runners_are_not_executable(
    tmp_path, monkeypatch
):
    root, name, _, _ = _configure_minimal_example(monkeypatch, tmp_path, language="cpp")
    for runner_name in (name, "mobilenetv2"):
        runner = root / "bin" / f"{runner_name}_sync"
        _make_executable(runner)
        runner.chmod(0o644)

    assert name not in {model["name"] for model in __import__("models").get_models()}


def test_get_models_excludes_python_source_when_studio_runtime_is_unavailable(
    tmp_path, monkeypatch
):
    _, name, _, _ = _configure_minimal_example(
        monkeypatch, tmp_path, language="python", python_runtime=False
    )

    assert name not in {model["name"] for model in __import__("models").get_models()}


def test_get_catalog_keeps_uninstalled_modelzoo_entry(tmp_path, monkeypatch):
    import models

    catalog = json.loads(
        (ROOT / "dx_modelzoo" / "data" / "model_catalog.json").read_text(
            encoding="utf-8"
        )
    )
    catalog_model = next(
        model for model in catalog["models"] if model["id"] == "efficientnet_lite0"
    )
    fake_root = tmp_path / "dx_app_root"
    source_dir = fake_root / "src" / "cpp_example" / "classification" / "efficientnet"
    source_dir.mkdir(parents=True)
    (source_dir / "efficientnet_sync.cpp").write_text("", encoding="utf-8")

    monkeypatch.setattr(models, "CONFIG_FILE", fake_root / "config" / "test_models.conf")
    monkeypatch.setattr(models, "DX_APP_ROOT", fake_root)
    monkeypatch.setattr(models, "CPP_DIR", fake_root / "src" / "cpp_example")
    monkeypatch.setattr(models, "PY_DIR", fake_root / "src" / "python_example")
    monkeypatch.setattr(models, "BUILD_DIR", fake_root / "bin", raising=False)
    monkeypatch.setattr(models, "_REG", models._load_reg())
    monkeypatch.setattr(models, "_download_index", lambda: {})

    entry = next(
        model
        for model in models.get_catalog()
        if model["model_file"] == catalog_model["model_file"]
    )

    assert entry["model_exists"] is False
    assert entry["dxnn_url"]
