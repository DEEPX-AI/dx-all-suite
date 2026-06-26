from copy import deepcopy
from typing import List

import numpy as np


class Normalize:
    """Normalize the image with mean and standard deviation.

    Args:
        mean (List[float]): mean values.
        std (List[float]): standard deviation values.
    """

    def __init__(self, mean: List[float], std: List[float], scale: float = None) -> None:
        self.mean = mean
        self.std = std
        self.scale = scale if scale is not None else 1.

    def __call__(self, inputs: np.ndarray) -> np.ndarray:
        """Normalize input image.

        Args:
            inputs (np.ndarray): input image.

        Returns:
            np.ndarray: normalized image.
        """
        inputs = deepcopy(inputs)
        inputs = inputs.astype(np.float32)
        img_shapes = inputs.shape
        unsqueeze_dims = []
        for i, shape in enumerate(img_shapes):
            if shape != 3 or len(unsqueeze_dims) != i:
                unsqueeze_dims.append(i)

        inputs = inputs * self.scale

        if inputs.shape[-1] == 3:
            inputs[..., 0] -= self.mean[0]
            inputs[..., 1] -= self.mean[1]
            inputs[..., 2] -= self.mean[2]
            inputs[..., 0] /= self.std[0]
            inputs[..., 1] /= self.std[1]
            inputs[..., 2] /= self.std[2]
        else:
            if 3 in img_shapes:
                mean = np.expand_dims(self.mean, unsqueeze_dims)
                std = np.expand_dims(self.std, unsqueeze_dims)
            else:
                mean = self.mean
                std = self.std
            inputs -= mean
            inputs /= std
        return inputs
