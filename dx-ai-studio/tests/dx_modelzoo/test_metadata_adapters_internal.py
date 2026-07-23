"""_html_parser / _yaml_parser 분리 모듈에 대한 포커스 테스트."""

import os
import textwrap

import pytest




class TestModuleExists:
    def test_html_parser_module_importable(self):
        from dx_modelzoo.metadata import _html_parser  # noqa: F401

    def test_yaml_parser_module_importable(self):
        from dx_modelzoo.metadata import _yaml_parser  # noqa: F401




class TestHtmlParser:
    """_html_parser 모듈의 헬퍼 함수 테스트."""

    def test_parse_internal_table_models_empty_html(self):
        from dx_modelzoo.metadata._html_parser import parse_internal_table_models

        result = parse_internal_table_models("")
        assert result == {}

    def test_parse_internal_table_models_no_table(self):
        from dx_modelzoo.metadata._html_parser import parse_internal_table_models

        result = parse_internal_table_models("<p>hello</p>")
        assert result == {}

    def test_parse_internal_table_models_malformed_html(self):
        from dx_modelzoo.metadata._html_parser import parse_internal_table_models

        result = parse_internal_table_models("<table><tr><td>broken")
        # malformed HTML should not crash
        assert isinstance(result, dict)

    def test_parse_internal_table_models_simple_row(self):
        from dx_modelzoo.metadata._html_parser import parse_internal_table_models

        html = textwrap.dedent("""\
            <table>
            <thead><tr><th>Name</th><th>Class Name</th><th>Task</th></tr></thead>
            <tbody>
            <tr><td>MyModel</td><td>MyModelClass</td><td>classification</td></tr>
            </tbody>
            </table>
        """)
        models = parse_internal_table_models(html)
        assert len(models) > 0
        # canonical key 가 존재해야 한다
        assert any("mymodel" in k for k in models)

    def test_parse_internal_table_models_artifact_link(self):
        from dx_modelzoo.metadata._html_parser import parse_internal_table_models

        html = textwrap.dedent("""\
            <table>
            <thead><tr><th>Name</th><th>Class Name</th><th>Raw ONNX</th></tr></thead>
            <tbody>
            <tr>
                <td>TestModel</td>
                <td>TestModelClass</td>
                <td><a href="https://example.com/test.onnx">link</a></td>
            </tr>
            </tbody>
            </table>
        """)
        models = parse_internal_table_models(html)
        assert len(models) > 0
        entry = next(iter(models.values()))
        assert entry.get("artifacts.onnx.remote_url") == "https://example.com/test.onnx"

    def test_expand_table_headers_rowspan(self):
        from dx_modelzoo.metadata._html_parser import expand_table_headers

        header_rows = [
            [
                {"text": "Group", "rowspan": 2, "colspan": 1},
                {"text": "Metrics", "rowspan": 1, "colspan": 2},
            ],
            [
                {"text": "Acc", "rowspan": 1, "colspan": 1},
                {"text": "Loss", "rowspan": 1, "colspan": 1},
            ],
        ]
        headers = expand_table_headers(header_rows)
        assert len(headers) == 3
        assert headers[0] == "Group"
        assert "Acc" in headers[1]
        assert "Loss" in headers[2]

    def test_clean_cell_text(self):
        from dx_modelzoo.metadata._html_parser import clean_cell_text

        assert clean_cell_text("  hello   world  ") == "hello world"
        assert clean_cell_text(None) == ""

    def test_html_span_default(self):
        from dx_modelzoo.metadata._html_parser import html_span

        assert html_span(None) == 1
        assert html_span("3") == 3
        assert html_span("abc") == 1




class TestYamlParser:
    """_yaml_parser 모듈의 헬퍼 함수 테스트."""

    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("null", None),
            ("Null", None),
            ("NULL", None),
            ("~", None),
            ("", None),
            ("  ", None),
        ],
    )
    def test_yaml_scalar_null_variants(self, raw, expected):
        from dx_modelzoo.metadata._yaml_parser import yaml_scalar

        assert yaml_scalar(raw) is expected

    def test_yaml_scalar_quoted(self):
        from dx_modelzoo.metadata._yaml_parser import yaml_scalar

        assert yaml_scalar('"hello"') == "hello"
        assert yaml_scalar("'world'") == "world"

    def test_yaml_scalar_plain(self):
        from dx_modelzoo.metadata._yaml_parser import yaml_scalar

        assert yaml_scalar("plain_value") == "plain_value"

    def test_yaml_top_level_value(self):
        from dx_modelzoo.metadata._yaml_parser import yaml_top_level_value

        text = "name: MyModel\ntask: classification\n"
        assert yaml_top_level_value(text, "name") == "MyModel"
        assert yaml_top_level_value(text, "task") == "classification"
        assert yaml_top_level_value(text, "missing") is None

    def test_yaml_nested_value(self):
        from dx_modelzoo.metadata._yaml_parser import yaml_nested_value

        text = "dataset:\n  type: imagenet\n  split: val\n"
        assert yaml_nested_value(text, "dataset", "type") == "imagenet"
        assert yaml_nested_value(text, "dataset", "missing") is None

    def test_yaml_first_shape(self):
        from dx_modelzoo.metadata._yaml_parser import yaml_first_shape

        text = "inputs:\n  shape:\n    - 1\n    - 3\n    - 224\n    - 224\n"
        assert yaml_first_shape(text) == [1, 3, 224, 224]

    def test_yaml_first_shape_empty(self):
        from dx_modelzoo.metadata._yaml_parser import yaml_first_shape

        assert yaml_first_shape("no shape here") == []

    def test_parse_modelzoo_yaml_file(self, tmp_path):
        from dx_modelzoo.metadata._yaml_parser import parse_modelzoo_yaml_file

        yaml_content = textwrap.dedent("""\
            name: TestModel
            task: classification
            description: "A test model"
            reference: "https://example.com"
            macs: "1.5G"
            params: "3.2M"
            dataset:
              type: imagenet
            inputs:
              shape:
                - 1
                - 3
                - 224
                - 224
        """)
        yaml_file = tmp_path / "test_model.yaml"
        yaml_file.write_text(yaml_content)

        result = parse_modelzoo_yaml_file(yaml_file)
        assert len(result) == 1
        cid = next(iter(result))
        fields = result[cid]
        assert fields["display.name"] == "TestModel"
        assert fields["display.task"] == "classification"
        assert fields["specification.dataset"] == "imagenet"
        assert fields["technical.input_shape"] == [1, 3, 224, 224]
        assert fields["specification.input_resolution"] == "224x224"




class TestAdaptersCompatibility:
    """adapters.py 의 기존 public API 가 여전히 작동하는지 확인."""

    def test_parse_internal_table_html_still_available(self):
        from dx_modelzoo.metadata.adapters import parse_internal_table_html

        result = parse_internal_table_html("")
        assert result["adapter"] == "internal_table"
        assert result["models"] == {}

    def test_parse_modelzoo_yaml_file_still_available(self, tmp_path):
        from dx_modelzoo.metadata.adapters import parse_modelzoo_yaml_file

        yaml_content = "name: CompatModel\ntask: detection\n"
        yaml_file = tmp_path / "compat.yaml"
        yaml_file.write_text(yaml_content)

        result = parse_modelzoo_yaml_file(yaml_file)
        assert len(result) == 1
        cid = next(iter(result))
        assert result[cid]["display.name"] == "CompatModel"
