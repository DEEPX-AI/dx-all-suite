"""Browser copy audit state matrix.

Maps every auditable module × UI state to a route, expected DOM selector,
and the server module needed to serve it.  The ``shared`` module is served
through ``launcher`` because its toolbar/help shell renders inside the
launcher's HTML.
"""
from __future__ import annotations

from dataclasses import dataclass

try:
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
except ImportError:  # pragma: no cover - browser evidence tests install Playwright.
    PlaywrightTimeoutError = TimeoutError

from .config import LANGUAGES


@dataclass(frozen=True)
class CopyAuditState:
    """One browser state to visit during the copy audit."""

    module: str
    state: str
    route: str
    expected_selector: str
    server_module: str | None = None
    locales: tuple[str, ...] = LANGUAGES
    ready_function: str | None = None
    ready_timeout_ms: int = 8000

    def __post_init__(self) -> None:
        if self.server_module is None:
            object.__setattr__(self, "server_module", self.module)


_MODELZOO_CATALOG_READY_FUNCTION = """() => {
    const countText = document.querySelector('#modelCount')?.textContent?.trim() || '';
    return /^\\d+\\s+/.test(countText) && !countText.startsWith('0 ');
}"""


COPY_AUDIT_STATES: tuple[CopyAuditState, ...] = (
    CopyAuditState("launcher", "home", "/", "body"),
    CopyAuditState("launcher", "about", "/about", "body"),
    CopyAuditState("launcher", "sdk-library", "/sdk-library", "body"),
    CopyAuditState("dx_app", "entry", "/", "body"),
    CopyAuditState("dx_stream", "entry", "/", "body"),
    CopyAuditState(
        "dx_modelzoo",
        "entry",
        "/",
        "body",
        ready_function=_MODELZOO_CATALOG_READY_FUNCTION,
    ),
    CopyAuditState("dx_compiler", "entry", "/", "body"),
    CopyAuditState("dx_planner", "entry", "/", "body"),
    CopyAuditState("dx_benchmark", "entry", "/", "body"),
    CopyAuditState("dx_monitor", "entry", "/", "body"),
    CopyAuditState("dx_agent_dev", "entry", "/", "body"),
    CopyAuditState("dx_agent_dev", "model-picker", "/", "#model-select"),
    CopyAuditState(
        "shared",
        "launcher-toolbar-and-help-shell",
        "/",
        "body",
        server_module="launcher",
    ),
)


def modules_in_matrix() -> set[str]:
    """Return the set of module names covered by the audit matrix."""
    return {s.module for s in COPY_AUDIT_STATES}


def wait_for_copy_audit_state_ready(page, state: CopyAuditState) -> None:
    """Wait for state-specific async rendering before text sampling."""
    if state.ready_function:
        try:
            page.wait_for_function(state.ready_function, timeout=state.ready_timeout_ms)
        except (TimeoutError, PlaywrightTimeoutError) as exc:
            raise RuntimeError(
                f"Readiness gate timed out for {state.module}/{state.state} "
                f"(expected selector: {state.expected_selector}, "
                f"timeout: {state.ready_timeout_ms}ms). "
                f"Ready function: {state.ready_function}"
            ) from exc
