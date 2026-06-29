import html
import re
from dataclasses import dataclass
from typing import Optional, Tuple

import cv2
import numpy as np
from loguru import logger

from rapid_doc.backend.pipeline.pipeline_middle_json_mkcontent import inline_left_delimiter, inline_right_delimiter
from rapid_doc.model.table.rapid_table_self import ModelType, RapidTable, RapidTableInput
from rapid_doc.utils.boxbase import is_in
from rapid_doc.utils.config_reader import get_device
from rapid_doc.utils.ocr_utils import points_to_bbox, bbox_to_points

TABLE_IMAGE_FALLBACK_HTML = "<table data-fallback='image'></table>"


@dataclass
class UnetResult:
    """UNET 추론 결과 컨테이너."""
    polygons: Optional[np.ndarray]
    rotated_polygons: Optional[np.ndarray]
    upscaled_bgr: np.ndarray


def escape_html(input_string):
    """Escape HTML Entities."""
    return html.escape(input_string)


class RapidTableModel(object):
    def __init__(self, ocr_engine, table_config=None, use_async=False,
                 device_ids=None, device_lock=None):
        if table_config is None:
            table_config = {}
        self.use_async = use_async
        device = get_device()
        engine_cfg = None
        if device.startswith('cuda'):
            device_id = int(device.split(':')[1]) if ':' in device else 0  # GPU 编号
            engine_cfg = {'use_cuda': True, "cuda_ep_cfg.device_id": device_id}
        self.model_type = ModelType.UNET
        self.ocr_engine = ocr_engine

        engine_type = table_config.get("engine_type")
        input_args = RapidTableInput(
            model_type=ModelType.UNET, use_ocr=False,
            model_dir_or_path=table_config.get("unet.model_dir_or_path"),
            engine_cfg=engine_cfg or {},
            engine_type=engine_type,
            use_async=self.use_async,
            device_ids=device_ids,
            device_lock=device_lock,
        )
        self.table_model = RapidTable(input_args)

    def prepare_image(self, image) -> Tuple[np.ndarray, bool]:
        """이미지 전처리 + Portrait 감지 → (bgr_image, is_rotated)."""
        bgr_image = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
        img_height, img_width = bgr_image.shape[:2]
        img_aspect_ratio = img_height / img_width if img_width > 0 else 1.0
        img_is_portrait = img_aspect_ratio > 1.2

        is_rotated = False
        if img_is_portrait:
            try:
                det_res = self.ocr_engine.ocr(bgr_image, rec=False)[0]
            except Exception:
                det_res = None
            if det_res:
                vertical_count = 0
                for box_ocr_res in det_res:
                    p1, p2, p3, p4 = box_ocr_res
                    width = p3[0] - p1[0]
                    height = p3[1] - p1[1]
                    aspect_ratio = width / height if height > 0 else 1.0
                    if aspect_ratio < 0.8:
                        vertical_count += 1
                if vertical_count >= len(det_res) * 0.3:
                    is_rotated = True

            if is_rotated:
                image = cv2.rotate(np.asarray(image), cv2.ROTATE_90_CLOCKWISE)
                bgr_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        return bgr_image, is_rotated

    def run_unet(self, bgr_image: np.ndarray, fill_image_res=None) -> UnetResult:
        """UNET 추론만 실행 → UnetResult."""
        work_img = bgr_image
        if fill_image_res:
            work_img = bgr_image.copy()
            for fill_image in fill_image_res:
                bbox = points_to_bbox(fill_image['ocr_bbox'])
                cv2.rectangle(
                    work_img,
                    (int(bbox[0]), int(bbox[1])),
                    (int(bbox[2]), int(bbox[3])),
                    (255, 255, 255),
                    thickness=-1,
                )
        h, w = work_img.shape[:2]
        upscaled_bgr = cv2.resize(work_img, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)
        polygons, rotated_polygons = self.table_model.table_structure.run_structure_only(
            upscaled_bgr
        )
        return UnetResult(
            polygons=polygons,
            rotated_polygons=rotated_polygons,
            upscaled_bgr=upscaled_bgr,
        )

    def run_ocr(self, bgr_image: np.ndarray, mfd_res=None) -> Optional[list]:
        """테이블용 OCR (det+rec) → [boxes, texts, scores] 또는 None."""
        ocr_result = self.ocr_engine.ocr(bgr_image, mfd_res=mfd_res)[0]
        if ocr_result:
            return [
                list(x)
                for x in zip(
                    *[[item[0], item[1][0], item[1][1]] for item in ocr_result]
                )
            ]
        return None

    def build_html(
        self,
        unet_result: UnetResult,
        ocr_result: Optional[list],
        fill_image_res=None,
        mfd_res=None,
        skip_text_in_image=True,
        use_img2table=False,
    ) -> Tuple[Optional[str], Optional[np.ndarray], Optional[np.ndarray], Optional[float]]:
        """UNET + OCR 결과를 결합하여 HTML 생성."""
        if not ocr_result:
            return "", None, None, 0.0

        # fill_image_res → ocr_result에 이미지 항목 추가 + 겹치는 OCR 제거
        if fill_image_res:
            for fill_image in fill_image_res:
                ocr_result[0].append(fill_image['ocr_bbox'])
                ocr_result[1].append(fill_image['uuid'])
                ocr_result[2].append(1)
                if skip_text_in_image:
                    delete_indices = []
                    for idx, ocr in enumerate(ocr_result[0][:-1]):
                        if is_in(points_to_bbox(ocr), points_to_bbox(fill_image['ocr_bbox'])):
                            delete_indices.append(idx)
                    for idx in sorted(delete_indices, reverse=True):
                        del ocr_result[0][idx]
                        del ocr_result[1][idx]
                        del ocr_result[2][idx]

        # mfd_res → ocr_result에 수식/체크박스 추가
        if mfd_res:
            for mfd in mfd_res:
                if mfd.get('latex'):
                    ocr_result[1].append(
                        f"{inline_left_delimiter}{mfd['latex']}{inline_right_delimiter}"
                    )
                elif mfd.get('checkbox'):
                    ocr_result[1].append(mfd['checkbox'])
                else:
                    continue
                ocr_result[0].append(bbox_to_points(mfd['bbox']))
                ocr_result[2].append(1)

        upscaled_bgr = unet_result.upscaled_bgr
        scaled_ocr = self._scale_ocr_result(ocr_result, 2)

        # img2table 시도 (explicit request)
        if use_img2table:
            try:
                html_code = self._run_img2table(upscaled_bgr, scaled_ocr)
                if html_code:
                    return html_code, None, None, None
            except ImportError:
                raise ValueError(
                    "Could not import img2table python package. "
                    "Please install it with `pip install img2table`."
                )
            except Exception as e:
                logger.exception(e)

        # UNET 결과 사용
        if unet_result.polygons is None:
            return "", None, None, 0.0

        # match_ocr_cell expects [(box, text, score), ...] (zipped tuples)
        zipped_ocr = list(zip(scaled_ocr[0], scaled_ocr[1], scaled_ocr[2]))

        try:
            table_results = self.table_model.table_structure.build_from_structure(
                upscaled_bgr,
                unet_result.polygons,
                unet_result.rotated_polygons,
                zipped_ocr,
            )
            html_code = table_results.pred_html
            table_cell_bboxes = table_results.cell_bboxes
            logic_points = table_results.logic_points
            elapse = table_results.elapse

            if html_code and self._is_single_column_table(html_code):
                logger.warning("UNET produced single-column table, retrying with img2table")
                try:
                    fallback_html = self._run_img2table(upscaled_bgr, scaled_ocr)
                    if fallback_html:
                        return fallback_html, None, None, elapse
                except Exception as e:
                    logger.warning(f"img2table fallback also failed: {e}")
                logger.warning("Both UNET and img2table failed, falling back to table image")
                return TABLE_IMAGE_FALLBACK_HTML, None, None, elapse

            return html_code, table_cell_bboxes, logic_points, elapse
        except Exception as e:
            logger.exception(e)
            return "", None, None, 0.0

    def predict(self, image, ocr_result=None, fill_image_res=None,
                mfd_res=None, skip_text_in_image=True, use_img2table=False):
        """하위 호환 API — 내부적으로 서브 메서드를 순차 호출."""
        bgr_image, is_rotated = self.prepare_image(image)
        if not ocr_result:
            ocr_result = self.run_ocr(bgr_image, mfd_res)
        unet_result = self.run_unet(bgr_image, fill_image_res)
        return self.build_html(
            unet_result, ocr_result, fill_image_res,
            mfd_res, skip_text_in_image, use_img2table,
        )

    @staticmethod
    def _scale_ocr_result(ocr_result, scale):
        """Scale OCR bounding box coordinates by the given factor."""
        if not ocr_result or len(ocr_result) < 3:
            return ocr_result
        boxes, texts, scores = ocr_result
        scaled_boxes = [[[p[0] * scale, p[1] * scale] for p in box] for box in boxes]
        return [scaled_boxes, texts, scores]

    @staticmethod
    def _is_single_column_table(html_code):
        """Check if UNET produced a degenerate single-column table (all rows have 1 cell)."""
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html_code, re.DOTALL)
        if len(rows) < 3:
            return False
        for row in rows:
            cells = re.findall(r'<td[^>]*>', row)
            if len(cells) != 1:
                return False
        return True

    def _run_img2table(self, bgr_image, ocr_result):
        """Run img2table on the given image. Returns HTML string or None."""
        from rapid_doc.model.table.img2table_self.image import Image
        from rapid_doc.model.table.img2table_self.RapidOcrTable import RapidOcrTable

        opencv_ocr = RapidOcrTable(ocr_result)
        doc = Image(src=bgr_image)
        extracted_tables = doc.extract_tables(
            ocr=opencv_ocr,
            implicit_rows=False,
            implicit_columns=False,
            borderless_tables=False,
            min_confidence=50
        )
        if extracted_tables:
            return "<html><body>" + extracted_tables[0].html + "</body></html>"
        return None

