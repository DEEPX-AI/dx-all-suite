"""DX Monitor — 런타임 이벤트 수집기.

RuntimeEventDispatcher를 통해 쓰로틀링/에러/복구 이벤트를 버퍼링한다.
dx_engine이 없는 환경에서는 빈 리스트를 반환한다.
"""
import threading
import time
from collections import deque

_events = deque(maxlen=200)
_lock = threading.Lock()
_initialized = False

_LEVEL_NAMES = {1: "INFO", 2: "WARNING", 3: "ERROR", 4: "CRITICAL"}
_CODE_NAMES = {
    2000: "WRITE_INPUT", 2001: "READ_OUTPUT",
    2002: "MEMORY_OVERFLOW", 2003: "MEMORY_ALLOCATION",
    2004: "DEVICE_EVENT", 2005: "RECOVERY_OCCURRED",
    2006: "TIMEOUT_OCCURRED", 2007: "THROTTLING_NOTICE",
    2008: "THROTTLING_EMERGENCY", 2009: "UNKNOWN",
}


def _on_event(level, etype, code, message, timestamp):
    entry = {
        "ts": timestamp,
        "time": time.time(),
        "level": _LEVEL_NAMES.get(level, str(level)),
        "level_num": level,
        "type": etype,
        "code": _CODE_NAMES.get(code, str(code)),
        "code_num": code,
        "message": message,
    }
    with _lock:
        _events.append(entry)


def init():
    """RuntimeEventDispatcher에 핸들러 등록. SDK 없으면 무시."""
    global _initialized
    if _initialized:
        return
    _initialized = True
    try:
        from dx_engine.runtime_event_dispatcher import RuntimeEventDispatcher
        dispatcher = RuntimeEventDispatcher()
        dispatcher.set_current_level(RuntimeEventDispatcher.LEVEL.INFO)
        dispatcher.register_event_handler(_on_event)
        print("[DX Monitor] RuntimeEventDispatcher handler registered")
    except Exception:
        print("[DX Monitor] RuntimeEventDispatcher unavailable — event log disabled")


def get_events(since=0.0, limit=100):
    """since(unix timestamp) 이후 이벤트를 최대 limit개 반환."""
    with _lock:
        filtered = [e for e in _events if e["time"] > since]
    return filtered[-limit:]


def get_all_events():
    """전체 이벤트 버퍼 반환."""
    with _lock:
        return list(_events)
