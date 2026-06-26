# SPDX-License-Identifier: Apache-2.0
"""Unit tests for ``_resolve_done_sentinel_dirs`` (conftest helper).

Covers the path-resolution behavior that several per-tool cascaded fixtures
duplicated incorrectly — when the agent emits a suite-root-relative DONE
output-dir but the fixture only tried ``workdir / rel``, the resulting path
had a duplicated prefix and ``exists()`` returned False, leaving
``scenario.output_dirs`` empty and triggering 7 false-fails per round.
"""

from __future__ import annotations

from pathlib import Path

from .conftest import _resolve_done_sentinel_dirs


_DONE_TEMPLATE = "[DX-AGENT-DEV: DONE (output-dir: {})]"


def _make_suite(tmp_path: Path) -> tuple[Path, Path]:
    """Create a minimal suite/sub-project layout under tmp_path.

    Returns (suite_root, stream_root) where stream_root is the workdir an
    agent would run inside (e.g., dx-runtime/dx_stream/).
    """
    suite = tmp_path / "suite"
    stream = suite / "dx-runtime" / "dx_stream"
    stream.mkdir(parents=True)
    return suite, stream


def test_workdir_relative_resolves(tmp_path, monkeypatch):
    """DONE path relative to workdir → resolved via workdir / rel."""
    suite, stream = _make_suite(tmp_path)
    monkeypatch.setattr("test_agent_e2e_scenarios.conftest.SUITE_ROOT", suite)

    sid = "20260521-205059_claude_sonnet46_yolo26n_cascaded"
    out = stream / "dx-agent-dev" / sid
    out.mkdir(parents=True)

    stdout = _DONE_TEMPLATE.format(f"dx-agent-dev/{sid}/")
    dirs, found = _resolve_done_sentinel_dirs(stdout, stream, [], name_filter="cascaded")

    assert found is True
    assert dirs == [out]


def test_suite_root_relative_resolves(tmp_path, monkeypatch):
    """The exact bug case: DONE path is suite-root-relative.

    ``workdir / rel`` produces a duplicated-prefix path that doesn't exist;
    the helper must fall back to ``SUITE_ROOT / rel`` and succeed.
    """
    suite, stream = _make_suite(tmp_path)
    monkeypatch.setattr("test_agent_e2e_scenarios.conftest.SUITE_ROOT", suite)

    sid = "20260521-205059_claude_sonnet46_yolo26n_cascaded"
    out = stream / "dx-agent-dev" / sid
    out.mkdir(parents=True)

    stdout = _DONE_TEMPLATE.format(f"dx-runtime/dx_stream/dx-agent-dev/{sid}/")
    dirs, found = _resolve_done_sentinel_dirs(stdout, stream, [], name_filter="cascaded")

    assert found is True
    assert dirs == [out]


def test_multi_path_split(tmp_path, monkeypatch):
    """Cross-project DONE with `` + `` separator → both paths resolved."""
    suite, stream = _make_suite(tmp_path)
    monkeypatch.setattr("test_agent_e2e_scenarios.conftest.SUITE_ROOT", suite)

    compile_dir = suite / "dx-compiler" / "dx-agent-dev" / "20260521-205059_c_compile"
    app_dir = suite / "dx-runtime" / "dx_app" / "dx-agent-dev" / "20260521-205059_c_inference"
    compile_dir.mkdir(parents=True)
    app_dir.mkdir(parents=True)

    rel_compile = "dx-compiler/dx-agent-dev/20260521-205059_c_compile/"
    rel_app = "dx-runtime/dx_app/dx-agent-dev/20260521-205059_c_inference/"
    stdout = _DONE_TEMPLATE.format(f"{rel_compile} + {rel_app}")

    dirs, found = _resolve_done_sentinel_dirs(stdout, stream, [], name_filter="")

    assert found is True
    assert set(dirs) == {compile_dir, app_dir}


def test_no_sentinel_returns_filtered_runner_dirs(tmp_path, monkeypatch):
    """Sentinel absent → fall through to name_filter-filtered runner_dirs."""
    suite, stream = _make_suite(tmp_path)
    monkeypatch.setattr("test_agent_e2e_scenarios.conftest.SUITE_ROOT", suite)

    a = stream / "dx-agent-dev" / "20260521-101010_x_cascaded"
    b = stream / "dx-agent-dev" / "20260521-111111_y_single_model"
    a.mkdir(parents=True)
    b.mkdir(parents=True)

    dirs, found = _resolve_done_sentinel_dirs(
        "no sentinel here", stream, [a, b], name_filter="cascaded"
    )

    assert found is False
    assert dirs == [a]


def test_sentinel_unresolvable_falls_back_to_runner_dirs(tmp_path, monkeypatch):
    """Sentinel found but no path resolves → return filtered runner_dirs.

    Guards against the regression that caused the original false-fails:
    a present-but-unresolvable sentinel must NOT silently produce an empty
    output_dirs list.
    """
    suite, stream = _make_suite(tmp_path)
    monkeypatch.setattr("test_agent_e2e_scenarios.conftest.SUITE_ROOT", suite)

    a = stream / "dx-agent-dev" / "20260521-101010_x_cascaded"
    b = stream / "dx-agent-dev" / "20260521-111111_y_other"
    a.mkdir(parents=True)
    b.mkdir(parents=True)

    stdout = _DONE_TEMPLATE.format("nonexistent/path/sid_cascaded/")
    dirs, found = _resolve_done_sentinel_dirs(stdout, stream, [a, b], name_filter="cascaded")

    assert found is True
    assert dirs == [a]
