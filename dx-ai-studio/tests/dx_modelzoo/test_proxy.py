"""proxy.py dx_app 프록시 테스트"""
import sys, pytest, socket
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_modelzoo"))


class TestHealthCheck:
    def test_health_check_false_when_down(self):
        from core.proxy import is_dx_app_alive
        result = is_dx_app_alive(port=59999, timeout=0.5)
        assert result is False

    @patch("core.proxy.socket.create_connection")
    def test_health_check_true_when_up(self, mock_conn):
        mock_sock = MagicMock()
        mock_conn.return_value = mock_sock
        from core.proxy import is_dx_app_alive
        result = is_dx_app_alive(port=8080, timeout=1)
        assert result is True
        mock_sock.close.assert_called_once()


class TestProxyRequest:
    @patch("core.proxy.http.client.HTTPConnection")
    def test_proxy_get(self, mock_http):
        mock_conn = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = b'{"ok":true}'
        mock_resp.getheaders.return_value = [("Content-Type", "application/json")]
        mock_conn.getresponse.return_value = mock_resp
        mock_http.return_value = mock_conn

        from core.proxy import proxy_request
        status, headers, body = proxy_request("GET", "/api/modelzoo/list", query="source=internal")
        assert status == 200
        assert b'"ok"' in body

    @patch("core.proxy.http.client.HTTPConnection")
    def test_proxy_connection_refused(self, mock_http):
        mock_http.return_value.request.side_effect = ConnectionRefusedError
        from core.proxy import proxy_request
        status, headers, body = proxy_request("GET", "/api/test")
        assert status == 502
        assert b"DX_APP_UNAVAILABLE" in body

    @patch("core.proxy.http.client.HTTPConnection")
    def test_proxy_error_response_has_content_length(self, mock_http):
        """프록시 오류 JSON은 HTTP/1.1 클라이언트가 body 종료를 알 수 있어야 한다."""
        mock_http.return_value.getresponse.side_effect = TimeoutError("timed out")
        from core.proxy import proxy_request
        status, headers, body = proxy_request("POST", "/api/run")

        header_map = {name.lower(): value for name, value in headers}
        assert status == 504
        assert header_map["content-type"] == "application/json"
        assert header_map["content-length"] == str(len(body))
        assert b"DX_APP_TIMEOUT" in body


class TestSafeModelId:
    def test_valid_id(self):
        from core.proxy import is_safe_model_id
        assert is_safe_model_id("yolov8n") is True
        assert is_safe_model_id("resnet50_v1.5") is True
        assert is_safe_model_id("3ddfa_v2_mobilnet0.5_120x120") is True

    def test_path_traversal_blocked(self):
        from core.proxy import is_safe_model_id
        assert is_safe_model_id("../../etc/passwd") is False
        assert is_safe_model_id("../config.py") is False

    def test_command_injection_blocked(self):
        from core.proxy import is_safe_model_id
        assert is_safe_model_id("model;rm -rf /") is False
        assert is_safe_model_id("model$(whoami)") is False
