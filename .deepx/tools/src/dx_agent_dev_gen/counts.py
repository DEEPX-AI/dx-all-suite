# SPDX-License-Identifier: Apache-2.0
"""Live dx_app model/task counts — the ONE definition shared by the generator
(template variables MODEL_COUNT/TASK_COUNT/TASK_LIST) and the conformance guard
(.deepx/tests/conformance/test_kb_counts.py). Never hand-write these numbers."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

REGISTRY_REL = Path("config") / "model_registry.json"
TASK_DIR_REL = Path("src") / "python_example"
NON_TASK_DIRS = frozenset({"common"})


def task_names(app_root: Path) -> list[str] | None:
    """Sorted task directory names under src/python_example, or None if absent."""
    task_dir = app_root / TASK_DIR_REL
    if not task_dir.is_dir():
        return None
    return sorted(
        d.name for d in task_dir.iterdir()
        if d.is_dir() and d.name not in NON_TASK_DIRS and not d.name.startswith((".", "_"))
    )


def model_count(app_root: Path) -> int | None:
    """Number of entries in config/model_registry.json (list or name→info dict), or
    None if the file is missing, unparsable, or not a list/dict."""
    registry = app_root / REGISTRY_REL
    if not registry.is_file():
        return None
    try:
        data = json.loads(registry.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    if not isinstance(data, (list, dict)):
        return None
    return len(data)


def task_model_counts(app_root: Path) -> Counter | None:
    """Per-task model counts (add_model_task → n) from config/model_registry.json,
    or None if the registry is missing/unparsable/not a list."""
    registry = app_root / REGISTRY_REL
    if not registry.is_file():
        return None
    try:
        data = json.loads(registry.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    if not isinstance(data, list):
        return None
    return Counter(m.get("add_model_task") for m in data if isinstance(m, dict))


def find_app_root(repo: Path) -> Path | None:
    """dx_app root reachable from *repo*: itself (dx_app), ./dx_app (dx-runtime) or
    ./dx-runtime/dx_app (suite). None when no registry is reachable."""
    for candidate in (repo, repo / "dx_app", repo / "dx-runtime" / "dx_app"):
        if (candidate / REGISTRY_REL).is_file():
            return candidate
    return None
