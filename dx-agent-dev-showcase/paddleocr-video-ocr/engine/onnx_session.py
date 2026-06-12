from abc import ABC, abstractmethod

import numpy as np
from typing import List

# import onnx
# import onnxruntime as ort
# import torch
# from onnx import ModelProto
# from onnxruntime import InferenceSession

# Python 3.10 compatibility: StrEnum backport
try:
    from enum import StrEnum
except ImportError:
    from enum import Enum
    class StrEnum(str, Enum):
        """StrEnum backport for Python < 3.11"""
        def __str__(self) -> str:
            return str(self.value)
        
        def _generate_next_value_(name, start, count, last_values):
            return name

# def torch_to_numpy(tensor: torch.Tensor) -> np.ndarray:
#     return tensor.detach().cpu().numpy()

class SessionType(StrEnum):
    onnxruntime = "OnnxRuntime"
    simulator = "Simulator"
    dxruntime = "DxRuntime"


class SessionBase(ABC):
    """Session Base Class.
    it needs file path, and session type.
    """

    def __init__(self, path: str, session_type) -> None:
        self.path = path
        self.type = session_type

    @abstractmethod
    def run(self, inputs: np.ndarray) -> np.ndarray:
        """run session.

        Args:
            inputs (np.ndarray): input value.

        Returns:
            np.ndarray: session output value.
        """
        ...


# def get_ort_provider() -> List[str]:
#     """get onnxruntime provider.
#     if cuda is available, return "CUDAExecutionProvider". else return "CPUExecutionProvider"
# 
#     Returns:
#         List[str]: onnxruntime provider.
#     """
#     if torch.cuda.is_available():
#         provider = ["CUDAExecutionProvider"]
#         print(f"Found {torch.cuda.device_count()} GPU(s), using GPU. ")
#     else:
#         provider = ["CPUExecutionProvider"]
#         print("No GPU is available, using CPU.")
#     return provider
#     # return ["CPUExecutionProvider"]


# def get_ort_session_options() -> ort.SessionOptions:
#     """get onnxruntime session options.
#     it sets graph_optimization_level to ORT_ENABLE_BASIC.
# 
#     Returns:
#         ort.SessionOptions: onnxruntime session options.
#     """
#     sess_option = ort.SessionOptions()
#     sess_option.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_BASIC
#     return sess_option

# class OnnxRuntimeSession(SessionBase):
#     """OnnxRuntimeSession class.
# 
#     Args:
#         path (str): onnx model path.
#     """
# 
#     def __init__(self, path: str):
#         super().__init__(path, SessionType.onnxruntime)
#         self.inference_session = self._get_inference_session()
# 
#     def _get_onnx_model(self) -> ModelProto:
        """get onnx model.

        Raises:
            InvalidPathError: if the path is not exist, raise FileNotFoundError.

        Returns:
            ModelProto: onnx model.
        """
        model = None
        try:
            model = onnx.load(self.path)
            return model
        except FileNotFoundError:
            raise FileNotFoundError(self.path)

    def _get_inference_session(self) -> InferenceSession:
        """get onnxruntime inference session.

        Returns:
            InferenceSession: onnxruntime inference session.
        """
        model = self._get_onnx_model()
        provider = get_ort_provider()
        sess_option = get_ort_session_options()

        return InferenceSession(model.SerializeToString(), sess_option, providers=provider)

    def run(self, inputs: torch.Tensor, output_tensor = None) -> List[np.ndarray]:
        """run onnxruntime session.

        Args:
            inputs (np.ndarray): inputs.

        Returns:
            List[np.ndarray]: outputs.
        """
        inputs = torch_to_numpy(inputs)
        sess_inputs_name = self.inference_session.get_inputs()[0].name
        sess_inputs = {sess_inputs_name: inputs.astype(np.float32)}
        return self.inference_session.run(output_tensor, sess_inputs)
