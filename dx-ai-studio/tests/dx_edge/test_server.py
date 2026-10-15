"""DX Cloud server — the page, and the HTTP layer of the cloud compile API.

AWS itself is replaced: the core functions are monkeypatched (their AWS behaviour is covered with
botocore Stubber in test_aws_compile.py), so these tests pin routing, validation hand-off and the
response shapes only.
"""
from __future__ import annotations

import json
import sys
import threading
import uuid
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from dx_edge.core import aws_compile as ac


@pytest.fixture()
def base():
    from dx_edge.server import create_server

    srv = create_server(port=0)
    t = threading.Thread(target=srv.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
    t.start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()
    srv.server_close()
    t.join(timeout=2)


def _get(url):
    try:
        with urlopen(url, timeout=5) as r:
            return r.status, r.headers, r.read()
    except HTTPError as e:
        return e.code, e.headers, e.read()


def _post(url, body: bytes, ctype: str, headers=None):
    req = Request(url, data=body, method="POST", headers={"Content-Type": ctype, **(headers or {})})
    try:
        with urlopen(req, timeout=5) as r:
            return r.status, r.read()
    except HTTPError as e:
        return e.code, e.read()


def _multipart(fields: dict, files: dict) -> tuple[bytes, str]:
    boundary = uuid.uuid4().hex
    out = []
    for k, v in fields.items():
        out.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    for k, (name, data) in files.items():
        out.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"; filename="{name}"\r\n'
            f"Content-Type: application/octet-stream\r\n\r\n".encode() + data + b"\r\n")
    out.append(f"--{boundary}--\r\n".encode())
    return b"".join(out), f"multipart/form-data; boundary={boundary}"


def test_page_has_the_marketplace_cards_and_the_compile_panel(base):
    code, _, body = _get(base + "/")
    html = body.decode()
    assert code == 200
    assert "prodview-ev6ed5omu4ulo" in html  # DEEPX Compiler Solution
    assert "prodview-732s46qfzuh34" in html  # DEEPX Greengrass Solution
    assert 'id="cloudCompile-compiler"' in html and 'id="cloudCompile-greengrass"' in html
    assert "{{DX_SHELL_" not in html  # shell slots filled


def test_heartbeat(base):
    code, _, body = _get(base + "/api/hb")
    assert code == 200 and json.loads(body) == {"ok": True}


def test_status_endpoint(base, monkeypatch):
    monkeypatch.setattr(ac, "status", lambda: {"boto3": True, "profiles": ["default"],
                                                "default_region": "ap-northeast-2"})
    code, _, body = _get(base + "/api/aws/status")
    assert code == 200
    assert json.loads(body)["default_region"] == "ap-northeast-2"


def test_missing_boto3_is_a_json_error_with_a_hint(base, monkeypatch):
    monkeypatch.setitem(sys.modules, "boto3", None)
    code, _, body = _get(base + "/api/aws/stacks?region=ap-northeast-2")
    assert code == 503
    assert "pip install" in json.loads(body)["error"]


def test_stacks_passes_profile_and_region(base, monkeypatch):
    seen = {}

    def fake(profile, region):
        seen.update(profile=profile, region=region)
        return [{"name": "s", "bucket": "b", "status": "CREATE_COMPLETE", "state_machine": True}]

    monkeypatch.setattr(ac, "list_stacks", fake)
    code, _, body = _get(base + "/api/aws/stacks?profile=dev&region=us-west-2")
    assert code == 200
    assert json.loads(body)["stacks"][0]["name"] == "s"
    assert seen == {"profile": "dev", "region": "us-west-2"}


def test_compile_hands_the_files_to_the_core_and_ignores_a_client_bucket(base, monkeypatch):
    seen = {}

    def fake(**kw):
        seen.update(kw)
        return {"prefix": "models/m-20261014-093000/", "stack": kw["stack"], "region": kw["region"]}

    monkeypatch.setattr(ac, "start_compile", fake)
    body, ctype = _multipart(
        {"profile": "dev", "region": "ap-northeast-2", "stack": "stk", "bucket": "attacker"},
        {"onnx": ("m.onnx", b"ONNX"), "json": ("m.json", b"{}")},
    )
    code, resp = _post(base + "/api/aws/compile", body, ctype)
    assert code == 200, resp
    assert json.loads(resp)["prefix"] == "models/m-20261014-093000/"
    assert seen["onnx_name"] == "m.onnx" and seen["onnx_data"] == b"ONNX"
    assert seen["json_name"] == "m.json" and seen["json_data"] == b"{}"
    assert "bucket" not in seen


