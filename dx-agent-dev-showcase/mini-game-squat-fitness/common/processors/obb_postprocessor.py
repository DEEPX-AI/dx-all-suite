"""
OBB (Oriented Bounding Box) Postprocessor

Processes model outputs in format (N, 7): [cx, cy, w, h, score, class_id, angle]
and converts to OBBResult with coordinate scaling and angle regularization.
"""

import numpy as np
from typing import List

from ..base import IPostprocessor, PreprocessContext, OBBResult


# DOTA v1 class labels (15 classes for aerial/satellite object detection)
DOTAV1_LABELS = [
    "plane", "ship", "storage-tank", "baseball-diamond", "tennis-court",
    "basketball-court", "ground-track-field", "harbor", "bridge",
    "large-vehicle", "small-vehicle", "helicopter", "roundabout",
    "soccer-ball-field", "swimming-pool"
]


class OBBPostprocessor(IPostprocessor):
    """
    Postprocessor for OBB (Oriented Bounding Box) detection models.
    
    Output format: [cx, cy, w, h, score, class_id, angle]
    Supports YOLOv26-OBB and similar models.
    """
    
    def __init__(self, input_width: int, input_height: int, config: dict = None):
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}
        
        self.score_threshold = self.config.get('score_threshold', 0.3)
        self.labels = self.config.get('labels', DOTAV1_LABELS)
    
    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext) -> List[OBBResult]:
        """
        Process OBB model outputs.
        
        Args:
            outputs: Model outputs, first tensor shape (N, 7) or (1, N, 7)
            ctx: Preprocessing context
            
        Returns:
            List of OBBResult objects
        """
        output = np.squeeze(outputs[0])
        
        if output.ndim != 2 or output.shape[1] < 7:
            return []
        
        # Filter by score threshold
        scores = output[:, 4]
        mask = scores >= self.score_threshold
        
        if not np.any(mask):
            return []
        
        filtered = output[mask]
        
        # Scale coordinates back to original image space
        gain = max(ctx.scale, 1e-6)
        pad_x = ctx.pad_x
        pad_y = ctx.pad_y
        
        # Transform cx, cy, w, h back to original coordinates
        cx_arr = (filtered[:, 0] - pad_x) / gain
        cy_arr = (filtered[:, 1] - pad_y) / gain
        w_arr = filtered[:, 2] / gain
        h_arr = filtered[:, 3] / gain
        scores_arr = filtered[:, 4]
        class_ids = filtered[:, 5].astype(int)
        angles = filtered[:, 6]
        
        # Regularize angles: if angle >= pi/2, swap w/h
        rboxes = np.column_stack([cx_arr, cy_arr, w_arr, h_arr, angles])
        rboxes = self._regularize_rboxes(rboxes)
        
        # Clip coordinates
        if ctx.original_width > 0 and ctx.original_height > 0:
            rboxes[:, 0] = np.clip(rboxes[:, 0], 0, ctx.original_width - 1)
            rboxes[:, 1] = np.clip(rboxes[:, 1], 0, ctx.original_height - 1)
        
        # Create result objects
        results = []
        for i in range(len(rboxes)):
            class_id = int(class_ids[i])
            if 0 <= class_id < len(self.labels):
                class_name = self.labels[class_id]
            else:
                class_name = f"class_{class_id}"
            
            result = OBBResult(
                cx=float(rboxes[i, 0]),
                cy=float(rboxes[i, 1]),
                width=float(rboxes[i, 2]),
                height=float(rboxes[i, 3]),
                angle=float(rboxes[i, 4]),
                confidence=float(scores_arr[i]),
                class_id=class_id,
                class_name=class_name
            )
            results.append(result)
        
        return results
    
    def get_model_name(self) -> str:
        return "YOLOv26OBB"
    
    @staticmethod
    def _regularize_rboxes(rboxes: np.ndarray) -> np.ndarray:
        """
        Regularize OBB rotation angles.
        
        If angle >= pi/2, swap width/height and normalize angle to [0, pi/2).
        """
        if rboxes.size == 0:
            return rboxes
        
        x, y, w, h, t = np.split(rboxes, 5, axis=-1)
        
        # Normalize angle to [0, pi)
        t = np.mod(t, np.pi)
        
        # If angle >= pi/2, swap w and h
        swap = t >= (np.pi / 2)
        
        w_reg = np.where(swap, h, w)
        h_reg = np.where(swap, w, h)
        t_reg = np.mod(t, np.pi / 2)
        
        return np.concatenate([x, y, w_reg, h_reg, t_reg], axis=-1)
