"""Artifact validation and server endpoint tests."""
import json
import urllib.request
import sys
import pytest
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError

MODULE_DIR = Path(__file__).resolve().parent.parent.parent / "dx_modelzoo"
TEST_PORT = 18095




def test_validate_artifact_id_accepts_known():
    from dx_modelzoo.metadata.artifacts import validate_artifact_id
    assert validate_artifact_id("qlite_dxnn") == "qlite_dxnn"
    assert validate_artifact_id("onnx") == "onnx"
    assert validate_artifact_id("qpro_json") == "qpro_json"


def test_validate_artifact_id_rejects_unknown():
    from dx_modelzoo.metadata.artifacts import validate_artifact_id
    assert validate_artifact_id("qlite_dxnn") == "qlite_dxnn"
    try:
        validate_artifact_id("../secret")
    except ValueError as e:
        assert "unknown_artifact" in str(e)
    else:
        raise AssertionError("expected ValueError")


def test_validate_artifact_id_rejects_empty():
    from dx_modelzoo.metadata.artifacts import validate_artifact_id
    try:
        validate_artifact_id("")
    except ValueError as e:
        assert "unknown_artifact" in str(e)
    else:
        raise AssertionError("expected ValueError")


def test_safe_local_artifact_path_rejects_traversal(tmp_path):
    from dx_modelzoo.metadata.artifacts import safe_local_artifact_path
    root = tmp_path / "assets"
    root.mkdir()
    assert safe_local_artifact_path(root, "models/AlexNet.dxnn").is_relative_to(root)
    for bad in ("../secret", "/etc/passwd"):
        try:
            safe_local_artifact_path(root, bad)
        except ValueError as e:
            assert "unsafe_artifact_path" in str(e)
        else:
            raise AssertionError("expected ValueError")


def test_safe_local_artifact_path_rejects_symlink_escape(tmp_path):
    from dx_modelzoo.metadata.artifacts import safe_local_artifact_path
    root = tmp_path / "assets"
    root.mkdir()
    # try to escape through a symlink
    link = root / "escape"
    link.symlink_to(tmp_path.parent)
    try:
        safe_local_artifact_path(root, "escape/secret.txt")
    except ValueError as e:
        assert "unsafe_artifact_path" in str(e)
    else:
        raise AssertionError("expected ValueError")


def test_validate_remote_url_allowlist_blocks_ssrf():
    from dx_modelzoo.metadata.artifacts import validate_remote_url
    assert validate_remote_url("https://sdk.deepx.ai/modelzoo/dxnn/AlexNet.dxnn", "internal")
    for bad in ("http://127.0.0.1/admin", "https://evil.example/AlexNet.dxnn"):
        try:
            validate_remote_url(bad, "internal")
        except ValueError as e:
            assert "unsafe_artifact_url" in str(e)
        else:
            raise AssertionError("expected ValueError")


def test_validate_remote_url_allows_internal_hosts():
    from dx_modelzoo.metadata.artifacts import validate_remote_url
    for url in (
        "https://modelzoo-api.devops.dpx.ai/v1/models/alexnet/qlite",
        "https://modelzoo-publish-api.devops.dpx.ai/models/alexnet.dxnn",
        "https://sdk.deepx.ai/modelzoo/dxnn/AlexNet.dxnn",
    ):
        assert validate_remote_url(url, "internal")


def test_validate_remote_url_rejects_private_ips():
    from dx_modelzoo.metadata.artifacts import validate_remote_url
    for bad in (
        "http://127.0.0.1/admin",
        "http://localhost:8080/secret",
        "http://10.0.0.1/internal",
        "http://192.168.1.1/admin",
        "https://[::1]/secret",
        "https://[::ffff:127.0.0.1]/secret",
        "https://[fd00::1]/secret",
    ):
        try:
            validate_remote_url(bad, "public")
        except ValueError as e:
            assert "unsafe_artifact_url" in str(e)
        else:
            raise AssertionError(f"expected ValueError for {bad}")


def test_validate_remote_url_rejects_non_https():
    from dx_modelzoo.metadata.artifacts import validate_remote_url
    try:
        validate_remote_url("http://sdk.deepx.ai/modelzoo/dxnn/AlexNet.dxnn", "public")
    except ValueError as e:
        assert "unsafe_artifact_url" in str(e)
    else:
        raise AssertionError("expected ValueError")




def _load_create_server():
    sys.modules.pop("server", None)
    sys.path.insert(0, str(MODULE_DIR))
    try:
        from server import create_server
    finally:
        sys.path.remove(str(MODULE_DIR))
    return create_server


