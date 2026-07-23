"""Phase 2 Task 7.1/7.2 — pytest 인프라 계약 테스트.

pytest.ini와 root tests/conftest.py가 요구사항을 충족하는지 검증한다.
Task 7.2: 모듈별 conftest 존재 및 sys.path 해킹 제거 계약.
"""
import ast
import configparser
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PYTEST_INI = REPO_ROOT / "pytest.ini"
ROOT_CONFTEST = REPO_ROOT / "tests" / "conftest.py"

REQUIRED_MARKERS = {
    "requires_node",
    "requires_pillow",
    "requires_dx_runtime",
    "external",
    "smoke",
}

# 광범위한 addopts 중 금지 목록 (collection 제한/조기 중단 옵션)
DISRUPTIVE_ADDOPTS = {"--maxfail", "-x", "--ignore"}


class TestPytestIniContract:
    """pytest.ini 존재 및 내용 계약."""

    def test_pytest_ini_exists(self):
        assert PYTEST_INI.exists(), "pytest.ini must exist at repo root"

    def test_testpaths_is_primary_tests_root(self):
        cfg = configparser.ConfigParser()
        cfg.read(str(PYTEST_INI))
        assert cfg.has_section("pytest"), "pytest.ini must have [pytest] section"
        testpaths = cfg.get("pytest", "testpaths", fallback="")
        paths = set(testpaths.split())
        assert paths == {"tests"}, f"testpaths should be limited to primary tests root: {paths}"

    def test_required_markers_declared(self):
        cfg = configparser.ConfigParser()
        cfg.read(str(PYTEST_INI))
        markers_raw = cfg.get("pytest", "markers", fallback="")
        declared = set()
        for line in markers_raw.splitlines():
            line = line.strip()
            if line:
                name = line.split(":")[0].strip()
                declared.add(name)
        missing = REQUIRED_MARKERS - declared
        assert not missing, f"Missing markers in pytest.ini: {missing}"

    def test_no_disruptive_addopts(self):
        cfg = configparser.ConfigParser()
        cfg.read(str(PYTEST_INI))
        addopts = cfg.get("pytest", "addopts", fallback="")
        for opt in DISRUPTIVE_ADDOPTS:
            assert opt not in addopts, f"Disruptive addopt '{opt}' found in pytest.ini"

    def test_full_suite_collects_without_namespace_errors(self):
        """Bare ``core`` imports must not break collection when all tests load together."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/",
                "--collect-only",
                "-q",
                "--ignore=tests/dx_stream/benchmark",
            ],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr + result.stdout
        assert "error during collection" not in result.stdout.lower(), result.stdout
        assert "ModuleNotFoundError" not in result.stdout, result.stdout


class TestRootConftestContract:
    """root tests/conftest.py 존재 및 내용 계약."""

    def test_root_conftest_exists(self):
        assert ROOT_CONFTEST.exists(), "tests/conftest.py must exist"

    def test_inserts_repo_root_into_sys_path(self):
        """conftest.py 소스가 parents[1]을 sys.path에 삽입하는 로직을 포함."""
        source = ROOT_CONFTEST.read_text()
        assert "parents[1]" in source or "parents[ 1 ]" in source, (
            "conftest.py must compute repo root via parents[1]"
        )
        assert "sys.path" in source, "conftest.py must reference sys.path"

    def test_does_not_contain_module_specific_paths(self):
        """conftest.py는 모듈별 경로를 포함하지 않아야 한다 (Task 7.2 범위)."""
        source = ROOT_CONFTEST.read_text()
        forbidden = ["dx_stream", "dx_modelzoo", "dx_monitor", "dx_sandbox", "dx_compiler"]
        for mod in forbidden:
            assert mod not in source, (
                f"root conftest.py must not mention '{mod}' — that belongs to Task 7.2"
            )

    def test_conditional_insert(self):
        """sys.path 삽입은 중복 방지 조건부여야 한다."""
        source = ROOT_CONFTEST.read_text()
        assert "not in sys.path" in source or "if str(ROOT)" in source, (
            "conftest.py must conditionally insert to avoid duplicates"
        )

    def test_root_tools_package_is_stable_after_module_paths_are_prepended(self):
        """모듈별 top-level package가 root tools.i18n_audit를 가리지 않아야 한다."""
        script = f"""
import runpy
import sys
from pathlib import Path

