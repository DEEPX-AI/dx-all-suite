"""Studio owns sample installation; SDK files are declarative input, never executed."""
import importlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import threading
import urllib.error
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest


def assets():
    assert importlib.util.find_spec("shared.asset_setup"), "Studio needs a safe asset entry point"
    return importlib.import_module("shared.asset_setup")


class Response(io.BytesIO):
    status = 200

    def __init__(self, data):
        super().__init__(data)
        self.headers = {"Content-Length": str(len(data))}


def archive(entries=None):
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w:gz") as tar:
        for name, body in (entries or [("samples/dance.mov", b"video")]):
            member = tarfile.TarInfo(name)
            member.size = len(body)
            tar.addfile(member, io.BytesIO(body))
    return output.getvalue()


def sdk(tmp_path, component="stream"):
    root = tmp_path / component
    root.mkdir()
    if component == "stream":
        (root / "model_list.json").write_text(json.dumps({
            "version": "2_4_0", "models": ["tiny.dxnn", "other.dxnn"]}))
        (root / "setup_sample_models.sh").write_text(
            'BASE_URL="https://sdk.deepx.ai/modelzoo/dxnn"\n')
        video_source = "res/video/sample_videos.tar.gz"
    else:
        (root / "scripts").mkdir()
        (root / "scripts" / "modelzoo_manifest.json").write_text(json.dumps([{
            "name": "Tiny", "dxnn_url": "https://sdk.deepx.ai/modelzoo/dxnn/2_4_0/tiny.dxnn",
            "json_url": "https://sdk.deepx.ai/modelzoo/json/2_4_0/tiny.json",
        }]))
        video_source = "res/video/sample_videos_${VIDEO_VERSION}.tar.gz"
    (root / "setup_sample_videos.sh").write_text(
        'BASE_URL="https://sdk.deepx.ai/"\nVIDEO_VERSION="v3.2.2"\nSOURCE_PATH="' + video_source + '"\n')
    return root


def opener(calls, video=None, fail=False):
    def open_url(url):
        calls.append(url)
        if fail:
            raise OSError("offline test")
        return Response(video if url.endswith(".tar.gz") else b"model")
    return open_url


@pytest.mark.parametrize("component", ["stream", "app"])
def test_complete_models_video_layout_and_existing_file_repair(tmp_path, component, monkeypatch):
    module = assets()
    monkeypatch.delenv("DX_APP_MODELS_DIR", raising=False)
    root = sdk(tmp_path, component)
    resources = tmp_path / "res"
    calls = []
    module.install_assets(component, sdk_root=root, resource_root=resources,
                          open_url=opener(calls, archive()))
    output = root / ("dx_stream/samples" if component == "stream" else "assets")
    assert (output / "models" / "tiny.dxnn").read_bytes() == b"model"
    assert (output / "videos" / "dance.mov").read_bytes() == b"video"
    assert (output / "models").is_symlink()
    assert (output / "videos").is_symlink()
    if component == "stream":
        assert (output / "models").resolve() == resources / "models" / "models-2_4_0"
        assert (output / "videos").resolve() == resources / "videos" / "sample_videos"
        assert calls[0] == "https://sdk.deepx.ai/modelzoo/dxnn/2_4_0/tiny.dxnn"
    else:
        assert (output / "models").resolve() == resources / "models"
        assert (output / "models" / "tiny.json").read_bytes() == b"model"
        assert (output / "videos").resolve() == resources / "videos" / "sample_videos_v3.2.2"
    (output / "models" / "tiny.dxnn").write_bytes(b"bad")
    module.install_assets(component, sdk_root=root, resource_root=resources,
                          open_url=opener(calls, archive()))
    assert (output / "models" / "tiny.dxnn").read_bytes() == b"model"


def test_single_model_does_not_download_videos_or_other_models(tmp_path):
    module = assets()
    root = sdk(tmp_path)
    calls = []
    module.install_assets("stream", model="tiny.dxnn", sdk_root=root, resource_root=tmp_path / "res",
                          open_url=opener(calls))
    assert len(calls) == 1 and calls[0].endswith("/tiny.dxnn")
    output = root / "dx_stream" / "samples"
    assert not (output / "models" / "other.dxnn").exists()
    assert not (output / "videos").exists()


@pytest.mark.parametrize("name", ["../tiny.dxnn", "unknown.dxnn", "-bad", "a" * 300])
def test_model_is_bounded_and_from_manifest_before_any_network(tmp_path, name):
    module = assets()
    root = sdk(tmp_path)
    calls = []
    with pytest.raises(ValueError, match="[Mm]odel"):
        module.install_assets("stream", model=name, sdk_root=root, resource_root=tmp_path / "res",
                              open_url=opener(calls))
    assert calls == []


