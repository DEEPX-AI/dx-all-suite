"""Tests for Studio-only runtime bootstrap and rollback transactions."""
import importlib


def _profile_api():
    return importlib.import_module("shared.runtime_profile")


def _bootstrap_api():
    return importlib.import_module("shared.runtime_bootstrap")


def _state_api():
    return importlib.import_module("shared.runtime_state")


class RecordingRunner:
    def __init__(self, fail_validation_for=None):
        self.fail_validation_for = fail_validation_for
        self.commands = []

    def install(self, definition):
        self.commands.append("install:{}".format(definition.version))
        return True

    def validate(self, definition):
        self.commands.append("validate:{}".format(definition.version))
        return definition.version != self.fail_validation_for


def test_installed_nontarget_runtime_is_accepted_as_is_when_it_validates(tmp_path):
    # Policy: DX runtimes ship per-version as coherent rt/fw/driver bundles that have been
    # distributed for a long time, so Studio must run on any installed version that passes the
    # launch contracts — it does NOT force-upgrade a working install to the manifest target.
    # An older-than-target runtime (2.3.0) that validates is activated as-is; the target 2.4.1
    # is never installed here.
    profile_api = _profile_api()
    bootstrap = _bootstrap_api()
    state_api = _state_api()
    manifest = profile_api.load_runtime_manifest(
        profile_api.DEFAULT_MANIFEST_PATH
    )
    profile = profile_api.RuntimeProfile(
        runtime_version="2.3.0",
        architecture="x86_64",
        driver_version="2.4.0",
        runtime_root=tmp_path / "runtime",
        state=profile_api.ProfileState.MIGRATION_REQUIRED,
        observations=(),
    )
    runner = RecordingRunner(fail_validation_for="2.4.1")
    state = state_api.RuntimeStateStore(tmp_path / "state.json")

    result = bootstrap.reconcile(profile, manifest, runner, state)

    assert result.status is bootstrap.BootstrapStatus.ACTIVE
    # only the INSTALLED version is validated; no install/upgrade/rollback of the target
    assert runner.commands == ["validate:2.3.0"]
    assert state.load().active_version == "2.3.0"
    assert state.load().phase is state_api.RuntimePhase.ACTIVE


def test_runtime_state_store_replaces_the_journal_atomically(tmp_path):
    state_api = _state_api()
    journal = tmp_path / "runtime" / "state.json"
    store = state_api.RuntimeStateStore(journal)

    store.save(state_api.RuntimeState(active_version="2.4.1"))

    assert store.load().active_version == "2.4.1"
    assert not list(journal.parent.glob("*.tmp"))


def test_target_version_noop_does_not_activate_when_validation_fails(tmp_path):
    profile_api = _profile_api()
    bootstrap = _bootstrap_api()
    state_api = _state_api()
    manifest = profile_api.load_runtime_manifest(profile_api.DEFAULT_MANIFEST_PATH)
    profile = profile_api.RuntimeProfile(
        runtime_version="2.4.1",
        architecture="x86_64",
        driver_version="2.5.1",
        runtime_root=tmp_path / "runtime",
        state=profile_api.ProfileState.TARGET_DISCOVERED,
        observations=(),
    )
    runner = RecordingRunner(fail_validation_for="2.4.1")
    state = state_api.RuntimeStateStore(tmp_path / "state.json")

    result = bootstrap.reconcile(profile, manifest, runner, state)

    assert result.status is bootstrap.BootstrapStatus.FAILED
    assert runner.commands == ["validate:2.4.1"]
    assert state.load().phase is state_api.RuntimePhase.FAILED
    assert state.load().active_version is None