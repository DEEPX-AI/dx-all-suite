"""Studio preparation requires the runnable targets it actually exposes, not any *_sync file."""
from pathlib import Path
import sys

import pytest

from dx_app.core import config, graph_cli, graph_validate, setup_steps
from shared import dx_app_layout


@pytest.fixture
def app_tree(tmp_path, monkeypatch):
    root = tmp_path / "app"
    root.mkdir()
    build = root / "build_x86_64" / "src" / "cpp_example"
    build.mkdir(parents=True)
    monkeypatch.setattr(setup_steps, "DX_APP_ROOT", root)
    monkeypatch.setattr(setup_steps, "BUILD_DIR", build)
    monkeypatch.setattr(config, "DX_APP_ROOT", root)
    monkeypatch.setattr(config, "BUILD_DIR", build)
    monkeypatch.setattr(setup_steps, "_probe_dx_engine_venv", lambda: (True, "ready"))
    monkeypatch.setattr(setup_steps, "_find_dxcom", lambda: None)
    monkeypatch.setattr(setup_steps, "_dxcom_version", lambda: None)
    monkeypatch.setattr(setup_steps, "_get_npu_driver_version", lambda: "--")
    from shared import runtime
    monkeypatch.setattr(runtime, "_has_numpy_cv2_dxengine", lambda _: True)
    monkeypatch.setattr(runtime, "runtime_python", lambda: sys.executable)
    dx_app_layout.clear_cache()
    yield root, build
    dx_app_layout.clear_cache()