def test_real_directory_unrelated_model_and_symlink_survive_failure(tmp_path):
    module = assets()
    root = sdk(tmp_path)
    output = root / "dx_stream" / "samples" / "models"
    output.mkdir(parents=True)
    unrelated = output / "personal.dxnn"
    unrelated.write_bytes(b"personal")
    link = output / "personal-link.dxnn"
    link.symlink_to(unrelated)
    (output / "tiny.dxnn").write_bytes(b"old")
    with pytest.raises(OSError, match="offline"):
        module.install_assets("stream", sdk_root=root, resource_root=tmp_path / "res",
                              open_url=opener([], fail=True))
    assert not output.is_symlink()
    assert unrelated.read_bytes() == b"personal"
    assert link.is_symlink() and link.resolve() == unrelated
    assert (output / "tiny.dxnn").read_bytes() == b"old"


def test_correct_link_preserved_and_user_link_never_repointed(tmp_path):
    module = assets()
    root = sdk(tmp_path)
    resources = tmp_path / "res"
    output = root / "dx_stream" / "samples" / "models"
    output.parent.mkdir(parents=True)
    user = tmp_path / "user"
    user.mkdir()
    (user / "precious").write_bytes(b"safe")
    output.symlink_to(user, target_is_directory=True)
    calls = []
    with pytest.raises(OSError, match="symlink"):
        module.install_assets("stream", model="tiny.dxnn", sdk_root=root, resource_root=resources,
                              open_url=opener(calls))
    assert calls == []
    assert output.resolve() == user
    assert (user / "precious").read_bytes() == b"safe"


def test_directory_permissions_fail_with_path_before_network(tmp_path, monkeypatch):
    module = assets()
    root = sdk(tmp_path)
    original = type(tmp_path).mkdir
    resources = tmp_path / "denied"
    calls = []

    def mkdir(path, *args, **kwargs):
        if str(path).startswith(str(resources)):
            raise PermissionError("original denied")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(type(tmp_path), "mkdir", mkdir)
    with pytest.raises(OSError, match="original denied") as exc:
        module.install_assets("stream", sdk_root=root, resource_root=resources, open_url=opener(calls))
    assert str(resources) in str(exc.value)
    assert calls == []


@pytest.mark.parametrize("name", ["../escaped.mov", "/escaped.mov", "samples/../../escaped.mov"])
def test_video_traversal_rejected_without_touching_old_video(tmp_path, name):
    module = assets()
    root = sdk(tmp_path)
    videos = root / "dx_stream" / "samples" / "videos"
    videos.mkdir(parents=True)
    old = videos / "dance.mov"
    old.write_bytes(b"old-video")
    with pytest.raises((ValueError, OSError), match="[Aa]rchive"):
        module.install_assets("stream", sdk_root=root, resource_root=tmp_path / "res",
                              open_url=opener([], archive([(name, b"evil")])))
    assert old.read_bytes() == b"old-video"
    assert not (root / "escaped.mov").exists()


def test_video_links_are_rejected_before_any_archive_member_is_published(tmp_path):
    module = assets()
    root = sdk(tmp_path)
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w:gz") as tar:
        member = tarfile.TarInfo("samples/dance.mov")
        member.size = 5
        tar.addfile(member, io.BytesIO(b"video"))
        member = tarfile.TarInfo("samples/evil")
        member.type = tarfile.SYMTYPE
        member.linkname = "../../outside"
        tar.addfile(member)
    with pytest.raises((ValueError, OSError), match="[Aa]rchive"):
        module.install_assets("stream", sdk_root=root, resource_root=tmp_path / "res",
                              open_url=opener([], output.getvalue()))
    assert not (root / "dx_stream" / "samples" / "videos" / "dance.mov").exists()


def test_cli_errors_are_nonzero_and_actionable(monkeypatch, capsys):
    module = assets()

    def failure(*args, **kwargs):
        raise PermissionError("denied: /original/models")

    monkeypatch.setattr(module, "install_assets", failure)
    assert module.main(["app"]) == 1
    assert "/original/models" in capsys.readouterr().err


def test_cli_cancel_is_nonzero(monkeypatch):
    module = assets()
    from shared.atomic_download import DownloadCancelled

    def cancelled(*args, **kwargs):
        raise DownloadCancelled("cancelled")

    monkeypatch.setattr(module, "install_assets", cancelled)
    assert module.main(["stream", "--model", "tiny.dxnn"]) == 130


