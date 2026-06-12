import os
import time
from typing import List, Tuple
from PIL import Image
from loguru import logger

from .model_init import MineruPipelineModel
from ...utils.config_reader import get_device
from ...utils.enum_class import ImageType
from ...utils.hash_utils import make_hashable
from ...utils.pdf_classify import classify
from ...utils.pdf_image_tools import load_images_from_pdf, get_ori_image
from ...utils.model_utils import get_vram, clean_memory
from ...utils.pdf_text_tool import get_page

os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'  # mps가 fallback 할 수 있도록 허용
os.environ['NO_ALBUMENTATIONS_UPDATE'] = '1'  # albumentations 업데이트 확인 비활성화

class ModelSingleton:
    _instance = None
    _models = {}

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_model(
        self,
        lang=None,
        formula_enable=None,
        table_enable=None,
        layout_config=None,
        ocr_config=None,
        formula_config=None,
        table_config=None,
    ):
        key = (lang, formula_enable, table_enable, make_hashable(layout_config), make_hashable(ocr_config), make_hashable(formula_config), make_hashable(table_config))
        if key not in self._models:
            self._models[key] = custom_model_init(
                lang=lang,
                formula_enable=formula_enable,
                table_enable=table_enable,
                layout_config=layout_config,
                ocr_config=ocr_config,
                formula_config=formula_config,
                table_config=table_config,
            )
        return self._models[key]


def custom_model_init(
    lang=None,
    formula_enable=True,
    table_enable=True,
    layout_config=None,
    ocr_config=None,
    formula_config=None,
    table_config=None,
):
    model_init_start = time.time()
    # 설정 파일에서 model-dir과 device 읽기
    device = get_device()

    final_formula_config = {"enable": formula_enable}
    if formula_config is not None:
        final_formula_config.update(formula_config)  # 전달된 설정 병합
    final_table_config = {"enable": table_enable}
    if table_config is not None:
        final_table_config.update(table_config)  # 전달된 설정 병합

    model_input = {
        'device': device,
        'layout_config': layout_config,
        'ocr_config': ocr_config,
        'table_config': final_table_config,
        'formula_config': final_formula_config,
        'lang': lang,
    }

    custom_model = MineruPipelineModel(**model_input)

    model_init_cost = time.time() - model_init_start
    logger.info(f'model init cost: {model_init_cost}')

    return custom_model


