import os
import sys
import time
import queue
import threading
from concurrent.futures import ThreadPoolExecutor

from dx_engine import InferenceEngine as IE

from .utils import get_rotate_crop_image, filter_tag_det_res
from .utils import det_router, rec_router, split_bbox_for_recognition, merge_recognition_results
from .utils import convert_boxes_to_quad_format, sorted_boxes, rotate_if_vertical

from typing import List, Tuple, Dict, Optional, Any, cast
import numpy as np
import cv2
import json
from datetime import datetime

engine_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(engine_path)

from baidu import det_preprocess, cls_preprocess, rec_preprocess, doc_ori_preprocess, uvdoc_preprocess, resize_align_corners
from models.ocr_postprocess import DetPostProcess, ClsPostProcess, RecLabelDecode, DocOriPostProcess
from preprocessing import PreProcessingCompose

class Node():
    """
    Base node class for OCR pipeline
    Base class for each processing stage (Detection, Classification, Recognition)
    """
    def prepare_input(self, inp: np.ndarray) -> np.ndarray:
        """
        Prepare input tensor for DXNN model
        NCHW -> NHWC conversion and ensure memory contiguity
        
        Args:
            inp: Input array (numpy array)
            
        Returns:
            Input array prepared for DXNN model
        """
        if inp.ndim == 3:
            inp = np.expand_dims(inp, 0)
        if inp.ndim == 4:
            inp = np.transpose(inp, (0, 2, 3, 1))
        return np.ascontiguousarray(inp)
    
    def thread_postprocess(self):
        return 0


class DetectionNode(Node):
    """
    Text Region Detection Node (PP-OCRv5 Detection)
    - Multi-resolution model support (640x640, 960x960)
    - Automatic model selection based on image size
    - DBNet-based text detection
    """
    def __init__(self, models:dict, det_db_thresh: float = 0.3, det_db_box_thresh: float = 0.6, det_db_unclip_ratio: float = 1.5):
        """
        Args:
            models: {resolution: IE_model} dictionary (e.g., {640: model_640, 960: model_960})
            det_db_thresh: Detection threshold
            det_db_box_thresh: Detection box threshold
            det_db_unclip_ratio: Detection unclip ratio
        """
        super().__init__()
        self.det_model_map: dict = models

        self.det_preprocess_map = {}
        for res in [640, 960]:
            res_det_preprocess = det_preprocess.copy()
            res_det_preprocess[0]['resize']['size'] = [res, res]
            self.det_preprocess_map[res] = PreProcessingCompose(res_det_preprocess)

        self.det_postprocess = DetPostProcess(
            thresh=det_db_thresh,
            box_thresh=det_db_box_thresh,
            max_candidates=1500,
            unclip_ratio=det_db_unclip_ratio,
            use_dilation=False,
            score_mode="fast",
            box_type="quad",
        )

        self.router = det_router
        self.counter = 0
    
    def __call__(self, img):
        """
        Perform text region detection on image
        
        Args:
            img: Input image (numpy array)
            
        Returns:
            tuple: (detected_boxes, execution_count)
        """
        engine_latency = 0
        h, w = img.shape[:2]
        mapped_res = self.router(w, h)
        res_preprocess = self.det_preprocess_map[mapped_res]
        res_model = self.det_model_map[mapped_res]

        input = res_preprocess(img)
        padding_info = res_preprocess.get_last_padding_info()
        input = self.prepare_input(input)
        start_time = time.time()
        output = res_model.run([input])
        engine_latency += time.time() - start_time
        det_output = self.postprocess(output[0], img.shape, padding_info)
        
        self.counter += 1
        
        return det_output, self.counter, engine_latency
    
    def postprocess(self, outputs, image_shape, padding_info=None):
        dt_boxes = self.det_postprocess(outputs, image_shape, padding_info)
        dt_boxes = dt_boxes[0]["points"]
        dt_boxes = filter_tag_det_res(dt_boxes, image_shape)
        return dt_boxes
    
    def draw_detection_boxes(self, image, dt_boxes, save_path=None):
        """Draw detection boxes on image and optionally save it.
        
        Args:
            image: Original image (numpy array)
            dt_boxes: Detection boxes from postprocess
            save_path: Path to save the image with boxes (optional)
            
        Returns:
            Image with drawn boxes
        """
        import os
        
        if len(dt_boxes) == 0:
            if save_path:
                cv2.imwrite(save_path, image)
            return image
            
        draw_img = image.copy()
        
        for box in dt_boxes:
            box = np.array(box).astype(np.int32)
            
            cv2.polylines(draw_img, [box], True, color=(0, 255, 0), thickness=2)
            
            for point in box:
                cv2.circle(draw_img, tuple(point), 3, (255, 0, 0), -1)
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            cv2.imwrite(save_path, draw_img)
            print(f"Detection result saved: {save_path}")
            
        return draw_img

class ClassificationNode(Node):
    """
    Text Orientation Classification Node (PP-OCRv5 Classification)
    - Determine if text image is rotated 180 degrees
    - Align detected text regions to correct orientation
    """
    def __init__(self, model:IE):
        """
        Args:
            model: Text orientation classification model (DXNN IE)
        """
        super().__init__()
        self.model = model
        self.cls_preprocess = PreProcessingCompose(cls_preprocess)
        self.cls_postprocess = ClsPostProcess()
        self.debug_counter = 0
    
    def __call__(self, det_outputs:List[np.ndarray]):
        """
        Perform orientation classification on detected text images
        
        Args:
            det_outputs: List of detected text images
            
        Returns:
            tuple: (classification_results_list, execution_count)
                classification_results: [[label, confidence], ...] format
        """
        outputs = []
        engine_latency = 0
        for det_output in det_outputs:
            cls_input = self.cls_preprocess(det_output)
            cls_input = self.prepare_input(cls_input)
            start_time = time.time()
            output = self.model.run([cls_input])
            engine_latency += time.time() - start_time
            label, score = self.cls_postprocess(output[0])[0]
            self.debug_counter += 1
            outputs.append([label, score])
        return outputs, self.debug_counter, engine_latency

    def save_sample_image(self, image, score):
        filename = f"sample_{self.debug_counter:06d}_{score}.jpg"
        save_path = os.path.join(self.debug_dir, filename)
        
        cv2.imwrite(save_path, image)
        self.debug_counter += 1


class RecognitionNode(Node):
    """
    Text Recognition Node (PP-OCRv5 Recognition)
    - Multi-model support for various aspect ratios of text images
    - Automatic model selection by ratio: ratio_3, ratio_5, ratio_10, ratio_15, ratio_25, ratio_35
    - CRNN-based text recognition
    """
    def __init__(self, models:dict, dict_dir:str, rec_score_thresh: float = 0.0):
        """
        Args:
            models: {ratio_key: IE_model} dictionary
            rec_score_thresh: Recognition score threshold for filtering results
        """
        super().__init__()
        self.rec_model_map: dict = models
        
        self.rec_preprocess_map = {}

        ratio_rec_preprocess = rec_preprocess.copy()
        ratio_rec_preprocess[0]['resize']['size'] = [48, 120]
        self.rec_preprocess_map[3] = PreProcessingCompose(ratio_rec_preprocess)
        for i in [5, 10, 15, 25, 35]:
            ratio_rec_preprocess[0]['resize']['size'] = [48, 48 * i]
            self.rec_preprocess_map[i] = PreProcessingCompose(ratio_rec_preprocess)
        character_dict_path = dict_dir
        
        self.rec_postprocess = RecLabelDecode(character_dict_path=character_dict_path, use_space_char=True)
        self.router = rec_router
        self.overlap_ratio = 0.1
        self.drop = rec_score_thresh
        self.debug_counter = 0

    def split_bbox_for_recognition(self, bbox, rec_image_shape, overlap_ratio=0.1):
        return split_bbox_for_recognition(bbox, rec_image_shape, overlap_ratio)
    
    def merge_recognition_results(self, split_results, overlap_ratio=0.1):
        return merge_recognition_results(split_results, overlap_ratio)
    
    def classify_ratio(self, width, height):
        """Classify image by W/H ratio into buckets: ≤3, ≤5, ≤15, >15"""
        ratio = width / height if height > 0 else float('inf')
        
        if ratio <= 4:
            return "ratio_3"
        elif ratio <= 10:
            return "ratio_5"
        elif ratio <= 12.5:
            return "ratio_10"
        elif ratio <= 25:
            return "ratio_15"
        else:
            return "ratio_25"
    
    def classify_height(self, height):
        """Classify image by height: 20 or >20"""
        if height <= 10:
            return "width_20"
        else:
            return "width_40"
        
    def __call__(self, original_image, boxes:List, crops:List[np.ndarray]):
        outputs = []
        engine_latency = 0
        min_latency = 10000000
        for i in range(len(crops)):
            cropped_img = crops[i]
            # Model selection based on image ratio
            mapped_ratio = self.router(cropped_img.shape[1], cropped_img.shape[0])
            ratio_preprocess = self.rec_preprocess_map[mapped_ratio]
            ratio_model = self.rec_model_map[mapped_ratio]

            inp = ratio_preprocess(cropped_img)
            rec_input = self.prepare_input(inp)

            start_time = time.time()
            output = ratio_model.run([rec_input])
            end_time = time.time()

            if min_latency > end_time - start_time:
                min_latency = end_time - start_time
            res = self.rec_postprocess(output[0])[0]
            engine_latency += end_time - start_time
            self.debug_counter += 1
            
            if res[1] > self.drop:
                outputs.append({
                    'bbox_index': i,
                    'bbox': boxes[i],
                    'text': res[0],
                    'score': res[1]
                })
        return outputs, self.debug_counter, engine_latency, min_latency