@pytest.mark.parametrize("kind", ["http", "permission", "network"])
@pytest.mark.parametrize("password", ["password", "pass'word"])
def test_failed_download_candidates_are_logged_without_url_secrets(tmp_path, monkeypatch, kind, password):
    module = assets()
    root = sdk(tmp_path)
    models = root / "dx_stream" / "samples" / "models"
    models.mkdir(parents=True)
    target = models / "tiny.dxnn"
    target.write_bytes(b"old-model")
    urls = [
        "https://user:{}@first.example/models/tiny.dxnn?token=private-token#private-fragment".format(password),
        "https://user:{}@last.example/models/tiny.dxnn?signature=private-signature#private-fragment".format(password),
    ]
    monkeypatch.setattr(module.dxrt, "download_urls", lambda url: urls)
    messages, calls = [], []
    def open_url(url):
        calls.append(url)
        if kind == "http":
            raise urllib.error.HTTPError(url, 404, "missing " + url, {}, None)
        if kind == "permission":
            raise PermissionError("access denied for " + url)
        raise OSError("connection failed for " + url)
    expected = {"http": urllib.error.HTTPError, "permission": PermissionError, "network": OSError}[kind]
    with pytest.raises(expected):
        module.install_assets(
            "stream", model="tiny.dxnn", sdk_root=root, resource_root=tmp_path / "res",
            open_url=open_url, log=lambda message, **kwargs: messages.append(message),
        )
    assert calls == urls
    diagnostic = "\n".join(messages)
    assert "https://first.example/models/tiny.dxnn" in diagnostic
    assert "https://last.example/models/tiny.dxnn" in diagnostic
    for secret in ("user:" + password, "private-token", "private-signature", "private-fragment"):
        assert secret not in diagnostic
    assert {"http": "404", "permission": "access denied", "network": "connection failed"}[kind] in diagnostic
    assert target.read_bytes() == b"old-model"
    assert not list(models.rglob("*.part"))


def test_download_fallback_keeps_the_success_path_and_reports_the_failed_candidate(tmp_path, monkeypatch):
    module = assets()
    root = sdk(tmp_path)
    urls = ["https://first.example/tiny.dxnn", "https://last.example/tiny.dxnn"]
    monkeypatch.setattr(module.dxrt, "download_urls", lambda url: urls)
    messages, calls = [], []
    def open_url(url):
        calls.append(url)
        if url == urls[0]:
            raise urllib.error.HTTPError(url, 404, "missing", {}, None)
        return Response(b"model")
    module.install_assets(
        "stream", model="tiny.dxnn", sdk_root=root, resource_root=tmp_path / "res",
        open_url=open_url, log=lambda message, **kwargs: messages.append(message),
    )
    assert calls == urls
    assert (root / "dx_stream" / "samples" / "models" / "tiny.dxnn").read_bytes() == b"model"
    assert any(urls[0] in message and "404" in message for message in messages)


def test_download_cancel_does_not_try_the_next_candidate(tmp_path, monkeypatch):
    module = assets()
    from shared.atomic_download import DownloadCancelled

    root = sdk(tmp_path)
    urls = ["https://first.example/tiny.dxnn", "https://last.example/tiny.dxnn"]
    monkeypatch.setattr(module.dxrt, "download_urls", lambda url: urls)
    calls = []
    def cancelled(url):
        calls.append(url)
        raise DownloadCancelled("cancelled")
    with pytest.raises(DownloadCancelled):
        module.install_assets("stream", model="tiny.dxnn", sdk_root=root,
                              resource_root=tmp_path / "res", open_url=cancelled)
    assert calls == urls[:1]


def test_cli_download_errors_redact_url_credentials_and_query(monkeypatch, capsys):
    module = assets()
    def failure(*args, **kwargs):
        raise OSError("Failed https://user:password@host.example/model.dxnn?token=private-token#private-fragment")
    monkeypatch.setattr(module, "install_assets", failure)
    assert module.main(["stream", "--model", "tiny.dxnn"]) == 1
    error = capsys.readouterr().err
    assert "https://host.example/model.dxnn" in error
    assert "password" not in error and "private-token" not in error and "private-fragment" not in error


