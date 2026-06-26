import time
from PIL import Image
from typing import List, Tuple

import cv2
from loguru import logger
from tqdm import tqdm
from collections import defaultdict
import numpy as np

from .model_init import AtomModelSingleton
from .model_list import AtomicModel
from ...utils.boxbase import rotate_image_and_boxes
from ...utils.checkbox_det_cls import checkbox_predict
from ...utils.config_reader import get_formula_enable, get_table_enable
from ...utils.enum_class import CategoryId
from ...utils.model_utils import crop_img, get_res_list_from_layout_res
from ...utils.ocr_utils import merge_det_boxes, update_det_boxes, sorted_boxes
from ...utils.ocr_utils import get_adjusted_mfdetrec_res, get_ocr_result_list, OcrConfidence, get_ocr_result_list_table
from ...utils.span_pre_proc import txt_spans_extract, txt_spans_bbox_extract, txt_spans_bbox_extract_table, \
    txt_most_angle_extract_table, extract_table_fill_image


# YOLO_LAYOUT_BASE_BATCH_SIZE = 8
# MFR_BASE_BATCH_SIZE = 16
# OCR_DET_BASE_BATCH_SIZE = 16

# LAYOUT_BASE_BATCH_SIZE = 1
# FORMULA_BASE_BATCH_SIZE = 1
# OCR_DET_BASE_BATCH_SIZE = 16


