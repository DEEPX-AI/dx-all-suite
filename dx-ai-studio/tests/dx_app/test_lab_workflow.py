"""RED contracts for Lab Composer workflow resolution and validation."""

from pathlib import Path

import pytest

from dx_app.core.lab_portal import lab_capabilities
from dx_app.core.lab_workflow import (
    _is_runnable,
    build_quick_start_workflow,
    build_template_workflow,
    default_graph_layout,
    validate_workflow,
)


def _runnable_models():
    return [{
        "name": "resnet18",
        "category": "classification",
        "model_file": "assets/models/resnet18_224x224.dxnn",
        "model_exists": True,
        "cpp": True,
        "cpp_sync": True,
    }]


def _workflow(**updates):
    workflow = {
        "schema_version": 1,
        "model": {
            "name": "resnet18",
            "category": "classification",
            "model_file": "assets/models/resnet18_224x224.dxnn",
            "language": "cpp",
            "variant": "sync",
        },
        "input": {"kind": "image", "path": "sample/img/sample_dog.jpg"},
        "nodes": [
            {"id": "input", "kind": "input", "enabled": True, "params": {}},
            {"id": "preprocess", "kind": "builtin_preprocess", "enabled": True, "params": {}},
            {"id": "inference", "kind": "inference", "enabled": True, "params": {}},
            {"id": "postprocess", "kind": "builtin_postprocess", "enabled": True, "params": {}},
            {"id": "visualize", "kind": "builtin_visualizer", "enabled": True, "params": {}},
        ],
        "plugins": [],
        "execution": {"save_output": True},
    }
    workflow.update(updates)
    return workflow


def test_quick_start_uses_runnable_registry_identity_only():
    workflow = build_quick_start_workflow(
        {"name": "ResNet-18", "category": "Image Classification"},
        models=_runnable_models(),
        assets=["sample/img/sample_dog.jpg"],
    )

    assert workflow["schema_version"] == 1
    assert workflow["id"].startswith("workflow_")
    assert workflow["source"] == "quick_start"
    assert workflow["template_id"] is None
    assert workflow["model"]["name"] == "resnet18"
    assert workflow["model"]["category"] == "classification"
    assert workflow["model"]["model_file"] == "assets/models/resnet18_224x224.dxnn"
    assert workflow["input"]["path"] == "sample/img/sample_dog.jpg"
    assert workflow["nodes"] == [
        {"id": "input", "kind": "input", "enabled": True, "params": {}},
        {"id": "preprocess", "kind": "builtin_preprocess", "enabled": True, "params": {}},
        {"id": "inference", "kind": "inference", "enabled": True, "params": {}},
        {"id": "postprocess", "kind": "builtin_postprocess", "enabled": True, "params": {}},
        {"id": "visualize", "kind": "builtin_visualizer", "enabled": True, "params": {}},
    ]
    assert workflow["plugins"] == []
    assert workflow["execution"] == {"device_id": None, "save_output": True}
    assert workflow["graph_layout"] == {
        "version": 1,
        "nodes": [
            {"id": "input", "x": 80, "y": 220},
            {"id": "preprocess", "x": 310, "y": 220},
            {"id": "inference", "x": 540, "y": 220},
            {"id": "postprocess", "x": 770, "y": 220},
            {"id": "visualize", "x": 1000, "y": 220},
        ],
        "edges": [
            {"id": "input-preprocess", "from": "input", "to": "preprocess"},
            {"id": "preprocess-inference", "from": "preprocess", "to": "inference"},
            {"id": "inference-postprocess", "from": "inference", "to": "postprocess"},
            {"id": "postprocess-visualize", "from": "postprocess", "to": "visualize"},
        ],
        "viewport": {"zoom": 1, "offset_x": 0, "offset_y": 0},
    }
    assert validate_workflow(workflow, plugin_root=None)["status"] == "ready"


