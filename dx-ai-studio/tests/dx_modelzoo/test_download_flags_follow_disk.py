"""A finished download shows as downloaded without a restart.

If `downloaded` were computed once at first catalogue load and cached for the life of the server, a model
downloaded from its detail page would stay "Download the model first" with Run Inference disabled, even after a reload.
"""
from __future__ import annotations

import importlib


def test_the_download_flags_follow_the_disk(tmp_path, monkeypatch):
    cat = importlib.import_module("dx_modelzoo.core.catalog")
    app = tmp_path / "dx_app"
    (app / "assets" / "models").mkdir(parents=True)
    monkeypatch.setattr(cat, "DX_APP_ROOT", app)
    fake = {"models": [{"id": "m1", "model_file": "assets/models/m1.dxnn", "model_file_qpro": "",
                        "downloaded": False, "downloaded_qlite": False, "downloaded_qpro": False}]}
    monkeypatch.setattr(cat, "_catalog_cache", fake)
    now = [1000.0]
    monkeypatch.setattr(cat.time, "time", lambda: now[0])
    monkeypatch.setattr(cat, "_flags_checked_at", 0.0, raising=False)

    assert cat.get_catalog()["models"][0]["downloaded"] is False
    (app / "assets" / "models" / "m1.dxnn").write_bytes(b"DXNN")
    now[0] += 5
    m = cat.get_catalog()["models"][0]
    assert m["downloaded"] is True and m["downloaded_qlite"] is True and m["downloaded_qpro"] is False
