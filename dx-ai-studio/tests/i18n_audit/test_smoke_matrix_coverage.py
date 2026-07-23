"""Automated coverage checks for the six-language browser smoke matrix."""

from tools.i18n_audit.browser_matrix import COPY_AUDIT_STATES, modules_in_matrix
from tools.i18n_audit.config import LANGUAGES

REQUIRED_MODULES = frozenset(
    {
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
)


def test_copy_audit_matrix_covers_entry_modules():
    covered = modules_in_matrix()
    missing = REQUIRED_MODULES - covered
    assert not missing, f"browser matrix missing modules: {sorted(missing)}"


def test_copy_audit_state_count_matches_smoke_plan():
    assert len(COPY_AUDIT_STATES) == 13
    assert len(LANGUAGES) == 6
