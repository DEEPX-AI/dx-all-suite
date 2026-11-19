"""A model with a C++ example source but no built runner is `cpp_buildable` — Model Zoo offers Build C++ runner."""
import importlib


def _cat(monkeypatch, tmp_path, src_exists, bin_exists):
    cat = importlib.import_module("dx_modelzoo.core.catalog")
    from shared import dx_app_layout as layout
    monkeypatch.setattr(cat, "DX_APP_ROOT", tmp_path)
    monkeypatch.setattr(cat, "BUILD_DIR", tmp_path / "build")
    monkeypatch.setattr(layout, "example_name", lambda root, task, name, mf="": "ex")
    src = tmp_path / "ex_sync.cpp"
    if src_exists:
        src.write_text("int main(){}")
    monkeypatch.setattr(layout, "cpp_source", lambda root, task, name, v: tmp_path / f"{name}_{v}.cpp")
    (tmp_path / "build").mkdir()
    if bin_exists:
        (tmp_path / "build" / "ex_sync").write_text("")
    return cat


def test_source_without_runner_is_buildable(monkeypatch, tmp_path):
    cat = _cat(monkeypatch, tmp_path, src_exists=True, bin_exists=False)
    assert cat._cpp_buildable("m", "classification", "m.dxnn") is True


def test_an_already_built_model_is_not(monkeypatch, tmp_path):
    assert _cat(monkeypatch, tmp_path, src_exists=True, bin_exists=True)._cpp_buildable("m", "c", "") is False


def test_a_model_without_a_cpp_source_is_not(monkeypatch, tmp_path):
    assert _cat(monkeypatch, tmp_path, src_exists=False, bin_exists=False)._cpp_buildable("m", "c", "") is False


def test_refresh_variants_updates_cpp_buildable(monkeypatch, tmp_path):
    cat = _cat(monkeypatch, tmp_path, True, False)
    monkeypatch.setattr(cat, "_detect_inference_variants", lambda *a, **k: {"cpp": ["sync"]})
    monkeypatch.setattr(cat, "_cpp_buildable", lambda *a, **k: False)
    c = {"models": [{"id": "m", "category": "c", "model_file": "", "variants": {}, "cpp_buildable": True}]}
    cat._refresh_variants(c)
    assert c["models"][0]["cpp_buildable"] is False
