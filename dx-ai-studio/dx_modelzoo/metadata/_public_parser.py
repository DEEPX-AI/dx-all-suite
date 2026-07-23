"""Parser for the PUBLIC DEEPX Model Zoo (developer.deepx.ai/modelzoo).

The public page renders server-side HTML tables (class "model-zoo-table") with a 3-row
grouped header:

  Class Name | Dataset | Input Resolution | Operations(GFLOPs) | Parameters(M) | License | Metric | Source
            | Original(FP32){Accuracy,ONNX} | Q-Lite{Accuracy,DXNN,JSON} | Q-Pro{Accuracy,DXNN,JSON}
            | Performance{FPS,FPS/Watt} | Sample Apps

The internal publish parser only handles flat single-row headers, so this dedicated parser
resolves the grouped header by the (stable) leaf-column order and validates it against the
expected header text before mapping — so a layout change warns instead of mis-mapping.
"""
from __future__ import annotations

import re
from html.parser import HTMLParser

from dx_modelzoo.metadata.normalization import canonical_model_id

# Leaf columns in left-to-right order -> normalized field path. None = ignore (Sample Apps).
_LEAF_FIELDS = [
    "display.class_name",
    "specification.dataset",
    "specification.input_resolution",
    "specification.operations",
    "specification.parameters",
    "legal.license",
    "specification.metric.name",
    "legal.source_url",
    "evaluation.raw.accuracy",
    "artifacts.onnx.remote_url",
    "evaluation.qlite.accuracy",
    "artifacts.qlite_dxnn.remote_url",
    "artifacts.qlite_json.remote_url",
    "evaluation.qpro.accuracy",
    "artifacts.qpro_dxnn.remote_url",
    "artifacts.qpro_json.remote_url",
    "performance.fps",
    "performance.fps_per_watt",
    None,  # Sample Apps
]
# Fields whose cell value is a link (take href, not text).
_LINK_FIELDS = {
    "legal.source_url", "artifacts.onnx.remote_url",
    "artifacts.qlite_dxnn.remote_url", "artifacts.qlite_json.remote_url",
    "artifacts.qpro_dxnn.remote_url", "artifacts.qpro_json.remote_url",
}
_FLOAT_FIELDS = {"performance.fps", "performance.fps_per_watt"}
# The expected 3rd header row (leaf labels under the grouped headers) — used to validate.
_EXPECTED_LEAF_ROW = ["Accuracy", "ONNX", "Accuracy", "DXNN", "JSON",
                      "Accuracy", "DXNN", "JSON", "FPS", "FPS/Watt"]


class _RowParser(HTMLParser):
    """Extract <tbody> rows from a single model-zoo table: each row -> list of (text, href)."""

    def __init__(self):
        super().__init__()
        self.rows: list[list[tuple]] = []
        self._in_tbody = False
        self._in_tr = False
        self._in_td = False
        self._cell_text: list[str] = []
        self._cell_href = None
        self._row: list[tuple] = []

    def handle_starttag(self, tag, attrs):
        if tag == "tbody":
            self._in_tbody = True
        elif tag == "tr" and self._in_tbody:
            self._in_tr = True
            self._row = []
        elif tag in ("td", "th") and self._in_tr:
            self._in_td = True
            self._cell_text = []
            self._cell_href = None
        elif tag == "a" and self._in_td and self._cell_href is None:
            for k, v in attrs:
                if k == "href":
                    self._cell_href = v
                    break

    def handle_endtag(self, tag):
        if tag == "tbody":
            self._in_tbody = False
        elif tag == "tr" and self._in_tr:
            self._in_tr = False
            if self._row:
                self.rows.append(self._row)
        elif tag in ("td", "th") and self._in_td:
            self._in_td = False
            self._row.append(("".join(self._cell_text).strip(), self._cell_href))

    def handle_data(self, data):
        if self._in_td:
            self._cell_text.append(data)


def _model_tables(html: str) -> list[str]:
    return [t for t in re.findall(r"<table\b[^>]*>.*?</table>", html, re.S | re.I)
            if "model-zoo-table" in t[:200] or ("GFLOPs" in t and "FPS/Watt" in t)]


def _set(fields: dict, path: str, value):
    if value not in ("", None):
        fields[path] = value


def parse_public_modelzoo_html(html: str) -> tuple[dict, list]:
    """Return ({model_id: {field: value}}, warnings)."""
    models: dict = {}
    warnings: list = []
    tables = _model_tables(html)
    if not tables:
        return models, ["no model-zoo tables found"]

    for table in tables:
        # validate the leaf header row to catch layout drift
        leaf_labels = re.findall(r"<th[^>]*>(.*?)</th>", table[:table.find("</thead>") + 8] if "</thead>" in table else table[:3000], re.S | re.I)
        leaf_labels = [re.sub(r"<[^>]+>", "", x).strip() for x in leaf_labels]
        if not any(set(_EXPECTED_LEAF_ROW).issubset(set(leaf_labels)) for _ in [0]):
            warnings.append("table header missing expected leaf columns — skipped")
            continue

        rp = _RowParser()
        rp.feed(table)
        for row in rp.rows:
            if len(row) < len(_LEAF_FIELDS) - 1:  # tolerate missing trailing Sample Apps cell
                continue
            name = (row[0][0] or "").strip()
            if not name:
                continue
            fields = {}
            for i, field in enumerate(_LEAF_FIELDS):
                if field is None or i >= len(row):
                    continue
                text, href = row[i]
                val = href if field in _LINK_FIELDS else text
                if field in _FLOAT_FIELDS and val not in ("", None):
                    try:
                        val = float(re.sub(r"[^0-9.]", "", val))
                    except ValueError:
                        pass
                _set(fields, field, val)
            # Key by the shared artifact filename (local catalog ids derive from dxnn/onnx
            # filenames, which differ from the public display name) — matches ~93% vs ~43%
            # by display name. Fall back to the display name when no artifact link exists.
            mid = _artifact_model_id(fields) or canonical_model_id(name)
            if mid:
                fields["display.class_name"] = name
                models[mid] = fields
    return models, warnings


def _artifact_model_id(fields: dict) -> str:
    """Derive a model id from the model's artifact filename (qlite/qpro DXNN or ONNX).

    Pass the full filename to canonical_model_id so it strips the real extension exactly once
    (Path.stem). Pre-stripping with rsplit then calling canonical_model_id double-strips and
    corrupts names with a dot in the number, e.g. "...mobilnet0.5_120x120.dxnn" -> "...mobilnet0".
    """
    for key in ("artifacts.qlite_dxnn.remote_url", "artifacts.qpro_dxnn.remote_url",
                "artifacts.onnx.remote_url"):
        url = fields.get(key)
        if url:
            filename = url.rstrip("/").split("/")[-1]
            return canonical_model_id(filename)
    return ""
