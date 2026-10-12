"""The two names of a task key — the dx_app per-model layout key and the legacy key.

The per-model layout names task folders after dx-modelzoo (22 → 28 tasks): 7 tasks are renamed and 7 are new. The
studio's task tables (label · icon · default input · image-only · result notes) are looked up by key, so this module
pairs the names and a value written under one name is also found under the other. The tables themselves stay in
``dx_modelzoo/core/config.py`` (CATEGORIES).

``ppu`` is a group of models, not a task — the per-model layout spreads it over ``object_detection/yolo_ppu`` and
similar, so it has no new key.

Contract: tests/shared/test_tasks.py
"""
from __future__ import annotations

LEGACY_TO_TASK = {
    "classification": "image_classification",
    "obb_detection": "oriented_object_detection",
    "face_alignment": "face_landmark",
    "embedding": "face_recognition",
    "attribute_recognition": "person_attribute",
    "image_enhancement": "low_light_enhancement",
    "reid": "person_reid",
}
TASK_TO_LEGACY = {v: k for k, v in LEGACY_TO_TASK.items()}

NEW_TASKS = (
    "anomaly_detection",
    "zero_shot_image_classification",
    "zero_shot_instance_segmentation",
    "image_matting",
    "image_retrieval",
    "visual_place_recognition",
    "face_attribute",
)


def canonical(key: str) -> str:
    """legacy key → per-model key (a key that is already new, or unknown, is returned unchanged)."""
    return LEGACY_TO_TASK.get(key, key)


def legacy(key: str) -> str:
    """per-model key → legacy key (unchanged when it has no pair)."""
    return TASK_TO_LEGACY.get(key, key)


def lookup(table: dict, key: str, default=None):
    """Look up table by key, falling back to the paired name."""
    if key in table:
        return table[key]
    for alt in (LEGACY_TO_TASK.get(key), TASK_TO_LEGACY.get(key)):
        if alt and alt in table:
            return table[alt]
    return default


class TaskTable(dict):
    """task key → value table. A value written under one name is also found under its pair (``get`` · ``[]`` ·
    ``in``).

    Wrapping an existing table (SAMPLE_IMAGES · EXAMPLE_TYPES · CAT_IMAGE …) lets new keys find old values without
    touching callers. Write each value once so the two names can never disagree."""

    def _alt(self, key):
        for alt in (LEGACY_TO_TASK.get(key), TASK_TO_LEGACY.get(key)):
            if alt is not None and dict.__contains__(self, alt):
                return alt
        return None

    def __missing__(self, key):
        alt = self._alt(key)
        if alt is None:
            raise KeyError(key)
        return dict.__getitem__(self, alt)

    def get(self, key, default=None):
        if dict.__contains__(self, key):
            return dict.__getitem__(self, key)
        alt = self._alt(key)
        return dict.__getitem__(self, alt) if alt is not None else default

    def __contains__(self, key):
        return dict.__contains__(self, key) or self._alt(key) is not None


class TaskSet(frozenset):
    """A set of task keys whose paired names count as members too (IMAGE_ONLY_CATEGORIES etc.)."""

    def __contains__(self, key):
        return (frozenset.__contains__(self, key) or frozenset.__contains__(self, LEGACY_TO_TASK.get(key, key))
                or frozenset.__contains__(self, TASK_TO_LEGACY.get(key, key)))
