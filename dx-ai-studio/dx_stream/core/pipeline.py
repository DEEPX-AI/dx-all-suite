"""GStreamer PipelineManager — PyGObject GI 바인딩 기반.

Python GI bindings (gi.repository.Gst, GstWebRTC)을 사용.
import 실패 시 graceful degradation — 파이프라인 직렬화 등 non-GStreamer 기능은 유지.
"""
from __future__ import annotations

import ctypes
import ctypes.util
import logging
import math
import os
import threading
import uuid
from pathlib import Path
from typing import Any

from dx_stream.core import gst_env as _gst_env

log = logging.getLogger(__name__)


def _drain_dxrt_msgqueues():
    """dxrtd 메시지 큐가 가득 차면 dxinfer가 blocking됨 — 시작 시 비우기."""
    try:
        libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)
        # IPC 메시지 큐 ID 조회: msgget(key, 0)
        IPC_NOWAIT = 0x800
        MSG_NOERROR = 0x1000
        buf = ctypes.create_string_buffer(8192)
        for key in [0x2a020467, 0x54020467]:
            msqid = libc.msgget(key, 0)
            if msqid < 0:
                continue
            drained = 0
            while libc.msgrcv(msqid, buf, 8000, 0, IPC_NOWAIT | MSG_NOERROR) >= 0:
                drained += 1
            if drained > 0:
                log.info("dxrtd 메시지 큐 (key=0x%x) %d개 메시지 비움", key, drained)
    except Exception:
        pass

# GI 바인딩 가용성
_gst_available = False
Gst = None
GLib = None

_gst_env.refresh_plugin_environment(prefer_environment=False)

try:
    import gi
    gi.require_version("Gst", "1.0")
    from gi.repository import Gst as _Gst, GLib as _GLib
    _Gst.init(None)
    _gst_env.refresh_plugin_environment(_Gst)
    Gst = _Gst
    GLib = _GLib
    _gst_available = True
except (ImportError, ValueError):
    log.warning("GStreamer GI 바인딩 불가 — 파이프라인 실행 비활성화")

# 인코더 폴백 체인
ENCODER_FALLBACK_CHAIN = [
    # HW H264 (mpph264enc) first on Rockchip: software vp8enc is the throughput bottleneck on
    # ARM (~6-11 fps), while the board's HW H264 block runs near real-time. H264 over webrtcbin
    # needs the browser's exact payload-type + a compatible profile, or the answer comes back
    # "a=inactive" (no video). Both are handled: the client probes its H264 payload-type
    # (preferredPayloadTypes) and the server applies it (_apply_webrtc_payload_types), and we pin
    # profile=baseline (Chrome/Firefox offer constrained-baseline by default, so baseline
    # negotiates cleanly). vp8enc stays right below as the portable software fallback (non-Rockchip
    # hosts and any browser that won't take this H264). config-interval=-1 keeps SPS/PPS inline.
    {"factory": "mpph264enc", "extra": "profile=baseline",
     "payloader": "h264parse ! rtph264pay config-interval=-1",
     "encoding_name": "H264", "payload_type": 96},
    {"factory": "vp8enc", "extra": "deadline=1 cpu-used=8",
     "payloader": "rtpvp8pay",
     "encoding_name": "VP8", "payload_type": 96},
    {"factory": "vaapih264enc", "extra": "",
     "payloader": "rtph264pay config-interval=-1",
     "encoding_name": "H264", "payload_type": 96},
    {"factory": "x264enc", "extra": "tune=zerolatency",
     "payloader": "rtph264pay config-interval=-1",
     "encoding_name": "H264", "payload_type": 96},
    {"factory": "jpegenc", "extra": "",
     "payloader": "rtpjpegpay",
     "encoding_name": "JPEG", "payload_type": 26},
]


def payloader_with_payload_type(payloader: str, payload_type: int | None) -> str:
    if payload_type is None:
        return payloader
    if any(part.startswith("pt=") for part in payloader.split()):
        return payloader
    return f"{payloader} pt={int(payload_type)}"


