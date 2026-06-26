import numpy as np


class Div:
    """Divide the input value by x.

    Args:
        x (float): divisor value.
    """

    def __init__(self, x: float | int) -> None:
        self.x = float(x)

    def __call__(self, inputs: np.ndarray) -> np.ndarray:
        """Divide the input value.

        Args:
            inputs (np.ndarray): input value.

        Returns:
            np.ndarray: divided value.
        """
        inputs = inputs.astype(np.float32)
        return inputs / self.x
