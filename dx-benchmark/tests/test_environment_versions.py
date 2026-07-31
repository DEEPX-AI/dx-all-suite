"""Environment section version reporting.

The report surfaces the installed-binary SDK versions (including the RT commit) and the
dx-all-suite RELEASE the SDKs were built from (DX-AllSuite). It no longer prints a git
"Source Provenance" section: the checkout the benchmark tool ran from does not necessarily
match the SDK build source (e.g. SDKs built from a release, tool run from a dev fork), so
that git state was misleading. Authoritative provenance = installed binaries + DX-AllSuite.
"""
from benchmark.reporter import _add_environment_section


def _fp():
    return {
        "host": {}, "product_name": None,
        "dx_all_suite_version": "v2.3.3",
        "npu": {"sku": "M1", "rt_version": "v3.4.0", "rt_version_raw": "v3.4.0+ed51532",
                "driver": "v2.5.1", "firmware": "v2.7.1"},
        "tools": {},
    }


def test_environment_shows_rt_commit_and_dxas_version():
    lines = []
    _add_environment_section(lines, _fp())
    out = "\n".join(lines)
    assert "v3.4.0+ed51532" in out                       # installed-binary RT commit still surfaced
    assert "DX-AllSuite" in out and "v2.3.3" in out       # release the SDKs were built from


def test_environment_has_no_git_source_provenance():
    lines = []
    _add_environment_section(lines, _fp())
    out = "\n".join(lines)
    assert "Source Provenance" not in out
    assert "Describe" not in out          # git provenance table header gone


def test_dxas_version_falls_back_when_unstamped():
    fp = _fp()
    del fp["dx_all_suite_version"]
    lines = []
    _add_environment_section(lines, fp)
    assert "| DX-AllSuite | N/A |" in "\n".join(lines)
