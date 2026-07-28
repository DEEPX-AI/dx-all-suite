"""11개 프리셋 데모 정의 + GStreamer 파이프라인 문자열 생성.

run_demo.sh의 11개 데모 매핑을 Python으로 재구성.
fpsdisplaysink를 videoconvert ! encoder ! rtph264pay ! webrtcbin으로 교체.
"""
from __future__ import annotations

import math
from pathlib import Path
from dx_stream.core.config import DX_STREAM_SRC, MODELS_DIR, CONFIGS_DIR, PIPELINES_DIR, VIDEOS_DIR
from dx_stream.core.pipeline import payloader_with_payload_type
import os

# model_list.json v2_4_0 renamed sample models to <name>_640x640.dxnn (efficientnet is
# 256x256); PPU models keep their names. Map the logical names used in DEMOS/pipelines to
# the actual on-disk files so the Demo Launcher resolves models after a fresh sample setup.
_MODEL_ALIAS = {
    "yolo26n.dxnn": "yolo26-n_640x640.dxnn",
    "YOLOv5s_Face.dxnn": "yolov5-s-face_640x640.dxnn",
    "yolo26n-pose.dxnn": "yolo26-n-pose_640x640.dxnn",
    "yolo26n-seg.dxnn": "yolo26-n-seg_640x640.dxnn",
    "YoloV5S_PPU.dxnn": "yolov5-s_640x640_ppu.dxnn",
    "EfficientNet_Lite0.dxnn": "efficientnet-lite0_256x256.dxnn",
    "SCRFD500M.dxnn": "scrfd-500m_640x640.dxnn",
}


def _model_file(name: str) -> str:
    """Resolve a logical model name to its actual on-disk file (alias-aware)."""
    return _MODEL_ALIAS.get(name, name)


_VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv"}


def _video_path(name: str):
    """Find a sample video by file name anywhere under VIDEOS_DIR (the tarball extracts
    into a sample_videos/ subdir), or None."""
    if not VIDEOS_DIR.exists():
        return None
    direct = VIDEOS_DIR / name
    if direct.is_file():
        return direct
    for f in VIDEOS_DIR.rglob(name):
        if f.is_file():
            return f
    return None


def _first_video():
    if VIDEOS_DIR.exists():
        for f in sorted(VIDEOS_DIR.rglob("*")):
            if f.is_file() and f.suffix.lower() in _VIDEO_EXTS:
                return f"file://{f.resolve()}"
    return f"file://{DX_STREAM_SRC}/samples/videos/sample_videos/boat.mp4"


_DEFAULT_VIDEO = _first_video()

_POSTPROC_LIB_DIR = os.environ.get("DX_POSTPROC_LIB_DIR", "/usr/local/share/gstdxstream/lib")

_REASON_LABELS_EN = {
    "missing_model": "Model not installed",
    "missing_config_file": "Missing config file",
    "missing_runtime_script": "Missing runtime script",
    "missing_sample_video": "Missing sample video",
    "missing_npu_device": "NPU device not found",
    "missing_dxstream_plugin": "DxStream GStreamer plugin not installed (run build.sh)",
}


def _format_reason_item(item: dict) -> str:
    code = item.get("code", "")
    label = _REASON_LABELS_EN.get(code, code) if code else "unknown"
    path = item.get("path")
    return f"{label}: {path}" if path else label

