"""The dx_rt minimum-version gate: parsing, the threshold, and its scope.

Scope matters as much as the threshold -- and the scope is *everything*, along
two axes. Across families: the gate is not about `--max-throughput` being
callable; it is about every row of a campaign describing the same runtime. The
E2E / multi-stream families drive GStreamer pipelines whose dxstream plugin
links the same libdxrt.so that ships with `run_model`, so the runtime version
moves their numbers too. Preflight therefore blocks a too-old runtime for every
family, not just the model one.

Across binaries: the recorded `npu.rt_version` -- the value that lands in the
results and the version trend -- comes from `dxrt-cli --version`, not from the
`run_model --help` banner. Gating only `run_model` guaranteed a version nothing
records, so `dxrt-cli` is gated at the same threshold; see
test_mixed_install_is_refused_because_dxrt_cli_sets_the_recorded_rt_version.
"""

import shutil
import subprocess

import pytest

from benchmark import env_fingerprint as ef
from benchmark.env_fingerprint import _parse_dxrt_version, check_preflight


def test_parse_dxrt_version_from_help_first_line():
    # The banner is argv[0]-dependent: `run_model` is a symlink to `dxrun`,
    # so both spellings occur in the wild. Verified against real v3.4.0/v3.5.0.
    assert _parse_dxrt_version("DXRT v3.5.0 run_model") == (3, 5, 0)
    assert _parse_dxrt_version("DXRT v3.5.0 dxrun") == (3, 5, 0)
    assert _parse_dxrt_version("DXRT v3.4.0 run_model") == (3, 4, 0)


def test_parse_dxrt_version_tolerates_build_stamp():
    # `_normalize_version` is not applied here, so a dirty build must still parse.
    assert _parse_dxrt_version("DXRT v3.5.0+9ef3f4c-dirty run_model") == (3, 5, 0)


def test_parse_dxrt_version_accepts_prerelease_as_that_version():
    # D6: staging itself is a v3.5.0-rc and does carry --max-throughput.
    assert _parse_dxrt_version("DXRT v3.5.0-rc.4 dxrun") == (3, 5, 0)


def test_parse_dxrt_version_tolerates_missing_v_prefix():
    # A banner that drops the 'v' must not read as "too old" on every host.
    assert _parse_dxrt_version("DXRT 3.5.0 run_model") == (3, 5, 0)


def test_parse_dxrt_version_returns_none_on_garbage():
    assert _parse_dxrt_version("unknown") is None
    assert _parse_dxrt_version(None) is None
    assert _parse_dxrt_version("") is None


def test_preflight_rejects_outdated_run_model():
    fp = {"missing_required": [],
          "outdated_required": [("run_model", "DXRT v3.4.0 run_model", "v3.5.0")]}
    ok, errors = check_preflight(fp)
    assert ok is False
    assert any("run_model" in e and "3.4.0" in e and "3.5.0" in e for e in errors)


def test_preflight_rejects_unparseable_version():
    # D5: fail closed. A present-but-broken run_model must not start a campaign.
    fp = {"missing_required": [], "outdated_required": [("run_model", "unknown", "v3.5.0")]}
    ok, errors = check_preflight(fp)
    assert ok is False
    assert any("unknown" in e for e in errors)


def test_preflight_still_rejects_a_missing_tool():
    # Absence and obsolescence are both preflight failures, with distinct messages.
    ok, errors = check_preflight({"missing_required": ["run_model"], "outdated_required": []})
    assert ok is False
    assert any("run_model" in e and "not found" in e for e in errors)


def test_preflight_passes_when_nothing_is_wrong():
    ok, errors = check_preflight({"missing_required": [], "outdated_required": []})
    assert ok is True
    assert errors == []


def test_fingerprint_flags_this_hosts_run_model():
    # Integration: whatever is installed here, the two lists must agree with it.
    from benchmark.env_fingerprint import (collect_fingerprint, MIN_TOOL_VERSIONS,
                                           _parse_dxrt_version)
    fp = collect_fingerprint()
    info = fp["tools"]["run_model"]
    outdated = dict((t, (f, n)) for t, f, n in fp["outdated_required"])
    if not info["available"]:
        assert "run_model" in fp["missing_required"]
        return
    found = _parse_dxrt_version(info["version"])
    if found is None or found < MIN_TOOL_VERSIONS["run_model"]:
        assert "run_model" in outdated
    else:
        assert "run_model" not in outdated