@pytest.mark.parametrize(
    ("layout", "blocker"),
    [
        (
            {
                "version": 1,
                "nodes": [
                    {"id": "input", "x": 0, "y": 0},
                    {"id": "preprocess", "x": 0, "y": 0},
                    {"id": "inference", "x": 0, "y": 0},
                    {"id": "postprocess", "x": 0, "y": 0},
                    {"id": "unknown", "x": 0, "y": 0},
                ],
                "edges": [],
                "viewport": {"zoom": 1, "offset_x": 0, "offset_y": 0},
            },
            {"node_id": "graph", "code": "graph_node_invalid"},
        ),
        (
            {
                "version": 1,
                "nodes": [
                    {"id": "input", "x": 0, "y": 0},
                    {"id": "preprocess", "x": 0, "y": 0},
                    {"id": "inference", "x": 0, "y": 0},
                    {"id": "postprocess", "x": 0, "y": 0},
                    {"id": "visualize", "x": 0, "y": 0},
                ],
                "edges": [
                    {"id": "input-preprocess", "from": "input", "to": "preprocess"},
                    {"id": "preprocess-inference", "from": "preprocess", "to": "inference"},
                    {"id": "inference-postprocess", "from": "inference", "to": "postprocess"},
                    {"id": "visualize-postprocess", "from": "visualize", "to": "postprocess"},
                ],
                "viewport": {"zoom": 1, "offset_x": 0, "offset_y": 0},
            },
            {"node_id": "graph", "code": "graph_edge_invalid"},
        ),
        (
            {
                "version": 1,
                "nodes": [
                    {"id": "input", "x": float("nan"), "y": 0},
                    {"id": "preprocess", "x": 0, "y": 0},
                    {"id": "inference", "x": 0, "y": 0},
                    {"id": "postprocess", "x": 0, "y": 0},
                    {"id": "visualize", "x": 0, "y": 0},
                ],
                "edges": [
                    {"id": "input-preprocess", "from": "input", "to": "preprocess"},
                    {"id": "preprocess-inference", "from": "preprocess", "to": "inference"},
                    {"id": "inference-postprocess", "from": "inference", "to": "postprocess"},
                    {"id": "postprocess-visualize", "from": "postprocess", "to": "visualize"},
                ],
                "viewport": {"zoom": 1, "offset_x": 0, "offset_y": 0},
            },
            {"node_id": "graph", "code": "graph_position_invalid"},
        ),
    ],
)
def test_workflow_rejects_noncanonical_graph_layouts(layout, blocker):
    result = validate_workflow(_workflow(graph_layout=layout), plugin_root=None)

    assert result["status"] == "blocked"
    assert blocker in result["blockers"]


def test_workflow_rejects_missing_duplicate_out_of_range_and_malformed_graph_metadata():
    cases = [
        (
            "missing edge",
            lambda layout: layout["edges"].pop(),
            {"node_id": "graph", "code": "graph_edge_invalid"},
        ),
        (
            "duplicate edge",
            lambda layout: layout["edges"].append(dict(layout["edges"][0])),
            {"node_id": "graph", "code": "graph_edge_invalid"},
        ),
        (
            "out-of-range position",
            lambda layout: layout["nodes"][0].update({"x": 5001}),
            {"node_id": "graph", "code": "graph_position_invalid"},
        ),
        (
            "unknown top-level field",
            lambda layout: layout.update({"unexpected": True}),
            {"node_id": "graph", "code": "graph_layout_invalid"},
        ),
        (
            "malformed viewport",
            lambda layout: layout.update({"viewport": {"zoom": 1, "offset_x": 0, "offset_y": 0, "extra": 1}}),
            {"node_id": "graph", "code": "graph_viewport_invalid"},
        ),
    ]

    for _, mutate, blocker in cases:
        layout = default_graph_layout()
        mutate(layout)

        result = validate_workflow(_workflow(graph_layout=layout), plugin_root=None)

        assert result["status"] == "blocked"
        assert blocker in result["blockers"]


def test_quick_start_does_not_fall_back_to_display_only_catalog_rows():
    workflow = build_quick_start_workflow(
        {"name": "Download-only model", "category": "Image Classification"},
        models=_runnable_models(),
        assets=["sample/img/sample_dog.jpg"],
    )

    assert workflow["validation"]["status"] == "blocked"
    assert workflow["validation"]["blockers"] == [
        {"node_id": "model", "code": "runnable_model_not_found"}
    ]