# 11개 프리셋 데모 정의 (run_demo.sh 매핑)
DEMOS = [
    {
        "id": 0,
        "name_ko": "객체 감지",
        "name_en": "Object Detection",
        "category": "object_detection",
        "model": "yolo26n.dxnn",
        "description_ko": "YOLOv26n 기반 기본 객체 감지",
        "description_en": "Basic object detection with YOLOv26n",
        "pipeline_type": "standard",
        "preprocess_id": 1,
        "resize": (640, 640),
        "postproc_lib": f"{_POSTPROC_LIB_DIR}/libpostprocess_yolo26od.so",
        "postproc_func": "PostProcess",
        "runtime_script": "single_network/object_detection/run_yolo26n.sh",
        "required_videos": ["blackbox-city-road.mp4"],
    },
    {
        "id": 1,
        "name_ko": "객체 감지 (PPU)",
        "name_en": "Object Detection PPU",
        "category": "object_detection",
        "model": "YoloV5S_PPU.dxnn",
        "description_ko": "YOLOv5S 하드웨어 후처리 사용",
        "description_en": "YOLOv5S with hardware post-processing unit",
        "pipeline_type": "config",
        "config_dir": "YoloV5S_PPU",
        "runtime_script": "single_network/object_detection/run_YoloV5S_PPU.sh",
        "required_configs": ["YoloV5S_PPU"],
        "required_videos": ["blackbox-city-road.mp4"],
    },
    {
        "id": 2,
        "name_ko": "얼굴 감지",
        "name_en": "Face Detection",
        "category": "face_detection",
        "model": "YOLOv5s_Face.dxnn",
        "description_ko": "YOLOv5s 기반 얼굴 감지",
        "description_en": "Face detection with YOLOv5s_Face",
        "pipeline_type": "standard",
        "preprocess_id": 1,
        "resize": (640, 640),
        "postproc_lib": f"{_POSTPROC_LIB_DIR}/libpostprocess_yolov5s_face.so",
        "postproc_func": "PostProcess",
        "runtime_script": "single_network/face_detection/run_YOLOv5s_Face.sh",
        "required_videos": ["dance-group.mov"],
    },
    {
        "id": 3,
        "name_ko": "얼굴 감지 (PPU)",
        "name_en": "Face Detection PPU",
        "category": "face_detection",
        "model": "SCRFD500M_PPU.dxnn",
        "description_ko": "SCRFD500M PPU 얼굴 감지",
        "description_en": "Face detection with SCRFD500M PPU",
        "pipeline_type": "standard",
        "preprocess_id": 1,
        "resize": (640, 640),
        "postproc_lib": f"{_POSTPROC_LIB_DIR}/libpostprocess_ppu.so",
        "postproc_func": "SCRFD500M_PPU",
        "runtime_script": "single_network/face_detection/run_SCRFD500M_PPU.sh",
        "required_videos": ["dance-group.mov"],
    },
    {
        "id": 4,
        "name_ko": "자세 추정",
        "name_en": "Pose Estimation",
        "category": "pose_estimation",
        "model": "yolo26n-pose.dxnn",
        "description_ko": "YOLOv26n 기반 자세 추정",
        "description_en": "Pose estimation with YOLOv26n",
        "pipeline_type": "standard",
        "preprocess_id": 1,
        "resize": (640, 640),
        "postproc_lib": f"{_POSTPROC_LIB_DIR}/libpostprocess_yolo26pose.so",
        "postproc_func": "PostProcess",
        "runtime_script": "single_network/pose_estimation/run_yolo26n-pose.sh",
        "required_videos": ["dance-group.mov"],
    },
    {
        "id": 5,
        "name_ko": "자세 추정 (PPU)",
        "name_en": "Pose Estimation PPU",
        "category": "pose_estimation",
        "model": "YOLOV5Pose_PPU.dxnn",
        "description_ko": "YOLOV5Pose PPU 자세 추정",
        "description_en": "Pose estimation with YOLOV5Pose PPU",
        "pipeline_type": "standard",
        "preprocess_id": 1,
        "resize": (640, 640),
        "postproc_lib": f"{_POSTPROC_LIB_DIR}/libpostprocess_ppu.so",
        "postproc_func": "YOLOV5Pose_PPU",
        "runtime_script": "single_network/pose_estimation/run_YOLOV5Pose_PPU.sh",
        "required_videos": ["dance-group.mov"],
    },
    {
        "id": 6,
        "name_ko": "인스턴스 세그멘테이션",
        "name_en": "Instance Segmentation",
        "category": "segmentation",
        "model": "yolo26n-seg.dxnn",
        "description_ko": "YOLOv26n 기반 인스턴스 세그멘테이션",
        "description_en": "Instance segmentation with YOLOv26n",
        "pipeline_type": "standard",
        "preprocess_id": 1,
        "resize": (640, 640),
        "postproc_lib": f"{_POSTPROC_LIB_DIR}/libpostprocess_yolo26seg.so",
        "postproc_func": "PostProcess",
        "runtime_script": "single_network/instance_segmentation/run_yolo26n-seg.sh",
        "required_videos": ["blackbox-city-road.mp4"],
    },
    {
        "id": 7,
        "name_ko": "다중 객체 추적",
        "name_en": "Multi-Object Tracking",
        "category": "tracking",
        "model": "YoloV5S_PPU.dxnn",
        "description_ko": "OC_SORT 알고리즘 기반 객체 추적",
        "description_en": "Multi-object tracking with OC_SORT algorithm",
        "pipeline_type": "tracking",
        "config_dir": "YoloV5S_PPU",
        "runtime_script": "tracking/run_multi_object_tracker.sh",
        "required_configs": ["YoloV5S_PPU"],
        "required_files": ["tracker_config.json"],
        "required_videos": ["blackbox-city-road.mp4"],
    },
    {
        "id": 8,
        "name_ko": "멀티 스트림",
        "name_en": "Multi-Stream",
        "category": "multi_stream",
        "model": "YoloV5S_PPU.dxnn",
        "description_ko": "4채널 2×2 다중 비디오 스트림",
        "description_en": "4-channel 2×2 multi-video stream",
        "pipeline_type": "multi",
        "runtime_script": "multi_stream/run_multi_stream.sh",
        "required_configs": ["YoloV5S_PPU"],
        "required_videos": ["blackbox-city-road.mp4"],
    },
    {
        "id": 9,
        "name_ko": "멀티 스트림 (RTSP)",
        "name_en": "Multi-Stream RTSP",
        "category": "multi_stream",
        "model": "YoloV5S_PPU.dxnn",
        "description_ko": "네트워크 카메라 RTSP 입력",
        "description_en": "Network camera RTSP input",
        "pipeline_type": "rtsp",
        "runtime_script": "rtsp/run_RTSP.sh",
        "required_configs": ["YoloV5S_PPU"],
    },
    {
        "id": 10,
        "name_ko": "2차 추론",
        "name_en": "Secondary Inference",
        "category": "secondary",
        "model": "YoloV5S_PPU.dxnn",
        "models": ["YoloV5S_PPU.dxnn", "EfficientNet_Lite0.dxnn", "SCRFD500M.dxnn"],
        "description_ko": "1차 감지 후 2차 분류 및 얼굴 인식",
        "description_en": "Primary detection + secondary classification/face recognition",
        "pipeline_type": "secondary",
        "config_dir": "YoloV5S_PPU",
        "runtime_script": "secondary_mode/run_secondary_mode.sh",
        "required_configs": ["YoloV5S_PPU"],
        "required_files": ["tracker_config.json"],
        "required_videos": ["dance-group.mov"],
    },
]

