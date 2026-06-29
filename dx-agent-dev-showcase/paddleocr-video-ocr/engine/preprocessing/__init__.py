from typing import Callable, Dict, List

import numpy as np

from preprocessing.centercrop import CenterCrop
from preprocessing.convertcolor import ConvertColor
from preprocessing.div import Div
from preprocessing.expanddim import ExpandDim
from preprocessing.normalize import Normalize
from preprocessing.resize import Resize
from preprocessing.transpose import Transpose

PREPROCESSING = Dict[str, Dict[str, str | int | float | List[int | float]]]


PREPROCESSING_MAP = {
    "resize": Resize,
    "centercrop": CenterCrop,
    "convertColor": ConvertColor,
    "normalize": Normalize,
    "div": Div,
    "transpose": Transpose,
    "expandDim": ExpandDim,
}


def parse_ort_preprocessing_ops(preprocessings: List[PREPROCESSING]) -> List[Callable]:
    """parse onnx runtime preprocessings.
    if expandDim preprocessing in preprocessing appear just one time, it removed.

    Args:
        preprocessings (List[PREPROCESSING]): preprocessing list.

    Returns:
        List[Callable]: preprocessing ops list.
    """
    expand_dim = True
    ops_list = []
    for preprocessing in preprocessings:
        ops_name = list(preprocessing.keys())[0]
        if ops_name == "expandDim" and expand_dim is True:
            expand_dim = False
            continue
        ops = PREPROCESSING_MAP[ops_name]
        kwargs = preprocessing[ops_name]
        ops_list.append(ops(**kwargs))
    return ops_list


def parse_npu_preprocessing_ops(preprocessings: List[PREPROCESSING]) -> List[Callable]:
    """parse npu preprocessing ops.
    it removes calculation operations like div, mul, add, normalizations.
    and also it remove transpose operations.

    Args:
        preprocessings (List[PREPROCESSING]): preprocessing list.

    Returns:
        List[Callable]: preprocessing ops list.
    """
    expand_dim = True
    ops_list = []
    for preprocessing in preprocessings:
        ops_name = list(preprocessing.keys())[0]
        if ops_name == "expandDim" and expand_dim is True:
            expand_dim = False
            continue

        if ops_name in ["div", "mul", "add", "normalize", "subtract"]:
            continue
        ops = PREPROCESSING_MAP[ops_name]
        kwargs = preprocessing[ops_name]
        ops_list.append(ops(**kwargs))
    return ops_list


def parse_preprocessing_ops(preprocessings: List[PREPROCESSING], is_ort: bool = False) -> List[Callable]:
    """parse preprocessing ops.

    Args:
        preprocessings (List[PREPROCESSING]): preprocessings.

    Returns:
        List[Callable]: preprocessings ops list.
    """
    if is_ort:
        return parse_ort_preprocessing_ops(preprocessings)
    return parse_npu_preprocessing_ops(preprocessings)



class PreProcessingCompose:
    """Pre Processing Compose.
    it composes pre processing operations.

    Args:
        preprocessings (List[PREPROCESSING]): preprocessings List.
    """

    def __init__(self, preprocessings: List[PREPROCESSING], is_ort: bool = False) -> None:
        self._check_preprocessings(preprocessings)
        self.preprocessings_ops = parse_preprocessing_ops(preprocessings, is_ort=is_ort)

    def _check_preprocessings(self, preprocessings: List[PREPROCESSING]) -> None:
        """check if the preprocessings are valid.

        Args:
            preprocessings (List[PREPROCESSING]): preprocessings.

        Raises:
            ValueError: if the preprocessings are invalid, raise ValueError.
        """
        for preprocessing in preprocessings:
            ops_name = list(preprocessing.keys())[0]
            if ops_name not in PREPROCESSING_MAP:
                raise ValueError(f"Invalid Preprocessing name. {preprocessing}")

    def __call__(self, inputs: np.ndarray) -> np.ndarray:
        result = inputs
        for op in self.preprocessings_ops:
            result = op(result)
        
        for op in self.preprocessings_ops:
            if hasattr(op, '_last_padding_info') and op._last_padding_info is not None:
                self._last_padding_info = op._last_padding_info
                break
        else:
            self._last_padding_info = None
            
        return result
    
    def get_last_padding_info(self):
        return getattr(self, '_last_padding_info', None)
