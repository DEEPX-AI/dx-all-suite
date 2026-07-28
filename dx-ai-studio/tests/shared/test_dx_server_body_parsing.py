import io
import json
from http.client import HTTPMessage
from unittest import mock

import pytest

from shared.dx_server import DXBaseHandler, DXServer, RequestBodyError


class _BodyHandler(DXBaseHandler):
    server_name = "BodyTest"
    log_silent = True

    def route(self):
        data = self.read_json_body()
        self.send_json({"ok": True, "data": data})


def _handler(method="POST", headers=None, body=b"{}"):
    h = _BodyHandler.__new__(_BodyHandler)
    h.command = method
    h.path = "/api/test"
    h.rfile = io.BytesIO(body)
    h.wfile = io.BytesIO()
    h._headers_buffer = []
    msg = HTTPMessage()
    msg["Host"] = "localhost"
    msg["Content-Length"] = str(len(body))
    if headers:
        for key, value in headers.items():
            if value is None:
                continue
            msg.replace_header(key, value) if key in msg else msg.__setitem__(key, value)
    h.headers = msg
    h.send_response = mock.Mock()
    h.send_header = mock.Mock()
    h.end_headers = mock.Mock()
    return h


def _response_code(handler):
    return handler.send_response.call_args[0][0]


def _response_body(handler):
    return json.loads(handler.wfile.getvalue())


def test_read_json_body_malformed_json_raises_controlled_400():
    h = _handler(body=b"{not-json")

    with pytest.raises(RequestBodyError) as exc:
        h.read_json_body()

    assert exc.value.status_code == 400
    assert "Invalid JSON" in exc.value.message


@pytest.mark.parametrize("content_length", ["abc", "", "-5", "3.14", "None"])
def test_read_json_body_invalid_content_length_raises_controlled_400(content_length):
    h = _handler(headers={"Content-Length": content_length}, body=b"")

    with pytest.raises(RequestBodyError) as exc:
        h.read_json_body()

    assert exc.value.status_code == 400
    assert "Content-Length" in exc.value.message


def test_read_json_body_too_large_rejected_before_body_read():
    class NoRead:
        def read(self, _size):
            raise AssertionError("body must not be read after size rejection")

    h = _handler(headers={"Content-Length": "100"}, body=b"")
    h.rfile = NoRead()
    h.json_max_bytes = 10

    with pytest.raises(RequestBodyError) as exc:
        h.read_json_body()

    assert exc.value.status_code == 413


def test_dispatch_converts_body_parse_error_to_json_response():
    h = _handler(body=b"{not-json")

    h.do_POST()

    assert _response_code(h) == 400
    assert "Invalid JSON" in _response_body(h)["error"]


def test_dispatch_converts_unexpected_handler_error_to_500():
    """An unhandled handler exception must become a 500 response, never a dropped
    connection (which the launcher/proxy would surface as an opaque 502)."""

    class _BoomHandler(DXBaseHandler):
        server_name = "BoomTest"
        log_silent = True

        def route(self):
            raise RuntimeError("boom")

    h = _BoomHandler.__new__(_BoomHandler)
    h.command = "POST"
    h.path = "/api/test"
    h.rfile = io.BytesIO(b"{}")
    h.wfile = io.BytesIO()
    h._headers_buffer = []
    msg = HTTPMessage()
    msg["Host"] = "localhost"
    msg["Content-Length"] = "2"
    h.headers = msg
    h.send_response = mock.Mock()
    h.send_header = mock.Mock()
    h.end_headers = mock.Mock()

    h.do_POST()

    assert _response_code(h) == 500


def test_parse_multipart_too_large_rejected_before_body_read():
    class NoRead:
        def read(self, _size):
            raise AssertionError("multipart body must not be read after size rejection")

    h = _handler(
        headers={
            "Content-Type": "multipart/form-data; boundary=BOUNDARY",
            "Content-Length": "100",
        },
        body=b"",
    )
    h.rfile = NoRead()
    h.upload_max_bytes = 10

    with pytest.raises(RequestBodyError) as exc:
        h.parse_multipart()

    assert exc.value.status_code == 413


def test_parse_multipart_avoids_full_body_split_duplication():
    class NoSplitBytes(bytes):
        def split(self, *args, **kwargs):
            raise AssertionError("multipart parser must not split the whole body")

    body = NoSplitBytes(
        b"--BOUNDARY\r\n"
        b'Content-Disposition: form-data; name="field"\r\n'
        b"\r\n"
        b"value\r\n"
        b"--BOUNDARY\r\n"
        b'Content-Disposition: form-data; name="file"; filename="x.txt"\r\n'
        b"Content-Type: text/plain\r\n"
        b"\r\n"
        b"hello\r\n"
        b"--BOUNDARY--\r\n"
    )
    h = _handler(
        headers={
            "Content-Type": "multipart/form-data; boundary=BOUNDARY",
            "Content-Length": str(len(body)),
        },
        body=body,
    )

    fields, files = h.parse_multipart()

    assert fields == {"field": "value"}
    assert files["file"] == {"filename": "x.txt", "data": b"hello"}


def test_parse_multipart_preserves_binary_bytes_without_splitting_payload_text():
    boundary = "BND123"
    blob = b"prefix--BND123suffix\r\nbinary\x00\xff\r\n"
    body = (
        f"--{boundary}\r\n".encode()
        + b'Content-Disposition: form-data; name="model"; filename="m.onnx"\r\n'
        + b"Content-Type: application/octet-stream\r\n\r\n"
        + blob
        + f"\r\n--{boundary}--\r\n".encode()
    )
    h = _handler(
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        body=body,
    )

    _fields, files = h.parse_multipart()

    assert files["model"] == {"filename": "m.onnx", "data": blob}


def test_parse_multipart_closes_temporary_file_on_invalid_boundary(monkeypatch):
    """Malformed multipart bodies must not leak the disk-backed temporary file."""
    from shared import dx_server

    created = []

    class TrackingFile(io.BytesIO):
        def __init__(self):
            super().__init__()
            created.append(self)

    monkeypatch.setattr(dx_server.tempfile, "TemporaryFile", TrackingFile)
    h = _handler(
        headers={"Content-Type": "multipart/form-data; boundary=BOUNDARY"},
        body=b"not-a-multipart-body",
    )

    assert h.parse_multipart() == ({}, {})
    assert len(created) == 1
    assert created[0].closed is True


def test_dxserver_force_free_port_uses_list_form_fuser(monkeypatch):
    calls = []
    monkeypatch.setattr("shared.dx_server.time.sleep", lambda _seconds: None)
    monkeypatch.setattr(
        "shared.dx_server.subprocess.run",
        lambda args, **kwargs: calls.append((args, kwargs)),
    )

    DXServer._force_free_port(12345)

    assert [call[0] for call in calls] == [
        ["fuser", "-k", "12345/tcp"],
        ["fuser", "-k", "12345/tcp6"],
    ]
    assert all("shell" not in call[1] for call in calls)


def test_launcher_force_free_port_uses_list_form_fuser(monkeypatch):
    import launcher.launcher as lmod

    calls = []
    monkeypatch.setattr(lmod, "_is_port_open", lambda _port: True)
    monkeypatch.setattr(lmod.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(
        lmod.subprocess,
        "run",
        lambda args, **kwargs: calls.append((args, kwargs)),
    )

    lmod._force_free_port(23456)

    assert [call[0] for call in calls] == [
        ["fuser", "-k", "23456/tcp"],
        ["fuser", "-k", "23456/tcp6"],
    ]
    assert all("shell" not in call[1] for call in calls)