_DEMO_I18N = {
    0: {
        "name_ja": "物体検出",
        "name_es": "Detección de objetos",
        "name_zh-CN": "目标检测",
        "name_zh-TW": "物件偵測",
        "description_ja": "YOLOv26nによる基本的な物体検出",
        "description_es": "Detección básica de objetos con YOLOv26n",
        "description_zh-CN": "基于 YOLOv26n 的基础目标检测",
        "description_zh-TW": "基於 YOLOv26n 的基本物件偵測",
    },
    1: {
        "name_ja": "物体検出 PPU",
        "name_es": "Detección de objetos PPU",
        "name_zh-CN": "目标检测 PPU",
        "name_zh-TW": "物件偵測 PPU",
        "description_ja": "ハードウェア後処理ユニットを使用したYOLOv5S",
        "description_es": "YOLOv5S con unidad de posprocesamiento por hardware",
        "description_zh-CN": "使用硬件后处理单元的 YOLOv5S",
        "description_zh-TW": "使用硬體後處理單元的 YOLOv5S",
    },
    2: {
        "name_ja": "顔検出",
        "name_es": "Detección de rostros",
        "name_zh-CN": "人脸检测",
        "name_zh-TW": "人臉偵測",
        "description_ja": "YOLOv5s_Faceによる顔検出",
        "description_es": "Detección de rostros con YOLOv5s_Face",
        "description_zh-CN": "使用 YOLOv5s_Face 的人脸检测",
        "description_zh-TW": "使用 YOLOv5s_Face 的人臉偵測",
    },
    3: {
        "name_ja": "顔検出 PPU",
        "name_es": "Detección de rostros PPU",
        "name_zh-CN": "人脸检测 PPU",
        "name_zh-TW": "人臉偵測 PPU",
        "description_ja": "SCRFD500M PPUによる顔検出",
        "description_es": "Detección de rostros con SCRFD500M PPU",
        "description_zh-CN": "使用 SCRFD500M PPU 的人脸检测",
        "description_zh-TW": "使用 SCRFD500M PPU 的人臉偵測",
    },
    4: {
        "name_ja": "姿勢推定",
        "name_es": "Estimación de pose",
        "name_zh-CN": "姿态估计",
        "name_zh-TW": "姿勢估計",
        "description_ja": "YOLOv26nによる姿勢推定",
        "description_es": "Estimación de pose con YOLOv26n",
        "description_zh-CN": "使用 YOLOv26n 的姿态估计",
        "description_zh-TW": "使用 YOLOv26n 的姿勢估計",
    },
    5: {
        "name_ja": "姿勢推定 PPU",
        "name_es": "Estimación de pose PPU",
        "name_zh-CN": "姿态估计 PPU",
        "name_zh-TW": "姿勢估計 PPU",
        "description_ja": "YOLOV5Pose PPUによる姿勢推定",
        "description_es": "Estimación de pose con YOLOV5Pose PPU",
        "description_zh-CN": "使用 YOLOV5Pose PPU 的姿态估计",
        "description_zh-TW": "使用 YOLOV5Pose PPU 的姿勢估計",
    },
    6: {
        "name_ja": "セマンティックセグメンテーション",
        "name_es": "Segmentación semántica",
        "name_zh-CN": "语义分割",
        "name_zh-TW": "語意分割",
        "description_ja": "YOLOv26nによるセマンティックセグメンテーション",
        "description_es": "Segmentación semántica con YOLOv26n",
        "description_zh-CN": "使用 YOLOv26n 的语义分割",
        "description_zh-TW": "使用 YOLOv26n 的語意分割",
    },
    7: {
        "name_ja": "複数物体追跡",
        "name_es": "Seguimiento multiobjeto",
        "name_zh-CN": "多目标跟踪",
        "name_zh-TW": "多物件追蹤",
        "description_ja": "OC_SORTアルゴリズムによる複数物体追跡",
        "description_es": "Seguimiento multiobjeto con el algoritmo OC_SORT",
        "description_zh-CN": "基于 OC_SORT 算法的多目标跟踪",
        "description_zh-TW": "基於 OC_SORT 演算法的多物件追蹤",
    },
    8: {
        "name_ja": "マルチストリーム",
        "name_es": "Multi-stream",
        "name_zh-CN": "多路流",
        "name_zh-TW": "多路串流",
        "description_ja": "4チャンネル2×2マルチビデオストリーム",
        "description_es": "Stream de video múltiple 2×2 de 4 canales",
        "description_zh-CN": "4 通道 2×2 多视频流",
        "description_zh-TW": "4 通道 2×2 多影片串流",
    },
    9: {
        "name_ja": "マルチストリーム RTSP",
        "name_es": "Multi-stream RTSP",
        "name_zh-CN": "多路流 RTSP",
        "name_zh-TW": "多路串流 RTSP",
        "description_ja": "ネットワークカメラRTSP入力",
        "description_es": "Entrada RTSP de cámara de red",
        "description_zh-CN": "网络摄像头 RTSP 输入",
        "description_zh-TW": "網路攝影機 RTSP 輸入",
    },
    10: {
        "name_ja": "二次推論",
        "name_es": "Inferencia secundaria",
        "name_zh-CN": "二次推理",
        "name_zh-TW": "二次推論",
        "description_ja": "一次検出後の二次分類と顔認識",
        "description_es": "Detección primaria más clasificación secundaria y reconocimiento facial",
        "description_zh-CN": "主检测后的二次分类和人脸识别",
        "description_zh-TW": "主要偵測後的二次分類與人臉辨識",
    },
}

