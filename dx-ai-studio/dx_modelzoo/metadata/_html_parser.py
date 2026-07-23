"""내부 Publish HTML 테이블 파싱 헬퍼.

adapters.py 에서 분리된 순수 파싱 로직.
AdapterResult 의존성 없이 dict[str, dict] 를 반환한다.
"""

import re
from html.parser import HTMLParser
from urllib.parse import urlparse
from pathlib import Path

from dx_modelzoo.metadata.normalization import canonical_model_id, normalize_source_value


_TABLE_FIELD_MAP = {
    "Task": "display.task",
    "Name": "display.name",
    "Class Name": "display.class_name",
    "Dataset": "specification.dataset",
    "Input Resolution": "specification.input_resolution",
    "Operations": "specification.operations",
    "Parameters": "specification.parameters",
    "License": "legal.license",
    "Metric": "specification.metric.name",
    "Source": "legal.source_url",
    "Raw Accuracy": "evaluation.raw.accuracy",
    "Raw ONNX": "artifacts.onnx.remote_url",
    "NPU Q-Lite Accuracy": "evaluation.qlite.accuracy",
    "NPU Q-Lite DXNN": "artifacts.qlite_dxnn.remote_url",
    "NPU Q-Lite JSON": "artifacts.qlite_json.remote_url",
    "NPU Q-Pro Accuracy": "evaluation.qpro.accuracy",
    "NPU Q-Pro DXNN": "artifacts.qpro_dxnn.remote_url",
    "NPU Q-Pro JSON": "artifacts.qpro_json.remote_url",
    "Q-Pro Accuracy": "evaluation.qpro.accuracy",
    "Q-Pro DXNN": "artifacts.qpro_dxnn.remote_url",
    "Q-Pro JSON": "artifacts.qpro_json.remote_url",
    "FPS": "performance.fps",
    "FPS/Watt": "performance.fps_per_watt",
    "Performance FPS": "performance.fps",
    "Performance FPS/Watt": "performance.fps_per_watt",
    "NPU Performance FPS": "performance.fps",
    "NPU Performance FPS/Watt": "performance.fps_per_watt",
}

_FLOAT_FIELDS = {"performance.fps", "performance.fps_per_watt"}

_ACCURACY_FIELDS = {
    "evaluation.raw.accuracy",
    "evaluation.onnx.accuracy",
    "evaluation.qlite.accuracy",
    "evaluation.qpro.accuracy",
    "evaluation.qmaster.accuracy",
}

_LINK_FIELDS = {
    "legal.source_url",
    "artifacts.onnx.remote_url",
    "artifacts.qlite_dxnn.remote_url",
    "artifacts.qlite_json.remote_url",
    "artifacts.qpro_dxnn.remote_url",
    "artifacts.qpro_json.remote_url",
}

_ARTIFACT_JOIN_SCORES = {
    "artifacts.qlite_dxnn.remote_url": 100,
    "artifacts.onnx.remote_url": 45,
    "artifacts.qlite_json.remote_url": 45,
    "artifacts.qpro_dxnn.remote_url": 45,
    "artifacts.qpro_json.remote_url": 45,
}


def html_span(value):
    """rowspan/colspan 속성값을 int 로 파싱. 최솟값 1."""
    try:
        span = int(value or 1)
    except (TypeError, ValueError):
        return 1
    return max(span, 1)


def clean_cell_text(text):
    """셀 텍스트를 정리하여 연속 공백을 단일 공백으로 변환."""
    return " ".join(str(text or "").split())


def expand_table_headers(header_rows):
    """rowspan/colspan 이 있는 thead 를 leaf column header 목록으로 펼친다."""
    grid = []
    for row_idx, row in enumerate(header_rows):
        while len(grid) <= row_idx:
            grid.append([])
        col_idx = 0
        for cell in row:
            while col_idx < len(grid[row_idx]) and grid[row_idx][col_idx] is not None:
                col_idx += 1
            text = clean_cell_text(cell.get("text", ""))
            rowspan = cell.get("rowspan", 1)
            colspan = cell.get("colspan", 1)
            for r in range(row_idx, row_idx + rowspan):
                while len(grid) <= r:
                    grid.append([])
                while len(grid[r]) < col_idx + colspan:
                    grid[r].append(None)
                for c in range(col_idx, col_idx + colspan):
                    grid[r][c] = text
            col_idx += colspan

    column_count = max((len(row) for row in grid), default=0)
    headers = []
    for col_idx in range(column_count):
        parts = []
        for row in grid:
            text = row[col_idx] if col_idx < len(row) and row[col_idx] else ""
            if text and (not parts or parts[-1] != text):
                parts.append(text)
        headers.append(clean_cell_text(" ".join(parts)))
    return headers


