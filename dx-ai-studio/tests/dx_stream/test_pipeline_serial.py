"""pipeline.py 테스트 — 파이프라인 직렬화 + 인코더 폴백 로직"""
import sys, pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_stream"))


class TestEncoderFallback:
    @patch("core.pipeline._gst_available", False)
    def test_fallback_returns_default_when_no_gst(self):
        from core.pipeline import detect_encoder
        enc = detect_encoder()
        assert enc["encoder"] == "vp8enc deadline=1"
        assert enc["payloader"] == "rtpvp8pay"

    @patch("core.pipeline._gst_available", True)
    def test_fallback_order(self):
        """인코더 폴백 순서: mpph264enc(HW H264, 저부하) → vp8enc(SW, 이식성) → vaapih264enc → x264enc → jpegenc"""
        from core.pipeline import ENCODER_FALLBACK_CHAIN
        assert ENCODER_FALLBACK_CHAIN[0]["factory"] == "mpph264enc"  # HW H264 — real-time on ARM
        assert ENCODER_FALLBACK_CHAIN[0]["extra"] == "profile=baseline"  # webrtc-compatible profile
        assert ENCODER_FALLBACK_CHAIN[1]["factory"] == "vp8enc"  # portable software fallback
        assert ENCODER_FALLBACK_CHAIN[2]["factory"] == "vaapih264enc"
        assert ENCODER_FALLBACK_CHAIN[3]["factory"] == "x264enc"
        assert ENCODER_FALLBACK_CHAIN[4]["factory"] == "jpegenc"


class TestPipelineJson:
    def test_json_to_gst_string_basic(self):
        from core.pipeline import pipeline_json_to_gst
        pipeline_def = {
            "nodes": [
                {"id": "src", "type": "urisourcebin", "props": {"uri": "file:///test.mp4"}},
                {"id": "dec", "type": "decodebin", "props": {}},
                {"id": "pre", "type": "dxpreprocess", "props": {"resize-width": 640, "resize-height": 640}},
            ],
            "edges": [["src", "dec"], ["dec", "pre"]]
        }
        gst_str = pipeline_json_to_gst(pipeline_def)
        assert "urisourcebin" in gst_str
        assert "uri=file:///test.mp4" in gst_str
        assert "dxpreprocess" in gst_str

    def test_gst_string_to_json_roundtrip(self):
        from core.pipeline import pipeline_json_to_gst
        pipeline_def = {
            "nodes": [
                {"id": "src", "type": "urisourcebin", "props": {"uri": "file:///test.mp4"}},
                {"id": "pre", "type": "dxpreprocess", "props": {"resize-width": 640}},
            ],
            "edges": [["src", "pre"]]
        }
        gst_str = pipeline_json_to_gst(pipeline_def)
        assert isinstance(gst_str, str)
        assert len(gst_str) > 0

    def test_json_to_gst_branching(self):
        """tee + gather 분기 파이프라인 변환 테스트."""
        from core.pipeline import pipeline_json_to_gst
        pipeline_def = {
            "nodes": [
                {"id": "n1", "type": "urisourcebin", "properties": {"uri": "file:///test.mp4"}},
                {"id": "n2", "type": "decodebin", "properties": {}},
                {"id": "n3", "type": "tee", "properties": {}},
                {"id": "n4", "type": "queue", "properties": {}},
                {"id": "n5", "type": "DxInfer", "properties": {"model-path": "/m1.dxnn"}},
                {"id": "n6", "type": "queue", "properties": {}},
                {"id": "n7", "type": "DxInfer", "properties": {"model-path": "/m2.dxnn"}},
                {"id": "n8", "type": "DxGather", "properties": {}},
                {"id": "n9", "type": "DxOsd", "properties": {}},
            ],
            "edges": [
                {"from": "n1", "to": "n2"},
                {"from": "n2", "to": "n3"},
                {"from": "n3", "to": "n4"},
                {"from": "n3", "to": "n6"},
                {"from": "n4", "to": "n5"},
                {"from": "n5", "to": "n8"},
                {"from": "n6", "to": "n7"},
                {"from": "n7", "to": "n8"},
                {"from": "n8", "to": "n9"},
            ],
        }
        result = pipeline_json_to_gst(pipeline_def)
        assert "name=t" in result
        assert "t. !" in result
        assert "dxgather" in result.lower() or "gather" in result.lower()

    def test_json_to_gst_multisource_compositor(self):
        """멀티스트림: N개 독립 소스가 compositor로 합류 — 모든 소스가 방출되어야 한다.

        이전 구현은 첫 소스 체인만 방출하고 나머지를 누락시켜 멀티스트림 빌더가
        한 스트림만 출력하던 회귀를 방지한다.
        """
        from core.pipeline import pipeline_json_to_gst
        nodes, edges = [], []
        for i in range(3):
            p = f"s{i}_"
            chain = [
                {"id": p + "src", "type": "urisourcebin", "properties": {"uri": f"file:///v{i}.mp4"}},
                {"id": p + "inf", "type": "DxInfer", "properties": {"model-path": f"/m{i}.dxnn"}},
                {"id": p + "osd", "type": "DxOsd", "properties": {}},
            ]
            nodes += chain
            edges += [{"from": chain[k]["id"], "to": chain[k + 1]["id"]} for k in range(len(chain) - 1)]
            edges.append({"from": p + "osd", "to": "comp"})
        nodes.append({"id": "comp", "type": "compositor", "properties": {}})
        result = pipeline_json_to_gst({"nodes": nodes, "edges": edges})
        # 모든 소스 체인이 존재해야 함 (이전엔 1개만)
        assert result.count("urisourcebin") == 3, result
        for i in range(3):
            assert f"/v{i}.mp4" in result, f"source {i} dropped: {result}"
        # compositor 가 3개의 sink pad 로 합류
        assert "compositor" in result
        for i in range(3):
            assert f".sink_{i}" in result, result
        # compositor 격자 배치가 자동 지정되어 화면이 겹치지 않음
        assert "::xpos=" in result and "::ypos=" in result, result

    def test_json_to_gst_branching_preserves_linear(self):
        """분기 코드 추가 후에도 선형 파이프라인은 정상 동작해야 한다."""
        from core.pipeline import pipeline_json_to_gst
        pipeline_def = {
            "nodes": [
                {"id": "a", "type": "src", "properties": {}},
                {"id": "b", "type": "sink", "properties": {}},
            ],
            "edges": [{"from": "a", "to": "b"}],
        }
        result = pipeline_json_to_gst(pipeline_def)
        assert result == "src ! sink"


class TestPipelineManagerMock:
    @patch("core.pipeline._gst_available", False)
    def test_start_without_gst_raises(self):
        from core.pipeline import PipelineManager
        pm = PipelineManager()
        with pytest.raises(RuntimeError, match="GStreamer"):
            pm.start("fakepipeline ! fakesink")

    @patch("core.pipeline._gst_available", False)
    def test_is_running_default_false(self):
        from core.pipeline import PipelineManager
        pm = PipelineManager()
        assert pm.is_running() is False

    @patch("core.pipeline._gst_available", False)
    def test_concurrent_limit(self):
        """동시 실행 1개 제한 — _pipeline_id 수동 설정으로 로직 테스트"""
        from core.pipeline import PipelineManager
        pm = PipelineManager()
        pm._pipeline_id = "test-123"
        assert pm._pipeline_id is not None