@pytest.mark.parametrize("truncated", [False, True])
def test_cli_runs_real_tiny_loopback_model_and_video_transfers(tmp_path, truncated):
    root = sdk(tmp_path)
    video = archive()
    calls = []
    output = root / "dx_stream" / "samples"
    if truncated:
        (output / "models").mkdir(parents=True)
        (output / "models" / "tiny.dxnn").write_bytes(b"good-old")

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            calls.append((self.path, self.headers.get("Accept-Encoding")))
            data = b"bad" if truncated else (video if self.path.endswith(".tar.gz") else b"model")
            self.send_response(200)
            self.send_header("Content-Length", str(len(data) + (8 if truncated else 0)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        base = "http://127.0.0.1:{}".format(server.server_port)
        (root / "setup_sample_models.sh").write_text('BASE_URL="' + base + '/models"\n')
        (root / "setup_sample_videos.sh").write_text(
            'BASE_URL="' + base + '/"\nSOURCE_PATH="res/video/sample_videos.tar.gz"\n')
        env = dict(os.environ, DX_STREAM_ROOT=str(root), DOCKER_VOLUME_PATH=str(tmp_path / "volume"),
                   PYTHONDONTWRITEBYTECODE="1")
        result = subprocess.run([sys.executable, "-m", "shared.asset_setup", "stream"],
                                cwd=str(Path(__file__).resolve().parents[2]), env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=15)
        assert result.returncode == (1 if truncated else 0), result.stdout + result.stderr
        if truncated:
            assert "[ERROR]" in result.stderr and "[OK]" not in result.stdout
            assert (output / "models" / "tiny.dxnn").read_bytes() == b"good-old"
            assert len(calls) == 1
        else:
            assert "[OK]" in result.stdout
            assert (output / "models" / "tiny.dxnn").read_bytes() == b"model"
            assert (output / "videos" / "dance.mov").read_bytes() == b"video"
            assert len(calls) == 3
        assert all(encoding == "identity" for _, encoding in calls)
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=5)


def test_correct_dangling_sample_symlink_is_kept_on_cancel(tmp_path):
    module = assets()
    from shared.atomic_download import DownloadCancelled
    root = sdk(tmp_path)
    resources = tmp_path / "res"
    output = root / "dx_stream" / "samples" / "models"
    output.parent.mkdir(parents=True)
    expected = resources / "models" / "models-2_4_0"
    output.symlink_to(expected, target_is_directory=True)
    with pytest.raises(DownloadCancelled):
        module.install_assets("stream", model="tiny.dxnn", sdk_root=root, resource_root=resources,
                              open_url=opener([]), cancel=lambda: True)
    assert output.is_symlink() and output.resolve() == expected
    assert not (output / "tiny.dxnn").exists()


@pytest.mark.parametrize("component", ["app", "stream"])
def test_local_readiness_never_verifies_existing_partials_and_never_uses_network(tmp_path, monkeypatch, component):
    module = assets()
    check = getattr(module, "sample_assets_status", None)
    assert callable(check), "Need shared local-only sample readiness"
    monkeypatch.delenv("DX_APP_MODELS_DIR", raising=False)
    root = sdk(tmp_path, component)
    resources = tmp_path / "res"
    output = root / ("assets" if component == "app" else "dx_stream/samples")
    (output / "models").mkdir(parents=True)
    (output / "models" / "tiny.dxnn").write_bytes(b"bad")
    if component == "stream":
        (output / "models" / "other.dxnn").write_bytes(b"bad")
    (output / "videos").mkdir()
    (output / "videos" / "dance.mov").write_bytes(b"bad")
    monkeypatch.setattr(module, "_open_url", lambda url: pytest.fail("readiness must be local"))
    result = check(component, sdk_root=root, resource_root=resources)
    assert result["verified"] is False   # present partials are never verified (ok = nothing missing)
    assert result["models"]["unverified"] >= 1
    assert "unverified" in result["detail"].lower()
    module.install_assets(component, sdk_root=root, resource_root=resources, open_url=opener([], archive()))
    result = check(component, sdk_root=root, resource_root=resources)
    assert result["ok"] is True, result
    assert result["verified"] is True, result
    (output / "models" / "tiny.dxnn").write_bytes(b"other")
    changed = check(component, sdk_root=root, resource_root=resources)
    # Changed after its record: present but unverified (never shown as verified, never as missing).
    assert changed["verified"] is False
    assert changed["models"]["unverified"] == 1 and changed["models"]["missing"] == 0


def test_single_app_model_keeps_manifest_json_sidecar_and_layout(tmp_path, monkeypatch):
    module = assets()
    monkeypatch.delenv("DX_APP_MODELS_DIR", raising=False)
    root = sdk(tmp_path, "app")
    resources = tmp_path / "res"
    calls = []
    module.install_assets("app", model="Tiny", sdk_root=root, resource_root=resources, open_url=opener(calls))
    models = root / "assets" / "models"
    assert models.resolve() == resources / "models"
    assert (models / "tiny.dxnn").read_bytes() == b"model"
    assert (models / "tiny.json").read_bytes() == b"model"
    assert len(calls) == 2 and calls[-1].endswith("/tiny.json")
    assert not (root / "assets" / "videos").exists()


def test_readiness_handles_missing_sdk_contract_as_unverified(tmp_path):
    module = assets()
    check = getattr(module, "sample_assets_status", None)
    assert callable(check), "Need shared local-only sample readiness"
    status = check("app", sdk_root=tmp_path)
    assert status["ok"] is False
    assert "unverified" in status["detail"].lower()


def test_app_cli_matches_actual_sdk_checkout_and_media_consumers(tmp_path, monkeypatch):
    actual = Path(__file__).resolve().parents[3] / "dx-runtime" / "dx_app"
    if not (actual / "setup.sh").is_file():
        pytest.skip("SDK checkout is required for the actual-contract integration test")
    setup = (actual / "setup.sh").read_text()
    video_setup = (actual / "setup_sample_videos.sh").read_text()
    video_path = Path(re.search(r"^\s*VIDEO_PATH=(\S+)", setup, re.M).group(1).strip("\"'"))
    assert 'OUTPUT_DIR="$SCRIPT_DIR/{}"'.format(video_path) in video_setup
    assert video_path == Path("assets/videos")
    images = subprocess.check_output(
        ["git", "-C", str(actual), "ls-tree", "-r", "--name-only", "HEAD",
         "--", "sample/img", "sample/video", "sample/videos"], text=True).splitlines()
    assert images and all(path.startswith("sample/img/") for path in images)

    # Materialize the SDK's Git image blobs, not placeholders or the developer's
    # already-installed assets, into a fresh checkout-shaped fixture.
    root = tmp_path / "app"
    root.mkdir()
    image_data = {}
    for relative in images:
        image_data[relative] = subprocess.check_output(
            ["git", "-C", str(actual), "show", "HEAD:" + relative])
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(image_data[relative])
    (root / "setup.sh").write_text(setup)
    (root / "setup_sample_videos.sh").write_text(video_setup)
    manifest = json.loads((actual / "scripts" / "modelzoo_manifest.json").read_text())
    (root / "scripts").mkdir()
    (root / "scripts" / "modelzoo_manifest.json").write_text(json.dumps(manifest[:1]))

    module = assets()
    gallery = importlib.import_module("dx_app.core.assets")
    config = importlib.import_module("dx_app.core.config")
    assert config.SAMPLE_DIR == config.DX_APP_ROOT / "sample"
    assert config.ASSETS_DIR == config.DX_APP_ROOT / "assets"
    default_video = Path(config._DEFAULT_VIDEO)
    video_name = default_video.relative_to(video_path).as_posix()
    monkeypatch.setattr(module, "DX_APP_ROOT", root)
    monkeypatch.setenv("DOCKER_VOLUME_PATH", str(tmp_path / "volume"))
    monkeypatch.delenv("DX_APP_MODELS_DIR", raising=False)
    monkeypatch.setattr(gallery, "DX_APP_ROOT", root)
    monkeypatch.setattr(gallery, "SAMPLE_DIR", root / "sample")
    monkeypatch.setattr(gallery, "ASSETS_DIR", root / "assets")
    calls = []
    monkeypatch.setattr(module, "_open_url", opener(calls, archive([("fixture/" + video_name, b"video")])))
    assert module.main(["app"]) == 0
    assert config._DEFAULT_IMAGE in gallery.get_images()
    assert str(default_video) in gallery.get_videos()
    assert (root / default_video).read_bytes() == b"video"
    assert all((root / path).read_bytes() == body for path, body in image_data.items())
    assert not (root / "sample" / "video").exists()
    assert not (root / "sample" / "videos").exists()
    version = re.search(r'^VIDEO_VERSION="([^"]+)"', video_setup, re.M).group(1)
    source = re.search(r'^SOURCE_PATH="([^"]+)"', video_setup, re.M).group(1)
    base = re.search(r'^BASE_URL="([^"]+)"', video_setup, re.M).group(1)
    assert calls[-1] == base + source.replace("${VIDEO_VERSION}", version)
    assert len(calls) == 2  # One actual manifest entry and one tiny mocked archive.
