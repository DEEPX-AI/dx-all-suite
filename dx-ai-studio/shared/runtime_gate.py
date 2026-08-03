"""Fail-closed launch policy for Studio inference modules."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from shared.runtime_profile import ContractCheck
from shared.runtime_state import RuntimePhase, RuntimeStateStore


_INFERENCE_MODULES = frozenset({"dx_app", "dx_stream"})


@dataclass(frozen=True)
class ModuleStartPolicy:
    """Whether a Studio module may perform an inference launch."""

    allowed: bool
    reason: Optional[ContractCheck] = None


def module_start_policy(
    module: str,
    state_store: Optional[RuntimeStateStore] = None,
) -> ModuleStartPolicy:
    """Permit setup/diagnostic modules while requiring an activated runtime for inference."""
    if module not in _INFERENCE_MODULES:
        return ModuleStartPolicy(allowed=True)

    state = (state_store or RuntimeStateStore()).load()
    active = state.phase is RuntimePhase.ACTIVE and bool(state.active_version)
    if active:
        return ModuleStartPolicy(allowed=True)

    return ModuleStartPolicy(
        allowed=False,
        reason=ContractCheck(
            check_id="profile.active",
            required="Studio runtime profile activated after complete App and Stream validation",
            observed="phase={} active_version={}".format(
                state.phase.value,
                state.active_version or "missing",
            ),
            passed=False,
            remediation="Complete Runtime Setup or restore a validated runtime profile before launching inference.",
        ),
    )