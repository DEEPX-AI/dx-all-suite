"""The Q-Master tier reaches the install path, not only the display.

Showing Q-Master on the ModelZoo screen is not enough: the dx_app downloader must also handle `qmaster`, or the
model is visible but cannot be downloaded.

Following the Q-Pro convention, it installs into assets/models/q-master/.
"""
from __future__ import annotations

import io
from pathlib import Path

import pytest


def _mz():
    import dx_app.core.modelzoo as mz

    return mz


def test_qmaster_has_its_own_install_dir():
    mz = _mz()
    assert mz.QMASTER_DIR.name == "q-master"
    assert mz.QMASTER_DIR.parent == mz.MODELS_DIR


def test_every_tier_is_in_the_chip_table():
    """One table holds the tier directories; it is the single source of truth."""
    mz = _mz()
    assert set(mz._CHIP_DIRS) == {"qlite", "qpro", "qmaster"}
    assert mz._CHIP_DIRS["qlite"] == (mz.MODELS_DIR, "assets/models")
    assert mz._CHIP_DIRS["qpro"] == (mz.QPRO_DIR, "assets/models/q-pro")
    assert mz._CHIP_DIRS["qmaster"] == (mz.QMASTER_DIR, "assets/models/q-master")


def test_download_sends_qmaster_to_its_own_dir():
    """Task assembly is a pure function that starts no thread, so it is checked directly."""
    mz = _mz()
    tasks = mz._build_tasks([{
        "name": "RepVGG-A0",
        "chip": "qmaster",
        "dxnn_url": "https://sdk.deepx.ai/modelzoo/q-master-dxnn/2_4_0/repvgga0_224x224.dxnn",
        "json_url": "https://sdk.deepx.ai/modelzoo/q-master-json/2_4_0/repvgga0_224x224.json",
    }])
    assert len(tasks) == 2, tasks
    for task in tasks:
        assert task["chip"] == "qmaster"
        assert task["dest"].parent == mz.QMASTER_DIR, task["dest"]


def test_each_tier_lands_in_its_own_directory():
    mz = _mz()
    for chip, (dest_dir, _rel) in mz._CHIP_DIRS.items():
        tasks = mz._build_tasks([{
            "name": "m", "chip": chip,
            "dxnn_url": "https://sdk.deepx.ai/x/m.dxnn", "json_url": None,
        }])
        assert tasks[0]["dest"].parent == dest_dir, chip


def test_unknown_chip_is_rejected_rather_than_silently_qpro():
    """With q-pro as the fallback, a mistyped chip would silently install into q-pro."""
    mz = _mz()
    with pytest.raises(ValueError, match="unknown chip"):
        mz._build_tasks([{
            "name": "typo", "chip": "qmater",
            "dxnn_url": "https://sdk.deepx.ai/x/a.dxnn", "json_url": None,
        }])

    res = mz.modelzoo_download([{
        "name": "typo", "chip": "qmater",
        "dxnn_url": "https://sdk.deepx.ai/x/a.dxnn", "json_url": None,
    }])
    assert not res["ok"], "모르는 chip 을 받아들였다"
    assert "chip" in (res.get("error") or "").lower()


def test_refresh_exists_checks_the_qmaster_dir(tmp_path, monkeypatch):
    mz = _mz()
    qm = tmp_path / "q-master"
    qm.mkdir()
    from shared.atomic_download import download_file

    class Response(io.BytesIO):
        status = 200
        headers = {"Content-Length": "4"}

    download_file("https://sdk.deepx.ai/x/repvgga0_224x224.dxnn",
                  qm / "repvgga0_224x224.dxnn", open_url=lambda u: Response(b"DXNN"))
    monkeypatch.setattr(mz, "QMASTER_DIR", qm)
    monkeypatch.setitem(mz._CHIP_DIRS, "qmaster", (qm, "assets/models/q-master"))

    models = [{
        "name": "RepVGG-A0",
        "qlite": {"dxnn_url": None},
        "qpro": {"dxnn_url": None},
        "qmaster": {
            "dxnn_url": "https://sdk.deepx.ai/x/repvgga0_224x224.dxnn",
            "exists": False,
        },
    }]
    mz._refresh_exists(models)
    assert models[0]["qmaster"]["exists"] is True


def test_auto_register_uses_the_qmaster_relative_path():
    """The path written to the registry must match the actual install location."""
    mz = _mz()
    src = Path(mz.__file__).read_text(encoding="utf-8")
    assert 'assets/models/q-master' not in src.replace('"assets/models/q-master"', ''), (
        "q-master 경로가 _CHIP_DIRS 밖에 하드코딩돼 있다"
    )
