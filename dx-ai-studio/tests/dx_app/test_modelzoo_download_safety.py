"""ModelZoo uses the same verified atomic transfer as sample setup."""
import io

import pytest

from dx_app.core import modelzoo


class Response(io.BytesIO):
    status = 200

    def __init__(self, body=b"model", length="5", cancel=False):
        super().__init__(body)
        self.headers = {} if length is None else {"Content-Length": length}
        self.cancel = cancel

    def read(self, size=-1):
        data = super().read(size)
        if self.cancel:
            modelzoo._dl_state["cancel"] = True
        return data


def run(monkeypatch, tmp_path, response):
    monkeypatch.setattr(modelzoo, "_make_opener", lambda source: None)
    monkeypatch.setattr(modelzoo, "_open", lambda *args: response)
    monkeypatch.setattr(modelzoo, "_auto_register", lambda: None)
    monkeypatch.setattr(modelzoo, "_CHIP_DIRS", {"qlite": (tmp_path, "assets/models")})
    tasks = modelzoo._build_tasks([{"name": "model", "chip": "qlite",
                                    "dxnn_url": "https://sdk.deepx.ai/models/model.dxnn"}])
    modelzoo._reset_dl_state()
    modelzoo._download_worker(tasks, "public")
    return modelzoo.modelzoo_status()


@pytest.mark.parametrize("body,length", [(b"bad", "12"), (b"", "0"), (b"model", None)])
def test_unverified_download_never_replaces_good_model(monkeypatch, tmp_path, body, length):
    target = tmp_path / "model.dxnn"
    target.write_bytes(b"good-old")
    status = run(monkeypatch, tmp_path, Response(body, length))
    assert status["results"][0]["status"] == "error", status
    assert target.read_bytes() == b"good-old"
    assert status["finished"] and not status["running"]
    assert not list(tmp_path.glob("*.part"))


def test_stale_final_file_is_refreshed(monkeypatch, tmp_path):
    target = tmp_path / "model.dxnn"
    target.write_bytes(b"bad")
    status = run(monkeypatch, tmp_path, Response())
    assert status["results"][0]["status"] == "ok"
    assert target.read_bytes() == b"model"


def test_cancellation_preserves_old_model_and_finishes_state(monkeypatch, tmp_path):
    target = tmp_path / "model.dxnn"
    target.write_bytes(b"good-old")
    status = run(monkeypatch, tmp_path, Response(cancel=True))
    assert status["results"][0]["status"] == "cancelled"
    assert target.read_bytes() == b"good-old"
    assert status["finished"] and not status["running"]


def test_modelzoo_requests_identity_even_with_custom_opener():
    requests = []

    class Opener:
        def open(self, request, timeout):
            requests.append(request)

    modelzoo._open(Opener(), "https://example/model.dxnn", 120)
    assert requests[0].get_header("Accept-encoding") == "identity"


def test_unverified_fallback_is_not_misreported_as_runtime_requirement(monkeypatch, tmp_path):
    from shared import dxrt
    monkeypatch.setattr(dxrt, "runtime_version", lambda: (3, 4, 2))
    monkeypatch.setattr(dxrt, "download_urls",
                        lambda url: [url.replace("/models/", "/2_4_0/")])
    monkeypatch.setattr(dxrt, "is_v9_only", lambda url: True)
    status = run(monkeypatch, tmp_path, Response(b"bad", "10"))
    result = status["results"][0]
    assert result["status"] == "error"
    assert "Incomplete" in result["error"]


def test_opener_failure_finishes_state(monkeypatch, tmp_path):
    def fail(source):
        raise OSError("invalid proxy CA")

    monkeypatch.setattr(modelzoo, "_make_opener", fail)
    monkeypatch.setattr(modelzoo, "_auto_register", lambda: None)
    modelzoo._reset_dl_state()
    modelzoo._dl_state["running"] = True
    modelzoo._download_worker([], "internal")
    status = modelzoo.modelzoo_status()
    assert status["finished"] and not status["running"]
    assert "invalid proxy CA" in status["results"][0]["error"]


def test_a_downloaded_file_without_a_record_is_shown_downloaded_but_unverified(monkeypatch, tmp_path):
    """Already-downloaded models (e.g. by the SDK's own downloader) are not "not downloaded";
    without a Studio record they are flagged unverified so the user can verify them."""
    monkeypatch.setattr(modelzoo, "_CHIP_DIRS", {"qlite": (tmp_path, "assets/models")})
    (tmp_path / "model.dxnn").write_bytes(b"from elsewhere")
    models = [{"qlite": {"dxnn_url": "https://example/model.dxnn", "exists": False}}]
    modelzoo._refresh_exists(models)
    assert models[0]["qlite"]["exists"] is True
    assert models[0]["qlite"]["install_state"] == "unverified"
    (tmp_path / "model.dxnn").unlink()
    modelzoo._refresh_exists(models)
    assert models[0]["qlite"]["exists"] is False
    assert models[0]["qlite"]["install_state"] == "missing"


def test_public_payload_tier_reports_an_unrecorded_file_as_unverified(monkeypatch, tmp_path):
    monkeypatch.setattr(modelzoo, "_CHIP_DIRS", {"qlite": (tmp_path, "assets/models")})
    (tmp_path / "model.dxnn").write_bytes(b"from elsewhere")
    tier = modelzoo._tier_block({"artifacts": {"qlite_dxnn": "https://example/model.dxnn"}}, "qlite")
    assert tier["exists"] is True and tier["install_state"] == "unverified"


def test_installed_receipt_is_cheap_and_metadata_sidecar_is_required(monkeypatch, tmp_path):
    run(monkeypatch, tmp_path, Response())
    models = [{"qlite": {"dxnn_url": "https://example/model.dxnn",
                         "json_url": "https://example/model.json"}}]
    monkeypatch.setattr(modelzoo, "_open", lambda *args: pytest.fail("readiness must not use network"))
    modelzoo._refresh_exists(models)
    assert models[0]["qlite"]["exists"] is False, "Manifest sidecar is still missing"
    from shared.atomic_download import download_file
    download_file("https://example/model.json", tmp_path / "model.json", open_url=lambda u: Response())
    modelzoo._refresh_exists(models)
    assert models[0]["qlite"]["exists"] is True
    assert models[0]["qlite"]["install_state"] == "verified"
