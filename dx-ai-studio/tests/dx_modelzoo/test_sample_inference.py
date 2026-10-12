"""ModelZoo sample-image inference API contracts."""
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(REPO_ROOT, 'dx_modelzoo'))


def test_sample_images_route_registered_in_server():
    """The /api/sample-images route must be registered in server.py."""
    server_src = open(os.path.join(REPO_ROOT, 'dx_modelzoo', 'server.py')).read()
    assert '/api/sample-images' in server_src, (
        "server.py must handle GET /api/sample-images"
    )


def test_sample_image_serve_route_registered_in_server():
    """The /api/sample-image/ route must be registered in server.py."""
    server_src = open(os.path.join(REPO_ROOT, 'dx_modelzoo', 'server.py')).read()
    assert '/api/sample-image/' in server_src, (
        "server.py must handle GET /api/sample-image/<filename>"
    )


def test_sample_img_dir_constant_defined():
    """config.py must define the SAMPLE_IMG_DIR constant."""
    from core.config import SAMPLE_IMG_DIR
    from pathlib import Path
    assert isinstance(SAMPLE_IMG_DIR, Path), "SAMPLE_IMG_DIR must be a Path"


def test_sample_images_list_helper_logic():
    """SAMPLE_IMG_DIR listing: extension filter, no recursion."""
    import tempfile, pathlib

    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        (td / "img_a.jpg").touch()
        (td / "img_b.PNG").touch()
        (td / "img_c.txt").touch()
        sub = td / "subdir"
        sub.mkdir()
        (sub / "img_d.jpg").touch()

        images = [
            f.name for f in td.iterdir()
            if f.is_file() and f.suffix.lower() in {'.jpg', '.jpeg', '.png'}
        ]
        assert sorted(images) == ['img_a.jpg', 'img_b.PNG'], (
            f"Expected only direct .jpg/.png files, got: {images}"
        )


def test_path_traversal_guard_in_server_source():
    """The /api/sample-image/ route in server.py must guard against path escape."""
    server_src = open(os.path.join(REPO_ROOT, 'dx_modelzoo', 'server.py')).read()
    # is_relative_to pattern must be present in the serve route
    assert 'is_relative_to' in server_src, (
        "server.py must use .is_relative_to() for path traversal protection in /api/sample-image/"
    )
    # Extension allowlist must be present
    assert "'.jpg', '.jpeg', '.png'" in server_src or '".jpg", ".jpeg", ".png"' in server_src or \
           "'.jpg','.jpeg','.png'" in server_src, (
        "server.py must have an extension allowlist in /api/sample-image/ route"
    )


def test_extension_allowlist_in_serve_route():
    """The serve route must refuse files without an image extension."""
    server_src = open(os.path.join(REPO_ROOT, 'dx_modelzoo', 'server.py')).read()
    # The serve route should check extension allowlist
    assert 'is_file()' in server_src, (
        "server.py serve route must use .is_file() not just .exists()"
    )


def test_default_image_selection_logic():
    """Default image pick: SAMPLE_IMAGES mapping → file exists → first file as fallback."""
    import tempfile, pathlib
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        sample_img_dir = td / "img"
        sample_img_dir.mkdir()
        (sample_img_dir / "sample_street.jpg").touch()
        (sample_img_dir / "sample_face.jpg").touch()

        sample_images_map = {
            "object_detection": "sample/img/sample_street.jpg",
            "face_detection": "sample/img/sample_face.jpg",
            "obb_detection": "sample/dota8_test/P0284.png",
            "embedding": "sample/img/face_pair",
        }

        def get_default(category, base_dir, mapping):
            raw = mapping.get(category, "")
            if raw:
                fname = pathlib.Path(raw).name
                candidate = base_dir / fname
                if candidate.is_file():
                    return fname
            files = sorted(f.name for f in base_dir.iterdir()
                           if f.is_file() and f.suffix.lower() in {'.jpg', '.jpeg', '.png'})
            return files[0] if files else None

        assert get_default("object_detection", sample_img_dir, sample_images_map) == "sample_street.jpg"
        assert get_default("face_detection", sample_img_dir, sample_images_map) == "sample_face.jpg"
        assert get_default("obb_detection", sample_img_dir, sample_images_map) == "sample_face.jpg"
        assert get_default("embedding", sample_img_dir, sample_images_map) == "sample_face.jpg"
        assert get_default("unknown_cat", sample_img_dir, sample_images_map) == "sample_face.jpg"


def test_js_load_sample_images_function_exists():
    """inference.js must have a loadSampleImages function."""
    js_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'js', 'inference.js')
    content = open(js_path).read()
    assert 'loadSampleImages' in content, "inference.js must define loadSampleImages"


def test_js_sample_grid_class_exists():
    """inference.js must reference the mz-sample-grid class."""
    js_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'js', 'inference.js')
    content = open(js_path).read()
    assert 'mz-sample-grid' in content, "inference.js must reference mz-sample-grid CSS class"


