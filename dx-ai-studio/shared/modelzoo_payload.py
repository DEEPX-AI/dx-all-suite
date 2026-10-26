"""Reader for the public DEEPX Model Zoo (developer.deepx.ai/modelzoo).

The page embeds a structured payload in the document:

    window.__MODEL_ZOO_DATA__ = {
      fields: [task, name, display, dataset, input, ops, params, license,
               metric, source, rawAcc, onnx, qlAcc, qlDxnn, qlJson,
               qpAcc, qpDxnn, qpJson, qmAcc, qmDxnn, qmJson, fps, fpsw],
      base:   "https://sdk.deepx.ai/modelzoo/",
      rows:   [[...], ...]
    }

There is no official JSON endpoint (the page makes no XHR/fetch calls, /modelzoo/*.json is 404,
/api/modelzoo redirects to the page, the bucket listing is 403), so this is still scraping — but of inline JSON,
which is far sturdier than a table: `fields` names the columns, so nothing depends on position. Positional parsing
can shift every field by one column (`fps` ← `fps_per_watt`) and publish wrong performance numbers.

Since this is not an official contract, it **never fails silently**: if the global or a required column is
missing, it raises instead of building a partial catalog.
"""
from __future__ import annotations

import json
from typing import Any

_GLOBAL = "window.__MODEL_ZOO_DATA__"

# Columns the reader cannot do without. (Sparse ones such as qm* are optional.)
_REQUIRED_FIELDS = (
    "task", "name", "display", "dataset", "input", "ops", "params",
    "license", "metric", "source", "rawAcc", "onnx",
    "qlAcc", "qlDxnn", "qlJson", "fps", "fpsw",
)

# payload column name → our artifact name
_ARTIFACTS = {
    "onnx": "onnx",
    "qlDxnn": "qlite_dxnn", "qlJson": "qlite_json",
    "qpDxnn": "qpro_dxnn",  "qpJson": "qpro_json",
    "qmDxnn": "qmaster_dxnn", "qmJson": "qmaster_json",
}
_ACCURACY = {"rawAcc": "raw", "qlAcc": "qlite", "qpAcc": "qpro", "qmAcc": "qmaster"}


def _extract_payload(html: str) -> dict[str, Any]:
    """Pull the object out of the global assignment.

    The end is found by **brace balance**. A regex up to the first `}` would cut a
    nested object short and then fail somewhere unrelated while parsing half the JSON.
    """
    at = html.find(_GLOBAL)
    if at < 0:
        raise ValueError(
            f"{_GLOBAL} 을 찾을 수 없다 — 페이지 구조가 또 바뀌었거나 응답이 "
            "우리가 기대한 문서가 아니다. 부분 카탈로그를 만들지 않는다."
        )
    start = html.find("{", at)
    if start < 0:
        raise ValueError(f"{_GLOBAL} 뒤에 객체가 없다")
    depth = 0
    for end in range(start, len(html)):
        ch = html[end]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return json.loads(html[start:end + 1])
    raise ValueError(f"{_GLOBAL} 의 객체가 닫히지 않았다")


def _as_number(value):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_public_payload(html: str) -> list[dict[str, Any]]:
    """Page HTML → list of model rows."""
    payload = _extract_payload(html)
    fields = payload.get("fields")
    rows = payload.get("rows")
    if not isinstance(fields, list) or not isinstance(rows, list):
        raise ValueError(f"{_GLOBAL} 에 fields/rows 가 없다")

    missing = [f for f in _REQUIRED_FIELDS if f not in fields]
    if missing:
        raise ValueError(
            f"fields 에서 필수 열이 사라졌다: {missing} — 이름으로 읽으므로 "
            "열이 바뀌면 값이 밀리는 대신 여기서 멈춘다."
        )
    at = {name: i for i, name in enumerate(fields)}
    base = (payload.get("base") or "").rstrip("/") + "/"

    def cell(row, name):
        i = at.get(name)
        return row[i] if i is not None and i < len(row) else None

    out: list[dict[str, Any]] = []
    for row in rows:
        artifacts = {}
        for field, key in _ARTIFACTS.items():
            raw = cell(row, field)
            if raw:
                # Relative paths in the payload look like `~onnx/...`.
                artifacts[key] = base + str(raw).lstrip("~/")
        out.append({
            "task": cell(row, "task"),
            "name": cell(row, "name"),
            "display": cell(row, "display"),
            "dataset": cell(row, "dataset"),
            "input": cell(row, "input"),
            "ops": _as_number(cell(row, "ops")),
            "params": _as_number(cell(row, "params")),
            "license": cell(row, "license"),
            "metric": cell(row, "metric"),
            "source": cell(row, "source"),
            "fps": _as_number(cell(row, "fps")),
            "fps_per_watt": _as_number(cell(row, "fpsw")),
            "accuracy": {tier: _as_number(cell(row, field))
                         for field, tier in _ACCURACY.items()},
            "artifacts": artifacts,
        })
    return out


# ── Adapter interface ────────────────────────────────────
# The adapter and studio_id_map expect {model_id: {leaf path: value}}. The leaf
# paths are ones the schema already defines (specification.dataset /
# parameters / metric.name / evaluation.qmaster ...); this reader only fills them.

_LEAF_OF = {
    "display":      "display.class_name",
    "dataset":      "specification.dataset",
    "input":        "specification.input_resolution",
    "ops":          "specification.operations",
    "params":       "specification.parameters",
    "license":      "legal.license",
    "metric":       "specification.metric.name",
    "source":       "legal.source_url",
    "fps":          "performance.fps",
    "fps_per_watt": "performance.fps_per_watt",
}
_ACCURACY_LEAF = {
    "raw": "evaluation.raw.accuracy", "qlite": "evaluation.qlite.accuracy",
    "qpro": "evaluation.qpro.accuracy", "qmaster": "evaluation.qmaster.accuracy",
}


def _artifact_model_id(artifacts: dict) -> str:
    """Build the model id from an artifact file name.

    Pass the **whole file name** to canonical_model_id. Stripping the extension first
    strips it twice and breaks names with a dot inside a number
    (`...mobilnet0.5_120x120.dxnn` → `...mobilnet0`).
    """
    from dx_modelzoo.metadata.normalization import canonical_model_id

    for key in ("qlite_dxnn", "qpro_dxnn", "onnx"):
        url = artifacts.get(key)
        if url:
            return canonical_model_id(url.rstrip("/").split("/")[-1])
    return ""


def parse_public_modelzoo_html(html: str) -> tuple[dict, list[str]]:
    """Public page HTML → (model dict, warnings)."""
    warnings: list[str] = []
    models: dict[str, dict] = {}

    for row in parse_public_payload(html):
        fields: dict = {}
        for src, leaf in _LEAF_OF.items():
            value = row.get(src)
            if value not in (None, ""):
                fields[leaf] = value
        for tier, leaf in _ACCURACY_LEAF.items():
            value = row["accuracy"].get(tier)
            # Leave out missing values. merge picks "the source that has a value",
            # so a None here could blank out a value another source filled in.
            if value is not None:
                fields[leaf] = value
        for key, url in row["artifacts"].items():
            fields[f"artifacts.{key}.remote_url"] = url

        mid = _artifact_model_id(row["artifacts"])
        if not mid:
            from dx_modelzoo.metadata.normalization import canonical_model_id
            mid = canonical_model_id(row.get("name") or row.get("display") or "")
        if not mid:
            warnings.append(f"모델 id 를 만들 수 없는 행: {row.get('display')!r}")
            continue
        if mid in models:
            models[mid].update(fields)
        else:
            models[mid] = fields
    return models, warnings