def test_workflow_with_unresolved_custom_plugin_is_blocked(tmp_path):
    workflow = _workflow(plugins=[{
        "id": "custom_postprocess",
        "stage": "postprocess",
        "language": "python",
        "entrypoint": "plugins/postprocess/missing.py",
        "interface_version": 1,
        "enabled": True,
    }])

    result = validate_workflow(workflow, plugin_root=tmp_path)
    assert result["status"] == "blocked"
    assert result["blockers"] == [
        {"node_id": "custom_postprocess", "code": "plugin_not_found"}
    ]


def test_workflow_with_unsafe_custom_plugin_path_is_blocked(tmp_path):
    workflow = _workflow(plugins=[{
        "id": "custom_preprocess",
        "stage": "preprocess",
        "language": "python",
        "entrypoint": "../../outside.py",
        "interface_version": 1,
        "enabled": True,
    }])

    result = validate_workflow(workflow, plugin_root=tmp_path)
    assert result["status"] == "blocked"
    assert result["blockers"] == [
        {"node_id": "custom_preprocess", "code": "plugin_path_unsafe"}
    ]


@pytest.mark.parametrize(
    ("nodes", "blocker"),
    [
        (
            [
                {"id": "input", "kind": "input", "enabled": True, "params": {}},
                {"id": "preprocess", "kind": "builtin_preprocess", "enabled": True, "params": {}},
                {"id": "postprocess", "kind": "builtin_postprocess", "enabled": True, "params": {}},
                {"id": "visualize", "kind": "builtin_visualizer", "enabled": True, "params": {}},
            ],
            {"node_id": "inference", "code": "inference_required"},
        ),
        (
            [
                {"id": "input", "kind": "input", "enabled": True, "params": {}},
                {"id": "preprocess", "kind": "builtin_preprocess", "enabled": True, "params": {}},
                {"id": "inference-1", "kind": "inference", "enabled": True, "params": {}},
                {"id": "inference-2", "kind": "inference", "enabled": True, "params": {}},
                {"id": "postprocess", "kind": "builtin_postprocess", "enabled": True, "params": {}},
                {"id": "visualize", "kind": "builtin_visualizer", "enabled": True, "params": {}},
            ],
            {"node_id": "inference", "code": "inference_count_invalid"},
        ),
        (
            [
                {"id": "input", "kind": "input", "enabled": True, "params": {}},
                {"id": "inference", "kind": "inference", "enabled": True, "params": {}},
                {"id": "preprocess", "kind": "builtin_preprocess", "enabled": True, "params": {}},
                {"id": "postprocess", "kind": "builtin_postprocess", "enabled": True, "params": {}},
                {"id": "visualize", "kind": "builtin_visualizer", "enabled": True, "params": {}},
            ],
            {"node_id": "preprocess", "code": "core_stage_order_invalid"},
        ),
        (
            [
                {"id": "input", "kind": "input", "enabled": True, "params": {}},
                {"id": "preprocess", "kind": "builtin_preprocess", "enabled": False, "params": {}},
                {"id": "inference", "kind": "inference", "enabled": True, "params": {}},
                {"id": "postprocess", "kind": "builtin_postprocess", "enabled": True, "params": {}},
                {"id": "visualize", "kind": "builtin_visualizer", "enabled": True, "params": {}},
            ],
            {"node_id": "preprocess", "code": "core_stage_required"},
        ),
    ],
)
def test_workflow_rejects_missing_duplicate_or_reordered_core_stages(nodes, blocker):
    result = validate_workflow(_workflow(nodes=nodes), plugin_root=None)
    assert result["status"] == "blocked"
    assert blocker in result["blockers"]


def test_workflow_rejects_unknown_node_kinds():
    workflow = _workflow(nodes=[
        {"id": "input", "kind": "input", "enabled": True, "params": {}},
        {"id": "preprocess", "kind": "builtin_preprocess", "enabled": True, "params": {}},
        {"id": "inference", "kind": "inference", "enabled": True, "params": {}},
        {"id": "unexpected", "kind": "network_request", "enabled": True, "params": {}},
        {"id": "postprocess", "kind": "builtin_postprocess", "enabled": True, "params": {}},
        {"id": "visualize", "kind": "builtin_visualizer", "enabled": True, "params": {}},
    ])

    result = validate_workflow(workflow, plugin_root=None)

    assert result["status"] == "blocked"
    assert {"node_id": "unexpected", "code": "unknown_node_kind"} in result["blockers"]