for _demo in DEMOS:
    _demo.update(_DEMO_I18N.get(_demo["id"], {}))

# No stun-server: air-gapped board can't reach public STUN → ICE stalls at "checking"
# (error 701). Same-LAN host candidates connect without it. See pipeline.get_webrtc_sink_str.
_WEBRTC_SINK = "videoconvert ! {encoder} ! {payloader} ! " \
               "webrtcbin name=sendrecv bundle-policy=max-bundle"

_NATIVE_SINK = "videoconvert ! fpsdisplaysink sync=false"


def _get_sink(encoder: dict, webrtc_ok: bool = True) -> str:
    """WebRTC 가용 시 webrtcbin, 아니면 fpsdisplaysink 반환."""
    if webrtc_ok:
        values = dict(encoder)
        values["payloader"] = payloader_with_payload_type(
            values["payloader"], values.get("payload_type")
        )
        return _WEBRTC_SINK.format(**values)
    return _NATIVE_SINK


def _standard_pipeline(demo: dict, encoder: dict, video_uri: str, webrtc_ok: bool = True) -> str:
    """일반 파이프라인 (개별 속성 방식) — 데모 0,2,3,4,5,6"""
    w, h = demo["resize"]
    model_path = str(MODELS_DIR / _model_file(demo["model"]))
    sink = _get_sink(encoder, webrtc_ok)
    return (
        f"urisourcebin uri={video_uri} ! decodebin ! "
        f"dxpreprocess preprocess-id={demo['preprocess_id']} "
        f"resize-width={w} resize-height={h} ! "
        f"queue max-size-buffers=1 ! "
        f"dxinfer preprocess-id={demo['preprocess_id']} "
        f"inference-id=1 model-path={model_path} ! "
        f"queue max-size-buffers=1 ! "
        f"dxpostprocess inference-id=1 "
        f"library-file-path={demo['postproc_lib']} "
        f"function-name={demo['postproc_func']} ! "
        f"queue max-size-buffers=1 ! "
        f"dxosd ! {sink}"
    )