# (banner, must_be_blocked) -- pins the threshold AND the fail-closed policy.
# Verified to kill all four mutants that survived the original suite:
#   min->(3,4,0) | min->(9,9,9) | `<` -> `<=` | `is None or` -> `is not None and`
_VERSION_TABLE = [
    ("DXRT v3.4.0 run_model",  True),   # below the minimum
    ("DXRT v3.5.0 run_model",  False),  # exactly the minimum -- must NOT be blocked
    ("DXRT v3.10.0 run_model", False),  # 10 > 5 numerically, not lexically
    ("unknown",                True),   # D5: unparseable fails closed
]


@pytest.mark.parametrize("banner,blocked", _VERSION_TABLE)
def test_version_gate_decision_table(monkeypatch, banner, blocked):
    real = ef._tool_version

    def fake(name):
        if name == "run_model":
            return {"path": "/stub/run_model", "version": banner, "available": True}
        return real(name)

    monkeypatch.setattr(ef, "_tool_version", fake)
    fp = ef.collect_fingerprint()
    flagged = [t for t, _f, _n in fp["outdated_required"]]
    assert ("run_model" in flagged) is blocked, \
        f"{banner!r}: expected blocked={blocked}, got outdated_required={fp['outdated_required']}"


def test_minimum_version_is_pinned():
    """A literal pin, so raising or lowering the bar is a deliberate edit.

    Mirrors tests/test_tool_version.py::test_protocol_version_is_v2_for_dxrun_sweep,
    which pins PROTOCOL_VERSION the same way and for the same reason. The exact
    set of gated tools is pinned too: dropping `dxrt-cli` back out would silently
    un-gate the binary that sets the recorded `rt_version`, and adding a tool
    without a `_tool_version` extraction branch would block every host.
    """
    assert ef.MIN_TOOL_VERSIONS == {"run_model": (3, 5, 0), "dxrt-cli": (3, 5, 0)}


@pytest.mark.parametrize("family", ["model", "e2e", "multi", "all"])
def test_version_gate_blocks_every_family(monkeypatch, capsys, family):
    """Pins the scope: a too-old runtime stops `run` whatever --family asks for.

    This is the property that family scoping would break, so it is asserted the
    only way that actually bites -- by driving ``cmd_run`` itself with a v3.4.0
    fingerprint and requiring rc=1 plus the "too old" message. Re-introducing a
    ``if "model" in families`` guard lets the pipeline families walk past the
    gate, and the ``_resolve_output_dir`` tripwire below turns that into a
    failure instead of a silently degraded campaign. An assertion on the
    ``families`` expression alone could not do that: the expression would no
    longer exist.
    """
    from benchmark import __main__ as m

    fp = {"missing_required": [], "missing_e2e": [],
          "outdated_required": [("run_model", "DXRT v3.4.0 run_model", "v3.5.0")]}
    monkeypatch.setattr(m, "collect_fingerprint", lambda: fp)
    monkeypatch.setattr(m, "check_cpu_governor", lambda _fp: None)

    def _tripwire(*_a, **_k):
        raise AssertionError(
            f"--family {family} walked past the version gate on a v3.4.0 runtime"
        )

    monkeypatch.setattr(m, "_resolve_output_dir", _tripwire)

    args = m._build_parser().parse_args(["run", "--family", family])
    rc = m.cmd_run(args)
    out = capsys.readouterr().out

    assert rc == 1, f"--family {family}: expected the version gate to block, got rc={rc}"
    assert "too old" in out, f"--family {family}: blocked, but not by the version gate:\n{out}"


# ── dxrt-cli: the binary the recorded `rt_version` actually comes from ──────

# Captured verbatim from `dxrt-cli --version` on a v3.4.0 host. Unlike
# run_model's one-line `--help` banner, this is a block: the version line is
# followed by minimum driver/compiler requirements, so only line 1 is the
# runtime version and everything below it must be dropped.
_REAL_DXRT_CLI_V340 = (
    "DXRT v3.4.0+fad14d6\n"
    "Minimum Driver Versions\n"
    "  Device Driver: v2.5.0\n"
    "  PCIe Driver: v2.4.0\n"
    "  Firmware: v2.7.0\n"
    "Minimum Compiler Versions\n"
    "  Compiler: v1.18.1\n"
    "  .dxnn File Format: v6"
)
_V350_RUN_MODEL = "DXRT v3.5.0 run_model"


