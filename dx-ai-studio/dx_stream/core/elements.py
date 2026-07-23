"""GStreamer 엘리먼트 레퍼런스 — DxStream 커스텀 13개 + GStreamer 표준 소스/싱크.

파이프라인 빌더 팔레트에서 사용.
"""
from __future__ import annotations

# 카테고리별 색상 (pipeline-iso.css와 동기화)
CATEGORY_COLORS = {
    "source": "#3B82F6",
    "preprocess": "#F59E0B",
    "inference": "#8B5CF6",
    "postprocess": "#F59E0B",
    "visualization": "#10B981",
    "tracking": "#EC4899",
    "messaging": "#06B6D4",
    "output": "#10B981",
    "utility": "#6B7280",
}

_ELEMENTS = [
    # DxStream 커스텀 (13개)
    {
        "name": "DxPreprocess",
        "category": "preprocess",
        "description_ko": "프레임 리사이즈, 색변환, ROI 추출",
        "description_en": "Frame resize, color conversion, ROI extraction", "description_es": "Frame resize, color conversion, ROI extraction",
        "properties": [
            {"name": "preprocess-id", "type": "int", "description": "전처리 식별자", "description_ko": "전처리 식별자", "description_en": "Preprocess identifier", "description_es": "Preprocess identifier"},
            {"name": "resize-width", "type": "int", "description": "리사이즈 너비", "description_ko": "리사이즈 너비", "description_en": "Resize width", "description_es": "Resize width"},
            {"name": "resize-height", "type": "int", "description": "리사이즈 높이", "description_ko": "리사이즈 높이", "description_en": "Resize height", "description_es": "Resize height"},
            {"name": "config-file-path", "type": "string", "description": "설정 파일 경로 (PPU 모드)", "description_ko": "설정 파일 경로 (PPU 모드)", "description_en": "Config file path (PPU mode)", "description_es": "Config file path (PPU mode)"},
            {"name": "secondary-mode", "type": "bool", "description_ko": "2차 추론 모드", "description_en": "Secondary inference mode", "description_es": "Secondary inference mode"},
            {"name": "interval", "type": "int", "description_ko": "처리 간격 (프레임 수)", "description_en": "Processing interval (frame count)", "description_es": "Processing interval (frame count)"},
            {"name": "min-object-width", "type": "int", "description_ko": "최소 객체 너비", "description_en": "Minimum object width", "description_es": "Minimum object width"},
            {"name": "min-object-height", "type": "int", "description_ko": "최소 객체 높이", "description_en": "Minimum object height", "description_es": "Minimum object height"},
            {"name": "keep-ratio", "type": "bool", "description_ko": "종횡비 유지", "description_en": "Keep aspect ratio", "description_es": "Keep aspect ratio"},
            {"name": "pad-value", "type": "int", "description_ko": "패딩 값", "description_en": "Padding value", "description_es": "Padding value"},
            {"name": "target-class-id", "type": "int", "description_ko": "대상 클래스 ID", "description_en": "Target class ID", "description_es": "Target class ID"},
        ],
    },
    {
        "name": "DxInfer",
        "category": "inference",
        "description_ko": "NPU에서 .dxnn 모델 실행",
        "description_en": "Run .dxnn model on NPU", "description_es": "Run .dxnn model on NPU",
        "properties": [
            {"name": "preprocess-id", "type": "int", "description": "전처리 식별자", "description_ko": "전처리 식별자", "description_en": "Preprocess identifier", "description_es": "Preprocess identifier"},
            {"name": "inference-id", "type": "int", "description": "추론 식별자", "description_ko": "추론 식별자", "description_en": "Inference identifier", "description_es": "Inference identifier"},
            {"name": "model-path", "type": "string", "description": "모델 파일 경로", "description_ko": "모델 파일 경로", "description_en": "Model file path", "description_es": "Model file path"},
            {"name": "config-file-path", "type": "string", "description": "설정 파일 경로 (PPU 모드)", "description_ko": "설정 파일 경로 (PPU 모드)", "description_en": "Config file path (PPU mode)", "description_es": "Config file path (PPU mode)"},
            {"name": "secondary-mode", "type": "bool", "description_ko": "2차 추론 모드", "description_en": "Secondary inference mode", "description_es": "Secondary inference mode"},
        ],
    },
    {
        "name": "DxPostprocess",
        "category": "postprocess",
        "description_ko": "추론 결과 파싱 (커스텀 .so 라이브러리)",
        "description_en": "Parse inference results with custom .so library", "description_es": "Parse inference results with custom .so library",
        "properties": [
            {"name": "inference-id", "type": "int", "description": "추론 식별자", "description_ko": "추론 식별자", "description_en": "Inference identifier", "description_es": "Inference identifier"},
            {"name": "library-file-path", "type": "string", "description": "후처리 라이브러리 경로", "description_ko": "후처리 라이브러리 경로", "description_en": "Post-process library path", "description_es": "Post-process library path"},
            {"name": "function-name", "type": "string", "description": "후처리 함수명", "description_ko": "후처리 함수명", "description_en": "Post-process function name", "description_es": "Post-process function name"},
            {"name": "config-file-path", "type": "string", "description": "설정 파일 경로 (PPU 모드)", "description_ko": "설정 파일 경로 (PPU 모드)", "description_en": "Config file path (PPU mode)", "description_es": "Config file path (PPU mode)"},
            {"name": "secondary-mode", "type": "bool", "description_ko": "2차 추론 모드", "description_en": "Secondary inference mode", "description_es": "Secondary inference mode"},
        ],
    },
    {
        "name": "DxTracker",
        "category": "tracking",
        "description_ko": "다중 객체 추적 (OC_SORT 알고리즘)",
        "description_en": "Multi-object tracking with OC_SORT algorithm", "description_es": "Multi-object tracking with OC_SORT algorithm",
        "properties": [
            {"name": "config-file-path", "type": "string", "description": "트래커 설정 파일 경로", "description_ko": "트래커 설정 파일 경로", "description_en": "Tracker config file path", "description_es": "Tracker config file path"},
        ],
    },
    {
        "name": "DxOsd",
        "category": "visualization",
        "description_ko": "바운딩 박스, 라벨, 마스크, 포즈 오버레이",
        "description_en": "Bounding box, label, mask, pose overlay", "description_es": "Bounding box, label, mask, pose overlay",
        "properties": [],
    },
    {
        "name": "DxGather",
        "category": "utility",
        "description_ko": "병렬 브랜치 합류",
        "description_en": "Merge parallel branches", "description_es": "Merge parallel branches",
        "properties": [],
    },
    {
        "name": "DxScale",
        "category": "preprocess",
        "description_ko": "HW 가속 스케일링",
        "description_en": "Hardware-accelerated scaling", "description_es": "Hardware-accelerated scaling",
        "properties": [
            {"name": "width", "type": "int", "description": "출력 너비", "description_ko": "출력 너비", "description_en": "Output width", "description_es": "Output width"},
            {"name": "height", "type": "int", "description": "출력 높이", "description_ko": "출력 높이", "description_en": "Output height", "description_es": "Output height"},
        ],
    },
    {
        "name": "DxConvert",
        "category": "preprocess",
        "description_ko": "색공간 변환",
        "description_en": "Color space conversion", "description_es": "Color space conversion",
        "properties": [],
    },
    {
        "name": "DxRate",
        "category": "utility",
        "description_ko": "프레임레이트 제어",
        "description_en": "Frame rate control", "description_es": "Frame rate control",
        "properties": [
            {"name": "rate", "type": "float", "description": "목표 FPS", "description_ko": "목표 FPS", "description_en": "Target FPS", "description_es": "FPS objetivo"},
        ],
    },
    {
        "name": "DxMsgConv",
        "category": "messaging",
        "description_ko": "메타데이터 → JSON 변환",
        "description_en": "Metadata to JSON conversion", "description_es": "Metadata to JSON conversion",
        "properties": [
            {"name": "config-file-path", "type": "string", "description_ko": "메시지 변환 설정 파일", "description_en": "Message conversion config file", "description_es": "Message conversion config file"},
        ],
    },
    {
        "name": "DxMsgBroker",
        "category": "messaging",
        "description_ko": "MQTT/Kafka 메시지 전송",
        "description_en": "MQTT/Kafka message publishing", "description_es": "MQTT/Kafka message publishing",
        "properties": [
            {"name": "proto-lib", "type": "string", "description": "프로토콜 라이브러리 경로", "description_ko": "프로토콜 라이브러리 경로", "description_en": "Protocol library path", "description_es": "Protocol library path"},
            {"name": "conn-str", "type": "string", "description": "연결 문자열", "description_ko": "연결 문자열", "description_en": "Connection string", "description_es": "Connection string"},
            {"name": "topic", "type": "string", "description": "토픽명", "description_ko": "토픽명", "description_en": "Topic name", "description_es": "Topic name"},
            {"name": "broker-name", "type": "string", "description_ko": "브로커 종류 (mqtt/kafka)", "description_en": "Broker type (mqtt/kafka)", "description_es": "Broker type (mqtt/kafka)"},
            {"name": "conn-info", "type": "string", "description_ko": "연결 정보 (host:port)", "description_en": "Connection info (host:port)", "description_es": "Connection info (host:port)"},
            {"name": "config", "type": "string", "description_ko": "브로커 설정 파일 경로", "description_en": "Broker config file path", "description_es": "Broker config file path"},
        ],
    },
    {
        "name": "DxInputSelector",
        "category": "utility",
        "description_ko": "입력 스트림 선택기",
        "description_en": "Input stream selector", "description_es": "Input stream selector",
        "properties": [
            {"name": "name", "type": "string", "description_ko": "엘리먼트 이름", "description_en": "Element name", "description_es": "Element name"},
        ],
    },
    {
        "name": "DxOutputSelector",
        "category": "utility",
        "description_ko": "출력 스트림 선택기",
        "description_en": "Output stream selector", "description_es": "Output stream selector",
        "properties": [
            {"name": "name", "type": "string", "description_ko": "엘리먼트 이름", "description_en": "Element name", "description_es": "Element name"},
        ],
    },
    # DX-VNPU hardware video codec / VO elements (dx_stream staging, v3.1.0+).
    # NOTE: these require the VNPU-enabled dx_stream plugin (staging .so); on an older installed
    # plugin they won't be found at run time. Properties mirror the staging element docs.
    {
        "name": "DxVnpuDec",
        "category": "source",
        "description_ko": "VNPU 하드웨어 비디오 디코더 (H.264/H.265 → raw)",
        "description_en": "VNPU hardware video decoder (H.264/H.265 → raw)",
        "description_es": "Decodificador de vídeo por hardware VNPU (H.264/H.265 → raw)",
        "properties": [
            {"name": "output-format", "type": "string", "description_ko": "출력 픽셀 포맷: NV12(기본)/RGB/BGR", "description_en": "Output pixel format: NV12 (default)/RGB/BGR", "description_es": "Formato de píxel de salida: NV12 (predet.)/RGB/BGR"},
            {"name": "output-width", "type": "int", "description_ko": "출력 폭 (0=입력과 동일)", "description_en": "Output width (0 = same as input)", "description_es": "Ancho de salida (0 = igual que entrada)"},
            {"name": "output-height", "type": "int", "description_ko": "출력 높이 (0=입력과 동일)", "description_en": "Output height (0 = same as input)", "description_es": "Alto de salida (0 = igual que entrada)"},
        ],
    },
    {
        "name": "DxVnpuEnc",
        "category": "output",
        "description_ko": "VNPU 하드웨어 비디오 인코더 (raw → H.264/H.265)",
        "description_en": "VNPU hardware video encoder (raw → H.264/H.265)",
        "description_es": "Codificador de vídeo por hardware VNPU (raw → H.264/H.265)",
        "properties": [
            {"name": "codec", "type": "string", "description_ko": "인코딩 코덱: h264(기본)/h265", "description_en": "Encoding codec: h264 (default)/h265", "description_es": "Códec de codificación: h264 (predet.)/h265"},
            {"name": "bitrate", "type": "int", "description_ko": "목표 비트레이트 (kbps, 기본 4096)", "description_en": "Target bitrate (kbps, default 4096)", "description_es": "Bitrate objetivo (kbps, predet. 4096)"},
        ],
    },
    {
        "name": "DxVnpuPipeline",
        "category": "inference",
        "description_ko": "VNPU 통합 추론 파이프라인 (VO 모드, H.264/H.265 입력)",
        "description_en": "VNPU integrated inference pipeline (VO mode, H.264/H.265 input)",
        "description_es": "Pipeline de inferencia integrado VNPU (modo VO, entrada H.264/H.265)",
        "properties": [
            {"name": "model-path", "type": "string", "description_ko": "추론용 .dxnn 모델 경로", "description_en": "Path to the .dxnn model for inference", "description_es": "Ruta del modelo .dxnn para inferencia"},
            {"name": "inference-id", "type": "int", "description_ko": "추론 식별자", "description_en": "Inference identifier", "description_es": "Identificador de inferencia"},
            {"name": "keep-ratio", "type": "bool", "description_ko": "리사이즈 시 종횡비 유지", "description_en": "Maintain aspect ratio on resize", "description_es": "Mantener relación de aspecto al redimensionar"},
            {"name": "use-ort", "type": "bool", "description_ko": "ORT 런타임 사용", "description_en": "Use ORT runtime", "description_es": "Usar runtime ORT"},
            {"name": "device-id", "type": "int", "description_ko": "VNPU 디바이스 ID (-1=자동)", "description_en": "VNPU device ID (-1 = auto)", "description_es": "ID de dispositivo VNPU (-1 = automático)"},
            {"name": "use-vnpu-hdmi", "type": "bool", "description_ko": "VNPU HDMI 출력(VO 모드) 활성화", "description_en": "Enable VNPU HDMI output (VO mode)", "description_es": "Habilitar salida HDMI VNPU (modo VO)"},
        ],
    },
    {
        "name": "DxVnpuOverlay",
        "category": "output",
        "description_ko": "VNPU 오버레이 렌더러 (HDMI 그리드 출력)",
        "description_en": "VNPU overlay renderer (HDMI grid output)",
        "description_es": "Renderizador de superposición VNPU (salida en cuadrícula HDMI)",
        "properties": [
            {"name": "model-path", "type": "string", "description_ko": "오버레이 설정용 .dxnn 모델 경로", "description_en": "Path to .dxnn model (for overlay config)", "description_es": "Ruta del modelo .dxnn (config. de superposición)"},
            {"name": "keep-ratio", "type": "bool", "description_ko": "오버레이 캔버스 종횡비 유지", "description_en": "Maintain aspect ratio for overlay canvas", "description_es": "Mantener relación de aspecto del lienzo"},
            {"name": "device-id", "type": "int", "description_ko": "VNPU 디바이스 ID (-1=자동)", "description_en": "VNPU device ID (-1 = auto)", "description_es": "ID de dispositivo VNPU (-1 = automático)"},
            {"name": "group-count", "type": "int", "description_ko": "HDMI 그리드 오버레이 그룹 수", "description_en": "Number of overlay groups for HDMI grid", "description_es": "Número de grupos de superposición para cuadrícula HDMI"},
        ],
    },
    # GStreamer 표준 (파이프라인 빌더용)
    {
        "name": "urisourcebin",
        "category": "source",
        "description_ko": "URI 기반 비디오 소스",
        "description_en": "URI-based video source", "description_es": "URI-based video source",
        "properties": [
            {"name": "uri", "type": "string", "description": "소스 URI", "description_ko": "소스 URI", "description_en": "Source URI", "description_es": "Source URI"},
        ],
    },
    {
        "name": "rtspsrc",
        "category": "source",
        "description_ko": "RTSP 네트워크 카메라 소스",
        "description_en": "RTSP network camera source", "description_es": "RTSP network camera source",
        "properties": [
            {"name": "location", "type": "string", "description": "RTSP URL", "description_ko": "RTSP URL", "description_en": "RTSP URL", "description_es": "RTSP URL"},
            {"name": "latency", "type": "int", "description": "지연 시간 (ms)", "description_ko": "지연 시간 (ms)", "description_en": "Latency (ms)", "description_es": "Latencia (ms)"},
        ],
    },
    {
        "name": "decodebin",
        "category": "utility",
        "description_ko": "자동 디코더 선택",
        "description_en": "Automatic decoder selection", "description_es": "Automatic decoder selection",
        "properties": [],
    },
    {
        "name": "videoconvert",
        "category": "utility",
        "description_ko": "비디오 포맷 변환",
        "description_en": "Video format conversion", "description_es": "Video format conversion",
        "properties": [],
    },
    {
        "name": "queue",
        "category": "utility",
        "description_ko": "데이터 큐 (스레드 경계)",
        "description_en": "Data queue (thread boundary)", "description_es": "Data queue (thread boundary)",
        "properties": [
            {"name": "max-size-buffers", "type": "int", "description": "최대 버퍼 수", "description_ko": "최대 버퍼 수", "description_en": "Max buffer count", "description_es": "Max buffer count"},
            {"name": "leaky", "type": "int", "description_ko": "누수 모드 (0=none, 1=upstream, 2=downstream)", "description_en": "Leaky mode (0=none, 1=upstream, 2=downstream)", "description_es": "Leaky mode (0=none, 1=upstream, 2=downstream)"},
        ],
    },
    {
        "name": "compositor",
        "category": "utility",
        "description_ko": "다중 비디오 합성",
        "description_en": "Multi-video compositing", "description_es": "Multi-video compositing",
        "properties": [],
    },
    {
        "name": "fpsdisplaysink",
        "category": "output",
        "description_ko": "FPS 표시 디스플레이 싱크",
        "description_en": "FPS display sink", "description_es": "FPS display sink",
        "properties": [
            {"name": "sync", "type": "bool", "description": "동기화 여부", "description_ko": "동기화 여부", "description_en": "Synchronization", "description_es": "Synchronization"},
            {"name": "video-sink", "type": "string", "description_ko": "내부 비디오 싱크 엘리먼트", "description_en": "Internal video sink element", "description_es": "Internal video sink element"},
        ],
    },
    {
        "name": "ximagesink",
        "category": "output",
        "description_ko": "X11 비디오 디스플레이 싱크",
        "description_en": "X11 video display sink", "description_es": "X11 video display sink",
        "properties": [
            {"name": "sync", "type": "bool", "description_ko": "클럭 동기화 여부", "description_en": "Clock synchronization", "description_es": "Clock synchronization"},
            {"name": "force-aspect-ratio", "type": "bool", "description_ko": "종횡비 유지", "description_en": "Preserve aspect ratio", "description_es": "Preserve aspect ratio"},
        ],
    },
    {
        "name": "tee",
        "category": "utility",
        "description_ko": "스트림을 여러 브랜치로 분기",
        "description_en": "Split stream into multiple branches", "description_es": "Split stream into multiple branches",
        "properties": [],
    },
    {
        "name": "webrtcbin",
        "category": "output",
        "description_ko": "WebRTC 스트리밍 출력",
        "description_en": "WebRTC streaming output", "description_es": "WebRTC streaming output",
        "properties": [
            {"name": "name", "type": "string", "description_ko": "엘리먼트 이름", "description_en": "Element name", "description_es": "Element name"},
            {"name": "bundle-policy", "type": "string", "description_ko": "번들 정책", "description_en": "Bundle policy", "description_es": "Bundle policy"},
            {"name": "stun-server", "type": "string", "description_ko": "STUN 서버 URL", "description_en": "STUN server URL", "description_es": "STUN server URL"},
            {"name": "turn-server", "type": "string", "description_ko": "TURN 서버 URL", "description_en": "TURN server URL", "description_es": "TURN server URL"},
        ],
    },
    {
        "name": "vp8enc",
        "category": "utility",
        "description_ko": "VP8 비디오 인코더",
        "description_en": "VP8 video encoder", "description_es": "VP8 video encoder",
        "properties": [
            {"name": "deadline", "type": "int", "description_ko": "인코딩 데드라인 (ms, 1=실시간)", "description_en": "Encoding deadline (ms, 1=realtime)", "description_es": "Encoding deadline (ms, 1=realtime)"},
            {"name": "target-bitrate", "type": "int", "description_ko": "목표 비트레이트 (bps)", "description_en": "Target bitrate (bps)", "description_es": "Target bitrate (bps)"},
        ],
    },
    {
        "name": "x264enc",
        "category": "utility",
        "description_ko": "H.264 비디오 인코더",
        "description_en": "H.264 video encoder", "description_es": "H.264 video encoder",
        "properties": [
            {"name": "tune", "type": "string", "description_ko": "인코딩 튜닝 (예: zerolatency)", "description_en": "Encoding tune (for example, zerolatency)", "description_es": "Encoding tune (for example, zerolatency)"},
            {"name": "speed-preset", "type": "string", "description_ko": "인코딩 속도 프리셋", "description_en": "Encoding speed preset", "description_es": "Encoding speed preset"},
            {"name": "bitrate", "type": "int", "description_ko": "목표 비트레이트 (kbps)", "description_en": "Target bitrate (kbps)", "description_es": "Target bitrate (kbps)"},
            {"name": "key-int-max", "type": "int", "description_ko": "키프레임 최대 간격", "description_en": "Maximum keyframe interval", "description_es": "Maximum keyframe interval"},
        ],
    },
]

