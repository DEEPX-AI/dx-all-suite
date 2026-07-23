"""WebRTC 시그널링 핸들러 — HTTP 기반 SDP/ICE 교환.

WebSocket 불필요. POST /api/webrtc/offer → SDP answer.
단일 peer(1:1), ICE 타임아웃 30초.
"""
from __future__ import annotations

import logging
import threading
import uuid
from typing import Any

log = logging.getLogger(__name__)

_gst_available = False
Gst = None
GstSdp = None
GstWebRTC = None
GLib = None

try:
    import gi
    gi.require_version("Gst", "1.0")
    gi.require_version("GstWebRTC", "1.0")
    gi.require_version("GstSdp", "1.0")
    from gi.repository import Gst as _Gst, GLib as _GLib
    from gi.repository import GstSdp as _GstSdp, GstWebRTC as _GstWebRTC
    Gst = _Gst
    GLib = _GLib
    GstSdp = _GstSdp
    GstWebRTC = _GstWebRTC
    _gst_available = True
except (ImportError, ValueError):
    log.warning("GStreamer WebRTC GI 바인딩 불가")


class WebRTCHandler:
    """WebRTC 시그널링 관리 — 단일 peer 제한."""

    ICE_TIMEOUT = 30  # 초

    def __init__(self):
        self._current_peer_id: str | None = None
        self._ice_candidates: list[dict] = []
        self._ice_buffer: list[dict] = []
        self._ice_timer: threading.Timer | None = None
        self._ice_handler_id: int | None = None
        self._lock = threading.Lock()

    def _reset_peer(self, new_peer_id: str):
        """이전 peer 해제, 새 peer로 전환"""
        if self._ice_timer is not None:
            self._ice_timer.cancel()
        self._current_peer_id = new_peer_id
        self._ice_candidates = []
        self._ice_buffer = []
        self._schedule_ice_timeout()

    def handle_offer(self, sdp_offer: str, pipeline_manager) -> str:
        """SDP offer → answer 생성.

        GLib.idle_add()로 GStreamer 메인 루프 스레드에서 실행.
        """
        if not _gst_available:
            raise RuntimeError("GStreamer WebRTC not available")
        if not pipeline_manager.is_running():
            raise RuntimeError("Pipeline not running — 먼저 파이프라인을 시작하세요")

        with self._lock:
            self._reset_peer(str(uuid.uuid4()))
            peer_id = self._current_peer_id

        webrtcbin = pipeline_manager.get_webrtcbin()
        if webrtcbin is None:
            raise RuntimeError("webrtcbin 엘리먼트를 찾을 수 없습니다")

        result: dict[str, str] = {}
        event = threading.Event()

        def _do_offer():
            try:
                if self._ice_handler_id is not None:
                    try:
                        webrtcbin.disconnect(self._ice_handler_id)
                    except Exception:
                        pass
                self._ice_handler_id = webrtcbin.connect(
                    "on-ice-candidate", self._on_ice_candidate_cb
                )
                _, sdpmsg = GstSdp.SDPMessage.new_from_text(sdp_offer)
                offer = GstWebRTC.WebRTCSessionDescription.new(
                    GstWebRTC.WebRTCSDPType.OFFER, sdpmsg
                )
                promise = Gst.Promise.new_with_change_func(
                    lambda p: self._on_answer_created(p, result, event, webrtcbin)
                )
                webrtcbin.emit("set-remote-description", offer, None)
                log.info("SDP remote description 설정 완료")
                webrtcbin.emit("create-answer", None, promise)
            except Exception as e:
                log.error("SDP offer 처리 실패: %s", e)
                result["error"] = str(e)
                event.set()

        GLib.idle_add(_do_offer)
        event.wait(timeout=10)

        if not event.is_set():
            raise RuntimeError("SDP answer 생성 타임아웃 (10초)")
        if "error" in result:
            raise RuntimeError(result["error"])
        return result.get("sdp", "")

    def _on_answer_created(self, promise, result: dict, event: threading.Event,
                           webrtcbin):
        """create-answer 콜백 — SDP answer를 추출하여 result에 저장"""
        try:
            reply = promise.get_reply()
            answer = reply.get_value("answer")
            webrtcbin.emit("set-local-description", answer, None)
            sdp_text = answer.sdp.as_text()
            result["sdp"] = sdp_text
            log.info("SDP answer 생성 완료 (길이=%d)", len(sdp_text))
        except Exception as e:
            log.error("SDP answer 생성 실패: %s", e)
            result["error"] = str(e)
        finally:
            event.set()

    def _on_ice_candidate_cb(self, element, mline_index: int, candidate: str):
        """webrtcbin on-ice-candidate 시그널 콜백"""
        log.debug("ICE candidate: mline=%d %s", mline_index, candidate[:60])
        with self._lock:
            self._ice_candidates.append({
                "sdpMLineIndex": mline_index,
                "sdpMid": str(mline_index),
                "candidate": candidate,
            })

    def handle_ice(self, sdp_mline_index: int, candidate: str, pipeline_manager):
        """클라이언트 ICE candidate를 webrtcbin에 추가"""
        if not _gst_available:
            self._buffer_ice_candidate(sdp_mline_index, candidate)
            return

        webrtcbin = pipeline_manager.get_webrtcbin()
        if webrtcbin is None:
            self._buffer_ice_candidate(sdp_mline_index, candidate)
            return

        GLib.idle_add(webrtcbin.emit, "add-ice-candidate", sdp_mline_index, candidate)

    def _buffer_ice_candidate(self, index: int, candidate: str):
        """GStreamer 없을 때 ICE candidate 버퍼에 저장"""
        self._ice_buffer.append({
            "sdpMLineIndex": index,
            "candidate": candidate,
        })

    def get_server_ice_candidates(self) -> list[dict]:
        """서버측 ICE 후보 반환 + 비움"""
        with self._lock:
            candidates = list(self._ice_candidates)
            self._ice_candidates = []
        return candidates

    def _schedule_ice_timeout(self):
        """ICE 연결 타임아웃 — 30초 후 정리"""
        if self._ice_timer is not None:
            self._ice_timer.cancel()
        self._ice_timer = threading.Timer(
            self.ICE_TIMEOUT, self._cleanup_stale_peer
        )
        self._ice_timer.daemon = True
        self._ice_timer.start()

    def _cleanup_stale_peer(self):
        """ICE 타임아웃 시 peer 정리"""
        log.warning("ICE 타임아웃 (%ds) — peer 정리", self.ICE_TIMEOUT)
        with self._lock:
            self._current_peer_id = None
            self._ice_candidates = []
            self._ice_buffer = []
