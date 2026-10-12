"""Contract for optional external dependency markers.

Checks that test files carry the right classification markers. Markers are
classification metadata only; they do not change existing skipif/skip behavior.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = REPO_ROOT / "tests"


def _get_module_markers(filepath: Path) -> set[str]:
    """Extract marker names declared by a pytestmark assignment or module-level decorator, from the AST."""
    return set(_get_module_marker_list(filepath))


def _get_module_marker_list(filepath: Path) -> list[str]:
    """Extract marker names declared by a pytestmark assignment, as a list that keeps duplicates."""
    source = filepath.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(filepath))
    markers: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "pytestmark":
                    markers.extend(sorted(_extract_marker_names(node.value)))
    return markers


def _get_function_markers(filepath: Path, func_name: str) -> set[str]:
    """Extract the pytest.mark.X decorator names applied to a given function, from the AST."""
    return set(_get_function_marker_list(filepath, func_name))


def _get_function_marker_list(filepath: Path, func_name: str) -> list[str]:
    """Extract the pytest marker names applied to a given function, as a list that keeps duplicates."""
    source = filepath.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(filepath))
    aliases = _collect_marker_aliases(tree)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            markers: list[str] = []
            for dec in node.decorator_list:
                names = _extract_marker_names(dec)
                if isinstance(dec, ast.Name) and dec.id in aliases:
                    names.extend(aliases[dec.id])
                markers.extend(sorted(names))
            return markers
    raise AssertionError(f"missing test function {func_name} in {filepath}")


def _get_effective_function_markers(filepath: Path, func_name: str) -> set[str]:
    """Return a function's effective markers: module-level pytestmark plus its decorators."""
    return set(_get_effective_function_marker_list(filepath, func_name))


def _get_effective_function_marker_list(filepath: Path, func_name: str) -> list[str]:
    """Return a function's effective markers as a list: module-level pytestmark plus its decorators."""
    return _get_module_marker_list(filepath) + _get_function_marker_list(filepath, func_name)


def _collect_marker_aliases(tree: ast.Module) -> dict[str, list[str]]:
    """Collect pytest.mark.X aliases from module-level assignments."""
    aliases: dict[str, list[str]] = {}
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name):
                names = _extract_marker_names(node.value)
                if names:
                    aliases[target.id] = names
    return aliases


def _extract_marker_names(node: ast.expr) -> list[str]:
    """Extract pytest.mark.X marker names (handles both lists and a single attribute)."""
    names: list[str] = []
    if isinstance(node, (ast.List, ast.Tuple)):
        for elt in node.elts:
            names.extend(_extract_marker_names(elt))
    elif isinstance(node, ast.Attribute):
        # pytest.mark.X or pytest.mark.skipif(...)
        chain = _dotted_name(node)
        if chain and chain.startswith("pytest.mark."):
            names.append(chain.split("pytest.mark.")[1])
    elif isinstance(node, ast.Call):
        names.extend(_extract_marker_names(node.func))
    return names


def _dotted_name(node: ast.expr) -> str:
    """Turn an Attribute chain into a dotted string."""
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


class TestMarkerExtractionHelpers:
    """The marker contract helpers themselves must detect duplicates and omissions."""

    def test_module_marker_list_preserves_duplicates(self, tmp_path):
        sample = tmp_path / "test_sample.py"
        sample.write_text(
            "\n".join(
                [
                    "import pytest",
                    "pytestmark = [",
                    "    pytest.mark.requires_dx_runtime,",
                    "    pytest.mark.requires_dx_runtime,",
                    "    pytest.mark.skipif(False, reason='available'),",
                    "]",
                ]
            ),
            encoding="utf-8",
        )

        markers = _get_module_marker_list(sample)

        assert markers.count("requires_dx_runtime") == 2

    def test_missing_function_lookup_fails_explicitly(self, tmp_path):
        sample = tmp_path / "test_sample.py"
        sample.write_text("def test_existing():\n    pass\n", encoding="utf-8")

        with pytest.raises(AssertionError, match="missing test function"):
            _get_function_marker_list(sample, "test_missing")


