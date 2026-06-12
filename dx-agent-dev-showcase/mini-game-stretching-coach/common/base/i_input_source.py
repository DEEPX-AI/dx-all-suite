"""
Abstract interface for input sources (Factory Method pattern)

This interface defines the contract for all input sources (image, video, camera, RTSP).
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Tuple
import numpy as np


class InputType(Enum):
    """Input source type enumeration"""
    IMAGE = "image"
    VIDEO = "video"
    CAMERA = "camera"
    RTSP = "rtsp"
    UNKNOWN = "unknown"


class IInputSource(ABC):
    """
    Abstract interface for input sources.
    
    All input sources (image, video, camera, RTSP) must implement this interface.
    This enables the Factory Method pattern for creating appropriate input handlers.
    """
    
    @abstractmethod
    def get_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Get the next frame from the input source.
        
        Returns:
            Tuple of (success, frame) where frame is BGR format numpy array
        """
        pass
    
    @abstractmethod
    def is_opened(self) -> bool:
        """Check if the input source is opened/available."""
        pass
    
    @abstractmethod
    def release(self) -> None:
        """Release the input source resources."""
        pass
    
    @abstractmethod
    def get_type(self) -> InputType:
        """Get the type of input source."""
        pass
    
    @abstractmethod
    def get_width(self) -> int:
        """Get the width of frames."""
        pass
    
    @abstractmethod
    def get_height(self) -> int:
        """Get the height of frames."""
        pass
    
    @abstractmethod
    def get_fps(self) -> float:
        """Get the FPS of the source (if applicable)."""
        pass
    
    @abstractmethod
    def get_total_frames(self) -> int:
        """Get total frame count (for video files)."""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get source description for logging."""
        pass
    
    @abstractmethod
    def is_live_source(self) -> bool:
        """Check if this is a live source (camera/RTSP)."""
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
