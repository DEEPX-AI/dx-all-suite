"""Tests that read the installed DEEPX SDK (dx-runtime/dx_app, its graph engine, the suite's submodules).

Studio is often checked out without them: a clone whose submodules are not initialised, or a board with an older
dx_app. A test that needs one says which with `require()`, and is skipped with that reason instead of failing on
someone else's missing tree.

DX_TESTS_REQUIRE_SDK=1 turns those skips into failures — on a board that has the release SDK installed, every one of
these tests must actually run.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

STRICT_ENV = "DX_TESTS_REQUIRE_SDK"


def require(ok: bool, reason: str) -> None:
    """Skip (fail under DX_TESTS_REQUIRE_SDK=1) unless `ok`; `reason` names what is missing."""
    if ok:
        return
    if strict():
        pytest.fail(f"{STRICT_ENV}=1 but this checkout lacks it: {reason}", pytrace=False)
    pytest.skip(f"not installed here: {reason}")


def strict() -> bool:
    return os.environ.get(STRICT_ENV) == "1"


def dx_app_root() -> Path:
    from shared.paths import DX_APP_ROOT
    return Path(DX_APP_ROOT)


def require_dx_app(*rel: str) -> Path:
    """The installed dx_app root, with each of `rel` (paths under it) present."""
    root = dx_app_root()
    require(root.is_dir(), f"dx_app is not installed ({root})")
    for r in rel:
        require((root / r).exists(), f"dx_app has no {r} ({root})")
    return root


def require_graph_examples() -> Path:
    """dx_app's sample graphs (src/cpp_example/multi_model_graph/*.json, the per-model dx_app)."""
    d = require_dx_app() / "src" / "cpp_example" / "multi_model_graph"
    require(d.is_dir() and any(d.glob("*.json")), f"dx_app ships no sample graphs in {d} (a dx_app before them)")
    return d