class DocumentOrientationNode(Node):
    """
    Document Orientation Correction Node (Document Orientation)
    - Detect document image rotation angle (0°, 90°, 180°, 270°)
    - First stage of PP-OCRv5 Document Preprocessing pipeline
    """
    def __init__(self, model: IE):
        """
        Args:
            model: Document orientation classification model (DXNN IE)
        """
        self.model = model
        self.preprocess = PreProcessingCompose(doc_ori_preprocess)
        self.doc_postprocess = DocOriPostProcess(label_list=['0', '90', '180', '270'])

    def __call__(self, image: np.ndarray) -> Tuple[List[Tuple[int, np.ndarray]], float]:
        """
        Analyze document image orientation and rotate to correct direction
        
        Args:
            image: Input document image
            
        Returns:
            tuple: ((rotation_angle, rotated_image), processing_time)
        """
        engine_latency = 0
        
        preprocessed = self.preprocess(image)
        preprocessed = self.prepare_input(preprocessed)
        # preprocessed = self.prepare_input_onnx(preprocessed)
        start_time = time.time()
        
        # DXNN inference (주석 처리)
        output = self.model.run([preprocessed])[0]
        
        # ONNX inference
        # onnx_outputs = self.onnx_session.run(self.output_names, {self.input_name: preprocessed})
        # output = onnx_outputs[0]
        
        engine_latency += time.time() - start_time
        
        angle, rotated_image = self.postprocess(output, image)
        return (angle, rotated_image), engine_latency

    def postprocess(self, output: np.ndarray, original_image: np.ndarray) -> Tuple[int, np.ndarray]:
        doc_ori_results = self.doc_postprocess(output)[0]  # [(label, score), ...]
        label, score = doc_ori_results
        rotated_image = self.rotate_image(original_image, label)
        
        return label, rotated_image
    
    def rotate_image(self, image: np.ndarray, angle: int) -> np.ndarray:
        """Rotate image by given angle"""
        if str(angle) == "0":
            return image
        elif str(angle) == "90":
            return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif str(angle) == "180":
            return cv2.rotate(image, cv2.ROTATE_180)
        elif str(angle) == "270":
            return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        else:
            return image