def detect_encoder() -> dict:
    """사용 가능한 최고 우선순위 인코더 정보를 반환한다.

    Returns:
        dict with keys: encoder, payloader, encoding_name, payload_type
    """
    default = {
        "encoder": "vp8enc deadline=1",
        "payloader": "rtpvp8pay",
        "encoding_name": "VP8",
        "payload_type": 96,
    }
    if not _gst_available:
        return default
    for enc in ENCODER_FALLBACK_CHAIN:
        if Gst.ElementFactory.find(enc["factory"]):
            extra = f" {enc['extra']}" if enc["extra"] else ""
            return {
                "encoder": f"{enc['factory']}{extra}",
                "payloader": enc["payloader"],
                "encoding_name": enc.get("encoding_name", "H264"),
                "payload_type": enc.get("payload_type", 96),
            }
    return default


def get_webrtc_sink_str(encoder: dict) -> str:
    """WebRTC 브라우저 싱크 문자열을 생성한다."""
    payloader = payloader_with_payload_type(
        encoder["payloader"], encoder.get("payload_type")
    )
    return (
        # No stun-server: this board runs air-gapped, so a public STUN host
        # (stun.l.google.com) is unreachable and its failed gathering stalls ICE at
        # "checking" (STUN error 701) → no video. On the same LAN, host candidates
        # connect directly without STUN. Add a LAN TURN/STUN only if cross-subnet is needed.
        f"videoconvert ! {encoder['encoder']} ! {payloader} ! "
        "webrtcbin name=sendrecv bundle-policy=max-bundle"
    )


def _resolve_props(elem_type: str, props: dict) -> dict:
    """프로퍼티 값을 실제 경로로 보정 (라이브러리/모델 경로 자동 해결)."""
    from dx_stream.core import config as _config
    resolved = dict(props)
    # model-path: 절대경로 아니면 MODELS_DIR에서 찾기
    if "model-path" in resolved:
        mp = str(resolved["model-path"])
        if mp and not mp.startswith("/"):
            candidate = _config.MODELS_DIR / mp
            if not candidate.exists() and not mp.endswith(".dxnn"):
                candidate = _config.MODELS_DIR / (mp + ".dxnn")
            if candidate.exists():
                resolved["model-path"] = str(candidate)
    if "config-file-path" in resolved:
        cp = str(resolved["config-file-path"])
        if cp and not cp.startswith("/"):
            candidate = _config.CONFIGS_DIR / cp
            if candidate.exists():
                resolved["config-file-path"] = str(candidate)
    # library-file-path: 절대경로 아니면 postprocess lib dir에서 찾기
    if "library-file-path" in resolved:
        lp = str(resolved["library-file-path"])
        if lp and not lp.startswith("/"):
            import os
            lib_dir = Path(os.environ.get(
                "DX_POSTPROC_LIB_DIR", "/usr/local/share/gstdxstream/lib"))
            # 후보 순서: 원래 이름 → lib*.so → libpostprocess_*.so
            candidates = [
                lib_dir / lp,
                lib_dir / f"{lp}.so",
                lib_dir / f"lib{lp}.so",
                lib_dir / f"libpostprocess_{lp}.so",
            ]
            for c in candidates:
                if c.exists():
                    resolved["library-file-path"] = str(c)
                    break
    return resolved


def pipeline_json_to_gst(pipeline_def: dict) -> str:
    """JSON 파이프라인 정의 → gst-launch 문자열 변환.

    pipeline_def 형식:
      nodes: [{id, type, props: {key: val}}]
      edges: [[src_id, dst_id]] 또는 [{from, to}]

    선형 및 분기(tee/gather) 파이프라인 모두 지원.
    """
    nodes = {n["id"]: n for n in pipeline_def["nodes"]}
    edges = pipeline_def["edges"]

    # Convert edge objects [{from, to}] or [{source, target}] to tuples [(src, dst)]
    if edges and isinstance(edges[0], dict):
        edges = [(e.get("from") or e.get("source"), e.get("to") or e.get("target")) for e in edges]

    # 인접 리스트 구성
    children = {}
    parents = {}
    for src, dst in edges:
        children.setdefault(src, []).append(dst)
        parents.setdefault(dst, []).append(src)

    # 분기점(out-degree > 1) 및 합류점(in-degree > 1) 감지
    branch_nodes = {nid for nid, ch in children.items() if len(ch) > 1}
    merge_nodes = {nid for nid, pa in parents.items() if len(pa) > 1}

    # 분기가 없으면 기존 선형 로직 사용
    if not branch_nodes and not merge_nodes:
        return _linear_pipeline(pipeline_def, nodes, edges)

    # 분기/합류가 있으면 named-link 문법 생성
    return _branching_pipeline(nodes, edges, children, parents, branch_nodes, merge_nodes)


