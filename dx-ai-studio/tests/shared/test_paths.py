import importlib
from pathlib import Path

def test_roots_resolve(monkeypatch):
    monkeypatch.delenv("DX_APP_ROOT", raising=False)
    import shared.paths as p; importlib.reload(p)
    assert p.STUDIO_ROOT.name == "dx-ai-studio"
    assert p.SUITE_ROOT == p.STUDIO_ROOT.parent
    assert p.DX_APP_ROOT == p.SUITE_ROOT / "dx-runtime" / "dx_app"

def test_env_override(monkeypatch, tmp_path):
    monkeypatch.setenv("DX_APP_ROOT", str(tmp_path))
    import shared.paths as p; importlib.reload(p)
    assert p.DX_APP_ROOT == tmp_path

def test_is_safe_path(tmp_path):
    import shared.paths as p
    inside = tmp_path / "a" / "b.txt"; inside.parent.mkdir(parents=True); inside.write_text("x")
    assert p.is_safe_path(inside, [tmp_path]) is True
    assert p.is_safe_path(Path("/etc/passwd"), [tmp_path]) is False

def test_outputs_dir(tmp_path, monkeypatch):
    import shared.paths as p
    d = p.outputs_dir("dx_app")
    assert d == p.STUDIO_ROOT / "outputs" / "dx_app" and d.is_dir()
    assert p.outputs_dir() == p.STUDIO_ROOT / "outputs"

def test_var_dir():
    import shared.paths as p
    d = p.var_dir("compiler", "uploads")
    assert d == p.STUDIO_ROOT / "var" / "compiler" / "uploads" and d.is_dir()
