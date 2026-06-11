"""
Thread-safe queue for asynchronous processing pipelines.
"""

import queue
import threading
from typing import TypeVar, Generic, Optional

T = TypeVar('T')


class SafeQueue(Generic[T]):
    """
    Thread-safe queue with additional utility methods.
    
    Used in async inference pipelines for passing data between threads.
    """
    
    def __init__(self, maxsize: int = 0, max_size: int = None):
        """
        Initialize the queue.
        
        Args:
            maxsize: Maximum queue size (0 for unlimited)
            max_size: Alias for maxsize (deprecated, for backward compatibility)
        """
        # Support both maxsize and max_size for compatibility
        size = max_size if max_size is not None else maxsize
        self._queue: queue.Queue = queue.Queue(maxsize=size)
        self._stopped = threading.Event()
    
    def put(self, item: T, block: bool = True, timeout: Optional[float] = None) -> bool:
        """
        Add an item to the queue.
        
        Args:
            item: Item to add
            block: Whether to block if queue is full
            timeout: Maximum time to wait (None for infinite)
            
        Returns:
            True if item was added, False if stopped or timeout
        """
        if self._stopped.is_set():
            return False
        
        try:
            self._queue.put(item, block=block, timeout=timeout)
            return True
        except queue.Full:
            return False
    
    def get(self, block: bool = True, timeout: Optional[float] = None) -> Optional[T]:
        """
        Get an item from the queue.
        
        Args:
            block: Whether to block if queue is empty
            timeout: Maximum time to wait (None for infinite)
            
        Returns:
            Item from queue, or None if stopped/timeout
        """
        if self._stopped.is_set() and self._queue.empty():
            return None
        
        try:
            return self._queue.get(block=block, timeout=timeout)
        except queue.Empty:
            return None
    
    def try_get(self) -> Optional[T]:
        """
        Non-blocking get attempt.
        
        Returns:
            Item if available, None otherwise
        """
        return self.get(block=False)
    
    def size(self) -> int:
        """Get current queue size."""
        return self._queue.qsize()
    
    def qsize(self) -> int:
        """Get current queue size (alias for size(), compatible with queue.Queue)."""
        return self._queue.qsize()
    
    def empty(self) -> bool:
        """Check if queue is empty."""
        return self._queue.empty()
    
    def full(self) -> bool:
        """Check if queue is full."""
        return self._queue.full()
    
    def clear(self) -> int:
        """
        Clear all items from the queue.
        
        Returns:
            Number of items cleared
        """
        count = 0
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
                count += 1
            except queue.Empty:
                break
        return count
    
    def stop(self) -> None:
        """Signal the queue to stop processing."""
        self._stopped.set()
    
    def is_stopped(self) -> bool:
        """Check if stop was signaled."""
        return self._stopped.is_set()
    
    def reset(self) -> None:
        """Reset the stop flag and clear the queue."""
        self._stopped.clear()
        self.clear()

    def put_nowait(self, item: T) -> bool:
        """Non-blocking put. Returns True if successful, False if full."""
        return self.put(item, block=False)

    def get_nowait(self) -> Optional[T]:
        """Non-blocking get. Returns item or None if empty."""
        return self.get(block=False)
