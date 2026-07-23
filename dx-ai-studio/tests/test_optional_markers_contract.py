"""Phase 2 Task 7.4 — optional external dependency marker 계약 테스트.

테스트 파일에 적절한 분류 마커가 적용되었는지 검증한다.
마커는 분류 메타데이터일 뿐, 기존 skipif/skip 동작은 변경하지 않는다.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = REPO_ROOT / "tests"


def _get_module_markers(filepath: Path) -> set[str]:
    """AST에서 pytestmark 할당 또는 모듈 레벨 데코레이터로 선언된 마커 이름을 추출."""
    return set(_get_module_marker_list(filepath))


def _get_module_marker_list(filepath: Path) -> list[str]:
    """AST에서 pytestmark 할당으로 선언된 마커 이름을 중복 포함 목록으로 추출."""
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
    """AST에서 특정 함수에 적용된 pytest.mark.X 데코레이터 이름을 추출."""
    return set(_get_function_marker_list(filepath, func_name))


def _get_function_marker_list(filepath: Path, func_name: str) -> list[str]:
    """AST에서 특정 함수에 적용된 pytest 마커 이름을 중복 포함 목록으로 추출."""
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
    """모듈 레벨 pytestmark와 함수 데코레이터를 합친 실제 함수 마커를 반환."""
    return set(_get_effective_function_marker_list(filepath, func_name))


def _get_effective_function_marker_list(filepath: Path, func_name: str) -> list[str]:
    """모듈 레벨 pytestmark와 함수 데코레이터를 합친 실제 함수 마커 목록을 반환."""
    return _get_module_marker_list(filepath) + _get_function_marker_list(filepath, func_name)


def _collect_marker_aliases(tree: ast.Module) -> dict[str, list[str]]:
    """모듈 레벨 할당에서 pytest.mark.X 별칭을 수집."""
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
    """pytest.mark.X 형태의 마커 이름을 추출 (리스트, 단일 속성 모두 처리)."""
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
    """Attribute 체인을 점 구분 문자열로 변환."""
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


class TestMarkerExtractionHelpers:
    """마커 contract helper 자체가 중복과 누락을 감지해야 한다."""

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
    """tests/test_hw_widget.py의 Node runtime 테스트만 requires_node 마커를 가져야 한다."""

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
    """test_shared_i18n_behavior_runtime에 requires_node 마커가 있어야 한다."""

    def test_runtime_function_has_requires_node(self):
        filepath = TESTS_DIR / "dx_stream" / "test_i18n_attributes.py"
        markers = _get_effective_function_marker_list(filepath, "test_shared_i18n_behavior_runtime")
        assert markers.count("requires_node") == 1, (
            f"test_shared_i18n_behavior_runtime must have exactly one requires_node marker, found: {markers}"
        )


class TestModelzooVirtualizedPerformanceMarkers:
    """Pillow 의존 테스트 함수에 requires_pillow 마커가 있어야 한다."""

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
    """dx_stream/benchmark 테스트 모듈에 requires_dx_runtime 마커가 있어야 한다."""

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