def test_compile_without_files_is_400(base):
    body, ctype = _multipart({"region": "ap-northeast-2", "stack": "stk"}, {})
    code, _ = _post(base + "/api/aws/compile", body, ctype)
    assert code == 400


def test_compile_cross_origin_is_refused(base, monkeypatch):
    monkeypatch.setattr(ac, "start_compile", lambda **kw: pytest.fail("must not run"))
    body, ctype = _multipart({"stack": "stk"}, {"onnx": ("m.onnx", b"x"), "json": ("m.json", b"{}")})
    code, _ = _post(base + "/api/aws/compile", body, ctype, {"Origin": "http://evil.example"})
    assert code == 403


def test_compile_status_maps_aws_errors_to_json(base):
    code, _, body = _get(base + "/api/aws/compile/status?region=ap-northeast-2&stack=s&prefix=models/../x/")
    assert code == 400
    assert "error" in json.loads(body)


def test_download_streams_the_dxnn_as_an_attachment(base, monkeypatch):
    import io
    from botocore.response import StreamingBody

    monkeypatch.setattr(ac, "open_dxnn",
                        lambda p, r, s, x: ("m.dxnn", 4, StreamingBody(io.BytesIO(b"DXNN"), 4)))
    code, headers, body = _get(base + "/api/aws/compile/download?region=ap-northeast-2&stack=s"
                                      "&prefix=models/m-20261014-093000/")
    assert code == 200 and body == b"DXNN"
    assert 'filename="m.dxnn"' in headers["Content-Disposition"]


def test_save_uses_the_studio_models_dir(base, monkeypatch, tmp_path):
    import dx_app.core.config as app_config

    monkeypatch.setattr(app_config, "MODELS_DIR", tmp_path)
    seen = {}

    def fake(profile, region, stack, prefix, models_dir):
        seen["dir"] = models_dir
        return models_dir / "m.dxnn"

    monkeypatch.setattr(ac, "save_dxnn", fake)
    payload = json.dumps({"profile": "", "region": "ap-northeast-2", "stack": "s",
                          "prefix": "models/m-20261014-093000/"}).encode()
    code, resp = _post(base + "/api/aws/compile/save", payload, "application/json")
    assert code == 200, resp
    assert seen["dir"] == tmp_path
    assert json.loads(resp)["path"] == str(tmp_path / "m.dxnn")


def test_launcher_serves_dx_cloud_under_cloud_path():
    """The module is shown as DX Cloud, so every place that routes to it says /cloud/."""
    from shared.auth_policy import map_launcher_proxy
    from shared.shell import MODULES

    assert map_launcher_proxy("/cloud/api/aws/status") == ("dx_edge", "/api/aws/status")
    assert map_launcher_proxy("/edge/") is None
    assert next(m for m in MODULES if m.name == "DX Cloud").path == "/cloud/"
    root = Path(__file__).resolve().parents[2]
    launcher = (root / "launcher/launcher.py").read_text(encoding="utf-8")
    assert '"dx_edge": "/cloud/"' in launcher
    assert '("/cloud", "dx_edge", False)' in launcher
    assert "edge: '/cloud/'" in (root / "launcher/static/launcher-state.js").read_text(encoding="utf-8")


# ── stack setup (subscription, create, progress, delete) ───────────────────

def test_subscription_endpoint(base, monkeypatch):
    from dx_edge.core import aws_stack as st

    monkeypatch.setattr(st, "subscription", lambda p, r: [{"id": "compiler", "subscribed": True}])
    code, _, body = _get(base + "/api/aws/subscription?profile=dev&region=ap-northeast-2")
    assert code == 200
    assert json.loads(body)["templates"][0]["subscribed"] is True


def test_create_stack_hands_the_body_to_the_core(base, monkeypatch):
    from dx_edge.core import aws_stack as st

    seen = {}

    def fake(profile, region, template, name):
        seen.update(profile=profile, region=region, template=template, name=name)
        return {"name": name, "bucket": "b", "template": template}

    monkeypatch.setattr(st, "create_stack", fake)
    payload = json.dumps({"profile": "dev", "region": "ap-northeast-2", "template": "compiler",
                          "name": "dx-cloud-1", "bucket": "attacker"}).encode()
    code, resp = _post(base + "/api/aws/stacks", payload, "application/json")
    assert code == 200, resp
    assert seen == {"profile": "dev", "region": "ap-northeast-2", "template": "compiler", "name": "dx-cloud-1"}


