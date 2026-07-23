"""DX App model registry contracts."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


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
    monkeypatch.setattr(models, "_REG", models._load_reg())

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
    monkeypatch.setattr(models, "_REG", models._load_reg())

    discovered = {model["name"]: model for model in models.get_models()}

    assert discovered["efficientnet"]["model_file"] == catalog_model["model_file"]
    assert "custom_model" in discovered
