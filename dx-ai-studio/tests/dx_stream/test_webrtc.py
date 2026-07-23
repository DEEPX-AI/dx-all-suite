"""webrtc.py 테스트 — GI 바인딩 모킹으로 시그널링 로직 검증"""
import sys, pytest, threading
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_stream"))


class TestWebRTCHandlerInit:
    def test_initial_state_no_peer(self):
        from core.webrtc import WebRTCHandler
        handler = WebRTCHandler()
        assert handler._current_peer_id is None
        assert handler.get_server_ice_candidates() == []

    def test_single_peer_enforcement(self):
        """2번째 연결 시도 시 이전 peer 자동 해제"""
        from core.webrtc import WebRTCHandler
        handler = WebRTCHandler()
        handler._current_peer_id = "peer-1"
        handler._ice_candidates = [{"candidate": "test"}]
        handler._reset_peer("peer-2")
        assert handler._current_peer_id == "peer-2"
        assert handler.get_server_ice_candidates() == []


class TestOfferAnswerFlow:
    @patch("core.webrtc._gst_available", False)
    def test_handle_offer_without_gst_raises(self):
        from core.webrtc import WebRTCHandler
        handler = WebRTCHandler()
        with pytest.raises(RuntimeError, match="GStreamer"):
            handler.handle_offer("fake-sdp", MagicMock())

    @patch("core.webrtc._gst_available", True)
    def test_handle_offer_requires_pipeline(self):
        from core.webrtc import WebRTCHandler
        handler = WebRTCHandler()
        mock_pm = MagicMock()
        mock_pm.is_running.return_value = False
        with pytest.raises(RuntimeError, match="[Pp]ipeline"):
            handler.handle_offer("fake-sdp", mock_pm)


class TestICEHandling:
    def test_handle_ice_stores_candidate(self):
        from core.webrtc import WebRTCHandler
        handler = WebRTCHandler()
        handler._current_peer_id = "peer-1"
        handler._ice_candidates = []
        handler._buffer_ice_candidate(0, "candidate:123")
        assert len(handler._ice_buffer) >= 1

    def test_ice_timeout_value(self):
        from core.webrtc import WebRTCHandler
        handler = WebRTCHandler()
        assert handler.ICE_TIMEOUT == 30
