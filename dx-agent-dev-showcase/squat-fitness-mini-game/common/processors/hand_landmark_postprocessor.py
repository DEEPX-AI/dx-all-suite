"""
Hand Landmark Postprocessor

Processes MediaPipe-style hand landmark model outputs.
Output: [1, 63] — 21 keypoints × 3 (x, y, z) normalized coordinates.
Optional: handedness score, hand confidence.

21 keypoints follow MediaPipe hand topology:
  0: Wrist
  1-4: Thumb (CMC, MCP, IP, TIP)
  5-8: Index finger (MCP, PIP, DIP, TIP)
  9-12: Middle finger
  13-16: Ring finger
  17-20: Pinky finger
"""

import numpy as np
from typing import List

from ..base import IPostprocessor, PreprocessContext, HandLandmarkResult


class HandLandmarkPostprocessor(IPostprocessor):
    """Postprocessor for hand landmark detection models."""
    
    NUM_LANDMARKS = 21
    COORDS_PER_LANDMARK = 3  # x, y, z
    
    def __init__(self, input_width: int, input_height: int, config: dict = None):
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}
        self.confidence_threshold = self.config.get('confidence_threshold', 0.5)
    
    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext) -> List[HandLandmarkResult]:
        if not outputs or len(outputs) == 0:
            return []
        
        # Parse 21 landmarks from primary output [1, 63]
        lm_data = outputs[0].flatten().astype(np.float32)
        num_elements = len(lm_data)
        num_lmks = min(self.NUM_LANDMARKS, num_elements // self.COORDS_PER_LANDMARK)
        
        landmarks = np.zeros((num_lmks, 3), dtype=np.float32)
        
        for i in range(num_lmks):
            offset = i * self.COORDS_PER_LANDMARK
            x = lm_data[offset]
            y = lm_data[offset + 1]
            z = lm_data[offset + 2] if offset + 2 < num_elements else 0.0
            
            # Coordinates may be normalized [0, 1] or in input pixel space
            if 0.0 <= x <= 1.0 and 0.0 <= y <= 1.0:
                landmarks[i] = [x * ctx.original_width, y * ctx.original_height, z]
            else:
                sx = ctx.original_width / self.input_width
                sy = ctx.original_height / self.input_height
                landmarks[i] = [x * sx, y * sy, z]
        
        result = HandLandmarkResult()
        result.landmarks = landmarks
        
        # Parse hand presence score (tensor[1]) — used as confidence
        if len(outputs) > 1:
            result.confidence = float(outputs[1].flatten()[0])
        else:
            result.handedness = "Unknown"
            result.confidence = 1.0
        
        # Parse handedness if available (tensor[2])
        if len(outputs) > 2:
            hand_score = outputs[2].flatten()[0]
            result.handedness = "Right" if hand_score > 0.5 else "Left"
        
        # Filter by confidence threshold
        if result.confidence >= self.confidence_threshold:
            return [result]
        return []
    
    def get_model_name(self) -> str:
        return "HandLandmark"
