"""POST /api/model_card/<id> returns the card as an attachment in the requested language."""
import json
import sys
import threading
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from dx_modelzoo.core.model_card_studio import DxAppMissing, studio_card
from shared.paths import DX_APP_ROOT

MODULE_DIR = Path(__file__).resolve().parents[2] / "dx_modelzoo"
def test_studio_card_without_a_dx_app_checkout(tmp_path):
    model = {"id": "x", "demo": {"python_example": "src/python_example/a/b/x/"}}
    with pytest.raises(DxAppMissing):
        studio_card(model, {}, {}, dx_app_root=tmp_path, data_dir=tmp_path, benchmark_path=tmp_path / "none.json",
                    asof=None)


_SERVER_GLOBALS = {}


@pytest.fixture(scope="module")
def port():
    if not (DX_APP_ROOT / "config" / "model_registry.json").is_file():
        pytest.skip("needs the dx_app checkout")
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


def test_get_command_uses_the_setup_name(port):
    # setup.sh --models knows this model by its manifest name, not the registry's lower-case name.
    page = _post(port, "/api/model_card/damoyolo_tinynasl20_t", {}).read().decode()
    assert "./setup.sh --models DamoYolo_tinynasL20_T" in page


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
