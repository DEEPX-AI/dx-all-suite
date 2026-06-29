"""
DX Engine 기반 OCR 모델
RapidOCR의 구조를 참고하여 DX Engine으로 구현
"""
import math
import time
import copy
import threading
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple, Callable, Any
import warnings

import cv2
import numpy as np
from loguru import logger
from tqdm import tqdm

from rapid_doc.utils.config_reader import get_device
from rapidocr.ch_ppocr_rec.utils import CTCLabelDecode
from rapid_doc.utils.ocr_utils import (
    check_img,
    preprocess_image,
    sorted_boxes,
    merge_det_boxes,
    update_det_boxes,
    get_rotate_crop_image,
)

try:
    from dx_engine import InferenceEngine, InferenceOption
except ImportError:
    logger.warning("dx_engine not installed. DxOcrModel will not work.")
    InferenceEngine = None

from rapid_doc.utils.device_utils import get_dxnn_devices


class DxOcrEngineType(Enum):
    """DX Engine OCR 엔진 타입"""
    DXENGINE = "dxengine"


class DxTextDetector:
    """DX Engine 기반 텍스트 검출기 (Multi-model 지원)"""
    
    def __init__(
        self,
        model_path: str,
        limit_side_len: int = 960,
        limit_type: str = "max",
        thresh: float = 0.3,
        box_thresh: float = 0.6,
        unclip_ratio: float = 1.5,
        use_dilation: bool = True,
        device: str = "cpu",
        input_size: int = 640,  # DX Engine용 고정 입력 크기
        use_multi_det_model: bool = False,  # Multi-model detection 사용 여부
        model_paths: dict = None,  # Ratio별 모델 경로
        use_async: bool = False,  # Async 모드 사용 여부
        device_ids: list = None,
        device_lock=None,
        **kwargs
    ):
        """
        Args:
            model_path: .dxnn 모델 파일 경로 (단일 모델 또는 기본 모델)
            limit_side_len: 입력 이미지 크기 제한 (사용 안 함 - DX Engine은 고정 크기)
            limit_type: 'max' 또는 'min' (사용 안 함)
            box_thresh: 텍스트 박스 임계값
            unclip_ratio: 박스 확장 비율
            use_dilation: 팽창 연산 사용 여부
            device: 실행 디바이스
            input_size: DX Engine 고정 입력 크기 (기본값: 640)
            use_multi_det_model: Multi-model detection 사용 여부
            model_paths: Ratio별 모델 경로 dict {1: path1, 2: path2, 4: path4}
            use_async: Async 모드 사용 여부
        """
        self.model_path = Path(model_path)
        self.limit_side_len = limit_side_len
        self.limit_type = limit_type
        self.thresh = thresh
        self.box_thresh = box_thresh
        self.unclip_ratio = unclip_ratio
        self.use_dilation = use_dilation
        self.device = device
        self.input_size = input_size
        self.use_async = use_async
        
        # Multi-model detection 설정
        self.use_multi_det_model = use_multi_det_model
        self.det_session_map = {}  # Ratio별 세션 저장
        
        # 전처리 파라미터
        self.mean = np.array([0.485, 0.456, 0.406])
        self.std = np.array([0.229, 0.224, 0.225])
        
        # Async callback 지원을 위한 추가 속성
        # request_id -> {'ori_shape': (h, w), 'target_size': (h, w), 'start_time': float}
        self.pending_requests = {}
        self.lock = threading.Lock()
        self._infer_lock = device_lock if device_lock is not None else threading.Lock()
        self._request_counter = 0  # thread-safe 카운터
        self._callback_session_ids = set()
        
        # DX Engine 초기화
        if InferenceEngine is None:
            raise ImportError("dx_engine is not installed. Please install it first.")
        
        self.io = InferenceOption()
        self.io.devices = device_ids if device_ids is not None else get_dxnn_devices()
        self.io.bound_option = InferenceOption.BOUND_OPTION.NPU_ALL
        
        if self.use_multi_det_model and model_paths:
            # Multi-model: ratio별 세션 초기화
            
            size_map = {
                1: (640, 640),
                2: (320, 640),
                4: (160, 640),
                10: (64, 640),
            }

            for ratio, path in model_paths.items():
                if Path(path).exists():
                    session = InferenceEngine(str(path), self.io)
                    self.det_session_map[ratio] = {
                        'session': session,
                        'path': path,
                        'size': size_map.get(ratio, (640, 640))
                    }
                    logger.info(f"Loaded detection model for ratio {ratio}: {path} (size: {self.det_session_map[ratio]['size']})")
                else:
                    logger.warning(f"Detection model not found for ratio {ratio}: {path}")
            
            if not self.det_session_map:
                logger.warning("No multi-model detection models loaded, falling back to single model")
                self.use_multi_det_model = False
                self.session = InferenceEngine(str(self.model_path), self.io)
                self.input_size = input_size
            else:
                logger.info(f"Multi-detection initialized with {len(self.det_session_map)} models")
        else:
            # Single model
            self.session = InferenceEngine(str(self.model_path), self.io)
            self.input_size = input_size
            logger.info(f"DX Engine static shape mode: input size fixed to {input_size}x{input_size}")
        
        mode_str = "ASYNC" if self.use_async else "SYNC"
        logger.info(f"DxTextDetector initialized with model: {self.model_path} ({mode_str} mode)")
    
    def det_router(self, h: int, w: int) -> int:
        """
        이미지 크기를 기반으로 detection model ratio를 선택
        
        W/H ratio에 따라 (가로가 더 긴 PDF 페이지 가정):
        - W/H <= 2.0: ratio 1 (160x640, 예: 1:4 비율)
        - W/H <= 4.0: ratio 2 (320x640, 예: 1:2 비율)
        - W/H > 4.0: ratio 4 (640x640, 예: 1:1 비율)
        
        Args:
            h: 이미지 높이
            w: 이미지 너비
            
        Returns:
            ratio (1, 2, 또는 4)
        """
        if h == 0:
            return 4  # 기본값
        
        wh_ratio = w / h
        
        if wh_ratio <= 2:
            return 1  # 640x640
        elif wh_ratio <= 4:
            return 2  # 320x640
        elif wh_ratio <= 10:
            return 4  # 160x640
        else:
            return 10  # 64x640

    def _on_detection_complete(self, outputs: List[np.ndarray], user_arg: Any) -> int:
        """
        DX Engine detection 추론 완료 시 호출되는 콜백
        
        Args:
            outputs: DX Engine 출력 결과 [prediction_map]
            user_arg: (unique_id, ori_shape, target_size, callback, start_time)
        
        Returns:
            0 (success)
        """
        try:
            unique_id, ori_shape, target_size, callback, start_time = user_arg
            
            # 후처리: 텍스트 박스 추출
            preds = outputs[0]
            boxes = self._postprocess(preds, ori_shape, target_size)
            
            elapse = time.time() - start_time
            result = DetResult(boxes=boxes, elapse=elapse)
            
            # 사용자 콜백 호출 (있는 경우)
            if callback is not None:
                callback(result, unique_id)
                
            # pending requests에서 제거 (DX Engine의 request_id 기반)
            # unique_id는 우리가 생성한 ID, DX Engine의 request_id와는 별개
                
        except Exception as e:
            logger.error(f"Detection callback error: {e}")
            import traceback
            traceback.print_exc()
            
            # 에러 발생 시에도 콜백 호출
            try:
                unique_id = user_arg[0] if user_arg else -1
                callback_fn = user_arg[3] if len(user_arg) > 3 else None
                if callback_fn is not None:
                    callback_fn(DetResult(boxes=None, elapse=0.0), unique_id)
            except:
                pass
            
        return 0

    def _ensure_callback_registered(self, session):
        """Register DX Engine callback for a session exactly once."""
        if session is None:
            return
        session_id = id(session)
        if session_id in self._callback_session_ids:
            return
        if not hasattr(session, 'register_callback'):
            logger.warning("DX Engine session does not support callbacks; callback parameter ignored")
            return
        session.register_callback(self._on_detection_complete)
        self._callback_session_ids.add(session_id)
    
    def __call__(self, img: np.ndarray):
        """
        텍스트 검출 실행 (동기/비동기 자동 선택)
        """
        with self._infer_lock:
            if self.use_async:
                request_id = self.run_async(img, callback=None)
                return self.wait_request(request_id)
            else:
                return self.run(img)
    
    def run(self, img: np.ndarray):
        """
        텍스트 검출 실행 (동기 방식)
        일반 DX Engine run() 사용
        
        Args:
            img: 입력 이미지 (numpy array)
            
        Returns:
            DetResult: 검출 결과 (boxes, elapse)
        """
        
        start_time = time.time()
        
        if self.use_multi_det_model:
            # Multi-model detection: ratio에 따라 모델 선택
            h, w = img.shape[:2]
            ratio = self.det_router(h, w)
            
            if ratio in self.det_session_map:
                session_info = self.det_session_map[ratio]
                session = session_info['session']
                target_size = session_info['size']
                
                # 1. 전처리 (ratio별 크기로 변환)
                preprocessed, ori_shape = self._preprocess_multi(img, target_size)
                if preprocessed is None:
                    return DetResult(boxes=None, elapse=time.time() - start_time)
                
                # 2. 동기 추론 (run 사용)
                preds = session.run([preprocessed])[0]
                
                if preds is None:
                    logger.warning(f"DX Engine 추론 실패 (ratio {ratio})")
                    return DetResult(boxes=None, elapse=time.time() - start_time)
                
                # 3. 후처리 (원본 크기로 좌표 변환)
                boxes = self._postprocess(preds, ori_shape, target_size)
                
                elapse = time.time() - start_time
                return DetResult(boxes=boxes, elapse=elapse)
            else:
                logger.warning(f"No model found for ratio {ratio}, using default model")
                # Fallback to single model
        
        # Single model detection (fallback)
        # 1. 전처리 (고정 크기로 변환)
        preprocessed, ori_shape = self._preprocess(img)
        if preprocessed is None:
            return DetResult(boxes=None, elapse=time.time() - start_time)
        
        # 2. 동기 추론 (run 사용)
        preds = self.session.run([preprocessed])[0]

        if preds is None:
            logger.warning("DX Engine 추론 실패")
            return DetResult(boxes=None, elapse=time.time() - start_time)
        
        # 3. 후처리 (원본 크기로 좌표 변환)
        boxes = self._postprocess(preds, ori_shape, (self.input_size, self.input_size))
        
        elapse = time.time() - start_time
        return DetResult(boxes=boxes, elapse=elapse)
    
    def run_async(self, img: np.ndarray, callback: Optional[Callable] = None) -> int:
        """
        비동기 텍스트 검출 (callback 사용)
        run_async() 사용
        
        Args:
            img: 입력 이미지 (numpy array)
            callback: 완료 시 호출될 콜백 함수 (result: DetResult, request_id: int)
            
        Returns:
            request_id: 요청 ID
        """
        start_time = time.time()
        
        if self.use_multi_det_model:
            # Multi-model detection: ratio에 따라 모델 선택
            h, w = img.shape[:2]
            ratio = self.det_router(h, w)
            
            if ratio in self.det_session_map:
                session_info = self.det_session_map[ratio]
                session = session_info['session']
                target_size = session_info['size']
                
                # 1. 전처리 (ratio별 크기로 변환)
                preprocessed, ori_shape = self._preprocess_multi(img, target_size)
                if preprocessed is None:
                    if callback:
                        callback(DetResult(boxes=None, elapse=0.0), -1)
                    return -1
                
                # 고유 ID 생성 (thread-safe)
                with self.lock:
                    unique_id = self._request_counter
                    self._request_counter += 1
                
                # 2. 비동기 추론 (user_arg로 후처리 정보 전달)
                if callback is not None:
                    self._ensure_callback_registered(session)
                request_id = session.run_async(
                    [preprocessed],
                    user_arg=(unique_id, ori_shape, target_size, callback, start_time)
                )
                
                # callback을 사용하지 않는 경우에만 wait_request용 메타데이터 저장
                if callback is None:
                    with self.lock:
                        self.pending_requests[request_id] = {
                            'ori_shape': ori_shape,
                            'target_size': target_size,
                            'start_time': start_time,
                        }
                
                return request_id
        
        # Single model detection (fallback)
        # 1. 전처리 (고정 크기로 변환)
        preprocessed, ori_shape = self._preprocess(img)
        if preprocessed is None:
            if callback:
                callback(DetResult(boxes=None, elapse=0.0), -1)
            return -1
        
        # 고유 ID 생성 (thread-safe)
        with self.lock:
            unique_id = self._request_counter
            self._request_counter += 1
        
        # 2. 비동기 추론
        if callback is not None:
            self._ensure_callback_registered(self.session)
        request_id = self.session.run_async(
            [preprocessed],
            user_arg=(unique_id, ori_shape, (self.input_size, self.input_size), callback, start_time)
        )
        
        if callback is None:
            with self.lock:
                self.pending_requests[request_id] = {
                    'ori_shape': ori_shape,
                    'target_size': (self.input_size, self.input_size),
                    'start_time': start_time,
                }
        
        return request_id
    
    def wait_request(self, request_id: int) -> Optional['DetResult']:
        """
        특정 request의 완료를 대기
        
        Args:
            request_id: 대기할 요청 ID
            
        Returns:
            DetResult (callback이 설정되지 않은 경우에만)
        """
        # 잘못된 request_id 처리
        if request_id == -1:
            logger.warning("Invalid request_id (-1), returning empty result")
            return DetResult(boxes=None, elapse=0.0)
        
        # Session을 찾아서 wait 호출
        session = None
        
        with self.lock:
            pending_data = self.pending_requests.pop(request_id, None)
            
        if pending_data is None:
            logger.warning(f"No pending data found for request_id {request_id}, returning empty result")
            return DetResult(boxes=None, elapse=0.0)
        
        ori_shape = pending_data.get('ori_shape')
        target_size = pending_data.get('target_size')
        start_time = pending_data.get('start_time', time.time())
        
        # 적절한 session 찾기
        if self.use_multi_det_model:
            # Multi-model에서 적절한 session 찾기
            for ratio, session_info in self.det_session_map.items():
                if session_info['size'] == target_size:
                    session = session_info['session']
                    break
        else:
            session = self.session
        
        if session is None:
            logger.error(f"No session found for target_size {target_size}")
            return DetResult(boxes=None, elapse=0.0)
        
        # wait 호출
        try:
            outputs = session.wait(request_id)
        except Exception as e:
            logger.error(f"DX Engine wait failed: {e}")
            return DetResult(boxes=None, elapse=time.time() - start_time)
        
        if outputs:
            # callback이 없는 경우 직접 후처리
            preds = outputs[0]
            boxes = self._postprocess(preds, ori_shape, target_size)
            elapse = time.time() - start_time
            
            return DetResult(boxes=boxes, elapse=elapse)
        
        # outputs가 없는 경우
        return DetResult(boxes=None, elapse=time.time() - start_time)
    
    def _preprocess(self, img: np.ndarray) -> Optional[Tuple[np.ndarray, Tuple[int, int]]]:
        """
        이미지 전처리 (DX Engine용 고정 크기 640x640)
        C++ 구현과 동일: pad-to-square(gray 114) → resize to target
        
        Args:
            img: 입력 이미지 (H, W, C)
            
        Returns:
            전처리된 이미지 (1, H, W, C), 원본 크기 (H, W)
        """
        try:
            ori_h, ori_w = img.shape[:2]
            target_size = self.input_size  # 640
            
            # Step 1: Pad to square with gray(114) — 비율 보존
            PAD_COLOR = (114, 114, 114)
            if ori_w < ori_h:
                # 세로가 더 김 → 오른쪽에 패딩
                pad_w = ori_h - ori_w
                padded = cv2.copyMakeBorder(img, 0, 0, 0, pad_w,
                                           cv2.BORDER_CONSTANT, value=PAD_COLOR)
            elif ori_w > ori_h:
                # 가로가 더 김 → 아래에 패딩
                pad_h = ori_w - ori_h
                padded = cv2.copyMakeBorder(img, 0, pad_h, 0, 0,
                                           cv2.BORDER_CONSTANT, value=PAD_COLOR)
            else:
                padded = img
            
            # padded_size = 패딩 후 정방형 크기 (좌표 매핑에 사용)
            padded_h, padded_w = padded.shape[:2]
            
            # Step 2: 정방형 이미지를 target_size × target_size로 resize
            img_resized = cv2.resize(padded, (target_size, target_size))
            
            # 배치 차원 추가
            img_batch = np.expand_dims(img_resized, axis=0)
            
            # ori_shape에 padded_size 정보도 포함 (후처리에서 좌표 매핑용)
            return img_batch, (ori_h, ori_w, padded_h, padded_w)
            
        except Exception as e:
            logger.error(f"전처리 오류: {e}")
            return None, None
    
    def _preprocess_multi(self, img: np.ndarray, target_size: Tuple[int, int]) -> Optional[Tuple[np.ndarray, Tuple[int, int]]]:
        """
        이미지 전처리 (Multi-model detection용, ratio별 가변 크기)
        C++ 구현과 동일: pad-to-square(gray 114) → resize to target
        
        Args:
            img: 입력 이미지 (H, W, C)
            target_size: 타겟 크기 (H, W) - e.g., (160, 640), (320, 640), (640, 640)
            
        Returns:
            전처리된 이미지 (1, target_h, target_w, C), 원본 크기 정보
        """
        try:
            ori_h, ori_w = img.shape[:2]
            target_h, target_w = target_size
            
            # Step 1: Pad to target aspect ratio with gray(114)
            # target이 정방형(640×640)이면 C++과 동일하게 pad-to-square
            # target이 비정방형이면 해당 ratio에 맞게 패딩
            PAD_COLOR = (114, 114, 114)
            target_ratio = target_w / target_h  # e.g., 640/640=1.0, 640/320=2.0
            orig_ratio = ori_w / ori_h
            
            if orig_ratio < target_ratio:
                # 이미지가 target보다 세로로 김 → 오른쪽에 패딩
                new_width = int(ori_h * target_ratio)
                pad_w = new_width - ori_w
                padded = cv2.copyMakeBorder(img, 0, 0, 0, pad_w,
                                           cv2.BORDER_CONSTANT, value=PAD_COLOR)
            elif orig_ratio > target_ratio:
                # 이미지가 target보다 가로로 김 → 아래에 패딩
                new_height = int(ori_w / target_ratio)
                pad_h = new_height - ori_h
                padded = cv2.copyMakeBorder(img, 0, pad_h, 0, 0,
                                           cv2.BORDER_CONSTANT, value=PAD_COLOR)
            else:
                padded = img
            
            padded_h, padded_w = padded.shape[:2]
            
            # Step 2: 타겟 크기로 resize
            img_resized = cv2.resize(padded, (target_w, target_h))
            
            # 배치 차원 추가
            img_batch = np.expand_dims(img_resized, axis=0)
            
            return img_batch, (ori_h, ori_w, padded_h, padded_w)
            
        except Exception as e:
            logger.error(f"Multi-model 전처리 오류: {e}")
            return None, None
    
    def _postprocess(self, preds, ori_shape, model_input_size: Tuple[int, int] = None) -> Optional[np.ndarray]:
        """
        후처리: 예측 결과에서 텍스트 박스 추출 및 원본 크기로 스케일 변환
        C++ 구현과 동일: model_output → padded_space → clip to original
        
        Args:
            preds: 모델 예측 결과 (probability map, shape: [1, 1, H, W])
            ori_shape: (ori_h, ori_w) 또는 (ori_h, ori_w, padded_h, padded_w)
            model_input_size: 모델 입력 크기 (H, W), None이면 self.input_size 사용
            
        Returns:
            텍스트 박스 배열 (N, 4, 2) - N개의 사각형, 각 4개 점 (원본 이미지 좌표)
        """
        if preds is None:
            return None
        
        try:
            import cv2
            from shapely.geometry import Polygon
            import pyclipper
            
            if model_input_size is None:
                if hasattr(self, 'input_size'):
                    model_h = model_w = self.input_size
                else:
                    model_h, model_w = preds.shape[2], preds.shape[3]
            else:
                model_h, model_w = model_input_size
            
            # ori_shape에서 정보 추출
            if len(ori_shape) == 4:
                ori_h, ori_w, padded_h, padded_w = ori_shape
            else:
                ori_h, ori_w = ori_shape[:2]
                # 패딩 정보 없으면 기존 방식 (하위 호환)
                padded_h, padded_w = ori_h, ori_w
            
            # 1. Probability map에서 이진화
            pred = preds[0, 0, :, :]  # (H, W)
            segmentation = pred > self.thresh
            
            # 2. 팽창 연산 (선택적)
            if self.use_dilation:
                kernel = np.ones((2, 2), np.uint8)
                segmentation = cv2.dilate(segmentation.astype(np.uint8), kernel)
            
            # 3. 윤곽선 찾기
            contours, _ = cv2.findContours(
                segmentation.astype(np.uint8),
                cv2.RETR_LIST,
                cv2.CHAIN_APPROX_SIMPLE
            )
            
            boxes = []
            scores = []
            
            # C++ 방식 좌표 매핑: model_output → padded_space → clip to original
            # scale = padded_size / model_output_size
            scale_h = padded_h / model_h
            scale_w = padded_w / model_w
            
            for contour in contours:
                # 최소 영역 계산
                if contour.shape[0] < 4:
                    continue
                
                # 점수 계산
                score = self._get_mini_boxes_score(pred, contour)
                if score < self.box_thresh:
                    continue
                
                # Unclip (박스 확장)
                try:
                    box = self._unclip(contour, self.unclip_ratio)
                    if box is None:
                        continue
                    
                    # 최소 외접 사각형
                    rect = cv2.minAreaRect(box)
                    points = cv2.boxPoints(rect)

                    box_width = np.max(points[:, 0]) - np.min(points[:, 0])
                    box_height = np.max(points[:, 1]) - np.min(points[:, 1])
                    MIN_BOX_SIZE = 5  # 픽셀
                    if box_width < MIN_BOX_SIZE or box_height < MIN_BOX_SIZE:
                        continue
                    
                    # ✅ Option 1: 점 순서 정렬 (좌상단부터 시계방향)
                    # y 좌표 기준으로 정렬하여 상단 2개, 하단 2개 분리
                    points_sorted = sorted(points, key=lambda p: p[1])
                    top_points = sorted(points_sorted[:2], key=lambda p: p[0])    # 상단: x 기준 정렬
                    bottom_points = sorted(points_sorted[2:], key=lambda p: p[0])  # 하단: x 기준 정렬
                    points = np.array([top_points[0], top_points[1], bottom_points[1], bottom_points[0]])
                    
                    # model_output → padded_space → clip to original bounds
                    points[:, 0] = np.clip(points[:, 0] * scale_w, 0, ori_w)
                    points[:, 1] = np.clip(points[:, 1] * scale_h, 0, ori_h)
                    
                    boxes.append(points)
                    scores.append(score)
                    
                except Exception as e:
                    logger.debug(f"Box processing error: {e}")
                    continue
            
            if len(boxes) == 0:
                return None
            
            return np.array(boxes, dtype=np.float32)
            
        except Exception as e:
            logger.error(f"후처리 오류: {e}")
            return None
    
    def _get_mini_boxes_score(self, pred: np.ndarray, contour: np.ndarray) -> float:
        """
        윤곽선 내부의 평균 점수 계산
        
        Args:
            pred: Probability map
            contour: 윤곽선
            
        Returns:
            평균 점수
        """
        min_score = 1.0
        try:
            mask = np.zeros(pred.shape, dtype=np.uint8)
            cv2.fillPoly(mask, [contour.astype(np.int32)], 1)
            return float(cv2.mean(pred, mask)[0])
        except:
            return min_score
    
    def _unclip(self, box: np.ndarray, unclip_ratio: float) -> Optional[np.ndarray]:
        """
        박스를 확장하여 텍스트 전체를 포함하도록 함
        
        Args:
            box: 윤곽선
            unclip_ratio: 확장 비율
            
        Returns:
            확장된 박스
        """
        try:
            import pyclipper
            from shapely.geometry import Polygon
            
            poly = Polygon(box.reshape(-1, 2))
            distance = poly.area * unclip_ratio / poly.length
            
            pco = pyclipper.PyclipperOffset()
            pco.AddPath(box.reshape(-1, 2).astype(np.int32).tolist(), 
                       pyclipper.JT_ROUND, 
                       pyclipper.ET_CLOSEDPOLYGON)
            expanded = pco.Execute(distance)
            
            if not expanded or len(expanded) == 0:
                return None
            
            # 첫 번째 폴리곤을 numpy array로 변환
            return np.array(expanded[0])
            
        except Exception as e:
            logger.debug(f"Unclip error: {e}")
            return None


