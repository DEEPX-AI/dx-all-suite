"""YAML scalar / path / model YAML 파싱 헬퍼.

adapters.py 에서 분리된 순수 파싱 로직.
stdlib 만 사용하여 간단한 YAML 파싱을 수행한다.
"""

import re
from pathlib import Path

from dx_modelzoo.metadata.normalization import canonical_model_id


def yaml_scalar(value):
    """간단한 YAML scalar 값을 stdlib 만으로 정규화."""
    value = value.strip()
    if value in {"", "null", "Null", "NULL", "~"}:
        return None
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def yaml_top_level_value(text, key):
    """YAML 텍스트에서 top-level key 의 값을 추출."""
    m = re.search(rf"^{re.escape(key)}:\s*(.*)$", text, re.MULTILINE)
    if not m:
        return None
    return yaml_scalar(m.group(1))


def yaml_nested_value(text, section, key):
    """YAML 텍스트에서 section 하위의 key 값을 추출."""
    lines = text.splitlines()
    in_section = False
    for line in lines:
        if not line.strip():
            continue
        if not line.startswith((" ", "\t")):
            in_section = line.strip() == f"{section}:"
            continue
        if in_section:
            m = re.match(rf"\s+{re.escape(key)}:\s*(.*)$", line)
            if m:
                return yaml_scalar(m.group(1))
    return None


def yaml_first_shape(text):
    """YAML 텍스트에서 첫 번째 shape 리스트를 추출."""
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        if line.strip() != "shape:":
            continue
        shape = []
        for next_line in lines[idx + 1:]:
            m = re.match(r"\s*-\s*(-?[0-9]+)\s*$", next_line)
            if not m:
                break
            shape.append(int(m.group(1)))
        if shape:
            return shape
    return []


def parse_modelzoo_yaml_file(file_path):
    """현재 dx-modelzoo YAML 모델 정의에서 기본 메타데이터를 추출."""
    file_path = Path(file_path)
    text = file_path.read_text(encoding="utf-8")

    name = yaml_top_level_value(text, "name")
    cid = canonical_model_id(name or file_path.stem)
    if not cid:
        return {}

    fields = {}
    if name:
        fields["display.name"] = name
        fields["display.class_name"] = name

    task = yaml_top_level_value(text, "task")
    if task:
        fields["display.task"] = task

    description = yaml_top_level_value(text, "description")
    if description:
        fields["content.use_case.en"] = description

    reference = yaml_top_level_value(text, "reference")
    if reference:
        fields["legal.source_url"] = reference

    macs = yaml_top_level_value(text, "macs")
    if macs:
        fields["specification.operations"] = macs

    params = yaml_top_level_value(text, "params")
    if params:
        fields["specification.parameters"] = params

    dataset = yaml_nested_value(text, "dataset", "type")
    if dataset:
        fields["specification.dataset"] = dataset

    shape = yaml_first_shape(text)
    if shape:
        fields["technical.input_shape"] = shape
        if len(shape) >= 4:
            fields["specification.input_resolution"] = f"{shape[-2]}x{shape[-1]}"

    return {cid: fields}
