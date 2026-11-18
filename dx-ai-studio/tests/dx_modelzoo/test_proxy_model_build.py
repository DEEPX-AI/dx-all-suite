"""Model Zoo reaches only the model-build job; clean-build / runtime-reset / generic setup stay out of reach."""
from dx_modelzoo import server


def _target(monkeypatch, path, method="POST"):
    seen, sent = {}, {}

    def fake(m, target, q, body, hdrs):
        seen["t"] = (m, target)
        return 200, [], b"{}"

    h = server.ModelZooHandler.__new__(server.ModelZooHandler)
    h.send_response = h.send_header = h.end_headers = lambda *a, **k: None
    h.wfile = type("W", (), {"write": lambda self, b: None})()
    h.send_json = lambda body, code=200: sent.update(code=code, body=body)
    monkeypatch.setattr(server, "proxy_request", fake)
    h._handle_proxy(method, path, "", b"{}", "application/json")
    return seen.get("t"), sent


def test_model_build_routes(monkeypatch):
    assert _target(monkeypatch, "/api/proxy/model-build")[0] == ("POST", "/api/setup/model-build")
    assert _target(monkeypatch, "/api/proxy/model-build/log", "GET")[0] == ("GET", "/api/setup/model-build/log")
    assert _target(monkeypatch, "/api/proxy/model-build/stop")[0] == ("POST", "/api/setup/model-build/stop")


def test_other_setup_paths_are_refused(monkeypatch):
    for p in ("/api/proxy/setup/run", "/api/proxy/setup/stop", "/api/proxy/clean-build",
              "/api/proxy/model-build/../setup/run", "/api/proxy/model-build/anything"):
        t, sent = _target(monkeypatch, p)
        assert t is None and sent["code"] == 400, p