class DxTextRecognizer:
    """DX Engine 기반 텍스트 인식기"""
    
    def __init__(
        self,
        model_path: str,
        rec_batch_num: int = 6,
        device: str = "cpu",
        input_height: int = 48,   # DX Engine용 고정 높이
        input_width: int = 640,   # DX Engine용 고정 너비
        char_dict_path: str = "None",
        use_async: bool = False,  # Async 모드 사용 여부
        device_ids: list = None,
        device_lock=None,
        **kwargs
    ):
        """
        Args:
            model_path: .dxnn 모델 파일 경로
            rec_batch_num: 배치 크기 (DX Engine은 배치 처리 미지원, 1로 강제됨)
            device: 실행 디바이스
            input_height: DX Engine 고정 입력 높이 (기본값: 48)
            input_width: DX Engine 고정 입력 너비 (기본값: 640)
            use_async: Async 모드 사용 여부
        """
        self.model_path = Path(model_path)
        # DX Engine은 배치 처리를 지원하지 않으므로 1로 강제
        self.rec_batch_num = 1
        self.device = device
        self.character_dict_path = char_dict_path
        self.use_async = use_async
        
        if rec_batch_num != 1:
            logger.warning(f"DX Engine does not support batch processing. Forcing rec_batch_num=1 (was {rec_batch_num})")
        
        # DX Engine용 고정 입력 크기
        self.input_height = input_height
        self.input_width = input_width
        self.rec_image_shape = [3, input_height, input_width]  # C, H, W
        
        logger.info(f"DX Engine static shape mode: input size fixed to {input_height}x{input_width}")
        
        # DX Engine 초기화
        if InferenceEngine is None:
            raise ImportError("dx_engine is not installed. Please install it first.")
        
        self.io = InferenceOption()
        self.io.devices = device_ids if device_ids is not None else get_dxnn_devices()
        self.io.bound_option = InferenceOption.BOUND_OPTION.NPU_ALL
        
        self.session = InferenceEngine(str(self.model_path), self.io)
        
        # Async callback 지원을 위한 추가 속성
        # request_id -> True (콜백 미사용 요청 추적)
        self.pending_requests = {}
        self.rec_lock = threading.Lock()
        self._infer_lock = device_lock if device_lock is not None else threading.Lock()
        self._request_counter = 0  # thread-safe 카운터
        self._callback_registered = False
        
        if self.use_async:
            logger.info("DxTextRecognizer initialized in ASYNC mode (callbacks on demand)")
        else:
            logger.info("DxTextRecognizer initialized in SYNC mode")
        
        # 문자 사전 (TODO: 모델 메타데이터에서 로드 또는 외부 파일에서 로드)
        self.character_dict = self._load_character_dict()
        self.ctc_decoder = CTCLabelDecode(character=self.character_dict)
    
    def _load_character_dict(self) -> List[str]:
        """
        문자 사전 로드
        
        Returns:
            문자 리스트
        """
        try:
            with open(self.character_dict_path, 'r', encoding='utf-8') as f:
                char_list = [line.strip() for line in f]
            return char_list
            
        except Exception as e:
            logger.error(f"문자 사전 로드 실패: {e}")
            return []
    
    def _on_recognition_complete(self, outputs: List[np.ndarray], user_arg: Any) -> int:
        """
        DX Engine recognition 추론 완료 시 호출되는 콜백
        
        Args:
            outputs: DX Engine 출력 결과
            user_arg: (unique_id, img_idx, callback, start_time)
        
        Returns:
            0 (success)
        """
        try:
            unique_id, img_idx, callback, start_time = user_arg
            
            # 후처리: 텍스트 디코딩
            preds = outputs[0]
            text, score = self._postprocess_single(preds)
            
            elapse = time.time() - start_time
            
            # 사용자 콜백 호출 (있는 경우)
            if callback is not None:
                callback(text, score, img_idx, unique_id)
                
        except Exception as e:
            logger.error(f"Recognition callback error: {e}")
            import traceback
            traceback.print_exc()
            
            # 에러 발생 시에도 콜백 호출
            try:
                unique_id = user_arg[0] if user_arg else -1
                img_idx = user_arg[1] if len(user_arg) > 1 else 0
                callback_fn = user_arg[2] if len(user_arg) > 2 else None
                if callback_fn is not None:
                    callback_fn("", 0.0, img_idx, unique_id)
            except:
                pass
            
        return 0

    def _ensure_callback_registered(self):
        """Register recognition callback only when needed."""
        if self._callback_registered:
            return
        if not hasattr(self.session, 'register_callback'):
            logger.warning("DX Engine recognizer session does not support callbacks; callback parameter ignored")
            return
        self.session.register_callback(self._on_recognition_complete)
        self._callback_registered = True
    
    def __call__(self, img_list: List[np.ndarray]) -> 'RecResult':
        """Run text recognition (auto-selects sync/async)"""
        with self._infer_lock:
            if self.use_async:
                request_ids = self.recognize_batch_async(img_list, callback=None)
                all_txts = []
                all_scores = []
                for req_id in request_ids:
                    result = self.wait_request(req_id)
                    if result:
                        text, score = result
                        all_txts.append(text)
                        all_scores.append(score)
                    else:
                        all_txts.append("")
                        all_scores.append(0.0)
                return RecResult(txts=all_txts, scores=all_scores, elapse=0.0)
            else:
                return self.run(img_list)
    
    def run(self, img_list: List[np.ndarray]) -> 'RecResult':
        """
        텍스트 인식 실행 (동기 방식)
        DX Engine은 배치 처리 미지원, 개별 처리
        일반 DX Engine run() 사용
        
        Args:
            img_list: 입력 이미지 리스트
            
        Returns:
            RecResult: 인식 결과 (txts, scores, elapse)
        """
        start_time = time.time()
        
        if not img_list:
            return RecResult(txts=[], scores=[], elapse=0.0)
        
        all_txts = []
        all_scores = []
        
        img_num = len(img_list)
        i = 0
        # DX Engine은 배치 처리 미지원 - 개별 이미지 처리
        for img in img_list:
            # 1. 전처리 (단일 이미지)
            img_input = self._preprocess_single(img)
            
            # 2. 동기 추론 (run 사용)
            try:
                preds = self.session.run(img_input)[0]
            except Exception as e:
                logger.error(f"DX Engine 추론 오류: {e}")
                all_txts.append("")
                all_scores.append(0.0)
                continue
            
            # 3. 후처리 (단일 결과)
            text, score = self._postprocess_single(preds)
            all_txts.append(text)
            all_scores.append(score)
            
        
        elapse = time.time() - start_time
        return RecResult(txts=all_txts, scores=all_scores, elapse=elapse)
    
    def run_async(self, img: np.ndarray, img_idx: int = 0, 
                  callback: Optional[Callable] = None) -> int:
        """
        비동기 텍스트 인식 (단일 이미지, callback 사용)
        run_async() 사용
        
        Args:
            img: 입력 이미지 (numpy array)
            img_idx: 이미지 인덱스 (배치 처리 시 구분용)
            callback: 완료 시 호출될 콜백 함수 (text: str, score: float, img_idx: int, request_id: int)
            
        Returns:
            request_id: 요청 ID
        """
        start_time = time.time()
        
        # 1. 전처리 (단일 이미지)
        img_input = self._preprocess_single(img)
        
        # 고유 ID 생성 (thread-safe)
        with self.rec_lock:
            unique_id = self._request_counter
            self._request_counter += 1
        
        # 2. 비동기 추론 (user_arg로 후처리 정보 전달)
        if callback is not None:
            self._ensure_callback_registered()
        request_id = self.session.run_async(
            img_input,
            user_arg=(unique_id, img_idx, callback, start_time)
        )
        
        if callback is None:
            with self.rec_lock:
                self.pending_requests[request_id] = True
        
        return request_id
    
    def recognize_batch_async(self, img_list: List[np.ndarray], 
                             callback: Optional[Callable] = None) -> List[int]:
        """
        비동기 텍스트 인식 (배치, callback 사용)
        
        Args:
            img_list: 입력 이미지 리스트
            callback: 완료 시 호출될 콜백 함수 (text: str, score: float, img_idx: int, request_id: int)
            
        Returns:
            request_ids: 요청 ID 리스트
        """
        request_ids = []
        
        for idx, img in enumerate(img_list):
            req_id = self.run_async(img, idx, callback)
            request_ids.append(req_id)
        
        return request_ids
    
    def wait_request(self, request_id: int) -> Optional[Tuple[str, float]]:
        """
        특정 request의 완료를 대기
        
        Args:
            request_id: 대기할 요청 ID
            
        Returns:
            (text, score) tuple (callback이 설정되지 않은 경우에만)
        """
        # 잘못된 request_id 처리
        if request_id == -1:
            logger.warning("Invalid request_id (-1), returning empty result")
            return ("", 0.0)
        
        with self.rec_lock:
            pending_flag = self.pending_requests.pop(request_id, None)
        
        if pending_flag is None:
            logger.warning(f"No pending data found for request_id {request_id}, returning empty result")
            return ("", 0.0)
        
        # wait 호출
        try:
            outputs = self.session.wait(request_id)
        except Exception as e:
            logger.error(f"DX Engine wait failed: {e}")
            return ("", 0.0)
        
        if outputs:
            preds = outputs[0]
            text, score = self._postprocess_single(preds)
            return (text, score)
        
        return ("", 0.0)
    
    def _preprocess_single(self, img: np.ndarray) -> np.ndarray:
        """
        단일 이미지 전처리 (DX Engine용)
        
        Args:
            img: 입력 이미지 (H, W, C)
            
        Returns:
            전처리된 이미지 (1, H, W, C) - batch_size=1
        """
        try:
            imgC, imgH, imgW = self.rec_image_shape
            
            # Width/Height 비율 계산
            h, w = img.shape[:2]
            wh_ratio = w * 1.0 / h
            max_wh_ratio = max(imgW / imgH, wh_ratio)
            
            # 이미지 리사이즈 및 패딩
            norm_img = self._resize_norm_img(img, max_wh_ratio)
            
            # batch 차원 추가 (1, H, W, C)
            batch_img = norm_img[np.newaxis, :]
            
            return batch_img
            
        except Exception as e:
            logger.error(f"전처리 오류: {e}")
            return np.zeros((1, *self.rec_image_shape[::-1]), dtype=np.uint8)  # (1, H, W, C)

    
    def _resize_norm_img(self, img: np.ndarray, max_wh_ratio: float, target_height: int = None, target_width: int = None) -> np.ndarray:
        """
        단일 이미지 리사이즈 및 정규화
        
        Args:
            img: 입력 이미지 (H, W, C)
            max_wh_ratio: 최대 W/H 비율
            target_height: 목표 높이 (None이면 self.rec_image_shape 사용)
            target_width: 목표 너비 (None이면 self.rec_image_shape 사용)
            
        Returns:
            전처리된 이미지 (H, W, C)
        """
        if target_height is None or target_width is None:
            imgC, imgH, imgW = self.rec_image_shape
        else:
            imgH, imgW = target_height, target_width
            imgC = 3
        
        # 리사이즈
        h, w = img.shape[:2]
        ratio = w / float(h)
        
        if math.ceil(imgH * ratio) > imgW:
            resized_w = imgW
        else:
            resized_w = int(math.ceil(imgH * ratio))
        
        resized_image = cv2.resize(img, (resized_w, imgH))
        
        # 패딩 (회색 114 — C++ 구현과 동일, 모델 학습 데이터와 일치)
        padding_im = np.ones((imgH, imgW, imgC), dtype=np.uint8) * 114
        padding_im[:, :resized_w, :] = resized_image
        
        return padding_im
    
    def _postprocess_single(self, preds) -> Tuple[str, float]:
        """
        후처리: 단일 예측 결과를 텍스트로 변환 (CTC 디코딩)
        
        Args:
            preds: 모델 예측 결과 (1, T, C) - Batch=1, Time, Classes
            
        Returns:
            (텍스트, 신뢰도)
        """
        if preds is None:
            return "", 0.0
        
        # RapidOCR의 CTCLabelDecode 사용
        # preds shape: (1, T, C) - 배치 크기 1
        line_results, _ = self.ctc_decoder(preds, return_word_box=False)
        
        # line_results: [(text, confidence)]
        if line_results:
            text, score = line_results[0]
            return text, score
        else:
            return "", 0.0



