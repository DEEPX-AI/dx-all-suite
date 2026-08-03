"""DX Monitor telemetry initialization without native runtime imports.

The native runtime is intentionally isolated in ``telemetry_worker.py``.  The
Studio process owns only a :class:`TelemetrySupervisor` cache consumer.
"""
import os
import threading

from dx_monitor.core.config import DX_APP_ROOT
from dx_monitor.core.telemetry_supervisor import TelemetrySupervisor


_LOCK = threading.RLock()
_LIFECYCLE = threading.Condition(_LOCK)
_SUPERVISOR = None
_STOPPING = False


def _explicit_mock_enabled():
    """Return whether the operator explicitly requested demo telemetry."""
    return os.environ.get("DX_MONITOR_EXPLICIT_MOCK") == "1"


def init():
    """Start one telemetry worker and connect Monitor cache consumers to it."""
    global _STOPPING, _SUPERVISOR
    from dx_monitor.core import events
    from shared import hardware as shared_hardware

    startup_error = None
    with _LIFECYCLE:
        while _STOPPING:
            _LIFECYCLE.wait()
        if _SUPERVISOR is not None:
            return _SUPERVISOR

        supervisor = TelemetrySupervisor()
        try:
            supervisor.start()
            shared_hardware.init_hw(
                telemetry=supervisor,
                explicit_mock=_explicit_mock_enabled(),
                app_root=DX_APP_ROOT,
            )
            events.set_provider(supervisor)
        except Exception as error:
            _STOPPING = True
            startup_error = error
        else:
            _SUPERVISOR = supervisor
            return supervisor

    try:
        shared_hardware.invalidate_telemetry_if(supervisor)
    finally:
        try:
            events.clear_provider_if(supervisor)
        finally:
            try:
                supervisor.stop()
            except Exception:
                # The startup failure remains the actionable error after its
                # exact shared bindings have been invalidated.
                pass
            finally:
                shared_hardware.detach_telemetry_if(supervisor)
                with _LIFECYCLE:
                    _STOPPING = False
                    _LIFECYCLE.notify_all()
    raise startup_error.with_traceback(startup_error.__traceback__)


def shutdown():
    """Stop the owned telemetry supervisor and detach the events provider."""
    global _STOPPING, _SUPERVISOR
    with _LIFECYCLE:
        if _STOPPING:
            while _STOPPING:
                _LIFECYCLE.wait()
            return
        supervisor = _SUPERVISOR
        if supervisor is None:
            return
        _STOPPING = True

    from dx_monitor.core import events
    from shared import hardware as shared_hardware

    try:
        shared_hardware.invalidate_telemetry_if(supervisor)
    finally:
        try:
            events.clear_provider_if(supervisor)
        finally:
            try:
                supervisor.stop()
            finally:
                shared_hardware.detach_telemetry_if(supervisor)
                with _LIFECYCLE:
                    if _SUPERVISOR is supervisor:
                        _SUPERVISOR = None
                    _STOPPING = False
                    _LIFECYCLE.notify_all()
