#!/usr/bin/env python3
"""DX Cloud web server — port 8100.

DEEPX on AWS: the AWS Marketplace entry points (DEEPX Compiler Solution, DEEPX Greengrass
Solution) and a cloud ONNX → DXNN compile through a deployed DEEPX Compiler stack.
The AWS work lives in dx_edge/core/aws_compile.py (compile), aws_stack.py (stack setup) and
aws_greengrass.py (Greengrass devices); this file only routes.
"""
from pathlib import Path

from shared.dx_server import DXBaseHandler, DXServer, RequestBodyError
from shared.shell import ShellSpec
from dx_edge.core import aws_compile as ac
from dx_edge.core import aws_greengrass as gg
from dx_edge.core import aws_stack as st

DEFAULT_PORT = 8100
STATIC_DIR = Path(__file__).resolve().parent / "static"
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
SERVER_NAME = "DX Cloud"

# A single screen, so there is no tab row — the template root carries .dx-shell--no-tabs.
DX_EDGE_SHELL = ShellSpec(module_key="cloud")


def _models_dir():
    """The Studio models directory — the same setting dx_app uses (DX_APP_MODELS_DIR)."""
    from dx_app.core import config as app_config
    return app_config.MODELS_DIR


class DXEdgeHandler(DXBaseHandler):
    """DX Cloud HTTP request handler."""

    server_name = SERVER_NAME
    static_dir = STATIC_DIR
    templates_dir = TEMPLATES_DIR
    shell_spec = DX_EDGE_SHELL
    log_silent = True
    upload_max_bytes = ac.MAX_ONNX_BYTES + ac.MAX_JSON_BYTES + 64 * 1024

    def _job_args(self, src: dict):
        return (src.get("profile", ""), src.get("region", ""), src.get("stack", ""),
                src.get("prefix", ""))

    def _query(self) -> dict:
        return {k: self.read_query_param(k) for k in ("profile", "region", "stack", "prefix", "name",
                                                       "device")}

    def route(self):
        if self.route_common():
            return
        path = self.url_path
        try:
            if self.command == "GET":
                if path == "/guide":
                    return self.serve_template("guide.html")
                if path == "/api/hb":
                    return self.send_json({"ok": True})
                if path == "/api/aws/status":
                    return self.send_json(ac.status(self.read_query_param("profile")))
                if path == "/api/aws/regions":
                    return self.send_json(ac.regions(self.read_query_param("profile")))
                if path == "/api/aws/identity":
                    q = self._query()
                    return self.send_json(ac.identity(q["profile"], q["region"]))
                if path == "/api/aws/stacks":
                    q = self._query()
                    return self.send_json({"stacks": ac.list_stacks(q["profile"], q["region"])})
                if path == "/api/aws/subscription":
                    q = self._query()
                    return self.send_json({"templates": st.subscription(q["profile"], q["region"])})
                if path == "/api/aws/stacks/progress":
                    q = self._query()
                    return self.send_json(st.stack_progress(q["profile"], q["region"], q["name"]))
                if path == "/api/aws/compile/status":
                    return self.send_json(ac.compile_status(*self._job_args(self._query())))
                if path == "/api/aws/compile/download":
                    return self._download()
                if path == "/api/aws/greengrass/devices":
                    q = self._query()
                    return self.send_json(gg.devices(q["profile"], q["region"], q["stack"]))
                if path == "/api/aws/greengrass/components":
                    q = self._query()
                    return self.send_json({"components": gg.components(q["profile"], q["region"],
                                                                       q["device"])})
            elif self.command == "POST":
                if path == "/api/aws/compile":
                    return self._start_compile()
                if path == "/api/aws/stacks":
                    b = self.read_json_body()
                    return self.send_json(st.create_stack(b.get("profile", ""), b.get("region", ""),
                                                          b.get("template", ""), b.get("name", "")))
                if path == "/api/aws/stacks/delete":
                    b = self.read_json_body()
                    return self.send_json(st.delete_stack(b.get("profile", ""), b.get("region", ""),
                                                          b.get("name", ""), b.get("confirm", "")))
                if path == "/api/aws/greengrass/install-script":
                    b = self.read_json_body()
                    return self.send_json(gg.install_script(b.get("profile", ""), b.get("region", ""),
                                                            b.get("stack", ""), b.get("thing", "")))
                if path == "/api/aws/compile/save":
                    out = ac.save_dxnn(*self._job_args(self.read_json_body()), _models_dir())
                    return self.send_json({"path": str(out)})
        except ac.AwsError as exc:
            return self.send_error_json(exc.status, exc.message)
        self.route_legacy()

    def _download(self):
        """Stream the .dxnn from S3 to the browser in chunks (models are tens of MB)."""
        name, size, body = ac.open_dxnn(*self._job_args(self._query()))
        chunks = ac.iter_body(body)
        first = next(chunks, b"")  # an AWS error here can still become a JSON error response
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", str(size))
        self.send_header("Content-Disposition", f'attachment; filename="{name}"')
        self.end_headers()
        if self._is_head_request():
            return
        try:
            self.wfile.write(first)
            for chunk in chunks:
                self.wfile.write(chunk)
        except ac.AwsError:
            # Headers are out; dropping the connection tells the browser the download failed.
            self.close_connection = True

    def _start_compile(self):
        fields, files = self.parse_multipart()
        onnx, cfg = files.get("onnx"), files.get("json")
        if not onnx or not cfg:
            raise RequestBodyError(400, "Both an .onnx and a .json file are required")
        job = ac.start_compile(
            profile=fields.get("profile", ""),
            region=fields.get("region", ""),
            stack=fields.get("stack", ""),
            onnx_name=onnx["filename"], onnx_data=onnx["data"],
            json_name=cfg["filename"], json_data=cfg["data"],
        )
        self.send_json(job)


def create_server(port=DEFAULT_PORT):
    """Server factory for tests: returns an HTTPServer instance."""
    from http.server import ThreadingHTTPServer
    srv = ThreadingHTTPServer(("127.0.0.1", port), DXEdgeHandler)
    srv.daemon_threads = True
    return srv


if __name__ == "__main__":
    DXServer(DXEdgeHandler, SERVER_NAME, default_port=DEFAULT_PORT).start()
