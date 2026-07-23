"""demos.py 테스트 — 데모 목록 및 파이프라인 문자열 생성"""
import sys, pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_stream"))


class TestDemoList:
    def test_has_11_dev_backed_demos(self):
        from core.demos import DEMOS
        assert len(DEMOS) == 11

    def test_removed_standalone_demos_are_not_exposed(self):
        from core.demos import DEMOS
        categories = {d["category"] for d in DEMOS}
        assert "obb_detection" not in categories
        assert "classification" not in categories

    def test_demo_fields(self):
        from core.demos import DEMOS
        required = {"id", "name_ko", "name_en", "category", "description_ko", "description_en"}
        for demo in DEMOS:
            assert required.issubset(demo.keys()), f"Demo {demo.get('id')} missing fields"
            # Every demo must have "model" (single) or "models" (list)
            assert "model" in demo or "models" in demo, f"Demo {demo.get('id')} missing model field"

    def test_demo_ids_unique(self):
        from core.demos import DEMOS
        ids = [d["id"] for d in DEMOS]
        assert len(ids) == len(set(ids))

    def test_demo_ids_are_sequential(self):
        from core.demos import DEMOS
        for i, demo in enumerate(DEMOS):
            assert demo["id"] == i


class TestPipelineString:
    def test_basic_pipeline_has_webrtcbin(self):
        from core.demos import build_pipeline_str
        pipe = build_pipeline_str(demo_id=0, encoder={"encoder": "x264enc tune=zerolatency", "payloader": "rtph264pay config-interval=-1", "encoding_name": "H264", "payload_type": 96})
        assert "webrtcbin" in pipe
        assert "dxinfer" in pipe
        assert "fpsdisplaysink" not in pipe

    def test_basic_pipeline_has_source(self):
        from core.demos import build_pipeline_str
        pipe = build_pipeline_str(demo_id=0, encoder={"encoder": "x264enc tune=zerolatency", "payloader": "rtph264pay config-interval=-1", "encoding_name": "H264", "payload_type": 96})
        assert "urisourcebin" in pipe

    def test_ppu_demo_uses_config_files(self):
        """PPU 데모 1번은 config-file-path 속성 사용"""
        from core.demos import build_pipeline_str
        pipe = build_pipeline_str(demo_id=1, encoder={"encoder": "x264enc tune=zerolatency", "payloader": "rtph264pay config-interval=-1", "encoding_name": "H264", "payload_type": 96})
        assert "config-file-path" in pipe

    def test_tracking_demo_has_dxtracker(self):
        from core.demos import build_pipeline_str
        pipe = build_pipeline_str(demo_id=7, encoder={"encoder": "x264enc tune=zerolatency", "payloader": "rtph264pay config-interval=-1", "encoding_name": "H264", "payload_type": 96})
        assert "dxtracker" in pipe

    def test_custom_video_source(self):
        from core.demos import build_pipeline_str
        pipe = build_pipeline_str(demo_id=0, encoder={"encoder": "x264enc tune=zerolatency", "payloader": "rtph264pay config-interval=-1", "encoding_name": "H264", "payload_type": 96},
                                  video_uri="file:///tmp/test.mp4")
        assert "file:///tmp/test.mp4" in pipe

    def test_all_demos_generate_valid_pipeline(self):
        from core.demos import DEMOS, build_pipeline_str
        for demo in DEMOS:
            pipe = build_pipeline_str(demo_id=demo["id"], encoder={"encoder": "x264enc tune=zerolatency", "payloader": "rtph264pay config-interval=-1", "encoding_name": "H264", "payload_type": 96})
            assert isinstance(pipe, str)
            assert len(pipe) > 50
            assert "webrtcbin" in pipe


class TestDemoAvailability:
    def test_check_demo_available(self):
        from core.demos import check_demo_available
        result = check_demo_available(0)
        assert "available" in result
        assert "reason" in result


