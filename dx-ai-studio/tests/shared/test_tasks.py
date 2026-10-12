"""The two names of a task key (dx_app per-model layout)."""
from __future__ import annotations

from shared import tasks


def test_legacy_and_new_names_pair_up():
    assert tasks.canonical("classification") == "image_classification"
    assert tasks.legacy("oriented_object_detection") == "obb_detection"
    assert tasks.canonical("object_detection") == "object_detection"
    assert set(tasks.LEGACY_TO_TASK.values()).isdisjoint(tasks.NEW_TASKS)


def test_a_table_answers_to_both_names():
    t = tasks.TaskTable({"classification": "dog.jpg", "anomaly_detection": "parking.jpg"})
    assert t["image_classification"] == "dog.jpg" and t.get("image_classification") == "dog.jpg"
    assert "image_classification" in t and "classification" in t
    assert t.get("nope", "x") == "x" and "nope" not in t
    s = tasks.TaskSet({"embedding", "person_reid"})
    assert "face_recognition" in s and "reid" in s and "object_detection" not in s


def test_every_task_key_has_a_row_in_the_model_zoo_table():
    from dx_modelzoo.core.config import CATEGORIES
    for key in list(tasks.LEGACY_TO_TASK) + list(tasks.LEGACY_TO_TASK.values()) + list(tasks.NEW_TASKS):
        assert key in CATEGORIES, key
