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
    assert set(outputs) == {f"{py}/README.md", f"{py}/model.html", f"{py}/result.webp", f"{cpp}/README.md",
                            "MODELS.md", "config/model_cards.json"}
    index = json.loads(outputs["config/model_cards.json"])
    assert index["asof"] == "2026-10-13" and index["models"][0]["zoo_task"] == "face_detection"
    assert "https://sdk.deepx.ai/modelzoo/q-lite-dxnn/2_5_0/yolov5-m-face_640x640.dxnn" in outputs["config/model_cards.json"].decode()
    assert report["count"] == 1 and report["setup_name_missing"] == [] and report["missing_image"] == []


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
    assert "MODELS.md" not in outputs and "config/model_cards.json" not in outputs