_ELEMENT_DETAILS = {
    "DxPreprocess": {
        "long_description_ko": "입력 프레임을 NPU 모델 입력 형식에 맞게 리사이즈·색상 변환·패딩하고, 필요하면 ROI나 2차 추론 대상만 추출해 다음 DxInfer로 전달합니다.",
        "long_description_en": "Resizes, converts color, pads, and optionally crops ROI regions so incoming frames match the tensor layout expected by the next DxInfer element.",
        "key_features": [
            {"ko": "모델 입력 크기와 종횡비 유지 옵션을 한 곳에서 제어", "en": "Controls model input size and aspect-ratio preservation in one stage", "es": "Controla el tamaño de entrada del modelo y la preservación de la relación de aspecto en una etapa", "ja": "モデル入力サイズとアスペクト比維持を一段階で制御", "zh-CN": "在单个阶段中控制模型输入尺寸和宽高比保持", "zh-TW": "在單一階段中控制模型輸入尺寸和寬高比維持"},
            {"ko": "PPU 설정 파일과 2차 추론 ROI 흐름 지원", "en": "Supports PPU config files and secondary-inference ROI flows", "es": "Admite archivos de configuración PPU y flujos de ROI de inferencia secundaria", "ja": "PPU設定ファイルと二次推論ROIフローをサポート", "zh-CN": "支持PPU配置文件和二次推理ROI流程", "zh-TW": "支援PPU設定檔和二次推論ROI流程"},
            {"ko": "preprocess-id로 DxInfer와 전처리 결과를 명확히 연결", "en": "Links preprocessing output to DxInfer through preprocess-id", "es": "Vincula la salida de preprocesamiento con DxInfer mediante preprocess-id", "ja": "preprocess-idを通じてDxInferと前処理出力を連携", "zh-CN": "通过preprocess-id将预处理输出与DxInfer连接", "zh-TW": "透過preprocess-id將預處理輸出與DxInfer連接"},
        ],
        "pipeline_hint_ko": "소스/디코더 뒤, DxInfer 앞에 배치합니다. preprocess-id는 연결되는 DxInfer의 preprocess-id와 맞추세요.",
        "pipeline_hint_en": "Place after source/decoder stages and before DxInfer. Match preprocess-id with the connected DxInfer preprocess-id.",
        "example_config": "DxPreprocess preprocess-id=0 resize-width=640 resize-height=640 keep-ratio=true ! DxInfer preprocess-id=0 model-path=/path/model.dxnn",
        "doc_path": "Elements/03_01_DxPreprocess.md",
        "related_elements": ["DxInfer", "DxScale", "DxConvert", "DxRoiExtract"],
    },
    "DxInfer": {
        "long_description_ko": "컴파일된 .dxnn 모델을 DEEPX NPU에서 실행하고 입력 텐서와 출력 텐서를 GStreamer 메타데이터 흐름에 연결하는 핵심 추론 엘리먼트입니다.",
        "long_description_en": "Runs a compiled .dxnn model on the DEEPX NPU and bridges input/output tensors into the GStreamer metadata flow for downstream processing.",
        "key_features": [
            {"ko": ".dxnn 모델 경로와 설정 파일 기반 추론 실행", "en": "Executes inference from a .dxnn model path and optional config file", "es": "Ejecuta inferencia desde una ruta de modelo .dxnn y archivo de configuración opcional", "ja": ".dxnnモデルパスとオプション設定ファイルから推論を実行", "zh-CN": "从.dxnn模型路径和可选配置文件执行推理", "zh-TW": "從.dxnn模型路徑和可選設定檔執行推論"},
            {"ko": "QoS 상황에서 프레임 처리 흐름을 안정적으로 유지", "en": "Maintains stable frame flow under QoS conditions", "es": "Mantiene un flujo de fotogramas estable en condiciones de QoS", "ja": "QoS条件下で安定したフレームフローを維持", "zh-CN": "在QoS条件下保持稳定的帧流", "zh-TW": "在QoS條件下維持穩定的幀流"},
            {"ko": "1차·2차 추론 파이프라인을 inference-id로 구분", "en": "Separates primary and secondary inference pipelines with inference-id", "es": "Separa pipelines de inferencia primaria y secundaria con inference-id", "ja": "inference-idで一次・二次推論パイプラインを分離", "zh-CN": "通过inference-id分离一次和二次推理管线", "zh-TW": "透過inference-id分離一次和二次推論管線"},
        ],
        "pipeline_hint_ko": "일반적으로 DxPreprocess 다음, DxPostprocess 앞에 배치합니다. preprocess-id와 inference-id를 후속 엘리먼트와 일치시키세요.",
        "pipeline_hint_en": "Typically place DxInfer after DxPreprocess and before DxPostprocess. Keep preprocess-id and inference-id aligned with downstream elements.",
        "example_config": "DxPreprocess preprocess-id=0 ! DxInfer preprocess-id=0 inference-id=0 model-path=/opt/models/yolo.dxnn ! DxPostprocess inference-id=0 library-file-path=/opt/lib/libpostprocess.so",
        "doc_path": "Elements/03_02_DxInfer.md",
        "related_elements": ["DxPreprocess", "DxPostprocess", "DxRoiExtract", "DxOsd"],
    },
    "DxPostprocess": {
        "long_description_ko": "NPU 출력 텐서를 모델별 후처리 함수로 파싱해 객체, 마스크, 포즈 같은 구조화된 메타데이터로 변환합니다.",
        "long_description_en": "Parses NPU output tensors through model-specific postprocess functions and converts them into structured metadata such as objects, masks, or poses.",
        "key_features": [
            {"ko": "커스텀 .so 라이브러리와 function-name으로 모델별 파서 선택", "en": "Selects model-specific parsers through a custom .so library and function-name", "es": "Selecciona analizadores específicos del modelo a través de una biblioteca .so personalizada y function-name", "ja": "カスタム.soライブラリとfunction-nameでモデル固有パーサーを選択", "zh-CN": "通过自定义.so库和function-name选择模型特定解析器", "zh-TW": "透過自訂.so函式庫和function-name選擇模型特定解析器"},
            {"ko": "DxOsd, DxTracker, DxMsgConv가 사용하는 메타데이터 생성", "en": "Produces metadata consumed by DxOsd, DxTracker, and DxMsgConv", "es": "Produce metadatos consumidos por DxOsd, DxTracker y DxMsgConv", "ja": "DxOsd、DxTracker、DxMsgConvが使用するメタデータを生成", "zh-CN": "生成DxOsd、DxTracker和DxMsgConv使用的元数据", "zh-TW": "產生DxOsd、DxTracker和DxMsgConv使用的中繼資料"},
            {"ko": "inference-id로 대응되는 DxInfer 결과를 추적", "en": "Tracks the corresponding DxInfer output with inference-id", "es": "Rastrea la salida correspondiente de DxInfer con inference-id", "ja": "inference-idで対応するDxInfer出力を追跡", "zh-CN": "通过inference-id跟踪对应的DxInfer输出", "zh-TW": "透過inference-id追蹤對應的DxInfer輸出"},
        ],
        "pipeline_hint_ko": "DxInfer 뒤에 배치하고, 시각화는 DxOsd, 추적은 DxTracker, 메시징은 DxMsgConv로 이어가세요.",
        "pipeline_hint_en": "Place after DxInfer, then continue to DxOsd for visualization, DxTracker for tracking, or DxMsgConv for messaging.",
        "example_config": "DxInfer inference-id=0 model-path=/opt/models/yolo.dxnn ! DxPostprocess inference-id=0 library-file-path=/opt/lib/libpostprocess.so function-name=PostProcess",
        "doc_path": "Elements/03_03_DxPostprocess.md",
        "related_elements": ["DxInfer", "DxTracker", "DxOsd", "DxMsgConv"],
    },
    "DxTracker": {
        "long_description_ko": "후처리된 객체 메타데이터에 추적 ID를 부여하고 프레임 간 객체 이동을 유지해 분석과 메시징 단계에서 일관된 객체 흐름을 제공합니다.",
        "long_description_en": "Assigns tracking IDs to postprocessed object metadata and keeps object continuity across frames for analytics and messaging stages.",
        "key_features": [
            {"ko": "OC_SORT 기반 다중 객체 추적", "en": "OC_SORT-based multi-object tracking", "es": "Seguimiento de múltiples objetos basado en OC_SORT", "ja": "OC_SORTベースの多重オブジェクト追跡", "zh-CN": "基于OC_SORT的多目标跟踪", "zh-TW": "基於OC_SORT的多目標追蹤"},
            {"ko": "트래커 설정 파일로 매칭·수명 정책 조정", "en": "Tunes matching and lifetime policy through a tracker config file", "es": "Ajusta la política de coincidencia y vida útil a través de un archivo de configuración de rastreador", "ja": "トラッカー設定ファイルでマッチングとライフタイムポリシーを調整", "zh-CN": "通过跟踪器配置文件调整匹配和生命周期策略", "zh-TW": "透過追蹤器設定檔調整匹配和生命週期策略"},
        ],
        "pipeline_hint_ko": "DxPostprocess 뒤, DxOsd 또는 DxMsgConv 앞에 배치하면 추적 ID가 시각화와 메시지에 반영됩니다.",
        "pipeline_hint_en": "Place after DxPostprocess and before DxOsd or DxMsgConv so track IDs appear in overlays and messages.",
        "doc_path": "Elements/03_04_DxTracker.md",
        "related_elements": ["DxPostprocess", "DxOsd", "DxMsgConv"],
    },
    "DxOsd": {
        "long_description_ko": "감지 박스, 클래스 라벨, 마스크, 포즈 키포인트 등 메타데이터를 비디오 프레임 위에 그려 실시간 미리보기와 스트리밍 출력에 사용합니다.",
        "long_description_en": "Draws metadata such as detection boxes, class labels, masks, and pose keypoints onto video frames for live preview and streaming output.",
        "key_features": [
            {"ko": "후처리·추적 결과를 프레임 오버레이로 렌더링", "en": "Renders postprocess and tracking results as frame overlays", "es": "Renderiza resultados de posprocesamiento y seguimiento como superposiciones de fotogramas", "ja": "後処理・追跡結果をフレームオーバーレイとしてレンダリング", "zh-CN": "将后处理和跟踪结果渲染为帧叠加层", "zh-TW": "將後處理和追蹤結果渲染為幀疊加層"},
            {"ko": "디스플레이 싱크나 WebRTC 출력 전 단계에 적합", "en": "Fits before display sinks or WebRTC output stages", "es": "Se ubica antes de los sinks de visualización o etapas de salida WebRTC", "ja": "ディスプレイシンクまたはWebRTC出力段の前に配置", "zh-CN": "适合放在显示接收器或WebRTC输出阶段之前", "zh-TW": "適合放在顯示接收器或WebRTC輸出階段之前"},
        ],
        "pipeline_hint_ko": "DxPostprocess 또는 DxTracker 뒤에 두고, 출력 전 videoconvert가 필요할 수 있습니다.",
        "pipeline_hint_en": "Use after DxPostprocess or DxTracker; videoconvert may be needed before display or encoder outputs.",
        "doc_path": "Elements/03_05_DxOsd.md",
        "related_elements": ["DxPostprocess", "DxTracker", "videoconvert", "fpsdisplaysink", "webrtcbin"],
    },
    "DxGather": {
        "long_description_ko": "분기된 병렬 파이프라인의 결과를 다시 모아 동기화된 후속 처리로 전달하는 유틸리티 엘리먼트입니다.",
        "long_description_en": "Collects results from branched parallel pipelines and forwards them into synchronized downstream processing.",
        "key_features": [
            {"ko": "분기 처리 결과 병합", "en": "Merges results from branched processing paths", "es": "Combina resultados de rutas de procesamiento ramificadas", "ja": "分岐した処理パスの結果をマージ", "zh-CN": "合并分支处理路径的结果", "zh-TW": "合併分支處理路徑的結果"},
            {"ko": "tee 또는 selector 기반 파이프라인의 합류 지점 구성", "en": "Forms a join point for tee or selector based pipelines", "es": "Forma un punto de unión para pipelines basados en tee o selector", "ja": "teeまたはselectorベースのパイプラインの合流点を構成", "zh-CN": "构成tee或selector管线的汇合点", "zh-TW": "構成tee或selector管線的匯合點"},
        ],
        "pipeline_hint_ko": "tee나 selector로 나눈 브랜치를 다시 합칠 때 사용하세요.",
        "pipeline_hint_en": "Use when branches split by tee or selectors need to converge again.",
        "doc_path": "Elements/03_06_DxGather.md",
        "related_elements": ["tee", "DxInputSelector", "DxOutputSelector"],
    },
    "DxInputSelector": {
        "long_description_ko": "여러 입력 후보 중 활성 입력을 선택해 파이프라인의 입력 전환이나 조건부 경로 구성을 돕습니다.",
        "long_description_en": "Selects one active input among multiple candidates to support input switching and conditional pipeline paths.",
        "key_features": [{"ko": "다중 입력 경로 선택", "en": "Selects among multiple input paths", "es": "Selecciona entre múltiples rutas de entrada", "ja": "複数の入力パスから選択", "zh-CN": "在多个输入路径中进行选择", "zh-TW": "在多個輸入路徑中進行選擇"}],
        "pipeline_hint_ko": "여러 소스나 분기 입력 중 하나만 다음 단계로 전달해야 할 때 사용합니다.",
        "pipeline_hint_en": "Use when only one source or branch input should continue downstream.",
        "doc_path": "Elements/03_07_DxInputSelector.md",
        "related_elements": ["DxOutputSelector", "DxGather"],
    },
    "DxOutputSelector": {
        "long_description_ko": "하나의 입력을 여러 출력 후보 중 선택된 경로로 전달해 동적 출력 전환을 구성합니다.",
        "long_description_en": "Routes one input to a selected output path for dynamic output switching.",
        "key_features": [{"ko": "다중 출력 경로 선택", "en": "Selects among multiple output paths", "es": "Selecciona entre múltiples rutas de salida", "ja": "複数の出力パスから選択", "zh-CN": "在多个输出路径中进行选择", "zh-TW": "在多個輸出路徑中進行選擇"}],
        "pipeline_hint_ko": "동일 입력을 상황에 따라 다른 처리 경로로 보낼 때 사용합니다.",
        "pipeline_hint_en": "Use when the same input should be routed to different downstream paths depending on runtime state.",
        "doc_path": "Elements/03_08_DxOutputSelector.md",
        "related_elements": ["DxInputSelector", "DxGather"],
    },
    "DxRate": {
        "long_description_ko": "파이프라인 처리량을 목표 FPS로 제한해 NPU 부하, 메시지 빈도, 출력 대역폭을 제어합니다.",
        "long_description_en": "Limits pipeline throughput to a target FPS to control NPU load, message rate, or output bandwidth.",
        "key_features": [{"ko": "프레임 처리 속도 제한", "en": "Caps frame processing rate", "es": "Limita la tasa de procesamiento de fotogramas", "ja": "フレーム処理レートを制限", "zh-CN": "限制帧处理速率", "zh-TW": "限制幀處理速率"}],
        "pipeline_hint_ko": "소스 직후나 무거운 추론 단계 앞에 배치해 처리량을 안정화하세요.",
        "pipeline_hint_en": "Place near the source or before heavy inference stages to stabilize throughput.",
        "doc_path": "Elements/03_09_DxRate.md",
        "related_elements": ["queue", "DxInfer"],
    },
    "DxMsgConv": {
        "long_description_ko": "추론·후처리·추적 메타데이터를 외부 시스템이 소비할 수 있는 JSON 메시지 형식으로 변환합니다.",
        "long_description_en": "Converts inference, postprocess, and tracking metadata into JSON messages consumable by external systems.",
        "key_features": [
            {"ko": "객체 메타데이터를 JSON 페이로드로 직렬화", "en": "Serializes object metadata into JSON payloads", "es": "Serializa metadatos de objetos en payloads JSON", "ja": "オブジェクトメタデータをJSONペイロードにシリアライズ", "zh-CN": "将对象元数据序列化为JSON载荷", "zh-TW": "將物件中繼資料序列化為JSON載荷"},
            {"ko": "브로커 전송 전 메시지 스키마를 설정 파일로 조정", "en": "Adjusts message schema by config file before broker publishing", "es": "Ajusta el esquema del mensaje mediante archivo de configuración antes de la publicación al broker", "ja": "ブローカー送信前に設定ファイルでメッセージスキーマを調整", "zh-CN": "在发布到代理之前通过配置文件调整消息模式", "zh-TW": "在發布到代理之前透過設定檔調整訊息模式"},
        ],
        "pipeline_hint_ko": "DxPostprocess 또는 DxTracker 뒤, DxMsgBroker 앞에 배치합니다.",
        "pipeline_hint_en": "Place after DxPostprocess or DxTracker and before DxMsgBroker.",
        "example_config": "DxPostprocess ! DxMsgConv config-file-path=/opt/config/msgconv.json ! DxMsgBroker broker-name=mqtt conn-info=localhost:1883 topic=dx/stream",
        "doc_path": "Elements/03_10_DxMsgConv.md",
        "related_elements": ["DxPostprocess", "DxTracker", "DxMsgBroker"],
    },
    "DxMsgBroker": {
        "long_description_ko": "변환된 JSON 메시지를 MQTT 또는 Kafka 같은 외부 메시지 브로커로 전송해 관제·저장·알림 시스템과 연동합니다.",
        "long_description_en": "Publishes converted JSON messages to external brokers such as MQTT or Kafka for monitoring, storage, or alerting systems.",
        "key_features": [
            {"ko": "MQTT/Kafka 브로커 출력 지원", "en": "Supports MQTT/Kafka broker output", "es": "Admite salida de broker MQTT/Kafka", "ja": "MQTT/Kafkaブローカー出力をサポート", "zh-CN": "支持MQTT/Kafka代理输出", "zh-TW": "支援MQTT/Kafka代理輸出"},
            {"ko": "토픽과 연결 정보를 속성으로 지정", "en": "Configures topics and connection information through properties", "es": "Configura temas e información de conexión a través de propiedades", "ja": "プロパティでトピックと接続情報を設定", "zh-CN": "通过属性配置主题和连接信息", "zh-TW": "透過屬性配置主題和連接資訊"},
        ],
        "pipeline_hint_ko": "메시징 브랜치의 마지막 엘리먼트로 사용합니다. 일반적으로 출력 연결은 만들지 않습니다.",
        "pipeline_hint_en": "Use as the final element in a messaging branch. It typically has no outgoing connection.",
        "example_config": "DxMsgConv ! DxMsgBroker broker-name=mqtt conn-info=localhost:1883 topic=dx/stream",
        "doc_path": "Elements/03_11_DxMsgBroker.md",
        "related_elements": ["DxMsgConv"],
    },
    "DxScale": {
        "long_description_ko": "프레임을 지정된 출력 해상도로 스케일링해 후속 전처리, 합성, 출력 단계의 크기 요구사항을 맞춥니다.",
        "long_description_en": "Scales frames to a specified output resolution so downstream preprocessing, compositing, or output stages receive the expected size.",
        "key_features": [{"ko": "하드웨어 가속 기반 프레임 크기 조정", "en": "Hardware-accelerated frame resizing", "es": "Redimensionamiento de fotogramas acelerado por hardware", "ja": "ハードウェアアクセラレーションによるフレームリサイズ", "zh-CN": "硬件加速帧缩放", "zh-TW": "硬體加速幀縮放"}],
        "pipeline_hint_ko": "DxPreprocess 전후 또는 출력 합성 전 해상도 정규화 단계로 사용하세요.",
        "pipeline_hint_en": "Use around DxPreprocess or before output composition to normalize resolution.",
        "doc_path": "Elements/03_12_DxScale.md",
        "related_elements": ["DxPreprocess", "DxConvert", "compositor"],
    },
    "DxConvert": {
        "long_description_ko": "비디오 색공간이나 픽셀 포맷을 후속 DX Stream 엘리먼트가 기대하는 형식으로 변환합니다.",
        "long_description_en": "Converts video color space or pixel format into the format expected by downstream DX Stream elements.",
        "key_features": [{"ko": "색공간·픽셀 포맷 변환", "en": "Color-space and pixel-format conversion", "es": "Conversión de espacio de color y formato de píxeles", "ja": "色空間・ピクセルフォーマット変換", "zh-CN": "色彩空间和像素格式转换", "zh-TW": "色彩空間和像素格式轉換"}],
        "pipeline_hint_ko": "디코더, 스케일러, OSD, 인코더 사이에서 포맷이 맞지 않을 때 배치하세요.",
        "pipeline_hint_en": "Insert between decoders, scalers, OSD, and encoders when formats do not match.",
        "doc_path": "Elements/03_13_DxConvert.md",
        "related_elements": ["DxScale", "DxPreprocess", "videoconvert"],
    },
}


