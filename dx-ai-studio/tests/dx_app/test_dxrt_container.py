"""Which .dxnn container DX-RT can read, and which download to pick.

Model Zoo 2_5_0 ships container v9, and DX-RT 3.4.2 reads only 6–8 ("Model file format version 9 is not
supported"). Rather than let the run fail after the download: fetch the 2_4_0 (v8) build of the same name first, and
if there is none, download nothing and say "DX-RT 3.5 required". With DX-RT 3.5 or later the publish page default
(2_5_0) is used as is.
"""
from __future__ import annotations

import io
import struct

import pytest

from shared import dxrt
from dx_app.core import modelzoo


@pytest.fixture
def rt(monkeypatch):
    def _set(ver):
        monkeypatch.setattr(dxrt, "runtime_version", lambda: ver)
    return _set


def test_the_container_limit_follows_the_runtime(rt):
    rt((3, 4, 2))
    assert dxrt.max_container() == 8 and not dxrt.supports(9) and dxrt.supports(8)
    rt((3, 5, 0))
    assert dxrt.max_container() == 9 and dxrt.supports(9)
    rt(None)
    assert dxrt.supports(9), "모르면 막지 않는다"


def test_the_version_is_read_from_release_ver(tmp_path, monkeypatch):
    (tmp_path / "dx_rt").mkdir()
    (tmp_path / "dx_rt" / "release.ver").write_text("v3.4.2\n")
    monkeypatch.setattr(dxrt, "DX_RUNTIME_ROOT", tmp_path)
    assert dxrt.runtime_version() == (3, 4, 2)


def test_a_2_5_0_url_is_tried_as_2_4_0_first_on_an_old_runtime(rt):
    rt((3, 4, 2))
    u = "https://sdk.deepx.ai/modelzoo/q-lite-dxnn/2_5_0/yolo26-n_640x640.dxnn"
    assert dxrt.download_urls(u) == ["https://sdk.deepx.ai/modelzoo/q-lite-dxnn/2_4_0/yolo26-n_640x640.dxnn"]
    rt((3, 5, 0))
    assert dxrt.download_urls(u) == [u]
    assert dxrt.download_urls("https://sdk.deepx.ai/modelzoo/dxnn/2_4_0/SCRFD500M_PPU.dxnn") == \
        ["https://sdk.deepx.ai/modelzoo/dxnn/2_4_0/SCRFD500M_PPU.dxnn"]


class _Resp(io.BytesIO):
    def __init__(self, status, body=b""):
        super().__init__(body)
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _run(monkeypatch, tmp_path, responses):
    """responses: url → (status, body)."""
    import urllib.error

    def _open(opener, url, timeout):
        status, body = responses.get(url, (404, b""))
        if status != 200:
            raise urllib.error.HTTPError(url, status, "x", None, None)
        return _Resp(status, body)

    monkeypatch.setattr(modelzoo, "_open", _open)
    monkeypatch.setattr(modelzoo, "_make_opener", lambda source: None)
    monkeypatch.setattr(modelzoo, "_auto_register", lambda: None)
    monkeypatch.setattr(modelzoo, "_CHIP_DIRS", {"qlite": (tmp_path, "assets/models")})
    tasks = modelzoo._build_tasks([{"name": "m", "chip": "qlite",
                                    "dxnn_url": "https://sdk.deepx.ai/modelzoo/q-lite-dxnn/2_5_0/m_640x640.dxnn"}])
    modelzoo._reset_dl_state()
    modelzoo._download_worker(tasks, "public")
    return modelzoo.modelzoo_status()["results"]


V8 = b"DXNN" + struct.pack("<I", 8) + b"body"


def test_an_old_runtime_gets_the_v8_file_when_there_is_one(rt, monkeypatch, tmp_path):
    rt((3, 4, 2))
    res = _run(monkeypatch, tmp_path, {"https://sdk.deepx.ai/modelzoo/q-lite-dxnn/2_4_0/m_640x640.dxnn": (200, V8)})
    assert res[0]["status"] == "ok", res
    assert (tmp_path / "m_640x640.dxnn").read_bytes() == V8


def test_an_old_runtime_does_not_download_a_v9_only_model(rt, monkeypatch, tmp_path):
    rt((3, 4, 2))
    res = _run(monkeypatch, tmp_path, {
        "https://sdk.deepx.ai/modelzoo/q-lite-dxnn/2_5_0/m_640x640.dxnn": (200, b"DXNN" + struct.pack("<I", 9))})
    assert res[0]["status"] == "needs_dxrt" and res[0]["needs_dxrt"] == dxrt.NEEDS_FOR_V9, res
    assert not (tmp_path / "m_640x640.dxnn").exists()


def test_a_v9_model_on_disk_is_marked_not_runnable(rt, tmp_path):
    rt((3, 4, 2))
    p = tmp_path / "x.dxnn"
    p.write_bytes(b"DXNN" + struct.pack("<I", 9))
    assert dxrt.needs_for_file(p) == dxrt.NEEDS_FOR_V9
    p.write_bytes(V8)
    assert dxrt.needs_for_file(p) is None
