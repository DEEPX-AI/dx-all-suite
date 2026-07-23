"""DX-APP Configuration — shared constants, paths, and state."""
import os,sys,re,json,time,base64,signal,shutil,hashlib,platform,tempfile
import subprocess,threading,webbrowser,mimetypes,collections
from http.server import HTTPServer,SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse,parse_qs
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed

SCRIPT_DIR  = Path(__file__).resolve().parent.parent   # dx_app/ (one level above core/)
_NPU_STATS_BIN = SCRIPT_DIR / "dx_npu_stats"
from shared.paths import SUITE_ROOT as _SUITE_ROOT, DX_APP_ROOT, DX_COMPILER_ROOT, DX_RUNTIME_ROOT, outputs_dir
import shared.runtime as _runtime
CPP_DIR     = DX_APP_ROOT/"src"/"cpp_example"
PY_DIR      = DX_APP_ROOT/"src"/"python_example"
ASSETS_DIR  = DX_APP_ROOT/"assets"
SAMPLE_DIR  = DX_APP_ROOT/"sample"
CONFIG_FILE = DX_APP_ROOT/"config"/"test_models.conf"
# C++ binary location varies by how dx_app was provisioned: a source build lands
# under build_<arch>/src/cpp_example, while the dx-runtime tree ships prebuilt
# binaries in bin/. Pick the first that exists so both work; fall back to the
# source-build path (used in the "run build.sh" hint) when none are present yet.
_BUILD_DIR_CANDIDATES = [
    DX_APP_ROOT/"build_x86_64"/"src"/"cpp_example",
    DX_APP_ROOT/"build_aarch64"/"src"/"cpp_example",
    DX_APP_ROOT/"bin",
]
BUILD_DIR   = next((d for d in _BUILD_DIR_CANDIDATES if d.is_dir()), _BUILD_DIR_CANDIDATES[0])
SCRIPTS_DIR = DX_APP_ROOT/"scripts"
SERVER_NAME = "DX App"
STATIC_DIR  = SCRIPT_DIR/"static"
TEMPLATES_DIR = SCRIPT_DIR/"templates"
OUTPUTS_DIR = outputs_dir("dx_app")

SKIP_CAT={"common","build","sample","__pycache__","utils","factory"}
_HARDCODED_CATEGORIES=["object_detection","face_detection","pose_estimation","obb_detection",
 "classification","instance_segmentation","semantic_segmentation","depth_estimation",
 "image_denoising","super_resolution","image_enhancement","embedding","ppu",
 "face_alignment","hand_landmark","object_detection_x_semantic_segmentation"]
_VIRTUAL_CATEGORIES={"object_detection_x_semantic_segmentation"}

def _scan_categories():
    cats=set(_HARDCODED_CATEGORIES)
    for base in[CPP_DIR,PY_DIR]:
        if base.is_dir():
            for d in base.iterdir():
                if d.is_dir() and d.name not in SKIP_CAT:
                    cats.add(d.name)
    cats|=_VIRTUAL_CATEGORIES
    return sorted(cats)

CATEGORIES=_scan_categories()
print(f"[INFO] Dynamic scan: {len(CATEGORIES)} categories found: {', '.join(CATEGORIES)}")
_CAT_LABEL_OVERRIDES={"object_detection_x_semantic_segmentation":"ObjDet × SegSem",
 "ppu":"PPU","obb_detection":"OBB Detection"}
def _make_label(c):
    if c in _CAT_LABEL_OVERRIDES:return _CAT_LABEL_OVERRIDES[c]
    return c.replace("_"," ").title()
CAT_LABEL={c:_make_label(c) for c in CATEGORIES}
_DEFAULT_IMAGE="sample/img/sample_street.jpg"
_DEFAULT_VIDEO="assets/videos/dance-group.mov"
_CAT_IMAGE_OVERRIDES={"object_detection":"sample/img/sample_street.jpg",
 "face_detection":"sample/img/sample_face.jpg",
 "pose_estimation":"sample/img/sample_people.jpg","obb_detection":"sample/img/sample_airport_satellite_view.png",
 "classification":"sample/img/sample_dog.jpg","instance_segmentation":"sample/img/sample_street.jpg",
 "semantic_segmentation":"sample/img/sample_horse.jpg","depth_estimation":"sample/img/sample_kitchen.jpg",
 # OBB detection: aerial/satellite scene (rotated boxes) — matches run_demo.py canonical input.
 "image_denoising":"sample/img/sample_denoising.jpg","super_resolution":"sample/img/sample_superresolution.png",
 "image_enhancement":"sample/img/sample_lowlight.jpg","embedding":"sample/img/face_pair",
 "reid":"sample/img/person_pair",
 "ppu":"sample/img/sample_face.jpg","face_alignment":"sample/img/sample_face.jpg",
 "hand_landmark":"sample/img/sample_hand.jpg",
 "attribute_recognition":"sample/img/sample_person_a1.jpg",
 "hand_detection":"sample/img/sample_hand.jpg","keypoint_detection":"sample/img/sample_street.jpg",
 "object_pose_estimation":"sample/dope/000000.png","panoptic_driving_perception":"sample/img/sample_parking.jpg",
 "3d_object_detection":"sample/kitti/velodyne/000049.bin",
 "object_detection_x_semantic_segmentation":"sample/img/sample_parking.jpg"}
