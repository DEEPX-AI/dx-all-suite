# -*- encoding: utf-8 -*-
from pathlib import Path
from typing import Union, Dict, Any

import numpy as np

from .logger import get_logger
from dx_engine import InferenceEngine, InferenceOption
from rapid_doc.utils.device_utils import get_dxnn_devices

class DxInferSession:
    def __init__(self, config: Dict[str, Any], use_async: bool = False,
                 device_ids: list = None, device_lock=None):
        """
        config에서 받는 항목:
        - model_path: 모델 파일 경로
        - engine_type: "dxengine"
        - use_cuda: GPU 사용 여부 (선택)
        - use_async: Async 모드 사용 여부
        """
        self.logger = get_logger("OrtInferSession")
        self.use_async = use_async
        self._device_lock = device_lock

        model_path = config.get("model_path", None)
        self._verify_model(model_path)
        
        self.io = InferenceOption()
        self.io.devices = device_ids if device_ids is not None else get_dxnn_devices()
        self.io.bound_option = InferenceOption.BOUND_OPTION.NPU_ALL
        
        self.session = InferenceEngine(model_path, self.io)
        
        # register_callback 사용하지 않음 — C++ 워커 스레드에서 Python 콜백 호출 시
        # GIL 문제로 segfault 발생 위험 (Layout에서 동일 문제 확인됨)
        # 대신 run_async + wait 패턴 사용
        self.logger.info(f"DxInferSession initialized (use_async={use_async})")

    @staticmethod
    def _verify_model(model_path: Union[str, Path, None]):
        if model_path is None:
            raise ValueError("model_path is None!")

        model_path = Path(model_path)
        if not model_path.exists():
            raise FileNotFoundError(f"{model_path} does not exists.")

        if not model_path.is_file():
            raise FileExistsError(f"{model_path} is not a file.")

    def __call__(self, input_array: np.ndarray) -> np.ndarray:
        """
        동기 추론 (run 사용)
        table_structure_unet.py의 infer()에서 호출:
        result = self.session(input["img"][None, ...])[0][0]
        """
        return self.session.run(input_array) 
