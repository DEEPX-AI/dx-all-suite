"""
Abstract interface for result visualization

This interface defines the contract for visualizing inference results.
"""

from abc import ABC, abstractmethod
from typing import List, Any
import numpy as np


class IVisualizer(ABC):
    """
    Abstract interface for visualizers.
    
    Visualizers draw inference results on images for display/saving.
    """
    
    @abstractmethod
    def visualize(self, frame: np.ndarray, results: List[Any]) -> np.ndarray:
        """
        Draw results on the image.
        
        Args:
            frame: Original image (will not be modified)
            results: List of results to visualize
            
        Returns:
            Visualized image
        """
        pass