class DetResult:
    """검출 결과"""
    def __init__(self, boxes, elapse):
        self.boxes = boxes
        self.elapse = elapse


class RecResult:
    """인식 결과"""
    def __init__(self, txts, scores, elapse):
        self.txts = txts
        self.scores = scores
        self.elapse = elapse


class DxOcrModel:
    """
    DX Engine 기반 OCR 모델
    RapidOcrModel과 동일한 인터페이스 제공
    """
    
    def __init__(
        self,
        det_model_path: Optional[str] = None,
        rec_model_path: Optional[str] = None,
        det_db_box_thresh: float = 0.3,
        det_db_unclip_ratio: float = 1.5,
        use_dilation: bool = True,
        enable_merge_det_boxes: bool = True,
        lang: Optional[str] = None,
        ocr_config: Optional[dict] = None,
        use_async: bool = False,
        det_device_ids: list = None,
        det_device_lock=None,
        rec_device_ids: list = None,
        rec_device_lock=None,
    ):
        """
        Args:
            det_model_path: 검출 모델 경로 (.dxnn)
            rec_model_path: 인식 모델 경로 (.dxnn)
            det_db_box_thresh: 검출 박스 임계값
            det_db_unclip_ratio: 박스 확장 비율
            use_dilation: 팽창 연산 사용 여부
            enable_merge_det_boxes: 박스 병합 활성화
            lang: 언어 설정
            ocr_config: OCR 설정
            use_async: Async 모드 사용 여부
        """
        self.drop_score = 0.3
        self.enable_merge_det_boxes = enable_merge_det_boxes
        self.use_async = use_async
        
        device = get_device()
        
        # Multi-model recognition 설정 (PaddleOCR 스타일)
        self.use_multi_rec_model = ocr_config.get('use_multi_rec_model', False) if ocr_config else False
        
        # Debug save 설정
        self.save_debug_images = ocr_config.get('save_debug_images', False) if ocr_config else False
        self.debug_save_dir = ocr_config.get('debug_save_dir', 'ocr_debug') if ocr_config else 'ocr_debug'
        self.debug_counter = 0
        
        logger.info(f"🔧 DX OCR __init__ | save_debug_images={self.save_debug_images} | debug_save_dir={self.debug_save_dir}")
        
        # Debug 디렉토리 생성
        if self.save_debug_images:
            import os
            os.makedirs(self.debug_save_dir, exist_ok=True)
            os.makedirs(f"{self.debug_save_dir}/det_input", exist_ok=True)
            os.makedirs(f"{self.debug_save_dir}/det_crops", exist_ok=True)
            os.makedirs(f"{self.debug_save_dir}/rec_crops", exist_ok=True)
            logger.info(f"✅ Debug image saving enabled: {self.debug_save_dir}")
        
        # 기본 설정
        default_config = {
            "det_limit_side_len": 960,
            "det_limit_type": "max",
            "det_box_thresh": det_db_box_thresh,
            "det_unclip_ratio": det_db_unclip_ratio,
            "det_use_dilation": use_dilation,
            "rec_batch_num": 6,
            "device": device,
        }
        
        # 사용자 설정 병합
        if ocr_config:
            default_config.update(ocr_config)
        
        # 모델 경로 설정
        if det_model_path is None:
            # TODO: 기본 모델 경로 설정
            logger.warning("검출 모델 경로가 지정되지 않았습니다!")
            det_model_path = "path/to/default/det_model.dxnn"
        
        if rec_model_path is None:
            # TODO: 기본 모델 경로 설정
            logger.warning("인식 모델 경로가 지정되지 않았습니다!")
            rec_model_path = "path/to/default/rec_model.dxnn"
        
        # Multi-model detection 설정
        use_multi_det_model = ocr_config.get('use_multi_det_model', False) if ocr_config else False
        det_model_paths = ocr_config.get('Det.model_paths', {}) if ocr_config else {}
        
        # 검출기와 인식기 초기화
        self.text_detector = DxTextDetector(
            model_path=det_model_path,
            limit_side_len=default_config["det_limit_side_len"],
            limit_type=default_config["det_limit_type"],
            box_thresh=default_config["det_box_thresh"],
            unclip_ratio=default_config["det_unclip_ratio"],
            use_dilation=default_config["det_use_dilation"],
            device=default_config["device"],
            use_multi_det_model=use_multi_det_model,
            model_paths=det_model_paths,
            use_async=self.use_async,
            device_ids=det_device_ids,
            device_lock=det_device_lock,
        )
        
        self.text_recognizer = DxTextRecognizer(
            model_path=rec_model_path,
            rec_batch_num=default_config["rec_batch_num"],
            device=default_config["device"],
            char_dict_path=default_config.get("char_dict_path", "None"),
            use_async=self.use_async,
            device_ids=rec_device_ids,
            device_lock=rec_device_lock,
        )
        
        self.rec_batch_num = self.text_recognizer.rec_batch_num
        
        # Multi-model recognition 초기화 (PaddleOCR 방식)
        if self.use_multi_rec_model:
            self._init_multi_rec_models(ocr_config)
        
        logger.info("DxOcrModel initialized successfully")
    
    def _init_multi_rec_models(self, ocr_config):
        """
        Initialize multi-recognition models based on PaddleOCR architecture
        Ratio-based model selection: [3, 5, 10, 15, 25, 35]
        """
        # Get model paths from config
        rec_model_paths = ocr_config.get('Rec.model_paths', {})
        if not rec_model_paths:
            logger.warning("Multi-rec model enabled but no model paths provided. Using single model.")
            self.use_multi_rec_model = False
            return
        
        # Initialize separate recognizer for each ratio
        self.rec_recognizer_map = {}
        device = ocr_config.get('device', 'cpu')
        char_dict_path = ocr_config.get('char_dict_path', 'None')
        
        # Ratio별 고정 크기 (PaddleOCR 표준)
        ratio_size_map = {
            3: (48, 120),    # 48x120
            5: (48, 240),    # 48x240
            10: (48, 480),   # 48x480
            15: (48, 720),   # 48x720
            25: (48, 1200),  # 48x1200
            35: (48, 1680),  # 48x1680
        }
        
        for ratio in [3, 5, 10, 15, 25, 35]:
            model_path = rec_model_paths.get(ratio)
            if model_path:
                imgH, imgW = ratio_size_map[ratio]
                # Create dedicated recognizer for this ratio
                recognizer = DxTextRecognizer(
                    model_path=model_path,
                    rec_batch_num=1,
                    device=device,
                    input_height=imgH,
                    input_width=imgW,
                    char_dict_path=char_dict_path,
                    use_async=self.use_async,
                )
                self.rec_recognizer_map[ratio] = recognizer
                logger.info(f"Loaded recognition model for ratio {ratio}: {model_path} (size: {imgH}x{imgW})")
            else:
                logger.warning(f"No model path for ratio {ratio}, using default")
        
        logger.info(f"Multi-recognition initialized with {len(self.rec_recognizer_map)} recognizers")
    
    def rec_router(self, width, height):
        """
        Route image to appropriate recognition model based on aspect ratio
        Same as PaddleOCR's rec_router
        """
        ratio = width / height
        
        if ratio <= 3:
            return 3
        elif ratio <= 5:
            return 5
        elif ratio <= 10:
            return 10
        elif ratio <= 15:
            return 15
        elif ratio <= 25:
            return 25
        else:
            return 35
    
    def update_debug_save_dir(self, debug_save_dir: str):
        """
        Update debug save directory and reset counter (for per-PDF processing)
        
        Args:
            debug_save_dir: New debug save directory path
        """
        self.debug_save_dir = debug_save_dir
        self.debug_counter = 0
        
        if self.save_debug_images:
            import os
            os.makedirs(self.debug_save_dir, exist_ok=True)
            os.makedirs(f"{self.debug_save_dir}/det_input", exist_ok=True)
            os.makedirs(f"{self.debug_save_dir}/det_crops", exist_ok=True)
            logger.info(f"Debug save directory updated: {self.debug_save_dir}")
    
    def ocr(
        self,
        img,
        det: bool = True,
        rec: bool = True,
        mfd_res=None,
        tqdm_enable: bool = False,
        tqdm_desc: str = "OCR-rec Predict",
    ):
        """
        OCR 실행 (RapidOcrModel과 동일한 인터페이스)
        
        Args:
            img: 입력 이미지
            det: 검출 수행 여부
            rec: 인식 수행 여부
            mfd_res: MFD 결과
            tqdm_enable: 진행바 표시
            tqdm_desc: 진행바 설명
            
        Returns:
            OCR 결과 리스트
        """
        assert isinstance(img, (np.ndarray, list, str, bytes))
        
        if isinstance(img, list) and det:
            logger.error("When input a list of images, det must be false")
            return None
        
        img = check_img(img)
        imgs = [img]
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            if det and rec:
                ocr_res = []
                for img in imgs:
                    img = preprocess_image(img)
                    dt_boxes, rec_res = self.__call__(img, mfd_res=mfd_res)
                    if not dt_boxes and not rec_res:
                        ocr_res.append(None)
                        continue
                    tmp_res = [[box.tolist(), res] for box, res in zip(dt_boxes, rec_res)]
                    ocr_res.append(tmp_res)
                return ocr_res
            
            elif det and not rec:
                ocr_res = []
                for img in imgs:
                    img = preprocess_image(img)
                    ori_im = img.copy()
                    
                    if self.save_debug_images:
                        det_input_path = f"{self.debug_save_dir}/det_input/det_input_{self.debug_counter:06d}.jpg"
                        cv2.imwrite(det_input_path, img)
                    
                    det_res = self.text_detector(img)
                    dt_boxes, elapse = det_res.boxes, det_res.elapse
                    
                    if dt_boxes is None:
                        ocr_res.append(None)
                        continue
                    
                    dt_boxes = np.array(dt_boxes)
                    dt_boxes = sorted_boxes(dt_boxes)
                    
                    if self.enable_merge_det_boxes:
                        dt_boxes = merge_det_boxes(dt_boxes)
                    
                    if mfd_res:
                        dt_boxes = update_det_boxes(dt_boxes, mfd_res)
                    
                    if self.save_debug_images:
                        img_with_boxes = ori_im.copy()
                        for box in dt_boxes:
                            box = np.array(box).astype(np.int32).reshape((-1, 1, 2))
                            cv2.polylines(img_with_boxes, [box], True, (0, 255, 0), 2)
                        det_bbox_path = f"{self.debug_save_dir}/det_input/det_bbox_{self.debug_counter:06d}.jpg"
                        cv2.imwrite(det_bbox_path, img_with_boxes)
                        self.debug_counter += 1
                    
                    tmp_res = [box.tolist() for box in dt_boxes]
                    ocr_res.append(tmp_res)
                return ocr_res
            
            elif not det and rec:
                ocr_res = []
                for img in imgs:
                    if not isinstance(img, list):
                        img = preprocess_image(img)
                        img = [img]
                    
                    if self.use_multi_rec_model:
                        from collections import defaultdict as _defaultdict
                        # Phase 1: Group crops by ratio
                        ratio_groups = _defaultdict(list)
                        for crop_idx, crop_img in enumerate(img):
                            if self.save_debug_images:
                                crop_path = f"{self.debug_save_dir}/rec_crops/rec_crop_{self.debug_counter:06d}_{crop_idx:03d}.jpg"
                                cv2.imwrite(crop_path, crop_img)
                            h, w = crop_img.shape[:2]
                            ratio = self.rec_router(w, h)
                            ratio_groups[ratio].append((crop_idx, crop_img))

                        # Phase 2: Submit each ratio group as a single batch
                        total_crops = len(img)
                        rec_results = [("", 0.0)] * total_crops

                        for ratio, group in ratio_groups.items():
                            recognizer = self.rec_recognizer_map.get(ratio, self.text_recognizer)
                            crop_imgs = [crop for _, crop in group]
                            try:
                                rec_result = recognizer(crop_imgs)
                                if rec_result.txts:
                                    for (orig_idx, _), text, score in zip(
                                        group, rec_result.txts, rec_result.scores
                                    ):
                                        rec_results[orig_idx] = (text, score)
                            except Exception as e:
                                logger.error(f"Batch rec failed for ratio {ratio}: {e}")
                        
                        if self.save_debug_images and len(img) > 0:
                            self.debug_counter += 1
                        
                        ocr_res.append(rec_results)
                    else:
                        for crop_idx, crop_img in enumerate(img):
                            if self.save_debug_images:
                                crop_path = f"{self.debug_save_dir}/rec_crops/rec_crop_{self.debug_counter:06d}_{crop_idx:03d}.jpg"
                                cv2.imwrite(crop_path, crop_img)
                        
                        if self.save_debug_images and len(img) > 0:
                            self.debug_counter += 1
                        
                        rec_result = self.text_recognizer(img)
                        rec_res = list(zip(rec_result.txts, rec_result.scores))
                        ocr_res.append(rec_res)
                
                return ocr_res
    
    DET_BATCH_CHUNK_SIZE = 16

    def ocr_det_batch(self, images, mfd_res_list=None):
        """Batch detection: submit all images, then wait for all results.

        Processes in chunks of DET_BATCH_CHUNK_SIZE to limit memory.
        Falls back to sequential processing on chunk failure.
        """
        all_results = []

        for chunk_start in range(0, len(images), self.DET_BATCH_CHUNK_SIZE):
            chunk_end = min(chunk_start + self.DET_BATCH_CHUNK_SIZE, len(images))
            chunk_imgs = images[chunk_start:chunk_end]
            chunk_mfds = (
                mfd_res_list[chunk_start:chunk_end]
                if mfd_res_list
                else [None] * len(chunk_imgs)
            )
            try:
                chunk_results = self._det_batch_chunk(chunk_imgs, chunk_mfds)
                all_results.extend(chunk_results)
            except Exception as e:
                logger.error(f"Batch det chunk failed: {e}, falling back to sequential")
                for i, img in enumerate(chunk_imgs):
                    mfd = chunk_mfds[i]
                    try:
                        seq_res = self.ocr(img, det=True, rec=False, mfd_res=mfd)
                        all_results.append(seq_res[0] if seq_res else None)
                    except Exception:
                        all_results.append(None)

        return all_results

    def _det_batch_chunk(self, images, mfd_list):
        """Process one chunk: preprocess → submit → wait → postprocess."""
        preprocessed = []
        ori_images = []
        for img in images:
            img = preprocess_image(img)
            ori_images.append(img.copy() if self.save_debug_images else None)
            preprocessed.append(img)

        results = []

        if self.text_detector.use_async:
            with self.text_detector._infer_lock:
                # Phase 1: Submit all
                request_infos = []
                for i, img in enumerate(preprocessed):
                    if self.save_debug_images:
                        det_path = f"{self.debug_save_dir}/det_input/det_input_{self.debug_counter + i:06d}.jpg"
                        cv2.imwrite(det_path, img)
                    req_id = self.text_detector.run_async(img, callback=None)
                    request_infos.append((req_id, img, mfd_list[i], i))

                # Phase 2: Wait for all
                for req_id, img, mfd_res, local_idx in request_infos:
                    if req_id == -1:
                        results.append(None)
                        continue
                    det_res = self.text_detector.wait_request(req_id)
                    boxes = self._postprocess_det_result(
                        det_res, img, mfd_res, ori_images[local_idx], local_idx
                    )
                    results.append(boxes)
        else:
            # Sync mode: use __call__ per item
            for i, img in enumerate(preprocessed):
                if self.save_debug_images:
                    det_path = f"{self.debug_save_dir}/det_input/det_input_{self.debug_counter + i:06d}.jpg"
                    cv2.imwrite(det_path, img)
                det_res = self.text_detector(img)
                boxes = self._postprocess_det_result(
                    det_res, img, mfd_list[i], ori_images[i], i
                )
                results.append(boxes)

        self.debug_counter += len(images)
        return results

    def _postprocess_det_result(self, det_res, img, mfd_res, ori_img, local_idx):
        """Shared post-processing for a single detection result."""
        dt_boxes = det_res.boxes
        if dt_boxes is None:
            return None
        dt_boxes = np.array(dt_boxes)
        dt_boxes = sorted_boxes(dt_boxes)
        if self.enable_merge_det_boxes:
            dt_boxes = merge_det_boxes(dt_boxes)
        if mfd_res:
            dt_boxes = update_det_boxes(dt_boxes, mfd_res)
        if self.save_debug_images and ori_img is not None:
            img_with_boxes = ori_img.copy()
            for box in dt_boxes:
                box_arr = np.array(box).astype(np.int32).reshape((-1, 1, 2))
                cv2.polylines(img_with_boxes, [box_arr], True, (0, 255, 0), 2)
            bbox_path = f"{self.debug_save_dir}/det_input/det_bbox_{self.debug_counter + local_idx:06d}.jpg"
            cv2.imwrite(bbox_path, img_with_boxes)
        return [box.tolist() for box in dt_boxes]
    
    def __call__(self, img, mfd_res=None):
        """Run detection + recognition (each protected by _infer_lock in DxTextDetector/DxTextRecognizer)"""
        logger.debug(f"DX OCR __call__ invoked | save_debug_images={self.save_debug_images} | counter={self.debug_counter}")
        
        if img is None:
            logger.debug("no valid image provided")
            return None, None
        
        ori_im = img.copy()
        
        # Save detection input image if debug enabled
        if self.save_debug_images:
            det_input_path = f"{self.debug_save_dir}/det_input/det_input_{self.debug_counter:06d}.jpg"
            cv2.imwrite(det_input_path, img)
            logger.debug(f"Saved detection input: {det_input_path}")
        
        # 1. 텍스트 검출
        det_res = self.text_detector(img)
        dt_boxes, elapse = det_res.boxes, det_res.elapse
        
        if dt_boxes is None:
            logger.debug("no dt_boxes found, elapsed : {}".format(elapse))
            return None, None
        
        # 2. 박스 정렬 및 병합
        dt_boxes = sorted_boxes(dt_boxes)
        
        if self.enable_merge_det_boxes:
            dt_boxes = merge_det_boxes(dt_boxes)
        
        if mfd_res:
            dt_boxes = update_det_boxes(dt_boxes, mfd_res)
        
        # Draw bboxes on image if debug enabled
        if self.save_debug_images:
            img_with_boxes = ori_im.copy()
            for box in dt_boxes:
                box = np.array(box).astype(np.int32).reshape((-1, 1, 2))
                cv2.polylines(img_with_boxes, [box], True, (0, 255, 0), 2)
            det_bbox_path = f"{self.debug_save_dir}/det_input/det_bbox_{self.debug_counter:06d}.jpg"
            cv2.imwrite(det_bbox_path, img_with_boxes)
            logger.debug(f"Saved detection bbox: {det_bbox_path}")
        
        # 3. 텍스트 영역 크롭
        img_crop_list = []
        for bno in range(len(dt_boxes)):
            tmp_box = copy.deepcopy(dt_boxes[bno])
            img_crop = get_rotate_crop_image(ori_im, tmp_box)
            img_crop_list.append(img_crop)
            
            # Save cropped image if debug enabled
            if self.save_debug_images:
                crop_path = f"{self.debug_save_dir}/det_crops/crop_{self.debug_counter:06d}_{bno:03d}.jpg"
                cv2.imwrite(crop_path, img_crop)
        
        # 4. 텍스트 인식 (multi-model 또는 single model)
        if self.use_multi_rec_model:
            rec_res = self._multi_model_recognition(img_crop_list)
        else:
            rec_result = self.text_recognizer(img_crop_list)
            rec_res = list(zip(rec_result.txts, rec_result.scores))
        
        # 5. 필터링
        filter_boxes, filter_rec_res = [], []
        for box, rec_result in zip(dt_boxes, rec_res):
            text, score = rec_result
            if score >= self.drop_score:
                filter_boxes.append(box)
                filter_rec_res.append(rec_result)
        
        # Increment debug counter after processing
        if self.save_debug_images:
            self.debug_counter += 1
        
        return filter_boxes, filter_rec_res
    
    def _multi_model_recognition(self, img_crop_list):
        """
        Multi-model recognition with automatic rotation for vertical text
        """
        rec_results = []
        
        for crop_img in img_crop_list:
            h, w = crop_img.shape[:2]
            
            if h > w * 1.5:
                crop_img = cv2.rotate(crop_img, cv2.ROTATE_90_CLOCKWISE)
                h, w = crop_img.shape[:2]
            
            # Route to appropriate model
            ratio = self.rec_router(w, h)
            
            # Get recognizer for this ratio
            if ratio in self.rec_recognizer_map:
                recognizer = self.rec_recognizer_map[ratio]
                
                # Use dedicated recognizer (already configured with correct size)
                rec_result = recognizer([crop_img])
                
                if rec_result.txts and len(rec_result.txts) > 0:
                    text, score = rec_result.txts[0], rec_result.scores[0]
                    rec_results.append((text, score))
                else:
                    rec_results.append(("", 0.0))
            else:
                # Fallback to default recognizer
                rec_result = self.text_recognizer([crop_img])
                if rec_result.txts and len(rec_result.txts) > 0:
                    rec_results.append((rec_result.txts[0], rec_result.scores[0]))
                else:
                    rec_results.append(("", 0.0))
        
        return rec_results


if __name__ == "__main__":
    # 테스트 코드
    logger.info("DX OCR 모델 테스트")
    
    # 모델 초기화
    ocr_model = DxOcrModel(
        det_model_path="path/to/det_model.dxnn",
        rec_model_path="path/to/rec_model.dxnn",
    )
    
    # 이미지 로드 및 OCR 실행
    # img = cv2.imread("test_image.png")
    # result = ocr_model.ocr(img, det=True, rec=True)
    # print(result)