@pytest.fixture(scope="module")
def server():
    """Start/stop a server for the tests."""
    import threading, time
    create_server = _load_create_server()
    srv = create_server(TEST_PORT)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    for _ in range(20):
        try:
            urlopen(f"http://127.0.0.1:{TEST_PORT}/api/categories", timeout=1)
            break
        except Exception:
            time.sleep(0.2)
    yield srv
    srv.shutdown()
    srv.server_close()
    sys.modules.pop("server", None)




def test_safe_local_artifact_path_accepts_double_dot_in_filename(tmp_path):
    """A valid file name such as model..v2.dxnn must be accepted."""
    from dx_modelzoo.metadata.artifacts import safe_local_artifact_path
    root = tmp_path / "assets"
    root.mkdir()
    # a file name containing '..' that is not a traversal
    result = safe_local_artifact_path(root, "models/model..v2.dxnn")
    assert result.is_relative_to(root)
    assert result.name == "model..v2.dxnn"




def test_resolve_artifact_blocks_internal_host_even_with_local_profile():
    """Internal host URLs must not be exposed, even with source_profile='local'."""
    from dx_modelzoo.metadata.artifacts import resolve_artifact
    model = {
        "id": "TestModel",
        "artifacts": {
            "qlite_dxnn": {
                "remote_url": "https://modelzoo-api.devops.dpx.ai/modelzoo/api/files/AlexNet.dxnn",
            }
        }
    }
    result = resolve_artifact(model, "qlite_dxnn", source_profile="local")
    assert not result["available"], "internal host URL should not be available"
    assert result.get("url") is None, "internal host URL must not be returned"


def test_resolve_artifact_allows_public_host_with_local_profile():
    """Public host URLs must be allowed with source_profile='local'."""
    from dx_modelzoo.metadata.artifacts import resolve_artifact
    model = {
        "id": "TestModel",
        "artifacts": {
            "qlite_dxnn": {
                "remote_url": "https://sdk.deepx.ai/modelzoo/dxnn/AlexNet.dxnn",
            }
        }
    }
    result = resolve_artifact(model, "qlite_dxnn", source_profile="local")
    assert result["available"]
    assert result["url"] == "https://sdk.deepx.ai/modelzoo/dxnn/AlexNet.dxnn"


class TestArtifactEndpoints:
    def test_artifact_endpoint_rejects_unknown_artifact(self, server):
        # get a valid model ID first
        resp = urlopen(f"http://127.0.0.1:{TEST_PORT}/api/catalog")
        data = json.loads(resp.read())
        if not data["models"]:
            pytest.skip("No models loaded")
        model_id = data["models"][0]["id"]
        try:
            urlopen(f"http://127.0.0.1:{TEST_PORT}/api/catalog/{model_id}/artifacts/not_real")
        except HTTPError as e:
            body = json.loads(e.read())
            assert e.code == 404
            assert body["error_code"] == "unknown_artifact"
        else:
            raise AssertionError("expected HTTPError")

    def test_artifact_endpoint_rejects_unknown_model(self, server):
        try:
            urlopen(f"http://127.0.0.1:{TEST_PORT}/api/catalog/nonexistent_xyz/artifacts/qlite_dxnn")
        except HTTPError as e:
            body = json.loads(e.read())
            assert e.code == 404
            assert body["error_code"] == "unknown_model"
        else:
            raise AssertionError("expected HTTPError")

    def test_artifact_endpoint_unavailable_artifact(self, server):
        resp = urlopen(f"http://127.0.0.1:{TEST_PORT}/api/catalog")
        data = json.loads(resp.read())
        if not data["models"]:
            pytest.skip("No models loaded")
        model_id = data["models"][0]["id"]
        # Do not follow redirects. For a remote artifact the server answers 302 to the CDN;
        # urlopen would follow it, so without internet the test would fail even though the
        # server answered correctly. What matters is the server's response, not the CDN.
        class _NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *args, **kwargs):
                return None

        opener = urllib.request.build_opener(_NoRedirect)
        try:
            resp = opener.open(
                f"http://127.0.0.1:{TEST_PORT}/api/catalog/{model_id}/artifacts/onnx")
            assert resp.status in (200, 302)
        except HTTPError as e:
            if e.code == 404:
                body = json.loads(e.read())
                assert body["error_code"] == "artifact_unavailable"
            else:
                assert e.code in (302, 303, 307), f"예상 밖 응답: {e.code}"

    def test_artifact_endpoint_rejects_traversal(self, server):
        try:
            urlopen(f"http://127.0.0.1:{TEST_PORT}/api/catalog/..%2F..%2Fetc/artifacts/qlite_dxnn")
        except HTTPError as e:
            assert e.code in (400, 404)
        else:
            raise AssertionError("expected HTTPError")
