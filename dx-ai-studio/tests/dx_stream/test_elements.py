"""elements.py 테스트 — 엘리먼트 레퍼런스"""
import pytest

from tests.dx_stream._stream_import import pin_stream_core

pin_stream_core()

from core.elements import (
    get_elements, get_element_by_name, get_elements_by_category,
    validate_connection, get_connection_rules,
    CONNECTION_RULES, ELEMENT_OVERRIDES,
)


class TestElements:
    def test_get_elements_count(self):
        elems = get_elements()
        assert len(elems) >= 27

    def test_element_has_required_fields(self):
        from core.elements import get_elements
        required = {"name", "category", "description_ko", "description_en", "properties"}
        for e in get_elements():
            assert required.issubset(e.keys()), f"Element {e.get('name')} missing fields"

    def test_categories_present(self):
        from core.elements import get_elements
        cats = {e["category"] for e in get_elements()}
        assert "preprocess" in cats
        assert "inference" in cats
        assert "postprocess" in cats

    def test_properties_is_list(self):
        from core.elements import get_elements
        for e in get_elements():
            assert isinstance(e["properties"], list)

    def test_get_element_by_name(self):
        from core.elements import get_element_by_name
        elem = get_element_by_name("DxInfer")
        assert elem is not None
        assert elem["name"] == "DxInfer"

    def test_property_descriptions_bilingual(self):
        from core.elements import get_elements
        for e in get_elements():
            for p in e["properties"]:
                assert "description_ko" in p, \
                    f"{e['name']}.{p['name']} missing description_ko"
                assert "description_en" in p, \
                    f"{e['name']}.{p['name']} missing description_en"

    def test_vnpu_elements_present_and_phantom_removed(self):
        """staging(v3.1.0)에 실제 등록된 VNPU HW 코덱 엘리먼트는 노출하고, 실제 플러그인에
        존재하지 않던 팬텀 엘리먼트(run 시 'no element' 실패)는 제거되어야 한다."""
        names = [e["name"] for e in get_elements()]
        for expected in ["DxVnpuDec", "DxVnpuEnc", "DxVnpuPipeline", "DxVnpuOverlay", "tee", "webrtcbin"]:
            assert expected in names, f"{expected} missing from elements"
        for phantom in ["DxRoiExtract", "DxTile", "DxDeTile", "DxMux"]:
            assert phantom not in names, f"{phantom} does not exist in the dx_stream plugin — must not be exposed"

    def test_pipeline_palette_covers_dx_runtime_pipeline_elements(self):
        names = {e["name"] for e in get_elements()}
        runtime_elements = {
            "urisourcebin",
            "decodebin",
            "queue",
            "DxPreprocess",
            "DxInfer",
            "DxPostprocess",
            "DxMsgConv",
            "DxMsgBroker",
            "DxTracker",
            "DxOsd",
            "DxInputSelector",
            "DxOutputSelector",
            "DxGather",
            "DxScale",
            "tee",
            "compositor",
            "videoconvert",
            "fpsdisplaysink",
            "ximagesink",
        }

        missing = sorted(runtime_elements - names)

        assert not missing, f"Pipeline palette missing dx-runtime elements: {missing}"

    def test_connection_rule_referenced_elements_exist_in_palette(self):
        names = {e["name"] for e in get_elements()}
        referenced = {
            elem
            for rule in get_connection_rules()["auto_converter_rules"]
            for elem in rule.get("to_elements", [])
        }

        missing = sorted(referenced - names)

        assert not missing, f"Connection rules reference elements missing from palette: {missing}"

    def test_core_dx_elements_have_rich_reference_details(self):
        for name in ["DxPreprocess", "DxInfer", "DxPostprocess"]:
            elem = get_element_by_name(name)
            assert elem is not None
            assert len(elem.get("long_description_en", "")) > len(elem["description_en"])
            assert len(elem.get("long_description_ko", "")) > len(elem["description_ko"])
            assert elem.get("key_features"), f"{name} missing key features"
            assert elem.get("doc_path", "").startswith("Elements/03_"), \
                f"{name} missing SDK doc path"

    def test_dxinfer_reference_has_pipeline_hint_and_example_config(self):
        elem = get_element_by_name("DxInfer")
        assert "DxPreprocess" in elem.get("pipeline_hint_en", "")
        assert "DxPostprocess" in elem.get("pipeline_hint_en", "")
        assert "model-path" in elem.get("example_config", "")
        assert "DxPreprocess" in elem.get("related_elements", [])
        assert "DxPostprocess" in elem.get("related_elements", [])


class TestConnectionValidation:
    def test_validate_allow_source_to_preprocess(self):
        r = validate_connection("urisourcebin", "DxPreprocess")
        assert r["result"] == "allow"

    def test_validate_block_source_to_source(self):
        r = validate_connection("urisourcebin", "rtspsrc")
        assert r["result"] == "block"

    def test_validate_block_output_has_no_output(self):
        r = validate_connection("fpsdisplaysink", "DxInfer")
        assert r["result"] == "block"

    def test_validate_block_source_has_no_input(self):
        r = validate_connection("DxInfer", "urisourcebin")
        assert r["result"] == "block"

    def test_validate_block_category_not_allowed(self):
        r = validate_connection("urisourcebin", "DxInfer")
        assert r["result"] == "block"

    def test_validate_warn_inference_to_inference(self):
        r = validate_connection("DxInfer", "DxInfer")
        assert r["result"] == "warn"
        assert "postprocess" in r["reason_en"].lower() or "inference" in r["reason_en"].lower()

    def test_validate_auto_convert_viz_to_encoder(self):
        r = validate_connection("DxOsd", "vp8enc")
        assert r["result"] == "auto_convert"
        assert r["insert"] == "videoconvert"

    def test_validate_auto_convert_viz_to_runtime_display_sink(self):
        r = validate_connection("DxOsd", "ximagesink")
        assert r["result"] == "auto_convert"
        assert r["insert"] == "videoconvert"

    def test_validate_auto_convert_viz_to_h264_encoder(self):
        r = validate_connection("DxOsd", "x264enc")
        assert r["result"] == "auto_convert"
        assert r["insert"] == "videoconvert"

    def test_validate_allow_utility_to_anything(self):
        r = validate_connection("videoconvert", "DxInfer")
        assert r["result"] == "allow"

    def test_validate_allow_to_utility(self):
        r = validate_connection("DxInfer", "videoconvert")
        assert r["result"] == "allow"

    def test_validate_dxmsgbroker_no_output(self):
        r = validate_connection("DxMsgBroker", "DxInfer")
        assert r["result"] == "block"

    def test_validate_unknown_element_fallback(self):
        r = validate_connection("nonexistent_a", "nonexistent_b")
        assert r["result"] == "allow"

    def test_get_connection_rules_returns_all_keys(self):
        rules = get_connection_rules()
        assert "connection_rules" in rules
        assert "element_overrides" in rules
        assert "semantic_warnings" in rules
        assert "auto_converter_rules" in rules
