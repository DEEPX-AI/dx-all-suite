"""DX Monitor event access backed by the isolated telemetry supervisor."""
import copy
import threading


_LOCK = threading.RLock()
_PROVIDER = None


def set_provider(provider):
    """Set or clear the object that exposes ``events(since, limit)``."""
    global _PROVIDER
    with _LOCK:
        _PROVIDER = provider


def clear_provider_if(provider):
    """Clear the provider only when it remains the supplied object."""
    global _PROVIDER
    with _LOCK:
        if _PROVIDER is not provider:
            return False
        _PROVIDER = None
        return True


def init():
    """Compatibility no-op; native event registration happens in the worker."""
    return None


def get_events(since=0.0, limit=100):
    """Return cached telemetry events, or an empty list when unavailable."""
    with _LOCK:
        provider = _PROVIDER
    if provider is None:
        return []
    try:
        result = provider.events(since=since, limit=limit)
        with _LOCK:
            if _PROVIDER is not provider:
                return []
        return copy.deepcopy(result) if isinstance(result, list) else []
    except Exception:
        return []


def get_all_events():
    """Compatibility accessor for the complete bounded cache."""
    return get_events(since=0.0, limit=200)