# Canonical per-category demo videos — synced to dx_app-dev scripts/run_demo.py (v3.1.x).
# Each maps to a task-appropriate clip present in assets/videos (sample_videos_v3.1.0).
_CAT_VIDEO_OVERRIDES={"object_detection":"assets/videos/snowboard.mp4",
 "face_detection":"assets/videos/dance-group.mov","obb_detection":"assets/videos/obb.mp4",
 "pose_estimation":"assets/videos/dance-solo.mov","hand_landmark":"assets/videos/hand.mp4",
 "hand_detection":"assets/videos/hand.mp4","face_alignment":"assets/videos/face-alignment-closeup.mp4",
 "instance_segmentation":"assets/videos/dogs.mp4","semantic_segmentation":"assets/videos/blackbox-city-road.mp4",
 "classification":"assets/videos/dogs.mp4","depth_estimation":"assets/videos/blackbox-city-road.mp4",
 "image_denoising":"assets/videos/noisy_hand.mp4","image_enhancement":"assets/videos/lowlight.mp4",
 "embedding":"assets/videos/face-pair-sofa.mp4","attribute_recognition":"assets/videos/person-pair-hallway.mp4",
 "reid":"assets/videos/person-pair-hallway.mp4","ppu":"assets/videos/snowboard.mp4",
 "keypoint_detection":"assets/videos/snowboard.mp4","object_pose_estimation":"assets/videos/snowboard.mp4",
 "panoptic_driving_perception":"assets/videos/blackbox-city-road.mp4",
 "3d_object_detection":"assets/videos/blackbox-city-road.mp4",
 "object_detection_x_semantic_segmentation":"assets/videos/blackbox-city-road.mp4"}
CAT_IMAGE={c:_CAT_IMAGE_OVERRIDES.get(c,_DEFAULT_IMAGE) for c in CATEGORIES}
CAT_VIDEO={c:_CAT_VIDEO_OVERRIDES.get(c,_DEFAULT_VIDEO) for c in CATEGORIES}
# Categories whose single-model examples accept image input only (mirror of dx_app
# _IMAGE_ONLY_TASKS in common/runner/sync_runner.py). The run tab disables video/stream
# input for these (see static/js/inference.js updateRunInputMode).
IMAGE_ONLY_CATEGORIES={"embedding","reid","attribute_recognition","hand_landmark",
 "hand_detection","object_pose_estimation","3d_object_detection"}
_TASK_TYPES_EXCLUDE={"face_alignment","hand_landmark","object_detection_x_semantic_segmentation"}
TASK_TYPES=[c for c in CATEGORIES if c not in _TASK_TYPES_EXCLUDE]
POSTPROCESSORS={"object_detection":["yolov5","yolov7","yolov8","yolov9","yolov10","yolov11",
 "yolov12","yolov26","yolox","ssd","nanodet","damoyolo","centernet","efficientdet"],
 "classification":["efficientnet"],"semantic_segmentation":["bisenetv1","bisenetv2","deeplabv3","segformer"],
 "instance_segmentation":["yolov5seg","yolov8seg","yolact"],
 "pose_estimation":["yolov5pose","yolov8pose","centerpose"],
 "face_detection":["scrfd","retinaface","ulfg","yolov5face","yolov7face"],
 "obb_detection":["obb"],"depth_estimation":["fastdepth"],"image_denoising":["dncnn"],
 "super_resolution":["espcn"],"image_enhancement":["zero_dce"],
 "embedding":["arcface","clip_image","clip_text"],"ppu":["yolov5_ppu","yolov7_ppu","yolov5pose_ppu","scrfd_ppu"]}