def _linear_pipeline(pipeline_def, nodes, edges):
    """선형 파이프라인 — 위상 정렬 기반."""
    ordered = []
    if edges:
        # 위상 정렬: 엣지 순서에 의존하지 않고 올바른 순서 보장
        dst_set = {dst for _, dst in edges}
        child_map = {}
        for src_id, dst_id in edges:
            child_map[src_id] = dst_id
        # 소스 노드: 어떤 엣지의 dst에도 없는 노드
        source_nodes = [src for src, _ in edges if src not in dst_set]
        if source_nodes:
            current = source_nodes[0]
        else:
            current = edges[0][0]
        visited = set()
        while current and current not in visited:
            ordered.append(current)
            visited.add(current)
            current = child_map.get(current)
    else:
        ordered = [n["id"] for n in pipeline_def["nodes"]]

    # inference-id 자동 연결: dxinfer에서 선언된 inference-id를 dxpostprocess에 전달
    infer_id_map = {}  # preprocess-id → inference-id
    for nid in ordered:
        node = nodes[nid]
        et = node["type"]
        if et.startswith("Dx") or et.startswith("DX"):
            et = et.lower()
        if et == "dxinfer":
            raw = node.get("properties", node.get("props", {}))
            iid = raw.get("inference-id", 1)
            infer_id_map[nid] = iid

    # dxinfer 바로 다음에 오는 dxpostprocess에 inference-id를 연결하기 위해
    # 순서대로 마지막으로 본 inference-id를 추적
    last_inference_id = None

    parts = []
    dx_elements = {"dxpreprocess", "dxinfer", "dxpostprocess", "dxosd",
                   "dxtracker", "dxgather"}

    for i, nid in enumerate(ordered):
        node = nodes[nid]
        elem_type = node["type"]
        # Dx* 엘리먼트는 GStreamer에서 소문자 사용
        if elem_type.startswith("Dx") or elem_type.startswith("DX"):
            elem_type = elem_type.lower()
        raw_props = node.get("properties", node.get("props", {}))
        props = _resolve_props(elem_type, raw_props)

        # dxinfer의 inference-id 기록
        if elem_type == "dxinfer":
            last_inference_id = props.get("inference-id", 1)

        # dxpostprocess에 inference-id 자동 연결 (없으면 직전 dxinfer 것 사용)
        if elem_type == "dxpostprocess" and "inference-id" not in props:
            if last_inference_id is not None:
                props["inference-id"] = last_inference_id

        # library-file-path + function-name 유효성 검증 (없으면 GStreamer가 abort)
        if "library-file-path" in props:
            lib_path = str(props["library-file-path"])
            if not Path(lib_path).exists():
                raise RuntimeError(
                    f"Postprocess library not found: {lib_path}")
            # function-name 검증
            func_name = props.get("function-name", "")
            if func_name:
                import ctypes
                try:
                    lib = ctypes.CDLL(lib_path)
                    if not hasattr(lib, func_name):
                        raise RuntimeError(
                            f"Function '{func_name}' not found in {lib_path}")
                except OSError as e:
                    raise RuntimeError(f"Cannot load library {lib_path}: {e}")
        elem_str = elem_type
        for k, v in props.items():
            if v != "" and v is not None:
                elem_str += f" {k}={v}"
        parts.append(elem_str)

        # dx 엘리먼트 사이에 queue 자동 삽입 (버퍼링 안정성)
        if i < len(ordered) - 1 and elem_type in dx_elements:
            next_node = nodes[ordered[i + 1]]
            next_type = next_node["type"]
            if next_type.startswith("Dx") or next_type.startswith("DX"):
                next_type = next_type.lower()
            if next_type in dx_elements:
                parts.append("queue max-size-buffers=1")

    return " ! ".join(parts)


