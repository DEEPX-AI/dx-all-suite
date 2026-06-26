from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
import re


VERSION_RE = re.compile(r"v?\d+\.\d+\.\d+")
COMPONENT_KEYS = (
    "dxcom",
    "dxtron",
    "dx-fw",
    "npu-driver",
    "dx-rt",
    "dx-stream",
    "dx-app",
)


class CompatibilityTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[dict[str, str | int]]] = []
        self._current_row: list[dict[str, str | int]] | None = None
        self._current_cell: dict[str, str | int] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "tr":
            self._current_row = []
            return
        if tag != "td" or self._current_row is None:
            return

        attr_map = {name: value for name, value in attrs}
        self._current_cell = {
            "text": "",
            "colspan": int(attr_map.get("colspan") or 1),
            "rowspan": int(attr_map.get("rowspan") or 1),
        }

    def handle_data(self, data: str) -> None:
        if self._current_cell is not None:
            self._current_cell["text"] = f"{self._current_cell['text']}{data}"

    def handle_endtag(self, tag: str) -> None:
        if tag == "td" and self._current_row is not None and self._current_cell is not None:
            self._current_cell["text"] = str(self._current_cell["text"]).strip()
            self._current_row.append(self._current_cell)
            self._current_cell = None
            return
        if tag == "tr" and self._current_row is not None:
            self.rows.append(self._current_row)
            self._current_row = None


def read_first_line(path: Path) -> str:
    with path.open(encoding="utf-8") as file:
        return file.readline().strip()


def normalize_version(version: str) -> str:
    normalized = version.strip()
    if not normalized:
        return ""
    if normalized.startswith("v"):
        return normalized
    return f"v{normalized}"


def parse_version_matrix(matrix_path: Path, suite_version: str) -> dict[str, str]:
    return parse_version_matrix_text(
        matrix_path.read_text(encoding="utf-8"), suite_version, source=str(matrix_path)
    )


def parse_version_matrix_text(
    content: str, suite_version: str, source: str = "<text>"
) -> dict[str, str]:
    parser = CompatibilityTableParser()
    parser.feed(content)

    for index, row in enumerate(parser.rows):
        if any(cell["text"] == suite_version and cell["colspan"] == 7 for cell in row):
            return _parse_suite_rows(parser.rows, index, suite_version)

    raise ValueError(f"Version {suite_version} not found in {source}")


def load_expected_versions(
    suite_version: str, local_path: Path
) -> tuple[dict[str, str], str]:
    """Load expected versions from the local compatibility matrix.

    Returns a tuple of (expected_versions, source_label).
    """
    return parse_version_matrix(local_path, suite_version), f"local ({local_path})"


def _parse_suite_rows(
    rows: list[list[dict[str, str | int]]],
    suite_row_index: int,
    suite_version: str,
) -> dict[str, str]:
    if len(rows) <= suite_row_index + 2:
        raise ValueError(f"Incomplete compatibility matrix rows for {suite_version}")

    parent_row = rows[suite_row_index + 1]
    component_row = rows[suite_row_index + 2]
    if len(parent_row) < 2 or len(component_row) < len(COMPONENT_KEYS):
        raise ValueError(f"Invalid compatibility matrix row shape for {suite_version}")

    expected = {
        "dx-compiler": _cell_version(parent_row[0], suite_version),
        "dx-runtime": _cell_version(parent_row[1], suite_version),
    }
    expected.update(
        {
            component: _cell_version(cell, suite_version)
            for component, cell in zip(COMPONENT_KEYS, component_row)
        }
    )
    return expected


def _cell_version(cell: dict[str, str | int], suite_version: str) -> str:
    match = VERSION_RE.search(str(cell["text"]))
    if match is None:
        raise ValueError(f"Missing version in compatibility matrix row for {suite_version}")
    return normalize_version(match.group(0))


def parse_dxcom_version(output: str) -> str | None:
    match = VERSION_RE.search(output)
    if match is None:
        return None
    return normalize_version(match.group(0))


def parse_dxrt_cli_versions(output: str) -> dict[str, str]:
    patterns = {
        "dx-rt": re.compile(r"DXRT\s+(v?\d+\.\d+\.\d+)"),
        "dx-fw": re.compile(r"FW version\s*:\s*(v?\d+\.\d+\.\d+)"),
        "npu-driver": re.compile(r"RT Driver version\s*:\s*(v?\d+\.\d+\.\d+)"),
    }

    versions: dict[str, str] = {}
    for component, pattern in patterns.items():
        match = pattern.search(output)
        if match is not None:
            versions[component] = normalize_version(match.group(1))
    return versions


@dataclass
class CheckResult:
    phase: str
    label: str
    actual: str
    expected: str
    status: str  # "pass" | "fail" | "skip"


CHECK_RESULTS: list[CheckResult] = []
RUN_CONTEXT: dict[str, str] = {"suite_version": "", "matrix_source": ""}


def record_result(phase: str, label: str, actual: str, expected: str, status: str) -> None:
    CHECK_RESULTS.append(CheckResult(phase, label, actual, expected, status))
