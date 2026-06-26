import numpy as np
from PIL import Image


class CenterCrop:
    """Crop the center of the image

    Args:
        height (int): target height.
        width (int): target width.
    """

    def __init__(self, height: int, width: int) -> None:
        self.height = height
        self.width = width

    def __call__(self, inputs: np.ndarray | Image.Image) -> np.ndarray:
        """crop the center of input image.

        Args:
            inputs (np.ndarray): input image.

        Returns:
            np.ndarray: cropped image.
        """
        if isinstance(inputs, Image.Image):
            inputs = np.array(inputs)

        height, width = inputs.shape[:2]
        crop_left = int(round((width - self.width) / 2.0))
        crop_top = int(round((height - self.height) / 2.0))
        return inputs[crop_top : crop_top + self.height, crop_left : crop_left + self.width]
