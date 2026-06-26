"""Terminal summary for the version compatibility suite.

Renders a human-readable PASS/FAIL/SKIP report after the pytest run, mirroring
the output of scripts/version_compatibility_check.sh.
"""

from .version_compatibility import CHECK_RESULTS, RUN_CONTEXT


PHASE_TITLES = {
    "release.ver": "[Phase 1] Submodule release.ver check",
    "cli": "[Phase 2] Installed binary version check",
}

_STATUS_GLYPH = {"pass": "✅", "fail": "❌", "skip": "⚠️"}


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    if not CHECK_RESULTS:
        return

    def line(text="", **markers):
        terminalreporter.write_line(text, **markers)

    line()
    line("=== Version Compatibility Check ===", bold=True)
    if RUN_CONTEXT.get("suite_version"):
        line(f"DX-AllSuite version: {RUN_CONTEXT['suite_version']}", cyan=True)
    if RUN_CONTEXT.get("matrix_source"):
        line(f"Compatibility matrix: {RUN_CONTEXT['matrix_source']}")

    passed = failed = skipped = 0
    for phase, title in PHASE_TITLES.items():
        rows = [r for r in CHECK_RESULTS if r.phase == phase]
        if not rows:
            continue
        line()
        line(title, bold=True)
        for row in rows:
            glyph = _STATUS_GLYPH.get(row.status, "?")
            if row.status == "pass":
                passed += 1
                line(f"  {glyph} {row.label:<20}: {row.actual} (expected: {row.expected})", green=True)
            elif row.status == "fail":
                failed += 1
                line(f"  {glyph} {row.label:<20}: {row.actual} (expected: {row.expected})", red=True)
            else:
                skipped += 1
                line(f"  {glyph} {row.label:<20}: {row.actual} (expected: {row.expected})", yellow=True)

    total = passed + failed
    line()
    line("--- Result ---", bold=True)
    if failed > 0:
        line(f"[FAIL] {passed}/{total} passed, {failed} failed, {skipped} skipped", red=True, bold=True)
    elif total == 0 and skipped > 0:
        line(f"[WARN] All checks skipped ({skipped} skipped). Nothing to verify.", yellow=True, bold=True)
    else:
        line(f"[SUCCESS] ALL PASS ({passed}/{total} passed, {skipped} skipped)", green=True, bold=True)