def _with_detail(element: dict) -> dict:
    detailed = dict(element)
    detailed.update(_ELEMENT_DETAILS.get(element["name"], {}))
    return detailed

CONNECTION_RULES = {
    "source":        {"has_input": False, "has_output": True,  "allowed_next": ["utility", "preprocess"]},
    "preprocess":    {"has_input": True,  "has_output": True,  "allowed_next": ["inference", "preprocess", "utility"]},
    "inference":     {"has_input": True,  "has_output": True,  "allowed_next": ["postprocess", "visualization", "tracking", "utility"]},
    "postprocess":   {"has_input": True,  "has_output": True,  "allowed_next": ["visualization", "tracking", "messaging", "utility", "inference"]},
    "tracking":      {"has_input": True,  "has_output": True,  "allowed_next": ["visualization", "messaging", "utility"]},
    "visualization": {"has_input": True,  "has_output": True,  "allowed_next": ["utility", "output", "messaging"]},
    "messaging":     {"has_input": True,  "has_output": True,  "allowed_next": ["messaging", "utility", "output"]},
    "utility":       {"has_input": True,  "has_output": True,  "allowed_next": None},
    "output":        {"has_input": True,  "has_output": False, "allowed_next": []},
}

ELEMENT_OVERRIDES = {
    "DxMsgBroker":  {"has_output": False, "recommended_prev_elements": ["DxMsgConv"]},
    "tee":          {"min_outputs": 2, "warn_msg_en": "Only one branch"},
    "DxGather":     {"min_inputs": 2,  "warn_msg_en": "Only one merge input"},
    "compositor":   {"min_inputs": 2,  "warn_msg_en": "Only one merge input"},
}

