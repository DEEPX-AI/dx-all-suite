from typing import List

import numpy as np


class Transpose:
    """Transpose the inputs with axis values.

    Args:
        axis (List[int]): axis values.
    """

    def __init__(self, axis: List[int]) -> None:
        self.axis = axis

    def __call__(self, inputs: np.ndarray) -> np.ndarray:
        """Transpose the inputs.

        Args:
            inputs (np.ndarray): inputs

        Returns:
            np.ndarray: transposed inputs.
        """
        return np.ascontiguousarray(np.transpose(inputs, axes=self.axis))
