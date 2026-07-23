"""Tests for Identity bypass and NodeGroup subgraph input protection in onnx_parser."""

from onnx import AttributeProto, TensorProto, helper

from dx_compiler.core.onnx_parser import parse_onnx_model



def _make_model(nodes, inputs=None, outputs=None, name="test_graph"):
    inputs = inputs or [helper.make_tensor_value_info("X", TensorProto.FLOAT, [1, 3, 4, 4])]
    outputs = outputs or [helper.make_tensor_value_info("Y", TensorProto.FLOAT, [1, 3, 4, 4])]
    graph = helper.make_graph(nodes, name, inputs, outputs)
    return helper.make_model(graph)


def _op_types(result):
    return [node["op_type"] for node in result["nodes"]]


def _edges_between(result, from_node, to_node):
    return [
        e for e in result["edges"]
        if e["from_node"] == from_node and e["to_node"] == to_node
    ]



class TestIdentityBypass:
    """Identity nodes with 1 non-empty input and 1 output should be bypassed."""

    def test_simple_identity_bypass_rewires_edge(self):
        """Relu -> Identity -> Sigmoid: Identity removed, edge relu->sigmoid."""
        nodes = [
            helper.make_node("Relu", ["X"], ["r_out"], name="relu_0"),
            helper.make_node("Identity", ["r_out"], ["id_out"], name="id_0"),
            helper.make_node("Sigmoid", ["id_out"], ["Y"], name="sig_0"),
        ]
        result = parse_onnx_model(_make_model(nodes))

        assert "Identity" not in _op_types(result)
        assert len(result["nodes"]) == 2
        edges = _edges_between(result, "relu_0", "sig_0")
        assert len(edges) >= 1

    def test_chained_identity_bypass_resolves_to_original_source(self):
        """Relu -> Identity -> Identity -> Sigmoid: both identities removed."""
        nodes = [
            helper.make_node("Relu", ["X"], ["r_out"], name="relu_0"),
            helper.make_node("Identity", ["r_out"], ["id1_out"], name="id_0"),
            helper.make_node("Identity", ["id1_out"], ["id2_out"], name="id_1"),
            helper.make_node("Sigmoid", ["id2_out"], ["Y"], name="sig_0"),
        ]
        result = parse_onnx_model(_make_model(nodes))

        assert "Identity" not in _op_types(result)
        assert len(result["nodes"]) == 2
        edges = _edges_between(result, "relu_0", "sig_0")
        assert len(edges) >= 1

    def test_identity_fanout_preserved(self):
        """Identity fans out X to Relu and Sigmoid; Identity removed."""
        nodes = [
            helper.make_node("Identity", ["X"], ["id_out"], name="id_0"),
            helper.make_node("Relu", ["id_out"], ["r_out"], name="relu_0"),
            helper.make_node("Sigmoid", ["id_out"], ["s_out"], name="sig_0"),
        ]
        out_r = helper.make_tensor_value_info("r_out", TensorProto.FLOAT, [1, 3, 4, 4])
        out_s = helper.make_tensor_value_info("s_out", TensorProto.FLOAT, [1, 3, 4, 4])
        result = parse_onnx_model(_make_model(nodes, outputs=[out_r, out_s]))

        assert "Identity" not in _op_types(result)
        # Both should get edges from graph input (from_node=None)
        relu_edges = [e for e in result["edges"] if e["to_node"] == "relu_0" and e["from_node"] is None]
        sig_edges = [e for e in result["edges"] if e["to_node"] == "sig_0" and e["from_node"] is None]
        assert len(relu_edges) >= 1
        assert len(sig_edges) >= 1

    def test_identity_at_graph_output_is_removed(self):
        """Relu -> Identity at graph output: Identity removed, output metadata traced."""
        nodes = [
            helper.make_node("Relu", ["X"], ["r_out"], name="relu_0"),
            helper.make_node("Identity", ["r_out"], ["Y"], name="id_0"),
        ]
        result = parse_onnx_model(_make_model(nodes))

        assert "Identity" not in _op_types(result)
        assert len(result["nodes"]) == 1
        out = result["outputs"][0]
        assert out["name"] == "Y"
        assert out["source_name"] == "r_out"
        assert out["source_node"] == "relu_0"

    def test_chained_identity_at_graph_output_resolves_fully(self):
        """Relu -> Identity -> Identity at graph output: resolves to Relu source."""
        nodes = [
            helper.make_node("Relu", ["X"], ["r_out"], name="relu_0"),
            helper.make_node("Identity", ["r_out"], ["id_out"], name="id_0"),
            helper.make_node("Identity", ["id_out"], ["Y"], name="id_1"),
        ]
        result = parse_onnx_model(_make_model(nodes))

        assert "Identity" not in _op_types(result)
        assert len(result["nodes"]) == 1
        out = result["outputs"][0]
        assert out["name"] == "Y"
        assert out["source_name"] == "r_out"
        assert out["source_node"] == "relu_0"

    def test_empty_output_identity_is_not_bypassed(self):
        """Identity with empty output string should not be bypassed."""
        nodes = [
            helper.make_node("Identity", ["X"], [""], name="id_0"),
        ]
        out = helper.make_tensor_value_info("", TensorProto.FLOAT, [1, 3, 4, 4])
        result = parse_onnx_model(_make_model(nodes, outputs=[out]))

        assert "Identity" in _op_types(result)

    def test_sole_identity_leaves_empty_node_list(self):
        """Graph with only Identity: result nodes == []."""
        nodes = [
            helper.make_node("Identity", ["X"], ["Y"], name="id_0"),
        ]
        result = parse_onnx_model(_make_model(nodes))

        assert result["nodes"] == []

    def test_multi_output_identity_is_not_bypassed(self):
        """Identity with outputs Y1, Y2 should remain."""
        nodes = [
            helper.make_node("Identity", ["X"], ["Y1", "Y2"], name="id_0"),
        ]
        out1 = helper.make_tensor_value_info("Y1", TensorProto.FLOAT, [1, 3, 4, 4])
        out2 = helper.make_tensor_value_info("Y2", TensorProto.FLOAT, [1, 3, 4, 4])
        result = parse_onnx_model(_make_model(nodes, outputs=[out1, out2]))

        assert "Identity" in _op_types(result)

    def test_empty_input_identity_is_not_bypassed(self):
        """Identity with empty input should remain."""
        nodes = [
            helper.make_node("Identity", [""], ["Y"], name="id_0"),
        ]
        result = parse_onnx_model(_make_model(nodes))

        assert "Identity" in _op_types(result)



