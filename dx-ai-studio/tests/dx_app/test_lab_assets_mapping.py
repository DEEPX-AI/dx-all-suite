import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]

def test_get_videos_accepts_category():
    import sys; sys.path.insert(0, str(ROOT))
    from dx_app.core import assets
    all_vids = assets.get_videos()
    assert isinstance(all_vids, list)
    from dx_app.core.config import CAT_VIDEO
    cat_vid = assets.get_videos("classification")
    assert isinstance(cat_vid, list)
    override = CAT_VIDEO.get("classification")
    if override and override in all_vids:
        assert cat_vid and cat_vid[0] == override

def test_get_videos_signature_is_backcompat():
    src = (ROOT / "dx_app" / "core" / "assets.py").read_text(encoding="utf-8")
    assert "def get_videos(category=None)" in src

def test_videos_route_threads_category():
    src = (ROOT / "dx_app" / "server.py").read_text(encoding="utf-8")
    assert "get_videos(" in src
    assert "category" in src.split("/api/videos", 1)[1][:400]


# ── Compatible-asset resolver: demo default > category default > generic gallery ──
# Deterministic via monkeypatch — does not depend on run_demo.sh contents or on the
# assets/videos directory existing on disk.

def _lab_portal():
    import sys; sys.path.insert(0, str(ROOT))
    from dx_app.core import lab_portal
    return lab_portal
