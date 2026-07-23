"""Tests for the copy audit browser state matrix."""
from __future__ import annotations

import pytest

from tools.i18n_audit.browser_matrix import (
    COPY_AUDIT_STATES,
    modules_in_matrix,
    wait_for_copy_audit_state_ready,
)
from tools.i18n_audit.config import LANGUAGES


def test_browser_matrix_covers_all_modules():
    assert modules_in_matrix() == {
        "launcher",
        "dx_app",
        "dx_stream",
        "dx_modelzoo",
        "dx_compiler",
        "dx_planner",
        "dx_benchmark",
        "dx_monitor",
        "dx_agent_dev",
        "shared",
    }


def test_browser_matrix_has_seven_module_release_shape():
    assert len(COPY_AUDIT_STATES) == 13
    assert len(COPY_AUDIT_STATES) * len(LANGUAGES) == 78
    assert all(state.module != "dx_sandbox" for state in COPY_AUDIT_STATES)


def test_each_state_has_route_and_expected_selector():
    for state in COPY_AUDIT_STATES:
        assert state.module
        assert state.server_module
        assert state.state
        assert state.route.startswith("/")
        assert state.expected_selector


def test_matrix_uses_all_target_languages():
    for state in COPY_AUDIT_STATES:
        assert state.locales == LANGUAGES


class _FakePage:
    def __init__(self):
        self.waits = []

    def wait_for_function(self, script, *, timeout):
        self.waits.append((script, timeout))


def test_modelzoo_entry_waits_for_async_catalog_count_before_sampling():
    state = next(s for s in COPY_AUDIT_STATES if s.module == "dx_modelzoo" and s.state == "entry")
    page = _FakePage()

    wait_for_copy_audit_state_ready(page, state)

    assert len(page.waits) == 1
    script, timeout = page.waits[0]
    assert "#modelCount" in script
    assert r"^\d+\s+" in script
    assert "startsWith('0 ')" in script
    assert timeout == 8000


class _TimingOutPage:
    def wait_for_function(self, script, *, timeout):
        raise TimeoutError(f"Timeout {timeout}ms exceeded")


def test_state_readiness_timeout_reports_module_state_and_selector():
    state = next(s for s in COPY_AUDIT_STATES if s.module == "dx_modelzoo" and s.state == "entry")

    with pytest.raises(RuntimeError, match="dx_modelzoo/entry") as exc_info:
        wait_for_copy_audit_state_ready(_TimingOutPage(), state)

    message = str(exc_info.value)
    assert "#modelCount" in message
    assert "body" in message
    assert "8000ms" in message
