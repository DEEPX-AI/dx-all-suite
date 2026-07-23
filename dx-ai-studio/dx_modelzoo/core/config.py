"""DX Model Zoo — 경로, 상수, 카테고리 정의."""
import importlib
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent          # dx_modelzoo/
import shared.paths as _shared_paths
# Reload so that a reload of THIS module (as done by env-override tests, e.g.
# monkeypatch.setenv(...); importlib.reload(config)) re-reads the current
# environment via shared.paths' own env-honoring computation, rather than
# reusing a stale value cached from shared.paths' first import.
importlib.reload(_shared_paths)
from shared.paths import SUITE_ROOT, DX_APP_ROOT

CONFIG_FILE = DX_APP_ROOT / "config" / "test_models.conf"
ASSETS_DIR = DX_APP_ROOT / "assets"
MODELS_DIR = ASSETS_DIR / "models"
CPP_DIR = DX_APP_ROOT / "src" / "cpp_example"
PY_DIR = DX_APP_ROOT / "src" / "python_example"
BUILD_DIR = DX_APP_ROOT / "build_x86_64" / "src" / "cpp_example"
SAMPLE_DIR = DX_APP_ROOT / "sample"
SAMPLE_IMG_DIR = SAMPLE_DIR / "img"

STATIC_DIR = SCRIPT_DIR / "static"
TEMPLATES_DIR = SCRIPT_DIR / "templates"
DATA_DIR = SCRIPT_DIR / "data"
CATALOG_FILE = DATA_DIR / "model_catalog.json"

DEFAULT_PORT = 8094
# Inference is proxied to the dx_app server. The launcher may reassign dx_app to a
# free port when 8080 is held by a foreign process, so honor DX_APP_PORT from the
# environment (set by the launcher) instead of hardcoding 8080.
try:
    DX_APP_PORT = int(os.environ.get("DX_APP_PORT", "8080"))
except (TypeError, ValueError):
    DX_APP_PORT = 8080
SERVER_NAME = "DX Model Zoo"

CATEGORIES = {
    "object_detection":     {"label_en": "Object Detection",      "label_ko": "객체 탐지",           "label_ja": "物体検出",              "label_es": "Detección de objetos",         "label_zh-CN": "目标检测",   "label_zh-TW": "物件偵測",   "icon": "🎯"},
    "classification":       {"label_en": "Classification",        "label_ko": "분류",               "label_ja": "分類",                  "label_es": "Clasificación",                "label_zh-CN": "分类",       "label_zh-TW": "分類",       "icon": "🏷️"},
    "ppu":                  {"label_en": "PPU",                   "label_ko": "PPU",                "label_ja": "PPU",                   "label_es": "PPU",                          "label_zh-CN": "PPU",        "label_zh-TW": "PPU",        "icon": "⚙️"},
    "instance_segmentation":{"label_en": "Instance Segmentation", "label_ko": "인스턴스 분할",       "label_ja": "インスタンスセグメンテーション", "label_es": "Segmentación de instancias",   "label_zh-CN": "实例分割",   "label_zh-TW": "實例分割",   "icon": "🎨"},
    "face_detection":       {"label_en": "Face Detection",        "label_ko": "얼굴 탐지",          "label_ja": "顔検出",                "label_es": "Detección de rostros",         "label_zh-CN": "人脸检测",   "label_zh-TW": "人臉偵測",   "icon": "👤"},
    "pose_estimation":      {"label_en": "Pose Estimation",       "label_ko": "자세 추정",          "label_ja": "姿勢推定",              "label_es": "Estimación de pose",           "label_zh-CN": "姿态估计",   "label_zh-TW": "姿態估計",   "icon": "🏃"},
    "semantic_segmentation":{"label_en": "Semantic Segmentation", "label_ko": "시맨틱 분할",        "label_ja": "セマンティックセグメンテーション","label_es": "Segmentación semántica",       "label_zh-CN": "语义分割",   "label_zh-TW": "語意分割",   "icon": "🖌️"},
    "image_denoising":      {"label_en": "Image Denoising",       "label_ko": "이미지 노이즈 제거", "label_ja": "画像ノイズ除去",         "label_es": "Eliminación de ruido de imagen","label_zh-CN": "图像去噪",   "label_zh-TW": "影像去噪",   "icon": "✨"},
    "obb_detection":        {"label_en": "OBB Detection",         "label_ko": "OBB 탐지",           "label_ja": "OBB検出",               "label_es": "Detección OBB",                "label_zh-CN": "OBB检测",    "label_zh-TW": "OBB偵測",    "icon": "📐"},
    "reid":                 {"label_en": "Re-Identification",     "label_ko": "재식별",             "label_ja": "再識別",                "label_es": "Reidentificación",             "label_zh-CN": "重识别",     "label_zh-TW": "重新識別",   "icon": "🔎"},
    "embedding":            {"label_en": "Embedding",             "label_ko": "임베딩",             "label_ja": "埋め込み",              "label_es": "Embedding",                    "label_zh-CN": "嵌入",       "label_zh-TW": "嵌入",       "icon": "🔗"},
    "attribute_recognition":{"label_en": "Attribute Recognition",  "label_ko": "속성 인식",          "label_ja": "属性認識",              "label_es": "Reconocimiento de atributos",  "label_zh-CN": "属性识别",   "label_zh-TW": "屬性辨識",   "icon": "🏷️"},
    "super_resolution":     {"label_en": "Super Resolution",      "label_ko": "초해상도",           "label_ja": "超解像",                "label_es": "Superresolución",              "label_zh-CN": "超分辨率",   "label_zh-TW": "超解析度",   "icon": "🔍"},
    "face_alignment":       {"label_en": "Face Alignment",        "label_ko": "얼굴 정렬",          "label_ja": "顔アライメント",         "label_es": "Alineación facial",            "label_zh-CN": "人脸对齐",   "label_zh-TW": "人臉對齊",   "icon": "😀"},
    "depth_estimation":     {"label_en": "Depth Estimation",      "label_ko": "깊이 추정",          "label_ja": "深度推定",              "label_es": "Estimación de profundidad",    "label_zh-CN": "深度估计",   "label_zh-TW": "深度估計",   "icon": "📏"},
    "image_enhancement":    {"label_en": "Image Enhancement",     "label_ko": "이미지 향상",        "label_ja": "画像強調",              "label_es": "Mejora de imagen",             "label_zh-CN": "图像增强",   "label_zh-TW": "影像增強",   "icon": "🌟"},
    "hand_landmark":        {"label_en": "Hand Landmark",         "label_ko": "손 랜드마크",        "label_ja": "手のランドマーク",       "label_es": "Puntos de referencia de la mano","label_zh-CN": "手部关键点", "label_zh-TW": "手部關鍵點", "icon": "✋"},
    "hand_detection":       {"label_en": "Hand Detection",        "label_ko": "손 탐지",            "label_ja": "手検出",                "label_es": "Detección de manos",           "label_zh-CN": "手部检测",   "label_zh-TW": "手部偵測",   "icon": "🤚"},
    "keypoint_detection":   {"label_en": "Keypoint Detection",    "label_ko": "키포인트 탐지",      "label_ja": "キーポイント検出",       "label_es": "Detección de puntos clave",    "label_zh-CN": "关键点检测", "label_zh-TW": "關鍵點偵測", "icon": "📍"},
    "object_pose_estimation":{"label_en": "Object Pose Estimation","label_ko": "객체 자세 추정",     "label_ja": "物体姿勢推定",          "label_es": "Estimación de pose de objetos","label_zh-CN": "物体姿态估计","label_zh-TW": "物件姿態估計","icon": "📦"},
    "panoptic_driving_perception":{"label_en": "Panoptic Driving Perception","label_ko": "파놉틱 주행 인식","label_ja": "パノプティック走行認識","label_es": "Percepción panóptica de conducción","label_zh-CN": "全景驾驶感知","label_zh-TW": "全景駕駛感知","icon": "🚗"},
    "3d_object_detection":  {"label_en": "3D Object Detection",   "label_ko": "3D 객체 탐지",       "label_ja": "3D物体検出",            "label_es": "Detección de objetos 3D",      "label_zh-CN": "3D目标检测", "label_zh-TW": "3D物件偵測", "icon": "🧊"},
}