class TestHwWidgetMarkers:
    """Only the Node runtime tests in tests/test_hw_widget.py carry the requires_node marker."""

    NODE_RUNTIME_TESTS = [
        "test_hw_widget_can_switch_between_two_npus",
        "test_hw_widget_hides_selector_for_single_npu",
        "test_hw_widget_falls_back_when_selected_index_disappears",
        "test_hw_widget_stale_index_multi_npu_clamps_to_zero",
        "test_hw_widget_missing_npu_values_render_na",
    ]

    @pytest.mark.parametrize("func_name", NODE_RUNTIME_TESTS)
    def test_node_runtime_function_has_single_requires_node(self, func_name):
        filepath = TESTS_DIR / "test_hw_widget.py"
        markers = _get_effective_function_marker_list(filepath, func_name)
        assert markers.count("requires_node") == 1, (
            f"{func_name} must have exactly one requires_node marker, found: {markers}"
        )

    def test_static_contract_is_not_marked_requires_node(self):
        filepath = TESTS_DIR / "test_hw_widget.py"
        markers = _get_effective_function_marker_list(filepath, "test_hw_widget_static_contracts")
        assert markers.count("requires_node") == 0, (
            f"static hw widget contract must not require node, found: {markers}"
        )


class TestI18nAttributeMarkers:
    """test_shared_i18n_behavior_runtime must carry the requires_node marker."""

    def test_runtime_function_has_requires_node(self):
        filepath = TESTS_DIR / "dx_stream" / "test_i18n_attributes.py"
        markers = _get_effective_function_marker_list(filepath, "test_shared_i18n_behavior_runtime")
        assert markers.count("requires_node") == 1, (
            f"test_shared_i18n_behavior_runtime must have exactly one requires_node marker, found: {markers}"
        )


class TestModelzooVirtualizedPerformanceMarkers:
    """Test functions that depend on Pillow must carry the requires_pillow marker."""

    PILLOW_TESTS = [
        "test_optimizer_dry_run_does_not_write_outputs",
        "test_optimizer_writes_webp_jpg_and_manifest",
        "test_dryrun_reports_skipped_when_outputs_exist",
        "test_stem_collision_produces_distinct_outputs",
        "test_cli_summary_zero_source_bytes",
        "test_rgba_composites_on_white_background",
    ]

    @pytest.mark.parametrize("func_name", PILLOW_TESTS)
    def test_pillow_test_has_requires_pillow(self, func_name):
        filepath = TESTS_DIR / "test_modelzoo_virtualized_performance.py"
        markers = _get_function_markers(filepath, func_name)
        assert "requires_pillow" in markers, (
            f"{func_name} must have requires_pillow marker, found: {markers}"
        )

    @pytest.mark.parametrize("func_name", PILLOW_TESTS)
    def test_pillow_test_preserves_skipif(self, func_name):
        filepath = TESTS_DIR / "test_modelzoo_virtualized_performance.py"
        markers = _get_function_markers(filepath, func_name)
        assert "skipif" in markers, (
            f"{func_name} must still have skipif marker (via _requires_pil), found: {markers}"
        )

    @pytest.mark.parametrize("func_name", PILLOW_TESTS)
    def test_pillow_test_has_single_requires_pillow_marker(self, func_name):
        filepath = TESTS_DIR / "test_modelzoo_virtualized_performance.py"
        markers = _get_function_marker_list(filepath, func_name)
        assert markers.count("requires_pillow") == 1, (
            f"{func_name} must have exactly one requires_pillow marker, found: {markers}"
        )


class TestBenchmarkMarkers:
    """The dx_stream/benchmark test modules must carry the requires_dx_runtime marker."""

    BENCHMARK_FILES = [
        "test_config_expansion.py",
        "test_generate_model_list.py",
        "test_main_args.py",
        "test_model_catalog.py",
        "test_sandbox_export.py",
    ]

    @pytest.mark.parametrize("filename", BENCHMARK_FILES)
    def test_benchmark_module_has_requires_dx_runtime(self, filename):
        filepath = TESTS_DIR / "dx_stream" / "benchmark" / filename
        markers = _get_module_marker_list(filepath)
        assert markers.count("requires_dx_runtime") == 1, (
            f"benchmark/{filename} must have exactly one requires_dx_runtime in pytestmark, found: {markers}"
        )

    @pytest.mark.parametrize("filename", BENCHMARK_FILES)
    def test_benchmark_module_preserves_skipif(self, filename):
        filepath = TESTS_DIR / "dx_stream" / "benchmark" / filename
        markers = _get_module_markers(filepath)
        assert "skipif" in markers, (
            f"benchmark/{filename} must still have skipif in pytestmark, found: {markers}"
        )
