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
    api = _api()
    manifest = api.load_runtime_manifest(PROFILE_MANIFEST)
    target = manifest.profile("2.4.1", "x86_64")
    rollback = manifest.profile("2.3.0", "x86_64")

    assert target.runtime.uri == (
        "https://raw.githubusercontent.com/DEEPX-AI/dx_rt/"
        "b10bda2fabc4e26645e919861b79bedbcd88071a/"
        "release/3.4.0/libdxrt-bin_3.4.0_amd64.deb"
    )
    assert target.runtime.sha256 == "736cfef009ce9e974ab1ab610d867239d19d72a426a53e367ddcbd53297b6e20"
    assert target.driver.sha256 == "b686c1d83acc0bd5ada7808fc913516ae0db6cceaff757c5cbf05914e0871d64"
    assert rollback.runtime.sha256 == "6bf79ef9c504a91a4ab84cfb482d72c7d4fad83cad5582d52f483133848c6a59"
    assert rollback.driver.sha256 == "3182d0ae59f69aad7b8ee6efdc13adf737abab8c0d90bd8ac9caddca9dd840e7"

    persisted = json.loads(PROFILE_MANIFEST.read_text(encoding="utf-8"))
    assert persisted["target_runtime_version"] == "2.4.1"