def _branching_pipeline(nodes, edges, children, parents, branch_nodes, merge_nodes):
    """분기/합류 파이프라인 — GStreamer named-link 문법.

    지원 토폴로지:
      - tee 분기 (out-degree > 1)            → ``t. ! <branch>``
      - dxgather/compositor 합류 (in-degree>1) → ``<branch> ! gather.sink_<i>``
      - **다중 소스 합류(멀티스트림)**: 서로 독립적인 N개의 소스 체인이 각각
        compositor.sink_<i> 로 들어가는 형태. 이전 구현은 첫 번째 소스 체인만
        방출하고 나머지를 통째로 누락시켰다 — 멀티스트림 빌더(데모 8 로드 등)가
        한 스트림만 나오거나 동작하지 않던 원인. 이제 모든 루트를 순회한다.
      - compositor 합류는 들어오는 스트림 수에 맞춰 ``sink_i::xpos/ypos`` 격자를
        자동 배치해 화면이 겹치지 않게 한다.
    """
    def _is(nid, *types):
        return nodes[nid]["type"].lower() in types

    # tee 이름 할당 (out-degree>1 이면서 tee)
    tee_names = {}
    for i, nid in enumerate(sorted(branch_nodes)):
        if _is(nid, "tee"):
            tee_names[nid] = "t" if i == 0 else f"t{i}"

    # gather/compositor 이름 할당 (in-degree>1)
    merge_names = {}
    mc = 0
    for nid in sorted(merge_nodes):
        if _is(nid, "dxgather", "compositor"):
            merge_names[nid] = "gather" if mc == 0 else f"gather{mc}"
            mc += 1

    merge_in_count = {m: len(parents.get(m, [])) for m in merge_names}

    def _grid_props(mid, idx):
        """compositor sink_idx 의 격자 위치 (1280x720 기준)."""
        if not _is(mid, "compositor"):
            return {}
        n = max(1, merge_in_count.get(mid, 1))
        cols = math.ceil(math.sqrt(n))
        rows = math.ceil(n / cols)
        sw, sh = 1280 // cols, 720 // rows
        c, r = idx % cols, idx // cols
        return {f"sink_{idx}::xpos": c * sw, f"sink_{idx}::ypos": r * sh}

    def _node_str(nid, extra_props=None):
        elem = nodes[nid]["type"].lower()
        props = _resolve_props(elem, dict(nodes[nid].get("properties", nodes[nid].get("props", {}))))
        if extra_props:
            props.update(extra_props)
        if nid in tee_names:
            props["name"] = tee_names[nid]
        if nid in merge_names:
            props["name"] = merge_names[nid]
        prop_str = ""
        for k, v in props.items():
            if v != "" and v is not None:
                prop_str += f" {k}={v}"
        return elem + prop_str

    # merge 별 sink pad 인덱스 발급 + compositor grid props 누적
    _sink_idx = {m: 0 for m in merge_names}
    _merge_props = {m: {} for m in merge_names}

    def _take_sink(mid):
        i = _sink_idx[mid]
        _sink_idx[mid] += 1
        _merge_props[mid].update(_grid_props(mid, i))
        return f"{merge_names[mid]}.sink_{i}"

    visited = set()
    segments = []

    def _emit_chain(start, prefix=""):
        """start 부터 선형 체인 방출. tee/merge 경계에서 종료.

        merge 노드를 만나면 ``merge.sink_<i>`` 로 링크하고 끝낸다(merge 정의는 별도).
        """
        chain = []
        cur = start
        while cur is not None and cur not in visited:
            if cur in merge_names:
                chain.append(_take_sink(cur))
                cur = None
                break
            visited.add(cur)
            chain.append(_node_str(cur))
            if cur in tee_names:
                cur = None  # tee 가지는 별도 방출
                break
            ch = children.get(cur, [])
            if len(ch) == 1:
                nxt = ch[0]
                if nxt in merge_names:
                    chain.append(_take_sink(nxt))
                    cur = None
                else:
                    cur = nxt
            else:
                cur = None
        if chain:
            segments.append(prefix + " ! ".join(chain))

    # 1) 모든 소스(root) 체인 방출 — 멀티스트림 핵심 수정
    all_dsts = {dst for _, dst in edges}
    roots = [nid for nid in nodes if nid not in all_dsts]
    if not roots:
        roots = [next(iter(nodes))]
    for r in sorted(roots):
        _emit_chain(r)

    # 2) tee 가지 방출
    for tnid in sorted(tee_names, key=lambda n: tee_names[n]):
        tname = tee_names[tnid]
        for ch_nid in children.get(tnid, []):
            _emit_chain(ch_nid, prefix=f"{tname}. ! ")

    # 3) merge 노드 정의 + 하류 선형 체인 방출 (한 번씩)
    for mnid in sorted(merge_names, key=lambda n: merge_names[n]):
        if mnid in visited:
            continue
        visited.add(mnid)
        ch = children.get(mnid, [])
        tail = []
        cur = ch[0] if len(ch) == 1 else None
        while cur is not None and cur not in visited:
            if cur in merge_names:
                tail.append(_take_sink(cur))
                cur = None
                break
            visited.add(cur)
            tail.append(_node_str(cur))
            if cur in tee_names:
                cur = None
                break
            nch = children.get(cur, [])
            cur = nch[0] if len(nch) == 1 else None
        seg = _node_str(mnid, extra_props=_merge_props.get(mnid))
        if tail:
            seg += " ! " + " ! ".join(tail)
        segments.append(seg)

    return " ".join(segments)


