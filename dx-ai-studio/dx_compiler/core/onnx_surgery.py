"""ONNX graph surgery for compile self-heal — make dynamic input dims static.

Some compile failures need the *model* changed, not just config.json (e.g. a dynamic
batch dim the NPU can't accept). These helpers rewrite input shapes deterministically and
write a new .onnx; the caller points the next compile at the surgically-fixed model.

Never touches weights/topology — only the declared input dims. Returns a structured result.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional


def _set_dim_value(dim, value: int) -> None:
    """Force an ONNX TensorShapeProto.Dimension to a concrete value."""
    if dim.HasField("dim_param"):
        dim.ClearField("dim_param")
    dim.dim_value = value


def fix_input_batch_to_one(in_path: str, out_path: Optional[str] = None) -> dict:
    """Set the batch (dim 0) of every graph input to 1 where it is dynamic or >1.

    Returns {status: changed|unchanged|error, out_path, changed_inputs}.
    """
    import onnx
    out_path = out_path or in_path
    try:
        model = onnx.load(in_path)
    except Exception as e:
        return {"status": "error", "summary": f"load failed: {e}", "out_path": None, "changed_inputs": []}

    initializers = {init.name for init in model.graph.initializer}
    changed = []
    for inp in model.graph.input:
        if inp.name in initializers:
            continue
        tt = inp.type.tensor_type
        if not tt.HasField("shape") or len(tt.shape.dim) == 0:
            continue
        d0 = tt.shape.dim[0]
        is_dynamic = d0.HasField("dim_param") or not d0.HasField("dim_value")
        if is_dynamic or (d0.HasField("dim_value") and d0.dim_value != 1):
            _set_dim_value(d0, 1)
            changed.append(inp.name)

    if not changed:
        return {"status": "unchanged", "summary": "batch already 1 on all inputs",
                "out_path": in_path, "changed_inputs": []}
    try:
        onnx.save(model, out_path)
    except Exception as e:
        return {"status": "error", "summary": f"save failed: {e}", "out_path": None, "changed_inputs": changed}
    return {"status": "changed", "summary": f"batch->1 on {len(changed)} input(s)",
            "out_path": out_path, "changed_inputs": changed}


def set_static_input_shapes(in_path: str, shapes: dict, out_path: Optional[str] = None) -> dict:
    """Set explicit static shapes for named inputs (e.g. {'images': [1,3,640,640]}).

    Only fully-static int shapes are applied; unknown names are ignored. Returns a result."""
    import onnx
    out_path = out_path or in_path
    try:
        model = onnx.load(in_path)
    except Exception as e:
        return {"status": "error", "summary": f"load failed: {e}", "out_path": None, "applied": []}

    by_name = {inp.name: inp for inp in model.graph.input}
    applied = []
    for name, shape in (shapes or {}).items():
        inp = by_name.get(name)
        if inp is None or not all(isinstance(d, int) and d > 0 for d in shape):
            continue
        tt = inp.type.tensor_type
        tt.ClearField("shape")
        for d in shape:
            tt.shape.dim.add().dim_value = d
        applied.append(name)

    if not applied:
        return {"status": "unchanged", "summary": "no matching static shapes applied",
                "out_path": in_path, "applied": []}
    try:
        onnx.save(model, out_path)
    except Exception as e:
        return {"status": "error", "summary": f"save failed: {e}", "out_path": None, "applied": applied}
    return {"status": "changed", "summary": f"set static shapes on {len(applied)} input(s)",
            "out_path": out_path, "applied": applied}
