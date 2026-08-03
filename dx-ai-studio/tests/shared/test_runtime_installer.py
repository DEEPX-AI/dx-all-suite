"""Tests for the Studio-owned external runtime artifact installer."""
import hashlib


def _definition():
    from shared.runtime_profile import RuntimeArtifact, RuntimeDefinition

    runtime_bytes = b"runtime-deb"
    driver_bytes = b"driver-deb"
    definition = RuntimeDefinition(
        version="2.4.1",
        architecture="x86_64",
        gstreamer_abi="1.20",
        suite_revision="suite",
        runtime_revision="runtime",
        runtime=RuntimeArtifact(
            version="3.4.0",
            uri="https://example.invalid/libdxrt.deb",
            sha256=hashlib.sha256(runtime_bytes).hexdigest(),
        ),
        driver=RuntimeArtifact(
            version="2.5.1",
            uri="https://example.invalid/dxrt-driver.deb",
            sha256=hashlib.sha256(driver_bytes).hexdigest(),
        ),
    )
    return definition, {definition.runtime.uri: runtime_bytes, definition.driver.uri: driver_bytes}


def test_installer_stages_verified_artifacts_before_authorized_install(tmp_path):
    from shared.runtime_installer import ExternalArtifactInstaller

    definition, payloads = _definition()
    commands = []
    installer = ExternalArtifactInstaller(
        cache_dir=tmp_path / "artifacts",
        fetcher=payloads.__getitem__,
        command_runner=lambda command: commands.append(command) or True,
        validator=lambda _definition: True,
        authorized=True,
    )

    assert installer.verify_artifact(definition)
    assert installer.install(definition)
    assert installer.validate(definition)
    assert commands == [
        ("sudo", "-n", "dpkg", "-i", *map(str, installer.staged_paths(definition)))
    ]
    assert all(path.is_file() for path in installer.staged_paths(definition))


def test_installer_rejects_bad_digest_before_any_privileged_command(tmp_path):
    from shared.runtime_installer import ExternalArtifactInstaller

    definition, payloads = _definition()
    payloads[definition.runtime.uri] = b"tampered"
    commands = []
    installer = ExternalArtifactInstaller(
        cache_dir=tmp_path / "artifacts",
        fetcher=payloads.__getitem__,
        command_runner=lambda command: commands.append(command) or True,
        authorized=True,
    )

    assert installer.verify_artifact(definition) is False
    assert installer.install(definition) is False
    assert commands == []


def test_installer_requires_explicit_authorization_for_dpkg(tmp_path):
    from shared.runtime_installer import ExternalArtifactInstaller

    definition, payloads = _definition()
    commands = []
    installer = ExternalArtifactInstaller(
        cache_dir=tmp_path / "artifacts",
        fetcher=payloads.__getitem__,
        command_runner=lambda command: commands.append(command) or True,
        authorized=False,
    )

    assert installer.verify_artifact(definition)
    assert installer.install(definition) is False
    assert commands == []