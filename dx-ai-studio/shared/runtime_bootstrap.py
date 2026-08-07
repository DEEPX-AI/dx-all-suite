"""Transactional Studio runtime bootstrap, activation, and rollback orchestration."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol, Union

from shared.runtime_profile import (
    ReconciliationPlan,
    ReconciliationState,
    RuntimeArtifact,
    RuntimeDefinition,
    RuntimeManifest,
    RuntimeProfile,
    plan_reconciliation,
)
from shared.runtime_state import RuntimePhase, RuntimeState, RuntimeStateStore


class RuntimeInstaller(Protocol):
    """External runtime installer contract; implementations never edit source trees."""

    def install(self, definition: RuntimeDefinition) -> bool:
        """Install the definition's externally supplied artifacts."""

    def validate(self, definition: RuntimeDefinition) -> bool:
        """Run the definition's complete post-install runtime contract."""


class BootstrapStatus(Enum):
    ACTIVE = "active"
    ROLLED_BACK = "rolled_back"
    BLOCKED = "blocked"
    FAILED = "failed"


@dataclass(frozen=True)
class BootstrapResult:
    status: BootstrapStatus
    plan: ReconciliationPlan
    reason: str


def _bounded_reason(value: object) -> str:
    return str(value).strip()[:400] or "Runtime installer reported no detail."


def _installed_probe_definition(profile: RuntimeProfile, plan: ReconciliationPlan) -> RuntimeDefinition:
    """A RuntimeDefinition to hand runner.validate() when accepting an installed runtime.

    validate() checks the REAL installed files and ignores this object, so a manifest entry is
    not required. Prefer plan.rollback — plan_reconciliation sets it to the INSTALLED version's
    definition (not plan.target, which is the upgrade target). Fall back to a synthesized
    definition for the installed version so the accept path also works for versions the manifest
    doesn't curate."""
    if plan.rollback is not None:
        return plan.rollback
    empty = RuntimeArtifact(version="", uri="", sha256="")
    return RuntimeDefinition(
        version=profile.runtime_version or "installed",
        architecture=profile.architecture,
        gstreamer_abi="",
        suite_revision="installed",
        runtime_revision="installed",
        runtime=empty,
        driver=empty,
    )


def _verify_artifact_if_supported(runner: RuntimeInstaller, definition: RuntimeDefinition) -> bool:
    """Require a runner-provided byte digest check when it stages external artifacts."""
    verifier = getattr(runner, "verify_artifact", None)
    if verifier is None:
        # The manifest digest was already checked by plan_reconciliation().  Test and
        # in-memory runners may not stage bytes; production download runners must.
        return True
    return bool(verifier(definition))


def _install_and_validate(
    runner: RuntimeInstaller,
    definition: RuntimeDefinition,
) -> tuple[bool, str]:
    try:
        if not _verify_artifact_if_supported(runner, definition):
            return False, "Artifact verification failed for runtime {}.".format(definition.version)
        if not runner.install(definition):
            return False, "Installer failed for runtime {}.".format(definition.version)
        if not runner.validate(definition):
            return False, "Validation failed for runtime {}.".format(definition.version)
    except Exception as exc:
        return False, _bounded_reason(exc)
    return True, ""


def _save(
    store: RuntimeStateStore,
    active_version: str | None,
    candidate_version: str | None,
    phase: RuntimePhase,
    reason: str,
) -> None:
    store.save(
        RuntimeState(
            active_version=active_version,
            candidate_version=candidate_version,
            phase=phase,
            reason=reason,
        )
    )


