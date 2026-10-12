"""DX Model Zoo — HTTP proxy to dx_app (8080)."""
import re
import json
import http.client
import socket
from dx_modelzoo.core.config import DX_APP_PORT, dx_app_port

_SAFE_ID_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._\-]{0,127}$")


def is_safe_model_id(model_id):
    """Validate a model id (guards against path traversal / injection)."""
    if not model_id or ".." in model_id:
        return False
    return bool(_SAFE_ID_RE.match(model_id))


def is_dx_app_alive(port=None, timeout=1):
    """Whether dx_app accepts TCP connections."""
    port = port or dx_app_port()
    try:
        sock = socket.create_connection(("127.0.0.1", port), timeout=timeout)
        sock.close()
        return True
    except (ConnectionRefusedError, OSError, socket.timeout):
        return False


def _json_error_response(status, code, detail):
    body = json.dumps({"error": code, "detail": str(detail)}).encode()
    return status, [
        ("Content-Type", "application/json"),
        ("Content-Length", str(len(body))),
        ("Connection", "close"),
    ], body


def proxy_request(method, path, query=None, body=None, headers=None, port=None):
    """Proxy an HTTP request to dx_app (8080).

    Returns:
        (status_code, response_headers, response_body)
    """
    port = port or dx_app_port()
    url = path
    if query:
        url = f"{path}?{query}"
    try:
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=30)
        req_headers = headers or {}
        conn.request(method, url, body=body, headers=req_headers)
        resp = conn.getresponse()
        resp_body = resp.read()
        resp_headers = resp.getheaders()
        status = resp.status
        conn.close()
        return status, resp_headers, resp_body
    except (socket.timeout, TimeoutError) as e:
        return _json_error_response(504, "DX_APP_TIMEOUT", e)
    except (ConnectionRefusedError, OSError) as e:
        return _json_error_response(502, "DX_APP_UNAVAILABLE", e)
    except Exception as e:
        return _json_error_response(500, "PROXY_FAILED", e)
