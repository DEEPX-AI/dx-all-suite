"""status.py 시스템 상태 감지 테스트 — 파일시스템 모킹으로 격리"""
import os, sys, pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_stream"))


class TestCheckNpu:
    @patch("core.status.Path.glob")
    def test_npu_detected(self, mock_glob):
        from core.status import _check_npu
        mock_glob.return_value = [Path("/dev/dxrt0")]
        result = _check_npu()
        assert result["ok"] is True
        assert result["devices"] == ["/dev/dxrt0"]

    @patch("core.status.Path.glob")
    def test_npu_not_found(self, mock_glob):
        from core.status import _check_npu
        mock_glob.return_value = []
        result = _check_npu()
        assert result["ok"] is False


class TestCheckGstreamer:
    @patch("shutil.which")
    def test_gst_installed(self, mock_which):
        from core.status import _check_gst
        mock_which.return_value = "/usr/bin/gst-inspect-1.0"
        result = _check_gst()
        assert result["installed"] is True

    @patch("shutil.which")
    def test_gst_not_installed(self, mock_which):
        from core.status import _check_gst
        mock_which.return_value = None
        result = _check_gst()
        assert result["installed"] is False
        assert result["ok"] is False


class TestCheckModels:
    def test_models_found(self, tmp_path):
        from core.status import _check_models
        from core.models import get_models
        models_dir = tmp_path / "models"
        models_dir.mkdir()
        (models_dir / "yolo26n.dxnn").touch()
        (models_dir / "YoloV5S.dxnn").touch()
        with patch("core.status.MODELS_DIR", models_dir):
            result = _check_models()
        assert result["total"] == len(get_models())
        assert result["installed"] == 2
        assert result["ok"] is False

    def test_no_models_dir(self, tmp_path):
        from core.status import _check_models
        with patch("core.status.MODELS_DIR", tmp_path / "nonexistent"):
            result = _check_models()
        assert result["installed"] == 0
        assert result["ok"] is False


class TestCheckVideos:
    def test_videos_found(self, tmp_path):
        from core.status import _check_videos
        videos_dir = tmp_path / "videos"
        videos_dir.mkdir()
        (videos_dir / "boat.mp4").touch()
        with patch("core.status.VIDEOS_DIR", videos_dir):
            result = _check_videos()
        assert result["count"] >= 1
        assert result["ok"] is True


def test_status_model_total_matches_runtime_catalog(monkeypatch, tmp_path, request):
    import json
    import importlib

    orig = os.environ.get("DX_STREAM_ROOT")

    root = tmp_path / "runtime"
    root.mkdir()
    (root / "model_list.json").write_text(json.dumps({"version": "2_3_0", "models": ["yolo26n.dxnn", "YoloV5S.dxnn"]}), encoding="utf-8")
    models_dir = root / "dx_stream" / "samples" / "models"
    models_dir.mkdir(parents=True)
    (models_dir / "yolo26n.dxnn").touch()
    monkeypatch.setenv("DX_STREAM_ROOT", str(root))

    import core.config as config
    import core.runtime as runtime
    import core.models as models
    import core.status as status
    importlib.reload(config)
    importlib.reload(runtime)
    importlib.reload(models)
    status = importlib.reload(status)

    def _restore_modules():
        if orig is None:
            os.environ.pop("DX_STREAM_ROOT", None)
        else:
            os.environ["DX_STREAM_ROOT"] = orig
        import core.config as _cfg
        import core.runtime as _rt
        import core.models as _mdl
        import core.status as _st
        importlib.reload(_cfg)
        importlib.reload(_rt)
        importlib.reload(_mdl)
        importlib.reload(_st)

    request.addfinalizer(_restore_modules)

    result = status._check_models()

    assert result["catalog_source"] == "manifest"
    assert result["total"] == len(models.get_models()) == 2
    assert result["installed"] == 1


class TestCheckSystem:
    @patch("core.status._check_npu")
    @patch("core.status._check_gst")
    @patch("core.status._check_models")
    @patch("core.status._check_videos")
    @patch("core.status._check_build")
    def test_check_system_aggregates(self, mock_build, mock_videos, mock_models, mock_gst, mock_npu):
        from core.status import check_system
        mock_npu.return_value = {"ok": True}
        mock_gst.return_value = {"ok": True}
        mock_models.return_value = {"ok": True, "catalog_source": "fallback"}
        mock_videos.return_value = {"ok": True}
        mock_build.return_value = {"ok": True}
        result = check_system()
        assert "npu" in result
        assert "gstreamer" in result
        assert "models" in result
        assert "videos" in result
        assert "build" in result
        assert result["catalog_source"] == "fallback"

    @patch("core.status._check_npu")
    @patch("core.status._check_gst")
    @patch("core.status._check_models")
    @patch("core.status._check_videos")
    @patch("core.status._check_build")
    def test_check_system_with_pipeline_mgr(self, mock_build, mock_videos, mock_models, mock_gst, mock_npu):
        from core.status import check_system
        mock_npu.return_value = {"ok": True}
        mock_gst.return_value = {"ok": True}
        mock_models.return_value = {"ok": True, "catalog_source": "fallback"}
        mock_videos.return_value = {"ok": True}
        mock_build.return_value = {"ok": True}

        mock_mgr = MagicMock()
        mock_mgr.is_running.return_value = True
        result = check_system(pipeline_mgr=mock_mgr)
        # GstShark/perf was removed; check_system still returns the core status blocks.
        assert "npu" in result and "gstreamer" in result and "models" in result
        assert "perf" not in result

    def test_check_system_has_system_info(self):
        from core.status import check_system
        result = check_system()
        assert 'system_info' in result
        info = result['system_info']
        assert 'os' in info
        assert 'python_version' in info
        assert 'gstreamer_version' in info
        assert 'npu_driver_version' in info


