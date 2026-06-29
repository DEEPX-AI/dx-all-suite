import numpy as np


class ExpandDim:
    """Expand the dimensions of the inputs by inserting a new axis based on the input axis.

    Args:
        axis (int): position that new axis is inserted.
    """

    def __init__(self, axis: int) -> None:
        self.axis = axis

    def __call__(self, inputs: np.ndarray) -> np.ndarray:
        """Expand dimension of the inputs.

        Args:
            inputs (np.ndarray): inputs.

        Returns:
            np.ndarray: inputs that expanded dimension.
        """
        return np.expand_dims(inputs, axis=self.axis)
