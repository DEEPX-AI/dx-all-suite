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


def test_compatible_composer_assets_prefers_demo_default(monkeypatch):
    lab_portal = _lab_portal()
    monkeypatch.setattr(
        lab_portal,
        "build_demos_payload",
        lambda: {"demos": [{
            "run_ref": {"category": "classification", "model_name": "resnet18"},
            "default_image": "sample/img/resnet_demo.jpg",
            "default_video": "assets/videos/resnet_demo.mp4",
        }]},
    )
    monkeypatch.setattr(
        lab_portal,
        "get_images",
        lambda category=None: ["sample/img/alpha.jpg", "sample/img/resnet_demo.jpg", "sample/img/beta.jpg"],
    )

    assets, preferred = lab_portal._compatible_composer_assets("classification", "image", "resnet18")

    assert preferred == "sample/img/resnet_demo.jpg"
    assert assets[0] == "sample/img/resnet_demo.jpg"
    assert set(assets) == {"sample/img/alpha.jpg", "sample/img/resnet_demo.jpg", "sample/img/beta.jpg"}
    generic = not (preferred and preferred in assets)
    assert generic is False


def test_compatible_composer_assets_falls_back_to_category_default(monkeypatch):
    lab_portal = _lab_portal()
    from dx_app.core.config import CAT_IMAGE

    # No demo matches this (model_name, category) — resolver should fall to CAT_IMAGE.
    monkeypatch.setattr(lab_portal, "build_demos_payload", lambda: {"demos": []})
    category_default = CAT_IMAGE["classification"]
    monkeypatch.setattr(
        lab_portal,
        "get_images",
        lambda category=None: ["sample/img/alpha.jpg", category_default, "sample/img/beta.jpg"],
    )

    assets, preferred = lab_portal._compatible_composer_assets("classification", "image", "resnet18")

    assert preferred == category_default
    assert assets[0] == category_default
    generic = not (preferred and preferred in assets)
    assert generic is False


def test_compatible_composer_assets_generic_fallback(monkeypatch):
    lab_portal = _lab_portal()

    # No demo match, and the category default isn't among the installed/compatible
    # assets — resolver has nothing precise to prefer and must mark the result generic.
    monkeypatch.setattr(lab_portal, "build_demos_payload", lambda: {"demos": []})
    monkeypatch.setattr(
        lab_portal,
        "get_images",
        lambda category=None: ["sample/img/alpha.jpg", "sample/img/beta.jpg"],
    )

    assets, preferred = lab_portal._compatible_composer_assets("classification", "image", "resnet18")

    assert assets == ["sample/img/alpha.jpg", "sample/img/beta.jpg"]
    generic = not (preferred and preferred in assets)
    assert generic is True


def test_preferred_default_asset_demo_beats_category(monkeypatch):
    lab_portal = _lab_portal()
    monkeypatch.setattr(
        lab_portal,
        "build_demos_payload",
        lambda: {"demos": [{
            "run_ref": {"category": "classification", "model_name": "resnet18"},
            "default_image": "sample/img/resnet_demo.jpg",
        }]},
    )
    assert lab_portal._preferred_default_asset("resnet18", "classification", "image") == "sample/img/resnet_demo.jpg"

    monkeypatch.setattr(lab_portal, "build_demos_payload", lambda: {"demos": []})
    from dx_app.core.config import CAT_IMAGE
    assert lab_portal._preferred_default_asset("resnet18", "classification", "image") == CAT_IMAGE["classification"]
