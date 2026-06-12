"""
True Async Pipeline Processing Module
CPU-HW Overlap Analysis using DX Engine run_async() + register_callback

    Stage DAG (Batch submission per stage):
    Stage 1: Layout      - Parallel run_async for all pages
    Stage 2: Area Plan   - Classify layout results into OCR/Table/Formula (CPU)
    Stage 4: PDF-det     - Direct text extraction (No model, CPU) [Pre-req]
    Stage 3||5: Formula(CPU) + OCR-det(NPU) - Parallel execution
    Stage 6: Table       - Sequential processing for all tables (Incl. OCR-det results)
    Stage 7: OCR-rec     - Batch recognition for all text crops

StreamingPipeline:
Runs stages as independent threads; passes PageContext via queue.Queue.
Optimizes latency via assembly-line processing (per-page).
"""

import os
import queue
import threading
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict

import cv2
import numpy as np
from loguru import logger
from tqdm import tqdm

from .model_init import MineruPipelineModel, AtomModelSingleton
from .pipeline_analyze import custom_model_init
from .model_list import AtomicModel
from ...utils.config_reader import get_formula_enable, get_table_enable, get_device
from ...utils.enum_class import CategoryId
from ...utils.model_utils import crop_img, get_res_list_from_layout_res, clean_memory
from ...utils.ocr_utils import (
    merge_det_boxes, update_det_boxes, sorted_boxes,
    get_adjusted_mfdetrec_res, get_ocr_result_list,
    OcrConfidence, get_ocr_result_list_table,
)
from ...utils.span_pre_proc import (
    txt_spans_bbox_extract, extract_table_fill_image, txt_most_angle_extract_table,
)
from ...utils.boxbase import rotate_image_and_boxes
from ...utils.checkbox_det_cls import checkbox_predict

# ─── 상수 ────────────────────────────────────────────────────────────────────
_TABLE_OPEN_TAG = '<table>'
_TABLE_CLOSE_TAG = '</table>'


# ─────────────────────────────────────────────────────────────────────────────
# 페이지 컨텍스트: 한 페이지의 모든 처리 상태를 추적
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class PageContext:
    """파이프라인을 흐르는 페이지 단위 상태 객체"""

    # 식별자
    pdf_idx: int
    page_idx: int

    # 입력 데이터
    np_img: Optional[np.ndarray] = None
    scale: float = 1.0
    ocr_enable: bool = False
    lang: str = "ch"
    page_dict: Optional[dict] = None

    # Stage 1: Layout 결과
    layout_res: list = field(default_factory=list)

    # Stage 2: 영역 후보 (layout 해석 결과)
    ocr_candidates: list = field(default_factory=list)   # OCR 후보 영역 (res dict)
    table_candidates: list = field(default_factory=list) # 테이블 후보 (table_img 포함)
    formula_regions: list = field(default_factory=list)  # 수식 검출 영역 (mfdetrec_res)
    formula_crops: list = field(default_factory=list)    # 크롭된 수식 이미지
    checkbox_res: list = field(default_factory=list)     # 체크박스 결과


# ─────────────────────────────────────────────────────────────────────────────
# 진정한 비동기 파이프라인
# ─────────────────────────────────────────────────────────────────────────────