class PipelineManager:
    """GStreamer 파이프라인 매니저 — 동시 실행 1개 제한.

    GLib.MainLoop을 별도 스레드에서 실행한다.
    HTTP 핸들러에서는 GLib.idle_add()로 GStreamer 호출을 마샬링해야 한다.
    """

    def __init__(self):
        self._pipeline = None
        self._pipeline_id: str | None = None
        self._mainloop = None
        self._mainloop_thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self._last_error: str | None = None
        self._extra_env: dict | None = None
        self._saved_env: dict | None = None

    def start(self, pipeline_str: str, extra_env: dict | None = None) -> str:
        """파이프라인 시작. 이미 실행 중이면 이전 것을 중지 후 시작.

        Returns: pipeline_id (UUID)
        Raises: RuntimeError — GStreamer 미설치
        """
        if not _gst_available:
            raise RuntimeError("GStreamer not available — GI 바인딩을 설치하세요")

        # dxrtd 메시지 큐 정리 (이전 프로세스 잔여 메시지로 인한 hang 방지)
        _drain_dxrt_msgqueues()

        with self._lock:
            if self._pipeline is not None:
                self._stop_internal()

            self._pipeline_id = str(uuid.uuid4())
            self._last_error = None
            log.info("파이프라인 시작: %s", self._pipeline_id)

            # Apply any caller-provided environment overrides for this pipeline run
            self._extra_env = extra_env
            self._saved_env = {}
            if self._extra_env:
                for k, v in self._extra_env.items():
                    self._saved_env[k] = os.environ.get(k)
                    os.environ[k] = v

            try:
                _gst_env.refresh_plugin_environment(Gst)
                self._pipeline = Gst.parse_launch(pipeline_str)
            except GLib.Error as e:
                self._pipeline = None
                self._pipeline_id = None
                if self._extra_env:
                    for k in self._extra_env:
                        if self._saved_env.get(k) is None:
                            os.environ.pop(k, None)
                        else:
                            os.environ[k] = self._saved_env[k]
                    self._extra_env = None
                    self._saved_env = {}
                raise RuntimeError(f"파이프라인 파싱 실패: {e.message}")

            # Bus 메시지 핸들링 (set_state 전에 연결해야 에러 감지)
            bus = self._pipeline.get_bus()
            bus.add_signal_watch()
            bus.connect("message::error", self._on_bus_error)
            bus.connect("message::warning", self._on_bus_warning)
            bus.connect("message::eos", self._on_bus_eos)

            if self._mainloop is None or (
                self._mainloop_thread is not None
                and not self._mainloop_thread.is_alive()
            ):
                self._mainloop = GLib.MainLoop()
                self._mainloop_thread = threading.Thread(
                    target=self._mainloop.run, daemon=True
                )
                self._mainloop_thread.start()

            # set_state(PLAYING)을 별도 스레드에서 실행 — NPU 초기화가 blocking될 수 있음
            pipeline_ref = self._pipeline
            state_result = [None]

            def _set_playing():
                state_result[0] = pipeline_ref.set_state(Gst.State.PLAYING)

            t = threading.Thread(target=_set_playing, daemon=True)
            t.start()
            t.join(timeout=10)
            if t.is_alive():
                log.warning("파이프라인 PLAYING 전환 10초 초과 — 비동기 계속")
            elif state_result[0] is not None:
                if state_result[0] == Gst.StateChangeReturn.FAILURE:
                    self._stop_internal()
                    raise RuntimeError("파이프라인 PLAYING 전환 실패")
                log.info("파이프라인 PLAYING 전환: %s", state_result[0])

            return self._pipeline_id

    def get_pipeline(self):
        """현재 GStreamer 파이프라인 객체 반환 (없으면 None)."""
        return self._pipeline

    def stop(self):
        """파이프라인 중지 — EOS 후 NULL"""
        with self._lock:
            self._stop_internal()

    def _stop_internal(self):
        """내부 중지 (lock 외부에서 호출 금지)"""
        if self._pipeline is not None:
            pipeline = self._pipeline
            self._pipeline = None
            self._pipeline_id = None

            def _force_null():
                try:
                    pipeline.set_state(Gst.State.NULL)
                except Exception:
                    pass

            t = threading.Thread(target=_force_null, daemon=True)
            t.start()
            t.join(timeout=3)
            if t.is_alive():
                log.warning("파이프라인 NULL 전환 타임아웃 — 백그라운드 정리 계속")
            log.info("파이프라인 중지 완료")

        # Restore original environment after pipeline stop
        if getattr(self, '_extra_env', None):
            for k in self._extra_env:
                if self._saved_env.get(k) is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = self._saved_env[k]
            self._extra_env = None
            self._saved_env = {}

    def is_running(self) -> bool:
        return self._pipeline is not None

    def get_pipeline_id(self) -> str | None:
        return self._pipeline_id

    def get_webrtcbin(self) -> Any | None:
        """파이프라인에서 webrtcbin 엘리먼트를 반환한다."""
        if self._pipeline is None:
            return None
        return self._pipeline.get_by_name("sendrecv")

    def idle_add(self, callback, *args):
        """GLib.idle_add() 래퍼 — HTTP 스레드에서 GStreamer 호출 시 사용"""
        if _gst_available and GLib:
            GLib.idle_add(callback, *args)
        else:
            callback(*args)

    def _on_bus_error(self, bus, msg):
        err, debug = msg.parse_error()
        log.error("파이프라인 에러: %s (%s)", err.message, debug)
        self._last_error = err.message

    def _on_bus_warning(self, bus, msg):
        warn, debug = msg.parse_warning()
        log.warning("파이프라인 경고: %s", warn.message)

    def _on_bus_eos(self, bus, msg):
        log.info("파이프라인 EOS 수신")

    def get_last_error(self) -> str | None:
        return self._last_error

    def wait_for_initial_error(self, timeout: float = 1.0) -> str | None:
        """짧은 시간 동안 즉시 버스 에러 발생 여부를 폴링한다."""
        import time
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self._last_error is not None:
                return self._last_error
            time.sleep(0.05)
        return self._last_error
