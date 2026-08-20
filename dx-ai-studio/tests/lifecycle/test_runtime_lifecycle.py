"""Fixture-local Managed Runtime Host lifecycle coverage."""
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.mark.runtime_lifecycle
class TestRuntimeLifecycle:
    class Runner:
        def __init__(self, fail_validation_for=None):
            self.fail_validation_for = fail_validation_for
            self.calls = []

        def install(self, definition):
            self.calls.append(("install", definition.version))
            return True

        def validate(self, definition):
            self.calls.append(("validate", definition.version))
            return definition.version != self.fail_validation_for

    @staticmethod
    def _profile(profile_api, tmp_path, version, state):
        return profile_api.RuntimeProfile(
            runtime_version=version,
            architecture="x86_64",
            driver_version=None,
            runtime_root=tmp_path / "fixture-runtime",
            state=state,
            observations=(),
        )

    def test_clean_host_bootstrap_activates_verified_target(self, tmp_path):
        from shared import runtime_profile as profile_api
        from shared.runtime_bootstrap import BootstrapStatus, reconcile
        from shared.runtime_state import RuntimeStateStore

        result = reconcile(
            self._profile(profile_api, tmp_path, None, profile_api.ProfileState.MISSING),
            profile_api.load_runtime_manifest(),
            self.Runner(),
            RuntimeStateStore(tmp_path / "state.json"),
        )

        assert result.status is BootstrapStatus.ACTIVE
        assert result.plan.target.version == "2.4.1"

    def test_installed_runtime_accepted_as_is_preserves_studio_data(self, tmp_path):
        # Policy: an already-installed runtime that passes the launch contracts is accepted
        # as-is regardless of version — Studio never force-upgrades a working install to the
        # manifest target. Only the installed version is validated; studio data is untouched.
        from shared import runtime_profile as profile_api
        from shared.runtime_bootstrap import BootstrapStatus, reconcile
        from shared.runtime_state import RuntimeStateStore

        studio_data = tmp_path / "studio-data"
        output = studio_data / "outputs" / "result.json"
        cache = studio_data / "cache" / "model.dxnn"
        output.parent.mkdir(parents=True)
        cache.parent.mkdir(parents=True)
        output.write_text("result", encoding="utf-8")
        cache.write_text("cache", encoding="utf-8")
        runner = self.Runner()

        result = reconcile(
            self._profile(profile_api, tmp_path, "2.3.0", profile_api.ProfileState.MIGRATION_REQUIRED),
            profile_api.load_runtime_manifest(),
            runner,
            RuntimeStateStore(tmp_path / "state.json"),
        )

        assert result.status is BootstrapStatus.ACTIVE
        assert runner.calls == [("validate", "2.3.0")]
        assert result.status.value == "active"
        assert output.read_text(encoding="utf-8") == "result"
        assert cache.read_text(encoding="utf-8") == "cache"

    def test_invalid_installed_runtime_fails_without_touching_studio_data(self, tmp_path):
        # A physically-installed runtime that FAILS the launch contracts is a broken install to
        # repair (FAILED) — not a trigger to install a different pinned version, and studio data
        # stays untouched.
        from shared import runtime_profile as profile_api
        from shared.runtime_bootstrap import BootstrapStatus, reconcile
        from shared.runtime_state import RuntimeStateStore

        sentinel = tmp_path / "studio-data" / "outputs" / "keep.txt"
        sentinel.parent.mkdir(parents=True)
        sentinel.write_text("keep", encoding="utf-8")
        runner = self.Runner(fail_validation_for="2.3.0")  # the INSTALLED runtime fails

        result = reconcile(
            self._profile(profile_api, tmp_path, "2.3.0", profile_api.ProfileState.MIGRATION_REQUIRED),
            profile_api.load_runtime_manifest(),
            runner,
            RuntimeStateStore(tmp_path / "state.json"),
        )

        assert result.status is BootstrapStatus.FAILED
        assert runner.calls == [("validate", "2.3.0")]
        assert sentinel.read_text(encoding="utf-8") == "keep"

    def test_child_environment_rejects_contaminated_parent_shell(self, tmp_path):
        from shared.runtime_environment import build_child_environment

        context = SimpleNamespace(
            python_executable=tmp_path / "infer" / "bin" / "python3",
            venv_root=tmp_path / "infer",
            library_dirs=(tmp_path / "runtime" / "lib",),
            plugin_dir=tmp_path / "runtime" / "gst",
            postprocess_lib_dir=tmp_path / "runtime" / "postprocess",
        )
        environment = build_child_environment(context, {
            "PATH": "/broken/venv/bin:/usr/bin",
            "VIRTUAL_ENV": "/broken/venv",
            "PYTHONPATH": "/broken/python",
            "GST_PLUGIN_PATH": "/broken/gst",
            "LD_LIBRARY_PATH": "/broken/lib",
        })

        assert "/broken/venv" not in environment["PATH"]
        assert "PYTHONPATH" not in environment
        assert environment["GST_PLUGIN_PATH"] == str(context.plugin_dir)