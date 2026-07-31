"""Model catalog – load .dxnn models from the manifest and classify by task/size.

The manifest (model_list.json) is the single source of truth for both download
(setup_data.sh) and classification. Filenames are opaque here — task/size come from
the manifest, so a future naming-rule change only touches the JSON, not this code.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .config import TASK_MAP, SIZES, MODEL_DIR, MODEL_LIST_JSON


@dataclass
class ModelEntry:
    """One YOLO26 model file."""
    name: str          # e.g. "yolo26-s_640x640.dxnn"
    path: Path         # absolute path
    task: str          # full task name, e.g. "object_detection"
    task_suffix: str   # manifest key, e.g. "od", "pose", "seg", "obb", "cls"
    size: str          # "n", "s", "m", "l", "x"

    def __str__(self) -> str:
        return f"{self.name} (task={self.task}, size={self.size})"


_SIZE_ORDER = {s: i for i, s in enumerate(SIZES)}
_TASK_ORDER = {k: i for i, k in enumerate(TASK_MAP.keys())}


def _load_manifest(manifest: Path = MODEL_LIST_JSON) -> list[dict]:
    with open(manifest) as f:
        return json.load(f)["models"]


def discover_models(
    model_dir: Path = MODEL_DIR,
    manifest: Path = MODEL_LIST_JSON,
) -> list[ModelEntry]:
    """Return classified entries for manifest models present in *model_dir*."""
    entries = []
    for m in _load_manifest(manifest):
        suffix = m["task"]
        task = TASK_MAP.get(suffix)
        if task is None:
            continue
        path = (model_dir / m["file"]).resolve()
        if not path.exists():
            continue  # parity with the old glob: only present files
        entries.append(ModelEntry(
            name=m["file"],
            path=path,
            task=task,
            task_suffix=suffix,
            size=m["size"],
        ))
    entries.sort(key=lambda e: (_TASK_ORDER.get(e.task_suffix, 99), _SIZE_ORDER.get(e.size, 99)))
    return entries


def filter_models(
    entries: list[ModelEntry],
    task: str | None = None,
    sizes: list[str] | None = None,
) -> list[ModelEntry]:
    """Filter model entries by task name and/or sizes."""
    result = entries
    if task:
        result = [e for e in result if e.task == task]
    if sizes:
        result = [e for e in result if e.size in sizes]
    return result
