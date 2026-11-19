from pathlib import Path
import shared.paths as paths


def test_host_arch_normalises_arm64(monkeypatch):
    monkeypatch.setattr(paths.platform, "machine", lambda: "arm64")
    assert paths.host_arch() == "aarch64"
    monkeypatch.setattr(paths.platform, "machine", lambda: "x86_64")
    assert paths.host_arch() == "x86_64"


def test_build_dir_candidates_put_host_arch_first(monkeypatch):
    root = Path("/r")
    monkeypatch.setattr(paths.platform, "machine", lambda: "aarch64")
    assert paths.build_dir_candidates(root) == [
        root / "build_aarch64" / "src" / "cpp_example",
        root / "build_x86_64" / "src" / "cpp_example",
        root / "bin",
    ]
    monkeypatch.setattr(paths.platform, "machine", lambda: "x86_64")
    assert paths.build_dir_candidates(root)[0] == root / "build_x86_64" / "src" / "cpp_example"


def test_pick_build_dir_prefers_existing_then_host(tmp_path, monkeypatch):
    monkeypatch.setattr(paths.platform, "machine", lambda: "aarch64")
    assert paths.pick_build_dir(tmp_path) == tmp_path / "build_aarch64" / "src" / "cpp_example"
    (tmp_path / "build_x86_64" / "src" / "cpp_example").mkdir(parents=True)
    assert paths.pick_build_dir(tmp_path) == tmp_path / "build_x86_64" / "src" / "cpp_example"
    (tmp_path / "build_aarch64" / "src" / "cpp_example").mkdir(parents=True)
    assert paths.pick_build_dir(tmp_path) == tmp_path / "build_aarch64" / "src" / "cpp_example"


def test_configs_use_shared_build_dir_rule():
    from dx_app.core import config as app_config
    from dx_modelzoo.core import config as mz_config
    assert app_config.BUILD_DIR == paths.pick_build_dir(app_config.DX_APP_ROOT)
    assert mz_config.BUILD_DIR == paths.pick_build_dir(mz_config.DX_APP_ROOT)
    assert app_config._BUILD_DIR_CANDIDATES[0].parent.parent.name == f"build_{paths.host_arch()}"