SEMANTIC_WARNINGS = [
    {
        "pattern": "inference_to_inference",
        "msg_en": "Consider adding postprocess between inference nodes",
    },
    {
        "pattern": "detile_without_tile",
        "msg_en": "Use with DxTile",
    },
]

AUTO_CONVERTER_RULES = [
    {
        "from_categories": ["visualization", "postprocess", "tracking"],
        "to_elements": ["vp8enc", "x264enc", "webrtcbin", "fpsdisplaysink", "ximagesink"],
        "insert": "videoconvert",
        "msg_en": "Auto-insert videoconvert?",
    },
]


def get_elements() -> list[dict]:
    """전체 엘리먼트 레퍼런스 반환"""
    return [_with_detail(e) for e in _ELEMENTS]


def get_element_by_name(name: str) -> dict | None:
    """이름으로 엘리먼트 조회"""
    for e in _ELEMENTS:
        if e["name"] == name:
            return _with_detail(e)
    return None


def get_elements_by_category() -> dict[str, list[dict]]:
    """카테고리별 엘리먼트 그룹핑"""
    cats: dict[str, list[dict]] = {}
    for e in get_elements():
        cats.setdefault(e["category"], []).append(e)
    return cats


def validate_connection(from_elem: str, to_elem: str) -> dict:
    """엘리먼트 연결 호환성 검증.

    Returns:
        {"result": "allow"} |
        {"result": "block", "reason_en": "...", "reason_ko": "..."} |
        {"result": "warn", "reason_en": "...", "reason_ko": "..."} |
        {"result": "auto_convert", "insert": "...", "msg_en": "...", "msg_ko": "..."}
    """
    from_el = get_element_by_name(from_elem)
    to_el = get_element_by_name(to_elem)

    # unknown elements → allow (차단하지 않음)
    if not from_el or not to_el:
        return {"result": "allow"}

    from_cat = from_el["category"]
    to_cat = to_el["category"]
    from_rule = CONNECTION_RULES.get(from_cat, {})
    to_rule = CONNECTION_RULES.get(to_cat, {})
    from_override = ELEMENT_OVERRIDES.get(from_elem, {})
    to_override = ELEMENT_OVERRIDES.get(to_elem, {})

    # Step 1: 구조 검증 — has_output / has_input
    has_output = from_override.get("has_output", from_rule.get("has_output", True))
    if not has_output:
        return {"result": "block", "reason_en": "Output has no outgoing connections",
                "reason_ko": "출력 엘리먼트는 나가는 연결이 없습니다"}

    has_input = to_override.get("has_input", to_rule.get("has_input", True))
    if not has_input:
        return {"result": "block", "reason_en": "Source cannot receive input",
                "reason_ko": "소스는 입력을 받을 수 없습니다"}

    # Step 2: 카테고리 호환성
    allowed_next = from_rule.get("allowed_next")
    if allowed_next is not None:
        if to_cat not in allowed_next and to_cat != "utility":
            # 시맨틱 경고가 블록보다 우선하는 경우 체크
            for sw in SEMANTIC_WARNINGS:
                if sw["pattern"] == "inference_to_inference" and from_cat == "inference" and to_cat == "inference":
                    return {"result": "warn", "reason_en": sw["msg_en"],
                            "reason_ko": "추론 노드 사이에 후처리 추가를 권장합니다"}
            return {"result": "block", "reason_en": "Category connection not allowed",
                    "reason_ko": "카테고리 연결이 허용되지 않습니다"}

    # Step 3: 자동 컨버터
    for rule in AUTO_CONVERTER_RULES:
        if from_cat in rule["from_categories"] and to_elem in rule["to_elements"]:
            return {
                "result": "auto_convert",
                "insert": rule["insert"],
                "msg_en": rule["msg_en"],
                "msg_ko": "자동으로 " + rule["insert"] + "를 삽입할까요?",
            }

    # Step 4: 시맨틱 경고
    for sw in SEMANTIC_WARNINGS:
        if sw["pattern"] == "inference_to_inference" and from_cat == "inference" and to_cat == "inference":
            return {"result": "warn", "reason_en": sw["msg_en"],
                    "reason_ko": "추론 노드 사이에 후처리 추가를 권장합니다"}

    rec = to_override.get("recommended_prev_elements")
    if rec and from_elem not in rec:
        return {"result": "warn",
                "reason_en": "Recommended: connect from " + ", ".join(rec),
                "reason_ko": "권장: " + ", ".join(rec) + "에서 연결"}

    return {"result": "allow"}


def get_connection_rules() -> dict:
    """프론트엔드에 전달할 연결 규칙 번들"""
    return {
        "connection_rules": CONNECTION_RULES,
        "element_overrides": ELEMENT_OVERRIDES,
        "semantic_warnings": SEMANTIC_WARNINGS,
        "auto_converter_rules": AUTO_CONVERTER_RULES,
    }
