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

@pytest.mark.parametrize("raw,expected", [
    ("v3.4.0", "v3.4.0"),                              # clean release unchanged
    ("3.4.0", "3.4.0"),                                # no leading v preserved
    ("v3.4.0+9ef3f4c-dirty", "v3.4.0"),                # semver build metadata dropped
    ("v3.4.0+9ef3f4c", "v3.4.0"),                       # build metadata w/o dirty
    ("v3.4.0-9-g9ef3f4c-dirty", "v3.4.0"),             # git describe (no '+') + dirty
    ("v3.4.0-9-g9ef3f4c", "v3.4.0"),                    # git describe (no '+')
    ("v3.4.0-dirty", "v3.4.0"),                         # bare dirty marker
    ("v3.4.0-rc.4", "v3.4.0-rc.4"),                     # genuine pre-release preserved
    ("v3.4.0-rc.4+abc-dirty", "v3.4.0-rc.4"),           # pre-release kept, build meta dropped
    ("unknown", "unknown"),                             # sentinel unchanged
    ("", ""),                                           # empty unchanged
])
def test_normalize_version(raw, expected):
    assert _normalize_version(raw) == expected


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