for _cat in CATEGORIES:
    if _cat not in POSTPROCESSORS:
        POSTPROCESSORS[_cat]=[]
_running_proc=None; _proc_lock=threading.Lock()
_recent_runs=collections.deque(maxlen=50); _history_lock=threading.Lock()
_lab_sessions=collections.OrderedDict(); _lab_lock=threading.Lock()
_LAB_SESSION_MAX=256
_LAB_SESSION_TTL_SECONDS=8*60*60
_HEARTBEAT=time.time(); _HB_TIMEOUT=3600  # 1 hour — prevents premature shutdown during long sessions

DX_COMPILER_VENV = DX_COMPILER_ROOT / "venv-dx-compiler-local"
DX_RT_ROOT = DX_RUNTIME_ROOT / "dx_rt"
DX_DRIVER_ROOT = DX_RUNTIME_ROOT / "dx_rt_npu_linux_driver"
for _name, _path in [("DX_APP_ROOT", DX_APP_ROOT), ("DX_COMPILER_ROOT", DX_COMPILER_ROOT),
                      ("DX_RUNTIME_ROOT", DX_RUNTIME_ROOT)]:
    if not _path.is_dir():
        print(f"[WARNING] {_name} not found: {_path}")
        print(f"[WARNING] Set {_name} environment variable to override")
# Generic background setup-step subprocess state (used by setup_steps.py — NOT compiler).
_comp_proc=None; _comp_lock=threading.Lock()
_comp_log=""; _comp_log_lock=threading.Lock()
_comp_done=False; _comp_exit_code=-1
_comp_dxnn_path=""; _comp_output_dir=""
_comp_stdin_proc=None  # process whose stdin we can write to

_DS=None; _dx_ok=False
def _load_dx():
    global _DS,_dx_ok
    def _imp():
        from dx_engine.device_status import DeviceStatus; return DeviceStatus
    # Try an already-built dx_engine (studio venv) BEFORE injecting fallback paths — the
    # uncompiled dx_rt/python_package/src tree (no _pydxrt.so) would otherwise shadow it
    # and force mock NPU data.
    try:
        _DS=_imp();_dx_ok=True;print("[OK] dx_engine loaded");return
    except Exception:pass
    for sp in _runtime.dx_engine_search_paths():
        if str(sp) not in sys.path:sys.path.insert(0,str(sp))
    try:
        _DS=_imp();_dx_ok=True;print("[OK] dx_engine loaded (via fallback path)")
    except Exception:_dx_ok=False;print("[INFO] dx_engine unavailable — mock NPU data")
_load_dx()

# shared/hardware.py 초기화 — DX App 내 inference/developer에서 get_hw() 사용
from shared.hardware import init_hw as _init_hw
_init_hw(ds=_DS, dx_ok=_dx_ok, npu_stats_bin=_NPU_STATS_BIN, app_root=DX_APP_ROOT)

# python_example scripts hard-depend on numpy+cv2. venv-dx-runtime is frequently an empty
# venv (dx_engine is injected via PYTHONPATH, not pip-installed), so shared.runtime probes
# each candidate and skips any interpreter missing numpy/cv2 — otherwise every python-variant
# demo dies with ModuleNotFoundError. Falls back to the gui server's own python.
_RUNTIME_PYTHON=_runtime.runtime_python()
print(f"[INFO] runtime python: {_RUNTIME_PYTHON}")

# dx_engine is NOT pip-installed — it lives under dx_rt/python_package/src and must be on
# PYTHONPATH for example subprocesses. The gui server injects it into its OWN sys.path at
# import (_load_dx), but that does not propagate to children, so export it explicitly.
_DX_POSTPROCESS_DIRS=[
    DX_APP_ROOT/"build"/"dx_postprocess",
    DX_APP_ROOT/"build_x86_64"/"dx_postprocess",
]
# Only fall back to the dx_rt source tree when the runtime python can't provide dx_engine
# itself (the `_pydxrt` shadow fix — see shared/runtime.py:dx_engine_pythonpath_dirs).
# dx_postprocess dirs are always safe to add (independent pybind extension).
_DX_ENGINE_SRC_DIRS=_runtime.dx_engine_pythonpath_dirs(_RUNTIME_PYTHON)
_RUNTIME_PYTHONPATH=os.pathsep.join(
    str(p) for p in [
        *_DX_ENGINE_SRC_DIRS,
        *_DX_POSTPROCESS_DIRS,
    ] if p.is_dir())
