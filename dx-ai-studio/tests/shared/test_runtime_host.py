"""Tests for Studio's runtime host reconciliation service."""


class _TargetRunner:
    def __init__(self):
        self.calls = []

    def install(self, definition):
        self.calls.append(("install", definition.version))
        return True

    def validate(self, definition):
        self.calls.append(("validate", definition.version))
        return True


def test_host_service_activates_discovered_target_only_after_validation(tmp_path):
    from shared import runtime_profile as profile_api
    from shared.runtime_host import RuntimeHost
    from shared.runtime_state import RuntimePhase, RuntimeStateStore

    profile = profile_api.RuntimeProfile(
        runtime_version="2.4.1",
        architecture="x86_64",
        driver_version="2.5.1",
        runtime_root=tmp_path / "runtime",
        state=profile_api.ProfileState.TARGET_DISCOVERED,
        observations=(),
    )
    runner = _TargetRunner()
    store = RuntimeStateStore(tmp_path / "state.json")
    host = RuntimeHost(
        manifest=profile_api.load_runtime_manifest(),
        state_store=store,
        profile_discoverer=lambda _manifest: profile,
        runner=runner,
    )

    result = host.reconcile()

    assert result.status.value == "active"
    assert runner.calls == [("validate", "2.4.1")]
    assert store.load().phase is RuntimePhase.ACTIVE