class TrueAsyncPipeline:
    """
    DX Engine run_async() 기반 파이프라인.

    핵심 원칙:
      • 각 스테이지는 모든 페이지의 작업을 모아 일제히 제출한 뒤 전체 결과를 수집한다.
      • use_async=True 플래그가 설정된 경우, DX 하드웨어는 여러 요청을 동시에 처리한다.
      • CPU 측 전·후처리는 하드웨어 추론과 최대한 오버랩한다.
    """

    def __init__(
        self,
        model: MineruPipelineModel,
        formula_enable: bool = True,
        table_enable: bool = True,
        use_det_mode: str = 'auto',
        layout_config: dict = None,
        ocr_config: dict = None,
        formula_config: dict = None,
        table_config: dict = None,
        checkbox_config: dict = None,
        verbose: bool = False,
    ):
        self.model = model
        self.formula_enable = get_formula_enable(formula_enable)
        self.table_enable = get_table_enable(table_enable)
        self.use_det_mode = use_det_mode
        self.layout_config = layout_config or {}
        self.ocr_config = ocr_config or {}
        self.formula_config = formula_config or {}
        self.table_config = table_config or {}
        self.checkbox_config = checkbox_config or {}
        self.verbose = verbose

        # 세부 옵션
        self.checkbox_enable = self.checkbox_config.get("checkbox_enable", False)
        self.formula_rec_enable = self.formula_config.get("formula_rec_enable", True)
        self.formula_level = self.formula_config.get("formula_level", 2)
        self.table_force_ocr = self.table_config.get("force_ocr", False)
        self.skip_text_in_image = self.table_config.get("skip_text_in_image", True)
        self.use_img2table = self.table_config.get("use_img2table", False)

        self.atom_model_manager = AtomModelSingleton()

        # 성능 통계
        self.perf_stats: Dict[str, Dict] = {}
        self.pdf_perf_stats = defaultdict(lambda: defaultdict(lambda: {'time': 0.0, 'count': 0}))

    # ─────────────────────────────── public ──────────────────────────────────

    def run(
        self,
        images_with_extra_info: List[Tuple],
    ) -> Tuple[List[Any], Dict]:
        """
        파이프라인 전체 실행.

        Returns:
            (images_layout_res 리스트, pdf_perf_stats 딕셔너리)
        """
        total = len(images_with_extra_info)
        logger.info(f"🚀 TrueAsyncPipeline: {total} pages")
        t_total = time.perf_counter()

        contexts = self._build_page_contexts(images_with_extra_info)

        self._stage_layout(contexts)            # Stage 1
        self._stage_plan_regions(contexts)      # Stage 2
        self._stage_pdf_det(contexts)           # Stage 4 (선행 — OCR-det의 skip 플래그 설정)
        self._run_parallel_formula_ocr_det(contexts)  # Stage 3∥5 병렬
        if self.table_enable:
            self._stage_table(contexts)         # Stage 6
        self._stage_ocr_rec(contexts)           # Stage 7

        elapsed = time.perf_counter() - t_total
        self._print_perf_summary(total, elapsed, "TrueAsyncPipeline")

        results = [ctx.layout_res for ctx in contexts]
        return results, dict(self.pdf_perf_stats)

    # ─────────────────────────── 입력 파싱 ───────────────────────────────────

    def _build_page_contexts(self, items: List[Tuple]) -> List[PageContext]:
        contexts = []
        for item in items:
            if len(item) == 7:
                img, scale, ocr_enable, lang, page_dict, pdf_idx, page_idx = item
            else:
                img, scale, ocr_enable, lang, page_dict = item
                pdf_idx, page_idx = 0, len(contexts)

            np_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            contexts.append(PageContext(
                pdf_idx=pdf_idx,
                page_idx=page_idx,
                np_img=np_img,
                scale=scale,
                ocr_enable=ocr_enable,
                lang=lang,
                page_dict=page_dict,
            ))
        return contexts

    # ─────────────────────────── Stage 1: Layout ─────────────────────────────

    def _stage_layout(self, contexts: List[PageContext]) -> None:
        """
        모든 페이지 이미지를 layout_model.batch_predict에 일제히 전달.
        use_async=True 모델에서는 내부적으로 run_async를 페이지별로 제출하고
        callback을 통해 결과를 수집하므로 하드웨어가 병렬 처리한다.
        """
        n = len(contexts)
        logger.info(f"[Stage 1/7] Layout — {n} pages")
        t0 = time.perf_counter()

        np_images = [ctx.np_img for ctx in contexts]
        batch_size = self.layout_config.get("batch_num", 1)

        all_layout_res = self.model.layout_model.batch_predict(np_images, batch_size)

        for ctx, layout_res in zip(contexts, all_layout_res):
            # formula_level 필터링
            if self.formula_enable and self.formula_level == 1:
                layout_res = [item for item in layout_res if item["category_id"] != 13]
            ctx.layout_res = layout_res

        elapsed = time.perf_counter() - t0
        self._record_perf('layout', elapsed, n, contexts)
        logger.info(f"   ↳ {elapsed:.3f}s | {n / max(elapsed, 0.001):.2f} it/s")

    # ─────────────────────────── Stage 2: 영역 플래닝 ────────────────────────

    def _stage_plan_regions(self, contexts: List[PageContext]) -> None:
        """
        layout 결과를 해석해 OCR 후보·테이블 후보·수식 영역·체크박스를 분류한다 (CPU only).
        """
        for ctx in contexts:
            ocr_candidates, table_candidates, formula_regions = get_res_list_from_layout_res(
                ctx.layout_res, ctx.np_img
            )

            # 체크박스 검출
            checkbox_res = []
            if self.checkbox_enable:
                checkbox_img = cv2.cvtColor(ctx.np_img, cv2.COLOR_RGB2BGR)
                checkbox_res = checkbox_predict(checkbox_img)
                for res in checkbox_res:
                    poly = [
                        res['bbox'][0], res['bbox'][1],
                        res['bbox'][2], res['bbox'][1],
                        res['bbox'][2], res['bbox'][3],
                        res['bbox'][0], res['bbox'][3],
                    ]
                    ctx.layout_res.append({
                        'bbox': res['bbox'], 'poly': poly,
                        'category_id': CategoryId.CheckBox,
                        'checkbox': res['text'], 'score': 0.9,
                    })

            ctx.ocr_candidates = list(ocr_candidates)
            ctx.checkbox_res = checkbox_res
            # formula_level=2: 행간 수식은 LaTeX 추론 대상에서 제외
            if self.formula_level == 2:
                formula_regions_for_latex = [
                    fr for fr in formula_regions
                    if fr.get("category_id") not in (
                        CategoryId.InterlineEquation_Layout,
                        CategoryId.InterlineEquation_YOLO,
                    )
                ]
            else:
                formula_regions_for_latex = list(formula_regions)
            ctx.formula_regions = formula_regions_for_latex

            # 테이블 후보: crop 이미지 포함
            ctx.table_candidates = []
            for tr in table_candidates:
                table_img, useful_list = crop_img(tr, ctx.np_img)
                ctx.table_candidates.append({
                    'table_res': tr,
                    'table_img': table_img,
                    'useful_list': useful_list,
                    'ocr_enable': ctx.ocr_enable,
                })

            # 수식 crop 이미지
            ctx.formula_crops = []
            for fr in ctx.formula_regions:
                latex_img, _ = crop_img(fr, ctx.np_img)
                ctx.formula_crops.append(latex_img)

    # ─────────────────────────── Stage 3: Formula ────────────────────────────

    def _stage_formula(self, contexts: List[PageContext]) -> None:
        """
        모든 페이지의 수식 crop 이미지를 모아 formula_model.batch_predict로 일괄 처리.
        formula_regions 항목에 latex 필드를 in-place로 채운다.
        """
        # (ctx, formula_region_ref, crop_img) 수집
        all_items = []
        all_crops = []
        for ctx in contexts:
            for fr_dict, crop in zip(ctx.formula_regions, ctx.formula_crops):
                all_items.append(fr_dict)
                all_crops.append(crop)

        if not all_crops:
            logger.info("[Stage 3/7] Formula — 없음 (skip)")
            return

        n = len(all_crops)
        logger.info(f"[Stage 3/7] Formula — {n} regions")
        t0 = time.perf_counter()

        batch_size = self.formula_config.get("batch_num", 1)
        latex_results = self.model.formula_model.batch_predict(all_crops, batch_size=batch_size)

        success = 0
        for fr_dict, latex in zip(all_items, latex_results):
            if latex:
                fr_dict['latex'] = latex
                success += 1

        elapsed = time.perf_counter() - t0
        self._record_perf('formula', elapsed, n, contexts)
        logger.info(f"   ↳ {elapsed:.3f}s | {n / max(elapsed, 0.001):.2f} it/s | success={success}/{n}")

    # ─────────────────────────── Stage 4: PDF-det ────────────────────────────

    def _stage_pdf_det(self, contexts: List[PageContext]) -> None:
        """
        텍스트 기반 PDF에서 텍스트 위치를 직접 추출한다 (모델 추론 없음, CPU only).
        스캔 PDF(ocr_enable=True) 또는 ocr 강제 모드면 건너뛴다.
        """
        if self.use_det_mode == 'ocr':
            return

        t0 = time.perf_counter()
        count = 0

        for ctx in contexts:
            if ctx.ocr_enable:
                continue
            for res in ctx.ocr_candidates:
                new_image, useful_list = crop_img(
                    res, ctx.np_img, crop_paste_x=50, crop_paste_y=50
                )
                adjusted = get_adjusted_mfdetrec_res(
                    ctx.formula_regions + ctx.checkbox_res, useful_list
                )
                bgr_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)
                ocr_res = txt_spans_bbox_extract(
                    ctx.page_dict, res, mfd_res=adjusted,
                    scale=ctx.scale, useful_list=useful_list,
                )
                if ocr_res:
                    result_list = get_ocr_result_list(
                        ocr_res, useful_list, ctx.ocr_enable, bgr_image, ctx.lang
                    )
                    ctx.layout_res.extend(result_list)
                    res['_pdf_det_done'] = True
                    count += 1

        elapsed = time.perf_counter() - t0
        if count > 0:
            self._record_perf('pdf_det', elapsed, count, contexts)
            if self.verbose:
                logger.info(f"[Stage 4/7] PDF-det — {count} regions in {elapsed:.3f}s")

    # ──────────────── Stage 3∥5: Formula(CPU) + OCR-det(NPU) 병렬 ─────────────

    def _run_parallel_formula_ocr_det(self, contexts: List[PageContext]) -> None:
        """Formula(CPU)와 OCR-det(NPU)를 병렬 실행한다.

        전제조건: _stage_pdf_det이 먼저 완료되어 _pdf_det_done 플래그가 설정됨.
        """
        cpu_error: List[Optional[Exception]] = [None]
        npu_error: List[Optional[Exception]] = [None]

        def cpu_worker():
            try:
                if self.formula_enable and self.formula_rec_enable:
                    self._stage_formula(contexts)
                elif self.formula_enable:
                    logger.info("[Stage 3/7] Formula — rec disabled, kept as image")
            except Exception as e:
                cpu_error[0] = e

        def npu_worker():
            try:
                self._stage_ocr_det(contexts)
            except Exception as e:
                npu_error[0] = e

        t_cpu = threading.Thread(target=cpu_worker, name="stage-formula-cpu", daemon=True)
        t_npu = threading.Thread(target=npu_worker, name="stage-ocr-det-npu", daemon=True)
        t_cpu.start()
        t_npu.start()
        t_cpu.join()
        t_npu.join()

        if cpu_error[0] and npu_error[0]:
            logger.error(f"[Stage 3∥5] NPU error also occurred: {npu_error[0]}")
            raise cpu_error[0]
        if cpu_error[0]:
            raise cpu_error[0]
        if npu_error[0]:
            raise npu_error[0]

    # ─────────────────────────── Stage 5: OCR-det ────────────────────────────

    def _should_skip_ocr_det(self, ctx: PageContext, res: dict) -> bool:
        """OCR-det를 건너뛰어야 하는 영역이면 True를 반환한다."""
        if ctx.ocr_enable:
            return False
        if self.use_det_mode == 'txt':
            return True
        return (
            self.use_det_mode != 'ocr'
            and not res.get('need_ocr_det')
            and bool(res.get('_pdf_det_done'))
        )

    def _collect_ocr_det_items(self, contexts: List[PageContext]) -> list:
        """OCR-det 처리 대상 이미지 목록을 수집해 반환한다."""
        all_items = []
        for ctx in contexts:
            for res in ctx.ocr_candidates:
                if self._should_skip_ocr_det(ctx, res):
                    continue
                res.pop('need_ocr_det', None)
                new_image, useful_list = crop_img(
                    res, ctx.np_img, crop_paste_x=50, crop_paste_y=50
                )
                adjusted = get_adjusted_mfdetrec_res(
                    ctx.formula_regions + ctx.checkbox_res, useful_list
                )
                bgr_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)
                all_items.append((ctx, res, adjusted, bgr_image, useful_list))
        return all_items

    def _stage_ocr_det(self, contexts: List[PageContext]) -> None:
        """
        OCR이 필요한 모든 영역을 모아 배치로 검출한다.

        배치 경로 (RapidOcrModel): det_batch_predict를 사용해 해상도별 그룹핑 후 일괄 처리.
        개별 경로 (DxOcrModel):    ocr_model.ocr(img, rec=False) 개별 처리
                                   (DX Engine은 내부 run_async로 하드웨어 병렬화).
        """
        ocr_model = self.atom_model_manager.get_atom_model(
            atom_model_name=AtomicModel.OCR,
            det_db_box_thresh=0.3,
            ocr_config=self.ocr_config,
        )

        all_items = self._collect_ocr_det_items(contexts)

        if not all_items:
            if self.verbose:
                logger.info("[Stage 5/7] OCR-det — 없음 (skip)")
            return

        n = len(all_items)
        logger.info(f"[Stage 5/7] OCR-det — {n} regions")
        t0 = time.perf_counter()
        count = 0

        # 배치 경로 (RapidOcrModel.det_batch_predict 지원 여부 확인)
        if hasattr(ocr_model, 'det_batch_predict'):
            count = self._ocr_det_batch(ocr_model, all_items)
        else:
            count = self._ocr_det_single(ocr_model, all_items)

        elapsed = time.perf_counter() - t0
        if count > 0:
            self._record_perf('ocr_det', elapsed, count, contexts)
        logger.info(f"   ↳ {elapsed:.3f}s | {count} boxes | {count / max(elapsed, 0.001):.2f} it/s")

    def _ocr_det_batch(self, ocr_model, all_items) -> int:
        """해상도별 그룹핑 후 det_batch_predict로 일괄 처리 (RapidOcrModel용)."""
        STRIDE = 64
        resolution_groups = defaultdict(list)
        for item in all_items:
            bgr_image = item[3]   # (ctx, res, adjusted, bgr_image, useful_list)
            h, w = bgr_image.shape[:2]
            nh = ((h + STRIDE) // STRIDE) * STRIDE
            nw = ((w + STRIDE) // STRIDE) * STRIDE
            resolution_groups[(nh, nw)].append(item)

        count = 0
        for _group_key, group_items in tqdm(resolution_groups.items(), desc="OCR-det batch"):
            count += self._process_ocr_det_group(ocr_model, group_items, STRIDE)
        return count

    def _process_ocr_det_group(
        self, ocr_model, group_items: list, stride: int
    ) -> int:
        """단일 해상도 그룹의 OCR-det 배치를 실행하고 처리된 박스 수를 반환한다."""
        max_h = max(it[3].shape[0] for it in group_items)
        max_w = max(it[3].shape[1] for it in group_items)
        th = ((max_h + stride - 1) // stride) * stride
        tw = ((max_w + stride - 1) // stride) * stride

        batch_imgs = []
        for _ctx, _res, _adj, bgr_image, _ul in group_items:
            h, w = bgr_image.shape[:2]
            padded = np.ones((th, tw, 3), dtype=np.uint8) * 255
            padded[:h, :w] = bgr_image
            batch_imgs.append(padded)

        batch_results = ocr_model.det_batch_predict(batch_imgs, len(batch_imgs))
        count = 0
        for item, (dt_boxes, _) in zip(group_items, batch_results):
            ctx, _res, adjusted, bgr_image, useful_list = item
            count += self._apply_det_boxes(ctx, dt_boxes, adjusted, bgr_image, useful_list)
        return count

    def _apply_det_boxes(
        self,
        ctx: PageContext,
        dt_boxes,
        adjusted,
        bgr_image: np.ndarray,
        useful_list: list,
    ) -> int:
        """검출된 박스를 후처리해 layout_res에 추가하고 처리된 박스 수를 반환한다."""
        if dt_boxes is None or len(dt_boxes) == 0:
            return 0
        dt_sorted = sorted_boxes(dt_boxes)
        dt_merged = merge_det_boxes(dt_sorted) if dt_sorted else []
        dt_final = (
            update_det_boxes(dt_merged, adjusted)
            if (dt_merged and adjusted) else dt_merged
        )
        ocr_res = [b.tolist() if hasattr(b, 'tolist') else b for b in dt_final]
        if not ocr_res:
            return 0
        result_list = get_ocr_result_list(
            ocr_res, useful_list, ctx.ocr_enable, bgr_image, None
        )
        ctx.layout_res.extend(result_list)
        return 1

    def _ocr_det_single(self, ocr_model, all_items) -> int:
        """Dispatch detection: batch path for DxOcrModel, sequential for others."""
        from rapid_doc.model.ocr.dx_ocr import DxOcrModel

        if isinstance(ocr_model, DxOcrModel) and hasattr(ocr_model, 'ocr_det_batch'):
            images = [bgr_image for _ctx, _res, _adj, bgr_image, _ul in all_items]
            mfd_list = [adj for _ctx, _res, adj, _bgr, _ul in all_items]
            try:
                batch_results = ocr_model.ocr_det_batch(images, mfd_list)
            except Exception as e:
                logger.error(f"Batch det failed: {e}, falling back to sequential")
                return self._ocr_det_single_sequential(ocr_model, all_items)

            count = 0
            for (ctx, _res, _adj, bgr_image, useful_list), ocr_res in zip(all_items, batch_results):
                if ocr_res:
                    result_list = get_ocr_result_list(
                        ocr_res, useful_list, ctx.ocr_enable, bgr_image, None
                    )
                    ctx.layout_res.extend(result_list)
                    count += 1
            return count
        else:
            return self._ocr_det_single_sequential(ocr_model, all_items)

    def _ocr_det_single_sequential(self, ocr_model, all_items) -> int:
        """Sequential per-image detection (fallback for non-DX models)."""
        count = 0
        for ctx, _res, adjusted, bgr_image, useful_list in tqdm(all_items, desc="OCR-det"):
            ocr_res = ocr_model.ocr(bgr_image, mfd_res=adjusted, rec=False)[0]
            if ocr_res:
                result_list = get_ocr_result_list(
                    ocr_res, useful_list, ctx.ocr_enable, bgr_image, None
                )
                ctx.layout_res.extend(result_list)
                count += 1
        return count

    # ─────────────────────────── Stage 6: Table ──────────────────────────────

    def _prepare_table_ocr_result(
        self,
        ocr_model_for_table,
        ctx: PageContext,
        ti: dict,
    ) -> list:
        """Return OCR results for table regions as [boxes, texts, scores].

        NOTE: det-only(rec=False) results have empty text, which causes
        the table model to skip its own OCR — a bug. Return None so that
        rapid_table internally runs det+rec OCR instead.
        """
        return None

    def _process_tables_parallel(
        self,
        table_model,
        items: list,
    ) -> None:
        """
        듀얼 스레드로 테이블 목록을 병렬 처리.
        Phase 1: prepare_image (순차)
        Phase 2: UNET + OCR (병렬 스레드)
        Phase 3: build_html (순차)
        """
        n = len(items)
        if n == 0:
            return

        # Phase 1: 준비
        prepared = []
        for ctx, ti in items:
            bgr_image, is_rotated = table_model.prepare_image(ti['table_img'])
            adjusted = get_adjusted_mfdetrec_res(
                ctx.formula_regions + ctx.checkbox_res,
                ti['useful_list'],
                return_text=True,
            )
            fill_image_res = extract_table_fill_image(ctx.page_dict, ti, scale=ctx.scale)
            prepared.append((bgr_image, adjusted, fill_image_res))

        # Phase 2: 병렬 실행
        unet_results = [None] * n
        ocr_results = [None] * n
        unet_error = [None]
        ocr_error = [None]

        def unet_worker():
            try:
                for i, (bgr, _, fill_res) in enumerate(prepared):
                    unet_results[i] = table_model.run_unet(bgr, fill_image_res=fill_res)
            except Exception as e:
                unet_error[0] = e

        def ocr_worker():
            try:
                for i, (bgr, adjusted, _) in enumerate(prepared):
                    ocr_results[i] = table_model.run_ocr(bgr, mfd_res=adjusted)
            except Exception as e:
                ocr_error[0] = e

        t_unet = threading.Thread(target=unet_worker, name="table-unet", daemon=True)
        t_ocr = threading.Thread(target=ocr_worker, name="table-ocr", daemon=True)
        t_unet.start()
        t_ocr.start()
        t_unet.join()
        t_ocr.join()

        if unet_error[0]:
            if ocr_error[0]:
                logger.error("OCR thread also failed: %s", ocr_error[0])
            raise unet_error[0]
        if ocr_error[0]:
            raise ocr_error[0]

        # Phase 3: 결합
        for i, (ctx, ti) in enumerate(items):
            _, adjusted, fill_res = prepared[i]
            html_code, _, _, _ = table_model.build_html(
                unet_results[i],
                ocr_results[i],
                fill_image_res=fill_res,
                mfd_res=adjusted,
                skip_text_in_image=self.skip_text_in_image,
                use_img2table=self.use_img2table,
            )
            self._apply_table_html(ti, html_code)

    def _stage_table(self, contexts: List[PageContext]) -> None:
        """모든 테이블 후보를 모아 듀얼 스레드 병렬 처리한다."""
        all_items = [
            (ctx, ti)
            for ctx in contexts
            for ti in ctx.table_candidates
        ]

        if not all_items:
            if self.verbose:
                logger.info("[Stage 6/7] Table — 없음 (skip)")
            return

        n = len(all_items)
        logger.info(f"[Stage 6/7] Table — {n} tables")
        t0 = time.perf_counter()

        table_model = self.atom_model_manager.get_atom_model(
            atom_model_name='table',
            ocr_config=self.ocr_config,
            table_config=self.table_config,
        )

        self._process_tables_parallel(table_model, all_items)

        elapsed = time.perf_counter() - t0
        self._record_perf('table', elapsed, n, contexts)
        logger.info(f"   ↳ {elapsed:.3f}s | {n / max(elapsed, 0.001):.2f} it/s")

    # ─────────────────────────── Stage 7: OCR-rec ────────────────────────────

    def _stage_ocr_rec(self, contexts: List[PageContext]) -> None:
        """
        category_id=15(OcrText) 항목의 텍스트 크롭을 모아 일괄 인식한다.
        DxOcrModel(use_async=True)의 경우 텍스트 인식기가 항목별로 run_async를
        제출하고 wait_request로 수집한다.
        """
        need_ocr_list = []
        img_crop_list = []

        for ctx in contexts:
            for item in ctx.layout_res:
                if item.get('category_id') == 15 and 'np_img' in item:
                    item['_pdf_idx'] = ctx.pdf_idx
                    need_ocr_list.append(item)
                    img_crop_list.append(item.pop('np_img'))
                    item.pop('lang', None)

        if not img_crop_list:
            return

        n = len(img_crop_list)
        logger.info(f"[Stage 7/7] OCR-rec — {n} crops")
        t0 = time.perf_counter()

        ocr_model = self.atom_model_manager.get_atom_model(
            atom_model_name=AtomicModel.OCR,
            det_db_box_thresh=0.3,
            ocr_config=self.ocr_config,
        )
        ocr_res_list = ocr_model.ocr(img_crop_list, det=False, tqdm_enable=True)[0]

        assert len(ocr_res_list) == len(need_ocr_list), (
            f"ocr_res_list 길이 불일치: {len(ocr_res_list)} vs {len(need_ocr_list)}"
        )

        for item, (text, score) in zip(need_ocr_list, ocr_res_list):
            item.pop('_pdf_idx', None)
            item['text'] = text
            item['score'] = float(f"{score:.3f}")
            if score < OcrConfidence.min_confidence:
                item['category_id'] = 16

        elapsed = time.perf_counter() - t0
        self._record_perf('ocr_rec', elapsed, n, contexts)
        logger.info(f"   ↳ {elapsed:.3f}s | {n / max(elapsed, 0.001):.2f} it/s")

    # ─────────────────────────── 통계 헬퍼 ──────────────────────────────────

    @staticmethod
    def _apply_table_html(ti: dict, html_code: Optional[str]) -> None:
        """Table 모델 결과 HTML을 검증 후 table_res에 저장한다."""
        if not html_code:
            logger.warning("Table recognition: HTML 테이블 태그 미발견")
            return
        # Image fallback marker — store as-is for downstream to handle
        if "data-fallback='image'" in html_code:
            ti['table_res']['html'] = html_code
            return
        if _TABLE_OPEN_TAG in html_code and _TABLE_CLOSE_TAG in html_code:
            s = html_code.find(_TABLE_OPEN_TAG)
            e = html_code.rfind(_TABLE_CLOSE_TAG) + len(_TABLE_CLOSE_TAG)
            ti['table_res']['html'] = html_code[s:e]
        else:
            logger.warning("Table recognition: HTML 테이블 태그 미발견")

    def _record_perf(
        self,
        key: str,
        elapsed: float,
        count: int,
        contexts: List[PageContext],
    ) -> None:
        self.perf_stats[key] = {'time': elapsed, 'count': count}
        # PDF별 통계 누적
        per_item = elapsed / max(count, 1)
        pdf_counts: Dict[int, int] = defaultdict(int)
        for ctx in contexts:
            pdf_counts[ctx.pdf_idx] += 1
        for pdf_idx, n in pdf_counts.items():
            self.pdf_perf_stats[pdf_idx][key]['time'] += per_item * n
            self.pdf_perf_stats[pdf_idx][key]['count'] += n

    def _print_perf_summary(
        self,
        total_pages: int = 0,
        wall_time: float = 0.0,
        pipeline_name: str = "",
    ) -> None:
        if not self.perf_stats:
            return

        total_stage = sum(v['time'] for v in self.perf_stats.values())
        W = 58

        logger.info("=" * W)
        title = f"{pipeline_name} PERFORMANCE SUMMARY" if pipeline_name else "PERFORMANCE SUMMARY"
        logger.info(f"{title:^{W}}")
        logger.info("=" * W)

        # Model loading time
        model_load_times = getattr(self.model, 'model_load_times', None)
        if model_load_times:
            total_load = sum(model_load_times.values())
            logger.info(f" {'Model Loading':<16} {total_load:>10.2f} s")
            for name, elapsed in model_load_times.items():
                logger.info(f"   {name:<14} {elapsed:>10.2f} s")
            logger.info("-" * W)

        logger.info(f" {'Pipeline Step':<16} {'Avg Latency':>14} {'Throughput':>14}     ")
        logger.info("-" * W)

        stage_order = ['layout', 'formula', 'pdf_det', 'ocr_det', 'table', 'ocr_rec']
        stage_labels = {
            'layout':  'Layout',
            'formula': 'Formula',
            'pdf_det': 'PDF-det',
            'ocr_det': 'OCR-det',
            'table':   'Table',
            'ocr_rec': 'OCR-rec',
        }
        for key in stage_order:
            if key not in self.perf_stats:
                continue
            s = self.perf_stats[key]
            t, c = s['time'], s['count']
            avg_ms = (t / max(c, 1)) * 1000
            fps = c / max(t, 0.001)
            label = stage_labels.get(key, key)
            logger.info(f" {label:<16} {avg_ms:>10.2f} ms {fps:>10.1f} FPS")

        logger.info("-" * W)
        logger.info(f" {'Total Stages':<16} {total_stage:>10.2f} s")

        if total_pages > 0 and wall_time > 0:
            overall_fps = total_pages / wall_time
            logger.info("-" * W)
            logger.info(f" {'Total Pages':<16} {total_pages:>14}")
            logger.info(f" {'Total Time':<16} {wall_time:>12.1f} s")
            logger.info(f" {'Overall':<16} {overall_fps:>10.1f} pages/s")

        logger.info("=" * W)

        # Per-document elapsed time
        if self.pdf_perf_stats:
            logger.info("")
            logger.info("=" * W)
            logger.info(f"{'PER-DOCUMENT ELAPSED TIME':^{W}}")
            logger.info("=" * W)
            logger.info(f" {'Document':<16} {'Total Time (s)':>14} {'Pages':>10}")
            logger.info("-" * W)
            for pdf_idx in sorted(self.pdf_perf_stats.keys()):
                pdf_stats = self.pdf_perf_stats[pdf_idx]
                doc_total = sum(s['time'] for s in pdf_stats.values())
                page_count = max(s['count'] for s in pdf_stats.values()) if pdf_stats else 0
                logger.info(f" {'PDF #' + str(pdf_idx):<16} {doc_total:>14.2f} {page_count:>10}")
            logger.info("=" * W)

    # ─────────────── 단일 페이지 처리 메서드 (StreamingPipeline 용) ────────────

    def _layout_one(self, ctx: PageContext) -> None:
        """단일 페이지 레이아웃 검출."""
        t0 = time.perf_counter()
        results = self.model.layout_model.batch_predict([ctx.np_img], 1)
        layout_res = results[0]
        if self.formula_enable and self.formula_level == 1:
            layout_res = [item for item in layout_res if item["category_id"] != 13]
        ctx.layout_res = layout_res
        self._accumulate_perf('layout', time.perf_counter() - t0, 1, ctx)

    def _plan_one(self, ctx: PageContext) -> None:
        """단일 페이지 영역 분류 (CPU only)."""
        ocr_candidates, table_candidates, formula_regions = get_res_list_from_layout_res(
            ctx.layout_res, ctx.np_img
        )
        checkbox_res = []
        if self.checkbox_enable:
            checkbox_img = cv2.cvtColor(ctx.np_img, cv2.COLOR_RGB2BGR)
            checkbox_res = checkbox_predict(checkbox_img)
            for res in checkbox_res:
                poly = [
                    res['bbox'][0], res['bbox'][1],
                    res['bbox'][2], res['bbox'][1],
                    res['bbox'][2], res['bbox'][3],
                    res['bbox'][0], res['bbox'][3],
                ]
                ctx.layout_res.append({
                    'bbox': res['bbox'], 'poly': poly,
                    'category_id': CategoryId.CheckBox,
                    'checkbox': res['text'], 'score': 0.9,
                })
        ctx.ocr_candidates = list(ocr_candidates)
        ctx.checkbox_res = checkbox_res
        # formula_level=2: 행간 수식은 LaTeX 추론 대상에서 제외
        if self.formula_level == 2:
            ctx.formula_regions = [
                fr for fr in formula_regions
                if fr.get("category_id") not in (
                    CategoryId.InterlineEquation_Layout,
                    CategoryId.InterlineEquation_YOLO,
                )
            ]
        else:
            ctx.formula_regions = list(formula_regions)
        ctx.table_candidates = []
        for tr in table_candidates:
            table_img, useful_list = crop_img(tr, ctx.np_img)
            ctx.table_candidates.append({
                'table_res': tr,
                'table_img': table_img,
                'useful_list': useful_list,
                'ocr_enable': ctx.ocr_enable,
            })
        ctx.formula_crops = []
        for fr in ctx.formula_regions:
            latex_img, _ = crop_img(fr, ctx.np_img)
            ctx.formula_crops.append(latex_img)

    def _formula_one(self, ctx: PageContext) -> None:
        """단일 페이지 수식 인식."""
        if not ctx.formula_crops:
            return
        t0 = time.perf_counter()
        batch_size = self.formula_config.get("batch_num", 1)
        latex_results = self.model.formula_model.batch_predict(
            ctx.formula_crops, batch_size=batch_size
        )
        for fr_dict, latex in zip(ctx.formula_regions, latex_results):
            if latex:
                fr_dict['latex'] = latex
        self._accumulate_perf('formula', time.perf_counter() - t0, len(ctx.formula_crops), ctx)

    def _pdf_det_one(self, ctx: PageContext) -> None:
        """단일 페이지 PDF 텍스트 직접 추출 (모델 없음)."""
        if self.use_det_mode == 'ocr' or ctx.ocr_enable:
            return
        t0 = time.perf_counter()
        count = 0
        for res in ctx.ocr_candidates:
            new_image, useful_list = crop_img(res, ctx.np_img, crop_paste_x=50, crop_paste_y=50)
            adjusted = get_adjusted_mfdetrec_res(
                ctx.formula_regions + ctx.checkbox_res, useful_list
            )
            bgr_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)
            ocr_res = txt_spans_bbox_extract(
                ctx.page_dict, res, mfd_res=adjusted,
                scale=ctx.scale, useful_list=useful_list,
            )
            if ocr_res:
                result_list = get_ocr_result_list(
                    ocr_res, useful_list, ctx.ocr_enable, bgr_image, ctx.lang
                )
                ctx.layout_res.extend(result_list)
                res['_pdf_det_done'] = True
                count += 1
        if count:
            self._accumulate_perf('pdf_det', time.perf_counter() - t0, count, ctx)

    def _ocr_det_one(self, ctx: PageContext) -> None:
        """단일 페이지 OCR 텍스트 박스 검출."""
        ocr_model = self.atom_model_manager.get_atom_model(
            atom_model_name=AtomicModel.OCR,
            det_db_box_thresh=0.3,
            ocr_config=self.ocr_config,
        )
        items = []
        for res in ctx.ocr_candidates:
            if self._should_skip_ocr_det(ctx, res):
                continue
            res.pop('need_ocr_det', None)
            new_image, useful_list = crop_img(res, ctx.np_img, crop_paste_x=50, crop_paste_y=50)
            adjusted = get_adjusted_mfdetrec_res(
                ctx.formula_regions + ctx.checkbox_res, useful_list
            )
            bgr_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)
            items.append((ctx, res, adjusted, bgr_image, useful_list))

        if not items:
            return
        t0 = time.perf_counter()
        if hasattr(ocr_model, 'det_batch_predict'):
            count = self._ocr_det_batch(ocr_model, items)
        else:
            count = self._ocr_det_single(ocr_model, items)
        if count:
            self._accumulate_perf('ocr_det', time.perf_counter() - t0, count, ctx)

    def _table_one(self, ctx: PageContext) -> None:
        """단일 페이지 테이블 인식 (듀얼 스레드 병렬)."""
        if not ctx.table_candidates:
            return
        t0 = time.perf_counter()
        table_model = self.atom_model_manager.get_atom_model(
            atom_model_name='table',
            ocr_config=self.ocr_config,
            table_config=self.table_config,
        )
        items = [(ctx, ti) for ti in ctx.table_candidates]
        self._process_tables_parallel(table_model, items)
        n = len(ctx.table_candidates)
        self._accumulate_perf('table', time.perf_counter() - t0, n, ctx)

    def _ocr_rec_one(self, ctx: PageContext) -> None:
        """단일 페이지 OCR 텍스트 인식."""
        need_ocr_list = []
        img_crop_list = []
        for item in ctx.layout_res:
            if item.get('category_id') == 15 and 'np_img' in item:
                item['_pdf_idx'] = ctx.pdf_idx
                need_ocr_list.append(item)
                img_crop_list.append(item.pop('np_img'))
                item.pop('lang', None)
        if not img_crop_list:
            return
        t0 = time.perf_counter()
        ocr_model = self.atom_model_manager.get_atom_model(
            atom_model_name=AtomicModel.OCR,
            det_db_box_thresh=0.3,
            ocr_config=self.ocr_config,
        )
        ocr_res_list = ocr_model.ocr(img_crop_list, det=False, tqdm_enable=False)[0]
        assert len(ocr_res_list) == len(need_ocr_list)
        for item, (text, score) in zip(need_ocr_list, ocr_res_list):
            item.pop('_pdf_idx', None)
            item['text'] = text
            item['score'] = float(f"{score:.3f}")
            if score < OcrConfidence.min_confidence:
                item['category_id'] = 16
        self._accumulate_perf('ocr_rec', time.perf_counter() - t0, len(img_crop_list), ctx)

    def _accumulate_perf(
        self,
        key: str,
        elapsed: float,
        count: int,
        ctx: PageContext,
    ) -> None:
        """스레드 안전한 성능 통계 누적 (StreamingPipeline에서 override)."""
        # TrueAsyncPipeline(배치 모드)에서는 _record_perf로 위임
        # — 이 메서드를 직접 호출하는 경우는 StreamingPipeline 전용
        pass


# ─────────────────────────────────────────────────────────────────────────────
# 스트리밍 파이프라인: 페이지 단위 어셈블리 라인
# ─────────────────────────────────────────────────────────────────────────────

_SENTINEL = object()  # 종료 신호


class StreamingPipeline(TrueAsyncPipeline):
    """
    페이지 단위 어셈블리 라인 파이프라인.

    각 스테이지가 독립 스레드로 실행되고, queue.Queue로 PageContext를 전달한다.
    Layout → Plan → Formula+PDF-det+OCR-det → Table → OCR-rec
    모든 스테이지가 서로 다른 페이지를 동시에 처리한다.

    스테이지 구성:
        Stage 1: Layout      (Worker 스레드 — NPU)
        Stage 2: Plan        (Worker 스레드 — CPU)
        Stage 3: Enrich      (Worker 스레드 — Formula + PDF-det + OCR-det 순차)
        Stage 4: Table       (Worker 스레드 — NPU+OCR, bottleneck)
        Stage 5: OCR-rec     (Worker 스레드 — OCR)
    """

    def run(
        self,
        images_with_extra_info: List[Tuple],
    ) -> Tuple[List[Any], Dict]:
        total = len(images_with_extra_info)
        logger.info(f"🚀 StreamingPipeline: {total} pages (assembly-line mode)")
        t_total = time.perf_counter()

        # 스레드 안전 perf 누적용 Lock
        self._perf_lock = threading.Lock()
        self._streaming_perf: Dict[str, Dict] = defaultdict(lambda: {'time': 0.0, 'count': 0})

        # 각 스테이지 간 Queue (maxsize=2: 처리 중 1 + 버퍼 1)
        q_layout  = queue.Queue(maxsize=2)
        q_plan    = queue.Queue(maxsize=2)
        q_enrich  = queue.Queue(maxsize=2)
        q_table   = queue.Queue(maxsize=2)
        q_done    = queue.Queue()

        # 스테이지 함수 정의
        def stage_layout():
            for item in images_with_extra_info:
                ctx = self._build_one_context(item, _seq_counter())
                if self.verbose:
                    logger.debug(f"[Stream] Layout  page ({ctx.pdf_idx},{ctx.page_idx})")
                self._layout_one(ctx)
                q_layout.put(ctx)
            q_layout.put(_SENTINEL)

        def stage_plan():
            while True:
                ctx = q_layout.get()
                if ctx is _SENTINEL:
                    q_plan.put(_SENTINEL)
                    break
                if self.verbose:
                    logger.debug(f"[Stream] Plan    page ({ctx.pdf_idx},{ctx.page_idx})")
                self._plan_one(ctx)
                q_plan.put(ctx)

        def stage_enrich():
            """Formula + PDF-det + OCR-det 를 한 스레드에서 순차 처리."""
            while True:
                ctx = q_plan.get()
                if ctx is _SENTINEL:
                    q_enrich.put(_SENTINEL)
                    break
                if self.verbose:
                    logger.debug(f"[Stream] Enrich  page ({ctx.pdf_idx},{ctx.page_idx})")
                if self.formula_enable and self.formula_rec_enable:
                    self._formula_one(ctx)
                self._pdf_det_one(ctx)
                self._ocr_det_one(ctx)
                q_enrich.put(ctx)

        def stage_table():
            while True:
                ctx = q_enrich.get()
                if ctx is _SENTINEL:
                    q_table.put(_SENTINEL)
                    break
                if self.verbose:
                    logger.debug(f"[Stream] Table   page ({ctx.pdf_idx},{ctx.page_idx})")
                if self.table_enable:
                    self._table_one(ctx)
                q_table.put(ctx)

        def stage_ocr_rec():
            while True:
                ctx = q_table.get()
                if ctx is _SENTINEL:
                    q_done.put(_SENTINEL)
                    break
                if self.verbose:
                    logger.debug(f"[Stream] OCR-rec page ({ctx.pdf_idx},{ctx.page_idx})")
                self._ocr_rec_one(ctx)
                q_done.put(ctx)

        # 시퀀스 카운터 (thread-safe, layout 스레드만 사용)
        _seq = [-1]
        def _seq_counter():
            _seq[0] += 1
            return _seq[0]

        # 스레드 시작
        threads = [
            threading.Thread(target=stage_layout,  name="stream-layout",  daemon=True),
            threading.Thread(target=stage_plan,    name="stream-plan",    daemon=True),
            threading.Thread(target=stage_enrich,  name="stream-enrich",  daemon=True),
            threading.Thread(target=stage_table,   name="stream-table",   daemon=True),
            threading.Thread(target=stage_ocr_rec, name="stream-ocr-rec", daemon=True),
        ]
        for t in threads:
            t.start()

        # 완료된 PageContext 수집
        completed: List[PageContext] = []
        sentinel_count = 0
        while sentinel_count < 1:
            item = q_done.get()
            if item is _SENTINEL:
                sentinel_count += 1
            else:
                completed.append(item)

        for t in threads:
            t.join()

        # 순서 복원 (pdf_idx, page_idx 기준)
        completed.sort(key=lambda c: (c.pdf_idx, c.page_idx))

        elapsed = time.perf_counter() - t_total
        self.perf_stats = {k: v for k, v in self._streaming_perf.items()}
        self._print_perf_summary(total, elapsed, "StreamingPipeline")

        results = [ctx.layout_res for ctx in completed]
        return results, dict(self.pdf_perf_stats)

    def _build_one_context(self, item: Tuple, _seq: int) -> PageContext:
        """단일 item에서 PageContext 생성."""
        if len(item) == 7:
            img, scale, ocr_enable, lang, page_dict, pdf_idx, page_idx = item
        else:
            img, scale, ocr_enable, lang, page_dict = item
            pdf_idx, page_idx = 0, _seq
        np_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        return PageContext(
            pdf_idx=pdf_idx,
            page_idx=page_idx,
            np_img=np_img,
            scale=scale,
            ocr_enable=ocr_enable,
            lang=lang,
            page_dict=page_dict,
        )

    def _accumulate_perf(
        self,
        key: str,
        elapsed: float,
        count: int,
        ctx: PageContext,
    ) -> None:
        """스레드 안전한 성능 통계 누적."""
        with self._perf_lock:
            self._streaming_perf[key]['time']  += elapsed
            self._streaming_perf[key]['count'] += count
            self.pdf_perf_stats[ctx.pdf_idx][key]['time']  += elapsed
            self.pdf_perf_stats[ctx.pdf_idx][key]['count'] += count


# ─────────────────────────────────────────────────────────────────────────────
# 세분화 스트리밍 파이프라인: Enrich 단계를 Formula/PDF-det/OCR-det 3단계로 분리
# ─────────────────────────────────────────────────────────────────────────────

class FinegrainedStreamingPipeline(StreamingPipeline):
    """
    7단계 페이지 단위 어셈블리 라인 파이프라인.

    StreamingPipeline의 Enrich(Formula+PDF-det+OCR-det) 단계를
    3개의 독립 스레드로 분리하여 NPU 활용률을 높인다.
    모든 단일 페이지 처리 메서드(_xxx_one)는 부모 클래스를 그대로 재사용한다.

    스테이지 구성:
        Stage 1: Layout   (fg-layout)   — NPU / maxsize=2
        Stage 2: Plan     (fg-plan)     — CPU / maxsize=2
        Stage 3: Formula  (fg-formula)  — NPU(ONNX) / maxsize=2
        Stage 4: PDF-det  (fg-pdf-det)  — CPU / maxsize=2
        Stage 5: OCR-det  (fg-ocr-det)  — NPU / maxsize=4 (버퍼 확장)
        Stage 6: Table    (fg-table)    — NPU / maxsize=4 (버퍼 확장)
        Stage 7: OCR-rec  (fg-ocr-rec)  — NPU / maxsize=unbounded (출력 수집)
    """

    _Q_OCR_MAXSIZE: int = 4     # OCR 집약 스테이지 버퍼
    _Q_DEFAULT_MAXSIZE: int = 2  # 일반 스테이지 버퍼

    def run(
        self,
        images_with_extra_info: List[Tuple],
    ) -> Tuple[List[Any], Dict]:
        total = len(images_with_extra_info)
        logger.info(f"🚀 FinegrainedStreamingPipeline: {total} pages (7-stage assembly-line)")
        t_total = time.perf_counter()

        self._perf_lock = threading.Lock()
        self._streaming_perf: Dict[str, Dict] = defaultdict(lambda: {'time': 0.0, 'count': 0})

        # 스테이지 간 Queue
        q_layout  = queue.Queue(maxsize=self._Q_DEFAULT_MAXSIZE)
        q_plan    = queue.Queue(maxsize=self._Q_DEFAULT_MAXSIZE)
        q_formula = queue.Queue(maxsize=self._Q_DEFAULT_MAXSIZE)
        q_pdf_det = queue.Queue(maxsize=self._Q_DEFAULT_MAXSIZE)
        q_ocr_det = queue.Queue(maxsize=self._Q_OCR_MAXSIZE)
        q_table   = queue.Queue(maxsize=self._Q_OCR_MAXSIZE)
        q_done    = queue.Queue()

        # thread-safe 시퀀스 카운터 (stage_layout 스레드 전용)
        _seq = [-1]

        def _next_seq() -> int:
            _seq[0] += 1
            return _seq[0]

        # ── 스테이지 함수 ──────────────────────────────────────────────────

        def stage_layout():
            for item in images_with_extra_info:
                ctx = self._build_one_context(item, _next_seq())
                if self.verbose:
                    logger.debug(f"[FG] Layout   page ({ctx.pdf_idx},{ctx.page_idx})")
                self._layout_one(ctx)
                q_layout.put(ctx)
            q_layout.put(_SENTINEL)

        def stage_plan():
            while True:
                ctx = q_layout.get()
                if ctx is _SENTINEL:
                    q_plan.put(_SENTINEL)
                    break
                if self.verbose:
                    logger.debug(f"[FG] Plan     page ({ctx.pdf_idx},{ctx.page_idx})")
                self._plan_one(ctx)
                q_plan.put(ctx)

        def stage_formula():
            while True:
                ctx = q_plan.get()
                if ctx is _SENTINEL:
                    q_formula.put(_SENTINEL)
                    break
                if self.verbose:
                    logger.debug(f"[FG] Formula  page ({ctx.pdf_idx},{ctx.page_idx})")
                if self.formula_enable and self.formula_rec_enable:
                    self._formula_one(ctx)
                q_formula.put(ctx)

        def stage_pdf_det():
            while True:
                ctx = q_formula.get()
                if ctx is _SENTINEL:
                    q_pdf_det.put(_SENTINEL)
                    break
                if self.verbose:
                    logger.debug(f"[FG] PDF-det  page ({ctx.pdf_idx},{ctx.page_idx})")
                self._pdf_det_one(ctx)
                q_pdf_det.put(ctx)

        def stage_ocr_det():
            while True:
                ctx = q_pdf_det.get()
                if ctx is _SENTINEL:
                    q_ocr_det.put(_SENTINEL)
                    break
                if self.verbose:
                    logger.debug(f"[FG] OCR-det  page ({ctx.pdf_idx},{ctx.page_idx})")
                self._ocr_det_one(ctx)
                q_ocr_det.put(ctx)

        def stage_table():
            while True:
                ctx = q_ocr_det.get()
                if ctx is _SENTINEL:
                    q_table.put(_SENTINEL)
                    break
                if self.verbose:
                    logger.debug(f"[FG] Table    page ({ctx.pdf_idx},{ctx.page_idx})")
                if self.table_enable:
                    self._table_one(ctx)
                q_table.put(ctx)

        def stage_ocr_rec():
            while True:
                ctx = q_table.get()
                if ctx is _SENTINEL:
                    q_done.put(_SENTINEL)
                    break
                if self.verbose:
                    logger.debug(f"[FG] OCR-rec  page ({ctx.pdf_idx},{ctx.page_idx})")
                self._ocr_rec_one(ctx)
                q_done.put(ctx)

        # ── 스레드 시작 ───────────────────────────────────────────────────

        threads = [
            threading.Thread(target=stage_layout,  name="fg-layout",  daemon=True),
            threading.Thread(target=stage_plan,    name="fg-plan",    daemon=True),
            threading.Thread(target=stage_formula, name="fg-formula", daemon=True),
            threading.Thread(target=stage_pdf_det, name="fg-pdf-det", daemon=True),
            threading.Thread(target=stage_ocr_det, name="fg-ocr-det", daemon=True),
            threading.Thread(target=stage_table,   name="fg-table",   daemon=True),
            threading.Thread(target=stage_ocr_rec, name="fg-ocr-rec", daemon=True),
        ]
        for t in threads:
            t.start()

        # ── 결과 수집 ─────────────────────────────────────────────────────

        completed: List[PageContext] = []
        while True:
            item = q_done.get()
            if item is _SENTINEL:
                break
            completed.append(item)

        for t in threads:
            t.join()

        # (pdf_idx, page_idx) 기준 정렬
        completed.sort(key=lambda c: (c.pdf_idx, c.page_idx))

        elapsed = time.perf_counter() - t_total
        self.perf_stats = {k: v for k, v in self._streaming_perf.items()}
        self._print_perf_summary(total, elapsed, "FinegrainedStreamingPipeline")

        results = [ctx.layout_res for ctx in completed]
        return results, dict(self.pdf_perf_stats)


# ─────────────────────────────────────────────────────────────────────────────
# 공개 API (pipeline_analyze.py 에서 호출)
# ─────────────────────────────────────────────────────────────────────────────

def async_batch_image_analyze(
    images_with_extra_info: List[Tuple],
    formula_enable: bool = True,
    table_enable: bool = True,
    layout_config: dict = None,
    ocr_config: dict = None,
    formula_config: dict = None,
    table_config: dict = None,
    checkbox_config: dict = None,
    input_interval: float = 0.0,   # pipeline_analyze.py 하위 호환 — 미사용
    verbose: bool = False,
    hybrid: bool = False,
) -> Tuple[List[Any], Dict]:
    """
    TrueAsyncPipeline을 사용한 배치 이미지 분석 (공개 API).

    모든 페이지를 스테이지별 배치로 처리한다:
      Layout(전체) → Plan(전체) → Formula(전체) → OCR-det(전체) → Table(전체) → OCR-rec(전체)
    DX Engine은 배치 제출 시 NPU 내부 큐를 통해 병렬 처리하므로
    단일 페이지 스트리밍보다 배치 모드가 더 효율적이다.

    pipeline_analyze.py → use_async_pipeline=True 경로에서 호출된다.

    Note: StreamingPipeline(어셈블리 라인 방식)도 이 파일에 구현되어 있으나,
    DX Engine NPU는 배치 제출 시 내부 병렬화가 더 효율적이어서 기본값으로
    TrueAsyncPipeline을 사용한다.
    """
    # use_async=True 로 복사체 생성 (원본 dict 수정 방지)
    ocr_config = {**(ocr_config or {}), 'use_async': True}
    layout_config = {**(layout_config or {}), 'use_async': True}
    table_config = {**(table_config or {}), 'use_async': True}

    use_det_mode = ocr_config.get('use_det_mode', 'auto')

    model = custom_model_init(
        lang=None,
        formula_enable=formula_enable,
        table_enable=table_enable,
        layout_config=layout_config,
        ocr_config=ocr_config,
        formula_config=formula_config,
        table_config=table_config,
        hybrid=hybrid,
    )

    pipeline = TrueAsyncPipeline(
        model=model,
        formula_enable=formula_enable,
        table_enable=table_enable,
        use_det_mode=use_det_mode,
        layout_config=layout_config,
        ocr_config=ocr_config,
        formula_config=formula_config,
        table_config=table_config,
        checkbox_config=checkbox_config,
        verbose=verbose,
    )

    results, pdf_perf_stats = pipeline.run(images_with_extra_info)
    model_load_times = getattr(model, 'model_load_times', {})
    clean_memory(get_device())
    return results, pdf_perf_stats, model_load_times


def finegrained_streaming_batch_image_analyze(
    images_with_extra_info: List[Tuple],
    formula_enable: bool = True,
    table_enable: bool = True,
    layout_config: dict = None,
    ocr_config: dict = None,
    formula_config: dict = None,
    table_config: dict = None,
    checkbox_config: dict = None,
    input_interval: float = 0.0,   # 하위 호환 — 미사용
    verbose: bool = False,
    hybrid: bool = False,
) -> Tuple[List[Any], Dict]:
    """
    FinegrainedStreamingPipeline을 사용한 배치 이미지 분석 (공개 API).

    Enrich 단계(Formula+PDF-det+OCR-det)를 3개의 독립 스레드 스테이지로 분리하여
    NPU 활용률을 높인다. 각 페이지가 7단계 어셈블리 라인을 순서대로 흐른다:
      Layout → Plan → Formula → PDF-det → OCR-det → Table → OCR-rec

    pipeline_analyze.py → use_async_pipeline="finegrained" 경로에서 호출된다.
    """
    ocr_config = {**(ocr_config or {}), 'use_async': True}
    layout_config = {**(layout_config or {}), 'use_async': True}
    table_config = {**(table_config or {}), 'use_async': True}

    use_det_mode = ocr_config.get('use_det_mode', 'auto')

    model = custom_model_init(
        lang=None,
        formula_enable=formula_enable,
        table_enable=table_enable,
        layout_config=layout_config,
        ocr_config=ocr_config,
        formula_config=formula_config,
        table_config=table_config,
        hybrid=hybrid,
    )

    pipeline = FinegrainedStreamingPipeline(
        model=model,
        formula_enable=formula_enable,
        table_enable=table_enable,
        use_det_mode=use_det_mode,
        layout_config=layout_config,
        ocr_config=ocr_config,
        formula_config=formula_config,
        table_config=table_config,
        checkbox_config=checkbox_config,
        verbose=verbose,
    )

    results, pdf_perf_stats = pipeline.run(images_with_extra_info)
    model_load_times = getattr(model, 'model_load_times', {})
    clean_memory(get_device())

    return results, pdf_perf_stats, model_load_times


# backward-compatible alias (pipeline_analyze.py의 기존 호출부가 input_interval을 넘기는 경우 대비)
def _async_batch_image_analyze_compat(
    images_with_extra_info,
    formula_enable=True,
    table_enable=True,
    layout_config=None,
    ocr_config=None,
    formula_config=None,
    table_config=None,
    checkbox_config=None,
    input_interval=0.0,   # 하위 호환을 위해 수신하지만 미사용
    verbose=False,
):
    """input_interval 파라미터를 포함한 하위 호환 래퍼."""
    return async_batch_image_analyze(
        images_with_extra_info,
        formula_enable=formula_enable,
        table_enable=table_enable,
        layout_config=layout_config,
        ocr_config=ocr_config,
        formula_config=formula_config,
        table_config=table_config,
        checkbox_config=checkbox_config,
        verbose=verbose,
    )