class TestNewDemos:
    def test_secondary_demo_exists(self):
        from core.demos import DEMOS
        sec_demos = [d for d in DEMOS if d["category"] == "secondary"]
        assert len(sec_demos) >= 1
        assert sec_demos[0]["pipeline_type"] == "secondary"
        assert "models" in sec_demos[0]
        assert len(sec_demos[0]["models"]) == 3

    def test_secondary_pipeline_has_tee_and_gather(self):
        from core.demos import build_pipeline_str
        pipe = build_pipeline_str(demo_id=10, encoder={"encoder": "x264enc tune=zerolatency", "payloader": "rtph264pay config-interval=-1", "encoding_name": "H264", "payload_type": 96})
        assert "tee name=t" in pipe
        assert "dxgather" in pipe
        assert "secondary-mode=true" in pipe

    def test_multi_pipeline_has_compositor(self):
        from core.demos import build_pipeline_str
        pipe = build_pipeline_str(demo_id=8, encoder={"encoder": "x264enc tune=zerolatency", "payloader": "rtph264pay config-interval=-1", "encoding_name": "H264", "payload_type": 96})
        assert "compositor" in pipe
        assert "dxscale" in pipe

    def test_rtsp_pipeline_has_mux_demux(self):
        from core.demos import build_pipeline_str
        pipe = build_pipeline_str(demo_id=9, encoder={"encoder": "x264enc tune=zerolatency", "payloader": "rtph264pay config-interval=-1", "encoding_name": "H264", "payload_type": 96})
        assert "dxinputselector" in pipe
        assert "dxoutputselector" in pipe
        assert "compositor" in pipe
        assert "rtspsrc" in pipe
        assert pipe.count("rtspsrc") == 4

    def test_check_demo_available_secondary(self):
        """Secondary demo should check all 3 models"""
        from core.demos import check_demo_available
        result = check_demo_available(10)
        assert "available" in result
        assert "reason" in result


def test_dev_demo_ids_and_categories():
    from core.demos import DEMOS
    assert [(d["id"], d["category"]) for d in DEMOS] == [
        (0, "object_detection"),
        (1, "object_detection"),
        (2, "face_detection"),
        (3, "face_detection"),
        (4, "pose_estimation"),
        (5, "pose_estimation"),
        (6, "segmentation"),
        (7, "tracking"),
        (8, "multi_stream"),
        (9, "multi_stream"),
        (10, "secondary"),
    ]


def test_config_demo_reports_missing_config(monkeypatch, tmp_path):
    import core.demos as demos
    models_dir = tmp_path / "models"
    models_dir.mkdir()
    (models_dir / "YoloV5S_PPU.dxnn").touch()
    monkeypatch.setattr(demos, "MODELS_DIR", models_dir)
    monkeypatch.setattr(demos, "CONFIGS_DIR", tmp_path / "configs")
    monkeypatch.setattr(demos, "PIPELINES_DIR", tmp_path / "pipelines", raising=False)
    monkeypatch.setattr(demos, "VIDEOS_DIR", tmp_path / "videos", raising=False)
    monkeypatch.setattr(demos, "_npu_exists", lambda: True)
    monkeypatch.setattr(demos, "_plugin_exists", lambda: True)

    result = demos.check_demo_available(1)

    assert result["available"] is False
    assert "Missing config file" in result["reason"]
    assert "설정 파일 없음" not in result["reason"]
    assert {
        "code": "missing_config_file",
        "path": "YoloV5S_PPU/preprocess_config.json",
    } in result["reason_items"]


def test_script_demo_reports_missing_runtime_script(monkeypatch, tmp_path):
    import core.demos as demos
    demo = demos.DEMOS[0]
    models_dir = tmp_path / "models"
    videos_dir = tmp_path / "videos"
    models_dir.mkdir()
    videos_dir.mkdir()
    (models_dir / demos._model_file(demo["model"])).touch()
    (videos_dir / demo["required_videos"][0]).touch()
    monkeypatch.setattr(demos, "MODELS_DIR", models_dir)
    monkeypatch.setattr(demos, "CONFIGS_DIR", tmp_path / "configs")
    monkeypatch.setattr(demos, "PIPELINES_DIR", tmp_path / "pipelines", raising=False)
    monkeypatch.setattr(demos, "VIDEOS_DIR", videos_dir, raising=False)
    monkeypatch.setattr(demos, "_npu_exists", lambda: True)
    monkeypatch.setattr(demos, "_plugin_exists", lambda: True)

    result = demos.check_demo_available(0)

    assert result["available"] is False
    assert result["reason"] == "Missing runtime script: single_network/object_detection/run_yolo26n.sh"
    assert "런타임 스크립트 없음" not in result["reason"]
    assert result["reason_items"] == [
        {
            "code": "missing_runtime_script",
            "path": "single_network/object_detection/run_yolo26n.sh",
        }
    ]


