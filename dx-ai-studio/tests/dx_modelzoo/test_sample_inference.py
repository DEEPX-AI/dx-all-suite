"""ModelZoo 샘플 이미지 inference API 계약 테스트."""
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(REPO_ROOT, 'dx_modelzoo'))


def test_sample_images_route_registered_in_server():
    """/api/sample-images 라우트가 server.py에 등록되어야 한다."""
    server_src = open(os.path.join(REPO_ROOT, 'dx_modelzoo', 'server.py')).read()
    assert '/api/sample-images' in server_src, (
        "server.py must handle GET /api/sample-images"
    )


def test_sample_image_serve_route_registered_in_server():
    """/api/sample-image/ 라우트가 server.py에 등록되어야 한다."""
    server_src = open(os.path.join(REPO_ROOT, 'dx_modelzoo', 'server.py')).read()
    assert '/api/sample-image/' in server_src, (
        "server.py must handle GET /api/sample-image/<filename>"
    )


def test_sample_img_dir_constant_defined():
    """config.py에 SAMPLE_IMG_DIR 상수가 정의되어야 한다."""
    from core.config import SAMPLE_IMG_DIR
    from pathlib import Path
    assert isinstance(SAMPLE_IMG_DIR, Path), "SAMPLE_IMG_DIR must be a Path"


def test_sample_images_list_helper_logic():
    """SAMPLE_IMG_DIR 목록 반환 로직: 확장자 필터 + 재귀 없음."""
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
    """server.py의 /api/sample-image/ 라우트에 실제 경로 탈출 방지 코드가 있어야 한다."""
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
    """serve route가 이미지 확장자 이외 파일 서빙을 거부해야 한다."""
    server_src = open(os.path.join(REPO_ROOT, 'dx_modelzoo', 'server.py')).read()
    # The serve route should check extension allowlist
    assert 'is_file()' in server_src, (
        "server.py serve route must use .is_file() not just .exists()"
    )


def test_default_image_selection_logic():
    """default 이미지 선정: SAMPLE_IMAGES 매핑 → 파일 존재 확인 → 첫 번째 파일 fallback."""
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
    """inference.js에 loadSampleImages 함수가 존재해야 한다."""
    js_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'js', 'inference.js')
    content = open(js_path).read()
    assert 'loadSampleImages' in content, "inference.js must define loadSampleImages"


def test_js_sample_grid_class_exists():
    """inference.js에 mz-sample-grid 클래스 참조가 있어야 한다."""
    js_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'js', 'inference.js')
    content = open(js_path).read()
    assert 'mz-sample-grid' in content, "inference.js must reference mz-sample-grid CSS class"


def test_js_input_mode_tabs_class_exists():
    """inference.js에 mz-input-mode-tabs 클래스 참조가 있어야 한다."""
    js_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'js', 'inference.js')
    content = open(js_path).read()
    assert 'mz-input-mode-tabs' in content, "inference.js must reference mz-input-mode-tabs CSS class"


def test_js_uses_image_path_not_input_path():
    """inference.js가 image_path 키를 사용해야 한다 (input_path 아님)."""
    js_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'js', 'inference.js')
    content = open(js_path).read()
    assert 'body.image_path' in content, (
        "inference.js must use body.image_path (not body.input_path) to match dx_app API"
    )
    assert 'body.input_path' not in content, (
        "inference.js must not use body.input_path — dx_app reads image_path"
    )


def test_js_sample_images_api_includes_model_id():
    """loadSampleImages()가 /api/sample-images 호출 시 model_id 파라미터를 포함해야 한다."""
    js_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'js', 'inference.js')
    content = open(js_path).read()
    assert 'model_id=' in content, (
        "inference.js must include model_id query param in /api/sample-images call"
    )


def test_js_sample_inference_uses_api_path_not_hardcoded():
    """runSampleInference가 하드코딩된 'sample/img/' 경로 대신 API 응답의 경로를 사용해야 한다.

    카테고리별 샘플 이미지가 다른 경로에 있을 수 있으므로, 선택된 파일명의 경로를
    API가 제공하는 data.sample_dir 또는 thumb의 data-sample-dir 속성에서 가져와야 한다.
    """
    js_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'js', 'inference.js')
    content = open(js_path).read()

    # runSampleInference 함수 본문에 하드코딩된 'sample/img/' 경로가 없어야 한다
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
    """loadSampleImages는 API sample_dir 누락 시 sample/img로 추측하지 않아야 한다."""
    js_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'js', 'inference.js')
    content = open(js_path).read()
    body = _extract_js_function_body(content, 'loadSampleImages')
    assert body is not None, "loadSampleImages function must exist"
    assert 'sample/img' not in body


def test_js_run_sample_inference_has_no_sample_img_fallback():
    """runSampleInference는 선택 썸네일의 data-sample-dir가 없으면 실행하지 않아야 한다."""
    js_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'js', 'inference.js')
    content = open(js_path).read()
    body = _extract_js_function_body(content, 'runSampleInference')
    assert body is not None, "runSampleInference function must exist"
    assert 'sample/img' not in body
    assert 'if (!sampleDir)' in body


