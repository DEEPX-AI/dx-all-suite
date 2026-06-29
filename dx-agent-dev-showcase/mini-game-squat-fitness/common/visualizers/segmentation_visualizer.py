"""
Semantic Segmentation Visualizer

Draws colored segmentation mask overlay.
"""

import numpy as np
import cv2
from typing import List

from ..base import IVisualizer, SegmentationResult


# Common color palettes
CITYSCAPES_PALETTE = np.array([
    [128, 64, 128],   # 0: road
    [244, 35, 232],   # 1: sidewalk
    [70, 70, 70],     # 2: building
    [102, 102, 156],  # 3: wall
    [190, 153, 153],  # 4: fence
    [153, 153, 153],  # 5: pole
    [250, 170, 30],   # 6: traffic light
    [220, 220, 0],    # 7: traffic sign
    [107, 142, 35],   # 8: vegetation
    [152, 251, 152],  # 9: terrain
    [70, 130, 180],   # 10: sky
    [220, 20, 60],    # 11: person
    [255, 0, 0],      # 12: rider
    [0, 0, 142],      # 13: car
    [0, 0, 70],       # 14: truck
    [0, 60, 100],     # 15: bus
    [0, 80, 100],     # 16: train
    [0, 0, 230],      # 17: motorcycle
    [119, 11, 32],    # 18: bicycle
], dtype=np.uint8)

ADE20K_PALETTE = np.random.randint(0, 255, size=(150, 3), dtype=np.uint8)
ADE20K_PALETTE[0] = [0, 0, 0]  # Background


class SemanticSegmentationVisualizer(IVisualizer):
    """
    Visualizer for semantic segmentation results.
    
    Overlays colored segmentation mask on image.
    """
    
    def __init__(self, palette: str = 'cityscapes', alpha: float = 0.6, 
                 custom_palette: np.ndarray = None, background_class: int = 0):
        """
        Initialize segmentation visualizer.
        
        Args:
            palette: Predefined palette name ('cityscapes', 'ade20k')
            alpha: Mask overlay transparency (0-1)
            custom_palette: Custom color palette (N, 3) array
            background_class: Class ID to skip (treat as background)
        """
        self.alpha = alpha
        self.background_class = background_class
        
        if custom_palette is not None:
            self.color_palette = custom_palette
        elif palette == 'cityscapes':
            self.color_palette = CITYSCAPES_PALETTE
        elif palette == 'ade20k':
            self.color_palette = ADE20K_PALETTE
        else:
            # Generate random palette
            self.color_palette = np.random.randint(0, 255, size=(256, 3), dtype=np.uint8)
    
    def visualize(self, image: np.ndarray, results: List[SegmentationResult]) -> np.ndarray:
        """
        Draw segmentation mask overlay on image.
        
        Args:
            image: Original image (BGR format)
            results: List containing SegmentationResult
            
        Returns:
            Image with colored mask overlay
        """
        output = image.copy()
        
        if not results:
            return output
        
        result = results[0]  # Single segmentation result
        class_map = result.mask  # Use mask attribute from SegmentationResult
        
        if class_map.size == 0:
            return output
        
        h, w = output.shape[:2]
        cm_h, cm_w = class_map.shape[:2]

        colored_mask_small = np.zeros((cm_h, cm_w, 3), dtype=np.uint8)
        for class_id in range(len(self.color_palette)):
            if class_id == self.background_class:
                continue
            mask = class_map.astype(np.int32) == class_id
            if np.any(mask):
                colored_mask_small[mask] = self.color_palette[class_id]

        colored_mask = cv2.resize(colored_mask_small, (w, h), interpolation=cv2.INTER_LINEAR)
        cv2.addWeighted(output, 1 - self.alpha, colored_mask, self.alpha, 0, dst=output)
        
        return output
