"""dx-benchmark tool self-version (SemVer).

The tool carries its OWN version, independent of:
  - the dx-all-suite release it MEASURES (``dx_all_suite_version``), and
  - the measurement methodology version (``PROTOCOL_VERSION``).

It is exposed as ``benchmark.__version__``, printed by ``python -m benchmark
--version``, and stamped into every ``environment.json`` fingerprint as
``benchmark_tool_version`` for provenance.
"""
import re
import subprocess
import sys
from pathlib import Path

import benchmark
from benchmark.env_fingerprint import collect_fingerprint

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_version_is_semver_and_pinned():
    assert re.fullmatch(r"\d+\.\d+\.\d+", benchmark.__version__), benchmark.__version__
    assert benchmark.__version__ == "0.1.0"


def test_cli_version_flag_prints_version():
    proc = subprocess.run(
        [sys.executable, "-m", "benchmark", "--version"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert benchmark.__version__ in (proc.stdout + proc.stderr)


def test_fingerprint_stamps_tool_version():
    fp = collect_fingerprint()
    assert fp.get("benchmark_tool_version") == benchmark.__version__


def test_tool_version_distinct_from_protocol_version():
    # tool version and measurement-protocol version are separate axes
    from benchmark.config import PROTOCOL_VERSION
    assert benchmark.__version__ != PROTOCOL_VERSION


def test_protocol_version_starts_at_v1_for_public_release():
    # The measurement-protocol version is public-facing (REPORT.md, ANALYSIS). It starts at
    # v1 for the first public release — internal pre-release iterations are not exposed.
    from benchmark.config import PROTOCOL_VERSION
    assert PROTOCOL_VERSION == "v1"


def test_release_ver_file_is_source_of_truth():
    # Suite convention: every component ships a `release.ver` (v-prefixed) — the single
    # source of truth for its version. __version__ derives from it (v stripped).
    root = Path(benchmark.__file__).resolve().parent.parent  # dx-benchmark/
    rv = (root / "release.ver").read_text().strip()
    assert rv == "v0.1.0", rv
    assert rv.lstrip("v") == benchmark.__version__


def test_suite_version_not_shadowed_by_own_release_ver():
    # dx-benchmark's OWN release.ver (its tool version) must NOT be mistaken for the
    # measured dx-all-suite version when resolving with the default (in-package) start.
    from benchmark.env_fingerprint import resolve_dx_all_suite_version
    v = resolve_dx_all_suite_version(None)
    assert v not in ("0.1.0", "v0.1.0"), f"suite version shadowed by tool release.ver: {v!r}"


def test_report_environment_section_shows_tool_version():
    from benchmark.reporter import _add_environment_section
    fp = {
        "host": {}, "tools": {},
        "npu": {"sku": "M1", "rt_version": "v3.4.0", "driver": "v2.5.1"},
        "dx_all_suite_version": "v2.4.0",
        "benchmark_tool_version": "0.1.0",
    }
    lines = []
    _add_environment_section(lines, fp)
    out = "\n".join(lines)
    assert "Benchmark Tool" in out
    assert "0.1.0" in out


def test_aggregator_run_and_env_carry_tool_version():
    from pathlib import Path
    from benchmark.aggregator import _normalize_run, _build_environment_summary
    fp = {
        "host": {}, "tools": {}, "software": {"dx_stream": "3.1.0"},
        "npu": {"sku": "M1", "rt_version": "v3.4.0", "driver": "v2.5.1"},
        "dx_all_suite_version": "v2.4.0",
        "benchmark_tool_version": "0.1.0",
    }
    run = _normalize_run("20260101_000000", "ENV", Path("."), fp)
    assert run.get("benchmark_tool_version") == "0.1.0"
    env = _build_environment_summary("ENV", "20260101_000000", fp)
    assert env.get("benchmark_tool_version") == "0.1.0"
