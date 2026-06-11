"""
Input Factory - Factory Method pattern implementation.

This factory automatically creates the appropriate input source
based on the input path or type.
"""

from pathlib import Path
from typing import Optional, Union

from ..base.i_input_source import IInputSource, InputType
from .image_source import ImageSource
from .video_source import VideoSource
from .camera_source import CameraSource
from .rtsp_source import RTSPSource


class InputFactory:
    """
    Factory for creating input sources.
    
    Implements the Factory Method pattern to automatically create
    the appropriate input source based on the input type.
    
    Usage:
        # Auto-detect from file path
        source = InputFactory.create("/path/to/image.jpg")
        source = InputFactory.create("/path/to/video.mp4")
        source = InputFactory.create("rtsp://server/stream")
        
        # Explicit creation
        source = InputFactory.create_from_camera(0)
        source = InputFactory.create_from_rtsp("rtsp://...")
    """
    
    @classmethod
    def create(cls, input_path: str, 
               camera_id: Optional[int] = None) -> IInputSource:
        """
        Auto-detect and create appropriate input source.
        
        Args:
            input_path: Path to file, RTSP URL, or "camera:N" for camera
            camera_id: Optional camera ID (overrides input_path)
            
        Returns:
            Appropriate IInputSource implementation
            
        Raises:
            ValueError: If input type cannot be determined
            FileNotFoundError: If file does not exist
            RuntimeError: If source cannot be opened
        """
        # Check for camera ID override
        if camera_id is not None:
            return CameraSource(camera_id)
        
        # Check for camera path format "camera:N"
        if input_path.lower().startswith('camera:'):
            try:
                device_id = int(input_path.split(':')[1])
                return CameraSource(device_id)
            except (IndexError, ValueError):
                return CameraSource(0)
        
        # Check for RTSP stream
        if RTSPSource.is_supported(input_path):
            return RTSPSource(input_path)
        
        # Check for image file
        if ImageSource.is_supported(input_path):
            return ImageSource(input_path)
        
        # Check for video file
        if VideoSource.is_supported(input_path):
            return VideoSource(input_path)
        
        # Unknown type - try video as fallback
        try:
            return VideoSource(input_path)
        except (FileNotFoundError, ValueError, RuntimeError):
            pass
        
        raise ValueError(f"Cannot determine input type for: {input_path}")
    
    @classmethod
    def create_from_file(cls, path: str) -> IInputSource:
        """
        Create input source from a file path (image or video).
        
        Args:
            path: Path to the file
            
        Returns:
            ImageSource or VideoSource
        """
        if ImageSource.is_supported(path):
            return ImageSource(path)
        elif VideoSource.is_supported(path):
            return VideoSource(path)
        else:
            raise ValueError(f"Unsupported file format: {path}")
    
    @classmethod
    def create_from_camera(cls, device_id: int = 0,
                           width: Optional[int] = None,
                           height: Optional[int] = None,
                           fps: Optional[float] = None) -> CameraSource:
        """
        Create camera input source.
        
        Args:
            device_id: Camera device ID
            width: Desired capture width
            height: Desired capture height
            fps: Desired capture FPS
            
        Returns:
            CameraSource
        """
        return CameraSource(device_id, width, height, fps)
    
    @classmethod
    def create_from_rtsp(cls, url: str,
                         buffer_size: int = 1) -> RTSPSource:
        """
        Create RTSP stream input source.
        
        Args:
            url: RTSP URL
            buffer_size: Buffer size for low latency
            
        Returns:
            RTSPSource
        """
        return RTSPSource(url, buffer_size)
    
    @classmethod
    def detect_type(cls, input_path: str) -> InputType:
        """
        Detect the input type without creating a source.
        
        Args:
            input_path: Path to file, URL, or camera identifier
            
        Returns:
            InputType enumeration value
        """
        if input_path.lower().startswith('camera:'):
            return InputType.CAMERA
        
        if RTSPSource.is_supported(input_path):
            return InputType.RTSP
        
        if ImageSource.is_supported(input_path):
            return InputType.IMAGE
        
        if VideoSource.is_supported(input_path):
            return InputType.VIDEO
        
        return InputType.UNKNOWN
    
    @classmethod
    def get_supported_image_extensions(cls) -> set:
        """Get set of supported image file extensions."""
        return ImageSource.EXTENSIONS
    
    @classmethod
    def get_supported_video_extensions(cls) -> set:
        """Get set of supported video file extensions."""
        return VideoSource.EXTENSIONS