@pytest.mark.parametrize("model_exists", [None, False, 0, "", "yes"])
def test_runnable_identity_requires_literal_true_model_exists(model_exists):
    model = {
        "name": "resnet18",
        "model_exists": model_exists,
        "cpp_sync": True,
    }

    assert _is_runnable(model) is False


@pytest.mark.parametrize("runner", ("cpp_sync", "py_sync"))
def test_runnable_identity_accepts_literal_true_model_exists_with_sync_runner(runner):
    model = {"name": "resnet18", "model_exists": True, runner: True}

    assert _is_runnable(model) is True


def test_composer_capabilities_publish_canonical_templates_and_package_types():
    composer = lab_capabilities()["composer"]

    assert {
        "classification_image",
        "detection_image",
        "segmentation_image",
        "pose_image",
        "ocr_image",
        "video",
        "camera",
    } <= set(composer["templates"])
    assert composer["templates"]["detection_image"] == {
        "category": "object_detection",
        "input_kind": "image",
    }
    assert composer["templates"]["segmentation_image"] == {
        "category": "semantic_segmentation",
        "input_kind": "image",
    }
    assert set(composer["package_types"]) == {"recipe", "run", "developer"}
    assert composer["feature_flags"]["developer_package_export"] is True


def test_detection_image_template_uses_matching_runnable_model_and_real_image():
    model = {
        "name": "yolov8n",
        "category": "object_detection",
        "model_file": "assets/models/yolov8n.dxnn",
        "model_exists": True,
        "py_sync": True,
    }

    workflow = build_template_workflow(
        "detection_image",
        models=[model, _runnable_models()[0]],
        images=["sample/img/sample_dog.jpg"],
        videos=[],
    )

    assert workflow["model"]["name"] == "yolov8n"
    assert workflow["input"] == {"kind": "image", "path": "sample/img/sample_dog.jpg"}
    assert workflow["validation"]["status"] == "ready"


def test_template_without_compatible_asset_and_unknown_template_are_blocked():
    model = {
        "name": "yolov8n",
        "category": "object_detection",
        "model_file": "assets/models/yolov8n.dxnn",
        "model_exists": True,
        "cpp_sync": True,
    }

    missing_asset = build_template_workflow(
        "detection_image", models=[model], images=[], videos=[]
    )
    unknown = build_template_workflow(
        "unrecognised_template", models=[model], images=["sample/img/sample_dog.jpg"], videos=[]
    )

    assert missing_asset["validation"]["status"] == "blocked"
    assert {"node_id": "input", "code": "compatible_input_not_found"} in missing_asset["validation"]["blockers"]
    assert unknown["validation"]["status"] == "blocked"
    assert {"node_id": "template", "code": "template_not_found"} in unknown["validation"]["blockers"]


def test_camera_template_without_runtime_input_is_blocked():
    workflow = build_template_workflow(
        "camera", models=_runnable_models(), images=[], videos=[]
    )

    assert workflow["input"] == {"kind": "camera", "path": ""}
    assert workflow["validation"]["status"] == "blocked"
    assert {"node_id": "input", "code": "camera_input_not_available"} in workflow["validation"]["blockers"]


def test_plugin_scaffold_templates_have_exact_interfaces_and_are_incomplete():
    template_root = Path(__file__).resolve().parents[2] / "dx_app" / "templates" / "lab_plugins"
    python_preprocess = (template_root / "python_preprocess.py").read_text(encoding="utf-8")
    python_postprocess = (template_root / "python_postprocess.py").read_text(encoding="utf-8")
    cpp_preprocess = (template_root / "cpp_preprocess.hpp").read_text(encoding="utf-8")
    cpp_postprocess = (template_root / "cpp_postprocess.hpp").read_text(encoding="utf-8")

    assert 'def preprocess(image, context):' in python_preprocess
    assert 'raise NotImplementedError("Implement preprocess(image, context)")' in python_preprocess
    assert 'def postprocess(outputs, context):' in python_postprocess
    assert 'raise NotImplementedError("Implement postprocess(outputs, context)")' in python_postprocess
    for source, function, parameter in (
        (cpp_preprocess, "preprocess", "input_path"),
        (cpp_postprocess, "postprocess", "output_path"),
    ):
        assert "#pragma once" in source
        assert "#include <string>" in source
        assert "namespace dx_app_lab" in source
        assert f"std::string {function}(const std::string& {parameter}, const PluginContext& context);" in source