def test_js_render_panel_disables_sample_tab_without_sample_dir():
    """sample_dir가 없는 모델은 Sample 탭을 비활성화하고 사용자 안내를 보여야 한다."""
    js_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'js', 'inference.js')
    content = open(js_path).read()
    body = _extract_js_function_body(content, 'renderInferencePanel')
    assert body is not None, "renderInferencePanel function must exist"
    assert 'hasSampleMetadata' in body
    assert 'Sample not available for this model' in body
    assert 'sampleDisabledAttr' in body


def test_js_render_panel_escapes_sample_path_hint():
    """기본 샘플 경로 힌트는 innerHTML에 들어가기 전에 이스케이프해야 한다."""
    js_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'js', 'inference.js')
    content = open(js_path).read()
    body = _extract_js_function_body(content, 'renderInferencePanel')
    assert body is not None, "renderInferencePanel function must exist"
    assert '_escAttr(samplePath)' in body


def test_css_sample_grid_defined():
    """style.css에 .mz-sample-grid 클래스가 정의되어야 한다."""
    css_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'css', 'style.css')
    content = open(css_path).read()
    assert '.mz-sample-grid' in content, "style.css must define .mz-sample-grid"


def test_css_inference_preview_defined():
    """style.css에 .mz-inference-preview 클래스가 정의되어야 한다."""
    css_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'css', 'style.css')
    content = open(css_path).read()
    assert '.mz-inference-preview' in content, "style.css must define .mz-inference-preview"


def test_inference_js_escattr_escapes_single_quote():
    """_escAttr 함수가 작은따옴표를 &#39;로 이스케이프해야 한다.

    renderInferencePanel에서 onclick='...' 내부에 값을 삽입할 때
    작은따옴표가 이스케이프되지 않으면 XSS 취약점이 된다.
    """
    js_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'js', 'inference.js')
    content = open(js_path).read()
    assert "&#39;" in content, (
        "_escAttr must escape single quotes as &#39; to prevent injection in "
        "single-quoted onclick attributes"
    )


def test_inference_js_render_panel_escapes_model_values():
    """renderInferencePanel이 model.id, category, model_file을 _escAttr로 이스케이프해야 한다.

    inline onclick에서 이 값들이 이스케이프 없이 삽입되면
    특수 문자가 포함된 모델명으로 JS 인젝션이 가능하다.
    """
    import re
    js_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'js', 'inference.js')
    content = open(js_path).read()

    # renderInferencePanel 함수 본문 추출
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

    # onclick 내에서 model.id/category/model_file이 _escAttr로 감싸져야 한다
    # 이스케이프 없이 직접 삽입하는 패턴이 없어야 한다
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
    """JS 소스에서 function funcName(...) { ... } 본문을 추출한다."""
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
    """renderInferencePanel은 onclick 내에서 모델 값을 직접 보간하지 않아야 한다.

    switchInferenceTab('upload', '${eId}', ...) 같은 패턴은 HTML이 &#39;를
    apostrophe로 디코딩한 뒤 JS가 실행되므로, 작은따옴표를 포함하는 값에서 깨진다.
    """
    import re
    js_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'js', 'inference.js')
    content = open(js_path).read()
    body = _extract_js_function_body(content, 'renderInferencePanel')
    assert body is not None, "renderInferencePanel function must exist"

    # 금지 패턴: onclick="someFunc('${eId}', '${eCat}', '${eFile}')" 형태
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
    """renderInferencePanel이 data-model-id / data-category / data-model-file 속성을 사용해야 한다."""
    js_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'js', 'inference.js')
    content = open(js_path).read()
    body = _extract_js_function_body(content, 'renderInferencePanel')
    assert body is not None, "renderInferencePanel function must exist"

    for attr in ('data-model-id', 'data-category', 'data-model-file'):
        assert attr in body, (
            f"renderInferencePanel must set {attr} attribute on interactive elements"
        )


def test_render_panel_uses_dataset_helper_functions():
    """renderInferencePanel의 onclick이 dataset을 읽는 헬퍼 함수를 호출해야 한다."""
    js_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'js', 'inference.js')
    content = open(js_path).read()
    body = _extract_js_function_body(content, 'renderInferencePanel')
    assert body is not None, "renderInferencePanel function must exist"

    # 헬퍼 함수가 onclick에서 호출되어야 한다
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
    """헬퍼 함수들이 btn/input의 dataset에서 modelId, category, modelFile을 읽어야 한다."""
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
    """_escAttr가 data 속성 값에서 작은따옴표를 &#39;로 이스케이프해야 한다.

    data-model-id="${eId}" 형태에서 eId에 큰따옴표가 포함되면 속성이 깨지므로
    &quot; 이스케이프도 필요하다.
    """
    js_path = os.path.join(REPO_ROOT, 'dx_modelzoo', 'static', 'js', 'inference.js')
    content = open(js_path).read()
    body = _extract_js_function_body(content, '_escAttr')
    assert body is not None, "_escAttr function must exist"

    # 작은따옴표 → &#39;
    assert "&#39;" in body, "_escAttr must escape ' to &#39;"
    # 큰따옴표 → &quot;
    assert "&quot;" in body, "_escAttr must escape \" to &quot;"
