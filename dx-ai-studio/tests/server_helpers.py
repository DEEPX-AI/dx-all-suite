"""Shared browser-audit server helpers.

Provides ``start_module_server`` for any test that needs to spin up a
module's HTTP server on an ephemeral port.
"""
from __future__ import annotations

import importlib
import os
import sys
import threading
from typing import Any


_MODULE_FACTORIES: dict[str, str] = {
    "dx_app": "dx_app.server",
    "dx_agent_dev": "dx_agent_dev.server",
    "dx_benchmark": "dx_benchmark.server",
    "dx_compiler": "dx_compiler.server",
    "dx_modelzoo": "dx_modelzoo.server",
    "dx_monitor": "dx_monitor.server",
    "dx_planner": "dx_planner.server",
    "dx_stream": "dx_stream.server",
    "launcher": "launcher.server",
}

KNOWN_MODULES = sorted(_MODULE_FACTORIES.keys())
_MONITOR_SKIP_HARDWARE_ENV = "DX_MONITOR_SKIP_HARDWARE_INIT"


def _clear_top_level_core_imports() -> None:
    """Avoid cross-module collisions from apps that import their local package as ``core``."""
    for name in list(sys.modules):
        if name == "core" or name.startswith("core."):
            del sys.modules[name]


def start_module_server(module: str) -> tuple[Any, int]:
    """Start a module's HTTP server on port 0 and return (server, port)."""
    if module not in _MODULE_FACTORIES:
        raise ValueError(
            f"Unknown module '{module}'. Known modules: {KNOWN_MODULES}"
        )
    factory_module = _MODULE_FACTORIES[module]
    _clear_top_level_core_imports()
    if factory_module in sys.modules:
        del sys.modules[factory_module]
    previous_skip = os.environ.get(_MONITOR_SKIP_HARDWARE_ENV)
    if module == "dx_monitor":
        os.environ[_MONITOR_SKIP_HARDWARE_ENV] = "1"
    try:
        mod = importlib.import_module(factory_module)
        srv = mod.create_server(port=0)
    finally:
        if module == "dx_monitor":
            if previous_skip is None:
                os.environ.pop(_MONITOR_SKIP_HARDWARE_ENV, None)
            else:
                os.environ[_MONITOR_SKIP_HARDWARE_ENV] = previous_skip
    port = srv.server_address[1]
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    return srv, port
