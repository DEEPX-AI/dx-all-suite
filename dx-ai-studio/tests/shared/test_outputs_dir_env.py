"""DX_STUDIO_OUTPUTS moves the results folder, so E2E tests do not pile images into the user's Outputs."""
from __future__ import annotations


def test_outputs_dir_follows_the_env(tmp_path, monkeypatch):
    from shared import paths
    monkeypatch.setenv("DX_STUDIO_OUTPUTS", str(tmp_path))
    assert paths.outputs_dir("dx_app") == tmp_path / "dx_app"
    assert (tmp_path / "dx_app").is_dir()


def test_outputs_dir_defaults_to_the_studio(monkeypatch):
    from shared import paths
    monkeypatch.delenv("DX_STUDIO_OUTPUTS", raising=False)
    assert paths.outputs_dir() == paths.STUDIO_ROOT / "outputs"


def test_the_e2e_tests_use_a_temporary_outputs_folder():
    from pathlib import Path
    src = (Path(__file__).resolve().parents[1] / "e2e" / "conftest.py").read_text(encoding="utf-8")
    assert 'os.environ["DX_STUDIO_OUTPUTS"]' in src
