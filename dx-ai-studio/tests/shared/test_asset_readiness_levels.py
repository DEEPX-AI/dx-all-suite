"""Sample-asset readiness matches what each step promises (S4 review of SR-848 follow-up).

* Quick Start promises the demo set — the models dx_app's run_demo.sh launches plus the videos —
  and only that set is downloaded and required.
* The full Sample Assets step promises the whole manifest.
* A file that is present but has no Studio verification record is *unverified*, not *missing*:
  it counts as installed, is reported separately, and running the step again verifies it by
  Content-Length without downloading the body again.
"""
import json

import pytest

from tests.shared.test_asset_setup import archive, assets, opener, sdk

DEMO_SH = '''#!/bin/bash
DEMO_MODEL=(
    "tiny.dxnn"   # the one demo model
)
DEMO_VIDEO=(
    "assets/videos/dance.mov"
)
'''


def _app_sdk(tmp_path):
    root = sdk(tmp_path, "app")
    (root / "scripts" / "modelzoo_manifest.json").write_text(json.dumps([
        {"name": "Tiny", "dxnn_url": "https://sdk.deepx.ai/modelzoo/dxnn/2_4_0/tiny.dxnn",
         "json_url": "https://sdk.deepx.ai/modelzoo/json/2_4_0/tiny.json"},
        {"name": "Huge", "dxnn_url": "https://sdk.deepx.ai/modelzoo/dxnn/2_4_0/huge.dxnn",
         "json_url": None},
    ]))
    (root / "run_demo.sh").write_text(DEMO_SH)
    return root


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.delenv("DX_APP_MODELS_DIR", raising=False)
    return _app_sdk(tmp_path), tmp_path / "res"


def test_demo_install_downloads_only_the_run_demo_models_and_the_videos(app):
    module = assets()
    root, resources = app
    calls = []
    module.install_assets("app", demo=True, sdk_root=root, resource_root=resources,
                          open_url=opener(calls, archive()))
    names = [url.rsplit("/", 1)[-1] for url in calls]
    assert "huge.dxnn" not in names
    assert {"tiny.dxnn", "tiny.json"} <= set(names)
    assert any(name.endswith(".tar.gz") for name in names), "demos need the sample videos"
    status = module.sample_assets_status("app", sdk_root=root, resource_root=resources)
    assert status["demo_ok"] is True, status
    assert status["ok"] is False, "the full step still promises the whole manifest"
    assert status["models"]["missing"] == 1


def test_the_cli_demo_flag_reaches_install(app, monkeypatch):
    module = assets()
    seen = {}
    monkeypatch.setattr(module, "install_assets", lambda component, **kw: seen.update(kw, c=component))
    assert module.main(["app", "--demo"]) == 0
    assert seen["demo"] is True and seen["c"] == "app"


def test_a_demo_request_without_the_sdk_demo_list_fails_clearly(app):
    module = assets()
    root, resources = app
    (root / "run_demo.sh").unlink()
    with pytest.raises(ValueError, match="run_demo.sh"):
        module.install_assets("app", demo=True, sdk_root=root, resource_root=resources,
                              open_url=opener([], archive()))


def test_present_without_a_record_is_unverified_not_missing(app):
    module = assets()
    root, resources = app
    module.install_assets("app", sdk_root=root, resource_root=resources, open_url=opener([], archive()))
    models = root / "assets" / "models"
    # A file another tool (the SDK's own downloader) wrote: present, no Studio record.
    (models / "huge.dxnn").write_bytes(b"from the sdk downloader")
    status = module.sample_assets_status("app", sdk_root=root, resource_root=resources)
    assert status["ok"] is True, "a present file is installed; it is not re-downloaded for a missing record"
    assert status["verified"] is False
    assert status["models"]["unverified"] == 1 and status["models"]["missing"] == 0
    assert "1 unverified" in status["detail"]
    (models / "huge.dxnn").unlink()
    status = module.sample_assets_status("app", sdk_root=root, resource_root=resources)
    assert status["ok"] is False and status["models"]["missing"] == 1


