"""Transactional Studio runtime bootstrap, activation, and rollback orchestration."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol, Union

from shared.runtime_profile import (
    ReconciliationPlan,
    ReconciliationState,
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