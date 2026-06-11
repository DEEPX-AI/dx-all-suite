"""
Image file input source implementation.
"""

from pathlib import Path
from typing import Tuple, Optional
import numpy as np
import cv2

from ..base.i_input_source import IInputSource, InputType


class ImageSource(IInputSource):
    """Input source for static image files."""
    
    # Supported image extensions
    EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}
    
    def __init__(self, path: str):
        """
        Initialize image source.
        
        Args:
            path: Path to the image file
        """
        self._path = Path(path)
        self._image: Optional[np.ndarray] = None
        self._already_read = False
        
        if not self._path.exists():
            raise FileNotFoundError(f"Image file not found: {path}")
        
        if self._path.suffix.lower() not in self.EXTENSIONS:
            raise ValueError(f"Unsupported image format: {self._path.suffix}")
        
        # Load image immediately
        self._image = cv2.imread(str(self._path))
        if self._image is None:
            raise RuntimeError(f"Failed to load image: {path}")
    
    def get_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Get the image (only returns once, then returns None)."""
        if not self._already_read and self._image is not None:
            self._already_read = True
            return True, self._image.copy()
        return False, None
    
    def is_opened(self) -> bool:
        """Check if image was loaded successfully."""
        return self._image is not None and not self._already_read
    
    def release(self) -> None:
        """Release image resources."""
        self._image = None
    
    def get_type(self) -> InputType:
        return InputType.IMAGE
    
    def get_width(self) -> int:
        return self._image.shape[1] if self._image is not None else 0
    
    def get_height(self) -> int:
        return self._image.shape[0] if self._image is not None else 0
    
    def get_fps(self) -> float:
        return 0.0  # N/A for image
    
    def get_total_frames(self) -> int:
        return 1
    
    def get_description(self) -> str:
        return f"Image: {self._path.name} ({self.get_width()}x{self.get_height()})"
    
    def is_live_source(self) -> bool:
        return False
    
    def reset(self) -> None:
        """Reset the image source to be read again."""
        self._already_read = False
    
    def __iter__(self):
        """Make ImageSource iterable."""
        self.reset()
        return self
    
    def __next__(self) -> np.ndarray:
        """Get next frame (for iteration)."""
        ret, frame = self.get_frame()
        if not ret or frame is None:
            raise StopIteration
        return frame
    
    def close(self) -> None:
        """Alias for release()."""
        self.release()
    
    @classmethod
    def is_supported(cls, path: str) -> bool:
        """Check if the file path is a supported image format."""
        return Path(path).suffix.lower() in cls.EXTENSIONS