def doc_analyze(
        pdf_bytes_list,
        lang_list: list[str] = None,
        parse_method: str = 'auto',
        formula_enable=True,
        table_enable=True,
        layout_config=None,
        ocr_config=None,
        formula_config=None,
        table_config=None,
        checkbox_config=None,
        use_async_pipeline: bool = False,
        async_input_interval: float = 0.0,
        async_verbose: bool = False,
):
    """
    MIN_BATCH_INFERENCE_SIZE를 적절히 늘리면 성능이 향상되며, 더 큰 MIN_BATCH_INFERENCE_SIZE는 더 많은 메모리를 소비합니다.
    환경 변수 MINERU_MIN_BATCH_INFERENCE_SIZE를 통해 설정할 수 있으며, 기본값은 384입니다.
    
    Args:
        use_async_pipeline: Use AsyncPipelineRapidDoc for processing (default: False)
        async_input_interval: Sleep interval between async job submissions
        async_verbose: Enable verbose logging for async pipeline
    """
    if lang_list is None:
        lang_list = ["ch"] * len(pdf_bytes_list)
    min_batch_inference_size = int(os.environ.get('MINERU_MIN_BATCH_INFERENCE_SIZE', 384))

    # 모든 페이지 정보 수집
    all_pages_info = []  # (dataset_index, page_index, img, ocr, lang, width, height) 저장

    all_image_lists = []
    all_pdf_docs = []
    ocr_enabled_list = []
    for pdf_idx, pdf_bytes in enumerate(pdf_bytes_list):
        # OCR 설정 결정
        _ocr_enable = False
        if parse_method == 'auto':
            if classify(pdf_bytes) == 'ocr':
                _ocr_enable = True
        elif parse_method == 'ocr':
            _ocr_enable = True
        
        # use_det_mode='ocr'이면 강제로 OCR 활성화
        if ocr_config and ocr_config.get('use_det_mode') == 'ocr':
            _ocr_enable = True
            logger.info(f"PDF #{pdf_idx}: use_det_mode='ocr' 설정으로 강제 OCR 활성화")

        _lang = lang_list[pdf_idx]

        # 각 데이터셋의 페이지 수집
        images_list, pdf_doc_list = load_images_from_pdf(pdf_bytes, image_type=ImageType.PIL)
        all_image_lists.append(images_list)

        all_pdf_dict = []
        page_force_ocr_flags = []
        for pdf_doc in pdf_doc_list:
            # pdf의 텍스트와 이미지 딕셔너리 객체 가져오기
            page_dict = get_page(pdf_doc)
            has_text_blocks = bool(page_dict['blocks'])
            page_force_ocr_flags.append(not has_text_blocks)
            if has_text_blocks:
                page_dict['ori_image_list'] = get_ori_image(pdf_doc) # PDF에서 모든 원본 이미지 추출
            else:
                page_dict['ori_image_list'] = [] # 텍스트를 추출할 수 없는 경우 스캔 버전으로 간주하여 이미지 추출 불필요
            pdf_doc.close()
            all_pdf_dict.append(page_dict)
        all_pdf_docs.append(all_pdf_dict)
        pdf_force_ocr = _ocr_enable or any(page_force_ocr_flags)
        ocr_enabled_list.append(pdf_force_ocr)

        for page_idx, img_dict in enumerate(images_list):
            needs_page_ocr = page_force_ocr_flags[page_idx] if page_idx < len(page_force_ocr_flags) else False
            all_pages_info.append((
                pdf_idx, page_idx,
                img_dict['img_pil'], img_dict['scale'], pdf_force_ocr or needs_page_ocr, _lang,
            ))

    # 배치 처리 준비 (PDF 인덱스 추가)
    images_with_extra_info = [
        (info[2], info[3], info[4], info[5], all_pdf_docs[info[0]][info[1]], info[0], info[1])  # pdf_idx, page_idx 추가
        for info in all_pages_info
    ]
    batch_size = min_batch_inference_size
    batch_images = [
        images_with_extra_info[i:i + batch_size]
        for i in range(0, len(images_with_extra_info), batch_size)
    ]

    # 배치 처리 실행 (Sync or Async mode)
    results = []
    all_pdf_perf_stats = {}  # PDF별 성능 통계 (배치 간 병합)
    processed_images_count = 0
    
    if use_async_pipeline:
        # Async mode: Process all pages at once using AsyncPipelineRapidDoc
        logger.info(f"🚀 Using AsyncPipelineRapidDoc for {len(images_with_extra_info)} pages")
        
        from .async_pipeline import async_batch_image_analyze
        
        results, all_pdf_perf_stats, _model_load_times = async_batch_image_analyze(
            images_with_extra_info,
            formula_enable=formula_enable,
            table_enable=table_enable,
            layout_config=layout_config,
            ocr_config=ocr_config,
            formula_config=formula_config,
            table_config=table_config,
            checkbox_config=checkbox_config,
            input_interval=async_input_interval,
            verbose=async_verbose
        )
        
    else:
        # Sync mode: Original batch processing
        for index, batch_image in enumerate(batch_images):
            processed_images_count += len(batch_image)
            logger.info(
                f'Batch {index + 1}/{len(batch_images)}: '
                f'{processed_images_count} pages/{len(images_with_extra_info)} pages'
            )
            batch_results, batch_pdf_stats = batch_image_analyze(
                batch_image, formula_enable, table_enable, 
                layout_config, ocr_config, formula_config, table_config, checkbox_config
            )
            results.extend(batch_results)
            
            # 배치별 PDF 통계를 병합
            for pdf_idx, pdf_stats in batch_pdf_stats.items():
                if pdf_idx not in all_pdf_perf_stats:
                    all_pdf_perf_stats[pdf_idx] = {}
                for model_name, model_stats in pdf_stats.items():
                    if model_name not in all_pdf_perf_stats[pdf_idx]:
                        all_pdf_perf_stats[pdf_idx][model_name] = {'time': 0.0, 'count': 0}
                    all_pdf_perf_stats[pdf_idx][model_name]['time'] += model_stats['time']
                    all_pdf_perf_stats[pdf_idx][model_name]['count'] += model_stats['count']

    # 반환 결과 구성
    infer_results = []

    for _ in range(len(pdf_bytes_list)):
        infer_results.append([])

    for i, page_info in enumerate(all_pages_info):
        pdf_idx, page_idx, pil_img, _, _, _ = page_info
        result = results[i]

        page_info_dict = {'page_no': page_idx, 'width': pil_img.width, 'height': pil_img.height}
        page_dict = {'layout_dets': result, 'page_info': page_info_dict}

        infer_results[pdf_idx].append(page_dict)

    # PDF별 성능 통계 출력 (batch_analyze에서 이미 출력했지만, 전체 배치 병합 결과 출력)
    if all_pdf_perf_stats:
        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 Aggregated performance per PDF (full batch)")
        logger.info("=" * 80)
        
        # 엔진 정보 추출
        engines = {}
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
        
        # 엔진 매핑
        engine_mapping = {
            'layout': engines.get('layout', 'unknown'),
            'formula': engines.get('formula', 'unknown'),
            'pdf_det': engines.get('ocr', 'unknown'),
            'ocr_det': engines.get('ocr', 'unknown'),
            'table': engines.get('table', 'unknown'),
            'ocr_rec': engines.get('ocr', 'unknown')
        }
        
        # 페이지 수 계산
        pdf_page_counts = {}
        for pdf_idx, _, _, _, _, _ in all_pages_info:
            pdf_page_counts[pdf_idx] = pdf_page_counts.get(pdf_idx, 0) + 1
        
        for pdf_idx in sorted(all_pdf_perf_stats.keys()):
            pdf_stats = all_pdf_perf_stats[pdf_idx]
            total_time = sum(model_stats['time'] for model_stats in pdf_stats.values())
            page_count = pdf_page_counts.get(pdf_idx, 0)
            
            logger.info(f"\n📄 PDF #{pdf_idx}: {page_count} pages, total time: {total_time:.2f}s")
            logger.info("-" * 80)
            
            # 모델별 통계 출력
            model_names = {
                'layout': '📊 Layout  ',
                'formula': '📐 Formula ',
                'pdf_det': '📄 PDF-det ',
                'ocr_det': '🔍 OCR-det ',
                'table': '📋 Table   ',
                'ocr_rec': '✍️  OCR-rec '
            }
            
            for key in ['layout', 'formula', 'pdf_det', 'ocr_det', 'table', 'ocr_rec']:
                if key in pdf_stats and pdf_stats[key]['time'] > 0:
                    model_stats = pdf_stats[key]
                    time_val = model_stats['time']
                    count = model_stats['count']
                    percentage = (time_val / total_time * 100) if total_time > 0 else 0
                    s_per_it = time_val / count if count > 0 else 0
                    it_per_s = count / time_val if time_val > 0 else 0
                    engine = engine_mapping.get(key, 'unknown')
                    
                    logger.info(
                        f"{model_names.get(key, key)} [{engine:>12s}] | {time_val:7.2f}s ({percentage:5.1f}%) | "
                        f"{int(count):4d}it | {s_per_it:.3f} s/it | {it_per_s:6.2f} it/s"
                    )
        
        logger.info("=" * 80)

    return infer_results, all_image_lists, all_pdf_docs, lang_list, ocr_enabled_list


