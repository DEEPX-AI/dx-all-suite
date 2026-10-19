"""Card rules from the spec (§3.3): values, deltas, warnings, versions, links, boards, commands."""
import json

import pytest

from dx_modelzoo.core import model_card as mc
from dx_modelzoo.core.model_card_labels import lede

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
    # Deltas come from the shown (2-decimal) values: 95.57 − 95.57, 94.14 − 94.13, 86.33 − 86.34.
    assert [c["delta"] for c in qlite["cells"]] == [0.0, 0.01, -0.01]
    assert acc["metric_count_mismatch"] is False
    assert acc["warnings"] == [{"tier": "Q-Pro", "metric": "AP(Easy)", "drop": 7.57}]


def test_downloads_carry_compiler_versions_and_internal_links_are_dropped(app):
    card = mc.build_card(MODEL, ROW, app, asof="2026-10-13")
    tiers = card["downloads"]["tiers"]
    assert [(t["label"], t["compiler"]) for t in tiers] == [("Q-Lite", "2.5.0"), ("Q-Pro", "2.4.0")]
    assert tiers[1]["json"] is None
    assert card["source"] is None          # the internal "No Reference" link never reaches a card
    assert card["published"] is True


def test_summary_fixes_the_article_and_falls_back(app):
    assert mc.build_card(MODEL, ROW, app, asof="2026-10-13")["summary"] == "YOLOv5-m-face is an object detector."
    bare = dict(MODEL, display={"name": "X"})
    card = mc.build_card(bare, ROW, app, task_label="Face Detection", asof="2026-10-13")
    assert card["summary"] == ""
    # The dataset is the one the accuracy was measured on, not necessarily the training set.
    assert lede(card) == "Face Detection model, evaluated on WiderFace."


@pytest.mark.parametrize("text, fixed", [
    ("X is a object detector.", "X is an object detector."),
    ("A object detector.", "An object detector."),
    ("X is a unified, one-stage model for a user and a universal use.",
     "X is a unified, one-stage model for a user and a universal use."),
    ("X is a European model and a one-shot model, a useful one.", "X is a European model and a one-shot model, a useful one."),
    ("X is a efficient and a interesting model.", "X is an efficient and an interesting model."),
])
def test_the_article_only_changes_before_vowel_sounds(text, fixed):
    assert mc.summary({"display": {"summary": {"en": text}}}) == fixed


def test_the_fallback_lede_is_translated_and_keeps_the_task_label_as_is(app):
    bare = dict(MODEL, display={"name": "X"})
    card = mc.build_card(bare, ROW, app, task_label="3D 객체 탐지", asof="2026-10-13", lang="ko")
    ko = {"{task} model, evaluated on {dataset}.": "{task} 모델, {dataset}로 평가."}
    assert lede(card, ko) == "3D 객체 탐지 모델, WiderFace로 평가."
    card = mc.build_card(bare, ROW, app, task_label="3D Object Detection", asof="2026-10-13")
    assert lede(card) == "3D Object Detection model, evaluated on WiderFace."
    card["dataset"] = None
    assert lede(card) == "3D Object Detection model."


def test_catalog_date_is_the_local_day():
    from datetime import timedelta, timezone
    kst = timezone(timedelta(hours=9))
    assert mc.catalog_date("2026-10-12T20:00:00+00:00", tz=kst) == "2026-10-13"
    assert mc.catalog_date("2026-10-13T05:00:18.427410+00:00", tz=kst) == "2026-10-13"
    assert mc.catalog_date("2026-10-13", tz=kst) == "2026-10-13"
    assert mc.catalog_date("", tz=kst) is None and mc.catalog_date(None) is None


def test_asof_is_required(app):
    with pytest.raises(TypeError):
        mc.build_card(MODEL, ROW, app)
    assert mc.build_card(MODEL, ROW, app, asof=None)["asof"] is None


def test_a_glued_metric_name_is_split_to_match_the_values(app):
    glued = dict(MODEL, specification=dict(MODEL["specification"], metric={"name": "AP(Easy)AP(Med)AP(Hard)"}))
    acc = mc.build_card(glued, ROW, app, asof="2026-10-13")["accuracy"]
    assert acc["metrics"] == ["AP(Easy)", "AP(Med)", "AP(Hard)"]
    assert len(acc["rows"][0]["cells"]) == 3 and acc["metric_count_mismatch"] is True
    odd = dict(MODEL, specification=dict(MODEL["specification"], metric={"name": "mAP"}))
    acc = mc.build_card(odd, ROW, app, asof="2026-10-13")["accuracy"]
    assert acc["metrics"] == ["mAP", "Metric 2", "Metric 3"] and acc["metric_count_mismatch"] is True


def test_unpublished_cards_use_the_registry_name_and_the_fallback_summary(app):
    studio_only = {k: v for k, v in MODEL.items() if k not in ("artifacts", "performance")}
    studio_only["display"] = {"name": "Yolov5 M Face", "summary": {"en": "Yolov5 M Face is a made-up summary."}}
    card = mc.build_card(studio_only, dict(ROW, original_name="YOLOv5m_Face"), app, task_label="Face Detection",
                         asof="2026-10-13")
    assert card["published"] is False
    assert card["name"] == "YOLOv5m_Face"
    assert lede(card) == "Face Detection model, evaluated on WiderFace."
    assert card["params"] == 21.04 and card["accuracy"]["rows"]
    card = mc.build_card(studio_only, ROW, app, asof="2026-10-13")
    assert card["name"] == "yolov5-m-face_640x640"


