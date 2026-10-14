"""The Lab composer is replaced by the Graph Composer tab (spec 2026-10-14 §2: removed, rebuilt from scratch).

Its modules, routes and plugin templates are gone; the export helper the Run page still needs moved to
dx_app/core/package_common.py; the Lab page links to the new tab.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def test_the_composer_modules_are_gone():
    for mod in ("dx_app.core.lab_workflow", "dx_app.core.lab_package"):
        assert importlib.util.find_spec(mod) is None, mod
    assert not (ROOT / "dx_app/templates/lab_plugins").exists()


def test_lab_capabilities_no_longer_offer_the_composer():
    from dx_app.core.lab_portal import lab_capabilities

    assert "composer" not in lab_capabilities()


@pytest.mark.parametrize("path", ["/api/lab/composer/quick_start", "/api/lab/composer/run",
                                  "/api/lab/composer/run_async", "/api/lab/composer/export",
                                  "/api/lab/composer/recipe/import"])
def test_the_composer_routes_are_gone(path):
    from dx_app.core.developer import lab_session
    from tests.dx_app.test_graph_routes import _route

    r = _route("POST", path, {}, {"X-Lab-Token": lab_session()["token"], "Origin": "http://localhost:8080"})
    assert r["code"] == 404


def test_package_export_keeps_its_common_helper():
    from dx_app.core import developer, package_common

    assert callable(package_common.complete_python_common)
    assert "package_common import complete_python_common" in Path(developer.__file__).read_text(encoding="utf-8")