def _executable(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/bin/sh\nexit 0\n")
    path.chmod(0o755)


def _example(root, build, *, nested=False):
    folder = root / "src" / "cpp_example" / "object_detection"
    folder = folder / "yolo" / "detector" if nested else folder / "detector"
    folder.mkdir(parents=True)
    for variant in ("sync", "async"):
        (folder / f"detector_{variant}.cpp").write_text("int main() { return 0; }\n")
        _executable(build / f"detector_{variant}")


def _graphs(build):
    for name in graph_cli.NAMES.values():
        _executable(build / name)


def test_studio_build_requests_full_sdk_build_without_changing_arch():
    step = setup_steps.SETUP_STEPS["dx-app-build"]
    assert "--all" in step["args"]
    assert step["args"][step["args"].index("--arch") + 1] == "x86_64"


def test_assets_use_studio_entrypoint_not_sdk_bulk_setup():
    step = setup_steps.SETUP_STEPS["dx-app-setup"]
    assert not step.get("script"), "SDK setup.sh is not the Studio asset installer"
    assert step["cmd"]() == [sys.executable, "-m", "shared.asset_setup", "app"]
    assert step["cwd"]() == Path(setup_steps.__file__).resolve().parents[2]


def test_minimal_build_does_not_skip_graph_preparation(app_tree):
    """The full step (Run All) still needs the Graph binaries a --minimal build lacks (SR-842);
    Quick Start, which builds --minimal for the demos, does not wait for them."""
    root, build = app_tree
    _example(root, build)
    status = setup_steps.setup_status()["dx-app-build"]
    assert not status["ok"], status
    assert status["demo_ok"], status
    assert "multi_model_graph_sync" in status["detail"]
    assert "dx-app-build" not in setup_steps.quick_start_plan()


def test_graphs_alone_are_not_a_complete_demo_build(app_tree):
    _, build = app_tree
    _graphs(build)
    assert not setup_steps.setup_status()["dx-app-build"]["ok"]


@pytest.mark.parametrize("nested,installed", [(False, False), (True, False), (True, True)])
def test_ready_build_resolves_declared_examples_and_both_graph_variants(app_tree, monkeypatch, nested, installed):
    root, build = app_tree
    if installed:
        build = root / "bin"
        monkeypatch.setattr(config, "BUILD_DIR", build)
        monkeypatch.setattr(setup_steps, "BUILD_DIR", build)
    _example(root, build, nested=nested)
    _graphs(build)
    assert setup_steps.setup_status()["dx-app-build"]["ok"]
    (build / "detector_async").unlink()
    status = setup_steps.setup_status()["dx-app-build"]
    assert not status["ok"], "a declared async runner must be executable too"
    assert "detector_async" in status["detail"]


def test_nonexecutable_graph_is_not_ready(app_tree):
    root, build = app_tree
    _example(root, build)
    _graphs(build)
    (build / "multi_model_graph_async").chmod(0o644)
    assert not setup_steps.setup_status()["dx-app-build"]["ok"]


def test_graph_missing_message_names_existing_full_or_targeted_build(monkeypatch):
    monkeypatch.setattr(graph_cli, "available", lambda: None)
    result = graph_validate.validate({"nodes": []})
    how = result["errors"][0]["how"]
    assert "./build.sh --target multi_model_graph_sync multi_model_graph_async" in how
    assert "./build.sh --all" in how
    monkeypatch.setattr(graph_cli, "binary", lambda variant: None)
    with pytest.raises(graph_cli.GraphCliMissing) as missing:
        graph_cli.run(["--help"])
    assert "./build.sh --target multi_model_graph_sync multi_model_graph_async" in str(missing.value)


def _without(monkeypatch, *missing):
    original = setup_steps.shutil.which
    monkeypatch.setattr(setup_steps.shutil, "which",
                        lambda name, **kw: None if name in missing else (original(name, **kw) or "/usr/bin/" + name))


def test_xvfb_is_a_separate_optional_live_requirement_not_a_dx_app_deps_gate(app_tree, monkeypatch):
    """dx_app install.sh --all never installs Xvfb, so gating dx-app-deps on it made Run All and
    Quick Start re-run sudo install.sh forever on a board without Xvfb."""
    _without(monkeypatch, "Xvfb")
    status = setup_steps.setup_status()
    assert status["dx-app-deps"]["ok"], status["dx-app-deps"]
    assert "Xvfb" not in status["dx-app-deps"]["detail"]
    live = status["live-display"]
    assert live["ok"] is False and live["optional"] is True
    assert live["hint"] == "sudo apt install xvfb"
    assert "sudo apt install xvfb" in live["detail"]
    assert "dx-app-deps" not in setup_steps.quick_start_plan()
    assert "live-display" not in setup_steps.quick_start_plan()
    assert "live-display" not in setup_steps.SETUP_STEPS, "no installer step runs apt for it"
    diag = next((c for c in setup_steps.deep_diagnostics()["checks"] if c["id"] == "live_display"), None)
    assert diag and not diag["ok"], "Setup diagnostics must check the Live display prerequisite"
    assert all("sudo apt install xvfb" in text for text in diag["fix"].values())
    assert "optional" in diag["label"]["en"].lower()
    _without(monkeypatch)
    assert setup_steps.setup_status()["live-display"]["ok"] is True


def test_dx_app_deps_still_needs_the_compiler_toolchain(app_tree, monkeypatch):
    _without(monkeypatch, "cmake")
    status = setup_steps.setup_status()["dx-app-deps"]
    assert not status["ok"] and "cmake" in status["detail"]


def _run_demo(root, *stems):
    (root / "run_demo.sh").write_text(
        "DEMO_MODEL=(\n" + "".join('    "{}.dxnn"\n'.format(stem) for stem in stems) + ")\n")


def _plain_example(root, build, name, built):
    folder = root / "src" / "cpp_example" / "object_detection" / name
    folder.mkdir(parents=True)
    for variant in ("sync", "async"):
        (folder / f"{name}_{variant}.cpp").write_text("int main() { return 0; }\n")
        if built:
            _executable(build / f"{name}_{variant}")


def test_build_readiness_is_the_demo_runners_and_graph_not_every_target(app_tree):
    """An optional per-model target that is not built (or fails to build on this board) must not
    keep the step "not ready" forever; the demo runners and the Graph binaries are the promise."""
    root, build = app_tree
    _run_demo(root, "detector")
    _example(root, build)
    _plain_example(root, build, "extra", built=False)
    _graphs(build)
    dx_app_layout.clear_cache()
    status = setup_steps.setup_status()["dx-app-build"]
    assert status["ok"] and status["demo_ok"], status
    assert status["complete"] is False
    assert "demo C++ 2/2" in status["detail"] and "all C++ 2/4" in status["detail"]
    (build / "detector_async").unlink()
    status = setup_steps.setup_status()["dx-app-build"]
    assert not status["ok"] and not status["demo_ok"]
    assert "detector_async" in status["detail"]


def test_quick_start_needs_only_the_demo_build_and_demo_assets(app_tree, monkeypatch):
    from shared import asset_setup

    root, build = app_tree
    _run_demo(root, "detector")
    _example(root, build)               # demo runners built, Graph binaries not
    dx_app_layout.clear_cache()
    monkeypatch.setattr(asset_setup, "sample_assets_status", lambda *a, **k: {
        "ok": False, "demo_ok": True, "verified": False, "detail": "demo models 1/1 · models 1/497"})
    status = setup_steps.setup_status()
    assert not status["dx-app-build"]["ok"] and status["dx-app-build"]["demo_ok"]
    plan = setup_steps.quick_start_plan()
    assert "dx-app-build" not in plan and "dx-app-setup" not in plan, plan


def test_quick_start_runs_the_minimal_build_and_the_demo_download():
    """demo_only reached setup_run but a "cmd" step ignored args, so Quick Start downloaded the
    whole manifest; the build step ran --all."""
    argv, _ = setup_steps.step_argv("dx-app-setup", {"demo_only": True})
    assert argv == [sys.executable, "-m", "shared.asset_setup", "app", "--demo"]
    argv, _ = setup_steps.step_argv("dx-app-setup", {})
    assert argv == [sys.executable, "-m", "shared.asset_setup", "app"]
    argv, _ = setup_steps.step_argv("dx-app-build", {"demo_only": True})
    assert "--minimal" in argv and "--all" not in argv
    assert argv[argv.index("--arch") + 1] == "x86_64"
    argv, _ = setup_steps.step_argv("dx-app-build", {})
    assert "--all" in argv and "--minimal" not in argv


@pytest.mark.parametrize("available", [False, True])
def test_opencv_diagnostic_uses_isolated_media_probe(app_tree, monkeypatch, available):
    from shared import media
    calls = []

    def probe(operation, **params):
        calls.append(operation)
        if not available:
            raise media.MediaError("OpenCV runtime probe failed; run Python Inference Deps in Setup")
        return {"opencv": "4.99.0", "numpy": "2.0.0"}

    monkeypatch.setattr(media, "run_media", probe)
    diag = next(c for c in setup_steps.deep_diagnostics()["checks"] if c["id"] == "opencv")
    assert calls == ["probe"]
    assert diag["ok"] == available
    assert ("4.99.0" if available else "OpenCV runtime probe failed") in diag["detail"]


def test_acceptance_runnable_model_requires_executable_selected_variant():
    from tests.acceptance.test_sdkreq_474_dx_app import _runnable_model
    models = [
        {"name": "yolov8-n_640x640", "category": "object_detection", "model_exists": True,
         "cpp": False, "cpp_sync": False, "python": True, "py_sync": True},
        {"name": "async_only", "category": "object_detection", "model_exists": True,
         "cpp": True, "cpp_sync": False, "cpp_async": True},
        {"name": "ready_sync", "category": "object_detection", "model_exists": True,
         "cpp": True, "cpp_sync": True},
    ]

    class Frame:
        def evaluate(self, script):
            return models

    assert _runnable_model(Frame())["name"] == "ready_sync"


def test_acceptance_graph_missing_prerequisite_is_not_run_but_ready_catalog_error_fails():
    from tests.acceptance import test_sdkreq_474_dx_app as acceptance

    assert hasattr(acceptance, "_graph_example"), "Graph acceptance needs an explicit prerequisite check"
    with pytest.raises(pytest.skip.Exception, match="NOT RUN:.*--target"):
        acceptance._graph_example({"available": False, "error": "graph_binary_missing"})
    with pytest.raises(AssertionError, match="list_models_failed"):
        acceptance._graph_example({"available": True, "error": "list_models_failed: native failure"})
    with pytest.raises(pytest.skip.Exception, match="NOT RUN:.*model"):
        acceptance._graph_example({"available": True, "models": [], "examples": [
            {"id": "missing", "models": ["absent"]}]})
    ready = {"id": "ready", "models": ["detector"], "logic": False}
    assert acceptance._graph_example({"available": True, "models": [
        {"name": "detector", "installed": True, "ready": True, "state": "installed"}],
        "examples": [{"id": "missing", "models": ["absent"]}, ready]}) == ready


@pytest.mark.parametrize("verified", [False, True])
def test_asset_readiness_uses_local_validation_not_any_nonempty_model_and_video(app_tree, monkeypatch, verified):
    from shared import asset_setup

    root, _ = app_tree
    assets = root / "assets"
    for folder, name in (("models", "legacy.dxnn"), ("videos", "partial.mp4")):
        (assets / folder).mkdir(parents=True)
        (assets / folder / name).write_bytes(b"bad")
    monkeypatch.setattr(setup_steps, "ASSETS_DIR", assets)
    calls = []
    status = {"ok": verified, "demo_ok": verified,
              "detail": "verified transfers" if verified else "unverified legacy assets"}

    def local_status(component, sdk_root=None, resource_root=None):
        calls.append((component, sdk_root))
        return status

    monkeypatch.setattr(asset_setup, "sample_assets_status", local_status, raising=False)
    assert setup_steps.setup_status()["dx-app-setup"] == status
    assert calls == [("app", root)]
    assert ("dx-app-setup" in setup_steps.quick_start_plan()) == (not verified)


def test_live_start_without_xvfb_fails_with_the_same_install_hint(monkeypatch):
    """No step installs Xvfb, so Live start is where its absence must be explained (SR-845)."""
    from dx_app.core import camera, graph_live, live

    _without(monkeypatch, "Xvfb")
    monkeypatch.setattr(live.shutil if hasattr(live, "shutil") else setup_steps.shutil, "which",
                        lambda name, **kw: None if name == "Xvfb" else "/usr/bin/" + name)
    monkeypatch.setattr(camera, "_xlib", lambda: object())
    monkeypatch.setattr(camera, "_xcb", lambda: object())
    result = live._start_live("demo", "object_detection", "m.dxnn", "cpp", "sync", "camera",
                              0, None, None, 0, 1)
    body = result[0] if isinstance(result, tuple) else result
    assert body["error_key"] == "live_deps_missing", body
    assert setup_steps.LIVE_DISPLAY_HINT in body["error"]
    assert any(setup_steps.LIVE_DISPLAY_HINT in item for item in graph_live._deps_missing())