def batch_image_analyze(
        images_with_extra_info: List[Tuple[Image.Image, float, bool, str, dict]],
        formula_enable=True,
        table_enable=True,
        layout_config=None,
        ocr_config=None,
        formula_config=None,
        table_config=None,
        checkbox_config=None,):

    from .batch_analyze import BatchAnalyze

    # 캐싱 없이 직접 모델 생성 (배치당 한 번만 생성)
    model = custom_model_init(
        lang=None,  # 기본 언어 사용 (또는 images_with_extra_info에서 가장 많이 쓰이는 언어 추출 가능)
        formula_enable=formula_enable,
        table_enable=table_enable,
        layout_config=layout_config,
        ocr_config=ocr_config,
        formula_config=formula_config,
        table_config=table_config,
    )

    batch_ratio = 1
    device = get_device()

    if str(device).startswith('npu'):
        try:
            import torch_npu
            if torch_npu.npu.is_available():
                torch_npu.npu.set_compile_mode(jit_compile=False)
        except Exception as e:
            raise RuntimeError(
                "NPU is selected as device, but torch_npu is not available. "
                "Please ensure that the torch_npu package is installed correctly."
            ) from e

    if str(device).startswith('npu') or str(device).startswith('cuda'):
        vram = get_vram(device)
        if vram is not None:
            gpu_memory = int(os.getenv('MINERU_VIRTUAL_VRAM_SIZE', round(vram)))
            if gpu_memory >= 16:
                batch_ratio = 16
            elif gpu_memory >= 12:
                batch_ratio = 8
            elif gpu_memory >= 8:
                batch_ratio = 4
            elif gpu_memory >= 6:
                batch_ratio = 2
            else:
                batch_ratio = 1
            logger.info(f'gpu_memory: {gpu_memory} GB, batch_ratio: {batch_ratio}')
        else:
            # Default batch_ratio when VRAM can't be determined
            batch_ratio = 1
            logger.info(f'Could not determine GPU memory, using default batch_ratio: {batch_ratio}')

    enable_ocr_det_batch = True
    batch_model = BatchAnalyze(model, batch_ratio, formula_enable, table_enable, enable_ocr_det_batch, layout_config, ocr_config, formula_config, table_config, checkbox_config)
    results, page_stats = batch_model(images_with_extra_info)

    clean_memory(get_device())

    return results, page_stats