"""POST /api/model_card/<id> returns the card as an attachment in the requested language."""
import base64
import json
import re
import sys
import threading
import time
from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest
from PIL import Image

from dx_modelzoo.core.model_card_studio import DxAppMissing, NoDxAppExample, studio_card
from tests.installed_sdk import require, require_dx_app

MODULE_DIR = Path(__file__).resolve().parents[2] / "dx_modelzoo"
def test_studio_card_without_a_dx_app_checkout(tmp_path):
    model = {"id": "x", "demo": {"python_example": "src/python_example/a/b/x/"}}
    with pytest.raises(DxAppMissing):
        studio_card(model, {}, {}, dx_app_root=tmp_path, data_dir=tmp_path, benchmark_path=tmp_path / "none.json",
                    asof=None)


def test_studio_card_without_a_dx_app_example(tmp_path):
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "model_registry.json").write_text(
        json.dumps([{"dxnn_file": "other.dxnn", "model_name": "other"}]), encoding="utf-8")
    model = {"id": "x", "demo": {"python_example": "src/python_example/a/b/x/"}}
    with pytest.raises(NoDxAppExample):
        studio_card(model, {}, {}, dx_app_root=tmp_path, data_dir=tmp_path, benchmark_path=tmp_path / "none.json",
                    asof=None)


def test_studio_card_leaves_off_the_links_the_last_link_check_found_dead(monkeypatch, tmp_path):
    from dx_modelzoo.core import model_card
    from tests.dx_modelzoo.test_export_dx_app_cards import _tree

    app, data, model = _tree(tmp_path)
    dead_url = "https://sdk.deepx.ai/modelzoo/q-pro-dxnn/2_4_0/yolov5-m-face_640x640.dxnn"
    store = tmp_path / "dead_download_links.json"
    model_card.save_dead_links([dead_url], "2026-10-13", store)
    monkeypatch.setattr(model_card, "DEAD_LINKS_PATH", store)
    html, _ = studio_card(model, {}, {"lang": "ko"}, dx_app_root=app, data_dir=data,
                          benchmark_path=tmp_path / "none.json", asof="2026-10-13")
    assert dead_url not in html and "q-lite-dxnn/2_5_0/yolov5-m-face_640x640.dxnn" in html


_SERVER_GLOBALS = {}


@pytest.fixture(scope="module")
def port():
    require_dx_app("config/model_registry.json")
    sys.modules.pop("server", None)
    sys.path.insert(0, str(MODULE_DIR))
    try:
        from server import create_server
    finally:
        sys.path.remove(str(MODULE_DIR))
    _SERVER_GLOBALS.update(globals=create_server.__globals__)     # the module the handler reads DX_APP_ROOT from
    srv = create_server(0)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    for _ in range(25):
        try:
            urlopen(f"http://127.0.0.1:{port}/api/categories", timeout=1)
            break
        except Exception:
            time.sleep(0.2)
    try:   # the cards below are of yolo26n, which a dx_app before the per-model layout has no example for
        _post(port, "/api/model_card/yolo26n", {})
    except HTTPError as exc:
        missing = exc.code == 404 and "No dx_app example" in exc.read().decode("utf-8", "replace")
        if missing:
            srv.shutdown()
            srv.server_close()
        require(not missing, "the installed dx_app has no yolo26n example (a dx_app before the per-model layout)")
    yield port
    srv.shutdown()
    srv.server_close()
    sys.modules.pop("server", None)


def _post(port, path, body):
    req = Request(f"http://127.0.0.1:{port}{path}", data=json.dumps(body).encode(), method="POST",
                  headers={"Content-Type": "application/json", "Origin": f"http://127.0.0.1:{port}"})
    return urlopen(req, timeout=30)


def test_label_keys(port):
    keys = json.loads(urlopen(f"http://127.0.0.1:{port}/api/model_card/labels").read())["keys"]
    assert "Quick start" in keys and "Download {tier} DXNN" in keys


def test_card_in_korean(port):
    resp = _post(port, "/api/model_card/yolo26n",
                 {"lang": "ko", "labels": {"Quick start": "빠른 시작"}, "task_label": "객체 탐지"})
    page = resp.read().decode()
    assert "attachment" in resp.headers.get("Content-Disposition", "")
    assert '<html lang="ko">' in page and "빠른 시작" in page and "객체 탐지" in page
    assert 'src="data:image/webp;base64,' in page and 'href="README.md"' not in page


