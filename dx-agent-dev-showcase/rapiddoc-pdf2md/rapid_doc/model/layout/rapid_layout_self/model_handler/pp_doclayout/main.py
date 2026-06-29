import time
import threading
from typing import List, Union, Optional, Callable

import numpy as np
from loguru import logger

from ...inference_engine.base import InferSession
from ...utils.typings import RapidLayoutOutput
from ..base import BaseModelHandler
from .post_process import PPPostProcess
from .pre_process import PPPreProcess
from ..utils import ModelType
from ...utils.typings import EngineType

class PPDocLayoutModelHandler(BaseModelHandler):
    def __init__(self, labels, conf_thres: Union[float, dict], iou_thres, session: InferSession, model_type: ModelType, engine_type: EngineType):
        if model_type == ModelType.PP_DOCLAYOUT_PLUS_L:
            target_size = (800, 800)
        elif model_type == ModelType.PP_DOCLAYOUT_S:
            target_size = (480, 480)
        else:
            # PP_DOCLAYOUT_L、PP_DOCLAYOUT_M、RT_DETR_L_WIRED_TABLE_CELL_DET、RT_DETR_L_WIRELESS_TABLE_CELL_DET
            target_size = (640, 640)
        self.img_size = target_size

        if engine_type == EngineType.DXENGINE:
            labels = [
                "paragraph_title", "image", "text", "number", "abstract", "content",
                "figure_title", "formula", "table", "table_title", "reference",
                "doc_title", "footnote", "header", "algorithm", "footer", "seal",
                "chart_title", "chart", "formula_number", "header_image",
                "footer_image", "aside_text"
            ]
            conf_thres = {
                0: 0.3,    # paragraph_title
                1: 0.5,    # image
                2: 0.4,    # text
                3: 0.5,    # number
                4: 0.5,    # abstract
                5: 0.5,    # content
                6: 0.5,    # figure_title
                7: 0.3,    # formula         
                8: 0.5,    # table
                9: 0.5,    # table_title
                10: 0.5,   # reference
                11: 0.5,   # doc_title
                12: 0.5,   # footnote
                13: 0.5,   # header
                14: 0.5,   # algorithm
                15: 0.5,   # footer
                16: 0.45,  # seal             
                17: 0.5,   # chart_title
                18: 0.5,   # chart
                19: 0.5,   # formula_number
                20: 0.5,   # header_image
                21: 0.5,   # footer_image
                22: 0.5    # aside_text
            }
        self.pp_preprocess = PPPreProcess(img_size=self.img_size, model_type=model_type, engine_type=engine_type)
        self.pp_postprocess = PPPostProcess(labels, conf_thres, iou_thres)

        self.session = session
        self.engine_type = engine_type
        self.model_type = model_type

    def __call__(self, ori_img_list: List[np.ndarray]) -> List[RapidLayoutOutput]:
        """
        Process image list and return layout analysis results.
        Always use sync processing (callback-based async causes segfault in DX Engine worker threads)
        """
        return self._process_sync(ori_img_list)
    
    def _process_sync(self, ori_img_list: List[np.ndarray]) -> List[RapidLayoutOutput]:
        """동기 방식 배치 처리 (기존 방식)"""
        s1 = time.perf_counter()
        # 1、前置处理
        img_inputs = []
        scale_factor_inputs = []
        for ori_img in ori_img_list:
            ori_img_shape = ori_img.shape[:2]
            img = self.preprocess(ori_img)
            scale_factor = [  # [w_scale, h_scale]
                self.img_size[0] / ori_img_shape[0],
                self.img_size[1] / ori_img_shape[1],
            ]
            img_inputs.append(img)
            scale_factor_inputs.append(scale_factor)
        img_inputs = np.concatenate(img_inputs, axis=0) # 拼接 batch
        scale_factor_inputs = np.array(scale_factor_inputs, np.float32)
        # 2、推理
        batch_preds = self.session(img_inputs, scale_factor_inputs)
        # 3、后处理
        batch_outputs = self._format_output(batch_preds)
        result_list = []
        for i, output in enumerate(batch_outputs):
            ori_img_shape = ori_img_list[i].shape[:2]
            datas = self.pp_postprocess(output["boxes"],[ori_img_shape[1], ori_img_shape[0]])
            if datas:
                boxes, scores, class_names = zip(*[(d["coordinate"], d["score"], d["label"]) for d in datas])
            else:
                boxes, scores, class_names = [], [], []
            elapse = time.perf_counter() - s1
            result = RapidLayoutOutput(img=ori_img_list[i], boxes=boxes,
                                       class_names=class_names, scores=scores, elapse=elapse)
            result_list.append(result)
        return result_list
    
    def _process_async(self, ori_img_list: List[np.ndarray]) -> List[RapidLayoutOutput]:
        """비동기 방식 페이지별 병렬 처리 (DX Engine 전용)"""
        start_time = time.perf_counter()
        num_pages = len(ori_img_list)
        
        # 이미지 리스트를 로컬 복사하여 클로저 문제 방지
        local_img_list = list(ori_img_list)
        
        # 결과 저장소
        results = [None] * num_pages
        lock = threading.Lock()
        pending_count = num_pages
        cv = threading.Condition(lock)
        page_start_times = {}  # 페이지별 시작 시간
        
        def on_complete(page_idx: int, page_start: float, ori_img: np.ndarray, total_pages: int, outputs, unique_id=None):
            """단일 페이지 추론 완료 콜백 - outputs는 run_async가 전달"""
            nonlocal pending_count
            try:
                
                if page_idx >= total_pages:
                    raise IndexError(f"page_idx {page_idx} out of range for {total_pages} pages")
                
                # 후처리
                ori_img_shape = ori_img.shape[:2]
                
                # outputs는 ONNX 후처리까지 완료된 결과
                batch_outputs = self._format_output(outputs)
                if batch_outputs:
                    output = batch_outputs[0]  # 단일 페이지
                    datas = self.pp_postprocess(output["boxes"], [ori_img_shape[1], ori_img_shape[0]])
                    if datas:
                        boxes, scores, class_names = zip(*[(d["coordinate"], d["score"], d["label"]) for d in datas])
                    else:
                        boxes, scores, class_names = [], [], []
                else:
                    boxes, scores, class_names = [], [], []
                
                elapse = time.perf_counter() - page_start
                result = RapidLayoutOutput(
                    img=ori_img, 
                    boxes=boxes,
                    class_names=class_names, 
                    scores=scores, 
                    elapse=elapse
                )
                
                with lock:
                    results[page_idx] = result
                    pending_count -= 1
                    cv.notify()
                    
            except Exception as e:
                logger.warning(f"Layout async callback error for page {page_idx}: {e}", exc_info=True)
                with lock:
                    # 에러 발생 시에도 더미 결과 저장
                    results[page_idx] = RapidLayoutOutput(
                        img=ori_img,
                        boxes=[], class_names=[], scores=[],
                        elapse=time.perf_counter() - page_start
                    )
                    pending_count -= 1
                    cv.notify()
        
        def create_callback(page_idx: int, page_start: float, ori_img: np.ndarray, total_pages: int):
            """각 페이지별 콜백 래퍼 생성 - 클로저 안전하게 캡처"""
            def callback_wrapper(outputs, unique_id=None):
                return on_complete(page_idx, page_start, ori_img, total_pages, outputs, unique_id)
            return callback_wrapper
        
        # 모든 페이지를 비동기로 제출
        request_ids = []
        
        for idx, ori_img in enumerate(local_img_list):
            page_start = time.perf_counter()
            page_start_times[idx] = page_start
            # 전처리
            ori_img_shape = ori_img.shape[:2]
            img = self.preprocess(ori_img)
            scale_factor = np.array([
                [self.img_size[0] / ori_img_shape[0],
                 self.img_size[1] / ori_img_shape[1]]
            ], dtype=np.float32)
            # 래퍼 함수로 콜백 생성 - 각 페이지의 인자를 안전하게 캡처
            cb = create_callback(idx, page_start, ori_img, num_pages)
            request_id = self.session.run_async(
                img,
                scale_factor,
                callback=cb
            )
            request_ids.append(request_id)
        
        # 모든 결과가 완료될 때까지 대기
        with cv:
            while pending_count > 0:
                cv.wait()
        
        total_time = time.perf_counter() - start_time
        # print(f"Layout async processing: {num_pages} pages in {total_time:.3f}s ({total_time/num_pages:.3f}s/page)")
        
        return results

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        return self.pp_preprocess(image)

    def postprocess(self, ori_img_shape, img, preds):
        return self.pp_postprocess(ori_img_shape, img, preds)

    def _format_output(self, pred):
        """
        Transform batch outputs into a list of single image output.

        Args:
            pred (Sequence[Any]): The input predictions, which can be either a list of 3 or 4 elements.
                - When len(pred) == 4, it is expected to be in the format [boxes, class_ids, scores, masks],
                  compatible with SOLOv2 output.
                - When len(pred) == 3, it is expected to be in the format [boxes, box_nums, masks],
                  compatible with Instance Segmentation output.

        Returns:
            List[dict]: A list of dictionaries, each containing either 'class_id' and 'masks' (for SOLOv2),
                or 'boxes' and 'masks' (for Instance Segmentation), or just 'boxes' if no masks are provided.
        """
        box_idx_start = 0
        pred_box = []

        if len(pred) == 4:
            # Adapt to SOLOv2
            pred_class_id = []
            pred_mask = []
            pred_class_id.append([pred[1], pred[2]])
            pred_mask.append(pred[3])
            return [
                {
                    "class_id": np.array(pred_class_id[i]),
                    "masks": np.array(pred_mask[i]),
                }
                for i in range(len(pred_class_id))
            ]

        if len(pred) == 3:
            # Adapt to Instance Segmentation
            pred_mask = []
        for idx in range(len(pred[1])):
            np_boxes_num = pred[1][idx]
            box_idx_end = box_idx_start + np_boxes_num
            np_boxes = pred[0][box_idx_start:box_idx_end]
            pred_box.append(np_boxes)
            if len(pred) == 3:
                np_masks = pred[2][box_idx_start:box_idx_end]
                pred_mask.append(np_masks)
            box_idx_start = box_idx_end

        if len(pred) == 3:
            return [
                {"boxes": np.array(pred_box[i]), "masks": np.array(pred_mask[i])}
                for i in range(len(pred_box))
            ]
        else:
            return [{"boxes": np.array(res)} for res in pred_box]