def test_has_cpp_follows_the_cpp_dir(app):
    assert mc.build_card(MODEL, ROW, app, asof="2026-10-13")["has_cpp"] is True
    import shutil
    shutil.rmtree(app / "src/cpp_example")
    assert mc.build_card(MODEL, ROW, app, asof="2026-10-13")["has_cpp"] is False


def test_rel_dir():
    assert mc.rel_dir("src/python_example/a/b/c", "src/cpp_example/a/b/c") == "../../../../cpp_example/a/b/c/"


def test_paths_sample_files_and_commands(app):
    card = mc.build_card(MODEL, ROW, app, asof="2026-10-13")
    assert card["paths"]["python"] == "src/python_example/face_detection/yolov5_face/yolov5-m-face_640x640"
    assert card["sample"] == "sample/img/sample_face.jpg"
    assert [f["name"] for f in card["files"]["python"]] == ["yolov5-m-face_640x640_sync.py", "config.json", "factory/"]
    assert [f["name"] for f in card["files"]["cpp"]] == ["yolov5-m-face_640x640_sync.cpp"]
    cmds = mc.commands(card)
    assert cmds["get"].endswith("./setup_sample_models.sh --models yolov5m_face")
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


def test_boards_without_a_valid_date_have_no_month():
    rows = [{"model": "m.dxnn", "env_id": "RPi5B_M1", "family": fam, "use_ort": False, "status": "ok", "fps": 10.0,
             "latency_ms": 5.0, "run_id": "20261399_000000"} for fam in ("throughput", "latency")]
    boards = mc.board_rows(rows, "m")
    assert len(boards["rows"]) == 1 and boards["measured"] is None


def test_formatting():
    assert mc.fmt_num(None) == "—"
    assert mc.fmt_num(39.0832) == "39.08"
    assert mc.fmt_fps(321.0) == "321" and mc.fmt_fps(228.42) == "228.4"
    assert mc.fmt_delta(-0.79) == "−0.79" and mc.fmt_delta(0.21) == "+0.21"
    assert mc.fmt_delta(0) == "±0.00" and mc.fmt_delta(-0.0) == "±0.00"
    assert mc.fmt_input("640x640x3") == "640 × 640 × 3"
    assert mc.public_url("https://sdk.deepx.ai/x.dxnn") == "https://sdk.deepx.ai/x.dxnn"
    assert mc.public_url("No Reference") is None


def test_zoo_task_is_the_publish_tables(app):
    model = dict(MODEL, display=dict(MODEL["display"], task="embedding", publish_task="image_retrieval"))
    assert mc.build_card(model, ROW, app, asof="2026-10-13")["zoo_task"] == "image_retrieval"
    assert mc.build_card(MODEL, ROW, app, asof="2026-10-13")["zoo_task"] == "face_detection"


MANIFEST_URL = "https://sdk.deepx.ai/modelzoo/dxnn/2_4_0/YOLOv5-M-Face_640x640.dxnn"


def test_an_unpublished_card_downloads_from_the_dx_app_manifest(app):
    studio_only = {k: v for k, v in MODEL.items() if k not in ("artifacts", "performance")}
    card = mc.build_card(studio_only, ROW, app, asof="2026-10-13", manifest_url=MANIFEST_URL)
    assert card["published"] is False
    assert card["downloads"]["manifest"] == {"dxnn": MANIFEST_URL, "compiler": "2.4.0"}
    # A published card links the publish table's files only.
    assert mc.build_card(MODEL, ROW, app, asof="2026-10-13", manifest_url=MANIFEST_URL)["downloads"]["manifest"] is None
    assert mc.build_card(studio_only, ROW, app, asof="2026-10-13")["downloads"]["manifest"] is None


def test_manifest_urls_match_the_dxnn_file_name_ignoring_case(tmp_path):
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts/modelzoo_manifest.json").write_text(json.dumps([
        {"name": "YOLOv5m_Face", "dxnn_url": MANIFEST_URL}, {"name": "no_url"}, "junk"]), encoding="utf-8")
    urls = mc.load_manifest_urls(tmp_path)
    assert urls == {"yolov5-m-face_640x640.dxnn": MANIFEST_URL}
    assert mc.manifest_url_for(urls, ROW) == MANIFEST_URL
    assert mc.load_manifest_urls(tmp_path / "missing") == {}


@pytest.mark.parametrize("generic", [
    "YOLOv5-m-face is a face detection model optimized for DEEPX NPU.",
    "Scrfd500M Ppu is a ppu model optimized for DEEPX NPU.",
    "DAMO-YOLO-L is a object detection model optimized for DEEPX NPU.",
    "AI model for anomaly_detection tasks.",
    "AI model for reid tasks.",
    "Object detection model for identifying and localizing objects.",
    "Image classification model for visual recognition tasks.",
])
def test_studio_template_summaries_give_way_to_the_fallback(app, generic):
    model = dict(MODEL, display=dict(MODEL["display"], summary={"en": generic}))
    assert lede(mc.build_card(model, ROW, app, task_label="Face Detection", asof="2026-10-13")) == \
        "Face Detection model, evaluated on WiderFace."


def test_a_kept_summary_reads_task_keys_as_words(app):
    model = dict(MODEL, display=dict(MODEL["display"],
                                     summary={"en": "EfficientAD is a fast anomaly_detection network for yolov5s_ppu."}))
    assert mc.build_card(model, ROW, app, asof="2026-10-13")["summary"] == \
        "EfficientAD is a fast anomaly detection network for yolov5s_ppu."
