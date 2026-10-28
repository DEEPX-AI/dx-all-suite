"""Shared thermal rules, kept free of hardware access so they can be tested.

dx-benchmark and ``dxrun --max-throughput --cool-down-temp`` must cool to the same
temperature. dxrun waits until ``temp < value`` on an integer sensor, dx-benchmark until
``temp <= target``; ``dxrun_cool_down_arg`` bridges the two.
"""
from __future__ import annotations

import math
import statistics
import time
from typing import Callable, Optional

# Used when the idle temperature could not be measured at all.
FALLBACK_IDLE_C = 45.0
# Margin above the idle floor for a start that is allowed despite a hot idle.
HOT_START_MARGIN_C = 3.0


def cooldown_target_c(idle_c: float, delta_c: float, cap_c: float) -> float:
    """Temperature every measurement window should start at or below."""
    return min(idle_c + delta_c, cap_c)


def target_for(cfg) -> float:
    """The campaign's single cool-down target (override wins, else idle + delta, capped)."""
    override = getattr(cfg, "thermal_target_override_c", None)
    if override is not None:
        return float(override)
    idle = cfg.thermal_idle_temp_c if cfg.thermal_idle_temp_c is not None else FALLBACK_IDLE_C
    return cooldown_target_c(idle, cfg.thermal_cooldown_target_delta_c,
                             cfg.thermal_cooldown_abs_cap_c)


def dxrun_cool_down_arg(target_c: float) -> int:
    """Value for ``--cool-down-temp`` so dxrun's ``temp < value`` means ``temp <= target``."""
    return int(math.floor(target_c)) + 1


def settle_idle_temp(
    read: Callable[[], Optional[float]],
    sleep: Callable[[float], None] = time.sleep,
    now: Callable[[], float] = time.monotonic,
    poll_sec: float = 15.0,
    window: int = 8,
    tol_c: float = 1.0,
    max_wait_sec: float = 1200.0,
) -> Optional[float]:
    """Wait until the temperature stops moving and return that settled value.

    A device that was just used reads warm and is still cooling; recording that as
    "idle" raised the whole campaign's cool-down target. Settled means the last
    ``window`` readings span at most ``tol_c``. Returns None when the sensor is
    unreadable or the temperature never settles within ``max_wait_sec``.
    """
    samples: list[float] = []
    deadline = now() + max_wait_sec
    while True:
        value = read()
        if value is None:
            return None
        samples.append(float(value))
        recent = samples[-window:]
        if len(recent) == window and max(recent) - min(recent) <= tol_c:
            return float(statistics.median(recent))
        if now() >= deadline:
            return None
        sleep(poll_sec)


def start_gate(idle_c: float, cap_c: float, hot_block_c: float,
               allow_hot_start: bool) -> tuple[bool, Optional[float], str]:
    """Decide whether a campaign may start. Returns (ok, target_override, message)."""
    if idle_c > hot_block_c:
        return (False, None,
                f"NPU idle temperature {idle_c:.1f}°C exceeds the hot-start limit "
                f"{hot_block_c:.1f}°C; cool the device or its surroundings first.")
    if idle_c >= cap_c:
        if not allow_hot_start:
            return (False, None,
                    f"NPU idle temperature {idle_c:.1f}°C is at or above the {cap_c:.0f}°C "
                    f"cool-down cap, so no window could start cool. Improve cooling, or pass "
                    f"--allow-hot-start to measure anyway (recorded in the results).")
        override = idle_c + HOT_START_MARGIN_C
        return (True, override,
                f"[WARN] hot start allowed: NPU idle {idle_c:.1f}°C >= cap {cap_c:.0f}°C; "
                f"cool-down target raised to {override:.1f}°C. Results are flagged.")
    return True, None, ""