def test_local_video_demo_reports_missing_video(monkeypatch, tmp_path):
    import core.demos as demos
    demo = demos.DEMOS[0]
    video_name = demo["required_videos"][0]
    models_dir = tmp_path / "models"
    pipelines_dir = tmp_path / "pipelines"
    models_dir.mkdir()
    (models_dir / demos._model_file(demo["model"])).touch()
    script_path = pipelines_dir / demo["runtime_script"]
    script_path.parent.mkdir(parents=True)
    script_path.touch()
    monkeypatch.setattr(demos, "MODELS_DIR", models_dir)
    monkeypatch.setattr(demos, "CONFIGS_DIR", tmp_path / "configs")
    monkeypatch.setattr(demos, "PIPELINES_DIR", pipelines_dir, raising=False)
    monkeypatch.setattr(demos, "VIDEOS_DIR", tmp_path / "videos", raising=False)
    monkeypatch.setattr(demos, "_npu_exists", lambda: True)
    monkeypatch.setattr(demos, "_plugin_exists", lambda: True)

    result = demos.check_demo_available(0)

    assert result["available"] is False
    assert f"Missing sample video: {video_name}" in result["reason"]
    assert "샘플 비디오 없음" not in result["reason"]
    assert {"code": "missing_sample_video", "path": video_name} in result["reason_items"]


def test_secondary_demo_still_requires_three_models():
    from core.demos import DEMOS
    secondary = DEMOS[10]
    assert secondary["category"] == "secondary"
    assert secondary["models"] == ["YoloV5S_PPU.dxnn", "EfficientNet_Lite0.dxnn", "SCRFD500M.dxnn"]


def test_secondary_demo_reports_all_three_missing_models(monkeypatch, tmp_path):
    import core.demos as demos
    monkeypatch.setattr(demos, "MODELS_DIR", tmp_path / "models")
    monkeypatch.setattr(demos, "CONFIGS_DIR", tmp_path / "configs")
    monkeypatch.setattr(demos, "PIPELINES_DIR", tmp_path / "pipelines", raising=False)
    monkeypatch.setattr(demos, "VIDEOS_DIR", tmp_path / "videos", raising=False)
    monkeypatch.setattr(demos, "_npu_exists", lambda: True)
    monkeypatch.setattr(demos, "_plugin_exists", lambda: True)

    result = demos.check_demo_available(10)

    assert result["available"] is False
    for model in ("YoloV5S_PPU.dxnn", "EfficientNet_Lite0.dxnn", "SCRFD500M.dxnn"):
        assert model in result["reason"]
        assert {"code": "missing_model", "path": model} in result["reason_items"]


def test_available_demo_reports_language_neutral_ready_reason(monkeypatch, tmp_path):
    import core.demos as demos

    demo = demos.DEMOS[0]
    models_dir = tmp_path / "models"
    videos_dir = tmp_path / "videos"
    pipelines_dir = tmp_path / "pipelines"
    models_dir.mkdir()
    videos_dir.mkdir()
    (models_dir / demos._model_file(demo["model"])).touch()
    (videos_dir / demo["required_videos"][0]).touch()
    script_path = pipelines_dir / demo["runtime_script"]
    script_path.parent.mkdir(parents=True)
    script_path.touch()
    monkeypatch.setattr(demos, "MODELS_DIR", models_dir)
    monkeypatch.setattr(demos, "CONFIGS_DIR", tmp_path / "configs")
    monkeypatch.setattr(demos, "PIPELINES_DIR", pipelines_dir, raising=False)
    monkeypatch.setattr(demos, "VIDEOS_DIR", videos_dir, raising=False)
    monkeypatch.setattr(demos, "_npu_exists", lambda: True)
    monkeypatch.setattr(demos, "_plugin_exists", lambda: True)

    result = demos.check_demo_available(0)

    assert result == {
        "available": True,
        "reason": "Ready to run",
        "reason_items": [],
        "demo_id": 0,
    }


def test_format_reason_item_tolerates_missing_code():
    import core.demos as demos

    assert demos._format_reason_item({}) == "unknown"
    assert demos._format_reason_item({"path": "model.dxnn"}) == "unknown: model.dxnn"


def test_rtsp_demo_does_not_require_local_videos():
    from core.demos import DEMOS
    rtsp = DEMOS[9]
    assert rtsp["pipeline_type"] == "rtsp"
    assert "required_videos" not in rtsp


def test_demo_metadata_covers_all_release_languages():
    from core.demos import DEMOS

    languages = ("en", "ko", "ja", "es", "zh-CN", "zh-TW")
    missing = {}
    for demo in DEMOS:
        for field in ("name", "description"):
            for lang in languages:
                key = f"{field}_{lang}"
                if not str(demo.get(key, "")).strip():
                    missing.setdefault(demo["id"], []).append(key)

    assert not missing, missing