def _config_pipeline(demo: dict, encoder: dict, video_uri: str, webrtc_ok: bool = True) -> str:
    """PPU 설정 파일 방식 파이프라인 — 데모 1"""
    cfg = str(CONFIGS_DIR / demo["config_dir"])
    sink = _get_sink(encoder, webrtc_ok)
    return (
        f"urisourcebin uri={video_uri} ! decodebin ! "
        f"dxpreprocess config-file-path={cfg}/preprocess_config.json ! queue ! "
        f"dxinfer config-file-path={cfg}/inference_config.json ! queue ! "
        f"dxpostprocess config-file-path={cfg}/postprocess_config.json ! queue ! "
        f"dxosd ! queue ! {sink}"
    )


def _tracking_pipeline(demo: dict, encoder: dict, video_uri: str, webrtc_ok: bool = True) -> str:
    """트래킹 파이프라인 — 데모 7"""
    cfg = str(CONFIGS_DIR / demo["config_dir"])
    tracker_cfg = str(CONFIGS_DIR / "tracker_config.json")
    sink = _get_sink(encoder, webrtc_ok)
    return (
        f"urisourcebin uri={video_uri} ! decodebin ! "
        f"dxpreprocess config-file-path={cfg}/preprocess_config.json ! queue ! "
        f"dxinfer config-file-path={cfg}/inference_config.json ! queue ! "
        f"dxpostprocess config-file-path={cfg}/postprocess_config.json ! queue ! "
        f"dxtracker config-file-path={tracker_cfg} ! queue ! "
        f"dxosd ! queue ! {sink}"
    )