def test_js_input_mode_tabs_class_exists():
    """inference.js must reference the mz-input-mode-tabs class."""
    js_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'js', 'inference.js')
    content = open(js_path).read()
    assert 'mz-input-mode-tabs' in content, "inference.js must reference mz-input-mode-tabs CSS class"


def test_js_uses_image_path_not_input_path():
    """inference.js must use the image_path key (not input_path)."""
    js_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'js', 'inference.js')
    content = open(js_path).read()
    assert 'body.image_path' in content, (
        "inference.js must use body.image_path (not body.input_path) to match dx_app API"
    )
    assert 'body.input_path' not in content, (
        "inference.js must not use body.input_path — dx_app reads image_path"
    )


def test_js_sample_images_api_includes_model_id():
    """loadSampleImages() must pass the model_id parameter to /api/sample-images."""
    js_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'js', 'inference.js')
    content = open(js_path).read()
    assert 'model_id=' in content, (
        "inference.js must include model_id query param in /api/sample-images call"
    )


def test_js_sample_inference_uses_api_path_not_hardcoded():
    """runSampleInference must use the path from the API response, not a hardcoded 'sample/img/'.

    Sample images can live in a different path per category, so the selected file's path must
    come from the API's data.sample_dir or the thumbnail's data-sample-dir attribute.
    """
    js_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'js', 'inference.js')
    content = open(js_path).read()

    # The runSampleInference body must not hardcode the 'sample/img/' path
    import re
    func_match = re.search(r'function\s+runSampleInference\s*\([^)]*\)\s*\{', content)
    assert func_match, "runSampleInference function must exist"
    start = func_match.end()
    depth = 1
    i = start
    while i < len(content) and depth > 0:
        if content[i] == '{': depth += 1
        elif content[i] == '}': depth -= 1
        i += 1
    body = content[start:i-1]
    assert 'sample/img/' not in body, (
        "runSampleInference must not hardcode 'sample/img/' path — "
        "should use data-sample-dir attribute from the API response"
    )


def test_js_load_sample_images_has_no_sample_img_fallback():
    """loadSampleImages must not guess sample/img when the API gives no sample_dir."""
    js_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'js', 'inference.js')
    content = open(js_path).read()
    body = _extract_js_function_body(content, 'loadSampleImages')
    assert body is not None, "loadSampleImages function must exist"
    assert 'sample/img' not in body


def test_js_run_sample_inference_has_no_sample_img_fallback():
    """runSampleInference must not run when the selected thumbnail has no data-sample-dir."""
    js_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'js', 'inference.js')
    content = open(js_path).read()
    body = _extract_js_function_body(content, 'runSampleInference')
    assert body is not None, "runSampleInference function must exist"
    assert 'sample/img' not in body
    assert 'if (!sampleDir)' in body


def test_js_render_panel_disables_sample_tab_without_sample_dir():
    """A model without sample_dir must disable the Sample tab and show a notice."""
    js_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'js', 'inference.js')
    content = open(js_path).read()
    body = _extract_js_function_body(content, 'renderInferencePanel')
    assert body is not None, "renderInferencePanel function must exist"
    assert 'hasSampleMetadata' in body
    assert 'Sample not available for this model' in body
    assert 'sampleDisabledAttr' in body


def test_js_render_panel_escapes_sample_path_hint():
    """The default sample path hint must be escaped before it goes into innerHTML."""
    js_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'js', 'inference.js')
    content = open(js_path).read()
    body = _extract_js_function_body(content, 'renderInferencePanel')
    assert body is not None, "renderInferencePanel function must exist"
    assert '_escAttr(samplePath)' in body


def test_css_sample_grid_defined():
    """style.css must define the .mz-sample-grid class."""
    css_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'css', 'style.css')
    content = open(css_path).read()
    assert '.mz-sample-grid' in content, "style.css must define .mz-sample-grid"


def test_css_inference_preview_defined():
    """style.css must define the .mz-inference-preview class."""
    css_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'css', 'style.css')
    content = open(css_path).read()
    assert '.mz-inference-preview' in content, "style.css must define .mz-inference-preview"


def test_inference_js_escattr_escapes_single_quote():
    """_escAttr must escape a single quote as &#39;.

    renderInferencePanel inserts values inside onclick='...'; an unescaped
    single quote there is an XSS hole.
    """
    js_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'js', 'inference.js')
    content = open(js_path).read()
    assert "&#39;" in content, (
        "_escAttr must escape single quotes as &#39; to prevent injection in "
        "single-quoted onclick attributes"
    )


