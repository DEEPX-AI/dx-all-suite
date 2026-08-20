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

    # Fast path failed (runtime not globally activated). Don't block this module for the OTHER
    # module's broken half: allow it if ITS OWN launch contracts validate live (e.g. dx_stream
    # runs when the GStreamer plugin is present even if the python inference venv isn't ready).
    # This live check runs only on the degraded path; the ACTIVE fast path above is unchanged.
    try:
        from shared.runtime_validation import validate_module_contracts
        module_result = validate_module_contracts(module)
        if module_result.checks and module_result.passed:
            return ModuleStartPolicy(allowed=True)
    except Exception:
        pass

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