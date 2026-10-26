"""Regression tests for Studio-owned runtime profile discovery and planning."""
import importlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROFILE_MANIFEST = ROOT / "config" / "runtime_profiles.json"


def _api():
    return importlib.import_module("shared.runtime_profile")


def _artifact(uri, version, digest="a" * 64):
    return {
        "version": version,
        "uri": uri,
        "sha256": digest,
    }


def _manifest(target_version="2.4.1"):
    return {
        "schema_version": 1,
        "studio_version": "0.1.0",
        "target_runtime_version": target_version,
        "profiles": {
            "2.3.0": {
                "gstreamer_abi": "1.20",
                "architectures": {
                    "x86_64": {
                        "runtime": _artifact("https://example.invalid/v2.3.0-runtime.deb", "3.3.0"),
                        "driver": _artifact("https://example.invalid/v2.3.0-driver.deb", "2.4.0"),
                    }
                },
            },
            "2.4.1": {
                "gstreamer_abi": "1.20",
                "architectures": {
                    "x86_64": {
                        "runtime": _artifact("https://example.invalid/v2.4.1-runtime.deb", "3.4.0"),
                        "driver": _artifact("https://example.invalid/v2.4.1-driver.deb", "2.5.1"),
                    }
                },
            },
        },
    }


def test_detected_runtime_version_is_not_checkout_version(tmp_path, monkeypatch):
    api = _api()
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    (runtime / "release.ver").write_text("v2.3.0\n", encoding="utf-8")
    suite = tmp_path / "suite"
    suite.mkdir()
    (suite / "release.ver").write_text("v9.9.9\n", encoding="utf-8")
    monkeypatch.setenv("DX_RUNTIME_ROOT", str(runtime))
    monkeypatch.setenv("DX_SUITE_ROOT", str(suite))

    profile = api.discover_runtime_profile(manifest=_manifest())

    assert profile.runtime_version == "2.3.0"
    assert profile.state is api.ProfileState.MIGRATION_REQUIRED
    assert any(check.check_id == "runtime.release_version" for check in profile.observations)


def test_installed_package_pair_maps_to_declared_profile_not_checkout(monkeypatch):
    api = _api()
    monkeypatch.delenv("DX_RUNTIME_ROOT", raising=False)
    monkeypatch.setattr(api, "DX_RUNTIME_ROOT", Path("/checkout/dx-runtime"))
    monkeypatch.setattr(api, "_installed_package_versions", lambda: ("3.3.0", "2.4.0"))
    monkeypatch.setattr(api, "_runtime_executable", lambda: "/usr/local/bin/dxcli")
    # Host checkout release.ver must not leak into discovery.
    monkeypatch.setattr(api, "_installed_runtime_root", lambda: Path("/nonexistent-dx-runtime"))

    profile = api.discover_runtime_profile(manifest=_manifest())

    assert profile.runtime_version == "2.3.0"
    assert profile.driver_version == "2.4.0"
    assert profile.state is api.ProfileState.MIGRATION_REQUIRED
    assert any(check.check_id == "runtime.package_pair" and check.passed for check in profile.observations)


def test_installed_package_pair_ignores_debian_package_revision(monkeypatch):
    api = _api()
    monkeypatch.delenv("DX_RUNTIME_ROOT", raising=False)
    monkeypatch.setattr(api, "_installed_package_versions", lambda: ("3.4.0", "2.5.1-2"))
    monkeypatch.setattr(api, "_runtime_executable", lambda: "/usr/local/bin/dxcli")

    profile = api.discover_runtime_profile(manifest=_manifest())

    assert profile.runtime_version == "2.4.1"
    assert profile.driver_version == "2.5.1"
    assert profile.state is api.ProfileState.TARGET_DISCOVERED


def test_profile_rejects_unsigned_install_or_rollback_artifact(tmp_path, monkeypatch):
    api = _api()
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    (runtime / "release.ver").write_text("v2.3.0\n", encoding="utf-8")
    monkeypatch.setenv("DX_RUNTIME_ROOT", str(runtime))
    manifest = _manifest()
    del manifest["profiles"]["2.4.1"]["architectures"]["x86_64"]["runtime"]["sha256"]

    profile = api.discover_runtime_profile(manifest=manifest)
    plan = api.plan_reconciliation(profile, manifest)

    assert plan.state is api.ReconciliationState.BLOCKED
    assert "artifact digest" in plan.reason.lower()