def _get_video_files(max_count: int = 4) -> list[str]:
    """VIDEOS_DIR에서 영상 파일을 최대 max_count개 반환."""
    files = sorted(
        f for f in VIDEOS_DIR.rglob("*")
        if f.is_file() and f.suffix.lower() in _VIDEO_EXTS
    ) if VIDEOS_DIR.exists() else []
    uris = [f"file://{f.resolve()}" for f in files[:max_count]]
    return uris if uris else [_DEFAULT_VIDEO]


def _multi_pipeline(demo: dict, encoder: dict, video_uri: str, webrtc_ok: bool = True) -> str:
    """멀티스트림 파이프라인 — 데모 8 (compositor 4채널 합성)"""
    cfg = str(CONFIGS_DIR / "YoloV5S_PPU")
    sink = _get_sink(encoder, webrtc_ok)

    videos = _get_video_files(max_count=4)
    if not videos:
        videos = [video_uri]
    num = len(videos)
    cols = math.ceil(math.sqrt(num))
    rows = math.ceil(num / cols)
    sw, sh = 1280 // cols, 720 // rows

    parts = []
    comp_props = []
    for i, v in enumerate(videos):
        col_idx = i % cols
        row_idx = i // cols
        xpos, ypos = col_idx * sw, row_idx * sh
        parts.append(
            f"urisourcebin uri={v} ! queue max-size-buffers=10 ! decodebin ! queue max-size-buffers=10 ! "
            f"dxpreprocess config-file-path={cfg}/preprocess_config.json ! queue max-size-buffers=10 ! "
            f"dxinfer config-file-path={cfg}/inference_config.json ! queue max-size-buffers=10 ! "
            f"dxpostprocess config-file-path={cfg}/postprocess_config.json ! queue max-size-buffers=10 ! "
            f"dxosd ! queue max-size-buffers=10 ! "
            f"dxscale width={sw} height={sh} ! queue max-size-buffers=10 ! comp.sink_{i}"
        )
        comp_props.append(f"sink_{i}::xpos={xpos} sink_{i}::ypos={ypos}")

    pipeline_str = " ".join(parts)
    comp = f"compositor name=comp {' '.join(comp_props)}"
    return f"{pipeline_str} {comp} ! {sink}"


def _rtsp_pipeline(demo: dict, encoder: dict, video_uri: str, webrtc_ok: bool = True) -> str:
    """RTSP 멀티스트림 파이프라인 — 데모 9

    Runtime run_RTSP.sh와 동일 아키텍처:
    4×rtspsrc → dxinputselector → 공유 추론 → dxoutputselector → compositor → webrtcbin
    """
    cfg = str(CONFIGS_DIR / "YoloV5S_PPU")
    sink = _get_sink(encoder, webrtc_ok)
    if video_uri.startswith("rtsp://"):
        base_rtsp = video_uri
        use_cctv_format = False
        # A user-supplied URL is a single camera → one full-frame tile (no channel-index suffix).
        num, cols, rows = 1, 1, 1
    else:
        base_rtsp = "rtsp://210.99.70.120:1935/live/cctv"
        use_cctv_format = True
        num, cols, rows = 4, 2, 2
    sw, sh = 1280 // cols, 720 // rows

    # 입력 브랜치: RTSP → dxinputselector
    input_parts = []
    for i in range(num):
        if use_cctv_format:
            uri = f"{base_rtsp}{i + 3:03d}.stream"
        else:
            uri = base_rtsp  # user's single-camera URL, used verbatim
        input_parts.append(
            f"rtspsrc location={uri} latency=100 ! "
            f"decodebin ! queue max-size-buffers=2 ! in.sink_{i}"
        )

    # 공유 추론 파이프라인
    shared = (
        f"dxinputselector name=in ! "
        f"dxpreprocess config-file-path={cfg}/preprocess_config.json ! "
        f"queue max-size-buffers=2 ! "
        f"dxinfer config-file-path={cfg}/inference_config.json ! "
        f"queue max-size-buffers=2 ! "
        f"dxpostprocess config-file-path={cfg}/postprocess_config.json ! "
        f"queue max-size-buffers=2 ! "
        f"dxosd ! dxoutputselector name=out"
    )

    # 출력 브랜치: dxoutputselector → dxscale → compositor
    output_parts = []
    comp_props = []
    for i in range(num):
        col_idx = i % cols
        row_idx = i // cols
        xpos, ypos = col_idx * sw, row_idx * sh
        output_parts.append(
            f"out.src_{i} ! queue max-size-buffers=2 ! "
            f"dxscale width={sw} height={sh} ! "
            f"queue max-size-buffers=2 ! comp.sink_{i}"
        )
        comp_props.append(f"sink_{i}::xpos={xpos} sink_{i}::ypos={ypos}")

    comp = f"compositor name=comp {' '.join(comp_props)}"
    return f"{' '.join(input_parts)} {shared} {' '.join(output_parts)} {comp} ! {sink}"


