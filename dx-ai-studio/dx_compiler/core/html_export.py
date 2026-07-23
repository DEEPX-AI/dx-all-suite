"""Standalone HTML summary generator.

Lazy-imports ``dx_com.html_export`` when the server process has dx_com.
When compile runs in a venv subprocess (typical launcher setup), summary
generation falls back to the same venv Python.
"""

from __future__ import annotations

import inspect
import json
import os
import subprocess


def _filter_kwargs(fn, kwargs):
    """Drop kwargs the installed dx_com function does not accept.

    dx_com's html_export API drifts between versions (e.g. dx_com 2.4's
    generate_summary_html dropped ``enhanced_scheme`` in favour of
    ``use_q_pro``/``calibration_method``). Filtering by the live signature keeps
    the studio compatible across compiler versions instead of raising TypeError.
    """
    sig = inspect.signature(fn)
    if any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()):
        return kwargs
    return {k: v for k, v in kwargs.items() if k in sig.parameters}

__all__ = [
    "generate_summary_html",
    "export_summary_html",
    "get_static_dir",
    "load_shared_js_assets",
]


def _venv_python():
    from dx_compiler.core.setup_service import setup_service

    return setup_service.get_venv_python()


def _call_via_venv(function_name: str, **kwargs):
    venv_python = _venv_python()
    if not venv_python:
        raise RuntimeError(
            "dx_com is not available and no compiler venv was found for HTML export"
        )
    runner = (
        "import json, os, inspect, dx_com;"
        f"from dx_com.html_export import {function_name} as _fn;"
        "args = json.loads(os.environ['DX_COMPILER_HTML_EXPORT_ARGS']);"
        "_sig = inspect.signature(_fn);"
        "_varkw = any(p.kind == p.VAR_KEYWORD for p in _sig.parameters.values());"
        "args = args if _varkw else {k: v for k, v in args.items() if k in _sig.parameters};"
        "result = _fn(**args);"
        "import sys;"
        "sys.stdout.write(result if isinstance(result, str) else json.dumps(result))"
    )
    env = dict(os.environ)
    env["DX_COMPILER_HTML_EXPORT_ARGS"] = json.dumps(kwargs)
    proc = subprocess.run(
        [str(venv_python), "-c", runner],
        env=env,
        capture_output=True,
        text=True,
        timeout=180,
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        raise RuntimeError(
            f"HTML export via venv failed (exit {proc.returncode}): {detail}"
        )
    if function_name == "load_shared_js_assets":
        return json.loads(proc.stdout)
    return proc.stdout


def generate_summary_html(**kwargs):
    """Generate a standalone HTML summary of compilation results."""
    try:
        from dx_com.html_export import generate_summary_html as _fn
        return _fn(**_filter_kwargs(_fn, kwargs))
    except ModuleNotFoundError:
        return _call_via_venv("generate_summary_html", **kwargs)


def export_summary_html(**kwargs):
    """Export a standalone HTML summary to a file."""
    try:
        from dx_com.html_export import export_summary_html as _fn
        return _fn(**_filter_kwargs(_fn, kwargs))
    except ModuleNotFoundError:
        return _call_via_venv("export_summary_html", **kwargs)


def get_static_dir():
    """Return the path to shared static assets."""
    from dx_com.html_export import get_static_dir as _fn
    return _fn()


def load_shared_js_assets():
    """Load shared JS assets as strings."""
    try:
        from dx_com.html_export import load_shared_js_assets as _fn
        return _fn()
    except ModuleNotFoundError:
        return _call_via_venv("load_shared_js_assets")
