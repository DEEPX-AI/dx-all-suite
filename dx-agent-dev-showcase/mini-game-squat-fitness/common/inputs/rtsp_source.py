"""
RTSP stream input source implementation.
"""

from typing import Tuple, Optional
import numpy as np
import cv2

from ..base.i_input_source import IInputSource, InputType


class RTSPSource(IInputSource):
    """Input source for RTSP network streams."""
    
    # RTSP URL prefixes
    PREFIXES = ('rtsp://', 'rtsps://')
    
    def __init__(self, url: str, 
                 buffer_size: int = 1,
                 connection_timeout: int = 5000):
        """
        Initialize RTSP source.
        
        Args:
            url: RTSP stream URL
            buffer_size: OpenCV buffer size (1 for minimal latency)
            connection_timeout: Connection timeout in milliseconds
        """
        self._url = url
        self._cap: Optional[cv2.VideoCapture] = None
        
        if not self.is_supported(url):
            raise ValueError(f"Invalid RTSP URL: {url}")
        
        # Configure for low latency
        self._cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
        self._cap.set(cv2.CAP_PROP_BUFFERSIZE, buffer_size)
        
        if not self._cap.isOpened():
            raise RuntimeError(f"Failed to connect to RTSP stream: {url}")
        
        # Cache stream properties
        self._width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self._height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self._fps = self._cap.get(cv2.CAP_PROP_FPS)
    
    def get_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Get the next frame from RTSP stream."""
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
        return InputType.RTSP
    
    def get_width(self) -> int:
        return self._width
    
    def get_height(self) -> int:
        return self._height
    
    def get_fps(self) -> float:
        return self._fps if self._fps > 0 else 30.0
    
    def get_total_frames(self) -> int:
        return -1  # Unlimited for live sources
    
    def get_description(self) -> str:
        # Hide credentials in URL for logging
        safe_url = self._url
        if '@' in safe_url:
            protocol, rest = safe_url.split('://', 1)
            if '@' in rest:
                _, host_part = rest.rsplit('@', 1)
                safe_url = f"{protocol}://***@{host_part}"
        return f"RTSP: {safe_url} ({self._width}x{self._height} @ {self._fps:.2f}fps)"
    
    def is_live_source(self) -> bool:
        return True
    
    def reconnect(self) -> bool:
        """Attempt to reconnect to the RTSP stream."""
        self.release()
        try:
            self._cap = cv2.VideoCapture(self._url, cv2.CAP_FFMPEG)
            self._cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            return self._cap.isOpened()
        except Exception:
            return False
    
    def __iter__(self):
        """Make RTSPSource iterable."""
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
    def is_supported(cls, url: str) -> bool:
        """Check if the URL is an RTSP stream."""
        return url.lower().startswith(cls.PREFIXES)