def test_bundled_manifest_uses_verified_staging_and_rollback_artifacts():
    """target = the runtime the suite pins (dx-runtime v2.5.0: DX-RT 3.5.0 · driver 2.7.0).

    Digests were computed from the downloaded .deb files at the pinned dx_rt / driver revisions.
    2.4.2, 2.4.1 and 2.3.0 stay as verified rollback profiles."""
    api = _api()
    manifest = api.load_runtime_manifest(PROFILE_MANIFEST)
    target = manifest.profile("2.5.0", "x86_64")
    arm = manifest.profile("2.5.0", "aarch64")
    prior = manifest.profile("2.4.2", "x86_64")
    prior_arm = manifest.profile("2.4.2", "aarch64")
    previous = manifest.profile("2.4.1", "x86_64")
    rollback = manifest.profile("2.3.0", "x86_64")

    assert target.runtime.uri == (
        "https://raw.githubusercontent.com/DEEPX-AI/dx_rt/"
        "02861ba4645e338a51c433099114079cbee59213/"
        "release/3.5.0/libdxrt-bin_3.5.0_amd64.deb"
    )
    assert arm.runtime.uri.endswith("/release/3.5.0/libdxrt-bin_3.5.0_arm64.deb")
    assert (target.runtime.version, target.driver.version) == ("3.5.0", "2.7.0")
    assert target.runtime.sha256 == "4abb3ab743f67e538cb8392d419d16242530ac68e1103b20f0b8e9ad8fdf67be"
    assert arm.runtime.sha256 == "2fe46df2e145f2825954932ff4e2cdbc6745433db489e8c0cccdc5f2ce18ae83"
    assert target.driver.sha256 == arm.driver.sha256 == (
        "36ff756cdfee8312d26a1a9b1abb1a9ea58bd764798be17ad9cec89b838cd4b5")
    assert prior.runtime.sha256 == "da782deac10acb1c997b52ea6d0160c06f112a68ad5e25035cfc8e16de0a8bdc"
    assert prior_arm.runtime.sha256 == "161223058938c54efadc581b33499210194da58e55cd5ade332e692ca0d649c2"
    assert prior.driver.sha256 == "6ab417956d2abd70c181c4aa0bae71bc60e0961ccf37eac9fc82d0e6a8314468"
    assert previous.runtime.sha256 == "736cfef009ce9e974ab1ab610d867239d19d72a426a53e367ddcbd53297b6e20"
    assert previous.driver.sha256 == "b686c1d83acc0bd5ada7808fc913516ae0db6cceaff757c5cbf05914e0871d64"
    assert rollback.runtime.sha256 == "6bf79ef9c504a91a4ab84cfb482d72c7d4fad83cad5582d52f483133848c6a59"
    assert rollback.driver.sha256 == "3182d0ae59f69aad7b8ee6efdc13adf737abab8c0d90bd8ac9caddca9dd840e7"

    persisted = json.loads(PROFILE_MANIFEST.read_text(encoding="utf-8"))
    assert persisted["target_runtime_version"] == "2.5.0"
    assert set(persisted["profiles"]) == {"2.3.0", "2.4.1", "2.4.2", "2.5.0"}


def _profile_for(api, monkeypatch, runtime_ver, driver_ver, arch):
    monkeypatch.delenv("DX_RUNTIME_ROOT", raising=False)
    monkeypatch.setattr(api, "_installed_package_versions", lambda: (runtime_ver, driver_ver))
    monkeypatch.setattr(api, "_runtime_executable", lambda: "/usr/local/bin/dxcli")
    monkeypatch.setattr(api, "normalize_architecture", lambda value=None: arch)
    # Host checkout release.ver must not leak into package-based discovery.
    monkeypatch.setattr(api, "_installed_runtime_root", lambda: Path("/nonexistent-dx-runtime"))
    return api.discover_runtime_profile(manifest=api.load_runtime_manifest(PROFILE_MANIFEST))


def test_bundled_manifest_discovers_every_declared_runtime(monkeypatch):
    api = _api()
    pairs = {"2.5.0": ("3.5.0", "2.7.0"), "2.4.2": ("3.4.2", "2.6.0"),
             "2.4.1": ("3.4.0", "2.5.1"), "2.3.0": ("3.3.0", "2.4.0")}
    for arch in ("x86_64", "aarch64"):
        for version, (rt, drv) in pairs.items():
            profile = _profile_for(api, monkeypatch, rt, drv, arch)
            assert profile.runtime_version == version
            expected = (api.ProfileState.TARGET_DISCOVERED if version == "2.5.0"
                        else api.ProfileState.MIGRATION_REQUIRED)
            assert profile.state is expected


def test_bundled_manifest_reconciles_old_profiles_to_2_5_0_and_blocks_unknown(monkeypatch):
    api = _api()
    manifest = api.load_runtime_manifest(PROFILE_MANIFEST)
    for arch in ("x86_64", "aarch64"):
        for rt, drv, state, rollback in (
            ("3.5.0", "2.7.0", api.ReconciliationState.NOOP, "2.5.0"),
            ("3.4.2", "2.6.0", api.ReconciliationState.RECONCILE, "2.4.2"),
            ("3.4.0", "2.5.1", api.ReconciliationState.RECONCILE, "2.4.1"),
            ("3.3.0", "2.4.0", api.ReconciliationState.RECONCILE, "2.3.0"),
        ):
            profile = _profile_for(api, monkeypatch, rt, drv, arch)
            plan = api.plan_reconciliation(profile, manifest)
            assert plan.state is state
            assert plan.target.version == "2.5.0"
            assert plan.rollback.version == rollback

    unsupported = _profile_for(api, monkeypatch, "9.9.9", "9.9.9", "x86_64")
    assert unsupported.state is api.ProfileState.UNSUPPORTED
    plan = api.plan_reconciliation(unsupported, manifest)
    assert plan.state is api.ReconciliationState.BLOCKED
    assert "No verified rollback profile" in plan.reason
