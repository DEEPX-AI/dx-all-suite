from pathlib import Path
import shutil
import subprocess

import pytest

from .version_compatibility import (
    RUN_CONTEXT,
    load_expected_versions,
    parse_dxcom_version,
    parse_dxrt_cli_versions,
    parse_version_matrix,
    read_first_line,
    record_result,
)


pytestmark = pytest.mark.version_compatibility

PROJECT_ROOT = Path(__file__).resolve().parents[2]
COMPAT_MATRIX = PROJECT_ROOT / "docs/source/04_Version_Compatibility.md"
SUITE_VERSION_FILE = PROJECT_ROOT / "release.ver"
COMPONENT_RELEASE_FILES = {
    "dx-compiler": PROJECT_ROOT / "dx-compiler/release.ver",
    "dx-runtime": PROJECT_ROOT / "dx-runtime/release.ver",
    "npu-driver": PROJECT_ROOT / "dx-runtime/dx_rt_npu_linux_driver/release.ver",
    "dx-rt": PROJECT_ROOT / "dx-runtime/dx_rt/release.ver",
    "dx-fw": PROJECT_ROOT / "dx-runtime/dx_fw/release.ver",
    "dx-app": PROJECT_ROOT / "dx-runtime/dx_app/release.ver",
    "dx-stream": PROJECT_ROOT / "dx-runtime/dx_stream/release.ver",
}


@pytest.fixture(scope="session")
def expected_versions():
    suite_version = read_first_line(SUITE_VERSION_FILE)
    expected, source = load_expected_versions(suite_version, COMPAT_MATRIX)
    RUN_CONTEXT["suite_version"] = suite_version
    RUN_CONTEXT["matrix_source"] = source
    return expected


def test_parse_version_matrix_extracts_current_suite_row(tmp_path):
    matrix = tmp_path / "04_Version_Compatibility.md"
    matrix.write_text(
        """
        <table><tbody>
          <tr><td rowspan="3">2026-05-14</td><td colspan="7" align="center">v2.3.3</td></tr>
          <tr><td colspan="2" align="center">v2.3.1</td><td colspan="5" align="center"><b>v2.3.3</b></td></tr>
          <tr>
            <td align="center">v2.3.0</td><td align="center">v2.0.1</td>
            <td align="center">v2.5.6</td><td align="center">v2.4.1</td>
            <td align="center">v3.3.2</td><td align="center">v3.0.1</td>
            <td align="center">v3.1.1</td>
          </tr>
        </tbody></table>
        """,
        encoding="utf-8",
    )

    expected = parse_version_matrix(matrix, "v2.3.3")

    assert expected["dx-compiler"] == "v2.3.1"
    assert expected["dx-runtime"] == "v2.3.3"
    assert expected["dxcom"] == "v2.3.0"
    assert expected["dxtron"] == "v2.0.1"
    assert expected["dx-fw"] == "v2.5.6"
    assert expected["npu-driver"] == "v2.4.1"
    assert expected["dx-rt"] == "v3.3.2"
    assert expected["dx-stream"] == "v3.0.1"
    assert expected["dx-app"] == "v3.1.1"


def test_parse_version_matrix_ignores_unexpected_trailing_cells(tmp_path):
    matrix = tmp_path / "04_Version_Compatibility.md"
    matrix.write_text(
        """
        <table><tbody>
          <tr><td rowspan="3">2026-05-14</td><td colspan="7" align="center">v2.3.3</td></tr>
          <tr><td colspan="2" align="center">v2.3.1</td><td colspan="5" align="center">v2.3.3</td></tr>
          <tr>
            <td>v2.3.0</td><td>v2.0.1</td><td>v2.5.6</td><td>v2.4.1</td>
            <td>v3.3.2</td><td>v3.0.1</td><td>v3.1.1</td><td>v9.9.9</td>
          </tr>
        </tbody></table>
        """,
        encoding="utf-8",
    )

    expected = parse_version_matrix(matrix, "v2.3.3")

    assert expected["dx-app"] == "v3.1.1"
    assert "v9.9.9" not in expected.values()


def test_parse_dxcom_version_normalizes_missing_v_prefix():
    assert parse_dxcom_version("DX-COM 2.3.0") == "v2.3.0"


def test_parse_dxrt_cli_versions_extracts_component_versions():
    output = """
    DXRT v3.3.2
    FW version : v2.5.6
    RT Driver version : v2.4.1
    """

    assert parse_dxrt_cli_versions(output) == {
        "dx-rt": "v3.3.2",
        "dx-fw": "v2.5.6",
        "npu-driver": "v2.4.1",
    }


@pytest.mark.parametrize("component", COMPONENT_RELEASE_FILES)
def test_release_ver_matches_compatibility_matrix(component, expected_versions):
    expected = expected_versions.get(component)
    if not expected:
        record_result("release.ver", component, "-", "-", "skip")
        pytest.skip(f"{component} is not defined in compatibility matrix")

    version_file = COMPONENT_RELEASE_FILES[component]
    if not version_file.exists():
        record_result("release.ver", component, "not found", expected, "skip")
        pytest.skip(f"{component} release.ver not found: {version_file}")

    actual = read_first_line(version_file)
    status = "pass" if actual == expected else "fail"
    record_result("release.ver", component, actual, expected, status)
    assert actual == expected


def test_dxcom_version_matches_compatibility_matrix(expected_versions):
    expected = expected_versions.get("dxcom")
    if not expected:
        record_result("cli", "dxcom", "-", "-", "skip")
        pytest.skip("dxcom is not defined in compatibility matrix")
    if shutil.which("dxcom") is None:
        record_result("cli", "dxcom", "not installed", expected, "skip")
        pytest.skip("dxcom command not found")

    result = subprocess.run(["dxcom", "-v"], capture_output=True, text=True, timeout=30)
    output = f"{result.stdout}\n{result.stderr}"
    actual = parse_dxcom_version(output)

    status = "pass" if actual == expected else "fail"
    record_result("cli", "dxcom", actual or "parse error", expected, status)
    assert actual == expected, output


def test_dxrt_cli_versions_match_compatibility_matrix(expected_versions):
    if shutil.which("dxrt-cli") is None:
        for component in ("dx-rt", "dx-fw", "npu-driver"):
            expected = expected_versions.get(component)
            if expected:
                record_result("cli", component, "not installed", expected, "skip")
        pytest.skip("dxrt-cli command not found")

    result = subprocess.run(["dxrt-cli", "-s"], capture_output=True, text=True, timeout=30)
    output = f"{result.stdout}\n{result.stderr}"
    actual_versions = parse_dxrt_cli_versions(output)

    failures = []
    for component in ("dx-rt", "dx-fw", "npu-driver"):
        expected = expected_versions.get(component)
        if not expected:
            continue
        actual = actual_versions.get(component)
        status = "pass" if actual == expected else "fail"
        record_result("cli", component, actual or "parse error", expected, status)
        if status == "fail":
            failures.append(component)

    assert not failures, output
