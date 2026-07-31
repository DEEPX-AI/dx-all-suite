"""dx-benchmark — DEEPX NPU benchmark suite.

``__version__`` is the tool's own SemVer, read from the component's ``release.ver``
(the single source of truth, matching the suite convention where every component ships a
``release.ver``). It is independent of:
  - the dx-all-suite release it MEASURES (recorded per-run as ``dx_all_suite_version``), and
  - the measurement methodology version (``benchmark.config.PROTOCOL_VERSION``).

Bump it by editing ``dx-benchmark/release.ver`` (tool code/CLI/output-schema changes only;
a new suite-version data campaign with an unchanged tool does NOT bump it).
"""

from pathlib import Path


def _read_version() -> str:
    """Read the tool version from ``dx-benchmark/release.ver`` (v-prefix stripped)."""
    try:
        raw = (Path(__file__).resolve().parent.parent / "release.ver").read_text().strip()
    except OSError:
        return "0.1.0"  # fallback if release.ver is missing
    return raw[1:] if raw[:1].lower() == "v" else raw


__version__ = _read_version()
"""dx-benchmark tool version (SemVer), sourced from release.ver. Beta line starts at 0.x."""
