# SPDX-License-Identifier: Apache-2.0
"""
Tests for dx_agent_dev_gen.counts — the single source of truth for live
dx_app model/task counts shared by the generator and the conformance guard
(.deepx/tests/conformance/test_kb_counts.py).
"""

from __future__ import annotations

from pathlib import Path

from collections import Counter

from dx_agent_dev_gen.counts import find_app_root, model_count, task_model_counts, task_names


class TestModelCount:
    def test_list_registry(self, tmp_path):
        (tmp_path / "config").mkdir()
        (tmp_path / "config" / "model_registry.json").write_text(
            '[{"a": 1}, {"b": 2}, {"c": 3}]', encoding="utf-8")
        assert model_count(tmp_path) == 3

    def test_dict_registry(self, tmp_path):
        (tmp_path / "config").mkdir()
        (tmp_path / "config" / "model_registry.json").write_text(
            '{"m1": {}, "m2": {}}', encoding="utf-8")
        assert model_count(tmp_path) == 2

    def test_scalar_registry_is_invalid(self, tmp_path):
        (tmp_path / "config").mkdir()
        (tmp_path / "config" / "model_registry.json").write_text("42", encoding="utf-8")
        assert model_count(tmp_path) is None

    def test_malformed_json_is_invalid(self, tmp_path):
        (tmp_path / "config").mkdir()
        (tmp_path / "config" / "model_registry.json").write_text("{ not json", encoding="utf-8")
        assert model_count(tmp_path) is None

    def test_missing_file_is_none(self, tmp_path):
        assert model_count(tmp_path) is None


class TestTaskNames:
    def test_filters_common_and_hidden_dirs(self, tmp_path):
        base = tmp_path / "src" / "python_example"
        for name in ("object_detection", "classification", "common", "__pycache__", ".hidden"):
            (base / name).mkdir(parents=True)
        assert task_names(tmp_path) == ["classification", "object_detection"]

    def test_ignores_files_not_dirs(self, tmp_path):
        base = tmp_path / "src" / "python_example"
        base.mkdir(parents=True)
        (base / "real_task").mkdir()
        (base / "README.md").write_text("x", encoding="utf-8")
        assert task_names(tmp_path) == ["real_task"]

    def test_missing_task_dir_is_none(self, tmp_path):
        assert task_names(tmp_path) is None


class TestTaskModelCounts:
    def test_list_registry_returns_counter(self, tmp_path):
        (tmp_path / "config").mkdir()
        (tmp_path / "config" / "model_registry.json").write_text(
            '[{"add_model_task": "object_detection"}, '
            '{"add_model_task": "object_detection"}, '
            '{"add_model_task": "classification"}]',
            encoding="utf-8")
        assert task_model_counts(tmp_path) == Counter(
            {"object_detection": 2, "classification": 1})

    def test_dict_registry_is_none(self, tmp_path):
        (tmp_path / "config").mkdir()
        (tmp_path / "config" / "model_registry.json").write_text(
            '{"m1": {"add_model_task": "object_detection"}}', encoding="utf-8")
        assert task_model_counts(tmp_path) is None

    def test_malformed_json_is_none(self, tmp_path):
        (tmp_path / "config").mkdir()
        (tmp_path / "config" / "model_registry.json").write_text("{ not json", encoding="utf-8")
        assert task_model_counts(tmp_path) is None

    def test_missing_file_is_none(self, tmp_path):
        assert task_model_counts(tmp_path) is None


class TestFindAppRoot:
    def test_self(self, tmp_path):
        (tmp_path / "config").mkdir()
        (tmp_path / "config" / "model_registry.json").write_text("[]", encoding="utf-8")
        assert find_app_root(tmp_path) == tmp_path

    def test_dx_runtime_layout(self, tmp_path):
        nested = tmp_path / "dx_app"
        (nested / "config").mkdir(parents=True)
        (nested / "config" / "model_registry.json").write_text("[]", encoding="utf-8")
        assert find_app_root(tmp_path) == nested

    def test_suite_layout(self, tmp_path):
        nested = tmp_path / "dx-runtime" / "dx_app"
        (nested / "config").mkdir(parents=True)
        (nested / "config" / "model_registry.json").write_text("[]", encoding="utf-8")
        assert find_app_root(tmp_path) == nested

    def test_none_when_unreachable(self, tmp_path):
        assert find_app_root(tmp_path) is None
