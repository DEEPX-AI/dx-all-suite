import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]


def test_capabilities_templates_expose_category_and_input_kind():
    import sys; sys.path.insert(0, str(ROOT))
    from dx_app.core import lab_portal
    caps = lab_portal.lab_capabilities()
    tpls = caps["composer"]["templates"]
    # each template entry must carry category (may be None for input-kind templates) and input_kind
    vals = tpls.values() if isinstance(tpls, dict) else tpls
    assert vals, "templates payload empty"
    for t in vals:
        assert "input_kind" in t
        assert "category" in t


def test_category_less_template_with_explicit_model_does_not_falsely_mismatch(monkeypatch):
    """`video`/`camera` templates carry no category constraint (category is None) — an
    explicit model of ANY category must proceed normally, never be rejected as a
    template_model_mismatch (the guard must skip the comparison when the template's
    category is None)."""
    import lab_portal
    from developer import lab_session

    classification_model = {
        "name": "resnet18",
        "category": "classification",
        "model_file": "assets/models/resnet18_224x224.dxnn",
        "model_exists": True,
        "cpp_sync": True,
    }
    monkeypatch.setattr(lab_portal, "get_models", lambda: [classification_model], raising=False)
    monkeypatch.setattr(lab_portal, "get_images", lambda category: [], raising=False)
    monkeypatch.setattr(
        lab_portal, "get_videos", lambda *a, **k: ["sample/video/sample.mp4"], raising=False
    )
    token = lab_session()["token"]

    result, code = lab_portal.plan_composer_template(
        token, {"template_id": "video", "model_name": "resnet18"},
    )

    assert code == 200
    assert "error_code" not in result
    assert result["workflow"]["model"]["name"] == "resnet18"
