import pytest

from benchmark import env_fingerprint
from benchmark.env_fingerprint import (
    _normalize_version,
    _read_release_ver,
    resolve_dx_all_suite_version,
)


def test_read_release_ver_walks_up(tmp_path):
    root = tmp_path / "suite"
    root.mkdir()
    (root / "release.ver").write_text("v2.4.0\n")
    deep = root / "a" / "b"
    deep.mkdir(parents=True)
    assert _read_release_ver(deep) == "v2.4.0"


def test_read_release_ver_none_when_absent(tmp_path):
    assert _read_release_ver(tmp_path) is None


def test_resolve_explicit_wins(tmp_path):
    (tmp_path / "release.ver").write_text("v2.3.0")
    assert resolve_dx_all_suite_version("v9.9.9", start=tmp_path) == "v9.9.9"


def test_resolve_falls_back_to_release_ver(tmp_path):
    (tmp_path / "release.ver").write_text("v2.3.0")
    assert resolve_dx_all_suite_version(None, start=tmp_path) == "v2.3.0"


def test_resolve_none_when_nothing(tmp_path):
    assert resolve_dx_all_suite_version(None, start=tmp_path) is None


def test_resolve_whitespace_explicit_falls_back(tmp_path):
    (tmp_path / "release.ver").write_text("v2.3.0")
    assert resolve_dx_all_suite_version("   ", start=tmp_path) == "v2.3.0"


# --- version normalization (git-describe / dirty build policy) -------------

# The canonical case table for the version-normalization rule. The dashboard
# carries a second implementation of the same rule (`cleanVer` in
# benchmark/dashboard/app.js), and
# tests/test_dashboard_build.py::test_cleanver_parity_with_python_normalize_version
# holds it to this very table -- so a case added here exercises both copies.
NORMALIZE_CASES = [
    ("v3.4.0", "v3.4.0"),                              # clean release unchanged
    ("3.4.0", "3.4.0"),                                # no leading v preserved
    ("v3.4.0+9ef3f4c-dirty", "v3.4.0"),                # semver build metadata dropped
    ("v3.4.0+9ef3f4c", "v3.4.0"),                       # build metadata w/o dirty
    ("v3.4.0-9-g9ef3f4c-dirty", "v3.4.0"),             # git describe (no '+') + dirty
    ("v3.4.0-9-g9ef3f4c", "v3.4.0"),                    # git describe (no '+')
    ("v3.4.0-dirty", "v3.4.0"),                         # bare dirty marker
    ("v3.4.0-rc.4", "v3.4.0-rc.4"),                     # genuine pre-release preserved
    ("v3.4.0-rc.4+abc-dirty", "v3.4.0-rc.4"),           # pre-release kept, build meta dropped
    # dx_rt v3.5.0 switched the stamp to a trailing parenthesised form. Measured
    # from the real binary: `dxrt-cli --version` -> "DXRT v3.5.0 (build: 1.d0298f2)",
    # which `_get_dxrt_version` hands over as the version part below.
    ("v3.5.0 (build: 1.d0298f2)", "v3.5.0"),            # real v3.5.0 paren build stamp
    ("v3.5.0 (build: 2.abc1234)", "v3.5.0"),            # a second build of the SAME release
    ("v3.5.0(build: 1.d0298f2)", "v3.5.0"),             # stamp with no separating space
    ("v3.5.0-rc.4", "v3.5.0-rc.4"),                     # pre-release still preserved
    ("v3.5.0-rc.4 (build: 1.d0298f2)", "v3.5.0-rc.4"),  # pre-release kept, paren stamp dropped
    ("unknown", "unknown"),                             # sentinel unchanged
    ("", ""),                                           # empty unchanged
]


@pytest.mark.parametrize("raw,expected", NORMALIZE_CASES)
def test_normalize_version(raw, expected):
    assert _normalize_version(raw) == expected