def _stub_dxrt_banners(monkeypatch, run_model_help, dxrt_cli_version):
    """Make `run_model --help` / `dxrt-cli --version` report the given banners.

    Stubs at the subprocess boundary (``_run``) instead of at ``_tool_version``,
    so the production extraction path -- which flag is passed and which line is
    kept -- is exercised rather than replaced. ``shutil.which`` is stubbed for
    the same two names so the outcome does not depend on what this host has
    installed; every other command still reaches the real implementation.
    """
    real_which, real_run = ef.shutil.which, ef._run

    def which(name, *a, **k):
        if name in ("run_model", "dxrt-cli"):
            return f"/stub/{name}"
        return real_which(name, *a, **k)

    def run(cmd, default="unknown"):
        if cmd[:2] == ["run_model", "--help"]:
            return run_model_help
        if cmd[:2] == ["dxrt-cli", "--version"]:
            return dxrt_cli_version
        return real_run(cmd, default)

    monkeypatch.setattr(ef.shutil, "which", which)
    monkeypatch.setattr(ef, "_run", run)


def test_dxrt_cli_version_is_captured_and_is_the_first_line_only(monkeypatch):
    """Prerequisite for gating it at all: the version must reach the fingerprint.

    A tool with no extraction branch reports ``"unknown"``, which the fail-closed
    policy reads as "too old" on every host -- so this is what makes the
    dxrt-cli entry in ``MIN_TOOL_VERSIONS`` mean something other than "always
    block". The trailing requirements block must not be carried along: it would
    be pasted verbatim into the "found ..." preflight message.
    """
    _stub_dxrt_banners(monkeypatch, _V350_RUN_MODEL, _REAL_DXRT_CLI_V340)
    info = ef._tool_version("dxrt-cli")
    assert info["available"] is True
    assert info["version"] == "DXRT v3.4.0+fad14d6"
    assert "Minimum Driver Versions" not in info["version"]
    assert _parse_dxrt_version(info["version"]) == (3, 4, 0)


# The run_model decision table, re-run against dxrt-cli's own banner shape
# (build-stamped, no tool name). Same threshold, same fail-closed policy.
_DXRT_CLI_VERSION_TABLE = [
    ("DXRT v3.4.0+fad14d6", True),   # below the minimum -- real v3.4.0 output
    ("DXRT v3.5.0+9ef3f4c", False),  # exactly the minimum -- must NOT be blocked
    ("DXRT v3.10.0",        False),  # 10 > 5 numerically, not lexically
    ("unknown",             True),   # D5: unparseable fails closed
]


@pytest.mark.parametrize("banner,blocked", _DXRT_CLI_VERSION_TABLE)
def test_dxrt_cli_version_gate_decision_table(monkeypatch, banner, blocked):
    _stub_dxrt_banners(monkeypatch, _V350_RUN_MODEL, banner)
    fp = ef.collect_fingerprint()
    flagged = [t for t, _f, _n in fp["outdated_required"]]
    assert ("dxrt-cli" in flagged) is blocked, \
        f"{banner!r}: expected blocked={blocked}, got outdated_required={fp['outdated_required']}"


def test_mixed_install_is_refused_because_dxrt_cli_sets_the_recorded_rt_version():
    """Why dxrt-cli is gated at all -- asserted on the recorded value, not a hint.

    ``npu.rt_version`` -- the field the results carry and the version-trend
    chart plots -- is produced by ``dxrt-cli --version`` (`_get_dxrt_version`),
    NOT by the ``run_model --help`` banner the gate originally read. A host with
    a v3.5.0 ``run_model`` in front of a v3.4.0 ``dxrt-cli`` therefore used to
    pass preflight and then stamp every row of the campaign "v3.4.0" -- exactly
    the protocol inconsistency the all-family gate exists to prevent. Preflight
    must refuse it.

    Not parametrized with ``monkeypatch`` per case on purpose: the assertion is
    about one specific skewed install, so it is spelled out once.
    """
    import pytest as _pytest

    mp = _pytest.MonkeyPatch()
    try:
        _stub_dxrt_banners(mp, _V350_RUN_MODEL, _REAL_DXRT_CLI_V340)
        fp = ef.collect_fingerprint()
    finally:
        mp.undo()

    # What the campaign would record, and what the old gate looked at.
    assert fp["npu"]["rt_version"] == "v3.4.0"
    assert fp["tools"]["run_model"]["version"] == _V350_RUN_MODEL

    flagged = [t for t, _f, _n in fp["outdated_required"]]
    assert "run_model" not in flagged, "the binary the old gate checked is fine here"
    assert "dxrt-cli" in flagged, \
        "a v3.4.0 dxrt-cli sets rt_version=v3.4.0 and must not pass preflight"

    # Isolated from whatever else this host is missing: only the version verdict.
    ok, errors = check_preflight(
        {"missing_required": [], "outdated_required": fp["outdated_required"]})
    assert ok is False
    assert any("dxrt-cli" in e and "3.4.0" in e and "3.5.0" in e for e in errors), errors