# 태스크별 Example 이미지 표시 타입
EXAMPLE_TYPES = {
    "object_detection": "single", "face_detection": "single",
    "pose_estimation": "single", "obb_detection": "single",
    "ppu": "single", "face_alignment": "single", "hand_landmark": "single",
    "attribute_recognition": "single", "embedding": "single",
    "image_denoising": "before_after", "super_resolution": "before_after",
    "image_enhancement": "before_after",
    "semantic_segmentation": "overlay", "instance_segmentation": "overlay",
    "depth_estimation": "overlay",
    "classification": "classified", "reid": "gallery",
    "hand_detection": "single", "keypoint_detection": "single",
    "object_pose_estimation": "single", "3d_object_detection": "single",
    "panoptic_driving_perception": "overlay",
}

# 태스크별 기본 샘플 이미지 (inference 용)
SAMPLE_IMAGES = {
    "object_detection": "sample/img/sample_street.jpg",
    "face_detection": "sample/img/sample_face.jpg",
    "pose_estimation": "sample/img/sample_people.jpg",
    "obb_detection": "sample/dota8_test/P0284.png",
    "classification": "sample/img/sample_dog.jpg",
    "instance_segmentation": "sample/img/sample_street.jpg",
    "semantic_segmentation": "sample/img/sample_parking.jpg",
    "depth_estimation": "sample/img/sample_horse.jpg",
    "image_denoising": "sample/img/sample_denoising.jpg",
    "super_resolution": "sample/img/sample_superresolution.png",
    "image_enhancement": "sample/img/sample_lowlight.jpg",
    "embedding": "sample/img/face_pair",
    "attribute_recognition": "sample/img/sample_person_a1.jpg",
    "reid": "sample/img/person_pair",
    "ppu": "sample/img/sample_street.jpg",
    "hand_landmark": "sample/img/sample_hand.jpg",
    "face_alignment": "sample/img/sample_face_a1.jpg",
    "hand_detection": "sample/img/sample_hand.jpg",
    "keypoint_detection": "sample/img/sample_street.jpg",
    "object_pose_estimation": "sample/dope/000000.png",
    "panoptic_driving_perception": "sample/img/sample_parking.jpg",
    "3d_object_detection": "sample/kitti/velodyne/000049.bin",
}

MODEL_IMAGE_OVERRIDE = {
    "scrfd500m_ppu": "sample/img/sample_face.jpg",
    "yolov5pose_ppu": "sample/img/sample_people.jpg",
    "handlandmarklite_1": "sample/img/sample_hand.jpg",
    "unet_mobilenet_v2": "sample/img/sample_dog.jpg",
}

for _name, _path in [("DX_APP_ROOT", DX_APP_ROOT)]:
    if not _path.is_dir():
        print(f"[WARNING] {_name} not found: {_path}")
