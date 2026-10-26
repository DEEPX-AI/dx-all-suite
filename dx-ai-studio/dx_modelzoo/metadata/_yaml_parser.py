"""Parsing helpers for YAML scalars, paths and model YAML.

Pure parsing logic split out of adapters.py.
Does simple YAML parsing with the stdlib only.
"""

import re
from pathlib import Path

from dx_modelzoo.metadata.normalization import canonical_model_id


def yaml_scalar(value):
    """Normalize a simple YAML scalar value using only the stdlib."""
    value = value.strip()
    if value in {"", "null", "Null", "NULL", "~"}:
        return None
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def yaml_top_level_value(text, key):
    """Extract the value of a top-level key from YAML text."""
    m = re.search(rf"^{re.escape(key)}:\s*(.*)$", text, re.MULTILINE)
    if not m:
        return None
    return yaml_scalar(m.group(1))


def yaml_nested_value(text, section, key):
    """Extract the value of a key under a section from YAML text."""
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
    """Extract the first shape list from YAML text."""
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
    """Extract basic metadata from a current dx-modelzoo YAML model definition."""
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
