"""The exporter writes every card file, reports gaps, and --check catches drift."""
import json

from PIL import Image

from dx_modelzoo.tools import export_dx_app_cards as ex
from tests.dx_modelzoo.test_model_card import MODEL, ROW


def _tree(tmp_path):
    app = tmp_path / "dx_app"
    (app / "config").mkdir(parents=True)
    (app / "scripts").mkdir()
    (app / "config/model_registry.json").write_text(json.dumps([ROW]), encoding="utf-8")
    (app / "scripts/modelzoo_manifest.json").write_text(json.dumps([{"name": "yolov5m_face"}]), encoding="utf-8")
    py = app / "src/python_example/face_detection/yolov5_face/yolov5-m-face_640x640"
    py.mkdir(parents=True)
    (py / "config.json").write_text(json.dumps({"default_image": "sample/img/sample_face.jpg"}), encoding="utf-8")
    (app / "src/cpp_example/face_detection/yolov5_face/yolov5-m-face_640x640").mkdir(parents=True)
    data = tmp_path / "data"
    (data / "examples").mkdir(parents=True)
    Image.new("RGB", (64, 48), "gray").save(data / "examples/yolov5m_face_result.jpg")
    model = dict(MODEL, demo={"python_example": "src/python_example/face_detection/yolov5_face/yolov5-m-face_640x640/"},
                 example_images={"result": "examples/yolov5m_face_result.jpg"})
    return app, data, model


def test_outputs_and_report(tmp_path):
    app, data, model = _tree(tmp_path)
    outputs, report = ex.build_outputs(app, [model], {"face_detection": {"label_en": "Face Detection"}}, [], data,
                                       "2026-10-13")
    py = "src/python_example/face_detection/yolov5_face/yolov5-m-face_640x640"
    cpp = "src/cpp_example/face_detection/yolov5_face/yolov5-m-face_640x640"
    # No card index in dx_app: the cards and MODELS.md only.
    assert set(outputs) == {f"{py}/README.md", f"{py}/model.html", f"{py}/result.webp", f"{cpp}/README.md",
                            "MODELS.md"}
    assert "https://sdk.deepx.ai/modelzoo/q-lite-dxnn/2_5_0/yolov5-m-face_640x640.dxnn" in outputs[f"{py}/README.md"].decode()
    assert report["count"] == 1 and report["setup_name_missing"] == [] and report["missing_image"] == []
    assert report["metric_count_mismatch"] == [] and report["no_python_dir"] == []
    page = outputs[f"{py}/model.html"].decode()
    assert 'href="../../../../cpp_example/face_detection/yolov5_face/yolov5-m-face_640x640/README.md"' in page
    # dx_app examples carry no benchmark numbers (FPS, FPS/W, board measurements)
    assert "FPS" not in page and "FPS" not in outputs["MODELS.md"].decode()
    assert "FPS" not in outputs[f"{py}/README.md"].decode() and "FPS" not in outputs[f"{cpp}/README.md"].decode()


def test_missing_dirs_are_reported_not_created(tmp_path):
    import shutil

    app, data, model = _tree(tmp_path)
    shutil.rmtree(app / "src/cpp_example")
    outputs, report = ex.build_outputs(app, [model], {}, [], data, "2026-10-13")
    py = "src/python_example/face_detection/yolov5_face/yolov5-m-face_640x640"
    assert not any(k.startswith("src/cpp_example") for k in outputs)
    assert "cpp_example" not in outputs[f"{py}/model.html"].decode()
    assert "C++ version" not in outputs[f"{py}/README.md"].decode()
    assert "[C++]" not in outputs["MODELS.md"].decode()
    shutil.rmtree(app / "src/python_example")
    outputs, report = ex.build_outputs(app, [model], {}, [], data, "2026-10-13")
    assert report["no_python_dir"] == ["yolov5-m-face_640x640"] and report["count"] == 0
    assert not any(k.startswith("src/") for k in outputs)


def test_glued_metric_names_are_reported(tmp_path):
    app, data, model = _tree(tmp_path)
    model["specification"] = dict(model["specification"], metric={"name": "AP(Easy)AP(Med)AP(Hard)"})
    _, report = ex.build_outputs(app, [model], {}, [], data, "2026-10-13")
    assert report["metric_count_mismatch"] == ["yolov5-m-face_640x640: 1 metric names, 3 values"]