def test_cpp_plugin_requires_exact_interface_and_cmake_source_registration(tmp_path):
    plugin_path = tmp_path / "plugins" / "postprocess" / "custom_postprocess.hpp"
    plugin_path.parent.mkdir(parents=True)
    plugin_path.write_text(
        """#pragma once
#include <string>
namespace dx_app_lab {
struct PluginContext;
std::string postprocess(const std::string& output_path, const PluginContext& context);
}
""",
        encoding="utf-8",
    )
    workflow = _workflow(plugins=[{
        "id": "custom_postprocess",
        "stage": "postprocess",
        "language": "cpp",
        "entrypoint": "plugins/postprocess/custom_postprocess.hpp",
        "interface_version": 1,
        "enabled": True,
    }])

    missing_cmake = validate_workflow(workflow, plugin_root=tmp_path)
    assert {"node_id": "custom_postprocess", "code": "plugin_cmake_source_missing"} in missing_cmake["blockers"]

    (tmp_path / "CMakeLists.txt").write_text(
        "set(DX_APP_LAB_PLUGIN_SOURCES plugins/postprocess/custom_postprocess.hpp)\n",
        encoding="utf-8",
    )
    assert validate_workflow(workflow, plugin_root=tmp_path)["status"] == "ready"


def test_cpp_plugin_without_required_interface_markers_is_incomplete(tmp_path):
    plugin_path = tmp_path / "plugins" / "preprocess" / "custom_preprocess.hpp"
    plugin_path.parent.mkdir(parents=True)
    plugin_path.write_text(
        """namespace dx_app_lab {
std::string preprocess(const std::string& input_path, const PluginContext& context);
}
""",
        encoding="utf-8",
    )
    (tmp_path / "CMakeLists.txt").write_text(
        "set(DX_APP_LAB_PLUGIN_SOURCES plugins/preprocess/custom_preprocess.hpp)\n",
        encoding="utf-8",
    )
    workflow = _workflow(plugins=[{
        "id": "custom_preprocess",
        "stage": "preprocess",
        "language": "cpp",
        "entrypoint": "plugins/preprocess/custom_preprocess.hpp",
        "interface_version": 1,
        "enabled": True,
    }])

    result = validate_workflow(workflow, plugin_root=tmp_path)
    assert {"node_id": "custom_preprocess", "code": "plugin_incomplete"} in result["blockers"]


def test_scaffolded_python_plugin_is_blocked_until_implemented(tmp_path):
    template = (
        Path(__file__).resolve().parents[2]
        / "dx_app" / "templates" / "lab_plugins" / "python_preprocess.py"
    )
    plugin_path = tmp_path / "plugins" / "preprocess" / "custom_preprocess.py"
    plugin_path.parent.mkdir(parents=True)
    plugin_path.write_text(template.read_text(encoding="utf-8"), encoding="utf-8")
    workflow = _workflow(plugins=[{
        "id": "custom_preprocess",
        "stage": "preprocess",
        "language": "python",
        "entrypoint": "plugins/preprocess/custom_preprocess.py",
        "interface_version": 1,
        "enabled": True,
    }])

    result = validate_workflow(workflow, plugin_root=tmp_path)
    assert {"node_id": "custom_preprocess", "code": "plugin_incomplete"} in result["blockers"]


