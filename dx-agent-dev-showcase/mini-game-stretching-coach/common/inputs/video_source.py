"""
Video file input source implementation.
"""

from pathlib import Path
from typing import Tuple, Optional
import numpy as np
import cv2

from ..base.i_input_source import IInputSource, InputType


class VideoSource(IInputSource):
    """Input source for video files."""
    
    # Supported video extensions
    EXTENSIONS = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'}
    
    def __init__(self, path: str):
        """
        Initialize video source.
        
        Args:
            path: Path to the video file
        """
        self._path = Path(path)
        self._cap: Optional[cv2.VideoCapture] = None
        
        if not self._path.exists():
            raise FileNotFoundError(f"Video file not found: {path}")
        
        if self._path.suffix.lower() not in self.EXTENSIONS:
            raise ValueError(f"Unsupported video format: {self._path.suffix}")
        
        self._cap = cv2.VideoCapture(str(self._path))
        if not self._cap.isOpened():
            raise RuntimeError(f"Failed to open video: {path}")
        
        # Cache video properties
        self._width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self._height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self._fps = self._cap.get(cv2.CAP_PROP_FPS)
        self._total_frames = int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    def get_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Get the next video frame."""
        if self._cap is None or not self._cap.isOpened():
            return False, None
        return self._cap.read()
    
    def is_opened(self) -> bool:
        return self._cap is not None and self._cap.isOpened()
    
    def release(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None
    
    def get_type(self) -> InputType:
        return InputType.VIDEO
    
    def get_width(self) -> int:
        return self._width
    
    def get_height(self) -> int:
        return self._height
    
    def get_fps(self) -> float:
        return self._fps if self._fps > 0 else 30.0
    
    def get_total_frames(self) -> int:
        return self._total_frames
    
    def get_description(self) -> str:
        return (f"Video: {self._path.name} ({self._width}x{self._height} @ "
                f"{self._fps:.2f}fps, {self._total_frames} frames)")
    
    def is_live_source(self) -> bool:
        return False
    
    def seek(self, frame_number: int) -> bool:
        """Seek to a specific frame number."""
        if self._cap is None:
            return False
        return self._cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    
    def get_current_frame_number(self) -> int:
        """Get the current frame number."""
        if self._cap is None:
            return 0
        return int(self._cap.get(cv2.CAP_PROP_POS_FRAMES))
    
    def __iter__(self):
        """Make VideoSource iterable."""
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
        """Check if the file path is a supported video format."""
        return Path(path).suffix.lower() in cls.EXTENSIONS