def reconcile(
    profile: RuntimeProfile,
    manifest: Union[RuntimeManifest, dict],
    runner: RuntimeInstaller,
    state_store: RuntimeStateStore,
) -> BootstrapResult:
    """Reconcile only through an install-validate-activate/rollback transaction."""
    plan = plan_reconciliation(profile, manifest)
    persisted = state_store.load()
    previous_active = persisted.active_version or profile.runtime_version

    # Accept any coherent ALREADY-INSTALLED runtime that passes the Studio App/Stream launch
    # contracts, regardless of its exact version. DX runtimes ship per-version as coherent
    # rt/fw/driver bundles and have been distributed for a long time, so Studio must run on all
    # of them rather than force one manifest-pinned target. runner.validate() checks the REAL
    # installed files (it ignores the definition it is handed — see RuntimeCandidateValidator),
    # so it is the source of truth for "a usable runtime is installed", and it also self-heals
    # the studio inference venv. A physically-installed runtime is never silently replaced: if
    # it validates it is activated as-is; if it does not, that is a broken install to repair
    # (FAILED), not a trigger to install a different pinned version. Only when NO runtime is
    # installed do we fall through to install the manifest target below.
    if profile.runtime_version is not None:
        probe = _installed_probe_definition(profile, plan)
        try:
            accepted = bool(runner.validate(probe))
            validation_error = ""
        except Exception as exc:
            accepted = False
            validation_error = _bounded_reason(exc)
        if accepted:
            reason = "Accepted installed runtime {}.".format(profile.runtime_version)
            _save(state_store, profile.runtime_version, None, RuntimePhase.ACTIVE, reason)
            return BootstrapResult(BootstrapStatus.ACTIVE, plan, reason)
        reason = "Installed runtime {} failed the Studio launch contracts.{}".format(
            profile.runtime_version, (" " + validation_error) if validation_error else ""
        )
        _save(state_store, None, profile.runtime_version, RuntimePhase.FAILED, reason)
        return BootstrapResult(BootstrapStatus.FAILED, plan, reason)

    if plan.state is ReconciliationState.BLOCKED:
        _save(state_store, previous_active, None, RuntimePhase.BLOCKED, plan.reason)
        return BootstrapResult(BootstrapStatus.BLOCKED, plan, plan.reason)

    if plan.state is ReconciliationState.NOOP:
        active = plan.target.version if plan.target else previous_active
        try:
            validated = bool(plan.target and runner.validate(plan.target))
        except Exception as exc:
            validated = False
            validation_reason = _bounded_reason(exc)
        else:
            validation_reason = "Validation failed for runtime {}.".format(active)
        if not validated:
            reason = "Existing target runtime is not validated: {}".format(validation_reason)
            _save(state_store, None, active, RuntimePhase.FAILED, reason)
            return BootstrapResult(BootstrapStatus.FAILED, plan, reason)
        reason = "Runtime profile is already active."
        _save(state_store, active, None, RuntimePhase.ACTIVE, reason)
        return BootstrapResult(BootstrapStatus.ACTIVE, plan, reason)

    assert plan.target is not None
    _save(
        state_store,
        previous_active,
        plan.target.version,
        RuntimePhase.CANDIDATE_INSTALLING,
        "Installing runtime candidate {}.".format(plan.target.version),
    )
    try:
        artifact_verified = _verify_artifact_if_supported(runner, plan.target)
        installed = artifact_verified and bool(runner.install(plan.target))
    except Exception as exc:
        artifact_verified = False
        installed = False
        candidate_reason = _bounded_reason(exc)
    else:
        candidate_reason = (
            "Artifact verification failed for runtime {}.".format(plan.target.version)
            if not artifact_verified
            else "Installer failed for runtime {}.".format(plan.target.version)
        )

    if installed:
        _save(
            state_store,
            previous_active,
            plan.target.version,
            RuntimePhase.CANDIDATE_VALIDATING,
            "Validating runtime candidate {}.".format(plan.target.version),
        )
        try:
            candidate_valid = bool(runner.validate(plan.target))
        except Exception as exc:
            candidate_valid = False
            candidate_reason = _bounded_reason(exc)
        else:
            if not candidate_valid:
                candidate_reason = "Validation failed for runtime {}.".format(plan.target.version)
        if candidate_valid:
            reason = "Runtime candidate {} activated after validation.".format(plan.target.version)
            _save(state_store, plan.target.version, None, RuntimePhase.ACTIVE, reason)
            return BootstrapResult(BootstrapStatus.ACTIVE, plan, reason)

    if plan.rollback is None:
        reason = "Candidate failed and no verified rollback profile exists: {}".format(candidate_reason)
        _save(state_store, previous_active, plan.target.version, RuntimePhase.FAILED, reason)
        return BootstrapResult(BootstrapStatus.FAILED, plan, reason)

    _save(
        state_store,
        previous_active,
        plan.rollback.version,
        RuntimePhase.ROLLING_BACK,
        "Restoring prior runtime {}.".format(plan.rollback.version),
    )
    rollback_ok, rollback_reason = _install_and_validate(runner, plan.rollback)
    if rollback_ok:
        reason = "Candidate {} failed; restored {}.".format(
            plan.target.version, plan.rollback.version
        )
        _save(state_store, plan.rollback.version, None, RuntimePhase.ACTIVE, reason)
        return BootstrapResult(BootstrapStatus.ROLLED_BACK, plan, reason)

    reason = "Candidate failure ({}) and rollback failure ({}).".format(
        candidate_reason, rollback_reason
    )
    _save(state_store, previous_active, plan.rollback.version, RuntimePhase.FAILED, reason)
    return BootstrapResult(BootstrapStatus.FAILED, plan, reason)