def test_stack_progress_endpoint(base, monkeypatch):
    from dx_edge.core import aws_stack as st

    monkeypatch.setattr(st, "stack_progress",
                        lambda p, r, n: {"name": n, "status": "CREATE_IN_PROGRESS", "events": []})
    code, _, body = _get(base + "/api/aws/stacks/progress?region=ap-northeast-2&name=dx-cloud-1")
    assert code == 200
    assert json.loads(body)["name"] == "dx-cloud-1"


def test_delete_stack_passes_the_typed_confirmation(base, monkeypatch):
    from dx_edge.core import aws_stack as st

    seen = {}

    def fake(profile, region, name, confirm):
        seen.update(name=name, confirm=confirm)
        raise ac.AwsError(400, "Type the stack name to confirm")

    monkeypatch.setattr(st, "delete_stack", fake)
    payload = json.dumps({"region": "ap-northeast-2", "name": "s", "confirm": "x"}).encode()
    code, resp = _post(base + "/api/aws/stacks/delete", payload, "application/json")
    assert code == 400
    assert "confirm" in json.loads(resp)["error"]
    assert seen == {"name": "s", "confirm": "x"}


@pytest.mark.parametrize("path,fn", [("/api/aws/stacks", "create_stack"),
                                     ("/api/aws/stacks/delete", "delete_stack")])
def test_stack_posts_cross_origin_are_refused(base, monkeypatch, path, fn):
    from dx_edge.core import aws_stack as st

    monkeypatch.setattr(st, fn, lambda *a: pytest.fail("must not run"))
    payload = json.dumps({"region": "ap-northeast-2", "name": "s", "confirm": "s",
                          "template": "compiler"}).encode()
    code, _ = _post(base + path, payload, "application/json", {"Origin": "http://evil.example"})
    assert code == 403


# ── Greengrass tab ──────────────────────────────────────────────────────────

def test_greengrass_devices_endpoint(base, monkeypatch):
    from dx_edge.core import aws_greengrass as gg

    seen = {}

    def fake(profile, region, stack):
        seen.update(profile=profile, region=region, stack=stack)
        return {"thing_group": "g", "deployment": None, "devices": []}

    monkeypatch.setattr(gg, "devices", fake)
    code, _, body = _get(base + "/api/aws/greengrass/devices?profile=dev&region=ap-northeast-2&stack=gg1")
    assert code == 200
    assert json.loads(body)["thing_group"] == "g"
    assert seen == {"profile": "dev", "region": "ap-northeast-2", "stack": "gg1"}


def test_greengrass_components_endpoint(base, monkeypatch):
    from dx_edge.core import aws_greengrass as gg

    monkeypatch.setattr(gg, "components", lambda p, r, d: [{"name": d, "version": "1", "state": "RUNNING"}])
    code, _, body = _get(base + "/api/aws/greengrass/components?region=ap-northeast-2&device=dev-a")
    assert code == 200
    assert json.loads(body)["components"][0]["name"] == "dev-a"


def test_greengrass_components_validation_is_a_json_400(base):
    code, _, body = _get(base + "/api/aws/greengrass/components?region=ap-northeast-2&device=a%20b")
    assert code == 400
    assert "error" in json.loads(body)


def test_greengrass_install_script_endpoint(base, monkeypatch):
    from dx_edge.core import aws_greengrass as gg

    seen = {}

    def fake(profile, region, stack, thing):
        seen.update(profile=profile, region=region, stack=stack, thing=thing)
        return {"script": "#!/usr/bin/env bash\n", "thing": thing, "thing_group": "g"}

    monkeypatch.setattr(gg, "install_script", fake)
    payload = json.dumps({"profile": "dev", "region": "ap-northeast-2", "stack": "gg1",
                          "thing": "dev-a"}).encode()
    code, resp = _post(base + "/api/aws/greengrass/install-script", payload, "application/json")
    assert code == 200, resp
    assert json.loads(resp)["thing"] == "dev-a"
    assert seen == {"profile": "dev", "region": "ap-northeast-2", "stack": "gg1", "thing": "dev-a"}


def test_greengrass_install_script_cross_origin_is_refused(base, monkeypatch):
    from dx_edge.core import aws_greengrass as gg

    monkeypatch.setattr(gg, "install_script", lambda *a: pytest.fail("must not run"))
    payload = json.dumps({"region": "ap-northeast-2", "stack": "gg1", "thing": "dev-a"}).encode()
    code, _ = _post(base + "/api/aws/greengrass/install-script", payload, "application/json",
                    {"Origin": "http://evil.example"})
    assert code == 403