def _secondary_pipeline(demo: dict, encoder: dict, video_uri: str, webrtc_ok: bool = True) -> str:
    """2차 추론 파이프라인 — 데모 10 (1차 감지 + 2차 분류 + 2차 얼굴)"""
    _SECONDARY_PREFERRED = ["dance-group.mov", "dance-group2.mov", "dance-solo.mov"]
    actual_uri = video_uri
    if actual_uri == _DEFAULT_VIDEO and VIDEOS_DIR.is_dir():
        for p in _SECONDARY_PREFERRED:
            if (VIDEOS_DIR / p).exists():
                actual_uri = f"file://{VIDEOS_DIR / p}"
                break
    cfg = str(CONFIGS_DIR / "YoloV5S_PPU")
    tracker_cfg = str(CONFIGS_DIR / "tracker_config.json")
    sink = _get_sink(encoder, webrtc_ok)
    models_dir = str(MODELS_DIR)
    lib_dir = _POSTPROC_LIB_DIR
    return (
        f"urisourcebin uri={actual_uri} ! decodebin ! "
        f"dxpreprocess config-file-path={cfg}/preprocess_config.json ! queue ! "
        f"dxinfer config-file-path={cfg}/inference_config.json ! queue ! "
        f"dxpostprocess config-file-path={cfg}/postprocess_config.json ! queue ! "
        f"dxtracker config-file-path={tracker_cfg} ! queue ! "
        f"tee name=t "
        f"t. ! queue ! "
        f"dxpreprocess preprocess-id=2 resize-width=224 resize-height=224 "
        f"secondary-mode=true interval=5 min-object-width=50 min-object-height=50 keep-ratio=false ! "
        f"queue max-size-buffers=1 ! "
        f"dxinfer preprocess-id=2 inference-id=2 secondary-mode=true "
        f"model-path={models_dir}/{_model_file('EfficientNet_Lite0.dxnn')} ! "
        f"queue max-size-buffers=1 ! "
        f"dxpostprocess inference-id=2 secondary-mode=true "
        f"library-file-path={lib_dir}/libpostprocess_object_class.so function-name=PostProcess ! "
        f"queue max-size-buffers=1 ! gather.sink_0 "
        f"t. ! queue ! "
        f"dxpreprocess preprocess-id=3 resize-width=640 resize-height=640 "
        f"secondary-mode=true target-class-id=0 min-object-width=50 min-object-height=50 "
        f"interval=5 keep-ratio=true pad-value=114 ! "
        f"queue max-size-buffers=1 ! "
        f"dxinfer preprocess-id=3 inference-id=3 secondary-mode=true "
        f"model-path={models_dir}/{_model_file('SCRFD500M.dxnn')} ! "
        f"queue max-size-buffers=1 ! "
        f"dxpostprocess inference-id=3 secondary-mode=true "
        f"library-file-path={lib_dir}/libpostprocess_scrfd500m.so function-name=PostProcess ! "
        f"queue max-size-buffers=1 ! gather.sink_1 "
        f"dxgather name=gather ! queue ! dxosd ! queue ! {sink}"
    )


