"""Studio orchestration entry point for managed runtime profile reconciliation."""
from __future__ import annotations

from pathlib import Path
from typing import Callable, Mapping, Optional, Union

from shared.runtime_bootstrap import BootstrapResult, RuntimeInstaller, reconcile
from shared.runtime_installer import ExternalArtifactInstaller
from shared.runtime_profile import (
    DEFAULT_MANIFEST_PATH,
    RuntimeManifest,
    RuntimeProfile,
    discover_runtime_profile,
    load_runtime_manifest,
)
from shared.runtime_state import RuntimeStateStore
from shared.runtime_validation import RuntimeCandidateValidator


ProfileDiscoverer = Callable[[RuntimeManifest], RuntimeProfile]


class RuntimeHost:
    """Coordinate discovery, verified installation, validation, and atomic activation."""

    def __init__(
        self,
        *,
        manifest: Optional[Union[RuntimeManifest, Mapping[str, object]]] = None,
        manifest_path: Path = DEFAULT_MANIFEST_PATH,
        state_store: Optional[RuntimeStateStore] = None,
        profile_discoverer: ProfileDiscoverer = discover_runtime_profile,
        runner: Optional[RuntimeInstaller] = None,
        authorized: bool = False,
    ) -> None:
        self.manifest = manifest or load_runtime_manifest(manifest_path)
        self.state_store = state_store or RuntimeStateStore()
        self.profile_discoverer = profile_discoverer
        self.candidate_validator = RuntimeCandidateValidator()
        self.runner = runner or ExternalArtifactInstaller(
            authorized=authorized,
            validator=self.candidate_validator.validate,
        )

    def discover(self) -> RuntimeProfile:
        """Observe installed package state without looking at checkout versions."""
        return self.profile_discoverer(self.manifest)

    def reconcile(self) -> BootstrapResult:
        """Run the fail-closed bootstrap transaction for the currently installed host."""
        return reconcile(
            self.discover(),
            self.manifest,
            self.runner,
            self.state_store,
        )