@pytest.mark.parametrize("extension", ["webp", "jpg"])
def test_card_embeds_an_optimized_result_without_the_original(port, tmp_path, monkeypatch, extension):
    image_path = tmp_path / "optimized/examples" / f"yolo26n_result-jpg.{extension}"
    image_path.parent.mkdir(parents=True)
    Image.new("RGB", (32, 24), "red").save(image_path)
    monkeypatch.setitem(_SERVER_GLOBALS["globals"], "DATA_DIR", tmp_path)
    page = _post(port, "/api/model_card/yolo26n",
                 {"lang": "ko", "labels": {"Quick start": "빠른 시작"}}).read().decode()
    assert '<html lang="ko">' in page and "빠른 시작" in page
    embedded = re.search(r'src="data:image/webp;base64,([^"]+)"', page)
    assert embedded is not None, "optimized-only release assets must be embedded in the HTML card"
    with Image.open(BytesIO(base64.b64decode(embedded.group(1)))) as image:
        assert image.format == "WEBP" and image.size == (32, 24)


def test_get_command_uses_the_setup_name(port):
    # setup_sample_models.sh --models knows this model by its manifest name, not the registry's lower-case name.
    page = _post(port, "/api/model_card/damoyolo_tinynasl20_t", {}).read().decode()
    assert "./setup_sample_models.sh --models DamoYolo_tinynasL20_T" in page


def test_missing_dx_app_is_503(port, tmp_path, monkeypatch):
    monkeypatch.setitem(_SERVER_GLOBALS["globals"], "DX_APP_ROOT", tmp_path)
    with pytest.raises(HTTPError) as gone:
        _post(port, "/api/model_card/yolo26n", {})
    assert gone.value.code == 503
    assert json.loads(gone.value.read()) == {"ok": False, "error": "The dx_app checkout is missing",
                                             "code": "DX_APP_MISSING"}


def test_bad_requests(port):
    with pytest.raises(HTTPError) as bad:
        _post(port, "/api/model_card/..%2Fx", {})
    assert bad.value.code == 400
    with pytest.raises(HTTPError) as missing:
        _post(port, "/api/model_card/no_such_model", {})
    assert missing.value.code == 404
    with pytest.raises(HTTPError) as broken:
        urlopen(Request(f"http://127.0.0.1:{port}/api/model_card/yolo26n", data=b"{not json", method="POST",
                        headers={"Content-Type": "application/json"}), timeout=30)
    assert broken.value.code == 400


def test_no_dx_app_example_is_404(port, monkeypatch):
    # Every catalog model has a dx_app example today, so the registry is emptied for this request.
    monkeypatch.setattr("dx_modelzoo.core.model_card_studio.load_registry", lambda root: {})
    with pytest.raises(HTTPError) as missing:
        _post(port, "/api/model_card/yolo26n", {})
    assert missing.value.code == 404
    assert json.loads(missing.value.read())["error"] == "No dx_app example for this model"


def test_other_errors_are_500(port, monkeypatch):
    # A registry row without dxnn_file is a KeyError (a LookupError): a server fault, not "no example".
    class EmptyRows(dict):
        def get(self, key, default=None):
            return {}

    monkeypatch.setattr("dx_modelzoo.core.model_card_studio.load_registry", lambda root: EmptyRows())
    with pytest.raises(HTTPError) as fault:
        _post(port, "/api/model_card/yolo26n", {})
    assert fault.value.code == 500


def test_unsupported_lang_falls_back_to_english(port):
    page = _post(port, "/api/model_card/yolo26n", {"lang": "xx-evil\"><script>"}).read().decode()
    assert '<html lang="en">' in page and "xx-evil" not in page


@pytest.mark.parametrize("task_label", ["T" * 81, 42, ["Detection"], ""])
def test_bad_task_label_falls_back_to_the_category(port, task_label):
    page = _post(port, "/api/model_card/yolo26n", {"task_label": task_label}).read().decode()
    assert "Object Detection" in page and "T" * 81 not in page and ">42<" not in page


def test_card_has_no_cpp_or_readme_link(port):
    page = _post(port, "/api/model_card/yolo26n", {}).read().decode()
    assert "C++ version of this example" not in page and ">README<" not in page and 'href="README.md"' not in page


def test_cross_origin_post_is_refused(port):
    req = Request(f"http://127.0.0.1:{port}/api/model_card/yolo26n", data=b"{}", method="POST",
                  headers={"Content-Type": "application/json", "Origin": "http://evil.example"})
    with pytest.raises(HTTPError) as refused:
        urlopen(req, timeout=30)
    assert refused.value.code == 403