def test_running_the_step_again_verifies_a_present_file_without_downloading_it(app):
    module = assets()
    root, resources = app
    module.install_assets("app", sdk_root=root, resource_root=resources, open_url=opener([], archive()))
    target = root / "assets" / "models" / "huge.dxnn"
    target.write_bytes(b"model")  # the size the server reports (opener serves b"model")
    for receipt in (target.parent / ".studio-assets").glob("*.json"):
        receipt.unlink()
    before = target.stat().st_mtime_ns
    module.install_assets("app", sdk_root=root, resource_root=resources, open_url=opener([], archive()))
    assert target.stat().st_mtime_ns == before, "a size-matching file is verified in place"
    assert module.sample_assets_status("app", sdk_root=root, resource_root=resources)["verified"] is True


def test_videos_the_sdk_installed_without_a_studio_inventory_are_unverified_not_missing(app):
    """The SDK's setup_sample_videos.sh writes no Studio inventory; those videos are present."""
    module = assets()
    root, resources = app
    module.install_assets("app", demo=True, sdk_root=root, resource_root=resources,
                          open_url=opener([], archive()))
    videos = root / "assets" / "videos"
    import shutil
    shutil.rmtree(videos / ".studio-assets")   # inventory and member records: as the SDK leaves it
    status = module.sample_assets_status("app", sdk_root=root, resource_root=resources)
    assert status["videos"]["unverified"] == 1 and status["videos"]["missing"] == 0, status
    assert status["demo_ok"] is True and status["verified"] is False
    for item in videos.iterdir():
        if item.is_file():
            item.unlink()
    status = module.sample_assets_status("app", sdk_root=root, resource_root=resources)
    assert status["demo_ok"] is False and status["videos"]["ok"] is False


def test_a_half_extracted_folder_without_an_inventory_is_not_ready(app):
    """Without a Studio inventory nothing says which files the archive held: a folder holding some other video
    but not one the demos play (run_demo.sh DEMO_VIDEO) is missing that video, not ready."""
    module = assets()
    root, resources = app
    module.install_assets("app", demo=True, sdk_root=root, resource_root=resources,
                          open_url=opener([], archive()))
    videos = root / "assets" / "videos"
    import shutil
    shutil.rmtree(videos / ".studio-assets")
    (videos / "dance.mov").unlink()
    (videos / "other.mp4").write_bytes(b"\0")
    status = module.sample_assets_status("app", sdk_root=root, resource_root=resources)
    assert status["videos"]["ok"] is False and status["videos"]["missing"] == 1, status
    assert status["videos"]["absent"] == ["dance.mov"]
    assert status["demo_ok"] is False and status["ok"] is False


def test_the_demo_videos_are_read_from_run_demo_sh(app):
    root, _ = app
    assert assets().demo_video_files(root) == ["dance.mov"]
    (root / "run_demo.sh").write_text('DEMO_VIDEO=(\n    ""\n    "assets/videos/a.mp4"  # x\n    "sample/b.mp4"\n'
                                      '    "assets/videos/../x.mp4"\n    "assets/videos/a.mp4"\n)\n')
    assert assets().demo_video_files(root) == ["a.mp4"]
    (root / "run_demo.sh").unlink()
    assert assets().demo_video_files(root) == []


@pytest.mark.parametrize("component", ["app", "stream"])
def test_missing_inventory_never_certifies_remaining_video_receipts(tmp_path, monkeypatch, component):
    monkeypatch.delenv("DX_APP_MODELS_DIR", raising=False)
    module = assets()
    root = _app_sdk(tmp_path) if component == "app" else sdk(tmp_path, "stream")
    resources = tmp_path / "res"
    module.install_assets(
        component,
        sdk_root=root,
        resource_root=resources,
        open_url=opener([], archive([
            ("samples/dance.mov", b"video"),
            ("samples/bonus.mp4", b"video"),
        ])),
    )
    output = root / ("assets" if component == "app" else "dx_stream/samples")
    videos = output / "videos"
    (videos / "bonus.mp4").unlink()
    (videos / ".studio-assets" / "sample-videos.json").unlink()

    status = module.sample_assets_status(component, sdk_root=root, resource_root=resources)

    assert status["videos"]["ok"] is True
    assert status["videos"]["all_verified"] is False
    assert status["videos"]["verified"] == 0
    assert status["videos"]["unverified"] == 1
    assert status["verified"] is False
