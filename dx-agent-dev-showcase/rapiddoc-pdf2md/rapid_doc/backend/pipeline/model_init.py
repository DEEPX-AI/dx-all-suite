import os
import time

from loguru import logger

from .model_list import AtomicModel
from ...model.layout.rapid_layout import RapidLayoutModel
from ...model.formula.rapid_formula_model import RapidFormulaModel
# RapidOcrModel은 실제 사용 시점에 lazy import (rapidocr 패키지 버전 의존 문제 방지)
from ...model.ocr.dx_ocr import DxOcrModel
from ...model.table.rapid_table import RapidTableModel
from ...utils.hash_utils import make_hashable

def table_model_init(ocr_config=None, table_config=None, device_ids=None, device_lock=None):
    use_async = table_config.get('use_async', False) if table_config else False
    atom_model_manager = AtomModelSingleton()
    ocr_engine = atom_model_manager.get_atom_model(
        atom_model_name=AtomicModel.OCR,
        det_db_box_thresh=0.5,
        det_db_unclip_ratio=1.6,
        ocr_config=ocr_config,
        enable_merge_det_boxes=False
    )
    table_model = RapidTableModel(ocr_engine, table_config, use_async=use_async,
                                   device_ids=device_ids, device_lock=device_lock)
    return table_model

def formula_model_init(formula_config=None):
    model = RapidFormulaModel(formula_config)
    return model


def layout_model_init(layout_config=None):
    # layout_config에서 use_async 추출 (있는 경우에만)
    use_async = layout_config.get('use_async', False) if layout_config else False
    model = RapidLayoutModel(layout_config, use_async=use_async)
    return model

def ocr_model_init(det_db_box_thresh=0.3, ocr_config=None, det_db_unclip_ratio=1.8, enable_merge_det_boxes=True,
                   det_device_ids=None, det_device_lock=None,
                   rec_device_ids=None, rec_device_lock=None):
    # DX Engine 사용 여부 확인
    use_dx_engine = False
    use_async = False
    if ocr_config:
        engine_type = ocr_config.get('engine_type')
        use_async = ocr_config.get('use_async', False)
        if engine_type and hasattr(engine_type, 'value') and engine_type.value == 'dxengine':
            use_dx_engine = True
        elif isinstance(engine_type, str) and engine_type.lower() == 'dxengine':
            use_dx_engine = True
    
    if use_dx_engine:
        # DX Engine 기반 OCR 모델 사용
        logger.info(f"Using DX Engine for OCR ({'ASYNC' if use_async else 'SYNC'} mode)")
        logger.info(f"DX Engine model paths: {det_db_box_thresh}, {det_db_unclip_ratio}")
        model = DxOcrModel(
            det_model_path=ocr_config.get('Det.model_path'),
            rec_model_path=ocr_config.get('Rec.model_path'),
            det_db_box_thresh=det_db_box_thresh,
            det_db_unclip_ratio=det_db_unclip_ratio,
            enable_merge_det_boxes=enable_merge_det_boxes,
            lang=None,  # lang은 실제로 사용되지 않음
            ocr_config=ocr_config,
            use_async=use_async,
            det_device_ids=det_device_ids,
            det_device_lock=det_device_lock,
            rec_device_ids=rec_device_ids,
            rec_device_lock=rec_device_lock,
        )
    else:
        # 기존 RapidOCR 사용 - DX Engine 전용 설정 제거
        logger.info("Using RapidOCR (ONNX Runtime/OpenVINO/Torch/Paddle)")
        # Lazy import: rapidocr 패키지 버전에 따라 내부 서브모듈 구조가 달라질 수 있으므로
        # dxengine을 쓰지 않을 때만 로드한다.
        from ...model.ocr.rapid_ocr import RapidOcrModel  # noqa: PLC0415

        # DX Engine 전용 키 필터링
        dx_only_keys = [
            'use_multi_det_model', 'use_multi_rec_model',
            'Det.model_paths', 'Rec.model_paths',
            'save_debug_images', 'debug_save_dir',
            'engine_type',  # DX Engine의 'dxengine' 문자열
            'use_async',  # async 관련 키도 필터링
        ]
        
        # ocr_config 복사 후 DX 전용 키 제거
        filtered_ocr_config = {k: v for k, v in ocr_config.items() if k not in dx_only_keys} if ocr_config else {}
        
        model = RapidOcrModel(
            det_db_box_thresh=det_db_box_thresh,
            lang=None,  # lang은 실제로 사용되지 않음
            ocr_config=filtered_ocr_config,
            use_dilation=True,
            det_db_unclip_ratio=det_db_unclip_ratio,
            enable_merge_det_boxes=enable_merge_det_boxes,
        )
    return model