class BatchAnalyze:
    def __init__(self, model, batch_ratio: int, formula_enable, table_enable, enable_ocr_det_batch: bool = False,
                layout_config=None,
                ocr_config=None,
                formula_config=None,
                table_config=None,
                checkbox_config=None):
        self.batch_ratio = batch_ratio
        self.formula_enable = get_formula_enable(formula_enable)
        self.formula_rec_enable = formula_config.get("formula_rec_enable", True) if formula_config else True
        self.formula_level = formula_config.get("formula_level", 2) if formula_config else 2
        self.table_enable = get_table_enable(table_enable)
        self.table_force_ocr = table_config.get("force_ocr", False) if table_config else False
        self.skip_text_in_image = table_config.get("skip_text_in_image", True) if table_config else True
        self.use_img2table = table_config.get("use_img2table", False) if table_config else False
        self.checkbox_enable = checkbox_config.get("checkbox_enable", False) if checkbox_config else False
        self.layout_config = layout_config
        self.ocr_config = ocr_config
        self.formula_config = formula_config
        self.table_config = table_config
        self.model = model  # Store the provided model without additional caching
        self.enable_ocr_det_batch = ocr_config.get("Det.rec_batch_num", 1) > 1 if ocr_config else False
        self.ocr_det_base_batch_size = ocr_config.get("Det.rec_batch_num", 1) if ocr_config else 1 #16
        self.layout_base_batch_size = layout_config.get("batch_num", 1) if layout_config else 1 #8
        self.formula_base_batch_size = formula_config.get("batch_num", 1) if formula_config else 1 #16
        self.use_det_mode = ocr_config.get("use_det_mode", 'auto') if ocr_config else 'auto'
        
        # Save engine configuration
        self.engines = self._get_engine_info(layout_config, ocr_config, formula_config, table_config)
        
        # Store performance statistics
        self.perf_stats = {}
        self.pdf_perf_stats = defaultdict(lambda: defaultdict(lambda: {'time': 0.0, 'count': 0}))

    def _get_engine_info(self, layout_config, ocr_config, formula_config, table_config):
        """Extract engine information from configuration objects"""
        engines = {}
        
        # Layout engine
        if layout_config:
            engine_type = layout_config.get('engine_type')
            if hasattr(engine_type, 'value'):
                engines['layout'] = engine_type.value
            elif isinstance(engine_type, str):
                engines['layout'] = engine_type
            else:
                engines['layout'] = 'onnxruntime'
        else:
            engines['layout'] = 'onnxruntime'
        
        # OCR engine
        if ocr_config:
            engine_type = ocr_config.get('engine_type') or ocr_config.get('Det.engine_type')
            if hasattr(engine_type, 'value'):
                engines['ocr'] = engine_type.value
            elif isinstance(engine_type, str):
                engines['ocr'] = engine_type
            else:
                engines['ocr'] = 'onnxruntime'
        else:
            engines['ocr'] = 'onnxruntime'
        
        # Formula engine
        if formula_config:
            engine_type = formula_config.get('engine_type')
            if hasattr(engine_type, 'value'):
                engines['formula'] = engine_type.value
            elif isinstance(engine_type, str):
                engines['formula'] = engine_type
            else:
                engines['formula'] = 'onnxruntime'
        else:
            engines['formula'] = 'onnxruntime'
        
        # Table engine
        if table_config:
            engine_type = table_config.get('engine_type')
            if hasattr(engine_type, 'value'):
                engines['table'] = engine_type.value
            elif isinstance(engine_type, str):
                engines['table'] = engine_type
            else:
                engines['table'] = 'onnxruntime'
        else:
            engines['table'] = 'onnxruntime'
        
        return engines

    def __call__(self, images_with_extra_info: List[Tuple[Image.Image, float, bool, str, dict]]) -> list:
        if len(images_with_extra_info) == 0:
            return [], []

        images_layout_res = []
        page_perf_stats = []  # Per-page performance statistics

        # Model already provided at init; no additional get_model call needed
        atom_model_manager = AtomModelSingleton()

        # Handle tuple length differences for backward compatibility
        first_item = images_with_extra_info[0]
        if len(first_item) == 7:
            # New version: (image, scale, ocr_enable, lang, pdf_dict, pdf_idx, page_idx)
            pdf_dict_list = [item[4] for item in images_with_extra_info]
            np_images = [cv2.cvtColor(np.array(item[0]), cv2.COLOR_RGB2BGR) for item in images_with_extra_info]
            scale_list = [item[1] for item in images_with_extra_info]
            pdf_indices = [item[5] for item in images_with_extra_info]
            page_indices = [item[6] for item in images_with_extra_info]
        else:
            # Legacy version: (image, scale, ocr_enable, lang, pdf_dict)
            pdf_dict_list = [item[4] for item in images_with_extra_info]
            np_images = [cv2.cvtColor(np.array(item[0]), cv2.COLOR_RGB2BGR) for item in images_with_extra_info]
            scale_list = [item[1] for item in images_with_extra_info]
            pdf_indices = [0] * len(images_with_extra_info)
            page_indices = list(range(len(images_with_extra_info)))

        # =====================================================================
        # Performance measurement: Layout model
        # =====================================================================
        layout_start = time.perf_counter()
        images_layout_res += self.model.layout_model.batch_predict(
            np_images, self.layout_base_batch_size
        )
        layout_time = time.perf_counter() - layout_start
        self.perf_stats['layout'] = {'time': layout_time, 'count': len(np_images)}
        # Collect per-PDF statistics (distribute time per page)
        for pdf_idx in pdf_indices:
            self.pdf_perf_stats[pdf_idx]['layout']['time'] += layout_time / len(np_images)
            self.pdf_perf_stats[pdf_idx]['layout']['count'] += 1
        logger.info(f"📊 [Layout] Processing time: {layout_time:.3f}s | "
                   f"{len(np_images)}it | "
                   f"{layout_time/len(np_images):.3f} s/it | "
                   f"{len(np_images)/layout_time:.2f} it/s")
        # =====================================================================

        # formula_level: formula recognition level
        #   0: all formulas → LaTeX recognition
        #   1: interline only (remove inline from layout), interline → LaTeX
        #   2 (default): inline → LaTeX, interline → image fallback (skip LaTeX)
        if self.formula_enable and self.formula_level == 1:
            images_layout_res = [
                [item for item in page if item["category_id"] != 13]
                for page in images_layout_res
            ]

        ocr_res_list_all_page = []
        table_res_list_all_page = []
        latex_res_list_all_page = []
        for index in range(len(np_images)):
            item = images_with_extra_info[index]
            if len(item) == 7:
                _, _, ocr_enable, _lang, _, _, _ = item
            else:
                _, _, ocr_enable, _lang, _ = item
            layout_res = images_layout_res[index]
            np_img = np_images[index]

            ocr_res_list, table_res_list, single_page_mfdetrec_res = (
                get_res_list_from_layout_res(layout_res, np_img)
            )

            # Checkbox detection
            checkbox_res = []
            if self.checkbox_enable:
                checkbox_img = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)
                checkbox_res = checkbox_predict(checkbox_img)
                for res in checkbox_res:
                    poly = [res['bbox'][0], res['bbox'][1], res['bbox'][2], res['bbox'][1],
                            res['bbox'][2], res['bbox'][3], res['bbox'][0], res['bbox'][3]]
                    layout_res.append({'bbox': res['bbox'], 'poly': poly, 'category_id': CategoryId.CheckBox,
                                       'checkbox': res['text'], 'score': 0.9})

            ocr_res_list_all_page.append({'ocr_res_list':ocr_res_list,
                                          'lang':_lang,
                                          'ocr_enable':ocr_enable,
                                          'np_img':np_img,
                                          'single_page_mfdetrec_res':single_page_mfdetrec_res,
                                          'checkbox_res': checkbox_res,
                                          'layout_res':layout_res,
                                          'page_idx': index,
                                          'pdf_idx': pdf_indices[index],
                                          })

            for table_res in table_res_list:
                table_img, useful_list = crop_img(table_res, np_img)
                table_res_list_all_page.append({'table_res':table_res,
                                                'lang':_lang,
                                                'table_img':table_img,
                                                'single_page_mfdetrec_res': single_page_mfdetrec_res,
                                                'checkbox_res': checkbox_res,
                                                'useful_list': useful_list,
                                                'ocr_enable': ocr_enable,
                                                'page_idx': index,
                                                'pdf_idx': pdf_indices[index],
                                              })
            for latex_res in single_page_mfdetrec_res:
                # formula_level=2: 행간 수식(cat 8,14)은 LaTeX 추론 스킵 → 이미지 폴백
                if self.formula_level == 2 and latex_res.get("category_id") in (
                    CategoryId.InterlineEquation_Layout,
                    CategoryId.InterlineEquation_YOLO,
                ):
                    continue
                latex_img, _ = crop_img(latex_res, np_img)
                latex_res_list_all_page.append({'latex_res': latex_res,
                                                'lang': _lang,
                                                'latex_img': latex_img,
                                                'page_idx': index,
                                                'pdf_idx': pdf_indices[index],
                                              })

        # =====================================================================
        # Performance measurement: Formula model
        # =====================================================================
        if self.formula_enable and self.formula_rec_enable and len(latex_res_list_all_page) > 0:
            formula_start = time.perf_counter()
            # Formula detection
            latex_imgs = [d['latex_img'] for d in latex_res_list_all_page]
            latex_results = self.model.formula_model.batch_predict(latex_imgs, batch_size=self.formula_base_batch_size)
            formula_success_count = 0
            for d, res in zip(latex_res_list_all_page, latex_results):
                if res:
                    d['latex_res']['latex'] = res
                    formula_success_count += 1
                else:
                    logger.warning('latex recognition processing fails, not get latex return')
            formula_time = time.perf_counter() - formula_start
            self.perf_stats['formula'] = {
                'time': formula_time, 
                'count': len(latex_imgs),
                'success': formula_success_count,
                'fail': len(latex_imgs) - formula_success_count
            }
            # Collect per-PDF statistics
            for d in latex_res_list_all_page:
                pdf_idx = d['pdf_idx']
                self.pdf_perf_stats[pdf_idx]['formula']['time'] += formula_time / len(latex_imgs)
                self.pdf_perf_stats[pdf_idx]['formula']['count'] += 1
            logger.info(f"📐 [Formula] Processing time: {formula_time:.3f}s | "
                       f"{len(latex_imgs)}it (success: {formula_success_count}, fail: {len(latex_imgs) - formula_success_count}) | "
                       f"{formula_time/max(len(latex_imgs), 1):.3f} s/it | "
                       f"{len(latex_imgs)/max(formula_time, 0.001):.2f} it/s")
        elif self.formula_enable and not self.formula_rec_enable:
            logger.info("📐 [Formula] formula_rec_enable=False; kept as image")
        elif self.formula_enable:
            logger.info("📐 [Formula] No formulas to process; skipped")
        # =====================================================================

        # VRAM cleanup
        # clean_vram(self.model.device, vram_threshold=8)

        # =====================================================================
        # Performance measurement: PDF-det (text extraction)
        # =====================================================================
        pdf_det_start = time.perf_counter()
        pdf_det_count = 0
        pdf_det_count_by_pdf = defaultdict(int)  # Count per PDF
        if self.use_det_mode != 'ocr':
            # Group by page
            ocr_res_list_grouped_page = {}
            for x in ocr_res_list_all_page:
                ocr_res_list_grouped_page.setdefault(x["page_idx"], []).append(x)
            # Calculate total count
            total_texts = sum(len(texts) for texts in ocr_res_list_grouped_page.values())
            with tqdm(total=total_texts, desc="PDF-det Predict") as pbar:
                for page_idx, text_list in ocr_res_list_grouped_page.items():
                    if text_list:
                        page_dict = pdf_dict_list[page_idx]
                        scale = scale_list[page_idx]
                    for ocr_res_list_dict in text_list:
                        _lang = ocr_res_list_dict['lang']
                        pdf_idx = ocr_res_list_dict['pdf_idx']
                        if ocr_res_list_dict['ocr_enable']:
                            # Skip when OCR is required
                            continue
                        # Extract text line locations from PDF
                        for res in ocr_res_list_dict['ocr_res_list']:
                            # res location info
                            new_image, useful_list = crop_img(
                                res, ocr_res_list_dict['np_img'], crop_paste_x=50, crop_paste_y=50
                            )
                            # Skip formulas and checkboxes
                            adjusted_mfdetrec_res = get_adjusted_mfdetrec_res(
                                ocr_res_list_dict['single_page_mfdetrec_res'] + ocr_res_list_dict['checkbox_res'],
                                useful_list
                            )
                            # PDF-det
                            bgr_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)
                            ocr_res = txt_spans_bbox_extract(page_dict, res, mfd_res=adjusted_mfdetrec_res, scale=scale, useful_list=useful_list)  # Extract text line locations from PDF
                            # Combine results
                            if ocr_res:
                                ocr_result_list = get_ocr_result_list(
                                    ocr_res, useful_list, ocr_res_list_dict['ocr_enable'], bgr_image, _lang
                                )

                                ocr_res_list_dict['layout_res'].extend(ocr_result_list)
                        pbar.update(1)  # Update after each item
                        pdf_det_count += 1
                        pdf_det_count_by_pdf[pdf_idx] += 1
        
        pdf_det_time = time.perf_counter() - pdf_det_start
        if pdf_det_count > 0:
            self.perf_stats['pdf_det'] = {'time': pdf_det_time, 'count': pdf_det_count}
            # Collect per-PDF statistics
            for pdf_idx, count in pdf_det_count_by_pdf.items():
                self.pdf_perf_stats[pdf_idx]['pdf_det']['time'] += (pdf_det_time / pdf_det_count) * count
                self.pdf_perf_stats[pdf_idx]['pdf_det']['count'] += count
            logger.info(f"📄 [PDF-det] Processing time: {pdf_det_time:.3f}s | "
                       f"{pdf_det_count}it | "
                       f"{pdf_det_time/pdf_det_count:.3f} s/it | "
                       f"{pdf_det_count/pdf_det_time:.2f} it/s")
        # =====================================================================


        # =====================================================================
        # Performance measurement: OCR Detection
        # =====================================================================
        ocr_det_start = time.perf_counter()
        ocr_det_count = 0
        ocr_det_count_by_pdf = defaultdict(int)  # Count per PDF
        # OCR detection processing
        if self.enable_ocr_det_batch:
            # Batch mode - group by resolution
            # Collect all crop images that need OCR detection
            all_cropped_images_info = []

            for ocr_res_list_dict in ocr_res_list_all_page:
                _lang = ocr_res_list_dict['lang']
                pdf_idx = ocr_res_list_dict['pdf_idx']
                for res in ocr_res_list_dict['ocr_res_list']:
                    # Decide whether to skip when full-page OCR is disabled
                    if not ocr_res_list_dict['ocr_enable']:
                        if (
                                self.use_det_mode == 'txt' or
                                (self.use_det_mode != 'ocr' and not ocr_res_list_dict['ocr_enable'] and not res.get('need_ocr_det'))
                        ):
                            # Skip if text boxes are extracted directly from PDF and OCR is unnecessary
                            continue
                    res.pop('need_ocr_det', None)
                    new_image, useful_list = crop_img(
                        res, ocr_res_list_dict['np_img'], crop_paste_x=50, crop_paste_y=50
                    )
                    # Skip formulas and checkboxes when performing OCR detection
                    adjusted_mfdetrec_res = get_adjusted_mfdetrec_res(
                        ocr_res_list_dict['single_page_mfdetrec_res'] + ocr_res_list_dict['checkbox_res'], useful_list
                    )

                    # Convert to BGR
                    bgr_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)

                    all_cropped_images_info.append((
                        bgr_image, useful_list, ocr_res_list_dict, res, adjusted_mfdetrec_res, pdf_idx
                    ))

            # Process all images together (no per-language grouping)
            if all_cropped_images_info:
                # Fetch OCR model once (language agnostic)
                ocr_model = atom_model_manager.get_atom_model(
                    atom_model_name=AtomicModel.OCR,
                    det_db_box_thresh=0.3,
                    ocr_config=self.ocr_config,
                )

                # Group by resolution and pad
                # RESOLUTION_GROUP_STRIDE = 32
                RESOLUTION_GROUP_STRIDE = 64  # Resolution grouping stride

                resolution_groups = defaultdict(list)
                for crop_info in all_cropped_images_info:
                    cropped_img = crop_info[0]
                    h, w = cropped_img.shape[:2]
                    # Normalize sizes to stride multiples to reduce group count
                    normalized_h = ((h + RESOLUTION_GROUP_STRIDE) // RESOLUTION_GROUP_STRIDE) * RESOLUTION_GROUP_STRIDE
                    normalized_w = ((w + RESOLUTION_GROUP_STRIDE) // RESOLUTION_GROUP_STRIDE) * RESOLUTION_GROUP_STRIDE
                    group_key = (normalized_h, normalized_w)
                    resolution_groups[group_key].append(crop_info)

                # Batch process each resolution group
                for group_key, group_crops in tqdm(resolution_groups.items(), desc="OCR-det"):

                    # Target size based on max dimensions within the group, rounded to stride
                    max_h = max(crop_info[0].shape[0] for crop_info in group_crops)
                    max_w = max(crop_info[0].shape[1] for crop_info in group_crops)
                    target_h = ((max_h + RESOLUTION_GROUP_STRIDE - 1) // RESOLUTION_GROUP_STRIDE) * RESOLUTION_GROUP_STRIDE
                    target_w = ((max_w + RESOLUTION_GROUP_STRIDE - 1) // RESOLUTION_GROUP_STRIDE) * RESOLUTION_GROUP_STRIDE

                    # Pad all images to a unified size
                    batch_images = []
                    for crop_info in group_crops:
                        img = crop_info[0]
                        h, w = img.shape[:2]
                        # Create a white background of target size
                        padded_img = np.ones((target_h, target_w, 3), dtype=np.uint8) * 255
                        # Paste original image at top-left
                        padded_img[:h, :w] = img
                        batch_images.append(padded_img)

                    # Batch detection
                    det_batch_size = min(len(batch_images), self.batch_ratio * self.ocr_det_base_batch_size)
                    # logger.debug(f"OCR-det batch: {det_batch_size} images, target size: {target_h}x{target_w}")
                    # batch_results = ocr_model.text_detector.batch_predict(batch_images, det_batch_size)
                    batch_results = ocr_model.det_batch_predict(batch_images, det_batch_size)

                    # Process batch results
                    for i, (crop_info, (dt_boxes, elapse)) in enumerate(zip(group_crops, batch_results)):
                        bgr_image, useful_list, ocr_res_list_dict, res, adjusted_mfdetrec_res, pdf_idx = crop_info

                        if dt_boxes is not None and len(dt_boxes) > 0:
                            # Apply core OCR flow steps directly

                            # 1. Sort detection boxes
                            if len(dt_boxes) > 0:
                                dt_boxes_sorted = sorted_boxes(dt_boxes)
                            else:
                                dt_boxes_sorted = []

                            # 2. Merge adjacent boxes
                            if dt_boxes_sorted:
                                dt_boxes_merged = merge_det_boxes(dt_boxes_sorted)
                            else:
                                dt_boxes_merged = []

                            # 3. Update boxes based on formula positions
                            if dt_boxes_merged and adjusted_mfdetrec_res:
                                dt_boxes_final = update_det_boxes(dt_boxes_merged, adjusted_mfdetrec_res)
                            else:
                                dt_boxes_final = dt_boxes_merged

                            # Build OCR result format
                            ocr_res = [box.tolist() if hasattr(box, 'tolist') else box for box in dt_boxes_final]

                            if ocr_res:
                                # Language removed for get_ocr_result_list last parameter
                                ocr_result_list = get_ocr_result_list(
                                    ocr_res, useful_list, ocr_res_list_dict['ocr_enable'], bgr_image, None
                                )

                                ocr_res_list_dict['layout_res'].extend(ocr_result_list)
                                ocr_det_count += 1
                                ocr_det_count_by_pdf[pdf_idx] += 1
        else:
            # Original single-image processing mode
            for ocr_res_list_dict in tqdm(ocr_res_list_all_page, desc="OCR-det Predict"):
                # Process each region requiring OCR
                _lang = ocr_res_list_dict['lang']
                pdf_idx = ocr_res_list_dict['pdf_idx']
                # Fetch OCR results for this language
                ocr_model = atom_model_manager.get_atom_model(
                    atom_model_name=AtomicModel.OCR,
                    ocr_show_log=False,
                    det_db_box_thresh=0.3,
                    ocr_config=self.ocr_config,
                )
                for res in ocr_res_list_dict['ocr_res_list']:
                    # Decide whether to skip when full-page OCR is disabled
                    if not ocr_res_list_dict['ocr_enable']:
                        if (
                                self.use_det_mode == 'txt' or
                                (self.use_det_mode != 'ocr' and not ocr_res_list_dict['ocr_enable'] and not res.get('need_ocr_det'))
                        ):
                            # Skip if text boxes are extracted directly from PDF and OCR is unnecessary
                            continue
                    res.pop('need_ocr_det', None)
                    new_image, useful_list = crop_img(
                        res, ocr_res_list_dict['np_img'], crop_paste_x=50, crop_paste_y=50
                    )
                    # Skip formulas and checkboxes when performing OCR detection
                    adjusted_mfdetrec_res = get_adjusted_mfdetrec_res(
                        ocr_res_list_dict['single_page_mfdetrec_res'] + ocr_res_list_dict['checkbox_res'], useful_list
                    )
                    # OCR-det
                    bgr_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)
                    ocr_res = ocr_model.ocr(
                        bgr_image, mfd_res=adjusted_mfdetrec_res, rec=False
                    )[0]

                    # Combine results
                    if ocr_res:
                        ocr_result_list = get_ocr_result_list(
                            ocr_res, useful_list, ocr_res_list_dict['ocr_enable'],bgr_image, None
                        )

                        ocr_res_list_dict['layout_res'].extend(ocr_result_list)
                        ocr_det_count += 1
                        ocr_det_count_by_pdf[pdf_idx] += 1
        
        ocr_det_time = time.perf_counter() - ocr_det_start
        if ocr_det_count > 0:
            self.perf_stats['ocr_det'] = {'time': ocr_det_time, 'count': ocr_det_count}
            # Collect per-PDF statistics
            for pdf_idx, count in ocr_det_count_by_pdf.items():
                self.pdf_perf_stats[pdf_idx]['ocr_det']['time'] += (ocr_det_time / ocr_det_count) * count
                self.pdf_perf_stats[pdf_idx]['ocr_det']['count'] += count
            logger.info(f"🔍 [OCR-det] Processing time: {ocr_det_time:.3f}s | "
                       f"{ocr_det_count}it | "
                       f"{ocr_det_time/ocr_det_count:.3f} s/it | "
                       f"{ocr_det_count/ocr_det_time:.2f} it/s")
        # =====================================================================

        # =====================================================================
        # Performance measurement: Table Recognition
        # =====================================================================
        table_start = time.perf_counter()
        table_count = 0
        table_count_by_pdf = defaultdict(int)  # Count per PDF
        table_ocr_in_table_count = 0  # Track OCR re-runs inside Table model
        # Table recognition
        if self.table_enable and len(table_res_list_all_page) > 0:
            # Group by page
            table_res_list_grouped_page = {}
            for x in table_res_list_all_page:
                table_res_list_grouped_page.setdefault(x["page_idx"], []).append(x)
            # Total number of tables
            total_tables = sum(len(tables) for tables in table_res_list_grouped_page.values())
            
            # Optimization: instantiate Table model once (shared across languages)
            table_model = atom_model_manager.get_atom_model(
                atom_model_name='table',
                ocr_config=self.ocr_config,
                table_config=self.table_config,
            )
            
            with tqdm(total=total_tables, desc="Table Predict") as pbar:
                for page_idx, table_list in table_res_list_grouped_page.items():
                    page_dict = pdf_dict_list[page_idx]
                    scale = scale_list[page_idx]
                    for table_res_dict in table_list:
                        _lang = table_res_dict['lang']
                        pdf_idx = table_res_dict['pdf_idx']
                        useful_list = table_res_dict['useful_list']
                        # Skip formulas and checkboxes during OCR detection
                        adjusted_mfdetrec_res = get_adjusted_mfdetrec_res(
                            table_res_dict['single_page_mfdetrec_res'] + table_res_dict['checkbox_res'],
                            useful_list, return_text=True
                        )

                        # Optimization: always prepare OCR results to avoid duplicate runs inside Table model
                        ocr_result = None
                        ocr_res = []
                        
                        # Decide whether to try extracting text directly from PDF
                        should_extract_from_pdf = (not self.table_force_ocr and not table_res_dict['ocr_enable'])
                        
                        if should_extract_from_pdf:
                            # if self.use_det_mode != 'ocr':
                            #     # Extract text blocks directly from PDF (disabled because some tables perform poorly), supports 270/90 degree tables
                            #     ocr_res, most_angle = txt_spans_bbox_extract_table(page_dict, table_res_dict, scale=scale)
                            pass
                        
                        # Perform OCR detection if PDF extraction failed or OCR is needed
                        if not ocr_res:
                            # Run OCR detection to identify text boxes
                            ocr_model = atom_model_manager.get_atom_model(
                                atom_model_name=AtomicModel.OCR,
                                ocr_show_log=False,
                                det_db_box_thresh=0.3,
                                ocr_config=self.ocr_config,
                                enable_merge_det_boxes=False,
                            )
                            new_table_image = cv2.cvtColor(table_res_dict['table_img'], cv2.COLOR_RGB2BGR)
                            ocr_res = ocr_model.ocr(new_table_image, mfd_res=adjusted_mfdetrec_res, rec=False)[0]
                            # Handle None safely
                            if ocr_res is None:
                                ocr_res = []
                            # Vote for text line angle from PDF
                            most_angle = txt_most_angle_extract_table(page_dict, table_res_dict, scale=scale)
                            if most_angle in [90, 270] and ocr_res:
                                table_res_dict['table_img'], ocr_res = rotate_image_and_boxes(
                                    np.asarray(table_res_dict["table_img"]),
                                    ocr_res,
                                    most_angle
                                )
                        
                        # Always prepare OCR results (from PDF extraction or OCR detection)
                        if ocr_res and len(ocr_res) > 0:
                            ocr_spans = get_ocr_result_list_table(ocr_res, useful_list, scale)
                            poly = table_res_dict['table_res']['poly']
                            table_bboxes = [[int(poly[0]/scale), int(poly[1]/scale), int(poly[4]/scale), int(poly[5]/scale)
                                                , None, None, None,'text', None, None, None, None, 1]]
                            # Extract table text from PDF if allowed
                            if should_extract_from_pdf:
                                txt_spans_extract(page_dict, ocr_spans, table_res_dict['table_img'], scale, table_bboxes,[])
                            # Final OCR result to prevent another OCR run inside Table model
                            if ocr_spans:
                                ocr_result = [list(x) for x in zip(*[[item['ori_bbox'], item['content'], item['score']] for item in ocr_spans])]
                            else:
                                ocr_result = [[], [], []]  # Empty result
                        else:
                            # Important: initialize empty lists to prevent OCR rerun inside Table model
                            ocr_result = [[], [], []]  # [boxes, texts, scores]
                            logger.debug(f"Table {table_count+1}: No OCR detection results; passing empty result")

                        # Debug: track OCR result status
                        if ocr_result is None:
                            table_ocr_in_table_count += 1
                            logger.warning(f"⚠️  Table {table_count+1}: ocr_result is None; OCR reran inside Table model!")
                        elif isinstance(ocr_result, list) and len(ocr_result) > 0 and len(ocr_result[0]) == 0:  # Empty OCR result
                            logger.debug(f"📋 Table {table_count+1}: No OCR results (text-free table or image-only)")
                        elif isinstance(ocr_result, list) and len(ocr_result) > 0:
                            logger.debug(f"✅ Table {table_count+1}: {len(ocr_result[0])} OCR boxes passed")
                        else:
                            logger.debug(f"📋 Table {table_count+1}: OCR result format check: {type(ocr_result)}")
                        
                        # Extract images inside the table from PDF
                        fill_image_res = extract_table_fill_image(page_dict, table_res_dict, scale=scale)
                        
                        # Table processing start log
                        table_predict_start = time.perf_counter()
                        logger.debug(f"🔄 Table {table_count+1} processing started...")
                        
                        html_code, table_cell_bboxes, logic_points, elapse = table_model.predict(table_res_dict['table_img'], ocr_result
                                                                                                 , fill_image_res, adjusted_mfdetrec_res, self.skip_text_in_image, self.use_img2table)
                        
                        table_predict_time = time.perf_counter() - table_predict_start
                        logger.debug(f"✅ Table {table_count+1} processing complete: {table_predict_time:.2f}s")
                        # Validate return content
                        if html_code:
                            # Check for image fallback marker
                            if "data-fallback='image'" in html_code:
                                table_res_dict['table_res']['html'] = html_code
                                logger.info(f"Table {table_count+1}: using image fallback")
                            # Ensure html_code contains table tags
                            elif '<table>' in html_code and '</table>' in html_code:
                                # Store trimmed HTML table content
                                start_index = html_code.find('<table>')
                                end_index = html_code.rfind('</table>') + len('</table>')
                                table_res_dict['table_res']['html'] = html_code[start_index:end_index]
                                # Add formula and image boxes for layout drawing
                                latex_boxes = [t["bbox"] for t in table_res_dict['single_page_mfdetrec_res'] + table_res_dict['checkbox_res'] if "bbox" in t]
                                if latex_boxes:
                                    table_res_dict['table_res']['latex_boxes'] = [[int(coord / scale) for coord in bbox] for bbox in latex_boxes]
                                img_boxes = [t["ori_bbox"] for t in fill_image_res if "bbox" in t]
                                if img_boxes:
                                    table_res_dict['table_res']['img_boxes'] = [[int(coord / scale) for coord in bbox] for bbox in img_boxes]
                            else:
                                logger.warning(
                                    'table recognition processing fails, not found expected HTML table end'
                                )
                        else:
                            logger.warning(
                                'table recognition processing fails, not get html return'
                            )
                        pbar.update(1)  # Update after each table
                        table_count += 1
                        table_count_by_pdf[pdf_idx] += 1
        
        table_time = time.perf_counter() - table_start
        if table_count > 0:
            self.perf_stats['table'] = {'time': table_time, 'count': table_count}
            # Collect per-PDF statistics
            for pdf_idx, count in table_count_by_pdf.items():
                self.pdf_perf_stats[pdf_idx]['table']['time'] += (table_time / table_count) * count
                self.pdf_perf_stats[pdf_idx]['table']['count'] += count
            logger.info(f"📋 [Table] Processing time: {table_time:.3f}s | "
                       f"{table_count}it | "
                       f"{table_time/table_count:.3f} s/it | "
                       f"{table_count/table_time:.2f} it/s")
            if table_ocr_in_table_count > 0:
                logger.warning(f"⚠️  OCR reran inside Table model: {table_ocr_in_table_count}/{table_count} cases "
                             f"({table_ocr_in_table_count/table_count*100:.1f}%) - performance impact")
        elif self.table_enable:
            logger.info("📋 [Table] No tables to process; skipped")
        # =====================================================================

        # OCR rec
        # Collect items needing text recognition (language agnostic)
        need_ocr_list = []
        img_crop_list = []

        for page_idx, layout_res in enumerate(images_layout_res):
            for layout_res_item in layout_res:
                if layout_res_item['category_id'] in [15]:
                    if 'np_img' in layout_res_item:
                        # Preserve pdf_idx
                        layout_res_item['pdf_idx'] = pdf_indices[page_idx]
                        need_ocr_list.append(layout_res_item)
                        img_crop_list.append(layout_res_item['np_img'])

                        # Remove fields after adding to list
                        layout_res_item.pop('np_img')
                        layout_res_item.pop('lang', None)  # Remove lang if present

        # =====================================================================
        # Performance measurement: OCR Recognition
        # =====================================================================
        ocr_rec_start = time.perf_counter()
        ocr_rec_count = 0
        ocr_rec_count_by_pdf = defaultdict(int)  # Count per PDF
        if len(img_crop_list) > 0:
            # Fetch OCR model once (language agnostic)
            ocr_model = atom_model_manager.get_atom_model(
                atom_model_name=AtomicModel.OCR,
                det_db_box_thresh=0.3,
                ocr_config=self.ocr_config,
            )
            ocr_res_list = ocr_model.ocr(img_crop_list, det=False, tqdm_enable=True)[0]
            
            # Ensure counts match
            assert len(ocr_res_list) == len(need_ocr_list), \
                f'ocr_res_list: {len(ocr_res_list)}, need_ocr_list: {len(need_ocr_list)}'

            # Process OCR results
            for index, layout_res_item in enumerate(need_ocr_list):
                ocr_text, ocr_score = ocr_res_list[index]
                pdf_idx = layout_res_item.pop('pdf_idx', 0)  # Retrieve and remove pdf_idx
                layout_res_item['text'] = ocr_text
                layout_res_item['score'] = float(f"{ocr_score:.3f}")
                if ocr_score < OcrConfidence.min_confidence:
                    layout_res_item['category_id'] = 16
                else:
                    layout_res_bbox = [layout_res_item['poly'][0], layout_res_item['poly'][1],
                                       layout_res_item['poly'][4], layout_res_item['poly'][5]]
                    layout_res_width = layout_res_bbox[2] - layout_res_bbox[0]
                    layout_res_height = layout_res_bbox[3] - layout_res_bbox[1]
                    if ocr_text in ['（204号', '（20', '（2', '（2号', '（20号', '号', '（204'] and ocr_score < 0.8 and layout_res_width < layout_res_height:
                        layout_res_item['category_id'] = 16
                
                ocr_rec_count += 1
                ocr_rec_count_by_pdf[pdf_idx] += 1
        
        ocr_rec_time = time.perf_counter() - ocr_rec_start
        if ocr_rec_count > 0:
            self.perf_stats['ocr_rec'] = {'time': ocr_rec_time, 'count': ocr_rec_count}
            # Collect per-PDF statistics
            for pdf_idx, count in ocr_rec_count_by_pdf.items():
                self.pdf_perf_stats[pdf_idx]['ocr_rec']['time'] += (ocr_rec_time / ocr_rec_count) * count
                self.pdf_perf_stats[pdf_idx]['ocr_rec']['count'] += count
            logger.info(f"✍️  [OCR-rec] Processing time: {ocr_rec_time:.3f}s | "
                       f"{ocr_rec_count}it | "
                       f"{ocr_rec_time/ocr_rec_count:.3f} s/it | "
                       f"{ocr_rec_count/ocr_rec_time:.2f} it/s")
        # =====================================================================

        # =====================================================================
        # Performance summary
        # =====================================================================
        self._print_performance_summary()
        # =====================================================================
        
        # Convert and return per-PDF performance statistics as dictionary
        pdf_perf_dict = dict(self.pdf_perf_stats)
        
        return images_layout_res, pdf_perf_dict
    
    def _print_performance_summary(self):
        """Print performance measurement summary"""
        if not self.perf_stats:
            return
        
        logger.info("=" * 80)
        logger.info("📈 Performance Summary")
        logger.info("=" * 80)
        
        # Model loading time
        model_load_times = getattr(self.model, 'model_load_times', None)
        if model_load_times:
            total_load = sum(model_load_times.values())
            logger.info(f"🔧 Model Loading  | {total_load:7.2f}s total")
            for name, elapsed in model_load_times.items():
                logger.info(f"     {name:<12s} | {elapsed:7.2f}s")
            logger.info("-" * 80)
        
        total_time = 0
        model_info = []
        
        # Collect per-model info
        model_names = {
            'layout': '📊 Layout  ',
            'formula': '📐 Formula ',
            'pdf_det': '📄 PDF-det ',
            'ocr_det': '🔍 OCR-det ',
            'table': '📋 Table   ',
            'ocr_rec': '✍️  OCR-rec '
        }
        
        # Engine mapping (pdf_det, ocr_det, ocr_rec use OCR engine)
        engine_mapping = {
            'layout': self.engines.get('layout', 'unknown'),
            'formula': self.engines.get('formula', 'unknown'),
            'pdf_det': self.engines.get('ocr', 'unknown'),
            'ocr_det': self.engines.get('ocr', 'unknown'),
            'table': self.engines.get('table', 'unknown'),
            'ocr_rec': self.engines.get('ocr', 'unknown')
        }
        
        for key in ['layout', 'formula', 'pdf_det', 'ocr_det', 'table', 'ocr_rec']:
            if key in self.perf_stats:
                stats = self.perf_stats[key]
                time_val = stats['time']
                count = stats['count']
                total_time += time_val
                s_per_it = time_val / count if count > 0 else 0
                it_per_s = count / time_val if time_val > 0 else 0
                model_info.append({
                    'name': model_names.get(key, key),
                    'engine': engine_mapping.get(key, 'unknown'),
                    'time': time_val,
                    'count': count,
                    's_per_it': s_per_it,
                    'it_per_s': it_per_s,
                    'percentage': 0  # Placeholder; computed below
                })
        
        # Compute percentages
        for info in model_info:
            info['percentage'] = (info['time'] / total_time * 100) if total_time > 0 else 0
        
        # Print overall stats
        for info in model_info:
            logger.info(
                f"{info['name']} [{info['engine']:>12s}] | {info['time']:7.2f}s ({info['percentage']:5.1f}%) | "
                f"{int(info['count']):4d}it | {info['s_per_it']:.3f} s/it | {info['it_per_s']:6.2f} it/s"
            )
        
        logger.info("-" * 80)
        logger.info(f"🔥 Total processing time: {total_time:.2f}s")
        logger.info("=" * 80)
        
        # Print per-PDF stats
        if self.pdf_perf_stats:
            logger.info("")
            logger.info("=" * 80)
            logger.info("📊 Performance by PDF")
            logger.info("=" * 80)
            
            for pdf_idx in sorted(self.pdf_perf_stats.keys()):
                pdf_stats = self.pdf_perf_stats[pdf_idx]
                pdf_total_time = sum(model['time'] for model in pdf_stats.values())
                
                if pdf_total_time == 0:
                    continue
                
                logger.info(f"\n📄 PDF #{pdf_idx} (total {pdf_total_time:.2f}s)")
                logger.info("-" * 80)
                
                # Collect per-model stats for the PDF
                pdf_model_info = []
                for key in ['layout', 'formula', 'pdf_det', 'ocr_det', 'table', 'ocr_rec']:
                    if key in pdf_stats and pdf_stats[key]['time'] > 0:
                        time_val = pdf_stats[key]['time']
                        count = pdf_stats[key]['count']
                        percentage = (time_val / pdf_total_time * 100) if pdf_total_time > 0 else 0
                        s_per_it = time_val / count if count > 0 else 0
                        it_per_s = count / time_val if time_val > 0 else 0
                        
                        pdf_model_info.append({
                            'name': model_names.get(key, key),
                            'engine': engine_mapping.get(key, 'unknown'),
                            'time': time_val,
                            'count': count,
                            'percentage': percentage,
                            's_per_it': s_per_it,
                            'it_per_s': it_per_s
                        })
                
                # Output
                for info in pdf_model_info:
                    logger.info(
                        f"{info['name']} [{info['engine']:>12s}] | {info['time']:7.2f}s ({info['percentage']:5.1f}%) | "
                        f"{int(info['count']):4d}it | {info['s_per_it']:.3f} s/it | {info['it_per_s']:6.2f} it/s"
                    )
            
            logger.info("=" * 80)