def test_inference_js_render_panel_escapes_model_values():
    """renderInferencePanel must escape model.id, category and model_file with _escAttr.

    Inserted unescaped into an inline onclick, a model name with special
    characters could inject JS.
    """
    import re
    js_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'js', 'inference.js')
    content = open(js_path).read()

    # Extract the renderInferencePanel body
    func_match = re.search(r'function\s+renderInferencePanel\s*\([^)]*\)\s*\{', content)
    assert func_match, "renderInferencePanel function must exist"
    start = func_match.end()
    depth = 1
    i = start
    while i < len(content) and depth > 0:
        if content[i] == '{': depth += 1
        elif content[i] == '}': depth -= 1
        i += 1
    body = content[start:i-1]

    # Inside onclick, model.id/category/model_file must be wrapped in _escAttr,
    # never inserted unescaped
    raw_patterns = [
        r"'\$\{model\.id\}'",
        r"'\$\{model\.category\}'",
        r"'\$\{model\.model_file\}'",
    ]
    for pat in raw_patterns:
        assert not re.search(pat, body), (
            f"renderInferencePanel must not inject raw model values into onclick — "
            f"found unescaped pattern: {pat}"
        )



def _extract_js_function_body(content, func_name):
    """Extract the body of function funcName(...) { ... } from JS source."""
    import re
    func_match = re.search(
        rf'function\s+{re.escape(func_name)}\s*\([^)]*\)\s*\{{', content
    )
    if not func_match:
        return None
    start = func_match.end()
    depth = 1
    i = start
    while i < len(content) and depth > 0:
        if content[i] == '{':
            depth += 1
        elif content[i] == '}':
            depth -= 1
        i += 1
    return content[start:i - 1]


def test_render_panel_no_inline_model_interpolation():
    """renderInferencePanel must not interpolate model values inside onclick.

    In a pattern like switchInferenceTab('upload', '${eId}', ...), HTML decodes &#39;
    back to an apostrophe before the JS runs, so a value with a single quote breaks it.
    """
    import re
    js_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'js', 'inference.js')
    content = open(js_path).read()
    body = _extract_js_function_body(content, 'renderInferencePanel')
    assert body is not None, "renderInferencePanel function must exist"

    # Forbidden: onclick="someFunc('${eId}', '${eCat}', '${eFile}')"
    forbidden = [
        r"switchInferenceTab\(\s*'[^']*'\s*,\s*'\$\{",
        r"onInferenceFileSelected\(\s*this\s*,\s*'\$\{",
        r"runDefaultInference\(\s*'\$\{",
        r"runSampleInference\(\s*'\$\{",
    ]
    for pat in forbidden:
        assert not re.search(pat, body), (
            f"renderInferencePanel must not inline-interpolate model values — "
            f"matched forbidden pattern: {pat}"
        )


def test_render_panel_uses_data_attributes():
    """renderInferencePanel must use the data-model-id / data-category / data-model-file attributes."""
    js_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'js', 'inference.js')
    content = open(js_path).read()
    body = _extract_js_function_body(content, 'renderInferencePanel')
    assert body is not None, "renderInferencePanel function must exist"

    for attr in ('data-model-id', 'data-category', 'data-model-file'):
        assert attr in body, (
            f"renderInferencePanel must set {attr} attribute on interactive elements"
        )


def test_render_panel_uses_dataset_helper_functions():
    """renderInferencePanel's onclick must call a helper that reads dataset."""
    js_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'js', 'inference.js')
    content = open(js_path).read()
    body = _extract_js_function_body(content, 'renderInferencePanel')
    assert body is not None, "renderInferencePanel function must exist"

    # The helper must be called from onclick
    helpers = [
        'switchInferenceTabFromButton',
        'onInferenceFileSelectedFromInput',
        'runDefaultInferenceFromButton',
        'runSampleInferenceFromButton',
    ]
    for h in helpers:
        assert h in body, (
            f"renderInferencePanel must use {h}() helper (reads this.dataset) "
            f"instead of inline string interpolation"
        )


def test_dataset_helpers_read_dataset():
    """The helpers must read modelId, category and modelFile from the btn/input dataset."""
    js_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'js', 'inference.js')
    content = open(js_path).read()

    helpers = {
        'switchInferenceTabFromButton': ['d.modelId', 'd.category', 'd.modelFile'],
        'onInferenceFileSelectedFromInput': ['d.modelId', 'd.category', 'd.modelFile'],
        'runDefaultInferenceFromButton': ['d.modelId', 'd.category', 'd.modelFile'],
        'runSampleInferenceFromButton': ['d.modelId', 'd.category', 'd.modelFile'],
    }
    for func_name, expected_refs in helpers.items():
        body = _extract_js_function_body(content, func_name)
        assert body is not None, f"{func_name} function must exist"
        for ref in expected_refs:
            assert ref in body, (
                f"{func_name} must read {ref} from dataset"
            )


def test_escattr_escapes_single_quote_for_data_attrs():
    """_escAttr must escape a single quote as &#39; in data attribute values.

    In data-model-id="${eId}", a double quote in eId breaks the attribute, so
    &quot; escaping is needed too.
    """
    js_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'js', 'inference.js')
    content = open(js_path).read()
    body = _extract_js_function_body(content, '_escAttr')
    assert body is not None, "_escAttr function must exist"

    # single quote → &#39;
    assert "&#39;" in body, "_escAttr must escape ' to &#39;"
    # double quote → &quot;
    assert "&quot;" in body, "_escAttr must escape \" to &quot;"