def _make_nodegroup_model(subgraph_nodes, subgraph_inputs=None, subgraph_outputs=None):
    """Create a model with a NodeGroup_npu node containing a subgraph."""
    subgraph_inputs = subgraph_inputs or [
        helper.make_tensor_value_info("sg_X", TensorProto.FLOAT, [1, 3, 4, 4])
    ]
    subgraph_outputs = subgraph_outputs or [
        helper.make_tensor_value_info("sg_Y", TensorProto.FLOAT, [1, 3, 4, 4])
    ]

    sg = helper.make_graph(subgraph_nodes, "npu_0", subgraph_inputs, subgraph_outputs)

    graph_in = helper.make_tensor_value_info("X", TensorProto.FLOAT, [1, 3, 4, 4])
    graph_out = helper.make_tensor_value_info("sg_Y", TensorProto.FLOAT, [1, 3, 4, 4])

    ng_node = helper.make_node(
        "NodeGroup_npu", ["X"], ["sg_Y"], name="npu_0",
        device="npu", node_count=len(subgraph_nodes),
    )
    ng_node.attribute.append(helper.make_attribute("subgraph", sg))

    outer_graph = helper.make_graph([ng_node], "outer", [graph_in], [graph_out])
    return helper.make_model(outer_graph)


class TestNodeGroupSubgraph:
    """Tests for subgraph Identity bypass and input protection."""

    def test_identity_in_nodegroup_subgraph_is_bypassed_and_count_updated(self):
        """Subgraph Identity -> Relu -> Sigmoid: Identity removed, node_count == 2."""
        sg_nodes = [
            helper.make_node("Identity", ["sg_X"], ["id_out"], name="sg_id_0"),
            helper.make_node("Relu", ["id_out"], ["r_out"], name="sg_relu_0"),
            helper.make_node("Sigmoid", ["r_out"], ["sg_Y"], name="sg_sig_0"),
        ]
        result = parse_onnx_model(_make_nodegroup_model(sg_nodes))

        op_types = _op_types(result)
        assert "Identity" not in op_types
        assert result["subgraphs"][0]["node_count"] == 2

    def test_subgraph_input_is_not_reported_as_implicit_parameter(self):
        """Subgraph Relu uses sg_X input; params must not contain sg_X."""
        sg_nodes = [
            helper.make_node("Relu", ["sg_X"], ["sg_Y"], name="sg_relu_0"),
        ]
        result = parse_onnx_model(_make_nodegroup_model(sg_nodes))

        param_names = [p["name"] for p in result["params"]]
        assert "sg_X" not in param_names

    def test_nodegroup_outer_output_not_implicit_param(self):
        """NodeGroup outer output with distinct name must not become an implicit param.

        Graph:
          subgraph: Relu sg_X->sg_R, Sigmoid sg_R->sg_Y (sg_sig_0)
          NodeGroup_npu outer input X, outer output ng_out, subgraph output sg_Y
          root Identity ng_out->Y (graph_id_0), graph output Y

        Expected:
          - Identity is removed
          - output Y has source_name=="ng_out" and source_node=="sg_sig_0"
          - params do not include ng_out or Y
        """
        sg_inputs = [helper.make_tensor_value_info("sg_X", TensorProto.FLOAT, [1, 3, 4, 4])]
        sg_outputs = [helper.make_tensor_value_info("sg_Y", TensorProto.FLOAT, [1, 3, 4, 4])]
        sg_nodes = [
            helper.make_node("Relu", ["sg_X"], ["sg_R"], name="sg_relu_0"),
            helper.make_node("Sigmoid", ["sg_R"], ["sg_Y"], name="sg_sig_0"),
        ]
        sg = helper.make_graph(sg_nodes, "npu_0", sg_inputs, sg_outputs)

        graph_in = helper.make_tensor_value_info("X", TensorProto.FLOAT, [1, 3, 4, 4])
        graph_out = helper.make_tensor_value_info("Y", TensorProto.FLOAT, [1, 3, 4, 4])

        ng_node = helper.make_node(
            "NodeGroup_npu", ["X"], ["ng_out"], name="npu_0",
            device="npu", node_count=2,
        )
        ng_node.attribute.append(helper.make_attribute("subgraph", sg))

        id_node = helper.make_node("Identity", ["ng_out"], ["Y"], name="graph_id_0")

        outer_graph = helper.make_graph([ng_node, id_node], "outer", [graph_in], [graph_out])
        model = helper.make_model(outer_graph)

        result = parse_onnx_model(model)

        # Identity must be removed
        assert "Identity" not in _op_types(result)

        # Output Y must have source metadata
        out = next(o for o in result["outputs"] if o["name"] == "Y")
        assert out.get("source_name") == "ng_out", f"source_name={out.get('source_name')}"
        assert out.get("source_node") == "sg_sig_0", f"source_node={out.get('source_node')}"

        # ng_out and Y must not appear in params
        param_names = [p["name"] for p in result["params"]]
        assert "ng_out" not in param_names
        assert "Y" not in param_names

    def test_nodegroup_outer_output_stale_identity_alias(self):
        """Bypassed subgraph Identity must not leave stale output_to_node alias.

        Graph:
          subgraph: Relu sg_X->sg_R (sg_relu_0), Identity sg_R->sg_Y (sg_id_0)
          NodeGroup_npu outer output ng_out paired with subgraph output sg_Y
          root Identity ng_out->Y (graph_id_0), graph output Y

        Expected:
          - Both Identity nodes removed
          - No node with id "sg_id_0" remains
          - output Y has source_name=="ng_out", source_node=="sg_relu_0"
          - params do not include ng_out or Y
        """
        sg_inputs = [helper.make_tensor_value_info("sg_X", TensorProto.FLOAT, [1, 3, 4, 4])]
        sg_outputs = [helper.make_tensor_value_info("sg_Y", TensorProto.FLOAT, [1, 3, 4, 4])]
        sg_nodes = [
            helper.make_node("Relu", ["sg_X"], ["sg_R"], name="sg_relu_0"),
            helper.make_node("Identity", ["sg_R"], ["sg_Y"], name="sg_id_0"),
        ]
        sg = helper.make_graph(sg_nodes, "npu_0", sg_inputs, sg_outputs)

        graph_in = helper.make_tensor_value_info("X", TensorProto.FLOAT, [1, 3, 4, 4])
        graph_out = helper.make_tensor_value_info("Y", TensorProto.FLOAT, [1, 3, 4, 4])

        ng_node = helper.make_node(
            "NodeGroup_npu", ["X"], ["ng_out"], name="npu_0",
            device="npu", node_count=2,
        )
        ng_node.attribute.append(helper.make_attribute("subgraph", sg))

        id_node = helper.make_node("Identity", ["ng_out"], ["Y"], name="graph_id_0")

        outer_graph = helper.make_graph([ng_node, id_node], "outer", [graph_in], [graph_out])
        model = helper.make_model(outer_graph)

        result = parse_onnx_model(model)

        # Both Identity nodes must be removed
        assert "Identity" not in _op_types(result)

        # sg_id_0 must not remain
        node_ids = [n["id"] for n in result["nodes"]]
        assert "sg_id_0" not in node_ids, f"sg_id_0 still in nodes: {node_ids}"

        # Output Y must resolve through ng_out to the real producer sg_relu_0
        out = next(o for o in result["outputs"] if o["name"] == "Y")
        assert out.get("source_name") == "ng_out", f"source_name={out.get('source_name')}"
        assert out.get("source_node") == "sg_relu_0", f"source_node={out.get('source_node')}"

        # ng_out and Y must not appear in params
        param_names = [p["name"] for p in result["params"]]
        assert "ng_out" not in param_names
        assert "Y" not in param_names

    def test_chained_subgraph_identity_producer_resolution(self):
        """Chained subgraph Identities must resolve to the real non-Identity producer.

        Graph:
          subgraph: Relu sg_X->sg_R (sg_relu_0),
                    Identity sg_R->sg_M (sg_id_0),
                    Identity sg_M->sg_Y (sg_id_1)
          NodeGroup_npu outer output ng_out paired with subgraph output sg_Y
          root Identity ng_out->Y (graph_id_0), graph output Y

        Expected:
          - All Identity nodes removed
          - No node with id sg_id_0 or sg_id_1 remains
          - output Y has source_name=="ng_out", source_node=="sg_relu_0"
          - params do not include ng_out or Y
        """
        sg_inputs = [helper.make_tensor_value_info("sg_X", TensorProto.FLOAT, [1, 3, 4, 4])]
        sg_outputs = [helper.make_tensor_value_info("sg_Y", TensorProto.FLOAT, [1, 3, 4, 4])]
        sg_nodes = [
            helper.make_node("Relu", ["sg_X"], ["sg_R"], name="sg_relu_0"),
            helper.make_node("Identity", ["sg_R"], ["sg_M"], name="sg_id_0"),
            helper.make_node("Identity", ["sg_M"], ["sg_Y"], name="sg_id_1"),
        ]
        sg = helper.make_graph(sg_nodes, "npu_0", sg_inputs, sg_outputs)

        graph_in = helper.make_tensor_value_info("X", TensorProto.FLOAT, [1, 3, 4, 4])
        graph_out = helper.make_tensor_value_info("Y", TensorProto.FLOAT, [1, 3, 4, 4])

        ng_node = helper.make_node(
            "NodeGroup_npu", ["X"], ["ng_out"], name="npu_0",
            device="npu", node_count=3,
        )
        ng_node.attribute.append(helper.make_attribute("subgraph", sg))

        id_node = helper.make_node("Identity", ["ng_out"], ["Y"], name="graph_id_0")

        outer_graph = helper.make_graph([ng_node, id_node], "outer", [graph_in], [graph_out])
        model = helper.make_model(outer_graph)

        result = parse_onnx_model(model)

        # All Identity nodes must be removed
        assert "Identity" not in _op_types(result)

        # sg_id_0 and sg_id_1 must not remain
        node_ids = [n["id"] for n in result["nodes"]]
        assert "sg_id_0" not in node_ids, f"sg_id_0 still in nodes: {node_ids}"
        assert "sg_id_1" not in node_ids, f"sg_id_1 still in nodes: {node_ids}"

        # Output Y must resolve through ng_out to the real producer sg_relu_0
        out = next(o for o in result["outputs"] if o["name"] == "Y")
        assert out.get("source_name") == "ng_out", f"source_name={out.get('source_name')}"
        assert out.get("source_node") == "sg_relu_0", f"source_node={out.get('source_node')}"

        # ng_out and Y must not appear in params
        param_names = [p["name"] for p in result["params"]]
        assert "ng_out" not in param_names
        assert "Y" not in param_names
