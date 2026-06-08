"""
Classification Postprocessor

For classification models like EfficientNet, ResNet, etc.
"""

import numpy as np
from typing import List, Any

from ..base import IPostprocessor, PreprocessContext, ClassificationResult


class ClassificationPostprocessor(IPostprocessor):
    """
    Postprocessor for classification models.
    
    Applies softmax and returns top-k predictions.
    """
    
    def __init__(self, input_width: int = 224, input_height: int = 224, config: dict = None):
        """
        Initialize classification postprocessor.
        
        Args:
            input_width: Model input width
            input_height: Model input height
            config: Optional configuration
        """
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}
        self.num_classes = self.config.get('num_classes', 1000)
        self.top_k = self.config.get('top_k', 5)
    
    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext) -> List[ClassificationResult]:
        """
        Process classification model outputs.
        
        Args:
            outputs: Model outputs
            ctx: Preprocessing context
            
        Returns:
            List of ClassificationResult (top-k predictions)
        """
        output = outputs[0]
        
        # Handle single class output (argmax already applied in model)
        if output.size == 1:
            class_id = int(output.item())
            return [ClassificationResult(
                class_id=class_id,
                confidence=1.0,
                class_name=""
            )]
        
        # Flatten and apply softmax
        logits = output.flatten() if output.ndim > 1 else output
        probabilities = self._softmax(logits)
        
        # Get top-k
        top_indices = np.argsort(probabilities)[::-1][:self.top_k]
        
        results = []
        for idx in top_indices:
            results.append(ClassificationResult(
                class_id=int(idx),
                confidence=float(probabilities[idx]),
                class_name=""
            ))
        
        return results
    
    def get_model_name(self) -> str:
        return "classification"
    
    def _softmax(self, x: np.ndarray) -> np.ndarray:
        """Apply softmax to logits."""
        exp_x = np.exp(x - np.max(x))
        return exp_x / np.sum(exp_x)