repo = Path({str(REPO_ROOT)!r})
sys.modules.pop("tools", None)
runpy.run_path(str(repo / "tests" / "conftest.py"))
sys.path.insert(0, str(repo / "dx_modelzoo"))

import tools.i18n_audit

sys.stdout.write(str(Path(tools.i18n_audit.__file__).resolve()))
"""
        result = subprocess.run(
            [sys.executable, "-c", script],
            text=True,
            capture_output=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        assert str(REPO_ROOT / "tools" / "i18n_audit") in result.stdout



TARGET_MODULE_CONFTESTS = [
    "tests/shared/conftest.py",
    "tests/dx_app/conftest.py",
    "tests/dx_benchmark/conftest.py",
    "tests/dx_compiler/conftest.py",
    "tests/dx_planner/conftest.py",
    "tests/launcher/conftest.py",
]

# 테스트 파일에서 제거되어야 할 redundant top-level sys.path.insert 패턴.
# 함수 내부의 동적 sys.path 조작(import-isolation 테스트)은 허용.
_TOPLEVEL_SYSPATH_INSERT = re.compile(
    r"^sys\.path\.insert\(0,\s*str\(", re.MULTILINE
)


class TestModuleConftestsExist:
    """Task 7.2: 대상 모듈별 conftest 파일 존재 검증."""

    @pytest.mark.parametrize("rel_path", TARGET_MODULE_CONFTESTS)
    def test_conftest_exists(self, rel_path):
        path = REPO_ROOT / rel_path
        assert path.exists(), f"{rel_path} must exist"

    @pytest.mark.parametrize("rel_path", TARGET_MODULE_CONFTESTS)
    def test_conftest_adds_only_allowed_paths(self, rel_path):
        """conftest는 sys.path만 조작하고, 애플리케이션 코드를 import하지 않아야 한다."""
        path = REPO_ROOT / rel_path
        if not path.exists():
            pytest.skip("conftest not yet created")
        source = path.read_text()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name in ("sys", "pathlib", "os", "importlib"), (
                        f"{rel_path} imports disallowed module: {alias.name}"
                    )
            elif isinstance(node, ast.ImportFrom):
                assert node.module in ("pathlib", "os", None), (
                    f"{rel_path} imports from disallowed module: {node.module}"
                )


# 대상 모듈 테스트 파일에서 redundant top-level sys.path 해킹이 제거되었는지 검증.
# 동적 isolation 함수 내부의 sys.path는 허용.
_FILES_MUST_NOT_HAVE_TOPLEVEL_SYSPATH = [
    "tests/dx_app/test_modelzoo_gateway.py",
    "tests/dx_app/test_server.py",
    "tests/dx_benchmark/test_server.py",
    "tests/dx_compiler/test_log_capture.py",
    "tests/dx_planner/test_aggregator.py",
    "tests/dx_planner/test_server.py",
    "tests/shared/test_dx_server_base.py",
]


class TestRedundantSysPathRemoved:
    """Task 7.2: conftest 추가 후 redundant top-level sys.path.insert 제거 검증."""

    @pytest.mark.parametrize("rel_path", _FILES_MUST_NOT_HAVE_TOPLEVEL_SYSPATH)
    def test_no_toplevel_syspath_insert(self, rel_path):
        """Top-level에 sys.path.insert(0, str(...)) 패턴이 없어야 한다."""
        path = REPO_ROOT / rel_path
        if not path.exists():
            pytest.skip("file not found")
        source = path.read_text()
        # 함수/클래스 외부(모듈 레벨)의 sys.path.insert만 검사
        tree = ast.parse(source)
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                call = node.value
                if (isinstance(call.func, ast.Attribute)
                        and isinstance(call.func.value, ast.Attribute)
                        and getattr(call.func.value, "attr", "") == "path"
                        and call.func.attr == "insert"):
                    pytest.fail(
                        f"{rel_path} still has top-level sys.path.insert — "
                        "should be handled by module conftest"
                    )
            elif isinstance(node, ast.If):
                # 조건부 sys.path.insert도 top-level이면 제거 대상
                for child in ast.walk(node):
                    if (isinstance(child, ast.Call)
                            and isinstance(child.func, ast.Attribute)
                            and getattr(child.func, "attr", "") == "insert"
                            and isinstance(child.func.value, ast.Attribute)
                            and getattr(child.func.value, "attr", "") == "path"):
                        pytest.fail(
                            f"{rel_path} still has top-level conditional sys.path.insert — "
                            "should be handled by module conftest"
                        )