def test_main_needs_the_catalog_date(tmp_path, monkeypatch, capsys):
    import pytest

    from dx_modelzoo.core import catalog
    monkeypatch.setattr(catalog, "get_catalog", lambda: {"models": [], "categories": {}})
    monkeypatch.setattr(catalog, "load_generated_catalog", lambda: {})
    with pytest.raises(SystemExit) as exit_:
        ex.main(["--dx-app", str(tmp_path), "--check"])
    assert exit_.value.code == 2 and "generated_at" in capsys.readouterr().err


def test_write_then_check_is_clean_and_drift_is_caught(tmp_path):
    app, data, model = _tree(tmp_path)
    outputs, _ = ex.build_outputs(app, [model], {}, [], data, "2026-10-13")
    ex.write_outputs(app, outputs)
    assert ex.changed_outputs(app, outputs) == []
    (app / "MODELS.md").write_text("edited", encoding="utf-8")
    assert ex.changed_outputs(app, outputs) == ["MODELS.md"]


def test_only_skips_the_index(tmp_path):
    app, data, model = _tree(tmp_path)
    outputs, _ = ex.build_outputs(app, [model], {}, [], data, "2026-10-13", only={"yolov5-m-face_640x640"})
    assert "MODELS.md" not in outputs


def test_setup_name_comes_from_the_manifest_row_for_the_same_file(tmp_path):
    # download_models.py matches --models against the manifest name (case-insensitive); the registry's
    # model_name can differ from it (e.g. yolov5m_6_1 vs YoloV5M_6.1), so the card uses the manifest's name.
    app, data, model = _tree(tmp_path)
    (app / "scripts/modelzoo_manifest.json").write_text(json.dumps([{
        "name": "YoloV5M_Face.v2",
        "dxnn_url": "https://sdk.deepx.ai/modelzoo/q-lite-dxnn/2_5_0/yolov5-m-face_640x640.dxnn"}]), encoding="utf-8")
    outputs, report = ex.build_outputs(app, [model], {}, [], data, "2026-10-13")
    py = "src/python_example/face_detection/yolov5_face/yolov5-m-face_640x640"
    assert "./setup_sample_models.sh --models YoloV5M_Face.v2" in outputs[f"{py}/README.md"].decode()
    assert report["setup_name_missing"] == []


def test_setup_name_check_ignores_case(tmp_path):
    app, data, model = _tree(tmp_path)
    (app / "scripts/modelzoo_manifest.json").write_text(json.dumps([{"name": "YOLOv5m_Face"}]), encoding="utf-8")
    _, report = ex.build_outputs(app, [model], {}, [], data, "2026-10-13")
    assert report["setup_name_missing"] == []


def test_dead_download_links_are_dropped_and_reported(tmp_path):
    app, data, model = _tree(tmp_path)
    dead = {"https://sdk.deepx.ai/modelzoo/q-lite-json/2_5_0/yolov5-m-face_640x640.json": 404,
            "https://sdk.deepx.ai/modelzoo/q-pro-dxnn/2_4_0/yolov5-m-face_640x640.dxnn": 403}
    asked = []

    def url_ok(url):
        asked.append(url)
        status = dead.get(url, 200)
        return status == 200, status

    outputs, report = ex.build_outputs(app, [model], {}, [], data, "2026-10-13", url_ok=url_ok)
    card = outputs["src/python_example/face_detection/yolov5_face/yolov5-m-face_640x640/README.md"].decode()
    assert "q-lite-dxnn/2_5_0/yolov5-m-face_640x640.dxnn" in card      # Q-Pro's dxnn is dead: the tier goes
    assert "https://sdk.deepx.ai/modelzoo/onnx/yolov5-m-face_640x640.onnx" in card
    assert sorted(report["dead_urls"]) == ["https://sdk.deepx.ai/modelzoo/q-lite-json/2_5_0/yolov5-m-face_640x640.json",
                                           "https://sdk.deepx.ai/modelzoo/q-pro-dxnn/2_4_0/yolov5-m-face_640x640.dxnn"]
    assert sorted(report["dead_links"]) == [
        "yolov5-m-face_640x640: https://sdk.deepx.ai/modelzoo/q-lite-json/2_5_0/yolov5-m-face_640x640.json (404)",
        "yolov5-m-face_640x640: https://sdk.deepx.ai/modelzoo/q-pro-dxnn/2_4_0/yolov5-m-face_640x640.dxnn (403)",
    ]
    assert len(asked) == len(set(asked)) == 4                          # each URL once
    readme = outputs["src/python_example/face_detection/yolov5_face/yolov5-m-face_640x640/README.md"].decode()
    assert "q-pro-dxnn" not in readme and "q-lite-json" not in readme