@pytest.mark.parametrize("banner,recorded,blocked", [
    ("DXRT v3.4.0+fad14d6", "v3.4.0", True),
    ("DXRT v3.5.0+9ef3f4c", "v3.5.0", False),
])
def test_gate_follows_the_binary_that_sets_rt_version(monkeypatch, banner, recorded, blocked):
    """`run_model` is pinned at v3.5.0 throughout; only `dxrt-cli` moves.

    The recorded ``rt_version`` and the preflight verdict move together with it.
    Re-scoping the gate back to ``run_model`` alone breaks the second assertion
    while the first keeps reporting the older runtime -- which is precisely the
    silent corruption being guarded against.
    """
    _stub_dxrt_banners(monkeypatch, _V350_RUN_MODEL, banner)
    fp = ef.collect_fingerprint()
    assert fp["npu"]["rt_version"] == recorded
    flagged = [t for t, _f, _n in fp["outdated_required"]]
    assert ("dxrt-cli" in flagged) is blocked


def test_dxrt_cli_remediation_names_the_required_version():
    """The hint must be actionable for a *version* failure, not just a missing one.

    `dxrt-cli` used to be gated on presence only, so a bare "install dx-runtime"
    was enough. Now that it can fail for being v3.4.0, the hint has to say which
    version closes it -- as run_model's already does.
    """
    hint = ef._remediation("dxrt-cli")
    assert "3.5.0" in hint


# -- the hint is derived, not transcribed ------------------------------------
# Both halves of the dx_rt install hint used to be literals: "3.5.0" and
# "amd64". A literal cannot be caught by an equality check against its own
# source, so each test below forces the source to a value the old literal never
# had -- bump the gate, move the host -- and requires the hint to follow.


def test_dxrt_hint_version_follows_the_gate_when_it_is_raised(monkeypatch):
    """Bumping MIN_TOOL_VERSIONS must not leave the hint advising the old deb.

    Asserting "3.5.0 appears in both" would pass against a hardcoded string, so
    the gate is moved somewhere no literal could already be: a v9.9.9 minimum
    must produce a v9.9.9 hint, and 3.5.0 must be gone from it entirely.
    """
    monkeypatch.setitem(ef.MIN_TOOL_VERSIONS, "run_model", (9, 9, 9))
    hint = ef._remediation("run_model")
    assert "v9.9.9+" in hint
    assert "libdxrt-bin_9.9.9_" in hint
    assert "3.5.0" not in hint


@pytest.mark.parametrize("machine, deb", [("x86_64", "amd64"), ("aarch64", "arm64")])
def test_dxrt_hint_names_the_running_hosts_deb_arch(monkeypatch, machine, deb):
    """dpkg names architectures differently from uname; the deb uses dpkg's.

    The aarch64 case is the one that bites: 4 of the 6 benchmark hosts are ARM
    boards, and the old literal sent every one of them to an amd64 package.
    Each case also asserts the *other* arch is absent, so a hint that names both
    (or ignores the host) fails rather than passing on a substring.
    """
    monkeypatch.setattr(ef.platform, "machine", lambda: machine)
    hint = ef._remediation("run_model")
    other = "arm64" if deb == "amd64" else "amd64"
    assert f"_{deb}.deb" in hint
    assert f"_{other}.deb" not in hint


def test_dxrt_hint_refuses_to_invent_an_arch_it_does_not_know(monkeypatch):
    """An unmapped machine gets a resolvable placeholder, never a guess.

    A concrete-but-wrong filename reads as authoritative and installs nothing.
    The subshell says what we do not know while staying copy-pasteable.
    """
    monkeypatch.setattr(ef.platform, "machine", lambda: "riscv64")
    hint = ef._remediation("run_model")
    assert "$(dpkg --print-architecture)" in hint
    assert "_amd64.deb" not in hint
    assert "_arm64.deb" not in hint


def test_dxrt_hint_arch_agrees_with_dpkg_on_this_host():
    """Independent oracle: dpkg itself, not our own mapping table.

    The parametrized test above proves the mapping is applied; this proves the
    mapping is *right*, by asking the tool that will consume the filename. On an
    aarch64 runner this fails outright against a hardcoded amd64.
    """
    dpkg = shutil.which("dpkg")
    if dpkg is None:
        pytest.skip("dpkg not installed -- no independent architecture oracle")
    arch = subprocess.run([dpkg, "--print-architecture"],
                          capture_output=True, text=True).stdout.strip()
    assert arch, "dpkg --print-architecture produced no output"
    assert f"_{arch}.deb" in ef._remediation("run_model")
