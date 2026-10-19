"""The SETUP page's public source reads the inline payload, not a table.

`developer.deepx.ai/modelzoo/` carries no data rows: the response has one `<table>` with two `<tr>` (the header
skeleton), and the models live in `window.__MODEL_ZOO_DATA__`. A table parser fails the 20-column detection there,
falls into the legacy branch and returns nothing.

Two things are protected here: the public source reads the payload, and the fourth tier reaches the install flow.
"""
from __future__ import annotations

from pathlib import Path

FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "dx_modelzoo"
    / "fixtures"
    / "public_modelzoo_payload.html"
)


def _models():
    from dx_app.core.modelzoo import _models_from_payload

    return _models_from_payload(FIXTURE.read_text(encoding="utf-8"))


def test_payload_yields_every_row():
    models = _models()
    assert len(models) == 8, f"픽스처 8행 중 {len(models)}건만 읽었다"


def test_each_model_carries_the_shape_dx_app_consumes():
    for m in _models():
        assert m["name"]
        assert "task" in m
        for tier in ("qlite", "qpro", "qmaster"):
            assert tier in m, f"{m['name']} 에 {tier} 블록이 없다"
            assert "dxnn_url" in m[tier]
            assert "exists" in m[tier]


def test_artifact_urls_are_absolute():
    """Artifact paths in the payload are relative to the base; the downloader needs absolute URLs."""
    seen = 0
    for m in _models():
        for tier in ("qlite", "qpro", "qmaster"):
            url = m[tier].get("dxnn_url")
            if url:
                assert url.startswith("http"), f"{m['name']}/{tier} 이 상대 경로다: {url}"
                seen += 1
    assert seen, "절대 URL 을 하나도 못 봤다"


def test_qmaster_is_none_where_the_source_has_none():
    """Only 15 of 354 models have Q-Master. Claiming one that does not exist makes the download die with 404."""
    models = _models()
    with_qm = [m for m in models if m["qmaster"].get("dxnn_url")]
    without_qm = [m for m in models if not m["qmaster"].get("dxnn_url")]
    assert with_qm, "픽스처에 Q-Master 가 있는 행이 있어야 한다"
    assert without_qm, "픽스처에 Q-Master 가 없는 행도 있어야 한다"
    for m in without_qm:
        assert m["qmaster"]["dxnn_url"] is None


def test_list_routes_public_source_to_the_payload_reader(monkeypatch):
    """If modelzoo_list(source='public') went through the table parser, it would return nothing."""
    import dx_app.core.modelzoo as mz

    monkeypatch.setattr(mz, "_fetch_page", lambda source: (FIXTURE.read_text(encoding="utf-8"), None))
    mz._cache.update({"models": [], "source": None, "ts": 0})

    result = mz.modelzoo_list(source=mz.SOURCE_PUBLIC)
    assert result["ok"], result.get("error")
    assert len(result["models"]) == 8
