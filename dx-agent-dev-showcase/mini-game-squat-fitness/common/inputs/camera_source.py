"""
Camera input source implementation.
"""

from typing import Tuple, Optional
import numpy as np
import cv2

from ..base.i_input_source import IInputSource, InputType


class CameraSource(IInputSource):
    """Input source for camera devices (USB, built-in)."""
    
    def __init__(self, device_id: int = 0, 
                 width: Optional[int] = None, 
                 height: Optional[int] = None,
                 fps: Optional[float] = None):
        """
        Initialize camera source.
        
        Args:
            device_id: Camera device ID (0 for default camera)
            width: Desired capture width (optional)
            height: Desired capture height (optional)
            fps: Desired capture FPS (optional)
        """
        self._device_id = device_id
        self._cap: Optional[cv2.VideoCapture] = None
        
        self._cap = cv2.VideoCapture(device_id)
        if not self._cap.isOpened():
            raise RuntimeError(f"Failed to open camera device: {device_id}")
        
        # Minimize frame buffer to prevent stale frames on live source
        self._cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # Set camera properties if specified
        if width is not None:
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        if height is not None:
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        if fps is not None:
            self._cap.set(cv2.CAP_PROP_FPS, fps)
        
        # Cache actual properties
        self._width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self._height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self._fps = self._cap.get(cv2.CAP_PROP_FPS)
    
    def get_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Get the next frame from camera."""
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
        return InputType.CAMERA
    
    def get_width(self) -> int:
        return self._width
    
    def get_height(self) -> int:
        return self._height
    
    def get_fps(self) -> float:
        return self._fps if self._fps > 0 else 30.0
    
    def get_total_frames(self) -> int:
        return -1  # Unlimited for live sources
    
    def get_description(self) -> str:
        return f"Camera: device {self._device_id} ({self._width}x{self._height} @ {self._fps:.2f}fps)"
    
    def is_live_source(self) -> bool:
        return True
    
    def set_auto_focus(self, enabled: bool) -> bool:
        """Enable or disable auto-focus."""
        if self._cap is None:
            return False
        return self._cap.set(cv2.CAP_PROP_AUTOFOCUS, 1 if enabled else 0)
    
    def set_exposure(self, value: float) -> bool:
        """Set camera exposure value."""
        if self._cap is None:
            return False
        return self._cap.set(cv2.CAP_PROP_EXPOSURE, value)
    
    def __iter__(self):
        """Make CameraSource iterable."""
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
