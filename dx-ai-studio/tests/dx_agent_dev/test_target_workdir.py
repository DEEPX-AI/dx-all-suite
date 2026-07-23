"""Target workdir resolution — mirrors the original SCENARIO_WORKDIRS
(.deepx/e2e/test.sh): suite / dx-runtime / dx_app / dx_stream / dx-compiler."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_agent_dev"))


def test_resolve_known_targets():
    from core.config import resolve_target, SUITE_ROOT
    assert resolve_target("suite") == SUITE_ROOT.resolve()
    assert resolve_target("dx-runtime") == (SUITE_ROOT / "dx-runtime").resolve()
    assert resolve_target("dx_app") == (SUITE_ROOT / "dx-runtime" / "dx_app").resolve()
    assert resolve_target("dx_stream") == (SUITE_ROOT / "dx-runtime" / "dx_stream").resolve()
    assert resolve_target("dx-compiler") == (SUITE_ROOT / "dx-compiler").resolve()


def test_resolve_defaults_and_rejects_unknown():
    from core.config import resolve_target, SUITE_ROOT
    assert resolve_target("") == SUITE_ROOT.resolve()
    assert resolve_target(None) == SUITE_ROOT.resolve()
    # unknown / traversal attempts fall back to the suite root (never escapes it)
    assert resolve_target("../../etc") == SUITE_ROOT.resolve()
    assert resolve_target("/etc/passwd") == SUITE_ROOT.resolve()
    assert resolve_target("nonsense") == SUITE_ROOT.resolve()


def test_resolved_target_is_within_suite_root():
    from core.config import resolve_target, SUITE_ROOT
    root = SUITE_ROOT.resolve()
    for name in ("suite", "dx-runtime", "dx_app", "dx_stream", "dx-compiler", "junk", ""):
        resolved = resolve_target(name)
        # must always stay within the suite root
        resolved.relative_to(root)  # raises if outside