def test_dead_links_are_stored_in_studio_and_reapplied_without_a_network_check(tmp_path):
    app, data, model = _tree(tmp_path)
    store = tmp_path / "dead_download_links.json"
    dead_url = "https://sdk.deepx.ai/modelzoo/q-pro-dxnn/2_4_0/yolov5-m-face_640x640.dxnn"
    outputs, first = ex.build_outputs(app, [model], {}, [], data, "2026-10-13",
                                      url_ok=lambda u: (u != dead_url, 200 if u != dead_url else 403))
    ex.save_dead_links(first["dead_urls"], "2026-10-13", store)
    assert json.loads(store.read_text())["dead_links"] == [dead_url]
    ex.write_outputs(app, outputs)
    # A later run without --verify-links (or --check) applies the stored list: same files, nothing to change.
    again, report = ex.build_outputs(app, [model], {}, [], data, "2026-10-13", url_ok=ex.stored_dead_links(store))
    assert again == outputs and ex.changed_outputs(app, again) == []
    assert report["dead_links"] == [f"yolov5-m-face_640x640: {dead_url} (dead at the last --verify-links)"]


def test_stored_dead_links_is_none_without_the_stored_file(tmp_path):
    assert ex.stored_dead_links(tmp_path / "missing.json") is None


def test_links_are_not_checked_by_default(tmp_path):
    app, data, model = _tree(tmp_path)
    outputs, report = ex.build_outputs(app, [model], {}, [], data, "2026-10-13")
    assert report["dead_links"] == []
    assert "q-pro-dxnn" in outputs["src/python_example/face_detection/yolov5_face/yolov5-m-face_640x640/README.md"].decode()


def test_head_status_reports_a_network_error_instead_of_raising():
    ok, status = ex.head_status("http://127.0.0.1:9/nothing.dxnn", timeout=2)
    assert ok is False and status


def test_an_unpublished_card_gets_the_manifest_download_which_is_checked_too(tmp_path):
    app, data, model = _tree(tmp_path)
    url = "https://sdk.deepx.ai/modelzoo/dxnn/2_4_0/YOLOv5-M-Face_640x640.dxnn"
    (app / "scripts/modelzoo_manifest.json").write_text(json.dumps([{"name": "yolov5m_face", "dxnn_url": url}]),
                                                        encoding="utf-8")
    model = {k: v for k, v in model.items() if k not in ("artifacts", "performance")}
    outputs, report = ex.build_outputs(app, [model], {}, [], data, "2026-10-13")
    py = "src/python_example/face_detection/yolov5_face/yolov5-m-face_640x640"
    assert report["unpublished"] == ["yolov5-m-face_640x640"]
    assert f"| DXNN (dx_app manifest) | DX-COM 2.4.0 | [DXNN]({url}) |" in outputs[f"{py}/README.md"].decode()
    assert url in outputs[f"{py}/model.html"].decode()
    outputs, report = ex.build_outputs(app, [model], {}, [], data, "2026-10-13", url_ok=lambda u: (False, 404))
    assert report["dead_links"] == [f"yolov5-m-face_640x640: {url} (404)"]
    assert "No public downloads." in outputs[f"{py}/README.md"].decode()


def test_model_html_carries_the_generated_marker(tmp_path):
    app, data, model = _tree(tmp_path)
    outputs, _ = ex.build_outputs(app, [model], {}, [], data, "2026-10-13")
    page = outputs["src/python_example/face_detection/yolov5_face/yolov5-m-face_640x640/model.html"].decode()
    assert page.splitlines()[:2] == ["<!doctype html>", "<!-- Generated by DX AI Studio (python -m "
                                     "dx_modelzoo.tools.export_dx_app_cards). Do not edit by hand. -->"]
