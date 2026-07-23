"""ONNX model parser — converts ONNX graphs to JSON-serializable dicts.

Exports
-------
categorize_op(op_type)   – classify an ONNX operator into one of 8 categories.
parse_onnx_model(source) – parse an ONNX model (file path or ModelProto) into a
                           graph dict with nodes, edges, inputs, outputs, params.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Sequence, Union

import numpy as np
import onnx
from onnx import AttributeProto, TensorProto, numpy_helper, shape_inference

__all__ = ["categorize_op", "parse_onnx_model"]


_CATEGORY_MAP: Dict[str, str] = {}

_CATEGORIES: Dict[str, Sequence[str]] = {
    "compute": [
        "Conv", "ConvTranspose", "MatMul", "Gemm", "InterPadConv",
        "ConvInteger", "MatMulInteger", "QLinearConv", "QLinearMatMul",
        # DX fused compute ops
        "DX_Conv", "DX_MatMul", "DX_BilinearResize",
    ],
    "memory": [
        "Reshape", "Transpose", "Flatten", "Concat", "Split", "Slice",
        "Gather", "GatherElements", "GatherND", "Scatter", "ScatterElements",
        "ScatterND", "Pad", "Squeeze", "Unsqueeze", "Expand", "Tile",
        "Shape", "ConstantOfShape", "Constant", "Identity", "Cast",
        "Resize", "Upsample", "DepthToSpace", "SpaceToDepth",
        # DX memory ops
        "DX_Flatten", "Formatter", "Im2col",
    ],
    "activation": [
        "Relu", "Sigmoid", "Tanh", "Softmax", "LogSoftmax", "LeakyRelu",
        "PRelu", "Selu", "Elu", "Celu", "HardSigmoid", "HardSwish",
        "Mish", "MISH", "Swish", "SiLU", "SiLU2", "Gelu",
        "Softplus", "Exp", "ThresholdedRelu", "Shrink",
        # DX activation ops
        "DX_Relu", "DX_Relu6", "DX_PAF", "DX_PRelu", "DX_LeakyRelu",
        "DxSoftmax",
    ],
    "normalization": [
        "BatchNormalization", "LayerNormalization", "InstanceNormalization",
        "GroupNormalization", "LpNormalization", "MeanVarianceNormalization",
        "LRN",
        # DX normalization ops
        "DxLayerNorm",
    ],
    "pooling": [
        "MaxPool", "AveragePool", "GlobalAveragePool", "GlobalMaxPool",
        "GlobalLpPool", "LpPool", "MaxRoiPool", "MaxUnpool",
        # DX pooling ops
        "DX_AveragePool", "DX_GAP",
    ],
    "elementwise": [
        "Add", "Sub", "Mul", "Div", "Pow", "Mod", "Clip", "Abs", "Neg",
        "Sqrt", "Log", "Floor", "Ceil", "Round", "Sign",
        "Reciprocal", "Min", "Max", "Sum", "Mean", "Where", "Equal",
        "Greater", "Less", "GreaterOrEqual", "LessOrEqual", "And", "Or",
        "Not", "Xor",
        # Reduce ops
        "ReduceL2", "ReduceMax", "ReduceMean", "ReduceMin",
        "ReduceProd", "ReduceSum",
        # DX elementwise ops
        "DX_Add", "DX_Mul", "DX_Round",
    ],
    "quantize": [
        "QuantizeLinear", "DequantizeLinear", "DynamicQuantizeLinear",
        "QLinearSigmoid", "QLinearLeakyRelu",
        "QLinearAdd", "QLinearAveragePool", "QLinearConcat",
        "QLinearGlobalAveragePool",
    ],
    "partition": [
        "NodeGroup_npu", "NodeGroup_cpu",
    ],
}

for _cat, _ops in _CATEGORIES.items():
    for _op in _ops:
        _CATEGORY_MAP[_op] = _cat


def categorize_op(op_type: str) -> str:
    """Return the category string for an ONNX op type."""
    return _CATEGORY_MAP.get(op_type, "other")



_DTYPE_MAP: Dict[int, str] = {
    TensorProto.FLOAT: "float32",
    TensorProto.UINT8: "uint8",
    TensorProto.INT8: "int8",
    TensorProto.UINT16: "uint16",
    TensorProto.INT16: "int16",
    TensorProto.INT32: "int32",
    TensorProto.INT64: "int64",
    TensorProto.BOOL: "bool",
    TensorProto.FLOAT16: "float16",
    TensorProto.DOUBLE: "float64",
    TensorProto.UINT32: "uint32",
    TensorProto.UINT64: "uint64",
    TensorProto.STRING: "string",
    TensorProto.COMPLEX64: "complex64",
    TensorProto.COMPLEX128: "complex128",
}

# Also handle BFLOAT16 if present in this onnx version
if hasattr(TensorProto, "BFLOAT16"):
    _DTYPE_MAP[TensorProto.BFLOAT16] = "bfloat16"

_DTYPE_BYTES: Dict[str, int] = {
    "float32": 4, "float64": 8, "float16": 2, "bfloat16": 2,
    "int8": 1, "uint8": 1, "int16": 2, "uint16": 2,
    "int32": 4, "uint32": 4, "int64": 8, "uint64": 8,
    "bool": 1, "complex64": 8, "complex128": 16,
}


def _dtype_str(elem_type: int) -> str:
    return _DTYPE_MAP.get(elem_type, f"unknown({elem_type})")


def _dtype_size(dtype_name: str) -> int:
    return _DTYPE_BYTES.get(dtype_name, 0)



def _extract_shape(type_proto) -> Optional[List[int]]:
    """Extract shape from a TypeProto, mapping symbolic dims to -1."""
    if not type_proto.HasField("tensor_type"):
        return None
    tensor_type = type_proto.tensor_type
    if not tensor_type.HasField("shape"):
        return None
    dims: List[int] = []
    for d in tensor_type.shape.dim:
        if d.dim_param:
            dims.append(-1)
        else:
            dims.append(d.dim_value)
    return dims


def _value_info_dict(vi) -> Dict[str, Any]:
    dtype = _dtype_str(vi.type.tensor_type.elem_type) if vi.type.HasField("tensor_type") else "unknown"
    shape = _extract_shape(vi.type)
    return {"name": vi.name, "shape": shape, "dtype": dtype}



def _extract_attr(attr: AttributeProto) -> Any:
    """Convert an ONNX AttributeProto to a plain Python value."""
    atype = attr.type
    if atype == AttributeProto.FLOAT:
        return float(attr.f)
    if atype == AttributeProto.INT:
        return int(attr.i)
    if atype == AttributeProto.STRING:
        return attr.s.decode("utf-8", errors="replace")
    if atype == AttributeProto.FLOATS:
        return list(float(v) for v in attr.floats)
    if atype == AttributeProto.INTS:
        return list(int(v) for v in attr.ints)
    if atype == AttributeProto.STRINGS:
        return [s.decode("utf-8", errors="replace") for s in attr.strings]
    if atype == AttributeProto.TENSOR:
        t = numpy_helper.to_array(attr.t)
        return {"shape": list(t.shape), "dtype": str(t.dtype), "data": "..."}
    if atype == AttributeProto.GRAPH:
        return {"graph_name": attr.g.name}
    return None



def parse_onnx_model(source: Union[str, onnx.ModelProto]) -> Dict[str, Any]:
    """Parse an ONNX model into a JSON-serializable graph dict.

    Parameters
    ----------
    source : str or onnx.ModelProto
        Either a file path to an ``.onnx`` file or an already-loaded
        ``ModelProto``.

    Returns
    -------
    dict
        Graph dict with keys: name, nodes, edges, inputs, outputs, params.

    Raises
    ------
    FileNotFoundError
        If *source* is a string path that does not exist.
    """
    if isinstance(source, str):
        path = source
        # If a directory is given, look for the first .onnx file in it
        if os.path.isdir(path):
            candidates = sorted(
                f for f in os.listdir(path)
                if f.lower().endswith('.onnx')
            )
            if not candidates:
                raise FileNotFoundError(f"No .onnx file found in directory: {path}")
            path = os.path.join(path, candidates[0])
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Model not found: {path}")

        # load_external_data=False: skip loading external .bin tensor data.
        # We only need graph topology, shapes, and dtypes — not raw weights.
        model = onnx.load(path, load_external_data=False)
    else:
        model = source

    # Run shape inference (best-effort; may fail without external data)
    try:
        model = shape_inference.infer_shapes(model)
    except Exception:
        pass

    graph = model.graph

    # Initializer names (parameters)
    initializer_names = {init.name for init in graph.initializer}

    # Build tensor → type info map from value_info + inputs + outputs
    tensor_info: Dict[str, Dict[str, Any]] = {}
    for vi in list(graph.value_info) + list(graph.input) + list(graph.output):
        tensor_info[vi.name] = _value_info_dict(vi)

    node_list: List[Dict[str, Any]] = []
    used_ids: set = set()
    output_to_node: Dict[str, str] = {}  # tensor_name → producing node id

    subgraphs: List[Dict[str, Any]] = []
    subgraph_initializers: list = []
    constant_params: list = []  # Constant op outputs treated as params

    for idx, node in enumerate(graph.node):
        if node.op_type.startswith("NodeGroup_"):
            sg_attr = None
            for attr in node.attribute:
                if attr.name == "subgraph" and attr.type == AttributeProto.GRAPH:
                    sg_attr = attr.g
                    break
            if sg_attr is None:
                continue

            subgraph_id = node.name  # e.g. "npu_0"
            device_suffix = node.op_type.split("_", 1)[1]  # e.g. "npu"

            # Merge subgraph initializers
            for init in sg_attr.initializer:
                initializer_names.add(init.name)
                subgraph_initializers.append(init)

            # Merge subgraph tensor info
            for vi in (list(sg_attr.value_info) + list(sg_attr.input)
                       + list(sg_attr.output)):
                tensor_info[vi.name] = _value_info_dict(vi)

            # Parse subgraph nodes
            sg_node_count = 0
            for sg_idx, sg_node in enumerate(sg_attr.node):
                # Constant nodes → params, not rendered
                if sg_node.op_type == "Constant":
                    for out_name in sg_node.output:
                        initializer_names.add(out_name)
                        for attr in sg_node.attribute:
                            if attr.name == "value" and attr.type == AttributeProto.TENSOR:
                                t = attr.t
                                constant_params.append({
                                    "name": out_name,
                                    "shape": list(t.dims),
                                    "dtype": _dtype_str(t.data_type),
                                })
                                break
                        else:
                            constant_params.append({
                                "name": out_name,
                                "shape": [],
                                "dtype": "unknown",
                            })
                    continue

                node_id = sg_node.name if sg_node.name else (
                    f"{sg_node.op_type}_{subgraph_id}_{sg_idx}")
                if node_id in used_ids:
                    suffix = 1
                    while f"{node_id}_{suffix}" in used_ids:
                        suffix += 1
                    node_id = f"{node_id}_{suffix}"
                used_ids.add(node_id)

                sg_attrs: Dict[str, Any] = {}
                for attr in sg_node.attribute:
                    val = _extract_attr(attr)
                    if val is not None:
                        sg_attrs[attr.name] = val

                node_dict = {
                    "id": node_id,
                    "op_type": sg_node.op_type,
                    "category": categorize_op(sg_node.op_type),
                    "inputs": list(sg_node.input),
                    "outputs": list(sg_node.output),
                    "attrs": sg_attrs,
                    "device": device_suffix,
                    "subgraph_id": subgraph_id,
                    "subgraph_device": device_suffix,
                }
                node_list.append(node_dict)
                sg_node_count += 1

                for out_name in sg_node.output:
                    output_to_node[out_name] = node_id

            # Register NodeGroup outer outputs as produced by the
            # corresponding subgraph producer so they are not classified
            # as implicit parameters.
            for outer_out, sg_out in zip(node.output, sg_attr.output):
                if outer_out and sg_out.name and sg_out.name in output_to_node:
                    output_to_node[outer_out] = output_to_node[sg_out.name]

            subgraphs.append({
                "id": subgraph_id,
                "device": device_suffix,
                "node_count": sg_node_count,
            })
            continue


        # Constant nodes are treated as parameters (like Netron).
        # Their outputs are added to initializer_names so downstream
        # edges are suppressed, and shape/dtype are recorded for the
        # params list.
        if node.op_type == "Constant":
            for out_name in node.output:
                initializer_names.add(out_name)
                # Extract shape/dtype from the value attribute
                for attr in node.attribute:
                    if attr.name == "value" and attr.type == AttributeProto.TENSOR:
                        t = attr.t
                        constant_params.append({
                            "name": out_name,
                            "shape": list(t.dims),
                            "dtype": _dtype_str(t.data_type),
                        })
                        break
                else:
                    # value_int / value_float / sparse_value variants
                    constant_params.append({
                        "name": out_name,
                        "shape": [],
                        "dtype": "unknown",
                    })
            continue

        node_id = node.name if node.name else f"{node.op_type}_{idx}"
        if node_id in used_ids:
            suffix = 1
            while f"{node_id}_{suffix}" in used_ids:
                suffix += 1
            node_id = f"{node_id}_{suffix}"
        used_ids.add(node_id)

        attrs: Dict[str, Any] = {}
        for attr in node.attribute:
            val = _extract_attr(attr)
            if val is not None:
                attrs[attr.name] = val

        node_dict = {
            "id": node_id,
            "op_type": node.op_type,
            "category": categorize_op(node.op_type),
            "inputs": list(node.input),
            "outputs": list(node.output),
            "attrs": attrs,
            "device": None,
        }
        node_list.append(node_dict)

        for out_name in node.output:
            output_to_node[out_name] = node_id

    # Detect implicit parameters: tensor names consumed by nodes but not
    # produced by any node and not declared as graph inputs.  This handles
    # NPU subgraphs where weights are baked into the binary and don't
    # appear in the ONNX initializer list (e.g. .dxnn files).
    graph_input_names = {vi.name for vi in graph.input}
    # Protect subgraph inputs from being flagged as implicit parameters
    for sg_info in subgraphs:
        for outer_node in graph.node:
            if outer_node.name == sg_info["id"]:
                for attr in outer_node.attribute:
                    if attr.name == "subgraph" and attr.type == AttributeProto.GRAPH:
                        for sg_input in attr.g.input:
                            graph_input_names.add(sg_input.name)
                break
    all_produced = set(output_to_node.keys())
    implicit_param_names: set = set()
    for node_dict in node_list:
        for inp in node_dict["inputs"]:
            if (inp and inp not in initializer_names
                    and inp not in graph_input_names
                    and inp not in all_produced):
                initializer_names.add(inp)
                implicit_param_names.add(inp)

    # Nodes whose ALL non-empty inputs come from initializers/constants
    # are param-processing ops (Identity, Reshape, Unsqueeze on weights).
    # Like Netron, remove them from the graph and treat their outputs as
    # params so they inline into consuming op nodes.
    changed = True
    while changed:
        changed = False
        kept: List[Dict[str, Any]] = []
        for nd in node_list:
            inputs = [i for i in nd["inputs"] if i]
            if inputs and all(i in initializer_names for i in inputs):
                # This node only processes params — hide it
                for out_name in nd["outputs"]:
                    initializer_names.add(out_name)
                    if out_name in output_to_node:
                        del output_to_node[out_name]
                    # Propagate shape/dtype info for the param
                    info = tensor_info.get(out_name, {})
                    if info:
                        constant_params.append({
                            "name": out_name,
                            "shape": info.get("shape"),
                            "dtype": info.get("dtype", "unknown"),
                        })
                    else:
                        constant_params.append({
                            "name": out_name,
                            "shape": None,
                            "dtype": "unknown",
                        })
                changed = True
            else:
                kept.append(nd)
        node_list = kept

    # Update subgraph node_count after param-only node removal
    for sg in subgraphs:
        sg["node_count"] = sum(
            1 for nd in node_list if nd.get("subgraph_id") == sg["id"]
        )

    # Remove Identity nodes with exactly 1 non-empty input and 1 non-empty output,
    # rewiring downstream consumers to the original source tensor.
    # Accumulate alias map across iterations so chained graph-output identities
    # resolve fully.
    accumulated_alias: Dict[str, str] = {}
    changed = True
    while changed:
        changed = False
        identity_map: Dict[str, str] = {}
        kept_nodes: List[Dict[str, Any]] = []
        for nd in node_list:
            if nd["op_type"] == "Identity":
                non_empty_inputs = [i for i in nd["inputs"] if i]
                non_empty_outputs = [o for o in nd["outputs"] if o]
                if len(non_empty_inputs) == 1 and len(non_empty_outputs) == 1:
                    identity_map[non_empty_outputs[0]] = non_empty_inputs[0]
                    accumulated_alias[non_empty_outputs[0]] = non_empty_inputs[0]
                    removed_node_id = nd["id"]
                    source_producer = output_to_node.get(non_empty_inputs[0])
                    # Update all output_to_node entries that reference the
                    # removed Identity — either as the direct output key or as
                    # a value (alias installed by NodeGroup boundary mapping).
                    # Do NOT delete the output key first; downstream chained
                    # Identities need the producer mapping to remain until
                    # they are processed.
                    for key, val in list(output_to_node.items()):
                        if key == non_empty_outputs[0] or val == removed_node_id:
                            if source_producer is not None:
                                output_to_node[key] = source_producer
                            else:
                                del output_to_node[key]
                    changed = True
                    continue
            kept_nodes.append(nd)
        node_list = kept_nodes

        # Resolve chained identities with cycle protection
        def _resolve(tensor: str, alias_map: Dict[str, str] = identity_map) -> str:
            visited: set = set()
            while tensor in alias_map:
                if tensor in visited:
                    break
                visited.add(tensor)
                tensor = alias_map[tensor]
            return tensor

        # Rewire remaining node inputs
        for nd in node_list:
            nd["inputs"] = [_resolve(i) if i else i for i in nd["inputs"]]

    # Recalculate subgraph node_count after Identity bypass
    for sg in subgraphs:
        sg["node_count"] = sum(
            1 for nd in node_list if nd.get("subgraph_id") == sg["id"]
        )

    edges: List[Dict[str, Any]] = []
    for node_dict in node_list:
        for inp in node_dict["inputs"]:
            if not inp or inp in initializer_names:
                continue
            info = tensor_info.get(inp, {})
            edge = {
                "from_node": output_to_node.get(inp),  # None for graph inputs
                "from_output": inp,
                "to_node": node_dict["id"],
                "to_input": inp,
                "shape": info.get("shape"),
                "dtype": info.get("dtype"),
            }
            edges.append(edge)

    inputs = [
        _value_info_dict(vi)
        for vi in graph.input
        if vi.name not in initializer_names
    ]

    outputs = [_value_info_dict(vi) for vi in graph.output]

    # Resolve accumulated Identity aliases for graph outputs with cycle protection
    def _resolve_accumulated(tensor: str) -> str:
        visited: set = set()
        while tensor in accumulated_alias:
            if tensor in visited:
                break
            visited.add(tensor)
            tensor = accumulated_alias[tensor]
        return tensor

    for out_dict in outputs:
        oname = out_dict["name"]
        if oname in accumulated_alias:
            resolved = _resolve_accumulated(oname)
            out_dict["source_name"] = resolved
            out_dict["source_node"] = output_to_node.get(resolved)

    # Ensure graph output tensor names can be resolved to producing nodes.
    # When NodeGroup flattening uses different internal names from root graph
    # output names, the lookup may fail.  Fall back to the last subgraph's
    # last node for any unresolved output.
    if subgraphs:
        for vi in graph.output:
            if vi.name not in output_to_node:
                last_sg_id = subgraphs[-1]["id"]
                for n in reversed(node_list):
                    if n.get("subgraph_id") == last_sg_id:
                        output_to_node[vi.name] = n["id"]
                        break

    params: List[Dict[str, Any]] = []
    seen_param_names: set = set()
    for init in list(graph.initializer) + subgraph_initializers:
        shape = list(init.dims)
        dtype = _dtype_str(init.data_type)
        num_elements = int(np.prod(shape)) if shape else 1
        size_bytes = num_elements * _dtype_size(dtype)
        params.append({
            "name": init.name,
            "shape": shape,
            "dtype": dtype,
            "size_bytes": size_bytes,
        })
        seen_param_names.add(init.name)

    # Add implicit params (detected from graph topology, no initializer data)
    for pname in sorted(implicit_param_names):
        if pname in seen_param_names:
            continue
        info = tensor_info.get(pname, {})
        shape = info.get("shape")
        dtype = info.get("dtype", "unknown")
        if shape:
            num_elements = int(np.prod([d for d in shape if d > 0])) if shape else 1
            size_bytes = num_elements * _dtype_size(dtype)
        else:
            size_bytes = 0
        params.append({
            "name": pname,
            "shape": shape,
            "dtype": dtype,
            "size_bytes": size_bytes,
        })

    # Add Constant-op outputs as params
    for cp in constant_params:
        if cp["name"] in seen_param_names:
            continue
        shape = cp["shape"]
        dtype = cp["dtype"]
        if shape:
            num_elements = int(np.prod([d for d in shape if d > 0])) if shape else 1
            size_bytes = num_elements * _dtype_size(dtype)
        else:
            size_bytes = 0
        params.append({
            "name": cp["name"],
            "shape": shape,
            "dtype": dtype,
            "size_bytes": size_bytes,
        })
        seen_param_names.add(cp["name"])

    return {
        "name": graph.name,
        "nodes": node_list,
        "edges": edges,
        "inputs": inputs,
        "outputs": outputs,
        "params": params,
        "tensor_info": tensor_info,
        "subgraphs": subgraphs,
    }