class DocumentUnwarpingNode(Node):
    """
    Document Unwarping Correction Node (Document Unwarping - UVDoc)
    - Correct warped document images to flat form
    - Second stage of PP-OCRv5 Document Preprocessing pipeline
    - Uses UVDoc algorithm
    """
    def __init__(self, model: IE):
        """
        Args:
            model: Document unwarping correction model (UVDoc DXNN IE)
        """
        self.model = model
        self.preprocess = PreProcessingCompose(uvdoc_preprocess)
        self.target_size = (712, 488)
        self.origin_shape = None
    
    def __call__(self, image: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Correct document image distortion to transform into flat form
        
        Args:
            image: Input document image
            
        Returns:
            tuple: (corrected_image, processing_time)
        """
        engine_latency = 0
        preprocessed = self.preprocess(image)
        preprocessed = self.prepare_input(preprocessed)

        start_time = time.time()
        output = self.model.run([preprocessed])[0]
        
        engine_latency += time.time() - start_time
        unwarped_image = self.postprocess(output, image)
        return unwarped_image, engine_latency

    def postprocess(self, uv_map: np.ndarray, original_image: np.ndarray) -> np.ndarray:
        """Post-processing: Image distortion correction using UV map"""
        orig_h, orig_w = original_image.shape[:2]
        
        if uv_map.ndim == 4:
            uv_map = uv_map.squeeze(0)
        
        # Resize UV map to original image size (vectorized operation)
        uv_resized = np.empty((2, orig_h, orig_w), dtype=np.float32)
        uv_resized[0] = cv2.resize(uv_map[0], (orig_w, orig_h), interpolation=cv2.INTER_LINEAR)
        uv_resized[1] = cv2.resize(uv_map[1], (orig_w, orig_h), interpolation=cv2.INTER_LINEAR)

        return self.gridsample_numpy(original_image, uv_resized, align_corners=True)
    def gridsample_numpy(self, input_image: np.ndarray, uv_map: np.ndarray, align_corners: bool = True) -> np.ndarray:
        """CPU-optimized grid sampling using OpenCV remap"""
        h, w = input_image.shape[:2]
        
        if align_corners:
            map_x = (uv_map[0] + 1.0) * ((w - 1) * 0.5)
            map_y = (uv_map[1] + 1.0) * ((h - 1) * 0.5)
        else:
            map_x = ((uv_map[0] + 1.0) * w - 1.0) * 0.5
            map_y = ((uv_map[1] + 1.0) * h - 1.0) * 0.5
        
        return cv2.remap(
            input_image,
            map_x.astype(np.float32),
            map_y.astype(np.float32),
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=0
        )

class DocumentPreprocessingPipeline:
    """
    PP-OCRv5 Style Document Preprocessing Pipeline
    - Stage 1: Document Orientation (document orientation correction)
    - Stage 2: Document Unwarping (document distortion correction)
    - Preprocessing pipeline for improving OCR accuracy
    """
    def __init__(self, 
                 orientation_model: Optional[IE] = None,
                 unwarping_model: Optional[IE] = None,
                 use_doc_orientation: bool = True,
                 use_doc_unwarping: bool = True):
        """
        Args:
            orientation_model: Document orientation correction model
            unwarping_model: Document distortion correction model  
            use_doc_orientation: Whether to use orientation correction
            use_doc_unwarping: Whether to use distortion correction
        """
        self.use_doc_orientation = use_doc_orientation and orientation_model is not None
        self.use_doc_unwarping = use_doc_unwarping and unwarping_model is not None

        self.orientation_node = DocumentOrientationNode(orientation_model) if orientation_model else None
        self.unwarping_node = DocumentUnwarpingNode(unwarping_model) if unwarping_model else None
        
        # Store last call's individual latencies for performance reporting
        self.last_ori_latency = 0.0
        self.last_uv_latency = 0.0

    def __call__(self, image: np.ndarray) -> Tuple[List[Dict], float]:
        """
        Execute document preprocessing pipeline
        
        Args:
            image: Input document image
            
        Returns:
            tuple: (processed_image, total_processing_time)
        """
        total_latency = 0
        current_image = image.copy()
        
        # Reset individual latencies
        self.last_ori_latency = 0.0
        self.last_uv_latency = 0.0
        
        if self.use_doc_orientation and self.orientation_node is not None:
            orientation_results, orientation_latency = self.orientation_node(current_image)
            total_latency += orientation_latency
            self.last_ori_latency = orientation_latency
            _, rotated_image = orientation_results
            current_image = rotated_image

        if self.use_doc_unwarping and self.unwarping_node is not None:
            current_image, unwarping_latency = self.unwarping_node(current_image)
            total_latency += unwarping_latency
            self.last_uv_latency = unwarping_latency
            
        return current_image, total_latency
    

class PaddleOcr():
    def __init__(self, 
                 det_model, 
                 cls_model: IE, 
                 rec_models: dict, 
                 rec_dict_dir: str,
                 doc_ori_model: Optional[IE],
                 doc_unwarping_model: Optional[IE] = None,
                 use_doc_preprocessing: bool = False,
                 use_doc_orientation: bool = True,
                 use_textline_orientation: bool = True,
                 det_db_thresh: float = 0.3,
                 det_db_box_thresh: float = 0.6,
                 det_db_unclip_ratio: float = 1.5,
                 rec_score_thresh: float = 0.0):
        '''
        @brief: PP-OCRv5 style OCR engine (including Document Preprocessing)
        @param:
            det_model: DeepX detection model (single IE or dict of {resolution: IE})
            cls_model: DeepX classification model (cls.dxnn) - textline orientation
            rec_models: DeepX recognition models dict
            doc_unwarping_model: Document distortion correction model (UVDoc)
            use_doc_preprocessing: Whether to use document preprocessing (unwarping)
            use_doc_orientation: Whether to use document orientation correction (doc_ori)
            use_textline_orientation: Whether to use textline orientation classification
            det_db_thresh: Detection threshold (for future use)
            det_db_box_thresh: Detection box threshold (for future use)
            det_db_unclip_ratio: Detection unclip ratio (for future use)
            rec_score_thresh: Recognition score threshold (for future use)
        @return:
            None
        '''
        # Support both single model and dict of models
        if isinstance(det_model, dict):
            self.det_models = det_model
        else:
            # Wrap single model in dict for compatibility
            self.det_models = {640: det_model}
        
        self.cls_model = cls_model
        self.rec_models: dict = rec_models
        self.use_doc_preprocessing = use_doc_preprocessing
        self.use_textline_orientation = use_textline_orientation
        
        # Store detection and recognition parameters (for future use)
        self.det_db_thresh = det_db_thresh
        self.det_db_box_thresh = det_db_box_thresh
        self.det_db_unclip_ratio = det_db_unclip_ratio
        self.rec_score_thresh = rec_score_thresh
        
        self.detection_node = DetectionNode(
            self.det_models,
            det_db_thresh=det_db_thresh,
            det_db_box_thresh=det_db_box_thresh,
            det_db_unclip_ratio=det_db_unclip_ratio
        )
        self.classification_node = ClassificationNode(self.cls_model)
        self.recognition_node = RecognitionNode(
            self.rec_models,
            dict_dir=rec_dict_dir,
            rec_score_thresh=rec_score_thresh
        )
                                              
        # Document Preprocessing pipeline (PP-OCRv5 architecture: det + rec + doc_ori + UVDoc)
        if use_doc_orientation or use_doc_preprocessing:
            self.doc_preprocessing = DocumentPreprocessingPipeline(
                orientation_model=doc_ori_model,
                unwarping_model=doc_unwarping_model,
                use_doc_orientation=use_doc_orientation,
                use_doc_unwarping=use_doc_preprocessing  # use_doc_preprocessing controls unwarping
            )
        else:
            self.doc_preprocessing = None
            
        self.cls_thresh = 0.9

        self.detection_time_duration = 0
        self.classification_time_duration = 0
        self.recognition_time_duration = 0
        self.min_recognition_time_duration = 0

        # Data collection setup
        self.data_collection_enabled = False
        self.skip_recognition_for_dataset = False
        self.sample_counter = 0
        self.base_sample_dir = "sampled_dataset/"
        self.doc_preprocessing_time_duration = 0
        self.ocr_run_count = 0
        self.ori_run_count = 0
        self.crops_run_count = 0

    def __call__(self, img, debug_output_path=None):
        """
        Execute PP-OCRv5 style OCR pipeline
        
        Processing order:
        1. Document Preprocessing (orientation correction + distortion correction) - same as PP-OCRv5
        2. Text Detection (text region detection)
        3. Text Classification (text orientation classification)
        4. Text Recognition (text content recognition)
        
        Args:
            img: Input image (numpy array)
            debug_output_path: Debug information save path (optional)
            
        Returns:
            tuple: (box_coordinates, cropped_images, recognition_results, preprocessed_image, debug_data)
        """
        
        debug_data = {
            'mode': 'sync',
            'timestamp': datetime.now().isoformat(),
            'detection': {},
            'classification': {},
            'recognition': {},
            'latency_ms': {
                'doc_ori': 0.0,
                'doc_uv': 0.0,
                'det': 0.0,
                'cls': 0.0,
                'rec': 0.0,
                'total': 0.0
            }
        }
        
        import time
        pipeline_start = time.time()
        
        processed_img = img
        doc_ori_latency = 0.0
        doc_uv_latency = 0.0
        det_latency = 0.0
        cls_latency = 0.0
        rec_latency = 0.0
        
        # 1. Document Preprocessing (PP-OCRv5와 동일한 로직)
        # Check use_doc_preprocessing flag instead of just doc_preprocessing existence
        if self.use_doc_preprocessing and self.doc_preprocessing is not None:
            processed_img, preprocessing_latency = self.doc_preprocessing(img)
            self.doc_preprocessing_time_duration += preprocessing_latency * 1000
            # Document preprocessing includes both orientation and unwarping
            # Get individual latencies if available
            if hasattr(self.doc_preprocessing, 'last_ori_latency'):
                doc_ori_latency = self.doc_preprocessing.last_ori_latency * 1000
            if hasattr(self.doc_preprocessing, 'last_uv_latency'):
                doc_uv_latency = self.doc_preprocessing.last_uv_latency * 1000
            # Fallback: if individual latencies not available, use total
            if doc_ori_latency == 0.0 and doc_uv_latency == 0.0:
                # Split by whether each is enabled
                if self.doc_preprocessing.use_doc_orientation and self.doc_preprocessing.use_doc_unwarping:
                    doc_ori_latency = preprocessing_latency * 500  # Half each
                    doc_uv_latency = preprocessing_latency * 500
                elif self.doc_preprocessing.use_doc_orientation:
                    doc_ori_latency = preprocessing_latency * 1000
                elif self.doc_preprocessing.use_doc_unwarping:
                    doc_uv_latency = preprocessing_latency * 1000
        
        # 2. Text Detection (전처리된 이미지에서 수행)
        det_outputs, _, engine_latency = self.detection_node(processed_img)
        det_latency = engine_latency * 1000
        boxes = sorted_boxes(det_outputs)

        self.detection_time_duration += engine_latency * 1000

        # Convert boxes to (n, 4, 2) format if needed
        boxes = convert_boxes_to_quad_format(boxes)
        
        # Save detection results
        debug_data['detection']['count'] = len(boxes)
        debug_data['detection']['boxes'] = [box.tolist() for box in boxes]
        
        crops = [rotate_if_vertical(get_rotate_crop_image(processed_img, box)) for box in boxes]
        
        if self.data_collection_enabled:
            for crop in crops:
                h, w = crop.shape[:2]
                self.save_sample_image(crop, w, h)
        
        # If we're collecting dataset and skipping recognition, return early
        if self.data_collection_enabled and self.skip_recognition_for_dataset:
            self.ocr_run_count += 1
            return [box.tolist() for box in boxes], crops, [], processed_img
        
        boxes = [box.tolist() for box in boxes]
        
        # 3. Text Classification (textline orientation) - conditional based on use_textline_orientation
        debug_data['classification']['results'] = []
        if self.use_textline_orientation:
            cls_results, _, engine_latency = self.classification_node(crops)
            cls_latency = engine_latency * 1000
            if crops:
                self.classification_time_duration += engine_latency / len(crops) * 1000
            
            # Save classification results and rotate if needed
            for i, [label, score] in enumerate(cls_results):
                rotated = "180" in label and score > self.cls_thresh
                debug_data['classification']['results'].append({
                    'crop_index': int(i),
                    'label': str(label),
                    'score': float(score),
                    'rotated': bool(rotated)
                })
                if rotated:
                    crops[i] = cv2.rotate(crops[i], cv2.ROTATE_180)
        else:
            # Skip classification - no rotation applied
            debug_data['classification']['skipped'] = True
                
        rec_results, _, engine_latency, min_latency = self.recognition_node(processed_img, boxes, crops)
        rec_latency = engine_latency * 1000
        if crops:
            self.recognition_time_duration += engine_latency / len(crops) * 1000
        self.min_recognition_time_duration += min_latency * 1000
        
        # Save recognition results
        debug_data['recognition']['count'] = len(rec_results)
        debug_data['recognition']['results'] = []
        for result in rec_results:
            debug_data['recognition']['results'].append({
                'bbox_index': result['bbox_index'],
                'text': result['text'],
                'score': float(result['score'])
            })
        
        # Calculate total pipeline latency and store all latencies
        pipeline_end = time.time()
        total_latency = (pipeline_end - pipeline_start) * 1000
        
        debug_data['latency_ms'] = {
            'doc_ori': doc_ori_latency,
            'doc_uv': doc_uv_latency,
            'det': det_latency,
            'cls': cls_latency,
            'rec': rec_latency,
            'total': total_latency
        }
        
        self.ocr_run_count += 1
        return boxes, crops, rec_results, processed_img, debug_data

# ==================== Async Pipeline Implementation ====================

class OCRJob:
    """Tracks the processing state of a single image through the OCR pipeline"""
    def __init__(self, job_id: str, image: np.ndarray, preprocessed_image: Optional[np.ndarray] = None):
        self.job_id = job_id
        self.image = image  # Original image
        self.preprocessed_image = preprocessed_image if preprocessed_image is not None else image  # Doc-preprocessed image
        self.state = 'created'
        self.timestamps: Dict[str, float] = {}
        
        # Detailed profiling
        self.stage_stats = {
            'doc_ori': {'start': 0.0, 'end': 0.0, 'duration': 0.0, 'preprocess': 0.0, 'postprocess': 0.0},
            'doc_uv': {'start': 0.0, 'end': 0.0, 'duration': 0.0, 'preprocess': 0.0, 'postprocess': 0.0},
            'det': {'start': 0.0, 'end': 0.0, 'duration': 0.0, 'preprocess': 0.0, 'postprocess': 0.0},
            'cls': {'start': 0.0, 'end': 0.0, 'duration': 0.0, 'count': 0, 'preprocess': 0.0, 'postprocess': 0.0, 'accumulated_duration': 0.0},
            'rec': {'start': 0.0, 'end': 0.0, 'duration': 0.0, 'count': 0, 'preprocess': 0.0, 'postprocess': 0.0, 'accumulated_duration': 0.0}
        }
        
        # Stage results
        self.det_boxes: Optional[List] = None
        self.crops: Optional[List[np.ndarray]] = None
        self.cls_results: Dict[int, Tuple] = {}  # crop_idx -> (label, score)
        self.rec_results: List[Dict] = []  # List of {'bbox_index', 'bbox', 'text', 'score'}
        self.rec_results_dict: Dict[int, Dict] = {} 
        
        # Per-crop timing tracking
        self.cls_crop_start_times: Dict[int, float] = {}
        self.rec_crop_start_times: Dict[int, float] = {}
        
        # Completion tracking
        self.cls_completed_count: int = 0
        self.rec_completed_count: int = 0
        self.expected_cls_count: int = 0
        self.expected_rec_count: int = 0
        
        self.error: Optional[str] = None
        
        # Buffer caching: Keep preprocessed inputs alive during async operations
        # This prevents Python GC from freeing memory that dx_engine still references
        self.det_input_buffer: Optional[np.ndarray] = None
        self.det_padding_info = None
        self.cls_input_buffers: Dict[int, np.ndarray] = {}  # crop_idx -> preprocessed input
        self.rec_input_buffers: Dict[int, np.ndarray] = {}  # crop_idx -> preprocessed input
        self.doc_ori_input_buffer: Optional[np.ndarray] = None
        self.doc_uv_input_buffer: Optional[np.ndarray] = None
        self.debug_output_dir: Optional[str] = None
        
        # Debug data tracking
        self.debug_data = {
            'mode': 'async',
            'job_id': job_id,
            'timestamp': datetime.now().isoformat(),
            'doc_preprocessing': {
                'orientation': {},
                'unwarping': {}
            },
            'detection': {},
            'classification': {'order': [], 'results': []},
            'recognition': {'order': [], 'results': []},
            'callback_order': []
        }


class AsyncPipelineOCR:
    """Asynchronous OCR pipeline using callbacks"""
    def __init__(self, 
                 det_model,
                 cls_model: IE, 
                 rec_models: dict,
                 rec_dict_dir: str,
                 doc_ori_model: Optional[IE] = None,
                 doc_unwarping_model: Optional[IE] = None,
                 use_doc_preprocessing: bool = False,
                 use_doc_orientation: bool = False,
                 use_textline_orientation: bool = True,
                 det_db_thresh: float = 0.3,
                 det_db_box_thresh: float = 0.6,
                 det_db_unclip_ratio: float = 1.5,
                 rec_score_thresh: float = 0.0,
                 input_interval: float = 0.0,
                 verbose: bool = True):
        """
        Initialize async OCR pipeline
        
        Args:
            det_model: DeepX detection model (single IE or dict of {resolution: IE})
            cls_model: Classification model
            rec_models: Dict of recognition models (ratio -> model)
            doc_ori_model: Document orientation model
            doc_unwarping_model: Document unwarping model
            use_doc_preprocessing: Enable document preprocessing
            use_doc_orientation: Enable document orientation correction
            use_textline_orientation: Enable textline orientation classification
            det_db_thresh: Detection threshold
            det_db_box_thresh: Detection box threshold
            det_db_unclip_ratio: Detection unclip ratio
            rec_score_thresh: Recognition score threshold
        """
        # Support both single model and dict of models (same as PaddleOcr)
        if isinstance(det_model, dict):
            self.det_models = det_model
        else:
            # Wrap single model in dict for compatibility
            self.det_models = {640: det_model}
        
        self.cls_model = cls_model
        self.rec_models = rec_models
        
        # Create nodes with parameters
        self.detection_node = DetectionNode(
            self.det_models,
            det_db_thresh=det_db_thresh,
            det_db_box_thresh=det_db_box_thresh,
            det_db_unclip_ratio=det_db_unclip_ratio
        )
        self.classification_node = ClassificationNode(self.cls_model)
        self.recognition_node = RecognitionNode(
            self.rec_models,
            dict_dir=rec_dict_dir,
            rec_score_thresh=rec_score_thresh
        )
        
        self.ocr_run_count = 0
        self.ori_run_count = 0
        self.crops_run_count = 0
        
        self.detection_time_duration = 0
        self.classification_time_duration = 0
        self.recognition_time_duration = 0
        self.min_recognition_time_duration = 0
        
        # # Document preprocessing (runs synchronously before async pipeline)
        if use_doc_orientation or use_doc_preprocessing:
            print("prepare documenta pre-processing pipeline")
            self.doc_preprocessing = DocumentPreprocessingPipeline(
                orientation_model=doc_ori_model,
                unwarping_model=doc_unwarping_model,
                use_doc_orientation=use_doc_orientation,
                use_doc_unwarping=use_doc_preprocessing
            )
        else:
            self.doc_preprocessing = None
        
        # Document preprocessing configuration for async pipeline
        self.use_doc_preprocessing = use_doc_preprocessing  # Add for dynamic control
        self.use_doc_orientation = bool(use_doc_orientation and doc_ori_model is not None)
        self.use_doc_unwarping = bool(use_doc_preprocessing and doc_unwarping_model is not None)
        self.doc_orientation_node = DocumentOrientationNode(doc_ori_model) if self.use_doc_orientation else None
        self.doc_unwarping_node = DocumentUnwarpingNode(doc_unwarping_model) if self.use_doc_unwarping else None
        
        # Textline orientation configuration (same as PaddleOcr)
        self.use_textline_orientation = use_textline_orientation
        
        # Debug mode
        self.debug = False
        self.show_debug_message = False
        
        # Async management
        self.lock = threading.Lock()
        self.active_jobs: Dict[str, OCRJob] = {}
        self.completed_queue = queue.Queue()
        
        # Configuration
        self.cls_thresh = 0.9
        
        # Statistics
        self.stats = {
            'doc_ori_submitted': 0, 'doc_ori_completed': 0,
            'doc_uv_submitted': 0, 'doc_uv_completed': 0,
            'det_submitted': 0, 'det_completed': 0,
            'cls_submitted': 0, 'cls_completed': 0,
            'rec_submitted': 0, 'rec_completed': 0
        }
        self.verbose = verbose
        self.input_interval = max(0.0, float(input_interval))

        # Performance monitoring
        self.perf_monitor = {
            'queue_sizes': [],
            'job_latencies': []
        }
        self.profiling_data = []
        self.buffer_stats = []

        # Stage dispatcher keeps DXRT callbacks lightweight under tight TASK_MAX_LOAD budgets
        self.stage_executor = ThreadPoolExecutor(max_workers=16)
        
        # Register callbacks
        self._register_callbacks()
        
        # initialize timing
        self.job_detection_start_time = time.time()
        self.job_detection_end_time = time.time()
        self.job_classification_start_time = time.time()
        self.job_classification_end_time = time.time()
        self.job_recognition_start_time = time.time()
        self.job_recognition_end_time = time.time()

    def _log(self, message: str, *, force: bool = False):
        if self.verbose or force:
            print(f"[AsyncPipeline] {message}")

    def _dispatch_stage(self, fn, *args):
        """Run heavy stage submissions outside DXRT callback threads."""
        if not self.stage_executor:
            fn(*args)
            return
        def _wrapper():
            try:
                fn(*args)
            except Exception as exc:
                self._log(f"Error running stage {fn.__name__}: {exc}", force=True)
                import traceback
                traceback.print_exc()
        self.stage_executor.submit(_wrapper)
    
    @staticmethod
    def convert_boxes_to_quad_format(boxes):
        """
        Convert boxes from (n*4, 2) format to (n, 4, 2) format
        @param boxes: numpy array of shape (n*4, 2) or list of boxes where n is number of text boxes
        @return: numpy array of shape (n, 4, 2) where each box has 4 corner points
        """
        # Convert list to numpy array if needed
        if isinstance(boxes, list):
            if len(boxes) == 0:
                return np.array([])
            # Check if each element is already a box (4 points)
            if len(boxes[0]) == 4:
                # Already in correct format, just convert to numpy
                return np.array(boxes)
            else:
                # Flatten the list and convert to numpy
                boxes = np.array(boxes)
        
        if len(boxes.shape) == 2 and boxes.shape[1] == 2:
            # Check if the number of points is divisible by 4
            if boxes.shape[0] % 4 != 0:
                raise ValueError(f"Number of points ({boxes.shape[0]}) must be divisible by 4")
            
            # Reshape to (n, 4, 2) where n = boxes.shape[0] // 4
            num_boxes = boxes.shape[0] // 4
            boxes_reshaped = boxes.reshape(num_boxes, 4, 2)
            return boxes_reshaped
        elif len(boxes.shape) == 3 and boxes.shape[1] == 4 and boxes.shape[2] == 2:
            # Already in correct format
            return boxes
        else:
            raise ValueError(f"Unexpected box format: {boxes.shape}")
    
    @staticmethod
    def sorted_boxes(dt_boxes: np.ndarray) -> List[np.ndarray]:
        boxes = sorted(dt_boxes, key=lambda x: (x[0][1], x[0][0]))
        _boxes = list(boxes)
        for i in range(len(_boxes)-1):
            for j in range(i, -1, -1):
                    if abs(_boxes[j + 1][0][1] - _boxes[j][0][1]) < 10 and (
                        _boxes[j + 1][0][0] < _boxes[j][0][0]
                    ):
                        tmp = _boxes[j]
                        _boxes[j] = _boxes[j + 1]
                        _boxes[j + 1] = tmp
                    else:
                        break
        return _boxes
    
    @staticmethod
    def get_rotate_crop_image(img, points):
        return get_rotate_crop_image(img, points)

    def rotate_if_vertical(self, crop):
        h, w = crop.shape[:2]
        if h > w * 2:
            return cv2.rotate(crop, cv2.ROTATE_90_COUNTERCLOCKWISE)
        return crop

    def _register_callbacks(self):
        """Register callbacks for all models"""
        # Detection callbacks (multiple resolution models)
        for res, model in self.det_models.items():
            model.register_callback(self._on_detection_complete)
        
        # Document preprocessing callbacks (use doc_preprocessing object flags)
        if self.doc_preprocessing and self.doc_preprocessing.use_doc_orientation and self.doc_orientation_node:
            self.doc_orientation_node.model.register_callback(self._on_doc_orientation_complete)
        if self.doc_preprocessing and self.doc_preprocessing.use_doc_unwarping and self.doc_unwarping_node:
            self.doc_unwarping_node.model.register_callback(self._on_doc_unwarping_complete)

        # Classification callback
        self.cls_model.register_callback(self._on_classification_complete)
        
        # Recognition callbacks (multiple ratio models)
        for ratio_key, model in self.rec_models.items():
            model.register_callback(self._on_recognition_complete)
    
    def get_preprocessed_image(self, image: np.ndarray) -> np.ndarray:
        """Run document preprocessing on image"""
        try:
            # Check use_doc_preprocessing flag (for dynamic control)
            if self.use_doc_preprocessing and self.doc_preprocessing is not None:
                preprocessed_image, _ = self.doc_preprocessing(image)
                return preprocessed_image
        except Exception as e:
            return image
        return image
    
    def process_batch(self, images: List[np.ndarray], timeout: float = 60.0, pass_preprocessing: bool = False, debug_output_dir: Optional[str] = None) -> List[Dict]:
        """
        Process a batch of images asynchronously
        
        Args:
            images: List of input images (numpy arrays)
            timeout: Timeout in seconds
            debug_output_dir: Optional directory to save debug JSON files
            
        Returns:
            List of results in original order
        """
        if not images:
            return []
        
        self._log(f"Starting batch processing: {len(images)} images")

        # 1. Create jobs
        jobs = []
        for i, orig_img in enumerate(images):
            job = OCRJob(f'job_{i}', orig_img)
            job.timestamps['start'] = time.time()
            if debug_output_dir:
                job.debug_output_dir = debug_output_dir
            jobs.append(job)
            self.active_jobs[job.job_id] = job

        # 2. Submit first stage for all jobs
        for job in jobs:
            if not pass_preprocessing:
                # Use doc_preprocessing object flags for consistency with PaddleOcr
                if self.doc_preprocessing and self.doc_preprocessing.use_doc_orientation:
                    self._submit_document_orientation(job)
                elif self.doc_preprocessing and self.doc_preprocessing.use_doc_unwarping:
                    self._submit_document_unwarping(job)
                else:
                    self._submit_detection(job)    
            else:
                self._submit_detection(job)

        # 3. Wait for all jobs to complete
        completed_jobs = {}
        start_time = time.time()

        while len(completed_jobs) < len(jobs):
            elapsed = time.time() - start_time
            if elapsed > timeout:
                self._log(f"Timeout after {elapsed:.1f}s, {len(completed_jobs)}/{len(jobs)} completed", force=True)
                break

            try:
                job = self.completed_queue.get(timeout=1.0)
                completed_jobs[job.job_id] = job
                self._log(f"Job completed: {job.job_id} ({len(completed_jobs)}/{len(jobs)})")
            except queue.Empty:
                continue

        # 4. Restore original order
        completed_in_order = []
        for original_job in jobs:
            if original_job.job_id in completed_jobs:
                completed_in_order.append(completed_jobs[original_job.job_id])
            else:
                # Job timed out or error
                self._log(f"Warning: Job {original_job.job_id} did not complete", force=True)
                completed_in_order.append(original_job)
        
        # 5. Collect profiling data
        current_batch_stats = []
        for job in completed_in_order:
            job_stat = {
                'job_id': job.job_id,
                'timestamps': job.timestamps,
                'stage_stats': job.stage_stats,
                'error': job.error
            }
            self.profiling_data.append(job_stat)
            current_batch_stats.append(job_stat)

        return self._format_results(completed_in_order)
    
    def _submit_document_orientation(self, job: OCRJob):
        """Submit document orientation inference."""
        if not self.doc_orientation_node:
            self._submit_document_unwarping(job)
            return

        job.timestamps['doc_ori_start'] = time.time()
        job.stage_stats['doc_ori']['start'] = job.timestamps['doc_ori_start']
        job.state = 'doc_orientation'

        t0 = time.time()
        preprocessed = self.doc_orientation_node.preprocess(job.preprocessed_image)
        model_input = self.doc_orientation_node.prepare_input(preprocessed)
        job.stage_stats['doc_ori']['preprocess'] = time.time() - t0
        job.doc_ori_input_buffer = model_input

        self._log(f"{job.job_id}: Submit doc orientation (shape={job.preprocessed_image.shape})")

        self.doc_orientation_node.model.run_async([job.doc_ori_input_buffer], user_arg=(job.job_id, 'doc_ori'))

        with self.lock:
            self.stats['doc_ori_submitted'] += 1

    def _on_doc_orientation_complete(self, outputs: List[np.ndarray], user_arg: Any) -> int:
        try:
            job_id, _ = user_arg
        except Exception as e:
            return 0

        if not self.doc_orientation_node:
            return 0

        try:
            with self.lock:
                job = self.active_jobs.get(job_id)
                if not job:
                    return 0
                self.stats['doc_ori_completed'] += 1
                job.debug_data['callback_order'].append('doc_ori_complete')

            job.timestamps['doc_ori_end'] = time.time()
            job.stage_stats['doc_ori']['end'] = job.timestamps['doc_ori_end']
            job.stage_stats['doc_ori']['duration'] = job.timestamps['doc_ori_end'] - job.timestamps['doc_ori_start']
            
            t0 = time.time()
            label, rotated_image = self.doc_orientation_node.postprocess(outputs[0], job.preprocessed_image)
            job.preprocessed_image = rotated_image
            job.stage_stats['doc_ori']['postprocess'] = time.time() - t0
            
            job.debug_data['doc_preprocessing']['orientation'] = {
                'label': str(label),
                'shape': list(rotated_image.shape)
            }

            self._log(f"{job_id}: Doc orientation complete -> label={label}")

            # Use doc_preprocessing object flag for consistency
            if self.doc_preprocessing and self.doc_preprocessing.use_doc_unwarping:
                self._dispatch_stage(self._submit_document_unwarping, job)
            else:
                self._dispatch_stage(self._submit_detection, job)

        except Exception as e:
            self._log(f"Error in doc orientation callback for {job_id}: {e}", force=True)
            import traceback
            traceback.print_exc()
            job_ref: Optional[OCRJob] = None
            with self.lock:
                job_ref = self.active_jobs.get(job_id)
            if job_ref is not None:
                job_ref.error = str(e)
                job_ref.state = 'error'
                self.completed_queue.put(job_ref)

        return 0

    def _submit_document_unwarping(self, job: OCRJob):
        """Submit document unwarping inference."""
        if not self.doc_unwarping_node:
            self._submit_detection(job)
            return

        job.timestamps['doc_uv_start'] = time.time()
        job.stage_stats['doc_uv']['start'] = job.timestamps['doc_uv_start']
        job.state = 'doc_unwarping'

        t0 = time.time()
        preprocessed = self.doc_unwarping_node.preprocess(job.preprocessed_image)
        model_input = self.doc_unwarping_node.prepare_input(preprocessed)
        job.stage_stats['doc_uv']['preprocess'] = time.time() - t0
        job.doc_uv_input_buffer = model_input

        self._log(f"{job.job_id}: Submit doc unwarping (shape={job.preprocessed_image.shape})")

        self.doc_unwarping_node.model.run_async([job.doc_uv_input_buffer], user_arg=(job.job_id, 'doc_uv'))

        with self.lock:
            self.stats['doc_uv_submitted'] += 1

    def _on_doc_unwarping_complete(self, outputs: List[np.ndarray], user_arg: Any) -> int:
        try:
            job_id, _ = user_arg
        except Exception as e:
            return 0

        if not self.doc_unwarping_node:
            return 0

        try:
            with self.lock:
                job = self.active_jobs.get(job_id)
                if not job:
                    return 0
                self.stats['doc_uv_completed'] += 1
                job.debug_data['callback_order'].append('doc_uv_complete')

            job.timestamps['doc_uv_end'] = time.time()
            job.stage_stats['doc_uv']['end'] = job.timestamps['doc_uv_end']
            job.stage_stats['doc_uv']['duration'] = job.timestamps['doc_uv_end'] - job.timestamps['doc_uv_start']

            # Defer heavy postprocess work to stage executor
            raw_output = outputs[0]
            self._dispatch_stage(self._finalize_doc_unwarping, job, raw_output)

        except Exception as e:
            self._log(f"Error in doc unwarping callback for {job_id}: {e}", force=True)
            import traceback
            traceback.print_exc()
            job_ref: Optional[OCRJob] = None
            with self.lock:
                job_ref = self.active_jobs.get(job_id)
            if job_ref is not None:
                job_ref.error = str(e)
                job_ref.state = 'error'
                self.completed_queue.put(job_ref)

        return 0

    def _finalize_doc_unwarping(self, job: OCRJob, raw_output: np.ndarray):
        """Run doc unwarping postprocess off the DXRT callback thread."""
        if not self.doc_unwarping_node:
            self._dispatch_stage(self._submit_detection, job)
            return

        job_id = job.job_id
        try:
            t0 = time.time()
            unwarped_image = self.doc_unwarping_node.postprocess(raw_output, job.preprocessed_image)
            job.preprocessed_image = unwarped_image
            job.stage_stats['doc_uv']['postprocess'] = time.time() - t0

            job.debug_data['doc_preprocessing']['unwarping'] = {
                'shape': list(unwarped_image.shape)
            }

            self._log(f"{job_id}: Doc unwarping complete (shape={unwarped_image.shape})")

            self._dispatch_stage(self._submit_detection, job)

        except Exception as e:
            self._log(f"Error finalizing doc unwarping for {job_id}: {e}", force=True)
            import traceback
            traceback.print_exc()
            job_ref: Optional[OCRJob] = None
            with self.lock:
                job_ref = self.active_jobs.get(job_id)
            if job_ref is not None:
                job_ref.error = str(e)
                job_ref.state = 'error'
                self.completed_queue.put(job_ref)

        return 0

    def _submit_detection(self, job: OCRJob):
        """Submit detection for a job"""
        job.timestamps['det_start'] = time.time()
        job.stage_stats['det']['start'] = job.timestamps['det_start']
        job.state = 'detecting'
        
        # Use preprocessed image for detection
        img = job.preprocessed_image
        h, w = img.shape[:2]
        
        # Route to appropriate detection model based on resolution
        mapped_res = self.detection_node.router(w, h)
        res_preprocess = self.detection_node.det_preprocess_map[mapped_res]
        res_model = self.det_models[mapped_res]
        
        # Preprocess image for the selected resolution
        t0 = time.time()
        preprocessed = res_preprocess(img)
        padding_info = res_preprocess.get_last_padding_info()
        model_input = self.detection_node.prepare_input(preprocessed)
        job.stage_stats['det']['preprocess'] = time.time() - t0
        
        # CRITICAL: Cache input buffer in job to prevent GC from freeing memory
        # dx_engine's run_async stores a reference to the buffer, not a copy
        # If buffer goes out of scope, Python GC may free or reuse the memory
        # causing non-deterministic results when dx_engine reads the data
        job.det_input_buffer = model_input
        job.det_padding_info = padding_info

        self._log(f"{job.job_id}: Submit detection (res={mapped_res}, shape={img.shape})")
        
        self._monitor_queues()
        try:
            # Submit async (buffer stays alive because job persists until completion)
            res_model.run_async([job.det_input_buffer], user_arg=(job.job_id, mapped_res, 'det'))
            with self.lock:
                self.stats['det_submitted'] += 1
        except Exception as e:
            self._log(f"Error submitting detection for {job.job_id}: {e}", force=True)
            import traceback
            traceback.print_exc()
            with self.lock:
                job_ref = self.active_jobs.get(job.job_id)
            if job_ref is not None:
                job_ref.error = str(e)
                job_ref.state = 'error'
                self.completed_queue.put(job_ref)
    
    def _on_detection_complete(self, outputs: List[np.ndarray], user_arg: Any) -> int:
        """Callback when detection completes"""
        # Handle None user_arg (deepx engine issue)
        if user_arg is None:
            self._log("WARNING: Detection callback received None user_arg, skipping", force=True)
            return 0
        
        job_id, mapped_res, stage = user_arg
        
        try:
            with self.lock:
                job = self.active_jobs.get(job_id)
                if not job:
                    return 0
                
                self.stats['det_completed'] += 1
                job.debug_data['callback_order'].append(f'det_complete')
            
            # Postprocess (outside lock)
            job.timestamps['det_end'] = time.time()
            job.stage_stats['det']['end'] = job.timestamps['det_end']
            job.stage_stats['det']['duration'] = job.timestamps['det_end'] - job.timestamps['det_start']

            raw_output = outputs[0]
            self._dispatch_stage(self._process_detection_results, job, mapped_res, raw_output)
            
        except Exception as e:
            self._log(f"Error in detection callback for {job_id}: {e}", force=True)
            import traceback
            traceback.print_exc()
            job_ref: Optional[OCRJob] = None
            with self.lock:
                job_ref = self.active_jobs.get(job_id)
            if job_ref is not None:
                job_ref.error = str(e)
                job_ref.state = 'error'
                self.completed_queue.put(job_ref)
        
        return 0

    def _process_detection_results(self, job: OCRJob, mapped_res: int, raw_output: np.ndarray):
        """Handle detection postprocess and crop generation on the executor."""
        job_id = job.job_id
        try:
            t0 = time.time()
            padding_info = job.det_padding_info
            det_output = self.detection_node.postprocess(raw_output, job.preprocessed_image.shape, padding_info)
            job.det_boxes = sorted_boxes(det_output)

            boxes_quad = convert_boxes_to_quad_format(job.det_boxes)
            job.crops = [
                rotate_if_vertical(get_rotate_crop_image(job.preprocessed_image, box))
                for box in boxes_quad
            ]
            job.det_boxes = [box.tolist() for box in job.det_boxes]
            job.stage_stats['det']['postprocess'] = time.time() - t0

            job.debug_data['detection']['count'] = len(job.det_boxes)
            job.debug_data['detection']['boxes'] = job.det_boxes

            if hasattr(job, 'debug_output_dir') and job.debug_output_dir:
                crop_dir = os.path.join(job.debug_output_dir, 'async_crops')
                os.makedirs(crop_dir, exist_ok=True)
                for i, crop in enumerate(job.crops):
                    crop_path = os.path.join(crop_dir, f'crop_{i:03d}.jpg')
                    cv2.imwrite(crop_path, crop)

            self._log(f"{job_id}: Detection complete, {len(job.det_boxes)} boxes found (res={mapped_res})")

            self._dispatch_stage(self._submit_classification, job)

        except Exception as e:
            self._log(f"Error processing detection results for {job_id}: {e}", force=True)
            import traceback
            traceback.print_exc()
            with self.lock:
                job_ref = self.active_jobs.get(job_id)
            if job_ref is not None:
                job_ref.error = str(e)
                job_ref.state = 'error'
                self.completed_queue.put(job_ref)
    
    def _submit_classification(self, job: OCRJob):
        """Submit classification for all crops"""
        if not job.crops:
            # No crops, skip to completion
            job.state = 'completed'
            job.timestamps['end'] = time.time()
            self.completed_queue.put(job)
            return
        
        job.timestamps['cls_start'] = time.time()
        job.stage_stats['cls']['start'] = job.timestamps['cls_start']
        job.stage_stats['cls']['count'] = len(job.crops)
        job.state = 'classifying'
        job.expected_cls_count = len(job.crops)
        job.expected_rec_count = len(job.crops)
        job.rec_results_dict = {}
        job.rec_completed_count = 0

        # Check if textline orientation classification is enabled (same as PaddleOcr)
        if not self.use_textline_orientation:
            # Skip classification and go directly to recognition
            self._log(f"{job.job_id}: Skip classification (use_textline_orientation=False), submit {len(job.crops)} crops to recognition")
            job.debug_data['classification']['skipped'] = True
            job.cls_completed_count = job.expected_cls_count  # Mark as complete
            
            # Submit all crops to recognition immediately
            for crop_idx in range(len(job.crops)):
                self._dispatch_stage(self._submit_recognition_for_crop, job, crop_idx)
            return

        self._log(f"{job.job_id}: Submit {len(job.crops)} crops to classification")
        
        self._monitor_queues()
        # Submit each crop
        t0 = time.time()
        for crop_idx, crop in enumerate(job.crops):
            # Preprocess (CRITICAL: Must match sync version!)
            # 1. Apply cls_preprocess first
            cls_preprocessed = self.classification_node.cls_preprocess(crop)
            # 2. Then prepare_input for model format
            cls_input = self.classification_node.prepare_input(cls_preprocessed)
            
            # CRITICAL: Cache input buffer to prevent GC
            job.cls_input_buffers[crop_idx] = cls_input
            
            with self.lock:
                self.stats['cls_submitted'] += 1
            
            # Record start time for this crop
            job.cls_crop_start_times[crop_idx] = time.time()

            # Submit async (buffer stays alive in job.cls_input_buffers)
            self.cls_model.run_async([job.cls_input_buffers[crop_idx]], user_arg=(job.job_id, crop_idx, 'cls'))
        
        job.stage_stats['cls']['preprocess'] += (time.time() - t0)
    
    def _on_classification_complete(self, outputs: List[np.ndarray], user_arg: Any) -> int:
        """Callback when classification completes"""
        # Handle None user_arg (deepx engine issue)
        if user_arg is None:
            self._log("WARNING: Classification callback received None user_arg, skipping", force=True)
            return 0
        
        job_id, crop_idx, stage = user_arg
        try:
            t0 = time.time()
            
            # Calculate duration for this specific crop
            crop_duration = 0.0
            
            cls_result = self.classification_node.cls_postprocess(outputs[0])[0]
            label = str(cls_result[0])
            score_raw = cls_result[1]
            score_candidate: Any
            if isinstance(score_raw, (list, tuple)) and score_raw:
                score_candidate = score_raw[0]
            else:
                score_candidate = score_raw
            try:
                score_value = float(score_candidate)
            except (TypeError, ValueError):
                score_value = 0.0
            
            # Determine if rotation is needed (logic part of postprocess)
            needs_rotation = (isinstance(label, str) and "180" in label) and score_value > self.cls_thresh
            
            # Apply rotation if needed (CV part of postprocess)
            # Note: We need to access job.crops which requires lock or careful access
            # Here we just calculate what to do, actual crop modification happens later
            
            post_time = time.time() - t0

            with self.lock:
                job = self.active_jobs.get(job_id)
                if not job:
                    return 0
                if not job.crops or crop_idx >= len(job.crops):
                    return 0

                # Calculate individual duration
                if crop_idx in job.cls_crop_start_times:
                    start_time = job.cls_crop_start_times[crop_idx]
                    crop_duration = t0 - start_time
                    job.stage_stats['cls']['accumulated_duration'] += crop_duration

                job.cls_results[crop_idx] = (label, score_value)
                job.cls_completed_count += 1
                all_done = (job.cls_completed_count >= job.expected_cls_count)
                
                # Accumulate postprocess time
                job.stage_stats['cls']['postprocess'] += post_time

                job.debug_data['callback_order'].append(f'cls_complete_{crop_idx}')
                job.debug_data['classification']['order'].append(int(crop_idx))
                # needs_rotation was calculated above
                job.debug_data['classification']['results'].append({
                    'crop_index': int(crop_idx),
                    'label': label,
                    'score': score_value,
                    'rotated': bool(needs_rotation)
                })

                self.stats['cls_completed'] += 1

            # Free classification buffer once it's no longer needed
            job.cls_input_buffers.pop(crop_idx, None)

            # Additional CV work (rotation) - measure this too
            t1 = time.time()
            crop_image = job.crops[crop_idx]
            if needs_rotation:
                rotated = cv2.rotate(crop_image, cv2.ROTATE_180)
                crop_image = np.ascontiguousarray(rotated, dtype=np.uint8)
                job.crops[crop_idx] = crop_image
            elif not crop_image.flags['C_CONTIGUOUS']:
                job.crops[crop_idx] = np.ascontiguousarray(crop_image)
            
            # Add rotation time to postprocess
            with self.lock:
                job.stage_stats['cls']['postprocess'] += (time.time() - t1)

            # Submit recognition immediately for this crop
            self._dispatch_stage(self._submit_recognition_for_crop, job, crop_idx)

            if all_done:
                job.timestamps['cls_end'] = time.time()
                job.stage_stats['cls']['end'] = job.timestamps['cls_end']
                job.stage_stats['cls']['duration'] = job.timestamps['cls_end'] - job.timestamps['cls_start']
                self._log(f"{job_id}: Classification complete, {job.cls_completed_count} crops")

        except Exception as e:
            self._log(f"Error in classification callback for {job_id}: {e}", force=True)
            import traceback
            traceback.print_exc()
            job_ref: Optional[OCRJob] = None
            with self.lock:
                job_ref = self.active_jobs.get(job_id)
            if job_ref is not None:
                job_ref.error = str(e)
                job_ref.state = 'error'
                self.completed_queue.put(job_ref)

        return 0
    
    def _submit_recognition_for_crop(self, job: OCRJob, crop_idx: int):
        """Submit recognition for a single crop immediately after classification."""
        if not job.crops:
            return

        crop = job.crops[crop_idx]
        if crop is None:
            return

        if 'rec_start' not in job.timestamps:
            job.timestamps['rec_start'] = time.time()
            job.stage_stats['rec']['start'] = job.timestamps['rec_start']
            job.stage_stats['rec']['count'] = len(job.crops)
            job.state = 'recognizing'

        self._log(f"{job.job_id}: Submit recognition for crop_{crop_idx} (shape={crop.shape})")

        try:
            if hasattr(self, 'debug') and self.debug:
                was_rotated = (
                    crop_idx in job.cls_results and
                    isinstance(job.cls_results[crop_idx][0], str) and
                    "180" in job.cls_results[crop_idx][0] and
                    job.cls_results[crop_idx][1] > self.cls_thresh
                )
                print(f"[DEBUG] Submitting rec for crop_{crop_idx}, shape={crop.shape}, rotated={was_rotated}")

            t0 = time.time()
            if not crop.flags['C_CONTIGUOUS']:
                crop = np.ascontiguousarray(crop, dtype=crop.dtype)
                job.crops[crop_idx] = crop

            mapped_ratio = self.recognition_node.router(crop.shape[1], crop.shape[0])
            ratio_preprocess = self.recognition_node.rec_preprocess_map[mapped_ratio]
            ratio_model = self.rec_models[mapped_ratio]

            inp = ratio_preprocess(crop)
            rec_input = self.recognition_node.prepare_input(inp)
            prep_time = time.time() - t0

            job.rec_input_buffers[crop_idx] = rec_input

            with self.lock:
                self.stats['rec_submitted'] += 1
                job.stage_stats['rec']['preprocess'] += prep_time
            
            # Record start time for this crop
            job.rec_crop_start_times[crop_idx] = time.time()

            self._monitor_queues()
            ratio_model.run_async([job.rec_input_buffers[crop_idx]], user_arg=(job.job_id, crop_idx, 'rec', mapped_ratio))

        except Exception as e:
            self._log(f"ERROR submitting rec for {job.job_id} crop_{crop_idx}: {e}", force=True)
            import traceback
            traceback.print_exc()
    
    def _on_recognition_complete(self, outputs: List[np.ndarray], user_arg: Any) -> int:
        """Callback when recognition completes"""
        # Handle None user_arg (deepx engine issue)
        if user_arg is None:
            self._log("WARNING: Recognition callback received None user_arg, skipping", force=True)
            return 0
        
        job_id, crop_idx, stage, mapped_ratio = user_arg
        
        try:
            # Postprocess (outside lock)
            t0 = time.time()
            res = self.recognition_node.rec_postprocess(outputs[0])[0]  # (text, score)
            text, score = res
            post_time = time.time() - t0
            
            # Debug logging
            if hasattr(self, 'debug') and self.debug:
                print(f"[DEBUG] Rec complete: {job_id}, crop_{crop_idx}, score={score:.3f}, text='{text[:20]}...'")
            
            # Update job state
            with self.lock:
                job = self.active_jobs.get(job_id)
                if not job:
                    if hasattr(self, 'debug') and self.debug:
                        print(f"[DEBUG] Job {job_id} not found in active_jobs!")
                    return 0
                
                job.stage_stats['rec']['postprocess'] += post_time
                
                # Calculate individual duration
                if crop_idx in job.rec_crop_start_times:
                    start_time = job.rec_crop_start_times[crop_idx]
                    crop_duration = t0 - start_time
                    job.stage_stats['rec']['accumulated_duration'] += crop_duration
                
                # Record callback order
                job.debug_data['callback_order'].append(f'rec_complete_{crop_idx}')
                job.debug_data['recognition']['order'].append(crop_idx)
                
                # Apply drop threshold and store in dictionary (order-independent)
                if score > self.recognition_node.drop:
                    # Store result in dict format indexed by crop_idx
                    result = {
                        'bbox_index': crop_idx,
                        'bbox': job.det_boxes[crop_idx] if job.det_boxes and crop_idx < len(job.det_boxes) else None,
                        'text': text,
                        'score': score
                    }
                    job.rec_results_dict[crop_idx] = result
                    
                    # Record recognition result
                    job.debug_data['recognition']['results'].append({
                        'bbox_index': crop_idx,
                        'text': text,
                        'score': float(score)
                    })
                
                job.rec_completed_count += 1
                job.rec_input_buffers.pop(crop_idx, None)
                all_done = (job.rec_completed_count >= job.expected_rec_count)
                
                if all_done:
                    job.timestamps['rec_end'] = time.time()
                    job.stage_stats['rec']['end'] = job.timestamps['rec_end']
                    job.stage_stats['rec']['duration'] = job.timestamps['rec_end'] - job.timestamps['rec_start']
                
                self.stats['rec_completed'] += 1
            
            # If all recognition done, mark job as complete
            if all_done:
                job.timestamps['rec_end'] = time.time()
                job.timestamps['end'] = time.time()
                job.state = 'completed'
                
                job.rec_results = [
                    job.rec_results_dict[idx] 
                    for idx in sorted(job.rec_results_dict.keys())
                ]
                
                self._log(f"{job_id}: Recognition complete, {len(job.rec_results)} texts recognized")
                
                self.completed_queue.put(job)
        
        except Exception as e:
            self._log(f"Error in recognition callback for {job_id}: {e}", force=True)
            import traceback
            traceback.print_exc()
            job_ref: Optional[OCRJob] = None
            with self.lock:
                job_ref = self.active_jobs.get(job_id)
            if job_ref is not None:
                job_ref.error = str(e)
                job_ref.state = 'error'
                self.completed_queue.put(job_ref)
        
        return 0
    
    def _format_results(self, completed_jobs: List[OCRJob]) -> List[Dict]:
        """Format job results to match sync version output"""
        results = []
        
        for job in completed_jobs:
            if job.error:
                self._log(f"Job {job.job_id} had error: {job.error}", force=True)
            
            # Calculate timings
            pipeline_total = 0
            if 'start' in job.timestamps and 'end' in job.timestamps:
                pipeline_total = (job.timestamps['end'] - job.timestamps['start']) * 1000
            
            det_time = 0
            if 'det_start' in job.timestamps and 'det_end' in job.timestamps:
                det_time = (job.timestamps['det_end'] - job.timestamps['det_start']) * 1000
            
            cls_time = 0
            if 'cls_start' in job.timestamps and 'cls_end' in job.timestamps:
                cls_time = (job.timestamps['cls_end'] - job.timestamps['cls_start']) * 1000
            
            rec_time = 0
            if 'rec_start' in job.timestamps and 'rec_end' in job.timestamps:
                rec_time = (job.timestamps['rec_end'] - job.timestamps['rec_start']) * 1000
            
            doc_ori_time = 0
            if 'doc_ori_start' in job.timestamps and 'doc_ori_end' in job.timestamps:
                doc_ori_time = (job.timestamps['doc_ori_end'] - job.timestamps['doc_ori_start']) * 1000
                
            doc_uv_time = 0
            if 'doc_uv_start' in job.timestamps and 'doc_uv_end' in job.timestamps:
                doc_uv_time = (job.timestamps['doc_uv_end'] - job.timestamps['doc_uv_start']) * 1000
            
            # Print per-module timing for this job
            num_crops = len(job.crops) if job.crops else 0
            num_texts = len(job.rec_results) if job.rec_results else 0
            
            if pipeline_total > 0:
                # Calculate CPS (Characters Per Second)
                total_chars = sum(len(result['text']) for result in job.rec_results)
                cps = (total_chars / (pipeline_total / 1000)) if pipeline_total > 0 else 0

            # CPU-compatible format with doc_preprocessor_res
            result = {
                'job_id': job.job_id,
                'boxes': job.det_boxes or [],
                'rec_results': job.rec_results,
                'preprocessed_image': job.preprocessed_image,
                # CPU-compatible fields
                'rec_texts': [r['text'] for r in job.rec_results],
                'rec_scores': [r['score'] for r in job.rec_results],
                'rec_polys': [r['bbox'] for r in job.rec_results],
                'doc_preprocessor_res': {'output_img': job.preprocessed_image},
                # Performance metrics
                'total_latency_ms': pipeline_total,
                'det_latency_ms': det_time,
                'cls_latency_ms': cls_time,
                'rec_latency_ms': rec_time,
                'doc_ori_latency_ms': doc_ori_time,
                'doc_uv_latency_ms': doc_uv_time,
                'state': job.state,
                'error': job.error,
                'perf_stats': {
                    
                    'det_time_ms': det_time,
                    'cls_time_ms': cls_time/(num_crops + 0.0001),
                    'rec_time_ms': rec_time/(num_crops + 0.0001),
                    'e2e_time_ms': pipeline_total,
                    'cps': cps,
                    'total_chars': total_chars,
                    'num_boxes': len(job.det_boxes) if job.det_boxes else 0,
                    'num_crops': num_crops
                }
            }
            results.append(result)

            # Collect stats for profiling
            if not job.error:
                self.perf_monitor['job_latencies'].append({
                    'job_id': job.job_id,
                    'total': pipeline_total,
                    'det': det_time,
                    'cls': cls_time,
                    'rec': rec_time,
                    'doc_ori': doc_ori_time,
                    'doc_uv': doc_uv_time,
                    'start_timestamp': job.timestamps.get('start', 0),
                    'end_timestamp': job.timestamps.get('end', 0)
                })
        
        return results
    
    def print_performance_report(self):
        """Print detailed performance report based on collected profiling data"""
        if not self.profiling_data:
            print("No profiling data available.")
            return

        print("\n" + "="*50)
        print("ASYNC PIPELINE PERFORMANCE REPORT")
        print("="*50)
        
        # Calculate average durations per stage
        stages = ['doc_ori', 'doc_uv', 'det', 'cls', 'rec']
        stage_durations = {s: [] for s in stages}
        
        for job in self.profiling_data:
            stats = job['stage_stats']
            for stage in stages:
                if stage in stats and stats[stage]['duration'] > 0:
                    stage_durations[stage].append(stats[stage]['duration'] * 1000) # ms
        
        print("\n[Stage Latencies (ms)]")
        print(f"{'Stage':<15} {'Count':<8} {'Avg':<10} {'Min':<10} {'Max':<10} {'Pre(Avg)':<10} {'Post(Avg)':<10} {'Accum(Avg)':<10}")
        print("-" * 95)
        
        for stage in stages:
            durs = stage_durations[stage]
            if durs:
                avg_d = sum(durs) / len(durs)
                min_d = min(durs)
                max_d = max(durs)
                
                # Calculate avg preprocess/postprocess
                total_pre = 0
                total_post = 0
                total_accum = 0
                total_count = 0
                
                for job in self.profiling_data:
                    stats = job['stage_stats']
                    if stage in stats:
                        s = stats[stage]
                        # For det/doc, count is effectively 1 per job. For cls/rec, it's num_crops.
                        # If 'count' key exists and > 0, use it. Else assume 1 (for single image stages).
                        count = s.get('count', 0)
                        if count == 0: count = 1 
                        
                        total_pre += s.get('preprocess', 0)
                        total_post += s.get('postprocess', 0)
                        total_accum += s.get('accumulated_duration', 0)
                        total_count += count
                
                # Averages per item (image or crop)
                avg_pre = (total_pre / total_count * 1000) if total_count > 0 else 0
                avg_post = (total_post / total_count * 1000) if total_count > 0 else 0
                avg_accum = (total_accum / total_count * 1000) if total_count > 0 else 0
                
                print(f"{stage:<15} {len(durs):<8} {avg_d:<10.2f} {min_d:<10.2f} {max_d:<10.2f} {avg_pre:<10.2f} {avg_post:<10.2f} {avg_accum:<10.2f}")
            else:
                print(f"{stage:<15} {'0':<8} {'N/A':<10} {'N/A':<10} {'N/A':<10} {'N/A':<10} {'N/A':<10} {'N/A':<10}")
                
        # Buffer stats analysis
        if self.buffer_stats:
            print("\n[Buffer Utilization]")
            print(f"{'Stage':<15} {'Avg Jobs':<10} {'Max Jobs':<10}")
            print("-" * 40)
            
            stage_counts = {s: [] for s in ['doc_orientation', 'doc_unwarping', 'detecting', 'classifying', 'recognizing']}
            for stat in self.buffer_stats:
                for s in stage_counts:
                    if s in stat:
                        stage_counts[s].append(stat[s])
            
            for stage, counts in stage_counts.items():
                if counts:
                    avg_c = sum(counts) / len(counts)
                    max_c = max(counts)
                    print(f"{stage:<15} {avg_c:<10.2f} {max_c:<10}")
        
        print("="*50 + "\n")

    def _monitor_queues(self):
        """Record current queue sizes for profiling"""
        try:
            executor_qsize = self.stage_executor._work_queue.qsize() if hasattr(self.stage_executor, '_work_queue') else 0
            
            # Count jobs in each state
            state_counts = {
                'doc_orientation': 0,
                'doc_unwarping': 0,
                'detecting': 0,
                'classifying': 0,
                'recognizing': 0,
                'completed': 0,
                'error': 0
            }
            
            # Snapshot active jobs
            with self.lock:
                for job in self.active_jobs.values():
                    if job.state in state_counts:
                        state_counts[job.state] += 1
            
            stats = {
                'timestamp': time.time(),
                'active_jobs': len(self.active_jobs),
                'executor_queue': executor_qsize,
                **state_counts
            }
            
            self.perf_monitor['queue_sizes'].append(stats)
            self.buffer_stats.append(stats)
            
        except Exception:
            pass