class AtomModelSingleton:
    _instance = None
    _models = {}
    _allocator = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def set_allocator(cls, allocator):
        """파이프라인 시작 전에 DeviceAllocator를 설정한다."""
        cls._allocator = allocator

    @classmethod
    def reset(cls):
        """테스트용: 싱글톤 상태 초기화."""
        cls._instance = None
        cls._models = {}
        cls._allocator = None

    def get_atom_model(self, atom_model_name: str, **kwargs):
        allocator = self.__class__._allocator

        # hybrid 모드: device 정보를 cache key에 포함
        if allocator and allocator.hybrid:
            if atom_model_name == AtomicModel.OCR:
                extra_key = (
                    tuple(allocator.get_devices("ocr_det")),
                    tuple(allocator.get_devices("ocr_rec")),
                )
            elif atom_model_name == AtomicModel.Layout:
                extra_key = tuple(allocator.get_devices("layout"))
            elif atom_model_name == AtomicModel.Table:
                extra_key = tuple(allocator.get_devices("table"))
            else:
                extra_key = None
        else:
            extra_key = None

        if atom_model_name in [AtomicModel.Layout]:
            key = (atom_model_name, make_hashable(kwargs.get('layout_config', None)), extra_key)
        elif atom_model_name in [AtomicModel.OCR]:
            key = (atom_model_name, make_hashable(kwargs.get('ocr_config', None)), extra_key)
        elif atom_model_name in [AtomicModel.Table]:
            key = (atom_model_name, make_hashable(kwargs.get('table_config', None)), extra_key)
        elif atom_model_name in [AtomicModel.FORMULA]:
            key = (atom_model_name, make_hashable(kwargs.get('formula_config', None)), extra_key)
        else:
            key = (atom_model_name, extra_key)

        if key not in self._models:
            # hybrid 모드: device params 주입
            if allocator and allocator.hybrid:
                if atom_model_name == AtomicModel.Layout:
                    kwargs['_device_ids'] = allocator.get_devices("layout")
                    kwargs['_device_lock'] = allocator.get_lock("layout")
                elif atom_model_name == AtomicModel.OCR:
                    kwargs['_det_device_ids'] = allocator.get_devices("ocr_det")
                    kwargs['_det_device_lock'] = allocator.get_lock("ocr_det")
                    kwargs['_rec_device_ids'] = allocator.get_devices("ocr_rec")
                    kwargs['_rec_device_lock'] = allocator.get_lock("ocr_rec")
                elif atom_model_name == AtomicModel.Table:
                    kwargs['_device_ids'] = allocator.get_devices("table")
                    kwargs['_device_lock'] = allocator.get_lock("table")
            self._models[key] = atom_model_init(model_name=atom_model_name, **kwargs)
        return self._models[key]

def atom_model_init(model_name: str, **kwargs):
    # hybrid device params 추출 (모델 생성자에 직접 전달하지 않음)
    device_ids = kwargs.pop('_device_ids', None)
    device_lock = kwargs.pop('_device_lock', None)
    det_device_ids = kwargs.pop('_det_device_ids', None)
    det_device_lock = kwargs.pop('_det_device_lock', None)
    rec_device_ids = kwargs.pop('_rec_device_ids', None)
    rec_device_lock = kwargs.pop('_rec_device_lock', None)

    atom_model = None
    if model_name == AtomicModel.Layout:
        layout_config = kwargs.get('layout_config') or {}
        if device_ids is not None:
            layout_config = {**layout_config, 'device_ids': device_ids, 'device_lock': device_lock}
            kwargs['layout_config'] = layout_config
        atom_model = layout_model_init(
            kwargs.get('layout_config'),
        )
    elif model_name == AtomicModel.FORMULA:
        atom_model = formula_model_init(
            kwargs.get('formula_config'),
        )
    elif model_name == AtomicModel.OCR:
        atom_model = ocr_model_init(
            kwargs.get('det_db_box_thresh', 0.6),
            kwargs.get('ocr_config'),
            kwargs.get('det_db_unclip_ratio', 2.0),
            kwargs.get('enable_merge_det_boxes', True),
            det_device_ids=det_device_ids,
            det_device_lock=det_device_lock,
            rec_device_ids=rec_device_ids,
            rec_device_lock=rec_device_lock,
        )
    elif model_name == AtomicModel.Table:
        atom_model = table_model_init(
            kwargs.get('ocr_config'),
            kwargs.get('table_config'),
            device_ids=device_ids,
            device_lock=device_lock,
        )
    else:
        logger.error('model name not allow')
        exit(1)

    if atom_model is None:
        logger.error('model init failed')
        exit(1)
    else:
        return atom_model


class MineruPipelineModel:
    def __init__(self, **kwargs):
        self.layout_config = kwargs.get('layout_config')
        self.ocr_config = kwargs.get('ocr_config')
        self.formula_config = kwargs.get('formula_config')
        self.apply_formula = self.formula_config.get('enable', True)
        self.table_config = kwargs.get('table_config')
        self.apply_table = self.table_config.get('enable', True)
        self.lang = kwargs.get('lang', None)
        self.device = kwargs.get('device', 'cpu')
        logger.info(
            'DocAnalysis init, this may take some times......'
        )
        atom_model_manager = AtomModelSingleton()
        self.model_load_times: dict[str, float] = {}

        if self.apply_formula:
            t0 = time.perf_counter()
            self.formula_model = atom_model_manager.get_atom_model(
                atom_model_name=AtomicModel.FORMULA,
                device=self.device,
                formula_config=self.formula_config,
            )
            self.model_load_times['formula'] = time.perf_counter() - t0

        t0 = time.perf_counter()
        self.layout_model = atom_model_manager.get_atom_model(
            atom_model_name=AtomicModel.Layout,
            device=self.device,
            layout_config=self.layout_config,
        )
        self.model_load_times['layout'] = time.perf_counter() - t0

        t0 = time.perf_counter()
        self.ocr_model = atom_model_manager.get_atom_model(
            atom_model_name=AtomicModel.OCR,
            det_db_box_thresh=0.3,
            ocr_config=self.ocr_config,
        )
        self.model_load_times['ocr'] = time.perf_counter() - t0

        if self.apply_table:
            t0 = time.perf_counter()
            self.table_model = atom_model_manager.get_atom_model(
                atom_model_name=AtomicModel.Table,
                ocr_config=self.ocr_config,
                table_config=self.table_config,
            )
            self.model_load_times['table'] = time.perf_counter() - t0

        logger.info('DocAnalysis init done!')