class _TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.headers = []
        self.header_rows = []
        self.rows = []
        self.tables = []
        self._in_thead = False
        self._in_tbody = False
        self._in_table = False
        self._current_table_header_rows = []
        self._current_table_rows = []
        self._current_row = []
        self._current_cell = None
        self._current_cell_tag = None

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "table":
            self._in_table = True
            self._current_table_header_rows = []
            self._current_table_rows = []
        elif tag == "thead":
            self._in_thead = True
        elif tag == "tbody":
            self._in_tbody = True
        elif tag == "tr":
            self._current_row = []
        elif tag in {"th", "td"}:
            self._current_cell_tag = tag
            self._current_cell = {
                "text": "",
                "href": None,
                "rowspan": html_span(attrs_dict.get("rowspan")),
                "colspan": html_span(attrs_dict.get("colspan")),
            }
        elif tag == "a" and self._current_cell is not None:
            href = attrs_dict.get("href")
            if href and not self._current_cell.get("href"):
                self._current_cell["href"] = href

    def handle_endtag(self, tag):
        if tag == "thead":
            self._in_thead = False
        elif tag == "tbody":
            self._in_tbody = False
        elif tag == self._current_cell_tag and self._current_cell is not None:
            self._current_cell["text"] = clean_cell_text(self._current_cell.get("text", ""))
            if tag == "th":
                self.headers.append(self._current_cell["text"])
            self._current_row.append(self._current_cell)
            self._current_cell = None
            self._current_cell_tag = None
        elif tag == "tr" and self._current_row:
            if self._in_thead:
                self.header_rows.append(self._current_row)
                self._current_table_header_rows.append(self._current_row)
            elif self._in_tbody:
                self.rows.append(self._current_row)
                self._current_table_rows.append(self._current_row)
        elif tag == "table":
            if self._current_table_header_rows or self._current_table_rows:
                self.tables.append({
                    "header_rows": self._current_table_header_rows,
                    "rows": self._current_table_rows,
                })
            self._in_table = False
            self._current_table_header_rows = []
            self._current_table_rows = []

    def handle_data(self, data):
        if self._current_cell is not None:
            self._current_cell["text"] += data


def _table_cell_value(cell, field):
    text = clean_cell_text(cell.get("text", ""))
    href = clean_cell_text(cell.get("href", ""))
    if field in _LINK_FIELDS and href:
        return href
    return text or href


def _table_model_id(value):
    text = str(value or "").strip()
    if not text:
        return ""
    text = re.sub(r"\.(dxnn|onnx|json|yaml|yml)$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"-\d+$", "", text)
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def _artifact_model_id(value):
    path = urlparse(str(value or "")).path
    return _table_model_id(Path(path).name)


def _table_model_id_aliases(cid):
    aliases = []

    def add(value):
        if value and value not in aliases:
            aliases.append(value)

    add(cid)
    if "_tinynas_l" in cid:
        add(cid.replace("_tinynas_l", "_tinynasl"))
    if cid.endswith("_hailo"):
        add(f"{cid[:-len('_hailo')]}_h")
    return aliases


def _add_join_candidate(candidates, cid, score):
    for offset, alias in enumerate(_table_model_id_aliases(cid)):
        candidates[alias] = max(candidates.get(alias, -1), score - offset)


def _table_join_candidates(name_val, class_name_val, entry):
    candidates = {}
    _add_join_candidate(candidates, _table_model_id(name_val), 50)
    _add_join_candidate(candidates, _table_model_id(class_name_val), 70)
    for field, value in entry.items():
        if field in _ARTIFACT_JOIN_SCORES:
            _add_join_candidate(candidates, _artifact_model_id(value), _ARTIFACT_JOIN_SCORES[field])
    return candidates


def _table_float(value):
    try:
        return float(str(value).replace(",", ""))
    except ValueError:
        return value


def _is_suspicious_accuracy(field, value):
    return field in _ACCURACY_FIELDS and str(value).strip() in {"0", "0.0", "0.00"}


def _parse_internal_table_rows(rows, headers):
    models = {}
    model_scores = {}
    for row in rows:
        entry = {}
        name_val = None
        class_name_val = None
        for idx, cell in enumerate(row):
            if idx >= len(headers):
                break
            header = headers[idx]
            field = _TABLE_FIELD_MAP.get(header)
            if not field:
                continue
            value = normalize_source_value(_table_cell_value(cell, field))
            if value is None:
                continue
            if header == "Name":
                name_val = value
            elif header == "Class Name":
                class_name_val = value
            if _is_suspicious_accuracy(field, value):
                base = field.rsplit(".", 1)[0]
                entry[f"{base}.source_status"] = "suspect"
                entry[f"{base}.suspect_value"] = str(value)
            elif field in _FLOAT_FIELDS:
                entry[field] = _table_float(value)
            else:
                entry[field] = value

        for cid, score in _table_join_candidates(name_val, class_name_val, entry).items():
            if score >= model_scores.get(cid, -1):
                models[cid] = dict(entry)
                model_scores[cid] = score
    return models


def parse_internal_table_models(html):
    """HTML 을 파싱하여 {canonical_id: fields} dict 를 반환.

    AdapterResult 에 의존하지 않는 순수 파싱 함수.
    """
    parser = _TableParser()
    parser.feed(html)
    models = {}
    if parser.tables:
        for table in parser.tables:
            headers = expand_table_headers(table["header_rows"])
            models.update(_parse_internal_table_rows(table["rows"], headers))
    else:
        headers = expand_table_headers(parser.header_rows)
        models.update(_parse_internal_table_rows(parser.rows, headers))
    return models