def test_plugin_scaffold_plan_returns_session_bound_preview_without_writing(tmp_path, monkeypatch):
    import dx_app.core.lab_portal as lab_portal
    from dx_app.core.developer import lab_session

    token = lab_session()["token"]
    workflow_manifest = lab_portal.create_manifest(
        "composer_workflow", workflow=_workflow(), creator_token=token
    )
    monkeypatch.setattr(lab_portal, "OUTPUTS_DIR", tmp_path)

    result = lab_portal.plan_composer_plugin_scaffold(token, {
        "workflow_manifest_id": workflow_manifest["id"],
        "plugin_name": "custom_preprocess",
        "stage": "preprocess",
        "language": "python",
    })

    assert result["kind"] == "composer_plugin_scaffold"
    assert result["creator_token"] == token
    assert result["status"] == "ready"
    assert result["operations"]
    assert all(operation["root"] == "OUTPUTS_DIR" for operation in result["operations"])
    assert all("lab_composer" in operation["path"] for operation in result["operations"])
    assert not any(tmp_path.rglob("*"))


def test_cpp_plugin_scaffold_preview_preserves_existing_cmake_sources(tmp_path, monkeypatch):
    import dx_app.core.lab_portal as lab_portal
    from dx_app.core.developer import lab_session

    token = lab_session()["token"]
    workflow_manifest = lab_portal.create_manifest(
        "composer_workflow", workflow=_workflow(), creator_token=token
    )
    monkeypatch.setattr(lab_portal, "OUTPUTS_DIR", tmp_path)
    workspace = tmp_path / "lab_composer" / workflow_manifest["id"]
    workspace.mkdir(parents=True)
    (workspace / "CMakeLists.txt").write_text(
        "set(DX_APP_LAB_PLUGIN_SOURCES\n"
        "    plugins/preprocess/first.hpp\n"
        ")\n",
        encoding="utf-8",
    )

    result = lab_portal.plan_composer_plugin_scaffold(token, {
        "workflow_manifest_id": workflow_manifest["id"],
        "plugin_name": "second",
        "stage": "postprocess",
        "language": "cpp",
    })

    cmake_preview = next(
        operation["preview"]
        for operation in result["operations"]
        if operation["path"].endswith("CMakeLists.txt")
    )
    assert "plugins/preprocess/first.hpp" in cmake_preview
    assert "plugins/postprocess/second.hpp" in cmake_preview


def test_plugin_scaffold_plan_rejects_symlinked_session_workspace(tmp_path, monkeypatch):
    import dx_app.core.lab_portal as lab_portal
    from dx_app.core.developer import lab_session

    token = lab_session()["token"]
    workflow_manifest = lab_portal.create_manifest(
        "composer_workflow", workflow=_workflow(), creator_token=token
    )
    outside = tmp_path / "outside"
    outside.mkdir()
    (tmp_path / "lab_composer").symlink_to(outside, target_is_directory=True)
    monkeypatch.setattr(lab_portal, "OUTPUTS_DIR", tmp_path)

    result = lab_portal.plan_composer_plugin_scaffold(token, {
        "workflow_manifest_id": workflow_manifest["id"],
        "plugin_name": "custom_preprocess",
        "stage": "preprocess",
        "language": "python",
    })

    assert result["status"] == 400
    assert result["error_code"] == "plugin_path_unsafe"

def test_compatible_asset_prefers_task_appropriate_default():
    """Quick Start's default input should suit the task: a generic detector must not
    default to a face crop just because it sorts first; a face model should get a face."""
    from dx_app.core.lab_workflow import _compatible_asset

    assets = [
        "sample/img/face_pair",
        "sample/img/sample_crowd.jpg",
        "sample/img/sample_dog.jpg",
        "sample/img/sample_face.jpg",
    ]
    # generic object detection → general scene, not the alphabetically-first face crop
    assert _compatible_asset(assets, "image", "object_detection") == "sample/img/sample_dog.jpg"
    # classification (no specific family) → general default
    assert _compatible_asset(assets, "image", "classification") == "sample/img/sample_dog.jpg"
    # face task → a face sample
    assert _compatible_asset(assets, "image", "face_detection") == "sample/img/sample_face.jpg"


def test_compatible_asset_falls_back_to_first_when_no_preferred_present():
    from dx_app.core.lab_workflow import _compatible_asset

    only = ["sample/img/face_pair"]
    # nothing preferred/general installed → keep working, return the first compatible
    assert _compatible_asset(only, "image", "object_detection") == "sample/img/face_pair"
    # no compatible asset at all
    assert _compatible_asset([], "image", "object_detection") is None