_BUILDERS = {
    "standard": _standard_pipeline,
    "config": _config_pipeline,
    "tracking": _tracking_pipeline,
    "multi": _multi_pipeline,
    "rtsp": _rtsp_pipeline,
    "secondary": _secondary_pipeline,
}


def build_pipeline_str(demo_id: int, encoder: dict, video_uri: str | None = None,
                       webrtc_ok: bool = True) -> str:
    """데모별 GStreamer 파이프라인 문자열 생성.

    webrtc_ok=True: encoder + webrtcbin, False: fpsdisplaysink 폴백.
    """
    demo = DEMOS[demo_id]
    # Default to the demo's OWN task-appropriate sample video (matching dx-runtime's
    # reference run_*.sh — e.g. face/pose demos use people videos, not a boat clip).
    # Fall back to the first available video only if the demo's video is missing.
    demo_vid = None
    for _name in demo.get("required_videos", []):
        _vp = _video_path(_name)  # returns a bare Path (or None)
        if _vp:
            demo_vid = f"file://{_vp}"  # GStreamer urisourcebin needs a file:// URI, not a bare path
            break
    uri = video_uri or demo_vid or _DEFAULT_VIDEO
    builder = _BUILDERS[demo["pipeline_type"]]
    return builder(demo, encoder, uri, webrtc_ok)


def _npu_exists() -> bool:
    """NPU 장치 존재 여부 확인 (테스트에서 monkeypatch 가능)."""
    return len(list(Path("/dev").glob("dxrt*"))) > 0


def _plugin_exists() -> bool:
    """DxStream GStreamer 플러그인 존재 여부 확인 (테스트에서 monkeypatch 가능).

    Delegates to the unified finder (core.gst_env) so every call site agrees on the set of
    locations checked (previously this only looked under /usr/local/lib)."""
    from dx_stream.core import gst_env

    return gst_env.plugin_available()


def check_demo_available(demo_id: int) -> dict:
    """데모 실행 가능 여부 확인 — 모델·설정·스크립트·비디오·NPU·플러그인 확인"""
    demo = DEMOS[demo_id]
    reason_items = []

    model_files = demo.get("models", [demo["model"]] if "model" in demo else [])
    for mf in model_files:
        if not (MODELS_DIR / _model_file(mf)).exists():
            reason_items.append({"code": "missing_model", "path": mf})

    for config_dir in demo.get("required_configs", []):
        for cfg in ("preprocess_config.json", "inference_config.json", "postprocess_config.json"):
            if not (CONFIGS_DIR / config_dir / cfg).exists():
                reason_items.append({"code": "missing_config_file", "path": f"{config_dir}/{cfg}"})

    for rel in demo.get("required_files", []):
        if not (CONFIGS_DIR / rel).exists():
            reason_items.append({"code": "missing_config_file", "path": rel})

    script = demo.get("runtime_script")
    if script:
        if not (PIPELINES_DIR / script).exists():
            reason_items.append({"code": "missing_runtime_script", "path": script})

    for video in demo.get("required_videos", []):
        if not _video_path(video):
            reason_items.append({"code": "missing_sample_video", "path": video})

    if not _npu_exists():
        reason_items.append({"code": "missing_npu_device"})

    if not _plugin_exists():
        reason_items.append({"code": "missing_dxstream_plugin"})

    return {
        "available": len(reason_items) == 0,
        "reason": "; ".join(_format_reason_item(item) for item in reason_items) if reason_items else "Ready to run",
        "reason_items": reason_items,
        "demo_id": demo_id,
    }


def list_demo_entries() -> list[dict]:
    """Return demo metadata enriched for the web UI."""
    demo_list = []
    for demo in DEMOS:
        entry = dict(demo)
        entry["default_video"] = _DEFAULT_VIDEO
        entry["availability"] = check_demo_available(demo["id"])
        entry["available"] = entry["availability"].get("available", False)
        demo_list.append(entry)
    return demo_list
