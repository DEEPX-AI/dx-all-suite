"""Live E2E checks against a real dx_com venv (skips when unavailable).

Requires dx_com 2.3.x features only. Excluded (need dx_com >= 2.4):
  - quant_diagnosis HTML report generation
  - QXNN checkpoint resume success path
  - use_q_pro / Auto Q-PRO compile
  - Interactive node-selection pause (needs event_queue in dx_com)
"""

from __future__ import annotations

import importlib.util
import inspect
import json
import re
import socket
import subprocess
import sys
import threading
import time
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

ROOT = Path(__file__).resolve().parents[2]
COMPILER_DIR = ROOT / "dx_compiler"
SDK_ROOT = ROOT.parent / "dx-compiler"
VENV_PY = SDK_ROOT / "venv-dx-compiler-local" / "bin" / "python3"
MODEL = SDK_ROOT / "dx_com" / "sample_models" / "onnx" / "MobileNetV2-1.onnx"
BASE_CONFIG = SDK_ROOT / "dx_com" / "sample_models" / "json" / "MobileNetV2-1.json"
CALIB = SDK_ROOT / "dx_com" / "calibration_dataset"

pytestmark = pytest.mark.e2e


def _free_port() -> int:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def _load_dx_com_info() -> dict | None:
    if not VENV_PY.is_file() or not MODEL.is_file():
        return None
    code = (
        "import inspect, json; from dx_com import compile as c; "
        "sig = inspect.signature(c); "
        "print(json.dumps({'params': list(sig.parameters.keys())}))"
    )
    proc = subprocess.run(
        [str(VENV_PY), "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if proc.returncode != 0:
        return None
    params = set(json.loads(proc.stdout.strip())["params"])
    html_export = subprocess.run(
        [str(VENV_PY), "-c", "import dx_com.html_export"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    return {
        "venv_python": VENV_PY,
        "params": params,
        "supports_quant_diagnosis": "quant_diagnosis" in params,
        "supports_checkpoint": "checkpoint" in params,
        "supports_use_q_pro": "use_q_pro" in params,
        "supports_event_queue": "event_queue" in params,
        "supports_html_export": html_export.returncode == 0,
    }


@pytest.fixture(scope="module")
def dx_com_info():
    info = _load_dx_com_info()
    if info is None:
        pytest.skip("dx_com venv or sample model not available")
    return info


@pytest.fixture(scope="module")
def fast_config(tmp_path_factory):
    out = tmp_path_factory.mktemp("e2e_cfg")
    cfg = json.loads(BASE_CONFIG.read_text(encoding="utf-8"))
    cfg["calibration_num"] = 3
    cfg["default_loader"]["dataset_path"] = str(CALIB)
    path = out / "fast.json"
    path.write_text(json.dumps(cfg), encoding="utf-8")
    return path


@pytest.fixture(scope="module")
def live_server():
    _clear_stale_modules()
    port = _free_port()
    base_url = f"http://127.0.0.1:{port}"

    spec = importlib.util.spec_from_file_location(
        "dx_compiler_e2e_server", COMPILER_DIR / "server.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)

    class ReuseServer(ThreadingHTTPServer):
        allow_reuse_address = True

    srv = ReuseServer(("127.0.0.1", port), module.CompilerHandler)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()

    ready = False
    for _ in range(50):
        try:
            urlopen(f"{base_url}/feature-check", timeout=1)
            ready = True
            break
        except Exception:
            time.sleep(0.1)
    if not ready:
        srv.shutdown()
        srv.server_close()
        pytest.fail("live E2E server did not start")

    yield {"base_url": base_url, "port": port, "module": module}

    srv.shutdown()
    srv.server_close()
    _clear_stale_modules()


def _clear_stale_modules():
    prefixes = ("dx_compiler", "dx_compiler_e2e_server", "core")
    for name in list(sys.modules):
        if any(name == p or name.startswith(p + ".") for p in prefixes):
            del sys.modules[name]
    root_str = str(ROOT)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)


def _get_json(base_url: str, path: str) -> dict:
    with urlopen(base_url + path, timeout=10) as resp:
        return json.loads(resp.read().decode())


def _post_json(base_url: str, path: str, payload: dict) -> tuple[int, dict | str]:
    data = json.dumps(payload).encode()
    req = Request(
        base_url + path,
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urlopen(req, timeout=30) as resp:
            body = resp.read().decode()
            try:
                return resp.status, json.loads(body)
            except json.JSONDecodeError:
                return resp.status, body
    except HTTPError as e:
        body = e.read().decode()
        try:
            return e.code, json.loads(body)
        except json.JSONDecodeError:
            return e.code, body


def _multipart_compile(base_url: str, fields: dict[str, str]) -> str:
    boundary = "----E2ELiveBoundary"
    body = "".join(
        f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'
        for k, v in fields.items()
    ) + f"--{boundary}--\r\n"
    req = Request(
        base_url + "/compile",
        data=body.encode(),
        method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urlopen(req, timeout=30) as resp:
        html = resp.read().decode()
    match = re.search(r'data-job-id="([a-f0-9]+)"', html)
    assert match, "compile response missing job id"
    return match.group(1)


def _wait_sse(base_url: str, job_id: str, timeout: float = 180) -> dict:
    url = base_url + f"/progress/{job_id}"
    req = Request(url, headers={"Accept": "text/event-stream"})
    last: dict = {"status": "running"}
    with urlopen(req, timeout=timeout + 5) as resp:
        buf = ""
        started = time.time()
        while time.time() - started < timeout:
            chunk = resp.read(1024)
            if not chunk:
                break
            buf += chunk.decode("utf-8", "replace")
            while "\n\n" in buf:
                block, buf = buf.split("\n\n", 1)
                for line in block.splitlines():
                    if not line.startswith("data:"):
                        continue
                    payload = json.loads(line[5:].strip())
                    last = payload
                    if payload.get("status") in ("done", "error"):
                        return payload
    return last


def _compile_fields(fast_config: Path, output_dir: Path, **extra: str) -> dict[str, str]:
    fields = {
        "model_path": str(MODEL),
        "config_path": str(fast_config),
        "output_dir": str(output_dir),
        "opt_level": "0",
        "model_server_path": "true",
        "config_server_path": "true",
    }
    fields.update(extra)
    return fields




def test_live_setup_status_and_samples(live_server, dx_com_info):
    base = live_server["base_url"]
    status = _get_json(base, "/setup/status")
    assert status.get("dx_com_installed") is True
    assert status.get("venv_python")

    samples = _get_json(base, "/setup/sample-models")
    assert isinstance(samples, list) and samples
    mobilenet = next((s for s in samples if s.get("name") == "MobileNetV2-1"), None)
    assert mobilenet and mobilenet.get("downloaded") is True


def test_live_feature_check(live_server):
    data = _get_json(live_server["base_url"], "/feature-check")
    assert data.get("compile") is True
    assert "capabilities" in data


def test_live_model_inspect(live_server):
    path = f"/model/inspect?path={MODEL}"
    data = _get_json(live_server["base_url"], path)
    assert "inputs" in data
    assert "input.1" in data["inputs"]


def test_live_viewer_parse(live_server):
    code, data = _post_json(live_server["base_url"], "/viewer/parse", {"path": str(MODEL)})
    assert code == 200
    assert isinstance(data, dict)
    assert data.get("nodes")
    assert data.get("edges") is not None


def test_live_config_generate(live_server):
    payload = {
        "input_shapes": {"input.1": [1, 3, 224, 224]},
        "calibration_num": 3,
        "calibration_method": "ema",
        "loader_mode": "default",
        "dataset_path": str(CALIB),
        "file_extensions": ["jpeg", "jpg", "png"],
    }
    code, data = _post_json(live_server["base_url"], "/config/generate", payload)
    assert code == 200
    assert data.get("path")
    assert Path(data["path"]).is_file()




def test_live_compile_produces_dxnn(live_server, fast_config, tmp_path):
    out = tmp_path / "compile_basic"
    out.mkdir()
    job_id = _multipart_compile(
        live_server["base_url"],
        _compile_fields(fast_config, out),
    )
    result = _wait_sse(live_server["base_url"], job_id)
    assert result.get("status") == "done", result.get("error")
    assert list(out.rglob("*.dxnn"))


def test_live_compile_with_gen_log(live_server, fast_config, tmp_path):
    out = tmp_path / "compile_log"
    out.mkdir()
    job_id = _multipart_compile(
        live_server["base_url"],
        _compile_fields(fast_config, out, gen_log="true"),
    )
    result = _wait_sse(live_server["base_url"], job_id)
    assert result.get("status") == "done", result.get("error")


def test_live_compile_with_enhanced_scheme(live_server, fast_config, tmp_path, dx_com_info):
    if "enhanced_scheme" not in dx_com_info["params"]:
        pytest.skip("enhanced_scheme not supported")
    out = tmp_path / "compile_dxq"
    out.mkdir()
    scheme = json.dumps({"DXQ-P0": {"alpha": 0.5}})
    job_id = _multipart_compile(
        live_server["base_url"],
        _compile_fields(fast_config, out, enhanced_scheme=scheme),
    )
    result = _wait_sse(live_server["base_url"], job_id)
    assert result.get("status") == "done", result.get("error")


def test_live_compile_node_selection_still_completes(live_server, fast_config, tmp_path):
    """Subprocess mode disables interactive pause but compile must still finish."""
    out = tmp_path / "compile_ns"
    out.mkdir()
    job_id = _multipart_compile(
        live_server["base_url"],
        _compile_fields(fast_config, out, node_selection="true"),
    )
    result = _wait_sse(live_server["base_url"], job_id)
    assert result.get("status") == "done", result.get("error")
    warnings = result.get("warnings") or []
    assert any(w.get("key") == "node_selection_unsupported_subprocess" for w in warnings)


def test_live_summary_after_compile(live_server, fast_config, tmp_path, dx_com_info):
    if not dx_com_info.get("supports_html_export"):
        pytest.skip("dx_com.html_export not available on installed dx_com")
    out = tmp_path / "compile_summary"
    out.mkdir()
    job_id = _multipart_compile(
        live_server["base_url"],
        _compile_fields(fast_config, out),
    )
    result = _wait_sse(live_server["base_url"], job_id)
    assert result.get("status") == "done"

    req = Request(
        live_server["base_url"] + f"/compile/{job_id}/summary",
        data=b"{}",
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urlopen(req, timeout=30) as resp:
        html = resp.read().decode()
    assert resp.status == 200
    assert "MobileNetV2" in html or "summary" in html.lower()




def test_live_summary_unavailable_returns_clear_error(live_server, fast_config, tmp_path, dx_com_info):
    if dx_com_info.get("supports_html_export"):
        pytest.skip("html_export available — covered by test_live_summary_after_compile")
    out = tmp_path / "compile_summary_skip"
    out.mkdir()
    job_id = _multipart_compile(
        live_server["base_url"],
        _compile_fields(fast_config, out),
    )
    result = _wait_sse(live_server["base_url"], job_id)
    assert result.get("status") == "done"

    req = Request(
        live_server["base_url"] + f"/compile/{job_id}/summary",
        data=b"{}",
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with pytest.raises(HTTPError) as exc:
        urlopen(req, timeout=30)
    assert exc.value.code == 500
    body = exc.value.read().decode()
    assert "html_export" in body.lower() or "summary" in body.lower()

    if dx_com_info["supports_quant_diagnosis"]:
        pytest.skip("quant_diagnosis supported — success path needs separate 2.4+ run")
    out = tmp_path / "compile_qd"
    out.mkdir()
    job_id = _multipart_compile(
        live_server["base_url"],
        _compile_fields(fast_config, out, quant_diagnosis="true"),
    )
    result = _wait_sse(live_server["base_url"], job_id, timeout=60)
    assert result.get("status") == "error"
    assert "quant_diagnosis" in (result.get("error") or "").lower()


def test_live_use_q_pro_rejected_without_support(live_server, fast_config, tmp_path, dx_com_info):
    if dx_com_info["supports_use_q_pro"]:
        pytest.skip("use_q_pro supported on this dx_com")
    out = tmp_path / "compile_qpro"
    out.mkdir()
    job_id = _multipart_compile(
        live_server["base_url"],
        _compile_fields(fast_config, out, use_q_pro="true"),
    )
    result = _wait_sse(live_server["base_url"], job_id, timeout=60)
    assert result.get("status") == "error"
    assert "use_q_pro" in (result.get("error") or "").lower()


def test_live_qxnn_resume_validation_errors(live_server, tmp_path):
    base = live_server["base_url"]
    code, body = _post_json(base, "/compile/resume", {"qxnn_path": "/tmp/x", "output_dir": str(tmp_path)})
    assert code == 400

    code, body = _post_json(base, "/compile/resume", {"qxnn_path": "/tmp/x.qxnn", "output_dir": ""})
    assert code == 400


def test_live_qxnn_resume_fails_without_checkpoint_support(live_server, tmp_path, dx_com_info):
    if dx_com_info["supports_checkpoint"]:
        pytest.skip("checkpoint supported — success path needs 2.4+ run")
    out = tmp_path / "resume_out"
    out.mkdir()
    code, body = _post_json(
        live_server["base_url"],
        "/compile/resume",
        {"qxnn_path": "/tmp/nonexistent.qxnn", "output_dir": str(out)},
    )
    assert code == 200
    assert isinstance(body, str)
    job_id = re.search(r'data-job-id="([a-f0-9]+)"', body)
    assert job_id
    result = _wait_sse(live_server["base_url"], job_id.group(1), timeout=60)
    assert result.get("status") == "error"
    err = (result.get("error") or "").lower()
    assert "checkpoint" in err or "nonexistent" in err or "resume failed" in err


def test_live_resume_summary_returns_clear_400(live_server, fast_config, tmp_path, dx_com_info):
    """A completed QXNN-resume job carries a .qxnn (not ONNX) as model_path, so
    /summary must return a clear 400 — not a 500 from the ONNX parser choking on
    the .qxnn (regression guard for the resume-summary 500)."""
    if not dx_com_info.get("supports_checkpoint") or not dx_com_info.get("supports_quant_diagnosis"):
        pytest.skip("needs dx_com 2.4+ (checkpoint + quant_diagnosis) to produce and resume a .qxnn")
    # 1) produce a .qxnn via a quant_diagnosis compile
    qd_out = tmp_path / "qd"
    qd_out.mkdir()
    job_id = _multipart_compile(
        live_server["base_url"],
        _compile_fields(fast_config, qd_out, quant_diagnosis="true"),
    )
    assert _wait_sse(live_server["base_url"], job_id, timeout=180).get("status") == "done"
    qxnn = next(iter(qd_out.rglob("*.qxnn")), None)
    assert qxnn is not None, "quant_diagnosis compile should emit a .qxnn"
    # 2) resume from that .qxnn
    resume_out = tmp_path / "resume"
    resume_out.mkdir()
    code, body = _post_json(
        live_server["base_url"],
        "/compile/resume",
        {"qxnn_path": str(qxnn), "output_dir": str(resume_out)},
    )
    assert code == 200
    m = re.search(r'data-job-id="([a-f0-9]+)"', body)
    assert m
    resume_job = m.group(1)
    assert _wait_sse(live_server["base_url"], resume_job, timeout=180).get("status") == "done"
    # 3) /summary on the resume job → clean 400 with a clear message, never a 500
    req = Request(
        live_server["base_url"] + f"/compile/{resume_job}/summary",
        data=b"{}",
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with pytest.raises(HTTPError) as exc:
        urlopen(req, timeout=30)
    assert exc.value.code == 400
    assert "resume" in exc.value.read().decode().lower()


def test_live_quant_diagnosis_report_404(live_server, fast_config, tmp_path):
    out = tmp_path / "compile_report404"
    out.mkdir()
    job_id = _multipart_compile(
        live_server["base_url"],
        _compile_fields(fast_config, out),
    )
    _wait_sse(live_server["base_url"], job_id)
    with pytest.raises(HTTPError) as exc:
        urlopen(live_server["base_url"] + f"/compile/{job_id}/quant-diagnosis/report", timeout=10)
    assert exc.value.code == 404


def test_live_bridge_filters_event_queue(dx_com_info):
    """compile_worker path must not pass unsupported GUI-only kwargs to dx_com."""
    if dx_com_info["supports_event_queue"]:
        pytest.skip("event_queue natively supported")
    env = {"PYTHONPATH": str(ROOT)}
    code = (
        "from dx_compiler.core.compiler_bridge import run_compile\n"
        "run_compile(model='m.onnx', config='c.json', output_dir='/tmp/out', event_queue=object())\n"
        "print('ok')"
    )
    proc = subprocess.run(
        [str(dx_com_info["venv_python"]), "-c", code],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    # Should not raise TypeError for event_queue; may fail later on missing files — that's fine.
    assert "unexpected keyword argument 'event_queue'" not in (proc.stderr + proc.stdout)
