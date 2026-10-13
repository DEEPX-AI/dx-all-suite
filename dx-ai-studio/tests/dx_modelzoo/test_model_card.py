"""Card rules from the spec (§3.3): values, deltas, warnings, versions, links, boards, commands."""
import json

import pytest

from dx_modelzoo.core import model_card as mc

MODEL = {
    "id": "yolov5m_face", "category": "face_detection", "name": "YOLOv5-m-face",
    "display": {"name": "YOLOv5-m-face", "task": "face_detection",
                "summary": {"en": "YOLOv5-m-face is a object detector.", "ko": "얼굴 탐지 모델."}},
    "specification": {"input_resolution": "640x640x3", "dataset": "WiderFace", "parameters": "21.04",
                      "operations": "25.84", "metric": {"name": "AP(Easy) / AP(Med) / AP(Hard)"}},
    "evaluation": {"raw": {"accuracy": "95.5657 / 94.1338 / 86.3405"},
                   "qlite": {"accuracy": "95.572 / 94.135 / 86.3257"},
                   "qpro": {"accuracy": "88.0 / 94.308 / 86.345"}},
    "performance": {"fps": 228.0, "fps_per_watt": 72.6},
    "artifacts": {"onnx": {"remote_url": "https://sdk.deepx.ai/modelzoo/onnx/yolov5-m-face_640x640.onnx"},
                  "qlite_dxnn": {"remote_url": "https://sdk.deepx.ai/modelzoo/q-lite-dxnn/2_5_0/yolov5-m-face_640x640.dxnn"},
                  "qlite_json": {"remote_url": "https://sdk.deepx.ai/modelzoo/q-lite-json/2_5_0/yolov5-m-face_640x640.json"},
                  "qpro_dxnn": {"remote_url": "https://sdk.deepx.ai/modelzoo/q-pro-dxnn/2_4_0/yolov5-m-face_640x640.dxnn"}},
    "legal": {"license": "GPL-3.0", "source_url": "https://modelzoo-publish-api.devops.dpx.ai/publish/No%20Reference",
              "copyright": "deepcam-cn", "license_text": "GNU GPL v3"},
}
ROW = {"model_name": "yolov5m_face", "dxnn_file": "yolov5-m-face_640x640.dxnn", "variant": "yolov5-m-face_640x640",
       "family": "yolov5_face", "task": "face_detection"}


@pytest.fixture()
def app(tmp_path):
    d = tmp_path / "src/python_example/face_detection/yolov5_face/yolov5-m-face_640x640"
    (d / "factory").mkdir(parents=True)
    (d / "config.json").write_text(json.dumps({"default_image": "sample/img/sample_face.jpg"}), encoding="utf-8")
    (d / "yolov5-m-face_640x640_sync.py").write_text("", encoding="utf-8")
    c = tmp_path / "src/cpp_example/face_detection/yolov5_face/yolov5-m-face_640x640"
    c.mkdir(parents=True)
    (c / "yolov5-m-face_640x640_sync.cpp").write_text("", encoding="utf-8")
    return tmp_path


def test_multi_metric_accuracy_with_deltas_and_a_warning(app):
    card = mc.build_card(MODEL, ROW, app, asof="2026-10-13")
    acc = card["accuracy"]
    assert acc["metrics"] == ["AP(Easy)", "AP(Med)", "AP(Hard)"]
    qlite = next(r for r in acc["rows"] if r["tier"] == "qlite")
    assert [c["value"] for c in qlite["cells"]] == [95.572, 94.135, 86.3257]
    assert qlite["cells"][0]["delta"] == pytest.approx(0.01, abs=0.005)
    assert acc["warnings"] == [{"tier": "Q-Pro", "metric": "AP(Easy)", "drop": 7.57}]


def test_downloads_carry_compiler_versions_and_internal_links_are_dropped(app):
    card = mc.build_card(MODEL, ROW, app, asof="2026-10-13")
    tiers = card["downloads"]["tiers"]
    assert [(t["label"], t["compiler"]) for t in tiers] == [("Q-Lite", "2.5.0"), ("Q-Pro", "2.4.0")]
    assert tiers[1]["json"] is None
    assert card["source"] is None          # the internal "No Reference" link never reaches a card
    assert card["published"] is True


def test_summary_fixes_the_article_and_falls_back(app):
    assert mc.build_card(MODEL, ROW, app)["summary"] == "YOLOv5-m-face is an object detector."
    bare = dict(MODEL, display={"name": "X"})
    assert mc.build_card(bare, ROW, app, task_label="Face Detection")["summary"] == \
        "X — face detection model, trained on WiderFace."


def test_paths_sample_files_and_commands(app):
    card = mc.build_card(MODEL, ROW, app)
    assert card["paths"]["python"] == "src/python_example/face_detection/yolov5_face/yolov5-m-face_640x640"
    assert card["sample"] == "sample/img/sample_face.jpg"
    assert [f["name"] for f in card["files"]["python"]] == ["yolov5-m-face_640x640_sync.py", "config.json", "factory/"]
    assert [f["name"] for f in card["files"]["cpp"]] == ["yolov5-m-face_640x640_sync.cpp"]
    cmds = mc.commands(card)
    assert cmds["get"].endswith("./setup.sh --models yolov5m_face")
    assert "--image sample/img/sample_face.jpg" in cmds["python"]
    assert cmds["cpp"].startswith("./build.sh --target yolov5-m-face_640x640_sync")
    assert "--loop 100 --no-display" in cmds["measure"]


def test_boards_use_the_newest_run_of_this_exact_file():
    rows = [
        {"model": "yolo26-n_640x640.dxnn", "env_id": "RPi5B_M1", "family": "throughput", "use_ort": False,
         "status": "ok", "fps": 170.0, "run_id": "20260716_100000"},
        {"model": "yolo26-n_640x640.dxnn", "env_id": "RPi5B_M1", "family": "throughput", "use_ort": False,
         "status": "ok", "fps": 179.6, "run_id": "20260720_224855"},
        {"model": "yolo26-n_640x640.dxnn", "env_id": "RPi5B_M1", "family": "latency", "use_ort": False,
         "status": "ok", "fps": 46.4, "latency_ms": 21.54, "run_id": "20260720_224855"},
        {"model": "yolo26-n_640x640.dxnn", "env_id": "RPi5B_M1", "family": "latency", "use_ort": True,
         "status": "ok", "fps": 99.0, "latency_ms": 9.0, "run_id": "20260721_000000"},
        {"model": "yolo26n.dxnn", "env_id": "ROCK5B+_M1", "family": "latency", "use_ort": False,
         "status": "ok", "fps": 1.0, "latency_ms": 1.0, "run_id": "20260720_000000"},
    ]
    boards = mc.board_rows(rows, "yolo26-n_640x640")
    assert boards == {"rows": [{"board": "DX-M1 · Raspberry Pi 5", "throughput_fps": 179.6,
                                "single_fps": 46.4, "latency_ms": 21.5}], "measured": "July 2026"}


def test_formatting():
    assert mc.fmt_num(None) == "—"
    assert mc.fmt_num(39.0832) == "39.08"
    assert mc.fmt_fps(321.0) == "321" and mc.fmt_fps(228.42) == "228.4"
    assert mc.fmt_delta(-0.79) == "−0.79" and mc.fmt_delta(0.21) == "+0.21"
    assert mc.fmt_input("640x640x3") == "640 × 640 × 3"
    assert mc.public_url("https://sdk.deepx.ai/x.dxnn") == "https://sdk.deepx.ai/x.dxnn"
    assert mc.public_url("No Reference") is None