def test_normalize_version_groups_builds_of_one_release():
    """The property the whole function exists for: two builds, one trend point.

    Without this, the first two v3.5.0 campaigns would appear in the Version
    Trend chart as two distinct versions and the dashboard label would read
    "rt 3.5.0 (build: 1.d0298f2)" instead of "rt 3.5.0".
    """
    build_1 = _normalize_version("v3.5.0 (build: 1.d0298f2)")
    build_2 = _normalize_version("v3.5.0 (build: 2.abc1234)")
    assert build_1 == build_2 == "v3.5.0"


def test_resolve_normalizes_dirty_explicit(tmp_path):
    # An explicit dirty version must be normalized so it groups/sorts with the
    # clean release instead of being treated as a distinct version.
    assert resolve_dx_all_suite_version("v3.4.0+9ef3f4c-dirty", start=tmp_path) == "v3.4.0"


def test_resolve_normalizes_dirty_release_ver(tmp_path):
    (tmp_path / "release.ver").write_text("v3.4.0+9ef3f4c-dirty\n")
    assert resolve_dx_all_suite_version(None, start=tmp_path) == "v3.4.0"


def _patch_dxrt(monkeypatch, version_line, s_output):
    monkeypatch.setattr(env_fingerprint.shutil, "which", lambda name: "/usr/bin/" + name)

    def fake_run(cmd, default="unknown"):
        if cmd[:2] == ["dxrt-cli", "--version"]:
            return version_line
        if cmd[:2] == ["dxrt-cli", "-s"]:
            return s_output
        return default

    monkeypatch.setattr(env_fingerprint, "_run", fake_run)


def test_get_npu_info_normalizes_rt_version_and_preserves_raw(monkeypatch):
    _patch_dxrt(monkeypatch, "DXRT v3.4.0+9ef3f4c-dirty", "* Device 0\n")
    info = env_fingerprint._get_npu_info()
    assert info["rt_version"] == "v3.4.0"
    assert info["rt_version_raw"] == "v3.4.0+9ef3f4c-dirty"


def test_get_npu_info_clean_version_has_no_raw_field(monkeypatch):
    _patch_dxrt(monkeypatch, "DXRT v3.4.0", "* Device 0\n")
    info = env_fingerprint._get_npu_info()
    assert info["rt_version"] == "v3.4.0"
    assert "rt_version_raw" not in info


# --- dx_rt v3.5.0 banner, end to end (subprocess boundary stubbed) ---------

# Line 1 measured from the real v3.5.0 binary; `dxrt-cli --version` then prints
# a minimum-driver/compiler requirements block, as the v3.4.0 output on the dev
# host does, so the stub is multi-line to exercise the line-1 extraction too.
_REAL_DXRT_CLI_V350 = (
    "DXRT v3.5.0 (build: 1.d0298f2)\n"
    "Minimum Driver Versions\n"
    "  Device Driver: v2.5.0\n"
)


def test_get_dxrt_version_v350_banner_normalizes_to_clean_version(monkeypatch):
    """The full real v3.5.0 banner must end up as a clean "v3.5.0".

    Split of responsibility: `_get_dxrt_version` strips the "DXRT " prefix and
    keeps line 1 verbatim -- the build stamp survives there so `_get_npu_info`
    can still record it as `rt_version_raw`. `_normalize_version` is what makes
    it clean. Asserting both halves pins that boundary.
    """
    _patch_dxrt(monkeypatch, _REAL_DXRT_CLI_V350, "* Device 0\n")
    raw = env_fingerprint._get_dxrt_version()
    assert raw == "v3.5.0 (build: 1.d0298f2)"
    assert _normalize_version(raw) == "v3.5.0"


def test_get_npu_info_normalizes_v350_paren_build_stamp(monkeypatch):
    # The recorded value the version trend groups on must be the clean release,
    # with the stamp kept beside it for auditing.
    _patch_dxrt(monkeypatch, _REAL_DXRT_CLI_V350, "* Device 0\n")
    info = env_fingerprint._get_npu_info()
    assert info["rt_version"] == "v3.5.0"
    assert info["rt_version_raw"] == "v3.5.0 (build: 1.d0298f2)"
