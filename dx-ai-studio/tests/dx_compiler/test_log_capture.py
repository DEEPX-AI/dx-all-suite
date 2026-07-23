"""DX Compiler log capture tests."""

import io
import sys
from pathlib import Path
from types import SimpleNamespace


def test_log_buffer_returns_lines_after_offset():
    from dx_compiler.core.log_capture import LogBuffer

    buffer = LogBuffer()
    buffer.append("first")
    buffer.append("second")

    assert buffer.get_new_lines(0) == ["first", "second"]
    assert buffer.get_new_lines(1) == ["second"]
    assert buffer.get_new_lines(2) == []


def test_log_capture_writes_through_and_captures_non_empty_lines():
    from dx_compiler.core.log_capture import LogBuffer, LogCapture

    original = io.StringIO()
    buffer = LogBuffer()
    capture = LogCapture(original, buffer)

    written = capture.write("hello\n\nworld\n")

    assert written == len("hello\n\nworld\n")
    assert original.getvalue() == "hello\n\nworld\n"
    assert buffer.get_new_lines(0) == ["hello", "world"]


def test_cr_aware_log_capture_filters_tqdm_and_tracks_subtask_progress():
    from dx_compiler.core.log_capture import LogBuffer, LogCapture

    original = io.StringIO()
    buffer = LogBuffer()
    job = SimpleNamespace(tqdm_sub=None)
    capture = LogCapture(original, buffer, handle_cr=True, job=job)

    progress = "Preparing Frontend IR:  92%|#####| 668/727 [00:01<00:00, 123.4it/s]\r"
    capture.write(progress)
    capture.write("real compiler error\n")

    assert original.getvalue() == progress + "real compiler error\n"
    assert buffer.get_new_lines(0) == ["real compiler error"]
    assert job.tqdm_sub == {
        "label": "Preparing Frontend IR",
        "percent": 92,
        "current": "668",
        "total": "727",
    }


def test_cr_aware_log_capture_flushes_non_tqdm_pending_line():
    from dx_compiler.core.log_capture import LogBuffer, LogCapture

    buffer = LogBuffer()
    capture = LogCapture(io.StringIO(), buffer, handle_cr=True)

    capture.write("partial compiler message")
    capture.flush_pending()

    assert buffer.get_new_lines(0) == ["partial compiler message"]


def test_cr_aware_log_capture_flush_pending_drops_partial_tqdm_fragment():
    from dx_compiler.core.log_capture import LogBuffer, LogCapture

    buffer = LogBuffer()
    capture = LogCapture(io.StringIO(), buffer, handle_cr=True)

    capture.write("50%|###")
    capture.flush_pending()

    assert buffer.get_new_lines(0) == []


def test_log_capture_public_api_is_explicit_and_runtime_checkable():
    import dx_compiler.core.log_capture as log_capture
    from dx_compiler.core.log_capture import TqdmProgressTarget

    assert log_capture.__all__ == ["LogBuffer", "LogCapture", "TqdmProgressTarget"]
    assert isinstance(SimpleNamespace(tqdm_sub=None), TqdmProgressTarget)
    assert not isinstance(SimpleNamespace(), TqdmProgressTarget)


def test_compiler_service_uses_shared_log_capture_classes():
    from dx_compiler.core.log_capture import LogBuffer, LogCapture
    import dx_compiler.core.compiler_service as compiler_service

    assert compiler_service.LogBuffer is LogBuffer
    assert compiler_service.LogCapture is LogCapture
