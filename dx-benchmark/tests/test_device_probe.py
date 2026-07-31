"""Device-liveness probe classification (conservative circuit breaker, B3).

DEAD is asserted from the REAL failure output captured in
results/RPi5B_M1/.../incidents/001/dxrt_cli_status.txt so the signature match is
grounded in observed device-death output, not a guess.
"""
from benchmark.runner_pipeline import _parse_device_verdict

# Verbatim shape of incidents/001/.../dxrt_cli_status.txt (device unrecoverable)
DEAD_OUTPUT = (
    "DXRT v3.3.2\n"
    '[dxrt-exception] Device input & output exception '
    '{"Fail to initialize device 0":'
    "/path/to/dx_rt/lib/device_pool/device_core.cpp:194:Identify}\n"
)

# Shape of a healthy `dxrt-cli -s` (device enumerated via "* Device" lines)
ALIVE_OUTPUT = (
    "DXRT v3.3.2\n"
    "* Device 0: M1, Accelerator type\n"
    "  * RT Driver version : v2.4.1\n"
    "  * FW version        : v2.5.6\n"
    "NPU 0: voltage 750 mV, clock 1000 MHz\n"
)


def test_verdict_dead_on_fail_to_initialize():
    assert _parse_device_verdict(DEAD_OUTPUT) == "dead"


def test_verdict_alive_on_enumerated_device():
    assert _parse_device_verdict(ALIVE_OUTPUT) == "alive"


def test_verdict_unknown_on_timeout_or_empty():
    assert _parse_device_verdict("<command timed out after 15s>") == "unknown"
    assert _parse_device_verdict("") == "unknown"
    assert _parse_device_verdict("unknown") == "unknown"
