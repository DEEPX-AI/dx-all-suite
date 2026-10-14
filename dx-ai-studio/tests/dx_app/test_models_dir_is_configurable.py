"""Where models are installed must be configurable.

Two reasons:

1. **Product** — models are large (a single .dxnn can be 85 MB), and keeping them on
   another disk is a natural request.

2. **Test determinism** — the dx_app landing model table renders differently
   depending on **what is installed locally**: models.js's `dl = !!runnable` turns on
   the C++/PYTHON/MODE columns and adds a Graph button to ACTIONS only for installed
   models. Five columns change width, the whole table reflows, and visual baselines
   drift by up to 22%. The cause is not the UI but tests capturing an uncontrolled
   input, the developer's filesystem.

   The repo already handles the same problem for dx_monitor: `tests/server_helpers.py`
   sets `DX_MONITOR_SKIP_HARDWARE_INIT=1` to turn off real hardware reads. dx_app's
   installed models are the same kind of input.

No test flag goes into production code: the **path is configurable** and the tests
use that setting — the same result, and a better product.
"""
from __future__ import annotations

import importlib
import os
from pathlib import Path

import pytest

ENV = "DX_APP_MODELS_DIR"


@pytest.fixture()
def reloaded(monkeypatch):
    """Reload config/models under the given environment."""

    def _load(models_dir: str | None):
        if models_dir is None:
            monkeypatch.delenv(ENV, raising=False)
        else:
            monkeypatch.setenv(ENV, models_dir)
        import dx_app.core.config as config

        importlib.reload(config)
        import dx_app.core.models as models

        importlib.reload(models)
        return config, models

    yield _load
    # Put the environment back before reloading: monkeypatch's own teardown runs after this one, so reloading first
    # would leave config.MODELS_DIR on the last test's (deleted) tmp dir and every later test would see no models.
    monkeypatch.undo()
    for name in ("dx_app.core.config", "dx_app.core.models"):
        import sys

        if name in sys.modules:
            importlib.reload(sys.modules[name])


def test_without_the_env_the_default_location_is_unchanged(reloaded):
    config, _ = reloaded(None)
    assert config.MODELS_DIR == config.ASSETS_DIR / "models"


def test_the_env_moves_the_models_directory(reloaded, tmp_path):
    config, _ = reloaded(str(tmp_path))
    assert config.MODELS_DIR == tmp_path


def test_a_model_is_not_installed_when_the_directory_is_empty(reloaded, tmp_path):
    """The core of visual determinism — the table must look empty whatever is really installed."""
    _, models = reloaded(str(tmp_path))
    assert models._required_dxnn_exists("assets/models/espcn-x4_17x17.dxnn") is False


def test_a_model_is_installed_when_it_sits_in_the_configured_directory(reloaded, tmp_path):
    (tmp_path / "espcn-x4_17x17.dxnn").write_bytes(b"not a real model")
    _, models = reloaded(str(tmp_path))
    assert models._required_dxnn_exists("assets/models/espcn-x4_17x17.dxnn") is True


def test_chip_subdirectories_follow_the_configured_root(reloaded, tmp_path):
    """q-pro / q-master live **under** the models directory and must move with it."""
    (tmp_path / "q-pro").mkdir()
    (tmp_path / "q-pro" / "x.dxnn").write_bytes(b"x")
    _, models = reloaded(str(tmp_path))
    assert models._required_dxnn_exists("assets/models/q-pro/x.dxnn") is True


def test_paths_outside_the_models_tree_are_untouched(reloaded, tmp_path):
    """This setting moves **only the models directory**.

    assets/videos and sample/ stay relative to DX_APP_ROOT. The function checks
    existence only and ignores the extension, so a real sample file is True;
    what matters is **where it resolves**, not whether it exists.
    """
    config, _ = reloaded(str(tmp_path))
    assert config.ASSETS_DIR == config.DX_APP_ROOT / "assets"
    assert config.resolve_model_path("assets/videos/x.mp4") == \
        config.DX_APP_ROOT / "assets" / "videos" / "x.mp4"
    assert config.resolve_model_path("sample/img/sample_dog.jpg") == \
        config.DX_APP_ROOT / "sample" / "img" / "sample_dog.jpg"
    # and model paths follow the setting — the same function must tell the two apart.
    assert config.resolve_model_path("assets/models/x.dxnn") == tmp_path / "x.dxnn"
